// =============================================================
// INPAINT PIPELINE
// =============================================================

import {
    API,
    getCurrentSteps,
    getCurrentHDStrategy,
    getWorkingImage,
    setWorkingImage,
    loadImageToCanvas,
} from "./loader.js";

import { getMaskBase64, hasUserDrawnMask } from "../core/mask.js";

export function setupInpainting() {
    // no-op for now; kept for symmetry
}

// Run inpaint on the CURRENT working image, with the CURRENT mask.
export async function runInpaint() {

    // ⭐ NEW LOGIC: Only send a mask if the user actually painted something
    let maskBase64 = "";
    if (hasUserDrawnMask()) {
        maskBase64 = getMaskBase64() || "";
    }

    console.log("DEBUG runInpaint:",
        "hasUserDrawnMask =", hasUserDrawnMask(),
        "maskBase64 length =", maskBase64.length
    );

    const workingImage = getWorkingImage();

    if (!workingImage) {
        alert("No working image loaded.");
        return;
    }

    const res = await fetch(`${API}/inpaint_v2`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            mask_base64: maskBase64,
            steps: getCurrentSteps(),
            hd_strategy: getCurrentHDStrategy(),
            bundle_id: window.currentBundleId,
        }),
    });

    const data = await res.json();
    console.log("Inpaint result:", data);

    if (data.ok && data.result_base64) {
        setWorkingImage(data.result_base64);
        await loadImageToCanvas(data.result_base64);
        // Mask stays as-is; user can refine and inpaint again
    } else {
        alert("Inpaint failed: " + data.error);
    }
}
