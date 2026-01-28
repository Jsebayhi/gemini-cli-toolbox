from flask import Blueprint, jsonify, request
from app.services.filesystem import FileSystemService
from app.services.launcher import LauncherService

api = Blueprint('api', __name__)

@api.route('/roots')
def get_roots():
    return jsonify({"roots": FileSystemService.get_roots()})

@api.route('/configs')
def get_configs():
    return jsonify({"configs": FileSystemService.get_configs()})

@api.route('/config-details')
def get_config_details():
    name = request.args.get('name', '')
    return jsonify(FileSystemService.get_config_details(name))

@api.route('/browse')
def browse():
    path = request.args.get('path', '')
    try:
        data = FileSystemService.browse(path)
        return jsonify(data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/launch', methods=['POST'])
def launch():
    data = request.json or {}
    project_path = data.get('project_path')
    config_profile = data.get('config_profile')
    session_type = data.get('session_type', 'cli')
    
    if not project_path:
        return jsonify({"error": "Project path required"}), 400
        
    try:
        result = LauncherService.launch(project_path, config_profile, session_type)
        if result["returncode"] == 0:
            result["status"] = "success"
            return jsonify(result)
        else:
            result["status"] = "error"
            # Map stderr to error field for frontend compatibility
            result["error"] = result["stderr"] or result["stdout"]
            return jsonify(result), 500
    except PermissionError as e:
        return jsonify({"status": "error", "error": str(e)}), 403
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500
