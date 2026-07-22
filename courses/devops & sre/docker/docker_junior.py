# Docker Junior Course Definition
COURSE_ID = "docker-junior-ops"
COURSE_TITLE = "Docker Junior Level"
COURSE_DESCRIPTION = "Master container mechanics, image building optimization, local networks, volumes, and multi-container environment management for DevOps, SRE, and backend workflows."

CURRICULUM_DATA = [
    {
        "id": 1,
        "title": "Module 1: Docker Architecture, Conceptual Foundations & Container Lifecycles",
        "theory": r"""
### Guided Conceptual Walkthrough
Think of a traditional Virtual Machine (VM) as a fully self-contained apartment building. Each apartment (VM) has its own foundation, structural walls, plumbing network, electrical system, and security guard at the gate (Guest OS, kernel, virtualized hardware, hypervisor overhead). Building a new apartment means paying for a completely duplicate set of foundations and structures, which is highly resource-intensive.

A container, on the other hand, is like renting a partitioned office space within a single shared commercial office building. Every office (container) shares the main building's structural foundation, central plumbing, electricity, and security system (the Host OS Kernel). However, each office has its own locked door, separate phone line, and custom desk layout (namespaces and control groups). This sharing of core building systems allows you to set up hundreds of offices in the space it would take to build just a few individual apartment blocks, with lightning-fast startup and minimal resource overhead.

The client-server architecture of Docker operates like a high-end restaurant:
- **The Docker Client (CLI):** This is the customer who places orders. It does not prepare the food; it simply hands a formatted slip (API request) to the server.
- **The Docker Daemon (`dockerd`):** This is the kitchen staff and master chef. It runs in the background on the host system, intercepts API requests, manages raw materials (images), and cooks the dishes (running containers).
- **The Registry (Docker Hub):** This is the wholesale pantry containing bulk ingredients and standardized recipes from around the world.

### Architectural & Flow Blueprint
The following diagrams demonstrate the client-server operational model and the complete state transition pipeline of a container lifecycle:

```mermaid
graph TD
    subgraph ClientSpace [Client Space]
        CLI[Docker CLI] -->|REST API over UNIX Socket| Daemon
    end
    subgraph HostSpace [Docker Host Daemon]
        Daemon[Docker Daemon - dockerd] -->|Manages| Images[(Images)]
        Daemon -->|Executes| Containers[Containers]
    end
    subgraph External [Registry Space]
        Registry[Docker Hub / Registry] <-->|Pull/Push| Daemon
    end
```

The diagram below details how the process lifecycle of a container moves across distinct states inside the kernel:

```mermaid
stateDiagram-v2
    [*] --> Created : docker create
    Created --> Running : docker start
    Running --> Paused : docker pause
    Paused --> Running : docker unpause
    Running --> Stopped : docker stop / SIGTERM
    Running --> Exited : Process Completes / Crash
    Stopped --> Running : docker start
    Stopped --> [*] : docker rm
    Exited --> [*] : docker rm
```

### Core Mechanics & Under-the-Hood Operations
Under the hood, Docker relies on several fundamental Linux kernel features to maintain isolation and enforce operational resource limits:
1. **Namespaces (Isolation Layer):**
   Namespaces restrict what a process can *see*. When Docker launches a container, it instantiates isolated namespaces for the process:
   - **pid (Process ID):** Restricts process visibility. Process ID 1 inside the container is mapped to an unprivileged child process ID on the host.
   - **net (Network):** Provides individual network devices, IP addresses, port binds, and routing tables.
   - **mnt (Mount):** Isolates the container filesystem mount points from the host system.
   - **ipc (Interprocess Communication):** Prevents shared memory segments or message queues from being accessed outside the container.
   - **uts (Unix Timesharing):** Allows the container to define its own hostname and domain name.
   - **user (User IDs):** Maps user and group IDs within a container to different IDs on the host.

2. **Control Groups / cgroups (Resource Constraints):**
   Cgroups govern what a process can *use*. They prevent any single container from executing a Denial-of-Service (DoS) on the host's shared physical hardware. Cgroups control maximum thresholds for CPU shares, memory limits, Block I/O, and PID counts.

3. **Lifecycle States:**
   - **Created:** The container is defined, and namespaces are allocated, but no processes are yet running inside the container namespace.
   - **Running:** The primary process (PID 1) is active and running inside the container namespace.
   - **Paused:** The kernel suspends all processes inside the container namespaces (using the cgroups freezer subsystem). CPU cycles fall to zero, but memory contents remain intact.
   - **Stopped:** The container's primary process is sent a `SIGTERM` signal, followed by `SIGKILL` if it fails to exit within a grace period. Namespaces are closed, but the filesystem modifications remain stored.
   - **Exited:** The primary process has terminated naturally (e.g., exit code 0) or crashed, releasing system CPU and RAM allocations.

### Deep-Dive Explanations (Advanced Context)
<details>
<summary>Deep Dive: Socket Communication and REST API</summary>
The Docker CLI is fundamentally a wrapper around a REST client. When you run a command like `docker ps`, the CLI translates your command into an HTTP GET request to `/v1.43/containers/json` and sends it via the UNIX domain socket located at `/var/run/docker.sock`. Because it is an HTTP-based REST API, you can query and manage the Docker daemon using standard networking utilities like `curl` if you have appropriate read/write file permissions on the socket file.
</details>

<details>
<summary>Deep Dive: Docker Daemon Thread Initialization</summary>
When the system daemon `dockerd` starts, it initializes several subsystems: the volume drivers, default bridge networks, and `containerd`. The `containerd` subsystem is an industry-standard container runtime that acts as a supervisor, managing the complete execution lifecycle of container processes. It relies on a lower-level tool called `runc` to interface directly with the Linux kernel namespaces, cgroups, and storage layers during container creation.
</details>

### Common Pitfalls & Troubleshooting
#### Pitfall 1: Daemon Communication and Socket Permission Failures
*   **Error Message:**
    ```text
    Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?
    ```
*   **Root Cause:** The Docker CLI interacts with the background Docker daemon via a UNIX domain socket (`/var/run/docker.sock`). This socket is owned by `root` and, by default, accessible only to members of the `docker` group. Running commands without proper permissions or with a stopped service causes this communication failure.
*   **Resolution CLI Command:**
    ```bash
    # Verify the daemon status via systemctl
    sudo systemctl status docker
    # Add the current user to the docker system group to bypass root requirements
    sudo usermod -aG docker $USER
    # Re-evaluate the group membership inside the current terminal session
    newgrp docker
    ```

#### Pitfall 2: Silent Exit with Code 137 (OOM Killer)
*   **Error Message:**
    ```text
    docker ps -a
    STATUS: Exited (137) 3 minutes ago
    ```
*   **Root Cause:** Exit code `137` indicates that the container process was terminated by the host system's kernel because it exceeded its allocated memory limits. The Out-of-Memory (OOM) killer steps in to protect the host's stability.
*   **Resolution CLI Command:**
    ```bash
    # Inspect the container metrics and verify memory consumption
    docker inspect app-worker --format='{{.State.OOMKilled}}'
    # Allocate realistic memory constraints via cgroups during execution
    docker run -d --name app-worker -m 512m --memory-swap 1g alpine sleep 100
    ```

#### Pitfall 3: Container Naming Collisions
*   **Error Message:**
    ```text
    docker: Error response from daemon: Conflict. The container name "/app-worker" is already in use by container "a1b2c3d4e5f6...". You have to remove (or rename) that container to be able to reuse that name.
    ```
*   **Root Cause:** Docker enforces global name uniqueness for all active and inactive containers on a single host. If a container was previously stopped but not removed, attempting to spin up a new container with the same `--name` will trigger a name collision error.
*   **Resolution CLI Command:**
    ```bash
    # Identify and stop/remove the conflicting container
    docker rm -f app-worker
    # Alternatively, ensure the container is removed automatically upon exit
    docker run -d --rm --name app-worker alpine sleep 100
    ```

### Traceability Check
Before proceeding to the Hands-On Labs, ensure you have committed the following concepts and commands to memory:
- Virtual Machine virtualization uses hypervisors while Containers use the host's shared kernel.
- Namespaces provide visibility isolation; cgroups enforce physical resource constraints.
- Containers go through states: Created, Running, Paused, Stopped, and Exited.
- `docker run` starts containers; `-d` detaches process; `--name` names containers; `--restart` controls recovery.
- `docker ps -a` reveals all states; `docker inspect` dumps raw JSON metadata; `docker logs` tracks output.
""",
        "commands": r"""
### Command & Syntax Reference

#### 1. Running a Container
```bash
docker run [OPTIONS] IMAGE [COMMAND] [ARG...]
```
*   **Parameter Anatomy:**
    - `-d` (Detached Mode): Runs the container in the background and prints the container ID.
    - `-p [HOST_PORT]:[CONTAINER_PORT]`: Maps a host port to a container port (e.g., `-p 8080:80`).
    - `--name [NAME]`: Assigns an explicit string name to the container. Allows easy targeting in downstream commands instead of random hashes.
    - `--restart [POLICY]`: Configures the container's recovery behavior. Valid options are `no`, `on-failure[:max-retries]`, `always`, and `unless-stopped`.
    - `-m [LIMIT]` (Memory Limit): Restricts RAM utilization (e.g., `256m`, `1g`).
    - `--cpus [LIMIT]`: Restricts the fractional CPU utilization (e.g., `0.5` restricts processing to half of a core).

#### 2. Lifecycle Transitions
```bash
docker create [OPTIONS] IMAGE [COMMAND] [ARG...]
```
*   **Parameter Anatomy:** Sets up the container filesystem and parameters but does not launch the process. Returns a container ID.

```bash
docker start CONTAINER [CONTAINER...]
```
*   **Parameter Anatomy:** Starts one or more stopped or newly created containers.

```bash
docker pause CONTAINER [CONTAINER...]
```
*   **Parameter Anatomy:** Suspends all processes within the specified container using cgroups freezer.

```bash
docker unpause CONTAINER [CONTAINER...]
```
*   **Parameter Anatomy:** Resumes execution of a paused container.

```bash
docker stop [OPTIONS] CONTAINER [CONTAINER...]
```
*   **Parameter Anatomy:** Sends `SIGTERM`, then `SIGKILL` after a grace period (default 10s).

#### 3. Querying and Inspecting State
```bash
docker ps [OPTIONS]
```
*   **Parameter Anatomy:**
    - `-a` (All): Displays both currently running and stopped/failed containers.
    - `-q` (Quiet): Returns only container IDs, useful for automation scripts.
    - `-f [FILTER]`: Filters output based on condition pairs (e.g., `-f status=exited`).

```bash
docker inspect [OPTIONS] CONTAINER|IMAGE
```
*   **Parameter Anatomy:**
    - `-f, --format [TEMPLATE]`: Parses the low-level JSON configuration using Go-template syntax (e.g., `--format='{{.NetworkSettings.IPAddress}}'`).

```bash
docker stats [OPTIONS] [CONTAINER...]
```
*   **Parameter Anatomy:** Displays a live stream of container resource usage statistics.

#### 4. Cleanups
```bash
docker rm CONTAINER [CONTAINER...]
```
*   **Parameter Anatomy:** Removes one or more stopped containers. Use `-f` (force) to stop and remove running containers.

```bash
docker rmi IMAGE [IMAGE...]
```
*   **Parameter Anatomy:** Deletes one or more images from local cache storage.

```bash
docker system prune [OPTIONS]
```
*   **Parameter Anatomy:** Cleans up dangling images, stopped containers, unused networks, and build caches. Use `-a` to remove all unused images and not just dangling ones.
""",
        "examples": r"""
### Real-World Examples

#### Example 1: Launching a High-Availability Service Stack Container
**Situation:** A microservice worker must process background tasks, restart automatically if it crashes, and limit its memory utilization to 128 Megabytes.
**Action:** Launch a detached container with explicit names, resource constraints, and restart policies, then query its health:
```bash
# Launch background worker running alpine with strict memory constraints and restart policy
docker run -d \
  --name task-processor \
  --restart always \
  -m 128m \
  alpine sh -c "while true; do echo 'Processing background task queue...'; sleep 10; done"

# Confirm the memory limit and restart policy in metadata
docker inspect task-processor --format='Memory: {{.HostConfig.Memory}} bytes | Restart: {{.HostConfig.RestartPolicy.Name}}'
```

#### Example 2: Managing and Monitoring Lifecycle State Changes
**Situation:** An operator wants to temporarily pause a computationally intensive task to free up host resources without destroying the container's progress.
**Action:** Create a container, transition it through paused and active states, and monitor its system stats:
```bash
# Start container running a long-running calculation
docker run -d --name stress-app alpine sh -c "while true; do echo 'Calculating math...'; sleep 1; done"

# Pause the container execution
docker pause stress-app

# Inspect the container status to verify it is paused
docker inspect stress-app --format='{{.State.Status}}'

# Resume container execution
docker unpause stress-app
```

#### Example 3: Extracting Diagnostic Log Buffers for Debugging
**Situation:** A runtime server container is misbehaving, and the team needs to audit the last 5 messages and verify if there are any error streams without scrolling through millions of lines of standard logs.
**Action:** Query the container logs filtering for specific output counts:
```bash
# Run a noisy utility container
docker run -d --name log-generator alpine sh -c "for i in 1 2 3 4 5; do echo 'Log index '\$i; sleep 1; done"

# Fetch exactly the last 3 logs
docker logs --tail 3 log-generator

# Clean up the container
docker rm -f log-generator
```

#### Example 4: Diagnosing Memory Consumption on Live Environments
**Situation:** A container is running a performance test, and SREs need to trace CPU usage percentages, memory utilization, and network traffic in real time.
**Action:** Query `docker stats` using custom format strings to render streamlined columns of live resource telemetry:
```bash
# Run a background calculation-heavy workload
docker run -d --name stress-calc alpine sh -c "dd if=/dev/urandom of=/dev/null"

# Trace telemetry in a simplified table output
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" stress-calc

# Stop and clean up the test
docker rm -f stress-calc
```

#### Example 5: Recovering Host Storage through Selective Purges
**Situation:** Disk space on a development workstation is fully exhausted due to hundreds of stopped containers and unused container cache layers.
**Action:** Run a force prune command to clean up all dangling and unused systems safely:
```bash
# Run a complete system prune to free disk blocks immediately
docker system prune -a -f
```
""",
        "exercise": r"""
### Hands-On Labs

#### Lab 1: Managing Container Lifecycles
**Objective:** Practice launching, monitoring, and cleaning up a target container.
**Tasks:**
1. Start a detached container named `dns-probe` using `alpine:latest` executing the command `ping 8.8.8.8`.
2. Retrieve the last 15 lines of the container's logs to verify successful pings.
3. Stop the container using `docker stop` and inspect its status with `docker ps -a` to confirm it exited.
4. Remove the container manually using `docker rm`.
5. Re-run a container named `dns-probe` again to ensure no naming conflicts remain.

#### Lab 2: Container State Transitions (Pause and Resume)
**Objective:** Learn how to freeze container execution states without terminating processes.
**Tasks:**
1. Start a container using `python:3.10-slim` that prints numbers 1 to 100 with a 1-second delay: `python -c "import time; [print(f'Count: {i}') or time.sleep(1) for i in range(1, 101)]"`.
2. View its status using `docker ps` and see that it is running.
3. Run `docker pause` on the container, and verify its state transition using `docker inspect`.
4. Open a terminal and verify that log printing has stopped.
5. Run `docker unpause` and confirm that execution resumes exactly where it left off.

#### Lab 3: Troubleshooting Runtime Environments
**Objective:** Debug runtime issues by entering an active container environment.
**Tasks:**
1. Run a detached background `nginx:alpine` container named `web-debug` mapping host port `8080` to container port `80`.
2. Execute an interactive shell session (`sh`) inside the running container context using `docker exec`.
3. Locate the default Nginx index file at `/usr/share/nginx/html/index.html` and append the text "Hello DevOps" to it.
4. Run `ps aux` inside the container to see the processes running inside the isolated namespace.
5. Exit the container shell session and run `curl http://localhost:8080` to verify your changes.

#### Lab 4: Runtime Configuration Audits
**Objective:** Extract internal metadata to verify state parameters and config options.
**Tasks:**
1. Start a container named `audit-target` running `redis:alpine`.
2. Run a `docker inspect` query to find its state configuration and determine its `Running` status (True/False).
3. Find the exact path where the container's standard output log file is saved on the host filesystem using Go-template formatting.
4. Locate the CPU and Memory configurations in the HostConfig section of the inspect output.
5. Clean up the container by stopping and removing it.

#### Lab 5: Container Resource Profiling under Load
**Objective:** Track the impact of workload execution on container resource constraints.
**Tasks:**
1. Run a helper container that performs a system stress routine (e.g., running `sha512sum /dev/urandom` inside an alpine container).
2. Open your terminal metrics viewer using `docker stats` and observe the CPU/Memory percentages.
3. Record how the numbers fluctuate under active computational load.
4. Stop the container to bring the host CPU utilization back to idle.
5. Clean up any remaining container resources.
""",
        "insight": r"""
### Interview Q&A

#### Q1: What is the primary difference between how a Virtual Machine and a Container share host resources?
* **Answer:** A VM packages a complete guest operating system and virtualizes hardware using a hypervisor, which translates instructions to the physical CPU. A container shares the host system's kernel directly, isolating processes through kernel namespaces and managing resource limits via cgroups. This results in minimal CPU and memory overhead compared to a VM.

#### Q2: What is the functional difference between `docker stop` and `docker kill`?
* **Answer:** `docker stop` sends a `SIGTERM` signal to the primary container process (PID 1), allowing it to clean up open files, finish active requests, and shut down gracefully. If it doesn't shut down within a grace period (default 10s), it sends `SIGKILL`. `docker kill` bypasses the graceful phase and immediately sends `SIGKILL` to terminate the process instantly.

#### Q3: Where is data stored inside a container, and what happens to it when the container is deleted?
* **Answer:** Data is written to a thin, writeable container layer that sits on top of the immutable image layers. This writeable layer is tightly coupled to the container's lifecycle. When the container is deleted (`docker rm`), its writeable layer is permanently destroyed, and any data stored inside it is lost unless persistent storage (volumes/bind mounts) was utilized.

#### Q4: What is the role of Linux namespaces and cgroups in containerization?
* **Answer:** They are the underlying Linux kernel technologies that make containers possible. **Namespaces** provide process-level isolation, hiding resources (like processes, network interfaces, filesystems, and IPC) from other containers. **Control groups (cgroups)** enforce resource governance, restricting how much CPU, memory, network bandwidth, or disk I/O a container can consume.

#### Q5: What is the difference between the 'Stopped' and 'Paused' container states?
* **Answer:** In the 'Stopped' state, the primary container process (PID 1) has exited and is no longer present in the host's process table. The container filesystem remains, but CPU and memory allocations are fully released. In the 'Paused' state, container processes are kept active in memory but frozen by the kernel's scheduler. They consume memory but zero CPU cycles, and resume execution instantly when unpaused.
"""
    },
    {
        "id": 2,
        "title": "Module 2: Containerization Mechanics & Writing Optimized Dockerfiles",
        "theory": r"""
### Guided Conceptual Walkthrough
Think of building a Docker image like baking a cake using a pre-packaged recipe. The `Dockerfile` is the recipe card, detailing step-by-step instructions. Every instruction (e.g., adding flour, adding milk, baking, adding icing) creates a physical layer on top of the last. 

If you make 10 cakes a day, you do not want to go to the store and grind the wheat into flour every single time. Instead, you pre-mix and store the dry base ingredients in your pantry. In Docker, this is **Layer Caching**. When you rebuild an image after a minor change in your application source code, Docker reuses the already completed dry-mix layers (installing system dependencies) and only executes the final step of copying the updated source code.

To do this efficiently, we use **Multi-Stage Builds**. This is like having a messy prep kitchen where you chop raw vegetables, peel skins, and boil stocks (the "Builder" stage with heavy compiler tools), and a clean dining room where you only bring the finalized, plated meal to the guest (the "Runtime" stage containing only the compiled binary, completely devoid of heavy, insecure compilation tools).

### Architectural & Flow Blueprint
The following schema visualizes how Docker walks through the layer cache and how cache invalidation propagates down the build chain:

```mermaid
graph TD
    subgraph Build [Docker Build Layer Cache Flow]
        step1["Step 1: FROM alpine:3.18<br>(Layer ID: 1a2b - CACHED)"]
        step2["Step 2: WORKDIR /app<br>(Layer ID: 3c4d - CACHED)"]
        step3["Step 3: COPY package.json .<br>(Layer ID: 5e6f - CACHED)"]
        step4["Step 4: RUN npm install<br>(Layer ID: 7g8h - CACHED)"]
        step5["Step 5: COPY src/ .<br>(File Change Detected - CACHE INVALIDATED)"]
        step6["Step 6: EXPOSE 3000<br>(New Layer ID: k1l2 - REBUILT)"]
        step7["Step 7: CMD ['npm', 'start']<br>(New Layer ID: m3n4 - REBUILT)"]

        step1 --> step2
        step2 --> step3
        step3 --> step4
        step4 --> step5
        step5 --> step6
        step6 --> step7
    end
```

*Rule of Cache Invalidation:* Once any step in the Dockerfile is invalidated (due to a file change in `COPY` or a modified script string), every single subsequent step below it is forced to rebuild from scratch.

### Core Mechanics & Under-the-Hood Operations
Every line in a `Dockerfile` corresponds to an immutable filesystem diff or a metadata change:
1. **Layer Creation:**
   Commands like `FROM`, `RUN`, `COPY`, and `ADD` create physical, read-only layers. Commands like `ENV`, `EXPOSE`, `CMD`, and `ENTRYPOINT` do not create heavy filesystem layers; instead, they alter the image's JSON metadata configuration.
2. **BuildKit Build Engine:**
   Modern Docker installations utilize **BuildKit** as the default compilation engine. BuildKit runs builds in parallel where dependencies allow, detects unused build stages, and enables advanced cache export/import options.
3. **CMD vs ENTRYPOINT Interaction:**
   `ENTRYPOINT` defines the executable binary that always runs when the container starts. `CMD` provides default arguments or parameters to that executable.
   - **Exec Form:** Written as a JSON array (e.g., `ENTRYPOINT ["/bin/ping", "8.8.8.8"]`). This runs directly as PID 1 without an intermediate shell, allowing standard signals like `SIGTERM` to propagate correctly.
   - **Shell Form:** Written as a raw string (e.g., `ENTRYPOINT /bin/ping 8.8.8.8`). This starts `/bin/sh -c` as PID 1, and the application runs as a child process, which prevents it from receiving OS signals directly.

### Deep-Dive Explanations (Advanced Context)
<details>
<summary>Deep Dive: COPY vs ADD Instructions</summary>
While both instructions copy files into the container image filesystem, they have distinct behaviors. `COPY` is straightforward and preferred for copying local files and directories. `ADD` includes advanced capabilities: it can pull files from remote URLs and automatically extract local tar archives (e.g., `.tar`, `.tar.gz`) into the target directory. Because of this magic, `ADD` should be used cautiously to avoid pulling untrusted remote assets or bloated archives.
</details>

<details>
<summary>Deep Dive: Exec Form Signal Trapping (PID 1)</summary>
When running an application in shell form, the shell process (`/bin/sh`) becomes PID 1. When you trigger `docker stop`, the daemon sends `SIGTERM` to PID 1, but most shells do not forward signals to their child processes. As a result, your application never receives the shutdown signal, waits for 10 seconds, and is forcefully terminated via `SIGKILL`. Using the JSON array exec form ensures your application process runs as PID 1 directly and can capture graceful shutdown hooks.
</details>

### Common Pitfalls & Troubleshooting
#### Pitfall 1: Bloated Images due to Separate RUN Steps
*   **Error Message:** Image builds successfully but is unexpectedly large (e.g., 800MB) for a simple script utility.
*   **Root Cause:** Running separate `RUN apt-get update` and `RUN apt-get install` commands creates a separate layer that stores the entire temporary apt cache index. Even if you clean the cache in a separate `RUN rm -rf /var/lib/apt/lists/*` command, that data remains locked in the parent layer forever.
*   **Resolution CLI Command / Dockerfile:**
    ```dockerfile
    # INCORRECT:
    # RUN apt-get update
    # RUN apt-get install -y curl
    # RUN rm -rf /var/lib/apt/lists/*

    # CORRECT (Chained in a single layer):
    RUN apt-get update && apt-get install -y \
        curl \
     && rm -rf /var/lib/apt/lists/*
    ```

#### Pitfall 2: Shell Expansion Failure in Exec Form
*   **Error Message:**
    ```text
    web_1  | env: 'sh': No such file or directory
    # or env variables print literally as $ENV_VAR inside container outputs
    ```
*   **Root Cause:** The exec form (`["echo", "$VAR"]`) does not invoke a shell. Therefore, environment variable expansion does not occur automatically, and `$VAR` is printed as a literal string.
*   **Resolution CLI Command / Dockerfile:**
    ```dockerfile
    # Correctly format the instruction to use a shell explicitly within the exec array:
    CMD ["sh", "-c", "echo My Var is: $VAR"]
    ```

#### Pitfall 3: Missing Run Executable Permissions
*   **Error Message:**
    ```text
    docker: Error response from daemon: failed to create task for container: failed to create shim task: OCI runtime create failed: runc create failed: unable to start container process: exec: "./entrypoint.sh": permission denied: unknown.
    ```
*   **Root Cause:** When files are copied from a host system to a container using `COPY`, they carry over the file permission bits of the host. If your local script file `entrypoint.sh` is not marked as executable (`chmod +x`), the container's execution engine will fail to start the process.
*   **Resolution CLI Command / Dockerfile:**
    ```dockerfile
    # Fix via local terminal before build:
    # chmod +x entrypoint.sh

    # Or force execution permissions inside the Dockerfile compilation:
    COPY entrypoint.sh .
    RUN chmod +x entrypoint.sh
    ENTRYPOINT ["./entrypoint.sh"]
    ```

### Traceability Check
Before proceeding, ensure you have verified the following items:
- Every instruction in a Dockerfile represents a read-only filesystem layer.
- Changing files early in a Dockerfile invalidates all subsequent layer caches.
- Multi-stage builds use `FROM ... AS ...` to segregate build tools from runtime execution environments.
- Exec form JSON formatting is required for proper signal transmission inside containers.
- Standard CMD parameters append directly to ENTRYPOINT commands at runtime.
""",
        "commands": r"""
### Command & Syntax Reference

#### Dockerfile Template & Anatomy
Here is a fully functional, production-ready multi-stage Dockerfile template for a containerized Node.js application:

```dockerfile
# Stage 1: Build & compilation environment
FROM node:18-alpine AS builder
WORKDIR /usr/src/app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Minimal production runtime
FROM node:18-alpine
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /usr/src/app/dist ./dist
COPY --from=builder /usr/src/app/package*.json ./
RUN npm ci --only=production
USER node
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

##### **Dockerfile Anatomy & Structural Rules**
*   `FROM node:18-alpine AS builder`:
    - **Syntax Rules:** Every valid Dockerfile must start with a `FROM` instruction (except for global `ARG` declarations).
    - **Anatomy:** Specifying `AS builder` defines a named intermediate compilation stage. The base image `node:18-alpine` uses an Alpine Linux distribution to minimize the footprint of the build stage.
*   `WORKDIR /usr/src/app`:
    - **Anatomy:** Sets the execution context for any subsequent `RUN`, `CMD`, `ENTRYPOINT`, `COPY`, and `ADD` instructions. If the directory does not exist, Docker creates it automatically.
*   `COPY package*.json ./`:
    - **Anatomy:** Copies the dependency manifests from the host's build context into the workdir of the container image. Using wildcards (`package*.json`) ensures both `package.json` and `package-lock.json` are captured, keeping dependencies locked to exact versions.
*   `RUN npm ci`:
    - **Anatomy:** Runs a clean, automated install of package dependencies. Placed *before* copying the application source code to optimize BuildKit caching.
*   `COPY --from=builder /usr/src/app/dist ./dist`:
    - **Anatomy:** The `--from=builder` flag targets the named first stage, copying *only* the compiled Javascript bundles into the fresh production stage.
*   `USER node`:
    - **Anatomy:** Instructs the runtime process to run under an unprivileged user space account instead of the default `root` user, drastically shrinking the security risk profile.
*   `EXPOSE 3000`:
    - **Anatomy:** Documentational metadata. It indicates that the application process inside the container intends to listen on port `3000`. It does *not* publish or map the port automatically; that requires `-p` at runtime.
*   `CMD ["node", "dist/index.js"]`:
    - **Anatomy:** The execution instruction using the **exec form** (JSON array). Unlike the **shell form** (`CMD node dist/index.js`), the exec form runs the executable directly without invoking a system shell (`/bin/sh -c`), ensuring system signals like `SIGTERM` propagate correctly.

#### 1. Building Images
```bash
docker build [OPTIONS] PATH
```
*   **Parameter Anatomy:**
    - `-t [TAG]` (Tag): Assigns a name and optional tag in the `name:tag` format (e.g., `-t backend-api:1.0.0`).
    - `-f [FILE]` (Dockerfile): Specifies an alternative name or path for the Dockerfile (defaults to `./Dockerfile`).
    - `--build-arg [KEY=VALUE]`: Passes dynamic build-time variables (defined via `ARG` in the Dockerfile) into the build context.
    - `--no-cache`: Forces the engine to ignore cached layers and rebuild the image from scratch.

#### 2. Image Auditing
```bash
docker history [OPTIONS] IMAGE
```
*   **Parameter Anatomy:**
    - Displays each layer size, creator instruction, and configuration metadata history. Use `--no-trunc` to read the full commands.
""",
        "examples": r"""
### Real-World Examples

#### Example 1: Creating a Cached Python Environment Image
**Situation:** You want to package a Python microservice with dependencies but avoid long compilation waits on every minor code edit.
**Action:** Build a multi-layered Dockerfile that separates the `requirements.txt` installation from the application source code copy step:
```dockerfile
FROM python:3.10-slim

WORKDIR /usr/src/app

# Install system requirements
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
 && rm -rf /var/lib/apt/lists/*

# Copy dependency manifests first to leverage build cache
COPY requirements.txt .

# Install Python package dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy remaining application source
COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

#### Example 2: Compiling a Go Web Application using Multi-Stage Builds
**Situation:** You are deploying a compiled Go service. Compiling requires a 500MB Go SDK, but the output binary is only 15MB and runs on raw alpine.
**Action:** Write a multi-stage Dockerfile that discards the compilation environment after generating the final executable:
```dockerfile
# Stage 1: Build the binary in a heavy Go SDK context
FROM golang:1.20-alpine AS builder
WORKDIR /build
COPY go.mod ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o main .

# Stage 2: Deploy the binary in a clean, minimal image
FROM alpine:3.18
WORKDIR /app
# Retrieve only the compiled binary from Stage 1
COPY --from=builder /build/main .
EXPOSE 8080
CMD ["./main"]
```

#### Example 3: Running Multiple App Instances with Dynamic Environment Tags
**Situation:** You need to pass custom git commit hashes and target runtime profiles directly into the image structure at build-time.
**Action:** Define `ARG` instructions in the configuration file and pass them during image compilation commands:
```dockerfile
# Contents of Dockerfile
FROM alpine:3.18
ARG COMMIT_HASH="unknown"
ENV RELEASE_COMMIT=$COMMIT_HASH
CMD ["sh", "-c", "echo Deploying release commit \$RELEASE_COMMIT"]
```
```bash
# Execute build step passing the argument value
docker build --build-arg COMMIT_HASH="a7b8c9d" -t app-release:latest .
```

#### Example 4: ADD vs COPY for Packaging Compressed Applications
**Situation:** You have a local compressed archive containing static html files (`assets.tar.gz`) that must be extracted into an Nginx server container.
**Action:** Use the `ADD` command in the Dockerfile to extract the archive automatically during the build layer step:
```dockerfile
FROM nginx:alpine
# Automatically extracts assets.tar.gz into /usr/share/nginx/html/
ADD assets.tar.gz /usr/share/nginx/html/
EXPOSE 80
```

#### Example 5: Image Layer Audit & Inspection
**Situation:** You suspect that an image contains extremely large cached packages and want to audit its history to identify exactly which command is responsible for adding size.
**Action:** Run a `docker history` command to verify the size contributions of each layer:
```bash
# Build the local test image
docker build -t history-test - <<EOF
FROM alpine:3.18
RUN apk update && apk add curl
RUN rm -rf /var/cache/apk/*
EOF

# Audit the layer build history
docker history history-test
```
""",
        "exercise": r"""
### Hands-On Labs

#### Lab 1: Building a Layer-Cached Web Service
**Objective:** Understand how Docker's layer cache works by building and updating an image.
**Tasks:**
1. Create a workspace directory and write a basic `requirements.txt` containing the `flask` library.
2. Write a Dockerfile that copies `requirements.txt` and runs `pip install` before copying the rest of your app files.
3. Build the image: `docker build -t cache-demo:v1 .`.
4. Make a small text change to your app code and rebuild as `cache-demo:v2`.
5. Verify in the output logs that the package installation step bypassed downloading and used the cache.

#### Lab 2: Crafting a Multi-Stage Build
**Objective:** Optimize image sizes and keep build tools out of your final image.
**Tasks:**
1. Write a multi-stage Dockerfile containing a Go compilation stage (builder) and a clean alpine production stage.
2. Build the image using `docker build -t multi-stage:latest .`.
3. Compare the storage size of this image against a single-stage Go image using `docker images`.
4. Confirm the runtime image contains only necessary runtime assets.

#### Lab 3: Demystifying ENTRYPOINT and CMD Overrides
**Objective:** Learn how to combine ENTRYPOINT and CMD to create flexible utility containers.
**Tasks:**
1. Create a Dockerfile with `ENTRYPOINT ["ping"]` and `CMD ["127.0.0.1"]` (exec form).
2. Build the image with the tag `pinger:latest`.
3. Run the container with no arguments (`docker run pinger:latest`) and verify it pings localhost.
4. Run the container appending a target IP (`docker run pinger:latest 8.8.8.8`) and verify it overrides the default CMD.
5. Try to override the entrypoint to run a shell using `docker run --entrypoint sh pinger:latest -c "echo Hello"`.

#### Lab 4: Build-Time ARG vs Runtime ENV Configuration
**Objective:** Differentiate between variables used during image construction and those used during runtime execution.
**Tasks:**
1. Create a Dockerfile declaring an `ARG BUILD_VERSION` and an `ENV RUNTIME_ENV=production`.
2. Write a startup command in the Dockerfile that prints both values: `CMD echo Build: $BUILD_VERSION Runtime: $RUNTIME_ENV`.
3. Build the image passing `--build-arg BUILD_VERSION=v2.1` and tag it as `var-test`.
4. Run the container and analyze the printed logs.
5. Attempt to override the runtime environment variable during execution (`docker run -e RUNTIME_ENV=staging var-test`) and verify the output.

#### Lab 5: Secure Non-Root User Execution
**Objective:** Build secure images that execute processes under unprivileged user space permissions.
**Tasks:**
1. Write a Dockerfile starting with `alpine:latest`.
2. Run commands to create a user group `appgroup` and an unprivileged system user `appuser`.
3. Use `WORKDIR` to establish a workspace folder and set its ownership to `appuser` using `chown`.
4. Set the active user using `USER appuser`.
5. Build, run, and execute `whoami` inside the container to verify it is not running as root.
""",
        "insight": r"""
### Interview Q&A

#### Q1: Why do we separate the dependency installation step from the source code copying step in a Dockerfile?
* **Answer:** Docker builds images layer-by-layer and caches each layer. If any files change in a copy operation, the cache for that layer and all subsequent layers is invalidated. By copying only dependency list files first, the slow package installation step remains cached unless dependencies actually change, saving significant build time during code modifications.

#### Q2: What is the operational difference between `CMD` and `ENTRYPOINT` in a Dockerfile?
* **Answer:** `ENTRYPOINT` defines the executable binary that always runs when the container starts. `CMD` provides default arguments or parameters to that executable. Users can easily override the `CMD` values by appending arguments to the `docker run` command, whereas overriding the `ENTRYPOINT` requires an explicit `--entrypoint` flag.

#### Q3: How do build-time arguments (`ARG`) differ from runtime environment variables (`ENV`)?
* **Answer:** `ARG` variables are only available during the image build process (e.g., specifying version tags or compiler flags) and are not accessible once the container starts running. `ENV` variables persist within the image metadata and are available to the application process at runtime.

#### Q4: How do multi-stage builds help improve container security in production?
* **Answer:** Multi-stage builds allow you to use development dependencies, compilers, and debugging utilities in a builder stage, and copy only the compiled binaries or runtime files into a slim production stage. This reduces the image's footprint and minimizes the attack surface by ensuring no unnecessary shell utilities or compilers are present in production.

#### Q5: Why is using the `latest` image tag discouraged in production deployments?
* **Answer:** The `latest` tag is mutable and dynamic. When a base image or application dependencies are updated, the registry updates `latest` to point to the new image. If a system pulls the image during auto-healing or scaling, it might fetch an untested version, leading to inconsistent application states and hard-to-debug failures across your infrastructure.
"""
    },
    {
        "id": 3,
        "title": "Module 3: Single-Host Network Drivers & Data Persistence Engines",
        "theory": r"""
### Guided Conceptual Walkthrough
Managing storage inside containers is like renting a hotel room:
- **Bind Mounts:** This is like bringing your own physical luggage from home. You map a specific folder on your host machine directly into the container. When you make changes to files in your IDE on your host, they instantly sync inside the room. This is optimal for local code development.
- **Named Volumes:** This is like utilizing a heavy safe built into the hotel wall. You don't know exactly where the gears and bolts are on the host filesystem (though Docker stores it under `/var/lib/docker/volumes/`), but it is highly secure, managed entirely by the hotel, and stays safe even if they remodel the room (delete the container). This is best for database storage.
- **Tmpfs Mounts:** This is like using a dry-erase board in the room. You can write notes on it extremely fast (it writes directly to host system RAM), but the second the power goes out or you check out (the container stops), the board is wiped completely clean.

For networks, think of communication boundaries:
- **Bridge Network:** A private inter-com network set up specifically inside your office. Every room gets its own internal extension (a private IP like `172.17.0.2`). They can call each other, but if an outsider wants to connect, you must explicitly forward a public phone line (port mapping `-p`).
- **Host Network:** Taking off the office doors and walls entirely. The container shares the host system's network stack directly. If the app listens on port `80`, it occupies port `80` on the physical host directly, bypassing any routing and offering raw speed.
- **None Network:** Placing a container in solitary confinement. There are no lines, no interfaces, and no external contacts, keeping processing entirely isolated.

### Architectural & Flow Blueprint
The following schema visualizes both storage mounts and network drivers running on a single physical host:

```mermaid
graph TD
    subgraph HostSystem [Docker Host System]
        subgraph NetDrivers [Network Drivers]
            bridge[Bridge Network - Default docker0 / IPs: 172.17.0.0/16]
            host_net[Host Network - Shares Host Interfaces]
            none_net[None Network - Fully Isolated Loopback]
        end

        subgraph StorageDrivers [Storage Subsystems]
            host_dir[/Host Path: /data/db\] -->|Bind Mount| ContainerA[Container A]
            vol_dir[(Named Volume: pg_data)] -->|Volume Mount| ContainerB[Container B]
            ram_dir[Host RAM Memory] -->|Tmpfs Mount| ContainerC[Container C]
        end
    end
```

### Core Mechanics & Under-the-Hood Operations
Let's analyze the internal mechanics of networking and storage:

1. **Network Engines:**
   - **Bridge:** Docker creates a virtual interface named `docker0` on the host kernel. When a container starts in bridge mode, Docker assigns a virtual ethernet pair (`veth` pair), routing one end inside the container's network namespace as `eth0` and attaching the other end to `docker0`. An internal network daemon configures firewall rules using `iptables` to perform Network Address Translation (NAT) and manage port mapping.
   - **Host:** Bypasses the network namespace allocation step. The container processes attach directly to the host's physical network adapters, avoiding virtual network mapping layers.
   - **None:** Instantiates only a loopback interface (`127.0.0.1`), disconnecting the container from all external network routing tables.

2. **Storage Subsystems:**
   - **Bind Mounts:** Standard UNIX namespace mounts. The filesystem mount point inside the container points directly to the host inode, allowing concurrent, bidirectional read/write actions.
   - **Named Volumes:** Docker provisions directories within `/var/lib/docker/volumes/` on the host. Because file ownership permissions are managed internally, named volumes are highly secure, reliable, and decoupled from host filesystem specifics.
   - **Tmpfs Mounts:** Writes directly to the host's kernel system RAM cache using a temporary directory, completely bypassing physical disk writes.

### Deep-Dive Explanations (Advanced Context)
<details>
<summary>Deep Dive: Docker Bridge DNS Resolution</summary>
When utilizing the default bridge network (`bridge`), container-to-container communication via hostnames is disabled. Containers must communicate using explicit IP addresses. However, when you create a *custom* bridge network (e.g., `docker network create my-net`), Docker automatically provisions an embedded DNS server at `127.0.0.11` inside each container namespace. This allows containers to resolve other containers dynamically using their assigned container names.
</details>

<details>
<summary>Deep Dive: Tmpfs Mount Security and Limitations</summary>
Tmpfs mounts are exclusive to Linux host environments and cannot write to persistent host filesystems. They are invaluable for storing sensitive files, like decryption keys, SSL certificates, or session caches, because they ensure that data is never written to disk, preventing physical storage leaks.
</details>

### Common Pitfalls & Troubleshooting
#### Pitfall 1: Port Allocation Conflicts in Host Mode
*   **Error Message:**
    ```text
    docker: Error response from daemon: driver failed programming external connectivity on endpoint web-app: Bind for 0.0.0.0:8080 failed: port is already allocated.
    ```
*   **Root Cause:** When running a container on the `host` network, port mapping (`-p`) is bypassed, and the container binds directly to host interfaces. If you attempt to run multiple container instances on the same host network that attempt to listen on the same port, a TCP bind conflict will occur.
*   **Resolution CLI Command:**
    ```bash
    # Reconfigure the internal application port or bind the container to a bridge network mapping different host ports:
    docker run -d --network bridge -p 9090:80 --name web-app nginx:alpine
    ```

#### Pitfall 2: Host Path Synchronization Permissions (Bind Mounts)
*   **Error Message:** Files created by a container process inside a bind mount cannot be edited or deleted on the host without `sudo` access.
*   **Root Cause:** Inside a container, processes often run as the `root` user by default. Any file written to a bind mount is created with `root:root` ownership on the host filesystem.
*   **Resolution CLI Command:**
    ```bash
    # Run the container specifying the local user ID and group ID:
    docker run -d --user "$(id -u):$(id -g)" -v "$(pwd)"/app:/app alpine touch /app/test_file.txt
    ```

#### Pitfall 3: Directory Shadowing in Volume Mounts
*   **Error Message:** Files that were present inside a container's target directory (e.g., `/usr/share/nginx/html/`) suddenly disappear when a bind mount is attached.
*   **Root Cause:** If you attach a bind mount or volume containing files (or empty folders) to a container directory, the mounted volume's content completely overlays and hides the container's pre-existing directory contents.
*   **Resolution CLI Command:**
    ```bash
    # Ensure you are not mounting an empty host folder over directory-critical files, or use named volumes which automatically copy pre-existing container data to the volume on initial mount:
    docker run -d --name secure-web -v nginx_assets:/usr/share/nginx/html nginx:alpine
    ```

### Traceability Check
Ensure you have committed the following concepts and commands to memory:
- Bridge networks assign private subnets; Host networks bypass namespaces; None networks isolate.
- Custom bridge networks provide automatic container name DNS resolution.
- Named volumes are stored in `/var/lib/docker/volumes/` and persist across lifecycle events.
- Bind mounts link directly to absolute host paths and are perfect for development.
- Tmpfs mounts run in RAM and are wiped instantly when the container exits.
""",
        "commands": r"""
### Command & Syntax Reference

#### 1. Volume Management
```bash
docker volume create [OPTIONS] [VOLUME]
```
*   **Parameter Anatomy:** Instantiates a named storage volume managed by Docker's driver.

```bash
docker volume ls [OPTIONS]
```
*   **Parameter Anatomy:** Lists all active named volumes on the host.

```bash
docker volume inspect VOLUME [VOLUME...]
```
*   **Parameter Anatomy:** Returns detailed JSON metadata, including the physical mount path on the host (`Mountpoint`).

```bash
docker volume rm VOLUME [VOLUME...]
```
*   **Parameter Anatomy:** Deletes a volume. Only stopped or disconnected volumes can be removed.

#### 2. Network Management
```bash
docker network create [OPTIONS] NETWORK
```
*   **Parameter Anatomy:**
    - `-d, --driver [DRIVER]`: Specifies the driver type (`bridge`, `host`, `none`).

```bash
docker network connect [OPTIONS] NETWORK CONTAINER
```
*   **Parameter Anatomy:** Connects a running container dynamically to an active network.

```bash
docker network disconnect [OPTIONS] NETWORK CONTAINER
```
*   **Parameter Anatomy:** Severs a container's connection to a network.

```bash
docker network ls [OPTIONS]
```
*   **Parameter Anatomy:** Displays all local networks and their respective drivers.

#### 3. Mounting Syntax
```bash
# Volume Mount Syntax
docker run -v [VOLUME_NAME]:[CONTAINER_PATH] IMAGE

# Bind Mount Syntax
docker run -v [HOST_ABSOLUTE_PATH]:[CONTAINER_PATH] IMAGE

# Tmpfs Mount Syntax
docker run --tmpfs [CONTAINER_PATH]:[OPTIONS] IMAGE
```
""",
        "examples": r"""
### Real-World Examples

#### Example 1: Creating and Linking a Custom Bridge Network
**Situation:** You need two separate microservice containers to communicate securely with each other using names instead of unstable IP addresses.
**Action:** Create a custom bridge network and connect both containers to it:
```bash
# Create custom isolated bridge network
docker network create app-bridge

# Start database service attached to the network
docker run -d --name db-service --network app-bridge redis:alpine

# Start client pinging the database using its container name
docker run --name app-client --network app-bridge alpine ping -c 3 db-service
```

#### Example 2: Configuring a Secure Named Volume for PostgreSQL Database
**Situation:** A development database must retain its tables, records, and schemas across system restarts and container updates.
**Action:** Configure a named volume to decouple database storage from the container lifecycle:
```bash
# Create local volume
docker volume create pg_data

# Start postgres container mapping the volume
docker run -d \
  --name local-db \
  -e POSTGRES_PASSWORD=my_secure_pass \
  -v pg_data:/var/lib/postgresql/data \
  postgres:15-alpine
```

#### Example 3: Launching a High-Performance Cache using Tmpfs
**Situation:** An SRE team needs to process high-frequency transient application logs in a secure, non-persistent storage space with high read/write speeds.
**Action:** Launch an alpine container with a custom tmpfs mount for memory processing:
```bash
# Run container with RAM-backed storage mounted at /tmp/cache
docker run -d \
  --name fast-cache \
  --tmpfs /tmp/cache:size=64m,mode=1777 \
  alpine sleep 100
```

#### Example 4: Running a Performance-Critical Container on the Host Network
**Situation:** A high-frequency network daemon requires raw access to external ports without packet forwarding overhead from Nginx or bridge network drivers.
**Action:** Run the container specifying `host` network configuration:
```bash
# Spin up an Nginx instance directly sharing host networking interfaces
docker run -d --name host-web --network host nginx:alpine
```

#### Example 5: Development Workspace Bind Mount with Hot-Reloading
**Situation:** A developer wants to make real-time updates inside their local directory and see the changes reflect instantly inside the container.
**Action:** Declare a bind mount mapping the local project workspace to the internal app container directory:
```bash
# Run alpine container with current host working directory mounted to /src
docker run -it --name dev-sync -v "$(pwd)":/src alpine sh -c "echo 'Sync active'; ls /src"
```
""",
        "exercise": r"""
### Hands-On Labs

#### Lab 1: Isolating Services on Custom Bridge Networks
**Objective:** Verify that containers on the default bridge cannot communicate via names, while custom networks enable DNS-based service discovery.
**Tasks:**
1. Start two containers (`web1` and `web2`) running `alpine sleep 100` on the default bridge network.
2. Attempt to ping `web2` from inside `web1` using its container name: `docker exec -it web1 ping web2`. Note that this lookup fails.
3. Create a custom network: `docker network create prod-net`.
4. Connect both containers to `prod-net` using `docker network connect`.
5. Repeat the ping command from `web1` to `web2` and confirm DNS resolves successfully.

#### Lab 2: Ensuring Database Persistence via Named Volumes
**Objective:** Confirm that files stored inside named volumes persist across container deletions.
**Tasks:**
1. Create a named volume: `docker volume create persist-test`.
2. Start an alpine container mapping this volume to `/data`: `docker run -d --name writer -v persist-test:/data alpine sleep 100`.
3. Create a test file inside the mount: `docker exec writer sh -c "echo 'Persistent data' > /data/info.txt"`.
4. Force remove the container: `docker rm -f writer`.
5. Start a new container (`reader`) using the same volume and verify `/data/info.txt` is intact: `docker run --rm -v persist-test:/data alpine cat /data/info.txt`.

#### Lab 3: Local Development with Real-Time Bind Mount Syncing
**Objective:** Synchronize a local web index file with an active Nginx web server dynamically.
**Tasks:**
1. Create a local folder named `html` and write a basic `index.html` file into it.
2. Start an Nginx container mounting the host's `html` folder to the container's default static asset directory: `docker run -d -p 8080:80 -v "$(pwd)"/html:/usr/share/nginx/html nginx:alpine`.
3. Open a browser or run `curl http://localhost:8080` to verify your file displays.
4. Modify the local `index.html` on your host machine.
5. Re-run `curl http://localhost:8080` and confirm the updates are reflected instantly without a rebuild or restart.

#### Lab 4: High-Speed Ephemeral RAM Storage via Tmpfs
**Objective:** Implement high-speed RAM-backed mounts and observe their transient behavior.
**Tasks:**
1. Start an alpine container with a tmpfs mount configured at `/mnt/ram`: `docker run -d --name ram-node --tmpfs /mnt/ram:size=32m alpine sleep 100`.
2. Write a test file inside the RAM path: `docker exec ram-node sh -c "echo 'RAM Data' > /mnt/ram/test.db"`.
3. Stop the container: `docker stop ram-node`.
4. Start the container again: `docker start ram-node`.
5. Read the contents of the file (`docker exec ram-node cat /mnt/ram/test.db`) and note that the data is gone because of the RAM reset.

#### Lab 5: Measuring Host Network Performance vs Bridge Network
**Objective:** Understand how host networking bypasses the port mapping layer.
**Tasks:**
1. Start an Nginx server using host networking: `docker run -d --name nginx-host --network host nginx:alpine`.
2. Verify you can access Nginx on port `80` of your host without using any `-p` port mapping options.
3. Stop and remove the `nginx-host` container.
4. Start an Nginx server on a custom bridge network mapping port `8081:80`.
5. Run `docker network inspect` on both networks and analyze the configuration difference.
""",
        "insight": r"""
### Interview Q&A

#### Q1: What is the primary difference between a Bind Mount and a Named Volume?
* **Answer:** A bind mount maps a user-specified absolute path on the host machine to a directory inside the container, making it useful for local code development. A named volume is managed entirely by Docker within its storage directory (e.g., `/var/lib/docker/volumes/`). This makes named volumes more secure, easier to manage, and less dependent on host-specific directory paths.

#### Q2: When should an engineer use Host networking instead of Bridge networking?
* **Answer:** Host networking should be used for applications that require maximum network performance, minimal latency, or need to manage wide ranges of ports dynamically. Because the container shares the host's network stack directly, it avoids virtual routing overhead (iptables, docker-proxy) and operates at native host speeds.

#### Q3: What is the benefit of using Tmpfs mounts in production configurations?
* **Answer:** Tmpfs mounts write data directly to system memory (RAM) instead of physical host storage. This makes them ideal for processing security-sensitive runtime credentials (like keys or certs) that should never touch physical disks, or for caching transient, high-frequency execution data to optimize performance.

#### Q4: Why is container-to-container name resolution disabled on the default bridge network?
* **Answer:** The default bridge network (`bridge`) is shared by all containers by default. Disabling automatic name resolution prevents naming conflicts and limits security exposure, ensuring containers cannot discover other services run by different users on the same host unless they are explicitly assigned to a custom bridge network.

#### Q5: How do you prevent a container from writing modifications back to a bind mount?
* **Answer:** You can append a read-only parameter (`:ro`) to the volume mapping command. For example, `docker run -v /host/path:/container/path:ro image_name` ensures that the container cannot modify host files, maintaining the integrity of the host's storage environment.
"""
    },
    {
        "id": 4,
        "title": "Module 4: Multi-Container Orchestration with Docker Compose",
        "theory": r"""
### Guided Conceptual Walkthrough
Managing a multi-container system (like a backend server, a relational database, and an in-memory cache) with raw CLI commands is like directing a symphonic orchestra by running around the stage and yelling instructions at every single musician one by one. If you stop to talk to the pianist, the violinist might lose their tempo or start playing the wrong sheet music.

**Docker Compose** is the master conductor. It reads a single, highly structured musical score (`docker-compose.yml`) that details exactly which musicians (services) should stand on stage, how they should connect to the rhythm (custom private bridge networks), and where they should read their sheet music (persistent volumes). 

If a musician walks off stage (container crash), the conductor automatically signals them to sit back down and resume playing. When the performance concludes, the conductor waves their baton once (`docker compose down`), and the entire stage is cleanly cleared in an instant.

### Architectural & Flow Blueprint
This diagram displays how Docker Compose establishes internal network communication channels and isolates data storage layers between containers:

```mermaid
graph TD
    subgraph Host [Docker Host System]
        subgraph Net [Private Bridge Network - app_net]
            web[web Service<br>IP: 172.20.0.3]
            db[db Service<br>IP: 172.20.0.2]
            web -- DNS Lookup: 'db' --> db
        end

        subgraph Storage [Persistent Storage Layers]
            bind[Bind Mount<br>./src] -->|Real-time Sync| web
            vol[(Named Volume<br>pg_data)] -->|Secure Data Persistence| db
        end
    end
    
    client[External Client] -->|Port Forward: 8080:80| web
```

### Core Mechanics & Under-the-Hood Operations
Underneath, Docker Compose processes declarations in YAML into system API calls dispatched to the Docker Engine:
1. **The Embedded DNS Engine:**
   When custom bridge networks are established, Docker starts a lightweight DNS server at IP address `127.0.0.11` inside each container namespace. When your application tries to connect to `db:5432`, the container's OS queries this resolver, which dynamically returns the current private network IP assigned to the database container.
2. **Volume Persistence Drivers:**
   - **Named Volumes:** Docker provisions a dedicated subdirectory within `/var/lib/docker/volumes/` on the host. This directory is entirely controlled by the Docker daemon. Because file ownership permissions are managed internally, named volumes are highly secure, reliable, and decoupled from host filesystem specifics.
   - **Bind Mounts:** Directly overlays a specific, existing path on the host filesystem over a path inside the container namespace using native kernel filesystem mounts. Any alterations made on the host (like saving code in an IDE) are instantaneously reflected inside the running container, bypassing layer compilation steps entirely.

### Deep-Dive Explanations (Advanced Context)
<details>
<summary>Deep Dive: Docker DNS Name Resolution Lifecycle</summary>
The embedded resolver handles standard DNS lookup requests. If a container queries a hostname matching a known service name or custom alias on its shared network, the resolver answers with the container's private IP. If the query is for an external address (e.g., `google.com`), the DNS resolver forwards the request to the host system's configured nameservers (defined in the host's `/etc/resolv.conf`).
</details>

<details>
<summary>Deep Dive: Bind Mount File Ownership Conflicts</summary>
When utilizing bind mounts for development, files created inside the container by a process running as `root` will be owned by `root` on the host. This often prevents developers from modifying, moving, or deleting those files inside their local IDEs without running `sudo`. To mitigate this, developers should configure the Docker container to run processes using matching host User IDs (UID) and Group IDs (GID) via user parameters or environment structures.
</details>

### Common Pitfalls & Troubleshooting
#### Pitfall 1: Application Connections Crashing on Boot (Race Conditions)
*   **Error Message:**
    ```text
    web_1  | ConnectionRefusedError: [Errno 111] Connection refused
    compose_web_1 exited with code 1
    ```
*   **Root Cause:** The `depends_on` instruction in a `docker-compose.yml` file only guarantees that the database container has *started*, not that the engine inside it is ready to accept socket connections. If the web container boots up faster than the database can run its initialization migrations, the web service will crash immediately.
*   **Resolution CLI Command / Configuration:**
    ```yaml
    # Integrate health check assertions to sequence startup order correctly:
    services:
      db:
        image: postgres:15-alpine
        healthcheck:
          test: ["CMD-SHELL", "pg_isready -U postgres"]
          interval: 5s
          timeout: 5s
          retries: 5
      web:
        image: my-app:latest
        depends_on:
          db:
            condition: service_healthy
    ```

#### Pitfall 2: Local Volume File Changes Not Synced (FileSystem Sync Limits)
*   **Error Message:** Editing code files on a Windows/macOS host system does not register inside the running container, necessitating manual app restarts.
*   **Root Cause:** Virtualization hypervisors on non-Linux hosts (e.g., Docker Desktop on macOS/Windows) utilize file synchronization shares (like gRPC FUSE or VirtioFS) to bridge filesystems. These engines occasionally fail to propagate filesystem write events (`inotify`) across the virtualization boundary.
*   **Resolution CLI Command:**
    ```bash
    # Restart the synchronization daemon or force-reload the compose context
    docker compose restart web
    # Ensure optimal sync protocol is selected in Docker Desktop settings (e.g. VirtioFS)
    ```

#### Pitfall 3: Stale Environment Settings in Recreated Stacks
*   **Error Message:** Changing values inside the local `.env` configuration file has no effect when running `docker compose up`.
*   **Root Cause:** Docker Compose attempts to reuse existing containers if their configurations are unchanged. If the compose file uses custom configurations that are stored in persistent state databases or cached build layers, changes inside `.env` may require container recreation or build cache invalidation.
*   **Resolution CLI Command:**
    ```bash
    # Force Compose to recreate containers and apply environment modifications
    docker compose up -d --force-recreate --build
    ```

### Traceability Check
Ensure you have assimilated the following operational mechanics:
- Docker Compose utilizes declarative YAML structures to model multi-container layouts.
- Custom bridge networks provide embedded DNS hostnames matching service names.
- Named volumes are persistent and managed by Docker; Bind Mounts link directly to host file inodes.
- Startup ordering is managed via `depends_on` conditions coupled with container `healthcheck` definitions.
- Running `docker compose down -v` is necessary to clear persistent volume allocations alongside containers.
""",
        "commands": r"""
### Command & Syntax Reference

#### Docker Compose Template & Anatomy
Here is a fully functional, production-ready `docker-compose.yml` template defining a multi-service web application stack:

```yaml
version: "3.8"

services:
  web:
    image: nginx:alpine
    ports:
      - "8080:80"
    volumes:
      - ./html:/usr/share/nginx/html:ro
    networks:
      - app_net
    depends_on:
      - api

  api:
    image: node:18-alpine
    environment:
      - DATABASE_URL=postgres://user:pass@db:5432/mydb
    networks:
      - app_net
      - db_net
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: mydb
    volumes:
      - db_data:/var/lib/postgresql/data
    networks:
      - db_net
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d mydb"]
      interval: 5s
      timeout: 5s
      retries: 5

networks:
  app_net:
    driver: bridge
  db_net:
    driver: bridge
    internal: true

volumes:
  db_data:
```

##### **Docker Compose Code Anatomy & Validation Rules**
*   `services:`:
    - **Syntax Rules:** The top-level block defining the container application blueprints. Each item under `services:` is a distinct service container that Docker Compose manages.
*   `ports: - "8080:80"`:
    - **Anatomy:** Publishes port `80` inside the container to port `8080` on the host. Must be wrapped in quotes to prevent YAML parsers from translating colon notation into sexagesimal base-60 integers.
*   `volumes: - ./html:/usr/share/nginx/html:ro`:
    - **Anatomy:** Mounts a local directory `./html` as a read-only (`ro`) bind mount inside the container. This prevents the running container from modifying local host assets.
*   `networks:`:
    - **Anatomy:** Isolation boundary. The `web` and `api` services can communicate over `app_net`. The `api` and `db` services communicate over `db_net`. Crucially, because `web` is not connected to `db_net`, it is completely isolated from accessing the database directly, reducing the network attack surface.
*   `depends_on:` with `condition: service_healthy`:
    - **Anatomy:** Dictates startup sequencing. Compose waits to start the `api` container until the `db` container's `healthcheck` script passes successfully (exiting with code `0`).
*   `healthcheck:`:
    - **Anatomy:** Active monitoring loop. Runs `pg_isready` inside the postgres container. If it fails 5 times consecutively, the database status is marked unhealthy, halting dependent startups.
*   `networks: db_net: driver: bridge internal: true`:
    - **Anatomy:** Explicitly creates a custom bridge network where `internal: true` blocks any external ingress or egress traffic, locking down database network interactions.
*   `volumes: db_data:`:
    - **Anatomy:** Allocates a named volume managed entirely by the Docker daemon's storage subsystem. It persists data independently of container recreation cycles.

#### 1. Managing Multi-Container Stacks
```bash
docker compose up [OPTIONS]
```
*   **Parameter Anatomy:**
    - `-d` (Detached): Configures, creates, runs, and monitors all services in the background.
    - `--build`: Forces Compose to rebuild custom images before initiating container launch routines.
    - `--force-recreate`: Recreates containers even if their configurations have not changed.

```bash
docker compose down [OPTIONS]
```
*   **Parameter Anatomy:**
    - Stops and destroys running containers, networks, and internal resources defined in the compose file.
    - `-v` (Volumes): Deletes all associated named volumes. Crucial for resetting databases to clean states.

#### 2. Querying Operational Contexts
```bash
docker compose ps [OPTIONS]
```
*   **Parameter Anatomy:**
    - Renders the current runtime and healthcheck status of containers associated with the local Compose context directory.

```bash
docker compose logs [OPTIONS] [SERVICE]
```
*   **Parameter Anatomy:**
    - Aggregates and displays logs from all running services. Specifying a service name (e.g., `docker compose logs db`) filters output specifically to that service.
    - `-f` (Follow): Streams logs live.

#### 3. Execution and Administration
```bash
docker compose exec [OPTIONS] SERVICE COMMAND [ARG...]
```
*   **Parameter Anatomy:**
    - Executes commands inside running service containers (e.g., `docker compose exec db psql -U postgres`).
""",
        "examples": r"""
### Real-World Examples

#### Example 1: Multi-Container Python Flask Application and Redis Caching Stack
**Situation:** You need to deploy a Flask application that writes hit statistics to an in-memory Redis cache, communicating over an isolated network.
**Action:** Create a standard declarative `docker-compose.yml` file to spin up both systems seamlessly:
```yaml
version: "3.8"

services:
  web:
    image: python:3.10-alpine
    command: sh -c "pip install redis flask && python -c '
from flask import Flask
import redis
app = Flask(__name__)
r = redis.Redis(host=\"cache\", port=6379)
@app.route(\"/\")
def hello():
    count = r.incr(\"hits\")
    return f\"Hello! This page has been viewed {count} times.\"
app.run(host=\"0.0.0.0\", port=8000)
'"
    ports:
      - "8080:8000"
    depends_on:
      - cache

  cache:
    image: redis:7-alpine
```

#### Example 2: Configuring Developer Hot-Reloading using a Bind Mount
**Situation:** A Node.js developer wants to make real-time updates inside their local `src` folder and see changes reflect instantly inside the container.
**Action:** Declare a bind mount mapping the local project workspace to the internal app container directory:
```yaml
version: "3.8"

services:
  node-app:
    image: node:18-alpine
    working_dir: /src
    volumes:
      - .:/src
    ports:
      - "3000:3000"
    command: "node server.js"
```

#### Example 3: Externalizing Sensitive Environment Secrets Securely
**Situation:** You need to pass database credentials into a database stack without hardcoding passwords inside your version-controlled code repository.
**Action:** Construct a local `.env` metadata file and bind-import variables dynamically:
```env
# Contents of local .env file (excluded from git)
DB_USER=master_admin
DB_PASSWORD=ultra_secure_pass_123
```
```yaml
# Contents of docker-compose.yml
version: "3.8"

services:
  database:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    ports:
      - "5432:5432"
```

#### Example 4: Ensuring Database Persistence with Named Volumes
**Situation:** A development PostgreSQL server must retain tables and records across system restarts and container updates.
**Action:** Configure a named volume to decouple database storage from the container lifecycle:
```yaml
version: "3.8"

services:
  postgres-db:
    image: postgres:15-alpine
    environment:
      POSTGRES_PASSWORD: admin_secret_password
    volumes:
      - postgres_data_store:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data_store:
```

#### Example 5: Sequencing Multi-Service Startup with Health Checks
**Situation:** A backend app crashes on startup because it attempts to query database schema migrations before PostgreSQL has initialized socket engines.
**Action:** Implement health checks and dependencies to postpone app startup until the database is fully operational:
```yaml
version: "3.8"

services:
  app:
    image: alpine:3.18
    command: sh -c "echo 'App connecting to db...'; sleep 2"
    depends_on:
      db-service:
        condition: service_healthy

  db-service:
    image: postgres:15-alpine
    environment:
      POSTGRES_PASSWORD: postgres_secret_pass
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 2s
      timeout: 2s
      retries: 10
```
""",
        "exercise": r"""
### Hands-On Labs

#### Lab 1: Deploying a Multi-Service Stack
**Objective:** Declare and manage multiple interconnected services using Docker Compose.
**Tasks:**
1. Create a `docker-compose.yml` file containing a backend web service running Nginx and an isolated Redis caching server.
2. Start the stack in background mode: `docker compose up -d`.
3. Verify that both containers are running using `docker compose ps`.
4. View aggregated service startup logs using `docker compose logs`.
5. Spin down the stack and verify all created containers and custom networks are removed.

#### Lab 2: Hot-Reloading Local Files via Bind Mounts
**Objective:** Keep code and container environments synchronized during local development.
**Tasks:**
1. Set up a basic Python web application.
2. Define a Compose service mapping your local directory to `/app` inside the container using a bind mount.
3. Start your services.
4. Modify a message string inside your host-side Python file and save it.
5. Query your application container and confirm the updates are reflected instantly without a rebuild.

#### Lab 3: Decoupling Secrets via Environment Profiles
**Objective:** Pass dynamic database configurations into a running container environment safely.
**Tasks:**
1. Create a `.env` file declaring database credentials.
2. Reference these values inside a `docker-compose.yml` service definition.
3. Bring up the environment and run `docker compose exec db env` to verify the environment variables were passed successfully.
4. Change a value inside `.env` and restart the stack using `docker compose up -d`.
5. Confirm the updated credentials were applied correctly inside the container.

#### Lab 4: Inter-Container DNS Verification
**Objective:** Verify automatic DNS-based service discovery between containers on a shared network.
**Tasks:**
1. Define two services (`web` and `api`) in a `docker-compose.yml` file.
2. Start the stack.
3. Execute an interactive shell inside the `web` container: `docker compose exec web sh`.
4. Ping the `api` container using its service name: `ping api`.
5. Confirm that the DNS successfully resolves the service name to the `api` container's internal IP address.

#### Lab 5: Volume Persistence Audits
**Objective:** Verify that database records persist across container restarts.
**Tasks:**
1. Create a database service in Compose and mount its data to a named volume.
2. Start the service, log into the database shell, and create a test table with sample records.
3. Stop and delete the container stack using `docker compose down`. Do not use the `-v` flag.
4. Recreate the stack using `docker compose up -d`.
5. Log back into the database and verify that your test table and sample records are still intact.
""",
        "insight": r"""
### Interview Q&A

#### Q1: What is the limitation of the `depends_on` parameter, and how can you ensure a database is ready before your app connects?
* **Answer:** By default, `depends_on` only tracks whether the dependent container has started, not whether the application inside it is ready to accept connections. To ensure a database is ready, you should define a `healthcheck` on the database service and use `depends_on` with a `service_healthy` condition.

#### Q2: What happens to persistent volumes when you run the `docker compose down` command?
* **Answer:** Running `docker compose down` stops and removes containers and networks, but leaves named volumes untouched on the disk to prevent data loss. To permanently delete the associated volumes alongside your containers, you must run `docker compose down -v`.

#### Q3: How can you manage different environment settings (e.g., development vs. production) using Docker Compose?
* **Answer:** You can use environment files (like `.env`) to swap configuration values across environments, or use multiple Compose files (e.g., `docker-compose.yml` and `docker-compose.override.yml`). Docker Compose automatically merges override files, allowing you to easily adjust ports, volumes, and logging parameters for different environments.

#### Q4: Why is it important to wrap port mappings in quotes inside a `docker-compose.yml` file?
* **Answer:** YAML parsers interpret colon-separated numbers without quotes (such as `80:80` or `9090:80`) in sexagesimal (base 60) notation. This can cause the port numbers to be parsed incorrectly, leading to unexpected binding failures. Wrapping port allocations in quotes (e.g., `"8080:80"`) ensures they are treated strictly as string variables.

#### Q5: How does Docker Compose resolve hostnames between isolated container services?
* **Answer:** Docker Compose automatically creates a user-defined bridge network when you start a stack. This network features an embedded DNS server that resolves service names to their corresponding container IP addresses, allowing containers to safely communicate using readable hostnames instead of static IPs.
"""
    }
]