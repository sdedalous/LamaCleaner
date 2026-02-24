import base64
import io
from PIL import Image
import numpy as np
from rembg import remove

import base64
import io
from PIL import Image
import numpy as np
from rembg import remove

def run_rembg(image_base64: str):
    try:
        # Accept both "data:image/png;base64,XXXX" and "XXXX"
        if "," in image_base64:
            _, encoded = image_base64.split(",", 1)
        else:
            encoded = image_base64

        img_bytes = base64.b64decode(encoded)
        img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")

        result = remove(img)

        alpha = result.split()[-1]
        mask = Image.fromarray(np.array(alpha))

        buf = io.BytesIO()
        mask.save(buf, format="PNG")
        mask_b64 = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

        return { "ok": True, "mask_base64": mask_b64 }

    except Exception as e:
        return { "ok": False, "error": str(e) }

