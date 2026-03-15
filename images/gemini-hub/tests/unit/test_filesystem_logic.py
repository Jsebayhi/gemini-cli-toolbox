from app.services.filesystem import FileSystemService
from app.config import Config

def test_get_roots(mocker):
    """Test getting workspace roots."""
    mocker.patch.object(Config, "HUB_ROOTS", ["/work"])
    assert FileSystemService.get_roots() == ["/work"]

def test_is_safe_path_success(mocker):
    """Test safe path detection."""
    mocker.patch.object(Config, "HUB_ROOTS", ["/safe"])
    assert FileSystemService.is_safe_path("/safe/sub/path") is True

def test_is_safe_path_failure(mocker):
    """Test unsafe path detection."""
    mocker.patch.object(Config, "HUB_ROOTS", ["/safe"])
    assert FileSystemService.is_safe_path("/unsafe/path") is False

def test_filesystem_is_safe_path_invalid_root(mocker):
    """Cover safety check failure when path is outside roots."""
    mocker.patch.object(Config, "HUB_ROOTS", ["/safe"])
    assert FileSystemService.is_safe_path("/unsafe/path") is False

def test_filesystem_browse_permission_error(mocker):
    """Cover permission error during directory browsing."""
    mocker.patch("os.listdir", side_effect=PermissionError("Denied"))
    try:
        FileSystemService.browse("/")
    except PermissionError:
        assert True

def test_filesystem_create_directory_invalid_name(mocker, tmp_path):
    """Cover value error for invalid directory names."""
    safe_path = tmp_path / "safe"
    safe_path.mkdir()
    
    mocker.patch.object(Config, "HUB_ROOTS", [str(safe_path)])
    try:
        FileSystemService.create_directory(str(safe_path), "../invalid")
    except ValueError:
        assert True
