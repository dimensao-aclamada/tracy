#!/usr/bin/env python3
"""
tracy.py - CLI entry point for Tracy versioning tool

This file handles command-line parsing and delegates functionality
to modular commands implemented in the `commands` package.

Supported commands:
- init <project>
- create [--project NAME] [--file FILE]
- list [--project NAME] [--file FILE]
- open
- reset --hash HASH [--force]
"""

import sys
from commands import create_version, init_project, list_versions, open_storage, reset_version

# -------------------------------
# Helper for CLI flag parsing
# -------------------------------
def get_flag_value(args, flag):
    """
    Retrieve the value of a CLI flag.
    Example: for args = ["create", "--project", "tracy"], get_flag_value(args, "--project") -> "tracy"
    """
    if flag in args:
        idx = args.index(flag)
        if idx + 1 < len(args):
            return args[idx + 1]
    return None

# -------------------------------
# CLI Entry Point
# -------------------------------
def main():
    args = sys.argv[1:]

    if not args:
        print(
            "Commands: init <project>, create [--project NAME] [--file FILE], "
            "list [--project NAME] [--file FILE], open, reset --hash HASH [--force]"
        )
        return

    cmd = args[0].lower()

    # -------------------------------
    # init <project>
    # -------------------------------
    if cmd == "init":
        if len(args) < 2:
            print("Usage: tracy init <project_name>")
            return
        init_project(args[1])

    # -------------------------------
    # create [--project NAME] [--file FILE]
    # -------------------------------
    elif cmd == "create":
        project = get_flag_value(args, "--project")
        file_name = get_flag_value(args, "--file")
        create_version(project, file_name)

    # -------------------------------
    # list [--project NAME] [--file FILE]
    # -------------------------------
    elif cmd == "list":
        project = get_flag_value(args, "--project")
        file_name = get_flag_value(args, "--file")
        list_versions(project, file_name)

    # -------------------------------
    # open - reveal storage folder in Finder/Explorer
    # -------------------------------
    elif cmd == "open":
        open_storage()

    # -------------------------------
    # reset --hash HASH [--force]
    # -------------------------------
    elif cmd == "reset":
        target_hash = get_flag_value(args, "--hash")
        force = "--force" in args
        if not target_hash:
            print("Usage: tracy reset --hash HASH [--force]")
            return
        reset_version(target_hash, force)

    # -------------------------------
    # Unknown command
    # -------------------------------
    else:
        print("Unknown command. Use init, create, list, open, or reset.")

# -------------------------------
# Main execution
# -------------------------------
if __name__ == "__main__":
    main()