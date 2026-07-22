"""
models.py
--------------------------
Database Models
"""
from datetime import datetime

from flask_login import UserMixin

from extensions import db


# -------------------------------------------------
# User
# -------------------------------------------------

class User(UserMixin, db.Model):

    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    password = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(50), default="Annotator")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    projects = db.relationship(
        "Project",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    activity_logs = db.relationship(
        "ActivityLog",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )


# -------------------------------------------------
# Project
# -------------------------------------------------

class Project(db.Model):

    __tablename__ = "project"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    description = db.Column(db.String(300))

    status = db.Column(db.String(20), default="Active")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    images = db.relationship(
        "ImageFile",
        backref="project",
        lazy=True,
        cascade="all, delete-orphan"
    )


# -------------------------------------------------
# Image File
# -------------------------------------------------

class ImageFile(db.Model):

    __tablename__ = "image_file"

    id = db.Column(db.Integer, primary_key=True)

    filename = db.Column(db.String(255), nullable=False)

    uploaded_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    project_id = db.Column(
        db.Integer,
        db.ForeignKey("project.id"),
        nullable=False
    )

    annotations = db.relationship(
        "Annotation",
        backref="image",
        lazy=True,
        cascade="all, delete-orphan"
    )


# -------------------------------------------------
# Annotation
# -------------------------------------------------
class Annotation(db.Model):
    
    __tablename__ = "annotation"

    id = db.Column(db.Integer, primary_key=True)

    label = db.Column(db.String(100))

    x = db.Column(db.Float)
    y = db.Column(db.Float)
    width = db.Column(db.Float)
    height = db.Column(db.Float)

    confidence = db.Column(db.Float, default=100)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    image_id = db.Column(
        db.Integer,
        db.ForeignKey("image_file.id"),
        nullable=False
    )

    # -------------------------
    # Review Fields
    # -------------------------

    status = db.Column(
        db.String(20),
        default="Pending"
    )

    review_comment = db.Column(
        db.Text
    )

    reviewed_by = db.Column(
        db.String(100)
    )

    reviewed_at = db.Column(
        db.DateTime
    )


# -------------------------------------------------
# Activity Log
# -------------------------------------------------

class ActivityLog(db.Model):

    __tablename__ = "activity_log"

    id = db.Column(db.Integer, primary_key=True)

    action = db.Column(db.String(255), nullable=False)

    timestamp = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )