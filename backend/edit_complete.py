import os
import json
from datetime import datetime
from PIL import Image
import base64
import io

BUNDLE_ROOT = "data/images"

def load_metadata(bundle_dir):
    meta_path = os.path.join(bundle_dir, "metadata.json")
    with open(meta_path, "r") as f:
        return json.load(f)

def save_metadata(bundle_dir, metadata):
    meta_path = os.path.join(bundle_dir, "metadata.json")
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=4)

# ---------------------------------------------------------
# Save final edited image into bundle as edit_result.png
# ---------------------------------------------------------
def save_edit_result(image_id: str, edited_base64: str):
    bundle_dir = os.path.join(BUNDLE_ROOT, image_id)
    result_path = os.path.join(bundle_dir, "edit_result.png")

    # Decode base64 → PIL image
    img_bytes = base64.b64decode(edited_base64)
    img = Image.open(io.BytesIO(img_bytes))

    # Save final edited image
    img.save(result_path)

    # Update metadata
    metadata = load_metadata(bundle_dir)
    metadata["status"] = "completed"
    metadata["routing"]["destination"] = "main"
    metadata["timestamps"]["edit_completed_at"] = datetime.utcnow().isoformat()

    save_metadata(bundle_dir, metadata)

    return {
        "ok": True,
        "edit_result": result_path,
        "bundle_dir": bundle_dir
    }
