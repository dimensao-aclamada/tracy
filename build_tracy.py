# build_tracy.py

"""
This module automates the build and deployment process for TracyApp on macOS.

It performs the following steps:
1. Removes previous build artifacts.
2. Builds the app using PyInstaller with a macOS bundle identifier.
3. Opens the resulting application.
4. Updates the `/usr/local/bin/tracy` symlink to point to the new build.

Requirements:
- Python 3.6+
- PyInstaller installed
- macOS
"""

import subprocess
import os
import sys

APP_NAME = "TracyApp"
SCRIPT_NAME = "tracy.py"
BUNDLE_IDENTIFIER = "com.dimmension.tracyapp"
SYMLINK_PATH = "/usr/local/bin/tracy"


def run_command(command, check=True, sudo=False):
    """Runs a shell command and optionally checks for errors."""
    if sudo:
        command = ["sudo"] + command
    print(f"Running command: {' '.join(command)}")
    subprocess.run(command, check=check)


def clean_build():
    """Removes previous build artifacts."""
    for folder in ["build", "dist", f"{APP_NAME}.spec"]:
        if os.path.exists(folder):
            print(f"Removing {folder}")
            if os.path.isdir(folder):
                subprocess.run(["rm", "-rf", folder], check=True)
            else:
                os.remove(folder)


def build_app():
    """Builds the app using PyInstaller."""
    run_command([
        "pyinstaller",
        SCRIPT_NAME,
        "--name", APP_NAME,
        "--onedir",
        "--windowed",
        "--osx-bundle-identifier", BUNDLE_IDENTIFIER
    ])


def open_app():
    """Opens the newly built macOS app."""
    app_path = os.path.join("dist", f"{APP_NAME}.app")
    run_command(["open", app_path])


def update_symlink():
    """Updates the symlink in /usr/local/bin."""
    app_executable = os.path.join(os.getcwd(), "dist", f"{APP_NAME}.app", "Contents", "MacOS", APP_NAME)
    if os.path.exists(SYMLINK_PATH):
        run_command(["rm", SYMLINK_PATH], sudo=True)
    run_command(["ln", "-s", app_executable, SYMLINK_PATH], sudo=True)


if __name__ == "__main__":
    clean_build()
    build_app()
    open_app()
    update_symlink()
    print("✅ Build and deployment complete!")