import subprocess
import logging
from app.services.prune import PruneService

def test_prune_sidecars_logic(mocker):
    """Test Layer 2 sidecar pruning logic."""
    
    # 1. Mock 'docker ps' output showing 2 sidecars
    # Format: ID|ParentName
    mock_ps_output = "sc1|gem-parent-1\nsc2|gem-parent-2"
    
    def mock_run(cmd, **kwargs):
        class MockResult:
            def __init__(self, code, stdout=""):
                self.returncode = code
                self.stdout = stdout
        
        # docker ps
        if "ps" in cmd and "label=com.gemini.role=sidecar" in cmd:
            return MockResult(0, mock_ps_output)
            
        # docker inspect
        if "inspect" in cmd:
            if "gem-parent-1" in cmd:
                return MockResult(0, "false") # Parent exists but NOT running
            if "gem-parent-2" in cmd:
                return MockResult(0, "true") # Parent IS running
            return MockResult(1, "no such object") # Parent missing
            
        # docker rm
        if "rm" in cmd:
            return MockResult(0)
            
        return MockResult(0)

    mock_subprocess = mocker.patch("subprocess.run", side_effect=mock_run)
    
    # Run pruning
    PruneService.prune_sidecars()
    
    # Verify calls
    # Should call rm for sc1 (parent not running)
    # Should NOT call rm for sc2 (parent running)
    
    rm_calls = [call for call in mock_subprocess.call_args_list if "rm" in call[0][0]]
    assert len(rm_calls) == 1
    assert "sc1" in rm_calls[0][0][0]
    assert "sc2" not in rm_calls[0][0][0]

def test_prune_sidecars_exception_handling(mocker):
    """Test that pruning doesn't crash on subprocess errors."""
    mocker.patch("subprocess.run", side_effect=Exception("Docker down"))
    
    # Should not raise exception
    PruneService.prune_sidecars()

def test_prune_sidecars_empty(mocker):
    """Test with no sidecars found."""
    class MockResult:
        def __init__(self, code, stdout=""):
            self.returncode = code
            self.stdout = stdout
            
    mocker.patch("subprocess.run", return_value=MockResult(0, ""))
    
    # Should not crash
    PruneService.prune_sidecars()
