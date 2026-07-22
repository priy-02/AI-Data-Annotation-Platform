"""
annotation.py
--------------------------
Annotation Blueprint
Handles:
- Open annotation page
- Save annotations
- Load annotations
- Delete annotations
- Annotation API
"""

from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    abort
)

from flask_login import (
    login_required,
    current_user
)

from extensions import db
from models import ImageFile, Annotation, ActivityLog

annotation_bp = Blueprint("annotation", __name__)


# ==========================================
# Open Annotation Page
# ==========================================

@annotation_bp.route("/annotate/<int:image_id>")
@login_required
def annotate(image_id):

    image = ImageFile.query.get_or_404(image_id)

    return render_template(
        "annotate.html",
        image=image
    )


# ==========================================
# Load Annotation Data
# ==========================================

@annotation_bp.route("/annotations/<int:image_id>")
@login_required
def get_annotations(image_id):

    image = ImageFile.query.get_or_404(image_id)

    data = []

    for ann in image.annotations:

        data.append({
            "id": ann.id,
            "label": ann.label,
            "x": ann.x,
            "y": ann.y,
            "width": ann.width,
            "height": ann.height
        })

    return jsonify(data)


# ==========================================
# Save Annotation
# ==========================================

@annotation_bp.route("/save_annotations/<int:image_id>", methods=["POST"])
@login_required
def save_annotations(image_id):

    image = ImageFile.query.get_or_404(image_id)

    annotations = request.get_json()

    if annotations is None:

        return jsonify({
            "success": False,
            "message": "No annotation data received."
        }), 400

    # Remove previous annotations
    Annotation.query.filter_by(
        image_id=image.id
    ).delete()

    # Save new annotations
    for item in annotations:

        annotation = Annotation(

            label=item["label"],

            x=float(item["x"]),

            y=float(item["y"]),

            width=float(item["width"]),

            height=float(item["height"]),

            image_id=image.id

        )

        db.session.add(annotation)

    db.session.commit()

    log = ActivityLog(

        action=f"Annotated {image.filename}",

        user_id=current_user.id

    )

    db.session.add(log)

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Annotations saved successfully."
    })


# ==========================================
# Delete One Annotation
# ==========================================

@annotation_bp.route("/delete_annotation/<int:annotation_id>", methods=["DELETE"])
@login_required
def delete_annotation(annotation_id):

    annotation = Annotation.query.get_or_404(annotation_id)

    db.session.delete(annotation)

    db.session.commit()

    return jsonify({
        "success": True
    })


# ==========================================
# Delete All Annotations
# ==========================================

@annotation_bp.route("/clear_annotations/<int:image_id>", methods=["DELETE"])
@login_required
def clear_annotations(image_id):

    image = ImageFile.query.get_or_404(image_id)

    Annotation.query.filter_by(
        image_id=image.id
    ).delete()

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "All annotations deleted."
    })


# ==========================================
# Annotation Statistics
# ==========================================

@annotation_bp.route("/annotation_stats/<int:image_id>")
@login_required
def annotation_stats(image_id):

    image = ImageFile.query.get_or_404(image_id)

    labels = {}

    for ann in image.annotations:

        labels[ann.label] = labels.get(
            ann.label,
            0
        ) + 1

    return jsonify({

        "image": image.filename,

        "total_annotations": len(image.annotations),

        "labels": labels

    })