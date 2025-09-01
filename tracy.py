#!/usr/bin/env python3

import os
import hashlib
import json
import shutil
import datetime
import sys

TRACY_DIR = ".tracy"
TRACY_DB = os.path.join(TRACY_DIR, "tracy.json")

# --- Helpers ---
def init_env(force=False):
    """Initialize a Tracy repository in the current folder."""
    if os.path.exists(TRACY_DIR) and not force:
        print("Tracy repository already initialized.")
        return
    os.makedirs(TRACY_DIR, exist_ok=True)
    if not os.path.exists(TRACY_DB) or force:
        with open(TRACY_DB, "w") as f:
            json.dump([], f)
    print("Initialized empty Tracy repository in", os.path.abspath(TRACY_DIR))


def ensure_env(confirm=True):
    """Ensure Tracy repository exists, optionally asking before init."""
    if not os.path.exists(TRACY_DIR):
        if confirm:
            ans = input("No Tracy repository found. Initialize one here? (Y/N): ").strip().upper()
            if ans != "Y":
                print("Aborted.")
                sys.exit(1)
        init_env()


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
    """Search recursively for filename in cwd; return list of full paths."""
    matches = []
    for root, _, files in os.walk("."):
        if filename in files:
            matches.append(os.path.abspath(os.path.join(root, filename)))
    return matches


# --- Commands ---
def create_version():
    ensure_env()

    level = input("Type L for launch, S for significant improvement or M for minor improvement: ").strip().upper()
    filename = input("Type the name (or path) of the file to be versioned: ").strip()

    # If user gave a path, resolve directly
    if os.path.sep in filename or os.path.isabs(filename):
        abs_path = os.path.abspath(filename)
        if not os.path.exists(abs_path):
            print("File not found!")
            return
    else:
        # Search in subfolders
        matches = search_file(filename)
        if not matches:
            print(f"No file named '{filename}' found in this folder or subfolders.")
            return
        elif len(matches) == 1:
            abs_path = matches[0]
        else:
            print(f"Multiple files found with name '{filename}':")
            for idx, path in enumerate(matches, 1):
                print(f"{idx}. {path}")
            choice = input("Choose the number: ").strip()
            try:
                idx = int(choice) - 1
                abs_path = matches[idx]
            except Exception:
                print("Invalid choice.")
                return

    commit = input("Commit message: ").strip()
    label = input("Optional label (press Enter to skip): ").strip()

    db = load_db()
    last_entry = next((e for e in reversed(db) if e["file"] == abs_path), None)
    last_version = last_entry["version"] if last_entry else None

    new_version = bump_version(last_version, level)
    h = file_hash(abs_path)

    # copy file to .tracy
    dest_path = os.path.join(TRACY_DIR, h)
    if not os.path.exists(dest_path):
        shutil.copy2(abs_path, dest_path)

    # update DB
    for e in db:
        if e["file"] == abs_path:
            e["latest"] = False

    entry = {
        "hash": h,
        "file": abs_path,
        "version": new_version,
        "latest": True,
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "commit": commit,
        "label": label if label else None
    }
    db.append(entry)
    save_db(db)
    print(f"Version {new_version} created for {abs_path} (hash {h[:8]}...)")


def reset_version():
    ensure_env()

    hash_prefix = input("Type the hash (full or short) of the version to reset to: ").strip()
    db = load_db()
    matches = [e for e in db if e["hash"].startswith(hash_prefix)]

    if not matches:
        print("No version found with that hash.")
        return

    if len(matches) > 1:
        matches.sort(key=lambda e: e["timestamp"], reverse=True)
        entry = matches[0]
        print(f"Multiple matches found, using the most recent version v{entry['version']} for {entry['file']}")
    else:
        entry = matches[0]

    filename = entry["file"]

    shutil.copy2(os.path.join(TRACY_DIR, entry["hash"]), filename)
    for e in db:
        if e["file"] == filename:
            e["latest"] = False
    entry["latest"] = True
    save_db(db)

    print(f"{filename} reset to version {entry['version']} (hash {entry['hash']})")


def list_versions():
    ensure_env(confirm=False)

    db = load_db()
    if not db:
        print("No versions yet.")
        return

    for e in db:
        mark = "(Latest)" if e["latest"] else ""
        label = f"[{e['label']}]" if e.get("label") else ""
        print(f"{e['file']} v{e['version']} {label} {mark}")
        print(f"  Commit: {e['commit']}")
        print(f"  Time:   {e['timestamp']}")
        print(f"  Hash:   {e['hash']}")
        print()


# --- CLI Entry ---
def main():
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == "init":
            init_env()
        elif cmd == "create":
            create_version()
        elif cmd == "reset":
            reset_version()
        elif cmd == "list":
            list_versions()
        else:
            print("Unknown command. Use 'init', 'create', 'reset', or 'list'.")
    else:
        choice = input("Type C to create, R to reset, L for list, or I for init: ").strip().upper()
        if choice == "C":
            create_version()
        elif choice == "R":
            reset_version()
        elif choice == "L":
            list_versions()
        elif choice == "I":
            init_env()
        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()
