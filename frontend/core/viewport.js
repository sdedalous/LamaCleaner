// =============================================================
// VIEWPORT + TRANSFORM
// =============================================================

export const VIEW_W = 800;
export const VIEW_H = 800;

export const ViewTransform = {
    scale: 1.0,
    offsetX: 0.0,
    offsetY: 0.0
};

export const ViewportState = {
    width: VIEW_W,
    height: VIEW_H
};

export let fullscreenTest = false;

export function applyViewTransform(ctx) {
    const { scale, offsetX, offsetY } = ViewTransform;
    ctx.setTransform(scale, 0, 0, scale, offsetX, offsetY);
}

export function resetTransform(ctx) {
    ctx.setTransform(1, 0, 0, 1, 0, 0);
}

export function screenToImage(x, y) {
    const { scale, offsetX, offsetY } = ViewTransform;
    return { x: (x - offsetX) / scale, y: (y - offsetY) / scale };
}

export function imageToScreen(x, y) {
    const { scale, offsetX, offsetY } = ViewTransform;
    return { x: x * scale + offsetX, y: y * scale + offsetY };
}

export function zoomAt(mouseX, mouseY, factor) {
    const { scale } = ViewTransform;
    const newScale = scale * factor;

    const imgBefore = screenToImage(mouseX, mouseY);
    ViewTransform.scale = newScale;
    const scrAfter = imageToScreen(imgBefore.x, imgBefore.y);

    ViewTransform.offsetX += mouseX - scrAfter.x;
    ViewTransform.offsetY += mouseY - scrAfter.y;
}

export function panBy(dx, dy) {
    ViewTransform.offsetX += dx;
    ViewTransform.offsetY += dy;
}

export function setFullscreenTest(flag) {
    fullscreenTest = flag;
}
