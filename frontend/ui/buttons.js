// =============================================================
// UI BUTTONS
// =============================================================
import { runRembg } from "../pipeline/rembg.js";
import { restoreMaskCheckpoint } from "../core/mask.js";
import { requestRedraw } from "../pipeline/state.js";
import { hasEdits, resetEdits } from "../pipeline/state.js";
import { savePass, finalizeImage, skipImage, reloadBaseImage } from "../pipeline/save.js";
import { loadNextImage, startSessionFromPath, API } from "../pipeline/loader.js";
import { draw } from "../core/drawing.js";
import { runInpaint } from "../pipeline/inpainting.js";
import { loadImageToCanvas } from "../pipeline/loader.js";
import { getMaskCanvas } from "../core/canvas.js";

export function setupButtons() {

    // ---------------------------------------------------------
    // START SESSION AUTOMATICALLY WHEN USER ENTERS PATH
    // ---------------------------------------------------------
    const pathInput = document.getElementById("folderPathInput");

    pathInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            const path = pathInput.value.trim();
            if (!path) {
                alert("Please enter a folder path.");
                return;
            }
            startSessionFromPath(path);
        }
    });

    // ---------------------------------------------------------
    // NEXT IMAGE
    // ---------------------------------------------------------
    document.getElementById("nextBtn").onclick = loadNextImage;

    // ---------------------------------------------------------
    // DONE BUTTON (save pass / finalize)
    // ---------------------------------------------------------
    document.getElementById("doneBtn").onclick = async () => {

        if (!hasEdits) {
            await skipImage();
            await loadNextImage();
            return;
        }

        const again = confirm("Do you want to edit again from the base image?");

        if (again) {
            await savePass();
            await reloadBaseImage();
            resetEdits();
            return;
        }

        await savePass();
        await finalizeImage();
        await loadNextImage();
    };

    // ---------------------------------------------------------
    // DELETE IMAGE
    // ---------------------------------------------------------
    document.getElementById("deleteBtn").onclick = async () => {
        await fetch(`${API}/delete_image`, { method: "POST" });
        await loadNextImage();
    };

    // ---------------------------------------------------------
    // CROP (TEST)
    // ---------------------------------------------------------
    const controls = document.getElementById("controls");

    const cropBtn = document.createElement("button");
    cropBtn.textContent = "Crop (Test)";
    cropBtn.onclick = async () => {
        const cropBox = [50, 50, 400, 400];

        const res = await fetch(`${API}/crop`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ crop_box: cropBox })
        });

        const data = await res.json();
        console.log("Crop result:", data);

        if (data.ok && data.output_path) {
            await loadImageToCanvas(data.output_path);
        }
    };
    controls.appendChild(cropBtn);

    // ---------------------------------------------------------
    // INPAINT
    // ---------------------------------------------------------
    const inpaintBtn = document.createElement("button");
    inpaintBtn.textContent = "Inpaint";
    inpaintBtn.id = "inpaintBtn";
    inpaintBtn.onclick = () => runInpaint();
    controls.appendChild(inpaintBtn);

    // ---------------------------------------------------------
    // REMBG
    // ---------------------------------------------------------
    const rembgBtn = document.createElement("button");
    rembgBtn.textContent = "Rembg";
    rembgBtn.id = "rembgBtn";
    rembgBtn.onclick = () => runRembg();
    controls.appendChild(rembgBtn);

    // ---------------------------------------------------------
    // RESTORE MASK (after rembg)
    // ---------------------------------------------------------
    const restoreMaskBtn = document.createElement("button");
    restoreMaskBtn.textContent = "Restore Mask";
    restoreMaskBtn.id = "restoreMaskBtn";
    restoreMaskBtn.onclick = () => {
        if (restoreMaskCheckpoint()) {
            requestRedraw();
        }
    };
    controls.appendChild(restoreMaskBtn);


    // ---------------------------------------------------------
    // WATERMARK UPLOAD
    // ---------------------------------------------------------
    document.getElementById("watermarkUpload").onchange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const form = new FormData();
        form.append("file", file);

        await fetch(`${API}/save_watermarked`, {
            method: "POST",
            body: form
        });

        await loadNextImage();
    };


}
