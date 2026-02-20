"""

import json
import os

MANIFEST_PATH = "data/session_manifest.json"


def load_manifest():
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, "r") as f:
            return json.load(f)
    return None


def save_manifest(manifest):
    os.makedirs(os.path.dirname(MANIFEST_PATH), exist_ok=True)
    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=4)


def collect_images(root, include_subfolders):
    exts = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"}
    files = []

    if include_subfolders:
        for dirpath, _, filenames in os.walk(root):
            for f in filenames:
                if os.path.splitext(f)[1].lower() in exts:
                    files.append(os.path.join(dirpath, f))
    else:
        for f in os.listdir(root):
            path = os.path.join(root, f)
            if os.path.isfile(path) and os.path.splitext(f)[1].lower() in exts:
                files.append(path)

    return sorted(files)


def create_manifest(target_dir, watermarked_dir, include_subfolders):
    file_list = collect_images(target_dir, include_subfolders)

    manifest = {
        "target_dir": target_dir,
        "watermarked_dir": watermarked_dir,
        "deleted_dir": os.path.join(target_dir, "deleted"),
        "include_subfolders": include_subfolders,
        "file_list": file_list,
        "current_index": 0,
        "processed": [],
        "deleted": [],
        "watermarked": [],
        "errors": [],
    }

    os.makedirs(manifest["deleted_dir"], exist_ok=True)
    os.makedirs("data/edits", exist_ok=True)

    return manifest
    """