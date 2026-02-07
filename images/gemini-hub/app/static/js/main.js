let currentPath = "";
let selectedConfig = "";

document.addEventListener("DOMContentLoaded", () => {
    checkConnectivity();
});

async function checkConnectivity() {
    const cards = document.querySelectorAll('.card');
    
    for (const card of cards) {
        const localBadge = card.querySelector('.local-badge');
        const mainLink = card.querySelector('.card-main-link');
        
        if (!localBadge) continue; // Offline or no local port
        
        const localUrl = localBadge.getAttribute('data-local-url');
        const vpnUrl = mainLink.href; // Original VPN URL from template
        
        // 1. Probe Localhost
        let localReachable = false;
        if (localUrl && ['localhost', '127.0.0.1'].includes(window.location.hostname)) {
            localReachable = await probeUrl(localUrl);
        }

        // 2. Probe VPN
        const vpnReachable = await probeUrl(vpnUrl);

        // 3. Apply Logic
        if (localReachable) {
            // Priority: Localhost
            mainLink.href = localUrl;
            
            if (vpnReachable) {
                // If VPN also works, show it as a badge
                localBadge.href = vpnUrl;
                localBadge.innerText = "VPN";
                localBadge.classList.remove('hidden');
                localBadge.title = "Connect via Tailscale IP";
            } else {
                // VPN unreachable? Hide badge.
                localBadge.classList.add('hidden');
            }
        } else {
            // Local unreachable (or remote client)
            // Main link remains VPN (default)
            // Local badge remains hidden (default)
             localBadge.classList.add('hidden');
        }
    }
}

async function probeUrl(url) {
    try {
        const controller = new AbortController();
        const id = setTimeout(() => controller.abort(), 1500); // 1.5s timeout
        
        await fetch(url, {
            mode: 'no-cors', // Opaque response is fine, we just want to know if it connects
            signal: controller.signal
        });
        clearTimeout(id);
        return true;
    } catch (e) {
        return false;
    }
}

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
    const taskInput = document.getElementById('task-input');
    if (taskInput) taskInput.value = "";
    fetchRoots();
}

function closeWizard() {
    document.getElementById('wizard').classList.remove('active');
}

// --- Recent Paths Logic ---
function getRecentPaths() {
    try {
        const raw = localStorage.getItem('recentPaths');
        return raw ? JSON.parse(raw) : [];
    } catch (e) {
        return [];
    }
}

function saveRecentPath(path) {
    if (!path) return;
    try {
        let recents = getRecentPaths();
        // Remove existing to bump to top
        recents = recents.filter(p => p !== path);
        // Add to front
        recents.unshift(path);
        // Limit to 3
        if (recents.length > 3) recents = recents.slice(0, 3);
        localStorage.setItem('recentPaths', JSON.stringify(recents));
    } catch (e) {
        console.error("Failed to save recent path", e);
    }
}

async function fetchRoots() {
    const res = await fetch('/api/roots');
    const data = await res.json();
    const list = document.getElementById('roots-list');
    list.innerHTML = "";

    // 1. Recent Paths
    const recents = getRecentPaths();
    if (recents.length > 0) {
        const header = document.createElement('div');
        header.innerText = "Recent";
        header.style.cssText = "font-size: 0.75rem; color: var(--text-dim); margin: 10px 0 5px 5px; text-transform: uppercase;";
        list.appendChild(header);

        recents.forEach(path => {
            const div = document.createElement('div');
            div.className = 'list-item';
            div.style.borderLeft = "3px solid var(--accent)";
            div.innerHTML = `<span style="font-family:monospace; font-size:0.9em">${path}</span> <span style="font-size:0.8em">🚀</span>`;
            div.onclick = () => {
                currentPath = path;
                goToConfig();
            };
            list.appendChild(div);
        });
    }

    // 2. System Roots
    const rootHeader = document.createElement('div');
    rootHeader.innerText = "System Roots";
    rootHeader.style.cssText = "font-size: 0.75rem; color: var(--text-dim); margin: 15px 0 5px 5px; text-transform: uppercase;";
    list.appendChild(rootHeader);

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
    
    // Setup Session Type Toggle
    const typeSelect = document.getElementById('session-type-select');
    typeSelect.onchange = toggleTaskInput;
    toggleTaskInput(); // Init state
    
    // Init Worktree State
    toggleWorktreeInput();
    
    showStep('step-config');
}

function toggleWorktreeInput() {
    const isChecked = document.getElementById('worktree-check').checked;
    const optionsDiv = document.getElementById('worktree-options');
    optionsDiv.style.display = isChecked ? 'block' : 'none';
}

function toggleTaskInput() {
    const type = document.getElementById('session-type-select').value;
    const taskContainer = document.getElementById('task-input').parentElement.parentElement; // The div wrapping label+checkbox and textarea
    const taskInput = document.getElementById('task-input');
    
    // Note: In updated HTML, task-input is inside a div, and that div is inside the main container div
    // Logic: The structure is <div> <div>Label+Check</div> <textarea> ... </div>
    // So parentElement of textarea is the container.
    
    if (type === 'bash') {
        taskInput.parentElement.style.display = 'none';
        taskInput.value = ""; 
    } else {
        taskInput.parentElement.style.display = 'block';
    }
    validateInteractive();
}

function validateInteractive() {
    const task = document.getElementById('task-input').value.trim();
    const check = document.getElementById('interactive-check');
    
    if (!task) {
        // No task? Must be interactive.
        check.checked = true;
        check.disabled = true;
        check.parentElement.title = "Interactive mode is required when no task is provided";
        check.parentElement.style.opacity = "0.6";
    } else {
        // Has task? User choice.
        check.disabled = false;
        check.parentElement.title = "";
        check.parentElement.style.opacity = "1";
    }
}

function openWizard() {
    document.getElementById('wizard').classList.add('active');
    const taskInput = document.getElementById('task-input');
    if (taskInput) {
        taskInput.value = "";
        validateInteractive();
    }
    fetchRoots();
}

function closeWizard() {
    document.getElementById('wizard').classList.remove('active');
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
            let html = "<div style='margin-bottom:5px'>◈ Active profile with custom arguments:</div>";
            html += "<div style='color:var(--text-dim); padding-left:10px; font-family:monospace; font-size:0.7rem;'>";
            html += data.extra_args.map(a => `<div>↳ ${a}</div>`).join('');
            html += "</div>";
            detailsDiv.innerHTML = html;
        } else {
            detailsDiv.innerText = "◈ Active profile using defaults";
        }
    } catch (e) {
        detailsDiv.innerText = "";
    }
}

async function doLaunch() {
    const btn = document.getElementById('launch-btn');
    const backBtn = document.getElementById('launch-back-btn');
    const loader = document.getElementById('launch-loader');
    const config = document.getElementById('config-select').value;
    const sessionType = document.getElementById('session-type-select').value;
    const imageVariant = document.getElementById('image-variant-select').value;
    const dockerEnabled = document.getElementById('docker-check').checked;
    const ideEnabled = document.getElementById('ide-check').checked;
    const worktreeMode = document.getElementById('worktree-check').checked;
    const worktreeName = document.getElementById('worktree-name').value;
    const task = document.getElementById('task-input').value;
    const interactive = document.getElementById('interactive-check').checked;
    const results = document.getElementById('launch-results');
    const status = document.getElementById('launch-status');
    const cmdSpan = document.getElementById('launch-cmd');
    const logPre = document.getElementById('launch-log');

    btn.style.display = "none";
    backBtn.style.display = "none";
    loader.style.display = "block";
    results.style.display = "none";

    try {
        const res = await fetch('/api/launch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                project_path: currentPath,
                config_profile: config,
                session_type: sessionType,
                image_variant: imageVariant,
                docker_enabled: dockerEnabled,
                ide_enabled: ideEnabled,
                worktree_mode: worktreeMode,
                worktree_name: worktreeName,
                task: task,
                interactive: interactive
            })
        });
        const result = await res.json();
        
        results.style.display = "block";
        cmdSpan.innerText = result.command || "???";
        logPre.innerText = (result.stdout || "") + "\n" + (result.stderr || "");
        
        if (result.status === 'success') {
            saveRecentPath(currentPath);
            status.innerText = "✅ Session launched!";
            status.style.color = "var(--accent)";
            
            // Try to extract hostname to offer direct connect
            const match = (result.stdout || "").match(/Container started: (gem-[a-zA-Z0-9-]+)/);
            if (match && match[1]) {
                const hostname = match[1];
                
                // 1. Default to VPN Button
                btn.innerText = "Connect (VPN) 🚀";
                btn.onclick = () => window.open(`http://${hostname}:3000`, '_blank');
                btn.style.display = "block";
                
                // 2. Upgrade to Local Button (if on host)
                if (['localhost', '127.0.0.1'].includes(window.location.hostname)) {
                    // Poll briefly for the port mapping to appear
                    setTimeout(async () => {
                        try {
                            const res = await fetch(`/api/resolve-local-url?hostname=${hostname}`);
                            const data = await res.json();
                            if (data.url) {
                                // Smart Upgrade: Change the main button to Local
                                btn.innerText = "Connect (Local) ⚡";
                                btn.onclick = () => window.open(data.url, '_blank');
                                btn.style.border = "1px solid var(--accent)";
                            }
                        } catch (e) { console.error("Failed to resolve local url", e); }
                    }, 1500); // Wait 1.5s for Docker to map ports
                }
            }

            backBtn.innerText = "Done";
            backBtn.onclick = () => window.location.reload();
            backBtn.style.display = "block";
        } else {
            status.innerText = "❌ Launch failed";
            status.style.color = "var(--offline)";
            btn.style.display = "block";
            backBtn.style.display = "block";
        }
    } catch (e) {
        status.innerText = "❌ Network Error";
        status.style.color = "var(--offline)";
        logPre.innerText = e.toString();
        results.style.display = "block";
        btn.style.display = "block";
        backBtn.style.display = "block";
    } finally {
        loader.style.display = "none";
    }
}
