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
                session_type: sessionType
            })
        });
        const result = await res.json();
        
        results.style.display = "block";
        cmdSpan.innerText = result.command || "???";
        logPre.innerText = (result.stdout || "") + "\n" + (result.stderr || "");
        
        if (result.status === 'success') {
            status.innerText = "✅ Session launched!";
            status.style.color = "var(--accent)";
            
            // Try to extract hostname to offer direct connect
            const match = (result.stdout || "").match(/Container started: (gem-[a-zA-Z0-9-]+)/);
            if (match && match[1]) {
                const hostname = match[1];
                btn.innerText = "Connect Now 🚀";
                btn.onclick = () => window.open(`http://${hostname}:3000`, '_blank');
                btn.style.display = "block";
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
