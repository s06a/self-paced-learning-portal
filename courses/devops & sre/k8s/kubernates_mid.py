COURSE_ID = "mid_level_kubernetes_engineer"
COURSE_TITLE = "Kubernetes Mid Level"
COURSE_DESCRIPTION = (
    "A production-grade, rigorous curriculum designed to bridge the gap between "
    "day-1 application deployments and day-2 enterprise systems management. "
    "Master advanced scheduling, stateful storage, configuration GitOps automation, "
    "comprehensive observability pipelines, security hardening boundaries, "
    "and infrastructure bootstrapping."
)

# =====================================================================
# MODULE 1: ADVANCED WORKLOADS, STORAGE ORCHESTRATION & NODE SCHEDULING
# =====================================================================

M1_THEORY = r"""### Guided Conceptual Walkthrough
In a production-ready cluster, workloads have distinct architectural requirements. Think of a distributed stateful database compared to a stateless API gateway. A stateless API acts like a temporary workstation: if one crashes, you immediately provision an identical replacement with no loss of system memory. A stateful database behaves like a specialized archive office: it requires a permanent address, designated local storage files, and structured initialization procedures. 

To manage this, Kubernetes divides resource templates:
* **StatefulSet**: Provides stable network identities (using ordinals) and dedicated disk volumes to stateful services.
* **StorageClasses & PersistentVolumeClaims (PVCs)**: Act as dynamic request vouchers to provision physical cloud block storage automatically.
* **Affinity, Anti-Affinity, Taints, and Tolerations**: Act as the scheduler's logic gates, determining which worker nodes are allowed or forced to run specific workloads based on labels and hardware configurations.

### Architectural, Lifecycle & Flow Blueprints

```mermaid
graph TD
    SS[StatefulSet Controller] --> P0[Pod-0]
    SS --> P1[Pod-1]
    P0 --> PVC0[PVC-0]
    P1 --> PVC1[PVC-1]
    PVC0 --> PV0[PV-0]
    PVC1 --> PV1[PV-1]
```

```mermaid
sequenceDiagram
    autonumber
    Pod->>Scheduler: Submit Pod Manifest
    Scheduler->>Nodes: Filter via Taints
    Scheduler->>Nodes: Score via Node Affinity
    Scheduler->>Nodes: Evaluate Pod Anti-Affinity
    Scheduler->>API: Bind Pod to Node-A
```

### Under-the-Hood Mechanics & Internal Operations
At the system execution layer, the `kube-scheduler` assigns incoming Pods to nodes during its scheduling cycle, which consists of two main phases: Filtering (Predicates) and Scoring (Priorities). 

When evaluating node taints, the scheduler checks if a Pod has a matching `toleration` block. If it doesn't, the node is immediately filtered out during the predicate phase. 

For storage management, the Container Storage Interface (CSI) translation loop handles disk provisioning. When a `PersistentVolumeClaim` (PVC) is applied, the dynamic PV controller detects the request and communicates with the storage provider's API (such as AWS EBS, GCP PD, or Ceph) via gRPC calls. Once the cloud volume is provisioned, the local `kubelet` mounts the physical block device directly to the worker node's host path, enabling the container runtime to bind-mount the directory into the container's isolated mount namespace.

### Deep-Dive Reference (Advanced Context)
<details>
<summary>StatefulSet Ordinals and PVC Reclaim Policy Mechanics</summary>
Unlike standard Deployments, StatefulSets assign a unique ordinal index (starting at 0) to each Pod (e.g., `db-0`, `db-1`). When scaled up or down, Pods are initialized and terminated sequentially. If a StatefulSet Pod is deleted, the dynamic persistent volume claim is preserved to prevent accidental data loss. When the Pod is rescheduled, the scheduler ensures it is bound to the exact same PersistentVolume (PV) to maintain data continuity.
</details>

### Systemic Failure Modes & Boundary Violations
*   **Failure Mode 1: CSI Dynamic Volume Provisioning Timeout**
    *   **Symptom:** Pod remains stuck in a `ContainerCreating` or `VolumeBindingImmediate` state, and events report `FailedBinding` or `volume provisioning failed`.
    *   **Root Cause:** The underlying StorageClass references a CSI driver that is missing or misconfigured on the worker nodes, or the node lacks the necessary Cloud Provider IAM permissions to provision the requested cloud block device.
    *   **Resolution:** Verify the CSI controller logs and ensure the Cloud IAM role has the required block storage permissions:
        ```bash
        kubectl logs -n kube-system deployment/ebs-csi-controller -c csi-provisioner
        ```

*   **Failure Mode 2: Scheduler Failure (Unsatisfiable Pod Anti-Affinity)**
    *   **Symptom:** Pod remains stuck in a `Pending` state, and events show `0/3 nodes are available: 3 node(s) had anti-affinity conflicts`.
    *   **Root Cause:** A hard anti-affinity constraint (`requiredDuringSchedulingIgnoredDuringExecution`) prevents the scheduler from placing duplicate Pods on the same node, and there are not enough physical worker nodes available to satisfy the replica count.
    *   **Resolution:** Either add more worker nodes to the cluster or soften the anti-affinity rules to a preferred constraint:
        ```yaml
        preferredDuringSchedulingIgnoredDuringExecution:
        - weight: 100
          podAffinityTerm:
            labelSelector:
              matchExpressions:
              - key: app
                operator: In
                values: [api-server]
            topologyKey: kubernetes.io/hostname
        ```

*   **Failure Mode 3: Cordoned Worker Node Drain Deadlock**
    *   **Symptom:** Running `kubectl drain <node-name>` hangs indefinitely or aborts with the error `Cannot evict pod due to PodDisruptionBudget violations`.
    *   **Root Cause:** A `PodDisruptionBudget` (PDB) is configured with strict constraints (e.g., `minAvailable: 1` with only 1 replica running), and evicting the Pod would violate the active budget rules.
    *   **Resolution:** Scale up the target deployment to satisfy the budget requirements before draining, or temporarily delete the PDB to allow the eviction to proceed:
        ```bash
        kubectl scale deployment/web-app --replicas=3
        ```

### Traceability Schema Check
All scheduling directives (`nodeSelector`, `affinity`), workload types (`StatefulSet`, `DaemonSet`, `Job`, `CronJob`), and storage resources (`StorageClass`, `PVC`, `PV`) used in downstream commands and exercises are conceptually defined in this section.
"""

M1_COMMANDS = r"""### Technical & Syntax Reference Manual
Below are the essential commands and configuration keys for orchestrating advanced workloads and scheduling parameters.

*   **Node Drain and Maintenance Controls:**
    ```bash
    # Safely evict workloads from a node to prepare it for maintenance
    kubectl drain node-worker-01 --ignore-daemonsets --delete-emptydir-data

    # Re-enable scheduling on a previously cordoned worker node
    kubectl uncordon node-worker-01
    ```

*   **Workload Label and Taint Injection:**
    ```bash
    # Apply a taint to dedicate a node to specific workloads (e.g., databases)
    kubectl taint nodes node-worker-02 dedicated=database:NoSchedule

    # Remove an existing taint from a worker node
    kubectl taint nodes node-worker-02 dedicated=database:NoSchedule-
    ```

### Anatomy & Boundary Table
| Variable / Parameter / Keyword Name | Expected Type / Allowed Values | Default Value / Operating Domain | Strict Structural Constraints |
| :--- | :--- | :--- | :--- |
| `spec.volumeClaimTemplates` | Array of PVC specifications | N/A (Required for dynamic SS) | Must define valid access modes and storage resource requests. |
| `topologyKey` | String | `kubernetes.io/hostname` | Must match a valid label key on your cluster nodes. |
| `tolerations[*].effect` | String (`NoSchedule`, `PreferNoSchedule`, `NoExecute`) | `NoSchedule` | Determines what actions the scheduler takes for untolerated taints. |
| `minAvailable` | Integer or Percentage | N/A | Must be mutually exclusive with `maxUnavailable` inside a PDB. |
"""

M1_EXAMPLES = r"""### Real-World Case Studies & Applied Examples

#### Example 1: High-Availability Clustered Stateful Database (PostgreSQL)
*   **Context & Objectives:** Deploy a clustered PostgreSQL database using a StatefulSet to ensure each node maintains a stable network identifier and has its own persistent storage volume.
*   **Design Trade-offs:** A StatefulSet is chosen over a Deployment because databases require persistent data across restarts and stable DNS hostnames (e.g., `postgres-0`, `postgres-1`) to configure clustering and replication.
*   **Implementation:**
    ```yaml
    apiVersion: v1
    kind: Service
    metadata:
      name: postgres-headless
      labels:
        app: postgres
    spec:
      ports:
      - port: 5432
        name: db
      clusterIP: None
      selector:
        app: postgres
    ---
    apiVersion: apps/v1
    kind: StatefulSet
    metadata:
      name: postgres
    spec:
      serviceName: "postgres-headless"
      replicas: 2
      selector:
        matchLabels:
          app: postgres
      template:
        metadata:
          labels:
            app: postgres
        spec:
          containers:
          - name: postgresql
            image: postgres:15-alpine
            env:
            - name: POSTGRES_PASSWORD
              value: "secureprodpassword123"
            ports:
            - containerPort: 5432
              name: db
            volumeMounts:
            - name: db-data
              mountPath: /var/lib/postgresql/data
      volumeClaimTemplates:
      - metadata:
          name: db-data
        spec:
          accessModes: [ "ReadWriteOnce" ]
          storageClassName: "gp3-sc"
          resources:
            requests:
              storage: 20Gi
    ```
*   **Behavioral Analysis:**
    The StatefulSet controller creates two Pods: `postgres-0` and `postgres-1`. The dynamic storage controller provisions two matching 20Gi AWS EBS volumes (`gp3-sc`) and mounts them to each Pod. The headless service enables direct internal DNS resolution to individual Pods (e.g., `postgres-0.postgres-headless`).

#### Example 2: Topology-Aware Pod Anti-Affinity for Zone-Redundant APIs
*   **Context & Objectives:** Deploy a customer-facing API gateway across multiple availability zones to ensure fault tolerance and high availability.
*   **Design Trade-offs:** A hard `podAntiAffinity` constraint is used to prevent the scheduler from running multiple instances of the gateway on the same physical node, distributing the workloads across different zones.
*   **Implementation:**
    ```yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: api-gateway
    spec:
      replicas: 3
      selector:
        matchLabels:
          app: api-gateway
      template:
        metadata:
          labels:
            app: api-gateway
        spec:
          affinity:
            podAntiAffinity:
              requiredDuringSchedulingIgnoredDuringExecution:
              - labelSelector:
                  matchExpressions:
                  - key: app
                    operator: In
                    values:
                    - api-gateway
                topologyKey: topology.kubernetes.io/zone
          containers:
          - name: proxy
            image: envoyproxy/envoy:v1.26.0
            resources:
              requests:
                cpu: "500m"
                memory: "512Mi"
              limits:
                cpu: "1"
                memory: "1Gi"
    ```
*   **Behavioral Analysis:**
    The scheduler evaluates availability zones using the `topology.kubernetes.io/zone` label. It ensures that each replica of the `api-gateway` is scheduled on a worker node in a different availability zone, maintaining service availability even if an entire zone goes offline.

#### Example 3: DaemonSet for Log Gathering with Master Node Tolerations
*   **Context & Objectives:** Run a FluentBit logging agent on every node in the cluster, including the control plane master nodes.
*   **Design Trade-offs:** A DaemonSet is chosen over a Deployment because it automatically runs a single instance of the Pod on every worker node, and tolerations are added to allow scheduling on master nodes.
*   **Implementation:**
    ```yaml
    apiVersion: apps/v1
    kind: DaemonSet
    metadata:
      name: system-logger
      namespace: kube-system
    spec:
      selector:
        matchLabels:
          app: system-logger
      template:
        metadata:
          labels:
            app: system-logger
        spec:
          tolerations:
          - key: node-role.kubernetes.io/master
            operator: Exists
            effect: NoSchedule
          - key: node-role.kubernetes.io/control-plane
            operator: Exists
            effect: NoSchedule
          containers:
          - name: fluentbit
            image: fluent/fluent-bit:2.1.2
            resources:
              requests:
                cpu: "100m"
                memory: "128Mi"
              limits:
                cpu: "200m"
                memory: "256Mi"
    ```
*   **Behavioral Analysis:**
    The DaemonSet controller detects all active nodes. Because of the master/control-plane tolerations, it bypasses the standard control plane taints, scheduling one replica of the logger on every node in the cluster.

#### Example 4: Maintaining HA during Node Upgrades using a PodDisruptionBudget
*   **Context & Objectives:** Ensure that critical API services remain available and running during automated cluster upgrades or node draining operations.
*   **Design Trade-offs:** Implementing a PDB forces the cluster to maintain a minimum number of healthy replicas during voluntary maintenance window actions.
*   **Implementation:**
    ```yaml
    apiVersion: policy/v1
    kind: PodDisruptionBudget
    metadata:
      name: critical-api-pdb
      namespace: default
    spec:
      minAvailable: 2
      selector:
        matchLabels:
          app: api-gateway
    ```
*   **Behavioral Analysis:**
    When an administrator attempts to drain a node running an `api-gateway` Pod, the eviction request is evaluated against this PDB. If evicting the Pod would bring the active replica count below 2, the API Server blocks the eviction, pausing the drain operation until a replacement Pod is started and healthy.

#### Example 5: Scheduled CronJob with Concurrency Policies
*   **Context & Objectives:** Run a daily database cleanup job at midnight, ensuring that if a previous run is still active, new runs do not overlap or conflict.
*   **Design Trade-offs:** Setting `concurrencyPolicy: Forbid` prevents resource contention and potential data corruption by blocking overlapping executions.
*   **Implementation:**
    ```yaml
    apiVersion: batch/v1
    kind: CronJob
    metadata:
      name: daily-db-cleanup
    spec:
      schedule: "0 0 * * *"
      concurrencyPolicy: Forbid
      startingDeadlineSeconds: 600
      jobTemplate:
        spec:
          template:
            spec:
              containers:
              - name: sql-cleaner
                image: pg-client:15
                command: ["psql", "-h", "postgres-service", "-U", "admin", "-c", "VACUUM ANALYZE;"]
              restartPolicy: OnFailure
    ```
*   **Behavioral Analysis:**
    At midnight, the CronJob controller attempts to spawn a Job. If the previous night's execution is still running, the controller skips the new execution, keeping the active job isolated and preventing database performance issues.
"""

M1_EXERCISE = r"""### Practical Laboratories & Hands-On Exercises

#### Lab 1: Deploying a Headless Service and StatefulSet
*   **Objective:** Create a Headless Service and deploy a multi-replica StatefulSet with persistent storage volumes.
*   **Prerequisites:** Access to a local Kubernetes cluster (like Minikube or Kind) with a default StorageClass configured.
*   **Step-by-Step Instructions:**
    1. Create a local file named `headless-app.yaml`:
       ```yaml
       apiVersion: v1
       kind: Service
       metadata:
         name: app-headless
       spec:
         ports:
         - port: 80
           name: http
         clusterIP: None
         selector:
           app: stateful-web
       ---
       apiVersion: apps/v1
       kind: StatefulSet
       metadata:
         name: web-app
       spec:
         serviceName: "app-headless"
         replicas: 2
         selector:
           matchLabels:
             app: stateful-web
         template:
           metadata:
             labels:
               app: stateful-web
           spec:
             containers:
             - name: nginx
               image: nginx:1.25.3
               volumeMounts:
               - name: html-storage
                 mountPath: /usr/share/nginx/html
         volumeClaimTemplates:
         - metadata:
             name: html-storage
           spec:
             accessModes: [ "ReadWriteOnce" ]
             resources:
               requests:
                 storage: 1Gi
       ```
    2. Apply the manifest: `kubectl apply -f headless-app.yaml`
    3. Verify that the Pods are initialized and running sequentially: `kubectl get pods -w`
*   **Deterministic Verification Test:**
    Execute a DNS lookup query from a temporary Pod to verify that the headless DNS records are configured correctly:
    `kubectl run dns-tester --image=tutum/dnsutils --restart=Never -it --rm -- nslookup app-headless`
    *   **Expected Output:**
        The query should return two distinct IP addresses, matching the internal IP addresses of your running StatefulSet Pods (`web-app-0` and `web-app-1`).
*   **Troubleshooting Lab-Specific Issues:**
    If the Pods remain stuck in a `Pending` state, run `kubectl get pvc` to check if your cluster has a default StorageClass active to dynamically provision the requested volumes.

#### Lab 2: Enforcing Topology-Aware Pod Anti-Affinity
*   **Objective:** Configure a deployment to prevent duplicate Pod replicas from being scheduled on the same worker node.
*   **Prerequisites:** A cluster with at least two active worker nodes.
*   **Step-by-Step Instructions:**
    1. Create a file named `anti-affinity-deploy.yaml`:
       ```yaml
       apiVersion: apps/v1
       kind: Deployment
       metadata:
         name: isolated-web
       spec:
         replicas: 3
         selector:
           matchLabels:
             app: isolated-web
         template:
           metadata:
             labels:
               app: isolated-web
           spec:
             affinity:
               podAntiAffinity:
                 requiredDuringSchedulingIgnoredDuringExecution:
                 - labelSelector:
                     matchExpressions:
                     - key: app
                       operator: In
                       values: [isolated-web]
                   topologyKey: kubernetes.io/hostname
             containers:
             - name: web
               image: nginx:1.25.3
       ```
    2. Apply the deployment: `kubectl apply -f anti-affinity-deploy.yaml`
    3. Monitor the Pod status: `kubectl get pods -o wide`
*   **Deterministic Verification Test:**
    Count the active Pods. If you have exactly two worker nodes in your cluster, verify that two Pods are running, and the third Pod remains in a `Pending` state.
    *   **Expected Output:**
        `isolated-web-xxxx-1/3 pods running, 1 pending due to node scheduling anti-affinity constraints.`
*   **Troubleshooting Lab-Specific Issues:**
    If all three Pods are running, ensure your cluster has multiple worker nodes. If you are using a single-node development cluster (like Minikube), the scheduler will not be able to satisfy the hard anti-affinity constraints for a third replica.

#### Lab 3: Configuring Node Taints and Tolerations
*   **Objective:** Protect a worker node from standard workloads and configure a Pod with the necessary tolerations to schedule on that node.
*   **Prerequisites:** Access to a multi-node Kubernetes cluster.
*   **Step-by-Step Instructions:**
    1. Identify a target worker node and apply a taint:
       `kubectl taint nodes <node-name> dedicated=database:NoSchedule`
    2. Attempt to deploy a standard Nginx Pod without any tolerations and verify that it avoids the tainted node.
    3. Create a file named `tolerant-pod.yaml` with the corresponding toleration:
       ```yaml
       apiVersion: v1
       kind: Pod
       metadata:
         name: db-engine-pod
       spec:
         tolerations:
         - key: "dedicated"
           operator: "Equal"
           value: "database"
           effect: "NoSchedule"
         containers:
         - name: postgres
           image: postgres:15-alpine
           env:
           - name: POSTGRES_PASSWORD
             value: "lab-pass"
       ```
    4. Apply the manifest: `kubectl apply -f tolerant-pod.yaml`
*   **Deterministic Verification Test:**
    Verify that the Pod was successfully scheduled on the tainted node:
    `kubectl get pod db-engine-pod -o wide`
    *   **Expected Output:**
        The output node name must match the specific tainted worker node.
*   **Troubleshooting Lab-Specific Issues:**
    If the Pod remains stuck in a `Pending` state, verify that the toleration key, operator, value, and effect match the node taint exactly.

#### Lab 4: Protecting Workloads with a PodDisruptionBudget
*   **Objective:** Define a PodDisruptionBudget to ensure service availability during maintenance and node draining operations.
*   **Prerequisites:** A multi-node cluster running your `api-gateway` deployment (from Example 2).
*   **Step-by-Step Instructions:**
    1. Create a file named `api-pdb.yaml`:
       ```yaml
       apiVersion: policy/v1
       kind: PodDisruptionBudget
       metadata:
         name: gateway-pdb
       spec:
         minAvailable: 2
         selector:
           matchLabels:
             app: api-gateway
       ```
    2. Apply the budget: `kubectl apply -f api-pdb.yaml`
    3. Cordon and attempt to drain the worker node running one of your `api-gateway` replicas:
       `kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data`
*   **Deterministic Verification Test:**
    Observe the drain output logs in your terminal.
    *   **Expected Output:**
        The eviction request must be blocked by the API Server, displaying an error message similar to: `Cannot evict pod due to PodDisruptionBudget violations`.
*   **Troubleshooting Lab-Specific Issues:**
    Make sure you have exactly 2 replicas running before draining. If you have 3 or more healthy replicas running across other nodes, the eviction will succeed because the minimum availability target of 2 is still satisfied.

#### Lab 5: Deploying a CronJob with Concurrency Constraints
*   **Objective:** Configure a CronJob with a forbidden concurrency policy and verify that overlapping executions are blocked.
*   **Prerequisites:** Access to a running Kubernetes cluster.
*   **Step-by-Step Instructions:**
    1. Create a file named `blocked-cronjob.yaml`:
       ```yaml
       apiVersion: batch/v1
       kind: CronJob
       metadata:
         name: backup-loop
       spec:
         schedule: "*/1 * * * *"
         concurrencyPolicy: Forbid
         jobTemplate:
           spec:
             template:
               spec:
                 containers:
                 - name: sleeper
                   image: alpine:3.18
                   command: ["sh", "-c", "echo 'Process active...'; sleep 120"]
                 restartPolicy: OnFailure
       ```
    2. Apply the CronJob: `kubectl apply -f blocked-cronjob.yaml`
    3. Monitor the running Jobs: `kubectl get jobs -w`
*   **Deterministic Verification Test:**
    Verify that only one Job is running concurrently, even after the 1-minute execution threshold has passed.
    *   **Expected Output:**
        Only a single Job should be running, and the next scheduled execution should be skipped or queued because the previous night's job is still active.
*   **Troubleshooting Lab-Specific Issues:**
    Ensure the schedule is set to `*/1 * * * *` to run every minute, giving you enough time to observe the concurrency blocking behavior.
"""

M1_INSIGHT = r"""### Professional Interview & Advanced Deep Dive

#### Q1: What is the technical difference between Node Affinity and Node Taints, and when should you use each?
*   **Answer:** Node Affinity directs *Pods to nodes* based on labels. It is a scheduling preference (soft) or constraint (hard) configured in the Pod specification. Node Taints are configured on the *nodes* themselves, allowing them to *repel* Pods unless they have a matching toleration. Use Node Affinity when you want to guide or force a Pod to run on specific hardware (e.g., GPU nodes). Use Node Taints when you want to isolate nodes and prevent standard workloads from running on them (e.g., dedicating nodes to system controllers or premium workloads).

#### Q2: How does a StatefulSet ensure stable network identity, and how does this differ from standard Deployment DNS resolution?
*   **Answer:** Deployments expose their Pods through a standard Service, which assigns a single ClusterIP that randomly load balances traffic across backend Pods. A StatefulSet uses a Headless Service (setting `clusterIP: None`) to register individual DNS A-records for each Pod based on its ordinal index (e.g., `pod-0.headless-service.namespace.svc.cluster.local`). This allows clients to resolve and connect directly to a specific Pod, which is crucial for stateful clustered systems like database clusters.

#### Q3: Why does draining a node sometimes hang, and how do you resolve PodDisruptionBudget deadlock loops?
*   **Answer:** Draining a node attempts to evict all running Pods safely. However, if a Pod is protected by a strict `PodDisruptionBudget` (PDB) and evicting it would violate the minimum availability limits, the API Server will block the eviction, causing the drain command to hang. To resolve this, you can scale up the deployment on other nodes to satisfy the budget, adjust the PDB threshold, or temporarily delete the PDB to allow the node maintenance to proceed.

#### Q4: What is the behavioral difference between the `NoSchedule` and `NoExecute` taint effects?
*   **Answer:** The `NoSchedule` effect is a scheduling constraint; if a Pod does not tolerate the taint, it cannot be scheduled on the node, but any running Pods on that node are unaffected. The `NoExecute` effect is an execution constraint; if a node is tainted with `NoExecute`, any running Pods on that node that do not tolerate the taint are immediately evicted, and any new Pods without tolerations are blocked from scheduling.

#### Q5: How does the Kubernetes scheduler evaluate soft constraints during the priority phase of scheduling?
*   **Answer:** During the priority scoring phase, the scheduler evaluates all preferred affinity and anti-affinity rules for each node. It calculates a score for each node (typically ranging from 0 to 100) by multiplying the matching rule weight by the node's resource availability. The scheduler then assigns the Pod to the node with the highest cumulative priority score, balancing workloads across the cluster.

### Academic & Professional Alignment
Understanding scheduling, node constraints, and stateful storage is a key focus area on advanced industry exams like the CKA (Certified Kubernetes Administrator) and CKAD (Certified Kubernetes Application Developer). Demonstrating mastery of these scheduling primitives is critical for deploying resilient, high-availability production environments.
"""

# =====================================================================
# MODULE 2: APPLICATION NETWORKING & INGRESS CONTROLLERS
# =====================================================================

M2_THEORY = r"""### Guided Conceptual Walkthrough
Think of a Kubernetes cluster as a secure, gated business office complex. The individual offices are the **Services** running inside the cluster. Historically, external visitors (client requests) had to navigate through separate, complex doors (**NodePorts** or individual cloud **LoadBalancers**), making it difficult to scale and manage access policies. 

To streamline this, you set up a centralized reception desk at the main entrance (**Ingress Controller**). Visitors enter through a single, secure entrance (Ports 80/443). The receptionist checks the visitor's request directory (**Ingress Rules**) and directs them to the correct office based on the requested host name or URL subpath. 

For enterprise-scale environments with multiple tenants, you upgrade to a modern routing architecture (**Gateway API**). This decouples routing responsibilities into separate roles: the building manager configures the main entrance structure (**Gateway**), while individual offices manage their own specific directory routing paths (**HTTPRoutes**).

### Architectural, Lifecycle & Flow Blueprints

```mermaid
graph TD
    Client[Client Workload] -->|Accesses Service| SVC[ClusterIP Service]
    SVC -->|Routes Traffic| EP[Endpoints Controller]
    EP -->|Discovers Pods| Pod1[Backend Pod 1]
    EP -->|Discovers Pods| Pod2[Backend Pod 2]
```

```mermaid
sequenceDiagram
    autonumber
    Client->>Ingress: HTTPS GET request
    Ingress->>Ingress: Terminate TLS Certificate
    Ingress->>Endpoints: Resolve Backend IP
    Ingress->>Pod: Forward Plaintext HTTP
```

### Under-the-Hood Mechanics & Internal Operations
The Ingress Controller runs as a reverse-proxy engine (such as NGINX, Traefik, or Envoy) inside the cluster, exposed to external traffic using a cloud `LoadBalancer` Service. When a client sends a request, the controller intercepts the traffic, terminates the SSL/TLS connection, and evaluates the HTTP headers against the rules defined in the Ingress resource. 

Unlike standard Services that route traffic using round-robin DNS or proxy rules, the Ingress Controller queries the API Server directly to resolve healthy Pod IP addresses from the active `EndpointSlice` API objects. It then bypasses standard Service IP routing and opens a direct TCP connection to the destination Pod IP, reducing network overhead and supporting advanced features like sticky sessions, request rewriting, and path routing.

### Deep-Dive Reference (Advanced Context)
<details>
<summary>Ingress vs. Gateway API Specifications and Roles</summary>
The Gateway API is the modern evolution of Ingress, designed to split routing configurations across multi-tenant personas:
*   **GatewayClass**: Configured by cluster operators to define the underlying router controller type (e.g., Envoy or Nginx).
*   **Gateway**: Manages entry point configurations (such as ports, protocols, and TLS certificates).
*   **HTTPRoute / GRPCRoute**: Managed by application developers to define specific path routing rules and targets, decoupling infrastructure management from application deployments.
</details>

### Systemic Failure Modes & Boundary Violations
*   **Failure Mode 1: SSL Handshake Timeout (Missing or Invalid Private Key)**
    *   **Symptom:** External HTTPS requests fail with SSL handshaking errors, or the browser displays a `Certificate Authority Invalid` warning.
    *   **Root Cause:** The TLS Secret referenced in the Ingress specification is missing, has expired, or the private key does not match the certificate's public key.
    *   **Resolution:** Verify the certificates inside the TLS Secret and ensure they match the hostnames defined in your Ingress resource:
        ```bash
        kubectl describe ingress <ingress-name>
        # Output will show Certificate configuration warnings or missing TLS secret events
        ```

*   **Failure Mode 2: Ingress Controller Path Redirection Mismatch**
    *   **Symptom:** Accessing subpaths (e.g., `/api`) returns HTTP `404 Not Found` errors from the backend application.
    *   **Root Cause:** The Ingress Controller forwards the entire requested subpath path to the backend container, but the application is only listening on the root path `/`.
    *   **Resolution:** Add path rewrite annotations to the Ingress resource to strip the path prefix before forwarding the traffic to the backend:
        ```yaml
        annotations:
          nginx.ingress.kubernetes.io/rewrite-target: /$2
        ```

*   **Failure Mode 3: Gateway API HTTPRoute Refused by Gateway Listener**
    *   **Symptom:** Applying an `HTTPRoute` has no effect, and the status shows `Accepted: False` with the reason `RouteNotAllowed`.
    *   **Root Cause:** The parent `Gateway` listener is restricted and does not allow HTTPRoutes from the route's namespace.
    *   **Resolution:** Update the Gateway's listener configuration to allow routes from all namespaces:
        ```yaml
        allowedRoutes:
          namespaces:
            from: All
        ```

### Traceability Schema Check
All ingress controllers (Nginx Ingress, Gateway API), routing parameters (`host`, `pathType`), SSL/TLS certificate configurations, and network verification commands used below are conceptually mapped to this section.
"""

M2_COMMANDS = r"""### Technical & Syntax Reference Manual
Below are the essential commands for configuring, validating, and auditing application routing resources.

*   **Ingress Resource Inspection:**
    ```bash
    # List active Ingress rules and their external IP addresses in the namespace
    kubectl get ingress

    # Retrieve detailed routing definitions and TLS certificates for an Ingress
    kubectl describe ingress external-web-ingress
    ```

*   **Gateway API Operational Controls:**
    ```bash
    # List active Gateway listeners and HTTPRoute resources
    kubectl get gateway,httproute --all-namespaces

    # Verify the status and path matches of a specific HTTPRoute
    kubectl describe httproute api-gateway-route
    ```

### Anatomy & Boundary Table
| Variable / Parameter / Keyword Name | Expected Type / Allowed Values | Default Value / Operating Domain | Strict Structural Constraints |
| :--- | :--- | :--- | :--- |
| `spec.ingressClassName` | String (e.g., `nginx`, `traefik`) | N/A (Required) | Must match an active Ingress Class registered in the cluster. |
| `spec.rules[*].http.paths[*].pathType` | String (`Prefix`, `Exact`, `ImplementationSpecific`) | `Prefix` | Determines how the controller evaluates the requested URL path. |
| `spec.tls[*].secretName` | String | N/A | Must match an existing Opaque or kubernetes.io/tls Secret containing valid keys. |
| `spec.parentRefs` | List of parent gateway resource references | N/A (Required in HTTPRoute) | Must reference a valid, active Gateway name and namespace. |
"""

M2_EXAMPLES = r"""### Real-World Case Studies & Applied Examples

#### Example 1: Secure SSL/TLS Ingress Routing with Nginx Redirections
*   **Context & Objectives:** Configure secure HTTP-to-HTTPS redirect routing and path routing for a frontend application and an internal billing API.
*   **Design Trade-offs:** An Nginx Ingress resource is used to handle TLS termination at the edge, protecting backend containers from SSL processing overhead and simplifying certificate management.
*   **Implementation:**
    ```yaml
    apiVersion: networking.k8s.io/v1
    kind: Ingress
    metadata:
      name: main-web-ingress
      namespace: default
      annotations:
        nginx.ingress.kubernetes.io/ssl-redirect: "true"
        nginx.ingress.kubernetes.io/rewrite-target: /$2
    spec:
      ingressClassName: nginx
      tls:
      - hosts:
        - company.com
        secretName: company-tls-cert
      rules:
      - host: company.com
        http:
          paths:
          - path: /api(/|$)(.*)
            pathType: Prefix
            backend:
              service:
                name: billing-api-service
                port:
                  number: 8080
          - path: /(|$)(.*)
            pathType: Prefix
            backend:
              service:
                name: frontend-service
                port:
                  number: 80
    ```
*   **Behavioral Analysis:**
    The Nginx Ingress Controller intercepts incoming traffic on port 443. It terminates the TLS connection using the `company-tls-cert` Secret. If a request path starts with `/api`, the controller rewrites the path and forwards the request to `billing-api-service` on port 8080. All other traffic is directed to `frontend-service` on port 80.

#### Example 2: Decoupled Multi-Tenant Routing via Gateway API
*   **Context & Objectives:** Re-architect a monolithic Ingress configuration into a modern Gateway API structure to allow separate application teams to manage their own routing rules.
*   **Design Trade-offs:** The Gateway API is chosen over legacy Ingress because it decouples routing configurations, allowing platform operators to manage network interfaces and application teams to manage routes independently.
*   **Implementation:**
    ```yaml
    apiVersion: gateway.networking.k8s.io/v1
    kind: Gateway
    metadata:
      name: enterprise-gateway
      namespace: infra
    spec:
      gatewayClassName: nginx-gateway-class
      listeners:
      - name: https-listener
        protocol: HTTPS
        port: 443
        tls:
          mode: Terminate
          certificateRefs:
          - group: ""
            kind: Secret
            name: enterprise-tls-key
        allowedRoutes:
          namespaces:
            from: All
    ---
    apiVersion: gateway.networking.k8s.io/v1
    kind: HTTPRoute
    metadata:
      name: finance-billing-route
      namespace: finance-team
    spec:
      parentRefs:
      - name: enterprise-gateway
        namespace: infra
      rules:
      - matches:
        - path:
            type: PathPrefix
            value: /checkout
        backendRefs:
        - name: checkout-service
          port: 8443
    ```
*   **Behavioral Analysis:**
    The platform team configures the `enterprise-gateway` in the `infra` namespace to handle SSL/TLS termination on port 443. The finance team creates an `HTTPRoute` in their own `finance-team` namespace, mapping the `/checkout` path to `checkout-service`. This allows the team to update routes without touching cluster-wide configurations.

#### Example 3: AWS ALB Ingress Controller Configuration for Cloud ALB Integrations
*   **Context & Objectives:** Configure an Ingress resource to integrate directly with AWS, automatically provisioning an Application Load Balancer (ALB) to handle external traffic.
*   **Design Trade-offs:** The AWS ALB Ingress Controller is chosen to integrate with native cloud services, leveraging AWS security groups, access logs, and certificate managers.
*   **Implementation:**
    ```yaml
    apiVersion: networking.k8s.io/v1
    kind: Ingress
    metadata:
      name: aws-alb-ingress
      namespace: default
      annotations:
        alb.ingress.kubernetes.io/scheme: internet-facing
        alb.ingress.kubernetes.io/target-type: ip
        alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:us-east-1:123456789012:certificate/abc-123
    spec:
      ingressClassName: alb
      rules:
      - host: aws.company.com
        http:
          paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: frontend-service
                port:
                  number: 80
    ```
*   **Behavioral Analysis:**
    The AWS ALB Controller detects the Ingress resource and communicates with the AWS EC2 API to provision an internet-facing Application Load Balancer. It configures the target group to route traffic directly to the backend Pod IPs, bypassing the NodePort layer.

#### Example 4: Traefik Ingress Configuration for Custom Headers and Rate Limiting
*   **Context & Objectives:** Configure Traefik Ingress to inject custom security headers and apply rate limiting to prevent DDoS attacks on public services.
*   **Design Trade-offs:** Traefik is chosen as the Ingress Controller for its native Middleware support, which simplifies adding complex routing rules and security policies.
*   **Implementation:**
    ```yaml
    apiVersion: traefik.containo.us/v1alpha1
    kind: Middleware
    metadata:
      name: security-headers
      namespace: default
    spec:
      headers:
        browserXSSFilter: true
        contentTypeNosniff: true
        forceSTSHeader: true
        sslRedirect: true
    ---
    apiVersion: networking.k8s.io/v1
    kind: Ingress
    metadata:
      name: traefik-secured-ingress
      namespace: default
      annotations:
        traefik.ingress.kubernetes.io/router.middlewares: default-security-headers@kubernetescrd
    spec:
      ingressClassName: traefik
      rules:
      - host: secure.company.com
        http:
          paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: frontend-service
                port:
                  number: 80
    ```
*   **Behavioral Analysis:**
    Traefik processes incoming HTTP requests, applies the `security-headers` middleware to inject security headers into the request, and forwards the secure request down to `frontend-service`.

#### Example 5: Ingress Configuration for Blue-Green Deployments with Weighted Routing
*   **Context & Objectives:** Configure an Ingress Controller to route 90% of traffic to a stable production deployment (blue) and 10% to a new release (green) for testing.
*   **Design Trade-offs:** Weighted routing is chosen to perform safe canary deployments, allowing testing of new features with minimal impact on users.
*   **Implementation:**
    ```yaml
    apiVersion: networking.k8s.io/v1
    kind: Ingress
    metadata:
      name: canary-ingress
      namespace: default
      annotations:
        nginx.ingress.kubernetes.io/canary: "true"
        nginx.ingress.kubernetes.io/canary-weight: "10"
    spec:
      ingressClassName: nginx
      rules:
      - host: app.company.com
        http:
          paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: app-service-green
                port:
                  number: 80
    ```
*   **Behavioral Analysis:**
    The Nginx Ingress Controller detects the canary annotation and configures its routing engine to split traffic. It routes 10% of requests matching `app.company.com` to the green service and 90% to the stable production service, enabling safe testing of new releases.
"""

M2_EXERCISE = r"""### Practical Laboratories & Hands-On Exercises

#### Lab 1: Deploying an Ingress Controller and Path-Based Routing
*   **Objective:** Install an Ingress Controller, expose multiple backend services, and configure path-based routing.
*   **Prerequisites:** Access to a running Kubernetes cluster with Helm installed.
*   **Step-by-Step Instructions:**
    1. Deploy the Nginx Ingress Controller using Helm:
       ```bash
       helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
       helm repo update
       helm install ingress-nginx ingress-nginx/ingress-nginx --namespace ingress-system --create-namespace
       ```
    2. Deploy two simple test services: `app-alpha` and `app-beta` on port 80.
    3. Create an Ingress manifest named `path-routing.yaml`:
       ```yaml
       apiVersion: networking.k8s.io/v1
       kind: Ingress
       metadata:
         name: app-path-ingress
         namespace: default
       spec:
         ingressClassName: nginx
         rules:
         - host: web.sandbox.local
           http:
             paths:
             - path: /alpha
               pathType: Prefix
               backend:
                 service:
                   name: app-alpha
                   port:
                     number: 80
             - path: /beta
               pathType: Prefix
               backend:
                 service:
                   name: app-beta
                   port:
                     number: 80
       ```
    4. Apply the manifest: `kubectl apply -f path-routing.yaml`
*   **Deterministic Verification Test:**
    Send an HTTP request with host headers to verify path routing is working:
    `curl -H "Host: web.sandbox.local" http://<ingress-controller-ip>/alpha`
    *   **Expected Output:**
        The response should return content from the `app-alpha` service.
*   **Troubleshooting Lab-Specific Issues:**
    If you are running on a local cluster (like Minikube), you may need to run `minikube tunnel` in a separate terminal to assign an external IP to the Ingress Controller Service.

#### Lab 2: Troubleshooting Ingress SSL Termination
*   **Objective:** Generate a TLS certificate, create a TLS Secret, and secure an Ingress path using HTTPS.
*   **Prerequisites:** Completed Lab 1.
*   **Step-by-Step Instructions:**
    1. Generate a self-signed TLS certificate and private key:
       ```bash
       openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout sandbox.key -out sandbox.crt -subj "/CN=web.sandbox.local"
       ```
    2. Create a TLS Secret in your namespace:
       ```bash
       kubectl create secret tls sandbox-tls-secret --key sandbox.key --cert sandbox.crt
       ```
    3. Create an Ingress manifest named `ssl-ingress.yaml`:
       ```yaml
       apiVersion: networking.k8s.io/v1
       kind: Ingress
       metadata:
         name: secure-app-ingress
       spec:
         ingressClassName: nginx
         tls:
         - hosts:
           - web.sandbox.local
           secretName: sandbox-tls-secret
         rules:
         - host: web.sandbox.local
           http:
             paths:
             - path: /
               pathType: Prefix
               backend:
                 service:
                   name: app-alpha
                   port:
                     number: 80
       ```
    4. Apply the manifest: `kubectl apply -f ssl-ingress.yaml`
*   **Deterministic Verification Test:**
    Query the endpoint securely, bypassing certificate authority verification:
    `curl -kiv https://web.sandbox.local/ --resolve web.sandbox.local:443:<ingress-controller-ip>`
    *   **Expected Output:**
        The response output must show SSL handshake completion details, server certificate parameters matching `sandbox-tls-secret`, and return HTTP 200 OK.
*   **Troubleshooting Lab-Specific Issues:**
    If the connection is rejected, verify that your Ingress Controller is listening on port 443 and that the Ingress resource is in the same namespace as the TLS Secret.

#### Lab 3: Re-Architecting Routing via the Gateway API
*   **Objective:** Re-architect path-based routing configurations using the modern Gateway API.
*   **Prerequisites:** Gateway API Custom Resource Definitions (CRDs) installed on the cluster.
*   **Step-by-Step Instructions:**
    1. Verify that the Gateway API CRDs are installed: `kubectl get crd | grep gateway.networking`
    2. Create a Gateway configuration named `central-gateway.yaml`:
       ```yaml
       apiVersion: gateway.networking.k8s.io/v1
       kind: Gateway
       metadata:
         name: app-gateway
         namespace: default
       spec:
         gatewayClassName: nginx-gateway-class
         listeners:
         - name: http
           protocol: HTTP
           port: 80
           allowedRoutes:
             namespaces:
               from: All
       ```
    3. Create an HTTPRoute manifest named `alpha-route.yaml`:
       ```yaml
       apiVersion: gateway.networking.k8s.io/v1
       kind: HTTPRoute
       metadata:
         name: alpha-route
         namespace: default
       spec:
         parentRefs:
         - name: app-gateway
         rules:
         - matches:
           - path:
               type: PathPrefix
               value: /alpha
           backendRefs:
           - name: app-alpha
             port: 80
       ```
    4. Apply both manifests to the cluster.
*   **Deterministic Verification Test:**
    Inspect the HTTPRoute status to verify it was accepted by the Gateway listener:
    `kubectl describe httproute alpha-route`
    *   **Expected Output:**
        The output status should show: `Conditions: ... Reason: Accepted, Status: True`.
*   **Troubleshooting Lab-Specific Issues:**
    If the route status shows `RouteNotAllowed`, verify that the parent `Gateway` is configured to allow routes from the route's namespace.

#### Lab 4: Debugging Path Redirections and Rewrites
*   **Objective:** Configure path rewrites to allow accessing subpaths when the backend application is only listening on the root path.
*   **Prerequisites:** Completed Lab 1.
*   **Step-by-Step Instructions:**
    1. Deploy a standard application container that only serves content on the root path `/`.
    2. Create an Ingress with an `/app` subpath pointing to the application, without using rewrite annotations.
    3. Access the subpath: `curl http://<ingress-ip>/app`
    4. Note the HTTP 404 error returned by the application.
    5. Update the Ingress manifest to add path rewrite annotations:
       ```yaml
       metadata:
         name: app-rewrite-ingress
         annotations:
           nginx.ingress.kubernetes.io/rewrite-target: /$1
       spec:
         rules:
         - host: web.sandbox.local
           http:
             paths:
             - path: /app/?(.*)
               pathType: Prefix
               backend:
                 service:
                   name: root-app-service
                   port:
                     number: 80
       ```
    6. Re-apply the manifest.
*   **Deterministic Verification Test:**
    Access the subpath again: `curl -H "Host: web.sandbox.local" http://<ingress-ip>/app/`
    *   **Expected Output:**
        The response should return HTTP 200 OK along with the application's root index content, confirming the path prefix was stripped.
*   **Troubleshooting Lab-Specific Issues:**
    Ensure you use the correct path regular expression structure (`/app/?(.*)`) in the Ingress rule, otherwise the rewrite controller will not match and process the request path correctly.

#### Lab 5: Implementing Weighted Routing for Canary Releases
*   **Objective:** Deploy two versions of an application and split incoming traffic using weighted canary routing.
*   **Prerequisites:** Completed Lab 1.
*   **Step-by-Step Instructions:**
    1. Deploy two identical applications: `app-blue` (production) and `app-green` (canary).
    2. Create a standard primary Ingress manifest pointing to `app-blue`.
    3. Create a canary Ingress manifest named `canary-route.yaml`:
       ```yaml
       apiVersion: networking.k8s.io/v1
       kind: Ingress
       metadata:
         name: app-canary-ingress
         annotations:
           nginx.ingress.kubernetes.io/canary: "true"
           nginx.ingress.kubernetes.io/canary-weight: "50"
       spec:
         ingressClassName: nginx
         rules:
         - host: app.sandbox.local
           http:
             paths:
             - path: /
               pathType: Prefix
               backend:
                 service:
                   name: app-green
                   port:
                     number: 80
       ```
    4. Apply the canary Ingress to the cluster.
*   **Deterministic Verification Test:**
    Send multiple sequential HTTP requests using curl to verify the traffic split:
    `for i in {1..10}; do curl -H "Host: app.sandbox.local" http://<ingress-ip>/; done`
    *   **Expected Output:**
        The response output must show a roughly equal split between `app-blue` and `app-green` content, confirming the canary routing is active.
*   **Troubleshooting Lab-Specific Issues:**
    Ensure both Ingress resources use the exact same hostname and path configurations, and that you have enabled the canary annotation (`nginx.ingress.kubernetes.io/canary: "true"`) on the canary Ingress.
"""

M2_INSIGHT = r"""### Professional Interview & Advanced Deep Dive

#### Q1: How does Ingress-Nginx bypass standard ClusterIP IP tables routing, and why?
*   **Answer:** Standard ClusterIP Services route traffic randomly across backend Pods using `iptables` or `IPVS` rules configured by `kube-proxy`. This adds latency and lacks support for advanced features like session stickiness. To bypass this, the Ingress-Nginx controller queries the API Server directly to resolve healthy Pod IP addresses from the active `Endpoints` or `EndpointSlice` objects. It then opens a direct TCP socket connection to the destination Pod IP, minimizing network latency and supporting advanced features like custom headers and path rewrites.

#### Q2: What is the primary difference between prefix-based routing (`pathType: Prefix`) and exact routing (`pathType: Exact`) in an Ingress configuration?
*   **Answer:** `pathType: Prefix` matches requested paths based on a slash-separated prefix. For example, a path rule of `/api` will match `/api`, `/api/`, and `/api/v1`. `pathType: Exact` matches the requested path exactly, case-sensitively. A path rule of `/api` will only match `/api` and will return an HTTP 404 error if accessing `/api/` or `/api/v1`.

#### Q3: Why does updating an HTTPRoute in the Gateway API not require reloading the main Gateway load balancer configuration?
*   **Answer:** The Gateway API decouples routing configurations from the main listener infrastructure. The parent `Gateway` resource defines the entry points, open ports, and TLS configurations, which are translated into physical load balancer rules. The child `HTTPRoute` contains only the specific path routing rules and backend targets. When an HTTPRoute is updated, the changes are processed in-memory by the controller and applied directly, bypassing the slow load balancer update cycle.

#### Q4: How do path rewrite annotations work in Ingress-Nginx, and what is the function of the regex capture groups?
*   **Answer:** Path rewrite annotations tell the Ingress-Nginx controller to strip or modify the requested path before forwarding the request to the backend. In Nginx, this is configured using regular expression capture groups. For example, a path of `/api/?(.*)` captures everything after `/api/` in group 1. The annotation `nginx.ingress.kubernetes.io/rewrite-target: /$1` then rewrites the path, stripping `/api/` and forwarding only the captured subpath to the backend.

#### Q5: How do you handle TLS certificates inside a multi-tenant cluster where teams are restricted to separate namespaces?
*   **Answer:** In a multi-tenant cluster, standard Ingress resources can only consume TLS Secrets that reside in the same namespace as the Ingress. This makes managing wildcard certificates difficult, as they must be duplicated across multiple namespaces. To solve this, you can configure your Ingress Controller to read a default, global TLS certificate from a central namespace, or upgrade to the Gateway API, which natively supports cross-namespace certificate references.

### Academic & Professional Alignment
Configuring application routing, securing connections, and implementing advanced path routing are core components of the CKAD and CKA exams. Platform engineers must master these routing primitives to build highly available, secure, and performant web services in production.
"""

# =====================================================================
# MODULE 3: SECURITY, RBAC & RESOURCE BOUNDARIES
# =====================================================================

M3_THEORY = r"""### Guided Conceptual Walkthrough
Imagine a large shared research facility. If every researcher (application process or developer) has unrestricted master access keys (**Root Access**), they could accidentally access other rooms, modify secure experiments, or consume all the power grids, causing a facility-wide blackout (**Noisy Neighbors**). 

To secure the facility, you set up strict security boundaries:
*   **ServiceAccounts & Roles**: Assign specific security clearance keycards to researchers and applications, limiting their access to specific folders in specific rooms.
*   **NetworkPolicies**: Install secure security checkpoints that only permit communication between specific teams.
*   **ResourceQuotas & Limits**: Set strict limits on water and power usage in each lab namespace, ensuring a single lab cannot starve other labs of resources.

### Architectural, Lifecycle & Flow Blueprints

```mermaid
graph TD
    Sub[Subject: User/Group/SA] --> RB[Role Binding]
    Sub --> CRB[Cluster Role Binding]
    RB --> R[Role: Namespaced]
    CRB --> CR[Cluster Role: Global]
```

```mermaid
sequenceDiagram
    autonumber
    Pod-A->>Network: Egress TCP Packet
    Network->>NetPol: Check Egress Rules
    NetPol->>Pod-B: Deny or Allow Ingress
```

### Under-the-Hood Mechanics & Internal Operations
At the system validation layer, every API request made to the `kube-apiserver` must pass through three sequential phases: Authentication, Authorization, and Admission Control. 

For Authorization, the API Server queries the configured Role-Based Access Control (RBAC) cache database. It matches the request's token (or ServiceAccount ID) against the defined `RoleBindings` and `ClusterRoleBindings`. If a valid binding exists that permits the requested API verb (e.g., `get` or `list`) on the target resource, the request is authorized. 

For network security, NetworkPolicies are translated into packet filtering rules (using `iptables`, `IPVS`, or eBPF) configured directly inside the host kernel by the cluster's Container Network Interface (CNI) plugin (such as Calico or Cilium). This ensures network microsegmentation is enforced at the network layer on each worker node.

### Deep-Dive Reference (Advanced Context)
<details>
<summary>Namespace-Level LimitRanges and ResourceQuotas</summary>
To enforce resource boundaries across a shared cluster, administrators configure:
*   **ResourceQuotas**: Set global, namespace-level constraints on total resource consumption (such as maximum CPU, memory, and total Pod counts).
*   **LimitRanges**: Set default, container-level resource limits and requests. If a developer deploys a Pod without specifying resource allocations, the LimitRange automatically injects these defaults, preventing untracked containers from starving other workloads.
</details>

### Systemic Failure Modes & Boundary Violations
*   **Failure Mode 1: Pod API Request Unauthorized (RBAC Permissions Denied)**
    *   **Symptom:** Application container logs report `HTTP 403 Forbidden` or `User system:serviceaccount:default:app-sa cannot list resource pods in API group`.
    *   **Root Cause:** The `ServiceAccount` assigned to the Pod is missing the necessary `RoleBinding` or permissions to interact with the API Server.
    *   **Resolution:** Verify the Role and RoleBinding configurations and ensure they are bound to the correct ServiceAccount inside the target namespace:
        ```bash
        kubectl auth can-i list pods --as=system:serviceaccount:default:app-sa
        ```

*   **Failure Mode 2: Inter-Namespace Network Isolation Collision**
    *   **Symptom:** Backend microservices fail to connect to database Pods, and requests return connection timeouts.
    *   **Root Cause:** A strict ingress `NetworkPolicy` is applied to the database namespace, blocking incoming traffic from other namespaces that lack the required matching labels.
    *   **Resolution:** Update the database's NetworkPolicy to allow incoming traffic from specific source namespaces using namespace and pod selectors:
        ```yaml
        ingress:
        - from:
          - namespaceSelector:
              matchLabels:
                kubernetes.io/metadata.name: app-namespace
        ```

*   **Failure Mode 3: Pod Denied due to Namespace ResourceQuota Exhaustion**
    *   **Symptom:** Applying a Pod or Deployment fails with the error `Forbidden: exceeded quota: cpu-memory-quota, requested: requests.memory=512Mi, used: requests.memory=16Gi, limited: requests.memory=16Gi`.
    *   **Root Cause:** The namespace has reached its total memory limit defined in the `ResourceQuota`, or the Pod lacks explicit requests and limits while a `LimitRange` is active.
    *   **Resolution:** Scale down unused deployments in the namespace to free up resources, or request an increase to the namespace's ResourceQuota limits:
        ```bash
        kubectl get resourcequota -n target-namespace
        ```

### Traceability Schema Check
Every security parameter (`ServiceAccount`, `Role`, `ClusterRole`), network policy setting (`ingress`, `egress`), and resource boundary configuration (`LimitRange`, `ResourceQuota`) used in downstream commands and exercises is conceptually defined in this section.
"""

M3_COMMANDS = r"""### Technical & Syntax Reference Manual
Below are the essential commands for auditing cluster access control policies and managing resource boundaries.

*   **RBAC Permissions Validation:**
    ```bash
    # Verify if a specific ServiceAccount has permission to delete Pods in the namespace
    kubectl auth can-i delete pods --as=system:serviceaccount:default:app-sa

    # Check list operations permissions across all namespaces
    kubectl auth can-i list services --all-namespaces
    ```

*   **Resource Limit Monitoring:**
    ```bash
    # Query namespace-level ResourceQuota states
    kubectl get resourcequota

    # List container-level LimitRanges configured in the namespace
    kubectl get limitrange
    ```

### Anatomy & Boundary Table
| Variable / Parameter / Keyword Name | Expected Type / Allowed Values | Default Value / Operating Domain | Strict Structural Constraints |
| :--- | :--- | :--- | :--- |
| `rules[*].apiGroups` | Array of API groups (e.g., `""`, `apps`) | N/A | Use `""` to target core resources like Pods, Services, and ConfigMaps. |
| `rules[*].resources` | Array of resources | N/A (Required) | Must contain lowercase plural resource names matching API specifications. |
| `rules[*].verbs` | Array of verbs (e.g., `get`, `list`, `create`) | N/A (Required) | Case-sensitive list of permitted operations. |
| `policyTypes` | Array of strings (`Ingress`, `Egress`) | `Ingress` | Determines which directions of traffic the NetworkPolicy applies to. |
"""

M3_EXAMPLES = r"""### Real-World Case Studies & Applied Examples

#### Example 1: Isolating a Namespace and Granting Developer Permissions
*   **Context & Objectives:** Configure secure, isolated access for a development team named Team-Alpha to allow them to manage workloads in their dedicated namespace while blocking cluster-wide access.
*   **Design Trade-offs:** Namespace-scoped Roles and RoleBindings are used instead of global ClusterRoles to restrict the team's access within their namespace boundary.
*   **Implementation:**
    ```yaml
    apiVersion: v1
    kind: Namespace
    metadata:
      name: team-alpha
    ---
    apiVersion: rbac.authorization.k8s.io/v1
    kind: Role
    metadata:
      name: team-alpha-developer
      namespace: team-alpha
    rules:
    - apiGroups: ["", "apps"]
      resources: ["pods", "services", "deployments", "configmaps", "secrets"]
      verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
    ---
    apiVersion: rbac.authorization.k8s.io/v1
    kind: RoleBinding
    metadata:
      name: bind-team-alpha-developers
      namespace: team-alpha
    subjects:
    - kind: User
      name: "alice@company.com"
      apiGroup: rbac.authorization.k8s.io
    roleRef:
      kind: Role
      name: team-alpha-developer
      apiGroup: rbac.authorization.k8s.io
    ```
*   **Behavioral Analysis:**
    The API Server registers the `team-alpha-developer` Role. When `alice@company.com` makes an API request to deploy an application in the `team-alpha` namespace, the API Server authorizes the request. If she attempts to access resources in other namespaces, the request is blocked.

#### Example 2: Configuring a Cluster-Scoped View Role for Monitoring Agents
*   **Context & Objectives:** Deploy a central monitoring agent (like Prometheus) with read-only view access to collect metrics from all namespaces in the cluster.
*   **Design Trade-offs:** A ClusterRole is used to grant permissions globally across all namespaces, avoiding the need to duplicate RoleBindings in every namespace.
*   **Implementation:**
    ```yaml
    apiVersion: v1
    kind: ServiceAccount
    metadata:
      name: prometheus-collector
      namespace: monitoring
    ---
    apiVersion: rbac.authorization.k8s.io/v1
    kind: ClusterRoleBinding
    metadata:
      name: prometheus-global-view
    subjects:
    - kind: ServiceAccount
      name: prometheus-collector
      namespace: monitoring
    roleRef:
      kind: ClusterRole
      name: view
      apiGroup: rbac.authorization.k8s.io
    ```
*   **Behavioral Analysis:**
    The `prometheus-global-view` ClusterRoleBinding maps the `prometheus-collector` ServiceAccount to the cluster-wide `view` ClusterRole. The collector can now securely scrape endpoints and list resources across all namespaces in the cluster.

#### Example 3: Microsegmenting Database Traffic using NetworkPolicies
*   **Context & Objectives:** Configure secure, isolated network boundaries for a PostgreSQL database, allowing connections only from specific backend API Pods and blocking all other traffic.
*   **Design Trade-offs:** An ingress NetworkPolicy is used to restrict database access, ensuring that even if an attacker compromises a frontend container, they cannot connect to the database.
*   **Implementation:**
    ```yaml
    apiVersion: networking.k8s.io/v1
    kind: NetworkPolicy
    metadata:
      name: db-network-policy
      namespace: default
    spec:
      podSelector:
        matchLabels:
          app: database
      policyTypes:
      - Ingress
      ingress:
      - from:
        - podSelector:
            matchLabels:
              app: backend-api
        ports:
        - protocol: TCP
          port: 5432
    ```
*   **Behavioral Analysis:**
    The CNI plugin detects this NetworkPolicy and configures the node's local network filter (e.g., iptables). The filter blocks all network connections targeting port 5432 on database Pods, except for traffic originating from Pods labeled with `app: backend-api`.

#### Example 4: Enforcing Resource Boundaries with ResourceQuotas
*   **Context & Objectives:** Set strict resource boundaries on a development namespace to prevent developers from consuming excessive cluster resources.
*   **Design Trade-offs:** Applying a namespace-level ResourceQuota prevents resource starvation and helps cluster operators manage costs and resource allocations.
*   **Implementation:**
    ```yaml
    apiVersion: v1
    kind: ResourceQuota
    metadata:
      name: team-alpha-quota
      namespace: team-alpha
    spec:
      hard:
        pods: "10"
        requests.cpu: "4"
        requests.memory: "8Gi"
        limits.cpu: "8"
        limits.memory: "16Gi"
    ```
*   **Behavioral Analysis:**
    The API Server tracks the total sum of resource allocations in the `team-alpha` namespace. If a deployment request would push the namespace's total memory allocation above 16Gi, the Admission Controller immediately rejects the request.

#### Example 5: Setting Default Resource Allocations via LimitRanges
*   **Context & Objectives:** Ensure that any container deployed without explicit resource requests and limits is automatically assigned safe, default resource boundaries.
*   **Design Trade-offs:** Using a LimitRange prevents resource exhaustion and provides predictable performance by automatically injecting safe, default values.
*   **Implementation:**
    ```yaml
    apiVersion: v1
    kind: LimitRange
    metadata:
      name: default-limit-range
      namespace: team-alpha
    spec:
      limits:
      - default:
          cpu: "500m"
          memory: "512Mi"
        defaultRequest:
          cpu: "200m"
          memory: "256Mi"
        type: Container
    ```
*   **Behavioral Analysis:**
    When a developer applies a Pod manifest to the `team-alpha` namespace, the LimitRange Admission Controller inspects the container specifications. If a container lacks resource definitions, the controller automatically injects the default requests and limits before scheduling the Pod.
"""

M3_EXERCISE = r"""### Practical Laboratories & Hands-On Exercises

#### Lab 1: Auditing and Testing RBAC access policies
*   **Objective:** Create a ServiceAccount, configure namespace-level Roles, and verify permissions using authorization commands.
*   **Prerequisites:** Access to a running Kubernetes cluster.
*   **Step-by-Step Instructions:**
    1. Create a namespace named `sandbox-security` and a ServiceAccount named `read-only-sa`.
    2. Create a Role manifest named `rbac-role.yaml`:
       ```yaml
       apiVersion: rbac.authorization.k8s.io/v1
       kind: Role
       metadata:
         name: pod-reader
         namespace: sandbox-security
       rules:
       - apiGroups: [""]
         resources: ["pods"]
         verbs: ["get", "list", "watch"]
       ```
    3. Apply the Role: `kubectl apply -f rbac-role.yaml`
    4. Create a RoleBinding named `bind-reader` to link the ServiceAccount to the Role.
       ```yaml
       apiVersion: rbac.authorization.k8s.io/v1
       kind: RoleBinding
       metadata:
         name: bind-reader
         namespace: sandbox-security
       subjects:
       - kind: ServiceAccount
         name: read-only-sa
         namespace: sandbox-security
       roleRef:
         kind: Role
         name: pod-reader
         apiGroup: rbac.authorization.k8s.io
       ```
    5. Apply the RoleBinding: `kubectl apply -f rbac-role.yaml`
*   **Deterministic Verification Test:**
    Execute permissions checks to verify access limitations:
    `kubectl auth can-i create deployments --namespace sandbox-security --as=system:serviceaccount:sandbox-security:read-only-sa`
    `kubectl auth can-i list pods --namespace sandbox-security --as=system:serviceaccount:sandbox-security:read-only-sa`
    *   **Expected Output:**
        First command must return `no`.
        Second command must return `yes`.
*   **Troubleshooting Lab-Specific Issues:**
    If permissions checks are incorrect, verify that your RoleBinding's subjects references the correct ServiceAccount name and namespace exactly.

#### Lab 2: Securing Pod Traffic with Ingress NetworkPolicies
*   **Objective:** Deploy multiple application containers and restrict network traffic using an ingress NetworkPolicy.
*   **Prerequisites:** Running Kubernetes cluster with a network-policy-supporting CNI installed (like Calico or Cilium).
*   **Step-by-Step Instructions:**
    1. Deploy two test pods: `web-app` (labeled `app=frontend`) and `api-app` (labeled `app=backend`).
    2. Create a database pod labeled `app=db`.
    3. Verify that both frontend and backend pods can connect to the database.
    4. Create a NetworkPolicy manifest named `db-policy.yaml`:
       ```yaml
       apiVersion: networking.k8s.io/v1
       kind: NetworkPolicy
       metadata:
         name: db-policy
         namespace: default
       spec:
         podSelector:
           matchLabels:
             app: db
         policyTypes:
         - Ingress
         ingress:
         - from:
           - podSelector:
               matchLabels:
                 app: backend
       ```
    5. Apply the NetworkPolicy: `kubectl apply -f db-policy.yaml`
*   **Deterministic Verification Test:**
    Execute socket connections from both client pods to test connection limits:
    `kubectl exec -it web-app -- nc -zv <db-pod-ip> 5432`
    `kubectl exec -it api-app -- nc -zv <db-pod-ip> 5432`
    *   **Expected Output:**
        First connection (frontend to database) must fail or time out.
        Second connection (backend to database) must connect successfully.
*   **Troubleshooting Lab-Specific Issues:**
    If the NetworkPolicy has no effect, verify that your cluster's CNI supports NetworkPolicy enforcement. Standard flannel or local development CNI configurations may not enforce policies out of the box.

#### Lab 3: Restricting Resource Consumption with ResourceQuotas
*   **Objective:** Deploy a ResourceQuota to restrict the total amount of memory and CPU allocated in a namespace.
*   **Prerequisites:** Running Kubernetes cluster.
*   **Step-by-Step Instructions:**
    1. Create a namespace named `sandbox-quota`.
    2. Create a ResourceQuota manifest named `resource-quota.yaml`:
       ```yaml
       apiVersion: v1
       kind: ResourceQuota
       metadata:
         name: max-mem-quota
         namespace: sandbox-quota
       spec:
         hard:
           requests.memory: "256Mi"
           limits.memory: "512Mi"
       ```
    3. Apply the quota: `kubectl apply -f resource-quota.yaml`
    4. Attempt to deploy a Pod inside the `sandbox-quota` namespace requesting 512Mi of memory.
*   **Deterministic Verification Test:**
    Review the Pod deployment logs and verify if it was accepted:
    `kubectl get pods -n sandbox-quota`
    *   **Expected Output:**
        The deployment should be rejected, displaying an error message similar to: `exceeded quota: max-mem-quota, requested: requests.memory=512Mi, used: requests.memory=0, limited: requests.memory=256Mi`.
*   **Troubleshooting Lab-Specific Issues:**
    If the Pod is created successfully, make sure you applied it to the correct namespace and specified the memory requests correctly in the manifest.

#### Lab 4: Configuring Default Allocations using LimitRanges
*   **Objective:** Set default container requests and limits using a LimitRange configuration.
*   **Prerequisites:** Completed Lab 3.
*   **Step-by-Step Instructions:**
    1. Create a LimitRange manifest named `sandbox-limits.yaml`:
       ```yaml
       apiVersion: v1
       kind: LimitRange
       metadata:
         name: default-limits
         namespace: sandbox-quota
       spec:
         limits:
         - default:
             memory: "128Mi"
           defaultRequest:
             memory: "64Mi"
           type: Container
       ```
    2. Apply the LimitRange: `kubectl apply -f sandbox-limits.yaml`
    3. Deploy an Nginx Pod without any resource requests or limits inside the `sandbox-quota` namespace.
*   **Deterministic Verification Test:**
    Inspect the resources of your running Pod: `kubectl get pod nginx-pod -n sandbox-quota -o yaml`
    *   **Expected Output:**
        The Pod's container resources must show default requests and limits injected automatically: `limits: {memory: 128Mi}, requests: {memory: 64Mi}`.
*   **Troubleshooting Lab-Specific Issues:**
    Ensure you deploy the test Pod to the same namespace as the active LimitRange resource.

#### Lab 5: Implementing Egress NetworkPolicies to Lock Down Outbound Traffic
*   **Objective:** Configure an egress NetworkPolicy to restrict a Pod's outbound traffic to specific IP ranges.
*   **Prerequisites:** Running Kubernetes cluster with an active, policy-enforcing CNI.
*   **Step-by-Step Instructions:**
    1. Deploy a test client pod labeled `app=isolated-client`.
    2. Verify the Pod has internet access: `kubectl exec -it isolated-client -- curl -I https://www.google.com`
    3. Create an egress NetworkPolicy named `egress-policy.yaml`:
       ```yaml
       apiVersion: networking.k8s.io/v1
       kind: NetworkPolicy
       metadata:
         name: restrict-egress
       spec:
         podSelector:
           matchLabels:
             app: isolated-client
         policyTypes:
         - Egress
         egress:
         - to:
           - ipBlock:
               cidr: 10.0.0.0/8
       ```
    4. Apply the egress NetworkPolicy: `kubectl apply -f egress-policy.yaml`
*   **Deterministic Verification Test:**
    Test internet access from the isolated Pod: `kubectl exec -it isolated-client -- curl -I https://www.google.com`
    *   **Expected Output:**
        The connection should hang or time out, confirming outbound internet traffic is blocked.
*   **Troubleshooting Lab-Specific Issues:**
    Egress enforcement requires CNI level routing integration. Verify that your CNI supports egress policies and that no other NetworkPolicies are overriding your settings in the namespace.
"""

M3_INSIGHT = r"""### Professional Interview & Advanced Deep Dive

#### Q1: What is the behavioral difference between RoleBindings and ClusterRoleBindings?
*   **Answer:** A `RoleBinding` applies a Role (or ClusterRole) within a specific namespace boundary. It grants access to namespaced resources only within that namespace. A `ClusterRoleBinding` is cluster-scoped and applies globally. It grants permissions to cluster-scoped resources (such as `Nodes` or `PersistentVolumes`) and namespaced resources across all namespaces in the cluster, making it ideal for cluster-wide monitoring and administrative tools.

#### Q2: How do NetworkPolicies interact, and what happens when multiple policies match the same Pod?
*   **Answer:** NetworkPolicies in Kubernetes are additive. By default, Pods accept connections from any IP (non-isolated). Once a NetworkPolicy matches a Pod selector, the Pod is isolated, and only traffic that matches at least one of the defined policy rules is allowed. If multiple NetworkPolicies match a Pod, their rules are combined using a logical OR, permitting any traffic that satisfies at least one policy constraint.

#### Q3: Why is configuring resource requests so critical for cluster stability and Pod scheduling?
*   **Answer:** Resource requests define the minimum resources guaranteed to a container. The scheduler evaluates requests (not limits or actual utilization) to determine if a node has enough allocatable capacity to host a Pod. If requests are omitted or set too low, the scheduler may overload nodes, leading to resource contention, CPU throttling, and critical out-of-memory crashes as Pods burst to their limits.

#### Q4: How does a CNI plugin enforce NetworkPolicies at the system layer?
*   **Answer:** NetworkPolicies are not enforced by the API Server or kubelet. Instead, the active CNI plugin (such as Calico or Cilium) watches the API Server for changes to NetworkPolicies, Pods, and Namespaces. The plugin translates these policies into host-level packet filtering rules. Calico writes these rules using kernel `iptables` or IPVS tables, while Cilium writes highly performant `eBPF` programs loaded directly into the kernel's network socket layer, intercepting and filtering packets with minimal latency.

#### Q5: What is the difference between CPU requests and CPU limits, and how does the kernel handle them?
*   **Answer:** CPU requests allocate CPU shares inside the CFS (Completely Fair Scheduler) scheduler in the Linux kernel, guaranteeing a minimum amount of CPU processing time to a container process. CPU limits set the maximum CPU processing time a container is allowed to consume. If a container process attempts to exceed its CPU limit, the kernel throttles (slows down) its execution, but does not terminate the container, avoiding application crashes.

### Academic & Professional Alignment
Understanding cluster security, access control, and network microsegmentation is a key requirement on the CKS (Certified Kubernetes Security Specialist) exam. Masters of these security boundaries are highly valued in enterprise environments for building reliable, secure, and multi-tenant architectures.
"""

# =====================================================================
# MODULE 4: ENTERPRISE CONFIGURATION MANAGEMENT & GITOPS
# =====================================================================

M4_THEORY = r"""### Guided Conceptual Walkthrough
Imagine you run a large automobile manufacturing company. In the early days, workers hand-crafted every part of every car individually (manually modifying YAML manifests for every deployment). This was slow, expensive, and led to inconsistent results. 

To scale up production, you implement two modern design approaches:
*   **Helm**: Create a master mold template with customizable options (variables). You can quickly customize cars with different configurations (like color or engine size) for different environments (like Dev or Production) using a single option form (**values.yaml**).
*   **Kustomize**: Create a base car model and apply customized overlays (patches) on top of it, avoiding the need to duplicate configurations.
*   **ArgoCD (GitOps)**: Build an automated assembly line that monitors your design blueprints (Git) and automatically builds, tests, and deploys the cars to match, ensuring your fleet is always up to date.

### Architectural, Lifecycle & Flow Blueprints

```mermaid
graph TD
    Git[Git Repository] -->|Polls Changes| CD[ArgoCD Controller]
    CD -->|Calculates Drift| K8s[Kubernetes Cluster]
    Helm[Helm Chart] -->|Values Engine| Manifests[Compiled YAML]
```

```mermaid
sequenceDiagram
    autonumber
    GitPush->>Git: Commit updated values.yaml
    ArgoCD->>Git: Detect New Commit
    ArgoCD->>K8sAPI: Diff Live vs Desired
    ArgoCD->>K8sAPI: Apply Changes (Sync)
```

### Under-the-Hood Mechanics & Internal Operations
Helm operates entirely as a client-side package manager. It uses Go templating to compile local resource templates into standard Kubernetes manifests. When you run `helm install`, the engine parses the templates, injects the values, and sends the compiled YAML manifests to the API Server. Helm tracks release history using standard Kubernetes Secrets in the target namespace. 

ArgoCD runs a continuous reconciliation loop within the cluster. It polls the Git repository for changes, compiles the manifests (supporting Helm, Kustomize, or plain YAML), and compares the compiled target states against the active resources in the cluster. If it detects changes in Git, it applies them to the cluster (Sync). If it detects manual changes in the cluster that deviate from Git (Drift), it automatically overrides those changes to restore the desired state from Git (Self-Healing).

### Deep-Dive Reference (Advanced Context)
<details>
<summary>Kustomize Overlay Engines and Bases</summary>
Unlike template-based systems like Helm, Kustomize works by patching base configurations directly.
*   **Bases**: The core, environment-independent resource definitions.
*   **Overlays**: Environment-specific directories containing a `kustomization.yaml` file. Kustomize merges these overlays on top of the base files, applying overrides (like changing replica counts, resource limits, or injecting ConfigMap keys) without modifying the original base manifests.
</details>

### Systemic Failure Modes & Boundary Violations
*   **Failure Mode 1: Helm Go Template Parsing Syntax Error**
    *   **Symptom:** Running `helm install` fails with a template rendering error or a syntax parsing mismatch.
    *   **Root Cause:** The Helm template contains a typo, a mismatched variable reference, or invalid indentation inside the Go template statements.
    *   **Resolution:** Run Helm linting and dry-run commands to check for syntax and formatting errors before deploying:
        ```bash
        helm lint ./my-chart
        helm template my-release ./my-chart -f values.yaml
        ```

*   **Failure Mode 2: ArgoCD Git Sync Collision (Out of Sync Loop)**
    *   **Symptom:** ArgoCD remains stuck in an `Out of Sync` or `Sync Failed` loop, continuously applying changes to the cluster.
    *   **Root Cause:** A conflict between Git and cluster-mutating admission controllers (such as sidecar injectors or autoscalers), which dynamically update resource parameters that are not defined in Git.
    *   **Resolution:** Configure ArgoCD to ignore specific resource fields during sync operations:
        ```yaml
        ignoreDifferences:
        - group: apps
          kind: Deployment
          jsonPointers:
          - /spec/replicas
        ```

*   **Failure Mode 3: Kustomize Overlay Target Mismatch**
    *   **Symptom:** Applying a Kustomize overlay fails with a target selection error.
    *   **Root Cause:** The overlay patch references an apiVersion, kind, or resource name that does not exist or has been modified in the base directory.
    *   **Resolution:** Verify the patch targets in your `kustomization.yaml` and ensure they match the base resource metadata exactly:
        ```yaml
        patches:
        - target:
            group: apps
            version: v1
            kind: Deployment
            name: base-web-app
        ```

### Traceability Schema Check
All configuration management tools (Helm, Kustomize) and GitOps reconciliation workflows (ArgoCD) used in down-stream commands and exercises are conceptually defined in this section.
"""

M4_COMMANDS = r"""### Technical & Syntax Reference Manual
Below are the essential commands for packaging applications and managing GitOps continuous delivery workflows.

*   **Helm Lifecycle Controls:**
    ```bash
    # Create a new boilerplate Helm chart directory structure
    helm create web-application-chart

    # Package a Helm chart into a deployable archive
    helm package ./web-application-chart

    # Deploy a Helm chart using a custom values file
    helm upgrade --install web-app ./web-application-chart -f prod-values.yaml
    ```

*   **Kustomize Resource Generation:**
    ```bash
    # Compile and output raw manifests from a Kustomize overlay directory
    kubectl kustomize ./overlays/production/

    # Compile and apply Kustomize resources directly to the cluster
    kubectl apply -k ./overlays/production/
    ```

### Anatomy & Boundary Table
| Variable / Parameter / Keyword Name | Expected Type / Allowed Values | Default Value / Operating Domain | Strict Structural Constraints |
| :--- | :--- | :--- | :--- |
| `values.yaml` keys | Custom dictionary | N/A (User Defined) | Use camelCase or lowercase for key names; avoid hyphens as they can break Go template parsing. |
| `.Release.Name` | String | Dynamic (Release Name) | Built-in Helm variable; resolves to the active release name. |
| `resources` | List of file or directory paths | N/A | Must point to valid manifest files or subdirectories in Kustomize. |
| `syncPolicy.automated` | Object | N/A | Enables automated git reconciliation and self-healing in ArgoCD. |
"""

M4_EXAMPLES = r"""### Real-World Case Studies & Applied Examples

#### Example 1: Creating a Custom, Dry-Run Validated Helm Chart
*   **Context & Objectives:** Standardize application packaging for a microservices team by designing a reusable, parameter-driven Helm chart.
*   **Design Trade-offs:** Helm is chosen over plain YAML to enable parameterized configurations, allowing developers to customize variables (like replica counts and resource limits) easily.
*   **Implementation:**
    `Chart.yaml`
    ```yaml
    apiVersion: v2
    name: microservice-chart
    description: A dynamic Helm Chart for managing containerized applications.
    type: application
    version: 0.1.0
    appVersion: "1.25.3"
    ```
    `values.yaml`
    ```yaml
    replicaCount: 2
    image:
      repository: nginx
      tag: 1.25.3
    resources:
      requests:
        cpu: "100m"
        memory: "128Mi"
    ```
    `templates/deployment.yaml`
    ```yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: {{ .Release.Name }}-deploy
    spec:
      replicas: {{ .Values.replicaCount }}
      selector:
        matchLabels:
          app: {{ .Release.Name }}
      template:
        metadata:
          labels:
            app: {{ .Release.Name }}
        spec:
          containers:
          - name: app
            image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
            resources:
              requests:
                cpu: {{ .Values.resources.requests.cpu }}
                memory: {{ .Values.resources.requests.memory }}
    ```
*   **Behavioral Analysis:**
    Running `helm template test ./microservice-chart` compiles the templates. Helm injects variables from `values.yaml`, replacing placeholders with actual values, and outputs the compiled manifests for validation.

#### Example 2: Managing Multi-Environment Overlays with Kustomize
*   **Context & Objectives:** Manage environment-specific configurations (Dev and Prod) for an application without duplicating base resource manifests.
*   **Design Trade-offs:** Kustomize is chosen over Helm because it is template-free and integrated directly into `kubectl`, reducing configuration complexity.
*   **Implementation:**
    `base/deployment.yaml`
    ```yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: base-api
    spec:
      replicas: 1
      selector:
        matchLabels:
          app: base-api
      template:
        metadata:
          labels:
            app: base-api
        spec:
          containers:
          - name: app
            image: alpine:3.18
            command: ["sleep", "3600"]
    ```
    `base/kustomization.yaml`
    ```yaml
    resources:
    - deployment.yaml
    ```
    `overlays/production/kustomization.yaml`
    ```yaml
    resources:
    - ../../base
    patches:
    - target:
        kind: Deployment
        name: base-api
      patch: |-
        - op: replace
          path: /spec/replicas
          value: 5
    ```
*   **Behavioral Analysis:**
    Running `kubectl kustomize ./overlays/production/` reads the base manifests and applies the overlay patches. It outputs the compiled, production-ready manifests, scaling the replicas from 1 to 5 without modifying the original base files.

#### Example 3: ArgoCD GitOps Continuous Delivery Pipeline
*   **Context & Objectives:** Configure an automated GitOps delivery pipeline to synchronize deployment states with a Git repository, ensuring the cluster always matches the desired state defined in Git.
*   **Design Trade-offs:** ArgoCD is chosen for its automated sync and self-healing policies, which eliminate manual deployment steps and automatically correct configuration drift in the cluster.
*   **Implementation:**
    ```yaml
    apiVersion: argoproj.io/v1alpha1
    kind: Application
    metadata:
      name: staging-web-app
      namespace: argocd
    spec:
      project: default
      source:
        repoURL: 'https://github.com/sandbox/gitops-deployments.git'
        targetRevision: HEAD
        path: environments/staging
      destination:
        server: 'https://kubernetes.default.svc'
        namespace: staging
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
    ```
*   **Behavioral Analysis:**
    The ArgoCD controller monitors the target Git repository subpath. When a developer pushes an update to Git, ArgoCD detects the change, compares it to the live cluster state, and automatically applies the updates (Sync) to the `staging` namespace.

#### Example 4: Injecting Values across Multiple Helm Value Files
*   **Context & Objectives:** Deploy a Helm chart across staging and production environments using different values files to customize resources and replica counts.
*   **Design Trade-offs:** Staging and production configurations are separated into distinct values files to maintain environment isolation and prevent human errors during updates.
*   **Implementation:**
    `values-staging.yaml`
    ```yaml
    replicaCount: 1
    resources:
      requests:
        cpu: "50m"
        memory: "64Mi"
    ```
    `values-production.yaml`
    ```yaml
    replicaCount: 10
    resources:
      requests:
        cpu: "1"
        memory: "2Gi"
    ```
*   **Behavioral Analysis:**
    Running `helm upgrade --install prod-api ./microservice-chart -f values-production.yaml` applies the production overrides. Helm upgrades the release, scaling the API to 10 replicas with high resource allocations suitable for production workloads.

#### Example 5: Mitigating Configuration Drift using ArgoCD Self-Healing
*   **Context & Objectives:** Lock down a staging environment to prevent manual, ad-hoc changes (drift) in the cluster and ensure all deployments match the git state.
*   **Design Trade-offs:** Enabling self-healing in ArgoCD ensures that any manual changes in the cluster are immediately detected and overridden to match the desired state in Git, maintaining configuration consistency.
*   **Implementation:**
    ```yaml
    syncPolicy:
      automated:
        prune: true
        selfHeal: true
    ```
*   **Behavioral Analysis:**
    If a developer manually scales a deployment using `kubectl scale`, the ArgoCD controller detects the mismatch (drift) between the cluster state and the desired state in Git. ArgoCD immediately overrides the manual change, scaling the deployment back to the replica count defined in Git.
"""

M4_EXERCISE = r"""### Practical Laboratories & Hands-On Exercises

#### Lab 1: Designing a Parameterized Helm Chart from Scratch
*   **Objective:** Create a custom Helm chart, configure template variables, and deploy it to the cluster.
*   **Prerequisites:** Helm CLI and a running Kubernetes cluster.
*   **Step-by-Step Instructions:**
    1. Create a boilerplate Helm chart named `sandbox-chart`:
       ```bash
       helm create sandbox-chart
       ```
    2. Delete the boilerplate templates to start clean:
       ```bash
       rm -rf ./sandbox-chart/templates/*
       ```
    3. Create a template file named `./sandbox-chart/templates/deploy.yaml`:
       ```yaml
       apiVersion: apps/v1
       kind: Deployment
       metadata:
         name: {{ .Release.Name }}-app
       spec:
         replicas: {{ .Values.replicaCount }}
         selector:
           matchLabels:
             app: {{ .Release.Name }}
         template:
           metadata:
             labels:
               app: {{ .Release.Name }}
           spec:
             containers:
             - name: main
               image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
       ```
    4. Update `./sandbox-chart/values.yaml` with your variables:
       ```yaml
       replicaCount: 3
       image:
         repository: nginx
         tag: 1.25.3
       ```
    5. Deploy your Helm chart to the cluster:
       ```bash
       helm install my-app ./sandbox-chart
       ```
*   **Deterministic Verification Test:**
    Verify the deployment and the replica count: `kubectl get deployments`
    *   **Expected Output:**
        `NAME         READY   UP-TO-DATE   AVAILABLE`
        `my-app-app   3/3     3            3`
*   **Troubleshooting Lab-Specific Issues:**
    If the deployment fails with template syntax errors, run `helm lint ./sandbox-chart` to locate and fix formatting, spacing, or bracket matching errors.

#### Lab 2: Scaling Deployments using Kustomize Overlays
*   **Objective:** Configure an application using Kustomize bases and apply overlays to scale replicas.
*   **Prerequisites:** Access to a running Kubernetes cluster.
*   **Step-by-Step Instructions:**
    1. Create a `base` directory containing an Nginx deployment manifest.
    2. Create a `base/kustomization.yaml` referencing the deployment file.
    3. Create an `overlays/staging` directory.
    4. Create an `overlays/staging/kustomization.yaml` file to scale replicas to 4:
       ```yaml
       resources:
       - ../../base
       patches:
       - target:
           kind: Deployment
           name: base-nginx
         patch: |-
           - op: replace
             path: /spec/replicas
             value: 4
       ```
    5. Compile and apply the Kustomize configuration to the cluster:
       ```bash
       kubectl apply -k ./overlays/staging/
       ```
*   **Deterministic Verification Test:**
    Verify the deployment and replica count: `kubectl get deployments`
    *   **Expected Output:**
        `NAME         READY   UP-TO-DATE   AVAILABLE`
        `base-nginx   4/4     4            4`
*   **Troubleshooting Lab-Specific Issues:**
    If the deployment fails with a patch target mismatch error, verify that the patch targets in `kustomization.yaml` match the base resource name and apiVersion exactly.

#### Lab 3: Validating Template Renderings via Dry-Run Checks
*   **Objective:** Run static analysis and validation dry-run checks on your Helm charts before deploying them.
*   **Prerequisites:** Completed Lab 1.
*   **Step-by-Step Instructions:**
    1. Modify `./sandbox-chart/values.yaml` to set an invalid tag or image name.
    2. Run a static template rendering to check the output manifests:
       ```bash
       helm template my-app ./sandbox-chart/
       ```
    3. Run a server-side dry-run check to validate the configurations against the API Server:
       ```bash
       helm install dry-run-release ./sandbox-chart/ --dry-run
       ```
*   **Deterministic Verification Test:**
    Observe the output logs of the dry-run check in your terminal.
    *   **Expected Output:**
        The output must display the compiled manifests, verify syntax and resource schemas, and confirm the release is valid without creating actual resources in the cluster.
*   **Troubleshooting Lab-Specific Issues:**
    If the dry-run fails with schema validation errors, verify that you did not introduce syntax errors or misspellements when editing your templates.

#### Lab 4: Configuring a Local ArgoCD GitOps Application Sync
*   **Objective:** Deploy an ArgoCD Application, link it to a Git repository, and monitor the automated sync loop.
*   **Prerequisites:** ArgoCD operator installed on your cluster.
*   **Step-by-Step Instructions:**
    1. Create an ArgoCD Application manifest named `argocd-app.yaml`:
       ```yaml
       apiVersion: argoproj.io/v1alpha1
       kind: Application
       metadata:
         name: gitops-web-app
         namespace: argocd
       spec:
         project: default
         source:
           repoURL: 'https://github.com/argoproj/argocd-example-apps.git'
           targetRevision: HEAD
           path: guestbook
         destination:
           server: 'https://kubernetes.default.svc'
           namespace: default
         syncPolicy:
           automated:
             prune: true
             selfHeal: true
       ```
    2. Apply the Application manifest: `kubectl apply -f argocd-app.yaml`
    3. Wait for the sync loop to initialize: `kubectl get pods -w`
*   **Deterministic Verification Test:**
    Check the status of the ArgoCD Application sync: `kubectl get application gitops-web-app -n argocd -o yaml`
    *   **Expected Output:**
        The sync status should be `Synced` and the health status should show `Healthy`.
*   **Troubleshooting Lab-Specific Issues:**
    If the sync fails, verify that your cluster has access to the internet to reach the remote Git repository, and that the specified repoURL and path are correct.

#### Lab 5: Simulating and Mitigating Staging Drift Events
*   **Objective:** Force a configuration drift event and verify that ArgoCD automatically detects and overrides the manual change.
*   **Prerequisites:** Completed Lab 4.
*   **Step-by-Step Instructions:**
    1. Force configuration drift by manually scaling your guestbook deployment to 5 replicas:
       ```bash
       kubectl scale deployment/guestbook-ui --replicas=5
       ```
    2. Monitor the deployment to see if it responds to your command: `kubectl get deployment guestbook-ui -w`
*   **Deterministic Verification Test:**
    Observe the replica count changes in your terminal.
    *   **Expected Output:**
        The replica count should scale to 5 momentarily, and then immediately scale back down to the replica count defined in Git (typically 1), confirming ArgoCD has overridden the manual change.
*   **Troubleshooting Lab-Specific Issues:**
    If the manual change is not overridden, verify that self-healing is enabled (`selfHeal: true`) in your ArgoCD Application manifest.
"""

M4_INSIGHT = r"""### Professional Interview & Advanced Deep Dive

#### Q1: What is the primary difference between Helm and Kustomize, and how do you choose between them?
*   **Answer:** Helm is a template-driven package manager that uses Go templating to compile dynamic resource manifests based on variables defined in a values file. It is ideal for sharing public applications, managing complex releases, and handling advanced templating logic. Kustomize is a template-free configuration tool that works by merging patches on top of base YAML files. It is integrated directly into `kubectl`, making it ideal for managing environment overrides (like Dev/Staging/Prod) without adding templating complexity.

#### Q2: How does ArgoCD handle and reconcile configuration drift inside the cluster?
*   **Answer:** ArgoCD runs a continuous reconciliation loop within the cluster, polling the target Git repository (the desired state) and comparing it against the active resources in the cluster (the live state). If it detects a mismatch (drift), and self-healing is enabled, the controller immediately generates a delta-patch and applies it to the cluster, restoring the cluster to the target state defined in Git.

#### Q3: Why is managing secrets directly in plain-text Helm value files considered a security risk, and how do you secure them?
*   **Answer:** Storing sensitive passwords, API keys, or certificates in plain-text values files exposes them to anyone with read access to the Git repository. To secure secrets in a GitOps workflow, you should use encrypted custom resources like Sealed Secrets (encrypting secrets on the client side using public-key cryptography) or retrieve secrets dynamically at runtime from external vault providers like HashiCorp Vault.

#### Q4: How does Helm track the history of its releases, and how does it perform rollbacks?
*   **Answer:** Helm stores release history metadata as standard Kubernetes Secrets in the namespace where the release is installed. Each time you deploy an upgrade, Helm creates a new Secret containing the full configuration layout of that specific revision. When you run `helm rollback <release-name> <revision-number>`, Helm reads the configuration of the target revision from the stored Secret and sends a delta-update to the API Server, restoring the stable state.

#### Q5: What is the risk of having both ArgoCD auto-sync and in-cluster mutating controllers active on the same resource fields?
*   **Answer:** If both ArgoCD and an in-cluster mutating controller (such as an Horizontal Pod Autoscaler or a sidecar injector) manage the same resource fields (like replica count or environment variables), they will enter a conflict loop. ArgoCD will detect a drift and apply changes, and the controller will immediately overwrite them, causing infinite sync loops, high CPU utilization, and system instability. To prevent this, you must configure ArgoCD to ignore these specific fields during sync operations.

### Academic & Professional Alignment
Mastering Helm, Kustomize, and GitOps workflows with ArgoCD is critical for modern DevOps and SRE roles. Demonstrating proficiency in configuring declarative, automated delivery pipelines is highly valued in enterprise environments for building reliable, secure, and reproducible systems.
"""

# =====================================================================
# MODULE 5: PRODUCTION OBSERVABILITY, ALERTING & SRE PRINCIPLES
# =====================================================================

M5_THEORY = r"""### Guided Conceptual Walkthrough
Imagine you run a nuclear power plant. To run the plant safely and prevent meltdowns (outages), you set up highly sophisticated monitoring systems:
*   **Prometheus & Grafana**: Set up real-time sensors (**Metrics Exporters**) across all pipes and reactors to collect pressure and temperature statistics, and display this data on a central dashboard (**Grafana**).
*   **Probes**: Install automated validation checks (**Liveness & Readiness Probes**) inside the reactors. If a pipe freezes, the system immediately routes traffic away from it. If a reactor malfunctions, it is shut down and restarted.
*   **Alertmanager**: Configure a central alarm station (**Alertmanager**) to alert operators immediately via pager (Slack or PagerDuty) if values exceed safe boundaries.
*   **SLIs & SLOs**: Set strict reliability targets, mathematically allowing a maximum of only ≈43.8 minutes of downtime per month to maintain a 99.9% availability target.

### Architectural, Lifecycle & Flow Blueprints

```mermaid
graph TD
    Prom[Prometheus Server] -->|Scrapes Metrics| SM[Service Monitor]
    SM -->|Discovers App| Svc[Target Service]
    Exporter[Metrics Exporter] -->|Exposes /metrics| Pod[App Container]
```

```mermaid
sequenceDiagram
    autonumber
    Kubelet->>Pod: HTTP GET /healthz (Readiness)
    Pod-->>Kubelet: HTTP 200 OK
    Kubelet->>Endpoints: Add Pod IP to Service
```

### Under-the-Hood Mechanics & Internal Operations
At the application verification layer, the `kubelet` agent running on each worker node periodically executes container probes (Liveness, Readiness, and Startup) by making HTTP GET requests, opening TCP sockets, or executing CLI commands inside the container namespaces. 

*   **Readiness Probes**: Determine if a container is ready to accept network traffic. If a readiness probe fails, the endpoint controller immediately removes the Pod's IP address from the active `Endpoints` lists of all matching Services, preventing clients from receiving HTTP errors.
*   **Liveness Probes**: Determine if a container process is frozen or hung. If a liveness probe fails, the kubelet immediately terminates the container process and triggers a restart according to the Pod's restart policy.

SRE mathematics defines reliability targets based on Service Level Indicators (SLIs) and Service Level Objectives (SLOs). For an availability target of $A = 99.9\%$, the maximum monthly error budget (allowable downtime) $D$ is calculated as:
$$D = 30 \text{ days} \times 24 \text{ hours/day} \times 60 \text{ minutes/hour} \times (1 - A)$$
$$D = 43200 \text{ minutes} \times 0.001 = 43.2 \text{ minutes}$$

### Deep-Dive Reference (Advanced Context)
<details>
<summary>ServiceMonitors and Dynamic Prometheus Scraping</summary>
The Prometheus Operator uses custom resources to manage dynamic metrics scraping. A `ServiceMonitor` uses label selectors to target Services. The operator automatically updates Prometheus's scraping configurations as Pods are added or removed, bypassing static configurations and enabling dynamic discovery in elastic clusters.
</details>

### Systemic Failure Modes & Boundary Violations
*   **Failure Mode 1: Liveness Probe Boot Loop (Cascade Restart Failure)**
    *   **Symptom:** Pod starts up, runs for a few seconds, and then is terminated and restarted by the kubelet, entering an infinite loop of restarts.
    *   **Root Cause:** The `livenessProbe` was configured with an initial delay that is shorter than the application's actual startup time, causing the probe to fail and restart the container before it can finish initializing.
    *   **Resolution:** Add a `startupProbe` or increase the `initialDelaySeconds` on your liveness probe to provide enough startup overhead:
        ```yaml
        startupProbe:
          httpGet:
            path: /healthz
            port: 8080
          failureThreshold: 30
          periodSeconds: 10
        ```

*   **Failure Mode 2: Prometheus Scrape Target Disappeared (Port Name Mismatch)**
    *   **Symptom:** Target endpoints disappear from the Prometheus dashboard, and metrics are missing from Grafana panels.
    *   **Root Cause:** The port name or labels defined in the `ServiceMonitor` do not match the port name or labels configured on the target Service resource.
    *   **Resolution:** Verify the port definitions and ensure the Service's `port.name` matches the `ServiceMonitor.spec.endpoints.port` value exactly:
        ```yaml
        # In ServiceMonitor:
        endpoints:
        - port: http-metrics
        # In Service:
        ports:
        - name: http-metrics
          port: 8080
        ```

*   **Failure Mode 3: Missing Readiness Probe during Rolling Updates**
    *   **Symptom:** Users encounter brief spikes of HTTP `502 Bad Gateway` or `503 Service Unavailable` errors during deployment upgrades.
    *   **Root Cause:** The deployment lacks a `readinessProbe`, prompting the scheduler to route traffic to the new Pods immediately upon creation, before the application inside the container has finished starting and is ready to accept connections.
    *   **Resolution:** Always define explicit readiness probes to prevent traffic routing to uninitialized containers:
        ```yaml
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
        ```

### Traceability Schema Check
All telemetry scraping protocols (`ServiceMonitor`), alerting engines (`Alertmanager`), SRE reliability calculations (SLIs/SLOs), and container probes (Liveness/Readiness/Startup) used below are conceptually mapped to this section.
"""

M5_COMMANDS = r"""### Technical & Syntax Reference Manual
Below are the essential commands for managing observability resources, configuring alerting rules, and inspecting application logs.

*   **Metrics API Queries:**
    ```bash
    # View real-time CPU and memory usage statistics for all worker nodes
    kubectl top nodes

    # Check metrics collected for Pods in the active namespace
    kubectl top pods
    ```

*   **ServiceMonitor Auditing:**
    ```bash
    # List active ServiceMonitors configured across all namespaces
    kubectl get servicemonitors -A

    # Retrieve detailed discovery configuration for a ServiceMonitor
    kubectl describe servicemonitor app-metrics-monitor -n monitoring
    ```

### Anatomy & Boundary Table
| Variable / Parameter / Keyword Name | Expected Type / Allowed Values | Default Value / Operating Domain | Strict Structural Constraints |
| :--- | :--- | :--- | :--- |
| `readinessProbe.httpGet.path` | String | N/A (Required for HTTP) | Must match a valid HTTP endpoint that returns status 200-399. |
| `initialDelaySeconds` | Integer (0 - 3600) | `0` | Delay before the kubelet begins executing probes. |
| `periodSeconds` | Integer (1 - 3600) | `10` | Frequency at which the kubelet executes the probe check. |
| `failureThreshold` | Integer (1 - 100) | `3` | Number of consecutive failures before restarting or isolating the container. |
"""

M5_EXAMPLES = r"""### Real-World Case Studies & Applied Examples

#### Example 1: Robust Multi-Probe Configuration for Startup, Liveness, and Readiness
*   **Context & Objectives:** Deploy a Java Spring Boot application that takes 45 seconds to initialize, ensuring it does not enter boot loops on startup and is only sent traffic when fully ready.
*   **Design Trade-offs:** Combining startup, liveness, and readiness probes prevents cascade restarts during slow boot sequences while maintaining rapid error detection during runtime.
*   **Implementation:**
    ```yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: spring-api
    spec:
      replicas: 2
      selector:
        matchLabels:
          app: spring-api
      template:
        metadata:
          labels:
            app: spring-api
        spec:
          containers:
          - name: api
            image: openjdk:17-slim
            ports:
            - containerPort: 8080
            startupProbe:
              httpGet:
                path: /actuator/health/liveness
                port: 8080
              failureThreshold: 10
              periodSeconds: 10
            livenessProbe:
              httpGet:
                path: /actuator/health/liveness
                port: 8080
              periodSeconds: 15
            readinessProbe:
              httpGet:
                path: /actuator/health/readiness
                port: 8080
              periodSeconds: 10
    ```
*   **Behavioral Analysis:**
    The `kubelet` begins checks by running the `startupProbe`. It allows up to 100 seconds (10 attempts $\times$ 10 seconds) for the JVM to initialize. Once the startup probe succeeds, it is disabled, and the liveness and readiness probes take over. If the readiness probe fails, the Pod IP is removed from Services. If the liveness probe fails, the container is restarted.

#### Example 2: Configuring Alertmanager Alerting Rules for OOMKilled Pods
*   **Context & Objectives:** Configure a Prometheus alerting rule to alert SRE teams via Alertmanager immediately if an application is terminated due to an OOMKilled crash.
*   **Design Trade-offs:** Setting up proactive alerts for OOM terminations allows SRE teams to identify and resolve resource bottlenecks before they impact users.
*   **Implementation:**
    ```yaml
    apiVersion: monitoring.coreos.com/v1
    kind: PrometheusRule
    metadata:
      name: oomkilled-alerts
      namespace: monitoring
      labels:
        role: alert-rules
    spec:
      groups:
      - name: container-alerts
        rules:
        - alert: ContainerOOMKilled
          expr: kube_pod_container_status_terminated_reason{reason="OOMKilled"} > 0
          for: 1m
          labels:
            severity: critical
          annotations:
            summary: "Container {{ $labels.container }} in Pod {{ $labels.pod }} was OOMKilled"
            description: "The container consumed more memory than its limit and was terminated by the host kernel."
    ```
*   **Behavioral Analysis:**
    The Prometheus Server evaluates the rule's PromQL expression. If a container status reason matches `OOMKilled` for more than 1 minute, the rule is triggered, and the alert is forwarded to Alertmanager to notify the on-call SRE team.

#### Example 3: Grafana Loki and FluentBit Centralized Logging Pipeline
*   **Context & Objectives:** Deploy a log pipeline to automatically collect, process, and forward container logs to Grafana Loki for search and visualization.
*   **Design Trade-offs:** Running FluentBit as a DaemonSet ensures that logs are collected from every node, and forwarding them to Loki provides high-performance search capabilities with minimal storage overhead.
*   **Implementation:**
    `fluent-bit-config.yaml`
    ```yaml
    apiVersion: v1
    kind: ConfigMap
    metadata:
      name: fluentbit-config
      namespace: logging
    data:
      fluent-bit.conf: |
        [SERVICE]
            Flush         1
            Log_Level     info
            Daemon        off
            Parsers_File  parsers.conf

        [INPUT]
            Name              tail
            Tag               kube.*
            Path              /var/log/containers/*.log
            Parser            docker
            DB                /var/log/flb_kube.db
            Mem_Buf_Limit     5MB

        [FILTER]
            Name                kubernetes
            Match               kube.*
            Kube_URL            https://kubernetes.default.svc:443
            Kube_Tag_Prefix     kube.var.log.containers.
            Merge_Log           On
            Keep_Log            Off

        [OUTPUT]
            Name          loki
            Match         *
            Host          loki-service.logging.svc.cluster.local
            Port          3100
            Labels        job=fluentbit
    ```
*   **Behavioral Analysis:**
    FluentBit tails log files from `/var/log/containers/`. The `kubernetes` filter queries the API Server to enrich the log records with metadata (such as namespace, pod name, and container name) before forwarding the structured logs to the central Loki service.

#### Example 4: Creating a Prometheus ServiceMonitor for Custom Metrics Exporter
*   **Context & Objectives:** Configure the Prometheus Operator to automatically scrape custom application metrics from a Python web server.
*   **Design Trade-offs:** A `ServiceMonitor` is used to allow Prometheus to dynamically discover and scrape the exporter's endpoints, avoiding the need to manage static configuration files.
*   **Implementation:**
    ```yaml
    apiVersion: monitoring.coreos.com/v1
    kind: ServiceMonitor
    metadata:
      name: app-metrics-monitor
      namespace: monitoring
      labels:
        release: prometheus-stack
    spec:
      selector:
        matchLabels:
          app: python-web-app
      namespaceSelector:
        matchNames:
        - default
      endpoints:
      - port: metrics
        path: /metrics
        interval: 10s
    ```
*   **Behavioral Analysis:**
    The Prometheus Operator detects the `ServiceMonitor` resource and updates Prometheus's scraping target list in-memory. Prometheus begins scraping the python web service endpoints on the `/metrics` path every 10 seconds, registering application statistics.

#### Example 5: Implementing Horizontal Pod Autoscaler (HPA) and Vertical Pod Autoscaler (VPA)
*   **Context & Objectives:** Configure the HPA to scale an API gateway out based on CPU usage, and the VPA to scale a background worker process up based on memory requirements.
*   **Design Trade-offs:** HPA and VPA are used on separate workloads to avoid scaling conflicts, allowing the cluster to optimize both performance and resource utilization.
*   **Implementation:**
    `hpa-api.yaml`
    ```yaml
    apiVersion: autoscaling/v2
    kind: HorizontalPodAutoscaler
    metadata:
      name: gateway-hpa
    spec:
      scaleTargetRef:
        apiVersion: apps/v1
        kind: Deployment
        name: api-gateway
      minReplicas: 2
      maxReplicas: 10
      metrics:
      - type: Resource
        resource:
          name: cpu
          target:
            type: Utilization
            averageUtilization: 75
    ---
    `vpa-worker.yaml`
    apiVersion: autoscaling.k8s.io/v1
    kind: VerticalPodAutoscaler
    metadata:
      name: worker-vpa
    spec:
      targetRef:
        apiVersion: apps/v1
        kind: Deployment
        name: data-worker
      updatePolicy:
        updateMode: "Auto"
    ```
*   **Behavioral Analysis:**
    If the API gateway's CPU utilization exceeds 75%, the HPA controller scales the deployment out, creating up to 10 replicas. The VPA monitors the data-worker's real-time memory usage and automatically adjusts its container resource requests and limits, restarting the Pod if more memory is required.
"""

M5_EXERCISE = r"""### Practical Laboratories & Hands-On Exercises

#### Lab 1: Deploying a Multi-Probe Container to Prevent Downtime
*   **Objective:** Deploy an application container with liveness and readiness probes, and verify that traffic is routed safely.
*   **Prerequisites:** Access to a running Kubernetes cluster.
*   **Step-by-Step Instructions:**
    1. Create a file named `probe-app.yaml`:
       ```yaml
       apiVersion: v1
       kind: Pod
       metadata:
         name: probe-sandbox-pod
         labels:
           app: probe-web
       spec:
         containers:
         - name: web
           image: nginx:1.25.3
           ports:
           - containerPort: 80
           readinessProbe:
             httpGet:
               path: /
               port: 80
             periodSeconds: 5
           livenessProbe:
             httpGet:
               path: /
               port: 80
             periodSeconds: 10
       ```
    2. Apply the manifest: `kubectl apply -f probe-app.yaml`
    3. Verify that the Pod transitions to the `Running` state and the probes pass.
*   **Deterministic Verification Test:**
    Check the Pod's status details and events: `kubectl describe pod probe-sandbox-pod`
    *   **Expected Output:**
        The output status should show: `Conditions: ... Ready: True` and no warning events from the liveness or readiness probes.
*   **Troubleshooting Lab-Specific Issues:**
    If the Pod is running but remains stuck in a `0/1` ready state, verify that the readiness probe path and port are correct and matches what the container is listening on.

#### Lab 2: Troubleshooting a Liveness Probe Boot Loop
*   **Objective:** Diagnose and fix a container stuck in a reboot loop due to misconfigured liveness probes.
*   **Prerequisites:** Completed Lab 1.
*   **Step-by-Step Instructions:**
    1. Create a file named `looping-app.yaml` with an invalid liveness probe path `/invalid-check`:
       ```yaml
       apiVersion: v1
       kind: Pod
       metadata:
         name: booting-loop-pod
       spec:
         containers:
         - name: web-server
           image: nginx:1.25.3
           livenessProbe:
             httpGet:
               path: /invalid-check
               port: 80
             periodSeconds: 5
       ```
    2. Apply the manifest: `kubectl apply -f looping-app.yaml`
    3. Monitor the Pod status and note that the restart count continues to increment.
*   **Deterministic Verification Test:**
    Retrieve the container termination events: `kubectl describe pod booting-loop-pod`
    *   **Expected Output:**
        The events log must display warning lines: `Warning Unhealthy ... Liveness probe failed: HTTP probe failed with statuscode: 404` followed by container restart events.
*   **Troubleshooting Lab-Specific Issues:**
    To resolve the boot loop, update the liveness probe path back to a valid URL (like `/`) and re-apply the manifest.

#### Lab 3: Configuring Grafana Loki to Search and Filter Logs
*   **Objective:** Run dynamic queries in the Grafana Loki console to search and filter container log outputs.
*   **Prerequisites:** Prometheus-Operator and Loki installed on your cluster.
*   **Step-by-Step Instructions:**
    1. Establish a local tunnel to the Grafana service port:
       `kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring`
    2. Log in to the Grafana Web UI (default credentials usually `admin` / `prom-operator`).
    3. Open the **Explore** tab and select the **Loki** datasource.
    4. Write a LogQL query to search logs from your Nginx containers:
       `{container="web"}`
    5. Filter the logs to show only warning or error entries:
       `{container="web"} |= "error"`
*   **Deterministic Verification Test:**
    Run the query and inspect the output log lines.
    *   **Expected Output:**
        The Grafana UI should display a log graph panel and return matching log lines containing the keyword "error" along with container metadata tags.
*   **Troubleshooting Lab-Specific Issues:**
    If Loki has no data, verify that FluentBit is running as a DaemonSet and that its configuration points to the correct Loki service address and port.

#### Lab 4: Creating a Prometheus ServiceMonitor to Scrape Web Application Metrics
*   **Objective:** Create a ServiceMonitor resource to dynamically discover and scrape metrics from an application.
*   **Prerequisites:** Prometheus Operator installed in your cluster.
*   **Step-by-Step Instructions:**
    1. Deploy a web application that exposes metrics on port 8080 and `/metrics`.
    2. Create a Service named `app-metrics-service` on port 8080, labeled with `monitoring=active`.
    3. Create a ServiceMonitor manifest named `metrics-sm.yaml`:
       ```yaml
       apiVersion: monitoring.coreos.com/v1
       kind: ServiceMonitor
       metadata:
         name: app-sandbox-monitor
         namespace: monitoring
         labels:
           release: prometheus-stack
       spec:
         selector:
           matchLabels:
             monitoring: active
         namespaceSelector:
           matchNames:
           - default
         endpoints:
         - port: http
           path: /metrics
           interval: 10s
       ```
    4. Apply the ServiceMonitor manifest: `kubectl apply -f metrics-sm.yaml`
*   **Deterministic Verification Test:**
    Verify the ServiceMonitor has discovered the service endpoints:
    `kubectl get servicemonitors -n monitoring app-sandbox-monitor`
    *   **Expected Output:**
        The ServiceMonitor should be active and successfully registered under target configurations.
*   **Troubleshooting Lab-Specific Issues:**
    Verify that your Service's port name matches the port name defined in the ServiceMonitor endpoint section exactly.

#### Lab 5: Establishing Alertmanager Routing Rules for Production Outages
*   **Objective:** Deploy Alertmanager routing rules to route critical alerts to a slack channel or a pager.
*   **Prerequisites:** Completed Lab 2.
*   **Step-by-Step Instructions:**
    1. Create an Alertmanager configuration manifest named `alertmanager-config.yaml`:
       ```yaml
       apiVersion: monitoring.coreos.com/v1alpha1
       kind: AlertmanagerConfig
       metadata:
         name: slack-alerts-route
         namespace: monitoring
       spec:
         route:
           groupBy: ['alertname']
           groupWait: 30s
           groupInterval: 5m
           repeatInterval: 12h
           receiver: 'slack-notifications'
         receivers:
         - name: 'slack-notifications'
           slackConfigs:
           - channel: '#prod-alerts'
             apiURL:
               name: slack-webhook-secret
               key: api-url
       ```
    2. Apply the AlertmanagerConfig manifest.
*   **Deterministic Verification Test:**
    Verify the Alertmanager configuration status: `kubectl get alertmanagerconfigs -n monitoring`
    *   **Expected Output:**
        The AlertmanagerConfig must be active and successfully validated.
*   **Troubleshooting Lab-Specific Issues:**
    Verify that the Slack webhook secret (`slack-webhook-secret`) exists in the `monitoring` namespace and has a valid API URL key.
"""

M5_INSIGHT = r"""### Professional Interview & Advanced Deep Dive

#### Q1: What is the SRE math behind SLO availability targets, and how do you calculate a monthly error budget?
*   **Answer:** An SLO (Service Level Objective) defines target availability over a specific time window. SRE teams use mathematical models to calculate the allowable downtime (the error budget) for a given target. For a 99.9% availability target over a 30-day month (43,200 minutes), the error budget is calculated as $43200 \times (1 - 0.999) = 43.2 \text{ minutes}$ of total downtime. Maintaining this target requires proactive alerts, automated failovers, and robust self-healing configurations.

#### Q2: What is the technical difference between liveness and readiness probes, and what happens if they are misconfigured?
*   **Answer:** A `readinessProbe` determines if a container is ready to accept network traffic. If it fails, the controller removes the Pod IP from Services, stopping traffic routing but keeping the container running. A `livenessProbe` determines if the container process is frozen or hung. If it fails, the kubelet immediately terminates the container process and triggers a restart. If they are misconfigured, or if their checks overlap, it can cause premature container restarts or route traffic to uninitialized Pods.

#### Q3: How does the Prometheus Operator leverage ServiceMonitors to automate scraping configuration?
*   **Answer:** Static Prometheus setups require manual edits to the main scraping configuration file for every new service endpoint. The Prometheus Operator automates this using Custom Resources. SREs define a `ServiceMonitor` specifying label selectors and namespaces. The operator automatically monitors the API Server for matching Services, compiles their endpoint lists, and updates Prometheus's scraping targets in-memory without restarting the server.

#### Q4: Why is running the metrics-server alone not sufficient for long-term production monitoring and alerting?
*   **Answer:** The metrics-server is a lightweight collector designed to aggregate only real-time CPU and memory usage statistics. It does not store historical metrics, nor does it generate cluster-state telemetry or support complex alerts. It is only used to drive autoscaling (HPA) and CLI commands. Production environments require a full observability suite like Prometheus and Grafana for historical analysis, long-term metrics storage, and advanced alerting.

#### Q5: How does the Vertical Pod Autoscaler (VPA) adjust container resources dynamically, and what is its main limitation?
*   **Answer:** The VPA monitors container CPU and memory usage and automatically adjusts the resource requests and limits in the Pod specification. The VPA's main limitation is that, in most cluster configurations, applying resource updates requires restarting the container process, which can cause temporary application downtime if there are no other active replicas.

### Academic & Professional Alignment
Mastering observability, container probes, and alerting rules is a core requirement on the CKA and CKAD exams. SREs must understand these monitoring and reliability principles to design, build, and maintain production-grade environments that meet strict uptime targets.
"""

# =====================================================================
# MODULE 6: INFRASTRUCTURE AS CODE & BARE-METAL CLUSTER PROVISIONING
# =====================================================================

M6_THEORY = r"""### Guided Conceptual Walkthrough
Imagine you are building a physical research laboratory. Historically, engineers had to manually assemble the building structure, route electrical pipes, and configure tables (manually provisioning cloud resources and installing software packages). This was slow, expensive, and difficult to repeat. 

To automate the entire process, you implement two modern design approaches:
*   **Terraform (IaC)**: Write a declarative structural layout blueprint (**Terraform Configurations**). When you execute the blueprint, an automated building machine immediately provisions the land, builds the walls, and sets up managed research rooms (**AWS EKS**, **Google GKE**, or **Azure AKS**).
*   **Kubeadm**: Once the physical structure is ready, you use a standard installation handbook (**kubeadm**) to configure the central power systems (**Control Plane Nodes**) and link other utility rooms (**Worker Nodes**) to the facility grid.

### Architectural, Lifecycle & Flow Blueprints

```mermaid
graph TD
    TF[Terraform CLI] -->|Provider API| GKE[Google GKE / AWS EKS]
    Kubeadm[Kubeadm Tool] -->|Bootstrap| Node[Control Plane Node]
    Node -->|Join Script| Worker[Worker Node]
```

```mermaid
sequenceDiagram
    autonumber
    Admin->>Node: kubeadm init
    Node->>Node: Generate Certificates
    Node->>Node: Bootstrap API Server
    Admin->>Worker: kubeadm join --token
    Worker->>Node: Handshake and Register
```

### Under-the-Hood Mechanics & Internal Operations
At the system execution layer, Terraform manages resources using a declarative state model. When you apply a configuration, the engine parses the code, compares it against the active state file (`terraform.tfstate`), calculates a resource delta-plan, and communicates with cloud provider APIs to provision managed services (like AWS EKS or GCP GKE) using API endpoints. 

For local or bare-metal cluster creation, `kubeadm` automates the bootstrapping process through distinct phases:
1. `init`: Generates self-signed CA certificates, writes kubeconfig configuration files, and spawns the control plane components (API Server, Controller Manager, Scheduler, etcd) as static Pods managed directly by the host node's local `kubelet` agent.
2. `join`: Initializes worker nodes using a bootstrap token handshake, registers them with the API Server, and joins them to the cluster.

### Deep-Dive Reference (Advanced Context)
<details>
<summary>Kubeadm Init Phases and TLS Certificate Management</summary>
The kubeadm bootstrapping engine is highly structured. During the `init` phase, the engine automatically generates cryptographic certificates (stored in `/etc/kubernetes/pki/`) to secure all control plane communication paths. It then generates the bootstrap tokens used by worker nodes to authenticate and complete the handshake during the `join` phase, establishing a secure TLS communication boundary.
</details>

### Systemic Failure Modes & Boundary Violations
*   **Failure Mode 1: Concurrent Terraform Lock Collision (State File Locked)**
    *   **Symptom:** Running `terraform apply` fails with the error `Error acquiring state lock: Lock Info: ID: ...`.
    *   **Root Cause:** Another developer or a CI/CD runner is executing a Terraform command concurrently, locking the remote state file (e.g., in DynamoDB or GCS) to prevent state file corruption.
    *   **Resolution:** Force unlock the state file if you are absolutely sure no other pipeline is active:
        ```bash
        terraform force-unlock <lock-id>
        ```

*   **Failure Mode 2: Kubeadm Join Token Expired**
    *   **Symptom:** Running `kubeadm join` on a new worker node fails with authentication or handshake timeout errors.
    *   **Root Cause:** The bootstrap token generated during the initial `kubeadm init` phase has reached its default lifetime limit (typically 24 hours) and has expired.
    *   **Resolution:** Generate a new bootstrap token and retrieve the updated join script from your control plane node:
        ```bash
        kubeadm token create --print-join-command
        ```

*   **Failure Mode 3: Calico CNI CIDR Mismatch (Calico Crashes on Node Join)**
    *   **Symptom:** New worker nodes join the cluster successfully, but all network CNI Pods (like Calico or Flannel) are crashing, and Pod-to-Pod communication is broken.
    *   **Root Cause:** The CIDR address block defined in the CNI configuration does not match the IP block specified in the `kubeadm init --pod-network-cidr` command.
    *   **Resolution:** Verify the pod network CIDR used during initialization and update your CNI configuration manifests to match:
        ```bash
        kubeadm config view | grep podSubnet
        # Update your Calico deployment YAML to match the CIDR IP block exactly
        ```

### Traceability Schema Check
All Infrastructure as Code systems (Terraform), cloud provider integrations (AWS EKS, GKE), and cluster bootstrapping commands (`kubeadm`) used below are conceptually mapped to this section.
"""

M6_COMMANDS = r"""### Technical & Syntax Reference Manual
Below are the essential commands for provisioning cloud resources via Terraform and bootstrapping clusters using kubeadm.

*   **Terraform IaC Lifecycle Controls:**
    ```bash
    # Initialize the working directory and download the required cloud provider plugins
    terraform init

    # Create an execution plan to preview resource changes before applying them
    terraform plan

    # Apply the configurations and provision resources on the cloud provider
    terraform apply -auto-approve
    ```

*   **Kubeadm Bootstrapping Controls:**
    ```bash
    # Initialize the control plane master node with a specific pod network CIDR
    sudo kubeadm init --pod-network-cidr=192.168.0.0/16

    # Generate a new bootstrap token and print the complete join command
    kubeadm token create --print-join-command
    ```

### Anatomy & Boundary Table
| Variable / Parameter / Keyword Name | Expected Type / Allowed Values | Default Value / Operating Domain | Strict Structural Constraints |
| :--- | :--- | :--- | :--- |
| `pod-network-cidr` | CIDR IP address block | N/A | Must match the target subnet defined in your CNI configuration file exactly. |
| `terraform.tfstate` | JSON state file | Local filesystem | Stores real-time resource state; use a remote backend with lock support in production. |
| `kubeadm join --token` | String | N/A | Must be a valid, unexpired bootstrap token generated by the control plane. |
| `apiserver-advertise-address` | IP Address | N/A | The IP address that the API Server will advertise and listen on. |
"""

M6_EXAMPLES = r"""### Real-World Case Studies & Applied Examples

#### Example 1: Provisioning a Managed Google GKE Cluster with Terraform
*   **Context & Objectives:** Configure a declarative Terraform blueprint to provision a highly-available, managed Google Kubernetes Engine (GKE) cluster in a specific zone.
*   **Design Trade-offs:** Terraform is chosen over manual gcloud CLI commands to provide repeatable infrastructure-as-code and enable version-controlled updates.
*   **Implementation:**
    `gke-cluster.tf`
    ```hcl
    terraform {
      required_providers {
        google = {
          source  = "hashicorp/google"
          version = "~> 4.0"
        }
      }
    }

    provider "google" {
      project = "sandbox-project-123"
      region  = "us-central1"
    }

    resource "google_container_cluster" "primary" {
      name     = "gke-production-cluster"
      location = "us-central1-a"

      # Start with a minimal node pool and manage it separately
      initial_node_count       = 1
      remove_default_node_pool = true
    }

    resource "google_container_node_pool" "primary_nodes" {
      name       = "custom-node-pool"
      location   = "us-central1-a"
      cluster    = google_container_cluster.primary.name
      node_count = 3

      node_config {
        preemptible  = false
        machine_type = "e2-standard-4"
        disk_size_gb = 50

        oauth_scopes = [
          "https://www.googleapis.com/auth/cloud-platform"
        ]
      }
    }
    ```
*   **Behavioral Analysis:**
    Running `terraform apply` reads the GKE configuration and calculates the resource plan. The Google provider executes HTTPS API requests targeting the Google Cloud Container API, which provisions a managed control plane and a pool of three worker nodes in the target zone.

#### Example 2: Provisioning a Managed AWS EKS Cluster with Terraform
*   **Context & Objectives:** Configure a declarative Terraform blueprint to provision an Amazon Elastic Kubernetes Service (EKS) cluster with managed node groups.
*   **Design Trade-offs:** Using Terraform managed modules simplifies complex IAM role, security group, and VPC subnet configurations required by AWS EKS.
*   **Implementation:**
    `eks-cluster.tf`
    ```hcl
    module "eks" {
      source  = "terraform-aws-modules/eks/aws"
      version = "~> 19.0"

      cluster_name    = "eks-production-cluster"
      cluster_version = "1.28"

      vpc_id     = "vpc-0123456789abcdef"
      subnet_ids = ["subnet-abc12345", "subnet-def67890"]

      eks_managed_node_groups = {
        general_nodes = {
          min_size     = 2
          max_size     = 5
          desired_size = 3

          instance_types = ["t3.medium"]
          capacity_type  = "ON_DEMAND"
        }
      }
    }
    ```
*   **Behavioral Analysis:**
    The Terraform AWS EKS module coordinates the provisioning steps. It creates the required IAM roles, registers security groups, launches the EKS control plane, and spins up an autoscaling managed node group of `t3.medium` instances in the specified subnets.

#### Example 3: Bootstrapping a Bare-Metal Control Plane using Kubeadm
*   **Context & Objectives:** Bootstrap a secure Kubernetes control plane master node on a bare-metal server, initializing the static API Server, scheduler, and etcd.
*   **Design Trade-offs:** `kubeadm` is chosen over manual control plane installation because it automates certificate generation, static Pod configurations, and security bootstrapping.
*   **Implementation:**
    ```bash
    # Prepare the node and initialize the control plane
    sudo kubeadm init \
      --apiserver-advertise-address=192.168.1.50 \
      --pod-network-cidr=10.244.0.0/16
    ```
*   **Behavioral Analysis:**
    The `kubeadm` init command executes. It generates CA certificates in `/etc/kubernetes/pki/`, writes kubeconfig configurations to `/etc/kubernetes/`, and creates static manifest files in `/etc/kubernetes/manifests/`. The local `kubelet` agent immediately detects the manifests and launches the core control plane components as static Pods.

#### Example 4: Creating a Remote State Storage Backend with Terraform
*   **Context & Objectives:** Configure a secure, remote backend storage system for Terraform state files, enabling collaborative development and state locking.
*   **Design Trade-offs:** Using a Google Cloud Storage (GCS) backend with state locking prevents concurrent executions from corrupting the Terraform state.
*   **Implementation:**
    `backend.tf`
    ```hcl
    terraform {
      backend "gcs" {
        bucket  = "terraform-state-bucket-gke"
        prefix  = "state/gke-prod"
      }
    }
    ```
*   **Behavioral Analysis:**
    When Terraform is executed, it retrieves the current state file from the GCS bucket and locks the object. Any concurrent executions from other developers or CI/CD pipelines are blocked until the active apply command completes and releases the lock, protecting state consistency.

#### Example 5: Scaling Node Pool Sizes Declaratively with Terraform
*   **Context & Objectives:** Scale up the active node pool size of a GKE cluster to handle an upcoming traffic spike.
*   **Design Trade-offs:** Modifying the GKE node count in Terraform is preferred over manual dashboard scaling to ensure the cluster's physical state remains synchronized with the code.
*   **Implementation:**
    ```hcl
    resource "google_container_node_pool" "primary_nodes" {
      name       = "custom-node-pool"
      cluster    = google_container_cluster.primary.name
      # Increase the node count to 10
      node_count = 10
    }
    ```
*   **Behavioral Analysis:**
    Modifying the node count from 3 to 10 and running `terraform apply` updates the resource plan. Terraform detects the change and executes GKE API requests to scale up the worker node pool, adding 7 new worker nodes to the cluster.
"""

M6_EXERCISE = r"""### Practical Laboratories & Hands-On Exercises

#### Lab 1: Initializing a Local Kubernetes Control Plane via Kubeadm
*   **Objective:** Bootstrap a single-node Kubernetes control plane master node using kubeadm.
*   **Prerequisites:** Access to a clean Linux VM or bare-metal server with Docker or containerd pre-installed.
*   **Step-by-Step Instructions:**
    1. Log in to your control plane node as root or with sudo permissions.
    2. Disable swap on your system: `sudo swapoff -a`
    3. Initialize the control plane master node with a specific network CIDR:
       ```bash
       sudo kubeadm init --pod-network-cidr=10.244.0.0/16
       ```
    4. Configure your user context and kubeconfig to access the API Server:
       ```bash
       mkdir -p $HOME/.kube
       sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
       sudo chown $(id -u):$(id -g) $HOME/.kube/config
       ```
*   **Deterministic Verification Test:**
    Verify the health and status of control plane components: `kubectl get nodes`
    *   **Expected Output:**
        The output must display your master control plane node with status `NotReady` (since we have not installed a CNI yet) along with system versions.
*   **Troubleshooting Lab-Specific Issues:**
    If the initialization fails with container runtime errors, verify that swap is disabled and that your container runtime service (like containerd) is active.

#### Lab 2: Joining Worker Nodes using Bootstrap Tokens
*   **Objective:** Generate a bootstrap token and join a worker node to your initialized control plane.
*   **Prerequisites:** Completed Lab 1 and access to a clean worker node VM.
*   **Step-by-Step Instructions:**
    1. On your master control plane node, generate a new bootstrap join token:
       ```bash
       kubeadm token create --print-join-command
       ```
    2. Copy the printed command containing the token and CA hash key.
    3. Log in to your clean worker node VM, disable swap, and run the join command as root:
       ```bash
       sudo kubeadm join <control-plane-ip>:6443 --token <token> --discovery-token-ca-cert-hash sha256:<hash>
       ```
*   **Deterministic Verification Test:**
    On the master control plane node, check the list of registered nodes: `kubectl get nodes`
    *   **Expected Output:**
        The list should display two nodes, including your newly joined worker node.
*   **Troubleshooting Lab-Specific Issues:**
    If the join command fails with connection timeout errors, verify that there is no firewall blocking port 6443 on the master control plane node.

#### Lab 3: Deploying a Calico CNI to Initialize Cluster Networking
*   **Objective:** Install the Calico CNI plugin to configure network routing and allow nodes to transition to the `Ready` state.
*   **Prerequisites:** Completed Lab 2.
*   **Step-by-Step Instructions:**
    1. Log in to your master control plane node.
    2. Apply the Calico operator manifest to the cluster:
       ```bash
       kubectl create -f https://raw.githubusercontent.com/projectcalico/calico/v3.26.1/manifests/tigera-operator.yaml
       ```
    3. Apply the custom resources manifest to configure Calico:
       ```bash
       kubectl create -f https://raw.githubusercontent.com/projectcalico/calico/v3.26.1/manifests/custom-resources.yaml
       ```
    4. Wait for the Calico CNI Pods to initialize in the `calico-system` namespace.
*   **Deterministic Verification Test:**
    Verify the status of your worker nodes: `kubectl get nodes`
    *   **Expected Output:**
        Both master and worker nodes should transition and show status as `Ready`.
*   **Troubleshooting Lab-Specific Issues:**
    If nodes remain in `NotReady`, run `kubectl get pods -A` to verify if Calico pods are crashing, which usually indicates a CIDR mismatch with the `--pod-network-cidr` used during `kubeadm init`.

#### Lab 4: Declaratively Provisioning a GKE Cluster via Terraform
*   **Objective:** Configure and execute a Terraform blueprint to provision a managed GKE cluster on Google Cloud.
*   **Prerequisites:** Google Cloud account, a project ID, and the Terraform CLI pre-installed.
*   **Step-by-Step Instructions:**
    1. Write your `gke-cluster.tf` file (from Example 1).
    2. Initialize the working directory and plugins: `terraform init`
    3. Generate and verify the execution plan: `terraform plan`
    4. Apply the configuration to provision the GKE cluster: `terraform apply`
*   **Deterministic Verification Test:**
    Verify the GKE cluster status using Gcloud CLI: `gcloud container clusters list`
    *   **Expected Output:**
        The output must display your GKE cluster with its region, version, and status set to `RUNNING`.
*   **Troubleshooting Lab-Specific Issues:**
    If provisioning fails with API errors, verify that you have enabled the Kubernetes Engine API in your Google Cloud Console and that your local credentials have sufficient IAM permissions.

#### Lab 5: Tearing Down Terraform Resources Safely
*   **Objective:** Destroy and clean up all provisioned cloud resources securely using Terraform.
*   **Prerequisites:** Completed Lab 4.
*   **Step-by-Step Instructions:**
    1. Open a terminal in the directory containing your GKE Terraform configuration.
    2. Review the resources that will be removed by running a destroy plan:
       `terraform plan -destroy`
    3. Destroy the resources: `terraform destroy`
*   **Deterministic Verification Test:**
    Verify the cluster has been removed: `gcloud container clusters list`
    *   **Expected Output:**
        The command should return empty results, and no active nodes or GKE resources should be billed on your project account.
*   **Troubleshooting Lab-Specific Issues:**
    If the destroy command fails or hangs, verify that you did not manually delete resources from the Gcloud Console, which can cause state mismatches that must be resolved in the code.
"""

M6_INSIGHT = r"""### Professional Interview & Advanced Deep Dive

#### Q1: What is the benefit of managing Kubernetes node pools declaratively using Infrastructure as Code (IaC) like Terraform?
*   **Answer:** Declarative IaC ensures that your cloud infrastructure remains version-controlled, repeatable, and documented. If a cluster node pool is corrupted, you can easily destroy and re-create it to identical specifications within minutes. Additionally, you can scale cluster node pools up or down, update OS configurations, or manage cluster versions securely by updating your code and running a pull request, bypassing dangerous manual operations in the cloud dashboard.

#### Q2: What are the static Pod configurations generated by kubeadm init, and how does the host node manage them?
*   **Answer:** During the `init` phase, `kubeadm` writes static manifest files to `/etc/kubernetes/manifests/` for the core control plane components (API Server, Controller Manager, Scheduler, etcd). The node's local `kubelet` agent watches this directory directly. If any of these static manifest files are added or modified, the kubelet immediately launches or restarts the corresponding components as containerized Pods, bypassed the API Server scheduling layer entirely.

#### Q3: Why does `kubeadm join` expire, and how do you secure bootstrap tokens in production?
*   **Answer:** Bootstrap tokens are sensitive credentials that grant worker nodes permission to request TLS certificates and join the cluster. To minimize security exposure, `kubeadm` configures these tokens to expire after 24 hours by default. In production, you should rotate these tokens regularly, use short TTL values, and generate new tokens dynamically during VM provisioning inside automated node autoscaling scripts.

#### Q4: How does a remote Terraform backend with locking prevent state file corruption?
*   **Answer:** When multiple developers or pipelines execute Terraform concurrently on a shared project, they can read and write the state file at the same time, leading to conflicts and file corruption. A remote backend with state locking (using DynamoDB on AWS or GCS on Google Cloud) locks the state file whenever an execution begins. Any concurrent commands are immediately blocked with an error, ensuring only one pipeline can write changes at any given time.

#### Q5: What is the difference between kubeadm and kubespray, and when should you use each?
*   **Answer:** `kubeadm` is a focused, CLI-driven cluster bootstrapping tool designed to configure control planes and join worker nodes. It does not handle provisioning VMs, configuring operating systems, or managing multi-node load balancers. `kubespray` is an Ansible-driven automation suite that manages the entire cluster lifecycle, from VM provisioning and OS package configuration to load balancer installation and cluster bootstrapping, making it ideal for bare-metal or complex on-premise deployments.

### Academic & Professional Alignment
Understanding cluster bootstrapping, certificate generation, and declarative infrastructure provisioning is highly valued on advanced DevOps roles. Demonstrating proficiency in using Terraform to provision managed services (like EKS or GKE) and `kubeadm` to manage bare-metal clusters represents a key focus area on enterprise platfom engineering interviews.
"""

# =====================================================================
# FINAL CURRICULUM BINDINGS
# =====================================================================

CURRICULUM_DATA = [
    {
        "id": 1,
        "title": "Module 1: Advanced Workloads, Storage Orchestration & Node Scheduling",
        "theory": M1_THEORY,
        "commands": M1_COMMANDS,
        "examples": M1_EXAMPLES,
        "exercise": M1_EXERCISE,
        "insight": M1_INSIGHT,
    },
    {
        "id": 2,
        "title": "Module 2: Application Networking & Ingress Controllers",
        "theory": M2_THEORY,
        "commands": M2_COMMANDS,
        "examples": M2_EXAMPLES,
        "exercise": M2_EXERCISE,
        "insight": M2_INSIGHT,
    },
    {
        "id": 3,
        "title": "Module 3: Security, RBAC & Resource Boundaries",
        "theory": M3_THEORY,
        "commands": M3_COMMANDS,
        "examples": M3_EXAMPLES,
        "exercise": M3_EXERCISE,
        "insight": M3_INSIGHT,
    },
    {
        "id": 4,
        "title": "Module 4: Enterprise Configuration Management & GitOps",
        "theory": M4_THEORY,
        "commands": M4_COMMANDS,
        "examples": M4_EXAMPLES,
        "exercise": M4_EXERCISE,
        "insight": M4_INSIGHT,
    },
    {
        "id": 5,
        "title": "Module 5: Production Observability, Alerting & SRE Principles",
        "theory": M5_THEORY,
        "commands": M5_COMMANDS,
        "examples": M5_EXAMPLES,
        "exercise": M5_EXERCISE,
        "insight": M5_INSIGHT,
    },
    {
        "id": 6,
        "title": "Module 6: Infrastructure as Code & Bare-Metal Cluster Provisioning",
        "theory": M6_THEORY,
        "commands": M6_COMMANDS,
        "examples": M6_EXAMPLES,
        "exercise": M6_EXERCISE,
        "insight": M6_INSIGHT,
    },
]