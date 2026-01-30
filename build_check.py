import PyInstaller.__main__
import os

APP_NAME = "Check_KB2999226"
MAIN_SCRIPT = "check_kb.py"

print(f"Building {APP_NAME}...")

PyInstaller.__main__.run([
    MAIN_SCRIPT,
    f'--name={APP_NAME}',
    '--onefile',
    '--clean',
    '--console',  # We want a console window to show the output
    '--uac-admin', # Request admin just in case registry access needs it (though read usually doesn't)
])

print(f"\nBuild complete. Check dist/{APP_NAME}.exe")
