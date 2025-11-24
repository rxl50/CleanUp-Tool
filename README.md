# CleanUp Tool

> ⚠️ **IMPORTANT WARNINGS - READ BEFORE USE** ⚠️
> 
> **This tool performs DESTRUCTIVE operations that CANNOT be easily undone.**
> 
> - **Always backup your data** before using this tool
> - **Test on non-critical systems first**
> - **Review what will be deleted** using the Preview feature before confirming
> - **Active conda environments are protected**, but double-check your selections
> - **System files are protected**, but use caution with system cleanup features
> - **Browser cache deletion** will require re-login to websites
> - **This tool is provided AS-IS** without warranty. Use at your own risk.

---

A comprehensive GUI application for cleaning up disk space on your computer. Features automatic backup system, restore points, and support for cleaning Anaconda environments, pip cache, system temp files, browser caches, and more.

## ⚠️ Critical Safety Information

### Before You Start

1. **Backup Important Data**: While this tool creates automatic backups, you should have your own backups of critical data
2. **Close Running Applications**: Close any applications that might be using files you plan to delete
3. **Review Preview Carefully**: Always use the Preview feature to see exactly what will be deleted
4. **Start Small**: Test with a few items first before bulk cleanup
5. **Keep Restore Points**: Don't delete restore points until you're certain you don't need them

### What Gets Protected

- ✅ Active conda environment (cannot be deleted)
- ✅ Base conda environment (cannot be deleted)
- ✅ System files and protected directories
- ✅ Files currently in use by running processes

### What Can Be Deleted

- ⚠️ **Conda Environments**: Unused conda environments (backed up before deletion)
- ⚠️ **Pip Cache**: All cached pip packages (will need to re-download)
- ⚠️ **System Temp Files**: Temporary files older than specified age
- ⚠️ **Browser Caches**: Cache files (will require re-login to websites)
- ⚠️ **Windows Update Cache**: Update download cache
- ⚠️ **Thumbnail Cache**: Windows thumbnail cache
- ⚠️ **Recycle Bin**: Contents of Recycle Bin

### Known Limitations

- **Browser Cache**: Clearing browser cache will log you out of websites
- **Conda Environments**: Large environments may take time to backup/restore
- **System Files**: Some system temp files may be locked and cannot be deleted
- **Restore Points**: Restore points take disk space - old ones are auto-cleaned after 30 days (configurable)

## Features

- **Anaconda Cleanup**: Remove unused conda environments with automatic backup
- **Pip Cache Cleanup**: Clear pip package cache
- **System Cleanup**: Remove temporary files, Windows caches
- **Browser Cleanup**: Clear cache from Chrome, Firefox, Edge, Opera
- **Automatic Backup**: Mandatory backup system before any deletion
- **Restore Points**: Restore deleted items from backup
- **Safety First**: Multiple safety checks and validations
- **Modern GUI**: Intuitive interface with clear visual feedback

## Installation

### Prerequisites
- Python 3.9 or higher
- pip (Python package installer)
- **Windows 10/11** (primary platform, Linux/Mac support may vary)

### Quick Start

1. **Navigate to the project directory:**
   ```bash
   cd CleanUp
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
   **Note:** If you encounter issues with PyQt5, try:
   ```bash
   pip install PyQt5 --upgrade
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

### Using Virtual Environment (Recommended)

To keep dependencies isolated:

```bash
# Create virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Activate it (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

## Usage

### First Time Setup

1. **Launch the application:**
   ```bash
   python main.py
   ```

2. **Review Settings**: Check the settings to configure:
   - Backup retention period
   - Maximum restore points
   - Safety levels for different cleanup types

3. **Start with Preview**: Always use Preview before actual cleanup

### Using the GUI

1. **Navigate through tabs** using the sidebar
2. **Click "Scan"** on any tab to find cleanup opportunities
3. **Review the list** of items found
4. **Select items** you want to clean (or deselect items you want to keep)
5. **Click "Preview"** to see detailed information about what will be deleted
6. **Click "Clean"** to perform cleanup (automatic backup is created first)

### Available Tabs

- **Home**: Overview and quick actions
- **Anaconda**: Remove unused conda environments
  - ⚠️ Active and base environments are automatically protected
  - ⚠️ Environments are backed up before deletion
- **Pip Cache**: Clear pip package cache
  - ⚠️ You'll need to re-download packages on next pip install
- **System**: Clean temporary files and Windows caches
  - ⚠️ Use age filter to avoid deleting recent files
- **Browser**: Clear browser caches (Chrome, Firefox, Edge, Opera)
  - ⚠️ Will log you out of websites
- **Restore Points**: View and manage backups
  - View details of what was backed up
  - Restore items if needed
  - Delete old restore points to free space

## Safety Features

- ✅ **Automatic backup** before any deletion
- ✅ **Protection of active conda environment** (cannot be deleted)
- ✅ **Protection of base conda environment** (cannot be deleted)
- ✅ **Process detection** (blocks cleanup if related processes running)
- ✅ **System file protection** (prevents deletion of critical system files)
- ✅ **Restore point system** for recovery
- ✅ **Input validation** (prevents invalid operations)
- ✅ **Thread-safe operations** (prevents GUI freezing)

## Restore Points

### Understanding Restore Points

- **Automatic Creation**: Restore points are created automatically before any deletion
- **Storage Location**: Stored in `backups/restore_points/` directory
- **Compression**: Restore points are compressed to save space
- **Retention**: Old restore points are auto-cleaned after 30 days (configurable)
- **Maximum Count**: Limited to 50 restore points by default (configurable)

### Restoring from Backup

1. Go to **Restore Points** tab
2. Click **Scan** to load available restore points
3. Select a restore point
4. Click **View Details** to see what was backed up
5. Click **Restore** to restore items (feature in development)

⚠️ **Note**: Full restore functionality is in development. Currently, conda environments can be restored, but file restoration may be limited.

## Standalone Executable

Create a standalone executable that runs **without Python or Docker**:

### Quick Build (Windows)

```bash
build.bat
```

This creates `dist/CleanUpTool.exe` - a single executable file (approximately 65 MB) that can be distributed to any Windows computer without requiring Python installation.

⚠️ **Note**: The executable is large because it includes Python and all dependencies. First run may be slower as it extracts files.

### Quick Build (Linux/Mac)

```bash
chmod +x build.sh
./build.sh
```

See [STANDALONE_BUILD.md](STANDALONE_BUILD.md) for detailed instructions.

## Docker Support

The application can also be run in Docker. See [DOCKER.md](DOCKER.md) for detailed Docker setup instructions.

**Quick Docker start:**
```bash
# Build image
docker build -t cleanup-tool .

# Run with X11 (Linux)
docker run -it --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix:rw cleanup-tool
```

## Troubleshooting

### Common Issues

1. **"Conda not found"**
   - Ensure conda is installed and in your PATH
   - Try running `conda --version` in terminal to verify

2. **"Pip not found"**
   - Ensure pip is installed: `python -m ensurepip --upgrade`
   - Try using `python -m pip` instead

3. **"Permission denied" errors**
   - Some files may require administrator privileges
   - Run the application as administrator if needed

4. **GUI doesn't appear**
   - Check if PyQt5 is installed: `pip install PyQt5`
   - Try running with console: Remove `--windowed` flag in build script

5. **Backup fails**
   - Check available disk space
   - Ensure write permissions in backup directory
   - Check backup directory path in settings

### Getting Help

- Check the logs in the application directory
- Review error messages in the status bar
- Ensure all prerequisites are installed

## Configuration

Configuration files are located in the `config/` directory:

- `defaults.json`: Default settings for safety levels, backup settings, etc.
- `ui_config.json`: UI-specific configuration

⚠️ **Warning**: Modifying configuration files incorrectly may cause the application to malfunction. Always backup configuration files before editing.

## Development

### Project Structure

```
CleanUp/
├── app.py                 # Application entry point
├── main.py                # Main script
├── config/                # Configuration files
├── core/                  # Core functionality
│   ├── backup_manager.py  # Backup system
│   ├── conda_manager.py   # Conda operations
│   ├── pip_manager.py     # Pip operations
│   └── ...
├── gui/                   # GUI components
│   ├── tabs/              # Tab implementations
│   └── ...
├── utils/                 # Utility functions
└── requirements.txt       # Python dependencies
```

### Contributing

⚠️ **This is a private repository.** Contributions should be discussed with the repository owner.

## License

See LICENSE file for details.

## Disclaimer

**THIS SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.**

**USE AT YOUR OWN RISK. Always backup your data before using this tool.**

---

**Version**: 1.0.0  
**Last Updated**: 2025  
**Platform**: Windows 10/11 (Primary), Linux/Mac (Partial Support)
