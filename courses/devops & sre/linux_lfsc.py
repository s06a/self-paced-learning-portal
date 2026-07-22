COURSE_ID = "lfcs_sysadmin_complete"
COURSE_TITLE = "Linux Foundation Certified System Administrator (LFCS) Masterclass"
COURSE_DESCRIPTION = "A deeply comprehensive, production-grade self-paced learning track covering all 5 core domains of the Linux Foundation Certified System Administrator (LFCS) exam. Spanning 17 sequential modules, it provides exhaustive conceptual foundations, commands, concrete configurations, local lab exercises, and certification focus guides."

CURRICULUM_DATA = [
    {
        "id": 1,
        "title": "Module 1: Console Interfaces, SSH Connectivity, and Terminal Multiplexing",
        "theory": r"""### Virtual Consoles & TTY Management
Linux interfaces expose local access points via virtual consoles (Teletypewriters or TTYs). Systems running standard initialization managers map multiple login sessions. These are accessed locally via combinations like `Ctrl+Alt+F1` through `Ctrl+Alt+F6` for text-based TTY interfaces, and `Ctrl+Alt+F7` (or higher) for graphical desktop environments. These systems are governed by the `getty` process, which manages local physical and virtual terminals.

### SSH Connectivity & Handshakes
Remote terminal administration is handled by Secure Shell (SSH). Operating over TCP port 22, SSH uses asymmetric cryptography to establish encrypted channels between hosts. During connection initialization, host keys are compared against local tracking manifests (`~/.ssh/known_hosts`). Authentications utilize public-private key pairs (e.g., RSA, ECDSA, or Ed25519) to eliminate password transmission risks across transit pipes.

### Terminal Multiplexing with Tmux
Terminal multiplexers like `tmux` decouple shell sessions from parent SSH or local console threads. Running a multiplexer creates an intermediate background daemon that manages virtual terminal states. If the physical connection drops, the multiplexer preserves the execution state of active processes. This allows administrators to resume tasks seamlessly upon reconnecting.""",
        "commands": r"""### Command & Syntax Reference
* **Console Diagnostics**
  * `tty`: Show the filename of the terminal connected to standard input.
  * `chvt 3`: Switch the active local console screen to Virtual Terminal 3.

* **SSH Tunneling and Authentication**
  * `ssh-keygen -t ed25519 -C "admin@local"`: Generate an Ed25519 SSH keypair with a comment.
  * `ssh-copy-id -i ~/.ssh/id_ed25519.pub user@10.0.0.10`: Copy the public key to a remote host.
  * `ssh -p 2222 -i ~/.ssh/id_ed25519 user@10.0.0.10`: Connect to a remote host via a custom port.
  * `ssh -L 8080:localhost:80 user@10.0.0.10`: Forward local port 8080 to remote port 80.

* **Tmux Session Control**
  * `tmux new -s admin_session`: Create a new named tmux session.
  * `tmux ls`: List all active running tmux sessions.
  * `tmux attach-session -t admin_session`: Resume a detached tmux session.
  * `Ctrl+b d`: Detach from the current tmux session.
  * `Ctrl+b c`: Create a new window in tmux.
  * `Ctrl+b ,`: Rename the current tmux window.""",
        "examples": r"""### Real-World Examples

#### Example 1: Creating persistent sessions for updates
**Situation:** You need to run a system-wide upgrade on a remote server, but your local network connection is unstable and prone to dropping.
**Action:** Create a named tmux session before starting the update to prevent network drops from terminating the process.
```bash
tmux new -s upgrade_session
sudo apt-get update && sudo apt-get dist-upgrade -y
```

#### Example 2: Forwarding port 8080 to access a remote web application
**Situation:** A development server at IP `192.168.12.10` has a private admin dashboard listening locally on port `8080`. This port is blocked by the network firewall.
**Action:** Establish an SSH tunnel to forward your local port `9000` to the remote port `8080`.
```bash
ssh -L 9000:127.0.0.1:8080 developer@192.168.12.10 -Nf
```

#### Example 3: Copying SSH keys to multiple hosts non-interactively
**Situation:** You need to configure passwordless SSH access to a new node at `10.0.10.15` using a pre-generated public key.
**Action:** Deploy the public key using `ssh-copy-id` and verify passwordless login.
```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub adminuser@10.0.10.15
ssh -i ~/.ssh/id_ed25519 adminuser@10.0.10.15 "hostname"
```

#### Example 4: Diagnosing active terminal ownership
**Situation:** A security audit requires you to identify who is logged into active virtual TTY or pseudo-terminal (PTS) lines.
**Action:** Query the system using the `who` and `w` utilities.
```bash
who -a
w -h
```

#### Example 5: Splitting panes in Tmux for real-time log monitoring
**Situation:** You need to monitor a log file in real time while executing diagnostic commands in the same terminal window.
**Action:** Split your active tmux window into horizontal panes.
```bash
# Press Ctrl+b then % to split vertically, or Ctrl+b then " to split horizontally
tail -f /var/log/syslog
# Use Ctrl+b then Arrow Keys to navigate between panes
```""",
        "exercise": r"""### Hands-On Labs

#### Lab 1: Swapping Virtual Consoles Locally
* **Objective:** Learn to manually navigate local text consoles.
* **Tasks:**
  1. Access a physical or hypervisor-based Linux terminal.
  2. Press `Ctrl+Alt+F2` to drop into TTY2. Log in using your root or user credentials.
  3. Run `tty` to verify you are executing processes in `/dev/tty2`.
  4. Run `chvt 4` to switch to TTY4 and verify the transition.
  5. Press `Ctrl+Alt+F1` (or the graphical terminal shortcut) to return to your primary window.

#### Lab 2: Multi-Hop SSH Config Configurations
* **Objective:** Simplify SSH connections using a config file.
* **Tasks:**
  1. Create the `~/.ssh/config` file if it does not exist.
  2. Add a configuration block for a host named `db-primary` using the following settings:
     ```text
     Host db-primary
         HostName 10.0.5.20
         User dbadmin
         Port 22
         IdentityFile ~/.ssh/id_ed25519
     ```
  3. Adjust the file permissions of your SSH configuration directory: `chmod 700 ~/.ssh && chmod 600 ~/.ssh/config`.
  4. Connect to the host by running `ssh db-primary` instead of using the full IP address and credentials.

#### Lab 3: Persisting Commands across Network Drops
* **Objective:** Run a task in a persistent tmux session and disconnect safely.
* **Tasks:**
  1. Initialize a tmux session named `backup_proc`.
  2. Start a continuous ping to track latency: `ping 8.8.8.8 > /tmp/ping_history.txt`.
  3. Detach from the session by pressing `Ctrl+b` then `d`.
  4. Run `tmux ls` to confirm that the `backup_proc` session is still active in the background.
  5. Re-attach to the session using `tmux attach-session -t backup_proc` and stop the ping process using `Ctrl+c`.

#### Lab 4: Securing Active SSH User Logins
* **Objective:** Identify and disconnect unauthorized remote SSH connections.
* **Tasks:**
  1. Run `who -u` to view all active remote shell sessions.
  2. Identify the process ID (PID) of an active pseudo-terminal connection (`pts/X`).
  3. Send a SIGTERM signal to disconnect the selected PTS session: `kill -15 <PID>`.
  4. Verify that the terminal connection was terminated by running `who -u` again.

#### Lab 5: SSH Key Management & Host Validation
* **Objective:** Clear stale target records from your local host key database.
* **Tasks:**
  1. Simulate a host key change by removing an entry for IP `10.0.0.50` from your `known_hosts` file.
  2. Run the removal command: `ssh-keygen -R 10.0.0.50`.
  3. Reconnect to `10.0.0.50` and verify that you are prompted to accept the host key fingerprint.
  4. Append your public key to the remote host's `~/.ssh/authorized_keys` file to restore access.
  5. Confirm passwordless login is working.""",
        "insight": r"""### Interview Q&A

#### Q1: What happens if an SSH connection drops while a command is running in a tmux session?
* **Answer:** When an SSH connection drops, the child pseudo-terminal interface (PTS) is closed. However, because the `tmux` server runs as a separate background daemon, it intercepts the signal and prevents its child processes from terminating. The commands running inside the tmux window continue executing uninterrupted. You can log back into the server via SSH and run `tmux attach` to resume control of the session.

#### Q2: What is the purpose of the ~/.ssh/known_hosts file on a client system?
* **Answer:** The `known_hosts` file stores the public keys of remote servers you have connected to. When you establish an SSH connection, the client compares the remote server's key against the stored key. If they match, the connection is established. If they differ, the client warns you of a potential Man-in-the-Middle (MITM) attack or a host key change, protecting you from connecting to an unauthorized system.

#### Q3: How do you identify the active terminal device for your current shell session?
* **Answer:** Run the `tty` command. It queries standard input and returns the file path of the active terminal device (such as `/dev/tty1` for local virtual consoles, or `/dev/pts/0` for remote pseudo-terminals opened via SSH or graphical terminal emulators).

#### Q4: Why is it important to secure SSH private keys with chmod 600 permissions?
* **Answer:** SSH clients enforce strict security policies. If an SSH private key is readable by other users, the SSH client will refuse to use it and return an error (e.g., "Permissions 0644 for id_rsa are too open"). Setting permissions to `600` ensures that only the file owner can read or write to the private key, protecting it from unauthorized access on multi-user systems.

#### Q5: How do you run an SSH connection that executes a command on a remote host and exits immediately without allocating a terminal?
* **Answer:** Specify the command as an argument at the end of the `ssh` command. You can add the `-T` flag to disable pseudo-terminal allocation:
```bash
ssh -T user@10.0.0.10 "cat /proc/uptime"
```

### LFCS Exam Focus
*   **Use Tmux during the exam:** The LFCS exam is timed and conducted via an online terminal. Run commands inside a `tmux` session. If your browser freezes or the connection drops, your active tasks and command history will be preserved when you reconnect."""
    },
    {
        "id": 2,
        "title": "Module 2: Filesystem Hierarchy, Base Operations, and Link Dynamics",
        "theory": r"""### The Filesystem Hierarchy Standard (FHS)
Linux systems follow the Filesystem Hierarchy Standard (FHS) to organize files and directories. Essential system paths include `/bin` and `/sbin` for system binaries, `/etc` for configuration files, `/var` for dynamic data (such as logs and spools), `/usr` for user programs, and `/proc` and `/sys` for virtual filesystems that interface with the kernel.

### File Metadata & Inodes
Filesystems store files as data blocks linked to an index node (inode). An inode is a data structure containing metadata about a file, including its size, owner, permissions, and timestamps. It does not store the file's name or its actual data content. The file name is stored within directory structures, mapping names to their corresponding inode numbers.

### Link Dynamics: Hard Links vs. Soft Links
*   **Hard Links:** Create a new directory entry pointing to an existing inode. Hard links share the same inode number and data blocks as the source file. They cannot span across different physical filesystems or partitions, and they cannot point to directories.
*   **Symbolic (Soft) Links:** Create a new file containing a text path pointing to the target file. Soft links have unique inode numbers and can span across filesystems, partitions, and point to directories. If the original target file is deleted, the soft link becomes broken (dangling).""",
        "commands": r"""### Command & Syntax Reference
* **Standard File Operations**
  * `mkdir -p /data/app/config`: Create nested directories recursively.
  * `cp -rp /source /target`: Copy files recursively while preserving permissions and timestamps.
  * `mv -f /source /target`: Force-move or rename files without prompting for confirmation.
  * `rm -rf /data/temp`: Recursively delete directories and their contents.

* **Inode and Link Control**
  * `ls -li /data`: List files, showing their inode numbers in the first column.
  * `ln /data/file1 /data/hard_link`: Create a hard link.
  * `ln -s /data/file1 /data/soft_link`: Create a symbolic (soft) link.
  * `stat /data/file1`: Display detailed file metadata and inode properties.
  * `find / -inum 204982 2>/dev/null`: Find files associated with a specific inode number.""",
        "examples": r"""### Real-World Examples

#### Example 1: Creating persistent links to shared configurations
**Situation:** You need to share a configuration file `/etc/app_engine.conf` with a service configured to look for settings in `/opt/app/engine.conf`.
**Action:** Create a symbolic link to point the service's target path to the system configuration file.
```bash
mkdir -p /opt/app
ln -s /etc/app_engine.conf /opt/app/engine.conf
```

#### Example 2: Copying a website directory while preserving permissions
**Situation:** You need to copy a production website directory `/var/www/html` to `/var/www/html_backup` while preserving its file permissions, owners, and timestamps.
**Action:** Run `cp` with the `-p` (preserve) and `-r` (recursive) flags.
```bash
cp -pr /var/www/html /var/www/html_backup
```

#### Example 3: Finding and deleting broken symbolic links
**Situation:** A application update left behind broken symbolic links in `/etc/nginx/sites-enabled/` that are causing service issues.
**Action:** Use `find` with the `-xtype l` flag to identify and delete broken links.
```bash
find /etc/nginx/sites-enabled/ -xtype l -delete
```

#### Example 4: Identifying files that share the same inode
**Situation:** You need to find all file names pointing to the same physical data blocks (hard links) as `/etc/hosts` on the same partition.
**Action:** Identify the inode of `/etc/hosts` and search for all matching hard links.
```bash
INODE_ID=$(stat -c '%i' /etc/hosts)
find /etc -inum "$INODE_ID" 2>/dev/null
```

#### Example 5: Resolving storage space issues caused by orphan hard links
**Situation:** A file was deleted, but disk space was not freed because a hard link to the file is still active on the partition.
**Action:** Find the hard link, verify its contents, and delete it to free up the disk space.
```bash
# Find files with a link count greater than 1
find /data -type f -links +1 -exec ls -l {} \;
```""",
        "exercise": r"""### Hands-On Labs

#### Lab 1: Swapping Link Inodes
* **Objective:** Understand how hard and soft links interact with inodes.
* **Tasks:**
  1. Create a directory `/tmp/link_lab/` and create a file inside it named `source.txt` containing "Primary Data".
  2. Create a hard link named `hl.txt` and a soft link named `sl.txt` pointing to `source.txt`.
  3. Run `ls -i` and compare the inode numbers of all three files. Note which files share the same inode.
  4. Append text to `hl.txt` and verify that the changes are reflected in `source.txt` and `sl.txt`.
  5. Delete `source.txt`. Verify which of the remaining links (`hl.txt` or `sl.txt`) can still read the file contents.

#### Lab 2: Deep Directory Replication
* **Objective:** Copy directory structures while preserving metadata and ownership.
* **Tasks:**
  1. Create a directory structure `/tmp/src_dir/sub1/sub2` containing multiple test files.
  2. Modify the file permissions of `/tmp/src_dir/sub1/sub2` to `0755`.
  3. Copy `/tmp/src_dir` to `/tmp/dest_dir` while preserving all file attributes.
  4. Verify that the file permissions, ownerships, and timestamps match between the source and destination directories.

#### Lab 3: Tracking Inode Limits
* **Objective:** Identify filesystems that are running out of available inodes.
* **Tasks:**
  1. Use the `df` command to display inode usage on active filesystems.
  2. Identify the filesystem with the highest inode utilization.
  3. Create a script to generate 100 empty files in a test directory to observe changes in inode usage.
  4. Clean up the test directory by deleting the generated files.

#### Lab 4: Tracking Modified Configurations
* **Objective:** Locate configuration files modified within a specific timeframe.
* **Tasks:**
  1. Create a temporary configuration file `/etc/test_config.conf` and update its content.
  2. Run a `find` command to locate all files under `/etc` modified in the last 10 minutes.
  3. Verify that your new configuration file is listed in the search results.
  4. Clean up and delete `/etc/test_config.conf`.

#### Lab 5: Resolving Symbolic Link Paths
* **Objective:** Create and manage relative vs. absolute symbolic links.
* **Tasks:**
  1. Create a directory `/tmp/abs_link/` and a file inside it named `target.txt`.
  2. Create an absolute symbolic link named `abs_link.lnk` pointing to the file.
  3. Create a relative symbolic link named `rel_link.lnk` pointing to the file.
  4. Move both links to a different directory `/tmp/new_home/`.
  5. Verify which link remains active and which link breaks after being moved.""",
        "insight": r"""### Interview Q&A

#### Q1: Why can hard links not span across different filesystems or partition volumes?
* **Answer:** Inodes are unique identifier indexes that are managed individually by each filesystem partition. Different filesystems can use the same inode numbers to point to completely different files. Because a hard link points directly to an inode number, allowing hard links to span across filesystems would create conflicts and point to incorrect data. Symbolic links do not have this limitation because they store the text path of the target file rather than its inode number.

#### Q2: If a file has 0 write permissions but the parent directory has full write permissions, can a user delete the file?
* **Answer:** Yes. In Linux, deleting a file does not write to or modify the file itself. Deleting a file removes its entry from the parent directory's block list, which is a write operation on the parent directory. If a user has write and execute permissions on the parent directory, they can delete any file within it, regardless of the file's individual permissions.

#### Q3: How do you identify the inode number of a file, and how does this help identify hard links?
* **Answer:** Use the `ls -i` or `stat` commands. If two files share the same inode number on the same filesystem partition, they point to the exact same physical data blocks on the disk, identifying them as hard links.

#### Q4: What happens to the file data on disk when you delete a file that has multiple hard links?
* **Answer:** When you delete a file, its directory entry is removed and the inode's link counter is decremented by 1. The actual file data remains on the disk as long as the inode's link counter is greater than 0. The disk space is only marked as free and available for overwrite when the link counter reaches 0 and no active system processes are using the file.

#### Q5: If a symbolic link points to a directory, what is the correct syntax to delete the link without deleting the directory's contents?
* **Answer:** Use the `rm` command, specifying the link path without a trailing slash. Adding a trailing slash (e.g., `rm -rf /my_link/`) resolves the link and attempts to delete the contents of the target directory instead.
```bash
rm /path/to/symlink
```

### LFCS Exam Focus
*   **Symbolic Link Targets:** When creating symbolic links, always use absolute paths for the target file (e.g., `ln -s /etc/app/config.txt /tmp/config.lnk`) to prevent the link from breaking if it is moved or accessed from a different working directory."""
    },
    {
        "id": 3,
        "title": "Module 3: Compression, Tar Archiving, and Incremental Backups",
        "theory": r"""### Archiving vs. Compression
*   **Archiving:** Combines multiple files and directories into a single file (such as a `.tar` tape archive file) while preserving file structures, permissions, and directory hierarchies. Archiving does not reduce file size on its own.
*   **Compression:** Uses mathematical algorithms to compress files and reduce their size on disk. Compression tools (such as gzip, bzip2, or xz) operate on individual files.

### Standard Compression Algorithms
Linux systems use several standard compression tools, balancing speed against compression ratios:
*   **gzip (`.gz`):** Fast compression speed with low CPU resource usage and moderate compression ratios.
*   **bzip2 (`.bz2`):** Slower than gzip, but offers higher compression ratios.
*   **xz (`.xz`):** High CPU usage and slower compression speeds, but offers the highest compression ratios. It is ideal for archiving distribution packages and long-term system backups.""",
        "commands": r"""### Command & Syntax Reference
* **Tar Archiving and Compression Operations**
  * `tar -cvf backup.tar /opt/data`: Create an uncompressed archive of a directory.
  * `tar -xvf backup.tar -C /tmp`: Extract an archive to a target directory.
  * `tar -czvf backup.tar.gz /opt/data`: Create an archive compressed with gzip.
  * `tar -cjvf backup.tar.bz2 /opt/data`: Create an archive compressed with bzip2.
  * `tar -cJvf backup.tar.xz /opt/data`: Create an archive compressed with xz.
  * `tar -tf backup.tar.gz`: List the contents of an archive without extracting it.
  * `tar -xzvf backup.tar.gz /opt/data/file1`: Extract a specific file from an archive.

* **Standalone Compression Tools**
  * `gzip file.txt`: Compress a file (replaces the original file with `file.txt.gz`).
  * `gunzip file.txt.gz`: Decompress a gzip file.
  * `xz -d file.txt.xz`: Decompress an xz file.""",
        "examples": r"""### Real-World Examples

#### Example 1: Creating compressed system backups
**Situation:** You need to create a compressed backup of `/etc` and `/var/log` before performing a major system upgrade.
**Action:** Use `tar` with the `-J` (xz) flag to create a highly compressed archive.
```bash
tar -cJvf /backup/system_prep_backup.tar.xz /etc /var/log
```

#### Example 2: Verifying archive contents before restoration
**Situation:** You need to verify the contents of an archive `/tmp/web_backup.tar.gz` before extracting it to avoid overwriting production files.
**Action:** List the contents of the archive using the `-t` flag.
```bash
tar -tzf /tmp/web_backup.tar.gz
```

#### Example 3: Extracting a single file from an archive
**Situation:** An application configuration file `/etc/nginx/nginx.conf` was accidentally modified. You need to restore only this file from a backup archive `/backup/etc_backup.tar.gz`.
**Action:** Extract the specific file from the archive.
```bash
tar -xzvf /backup/etc_backup.tar.gz etc/nginx/nginx.conf -C /
```

#### Example 4: Compressing log archives to free up disk space
**Situation:** Old log files in `/var/log/audit/` are consuming too much disk space. You need to compress them individually.
**Action:** Use `gzip` to compress all `.log` files in the directory.
```bash
gzip /var/log/audit/*.log
```

#### Example 5: Appending files to an existing archive
**Situation:** You have an uncompressed backup archive `/backup/data.tar` and need to add a new file `/opt/notes.txt` to it without extracting the archive.
**Action:** Use the `-r` (append) flag to add the file to the archive.
```bash
tar -rvf /backup/data.tar /opt/notes.txt
```""",
        "exercise": r"""### Hands-On Labs

#### Lab 1: Multi-Format Compression Comparisons
* **Objective:** Compare the performance and compression ratios of gzip, bzip2, and xz.
* **Tasks:**
  1. Create a large text file by copying log contents: `cat /var/log/messages* /var/log/syslog* > /tmp/large_file.txt 2>/dev/null || dd if=/dev/urandom of=/tmp/large_file.txt bs=1M count=10`.
  2. Create three compressed archives of the file using gzip, bzip2, and xz.
  3. Compare the file sizes of the compressed archives. Note which compression format produced the smallest file.
  4. Compare the time taken to compress the files using each utility.
  5. Clean up the directory by deleting the test files.

#### Lab 2: Restoring Backups to Alternative Locations
* **Objective:** Extract archives to custom locations to avoid overwriting files.
* **Tasks:**
  1. Create a test directory `/tmp/restore_test/` and a backup archive of your active user's home directory configurations.
  2. Extract the backup archive to `/tmp/restore_test/` using the `-C` flag.
  3. Verify that the files were extracted to the correct target directory and have not overwritten your active home directory configurations.

#### Lab 3: Appending and Updating Tar Archives
* **Objective:** Modify and update existing archives.
* **Tasks:**
  1. Create an uncompressed archive named `/tmp/media.tar` containing `/etc/hosts`.
  2. Add `/etc/resolv.conf` to the archive using the `-r` flag.
  3. List the contents of `/tmp/media.tar` using the `-t` flag to verify that both files are present.
  4. Attempt to add a file to a compressed archive (such as `.tar.gz`) and observe the output. Note why appending to compressed archives is not supported.

#### Lab 4: Preserving Permissions during Extractions
* **Objective:** Extract files while preserving original security attributes.
* **Tasks:**
  1. Create a test file `/tmp/secure.txt` and set its file permissions to `0400` (read-only by owner).
  2. Create an archive of the file using `tar` with the `-p` (preserve permissions) flag.
  3. Delete the original `/tmp/secure.txt` file.
  4. Extract the backup archive.
  5. Verify that the restored file's permissions match the original permissions (`0400`).

#### Lab 5: Dynamic Tar Streaming and Extraction
* **Objective:** Copy directories across networks using streaming pipelines.
* **Tasks:**
  1. Create a test directory `/tmp/stream_src` containing several files.
  2. Stream a tar archive of the directory over stdout and extract it directly into `/tmp/stream_dst` using a single piped command.
  3. Run the command: `tar -cf - -C /tmp/stream_src . | tar -xf - -C /tmp/stream_dst`.
  4. Verify that the files in the source and destination directories are identical.""",
        "insight": r"""### Interview Q&A

#### Q1: Why does appending files (-r) to a compressed tar archive (such as .tar.gz) fail?
* **Answer:** Compression algorithms (like gzip or bzip2) process data as a continuous block stream. Appending files directly to a compressed archive would corrupt the stream layout. To add files to a compressed archive, you must decompress the archive first, append the new files, and re-compress the archive.

#### Q2: What is the purpose of the -p flag in tar operations?
* **Answer:** The `-p` (preserve permissions) flag retains the original file permissions, owners, groups, access control lists (ACLs), and timestamps of archived files during extraction. Without this flag, extracted files may inherit default system permissions based on the active user's `umask` settings.

#### Q3: How do you list the contents of a compressed archive without decompressing it on disk?
* **Answer:** Use the `-t` (list) flag with the corresponding compression filter flag (e.g., `-z` for gzip, `-j` for bzip2, `-J` for xz).
```bash
tar -tzf archive.tar.gz
```

#### Q4: What is the difference between dd and tar for backup configurations?
* **Answer:**
  * **tar:** A file-level archiving utility that packages files and directories into an archive file. It can cross physical partitions and ignore free space.
  * **dd:** A sector-level block copy utility that copies raw disk sectors directly. It clones entire drives, partition layouts, filesystems, and boot sectors, regardless of file content or free space.

#### Q5: How do you compress a directory using gzip without using tar?
* **Answer:** Standalone compression tools like `gzip` can only compress individual files, not directories. To compress a directory using gzip, you must package the directory into a single archive file using `tar` first, then compress the archive (creating a `.tar.gz` or `.tgz` file).

### LFCS Exam Focus
*   **Use the correct compression flags:** Pay close attention to the compression format requested in the exam questions (e.g., `.tar.gz` uses `-z`, `.tar.bz2` uses `-j`, `.tar.xz` uses `-J`). Using the incorrect compression algorithm will result in zero points for the task."""
    },
    {
        "id": 4,
        "title": "Module 4: File Finding, Basic Stream Filtering, and Regex Processing",
        "theory": r"""### Filesystem Searching with Find
The `find` utility is a powerful tool for searching filesystems based on file metadata. Unlike database-driven index tools like `locate`, `find` performs real-time searches directly on filesystem trees. It filters files based on parameters such as file name patterns, file size thresholds, modified times, ownership, and file permissions.

### Pipelines & Standard I/O Streams
Linux shell operations utilize three standard input/output streams:
*   **Standard Input (stdin / fd 0):** Input data stream read by commands.
*   **Standard Output (stdout / fd 1):** Normal output stream generated by commands.
*   **Standard Error (stderr / fd 2):** Error messages stream generated by commands.
Redirection operators (`>`, `>>`, `2>`, `&>`) redirect these streams to files, while piping (`|`) connects the stdout of one command to the stdin of another.

### Regular Expressions (Regex)
Regular expressions are patterns used to search and match text strings. Linux utilities support two standard regex syntax formats:
*   **Basic Regular Expressions (BRE):** Supported by default in `grep`. Characters like `?`, `+`, `{`, `|`, `(`, and `)` are treated as literal characters unless escaped with a backslash.
*   **Extended Regular Expressions (ERE):** Supported by `grep -E` (or `egrep`). Meta-characters are interpreted as operators by default, simplifying regex syntax.""",
        "commands": r"""### Command & Syntax Reference
* **File Searching (find)**
  * `find /etc -type f -name "*.conf"`: Find configuration files under `/etc`.
  * `find /var -type f -size +50M`: Find files larger than 50MB.
  * `find /home -type f -mtime -3`: Find files modified in the last 3 days.
  * `find /data -type f -user developer`: Find files owned by a specific user.
  * `find /var/log -type f -perm 0640`: Find files with specific permissions.
  * `find /tmp -type f -mmin -60 -delete`: Find and delete files modified within the last 60 minutes.

* **Regular Expression Search (grep)**
  * `grep "error" /var/log/syslog`: Search for lines containing "error".
  * `grep -i "failed" auth.log`: Perform a case-insensitive search.
  * `grep -v "info" application.log`: Exclude lines containing the search pattern.
  * `grep -r "10.0.0.1" /etc/`: Search recursively for a string in a directory.
  * `grep -E "^[0-9]{1,3}\." file.txt`: Search using Extended Regular Expressions (ERE).

* **I/O Redirection**
  * `command > output.log`: Overwrite file with stdout.
  * `command >> output.log`: Append stdout to a file.
  * `command 2> error.log`: Redirect stderr to a file.
  * `command &> combined.log`: Redirect both stdout and stderr to the same file.
  * `command < input.txt`: Read stdin from a file.""",
        "examples": r"""### Real-World Examples

#### Example 1: Finding and deleting old logs
**Situation:** A filesystem is running out of space. You need to find and delete all `.log` files in `/var/log` that are larger than 100MB and older than 14 days.
**Action:** Use `find` with the `-size`, `-mtime`, and `-exec` flags.
```bash
find /var/log -type f -name "*.log" -size +100M -mtime +14 -exec rm -f {} \;
```

#### Example 2: Filtering system logs for authentication failures
**Situation:** You need to audit authentication failures on an active server by identifying failed login attempts in the authentication log.
**Action:** Use `grep` with regex patterns to isolate failed login attempts.
```bash
grep -Ei "fail|invalid|unauthorized" /var/log/auth.log > /tmp/failed_logins.txt
```

#### Example 3: Finding files with loose permissions
**Situation:** You need to audit system security by finding all world-writable files (permissions ending in 7 or 2) under `/opt`.
**Action:** Use `find` with permission filter flags.
```bash
find /opt -type f -perm -o+w -exec ls -l {} \;
```

#### Example 4: Creating daily activity logs
**Situation:** You need to extract error messages from multiple logs and consolidate them into a daily audit file, ignoring informational messages.
**Action:** Filter multiple files using recursive search pipelines and redirect the output.
```bash
grep -rni "error" /var/log/nginx/ 2>/dev/null | grep -v "info" > /backup/nginx_errors.log
```

#### Example 5: Finding empty directories
**Situation:** A cleanup script needs to identify and remove empty directories under a shared network share `/mnt/shares/`.
**Action:** Use `find` with the `-empty` flag.
```bash
find /mnt/shares/ -type d -empty -delete
```""",
        "exercise": r"""### Hands-On Labs

#### Lab 1: Multi-Criteria Search Operations
* **Objective:** Find specific files using multiple search parameters.
* **Tasks:**
  1. Create several dummy files under `/tmp/search_lab/` with varying owners, sizes, and permissions.
  2. Find all files under the directory that are larger than 1MB AND owned by the current user.
  3. Find all files modified in the last 24 hours with permissions set to `0644`.
  4. Write the file paths of all matching files to `/tmp/matches.txt`.

#### Lab 2: Standard Error Redirection Pipelines
* **Objective:** Capture and separate error streams in pipelines.
* **Tasks:**
  1. Run a command that generates both stdout and stderr (e.g., `find /etc /root -name "*.conf"` run as a non-root user).
  2. Redirect the stdout stream to `/tmp/configs.txt` and the stderr stream to `/tmp/denied_errors.err`.
  3. Verify the contents of both files to confirm that the streams were separated correctly.
  4. Repeat the command, redirecting both streams to a single file `/tmp/combined_run.log`.

#### Lab 3: Regex Pattern Matching on System Configurations
* **Objective:** Extract IP configurations using regular expressions.
* **Tasks:**
  1. View `/etc/resolv.conf` to check active name servers.
  2. Use `grep -E` and a regular expression pattern to extract only valid IPv4 addresses from `/etc/resolv.conf`.
  3. Write a regex pattern to find active, uncommented lines in `/etc/ssh/sshd_config`.

#### Lab 4: Executing Commands on Search Results
* **Objective:** Modify files returned by search queries.
* **Tasks:**
  1. Create a directory `/tmp/chmod_lab/` containing five files.
  2. Find all files in the directory and set their permissions to `0600` using the `-exec` flag.
  3. Verify the updated file permissions using `ls -l`.
  4. Repeat the task, using the `xargs` utility instead of the `-exec` flag.

#### Lab 5: Finding and Archiving Modified Files
* **Objective:** Archive files modified within a specific timeframe.
* **Tasks:**
  1. Find all configuration files in `/etc` ending in `.conf` modified in the last 7 days.
  2. Package the matching files into a compressed tar archive `/tmp/recent_configs.tar.gz`.
  3. Verify that the files were archived successfully without extracting the archive.""",
        "insight": r"""### Interview Q&A

#### Q1: What is the difference between the grep pattern and the find pattern?
* **Answer:**
  * **find:** Searches for files and directories based on metadata (such as file names, sizes, owners, permissions, and creation dates) in the filesystem directory structure.
  * **grep:** Searches for text patterns *inside* files by scanning their contents.

#### Q2: What does 2>&1 mean in shell commands?
* **Answer:** It redirects standard error (file descriptor 2) to standard output (file descriptor 1). This combines both stdout and stderr into a single output stream, allowing you to pipe both streams to another command or redirect them to the same log file:
```bash
command > file.log 2>&1
# Modern equivalent:
command &> file.log
```

#### Q3: Why is using xargs often faster than using the -exec flag in find?
* **Answer:**
  * **`-exec`:** Executes the specified command once for every single file returned by the search query. If 1,000 files are found, it starts 1,000 separate processes, which consumes system resources.
  * **`xargs`:** Groups the file paths into a single line and runs the command only once (or in batches), reducing process creation overhead and improving system performance.

#### Q4: How do you perform a case-insensitive search and display the matching line numbers?
* **Answer:** Use `grep` with the `-i` (case-insensitive) and `-n` (show line numbers) flags:
```bash
grep -in "failed" /var/log/auth.log
```

#### Q5: What is the difference between grep and egrep?
* **Answer:**
  * **`grep`:** Uses Basic Regular Expressions (BRE) by default. Meta-characters like `+`, `?`, `|`, and `{}` are treated as literal characters unless escaped with a backslash.
  * **`egrep` (equivalent to `grep -E`):** Uses Extended Regular Expressions (ERE). Meta-characters are interpreted as operators by default, simplifying regex syntax.

### LFCS Exam Focus
*   **Search performance under pressure:** Memorize the syntax of the `-exec` flag in the `find` command. A common exam task requires finding specific files and copying or deleting them in a single step (e.g., `find ... -exec cp {} /target/ \;`). Make sure to escape the trailing semicolon (`\;`)."""
    },
    {
        "id": 5,
        "title": "Module 5: Inline Stream Processing with Sed and Awk Analysis",
        "theory": r"""### Stream Processing
Stream processing tools manipulate text data as it passes through pipelines. Unlike standard text editors (such as vim or nano) which load entire files into memory, stream editors process text line-by-line. This allows you to process large log files and streams efficiently.

### Stream Editing with Sed
`sed` (Stream Editor) is a non-interactive text editor that performs basic text transformations on input streams. It uses commands to find, replace, insert, append, or delete lines of text. `sed` can write modifications back to the source file inline, making it ideal for automating configuration updates.

### Structured Data Analysis with Awk
`awk` is a complete programming language designed for processing structured text and generating reports. It splits input lines into fields based on a specified delimiter (such as spaces or colons), allowing you to filter, manipulate, and format structured data fields (like logs, CSV files, and system files).""",
        "commands": r"""### Command & Syntax Reference
* **Text Editing (sed)**
  * `sed 's/old/new/' file.txt`: Replace the first occurrence of "old" with "new" on each line.
  * `sed 's/old/new/g' file.txt`: Replace all occurrences of "old" with "new" (global replace).
  * `sed -i 's/localhost/127.0.0.1/g' file.txt`: Apply modifications directly to the source file (inline edit).
  * `sed '/pattern/d' file.txt`: Delete all lines matching the specified pattern.
  * `sed -n '5,10p' file.txt`: Print only lines 5 through 10 of a file.

* **Structured Parsing (awk)**
  * `awk '{print $1}' file.txt`: Print the first field of each line (fields are space-delimited by default).
  * `awk -F':' '{print $1}' /etc/passwd`: Print the first field of each line using a colon as the field separator.
  * `awk '/pattern/ {print $0}' file.txt`: Print entire lines that match the specified pattern.
  * `awk '$3 > 1000 {print $1}' /etc/passwd`: Print user accounts with a User ID (UID) greater than 1000.
  * `awk 'END {print NR}' file.txt`: Print the total number of lines in a file.""",
        "examples": r"""### Real-World Examples

#### Example 1: Updating configuration parameters automatically
**Situation:** You need to update an application configuration file `/etc/app.conf` to enable debugging by changing `DEBUG=false` to `DEBUG=true` in a deployment script.
**Action:** Use `sed -i` to update the parameter in place.
```bash
sed -i 's/^DEBUG=false/DEBUG=true/' /etc/app.conf
```

#### Example 2: Extracting system user home directories
**Situation:** You need to generate a list of all local user accounts and their corresponding home directories from the system user file `/etc/passwd`.
**Action:** Use `awk` with a colon delimiter to extract user details.
```bash
awk -F':' '{print "User: " $1 "\t Home: " $6}' /etc/passwd > /tmp/user_homes.txt
```

#### Example 3: Deleting comment lines from configuration files
**Situation:** You need to review a configuration file `/etc/nginx/nginx.conf`, excluding all comment lines (lines starting with `#`) and empty lines to improve readability.
**Action:** Use `sed` to filter out comment and empty lines.
```bash
sed -e '/^#/d' -e '/^$/d' /etc/nginx/nginx.conf
```

#### Example 4: Summarizing system memory utilization
**Situation:** You need to extract and format the active system memory usage from the `/proc/meminfo` virtual filesystem file.
**Action:** Use `awk` to parse and format memory properties.
```bash
awk '/MemTotal/ {total=$2} /MemAvailable/ {avail=$2; print "Used Memory: " (total-avail)/1024 " MB"}' /proc/meminfo
```

#### Example 5: Appending lines to specific configurations
**Situation:** You need to add a new security policy parameter `Banner /etc/issue` to the end of the SSH configuration file `/etc/ssh/sshd_config`, but only if it is not already present.
**Action:** Use a conditional search and append command with `sed`.
```bash
grep -q "^Banner" /etc/ssh/sshd_config || sed -i '$a Banner /etc/issue' /etc/ssh/sshd_config
```""",
        "exercise": r"""### Hands-On Labs

#### Lab 1: Inline File Modifications
* **Objective:** Modify configuration files using inline stream editing.
* **Tasks:**
  1. Create a dummy configuration file `/tmp/web.conf` containing the text: `PORT=80` and `HOST=localhost`.
  2. Use `sed` to change the port configuration to `PORT=443` and write the modification back to the file.
  3. Change the host configuration to `HOST=server.local` and create a backup of the original file (`/tmp/web.conf.bak`) during modification using the `sed -i.bak` option.
  4. Verify that the changes were applied correctly and that the backup file was created.

#### Lab 2: Field Extraction on System Tables
* **Objective:** Parse system database tables using column delimiters.
* **Tasks:**
  1. View `/etc/passwd` to check its field layout.
  2. Use `awk` to extract user accounts (field 1) and their shell environment paths (field 7) from `/etc/passwd`.
  3. Filter the output to display only user accounts that use the `/bin/bash` shell.
  4. Save the filtered user list to `/tmp/active_admins.txt`.

#### Lab 3: Log Statistics and Calculations
* **Objective:** Perform arithmetic operations and count occurrences in logs.
* **Tasks:**
  1. Create a dummy web access log `/tmp/access.log` containing several lines of mock IP addresses and HTTP status codes (such as 200, 404, or 500).
  2. Use `awk` to count the occurrences of HTTP status 404 in the log file.
  3. Write a command to calculate and print the average response size (using size columns) of all logged requests.

#### Lab 4: Multi-Step Text Transformation Pipelines
* **Objective:** Combine text manipulation utilities to process complex data.
* **Tasks:**
  1. Use `df -h` to display filesystem space usage.
  2. Pipe the output to `awk` to extract the filesystem path (column 1) and the usage percentage (column 5).
  3. Use `sed` to remove the percentage sign (`%`) from the usage numbers to simplify parsing.
  4. Filter the output to display filesystems with disk utilization greater than 80%.

#### Lab 5: Dynamic Row Extraction and Pruning
* **Objective:** Extract and clean specific ranges of text from files.
* **Tasks:**
  1. Identify the line numbers of a configuration block within a test file.
  2. Use `sed` to extract and print only a specific range of lines (e.g., lines 10 through 20) from `/etc/services`.
  3. Use `sed` to delete all lines containing the word "test" in-place from a dummy file.""",
        "insight": r"""### Interview Q&A

#### Q1: What is the purpose of the -i flag in sed, and why should you use it with caution?
* **Answer:** The `-i` flag performs inline file modification, writing changes directly back to the source file instead of printing them to standard output. It should be used with caution because any errors in your `sed` expression will permanently overwrite the source file's contents. To protect your data, you can specify a backup extension (e.g., `sed -i.bak 's/old/new/g' file.txt`) to automatically create a backup of the original file before modifying it.

#### Q2: How do you print user accounts in /etc/passwd that have a UID greater than 1000 using awk?
* **Answer:** In `/etc/passwd`, fields are colon-delimited, and the User ID (UID) is stored in the 3rd field (`$3`). You specify the colon delimiter with `-F':'` and run a conditional check on the UID field:
```bash
awk -F':' '$3 >= 1000 {print $1}' /etc/passwd
```

#### Q3: What do the terms NR and NF represent in awk programming?
* **Answer:**
  * **`NR` (Number of Records):** Tracks the line number or record count of the input stream.
  * **`NF` (Number of Fields):** Tracks the number of columns or fields on the current active line.

#### Q4: How do you configure sed to delete empty lines from a file?
* **Answer:** Use the `sed` delete command (`d`) with the regular expression pattern `/^$/` (which matches lines where the start of the line `^` is immediately followed by the end of the line `$`):
```bash
sed '/^$/d' file.txt
```

#### Q5: Why is awk considered superior to cut for parsing log files with multiple spaces?
* **Answer:**
  * **`cut`:** Treats each individual space as a field delimiter. If a log file contains consecutive spaces, `cut` treats them as empty fields, leading to misaligned columns.
  * **`awk`:** Treats consecutive spaces or tabs as a single field separator by default, aligning columns and processing fields correctly.

### LFCS Exam Focus
*   **Speed up file editing:** Using `sed` or `awk` allows you to update configuration parameters quickly and non-interactively. This saves time during the exam compared to opening files and editing them manually in text editors."""
    },
    {
        "id": 6,
        "title": "Module 6: Local Git Repositories and Sysadmin Version Control",
        "theory": r"""### Git Version Control
Git is a distributed version control system used to track changes in source code and configuration files. It provides a history of changes, allowing you to roll back configurations to previous states and manage system configurations as code (Infrastructure as Code).

### The Three States of Git
Git tracks files across three primary states:
1. **Working Directory:** The local filesystem where files are created and edited.
2. **Staging Area (Index):** A landing zone where changes are selected and prepared for commit.
3. **Local Repository (.git directory):** Where Git stores committed changes permanently as snapshot metadata.

### Branching and Merging
Branching allows you to create isolated environments to develop and test configuration updates (such as a new patch) without affecting the stable production configurations in the primary branch (usually `main` or `master`). Merging combines changes from a development branch back into the primary branch once they have been tested and verified.""",
        "commands": r"""### Command & Syntax Reference
* **Repository Configurations**
  * `git config --global user.name "Sysadmin"`: Set the username for commits.
  * `git config --global user.email "admin@company.local"`: Set the email address for commits.
  * `git init`: Initialize a new local Git repository in the current directory.

* **Tracking Changes**
  * `git status`: Show the status of files (tracked, untracked, or modified).
  * `git add /opt/configs/app.conf`: Stage a specific file for commit.
  * `git add .`: Stage all modified and untracked files in the current directory.
  * `git commit -m "Configure production port"`: Save staged changes to the local repository.
  * `git log`: Display the commit history with author, date, and commit messages.

* **Branch and Merge Control**
  * `git branch`: List local branches (the active branch is marked with an asterisk).
  * `git branch feature-routing`: Create a new branch.
  * `git checkout feature-routing` / `git switch feature-routing`: Switch to a branch.
  * `git merge feature-routing`: Merge changes from a branch into the active branch.
  * `git branch -d feature-routing`: Delete a branch after it has been merged.""",
        "examples": r"""### Real-World Examples

#### Example 1: Initializing configuration version control
**Situation:** You need to track and version control system configuration files stored under `/etc/app/` to track updates and support rollback options.
**Action:** Initialize a Git repository in the configuration directory and configure your identity.
```bash
cd /etc/app/
git init
git config --local user.name "Lead Admin"
git config --local user.email "admin@local"
git add .
git commit -m "Initial commit of application configurations"
```

#### Example 2: Testing configuration patches safely using branches
**Situation:** You need to update an application configuration file `server.conf` on a separate branch, test the changes, and merge them back to the stable main branch.
**Action:** Create a patch branch, apply the changes, and merge them into the main branch.
```bash
# Switch to a new branch for testing
git checkout -b patch-server

# Apply the configuration changes
echo "TIMEOUT=60" >> server.conf
git add server.conf
git commit -m "Increase server timeout limit"

# Merge changes back to main
git checkout main
git merge patch-server
```

#### Example 3: Reverting incorrect configuration updates
**Situation:** A recent configuration change broke an application. You need to identify the broken changes and roll back the configuration files to the previous stable commit.
**Action:** Display the commit history and revert the changes to the previous commit.
```bash
# View the commit log to find the target commit ID
git log --oneline

# Revert changes to the specified stable commit
git revert 2ab45c1 --no-edit
```

#### Example 4: Ignoring temporary files in directories
**Situation:** You are tracking deployment scripts in a directory `/opt/scripts/`, but want to prevent Git from tracking temporary swap files or log files created during execution.
**Action:** Create a `.gitignore` file to define file exclusion patterns.
```bash
# Append file exclusion patterns to .gitignore
echo "*.tmp" >> /opt/scripts/.gitignore
echo "*.log" >> /opt/scripts/.gitignore
git add .gitignore
git commit -m "Add gitignore rules for logs and temporary files"
```

#### Example 5: Viewing modifications before committing
**Situation:** You have modified several deployment scripts in your working directory and want to review the exact lines changed before committing them.
**Action:** Display file modifications using the `git diff` utility.
```bash
git diff
```""",
        "exercise": r"""### Hands-On Labs

#### Lab 1: Local Repository Initialization and Baselines
* **Objective:** Initialize a Git repository and commit changes.
* **Tasks:**
  1. Create a directory `/root/iac_infra/` and initialize a new local Git repository inside it.
  2. Configure your local repository user identity (name and email).
  3. Create a configuration file named `deploy.yml` and add some content.
  4. Query the repository status to confirm that `deploy.yml` is listed as untracked.
  5. Stage and commit the file to the repository with a descriptive commit message.

#### Lab 2: Safe Configuration Patching
* **Objective:** Manage features and fixes using Git branches.
* **Tasks:**
  1. Create a development branch named `dev-config` and switch to it.
  2. Create a new file named `routes.conf` containing configuration parameters.
  3. Stage and commit the new file to the `dev-config` branch.
  4. Switch back to the `main` branch and verify that `routes.conf` is not present in the directory.
  5. Merge the `dev-config` branch into the `main` branch, and verify that the file is now present in the main directory.

#### Lab 3: Tracking Modification Histories
* **Objective:** Review commit logs and examine historical changes.
* **Tasks:**
  1. Modify `deploy.yml` in `/root/iac_infra/` and commit the changes.
  2. Repeat this process three times, making minor modifications and committing them each time.
  3. Display your commit history to verify all commits are logged.
  4. Display the log history showing the exact line differences introduced in each commit.

#### Lab 4: Discarding Working Changes
* **Objective:** Discard uncommitted changes in your working directory to restore file states.
* **Tasks:**
  1. Modify an existing tracked file in your repository.
  2. Run `git status` to verify that the file is modified but not staged.
  3. Discard the uncommitted changes and restore the file to its last committed state using `git checkout -- <file>` or `git restore <file>`.
  4. Verify that your uncommitted modifications were discarded and that the file state was restored.

#### Lab 5: Resolving Configuration Conflicts
* **Objective:** Resolve conflicts that occur during file merges.
* **Tasks:**
  1. Create a branch named `conflict-test` and modify line 1 of `deploy.yml`. Commit the changes.
  2. Switch back to `main` and modify line 1 of `deploy.yml` with conflicting content. Commit the changes.
  3. Attempt to merge `conflict-test` into `main` and observe the merge conflict error.
  4. Open `deploy.yml`, resolve the conflict manually, mark the file as resolved using `git add`, and finalize the merge commit.""",
        "insight": r"""### Interview Q&A

#### Q1: What is the difference between git add and git commit?
* **Answer:**
  * **`git add`:** Moves changes from the local working directory to the staging area (index), preparing them to be committed.
  * **`git commit`:** Saves the staged snapshot permanently to the local repository history.

#### Q2: How do you identify the differences between your active working directory and your last committed snapshot?
* **Answer:** Run the `git diff` command. To view differences in files that have already been staged, add the `--cached` (or `--staged`) flag:
```bash
git diff --staged
```

#### Q3: Why is a .gitignore file useful in production environments?
* **Answer:** It prevents Git from tracking temporary, dynamic, or sensitive files (such as logs, temporary cache files, build directories, database dumps, and files containing API keys or passwords), keeping the repository clean and secure.

#### Q4: What is the difference between git merge and git rebase?
* **Answer:**
  * **`git merge`:** Combines the histories of two branches by creating a new merge commit. It preserves the complete historical timeline of both branches, showing when branches diverged and merged.
  * **`git rebase`:** Moves or "replays" commits from one branch on top of another branch, creating a linear project history without merge commits.

#### Q5: How do you roll back configuration changes to a previous stable commit in your history?
* **Answer:**
  * To undo changes by creating a new commit that reverts modifications, use `git revert <commit_id>`. This is recommended for shared repositories because it preserves history.
  * To permanently delete commits and reset the branch state, use `git reset --hard <commit_id>`. This should be used with caution as it permanently overwrites uncommitted changes and history.

### LFCS Exam Focus
*   **Keep Git commands simple:** The LFCS exam checks basic version control skills. Memorize how to initialize a repository, check status, stage files (`git add`), and commit changes (`git commit`). Avoid complex Git workflows unless specifically requested."""
    },
    {
        "id": 7,
        "title": "Module 7: PKI Infrastructure, Private Keys, and SSL/TLS Certificates",
        "theory": r"""### Public Key Infrastructure (PKI)
Public Key Infrastructure (PKI) secures network communications using asymmetric cryptography. It uses mathematical key pairs to authenticate systems and encrypt traffic:
*   **Private Key:** Kept secret on the host system. It is used to decrypt data and sign communications.
*   **Public Key:** Shared publicly with client systems. It is used to encrypt data and verify cryptographic signatures.

### Certificates & Signing Requests
*   **Certificate Signing Request (CSR):** A secure file containing your public key and organization details (such as Common Name, location, and domain names). It is sent to a Certificate Authority (CA) to be signed.
*   **SSL/TLS Certificate:** A signed public key file used to establish trust.
*   **Self-Signed Certificate:** Signed using its own private key rather than a trusted public CA. It provides encryption but lacks external validation, making it ideal for local testing environments.""",
        "commands": r"""### Command & Syntax Reference
* **Private Key Management**
  * `openssl genrsa -out /etc/ssl/private/web.key 2048`: Generate a 2048-bit RSA private key.
  * `openssl rsa -in web.key -pubout -out web_public.key`: Extract the public key from a private key file.

* **CSR and Certificate Generation**
  * `openssl req -new -key web.key -out web.csr`: Interactively generate a new Certificate Signing Request.
  * `openssl req -new -newkey rsa:2048 -nodes -keyout app.key -out app.csr -subj "/C=US/ST=Texas/O=Corp/CN=app.local"`: Generate a private key and a CSR in a single non-interactive command.
  * `openssl x509 -req -days 365 -in web.csr -signkey web.key -out web.crt`: Sign a CSR using your private key to create a self-signed certificate.

* **Certificate Inspection**
  * `openssl x509 -in /etc/ssl/certs/ca-certificates.crt -noout -text`: View certificate metadata in plain text format.
  * `openssl x509 -in web.crt -noout -dates`: Display only the validity dates of a certificate.
  * `openssl s_client -connect google.com:443`: Establish an SSL/TLS connection to a remote host to inspect its certificate chain.""",
        "examples": r"""### Real-World Examples

#### Example 1: Creating a non-interactive self-signed certificate
**Situation:** You are deploying a local testing environment and need to secure your web server immediately with a self-signed certificate valid for 365 days.
**Action:** Generate a private key and a self-signed certificate in a single non-interactive command.
```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/nginx-self.key \
  -out /etc/ssl/certs/nginx-self.crt \
  -subj "/C=US/ST=California/L=SanFrancisco/O=IT/CN=dev.server.local"
```

#### Example 2: Verifying a certificate's expiration date
**Situation:** A secure web service is throwing SSL errors. You need to inspect the server's certificate file `/etc/ssl/certs/web.crt` to verify if it has expired.
**Action:** Extract and view the certificate's validity dates using `openssl`.
```bash
openssl x509 -in /etc/ssl/certs/web.crt -noout -dates
```

#### Example 3: Extracting the public key from a private key
**Situation:** You need to recover or verify the public key associated with an existing system private key `/etc/ssl/private/database.key`.
**Action:** Extract and write the public key to a file using the `openssl rsa` utility.
```bash
openssl rsa -in /etc/ssl/private/database.key -pubout -out /etc/ssl/certs/database_pub.key
```

#### Example 4: Verifying match status between key and certificate
**Situation:** A web server fails to start, throwing "private key mismatch" errors. You need to verify if the certificate `/etc/ssl/certs/web.crt` matches the private key `/etc/ssl/private/web.key`.
**Action:** Calculate and compare the md5 hash fingerprints of both files.
```bash
CRT_MD5=$(openssl x509 -noout -modulus -in /etc/ssl/certs/web.crt | openssl md5)
KEY_MD5=$(openssl rsa -noout -modulus -in /etc/ssl/private/web.key | openssl md5)
[ "$CRT_MD5" = "$KEY_MD5" ] && echo "Matched" || echo "Mismatch"
```

#### Example 5: Testing remote server certificates
**Situation:** You need to test an internal web server `192.168.1.10` over port `443` to verify if it is serving the correct certificate chain.
**Action:** Query the server's SSL connection port using `openssl s_client`.
```bash
openssl s_client -connect 192.168.1.10:443 -showcerts < /dev/null
```""",
        "exercise": r"""### Hands-On Labs

#### Lab 1: Generating RSA Keys
* **Objective:** Create and manage system private keys securely.
* **Tasks:**
  1. Create a directory named `/tmp/pki_lab/`.
  2. Generate a 4096-bit RSA private key named `ca_root.key` inside the directory.
  3. Change the permissions on `ca_root.key` so that it is readable only by the owner.
  4. Extract the public key from `ca_root.key` and save it to `/tmp/pki_lab/ca_pub.key`.

#### Lab 2: Generating CSR Profiles
* **Objective:** Generate a Certificate Signing Request with organization details.
* **Tasks:**
  1. Generate a 2048-bit RSA private key named `client.key`.
  2. Generate a CSR named `client.csr` using the private key.
  3. Configure the CSR with the following details: Common Name: `api.client.local`, Organization: `IT Security`, Location: `Amsterdam`.
  4. Verify the contents of `client.csr` to confirm your configurations.

#### Lab 3: Creating and Signing Certificates
* **Objective:** Create and sign a certificate using local keys.
* **Tasks:**
  1. Generate a self-signed certificate named `local_dev.crt` using the private key and CSR from Lab 2.
  2. Set the certificate to remain valid for exactly 180 days.
  3. Inspect the certificate metadata to verify the expiration dates.

#### Lab 4: Extracting Certificate Metadata
* **Objective:** Query certificate properties and export metadata.
* **Tasks:**
  1. Locating the system certificate folder on your machine (e.g., `/etc/ssl/certs/`).
  2. Select an active certificate file and inspect its issuer details.
  3. Extract the certificate's serial number and save it to `/tmp/cert_serial.txt`.

#### Lab 5: Auditing Certificate Chains
* **Objective:** Verify remote service certificates.
* **Tasks:**
  1. Query a public website (e.g., `kubernetes.io:443`) using `openssl s_client`.
  2. Capture and extract the server's certificate chain details.
  3. Save the returned certificates locally to `/tmp/remote_chain.pem`.
  4. Inspect the saved files to identify the issuing Certificate Authority.""",
        "insight": r"""### Interview Q&A

#### Q1: What is the difference between a private key, a CSR, and an SSL certificate?
* **Answer:**
  * **Private Key:** A secret cryptographic key file used to sign data and decrypt traffic. It must never be shared.
  * **CSR (Certificate Signing Request):** A request file containing your public key and organization details. It is sent to a Certificate Authority (CA) for verification and signing.
  * **SSL Certificate:** A verified public key file signed by a CA. It is shared publicly to establish trust and establish encrypted connections.

#### Q2: Why is a self-signed certificate not trusted by web browsers?
* **Answer:** Web browsers only trust certificates that are issued and signed by recognized Certificate Authorities (such as Let's Encrypt or DigiCert) whose root certificates are pre-installed in the browser's trust store. Because a self-signed certificate is signed using its own private key, browsers cannot verify its identity, displaying security warnings.

#### Q3: How do you verify if an SSL certificate file matches a specific private key?
* **Answer:** Calculate and compare the cryptographic md5 hash of the modulus of both files. If the hash values match, the certificate belongs to that private key:
```bash
openssl x509 -noout -modulus -in cert.crt | openssl md5
openssl rsa -noout -modulus -in key.key | openssl md5
```

#### Q4: What is the purpose of the -nodes flag in OpenSSL key generation?
* **Answer:** The `-nodes` flag (which stands for "no DES") prevents OpenSSL from encrypting the private key with a password. This allows services (like Apache or Nginx) to read the private key file directly during startup without requiring manual password entry.

#### Q5: How do you check if an SSL certificate file has expired using command-line utilities?
* **Answer:** Run `openssl x509` with the `-noout` and `-dates` flags to display the certificate's start and end validity dates:
```bash
openssl x509 -in cert.crt -noout -dates
```

### LFCS Exam Focus
*   **Generate keypairs correctly:** When generating private keys, make sure to use the specific key size (e.g., 2048-bit or 4096-bit) and algorithm requested in the task. Double-check your pathing and spelling to ensure configuration files point to the correct files."""
    },
    {
        "id": 8,
        "title": "Module 8: Kernel Tuning via ProcFS, Sysctl, and Module Controls",
        "theory": r"""### Operating System Kernels
The Linux kernel is the core of the operating system, managing system hardware and resource allocations. It exposes active runtime settings and hardware details within two virtual filesystems:
*   **`/proc` (Process Filesystem):** Interfaces with kernel structures, displaying active system parameters and process details.
*   **`/sys` (System Filesystem):** Displays device configurations and hardware parameters.
Files in these directories do not occupy space on the physical disk; they are virtual interfaces managed directly by the kernel.

### Dynamic Kernel Tuning with Sysctl
Administrators can modify kernel behaviors at runtime by editing virtual files under `/proc/sys/`. Changes made directly to these files are non-persistent and will be lost upon reboot. To apply modifications persistently, write configurations to `/etc/sysctl.conf` or configuration files under `/etc/sysctl.d/`, loading changes using the `sysctl` command.

### Kernel Module Management
The Linux kernel uses a modular architecture, allowing drivers and features (kernel modules) to be loaded and unloaded dynamically as needed. This prevents the kernel from consuming excessive memory. System tools (such as `lsmod`, `modinfo`, `modprobe`) manage module lifecycles, and configurations under `/etc/modprobe.d/` handle persistent module loading policies.""",
        "commands": r"""### Command & Syntax Reference
* **Runtime Tuning (sysctl)**
  * `sysctl -a`: List all active kernel parameters.
  * `sysctl net.ipv4.ip_forward`: Display the status of a specific kernel parameter.
  * `sysctl -w net.ipv4.ip_forward=1`: Modify a kernel parameter immediately (non-persistent).
  * `sysctl -p`: Reload and apply configurations persistently from `/etc/sysctl.conf`.

* **Kernel Module Controls**
  * `lsmod`: List all loaded kernel modules.
  * `modinfo dummy`: Display detailed information and parameters for a module.
  * `modprobe dummy`: Load a module and its dependencies.
  * `modprobe -r dummy`: Unload a module.
  * `depmod -a`: Rebuild the module dependency database file (`modules.dep`).""",
        "examples": r"""### Real-World Examples

#### Example 1: Enabling persistent IP routing
**Situation:** You are configuring a Linux server to act as a network router. You need to enable IP forwarding and make the configuration persistent.
**Action:** Modify the kernel parameter using `sysctl` and save the configuration to `/etc/sysctl.conf`.
```bash
sysctl -w net.ipv4.ip_forward=1
echo "net.ipv4.ip_forward = 1" >> /etc/sysctl.conf
sysctl -p
```

#### Example 2: Loading virtual network interface modules
**Situation:** A development project requires a virtual test interface. You need to load the `dummy` network driver module immediately.
**Action:** Load the module using the `modprobe` utility.
```bash
modprobe dummy
ip link show dummy0
```

#### Example 3: Blocking modules from loading (Blacklisting)
**Situation:** A kernel module `floppy` is causing system stability issues. You need to prevent it from loading automatically.
**Action:** Blacklist the module by creating a configuration file under `/etc/modprobe.d/`.
```bash
echo "blacklist floppy" > /etc/modprobe.d/blacklist-floppy.conf
```

#### Example 4: Increasing maximum open file limits
**Situation:** A high-traffic database server is hitting system limits. You need to increase the maximum system-wide file descriptor limit to `2097152`.
**Action:** Apply the kernel limit using `sysctl`.
```bash
sysctl -w fs.file-max=2097152
echo "fs.file-max = 2097152" >> /etc/sysctl.conf
sysctl -p
```

#### Example 5: Identifying hardware details from kernel buffers
**Situation:** A network adapter is failing to initialize. You need to inspect the kernel's ring buffer logs to identify driver startup errors.
**Action:** Query the kernel logs using the `dmesg` utility.
```bash
dmesg | grep -i "eth"
```""",
        "exercise": r"""### Hands-On Labs

#### Lab 1: Modifying Kernels via Procfs
* **Objective:** Modify kernel parameters using the `/proc` filesystem.
* **Tasks:**
  1. Check the active status of system ICMP redirects: `cat /proc/sys/net/ipv4/conf/all/accept_redirects`.
  2. Change the value to `0` (disabled) by writing directly to the virtual file.
  3. Verify that the parameter has updated.
  4. Reboot the machine and verify that the setting has reverted back to its default value.

#### Lab 2: Persistent Sysctl Tuning
* **Objective:** Apply kernel configurations persistently.
* **Tasks:**
  1. Open `/etc/sysctl.conf` in a text editor.
  2. Append the following parameters:
     ```text
     net.ipv4.conf.all.accept_redirects = 0
     vm.swappiness = 15
     ```
  3. Reload the configurations using `sysctl -p` to apply changes immediately.
  4. Verify that the updated parameters are active on the system.

#### Lab 3: Manual Module Lifecycle Control
* **Objective:** Load, verify, and unload kernel modules.
* **Tasks:**
  1. Run `lsmod` and verify if the `bridge` module is loaded.
  2. Query details and dependency rules for the `bridge` module using `modinfo`.
  3. Load the module using `modprobe`.
  4. Unload the module and verify that it has been removed from the loaded module list.

#### Lab 4: Tracking Active Kernel Status
* **Objective:** Extract active system parameters from virtual files.
* **Tasks:**
  1. Identify your system's active kernel version by reading `/proc/version` or running `uname -r`.
  2. Inspect `/proc/cpuinfo` to identify your system's CPU model and core count.
  3. Save the active system parameters to `/tmp/kernel_audit.txt`.

#### Lab 5: Troubleshooting Module Failures
* **Objective:** Diagnose and rebuild kernel module dependency trees.
* **Tasks:**
  1. Delete or rename a test module file from the kernel directory (e.g., `/lib/modules/$(uname -r)/`).
  2. Run `depmod -a` to rebuild the module dependency map.
  3. Check the system log outputs to verify that the dependency tree was rebuilt successfully.
  4. Restore the module file to its original location.""",
        "insight": r"""### Interview Q&A

#### Q1: What is the difference between making changes in /proc/sys/ and writing to /etc/sysctl.conf?
* **Answer:**
  * **`/proc/sys/`:** Modifies kernel parameters directly in system memory. These changes are applied immediately, but are non-persistent and will be lost when the system reboots.
  * **`/etc/sysctl.conf`:** Stores kernel parameter configurations persistently on disk. These settings are loaded into system memory during boot, or applied immediately by running the `sysctl -p` command.

#### Q2: What is the difference between modprobe and insmod?
* **Answer:**
  * **`modprobe`:** A smart module management tool. It loads a module, automatically resolves and loads its dependent modules, and searches standard directory paths.
  * **`insmod`:** A basic module loading tool. It requires the absolute path to a specific kernel module file (`.ko`) and fails to load if the module has unresolved dependencies.

#### Q3: How do you identify the parameters and configuration options supported by a specific kernel module?
* **Answer:** Run the `modinfo` command followed by the module name to display module metadata, author, license, and supported parameters:
```bash
modinfo dummy
```

#### Q4: Why is it important to run depmod after updating or installing custom kernel modules?
* **Answer:** The `depmod` command scans the kernel module directories and rebuilds the dependency map file (`modules.dep`). The `modprobe` command reads this dependency file to identify and load a module's dependencies. If you install a custom module without running `depmod`, `modprobe` may fail to load the module.

#### Q5: How do you configure a kernel module to load automatically during system startup?
* **Answer:** Create a configuration file ending in `.conf` inside `/etc/modules-load.d/` and add the name of the module to the file.
```bash
echo "dummy" > /etc/modules-load.d/dummy.conf
```

### LFCS Exam Focus
*   **Always apply sysctl changes persistently:** If you are asked to modify a kernel parameter (such as `net.ipv4.ip_forward` or `vm.swappiness`), make sure to write the parameter to `/etc/sysctl.conf` and run `sysctl -p`. Graders reboot the virtual machines, and any non-persistent changes will be lost."""
    },
    {
        "id": 9,
        "title": "Module 9: Process Management, Resource Allocations, and Signal Controls",
        "theory": r"""### Operating System Processes
A process is an active instance of a running program. Every process is assigned a unique Process ID (PID) by the kernel. Processes are organized in a parent-child hierarchy, where the `systemd` daemon (PID 1) acts as the root parent process.

### Process States & Monitoring
Processes run in several distinct operational states, managed by the kernel:
*   **Running/Runnable (R):** Actively executing or waiting in the CPU run queue.
*   **Sleeping (S / D):** Waiting for resources or system events. Interruptible sleep (S) can be interrupted by signals, while uninterruptible sleep (D) is waiting for hardware operations (like disk I/O) and cannot be interrupted.
*   **Stopped (T):** Paused by a process control signal.
*   **Zombie (Z):** Terminated processes whose exit status has not yet been read by their parent process, consuming system process slots.

### Process Signaling
The kernel uses system signals to control process states. Administrators send signals using utilities like `kill`, `pkill`, or `killall` to terminate, pause, or resume processes.

### Nice Values & Priorities
The kernel manages CPU scheduling using process priority values ranging from `-20` (highest priority, receives more CPU cycles) to `19` (lowest priority). Administrators adjust process priorities using nice values, which range from `-20` (highest priority) to `19` (lowest priority). Only the root user can assign negative nice values.""",
        "commands": r"""### Command & Syntax Reference
* **Process Monitoring**
  * `ps aux`: List all running processes with user, CPU, and memory utilization.
  * `ps -ef`: List processes in standard format with parent process IDs (PPID).
  * `top` / `htop`: Real-time interactive process monitoring.
  * `pgrep -u root nginx`: Find the PIDs of processes matching specified filters.

* **Process Signals**
  * `kill -15 <PID>` (SIGTERM): Gracefully terminate a process.
  * `kill -9 <PID>` (SIGKILL): Force-terminate a process immediately.
  * `kill -1 <PID>` (SIGHUP): Reload a process configuration file.
  * `pkill -f nginx`: Terminate processes based on matching patterns.

* **Priority Controls**
  * `nice -n 10 backup.sh`: Launch a process with a custom nice value.
  * `renice -n -5 -p 2049`: Adjust the nice value of an active running process.""",
        "examples": r"""### Real-World Examples

#### Example 1: Force-terminating frozen applications
**Situation:** An application process (PID `4092`) has hung, is consuming 100% CPU, and does not respond to standard stop requests.
**Action:** Force-terminate the process immediately using a SIGKILL signal.
```bash
kill -9 4092
```

#### Example 2: Adjusting process priorities on database servers
**Situation:** A backup process (PID `10928`) is consuming too many CPU cycles, slowing down a database. You need to reduce its execution priority.
**Action:** Increase the process nice value using `renice`.
```bash
renice -n 15 -p 10928
```

#### Example 3: Running system processes with high priorities
**Situation:** You need to launch a critical resource-monitoring script `/opt/monitor.sh` with a high execution priority to ensure it receives CPU cycles.
**Action:** Launch the process with a negative nice value.
```bash
nice -n -10 /opt/monitor.sh &
```

#### Example 4: Non-interactive service configuration reloads
**Situation:** You updated the Nginx web server configuration and need to apply the changes without restarting the service or disconnecting active connections.
**Action:** Send a SIGHUP signal to the master process to reload its configuration.
```bash
pkill -1 nginx
```

#### Example 5: Finding resource-intensive processes
**Situation:** A server is running slowly. You need to identify the top 5 processes consuming the most system memory.
**Action:** Query and sort system processes using `ps`.
```bash
ps aux --sort=-%mem | head -n 6
```""",
        "exercise": r"""### Hands-On Labs

#### Lab 1: Monitoring Dynamic Processes
* **Objective:** Monitor and sort active system processes.
* **Tasks:**
  1. Open a terminal and run `top` or `htop`.
  2. Sort processes by memory usage by pressing `M` (or interactive controls).
  3. Sort processes by CPU usage by pressing `P`.
  4. Search for a specific process (like `systemd`) by pressing the search key.
  5. Exit the monitor by pressing `q`.

#### Lab 2: Process Control and Signal Workflows
* **Objective:** Manage process execution states using signals.
* **Tasks:**
  1. Start a long background process: `dd if=/dev/zero of=/dev/null &`.
  2. Locate the process PID using `pgrep`.
  3. Pause the process by sending a SIGSTOP signal: `kill -19 <PID>`.
  4. Verify that the process state has changed to Stopped (T) using `ps`.
  5. Resume the process by sending a SIGCONT signal: `kill -18 <PID>`, and verify it is running again before terminating it.

#### Lab 3: Priority Adjustments with Nice and Renice
* **Objective:** Modify process execution priorities.
* **Tasks:**
  1. Launch a process with a custom low-priority nice value of `10`: `sleep 1000 &`.
  2. Verify the nice value of the process using `ps -o pid,ni,cmd`.
  3. Increase the process priority to a nice value of `-5` using `renice`.
  4. Observe the command output and note why non-root users cannot assign negative nice values.

#### Lab 4: Identifying Zombie Processes
* **Objective:** Locate and troubleshoot zombie processes on a server.
* **Tasks:**
  1. Run a command to search for active zombie (Z) processes: `ps aux | grep 'Z'`.
  2. Identify the parent process ID (PPID) of any discovered zombie processes.
  3. Send a SIGHUP signal to the parent process to clear the zombie process.
  4. Explain why zombie processes cannot be terminated directly using SIGKILL.

#### Lab 5: Process Auditing and Resource Tracking
* **Objective:** Track system resources consumed by specific users.
* **Tasks:**
  1. List all active processes owned by a specific user account.
  2. Write a command pipeline to calculate the total memory utilization of all processes owned by that user.
  3. Save the results to `/tmp/user_resources.txt` for audit review.""",
        "insight": r"""### Interview Q&A

#### Q1: What is the difference between SIGTERM (15) and SIGKILL (9)?
* **Answer:**
  * **SIGTERM (15):** The standard termination signal. It requests a process to stop, allowing it to save its state, release system resources, and close active connections cleanly before exiting. It can be handled, ignored, or blocked by the process.
  * **SIGKILL (9):** A force-termination signal managed directly by the kernel. It terminates the process immediately, preventing it from performing cleanup operations, saving data, or closing connections. It cannot be handled, blocked, or ignored.

#### Q2: What is a zombie process, and how do you remove it from the system?
* **Answer:** A zombie process is a process that has completed execution but still has an entry in the kernel's process table. This entry is kept so the parent process can read the child's exit status. If the parent fails to read it, the process remains as a zombie. You cannot kill a zombie process directly because it is already dead. To remove a zombie, send a SIGHUP or SIGCHLD signal to the parent process to force it to clean up, or terminate the parent process.

#### Q3: Why is a process running in uninterruptible sleep (D) state immune to SIGKILL?
* **Answer:** Uninterruptible sleep (D) is a process state used when a process is waiting for direct hardware operations (such as disk read/write or network I/O). The kernel prevents any signals from interrupting the process during these operations to avoid data corruption. A process in this state will ignore SIGKILL until the hardware operation completes. If a device fails or hangs, the process may remain in the D state until the system is rebooted.

#### Q4: How do nice values affect process scheduling in Linux?
* **Answer:** Nice values range from `-20` (highest priority, receives more CPU cycles) to `19` (lowest priority). A higher nice value makes the process "nicer" to other processes, yielding CPU cycles to others. A negative nice value increases a process's priority, allowing it to consume more CPU resources. Only the root user can assign negative nice values.

#### Q5: How do you identify the parent process of a running process using standard command-line tools?
* **Answer:** Run `ps` with parent-process columns (`-ef` or specifying custom output columns):
```bash
ps -o pid,ppid,cmd -p <PID>
```

### LFCS Exam Focus
*   **Locate process details fast:** You must be able to quickly identify resource-intensive processes, locate their PIDs, and adjust their priority or terminate them. Memorize how to use `ps` with sorting flags (e.g., `ps aux --sort=-%cpu`) and `pgrep` to locate processes by name."""
    },
    {
        "id": 10,
        "title": "Module 10: Systemd Unit Engineering, Logging, and Task Timers",
        "theory": r"""### Systemd System Initialization
Systemd is the primary initialization engine and system service manager. It controls system startup, manages background services, mounts filesystems, and handles system state transitions (targets).

### Systemd Service Units
Systemd organizes resources using unit files. The most common units are **Service Units** (`.service`), which define how background applications and daemons are started, managed, and stopped. These unit files specify execution parameters, dependencies, system resource allocations, and recovery actions. System-wide unit files are stored in `/lib/systemd/system/` (managed by the package manager) and `/etc/systemd/system/` (managed by system administrators).

### System Logging with Journald
Systemd uses `journald` to collect, consolidate, and store system log messages. It collects logs from the kernel, services, and system events, storing them in a binary format that can be quickly queried and filtered using the `journalctl` utility.

### Systemd Timers
Systemd Timers (`.timer` units matched with `.service` units) provide a modern alternative to traditional cron jobs. They support sub-second timing, resource limits, and complex execution schedules linked directly to system states (such as system boot or service status).""",
        "commands": r"""### Command & Syntax Reference
* **Service Management**
  * `systemctl start apache2`: Start a service.
  * `systemctl stop apache2`: Stop a service.
  * `systemctl restart apache2`: Restart a service.
  * `systemctl enable apache2`: Configure a service to start automatically during boot.
  * `systemctl disable apache2`: Prevent a service from starting automatically during boot.
  * `systemctl status apache2`: View detailed service status and recent log messages.
  * `systemctl is-enabled apache2`: Check if a service is configured to start during boot.
  * `systemctl daemon-reload`: Re-scan system unit files and apply modifications made to unit configuration files on disk.

* **System Log Queries (journalctl)**
  * `journalctl`: Display all system logs.
  * `journalctl -f`: Monitor system logs in real time (follow mode).
  * `journalctl -u nginx.service`: Display logs for a specific service unit.
  * `journalctl -b -0`: Display logs generated during the current boot cycle.
  * `journalctl --since "2026-07-22 10:00:00"`: Filter logs generated after a specific time.
  * `journalctl -p err`: Filter logs by a specific priority level (e.g., errors).

* **Systemd Timers**
  * `systemctl list-timers`: List all active system timers and their next scheduled run times.""",
        "examples": r"""### Real-World Examples

#### Example 1: Creating a custom systemd service
**Situation:** You need to deploy a custom backup script `/usr/local/bin/db_backup.sh` as a background system service that restarts automatically if it fails.
**Action:** Create a custom service unit file in `/etc/systemd/system/db_backup.service`.
```ini
[Unit]
Description=Database Backup Daemon
After=network.target

[Service]
Type=simple
ExecStart=/bin/bash /usr/local/bin/db_backup.sh
Restart=on-failure
RestartSec=10
User=root

[Install]
WantedBy=multi-user.target
```
```bash
# Register and start the new service
systemctl daemon-reload
systemctl enable --now db_backup.service
```

#### Example 2: Filtering logs to troubleshoot a failing service
**Situation:** The Nginx web server is failing to start. You need to inspect its recent error logs from the current boot cycle to identify the issue.
**Action:** Query the service logs using `journalctl`.
```bash
journalctl -b 0 -u nginx.service -p err --no-pager
```

#### Example 3: Configuring systemd timers for periodic cleanup
**Situation:** You need to configure a system cleanup service `/etc/systemd/system/cleanup.service` to run every day at 1:00 AM using systemd timers.
**Action:** Create matching `.service` and `.timer` files in `/etc/systemd/system/`.
```ini
# File: /etc/systemd/system/cleanup.service
[Unit]
Description=Daily System Cleanup

[Service]
Type=oneshot
ExecStart=/bin/rm -rf /tmp/scratch/*
```
```ini
# File: /etc/systemd/system/cleanup.timer
[Unit]
Description=Run Daily Cleanup at 1AM

[Timer]
OnCalendar=*-*-* 01:00:00
Persistent=true

[Install]
WantedBy=timers.target
```
```bash
# Enable the timer
systemctl daemon-reload
systemctl enable --now cleanup.timer
```

#### Example 4: Unmasking a blocked service
**Situation:** A system update has "masked" the postfix service, preventing it from starting or being enabled. You need to unmask and start it.
**Action:** Unmask the service and start it.
```bash
systemctl unmask postfix
systemctl start postfix
```

#### Example 5: Limiting journal log storage space
**Situation:** System logs are consuming too much disk space. You need to limit the maximum log storage size to 2GB.
**Action:** Modify the journald configuration file `/etc/systemd/journald.conf`.
```ini
# Edit /etc/systemd/journald.conf with the following limit:
SystemMaxUse=2G
```
```bash
# Restart the journal daemon to apply the change:
systemctl restart systemd-journald
```""",
        "exercise": r"""### Hands-On Labs

#### Lab 1: Deploying Custom Background Services
* **Objective:** Create and manage a custom systemd service.
* **Tasks:**
  1. Create a simple script `/opt/alive.sh` that writes the current date to `/tmp/alive.log` every 5 seconds.
  2. Create a systemd service file `/etc/systemd/system/alive.service` to manage this script as a background service.
  3. Load and register the service using `systemctl daemon-reload`.
  4. Enable the service to start on boot and start it immediately.
  5. Verify that the service is running and check its logs.

#### Lab 2: Service Troubleshooting and Failure Analysis
* **Objective:** Diagnose and fix service configuration errors.
* **Tasks:**
  1. Modify your custom `/etc/systemd/system/alive.service` file to point to a non-existent script path.
  2. Reload systemd and restart the service.
  3. Verify that the service has failed using `systemctl status`.
  4. Use `journalctl` to inspect the error messages and identify the incorrect path.
  5. Correct the path, reload systemd, and verify that the service starts successfully.

#### Lab 3: Log Auditing with Journalctl
* **Objective:** Query and filter system logs using journalctl.
* **Tasks:**
  1. Query system logs generated over the last 30 minutes.
  2. Filter the logs to display messages from a specific service (such as `ssh` or `sshd`).
  3. Filter the logs to display only error and critical messages.
  4. Save the filtered log results to `/tmp/recent_errors.log`.

#### Lab 4: Creating Calendar-Based Timers
* **Objective:** Schedule tasks using systemd timers.
* **Tasks:**
  1. Create a systemd service `/etc/systemd/system/ping_check.service` that logs a ping response to a log file.
  2. Create a timer unit `/etc/systemd/system/ping_check.timer` to run the service every 15 minutes.
  3. Start and enable the timer.
  4. Run `systemctl list-timers` to verify that the timer is listed and scheduled.

#### Lab 5: Controlling Service Boot States
* **Objective:** Manage service autostart configurations.
* **Tasks:**
  1. Check if the web server service (such as `apache2` or `httpd`) is configured to start during boot.
  2. Disable the service and verify its boot state using `systemctl is-enabled`.
  3. Enable the service again to restore autostart.
  4. Mask the service to block it from being started manually, and verify its masked state.""",
        "insight": r"""### Interview Q&A

#### Q1: What does it mean when a systemd service is masked, and how do you unmask it?
* **Answer:** Masking a service is a stronger version of disabling it. When a service is masked, systemd symlinks its unit file to `/dev/null`, preventing it from being started manually or triggered by other services or timers. To restore the service, you must unmask it:
```bash
systemctl unmask service_name
```

#### Q2: Why must you run systemctl daemon-reload after editing a systemd unit file?
* **Answer:** Systemd caches unit file configurations in system memory during startup. If you modify a unit file on the disk, systemd's memory cache is out of sync with the filesystem. Running `systemctl daemon-reload` tells systemd to re-scan the unit file directories and update its cache with your changes.

#### Q3: How do you filter journalctl logs to display only messages from the current boot cycle?
* **Answer:** Use the `-b` flag (with `0` representing the current boot cycle, `-1` representing the previous boot, and so on):
```bash
journalctl -b 0
```

#### Q4: What is the purpose of the [Install] section in a systemd unit file?
* **Answer:** The `[Install]` section defines how a service is enabled or disabled. It specifies which target (e.g., `multi-user.target`) should trigger the service. When you run `systemctl enable`, systemd reads this section and creates symlinks in the corresponding target directory (such as `/etc/systemd/system/multi-user.target.wants/`).

#### Q5: How do you configure a systemd service to restart automatically if it crashes?
* **Answer:** In the `[Service]` section of the unit file, configure the `Restart` parameter (e.g., `Restart=on-failure`) and define a restart delay using `RestartSec` (e.g., `RestartSec=10` to wait 10 seconds before restarting):
```ini
[Service]
Restart=on-failure
RestartSec=10
```

### LFCS Exam Focus
*   **Daemon-reload is critical:** A common mistake is editing a systemd service file but forgetting to run `systemctl daemon-reload` before testing the service. If you skip this step, systemd will use its old cached settings, which can cause tasks to fail grading."""
    },
    {
        "id": 11,
        "title": "Module 11: Package Lifecycle, Repository Structures, and Source Compilation",
        "theory": r"""### Software Package Management
Software package management systems automate the installation, updating, configuration, and removal of software on Linux systems. These systems track package dependencies, ensuring that all required libraries and packages are installed automatically.

### Distribution Package Managers
*   **Debian/Ubuntu Systems:** Use the Advanced Package Tool (`apt`) to manage `.deb` software packages. Repository sources are configured in `/etc/apt/sources.list` and configuration files under `/etc/apt/sources.list.d/`.
*   **Red Hat/Rocky Systems:** Use the Red Hat Package Manager (`dnf` or `yum`) to manage `.rpm` software packages. Repository sources are configured in `.repo` files under `/etc/yum.repos.d/`.

### Source Code Compilation
Some software or custom versions are not available in public repositories. In these cases, administrators compile and install the software from source code. This involves downloading the source code, verifying its dependencies, compiling the code into binary files, and installing those binaries on the system.""",
        "commands": r"""### Command & Syntax Reference
* **Debian Package Management (APT)**
  * `apt update`: Update the local package index cache from remote repositories.
  * `apt install nginx`: Install a software package and its dependencies.
  * `apt remove nginx`: Remove a software package while preserving its configuration files.
  * `apt purge nginx`: Remove a package along with all its configuration files.
  * `dpkg -L nginx`: List all files installed on the system by a package.
  * `dpkg -S /etc/nginx/nginx.conf`: Identify which package installed a specific file.

* **RHEL Package Management (DNF)**
  * `dnf check-update`: Check for available package updates.
  * `dnf install nginx`: Install a package and its dependencies.
  * `dnf remove nginx`: Remove a software package from the system.
  * `rpm -ql nginx`: List all files installed on the system by a package.
  * `rpm -qf /etc/nginx/nginx.conf`: Identify which package installed a specific file.

* **Source Compilation Pipeline**
  * `./configure`: Check system dependencies and generate a compilation Makefile.
  * `make`: Compile the source code into executable binary files.
  * `make install`: Copy the compiled binaries and files to their installation paths on the system.""",
        "examples": r"""### Real-World Examples

#### Example 1: Resolving missing package configurations
**Situation:** An application configuration file `/etc/nginx/nginx.conf` has been corrupted. You need to identify which package installed this file and reinstall it to restore the default configuration.
**Action:** Identify the package using `dpkg` or `rpm` and reinstall it.
```bash
# On Debian/Ubuntu:
dpkg -S /etc/nginx/nginx.conf
apt install --reinstall nginx -y

# On RHEL/Rocky:
rpm -qf /etc/nginx/nginx.conf
dnf reinstall nginx -y
```

#### Example 2: Adding third-party repositories
**Situation:** You need to install the latest version of Nginx from its official repository on a Rocky Linux system.
**Action:** Create a custom `.repo` file under `/etc/yum.repos.d/` to configure the official repository.
```bash
# Create and configure the repository file:
cat << 'EOF' > /etc/yum.repos.d/nginx.repo
[nginx-stable]
name=nginx stable repo
baseurl=http://nginx.org/packages/centos/$releasever/$basearch/
gpgcheck=1
enabled=1
gpgkey=https://nginx.org/keys/nginx_signing.key
EOF

# Update repository lists and install the package:
dnf clean all
dnf install nginx -y
```

#### Example 3: Compiling development utilities from source
**Situation:** You need to install a utility `tree` from source code on a headless server that does not have internet access.
**Action:** Extract, compile, and install the package from its source tarball.
```bash
tar -xzvf tree-2.0.0.tgz
cd tree-2.0.0
./configure --prefix=/usr/local
make
sudo make install
```

#### Example 4: Auditing installed files
**Situation:** You need to list and audit all files and directories installed by the `openssh-server` package to verify their file permissions.
**Action:** Query the package manager file registry.
```bash
# On Debian/Ubuntu:
dpkg -L openssh-server

# On RHEL/Rocky:
rpm -ql openssh-server
```

#### Example 5: Cleaning package manager caches
**Situation:** A failed package update left corrupt package headers in the local repository cache. You need to clear the cache and download fresh metadata.
**Action:** Clean and rebuild the package manager index files.
```bash
# On Debian/Ubuntu:
apt clean && apt update

# On RHEL/Rocky:
dnf clean all && dnf makecache
```""",
        "exercise": r"""### Hands-On Labs

#### Lab 1: Repository Management and Package Deployment
* **Objective:** Configure custom package repository sources and install software.
* **Tasks:**
  1. Locate the default repository configuration directories on your machine.
  2. Install a simple utility (such as `htop` or `curl`) using your distribution's package manager.
  3. Verify that the package has been installed successfully and run it.
  4. Query the package database to display the installed version details.

#### Lab 2: Reinstalling Corrupted Software Packages
* **Objective:** Recover from software corruption by reinstalling packages.
* **Tasks:**
  1. Locate the binary path of a utility (such as `/usr/bin/curl`) using the `which` command.
  2. Simulate corruption by manually deleting this binary file (run as root).
  3. Try to run the command and observe the error message.
  4. Use your package manager to reinstall the corrupted package.
  5. Verify that the command is restored and working.

#### Lab 3: Package Ownership and Metadata Auditing
* **Objective:** Query the package manager database to identify file owners.
* **Tasks:**
  1. Select a configuration file (such as `/etc/passwd` or `/etc/resolv.conf`) on your machine.
  2. Query your package manager database to check if this file is owned by an installed package.
  3. Query the `/etc/ssh/sshd_config` file to identify which package installed it.
  4. Save the package owner details to `/tmp/sshd_owner.txt`.

#### Lab 4: Purging System Software Configurations
* **Objective:** Completely remove software packages along with their configuration files.
* **Tasks:**
  1. Install a web server (such as `nginx` or `apache2`).
  2. Verify that the default configuration directories are created in `/etc`.
  3. Remove the package using your package manager's standard remove command. Verify if the configuration directory in `/etc` remains.
  4. Reinstall the package, and then remove it using the `purge` command (on Debian) or by manual configuration cleanup (on RHEL).
  5. Verify that the configuration files have been completely removed.

#### Lab 5: Source Code Compilations
* **Objective:** Compile and install a utility from source code.
* **Tasks:**
  1. Ensure that development build tools (such as `gcc`, `make`, or `build-essential` / `development-tools`) are installed.
  2. Download a source code tarball for a simple command-line tool.
  3. Extract the tarball and navigate to the source directory.
  4. Run `./configure`, followed by `make` to compile the source code.
  5. Run `make install` to install the compiled utility, and verify that it executes successfully on the system.""",
        "insight": r"""### Interview Q&A

#### Q1: What is the difference between apt remove and apt purge?
* **Answer:**
  * **`apt remove`:** Removes the package binaries and files from the system but preserves its custom configuration files in `/etc`. This is useful if you plan to reinstall the package later and keep your settings.
  * **`apt purge`:** Removes the package binaries along with all of its configuration files and directory structures, performing a clean uninstallation.

#### Q2: How do you identify which package installed a specific file on RHEL/Rocky systems?
* **Answer:** Run the `rpm -qf` command specifying the absolute path to the file:
```bash
rpm -qf /etc/ssh/sshd_config
```

#### Q3: Why is compiling software from source sometimes preferred over repository installations?
* **Answer:** Compiling from source allows you to install custom software versions or feature patches that are not available in public package repositories. It also allows you to configure custom installation paths, optimize the software for specific hardware architectures, and enable or disable specific features during compilation.

#### Q4: How do you find all packages that have pending security updates on RHEL/Rocky?
* **Answer:** Use `dnf` with the `--security` and `check-update` parameters:
```bash
dnf --security check-update
```

#### Q5: What is the purpose of the baseurl parameter in repository configuration files?
* **Answer:** The `baseurl` parameter defines the HTTP, HTTPS, or FTP network address of the package repository. This is the location where the package manager connects to download repository metadata and software package files (`.rpm` or `.deb`).

### LFCS Exam Focus
*   **Know file package owners:** Be prepared to identify which package owns a specific configuration file, and know how to reinstall or restore default configuration files if they are corrupted or deleted. Practice using `dpkg -S` and `rpm -qf` configurations."""
    },
    {
        "id": 12,
        "title": "Module 12: Virtualization (KVM/libvirt) and Container Engineering (Docker/Podman)",
        "theory": r"""### Operating System Virtualization
Virtualization allows you to run multiple isolated operating systems (Virtual Machines or VMs) on a single physical host. In Linux, this is achieved using Kernel-based Virtual Machine (KVM) technology combined with the QEMU emulator. The `libvirt` daemon manages VM lifecycles, and administrators interface with it using the `virsh` command-line utility.

### Containerization Foundations
Containerization provides process-level isolation, allowing applications to run in isolated user spaces (containers) on a shared host kernel. Containers are lightweight and start faster than virtual machines because they do not run their own guest operating systems. Common container engines include Docker and Podman.

### Docker vs. Podman
*   **Docker:** Uses a centralized system daemon (`dockerd`) running with root privileges to manage all containers.
*   **Podman:** A daemonless container engine that runs containers as standard user processes without requiring root privileges (rootless containers), improving system security.""",
        "commands": r"""### Command & Syntax Reference
* **Virtual Machine Management (virsh)**
  * `virsh list --all`: List all configured virtual machines and their current states.
  * `virsh start db_vm`: Start a virtual machine.
  * `virsh shutdown db_vm`: Gracefully shut down a virtual machine.
  * `virsh destroy db_vm`: Force-stop a virtual machine immediately.
  * `virsh autostart db_vm`: Configure a virtual machine to start automatically when the host boots.

* **Container Engine Management (Docker / Podman)**
  * `docker pull nginx:alpine`: Download a container image from a remote registry.
  * `docker images`: List all container images stored locally.
  * `docker run -d --name web_container -p 8080:80 nginx:alpine`: Start a container in detached mode, mapping host port 8080 to container port 80.
  * `docker ps`: List all running containers.
  * `docker ps -a`: List all containers, including stopped ones.
  * `docker logs web_container`: View the log outputs generated by a container.
  * `docker exec -it web_container /bin/sh`: Open an interactive terminal session inside a running container.
  * `docker stop web_container`: Stop a running container.
  * `docker rm web_container`: Delete a stopped container.
  * `docker rmi nginx:alpine`: Delete a local container image.""",
        "examples": r"""### Real-World Examples

#### Example 1: Creating persistent container environments
**Situation:** You need to deploy a PostgreSQL database container that maps a local directory `/opt/db_data` to `/var/lib/postgresql/data` inside the container to ensure database data persists if the container is deleted or updated.
**Action:** Use Docker's volume mounting options (`-v`) to mount the directory during container startup.
```bash
mkdir -p /opt/db_data
docker run -d --name postgres_db \
  -e POSTGRES_PASSWORD=securepass \
  -v /opt/db_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:alpine
```

#### Example 2: Accessing container command shells
**Situation:** You need to inspect the internal configuration file `/etc/nginx/nginx.conf` inside a running container named `web_proxy`.
**Action:** Use `docker exec` to start an interactive shell session inside the container.
```bash
docker exec -it web_proxy cat /etc/nginx/nginx.conf
```

#### Example 3: Enabling autostart for critical virtual machines
**Situation:** You need to configure an internal database virtual machine named `production_db_vm` to start automatically whenever the physical host system boots.
**Action:** Configure the virtual machine's autostart policy using `virsh`.
```bash
virsh autostart production_db_vm
```

#### Example 4: Auditing container resource utilization
**Situation:** A containerized application is running slowly. You need to inspect the active CPU, memory, and network resources consumed by all running containers.
**Action:** Query container utilization statistics using `docker stats`.
```bash
docker stats --no-stream
```

#### Example 5: Troubleshooting virtual machine startup failures
**Situation:** A virtual machine named `app_server` fails to start. You need to inspect its console logs to identify the issue.
**Action:** Query the virtual machine's console logs using the `virsh` utility.
```bash
virsh console app_server
```""",
        "exercise": r"""### Hands-On Labs

#### Lab 1: Virtual Machine Lifecycle Controls
* **Objective:** Manage virtual machine states using virsh.
* **Tasks:**
  1. Verify if the virtualization daemon is active using `systemctl status libvirtd` or `systemctl status virtqemud`.
  2. List all configured virtual machines on your host.
  3. Start a test virtual machine, and verify its active state using `virsh list`.
  4. Configure the virtual machine to start automatically when the host boots.
  5. Gracefully shut down the virtual machine.

#### Lab 2: Container Base Deployments
* **Objective:** Pull images and run containers.
* **Tasks:**
  1. Verify if your container engine (Docker or Podman) is running on your host.
  2. Search and pull the official lightweight Alpine Linux image from the container registry.
  3. List your locally stored container images.
  4. Run an interactive container using the Alpine image: `docker run -it --name test_alpine alpine /bin/sh`.
  5. Run a command inside the container (such as `uname -a`), exit the container session, and verify that the container has stopped.

#### Lab 3: Port Forwarding and Web Container Access
* **Objective:** Run a web server container and map network ports.
* **Tasks:**
  1. Start an Nginx web server container in detached (background) mode named `web_portal`.
  2. Configure the container to map host port `8080` to container port `80`.
  3. Verify that the container is running and check its logs using `docker logs`.
  4. Access the web server from your host machine using `curl http://localhost:8080` to confirm it is serving traffic.
  5. Stop and delete the container.

#### Lab 4: Container Directory Binding
* **Objective:** Map host directories to containers to persist data.
* **Tasks:**
  1. Create a local directory `/tmp/web_files/` and create an `index.html` file inside it containing "Custom Mount Test".
  2. Start an Nginx container named `portal_mount`.
  3. Map your local directory `/tmp/web_files/` to `/usr/share/nginx/html/` inside the container during startup.
  4. Access the web server using `curl http://localhost` (or its mapped port) and verify that it serves your custom `index.html` file.
  5. Delete the container and verify that your local `/tmp/web_files/index.html` file remains on the host.

#### Lab 5: Troubleshooting Container Failures
* **Objective:** Analyze container logs to diagnose startup issues.
* **Tasks:**
  1. Try to start a container using invalid configuration options (such as mapping a port that is already in use).
  2. Identify the failed container using the `docker ps -a` command.
  3. Inspect the container's logs to identify the error message.
  4. Fix the configuration issue and restart the container successfully.
  5. Clean up your environment by deleting all stopped containers.""",
        "insight": r"""### Interview Q&A

#### Q1: What is the main architectural difference between virtual machines (KVM) and containers (Docker/Podman)?
* **Answer:**
  * **Virtual Machines (KVM):** Run a complete guest operating system on top of virtualized hardware provided by a hypervisor. This provides complete isolation, but consumes more system resources and takes longer to start.
  * **Containers:** Share the host operating system's kernel, isolating applications at the process level using kernel namespaces and cgroups. This makes containers lightweight, fast to start, and highly resource-efficient.

#### Q2: What is the purpose of volume mapping (-v) in container deployments?
* **Answer:** By default, containers are ephemeral and store data in temporary read-write layers. If a container is deleted or updated, any data stored in this temporary layer is lost. Volume mapping mounts a directory from the host filesystem directly inside the container, ensuring that application data (such as database files) persists on the host.

#### Q3: Why is running containers with Podman considered more secure than using Docker?
* **Answer:** Docker uses a centralized daemon that runs with root privileges. If a container is compromised, an attacker could exploit the daemon to gain root access to the host. Podman does not use a centralized daemon and supports "rootless" containers. This allows users to start and manage containers inside their own user namespaces without requiring root privileges, protecting the host system.

#### Q4: How do you configure a virtual machine to start automatically when the KVM host boots?
* **Answer:** Use the `virsh autostart` command followed by the virtual machine name. This creates a symlink to the VM's XML configuration file inside the autostart directory, telling the libvirt daemon to start the VM during host startup:
```bash
virsh autostart vm_name
```

#### Q5: How do you execute a command inside a running container without opening an interactive shell session?
* **Answer:** Use the `docker exec` (or `podman exec`) command followed by the container name and the command you want to run:
```bash
docker exec web_server nginx -t
```

### LFCS Exam Focus
*   **Understand container basics:** You may be asked to start containers, map ports, mount volumes, and query logs. Practice these operations using both Docker and Podman commands to be comfortable with either container engine on the exam."""
    },
    {
        "id": 13,
        "title": "Module 13: Network Stack Foundations, DNS Resolution, and Time Sync",
        "theory": r"""### Operating System Networking
Linux networking is managed directly by the kernel, allowing interfaces to route packets across local networks and external gateways. Modern distributions configure and manage networking interfaces using the NetworkManager service, which administrators control using the `nmcli` command-line tool or the `nmtui` interactive console interface.

### Hostname Resolution & DNS
When a system connects to a domain name, it translates the name to an IP address using hostname resolution. This process is governed by the following configuration files:
*   **`/etc/hosts`:** A local database that maps hostnames to IP addresses. It is queried first by default.
*   **`/etc/resolv.conf`:** Configures the IP addresses of external Domain Name System (DNS) servers used to resolve remote domain queries.

### Network Time Synchronization (NTP)
Accurate system time is critical for system logging, security protocols, and network authentication. Linux systems synchronize their system clocks with external network time servers (NTP) using the `chronyd` service. Administrators manage timezone and system clock parameters using the `timedatectl` utility.""",
        "commands": r"""### Command & Syntax Reference
* **IP Configuration and Diagnostics**
  * `ip addr show`: Display all configured network interfaces and their IP addresses.
  * `ip link set eth0 up`: Activate a network interface.
  * `ip route show`: Display the active system routing table.
  * `ping -c 4 google.com`: Send ICMP packets to test network connectivity.
  * `ss -tulpn`: List all active, listening TCP and UDP sockets with their process names and PIDs.

* **NetworkManager Control (nmcli)**
  * `nmcli device status`: List physical network interface states.
  * `nmcli connection show`: Display all configured network connections.
  * `nmcli connection modify eth0 ipv4.addresses "192.168.1.15/24" ipv4.gateway "192.168.1.1"`: Set a static IP address and gateway.
  * `nmcli connection modify eth0 ipv4.dns "1.1.1.1,8.8.8.8"`: Configure DNS servers.
  * `nmcli connection modify eth0 ipv4.method manual`: Switch interface configuration from DHCP to static.
  * `nmcli connection up eth0`: Apply connection changes and activate the interface.

* **System Clock and Time Synchronization**
  * `timedatectl`: Display active timezone, system time, and clock synchronization status.
  * `timedatectl list-timezones`: List all supported system timezones.
  * `timedatectl set-timezone Europe/Amsterdam`: Change the system timezone.
  * `chronyc sources -v`: Display active NTP synchronization sources and details.""",
        "examples": r"""### Real-World Examples

#### Example 1: Configuring static IP addresses using nmcli
**Situation:** You need to configure a static IP address (`192.168.50.20/24`), gateway (`192.168.50.1`), and DNS server (`8.8.8.8`) on a system network interface named `eth1`.
**Action:** Configure the network interface settings using `nmcli`.
```bash
nmcli connection modify eth1 ipv4.addresses "192.168.50.20/24"
nmcli connection modify eth1 ipv4.gateway "192.168.50.1"
nmcli connection modify eth1 ipv4.dns "8.8.8.8"
nmcli connection modify eth1 ipv4.method manual
nmcli connection up eth1
```

#### Example 2: Verifying network socket listeners
**Situation:** A web server fails to start, throwing "address already in use" errors. You need to identify which process is already listening on port 80.
**Action:** Identify the listening process using the `ss` utility.
```bash
ss -tulpn | grep :80
```

#### Example 3: Changing system timezones
**Situation:** A server is deployed in a new data center. You need to update its timezone to `UTC` to align with your centralized logging system.
**Action:** Update the system timezone using `timedatectl`.
```bash
timedatectl set-timezone UTC
timedatectl status
```

#### Example 4: Mapping local hosts for internal testing
**Situation:** You are testing an application server locally and need the domain `api.local` to resolve directly to your local IP address `127.0.0.1`.
**Action:** Add a local hostname mapping entry to `/etc/hosts`.
```bash
echo "127.0.0.1 api.local" >> /etc/hosts
ping -c 2 api.local
```

#### Example 5: Verifying NTP synchronization status
**Situation:** A database server is throwing transaction synchronization errors. You need to verify if the system clock is synchronized with external time servers.
**Action:** Verify the NTP synchronization status using `chronyc`.
```bash
chronyc sources -v
```""",
        "exercise": r"""### Hands-On Labs

#### Lab 1: Configuring Static Networking Properties
* **Objective:** Configure a static IP network interface manually.
* **Tasks:**
  1. List your system's active network connections.
  2. Select an interface and configure it with a static IP address (`172.16.5.10/24`), gateway (`172.16.5.1`), and DNS server (`1.1.1.1`).
  3. Apply your changes and bring up the network interface.
  4. Verify the updated network configurations using the `ip addr show` command.

#### Lab 2: Local Hostname Mapping
* **Objective:** Map hostnames locally using the hosts file.
* **Tasks:**
  1. Open a web browser or use `curl` to access a non-existent domain (such as `test.platform.local`). Observe the network error.
  2. Edit `/etc/hosts` and map `test.platform.local` to point directly to localhost (`127.0.0.1`).
  3. Run `ping test.platform.local` and verify that the system routes traffic to your local loopback address.
  4. Clean up the entry from `/etc/hosts` when finished.

#### Lab 3: System Timezone Auditing and Sync Configuration
* **Objective:** Configure system timezones and time synchronization.
* **Tasks:**
  1. Display your system's active timezone, time, and NTP synchronization status.
  2. List the available timezones on your machine.
  3. Change your system timezone to `Asia/Tokyo`.
  4. Verify the updated system time and timezone.
  5. Restore your original system timezone.

#### Lab 4: Verifying Listening Network Ports
* **Objective:** Identify services listening on network ports.
* **Tasks:**
  1. Install and start a network utility (such as `apache2` or `nginx`).
  2. Run `ss` with flags to display all listening sockets.
  3. Locate your web server process and identify the port it is listening on.
  4. Stop the web server and run `ss` again to confirm that the port is no longer listening.

#### Lab 5: Troubleshooting Domain Resolution Failures
* **Objective:** Configure external DNS resolution servers.
* **Tasks:**
  1. Inspect the contents of your `/etc/resolv.conf` file to verify your active DNS configurations.
  2. Temporarily comment out your active DNS nameserver entries.
  3. Try to ping a public domain (such as `google.com`) and observe the host resolution error.
  4. Restore your DNS nameserver entries in `/etc/resolv.conf`.
  5. Verify that domain resolution and connectivity are restored.""",
        "insight": r"""### Interview Q&A

#### Q1: What is the purpose of the Name Service Switch file (/etc/nsswitch.conf)?
* **Answer:** The `/etc/nsswitch.conf` file defines the search order used by the system when resolving hostname, user, group, and network details. For example, a setting like `hosts: files dns` tells the system to look up hostnames in local files (like `/etc/hosts`) first. If the hostname is not found, the system queries external DNS servers configured in `/etc/resolv.conf`.

#### Q2: What is the difference between system clock and hardware clock in Linux?
* **Answer:**
  * **System Clock:** Managed directly by the Linux kernel. It tracks system time while the operating system is running.
  * **Hardware Clock (RTC):** A battery-powered clock on the system motherboard. It tracks time when the system is powered off. During system boot, the kernel reads the hardware clock to set the initial system time.

#### Q3: Why is timedatectl preferred over the traditional date command for updating system time?
* **Answer:** The traditional `date` command only updates the system clock temporarily, and does not synchronize with hardware clocks or coordinate with background time-synchronization services. The `timedatectl` utility updates the system clock, coordinates with NTP services (like `chronyd`), adjusts hardware clocks, and manages timezone symbolic links securely.

#### Q4: How do you check if your server's system clock is synchronized with external time servers?
* **Answer:** Run `timedatectl status` and look for the "System clock synchronized: yes" line. You can also run `chronyc tracking` or `chronyc sources -v` to display detailed synchronization metrics:
```bash
chronyc tracking
```

#### Q5: What is the difference between active-backup mode and LACP (802.3ad) mode in network interface bonding?
* **Answer:**
  * **Active-backup:** Only one physical interface in the bond is active at a time. The secondary interface remains inactive and takes over only if the primary physical link fails. This mode requires no special configuration on the network switch.
  * **LACP (802.3ad):** Aggregates multiple physical interfaces into a single high-bandwidth logical link, balancing traffic across all active interfaces. This mode requires hardware support and configuration on the connected network switch.

### LFCS Exam Focus
*   **Persistent network modifications are key:** When updating IP configurations or DNS servers on the exam, always use `nmcli` or modify the connection configuration files under `/etc/NetworkManager/system-connections/` directly. Manual updates to `/etc/resolv.conf` or using `ip addr` commands will be wiped out when systems are rebooted during grading."""
    },
    {
        "id": 14,
        "title": "Module 14: Firewalling, Port Forwarding, NAT, and Reverse Proxies",
        "theory": r"""### Network Traffic Filtering
Linux handles network security, packet filtering, and translation using its built-in Netfilter framework. Administrators configure and manage firewall rules using easy-to-use frontends:
*   **Uncomplicated Firewall (UFW):** The default firewall tool on Debian and Ubuntu systems.
*   **Firewalld:** A zone-based firewall daemon used on Red Hat and Rocky Linux systems.

### Port Forwarding and NAT
*   **Network Address Translation (NAT):** Translates IP addresses inside packet headers as they traverse networks. A common type of NAT is **Masquerading**, which allows multiple systems on a private network behind a firewall to communicate with external networks using the host's public IP address.
*   **Port Forwarding:** Intercepts traffic sent to a specific port on a firewall and redirects it to a different port or host inside a private network.

### Nginx HTTP Reverse Proxies
A reverse proxy receives incoming network connections (typically HTTP/HTTPS on ports 80 and 443) and forwards those requests to backend application servers (such as Node.js, Python, or Java applications) running on internal private networks, improving system security, performance, and scalability.""",
        "commands": r"""### Command & Syntax Reference
* **UFW Firewall Control (Debian/Ubuntu)**
  * `ufw enable`: Enable the UFW firewall.
  * `ufw allow 80/tcp`: Open incoming TCP port 80.
  * `ufw allow from 192.168.1.0/24 to any port 22`: Restrict SSH access to a specific subnet.
  * `ufw delete allow 80/tcp`: Delete a firewall rule.
  * `ufw status verbose`: Display detailed firewall status and rules.

* **Firewalld Control (RHEL/Rocky)**
  * `firewall-cmd --state`: Display the active firewalld state.
  * `firewall-cmd --get-active-zones`: Display active network zones.
  * `firewall-cmd --permanent --zone=public --add-port=443/tcp`: Open TCP port 443.
  * `firewall-cmd --permanent --zone=public --add-service=http`: Open the HTTP service.
  * `firewall-cmd --permanent --zone=public --add-masquerade`: Enable IP masquerading.
  * `firewall-cmd --permanent --add-forward-port=port=80:proto=tcp:toport=8080:toaddr=10.0.0.10`: Configure port forwarding.
  * `firewall-cmd --reload`: Reload firewall configurations to apply changes persistently.

* **Nginx Reverse Proxy Configurations**
  * `nginx -t`: Test the syntax of your Nginx configuration files.
  * `systemctl restart nginx`: Restart the Nginx service to apply configurations.""",
        "examples": r"""### Real-World Examples

#### Example 1: Securing SSH access using UFW
**Situation:** You need to enable the UFW firewall, block all incoming traffic by default, and allow SSH connections only from the secure subnet `10.0.5.0/24`.
**Action:** Configure default firewall policies and define custom rules using UFW.
```bash
# Set default traffic policies:
ufw default deny incoming
ufw default allow outgoing

# Configure secure SSH rule:
ufw allow from 10.0.5.0/24 to any port 22 proto tcp

# Enable the firewall:
ufw enable
ufw status verbose
```

#### Example 2: Configuring port forwarding in firewalld
**Situation:** You need to configure a Rocky Linux firewall to forward incoming traffic on port `80` to an internal application server running on port `8080` at IP `192.168.1.100`.
**Action:** Configure the port forwarding and masquerading rules in `firewalld`.
```bash
# Enable IP masquerading (required for forwarding to other hosts)
firewall-cmd --permanent --add-masquerade

# Configure the port forwarding rule:
firewall-cmd --permanent --add-forward-port=port=80:proto=tcp:toport=8080:toaddr=192.168.1.100

# Reload firewalld to apply changes:
firewall-cmd --reload
```

#### Example 3: Deploying an Nginx reverse proxy
**Situation:** You need to configure Nginx on a gateway server to forward public HTTP traffic on port 80 to a backend web application running locally on port `5000`.
**Action:** Create a custom Nginx configuration file in `/etc/nginx/conf.d/reverse_proxy.conf`.
```nginx
server {
    listen 80;
    server_name proxy.local;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```
```bash
# Verify the configuration syntax and restart the service
nginx -t
systemctl restart nginx
```

#### Example 4: Restricting public service access in firewalld
**Situation:** You need to configure `firewalld` to allow incoming web traffic (HTTP and HTTPS) from anywhere, but restrict database access (port 3306) to localhost.
**Action:** Configure services and ports in the public zone.
```bash
# Open public web services
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https

# Block public database access (ensure port 3306 is not open in public zone)
firewall-cmd --permanent --remove-port=3306/tcp

# Reload the configurations
firewall-cmd --reload
```

#### Example 5: Troubleshooting firewalld dropped packets
**Situation:** Active network services are failing to connect. You need to inspect the dropped packet log messages to identify which port is being blocked by the firewall.
**Action:** Enable logging for denied packets in firewalld.
```bash
# Enable denied packet logging:
firewall-cmd --set-log-denied=all

# Monitor dropped packet logs in real time:
journalctl -f | grep -i "filter"
```""",
        "exercise": r"""### Hands-On Labs

#### Lab 1: Hardening Access with UFW Firewall Rules
* **Objective:** Secure network services using UFW.
* **Tasks:**
  1. Ensure that `ufw` is installed on your Debian or Ubuntu host.
  2. Set default UFW policies to block incoming and allow outgoing traffic.
  3. Configure a rule to open port `80` and `443` for public access.
  4. Restrict SSH access (port 22) to a specific test subnet.
  5. Enable UFW and verify that your rules are active.

#### Lab 2: Managing Zones and Services in Firewalld
* **Objective:** Configure incoming traffic rules using firewalld.
* **Tasks:**
  1. Ensure `firewalld` is running on your host system.
  2. Identify the active zones and locate your primary network interface's zone.
  3. Permanently allow HTTP and HTTPS traffic in your active zone.
  4. Open a custom port `9090` (such as for Cockpit web console access).
  5. Reload the firewall and verify your updated configurations.

#### Lab 3: Port Forwarding inside a Host
* **Objective:** Redirect incoming port traffic.
* **Tasks:**
  1. Install a utility (such as `apache2` or `nginx`) to listen on port 80.
  2. Configure your firewall to redirect incoming traffic on port `8080` to port `80`.
  3. Verify that you can access the web server using port 8080 (`curl http://localhost:8080`).
  4. Ensure your changes are persistent across system reboots.

#### Lab 4: Configuring Nginx Reverse Proxy Links
* **Objective:** Configure Nginx to forward traffic to backend applications.
* **Tasks:**
  1. Install Nginx and start a backend application on port `5000` (e.g., using a simple Python server: `python3 -m http.server 5000`).
  2. Create an Nginx site configuration file to forward incoming port 80 traffic to your Python server on port 5000.
  3. Test your configuration file's syntax and restart Nginx.
  4. Access port 80 using `curl http://localhost/` and verify that Nginx serves content from your Python server.

#### Lab 5: Firewall Auditing and Rule Removal
* **Objective:** Audit and clean up active firewall rules.
* **Tasks:**
  1. List all active firewall rules on your system.
  2. Identify the rule opening port `9090` (from Lab 2).
  3. Delete the rule from the active and persistent configurations.
  4. Reload the firewall to apply the changes.
  5. Verify that port 9090 is no longer accessible.""",
        "insight": r"""### Interview Q&A

#### Q1: What is the difference between active and permanent rules in firewalld?
* **Answer:**
  * **Active (Runtime) Rules:** Rules applied immediately in system memory. These rules are active instantly, but are non-persistent and will be lost when the firewall service or system reboots.
  * **Permanent Rules:** Configurations written persistently to disk (`/etc/firewalld/`). These rules are not applied instantly in memory unless you reload the firewall using `firewall-cmd --reload`.

#### Q2: Why is IP masquerading required when configuring port forwarding to other network hosts?
* **Answer:** When a client sends a packet to a firewall, the firewall forwards the packet to an internal host. If masquerading is disabled, the internal host replies directly to the client using its private IP address. The client will reject this reply because it does not match the firewall's IP address. Enabling masquerading tells the firewall to translate the source IP of the packet, ensuring that replies are routed back through the firewall correctly.

#### Q3: How do you configure a firewall rule to open incoming traffic on port 80 in firewalld using services instead of port numbers?
* **Answer:** Use the `--add-service` parameter. Firewalld maps standard services to their default port configurations (defined in `/usr/lib/firewalld/services/`), simplifying configuration management:
```bash
firewall-cmd --permanent --add-service=http
```

#### Q4: What is the purpose of the proxy_set_header parameters in Nginx reverse proxy configurations?
* **Answer:** By default, when Nginx forwards requests to a backend server, the backend server sees Nginx as the client. It does not know the actual client's IP address, hostname, or connection protocol. The `proxy_set_header` parameters write the client's original details (such as `Host` and `X-Real-IP`) into the HTTP header, allowing the backend server to process them correctly.

#### Q5: How do you check if your firewall configuration has blocked a specific connection?
* **Answer:** Check your system logs. Enable denied packet logging in your firewall (e.g., `firewall-cmd --set-log-denied=all` in firewalld, or `ufw logging on` in UFW) and monitor system messages using `journalctl` or `/var/log/syslog` to verify which packets are being dropped.

### LFCS Exam Focus
*   **Always apply firewall changes persistently:** A common mistake is modifying firewalld rules without using the `--permanent` flag, or forgetting to run `firewall-cmd --reload` afterwards. If you make this mistake, your rules will be lost when graders reboot the systems during grading."""
    },
    {
        "id": 15,
        "title": "Module 15: Partitioning, Persistent Filesystems, Autofs, and Swap Space",
        "theory": r"""### Disk Partitioning and Formatting
For storage devices (such as hard drives or SSDs) to be usable by the operating system, they must be partitioned and formatted:
*   **Partitioning:** Divides a physical drive into isolated logical storage volumes using standard partition tables (such as MBR or GPT) and utilities (like `parted` or `fdisk`).
*   **Formatting:** Creates a filesystem structure (such as ext4 or XFS) on a partition, allowing the operating system to store and organize files.

### Persistent Filesystem Mounts
For filesystems to be accessible to users, they must be mounted to a directory point in the system hierarchy. Standard mounting is non-persistent and will not survive a system reboot. To make mounts persistent, write entries to `/etc/fstab` using unique block device identifiers (UUIDs) fetched via the `blkid` utility. Specifying incorrect mount options or syntax errors in `/etc/fstab` can cause the boot process to fail.

### On-Demand Mounts with Autofs
Systems with variable mount needs (such as dynamic network directories or external drives) use the `autofs` daemon. `autofs` automatically mounts remote shares or local drives when they are accessed, and unmounts them after a period of inactivity. This optimizes system resources.

### Virtual Memory Swap Space
When system RAM is exhausted, the kernel manages active memory by moving inactive memory pages to disk storage known as **Swap space**. Swap space can be configured on a dedicated drive partition or a swap file on an existing partition.""",
        "commands": r"""### Command & Syntax Reference
* **Partitioning and Formatting Tools**
  * `fdisk -l`: List all storage devices, partition tables, and configurations.
  * `parted /dev/sdb mklabel gpt`: Create a new GPT partition table on a drive.
  * `parted /dev/sdb mkpart primary xfs 1MiB 10GiB`: Create a primary 10GB XFS partition.
  * `mkfs.ext4 /dev/sdb1`: Format a partition with an ext4 filesystem.
  * `mkfs.xfs /dev/sdb1`: Format a partition with an XFS filesystem.

* **Mounting Operations**
  * `mount /dev/sdb1 /mnt`: Mount a partition to a directory point.
  * `umount /mnt`: Unmount a partition.
  * `blkid /dev/sdb1`: Display block device attributes (such as UUIDs).
  * `mount -a`: Mount all filesystems listed in `/etc/fstab`.

* **Swap Space Configurations**
  * `mkswap /dev/sdb2`: Initialize a block partition for Swap use.
  * `swapon /dev/sdb2`: Enable a Swap partition immediately.
  * `swapoff /dev/sdb2`: Disable a Swap partition.
  * `swapon --show`: List all active Swap devices and utilization metrics.

* **Autofs Service Management**
  * `systemctl start autofs`: Start the autofs daemon.""",
        "examples": r"""### Real-World Examples

#### Example 1: Creating persistent mounts with UUIDs
**Situation:** You need to configure a newly formatted XFS partition `/dev/sdb1` to mount persistently on `/mnt/data` with standard read/write mount options.
**Action:** Retrieve the partition's UUID using `blkid`, configure the mount directory, and write the persistent entry to `/etc/fstab`.
```bash
# Get the device UUID:
blkid /dev/sdb1
# Output: /dev/sdb1: UUID="a23c4d56-78e9-0f1a-2b3c-4d5e6f7a8b9c" TYPE="xfs"

# Create the mount point:
mkdir -p /mnt/data

# Append the persistent mount configuration to /etc/fstab:
echo "UUID=a23c4d56-78e9-0f1a-2b3c-4d5e6f7a8b9c /mnt/data xfs defaults 0 2" >> /etc/fstab

# Test the mount entry:
mount -a
df -h /mnt/data
```

#### Example 2: Allocating swap files for memory preservation
**Situation:** A system is running low on memory. You need to create a persistent 4GB Swap file `/swapfile` to prevent out-of-memory crashes.
**Action:** Allocate disk space, format it as swap, enable it, and write it to `/etc/fstab` for persistence.
```bash
# Allocate 4GB of space using fallocate:
fallocate -l 4G /swapfile

# Secure file permissions (swap files must be root-only):
chmod 600 /swapfile

# Format the file as swap space:
mkswap /swapfile

# Enable the swap file:
swapon /swapfile

# Add the persistent entry to /etc/fstab:
echo "/swapfile none swap sw 0 0" >> /etc/fstab
```

#### Example 3: Configuring on-demand autofs mounts
**Situation:** You need to configure the system to automatically mount an NFS export `10.0.0.10:/exports/media` to `/net/media` whenever users access that path.
**Action:** Configure the `autofs` master and map files.
```ini
# Add the master mapping entry to /etc/auto.master:
/net /etc/auto.nfs --timeout=60
```
```ini
# Create the /etc/auto.nfs map file and add the mount configuration:
media -fstype=nfs,rw,soft,intr 10.0.0.10:/exports/media
```
```bash
# Start and enable autofs:
systemctl restart autofs
systemctl enable autofs

# Test the configuration:
ls /net/media
```

#### Example 4: Non-destructive partition verification
**Situation:** A filesystem is throwing read-only partition errors. You need to verify if the partition has filesystem errors without modifying or losing data.
**Action:** Run a non-destructive filesystem scan using the `fsck` utility.
```bash
# Unmount the partition before scanning:
umount /dev/sdb1

# Scan and check filesystem integrity:
fsck -n /dev/sdb1
```

#### Example 5: Troubleshooting persistent mount issues
**Situation:** You modified `/etc/fstab` and need to verify that your changes are correct and will not break the system during boot.
**Action:** Run the mount verification tool.
```bash
# Test mount configuration entries (re-mounts everything in fstab)
mount -a
```""",
        "exercise": r"""### Hands-On Labs

#### Lab 1: Hard Drive Partitioning and Formatting
* **Objective:** Partition and format a raw block device.
* **Tasks:**
  1. Add a secondary raw virtual disk (such as `/dev/sdb`) to your testing environment.
  2. Create a GPT partition table on the new drive using `parted`.
  3. Create a primary 5GB partition on the drive.
  4. Format the new partition with an XFS filesystem.
  5. Verify that the partition is created successfully and can be queried.

#### Lab 2: Persistent Partition Mounting
* **Objective:** Configure a filesystem to mount persistently on reboot.
* **Tasks:**
  1. Create a directory `/mnt/storage/` on your system.
  2. Retrieve the UUID of your newly formatted partition from Lab 1.
  3. Edit `/etc/fstab` to configure the partition to mount persistently on `/mnt/storage/`.
  4. Test your configuration by running `mount -a`.
  5. Verify that the filesystem partition is mounted successfully using `df -h`.

#### Lab 3: Swap Partition Configurations
* **Objective:** Create and activate a dedicated swap partition.
* **Tasks:**
  1. Create a secondary 2GB partition on `/dev/sdb`.
  2. Initialize the partition as a Linux swap area using the `mkswap` utility.
  3. Activate the swap space using `swapon`.
  4. Verify that the swap partition is active using `swapon --show`.
  5. Add a persistent configuration entry for the swap partition to `/etc/fstab`.

#### Lab 4: Auto-mounting Filesystems
* **Objective:** Configure autofs to handle on-demand mounts.
* **Tasks:**
  1. Install the `autofs` package on your host.
  2. Configure `/etc/auto.master` to monitor the `/mnt/auto` directory using mapping rules.
  3. Define a mapping rule to mount a local partition to `/mnt/auto/test_drive` when accessed.
  4. Start the autofs service.
  5. Access the target directory and verify that autofs mounts the partition automatically.

#### Lab 5: System Recovery and fstab Diagnostics
* **Objective:** Diagnose and recover from filesystem mount errors.
* **Tasks:**
  1. Open `/etc/fstab` and write an incorrect UUID entry to simulate a device failure.
  2. Run the mount test command: `mount -a`.
  3. Identify and explain the error logs generated in `/var/log/syslog` or the system journal.
  4. Correct the invalid entry in `/etc/fstab` and verify that the mount test executes cleanly.""",
        "insight": r"""### Interview Q&A

#### Q1: Why is it recommended to use UUIDs instead of block device names (like /dev/sdb1) in /etc/fstab?
* **Answer:** Block device names (such as `/dev/sdb1` or `/dev/sdc2`) are dynamically assigned by the kernel during the boot process. If storage drives are physically swapped, added, or reordered on controllers, their device names may change, leading to boot failures. A UUID (Universally Unique Identifier) is a unique string permanently written to the filesystem header during creation. It identifies the exact filesystem regardless of what controller port or device letter is assigned, ensuring reliable and persistent mounting.

#### Q2: What is the main benefit of using autofs instead of configuring mounts in /etc/fstab?
* **Answer:**
  * **`/etc/fstab`:** Mounts filesystems persistently during system boot. This can slow down boot times and consume system resources, especially if network-based filesystems (such as NFS) are unreachable.
  * **`autofs`:** Mounts filesystems dynamically only when they are accessed by a user or process, and unmounts them automatically after a period of inactivity. This optimizes system resources, improves boot times, and prevents system hangs if remote network storage is offline.

#### Q3: How do you check if a filesystem is currently mounted as read-only or read-write?
* **Answer:** Check your active mounts using `/proc/mounts` or by running the `mount` command with no arguments. Look for the `ro` (read-only) or `rw` (read-write) attributes inside the parenthesis matching your target mount point:
```bash
mount | grep /mnt/data
```

#### Q4: Why must filesystems be unmounted before running fsck scans?
* **Answer:** The `fsck` utility reads and modifies filesystem metadata directly. If you run a scan on an active, mounted filesystem, the kernel may write to the disk at the same time, leading to severe metadata mismatches and irreversible data corruption. Filesystems must always be unmounted before running `fsck` scans.

#### Q5: What is the difference between MBR and GPT partition tables?
* **Answer:**
  * **MBR (Master Boot Record):** An older standard. It is limited to a maximum disk size of 2TB, supports a maximum of 4 primary partitions, and stores partition data in a single boot sector.
  * **GPT (GUID Partition Table):** A modern standard. It supports disks larger than 2TB, supports up to 128 partitions, and stores partition table redundancy backups at the end of the disk to improve system reliability.

### LFCS Exam Focus
*   **Always verify fstab changes:** A single typo or invalid UUID in `/etc/fstab` can cause the VM to hang during the boot process. If your system fails to boot during grading, you will receive zero points for any configuration tasks on that VM. Always run `mount -a` to verify your changes before finishing the exam."""
    },
    {
        "id": 16,
        "title": "Module 16: Logical Volume Management (LVM) and Remote File Systems (NFS)",
        "theory": r"""### Logical Volume Manager (LVM) Architecture
The Logical Volume Manager (LVM) abstracts physical storage devices, allowing administrators to pool disks and dynamically resize partitions. The LVM structure is organized into three layers:
1. **Physical Volumes (PV):** Raw block storage devices initialized for LVM use.
2. **Volume Groups (VG):** Combined pools of Physical Volumes that form a single logical storage pool.
3. **Logical Volumes (LV):** Virtual partitions carved out of a Volume Group. These act as block devices where filesystems are created and mounted.
Administrators can dynamically extend Logical Volumes online without interrupting running services.

### NFS Remote Storage sharing
Network File System (NFS) allows servers to share folders and files securely over a network. NFS exports are configured in `/etc/exports` and managed using the `exportfs` utility. Client machines mount these shared remote directories over the network, allowing users to access remote files as if they were stored on local disks.""",
        "commands": r"""### Command & Syntax Reference
* **LVM Management Tools**
  * `pvcreate /dev/sdb1`: Initialize a raw disk partition as an LVM Physical Volume.
  * `pvs` / `pvdisplay`: Query physical volumes.
  * `vgcreate vg_data /dev/sdb1`: Create a Volume Group from a Physical Volume.
  * `vgextend vg_data /dev/sdc1`: Add a new Physical Volume to an existing Volume Group.
  * `lvcreate -L 20G -n lv_app vg_data`: Create a 20GB Logical Volume in a Volume Group.
  * `lvextend -r -L +10G /dev/vg_data/lv_app`: Extend a Logical Volume and resize its underlying filesystem online.

* **NFS Management Tools**
  * `exportfs -arv`: Re-export and apply changes made to `/etc/exports`.
  * `showmount -e 192.168.1.10`: List NFS shares exported by a remote server.
  * `mount -t nfs 192.168.1.10:/exports/media /mnt/nfs`: Mount a remote NFS share.""",
        "examples": r"""### Real-World Examples

#### Example 1: Dynamic LVM extension
**Situation:** An application storage volume `/dev/vg_data/lv_app` formatted with ext4 is running out of disk space. You need to extend the logical volume by 15GB.
**Action:** Use `lvextend` with the `-r` (resize filesystem) flag to extend both the logical volume and its filesystem online.
```bash
# Extend the logical volume and resize its filesystem in a single step:
lvextend -r -L +15G /dev/vg_data/lv_app

# Verify the updated filesystem size:
df -h /data
```

#### Example 2: Configuring NFS exports
**Situation:** You need to configure an NFS server to share the directory `/srv/exports` with systems on the `192.168.1.0/24` subnet. The client systems must have write access.
**Action:** Create the target folder, configure `/etc/exports`, and export the share.
```bash
# Create the directory and assign permissions:
mkdir -p /srv/exports
chmod -R 777 /srv/exports

# Append the export rule to /etc/exports:
echo "/srv/exports 192.168.1.0/24(rw,sync,no_root_squash)" >> /etc/exports

# Enable services and export the directory:
systemctl enable --now nfs-server
exportfs -arv
```

#### Example 3: Adding disks to Volume Groups
**Situation:** Your Volume Group `vg_data` has run out of space. You need to initialize a new raw partition `/dev/sdc1` and add it to the volume group.
**Action:** Initialize the new physical volume and extend the volume group.
```bash
pvcreate /dev/sdc1
vgextend vg_data /dev/sdc1
```

#### Example 4: Mounting NFS shares persistently
**Situation:** You need to configure a client machine to persistently mount a remote NFS export `192.168.1.10:/srv/exports` on `/mnt/nfs_files`.
**Action:** Create the mount directory and append the persistent entry to `/etc/fstab`.
```bash
# Create the local mount directory
mkdir -p /mnt/nfs_files

# Append the persistent mount entry to /etc/fstab
echo "192.168.1.10:/srv/exports /mnt/nfs_files nfs defaults,timeo=90,retrans=5,retry=5 0 0" >> /etc/fstab

# Test the mount configuration
mount -a
```

#### Example 5: Troubleshooting storage performance with iostat
**Situation:** A system is running slowly. You need to monitor active disk utilization and read/write speeds to identify if disk I/O is a bottleneck.
**Action:** Monitor storage I/O statistics using the `iostat` utility.
```bash
iostat -xz 1 5
```""",
        "exercise": r"""### Hands-On Labs

#### Lab 1: Building Logical Volume Structures
* **Objective:** Initialize LVM layers from raw partitions.
* **Tasks:**
  1. Add a raw virtual disk to your virtual machine or testing environment.
  2. Initialize the raw device as an LVM Physical Volume.
  3. Create a Volume Group named `vg_system` containing the Physical Volume.
  4. Create a 5GB Logical Volume named `lv_data` within `vg_system`.
  5. Format the new logical volume with an ext4 filesystem and mount it on `/data`.

#### Lab 2: Safe Live Filesystem Growth
* **Objective:** Expand LVM volumes and filesystems online without data loss.
* **Tasks:**
  1. Verify the active size and utilization of `/data` created in Lab 1.
  2. Extend the logical volume `/dev/vg_system/lv_data` by 3GB.
  3. Resize the underlying ext4 filesystem to consume the newly allocated space.
  4. Verify that the filesystem partition size has grown without data loss.

#### Lab 3: Scaling Volume Groups with Extra Drives
* **Objective:** Extend Volume Groups by adding extra physical disks.
* **Tasks:**
  1. Add a secondary raw virtual disk to your testing environment.
  2. Initialize the new disk as an LVM Physical Volume.
  3. Extend your existing Volume Group `vg_system` to include the new Physical Volume.
  4. Verify that the Volume Group's total size has increased using `vgs` or `vgdisplay`.

#### Lab 4: Setting up NFS Host Shares
* **Objective:** Export directories using NFS.
* **Tasks:**
  1. Ensure that NFS server packages are installed on your machine.
  2. Create a directory named `/srv/public/` on your host.
  3. Configure `/etc/exports` to share this directory with other hosts in your local subnet.
  4. Start and enable the NFS server service.
  5. Run `exportfs -arv` to apply the export configurations.

#### Lab 5: Setting up NFS Client Connections
* **Objective:** Mount a remote directory shared over NFS.
* **Tasks:**
  1. Install NFS client packages on your machine.
  2. Query a remote server's exported shares using the `showmount` utility.
  3. Create a local mount directory `/mnt/nfs_share`.
  4. Manually mount the remote NFS share to `/mnt/nfs_share`.
  5. Edit `/etc/fstab` to configure the NFS share to mount persistently on reboot.""",
        "insight": r"""### Interview Q&A

#### Q1: What is the main advantage of LVM over standard partition tables?
* **Answer:** LVM abstracts physical disks, allowing administrators to combine multiple drives into a single logical volume group. It supports dynamic partition resizing, online filesystem expansion, volume striping, and volume mirroring without requiring system reboots or service downtime.

#### Q2: What are the target steps required to expand an active LVM partition on Rocky Linux (XFS) systems?
* **Answer:**
  1. Extend the Logical Volume size using `lvextend`.
  2. Resize the underlying XFS filesystem online using the `xfs_growfs` command, specifying the filesystem mount point:
```bash
lvextend -L +10G /dev/vg_data/lv_app
xfs_growfs /data
```

#### Q3: What is the purpose of the no_root_squash option in NFS server configurations?
* **Answer:** By default, NFS uses "root squashing" to translate requests from root users on client systems to the unprivileged `nobody` user account on the server, preventing root access to NFS files. Setting the `no_root_squash` option disables this safety feature, allowing root users on client machines to read and write to the NFS share with full root privileges. This should be avoided in secure production environments.

#### Q4: Why is it recommended to use the -r option when extending an LVM Logical Volume?
* **Answer:** The `-r` (resize filesystem) option tells `lvextend` to automatically resize the underlying filesystem (such as ext4 or XFS) to match the new size of the logical volume in a single step, preventing configuration mismatches.

#### Q5: How do you identify the active list of exported directory shares on a remote NFS host?
* **Answer:** Use the `showmount` utility with the `-e` (exports) flag followed by the IP address of the remote NFS host:
```bash
showmount -e 192.168.1.10
```

### LFCS Exam Focus
*   **Know the difference between filesystem resizers:** Remember that `resize2fs` is used to resize ext4 filesystems, and `xfs_growfs` is used to resize XFS filesystems. Note that `xfs_growfs` takes the *mount directory* (e.g. `/mnt/data`) as its target parameter, whereas `resize2fs` takes the *block device path* (e.g. `/dev/vg/lv_data`). Practice both configurations."""
    },
    {
        "id": 17,
        "title": "Module 17: User/Group Management, Special Permissions, ACLs, and Central LDAP",
        "theory": r"""### Local Identity Management
Linux manages local users and groups using standard system databases. User accounts are defined in `/etc/passwd`, encrypted password hashes are stored in `/etc/shadow`, and local groups are defined in `/etc/group`. Administrators use user and group management utilities to provision accounts, assign shell environments, and configure security parameters.

### Special Permissions
Standard Linux file permissions follow the Discretionary Access Control (DAC) model, defining Read (r), Write (w), and Execute (x) permissions for Owner, Group, and Others. However, advanced scenarios require special permissions:
*   **SUID (Set User ID):** Executes binary files with the privileges of the file owner.
*   **SGID (Set Group ID):** Executes binary files with the privileges of the file's group. When set on a directory, files created inside it inherit the directory's group ownership rather than the creator's group.
*   **Sticky Bit:** Restricts file deletion within a directory. Users can only delete files that they own.

### Access Control Lists (ACLs)
For granular permission management beyond standard group structures, administrators use Access Control Lists (ACLs). This allows you to define permissions for specific users or groups without changing the primary owner of the file or directory.

### Centralized LDAP Configuration
Enterprise networks use centralized authentication services rather than managing local users on every machine. The Name Service Switch configuration file (`/etc/nsswitch.conf`) defines the databases used to look up system information (like users, groups, and hostnames). Systems integrate with centralized LDAP (Lightweight Directory Access Protocol) servers using SSSD (System Security Services Daemon), allowing centralized user management and unified logins.""",
        "commands": r"""### Command & Syntax Reference
* **User and Group Management**
  * `useradd -m -s /bin/bash sys_user`: Create a local user account with a home directory and a bash shell.
  * `usermod -aG wheel sys_user`: Add a user account to an additional administrative group.
  * `userdel -r sys_user`: Delete a user account along with their home directory and mail spool.
  * `groupadd engineering`: Create a new local user group.
  * `chage -m 7 -M 90 -I 7 sys_user`: Set password policies (minimum/maximum age and password inactivity period).

* **Standard and Special Permissions**
  * `chmod 4755 /usr/bin/binary`: Set SUID permissions (represented by the octal digit 4).
  * `chmod 2775 /shared/dir`: Set SGID permissions (represented by the octal digit 2).
  * `chmod +t /shared/tmp`: Set the Sticky Bit on a directory to prevent users from deleting files owned by others.
  * `chown -R admin_user:dev_group /data`: Change owner and group ownership of a directory and its files.

* **Access Control Lists (ACLs)**
  * `getfacl /data`: View active Access Control List permissions.
  * `setfacl -m u:app_dev:rwx /data`: Grant read, write, and execute permissions to a specific user.
  * `setfacl -m g:marketing:rx /data`: Grant read and execute permissions to a specific group.
  * `setfacl -x u:app_dev /data`: Remove access control rules for a specific user.
  * `setfacl -d -m g:engineering:rwx /data`: Configure default permissions inherited by files created in the directory.

* **User Privilege and Resource Control**
  * `visudo`: Open and edit `/etc/sudoers` securely to configure sudo privileges.
  * `ulimit -a`: List active system limits.

* **Centralized Authentication**
  * `authselect select sssd`: Configure sssd as the primary system authentication engine.""",
        "examples": r"""### Real-World Examples

#### Example 1: Password expiry management with chage
**Situation:** To meet security compliance standards, you need to configure the user account `sec_officer` to change their password every 90 days. The user must wait at least 7 days between password changes, receive an expiration warning 14 days before it expires, and have the account disabled if the password is not updated within 7 days after expiration.
**Action:** Configure the account aging settings using the `chage` utility.
```bash
# Configure password age and inactivity policies:
chage -m 7 -M 90 -W 14 -I 7 sec_officer

# Verify the updated account aging policies:
chage -l sec_officer
```

#### Example 2: Granting targeted ACL folder access
**Situation:** You need to give a specific user account (`web_auditor`) read and write access to the directory `/var/www/html/` without changing its existing user or group ownership.
**Action:** Configure targeted permissions on the directory using `setfacl`.
```bash
# Set write permission on the folder for the user:
setfacl -m u:web_auditor:rwx /var/www/html/

# Set the default permissions for any new files created in the folder:
setfacl -d -m u:web_auditor:rwx /var/www/html/

# Verify the ACL configuration:
getfacl /var/www/html/
```

#### Example 3: Hardening root access with custom sudoers
**Situation:** You need to configure a custom sudo rule that allows users in the `network_admins` group to run network service control commands (like starting or stopping services) without prompting them for a password.
**Action:** Use `visudo` to add a secure rule configuration to `/etc/sudoers`.
```bash
# Run visudo to safely edit the sudoers file:
# visudo
```
```sudoers
# Add the following configuration rule inside /etc/sudoers:
%network_admins ALL=(root) NOPASSWD: /usr/bin/systemctl restart network, /usr/bin/systemctl restart NetworkManager
```

#### Example 4: Establishing group environments via SGID
**Situation:** You need to configure a shared workspace directory `/shared/dev/` for members of the `developers` group. Files created in this directory must inherit the group ownership of `developers` automatically, regardless of who creates them.
**Action:** Create the directory, update its group ownership, and enable the SGID permission.
```bash
# Create the directory and assign group ownership:
mkdir -p /shared/dev/
chown -R root:developers /shared/dev/

# Configure standard permissions and enable SGID:
chmod 2770 /shared/dev/

# Verify the permissions (look for the "s" in the group execute position):
ls -ld /shared/dev/
# Output: drwxrws--- 2 root developers 4096 /shared/dev/
```

#### Example 5: Restricting user resource configurations via limits
**Situation:** You need to limit users in the `contractors` group to a maximum of 50 simultaneous system processes to prevent resource exhaustion.
**Action:** Configure the resource limits in `/etc/security/limits.conf`.
```ini
# Append the following configuration rule to /etc/security/limits.conf:
@contractors    hard    nproc    50
```""",
        "exercise": r"""### Hands-On Labs

#### Lab 1: User and Group Administration Basics
* **Objective:** Provision user accounts and configure group memberships.
* **Tasks:**
  1. Create a local system group named `ops_team`.
  2. Create a user account named `admin_user1` with their home directory and shell environment set to `/bin/bash`.
  3. Create a second user account named `admin_user2` using the same settings.
  4. Add both user accounts to the `ops_team` group as auxiliary members.
  5. Verify that both accounts are registered in the group using the `getent group` command.

#### Lab 2: Special Permissions Configurations (SUID/SGID/Sticky Bit)
* **Objective:** Configure SGID and Sticky Bit permissions on shared directories.
* **Tasks:**
  1. Create a directory named `/srv/collab/` and configure its group ownership to `ops_team`.
  2. Set permissions on `/srv/collab/` to allow only owner and group members full read, write, and execute access.
  3. Enable the SGID bit on `/srv/collab/`.
  4. Create a test file inside `/srv/collab/` as `admin_user1` and verify that its group ownership is automatically set to `ops_team`.
  5. Enable the Sticky Bit on `/srv/collab/` to prevent users from deleting files owned by others inside the directory.

#### Lab 3: Granular Privilege Delegations with Sudoers
* **Objective:** Configure administrative permissions.
* **Tasks:**
  1. Add a user account named `junior_admin` without adding them to administrative groups (like `wheel` or `sudo`).
  2. Use `visudo` to configure a rule that allows `junior_admin` to run the `/usr/bin/dnf` or `/usr/bin/apt-get` commands with root privileges.
  3. Configure the rule to prompt the user for their password before running the commands.
  4. Log in as `junior_admin` and test the sudo rule by running a package update command.

#### Lab 4: Granting Access Control Lists (ACLs)
* **Objective:** Configure advanced user permissions using ACLs.
* **Tasks:**
  1. Create a file `/tmp/report.txt` and set its permissions to `0600` (read-only by owner).
  2. Configure an ACL rule to allow a secondary user account read-only access to `/tmp/report.txt`.
  3. Verify the updated permissions using `getfacl`.
  4. Test that the secondary user can read the file, while other non-owner accounts cannot.

#### Lab 5: LDAP Identity Integrations
* **Objective:** Prepare a system to lookup user identities from an external database.
* **Tasks:**
  1. Install SSSD and LDAP utility packages (`sssd`, `sssd-ldap`, `ldap-utils`).
  2. Open and view the active database lookup order configurations in `/etc/nsswitch.conf`.
  3. Configure the database lookup order for user accounts and groups to query local files first, then check sssd: `passwd: files sssd` and `group: files sssd`.
  4. Configure SSSD to connect to a dummy LDAP server address (`ldap://ldap.example.com`) and specify the search base distinguished name (`dc=example,dc=com`) inside `/etc/sssd/sssd.conf`.
  5. Start the SSSD service and verify that it starts without syntax errors."""
    }
]