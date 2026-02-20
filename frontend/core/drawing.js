// =============================================================
// DRAWING PIPELINE
// =============================================================

import {
    applyViewTransform,
    resetTransform,
    ViewTransform,
    ViewportState
} from "./viewport.js";

import {
    getImageCanvas,
    getMaskCanvas,
    getImageCtx,
    getMaskCtx,
    getImg,
    getMaskBuffer
} from "./canvas.js";

export function draw() {
    const img = getImg();
    if (!img || !img.width || !img.height) return;

    const imageCanvas = getImageCanvas();
    const maskCanvas = getMaskCanvas();
    const imgCtx = getImageCtx();
    const maskCtx = getMaskCtx();
    const maskBuffer = getMaskBuffer();

    // ------------------------------------------------------------
    // IMAGE LAYER (view space)
    // ------------------------------------------------------------
    resetTransform(imgCtx);
    imgCtx.clearRect(0, 0, imageCanvas.width, imageCanvas.height);

    applyViewTransform(imgCtx);
    imgCtx.drawImage(img, 0, 0);
    resetTransform(imgCtx);

    // ------------------------------------------------------------
    // MASK OVERLAY (maskBuffer in IMAGE SPACE → drawn in VIEW SPACE)
    // ------------------------------------------------------------
    resetTransform(maskCtx);
    maskCtx.clearRect(0, 0, maskCanvas.width, maskCanvas.height);

    if (maskBuffer) {
        maskCtx.save();

        // Draw in VIEW SPACE (same transform as image)
        applyViewTransform(maskCtx);

        // 1) Draw maskBuffer (white = masked, transparent = erased)
        maskCtx.drawImage(maskBuffer, 0, 0);

        // 2) Tint masked area red
        maskCtx.globalCompositeOperation = "source-in";
        maskCtx.fillStyle = "rgba(255, 0, 0, 0.4)";
        maskCtx.fillRect(0, 0, maskBuffer.width, maskBuffer.height);

        maskCtx.restore();
    }

    resetTransform(maskCtx);
}

export function fitImageToViewport() {
    const img = getImg();
    if (!img || !img.width || !img.height) return;

    const { width, height } = ViewportState;

    const scaleX = width / img.width;
    const scaleY = height / img.height;
    const fitScale = Math.min(scaleX, scaleY);

    ViewTransform.scale = fitScale;
    ViewTransform.offsetX = (width - img.width * fitScale) / 2;
    ViewTransform.offsetY = (height - img.height * fitScale) / 2;
}
