import subprocess
import sys
import platform
import ctypes
import os
from datetime import datetime

log_messages = []

def log_print(*args, **kwargs):
    msg = " ".join(map(str, args))
    print(msg, **kwargs)
    log_messages.append(msg)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def check_sp1():
    log_print(f"Checking for Windows Service Pack 1...")
    ps_command = r"""
    $os = Get-WmiObject Win32_OperatingSystem
    if ($os.ServicePackMajorVersion -ge 1) { Write-Output "FOUND" } else { Write-Output "MISSING" }
    """
    try:
        process = subprocess.Popen(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_command],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True, 
            encoding='utf-8',
            errors='replace'
        )
        stdout, _ = process.communicate()
        return "FOUND" in stdout.strip()
    except:
        return False

def check_kb(kb_id, description):
    log_print(f"Checking for {kb_id} ({description})...")
    
    # PowerShell command to check registry directly for the package
    # We check Component Based Servicing (CBS) packages as it's more reliable for specific updates
    ps_command = f"""
    $ErrorActionPreference = 'Stop'
    try {{
        $path = "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Component Based Servicing\\Packages"
        $result = Get-ChildItem -Path $path -ErrorAction SilentlyContinue | Where-Object {{ $_.Name -like "*{kb_id}*" }}
        
        if ($result) {{
            Write-Output "FOUND"
        }} else {{
            # Fallback check using Get-HotFix (standard method)
            $hotfix = Get-HotFix -Id {kb_id} -ErrorAction SilentlyContinue
            if ($hotfix) {{
                Write-Output "FOUND"
            }} else {{
                Write-Output "MISSING"
            }}
        }}
    }} catch {{
        Write-Output "ERROR"
    }}
    """
    
    try:
        process = subprocess.Popen(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_command],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True, 
            encoding='utf-8',
            errors='replace'
        )
        stdout, _ = process.communicate()
        
        if "FOUND" in stdout.strip():
            log_print(f"   [OK] {kb_id} is installed.")
            return True
        else:
            log_print(f"   [X] {kb_id} is MISSING.")
            return False
            
    except Exception as e:
        log_print(f"   [!] Failed to check {kb_id}: {e}")
        return False

def main():
    # Set console title
    if sys.platform == 'win32':
        ctypes.windll.kernel32.SetConsoleTitleW("System Requirement Check - Koperasi Brimob")
    
    log_print(f"Run Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log_print(f"Operating System: {platform.system()} {platform.release()} ({platform.version()})")
    log_print(f"Machine Architecture: {platform.machine()}")
    is_64bits = sys.maxsize > 2**32
    log_print(f"Python Architecture: {'64-bit' if is_64bits else '32-bit'}")
    log_print("-" * 60)

    # Main logic
    is_win7 = "7" in platform.release()
    
    if not is_win7:
        log_print("Note: You are not running Windows 7.")
        log_print("This check is primarily for Windows 7 users. Newer Windows versions usually have these updates built-in.")
        log_print("Scanning anyway to ensure environment integrity...")
    
    log_print("\nScanning system requirements...\n")
    
    # Define dependency chain
    # Format: (Check Function/Lambda, Name, Description, Download Info)
    # The order matters!
    
    checks = []
    
    # 1. SP1 Check (Only strict for Win 7)
    if is_win7:
        checks.append({
            "check": check_sp1,
            "id": "SP1", 
            "name": "Service Pack 1",
            "required": True
        })

    # 2. KB2533623 (Critical for ctypes/PyInstaller)
    checks.append({
        "check": lambda: check_kb("KB2533623", "Insecure Library Loading Update"),
        "id": "KB2533623",
        "name": "Insecure Library Loading Update (Fixes WinError 87)",
        "required": True
    })

    # 3. KB3020369
    checks.append({
        "check": lambda: check_kb("KB3020369", "Servicing Stack Update"),
        "id": "KB3020369",
        "name": "Servicing Stack Update",
        "required": True
    })

    # 3. KB4474419
    checks.append({
        "check": lambda: check_kb("KB4474419", "SHA-2 Code Signing Support"),
        "id": "KB4474419",
        "name": "SHA-2 Code Signing Support",
        "required": True
    })
    
    # 4. KB4490628
    checks.append({
        "check": lambda: check_kb("KB4490628", "SHA-2 Support Update"),
        "id": "KB4490628",
        "name": "SHA-2 Support Update",
        "required": True
    })

    # 5. KB2999226 (The Goal)
    checks.append({
        "check": lambda: check_kb("KB2999226", "Universal C Runtime"),
        "id": "KB2999226",
        "name": "Universal C Runtime",
        "required": True
    })

    missing_items = []
    
    for item in checks:
        if not item["check"]():
            missing_items.append(item)

    arch = "x86" if platform.machine().endswith('86') else "x64"
    if platform.machine() == "AMD64":
        arch = "x64"
    
    log_print("-" * 60)
    
    if not missing_items:
        log_print("\n[SUCCESS] All system requirements are met.")
        log_print("You are ready to run the application.")
    else:
        log_print("\n[ATTENTION] Missing requirements detected!")
        log_print(f"System Architecture Detected: {platform.machine()} ({arch})")
        log_print("To avoid 'Update not applicable' errors, please install the missing updates in the following EXACT order:\n")
        
        for i, item in enumerate(missing_items, 1):
            log_print(f"{i}. {item['id']} - {item['name']}")
            
        log_print("\nInstallation Instructions:")
        
        if any(x['id'] == 'SP1' for x in missing_items):
             log_print("\n[STEP 1] Install Windows 7 Service Pack 1")
             log_print("   - Ensure your Windows Update is working or download SP1 manually from Microsoft Catalog.")

        if any(x['id'] == 'KB2533623' for x in missing_items):
             log_print("\n[STEP 2] Install KB2533623 (Insecure Library Loading Update)")
             log_print("   - CRITICAL: This fixes the 'WinError 87' crash at startup.")
             log_print(f"   - Download: Search 'KB2533623 Windows 7 {arch}' on Microsoft Update Catalog.")

        if any(x['id'] == 'KB3020369' for x in missing_items):
             log_print("\n[STEP 2] Install KB3020369 (Servicing Stack Update)")
             log_print("   - This is required before installing SHA-2 updates.")
             log_print(f"   - Download: Search 'KB3020369 Windows 7 {arch}' on Microsoft Update Catalog.")

        if any(x['id'] in ['KB4474419', 'KB4490628'] for x in missing_items):
             log_print("\n[STEP 3] Install SHA-2 Support Updates (KB4474419 & KB4490628)")
             log_print("   - Required to install modern updates signed with SHA-2.")
             log_print(f"   - Download: Search 'KB4474419 Windows 7 {arch}' and 'KB4490628 Windows 7 {arch}'.")

        if any(x['id'] == 'KB2999226' for x in missing_items):
             log_print("\n[STEP 4] Install KB2999226 (Universal C Runtime)")
             log_print("   - The final requirement for Python applications.")
             log_print(f"   - Link: https://www.microsoft.com/en-us/download/details.aspx?id=49077 (Select {arch} version)")

        log_print("\nIMPORTANT: Restart your computer after EACH step if prompted.")
    
    log_print("\n" + "=" * 60)
    
    # Save log to file
    try:
        log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log.txt")
        with open(log_file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(log_messages))
        print(f"\nLog saved to: {log_file_path}")
    except Exception as e:
        print(f"\nFailed to save log: {e}")

    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
