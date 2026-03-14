import pytest
import os
from app.services.filesystem import FileSystemService
from app.config import Config
from unittest.mock import patch

def test_is_safe_path_success():
    """Test safe path detection."""
    with patch.object(Config, "HUB_ROOTS", ["/work"]):
        assert FileSystemService.is_safe_path("/work/project") is True
        assert FileSystemService.is_safe_path("/work/../outside") is False

def test_get_roots():
    """Test retrieval of scannable roots."""
    with patch.object(Config, "HUB_ROOTS", ["/a", "/b"]):
        roots = FileSystemService.get_roots()
        assert "/a" in roots
        assert "/b" in roots

def test_browse_not_dir():
    """Test browsing a path that isn't a directory."""
    with patch("os.path.isdir", return_value=False), \
         patch("app.services.filesystem.FileSystemService.is_safe_path", return_value=True):
        with pytest.raises(FileNotFoundError):
            FileSystemService.browse("/some/file")

def test_create_directory_already_exists(tmp_path):
    """Test creating a directory that already exists."""
    parent = tmp_path / "parent"
    parent.mkdir()
    child = parent / "exists"
    child.mkdir()
    
    with patch("app.services.filesystem.FileSystemService.is_safe_path", return_value=True):
        with pytest.raises(FileExistsError):
            FileSystemService.create_directory(str(parent), "exists")

def test_get_configs_logic(tmp_path):
    """Test configuration scanning logic."""
    config_root = tmp_path / "configs"
    config_root.mkdir()
    (config_root / "profile1").mkdir()
    (config_root / "not-a-dir").touch()
    
    with patch.object(Config, "HOST_CONFIG_ROOT", str(config_root)):
        configs = FileSystemService.get_configs()
        # get_configs returns a list of strings (names)
        assert len(configs) == 1
        assert configs[0] == "profile1"

def test_get_config_details_complex(tmp_path):
    """Test parsing of complex extra-args."""
    config_root = tmp_path / "configs"
    config_root.mkdir()
    profile = config_root / "p1"
    profile.mkdir()
    (profile / "extra-args").write_text("--env 'A=B' # env var\n\n# final comment")
    
    with patch.object(Config, "HOST_CONFIG_ROOT", str(config_root)):
        res = FileSystemService.get_config_details("p1")
        args = res["extra_args"]
        # shlex strips quotes by default
        assert args[0]["arg"] == "--env A=B"
        assert args[0]["comment"] == "env var"
        assert args[1]["type"] == "blank"
        assert args[2]["type"] == "comment"

def test_create_directory_already_exists_logic(tmp_path):
    """Test FileExistsError handling."""
    root = tmp_path / "work"
    root.mkdir()
    (root / "dup").mkdir()
    
    with patch("app.services.filesystem.FileSystemService.is_safe_path", return_value=True):
        with pytest.raises(FileExistsError):
            FileSystemService.create_directory(str(root), "dup")

def test_get_config_details_logic(tmp_path):
    """Test parsing of extra-args file."""
    config_root = tmp_path / "configs"
    config_root.mkdir()
    profile = config_root / "profile1"
    profile.mkdir()
    
    extra_args = profile / "extra-args"
    extra_args.write_text("# Comment\n\n--flag arg # flag comment\n")
    
    with patch.object(Config, "HOST_CONFIG_ROOT", str(config_root)):
        details = FileSystemService.get_config_details("profile1")
        lines = details["extra_args"]
        assert len(lines) == 3
        assert lines[0]["type"] == "comment"
        assert lines[1]["type"] == "blank"
        assert lines[2]["type"] == "arg"
        assert "--flag arg" in lines[2]["arg"]
        assert lines[2]["comment"] == "flag comment"

def test_create_directory_security_logic():
    """Test security checks in create_directory."""
    with patch("app.services.filesystem.FileSystemService.is_safe_path", return_value=False):
        with pytest.raises(PermissionError):
            FileSystemService.create_directory("/forbidden", "new")

def test_create_directory_invalid_name_logic():
    """Test sanitization in create_directory."""
    with patch("app.services.filesystem.FileSystemService.is_safe_path", return_value=True), \
         patch("os.path.isdir", return_value=True):
        with pytest.raises(ValueError):
            FileSystemService.create_directory("/work", "invalid/name")
        with pytest.raises(ValueError):
            FileSystemService.create_directory("/work", "..")

def test_browse_logic(tmp_path):
    """Test detailed browsing results."""
    root = tmp_path / "work"
    root.mkdir()
    (root / "dir1").mkdir()
    (root / "file1").touch()

    with patch.object(Config, "HUB_ROOTS", [str(root)]):
        res = FileSystemService.browse(str(root))
        assert res["path"] == str(root)
        # Should only list directories
        assert len(res["directories"]) == 1
        assert res["directories"][0] == "dir1"

def test_create_directory_logic(tmp_path):
    """Test directory creation with parent path."""
    root = tmp_path / "work"
    root.mkdir()
    
    with patch("app.services.filesystem.FileSystemService.is_safe_path", return_value=True):
        new_path = FileSystemService.create_directory(str(root), "new-project")
        assert os.path.exists(new_path)
        assert "new-project" in new_path
