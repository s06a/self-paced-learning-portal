COURSE_ID = "junior_kubernetes_engineer"
COURSE_TITLE = "Junior Kubernetes Engineer"
COURSE_DESCRIPTION = (
    "A production-ready curriculum tailored for Junior Kubernetes Engineers "
    "focusing on declarative workflows, core networking, system diagnostics, "
    "Helm chart packaging, and multi-container cluster observability."
)

# ==========================================
# MODULE 1: CORE WORKLOADS & STATEFUL CONFIG
# ==========================================

M1_THEORY = r"""### The Declarative Paradigm
In Kubernetes, management is entirely declarative rather than imperative. Instead of executing manual sequence steps to deploy servers, engineers declare the desired system state in structured configuration manifests. The Kubernetes Control Plane constantly executes background reconciliation loops (reconciliation controllers) to observe current status and correct drift to ensure the cluster state aligns with declared specifications.

### Core Workload Abstractions
Applications run inside virtualized runtime abstractions designed for lifecycle automation:
* **Pods**: The most primitive, atomic compute unit in a cluster. A Pod wraps one or more co-located containers, sharing network namespaces, storage volumes, and runtime rules.
* **ReplicaSets**: A management process that guarantees a exact designated volume of identical Pod instances are active across available nodes.
* **Deployments**: The industry standard for stateless application management. A Deployment controller abstracts the underlying ReplicaSets, managing rolling updates, transactional rollbacks, health verification, and scaling.

### ConfigMaps and Secrets
12-Factor application design principles dictate separating configurations from compiled code:
* **ConfigMaps**: Store standard key-value pairs (environment variables, flags, or configuration files) loaded by containers at runtime.
* **Secrets**: Designed to contain sensitive keys, passwords, certificates, or tokens. While structurally similar to ConfigMaps, secrets are encoded in Base64 and secure access is restricted using RBAC rules.

### Namespaces
Namespaces partition a single physical Kubernetes cluster into logically isolated environments. They prevent resource naming collisions across distinct environments (such as development, testing, and production) and serve as a boundary for resource quotas and security policies.
"""

M1_COMMANDS = r"""### Command & Syntax Reference
Below are the essential commands for managing workloads, configuration files, and namespaces in a Kubernetes cluster.

* **Workload Execution & State Application:**
  ```bash
  # Apply or update workloads declared in a local YAML configuration file
  kubectl apply -f manifest.yaml

  # List active Pods in the current namespace
  kubectl get pods

  # Retrieve wide information including host IP addresses for active deployments
  kubectl get deployments -o wide

  # View detailed controller states, configurations, and system events
  kubectl describe deployment nginx-deployment
  ```

* **Environment Separation & Configuration Generation:**
  ```bash
  # Create a logical namespace
  kubectl create namespace production-env

  # Create a ConfigMap from static literal flags
  kubectl create configmap app-settings --from-literal=LOG_LEVEL=info --from-literal=MAX_WORKERS=4 -n production-env

  # Create a Secret containing sensitive credentials
  kubectl create secret generic database-creds --from-literal=username=db-admin --from-literal=password=P@ssw0rd987 -n production-env
  ```
"""

M1_EXAMPLES = r"""### Real-World Examples
#### Example 1: Minimal Self-Healing Pod
**Situation:** An engineer needs to deploy a standalone web server to verify that the container runtime on the node is functioning correctly.
**Action:** Define and apply a standalone Nginx Pod manifest in the default namespace.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: static-webserver
  namespace: default
  labels:
    tier: frontend
spec:
  containers:
  - name: web-container
    image: nginx:1.25.3
    ports:
    - containerPort: 80
```

#### Example 2: High Availability Web Deployment
**Situation:** A development team requires three identical instances of an application web tier running concurrently, with rollbacks enabled if updates fail.
**Action:** Configure a declarative Deployment object implementing a RollingUpdate strategy.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: stable-web-tier
  namespace: default
  labels:
    app: secure-web
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: secure-web
  template:
    metadata:
      labels:
        app: secure-web
    spec:
      containers:
      - name: static-nginx
        image: nginx:1.25.3
        ports:
        - containerPort: 80
```

#### Example 3: Decoupling Configurations via ConfigMap
**Situation:** A microservice requires external settings to change its database endpoints and logging behavior without rebuilding the container image.
**Action:** Write a complete ConfigMap manifest and inject its data keys directly into a container specification.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: service-settings
  namespace: default
data:
  DB_HOST: "postgres-service.internal"
  LOG_LEVEL: "WARNING"
---
apiVersion: v1
kind: Pod
metadata:
  name: configured-app
  namespace: default
spec:
  containers:
  - name: app-runner
    image: alpine:3.18
    command: ["sh", "-c", "echo App logging level: $APP_LOG && sleep 3600"]
    env:
    - name: APP_LOG
      valueFrom:
        configMapKeyRef:
          name: service-settings
          key: LOG_LEVEL
```

#### Example 4: Injecting Base64 Sensitive Credentials
**Situation:** A secure microservice needs a protected database password at runtime without putting credentials in plain text in the deployment manifest.
**Action:** Define a Kubernetes Secret containing Base64 encoded values and map it as an environment variable in the application container.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: backend-db-secret
  namespace: default
type: Opaque
data:
  db-pass: U3VwZXJTZWNyZXRLZXkxMjM=
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: secure-database-client
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      app: db-client
  template:
    metadata:
      labels:
        app: db-client
    spec:
      containers:
      - name: client-container
        image: alpine:3.18
        command: ["sh", "-c", "echo Password loaded from secret: $DB_PASSWORD && sleep 3600"]
        env:
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: backend-db-secret
              key: db-pass
```

#### Example 5: Multi-Tenant Namespace Partition
**Situation:** System administrators must isolate system resources for a development team named Team-Alpha to prevent naming conflicts with production workloads.
**Action:** Formulate and deploy a dedicated namespace manifest containing all related workloads.

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: team-alpha-dev
  labels:
    environment: development
    owner: team-alpha
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: local-settings
  namespace: team-alpha-dev
data:
  DEV_MODE: "true"
```
"""

M1_EXERCISE = r"""### Hands-On Labs
#### Lab 1: Deploying a Standalone Nginx Pod
* **Objective:** Create and deploy a single-container web pod and verify its successful initialization.
* **Tasks:**
  1. Write a local configuration file named `nginx-pod.yaml` containing the declarative configuration for a single Nginx pod.
  2. Apply the manifest file to your local cluster context:
     `kubectl apply -f nginx-pod.yaml`
  3. Query the cluster state to track pod initialization status:
     `kubectl get pods -w`
  4. Review detailed configuration data using the describe option:
     `kubectl describe pod static-webserver`
  5. Delete the pod to release allocated resources:
     `kubectl delete -f nginx-pod.yaml`

#### Lab 2: Scaling and Rolling Out a Deployment
* **Objective:** Deploy a scalable workload, increase instance count, and analyze status changes.
* **Tasks:**
  1. Create a local deployment configuration file named `deploy-test.yaml` using Nginx version `1.25.3` with a replica factor of 2.
  2. Deploy the file into the active cluster context.
  3. Use scale commands to increase the active deployment instance count to 5:
     `kubectl scale deployment stable-web-tier --replicas=5`
  4. Verify that 5 instances are running:
     `kubectl get pods`
  5. Clean up the deployment and all managed ReplicaSets:
     `kubectl delete -f deploy-test.yaml`

#### Lab 3: Injecting Environment Variables with a ConfigMap
* **Objective:** Decouple application settings by passing ConfigMap properties down into a container context.
* **Tasks:**
  1. Create a local ConfigMap named `runtime-vars` containing the key `APP_COLOR` with value `green`.
  2. Write a pod manifest where the container prints the `$APP_COLOR` environment variable on startup.
  3. Apply the ConfigMap and the pod manifest to the cluster.
  4. Inspect the standard output log stream of the pod to verify the variable was read correctly:
     `kubectl logs configured-app`
  5. Delete the created objects.

#### Lab 4: Provisioning and Consuming a Secret
* **Objective:** Store sensitive values inside an encrypted secret and consume those settings inside a container.
* **Tasks:**
  1. Create a generic secret key named `api-token-secret` using command-line arguments:
     `kubectl create secret generic api-token-secret --from-literal=token=SuperSecretAccessCode001`
  2. Define a Deployment YAML that exposes this secret as an environment variable named `API_TOKEN`.
  3. Deploy the application to the cluster.
  4. Exec into the pod container and echo the variable to confirm secret ingestion:
     `kubectl exec -it secure-database-client-xxxx -- env | grep API_TOKEN`
  5. Clean up the secret and deployment.

#### Lab 5: Partitioning Resources with a Namespace
* **Objective:** Segment identical config names across two distinct namespaces.
* **Tasks:**
  1. Create two namespaces: `testing` and `staging`.
  2. Create an identical ConfigMap key `ENV_NAME` set to `test` in `testing` and `stage` in `staging`.
  3. Verify namespaces are active using standard list commands:
     `kubectl get namespaces`
  4. Query each namespace to verify the isolation of the ConfigMap values:
     `kubectl get configmap local-settings -n testing -o yaml`
     `kubectl get configmap local-settings -n staging -o yaml`
  5. Clean up both namespaces to remove all associated configurations.
"""

M1_INSIGHT = r"""### Interview Q&A
#### Q1: Why should we use a Deployment instead of a ReplicaSet or bare Pod?
* **Answer:** Deployments represent a higher-level abstraction designed to manage the lifecycle of stateless applications. While a bare Pod does not provide self-healing and a ReplicaSet only ensures scale targets, a Deployment manages rolling updates, allows rollbacks, and provides fine-grained control over rollout strategies (like MaxSurge and MaxUnavailable) to prevent application downtime during updates.

#### Q2: What is the default update strategy of a Deployment, and how does it work?
* **Answer:** The default update strategy is a `RollingUpdate`. Under this strategy, the Deployment controller replaces the old Pods with new ones incrementally. It creates a new ReplicaSet alongside the old one, scaling the new one up while scaling the old one down, keeping a specific percentage of Pods active throughout the transition.

#### Q3: What is the difference between ConfigMap environment injection and mounting it as a volume?
* **Answer:** Injecting ConfigMap keys as environment variables loads those values when the container starts. Any updates to the ConfigMap on the server will not be reflected inside the running container until it is restarted. Mounting a ConfigMap as a volume automatically synchronizes changes. If the underlying ConfigMap data is modified, the mounted files are updated inside the container dynamically.

#### Q4: Is a Kubernetes Secret secure out of the box? Why or why not?
* **Answer:** No. By default, secrets are only Base64 encoded, which is simple obfuscation rather than encryption. Anyone with access to the YAML manifests or with read permissions in the namespace can decode the secrets. To make secrets secure, you must enable Encryption at Rest in the etcd datastore, restrict access using strict RBAC rules, or integrate external security tools like HashiCorp Vault.

#### Q5: How do Namespaces isolate resources, and what objects are non-namespaced?
* **Answer:** Namespaces provide virtual isolation for logical resources. Namespaced resources (like Pods, Deployments, Services, and ConfigMaps) must have unique names within their namespace but can share names across different namespaces. Some resources are cluster-scoped and cannot be isolated within a namespace. Examples of cluster-scoped resources include Nodes, Namespaces, PersistentVolumes, and ClusterRoles.
"""

# ==========================================
# MODULE 2: SERVICE DISCOVERY & NETWORKING
# ==========================================

M2_THEORY = r"""### Internal & External Connectivity
Because Pods are ephemeral, they are constantly created and destroyed, and their IP addresses are unreliable. To establish stable network paths for application tiers, Kubernetes decouples workloads using **Services**. Services use selectors (label queries) to identify target Pods and automatically route incoming traffic to those healthy instances.

### Service Types
* **ClusterIP**: Exposes the service on a cluster-internal IP address. This is the default service type and makes the workload accessible only from other workloads within the same cluster.
* **NodePort**: Allocates a static port from a dedicated range (typically 30000–32767) on every node's external network interface. Traffic sent to any node's IP address on that allocated port is forwarded to the corresponding target container port.
* **LoadBalancer**: Integrates with external cloud infrastructure (such as AWS, GCP, Azure, or OpenStack) to provision an external load balancer, assigning a public IP address that routes internet traffic directly to the service.
* **Headless Services**: Created by setting `.spec.clusterIP` to `"None"`. Instead of routing traffic through a single service IP, a Headless Service returns the individual IP addresses of the targeted backend pods directly via DNS queries. This is useful for stateful applications like databases or caches.

### Ingress Routing
An **Ingress** resource is an API object that manages external HTTP and HTTPS traffic to services within a cluster. It works as a reverse proxy, routing incoming requests to backend services based on defined path rules, host names, or URL paths. An Ingress resource requires an Ingress Controller (like NGINX Ingress Controller or Traefik) running in the cluster to process and enforce these routing rules.
"""

M2_COMMANDS = r"""### Command & Syntax Reference
Below are the essential commands for configuring, exposing, and auditing Kubernetes services and ingress configurations.

* **Service Resource Creation & Monitoring:**
  ```bash
  # Expose an existing active Deployment as a ClusterIP service
  kubectl expose deployment stable-web-tier --port=80 --target-port=8080 --name=internal-svc

  # List all configured services in the current namespace
  kubectl get svc

  # Show detailed endpoints mapped to a specific service
  kubectl get endpoints internal-svc

  # Describe active services and target port bindings
  kubectl describe svc internal-svc
  ```

* **Ingress Integration & Auditing:**
  ```bash
  # List all ingress rules in the current namespace
  kubectl get ingress

  # Fetch details of ingress host matchings and SSL configurations
  kubectl describe ingress public-ingress
  ```
"""

M2_EXAMPLES = r"""### Real-World Examples
#### Example 1: Decoupled Service with ClusterIP
**Situation:** An engineering team needs to expose an internal backend API service to a frontend web tier, ensuring it is not accessible from outside the cluster.
**Action:** Deploy an internal ClusterIP Service pointing to backend workloads matching the label `tier: backend`.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: api-cluster-service
  namespace: default
spec:
  type: ClusterIP
  selector:
    tier: backend
  ports:
  - name: http
    protocol: TCP
    port: 80
    targetPort: 8080
```

#### Example 2: NodePort External Exposure
**Situation:** Developers need to quickly access a web dashboard tool on their local machines without configuring external ingress systems or public load balancers.
**Action:** Declare a NodePort Service that maps an external high port directly to the web dashboard pod.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: developer-nodeport-svc
  namespace: default
spec:
  type: NodePort
  selector:
    app: dev-dashboard
  ports:
  - name: http
    protocol: TCP
    port: 80
    targetPort: 80
    nodePort: 31000
```

#### Example 3: Provisioning an External Cloud LoadBalancer
**Situation:** An e-commerce service needs to accept traffic directly from the internet via a public IP address provisioned by a cloud service provider.
**Action:** Define a LoadBalancer Service resource targeting the frontend web service.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: public-ecommerce-svc
  namespace: default
spec:
  type: LoadBalancer
  selector:
    app: shop-frontend
  ports:
  - name: https
    protocol: TCP
    port: 443
    targetPort: 8443
```

#### Example 4: Implementing a Headless Service
**Situation:** A stateful clustered database deployment (such as MongoDB or PostgreSQL) requires each individual node to communicate directly with other nodes using unique hostnames instead of a single service proxy IP.
**Action:** Declare a Headless Service by setting the clusterIP field to None.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: database-headless-svc
  namespace: default
spec:
  clusterIP: None
  selector:
    app: stateful-db
  ports:
  - name: dbport
    port: 5432
    targetPort: 5432
```

#### Example 5: Setting Ingress HTTP Host and Path Routing Rules
**Situation:** A cluster runs a web application and an API backend. Both need to be exposed externally on a single public IP address under distinct domain subpaths.
**Action:** Create an Ingress resource with specific host and path routing rules pointing to the target backend services.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: main-application-ingress
  namespace: default
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - host: app.company.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-cluster-service
            port:
              number: 80
      - path: /
        pathType: Prefix
        backend:
          service:
            name: public-ecommerce-svc
            port:
              number: 443
```
"""

M3_EXERCISE = None  # Defined in separate sections for modular cleanliness
# ==========================================
# MODULE 2: LABS & INSIGHTS (SPLIT FOR PYTHON VALUE CONVERSION)
# ==========================================

M2_EXERCISE = r"""### Hands-On Labs
#### Lab 1: Exposing a Backend via ClusterIP
* **Objective:** Deploy a target application and configure internal-only cluster routing to access it.
* **Tasks:**
  1. Create a pod configuration named `app-pod.yaml` containing the configuration for an application web server labeled `tier: backend`. Apply it to your cluster.
  2. Write a Service manifest named `cluster-ip.yaml` declaring a Service of type ClusterIP targeting container port 80.
  3. Deploy the Service configuration:
     `kubectl apply -f cluster-ip.yaml`
  4. Launch an ephemeral pod to test connection to the backend service over the internal cluster network:
     `kubectl run network-client -it --rm --image=alpine:3.18 -- wget -qO- http://api-cluster-service:80`
  5. Delete the resource configurations.

#### Lab 2: Connecting to an App via NodePort
* **Objective:** Configure a NodePort Service to access an in-cluster web application from your local machine.
* **Tasks:**
  1. Create an Nginx web deployment with 2 replicas in your local cluster.
  2. Create a NodePort Service named `nginx-nodeport` targeting port 80 and mapping it to nodePort 32000. Apply it to the cluster.
  3. Verify the port allocation by running:
     `kubectl get svc nginx-nodeport`
  4. Access the application using curl or a web browser via your local node's IP address:
     `curl http://127.0.0.1:32000`
  5. Delete the service and deployment.

#### Lab 3: Validating Pod DNS Resolution
* **Objective:** Test internal CoreDNS resolution of Service names within the cluster.
* **Tasks:**
  1. Deploy a backend Service named `dns-service` matching workloads labeled `app: dns-target`.
  2. Deploy a pod named `dns-tester` using the `alpine:3.18` image.
  3. Exec into the pod and install dnsutils (if using an image that supports package management) or run lookup tests:
     `kubectl exec -it dns-tester -- nslookup dns-service`
  4. Analyze the output IP address to confirm it matches the ClusterIP of the `dns-service`.
  5. Delete the tester pod and service.

#### Lab 4: Configuring and Testing a Headless Service
* **Objective:** Deploy a Headless Service to discover individual Pod IP addresses directly via DNS queries.
* **Tasks:**
  1. Create a deployment named `database-nodes` running 3 replicas of an alpine web server. Label these pods with `app: stateful-db`.
  2. Define a Headless Service (setting clusterIP to `None`) named `db-headless` targeting those database node labels. Apply it to your cluster.
  3. Deploy a temporary troubleshooting pod named `dns-dnsutils` using image `tutum/dnsutils` or similar.
  4. Run a DNS lookup on the Headless Service name:
     `kubectl exec -it dns-dnsutils -- nslookup db-headless`
  5. Verify that the DNS lookup returns three distinct A-records (IP addresses) matching the individual IPs of your running backend pods.

#### Lab 5: Implementing Basic Ingress Path Rules
* **Objective:** Deploy an Ingress resource to route local domain traffic to multiple internal services.
* **Tasks:**
  1. Create two separate web server deployments: `web-one` and `web-two`.
  2. Create two corresponding ClusterIP services: `svc-one` on port 80 and `svc-two` on port 80.
  3. Write an Ingress manifest that routes traffic sent to `http://test-router.local/first` to `svc-one` and traffic sent to `http://test-router.local/second` to `svc-two`.
  4. Apply the Ingress configuration to the cluster.
  5. Verify that the routing rules are configured correctly in the cluster:
     `kubectl describe ingress main-application-ingress`
"""

M2_INSIGHT = r"""### Interview Q&A
#### Q1: How does a Service determine which Pods to route traffic to?
* **Answer:** Services use `label selectors` to target Pods. The Service controller continuously queries the API Server for active Pods that match these defined label selectors. When it finds matching Pods, their current IP addresses are added to an associated `Endpoints` object. This Endpoints list is what the cluster uses to route traffic directly to active, healthy container instances.

#### Q2: When would you use a Headless Service instead of a standard ClusterIP?
* **Answer:** A Headless Service (defined by setting `clusterIP: None`) is used when you need to bypass standard service proxying and load balancing. Instead of returning a single ClusterIP, DNS queries for a Headless Service return the individual IP addresses of all targeted backends. This is useful for stateful applications like distributed databases (e.g., Cassandra, PostgreSQL replicas) where client applications need to connect directly to specific nodes in the cluster.

#### Q3: What is the difference between targetPort and port in a Service YAML?
* **Answer:** The `port` field is the port number that the Service exposes internally within the cluster. Other workloads send traffic to the Service using this port. The `targetPort` field is the port number that the application container is listening on inside the backend Pod. Incoming traffic to the Service is forwarded down to this port on the target container.

#### Q4: What is the typical port allocation range for a NodePort Service?
* **Answer:** The default port allocation range reserved for NodePort Services is `30000–32767`. If you do not specify a port in your manifest, the API Server will automatically allocate an unused port from this range. Cluster administrators can customize this port range by modifying the `--service-node-port-range` flag on the API Server configuration.

#### Q5: Why is an Ingress Controller needed alongside an Ingress Resource?
* **Answer:** An Ingress Resource is just a metadata definition. It stores the routing rules in the etcd database but does not handle or route any actual network traffic itself. An Ingress Controller is the active system daemon (such as NGINX or Traefik) that runs in the cluster, monitors the API Server for new Ingress Resources, and configures its reverse proxy engine to route incoming HTTP/HTTPS traffic according to those defined rules.
"""

# ==========================================
# MODULE 3: LOCAL WORKFLOWS & POD DIAGNOSTICS
# ==========================================

M3_THEORY = r"""### Cluster Emulation and Development Workflow
Testing Kubernetes configurations directly on a remote server can be slow and risky. To speed up development, engineers use local cluster engines like **Kind** (Kubernetes-in-Docker) or **Minikube**. These tools run entire Kubernetes environments within containerized node frameworks or small virtual machines on a local laptop. This allows developers to safely test their deployments, manifest structures, and networking configurations locally before deploying changes to shared testing or production environments.

### System Diagnostics with Kubectl
When a deployed application does not work as expected, developers can use several built-in commands to inspect and diagnose the issue:
* `kubectl describe`: Queries complete metadata, active configurations, controller specifications, and recent system event logs for a resource.
* `kubectl logs`: Retrieves the standard output (stdout) and standard error (stderr) streams from a running container.
* `kubectl exec`: Opens an interactive shell session directly inside a container to test local files or verify database connections.
* `kubectl port-forward`: Sets up a secure network tunnel that maps a port on your local machine to a container port in the cluster, bypassing the service layer for quick testing.

### Understanding Common Pod Failures
Understanding common container errors helps engineers quickly troubleshoot issues:
* **ImagePullBackOff**: The container runtime is unable to download the container image. This is usually caused by a typo in the image name, an invalid tag, or missing private registry credentials.
* **CrashLoopBackOff**: The container starts, but exits repeatedly. This points to runtime application crashes, syntax errors in startup commands, missing configuration variables, or database connection failures.
* **OOMKilled**: The container is terminated by the host node because its memory usage exceeded the maximum limit defined in the Pod specification.
* **Pending**: The Pod cannot be scheduled on any node. This typically indicates a lack of available CPU/Memory resources in the cluster, or unmet scheduling rules like taints, tolerations, or node selectors.
"""

M3_COMMANDS = r"""### Command & Syntax Reference
Below are essential diagnostic and execution commands used to troubleshoot and verify active applications.

* **Cluster Initialization & Status Inspection:**
  ```bash
  # Create a multi-node cluster configuration using Kind
  kind create cluster --name local-dev --config cluster-config.yaml

  # Query the health and version information of the local API Server
  kubectl cluster-info
  ```

* **Application Diagnostics & Troubleshooting:**
  ```bash
  # Check system events across the active namespace, sorted by timestamp
  kubectl get events --sort-by='.metadata.creationTimestamp'

  # Retrieve logs from a container that crashed and exited previously
  kubectl logs web-pod -c nginx-container --previous

  # Open an interactive terminal session inside a target container
  kubectl exec -it web-pod -c nginx-container -- /bin/sh

  # Map local workstation port 8080 to container port 80 inside a pod
  kubectl port-forward pod/web-pod 8080:80
  ```
"""

M3_EXAMPLES = r"""### Real-World Examples
#### Example 1: Kind Multi-Node Local Cluster
**Situation:** An infrastructure team needs to test how an application behaves when deployed across a cluster with multiple worker nodes on their local laptops.
**Action:** Write a Kind cluster configuration manifest defining one control-plane node and two worker nodes, then initialize the cluster.

```yaml
# kind-config.yaml
apiVersion: kind.x-k8s.io/v1alpha4
kind: Cluster
nodes:
- role: control-plane
- role: worker
- role: worker
```

*CLI execution command to create the cluster:*
```bash
kind create cluster --name dev-cluster --config kind-config.yaml
```

#### Example 2: Diagnosing ImagePullBackOff
**Situation:** A deployment is failing with an `ImagePullBackOff` status because of an incorrect tag version in the container image path.
**Action:** Use describe commands to inspect the pull events, find the tag error, and apply a corrected manifest file.

*Failing Manifest File:*
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: billing-api-pod
  namespace: default
spec:
  containers:
  - name: api-container
    image: alpine:invalid-v10.9.1
    command: ["sleep", "3600"]
```

*Steps to diagnose and apply the fix:*
```bash
# 1. View historical events to identify the failure details
kubectl describe pod billing-api-pod
# Output log shows: Failed to pull image "alpine:invalid-v10.9.1": rpc error: code = NotFound

# 2. Modify the image path to use a valid tag (alpine:3.18) and reapply the file
```

*Corrected Manifest File:*
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: billing-api-pod
  namespace: default
spec:
  containers:
  - name: api-container
    image: alpine:3.18
    command: ["sleep", "3600"]
```

#### Example 3: Fixing a CrashLoopBackOff Application
**Situation:** A database client container keeps crashing at launch, with its status degrading to `CrashLoopBackOff` because it is missing a required connection string.
**Action:** Retrieve the output logs from the crashed container, identify the missing setting, and update the manifest.

*Failing Manifest File:*
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: db-client-pod
  namespace: default
spec:
  containers:
  - name: app-container
    image: busybox
    command: ["sh", "-c", "if [ -z \"$DB_URL\" ]; then echo 'FATAL ERROR: Connection URL missing!'; exit 1; else sleep 3600; fi"]
```

*Steps to diagnose and apply the fix:*
```bash
# 1. Inspect container log outputs to find the error message
kubectl logs db-client-pod
# Output shows: FATAL ERROR: Connection URL missing!

# 2. Add the missing DB_URL environment variable to the manifest and re-apply
```

*Corrected Manifest File:*
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: db-client-pod
  namespace: default
spec:
  containers:
  - name: app-container
    image: busybox
    command: ["sh", "-c", "if [ -z \"$DB_URL\" ]; then echo 'FATAL ERROR: Connection URL missing!'; exit 1; else sleep 3600; fi"]
    env:
    - name: DB_URL
      value: "mongodb://mongo-db.default.svc:27017/prod"
```

#### Example 4: Diagnosing an OOMKilled Container
**Situation:** A memory-intensive application pod is crashing with an exit code of `137` because its memory usage exceeds the maximum limit defined in the manifest.
**Action:** Analyze the pod state details, increase the memory limit in the manifest, and reapply the configuration.

*Failing Manifest File:*
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: data-aggregator-pod
  namespace: default
spec:
  containers:
  - name: memory-hog
    image: alpine:3.18
    command: ["sh", "-c", "dd if=/dev/zero of=/dev/null bs=128M count=1"]
    resources:
      limits:
        memory: "32Mi"
      requests:
        memory: "16Mi"
```

*Steps to diagnose and apply the fix:*
```bash
# 1. Check pod status details
kubectl describe pod data-aggregator-pod
# Output logs show: State: Terminated, Reason: OOMKilled, Exit Code: 137

# 2. Increase the memory limit to 256Mi and reapply the configuration
```

*Corrected Manifest File:*
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: data-aggregator-pod
  namespace: default
spec:
  containers:
  - name: memory-hog
    image: alpine:3.18
    command: ["sh", "-c", "dd if=/dev/zero of=/dev/null bs=128M count=1"]
    resources:
      limits:
        memory: "256Mi"
      requests:
        memory: "128Mi"
```

#### Example 5: Resolving an Unschedulable Pending Pod
**Situation:** A workload is stuck in a `Pending` state because it requests more CPU resources than any single worker node has available.
**Action:** Use describe commands to verify the scheduling failure, lower the CPU request in the manifest, and redeploy.

*Failing Manifest File:*
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: giant-workload-pod
  namespace: default
spec:
  containers:
  - name: nginx-web
    image: nginx:1.25.3
    resources:
      requests:
        cpu: "99"
```

*Steps to diagnose and apply the fix:*
```bash
# 1. View scheduling logs
kubectl describe pod giant-workload-pod
# Output reports: Warning FailedScheduling ... 0/3 nodes are available: 3 Insufficient cpu.

# 2. Reduce CPU request to 100m (0.1 CPU core) and reapply the configuration
```

*Corrected Manifest File:*
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: giant-workload-pod
  namespace: default
spec:
  containers:
  - name: nginx-web
    image: nginx:1.25.3
    resources:
      requests:
        cpu: "100m"
```
"""

# ==========================================
# MODULE 3: LABS & INSIGHTS (SPLIT FOR PYTHON VALUE CONVERSION)
# ==========================================

M3_EXERCISE = r"""### Hands-On Labs
#### Lab 1: Provisioning a Multi-Node Kind Cluster
* **Objective:** Set up and run a local Kubernetes cluster containing one control-plane and two worker nodes using Kind.
* **Tasks:**
  1. Install the Kind CLI on your local workstation.
  2. Write a Kind configuration file named `kind-three-node.yaml` that defines a multi-node topology.
  3. Initialize the cluster using the configuration file:
     `kind create cluster --name lab-cluster --config kind-three-node.yaml`
  4. Verify that all nodes are initialized and in a `Ready` state:
     `kubectl get nodes`
  5. Delete the cluster when finished:
     `kind delete cluster --name lab-cluster`

#### Lab 2: Fixing an Image Retrieval Typo in a Deployment
* **Objective:** Identify and fix a deployment failure caused by an invalid image tag.
* **Tasks:**
  1. Deploy a file named `bad-deployment.yaml` with the container image set to `nginx:invalid-ver-99`.
  2. Monitor the deployment to verify the pod status degrades to `ErrImagePull` or `ImagePullBackOff`.
  3. Run `kubectl describe pod` to inspect the error events from the container runtime.
  4. Edit the manifest file to update the container image to a valid version (`nginx:1.25.3`).
  5. Reapply the manifest and verify that the pod status transitions to `Running`.

#### Lab 3: Debugging an Application Runtime Crash
* **Objective:** Diagnose and fix a container that keeps crashing on startup because of an invalid environment variable value.
* **Tasks:**
  1. Write a pod manifest named `crashing-app.yaml` with a start command that exits with a non-zero exit code if `DEBUG_LEVEL` is not set to `VERBOSE`.
  2. Deploy the pod into the cluster.
  3. Check the pod status and confirm it goes into a `CrashLoopBackOff` loop:
     `kubectl get pods`
  4. Retrieve the container logs to find the application-level crash details:
     `kubectl logs crashing-app`
  5. Update the manifest to define `DEBUG_LEVEL=VERBOSE`, reapply, and confirm the pod runs successfully.

#### Lab 4: Resolving Memory Resource Limits for an OOM-Killed App
* **Objective:** Identify a container crashing because of resource limits and resolve the issue by adjusting those limits.
* **Tasks:**
  1. Deploy an application manifest that allocates more memory than its limit configuration allows.
  2. Monitor the cluster to watch the pod crash with an `OOMKilled` status.
  3. Run describe commands to confirm the container was terminated by the OOM killer with exit code `137`.
  4. Increase the memory limit in the manifest file to provide enough memory overhead.
  5. Reapply the manifest and verify that the application runs stably.

#### Lab 5: Scheduling a Pending Pod by Adjusting Resources
* **Objective:** Find why a pod is stuck in a Pending state and fix it by reducing its CPU request.
* **Tasks:**
  1. Deploy a workload manifest named `massive-cpu-pod.yaml` requesting 50 CPU cores.
  2. Verify that the pod is stuck in a `Pending` state:
     `kubectl get pods`
  3. Run `kubectl describe pod` to view the scheduler's event logs and confirm it failed due to insufficient CPU resources.
  4. Lower the requested CPU value in the manifest file to `250m` (0.25 cores).
  5. Reapply the configuration and confirm that the scheduler is now able to assign the pod to a node.
"""

M3_INSIGHT = r"""### Interview Q&A
#### Q1: What does the CrashLoopBackOff status signify, and how do we start debugging it?
* **Answer:** A `CrashLoopBackOff` status means that the container started, but repeatedly crashed and exited. Since this is an application-level crash rather than a Kubernetes scheduling issue, the best way to start debugging is by pulling the container's logs using `kubectl logs <pod-name>`. If the container keeps restarting, you can view the logs from the previous failed run using the `--previous` flag.

#### Q2: Why would a Pod remain in a Pending state indefinitely?
* **Answer:** A Pod remains in a `Pending` state when the scheduler cannot find any worker node that meets its resource requirements or scheduling constraints. This is often caused by requesting more CPU or memory than the nodes have available, using node selectors or affinity rules that do not match any nodes, or having node taints that the Pod does not tolerate.

#### Q3: What is the difference between running `kubectl logs` on an active Pod versus a terminated Pod?
* **Answer:** Running `kubectl logs <pod-name>` retrieves the current stdout/stderr stream from the actively running container inside the Pod. If the container has crashed and restarted, running `kubectl logs <pod-name>` only shows the logs from the new container instance. To view the logs from the crashed container that was terminated, you must run `kubectl logs <pod-name> --previous`.

#### Q4: How can we interactively check internal cluster networking connectivity from inside a running container?
* **Answer:** You can check internal connectivity by opening an interactive shell inside the container using `kubectl exec -it <pod-name> -- /bin/sh` or `/bin/bash`. Once inside the container, you can run networking tools like `wget`, `curl`, `nslookup`, or `ping` (depending on what is installed in the container image) to verify connections to database services, external APIs, or other internal microservices.

#### Q5: What does an exit code of 137 represent when diagnosing a container termination?
* **Answer:** An exit code of `137` indicates that the container was terminated by a Unix `SIGKILL` signal (Signal 9 + Exit Code 128). In Kubernetes, this most commonly occurs when the host node's Out-Of-Memory (OOM) killer terminates a container because its active memory usage exceeded the maximum memory limit defined in its manifest.
"""

# ==========================================
# MODULE 4: APPLICATION PACKAGING WITH HELM
# ==========================================

M4_THEORY = r"""### Application Packaging and Management
Deploying applications by running separate YAML manifests manually can quickly become hard to scale. **Helm** solves this as a package manager for Kubernetes. Helm packages related sets of Kubernetes resources into a single structured archive called a **Chart**.

### Helm Templates and Values
A Helm chart separates structural resource layouts from environment-specific configuration values:
* **Templates**: Core Kubernetes manifests written with placeholders and template logic.
* **values.yaml**: The configuration file that defines the values used to fill in those template placeholders at deployment time.

By using different values files (e.g., `values-dev.yaml`, `values-prod.yaml`), engineers can deploy identical application patterns across different environments without modifying the underlying resource templates.

### Managing Helm Releases
When you install a Helm chart, it creates an active instance in the cluster called a **Release**. Helm tracks the history of all release updates, allowing engineers to:
* Deploy configuration updates using `helm upgrade`.
* View previous deployment histories.
* Roll back to a previous stable state using `helm rollback` if an update fails.

### Managing Registry Access
When deploying containers, you can control when and how images are downloaded from registries:
* **imagePullPolicy**: Controls how the local container runtime downloads images:
  * `Always`: Always checks the remote container registry for updates, even if the image exists locally.
  * `IfNotPresent`: Only downloads the image if it is missing from the local node's cache.
  * `Never`: Relies entirely on images pre-loaded on the host node.
* **imagePullSecrets**: Links container specifications to local Docker registry authentication credentials, allowing secure image pulling from protected, private registries.
"""

M4_COMMANDS = r"""### Command & Syntax Reference
Below are essential commands for managing Helm charts, tracking release histories, and configuring private registries.

* **Helm Repository and Release Operations:**
  ```bash
  # Register a new chart repository
  helm repo add bitnami https://charts.bitnami.com/bitnami

  # Update the local cache of available charts
  helm repo update

  # Deploy a chart using custom configuration values
  helm install app-cache bitnami/redis -f dev-values.yaml -n cache-tier --create-namespace

  # List active Helm releases in the current namespace
  helm list
  ```

* **Release Lifecycle & Upgrades:**
  ```bash
  # Apply updated configurations to a release
  helm upgrade app-cache bitnami/redis -f prod-values.yaml -n cache-tier

  # View the revision history of a release
  helm history app-cache -n cache-tier

  # Roll back a release to a previous stable version (e.g., revision 1)
  helm rollback app-cache 1 -n cache-tier

  # Uninstall a release and delete its associated resources
  helm uninstall app-cache -n cache-tier
  ```
"""

M4_EXAMPLES = r"""### Real-World Examples
#### Example 1: Overriding Bitnami Redis Configuration Values
**Situation:** An engineering team wants to deploy Redis as a replicated high-availability cluster using a Bitnami Helm chart, with resource limits tailored for development.
**Action:** Write a custom `values.yaml` file to define the replica topology and memory requests, and deploy it using Helm.

*Custom values.yaml:*
```yaml
architecture: replication
auth:
  enabled: true
  sentinel: false
replica:
  replicaCount: 2
  resources:
    requests:
      cpu: "100m"
      memory: "128Mi"
    limits:
      cpu: "300m"
      memory: "256Mi"
```

*Commands to execute the deployment:*
```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm install dev-redis bitnami/redis -f values.yaml --namespace dev-databases --create-namespace
```

#### Example 2: Upgrading a Helm Release
**Situation:** Operators need to scale up their Redis replica count and increase its memory limits to handle growing traffic in a development cluster.
**Action:** Modify the replica count and limits in the values file, then upgrade the running Helm release.

*Updated values.yaml:*
```yaml
architecture: replication
auth:
  enabled: true
  sentinel: false
replica:
  replicaCount: 4
  resources:
    requests:
      cpu: "100m"
      memory: "128Mi"
    limits:
      cpu: "500m"
      memory: "512Mi"
```

*Commands to upgrade and verify:*
```bash
helm upgrade dev-redis bitnami/redis -f values.yaml --namespace dev-databases
```

#### Example 3: Reverting a Failed Update
**Situation:** An upgrade was deployed with misconfigured settings, causing database connection failures. The team needs to quickly restore the database to its previous stable state.
**Action:** Review the deployment history of the release and roll back to the last stable revision.

*Commands to view history and roll back:*
```bash
# 1. View the revision history
helm history dev-redis --namespace dev-databases
# Output displays:
# REVISION    UPDATED                     STATUS        CHART          APP VERSION    DESCRIPTION
# 1           Mon Jul 20 22:00:00 2026    superseded    redis-18.6.1   7.2.4          Install complete
# 2           Mon Jul 20 22:05:00 2026    failed        redis-18.6.1   7.2.4          Upgrade failed

# 2. Roll back to revision 1
helm rollback dev-redis 1 --namespace dev-databases
```

#### Example 4: Setting Container Image Pull Policies
**Situation:** A development team is frequently updating a test image tag and needs the Kubernetes cluster to always download the latest version of the image from the registry on startup, bypassing the local node's cache.
**Action:** Set the container's `imagePullPolicy` to `Always` in the pod deployment specification.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dynamic-webserver
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      app: web-server
  template:
    metadata:
      labels:
        app: web-server
    spec:
      containers:
      - name: main-app
        image: company/web-frontend:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 80
```

#### Example 5: Deploying with imagePullSecrets for Private Registries
**Situation:** A security team is hosting sensitive container images in a private registry that requires authenticated credentials to pull.
**Action:** Create a registry access secret in the namespace and reference it in the `imagePullSecrets` section of the Deployment manifest.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: private-registry-creds
  namespace: default
type: kubernetes.io/dockerconfigjson
data:
  .dockerconfigjson: eyJhdXRocyI6eyJteS1wcml2YXRlLXJlZ2lzdHJ5LmlvIjp7InVzZXJuYW1lIjoicmVnaXN0cnktdXNlciIsInBhc3N3b3JkIjoiU3VwZXJTZWNyZXRSZWdpc3RyeVBhc3N3b3JkMTIzIiwiZW1haWwiOiJzcmVAY29tcGFueS5jb20iLCJhdXRoIjoiZFhObGNpMTFjMlZ5T2xOMWNHVnlVMlZqY21WMFVHVnpjM2R2Y2tRPSJ9fX0=
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: private-service-deployment
  namespace: default
spec:
  replicas: 2
  selector:
    matchLabels:
      app: private-api
  template:
    metadata:
      labels:
        app: private-api
    spec:
      imagePullSecrets:
      - name: private-registry-creds
      containers:
      - name: api-container
        image: my-private-registry.io/apps/secure-api:v1.0.0
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 8080
```
"""

# ==========================================
# MODULE 4: LABS & INSIGHTS (SPLIT FOR PYTHON VALUE CONVERSION)
# ==========================================

M4_EXERCISE = r"""### Hands-On Labs
#### Lab 1: Deploying a Customized Redis Cluster with Helm
* **Objective:** Register a chart repository and deploy a replica-backed database using custom value configuration settings.
* **Tasks:**
  1. Add the Bitnami repository to Helm:
     `helm repo add bitnami https://charts.bitnami.com/bitnami`
  2. Create a configuration override file named `redis-values.yaml`:
     ```yaml
     architecture: standalone
     auth:
       enabled: false
     master:
       resources:
         requests:
           memory: "64Mi"
         limits:
           memory: "128Mi"
     ```
  3. Deploy the Redis release named `lab-db` inside namespace `database-dev`:
     `helm install lab-db bitnami/redis -f redis-values.yaml -n database-dev --create-namespace`
  4. Verify the deployment and check that all pods are running:
     `kubectl get pods -n database-dev`

#### Lab 2: Managing Release Upgrades and Version Rollbacks
* **Objective:** Perform updates to a Helm release and roll back to a previous revision.
* **Tasks:**
  1. Modify your local `redis-values.yaml` file to scale the memory limit to `256Mi`.
  2. Apply the configuration change using the upgrade command:
     `helm upgrade lab-db bitnami/redis -f redis-values.yaml -n database-dev`
  3. View the release history to verify the new revision was created:
     `helm history lab-db -n database-dev`
  4. Roll back the release to its original configuration (revision 1):
     `helm rollback lab-db 1 -n database-dev`
  5. Verify that the memory limits were reverted by inspecting the master pod specification.

#### Lab 3: Configuring Image Pull Secrets for Private Registries
* **Objective:** Create a docker-registry secret and configure a Deployment to pull images using those credentials.
* **Tasks:**
  1. Create a namespace named `secure-pulls`.
  2. Create a secure container registry configuration secret named `custom-registry-key` using mock credentials:
     `kubectl create secret docker-registry custom-registry-key --docker-server=https://index.docker.io/v1/ --docker-username=test-user --docker-password=secret-pass --docker-email=user@domain.com -n secure-pulls`
  3. Write a deployment manifest `private-deployment.yaml` that references the `custom-registry-key` in its `imagePullSecrets` list.
  4. Apply the deployment manifest to the cluster.
  5. Confirm that the pod configurations are active and the secret was linked correctly:
     `kubectl get deployment private-service -n secure-pulls -o yaml | grep imagePullSecrets`

#### Lab 4: Testing Local Image Loading and Pull Policies
* **Objective:** Use Kind to load a local image to test container starting behaviors and different image pull policies.
* **Tasks:**
  1. Build or pull a test image locally on your machine, tag it as `local-test-app:v1.0`.
  2. Load the local image into your active Kind cluster:
     `kind load docker-image local-test-app:v1.0 --name lab-cluster`
  3. Write a pod manifest named `local-pod.yaml` that uses this image, and set `imagePullPolicy: IfNotPresent` (or `Never`) to ensure it runs without trying to download from a remote registry.
  4. Apply the manifest and verify that the pod runs successfully using the locally loaded image.
  5. Change the policy to `Always`, reapply, and verify that the container runtime fails to pull the image from the remote registry.

#### Lab 5: Tracking Helm Release History and Purging Releases
* **Objective:** Manage the lifecycle of deployed applications and clean up resources when they are no longer needed.
* **Tasks:**
  1. List all active releases across all namespaces in your cluster:
     `helm list -A`
  2. Run history commands to inspect a specific release's update history:
     `helm history lab-db -n database-dev`
  3. Uninstall the release:
     `helm uninstall lab-db -n database-dev`
  4. Verify that all associated Kubernetes pods, services, and secrets have been removed from the namespace:
     `kubectl get all -n database-dev`
"""

M4_INSIGHT = r"""### Interview Q&A
#### Q1: How does Helm track the history of its releases?
* **Answer:** Helm stores release metadata as standard Kubernetes Secrets (or ConfigMaps, depending on configuration) inside the namespace where the release is installed. Each time you deploy an upgrade, Helm creates a new Secret containing the full configuration layout of that specific revision, allowing it to track history and perform rollbacks.

#### Q2: What is the behavioral difference between `imagePullPolicy: Always` and `imagePullPolicy: IfNotPresent`?
* **Answer:** With `Always`, the container runtime queries the remote container registry on every pod startup or restart to check if the image has changed. If there is a new image digest, it downloads it. With `IfNotPresent`, the container runtime first checks the node's local cache. It only attempts to download the image from the remote registry if the image is missing locally, which helps save network bandwidth and speeds up container startup times.

#### Q3: How do we pass custom parameters to a Helm chart without writing a separate values file?
* **Answer:** You can pass custom parameters inline during installation or upgrade by using the `--set` flag on the command line. This allows you to override specific parameters directly from your terminal. For example: `helm install my-app bitnami/nginx --set service.port=8080,replicaCount=3`.

#### Q4: Why is it necessary to declare `imagePullSecrets` inside the Pod spec rather than referencing a generic Secret directly in the container?
* **Answer:** Downloading container images is handled directly by the container runtime on the host node, which runs outside the individual container environments. Therefore, the authentication secrets must be declared inside the Pod specification so the Kubernetes node agent (Kubelet) can read the credentials and authenticate with the registry before initializing the container.

#### Q5: How do you completely purge a Helm release, including its revision history?
* **Answer:** In Helm 3, running `helm uninstall <release-name>` automatically uninstalls the application and removes its entire revision history from the cluster by deleting all associated secrets.
"""

# ==========================================
# MODULE 5: METRICS & SYSTEM OBSERVABILITY
# ==========================================

M5_THEORY = r"""### Cluster Observability and Logs
Observing and monitoring running systems is essential for diagnosing issues in distributed clusters. In Kubernetes, container runtimes automatically redirect standard output (stdout) and standard error (stderr) streams to log files on the host node. The `kubectl logs` command queries these files to display the logs. When working with multi-container Pods (such as an application container running alongside a logging sidecar or proxy), you must specify the target container name using the `-c` flag to view logs for that specific container.

### Monitoring Infrastructure Metrics
The **Metrics Server** is a lightweight, cluster-wide collector of resource usage data. It collects CPU and memory utilization metrics directly from the container runtime on each worker node. This data can be queried using commands like `kubectl top` to monitor cluster utilization in real time, help identify resource leaks, and configure autoscaling policies.

### Managing Compute Resources
To ensure cluster stability and prevent resource contention, engineers must define resource parameters for their containers:
* **Requests**: The minimum amount of CPU and memory a container requires to run. The scheduler uses these values to decide which node has enough available capacity to host the Pod.
* **Limits**: The absolute maximum amount of CPU and memory a container is allowed to consume on a node. 

### Enforcing Resource Limits
When resource limits are reached, the host system handles CPU and memory differently:
* **CPU Throttling**: If a container attempts to use more CPU than its defined limit, the host kernel throttles (slows down) the container's CPU usage to keep it within the limit. The container continues to run, but its performance may degrade.
* **OOM Termination**: If a container attempts to use more memory than its limit, the host system's Out of Memory killer immediately terminates the container process. The container will exit with a status code of `137` and restart if managed by a controller.
"""

M5_COMMANDS = r"""### Command & Syntax Reference
Below are essential commands for inspecting logs, monitoring resource usage, and tracking cluster metrics.

* **Log Extraction & Analysis:**
  ```bash
  # Stream real-time log output from a container (similar to tail -f)
  kubectl logs -f app-server-pod -c main-container -n staging

  # View logs from a previously crashed container instance
  kubectl logs app-server-pod -c main-container --previous -n staging
  ```

* **Resource Usage Monitoring:**
  ```bash
  # View real-time CPU and memory usage for all nodes in the cluster
  kubectl top nodes

  # View resource usage for all pods in the active namespace
  kubectl top pods

  # View resource usage broken down by individual containers inside a pod
  kubectl top pod app-server-pod --containers -n staging
  ```
"""

M5_EXAMPLES = r"""### Real-World Examples
#### Example 1: Multi-Container Logs Extraction
**Situation:** A development team deployed a web application that runs an Nginx server alongside a fluentd logging sidecar container. They need to separate the web server's traffic logs from the sidecar's sync logs.
**Action:** Use specific container flags (`-c`) with log commands to isolate the log streams.

*Multi-Container Pod Manifest:*
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: web-and-log-pod
  namespace: default
spec:
  containers:
  - name: web-server
    image: nginx:1.25.3
    ports:
    - containerPort: 80
  - name: logging-agent
    image: alpine:3.18
    command: ["sh", "-c", "while true; do echo 'Sidecar log collection active...'; sleep 10; done"]
```

*Commands to query logs from each container:*
```bash
# Query the web-server container logs
kubectl logs web-and-log-pod -c web-server

# Query the logging-agent sidecar container logs
kubectl logs web-and-log-pod -c logging-agent
```

#### Example 2: Recovering Logs from a Crashed Container
**Situation:** An API container crashed on startup. Because the container has restarted, standard log commands only show the startup logs of the new container instance.
**Action:** Use the `--previous` flag to retrieve the error logs from the container instance that crashed.

```bash
# Query logs from the previous failed container run
kubectl logs backend-api-pod -c main-api --previous
```

#### Example 3: Auditing Cluster Resource Consumption
**Situation:** System administrators want to check which pods in a namespace are consuming the most memory to identify potential memory leaks.
**Action:** Run metrics commands to sort and view resource usage metrics.

```bash
# 1. Check resource consumption of all pods in the default namespace
kubectl top pods

# Output displays:
# NAME                     CPU(cores)   MEMORY(bytes)
# memory-intensive-pod     150m         412Mi
# standard-web-tier-xxxx   5m           24Mi

# 2. Inspect resource usage for individual containers inside a specific pod
kubectl top pod memory-intensive-pod --containers
```

#### Example 4: Configuring Container Resource Requests
**Situation:** A database service needs to guarantee it is scheduled on a worker node that has at least 512Mi of memory and 0.5 CPU cores dedicated to its execution.
**Action:** Define explicit CPU and memory resource requests in the container specification.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secured-db-pod
  namespace: default
spec:
  containers:
  - name: database
    image: postgres:15-alpine
    resources:
      requests:
        memory: "512Mi"
        cpu: "500m"
```

#### Example 5: Setting Resource Limits to Prevent Starvation
**Situation:** A batch process runs heavy data calculations and must be restricted to prevent it from consuming all CPU and memory on its host node, which could impact other services.
**Action:** Apply strict resource limits to the container specification in the deployment manifest.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: batch-processing-worker
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      app: batch-worker
  template:
    metadata:
      labels:
        app: batch-worker
    spec:
      containers:
      - name: processor
        image: alpine:3.18
        command: ["sh", "-c", "dd if=/dev/zero of=/dev/null"]
        resources:
          requests:
            memory: "64Mi"
            cpu: "100m"
          limits:
            memory: "128Mi"
            cpu: "500m"
```
"""

# ==========================================
# MODULE 5: LABS & INSIGHTS (SPLIT FOR PYTHON VALUE CONVERSION)
# ==========================================

M5_EXERCISE = r"""### Hands-On Labs
#### Lab 1: Monitoring Outputs from a Dual-Container Pod
* **Objective:** Deploy a multi-container pod and isolate log streams from each container.
* **Tasks:**
  1. Write a manifest named `dual-container.yaml` containing two containers: `nginx` and an alpine-based `sidecar-log` logging container.
  2. Deploy the pod to the cluster.
  3. Query the logs from the `nginx` container:
     `kubectl logs dual-container -c nginx`
  4. Query the logs from the `sidecar-log` container:
     `kubectl logs dual-container -c sidecar-log`
  5. Delete the pod.

#### Lab 2: Recovering Terminated Container Logs
* **Objective:** Inspect logs from a previously crashed container instance using diagnostic commands.
* **Tasks:**
  1. Write a pod manifest named `crashing-logger.yaml` with a start command that prints an error message and exits after 5 seconds:
     ```yaml
     apiVersion: v1
     kind: Pod
     metadata:
       name: crashing-logger
       namespace: default
     spec:
       containers:
       - name: logger-container
         image: alpine:3.18
         command: ["sh", "-c", "echo 'INITIALIZATION FAIL: Database connection refused!'; exit 1"]
     ```
  2. Apply the manifest and wait for the status to show restarts:
     `kubectl get pods -w`
  3. Retrieve the failure message logs from the previous crashed run:
     `kubectl logs crashing-logger -c logger-container --previous`
  4. Verify that the output displays the 'Database connection refused!' error message.
  5. Delete the crashing pod.

#### Lab 3: Tracking Cluster Metrics via Metrics-Server
* **Objective:** Verify and run metric reporting commands to monitor node and container resource usage.
* **Tasks:**
  1. Check if the Metrics Server is running in your cluster by querying its pods (typically running in the `kube-system` namespace):
     `kubectl get pods -n kube-system | grep metrics-server`
  2. Retrieve real-time CPU and memory usage statistics for all worker nodes:
     `kubectl top nodes`
  3. Run a CPU-intensive test pod in your cluster.
  4. Query resource usage at the pod level to monitor the test pod's consumption:
     `kubectl top pods`
  5. Identify the CPU and memory consumption of individual containers inside that pod.

#### Lab 4: Allocating Requests to Stabilize Scheduling
* **Objective:** Configure resource requests on a deployment to ensure proper node assignment.
* **Tasks:**
  1. Create a deployment manifest named `db-deployment.yaml` with 2 replicas.
  2. Define resource requests inside the container specification, requesting `200m` of CPU and `256Mi` of memory.
  3. Deploy the application to your cluster.
  4. Verify that the scheduler assigned the pods to nodes that have enough available capacity:
     `kubectl get pods -o wide`
  5. Review the allocated resource requests on your worker nodes using node description commands:
     `kubectl describe node <node-name>`

#### Lab 5: Setting Resource Limits and Simulating Memory Stress
* **Objective:** Set container resource limits and observe container behavior under memory pressure.
* **Tasks:**
  1. Write a pod manifest named `limited-pod.yaml` that sets a strict memory limit of `64Mi`:
     ```yaml
     apiVersion: v1
     kind: Pod
     metadata:
       name: limited-pod
       namespace: default
     spec:
       containers:
       - name: test-container
         image: alpine:3.18
         command: ["sh", "-c", "dd if=/dev/zero of=/dev/null bs=128M count=1"]
         resources:
           limits:
             memory: "64Mi"
           requests:
             memory: "32Mi"
     ```
  2. Apply the manifest and monitor the pod status as it initializes.
  3. Verify that the container is terminated with an OOMKilled state.
  4. Inspect the termination status details to confirm it exited with code `137`:
     `kubectl describe pod limited-pod`
  5. Delete the resource configurations.
"""

M5_INSIGHT = r"""### Interview Q&A
#### Q1: What is the difference between CPU requests and CPU limits?
* **Answer:** CPU requests define the minimum amount of CPU resources a container is guaranteed to have. The Kubernetes scheduler uses this value to determine which node has enough capacity to host the Pod. CPU limits define the absolute maximum amount of CPU resources a container is allowed to consume. If a container attempts to exceed its limit, the host kernel throttles its CPU usage but does not terminate the container.

#### Q2: How does Kubernetes handle memory limits exhaustion differently than CPU limits exhaustion?
* **Answer:** Memory and CPU are handled differently because CPU is a compressible resource, while memory is incompressible. If a container reaches its CPU limit, its CPU usage is throttled (slowed down), but the container continues to run. If a container reaches its memory limit and attempts to allocate more, the host system's Out of Memory (OOM) killer immediately terminates the container process with exit code `137` to protect node stability.

#### Q3: What is the function of the metrics-server in a Kubernetes cluster?
* **Answer:** The metrics-server is a cluster-wide aggregator of resource usage data. It collects CPU and memory metrics from each worker node's Kubelet agent (via the Summary API) and provides this data through the Kubernetes Metrics API. This metrics data is queried by commands like `kubectl top` and is used by controllers like the Horizontal Pod Autoscaler (HPA) to scale workloads.

#### Q4: How can we extract logs from a container that has crashed and exited?
* **Answer:** If a container has crashed and restarted, running standard log commands will only show logs from the current running instance. To view the logs from the instance that crashed, you must append the `--previous` flag to your log command: `kubectl logs <pod-name> -c <container-name> --previous`.

#### Q5: How does the Kubernetes scheduler use container Requests to make scheduling decisions?
* **Answer:** When a new Pod is created, the scheduler evaluates the sum of the resource requests defined for all containers inside that Pod. It then filters the available worker nodes and only schedules the Pod on a node that has enough allocatable CPU and memory capacity to satisfy those request values. The scheduler does not look at the node's active, real-time resource usage, but rather the total sum of requests already allocated to existing pods on that node.
"""

# ==========================================
# CURRICULUM DATA BINDINGS
# ==========================================

CURRICULUM_DATA = [
    {
        "id": 1,
        "title": "Module 1: Kubernetes Core Workloads & Stateful Configuration",
        "theory": M1_THEORY,
        "commands": M1_COMMANDS,
        "examples": M1_EXAMPLES,
        "exercise": M1_EXERCISE,
        "insight": M1_INSIGHT,
    },
    {
        "id": 2,
        "title": "Module 2: In-Cluster Networking & Service Discovery",
        "theory": M2_THEORY,
        "commands": M2_COMMANDS,
        "examples": M2_EXAMPLES,
        "exercise": M2_EXERCISE,
        "insight": M2_INSIGHT,
    },
    {
        "id": 3,
        "title": "Module 3: Local Workflows & Container Diagnostics",
        "theory": M3_THEORY,
        "commands": M3_COMMANDS,
        "examples": M3_EXAMPLES,
        "exercise": M3_EXERCISE,
        "insight": M3_INSIGHT,
    },
    {
        "id": 4,
        "title": "Module 4: Application Packaging & Registry Access with Helm",
        "theory": M4_THEORY,
        "commands": M4_COMMANDS,
        "examples": M4_EXAMPLES,
        "exercise": M4_EXERCISE,
        "insight": M4_INSIGHT,
    },
    {
        "id": 5,
        "title": "Module 5: Metrics & Container Observability",
        "theory": M5_THEORY,
        "commands": M5_COMMANDS,
        "examples": M5_EXAMPLES,
        "exercise": M5_EXERCISE,
        "insight": M5_INSIGHT,
    },
]