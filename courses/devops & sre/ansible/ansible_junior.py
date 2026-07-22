COURSE_ID = "ansible_devops_sre_junior"
COURSE_TITLE = "Ansible for DevOps & SRE: Foundations & Configuration Management"
COURSE_DESCRIPTION = "Master the core philosophy of Ansible, declarative infrastructure as code, structured inventories, dynamic playbooks, system facts, and secret management using Ansible Vault."

CURRICULUM_DATA = [
    {
        "id": 1,
        "title": "Module 1: Introduction to Ansible & IaC (Infrastructure as Code)",
        "theory": """### Core Philosophy of Infrastructure as Code
Infrastructure as Code (IaC) is an industry practice designed to manage and provision computing infrastructure through machine-readable definition files rather than manual hardware configuration or interactive configuration tools. Under this umbrella, automation tools generally align with one of two logical execution philosophies:
1. **Declarative Automation:** You define the desired end-state of the target system (e.g., 'this package must be installed and running on port 80'). The tool evaluates the system's current state and performs only the necessary operations to reconcile it with the desired state. This characteristic is known as *idempotence*.
2. **Imperative Automation:** You specify the precise, sequential steps required to achieve a goal (e.g., 'run apt-get update, then run apt-get install, then open port 80'). This approach is highly sequence-dependent and often fails or introduces unintended state drift if run repeatedly.

Ansible is fundamentally a declarative automation platform, meaning playbooks describe target configurations rather than sequential execution scripts.

### The Ansible Architecture & Push vs. Pull Model
Unlike legacy configuration management systems such as Chef or Puppet, which rely on an agent-server architecture, Ansible utilizes an **agentless, push-based model**:
* **Agentless Design:** There are no background daemons or client packages installed on target systems. This eliminates configuration drift caused by outdated agents, reduces runtime resource overhead, and simplifies initial bootstrapping.
* **Push Model:** Configurations are defined, parsed, and executed from a single machine known as the **Control Node**. The Control Node pushes compiled Python modules (or PowerShell scripts for Windows) to remote **Managed Nodes** over standard transport protocols.
* **Control Node Requirements:** Must run a Unix-like operating system (such as Linux, macOS, or WSL on Windows) with Python installed.
* **Managed Node Requirements:** Must have an active SSH daemon (or WinRM/SSH for Windows) and a Python interpreter installed.

### Under the Hood: SSH Transport Mechanism
Ansible relies heavily on standard SSH (Secure Shell) for its transport layer on Unix-based targets. When executing tasks, Ansible connects to the remote machine, transfers compiled code packages into a temporary directory (usually `~/.ansible/tmp/`), executes those payloads natively, captures stdout/stderr JSON responses, and deletes the temporary files.

To maintain secure, non-interactive execution, SRE best practices dictate using **SSH public-key authentication** rather than plain text passwords. This involves generating an asymmetric cryptographic key pair (such as ED25519) on the control node and distributing the public key to the authorized keys file on each managed node.

### Ansible Configuration File Hierarchy
Ansible’s runtime behavior is governed by its configuration file (`ansible.cfg`). This configuration is resolved dynamically by checking directories in the following order of precedence:
1. `ANSIBLE_CONFIG` (An environment variable pointing directly to a file).
2. `ansible.cfg` (Located in the current working directory from which the command is executed).
3. `~/.ansible.cfg` (Located in the user's home directory).
4. `/etc/ansible/ansible.cfg` (The global default fallback file).

Understanding this resolution order is critical; standard practice is to maintain a dedicated `ansible.cfg` within the root of each infrastructure Git repository to ensure consistent settings across team members and CI/CD runners.""",
        "commands": """### Command & Syntax Reference

#### Verify Ansible Control Node Installation
```bash
# Check version, configuration file location, and Python dependencies
ansible --version
```

#### Generate Secure Asymmetric SSH Keypair
```bash
# Generate a modern, highly secure ED25519 SSH keypair for Ansible automation
ssh-keygen -t ed25519 -C "ansible_automation_control" -f ~/.ssh/id_ed25519 -N ""
```

#### Distribute Public Key to Managed Target Node
```bash
# Copy the public key to a remote host to allow non-interactive authentication
ssh-copy-id -i ~/.ssh/id_ed25519.pub sysadmin@192.168.1.50
```

#### Test SSH Connection Directly
```bash
# Verify passwordless authentication works outside of Ansible
ssh -i ~/.ssh/id_ed25519 sysadmin@192.168.1.50 "uname -a"
```

#### Dump All Current Configurations
```bash
# View active configurations along with their source files
ansible-config dump --only-changed
```""",
        "examples": """### Real-World Examples

#### Example 1: Modern ansible.cfg Configurations
* **Situation:** A systems administrator needs to establish a consistent, performance-optimized, and secure Ansible execution configuration inside an active project folder.
* **Action:** Create a local `ansible.cfg` file that specifies custom SSH behaviors, default inventories, and path patterns.

```ini
# ansible.cfg
[defaults]
inventory = ./hosts.ini
host_key_checking = True
stdout_callback = yaml
callbacks_enabled = timer, profile_tasks
forks = 10
roles_path = ./roles

[ssh_connection]
ssh_args = -o ControlMaster=auto -o ControlPersist=60s
pipelining = True
```

#### Example 2: Automatic Control Node Bootstrap Script
* **Situation:** An SRE wants to write a shell script to automate the installation of Ansible and dependencies on an Ubuntu-based control node.
* **Action:** Build a bash script that installs Python, configures the official PPA, and installs Ansible.

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "==> Updating package indices..."
sudo apt-get update -y

echo "==> Installing system dependencies..."
sudo apt-get install -y software-properties-common python3-pip python3-venv curl

echo "==> Adding Ansible PPA repository..."
sudo apt-add-repository --yes --update ppa:ansible/ansible

echo "==> Installing Ansible Core..."
sudo apt-get install -y ansible

echo "==> Verifying installation..."
ansible --version
```

#### Example 3: Ansible SSH Target Inventory Verification
* **Situation:** A developer needs to construct a basic inventory to check if three development machines are responding to Ansible commands.
* **Action:** Draft an INI-formatted inventory file defining connections to local virtual environments.

```ini
# hosts.ini
[devservers]
dev-app-01 ansible_host=192.168.56.101 ansible_user=vagrant ansible_ssh_private_key_file=~/.ssh/id_ed25519
dev-app-02 ansible_host=192.168.56.102 ansible_user=vagrant ansible_ssh_private_key_file=~/.ssh/id_ed25519
dev-app-03 ansible_host=192.168.56.103 ansible_user=vagrant ansible_ssh_private_key_file=~/.ssh/id_ed25519
```

#### Example 4: Custom SSH Connection Tweaks for Managed Nodes
* **Situation:** An operations team has web servers that use a non-standard SSH port (e.g., 2222) due to perimeter security policies.
* **Action:** Construct a configuration to let Ansible target these instances over standard inventory mappings.

```ini
# inventory_custom_ssh.ini
[secure_perimeter]
prod-edge-01 ansible_host=203.0.113.15 ansible_port=2222 ansible_user=ops_admin ansible_ssh_private_key_file=~/.ssh/production_deploy_key
prod-edge-02 ansible_host=203.0.113.16 ansible_port=2222 ansible_user=ops_admin ansible_ssh_private_key_file=~/.ssh/production_deploy_key
```

#### Example 5: Basic Ping Execution with Verbose Logging
* **Situation:** After setting up keys and inventories, an engineer wants to test network path latency and Ansible transport module integrity on remote targets.
* **Action:** Run a verbose execution using Ansible command line interfaces.

```bash
# Execute the built-in ping test module with high verbosity to diagnose connection layers
ansible devservers -i hosts.ini -m ansible.builtin.ping -vvv
```""",
        "exercise": """### Hands-On Labs

#### Lab 1: Control Node Setup and Verification
* **Objective:** Install Ansible and inspect configuration defaults.
* **Tasks:**
  1. Boot up an Ubuntu-based virtual machine or open a clean WSL console terminal.
  2. Install Python3 and pip dependencies.
  3. Run the commands `sudo apt update && sudo apt install -y ansible`.
  4. Run `ansible --version` and locate the designated system-wide default configuration path.

#### Lab 2: Generating and Copying SSH Keys to Managed Targets
* **Objective:** Enable secure, passwordless authentication from the Control Node to a target machine.
* **Tasks:**
  1. Open a terminal session on your Control Node.
  2. Run `ssh-keygen -t ed25519 -f ~/.ssh/id_ansible -N ""` to generate the keypair.
  3. Deploy this public key to a local target machine or virtual machine using `ssh-copy-id -i ~/.ssh/id_ansible.pub username@localhost`.
  4. Connect manually using `ssh -i ~/.ssh/id_ansible username@localhost` to verify no password prompt is displayed.

#### Lab 3: Crafting a Specialized ansible.cfg
* **Objective:** Establish isolated configuration structures inside a dedicated deployment directory.
* **Tasks:**
  1. Create a workspace directory named `ansible-lab` and change into it.
  2. Create a blank file named `ansible.cfg`.
  3. Define custom behaviors: force host key checking to `True`, set the default inventory target parameter to `hosts.ini`, and enable the `timer` callback.
  4. Run `ansible-config dump --only-changed` to confirm that your local overrides are successfully read.

#### Lab 4: Defining and Debugging Connections
* **Objective:** Map targets inside an active inventory and test connection limits.
* **Tasks:**
  1. Inside `ansible-lab`, create a `hosts.ini` file containing a group called `[test_targets]`.
  2. Add the address `127.0.0.1` as a target host, and configure connection parameters: `ansible_connection=local`.
  3. Run the command `ansible test_targets -m ansible.builtin.ping` to test execution.
  4. Verify that the task succeeds and returns a JSON payload containing `"ping": "pong"`.

#### Lab 5: Verifying Connection Latencies and SSH Configuration
* **Objective:** Use connection profiling features to audit performance bottlenecks.
* **Tasks:**
  1. Edit the local `ansible.cfg` configuration in your working directory.
  2. Inside the `[ssh_connection]` block, enable `pipelining = True`.
  3. Run `ansible test_targets -m ansible.builtin.ping` with the timer callback active.
  4. Analyze the total time taken before and after the modification to confirm the speed improvement.""",
        "insight": """### Interview Q&A

#### Q1: What is the primary difference between declarative and imperative configuration management models, and where does Ansible sit?
* **Answer:** Declarative models focus on the final state of the target system, whereas imperative models focus on the actions needed to get there. Ansible is declarative. Instead of detailing commands to create directories, set permissions, and copy files, you define the desired directory structure and file contents. Ansible then determines the correct steps to make the system match that definition.

#### Q2: How does the agentless nature of Ansible impact network performance and security policies?
* **Answer:** Agentless deployment reduces target server overhead by eliminating background daemons, which minimizes attack vectors and avoids agent upgrade cycles. For security, it relies on standard secure mechanisms like SSH or WinRM, matching existing infrastructure access controls. However, it can increase CPU and network usage on the Control Node during concurrent tasks, which can be optimized with features like SSH multiplexing and pipelining.

#### Q3: Describe the hierarchy of ansible.cfg resolution and how you can override configurations for a specific run.
* **Answer:** Ansible checks configurations in this order: first, the `ANSIBLE_CONFIG` environment variable; second, a local `ansible.cfg` in the current working directory; third, `~/.ansible.cfg` in the user's home directory; and finally, `/etc/ansible/ansible.cfg`. You can override individual configuration parameters on the command line using environment variables (e.g., `ANSIBLE_HOST_KEY_CHECKING=False ansible ...`).

#### Q4: Why is key-based SSH authentication strongly preferred over password-based authentication in production Ansible pipelines?
* **Answer:** Key-based authentication allows secure, unattended automation without hardcoding credentials in playbooks or logs. It prevents brute-force password discovery and simplifies key rotation policies. Additionally, password-based authentication requires the manual input or insecure piping of passwords, which can disrupt automated continuous integration/continuous deployment (CI/CD) pipelines.

#### Q5: How do you handle target systems that use custom, non-standard SSH ports or different system administrator login names?
* **Answer:** These connection parameters can be defined per host or group within the inventory using specific connection variables: `ansible_port` overrides the standard SSH port (default 22), and `ansible_user` specifies the login user. This separates system variations from actual playbook declarations.

### Ansible Certification Focus
* **Core Topic:** Understand how to modify and debug `ansible.cfg`. Expect questions on resolving configuration paths and disabling `host_key_checking` safely.
* **Best Practice:** Keep an isolated, local `ansible.cfg` file inside your Git repositories to maintain project environment consistency."""
    },
    {
        "id": 2,
        "title": "Module 2: Inventories & Ad-Hoc Commands",
        "theory": """### Anatomy of Ansible Inventories
An inventory is a structured representation of the infrastructure managed by Ansible. It lists target hosts, maps them to semantic environments, and groups them by workload function or physical location.
Ansible supports two standard file formats for static inventories:
1. **INI Format:** A simple key-value format using section headers for groups.
2. **YAML Format:** A structured, hierarchical format that is cleaner for complex nested groups but has stricter syntax rules.

Within inventories, we can define structural hierarchies. Child groups can be nested within parent groups, allowing system administrators to apply variables to large groups of servers (such as all geographic regions) while keeping specialized variables for specific instances (such as database primary nodes).

### Variable Scope: Host vs. Group Variables
When managing scale, variables should not be hardcoded inside playbooks. Instead, they should be applied using appropriate scope in the inventory layer:
* **Host Variables:** Specific to a single machine (e.g., its unique internal IP address, or specific database replication ID).
* **Group Variables:** Applied to every host within a target group (e.g., consistent backup directories, monitoring endpoints, or system time zones).

### Designing Standard Directory Layouts
Placing too many variables directly inside the primary inventory file makes it difficult to read and manage. SRE guidelines suggest using separate directories named `group_vars/` and `host_vars/` located alongside the inventory file or playbook.
* If a host is named `prod-db-01`, Ansible automatically reads variables defined in a file named `host_vars/prod-db-01.yml`.
* If a group is named `webservers`, Ansible automatically imports variables from `group_vars/webservers.yml`.
* Files inside these directories must be written in valid YAML.

### Ad-Hoc Execution Concepts & Syntax
Ad-hoc commands are quick, single-task operations executed from the command line without writing a full playbook. They are useful for rapid system tasks, such as checking disk space across a cluster, restarting a service during an incident, or collecting system configuration states.

An ad-hoc command follows this syntax structure:
`ansible <host-pattern> -i <inventory> -m <module_name> -a "<module_arguments>" --become`
The `--become` flag tells Ansible to escalate privileges (typically using `sudo`) on the target machine to run tasks that require root access.""",
        "commands": """### Command & Syntax Reference

#### List Hosts Matching a Specific Inventory Pattern
```bash
# Preview which hosts will be targeted by a group query
ansible webservers -i hosts.ini --list-hosts
```

#### Basic Ping Test (Ad-Hoc)
```bash
# Verify connectivity and Python interpreter status across all hosts
ansible all -i hosts.ini -m ansible.builtin.ping
```

#### Package Installation (Ad-Hoc)
```bash
# Install curl on all webservers using root privileges
ansible webservers -i hosts.ini -m ansible.builtin.apt -a "name=curl state=present" --become
```

#### Service State Management (Ad-Hoc)
```bash
# Restart the Nginx service across all webservers
ansible webservers -i hosts.ini -m ansible.builtin.service -a "name=nginx state=restarted" --become
```

#### Remote Command Execution (Ad-Hoc)
```bash
# Check raw disk space status across database target servers
ansible dbservers -i hosts.ini -m ansible.builtin.command -a "df -h"
```""",
        "examples": """### Real-World Examples

#### Example 1: INI Inventory with Nested Groups
* **Situation:** An operations team wants to structure an infrastructure blueprint containing both staging and production virtual environments.
* **Action:** Build a structured `hosts.ini` file using child group declarations.

```ini
# hosts.ini
[staging_web]
stage-web-01.local ansible_host=192.168.10.11
stage-web-02.local ansible_host=192.168.10.12

[production_web]
prod-web-01.local ansible_host=192.168.20.11
prod-web-02.local ansible_host=192.168.20.12

# Parent group containing all web servers
[webservers:children]
staging_web
production_web

[all:vars]
ansible_user=deploy_user
```

#### Example 2: Structured YAML Inventory Equivalent
* **Situation:** An engineer needs to convert the INI architecture into a standardized YAML schema to align with configuration policies.
* **Action:** Write a valid YAML representation of the staging and production setup.

```yaml
# hosts.yaml
all:
  children:
    webservers:
      children:
        staging_web:
          hosts:
            stage-web-01.local:
              ansible_host: 192.168.10.11
            stage-web-02.local:
              ansible_host: 192.168.10.12
        production_web:
          hosts:
            prod-web-01.local:
              ansible_host: 192.168.20.11
            prod-web-02.local:
              ansible_host: 192.168.20.12
  vars:
    ansible_user: deploy_user
```

#### Example 3: Defining group_vars/all.yml Variables
* **Situation:** A team wants to set default system packages and NTP configurations that apply globally across all infrastructure instances.
* **Action:** Create a global group variables file.

```yaml
# group_vars/all.yml
---
system_timezone: "UTC"
dns_nameservers:
  - 8.8.8.8
  - 1.1.1.1
ntp_server: "pool.ntp.org"
common_packages:
  - htop
  - tmux
  - git
```

#### Example 4: Defining host_vars/db-prod-01.yml Variables
* **Situation:** A primary database node requires custom local volume mount targets and storage limits that are different from other nodes.
* **Action:** Create a targeted host-specific variables configuration file.

```yaml
# host_vars/prod-web-01.local.yml
---
local_backup_path: "/var/backups/local/database"
max_connections: 500
shared_buffers_size: "4GB"
is_database_primary: true
```

#### Example 5: Targeted Ad-Hoc Task Checking Disk Usage and Services
* **Situation:** An SRE needs to inspect logs and disk consumption on all production web hosts during an outage.
* **Action:** Run a sequence of targeted ad-hoc commands.

```bash
# Command 1: Inspect system memory status
ansible production_web -i hosts.yaml -m ansible.builtin.command -a "free -m"

# Command 2: Tail last 5 lines of the system logs safely
ansible production_web -i hosts.yaml -m ansible.builtin.shell -a "tail -n 5 /var/log/syslog" --become
```""",
        "exercise": """### Hands-On Labs

#### Lab 1: Establishing an INI Inventory with Multiple Environments
* **Objective:** Design a custom local network inventory matching system environments.
* **Tasks:**
  1. Inside your `ansible-lab` workspace, create an INI inventory file named `multi_env_hosts.ini`.
  2. Create a group `[app_servers]` containing two mock endpoints (e.g., `app-srv-01` and `app-srv-02`).
  3. Map variables directly inside the hosts lines overriding their connection paths to point to localhost with different port tags.
  4. Query and list hosts using `ansible app_servers -i multi_env_hosts.ini --list-hosts`.

#### Lab 2: Translating INI Inventories to YAML Format
* **Objective:** Convert INI inventories to YAML syntax.
* **Tasks:**
  1. Read the `multi_env_hosts.ini` configuration created in Lab 1.
  2. Create a new file named `multi_env_hosts.yaml`.
  3. Recreate the same group structures and host-variable associations in YAML format.
  4. Run `ansible all -i multi_env_hosts.yaml --list-hosts` to confirm they produce the same list.

#### Lab 3: Implementing a host_vars and group_vars Directory Structure
* **Objective:** Clean up variables inside dynamic inventories using files.
* **Tasks:**
  1. Create directories named `group_vars` and `host_vars` in your lab workspace.
  2. Inside `group_vars`, create `app_servers.yml`. Add a key-value pair: `app_port: 8080`.
  3. Inside `host_vars`, create a file matching host name `app-srv-01.yml`. Add `node_priority: primary`.
  4. Run an ad-hoc debugging script: `ansible app_servers -i multi_env_hosts.yaml -m ansible.builtin.debug -a "var=app_port"`.

#### Lab 4: Verifying Infrastructure State with Ad-Hoc Commands
* **Objective:** Retrieve basic system information using ad-hoc commands.
* **Tasks:**
  1. Target your local machine using the command options.
  2. Run the command module with the argument `uname -a`.
  3. Retrieve raw memory consumption metrics using `free -h` through the `ansible.builtin.command` module.
  4. Run a system setup query using `ansible localhost -m ansible.builtin.setup -a "filter=ansible_date_time"`.

#### Lab 5: Deploying a Custom Group of Packages and Reloading Services via Ad-Hoc
* **Objective:** Run installation and state tasks using ad-hoc modules.
* **Tasks:**
  1. Run a module action to verify if `nginx` is installed on your target group.
  2. Run the package management command to verify that `nginx` status is set to latest. Use privilege escalation (`--become`).
  3. Run an ad-hoc execution targeting the system services configuration to restart the service.
  4. Verify the operation by querying the service state.""",
        "insight": """### Interview Q&A

#### Q1: How do host variables defined in host_vars files compare with inline variables within the inventory file?
* **Answer:** Variables defined in `host_vars/` directory files are functionally equivalent to those written inline in the inventory, but they are much easier to manage. As configurations scale, inline inventory declarations become hard to read. Moving variables to individual YAML files inside `host_vars/` separates infrastructure definitions from metadata, which simplifies version control and improves readability.

#### Q2: What is the 'all' group and the 'ungrouped' group in an Ansible inventory, and can they be modified?
* **Answer:** Ansible creates two default groups: 'all' and 'ungrouped'. The 'all' group contains every host defined in your inventory. The 'ungrouped' group contains hosts that do not belong to any user-defined group. These groups are built-in and cannot be deleted, but you can define variables for them (e.g., using `group_vars/all.yml`).

#### Q3: Why should you avoid using the shell or command modules in ad-hoc commands when managing packages?
* **Answer:** The `command` and `shell` modules execute raw shell scripts and are not declarative or idempotent. If you run `apt-get install nginx` via the shell module, it runs the install process every time, even if Nginx is already installed. Using dedicated modules like `ansible.builtin.apt` ensures idempotence; Ansible checks the system state first and only installs the package if it is missing.

#### Q4: How does Ansible handle overlapping variables defined in both a child group and a parent group?
* **Answer:** Ansible uses a strict variable precedence hierarchy. Variables defined in a child group override those defined in parent groups. If the same variable is defined in both, the more specific (child group) definition takes precedence over the broader (parent group) definition.

#### Q5: What command flag can you use to preview which hosts match a specific pattern without running any action?
* **Answer:** The `--list-hosts` flag can be appended to any Ansible execution command. For example, running `ansible webservers:!staging -i inventory.ini --list-hosts` lists all hosts matching the criteria without connecting to them or executing any tasks.

### Ansible Certification Focus
* **Core Topic:** Understand group nesting patterns and variable inheritance. Ensure you can construct exclusion filters (such as `webservers:&production`) for targeted executions.
* **Best Practice:** Keep your primary inventory file clean of individual host variables; use `group_vars/` and `host_vars/` for clearer infrastructure structure."""
    },
    {
        "id": 3,
        "title": "Module 3: Playbooks & YAML Syntax",
        "theory": """### YAML Syntax Ground Rules
YAML (YAML Ain't Markup Language) is a human-readable data serialization language used by Ansible to define playbooks. It relies on strict formatting rules:
* **Indentation:** Must use spaces; tabs are not allowed. Consistent indentation (usually 2 spaces per level) defines structure.
* **Lists:** Members of a list start with a leading hyphen and space (`- `).
* **Dictionaries (Key-Value Pairs):** Keys and values are separated by a colon and a space (`key: value`).
* **Multi-line Strings:** Defined using `|` to preserve newlines, or `>` to fold newlines into spaces.

### Playbook Structure: Plays, Tasks, and Targets
An Ansible playbook is a YAML file containing one or more *plays*. The primary goal of a play is to map a specific group of hosts to a series of tasks.
* **Play:** Maps hosts to roles or tasks and defines configuration settings, such as the remote execution user and privilege escalation options.
* **Task:** Defines an individual action to apply to a host. Tasks are executed sequentially from top to bottom. Each task should be named (`name:`) to provide clear execution logs.
* **Module:** The actual tool or plugin that performs the task on the system (e.g., `ansible.builtin.copy`).

### Idiomatic Use of Core Modules
* **Files & Templates:** Use `copy` to transfer static files, `file` to manage directories and permissions, and `template` to generate files dynamically. Use `lineinfile` only for simple, single-line adjustments to existing configuration files.
* **Packages & Services:** Use generic modules like `package` for multi-OS environments, or OS-specific modules like `apt` (Debian/Ubuntu) or `yum` (CentOS/RHEL). Use the `service` or `systemd` modules to manage service states and boot configurations.
* **Command & Shell:** The `command` module is preferred for running binary scripts because it does not load local shell variables, which reduces safety risks. Use `shell` only when you need shell-specific features like pipes, redirects, or environment variables.

### Handlers: Event-Driven Automation State Management
Handlers are special tasks that run only when triggered by another task.
* They are defined in a separate `handlers:` block at the end of a play.
* A task notifies a handler using the `notify` keyword, which references the handler's name.
* The handler only runs if the notifying task reports a status of `changed`.
* Handlers run once at the end of the entire play, preventing services from restarting multiple times during a single playbook run.""",
        "commands": """### Command & Syntax Reference

#### Verify Playbook Syntax
```bash
# Check a playbook for YAML and structure formatting errors without running it
ansible-playbook -i hosts.ini deploy.yml --syntax-check
```

#### Execute a Playbook
```bash
# Run a playbook against hosts defined in your inventory
ansible-playbook -i hosts.ini deploy.yml
```

#### Run in Dry-Run Mode
```bash
# Preview changes that would be made on the target hosts without applying them
ansible-playbook -i hosts.ini deploy.yml --check
```

#### Start Execution at a Specific Task
```bash
# Resume playbook execution starting at a designated task name
ansible-playbook -i hosts.ini deploy.yml --start-at-task="Restart Nginx"
```

#### Run Specific Tagged Tasks
```bash
# Only run tasks that are tagged with the specified identifier
ansible-playbook -i hosts.ini deploy.yml --tags "packages,config"
```""",
        "examples": """### Real-World Examples

#### Example 1: Single-Play Web Server Installation Playbook
* **Situation:** An SRE team needs a simple playbook to install Apache, set up a basic index page, and start the service on Ubuntu servers.
* **Action:** Write a complete, self-contained playbook using standard modules.

```yaml
# deploy_apache.yml
---
- name: Deploy and Enable Apache Web Server
  hosts: webservers
  become: true
  tasks:
    - name: Ensure Apache is installed
      ansible.builtin.apt:
        name: apache2
        state: present
        update_cache: true

    - name: Deploy default index.html index file
      ansible.builtin.copy:
        content: "<html><body><h1>Site configured by Ansible</h1></body></html>\n"
        dest: /var/www/html/index.html
        owner: www-data
        group: www-data
        mode: '0644'

    - name: Ensure Apache is started and enabled on boot
      ansible.builtin.service:
        name: apache2
        state: started
        enabled: true
```

#### Example 2: Linux User and Security Configuration Playbook
* **Situation:** An administrator needs to create a deployment group and user account on all system nodes for application execution.
* **Action:** Build a playbook using the `group`, `user`, and `authorized_key` modules.

```yaml
# configure_users.yml
---
- name: Provision Deployment User Account
  hosts: all
  become: true
  tasks:
    - name: Create the deployers system group
      ansible.builtin.group:
        name: deployers
        state: present
        gid: 2000

    - name: Create system deployment user
      ansible.builtin.user:
        name: deployer
        comment: "Automation Deployer Account"
        uid: 2000
        group: deployers
        shell: /bin/bash
        state: present
        create_home: true

    - name: Authorize administrative public SSH keys
      ansible.posix.authorized_key:
        user: deployer
        state: present
        key: "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOm6SFS+kIWh7bVn6sK5rLh7pD4fXw0nSRE ansible_automation_key"
```

#### Example 3: Multi-Handler Playbook with Configuration Updates
* **Situation:** Configuring a security service requires copying multiple configuration files, and the service must be restarted only if any of those files change.
* **Action:** Define a playbook with task notifications and unified handlers.

```yaml
# configure_ssh.yml
---
- name: Manage Secure SSH Configuration Daemon
  hosts: all
  become: true
  tasks:
    - name: Deploy updated sshd configuration
      ansible.builtin.copy:
        src: files/sshd_config
        dest: /etc/ssh/sshd_config
        owner: root
        group: root
        mode: '0600'
      notify: Restart SSH Service

    - name: Deploy updated banners
      ansible.builtin.copy:
        src: files/issue
        dest: /etc/issue
        owner: root
        group: root
        mode: '0644'
      notify: Restart SSH Service

  handlers:
    - name: Restart SSH Service
      ansible.builtin.service:
        name: sshd
        state: restarted
```

#### Example 4: Directory Creation and Permission Mapping
* **Situation:** A development project requires target directories on server nodes configured with specific permissions and ownership before deployment.
* **Action:** Use the `file` module to construct directories and set properties recursively.

```yaml
# setup_directories.yml
---
- name: Bootstrap Application Directory Trees
  hosts: appservers
  become: true
  tasks:
    - name: Create base storage directory
      ansible.builtin.file:
        path: /opt/app-data
        state: directory
        owner: root
        group: root
        mode: '0755'

    - name: Create specific log storage subfolder
      ansible.builtin.file:
        path: /opt/app-data/logs
        state: directory
        owner: syslog
        group: adm
        mode: '0770'
```

#### Example 5: Multi-Play Execution Orchestrating Web and Database Steps
* **Situation:** A deployment workflow requires updating database servers before updating the front-end web servers.
* **Action:** Combine multiple plays into a single playbook file to enforce order.

```yaml
# deploy_stack.yml
---
- name: Database Configuration Phase
  hosts: dbservers
  become: true
  tasks:
    - name: Check database connection response
      ansible.builtin.command: mysqladmin ping -h localhost
      changed_when: false

- name: Web Application Deployment Phase
  hosts: webservers
  become: true
  tasks:
    - name: Install latest web components
      ansible.builtin.apt:
        name: nginx
        state: present
```""",
        "exercise": """### Hands-On Labs

#### Lab 1: Writing and Parsing a Valid YAML Configuration Playbook
* **Objective:** Create a basic playbook and check its syntax.
* **Tasks:**
  1. In your workspace, create a file named `test_playbook.yml`.
  2. Write a single play targeting `all` that runs a simple debug task printing a message.
  3. Intentionally introduce an indentation error (such as using tabs or misaligning list elements).
  4. Run `ansible-playbook test_playbook.yml --syntax-check`, review the parsing error, fix the indentation, and verify it passes.

#### Lab 2: Standardizing Web Packages and System States
* **Objective:** Install and configure Nginx on a managed host.
* **Tasks:**
  1. Create a playbook named `install_nginx.yml` targeting your local machine or test VMs.
  2. Add tasks to install `nginx` and start the service.
  3. Ensure the task runs with privilege escalation (`become: true`).
  4. Execute the playbook and run it a second time to verify that the tasks show a state of `ok` rather than `changed`.

#### Lab 3: Creating Multi-tier Directory Permissions and Static Configuration Copies
* **Objective:** Manage directories, files, and permissions on remote hosts.
* **Tasks:**
  1. Create a workspace directory `files/` and add a text file named `app_config.conf`.
  2. Write a playbook `file_manager.yml` to create a `/var/app/` directory with `0755` permissions.
  3. Add a task to copy `files/app_config.conf` to `/var/app/app_config.conf` with `0644` permissions.
  4. Run the playbook and verify the file and directory are created with the correct permissions.

#### Lab 4: Triggering Event-Driven Configuration Reloads using Handlers
* **Objective:** Use handlers to restart a service only when configuration files change.
* **Tasks:**
  1. Extend your Nginx deployment playbook from Lab 2.
  2. Add a task that uses the `copy` module to deploy a custom configuration file to `/etc/nginx/nginx.conf`.
  3. Add a `notify` statement pointing to a handler named "Restart Nginx Service".
  4. Add the `handlers:` section to restart Nginx. Run the playbook twice to confirm the handler only runs when the file is copied or updated.

#### Lab 5: Running Playbooks in Dry-Run and Specific Tags Filter Modes
* **Objective:** Test and filter playbook execution using tags and check mode.
* **Tasks:**
  1. Edit your playbook and add tags to your tasks (e.g., `tags: packages` on the install task and `tags: configuration` on the copy task).
  2. Run the playbook in dry-run mode using `ansible-playbook -i hosts.ini install_nginx.yml --check`.
  3. Verify that no changes are applied to your system.
  4. Execute only the configuration tasks using `ansible-playbook -i hosts.ini install_nginx.yml --tags "configuration"`.""",
        "insight": """### Interview Q&A

#### Q1: What makes a playbook task idempotent, and why is this concept foundational to Ansible?
* **Answer:** A task is idempotent if running it multiple times produces the same final state without making unnecessary changes. Idempotence ensures that if a system is already in the desired state, Ansible does nothing. This prevents configuration drift, keeps systems stable, and avoids disruptions like restarting healthy services.

#### Q2: What are the differences between command, shell, and raw modules, and when is each appropriate?
* **Answer:** 
  * `command` runs a binary command directly on the remote system. It is secure and avoids shell-specific errors because it does not run through a shell process like `/bin/sh`.
  * `shell` runs commands through the remote shell environment. Use it only when you need shell features like pipes (`|`), redirection (`>`), or environment variables.
  * `raw` executes commands directly through the SSH connection channel, bypassing the Python subsystem entirely. Use it only to bootstrap Python on newly provisioned machines.

#### Q3: How do Ansible Handlers ensure that a service is only restarted once, even if multiple tasks declare notify?
* **Answer:** Ansible queues notified handlers during execution and runs them once at the end of the play, regardless of how many tasks notified them. This prevents services from restarting multiple times during a single playbook run. Handlers only execute if at least one of the notifying tasks actually changes the system's state.

#### Q4: What is the impact of running ansible-playbook with the --check flag, and are there tasks it cannot test?
* **Answer:** The `--check` flag enables dry-run mode, where modules report what changes they *would* make without actually applying them. However, tasks that depend on the output of previous steps (such as running a command and registering its output) may fail because those previous steps were not actually executed.

#### Q5: How do you force handlers to run immediately before the play completes?
* **Answer:** You can force queued handlers to run immediately by adding a task that calls the `meta` module with the `flush_handlers` argument. This is useful when a service must be restarted and verified before subsequent tasks in the play can proceed.

### Ansible Certification Focus
* **Core Topic:** Understand YAML syntax and structure. Expect questions requiring you to find syntax errors in playbooks, such as missing colons or bad indentation.
* **Best Practice:** Always name your tasks clearly. This serves as self-documentation and makes execution logs easy to follow and debug."""
    },
    {
        "id": 4,
        "title": "Module 4: Variables, Facts, & Control Flow",
        "theory": """### Understanding Variable Precedence
Ansible provides a highly flexible variable system, but as a result, variables can be defined in multiple places. To resolve conflicts, Ansible uses a strict variable precedence hierarchy with 22 levels. The most common levels, ordered from lowest precedence to highest precedence, are:
1. Group variables defined in inventories (`group_vars/all`).
2. Group variables defined in child groups (`group_vars/webservers`).
3. Host variables defined in inventories (`host_vars/host`).
4. Playbook variables defined within a play's `vars` block.
5. Variables loaded from external files via `vars_files`.
6. Variables registered during execution using the `register` keyword.
7. Extra variables passed on the command line using `-e` or `--extra-vars` (which always win).

### Ansible Facts: Dynamic Infrastructure Inspection
When a playbook runs, Ansible automatically executes a setup task before the first user-defined task. This step gathers **facts**—detailed system metadata from the managed node, such as:
* Operating system distribution, release, and kernel versions.
* Network interface names, IP addresses, and MAC addresses.
* CPU core counts, total system memory, and available disk storage.

These facts are stored in the read-only `ansible_facts` variable and can be used to make dynamic configuration decisions. Collecting facts takes time, so if your playbook does not need system metadata, you can speed up execution by setting `gather_facts: false` in your play.

### Conditional Logic Execution with 'when'
Conditionals allow you to execute tasks only when specific criteria are met. In Ansible, this is handled using the `when` statement at the task level.
`when` expressions are evaluated using Jinja2 syntax (without curly braces). They can test:
* Gathered system facts (e.g., `when: ansible_facts['os_family'] == "Debian"`).
* The status of registered variables (e.g., `when: task_result.changed`).
* Custom boolean flags (e.g., `when: is_production_node`).

### Iterative Operations using 'loop' and Filters
Instead of writing repetitive tasks to perform the same action on multiple items (like installing five different packages), you can use the `loop` keyword.
* The task iterates over a list of items, and the current item is accessed using the `item` variable.
* You can apply **Jinja2 filters** (like `| default()`, `| lower`, or `| unique`) to transform your data on the fly.
* Modern Ansible uses the simple `loop` keyword instead of legacy, deprecated loop styles like `with_items`, `with_dict`, or `with_subelements`.""",
        "commands": """### Command & Syntax Reference

#### Query System Facts (Ad-Hoc Setup)
```bash
# Dump all gathered system facts for a host to raw JSON
ansible localhost -m ansible.builtin.setup
```

#### Filter Gathered Facts
```bash
# Retrieve only memory-related system facts from target servers
ansible webservers -i hosts.ini -m ansible.builtin.setup -a "filter=ansible_memtotal_mb"
```

#### Run Playbook with Extra Variables
```bash
# Pass high-precedence variables directly to a playbook execution
ansible-playbook -i hosts.ini deploy.yml -e "app_version=2.4.1 environment_tier=production"
```

#### Debug a Variable's Value
```bash
# Output the current value of a variable during playbook execution
ansible-playbook -i hosts.ini deploy.yml --start-at-task="Debug variable value"
```""",
        "examples": """### Real-World Examples

#### Example 1: Conditional Package Installation Based on OS Family Fact
* **Situation:** A playbook must support both Ubuntu and CentOS systems, which use different package names for the Apache web server.
* **Action:** Use the `ansible_facts['os_family']` system fact to conditionally run the correct package installation task.

```yaml
# deploy_web_multi_os.yml
---
- name: Multi-OS Apache Installation
  hosts: webservers
  become: true
  tasks:
    - name: Install Apache on Debian-based systems
      ansible.builtin.apt:
        name: apache2
        state: present
      when: ansible_facts['os_family'] == "Debian"

    - name: Install Apache on RedHat-based systems
      ansible.builtin.yum:
        name: httpd
        state: present
      when: ansible_facts['os_family'] == "RedHat"
```

#### Example 2: Iterating Over System Packages and User Configurations via Loops
* **Situation:** An administrator needs to install multiple diagnostic packages and create several system user accounts in a single task block.
* **Action:** Use the `loop` keyword to iterate over a list of strings and a list of structured dictionaries.

```yaml
# bootstrap_tools.yml
---
- name: Bootstrap Core System Tools
  hosts: all
  become: true
  tasks:
    - name: Install required diagnostic packages
      ansible.builtin.package:
        name: "{{ item }}"
        state: present
      loop:
        - htop
        - sysstat
        - nmap
        - tcpdump

    - name: Configure developer administrative accounts
      ansible.builtin.user:
        name: "{{ item.username }}"
        uid: "{{ item.uid }}"
        shell: /bin/bash
        state: present
      loop:
        - { username: 'alice', uid: 3001 }
        - { username: 'bob', uid: 3002 }
        - { username: 'charlie', uid: 3003 }
```

#### Example 3: Capturing Task Output and Registering Variables
* **Situation:** A deployment process requires checking if a directory exists and only running a secondary configuration script if the directory is missing.
* **Action:** Register the output of the directory check and use it in a conditional `when` statement on the next task.

```yaml
# conditional_setup.yml
---
- name: Conditional Application Configuration
  hosts: appservers
  become: true
  tasks:
    - name: Check if application directory exists
      ansible.builtin.stat:
        path: /var/app/data
      register: app_directory_status

    - name: Create directory if it does not exist
      ansible.builtin.file:
        path: /var/app/data
        state: directory
        owner: deployer
        group: deployers
        mode: '0755'
      when: not app_directory_status.stat.exists

    - name: Log directory status check
      ansible.builtin.debug:
        msg: "Directory existence state: {{ app_directory_status.stat.exists }}"
```

#### Example 4: Dynamically Rendering a Jinja2 Template Using Facts
* **Situation:** A system must deploy a dynamic "Message of the Day" (`/etc/motd`) file displaying the host's actual memory, CPU, and network interface facts.
* **Action:** Create a Jinja2 template that references system facts, and deploy it using the `template` module.

```jinja2
# templates/motd.j2 (This file is stored in your templates folder)
========================================================================
Welcome to {{ ansible_facts['hostname'] }}
Operating System: {{ ansible_facts['distribution'] }} {{ ansible_facts['distribution_version'] }}
Total Memory:     {{ ansible_facts['memtotal_mb'] }} MB
Primary IP:       {{ ansible_facts['default_ipv4']['address'] }}
Managed by Ansible. Unauthorised access is prohibited.
========================================================================
```

```yaml
# deploy_motd.yml
---
- name: Deploy Dynamic System Banners
  hosts: all
  become: true
  tasks:
    - name: Deploy dynamic MOTD template file
      ansible.builtin.template:
        src: templates/motd.j2
        dest: /etc/motd
        owner: root
        group: root
        mode: '0644'
```

#### Example 5: High-Precedence Playbook Variables Overriding Defaults
* **Situation:** An operations manager needs to set default application parameters in a vars file but allow developer overrides during specific automated deployments.
* **Action:** Build a playbook with defined vars blocks and show how to override them at runtime.

```yaml
# deploy_app.yml
---
- name: Deploy Configured Web Service
  hosts: webservers
  vars:
    app_port: 8080
    deploy_env: development
  tasks:
    - name: Print current targeted deployment environment info
      ansible.builtin.debug:
        msg: "Deploying port {{ app_port }} to {{ deploy_env }} environment tier."
```
*(To override these settings at runtime, run: `ansible-playbook -i hosts.ini deploy_app.yml -e "app_port=443 deploy_env=production"`)*""",
        "exercise": """### Hands-On Labs

#### Lab 1: Extracting and Filtering Specific Host Facts
* **Objective:** Use the setup module to view and filter system facts.
* **Tasks:**
  1. Open a terminal and run the ad-hoc command to query your local host's facts: `ansible localhost -m ansible.builtin.setup`.
  2. Filter the output to display only network interface facts using `ansible localhost -m ansible.builtin.setup -a "filter=ansible_interfaces"`.
  3. Locate the variable name that stores your system's operating system distribution (e.g., `ansible_facts['distribution']`).

#### Lab 2: Writing a Multi-OS Conditional Task Execution Playbook
* **Objective:** Create a playbook that runs different tasks depending on the target OS.
* **Tasks:**
  1. Write a playbook named `os_diagnostic.yml` that gathers system facts.
  2. Add a task that runs a shell command only on systems where the `os_family` is RedHat.
  3. Add a second task that runs only on systems where the `os_family` is Debian.
  4. Run the playbook against your local machine to verify that only the task matching your operating system family executes.

#### Lab 3: Implementing Advanced Loops with Dictionaries
* **Objective:** Use loops to create multiple system directories with different permissions and ownership.
* **Tasks:**
  1. Create a playbook named `directory_loop.yml`.
  2. Define a list of dictionaries, where each dictionary contains a directory path, target owner, and permission mode.
  3. Use the `loop` keyword to iterate over this list, and reference your variables using `item.path`, `item.owner`, and `item.mode`.
  4. Run the playbook to create the directories and verify they are configured correctly.

#### Lab 4: Tracking Executed Command States and Conditionals
* **Objective:** Capture a command's output and use it to decide whether to run a subsequent task.
* **Tasks:**
  1. Write a playbook that runs a command checking if a specific user account exists (e.g., `id deployer`). Use `ignore_errors: true` so the task doesn't stop the playbook if the user is missing.
  2. Register the output of this task into a variable named `user_check`.
  3. Add a task to create the user only when the check fails (e.g., `when: user_check.rc != 0`).
  4. Run the playbook to confirm the user is created only when missing.

#### Lab 5: Generating a Comprehensive Dynamic Motd using Jinja2
* **Objective:** Render and deploy a dynamic banner template using gathered system facts.
* **Tasks:**
  1. Create a `templates` directory in your workspace.
  2. Inside `templates`, create a file named `system_banner.j2` that displays your system's hostname, OS, and total memory.
  3. Write a playbook that uses the `template` module to copy `system_banner.j2` to `/tmp/motd`.
  4. Run the playbook and verify that `/tmp/motd` contains the correct system metadata.""",
        "insight": """### Interview Q&A

#### Q1: What is the practical hierarchy of variables inside Ansible, and which wins between group_vars and playbook variables?
* **Answer:** Ansible has a strict variable precedence hierarchy with 22 levels. In practice, variables defined directly in the playbook's `vars` block have higher precedence and will override variables defined in `group_vars/` or `host_vars/` directory files. To override playbook variables, you must pass extra variables on the command line using the `-e` or `--extra-vars` flag.

#### Q2: Why would you disable fact gathering in a playbook, and what are the benefits and consequences?
* **Answer:** Gathering facts sends an initial request to collect system metadata from every managed node, which can slow down executions in large environments. You can disable this by setting `gather_facts: false` on the play. This speeds up execution, but it means you cannot use system facts (such as OS family, network configurations, or disk space) in your tasks or templates.

#### Q3: How can you check if a registered variable was successfully changed or failed in a conditional expression?
* **Answer:** When you register a task's output using the `register` keyword, the resulting variable contains several properties. You can test these in a conditional statement using properties like `variable_name.changed` (boolean), `variable_name.failed` (boolean), or `variable_name.rc` (the shell return code, where 0 indicates success).

#### Q4: What are Jinja2 filters, and how do you use them to transform variables in a task?
* **Answer:** Jinja2 filters are functions used to modify, format, or transform variables. They are applied using the pipe symbol (`|`). For example, you can convert a string to lowercase using `{{ my_variable | lower }}`, or provide a fallback value if a variable is undefined using `{{ port | default(80) }}`.

#### Q5: How do you loop over a nested dictionary or run multi-variable loops in Modern Ansible?
* **Answer:** You can loop over a dictionary by applying the `dict2items` filter to the dictionary variable, which converts it into a standard list of key-value pairs that the `loop` keyword can process. You can access individual properties inside the loop using `item.key` and `item.value`.

### Ansible Certification Focus
* **Core Topic:** Understand how to use system facts in conditionals and how variable precedence resolves conflicts. Expect questions asking you to predict which variable value wins when defined in multiple places.
* **Best Practice:** Keep fact gathering enabled only when your playbook needs to make dynamic decisions based on system metadata; disable it to speed up execution when managing large environments."""
    },
    {
        "id": 5,
        "title": "Module 5: Basic Secret Management",
        "theory": """### The Need for Secret Management in GitOps
Modern operations teams rely on Git to manage infrastructure configuration files (GitOps). However, committing plain-text secrets (such as API tokens, database passwords, and private SSH keys) to a shared version control system creates a severe security vulnerability.

To prevent credential leaks while still keeping configurations in version control, Ansible provides **Ansible Vault**. This built-in tool encrypts sensitive files and variables at rest, allowing you to safely store them in Git and decrypt them dynamically at runtime.

### How Ansible Vault Encrypts Data
Ansible Vault uses symmetrical encryption (**AES-256**) to secure data. The same password used to encrypt the file is required to decrypt and read it at runtime.
Ansible Vault supports two main encryption workflows:
1. **File-level Encryption:** Encrypts an entire YAML or text file (such as a database variables file containing usernames, hostnames, and passwords). This is easy to manage but hides the file's structure in Git diffs.
2. **Variable-level (Inline) Encryption:** Encrypts only a single, specific string value within an otherwise unencrypted, human-readable YAML file. This allows you to track changes to other configuration parameters in Git while keeping individual sensitive values secure.

### Command Line Vault Workflows
The `ansible-vault` command-line utility provides tools to manage encrypted files:
* `create`: Generates a new encrypted file.
* `encrypt`: Encrypts an existing plain-text file.
* `decrypt`: Permanently converts an encrypted file back to plain text.
* `edit`: Decrypts a file on the fly into a temporary text editor, saving changes securely without writing decrypted data to disk.
* `view`: Displays the decrypted content in the console without modifying the file.

### SRE Best Practices for Storing and Running Vault Secrets
* **Password Management:** Never commit your Ansible Vault password to Git. Instead, store it in a secure password manager or key vault.
* **Automated Runs:** For automated environments like CI/CD pipelines, you can store the Vault password in a secure file on the Control Node and reference it using the `--vault-password-file` argument. Ensure the password file has strict permissions (`chmod 600`) so it is only readable by the Ansible execution user.
* **Multiple Vaults:** In complex environments, you can define multiple vault passwords (e.g., one for development and one for production) using unique Vault IDs to isolate environments.""",
        "commands": """### Command & Syntax Reference

#### Create a New Encrypted File
```bash
# Initialize a new encrypted YAML file and prompt for a password
ansible-vault create vars/secrets.yml
```

#### Encrypt an Existing Plain-text File
```bash
# Secure an existing file using AES-256 encryption
ansible-vault encrypt vars/db_credentials.yml
```

#### Edit an Encrypted File Safely
```bash
# Open an encrypted file in your terminal editor without decrypting it on disk
ansible-vault edit vars/secrets.yml
```

#### View Encrypted File Contents
```bash
# Display the decrypted contents of a file without saving it to disk
ansible-vault view vars/secrets.yml
```

#### Generate an Inline Encrypted String
```bash
# Generate an encrypted string value to paste into an unencrypted playbook
ansible-vault encrypt_string "SuperSecretPassword123" --name "db_password"
```

#### Run Playbook with Password Prompt
```bash
# Run a playbook and prompt for the Vault decryption password at startup
ansible-playbook -i hosts.ini deploy.yml --ask-vault-pass
```

#### Run Playbook with a Password File
```bash
# Run a playbook using a secure, local file to automatically decrypt secrets
ansible-playbook -i hosts.ini deploy.yml --vault-password-file ~/.vault_pass.txt
```""",
        "examples": """### Real-World Examples

#### Example 1: Completely Encrypted Configuration Variables File (secrets.yml)
* **Situation:** An administrator needs to encrypt a complete file containing sensitive database credentials before committing it to a Git repository.
* **Action:** Create a standard variables file containing the passwords, and then run `ansible-vault encrypt` on it.

```yaml
# vars/secrets.yml (After running ansible-vault encrypt, the file looks like this in Git)
$ANSIBLE_VAULT;1.1;AES256
38656133643762396131366531396263306161646639656132643564613261626233633534346535
3333333364383461623962663162613539316335356130380a656663363234633737636166316639
33636531643465393466316465383561366162306236616437343461323334643033626265333062
3962363065663731330a343538356338303332306338363836373562623164636561656534636235
6566
```
*(When decrypted using `ansible-vault view vars/secrets.yml`, the content is:)*
```yaml
# vars/secrets.yml (Decrypted View)
---
vault_db_user: "db_admin_prod"
vault_db_password: "MySecureProductionPassword987!"
vault_api_key: "api-key-abc123xyz"
```

#### Example 2: Single Inline Encrypted Variable (String Level Encryption)
* **Situation:** A team wants to keep a playbook's configuration parameters public and readable in Git while encrypting only the database password string.
* **Action:** Generate an encrypted string using `ansible-vault encrypt_string` and paste it directly into the playbook's variable block.

```yaml
# deploy_app_inline_secrets.yml
---
- name: Deploy Secure Application Service
  hosts: appservers
  vars:
    app_port: 9000
    db_username: "app_user"
    # This string is the encrypted representation of the password
    db_password: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          62653231366264393663666632336132343834316637376335393134633031316635393036663435
          6133373966373134646164366637653531393635356434310a623135363032336636363636343031
          31363666623661633433613661333932373738613464613765353633343864313235613735613861
          3564616561653830380a653434333630373461356631623930316466653063373832326531306337
          6139
  tasks:
    - name: Show that unencrypted metadata is readable
      ansible.builtin.debug:
        msg: "Deploying to port {{ app_port }} with database user {{ db_username }}"
```

#### Example 3: Playbook Loading Encrypted YAML Secrets
* **Situation:** An SRE wants to load secure credentials from an encrypted external file and use those variables in an active deployment play.
* **Action:** Use the `vars_files` block to import variables from an encrypted file.

```yaml
# deploy_with_secret_file.yml
---
- name: Deploy Application with External Secrets
  hosts: appservers
  become: true
  vars_files:
    - vars/secrets.yml
  tasks:
    - name: Ensure database user is present on target system
      ansible.builtin.user:
        name: "{{ vault_db_user }}"
        password: "{{ vault_db_password | password_hash('sha512') }}"
        shell: /bin/bash
        state: present
```

#### Example 4: Automating Decryption in CI/CD using Password Files
* **Situation:** A DevOps pipeline runner must execute a deployment playbook that uses encrypted secrets without manual intervention.
* **Action:** Store the Vault password in a secure file on the pipeline runner and reference it in the execution command.

```bash
# Step 1: Create a secure password file with strict permissions on the runner
echo "MyVaultPassword123!" > ~/.vault_pass.txt
chmod 600 ~/.vault_pass.txt

# Step 2: Execute the playbook using the password file
ansible-playbook -i hosts.ini deploy_with_secret_file.yml --vault-password-file ~/.vault_pass.txt
```

#### Example 5: Playbook Using Multi-Vault ID Passwords
* **Situation:** An infrastructure team uses different encryption passwords for development and production environments, and needs to run a playbook that accesses variables from both.
* **Action:** Tag files with specific Vault IDs, and run the playbook referencing those IDs.

```bash
# Step 1: Create dev secrets with the 'dev' vault ID
ansible-vault create --vault-id dev@prompt vars/dev_secrets.yml

# Step 2: Create production secrets with the 'prod' vault ID
ansible-vault create --vault-id prod@prompt vars/prod_secrets.yml

# Step 3: Run the playbook and prompt for passwords for both environments
ansible-playbook -i hosts.ini deploy.yml --vault-id dev@prompt --vault-id prod@prompt
```""",
        "exercise": """### Hands-On Labs

#### Lab 1: Encrypting and Decrypting Complete Group Variable Files
* **Objective:** Secure a group variables file using Ansible Vault.
* **Tasks:**
  1. Inside your workspace, create a file named `vars/vault_secrets.yml`.
  2. Add some sensitive key-value pairs (e.g., `db_pass: "SecurePassword"`).
  3. Run `ansible-vault encrypt vars/vault_secrets.yml` and set a password.
  4. Open the file in a text editor to confirm that the contents are fully encrypted and no plain-text strings are visible.
  5. Run `ansible-vault decrypt vars/vault_secrets.yml` to return it to plain text.

#### Lab 2: Creating and Using Inline Encrypted Strings
* **Objective:** Secure an individual variable string while keeping the rest of the configuration file readable.
* **Tasks:**
  1. Open a terminal on your Control Node.
  2. Run `ansible-vault encrypt_string "SecretAdminPassword" --name "admin_password"`.
  3. Copy the output block generated by the command.
  4. Create a playbook named `deploy_admin.yml` and paste the copied block into the `vars` section.
  5. Add a debug task to print the value of `admin_password` to verify it decrypts successfully.

#### Lab 3: Running a Vault-Secured Playbook Deploying Database Configurations
* **Objective:** Execute a playbook that loads and decrypts variable values at runtime.
* **Tasks:**
  1. Create an encrypted variables file `vars/db_secrets.yml` containing a single variable `database_root_password: "DBAdminPassword1!"`.
  2. Write a playbook `setup_db.yml` that references `vars/db_secrets.yml` in its `vars_files` block.
  3. Add a task that prints a message containing the decrypted variable.
  4. Run the playbook using `ansible-playbook setup_db.yml --ask-vault-pass` and enter your password.

#### Lab 4: Securing and Utilizing Password Files via Local Host Configurations
* **Objective:** Automate playbook execution using a secure password file.
* **Tasks:**
  1. Create a password file on your system named `~/.vault_key` containing your vault decryption password.
  2. Set strict file permissions on the password file: `chmod 600 ~/.vault_key`.
  3. Create an environment variable pointing to the password file: `export ANSIBLE_VAULT_PASSWORD_FILE=~/.vault_key`.
  4. Run your `setup_db.yml` playbook without passing any extra CLI arguments. Verify that it decrypts the variables and runs successfully without prompting you for a password.

#### Lab 5: Implementing Password Rekeying across Multiple Encrypted Files
* **Objective:** Change the password of an encrypted vault file without losing its contents.
* **Tasks:**
  1. Create an encrypted file `vars/old_secrets.yml` using the password `OldPassword123!`.
  2. Run the command `ansible-vault rekey vars/old_secrets.yml`.
  3. Enter the old password, and then set a new password when prompted.
  4. Run `ansible-vault view vars/old_secrets.yml` using the new password to verify that the file's contents are intact and accessible.""",
        "insight": """### Interview Q&A

#### Q1: What algorithm does Ansible Vault use to encrypt variables, and is it safe to commit encrypted files to Git?
* **Answer:** Ansible Vault uses symmetrical Advanced Encryption Standard with a 256-bit key (AES-256) to secure data. Because this is a robust encryption standard, it is safe to commit vault-encrypted files to Git repositories, provided you use strong, complex passwords that cannot be easily brute-forced.

#### Q2: How can we feed multiple different passwords to Ansible for distinct vaults in the same execution?
* **Answer:** You can handle multiple passwords by defining vault IDs. Using the `--vault-id` flag, you can tag each encrypted file with a label (e.g., `dev` or `prod`) and map each label to a different password file or prompt: `ansible-playbook deploy.yml --vault-id dev@~/.dev_pass --vault-id prod@~/.prod_pass`.

#### Q3: What is the security risk of leaving the vault password file with loose permissions on the Control Node?
* **Answer:** If the password file has loose permissions (like `0644`), other users or processes on the Control Node can read the file and extract the vault password, compromising the security of your encrypted configurations. SRE guidelines dictate setting strict file permissions (`chmod 600`) so that only the owner can read or write to the file.

#### Q4: How do you view the content of an encrypted vault file without completely decrypting it on disk?
* **Answer:** You can view the contents of an encrypted file using the `ansible-vault view <filename>` command. This decrypts the data temporarily in your terminal window but does not write the decrypted content to disk, keeping your secrets secure.

#### Q5: What is the optimal SRE workflow for managing Vault passwords in a collaborative engineering team?
* **Answer:** For collaborative teams, SRE best practices involve storing vault passwords in a centralized secret manager (such as HashiCorp Vault, AWS Secrets Manager, or a secure team password manager). Access to password files on control nodes should be restricted using local file system permissions, and temporary pipeline runs should load secrets dynamically using secure environment variables or short-lived tokens.

### Ansible Certification Focus
* **Core Topic:** Understand the different `ansible-vault` command-line operations (`create`, `encrypt`, `decrypt`, `edit`, `rekey`). Expect questions requiring you to identify the correct syntax for these operations.
* **Best Practice:** SRE guidelines dictate using variable-level (inline) encryption for minor changes. This keeps your configuration files readable in Git and preserves clear revision history while securing sensitive values."""
    }
]