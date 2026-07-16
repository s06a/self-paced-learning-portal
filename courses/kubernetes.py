# Kubernetes Course Definition
COURSE_ID = "kubernetes"
COURSE_TITLE = "Kubernetes Administrator (CKA) (Not Completed)"
COURSE_DESCRIPTION = "Explore production container orchestration, declarative microservices deployments, service discovery networks, and ingress traffic controllers."

CURRICULUM_DATA = [
    {
        "id": 1,
        "title": "Module 1: Kubernetes Core Architecture & Declarative Primitives",
        "theory": """
### The Kubernetes Paradigm
Kubernetes (K8s) is an open-source container orchestration engine designed to automate deployment, scaling, and management of containerized workloads. Unlike standalone Docker engines, Kubernetes manages clusters of physical or virtual machines, abstracting individual hardware nodes into a single, cohesive processing unit.

### Control Plane vs. Worker Nodes
Kubernetes splits its physical topology into two major roles:
1. **Control Plane Components:**
   - **kube-apiserver:** The administrative gateway of the cluster. Every action (imperative or declarative) passes through the API server via REST calls.
   - **etcd:** The highly available, consistent key-value store serving as Kubernetes' single source of truth for cluster state metrics.
   - **kube-scheduler:** Watches for newly created Pods with no assigned node, selecting the optimal node for execution based on physical resource requirements and policies.
   - **kube-controller-manager:** Runs the primary daemon controller reconciliation loops (Node Controller, Deployment Controller, Job Controller).
2. **Worker Node Components:**
   - **kubelet:** An active agent that runs on each node in the cluster, ensuring containers are running within their declared Pod structures.
   - **kube-proxy:** A network proxy managing local host TCP/UDP packet forwarding rules to enable internal service discovery.
   - **Container Runtime (e.g., containerd):** The low-level execution engine responsible for starting and stopping container environments.
        """,
        "commands": """
### Command Reference

To manipulate cluster states, query workloads, and inspect running pods, learn these essential commands:

* `kubectl run [NAME] --image=[IMAGE]`  
  Spins up an ephemeral, standalone Pod.  
* `kubectl get [resource_type]`  
  Lists active structures in your current context namespace.  
  - `-o wide`: Shows enhanced details including host IP and target nodes.  
* `kubectl describe [resource_type] [NAME]`  
  Queries extensive low-level metadata, event details, and state transitions.  
* `kubectl apply -f [FILE_PATH]`  
  Applies declarative configurations stored in local YAML or JSON files.  
* `kubectl delete [resource_type] [NAME]`  
  Tears down resources and cleans associated dependencies.
        """,
        "examples": """
### Real-World Examples

#### Example 1: Constructing a Multi-Container Pod (Sidecar Pattern)
* **Situation:** A web server pod needs a helper agent to dynamically pull logs and stream them to an external aggregator.
* **Action:** Declare two containers inside a single Pod configuration mapping a shared directory volume:
  ```yaml
  apiVersion: v1
  kind: Pod
  metadata:
    name: web-sidecar-pod
  spec:
    volumes:
    - name: shared-logs
      emptyDir: {}
    containers:
    - name: web-server
      image: nginx:alpine
      volumeMounts:
      - name: shared-logs
        mountPath: /var/log/nginx
    - name: sidecar-agent
      image: alpine
      command: ["/bin/sh", "-c", "tail -f /logs/access.log"]
      volumeMounts:
      - name: shared-logs
        mountPath: /logs
  ```

#### Example 2: Creating a Declarative ReplicaSet Deployment
* **Situation:** You need to ensure three identical instances of your API run continuously, auto-healing in case of node failures.
* **Action:** Apply a Deployment manifest detailing the desired replicas count:
  ```yaml
  apiVersion: apps/v1
  kind: Deployment
  metadata:
    name: api-deployment
  spec:
    replicas: 3
    selector:
      matchLabels:
        app: fast-api
    template:
      metadata:
        labels:
          app: fast-api
      spec:
        containers:
        - name: app
          image: python:3.9-slim
  ```
        """,
        "exercise": """
### Hands-On Labs

#### Lab 1: Deploying a Multi-Replica Web Service
* **Objective:** Deploy an Nginx deployment across your cluster and monitor the scaling phase.
* **Tasks:**
  1. Write a deployment YAML configuration specifying 4 replicas of Nginx.
  2. Apply the deployment configuration using `kubectl apply -f`.
  3. Inspect node placement details using `kubectl get pods -o wide`.

#### Lab 2: Scaling Deployments Dynamically
* **Objective:** Scale up an active deployment imperatively and observe the pod scheduling lifecycle.
* **Tasks:**
  1. Execute `kubectl scale deployment api-deployment --replicas=6`.
  2. Run `kubectl get pods` immediately and watch container states transition from `ContainerCreating` to `Running`.
        """,
        "insight": """
### Interview Q&A

#### Q1: What is the main structural difference between a Pod and a Container?
* **Answer:** A Container is an isolated, single runtime process. A Pod is the smallest deployable unit in Kubernetes, serving as an execution wrapper that can house one or more tightly coupled containers. All containers inside a single Pod share the same network namespace, IP address, port space, and storage volumes.

#### Q2: How does the Control Plane recover when an active worker node crashes?
* **Answer:** The `kube-controller-manager` detects that the node is unreachable. If the node stays offline beyond the eviction timeout, the controller manager flags the affected pods as dead and instructs the `kube-scheduler` to reschedule replacement pods onto remaining healthy worker nodes.

### CKA Exam Focus
Be prepared to write clean Pod and Deployment specs manually. Understand how to query the API server using JSONPath selectors (`kubectl get pods -o jsonpath='{.items[*].metadata.name}'`).
        """
    },
    {
        "id": 2,
        "title": "Module 2: Services, Ingress, & Cluster Networking",
        "theory": """
### Kubernetes Networking Architecture
Kubernetes enforces a strict flat networking model: every Pod gets its own unique, routable IP address within the cluster, and Pods can communicate with other Pods on any node without NAT.

### Service Abstractions
Since Pods are ephemeral and their IP addresses change on recreation, Kubernetes introduces **Services** to act as reliable entrypoints with stable IPs:
- **ClusterIP (default):** Exposes the service on a private IP internal to the cluster.
- **NodePort:** Exposes the service on each node's IP at a static port (usually between `30000-32767`).
- **LoadBalancer:** Provisions an external load balancer in supported cloud environments, routing traffic to NodePort and ClusterIP.

### Ingress Controllers
While Services route layer-4 traffic, **Ingress** manages layer-7 (HTTP/HTTPS) routing. It uses defined host rules and path configurations to act as an entrypoint reverse proxy.
        """,
        "commands": """
### Command Reference

To manage, expose, and debug networking interfaces, learn the following commands:

* `kubectl expose deployment [NAME] --port=[PORT] --target-port=[TARGET]`  
  Automatically creates a ClusterIP service for your deployment workloads.  
* `kubectl get svc`  
  Lists all active services and their allocated virtual Cluster IPs.  
* `kubectl get ingress`  
  Displays active Ingress configurations and external routing controllers.  
* `kubectl port-forward [POD_NAME] [LOCAL_PORT]:[REMOTE_PORT]`  
  Bypasses service topologies to map a local terminal port directly to a running Pod for debugging.
        """,
        "examples": """
### Real-World Examples

#### Example 1: Exposing a Web Application via NodePort
* **Situation:** You need to expose your internal Nginx deployment to developers outside the local cluster network.
* **Action:** Construct a NodePort service mapping traffic to your application's target port:
  ```yaml
  apiVersion: v1
  kind: Service
  metadata:
    name: web-nodeport-svc
  spec:
    type: NodePort
    selector:
      app: web-server
    ports:
    - port: 80
      targetPort: 80
      nodePort: 32080
  ```

#### Example 2: Structuring Ingress Rules for Path-Based Routing
* **Situation:** You want a single entrypoint URL to route `/api` to the backend service and `/` to your frontend.
* **Action:** Declare an Ingress resource defining path-based rules:
  ```yaml
  apiVersion: networking.k8s.io/v1
  kind: Ingress
  metadata:
    name: main-ingress
  spec:
    rules:
    - host: academy.local
      http:
        paths:
        - path: /api
          pathType: Prefix
          backend:
            service:
              name: backend-svc
              port:
                number: 8080
        - path: /
          pathType: Prefix
          backend:
            service:
              name: frontend-svc
              port:
                number: 80
  ```
        """,
        "exercise": """
### Hands-On Labs

#### Lab 1: Exposing Services Internally
* **Objective:** Verify DNS-based service discovery between isolated Pods in a ClusterIP namespace.
* **Tasks:**
  1. Create a simple backend deployment and expose it via ClusterIP.
  2. Launch an ephemeral alpine container running `wget` or `curl`.
  3. Request the backend service using its DNS name (e.g., `http://backend-svc`) and inspect the output.

#### Lab 2: Debugging Network Endpoints
* **Objective:** Trace endpoints mapping to verify services are correctly connected to backend pods.
* **Tasks:**
  1. Expose an Nginx deployment.
  2. Query mapped targets using `kubectl get endpoints`.
  3. Scale down the deployment to 0 and verify the endpoints list updates to empty.
        """,
        "insight": """
### Interview Q&A

#### Q1: What is the exact difference between targetPort, port, and nodePort?
* **Answer:** 
  - `targetPort` is the port your containerized application listens on inside the pod.
  - `port` is the internal cluster port allocated by the virtual Service ClusterIP.
  - `nodePort` is the port opened on all physical cluster nodes to receive external traffic.

#### Q2: How does kube-proxy handle ClusterIP routing under the hood?
* **Answer:** `kube-proxy` does not run as a routing proxy for actual packet paths. Instead, it runs on each node and writes standard Linux IPtables or IPVS rules. When a client attempts to connect to a ClusterIP, the host kernel intercept rules instantly translate the destination IP (DNAT) to one of the healthy pod IPs.

### CKA Exam Focus
Understand CoreDNS behaviors. Know that services are registered with automatic DNS entries following the format: `[service-name].[namespace].svc.cluster.local`.
        """
    }
]
