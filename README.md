# Self-Paced Learning Portal

A lightweight, self-hosted learning portal for self-paced study in DevOps, SRE, and software development. 

The application is completely self-contained. When you run the launcher script, it automatically creates a Python virtual environment, installs the required dependencies, generates the initial curriculum configurations, and starts the server.

---

## Visuals

### Course Selection Dashboard
*Select a specialization track from the dynamic home dashboard.*

![Course Selection Dashboard](docs/images/dashboard.png)

### Interactive Workspace
*Track progress section-by-section, adjust font sizes, and view interview preparation questions.*

![Interactive Workspace](docs/images/workspace.png)

---

## Features

* **Zero-Config Isolation:** Automatically bootstraps and runs within a local `.venv` virtual environment.
* **Dynamic Course Loading:** Loads any curriculum defined in Python configuration files inside the `/courses` directory automatically.
* **Persistent Progress Tracking:** Saves your completion states locally using a SQLite database.
* **Unified Search:** Searches across all active curriculums and displays course-mapped matches.

---

## How to Run

### Prerequisites
* **Python 3.8+** must be installed on your system.

### 1. Clone the Repository
Clone this repository to your local machine:
```bash
git clone <YOUR_GITHUB_REPO_URL>
cd self-paced-learning-portal
```

### 2. Launch the Application
Run the master bootstrapper script. This will automatically set up the virtual environment, resolve dependencies, and start the local server:
```bash
python main.py
```

### 3. Access the Portal
Once the terminal displays that the server is online, open your web browser and navigate to:
```text
http://127.0.0.1:8000
```

---

## Adding Your Own Curriculums
To add a new course, create a Python file (e.g., `ansible.py`) inside the `/courses` directory. The platform will automatically load it on the next page refresh:

```python
COURSE_ID = "ansible"
COURSE_TITLE = "Ansible Automation"
COURSE_DESCRIPTION = "A brief description of your track."
CURRICULUM_DATA = [ ... ]
```

---

## License
This project is licensed under the MIT License.