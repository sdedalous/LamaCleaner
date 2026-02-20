import os
import shutil
import json
from datetime import datetime, timezone

DATA_ROOT = "data"
IMAGES_ROOT = os.path.join(DATA_ROOT, "images")
EXPORT_ROOT = "dataset_v2"


def export_dataset_v2(val_split: float = 0.1):
    """
    Bundle-native dataset exporter.

    Reads bundles from:
        data/images/<bundle_id>/

    Requires:
        normalized.png
        edit_result.png

    Writes:
        dataset_v2/
            train/input/
            train/output/
            val/input/
            val/output/
    """

    # ---------------------------------------------------------
    # Clean previous export
    # ---------------------------------------------------------
    if os.path.exists(EXPORT_ROOT):
        shutil.rmtree(EXPORT_ROOT)

    train_in = os.path.join(EXPORT_ROOT, "train", "input")
    train_out = os.path.join(EXPORT_ROOT, "train", "output")
    val_in = os.path.join(EXPORT_ROOT, "val", "input")
    val_out = os.path.join(EXPORT_ROOT, "val", "output")

    os.makedirs(train_in, exist_ok=True)
    os.makedirs(train_out, exist_ok=True)
    os.makedirs(val_in, exist_ok=True)
    os.makedirs(val_out, exist_ok=True)

    # ---------------------------------------------------------
    # Scan bundles
    # ---------------------------------------------------------
    if not os.path.exists(IMAGES_ROOT):
        return {
            "ok": False,
            "error": "No bundles found (data/images missing)"
        }

    bundle_ids = sorted(os.listdir(IMAGES_ROOT))
    valid = []

    for bundle_id in bundle_ids:
        bundle_dir = os.path.join(IMAGES_ROOT, bundle_id)
        if not os.path.isdir(bundle_dir):
            continue

        norm = os.path.join(bundle_dir, "normalized.png")
        edit = os.path.join(bundle_dir, "edit_result.png")

        if os.path.exists(norm) and os.path.exists(edit):
            valid.append((bundle_id, norm, edit))

    total = len(valid)
    if total == 0:
        return {
            "ok": False,
            "error": "No completed bundles found (no edit_result.png)",
            "total": 0
        }

    # ---------------------------------------------------------
    # Deterministic split
    # ---------------------------------------------------------
    val_count = int(total * val_split)
    train_count = total - val_count

    for i, (bundle_id, norm_path, edit_path) in enumerate(valid):
        if i < val_count:
            in_dir = val_in
            out_dir = val_out
        else:
            in_dir = train_in
            out_dir = train_out

        shutil.copy2(norm_path, os.path.join(in_dir, f"{bundle_id}.png"))
        shutil.copy2(edit_path, os.path.join(out_dir, f"{bundle_id}.png"))

    return {
        "ok": True,
        "total_bundles": total,
        "train_count": train_count,
        "val_count": val_count,
        "export_root": os.path.abspath(EXPORT_ROOT),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
