import pytest
import threading
from werkzeug.serving import make_server
from app import create_app
from app.config import Config

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Patch the Config class attributes directly so services see them
    # We must patch where Config is DEFINED, not imported, but services import Config class.
    # Changing attributes on the class affects all users.
    
    # Save original values
    original_roots = Config.HUB_ROOTS
    original_config_root = Config.HOST_CONFIG_ROOT
    original_auth_key = Config.TAILSCALE_AUTH_KEY
    original_auto_shutdown = Config.HUB_AUTO_SHUTDOWN
    
    # Set mock values
    Config.HUB_ROOTS = ["/mock/root"]
    Config.HOST_CONFIG_ROOT = "/mock/config"
    Config.TAILSCALE_AUTH_KEY = "mock-key"
    Config.HUB_AUTO_SHUTDOWN = False

    app = create_app(Config)
    
    yield app
    
    # Restore original values
    Config.HUB_ROOTS = original_roots
    Config.HOST_CONFIG_ROOT = original_config_root
    Config.TAILSCALE_AUTH_KEY = original_auth_key
    Config.HUB_AUTO_SHUTDOWN = original_auto_shutdown

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture(scope="session")
def runner(app):
    """A test runner for the app's CLI commands."""
    return app.test_cli_runner()

@pytest.fixture
def live_server_url(app):
    """Start a live server in a separate thread for UI testing."""
    # Use port 0 to let the OS pick a free port
    server = make_server('127.0.0.1', 0, app)
    port = server.socket.getsockname()[1]
    
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    
    url = f"http://127.0.0.1:{port}"
    yield url
    
    server.shutdown()
    thread.join()
