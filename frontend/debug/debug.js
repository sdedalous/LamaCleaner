// frontend/debug/debug.js
// =============================================================
// DEBUG TOOLKIT — SAFE, ISOLATED, REUSABLE
// =============================================================

import { 
    getMaskBuffer, 
    getMaskBufferCtx, 
    getImg 
} from "../core/canvas.js";
import { ViewTransform } from "../core/viewport.js";

export const DEBUG_ENABLED = true;

// -------------------------------------------------------------
// 1. Sample mask buffer pixels
// -------------------------------------------------------------
export function debugMaskBufferSample(label) {
    if (!DEBUG_ENABLED) return;

    const buf = getMaskBuffer();
    const ctx = getMaskBufferCtx();
    if (!buf || !ctx) {
        console.log(label, "NO MASK BUFFER");
        return;
    }

    const samplePoints = [
        [0, 0],
        [buf.width - 1, 0],
        [0, buf.height - 1],
        [buf.width - 1, buf.height - 1],
        [Math.floor(buf.width / 2), Math.floor(buf.height / 2)]
    ];

    console.log(`\n===== MASK BUFFER DEBUG: ${label} =====`);
    for (const [x, y] of samplePoints) {
        const pixel = ctx.getImageData(x, y, 1, 1).data;
        console.log(`(${x},${y}) → RGBA =`, pixel);
    }
    console.log("=====================================\n");
}

// -------------------------------------------------------------
// 2. Dump mask buffer as ASCII map (low-res)
// -------------------------------------------------------------
export function debugMaskAscii(label, step = 50) {
    if (!DEBUG_ENABLED) return;

    const buf = getMaskBuffer();
    const ctx = getMaskBufferCtx();
    if (!buf || !ctx) return;

    console.log(`\n===== MASK ASCII DEBUG: ${label} =====`);
    for (let y = 0; y < buf.height; y += step) {
        let row = "";
        for (let x = 0; x < buf.width; x += step) {
            const a = ctx.getImageData(x, y, 1, 1).data[3];
            row += a > 128 ? "#" : ".";
        }
        console.log(row);
    }
    console.log("=====================================\n");
}

// -------------------------------------------------------------
// 3. Dump mask buffer as base64 PNG
// -------------------------------------------------------------
export function debugMaskBase64(label) {
    if (!DEBUG_ENABLED) return;

    const buf = getMaskBuffer();
    if (!buf) return;

    console.log(`\n===== MASK BASE64 DEBUG: ${label} =====`);
    console.log(buf.toDataURL("image/png").slice(0, 200) + "...");
    console.log("=====================================\n");
}

// -------------------------------------------------------------
// 4. Log view transform
// -------------------------------------------------------------
export function debugViewTransform(label) {
    if (!DEBUG_ENABLED) return;

    console.log(`\n===== VIEW TRANSFORM DEBUG: ${label} =====`);
    console.log("scale:", ViewTransform.scale);
    console.log("offsetX:", ViewTransform.offsetX);
    console.log("offsetY:", ViewTransform.offsetY);
    console.log("=====================================\n");
}

// -------------------------------------------------------------
// 5. Log working image metadata
// -------------------------------------------------------------
export function debugWorkingImage(label) {
    if (!DEBUG_ENABLED) return;

    const img = getImg();
    if (!img) return;

    console.log(`\n===== WORKING IMAGE DEBUG: ${label} =====`);
    console.log("size:", img.width, img.height);
    console.log("=====================================\n");
}


import { getMaskCanvas, getImageCanvas } from "../core/canvas.js";

export function debugViewport(label) {
    const maskCanvas = getMaskCanvas();
    const imageCanvas = getImageCanvas();

    console.log(`\n===== VIEWPORT DEBUG: ${label} =====`);
    console.log("scale:", ViewTransform.scale);
    console.log("offsetX:", ViewTransform.offsetX);
    console.log("offsetY:", ViewTransform.offsetY);

    console.log("imageCanvas size:", imageCanvas?.width, imageCanvas?.height);
    console.log("maskCanvas size:", maskCanvas?.width, maskCanvas?.height);
    console.log("=====================================\n");
}

