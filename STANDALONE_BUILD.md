# Building Standalone Executable

This guide explains how to create a standalone executable that runs without Python or Docker.

## What is a Standalone Executable?

A standalone executable is a single file (`.exe` on Windows) that contains:
- Your application code
- Python interpreter
- All required libraries
- Dependencies

**Users don't need Python installed** to run it!

## Prerequisites

- Python 3.9 or higher (only needed for building)
- pip (Python package installer)
- All application dependencies installed

## Quick Build (Windows)

### Option 1: Using Build Script (Easiest)

Simply run:
```bash
build.bat
```

This will:
1. Install build dependencies (PyInstaller)
2. Install application dependencies
3. Build the standalone executable
4. Create `dist/CleanUpTool.exe`

### Option 2: Manual Build

```bash
# 1. Install build tool
pip install PyInstaller

# 2. Build executable
python build_standalone.py
```

## Quick Build (Linux/Mac)

```bash
# Make script executable
chmod +x build.sh

# Run build script
./build.sh
```

Or manually:
```bash
pip3 install PyInstaller
python3 build_standalone.py
```

## Output

After building, you'll find:

- **Windows**: `dist/CleanUpTool.exe`
- **Linux/Mac**: `dist/CleanUpTool`

The executable is **self-contained** and can be distributed to other computers.

## Distribution

### Single File Distribution

The executable in `dist/` folder is ready to distribute:

1. **Copy the executable** (`CleanUpTool.exe` on Windows)
2. **Share it** with users
3. **Users can run it directly** - no installation needed!

### Including Data Files

If you need to include additional files (configs, icons, etc.):

1. Create a folder with the executable
2. Include necessary files:
   ```
   CleanUpTool/
   ├── CleanUpTool.exe
   ├── config/
   │   └── defaults.json
   └── README.txt
   ```

## Build Options

### Customize Build

Edit `build_standalone.py` to customize:

- **Executable name**: Change `--name=CleanUpTool`
- **Icon**: Add `--icon=path/to/icon.ico`
- **Console window**: Remove `--windowed` to show console
- **Additional files**: Add more `--add-data` entries

### Advanced Options

```python
# In build_standalone.py, you can add:
'--debug=all',  # Debug mode
'--log-level=DEBUG',  # Verbose logging
'--exclude-module=module_name',  # Exclude modules
```

## Troubleshooting

### Issue: "PyInstaller not found"

**Solution:**
```bash
pip install PyInstaller
```

### Issue: "Module not found" errors

**Solution:** Add hidden imports in `build_standalone.py`:
```python
'--hidden-import=module_name',
```

### Issue: Large executable size

**Solution:** This is normal. PyInstaller bundles Python and all dependencies:
- Typical size: 50-150 MB
- First run may be slower (extraction)

### Issue: Antivirus flags the executable

**Solution:** This is a false positive. PyInstaller executables are often flagged:
- Add exception in antivirus
- Code-sign the executable (requires certificate)
- Use `--key` option for encryption

### Issue: Missing DLLs on Windows

**Solution:** Install Visual C++ Redistributable:
- Download from Microsoft
- Install on target machine

## File Size Optimization

To reduce executable size:

1. **Exclude unnecessary modules:**
   ```python
   '--exclude-module=matplotlib',
   '--exclude-module=numpy',  # If not needed
   ```

2. **Use UPX compression** (optional):
   ```python
   '--upx-dir=path/to/upx',
   ```

3. **One directory mode** (instead of onefile):
   ```python
   # Remove '--onefile' for faster startup
   ```

## Testing the Standalone Executable

1. **Test on build machine:**
   ```bash
   dist/CleanUpTool.exe
   ```

2. **Test on clean machine:**
   - Copy to a computer without Python
   - Run and verify it works

3. **Check functionality:**
   - All tabs work
   - File operations work
   - GUI displays correctly

## Distribution Checklist

Before distributing:

- [ ] Test executable on clean machine (no Python)
- [ ] Verify all features work
- [ ] Check file size (acceptable for distribution)
- [ ] Create README for end users
- [ ] Consider code signing (optional, for trust)
- [ ] Test on different Windows versions (if Windows)

## Alternative: Portable Package

Instead of single executable, create a portable package:

1. Build in **onedir mode** (remove `--onefile`):
   ```python
   # In build_standalone.py, remove '--onefile'
   ```

2. Package the entire `dist/CleanUpTool/` folder
3. Users run `CleanUpTool.exe` from the folder

**Advantages:**
- Faster startup (no extraction)
- Easier to update (replace files)
- Smaller individual files

**Disadvantages:**
- Multiple files to distribute
- Folder structure required

## Code Signing (Optional)

For production distribution, consider code signing:

1. Obtain code signing certificate
2. Sign the executable:
   ```bash
   signtool sign /f certificate.pfx /p "<certificate-password>" CleanUpTool.exe
   ```

This prevents "Unknown Publisher" warnings.

## Platform-Specific Notes

### Windows

- Creates `.exe` file
- May require admin privileges for some operations
- Consider adding to Windows Defender exclusions

### Linux

- Creates executable (no extension)
- May need to set executable permission:
  ```bash
  chmod +x dist/CleanUpTool
  ```

### macOS

- Creates executable
- May need to sign for Gatekeeper
- Consider creating `.app` bundle instead

## Next Steps

1. **Build the executable** using `build.bat` or `build.sh`
2. **Test thoroughly** on a clean machine
3. **Distribute** the executable to users
4. **Collect feedback** and iterate

## Support

If you encounter issues:
1. Check PyInstaller documentation: https://pyinstaller.org/
2. Review build logs in `build/` folder
3. Test with `--debug=all` for verbose output

