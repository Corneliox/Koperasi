import PyInstaller.__main__
import os
import sys
import platform

APP_NAME = "Check_KB2999226"
MAIN_SCRIPT = "check_kb.py"

# Architecture Check for Build Environment
is_64bits = sys.maxsize > 2**32
print(f"Build Environment: Python {platform.python_version()} ({'64-bit' if is_64bits else '32-bit'})")

if is_64bits:
    print("\n[WARNING] You are building with a 64-bit Python environment.")
    print("The resulting .exe will ONLY run on 64-bit Windows.")
    print("It will NOT run on Windows 7 32-bit.")
    print("To build for 32-bit Windows, you must install and use a 32-bit version of Python.")
    print("Proceeding with build...\n")
else:
    print("[INFO] Building with 32-bit Python. This should be compatible with 32-bit and 64-bit Windows.\n")

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
