// =============================================================
// REMBG PIPELINE
// =============================================================

import { API, getWorkingImage } from "./loader.js";
import {
    saveMaskCheckpoint,
    restoreMaskCheckpoint,
} from "../core/mask.js";
import { requestRedraw } from "../pipeline/state.js";

export async function runRembg() {
    const workingImage = getWorkingImage();
    if (!workingImage) {
        alert("No working image loaded.");
        return;
    }

    // Save current mask so we can restore if rembg result is bad
    saveMaskCheckpoint();

    const res = await fetch(`${API}/rembg`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            bundle_id: window.currentBundleId,
            image_base64: workingImage,
        }),
    });

    const data = await res.json();
    console.log("Rembg result:", data);

    if (data.ok && data.mask_base64) {
        const img = new Image();
        img.src = data.mask_base64;
        img.onload = () => {
            const canvas = document.getElementById("maskCanvas");
            const ctx = canvas.getContext("2d");
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.drawImage(img, 0, 0);
            requestRedraw();
        };
    } else {
        alert("Rembg failed: " + (data.error || "Unknown error"));
        // Roll back to pre-rembg mask if we have one
        if (restoreMaskCheckpoint()) {
            requestRedraw();
        }
    }
}
