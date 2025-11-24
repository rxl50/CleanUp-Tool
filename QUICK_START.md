# Quick Start Guide

Choose the method that works best for you:

## 🚀 Method 1: Standalone Executable (Recommended)

**Best for:** Distributing to others, no Python required

### Build the executable:

**Windows:**
```bash
build.bat
```

**Linux/Mac:**
```bash
chmod +x build.sh
./build.sh
```

**Result:** Single executable file (`CleanUpTool.exe` on Windows) that runs without Python!

---

## 🐍 Method 2: Run with Python (Development)

**Best for:** Development, testing, quick runs

### Install and run:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

**Result:** Runs directly with Python (requires Python installed)

---

## 🐳 Method 3: Docker

**Best for:** Isolated environments, testing

### Build and run:

```bash
# Build image
docker build -t cleanup-tool .

# Run container
docker-compose up
```

**Result:** Runs in Docker container (requires Docker installed)

---

## 📋 Comparison

| Method | Requires Python | Requires Docker | File Size | Startup Speed |
|--------|----------------|-----------------|-----------|---------------|
| Standalone | ❌ No | ❌ No | ~50-150 MB | Slower (first run) |
| Python | ✅ Yes | ❌ No | Small | Fast |
| Docker | ❌ No | ✅ Yes | Large | Medium |

## 💡 Recommendation

- **For end users:** Use **Standalone Executable** - just double-click and run!
- **For developers:** Use **Python** - easier to modify and debug
- **For testing:** Use **Docker** - isolated environment

## 🎯 Quick Decision

**Want to share with others?** → Use `build.bat` to create standalone executable

**Just want to use it yourself?** → Run `python main.py` directly

**Want to test in isolation?** → Use Docker

