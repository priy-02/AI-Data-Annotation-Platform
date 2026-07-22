"""
dashboard.py
--------------------------
Dashboard Blueprint
"""

import os

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app
)

from flask_login import (
    login_required,
    current_user
)

from werkzeug.utils import secure_filename

from extensions import db

from models import (
    Annotation,
    Project,
    ImageFile,
    ActivityLog
)

# -------------------------------------------------
# Blueprint
# -------------------------------------------------

dashboard_bp = Blueprint("dashboard", __name__)

# -------------------------------------------------
# Allowed File Extensions
# -------------------------------------------------

def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_EXTENSIONS"]
    )

# -------------------------------------------------
# Dashboard
# -------------------------------------------------

@dashboard_bp.route("/dashboard")
@login_required
def dashboard():

    search = request.args.get("search", "").strip()

    query = ImageFile.query

    if search:
        query = query.filter(
            ImageFile.filename.ilike(f"%{search}%")
        )

    images = query.order_by(
        ImageFile.uploaded_at.desc()
    ).all()

    total_images = len(images)
    total_projects = Project.query.count()

    total_annotations = 0
    completed = 0
    pending = 0

    chart_labels = []
    chart_values = []

    for image in images:

        annotation_count = len(image.annotations)

        image.annotation_count = annotation_count

        image.uploaded_time = (
            image.uploaded_at.strftime("%d-%m-%Y %H:%M")
            if image.uploaded_at
            else "N/A"
        )

        if annotation_count > 0:
            image.status = "Completed"
            completed += 1
        else:
            image.status = "Pending"
            pending += 1

        total_annotations += annotation_count

        chart_labels.append(image.filename)
        chart_values.append(annotation_count)

    # -------------------------------------------------
    # Review Statistics
    # -------------------------------------------------
    # -------------------------------------------------
    # Review Statistics
    # -------------------------------------------------

    pending_reviews = Annotation.query.filter_by(
        status="Pending"
    ).count()

    approved_reviews = Annotation.query.filter_by(
        status="Approved"
    ).count()

    rejected_reviews = Annotation.query.filter_by(
        status="Rejected"
    ).count()

    total_review_annotations = Annotation.query.count()

    if total_review_annotations > 0:
        review_completion = round(
            ((approved_reviews + rejected_reviews) / total_review_annotations) * 100,
            1
        )
    else:
        review_completion = 0

    return render_template(
        "dashboard.html",
        images=images,
        total_images=total_images,
        total_projects=total_projects,
        total_annotations=total_annotations,
        completed=completed,
        pending=pending,
        pending_reviews=pending_reviews,
        approved_reviews=approved_reviews,
        rejected_reviews=rejected_reviews,
        review_completion=review_completion,
        chart_labels=chart_labels,
        chart_values=chart_values,
        search=search
    )
    
    # -------------------------------------------------
# Upload Image
# -------------------------------------------------

@dashboard_bp.route("/upload", methods=["POST"])
@login_required
def upload():

    if "image" not in request.files:
        flash("No file selected.", "warning")
        return redirect(url_for("dashboard.dashboard"))

    file = request.files["image"]

    if file.filename == "":
        flash("Please select an image.", "warning")
        return redirect(url_for("dashboard.dashboard"))

    if not allowed_file(file.filename):
        flash("Invalid file type.", "danger")
        return redirect(url_for("dashboard.dashboard"))

    filename = secure_filename(file.filename)

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)

    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)

    # Find or create the default project
    project = Project.query.filter_by(
        user_id=current_user.id,
        name="Default Project"
    ).first()

    if not project:
        project = Project(
            name="Default Project",
            description="Auto Created",
            status="Active",
            user_id=current_user.id
        )

        db.session.add(project)
        db.session.commit()

    image = ImageFile(
        filename=filename,
        project_id=project.id
    )

    db.session.add(image)

    activity = ActivityLog(
        action=f"Uploaded image: {filename}",
        user_id=current_user.id
    )

    db.session.add(activity)
    db.session.commit()

    flash("Image uploaded successfully.", "success")

    return redirect(url_for("dashboard.dashboard"))


# -------------------------------------------------
# Delete Image
# -------------------------------------------------

@dashboard_bp.route("/delete_image/<int:image_id>")
@login_required
def delete_image(image_id):

    image = ImageFile.query.get_or_404(image_id)

    filepath = os.path.join(
        current_app.config["UPLOAD_FOLDER"],
        image.filename
    )

    if os.path.exists(filepath):
        os.remove(filepath)

    # Delete related annotations first
    Annotation.query.filter_by(image_id=image.id).delete()

    db.session.delete(image)
    db.session.commit()

    flash("Image deleted successfully.", "success")

    return redirect(url_for("dashboard.dashboard"))
# -------------------------------------------------
# Projects
# -------------------------------------------------

@dashboard_bp.route("/projects")
@login_required
def projects():

    projects = Project.query.order_by(
        Project.created_at.desc()
    ).all()

    total_projects = len(projects)

    completed_projects = Project.query.filter_by(
        status="Completed"
    ).count()

    active_projects = Project.query.filter_by(
        status="Active"
    ).count()

    total_images = ImageFile.query.count()

    total_annotations = Annotation.query.count()

    if total_projects > 0:
        completion_percentage = round(
            (completed_projects / total_projects) * 100,
            1
        )
    else:
        completion_percentage = 0

    return render_template(
        "projects.html",
        projects=projects,
        total_projects=total_projects,
        completed_projects=completed_projects,
        active_projects=active_projects,
        total_images=total_images,
        total_annotations=total_annotations,
        completion_percentage=completion_percentage
    )
    
    

    

# -------------------------------------------------
# Activity
# -------------------------------------------------

@dashboard_bp.route("/activity")
@login_required
def activity():

    logs = ActivityLog.query.order_by(
        ActivityLog.timestamp.desc()
    ).all()

    return render_template(
        "activity.html",
        logs=logs
    )


# -------------------------------------------------
# Create Project
# -------------------------------------------------

@dashboard_bp.route("/project/create", methods=["POST"])
@login_required
def create_project():

    name = request.form.get("name")
    description = request.form.get("description")

    if not name:
        flash("Project name is required.", "danger")
        return redirect(url_for("dashboard.projects"))

    project = Project(
        name=name,
        description=description,
        status="Active",
        user_id=current_user.id
    )

    db.session.add(project)

    db.session.add(
        ActivityLog(
            action=f"Created project: {name}",
            user_id=current_user.id
        )
    )

    db.session.commit()

    flash("Project created successfully.", "success")

    return redirect(url_for("dashboard.projects"))


# -------------------------------------------------
# Delete Project
# -------------------------------------------------

@dashboard_bp.route("/project/delete/<int:id>")
@login_required
def delete_project(id):

    project = Project.query.get_or_404(id)

    db.session.add(
        ActivityLog(
            action=f"Deleted project: {project.name}",
            user_id=current_user.id
        )
    )

    db.session.delete(project)
    db.session.commit()

    flash("Project deleted successfully.", "success")

    return redirect(url_for("dashboard.projects"))


# -------------------------------------------------
# Change Project Status
# -------------------------------------------------

@dashboard_bp.route("/project/status/<int:id>")
@login_required
def change_status(id):

    project = Project.query.get_or_404(id)

    if project.status == "Active":
        project.status = "Completed"
    else:
        project.status = "Active"

    db.session.commit()

    flash("Project status updated successfully.", "success")

    return redirect(url_for("dashboard.projects"))