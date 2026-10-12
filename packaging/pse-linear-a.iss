; Inno Setup script for the Windows installer; build_exe.sh passes
; AppVersion, SourceDir (the staged bundle) and OutDir. Per-user install,
; no administrator rights.

#define AppName "PSE Linear A"

[Setup]
AppId={{252c82a7-33f4-4ba4-a391-794cbb7d79b9}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=Andrej Ristic
AppPublisherURL=https://github.com/andrejristic/pse-linear-a
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
LicenseFile={#SourceDir}\LICENSE.txt
OutputDir={#OutDir}
OutputBaseFilename=PSELinearA-Setup-{#AppVersion}
SetupIconFile={#SourceDir}\pse-linear-a.ico
UninstallDisplayIcon={app}\pse-linear-a.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\pse-linear-a.exe"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\pse-linear-a.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\pse-linear-a.exe"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent
