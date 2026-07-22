COURSE_ID = "cka_ultimate_mastery"
COURSE_TITLE = "Certified Kubernetes Administrator (CKA) Complete Mastery Course"
COURSE_DESCRIPTION = "The ultimate hands-on curriculum spanning 9 core modules, covering every CKA domain in thorough, production-grade detail. Spans from fundamental API objects to highly advanced cluster architecture, upgrades, networking, and system troubleshooting."

CURRICULUM_DATA = [
    {
        "id": 1,
        "title": "Module 1: Kubernetes Core Architecture, Declarative Primitives, & CLI Tools",
        "theory": """### The Kubernetes Paradigm and Core Architecture
Kubernetes is an open-source container orchestration engine designed to manage the deployment, scaling, and operational lifecycle of containerized workloads. At its core, the system operates on a declarative model: you define the desired state of your applications, and the control plane continuously reconciles the cluster's actual state with your target declaration.

The control plane coordinates cluster-wide operations. The central component is the `kube-apiserver`, a RESTful API server that acts as the single point of contact for administrative commands and internal components. State data is persisted across the cluster in `etcd`, a highly consistent, distributed key-value store. The `kube-scheduler` monitors newly created Pods that lack an assigned node and determines the optimal host based on resources and affinity rules. The `kube-controller-manager` runs loop controllers to regulate node states, job configurations, endpoints, and replication sets.

On worker hosts, the `kubelet` agent receives Pod declarations from the API server and interfaces directly with the container runtime (CRI) to launch, maintain, and verify container runtimes. The `kube-proxy` maintains node firewall configurations and local routing tables to forward traffic to correct Pod endpoints.

### Declarative API Objects and Namespaces
All entities in Kubernetes are defined as API resources (such as Pods, Namespaces, Services, or ConfigMaps). Resource structures are serialized as YAML or JSON manifests and submitted to the API server. 
- **Namespaces:** Provide virtual isolation boundaries within a single physical cluster, allowing teams, environments, or projects to share compute resources safely.
- **Labels & Selectors:** Labels are arbitrary, metadata key-value pairs attached to resources. Selectors are query mechanisms that components like Services or ReplicaSets use to group and target sets of labeled Pods.

### Mastering the Kubectl Command-Line Interface
The `kubectl` command-line utility is the primary tool for interacting with the Kubernetes API. While declarative manifests are used for production changes, imperative commands are essential for rapid prototyping, troubleshooting, and time-sensitive exam scenarios. Mastering options like `--dry-run=client -o yaml` is critical for generating clean, syntax-compliant YAML templates instantly.""",
        "commands": """### Command & Syntax Reference

```bash
# Display general API resources, shortnames, and API groups
kubectl api-resources

# Run a temporary diagnostic container in a specific namespace
kubectl run alpine-debug --image=alpine:3.18 -n development -- rm -f /tmp/lock

# Generate a dry-run Pod manifest without creating it on the cluster
kubectl run web-server --image=nginx:1.25.1 --dry-run=client -o yaml > pod-template.yaml

# Apply a declarative configuration manifest
kubectl apply -f pod-template.yaml

# Filter pods across all namespaces matching a label query
kubectl get pods -l "env=production,tier=backend" -A

# Add or update a label on a running pod
kubectl label pod web-server tier=frontend --overwrite

# Describe a specific pod to view event logs and container statuses
kubectl describe pod web-server -n development
```""",
        "examples": """### Real-World Examples

#### Example 1: Minimal Declarative Namespace & Pod
* **Situation:** A team needs a completely isolated sandbox namespace and a baseline web container deployed with standard labels for testing.
* **Action:** Define a combined Namespace and labeled Pod manifest.

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

#### Example 2: Multi-Container Pod with Ephemeral emptyDir
* **Situation:** A custom web application container writes raw logs to a shared local directory, and a separate sidecar log-shipper container must parse those logs in real time.
* **Action:** Build a multi-container pod utilizing an in-memory `emptyDir` volume mount.

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

#### Example 3: Service Selector Mapping
* **Situation:** A backend team needs to expose an application running in pods that carry the labels `app: auth-engine` and `tier: secure`.
* **Action:** Define a ClusterIP Service referencing the precise label selectors.

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

#### Example 4: Pod Manifest with Annotations
* **Situation:** Compliance policies dictate that all running applications must document deployment metadata, contact details, and change descriptions inside the container metadata.
* **Action:** Define a Pod manifest utilizing metadata annotations.

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

#### Example 5: Imperative Templating Script
* **Situation:** A DevOps engineer wants a repeatable script to generate clean, declarative configurations on the fly to save time during deployments.
* **Action:** Write a short bash script using `kubectl` dry-run commands.

```bash
#!/bin/bash
# Generate a namespace and pod template automatically
kubectl create namespace staging-api --dry-run=client -o yaml > bootstrap.yaml
echo "---" >> bootstrap.yaml
kubectl run staging-worker --image=python:3.11-alpine --namespace=staging-api --dry-run=client -o yaml >> bootstrap.yaml
echo "Bootstrap manifest successfully written to bootstrap.yaml"
```""",
        "exercise": """### Hands-On Labs

#### Lab 1: Namespace Creation and Pod Isolation
* **Objective:** Learn to create separate virtual environments and deploy isolated resources inside them.
* **Tasks:**
    1. Create a namespace named `finance-sandbox` using the command-line utility.
    2. Imperatively generate a Pod named `ledger-db` utilizing the `redis:7.0-alpine` image inside `finance-sandbox`.
    3. Retrieve running pods specifically within the `finance-sandbox` namespace.
    4. Confirm that the default namespace does not list the new pod.

#### Lab 2: Managing Pod Metadata Labels
* **Objective:** Practice manipulating and querying resource labels.
* **Tasks:**
    1. Deploy an `nginx:1.25.1` pod named `portal-frontend` in the `default` namespace.
    2. Add the label `environment=production` to the pod using `kubectl label`.
    3. Add another label `tier=frontend` to the same pod.
    4. Query pods in the default namespace using the selector `environment=production`.
    5. Modify the `environment` label to `staging` using the `--overwrite` flag.

#### Lab 3: API Resource Discovery and Shortnames
* **Objective:** Discover API groupings and resource metadata on a live cluster.
* **Tasks:**
    1. Query all resource groups supported by the cluster using `kubectl api-resources`.
    2. Find the shortname for the `ServiceAccount` and `PersistentVolumeClaim` resources.
    3. Identify which API resources belong to the `apps` API group.
    4. Describe the schema properties of a Pod's specification using `kubectl explain pod.spec.containers`.

#### Lab 4: Configuring Multi-Container Log Collectors
* **Objective:** Deploy a pod with two cooperating containers sharing an emptyDir volume.
* **Tasks:**
    1. Write a YAML manifest defining a Pod with two containers named `app-source` and `log-reader`.
    2. Configure a shared `emptyDir` volume named `log-transport` mounted at `/mnt/logs` in both containers.
    3. Configure `app-source` to append system logs to `/mnt/logs/debug.txt` every 2 seconds.
    4. Configure `log-reader` to output contents from `/mnt/logs/debug.txt` to stdout.
    5. Apply the manifest and verify the outputs using `kubectl logs <pod-name> -c log-reader`.

#### Lab 5: Manifest Generation and Export
* **Objective:** Generate error-free declarative files from running resources.
* **Tasks:**
    1. Run a pod imperatively named `temp-worker` utilizing the `alpine:3.18` image.
    2. Export the configuration of the running `temp-worker` pod as JSON/YAML, purging runtime status blocks.
    3. Delete the running pod from the cluster.
    4. Re-apply the exported configuration to recreate the pod cleanly.""",
        "insight": """### Interview Q&A

#### Q1: What is the main design advantage of the declarative model over the imperative model?
* **Answer:** In an imperative model, you execute explicit commands to modify state step-by-step (e.g., 'start container', 'add route'), which requires complex error handling to resolve intermediate state failures. The declarative model lets you specify the final target state. The control plane handles the reconciliation loop, automatically correcting deviations (like failures or scaling issues) to reach that state.

#### Q2: What is etcd, and why is its reliability critical to the cluster?
* **Answer:** `etcd` is a distributed, consistent key-value store used as the single source of truth for all Kubernetes cluster state data. If etcd becomes unavailable or corrupt, the API server cannot process state mutations, new pods cannot schedule, and existing controllers cannot reconcile state, effectively locking the cluster.

#### Q3: Why is a Pod, rather than a single container, the basic unit of execution in Kubernetes?
* **Answer:** A Pod provides a shared context (shared Linux namespaces and cgroups) for its containers. This ensures that all containers in the same Pod share an IP address, port space, and storage volumes. It allows tightly coupled helper containers (like sidecars, proxies, or loggers) to communicate directly via `localhost` and share storage, which would be difficult to coordinate across separate containers.

#### Q4: How do Labels differ from Annotations in Kubernetes?
* **Answer:** Labels are key-value pairs used to identify, group, and query API resources. They are indexed by the API server and can be used in selectors (e.g., mapping a Service to Pods). Annotations are non-identifying metadata used to store larger, non-indexed helper data (such as build IDs, team contact channels, or configuration policies) for external tools and systems.

#### Q5: What is the function of the kubelet on a worker node?
* **Answer:** The `kubelet` is an agent running on each worker node. It registers the node with the API server, watches for Pod specifications assigned to its host, and calls the Container Runtime Interface (CRI) to ensure the declared containers are running and healthy. It also reports node status and resource utilization metrics back to the control plane.

### CKA Exam Focus
- Learn the syntax for rapid manifest creation: `kubectl run ... --dry-run=client -o yaml`.
- When asked to deploy resources in a specific namespace, make sure to append `-n <namespace>` or include it directly in the YAML metadata to avoid deploying to `default`.
- Learn to search documentation for simple Pod and Namespace structures using `kubectl explain` directly from the terminal."""
    },
    {
        "id": 2,
        "title": "Module 2: Application Deployments, Workload Controllers, & Lifecycles",
        "theory": """### Workload Controllers and Lifecycle Management
Kubernetes provides several workload controllers to manage Pod execution lifecycles based on application architecture and operational requirements.

- **Deployments:** The standard choice for stateless applications. They define a desired scale (replicas) and manage rolling updates or rollbacks. Deployments manage an underlying `ReplicaSet`, which matches the requested number of pods by creating or terminating resources.
- **DaemonSets:** Ensure that a single copy of a specific Pod runs on all (or selected) nodes. This is useful for system-level infrastructure agents, such as log collectors (e.g., Fluentd) or network proxies.
- **StatefulSets:** Manage workloads that require persistent state, stable network identities, and dedicated storage. Pods are created sequentially (0, 1, 2...) with predictable hostnames (e.g., `db-0`, `db-1`), and each pod maintains its identity and storage mapping even if rescheduled to a different node.
- **Jobs & CronJobs:** Jobs run a batch workload to completion (exiting when the task finishes). CronJobs schedule Jobs at specified intervals using standard crontab syntax.

### Init Containers & Native Sidecars
Workloads often require setup steps (such as running database migrations or waiting for a dependency) before the main container starts. `Init Containers` run sequentially and must exit successfully before the application containers start. 

Starting in Kubernetes v1.28+, native `Sidecar Containers` are supported. They are defined within the init container block but have their lifecycle extended to run concurrently with the main application container, terminating automatically when the main container exits.

### Workload Health and Probes
To ensure application reliability, the kubelet monitors container health using three types of probes:
- **Startup Probe:** Disables liveness and readiness checks during container startup to prevent premature restarts on slow-booting applications.
- **Liveness Probe:** Monitors container health to determine if it has crashed or locked up. If the probe fails, the kubelet restarts the container.
- **Readiness Probe:** Checks if the container is ready to accept user traffic. If the probe fails, the pod is temporarily removed from service endpoints to prevent routing traffic to an unready application.""",
        "commands": """### Command & Syntax Reference

```bash
# Imperatively create a Deployment of nginx with 3 replicas
kubectl create deployment web-app --image=nginx:1.25.1 --replicas=3

# Scale an active deployment to 10 replicas
kubectl scale deployment web-app --replicas=10

# Check the rolling update history of a deployment
kubectl rollout history deployment/web-app

# Roll back a deployment to a specific historical revision
kubectl rollout undo deployment/web-app --to-revision=2

# Monitor the status of an active deployment upgrade
kubectl rollout status deployment/web-app

# Pause a deployment rollout to execute intermediate changes
kubectl rollout pause deployment/web-app

# Resume a paused deployment rollout
kubectl rollout resume deployment/web-app
```""",
        "examples": """### Real-World Examples

#### Example 1: Deployment with Rolling Update and Probes
* **Situation:** Deploy a high-availability stateless API gateway that requires zero-downtime updates and reliable health checks.
* **Action:** Define a Deployment with an explicit rolling update strategy and configured liveness/readiness probes.

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

#### Example 2: Infrastructure DaemonSet
* **Situation:** An operations team needs to collect system statistics from every node in the cluster and send them to a central monitoring system.
* **Action:** Define a DaemonSet to run the metric collector on all worker nodes.

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: metric-collector
  namespace: kube-system
spec:
  selector:
    matchLabels:
      name: collector-agent
  template:
    metadata:
      labels:
        name: collector-agent
    spec:
      containers:
      - name: agent
        image: alpine:3.18
        command: ["/bin/sh", "-c", "while true; do echo 'Gathering metrics...'; sleep 60; done"]
```

#### Example 3: StatefulSet with Stable Identity
* **Situation:** Set up a clustered key-value store where each node requires a predictable network identity and stable storage mapping.
* **Action:** Combine a Headless Service with a StatefulSet configuration.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: redis-hs
spec:
  clusterIP: None
  selector:
    app: redis-cluster
  ports:
  - port: 6379
    name: redis
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redis-node
spec:
  serviceName: "redis-hs"
  replicas: 2
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
        - name: redis-vol
          mountPath: /data
  volumeClaimTemplates:
  - metadata:
      name: redis-vol
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 1Gi
```

#### Example 4: Scheduled Database Backup CronJob
* **Situation:** Set up an automated database backup task that runs nightly at 1:30 AM, ensuring old job runs are automatically cleaned up.
* **Action:** Configure a CronJob with history limits and concurrency policies.

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: db-backup-cron
  namespace: default
spec:
  schedule: "30 1 * * *"
  concurrencyPolicy: Forbid
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup-tool
            image: alpine:3.18
            command: ["/bin/sh", "-c", "echo 'Backing up databases...'; sleep 30; echo 'Backup complete'"]
          restartPolicy: OnFailure
```

#### Example 5: Native Sidecar Container Definition
* **Situation:** A web service requires a secondary local proxy container to secure outbound traffic, and the proxy must start before the main application starts.
* **Action:** Define the proxy as an init container with the sidecar restart policy (requires Kubernetes v1.28+).

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
```""",
        "exercise": """### Hands-On Labs

#### Lab 1: Zero-Downtime Deployment Upgrades
* **Objective:** Perform a rolling update and roll back a failed deployment to a previous version.
* **Tasks:**
    1. Create a Deployment of Nginx named `frontend-scaler` with 3 replicas.
    2. Configure the deployment update strategy with `maxSurge: 1` and `maxUnavailable: 0`.
    3. Update the container image version to a non-existent tag (e.g., `nginx:invalid-tag`) and track progress using `kubectl rollout status`.
    4. Confirm that the upgrade pauses and existing replicas remain running to prevent downtime.
    5. Roll back the deployment to the last stable configuration using `kubectl rollout undo`.

#### Lab 2: Deploying DaemonSet Agents
* **Objective:** Ensure cluster monitoring agents run on all worker nodes.
* **Tasks:**
    1. Write a DaemonSet manifest to run a lightweight container on all nodes.
    2. Apply the manifest and verify the daemon pods are distributed across all worker nodes.
    3. Label one of your nodes as unschedulable (using cordon) and observe if the DaemonSet pod remains running on that node.

#### Lab 3: Configuring Container Liveness Probes
* **Objective:** Implement health probes to automatically restart failing containers.
* **Tasks:**
    1. Write a Pod manifest containing an alpine container.
    2. Configure the container to create a lockfile `/tmp/healthy` at startup, delete it after 15 seconds, and sleep.
    3. Configure a liveness probe that checks for the existence of `/tmp/healthy` every 5 seconds.
    4. Apply the manifest and monitor the container restarts using `kubectl get pods -w` as the lockfile is deleted.

#### Lab 4: Waiting for Service Dependencies with Init Containers
* **Objective:** Block the main application container until its service dependencies are running.
* **Tasks:**
    1. Create a Pod containing an init container that runs `nslookup db-svc` in a loop.
    2. Create a main container in the pod that starts a web server.
    3. Apply the pod manifest and verify its status is stuck in `Init:0/1`.
    4. Deploy a Service named `db-svc` and verify the pod transitions to `Running` status.

#### Lab 5: Implementing Scheduled CronJobs
* **Objective:** Configure batch processes to run on a set schedule.
* **Tasks:**
    1. Define a CronJob scheduled to run every minute (`* * * * *`).
    2. Configure the job to run a simple script that outputs a success message and exits.
    3. Apply the manifest and monitor the generated jobs and pods.
    4. Verify that completed job pods are cleaned up according to the defined history limits.""",
        "insight": """### Interview Q&A

#### Q1: What is the benefit of setting maxSurge and maxUnavailable during a rolling update?
* **Answer:** These parameters let you control the pace and risk of rolling updates. `maxSurge` specifies the maximum number of extra pods that can be created above the desired replica count during an upgrade. `maxUnavailable` specifies the maximum number of pods that can be offline at any given time. Configuring `maxUnavailable: 0` ensures that the cluster maintains full capacity throughout the rolling update.

#### Q2: What happens to a Pod managed by a Deployment if the Deployment is deleted?
* **Answer:** When a Deployment is deleted, Kubernetes uses garbage collection to automatically delete the associated `ReplicaSet` and all the `Pods` it manages, unless the `--cascade=orphan` flag is used during deletion.

#### Q3: Why is a Headless Service required when defining a StatefulSet?
* **Answer:** Stateful pods require unique, predictable, and direct network access (e.g., to distinguish between primary and replica database nodes). A Headless Service (a Service with `clusterIP: None`) does not create a load-balancing IP. Instead, it creates direct DNS A-records for each individual pod (e.g., `pod-0.headless-service`), allowing clients to connect directly to specific nodes.

#### Q4: How does a Readiness Probe affect Pod traffic routing?
* **Answer:** If a container's Readiness Probe fails, Kubernetes temporarily removes the Pod's IP address from the endpoints list of all matching Services. This ensures that the Service load balancer stops routing user traffic to that pod until the probe succeeds again.

#### Q5: What is the execution order and lifecycle of Init Containers?
* **Answer:** Init containers run sequentially, one after the other, and each must exit successfully (`exit 0`) before the next init container begins. If an init container fails, Kubernetes restarts the pod (according to its restart policy) and runs the initialization sequence again. Main application containers cannot start until all init containers have completed successfully.

### CKA Exam Focus
- Ensure you understand the distinction between Jobs (which run once to completion) and Deployments (which are designed to keep stateless applications running indefinitely).
- Practice configuring path parameters for `httpGet` probes, as misconfigured endpoints can lead to unexpected restart loops."""
    },
    {
        "id": 3,
        "title": "Module 3: Advanced Pod Scheduling, Resource Controls, & Policies",
        "theory": """### Kubernetes Scheduler and Pod Placement
The Kubernetes Scheduler is responsible for assigning pods to optimal nodes in the cluster. This scheduling process occurs in two main phases:
1.  **Filtering (Predicates):** The scheduler evaluates node resources and constraints (such as CPU, memory, taints, and selectors) to filter out nodes that cannot run the pod.
2.  **Scoring (Priorities):** The remaining nodes are scored based on optimization rules (such as resource balance and affinity preferences) to select the best host node.

### Resource Requests and Limits
Managing node resources requires defining CPU and memory requirements for each container:
- **Requests:** The minimum amount of CPU and memory the container needs to run. The scheduler uses requests to determine if a node has enough allocatable capacity to run the pod.
- **Limits:** The maximum amount of CPU and memory the container is allowed to consume. If a container exceeds its memory limit, it is terminated with an Out-of-Memory (OOM) error. If it exceeds its CPU limit, its CPU usage is throttled, but the container is not terminated.

### Advanced Scheduling: Affinity, Taints, & Tolerations
To control pod placement more precisely, use these scheduling mechanisms:
- **Node Selector:** A simple key-value match to place pods on nodes with matching labels.
- **Node Affinity:** An advanced matching system supporting logical operators. It can be enforced as a hard constraint (`requiredDuringSchedulingIgnoredDuringExecution`) or a soft preference (`preferredDuringSchedulingIgnoredDuringExecution`).
- **Pod Affinity & Anti-Affinity:** Places pods on nodes based on the labels of other pods already running on those nodes. For example, Pod Anti-Affinity is often used to ensure replicas of a web server are distributed across different nodes or zones for high availability.
- **Taints and Tolerations:** Node taints repel pods. Pods can override this repulsion by defining matching tolerations, allowing them to schedule on tainted nodes (e.g., reserving specific nodes for GPU workloads).

### Resource Restrictions: ResourceQuotas and LimitRanges
To prevent resource overcommitment in shared environments, define cluster resource limits:
- **ResourceQuotas:** Limit the total resource consumption (e.g., total CPU, memory, or number of pods) within a namespace.
- **LimitRanges:** Enforce default resource requests and limits for any container created in a namespace that does not define them explicitly.""",
        "commands": """### Command & Syntax Reference

```bash
# Label a worker node to target it with node selectors
kubectl label node worker-01 hardware=high-cpu

# View active taints on all nodes in the cluster
kubectl get nodes -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints

# Apply a NoSchedule taint to a worker node
kubectl taint nodes worker-01 dedicated=database:NoSchedule

# Remove a taint from a worker node
kubectl taint nodes worker-01 dedicated:NoSchedule-

# View ResourceQuotas configured in a namespace
kubectl get quota -n development

# View LimitRanges configured in a namespace
kubectl get limitrange -n development
```""",
        "examples": """### Real-World Examples

#### Example 1: Pod with Strict Resource Controls
* **Situation:** Deploy a memory-intensive microservice with defined resource requests and limits to prevent it from consuming all host memory.
* **Action:** Define CPU and memory requests and limits in the Pod specification.

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

#### Example 2: Pod with Node Affinity Rules
* **Situation:** Schedule an analytics worker node only on hosts with high-performance CPUs, with a preference for nodes in zone `us-east-1a`.
* **Action:** Configure a Pod with hard and soft Node Affinity rules.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: analytics-worker
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: hardware
            operator: In
            values:
            - high-cpu
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        preference:
          matchExpressions:
          - key: topology.kubernetes.io/zone
            operator: In
            values:
            - us-east-1a
  containers:
  - name: worker
    image: alpine:3.18
    command: ["/bin/sh", "-c", "echo 'Analyzing data...'; sleep 300"]
```

#### Example 3: High-Availability Pod Anti-Affinity
* **Situation:** Deploy three replicas of a web server and ensure that no two replicas run on the same physical host node.
* **Action:** Configure a Deployment with a Pod Anti-Affinity rule.

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
* **Situation:** Run an administrative monitoring tool on master nodes that carry the taint `node-role.kubernetes.io/control-plane:NoSchedule`.
* **Action:** Create a Pod manifest with a matching Toleration.

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

#### Example 5: Namespace ResourceQuota & LimitRange
* **Situation:** Restrict a development namespace to a maximum of 4 cores, 8Gi of memory, and 10 Pods, while enforcing default container resource requests.
* **Action:** Define a ResourceQuota and a LimitRange in the target namespace.

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: dev-quota
  namespace: default
spec:
  hard:
    pods: "10"
    requests.cpu: "2"
    requests.memory: "4Gi"
    limits.cpu: "4"
    limits.memory: "8Gi"
---
apiVersion: v1
kind: LimitRange
metadata:
  name: dev-limits
  namespace: default
spec:
  limits:
  - default:
      cpu: "500m"
      memory: "512Mi"
    defaultRequest:
      cpu: "200m"
      memory: "256Mi"
    type: Container
```""",
        "exercise": """### Hands-On Labs

#### Lab 1: Enforcing Resource Limits and Observing OOM Kills
* **Objective:** Observe how the cluster handles containers that exceed their resource limits.
* **Tasks:**
    1. Create a Pod with a memory limit of `50Mi`.
    2. Configure the container to run a script that allocates a large array to intentionally consume memory.
    3. Apply the manifest and monitor the pod status.
    4. Verify that the pod is terminated with an Out-of-Memory (`OOMKilled`) status.

#### Lab 2: Targeted Node Scheduling with Affinity
* **Objective:** Schedule workloads on specific hosts using node labels and affinity rules.
* **Tasks:**
    1. Label node `worker-01` with the label `disktype=ssd`.
    2. Write a Pod manifest that uses Node Affinity to target nodes with the `disktype=ssd` label.
    3. Apply the manifest and verify the pod is scheduled on `worker-01`.
    4. Delete the label from the node and verify how subsequent scheduled pods are affected.

#### Lab 3: Distributing Workloads with Anti-Affinity
* **Objective:** Maintain high availability by distributing application replicas across different nodes.
* **Tasks:**
    1. Deploy a Deployment with 3 replicas.
    2. Configure a Pod Anti-Affinity rule targeting the deployment's own label selector.
    3. Verify that each pod is scheduled on a different worker node.
    4. Scale the deployment beyond the number of available nodes and observe if the new pods remain in a `Pending` state.

#### Lab 4: Restricting Nodes using Taints and Tolerations
* **Objective:** Reserve dedicated nodes for specific workloads using taints.
* **Tasks:**
    1. Apply a NoSchedule taint to a worker node: `kubectl taint nodes <node-name> dedicated=infra:NoSchedule`.
    2. Deploy a standard test pod and verify that it is scheduled on a different node.
    3. Deploy a second pod with a matching toleration for the taint.
    4. Verify that the second pod schedules successfully on the tainted node.

#### Lab 5: Implementing Namespace Resource Quotas
* **Objective:** Limit resource consumption within a development namespace.
* **Tasks:**
    1. Create a namespace named `quota-test`.
    2. Apply a ResourceQuota limiting the namespace to `1` CPU and `1Gi` of memory.
    3. Deploy an application pod that fits within this quota.
    4. Attempt to deploy a second pod that exceeds the remaining quota, and verify that the API server rejects the request.""",
        "insight": """### Interview Q&A

#### Q1: What happens if a container exceeds its memory limits versus its CPU limits?
* **Answer:** If a container exceeds its memory limit, the Linux kernel's Out-Of-Memory (OOM) killer terminates the process, causing the container to exit with status code 137 (OOMKilled). If a container exceeds its CPU limit, Kubernetes throttles its CPU usage, slowing down execution, but does not terminate the container.

#### Q2: How do Requests and Limits affect Quality of Service (QoS) classes?
* **Answer:** Kubernetes assigns QoS classes to pods based on their resource configurations:
  - **Guaranteed:** Every container in the pod has identical CPU and memory requests and limits.
  - **Burstable:** Requests and limits are defined, but they are not equal, or some containers lack limits.
  - **BestEffort:** No containers in the pod have requests or limits defined.
  The cluster uses these classes to determine eviction priority when node resources are low.

#### Q3: What is the difference between a Node Selector and Node Affinity?
* **Answer:** A Node Selector is a simple key-value matching rule used to schedule pods on nodes with matching labels. Node Affinity is a more flexible system that supports logical operators (such as `In`, `NotIn`, `Exists`), soft preferences (`preferredDuringScheduling`), and the ability to schedule pods relative to other pods (Pod Affinity).

#### Q4: How does the NoExecute taint effect behave compared to NoSchedule?
* **Answer:** The `NoSchedule` taint prevents new pods from scheduling on a node unless they have a matching toleration, but does not affect existing pods running on the node. The `NoExecute` taint also prevents new pods from scheduling, but additionally evicts any running pods on the node that do not have a matching toleration.

#### Q5: Why is a pod rejected if a LimitRange is active but the pod defines no resources?
* **Answer:** If a `LimitRange` defines minimum/maximum limits but no default requests or limits, and a pod is submitted without resource definitions, the API server will reject the pod if it violates the LimitRange boundaries. If defaults are defined, the LimitRange automatically injects them into the pod specification at creation time.

### CKA Exam Focus
- Ensure you understand the distinction between `requests` (used for scheduling decisions) and `limits` (enforced at runtime).
- Practice writing tolerations using both the `Equal` operator (which requires a specific value) and the `Exists` operator (which matches any value for a given key)."""
    },
    {
        "id": 4,
        "title": "Module 4: Cluster Access Control, Authentication, & Advanced RBAC",
        "theory": """### Kubernetes Security and Access Control
Kubernetes secures its API server using a multi-stage authentication and authorization process. Every API request must pass through three phases:
1.  **Authentication (AuthN):** Verifies the identity of the requester (e.g., a human user or an internal service account).
2.  **Authorization (AuthZ):** Verifies if the authenticated identity has permission to perform the requested action (typically implemented using Role-Based Access Control).
3.  **Admission Control:** Modifies or validates requests before they are persisted in etcd (e.g., enforcing security policies).

### Authentication: Users & ServiceAccounts
Kubernetes distinguishes between human users and service accounts:
- **User Accounts:** Intended for humans and managed externally to the cluster (e.g., using client certificates, OpenID Connect, or LDAP). Kubernetes does not store "User" resources in etcd.
- **ServiceAccounts:** Intended for internal cluster processes, such as pods interacting with the API server. These are resources managed directly within namespaces and can be assigned API tokens.

### Role-Based Access Control (RBAC) Mechanics
RBAC regulates access to API resources based on roles assigned to users or service accounts. RBAC policies are composed of four key objects:
- **Role:** Defines permissions (verbs like get, list, create) for namespaced API resources within a specific namespace.
- **ClusterRole:** Defines permissions for cluster-scoped resources (such as nodes or PVs) or namespaced resources across all namespaces.
- **RoleBinding:** Associates a Role (or ClusterRole) with a user or ServiceAccount within a specific namespace.
- **ClusterRoleBinding:** Associates a ClusterRole with a user or ServiceAccount cluster-wide, granting access across all namespaces.

### Certificate Signing Request (CSR) API
To add new users to the cluster safely, Kubernetes provides the Certificate Signing Request (CSR) API. Administrators generate a private key and a CSR, submit the request to the API server, and approve it to issue a client certificate for authentication.

### Kubeconfigs
The client configuration for connecting to a cluster is stored in a `kubeconfig` file. It organizes connection details, clusters, user credentials, and security contexts into active contexts for `kubectl`.""",
        "commands": """### Command & Syntax Reference

```bash
# Create a new ServiceAccount in a specific namespace
kubectl create serviceaccount app-sa -n development

# Test user authorization permissions using auth can-i
kubectl auth can-i create deployments --as=system:serviceaccount:development:app-sa

# Create an RBAC Role with read-only access to pods
kubectl create role pod-reader --verb=get,list,watch --resource=pods -n development

# Bind a ServiceAccount to a Role
kubectl create rolebinding read-pods-bind --role=pod-reader --serviceaccount=development:app-sa -n development

# Create a ClusterRole with view-only access to cluster resources
kubectl create clusterrole cluster-viewer --verb=get,list,watch --resource=nodes,namespaces

# Bind a user to a ClusterRole cluster-wide
kubectl create clusterrolebinding view-all --clusterrole=cluster-viewer --user=developer@company.com

# List and approve pending certificate signing requests
kubectl get csr
kubectl certificate approve developer-csr
```""",
        "examples": """### Real-World Examples

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
  request: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURSBSRVFVRVNULS0tLS0KTUI0Q0FEQWdBb0dDQm9SME93R0NBUXN0R0NBR0JnQXdBREVMTUFrR0ExVUVCaE1DVlZNd0NnWURWUVFLREFoTApVbVZ6ZDJWeWR6RUxNQWtHQTFVRUF3d0NZV3hwWTJWek1GNHdEallEVlFRSERBaE9iM0psWlhScGJDQlRiM0psCmFXNW5JRk5oYm1SMmIzSWdVMDFGUXpFS01CRUdDU3FHU0liM0RRRUpBUVlEUVdKcGMyVWdaR1YyWlhKdmNHVnkKY0FvR0NDb1IweURXQXdFSE1GNHdEallEVlFRRERBaE9iM0psWlhScGJDQlRiM0psYVc1bklGTmhibVIyYjNJZwpVMDVGVkdVZ0FvR0NDb1IweURXQXdFSE1GNHdEallEVlFRSERBaE9iM0psWlhScGJDQlRiM0psYVc1bklGTmgKYm1SMmIzSWdVMDVGVkdVZ0FvR0NDb1IweURXQXdFSAotLS0tLUVORCBDRVJUSUZJQ0FURSBSRVFVRVNULS0tLS0K
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
```""",
        "exercise": """### Hands-On Labs

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
    4. Identify which roles grant write permissions within a production namespace.""",
        "insight": """### Interview Q&A

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
- Remember that API group names must be specified correctly in RBAC manifests (e.g., the `apps` group for Deployments, or an empty string `""` for core resources like Pods and Secrets)."""
    },
    {
        "id": 5,
        "title": "Module 5: Cluster Bootstrapping, High Availability, & Lifecycle Upgrades",
        "theory": """### Bootstrapping Production Clusters with Kubeadm
Production-grade Kubernetes clusters are bootstrapped and managed using `kubeadm`. The bootstrapping process consists of several key phases:
1.  **System Verification:** Verify system requirements, load kernel modules (e.g., `br_netfilter`), and configure container runtimes (such as containerd).
2.  **Control Plane Initialization (`kubeadm init`):** Generates self-signed TLS certificates, creates kubeconfig files, and deploys control plane components (api-server, etcd, scheduler, controller-manager) as static pods.
3.  **Network Setup:** Deploys a Container Network Interface (CNI) plugin (such as Calico or Flannel) to enable pod-to-pod networking.
4.  **Joining Nodes (`kubeadm join`):** Adds worker nodes to the cluster using secure tokens generated by the control plane.

### High Availability (HA) topologies
To prevent single points of failure, production clusters use high-availability control planes. This can be configured in two ways:
- **Stacked Control Plane Nodes:** `etcd` runs on the same nodes as the control plane components. This is simpler to configure but requires more resources per control plane node.
- **External etcd Cluster:** `etcd` runs on a separate dedicated cluster of machines, decoupling state storage from control plane processing.

### Sequential Cluster Upgrades
To maintain stability, clusters must be upgraded sequentially, one minor version at a time (e.g., `v1.27` to `v1.28`). The upgrade order is strictly enforced:
1.  **Upgrade kubeadm:** Upgrade the `kubeadm` binary on the primary control plane node.
2.  **Upgrade Control Plane:** Run `kubeadm upgrade plan` and `kubeadm upgrade apply` to upgrade control plane components.
3.  **Upgrade Control Node Binaries:** Upgrade `kubectl` and `kubelet` on the control plane node, then restart the kubelet.
4.  **Upgrade Worker Nodes:** For each worker node, drain the node to evict running workloads, upgrade `kubeadm`, run `kubeadm upgrade node`, upgrade `kubelet` and `kubectl`, restart the kubelet, and uncordon the node.

### etcd Disaster Recovery
Because `etcd` stores the entire state of the cluster, taking regular backups is critical. Backups are captured using `etcdctl` snapshots. If the cluster fails, administrators can restore from a snapshot to recover the cluster state.""",
        "commands": """### Command & Syntax Reference

```bash
# Initialize a control plane node using a custom IP and network range
kubeadm init --pod-network-cidr=10.244.0.0/16 --apiserver-advertise-address=192.168.1.10

# Generate a join command for a new worker node
kubeadm token create --print-join-command

# Drain a node to evict running workloads before maintenance
kubectl drain worker-01 --ignore-daemonsets --delete-emptydir-data

# Uncordon a node to resume scheduling workloads after maintenance
kubectl uncordon worker-01

# Take an etcd database snapshot backup
ETCDCTL_API=3 etcdctl --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  snapshot save /var/lib/db/etcd-backup.db

# Restore an etcd snapshot to a new directory
ETCDCTL_API=3 etcdctl --data-dir=/var/lib/etcd-new \
  snapshot restore /var/lib/db/etcd-backup.db
```""",
        "examples": """### Real-World Examples

#### Example 1: Kubeadm Custom Cluster Configuration
* **Situation:** Bootstrap a high-availability cluster using a custom configuration file to define API server settings and network subnets.
* **Action:** Generate and feed a declarative `ClusterConfiguration` to kubeadm.

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

#### Example 2: Node Pre-flight System Configuration
* **Situation:** Before initializing a cluster, configure host kernel parameters to allow proper container network bridging.
* **Action:** Create a system configuration file to load required kernel modules at boot.

```ini
# /etc/modules-load.d/k8s.conf
br_netfilter
overlay

# /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
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
```""",
        "exercise": """### Hands-On Labs

#### Lab 1: Initializing a Single-Node Control Plane
* **Objective:** Initialize a control plane node using kubeadm.
* **Tasks:**
    1. Configure host kernel modules and container runtime parameters.
    2. Initialize the control plane using `kubeadm init` with a pod network CIDR.
    3. Copy the generated admin kubeconfig to your user directory (`~/.kube/config`).
    4. Deploy a Container Network Interface (CNI) plugin (like Flannel or Calico) and verify all system pods transition to `Running`.

#### Lab 2: Joining Worker Nodes to the Cluster
* **Objective:** Register a worker node to an existing control plane.
* **Tasks:**
    1. Run `kubeadm token create --print-join-command` on the control plane node to generate a join command.
    2. SSH into the worker node and run the join command.
    3. Monitor node registration progress from the control plane using `kubectl get nodes -w`.
    4. Verify that the new worker node enters the `Ready` state.

#### Lab 3: Upgrading the Control Plane Node
* **Objective:** Upgrade a control plane node to a newer minor version.
* **Tasks:**
    1. Drain the control plane node to evict running workloads.
    2. Upgrade the `kubeadm` package to the target version.
    3. Run `kubeadm upgrade plan` followed by `kubeadm upgrade apply <version>`.
    4. Upgrade the `kubelet` and `kubectl` packages on the host.
    5. Restart the kubelet service and uncordon the node.

#### Lab 4: Upgrading Worker Nodes Safely
* **Objective:** Upgrade worker nodes with zero downtime for running workloads.
* **Tasks:**
    1. Drain the worker node from the control plane.
    2. SSH into the worker node and upgrade the `kubeadm` package.
    3. Run `kubeadm upgrade node` on the worker host.
    4. Upgrade the `kubelet` and `kubectl` packages on the worker host.
    5. Restart the kubelet service, then uncordon the node from the control plane.

#### Lab 5: Backing Up and Restoring the etcd Store
* **Objective:** Backup the cluster state and restore it in a disaster recovery scenario.
* **Tasks:**
    1. Take an etcd database snapshot using `etcdctl snapshot save`.
    2. Create a test namespace on the cluster, then verify the snapshot backup was successful.
    3. Run `etcdctl snapshot restore` to restore the snapshot to a new data directory.
    4. Update the etcd static pod manifest (`/etc/kubernetes/manifests/etcd.yaml`) to point to the restored data directory.
    5. Verify the cluster state is restored to the point of the backup (and the test namespace is gone).""",
        "insight": """### Interview Q&A

#### Q1: What happens during the execution of kubeadm init?
* **Answer:** `kubeadm init` runs pre-flight checks, generates self-signed TLS certificates for cluster components, writes kubeconfig files for administrative access, generates static pod manifests for control plane components (api-server, controller-manager, scheduler, etcd), taints the control node to prevent running application workloads, and generates a join token for worker nodes.

#### Q2: Why is it critical to drain a node before performing upgrades or maintenance?
* **Answer:** Draining a node gracefully evicts all running pods (safely rescheduling them on other worker nodes) before host maintenance. This ensures that stateless deployments maintain their active replica counts and prevents stateful applications from experiencing sudden, ungraceful shutdowns.

#### Q3: How do Stacked etcd topologies differ from External etcd topologies?
* **Answer:** In a stacked topology, the etcd database runs on the same nodes as the control plane components. This is simpler to set up and manage, but risks resource contention on the control plane hosts. In an external topology, etcd runs on a separate dedicated cluster of machines, which decouples state storage from processing and improves cluster reliability.

#### Q4: Why must control plane nodes be upgraded before worker nodes?
* **Answer:** Kubernetes maintains strict version skew compatibility rules: the API server must be at the same or a newer version than all other cluster components (such as the controller-manager, scheduler, kubelet, and kube-proxy). Upgrading worker nodes first would break this compatibility and cause API communication errors.

#### Q5: How do you authorize etcdctl commands on a TLS-secured cluster?
* **Answer:** Since etcd is secured with mutual TLS, all commands must include the cluster's client certificates and keys for authentication. These are typically located on the control plane host: `--cacert=/etc/kubernetes/pki/etcd/ca.crt`, `--cert=/etc/kubernetes/pki/etcd/server.crt`, and `--key=/etc/kubernetes/pki/etcd/server.key`.

### CKA Exam Focus
- Ensure you know how to write etcd backup commands using the correct certificate paths.
- Practice upgrading both control plane and worker nodes sequentially, as node upgrades are a common task in the CKA exam.
- Remember to set `ETCDCTL_API=3` before running any etcdctl commands to use the correct API version."""
    },
    {
        "id": 6,
        "title": "Module 6: Services, CoreDNS, and Core Cluster Networking",
        "theory": """### Kubernetes Networking Model
The Kubernetes networking model operates on a flat network design: every Pod receives a unique, routable IP address within the cluster network. Pods can communicate directly with other pods on any node without using Network Address Translation (NAT) or port mapping. This flat network is managed by Container Network Interface (CNI) plugins (such as Calico, Flannel, or Cilium), which handle IP address allocation and configure virtual network interfaces on worker hosts.

### Service Types and Traffic Routing
Because Pods are ephemeral and their IP addresses change when rescheduled, Kubernetes uses Services to provide stable network endpoints. Services use label selectors to identify and route traffic to backing pods:
- **ClusterIP (Default):** Exposes the service on a cluster-internal IP address. This service is only accessible from within the cluster.
- **NodePort:** Exposes the service on each node's physical IP address at a static port (within the range 30000–32767). External traffic sent to any node IP and NodePort is routed to the backing pods.
- **LoadBalancer:** Integrates with cloud providers to provision an external load balancer, which routes traffic to a NodePort service.
- **Headless Service:** Created by setting `clusterIP: None` in the Service specification. It does not create a virtual load-balancing IP. Instead, it allows direct DNS resolution to the individual IP addresses of the backing pods.

### Endpoints & EndpointSlices
Services map to target pods via endpoint objects. The control plane automatically maintains `Endpoints` or modern, highly scalable `EndpointSlices` matching the pod label selectors.

### Cluster DNS and Name Resolution
Kubernetes deploys CoreDNS as a cluster-wide service to handle internal name resolution. CoreDNS automatically creates DNS records for Services and Pods. The standard FQDN format for a Service is:
`<service-name>.<namespace>.svc.cluster.local`

Applications can resolve services in the same namespace using the short service name (e.g., `db-service`), or across namespaces using the full FQDN.""",
        "commands": """### Command & Syntax Reference

```bash
# Expose a Deployment as a NodePort Service imperatively
kubectl expose deployment web-app --port=80 --target-port=8080 --type=NodePort --name=web-service

# View active EndpointSlices in the default namespace
kubectl get endpointslices

# View active Endpoints in the default namespace
kubectl get endpoints

# Query cluster DNS from within a temporary network testing pod
kubectl run nslookup-test --image=busybox:1.36 --restart=Never -it -- nslookup kubernetes.default.svc.cluster.local

# Forward local port 8080 to pod port 80 directly
kubectl port-forward pod/web-app 8080:80

# View configuration mappings for CoreDNS
kubectl get configmap coredns -n kube-system -o yaml
```""",
        "examples": """### Real-World Examples

#### Example 1: Multi-Port Service Configuration
* **Situation:** Deploy a web application that exposes web traffic on port `80` and administration metrics on port `9090`.
* **Action:** Define a ClusterIP Service with multiple named ports.

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
* **Situation:** Expose an application externally on a specific physical host port across all cluster nodes.
* **Action:** Define a NodePort Service with a static port inside the permitted range (`30000-32767`).

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
* **Situation:** Deploy a clustered database where clients must connect directly to individual database replicas (rather than a load-balanced endpoint).
* **Action:** Set `clusterIP: None` in the Service specification to create a Headless Service.

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
* **Situation:** Route traffic through a Kubernetes Service to an external database running outside the cluster.
* **Action:** Create a Service without a label selector and manually define matching `Endpoints`.

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
* **Situation:** Configure cluster name resolution so lookup queries for `*.internal.company` are forwarded to a corporate DNS server at `10.10.10.10`.
* **Action:** Update the cluster's CoreDNS configuration map.

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
```""",
        "exercise": """### Hands-On Labs

#### Lab 1: Exposing Pods Internally via ClusterIP
* **Objective:** Deploy stateless pods and expose them using a ClusterIP service.
* **Tasks:**
    1. Create a Deployment of `httpd:2.4` with 2 replicas labeled `app=http-web`.
    2. Expose the deployment as a ClusterIP Service named `http-internal` on port `80` targeting container port `80`.
    3. Retrieve the Service's ClusterIP and verify internal connectivity from a separate test pod using `curl`.
    4. View the associated endpoints and EndpointSlices generated by the control plane.

#### Lab 2: External Access via NodePort Services
* **Objective:** Expose workloads outside the cluster using NodePort Services.
* **Tasks:**
    1. Create a Pod labeled `app=nodeport-app` running a simple web server.
    2. Expose the pod using a NodePort Service on static port `31080`.
    3. Retrieve the IP address of one of your cluster's worker nodes.
    4. Run a curl query from your host machine to verify connectivity using the worker IP and port `31080`.

#### Lab 3: Setting Up and Querying Headless Services
* **Objective:** Configure a headless service and verify direct name resolution.
* **Tasks:**
    1. Deploy a StatefulSet of 2 replicas running `redis` with labels `app=redis-store`.
    2. Create a Headless Service (setting `clusterIP: None`) named `redis-headless`.
    3. Deploy an interactive network troubleshooting pod running dns tools (such as `nicolaka/netshoot`).
    4. Run `nslookup redis-headless` within the pod and verify that it returns the direct IP addresses of the individual Redis pods.

#### Lab 4: Mapping External Services to Endpoints
* **Objective:** Route traffic from inside the cluster to an external service using manual Endpoints.
* **Tasks:**
    1. Create a ClusterIP Service named `mock-external-api` without specifying a label selector.
    2. Create an Endpoints resource with the same name, mapping it to an external public IP address (e.g., `8.8.8.8`).
    3. Launch a test pod and verify that requests sent to `mock-external-api` are routed to the external target.

#### Lab 5: Customizing CoreDNS Mappings
* **Objective:** Modify CoreDNS configurations to forward name resolution queries to external DNS servers.
* **Tasks:**
    1. Edit the `coredns` ConfigMap in the `kube-system` namespace.
    2. Append a custom forwarding block for domain `test.internal` routing to DNS server `1.1.1.1`.
    3. Restart the CoreDNS deployment to apply the new configurations.
    4. Deploy a network debugging pod and run `nslookup` queries to verify the custom routing.""",
        "insight": """### Interview Q&A

#### Q1: What is the function of the ClusterIP in a Kubernetes Service?
* **Answer:** A ClusterIP is a virtual, stable IP address assigned to a Service. It is managed by `kube-proxy` on each node, which configures network routing rules (using `iptables` or `IPVS`) to intercept traffic sent to the ClusterIP and load-balance it across the backing pod IP addresses.

#### Q2: What happens if you define a Service with a label selector, but no pods match that selector?
* **Answer:** The Service will be created successfully, but its corresponding `Endpoints` and `EndpointSlices` resources will be empty. Any applications or clients attempting to connect to the Service will receive network timeout or connection refused errors.

#### Q3: Why would an operator use a Headless Service instead of a standard Service?
* **Answer:** Headless Services are used when clients need to connect directly to specific individual pods (e.g., in stateful clustered applications like databases or message queues). By disabling the load-balancing IP, name resolution queries return direct records for each pod, allowing clients to establish direct connections to primary or replica nodes.

#### Q4: How does kube-proxy handle traffic in IPVS mode compared to iptables mode?
* **Answer:** In `iptables` mode, `kube-proxy` writes sequential firewall rules for each service, which can degrade packet processing performance as the cluster scales to thousands of services. In `IPVS` mode, it uses IP Virtual Server kernel hashing tables, which process load balancing in O(1) time complexity and improve scalability in large clusters.

#### Q5: What is the naming convention for Service DNS records in Kubernetes?
* **Answer:** The full domain name is `<service-name>.<namespace>.svc.<cluster-domain>` (the default cluster domain is `cluster.local`). Pods in the same namespace can resolve the service using the short service name (e.g., `my-service`), while pods in other namespaces can resolve it using `<service-name>.<namespace>`.

### CKA Exam Focus
- Ensure you understand how to use `kubectl exec` to run `nslookup` tests inside pods for DNS troubleshooting questions.
- Practice configuring multi-port services, as mapping the correct port names and target ports is a common task in the exam."""
    },
    {
        "id": 7,
        "title": "Module 7: Advanced Network Isolation, Ingress, and Gateway API",
        "theory": """### Network Security and NetworkPolicies
By default, the Kubernetes network is completely open: any pod can communicate with any other pod in the cluster, even across different namespaces. To implement security isolation, use `NetworkPolicies`.

`NetworkPolicies` function as local, stateful firewalls managed by the CNI plugin on each node. They restrict pod communication based on specific criteria:
- **Namespace Selector:** Restricts traffic to or from pods within specific namespaces.
- **Pod Selector:** Restricts traffic to or from pods matching defined labels.
- **CIDR Blocks:** Restricts traffic based on IP address ranges (useful for external services).

NetworkPolicies can be configured to manage incoming traffic (Ingress), outgoing traffic (Egress), or both.

### Ingress Controllers and Traffic Routing
While Services manage traffic routing within the cluster, `Ingress` resources manage external access (typically HTTP/HTTPS) to those services.

An Ingress resource defines routing rules, but requires an active `Ingress Controller` (such as Nginx Ingress or Traefik) running in the cluster to process those rules. The Ingress Controller acts as a reverse proxy, parsing routing paths, terminating SSL/TLS sessions, and forwarding traffic directly to backing pods.

### Next-Generation Routing: Gateway API
The `Gateway API` is a next-generation API that models service networking as a modular collection of resources (GatewayClass, Gateway, and HTTPRoute) for role-oriented cluster networking.

It splits networking concerns into separate, dedicated resources:
- **GatewayClass:** Managed by infrastructure providers to define templates for gateways (e.g., defining load balancer integrations).
- **Gateway:** Managed by cluster administrators to define where and how to listen for traffic (e.g., opening port 443 on an external IP).
- **HTTPRoute:** Managed by application developers to define routing rules for specific paths (e.g., routing `/api/v1` to a backend service).""",
        "commands": """### Command & Syntax Reference

```bash
# View all NetworkPolicies in a namespace
kubectl get netpol -n production

# Describe a specific Ingress configuration and target backends
kubectl describe ingress main-ingress

# View active HTTPRoutes in the Gateway API
kubectl get httproute -n production

# View active Gateways in the Gateway API
kubectl get gateway -n production

# Get Ingress Controller logs to troubleshoot routing errors
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller

# Generate a dry-run Ingress resource manifest
kubectl create ingress api-ingress --rule="api.app.com/v1*=v1-service:8080" --dry-run=client -o yaml
```""",
        "examples": """### Real-World Examples

#### Example 1: Restricting Pod Traffic with NetworkPolicies
* **Situation:** Secure an application namespace by blocking all incoming traffic to database pods, except for traffic originating from backend API pods.
* **Action:** Define an Ingress NetworkPolicy in the database namespace.

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
* **Situation:** Expose an internal web application externally using an Ingress resource, securing connection traffic with SSL/TLS certificates.
* **Action:** Deploy an Ingress resource with a defined TLS configuration block.

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
* **Situation:** Route external traffic to different backend services based on the request host and URL path.
* **Action:** Configure an Ingress resource with multiple host and path rules.

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
* **Situation:** Deploy a Gateway resource that listens for HTTP traffic on port 80 across all namespaces.
* **Action:** Define a Gateway resource using the standard Gateway API specification.

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
* **Situation:** Route web traffic to a payment API based on host pathing.
* **Action:** Deploy a declarative `HTTPRoute` referencing an established Gateway.

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
```""",
        "exercise": """### Hands-On Labs

#### Lab 1: Enforcing Default-Deny Network Isolation
* **Objective:** Secure a namespace by blocking all incoming and outgoing traffic by default.
* **Tasks:**
    1. Create a namespace named `secure-zone`.
    2. Apply a default-deny NetworkPolicy targeting all pods in the namespace.
    3. Deploy two test pods in the namespace and verify they cannot communicate with each other.
    4. Deploy a third pod and verify that all external outbound traffic (such as DNS requests) is blocked.

#### Lab 2: Whitelisting Pod Ingress Traffic
* **Objective:** Allow specific pods to communicate while maintaining network isolation.
* **Tasks:**
    1. Create a default-deny NetworkPolicy in your development namespace.
    2. Label a target pod with the label `role=database`.
    3. Create an Ingress NetworkPolicy that allows traffic to the database pod, but only if the source pod has the label `role=api`.
    4. Verify that the api pod can connect to the database, but pods with other labels are blocked.

#### Lab 3: Configuring Ingress Routing Routes
* **Objective:** Route external traffic to distinct endpoints based on URL paths using an Ingress resource.
* **Tasks:**
    1. Deploy two sample applications: `v1-app` and `v2-app`.
    2. Create corresponding ClusterIP services for both apps.
    3. Deploy an Ingress resource routing `/v1` requests to `v1-app` and `/v2` requests to `v2-app`.
    4. Run local tests using custom header maps to verify path routing.

#### Lab 4: Implementing Ingress TLS Termination
* **Objective:** Secure an Ingress route with SSL/TLS certificates.
* **Tasks:**
    1. Generate a self-signed TLS certificate and private key using OpenSSL.
    2. Create a TLS Secret in your cluster using the generated certificate files.
    3. Update your Ingress resource configuration to use the TLS Secret for termination.
    4. Run a curl request using HTTPS and verify the connection is secured.

#### Lab 5: Deploying Gateway API HTTPRoutes
* **Objective:** Route traffic using the modern Gateway API specification.
* **Tasks:**
    1. Install the Gateway API Custom Resource Definitions (CRDs) on your cluster.
    2. Define a Gateway resource named `public-gateway`.
    3. Construct and apply an `HTTPRoute` directing path `/api` requests to a backend service.
    4. Query the gateway endpoint to confirm traffic is routed to the backend service.""",
        "insight": """### Interview Q&A

#### Q1: How does a stateful NetworkPolicy operate?
* **Answer:** NetworkPolicies are stateful firewalls. When you define an Ingress rule allowing incoming traffic to a pod, the system automatically permits the corresponding outgoing return traffic, without requiring you to write an explicit egress rule.

#### Q2: What happens if a pod matches multiple NetworkPolicies?
* **Answer:** NetworkPolicies are additive (logical OR operations). If a pod matches multiple policies, the system combines all permitted rules from those policies. The pod will allow any traffic that is whitelisted by at least one of the applied policies.

#### Q3: Why is an Ingress Controller required to use Ingress resources?
* **Answer:** An Ingress resource is only a declarative configuration file. It does not perform any actual routing. An Ingress Controller must run in the cluster (such as Nginx Ingress or Traefik) to watch for Ingress resources, parse their routing rules, and configure its reverse-proxy engine to route traffic.

#### Q4: What is the difference between Ingress and the Gateway API?
* **Answer:** Ingress is a single resource that combines routing paths, TLS certificates, and provider-specific configurations. The Gateway API is a next-generation API that splits these concerns into separate, dedicated resources: infrastructure teams manage `GatewayClass` and `Gateway`, while application developers manage `HTTPRoute` configurations independently.

#### Q5: How do pathTypes (Exact versus Prefix) affect Ingress routing?
* **Answer:** `Exact` matches the request path exactly (e.g., a rule for `/api` will only match `/api` and not `/api/v1`). `Prefix` matches any sub-paths that start with the prefix (e.g., a rule for `/api` will match `/api`, `/api/v1`, and `/api/v1/users`).

### CKA Exam Focus
- NetworkPolicies only work if your CNI plugin supports them (such as Calico or Cilium). On clusters using Flannel, NetworkPolicies are silently ignored.
- Remember that namespaces must be labeled correctly to use them in NetworkPolicy `namespaceSelectors`."""
    },
    {
        "id": 8,
        "title": "Module 8: Storage Provisioning, CSI, and Volume Lifecycles",
        "theory": """### Kubernetes Storage Architecture
Stateful applications require data to persist beyond the lifecycle of individual container restarts or pod rescheduling. To achieve this, Kubernetes decouples storage consumption from storage provisioning:
- **PersistentVolume (PV):** A cluster-scoped storage resource provisioned by an administrator or a StorageClass. It represents actual storage capacity (e.g., local disk, cloud storage, NFS).
- **PersistentVolumeClaim (PVC):** A namespace-scoped request for storage by a user. It defines access modes, size requirements, and StorageClass names.
- **StorageClass:** A declarative resource that enables dynamic volume provisioning. It defines a provisioner (e.g., a CSI plugin) and parameters for creating PVs automatically when a PVC is created.

### Reclaim Policies and Access Modes
When a PVC is deleted, the corresponding PV behaves according to its Reclaim Policy:
- **Retain:** The physical storage is preserved, allowing administrators to recover data manually. No other PVC can claim this PV until it is manually scrubbed.
- **Delete:** The physical storage and the PV are deleted automatically.

PV access patterns are defined by Access Modes:
- **ReadWriteOnce (RWO):** Volume can be mounted as read-write by a single node.
- **ReadOnlyMany (ROX):** Volume can be mounted read-only by many nodes.
- **ReadWriteMany (RWX):** Volume can be mounted as read-write by many nodes.

### Container Storage Interface (CSI)
The CSI is a standardized specification that allows third-party storage providers to write drivers for Kubernetes without modifying the core Kubernetes codebase. The CSI driver processes the lifecycle of volume creation, mounting, and deletion on worker hosts.""",
        "commands": """### Command & Syntax Reference

```bash
# Get all StorageClasses inside the cluster
kubectl get sc

# Get all Persistent Volumes sorted by storage size
kubectl get pv --sort-by=.spec.capacity.storage

# View all PVCs within a target namespace
kubectl get pvc -n production

# Describe detailed PVC binding logs and provisioner statuses
kubectl describe pvc app-storage-claim

# Inspect physical mounts on worker nodes using SSH
ssh node-01 "df -h"

# Create a PVC dynamically from standard input templates
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: dynamic-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
EOF
```""",
        "examples": """### Real-World Examples

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
```""",
        "exercise": """### Hands-On Labs

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
    4. Delete the pod and verify that the temporary memory allocation is purged.""",
        "insight": """### Interview Q&A

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
- Remember that you must delete the consuming Pod first before you can successfully delete a bound PersistentVolumeClaim (PVC)."""
    },
    {
        "id": 9,
        "title": "Module 9: Advanced Diagnostics, Filtering, & Troubleshooting",
        "theory": """### Advanced Troubleshooting & Diagnostics
Troubleshooting in Kubernetes requires a systematic approach, starting from the node level and working up to application workloads. When issues arise, verify the health of the underlying nodes, inspect the control plane components, analyze the network and DNS settings, and finally debug individual workloads.

### Node Level Diagnostics
If a worker node enters a `NotReady` state, it is typically due to a node-level daemon failure:
- **Kubelet Status:** Inspect the `kubelet` system service using systemd (`systemctl status kubelet`). Use `journalctl -u kubelet` to read detailed error logs.
- **Container Runtime:** Ensure the container runtime (e.g., `containerd`) is running. Check disk space, memory limits, and node-level system logs.

### Control Plane Diagnostics
Control plane components (such as `kube-apiserver`, `kube-controller-manager`, `kube-scheduler`, and `etcd`) usually run as static pods. If these pods are failing:
- Locate their manifest configurations under `/etc/kubernetes/manifests`.
- Read log outputs directly from `/var/log/pods` or `/var/log/containers` on the host machine.
- Verify certificate configurations under `/etc/kubernetes/pki` to identify expiration issues.

### Querying with JSONPath
When managing large clusters, use JSONPath expressions to filter and format `kubectl` outputs, allowing you to extract specific resource fields (like container images, node IPs, or secret data) quickly.

### Metrics & Resource Monitoring
Deploy the `metrics-server` to collect resource utilization metrics (CPU and memory) across the cluster. Use `kubectl top nodes` and `kubectl top pods` to identify resource bottlenecks and diagnose performance issues.""",
        "commands": """### Command & Syntax Reference

```bash
# Get details for a NotReady worker node
kubectl describe node worker-01

# View detailed system logs for the kubelet daemon
journalctl -u kubelet -f --no-pager

# Get container runtime logs on the host machine
journalctl -u containerd -n 100

# Extract all Pod names and their IP addresses using JSONPath
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\\t"}{.status.podIP}{"\\n"}{end}'

# Get the container image used in a specific deployment using JSONPath
kubectl get deployment web-app -o jsonpath='{.spec.template.spec.containers[0].image}'

# View cluster CPU and memory usage using top
kubectl top nodes
kubectl top pods
```""",
        "examples": """### Real-World Examples

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

#### Example 3: JSONPath metadata query script
* **Situation:** Quickly find the node names, operating system, and kernel version of all hosts in the cluster.
* **Action:** Run a JSONPath formatted query from your terminal.

```bash
kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}{"\\t"}{.status.nodeInfo.osImage}{"\\t"}{.status.nodeInfo.kernelVersion}{"\\n"}{end}'
```

#### Example 4: Metrics Server Scrape Configuration
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

#### Example 5: Network Diagnostics Pod Manifest
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
```""",
        "exercise": """### Hands-On Labs

#### Lab 1: Repairing a Failed Kubelet Daemon
* **Objective:** Troubleshoot and fix a kubelet service that fails to start.
* **Tasks:**
    1. SSH into a worker node and stop the kubelet service.
    2. Modify the configuration path inside `/etc/systemd/system/kubelet.service.d/10-kubeadm.conf` to a non-existent file path to simulate a configuration error.
    3. Attempt to start the service and analyze the errors using `journalctl -u kubelet`.
    4. Correct the configuration path, reload the systemd manager daemon, and restart the service successfully.

#### Lab 2: Debugging CrashLooping Pods
* **Objective:** Identify and fix runtime errors in crashing containers.
* **Tasks:**
    1. Deploy a pod running an application that is missing a required configuration.
    2. Check the container status and verify it is in a `CrashLoopBackOff` state.
    3. Retrieve the failure logs using `kubectl logs <pod-name> --previous`.
    4. Edit the pod configuration to fix the issue, apply the changes, and verify the pod runs successfully.

#### Lab 3: Querying API Outputs with JSONPath
* **Objective:** Extract specific fields from cluster resources using JSONPath expressions.
* **Tasks:**
    1. Get the list of all running pods in all namespaces, outputting only their names and namespaces.
    2. Extract the internal IP address of a specific worker node.
    3. Retrieve the path of a static host directory mounted in a volume.
    4. Write a single JSONPath query to list all container images currently running in the cluster.

#### Lab 4: Diagnosing Cluster DNS Failures
* **Objective:** Troubleshoot DNS resolution issues between pods.
* **Tasks:**
    1. Deploy a web service and check if other pods can resolve its name.
    2. If resolution fails, check the health of the CoreDNS pods and review their logs using `kubectl logs -n kube-system -l k8s-app=kube-dns`.
    3. Verify that the CoreDNS Service carries the correct IP address in `/etc/resolv.conf` of the client pods.
    4. Resolve any network policy or configuration blocking CoreDNS.

#### Lab 5: Troubleshooting Static Pod Manifests
* **Objective:** Fix control plane components that fail to start due to configuration errors.
* **Tasks:**
    1. Navigate to `/etc/kubernetes/manifests` on a control plane node.
    2. Introduce a syntax error into `kube-scheduler.yaml`.
    3. Verify that the scheduler pod terminates and is no longer running in the cluster.
    4. Locate and review the container logs, fix the syntax error in the manifest, and verify the scheduler is recovered successfully.""",
        "insight": """### Interview Q&A

#### Q1: How do you diagnose a kubelet that won't start?
* **Answer:** Start by checking the status of the service using `systemctl status kubelet`. If the status is failed, review the system logs using `journalctl -u kubelet -e` to find the specific error (e.g., missing configurations, invalid swap settings, or container runtime connection failures).

#### Q2: Where do you find the logs for static control plane pods if the API server is down?
* **Answer:** Since the API server is down, standard `kubectl` commands will fail. Instead, SSH into the control plane host and read the container log files directly from `/var/log/pods` or `/var/log/containers`.

#### Q3: How do you check if the host has swap enabled, and why does this affect the kubelet?
* **Answer:** Run `free -m` or `cat /proc/swaps` on the host to check if swap is active. By default, the kubelet will fail to start if swap is enabled on the host, as swap can cause unpredictable performance issues (though this behavior can be overridden using `--fail-swap-on=false`).

#### Q4: What tools should be inside a network debugging container?
* **Answer:** A network debugging container (such as `netshoot`) should contain tools like `nslookup` (for DNS resolution), `curl` or `wget` (for HTTP routing tests), `ping` (for network layer reachability), `traceroute` or `mtr` (for path analysis), and `tcpdump` or `tshark` (for packet capturing).

#### Q5: How do you identify certificate expiration issues on a control plane node?
* **Answer:** Run `kubeadm certs check-expiration` on the control plane node to check the expiration dates of all certificates used by the cluster. Additionally, check the kubelet logs for TLS handshake or verification errors, which often indicate expired client certificates.

### CKA Exam Focus
- Troubleshooting is the highest-weighted domain on the CKA exam.
- Practice locating systemd logs using `journalctl` and static pod manifests under `/etc/kubernetes/manifests`.
- Get comfortable using the `crictl` CLI utility to inspect container runtimes directly on worker hosts."""
    }
]