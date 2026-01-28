import pytest
from unittest.mock import patch, MagicMock
from app.services.filesystem import FileSystemService

def test_get_configs_error():
    """Test handling of directory listing error."""
    with patch("os.path.isdir", return_value=True), \
         patch("os.listdir", side_effect=PermissionError("Denied")), \
         patch("app.services.filesystem.logger") as mock_logger:
        
        configs = FileSystemService.get_configs()
        assert configs == []
        assert mock_logger.error.called

def test_get_config_details_error():
    """Test handling of file reading error."""
    with patch("os.path.join", return_value="/mock/path"), \
         patch("os.path.isfile", return_value=True), \
         patch("builtins.open", side_effect=IOError("Read failed")), \
         patch("app.services.filesystem.logger") as mock_logger:
        
        details = FileSystemService.get_config_details("profile1")
        assert details == {"extra_args": []}
        assert mock_logger.error.called
