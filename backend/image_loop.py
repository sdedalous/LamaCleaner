import os
from backend.normalise import normalise_into_bundle

BUNDLE_ROOT = "data/images"


def get_next_image():
    manifest = load_manifest()
    if manifest is None:
        return {"done": True, "error": "No active manifest"}

    idx = manifest["current_index"]
    total = len(manifest["file_list"])

    if idx >= total:
        return {"done": True, "error": "No more images"}

    # Raw path from manifest
    raw_path = manifest["file_list"][idx]

    # Image ID (folder name inside data/images/)
    image_id = os.path.splitext(os.path.basename(raw_path))[0]
    bundle_dir = os.path.join(BUNDLE_ROOT, image_id)
    normalized_path = os.path.join(bundle_dir, "normalized.png")

    # Normalize into bundle only once
    if not os.path.exists(normalized_path):
        try:
            normalise_into_bundle(image_id, raw_path)
        except Exception as e:
            return {
                "done": True,
                "error": f"Normalization failed: {e}",
                "path": raw_path
            }

    # Return normalized path to frontend
    return {
        "done": False,
        "path": normalized_path,
        "index": idx,
        "total": total,
    }


def mark_done():
    manifest = load_manifest()
    if manifest is None:
        return {"ok": False, "error": "No active manifest"}

    idx = manifest["current_index"]
    total = len(manifest["file_list"])

    if idx >= total:
        return {"ok": False, "error": "No more images"}

    # Mark current image as processed
    manifest["processed"].append(manifest["file_list"][idx])

    # Advance index
    manifest["current_index"] += 1

    save_manifest(manifest)
    return {"ok": True, "index": manifest["current_index"], "total": total}
