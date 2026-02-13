from unittest.mock import patch

# --- FileSystem Tests ---

def test_get_roots(client):
    """Test retrieving allowed workspace roots."""
    with patch("app.config.Config.HUB_ROOTS", ["/real/root"]):
        response = client.get('/api/roots')
        assert response.status_code == 200
        assert response.json == {"roots": ["/real/root"]}

def test_browse_success(client, tmp_path):
    """Test browsing a valid directory."""
    # Setup: Create real FS structure
    root = tmp_path / "workspace"
    root.mkdir()
    (root / "project1").mkdir()
    (root / ".git").mkdir()
    (root / "file.txt").touch()

    # Patch Config to allow access to this root
    with patch("app.config.Config.HUB_ROOTS", [str(root)]):
        response = client.get(f'/api/browse?path={root}')
        
        assert response.status_code == 200
        data = response.json
        assert "directories" in data
        assert "project1" in data["directories"]
        assert ".git" not in data["directories"] # Hidden files filtered
        assert "file.txt" not in data["directories"] # Files filtered

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
        # Request a path that starts with root but doesn't exist
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
    # Setup: Create real FS structure
    (tmp_path / "profile1").mkdir()
    (tmp_path / "profile2").mkdir()
    (tmp_path / "file.txt").touch()

    with patch("app.config.Config.HOST_CONFIG_ROOT", str(tmp_path)):
        response = client.get('/api/configs')
        
        assert response.status_code == 200
        assert "configs" in response.json
        assert "profile1" in response.json["configs"]
        assert "file.txt" not in response.json["configs"]

def test_get_config_details(client, tmp_path):
    """Test reading profile details."""
    # Setup: Create real profile and file
    profile_dir = tmp_path / "profile1"
    profile_dir.mkdir()
    (profile_dir / "extra-args").write_text("--preview\n--volume /data:/data")

    with patch("app.config.Config.HOST_CONFIG_ROOT", str(tmp_path)):
        response = client.get('/api/config-details?name=profile1')
        
        assert response.status_code == 200
        assert "extra_args" in response.json
        assert "--preview" in response.json["extra_args"]

# --- Launcher Tests ---

def test_launch_success(client):
    """Test successful session launch."""
    with patch("subprocess.run") as mock_run:
        # Configure mock success
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = ">> Container started: gem-test-cli-123"
        mock_run.return_value.stderr = ""

        payload = {
            "project_path": "/mock/root/my-project",
            "config_profile": "work",
            "session_type": "bash"
        }
        
        response = client.post('/api/launch', json=payload)
        
        assert response.status_code == 200
        assert response.json["status"] == "success"
        
        # Verify call args
        args, kwargs = mock_run.call_args
        cmd = args[0]
        assert "gemini-toolbox" in cmd
        assert "--bash" in cmd # Session type
        assert "--profile" in cmd # Config profile
        assert "GEMINI_REMOTE_KEY" in kwargs["env"] # Auth key passed

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
        
        # Verify call args
        args, _ = mock_run.call_args
        cmd = args[0]
        assert "--" in cmd
        assert "do something autonomous" in cmd

def test_launch_full_options(client):
    """Test launch with all parity options (preview + no-docker + worktree + custom image + docker args)."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = ">> Container started"
        mock_run.return_value.stderr = ""

        payload = {
            "project_path": "/mock/root/project",
            "image_variant": "preview",
            "docker_enabled": False,
            "ide_enabled": False,
            "worktree_mode": True,
            "worktree_name": "feat/api",
            "custom_image": "my-custom-image:latest",
            "docker_args": "-v /data:/data"
        }
        
        response = client.post('/api/launch', json=payload)
        
        assert response.status_code == 200
        assert response.json["status"] == "success"
        
        # Verify call args
        args, _ = mock_run.call_args
        cmd = args[0]
        # custom_image overrides preview
        assert "--image" in cmd
        assert "my-custom-image:latest" in cmd
        assert "--preview" not in cmd
        
        assert "--no-docker" in cmd
        assert "--no-ide" in cmd
        assert "--worktree" in cmd
        assert "--name" in cmd
        assert "feat/api" in cmd
        assert "--docker-args" in cmd
        assert "-v /data:/data" in cmd

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
        assert "Docker error" in response.json["error"]

# --- Tailscale/Resolve Tests ---

def test_resolve_local_url_success(client):
    """Test resolving a local URL for a valid hostname."""
    mock_containers = [{"name": "gem-test", "local_url": "http://localhost:1234"}]
    with patch("app.services.discovery.DiscoveryService.get_local_containers", return_value=mock_containers):
        response = client.get('/api/resolve-local-url?hostname=gem-test')
        assert response.status_code == 200
        assert response.json["url"] == "http://localhost:1234"

def test_resolve_local_url_not_found(client):
    """Test resolving a hostname that has no local mapping."""
    with patch("app.services.discovery.DiscoveryService.get_local_containers", return_value=[]):
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

        mock_run.assert_called_with(["docker", "stop", "gem-test"], capture_output=True, text=True, timeout=30)



def test_stop_session_invalid_id(client):

    """Test stop rejection for invalid ID."""

    response = client.post('/api/sessions/stop', json={"session_id": "not-gem-id"})

    assert response.status_code == 403



def test_stop_session_missing_param(client):



    """Test stop without session_id."""



    response = client.post('/api/sessions/stop', json={})



    assert response.status_code == 400







def test_browse_permission_error(client):



    with patch("app.services.filesystem.FileSystemService.browse", side_effect=PermissionError("Denied")):



        res = client.get('/api/browse?path=/restricted')



        assert res.status_code == 403







def test_launch_permission_error(client):



    with patch("app.services.launcher.LauncherService.launch", side_effect=PermissionError("Forbidden")):



        res = client.post('/api/launch', json={"project_path": "/restricted"})



        assert res.status_code == 403







def test_launch_generic_exception(client):



    with patch("app.services.launcher.LauncherService.launch", side_effect=Exception("Internal error")):



        res = client.post('/api/launch', json={"project_path": "/some/path"})



        assert res.status_code == 500







def test_stop_session_permission_error(client):



    with patch("app.services.session.SessionService.stop", side_effect=PermissionError("Cannot stop")):



        res = client.post('/api/sessions/stop', json={"session_id": "gem-target"})



        assert res.status_code == 403







def test_stop_session_generic_exception(client):



    with patch("app.services.session.SessionService.stop", side_effect=Exception("Failed")):



        res = client.post('/api/sessions/stop', json={"session_id": "gem-target"})



        assert res.status_code == 500




