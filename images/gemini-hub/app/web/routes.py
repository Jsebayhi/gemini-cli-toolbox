from flask import Blueprint, render_template
from app.services.tailscale import TailscaleService

web = Blueprint('web', __name__)

@web.route('/')
def home():
    status = TailscaleService.get_status()
    machines = TailscaleService.parse_peers(status)
    return render_template('index.html', machines=machines)
