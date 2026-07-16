# Docker Course Definition
COURSE_ID = "docker"
COURSE_TITLE = "Docker Certified Associate (DCA)"
COURSE_DESCRIPTION = "Master core container primitives, high-performance Dockerfiles, persistent storage volumes, overlay networks, and Docker Swarm orchestration."

CURRICULUM_DATA = [
    {
        "id": 1,
        "title": "Module 1: Foundational Containerization & Architecture",
        "theory": """
### The Containerization Paradigm
Virtual Machines (VMs) rely on a hypervisor to slice physical hardware into isolated guest operating systems, each carrying its own kernel, system libraries, and substantial overhead. In contrast, **Containers share the host operating system's kernel** and isolate processes at the user-space level, rendering them lightweight, fast to boot, and highly resource-efficient.

### Linux Kernel Primitives (Under the Hood)
Docker is built on fundamental Linux kernel features:
1. **Namespaces:** Provide boundary isolation.
   - **PID:** Isolates process IDs (container processes cannot see host processes).
   - **NET:** Isolates network interfaces, routing tables, and port spaces.
   - **MNT:** Isolates filesystem mount points.
   - **IPC:** Isolates System V IPC and POSIX message queues.
   - **UTS:** Isolates hostname and domain name.
   - **USER:** Maps container UID/GIDs to host UID/GIDs for security boundaries.
2. **Control Groups (cgroups):** Enforce physical resource constraints (CPU, memory, disk I/O, network bandwidth).
3. **Union File System (UnionFS):** Enables layering by merging multiple directories into a single unified filesystem. It relies on **Copy-on-Write (CoW)**, copying files to the top writable layer only when write modifications are executed.

### Docker Engine Architecture
The modern Docker Engine conforms to the Open Container Initiative (OCI) specification:
* **Docker Client:** Parses commands and communicates via REST API with the Docker daemon.
* **Docker Daemon (dockerd):** Manages high-level objects like networks, volumes, and images.
* **containerd:** A CNCF-graduated container runtime managing the execution lifecycle.
* **runC:** The low-level execution tool that directly interacts with kernel namespaces and cgroups to instantiate containers.
        """,
        "commands": """
### Command Reference

To manipulate containers, inspect system layers, and manage the local daemon lifecycle, learn the following primary commands:

* `docker run [OPTIONS] IMAGE [COMMAND] [ARG...]`  
  Creates and starts a container from a target image.  
  - `-d`: Run container in background (detached mode) and print container ID.  
  - `-it`: Allocate a pseudo-TTY and keep stdin open (interactive shell access).  
  - `--name`: Assign a custom name to the container.  
  - `-p host_port:container_port`: Publish a container's port(s) to the host.  
* `docker ps [OPTIONS]`  
  Lists active containers.  
  - `-a`: Show all containers (default shows just running).  
  - `-q`: Only display numeric container IDs.  
* `docker exec [OPTIONS] CONTAINER COMMAND [ARG...]`  
  Runs a new command inside an actively running container.  
  - `-it`: Standard interactive access parameter combination.  
* `docker inspect [OPTIONS] NAME|ID [NAME|ID...]`  
  Return low-level information on Docker objects in structured JSON format.  
* `docker system info`  
  Display system-wide information regarding your host system's Docker installation.
        """,
        "examples": """
### Real-World Examples

#### Example 1: Inspecting Containerized Process Tables on the Host
* **Situation:** You need to verify that container processes are running directly on the host kernel under isolated namespaces.
* **Action:** Start a detached Nginx container, view its internals, and find its parent process ID on the host using native Linux tools:
  ```bash
  docker run -d --name test-process-nginx -p 8080:80 nginx:alpine
  docker exec test-process-nginx ps aux
  ps aux | grep "nginx: master process"
  ```

#### Example 2: Interacting Directly with the Docker Engine Socket
* **Situation:** You need to debug or verify daemon health when the standard Docker CLI client is corrupted or uninstalled.
* **Action:** Communicate directly with the system daemon using `curl` via the default UNIX socket file:
  ```bash
  sudo curl --unix-socket /var/run/docker.sock http://localhost/v1.41/containers/json
  ```

#### Example 3: Verifying Control Group Memory Constraints
* **Situation:** A container is consuming excessive RAM. You must force memory limit rules on the runtime and verify cgroup configuration.
* **Action:** Launch an Alpine container with memory constraints, then read the cgroup interface values on the host filesystem:
  ```bash
  docker run -d --name mem-limited --memory="50m" alpine sleep 3000
  docker inspect mem-limited | grep -i memory
  # Check system cgroups directory directly (for cgroups v1)
  cat /sys/fs/cgroup/memory/docker/<long_container_id>/memory.limit_in_bytes
  ```

#### Example 4: Accessing Shell Terminal of Container without SSH
* **Situation:** You must troubleshoot configuration logs inside an active database container dynamically.
* **Action:** Use the `exec` command to spawn an interactive shell terminal securely within the container's namespaces:
  ```bash
  docker exec -it my-database /bin/sh
  ```

#### Example 5: Cleaning up Stopped Container Resources
* **Situation:** The local development host is running low on disk space due to accumulated dead container states.
* **Action:** Filter, list, and purge stopped container resources using clean CLI tools:
  ```bash
  # Find stopped containers
  docker ps -a -f status=exited
  # Prune stopped containers
  docker container prune -f
  ```
        """,
        "exercise": """
### Hands-On Labs

#### Lab 1: Bypassing the CLI to Fetch Metadata
* **Objective:** Pull an Nginx image and start a container strictly using low-level engine calls via `curl`.
* **Tasks:**
  1. Pull the image:
     ```bash
     sudo curl --unix-socket /var/run/docker.sock -X POST "http://localhost/v1.41/images/create?fromImage=nginx&tag=alpine"
     ```
  2. Verify the image download using `docker images`.

#### Lab 2: Mapping a Detached Web Workspace
* **Objective:** Start a detached container and retrieve its active log stream without maintaining an active terminal session.
* **Tasks:**
  1. Run Nginx in detached mode mapping host port `8081` to container port `80`.
  2. Retrieve logs using `docker logs -f [container-name]`.
  3. Query `http://localhost:8081` in a separate terminal and watch logs stream.

#### Lab 3: Memory Constraint Verification
* **Objective:** Run a container limited to 100MB of RAM and intentionally trigger an out-of-memory crash.
* **Tasks:**
  1. Start a memory-constrained container: `--memory="100m"`.
  2. Use a benchmark utility inside the container to allocate 150MB of RAM.
  3. Check the exit status of the container to verify it was killed by the OOM engine.

#### Lab 4: User Namespace Isolation
* **Objective:** Inspect UID maps inside a running container to verify user isolation.
* **Tasks:**
  1. Run a container mapping host users to container users.
  2. Run `docker exec [name] id` and verify the process UID inside the container namespaces.
  3. Verify that the process maps to an unprivileged user on the host system.

#### Lab 5: System Resource Diagnostics
* **Objective:** Collect global engine status details to inspect host kernel and namespace features.
* **Tasks:**
  1. Run `docker system info`.
  2. Check the output for kernel version, container runtimes, and active security profiles.
        """,
        "insight": """
### Interview Q&A

#### Q1: If a container runs as root inside its namespace, does it have root privileges on the host? Explain how you would mitigate this risk using kernel-level features.
* **Answer:** Yes, by default, UID 0 (root) inside a container maps directly to UID 0 (root) on the host. If a process escapes the container boundary, it inherits full root capabilities on the host. To mitigate this, enable **User Namespace Remapping** (`userns-remap` in `/etc/docker/daemon.json`), which maps the container's UID 0 to an unprivileged high-range UID on the host.

#### Q2: What is the exact difference between containerd and runC in the runtime lifecycle?
* **Answer:** `containerd` is a high-level container runtime that manages the complete container lifecycle (fetching images, monitoring resource allocations, managing networks). `runC` is a low-level OCI-compliant execution engine that interacts directly with the Linux kernel to configure namespaces/cgroups and spin up the container process, exiting immediately after initialization.

#### Q3: How do Linux cgroups differ from Namespaces?
* **Answer:** Namespaces provide **isolation** (restricting what a process can see, such as other processes, network adapters, or filesystems). Control groups (cgroups) provide **resource limitation** (governing what a process can consume, such as CPU, RAM, or disk I/O).

#### Q4: What is the Copy-on-Write (CoW) mechanism in UnionFS?
* **Answer:** CoW is an optimization strategy where system files inside read-only layers are shared. When a container attempts to modify a file, UnionFS copies the file from the lower read-only layers up to the container's top writable layer before applying modifications, saving storage space and memory.

#### Q5: How do you identify a container's physical parent process on the host?
* **Answer:** Retrieve the container's State PID using `docker inspect --format '{{.State.Pid}}' [container_id]`. Then, run `ps -ef | grep [PID]` on the host to inspect the parent-child relationship of the processes.

### DCA Exam Focus
Understand the exact hierarchy: **Docker CLI -> dockerd -> containerd -> containerd-shim -> runC**. Know that runC exits after starting the container, leaving containerd-shim to manage process lifecycle.
        """
    },
    {
        "id": 2,
        "title": "Module 2: High-Performance Dockerfile Design & Image Optimization",
        "theory": """
### The Layered File System
A Docker image is a read-only stack of layers, with each `Dockerfile` instruction representing a new layer. At execution, Docker mounts a thin, temporary **writable layer** on top of the stack.

### Shell Form vs. Exec Form
* **Shell Form (`CMD echo "Hello"`)**: Executes the command inside `/bin/sh -c`. The application runs as a subprocess, meaning it will not receive operating system signals like `SIGTERM` (it won't run as PID 1).
* **Exec Form (`CMD ["echo", "Hello"]`)**: Invokes the executable directly without a shell wrapper. This ensures the application runs as PID 1, allowing for graceful termination of processes.

### Build Context & Multi-Stage Builds
* **Build Context:** The directory passed to `docker build`. Every file in this path (unless specified in `.dockerignore`) is sent to the Docker daemon, slowing down builds.
* **Multi-Stage Builds:** Allow you to use multiple `FROM` instructions in a single Dockerfile. You can compile your software in a heavy development stage and then copy only the compiled binaries into a secure, minimal runtime stage (such as `distroless` or `alpine`), excluding build tooling.
        """,
        "commands": """
### Command Reference

To build, tag, prune, and verify the caching metrics of custom container images, master the following commands:

* `docker build [OPTIONS] PATH | URL | -`  
  Build an image from a Dockerfile.  
  - `-t name:tag`: Tag the built image with a specific repository name and version tag.  
  - `-f file`: Use a custom Dockerfile path name instead of the default `Dockerfile`.  
  - `--no-cache`: Do not use cache when building the image.  
  - `--build-arg key=value`: Set build-time variables.  
* `docker images`  
  List all locally downloaded and compiled images.  
* `docker rmi [OPTIONS] IMAGE [IMAGE...]`  
  Remove one or more images from the host system cache.  
* `docker history [OPTIONS] IMAGE`  
  Show the build layer history and intermediate instruction execution trace of an image.
        """,
        "examples": """
### Real-World Examples

#### Example 1: Isolating Package Managers to Optimize Build Caching
* **Situation:** Your Node.js build reinstalls dependencies every time you modify an application code file, slowing pipelines.
* **Dockerfile Resolution:**
  ```dockerfile
  FROM node:18-alpine
  WORKDIR /app
  # Copy package manifest first to create a dedicated cached layer
  COPY package*.json ./
  RUN npm ci
  # Copy application source code subsequently
  COPY . .
  CMD ["node", "app.js"]
  ```

#### Example 2: Multi-Stage Build Compilations (Go Binary Build)
* **Situation:** You want to deploy a lightweight Go application without bundling the full Go compiler and build dependencies in the production image.
* **Dockerfile Resolution:**
  ```dockerfile
  # Stage 1: Build compilation tools
  FROM golang:1.20-alpine AS builder
  WORKDIR /src
  COPY . .
  RUN CGO_ENABLED=0 GOOS=linux go build -o myapp .

  # Stage 2: Clean runtime target
  FROM scratch
  WORKDIR /app
  COPY --from=builder /src/myapp .
  EXPOSE 8080
  ENTRYPOINT ["/app/myapp"]
  ```

#### Example 3: Running with Dynamic Build Arguments
* **Situation:** You need to bake version-specific tags into your image layers during automated builds without hardcoding them.
* **Dockerfile Resolution:**
  ```dockerfile
  FROM alpine:latest
  ARG APP_VERSION=1.0.0
  ENV APP_VERSION=${APP_VERSION}
  RUN echo "Building version: ${APP_VERSION}" > /etc/app_version.txt
  CMD ["cat", "/etc/app_version.txt"]
  ```
  Build command:
  ```bash
  docker build --build-arg APP_VERSION=2.4.1 -t myapp:2.4.1 .
  ```

#### Example 4: Troubleshooting Layer Blowup with Intermediate Layers
* **Situation:** Your Dockerfile executes commands on separate lines, causing the final image size to swell because temporary files are cached in intermediate layers.
* **Dockerfile Resolution:** Chain execution commands and clean up package managers in a single `RUN` layer:
  ```dockerfile
  FROM ubuntu:22.04
  RUN apt-get update && apt-get install -y \
      curl \
      git \
      && apt-get clean && rm -rf /var/lib/apt/lists/*
  ```

#### Example 5: Implementing a Non-Root System User
* **Situation:** To run securely, you need to ensure your application process cannot access root capabilities inside the container namespace.
* **Dockerfile Resolution:** Configure a system group and user, then switch the execution context:
  ```dockerfile
  FROM alpine:latest
  RUN addgroup -S appgroup && adduser -S appuser -G appgroup
  WORKDIR /home/appuser
  USER appuser
  CMD ["whoami"]
  ```
        """,
        "exercise": """
### Hands-On Labs

#### Lab 1: The Monolith Slimdown Challenge
* **Objective:** Refactor a bloated static asset build and convert it into a minimal Alpine build.
* **Tasks:**
  1. Analyze a provided monolithic build file.
  2. Implement a `.dockerignore` file containing local dependency folders.
  3. Divide build execution steps into a compiled stage and a minimal runner stage.
  4. Build and verify the size reduction using `docker images`.

#### Lab 2: Implementing Signal-Aware Entrypoints
* **Objective:** Configure an CMD to use the Exec form to ensure the containerised application handles OS signals correctly.
* **Tasks:**
  1. Write a Dockerfile with a simple bash execution script.
  2. Run the application using the Shell form: `CMD my-script.sh`.
  3. Verify that running `docker stop` on this container takes 10 seconds before force-killing it.
  4. Refactor the instruction to the Exec form: `ENTRYPOINT ["/bin/sh", "my-script.sh"]` and verify it stops instantly.

#### Lab 3: Dynamic Build Parameter Auditing
* **Objective:** Use build arguments to configure an application build for different environments.
* **Tasks:**
  1. Author a Dockerfile that exposes an `ARG STAGE=dev` environment identifier.
  2. Clean the image with `docker build --build-arg STAGE=production -t app:prod .`.
  3. Instantiate the image and verify the variable configuration inside the running container.

#### Lab 4: Build History Layer Audit
* **Objective:** Inspect an image's layers to identify which commands contribute most to its final size.
* **Tasks:**
  1. Build any simple image using a multi-step Dockerfile.
  2. Run `docker history [image-name]` to view the layer sizes.
  3. Identify the largest layer and combine commands inside the Dockerfile to optimize it.

#### Lab 5: Build Context Optimization
* **Objective:** Configure `.dockerignore` to prevent large unused files from being sent to the Docker daemon.
* **Tasks:**
  1. Create a large dummy file (`large.tmp`) in your build directory.
  2. Execute a build and observe the build context size in the terminal output.
  3. Add `large.tmp` to `.dockerignore` and verify the build context size decreases.
        """,
        "insight": """
### Interview Q&A

#### Q1: Explain why using `npm install` before copying your application source code is beneficial for Docker's build cache. What happens if you modify a line of code in your source file?
* **Answer:** Docker caches build steps layer-by-layer. If any layer is invalidated, all subsequent steps are rebuilt. By isolating dependencies (`COPY package.json` and `RUN npm install`) prior to copying the code (`COPY . .`), Docker can reuse the cached dependency layer as long as the package list has not changed, vastly accelerating daily builds.

#### Q2: What is the difference between CMD and ENTRYPOINT instructions?
* **Answer:** `ENTRYPOINT` defines the executable that runs when the container starts and is not easily overridden. `CMD` provides default arguments passed to the `ENTRYPOINT`, which can be overridden by passing arguments at the command line.

#### Q3: Why is the shell form of CMD considered bad practice for PID 1 processes?
* **Answer:** The shell form wraps your command in `/bin/sh -c`. This makes the shell run as PID 1, and your application run as a subprocess. Since shells do not forward OS signals (like `SIGTERM`), your application will not terminate gracefully.

#### Q4: How does COPY differ from ADD?
* **Answer:** `COPY` simply copies local files from the host build context into the container. `ADD` can do this as well, but it also supports downloading files from remote URLs and automatically unpacking compressed tar archives into the target directory.

#### Q5: How does multi-stage builds improve security?
* **Answer:** Multi-stage builds separate the compile-time dependencies (compilers, debuggers, source code) from the runtime environment. By copying only the compiled binary into a minimal production image, you minimize the attack surface of the container.

### DCA Exam Focus
Understand how caching behaves with `COPY` and `ADD`. Note that `COPY` and `ADD` evaluate file content checksums, not modification times, to determine cache hits.
        """
    },
    {
        "id": 3,
        "title": "Module 3: Advanced Storage Mechanics & Data Persistence",
        "theory": """
### Storage Drivers
Docker uses pluggable storage drivers (e.g., `overlay2`, `btrfs`, `zfs`) to manage the layered filesystem of images and containers. `overlay2` is the modern default for Linux systems, separating storage into lower (read-only) and upper (read-write) directories.

### Data Mount Types
1. **Volumes:** Managed entirely by the Docker engine on the host filesystem (`/var/lib/docker/volumes/`). Highly recommended for production database engines as they bypass container storage layer overhead.
2. **Bind Mounts:** Maps an arbitrary directory or file on the host machine to a directory or file in the container. Highly dependent on host directory layouts.
3. **tmpfs Mounts:** Mounts data directly into host memory (RAM). Data never touches the host disk and is discarded on container stop. Extremely secure for transient credentials or sessions.
        """,
        "commands": """
### Command Reference

To persist files outside the container lifecycle and manage storage endpoints, master these commands:

* `docker volume create [OPTIONS] [VOLUME]`  
  Create a named storage partition managed by Docker.  
* `docker volume ls`  
  List all active named volumes on the host system.  
* `docker volume inspect [OPTIONS] VOLUME [VOLUME...]`  
  Display detailed volume metadata, including the absolute mountpath location on the host.  
* `docker volume rm [OPTIONS] VOLUME [VOLUME...]`  
  Remove one or more named volumes. (Fails if any volume is still attached to a container).  
* `docker run -v [volume_name]:[container_path]` or `--mount type=volume,source=[vol],target=[path]`  
  Mount directories during container instantiation.
        """,
        "examples": """
### Real-World Examples

#### Example 1: Creating Named Persistent Storage for Database Integrity
* **Situation:** A database container must persist files across rebuilds or configuration changes.
* **Action:** Create a dedicated docker volume, then map it to the database's default storage directory:
  ```bash
  docker volume create pg_prod_data
  docker run -d --name db-postgres -v pg_prod_data:/var/lib/postgresql/data -e POSTGRES_PASSWORD=securepass postgres:15-alpine
  ```

#### Example 2: Mounting Host Configurations Read-Only
* **Situation:** A web server needs to read configuration files on the host, but you want to prevent the containerized process from mutating these files.
* **Action:** Use explicit `--mount` options with the `readonly` flag enabled:
  ```bash
  docker run -d --name readonly-nginx --mount type=bind,source=/etc/nginx/nginx.conf,target=/etc/nginx/nginx.conf,readonly -p 80:80 nginx:alpine
  ```

#### Example 3: Troubleshooting Permission Mismatches with Host Bind Mounts
* **Situation:** You bind-mount a host path owned by root into a container running as a non-root user (UID 1001), resulting in "Permission Denied" errors.
* **Action:** Adjust ownership on the host filesystem before executing the mount with matching user permissions:
  ```bash
  sudo chown -R 1001:1001 /home/user/app/data
  docker run -d -v /home/user/app/data:/app/data --user 1001:1001 myapp:latest
  ```

#### Example 4: Utilizing In-Memory Mounting for Transient Keys
* **Situation:** You need to pass sensitive private SSH keys into a batch processing agent without writing them to disk.
* **Action:** Mount the key target path using an in-memory `tmpfs` volume:
  ```bash
  docker run -d --name key-handler --mount type=tmpfs,destination=/root/.ssh,tmpfs-mode=1770 my-agent:latest
  ```

#### Example 5: Backing up Container Storage via Sidecar Containers
* **Situation:** You need to back up files stored inside a named volume to the host system as a compressed archive.
* **Action:** Spawn a temporary sidecar container to mount the target volume and back it up:
  ```bash
  docker run --rm -v pg_prod_data:/volume -v /tmp:/backup alpine tar cvf /backup/db_backup.tar /volume
  ```
        """,
        "exercise": """
### Hands-On Labs

#### Lab 1: Stateful Application Migration Lab
* **Objective:** Verify data persists across the destruction and reconstruction of a database container.
* **Tasks:**
  1. Create a named volume `state_vol`.
  2. Launch a PostgreSQL instance utilizing `state_vol` for storage.
  3. Write a test table and record to the database, then delete the container.
  4. Launch a new PostgreSQL container mounting `state_vol` and verify the data is intact.

#### Lab 2: Mapping a Dynamic Read-Only Config Backplane
* **Objective:** Configure an application container to receive configuration files from the host while preventing modifications to those files.
* **Tasks:**
  1. Write a simple text configuration file on your host filesystem.
  2. Mount the config file into an Alpine container using `--mount type=bind,...,readonly`.
  3. Attempt to modify or write to the mounted file from inside the container and verify that the write operation fails.

#### Lab 3: Volume Cleanup and Orphan Recovery
* **Objective:** Identify and clean up orphaned volumes that are consuming disk space on the host.
* **Tasks:**
  1. Create several temporary containers that use anonymous volumes.
  2. Remove the containers while omitting the `-v` flag to leave the volumes orphaned on the host.
  3. Find and inspect these dangling volumes using `docker volume ls -f dangling=true`.
  4. Safely purge all unused volumes using `docker volume prune -f`.

#### Lab 4: Dynamic Storage Driver Auditing
* **Objective:** Determine the active storage driver configured on your Docker host.
* **Tasks:**
  1. Run `docker info`.
  2. Locate the "Storage Driver" line in the output and write down the driver name (e.g., `overlay2`).
  3. Locate the physical path where Docker stores container filesystem layers on the host (usually `/var/lib/docker/overlay2`).

#### Lab 5: Host File Modification Tracking
* **Objective:** Verify that modifications to a host file are immediately reflected inside a container using a bind mount.
* **Tasks:**
  1. Create a file `host_file.txt` on the host.
  2. Mount it inside an Alpine container using a bind mount.
  3. Modify the file on the host, then cat the file inside the container to verify the changes synchronized.
        """,
        "insight": """
### Interview Q&A

#### Q1: When mounting a host directory into a container via a bind mount, how do you handle file permission issues when the container processes run as a non-root user (e.g., UID 1000) but the host directory is owned by root?
* **Answer:** To avoid write permission failures, ensure the host directory has ownership permissions mapped to match the container's execution user ID, or pass the `--user` flag at run-time (e.g., `--user 1000:1000`) to force the container process execution to conform to host permissions.

#### Q2: What is the main structural difference between volumes and bind mounts?
* **Answer:** Volumes are created and managed directly by the Docker engine, stored in a private directory layout on the host (`/var/lib/docker/volumes/`). Bind mounts map any arbitrary path on the host system to the container, making them dependent on the host directory structures.

#### Q3: In what scenario is a tmpfs mount highly recommended over standard storage options?
* **Answer:** A `tmpfs` mount is recommended for securing highly sensitive, transient files (such as certificates or dynamic SSH keys) that should not be written to the host filesystem. Since it runs in-memory, the data disappears immediately when the container is stopped.

#### Q4: Why is running database workloads directly on a container's layered filesystem bad practice?
* **Answer:** Writing data to the container's writable layer involves storage driver overhead (such as copy-on-write latency), slowing performance. Furthermore, container layered filesystems are ephemeral; deleting the container immediately destroys the database files.

#### Q5: How do you configure a container to share volumes with another container?
* **Answer:** Use the `--volumes-from` flag when starting the second container, which maps all volumes from the source container into the target container's namespace.

### DCA Exam Focus
Understand syntax differences: `--volume` (`-v`) automatically creates a host directory if it does not exist, whereas `--mount` (the modern preferred engine mechanism) will fail explicitly with an error, protecting operations from unintended silent host configurations.
        """
    },
    {
        "id": 4,
        "title": "Module 4: Production-Grade Docker Networking",
        "theory": """
### The Container Network Model (CNM)
CNM defines container networking interfaces. It is comprised of three core components:
- **Sandbox:** The isolated container network configuration (IP, MAC, routing, DNS).
- **Endpoint:** Represents a network interface (veth pairs).
- **Network:** A collection of endpoints communicating with each other.

### Network Drivers
* **Bridge (default):** Private network on a single host. User-defined bridges enable **automatic internal DNS resolution** by container name.
* **Host:** Bypasses network namespaces; the container shares host IP addresses and ports directly, offering maximum throughput.
* **None:** No network adapters are attached, providing isolated batch processing capabilities.
* **Overlay:** Spans multiple host nodes in a swarm cluster, enabling secure routing of network packets across physical servers.
* **Macvlan:** Configures explicit physical MAC addresses for containers, making them look like hardware nodes directly attached to the physical local area network.
        """,
        "commands": """
### Command Reference

To create, configure, and troubleshoot container networks, master the following CLI commands:

* `docker network create [OPTIONS] NETWORK`  
  Create a new network.  
  - `-d, --driver`: Specify the network driver (default is `bridge`).  
* `docker network ls`  
  List all networks managed by the local Docker daemon.  
* `docker network inspect [OPTIONS] NETWORK [NETWORK...]`  
  Display detailed network configuration metadata, including connected container IP allocations.  
* `docker network connect [OPTIONS] NETWORK CONTAINER`  
  Connect an actively running container to a network on the fly.  
* `docker network disconnect [OPTIONS] NETWORK CONTAINER`  
  Disconnect a container from a network.
        """,
        "examples": """
### Real-World Examples

#### Example 1: Creating Isolated Backplanes with Custom Bridges
* **Situation:** You need to isolate database traffic from the public-facing API network layer on a single host.
* **Action:** Create a private user-defined bridge network, then launch a database container on it:
  ```bash
  docker network create --driver bridge secure_db_net
  docker run -d --name secure-postgres --network secure_db_net postgres:alpine
  ```

#### Example 2: Diagnostic Inspection of Docker IPtables Rules
* **Situation:** You need to troubleshoot incoming port forwarding issues to understand how traffic routes from your host interface to the container.
* **Action:** Query your Linux system's nat table directly to view port-forwarding rules:
  ```bash
  sudo iptables -t nat -L DOCKER -n -v
  ```

#### Example 3: Debugging Networks with Netshoot Containers
* **Situation:** Two containers are failing to communicate. You need to inspect routing tables and DNS records from within the network namespace without modifying the production images.
* **Action:** Launch a diagnostic helper container within the target network namespace to perform troubleshooting:
  ```bash
  docker run -it --rm --network secure_db_net nicolaka/netshoot nslookup secure-postgres
  ```

#### Example 4: Setting Up Custom Hosts File Aliases
* **Situation:** A container needs to connect to an external legacy server using a specific domain name, but you want to avoid hardcoding DNS names in your application.
* **Action:** Use the `--add-host` flag to inject host mapping entries directly into the container's `/etc/hosts` file:
  ```bash
  docker run -d --name host-mapped --add-host legacy-db:192.168.10.50 my-app:latest
  ```

#### Example 5: Connecting a Running Container to Multiple Networks
* **Situation:** An active service needs to access resources on another network without being restarted.
* **Action:** Connect the running container to the target network dynamically:
  ```bash
  docker network connect secure_db_net my-active-api
  ```
        """,
        "exercise": """
### Hands-On Labs

#### Lab 1: Isolating a Three-Tier Stack
* **Objective:** Design an isolated multi-network topography representing a public-facing reverse proxy, private API, and an unreachable database backend.
* **Tasks:**
  1. Create two custom networks: `front_net` and `back_net`.
  2. Run an Nginx proxy connected only to `front_net`.
  3. Run an API app instance connected to both networks.
  4. Run a Redis instance connected only to `back_net`.
  5. Verify that the proxy can reach the API, but cannot connect to the database.

#### Lab 2: Verifying Service Discovery Resolution
* **Objective:** Use a custom bridge network to verify automatic name resolution (DNS) between containers.
* **Tasks:**
  1. Create a custom network `test_dns_net`.
  2. Run two simple Alpine containers on this network.
  3. Ping one container from the other using its container name as the target hostname.
  4. Verify the ping fails when running the same containers on the default bridge network.

#### Lab 3: Benchmarking Network Drivers
* **Objective:** Compare network performance and throughput between the `bridge` and `host` network drivers.
* **Tasks:**
  1. Launch an `iperf3` server container using the default `bridge` driver.
  2. Run a network client container to measure throughput.
  3. Re-run the tests using the `host` network driver and compare metrics.

#### Lab 4: Dynamic Network Attachment
* **Objective:** Connect a running container to a network on-the-fly and verify communications.
* **Tasks:**
  1. Run a container on the default bridge network.
  2. Create a custom bridge network and start a target service on it.
  3. Use `docker network connect` to bridge the first container into the new network dynamically.

#### Lab 5: Port Mapping NAT Audit
* **Objective:** Audit the mapping translation configurations of exposed system ports.
* **Tasks:**
  1. Run a container mapping host port 8085 to container port 80.
  2. Use `docker ps` and `docker port` to verify the port forwarding configurations.
        """,
        "insight": """
### Interview Q&A

#### Q1: What happens to network latency and throughput when running a container with the host network driver versus the bridge driver? In what scenario is Macvlan preferred over Overlay?
* **Answer:** The `host` driver delivers near-zero latency overhead because it completely bypasses network namespace transitions and Network Address Translation (NAT) overhead. `Macvlan` is preferred when containers must be directly reachable by legacy non-containerized systems on the same physical network without passing through routing proxies or ingress mesh overheads.

#### Q2: Why does the default bridge network not support automatic service discovery by container name?
* **Answer:** The default bridge network is designed for legacy backward compatibility. It does not contain the embedded DNS helper capabilities built into custom user-defined networks. To map containers by name, you must deploy them on a user-defined bridge network.

#### Q3: Explain how port publishing works under the hood when exposing a port.
* **Answer:** When you publish a port (`-p 80:80`), the Docker daemon configures local IPtables firewall rules (such as DNAT) on the host system. This intercepts traffic arriving on host port 80 and translates the packets to the private IP address assigned to the container network adapter.

#### Q4: What is the purpose of the container overlay network driver?
* **Answer:** The `overlay` network driver enables secure communication between containers across separate physical hosts in a Docker Swarm cluster. Under the hood, it creates a virtual VXLAN tunnel to wrap and secure the cross-host network traffic.

#### Q5: How do you inspect which containers are attached to a specific network?
* **Answer:** Run `docker network inspect [network_name]`. The resulting JSON output contains a `Containers` block detailing the metadata and internal IP addresses of all attached containers.

### DCA Exam Focus
Understand that the default bridge network (`bridge`) does **not** support automatic service discovery/DNS mapping. To get DNS lookup by container name, you must use a custom, user-defined bridge network.
        """
    },
    {
        "id": 5,
        "title": "Module 5: Orchestrating with Docker Compose",
        "theory": """
### Multi-Container Orchestration
Docker Compose is a client-side tool used to define and manage multi-container applications in a declarative YAML manifest. 

### Core Manifest Components
- `services`: Defines the isolated application components.
- `networks`: Establishes customized backplanes.
- `volumes`: Preserves long-term data files.
- `depends_on`: Declares startup hierarchies and conditional initialization requirements.

### Lifecycle Workflow
- `docker compose up -d`: Instantiates or updates missing configuration structures in background detached mode.
- `docker compose down -v`: Safely tears down containers, networks, and explicitly associated volumes.
        """,
        "commands": """
### Command Reference

To manage multi-container stacks and monitor service orchestration lifecycles, master the following CLI commands:

* `docker compose up [OPTIONS]`  
  Build, create, start, and attach to containers for a service.  
  - `-d`: Run in detached background mode.  
  - `--build`: Force build images before starting containers.  
* `docker compose down [OPTIONS]`  
  Stop and remove containers, networks, images, and volumes.  
  - `-v`: Remove named volumes defined in the `volumes` section.  
* `docker compose ps`  
  List all active containers associated with the local project stack.  
* `docker compose logs [OPTIONS] [SERVICE...]`  
  View aggregated output log streams from all services in the stack.  
  - `-f`: Follow log output dynamically.  
* `docker compose exec [SERVICE] [COMMAND]`  
  Execute an arbitrary command inside a running service container.
        """,
        "examples": """
### Real-World Examples

#### Example 1: Resolving Cold-Start Race Conditions with Explicit Healthchecks
* **Situation:** Your API container crashes on startup because the database is still initializing and is not yet ready to accept connections, despite the database container being running.
* **Compose Configuration:**
  ```yaml
  version: '3.8'
  services:
    db:
      image: postgres:15-alpine
      environment:
        POSTGRES_DB: app_db
        POSTGRES_PASSWORD: secure_password
      healthcheck:
        test: ["CMD-SHELL", "pg_isready -U postgres -d app_db"]
        interval: 3s
        timeout: 3s
        retries: 5
    api:
      image: my_api_image:latest
      depends_on:
        db:
          condition: service_healthy
  ```

#### Example 2: Multi-Environment Config Loading
* **Situation:** You need to load alternate database hosts and secrets between development and production environments without duplicating your core Compose YAML file.
* **Setup Strategy:** Combine multiple compose files during execution to merge configuration values:
  ```bash
  docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
  ```

#### Example 3: Scaling Services to Handle Increased API Traffic
* **Situation:** You need to scale your API instances to three to handle a surge in traffic, while avoiding port allocation collisions on the host.
* **Resolution Action:** Define internal routing and scale your container service:
  ```bash
  docker compose up -d --scale api=3
  ```

#### Example 4: Mounting Shared Configuration and Data Volumes
* **Situation:** Multiple services in your stack need to access a shared folder to read or write files at runtime.
* **Compose Configuration:** Define and attach a shared named volume to multiple services:
  ```yaml
  services:
    uploader:
      image: upload-service
      volumes:
        - shared_data:/data/uploads
    processor:
      image: processing-service
      volumes:
        - shared_data:/data/uploads
  volumes:
    shared_data:
  ```

#### Example 5: Executing Isolated Database Migrations on Startup
* **Situation:** You need to run database migration scripts before starting your application container.
* **Compose Configuration:** Use a short-lived migration service that must run and exit successfully before starting the application:
  ```yaml
  services:
    db-migration:
      image: migration-tool
      command: ["npm", "run", "db:migrate"]
      depends_on:
        db:
          condition: service_healthy
    api:
      image: web-app
      depends_on:
        db-migration:
          condition: service_completed_successfully
  ```
        """,
        "exercise": """
### Hands-On Labs

#### Lab 1: The Three-Tier Microservices Stack
* **Objective:** Deploy a three-tier web application stack with database replication, isolated network backplanes, and state persistence.
* **Tasks:**
  1. Create a `docker-compose.yml` file defining a web proxy, an API, and a database service.
  2. Map appropriate port configurations and assign named volumes for database files.
  3. Spin up the stack in detached mode and verify network health using `docker compose ps`.

#### Lab 2: Implementing Graceful Scaling Behaviors
* **Objective:** Scale a service container dynamically to handle high traffic demands while avoiding port allocation conflicts.
* **Tasks:**
  1. Build a Compose stack that exposes a web application service.
  2. Verify that running `docker compose up -d --scale web=3` fails if you have hardcoded a single host port mapping (e.g., `80:80`).
  3. Refactor the ports mapping configuration to expose a range of host ports or route traffic through a dynamic reverse proxy.

#### Lab 3: Multi-Environment Variables Lab
* **Objective:** Configure a single Compose file to change its behavior dynamically depending on the active environment configuration.
* **Tasks:**
  1. Create a Compose file that references an external environment variable: `${APP_PORT}`.
  2. Implement an `.env` file that defines `APP_PORT=8080`.
  3. Run the stack and verify that the container is reachable on port 8080.

#### Lab 4: Composition Tear-Down Audit
* **Objective:** Safely destroy an entire application stack, verifying image layer and storage cleanups.
* **Tasks:**
  1. Run `docker compose down` inside your project directory.
  2. Verify that the associated networks and container namespaces are removed.
  3. Run `docker compose down -v` to ensure persistent storage volumes are pruned.

#### Lab 5: Dynamic Log Aggregation
* **Objective:** Inspect live system communications across multiple services using logging streams.
* **Tasks:**
  1. Run a multi-service Compose stack.
  2. Execute `docker compose logs -f [service_name]` to target a specific service.
  3. Monitor database connection attempts dynamically as the API boots up.
        """,
        "insight": """
### Interview Q&A

#### Q1: How does Docker Compose handle changes in your configuration when you run docker compose up -d a second time? Does it recreate all containers, or only modified ones?
* **Answer:** Docker Compose acts declaratively. It compares the state of active containers with the defined YAML configuration. Only modified configurations (images, volume additions, altered env mappings) are re-created, while unmodified resources continue running continuously.

#### Q2: What is the purpose of the `docker-compose.override.yml` file?
* **Answer:** It is a default file that Docker Compose automatically merges with your primary `docker-compose.yml` when running commands locally. It is commonly used to inject local development configurations (such as port exposures or debug keys) without polluting your production code.

#### Q3: How do you enforce container startup ordering in Docker Compose?
* **Answer:** Use the `depends_on` block to declare service relationships. For advanced control (such as waiting for database tables to initialize), combine `depends_on` with a service `healthcheck` constraint.

#### Q4: How does Compose locate and isolate separate container stacks running on the same host?
* **Answer:** It isolates stacks using a **Project Name** (derived by default from the parent directory's name). All resources (containers, networks, volumes) are prefixed with this project name to prevent cross-stack interference.

#### Q5: Can you scale a containerized service that uses host port mapping?
* **Answer:** No, trying to scale a service with a hardcoded host port mapping (e.g., `80:80`) causes host port allocation collisions. To scale a service, either omit host port exposure or use dynamic ranges (e.g., `80-85:80`) and route traffic through an ingress load balancer.

### DCA Exam Focus
Be prepared to recognize syntactically incorrect YAML blocks. Pay special attention to ports declaration lists vs. single exposed numbers, and volume map syntax parameters.
        """
    },
    {
        "id": 6,
        "title": "Module 6: Enterprise-Grade Security & Hardening (Senior Level)",
        "theory": """
### Principle of Least Privilege
By default, Docker containers run with too many Linux capabilities. To enforce absolute isolation, containerized processes should:
1. Run as a non-root system user.
2. Drop all unnecessary kernel privileges.

### Restricting Kernel Capabilities
Linux capabilities divide system privileges normally held by root into distinct blocks. You can drop all kernel privileges and selectively add only the necessary capabilities:
- `CHOWN`: Make arbitrary file ownership changes.
- `NET_BIND_SERVICE`: Bind ports lower than 1024.

### Read-Only Filesystems
Running with a read-only root partition (`--read-only`) prevents malicious exploits from injecting files, editing libraries, or executing arbitrary local shell scripts.
        """,
        "commands": """
### Command Reference

To run containers with restricted privileges, drop system capabilities, and enforce resource limits, learn the following command flags:

* `docker run --user [uid:gid]`  
  Force the containerized process to execute under a specific unprivileged UID/GID.  
* `docker run --cap-drop=ALL`  
  Remove all default Linux kernel capabilities from the container.  
* `docker run --cap-add=[CAPABILITY]`  
  Selectively add a specific required capability (e.g., `NET_BIND_SERVICE`).  
* `docker run --read-only`  
  Enforce a read-only root filesystem, blocking write operations to system directories.  
* `docker run --memory=[limit] --cpus=[limit]`  
  Configure resource limits to prevent denial-of-service (DoS) resource starvation.
        """,
        "examples": """
### Real-World Examples

#### Example 1: Enforcing Capabilities Drops
* **Situation:** You need to harden a container against kernel privilege escalation by stripping all kernel privileges except for port binding.
* **Action:** Launch the container dropping all privileges, then selectively add the capability required to bind ports below 1024:
  ```bash
  docker run -d --name secure-service --cap-drop=ALL --cap-add=NET_BIND_SERVICE -p 80:80 nginx:alpine
  ```

#### Example 2: Running a Hardened Container with a Read-Only Filesystem
* **Situation:** You need to prevent attackers from writing executable files or scripts to the filesystem of an exposed web application.
* **Action:** Run the container with a read-only filesystem, mounting a temporary volume in memory for paths that require write access:
  ```bash
  docker run -d --name hardened-nginx --read-only --mount type=tmpfs,destination=/var/cache/nginx --mount type=tmpfs,destination=/var/run -p 8080:80 nginx:alpine
  ```

#### Example 3: Scanning Production Images for Vulnerabilities
* **Situation:** You need to identify high and critical CVEs inside an image before deploying it to production.
* **Action:** Use Docker Scout to scan the target image:
  ```bash
  docker scout cves nginx:latest
  ```

#### Example 4: Mitigating Denial of Service via Fork-Bomb Protections
* **Situation:** A compromised container could spawn unlimited child processes, exhausting the host OS process table and locking up the physical server.
* **Action:** Set a strict processes execution limit inside the container:
  ```bash
  docker run -d --pids-limit=50 my-untrusted-app:latest
  ```

#### Example 5: Configuring TCP Socket TLS Daemon Communication
* **Situation:** You need to connect to a remote host's Docker daemon securely over the internet.
* **Action:** Configure the daemon to listen on a TCP port and enforce TLS client certificate verification. Edit `/etc/docker/daemon.json` on the remote host:
  ```json
  {
    "tlsverify": true,
    "tlscacert": "/etc/docker/ca.pem",
    "tlscert": "/etc/docker/server-cert.pem",
    "tlskey": "/etc/docker/server-key.pem",
    "hosts": ["tcp://0.0.0.0:2376"]
  }
  ```
        """,
        "exercise": """
### Hands-On Labs

#### Lab 1: The Privilege Escalation Audit
* **Objective:** Audit a legacy image that runs as root and modify it to run securely under an unprivileged user.
* **Tasks:**
  1. Inspect the running user of a legacy container using `docker exec whoami`.
  2. Rewrite the application's Dockerfile to define a custom user (UID 10001) and group.
  3. Rebuild the image and verify that the containerized process no longer runs as root.

#### Lab 2: Implementing Read-Only Storage Hardening
* **Objective:** Configure a containerized web server to run with a read-only root filesystem while still allowing write access to temporary log paths.
* **Tasks:**
  1. Attempt to run an Nginx container using the `--read-only` flag and analyze the crash logs when Nginx fails to write to its cache directory.
  2. Resolve the write failures by mounting `tmpfs` volumes at `/var/cache/nginx` and `/var/run`.
  3. Verify that you can access the website, but cannot modify files in other directories (e.g., `/usr/share/nginx/html`).

#### Lab 3: Defending Against DoS Starvation
* **Objective:** Apply strict resource limits to a container to prevent it from consuming excessive host CPU and memory.
* **Tasks:**
  1. Run a container with memory restricted to `64MB` and CPU allocation limited to `0.5` cores:
     ```bash
     docker run -it --memory="64m" --cpus="0.5" alpine /bin/sh
     ```
  2. Verify the resource limits inside the container by inspecting the appropriate control group file structures on the host.

#### Lab 4: Inspecting dropped capabilities
* **Objective:** Verify which kernel privileges are active inside a running container.
* **Tasks:**
  1. Run a standard Alpine container and run `capsh --print` inside it.
  2. Re-run with `--cap-drop=ALL` and inspect how the active capability set is reduced.

#### Lab 5: Host PID Visibility Audit
* **Objective:** Verify that containers cannot see parent processes running on the host OS.
* **Tasks:**
  1. Start a standard detached container.
  2. Execute `ps aux` inside the container.
  3. Verify that host process IDs (such as system daemons) are hidden from the container's process list.
        """,
        "insight": """
### Interview Q&A

#### Q1: If a container escapes its namespace, how does User Namespace Remapping prevent the containerized root user from acquiring root access on the underlying host?
* **Answer:** User Namespace Remapping maps the container's internal UID 0 (root) to a high, unprivileged range on the host system (e.g., UID 165536). If a process escapes its namespaces, the host kernel views it as UID 165536, preventing it from executing administrative tasks or compromising the host root filesystem.

#### Q2: What are Linux kernel capabilities and why should you drop them?
* **Answer:** Linux capabilities break down the absolute powers of the root user into discrete, independent privileges. By default, Docker grants several capabilities (like `NET_RAW` or `SYS_CHROOT`) that are unnecessary for most workloads. Dropping unnecessary capabilities reduces the risk of privilege escalation.

#### Q3: Why is running a container with the `--privileged` flag considered high risk?
* **Answer:** The `--privileged` flag bypasses all namespace and control group boundaries, granting the container full, direct access to the host system's hardware and kernel space. A privileged container is essentially running directly on the host as root.

#### Q4: How does Docker Content Trust (DCT) secure the image distribution pipeline?
* **Answer:** DCT uses digital signatures to verify the integrity and publisher of images pulled from registries. When enabled, Docker will reject pulls of unsigned or altered images, protecting hosts from running compromised software.

#### Q5: What is the purpose of Seccomp profiles in Docker?
* **Answer:** Seccomp (Secure Computing Mode) profiles restrict the system calls a containerized process can make to the host kernel. Docker applies a default Seccomp profile that blocks dangerous system calls (such as `reboot` or `swapon`), protecting the host kernel from abuse.

### DCA Exam Focus
Understand Docker Content Trust (DCT). Know that enabling `export DOCKER_CONTENT_TRUST=1` forces Docker to only pull and run verified, signed images from trusted registries.
        """
    },
    {
        "id": 7,
        "title": "Module 7: Image Registry Management & Distribution",
        "theory": """
### Registry Architectures
Registries store and distribute Docker image layers. The open-source `registry:2` container image allows you to run your own local registry.

### Secure Transport TLS Requirements
By default, Docker refuses to communicate with registries over unencrypted HTTP. To enable external pushes and pulls, you must secure the endpoint using trusted TLS certificates or configure the registry under `insecure-registries` within `/etc/docker/daemon.json`.

### Tagging Strategies
- **Semantic Versioning (SemVer):** e.g., `1.4.2`. Highly stable, predictable production model.
- **Git Commit Hash:** e.g., `app:sha-ab76c89`. Excellent for continuous delivery traceability.
- **Latest Tag:** Represents a rolling alias pointing to the newest build. Avoid utilizing this in production as it is non-deterministic.
        """,
        "commands": """
### Command Reference

To log in, tag, push, and pull images from custom repositories, learn the following commands:

* `docker login [OPTIONS] [SERVER]`  
  Authenticate with a container registry.  
  - `-u, --username`: Specify the login username.  
  - `-p, --password`: Pass the login password or token.  
* `docker tag SOURCE_IMAGE[:TAG] TARGET_IMAGE[:TAG]`  
  Create a tag `TARGET_IMAGE` that refers to `SOURCE_IMAGE`.  
* `docker push [OPTIONS] NAME[:TAG]`  
  Upload an image to a registry.  
* `docker pull [OPTIONS] NAME[:TAG]`  
  Download an image from a registry.
        """,
        "examples": """
### Real-World Examples

#### Example 1: Deploying an Internal Private Secure Registry with Self-Signed Certificates
* **Situation:** You need to set up an internal container image registry for private distribution without using external cloud services.
* **Action:** Generate self-signed keys, then spin up the registry mapping these files to secure communications:
  ```bash
  openssl req -newkey rsa:4000 -nodes -sha256 -keyout domain.key -x509 -days 365 -out domain.crt
  docker run -d --name secure-registry -v "$(pwd)"/certs:/certs -e REGISTRY_HTTP_TLS_CERTIFICATE=/certs/domain.crt -e REGISTRY_HTTP_TLS_KEY=/certs/domain.key -p 5000:5000 registry:2
  ```

#### Example 2: Configuring Host Daemons to Accept Insecure Registries
* **Situation:** A local testing registry lacks certificates, and Docker blocks push attempts with an untrusted connection error.
* **Action:** Edit `/etc/docker/daemon.json` to trust the endpoint, then restart the system service:
  ```json
  {
    "insecure-registries" : ["myregistry.local:5000"]
  }
  ```
  ```bash
  sudo systemctl restart docker
  ```

#### Example 3: Running Garbage Collection on Private Registries
* **Situation:** Your private registry's disk is filling up with orphaned and untagged layers that need to be purged.
* **Action:** Run the container registry's built-in garbage collection utility:
  ```bash
  docker exec -it secure-registry bin/registry garbage-collect /etc/docker/registry/config.yml
  ```

#### Example 4: Automating Registry Authentication via Config Files
* **Situation:** You need to automate container registry login within a CI/CD pipeline script without exposing your password in plain text.
* **Action:** Pass authentication credentials securely via standard input to avoid leak risks:
  ```bash
  echo "${REGISTRY_TOKEN}" | docker login registry.mycompany.com --username "pipeline-runner" --password-stdin
  ```

#### Example 5: Implementing Semantic Version Pinning
* **Situation:** You want to implement a strict, auditable tagging strategy that avoids the mutable `latest` tag in production.
* **Action:** Use a script to build, tag, and push images using both semantic versions and git commit hashes:
  ```bash
  COMMIT_SHA=$(git rev-parse --short HEAD)
  docker build -t registry.mycompany.com/app:v1.2.3 .
  docker tag registry.mycompany.com/app:v1.2.3 registry.mycompany.com/app:sha-${COMMIT_SHA}
  docker push registry.mycompany.com/app:v1.2.3
  docker push registry.mycompany.com/app:sha-${COMMIT_SHA}
  ```
        """,
        "exercise": """
### Hands-On Labs

#### Lab 1: Hosting a Private Secure Local Registry
* **Objective:** Deploy an instance of the Docker Registry, generate certificates to secure it, and log in successfully.
* **Tasks:**
  1. Generate a self-signed TLS certificate on your host.
  2. Spin up a `registry:2` container configured to load your self-signed certificate.
  3. Configure your local Docker daemon to trust this registry.
  4. Authenticate using `docker login localhost:5000`.

#### Lab 2: Building and Pushing Custom Layer Images
* **Objective:** Tag and push a locally compiled image to your private registry, verify its upload, and pull it on demand.
* **Tasks:**
  1. Build a lightweight Alpine-based image.
  2. Tag the image using your private registry's domain name: `localhost:5000/test-app:1.0.0`.
  3. Push the image to your registry and verify that the layers upload successfully.
  4. Delete the local image from your host and pull it again from the registry.

#### Lab 3: Registry Authentication Hardening Lab
* **Objective:** Restrict access to your private registry using basic HTTP authentication.
* **Tasks:**
  1. Use the `htpasswd` utility to generate a secure credential file.
  2. Relaunch your private registry container configured to use the generated authentication file.
  3. Verify that push and pull attempts fail without executing a successful `docker login` command first.

#### Lab 4: Pulling Verification of Multi-tag Architectures
* **Objective:** Push and catalog identical image binaries with separate SemVer identifiers.
* **Tasks:**
  1. Build a simple image and tag it with multiple release variants (e.g., `v1.0.0`, `latest`).
  2. Push both tags to your registry and verify they point to the identical manifest digest.

#### Lab 5: Registry API Audit
* **Objective:** Query the registry's built-in REST API catalog directly.
* **Tasks:**
  1. Pull a list of all repositories stored in your registry using the catalog API endpoint:
     ```bash
     curl http://localhost:5000/v2/_catalog
     ```
  2. Parse the JSON response to verify your images are registered.
        """,
        "insight": """
### Interview Q&A

#### Q1: Why is using the latest tag in production environments considered an anti-pattern? How do you implement robust rollbacks when using automated image distribution pipelines?
* **Answer:** The `latest` tag is mutable; it is constantly overwritten by new builds. If a deployment fails, there is no way to pin down the exact historical image variant to rollback to. To support reliable rollbacks, tag your images with explicit version tags or git commit hashes, allowing you to easily target stable releases.

#### Q2: What security risks are introduced when running local registries without TLS (over HTTP)?
* **Answer:** Communicating over unencrypted HTTP exposes credentials and image data to man-in-the-middle (MitM) attacks. Furthermore, the Docker engine rejects connections to insecure registries by default, requiring you to explicitly modify client config files to trust the endpoint.

#### Q3: How do you configure a private registry to store its image layers on AWS S3 instead of local disk?
* **Answer:** Configure the registry container with S3 storage driver variables, passing parameters such as `REGISTRY_STORAGE_S3_BUCKET`, `REGISTRY_STORAGE_S3_REGION`, and access credentials directly to the container environment.

#### Q4: What is the exact purpose of running "garbage collection" on a registry?
* **Answer:** When you delete an image tag from a registry, the reference is removed, but the underlying layers (blobs) remain on disk. Running garbage collection scans the registry, identifies these orphaned layers, and deletes them to free up physical storage.

#### Q5: What is a Docker registry manifest?
* **Answer:** A manifest is a JSON file that defines a Docker image. It lists all of the image's filesystem layers, their cryptographic hashes (digests), and the metadata (such as entrypoint commands or environments) required to run the container.

### DCA Exam Focus
Know how to tag an image with an external registry URL: `docker tag [local-image] [registry-domain]/[repository]/[image-name]:[tag]`.
        """
    },
    {
        "id": 8,
        "title": "Module 8: Native Clustering with Docker Swarm",
        "theory": """
### Swarm Architecture
Docker Swarm is Docker's native container orchestration engine. It consists of:
* **Manager Nodes:** Manage cluster state, schedule services, and maintain quorum using the **Raft Consensus Algorithm**.
* **Worker Nodes:** Receive and execute tasks assigned by the managers.

### Quorum and the Raft Consensus Algorithm
For a Swarm cluster to remain operational, managers must maintain a strict majority quorum:
$$\text{Quorum} = \lfloor N/2 \rfloor + 1$$
If quorum is lost (e.g., due to a split-brain network partition), write operations freeze to prevent cluster state inconsistency.

### Swarm Deployment Abstractions
- **Service:** A declarative state definition of a workload (similar to a container, but run across multiple nodes).
- **Task:** The actual runtime container instance scheduled to execute a service's work.
- **Stack:** A collection of Swarm services deployed together using a standard Compose file format.
        """,
        "commands": """
### Command Reference

To initialize clusters, manage cluster nodes, and deploy scaled stacks, master the following Swarm commands:

* `docker swarm init [OPTIONS]`  
  Initialize a Swarm cluster. The current node becomes the first manager.  
  - `--advertise-addr`: Specify the IP address to advertise to other nodes.  
* `docker swarm join [OPTIONS] HOST:PORT`  
  Join a Swarm cluster as a worker or manager node.  
* `docker node ls`  
  List all active nodes in the Swarm cluster (can only be run from manager nodes).  
* `docker service create [OPTIONS] IMAGE [COMMAND] [ARG...]`  
  Create a new Swarm service.  
  - `--replicas`: Define the number of container tasks to run across the cluster.  
* `docker stack deploy [OPTIONS] STACK`  
  Deploy a multi-service application stack using a Compose file.
        """,
        "examples": """
### Real-World Examples

#### Example 1: Creating a Cluster and Demoting Manager Nodes
* **Situation:** You need to transition an active manager node to a worker node for system maintenance.
* **Action:** Inspect the active cluster nodes, then demote the target manager:
  ```bash
  docker node ls
  docker node demote node-2-manager
  ```

#### Example 2: Executing Zero-Downtime Rolling Service Updates
* **Situation:** You need to deploy a new version of an application without causing downtime.
* **Action:** Deploy the service with rolling update policies, then run the update command:
  ```bash
  docker service create --name api-prod --replicas 5 --update-delay 10s --update-parallelism 1 myregistry.com/api:1.0.0
  docker service update --image myregistry.com/api:2.0.0 api-prod
  ```

#### Example 3: Managing Secrets inside Swarm
* **Situation:** You need to pass database credentials to container tasks securely without baking them into images or exposing them as plaintext environment variables.
* **Action:** Create the Swarm secret, then attach it during service creation:
  ```bash
  echo "my_super_secure_password" | docker secret create db_production_password -
  docker service create --name secure-app --secret db_production_password my-app:latest
  ```

#### Example 4: Creating Global Services for Monitoring Agents
* **Situation:** You need to run a log collection agent (like Fluentd) on every node in the Swarm cluster, including nodes added in the future.
* **Action:** Deploy the service with global mode enabled, which ensures exactly one task runs per node:
  ```bash
  docker service create --name log-collector --mode global monitoring-agent:latest
  ```

#### Example 5: Recovering Quorum After Manager Node Failure
* **Situation:** Two of your three managers are offline, and the remaining manager refuses to accept write operations because quorum is lost.
* **Action:** Force the remaining manager to initialize a new single-manager cluster, recovering the cluster state:
  ```bash
  docker swarm init --force-new-cluster --advertise-addr 192.168.1.100
  ```
        """,
        "exercise": """
### Hands-On Labs

#### Lab 1: Multi-Node Cluster Orchestration
* **Objective:** Initialize a Swarm manager node, add worker nodes to the cluster, and inspect the cluster state.
* **Tasks:**
  1. Initialize Swarm on your primary terminal node: `docker swarm init`.
  2. Join worker nodes to the cluster using the join token generated during initialization.
  3. Verify that all nodes are registered and online by running `docker node ls` on the manager.

#### Lab 2: Highly Available Service Scaling Lab
* **Objective:** Deploy a highly available service, scale its replica tasks, and verify automatic scheduling across nodes.
* **Tasks:**
  1. Create a replicated service using Nginx:
     ```bash
     docker service create --name web-service --replicas 2 -p 8080:80 nginx:alpine
     ```
  2. Scale the service to five replicas and watch the scheduling behavior:
     ```bash
     docker service scale web-service=5
     ```
  3. Inspect node distribution to verify tasks are running on multiple nodes.

#### Lab 3: Swarm Secrets Orchestration
* **Objective:** Create and inject a Swarm secret into an active service container to securely configure your application.
* **Tasks:**
  1. Create a secure Swarm secret containing a mock API token.
  2. Deploy a service that references this secret.
  3. Log into one of the container tasks and verify that the decrypted secret is available at `/run/secrets/`.

#### Lab 4: Service Rollback Lab
* **Objective:** Perform a rolling service update and verify rollback behavior.
* **Tasks:**
  1. Deploy a service running an old image tag.
  2. Update the service to a new, broken image tag.
  3. Roll back the deployment to the previous stable release using `docker service rollback`.

#### Lab 5: Cluster Health Check and Rescheduling
* **Objective:** Verify that Swarm automatically reschedules tasks from unhealthy nodes to healthy ones.
* **Tasks:**
  1. Run a service scaled to three replicas.
  2. Force-shutdown or stop one of your worker nodes.
  3. Verify that Swarm immediately reschedules the missing container tasks onto the remaining healthy nodes.
        """,
        "insight": """
### Interview Q&A

#### Q1: Explain how the Raft Consensus Algorithm operates within Docker Swarm Manager nodes. What is the minimum number of managers required to tolerate a loss of 2 managers?
* **Answer:** Raft requires a strict majority of managers to be online to authorize cluster changes. If you have $N$ managers, you need at least $\lfloor N/2 \rfloor + 1$ online. To tolerate a loss of 2 managers, you must start with a minimum of 5 manager nodes (quorum of 3 is maintained when 2 go offline).

#### Q2: How does the Swarm Routing Mesh route traffic to container tasks?
* **Answer:** The Routing Mesh uses an IPVS load balancer on every node. When traffic arrives on an exposed port on any node, IPVS routes the packets over the overlay network to an active container task running on any host in the cluster.

#### Q3: What is the main structural difference between a Swarm Service and a Swarm Task?
* **Answer:** A Swarm Service is the declarative definition of your workload (such as image name, replicas, and ports). A Swarm Task is the actual running container instance scheduled by the manager to execute that workload on a node.

#### Q4: How do secrets differ from configurations in Swarm?
* **Answer:** Both are injected at runtime, but Secrets are cryptographically stored on managers, transmitted securely to nodes, and mounted strictly inside the container's RAM space. Configurations are meant for non-sensitive data (like config files) and are stored in plaintext.

#### Q5: Can you run standard Docker Compose files on a Swarm cluster?
* **Answer:** Yes, by deploying them as a Stack. Use the `docker stack deploy -c docker-compose.yml [stack_name]` command, which parses the compose file and creates the declared services on the cluster.

### DCA Exam Focus
Understand Swarm network port requirements:
- **Port 2377 TCP:** Cluster management communications.
- **Port 7946 TCP/UDP:** Node-to-node communication (gossip).
- **Port 4789 UDP:** Overlay network data traffic.
        """
    },
    {
        "id": 9,
        "title": "Module 9: Production Diagnostics, Logging, & Monitoring",
        "theory": """
### Logging Drivers
Docker captures stdout and stderr from container processes. By default, these logs are handled by the `json-file` driver. If left unconfigured, these log files can grow indefinitely and fill up the host disk. It is best practice to configure log rotation.

### Common Diagnostic Tools
- `docker inspect`: Returns a detailed JSON block detailing container metadata.
- `docker stats`: Live resource usage statistics (CPU, RAM, networking).
- `docker diff`: Inspects changes made directly to the container's writable filesystem layer.
- `docker events`: Stream of actions executed by the daemon.

### Identifying Fatal Exit Codes
* **Exit Code 137:** The container was terminated by the OS Out-of-Memory (OOM) killer or via a manual `kill -9` (`SIGKILL`).
* **Exit Code 139:** Segmentation fault error.
* **Exit Code 127:** Executable file or command not found.
        """,
        "commands": """
### Command Reference

To troubleshoot issues and monitor running containers, master the following diagnostic commands:

* `docker stats [OPTIONS] [CONTAINER...]`  
  Display a live, real-time stream of container resource usage statistics.  
* `docker logs [OPTIONS] CONTAINER`  
  Fetch the logs of a container.  
  - `--tail`: Number of lines to show from the end of the logs.  
  - `-t, --timestamps`: Show timestamps for each log entry.  
* `docker diff CONTAINER`  
  Inspect changes on a container's filesystem (shows added, changed, or deleted files).  
* `docker events [OPTIONS]`  
  Get real-time event logs from the Docker daemon.  
* `docker inspect --format '{{json .State}}' CONTAINER`  
  Filter and display specific metadata fields.
        """,
        "examples": """
### Real-World Examples

#### Example 1: Troubleshooting Zombie Processes inside Containers
* **Situation:** Your application spawns background processes that become defunct/zombie processes, leaking resources over time.
* **Action:** Set the execution command to use `tini` as the init process to handle signal forwarding and reap zombie processes:
  ```bash
  docker run -d --name app-init --init my-app:latest
  ```

#### Example 2: Programmatic Metadata Parsing with Docker Inspect Formatting
* **Situation:** You need to extract a container's dynamic IP address or status programmatically in a bash script.
* **Action:** Use Go template formatting inside `docker inspect`:
  ```bash
  docker inspect --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' my-nginx-container
  ```

#### Example 3: Debugging Storage Overconsumption by Locating File System Mutations
* **Situation:** A container is consuming disk space, and you need to identify which path or process is writing to the container's writable layer instead of a volume.
* **Action:** Query the container's write delta:
  ```bash
  docker diff my-nginx-container
  ```

#### Example 4: Real-time Event Monitoring
* **Situation:** You need to track container start, stop, and destroy events in real-time to audit daemon activity.
* **Action:** Use the events command to stream daemon logs:
  ```bash
  docker events --filter 'type=container' --filter 'event=die'
  ```

#### Example 5: Capturing Metrics for Prometheus Integration
* **Situation:** You need to expose host and engine performance metrics in Prometheus format for system monitoring.
* **Action:** Configure the daemon to expose engine metrics directly. Edit `/etc/docker/daemon.json`:
  ```json
  {
    "metrics-addr": "127.0.0.1:9323",
    "experimental": true
  }
  ```
        """,
        "exercise": """
### Hands-On Labs

#### Lab 1: The Out Of Memory Recovery Lab
* **Objective:** Troubleshoot a container that is crashing with exit code 137, identify the cause, and resolve the issue.
* **Tasks:**
  1. Run a test container configured with a very low memory limit (e.g., 10MB) and execute a process that consumes more memory.
  2. Verify that the container exits immediately.
  3. Inspect the exit code of the crashed container using `docker ps -a`.
  4. Run `docker inspect` to confirm the container was terminated by the OOM killer (`"OOMKilled": true` in the state block).

#### Lab 2: Logging Driver Configuration Lab
* **Objective:** Configure the Docker daemon to rotate log files automatically to prevent them from filling up the host disk.
* **Tasks:**
  1. Edit `/etc/docker/daemon.json` to configure the default log options:
     ```json
     {
       "log-driver": "json-file",
       "log-opts": {
         "max-size": "5m",
         "max-file": "3"
       }
     }
     ```
  2. Restart the Docker daemon to apply the configuration.
  3. Verify that container logs rotate automatically and never exceed the configured file size limit.

#### Lab 3: Runtime Metrics Capturing
* **Objective:** Use diagnostic tools to identify resource bottlenecks inside running containers.
* **Tasks:**
  1. Launch several containers running intensive batch tasks.
  2. Use `docker stats` to monitor CPU, memory, and network utilization in real-time.
  3. Identify which container is consuming the most resources and force-stop it.

#### Lab 4: Live Event Streaming Audit
* **Objective:** Track system events during a container lifecycle.
* **Tasks:**
  1. Start `docker events` in one terminal window.
  2. Start, stop, and destroy a container in another terminal.
  3. Audit the generated events stream output.

#### Lab 5: Filesystem Mutation Audit
* **Objective:** Verify which files are created inside the container's writable layer during execution.
* **Tasks:**
  1. Run an Alpine container and write a temporary file to `/tmp`.
  2. Execute `docker diff` on the container from the host.
  3. Verify the file path is listed with an `A` (Added) indicator.
        """,
        "insight": """
### Interview Q&A

#### Q1: If you see a container state of Exited (137), what does that exit code signify, and how do you determine if the host operating system kernel triggered it?
* **Answer:** Exit code 137 indicates that the process was terminated by `SIGKILL` (signal 9 + exit offset 128). To check if this was triggered by the kernel's Out-Of-Memory (OOM) killer, inspect system logs with `dmesg | grep -i oom` or run `docker inspect` on the stopped container and check the `OOMKilled` boolean in the state block.

#### Q2: What is the risk of using the default json-file logging driver without configuration?
* **Answer:** By default, the `json-file` driver does not rotate or limit log file sizes. If a container continuously writes to stdout/stderr, these files will grow indefinitely and consume all available disk space on the host.

#### Q3: How does the syslog logging driver differ from the default json-file driver?
* **Answer:** The `syslog` driver redirects container logs directly to the host's system logging daemon, preventing Docker from storing log files locally on disk. Note that when using `syslog`, the `docker logs` command is disabled.

#### Q4: What does exit code 127 indicate, and how do you debug it?
* **Answer:** Exit code 127 means the command or executable specified in the container's entrypoint or command was not found. Debug this by verifying that the path to the executable is correct, and that the binary exists inside the image.

#### Q5: How do you capture container networking traffic on a bridge network from the host?
* **Answer:** Find the container's virtual ethernet adapter interface name using `docker inspect`. Then, use standard network monitoring tools on the host (like `tcpdump -i [veth_name]`) to capture packets directly.

### DCA Exam Focus
Understand all common exit codes (137, 139, 126, 127). Know how to switch logging targets dynamically (e.g., streaming logs to `syslog` or `fluentd`).
        """
    },
    {
        "id": 10,
        "title": "Module 10: Multi-Platform CI/CD Integration & Buildx",
        "theory": """
### CI/CD Architecture Models
- **Docker-out-of-Docker (DooD):** Mounts the host's `/var/run/docker.sock` socket inside your pipeline runner container. This allows the runner to execute Docker commands on the host daemon. It is faster and shares the host's cache, but it presents security risks since the runner container gets root access to the host.
- **Docker-in-Docker (DinD):** Runs an isolated Docker daemon inside the container. This setup is highly isolated, but it requires running the container in `--privileged` mode, which presents significant security risks.

### Buildx & BuildKit
Buildx is a Docker CLI plugin that exposes modern image-building features powered by BuildKit:
- **Parallel Step Execution:** Accelerates compilation times.
- **Cache Mounts (`--mount=type=cache`):** Allows package managers (like `apt` or `npm`) to persist cache structures across separate image builds.
- **Multi-Platform Manifests:** Compiles and packages images for different CPU architectures (e.g., AMD64 and ARM64) simultaneously.
        """,
        "commands": """
### Command Reference

To configure next-generation build tools, manage builder instances, and execute multi-platform compilation tasks, master these commands:

* `docker buildx create [OPTIONS]`  
  Create a new builder instance.  
  - `--name`: Assign a custom name to the builder.  
  - `--use`: Set this builder as the default active builder.  
* `docker buildx ls`  
  List all available builder instances and their supported platform architectures.  
* `docker buildx build [OPTIONS] PATH`  
  Execute an image build using the BuildKit engine.  
  - `--platform`: Specify target platforms (e.g., `linux/amd64,linux/arm64`).  
  - `--push`: Push the compiled multi-architecture image directly to your registry.  
* `export DOCKER_BUILDKIT=1`  
  Enable the modern BuildKit engine for standard build commands on older Docker installations.
        """,
        "examples": """
### Real-World Examples

#### Example 1: Accelerating Javascript Builds using BuildKit Cache Mounts
* **Situation:** Installing packages inside your CI pipeline from scratch on every run takes too long.
* **Dockerfile Resolution:** Use cache mounts to persist package manager cache directories across builds:
  ```dockerfile
  # syntax=docker/dockerfile:1
  FROM node:18-alpine
  WORKDIR /app
  COPY package*.json ./
  # Mount the npm cache directory to speed up subsequent builds
  RUN --mount=type=cache,target=/root/.npm npm ci
  COPY . .
  ```

#### Example 2: Configuring a DooD (Docker Out of Docker) pipeline runner
* **Situation:** You need to configure a GitLab or Jenkins runner that can run Docker commands without using unsecure privileged modes.
* **Pipeline Configuration:** Map the local engine socket as a mount path inside the runner configuration:
  ```bash
  docker run -d --name pipeline-runner -v /var/run/docker.sock:/var/run/docker.sock gitlab-runner:latest
  ```

#### Example 3: Running a Multi-Platform Build with Buildx
* **Situation:** You need to build and publish an image that can run on both standard cloud servers (AMD64) and Apple Silicon developer machines (ARM64) from your local computer.
* **Action:** Use `buildx` to compile for both architectures:
  ```bash
  docker buildx create --name multi-arch-builder --use
  docker buildx build --platform linux/amd64,linux/arm64 -t myregistry.com/app:v1.0 --push .
  ```

#### Example 4: Mounting Secrets at Build Time
* **Situation:** You need to access a private SSH key or API token during the image build process (e.g., to clone a private repository), but you don't want the secret to be baked into the image layers.
* **Action:** Mount the secret using BuildKit's secret mount type:
  ```dockerfile
  # syntax=docker/dockerfile:1
  FROM alpine:latest
  # The secret is mounted securely and is not cached in the final image
  RUN --mount=type=secret,id=git_ssh_key cat /run/secrets/git_ssh_key
  ```
  Build command:
  ```bash
  docker buildx build --secret id=git_ssh_key,src=~/.ssh/id_rsa -t my-app .
  ```

#### Example 5: Compiling High-Speed Multi-Platform Builds using Native Emulation
* **Situation:** Multi-architecture builds using QEMU emulation are slow. You need to leverage native compilation for each target platform during the build.
* **Dockerfile Resolution:** Use target platform build arguments to run architecture-specific commands:
  ```dockerfile
  FROM --platform=$BUILDPLATFORM golang:1.20-alpine AS builder
  ARG TARGETOS
  ARG TARGETARCH
  WORKDIR /app
  COPY . .
  RUN GOOS=$TARGETOS GOARCH=$TARGETARCH go build -o myapp .
  ```
        """,
        "exercise": """
### Hands-On Labs

#### Lab 1: Building a BuildKit Caching Pipeline
* **Objective:** Modify an application Dockerfile to use persistent cache mounts and measure the speed improvement in subsequent builds.
* **Tasks:**
  1. Add a cache mount (`--mount=type=cache`) to your dependency installation step in your Dockerfile.
  2. Run an initial build and measure the compilation time.
  3. Modify an application file and run the build again to verify that package manager dependencies are loaded from the cache.

#### Lab 2: Cross-Platform Builder Compilation
* **Objective:** Create a multi-architecture builder instance, verify its platform support, and compile an image for multiple CPU architectures.
* **Tasks:**
  1. Create a custom builder: `docker buildx create --name cross-builder --use`.
  2. Inspect the builder's platform support using `docker buildx inspect`.
  3. Compile a test image for both `linux/amd64` and `linux/arm64` architectures.

#### Lab 3: Implementing a Secure Socket Pipeline Runner
* **Objective:** Deploy a secure, isolated CI/CD runner container that communicates with the host's Docker engine via the UNIX socket.
* **Tasks:**
  1. Start a helper runner container mounting `/var/run/docker.sock` to the container's socket path.
  2. Access the runner's terminal and execute Docker commands to verify you can manage host resources.
  3. Implement strict permissions on the host socket file to restrict which container users can access the engine.

#### Lab 4: BuildKit Multi-Platform Verification
* **Objective:** Inspect a compiled multi-architecture image in your registry.
* **Tasks:**
  1. Build a multi-platform image with `buildx` and push it to a public registry.
  2. Inspect the image manifest using `docker buildx imagetools inspect [image_name]`.
  3. Verify that separate digests exist for AMD64 and ARM64 platforms.

#### Lab 5: Parallel Build Step Audit
* **Objective:** Verify how BuildKit executes independent build steps in parallel.
* **Tasks:**
  1. Write a Dockerfile containing independent multi-stage compilation branches.
  2. Execute the build and inspect the terminal output graph to verify that steps run in parallel.
        """,
        "insight": """
### Interview Q&A

#### Q1: What are the primary security and security-context risks associated with running Docker-in-Docker (DinD) inside automated pipeline runners compared to mounting the docker socket (DooD)?
* **Answer:** DinD requires the runner container to have the `--privileged` flag enabled, which bypasses all container security protections and grants the container full access to the host system hardware and kernel. While DooD is more secure because it does not require privileged mode, anyone with access to the mounted `/var/run/docker.sock` socket still has root-level control over the host.

#### Q2: What is BuildKit and how does it differ from the legacy build engine?
* **Answer:** BuildKit is a modern, high-performance image build engine. It introduces several performance improvements over the legacy engine, including parallel step execution, automatic caching of unused build stages, and native support for mount features (such as secrets and package cache volumes).

#### Q3: How do you configure a build to use caching from an external registry rather than local layers?
* **Answer:** Use Buildx's `--cache-from` and `--cache-to` options. Passing parameters like `--cache-to=type=registry,ref=myregistry.com/app:cache` pushes build cache metadata directly to the registry, making it accessible to external CI/CD runners.

#### Q4: Why are multi-platform builds using QEMU slower than native compilations?
* **Answer:** QEMU emulates the instructions of the target architecture (such as ARM64) on your host CPU (such as AMD64) using software translation. This introduces significant CPU overhead. Native compilation processes avoid this translation lag.

#### Q5: How do you securely inject sensitive credentials (like an API token) during an image build without exposing them in the final image layers?
* **Answer:** Use BuildKit's `--secret` mount feature. This mounts the secret temporarily into the container's RAM space during the execution of specific instructions, ensuring the credentials never touch the host disk or the final image layers.

### DCA Exam Focus
Understand how to enable BuildKit globally via environment configurations (`export DOCKER_BUILDKIT=1`).
        """
    },
    {
        "id": 11,
        "title": "Module 11: DCA Exam Prep & Senior Capstone",
        "theory": """
### DCA Exam Blueprint Breakdown
The Docker Certified Associate (DCA) exam evaluates candidates across six key domains:
1. **Orchestration (25%)**: Swarm management, service creation, rolling updates, and routing mesh.
2. **Image Creation, Management, and Registry (20%)**: Optimized Dockerfiles, multi-stage builds, registry auth, and Docker Content Trust.
3. **Installation and Configuration (15%)**: Daemon engine options, log rotation, storage driver selection, and rootless operation.
4. **Networking (15%)**: Drivers, user-defined bridges, service discovery, and cross-host overlay networking.
5. **Security (15%)**: Linux capabilities, namespaces, cgroups, user remapping, and certificate configuration.
6. **Storage and Volumes (10%)**: Host mounting, persistent volumes, and storage drivers.

### Complex System Design Patterns
Senior DevOps engineers must be able to design highly available, self-healing, secure container environments across multiple hosts.
        """,
        "commands": """
### Command Reference

To prepare for the DCA exam and manage complex production environments, master the following administrative commands:

* `docker system prune [OPTIONS]`  
  Remove unused data from the host system.  
  - `-a, --all`: Remove all unused images, not just dangling ones.  
  - `--volumes`: Prune unused volumes as well.  
* `docker system df`  
  Show disk space usage by different Docker resources on the host.  
* `docker node update --role [manager|worker] [NODE]`  
  Update the role of a node in the Swarm cluster.  
* `docker service rollback [SERVICE]`  
  Roll back a Swarm service to its previous configuration version.  
* `docker service ps [SERVICE]`  
  List the tasks of a service, including previous versions and their exit statuses.
        """,
        "examples": """
### Real-World Examples

#### Example 1: Restoring a Fragmented Swarm Manager Consensus Group
* **Situation:** Two of your three Swarm managers have gone offline permanently due to hardware failure, causing the cluster to lose quorum and lock up.
* **Action:** Force-reinitialize the Swarm on the remaining healthy manager node to restore cluster state:
  ```bash
  docker swarm init --force-new-cluster --advertise-addr 192.168.1.100
  ```

#### Example 2: Managing Orphaned Resources and Inode Leaks
* **Situation:** Your host is running out of disk space or inodes due to build-up of dangling images, anonymous volumes, and stopped containers.
* **Action:** Perform a complete cleanup of unused resources:
  ```bash
  docker system prune -a --volumes --force
  ```

#### Example 3: Recovering from Database Storage Driver I/O Bottlenecks
* **Situation:** A performance review shows that your database container is experiencing high read/write latency.
* **Action:** Inspect the container's storage configuration and ensure it is not writing directly to its layered filesystem:
  ```bash
  docker inspect --format='{{range .Mounts}}{{.Type}}: {{.Source}}{{end}}' my-database
  ```

#### Example 4: Implementing Zero-Downtime Service Rollbacks
* **Situation:** You deployed a bad image version to a Swarm service, and users are experiencing errors. You need to roll back to the previous stable release instantly.
* **Action:** Roll back the service deployment:
  ```bash
  docker service rollback api-service
  ```

#### Example 5: Pinning Storage Drivers Globally
* **Situation:** You need to force the Docker daemon to use the high-performance `overlay2` storage driver on all new host installations.
* **Action:** Edit `/etc/docker/daemon.json` to configure the storage driver explicitly:
  ```json
  {
    "storage-driver": "overlay2"
  }
  ```
        """,
        "exercise": """
### Hands-On Labs

#### Lab 1: The Production Hardened Capstone Stack
* **Objective:** Design, deploy, and secure a production-ready, highly available three-tier application stack on a Swarm cluster.
* **Tasks:**
  1. Initialize a multi-node Swarm cluster.
  2. Secure your configuration files and database credentials using Swarm secrets and Swarm configs.
  3. Ensure no container runs as root.
  4. Set up log rotation for all services.
  5. Enforce explicit CPU and memory resource limits for every container.
  6. Perform a zero-downtime rolling update of your web service, and verify the traffic continues to route without interruption.

#### Lab 2: Simulating and Recovering from Swarm Split-Brain
* **Objective:** Simulate a network partition on manager nodes to understand quorum and recover the cluster state.
* **Tasks:**
  1. Set up a three-manager Swarm cluster.
  2. Disconnect or stop two of the manager nodes to simulate a network partition.
  3. Verify that the remaining manager node transitions to a read-only state and refuses cluster configuration updates.
  4. Recover the cluster by running `docker swarm init --force-new-cluster` on the remaining active manager node.

#### Lab 3: Master Storage Pruning Lab
* **Objective:** Identify and recover host disk space consumed by accumulated images, containers, and volumes.
* **Tasks:**
  1. Run `docker system df` to check the disk space usage of your Docker installation.
  2. Create several intermediate images and anonymous volumes to simulate disk fragmentation.
  3. Perform a safe system prune to recover disk space: `docker system prune --volumes`.
  4. Run `docker system df` again to verify the recovered disk space.

#### Lab 4: Node Promotion and Demotion Audit
* **Objective:** Manage Swarm cluster membership roles dynamically.
* **Tasks:**
  1. Inspect the roles of nodes in your cluster: `docker node ls`.
  2. Promote a worker node to a manager: `docker node promote [node_name]`.
  3. Verify the role change, then demote the node back to a worker.

#### Lab 5: Rolling Update Monitoring Lab
* **Objective:** Track task state transitions dynamically during a service update.
* **Tasks:**
  1. Run a service scaled to three replicas.
  2. Trigger an update to a new image version.
  3. Run `docker service ps [service_name]` continuously to inspect the rolling transition of individual tasks.
        """,
        "insight": """
### Interview Q&A

#### Q1: Which Swarm command is used to join a new node as a manager?
* **Answer:** `docker swarm join-token manager` (displays the join token and command required to join as a manager node)

#### Q2: How can you configure the Docker daemon to use user namespace remapping?
* **Answer:** Add the `"userns-remap": "default"` key-value pair to the `/etc/docker/daemon.json` configuration file, then restart the Docker service.

#### Q3: What is the minimum number of manager nodes required to tolerate the failure of 1 manager?
* **Answer:** 3 manager nodes. Raft quorum requires a strict majority of managers to be online ($\\lfloor N/2 \\rfloor + 1$). For 3 managers, quorum is 2. If 1 fails, 2 remain online, which is enough to maintain quorum.

#### Q4: What is the exact difference between replicated and global services in Swarm?
* **Answer:** Replicated services run a specific, user-defined number of replica tasks across the cluster. Global services run exactly one task on every active node in the cluster, including nodes added in the future.

#### Q5: How do you retrieve logs for a specific service running inside a Swarm cluster?
* **Answer:** Run `docker service logs [service_name]`. Swarm aggregates standard output and error logs from all running tasks across all nodes and streams them back to your terminal.
        """
    }
]
