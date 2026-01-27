from flask import Flask
from app.config import Config
from app.web.routes import web
from app.api.routes import api
from app.services.monitor import MonitorService

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Validate critical config
    config_class.validate()
    
    # Register Blueprints
    app.register_blueprint(web)
    app.register_blueprint(api, url_prefix='/api')
    
    # Start background services
    # Note: In development with reloader, this might start twice. 
    # Production usage via gunicorn is preferred.
    MonitorService.start()
    
    return app
