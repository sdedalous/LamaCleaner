export let hasEdits = false;

export function markEdited() {
    hasEdits = true;
}

export function resetEdits() {
    hasEdits = false;
}
