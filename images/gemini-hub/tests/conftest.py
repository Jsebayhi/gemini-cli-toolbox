import pytest
from app import create_app
from app.config import Config

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Override config for testing
    class TestConfig(Config):
        TESTING = True
        # Mock paths to avoid hitting real disk
        HUB_ROOTS = ["/mock/root"]
        HOST_CONFIG_ROOT = "/mock/config"
        TAILSCALE_AUTH_KEY = "mock-key"
        HUB_AUTO_SHUTDOWN = False

    app = create_app(TestConfig)
    yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's CLI commands."""
    return app.test_cli_runner()
