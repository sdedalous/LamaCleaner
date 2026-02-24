from typing import List
import os
import json
import time
from backend.sha_helper import get_nth_image
from backend.hash_utils import compute_sha1
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Backend modules
from backend.edit_complete import save_edit_result
from backend.save_edit_result_v2 import save_edit_result_v2
from backend.export_dataset_v2 import export_dataset_v2
from backend.image_loop import get_next_image, mark_done
from backend.file_ops import delete_image, save_watermarked
from backend.backend_crop import run_crop

# Routing helpers
from backend.routing import (
    route_mark_done,
    route_large_model,
    route_exclude
)

print(">>> USING MAIN.PY FROM:", __file__)

# =============================================================
# CONFIG + FRONTEND SETUP
# =============================================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
CONFIG_PATH = os.path.join(PROJECT_ROOT, "config", "config.json")
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")

def load_app_config():
    if not os.path.exists(CONFIG_PATH):
        raise RuntimeError(f"Config file not found: {CONFIG_PATH}")
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

app_config = load_app_config()
print(">>> BACKEND CONFIG LOADED:", app_config)

app = FastAPI()

# Serve frontend
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")

@app.get("/")
def serve_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================
# API MODELS
# =============================================================

class InitSessionRequest(BaseModel):
    target_dir: str
    watermarked_dir: str
    include_subfolders: bool

class CropRequest(BaseModel):
    crop_box: List[int]

class InpaintRequest(BaseModel):
    mask_base64: str
    steps: int | None = None
    hd_strategy: str | None = None
    bundle_id: str | None = None

class UpdateConfigRequest(BaseModel):
    model: str | None = None
    steps: int | None = None
    hd_strategy: str | None = None

# =============================================================
# CONFIG ENDPOINTS
# =============================================================

@app.get("/config")
def get_config():
    return app_config

@app.post("/config")
def update_config(req: UpdateConfigRequest):
    cfg = load_app_config()
    changed_model = False

    if req.model is not None and req.model != cfg.get("model"):
        cfg["model"] = req.model
        changed_model = True

    if req.steps is not None:
        cfg["steps"] = int(req.steps)

    if req.hd_strategy is not None:
        cfg["hd_strategy"] = req.hd_strategy

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

    return {
        "ok": True,
        "config": cfg,
        "restart_required": changed_model
    }

# =============================================================
# IMAGE SERVING
# =============================================================

from fastapi import HTTPException
from fastapi.responses import FileResponse
from urllib.parse import unquote
from pathlib import Path

@app.get("/image")
def serve_image(path: str):
    # 1. URL-decode (%20 → space, %27 → ')
    decoded = unquote(path)

    # 2. Normalize Windows path separators
    normalized = Path(decoded)

    # 3. Validate existence
    if not normalized.exists():
        print("❌ FILE NOT FOUND:", normalized)
        raise HTTPException(status_code=404, detail=f"File not found: {normalized}")

    # 4. Serve the file
    return FileResponse(normalized)


# =============================================================
# BASIC EDITING ENDPOINTS
# =============================================================

@app.post("/crop")
async def crop_endpoint(request: CropRequest):
    return run_crop(request.crop_box)

@app.post("/save_edit_result")
async def save_edit_result_endpoint(image_id: str, edited_base64: str):
    return save_edit_result(image_id, edited_base64)

# =============================================================
# ROUTING ENDPOINTS
# =============================================================

@app.post("/route/mark_done")
async def api_route_mark_done(image_id: str):
    return route_mark_done(image_id)

@app.post("/route/large_model")
async def api_route_large_model(image_id: str):
    return route_large_model(image_id)

@app.post("/route/exclude")
async def api_route_exclude(image_id: str, reason: str):
    return route_exclude(image_id, reason)

# =============================================================
# V2 SESSION + NAVIGATION
# =============================================================

from backend.manifest_v2 import (
    create_manifest_v2,
    load_manifest_v2,
    save_manifest_v2,
    get_current_bundle_id,
    advance_to_next_bundle,
    is_done
)

class InitRequest(BaseModel):
    target_dir: str

def discover_images(root):
    """
    Return all image files directly inside `root`.
    No recursion. No subfolder logic.
    """
    exts = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
    results = []

    for entry in os.scandir(root):
        if entry.is_file():
            ext = os.path.splitext(entry.name)[1].lower()
            if ext in exts:
                results.append(entry.path)

    return sorted(results)


@app.post("/init_session_v2")
async def init_session_v2(req: InitRequest):
    """
    Initialize a V2 session using lazy scanning.
    We do NOT preload or scan the folder.
    We simply store the target directory and start at index 0.
    """
    manifest = {
        "target_dir": req.target_dir,
        "current_index": 0
    }

    save_manifest_v2(manifest)

    return {
        "ok": True,
        "message": "V2 session initialized"
    }

@app.get("/reload_bundle_v2")
async def reload_bundle_v2(bundle_id: str):
    """
    Reload the CURRENT bundle without advancing the manifest index.

    Returns:
        - url: inpaint.png if it exists, else normalized.png
        - mask_url: mask.png if it exists
    """
    bundle_dir = os.path.join("data/images", bundle_id)
    normalized_path = os.path.join(bundle_dir, "normalized.png")
    inpaint_path = os.path.join(bundle_dir, "inpaint.png")
    mask_path = os.path.join(bundle_dir, "mask.png")

    if not os.path.exists(normalized_path) and not os.path.exists(inpaint_path):
        return {
            "ok": False,
            "error": f"No images found for bundle_id={bundle_id}",
            "url": None,
            "mask_url": None,
            "bundle_id": bundle_id,
        }

    # Prefer inpaint.png if it exists
    if os.path.exists(inpaint_path):
        url = f"/image?path=data/images/{bundle_id}/inpaint.png"
    else:
        url = f"/image?path=data/images/{bundle_id}/normalized.png"

    mask_url = None
    if os.path.exists(mask_path):
        mask_url = f"/image?path=data/images/{bundle_id}/mask.png"

    return {
        "ok": True,
        "error": None,
        "bundle_id": bundle_id,
        "url": url,
        "mask_url": mask_url,
    }


@app.get("/next_image_v2")
async def next_image_v2():
    manifest = load_manifest_v2()
    if manifest is None:
        return {"ok": False, "error": "No v2 manifest found"}

    target_dir = manifest["target_dir"]
    idx = manifest["current_index"]

    # Lazily get the nth image
    raw_path = get_nth_image(target_dir, idx)
    if raw_path is None:
        return {"ok": True, "done": True, "url": None}

    # Compute SHA-1 for bundle identity
    sha1 = compute_sha1(raw_path)

    # Bundle ID = stem + sha1
    stem = os.path.splitext(os.path.basename(raw_path))[0]
    bundle_id = f"{stem}__sha1_{sha1}"

    # Bundle directory
    bundle_dir = os.path.join("data/images", bundle_id)
    normalized_path = os.path.join(bundle_dir, "normalized.png")

    # Normalize only if bundle doesn't exist
    if not os.path.exists(normalized_path):
        from backend.normalise import normalise_into_bundle
        normalise_into_bundle(bundle_id, raw_path)

    # Update manifest
    manifest["current_index"] = idx + 1
    save_manifest_v2(manifest)

    # URL for normalized image
    inpaint_path = os.path.join(bundle_dir, "inpaint.png")

    if os.path.exists(inpaint_path):
        url = f"/image?path=data/images/{bundle_id}/inpaint.png"
    else:
        url = f"/image?path=data/images/{bundle_id}/normalized.png"


    # ⭐ Load existing mask if present
    mask_path = os.path.join(bundle_dir, "mask.png")
    mask_url = None
    if os.path.exists(mask_path):
        mask_url = f"/image?path=data/images/{bundle_id}/mask.png"

    # ⭐ Return everything
    return {
        "ok": True,
        "done": False,
        "bundle_id": bundle_id,
        "url": url,
        "mask_url": mask_url,
        "index": idx
    }


# =============================================================
# V2 INPAINT
# =============================================================

from backend.inpaint_v2 import run_inpaint_v2

@app.post("/inpaint_v2")
async def inpaint_v2(request: InpaintRequest):
    # --- DEBUG: confirm the HTTP endpoint is actually being hit ---
    print("🔥 DEBUG: /inpaint_v2 endpoint HIT")
    print("🔥 DEBUG: bundle_id =", request.bundle_id)
    print("🔥 DEBUG: mask_base64 length =", len(request.mask_base64 or ""))

    if not request.bundle_id:
        return {"ok": False, "error": "bundle_id is required"}

    # --- DEBUG: confirm what model + steps the route is passing ---
    model_name = app_config.get("model", "lama")
    steps = request.steps or app_config.get("steps", 20)
    hd_strategy = request.hd_strategy or app_config.get("hd_strategy", "CROP")

    print("🔥 DEBUG: model_name =", model_name)
    print("🔥 DEBUG: steps =", steps)
    print("🔥 DEBUG: hd_strategy =", hd_strategy)

    # --- Call the actual worker function ---
    result = run_inpaint_v2(
        bundle_id=request.bundle_id,
        mask_base64=request.mask_base64,
        model_name=model_name,
        steps=steps,
        hd_strategy=hd_strategy
    )

    # --- DEBUG: confirm the worker returned something ---
    print("🔥 DEBUG: run_inpaint_v2 returned ok =", result.get("ok"))

    return result

# =============================================================
# REMBG ENDPOINT
# =============================================================
from backend.rembg import run_rembg

@app.post("/rembg")
async def rembg_endpoint(payload: dict):
    image_base64 = payload.get("image_base64")
    bundle_id = payload.get("bundle_id")

    if not image_base64:
        return { "ok": False, "error": "Missing image_base64" }

    return run_rembg(image_base64)


# =============================================================
# V2 MULTI-PASS EDITING (NEW)
# =============================================================

from pathlib import Path
import base64
from backend.file_ops import ensure_bundle, save_base64_image, load_json, save_json


@app.post("/save_pass")
def save_pass_endpoint(bundle_id: str, edited_base64: str):
    """
    Save a single editing pass into:
        data/images/<bundle_id>/pass_N/input_crop.png
    and update image_metadata.json with num_passes.
    """
    bundle = ensure_bundle(bundle_id)

    # Metadata path
    meta_path = bundle / "image_metadata.json"
    meta = load_json(meta_path, default={})

    # Determine next pass number
    pass_index = meta.get("num_passes", 0) + 1

    # Create pass folder
    pass_folder = bundle / f"pass_{pass_index}"
    pass_folder.mkdir(exist_ok=True)

    # Save edited image
    save_base64_image(edited_base64, pass_folder / "input_crop.png")

    # Update metadata
    meta["num_passes"] = pass_index
    save_json(meta_path, meta)

    return {
        "ok": True,
        "bundle_id": bundle_id,
        "pass_index": pass_index
    }


@app.post("/reload_base_image")
def reload_base_image_endpoint(bundle_id: str):
    """
    Reload the base-cropped image so the user can begin a new pass.
    Returns base64 PNG for the frontend canvas.
    """
    bundle = ensure_bundle(bundle_id)
    base_crop_path = bundle / "base_crop.png"

    if not base_crop_path.exists():
        return {"ok": False, "error": "base_crop.png missing"}

    img_bytes = base_crop_path.read_bytes()
    encoded = base64.b64encode(img_bytes).decode("utf-8")
    base64_str = f"data:image/png;base64,{encoded}"

    return {
        "ok": True,
        "base_image_base64": base64_str
    }


@app.post("/skip_image")
def skip_image_endpoint(bundle_id: str):
    """
    Mark the image as skipped.
    No passes are saved.
    """
    bundle = ensure_bundle(bundle_id)
    meta_path = bundle / "image_metadata.json"
    meta = load_json(meta_path, default={})

    meta["skipped"] = True
    meta["edited"] = False
    meta["num_passes"] = 0

    save_json(meta_path, meta)

    return {"ok": True, "skipped": True}


@app.post("/finalize_image")
def finalize_image_endpoint(bundle_id: str):
    """
    Mark the image as fully edited.
    num_passes is preserved.
    """
    bundle = ensure_bundle(bundle_id)
    meta_path = bundle / "image_metadata.json"
    meta = load_json(meta_path, default={})

    meta["edited"] = True
    meta["skipped"] = False

    save_json(meta_path, meta)

    return {
        "ok": True,
        "finalized": True,
        "num_passes": meta.get("num_passes", 0)
    }

# =============================================================
# V2 SAVE + EXPORT
# =============================================================

@app.post("/save_edit_result_v2")
async def save_edit_result_v2_endpoint(bundle_id: str, edited_base64: str):
    return save_edit_result_v2(bundle_id, edited_base64)

@app.post("/export_dataset_v2")
async def export_dataset_v2_endpoint(val_split: float = 0.1):
    return export_dataset_v2(val_split=val_split)
