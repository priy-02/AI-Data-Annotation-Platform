import os


class Config:
    # ==============================
    # Flask Configuration
    # ==============================
    SECRET_KEY = "your-secret-key-change-this"

    # ==============================
    # Database Configuration
    # ==============================
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ==============================
    # Project Directories
    # ==============================
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    STATIC_FOLDER = os.path.join(BASE_DIR, "static")

    UPLOAD_FOLDER = os.path.join(STATIC_FOLDER, "uploads")

    ANNOTATION_FOLDER = os.path.join(BASE_DIR, "annotations")

    EXPORT_FOLDER = os.path.join(BASE_DIR, "exports")

    YOLO_FOLDER = os.path.join(EXPORT_FOLDER, "yolo")

    COCO_FOLDER = os.path.join(EXPORT_FOLDER, "coco")

    VOC_FOLDER = os.path.join(EXPORT_FOLDER, "voc")

    # ==============================
    # Allowed Image Types
    # ==============================
    ALLOWED_EXTENSIONS = {
        "png",
        "jpg",
        "jpeg",
        "bmp",
        "webp"
    }

    # ==============================
    # Default Annotation Labels
    # ==============================
    CLASS_MAP = {
        "person": 0,
        "car": 1,
        "bike": 2,
        "bus": 3,
        "truck": 4,
        "cat": 5,
        "dog": 6
    }

    # ==============================
    # Application Settings
    # ==============================
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB upload limit

    DEBUG = True