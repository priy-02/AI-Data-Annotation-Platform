from flask import Flask
import os
import csv


from config import Config
from extensions import db, login_manager

from auth import auth_bp
from dashboard import dashboard_bp
from annotation import annotation_bp
from exports import export_bp
from reports import reports_bp
from models import User
from review import review_bp



def create_app():

    app = Flask(__name__)

    # Load Configuration
    app.config.from_object(Config)
    app.config["REMEMBER_COOKIE_DURATION"] = 86400
    app.config["SESSION_PERMANENT"] = False

    # Create Required Folders
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["ANNOTATION_FOLDER"], exist_ok=True)
    os.makedirs(app.config["YOLO_FOLDER"], exist_ok=True)
    os.makedirs(app.config["COCO_FOLDER"], exist_ok=True)
    os.makedirs(app.config["VOC_FOLDER"], exist_ok=True)

    # Initialize Extensions
    db.init_app(app)
    login_manager.init_app(app)
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(annotation_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(review_bp)

    # Create Database
    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)