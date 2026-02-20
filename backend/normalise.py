import os
import shutil
import json
from datetime import datetime
from PIL import Image
import numpy as np

# ---------------------------------------------------------
# NORMALISATION SETTINGS
# ---------------------------------------------------------
MAX_SIZE = 1400          # longest side cap
BLACK_THRESHOLD = 5      # pixel intensity threshold for padding detection

# ---------------------------------------------------------
# BUNDLE SETTINGS
# ---------------------------------------------------------
BUNDLE_ROOT = "data/images"
EXCLUSIONS_FILE = "data/exclusions.json"


# ---------------------------------------------------------
# Utility: ensure directory exists
# ---------------------------------------------------------
def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


# ---------------------------------------------------------
# Exclusion file helpers
# ---------------------------------------------------------
def ensure_exclusions_file():
    if not os.path.exists(EXCLUSIONS_FILE):
        with open(EXCLUSIONS_FILE, "w") as f:
            json.dump({"watermark": [], "delete": []}, f, indent=4)

def load_exclusions():
    ensure_exclusions_file()
    with open(EXCLUSIONS_FILE, "r") as f:
        return json.load(f)

def save_exclusions(data):
    with open(EXCLUSIONS_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ---------------------------------------------------------
# Create bundle directory
# ---------------------------------------------------------
def create_bundle_dir(image_id):
    bundle_dir = os.path.join(BUNDLE_ROOT, image_id)
    ensure_dir(bundle_dir)
    return bundle_dir


# ---------------------------------------------------------
# Save metadata.json
# ---------------------------------------------------------
def save_metadata(bundle_dir, metadata):
    meta_path = os.path.join(bundle_dir, "metadata.json")
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=4)


# ---------------------------------------------------------
# Detect black padding on all four sides
# ---------------------------------------------------------
def detect_black_padding(img: Image.Image):
    arr = np.array(img)

    # If RGBA, operate on RGB only
    if arr.ndim == 3 and arr.shape[2] == 4:
        rgb = arr[:, :, :3]
    else:
        rgb = arr

    h, w, _ = rgb.shape

    gray = np.mean(rgb, axis=2)
    black_mask = gray < BLACK_THRESHOLD

    top = 0
    while top < h and black_mask[top, :].all():
        top += 1

    bottom = h - 1
    while bottom >= 0 and black_mask[bottom, :].all():
        bottom -= 1

    left = 0
    while left < w and black_mask[:, left].all():
        left += 1

    right = w - 1
    while right >= 0 and black_mask[:, right].all():
        right -= 1

    if left >= right or top >= bottom:
        return (0, 0, w, h)

    return (left, top, right + 1, bottom + 1)


# ---------------------------------------------------------
# Downscale if image is too large
# ---------------------------------------------------------
def downscale_if_needed(img: Image.Image):
    w, h = img.size
    longest = max(w, h)

    if longest <= MAX_SIZE:
        return img

    scale = MAX_SIZE / longest
    new_w = int(w * scale)
    new_h = int(h * scale)

    return img.resize((new_w, new_h), Image.LANCZOS)


# ---------------------------------------------------------
# Main bundle-aware normalisation function
# ---------------------------------------------------------
def normalise_into_bundle(image_id: str, raw_path: str):
    # 1. Create bundle directory
    bundle_dir = create_bundle_dir(image_id)

    # 2. Copy raw image into bundle
    raw_out = os.path.join(bundle_dir, "raw.png")
    shutil.copy(raw_path, raw_out)

    # 3. Load image
    img = Image.open(raw_out)
    raw_w, raw_h = img.size
    has_alpha = img.mode == "RGBA"

    # 4. Separate alpha if present
    alpha = None
    if has_alpha:
        rgb = img.convert("RGB")
        alpha = img.split()[-1]
    else:
        rgb = img.convert("RGB")

    # 5. Remove black padding
    crop_box = detect_black_padding(rgb)
    rgb = rgb.crop(crop_box)
    if alpha is not None:
        alpha = alpha.crop(crop_box)

    # 6. Downscale if needed
    rgb = downscale_if_needed(rgb)
    if alpha is not None:
        alpha = downscale_if_needed(alpha)

    # 7. Save alpha if present
    alpha_out = os.path.join(bundle_dir, "alpha.png")
    if alpha is not None:
        alpha.save(alpha_out)

    # 8. Recombine alpha for normalized preview
    if alpha is not None:
        rgb.putalpha(alpha)

    # 9. Save normalized image
    normalized_out = os.path.join(bundle_dir, "normalized.png")
    rgb.save(normalized_out)

    # 10. Build metadata.json
    metadata = {
        "image_id": image_id,
        "original_filename": os.path.basename(raw_path),
        "raw_dimensions": {"width": raw_w, "height": raw_h},
        "normalized_dimensions": {
            "width": rgb.size[0],
            "height": rgb.size[1]
        },
        "has_alpha": has_alpha,
        "normalization": {
            "removed_padding": crop_box != (0, 0, raw_w, raw_h),
            "downscaled": max(raw_w, raw_h) > MAX_SIZE,
            "downscale_factor": MAX_SIZE / max(raw_w, raw_h) if max(raw_w, raw_h) > MAX_SIZE else 1.0,
            "exif_orientation_fixed": False
        },
        "status": "pending",
        "excluded": False,
        "exclude_reason": None,
        "routing": {"destination": "main"},
        "timestamps": {
            "normalized_at": datetime.utcnow().isoformat(),
            "edit_completed_at": None,
            "routed_at": None
        }
    }

    save_metadata(bundle_dir, metadata)

    # 11. Return normalized path for frontend
    return {
        "ok": True,
        "bundle_dir": bundle_dir,
        "raw": raw_out,
        "normalized": normalized_out,
        "alpha": alpha_out if has_alpha else None,
        "crop_box": crop_box,
        "final_size": rgb.size
    }
import os
import shutil
import json
from datetime import datetime
from PIL import Image
import numpy as np

# ---------------------------------------------------------
# NORMALISATION SETTINGS
# ---------------------------------------------------------
MAX_SIZE = 1400          # longest side cap
BLACK_THRESHOLD = 5      # pixel intensity threshold for padding detection

# ---------------------------------------------------------
# BUNDLE SETTINGS
# ---------------------------------------------------------
BUNDLE_ROOT = "data/images"
EXCLUSIONS_FILE = "data/exclusions.json"


# ---------------------------------------------------------
# Utility: ensure directory exists
# ---------------------------------------------------------
def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


# ---------------------------------------------------------
# Exclusion file helpers
# ---------------------------------------------------------
def ensure_exclusions_file():
    if not os.path.exists(EXCLUSIONS_FILE):
        with open(EXCLUSIONS_FILE, "w") as f:
            json.dump({"watermark": [], "delete": []}, f, indent=4)

def load_exclusions():
    ensure_exclusions_file()
    with open(EXCLUSIONS_FILE, "r") as f:
        return json.load(f)

def save_exclusions(data):
    with open(EXCLUSIONS_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ---------------------------------------------------------
# Create bundle directory
# ---------------------------------------------------------
def create_bundle_dir(image_id):
    bundle_dir = os.path.join(BUNDLE_ROOT, image_id)
    ensure_dir(bundle_dir)
    return bundle_dir


# ---------------------------------------------------------
# Save metadata.json
# ---------------------------------------------------------
def save_metadata(bundle_dir, metadata):
    meta_path = os.path.join(bundle_dir, "metadata.json")
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=4)


# ---------------------------------------------------------
# Detect black padding on all four sides
# ---------------------------------------------------------
def detect_black_padding(img: Image.Image):
    arr = np.array(img)

    # If RGBA, operate on RGB only
    if arr.ndim == 3 and arr.shape[2] == 4:
        rgb = arr[:, :, :3]
    else:
        rgb = arr

    h, w, _ = rgb.shape

    gray = np.mean(rgb, axis=2)
    black_mask = gray < BLACK_THRESHOLD

    top = 0
    while top < h and black_mask[top, :].all():
        top += 1

    bottom = h - 1
    while bottom >= 0 and black_mask[bottom, :].all():
        bottom -= 1

    left = 0
    while left < w and black_mask[:, left].all():
        left += 1

    right = w - 1
    while right >= 0 and black_mask[:, right].all():
        right -= 1

    if left >= right or top >= bottom:
        return (0, 0, w, h)

    return (left, top, right + 1, bottom + 1)


# ---------------------------------------------------------
# Downscale if image is too large
# ---------------------------------------------------------
def downscale_if_needed(img: Image.Image):
    w, h = img.size
    longest = max(w, h)

    if longest <= MAX_SIZE:
        return img

    scale = MAX_SIZE / longest
    new_w = int(w * scale)
    new_h = int(h * scale)

    return img.resize((new_w, new_h), Image.LANCZOS)


# ---------------------------------------------------------
# Main bundle-aware normalisation function
# ---------------------------------------------------------
def normalise_into_bundle(image_id: str, raw_path: str):
    # 1. Create bundle directory
    bundle_dir = create_bundle_dir(image_id)

    # 2. Copy raw image into bundle
    raw_out = os.path.join(bundle_dir, "raw.png")
    shutil.copy(raw_path, raw_out)

    # 3. Load image
    img = Image.open(raw_out)
    raw_w, raw_h = img.size
    has_alpha = img.mode == "RGBA"

    # 4. Separate alpha if present
    alpha = None
    if has_alpha:
        rgb = img.convert("RGB")
        alpha = img.split()[-1]
    else:
        rgb = img.convert("RGB")

    # 5. Remove black padding
    crop_box = detect_black_padding(rgb)
    rgb = rgb.crop(crop_box)
    if alpha is not None:
        alpha = alpha.crop(crop_box)

    # 6. Downscale if needed
    rgb = downscale_if_needed(rgb)
    if alpha is not None:
        alpha = downscale_if_needed(alpha)

    # 7. Save alpha if present
    alpha_out = os.path.join(bundle_dir, "alpha.png")
    if alpha is not None:
        alpha.save(alpha_out)

    # 8. Recombine alpha for normalized preview
    if alpha is not None:
        rgb.putalpha(alpha)

    # 9. Save normalized image
    normalized_out = os.path.join(bundle_dir, "normalized.png")
    rgb.save(normalized_out)

    # 10. Build metadata.json
    metadata = {
        "image_id": image_id,
        "original_filename": os.path.basename(raw_path),
        "raw_dimensions": {"width": raw_w, "height": raw_h},
        "normalized_dimensions": {
            "width": rgb.size[0],
            "height": rgb.size[1]
        },
        "has_alpha": has_alpha,
        "normalization": {
            "removed_padding": crop_box != (0, 0, raw_w, raw_h),
            "downscaled": max(raw_w, raw_h) > MAX_SIZE,
            "downscale_factor": MAX_SIZE / max(raw_w, raw_h) if max(raw_w, raw_h) > MAX_SIZE else 1.0,
            "exif_orientation_fixed": False
        },
        "status": "pending",
        "excluded": False,
        "exclude_reason": None,
        "routing": {"destination": "main"},
        "timestamps": {
            "normalized_at": datetime.utcnow().isoformat(),
            "edit_completed_at": None,
            "routed_at": None
        }
    }

    save_metadata(bundle_dir, metadata)

    # 11. Return normalized path for frontend
    return {
        "ok": True,
        "bundle_dir": bundle_dir,
        "raw": raw_out,
        "normalized": normalized_out,
        "alpha": alpha_out if has_alpha else None,
        "crop_box": crop_box,
        "final_size": rgb.size
    }
import os
import shutil
import json
from datetime import datetime
from PIL import Image
import numpy as np

# ---------------------------------------------------------
# NORMALISATION SETTINGS
# ---------------------------------------------------------
MAX_SIZE = 1400          # longest side cap
BLACK_THRESHOLD = 5      # pixel intensity threshold for padding detection

# ---------------------------------------------------------
# BUNDLE SETTINGS
# ---------------------------------------------------------
BUNDLE_ROOT = "data/images"
EXCLUSIONS_FILE = "data/exclusions.json"


# ---------------------------------------------------------
# Utility: ensure directory exists
# ---------------------------------------------------------
def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


# ---------------------------------------------------------
# Exclusion file helpers
# ---------------------------------------------------------
def ensure_exclusions_file():
    if not os.path.exists(EXCLUSIONS_FILE):
        with open(EXCLUSIONS_FILE, "w") as f:
            json.dump({"watermark": [], "delete": []}, f, indent=4)

def load_exclusions():
    ensure_exclusions_file()
    with open(EXCLUSIONS_FILE, "r") as f:
        return json.load(f)

def save_exclusions(data):
    with open(EXCLUSIONS_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ---------------------------------------------------------
# Create bundle directory
# ---------------------------------------------------------
def create_bundle_dir(image_id):
    bundle_dir = os.path.join(BUNDLE_ROOT, image_id)
    ensure_dir(bundle_dir)
    return bundle_dir


# ---------------------------------------------------------
# Save metadata.json
# ---------------------------------------------------------
def save_metadata(bundle_dir, metadata):
    meta_path = os.path.join(bundle_dir, "metadata.json")
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=4)


# ---------------------------------------------------------
# Detect black padding on all four sides
# ---------------------------------------------------------
def detect_black_padding(img: Image.Image):
    arr = np.array(img)

    # If RGBA, operate on RGB only
    if arr.ndim == 3 and arr.shape[2] == 4:
        rgb = arr[:, :, :3]
    else:
        rgb = arr

    h, w, _ = rgb.shape

    gray = np.mean(rgb, axis=2)
    black_mask = gray < BLACK_THRESHOLD

    top = 0
    while top < h and black_mask[top, :].all():
        top += 1

    bottom = h - 1
    while bottom >= 0 and black_mask[bottom, :].all():
        bottom -= 1

    left = 0
    while left < w and black_mask[:, left].all():
        left += 1

    right = w - 1
    while right >= 0 and black_mask[:, right].all():
        right -= 1

    if left >= right or top >= bottom:
        return (0, 0, w, h)

    return (left, top, right + 1, bottom + 1)


# ---------------------------------------------------------
# Downscale if image is too large
# ---------------------------------------------------------
def downscale_if_needed(img: Image.Image):
    w, h = img.size
    longest = max(w, h)

    if longest <= MAX_SIZE:
        return img

    scale = MAX_SIZE / longest
    new_w = int(w * scale)
    new_h = int(h * scale)

    return img.resize((new_w, new_h), Image.LANCZOS)


# ---------------------------------------------------------
# Main bundle-aware normalisation function
# ---------------------------------------------------------
def normalise_into_bundle(image_id: str, raw_path: str):
    # 1. Create bundle directory
    bundle_dir = create_bundle_dir(image_id)

    # 2. Copy raw image into bundle
    raw_out = os.path.join(bundle_dir, "raw.png")
    shutil.copy(raw_path, raw_out)

    # 3. Load image
    img = Image.open(raw_out)
    raw_w, raw_h = img.size
    has_alpha = img.mode == "RGBA"

    # 4. Separate alpha if present
    alpha = None
    if has_alpha:
        rgb = img.convert("RGB")
        alpha = img.split()[-1]
    else:
        rgb = img.convert("RGB")

    # 5. Remove black padding
    crop_box = detect_black_padding(rgb)
    rgb = rgb.crop(crop_box)
    if alpha is not None:
        alpha = alpha.crop(crop_box)

    # 6. Downscale if needed
    rgb = downscale_if_needed(rgb)
    if alpha is not None:
        alpha = downscale_if_needed(alpha)

    # 7. Save alpha if present
    alpha_out = os.path.join(bundle_dir, "alpha.png")
    if alpha is not None:
        alpha.save(alpha_out)

    # 8. Recombine alpha for normalized preview
    if alpha is not None:
        rgb.putalpha(alpha)

    # 9. Save normalized image
    normalized_out = os.path.join(bundle_dir, "normalized.png")
    rgb.save(normalized_out)

    # 10. Build metadata.json
    metadata = {
        "image_id": image_id,
        "original_filename": os.path.basename(raw_path),
        "raw_dimensions": {"width": raw_w, "height": raw_h},
        "normalized_dimensions": {
            "width": rgb.size[0],
            "height": rgb.size[1]
        },
        "has_alpha": has_alpha,
        "normalization": {
            "removed_padding": crop_box != (0, 0, raw_w, raw_h),
            "downscaled": max(raw_w, raw_h) > MAX_SIZE,
            "downscale_factor": MAX_SIZE / max(raw_w, raw_h) if max(raw_w, raw_h) > MAX_SIZE else 1.0,
            "exif_orientation_fixed": False
        },
        "status": "pending",
        "excluded": False,
        "exclude_reason": None,
        "routing": {"destination": "main"},
        "timestamps": {
            "normalized_at": datetime.utcnow().isoformat(),
            "edit_completed_at": None,
            "routed_at": None
        }
    }

    save_metadata(bundle_dir, metadata)

    # 11. Return normalized path for frontend
    return {
        "ok": True,
        "bundle_dir": bundle_dir,
        "raw": raw_out,
        "normalized": normalized_out,
        "alpha": alpha_out if has_alpha else None,
        "crop_box": crop_box,
        "final_size": rgb.size
    }
