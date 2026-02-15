import pytest
import threading
import logging
import socket
import time
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
    """Start a live server in a separate thread with socket synchronization."""
    server = make_server('127.0.0.1', 0, app)
    port = server.socket.getsockname()[1]
    
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    
    url = f"http://127.0.0.1:{port}"
    
    # Master Catch: Socket Synchronization
    # Poll the port until it is actually listening to avoid race conditions
    start_time = time.time()
    while time.time() - start_time < 2.0:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.1):
                break
        except (ConnectionRefusedError, socket.timeout):
            time.sleep(0.05)
    else:
        pytest.fail("Flask server failed to start within 2 seconds")
        
    yield url
    
    server.shutdown()
    thread.join()

@pytest.fixture(scope="session", autouse=True)
def _check_playwright_binaries():
    """Ensure browser binaries are installed before running UI tests (Developer UX)."""
    import subprocess
    try:
        # Check if chromium is available via playwright cli
        subprocess.run(["playwright", "install", "--dry-run", "chromium"], 
                       capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        # We don't fail standard tests, only warn or let UI tests fail naturally
        # with a clear message if we were running them.
        pass

@pytest.fixture
def hub(page, live_server_url: str) -> HubPage:
    """Fixture to provide a HubPage POM instance with console monitoring."""
    errors = []
    def on_console(msg):
        if msg.type == "error":
            if "status of 403" in msg.text or "status of 500" in msg.text:
                return
            errors.append(msg.text)
            
    page.on("console", on_console)
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    
    hub_page = HubPage(page, live_server_url)
    yield hub_page
    
    if errors:
        pytest.fail(f"Test passed but JS console errors were detected: {errors}")

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
    if "page" not in request.fixturenames:
        yield
        return

    context = request.getfixturevalue("context")
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    
    yield
    
    if request.node.rep_call.failed:
        test_name = request.node.name.replace("[", "-").replace("]", "-")
        context.tracing.stop(path=f"test-results/trace-{test_name}.zip")
    else:
        context.tracing.stop()

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)
