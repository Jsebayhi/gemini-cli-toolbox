from flask import Flask
from app.config import Config

def create_app():
    app = Flask(__name__)
    
    # Initialize Config
    Config.validate()
    
    # Register Blueprints
    from app.web.routes import web
    from app.api.routes import api
    
    app.register_blueprint(web)
    app.register_blueprint(api, url_prefix='/api')
    
    return app
