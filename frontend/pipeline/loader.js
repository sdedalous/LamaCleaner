// =============================================================
// IMAGE LOADING + SESSION MANAGEMENT
// =============================================================

import {
    setImg,
    setImageBuffer,
    setMaskBufferSize,
    getMaskCanvas,
    getMaskCtx,
    getMaskBuffer,
    getMaskBufferCtx
} from "../core/canvas.js";

import { fitImageToViewport, draw } from "../core/drawing.js";

export const API = "http://127.0.0.1:8000";
export const DEV_MODE = true;

export let totalImages = 0;
export let currentIndex = 0;

// -------------------------------------------------------------
// Working image state
// -------------------------------------------------------------
let workingImageBase64 = null;

export function setWorkingImage(src) {
    workingImageBase64 = src;
}

export function getWorkingImage() {
    return workingImageBase64;
}

// -------------------------------------------------------------
// SESSION (Manual Path Version)
// -------------------------------------------------------------
export async function startSessionFromPath(folderPath) {
    const res = await fetch(`${API}/init_session_v2`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target_dir: folderPath })
    });

    const data = await res.json();

    totalImages = data.bundle_count ?? data.count ?? 0;
    currentIndex = 0;
    updateProgress();
    alert(`Loaded ${totalImages} images`);

    await loadNextImage();
}

export async function loadNextImage() {
    console.log("loadNextImage CALLED");

    const res = await fetch(`${API}/next_image_v2`);
    const data = await res.json();

    if (!data.url) {
        alert("No more images");
        return;
    }

    window.currentBundleId = data.bundle_id;
    setWorkingImage(data.url);

    // 1️⃣ Load image (creates maskBuffer with correct size)
    await loadImageToCanvas(data.url);
    // 2.5️⃣ Load existing mask if present
    if (data.mask_url) {
        loadSavedMaskForCurrentImage(`${API}${data.mask_url}`);
    }


    // 2️⃣ Clear view-space maskCanvas (overlay) ONLY if there is no saved mask
    const maskCanvas = getMaskCanvas();
    const maskCtx = getMaskCtx();
    if (maskCanvas && maskCtx && !data.mask_url) {
        maskCtx.setTransform(1, 0, 0, 1, 0, 0);
        maskCtx.clearRect(0, 0, maskCanvas.width, maskCanvas.height);
    }

    // 3️⃣ Fit viewport and draw once
    fitImageToViewport();
    if (!data.mask_url) {
        draw(); // when there is a saved mask, loadSavedMaskForCurrentImage() will call draw()
    }


    // 4️⃣ Update progress indicator
    if (data.index !== undefined) {
        currentIndex = data.index;
        updateProgress();
    }
}


// -------------------------------------------------------------
// PROGRESS BAR
// -------------------------------------------------------------
export function updateProgress() {
    if (totalImages === 0) return;
    const pct = (currentIndex / totalImages) * 100;
    const bar = document.getElementById("progressBar");
    if (bar) {
        bar.style.width = pct + "%";
    }
}

// -------------------------------------------------------------
// IMAGE LOADING
// -------------------------------------------------------------
// -------------------------------------------------------------
// IMAGE LOADING
// -------------------------------------------------------------
export function loadImageToCanvas(path) {
    return new Promise((resolve) => {
        let url = path;

        console.log("Loading image:", url);

        const img = new Image();

        img.onload = () => {
            // 1) Store image
            setImg(img);
            setImageBuffer(img);

            // 2) Create IMAGE-SPACE mask buffer matching normalized image size
            setMaskBufferSize(img.width, img.height);

            // 3) Initialize mask buffer as FULL mask ONLY if no saved mask will be loaded
            const buf = getMaskBuffer();
            const bufCtx = getMaskBufferCtx();
            if (buf && bufCtx && !window.__loadingSavedMask) {
                bufCtx.setTransform(1, 0, 0, 1, 0, 0);
                bufCtx.fillStyle = "white";
                bufCtx.fillRect(0, 0, buf.width, buf.height);
            }
            // 4) First draw
            draw();
            resolve();
        };

        img.onerror = (err) => {
            console.error("Image failed to load:", url, err);
            resolve();
        };

        // Correct handling of base64 images
        if (url.startsWith("data:image/")) {
            img.src = url;   // <-- load base64 directly
        }
        else if (url.startsWith("/image?path=")) {
            img.src = `${API}${url}`;
        }
        else if (!url.startsWith("http")) {
            img.src = `${API}/image?path=${encodeURIComponent(url)}`;
        }
        else {
            img.src = url;
        }
    });
}


// -------------------------------------------------------------
// MODEL CONFIG LOADING
// -------------------------------------------------------------
let currentModel = null;
let currentSteps = null;
let currentHDStrategy = null;

export async function loadModelConfig() {
    try {
        const res = await fetch(`${API}/config`);
        const cfg = await res.json();

        currentModel = cfg.model;
        currentSteps = cfg.steps;
        currentHDStrategy = cfg.hd_strategy;

        console.log("Loaded backend config:", cfg);
        return cfg;
    } catch (err) {
        console.error("Failed to load backend config:", err);
        return null;
    }
}

export function getCurrentModel() { return currentModel; }
export function getCurrentSteps() { return currentSteps; }
export function getCurrentHDStrategy() { return currentHDStrategy; }
export function setCurrentModel(m) { currentModel = m; }
export function setCurrentSteps(s) { currentSteps = s; }
export function setCurrentHDStrategy(h) { currentHDStrategy = h; }

// -------------------------------------------------------------
// FUTURE: Saved mask loading stub
// -------------------------------------------------------------
export async function loadSavedMaskForCurrentImage(maskUrl) {
    const img = new Image();
    img.onload = () => {
        const buf = getMaskBuffer();
        const bufCtx = getMaskBufferCtx();
        const maskCanvas = getMaskCanvas();
        const maskCtx = getMaskCtx();

        if (!buf || !bufCtx || !maskCanvas || !maskCtx) return;

        // 1️⃣ Clear the view-space overlay (red tint)
        maskCtx.setTransform(1, 0, 0, 1, 0, 0);
        maskCtx.clearRect(0, 0, maskCanvas.width, maskCanvas.height);

        // 2️⃣ Load the saved mask into the IMAGE-SPACE buffer
        bufCtx.setTransform(1, 0, 0, 1, 0, 0);
        bufCtx.clearRect(0, 0, buf.width, buf.height);
        bufCtx.drawImage(img, 0, 0, buf.width, buf.height);

        // 3️⃣ Redraw everything (this regenerates the red overlay)
        draw();
    };

    img.src = maskUrl;
}
