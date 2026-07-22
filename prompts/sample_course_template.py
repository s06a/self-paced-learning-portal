COURSE_ID = "ansible"
COURSE_TITLE = "Ansible IT Automation"
COURSE_DESCRIPTION = "Master IT automation, configuration management, and application deployment with Ansible playbooks, roles, and vault."

CURRICULUM_DATA = [
    {
        "id": 1,
        "title": "Ansible Fundamentals & Playbooks",
        "theory": """### Guided Conceptual Walkthrough
Imagine you are a head chef managing ten identical kitchens across a hotel chain. If you need to update the recipe for a signature dish or ensure a specific set of knives is sharpened, you have two choices:
1. **The Imperative Approach (SSH scripts):** Run from kitchen to kitchen, yelling instructions to individual cooks, hoping they perform the tasks correctly and in the exact order. If a cook is halfway done and gets interrupted, the kitchen is left in a broken, half-configured state.
2. **The Declarative Approach (Ansible):** Write a single, clear "state of the kitchen" master manual (a Playbook). You send this manual to a dedicated chef assistant (Ansible Controller) who checks each kitchen. If Kitchen #3 already has the knives sharpened, the assistant leaves them alone. If Kitchen #5 is missing the new recipe, the assistant updates it. This is **Idempotency**—only making changes where the current state does not match the desired final state.

### Architectural & Flow Blueprint
The following diagram illustrates how Ansible runs agentlessly from your control node to target nodes over SSH:

```mermaid
graph TD
    subgraph Control Node
        A[Ansible Playbook<br>Desired State] -->|Reads Hosts| B[Inventory.ini<br>Target IPs]
    end
    A -->|SSH Protocol / SFTP / Agentless<br>Pushes Python modules| Target1[Host #1<br>Web Server]
    A -->|SSH Protocol / SFTP / Agentless<br>Pushes Python modules| Target2[Host #2<br>Web Server]
    A -->|SSH Protocol / SFTP / Agentless<br>Pushes Python modules| Target3[Host #3<br>DB Server]
```

### Core Mechanics & Under-the-Hood Operations
When you execute `ansible-playbook`:
1. **Inventory Parsing**: Ansible reads your host definitions.
2. **Connection Handshake**: Ansible opens an SSH session to each target node in parallel (controlled by the `forks` parameter, default is 5).
3. **Fact Gathering**: Ansible copies a small module called `setup` to the target, executes it, and retrieves comprehensive target environment facts (CPU, OS version, disk mounts, IPs) stored as `ansible_facts`.
4. **Module Generation & Transfer**: For each task, Ansible wraps the corresponding Python module code (e.g., `apt` or `copy`) into a temporary script, transfers it via SFTP/SCP to `/tmp`, and changes permissions to make it executable.
5. **Execution & Cleanup**: The target Python interpreter executes the module. It outputs JSON containing status flags (`changed: true/false`, `failed: true/false`, and details). Ansible captures the JSON, removes the temporary Python files from `/tmp`, and displays the formatted terminal output.

### Deep-Dive Explanations (Advanced Context)
<details>
<summary>Click to expand: Understanding SSH ControlPath & Pipelining</summary>
By default, SSH closes and opens connections for every task, adding massive latency. To scale Ansible to hundreds of nodes, you can enable <strong>SSH Pipelining</strong> in <code>ansible.cfg</code>. This executes modules by piping them directly into the remote shell stdin instead of transferring them via SFTP/SCP, cutting down round-trips. Combine this with <strong>ControlPersist</strong> to keep SSH multiplexing sockets alive across multiple playbook plays, boosting speed by up to 400%.
</details>

<details>
<summary>Click to expand: The setup module and Fact Caching</summary>
Fact gathering is slow. If your playbooks do not use variables like <code>{{ ansible_distribution }}</code>, you can disable fact gathering entirely using <code>gather_facts: no</code> on your play. Alternatively, configure <strong>Fact Caching</strong> in <code>ansible.cfg</code> using Redis or local JSON files to persist facts across runs so you only query the remote OS once per day.
</details>

### Common Pitfalls & Troubleshooting

#### Pitfall 1: Unreachable Hosts / SSH Host Key Verification Failure
* **Error Message:**
  `fatal: [192.168.1.50]: UNREACHABLE! => {"changed": false, "msg": "Failed to connect to the host via ssh: Host key verification failed.", "unreachable": true}`
* **Why it happens:** The control node has not seen the SSH fingerprint of the target node, or the fingerprint has changed, causing SSH to block interactively.
* **Resolution:** You can disable Host Key Checking in `ansible.cfg` (recommended only for trusted, local test environments) or pre-seed your `known_hosts` file:
  ```ini
  # Add this to ansible.cfg under [defaults]
  host_key_checking = False
  ```
  Or run manually: `ssh-keyscan -H 192.168.1.50 >> ~/.ssh/known_hosts`

#### Pitfall 2: Privilege Escalation (Sudo) Password Missing
* **Error Message:**
  `fatal: [web1]: FAILED! => {"msg": "Missing sudo password in connection, but was required."}`
* **Why it happens:** A task requires administrator access (e.g., `become: yes` to install package), but the SSH user is not configured for passwordless sudo, and you did not pass a password prompts tool.
* **Resolution:** Pass the become-password flag during execution or configure passwordless sudo on the host:
  ```bash
  # Execute with password prompt for privilege escalation:
  ansible-playbook -i inventory.ini deploy.yml --ask-become-pass
  ```

#### Pitfall 3: Indentation Errors (YAML Parsing Failure)
* **Error Message:**
  `ERROR! Syntax Error while loading YAML. ... The error appears to be in '/tmp/playbook.yml': line 6, column 5`
* **Why it happens:** YAML uses strict space-based indentation. Mixing tabs and spaces, or misaligning list markers (`-`) and their parent keys, breaks the parser.
* **Resolution:** Always use spaces (standard is 2 spaces per indentation level) and validate your files with a linting utility before executing:
  ```bash
  ansible-lint playbook.yml
  ```

### Traceability Check
All commands (`ansible`, `ansible-playbook`, `ansible-vault`), parameters (`hosts`, `tasks`, `vars_files`, `become`), modules (`apt`, `copy`, `service`, `user`, `authorized_key`, `cron`), and file configurations (`inventory.ini`, `vault_secrets.yml`) referenced in the Hands-On Labs are fully introduced, explained, and mapped step-by-step in this curriculum chapter. Let's begin the practical sessions.""",
        "commands": """### Command & Syntax Reference

#### Core CLI Commands
```bash
# Ping hosts to test connection
ansible all -m ping -i inventory.ini

# Ad-hoc command to run shell directives directly on the managed node
ansible webservers -a "free -h" -i inventory.ini -b
```
##### Command Parameter Anatomy:
* `all` or `webservers`: Target inventory group or host pattern.
* `-m ping`: Specifies the module to execute. The `ping` module verifies SSH and Python environments.
* `-i inventory.ini`: Defines path to your inventory host catalog.
* `-a "free -h"`: Arguments passed directly to the default `command` module.
* `-b`: Enables privilege escalation (`become`). Executes the command as `root` on the remote target.

---

#### Playbook Syntax Anatomy
Here is a comprehensive breakdown of a standard playbook configuration block:

```yaml
- name: Deploy Secure Web Environment             # 1. Play Name
  hosts: webservers                              # 2. Target Host Group
  become: yes                                    # 3. Enable Sudo Escalation
  vars:                                          # 4. Local Variables Block
    http_port: 80
  vars_files:                                    # 5. Encrypted Vault Variable Files
    - secure_secrets.yml
  
  tasks:                                         # 6. List of Tasks to Execute
    - name: Ensure Apache Web Server is Installed
      apt:                                       # 7. Package Management Module
        name: apache2
        state: present                           # 8. Desired State (present, absent, latest)
```

##### Line-by-Line Code Anatomy:
* **`hosts: webservers`**: Limits execution to targets under the `[webservers]` group defined in `inventory.ini`.
* **`become: yes`**: Instructs Ansible to execute all downstream tasks inside this play using `sudo` (privilege escalation).
* **`vars_files`**: Imports an external list of variables. This allows decoupling sensitive operational configurations from generic playbook logic.
* **`state: present`**: Rather than saying "install", Ansible checks if Apache is already on disk. If found, it skips installation (idempotency). Use `latest` only if you want automatic rolling updates, though it breaks reproducibility.
* **`state: started` and `enabled: yes`**: `started` guarantees the service runs right now. `enabled` updates the target systemd init configurations to boot the service automatically on machine reboot.""",
        "examples": """### Real-World Examples

#### Example 1: Basic Package Installation and Service Management
This playbook ensures the Apache package is installed, configured, enabled, and running.
```yaml
- name: Ensure Base Web Infrastructure is Active
  hosts: webservers
  become: yes
  tasks:
    - name: Install Apache Package
      apt:
        name: apache2
        state: present
        update_cache: yes
    - name: Ensure Apache is Running and Enabled on Boot
      service:
        name: apache2
        state: started
        enabled: yes
```

#### Example 2: Synchronizing Configuration Files with Handlers
Configure Nginx using a custom site file template, triggering a service reload only when the file changes.
```yaml
- name: Deploy Custom Proxy Configurations
  hosts: webservers
  become: yes
  tasks:
    - name: Push Nginx Main Configuration File
      copy:
        src: nginx.conf
        dest: /etc/nginx/nginx.conf
        owner: root
        group: root
        mode: '0644'
      notify: Reload Nginx Service
  handlers:
    - name: Reload Nginx Service
      service:
        name: nginx
        state: reloaded
```

#### Example 3: Creating and Managing System Users Safely
Define target user parameters, secure automated directories, and deploy SSH credentials.
```yaml
- name: Bootstrap System Engineers and Deployer Accounts
  hosts: all
  become: yes
  tasks:
    - name: Create System Deploy Group
      group:
        name: deployers
        state: present
    - name: Create Deployer Admin User Account
      user:
        name: deployer
        group: deployers
        shell: /bin/bash
        create_home: yes
    - name: Authorize Control Node Public SSH Key
      authorized_key:
        user: deployer
        state: present
        key: "{{ lookup('file', '~/.ssh/id_rsa.pub') }}"
```

#### Example 4: Setting Up an Automated Database Backup Cron Job
Schedule automated script runtime using Cron engine variables without custom scripting.
```yaml
- name: Deploy Secure Database Backup Automation
  hosts: dbservers
  become: yes
  tasks:
    - name: Synchronize Database Dump Script to Remote Directory
      copy:
        src: db_backup.sh
        dest: /usr/local/bin/db_backup.sh
        owner: root
        group: root
        mode: '0750'
    - name: Register Cron System Schedule Entry
      cron:
        name: "Perform Daily Cold Database Backups"
        minute: "0"
        hour: "3"
        job: "/usr/local/bin/db_backup.sh > /dev/null 2>&1"
        state: present
```

#### Example 5: Using Vault for Encrypted Sensitive Variables
Retrieve and consume highly encrypted secrets (like database administrator passwords) securely.
```yaml
- name: Provision Multi-Tier Web Databases
  hosts: dbservers
  become: yes
  vars_files:
    - vault_secrets.yml
  tasks:
    - name: Configure Secure MySQL Administrative User Credentials
      mysql_user:
        name: dbadmin
        password: "{{ vault_db_password }}"
        priv: '*.*:ALL,GRANT'
        host: localhost
        state: present
```""",
        "exercise": """### Hands-On Labs

#### Lab 1: Setup Local Static Inventory
* **Objective:** Design a custom local Ansible static inventory configuration map to run plays locally without SSH requirements.
* **Tasks:**
  1. Create a workspace directory and write an inventory file named `inventory.ini`.
  2. Populate it with a local group targeting your machine safely:
     ```ini
     [local]
     localhost ansible_connection=local
     ```
  3. Validate connectivity by running the ad-hoc command:
     `ansible local -m ping -i inventory.ini`

#### Lab 2: Write Package Tracking Playbook
* **Objective:** Create and execute a playbook targeting local package tracking.
* **Tasks:**
  1. Create a playbook file named `install_git.yml`.
  2. Write a play targeting host group `local` that ensures the `git` package is present.
     ```yaml
     - name: Local Package Audit
       hosts: local
       become: yes
       tasks:
         - name: Keep Git Binary Present on System
           apt:
             name: git
             state: present
     ```
  3. Execute the playbook locally using standard terminal commands:
     `ansible-playbook -i inventory.ini install_git.yml --ask-become-pass`

#### Lab 3: Deploy Automated File and Log Handlers
* **Objective:** Create a dynamic config deployment setup that reboots a custom logger only on updates.
* **Tasks:**
  1. Create a dummy test file in your control workspace named `app_config.conf`.
  2. Create a playbook named `deploy_config.yml`.
  3. Configure a task to copy `app_config.conf` to `/tmp/app_config.conf`, notifying a custom handler to display a message with the `debug` module when the target configuration changes.
  4. Run the playbook twice. Note how the handler executes only on the first run (idempotency in action).

#### Lab 4: Programmatic System User Generation
* **Objective:** Automatically configure groups and developers to learn deployment standards.
* **Tasks:**
  1. Write a playbook named `system_users.yml` targeting your local test group.
  2. Define tasks to create a user group named `operators`.
  3. Create a user named `ops_engineer` associated with the group, configuring their default shell to `/bin/bash`.
  4. Run the playbook and verify user generation by inspecting your local machine:
     `id ops_engineer`

#### Lab 5: Create and Decrypt Ansible Vault Secrets
* **Objective:** Encrypt passwords inside a git-safe variable storage file and consume them inside playbooks.
* **Tasks:**
  1. Create a secure vault file using the CLI helper:
     `ansible-vault create vault_secrets.yml`
  2. Provide a master vault passphrase and add this key-value pair inside the encrypted editor:
     `vault_db_password: "SuperSecretPassword123!"`
  3. Create a short test playbook called `deploy_db_credentials.yml` that reads `vault_secrets.yml` using `vars_files` and outputs the password using a debug task (ensure you decrypt safely).
  4. Run the playbook passing the decryption query:
     `ansible-playbook -i inventory.ini deploy_db_credentials.yml --ask-vault-pass`""",
        "insight": """### Interview Q&A

#### Q1: Explain Ansible's agentless architecture and its primary benefits.
* **Answer:** Ansible does not require any background agent services or daemon software to be pre-installed on the managed target nodes. Instead, it relies on standard communication channels like SSH (for Unix/Linux) or WinRM (for Windows). This eliminates administrative overhead, cuts memory footprints, simplifies patching of agent software, and reduces the potential security attack surface across enterprise infrastructure.

#### Q2: What is idempotency and how does it protect remote infrastructure?
* **Answer:** Idempotency is an engineering principle where performing an automated operation multiple times yields the exact same target state without side effects. In practice, Ansible modules check the current actual state of the target system before applying any changes. If the target system is already configured with the desired state (e.g., Apache package is installed), Ansible reports `ok` and skips modification. This prevents unwanted configuration drifts, unexpected restarts, or state duplication during routine play runs.

#### Q3: How do Ansible Handlers differ from normal Tasks, and when do they execute?
* **Answer:** Normal tasks execute sequentially in the exact order they are defined inside a play. Handlers are special tasks that are only triggered ("notified") if a parent task records a state change (i.e., returns `changed: true`). Furthermore, handlers are queued and executed once at the very end of the entire play, regardless of how many individual tasks notified them. This avoids redundant system restarts (e.g., reloading Nginx only once even if multiple configurations were updated during the run).

#### Q4: What is the purpose of Ansible Vault and how do you use it in execution?
* **Answer:** Ansible Vault provides symmetric encryption to secure sensitive data such as API keys, database credentials, private keys, or system passwords directly inside YAML variables or configuration files. This allows teams to safely store configurations in source control (like Git) without exposure. During execution, playbooks decryption keys are provided to Ansible using the `--ask-vault-pass` command-line flag or referencing a secure file path in `ansible.cfg`.

#### Q5: How does the `serial` keyword work in multi-node playbook execution?
* **Answer:** The `serial` directive controls the batch sizing of playbook execution across your hosts inventory. Instead of running tasks concurrently on all 100 targets in your inventory, defining `serial: 5` instructs Ansible to execute the entire playbook on a batch of 5 servers at a time. It only moves to the next batch of 5 hosts if the current batch completes successfully. This is ideal for zero-downtime rolling upgrades and database migrations in high-availability environments."""
    }
]