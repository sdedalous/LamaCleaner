// =============================================================
// KEYBOARD SHORTCUTS
// =============================================================

export function setupShortcuts() {
    document.addEventListener("keydown", (e) => {
        if (e.key === "d") document.getElementById("doneBtn")?.click();
        if (e.key === "x") document.getElementById("deleteBtn")?.click();
        if (e.key === "n") document.getElementById("nextBtn")?.click();
        if (e.key === "z") document.getElementById("undoBtn")?.click();
        if (e.key === "y") document.getElementById("redoBtn")?.click();
    });
}
