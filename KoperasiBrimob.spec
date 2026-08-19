# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_all

datas = []
binaries = []
hiddenimports = [
    'customtkinter', 'darkdetect', 'tkinter', 'tkinter.ttk', 'tkinter.messagebox',
    'tkcalendar', 'babel', 'babel.numbers', 'babel.dates', 'sqlite3', 'subprocess',
    'pandas', 'pandas.io.formats.excel', 'openpyxl', 'openpyxl.styles', 'openpyxl.utils',
    'openpyxl.cell', 'xlsxwriter', 'fpdf', 'fpdf2', 'PIL', 'PIL.Image', 'PIL.ImageTk',
    'app', 'app.database', 'app.database.connection', 'app.modules',
    'app.modules.warehouse', 'app.modules.members', 'app.modules.loans',
    'app.modules.transactions', 'app.ui', 'app.ui.login_frame',
    'app.ui.category_select_frame', 'app.ui.dashboard_frame', 'app.ui.store_frame',
    'app.ui.history_frame', 'app.ui.members_frame', 'app.ui.loans_frame',
    'app.ui.financial_frame', 'app.ui.admin_panel', 'app.utils', 'app.utils.export',
    'app.utils.excel_import', 'app.utils.receipt', 'app.utils.fuzzy_search',
    'app.utils.error_handler', 'app.utils.decorators', 'app.utils.audit_log',
    'app.utils.financial_report', 'app.utils.emoji_fix'
]

datas += collect_data_files('babel')
hiddenimports += collect_submodules('pandas')
hiddenimports += collect_submodules('PIL')

tmp_ctk = collect_all('customtkinter')
datas += tmp_ctk[0]; binaries += tmp_ctk[1]; hiddenimports += tmp_ctk[2]

tmp_tkcal = collect_all('tkcalendar')
datas += tmp_tkcal[0]; binaries += tmp_tkcal[1]; hiddenimports += tmp_tkcal[2]

tmp_babel = collect_all('babel')
datas += tmp_babel[0]; binaries += tmp_babel[1]; hiddenimports += tmp_babel[2]

tmp_fpdf = collect_all('fpdf2')
datas += tmp_fpdf[0]; binaries += tmp_fpdf[1]; hiddenimports += tmp_fpdf[2]

icon_file = 'icon.ico' if os.path.exists('icon.ico') else None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pytest', 'IPython', 'matplotlib', 'scipy', 'tornado', 'black', 'nbformat', 'jedi', 'jinja2'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='KoperasiBrimob',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file,
)
