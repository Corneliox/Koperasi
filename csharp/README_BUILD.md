BUILD INSTRUCTIONS - KOPERASI BRIMOB (C# PORT)
==================================================

Prerequisites:
--------------
1. Microsoft .NET Framework 4.0 (Installed by default on updated Win 7).
2. Visual Studio 2010 or newer (or just the C# Compiler `csc.exe`).
3. System.Data.SQLite Binaries for .NET 4.0 (x86).

Directory Structure:
--------------------
```
Csharp/
  └── KoperasiBrimob/
       ├── KoperasiBrimob.sln
       ├── KoperasiBrimob.csproj
       ├── Program.cs
       ├── Forms/
       ├── Models/
       ├── Services/
       ├── Helpers/
       └── Properties/
```

How to Build (Visual Studio):
-----------------------------
1. Open `Csharp/KoperasiBrimob/KoperasiBrimob.sln`.
2. Add Reference to `System.Data.SQLite.dll`:
   - Download "sqlite-netFx40-binary-bundle-x86-2010-1.0.118.0.zip" (or similar) from system.data.sqlite.org.
   - Extract `System.Data.SQLite.dll`.
   - In VS, Right-click "References" -> Add Reference -> Browse -> Select the DLL.
3. Build Solution (Release / x86).

How to Build (Command Line / Offline):
--------------------------------------
If you don't have VS, you can use the .NET Framework compiler.

1. Place `System.Data.SQLite.dll` in the project folder.
2. Run this command from `Csharp/KoperasiBrimob/`:
   
   C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe /target:winexe /out:KoperasiBrimob.exe /recurse:*.cs /reference:System.Data.SQLite.dll /platform:x86

Running the Application:
------------------------
1. Ensure the following files are in the same folder as `KoperasiBrimob.exe`:
   - System.Data.SQLite.dll
   - SQLite.Interop.dll (This is CRITICAL for x86. It comes with the SQLite download).
   - koperasi_brimob.db (Will be created automatically if missing).

Single Executable (Advanced):
-----------------------------
To make a truly single .exe file without accompanying DLLs:
1. You must use a tool like "Costura.Fody" (NuGet package) if you have internet/NuGet access on a dev machine.
2. OR use "ILMerge".
3. OR manually embed the DLLs as "Embedded Resources" in Visual Studio and use `AppDomain.AssemblyResolve` in `Program.cs` to load them from memory (requires complex boilerplate code not included here to keep source readable).

For the target Windows 7 offline environment, the safest approach is to copy the folder containing the `.exe` and the two `.dll` files.

Features Implemented:
---------------------
- **Auth**: Admin/Admin123 default.
- **Tabs**: Dashboard, Sembako, Taktikal, Anggota, Pinjaman.
- **Loan**: Simulation (Principal + Flat Interest), Repayment.
- **Warehouse**: Stock In/Out, Returns (Reduces stock, logs RETURN).
- **Members**: Fuzzy Search (Levenshtein) to prevent duplicates.
- **Easter Egg**: Ctrl + Click Admin Icon 5 times to show Reset dialog.
- **Logging**: Immutable audit logs to SQLite.

Troubleshooting:
----------------
- "DllNotFoundException": Missing `SQLite.Interop.dll`.
- "BadImageFormatException": Mismatch between x86/x64. Ensure you built for x86 and are using x86 SQLite DLLs.
