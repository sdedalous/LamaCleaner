# backend/crop.py
# =============================================================
# TEMPORARY CROP STUB
# =============================================================
# This file is intentionally minimal. The real cropping pipeline
# will be implemented later. For now, this stub prevents import
# errors and keeps the /crop endpoint functional for testing.

import os
from typing import Dict, List
from PIL import Image


def run_crop(crop_box: List[int], src_path: str) -> Dict:
    """
    Temporary stub crop function.
    Crops the given image path using the provided box.
    Does NOT interact with any manifest or session state.
    """

    if not os.path.exists(src_path):
        return {"ok": False, "error": f"Source image not found: {src_path}"}

    # Ensure edits dir exists
    edits_dir = os.path.join("data", "edits")
    os.makedirs(edits_dir, exist_ok=True)

    # Build output path
    base, ext = os.path.splitext(os.path.basename(src_path))
    if ext == "":
        ext = ".png"
    out_path = os.path.join(edits_dir, f"{base}_crop{ext}")

    # Perform crop
    try:
        img = Image.open(src_path)
        cropped = img.crop(tuple(crop_box))
        cropped.save(out_path)
    except Exception as e:
        return {"ok": False, "error": str(e)}

    # Convert filesystem path → browser path
    browser_path = "file:///" + os.path.abspath(out_path).replace("\\", "/")

    return {"ok": True, "output_path": browser_path}
