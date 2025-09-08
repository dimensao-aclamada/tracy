import os
import platform


# --- Global Tracy paths ---
if platform.system() == "Windows":
    TRACY_DIR = os.path.join(os.environ["USERPROFILE"], ".tracy")
else:
    TRACY_DIR = os.path.join(os.path.expanduser("~"), ".tracy   ")

OBJECTS_DIR = os.path.join(TRACY_DIR, "objects")
TRACY_DB = os.path.join(TRACY_DIR, "tracy.json")
