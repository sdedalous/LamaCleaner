import os
import json
import base64
from pathlib import Path

# =============================================================
# ROOT DATA DIRECTORY (V2)
# =============================================================
# All bundle folders live under:
#     data/images/<bundle_id>/
# =============================================================

DATA_ROOT = Path("data/images")


# =============================================================
# BUNDLE HELPERS
# =============================================================

def ensure_bundle(bundle_id: str) -> Path:
    """
    Ensure the bundle directory exists:
        data/images/<bundle_id>/
    """
    bundle_path = DATA_ROOT / bundle_id
    bundle_path.mkdir(parents=True, exist_ok=True)
    return bundle_path


# =============================================================
# IMAGE HELPERS
# =============================================================

def save_base64_image(base64_str: str, out_path: Path):
    """
    Save a base64 PNG string to disk.
    """
    if "," in base64_str:
        _, encoded = base64_str.split(",", 1)
    else:
        encoded = base64_str

    img_bytes = base64.b64decode(encoded)
    out_path.write_bytes(img_bytes)


# =============================================================
# JSON HELPERS
# =============================================================

def load_json(path: Path, default=None):
    """
    Load JSON from disk. If missing, return default.
    """
    if not path.exists():
        return default if default is not None else {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return default if default is not None else {}


def save_json(path: Path, data: dict):
    """
    Save JSON to disk with indentation.
    """
    path.write_text(json.dumps(data, indent=4))


# =============================================================
# OPTIONAL: SAFE DELETE (used by legacy routing)
# =============================================================

def delete_image():
    """
    Legacy compatibility: delete the current image.
    This is still used by routing endpoints.
    """
    return {"ok": True, "message": "delete_image not implemented in V2"}


# =============================================================
# OPTIONAL: SAVE WATERMARKED (legacy compatibility)
# =============================================================

async def save_watermarked(file):
    """
    Legacy compatibility: save uploaded watermarked file.
    Not used in V2 pipeline.
    """
    return {"ok": True, "message": "save_watermarked not implemented in V2"}
