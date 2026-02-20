// =============================================================
// SAVE PIPELINE (FRONTEND)
// =============================================================

import { API } from "./loader.js";

// -------------------------------------------------------------
// SAVE ONE PASS (pass_N)
// -------------------------------------------------------------
export async function savePass() {
    const canvas = document.getElementById("mainCanvas");
    const edited_base64 = canvas.toDataURL("image/png");

    const res = await fetch(`${API}/save_pass`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            bundle_id: window.currentBundleId,
            edited_base64: edited_base64
        })
    });

    const data = await res.json();
    console.log("Saved pass:", data);
    return data;
}

// -------------------------------------------------------------
// SKIP IMAGE (no edits)
// -------------------------------------------------------------
export async function skipImage() {
    const res = await fetch(`${API}/skip_image`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            bundle_id: window.currentBundleId
        })
    });

    const data = await res.json();
    console.log("Skipped image:", data);
    return data;
}

// -------------------------------------------------------------
// FINALIZE IMAGE (after last pass)
// -------------------------------------------------------------
export async function finalizeImage() {
    const res = await fetch(`${API}/finalize_image`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            bundle_id: window.currentBundleId
        })
    });

    const data = await res.json();
    console.log("Finalized image:", data);
    return data;
}

// -------------------------------------------------------------
// RELOAD BASE IMAGE (for new pass)
// -------------------------------------------------------------
export async function reloadBaseImage() {
    const res = await fetch(`${API}/reload_base_image`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            bundle_id: window.currentBundleId
        })
    });

    const data = await res.json();
    console.log("Reloaded base image:", data);

    // The backend returns the base-cropped image path or base64
    if (data.base_image_base64) {
        const img = new Image();
        img.src = data.base_image_base64;
        img.onload = () => {
            const canvas = document.getElementById("mainCanvas");
            const ctx = canvas.getContext("2d");
            ctx.drawImage(img, 0, 0);
        };
    }

    return data;
}
