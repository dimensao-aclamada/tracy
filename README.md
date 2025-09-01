# Tracy 🕵️‍♀️
*A detective for your files — lightweight, smart, and always on the case.*

Tracy is a **minimalist file-based version control system**.
Unlike Git (which works on repositories of many files), Tracy focuses on **individual files** — making it perfect for documents, configs, scripts, or anything you want to version quickly without ceremony.

Inspired by **Dick Tracy**, the tough, fast, and intelligent detective, Tracy helps you **track, version, and restore** files with speed and clarity.

---

## ✨ Features
- 📂 **Per-file versioning** — track files independently.  
- 📝 **Semantic versioning** — major, minor, patch bumps (Launch, Significant, Minor).  
- 🔑 **SHA-256 hash storage** — ensures integrity, with shortened display for convenience.  
- 📜 **Commit messages & labels** — document your changes.  
- ⏱ **Timestamps & latest marker** — know when and what is the current version.  
- 🔍 **Subfolder search** — find files even if you don’t recall the full path.  
- 🖥 **Interactive or CLI mode** — quick single-letter prompts or explicit commands.  
- ⚡ **Zero-config init** — just start using, or run `tracy init` explicitly.  
- 🛠 **Cross-platform** — works on Linux, macOS, and Windows (can be packaged as `.exe` or `.app`).  

---

## 🚀 Installation

### From source
```bash
git clone https://github.com/dimensao-aclamada/tracy.git
cd tracy
pip install .
```

This installs `tracy` as a system-wide command.  

### Build as executable (optional)
- **Windows**:  
  ```bash
  pip install pyinstaller
  pyinstaller --onefile tracy.py
  dist/tracy.exe
  ```
- **macOS/Linux**:  
  ```bash
  pyinstaller --onefile tracy.py
  dist/tracy
  ```

---

## 🕹 Usage

### Initialize a Tracy repo
```bash
tracy init
```
Creates a hidden `.tracy/` folder and `tracy.json` database.  
If you forget, Tracy will ask you whether to initialize when you first run a command.  

---

### Create a version
```bash
tracy create
```
Interactive flow:  
1. Select version bump — Launch (major), Significant (minor), or Minor (patch).  
2. Select file (searches recursively if only a filename is given).  
3. Enter commit message and optional label.  

Tracy stores a hashed copy in `.tracy/` and records metadata in `.tracy/tracy.json`.  

---

### Reset a version
```bash
tracy reset
```
- Provide a hash prefix (short or full).  
- Tracy restores the file to the saved version.  
- If multiple matches, the **most recent** is chosen.  

---

### List versions
```bash
tracy list
```
Shows history with file path, version, commit, timestamp, and hash.  
Example:
```
/home/user/project/config.yaml v1.2.0 [production] (Latest)
  Commit: tuned caching parameters
  Time:   2025-09-01T18:21:44
  Hash:   aaf5dab2f10a9c37...
```

---

## 🧩 Example Workflow
```bash
tracy init
tracy create config.yaml    # v1.0.0
tracy create config.yaml    # v1.0.1 (minor)
tracy create config.yaml    # v1.1.0 (significant)
tracy list
tracy reset                 # restore an earlier version by hash
```

---

## 🔮 Roadmap
- [ ] Flags for non-interactive usage (`--level M --commit "msg" --label bugfix`).  
- [ ] Global mode (track files across directories).  
- [ ] Diff and compare between versions.  
- [ ] Ignore patterns (like `.gitignore`).  

---

## 🤝 Contributing
Contributions are welcome! Fork, open a PR, or suggest improvements.  

---

## 📜 License
MIT License. Free to use, modify, and share.
