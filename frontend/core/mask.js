// =============================================================
// MASK LAYER: BRUSH + ERASER + EXPORT (IMAGE-SPACE BUFFER)
// =============================================================
import { requestRedraw } from "../pipeline/state.js";
import { screenToImage, ViewTransform } from "./viewport.js";
import {
    getMaskCanvas,
    getMaskBuffer,
    getMaskBufferCtx
} from "./canvas.js";
import { draw } from "./drawing.js";

let brushSize = 40;
let drawing = false;
let lastBrushX = null;
let lastBrushY = null;

// "mask" = remove red (reveal inpaint area)
// "erase" = add red back
let currentTool = "mask";
let userHasDrawnMask = false;
export function hasUserDrawnMask() {
    return userHasDrawnMask;
}

export function setupMask() {
    const maskCanvas = getMaskCanvas();
    const brushSlider = document.getElementById("brushSize");
    const maskBtn = document.getElementById("toolMask");
    const eraseBtn = document.getElementById("toolErase");

    // Brush size
    if (brushSlider) {
        brushSlider.addEventListener("input", (e) => {
            brushSize = parseInt(e.target.value, 10);
            updateBrushCursor();
        });
    }
    updateBrushCursor();

    // Tool buttons
    if (maskBtn) {
        maskBtn.addEventListener("click", () => {
            currentTool = "mask";
            maskBtn.classList.add("active");
            if (eraseBtn) eraseBtn.classList.remove("active");
        });
    }
    if (eraseBtn) {
        eraseBtn.addEventListener("click", () => {
            currentTool = "erase";
            eraseBtn.classList.add("active");
            if (maskBtn) maskBtn.classList.remove("active");
        });
    }


    // Drawing events
    maskCanvas.addEventListener("mousedown", (e) => {
        if (e.button === 0) {
            drawing = true;
            lastBrushX = null;
            lastBrushY = null;
            drawBrush(e);
        }
    });

    maskCanvas.addEventListener("mousemove", (e) => {
        if (drawing) drawBrush(e);
    });

    maskCanvas.addEventListener("mouseup", () => {
        drawing = false;
        lastBrushX = null;
        lastBrushY = null;
    });

    maskCanvas.addEventListener("mouseleave", () => {
        drawing = false;
        lastBrushX = null;
        lastBrushY = null;
    });
}

function drawBrush(e) {
    const ctx = getMaskBufferCtx();
    const buf = getMaskBuffer();
    if (!ctx || !buf) return;

    userHasDrawnMask = true;

    // Convert CANVAS → IMAGE coordinates
    const { x, y } = screenToImage(e.offsetX, e.offsetY);

    // Always draw in IMAGE SPACE
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.lineWidth = brushSize / ViewTransform.scale;

    if (currentTool === "mask") {
        // ⭐ GIMP-style: brush ERASES mask (reveals image)
        ctx.globalCompositeOperation = "destination-out";
        ctx.strokeStyle = "rgba(0,0,0,1)";
    } else {
        // ⭐ Eraser tool: ADD mask back (restore red overlay)
        ctx.globalCompositeOperation = "source-over";
        ctx.strokeStyle = "white";
    }

    if (lastBrushX === null) {
        lastBrushX = x;
        lastBrushY = y;
    }

    ctx.beginPath();
    ctx.moveTo(lastBrushX, lastBrushY);
    ctx.lineTo(x, y);
    ctx.stroke();

    lastBrushX = x;
    lastBrushY = y;

    requestRedraw();

}


function updateBrushCursor() {
    const maskCanvas = getMaskCanvas();
    const size = brushSize;
    const radius = size / 2;

    const cursorCanvas = document.createElement("canvas");
    cursorCanvas.width = size;
    cursorCanvas.height = size;

    const ctx = cursorCanvas.getContext("2d");
    ctx.strokeStyle = "rgba(255,255,255,0.9)";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(radius, radius, radius - 1, 0, Math.PI * 2);
    ctx.stroke();

    const url = cursorCanvas.toDataURL("image/png");
    maskCanvas.style.cursor = `url(${url}) ${radius} ${radius}, crosshair`;
}

// Export mask as PNG (IMAGE-SPACE)
export function getMaskBase64() {
    const buf = getMaskBuffer();
    if (!buf) return null;
    return buf.toDataURL("image/png").split(",")[1];
}

// Load mask from base64 into IMAGE-SPACE buffer
export function setMaskFromBase64(base64Str) {
    const img = new Image();
    img.onload = () => {
        const ctx = getMaskBufferCtx();
        const buf = getMaskBuffer();
        if (!ctx || !buf) return;
        ctx.setTransform(1, 0, 0, 1, 0, 0);
        ctx.clearRect(0, 0, buf.width, buf.height);
        ctx.drawImage(img, 0, 0, buf.width, buf.height);
        requestRedraw();
    };
    img.src = "data:image/png;base64," + base64Str;
}

// =============================================================
// MASK CHECKPOINT (for rembg)
// =============================================================

let maskCheckpoint = null;

export function saveMaskCheckpoint() {
    const canvas = document.getElementById("maskCanvas");
    const clone = document.createElement("canvas");
    clone.width = canvas.width;
    clone.height = canvas.height;
    clone.getContext("2d").drawImage(canvas, 0, 0);
    maskCheckpoint = clone;
}

export function restoreMaskCheckpoint() {
    if (!maskCheckpoint) return false;

    const canvas = document.getElementById("maskCanvas");
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(maskCheckpoint, 0, 0);

    return true;
}

export function clearMaskCheckpoint() {
    maskCheckpoint = null;
}
