// =============================================================
// ZOOM + PAN
// =============================================================

import { getMaskCanvas, getImageCanvas } from "./canvas.js";
import { zoomAt, panBy, fullscreenTest } from "./viewport.js";
import { requestRedraw } from "../pipeline/state.js";


export function setupZoomPan() {
    const maskCanvas = getMaskCanvas();
    const imageCanvas = getImageCanvas();

    // Helper: zoom around canvas center (Photos-style)
    function zoomAtCanvasCenter(deltaY) {
        const rect = maskCanvas.getBoundingClientRect();
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;

        const factor = deltaY < 0 ? 1.1 : 1 / 1.1;
        zoomAt(centerX, centerY, factor);
        requestRedraw();
    }

    // Wheel on maskCanvas
    maskCanvas.addEventListener("wheel", (e) => {
        if (fullscreenTest) return;
        e.preventDefault();
        zoomAtCanvasCenter(e.deltaY);
    }, { passive: false });

    // Wheel on imageCanvas forwards to same center-based zoom
    imageCanvas.addEventListener("wheel", (e) => {
        if (fullscreenTest) return;
        e.preventDefault();
        zoomAtCanvasCenter(e.deltaY);
    }, { passive: false });

    let panning = false;
    let lastX = 0;
    let lastY = 0;

    maskCanvas.addEventListener("mousedown", (e) => {
        if (fullscreenTest) return;
        if (e.button === 1) {
            panning = true;
            lastX = e.clientX;
            lastY = e.clientY;
        }
    });

    maskCanvas.addEventListener("mousemove", (e) => {
        if (fullscreenTest) return;
        if (panning) {
            const dx = e.clientX - lastX;
            const dy = e.clientY - lastY;
            panBy(dx, dy);
            lastX = e.clientX;
            lastY = e.clientY;
            requestRedraw();
        }
    });

    maskCanvas.addEventListener("mouseup", (e) => {
        if (e.button === 1) panning = false;
    });

    maskCanvas.addEventListener("mouseleave", () => {
        panning = false;
    });
}
