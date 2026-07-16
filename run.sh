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
conn.commit()
conn.close()
print("Database data.db verified/initialized successfully.")
'

# 6. Check if courses directory is empty; if so, create a sample Docker course
if [ -z "$(ls -A courses)" ]; then
    echo "No courses detected. Creating a sample Docker course..."
    cat << 'EOF' > courses/docker.py
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