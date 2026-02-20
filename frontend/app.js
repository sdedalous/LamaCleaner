// =============================================================
// APP ORCHESTRATOR
// =============================================================

import { setupCanvas, getMaskCanvas } from "./core/canvas.js";

import { setupMask } from "./core/mask.js";
import { setupZoomPan } from "./core/zoom_pan.js";

import { loadModelConfig, DEV_MODE } from "./pipeline/loader.js";
import { setupInpainting } from "./pipeline/inpainting.js";

import { setupButtons } from "./ui/buttons.js";
import { setupShortcuts } from "./ui/shortcuts.js";
import { setupAdvancedSettings } from "./ui/advancedSettings.js";

import { attachInputHandlers } from "./core/input.js";
import { draw } from "./core/drawing.js";

window.addEventListener("load", async () => {
    // Core systems
    setupCanvas();
    setupMask();
    setupZoomPan();

    // Attach mask painting input handlers
    // attachInputHandlers(getMaskCanvas());

    // UI systems
    setupButtons();
    setupShortcuts();
    setupAdvancedSettings();
    setupInpainting();

    // Backend config
    await loadModelConfig();

    if (DEV_MODE) {
        console.log("DEV_MODE: waiting for folder selection.");
    }
});
