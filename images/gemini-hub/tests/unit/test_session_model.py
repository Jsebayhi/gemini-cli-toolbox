from app.models.session import GeminiSession

def test_session_initialization():
    """Test standard GeminiSession initialization."""
    s = GeminiSession(
        name="gem-proj-cli-123",
        project="proj",
        session_type="cli",
        uid="123"
    )
    assert s.name == "gem-proj-cli-123"
    assert s.is_running is False
    assert s.is_reachable is False

def test_session_to_dict():
    """Test conversion of session to dictionary for API responses."""
    s = GeminiSession(
        name="gem-proj-cli-123",
        project="proj",
        session_type="cli",
        uid="123"
    )
    s.is_running = True
    
    d = s.to_dict()
    assert d["is_running"] is True
    assert d["is_reachable"] is False
    assert d["online"] is True

def test_session_from_name_standard():
    """Test parsing a standard session name."""
    s = GeminiSession.from_name("gem-my-project-bash-abc123")
    assert s is not None
    assert s.project == "my-project"
    assert s.session_type == "bash"
    assert s.uid == "abc123"

def test_session_from_name_invalid():
    """Ensure invalid names return None."""
    assert GeminiSession.from_name("not-a-gemini-session") is None
