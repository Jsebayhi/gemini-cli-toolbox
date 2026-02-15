import pytest
import threading
import logging
from werkzeug.serving import make_server
from app import create_app
from app.config import Config

@pytest.fixture
def app(monkeypatch):
    """Create and configure a new app instance for each test."""
    # Use monkeypatch to safely modify Config attributes for the duration of the test.
    # This is thread-safe and process-safe.
    monkeypatch.setattr(Config, "HUB_ROOTS", ["/mock/root"])
    monkeypatch.setattr(Config, "HOST_CONFIG_ROOT", "/mock/config")
    monkeypatch.setattr(Config, "TAILSCALE_AUTH_KEY", "mock-key")
    monkeypatch.setattr(Config, "HUB_AUTO_SHUTDOWN", False)

    app = create_app(Config)
    return app

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

@pytest.fixture
def suppress_logs():
    """Fixture to suppress common expected log errors during tests."""
    logger = logging.getLogger("app.services.tailscale")
    original_level = logger.level
    logger.setLevel(logging.CRITICAL)
    yield
    logger.setLevel(original_level)
