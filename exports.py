"""
exports.py
--------------------------
Dataset Export Blueprint
Supports:
- YOLO
- COCO
- Pascal VOC
- ZIP Download
"""

import os
import json
import zipfile
import xml.etree.ElementTree as ET

from flask import (
    Blueprint,
    current_app,
    send_file,
    flash,
    redirect,
    url_for
)

from flask_login import login_required

from models import ImageFile
from extensions import db

export_bp = Blueprint("export", __name__)


# =====================================
# YOLO EXPORT
# =====================================

@export_bp.route("/export/yolo")
@login_required
def export_yolo():

    class_map = current_app.config["CLASS_MAP"]
    export_folder = current_app.config["YOLO_FOLDER"]

    os.makedirs(export_folder, exist_ok=True)

    for image in ImageFile.query.all():

        txt_name = os.path.splitext(image.filename)[0] + ".txt"

        txt_path = os.path.join(export_folder, txt_name)

        with open(txt_path, "w") as f:

            for ann in image.annotations:

                class_id = class_map.get(ann.label, 0)

                x_center = ann.x + ann.width / 2
                y_center = ann.y + ann.height / 2

                f.write(
                    f"{class_id} "
                    f"{x_center:.6f} "
                    f"{y_center:.6f} "
                    f"{ann.width:.6f} "
                    f"{ann.height:.6f}\n"
                )

    flash("YOLO Export Successful", "success")

    return redirect(url_for("dashboard.dashboard"))


# =====================================
# COCO EXPORT
# =====================================

@export_bp.route("/export/coco")
@login_required
def export_coco():

    export_folder = current_app.config["COCO_FOLDER"]

    os.makedirs(export_folder, exist_ok=True)

    class_map = current_app.config["CLASS_MAP"]

    categories = []

    for name, idx in class_map.items():

        categories.append({

            "id": idx,

            "name": name

        })

    images = []

    annotations = []

    ann_id = 1

    for image in ImageFile.query.all():

        images.append({

            "id": image.id,

            "file_name": image.filename

        })

        for ann in image.annotations:

            annotations.append({

                "id": ann_id,

                "image_id": image.id,

                "category_id": class_map.get(ann.label, 0),

                "bbox": [

                    ann.x,

                    ann.y,

                    ann.width,

                    ann.height

                ],

                "area": ann.width * ann.height,

                "iscrowd": 0

            })

            ann_id += 1

    coco = {

        "images": images,

        "annotations": annotations,

        "categories": categories

    }

    output = os.path.join(export_folder, "annotations.json")

    with open(output, "w") as f:

        json.dump(coco, f, indent=4)

    flash("COCO Export Successful", "success")

    return redirect(url_for("dashboard.dashboard"))


# =====================================
# PASCAL VOC EXPORT
# =====================================

@export_bp.route("/export/voc")
@login_required
def export_voc():

    export_folder = current_app.config["VOC_FOLDER"]

    os.makedirs(export_folder, exist_ok=True)

    for image in ImageFile.query.all():

        root = ET.Element("annotation")

        ET.SubElement(root, "filename").text = image.filename

        for ann in image.annotations:

            obj = ET.SubElement(root, "object")

            ET.SubElement(obj, "name").text = ann.label

            box = ET.SubElement(obj, "bndbox")

            ET.SubElement(box, "xmin").text = str(int(ann.x))
            ET.SubElement(box, "ymin").text = str(int(ann.y))
            ET.SubElement(box, "xmax").text = str(int(ann.x + ann.width))
            ET.SubElement(box, "ymax").text = str(int(ann.y + ann.height))

        tree = ET.ElementTree(root)

        xml_name = os.path.splitext(image.filename)[0] + ".xml"

        tree.write(
            os.path.join(export_folder, xml_name),
            encoding="utf-8",
            xml_declaration=True
        )

    flash("Pascal VOC Export Successful", "success")

    return redirect(url_for("dashboard.dashboard"))


# =====================================
# DOWNLOAD COMPLETE DATASET
# =====================================

@export_bp.route("/download_dataset")
@login_required
def download_dataset():

    zip_name = "dataset.zip"

    with zipfile.ZipFile(zip_name, "w") as zipf:

        for folder in [

            current_app.config["UPLOAD_FOLDER"],
            current_app.config["YOLO_FOLDER"],
            current_app.config["COCO_FOLDER"],
            current_app.config["VOC_FOLDER"]

        ]:

            if not os.path.exists(folder):
                continue

            for root, dirs, files in os.walk(folder):

                for file in files:

                    filepath = os.path.join(root, file)

                    zipf.write(

                        filepath,

                        os.path.relpath(filepath)

                    )

    return send_file(

        zip_name,

        as_attachment=True

    )