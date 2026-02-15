from playwright.sync_api import Page, expect

def test_dashboard_loads(page: Page, live_server_url):
    """Verify that the dashboard loads and displays the title."""
    # live_server_url is the base URL of the running Flask app
    page.goto(live_server_url)
    
    # Check title
    expect(page).to_have_title("Gemini Hub")
    
    # Check for main components
    expect(page.get_by_text("Gemini Workspace Hub")).to_be_visible()
    expect(page.get_by_placeholder("Search sessions...")).to_be_visible()

def test_dashboard_no_sessions_initially(page: Page, live_server_url):
    """Verify the 'No active sessions' message is shown when mock Tailscale returns nothing."""
    page.goto(live_server_url)
    
    # Since we use mock values in conftest.py, and don't have real tailscale,
    # it should show "No active sessions found".
    expect(page.get_by_text("No active sessions found")).to_be_visible()
