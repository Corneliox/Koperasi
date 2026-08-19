; Inno Setup Script for Koperasi Brimob v4.2
; Target: Windows 10 / Windows 11 (64-bit Native)

#define MyAppName "Koperasi Brimob"
#define MyAppVersion "4.2"
#define MyAppPublisher "Cornelio"
#define MyAppURL "https://github.com/Corneliox/koperasi_brimob"
#define MyAppExeName "KoperasiBrimob.exe"

[Setup]
AppId={{C62B6D4F-8F32-4161-9C55-789012345678}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} v{#MyAppVersion} (Win10/11 x64)
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableDirPage=no
DisableProgramGroupPage=no
UsePreviousAppDir=yes
PrivilegesRequired=admin
OutputDir=.
OutputBaseFilename=KoperasiBrimob_Setup_v{#MyAppVersion}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes
RestartApplications=yes
MinVersion=10.0
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Dirs]
Name: "{app}\logs"; Permissions: everyone-full

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
var
  KeepData: Boolean;

// Verify Windows 10/11 64-bit requirement on setup launch
function InitializeSetup(): Boolean;
var
  Version: TWindowsVersion;
begin
  GetWindowsVersionEx(Version);
  if (Version.Major < 10) or (not IsWin64) then
  begin
    MsgBox('Instalasi Dibatalkan.' + #13#10 + #13#10 + 
           'Versi Koperasi Brimob v' + '{#MyAppVersion}' + ' ini dikhususkan secara native untuk Windows 10 dan Windows 11 (64-bit).' + #13#10 +
           'Sistem operasi ini tidak memenuhi spesifikasi minimum.', mbCriticalError, MB_OK);
    Result := False;
    Exit;
  end;
  Result := True;
end;

// Uninstallation confirmation for database retention
function InitializeUninstall(): Boolean;
begin
  case MsgBox('Apakah Anda ingin menghapus DATABASE dan DATA TRANSAKSI juga?' + #13#10 + #13#10 + 
              'Pilih NO jika Anda hanya ingin menginstal ulang aplikasi tanpa kehilangan data.' + #13#10 +
              'Pilih YES jika Anda ingin membersihkan seluruh data dari komputer ini.', 
              mbConfirmation, MB_YESNOCANCEL) of
    IDYES: 
      begin
        KeepData := False;
        Result := True;
      end;
    IDNO: 
      begin
        KeepData := True;
        Result := True;
      end;
    IDCANCEL:
      Result := False;
  end;
end;

procedure CurUninstallStepChanged(UninstallStep: TUninstallStep);
var
  DataDir: String;
begin
  if (UninstallStep = usPostUninstall) and (not KeepData) then
  begin
    DataDir := ExpandConstant('{userappdata}\KoperasiBrimob');
    if DirExists(DataDir) then
    begin
      if DelTree(DataDir, True, True, True) then
        Log('Data directory deleted: ' + DataDir)
      else
        Log('Failed to delete data directory: ' + DataDir);
    end;
    
    // Clean logs in installation directory
    DataDir := ExpandConstant('{app}\logs');
    if DirExists(DataDir) then
      DelTree(DataDir, True, True, True);
  end;
end;
