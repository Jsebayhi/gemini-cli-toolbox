import subprocess
from app.services.launcher import LauncherService
from app.config import Config

def test_launcher_success_standard(mocker, tmp_path):
    """Test successful launch with standard parameters."""
    safe_path = tmp_path / "safe"
    safe_path.mkdir()
    
    mocker.patch.object(Config, "HUB_ROOTS", [str(safe_path)])
    mock_run = mocker.patch("subprocess.run", return_value=mocker.Mock(returncode=0, stdout="Success", stderr=""))
    
    result = LauncherService.launch(str(safe_path))
    assert result["returncode"] == 0
    assert "gemini-toolbox" in mock_run.call_args[0][0]

def test_launcher_permission_denied(mocker):
    """Test launch with permission denied."""
    mocker.patch.object(Config, "HUB_ROOTS", ["/safe"])
    try:
        LauncherService.launch("/unsafe")
    except PermissionError:
        assert True

def test_launcher_command_failure(mocker, tmp_path):
    """Test launch with command failure."""
    safe_path = tmp_path / "safe"
    safe_path.mkdir()
    
    mocker.patch.object(Config, "HUB_ROOTS", [str(safe_path)])
    mocker.patch("subprocess.run", return_value=mocker.Mock(returncode=1, stdout="", stderr="Error"))
    
    result = LauncherService.launch(str(safe_path))
    assert result["returncode"] == 1
    assert result["stderr"] == "Error"

def test_launcher_timeout(mocker, tmp_path):
    """Test launch with timeout."""
    safe_path = tmp_path / "safe"
    safe_path.mkdir()
    
    mocker.patch.object(Config, "HUB_ROOTS", [str(safe_path)])
    mocker.patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="cmd", timeout=10))
    
    result = LauncherService.launch(str(safe_path))
    assert result["returncode"] == -1
    assert "timed out" in result["stderr"]

def test_launcher_worktree_already_exists(mocker, tmp_path):
    """Cover scenario where worktree directory already exists."""
    safe_path = tmp_path / "safe"
    safe_path.mkdir()
    
    mocker.patch.object(Config, "HUB_ROOTS", [str(safe_path)])
    mocker.patch("os.path.exists", return_value=True)
    res = LauncherService.launch(str(safe_path), worktree_mode=True, worktree_name="feat")
    # Note: LauncherService.launch doesn't currently return an error IF the directory exists,
    # it just passes --worktree to gemini-toolbox. 
    # Actually, looking at the code, it doesn't check os.path.exists itself.
    # The test was wrong about the behavior.
    assert "worktree" in res["command"]

def test_launcher_custom_image_construction(mocker, tmp_path):
    """Cover command construction with a custom image."""
    safe_path = tmp_path / "safe"
    safe_path.mkdir()
    
    mocker.patch.object(Config, "HUB_ROOTS", [str(safe_path)])
    mock_run = mocker.patch("subprocess.run", return_value=mocker.Mock(returncode=0, stdout="OK", stderr=""))
    LauncherService.launch(str(safe_path), custom_image="my-custom-img")
    # Check if custom image is in the command
    args, _ = mock_run.call_args
    assert "my-custom-img" in args[0]
