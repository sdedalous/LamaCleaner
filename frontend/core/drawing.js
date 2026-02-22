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
    console.log(
        "%cDRAW CALLED",
        "color: red; font-weight: bold;",
        "loadingSavedMask =", window.__loadingSavedMask,
        "\nstack:", new Error().stack
    );

    const img = getImg();
    const maskBuffer = getMaskBuffer();
    const imageCanvas = getImageCanvas();
    const maskCanvas = getMaskCanvas();
    const imgCtx = getImageCtx();
    const maskCtx = getMaskCtx();

    console.log("DRAW: img =", img?.width, img?.height);
    console.log("DRAW: maskBuffer =", maskBuffer?.width, maskBuffer?.height);
    console.log("DRAW: imageCanvas =", imageCanvas?.width, imageCanvas?.height);
    console.log("DRAW: maskCanvas =", maskCanvas?.width, maskCanvas?.height);

    if (!img || !img.width || !img.height) {
        console.log("DRAW: no image, abort");
        return;
    }

    // ------------------------------------------------------------
    // IMAGE LAYER
    // ------------------------------------------------------------
    resetTransform(imgCtx);
    imgCtx.clearRect(0, 0, imageCanvas.width, imageCanvas.height);

    console.log("DRAW: applying view transform for image");
    applyViewTransform(imgCtx);
    imgCtx.drawImage(img, 0, 0);
    resetTransform(imgCtx);

    // ------------------------------------------------------------
    // MASK OVERLAY
    // ------------------------------------------------------------
    resetTransform(maskCtx);
    maskCtx.clearRect(0, 0, maskCanvas.width, maskCanvas.height);

    if (!maskBuffer) {
        console.log("DRAW: maskBuffer is NULL — overlay will be empty");
        return;
    }

    console.log("DRAW: drawing maskBuffer into overlay");

    maskCtx.save();
    applyViewTransform(maskCtx);

    // Draw maskBuffer
    maskCtx.drawImage(maskBuffer, 0, 0);

    // Tint masked area red
    maskCtx.globalCompositeOperation = "source-in";
    maskCtx.fillStyle = "rgba(255, 0, 0, 0.4)";
    maskCtx.fillRect(0, 0, maskBuffer.width, maskBuffer.height);

    maskCtx.restore();

    resetTransform(maskCtx);

    console.log("DRAW: finished");
}


export function fitImageToViewport() {
    console.log("fitImageToViewport CALLED, loadingSavedMask =", window.__loadingSavedMask);
    if (window.__loadingSavedMask) return;
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
