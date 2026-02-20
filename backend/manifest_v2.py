import os
import json
from typing import Dict, List, Optional

DATA_ROOT = "data"
IMAGES_ROOT = os.path.join(DATA_ROOT, "images")
MANIFEST_V2_PATH = os.path.join(DATA_ROOT, "manifest_v2.json")


# ---------------------------------------------------------
# Discover bundles (NOT raw input images)
# ---------------------------------------------------------
def _discover_bundle_ids() -> List[str]:
    """
    Discover bundle IDs from data/images.

    A bundle is any directory directly under data/images.
    This does NOT scan the user input directory.
    """
    if not os.path.exists(IMAGES_ROOT):
        return []

    bundle_ids = []
    for name in os.listdir(IMAGES_ROOT):
        full = os.path.join(IMAGES_ROOT, name)
        if os.path.isdir(full):
            bundle_ids.append(name)

    return sorted(bundle_ids)


# ---------------------------------------------------------
# Create a new manifest_v2
# ---------------------------------------------------------
def create_manifest_v2() -> Dict:
    """
    Create a new bundle-native manifest.

    Schema:
        {
            "bundle_ids": [...],
            "current_index": 0
        }

    This indexes existing bundles in data/images.
    """
    bundle_ids = _discover_bundle_ids()

    manifest = {
        "bundle_ids": bundle_ids,
        "current_index": 0,
    }

    os.makedirs(DATA_ROOT, exist_ok=True)
    with open(MANIFEST_V2_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    return manifest


# ---------------------------------------------------------
# Load/save manifest_v2
# ---------------------------------------------------------
def load_manifest_v2() -> Optional[Dict]:
    if not os.path.exists(MANIFEST_V2_PATH):
        return None

    with open(MANIFEST_V2_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_manifest_v2(manifest: Dict) -> None:
    os.makedirs(DATA_ROOT, exist_ok=True)
    with open(MANIFEST_V2_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
def get_current_bundle_id(manifest: Dict) -> Optional[str]:
    """
    Return the current bundle_id, or None if out of range.
    """
    idx = manifest.get("current_index", 0)
    bundle_ids = manifest.get("bundle_ids", [])

    if not bundle_ids:
        return None
    if idx < 0 or idx >= len(bundle_ids):
        return None

    return bundle_ids[idx]


def advance_to_next_bundle(manifest: Dict) -> Dict:
    """
    Increment current_index, clamped to the end.
    """
    bundle_ids = manifest.get("bundle_ids", [])
    idx = manifest.get("current_index", 0)

    if not bundle_ids:
        manifest["current_index"] = 0
        return manifest

    idx += 1
    if idx >= len(bundle_ids):
        idx = len(bundle_ids)  # "past the end" → done

    manifest["current_index"] = idx
    return manifest


def is_done(manifest: Dict) -> bool:
    """
    True if we've moved past the last bundle.
    """
    bundle_ids = manifest.get("bundle_ids", [])
    idx = manifest.get("current_index", 0)
    return idx >= len(bundle_ids)
