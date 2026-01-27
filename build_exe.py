"""
PyInstaller Build Script for Koperasi Brimob
Builds standalone .exe for Windows 7 x32 - Windows 11 x64
"""
import PyInstaller.__main__
import os
import sys

# Get the directory where the script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Application info
APP_NAME = "KoperasiBrimob"
MAIN_SCRIPT = os.path.join(BASE_DIR, "main.py")
ICON_PATH = os.path.join(BASE_DIR, "icon.ico")  # Set to your .ico file path if you have one

# Hidden imports needed for the application
HIDDEN_IMPORTS = [
    # CustomTkinter
    'customtkinter',
    'darkdetect',
    
    # Tkinter & Calendar
    'tkinter',
    'tkinter.ttk',
    'tkinter.messagebox',
    'tkcalendar',
    
    # Babel (required by tkcalendar)
    'babel',
    'babel.numbers',
    'babel.dates',
    
    # Database
    'sqlite3',
    
    # Data Processing
    'pandas',
    'pandas.io.formats.excel',
    'openpyxl',
    'openpyxl.styles',
    'openpyxl.utils',
    'openpyxl.cell',
    'xlsxwriter',
    
    # PDF Generation
    'fpdf',
    'fpdf2',
    
    # Image Processing
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    
    # App modules
    'app',
    'app.database',
    'app.database.connection',
    'app.modules',
    'app.modules.warehouse',
    'app.modules.members',
    'app.modules.loans',
    'app.modules.transactions',
    'app.ui',
    'app.ui.login_frame',
    'app.ui.category_select_frame',
    'app.ui.dashboard_frame',
    'app.ui.store_frame',
    'app.ui.history_frame',
    'app.ui.members_frame',
    'app.ui.loans_frame',
    'app.utils',
    'app.utils.export',
]

# Data files to include
DATAS = [
    # Include customtkinter assets
]

# Try to find customtkinter path
try:
    import customtkinter
    ctk_path = os.path.dirname(customtkinter.__file__)
    DATAS.append((ctk_path, 'customtkinter'))
except ImportError:
    print("Warning: customtkinter not found")

# Build arguments
build_args = [
    MAIN_SCRIPT,
    f'--name={APP_NAME}',
    '--onefile',  # Single executable
    '--windowed',  # No console window
    '--clean',  # Clean cache
    '--noconfirm',  # Overwrite without asking
]

# Add hidden imports
for hidden in HIDDEN_IMPORTS:
    build_args.append(f'--hidden-import={hidden}')

# Add data files
for src, dest in DATAS:
    if os.path.exists(src):
        build_args.append(f'--add-data={src}{os.pathsep}{dest}')

# Add icon if exists
if ICON_PATH and os.path.exists(ICON_PATH):
    build_args.append(f'--icon={ICON_PATH}')

# Additional options for compatibility
build_args.extend([
    '--collect-all=customtkinter',
    '--collect-all=tkcalendar',
    '--collect-all=babel',
    '--collect-data=babel',
])

def build():
    """Run PyInstaller build"""
    print("=" * 50)
    print("Building Koperasi Brimob Application")
    print("=" * 50)
    print(f"\nBase Directory: {BASE_DIR}")
    print(f"Main Script: {MAIN_SCRIPT}")
    print(f"\nBuild Arguments:")
    for arg in build_args:
        print(f"  {arg}")
    print("\n" + "=" * 50)
    print("Starting build process...")
    print("=" * 50 + "\n")
    
    try:
        PyInstaller.__main__.run(build_args)
        print("\n" + "=" * 50)
        print("BUILD SUCCESSFUL!")
        print(f"Executable: dist/{APP_NAME}.exe")
        print("=" * 50)
    except Exception as e:
        print(f"\nBUILD FAILED: {e}")
        sys.exit(1)


if __name__ == "__main__":
    build()
