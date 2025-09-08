# 📦 Tracy: A Lightweight Versioning CLI

Tracy is a simple, command-line tool for managing local versions of your files. Unlike complex version control systems, Tracy is designed for quick, personal backups and versioning of individual files or small projects.

It's perfect for when you just need a way to save a snapshot of a file without setting up a full Git repository.

## 🤔 Why Tracy, and not Git?

Git is a powerful, distributed version control system designed for collaborative development on large projects. It tracks an entire codebase, manages branches, and handles complex merge conflicts. This power comes with a learning curve and significant overhead for simple tasks.

Tracy is a lightweight "undo button" for your local files. It's not a replacement for Git, but a simple companion tool for when you need a quick, personal safety net. Tracy excels in situations where setting up a full Git repository is overkill or when you need to rapidly revert changes without affecting your commit history.

A great use case for Tracy is when working with AI. As you iterate with AI-assisted coding, you can quickly create versions of a single file before an AI model "hallucinates," forgets code, replaces it with placeholders, or breaks something that was working. With Tracy, a quick `tracy reset` brings you back to a stable state in seconds, without leaving a trace in your Git history.

## ✨ Features

- **Simple Project and File Versioning**: Create versions for specific projects or individual files.  
- **Easy Snapshot Creation**: Use a single command to create a new version of your work at any point.  
- **Version History**: List all stored versions, identified by their unique hashes.  
- **Effortless Reversion**: Restore a file to any previous state using its hash.  
- **Local Storage**: All versions are stored locally, giving you full control and privacy.  

## 🚀 Installation

Tracy is a single Python script. To use it, simply download the `tracy.py` file and make it executable.

```bash
# Download the script (or copy-paste it)
curl -o tracy https://raw.githubusercontent.com/dimensao-aclamada/tracy/main/tracy.py

# Make it executable
chmod +x tracy
```

For global access, you can move the script to a directory in your system's PATH:

```bash
# For macOS / Linux
sudo mv tracy /usr/local/bin/
```

You can now run `tracy` from any directory.

## 📖 Usage

Here is a breakdown of Tracy's commands and their usage.

### tracy init <project_name>
Initializes a new project directory for Tracy to store your versions. This must be run before creating versions for a project.  

**Example:**
```bash
tracy init my-first-project
```

### tracy create [--project NAME] [--file FILE]
Creates a new version of a file.  

- If you specify `--project`, it creates a version of the current file within that project's storage.  
- If you specify `--file`, it creates a version of that specific file.  
- If you don't specify any flags, it creates a version of the current directory's contents.  

**Examples:**
```bash
# Create a version of 'main.py' for the 'my-first-project'
tracy create --project my-first-project --file main.py

# Create a version of all files in the current directory
tracy create
```

### tracy list [--project NAME] [--file FILE]
Lists the stored versions.  

- `--project`: Lists versions for a specific project.  
- `--file`: Lists versions for a specific file.  

**Examples:**
```bash
# List all versions for 'my-first-project'
tracy list --project my-first-project

# List all versions for the 'notes.txt' file
tracy list --file notes.txt
```

### tracy open
Opens the Tracy storage directory in your system's file browser (Finder on macOS, Explorer on Windows). This is useful for manually inspecting or managing your stored versions.  

**Example:**
```bash
tracy open
```

### tracy reset --hash HASH [--force]
Resets a file to a previous version using its hash.  

- `--hash HASH`: Required. The unique hash of the version you want to restore.  
- `--force`: Optional. Overwrites the current file without a confirmation prompt.  

**Example:**
```bash
# Reset the current file to the version with hash 'a1b2c3d4e5f6'
tracy reset --hash a1b2c3d4e5f6

# Force reset without confirmation
tracy reset --hash a1b2c3d4e5f6 --force
```

## 🤝 Contributing

Tracy is a simple tool designed for personal use, but if you have ideas for improvements or new features, feel free to open an issue or submit a pull request.
