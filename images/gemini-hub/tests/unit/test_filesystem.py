import pytest
from unittest.mock import patch
from app.services.filesystem import FileSystemService

def test_get_configs_real_fs(tmp_path):
    """Test listing configs using a real temporary filesystem."""
    # Setup: Create a directory structure
    (tmp_path / "profile1").mkdir()
    (tmp_path / "profile2").mkdir()
    (tmp_path / "file.txt").touch() # Should be ignored
    
    # Patch Config to point to tmp_path
    with patch("app.config.Config.HOST_CONFIG_ROOT", str(tmp_path)):
        configs = FileSystemService.get_configs()
        
        assert "profile1" in configs
        assert "profile2" in configs
        assert "file.txt" not in configs
        assert len(configs) == 2

def test_get_config_details_real_fs(tmp_path):
    """Test reading config details from a real file."""
    profile_dir = tmp_path / "work"
    profile_dir.mkdir()
    extra_args_file = profile_dir / "extra-args"
    extra_args_file.write_text("--preview\n\n# Comment\n--volume /foo:/bar")
    
    with patch("app.config.Config.HOST_CONFIG_ROOT", str(tmp_path)):
        details = FileSystemService.get_config_details("work")
        
        assert {"type": "arg", "raw": "--preview", "arg": "--preview", "comment": ""} in details["extra_args"]
        assert {"type": "blank", "raw": ""} in details["extra_args"]
        assert {"type": "comment", "raw": "# Comment", "arg": "", "comment": "Comment"} in details["extra_args"]
        assert {"type": "arg", "raw": "--volume /foo:/bar", "arg": "--volume /foo:/bar", "comment": ""} in details["extra_args"]

def test_get_config_details_with_eol_comments(tmp_path):
    """Test reading config details with complex end-of-line comments."""
    profile_dir = tmp_path / "work"
    profile_dir.mkdir()
    extra_args_file = profile_dir / "extra-args"
    extra_args_file.write_text(
        "--preview # use preview\n"
        "  # Whole line comment with spaces\n"
        "--volume \"/path with spaces:/data\" # comment\n"
        "--env FOO=\"#BAR\" # comment with hash in value"
    )
    
    with patch("app.config.Config.HOST_CONFIG_ROOT", str(tmp_path)):
        details = FileSystemService.get_config_details("work")
        
        # Verify extraction of both arg and comment while keeping original structure
        assert {"type": "arg", "raw": "--preview # use preview", "arg": "--preview", "comment": "use preview"} in details["extra_args"]
        assert {"type": "comment", "raw": "  # Whole line comment with spaces", "arg": "", "comment": "Whole line comment with spaces"} in details["extra_args"]
        assert {"type": "arg", "raw": "--volume \"/path with spaces:/data\" # comment", "arg": "--volume '/path with spaces:/data'", "comment": "comment"} in details["extra_args"]
        assert {"type": "arg", "raw": "--env FOO=\"#BAR\" # comment with hash in value", "arg": "--env 'FOO=#BAR'", "comment": "comment with hash in value"} in details["extra_args"]

def test_browse_real_fs(tmp_path):
    """Test browsing a directory structure."""
    root = tmp_path / "workspace"
    root.mkdir()
    (root / "project-a").mkdir()
    (root / ".hidden").mkdir() # Should be hidden
    (root / "README.md").touch() # Should be hidden (browse returns dirs only)
    
    # Patch HUB_ROOTS to allow access
    with patch("app.config.Config.HUB_ROOTS", [str(root)]):
        result = FileSystemService.browse(str(root))
        
        assert result["path"] == str(root)
        assert "project-a" in result["directories"]
        assert ".hidden" not in result["directories"]
        assert "README.md" not in result["directories"]

def test_browse_security_real_fs(tmp_path):
    """Test that browsing outside roots is denied."""
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    forbidden = tmp_path / "forbidden"
    forbidden.mkdir()
    
    with patch("app.config.Config.HUB_ROOTS", [str(allowed)]):
        # Access allowed
        FileSystemService.browse(str(allowed))
        
        # Access denied
        with pytest.raises(PermissionError):
            FileSystemService.browse(str(forbidden))

def test_get_configs_permission_error(tmp_path):
    """Test handling of permission errors on real FS."""
    # We simulate permission error by removing read permissions
    # Note: This might not work on all CI environments (e.g. root)
    # So we keep the Mock for error injection as it's cleaner for 'impossible' errors
    
    with (
        patch("app.config.Config.HOST_CONFIG_ROOT", str(tmp_path)),
        patch("os.listdir", side_effect=PermissionError("Denied")),
        patch("app.services.filesystem.logger") as mock_logger
    ):
        
        configs = FileSystemService.get_configs()
        assert configs == []
        assert mock_logger.error.called
