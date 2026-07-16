# Self-Paced Learning Portal

A lightweight, self-hosted learning portal for self-paced study in DevOps, SRE, and software development. 

## Visuals

### Course Selection Dashboard

![Course Selection Dashboard](docs/images/dashboard.png)

### Interactive Workspace

![Interactive Workspace](docs/images/workspace.png)

## Features

* **Zero-Config Isolation:** Automatically bootstraps and runs within a local `.venv` virtual environment.
* **Dynamic Course Loading:** Loads any curriculum defined in Python configuration files inside the `/courses` directory automatically.
* **Persistent Progress Tracking:** Saves your completion states locally using a SQLite database.
* **Unified Search:** Searches across all active curriculums and displays course-mapped matches.

## How to Run

### Prerequisites
* **Python 3.8+** must be installed on your system.

### 1. Clone the Repository
```bash
git clone git@github.com:s06a/self-paced-learning-portal.git
cd self-paced-learning-portal
```

### 2. Launch the Application
```bash
python main.py
```

### 3. Access the Portal
```text
http://127.0.0.1:8000
```

## Adding Your Own Curriculums
To add a new course, create a Python file (e.g., `ansible.py`) inside the `/courses` directory. The platform will automatically load it on the next page refresh:

```python
COURSE_ID = "ansible"
COURSE_TITLE = "Ansible Automation"
COURSE_DESCRIPTION = "A brief description of your track."
CURRICULUM_DATA = [ ... ]
```

Feel free to open a PR!

## License
This project is licensed under the MIT License.