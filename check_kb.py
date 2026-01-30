import subprocess
import sys
import platform
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def check_kb2999226():
    print("=" * 60)
    print("Checking for Windows 7 Update KB2999226 (Universal C Runtime)")
    print("=" * 60)
    
    # PowerShell command to check registry directly for the package
    # We check Component Based Servicing (CBS) packages as it's more reliable for specific updates
    ps_command = r"""
    $ErrorActionPreference = 'Stop'
    try {
        $path = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing\Packages"
        $result = Get-ChildItem -Path $path -ErrorAction SilentlyContinue | Where-Object { $_.Name -like \"*KB2999226*\" }
        
        if ($result) {
            Write-Output "FOUND"
            foreach ($item in $result) {
                Write-Output $item.Name
            }
        } else {
            # Fallback check using Get-HotFix (standard method)
            $hotfix = Get-HotFix -Id KB2999226 -ErrorAction SilentlyContinue
            if ($hotfix) {
                Write-Output "FOUND_HOTFIX"
            } else {
                Write-Output "MISSING"
            }
        }
    } catch {
        Write-Output "ERROR: $_"
    }
    """
    
    try:
        # Run PowerShell command
        process = subprocess.Popen(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_command],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        
        output = stdout.strip()
        
        if "FOUND" in output or "FOUND_HOTFIX" in output:
            print("\n[SUCCESS] Update KB2999226 is INSTALLED.")
            if "Package_" in output:
                print("\nRegistry entries found:")
                for line in output.split('\n'):
                    if "FOUND" not in line:
                        print(f" - {line}")
            return True
            
        elif "MISSING" in output:
            print("\n[FAILURE] Update KB2999226 is NOT FOUND on this system.")
            return False
            
        else:
            print(f"\n[ERROR] Could not verify update status.\nOutput: {output}\nError: {stderr}")
            return False
            
    except Exception as e:
        print(f"\n[EXCEPTION] Failed to run check: {e}")
        return False

def main():
    # Set console title
    if sys.platform == 'win32':
        ctypes.windll.kernel32.SetConsoleTitleW("System Requirement Check - KB2999226")
    
    print(f"Operating System: {platform.system()} {platform.release()} ({platform.version()})")
    print(f"Architecture: {platform.machine()}")
    print("-" * 60)

    # Main logic
    is_win7 = "7" in platform.release()
    
    if not is_win7:
        print("Note: You are not running Windows 7.")
        print("This check is primarily for Windows 7 users, but we will scan anyway.")
    
    print("\nScanning registry and hotfixes...")
    success = check_kb2999226()
    
    print("-" * 60)
    if not success:
        print("\n!!! ACTION REQUIRED !!!")
        print("This computer is missing a critical update required to run the application.")
        print("Please download and install KB2999226 from Microsoft:")
        print("\nLINK: https://www.microsoft.com/en-us/download/details.aspx?id=49077")
        print("\n1. Go to the link above.")
        print("2. Download the update.")
        print("3. Install it and Restart your computer.")
        print("4. Run this application again.")
        print("!" * 60)
        
        # Open browser automatically if they want?
        # Better to just show link to avoid unexpected behavior.
    else:
        print("\nSystem Check Passed. You are ready to run the main application.")
    
    print("\n" + "=" * 60)
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
