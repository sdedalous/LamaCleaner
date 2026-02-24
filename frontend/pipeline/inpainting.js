// =============================================================
// INPAINT PIPELINE
// =============================================================
import { debugMaskAscii } from "../debug/debug.js";
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
import { reloadCurrentBundle } from "./loader.js";

export async function runInpaint() {
    debugMaskAscii("BEFORE GETMASKBASE64", 50);

    const maskBase64 = getMaskBase64() || "";
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

    if (!data.ok) {
        alert("Inpaint failed: " + data.error);
        return;
    }

    // ⭐ Do NOT use data.result_base64 anymore.
    // ⭐ Backend has already written inpaint.png + mask.png into the bundle.
    // ⭐ Just reload the current bundle via the same pipeline as initial load.
    await reloadCurrentBundle();
}

