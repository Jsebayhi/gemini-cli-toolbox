from app import create_app

app = create_app()

if __name__ == '__main__':
    # Listen on all interfaces so the host (and mapped ports) can reach it
    app.run(host='0.0.0.0', port=8888)
