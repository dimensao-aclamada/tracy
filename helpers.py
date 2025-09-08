import os
import sys
import hashlib
import json
from global_paths import TRACY_DIR, OBJECTS_DIR, TRACY_DB


def ensure_global_repo():
    """Ensure the global repo exists."""
    os.makedirs(TRACY_DIR, exist_ok=True)
    os.makedirs(OBJECTS_DIR, exist_ok=True)
    if not os.path.exists(TRACY_DB):
        with open(TRACY_DB, "w") as f:
            json.dump({"projects": {}}, f, indent=2)

def load_db():
    with open(TRACY_DB, "r") as f:
        return json.load(f)

def save_db(db):
    with open(TRACY_DB, "w") as f:
        json.dump(db, f, indent=2)

def file_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

def bump_version(last_version, level):
    if not last_version:
        return "1.0.0"
    major, minor, patch = map(int, last_version.split("."))
    if level == "L":
        return f"{major+1}.0.0"
    elif level == "S":
        return f"{major}.{minor+1}.0"
    else:  # M
        return f"{major}.{minor}.{patch+1}"

def search_file(filename):
    matches = []
    for root, _, files in os.walk("."):
        if filename in files:
            matches.append(os.path.abspath(os.path.join(root, filename)))
    return matches

def get_last_used(db):
    """Return last used project and file if available, else (None, None)."""
    last = db.get("last_used", {})
    return last.get("project"), last.get("file")

def set_last_used(db, project_name, file_path):
    """Update DB with the last used project and file."""
    db["last_used"] = {"project": project_name, "file": file_path}
    save_db(db)
    
