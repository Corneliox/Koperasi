RECONSTRUCTED C# KOPERASI BRIMOB v3
=====================================

Status:
-------
- Architecture: 100% (Dark Theme, Sidebar, Services)
- Logic Parity: 100% (Warehouse Rules, Levenshtein, Loan Sim)
- UI Implementation:
  - Dashboard: ✅ Implemented
  - Sembako/Taktikal: ✅ Implemented (Grid + Search + Add Item)
  - Members: ✅ Implemented
  - Loans: ✅ Implemented
  - Admin: ✅ Easter Egg & Login
  - NEW: Import/Export Excel (CSV), Database Backup/Restore

Files Added:
------------
- Views/Panels/DashboardPanel.cs
- Views/Panels/StorePanel.cs
- Views/Dialogs/BaseDialog.cs
- Views/Dialogs/AddItemDialog.cs
- Services/DataService.cs (Import/Export logic)

Fixes:
------
- UI Overflow: All grids now have a 2.5% right margin (Padding) to prevent cutoff.
- Import: "Import CSV" button added to Store Panel.
- Export: "Export Excel" added to Store & History Panels.
- Backup: "Backup/Restore DB" added to Admin Panel (Laporan).

How to Build:
-------------
C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe /target:winexe /platform:x86 /out:bin\KoperasiBrimob.exe /r:System.Data.SQLite.dll,Microsoft.VisualBasic.dll /recurse:*.cs

Using Import:
-------------
1. Create a CSV file with columns: Name, Stock, Price (Optional).
2. Click "Import CSV" in the Sembako/Taktikal panel.
3. Select the file. Items will be added or stock updated.
