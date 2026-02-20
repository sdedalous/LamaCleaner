// =============================================================
// CANVAS SETUP + SHARED BUFFERS
// =============================================================

import { VIEW_W, VIEW_H, ViewportState } from "./viewport.js";

let imageCanvas, maskCanvas;
let imgCtx, maskCtx;

let img = null;
let imageBuffer = null;

// Offscreen mask in IMAGE SPACE
let maskBuffer = null;
let maskBufferCtx = null;

// =============================================================
// CANVAS SETUP
// =============================================================
export function setupCanvas() {
    imageCanvas = document.getElementById("imageCanvas");
    maskCanvas = document.getElementById("maskCanvas");

    imgCtx = imageCanvas.getContext("2d");
    maskCtx = maskCanvas.getContext("2d");

    imageCanvas.width = VIEW_W;
    imageCanvas.height = VIEW_H;
    maskCanvas.width = VIEW_W;
    maskCanvas.height = VIEW_H;

    ViewportState.width = VIEW_W;
    ViewportState.height = VIEW_H;

    imgCtx.imageSmoothingEnabled = false;
    maskCtx.imageSmoothingEnabled = false;
}

// =============================================================
// IMAGE + MASK BUFFERS
// =============================================================
export function setImg(newImg) { img = newImg; }
export function getImg() { return img; }

export function setImageBuffer(buf) { imageBuffer = buf; }
export function getImageBuffer() { return imageBuffer; }

// Offscreen mask buffer in IMAGE SPACE (normalized size)
export function setMaskBufferSize(w, h) {
    maskBuffer = document.createElement("canvas");
    maskBuffer.width = w;
    maskBuffer.height = h;
    maskBufferCtx = maskBuffer.getContext("2d");

    // ⭐ Start as FULL mask (white)
    maskBufferCtx.setTransform(1, 0, 0, 1, 0, 0);
    maskBufferCtx.fillStyle = "white";
    maskBufferCtx.fillRect(0, 0, w, h);
}

export function getMaskBuffer() { return maskBuffer; }
export function getMaskBufferCtx() { return maskBufferCtx; }

// =============================================================
// CANVAS ACCESSORS
// =============================================================
export function getImageCanvas() { return imageCanvas; }
export function getMaskCanvas() { return maskCanvas; }
export function getImageCtx() { return imgCtx; }
export function getMaskCtx() { return maskCtx; }
