import os, hashlib

def ensure_dirs(*paths):
    for p in paths:
        os.makedirs(p, exist_ok=True)

def hash_file(path):
    hasher = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()
