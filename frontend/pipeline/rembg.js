// =============================================================
// REMBG PIPELINE (CLEANED FOR BUNDLE ARCHITECTURE)
// =============================================================

import { API } from "./loader.js";
import {
    saveMaskCheckpoint,
    restoreMaskCheckpoint,
} from "../core/mask.js";
import { requestRedraw } from "../pipeline/state.js";

// -------------------------------------------------------------
// Run REMBG on the CURRENT bundle
// -------------------------------------------------------------
export async function runRembg() {
    if (!window.currentBundleId) {
        alert("No bundle loaded.");
        return;
    }

    // Save current mask so we can restore if rembg result is bad
    saveMaskCheckpoint();

    const res = await fetch(`${API}/rembg_v2`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            bundle_id: window.currentBundleId
        }),
    });

    const data = await res.json();
    console.log("Rembg result:", data);

    if (!data.ok) {
        alert("Rembg failed: " + (data.error || "Unknown error"));
        if (restoreMaskCheckpoint()) {
            requestRedraw();
        }
        return;
    }

    // Backend has already written:
    //   bundle/<id>/rembg.png
    //   bundle/<id>/mask.png
    //
    // So we simply reload the bundle via the unified loader.
    const { reloadCurrentBundle } = await import("./loader.js");
    await reloadCurrentBundle();
}
