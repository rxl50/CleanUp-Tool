# How to Run CleanUp Tool

## Prerequisites

1. **Python 3.9 or higher** - Check your version:
   ```bash
   python --version
   ```
   or
   ```bash
   python3 --version
   ```

2. **pip** (Python package installer) - Usually comes with Python

## Step-by-Step Instructions

### Step 1: Navigate to the Project Directory

Open a terminal/command prompt and navigate to the CleanUp folder:

```bash
cd "C:\path\to\CleanUp"
```

### Step 2: Create a Virtual Environment (Recommended)

This keeps dependencies isolated:

```bash
python -m venv venv
```

Activate the virtual environment:

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### Step 3: Install Dependencies

Install all required packages:

```bash
pip install -r requirements.txt
```

This will install:
- PyQt5 (GUI framework)
- psutil (system information)
- send2trash (safe file deletion)
- And other dependencies

**Note:** If you encounter issues installing PyQt5, try:
```bash
pip install PyQt5 --upgrade
```

### Step 4: Run the Application

Simply run:

```bash
python main.py
```

or

```bash
python3 main.py
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'PyQt5'"

**Solution:** Install PyQt5:
```bash
pip install PyQt5
```

### Issue: "conda: command not found" or "pip: command not found"

**Solution:** 
- Make sure Python is installed and added to PATH
- For conda: Install Anaconda or Miniconda
- For pip: Usually comes with Python, but you may need to install it separately

### Issue: Application window doesn't appear

**Solution:**
- Check if Python process is running in Task Manager
- Try running from command line to see error messages
- Make sure you have a display/GUI environment (for remote servers, use X11 forwarding)

### Issue: Permission errors when cleaning

**Solution:**
- Run the application as Administrator (Windows) or with sudo (Linux)
- Some system files require elevated permissions

## First Run

When you first run the application:

1. The GUI window will open
2. You'll see a dashboard with disk space information
3. Navigate through tabs using the sidebar:
   - **Home**: Overview and quick actions
   - **Anaconda**: Clean conda environments
   - **Pip Cache**: Clean pip cache
   - **System**: Clean system temp files
   - **Browser**: Clean browser caches
   - **Restore Points**: Manage backups

4. Click "Scan" on any tab to find cleanup opportunities
5. Select items and click "Preview" to see what will be deleted
6. Click "Clean" to perform cleanup (backup is created automatically)

## Quick Start Example

```bash
# 1. Navigate to project
cd "C:\path\to\CleanUp"

# 2. Install dependencies (first time only)
pip install -r requirements.txt

# 3. Run the application
python main.py
```

## Running Without Virtual Environment

If you prefer not to use a virtual environment:

```bash
# Install dependencies globally (not recommended)
pip install -r requirements.txt

# Run the application
python main.py
```

**Warning:** Installing globally may cause conflicts with other Python projects.

## Additional Notes

- The application creates a `backups/` folder for restore points
- Logs are saved in the `logs/` folder
- Configuration is stored in `config/user_settings.json`
- All cleanup operations create automatic backups before deletion

## Need Help?

If you encounter any issues:
1. Check the error message in the terminal
2. Look at the logs in the `logs/` folder
3. Make sure all dependencies are installed correctly

