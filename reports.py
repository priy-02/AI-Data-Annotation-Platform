"""
reports.py
--------------------------
Reports Blueprint
"""

import csv
from io import StringIO, BytesIO
from datetime import datetime

from flask import Blueprint, render_template, make_response
from flask_login import login_required

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from models import Project, ImageFile, Annotation

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/reports")
@login_required
def reports():
    total_projects = Project.query.count()
    total_images = ImageFile.query.count()
    total_annotations = Annotation.query.count()

    images = ImageFile.query.all()
    projects = Project.query.all()

    completed_images = sum(1 for i in images if len(i.annotations) > 0)
    pending_images = total_images - completed_images

    completion_rate = round((completed_images / total_images) * 100, 2) if total_images else 0
    avg_annotations = round(total_annotations / total_images, 2) if total_images else 0
    avg_images = round(total_images / total_projects, 2) if total_projects else 0

    most_annotated = None
    max_annotations = 0
    for image in images:
        c = len(image.annotations)
        if c > max_annotations:
            max_annotations = c
            most_annotated = image

    image_labels = [i.filename for i in images]
    annotation_counts = [len(i.annotations) for i in images]
    project_labels = [p.name for p in projects]
    project_counts = [len(p.images) for p in projects]

    return render_template(
        "reports.html",
        total_projects=total_projects,
        total_images=total_images,
        total_annotations=total_annotations,
        completed_images=completed_images,
        pending_images=pending_images,
        completion_rate=completion_rate,
        avg_annotations=avg_annotations,
        avg_images=avg_images,
        most_annotated=most_annotated,
        max_annotations=max_annotations,
        images=images,
        projects=projects,
        image_labels=image_labels,
        annotation_counts=annotation_counts,
        project_labels=project_labels,
        project_counts=project_counts
    )


@reports_bp.route("/reports/export/csv")
@login_required
def export_csv():
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Image", "Annotations", "Status"])

    for image in ImageFile.query.all():
        count = len(image.annotations)
        writer.writerow([
            image.filename,
            count,
            "Completed" if count else "Pending"
        ])

    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=annotation_report.csv"
    response.headers["Content-Type"] = "text/csv"
    return response


@reports_bp.route("/reports/export/pdf")
@login_required
def export_pdf():
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("<b>AI Data Annotation Platform Report</b>", styles["Title"]))
    elements.append(Paragraph(
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        styles["Normal"]
    ))

    images = ImageFile.query.all()

    stats = [
        ["Metric", "Value"],
        ["Projects", Project.query.count()],
        ["Images", ImageFile.query.count()],
        ["Annotations", Annotation.query.count()],
    ]

    stats_table = Table(stats)
    stats_table.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.grey),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("GRID",(0,0),(-1,-1),1,colors.black),
    ]))
    elements.append(stats_table)

    rows = [["Image","Annotations","Status"]]
    for img in images:
        c = len(img.annotations)
        rows.append([img.filename, str(c), "Completed" if c else "Pending"])

    tbl = Table(rows)
    tbl.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.darkblue),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("GRID",(0,0),(-1,-1),1,colors.black),
    ]))
    elements.append(tbl)

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()

    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "attachment; filename=annotation_report.pdf"
    return response
