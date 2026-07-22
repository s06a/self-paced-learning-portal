COURSE_ID = "mid_level_kubernetes_engineer"
COURSE_TITLE = "Mid-Level Kubernetes Engineer"
COURSE_DESCRIPTION = "Transition from deploying simple stateless apps to orchestrating complex, resilient, stateful, and secure environments. Learn to configure advanced scheduling, dynamic storage with CSI, multi-tenant networking, RBAC, GitOps deployments, and enterprise monitoring."

CURRICULUM_DATA = [
    {
        "id": 1,
        "title": "Module 1: Advanced Workloads, Resource Allocation & Scheduling",
        "theory": """### Stateful Workloads vs. Stateless Architectures
Stateless applications (like REST APIs) do not preserve client context or transactional state across requests. If a Pod fails, another takes its place immediately. Conversely, stateful applications (like PostgreSQL, Cassandra, or ZooKeeper) require stable network identities, persistent disk state, and orderly scaling/startup sequences. 

Kubernetes handles stateful workloads using the `StatefulSet` controller. Unlike standard Deployments, StatefulSets ensure that each Pod receives:
* A stable, unique ordinal index (e.g., `web-0`, `web-1`).
* Dedicated storage volumes dynamically linked to the specific ordinal index.
* A stable network DNS identity using a Headless Service (a cluster service with `clusterIP: None` mapping directly to the Pod IPs via DNS records).

### Advanced Scheduling Mechanics
The Kubernetes Scheduler binds incoming Pods to nodes using filtering (Predicates) and scoring (Priorities). Advanced configuration allows you to guide or enforce these scheduling decisions:
* **nodeSelector:** Simple key-value mapping to match labels on target nodes.
* **Node Affinity/Anti-Affinity:** Offers richer logical evaluation, including soft rules (`preferredDuringSchedulingIgnoredDuringExecution`) and hard constraints (`requiredDuringSchedulingIgnoredDuringExecution`).
* **Pod Affinity/Anti-Affinity:** Directs Pod placement relative to other running Pods. For instance, Pod Anti-Affinity is critical for high availability (HA) to ensure duplicate instances of an API gateway are not co-located on the same physical node or zone.
* **Taints & Tolerations:** Restricts which pods can deploy on which nodes. A Taint blocks pods unless they possess a corresponding Toleration. This is commonly used to dedicate nodes to specific GPU workloads, database clusters, or to isolate system control planes.

### Resource Allocations & Quality of Service (QoS)
Configuring precise CPU and memory constraints guarantees cluster-wide stability.
* **Requests:** The minimum resources the Scheduler uses to assign a Pod to a node.
* **Limits:** The maximum resources a Pod can consume. Exceeding memory limits results in immediate Out-Of-Memory (OOM) termination. Exceeding CPU limits results in throttling, but not termination.

Based on these values, Kubernetes assigns one of three Quality of Service (QoS) classes:
1. **Guaranteed:** Requests match Limits exactly for both CPU and memory.
2. **Burstable:** Requests and Limits are configured, but do not match (or only one resource is defined).
3. **BestEffort:** No requests or limits are declared. These are terminated first during node resource starvation.

To safeguard highly critical services from administrative disruption (such as automatic node upgrades, drain procedures, or automated scaling operations), engineers deploy a `PodDisruptionBudget` (PDB). A PDB specifies the minimum available or maximum unavailable Pod count a controller must maintain during voluntary maintenance windows.""",
        "commands": """### Command & Syntax Reference
```bash
# Safely drain a node by evicting all pods (excluding DaemonSets)
kubectl drain node-01 --ignore-daemonsets --delete-emptydir-data

# Make a cordoned node schedulable again
kubectl uncordon node-01

# View resources requested and consumed by cluster nodes
kubectl top node

# View resources consumed by pods in the current namespace
kubectl top pod

# Label a node for affinity operations
kubectl label nodes node-02 disktype=ssd

# Show node labels
kubectl get nodes --show-labels

# Apply a taint to a specific node (NoSchedule policy)
kubectl taint nodes node-03 dedicated=databases:NoSchedule

# Remove a taint from a node
kubectl taint nodes node-03 dedicated=databases:NoSchedule-

# Describe resource configurations and QoS metrics for a pod
kubectl describe pod web-app-0 | grep -A 5 "QoS Class"
```""",
        "examples": """### Real-World Examples

#### Example 1: StatefulSet with Headless Service for Clustered Cache
**Situation:** A distributed key-value store requires independent network identities and distinct storage persistence for each replica.
**Action:** Deploy a Headless Service accompanied by a StatefulSet defining a `volumeClaimTemplate` to automatically provision localized PVs.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: cache-service
  labels:
    app: redis-cluster
spec:
  ports:
  - port: 6379
    name: redis
  clusterIP: None
  selector:
    app: redis-cluster
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: cache
spec:
  serviceName: "cache-service"
  replicas: 3
  selector:
    matchLabels:
      app: redis-cluster
  template:
    metadata:
      labels:
        app: redis-cluster
    spec:
      containers:
      - name: redis
        image: redis:7.0-alpine
        ports:
        - containerPort: 6379
          name: redis
        volumeMounts:
        - name: cache-data
          mountPath: /data
  volumeClaimTemplates:
  - metadata:
      name: cache-data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 5Gi
```

#### Example 2: Pod Anti-Affinity for Zone-Redundant Web Deployments
**Situation:** A high-throughput API deployment must distribute its pods across multiple availability zones to ensure fault tolerance.
**Action:** Configure a hard Pod Anti-Affinity rule matching the deployment's labels based on the zone topology key.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: external-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: external-api
  template:
    metadata:
      labels:
        app: external-api
    spec:
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchExpressions:
              - key: app
                operator: In
                values:
                - external-api
            topologyKey: topology.kubernetes.io/zone
      containers:
      - name: api-server
        image: nginx:1.25-alpine
        resources:
          requests:
            cpu: "250m"
            memory: "256Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"
```

#### Example 3: DaemonSet for Log Gathering with Tolerations
**Situation:** An infrastructure logging agent must be running on every active node, including master/control-plane nodes which contain specific scheduler taints.
**Action:** Deploy a DaemonSet featuring the system tolerations needed to schedule across all control-plane nodes.

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: infra-logger
  namespace: kube-system
spec:
  selector:
    matchLabels:
      app: infra-logger
  template:
    metadata:
      labels:
        app: infra-logger
    spec:
      tolerations:
      - key: node-role.kubernetes.io/master
        operator: Exists
        effect: NoSchedule
      - key: node-role.kubernetes.io/control-plane
        operator: Exists
        effect: NoSchedule
      containers:
      - name: agent
        image: fluent/fluent-bit:2.1
        resources:
          requests:
            cpu: "100m"
            memory: "128Mi"
          limits:
            cpu: "200m"
            memory: "256Mi"
```

#### Example 4: PodDisruptionBudget for High-Availability APIs
**Situation:** A production billing system must preserve at least 2 online replicas during node maintenance operations, manual upgrades, or cluster sizing events.
**Action:** Implement a matching PodDisruptionBudget targeting the billing application deployment.

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: billing-api-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: billing-api
```

#### Example 5: Scheduled Nightly Database Backup CronJob
**Situation:** Database backups must run daily at midnight. Parallel backups cannot occur simultaneously, and missed executions must be avoided.
**Action:** Define a CronJob with `concurrencyPolicy: Forbid` and a defined resource constraints template.

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: nightly-backup
spec:
  schedule: "0 0 * * *"
  concurrencyPolicy: Forbid
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 5
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: pg-dump
            image: postgres:15-alpine
            command:
            - /bin/sh
            - -c
            - "echo 'Exporting database snapshot...'; pg_dumpall -U postgres > /backup/db_snap.sql"
            resources:
              requests:
                cpu: "500m"
                memory: "512Mi"
              limits:
                cpu: "1"
                memory: "1Gi"
          restartPolicy: OnFailure
```""",
        "exercise": """### Hands-On Labs

#### Lab 1: Deploying a Headless Service and StatefulSet
* **Objective:** Establish a cluster-addressable Headless Service and run a StatefulSet verifying state persistence.
* **Tasks:**
  1. Define and apply a Headless Service named `datastore-svc` with `clusterIP: None` and label selector `app=datastore`.
  2. Implement a StatefulSet named `datastore` managing 2 replicas running `busybox`. Have them write their hostname to a persistent file under `/data/host.txt` using a Dynamic Volume Claim.
  3. Validate using DNS lookup (`nslookup datastore-0.datastore-svc`) from inside a temporary busybox container.

#### Lab 2: Enforcing Pod Anti-Affinity
* **Objective:** Prevent duplicate instances of a web service from occupying the same nodes.
* **Tasks:**
  1. Create a Deployment named `redundant-web` with 3 replicas.
  2. Add a `podAntiAffinity` block under `spec.template.spec` enforcing hard anti-affinity (`requiredDuringSchedulingIgnoredDuringExecution`) for labels matching `app: redundant-web` on the topology key `kubernetes.io/hostname`.
  3. Validate that if you have only 2 nodes, the third pod remains in a `Pending` state.

#### Lab 3: Configuring Taints on a Node and Tolerations on a Pod
* **Objective:** Secure a worker node for a specific processing utility, isolating standard workloads.
* **Tasks:**
  1. Add a taint to a specific cluster worker node: `kubectl taint nodes <node-name> processing=batch:NoSchedule`.
  2. Deploy a general application pod without tolerations and verify that it avoids the tainted node.
  3. Deploy a batch application pod that explicitly tolerates the `processing=batch:NoSchedule` taint, verifying scheduling success.

#### Lab 4: Implementing a PodDisruptionBudget
* **Objective:** Prevent active worker nodes from evicting vital system pods under manual administration tasks.
* **Tasks:**
  1. Deploy a web service named `essential-app` containing 3 replicas.
  2. Apply a PodDisruptionBudget ensuring a `minAvailable` value of 2.
  3. Attempt to run `kubectl drain` on the node holding the pods, monitoring the API rejection mechanisms.

#### Lab 5: Designing a CronJob with Concurrency Constraints
* **Objective:** Configure an asynchronous processing CronJob preventing job overlap.
* **Tasks:**
  1. Create a CronJob scheduling a workload executing every minute.
  2. Include a logic sleep script running for 120 seconds.
  3. Apply `concurrencyPolicy: Forbid` and monitor that the scheduler skips execution if the prior pod has not finished.""",
        "insight": """### Interview Q&A

#### Q1: What is the difference between hard (requiredDuringScheduling) and soft (preferredDuringScheduling) node affinity?
* **Answer:** Hard affinity acts as a strict selector constraint; if no node meets the matching requirements, the pod will remain in a `Pending` state. Soft affinity operates as a ranking metric; the scheduler attempts to match the defined criteria to score nodes, but if no suitable node fits the criteria, it will schedule the pod onto any available fallback node to avoid downtime.

#### Q2: How do Kubernetes QoS (Quality of Service) classes work, and what triggers an Out-Of-Memory (OOM) kill?
* **Answer:** Kubernetes allocates QoS classes (`Guaranteed`, `Burstable`, `BestEffort`) based on specified resource blocks. If memory resource usage on a node hits critical limits, the Linux kernel's Out-Of-Memory (OOM) killer kicks in. It terminates pods based on their `OOMScore`, which is determined by their QoS class and the percentage of requested memory they consume. `BestEffort` pods are terminated first, followed by `Burstable` pods consuming beyond their requested values. `Guaranteed` pods are highly isolated and only terminated as a final option.

#### Q3: Why does a StatefulSet require a headless service?
* **Answer:** Normal services run as load-balanced gateways that route traffic randomly across dynamic IP endpoints. A StatefulSet needs to interact with individual nodes directly (e.g., in a primary-replica cluster architecture). A headless service (`clusterIP: None`) enables client systems to run DNS lookups that return the full set of pod internal IPs, and resolves pod-specific domains (e.g., `pod-0.headless-service`) straight to the matching host.

#### Q4: What is the purpose of a PodDisruptionBudget, and how does it safeguard workloads during maintenance?
* **Answer:** A PodDisruptionBudget (PDB) defines the structural limits of tolerated downtime caused by voluntary cluster administration tasks (such as node drains, cluster upgrades, or autoscaling actions). The API server blocks eviction requests that violate the threshold (e.g., maintaining at least 2 active replicas or allowing at most 1 offline pod), pausing operations until resource capacities normalize.

#### Q5: How do CronJobs handle missed schedules or concurrent executions?
* **Answer:** CronJobs track executions via an internal controller. If `concurrencyPolicy` is set to `Allow`, concurrent instances are spawned without limits. If set to `Forbid`, active jobs block upcoming scheduling loops. If set to `Replace`, the active container is destroyed to make room for the new instance. The field `startingDeadlineSeconds` establishes the deadline threshold for starting missed executions before marking them failed."""
    },
    {
        "id": 2,
        "title": "Module 2: Storage, CSI, and Network Routing",
        "theory": """### Dynamic Volume Provisioning & StorageClasses
Stateless containers lack disk persistency; when a container restarts, modifications are wiped out. Kubernetes isolates storage configurations using dynamic lifecycle objects:
* **StorageClass (SC):** Defines the storage backend parameters, CSI driver provisioner, and reclaim policies (e.g., `Delete` vs. `Retain`).
* **PersistentVolume (PV):** A cluster-wide physical disk allocation configured by an administrator or automatically spawned by the StorageClass controller.
* **PersistentVolumeClaim (PVC):** A user's logical request for storage. PVCs state specific storage sizes and dynamic access parameters:
  - `ReadWriteOnce (RWO)`: Mounted as read-write by a single node.
  - `ReadOnlyMany (ROX)`: Mounted read-only by many nodes.
  - `ReadWriteMany (RWX)`: Mounted as read-write by many nodes concurrently.

### Container Storage Interface (CSI) Drivers
The Container Storage Interface (CSI) is an industry-standard interface that allows storage providers to build out-of-tree plugins for Kubernetes. CSI drivers run as localized controllers within the cluster, handling operations such as mounting, formatting, resizing, snapshotting, and provisioning raw cloud block devices (e.g., AWS EBS, Azure Disk, GCE PD) or network storage systems (e.g., Ceph, NFS).

### K8s Network Routing: Ingress & Gateway API
Routing external client traffic down into cluster workloads has evolved through distinct layers:
* **Ingress:** A legacy resource defining HTTP routing rules. Ingress requires an Ingress Controller (e.g., `ingress-nginx`) to process these rule manifests and translate them into routing engine configurations (like Nginx upstream directives).
* **Gateway API:** The modern evolution of Ingress. It structures routing responsibilities across multi-tenant personas:
  - `GatewayClass`: Defined by infrastructure administrators to assign controller types.
  - `Gateway`: Describes the entry point configuration (such as ports, protocols, and TLS certificates).
  - `HTTPRoute` / `GRPCRoute`: Defined by application developers to point external URIs to backend service targets. This decouples infrastructure operations from application logic.

### Network Policies
By default, Kubernetes pods run with an open "non-isolated" policy, permitting open lateral communication across namespaces (East-West traffic). A `NetworkPolicy` acts as a distributed firewall using label selectors. Policies define:
* **Ingress rules:** Restricting incoming traffic source labels, ports, and IP blocks.
* **Egress rules:** Limiting outbound paths, securing environments from unauthorized external calls or lateral database exfiltration.""",
        "commands": """### Command & Syntax Reference
```bash
# List all active cluster StorageClasses
kubectl get storageclass

# Check active PersistentVolumes and their bound states
kubectl get pv

# Check namespace PersistentVolumeClaims
kubectl get pvc

# Check Ingress configurations and external IP mappings
kubectl get ingress

# Check Gateway API structures
kubectl get gateway,httproute

# Retrieve and debug CSI driver controllers active inside the cluster
kubectl get csidrivers

# Describe active network policy configurations
kubectl describe networkpolicy database-policy
```""",
        "examples": """### Real-World Examples

#### Example 1: Dynamic StorageClass and PVC Definition
**Situation:** A mid-level engineer needs to define a fast SSD-backed dynamic storage provisioning configuration for localized microservices.
**Action:** Create a custom StorageClass employing an volume expansion binding, and write a matching PersistentVolumeClaim.

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: kubernetes.io/aws-ebs
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
parameters:
  type: gp3
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: data-pvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: fast-ssd
  resources:
    requests:
      storage: 10Gi
```

#### Example 2: Secure TLS Ingress with Nginx Annotations
**Situation:** Route external HTTP/HTTPS traffic to a frontend dashboard microservice, enforcing secure TLS termination and redirecting HTTP calls.
**Action:** Deploy an Ingress resource with matching TLS references and specific configuration annotations.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: dynamic-web-ingress
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/backend-protocol: "HTTP"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - dashboard.example.com
    secretName: wildcard-tls-secret
  rules:
  - host: dashboard.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: dashboard-service
            port:
              number: 80
```

#### Example 3: Decoupled Routing via Gateway API and HTTPRoute
**Situation:** Transition a legacy Ingress setup to a modern Gateway API architecture for multi-tenant service isolation.
**Action:** Establish a standard Gateway listener targeting an HTTPRoute targeting a secure billing backend.

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: main-gateway
spec:
  gatewayClassName: eg-gateway-class
  listeners:
  - name: http
    protocol: HTTP
    port: 80
    allowedRoutes:
      namespaces:
        from: All
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: billing-route
  namespace: finance
spec:
  parentRefs:
  - name: main-gateway
    namespace: default
  rules:
  - matches:
    - path:
        type: PathPrefix
        value: /billing
    backendRefs:
    - name: billing-svc
      port: 8080
```

#### Example 4: Restricting Database Access via Ingress NetworkPolicy
**Situation:** Secure a database cluster so that only pods belonging to the billing backend can establish connections over port 5432.
**Action:** Define an isolated NetworkPolicy matching database pods that filters traffic based on pod label selectors.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: db-access-policy
  namespace: database-layer
spec:
  podSelector:
    matchLabels:
      role: db
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: finance
      podSelector:
        matchLabels:
          app: billing-api
    ports:
    - protocol: TCP
      port: 5432
```

#### Example 5: Strict Outbound Egress Isolation for Microservices
**Situation:** Restrict a payment integration microservice from initiating communication to random IP targets, limiting outbound traffic to specific subnets.
**Action:** Apply an egress-focused NetworkPolicy specifying permitted external CIDR ranges.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: egress-isolation-policy
spec:
  podSelector:
    matchLabels:
      app: checkout
  policyTypes:
  - Egress
  egress:
  - to:
    - ipBlock:
        cidr: 203.0.113.0/24
    ports:
    - protocol: TCP
      port: 443
```""",
        "exercise": """### Hands-On Labs

#### Lab 1: Dynamic Storage Mount Troubleshooting
* **Objective:** Create and mount storage dynamically, resolving potential volume binding errors.
* **Tasks:**
  1. Define a Dynamic StorageClass with `volumeBindingMode: WaitForFirstConsumer`.
  2. Create a PersistentVolumeClaim requesting 20Gi from this StorageClass.
  3. Spin up an Nginx Pod mounting this PVC under `/usr/share/nginx/html`, write an `index.html` file, and verify persistent behavior across Pod restarts.

#### Lab 2: Multi-Host Ingress Routing Integration
* **Objective:** Deploy and verify an ingress resource routing multi-domain traffic.
* **Tasks:**
  1. Create two microservice deployments: `web-one` and `web-two`.
  2. Deploy an Ingress configuring virtual host routing (`one.local` pointing to `web-one`, and `two.local` pointing to `web-two`).
  3. Validate access mapping patterns using curl commands targeting localized header formats (`curl -H "Host: one.local" http://<ingress-ip>`).

#### Lab 3: Translating Ingress to Gateway API
* **Objective:** Re-architect web access patterns to use Gateway API resources.
* **Tasks:**
  1. Verify the Gateway API CRDs are installed on your environment.
  2. Instantiate a central `Gateway` listening on Port 80.
  3. Author an `HTTPRoute` linking prefix paths `/api/v1` and `/api/v2` to target services, verifying structural path matching.

#### Lab 4: Creating an Isolate Namespace NetworkPolicy
* **Objective:** Establish a strict default-deny network posture across an entire namespace.
* **Tasks:**
  1. Set up a dedicated testing namespace called `secure-zone`.
  2. Apply a default-deny NetworkPolicy that blocks all ingress and egress traffic by default.
  3. Deploy a client pod inside the namespace, testing connectivity and verifying complete isolation.

#### Lab 5: Establishing Fine-Grained DB Communication Links
* **Objective:** Selectively permit cross-namespace database communication.
* **Tasks:**
  1. Deploy a database service in namespace `db-net`.
  2. Apply a NetworkPolicy allowing ingress traffic exclusively from pods labeled `access-tier=backend` within namespace `app-net`.
  3. Execute connectivity checks using `nc` or `telnet` from unauthorized namespaces to verify the traffic is blocked.""",
        "insight": """### Interview Q&A

#### Q1: What is the primary difference between legacy Ingress and the new Gateway API?
* **Answer:** Legacy Ingress is a single, monolithic resource representing routing rules, which often leads to conflict and maintenance bottlenecks when shared across multiple teams. The Gateway API is role-oriented, decoupling routing into separate CRDs: `GatewayClass` (defined by infrastructure providers), `Gateway` (managed by platform operators to configure IP allocations, TLS, and load balancer entries), and `HTTPRoute`/`GRPCRoute` (managed by developers to define application-level path rules).

#### Q2: Explain the dynamic volume provisioning cycle of PVCs and PVs.
* **Answer:** When a user creates a PersistentVolumeClaim (PVC) specifying a specific StorageClass, the corresponding dynamic provisioner (such as an EBS or Azure Disk CSI driver) watches the PVC events. It provisions the requested disk block inside the cloud or storage provider, instantiates a corresponding PersistentVolume (PV) object in Kubernetes, and binds the PV directly to the user's PVC.

#### Q3: What are the main reclaim policies for PersistentVolumes, and what happens to the underlying data?
* **Answer:** The two primary reclaim policies are `Delete` and `Retain`. Under `Delete`, deleting a PVC automatically removes the associated PV and the underlying physical disk block from the storage provider. Under `Retain`, deleting a PVC marks the PV status as `Released` but does not delete the physical disk block, allowing storage admins to manually recover data or re-import the volume.

#### Q4: How does an Ingress Controller route traffic inside the cluster?
* **Answer:** The Ingress Controller acts as an edge reverse-proxy. It continuously watches the Kubernetes API for modifications to Endpoints, Pods, Services, and Ingress resources. When a client requests a resource, the controller bypasses standard Service IP round-robin routing and maps connections straight to active pod IP backends to minimize overhead and support advanced sticky-sessions or headers.

#### Q5: Why are default-deny NetworkPolicies recommended, and how do you implement them?
* **Answer:** By default, Kubernetes pods accept connections from any IP or namespace in the cluster. Implementing a default-deny policy (which selects all pods with empty curly braces `{}` and defines no ingress/egress rules) blocks unauthorized traffic by default. This forces team members to explicitly define required network communication paths, establishing a reliable "least-privilege" zero-trust architecture."""
    },
    {
        "id": 3,
        "title": "Module 3: Security, RBAC, and GitOps Packaging",
        "theory": """### Role-Based Access Control (RBAC)
Kubernetes authenticates requests but relies on Role-Based Access Control (RBAC) for authorization. RBAC uses four API resources:
* **Role:** Namespace-scoped access rules. It contains list structures of allowed verbs (e.g., `get`, `list`, `watch`, `create`, `update`, `delete`) mapped to resource types (e.g., `pods`, `services`, `deployments`).
* **ClusterRole:** Cluster-scoped access rules. It operates identically to a Role but controls non-namespaced resources (like `Nodes`, `PersistentVolumes`) or grants permission across all namespaces in the cluster.
* **RoleBinding:** Assigns a `Role` to a user, group, or `ServiceAccount` within a specific namespace.
* **ClusterRoleBinding:** Assigns a `ClusterRole` to target users, groups, or ServiceAccounts globally across all namespaces.

### Secrets Management and Security
By default, native Kubernetes Secrets are stored as unencrypted Base64-encoded strings within `etcd`. Anyone with read access to the API or etcd can decode these secrets. This risk can be mitigated in production using external workflows:
* **Enabling Encryption-at-Rest:** Configured on the control plane using providers like KMS.
* **Sealed Secrets:** Translates standard secrets into encrypted custom CRDs (`SealedSecret`) using public/private key-pair operations. These can be safely stored in public Git repositories.
* **External Secrets Operator:** Dynamically pulls secrets from external vaults (e.g., HashiCorp Vault, AWS Secrets Manager) and mounts them into native namespaces dynamically.

### GitOps Packaging: Helm and Kustomize
Managing raw manifests for multiple environments (Dev, Staging, Prod) quickly becomes unmanageable. Two main approaches help resolve this problem:
* **Helm:** A package manager that treats resources as a cohesive application (a Chart). Helm uses Go templating to dynamically inject parameters into manifests based on variables defined in a `values.yaml` file.
* **Kustomize:** A template-free configuration tool integrated directly into `kubectl`. It uses a base directory of common manifests and applies overlay overrides (such as `kustomization.yaml` patches) to customize resources for specific environments without duplicating code.

### In-Cluster Continuous Delivery (GitOps)
GitOps defines Git as the single source of truth for desired infrastructure and application state. Agents like **ArgoCD** or **FluxCD** run inside the cluster to reconcile configurations. They continuously pull manifest changes from git repos and apply them to the cluster, automatically overriding manual cluster updates (drift detection) to keep systems secure and consistent.""",
        "commands": """### Command & Syntax Reference
```bash
# Verify if current user context can perform an API operation
kubectl auth can-i create deployments --namespace default

# Check permissions for a specific service account
kubectl auth can-i list pods --as=system:serviceaccount:default:monitoring-sa

# Create a local development Helm template from local parameters
helm create my-app

# Render Helm template locally to check for syntax errors
helm template my-app ./my-app-chart/ -f values-dev.yaml

# Package a local Helm chart into an archive
helm package ./my-app-chart/

# Install or upgrade a Helm release inside a target namespace
helm upgrade --install my-app-release ./my-app-chart/ --namespace production

# Apply a local Kustomize configuration overlay directory
kubectl apply -k ./overlays/production/

# Render Kustomize configuration to verify structural generation output
kubectl kustomize ./overlays/production/
```""",
        "examples": """### Real-World Examples

#### Example 1: RBAC Developer Namespace Isolation
**Situation:** Set up an isolated team namespace so developers can manage deployments, pods, and services, while blocking modifications to ingress and persistent volumes.
**Action:** Define a `Role` and a `RoleBinding` targeting the specific developer group within the namespace.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: engineering
  name: developer-role
rules:
- apiGroups: [""]
  resources: ["pods", "services", "configmaps", "persistentvolumeclaims"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
- apiGroups: ["apps"]
  resources: ["deployments", "statefulsets"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: bind-developers
  namespace: engineering
spec:
  subjects:
  - kind: Group
    name: "oidc:dev-group"
    apiGroup: rbac.authorization.k8s.io
  roleRef:
    kind: Role
    name: developer-role
    apiGroup: rbac.authorization.k8s.io
```

#### Example 2: Read-Only Cluster-Wide Monitoring ServiceAccount
**Situation:** A Prometheus monitoring agent requires read-only cluster access to scrape node capacity, service endpoints, and namespace definitions.
**Action:** Deploy a dedicated `ServiceAccount` and attach a cluster-wide `ClusterRoleBinding` pointing to the pre-configured `view` ClusterRole.

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: monitoring-collector
  namespace: monitoring
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: monitoring-view-binding
spec:
  subjects:
  - kind: ServiceAccount
    name: monitoring-collector
    namespace: monitoring
  roleRef:
    kind: ClusterRole
    name: view
    apiGroup: rbac.authorization.k8s.io
```

#### Example 3: Kustomize Base and Production Overlay Manifests
**Situation:** A team needs to manage environment-specific configurations without duplicating base resource manifests.
**Action:** Use Kustomize overlays. Define a production patch to scale a base deployment to 5 replicas.

*Directory Structure:*
`base/kustomization.yaml`
`base/deployment.yaml`
`overlays/production/kustomization.yaml`

```yaml
# FILE: base/kustomization.yaml
resources:
  - deployment.yaml
```

```yaml
# FILE: overlays/production/kustomization.yaml
resources:
  - ../../base
patches:
- target:
    kind: Deployment
    name: web-app
  patch: |-
    - op: replace
      path: /spec/replicas
      value: 5
```

#### Example 4: Customizable Helm Chart Templates
**Situation:** A deployment configuration must dynamically scale its replica counts and change configuration settings based on environment-specific parameters.
**Action:** Write a dynamic Helm deployment template that injects variables from a `values.yaml` file.

```yaml
# FILE: my-app/templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-app
spec:
  replicas: {{ .Values.replicaCount | default 2 }}
  selector:
    matchLabels:
      app: {{ .Release.Name }}
  template:
    metadata:
      labels:
        app: {{ .Release.Name }}
    spec:
      containers:
      - name: application
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
        env:
        - name: ENV_MODE
          value: "{{ .Values.envMode }}"
```

#### Example 5: ArgoCD Application GitOps Deployment
**Situation:** Automatically synchronize deployment state with an external GitHub registry path to implement GitOps.
**Action:** Apply an ArgoCD Application resource that points to the target repository and enforces automated synchronization.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: live-payment-service
  namespace: argocd
spec:
  project: default
  source:
    repoURL: 'https://github.com/enterprise/gitops-infra.git'
    targetRevision: HEAD
    path: apps/payment-service/overlays/production
  destination:
    server: 'https://kubernetes.default.svc'
    namespace: production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```""",
        "exercise": """### Hands-On Labs

#### Lab 1: Testing RBAC Access Permissions
* **Objective:** Verify RBAC policies by simulating operations using different ServiceAccount identities.
* **Tasks:**
  1. Create a namespace named `test-rbac` and a ServiceAccount named `read-only-sa`.
  2. Apply a Role and RoleBinding allowing ONLY `get` and `list` operations for Pod resources.
  3. Validate access permissions using target context command parameters: `kubectl auth can-i create pods --as=system:serviceaccount:test-rbac:read-only-sa`.

#### Lab 2: Authoring a Multi-Environment Kustomize Build
* **Objective:** Use Kustomize to configure base templates and environment-specific overlays (Dev and Prod).
* **Tasks:**
  1. Create a `base` directory containing an Nginx deployment manifest.
  2. Create a `dev` overlay directory specifying `replicas: 1` and a `prod` overlay specifying `replicas: 3`.
  3. Run `kubectl kustomize` against each overlay to verify that the generated manifests contain the expected configurations.

#### Lab 3: Creating and Packaging a Custom Helm Chart
* **Objective:** Design, package, and install a dynamic custom Helm chart.
* **Tasks:**
  1. Initialize a Helm template layout locally using `helm create simple-server`.
  2. Modify the values structure to inject variables for the application Port and host parameters.
  3. Run `helm package` and install the package with dynamic environment parameter flags (`--set replicaCount=3`).

#### Lab 4: Configuring an ArgoCD Application for Automated Sync
* **Objective:** Deploy and monitor a GitOps sync loop.
* **Tasks:**
  1. Deploy the standard community ArgoCD operator on your local cluster.
  2. Create a git repository containing simple, valid Kubernetes manifests.
  3. Deploy an ArgoCD Application resource pointing to your git repository, make an update in Git, and verify that the changes automatically reconcile on the cluster.

#### Lab 5: Implementing SealedSecrets Management
* **Objective:** Encrypt and commit a simulated database password securely to Git.
* **Tasks:**
  1. Install the Sealed Secrets controller in your cluster.
  2. Use the `kubeseal` CLI utility to generate a `SealedSecret` manifest from a local password secret.
  3. Verify that the decrypted password secret is correctly generated inside the cluster, while the generated SealedSecret manifest can be safely saved to public git repositories.""",
        "insight": """### Interview Q&A

#### Q1: What is the difference between a Role and a ClusterRole?
* **Answer:** A `Role` defines namespaced permissions, meaning its access rules apply only within the namespace where it is deployed. A `ClusterRole` defines non-namespaced, cluster-wide permissions. It is used to govern cluster-scoped resources (such as `Nodes` or `PersistentVolumes`), cluster infrastructure patterns, or to define permissions that apply across all namespaces simultaneously.

#### Q2: Why are native Kubernetes Secrets considered insecure at rest, and how do you mitigate this?
* **Answer:** By default, Kubernetes Secrets are stored as unencrypted, Base64-encoded strings within `etcd`. They are not encrypted or hashed, meaning anyone with access to the database can read them. To secure secrets, you can encrypt the database at rest (using KMS encryption-at-rest keys), manage secrets using specialized tools like Sealed Secrets (public-key client-side encryption), or retrieve them dynamically at runtime from external vault providers like HashiCorp Vault.

#### Q3: When would you use Kustomize over Helm, and vice versa?
* **Answer:** Use Kustomize when you want to manage environment variations without adding templating complexity, as it works by patching base YAML configurations directly. Use Helm when you are sharing public applications or need a full-featured package manager with helper functions, complex loops, template validation, and release management.

#### Q4: How does a GitOps operator like ArgoCD reconcile cluster state with Git?
* **Answer:** ArgoCD runs a continuous reconciliation loop within the cluster. It compares the live resources in the cluster against the target states defined in a git repository. If it detects changes in Git, it applies them to the cluster (Sync). If it detects manual changes in the cluster that deviate from Git (Drift), it automatically overrides those changes to restore the desired state from Git (Self-Healing).

#### Q5: How do you verify what actions a ServiceAccount can perform?
* **Answer:** You can use the `kubectl auth can-i` command. By appending the target resource and namespace details, and specifying the target ServiceAccount with the `--as` flag, you can query authorization details without manually parsing complex RBAC YAML manifests."""
    },
    {
        "id": 4,
        "title": "Module 4: K8s-Centric Observability & Custom Autoscaling",
        "theory": """### Prometheus Operator & ServiceMonitors
Monitoring Kubernetes workloads requires dynamic discovery. The Prometheus Operator simplifies monitoring configuration using custom resources:
* **ServiceMonitor:** A custom resource that tells Prometheus how to discover and scrape metrics from Kubernetes Services. It uses label selectors to target specific services and scraper configurations.
* **PodMonitor:** Directly scrapes metrics endpoints on Pods, bypassing the Service layer entirely. This is useful for monitoring components that run without dynamic load balancing (such as standalone worker agents).

### Kube-State-Metrics vs. Metrics Server
Two primary metrics components provide different insights into the cluster:
1. **Metrics-Server:** A resource metrics collector that aggregates temporary, real-time memory and CPU utilization statistics. This data is used by commands like `kubectl top` and scaling components like the Horizontal Pod Autoscaler (HPA).
2. **kube-state-metrics:** A service that generates cluster-state metrics by listening to the Kubernetes API server. It outputs metrics on resource health and state (e.g., how many replicas are running, pod pending times, volume capacities, node schedulability, etc.), which are scraped by Prometheus for long-term storage and visualization.

### Custom Metrics Auto-scaling
Standard horizontal pod autoscaling (HPA) triggers scaling actions based on CPU or memory thresholds. However, high-traffic APIs or asynchronous queue workers often require scaling based on application-level metrics, such as:
* HTTP Request Rate (e.g., requests per second).
* Queue depth / message lag (e.g., Kafka lag, RabbitMQ message counts).

To scale based on these custom metrics, you must configure the **Prometheus Adapter** to query Prometheus metrics and register them as API metrics. This allows the HPA to read application-level metrics directly from the Custom Metrics API (`custom.metrics.k8s.io`).

### Log Shipping and Pipelines
Kubernetes writes container `stdout` and `stderr` streams directly to files on the host node (`/var/log/pods`). If a pod is deleted, its logs are deleted with it. To preserve logs for analysis, you must set up log shippers:
* **FluentBit / Vector:** Lightweight agents that run as DaemonSets on every node. They mount the host's log directory, parse raw JSON container logs, attach Kubernetes metadata (e.g., namespace, pod name, container name), and stream the structured logs to long-term storage (such as Elasticsearch, OpenSearch, Grafana Loki, or S3).""",
        "commands": """### Command & Syntax Reference
```bash
# Check custom metrics registered in the cluster API
kubectl get --raw "/apis/custom.metrics.k8s.io/v1beta1" | jq .

# Verify the metric-server is active and collecting metrics
kubectl get apiservices | grep metrics-server

# List ServiceMonitors configured across all namespaces
kubectl get servicemonitors --all-namespaces

# View HPA autoscaling states and dynamic metric targets
kubectl get hpa

# Inspect the status of active autoscale loops
kubectl describe hpa billing-autoscaler

# View raw logs of log shipping agents
kubectl logs -l app=fluent-bit -n logging --tail=100
```""",
        "examples": """### Real-World Examples

#### Example 1: ServiceMonitor Targeting Microservice Metrics
**Situation:** Configure the Prometheus Operator to automatically scrape metrics from a web service exposing `/metrics` on port 8080.
**Action:** Deploy a `ServiceMonitor` with a matching label selector that targets the service.

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: billing-api-monitor
  namespace: monitoring
  labels:
    release: prometheus-stack
spec:
  selector:
    matchLabels:
      app: billing-api
  namespaceSelector:
    matchNames:
    - finance
  endpoints:
  - port: metrics-port
    path: /metrics
    interval: 15s
```

#### Example 2: Dynamic PodMonitor for Standalone Workers
**Situation:** A group of background processing workers does not run behind a Service, but needs to expose and scrape application metrics directly.
**Action:** Define a `PodMonitor` target matching the worker labels on the designated metrics port.

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PodMonitor
metadata:
  name: worker-monitor
  namespace: monitoring
  labels:
    release: prometheus-stack
spec:
  selector:
    matchLabels:
      role: worker
  podMetricsEndpoints:
  - port: telemetry
    interval: 10s
```

#### Example 3: HorizontalPodAutoscaler (HPA) Scaling on Custom HTTP Metrics
**Situation:** An API deployment needs to scale dynamically based on HTTP request rates, rather than CPU or memory usage.
**Action:** Define an HPA resource targeting the custom metric `http_requests_per_second` sourced from the Custom Metrics API.

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-autoscaler
  namespace: web
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: customer-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "150"
```

#### Example 4: FluentBit DaemonSet Volume Mounting Configuration
**Situation:** A platform team must deploy a FluentBit collector on every node to scrape container console output.
**Action:** Define hostPath mounts within the DaemonSet to securely access and scrape node logs.

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluent-bit
  namespace: logging
spec:
  selector:
    matchLabels:
      app: fluent-bit
  template:
    metadata:
      labels:
        app: fluent-bit
    spec:
      containers:
      - name: fluent-bit
        image: fluent/fluent-bit:2.1
        volumeMounts:
        - name: varlog
          mountPath: /var/log
        - name: varlibdockercontainers
          mountPath: /var/lib/docker/containers
          readOnly: true
      volumes:
      - name: varlog
        hostPath:
          path: /var/log
      - name: varlibdockercontainers
        hostPath:
          path: /var/lib/docker/containers
```

#### Example 5: Custom Prometheus Adapter Metric Mapping Rules
**Situation:** Map custom Prometheus queries (such as system error rates) to the Custom Metrics API so they can be read by HPA controllers.
**Action:** Add discovery and query formatting rules inside the Prometheus Adapter configuration.

```yaml
rules:
- seriesQuery: '{__name__=~"http_requests_total"}'
  resources:
    overrides:
      namespace: {resource: "namespace"}
      pod: {resource: "pod"}
  name:
    matches: "^(.*)_total"
    as: "${1}_per_second"
  metricsQuery: 'sum(rate(<<.Series>>[2m])) by (<<.GroupBy>>)'
```""",
        "exercise": """### Hands-On Labs

#### Lab 1: Deploying a ServiceMonitor for a Microservice
* **Objective:** Configure Prometheus to scrape metrics from a running application using a ServiceMonitor.
* **Tasks:**
  1. Deploy an Nginx deployment with a Prometheus metrics exporter sidecar, exposing metrics on port 9113.
  2. Create a Kubernetes Service pointing to the metrics port, applying the label `monitor-target: active`.
  3. Deploy a ServiceMonitor matching the service label, and verify that the target endpoints show up as active in the Prometheus target dashboard.

#### Lab 2: Querying kube-state-metrics
* **Objective:** Use Prometheus to inspect and analyze cluster-level metrics.
* **Tasks:**
  1. Verify `kube-state-metrics` is deployed and running inside your cluster.
  2. Use port-forwarding to access the Prometheus Query UI.
  3. Execute queries to analyze cluster state, such as checking for failing pods (`kube_pod_status_phase{phase="Failed"}`) or verifying replica limits (`kube_deployment_status_replicas_unavailable`).

#### Lab 3: Configuring custom HPA metrics scaling
* **Objective:** Set up an HPA to scale an application based on a custom metric.
* **Tasks:**
  1. Verify the metrics API returns metric values from Prometheus: `kubectl get --raw "/apis/custom.metrics.k8s.io/v1beta1"`.
  2. Create an HPA that targets a sample application Deployment.
  3. Set up the HPA to trigger scaling when the custom metric `http_requests_per_second` exceeds an average value of 50.

#### Lab 4: Creating a Local FluentBit Log Forwarder
* **Objective:** Deploy and configure FluentBit to forward container logs to stdout.
* **Tasks:**
  1. Create a `logging` namespace and deploy FluentBit as a DaemonSet.
  2. Configure FluentBit to tail container log files from `/var/log/containers/*.log`.
  3. Add a configuration rule that outputs formatted logs directly to standard out, and verify that you can view the forwarded log output in the fluent-bit container logs.

#### Lab 5: Troubleshooting Prometheus Target Failures
* **Objective:** Identify and fix a scraping failure caused by mismatched labels.
* **Tasks:**
  1. Intentionally break a ServiceMonitor configuration by changing its label selectors to point to non-existent values.
  2. Verify that target endpoints disappear from the Prometheus console.
  3. Use `kubectl describe` and Prometheus targets diagnostics to identify the mismatch, correct the labels, and verify that metrics scraping resumes.""",
        "insight": """### Interview Q&A

#### Q1: What is the purpose of kube-state-metrics compared to metrics-server?
* **Answer:** Metrics-Server is a lightweight collector that aggregates real-time CPU and memory usage statistics. It is used to drive autoscaling (HPA) and resource CLI commands (`kubectl top`). kube-state-metrics does not collect resource utilization. Instead, it queries the Kubernetes API server and generates metrics on the health and status of cluster resources (e.g., pending pods, container restarts, limits configurations, and volume usage), which are scrapped by Prometheus for long-term monitoring and alerting.

#### Q2: How does a ServiceMonitor find target endpoints?
* **Answer:** A ServiceMonitor uses label selectors to target services in specific namespaces. It scans these matching services to identify their corresponding endpoint pools, and then queries each endpoint directly on the defined port and path. This design relies on the Prometheus Operator to dynamically update Prometheus scraping targets as pods are added or removed.

#### Q3: How does the Prometheus Adapter bridge custom metrics to the HPA?
* **Answer:** The Prometheus Adapter acts as an API extension server. It translates requests from the Custom Metrics API (`custom.metrics.k8s.io`) into Prometheus Query Language (PromQL) queries. It executes these queries against Prometheus, formats the returned data into API-compatible metrics, and serves them to the Kubernetes HPA controller to drive autoscaling decisions.

#### Q4: Explain how FluentBit collects and parses container logs.
* **Answer:** FluentBit runs as a DaemonSet on each node and mounts the host's log directory (`/var/log/containers`). It tails the console log files produced by the container runtime. It then queries the local Kubernetes API using the pod's name and namespace to retrieve metadata (such as labels, annotations, and owner references), enriches the raw log records with this context, and forwards the structured JSON logs to downstream storage systems.

#### Q5: What is the difference between HPA and VPA, and can they be used together?
* **Answer:** The Horizontal Pod Autoscaler (HPA) scales applications out by adding or removing pod replicas. The Vertical Pod Autoscaler (VPA) scales applications up or down by adjusting the CPU and memory limits of existing pods. They should not be used together on the same resource metrics (like CPU or memory), as their scaling logic will conflict, leading to unstable scaling behavior. However, you can combine them if the HPA is configured to scale based on custom metrics (like request rates) while the VPA manages CPU and memory allocations."""
    }
]