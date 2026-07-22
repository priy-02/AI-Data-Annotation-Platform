// ======================================
// AI DATA ANNOTATION PLATFORM
// annotation.js
// Part 1
// ======================================

// -----------------------------
// DOM Elements
// -----------------------------

const image = document.getElementById("image");
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

const labelInput = document.getElementById("label");
const confidenceSlider = document.getElementById("confidence");

const saveBtn = document.getElementById("saveBtn");
const clearBtn = document.getElementById("clearBtn");
const deleteBtn = document.getElementById("deleteBtn");
const editBtn = document.getElementById("editBtn");

const annotationList = document.getElementById("annotationList");
const objectCount = document.getElementById("objectCount");
const statusText = document.getElementById("statusText");

// -----------------------------
// Variables
// -----------------------------

let annotations = [];

let drawing = false;

let startX = 0;
let startY = 0;

let currentBox = null;

let selectedIndex = -1;

// -----------------------------
// Setup Canvas
// -----------------------------
function setupCanvas() {

    canvas.width = image.offsetWidth;
    canvas.height = image.offsetHeight;

    canvas.style.width = image.offsetWidth + "px";
    canvas.style.height = image.offsetHeight + "px";

    canvas.style.position = "absolute";
    canvas.style.left = "0";
    canvas.style.top = "0";

    redrawCanvas();

}

// -----------------------------
// Draw Canvas
// -----------------------------

function redrawCanvas() {

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    annotations.forEach((box, index) => {

        ctx.strokeStyle =
            (index === selectedIndex) ? "blue" : "red";

        ctx.lineWidth = 2;

        ctx.strokeRect(
            box.x,
            box.y,
            box.width,
            box.height
        );

        ctx.fillStyle = "red";

        ctx.font = "16px Arial";

        ctx.fillText(
            box.label,
            box.x,
            box.y - 5
        );

    });

    if (currentBox) {

        ctx.strokeStyle = "lime";

        ctx.lineWidth = 2;

        ctx.strokeRect(
            currentBox.x,
            currentBox.y,
            currentBox.width,
            currentBox.height
        );

    }

}

// -----------------------------
// Mouse Events
// -----------------------------

// ======================================
// Mouse Events
// ======================================

canvas.addEventListener("mousedown", function (e) {

    drawing = true;

    const rect = canvas.getBoundingClientRect();

    startX = e.clientX - rect.left;
    startY = e.clientY - rect.top;

    currentBox = null;

});

canvas.addEventListener("mousemove", function (e) {

    if (!drawing) return;

    const rect = canvas.getBoundingClientRect();

    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    currentBox = {

        x: Math.min(startX, x),

        y: Math.min(startY, y),

        width: Math.abs(x - startX),

        height: Math.abs(y - startY)

    };

    redrawCanvas();

});

canvas.addEventListener("mouseup", function () {

    if (!drawing) return;

    drawing = false;

    redrawCanvas();

});

canvas.addEventListener("mouseleave", function () {

    drawing = false;

});
// ======================================
// Save Annotation
// ======================================

saveBtn.addEventListener("click", function () {

    if (currentBox == null) {

        alert("Draw a bounding box first.");

        return;

    }

    const label = labelInput.value.trim();

    if (label === "") {

        alert("Please enter an object label.");

        return;

    }

    if (
        Math.abs(currentBox.width) < 20 ||
        Math.abs(currentBox.height) < 20
    ) {

        alert("Bounding box is too small.");

        return;

    }

    currentBox.label = label;

    currentBox.confidence = parseInt(
        confidenceSlider.value
    );

    annotations.push(currentBox);

    currentBox = null;

    labelInput.value = "";

    redrawCanvas();

    updateAnnotationList();

    saveAnnotationsToServer();

});


// ======================================
// Annotation List
// ======================================

function updateAnnotationList() {

    annotationList.innerHTML = "";

    objectCount.innerHTML = annotations.length;

    if (annotations.length === 0) {

        annotationList.innerHTML =
            "<p>No annotations available.</p>";

        return;

    }

    annotations.forEach((box, index) => {

        const item = document.createElement("div");

        item.className = "annotation-item";

        item.innerHTML = `

            <h4>${box.label}</h4>

            <p>X : ${Math.round(box.x)}</p>

            <p>Y : ${Math.round(box.y)}</p>

            <p>Width : ${Math.round(box.width)}</p>

            <p>Height : ${Math.round(box.height)}</p>

            <p>Confidence : ${box.confidence}%</p>

        `;

        item.onclick = function () {

            selectedIndex = index;

            redrawCanvas();

        };

        annotationList.appendChild(item);

    });

}


// ======================================
// Save to Flask
// ======================================

function saveAnnotationsToServer() {

    fetch("/save_annotations/" + IMAGE_ID, {

        method: "POST",

        headers: {

            "Content-Type": "application/json"

        },

        body: JSON.stringify(annotations)

    })

    .then(response => response.json())

    .then(data => {

        statusText.innerHTML = data.message;

        console.log(data);

    })

    .catch(error => {

        console.error(error);

    });

}


// ======================================
// Load Existing Annotations
// ======================================

function loadAnnotations() {

    fetch("/annotations/" + IMAGE_ID)

    .then(response => response.json())

    .then(data => {

        annotations = data;

        redrawCanvas();

        updateAnnotationList();

    })

    .catch(error => {

        console.error(error);

    });

}


// ======================================
// Load annotations when page opens
// ======================================

window.onload = function () {

    setupCanvas();

    loadAnnotations();

};
// ======================================
// Clear Current Box
// ======================================

clearBtn.addEventListener("click", function () {

    currentBox = null;

    redrawCanvas();

    statusText.innerHTML = "Current box cleared.";

});


// ======================================
// Delete Selected Annotation
// ======================================

deleteBtn.addEventListener("click", function () {

    if (selectedIndex === -1) {

        alert("Select an annotation first.");

        return;

    }

    if (!confirm("Delete selected annotation?")) {

        return;

    }

    annotations.splice(selectedIndex, 1);

    selectedIndex = -1;

    redrawCanvas();

    updateAnnotationList();

    saveAnnotationsToServer();

    statusText.innerHTML = "Annotation deleted.";

});


// ======================================
// Edit Annotation
// ======================================

editBtn.addEventListener("click", function () {

    if (selectedIndex === -1) {

        alert("Select an annotation first.");

        return;

    }

    const newLabel = prompt(
        "Enter new label",
        annotations[selectedIndex].label
    );

    if (!newLabel) {

        return;

    }

    annotations[selectedIndex].label = newLabel.trim();

    redrawCanvas();

    updateAnnotationList();

    saveAnnotationsToServer();

    statusText.innerHTML = "Annotation updated.";

});


// ======================================
// Mini Map
// ======================================

function drawMiniMap() {

    const mini = document.getElementById("miniMap");

    if (!mini) return;

    const mctx = mini.getContext("2d");

    mctx.clearRect(0, 0, mini.width, mini.height);

    mctx.drawImage(
        image,
        0,
        0,
        mini.width,
        mini.height
    );

    const scaleX = mini.width / canvas.width;
    const scaleY = mini.height / canvas.height;

    annotations.forEach(function(box){

        mctx.strokeStyle = "red";

        mctx.lineWidth = 1;

        mctx.strokeRect(

            box.x * scaleX,

            box.y * scaleY,

            box.width * scaleX,

            box.height * scaleY

        );

    });

}

setInterval(drawMiniMap, 1000);


// ======================================
// Export Buttons
// ======================================

document.getElementById("downloadBtn").onclick = function () {

    const blob = new Blob(

        [JSON.stringify(annotations, null, 4)],

        { type: "application/json" }

    );

    const link = document.createElement("a");

    link.href = URL.createObjectURL(blob);

    link.download = IMAGE_NAME + ".json";

    link.click();

};


document.getElementById("yoloBtn").onclick = function () {

    window.location.href = "/export/yolo";

};


document.getElementById("cocoBtn").onclick = function () {

    window.location.href = "/export/coco";

};


document.getElementById("vocBtn").onclick = function () {

    window.location.href = "/export/voc";

};


document.getElementById("zipBtn").onclick = function () {

    window.location.href = "/download_dataset";

};


// ======================================
// Review Mode
// ======================================

const reviewBtn = document.getElementById("reviewBtn");

if (reviewBtn) {

    reviewBtn.onclick = function () {

        alert("Review Mode Enabled");

    };

}


// ======================================
// Annotation History
// ======================================

const historyBtn = document.getElementById("historyBtn");

if (historyBtn) {

    historyBtn.onclick = function () {

        alert(
            "History currently contains " +
            annotations.length +
            " annotation(s)."
        );

    };

}


// ======================================
// Live Clock
// ======================================

setInterval(function(){

    const clock = document.getElementById("clock");

    if(clock){

        clock.innerHTML = new Date().toLocaleTimeString();

    }

},1000);


// ======================================
// Confidence Slider
// ======================================

confidenceSlider.addEventListener("input", function(){

    document.getElementById("confidenceValue").innerHTML =

        this.value + "%";

});


// ======================================
// Full Screen
// ======================================

document.getElementById("fullscreenBtn").onclick = function(){

    document.documentElement.requestFullscreen();

};


// ======================================
// Dark Mode
// ======================================

document.getElementById("themeBtn").onclick = function(){

    document.body.classList.toggle("dark");

};


// ======================================
// Finished
// ======================================

console.log("Annotation Module Loaded Successfully");