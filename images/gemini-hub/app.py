import json
import subprocess
import socket
import os
import sys
import time
import threading
import signal
from flask import Flask, render_template_string, jsonify, request

app = Flask(__name__)

# --- Configuration ---
HUB_ROOTS = [r for r in os.environ.get("HUB_ROOTS", "").split(":") if r]
HOST_CONFIG_ROOT = os.environ.get("HOST_CONFIG_ROOT", "")
HOST_HOME = os.environ.get("HOST_HOME", "")

# HTML Template (Mobile First + Filtering)
TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gemini Hub</title>
    <style>
        :root {
            --bg-color: #121212;
            --card-bg: #1e1e1e;
            --text-main: #ffffff;
            --text-dim: #aaaaaa;
            --accent: #4caf50;
            --accent-hover: #45a049;
            --offline: #f44336;
            --input-bg: #333;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            margin: 0;
            padding: 20px;
        }
        h1 {
            text-align: center;
            font-size: 1.5rem;
            margin-bottom: 20px;
            color: var(--text-dim);
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        /* Filters */
        .filters {
            display: flex;
            gap: 10px;
            margin-bottom: 10px;
            flex-wrap: wrap;
            align-items: center;
        }
        .filter-input {
            flex: 1;
            background: var(--input-bg);
            border: none;
            padding: 12px;
            border-radius: 8px;
            color: white;
            font-size: 1rem;
        }
        .filter-select {
            background: var(--input-bg);
            border: none;
            padding: 12px;
            border-radius: 8px;
            color: white;
            font-size: 1rem;
            min-width: 100px;
        }
        .filter-checkbox {
            display: flex;
            align-items: center;
            gap: 5px;
            color: var(--text-dim);
            font-size: 0.9rem;
            cursor: pointer;
            padding: 0 5px;
        }
        
        .card {
            background-color: var(--card-bg);
            border-radius: 12px;
            padding: 20px;
            text-decoration: none;
            color: var(--text-main);
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: transform 0.1s, background-color 0.2s;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        .card:active {
            transform: scale(0.98);
            background-color: #2c2c2c;
        }
        .card.hidden {
            display: none;
        }
        .info {
            display: flex;
            flex-direction: column;
            gap: 4px;
        }
        .name {
            font-size: 1.1rem;
            font-weight: 600;
        }
        .meta {
            font-size: 0.85rem;
            color: var(--text-dim);
            display: flex;
            gap: 10px;
        }
        .badge {
            background: #333;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.75rem;
            text-transform: uppercase;
        }
        .status {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background-color: var(--accent);
            box-shadow: 0 0 8px var(--accent);
        }
        .status.offline {
            background-color: var(--offline);
            box-shadow: none;
        }
        .empty-state {
            text-align: center;
            color: var(--text-dim);
            padding: 40px;
            background: var(--card-bg);
            border-radius: 12px;
        }
        .refresh-btn {
            display: block;
            width: 100%;
            padding: 15px;
            margin-top: 20px;
            background-color: #333;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            cursor: pointer;
        }
        .action-btn {
            background-color: var(--accent);
            color: white;
            margin-bottom: 10px;
        }
        .action-btn:active {
            background-color: var(--accent-hover);
        }

        /* Wizard Overlay */
        .overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: var(--bg-color);
            z-index: 1000;
            padding: 20px;
            display: none;
            flex-direction: column;
            overflow-y: auto;
        }
        .overlay.active {
            display: flex;
        }
        .overlay-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .close-btn {
            background: none;
            border: none;
            color: var(--text-dim);
            font-size: 1.5rem;
            cursor: pointer;
        }
        
        .list-group {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .list-item {
            background: var(--card-bg);
            padding: 15px;
            border-radius: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
        }
        .list-item:active {
            background: #2c2c2c;
        }
        .breadcrumb {
            font-size: 0.8rem;
            color: var(--text-dim);
            margin-bottom: 15px;
            word-break: break-all;
        }
        
        .wizard-step {
            display: none;
        }
        .wizard-step.active {
            display: block;
        }
        
        .footer-actions {
            margin-top: auto;
            padding-top: 20px;
            display: flex;
            gap: 10px;
        }
        .btn-small {
            padding: 8px 12px;
            font-size: 0.85rem;
        }
        
        /* Loading Spinner */
        .loader {
            border: 3px solid #333;
            border-top: 3px solid var(--accent);
            border-radius: 50%;
            width: 20px;
            height: 20px;
            animation: spin 1s linear infinite;
            display: none;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <h1>Gemini Workspace Hub</h1>
    
    <div class="container">
        <button class="refresh-btn action-btn" onclick="openWizard()">+ New Session</button>

        <!-- Filters -->
        <div class="filters">
            <input type="text" id="projectFilter" class="filter-input" placeholder="Search sessions..." onkeyup="filterList()">
            <select id="typeFilter" class="filter-select" onchange="filterList()">
                <option value="all">All Types</option>
                <option value="geminicli">Gemini CLI</option>
                <option value="bash">Bash</option>
            </select>
            <label class="filter-checkbox">
                <input type="checkbox" id="offlineFilter" onchange="filterList()"> Offline
            </label>
        </div>

        {% if machines %}
            {% for m in machines %}
            <a href="http://{{ m.ip }}:3000" class="card {% if not m.online %}hidden{% endif %}" target="_blank" data-project="{{ m.project }}" data-type="{{ m.type }}" data-online="{{ 'true' if m.online else 'false' }}">
                <div class="info">
                    <span class="name">{{ m.project }}</span>
                    <div class="meta">
                        <span class="badge">{{ m.type }}</span>
                        <span class="ip">{{ m.ip }}</span>
                    </div>
                </div>
                <div class="status {% if not m.online %}offline{% endif %}"></div>
            </a>
            {% endfor %}
        {% else %}
            <div class="empty-state">
                <p>No active sessions found.</p>
                <small>Launch one below or from your desktop.</small>
            </div>
        {% endif %}
        
        <button class="refresh-btn" onclick="window.location.reload();">Refresh List</button>
    </div>

    <!-- Wizard Overlay -->
    <div id="wizard" class="overlay">
        <div class="overlay-header">
            <h2>Launch Session</h2>
            <button class="close-btn" onclick="closeWizard()">×</button>
        </div>

        <!-- Step 1: Select Root -->
        <div id="step-roots" class="wizard-step active">
            <p>Select a workspace root:</p>
            <div id="roots-list" class="list-group"></div>
        </div>

        <!-- Step 2: Browse -->
        <div id="step-browse" class="wizard-step">
            <div class="breadcrumb" id="current-path"></div>
            <div id="folder-list" class="list-group"></div>
            <div class="footer-actions">
                <button class="refresh-btn btn-small" onclick="goBackToRoots()">Change Root</button>
                <button class="refresh-btn action-btn btn-small" style="margin:0" onclick="goToConfig()">Use This Folder</button>
            </div>
        </div>

        <!-- Step 3: Config -->
        <div id="step-config" class="wizard-step">
            <p>Select Configuration:</p>
            <select id="config-select" class="filter-select" style="width:100%; margin-bottom:10px" onchange="loadConfigDetails()">
                <option value="">Default (Global)</option>
            </select>
            <div id="config-details" style="font-size: 0.8rem; color: var(--text-dim); margin-bottom: 20px; min-height: 1.2em;">
                <!-- Extra args info here -->
            </div>
            <div class="footer-actions">
                <button class="refresh-btn btn-small" onclick="goToBrowse()">Back</button>
                <button id="launch-btn" class="refresh-btn action-btn btn-small" style="margin:0" onclick="doLaunch()">
                    Launch Now
                </button>
                <div id="launch-loader" class="loader"></div>
            </div>
        </div>
    </div>

    <script>
        let currentPath = "";
        let selectedConfig = "";

        function filterList() {
            const search = document.getElementById('projectFilter').value.toLowerCase();
            const type = document.getElementById('typeFilter').value;
            const showOffline = document.getElementById('offlineFilter').checked;
            const cards = document.querySelectorAll('.card');
            
            cards.forEach(card => {
                const project = card.getAttribute('data-project').toLowerCase();
                const cardType = card.getAttribute('data-type');
                const isOnline = card.getAttribute('data-online') === 'true';
                
                const matchesSearch = project.includes(search);
                const matchesType = (type === 'all' || cardType === type);
                const matchesOnline = (showOffline || isOnline);
                
                if (matchesSearch && matchesType && matchesOnline) {
                    card.classList.remove('hidden');
                } else {
                    card.classList.add('hidden');
                }
            });
        }

        // --- Wizard Logic ---

        function openWizard() {
            document.getElementById('wizard').classList.add('active');
            fetchRoots();
        }

        function closeWizard() {
            document.getElementById('wizard').classList.remove('active');
        }

        async function fetchRoots() {
            const res = await fetch('/api/roots');
            const data = await res.json();
            const list = document.getElementById('roots-list');
            list.innerHTML = "";
            data.roots.forEach(root => {
                const div = document.createElement('div');
                div.className = 'list-item';
                div.innerHTML = `<span>${root}</span> <span>›</span>`;
                div.onclick = () => startBrowsing(root);
                list.appendChild(div);
            });
            showStep('step-roots');
        }

        function showStep(id) {
            document.querySelectorAll('.wizard-step').forEach(s => s.classList.remove('active'));
            document.getElementById(id).classList.add('active');
        }

        function startBrowsing(path) {
            currentPath = path;
            loadPath(path);
            showStep('step-browse');
        }

        async function loadPath(path) {
            currentPath = path;
            document.getElementById('current-path').innerText = path;
            const res = await fetch(`/api/browse?path=${encodeURIComponent(path)}`);
            const data = await res.json();
            
            const list = document.getElementById('folder-list');
            list.innerHTML = "";

            // Add Parent folder
            if (path.includes('/') && path.length > 1) {
                const up = document.createElement('div');
                up.className = 'list-item';
                up.style.opacity = "0.6";
                up.innerHTML = `<span>.. (Up)</span>`;
                up.onclick = () => {
                    const parts = path.split('/');
                    parts.pop();
                    loadPath(parts.join('/') || '/');
                };
                list.appendChild(up);
            }

            data.directories.forEach(dir => {
                const div = document.createElement('div');
                div.className = 'list-item';
                div.innerHTML = `<span>📁 ${dir}</span> <span>›</span>`;
                div.onclick = () => loadPath(path + (path.endsWith('/') ? '' : '/') + dir);
                list.appendChild(div);
            });
        }

        function goBackToRoots() { fetchRoots(); }
        function goToBrowse() { showStep('step-browse'); }

        async function goToConfig() {
            const res = await fetch('/api/configs');
            const data = await res.json();
            const select = document.getElementById('config-select');
            
            // Keep first option
            select.innerHTML = '<option value="">Default (Global)</option>';
            data.configs.forEach(c => {
                const opt = document.createElement('option');
                opt.value = c;
                opt.innerText = c;
                select.appendChild(opt);
            });
            document.getElementById('config-details').innerText = "";
            showStep('step-config');
        }

        async function loadConfigDetails() {
            const config = document.getElementById('config-select').value;
            const detailsDiv = document.getElementById('config-details');
            if (!config) {
                detailsDiv.innerText = "";
                return;
            }

            try {
                const res = await fetch(`/api/config-details?name=${encodeURIComponent(config)}`);
                const data = await res.json();
                if (data.extra_args && data.extra_args.length > 0) {
                    detailsDiv.innerText = "⚡ Custom arguments: " + data.extra_args.join(" ");
                } else {
                    detailsDiv.innerText = "Using default settings.";
                }
            } catch (e) {
                detailsDiv.innerText = "";
            }
        }

        async function doLaunch() {
            const btn = document.getElementById('launch-btn');
            const loader = document.getElementById('launch-loader');
            const config = document.getElementById('config-select').value;

            btn.style.display = "none";
            loader.style.display = "block";

            try {
                const res = await fetch('/api/launch', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        project_path: currentPath,
                        config_profile: config
                    })
                });
                const result = await res.json();
                
                if (result.status === 'success') {
                    alert("Session launched! Refreshing list...");
                    closeWizard();
                    setTimeout(() => window.location.reload(), 2000);
                } else {
                    alert("Error: " + result.error);
                    btn.style.display = "block";
                    loader.style.display = "none";
                }
            } catch (e) {
                alert("Launch failed: " + e);
                btn.style.display = "block";
                loader.style.display = "none";
            }
        }
    </script>
</body>
</html>
"""

def get_tailscale_status():
    """
    Executes `tailscale status --json`.
    Now running locally, so no socket path needed.
    """
    try:
        cmd = ["tailscale", "status", "--json"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error querying tailscale: {result.stderr}")
            return {}
            
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Exception: {e}")
        return {}

def parse_peers(status_json):
    """
    Extracts and filters relevant peers from the JSON.
    Looking for:
    1. Hostnames starting with 'gemini-'
    2. Has a valid IPv4 address
    """
    machines = []
    
    # Check 'Peer' (other machines)
    peers = status_json.get("Peer", {})
    
    # We iterate over all peers
    for _, node in peers.items():
        hostname = node.get("HostName", "")
        
        # FILTER: Only show "gem-" instances (standard prefix)
        # matches: gem-myproject-cli-a1b2
        if not hostname.startswith("gem-"):
            continue
            
        # Parse Hostname Metadata
        # Format: gem-{project}-{type}-{suffix}
        # We split and then filter out empty strings (squeezing)
        raw_parts = hostname.split('-')
        parts = [p for p in raw_parts if p]
        
        project = "Unknown"
        session_type = "Unknown"
        
        # We need at least 4 parts: gem, project, type, suffix
        if len(parts) >= 4:
            # Suffix is the last part
            # Type is the second to last part
            session_type = parts[-2]
            
            # Project is everything between 'gem' (index 0) and 'type' (index -2)
            project = "-".join(parts[1:-2])
            
        elif len(parts) == 3:
            # Legacy/Fallback: gem-project-suffix
            project = parts[1]
            session_type = "cli"
            
        # Get IPv4
        addrs = node.get("TailscaleIPs", [])
        ip = next((a for a in addrs if "." in a), None)
        
        if ip:
            machines.append({
                "name": hostname,
                "project": project,
                "type": session_type,
                "ip": ip,
                "online": node.get("Online", False)
            })
            
    # Sort by name
    machines.sort(key=lambda x: x["name"])
    return machines

def auto_shutdown_monitor():
    """
    Background thread that monitors active sessions.
    If no sessions are found for 60 seconds, it kills the process.
    """
    TIMEOUT_SECONDS = 60
    last_active = time.time()
    
    print(f">> Monitor started. Auto-shutdown after {TIMEOUT_SECONDS}s of inactivity.")
    
    while True:
        time.sleep(10)
        try:
            # Check for peers
            data = get_tailscale_status()
            machines = parse_peers(data)
            
            if machines:
                last_active = time.time()
            else:
                idle_time = time.time() - last_active
                if idle_time > TIMEOUT_SECONDS:
                    print(f">> Inactivity limit ({TIMEOUT_SECONDS}s) reached. Shutting down.")
                    # Kill self (Flask + Container)
                    os.kill(os.getpid(), signal.SIGTERM)
        except Exception as e:
            print(f"Monitor error: {e}")

@app.route('/')
def home():
    data = get_tailscale_status()
    machines = parse_peers(data)
    return render_template_string(TEMPLATE, machines=machines)

# --- Discovery & Browsing API ---

@app.route('/api/roots')
def get_roots():
    """Returns the list of allowed workspace roots."""
    return jsonify({"roots": HUB_ROOTS})

@app.route('/api/configs')
def get_configs():
    """Lists subdirectories in the HOST_CONFIG_ROOT."""
    configs = []
    if os.path.isdir(HOST_CONFIG_ROOT):
        configs = [d for d in os.listdir(HOST_CONFIG_ROOT) 
                   if os.path.isdir(os.path.join(HOST_CONFIG_ROOT, d))]
    configs.sort()
    return jsonify({"configs": configs})

@app.route('/api/config-details')
def get_config_details():
    """Returns details (like extra-args) for a specific config profile."""
    name = request.args.get('name', '')
    if not name:
        return jsonify({})
    
    profile_path = os.path.join(HOST_CONFIG_ROOT, name)
    
    # Logic matches gemini-toolbox:
    # If .gemini exists, extra-args is in profile_path.
    # If not, extra-args is also in profile_path (legacy/simple mode).
    # So we always look in profile_path.
    extra_args_path = os.path.join(profile_path, "extra-args")
    
    details = {"extra_args": []}
    if os.path.isfile(extra_args_path):
        try:
            with open(extra_args_path, 'r') as f:
                # Read non-empty lines that don't start with #
                args = []
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        args.append(line)
                details["extra_args"] = args
        except Exception as e:
            print(f"Error reading extra-args: {e}")
            
    return jsonify(details)

@app.route('/api/browse')
def browse():
    """Lists subdirectories of a given path, restricted to HUB_ROOTS."""
    path = request.args.get('path', '')
    
    if not path:
        return jsonify({"error": "Path required"}), 400
        
    # Security: Ensure path is within one of the HUB_ROOTS
    path = os.path.abspath(path)
    allowed = any(path.startswith(os.path.abspath(root)) for root in HUB_ROOTS)
    
    if not allowed:
        return jsonify({"error": "Access denied"}), 403
        
    if not os.path.isdir(path):
        return jsonify({"error": "Not a directory"}), 404
        
    try:
        # Only return directories
        items = []
        for item in os.listdir(path):
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path) and not item.startswith('.'):
                items.append(item)
        items.sort()
        return jsonify({"path": path, "directories": items})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/launch', methods=['POST'])
def launch():
    """Launches a new Gemini session using the toolbox script."""
    data = request.json or {}
    project_path = data.get('project_path')
    config_profile = data.get('config_profile')
    
    if not project_path:
        return jsonify({"error": "Project path required"}), 400
        
    # Security: Ensure path is within allowed roots
    project_path = os.path.abspath(project_path)
    allowed = any(project_path.startswith(os.path.abspath(root)) for root in HUB_ROOTS)
    
    if not allowed:
        return jsonify({"error": "Access denied"}), 403
        
    if not os.path.isdir(project_path):
        return jsonify({"error": "Project directory not found"}), 404

    # Resolve config path
    config_args = []
    if config_profile:
        profile_path = os.path.join(HOST_CONFIG_ROOT, config_profile)
        # The Hub always uses Profile Mode (nested .gemini) for its managed profiles
        config_args = ["--profile", profile_path]

    try:
        # Prepare Environment
        # We MUST set HOME to HOST_HOME so the script resolves host paths correctly
        env = os.environ.copy()
        if HOST_HOME:
            env["HOME"] = HOST_HOME
            
        # Execute Launcher
        # We use --detached to ensure the script returns immediately
        # AUTH_KEY is already in os.environ from entrypoint
        cmd = ["gemini-toolbox", "--remote", env.get("TAILSCALE_AUTH_KEY", ""), "--detached"] + config_args
        
        print(f">> Executing: {' '.join(cmd)} in {project_path}")
        
        # We run it in the background from Python's perspective too, 
        # though --detached makes the bash script return fast.
        result = subprocess.run(cmd, cwd=project_path, env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            return jsonify({
                "status": "success",
                "output": result.stdout
            })
        else:
            return jsonify({
                "status": "error",
                "error": result.stderr or result.stdout
            }), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Start the monitor thread
    t = threading.Thread(target=auto_shutdown_monitor, daemon=True)
    t.start()
    
    # Listen on all interfaces so the host (and mapped ports) can reach it
    app.run(host='0.0.0.0', port=8888)
