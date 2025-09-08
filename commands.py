import os
import sys
import datetime
import shutil

from global_paths import OBJECTS_DIR

from helpers import (
    ensure_global_repo,
    load_db,save_db,
    search_file,
    file_hash,
    bump_version,
    get_last_used,
    set_last_used,
)

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

def create_version(project_name=None, file_name=None):
    """
    Create a new version of a file inside a project.

    Args:
        project_name (str | None): Project name to use. If None, prompt user (with last-project fallback).
        file_name (str | None): Path or name of file to version. If None, prompt user (with last-file fallback).
    """    
    ensure_global_repo()
    db = load_db()

    # --- Project selection ---
    last_project, last_file = get_last_used(db)

    if project_name is None:
        project_name = input(
            f"Project name (leave blank for '{last_project or 'default'}'): "
        ).strip() or last_project or "default"

    if project_name not in db["projects"]:
        create = input(f"Project '{project_name}' not found. Create it? (Y/N): ").strip().upper()
        if create != "Y":
            print("Aborted.")
            return
        db["projects"][project_name] = {"versions": []}

    # --- File selection ---
    if file_name:  
        # If --file was provided on the CLI
        filename = file_name
    else:
        if last_file:
            prompt = f"Type the name (or path) of the file to be versioned (leave blank for last: '{last_file}'): "
        else:
            prompt = "Type the name (or path) of the file to be versioned: "
        filename = input(prompt).strip() or last_file

    if not filename:
        print("No file provided and no last file remembered.")
        return
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
            except (ValueError, IndexError):
                print("Invalid choice.")
                return

    # --- Version metadata ---
    level = input("Type L for launch, S for significant improvement or M for minor improvement: ").strip().upper()
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

    # --- Save and update last used ---
    set_last_used(db, project_name, abs_path)
    save_db(db)

    print(f"Version {new_version} created for {abs_path} in project '{project_name}' (hash {h[:8]}...)")
    
def list_versions(project_name=None, file_name=None):
    """
    List versions with flexible filtering.

    Args:
        project_name (str | None): Specific project name, or None to let user choose.
        file_name (str | None): Specific file name (path or basename), or None.

    Behavior:
        - If both project and file are given: show versions for that file in that project.
        - If only project is given: show files in that project, let user pick one.
        - If only file is given: search across all projects, disambiguate if needed.
        - If both blank: show projects, then delegate to project case.
    """
    ensure_global_repo()
    db = load_db()

    # --- Case 1: both project and file provided ---
    if project_name and file_name:
        if project_name not in db["projects"]:
            print(f"Project '{project_name}' not found.")
            return
        versions = [e for e in db["projects"][project_name]["versions"]
                    if os.path.basename(e["path"]) == os.path.basename(file_name)]
        if not versions:
            print(f"No versions found for '{file_name}' in project '{project_name}'.")
            return
        _print_versions(project_name, versions)
        return

    # --- Case 2: only project provided ---
    if project_name and not file_name:
        if project_name not in db["projects"]:
            print(f"Project '{project_name}' not found.")
            return
        versions = db["projects"][project_name]["versions"]
        if not versions:
            print(f"No versions yet in project '{project_name}'.")
            return
        files = sorted(set(e["path"] for e in versions))
        print(f"Files in project '{project_name}':")
        for idx, f in enumerate(files, 1):
            print(f"{idx}. {f}")
        choice = input("Choose file number: ").strip()
        try:
            chosen = files[int(choice) - 1]
        except (ValueError, IndexError):
            print("Invalid choice.")
            return
        versions = [e for e in versions if e["path"] == chosen]
        _print_versions(project_name, versions)
        return

    # --- Case 3: only file provided ---
    if file_name and not project_name:
        matches = []
        for proj, data in db["projects"].items():
            for e in data["versions"]:
                if os.path.basename(e["path"]) == os.path.basename(file_name):
                    matches.append((proj, e["path"]))
        if not matches:
            print(f"No versions found for file '{file_name}'.")
            return
        if len(matches) == 1:
            proj, path = matches[0]
            versions = [e for e in db["projects"][proj]["versions"] if e["path"] == path]
            _print_versions(proj, versions)
            return
        print("Multiple matches found:")
        for idx, (proj, path) in enumerate(matches, 1):
            print(f"{idx}. {proj}: {path}")
        choice = input("Choose number: ").strip()
        try:
            proj, path = matches[int(choice) - 1]
        except (ValueError, IndexError):
            print("Invalid choice.")
            return
        versions = [e for e in db["projects"][proj]["versions"] if e["path"] == path]
        _print_versions(proj, versions)
        return

    # --- Case 4: both blank ---
    projects = list(db["projects"].keys())
    if not projects:
        print("No projects found.")
        return
    print("Projects:")
    for idx, proj in enumerate(projects, 1):
        print(f"{idx}. {proj}")
    choice = input("Choose project number: ").strip()
    try:
        proj = projects[int(choice) - 1]
    except (ValueError, IndexError):
        print("Invalid choice.")
        return
    list_versions(proj, None)

def _print_versions(project_name, versions):
    """Helper to print versions list for a project/file, showing latest and current."""
    print(f"\nVersions in project '{project_name}':")
    for e in versions:
        marks = []
        if e.get("latest"):
            marks.append("Latest")
        if e.get("current"):
            marks.append("Current")
        mark_str = f"({' & '.join(marks)})" if marks else ""
        label = f"[{e['label']}]" if e.get("label") else ""
        print(f"  {e['path']} v{e['version']} {label} {mark_str}")
        print(f"    Commit: {e['commit']}")
        print(f"    Time:   {e['timestamp']}")
        print(f"    Hash:   {e['hash']}")

def reset_version(target_hash, force=False):
    """
    Reset a file to a specific version identified by hash.

    Args:
        target_hash (str): Full or partial hash of the version.
        force (bool): If True, skip confirmation.
    """
    ensure_global_repo()
    db = load_db()

    # Find all matching versions across projects
    matches = []
    for proj, data in db["projects"].items():
        for e in data["versions"]:
            if e["hash"].startswith(target_hash):
                matches.append((proj, e))

    if not matches:
        print(f"No version found matching hash {target_hash}.")
        return
    if len(matches) > 1:
        print("Multiple matches found:")
        for idx, (proj, e) in enumerate(matches, 1):
            print(f"{idx}. {proj}: {e['path']} v{e['version']} ({e['hash'][:8]})")
        choice = input("Choose number: ").strip()
        try:
            proj, entry = matches[int(choice) - 1]
        except (ValueError, IndexError):
            print("Invalid choice.")
            return
    else:
        proj, entry = matches[0]

    dest_path = entry["path"]
    src_path = os.path.join(OBJECTS_DIR, entry["hash"])

    if not os.path.exists(src_path):
        print(f"Stored version not found in objects repo (hash {entry['hash']}).")
        return

    # Confirm overwrite
    if not force:
        confirm = input(
            f"Reset {dest_path} to version {entry['version']} ({entry['hash'][:8]})? This will overwrite the file. (Y/N): "
        ).strip().upper()
        if confirm != "Y":
            print("Aborted.")
            return

    shutil.copy2(src_path, dest_path)

    # Update DB: mark "current"
    for e in db["projects"][proj]["versions"]:
        if e["path"] == dest_path:
            e["current"] = (e["hash"] == entry["hash"])
    save_db(db)

    print(f"File {dest_path} has been reset to version {entry['version']} (hash {entry['hash'][:8]}...).")
    
def open_storage():
    """
    Reveal the folder where versioned files are stored.

    On macOS this uses the `open` command to reveal the OBJECTS_DIR in Finder.
    On Linux it uses `xdg-open`, and on Windows `explorer`.
    """
    path = os.path.abspath(OBJECTS_DIR)

    if not os.path.exists(path):
        print(f"Storage directory '{path}' does not exist.")
        return

    if sys.platform == "darwin":  # macOS
        os.system(f"open '{path}'")
    elif sys.platform.startswith("linux"):
        os.system(f"xdg-open '{path}'")
    elif sys.platform.startswith("win"):
        os.system(f"explorer {path}")
    else:
        print(f"Don't know how to open folders on this platform ({sys.platform}).")
        print(f"Path to storage: {path}")