import os

def get_nth_image(root: str, n: int):
    """
    Lazily return the nth image file in `root`.
    No recursion. No preloading. No sorting.
    Returns None if no such file exists.
    """
    exts = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
    count = 0

    try:
        for entry in os.scandir(root):
            if not entry.is_file():
                continue

            ext = os.path.splitext(entry.name)[1].lower()
            if ext not in exts:
                continue

            if count == n:
                return entry.path

            count += 1

    except FileNotFoundError:
        return None

    return None
