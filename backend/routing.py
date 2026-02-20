import os
import json
from datetime import datetime

BUNDLE_ROOT = "data/images"
EXCLUSIONS_FILE = "data/exclusions.json"

def load_metadata(bundle_dir):
    meta_path = os.path.join(bundle_dir, "metadata.json")
    with open(meta_path, "r") as f:
        return json.load(f)

def save_metadata(bundle_dir, metadata):
    meta_path = os.path.join(bundle_dir, "metadata.json")
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=4)

def load_exclusions():
    if not os.path.exists(EXCLUSIONS_FILE):
        with open(EXCLUSIONS_FILE, "w") as f:
            json.dump({"watermark": [], "delete": []}, f, indent=4)
    with open(EXCLUSIONS_FILE, "r") as f:
        return json.load(f)

def save_exclusions(data):
    with open(EXCLUSIONS_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ---------------------------------------------------------
# ROUTE: Mark as done
# ---------------------------------------------------------
def route_mark_done(image_id):
    bundle_dir = os.path.join(BUNDLE_ROOT, image_id)
    metadata = load_metadata(bundle_dir)

    metadata["status"] = "completed"
    metadata["routing"]["destination"] = "main"
    metadata["timestamps"]["edit_completed_at"] = datetime.utcnow().isoformat()

    save_metadata(bundle_dir, metadata)

    return {"ok": True, "routed": "main"}


# ---------------------------------------------------------
# ROUTE: Send to large model
# ---------------------------------------------------------
def route_large_model(image_id):
    bundle_dir = os.path.join(BUNDLE_ROOT, image_id)
    metadata = load_metadata(bundle_dir)

    metadata["status"] = "routed"
    metadata["routing"]["destination"] = "large_model"
    metadata["timestamps"]["routed_at"] = datetime.utcnow().isoformat()

    save_metadata(bundle_dir, metadata)

    return {"ok": True, "routed": "large_model"}


# ---------------------------------------------------------
# ROUTE: Watermark or Delete (excluded)
# ---------------------------------------------------------
def route_exclude(image_id, reason):
    assert reason in ("watermark", "delete")

    bundle_dir = os.path.join(BUNDLE_ROOT, image_id)
    metadata = load_metadata(bundle_dir)

    metadata["excluded"] = True
    metadata["exclude_reason"] = reason
    metadata["status"] = "excluded"
    metadata["timestamps"]["routed_at"] = datetime.utcnow().isoformat()

    save_metadata(bundle_dir, metadata)

    # Append to exclusions.json
    exclusions = load_exclusions()
    exclusions[reason].append(image_id)
    save_exclusions(exclusions)

    return {"ok": True, "excluded": reason}
