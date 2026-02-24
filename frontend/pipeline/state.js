export let hasEdits = false;

export function markEdited() {
    hasEdits = true;
}

export function resetEdits() {
    hasEdits = false;
}
export function requestRedraw() {
    window.dispatchEvent(new Event("request-redraw"));
}
