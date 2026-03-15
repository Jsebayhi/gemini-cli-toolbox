from flask import Blueprint, render_template
from app.services.discovery import DiscoveryService

web = Blueprint('web', __name__)

@web.route('/')
def home():
    machines = DiscoveryService().get_sessions()
    return render_template('index.html', machines=machines)
