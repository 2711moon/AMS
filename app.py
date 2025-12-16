#app.py
from flask import Flask
from config import Config
from extensions import init_extensions
from routes import register_blueprints
from routes.export import start_backup_scheduler 

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    init_extensions(app)
    register_blueprints(app)

    start_backup_scheduler() 

    return app

if __name__ == '__main__':
    app = create_app()
    @app.route('/debug-session')
    def debug_session():
        from flask import session
        return str(session)
    app.run(debug=True)
