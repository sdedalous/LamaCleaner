// =============================================================
// CROPPING PIPELINE (STUB)
// =============================================================
//
// Cropping is currently disabled in the UI and not part of the
// edition-based workflow. The previous implementation relied on
// ad-hoc canvas drawing and direct draw() calls, which no longer
// fits the event-driven redraw pipeline.
//
// When cropping is reintroduced, it should:
//
//   • Use the unified viewport transform system
//   • Render crop boxes via the central drawing pipeline
//   • Avoid direct canvas manipulation
//   • Integrate with the edition stack (undo/redo)
//   • Produce a new edition rather than mutating global state
//   • Never call draw() directly — use requestRedraw()
//
// For now, this stub keeps the module valid and loadable.
//

export function setupCropping() {
    // No-op placeholder.
}
