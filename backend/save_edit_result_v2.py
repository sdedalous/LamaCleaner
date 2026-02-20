import os
import base64
from io import BytesIO
from PIL import Image

IMAGES_ROOT = "data/images"


def save_edit_result_v2(bundle_id: str, edited_base64: str):
    """
    Save the final edited image for a bundle.

    Reads:
        edited_base64 (PNG data from the canvas)

    Writes:
        data/images/<bundle_id>/edit_result.png

    Returns:
        {
            ok: True/False,
            url: "/image?path=...",
            bundle_id: <bundle_id>,
            error: None or str
        }
    """

    try:
        # ---------------------------------------------------------
        # Resolve bundle paths
        # ---------------------------------------------------------
        bundle_dir = os.path.join(IMAGES_ROOT, bundle_id)
        out_path = os.path.join(bundle_dir, "edit_result.png")

        if not os.path.exists(bundle_dir):
            return {
                "ok": False,
                "error": f"Bundle directory not found: {bundle_id}"
            }

        # ---------------------------------------------------------
        # Decode base64 → PIL image
        # ---------------------------------------------------------
        try:
            img_bytes = base64.b64decode(edited_base64)
        except Exception:
            return {
                "ok": False,
                "error": "Invalid base64 image data"
            }

        img = Image.open(BytesIO(img_bytes))

        # ---------------------------------------------------------
        # Save final edited image
        # ---------------------------------------------------------
        img.save(out_path, format="PNG")

        # ---------------------------------------------------------
        # Return clean URL
        # ---------------------------------------------------------
        url = f"/image?path={out_path}"

        return {
            "ok": True,
            "url": url,
            "bundle_id": bundle_id,
            "error": None
        }

    except Exception as e:
        print("🔥 SAVE_EDIT_RESULT_V2 ERROR:", e)
        return {
            "ok": False,
            "error": str(e),
            "url": None
        }
