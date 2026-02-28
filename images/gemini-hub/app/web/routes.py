from flask import Blueprint, render_template
from app.services.tailscale import TailscaleService
from app.config import Config

web = Blueprint('web', __name__)

@web.route('/')
def home():
    status = TailscaleService.get_status()
    machines = TailscaleService.parse_peers(status)
    has_vpn_key = bool(Config.TAILSCALE_AUTH_KEY)
    return render_template('index.html', machines=machines, hub_no_vpn=Config.HUB_NO_VPN, has_vpn_key=has_vpn_key)
