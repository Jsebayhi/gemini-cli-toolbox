import pytest
from playwright.sync_api import Page, expect
from unittest.mock import patch

def test_dashboard_loads(page: Page, live_server_url):
    """Verify that the dashboard loads and displays the title."""
    page.goto(live_server_url)
    expect(page).to_have_title("Gemini Hub")
    expect(page.get_by_text("Gemini Workspace Hub")).to_be_visible()
    expect(page.get_by_placeholder("Search sessions...")).to_be_visible()

def test_dashboard_no_sessions_initially(page: Page, live_server_url):
    """Verify the 'No active sessions' message is shown when mock Tailscale returns nothing."""
    page.goto(live_server_url)
    expect(page.get_by_text("No active sessions found")).to_be_visible()

def test_wizard_full_launch_journey(page: Page, live_server_url):
    """Test the full wizard journey from root selection to launch."""
    
    # Mock data
    mock_roots = ["/mock/projects", "/mock/lab"]
    mock_dirs = ["my-app", "another-project"]
    mock_configs = ["work", "personal"]
    
    # We patch the services that the API routes call
    with patch("app.services.filesystem.FileSystemService.get_roots", return_value=mock_roots), \
         patch("app.services.filesystem.FileSystemService.browse", return_value={"directories": mock_dirs, "files": []}), \
         patch("app.services.filesystem.FileSystemService.get_configs", return_value=mock_configs), \
         patch("app.services.launcher.LauncherService.launch", return_value={"returncode": 0, "stdout": "Container started: gem-my-app-cli-abc123", "stderr": "", "command": "gemini-toolbox launch ..."}):

        page.goto(live_server_url)
        
        # 1. Open Wizard
        page.get_by_role("button", name="+ New Session").click()
        expect(page.get_by_text("Select a workspace root:")).to_be_visible()
        
        # 2. Select Root
        # Use #roots-list to avoid ambiguity with breadcrumb
        page.locator("#roots-list").get_by_text("/mock/projects").click()
        expect(page.locator("#current-path")).to_have_text("/mock/projects")
        
        # 3. Browse to folder
        # Use #folder-list to avoid ambiguity
        page.locator("#folder-list").get_by_text("📁 my-app").click()
        expect(page.locator("#current-path")).to_have_text("/mock/projects/my-app")
        
        # 4. Use this folder
        page.get_by_role("button", name="Use This Folder").click()
        expect(page.get_by_text("Profile Configuration")).to_be_visible()
        
        # 5. Configure Session
        # Verify default interactive state (disabled because no task)
        expect(page.get_by_label("Interactive")).to_be_checked()
        expect(page.get_by_label("Interactive")).to_be_disabled()
        
        # Enter a task
        page.get_by_placeholder("e.g. write a hello world in python...").fill("Say hello")
        # Now interactive should be enabled
        expect(page.get_by_label("Interactive")).to_be_enabled()
        
        # Select a profile
        page.locator("#config-select").select_option("work")
        
        # Select a variant
        page.locator("#image-variant-select").select_option("standard")
        
        # 6. Launch
        page.get_by_role("button", name="Launch Session").click()
        
        # 7. Verify Results
        expect(page.get_by_text("Session launched!")).to_be_visible()
        expect(page.get_by_text("Container started: gem-my-app-cli-abc123")).to_be_visible()
        
        # Verify Connect button appeared
        expect(page.get_by_role("button", name="Connect (VPN)")).to_be_visible()
        
        # Verify Done button takes us back
        page.get_by_role("button", name="Done").click()
        expect(page.get_by_text("Gemini Workspace Hub")).to_be_visible()

def test_wizard_navigation_back_and_up(page: Page, live_server_url):
    """Test 'Back' and 'Up' navigation in the wizard."""
    
    mock_roots = ["/projects"]
    mock_dirs_root = ["subdir"]
    mock_dirs_sub = ["leaf"]
    
    with patch("app.services.filesystem.FileSystemService.get_roots", return_value=mock_roots), \
         patch("app.services.filesystem.FileSystemService.browse") as mock_browse:
        
        # Setup mock_browse to return different things based on call
        def browse_side_effect(path):
            if path == "/projects":
                return {"directories": mock_dirs_root, "files": []}
            return {"directories": mock_dirs_sub, "files": []}
        
        mock_browse.side_effect = browse_side_effect

        page.goto(live_server_url)
        page.get_by_role("button", name="+ New Session").click()
        
        # Go deep
        page.locator("#roots-list").get_by_text("/projects").click()
        page.locator("#folder-list").get_by_text("📁 subdir").click()
        expect(page.locator("#current-path")).to_have_text("/projects/subdir")
        
        # Go Up
        page.get_by_text(".. (Up)").click()
        expect(page.locator("#current-path")).to_have_text("/projects")
        expect(page.locator("#folder-list").get_by_text("📁 subdir")).to_be_visible()
        
        # Change Root (goes back to roots list)
        page.get_by_role("button", name="Change Root").click()
        expect(page.get_by_text("Select a workspace root:")).to_be_visible()
        expect(page.locator("#roots-list").get_by_text("/projects")).to_be_visible()

def test_wizard_custom_image_toggle(page: Page, live_server_url):
    """Verify that custom image input toggles correctly."""
    
    with patch("app.services.filesystem.FileSystemService.get_roots", return_value=["/root"]), \
         patch("app.services.filesystem.FileSystemService.browse", return_value={"directories": [], "files": []}), \
         patch("app.services.filesystem.FileSystemService.get_configs", return_value=[]):
             
        page.goto(live_server_url)
        page.get_by_role("button", name="+ New Session").click()
        page.locator("#roots-list").get_by_text("/root").click()
        page.get_by_role("button", name="Use This Folder").click()
        
        # Initially hidden
        expect(page.get_by_placeholder("e.g. jsebayhi/gemini-cli-toolbox:latest")).not_to_be_visible()
        
        # Select Custom
        page.locator("#image-variant-select").select_option("custom")
        expect(page.get_by_placeholder("e.g. jsebayhi/gemini-cli-toolbox:latest")).to_be_visible()
        
        # Back to standard
        page.locator("#image-variant-select").select_option("standard")
        expect(page.get_by_placeholder("e.g. jsebayhi/gemini-cli-toolbox:latest")).not_to_be_visible()

def test_wizard_worktree_toggle(page: Page, live_server_url):
    """Verify that worktree options toggle correctly."""
    
    with patch("app.services.filesystem.FileSystemService.get_roots", return_value=["/root"]), \
         patch("app.services.filesystem.FileSystemService.browse", return_value={"directories": [], "files": []}), \
         patch("app.services.filesystem.FileSystemService.get_configs", return_value=[]):
             
        page.goto(live_server_url)
        page.get_by_role("button", name="+ New Session").click()
        page.locator("#roots-list").get_by_text("/root").click()
        page.get_by_role("button", name="Use This Folder").click()
        
        # Initially hidden
        expect(page.get_by_placeholder("Optional: Branch/Worktree Name")).not_to_be_visible()
        
        # Check Worktree
        page.get_by_label("Launch in Ephemeral Worktree").check()
        expect(page.get_by_placeholder("Optional: Branch/Worktree Name")).to_be_visible()
        
        # Uncheck
        page.get_by_label("Launch in Ephemeral Worktree").uncheck()
        expect(page.get_by_placeholder("Optional: Branch/Worktree Name")).not_to_be_visible()

def test_dashboard_filtering(page: Page, live_server_url):
    """Verify that session filtering works."""
    
    mock_machines = [
        {"name": "gem-proj1-cli-1", "project": "proj1", "type": "geminicli", "ip": "100.1.1.1", "online": True},
        {"name": "gem-proj2-bash-2", "project": "proj2", "type": "bash", "ip": "100.1.1.2", "online": True},
    ]
    
    with patch("app.services.tailscale.TailscaleService.get_status", return_value={}), \
         patch("app.services.tailscale.TailscaleService.parse_peers", return_value=mock_machines):
        
        page.goto(live_server_url)
        
        # Both visible initially
        expect(page.get_by_text("proj1")).to_be_visible()
        expect(page.get_by_text("proj2")).to_be_visible()
        
        # Filter by name
        page.get_by_placeholder("Search sessions...").press_sequentially("proj1", delay=50)
        # Filtering is client-side JS (onkeyup), might need a tiny wait for it to process
        page.wait_for_timeout(500)
        
        expect(page.get_by_text("proj1")).to_be_visible()
        expect(page.get_by_text("proj2")).not_to_be_visible()
        
        # Clear filter
        page.get_by_placeholder("Search sessions...").fill("")
        page.wait_for_timeout(500)
        expect(page.get_by_text("proj1")).to_be_visible()
        expect(page.get_by_text("proj2")).to_be_visible()
        
        # Filter by type
        page.locator("#typeFilter").select_option("bash")
        page.wait_for_timeout(500)
        expect(page.get_by_text("proj1")).not_to_be_visible()
        expect(page.get_by_text("proj2")).to_be_visible()

def test_session_stop_lifecycle(page: Page, live_server_url):
    """Verify that stopping a session from the UI works correctly."""
    
    mock_machines = [
        {"name": "gem-to-stop", "project": "stop-me", "type": "geminicli", "ip": "100.1.1.1", "online": True},
    ]
    
    with patch("app.services.tailscale.TailscaleService.get_status", return_value={}), \
         patch("app.services.tailscale.TailscaleService.parse_peers", return_value=mock_machines), \
         patch("app.services.session.SessionService.stop", return_value={"status": "success", "session_id": "gem-to-stop"}):
        
        page.goto(live_server_url)
        expect(page.get_by_text("stop-me")).to_be_visible()
        
        # 1. Handle the confirmation dialog
        # In Playwright, we must register the dialog handler BEFORE the action that triggers it
        page.on("dialog", lambda dialog: dialog.accept())
        
        # 2. Click Stop
        page.get_by_role("button", name="Stop").click()
        
        # 3. Verify UI state (button text changes and card becomes semi-transparent)
        # The button text changes to "Stopped"
        expect(page.get_by_role("button", name="Stopped")).to_be_visible()
        
        # The card should have opacity 0.5
        card = page.locator(".card", has_text="stop-me")
        expect(card).to_have_css("opacity", "0.5")

def test_wizard_recent_paths_persistence(page: Page, live_server_url):
    """Verify that recent paths are saved and accessible."""
    
    mock_roots = ["/mock/root"]
    mock_configs = ["work"]
    
    with patch("app.services.filesystem.FileSystemService.get_roots", return_value=mock_roots), \
         patch("app.services.filesystem.FileSystemService.get_configs", return_value=mock_configs):
        
        # Setup localStorage via evaluation BEFORE navigating to wizard
        page.goto(live_server_url)
        page.evaluate("localStorage.setItem('recentPaths', JSON.stringify(['/mock/recent/path']))")
        
        # Re-open or trigger fetchRoots (we reload to be safe)
        page.goto(live_server_url)
        
        # 1. Open Wizard
        page.get_by_role("button", name="+ New Session").click()
        
        # 2. Verify Recent path appears
        expect(page.get_by_text("Recent", exact=True)).to_be_visible()
        expect(page.get_by_text("/mock/recent/path")).to_be_visible()
        
        # 3. Click Recent path
        page.get_by_text("/mock/recent/path").click()
        
        # 4. Verify it skipped browsing and went directly to Config
        expect(page.locator("#config-project-path")).to_have_text("/mock/recent/path")
        expect(page.get_by_text("Profile Configuration")).to_be_visible()

def test_connectivity_hybrid_mode(page: Page, live_server_url):
    """Verify that LOCAL/VPN badges appear correctly based on reachability."""
    
    mock_machines = [
        {
            "name": "gem-hybrid", 
            "project": "hybrid-app", 
            "type": "geminicli", 
            "ip": "100.1.1.1", 
            "online": True,
            "local_url": "http://localhost:32768"
        },
    ]
    
    with patch("app.services.tailscale.TailscaleService.get_status", return_value={}), \
         patch("app.services.tailscale.TailscaleService.parse_peers", return_value=mock_machines):
        
        # 1. Setup route interception to simulate reachability
        # We need to allow the main app but mock the probe URLs
        
        def handle_route(route):
            if "localhost:32768" in route.request.url:
                route.fulfill(status=200, body="")
            elif "100.1.1.1:3000" in route.request.url:
                route.fulfill(status=200, body="")
            else:
                route.continue_()

        page.route("**/*", handle_route)
        
        # Navigate
        page.goto(live_server_url)
        
        # Wait for connectivity check logic to run (async in main.js)
        page.wait_for_timeout(500)
        
        # 2. Verify LOCAL link is the main one if reachable
        main_link = page.locator(".card-main-link", has_text="hybrid-app")
        expect(main_link).to_have_attribute("href", "http://localhost:32768")
        
        # 3. Verify VPN badge appeared as secondary
        vpn_badge = page.locator(".local-badge", has_text="VPN")
        expect(vpn_badge).to_be_visible()
        expect(vpn_badge).to_have_attribute("href", "http://100.1.1.1:3000/")

def test_wizard_bash_mode_hides_inputs(page: Page, live_server_url):
    """Verify that selecting Bash mode hides Task and Interactive inputs."""
    
    with patch("app.services.filesystem.FileSystemService.get_roots", return_value=["/root"]), \
         patch("app.services.filesystem.FileSystemService.browse", return_value={"directories": [], "files": []}), \
         patch("app.services.filesystem.FileSystemService.get_configs", return_value=[]):
             
        page.goto(live_server_url)
        page.get_by_role("button", name="+ New Session").click()
        page.locator("#roots-list").get_by_text("/root").click()
        page.get_by_role("button", name="Use This Folder").click()
        
        # Initially (CLI mode) - Task is visible
        expect(page.get_by_placeholder("e.g. write a hello world in python...")).to_be_visible()
        
        # Select Bash
        page.locator("#session-type-select").select_option("bash")
        
        # Task should be hidden
        expect(page.get_by_placeholder("e.g. write a hello world in python...")).not_to_be_visible()

def test_wizard_advanced_options_toggle(page: Page, live_server_url):
    """Verify that the Advanced Options accordion works."""
    
    with patch("app.services.filesystem.FileSystemService.get_roots", return_value=["/root"]), \
         patch("app.services.filesystem.FileSystemService.browse", return_value={"directories": [], "files": []}), \
         patch("app.services.filesystem.FileSystemService.get_configs", return_value=[]):
             
        page.goto(live_server_url)
        page.get_by_role("button", name="+ New Session").click()
        page.locator("#roots-list").get_by_text("/root").click()
        page.get_by_role("button", name="Use This Folder").click()
        
        # Initially hidden
        expect(page.get_by_placeholder("e.g. -v /host/path:/container/path")).not_to_be_visible()
        
        # Toggle Open
        page.get_by_text("Advanced Options").click()
        expect(page.get_by_placeholder("e.g. -v /host/path:/container/path")).to_be_visible()
        
        # Toggle Closed
        page.get_by_text("Advanced Options").click()
        expect(page.get_by_placeholder("e.g. -v /host/path:/container/path")).not_to_be_visible()

def test_wizard_browse_error_handling(page: Page, live_server_url):
    """Verify that browsing errors are handled gracefully."""
    
    with patch("app.services.filesystem.FileSystemService.get_roots", return_value=["/root"]), \
         patch("app.services.filesystem.FileSystemService.browse", side_effect=PermissionError("Access Denied")):
             
        page.goto(live_server_url)
        page.get_by_role("button", name="+ New Session").click()
        
        # Handle the browser alert
        page.on("dialog", lambda dialog: expect(dialog.message).to_contain("Access Denied"))
        page.on("dialog", lambda dialog: dialog.dismiss())
        
        # Click the root to trigger browse
        page.get_by_text("/root").click()

def test_wizard_launch_error_handling(page: Page, live_server_url):
    """Verify that launch errors are displayed in the UI."""
    
    with patch("app.services.filesystem.FileSystemService.get_roots", return_value=["/root"]), \
         patch("app.services.filesystem.FileSystemService.browse", return_value={"directories": [], "files": []}), \
         patch("app.services.filesystem.FileSystemService.get_configs", return_value=[]), \
         patch("app.services.launcher.LauncherService.launch", return_value={"returncode": 1, "stdout": "", "stderr": "Permission denied by host daemon", "command": "docker run ..."}):
             
        page.goto(live_server_url)
        page.get_by_role("button", name="+ New Session").click()
        page.locator("#roots-list").get_by_text("/root").click()
        page.get_by_role("button", name="Use This Folder").click()
        
        # Launch
        page.get_by_role("button", name="Launch Session").click()
        
        # Verify Error State
        expect(page.get_by_text("Launch failed")).to_be_visible()
        expect(page.get_by_text("Permission denied by host daemon")).to_be_visible()
