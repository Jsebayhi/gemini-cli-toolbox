from unittest.mock import patch
from app.services.filesystem import FileSystemService
from app.config import Config

def test_get_roots():
    """Test retrieving configured workspace roots."""
    with patch.object(Config, "HUB_ROOTS", ["/root1", "/root2"]):
        roots = FileSystemService.get_roots()
        assert roots == ["/root1", "/root2"]

def test_is_safe_path_success():
    """Test that safe paths are correctly identified."""
    with patch.object(Config, "HUB_ROOTS", ["/safe"]):
        assert FileSystemService.is_safe_path("/safe/project") is True

def test_is_safe_path_failure():
    """Test that unsafe paths are correctly identified."""
    with patch.object(Config, "HUB_ROOTS", ["/safe"]):
        assert FileSystemService.is_safe_path("/unsafe/project") is False
