COURSE_ID = "ansible"
COURSE_TITLE = "Ansible IT Automation"
COURSE_DESCRIPTION = "Master IT automation, configuration management, and application deployment with Ansible playbooks, roles, and vault."

CURRICULUM_DATA = [
    {
        "id": 1,
        "title": "Ansible Fundamentals & Playbooks",
        "theory": """### Core Concepts
Ansible is an agentless automation engine that automates software provisioning, configuration management, and application deployment. It communicates over standard SSH (or WinRM on Windows) and uses declarative YAML playbooks to define system states.

Key pillars of Ansible include:
- **Inventory**: A list of managed target nodes.
- **Playbooks**: Declared configuration files written in YAML.
- **Modules**: Units of code executed on remote hosts (e.g., `apt`, `yum`, `copy`, `service`).
- **Idempotency**: The guarantee that running an operation multiple times leaves the system in the same state without unintended side effects.""",
        "commands": """```bash
# Ping all hosts in the inventory to test connectivity
ansible all -m ping -i inventory.ini

# Run an ad-hoc command to check memory usage on all webservers
ansible webservers -a "free -m" -i inventory.ini

# Execute a playbook using a specific inventory
ansible-playbook deploy.yml -i inventory.ini
```""",
        "examples": """### Real-World Scenarios

#### Scenario 1: Basic Package Installation and Service Management
Ensure Apache is installed, enabled, and started on web servers.
```yaml
- name: Configure Web Server
  hosts: webservers
  tasks:
    - name: Install Apache
      apt:
        name: apache2
        state: present
    - name: Start Apache
      service:
        name: apache2
        state: started
        enabled: yes
```

#### Scenario 2: Synchronizing Configuration Files with Handlers
Copy a configuration file and restart the service only if the configuration changes.
```yaml
- name: Update Configuration
  hosts: webservers
  tasks:
    - name: Copy Nginx Config
      copy:
        src: nginx.conf
        dest: /etc/nginx/nginx.conf
      notify: Restart Nginx
  handlers:
    - name: Restart Nginx
      service:
        name: nginx
        state: restarted
```

#### Scenario 3: Creating and Managing System Users Safely
Create system users with specific shell configurations and public SSH keys.
```yaml
- name: Create Deployer User
  hosts: all
  tasks:
    - name: Add Deployer Group
      group:
        name: deployers
        state: present
    - name: Create User
      user:
        name: deployer
        group: deployers
        shell: /bin/bash
    - name: Authorize SSH Key
      authorized_key:
        user: deployer
        state: present
        key: "{{ lookup('file', '~/.ssh/id_rsa.pub') }}"
```

#### Scenario 4: Setting Up an Automated Database Backup Cron Job
Deploy a shell script and define a cron entry for system database backups.
```yaml
- name: Database Backup Cron
  hosts: dbservers
  tasks:
    - name: Copy backup script
      copy:
        src: backup.sh
        dest: /usr/local/bin/backup.sh
        mode: '0755'
    - name: Schedule Daily Cron
      cron:
        name: "Database backup"
        minute: "0"
        hour: "2"
        job: "/usr/local/bin/backup.sh"
```

#### Scenario 5: Using Vault for Encrypted Sensitive Variables
Load encrypted credentials securely using Ansible Vault variables during playbooks execution.
```yaml
- name: Secure Database Provisioning
  hosts: dbservers
  vars_files:
    - vault_secrets.yml
  tasks:
    - name: Configure DB Credentials
      mysql_user:
        name: dbadmin
        password: "{{ vault_db_password }}"
        priv: '*.*:ALL'
        state: present
```""",
        "exercise": """### Lab Assignment
1. **Setup Inventory**: Create a static file named `inventory.ini` mapping `localhost` under a group named `[local]`. Include the `ansible_connection=local` parameter to prevent external SSH requirements.
2. **Package Tracking Playbook**: Write a basic playbook named `install_git.yml` that targets the `local` host group and ensures that the `git` package is present on the system.
3. **Deploy Web Page**: Create a playbook called `deploy_page.yml` to write a custom string to `/tmp/index.html` using the Ansible `copy` or `template` module.
4. **Handler Implementation**: Extend your `deploy_page.yml` playbook to trigger a message log via the `debug` module as a handler whenever `/tmp/index.html` is modified.
5. **Variable Protection**: Use the command `ansible-vault create secret.yml` to define a secure credential variable, and practice running a configuration task reading from this encrypted file.""",
        "insight": """### Certified Prep Queries
**Q1: Explain Ansible's agentless architecture and its primary benefits.**

**A1:** Ansible is agentless because it does not require background software (agents) to be installed on remote targets. It leverages standard communication protocols like SSH (Linux) or WinRM (Windows) to push short ephemeral execution modules, reducing administrative overhead and boosting system security.

**Q2: What is idempotency and how does it protect remote infrastructure?**

**A2:** Idempotency ensures that running an automation sequence multiple times yields the exact same state without producing unintended actions (such as duplicating lines in files or repeatedly restarting running services). It checks actual status before executing state modifications.

**Q3: How do Ansible Handlers differ from normal Tasks, and when do they execute?**

**A3:** Tasks execute sequentially in the order they are defined. Handlers are special tasks that only execute at the end of a play if they are notified by a parent task that recorded a state change (indicated by `changed` status in the execution output).

**Q4: What is the purpose of Ansible Vault and how do you use it in execution?**

**A4:** Ansible Vault provides symmetric encryption to shield sensitive variables, passwords, or files stored in git repositories. Playbooks referencing these variables are run by providing the password dynamically using the `--ask-vault-pass` flag.

**Q5: How does the `serial` keyword work in multi-node playbook execution?**

**A5:** The `serial` directive controls the batch sizing of playbook tasks across your host list. Instead of running all tasks concurrently on all inventory nodes, Ansible executes the entire play on a limited batch size (e.g., 1 or 2 servers at a time), which is ideal for zero-downtime rolling upgrades."""
    }
]