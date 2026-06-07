import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime
from models import db, User, EmergencyContact, SOSHistory, IncidentReport, Admin
from config import config
import json

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG') or (
            'production' if os.environ.get('FLASK_ENV') == 'production' else 'default'
        )

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.contacts import contacts_bp
    from routes.sos import sos_bp
    from routes.incidents import incidents_bp
    from routes.admin import admin_bp
    from routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(contacts_bp)
    app.register_blueprint(sos_bp)
    app.register_blueprint(incidents_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')

    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.home'))
        return render_template('index.html')

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    with app.app_context():
        db.create_all()
        # Create default admin if not exists
        if not Admin.query.filter_by(username='admin').first():
            admin = Admin(
                username='admin',
                email='admin@womensafety.com',
                is_super_admin=True
            )
            admin.set_password('Admin@123')
            db.session.add(admin)
            db.session.commit()
            print("Default admin created: username=admin, password=Admin@123")

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
