from unittest.mock import patch

def test_get_roots(client):
    """Test getting workspace roots."""
    with patch("app.api.routes.FileSystemService.get_roots", return_value=["/work"]):
        response = client.get('/api/roots')
        assert response.status_code == 200
        assert response.json == {"roots": ["/work"]}

def test_get_configs(client):
    """Test getting configuration profiles."""
    with patch("app.api.routes.FileSystemService.get_configs", return_value=[{"name": "default"}]):
        response = client.get('/api/configs')
        assert response.status_code == 200
        assert response.json == {"configs": [{"name": "default"}]}

def test_get_config_details(client):
    """Test getting configuration details."""
    with patch("app.api.routes.FileSystemService.get_config_details", return_value={"name": "default"}):
        response = client.get('/api/config-details?name=default')
        assert response.status_code == 200
        assert response.json == {"name": "default"}

def test_browse_success(client):
    """Test directory browsing."""
    mock_data = {"current_path": "/work", "items": []}
    with patch("app.api.routes.FileSystemService.browse", return_value=mock_data):
        response = client.get('/api/browse?path=/work')
        assert response.status_code == 200
        assert response.json == mock_data

def test_browse_access_denied(client):
    """Test directory browsing with permission error."""
    with patch("app.api.routes.FileSystemService.browse", side_effect=PermissionError("Access denied")):
        response = client.get('/api/browse?path=/root')
        assert response.status_code == 403
        assert response.json == {"error": "Access denied"}

def test_browse_not_found(client):
    """Test directory browsing with not found error."""
    with patch("app.api.routes.FileSystemService.browse", side_effect=FileNotFoundError("Not found")):
        response = client.get('/api/browse?path=/invalid')
        assert response.status_code == 404
        assert response.json == {"error": "Not found"}

def test_browse_missing_param(client):
    """Test directory browsing with missing path parameter."""
    response = client.get('/api/browse')
    assert response.status_code == 400
    assert "error" in response.json

def test_create_directory_success(client):
    """Test creating a directory."""
    with patch("app.api.routes.FileSystemService.create_directory", return_value="/work/new"):
        response = client.post('/api/create-directory', json={"parent_path": "/work", "name": "new"})
        assert response.status_code == 200
        assert response.json == {"status": "success", "path": "/work/new"}

def test_create_directory_invalid_name(client):
    """Test creating a directory with invalid name."""
    with patch("app.api.routes.FileSystemService.create_directory", side_effect=ValueError("Invalid name")):
        response = client.post('/api/create-directory', json={"parent_path": "/work", "name": ""})
        assert response.status_code == 400
        assert response.json == {"error": "Invalid name"}

def test_create_directory_already_exists(client):
    """Test creating a directory that already exists."""
    with patch("app.api.routes.FileSystemService.create_directory", side_effect=FileExistsError("Already exists")):
        response = client.post('/api/create-directory', json={"parent_path": "/work", "name": "exists"})
        assert response.status_code == 409
        assert response.json == {"error": "Already exists"}

def test_create_directory_access_denied(client):
    """Test creating a directory with permission error."""
    with patch("app.api.routes.FileSystemService.create_directory", side_effect=PermissionError("Access denied")):
        response = client.post('/api/create-directory', json={"parent_path": "/root", "name": "new"})
        assert response.status_code == 403
        assert response.json == {"error": "Access denied"}

def test_launch_success(client):
    """Test launching a session."""
    mock_result = {"returncode": 0, "stdout": "Success", "stderr": "", "command": "...", "status": "success"}
    with patch("app.api.routes.LauncherService.launch", return_value=mock_result):
        response = client.post('/api/launch', json={"project_path": "/work"})
        assert response.status_code == 200
        assert response.json["status"] == "success"

def test_launch_with_task_api(client):
    """Test launching a session with a task."""
    mock_result = {"returncode": 0, "stdout": "Task started", "stderr": "", "command": "...", "status": "success"}
    with patch("app.api.routes.LauncherService.launch", return_value=mock_result):
        response = client.post('/api/launch', json={"project_path": "/work", "task": "test task"})
        assert response.status_code == 200
        assert response.json["status"] == "success"

def test_launch_full_options(client):
    """Test launching with all options."""
    mock_result = {"returncode": 0, "stdout": "Full options", "stderr": "", "command": "...", "status": "success"}
    with patch("app.api.routes.LauncherService.launch", return_value=mock_result):
        response = client.post('/api/launch', json={
            "project_path": "/work",
            "config_profile": "work",
            "session_type": "cli",
            "task": "test",
            "interactive": False,
            "image_variant": "preview",
            "docker_enabled": False,
            "ide_enabled": False,
            "worktree_mode": True,
            "worktree_name": "feat",
            "custom_image": "my-img",
            "docker_args": "-v /tmp:/tmp"
        })
        assert response.status_code == 200
        assert response.json["status"] == "success"

def test_launch_failure_permission(client):
    """Test launching with permission error."""
    with patch("app.api.routes.LauncherService.launch", side_effect=PermissionError("Not allowed")):
        response = client.post('/api/launch', json={"project_path": "/work"})
        assert response.status_code == 403
        assert response.json == {"status": "error", "error": "Not allowed"}

def test_launch_failure_subprocess(client):
    """Test launching with subprocess failure."""
    mock_result = {"returncode": 1, "stdout": "", "stderr": "Command failed", "command": "...", "status": "error"}
    with patch("app.api.routes.LauncherService.launch", return_value=mock_result):
        response = client.post('/api/launch', json={"project_path": "/work"})
        assert response.status_code == 500
        assert response.json["status"] == "error"
        assert response.json["error"] == "Command failed"

def test_resolve_local_url_success(client):
    """Test resolving a local URL for a valid hostname."""
    s = {
        "name": "gem-app-cli-123",
        "local_url": "http://localhost:32768"
    }
    
    with patch("app.api.routes.DiscoveryService.get_sessions", return_value=[s]):
        response = client.get('/api/resolve-local-url?hostname=gem-app-cli-123')
        assert response.status_code == 200
        assert response.json == {"url": "http://localhost:32768"}

def test_resolve_local_url_not_found(client):
    """Test resolving a hostname that has no local mapping."""
    with patch("app.api.routes.DiscoveryService.get_sessions", return_value=[]):
        response = client.get('/api/resolve-local-url?hostname=gem-app-cli-123')
        assert response.status_code == 200
        assert response.json == {"url": None}

def test_resolve_local_url_missing_param(client):
    """Test resolving local URL with missing hostname parameter."""
    response = client.get('/api/resolve-local-url')
    assert response.status_code == 200
    assert response.json == {"url": None}

def test_stop_session_success(client):
    """Test stopping a session."""
    with patch("app.api.routes.SessionService.stop", return_value={"status": "success"}):
        response = client.post('/api/sessions/stop', json={"session_id": "gem-app-cli-123"})
        assert response.status_code == 200
        assert response.json == {"status": "success"}

def test_stop_session_invalid_id(client):
    """Test stopping a session with invalid ID."""
    with patch("app.api.routes.SessionService.stop", return_value={"status": "error", "error": "Not found"}):
        response = client.post('/api/sessions/stop', json={"session_id": "invalid"})
        assert response.status_code == 500
        assert response.json == {"status": "error", "error": "Not found"}

def test_stop_session_missing_param(client):
    """Test stopping a session with missing ID."""
    response = client.post('/api/sessions/stop', json={})
    assert response.status_code == 400
    assert response.json == {"error": "Session ID required"}
