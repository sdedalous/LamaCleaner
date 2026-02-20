import hashlib

def compute_sha1(path: str) -> str:
    """
    Compute SHA-1 hash of a file efficiently.
    """
    sha1 = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha1.update(chunk)
    return sha1.hexdigest()
