"""
Central API Contract Definitions (JSON Schema).
Ensures consistency between backend responses and frontend expectations.
"""

BROWSE_SCHEMA = {
    "type": "object",
    "properties": {
        "directories": {"type": "array", "items": {"type": "string"}},
        "files": {"type": "array", "items": {"type": "string"}},
        "path": {"type": "string"}
    },
    "required": ["directories", "path"],
    "additionalProperties": False
}

ROOTS_SCHEMA = {
    "type": "object",
    "properties": {
        "roots": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["roots"]
}

LAUNCH_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {"enum": ["success", "error"]},
        "command": {"type": "string"},
        "stdout": {"type": "string"},
        "stderr": {"type": "string"},
        "returncode": {"type": "integer"}
    },
    "required": ["status"]
}
