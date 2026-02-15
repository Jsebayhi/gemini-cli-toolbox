from unittest.mock import patch
from jsonschema import validate
from tests.contracts import ROOTS_SCHEMA, BROWSE_SCHEMA, LAUNCH_SCHEMA

# --- FileSystem Tests ---

def test_get_roots(client):
    """Test retrieving allowed workspace roots and verify contract."""
    with patch("app.config.Config.HUB_ROOTS", ["/real/root"]):
        response = client.get('/api/roots')
        assert response.status_code == 200
        validate(instance=response.json, schema=ROOTS_SCHEMA)
        assert response.json == {"roots": ["/real/root"]}

def test_browse_success(client, tmp_path):
    """Test browsing a valid directory and verify contract."""
    root = tmp_path / "workspace"
    root.mkdir()
    (root / "project1").mkdir()
    (root / "file.txt").touch()

    with patch("app.config.Config.HUB_ROOTS", [str(root)]):
        response = client.get(f'/api/browse?path={root}')
        
        assert response.status_code == 200
        validate(instance=response.json, schema=BROWSE_SCHEMA)
        assert "project1" in response.json["directories"]

def test_browse_access_denied(client, tmp_path):
    """Test browsing outside allowed roots."""
    root = tmp_path / "allowed"
    root.mkdir()
    
    with patch("app.config.Config.HUB_ROOTS", [str(root)]):
        response = client.get('/api/browse?path=/etc')
        assert response.status_code == 403

def test_browse_not_found(client, tmp_path):
    """Test browsing a non-existent directory."""
    root = tmp_path / "workspace"
    root.mkdir()
    
    with patch("app.config.Config.HUB_ROOTS", [str(root)]):
        missing_path = root / "missing"
        response = client.get(f'/api/browse?path={missing_path}')
        assert response.status_code == 404

def test_browse_missing_param(client):
    """Test browsing without path parameter."""
    response = client.get('/api/browse')
    assert response.status_code == 400

# --- Config Tests ---

def test_get_configs(client, tmp_path):
    """Test listing configuration profiles."""
    (tmp_path / "profile1").mkdir()

    with patch("app.config.Config.HOST_CONFIG_ROOT", str(tmp_path)):
        response = client.get('/api/configs')
        assert response.status_code == 200
        assert "profile1" in response.json["configs"]

def test_get_config_details(client, tmp_path):
    """Test reading profile details."""
    profile_dir = tmp_path / "profile1"
    profile_dir.mkdir()
    (profile_dir / "extra-args").write_text("--preview")

    with patch("app.config.Config.HOST_CONFIG_ROOT", str(tmp_path)):
        response = client.get('/api/config-details?name=profile1')
        assert response.status_code == 200
        assert "--preview" in response.json["extra_args"]

# --- Launcher Tests ---

def test_launch_success(client):
    """Test successful session launch and verify contract."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = ">> Container started: gem-test-cli-123"
        mock_run.return_value.stderr = ""

        payload = {
            "project_path": "/mock/root/my-project",
            "session_type": "bash"
        }
        
        response = client.post('/api/launch', json=payload)
        
        assert response.status_code == 200
        validate(instance=response.json, schema=LAUNCH_SCHEMA)
        assert response.json["status"] == "success"

def test_launch_with_task_api(client):
    """Test API launch with an autonomous task."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Bot started"
        mock_run.return_value.stderr = ""

        payload = {
            "project_path": "/mock/root/project",
            "task": "do something autonomous"
        }
        
        response = client.post('/api/launch', json=payload)
        assert response.status_code == 200
        assert response.json["status"] == "success"

def test_launch_full_options(client):
    """Test launch with all parity options."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = ">> Container started"
        mock_run.return_value.stderr = ""

        payload = {
            "project_path": "/mock/root/project",
            "image_variant": "preview",
            "worktree_mode": True,
            "worktree_name": "feat/api"
        }
        
        response = client.post('/api/launch', json=payload)
        assert response.status_code == 200
        assert response.json["status"] == "success"

def test_launch_failure_permission(client):
    """Test launch rejection for unauthorized path."""
    payload = {"project_path": "/unauthorized/path"}
    response = client.post('/api/launch', json=payload)
    assert response.status_code == 403

def test_launch_failure_subprocess(client):
    """Test handling of subprocess failure."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "Docker error"
        mock_run.return_value.stdout = ""
        
        payload = {"project_path": "/mock/root/project"}
        response = client.post('/api/launch', json=payload)
        
        assert response.status_code == 500
        assert response.json["status"] == "error"
        validate(instance=response.json, schema=LAUNCH_SCHEMA)

# --- Tailscale/Resolve Tests ---

def test_resolve_local_url_success(client):
    """Test resolving a local URL for a valid hostname."""
    with patch("app.services.tailscale.TailscaleService.get_local_ports") as mock_ports:
        mock_ports.return_value = {"gem-test": "http://localhost:1234"}
        
        response = client.get('/api/resolve-local-url?hostname=gem-test')
        assert response.status_code == 200
        assert response.json["url"] == "http://localhost:1234"

def test_resolve_local_url_not_found(client):
    """Test resolving a hostname that has no local mapping."""
    with patch("app.services.tailscale.TailscaleService.get_local_ports") as mock_ports:
        mock_ports.return_value = {}
        
        response = client.get('/api/resolve-local-url?hostname=gem-test')
        assert response.status_code == 200
        assert response.json["url"] is None

def test_resolve_local_url_missing_param(client):
    """Test resolving without hostname parameter."""
    response = client.get('/api/resolve-local-url')
    assert response.status_code == 200
    assert response.json["url"] is None

# --- Session Lifecycle Tests ---

def test_stop_session_success(client):
    """Test successful session stop."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "gem-test"
        
        response = client.post('/api/sessions/stop', json={"session_id": "gem-test"})
        
        assert response.status_code == 200
        assert response.json["status"] == "success"

def test_stop_session_invalid_id(client):
    """Test stop rejection for invalid ID."""
    response = client.post('/api/sessions/stop', json={"session_id": "not-gem-id"})
    assert response.status_code == 403

def test_stop_session_missing_param(client):
    """Test stop without session_id."""
    response = client.post('/api/sessions/stop', json={})
    assert response.status_code == 400
