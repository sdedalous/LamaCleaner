import os
import base64
from io import BytesIO
import numpy as np
from PIL import Image

from lama_cleaner.schema import Config, HDStrategy

from backend.lama_loader import lama
from backend.zits_loader import zits
from backend.ldm_loader import ldm
from backend.mat_loader import mat

MODEL_MAP = {
    "lama": lama,
    "zits": zits,
    "ldm": ldm,
    "mat": mat,
}

BUNDLE_ROOT = "data/images"


def run_inpaint_v2(
    bundle_id: str,
    mask_base64: str,
    model_name: str,
    steps: int,
    hd_strategy: str
):
    """
    BUNDLE MODE

    bundle_id = folder name under data/images

    Reads:
        data/images/<bundle_id>/normalized.png

    Writes:
        data/images/<bundle_id>/inpaint.png
    """

    try:
        # ---------------------------------------------------------
        # Resolve bundle paths
        # ---------------------------------------------------------
        bundle_dir = os.path.join(BUNDLE_ROOT, bundle_id)
        normalized_path = os.path.join(bundle_dir, "normalized.png")
        inpaint_path = os.path.join(bundle_dir, "inpaint.png")

        if not os.path.exists(normalized_path):
            return {
                "ok": False,
                "error": f"Missing normalized image: {normalized_path}",
                "result_base64": None,
                "bundle_id": bundle_id,
            }

        # ---------------------------------------------------------
        # Start from latest inpaint if it exists, otherwise normalized
        # (makes edits cumulative)
        # ---------------------------------------------------------
        if os.path.exists(inpaint_path):
            src_path = inpaint_path
        else:
            src_path = normalized_path

        print("🔥 DEBUG run_inpaint_v2: src_path =", src_path)

        # ---------------------------------------------------------
        # Load source image
        # ---------------------------------------------------------
        src_img = Image.open(src_path)
        src_img.load()
        icc_profile = src_img.info.get("icc_profile", None)

        src_np_full = np.array(src_img)

        # Extract RGB + alpha
        if src_img.mode == "RGBA":
            rgb_np = src_np_full[..., :3]
            alpha_np = src_np_full[..., 3]
            alpha = Image.fromarray(alpha_np)
        else:
            rgb_np = src_np_full
            alpha = None

        rgb_img = Image.fromarray(rgb_np)

        # ---------------------------------------------------------
        # Decode mask
        # ---------------------------------------------------------
        # ---------------------------------------------------------
        # If mask_base64 is empty → do NOT inpaint
        # ---------------------------------------------------------
        if not mask_base64:
            print("🔥 DEBUG: Empty mask received — skipping inpaint")
            return {
                "ok": True,
                "result_base64": None,
                "bundle_id": bundle_id,
                "error": "EMPTY_MASK"
            }

        mask_bytes = base64.b64decode(mask_base64)
        mask_img = Image.open(BytesIO(mask_bytes)).convert("L")
        mask_img = mask_img.resize(rgb_img.size, Image.NEAREST)
        # Save the actual mask for future sessions
        mask_img.save(os.path.join(bundle_dir, "mask.png"))

        # ---------------------------------------------------------
        # Resolution corridor
        # ---------------------------------------------------------
        orig_w, orig_h = rgb_img.size
        MIN_RES = 1000
        MAX_RES = 2048

        if orig_w < MIN_RES or orig_h < MIN_RES:
            working_img = rgb_img
            working_mask = mask_img

        elif orig_w > MAX_RES or orig_h > MAX_RES:
            resize_factor = min(MAX_RES / orig_w, MAX_RES / orig_h)
            new_w = int(orig_w * resize_factor)
            new_h = int(orig_h * resize_factor)

            working_img = rgb_img.resize((new_w, new_h), Image.LANCZOS)
            working_mask = mask_img.resize((new_w, new_h), Image.NEAREST)

        else:
            working_img = rgb_img
            working_mask = mask_img

        working_np = np.array(working_img)
        working_mask_np = np.array(working_mask)
        working_mask_np = 255 - working_mask_np

        # ---------------------------------------------------------
        # Run model
        # ---------------------------------------------------------
        if model_name not in MODEL_MAP:
            return {
                "ok": False,
                "error": f"Unknown model: {model_name}",
                "result_base64": None,
                "bundle_id": bundle_id,
            }

        model = MODEL_MAP[model_name]

        config = Config(
            ldm_steps=int(steps),
            hd_strategy=HDStrategy[hd_strategy],
            hd_strategy_crop_margin=128,
            hd_strategy_crop_trigger_size=512,
            hd_strategy_resize_limit=2048,
        )

        inpainted_np = model(
            working_np.astype(np.uint8),
            working_mask_np,
            config,
        )

        inpainted_np = np.clip(inpainted_np, 0, 255).astype(np.uint8)
        inpainted_np = inpainted_np[..., ::-1]  # BGR → RGB

        # ---------------------------------------------------------
        # Rebuild image
        # ---------------------------------------------------------
        if alpha is not None:
            result_img = Image.fromarray(inpainted_np).convert("RGBA")
            result_img.putalpha(alpha)
        else:
            result_img = Image.fromarray(inpainted_np)

        # ---------------------------------------------------------
        # Save output inside bundle
        # ---------------------------------------------------------
        save_kwargs = {}
        if icc_profile:
            save_kwargs["icc_profile"] = icc_profile

        result_img.save(inpaint_path, **save_kwargs)

        # ---------------------------------------------------------
        # Return base64
        # ---------------------------------------------------------
        buffer = BytesIO()
        result_img.save(buffer, format="PNG")
        result_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        result_base64 = "data:image/png;base64," + result_base64

        return {
            "ok": True,
            "result_base64": result_base64,
            "bundle_id": bundle_id,
            "error": None,
        }

    except Exception as e:
        print("🔥 INPAINT_V2 ERROR:", e)
        return {
            "ok": False,
            "error": str(e),
            "result_base64": None,
            "bundle_id": bundle_id,
        }
