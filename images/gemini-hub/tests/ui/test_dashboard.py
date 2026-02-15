import pytest
from playwright.sync_api import Page, expect
from unittest.mock import patch

def test_dashboard_loads(page: Page, live_server_url):
    """Verify that the dashboard loads and displays the title."""
    page.goto(live_server_url)
    expect(page).to_have_title("Gemini Hub")
    expect(page.get_by_text("Gemini Workspace Hub")).to_be_visible()
    expect(page.get_by_placeholder("Search sessions...")).to_be_visible()

@pytest.mark.usefixtures("suppress_logs")
def test_dashboard_no_sessions_initially(page: Page, live_server_url):
    """Verify the 'No active sessions' message is shown when mock Tailscale returns nothing."""
    page.goto(live_server_url)
    expect(page.get_by_text("No active sessions found")).to_be_visible()

def test_wizard_full_launch_journey(page: Page, live_server_url, tmp_path, monkeypatch):
    """Test the full wizard journey using a REAL directory structure (tmp_path)."""
    
    project_root = tmp_path / "projects"
    project_root.mkdir()
    app_dir = project_root / "my-app"
    app_dir.mkdir()
    
    from app.config import Config
    monkeypatch.setattr(Config, "HUB_ROOTS", [str(project_root)])
    
    with patch("app.services.launcher.LauncherService.launch", return_value={"returncode": 0, "stdout": "Container started: gem-my-app-cli-abc123", "stderr": "", "command": "cmd"}):
        page.goto(live_server_url)
        page.get_by_role("button", name="+ New Session").click()
        page.locator("#roots-list").get_by_text(str(project_root)).click()
        page.locator("#folder-list").get_by_text("📁 my-app").click()
        
        expect(page.locator("#current-path")).to_have_text(str(app_dir))
        
        page.get_by_role("button", name="Use This Folder").click()
        page.get_by_placeholder("e.g. write a hello world in python...").fill("Say hello")
        page.get_by_role("button", name="Launch Session").click()
        
        expect(page.get_by_text("Session launched!")).to_be_visible()
        expect(page.get_by_role("button", name="Connect (VPN)")).to_be_visible()

def test_wizard_navigation_back_and_up(page: Page, live_server_url, tmp_path, monkeypatch):
    """Test 'Back' and 'Up' navigation using real filesystem."""
    root = tmp_path / "projects"
    root.mkdir()
    subdir = root / "subdir"
    subdir.mkdir()
    
    from app.config import Config
    monkeypatch.setattr(Config, "HUB_ROOTS", [str(root)])
    
    page.goto(live_server_url)
    page.get_by_role("button", name="+ New Session").click()
    
    page.locator("#roots-list").get_by_text(str(root)).click()
    page.locator("#folder-list").get_by_text("📁 subdir").click()
    expect(page.locator("#current-path")).to_have_text(str(subdir))
    
    page.get_by_text(".. (Up)").click()
    expect(page.locator("#current-path")).to_have_text(str(root))
    expect(page.locator("#folder-list").get_by_text("📁 subdir")).to_be_visible()

def test_wizard_custom_image_toggle(page: Page, live_server_url):
    """Verify that custom image input toggles correctly."""
    with patch("app.services.filesystem.FileSystemService.get_roots", return_value=["/root"]), \
         patch("app.services.filesystem.FileSystemService.browse", return_value={"directories": [], "files": []}), \
         patch("app.services.filesystem.FileSystemService.get_configs", return_value=[]):
        page.goto(live_server_url)
        page.get_by_role("button", name="+ New Session").click()
        page.locator("#roots-list").get_by_text("/root").click()
        page.get_by_role("button", name="Use This Folder").click()
        
        input_locator = page.get_by_placeholder("e.g. jsebayhi/gemini-cli-toolbox:latest")
        expect(input_locator).to_be_hidden()
        
        page.locator("#image-variant-select").select_option("custom")
        expect(input_locator).to_be_visible()

def test_dashboard_filtering(page: Page, live_server_url):
    """Verify that session filtering works without static sleeps."""
    mock_machines = [
        {"name": "gem-p1", "project": "proj-alpha", "type": "geminicli", "ip": "1.1.1.1", "online": True},
        {"name": "gem-p2", "project": "proj-beta", "type": "bash", "ip": "1.1.1.2", "online": True},
    ]
    with patch("app.services.tailscale.TailscaleService.get_status", return_value={}), \
         patch("app.services.tailscale.TailscaleService.parse_peers", return_value=mock_machines):
        
        page.goto(live_server_url)
        expect(page.locator(".card")).to_have_count(2)
        
        page.get_by_placeholder("Search sessions...").press_sequentially("alpha", delay=50)
        
        expect(page.locator(".card:visible")).to_have_count(1)
        expect(page.get_by_text("proj-alpha")).to_be_visible()
        expect(page.get_by_text("proj-beta")).to_be_hidden()

@pytest.mark.usefixtures("suppress_logs")
def test_session_stop_lifecycle(page: Page, live_server_url):
    """Verify that stopping a session from the UI works correctly."""
    mock_machines = [{"name": "gem-s", "project": "s", "type": "geminicli", "ip": "1.1.1.1", "online": True}]
    with patch("app.services.tailscale.TailscaleService.get_status", return_value={}), \
         patch("app.services.tailscale.TailscaleService.parse_peers", return_value=mock_machines), \
         patch("app.services.session.SessionService.stop", return_value={"status": "success", "session_id": "gem-s"}):
        page.goto(live_server_url)
        page.on("dialog", lambda dialog: dialog.accept())
        page.get_by_role("button", name="Stop").click()
        
        expect(page.get_by_role("button", name="Stopped")).to_be_visible()
        expect(page.locator(".card", has_text="s")).to_have_css("opacity", "0.5")

@pytest.mark.skip(reason="Flaky probe logic in headless CI environment")
@pytest.mark.usefixtures("suppress_logs")
def test_connectivity_hybrid_mode(page: Page, live_server_url):
    """Verify hybrid mode using deterministic JS mocking instead of network interception."""
    page.add_init_script("""
        window.probeUrl = async (url) => {
            if (url.includes('localhost') || url.includes('127.0.0.1')) return true;
            if (url.includes('1.1.1.1')) return true;
            return false;
        };
    """)
    
    mock_machines = [{
        "name": "gem-h", 
        "project": "hybrid-app", 
        "type": "cli", 
        "ip": "1.1.1.1", 
        "online": True, 
        "local_url": "http://localhost:32768"
    }]
    
    with patch("app.services.tailscale.TailscaleService.get_status", return_value={}), \
         patch("app.services.tailscale.TailscaleService.parse_peers", return_value=mock_machines):
        
        url = live_server_url.replace("127.0.0.1", "localhost")
        page.goto(url)
        
        main_link = page.locator(".card-main-link", has_text="hybrid-app")
        expect(main_link).to_have_attribute("href", "http://localhost:32768")
        expect(page.locator(".local-badge")).to_have_text("VPN")

def test_wizard_recent_paths_persistence(page: Page, live_server_url):
    """Verify that recent paths are saved and accessible."""
    page.goto(live_server_url)
    page.evaluate("localStorage.clear()")
    
    mock_roots = ["/mock/root"]
    with patch("app.services.filesystem.FileSystemService.get_roots", return_value=mock_roots):
        page.evaluate("localStorage.setItem('recentPaths', JSON.stringify(['/mock/recent/path']))")
        page.goto(live_server_url)
        page.get_by_role("button", name="+ New Session").click()
        expect(page.get_by_text("Recent", exact=True)).to_be_visible()
        page.get_by_text("/mock/recent/path").click()
        expect(page.locator("#config-project-path")).to_have_text("/mock/recent/path")

def test_wizard_bash_mode_hides_inputs(page: Page, live_server_url):
    """Verify that selecting Bash mode hides Task and Interactive inputs."""
    with patch("app.services.filesystem.FileSystemService.get_roots", return_value=["/root"]), \
         patch("app.services.filesystem.FileSystemService.browse", return_value={"directories": [], "files": []}):
        page.goto(live_server_url)
        page.get_by_role("button", name="+ New Session").click()
        page.locator("#roots-list").get_by_text("/root").click()
        page.get_by_role("button", name="Use This Folder").click()
        page.locator("#session-type-select").select_option("bash")
        expect(page.get_by_placeholder("e.g. write a hello world in python...")).to_be_hidden()

def test_wizard_advanced_options_toggle(page: Page, live_server_url):
    """Verify that the Advanced Options accordion works."""
    with patch("app.services.filesystem.FileSystemService.get_roots", return_value=["/root"]), \
         patch("app.services.filesystem.FileSystemService.browse", return_value={"directories": [], "files": []}):
        page.goto(live_server_url)
        page.get_by_role("button", name="+ New Session").click()
        page.locator("#roots-list").get_by_text("/root").click()
        page.get_by_role("button", name="Use This Folder").click()
        
        options_locator = page.get_by_placeholder("e.g. -v /host/path:/container/path")
        expect(options_locator).to_be_hidden()
        page.get_by_text("Advanced Options").click()
        expect(options_locator).to_be_visible()

@pytest.mark.usefixtures("suppress_logs")
def test_wizard_browse_error_handling(page: Page, live_server_url):
    """Verify that browsing errors are handled gracefully."""
    with patch("app.services.filesystem.FileSystemService.get_roots", return_value=["/root"]), \
         patch("app.services.filesystem.FileSystemService.browse", side_effect=PermissionError("Access Denied")):
        page.goto(live_server_url)
        page.get_by_role("button", name="+ New Session").click()
        page.on("dialog", lambda dialog: expect(dialog.message).to_contain("Access Denied"))
        page.get_by_text("/root").click()

@pytest.mark.usefixtures("suppress_logs")
def test_wizard_launch_error_handling(page: Page, live_server_url):
    """Verify that launch errors are displayed in the UI."""
    with patch("app.services.filesystem.FileSystemService.get_roots", return_value=["/root"]), \
         patch("app.services.filesystem.FileSystemService.browse", return_value={"directories": [], "files": []}), \
         patch("app.services.launcher.LauncherService.launch", return_value={"returncode": 1, "stdout": "", "stderr": "Failed", "command": "cmd"}):
        page.goto(live_server_url)
        page.get_by_role("button", name="+ New Session").click()
        page.locator("#roots-list").get_by_text("/root").click()
        page.get_by_role("button", name="Use This Folder").click()
        page.get_by_role("button", name="Launch Session").click()
        expect(page.get_by_text("Launch failed")).to_be_visible()

def test_wizard_worktree_toggle(page: Page, live_server_url):
    """Verify that worktree options toggle correctly."""
    with patch("app.services.filesystem.FileSystemService.get_roots", return_value=["/root"]), \
         patch("app.services.filesystem.FileSystemService.browse", return_value={"directories": [], "files": []}), \
         patch("app.services.filesystem.FileSystemService.get_configs", return_value=[]):
        page.goto(live_server_url)
        page.get_by_role("button", name="+ New Session").click()
        page.locator("#roots-list").get_by_text("/root").click()
        page.get_by_role("button", name="Use This Folder").click()
        
        expect(page.get_by_placeholder("Optional: Branch/Worktree Name")).to_be_hidden()
        page.get_by_label("Launch in Ephemeral Worktree").check()
        expect(page.get_by_placeholder("Optional: Branch/Worktree Name")).to_be_visible()
