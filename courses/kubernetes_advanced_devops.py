COURSE_ID = "k8s_advanced_devops"
COURSE_TITLE = "Advanced Kubernetes for DevOps Engineers"
COURSE_DESCRIPTION = (
    "A production-grade Kubernetes curriculum for engineers who already understand "
    "Pods, Namespaces, basic Deployments, Nodes, and Horizontal Pod Autoscaling. "
    "This track skips the fundamentals and dives directly into the advanced networking, "
    "storage, scheduling, configuration, and GitOps patterns required to run real "
    "workloads reliably in production clusters."
)

CURRICULUM_DATA = [
    {
        "id": 1,
        "title": "Module 1: Advanced Networking & Ingress Controllers",
        "theory": """
### Beyond ClusterIP: The Kubernetes Service Model Deep Dive
A Kubernetes `Service` is not a single object type but a policy expressed through several distinct modes. `ClusterIP` provides a stable virtual IP routed internally by `kube-proxy` via iptables or IPVS rules. `NodePort` layers a static port (30000-32767) on every node on top of a ClusterIP. `LoadBalancer` asks the cloud provider's controller to provision an external L4 load balancer that targets the NodePort. `ExternalName` is a DNS-level CNAME with no proxying at all. Understanding that these are layered abstractions -- not four unrelated features -- is essential for debugging connectivity issues, because a broken `LoadBalancer` Service is frequently actually a broken ClusterIP or a broken kube-proxy rule underneath it.

### Endpoints, EndpointSlices, and Readiness
Services do not talk to Pods directly; they talk to `Endpoints` (or, in modern clusters, `EndpointSlices`, which shard endpoint data for scalability beyond a few hundred Pods). An EndpointSlice entry is only added when a Pod passes its readiness probe. This is the mechanism that makes rolling updates safe: kube-proxy will never forward traffic to a Pod whose container is still starting up, even if the container process is technically running.

### Ingress: The HTTP/HTTPS Layer 7 Gateway
`Service` objects operate at Layer 4 (TCP/UDP). To do host-based or path-based HTTP routing, TLS termination, and virtual hosting, you need an `Ingress` resource plus an Ingress Controller (NGINX Ingress, Traefik, HAProxy, or a cloud-native ALB controller) that actually implements the routing rules. The `Ingress` object itself is declarative intent; without a controller watching the cluster, it does nothing. Production clusters almost always standardize on the `IngressClass` resource to disambiguate which controller should honor which Ingress objects when multiple controllers coexist.

### Automating TLS with cert-manager
Manually rotating TLS certificates does not scale. `cert-manager` is a Kubernetes-native controller that watches `Certificate` and `Issuer`/`ClusterIssuer` custom resources, requests certificates from an ACME provider such as Let's Encrypt (or an internal CA, Vault, or self-signed issuer), stores the resulting key pair in a `Secret`, and automatically renews it before expiry. The `Issuer` scopes to a namespace; `ClusterIssuer` is cluster-wide. Combined with the `ingress-shim` annotations (`cert-manager.io/cluster-issuer`), cert-manager can automatically provision a `Certificate` object directly from an `Ingress` definition.

### Network Policies: Default-Deny Microservice Isolation
By default, every Pod in a Kubernetes cluster can reach every other Pod -- there is no network isolation out of the box. `NetworkPolicy` objects, enforced by the CNI plugin (Calico, Cilium, or Weave -- not all CNIs support them, notably plain Flannel does not), let you define allow-lists for ingress and egress traffic using label selectors. The critical mental model: NetworkPolicies are additive/allow-only. If a Pod is selected by at least one NetworkPolicy, all traffic not explicitly allowed is denied. If a Pod is selected by zero NetworkPolicies, all traffic is allowed. The standard production pattern is to apply a namespace-wide default-deny policy first, then layer specific allow rules on top.
""",
        "commands": """
### Command & Syntax Reference

**Service inspection**
- `kubectl get svc -o wide` -- list Services with cluster IPs and selectors.
- `kubectl get endpointslices -l kubernetes.io/service-name=<svc>` -- see which Pods currently back a Service.
- `kubectl describe svc <name>` -- shows selector, ports, and endpoints in one view.

**Ingress**
- `kubectl get ingressclass` -- list available Ingress controllers registered in the cluster.
- `kubectl get ingress -A` -- list all Ingress objects across namespaces.
- `kubectl describe ingress <name>` -- shows backend rules and any TLS section.

**cert-manager**
- `kubectl get clusterissuer` -- list cluster-wide certificate issuers.
- `kubectl get certificate -A` -- list Certificate resources and their `READY` status.
- `kubectl describe certificaterequest <name>` -- inspect why a certificate issuance failed.
- `kubectl get secret <tls-secret> -o yaml` -- inspect the resulting TLS Secret (`tls.crt` / `tls.key`).

**NetworkPolicy**
- `kubectl get networkpolicy -A` -- list all NetworkPolicy objects.
- `kubectl describe networkpolicy <name>` -- shows podSelector plus ingress/egress rules.

**Key YAML fields to master**
```yaml
# Service selector must match Pod labels exactly (set intersection, not string match)
spec:
  selector:
    app: my-app
  ports:
    - port: 80          # port the Service exposes
      targetPort: 8080  # port the container listens on
      protocol: TCP
  type: ClusterIP        # ClusterIP | NodePort | LoadBalancer | ExternalName
```
```yaml
# NetworkPolicy skeleton -- podSelector: {} means "all pods in this namespace"
spec:
  podSelector: {}
  policyTypes: ["Ingress", "Egress"]
  ingress: []   # empty list = deny all ingress
  egress: []    # empty list = deny all egress
```
""",
        "examples": """
### Real-World Examples

#### Example 1: Path-Based Ingress with Automatic TLS via cert-manager
**Situation:** A platform team runs an NGINX Ingress Controller and needs `api.example.com` to route `/v1` to one backend Service and `/v2` to another, with Let's Encrypt-issued TLS terminated at the edge.

**Action:** Define a `ClusterIssuer` for Let's Encrypt's production ACME endpoint using HTTP-01 validation, then an `Ingress` annotated to request a certificate through `ingress-shim`.

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: platform-team@example.com
    privateKeySecretRef:
      name: letsencrypt-prod-account-key
    solvers:
      - http01:
          ingress:
            class: nginx
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api-ingress
  namespace: production
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rewrite-target: /$2
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - api.example.com
      secretName: api-example-com-tls
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /v1(/|$)(.*)
            pathType: ImplementationSpecific
            backend:
              service:
                name: api-v1-service
                port:
                  number: 80
          - path: /v2(/|$)(.*)
            pathType: ImplementationSpecific
            backend:
              service:
                name: api-v2-service
                port:
                  number: 80
```

#### Example 2: Default-Deny Namespace with Explicit Allow Rules
**Situation:** A `payments` namespace must reject all traffic by default and only allow the `checkout` service to talk to the `ledger` service on port 5432, plus permit DNS egress to kube-system.

**Action:** Apply a default-deny policy, then two scoped allow policies.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: payments
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-checkout-to-ledger
  namespace: payments
spec:
  podSelector:
    matchLabels:
      app: ledger
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: checkout
      ports:
        - protocol: TCP
          port: 5432
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns-egress
  namespace: payments
spec:
  podSelector: {}
  policyTypes:
    - Egress
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: kube-system
      ports:
        - protocol: UDP
          port: 53
        - protocol: TCP
          port: 53
```

#### Example 3: Internal-Only Service with a Headless Backend for Peer Discovery
**Situation:** A caching layer's client library needs to discover every backend Pod IP directly instead of going through a single virtual IP.

**Action:** Create a headless Service (`clusterIP: None`) so DNS returns all Pod IPs behind the selector.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: cache-headless
  namespace: production
spec:
  clusterIP: None
  selector:
    app: cache-node
  ports:
    - name: gossip
      port: 7946
      targetPort: 7946
```
""",
        "exercise": """
### Hands-On Labs

#### Lab 1: Stand Up an Ingress Controller and Route Two Services
**Objective:** Deploy NGINX Ingress locally (via kind or minikube) and route traffic to two separate backend Services by path.

**Tasks:**
1. Install the NGINX Ingress Controller manifest for your local distribution (`kubectl apply -f` the official deploy YAML for kind/minikube).
2. Deploy two simple Deployments, `echo-blue` and `echo-green`, each with a Service of the same name exposing port 80.
3. Write an `Ingress` object routing `/blue` to `echo-blue` and `/green` to `echo-green` on host `local.test`.
4. Add `127.0.0.1 local.test` to your `/etc/hosts` (or equivalent) and curl both paths to confirm correct routing.
5. Run `kubectl describe ingress` and identify which controller picked up the object via the `ingressClassName` field.

#### Lab 2: Enforce Default-Deny and Verify with a Debug Pod
**Objective:** Prove that NetworkPolicies actually block traffic, not just declare intent.

**Tasks:**
1. Create a namespace `netpol-lab` and deploy two Pods: `server` (running any simple HTTP server on port 80) with label `app: server`, and `client` (a debug image with `curl`).
2. From `client`, curl `server`'s ClusterIP and confirm it succeeds (no policy yet).
3. Apply a default-deny-all NetworkPolicy scoped to `netpol-lab`.
4. Re-run the curl from `client` and confirm it now times out.
5. Add a scoped `allow` NetworkPolicy permitting only Pods labeled `role: approved` to reach `server`. Label `client` accordingly and confirm access is restored.
6. Explain in your own notes why an *unlabeled* namespace's Pods were still able to reach `server` before step 3 despite `server` never having granted access explicitly.

#### Lab 3: Automate a Self-Signed Certificate with cert-manager
**Objective:** Get hands-on with the cert-manager issuance lifecycle without depending on a public ACME server.

**Tasks:**
1. Install cert-manager via its official manifest into your local cluster.
2. Create a `ClusterIssuer` of kind `SelfSigned`.
3. Create a `Certificate` resource referencing that issuer, requesting a `Secret` named `demo-tls` for DNS name `demo.local`.
4. Run `kubectl describe certificate demo-tls` repeatedly and observe the `Ready` condition transition from `False` to `True`.
5. Inspect the generated Secret with `kubectl get secret demo-tls -o yaml` and decode the `tls.crt` field with `base64 -d` to confirm a real certificate was issued.
""",
        "insight": """
### Interview Q&A

#### Q1: What is the difference between a Service and an Ingress, and why can't Ingress replace Service entirely?
* **Answer:** A Service is a Layer 4 abstraction providing a stable virtual IP and load-balancing across a set of Pods; it works for any TCP/UDP traffic. An Ingress is a Layer 7 abstraction that only understands HTTP/HTTPS and requires a Service as its backend target -- Ingress rules ultimately point at Service names and ports, they never target Pods directly. You still need Services even in an Ingress-heavy cluster because Ingress controllers route to Services, and non-HTTP protocols (gRPC-over-raw-TCP edge cases aside, databases, message queues) can't use Ingress at all.

#### Q2: A Pod's traffic is being unexpectedly blocked after you applied a NetworkPolicy to a completely different Pod. How is that possible?
* **Answer:** NetworkPolicies are evaluated by matching `podSelector` and `namespaceSelector` fields against labels, not against a policy's `metadata.name` or the Pod it was "intended" for. If the newly applied policy's `podSelector` unintentionally matches other Pods sharing a common label (for example, a broad `tier: backend` selector), it silently starts governing those Pods too, and because NetworkPolicies are default-deny once any policy selects a Pod, previously wide-open traffic can suddenly be dropped. Always test selectors with `kubectl get pods -l <selector>` before applying.

#### Q3: Why would a Certificate resource stay stuck in `Ready: False` indefinitely with an HTTP-01 solver?
* **Answer:** HTTP-01 validation requires the ACME server to reach `http://<domain>/.well-known/acme-challenge/<token>` on port 80 from the public internet. Common failure causes are: the domain's DNS not actually pointing at the Ingress Controller's external IP yet, a firewall or CDN blocking port 80, or the `ingressClassName` in the Ingress not matching the class the solver is configured to inject its challenge into. Checking `kubectl describe challenge` (a child resource of the CertificateRequest) shows the exact HTTP status the ACME server received.

### CKA/CKAD Exam Focus
- Be fast at writing NetworkPolicy YAML from memory -- the exam does not provide cert-manager but frequently tests default-deny plus scoped-allow patterns under time pressure.
- Know the exact precedence: Ingress `pathType` values (`Exact`, `Prefix`, `ImplementationSpecific`) behave differently, and exam questions often hinge on `Prefix` vs `Exact` matching subtleties.
- Practice diagnosing Service connectivity with `kubectl get endpoints` first -- a Service with zero endpoints because the selector doesn't match Pod labels is one of the most common exam trick scenarios.
""",
    },
    {
        "id": 2,
        "title": "Module 2: Persistent Storage & Stateful Workloads",
        "theory": """
### The Storage Abstraction Stack
Kubernetes storage is a chain of four objects working together: a `StorageClass` describes *how* to provision storage (which CSI driver, what disk type, what reclaim policy); a `PersistentVolume` (PV) is the actual piece of provisioned storage (a cluster-scoped resource); a `PersistentVolumeClaim` (PVC) is a namespaced request for storage matching certain criteria (size, access mode, StorageClass); and the Pod mounts the PVC by name, remaining completely unaware of the underlying disk technology. This indirection is what lets the same Pod spec run unmodified on AWS EBS, GCE Persistent Disk, or on-prem Ceph.

### Static vs Dynamic Provisioning
In static provisioning, an administrator pre-creates PVs by hand and PVCs bind to whichever matching PV exists. This does not scale operationally. Dynamic provisioning, driven by the Container Storage Interface (CSI), lets a PVC trigger on-demand creation of a brand-new backing volume the moment it's created, using the StorageClass's `provisioner` field to determine which CSI driver handles the request. Almost all production clusters use dynamic provisioning exclusively.

### Access Modes and Their Real Constraints
`ReadWriteOnce` (RWO) means the volume can be mounted read-write by a single node (not a single Pod -- multiple Pods on the *same* node can share it). `ReadOnlyMany` (ROX) allows many nodes to mount read-only. `ReadWriteMany` (RWX) allows many nodes read-write simultaneously but is only supported by specific backends (NFS, CephFS, EFS, Azure Files) -- block storage like EBS or standard GCE PD cannot do RWX. `ReadWriteOncePod` (RWOP), a newer mode, restricts the volume to a single Pod cluster-wide, useful for workloads like single-writer databases where even accidental double-mounting on the same node must be prevented.

### StatefulSets: Ordered, Named, and Stable
Unlike a Deployment's fungible, randomly-named Pods, a `StatefulSet` gives each Pod a stable, predictable identity: `<statefulset-name>-0`, `-1`, `-2`, etc. Pods are created and terminated in strict ordinal order (unless `podManagementPolicy: Parallel` is set), and each Pod gets its own PVC generated from a `volumeClaimTemplate`, so `-0` always reattaches to the same disk it had before, even after rescheduling. A `StatefulSet` is normally paired with a headless Service (`clusterIP: None`), which gives each Pod a stable DNS name of the form `<pod-name>.<service-name>.<namespace>.svc.cluster.local` -- essential for clustered databases where peers must find each other by a consistent address.

### Reclaim Policies and Data Safety
A PV's `persistentVolumeReclaimPolicy` determines what happens when its PVC is deleted: `Delete` destroys the underlying storage (the default for most dynamically provisioned classes -- dangerous for production databases), while `Retain` leaves the disk intact and moves the PV to a `Released` state requiring manual intervention to reuse or clean it up. Production StorageClasses for critical stateful workloads should almost always override the default to `Retain`.
""",
        "commands": """
### Command & Syntax Reference

- `kubectl get storageclass` -- list available StorageClasses; the one marked `(default)` is used when a PVC omits `storageClassName`.
- `kubectl get pv` -- list PersistentVolumes cluster-wide, showing `STATUS` (`Available`, `Bound`, `Released`, `Failed`).
- `kubectl get pvc -n <namespace>` -- list PersistentVolumeClaims and their bound PV.
- `kubectl describe pvc <name>` -- shows binding events, useful when a PVC is stuck `Pending`.
- `kubectl get statefulset -o wide` -- list StatefulSets with current/desired replica counts.
- `kubectl rollout status statefulset/<name>` -- watch a StatefulSet rollout to completion.
- `kubectl delete pod <sts-name>-0` -- safe way to force-restart a specific ordinal Pod; the StatefulSet controller recreates it with the same identity and reattaches its PVC.

**Key YAML fields to master**
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd-retain
provisioner: ebs.csi.aws.com   # CSI driver name -- differs per cloud/backend
parameters:
  type: gp3
reclaimPolicy: Retain           # Delete | Retain
volumeBindingMode: WaitForFirstConsumer  # delays provisioning until a Pod is scheduled
allowVolumeExpansion: true
```
```yaml
# volumeClaimTemplates only exist inside StatefulSet specs, not Deployments
spec:
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes: ["ReadWriteOnce"]
        storageClassName: fast-ssd-retain
        resources:
          requests:
            storage: 10Gi
```
""",
        "examples": """
### Real-World Examples

#### Example 1: A Three-Node PostgreSQL-Style StatefulSet with Stable Storage
**Situation:** A team needs a stateful database cluster where each replica keeps its own disk across restarts and can be addressed by a predictable hostname for replication configuration.

**Action:** Define a headless Service plus a StatefulSet using `volumeClaimTemplates` so Kubernetes auto-creates one PVC per replica.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: pg-headless
  namespace: data
spec:
  clusterIP: None
  selector:
    app: pg
  ports:
    - port: 5432
      name: postgres
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: pg
  namespace: data
spec:
  serviceName: pg-headless
  replicas: 3
  podManagementPolicy: OrderedReady
  selector:
    matchLabels:
      app: pg
  template:
    metadata:
      labels:
        app: pg
    spec:
      containers:
        - name: postgres
          image: postgres:16
          env:
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: pg-credentials
                  key: password
          ports:
            - containerPort: 5432
          volumeMounts:
            - name: data
              mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes: ["ReadWriteOnce"]
        storageClassName: fast-ssd-retain
        resources:
          requests:
            storage: 20Gi
```

#### Example 2: A ReadWriteMany Shared Volume for a Multi-Replica Report Renderer
**Situation:** Several Deployment replicas need to write generated PDF reports to a common location that any replica can serve back to clients.

**Action:** Provision an RWX-capable PVC (backed by an NFS or EFS CSI driver) and mount it from every Pod in the Deployment.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: shared-reports
  namespace: reporting
spec:
  accessModes: ["ReadWriteMany"]
  storageClassName: efs-sc
  resources:
    requests:
      storage: 100Gi
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: report-renderer
  namespace: reporting
spec:
  replicas: 4
  selector:
    matchLabels:
      app: report-renderer
  template:
    metadata:
      labels:
        app: report-renderer
    spec:
      containers:
        - name: renderer
          image: registry.example.com/report-renderer:2.3.0
          volumeMounts:
            - name: reports
              mountPath: /var/reports
      volumes:
        - name: reports
          persistentVolumeClaim:
            claimName: shared-reports
```

#### Example 3: Expanding a Volume Without Downtime
**Situation:** A production database PVC is running low on space and the StorageClass supports online expansion.

**Action:** Patch the PVC's storage request upward; the CSI driver and filesystem resize online if `allowVolumeExpansion: true` on the StorageClass.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pg-data-pg-0
  namespace: data
spec:
  accessModes: ["ReadWriteOnce"]
  storageClassName: fast-ssd-retain
  resources:
    requests:
      storage: 50Gi   # increased from 20Gi
```
""",
        "exercise": """
### Hands-On Labs

#### Lab 1: Observe PVC-to-PV Binding with Dynamic Provisioning
**Objective:** Understand the full lifecycle from StorageClass to bound PVC.

**Tasks:**
1. Run `kubectl get storageclass` and identify the default class in your cluster (kind/minikube ship one out of the box).
2. Create a PVC requesting 1Gi with no explicit `storageClassName` and confirm it binds to a dynamically created PV.
3. Run `kubectl get pv` and note the `RECLAIM POLICY` and `STATUS` columns.
4. Delete the PVC and observe what happens to the PV -- is it deleted, or does it move to `Released`?
5. Create a second StorageClass with `reclaimPolicy: Retain`, repeat steps 2-4 using it, and document the behavioral difference.

#### Lab 2: Deploy a StatefulSet and Prove Identity Persists Across Rescheduling
**Objective:** Confirm that StatefulSet Pods keep their storage and DNS identity after being deleted.

**Tasks:**
1. Deploy the three-node headless-Service-backed StatefulSet from Example 1 (a lightweight image is fine for the lab, e.g., writing a timestamp file to the mounted volume on startup).
2. From a debug Pod, resolve `pg-1.pg-headless.data.svc.cluster.local` via `nslookup` and confirm it returns the specific Pod's IP.
3. Exec into `pg-1` and write a marker file to the mounted volume path.
4. Delete Pod `pg-1` with `kubectl delete pod pg-1` and wait for it to be recreated.
5. Exec into the new `pg-1` and confirm the marker file is still present, proving the same PVC was reattached.

#### Lab 3: Force a StatefulSet Scale-Down and Handle Orphaned PVCs
**Objective:** Understand that scaling a StatefulSet down does NOT delete its PVCs by default.

**Tasks:**
1. Scale the `pg` StatefulSet from 3 replicas down to 1 with `kubectl scale statefulset pg --replicas=1`.
2. Run `kubectl get pvc -n data` and confirm the PVCs for `pg-1` and `pg-2` still exist even though their Pods are gone.
3. Scale back up to 3 and confirm the same PVCs are reused rather than new ones created.
4. Manually delete the leftover PVCs only after documenting why Kubernetes intentionally leaves this as a manual step (data safety).
""",
        "insight": """
### Interview Q&A

#### Q1: Why does a StatefulSet require a headless Service, and what breaks if you use a normal ClusterIP Service instead?
* **Answer:** A headless Service (`clusterIP: None`) tells CoreDNS to return the individual Pod IPs directly instead of a single virtual IP, which is what generates the per-Pod DNS names (`pg-0.pg-headless...`) that StatefulSet peers rely on for discovery and stable addressing. With a normal ClusterIP Service, clients would only ever resolve to one load-balanced virtual IP with no way to address a specific ordinal Pod, which breaks primary/replica database topologies that need to talk to a specific member (e.g., always writing to `-0` as primary).

#### Q2: A PVC is stuck in `Pending` state and never binds. What are the most likely causes?
* **Answer:** The most common causes, roughly in order of frequency: the requested `storageClassName` doesn't exist or has a typo; the StorageClass uses `volumeBindingMode: WaitForFirstConsumer` and no Pod has been scheduled yet to trigger provisioning (this is normal, not an error); the requested access mode isn't supported by the backend (e.g., asking for RWX on a block-storage-only provisioner); or the cloud account has hit a quota limit on the underlying disk type. `kubectl describe pvc` surfaces the actual event message for all of these.

#### Q3: What is the practical difference between `Delete` and `Retain` reclaim policies, and why might `Retain` still be "dangerous" if misunderstood?
* **Answer:** `Delete` destroys the underlying cloud disk the moment its PVC is deleted, which is fast but means a mistaken `kubectl delete pvc` permanently destroys data. `Retain` preserves the disk and leaves the PV in `Released` state, but that PV cannot be automatically rebound to a new PVC -- an administrator must manually clear its `claimRef` or delete and recreate the PV pointing at the same underlying volume. Teams sometimes assume `Retain` alone is a backup strategy; it isn't -- it only prevents accidental deletion of the live volume, it doesn't provide point-in-time recovery.

### CKA Exam Focus
- Practice writing a full StorageClass -> PVC -> Pod chain from memory without a default StorageClass present, since exam clusters sometimes don't have one.
- Know `volumeBindingMode: WaitForFirstConsumer` by heart -- it's frequently the answer to "why is my PVC still Pending after I created it" scenarios.
- Be able to troubleshoot with `kubectl describe pvc/pv` rather than guessing; the exam rewards reading actual event output over assumption.
""",
    },
    {
        "id": 3,
        "title": "Module 3: Advanced Scheduling & Node Management",
        "theory": """
### Taints and Tolerations: Repelling, Not Attracting
A taint is applied to a *node* and repels Pods unless they carry a matching toleration; this is the opposite direction of affinity, which pulls Pods toward nodes. Taints have three effects: `NoSchedule` (new Pods won't be placed there, existing ones stay), `PreferNoSchedule` (a soft version, best-effort avoidance), and `NoExecute` (existing Pods without the toleration are actively evicted, and new ones are blocked). `NoExecute` also supports `tolerationSeconds`, letting a Pod tolerate the taint temporarily before eviction -- a key mechanism behind how Kubernetes handles `node.kubernetes.io/not-ready` and `node.kubernetes.io/unreachable` taints during node failures, giving Pods a grace period before rescheduling elsewhere.

### Node Affinity and Anti-Affinity
`nodeAffinity` extends the older `nodeSelector` with richer boolean logic (`In`, `NotIn`, `Exists`, `Gt`, `Lt`) and two enforcement strengths: `requiredDuringSchedulingIgnoredDuringExecution` (a hard constraint the scheduler must satisfy) and `preferredDuringSchedulingIgnoredDuringExecution` (a weighted soft preference). `podAffinity` and `podAntiAffinity` work similarly but match against labels of *other Pods* rather than node labels, letting you co-locate cooperating Pods on the same node/zone (affinity) or spread replicas apart for fault tolerance (anti-affinity) using a `topologyKey` such as `kubernetes.io/hostname` or `topology.kubernetes.io/zone`.

### Pod Topology Spread Constraints
Pod anti-affinity is powerful but expensive to compute at scale and only expresses pairwise relationships. `topologySpreadConstraints` instead directly describes the *evenness* you want across a topology domain (zone, node, rack) using `maxSkew`, a `topologyKey`, and a `whenUnsatisfiable` policy (`DoNotSchedule` for hard enforcement or `ScheduleAnyway` for best-effort). This is the modern, more scalable replacement for most anti-affinity use cases in production clusters running hundreds of replicas.

### Resource Quotas and LimitRanges
A `ResourceQuota` caps the total resource consumption (CPU, memory, object counts like PVCs or Services) within a namespace -- essential in multi-tenant clusters to stop one team from starving others. A `LimitRange` operates at the individual Pod/container level within a namespace, enforcing default requests/limits when a Pod omits them and rejecting Pods whose requests fall outside a min/max range. The two work together: LimitRange ensures every Pod has sane, bounded resource requests; ResourceQuota ensures the sum across all Pods in the namespace stays within budget. Note that if a ResourceQuota tracking CPU/memory exists in a namespace, every Pod created there *must* explicitly specify requests/limits (or have them injected by a LimitRange) or the Pod will be rejected outright.
""",
        "commands": """
### Command & Syntax Reference

- `kubectl taint nodes <node> key=value:NoSchedule` -- add a taint to a node.
- `kubectl taint nodes <node> key=value:NoSchedule-` -- remove a taint (trailing dash).
- `kubectl describe node <node> | grep Taints` -- inspect current taints on a node.
- `kubectl get resourcequota -n <namespace>` -- view quota usage vs limits.
- `kubectl describe limitrange -n <namespace>` -- view default/min/max constraints.
- `kubectl get pods -o wide --field-selector spec.nodeName=<node>` -- see what's actually scheduled on a given node.

**Key YAML fields to master**
```yaml
# Toleration matching a NoExecute taint with a grace period
tolerations:
  - key: "node.kubernetes.io/unreachable"
    operator: "Exists"
    effect: "NoExecute"
    tolerationSeconds: 300
```
```yaml
# Required node affinity vs preferred pod anti-affinity together
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
        - matchExpressions:
            - key: disktype
              operator: In
              values: ["ssd"]
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchLabels:
              app: my-app
          topologyKey: kubernetes.io/hostname
```
```yaml
topologySpreadConstraints:
  - maxSkew: 1
    topologyKey: topology.kubernetes.io/zone
    whenUnsatisfiable: DoNotSchedule
    labelSelector:
      matchLabels:
        app: my-app
```
""",
        "examples": """
### Real-World Examples

#### Example 1: Dedicated GPU Nodes with Taints and Matching Tolerations
**Situation:** A platform team has a small, expensive pool of GPU nodes that must be reserved exclusively for ML training Pods -- no regular workload should ever land there by accident.

**Action:** Taint the GPU nodes and require the toleration plus a matching node affinity on the training Job.

```bash
kubectl taint nodes gpu-node-1 workload=gpu:NoSchedule
kubectl label nodes gpu-node-1 hardware=gpu
```

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: model-training
  namespace: ml
spec:
  template:
    spec:
      tolerations:
        - key: "workload"
          operator: "Equal"
          value: "gpu"
          effect: "NoSchedule"
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
              - matchExpressions:
                  - key: hardware
                    operator: In
                    values: ["gpu"]
      containers:
        - name: trainer
          image: registry.example.com/model-trainer:1.4.0
          resources:
            requests:
              cpu: "4"
              memory: "16Gi"
              nvidia.com/gpu: "1"
            limits:
              cpu: "4"
              memory: "16Gi"
              nvidia.com/gpu: "1"
      restartPolicy: Never
```

#### Example 2: Zone-Even Spread for a High-Availability API Deployment
**Situation:** An API Deployment with 6 replicas must survive an entire availability-zone outage, requiring roughly even spread across 3 zones.

**Action:** Use `topologySpreadConstraints` with a hard `DoNotSchedule` policy.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: checkout-api
  namespace: production
spec:
  replicas: 6
  selector:
    matchLabels:
      app: checkout-api
  template:
    metadata:
      labels:
        app: checkout-api
    spec:
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: DoNotSchedule
          labelSelector:
            matchLabels:
              app: checkout-api
      containers:
        - name: checkout-api
          image: registry.example.com/checkout-api:3.1.0
          resources:
            requests:
              cpu: "500m"
              memory: "512Mi"
            limits:
              cpu: "1"
              memory: "1Gi"
```

#### Example 3: Namespace Guardrails with ResourceQuota and LimitRange
**Situation:** A shared `staging` namespace is repeatedly getting overloaded because developers forget to set resource requests, causing noisy-neighbor problems.

**Action:** Enforce sane defaults with a LimitRange and cap total namespace consumption with a ResourceQuota.

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: staging-defaults
  namespace: staging
spec:
  limits:
    - type: Container
      default:
        cpu: "500m"
        memory: "512Mi"
      defaultRequest:
        cpu: "100m"
        memory: "128Mi"
      max:
        cpu: "2"
        memory: "2Gi"
      min:
        cpu: "50m"
        memory: "64Mi"
---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: staging-quota
  namespace: staging
spec:
  hard:
    requests.cpu: "20"
    requests.memory: 40Gi
    limits.cpu: "40"
    limits.memory: 80Gi
    pods: "100"
```
""",
        "exercise": """
### Hands-On Labs

#### Lab 1: Cordon, Drain, and Taint a Node Manually
**Objective:** Practice the manual node-maintenance workflow used before patching or decommissioning a node.

**Tasks:**
1. Pick a worker node in your local multi-node cluster (kind supports multi-node configs) and run `kubectl cordon <node>`; confirm via `kubectl get nodes` that it now shows `SchedulingDisabled`.
2. Deploy a Deployment with several replicas before draining, then run `kubectl drain <node> --ignore-daemonsets --delete-emptydir-data` and observe Pods being evicted and rescheduled elsewhere.
3. Apply a `NoExecute` taint to a *different* node that already has Pods running on it without a matching toleration, and watch them get evicted in real time with `kubectl get pods -w`.
4. Uncordon and untaint both nodes to restore normal scheduling.

#### Lab 2: Force an Uneven Cluster into Balance with Topology Spread
**Objective:** See `maxSkew` and `DoNotSchedule` actually reject scheduling when the topology can't be balanced.

**Tasks:**
1. Label two nodes `zone=a` and one node `zone=b` (`kubectl label node <name> topology.kubernetes.io/zone=a`).
2. Deploy a Deployment with 6 replicas and a `topologySpreadConstraints` block using `maxSkew: 1`, `topologyKey: topology.kubernetes.io/zone`, `whenUnsatisfiable: DoNotSchedule`.
3. Watch `kubectl get pods -o wide` and confirm Pods pile up unevenly and some remain `Pending` once the skew limit is hit, since a 2-zone imbalance can't satisfy `maxSkew: 1` at 6 replicas across an uneven 2:1 node split.
4. Change `whenUnsatisfiable` to `ScheduleAnyway` and reapply; confirm all 6 Pods now schedule despite imbalance.

#### Lab 3: Build ResourceQuota Guardrails and Trigger a Rejection
**Objective:** Confirm ResourceQuota + LimitRange interplay by intentionally hitting the ceiling.

**Tasks:**
1. Create a namespace `quota-lab` with the LimitRange and ResourceQuota from Example 3, but set `pods: "3"` in the quota.
2. Deploy a Deployment with `replicas: 5` in that namespace and observe via `kubectl describe deployment` and `kubectl get events` that only 3 Pods are admitted while the rest fail quota admission.
3. Deploy a single Pod that explicitly requests `memory: "5Gi"` and confirm it's rejected for exceeding the LimitRange's `max`.
4. Remove the explicit resource requests from a test Pod entirely and confirm the LimitRange's `defaultRequest` values are auto-injected by inspecting `kubectl get pod <name> -o yaml`.
""",
        "insight": """
### Interview Q&A

#### Q1: What's the practical difference between `nodeAffinity` and `taints/tolerations`, and when would you use both together?
* **Answer:** Affinity is an *attractive* force controlled from the Pod side -- it says "I want to run on nodes like this," but it doesn't stop other Pods from also landing there. Taints are a *repulsive* force controlled from the node side -- they block all Pods by default regardless of what those Pods want, unless they explicitly tolerate the taint. Using both together (taint the GPU nodes, then require both the toleration and a matching node affinity on the GPU workload) is the standard production pattern because the taint keeps everything else off the expensive nodes, and the affinity keeps the GPU workload from ever accidentally landing on a normal node where the GPU driver doesn't exist.

#### Q2: Why might `podAntiAffinity` become a scheduling bottleneck at scale, and what's the modern replacement?
* **Answer:** `podAntiAffinity` requires the scheduler to evaluate pairwise relationships between the incoming Pod and every other running Pod matching the label selector, which becomes computationally expensive as replica counts and node counts grow into the hundreds or thousands. `topologySpreadConstraints` instead reasons directly about the distribution of Pods across topology domains using simple counting (`maxSkew`), which scales far better and expresses "spread evenly" intent more directly than a web of pairwise anti-affinity rules.

#### Q3: A Pod is stuck in `Pending` in a namespace that has a ResourceQuota. `kubectl describe pod` shows no scheduling-related events at all. What's the first thing to check?
* **Answer:** If a ResourceQuota tracking `requests.cpu`/`requests.memory` exists in the namespace, the Pod must be *admitted* by the API server before it's even considered for scheduling; if the Pod (and no LimitRange fills in defaults) omits resource requests, the API server rejects it outright at admission time, before a Node is ever considered, which is why no scheduling event appears. The fix is `kubectl describe resourcequota` to see current usage against the hard limits, and checking whether the Pod spec or a LimitRange in the namespace actually sets requests.

### CKA Exam Focus
- Memorize the taint syntax cold: `kubectl taint nodes <node> key=value:Effect` and the removal form with a trailing `-`.
- Be able to write `requiredDuringSchedulingIgnoredDuringExecution` node affinity YAML from memory -- it shows up constantly in scheduling-focused exam objectives.
- Know that `ResourceQuota` operates at the namespace level and `LimitRange` at the Pod/container level; exam questions often test whether you know which object to edit for a given symptom.
""",
    },
    {
        "id": 4,
        "title": "Module 4: Configuration & Secret Management",
        "theory": """
### ConfigMaps: Externalizing Non-Sensitive Configuration
A `ConfigMap` decouples environment-specific configuration from container images, letting the same image run in dev, staging, and prod with different behavior. ConfigMaps can be consumed three ways: as individual environment variables (`env.valueFrom.configMapKeyRef`), as a bulk set of environment variables (`envFrom.configMapRef`), or as mounted files in a volume -- the last option is the only one that supports live-updates, since kubelet periodically syncs mounted ConfigMap volumes (with some propagation delay), whereas environment variables are injected once at container start and never change without a Pod restart.

### Secrets: Better Than ConfigMaps, But Not Encrypted By Default
A `Secret` is structurally almost identical to a ConfigMap but intended for sensitive data. Critically, base64 encoding (which is all a raw Secret provides by default) is *not* encryption -- anyone with API read access to the Secret, or access to unencrypted etcd, can trivially decode it. Production clusters must layer on `EncryptionConfiguration` at the API server level to encrypt Secret data at rest in etcd, and should use RBAC to tightly restrict `get`/`list` on Secret objects. Built-in Secret types include `Opaque` (generic), `kubernetes.io/tls` (cert+key pair, used directly by Ingress), and `kubernetes.io/dockerconfigjson` (registry credentials for pulling private images).

### The Problem with Storing Secrets in Git
GitOps workflows want everything, including Secrets, declared in Git -- but committing raw Secret manifests to a repository leaks credentials into version history permanently, even if later deleted. Two dominant patterns solve this: **Sealed Secrets** (Bitnami), where a client-side `kubeseal` CLI encrypts a Secret asymmetrically so only the cluster's private key (held by an in-cluster controller) can decrypt it, making the encrypted `SealedSecret` object safe to commit; and the **External Secrets Operator (ESO)**, which instead keeps the actual secret material entirely outside Kubernetes in a dedicated secret manager (AWS Secrets Manager, HashiCorp Vault, Azure Key Vault, GCP Secret Manager), and syncs it into a real Kubernetes `Secret` at runtime via an `ExternalSecret` custom resource that references a `SecretStore` or `ClusterSecretStore` connection.

### Secure Injection Patterns
Beyond ESO, workloads can fetch secrets directly at runtime using a sidecar or CSI driver, such as the Secrets Store CSI Driver, which mounts secrets from an external vault as a volume without ever creating a native Kubernetes Secret object at all -- reducing the attack surface further since the secret never touches etcd. Combined with short-lived, workload-identity-based authentication (IRSA on AWS, Workload Identity on GCP), Pods can authenticate to the external secret store without any long-lived static credential stored in the cluster whatsoever.
""",
        "commands": """
### Command & Syntax Reference

- `kubectl create configmap <name> --from-literal=key=value` -- create a ConfigMap from literal key/value pairs.
- `kubectl create configmap <name> --from-file=config.yaml` -- create a ConfigMap from a file, keyed by filename.
- `kubectl create secret generic <name> --from-literal=password=<val>` -- create an Opaque Secret.
- `kubectl create secret tls <name> --cert=path/to/tls.crt --key=path/to/tls.key` -- create a `kubernetes.io/tls` Secret.
- `kubectl get secret <name> -o jsonpath='{.data.password}' | base64 -d` -- decode a Secret value for inspection.
- `kubeseal --format=yaml < secret.yaml > sealed-secret.yaml` -- encrypt a Secret client-side with Sealed Secrets.
- `kubectl get externalsecret -A` -- list ExternalSecret resources and their sync status.
- `kubectl get secretstore,clustersecretstore -A` -- list configured backends for External Secrets Operator.

**Key YAML fields to master**
```yaml
# Mounting a ConfigMap as files supports live-update; env injection does not
volumeMounts:
  - name: config-vol
    mountPath: /etc/app/config
volumes:
  - name: config-vol
    configMap:
      name: app-config
```
```yaml
# ExternalSecret pulling from a ClusterSecretStore
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: db-credentials
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: ClusterSecretStore
  target:
    name: db-credentials-k8s
  data:
    - secretKey: password
      remoteRef:
        key: prod/db/password
```
""",
        "examples": """
### Real-World Examples

#### Example 1: Live-Reloading Application Config via a Mounted ConfigMap
**Situation:** A service needs its logging verbosity and feature flags adjustable without a Pod restart or redeploy.

**Action:** Mount the ConfigMap as a volume rather than injecting as environment variables, and have the app watch the file for changes.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: production
data:
  config.yaml: |
    logLevel: info
    featureFlags:
      newCheckoutFlow: true
      betaDashboard: false
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-server
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: app-server
  template:
    metadata:
      labels:
        app: app-server
    spec:
      containers:
        - name: app-server
          image: registry.example.com/app-server:5.2.0
          volumeMounts:
            - name: config-vol
              mountPath: /etc/app
              readOnly: true
      volumes:
        - name: config-vol
          configMap:
            name: app-config
```

#### Example 2: Syncing a Database Password from AWS Secrets Manager via ESO
**Situation:** A team wants the source of truth for database credentials to live in AWS Secrets Manager (with automatic rotation) rather than as a static Kubernetes Secret committed anywhere.

**Action:** Configure a `ClusterSecretStore` authenticating via IRSA, then an `ExternalSecret` that continuously syncs the password into a native Secret the Pod consumes normally.

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ClusterSecretStore
metadata:
  name: aws-secrets-manager
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-east-1
      auth:
        jwt:
          serviceAccountRef:
            name: external-secrets-sa
            namespace: external-secrets
---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: db-credentials
  namespace: production
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: ClusterSecretStore
  target:
    name: db-credentials-k8s
    creationPolicy: Owner
  data:
    - secretKey: password
      remoteRef:
        key: prod/db/credentials
        property: password
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: orders-service
  namespace: production
spec:
  replicas: 2
  selector:
    matchLabels:
      app: orders-service
  template:
    metadata:
      labels:
        app: orders-service
    spec:
      containers:
        - name: orders-service
          image: registry.example.com/orders-service:7.0.1
          env:
            - name: DB_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: db-credentials-k8s
                  key: password
```

#### Example 3: A GitOps-Safe SealedSecret for Registry Credentials
**Situation:** A private image registry pull secret needs to be committed to the same Git repo ArgoCD watches, without exposing the raw credential.

**Action:** Encrypt a `dockerconfigjson` Secret client-side with `kubeseal` before committing.

```yaml
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: registry-pull-secret
  namespace: production
spec:
  encryptedData:
    .dockerconfigjson: AgBy8hCwtLwFV1234examplesealedciphertextvaluegoeshere==
  template:
    type: kubernetes.io/dockerconfigjson
    metadata:
      name: registry-pull-secret
      namespace: production
```
""",
        "exercise": """
### Hands-On Labs

#### Lab 1: Compare Env-Var vs Mounted-Volume ConfigMap Update Behavior
**Objective:** Directly observe why mounted ConfigMaps support live updates and env-var injection does not.

**Tasks:**
1. Create a ConfigMap `demo-config` with key `message: "version-1"`.
2. Deploy one Pod that injects `message` as an environment variable, and a second Pod that mounts the ConfigMap as a volume at `/etc/config`.
3. Exec into both Pods and confirm both show `version-1`.
4. Update the ConfigMap to `message: "version-2"` with `kubectl edit configmap demo-config`.
5. Without restarting either Pod, re-check both: the env-var Pod still shows `version-1`; the mounted-volume Pod eventually shows `version-2` after the kubelet sync interval. Document the delay you observed.

#### Lab 2: Prove Secrets Are Not Encrypted by Default
**Objective:** Understand the real security properties (and gaps) of a raw Kubernetes Secret.

**Tasks:**
1. Create a Secret with `kubectl create secret generic demo-secret --from-literal=password=SuperSecret123`.
2. Retrieve it with `kubectl get secret demo-secret -o yaml` and manually base64-decode the `data.password` field to confirm it's trivially reversible, not encrypted.
3. If running a local cluster with etcd access (e.g., kind), inspect the raw etcd data for that key to confirm it's stored in plaintext-equivalent form without an `EncryptionConfiguration` applied.
4. Research your cluster distribution's method for enabling `EncryptionConfiguration` at rest and write down the steps (this may be read-only research if your local cluster doesn't support editing API server flags).

#### Lab 3: Install External Secrets Operator and Sync a Fake Secret Store
**Objective:** Get hands-on with the ExternalSecret sync loop end-to-end.

**Tasks:**
1. Install the External Secrets Operator via its Helm chart into your local cluster.
2. Configure a `SecretStore` using the `fake` provider (ESO ships a built-in fake backend for testing, avoiding any cloud dependency).
3. Create an `ExternalSecret` referencing a key in the fake store and confirm a real Kubernetes `Secret` object appears with `kubectl get secret`.
4. Change the value in the fake store's config and confirm, after the `refreshInterval` elapses, the Kubernetes Secret's data updates automatically without you touching it directly.
""",
        "insight": """
### Interview Q&A

#### Q1: Why is a base64-encoded Kubernetes Secret not considered "encrypted," and what's needed to actually secure it?
* **Answer:** Base64 is a reversible encoding scheme, not a cryptographic transformation -- anyone with the encoded string can decode it in one command with no key required. True protection requires two separate layers: encryption at rest in etcd via an API server `EncryptionConfiguration` (so a stolen etcd snapshot or disk isn't readable), and strict RBAC limiting which users/ServiceAccounts can `get`/`list` Secret objects through the API server in the first place, since encryption at rest does nothing to stop an authorized API call from reading the value in plaintext.

#### Q2: What problem does the External Secrets Operator solve that plain Kubernetes Secrets and even Sealed Secrets don't?
* **Answer:** Plain Secrets require the sensitive value to exist inside the cluster (and often inside a Git repo before Sealed Secrets encrypts it). Sealed Secrets solves the "safe to commit to Git" problem but the decrypted value still ends up sitting in a native Kubernetes Secret at runtime, and rotation still requires re-encrypting and re-committing. ESO instead treats the external vault (Vault, AWS Secrets Manager, etc.) as the single source of truth permanently -- rotation happens centrally in the vault, and ESO's `refreshInterval` loop propagates the new value into the cluster automatically, without ever requiring the secret to pass through Git in any form, encrypted or not.

#### Q3: A Pod using `envFrom.configMapRef` isn't picking up a ConfigMap change after `kubectl apply`. Is this a bug?
* **Answer:** No -- this is expected behavior, not a bug. Environment variables are resolved once at container start time from the ConfigMap's contents at that moment; Kubernetes does not re-inject environment variables into a already-running container process, since that isn't something the container runtime supports. To pick up the change, the Pod must be restarted (commonly done by triggering a rolling restart of the owning Deployment), or the application should instead be redesigned to read config from a mounted volume, which the kubelet does periodically refresh in-place.

### CKAD Exam Focus
- Practice the exact `kubectl create configmap`/`secret` imperative syntax from memory -- it's faster than writing YAML under exam time pressure.
- Know cold which Secret consumption method supports live updates (mounted volume) versus which doesn't (env vars) -- this is a frequently tested distinction.
- Be able to explain, without notes, why raw Secrets are not "secure by default" -- several CKS (Security Specialist) exam objectives build directly on this gap.
""",
    },
    {
        "id": 5,
        "title": "Module 5: GitOps & CI/CD Git Integration",
        "theory": """
### What GitOps Actually Means
GitOps is the practice of using a Git repository as the single source of truth for a system's *desired state*, with an in-cluster controller continuously reconciling the *live state* to match it -- rather than a CI pipeline pushing changes imperatively via `kubectl apply` from outside the cluster. The critical shift is pull versus push: a traditional CI/CD pipeline has credentials to push into the cluster from an external system (a security liability), whereas a GitOps controller like ArgoCD or FluxCD runs inside the cluster and pulls changes from Git, meaning the cluster never has to expose an API endpoint to the CI system at all.

### ArgoCD's Core Reconciliation Loop
ArgoCD's central object is the `Application` custom resource, which declares a Git repo/path/revision as the source and a cluster/namespace as the destination. ArgoCD continuously diffs the live cluster state against the rendered manifests from Git and reports a `SyncStatus` (`Synced` or `OutOfSync`) independently from a `HealthStatus` (whether the resources are actually healthy, e.g., a Deployment's Pods are Ready). Sync can be `manual` (requiring a human or automation to click "Sync") or `automated`, and automated sync additionally supports `selfHeal` (revert any manual `kubectl` drift back to match Git) and `prune` (delete cluster resources that were removed from Git).

### FluxCD's Toolkit-Based Architecture
FluxCD takes a more composable approach, built from separate controllers each responsible for one concern: `source-controller` watches Git/Helm/OCI repositories and produces immutable Artifacts; `kustomize-controller` (or `helm-controller`) applies those artifacts to the cluster, running `kustomize build` or `helm template` as needed; and `notification-controller` handles alerting on reconciliation events. This separation makes Flux more modular for advanced pipelines (e.g., image update automation via `image-reflector-controller` and `image-automation-controller`, which can commit new image tags back to Git automatically after a CI build publishes them).

### The App-of-Apps and Environment Promotion Pattern
Real GitOps setups rarely manage a single Application/Kustomization directly; instead they use an "app-of-apps" pattern (ArgoCD) or a directory-of-Kustomizations pattern (Flux) where a top-level object declares child Applications/Kustomizations, each pointing at environment-specific overlay directories (`overlays/dev`, `overlays/staging`, `overlays/prod`) built on a shared `base` via Kustomize. Promotion between environments then becomes a Git operation -- merging a branch or bumping an image tag in an overlay file -- rather than a manual deployment step, giving a full audit trail of every production change through Git history and PR review.

### Progressive Delivery on Top of GitOps
GitOps tools are frequently paired with progressive delivery controllers like Argo Rollouts or Flagger, which replace the plain `Deployment` object with a `Rollout` (Argo) or add an analysis layer, enabling canary or blue-green rollouts driven by real metrics (error rate, latency from Prometheus) rather than a fixed timer -- automatically rolling back if the canary's metrics degrade, all while the desired end-state is still declared in Git and reconciled the same way.
""",
        "commands": """
### Command & Syntax Reference

**ArgoCD CLI**
- `argocd app create <name> --repo <url> --path <path> --dest-server https://kubernetes.default.svc --dest-namespace <ns>` -- register a new Application.
- `argocd app sync <name>` -- trigger a manual sync.
- `argocd app get <name>` -- show sync/health status and diff.
- `argocd app diff <name>` -- show exactly what's out of sync between Git and the live cluster.
- `kubectl get application -n argocd` -- list Applications as native CRDs.

**FluxCD CLI**
- `flux bootstrap github --owner=<org> --repository=<repo> --path=clusters/prod` -- bootstrap Flux against a GitHub repo.
- `flux get kustomizations` -- list Kustomization reconciliation status.
- `flux get sources git` -- list GitRepository sources and last-fetched revision.
- `flux reconcile kustomization <name> --with-source` -- force an immediate reconciliation.
- `flux suspend kustomization <name>` / `flux resume kustomization <name>` -- pause/resume reconciliation, e.g., during an incident.

**Key YAML fields to master**
```yaml
# ArgoCD Application with automated self-healing sync
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: orders-service
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/example-org/gitops-repo.git
    targetRevision: main
    path: overlays/prod/orders-service
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      selfHeal: true
      prune: true
```
```yaml
# Flux Kustomization pointing at a GitRepository source
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: orders-service
  namespace: flux-system
spec:
  interval: 5m
  path: ./overlays/prod/orders-service
  prune: true
  sourceRef:
    kind: GitRepository
    name: gitops-repo
  targetNamespace: production
```
""",
        "examples": """
### Real-World Examples

#### Example 1: App-of-Apps Bootstrapping Multiple Services in ArgoCD
**Situation:** A platform team wants a single Git commit to be able to bootstrap or update dozens of microservice Applications rather than manually running `argocd app create` for each.

**Action:** Define a parent "root" Application whose source path itself contains child `Application` manifests.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: root-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/example-org/gitops-repo.git
    targetRevision: main
    path: apps/production
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
  syncPolicy:
    automated:
      selfHeal: true
      prune: true
```
```yaml
# apps/production/orders-service.yaml -- one of many child Applications
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: orders-service
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/example-org/gitops-repo.git
    targetRevision: main
    path: overlays/prod/orders-service
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      selfHeal: true
      prune: true
```

#### Example 2: Kustomize Base/Overlay Structure for Environment Promotion
**Situation:** The same application must deploy to `dev`, `staging`, and `prod` with different replica counts and image tags, without duplicating the full manifest three times.

**Action:** Define a shared `base` and environment-specific overlays using strategic merge patches.

```yaml
# base/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: orders-service
spec:
  replicas: 1
  selector:
    matchLabels:
      app: orders-service
  template:
    metadata:
      labels:
        app: orders-service
    spec:
      containers:
        - name: orders-service
          image: registry.example.com/orders-service:latest
          ports:
            - containerPort: 8080
```
```yaml
# base/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - deployment.yaml
```
```yaml
# overlays/prod/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: production
resources:
  - ../../base
patches:
  - target:
      kind: Deployment
      name: orders-service
    patch: |-
      - op: replace
        path: /spec/replicas
        value: 5
images:
  - name: registry.example.com/orders-service
    newTag: 7.0.1
```

#### Example 3: Automated Canary Rollout with Argo Rollouts and ArgoCD
**Situation:** A team wants every deployment of a customer-facing checkout service to automatically canary against real error-rate metrics before fully rolling out, without any manual sign-off.

**Action:** Replace the Deployment with a `Rollout` object referencing an `AnalysisTemplate` backed by Prometheus, still deployed declaratively via ArgoCD.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: checkout-service
  namespace: production
spec:
  replicas: 5
  strategy:
    canary:
      steps:
        - setWeight: 20
        - pause: { duration: 300 }
        - analysis:
            templates:
              - templateName: error-rate-check
        - setWeight: 50
        - pause: { duration: 300 }
        - setWeight: 100
  selector:
    matchLabels:
      app: checkout-service
  template:
    metadata:
      labels:
        app: checkout-service
    spec:
      containers:
        - name: checkout-service
          image: registry.example.com/checkout-service:8.9.0
          ports:
            - containerPort: 8080
---
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: error-rate-check
  namespace: production
spec:
  metrics:
    - name: error-rate
      interval: 1m
      successCondition: result[0] < 0.02
      provider:
        prometheus:
          address: http://prometheus.monitoring.svc.cluster.local:9090
          query: |
            sum(rate(http_requests_total{app="checkout-service",status=~"5.."}[5m]))
            /
            sum(rate(http_requests_total{app="checkout-service"}[5m]))
```
""",
        "exercise": """
### Hands-On Labs

#### Lab 1: Bootstrap ArgoCD and Deploy an App from a Public Git Repo
**Objective:** Get ArgoCD running end-to-end against a real Git-backed Application.

**Tasks:**
1. Install ArgoCD into your local cluster via its standard install manifest.
2. Port-forward the ArgoCD API server and log in with the CLI.
3. Create an `Application` pointing at a public sample manifest repository, with `syncPolicy.automated.selfHeal: true`.
4. Confirm the Application shows `Synced`/`Healthy` in `argocd app get`.
5. Manually `kubectl edit` one of the deployed resources to introduce drift (e.g., change replica count), and observe ArgoCD automatically revert it back to match Git within seconds, proving `selfHeal` works.

#### Lab 2: Build a Kustomize Base/Overlay Structure and Diff Environments
**Objective:** Practice the base/overlay pattern independent of any GitOps controller first.

**Tasks:**
1. Create a `base/` directory with a Deployment and Service plus a `kustomization.yaml`.
2. Create `overlays/dev` and `overlays/prod` directories, each referencing `../../base` with different replica counts and a different image tag via the `images` field.
3. Run `kubectl kustomize overlays/dev` and `kubectl kustomize overlays/prod` locally (no cluster needed) and diff the two rendered outputs to confirm only the intended fields differ.
4. Apply the `dev` overlay to your local cluster with `kubectl apply -k overlays/dev` and confirm the resulting Deployment matches expectations.

#### Lab 3: Simulate a Full GitOps Promotion Flow
**Objective:** Experience the "Git commit is the deployment" model end-to-end.

**Tasks:**
1. Using the ArgoCD Application from Lab 1 (or a Flux Kustomization, if you set up Flux instead), point it at your own fork of the sample repo rather than the upstream one.
2. Edit the overlay's image tag directly in your fork via a Git commit (not `kubectl`), and push.
3. Watch the GitOps controller detect the new commit and automatically reconcile the cluster to the new image tag, without you running any `kubectl` or `argocd`/`flux` command manually.
4. Introduce a deliberately broken manifest (e.g., invalid YAML indentation) in a new commit and observe how the controller reports the sync failure, then revert the commit and confirm the cluster recovers automatically once the fix is pushed.
""",
        "insight": """
### Interview Q&A

#### Q1: What's the core security advantage of a pull-based GitOps model (ArgoCD/Flux) over a traditional push-based CI/CD pipeline?
* **Answer:** In a push model, the CI system (running outside the cluster, often on a shared SaaS runner) must hold long-lived credentials with write access to the cluster's API server, meaning a compromised CI pipeline is a direct path to compromising production. In a pull model, the reconciliation controller runs inside the cluster and only needs read access to the Git repository -- there's no inbound credential into the cluster from an external system at all, dramatically shrinking the attack surface, and any change still requires a Git commit (which is naturally auditable and reviewable via PRs).

#### Q2: In ArgoCD, an Application shows `SyncStatus: Synced` but `HealthStatus: Degraded`. What does that combination actually mean?
* **Answer:** `SyncStatus` only reflects whether the live cluster manifests match what's declared in Git byte-for-byte -- it says nothing about whether the workload is actually functioning. `HealthStatus` is a separate, resource-type-aware check (for a Deployment, whether the desired replica count is Ready; for a Service, whether it has endpoints, etc.). `Synced` + `Degraded` means Git and the cluster agree on the *desired* state, but that desired state isn't actually working right now -- for example, a bad image tag that was correctly deployed exactly as committed, but the container is crash-looping. This distinction is exactly why relying on sync status alone is insufficient for verifying a deployment actually succeeded.

#### Q3: Why would a team choose Flux's separated-controller architecture over ArgoCD's more monolithic Application model, or vice versa?
* **Answer:** Flux's separation into distinct controllers for sourcing, applying, and image automation makes it more composable for teams that want to build custom pipelines from smaller pieces, and its native image-update-automation controllers can commit new image tags back to Git automatically, closing the loop without an external CI step. ArgoCD's more monolithic `Application` model instead centers on a polished built-in UI showing live resource trees/diffs and a first-class multi-cluster/multi-tenant `AppProject` model, which teams that prioritize visibility and self-service for many application teams often prefer. Neither is strictly "better" -- the choice is largely about whether a team values Flux's composability or ArgoCD's integrated visualization and project-based access control more.

### GitOps Certification & Interview Focus
- Be able to clearly explain sync vs. health status in ArgoCD -- it's one of the most commonly misunderstood distinctions even among practitioners.
- Understand that Kustomize overlays are a *build-time* concept (rendering final YAML) that's completely independent of GitOps controllers, which only handle *apply-time* reconciliation -- the two compose but are not the same layer.
- Be ready to discuss how progressive delivery (canary/blue-green via Argo Rollouts or Flagger) layers on top of, rather than replaces, the base GitOps reconciliation loop.
""",
    },
]
