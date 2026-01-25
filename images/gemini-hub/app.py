import json
import subprocess
import socket
import os
import sys
import time
import threading
import signal
from flask import Flask, render_template_string

app = Flask(__name__)

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
    </style>
</head>
<body>
    <h1>Gemini Workspace Hub</h1>
    
    <div class="container">
        <!-- Filters -->
        <div class="filters">
            <input type="text" id="projectFilter" class="filter-input" placeholder="Search projects..." onkeyup="filterList()">
            <select id="typeFilter" class="filter-select" onchange="filterList()">
                <option value="all">All Types</option>
                <option value="geminicli">Gemini CLI</option>
                <option value="bash">Bash</option>
            </select>
            <label class="filter-checkbox">
                <input type="checkbox" id="offlineFilter" onchange="filterList()"> Show Offline
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
                <p>No active Gemini containers found.</p>
                <small>Run 'gemini-toolbox --remote ...' to start one.</small>
            </div>
        {% endif %}
        
        <button class="refresh-btn" onclick="window.location.reload();">Refresh List</button>
    </div>

    <script>
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

if __name__ == '__main__':
    # Start the monitor thread
    t = threading.Thread(target=auto_shutdown_monitor, daemon=True)
    t.start()
    
    # Listen on all interfaces so the host (and mapped ports) can reach it
    app.run(host='0.0.0.0', port=8888)
