"""
utils.py
-----------------------------
Utility Functions
Shared helper functions used across the project.
"""

import os
from datetime import datetime
from flask import current_app

from extensions import db
from models import Project, ActivityLog


# ===========================================
# Check Allowed File Extension
# ===========================================

def allowed_file(filename):
    """
    Returns True if the uploaded file extension is allowed.
    """

    if "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()

    return extension in current_app.config["ALLOWED_EXTENSIONS"]


# ===========================================
# Get or Create Default Project
# ===========================================

def get_default_project(user):

    project = Project.query.filter_by(
        user_id=user.id,
        name="Default Project"
    ).first()

    if project:
        return project

    project = Project(
        name="Default Project",
        description="Automatically created project.",
        user_id=user.id
    )

    db.session.add(project)
    db.session.commit()

    return project


# ===========================================
# Log User Activity
# ===========================================

def log_activity(user_id, action):

    activity = ActivityLog(
        user_id=user_id,
        action=action
    )

    db.session.add(activity)
    db.session.commit()


# ===========================================
# Convert Bounding Box to YOLO Format
# ===========================================

def convert_to_yolo(x, y, width, height,
                    image_width, image_height):

    x_center = (x + width / 2) / image_width

    y_center = (y + height / 2) / image_height

    w = width / image_width

    h = height / image_height

    return (

        round(x_center, 6),

        round(y_center, 6),

        round(w, 6),

        round(h, 6)

    )


# ===========================================
# Calculate Annotation Statistics
# ===========================================

def annotation_statistics(annotations):

    total = len(annotations)

    labels = {}

    for ann in annotations:

        labels[ann.label] = labels.get(
            ann.label,
            0
        ) + 1

    return {

        "total_annotations": total,

        "labels": labels

    }


# ===========================================
# Format File Size
# ===========================================

def format_size(size):

    units = [

        "Bytes",

        "KB",

        "MB",

        "GB",

        "TB"

    ]

    index = 0

    while size >= 1024 and index < len(units) - 1:

        size /= 1024

        index += 1

    return f"{size:.2f} {units[index]}"


# ===========================================
# Count Uploaded Images
# ===========================================

def count_uploaded_images():

    upload_folder = current_app.config["UPLOAD_FOLDER"]

    if not os.path.exists(upload_folder):
        return 0

    return len(

        [

            file

            for file in os.listdir(upload_folder)

            if os.path.isfile(

                os.path.join(upload_folder, file)

            )

        ]

    )


# ===========================================
# Timestamp
# ===========================================

def current_timestamp():

    return datetime.now().strftime(
        "%d-%m-%Y %H:%M:%S"
    )


# ===========================================
# Application Information
# ===========================================

APP_NAME = "AI Data Annotation Platform"

VERSION = "2.0"

AUTHOR = "Vegu Priya"