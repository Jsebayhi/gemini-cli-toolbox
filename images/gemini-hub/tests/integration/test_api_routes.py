import pytest
from unittest.mock import patch, MagicMock

# --- FileSystem Tests ---

def test_get_roots(client):
    """Test retrieving allowed workspace roots."""
    response = client.get('/api/roots')
    assert response.status_code == 200
    assert response.json == {"roots": ["/mock/root"]}

def test_browse_success(client):
    """Test browsing a valid directory."""
    with patch("os.path.isdir", return_value=True), \
         patch("os.listdir", return_value=["project1", ".git", "file.txt"]):
        
        # We must use a path inside the mock root
        response = client.get('/api/browse?path=/mock/root')
        
        assert response.status_code == 200
        data = response.json
        assert "directories" in data
        assert "project1" in data["directories"]
        assert ".git" not in data["directories"] # Hidden files filtered

def test_browse_access_denied(client):
    """Test browsing outside allowed roots."""
    response = client.get('/api/browse?path=/etc')
    assert response.status_code == 403

def test_browse_not_found(client):
    """Test browsing a non-existent directory."""
    with patch("os.path.isdir", return_value=False):
        response = client.get('/api/browse?path=/mock/root/missing')
        assert response.status_code == 404

def test_browse_missing_param(client):
    """Test browsing without path parameter."""
    response = client.get('/api/browse')
    assert response.status_code == 400

# --- Config Tests ---

def test_get_configs(client):
    """Test listing configuration profiles."""
    # Mock os.listdir on HOST_CONFIG_ROOT
    with patch("os.path.isdir", return_value=True), \
         patch("os.listdir", return_value=["profile1", "profile2", "file.txt"]):
        
        # We also need to mock os.path.isdir for the filter check inside listdir loop
        def isdir_side_effect(path):
            return "file.txt" not in path
            
        with patch("os.path.isdir", side_effect=isdir_side_effect):
            response = client.get('/api/configs')
            
            assert response.status_code == 200
            assert "configs" in response.json
            assert "profile1" in response.json["configs"]
            assert "file.txt" not in response.json["configs"]

def test_get_config_details(client):
    """Test reading profile details."""
    mock_content = "--full\n--volume /data:/data"
    with patch("os.path.isfile", return_value=True), \
         patch("builtins.open", new_callable=MagicMock) as mock_open:
        
        mock_file = MagicMock()
        mock_file.__enter__.return_value = mock_content.splitlines()
        mock_open.return_value = mock_file
        
        response = client.get('/api/config-details?name=profile1')
        
        assert response.status_code == 200
        assert "extra_args" in response.json
        assert "--full" in response.json["extra_args"]

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
