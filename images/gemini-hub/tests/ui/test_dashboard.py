import pytest
from playwright.sync_api import expect
from unittest.mock import patch
from tests.ui.pages import HubPage

def test_dashboard_loads(hub: HubPage):
    """Verify that the dashboard loads and displays the title."""
    hub.navigate()
    expect(hub.page).to_have_title("Gemini Hub")
    expect(hub.page.get_by_text("Gemini Workspace Hub")).to_be_visible()
    expect(hub.project_filter).to_be_visible()

@pytest.mark.usefixtures("suppress_logs")
def test_dashboard_no_sessions_initially(hub: HubPage):
    """Verify the 'No active sessions' message is shown when mock Tailscale returns nothing."""
    hub.navigate()
    expect(hub.page.get_by_text("No active sessions found")).to_be_visible()

def test_wizard_full_launch_journey(hub: HubPage, tmp_path, monkeypatch):
    """Test the full wizard journey using POM and real filesystem."""
    project_root = tmp_path / "projects"
    project_root.mkdir()
    app_dir = project_root / "my-app"
    app_dir.mkdir()
    
    from app.config import Config
    monkeypatch.setattr(Config, "HUB_ROOTS", [str(project_root)])
    
    # We need to mock a stdout that contains "Container started: ..." for the Connect button to appear
    mock_out = "Container started: gem-test-session"
    with patch("app.services.launcher.LauncherService.launch", return_value={"returncode": 0, "stdout": mock_out, "stderr": "", "command": "cmd"}):
        hub.navigate()
        hub.open_wizard()
        hub.select_root(str(project_root))
        hub.select_folder("my-app")
        
        expect(hub.current_path).to_have_text(str(app_dir))
        
        hub.use_this_folder()
        hub.launch(task="Hello", variant="standard")
        
        expect(hub.page.get_by_text("Session launched!")).to_be_visible()
        # The button text in main.js is "Connect (VPN) 🚀"
        expect(hub.page.get_by_role("button", name="Connect (VPN) 🚀")).to_be_visible()

def test_wizard_navigation_back_and_up(hub: HubPage, tmp_path, monkeypatch):
    """Test 'Back' and 'Up' navigation using POM and real filesystem."""
    root = tmp_path / "projects"
    root.mkdir()
    subdir = root / "subdir"
    subdir.mkdir()
    
    from app.config import Config
    monkeypatch.setattr(Config, "HUB_ROOTS", [str(root)])
    
    hub.navigate()
    hub.open_wizard()
    hub.select_root(str(root))
    hub.select_folder("subdir")
    expect(hub.current_path).to_have_text(str(subdir))
    
    hub.page.get_by_text(".. (Up)").click()
    expect(hub.current_path).to_have_text(str(root))
    expect(hub.folder_list.get_by_text("📁 subdir")).to_be_visible()

def test_wizard_custom_image_toggle(hub: HubPage):
    """Verify that custom image input toggles correctly."""
    with patch("app.services.filesystem.FileSystemService.get_roots", return_value=["/root"]), \
         patch("app.services.filesystem.FileSystemService.browse", return_value={"directories": [], "files": []}):
        hub.navigate()
        hub.open_wizard()
        hub.select_root("/root")
        hub.use_this_folder()
        
        input_locator = hub.page.get_by_placeholder("e.g. jsebayhi/gemini-cli-toolbox:latest")
        expect(input_locator).to_be_hidden()
        
        hub.image_variant_select.select_option("custom")
        expect(input_locator).to_be_visible()

def test_dashboard_filtering(hub: HubPage):
    """Verify that session filtering works without static sleeps."""
    mock_machines = [
        {"name": "gem-p1", "project": "proj-alpha", "type": "geminicli", "ip": "100.1.1.1", "online": True},
        {"name": "gem-p2", "project": "proj-beta", "type": "bash", "ip": "100.1.1.2", "online": True},
    ]
    with patch("app.services.tailscale.TailscaleService.get_status", return_value={}), \
         patch("app.services.tailscale.TailscaleService.parse_peers", return_value=mock_machines):
        hub.navigate()
        expect(hub.page.locator(".card")).to_have_count(2)
        
        hub.project_filter.press_sequentially("alpha", delay=50)
        expect(hub.page.locator(".card:visible")).to_have_count(1)
        expect(hub.page.get_by_text("proj-alpha")).to_be_visible()

@pytest.mark.usefixtures("suppress_logs")
def test_session_stop_lifecycle(hub: HubPage):
    """Verify that stopping a session from the UI works correctly."""
    mock_machines = [{"name": "gem-s", "project": "stop-me", "type": "geminicli", "ip": "100.1.1.1", "online": True}]
    with patch("app.services.tailscale.TailscaleService.get_status", return_value={}), \
         patch("app.services.tailscale.TailscaleService.parse_peers", return_value=mock_machines), \
         patch("app.services.session.SessionService.stop", return_value={"status": "success", "session_id": "gem-s"}):
        hub.navigate()
        hub.stop_session("stop-me")
        expect(hub.page.get_by_role("button", name="Stopped")).to_be_visible()
        expect(hub.page.locator(".card", has_text="stop-me")).to_have_css("opacity", "0.5")

def test_wizard_recent_paths_persistence(hub: HubPage):
    """Verify that recent paths are saved and accessible."""
    hub.navigate()
    hub.page.evaluate("localStorage.clear()")
    
    recent_path = "/mock/recent/path"
    mock_roots = ["/mock/root"]
    with patch("app.services.filesystem.FileSystemService.get_roots", return_value=mock_roots), \
         patch("app.services.filesystem.FileSystemService.get_configs", return_value=[]):
        hub.page.evaluate(f"localStorage.setItem('recentPaths', JSON.stringify(['{recent_path}']))")
        hub.navigate()
        hub.open_wizard()
        expect(hub.page.get_by_text("Recent", exact=True)).to_be_visible()
        hub.page.get_by_text(recent_path).click()
        # In main.js, clicking a recent path calls goToConfig() which updates config-project-path
        expect(hub.page.locator("#config-project-path")).to_have_text(recent_path)

@pytest.mark.skip(reason="Flaky probe logic in headless CI environment")
@pytest.mark.usefixtures("suppress_logs")
def test_connectivity_hybrid_mode(hub: HubPage):
    """Verify hybrid mode using POM."""
    hub.page.add_init_script("window.probeUrl = async () => true;")
    mock_machines = [{"name": "gem-h", "project": "h", "type": "cli", "ip": "1.1.1.1", "online": True, "local_url": "http://localhost:32768"}]
    
    with patch("app.services.tailscale.TailscaleService.get_status", return_value={}), \
         patch("app.services.tailscale.TailscaleService.parse_peers", return_value=mock_machines):
        url = hub.base_url.replace("127.0.0.1", "localhost")
        hub.page.goto(url)
        expect(hub.page.locator(".local-badge")).to_have_text("VPN")

def test_wizard_bash_mode_hides_inputs(hub: HubPage):
    """Verify that selecting Bash mode hides Task and Interactive inputs."""
    with patch("app.services.filesystem.FileSystemService.get_roots", return_value=["/root"]), \
         patch("app.services.filesystem.FileSystemService.browse", return_value={"directories": [], "files": []}):
        hub.navigate()
        hub.open_wizard()
        hub.select_root("/root")
        hub.use_this_folder()
        hub.session_type_select.select_option("bash")
        expect(hub.task_input).to_be_hidden()

def test_wizard_advanced_options_toggle(hub: HubPage):
    """Verify that the Advanced Options accordion works."""
    with patch("app.services.filesystem.FileSystemService.get_roots", return_value=["/root"]), \
         patch("app.services.filesystem.FileSystemService.browse", return_value={"directories": [], "files": []}):
        hub.navigate()
        hub.open_wizard()
        hub.select_root("/root")
        hub.use_this_folder()
        expect(hub.docker_args_input).to_be_hidden()
        hub.advanced_toggle.click()
        expect(hub.docker_args_input).to_be_visible()

@pytest.mark.usefixtures("suppress_logs")
def test_wizard_browse_error_handling(hub: HubPage):
    """Verify that browsing errors are handled gracefully."""
    with patch("app.services.filesystem.FileSystemService.get_roots", return_value=["/root"]), \
         patch("app.services.filesystem.FileSystemService.browse", side_effect=PermissionError("Access Denied")):
        hub.navigate()
        hub.open_wizard()
        hub.page.on("dialog", lambda dialog: expect(dialog.message).to_contain("Access Denied"))
        hub.select_root("/root")

@pytest.mark.usefixtures("suppress_logs")
def test_wizard_launch_error_handling(hub: HubPage):
    """Verify that launch errors are displayed in the UI."""
    with patch("app.services.filesystem.FileSystemService.get_roots", return_value=["/root"]), \
         patch("app.services.filesystem.FileSystemService.browse", return_value={"directories": [], "files": []}), \
         patch("app.services.launcher.LauncherService.launch", return_value={"returncode": 1, "stdout": "", "stderr": "Failed", "command": "cmd"}):
        hub.navigate()
        hub.open_wizard()
        hub.select_root("/root")
        hub.use_this_folder()
        hub.launch()
        expect(hub.page.get_by_text("Launch failed")).to_be_visible()

def test_wizard_worktree_toggle(hub: HubPage):
    """Verify that worktree options toggle correctly."""
    with patch("app.services.filesystem.FileSystemService.get_roots", return_value=["/root"]), \
         patch("app.services.filesystem.FileSystemService.browse", return_value={"directories": [], "files": []}):
        hub.navigate()
        hub.open_wizard()
        hub.select_root("/root")
        hub.use_this_folder()
        
        expect(hub.worktree_name_input).to_be_hidden()
        hub.worktree_check.check()
        expect(hub.worktree_name_input).to_be_visible()
