#!/usr/bin/env bash

# Exit immediately if any step fails
set -e

echo "=========================================="
echo "Initializing Self-Paced Learning Portal..."
echo "=========================================="

# 1. Create folder structure if it doesn't exist
mkdir -p app/static
mkdir -p courses

# 2. Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed. Please install it to continue."
    exit 1
fi

# 3. Handle Python Virtual Environment (.venv)
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment (.venv)..."
    python3 -m venv .venv
fi

echo "Activating virtual environment..."
source .venv/bin/activate

# 4. Install FastAPI and Uvicorn
echo "Installing/upgrading dependencies..."
pip install --upgrade pip
pip install fastapi uvicorn

# 5. Initialize data.db SQLite database
echo "Checking/initializing Database (data.db)..."
python3 -c '
import sqlite3
conn = sqlite3.connect("data.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS progress (
    course_id TEXT,
    module_id INTEGER,
    section_id TEXT,
    PRIMARY KEY (course_id, module_id, section_id)
);
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS pomodoro (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    completed_at TEXT,
    duration_minutes INTEGER
);
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id TEXT,
    module_id INTEGER,
    section_id TEXT,
    selected_text TEXT,
    note_text TEXT,
    created_at TEXT,
    occurrence_index INTEGER DEFAULT 0
);
""")
conn.commit()
conn.close()
print("Database data.db verified/initialized successfully.")
'

# 6. Check if courses directory is empty; if so, create sample courses under folder categories
if [ -z "$(ls -A courses)" ]; then
    echo "No courses detected. Creating sample courses under categorized folders..."
    mkdir -p courses/devops/containers
    mkdir -p courses/sre
    cat << 'EOF' > courses/devops/docker.py
COURSE_ID = "docker"
COURSE_TITLE = "Docker Containerization"
COURSE_DESCRIPTION = "A self-paced engineering track covering container engines, image optimization, and volume configurations."

CURRICULUM_DATA = [
    {
        "id": 1,
        "title": "Understanding Containers vs Virtual Machines",
        "theory": "### Core Concepts\nVirtual machines package an entire operating system, whereas containers share the host machine's kernel and isolate user space. This makes containers significantly lighter, faster to boot, and less resource-intensive.",
        "commands": "```bash\n# Check Docker version and engine info\ndocker version\ndocker info\n```",
        "examples": "```bash\n# Run a simple nginx container on port 80\ndocker run --name web-server -d -p 80:80 nginx\n```",
        "exercise": "### Lab Assignment\n1. Run an interactive Ubuntu container using `docker run -it ubuntu /bin/bash`.\n2. Inside the container, run `apt-get update && apt-get install -y curl` to install curl.\n3. Exit the container and list your active containers.",
        "insight": "### Certified Prep Queries\n**Q: What is the difference between an image and a container?**\n\n**A:** An image is a read-only template that defines the environment (a blueprint). A container is a running instance of that image with a read-write filesystem layer stacked on top."
    }
]
EOF

    cat << 'EOF' > courses/devops/containers/docker_advanced.py
COURSE_ID = "docker_advanced"
COURSE_TITLE = "Advanced Docker Production"
COURSE_DESCRIPTION = "Advanced orchestration, network plugins, multi-stage builds, and container security."

CURRICULUM_DATA = [
    {
        "id": 1,
        "title": "Multi-Stage Build Architecture",
        "theory": "### Core Concepts\nMulti-stage builds allow developers to optimize Dockerfile sizes by using multiple FROM statements. Unnecessary build tools are left behind in the builder stage.",
        "commands": "```dockerfile\n# Example of multi-stage build\nFROM golang:1.20 AS builder\nWORKDIR /app\nCOPY . .\nRUN go build -o main .\n\nFROM alpine:latest\nWORKDIR /root/\nCOPY --from=builder /app/main .\nCMD [\"./main\"]\n```",
        "examples": "```bash\n# Build the production optimized image\ndocker build -t my-app:prod .\n```",
        "exercise": "### Lab Assignment\n1. Design a simple multi-stage Dockerfile for a Node.js or Go application.\n2. Verify that the final image contains only the compiled binary and minimal dependencies.",
        "insight": "### Certified Prep Queries\n**Q: How do multi-stage builds decrease vulnerability footprint?**\n\n**A:** By excluding build dependencies and compilers from the final execution image, multi-stage builds remove potential attack vectors from runtime containers."
    }
]
EOF

    cat << 'EOF' > courses/sre/kubernetes.py
COURSE_ID = "kubernetes"
COURSE_TITLE = "Kubernetes Administrator"
COURSE_DESCRIPTION = "Master container orchestration, cluster architecture, and application scheduling."

CURRICULUM_DATA = [
    {
        "id": 1,
        "title": "Kubernetes Architecture & Core Components",
        "theory": "### Core Concepts\nKubernetes consists of a Control Plane (API Server, Scheduler, Controller Manager, etcd) and Worker Nodes (Kubelet, Kube-Proxy, Container Runtime). It manages containerized workloads declaratively.",
        "commands": "```bash\n# Check cluster status and nodes\nkubectl cluster-info\nkubectl get nodes\n```",
        "examples": "```yaml\n# Create a basic Nginx Pod\napiVersion: v1\nkind: Pod\nmetadata:\n  name: nginx-pod\nspec:\n  containers:\n  - name: nginx\n    image: nginx:alpine\n```",
        "exercise": "### Lab Assignment\n1. Use `kubectl get pods` to list any existing pods.\n2. Create a temporary Nginx pod and verify its running state.\n3. Delete the pod to clean up.",
        "insight": "### Certified Prep Queries\n**Q: What is the main duty of the Kubelet?**\n\n**A:** The Kubelet is an agent running on each node that ensures containers are running in a Pod according to the PodSpecs provided by the API Server."
    }
]
EOF
fi

# Reminder: Warn if application code is missing
if [ ! -f "app/main.py" ] || [ ! -f "app/static/index.html" ]; then
    echo "Warning: Ensure 'app/main.py' and 'app/static/index.html' are created before visiting."
fi

# 7. Start the Uvicorn Server
echo "=========================================="
echo "Starting FastAPI application..."
echo "Access the portal at: http://127.0.0.1:8000"
echo "=========================================="

exec uvicorn app.main:app --reload