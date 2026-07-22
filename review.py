from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import login_required, current_user

from extensions import db
from models import Annotation, ActivityLog

review_bp = Blueprint("review", __name__)


# ----------------------------------------
# Review Dashboard
# ----------------------------------------

@review_bp.route("/review")
@login_required
def review_dashboard():

    search = request.args.get("search", "").strip()
    status = request.args.get("status", "")
    page = request.args.get("page", 1, type=int)

    query = Annotation.query

    if search:
        query = query.filter(
            Annotation.label.ilike(f"%{search}%")
        )

    if status:
        query = query.filter(
            Annotation.status == status
        )

    annotations = query.order_by(
        Annotation.created_at.desc()
    ).paginate(
        page=page,
        per_page=10,
        error_out=False
    )

    return render_template(
        "review_dashboard.html",
        annotations=annotations,
        search=search,
        status=status
    )


# ----------------------------------------
# Review Details
# ----------------------------------------

@review_bp.route("/review/<int:annotation_id>")
@login_required
def review_annotation(annotation_id):

    annotation = Annotation.query.get_or_404(annotation_id)

    return render_template(
        "review.html",
        annotation=annotation
    )


# ----------------------------------------
# Approve
# ----------------------------------------

@review_bp.route("/review/<int:annotation_id>/approve", methods=["POST"])
@login_required
def approve_annotation(annotation_id):

    annotation = Annotation.query.get_or_404(annotation_id)

    annotation.status = "Approved"
    annotation.reviewed_by = current_user.name
    annotation.reviewed_at = datetime.utcnow()

    log = ActivityLog(
        action=f"Approved annotation #{annotation.id}",
        user_id=current_user.id
    )

    db.session.add(log)
    db.session.commit()

    flash("Annotation approved successfully.", "success")

    return redirect(
        url_for(
            "review.review_annotation",
            annotation_id=annotation.id
        )
    )


# ----------------------------------------
# Reject
# ----------------------------------------

@review_bp.route("/review/<int:annotation_id>/reject", methods=["POST"])
@login_required
def reject_annotation(annotation_id):

    annotation = Annotation.query.get_or_404(annotation_id)

    annotation.status = "Rejected"
    annotation.reviewed_by = current_user.name
    annotation.reviewed_at = datetime.utcnow()

    log = ActivityLog(
        action=f"Rejected annotation #{annotation.id}",
        user_id=current_user.id
    )

    db.session.add(log)
    db.session.commit()

    flash("Annotation rejected.", "warning")

    return redirect(
        url_for(
            "review.review_annotation",
            annotation_id=annotation.id
        )
    )


# ----------------------------------------
# Reset to Pending
# ----------------------------------------

@review_bp.route("/review/<int:annotation_id>/pending", methods=["POST"])
@login_required
def pending_annotation(annotation_id):

    annotation = Annotation.query.get_or_404(annotation_id)

    annotation.status = "Pending"
    annotation.reviewed_by = None
    annotation.reviewed_at = None

    log = ActivityLog(
        action=f"Returned annotation #{annotation.id} to Pending",
        user_id=current_user.id
    )

    db.session.add(log)
    db.session.commit()

    flash("Annotation moved back to Pending.", "info")

    return redirect(
        url_for(
            "review.review_annotation",
            annotation_id=annotation.id
        )
    )


# ----------------------------------------
# Save Review Comment
# ----------------------------------------

@review_bp.route("/review/<int:annotation_id>/comment", methods=["POST"])
@login_required
def save_comment(annotation_id):

    annotation = Annotation.query.get_or_404(annotation_id)

    annotation.review_comment = request.form.get(
        "review_comment"
    )

    annotation.reviewed_by = current_user.name
    annotation.reviewed_at = datetime.utcnow()

    log = ActivityLog(
        action=f"Updated review comment for annotation #{annotation.id}",
        user_id=current_user.id
    )

    db.session.add(log)
    db.session.commit()

    flash("Review comment saved.", "success")

    return redirect(
        url_for(
            "review.review_annotation",
            annotation_id=annotation.id
        )
    )