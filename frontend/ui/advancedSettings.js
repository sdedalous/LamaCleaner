// =============================================================
// ADVANCED SETTINGS + MODEL CONFIG
// =============================================================

import {
    API,
    loadModelConfig,
    getCurrentModel,
    getCurrentSteps,
    getCurrentHDStrategy,
    setCurrentModel,
    setCurrentSteps,
    setCurrentHDStrategy
} from "../pipeline/loader.js";

const modelConfig = {
    models: [
        { id: "lama", label: "LaMa" },
        { id: "zits", label: "ZITS" },
        { id: "ldm", label: "LDM" },
        { id: "mat", label: "MAT" }
    ],
    hd_strategies: ["ORIGINAL", "CROP", "RESIZE"]
};

export function setupAdvancedSettings() {
    const advBtn = document.getElementById("advBtn");
    const advPanel = document.getElementById("advPanel");
    const backBtn = document.getElementById("backBtn");
    const saveBtn = document.getElementById("saveModelBtn");

    advBtn.onclick = async () => {
        const cfg = await loadModelConfig();
        if (cfg) populateAdvancedSettingsUI();
        advPanel.style.display = "block";
    };

    backBtn.onclick = () => {
        advPanel.style.display = "none";
    };

    saveBtn.onclick = async () => {
        const selected = document.querySelector('input[name="model"]:checked');
        const newModel = selected ? selected.value : getCurrentModel();
        const newSteps = parseInt(document.getElementById("stepsInput").value, 10);
        const newHD = document.getElementById("hdStrategySelect").value;

        const res = await fetch(`${API}/config`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                model: newModel,
                steps: newSteps,
                hd_strategy: newHD
            })
        });

        const data = await res.json();
        console.log("Config save response:", data);

        setCurrentModel(newModel);
        setCurrentSteps(newSteps);
        setCurrentHDStrategy(newHD);

        if (data.restart_required) {
            let banner = document.getElementById("restartBanner");
            if (!banner) {
                banner = document.createElement("div");
                banner.id = "restartBanner";
                banner.textContent = "Restart required: please refresh the page.";
                banner.style.background = "#a33";
                banner.style.color = "#fff";
                banner.style.padding = "8px";
                banner.style.marginTop = "10px";
                banner.style.fontWeight = "bold";
                document.getElementById("advPanel").appendChild(banner);
            }
        }

        advPanel.style.display = "none";
    };
}

function populateAdvancedSettingsUI() {
    const modelContainer = document.getElementById("modelOptions");
    modelContainer.innerHTML = "";

    const currentModel = getCurrentModel();
    const currentSteps = getCurrentSteps();
    const currentHDStrategy = getCurrentHDStrategy();

    modelConfig.models.forEach(m => {
        const html = `
            <label>
                <input type="radio" name="model" value="${m.id}"
                    ${m.id === currentModel ? "checked" : ""}>
                ${m.label}
            </label><br>
        `;
        modelContainer.insertAdjacentHTML("beforeend", html);
    });

    document.getElementById("stepsInput").value = currentSteps;

    const hdSelect = document.getElementById("hdStrategySelect");
    hdSelect.innerHTML = "";
    modelConfig.hd_strategies.forEach(s => {
        const opt = `<option value="${s}" ${s === currentHDStrategy ? "selected" : ""}>${s}</option>`;
        hdSelect.insertAdjacentHTML("beforeend", opt);
    });
}
