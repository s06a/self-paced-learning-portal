COURSE_ID = "cka_ultimate_mastery"
COURSE_TITLE = "Certified Kubernetes Administrator (CKA)"
COURSE_DESCRIPTION = (
    "The ultimate hands-on curriculum spanning 9 core modules, covering every CKA domain "
    "in thorough, production-grade detail. Spans from fundamental API objects to highly "
    "advanced cluster architecture, upgrades, networking, and system troubleshooting."
)

# =====================================================================
# MODULE 1: KUBERNETES CORE ARCHITECTURE, DECLARATIVE PRIMITIVES, & CLI SPEED
# =====================================================================

M1_THEORY = r"""### Guided Conceptual Walkthrough
In a production-ready Kubernetes cluster, management operates on a declarative model. Think of a automated physical warehouse. Instead of having a manager manually direct each worker, the managers write a master manifest description detailing the desired state of the warehouse floor (**Declarative YAML**). 

The warehouse control room (**Control Plane**) continuously monitors the floor. If a machine malfunctions or crashes (**Pod Failure**), the supervisor (**kube-controller-manager**) detects the drift and immediately requests a replacement. The supervisor works with the scheduler (**kube-scheduler**) to assign the machine to the best available assembly line station (**Worker Node**).

In engineering terms, we translate this warehouse model directly into cluster components. The `kube-apiserver` acts as the central communication gateway. All state metadata is persisted across a consistent, distributed database ledger (**etcd**). On the worker nodes, the `kubelet` agent receives Pod declarations from the API Server and communicates with the local container runtime (CRI) to launch, maintain, and verify container runtimes.

### Architectural, Lifecycle & Flow Blueprints

```mermaid
graph TD
    subgraph Control Plane
        API[API Server] --> ETCD[(etcd Database)]
        SCH[Scheduler] --> API
        KCM[Controller Manager] --> API
    end
    subgraph Worker Node
        KUBELET[Kubelet] -->|Monitors Pods| API
        KP[Kube-Proxy] -->|Manages Routing| API
        CR[Container Runtime] -->|Spawns Containers| KUBELET
    end
```

```mermaid
sequenceDiagram
    autonumber
    User->>API: kubectl apply -f pod.yaml
    API->>ETCD: Commit State
    KCM->>API: Detect Drift
    SCH->>API: Score & Bind Node
    API->>KUBELET: Instruct Pod Spawning
    KUBELET->>CR: Initialize Containers
```

### Under-the-Hood Mechanics & Internal Operations
The Kubernetes API Server is a stateless REST server that processes incoming HTTP/JSON payloads over secure TLS channels. When a user runs a command like `kubectl apply`, the request undergoes Authentication, Authorization, and Admission Control before any state transitions are executed. 

Once approved, the API Server writes the updated configuration to `etcd` using a secure gRPC interface. `etcd` uses Multi-Version Concurrency Control (MVCC) to ensure transactional consistency across the distributed cluster. 

The `kube-scheduler` detects newly created Pods with empty `nodeName` fields. It filters available worker nodes based on resource capacity (Predicates) and scores them based on affinity rules (Priorities). Once a node is selected, the scheduler writes a binding object back to the API Server, which notifies the target node's `kubelet` to pull the image and spawn the container process.

### Deep-Dive Reference (Advanced Context)
<details>
<summary>Declarative Configuration, Drift Detection, and MVCC</summary>
The cluster state is managed using a declarative model where resources are defined as API objects. Each object contains metadata labels used for grouping, selectors used by Services and ReplicaSets to target Pods, and a specification defining the desired state. The `kube-controller-manager` runs continuous background loops comparing this specification against the live state (drift detection), sending corrective requests to the API Server if deviations are found.
</details>

### Systemic Failure Modes & Boundary Violations
*   **Failure Mode 1: API Server Unreachable (Connection Refused)**
    *   **Symptom:** Running `kubectl` commands returns the error `The connection to the server localhost:8080 was refused`.
    *   **Root Cause:** The kubeconfig file (`~/.kube/config`) is missing, misconfigured, or the client context is targeting an inactive API Server endpoint.
    *   **Resolution:** Verify that your active kubeconfig path and context are configured correctly:
        ```bash
        export KUBECONFIG=$HOME/.kube/config
        kubectl config view
        ```

*   **Failure Mode 2: etcd Storage Space Exhaustion**
    *   **Symptom:** The API Server rejects all write operations, and etcd logs report `etcdserver: mvcc: database space exceeded`.
    *   **Root Cause:** The etcd database file has reached its maximum size limit (typically 2GB) due to fragmented keys or missing historical compaction policies.
    *   **Resolution:** Compact etcd keys, run defragmentation, and clear the database alarm:
        ```bash
        etcdctl --endpoints=https://127.0.0.1:2379 compact 1000
        etcdctl --endpoints=https://127.0.0.1:2379 defrag
        etcdctl --endpoints=https://127.0.0.1:2379 alarm disarm
        ```

*   **Failure Mode 3: Kubelet Communication Outage**
    *   **Symptom:** Nodes enter a `NotReady` state, and Pods remain stuck in a `Terminating` or `Unknown` state.
    *   **Root Cause:** The `kubelet` agent on the worker node has crashed, stopped, or network issues are preventing it from communicating with the API Server.
    *   **Resolution:** Log in to the worker node and verify the status of the kubelet service:
        ```bash
        sudo systemctl status kubelet
        sudo systemctl restart kubelet
        ```

### Traceability Schema Check
All core components (Control Plane, Worker Node agents), declarative configuration manifests, and basic command-line parameters used below are conceptually defined in this section.
"""

M1_COMMANDS = r"""### Technical & Syntax Reference Manual
Below are the essential operations for managing declarative manifests, resources, and contexts using the command-line utility.

*   **API Discovery and Resource Extraction:**
    ```bash
    # List all supported API resources, shortnames, and API groups
    kubectl api-resources

    # Generate a baseline dry-run Pod manifest without creating it in the cluster
    kubectl run test-nginx --image=nginx:1.25.1 --dry-run=client -o yaml > pod-template.yaml
    ```

*   **Resource Label and Namespace Controls:**
    ```bash
    # Create a separate, isolated namespace boundary
    kubectl create namespace sandbox-env

    # Apply or update a metadata label on an active Pod resource
    kubectl label pod test-nginx tier=frontend --overwrite
    ```

### Anatomy & Boundary Table
| Variable / Parameter / Keyword Name | Expected Type / Allowed Values | Default Value / Operating Domain | Strict Structural Constraints |
| :--- | :--- | :--- | :--- |
| `apiVersion` | String (e.g., `v1`, `apps/v1`) | N/A (Required in YAML) | Must match a valid API group and version registered with the API Server. |
| `kind` | String (e.g., `Pod`, `Namespace`) | N/A (Required in YAML) | Case-sensitive resource type declaration matching API objects. |
| `metadata.name` | String | N/A (Required in YAML) | Must be a lowercase, DNS-1123 compatible resource identifier (max 253 characters). |
| `--dry-run` | String (`client`, `server`) | `client` | Evaluates syntax and formats manifests without committing state transitions to etcd. |
"""

M1_EXAMPLES = r"""### Real-World Case Studies & Applied Examples

#### Example 1: Minimal Declarative Namespace & Pod Deployment
*   **Context & Objectives:** Deploy an isolated sandbox namespace and run a baseline Nginx web container with standard metadata labels inside that boundary.
*   **Design Trade-offs:** Namespace-scoped isolation is used instead of global cluster deployment to separate resources and prevent naming collisions.
*   **Implementation:**
    ```yaml
    apiVersion: v1
    kind: Namespace
    metadata:
      name: sandbox-env
    ---
    apiVersion: v1
    kind: Pod
    metadata:
      name: test-web-server
      namespace: sandbox-env
      labels:
        app: test-web
        tier: frontend
    spec:
      containers:
      - name: web-container
        image: nginx:1.25.1
        ports:
        - containerPort: 80
    ```
*   **Behavioral Analysis:**
    Applying this manifest triggers the API Server to register the `sandbox-env` namespace. The `test-web-server` Pod is then created inside this namespace. The scheduler scores available nodes and binds the Pod to a node, prompting the node's Kubelet to instruct containerd to pull the image and launch the container process.

#### Example 2: Multi-Container Pod with Ephemeral emptyDir Volume
*   **Context & Objectives:** Deploy an application container that writes log files to a shared directory, alongside a sidecar log collector that reads and processes those logs in real time.
*   **Design Trade-offs:** Placing both containers inside a single Pod guarantees they are scheduled on the same host node and can share storage volumes for fast, local file sharing.
*   **Implementation:**
    ```yaml
    apiVersion: v1
    kind: Pod
    metadata:
      name: web-logging-pod
      namespace: default
      labels:
        app: analytics
    spec:
      containers:
      - name: main-app
        image: alpine:3.18
        command: ["/bin/sh", "-c", "while true; do echo $(date) 'Transaction completed' >> /var/log/app/output.log; sleep 5; done"]
        volumeMounts:
        - name: shared-logs
          mountPath: /var/log/app
      - name: log-shipper
        image: alpine:3.18
        command: ["/bin/sh", "-c", "tail -n+1 -f /var/log/app/output.log"]
        volumeMounts:
        - name: shared-logs
          mountPath: /var/log/app
      volumes:
      - name: shared-logs
        emptyDir: {}
    ```
*   **Behavioral Analysis:**
    The scheduler places the Pod on a node. The Kubelet mounts an in-memory `emptyDir` volume on the host. The `main-app` container writes log data to `/var/log/app/output.log`, and the `log-shipper` sidecar container reads and streams those logs to stdout, enabling centralized log collection.

#### Example 3: Service Selector Label Mapping
*   **Context & Objectives:** Create a Service to expose an application running in Pods that carry the labels `app: auth-engine` and `tier: secure`.
*   **Design Trade-offs:** A ClusterIP Service is used to provide a stable, internal-only virtual IP address, load balancing traffic across the backing Pods.
*   **Implementation:**
    ```yaml
    apiVersion: v1
    kind: Service
    metadata:
      name: auth-service
      namespace: default
    spec:
      type: ClusterIP
      ports:
      - port: 8080
        targetPort: 8080
      selector:
        app: auth-engine
        tier: secure
    ```
*   **Behavioral Analysis:**
    The API Server registers the `auth-service`. The Endpoints controller automatically scans the namespace for Pods labeled with `app: auth-engine` and `tier: secure`, and maps their current IP addresses to the service, enabling internal load balancing.

#### Example 4: Pod Manifest with Metadata Annotations
*   **Context & Objectives:** Enforce security and compliance policies by documenting deployment metadata, contact details, and change identifiers directly in the Pod metadata.
*   **Design Trade-offs:** Annotations are used to store non-identifying metadata that cannot be used in label queries but can be read by external auditing tools.
*   **Implementation:**
    ```yaml
    apiVersion: v1
    kind: Pod
    metadata:
      name: secured-api
      namespace: default
      annotations:
        owner: "security-ops"
        slack-channel: "#sec-alerts"
        last-deployed: "2026-07-22"
        change-id: "CHG-908123"
      labels:
        app: api-core
    spec:
      containers:
      - name: api-container
        image: redis:7.0-alpine
    ```
*   **Behavioral Analysis:**
    The API Server commits the annotations to etcd. While the `app: api-core` label can be used to query the Pod, the annotations are preserved as reference metadata, allowing automated auditing tools to verify compliance.

#### Example 5: Automating Manifest Generation via Dry-Run Checks
*   **Context & Objectives:** Write an automated shell script using `kubectl` dry-run commands to generate clean, syntax-compliant YAML templates instantly.
*   **Design Trade-offs:** Generating templates using dry-run commands is preferred over writing manifests from scratch to prevent syntax errors and speed up deployments.
*   **Implementation:**
    ```bash
    #!/bin/bash
    # Generate a namespace and a Pod template automatically
    kubectl create namespace staging-api --dry-run=client -o yaml > bootstrap.yaml
    echo "---" >> bootstrap.yaml
    kubectl run staging-worker --image=python:3.11-alpine --namespace=staging-api --dry-run=client -o yaml >> bootstrap.yaml
    echo "Bootstrap manifest successfully written to bootstrap.yaml"
    ```
*   **Behavioral Analysis:**
    The script runs `kubectl` with the `--dry-run=client` flag. The CLI contacts local libraries to generate valid YAML structures without sending any API requests to the cluster, saving the output templates directly to `bootstrap.yaml`.
"""

M1_EXERCISE = r"""### Practical Laboratories & Hands-On Exercises

#### Lab 1: Namespace Creation and Pod Isolation
*   **Objective:** Create separate virtual environments and deploy isolated resources inside those boundaries.
*   **Prerequisites:** Access to a running Kubernetes cluster.
*   **Step-by-Step Instructions:**
    1. Create a namespace named `finance-sandbox`:
       ```bash
       kubectl create namespace finance-sandbox
       ```
    2. Imperatively generate a Pod manifest named `ledger-db` using image `redis:7.0-alpine` inside `finance-sandbox`:
       ```bash
       kubectl run ledger-db --image=redis:7.0-alpine -n finance-sandbox --dry-run=client -o yaml > ledger-pod.yaml
       ```
    3. Apply the generated manifest: `kubectl apply -f ledger-pod.yaml`
    4. Query the Pods specifically within the `finance-sandbox` namespace:
       ```bash
       kubectl get pods -n finance-sandbox
       ```
*   **Deterministic Verification Test:**
    Verify that the default namespace does not list the new Pod:
    `kubectl get pods`
    *   **Expected Output:**
        The output must be empty, and the Pod `ledger-db` must only be visible inside the `finance-sandbox` namespace.
*   **Troubleshooting Lab-Specific Issues:**
    If the Pod fails to deploy, run `kubectl describe pod ledger-db -n finance-sandbox` to check for scheduling or image pull errors.

#### Lab 2: Managing Pod Metadata Labels and Selectors
*   **Objective:** Practice manipulating and querying resource labels.
*   **Prerequisites:** Completed Lab 1.
*   **Step-by-Step Instructions:**
    1. Deploy an Nginx Pod named `portal-frontend` in the `default` namespace:
       ```bash
       kubectl run portal-frontend --image=nginx:1.25.1
       ```
    2. Add the label `environment=production` to the Pod:
       ```bash
       kubectl label pod portal-frontend environment=production
       ```
    3. Add another label `tier=frontend` to the same Pod:
       ```bash
       kubectl label pod portal-frontend tier=frontend
       ```
    4. Modify the `environment` label value to `staging` using the overwrite flag:
       ```bash
       kubectl label pod portal-frontend environment=staging --overwrite
       ```
*   **Deterministic Verification Test:**
    Query the Pods in the default namespace using the selector `environment=staging`:
    `kubectl get pods -l environment=staging`
    *   **Expected Output:**
        The command must return the `portal-frontend` Pod.
*   **Troubleshooting Lab-Specific Issues:**
    If the query returns empty results, run `kubectl get pod portal-frontend --show-labels` to verify that the labels were applied and overwritten correctly.

#### Lab 3: API Resource Discovery and Shortnames
*   **Objective:** Discover API groupings and resource metadata on a live cluster.
*   **Prerequisites:** Access to a running Kubernetes cluster.
*   **Step-by-Step Instructions:**
    1. Query all resource groups supported by the cluster:
       ```bash
       kubectl api-resources
       ```
    2. Find the shortname for `ServiceAccount` and `PersistentVolumeClaim` resources.
    3. Identify which API resources belong to the `apps` API group.
*   **Deterministic Verification Test:**
    Describe the schema properties of a Pod's specification using explain commands:
    `kubectl explain pod.spec.containers`
    *   **Expected Output:**
        The terminal must print detailed schema descriptions and fields for the container specifications.
*   **Troubleshooting Lab-Specific Issues:**
    If the explain command fails, verify that your client has network access to reach the API Server.

#### Lab 4: Configuring Multi-Container Log Collectors
*   **Objective:** Deploy a Pod with two cooperating containers sharing an emptyDir volume.
*   **Prerequisites:** Completed Lab 1.
*   **Step-by-Step Instructions:**
    1. Create a file named `log-collector-pod.yaml` (using the template from Example 2).
    2. Apply the manifest to the cluster: `kubectl apply -f log-collector-pod.yaml`
    3. Monitor the log stream generated by the sidecar container.
*   **Deterministic Verification Test:**
    Query the logs of the reader container:
    `kubectl logs web-logging-pod -c log-shipper`
    *   **Expected Output:**
        The output must display running logs: `... Transaction completed` printed every 5 seconds.
*   **Troubleshooting Lab-Specific Issues:**
    If the sidecar container fails to start, verify that the `emptyDir` mount path is identical in both container specifications.

#### Lab 5: Manifest Generation and Exporting Clean Templates
*   **Objective:** Generate error-free declarative files from running resources.
*   **Prerequisites:** Completed Lab 1.
*   **Step-by-Step Instructions:**
    1. Run a Pod named `temp-worker` imperatively:
       ```bash
       kubectl run temp-worker --image=alpine:3.18 -- sleep 3600
       ```
    2. Export the configuration of the running Pod, purging runtime status blocks:
       ```bash
       kubectl get pod temp-worker -o yaml > clean-pod.yaml
       ```
    3. Delete the running Pod from the cluster: `kubectl delete pod temp-worker`
*   **Deterministic Verification Test:**
    Re-apply the exported configuration:
    `kubectl apply -f clean-pod.yaml`
    *   **Expected Output:**
        The Pod must be recreated successfully and transition to a `Running` state.
*   **Troubleshooting Lab-Specific Issues:**
    If the re-apply command fails with field read-only errors, edit `clean-pod.yaml` to remove metadata status blocks (like `status:`, `uid:`, or `creationTimestamp:`).
"""

M1_INSIGHT = r"""### Professional Interview & Advanced Deep Dive

#### Q1: What is the main design advantage of the declarative model over the imperative model?
*   **Answer:** In an imperative model, you execute explicit commands to modify state step-by-step (e.g., 'start container', 'add route'), which requires complex error handling to resolve intermediate state failures. The declarative model lets you specify the final target state. The control plane handles the reconciliation loop, automatically correcting deviations (like failures or scaling issues) to reach that state.

#### Q2: What is etcd, and why is its reliability critical to the cluster?
*   **Answer:** `etcd` is a distributed, consistent key-value store used as the single source of truth for all Kubernetes cluster state data. If etcd becomes unavailable or corrupt, the API server cannot process state mutations, new pods cannot schedule, and existing controllers cannot reconcile state, effectively locking the cluster.

#### Q3: Why is a Pod, rather than a single container, the basic unit of execution in Kubernetes?
*   **Answer:** A Pod provides a shared context (shared Linux namespaces and cgroups) for its containers. This ensures that all containers in the same Pod share an IP address, port space, and storage volumes. It allows tightly coupled helper containers (like sidecars, proxies, or loggers) to communicate directly via `localhost` and share storage, which would be difficult to coordinate across separate containers.

#### Q4: How do Labels differ from Annotations in Kubernetes?
*   **Answer:** Labels are key-value pairs used to identify, group, and query API resources. They are indexed by the API server and can be used in selectors (e.g., mapping a Service to Pods). Annotations are non-identifying metadata used to store larger, non-indexed helper data (such as build IDs, team contact channels, or configuration policies) for external tools and systems.

#### Q5: What is the function of the kubelet on a worker node?
*   **Answer:** The `kubelet` is an agent running on each worker node. It registers the node with the API server, watches for Pod specifications assigned to its host, and calls the Container Runtime Interface (CRI) to ensure the declared containers are running and healthy. It also reports node status and resource utilization metrics back to the control plane.

### Academic & Professional Alignment
Many junior engineers mistake `nslookup` failures for application bugs. In certification exams like the CKA, candidates are tested on verifying name resolution, socket bindings, and generating clean YAML templates under time pressure. Mastering these foundational CLI commands is critical for success in both exams and real-world platform engineering.
"""

# =====================================================================
# MODULE 2: CLUSTER BOOTSTRAPPING, HIGH AVAILABILITY, & UPGRADES
# =====================================================================

M2_THEORY = r"""### Guided Conceptual Walkthrough
Imagine you are building a physical research laboratory. Historically, engineers had to manually assemble the building structure, route electrical pipes, and configure tables (manually provisioning servers and installing software packages). This was slow, expensive, and difficult to repeat. 

To automate the entire process, you implement two modern design approaches:
*   **Kubeadm**: Use a standard installation handbook (**kubeadm**) to configure the central power systems (**Control Plane Nodes**) and link other utility rooms (**Worker Nodes**) to the facility grid.
*   **Upgrade Workflow**: Upgrade the facility in a strict, sequential order to prevent control panel failures.

### Architectural, Lifecycle & Flow Blueprints

```mermaid
graph TD
    CP[Control Plane Node] -->|Bootstrap| API[API Server]
    API -->|etcd Store| ETCD[(etcd)]
    Worker[Worker Node] -->|Join Handshake| API
```

```mermaid
sequenceDiagram
    autonumber
    Admin->>CP: kubeadm init --pod-network-cidr
    CP->>CP: Generate PKI Certificates
    CP->>CP: Start Static Pod Control Plane
    Admin->>Worker: kubeadm join --token
    Worker->>CP: Register Node
```

### Under-the-Hood Mechanics & Internal Operations
The cluster bootstrapping process using `kubeadm` executes through several distinct phases:
1. **System Validation**: Verifies system requirements, disables swap, and loads kernel modules (such as `br_netfilter` and `overlay`).
2. **Control Plane Initialization (`kubeadm init`)**: Generates self-signed TLS certificates (stored in `/etc/kubernetes/pki/`), writes kubeconfig files to `/etc/kubernetes/`, and creates static Pod manifest files in `/etc/kubernetes/manifests/`. The local `kubelet` agent immediately detects the manifests and launches the core control plane components (API Server, Controller Manager, Scheduler, etcd) as static Pods.
3. **Cluster Joining (`kubeadm join`)**: Worker nodes connect to the control plane using a bootstrap token handshake, register their local kubelet, and join the cluster.

To maintain cluster stability during upgrades, you must execute steps sequentially, one minor version at a time (e.g., `v1.27` to `v1.28`), and always upgrade the control plane node before worker nodes to satisfy version skew requirements.

### Deep-Dive Reference (Advanced Context)
<details>
<summary>Static Pod Manifests and High Availability Topologies</summary>
Static Pods are managed directly by the local `kubelet` daemon on the node, bypassing the API Server scheduler. If a control plane component crashes, the local kubelet immediately restarts it. 

To prevent single points of failure, high-availability clusters run multiple redundant control plane nodes. This can be configured in two ways:
*   **Stacked etcd topology**: etcd runs on the same nodes as the control plane components. This is simpler to set up and manage, but risks resource contention.
*   **External etcd topology**: etcd runs on a separate dedicated cluster of machines, decoupling state storage from processing and improving reliability.
</details>

### Systemic Failure Modes & Boundary Violations
*   **Failure Mode 1: Kubelet fails to start due to swap enabled**
    *   **Symptom:** Kubelet crashes on startup, and system logs report `Failed to run kubelet: running with swap on is not supported`.
    *   **Root Cause:** The host node has swap partition active, violating the Kubelet's resource accounting checks.
    *   **Resolution:** Disable swap permanently and restart the service:
        ```bash
        sudo swapoff -a
        sudo sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab
        sudo systemctl restart kubelet
        ```

*   **Failure Mode 2: Bootstrap token expired during node join**
    *   **Symptom:** Running `kubeadm join` on a new worker node fails with authentication or handshake timeout errors.
    *   **Root Cause:** The bootstrap token generated during the initial `kubeadm init` phase has reached its default lifetime limit (typically 24 hours) and expired.
    *   **Resolution:** Generate a new bootstrap token and retrieve the updated join command from your control plane node:
        ```bash
        kubeadm token create --print-join-command
        ```

*   **Failure Mode 3: Control plane static Pod parsing error**
    *   **Symptom:** The API Server stops responding, and `kubectl` commands return connection refused errors.
    *   **Root Cause:** A syntax error or typo was introduced in one of the static Pod manifests inside `/etc/kubernetes/manifests/`.
    *   **Resolution:** SSH into the control plane host, locate the modified manifest, and fix the syntax error:
        ```bash
        sudo nano /etc/kubernetes/manifests/kube-apiserver.yaml
        ```

### Traceability Schema Check
All bootstrapping commands (`kubeadm init`, `join`, `upgrade`), static Pod configurations, and cluster upgrade workflows discussed below are conceptually defined in this section.
"""

M2_COMMANDS = r"""### Technical & Syntax Reference Manual
Below are the essential operational commands for bootstrapping, upgrading, and managing cluster nodes.

*   **Kubeadm Bootstrapping and Nodes Management:**
    ```bash
    # Initialize the control plane node with a specific pod network CIDR range
    sudo kubeadm init --pod-network-cidr=10.244.0.0/16

    # Drain a node to safely evict running workloads before maintenance
    kubectl drain worker-01 --ignore-daemonsets --delete-emptydir-data

    # Cordon a node to temporarily prevent new workloads from scheduling on it
    kubectl cordon worker-01

    # Uncordon a node to resume scheduling workloads after maintenance
    kubectl uncordon worker-01
    ```

*   **Cluster Upgrades and token generation:**
    ```bash
    # Generate a new bootstrap token and print the complete join command
    kubeadm token create --print-join-command

    # Run upgrade validation plan to check for compatibility and version issues
    kubeadm upgrade plan
    ```

### Anatomy & Boundary Table
| Variable / Parameter / Keyword Name | Expected Type / Allowed Values | Default Value / Operating Domain | Strict Structural Constraints |
| :--- | :--- | :--- | :--- |
| `pod-network-cidr` | CIDR IP address block | N/A | Must match the target subnet defined in your CNI configuration file exactly. |
| `--ignore-daemonsets` | Flag | N/A | Essential flag during node drain to avoid failing on system DaemonSet Pods. |
| `kubeadm join --token` | String | N/A | Must be a valid, unexpired bootstrap token generated by the control plane. |
| static Pod directory | Absolute Directory Path | `/etc/kubernetes/manifests` | Any manifest file placed in this directory is automatically run as a static Pod. |
"""

M2_EXAMPLES = r"""### Real-World Case Studies & Applied Examples

#### Example 1: Kubeadm Custom Cluster Configuration
*   **Context & Objectives:** Bootstrap a high-availability control plane node using a custom configuration file to define API Server settings and network subnets.
*   **Design Trade-offs:** A declarative configuration file is used instead of command-line flags to enable consistent, repeatable cluster deployments.
*   **Implementation:**
    ```yaml
    apiVersion: kubeadm.k8s.io/v1beta3
    kind: InitConfiguration
    localAPIEndpoint:
      advertiseAddress: "192.168.1.10"
      bindPort: 6443
    nodeRegistration:
      criSocket: "unix:///var/run/containerd/containerd.sock"
      name: "control-plane-01"
    ---
    apiVersion: kubeadm.k8s.io/v1beta3
    kind: ClusterConfiguration
    kubernetesVersion: "v1.28.0"
    controlPlaneEndpoint: "192.168.1.10:6443"
    networking:
      podSubnet: "10.244.0.0/16"
      serviceSubnet: "10.96.0.0/12"
    ```
*   **Behavioral Analysis:**
    Running `kubeadm init --config=config.yaml` tells kubeadm to parse these parameters. The engine generates the required TLS certificates, initializes the etcd database, and creates the static Pod manifest files using the defined subnets.

#### Example 2: Node Pre-flight System Configuration
*   **Context & Objectives:** Configure host kernel parameters to allow proper container network bridging before initializing the cluster.
*   **Design Trade-offs:** Kernel configurations are applied permanently at the OS level to ensure network bridging remains active across host restarts.
*   **Implementation:**
    Create `/etc/modules-load.d/k8s.conf`:
    ```ini
    br_netfilter
    overlay
    ```
    Create `/etc/sysctl.d/k8s.conf`:
    ```ini
    net.bridge.bridge-nf-call-iptables  = 1
    net.bridge.bridge-nf-call-ip6tables = 1
    net.ipv4.ip_forward                 = 1
    ```
*   **Behavioral Analysis:**
    The host OS loads the `br_netfilter` and `overlay` modules during boot. The sysctl rules enable IPv4 forwarding and bridge network packets to iptables filtering tables, allowing the container runtime and CNI to route Pod traffic correctly.

#### Example 3: Automated etcd Snapshot Backup Script
*   **Context & Objectives:** Configure an automated shell script to capture etcd snapshots safely on a control plane node.
*   **Design Trade-offs:** Cert-authenticated bash scripting is used instead of Pod-based tools to ensure backups continue even during Control Plane outages.
*   **Implementation:**
    ```bash
    #!/bin/bash
    export ETCDCTL_API=3
    BACKUP_PATH="/var/lib/db/etcd-backups"
    mkdir -p "${BACKUP_PATH}"

    etcdctl \
      --endpoints=https://127.0.0.1:2379 \
      --cacert=/etc/kubernetes/pki/etcd/ca.crt \
      --cert=/etc/kubernetes/pki/etcd/server.crt \
      --key=/etc/kubernetes/pki/etcd/server.key \
      snapshot save "${BACKUP_PATH}/etcd-backup-$(date +%F-%H%M).db"
    ```
*   **Behavioral Analysis:**
    The script runs the `etcdctl` client on the host node, authenticating via local TLS certificates, and writes a compressed snapshot of the current etcd database state to `/var/backups/`.

#### Example 4: etcd Static Pod Configuration
*   **Context & Objectives:** Update the etcd static Pod to use a restored database directory after performing a disaster recovery restore.
*   **Design Trade-offs:** Updating the host's static Pod manifest is the only reliable way to update etcd when the API Server is down.
*   **Implementation:**
    Modify `/etc/kubernetes/manifests/etcd.yaml`:
    ```yaml
    apiVersion: v1
    kind: Pod
    metadata:
      name: etcd
      namespace: kube-system
    spec:
      containers:
      - name: etcd
        image: registry.k8s.io/etcd:3.5.9-0
        command:
        - etcd
        - --data-dir=/var/lib/etcd-new
        - --listen-client-urls=https://127.0.0.1:2379
        volumeMounts:
        - mountPath: /var/lib/etcd-new
          name: etcd-data
      volumes:
      - hostPath:
          path: /var/lib/etcd-new
        name: etcd-data
    ```
*   **Behavioral Analysis:**
    The local `kubelet` agent detects the changes inside `/etc/kubernetes/manifests/etcd.yaml` and restarts the etcd container process, pointing it to the newly restored database directory.

#### Example 5: Upgrading Worker Node Kubelet Daemon
*   **Context & Objectives:** Complete the upgrade of a worker node by installing the target version of the kubelet and restarting the service.
*   **Design Trade-offs:** We drain the node before upgrading to prevent running workloads from experiencing sudden, ungraceful shutdowns.
*   **Implementation:**
    ```bash
    #!/bin/bash
    # Upgrade the kubelet binary on Debian-based hosts
    apt-mark unhold kubelet
    apt-get update && apt-get install -y kubelet=1.28.0-00
    apt-mark hold kubelet

    # Reload and restart the systemd service
    systemctl daemon-reload
    systemctl restart kubelet
    ```
*   **Behavioral Analysis:**
    The package manager installs the target kubelet version. Running systemctl commands reloads the configurations and restarts the kubelet service, completing the node upgrade.
"""

M2_EXERCISE = r"""### Practical Laboratories & Hands-On Exercises

#### Lab 1: Initializing a Single-Node Control Plane
*   **Objective:** Initialize a control plane node using kubeadm.
*   **Prerequisites:** Access to a clean Linux VM or bare-metal server with containerd pre-installed.
*   **Step-by-Step Instructions:**
    1. Configure host kernel modules and container runtime parameters.
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

#### Lab 2: Joining Worker Nodes to the Cluster
*   **Objective:** Register a worker node to an existing control plane.
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

#### Lab 3: Upgrading the Control Plane Node
*   **Objective:** Upgrade a control plane node to a newer minor version.
*   **Prerequisites:** Access to a multi-node cluster.
*   **Step-by-Step Instructions:**
    1. Drain the control plane node to evict running workloads:
       ```bash
       kubectl drain control-plane-node --ignore-daemonsets --delete-emptydir-data
       ```
    2. Upgrade the `kubeadm` package to the target version:
       ```bash
       sudo apt-get update && sudo apt-get install -y kubeadm=1.28.0-00
       ```
    3. Run the upgrade validation plan and apply the update:
       ```bash
       sudo kubeadm upgrade plan
       sudo kubeadm upgrade apply v1.28.0 -y
       ```
    4. Upgrade the `kubelet` and `kubectl` packages on the host.
    5. Restart the kubelet service: `sudo systemctl restart kubelet`
    6. Uncordon the node: `kubectl uncordon control-plane-node`
*   **Deterministic Verification Test:**
    Verify the upgraded node status: `kubectl get nodes`
    *   **Expected Output:**
        The output must display the upgraded version `v1.28.0` on your control plane node.
*   **Troubleshooting Lab-Specific Issues:**
    If the node status remains `NotReady`, verify that the kubelet service started successfully and check system logs: `journalctl -u kubelet`.

#### Lab 4: Upgrading Worker Nodes Safely
*   **Objective:** Upgrade worker nodes with zero downtime for running workloads.
*   **Prerequisites:** Completed Lab 3.
*   **Step-by-Step Instructions:**
    1. Drain the worker node from the control plane:
       ```bash
       kubectl drain worker-01 --ignore-daemonsets --delete-emptydir-data
       ```
    2. SSH into the worker node and upgrade the `kubeadm` package to version `1.28.0-00`.
    3. Run `sudo kubeadm upgrade node` on the worker host.
    4. Upgrade the `kubelet` and `kubectl` packages on the worker host.
    5. Restart the kubelet service, then uncordon the node from the control plane:
       ```bash
       kubectl uncordon worker-01
       ```
*   **Deterministic Verification Test:**
    Verify the upgraded worker node status: `kubectl get nodes`
    *   **Expected Output:**
        The output must display the upgraded version `v1.28.0` on your worker node.
*   **Troubleshooting Lab-Specific Issues:**
    If the drain command hangs, verify if a PodDisruptionBudget is protecting workloads, and scale up the deployment on other nodes to satisfy the budget.

#### Lab 5: Backing Up and Restoring the etcd Store
*   **Objective:** Backup the cluster state and restore it in a disaster recovery scenario.
*   **Prerequisites:** Access to a running control plane master node.
*   **Step-by-Step Instructions:**
    1. Take an etcd database snapshot:
       ```bash
       sudo ETCDCTL_API=3 etcdctl \
         --endpoints=https://127.0.0.1:2379 \
         --cacert=/etc/kubernetes/pki/etcd/ca.crt \
         --cert=/etc/kubernetes/pki/etcd/server.crt \
         --key=/etc/kubernetes/pki/etcd/server.key \
         snapshot save /tmp/etcd-lab.db
       ```
    2. Create a test namespace on the cluster, then verify the snapshot backup was successful.
    3. Run snapshot restore to a new data directory:
       ```bash
       sudo ETCDCTL_API=3 etcdctl --data-dir=/var/lib/etcd-recovered snapshot restore /tmp/etcd-lab.db
       ```
    4. Update your local etcd static Pod configuration `/etc/kubernetes/manifests/etcd.yaml` to mount and use `/var/lib/etcd-recovered` as its data directory.
*   **Deterministic Verification Test:**
    Verify that your cluster has been rolled back and that the namespace marker has been deleted:
    `kubectl get namespaces`
    *   **Expected Output:**
        The output must NOT display the namespace `etcd-test-marker`, confirming the cluster state was restored successfully to the snapshot point.
*   **Troubleshooting Lab-Specific Issues:**
    If the API Server fails to restart after updating the etcd data directory, verify that your `/etc/kubernetes/manifests/etcd.yaml` file has valid syntax and that the permissions on `/var/lib/etcd-recovered` allow the etcd container process to read and write to the directory.
"""

M2_INSIGHT = r"""### Interview Q&A

#### Q1: What happens during the execution of kubeadm init?
*   **Answer:** `kubeadm init` runs pre-flight checks, generates self-signed TLS certificates for cluster components, writes kubeconfig files for administrative access, generates static pod manifests for control plane components (api-server, controller-manager, scheduler, etcd), taints the control node to prevent running application workloads, and generates a join token for worker nodes.

#### Q2: Why is it critical to drain a node before performing upgrades or maintenance?
*   **Answer:** Draining a node gracefully evicts all running pods (safely rescheduling them on other worker nodes) before host maintenance. This ensures that stateless deployments maintain their active replica counts and prevents stateful applications from experiencing sudden, ungraceful shutdowns.

#### Q3: How do Stacked etcd topologies differ from External etcd topologies?
*   **Answer:** In a stacked topology, the etcd database runs on the same nodes as the control plane components. This is simpler to set up and manage, but risks resource contention on the control plane hosts. In an external topology, etcd runs on a separate dedicated cluster of machines, which decouples state storage from processing and improves cluster reliability.

#### Q4: Why must control plane nodes be upgraded before worker nodes?
*   **Answer:** Kubernetes maintains strict version skew compatibility rules: the API server must be at the same or a newer version than all other cluster components (such as the controller-manager, scheduler, kubelet, and kube-proxy). Upgrading worker nodes first would break this compatibility and cause API communication errors.

#### Q5: How do you authorize etcdctl commands on a TLS-secured cluster?
*   **Answer:** Since etcd is secured with mutual TLS, all commands must include the cluster's client certificates and keys for authentication. These are typically located on the control plane host: `--cacert=/etc/kubernetes/pki/etcd/ca.crt`, `--cert=/etc/kubernetes/pki/etcd/server.crt`, and `--key=/etc/kubernetes/pki/etcd/server.key`.

### CKA Exam Focus
- Ensure you know how to write etcd backup commands using the correct certificate paths.
- Practice upgrading both control plane and worker nodes sequentially, as node upgrades are a common task in the CKA exam.
- Remember to set `ETCDCTL_API=3` before running any etcdctl commands to use the correct API version.
"""

# =====================================================================
# MODULE 3: WORKLOADS, LIFECYCLE MANAGEMENT, & ADVANCED SCHEDULING
# =====================================================================

M3_THEORY = r"""### Guided Conceptual Walkthrough
Imagine a large shared research facility. If every researcher (application process or developer) has unrestricted master access keys (**Root Access**), they could accidentally access other rooms, modify secure experiments, or consume all the power grids, causing a facility-wide blackout (**Noisy Neighbors**). 

To secure the facility, you set up strict scheduling and resource boundaries:
*   **Init Containers**: Ensure that specific configuration tasks are run before the main application starts.
*   **Affinity & Anti-Affinity**: Force the scheduler to place Pods on specific nodes or prevent duplicate instances from running on the same host node.
*   **Taints & Tolerations**: Node taints repel Pods, preventing standard workloads from running on dedicated nodes.

### Architectural, Lifecycle & Flow Blueprints

```mermaid
graph TD
    User[Client Operator] -->|Apply Deployment| API[API Server]
    API -->|Consensus State| ETCD[(etcd)]
    SCH[Scheduler] -->|Evaluate Affinity| Node[Worker Node]
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

For resource allocations, the Kubelet uses Linux kernel Control Groups (cgroups) to enforce requests and limits at the process level. The kernel throttles the container process if it attempts to exceed its CPU limit, and terminates it using the host's Out-Of-Memory (OOM) killer if it attempts to exceed its memory limit.

### Deep-Dive Reference (Advanced Context)
<details>
<summary>Quality of Service (QoS) Classes and Eviction Priority</summary>
Kubernetes classifies Pods into three Quality of Service (QoS) classes based on their resource configuration:
*   **Guaranteed**: Every container in the Pod has identical CPU and memory requests and limits.
*   **Burstable**: At least one container has a request that is lower than its limit, or has no limit defined.
*   **BestEffort**: No containers have any requests or limits defined.
If the worker node runs out of memory, the kernel will terminate processes starting with `BestEffort` Pods first, then `Burstable` Pods, and finally `Guaranteed` Pods only if absolutely necessary to keep the node stable.
</details>

### Systemic Failure Modes & Boundary Violations
*   **Failure Mode 1: Pod Crashes with OOMKilled (Exit Code 137)**
    *   **Symptom:** Pods crash repeatedly, showing a status of `OOMKilled`, or running describe commands displays `Exit Code: 137`.
    *   **Root Cause:** The container process consumed more memory than the maximum memory limit defined in its Pod specification.
    *   **Resolution:** Increase the memory limit in the Pod manifest to accommodate the application's runtime requirements:
        ```yaml
        resources:
          limits:
            memory: "512Mi"
        ```

*   **Failure Mode 2: Scheduler Failure (Unsatisfiable Pod Anti-Affinity)**
    *   **Symptom:** Pod remains stuck in a `Pending` state, and events show `0/3 nodes are available: 3 node(s) had anti-affinity conflicts`.
    *   **Root Cause:** A hard anti-affinity constraint prevents the scheduler from placing duplicate Pods on the same node.
    *   **Resolution:** Either add more worker nodes to the cluster or soften the anti-affinity rules to a preferred constraint.

*   **Failure Mode 3: Container Exit Loop (CrashLoopBackOff)**
    *   **Symptom:** The Pod status shows `CrashLoopBackOff`, and the restart count continues to increment.
    *   **Root Cause:** The application is starting successfully but crashing shortly after due to an internal application error or a failed database connection.
    *   **Resolution:** Retrieve the container's logs (including logs from the previous failed run) to diagnose and fix the application-level issue:
        ```bash
        kubectl logs <pod-name> --previous
        ```

### Traceability Schema Check
All scheduling directives (`nodeSelector`, `affinity`, `tolerations`), container parameters (`requests`, `limits`), and Pod lifecycle hooks used below are conceptually defined in this section.
"""

M3_COMMANDS = r"""### Technical & Syntax Reference Manual
Below are the essential commands for managing workloads, scaling replicas, and configuring scheduling parameters.

*   **Deployment Operations and Scaling:**
    ```bash
    # Scale an active deployment to 5 replicas
    kubectl scale deployment/api-server --replicas=5

    # Check the rolling update history of a deployment
    kubectl rollout history deployment/api-server
    ```

*   **Scheduler Audit and Controls:**
    ```bash
    # View active taints on all nodes in the cluster
    kubectl get nodes -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints

    # Apply a NoSchedule taint to a worker node
    kubectl taint nodes worker-01 dedicated=database:NoSchedule
    ```

### Anatomy & Boundary Table
| Variable / Parameter / Keyword Name | Expected Type / Allowed Values | Default Value / Operating Domain | Strict Structural Constraints |
| :--- | :--- | :--- | :--- |
| `spec.replicas` | Integer (0 - 1000+) | `1` | Defines the desired target number of concurrent identical Pod instances to run. |
| `topologyKey` | String | `kubernetes.io/hostname` | Must match a valid label key on your cluster nodes. |
| `tolerations[*].effect` | String (`NoSchedule`, `PreferNoSchedule`, `NoExecute`) | `NoSchedule` | Determines what actions the scheduler takes for untolerated taints. |
| `initialDelaySeconds` | Integer (0 - 3600) | `0` | Delay before the kubelet begins executing health probes. |
"""

M3_EXAMPLES = r"""### Real-World Examples

#### Example 1: Deployment with Rolling Update and Probes
*   **Situation:** Deploy a high-availability stateless API gateway that requires zero-downtime updates and reliable health checks.
*   **Action:** Define a Deployment with an explicit rolling update strategy and configured liveness/readiness probes.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
  namespace: default
  labels:
    tier: gateway
spec:
  replicas: 3
  selector:
    matchLabels:
      app: gateway-engine
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: gateway-engine
    spec:
      containers:
      - name: gateway-container
        image: nginx:1.25.1
        ports:
        - containerPort: 80
        livenessProbe:
          httpGet:
            path: /healthz
            port: 80
          initialDelaySeconds: 15
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
```

#### Example 2: Pod with Strict Resource Controls
*   **Situation:** Deploy a memory-intensive microservice with defined resource requests and limits to prevent it from consuming all host memory.
*   **Action:** Define CPU and memory requests and limits in the Pod specification.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: dynamic-cache
  namespace: default
spec:
  containers:
  - name: cache-container
    image: redis:7.0-alpine
    resources:
      requests:
        memory: "64Mi"
        cpu: "250m"
      limits:
        memory: "128Mi"
        cpu: "500m"
```

#### Example 3: High-Availability Pod Anti-Affinity
*   **Situation:** Deploy three replicas of a web server and ensure that no two replicas run on the same physical host node.
*   **Action:** Configure a Deployment with a Pod Anti-Affinity rule.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-ha
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web-ha
  template:
    metadata:
      labels:
        app: web-ha
    spec:
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchExpressions:
              - key: app
                operator: In
                values:
                - web-ha
            topologyKey: "kubernetes.io/hostname"
      containers:
      - name: nginx
        image: nginx:1.25.1
```

#### Example 4: Pod with Tolerations for Tainted Nodes
*   **Situation:** Run an administrative monitoring tool on master nodes that carry the taint `node-role.kubernetes.io/control-plane:NoSchedule`.
*   **Action:** Create a Pod manifest with a matching Toleration.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: plane-observer
spec:
  tolerations:
  - key: "node-role.kubernetes.io/control-plane"
    operator: "Exists"
    effect: "NoSchedule"
  containers:
  - name: observer
    image: alpine:3.18
    command: ["/bin/sh", "-c", "echo 'Observing...'; sleep 3600"]
```

#### Example 5: Native Sidecar Container Definition
*   **Situation:** A web service requires a secondary local proxy container to secure outbound traffic, and the proxy must start before the main application starts.
*   **Action:** Define the proxy as an init container with the sidecar restart policy (requires Kubernetes v1.28+).

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-web-app
spec:
  containers:
  - name: main-web
    image: nginx:1.25.1
    ports:
    - containerPort: 80
  initContainers:
  - name: secure-proxy
    image: alpine:3.18
    command: ["/bin/sh", "-c", "echo 'Proxy started, securing traffic...'; while true; do sleep 3600; done"]
    restartPolicy: Always
```
"""

M3_EXERCISE = r"""### Practical Laboratories & Hands-On Exercises

#### Lab 1: Enforcing Resource Limits and Observing OOM Kills
*   **Objective:** Observe how the cluster handles containers that exceed their resource limits.
*   **Tasks:**
    1. Create a Pod with a memory limit of `50Mi`.
    2. Configure the container to run a script that allocates a large array to intentionally consume memory.
    3. Apply the manifest and monitor the pod status.
    4. Verify that the pod is terminated with an Out-of-Memory (`OOMKilled`) status.

#### Lab 2: Targeted Node Scheduling with Affinity
*   **Objective:** Schedule workloads on specific hosts using node labels and affinity rules.
*   **Tasks:**
    1. Label node `worker-01` with the label `disktype=ssd`.
    2. Write a Pod manifest that uses Node Affinity to target nodes with the `disktype=ssd` label.
    3. Apply the manifest and verify the pod is scheduled on `worker-01`.
    4. Delete the label from the node and verify how subsequent scheduled pods are affected.

#### Lab 3: Distributing Workloads with Anti-Affinity
*   **Objective:** Maintain high availability by distributing application replicas across different nodes.
*   **Tasks:**
    1. Deploy a Deployment with 3 replicas.
    2. Configure a Pod Anti-Affinity rule targeting the deployment's own label selector.
    3. Verify that each pod is scheduled on a different worker node.
    4. Scale the deployment beyond the number of available nodes and observe if the new pods remain in a `Pending` state.

#### Lab 4: Restricting Nodes using Taints and Tolerations
*   **Objective:** Reserve dedicated nodes for specific workloads using taints.
*   **Tasks:**
    1. Apply a NoSchedule taint to a worker node: `kubectl taint nodes <node-name> dedicated=infra:NoSchedule`.
    2. Deploy a standard test pod and verify that it is scheduled on a different node.
    3. Deploy a second pod with a matching toleration for the taint.
    4. Verify that the second pod schedules successfully on the tainted node.

#### Lab 5: Dynamic Rollout Management and Rollback Checks
*   **Objective:** Practice rolling out deployment updates and reversing configurations under time constraints.
*   **Tasks:**
    1. Deploy a Deployment of `nginx:1.25.1` named `web-rollout-lab` with 3 replicas.
    2. Update the container image to `nginx:invalid-version-tag` to simulate a failed rollout.
    3. Verify that the rollout is stuck using `kubectl rollout status`.
    4. Roll back the deployment to the last stable state using `kubectl rollout undo` and verify that all Pods return to a healthy `Running` state.
"""

M3_INSIGHT = r"""### Interview Q&A

#### Q1: What happens if a container exceeds its memory limits versus its CPU limits?
*   **Answer:** If a container exceeds its memory limit, the Linux kernel's Out-Of-Memory (OOM) killer terminates the process, causing the container to exit with status code 137 (OOMKilled). If a container exceeds its CPU limit, Kubernetes throttles its CPU usage, slowing down execution, but does not terminate the container.

#### Q2: How do Requests and Limits affect Quality of Service (QoS) classes?
*   **Answer:** Kubernetes assigns QoS classes to pods based on their resource configurations:
  - **Guaranteed:** Every container in the pod has identical CPU and memory requests and limits.
  - **Burstable:** Requests and limits are defined, but they are not equal, or some containers lack limits.
  - **BestEffort:** No containers in the pod have requests or limits defined.
  The cluster uses these classes to determine eviction priority when node resources are low.

#### Q3: What is the difference between a Node Selector and Node Affinity?
*   **Answer:** A Node Selector is a simple key-value matching rule used to schedule pods on nodes with matching labels. Node Affinity is a more flexible system that supports logical operators (such as `In`, `NotIn`, `Exists`), soft preferences (`preferredDuringScheduling`), and the ability to schedule pods relative to other pods (Pod Affinity).

#### Q4: How does the NoExecute taint effect behave compared to NoSchedule?
*   **Answer:** The `NoSchedule` taint prevents new pods from scheduling on a node unless they have a matching toleration, but does not affect existing pods running on the node. The `NoExecute` taint also prevents new pods from scheduling, but additionally evicts any running pods on the node that do not have a matching toleration.

#### Q5: Why is a pod rejected if a LimitRange is active but the pod defines no resources?
*   **Answer:** If a `LimitRange` defines minimum/maximum limits but no default requests or limits, and a pod is submitted without resource definitions, the API server will reject the pod if it violates the LimitRange boundaries. If defaults are defined, the LimitRange automatically injects them into the pod specification at creation time.

### CKA Exam Focus
- Ensure you understand the distinction between `requests` (used for scheduling decisions) and `limits` (enforced at runtime).
- Practice configuring path parameters for `httpGet` probes, as misconfigured endpoints can lead to unexpected restart loops.
"""

# =====================================================================
# MODULE 4: SERVICES, COREDNS, & CORE CLUSTER NETWORKING
# =====================================================================

M4_THEORY = r"""### Guided Conceptual Walkthrough
Imagine you run a customer support call center. The individual operators (**Pods**) are constantly changing shifts, moving to different desks, or taking breaks, making it impossible to call any specific operator directly. 

To solve this, you set up a centralized hotline switchboard (**Service**). Customers call a single, permanent hotline number (**ClusterIP**). The switchboard automatically routes incoming calls to whoever is currently active and ready to take a call. 

If you want to allow external callers from the public telephone network to reach your support team, you assign a public toll-free number (**LoadBalancer**) to your switchboard. 

In engineering terms, this is how Kubernetes services work. Since Pods are ephemeral and their IP addresses are unreliable, we configure Services to act as stable access points. Services use label selectors to track backend Pods dynamically and automatically load balance traffic across those active, healthy instances.

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
    Pod-A->>CoreDNS: DNS Query (db-service.default.svc.cluster.local)
    CoreDNS-->>Pod-A: Returns Service ClusterIP (10.96.100.5)
    Pod-A->>ServiceIP: Sends TCP Packet to 10.96.100.5
    Node-Kernel->>Pod-B: NAT Translation routes packet to Backend Pod (10.244.1.15)
```

### Under-the-Hood Mechanics & Internal Operations
Services in Kubernetes do not exist as physical appliances, routers, or container processes. Instead, they are virtual entities configured directly inside the host kernel's packet filtering engine (such as `iptables` or `IPVS`) on each worker node.
1. **The Endpoints Controller**: Monitors the API Server for active Pods that match a Service's label selector. It compiles their current IP addresses into an **Endpoints** (or EndpointSlice) API object.
2. **kube-proxy**: Runs on every node and monitors the API Server for changes to Services and Endpoints. When changes occur, it updates the host's local packet filtering rules.
3. **CoreDNS**: The in-cluster DNS server that monitors Service objects and automatically creates a corresponding DNS A-record for each Service (e.g., `service-name.namespace-name.svc.cluster.local`).

When a container makes a request to a Service's DNS name, the container's internal resolver queries CoreDNS to resolve the Service's virtual ClusterIP. When the container sends a packet to this ClusterIP, the host node's kernel immediately intercepts the packet, applies Destination Network Address Translation (DNAT) based on the iptables rules configured by kube-proxy, and routes the packet directly to a random healthy backend Pod's IP address.

### Deep-Dive Reference (Advanced Context)
<details>
<summary>Service Types and CoreDNS Resolution Path</summary>
Kubernetes supports four main types of Services:
*   **ClusterIP**: Exposes the service on a cluster-internal IP address. This is the default service type and makes the workload accessible only from within the cluster.
*   **NodePort**: Allocates a static port from a reserved range (typically 30000–32767) on every node's external network interface. Traffic sent to any node's IP address on that port is automatically forwarded to the service.
*   **LoadBalancer**: Integrates with external cloud infrastructure (such as AWS, GCP, or Azure) to provision an external load balancer, assigning a public IP address that routes internet traffic directly to the service.
*   **Headless Service**: Created by setting `clusterIP: None` in the Service specification. It does not create a virtual load-balancing IP. Instead, it allows direct DNS resolution to the individual IP addresses of the backing pods.
</details>

### Systemic Failure Modes & Boundary Violations
*   **Failure Mode 1: Service Selector Label Mismatch**
    *   **Symptom:** Querying a Service returns connection timeouts or HTTP 503 errors, and listing endpoints for the service shows empty results.
    *   **Root Cause:** The label selector defined in the Service specification does not match the actual labels configured on the backend Pods.
    *   **Resolution:** Verify the labels on your running Pods and ensure the Service's selector matches them exactly.

*   **Failure Mode 2: NodePort Port Allocation Exhaustion**
    *   **Symptom:** Creating a NodePort service fails with the error `provided port is not in the valid range` or `port is already allocated`.
    *   **Root Cause:** The requested NodePort is outside the default reserved range (`30000–32767`), or the requested port is already occupied by another Service.
    *   **Resolution:** Either omit the `nodePort` field in your manifest to let the API Server allocate an unused port automatically, or select an unallocated port within the valid range:
        ```bash
        kubectl get svc -A | grep -i nodeport
        ```

*   **Failure Mode 3: In-Cluster DNS Resolution Failures**
    *   **Symptom:** Containers fail to communicate with internal services using DNS names (e.g., `db-service`), but can connect if using the direct ClusterIP.
    *   **Root Cause:** The CoreDNS pods are crashing, misconfigured, or resource-starved, preventing local DNS resolution.
    *   **Resolution:** Check the health and logs of the CoreDNS pods running in the system namespace:
        ```bash
        kubectl get pods -n kube-system -l k8s-app=kube-dns
        ```

### Traceability Schema Check
All Service types (ClusterIP, NodePort, LoadBalancer, Headless), CoreDNS resolution behaviors, and network troubleshooting workflows used below are conceptually defined in this section.
"""

M4_COMMANDS = r"""### Technical & Syntax Reference Manual
Below are the essential commands for managing Service resources and troubleshooting internal network routing.

*   **Exposing Workloads as Services:**
    ```bash
    # Expose a Deployment as a ClusterIP service on port 80, targeting port 8080 on the containers
    kubectl expose deployment prod-web --port=80 --target-port=8080 --name=web-service

    # List all services in the current namespace along with their IP addresses and ports
    kubectl get svc
    ```

*   **Querying Network Configuration Details:**
    ```bash
    # View the active Endpoints mapped to a specific service
    kubectl get endpoints web-service

    # Retrieve detailed configuration and target port mappings for a service
    kubectl describe svc web-service
    ```

### Anatomy & Boundary Table
| Variable / Parameter / Keyword Name | Expected Type / Allowed Values | Default Value / Operating Domain | Strict Structural Constraints |
| :--- | :--- | :--- | :--- |
| `spec.type` | String (`ClusterIP`, `NodePort`, `LoadBalancer`, `ExternalName`) | `ClusterIP` | Case-sensitive. Determines how the service is exposed within and outside the cluster. |
| `spec.ports[].port` | Integer (1 - 65535) | N/A (Required) | The port number that the Service exposes internally within the cluster. |
| `spec.ports[].targetPort` | Integer or String | Matches `spec.ports[].port` | The port number or named port that the application is listening on inside the backend Pods. |
| `spec.ports[].nodePort` | Integer (30000 - 32767) | Auto-allocated | Only applicable for `NodePort` and `LoadBalancer` service types. |
"""

M4_EXAMPLES = r"""### Real-World Examples

#### Example 1: Multi-Port Service Configuration
*   **Situation:** Deploy a web application that exposes web traffic on port `80` and administration metrics on port `9090`.
*   **Action:** Define a ClusterIP Service with multiple named ports.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-multiport-svc
  namespace: default
spec:
  type: ClusterIP
  ports:
  - name: http
    port: 80
    targetPort: 8080
    protocol: TCP
  - name: metrics
    port: 9090
    targetPort: 9091
    protocol: TCP
  selector:
    app: multi-web
```

#### Example 2: NodePort Service with Static Port Assignment
*   **Situation:** Expose an application externally on a specific physical host port across all cluster nodes.
*   **Action:** Define a NodePort Service with a static port inside the permitted range (`30000-32767`).

```yaml
apiVersion: v1
kind: Service
metadata:
  name: static-nodeport-svc
spec:
  type: NodePort
  ports:
  - port: 80
    targetPort: 8080
    nodePort: 32080
    protocol: TCP
  selector:
    app: external-app
```

#### Example 3: Headless Service for Database Replicas
*   **Situation:** Deploy a clustered database where clients must connect directly to individual database replicas (rather than a load-balanced endpoint).
*   **Action:** Set `clusterIP: None` in the Service specification to create a Headless Service.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: db-headless
spec:
  clusterIP: None
  ports:
  - port: 5432
    targetPort: 5432
    name: postgres
  selector:
    app: db-cluster
```

#### Example 4: Manual Endpoints for External Targets
*   **Situation:** Route traffic through a Kubernetes Service to an external database running outside the cluster.
*   **Action:** Create a Service without a label selector and manually define matching `Endpoints`.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: external-db-svc
spec:
  ports:
  - port: 3306
    targetPort: 3306
---
apiVersion: v1
kind: Endpoints
metadata:
  name: external-db-svc
subsets:
- addresses:
  - ip: 192.168.100.50
  ports:
  - port: 3306
```

#### Example 5: Custom CoreDNS Forwarding ConfigMap
*   **Situation:** Configure cluster name resolution so lookup queries for `*.internal.company` are forwarded to a corporate DNS server at `10.10.10.10`.
*   **Action:** Update the cluster's CoreDNS configuration map.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: coredns
  namespace: kube-system
data:
  Corefile: |
    .:53 {
        errors
        health
        ready
        kubernetes cluster.local in-addr.arpa ip6.arpa {
           pods insecure
           fallthrough in-addr.arpa ip6.arpa
        }
        prometheus :9153
        forward . 8.8.8.8 8.8.4.4
        cache 30
        loop
        reload
        loadbalance
    }
    internal.company:53 {
        forward . 10.10.10.10
    }
```
"""

M4_EXERCISE = r"""### Practical Laboratories & Hands-On Exercises

#### Lab 1: Exposing Pods Internally via ClusterIP
*   **Objective:** Deploy stateless pods and expose them using a ClusterIP service.
*   **Prerequisites:** Access to a running Kubernetes cluster.
*   **Tasks:**
    1. Create a Deployment of `httpd:2.4` with 2 replicas labeled `app=http-web`.
    2. Expose the deployment as a ClusterIP Service named `http-internal` on port `80` targeting container port `80`.
    3. Retrieve the Service's ClusterIP and verify internal connectivity from a separate test pod using `curl`.
    4. View the associated endpoints and EndpointSlices generated by the control plane.

#### Lab 2: External Access via NodePort Services
*   **Objective:** Expose workloads outside the cluster using NodePort Services.
*   **Tasks:**
    1. Create a Pod labeled `app=nodeport-app` running a simple web server.
    2. Expose the pod using a NodePort Service on static port `31080`.
    3. Retrieve the IP address of one of your cluster's worker nodes.
    4. Run a curl query from your host machine to verify connectivity using the worker IP and port `31080`.

#### Lab 3: Setting Up and Querying Headless Services
*   **Objective:** Configure a headless service and verify direct name resolution.
*   **Tasks:**
    1. Deploy a StatefulSet of 2 replicas running `redis` with labels `app=redis-store`.
    2. Create a Headless Service (setting `clusterIP: None`) named `redis-headless`.
    3. Deploy an interactive network troubleshooting pod running dns tools (such as `nicolaka/netshoot`).
    4. Run `nslookup redis-headless` within the pod and verify that it returns the direct IP addresses of the individual Redis pods.

#### Lab 4: Mapping External Services to Endpoints
*   **Objective:** Route traffic from inside the cluster to an external service using manual Endpoints.
*   **Tasks:**
    1. Create a ClusterIP Service named `mock-external-api` without specifying a label selector.
    2. Create an Endpoints resource with the same name, mapping it to an external public IP address (e.g., `8.8.8.8`).
    3. Launch a test pod and verify that requests sent to `mock-external-api` are routed to the external target.

#### Lab 5: Customizing CoreDNS Mappings
*   **Objective:** Modify CoreDNS configurations to forward name resolution queries to external DNS servers.
*   **Tasks:**
    1. Edit the `coredns` ConfigMap in the `kube-system` namespace.
    2. Append a custom forwarding block for domain `test.internal` routing to DNS server `1.1.1.1`.
    3. Restart the CoreDNS deployment to apply the new configurations.
    4. Deploy a network debugging pod and run `nslookup` queries to verify the custom routing.
"""

M4_INSIGHT = r"""### Interview Q&A

#### Q1: What is the function of the ClusterIP in a Kubernetes Service?
*   **Answer:** A ClusterIP is a virtual, stable IP address assigned to a Service. It is managed by `kube-proxy` on each node, which configures network routing rules (using `iptables` or `IPVS`) to intercept traffic sent to the ClusterIP and load-balance it across the backing pod IP addresses.

#### Q2: What happens if you define a Service with a label selector, but no pods match that selector?
*   **Answer:** The Service will be created successfully, but its corresponding `Endpoints` and `EndpointSlices` resources will be empty. Any applications or clients attempting to connect to the Service will receive network timeout or connection refused errors.

#### Q3: Why would an operator use a Headless Service instead of a standard Service?
*   **Answer:** Headless Services are used when clients need to connect directly to specific individual pods (e.g., in stateful clustered applications like databases or message queues). By disabling the load-balancing IP, name resolution queries return direct records for each pod, allowing clients to establish direct connections to primary or replica nodes.

#### Q4: How does kube-proxy handle traffic in IPVS mode compared to iptables mode?
*   **Answer:** In `iptables` mode, `kube-proxy` writes sequential firewall rules for each service, which can degrade packet processing performance as the cluster scales to thousands of services. In `IPVS` mode, it uses IP Virtual Server kernel hashing tables, which process load balancing in O(1) time complexity and improve scalability in large clusters.

#### Q5: What is the naming convention for Service DNS records in Kubernetes?
*   **Answer:** The full domain name is `<service-name>.<namespace>.svc.<cluster-domain>` (the default cluster domain is `cluster.local`). Pods in the same namespace can resolve the service using the short service name (e.g., `my-service`), while pods in other namespaces can resolve it using `<service-name>.<namespace>`.

### CKA Exam Focus
- Ensure you know how to use `kubectl exec` to run `nslookup` tests inside pods for DNS troubleshooting questions.
- Practice configuring multi-port services, as mapping the correct port names and target ports is a common task in the exam.
"""

# =====================================================================
# MODULE 5: ADVANCED NETWORK ISOLATION, INGRESS, & GATEWAY API
# =====================================================================

M5_THEORY = r"""### Guided Conceptual Walkthrough
Imagine you run a secure office building. By default, any employee can walk into any office, regardless of their role or department (**Default-Open Pod Networking**). 

To secure the building, you implement three layers of security and access boundaries:
*   **Network Policies**: Install secure checkpoints in the hallways that verify employee ID badges (**Labels**) and only allow specific departments to communicate.
*   **Ingress Controller**: Place a secure reception desk at the main entrance of the building. Visitors enter through a single entrance, and the receptionist routes them to the correct office based on their destination directory (**Host/Path Routing**) and verifies their identity (**TLS Termination**).
*   **Gateway API**: Upgrade the building to a modern, decoupled routing network where the building manager configures the physical entrance interfaces (**Gateway**) while individual teams manage their own specific directory routing paths (**HTTPRoutes**).

### Architectural, Lifecycle & Flow Blueprints

```mermaid
graph TD
    Client[External Client] -->|HTTPS Request| Ingress[Ingress Controller]
    Ingress -->|Decrypts TLS| Svc[ClusterIP Service]
    Svc -->|Load Balances| Pod[Application Pod]
```

```mermaid
sequenceDiagram
    autonumber
    Pod-A->>Network: Inbound Traffic to Pod-B
    Network->>NetPol: Evaluate NetworkPolicy Selector Match
    NetPol-->>Network: Accept / Drop Packet (L4 Port Filter)
```

### Under-the-Hood Mechanics & Internal Operations
At the system validation layer, NetworkPolicies act as local, stateful firewalls managed by the CNI plugin on each node. They are not enforced by the API Server or kubelet. Instead, CNI plugins (such as Calico or Cilium) watch the API Server for changes to NetworkPolicies and translate them into host-level packet filtering rules. Calico writes these rules using kernel `iptables` or IPVS tables, while Cilium writes highly performant `eBPF` programs loaded directly into the kernel's network socket layer, intercepting and filtering packets with minimal latency.

An Ingress resource defines external routing rules but requires an active `Ingress Controller` (such as Nginx Ingress or Traefik) running in the cluster to process those rules. The Ingress Controller acts as a reverse proxy, parsing routing paths, terminating SSL/TLS sessions, and forwarding traffic directly to backing pods.

The Gateway API is a next-generation API that splits these concerns into separate, dedicated resources: infrastructure teams manage `GatewayClass` and `Gateway`, while application developers manage `HTTPRoute` configurations independently.

### Deep-Dive Reference (Advanced Context)
<details>
<summary>NetworkPolicy Ingress, Egress, and CIDR Isolation Rules</summary>
NetworkPolicies allow isolating traffic based on namespace selectors, pod selectors, or CIDR blocks. Ingress rules restrict incoming traffic, while Egress rules restrict outbound traffic. A default-deny policy (which selects all pods with empty curly braces `{}` and defines no ingress/egress rules) blocks all unauthorized traffic by default, forcing teams to explicitly define required network communication paths.
</details>

### Systemic Failure Modes & Boundary Violations
*   **Failure Mode 1: Inter-Namespace Network Isolation Collision**
    *   **Symptom:** Backend microservices fail to connect to database Pods, and requests return connection timeouts.
    *   **Root Cause:** A strict ingress `NetworkPolicy` is applied to the database namespace, blocking incoming traffic from other namespaces that lack the required matching labels.
    *   **Resolution:** Update the database's NetworkPolicy to allow incoming traffic from specific source namespaces using namespace and pod selectors.

*   **Failure Mode 2: SSL Handshake Timeout (Missing or Invalid Private Key)**
    *   **Symptom:** External HTTPS requests fail with SSL handshaking errors, or the browser displays a `Certificate Authority Invalid` warning.
    *   **Root Cause:** The TLS Secret referenced in the Ingress specification is missing, has expired, or the private key does not match the certificate's public key.
    *   **Resolution:** Verify the certificates inside the TLS Secret and ensure they match the hostnames defined in your Ingress resource:
        ```bash
        kubectl describe ingress <ingress-name>
        ```

*   **Failure Mode 3: Ingress Controller Path Redirection Mismatch**
    *   **Symptom:** Accessing subpaths (e.g., `/api`) returns HTTP `404 Not Found` errors from the backend application.
    *   **Root Cause:** The Ingress Controller forwards the entire requested subpath path to the backend container, but the application is only listening on the root path `/`.
    *   **Resolution:** Add path rewrite annotations to the Ingress resource to strip the path prefix before forwarding the traffic to the backend:
        ```yaml
        annotations:
          nginx.ingress.kubernetes.io/rewrite-target: /$1
        ```

### Traceability Schema Check
All network security resources (`NetworkPolicy`), external ingress proxies (`Ingress`), and modern Gateway API specifications used below are conceptually defined in this section.
"""

M5_COMMANDS = r"""### Technical & Syntax Reference Manual
Below are the essential commands for configuring, validating, and auditing network policy isolation and external ingress resources.

*   **NetworkPolicy Configuration Auditing:**
    ```bash
    # View all active NetworkPolicies in the specified namespace
    kubectl get netpol -n production

    # Retrieve detailed status and rules configuration for a NetworkPolicy
    kubectl describe netpol restrict-db-access
    ```

*   **Ingress Operations and Logs:**
    ```bash
    # Get active Ingress rules and external IP allocations in the namespace
    kubectl get ingress

    # Stream real-time logs from the Ingress Controller to debug routing errors
    kubectl logs -n ingress-nginx deployment/ingress-nginx-controller
    ```

### Anatomy & Boundary Table
| Variable / Parameter / Keyword Name | Expected Type / Allowed Values | Default Value / Operating Domain | Strict Structural Constraints |
| :--- | :--- | :--- | :--- |
| `policyTypes` | Array of strings (`Ingress`, `Egress`) | `Ingress` | Determines which directions of traffic the NetworkPolicy applies to. |
| `spec.ingressClassName` | String (e.g., `nginx`, `traefik`) | N/A (Required) | Must match an active Ingress Class registered in the cluster. |
| `spec.rules[*].http.paths[*].pathType` | String (`Prefix`, `Exact`, `ImplementationSpecific`) | `Prefix` | Determines how the controller evaluates the requested URL path. |
| `spec.tls[*].secretName` | String | N/A | Must match an existing Opaque or kubernetes.io/tls Secret containing valid keys. |
"""

M5_EXAMPLES = r"""### Real-World Examples

#### Example 1: Restricting Pod Traffic with NetworkPolicies
*   **Situation:** Secure an application namespace by blocking all incoming traffic to database pods, except for traffic originating from backend API pods.
*   **Action:** Define an Ingress NetworkPolicy in the database namespace.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: restrict-db-access
  namespace: default
spec:
  podSelector:
    matchLabels:
      app: mysql-database
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: backend-api
    ports:
    - protocol: TCP
      port: 3306
```

#### Example 2: Ingress Resource with TLS Termination
*   **Situation:** Expose an internal web application externally using an Ingress resource, securing connection traffic with SSL/TLS certificates.
*   **Action:** Deploy an Ingress resource with a defined TLS configuration block.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: secured-web-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  tls:
  - hosts:
    - app.company.com
    secretName: company-tls-cert
  rules:
  - host: app.company.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-frontend-svc
            port:
              number: 80
```

#### Example 3: Ingress with Host and Path-Based Routing
*   **Situation:** Route external traffic to different backend services based on the request host and URL path.
*   **Action:** Configure an Ingress resource with multiple host and path rules.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: routing-ingress
spec:
  rules:
  - host: api.app.com
    http:
      paths:
      - path: /payments
        pathType: Prefix
        backend:
          service:
            name: payment-svc
            port:
              number: 8080
  - host: portal.app.com
    http:
      paths:
      - path: /dashboard
        pathType: Exact
        backend:
          service:
            name: dashboard-svc
            port:
              number: 80
```

#### Example 4: Gateway API Gateway Configuration
*   **Situation:** Deploy a Gateway resource that listens for HTTP traffic on port 80 across all namespaces.
*   **Action:** Define a Gateway resource using the standard Gateway API specification.

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: public-gateway
  namespace: default
spec:
  gatewayClassName: company-load-balancer
  listeners:
  - name: http-listener
    protocol: HTTP
    port: 80
    allowedRoutes:
      namespaces:
        from: All
```

#### Example 5: Gateway API HTTPRoute Mapping
*   **Situation:** Route web traffic to a payment API based on host pathing.
*   **Action:** Deploy a declarative `HTTPRoute` referencing an established Gateway.

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: payment-route
  namespace: default
spec:
  parentRefs:
  - group: gateway.networking.k8s.io
    kind: Gateway
    name: public-gateway
  rules:
  - matches:
    - path:
        type: PathPrefix
        value: /v2/payments
    backendRefs:
    - name: payment-svc-v2
      port: 8080
```
"""

M5_EXERCISE = r"""### Practical Laboratories & Hands-On Exercises

#### Lab 1: Enforcing Default-Deny Network Isolation
*   **Objective:** Secure a namespace by blocking all incoming and outgoing traffic by default.
*   **Tasks:**
    1. Create a namespace named `secure-zone`.
    2. Apply a default-deny NetworkPolicy targeting all pods in the namespace.
    3. Deploy two test pods in the namespace and verify they cannot communicate with each other.
    4. Deploy a third pod and verify that all external outbound traffic (such as DNS requests) is blocked.

#### Lab 2: Whitelisting Pod Ingress Traffic
*   **Objective:** Allow specific pods to communicate while maintaining network isolation.
*   **Tasks:**
    1. Create a default-deny NetworkPolicy in your development namespace.
    2. Label a target pod with the label `role=database`.
    3. Create an Ingress NetworkPolicy that allows traffic to the database pod, but only if the source pod has the label `role=api`.
    4. Verify that the api pod can connect to the database, but pods with other labels are blocked.

#### Lab 3: Configuring Ingress Routing Routes
*   **Objective:** Route external traffic to distinct endpoints based on URL paths using an Ingress resource.
*   **Tasks:**
    1. Deploy two sample applications: `v1-app` and `v2-app`.
    2. Create corresponding ClusterIP services for both apps.
    3. Deploy an Ingress resource routing `/v1` requests to `v1-app` and `/v2` requests to `v2-app`.
    4. Run local tests using custom header maps to verify path routing.

#### Lab 4: Implementing Ingress TLS Termination
*   **Objective:** Secure an Ingress route with SSL/TLS certificates.
*   **Tasks:**
    1. Generate a self-signed TLS certificate and private key using OpenSSL.
    2. Create a TLS Secret in your cluster using the generated certificate files.
    3. Update your Ingress resource configuration to use the TLS Secret for termination.
    4. Run a curl request using HTTPS and verify the connection is secured.

#### Lab 5: Deploying Gateway API HTTPRoutes
*   **Objective:** Route traffic using the modern Gateway API specification.
*   **Tasks:**
    1. Install the Gateway API Custom Resource Definitions (CRDs) on your cluster.
    2. Define a Gateway resource named `public-gateway`.
    3. Construct and apply an `HTTPRoute` directing path `/api` requests to a backend service.
    4. Query the gateway endpoint to confirm traffic is routed to the backend service.
"""

M5_INSIGHT = r"""### Interview Q&A

#### Q1: How does a stateful NetworkPolicy operate?
*   **Answer:** NetworkPolicies are stateful firewalls. When you define an Ingress rule allowing incoming traffic to a pod, the system automatically permits the corresponding outgoing return traffic, without requiring you to write an explicit egress rule.

#### Q2: What happens if a pod matches multiple NetworkPolicies?
*   **Answer:** NetworkPolicies are additive (logical OR operations). If a pod matches multiple policies, the system combines all permitted rules from those policies. The pod will allow any traffic that is whitelisted by at least one of the applied policies.

#### Q3: Why is an Ingress Controller required to use Ingress resources?
*   **Answer:** An Ingress resource is only a declarative configuration file. It does not perform any actual routing. An Ingress Controller must run in the cluster (such as Nginx Ingress or Traefik) to watch for Ingress resources, parse their routing rules, and configure its reverse-proxy engine to route traffic.

#### Q4: What is the difference between Ingress and the Gateway API?
*   **Answer:** Ingress is a single resource that combines routing paths, TLS certificates, and provider-specific configurations. The Gateway API is a next-generation API that splits these concerns into separate, dedicated resources: infrastructure teams manage `GatewayClass` and `Gateway`, while application developers manage `HTTPRoute` configurations independently.

#### Q5: How do pathTypes (Exact versus Prefix) affect Ingress routing?
*   **Answer:** `Exact` matches the request path exactly (e.g., a rule for `/api` will only match `/api` and not `/api/v1`). `Prefix` matches any sub-paths that start with the prefix (e.g., a rule for `/api` will match `/api`, `/api/v1`, and `/api/v1/users`).

### CKA Exam Focus
- NetworkPolicies only work if your CNI plugin supports them (such as Calico or Cilium). On clusters using Flannel, NetworkPolicies are silently ignored.
- Remember that namespaces must be labeled correctly to use them in NetworkPolicy `namespaceSelectors`.
"""

# =====================================================================
# MODULE 6: STORAGE PRIMITIVES, DYNAMIC PROVISIONING, & STATEFUL MOUNTS
# =====================================================================

M6_THEORY = r"""### Guided Conceptual Walkthrough
Imagine you run a large private university library. If students (application processes or Pods) write their research notes directly on their tables (**Ephemeral Storage**), their work is wiped out whenever they leave the library (**Pod Restart**). 

To ensure data persists, you establish a professional archiving system:
*   **PersistentVolume (PV)**: Dedicate a set of permanent storage lockers in the basement of the library (**Physical Block Storage**).
*   **PersistentVolumeClaim (PVC)**: Students use dynamic request cards (**PVC**) to claim a locker with specific size requirements and access parameters (**Access Modes**).
*   **StorageClass**: For larger volumes, you set up an automated dynamic locker generator (**StorageClass**) that builds and assigns lockers on demand, avoiding the need for manual setup.

### Architectural, Lifecycle & Flow Blueprints

```mermaid
graph TD
    Pod[Application Pod] -->|Mounts Claim| PVC[PersistentVolumeClaim]
    PVC -->|Binds to| PV[PersistentVolume]
    SC[StorageClass] -->|Dynamically Provisions| PV
```

```mermaid
sequenceDiagram
    autonumber
    PodDeploy->>PVC: Create claim requesting GP3 SC (10Gi)
    SC->>CSI: Trigger AWS EBS API allocation
    CSI-->>SC: Confirm volume created
    SC->>PV: Register PersistentVolume object
    PV->>PVC: Bind claim to volume
    Kubelet->>Pod: Mount physical volume path inside container
```

### Under-the-Hood Mechanics & Internal Operations
Decoupling application configuration and storage from container images is a core principle of cloud-native architecture. 
1. **PV access patterns**: Defined by Access Modes (`ReadWriteOnce` for single-node read-write, `ReadOnlyMany` for multi-node read-only, and `ReadWriteMany` for multi-node read-write).
2. **Reclaim Policy**: Controls what happens to the underlying storage block when a PVC is deleted (either `Delete` to remove the physical storage block automatically, or `Retain` to preserve the volume for manual recovery).
3. **CSI Driver**: Runs as a localized controller within the cluster. It intercepts volume claim events and executes secure APIs directly against cloud or block storage providers, automating disk allocations, attachments, formatting, and partition mounts on worker nodes.

### Deep-Dive Reference (Advanced Context)
<details>
<summary>Volume Modes and StatefulSet Storage Patterns</summary>
Kubernetes supports two volume modes: `Filesystem` (the default mode, where volumes are mounted as a directory) and `Block` (which exposes the raw block device directly to the container, bypassing the filesystem layer for high-performance databases). When running stateful applications using StatefulSets, administrators define a `volumeClaimTemplates` block. This ensures that each generated replica receives a unique, dedicated PersistentVolumeClaim (PVC) that persists across Pod restarts and re-scheduling.
</details>

### Systemic Failure Modes & Boundary Violations
*   **Failure Mode 1: PVC stuck in Pending state (Provisioning Timeout)**
    *   **Symptom:** PVC status remains stuck in `Pending`, and running describe commands reports `volume provisioning failed` or `StorageClass not found`.
    *   **Root Cause:** The requested StorageClass does not exist in the cluster, or the underlying CSI driver controller is crashing or missing IAM permissions.
    *   **Resolution:** Verify that the referenced StorageClass is active, and inspect the CSI controller logs:
        ```bash
        kubectl get sc
        kubectl logs -n kube-system deployment/ebs-csi-controller
        ```

*   **Failure Mode 2: Multi-Node Mount Conflict (ReadWriteOnce Violation)**
    *   **Symptom:** Pod remains stuck in `ContainerCreating` or `Multi-Attach error for volume`, and events show `Volume is already used by another Pod`.
    *   **Root Cause:** A Pod is scheduled to a different worker node and is trying to mount a PersistentVolume configured with `ReadWriteOnce` access mode, while the volume is already mounted to another node.
    *   **Resolution:** Ensure your application uses a deployment configuration that terminates old Pods before starting new ones, or use a StorageClass that supports `ReadWriteMany` (like NFS or Ceph).

*   **Failure Mode 3: Retained PV Re-claim Blocked**
    *   **Symptom:** Creating a new PVC that references a released, retained PV remains stuck in `Pending`.
    *   **Root Cause:** The PV is marked with a status of `Released` and has a previous claim reference in its metadata, which blocks other claims from binding to it.
    *   **Resolution:** Manually edit the PV resource to clear its `claimRef` block, allowing new PVCs to bind to the volume.

### Traceability Schema Check
All storage resources (`StorageClass`, `PersistentVolumeClaim`, `PersistentVolume`), access modes, reclaim policies, and mounting parameters used below are conceptually defined in this section.
"""

M6_COMMANDS = r"""### Technical & Syntax Reference Manual
Below are the essential commands for managing storage configurations, volume claims, and verifying bound states.

*   **Storage Auditing and Listing:**
    ```bash
    # List all active StorageClasses inside the cluster
    kubectl get sc

    # Retrieve all PersistentVolumes sorted by storage size
    kubectl get pv --sort-by=.spec.capacity.storage

    # View PersistentVolumeClaims configured in the namespace
    kubectl get pvc -n production
    ```

*   **Mount Verification and Volume Diagnostics:**
    ```bash
    # Describe detailed binding logs and provisioner statuses for a PVC
    kubectl describe pvc app-storage-claim

    # Verify physical disk mounts directly on a worker node using SSH
    ssh node-01 "df -h"
    ```

### Anatomy & Boundary Table
| Variable / Parameter / Keyword Name | Expected Type / Allowed Values | Default Value / Operating Domain | Strict Structural Constraints |
| :--- | :--- | :--- | :--- |
| `spec.storageClassName` | String | N/A | Must match an existing, active StorageClass name in the cluster. |
| `spec.accessModes` | Array of strings (`ReadWriteOnce`, `ReadOnlyMany`, `ReadWriteMany`) | N/A (Required) | Determines how many nodes can mount and write to the volume concurrently. |
| `spec.persistentVolumeReclaimPolicy` | String (`Delete`, `Retain`) | `Delete` | Defines how the cluster handles the physical volume when the PVC is deleted. |
| `spec.volumeMode` | String (`Filesystem`, `Block`) | `Filesystem` | Defines whether the volume is formatted with a filesystem or exposed as raw block. |
"""

M6_EXAMPLES = r"""### Real-World Examples

#### Example 1: Static PersistentVolume (hostPath)
* **Situation:** Pre-provision static host storage on a worker node and bind it to a development application.
* **Action:** Deploy a PersistentVolume matched to a PersistentVolumeClaim.

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: static-data-pv
spec:
  storageClassName: manual
  capacity:
    storage: 5Gi
  accessModes:
    - ReadWriteOnce
  hostPath:
    path: "/mnt/data/v1"
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: static-data-pvc
spec:
  storageClassName: manual
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
```

#### Example 2: Dynamic Volume Provisioning StorageClass
* **Situation:** Enable dynamic volume provisioning using a local storage provisioner that waits for the consuming pod before binding.
* **Action:** Deploy a StorageClass with `volumeBindingMode: WaitForFirstConsumer`.

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: local-wait-storage
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: WaitForFirstConsumer
reclaimPolicy: Delete
```

#### Example 3: Dynamic PersistentVolumeClaim
* **Situation:** A development application needs a 10Gi volume allocated automatically using the local wait storage class.
* **Action:** Define a PersistentVolumeClaim requesting the storage class.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: local-pvc
  namespace: default
spec:
  storageClassName: local-wait-storage
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

#### Example 4: StatefulSet with volumeClaimTemplates
* **Situation:** Deploy a multi-replica key-value database (e.g., Redis) where each replica requires a distinct persistent disk.
* **Action:** Define a StatefulSet containing a `volumeClaimTemplates` definition.

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: local-kv-store
spec:
  serviceName: kv-internal
  replicas: 2
  selector:
    matchLabels:
      app: kv-store
  template:
    metadata:
      labels:
        app: kv-store
    spec:
      containers:
      - name: storage-node
        image: redis:7.0-alpine
        ports:
        - containerPort: 6379
          name: redis
        volumeMounts:
        - name: redis-persistent-data
          mountPath: /data
  volumeClaimTemplates:
  - metadata:
      name: redis-persistent-data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: "local-wait-storage"
      resources:
        requests:
          storage: 2Gi
```

#### Example 5: High-Speed Scratchpad emptyDir Mount
* **Situation:** A heavy data-processing pipeline requires high-speed scratch space that is automatically purged when the pod terminates.
* **Action:** Mount a high-performance in-memory `emptyDir` volume.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: scratchpad-app
spec:
  containers:
  - name: processor
    image: alpine:3.18
    command: ["/bin/sh", "-c", "dd if=/dev/urandom of=/scratch/temp.bin bs=1M count=100 && sleep 3600"]
    volumeMounts:
    - name: temp-disk
      mountPath: /scratch
  volumes:
  - name: temp-disk
    emptyDir:
      medium: Memory
      sizeLimit: 512Mi
```
"""

M6_EXERCISE = r"""### Practical Laboratories & Hands-On Exercises

#### Lab 1: Setting Up HostPath Storage
* **Objective:** Create a static hostPath PersistentVolume and bind a claim to it.
* **Tasks:**
    1. Create a PersistentVolume named `host-pv` with a capacity of `2Gi` mapping to hostPath `/mnt/data`.
    2. Create a PersistentVolumeClaim named `host-pvc` with a capacity of `2Gi` and access mode `ReadWriteOnce`.
    3. Verify that the PV status changes from `Available` to `Bound` using `kubectl get pv`.
    4. Deploy a test pod that mounts the PVC and writes a file to the volume.

#### Lab 2: Dynamic Volume Provisioning
* **Objective:** Dynamic provisioning test with default cluster storage.
* **Tasks:**
    1. Retrieve the list of active StorageClasses on your cluster.
    2. Create a PVC referencing one of the active StorageClasses.
    3. Deploy a temporary Pod that mounts this dynamic PVC.
    4. Confirm that a PersistentVolume (PV) was created automatically by the storage class.

#### Lab 3: Validating Reclaim Policies
* **Objective:** Observe data retention behaviors when reclaiming storage.
* **Tasks:**
    1. Create a PV with reclaim policy set to `Retain`.
    2. Create a PVC that binds to this PV.
    3. Deploy a pod, write test files to the mounted volume, and then delete the pod and PVC.
    4. Verify that the PV state changes to `Released` but is NOT deleted.
    5. Check the target host node to verify that the physical test files are preserved.

#### Lab 4: StatefulSet Dynamic Volume Mounts
* **Objective:** Deploy database replicas with distinct volumes using StatefulSets.
* **Tasks:**
    1. Create a headless service for a StatefulSet.
    2. Deploy a StatefulSet with 2 replicas using a `volumeClaimTemplates` block.
    3. Verify that two distinct PVCs and two PVs are created automatically.
    4. Delete one of the StatefulSet pods and verify that the rescheduled pod rebinds to its original volume.

#### Lab 5: Ephemeral emptyDir Volume Mounting
* **Objective:** Mount in-memory scratch space in container applications.
* **Tasks:**
    1. Create a Pod with an `emptyDir` volume using the `Memory` medium.
    2. Configure the container to mount the volume and write temporary diagnostic files.
    3. Verify that the volume mounts and writes successfully.
    4. Delete the pod and verify that the temporary memory allocation is purged.
"""

M6_INSIGHT = r"""### Interview Q&A

#### Q1: What are the three PersistentVolume access modes?
* **Answer:**
  - **ReadWriteOnce (RWO):** Volume can be mounted as read-write by a single node.
  - **ReadOnlyMany (ROX):** Volume can be mounted read-only by many nodes.
  - **ReadWriteMany (RWX):** Volume can be mounted as read-write by many nodes.

#### Q2: What are the PV reclaim policies?
* **Answer:**
  - **Retain:** The physical storage is preserved, allowing administrators to recover data manually. No other PVC can claim this PV until it is manually scrubbed.
  - **Delete:** The physical storage and the PV are deleted automatically.

#### Q3: Why does a dynamic PVC create a PV automatically?
* **Answer:** When a PVC is created, the API server checks if it references a StorageClass. If it does, the StorageClass provisioner (e.g., a CSI plugin) automatically provisions the requested storage, creates a matching PersistentVolume (PV), and binds it to the PVC.

#### Q4: How does volumeBindingMode: WaitForFirstConsumer improve scheduling?
* **Answer:** By delaying volume provisioning until the pod is scheduled, the StorageClass ensures that the volume is created in the correct availability zone where the pod runs, preventing scheduling conflicts on multi-node clusters.

#### Q5: What happens to hostPath data when a pod is rescheduled?
* **Answer:** Since hostPath volumes write data directly to the host node's filesystem, if the pod is rescheduled to a *different* node, it will mount the directory on that new node, losing access to its original data.

### CKA Exam Focus
- Understand the distinction between cluster-scoped resources (`PersistentVolume`) and namespace-scoped resources (`PersistentVolumeClaim`).
- Remember that you must delete the consuming Pod first before you can successfully delete a bound PersistentVolumeClaim (PVC).
"""

# =====================================================================
# MODULE 7: CLUSTER ACCESS CONTROL, AUTHENTICATION, & ENTERPRISE RBAC
# =====================================================================

M7_THEORY = r"""### Guided Conceptual Walkthrough
Imagine a high-security research facility. If every scientist has unrestricted master access keys (**Root Access**), they could accidentally access other rooms, modify secure experiments, or compromise the entire facility. 

To secure the facility, you set up strict security boundaries:
*   **ServiceAccounts & Roles**: Assign specific keycard permissions to users and application processes, restricting what folders they can read and write inside specific rooms (**Namespace Rules**).
*   **ClusterRoles**: Define global, cluster-wide keycard permissions to govern cluster-scoped resources (such as nodes or physical storage volumes) across all namespaces.
*   **Certificate Signing Request (CSR) API**: Set up an automated credentials office where new scientists submit their identification files (**CSR**) to receive signed access certificates.

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
    Client->>API: API Request (Auth Token)
    API->>API: Authenticate Client Identity (AuthN)
    API->>API: Evaluate RBAC Role Bindings (AuthZ)
    API->>API: Process Admission Control Checks
    API->>ETCD: Commit Object State Transitions
```

### Under-the-Hood Mechanics & Internal Operations
At the system validation layer, every API request made to the `kube-apiserver` must pass through three sequential phases: Authentication, Authorization, and Admission Control before any state changes are committed to etcd.

For Authorization, the API Server queries the active Role-Based Access Control (RBAC) cache database. It matches the request's token (or ServiceAccount ID) against the defined `RoleBindings` and `ClusterRoleBindings`. If a valid binding exists that permits the requested API verb (e.g., `get` or `list`) on the target resource, the request is authorized. 

Human users are authenticated externally using client certificates signed by the cluster's CA, while application processes use ServiceAccounts, which carry secure API tokens mounted directly as files inside the container filesystem.

### Deep-Dive Reference (Advanced Context)
<details>
<summary>Namespace-Scoped Roles versus ClusterRoles</summary>
A `Role` defines namespace-scoped permissions, meaning its access rules apply only within the namespace where it is deployed. A `ClusterRole` defines non-namespaced, cluster-wide permissions. It can be bound globally using a `ClusterRoleBinding` to grant access across all namespaces, or bound locally using a `RoleBinding` to restrict those cluster-wide permissions to a single target namespace.
</details>

### Systemic Failure Modes & Boundary Violations
*   **Failure Mode 1: Pod API Request Unauthorized (RBAC Permissions Denied)**
    *   **Symptom:** Application container logs report `HTTP 403 Forbidden` or `User system:serviceaccount:default:app-sa cannot list resource pods in API group`.
    *   **Root Cause:** The `ServiceAccount` assigned to the Pod is missing the necessary `RoleBinding` or permissions to interact with the API Server.
    *   **Resolution:** Verify the Role and RoleBinding configurations and ensure they are bound to the correct ServiceAccount inside the target namespace:
        ```bash
        kubectl auth can-i list pods --as=system:serviceaccount:default:app-sa
        ```

*   **Failure Mode 2: Client Certificate Expired (Authentication Failure)**
    *   **Symptom:** Running `kubectl` commands returns the error `Unable to connect to the server: x509: certificate has expired`.
    *   **Root Cause:** The client certificate used by the user context has exceeded its validity lifetime and is rejected by the API Server.
    *   **Resolution:** Renew the client certificate using the Certificate Signing Request (CSR) API.

*   **Failure Mode 3: Missing CA Bundle in Webhook Configuration**
    *   **Symptom:** API requests fail with SSL handshaking errors, or the browser displays a `Certificate Authority Invalid` warning.
    *   **Root Cause:** The `ValidatingWebhookConfiguration` or mutating webhook is missing the valid `caBundle` certificate required to verify the webhook server.
    *   **Resolution:** Retrieve the cluster's root CA certificate and inject it into the webhook configuration's `caBundle` field.

### Traceability Schema Check
All access control resources (`ServiceAccount`, `Role`, `ClusterRole`, `RoleBinding`, `ClusterRoleBinding`), user authentication mechanisms, and certificate APIs used below are conceptually defined in this section.
"""

M7_COMMANDS = r"""### Technical & Syntax Reference Manual
Below are the essential commands for auditing cluster access control policies and managing user authentication.

*   **RBAC Permissions Validation:**
    ```bash
    # Verify if a specific ServiceAccount has permission to list Pods in the namespace
    kubectl auth can-i list pods --as=system:serviceaccount:default:app-sa

    # Check write operations permissions across all namespaces in the cluster
    kubectl auth can-i create deployments --all-namespaces
    ```

*   **Managing Cluster Access Roles:**
    ```bash
    # Create an RBAC Role with read-only access to pods inside a namespace
    kubectl create role pod-reader --verb=get,list,watch --resource=pods -n default

    # Bind a ServiceAccount to a Role inside a specific namespace
    kubectl create rolebinding read-pods-bind --role=pod-reader --serviceaccount=default:app-sa -n default
    ```

### Anatomy & Boundary Table
| Variable / Parameter / Keyword Name | Expected Type / Allowed Values | Default Value / Operating Domain | Strict Structural Constraints |
| :--- | :--- | :--- | :--- |
| `rules[*].apiGroups` | Array of API groups (e.g., `""`, `apps`) | N/A | Use `""` to target core resources like Pods, Services, and ConfigMaps. |
| `rules[*].resources` | Array of resources | N/A (Required) | Must contain lowercase plural resource names matching API specifications. |
| `rules[*].verbs` | Array of verbs (e.g., `get`, `list`, `create`) | N/A (Required) | Case-sensitive list of permitted operations. |
| `subjects[*].kind` | String (`User`, `Group`, `ServiceAccount`) | N/A | Defines the target identity type being bound to the Role. |
"""

M7_EXAMPLES = r"""### Real-World Examples

#### Example 1: ServiceAccount with Explicit Token Secret
* **Situation:** A continuous integration (CI) tool needs a long-lived API token associated with a ServiceAccount to deploy applications.
* **Action:** Create a ServiceAccount and map it to an explicit token Secret.

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: deployment-sa
  namespace: default
---
apiVersion: v1
kind: Secret
metadata:
  name: deployment-sa-token
  namespace: default
  annotations:
    kubernetes.io/service-account.name: "deployment-sa"
type: kubernetes.io/service-account-token
```

#### Example 2: Namespace-Scoped Role and RoleBinding
* **Situation:** Give developers read-write access to deployments, replicasets, and pods inside the `development` namespace.
* **Action:** Define a Role and a RoleBinding for the development group.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: dev-developer-role
  namespace: default
rules:
- apiGroups: ["", "apps"]
  resources: ["pods", "deployments", "replicasets"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: dev-developer-binding
  namespace: default
subjects:
- kind: Group
  name: "dev-engineers"
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: dev-developer-role
  apiGroup: rbac.authorization.k8s.io
```

#### Example 3: ClusterRole and ClusterRoleBinding for Global Read Access
* **Situation:** A monitoring tool needs read-only access to nodes, namespaces, and services across all namespaces in the cluster.
* **Action:** Define a ClusterRole and a ClusterRoleBinding.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: global-monitoring-role
rules:
- apiGroups: [""]
  resources: ["nodes", "namespaces", "services"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: global-monitoring-binding
subjects:
- kind: ServiceAccount
  name: monitoring-sa
  namespace: default
roleRef:
  kind: ClusterRole
  name: global-monitoring-role
  apiGroup: rbac.authorization.k8s.io
```

#### Example 4: CertificateSigningRequest (CSR) Manifest
* **Situation:** Add a external developer named `alice` to the cluster by submitting her Certificate Signing Request (CSR) to the API server.
* **Action:** Define and submit a CSR manifest containing the base64-encoded request.

```yaml
apiVersion: certificates.k8s.io/v1
kind: CertificateSigningRequest
metadata:
  name: alice-dev-csr
spec:
  request: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURSBSRVFVRVNULS0tLS0KTUI0Q0FEQWdBb0dDQm9SME93R0NBUXN0R0NBR0JnQXdBREVMTUFrR0ExVUVCaE1DVlZNd0NnWURWUVFLREFoTApVbVZ6ZDJWeWR6RUxNQWtHQTFVRUF3d0NZV3hwWTJWek1GNHdEallEVlFRRERBaE9iM0psWlhScGJDQlRiM0psYVc1bklGTmhibVIyYjNJZwpVMDVGVkdVZ0FvR0NDb1IweURXQXdFSE1GNHdEallEVlFRSERBaE9iM0psWlhScGJDQlRiM0psYVc1bklGTmhKYm1SMmIzSWdVMDVGVkdVZ0FvR0NDb1IweURXQXdFSAotLS0tLUVORCBDRVJUSUZJQ0FURSBSRVFVRVNULS0tLS0K
  signerName: kubernetes.io/kube-apiserver-client
  usages:
  - client auth
```

#### Example 5: Custom Kubeconfig Context Configuration
* **Situation:** Configure a developer's local `kubeconfig` file to switch between production and staging contexts using client certificates.
* **Action:** Create a syntax-compliant kubeconfig structure.

```yaml
apiVersion: v1
kind: Config
clusters:
- cluster:
    certificate-authority: /etc/kubernetes/pki/ca.crt
    server: https://192.168.1.10:6443
  name: cluster.local
users:
- name: developer-alice
  user:
    client-certificate: /home/alice/.certs/alice.crt
    client-key: /home/alice/.certs/alice.key
contexts:
- context:
    cluster: cluster.local
    user: developer-alice
    namespace: default
  name: alice-context
current-context: alice-context
```
"""

M7_EXERCISE = r"""### Practical Laboratories & Hands-On Exercises

#### Lab 1: Restricting Pod Access using RBAC Roles
* **Objective:** Restrict a ServiceAccount so it can only list and modify pods within a single namespace.
* **Tasks:**
    1. Create a namespace named `rbac-sandbox`.
    2. Create a ServiceAccount named `read-write-sa` inside the namespace.
    3. Create a Role named `pod-manager` in `rbac-sandbox` that allows all verbs on `pods`.
    4. Bind the ServiceAccount to the Role using a RoleBinding.
    5. Verify the permissions using `kubectl auth can-i get pods --as=system:serviceaccount:rbac-sandbox:read-write-sa -n rbac-sandbox`.

#### Lab 2: Delegating Cluster-Wide Permissions
* **Objective:** Grant cluster-wide view access to a specific monitoring user.
* **Tasks:**
    1. Create a ServiceAccount named `collector-sa` in the `kube-system` namespace.
    2. Create a ClusterRoleBinding that binds `collector-sa` to the default `view` ClusterRole.
    3. Verify that `collector-sa` can list resources (like nodes and namespaces) across the entire cluster.
    4. Confirm that the ServiceAccount is blocked from creating or modifying resources.

#### Lab 3: Creating and Approving a Certificate Signing Request (CSR)
* **Objective:** Add a new user to the cluster using the Certificate Signing Request API.
* **Tasks:**
    1. Generate a private key and a CSR on your local machine using OpenSSL.
    2. Write a CertificateSigningRequest manifest containing the base64-encoded CSR and submit it to the API server.
    3. View the pending request using `kubectl get csr`.
    4. Approve the request using `kubectl certificate approve <csr-name>`.
    5. Retrieve the issued client certificate and verify its details.

#### Lab 4: Creating a Custom Multi-Cluster Kubeconfig
* **Objective:** Configure a kubeconfig file to switch between contexts and namespaces.
* **Tasks:**
    1. Create a copy of your existing `~/.kube/config` file to use as a template.
    2. Define a new context that defaults to the `kube-system` namespace.
    3. Switch to the new context using `kubectl config use-context`.
    4. Run a command (such as `kubectl get pods`) and verify it runs in the `kube-system` namespace by default.

#### Lab 5: Auditing Cluster Permissions
* **Objective:** Use kubectl commands to audit user permissions across the cluster.
* **Tasks:**
    1. Find all ClusterRoleBindings that reference the default `admin` or `cluster-admin` roles.
    2. Check if a specific ServiceAccount has permissions to read secrets in the `default` namespace.
    3. Test if a user can delete nodes using `kubectl auth can-i delete nodes --as=<user-name>`.
    4. Identify which roles grant write permissions within a production namespace.
"""

M7_INSIGHT = r"""### Interview Q&A

#### Q1: What is the difference between a RoleBinding and a ClusterRoleBinding?
* **Answer:** A `RoleBinding` applies permissions to a specific namespace. It can bind users or service accounts to a namespace-scoped Role, or to a ClusterRole (which limits those cluster-wide permissions to that single namespace). A `ClusterRoleBinding` applies permissions cluster-wide across all namespaces and can only bind to a `ClusterRole`.

#### Q2: What does a RoleBinding do when bound to a ClusterRole?
* **Answer:** It grants the permissions defined in the ClusterRole, but restricts them strictly to the namespace where the RoleBinding is defined. This allows administrators to define common roles (like `view` or `edit`) once as ClusterRoles, and reuse them across multiple namespaces using individual RoleBindings.

#### Q3: Why does Kubernetes require a signerName when creating a CSR?
* **Answer:** The `signerName` specifies which certificate authority (CA) or system component should sign the certificate. For client certificates, using `kubernetes.io/kube-apiserver-client` ensures the issued certificate is signed by the cluster's root CA and accepted by the API server for authentication.

#### Q4: How do ServiceAccounts authenticate when running inside a Pod?
* **Answer:** When a pod is created, Kubernetes mounts the ServiceAccount's API token, certificate, and namespace information as a volume at `/var/run/secrets/kubernetes.io/serviceaccount`. Internal application processes or client libraries read these files to authenticate their API requests.

#### Q5: What is the difference between Authentication and Authorization in Kubernetes?
* **Answer:** Authentication (AuthN) verifies *who* is making the request (e.g., confirming the requester is indeed user `alice`). Authorization (AuthZ) verifies *what* that authenticated user is allowed to do (e.g., confirming if `alice` has permission to run `kubectl delete pod`).

### CKA Exam Focus
- Learn to use `kubectl auth can-i` with the `--as` flag to quickly verify RBAC configurations during the exam.
- Remember that API group names must be specified correctly in RBAC manifests (e.g., the `apps` group for Deployments, or an empty string `""` for core resources like Pods and Secrets).
"""

# =====================================================================
# MODULE 8: CONTROL PLANE & NODE-LEVEL DISASTER RECOVERY & TROUBLESHOOTING
# =====================================================================

M8_THEORY = r"""### Guided Conceptual Walkthrough
Imagine you run a large private power plant. To prevent facility-wide blackouts (**Cluster Outages**), you set up highly sophisticated backup and disaster recovery systems:
*   **etcdctl Backups**: Set up an automated backup system to routinely capture snapshots of the central power grid control logs (**etcd snapshots**).
*   **Kubelet System Diagnostics**: Install local diagnostic sensors (**systemctl & journalctl**) on every power generator (**Worker Nodes**). If a generator overheats or experiences high load pressure (**Disk/Memory/PID Pressure**), the sensors immediately alert operators.
*   **Static Pod Recovery**: Install automated backup files (**Static Pod Manifests**). If the main control plane indicators crash, the local node backup system automatically restarts them, restoring power within seconds.

### Architectural, Lifecycle & Flow Blueprints

```mermaid
graph TD
    Host[Host Node] -->|Reads Manifests| Kubelet[Local Kubelet Daemon]
    Kubelet -->|Spawns| StaticPod[Static Pod: API Server]
    Kubelet -->|Reports Status| API[K8s API Server]
```

```mermaid
sequenceDiagram
    autonumber
    Kubelet->>Node: Monitor CPU & Memory Load
    Node->>Kubelet: Memory Allocation Exceeds Limit
    Kubelet->>Kubelet: Mark Node Condition: MemoryPressure
    Kubelet->>API: Send Node Status: NotReady
```

### Under-the-Hood Mechanics & Internal Operations
At the system execution layer, static Pods are managed directly by the host node's local `kubelet` agent, bypassing the API Server scheduler. The kubelet watches a specific host directory (typically `/etc/kubernetes/manifests/`) for YAML manifest files. If a file is added, modified, or deleted, the kubelet immediately creates, restarts, or terminates the corresponding static Pod container process, keeping the core control plane components highly available.

If a worker node experiences high load, the Kubelet's resource evictor kicks in. The Kubelet monitors system resource thresholds (such as memory, disk, and PID allocations). If usage exceeds defined limits, the Kubelet flags the node with specific conditions (such as `MemoryPressure` or `DiskPressure`), stops scheduling new Pods, and begins evicting `BestEffort` and `Burstable` Pods to protect host stability.

### Deep-Dive Reference (Advanced Context)
<details>
<summary>etcd snapshot recovery and certificates check-expiration</summary>
Disaster recovery for the cluster's state database requires performing an offline restore using `etcdctl`. SREs stop the local etcd container, run the restore command to write the snapshot data to a new directory, and update the static Pod manifest to point to the restored files. Additionally, the cluster's TLS certificates (stored in `/etc/kubernetes/pki/`) must be audited regularly using `kubeadm certs check-expiration` to prevent sudden connection outages due to certificate expiration.
</details>

### Systemic Failure Modes & Boundary Violations
*   **Failure Mode 1: Kubelet fails to start due to swap active**
    *   **Symptom:** Worker nodes enter a `NotReady` state, and the kubelet service crashes on startup.
    *   **Root Cause:** The host node has swap partition active, which violates the Kubelet's resource accounting checks.
    *   **Resolution:** Disable swap permanently and restart the service:
        ```bash
        sudo swapoff -a
        sudo systemctl restart kubelet
        ```

*   **Failure Mode 2: etcd Database Space Quota Exhausted**
    *   **Symptom:** All cluster write operations fail with the error `etcdserver: mvcc: database space exceeded`.
    *   **Root Cause:** The etcd database file has reached its maximum size limit due to fragmented keys or missing historical compaction policies.
    *   **Resolution:** Compact etcd keys, run defragmentation, and clear the database alarm:
        ```bash
        etcdctl --endpoints=https://127.0.0.1:2379 compact 1000
        etcdctl --endpoints=https://127.0.0.1:2379 defrag
        etcdctl --endpoints=https://127.0.0.1:2379 alarm disarm
        ```

*   **Failure Mode 3: API Server Static Pod manifest parsing error**
    *   **Symptom:** The API Server stops responding, and `kubectl` commands return connection refused errors.
    *   **Root Cause:** A syntax error or typo was introduced in one of the static Pod manifests inside `/etc/kubernetes/manifests/`.
    *   **Resolution:** SSH into the control plane host, locate the modified manifest, and fix the syntax error:
        ```bash
        sudo nano /etc/kubernetes/manifests/kube-apiserver.yaml
        ```

### Traceability Schema Check
All control plane components (etcd, API Server), static Pod configurations, node-level diagnostics, and certificate checking APIs used below are conceptually defined in this section.
"""

M8_COMMANDS = r"""### Technical & Syntax Reference Manual
Below are the essential commands for auditing control plane health, checking certificates, and performing etcd disaster recovery.

*   **etcd Database Snapshot and Recovery:**
    ```bash
    # Securely capture a point-in-time snapshot of the etcd database state
    ETCDCTL_API=3 etcdctl \
      --endpoints=https://127.0.0.1:2379 \
      --cacert=/etc/kubernetes/pki/etcd/ca.crt \
      --cert=/etc/kubernetes/pki/etcd/server.crt \
      --key=/etc/kubernetes/pki/etcd/server.key \
      snapshot save /var/backups/etcd-snapshot.db

    # Restore an etcd snapshot to a new recovery directory
    ETCDCTL_API=3 etcdctl --data-dir=/var/lib/etcd-recovered snapshot restore /var/backups/etcd-snapshot.db
    ```

*   **Cluster Certificates Auditing:**
    ```bash
    # Verify expiration dates of all control plane certificates
    kubeadm certs check-expiration

    # Manually renew all control plane certificates
    kubeadm certs renew all
    ```

### Anatomy & Boundary Table
| Variable / Parameter / Keyword Name | Expected Type / Allowed Values | Default Value / Operating Domain | Strict Structural Constraints |
| :--- | :--- | :--- | :--- |
| `etcdctl` --endpoints | String (URL) | `https://127.0.0.1:2379` | Must point to a valid, reachable etcd cluster member node. |
| static Pod directory | Absolute Directory Path | `/etc/kubernetes/manifests` | Any manifest file placed in this directory is automatically run as a static Pod. |
| `kubeadm certs check-expiration` | Command | N/A | Must be executed on a control plane master node with root/sudo permissions. |
| `--pod-network-cidr` | CIDR IP address block | N/A | Must match the target subnet defined in your CNI configuration file exactly. |
"""

M8_EXAMPLES = r"""### Real-World Examples

#### Example 1: Kubelet Systemd Troubleshooting Configuration File
* **Situation:** A worker node is `NotReady`. An administrator must inspect and configure the `kubelet` systemd unit file on the host machine.
* **Action:** Review and repair the systemd unit file.

```ini
[Unit]
Description=Kubernetes Kubelet
Documentation=https://github.com/kubernetes/kubernetes
After=containerd.service
Requires=containerd.service

[Service]
ExecStart=/usr/bin/kubelet \
  --config=/var/lib/kubelet/config.yaml \
  --container-runtime-endpoint=unix:///var/run/containerd/containerd.sock \
  --kubeconfig=/etc/kubernetes/kubelet.conf \
  --register-node=true
Restart=always
StartLimitInterval=0
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Example 2: Static Pod manifest for diagnostic agent
* **Situation:** Deploy a temporary diagnostic tool on a specific node without using the scheduling control plane.
* **Action:** Write a Pod manifest directly into the host's static pods directory `/etc/kubernetes/manifests/diagnostics.yaml`.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: node-diagnostic-agent
  namespace: kube-system
spec:
  containers:
  - name: diagnostic-container
    image: alpine:3.18
    command: ["/bin/sh", "-c", "while true; do echo 'Healthy'; sleep 30; done"]
    securityContext:
      privileged: true
```

#### Example 3: Automated etcd Snapshot Backup Script
* **Situation:** Set up an automated script to take scheduled snapshots of the etcd database using cluster certificates.
* **Action:** Write a bash script that handles authentication and outputs dated snapshots.

```bash
#!/bin/bash
export ETCDCTL_API=3
BACKUP_PATH="/var/lib/db/etcd-backups"
mkdir -p "${BACKUP_PATH}"

etcdctl \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  snapshot save "${BACKUP_PATH}/etcd-backup-$(date +%F-%H%M).db"
```

#### Example 4: etcd Static Pod Configuration
* **Situation:** Update etcd to use a restored data directory after performing a disaster recovery restore.
* **Action:** Modify the host's etcd static pod manifest at `/etc/kubernetes/manifests/etcd.yaml`.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: etcd
  namespace: kube-system
spec:
  containers:
  - name: etcd
    image: registry.k8s.io/etcd:3.5.9-0
    command:
    - etcd
    - --data-dir=/var/lib/etcd-new
    - --listen-client-urls=https://127.0.0.1:2379
    volumeMounts:
    - mountPath: /var/lib/etcd-new
      name: etcd-data
  volumes:
  - hostPath:
      path: /var/lib/etcd-new
    name: etcd-data
```

#### Example 5: Upgrading Worker Node Kubelet Daemon
* **Situation:** Complete the upgrade of a worker node by installing the target version of the kubelet and restarting the service.
* **Action:** Run package manager commands to upgrade and restart the kubelet.

```bash
#!/bin/bash
# Upgrade the kubelet binary on Debian-based hosts
apt-mark unhold kubelet
apt-get update && apt-get install -y kubelet=1.28.0-00
apt-mark hold kubelet

# Reload and restart the systemd service
systemctl daemon-reload
systemctl restart kubelet
```
"""

M8_EXERCISE = r"""### Practical Laboratories & Hands-On Exercises

#### Lab 1: Repairing a Failed Kubelet Daemon
* **Objective:** Troubleshoot and fix a kubelet service that fails to start.
* **Tasks:**
    1. SSH into a worker node and stop the kubelet service.
    2. Modify the configuration path inside `/etc/systemd/system/kubelet.service.d/10-kubeadm.conf` to a non-existent file path to simulate a configuration error.
    3. Attempt to start the service and analyze the errors using `journalctl -u kubelet`.
    4. Correct the configuration path, reload the systemd manager daemon, and restart the service successfully.

#### Lab 2: Troubleshooting Static Pod Manifests
* **Objective:** Fix control plane components that fail to start due to configuration errors.
* **Tasks:**
    1. Navigate to `/etc/kubernetes/manifests` on a control plane node.
    2. Introduce a syntax error into `kube-scheduler.yaml`.
    3. Verify that the scheduler pod terminates and is no longer running in the cluster.
    4. Locate and review the container logs, fix the syntax error in the manifest, and verify the scheduler is recovered successfully.

#### Lab 3: Performing etcd Database Disaster Recovery
*   **Objective:** Capture an etcd database snapshot, simulate a disaster, and perform an offline restore.
*   **Prerequisites:** Access to a running control plane master node.
*   **Step-by-Step Instructions:**
    1. Take an etcd database snapshot using `etcdctl`:
       ```bash
       sudo ETCDCTL_API=3 etcdctl \
         --endpoints=https://127.0.0.1:2379 \
         --cacert=/etc/kubernetes/pki/etcd/ca.crt \
         --cert=/etc/kubernetes/pki/etcd/server.crt \
         --key=/etc/kubernetes/pki/etcd/server.key \
         snapshot save /tmp/etcd-lab.db
       ```
    2. Create a test namespace `etcd-recovery-test` inside the cluster.
    3. Run snapshot restore to a new recovery directory:
       ```bash
       sudo ETCDCTL_API=3 etcdctl --data-dir=/var/lib/etcd-recovered snapshot restore /tmp/etcd-lab.db
       ```
    4. Update your local etcd static Pod configuration `/etc/kubernetes/manifests/etcd.yaml` to mount and use `/var/lib/etcd-recovered` as its data directory.
*   **Deterministic Verification Test:**
    Verify that your cluster has been rolled back and that the namespace marker has been deleted:
    `kubectl get namespaces`
    *   **Expected Output:**
        The output must NOT display the namespace `etcd-recovery-test`, confirming the cluster state was restored successfully to the snapshot point.
*   **Troubleshooting Lab-Specific Issues:**
    If the API Server fails to restart after updating the etcd data directory, verify that your `/etc/kubernetes/manifests/etcd.yaml` file has valid syntax and that the permissions on `/var/lib/etcd-recovered` allow the etcd container process to read and write to the directory.

#### Lab 4: Checking and Renewing Expired TLS Certificates
*   **Objective:** Check the expiration dates of all control plane certificates and renew them manually.
*   **Prerequisites:** Sudo access on a control plane node.
*   **Step-by-Step Instructions:**
    1. SSH into your control plane master node.
    2. Check the expiration status of your cluster certificates:
       ```bash
       sudo kubeadm certs check-expiration
       ```
    3. Renew all certificates manually:
       ```bash
       sudo kubeadm certs renew all
       ```
*   **Deterministic Verification Test:**
    Verify the updated certificate status:
    `sudo kubeadm certs check-expiration`
    *   **Expected Output:**
        The output must show that all certificates are renewed and have a validity period of 365 days.
*   **Troubleshooting Lab-Specific Issues:**
    Ensure you restart your control plane static Pods (API Server, Controller Manager, Scheduler) after renewing certificates to ensure they load the updated files.

#### Lab 5: Resolving Kubelet Disk Pressure Eviction Events
*   **Objective:** Identify a node in a DiskPressure condition and resolve the issue.
*   **Prerequisites:** Access to a multi-node cluster.
*   **Step-by-Step Instructions:**
    1. SSH into a worker node and simulate disk pressure by writing a large file to `/var/lib/kubelet` or `/`.
    2. Monitor the node's status from the control plane: `kubectl get nodes` (the node should show a DiskPressure condition or enter a `NotReady` state).
    3. Free up host space by deleting the large temporary file or cleaning up old cached container images:
       ```bash
       sudo crictl rmi --prune
       ```
*   **Deterministic Verification Test:**
    Verify the node status: `kubectl get nodes`
    *   **Expected Output:**
        The node status must return to `Ready` with no active DiskPressure conditions.
*   **Troubleshooting Lab-Specific Issues:**
    If the node status does not update, restart the kubelet service on the worker node to force a resource utilization re-evaluation.
"""

M8_INSIGHT = r"""### Interview Q&A

#### Q1: How do you diagnose a kubelet that won't start?
* **Answer:** Start by checking the status of the service using `systemctl status kubelet`. If the status is failed, review the system logs using `journalctl -u kubelet -e` to find the specific error (e.g., missing configurations, invalid swap settings, or container runtime connection failures).

#### Q2: Where do you find the logs for static control plane pods if the API server is down?
* **Answer:** Since the API server is down, `kubectl` commands will fail. Instead, SSH into the control plane host and read the container log files directly from `/var/log/pods` or `/var/log/containers`.

#### Q3: How do you check if the host has swap enabled, and why does this affect the kubelet?
* **Answer:** Run `free -m` or `cat /proc/swaps` on the host to check if swap is active. By default, the kubelet will fail to start if swap is enabled on the host, as swap can cause unpredictable performance issues (though this behavior can be overridden using `--fail-swap-on=false`).

#### Q4: What tools should be inside a network debugging container?
* **Answer:** A network debugging container (such as `netshoot`) should contain tools like `nslookup` (for DNS resolution), `curl` or `wget` (for HTTP routing tests), `ping` (for network layer reachability), `traceroute` or `mtr` (for path analysis), and `tcpdump` or `tshark` (for packet capturing).

#### Q5: How do you identify certificate expiration issues on a control plane node?
* **Answer:** Run `kubeadm certs check-expiration` on the control plane node to check the expiration dates of all certificates used by the cluster. Additionally, check the kubelet logs for TLS handshake or verification errors, which often indicate expired client certificates.

### CKA Exam Focus
- Troubleshooting is the highest-weighted domain on the CKA exam.
- Practice locating systemd logs using `journalctl` and static pod manifests under `/etc/kubernetes/manifests`.
- Get comfortable using the `crictl` CLI utility to inspect container runtimes directly on worker hosts.
"""

# =====================================================================
# MODULE 9: APPLICATION DIAGNOSTICS, NETWORKING FAILURES, & EXAM STRATEGY
# =====================================================================

M9_THEORY = r"""### Guided Conceptual Walkthrough
Imagine you run a large private university. To manage the campus efficiently, prevent resource waste, and make services easy to use, you implement multiple layers of diagnostic and optimization systems:
*   **JSONPath Queries**: Set up an advanced search engine (**JSONPath**) to quickly extract specific student data fields (container images, node IPs, etc.) from the main campus registry database.
*   **Application Diagnostics**: Install real-time diagnostic systems (**kubectl logs & describe**) across all classrooms to monitor, analyze, and report on teaching and student behavior. If a classroom process freezes or crashes (**CrashLoopBackOff**), the system immediately alerts the supervisor.
*   **Exam Strategies**: Practice with simple, automated forms and template blueprints to complete maintenance tasks under strict time constraints.

### Architectural, Lifecycle & Flow Blueprints

```mermaid
graph TD
    Client[Client Operator] -->|kubectl get -o jsonpath| API[API Server]
    API -->|Filters JSON Metadata| Client
    Client -->|kubectl logs| Pod[Target Pod]
```

```mermaid
sequenceDiagram
    autonumber
    Pod->>API: Spawning Container Fails (Exit Code 1)
    API->>API: Set Pod Status: CrashLoopBackOff
    Operator->>API: kubectl logs --previous
    API-->>Operator: Return terminated container stdout/stderr
```

### Under-the-Hood Mechanics & Internal Operations
At the application diagnostics layer, the `kubelet` agent redirects container stdout and stderr streams directly to log files on the host node (`/var/log/pods`). When an administrator runs `kubectl logs`, the API Server acts as a proxy, fetching the log data from the host node and streaming it back to the client. 

If a container exits with a non-zero exit code, the Kubelet restarts it according to the Pod's restart policy, applying an exponential backoff delay (from 10s up to 5 minutes) to avoid overloading the system, which changes the Pod status to `CrashLoopBackOff`. 

To extract specific resource parameters from the API Server's massive JSON metadata outputs under tight time constraints, operators use JSONPath expressions to filter and format outputs on the fly, bypassing slow manual parsing.

### Deep-Dive Reference (Advanced Context)
<details>
<summary>JSONPath Metadata Queries and CKA Exam Strategies</summary>
JSONPath allows filtering and formatting API outputs dynamically. For example, to list all running container images across all namespaces:
`kubectl get pods -A -o jsonpath='{.items[*].spec.containers[*].image}'`
During the CKA exam, candidates must work quickly and accurately. Memorizing YAML templates, using dry-run commands, and using JSONPath expressions to extract metadata can save critical time.
</details>

### Systemic Failure Modes & Boundary Violations
*   **Failure Mode 1: Pod stuck in CrashLoopBackOff (Database Connection Error)**
    *   **Symptom:** Pod status displays `CrashLoopBackOff`, and restart counts continue to increment.
    *   **Root Cause:** The application is starting successfully but crashing shortly after because a database connection string or environment variable is missing or incorrect.
    *   **Resolution:** Retrieve the container logs (including logs from the previous failed run) to identify the missing variable, update the configuration, and re-apply:
        ```bash
        kubectl logs <pod-name> --previous
        ```

*   **Failure Mode 2: Ingress routing HTTP 503 Bad Gateway**
    *   **Symptom:** Accessing external services via Ingress returns HTTP 503 Service Unavailable errors.
    *   **Root Cause:** The Ingress Controller's routing rules are pointing to a Service that has an empty endpoints pool due to mismatched label selectors.
    *   **Resolution:** Check the service's endpoints list and ensure the selectors match the Pod labels exactly:
        ```bash
        kubectl get endpoints <service-name>
        ```

*   **Failure Mode 3: Pod stuck in Pending state (Unschedulable)**
    *   **Symptom:** Pod remains stuck in `Pending`, and describe commands report `0/3 nodes are available: 3 Insufficient cpu`.
    *   **Root Cause:** The Pod requests more CPU or memory than any single node has available, or the node taints are not tolerated.
    *   **Resolution:** Lower the resource requests in the Pod specification or apply the matching tolerations.

### Traceability Schema Check
All diagnostic commands (`logs`, `describe`), JSONPath metadata filters, and application failure states discussed below are conceptually defined in this section.
"""

M9_COMMANDS = r"""### Technical & Syntax Reference Manual
Below are the essential operational commands for diagnosing application failures and extracting metadata using JSONPath.

*   **Log Extraction and Diagnostics:**
    ```bash
    # Retrieve logs from a previously crashed container instance
    kubectl logs application-pod --previous -c main-container

    # Extract all Pod names and their IP addresses across all namespaces
    kubectl get pods -A -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.podIP}{"\n"}{end}'
    ```

*   **JSONPath Image Extraction:**
    ```bash
    # List all container images currently running in the default namespace
    kubectl get pods -o jsonpath='{.items[*].spec.containers[*].image}'
    ```

### Anatomy & Boundary Table
| Variable / Parameter / Keyword Name | Expected Type / Allowed Values | Default Value / Operating Domain | Strict Structural Constraints |
| :--- | :--- | :--- | :--- |
| `jsonpath` expression | JSONPath query string | N/A | Must follow valid JSONPath query format, wrapped in single quotes to avoid shell parsing. |
| `--previous` (logs flag) | Flag | N/A | Instructs the CLI to retrieve logs from the previously crashed container instance. |
| `kubectl top` | Command | N/A | Requires metrics-server to be installed and active in the cluster. |
| `status.podIP` | String (IP address) | N/A | Represents the unique cluster-routable IP address assigned to the Pod. |
"""

M9_EXAMPLES = r"""### Real-World Examples

#### Example 1: JSONPath metadata query script
* **Situation:** Quickly find the node names, operating system, and kernel version of all hosts in the cluster.
* **Action:** Run a JSONPath formatted query from your terminal.

```bash
kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}{"\\t"}{.status.nodeInfo.osImage}{"\\t"}{.status.nodeInfo.kernelVersion}{"\\n"}{end}'
```

#### Example 2: Static Pod manifest for diagnostic agent
* **Situation:** Deploy a temporary diagnostic tool on a specific node without using the scheduling control plane.
* **Action:** Write a Pod manifest directly into the host's static pods directory `/etc/kubernetes/manifests/diagnostics.yaml`.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: node-diagnostic-agent
  namespace: kube-system
spec:
  containers:
  - name: diagnostic-container
    image: alpine:3.18
    command: ["/bin/sh", "-c", "while true; do echo 'Healthy'; sleep 30; done"]
    securityContext:
      privileged: true
```

#### Example 3: Metrics Server Scrape Configuration
* **Situation:** The metrics-server cannot scrape node resource usage because node IP certificates are self-signed.
* **Action:** Edit the metrics-server deployment to bypass TLS validation for node IP scraping.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: metrics-server
  namespace: kube-system
spec:
  replicas: 1
  selector:
    matchLabels:
      k8s-app: metrics-server
  template:
    metadata:
      labels:
        k8s-app: metrics-server
    spec:
      containers:
      - name: metrics-server
        image: registry.k8s.io/metrics-server/metrics-server:v0.6.3
        args:
        - --cert-dir=/tmp
        - --secure-port=4443
        - --kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname
        - --kubelet-use-node-status-port
        - --kubelet-insecure-tls
```

#### Example 4: Network Diagnostics Pod Manifest
* **Situation:** Spin up a dedicated network testing pod to troubleshoot routing issues within the cluster.
* **Action:** Deploy an ephemeral pod containing diagnostic utilities.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: network-diagnostic-tool
  namespace: default
spec:
  containers:
  - name: tool-container
    image: nicolaka/netshoot:latest
    command: ["/bin/sh", "-c", "while true; do sleep 3600; done"]
    securityContext:
      capabilities:
        add: ["NET_ADMIN", "SYS_ADMIN"]
```

#### Example 5: Resolving CrashLoopBackOff due to a missing ConfigMap
* **Situation:** A web container keeps crashing on startup with a `CrashLoopBackOff` status because a required configuration file is missing.
* **Action:** Retrieve logs, identify the missing ConfigMap, and deploy it to resolve the crash.

```bash
# 1. Inspect container log outputs to find the error message
kubectl logs web-server-pod
# Output shows: FATAL ERROR: Config file /etc/config/app.json not found!

# 2. Deploy the missing ConfigMap and reapply the Pod
```
"""

M9_EXERCISE = r"""### Practical Laboratories & Hands-On Exercises

#### Lab 1: Debugging CrashLooping Pods
* **Objective:** Identify and fix runtime errors in crashing containers.
* **Tasks:**
    1. Deploy a pod running an application that is missing a required configuration.
    2. Check the container status and verify it is in a `CrashLoopBackOff` state.
    3. Retrieve the failure logs using `kubectl logs <pod-name> --previous`.
    4. Edit the pod configuration to fix the issue, apply the changes, and verify the pod runs successfully.

#### Lab 2: Querying API Outputs with JSONPath
* **Objective:** Extract specific fields from cluster resources using JSONPath expressions.
* **Tasks:**
    1. Get the list of all running pods in all namespaces, outputting only their names and namespaces.
    2. Extract the internal IP address of a specific worker node.
    3. Retrieve the path of a static host directory mounted in a volume.
    4. Write a single JSONPath query to list all container images currently running in the cluster.

#### Lab 3: Diagnosing Cluster DNS Failures
* **Objective:** Troubleshoot DNS resolution issues between pods.
* **Tasks:**
    1. Deploy a web service and check if other pods can resolve its name.
    2. If resolution fails, check the health of the CoreDNS pods and review their logs using `kubectl logs -n kube-system -l k8s-app=kube-dns`.
    3. Verify that the CoreDNS Service carries the correct IP address in `/etc/resolv.conf` of the client pods.
    4. Resolve any network policy or configuration blocking CoreDNS.

#### Lab 4: Troubleshooting Service Routing Selector Mismatches
*   **Objective:** Diagnose and repair a Service that has stopped routing traffic due to mismatched selectors.
*   **Prerequisites:** Access to a running Kubernetes cluster.
*   **Step-by-Step Instructions:**
    1. Deploy an application Pod labeled `app=production-api`.
    2. Create a Service named `api-svc` with an incorrect selector label `app=staging-api`.
    3. Attempt to connect to the Service and verify that the connection times out.
    4. Check the service's endpoint list: `kubectl get endpoints api-svc` (should show `<none>`).
    5. Update the Service's selector to `app=production-api` and re-apply.
*   **Deterministic Verification Test:**
    Verify the service's endpoint list:
    `kubectl get endpoints api-svc`
    *   **Expected Output:**
        The output must display the Pod's IP address, confirming the Service is successfully routing traffic.
*   **Troubleshooting Lab-Specific Issues:**
    Verify the Pod labels using `kubectl get pods --show-labels` to ensure the Service's selector matches them exactly.

#### Lab 5: Verifying NetworkPolicy Blocking Behaviors
*   **Objective:** Diagnose connection issues caused by active NetworkPolicies and resolve them.
*   **Prerequisites:** Completed Lab 4.
*   **Step-by-Step Instructions:**
    1. Deploy a backend database Pod inside your namespace.
    2. Apply a strict NetworkPolicy that blocks all incoming traffic to the database Pod.
    3. Verify that the application Pod fails to connect to the database.
    4. Update the NetworkPolicy to allow incoming traffic from Pods labeled `app=production-api`.
*   **Deterministic Verification Test:**
    Test database connection from the API Pod:
    `kubectl exec -it production-api -- nc -zv <db-pod-ip> 5432`
    *   **Expected Output:**
        `Connection to <db-pod-ip> 5432 port [tcp/*] succeeded!`
*   **Troubleshooting Lab-Specific Issues:**
    Verify that your cluster's CNI supports NetworkPolicies (such as Calico or Cilium), otherwise policies will be silently ignored.
"""

M9_INSIGHT = r"""### Interview Q&A

#### Q1: How do you diagnose a kubelet that won't start?
* **Answer:** Start by checking the status of the service using `systemctl status kubelet`. If the status is failed, review the system logs using `journalctl -u kubelet -e` to find the specific error (e.g., missing configurations, invalid swap settings, or container runtime connection failures).

#### Q2: Where do you find the logs for static control plane pods if the API server is down?
* **Answer:** Since the API server is down, `kubectl` commands will fail. Instead, SSH into the control plane host and read the container log files directly from `/var/log/pods` or `/var/log/containers`.

#### Q3: How do you check if the host has swap enabled, and why does this affect the kubelet?
* **Answer:** Run `free -m` or `cat /proc/swaps` on the host to check if swap is active. By default, the kubelet will fail to start if swap is enabled on the host, as swap can cause unpredictable performance issues (though this behavior can be overridden using `--fail-swap-on=false`).

#### Q4: What tools should be inside a network debugging container?
* **Answer:** A network debugging container (such as `netshoot`) should contain tools like `nslookup` (for DNS resolution), `curl` or `wget` (for HTTP routing tests), `ping` (for network layer reachability), `traceroute` or `mtr` (for path analysis), and `tcpdump` or `tshark` (for packet capturing).

#### Q5: How do you identify certificate expiration issues on a control plane node?
* **Answer:** Run `kubeadm certs check-expiration` on the control plane node to check the expiration dates of all certificates used by the cluster. Additionally, check the kubelet logs for TLS handshake or verification errors, which often indicate expired client certificates.

### CKA Exam Focus
- Troubleshooting is the highest-weighted domain on the CKA exam.
- Practice locating systemd logs using `journalctl` and static pod manifests under `/etc/kubernetes/manifests`.
- Get comfortable using the `crictl` CLI utility to inspect container runtimes directly on worker hosts.
"""

# =====================================================================
# FINAL CURRICULUM BINDINGS
# =====================================================================

CURRICULUM_DATA = [
    {
        "id": 1,
        "title": "Module 1: Kubernetes Core Architecture, Declarative Primitives, & CLI Speed",
        "theory": M1_THEORY,
        "commands": M1_COMMANDS,
        "examples": M1_EXAMPLES,
        "exercise": M1_EXERCISE,
        "insight": M1_INSIGHT,
    },
    {
        "id": 2,
        "title": "Module 2: Cluster Bootstrapping, High Availability, & Upgrades",
        "theory": M2_THEORY,
        "commands": M2_COMMANDS,
        "examples": M2_EXAMPLES,
        "exercise": M2_EXERCISE,
        "insight": M2_INSIGHT,
    },
    {
        "id": 3,
        "title": "Module 3: Workloads, Lifecycle Management, & Advanced Scheduling",
        "theory": M3_THEORY,
        "commands": M3_COMMANDS,
        "examples": M3_EXAMPLES,
        "exercise": M3_EXERCISE,
        "insight": M3_INSIGHT,
    },
    {
        "id": 4,
        "title": "Module 4: Services, CoreDNS, & Core Cluster Networking",
        "theory": M4_THEORY,
        "commands": M4_COMMANDS,
        "examples": M4_EXAMPLES,
        "exercise": M4_EXERCISE,
        "insight": M4_INSIGHT,
    },
    {
        "id": 5,
        "title": "Module 5: Advanced Network Isolation, Ingress, & Gateway API",
        "theory": M5_THEORY,
        "commands": M5_COMMANDS,
        "examples": M5_EXAMPLES,
        "exercise": M5_EXERCISE,
        "insight": M5_INSIGHT,
    },
    {
        "id": 6,
        "title": "Module 6: Storage Primitives, Dynamic Provisioning, & Stateful Mounts",
        "theory": M6_THEORY,
        "commands": M6_COMMANDS,
        "examples": M6_EXAMPLES,
        "exercise": M6_EXERCISE,
        "insight": M6_INSIGHT,
    },
    {
        "id": 7,
        "title": "Module 7: Cluster Access Control, Authentication, & Enterprise RBAC",
        "theory": M7_THEORY,
        "commands": M7_COMMANDS,
        "examples": M7_EXAMPLES,
        "exercise": M7_EXERCISE,
        "insight": M7_INSIGHT,
    },
    {
        "id": 8,
        "title": "Module 8: Control Plane & Node-Level Disaster Recovery & Troubleshooting",
        "theory": M8_THEORY,
        "commands": M8_COMMANDS,
        "examples": M8_EXAMPLES,
        "exercise": M8_EXERCISE,
        "insight": M8_INSIGHT,
    },
    {
        "id": 9,
        "title": "Module 9: Application Diagnostics, Networking Failures, & Exam Strategy",
        "theory": M9_THEORY,
        "commands": M9_COMMANDS,
        "examples": M9_EXAMPLES,
        "exercise": M9_EXERCISE,
        "insight": M9_INSIGHT,
    },
]