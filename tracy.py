#!/usr/bin/env python3

import os
import hashlib
import json
import shutil
import datetime
import sys
import platform

# --- Global Tracy paths ---
if platform.system() == "Windows":
    TRACY_DIR = os.path.join(os.environ["USERPROFILE"], ".tracy")
else:
    TRACY_DIR = os.path.join(os.path.expanduser("~"), ".tracy")

OBJECTS_DIR = os.path.join(TRACY_DIR, "objects")
TRACY_DB = os.path.join(TRACY_DIR, "tracy.json")

# --- Helpers ---
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

# --- Commands ---
def init_project(project_name):
    ensure_global_repo()
    db = load_db()
    if project_name in db["projects"]:
        print(f"Project '{project_name}' already exists.")
    else:
        db["projects"][project_name] = {"versions": []}
        save_db(db)
        print(f"Initialized project '{project_name}' in centralized Tracy repository.")

def create_version(project_name=None):
    ensure_global_repo()
    db = load_db()
    
    if project_name is None:
        project_name = input("Project name (leave blank for 'default'): ").strip() or "default"

    if project_name not in db["projects"]:
        create = input(f"Project '{project_name}' not found. Create it? (Y/N): ").strip().upper()
        if create != "Y":
            print("Aborted.")
            return
        db["projects"][project_name] = {"versions": []}

    level = input("Type L for launch, S for significant improvement or M for minor improvement: ").strip().upper()
    filename = input("Type the name (or path) of the file to be versioned: ").strip()

    # Resolve path
    if os.path.sep in filename or os.path.isabs(filename):
        abs_path = os.path.abspath(filename)
        if not os.path.exists(abs_path):
            print("File not found!")
            return
    else:
        matches = search_file(filename)
        if not matches:
            print(f"No file named '{filename}' found.")
            return
        elif len(matches) == 1:
            abs_path = matches[0]
        else:
            print(f"Multiple files found with name '{filename}':")
            for idx, path in enumerate(matches, 1):
                print(f"{idx}. {path}")
            choice = input("Choose the number: ").strip()
            try:
                abs_path = matches[int(choice)-1]
            except:
                print("Invalid choice.")
                return

    commit = input("Commit message: ").strip()
    label = input("Optional label (press Enter to skip): ").strip()

    versions = db["projects"][project_name]["versions"]
    last_entry = next((e for e in reversed(versions) if e["path"] == abs_path), None)
    last_version = last_entry["version"] if last_entry else None
    new_version = bump_version(last_version, level)
    h = file_hash(abs_path)

    # Copy file
    dest_path = os.path.join(OBJECTS_DIR, h)
    if not os.path.exists(dest_path):
        shutil.copy2(abs_path, dest_path)

    # Update metadata
    for e in versions:
        if e["path"] == abs_path:
            e["latest"] = False

    entry = {
        "hash": h,
        "path": abs_path,
        "version": new_version,
        "latest": True,
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "commit": commit,
        "label": label if label else None
    }
    versions.append(entry)
    save_db(db)
    print(f"Version {new_version} created for {abs_path} in project '{project_name}' (hash {h[:8]}...)")

def list_versions(project_name=None):
    ensure_global_repo()
    db = load_db()

    projects = [project_name] if project_name else db["projects"].keys()
    for proj in projects:
        if proj not in db["projects"]:
            print(f"Project '{proj}' not found.")
            continue
        print(f"\nProject: {proj}")
        versions = db["projects"][proj]["versions"]
        if not versions:
            print("  No versions yet.")
            continue
        for e in versions:
            mark = "(Latest)" if e["latest"] else ""
            label = f"[{e['label']}]" if e.get("label") else ""
            print(f"  {e['path']} v{e['version']} {label} {mark}")
            print(f"    Commit: {e['commit']}")
            print(f"    Time:   {e['timestamp']}")
            print(f"    Hash:   {e['hash']}")

# --- CLI ---
def main():
    args = sys.argv[1:]
    if not args:
        print("Commands: init <project>, create [--project NAME], list [--project NAME]")
        return
    cmd = args[0].lower()
    if cmd == "init":
        if len(args) < 2:
            print("Usage: tracy init <project_name>")
            return
        init_project(args[1])
    elif cmd == "create":
        project = None
        if "--project" in args:
            idx = args.index("--project")
            project = args[idx+1] if idx+1 < len(args) else None
        create_version(project)
    elif cmd == "list":
        project = None
        if "--project" in args:
            idx = args.index("--project")
            project = args[idx+1] if idx+1 < len(args) else None
        list_versions(project)
    else:
        print("Unknown command. Use init, create, list.")

if __name__ == "__main__":
    main()
