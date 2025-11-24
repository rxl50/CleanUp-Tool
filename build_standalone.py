"""Build script for creating standalone executable."""

import PyInstaller.__main__
import sys
import os
from pathlib import Path

def build_executable():
    """Build standalone executable using PyInstaller."""
    
    # Get project root
    project_root = Path(__file__).parent
    
    # Determine path separator for --add-data
    # Windows uses semicolon, Unix uses colon
    sep = ';' if sys.platform == 'win32' else ':'
    
    # PyInstaller arguments
    args = [
        'main.py',  # Main script
        '--name=CleanUpTool',  # Executable name
        '--onefile',  # Single executable file
        '--windowed',  # No console window (GUI app)
        '--icon=NONE',  # Add icon file path if you have one
        '--hidden-import=PyQt5.QtCore',
        '--hidden-import=PyQt5.QtGui',
        '--hidden-import=PyQt5.QtWidgets',
        '--hidden-import=psutil',
        '--hidden-import=send2trash',
        '--collect-all=PyQt5',  # Collect all PyQt5 files
        '--noconfirm',  # Overwrite output without asking
        '--clean',  # Clean cache before building
    ]
    
    # Add config files
    config_files = ['config/defaults.json', 'config/ui_config.json']
    for config_file in config_files:
        file_path = project_root / config_file
        if file_path.exists():
            # Extract just the filename for destination
            dest_name = Path(config_file).name
            args.append(f'--add-data={config_file}{sep}config')
    
    # Windows specific
    if sys.platform == 'win32':
        args.append('--uac-admin')  # Request admin privileges if needed
    
    print("Building standalone executable...")
    print(f"Arguments: {' '.join(args)}")
    print()
    
    # Run PyInstaller
    PyInstaller.__main__.run(args)
    
    print()
    print("=" * 60)
    print("Build complete!")
    print("=" * 60)
    print(f"Executable location: {project_root / 'dist' / 'CleanUpTool.exe'}")
    print()
    print("You can now distribute the executable from the 'dist' folder.")
    print("Note: The first run may be slower as it extracts files.")

if __name__ == '__main__':
    build_executable()

