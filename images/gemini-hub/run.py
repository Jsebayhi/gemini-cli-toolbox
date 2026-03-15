from app import create_app
from app.services.monitor import MonitorService
from app.services.prune import PruneService

app = create_app()

if __name__ == '__main__':
    # Start background services
    MonitorService.start()
    PruneService.start()
    
    # Listen on all interfaces so the host (and mapped ports) can reach it
    app.run(host='0.0.0.0', port=8888)
