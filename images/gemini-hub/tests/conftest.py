import pytest
import threading
import logging
from typing import Generator
from flask import Flask
from werkzeug.serving import make_server
from app import create_app
from app.config import Config
from tests.ui.pages import HubPage

@pytest.fixture
def app(monkeypatch: pytest.MonkeyPatch) -> Flask:
    """Create and configure a new app instance for each test."""
    monkeypatch.setattr(Config, "HUB_ROOTS", ["/mock/root"])
    monkeypatch.setattr(Config, "HOST_CONFIG_ROOT", "/mock/config")
    monkeypatch.setattr(Config, "TAILSCALE_AUTH_KEY", "mock-key")
    monkeypatch.setattr(Config, "HUB_AUTO_SHUTDOWN", False)

    app = create_app(Config)
    return app

@pytest.fixture
def client(app: Flask):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture(scope="session")
def runner(app: Flask):
    """A test runner for the app's CLI commands."""
    return app.test_cli_runner()

@pytest.fixture
def live_server_url(app: Flask) -> Generator[str, None, None]:
    """Start a live server in a separate thread for UI testing."""
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
def hub(page, live_server_url: str) -> HubPage:
    """Fixture to provide a HubPage POM instance."""
    return HubPage(page, live_server_url)

@pytest.fixture
def suppress_logs():
    """Fixture to suppress common expected log errors during tests."""
    logger = logging.getLogger("app.services.tailscale")
    original_level = logger.level
    logger.setLevel(logging.CRITICAL)
    yield
    logger.setLevel(original_level)

@pytest.fixture(autouse=True)
def _auto_tracing(context: Generator, request: pytest.FixtureRequest):
    """Automatically start tracing for every UI test and save on failure."""
    # This fixture only applies to tests that use 'page' (UI tests)
    if "page" not in request.fixturenames:
        yield
        return

    # Start tracing
    context = request.getfixturevalue("context")
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    
    yield
    
    # Save trace ONLY on failure
    if request.node.rep_call.failed:
        test_name = request.node.name.replace("[", "-").replace("]", "-")
        context.tracing.stop(path=f"test-results/trace-{test_name}.zip")
    else:
        context.tracing.stop()

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to catch test failure status for the auto_tracing fixture."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)
