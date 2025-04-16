#define MyAppVersion "0.1.0"

[Setup]
AppName=Flapkine
AppVersion={#MyAppVersion}
DefaultDirName={autopf}\Flapkine
DefaultGroupName=Flapkine
OutputBaseFilename=Flapkine-{#MyAppVersion}-x64-setup
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
DisableProgramGroupPage=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "..\dist\FlapkineApp\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{group}\Flapkine"; Filename: "{app}\Flapkine.exe"; IconFilename: "{app}\Flapkine.exe"
Name: "{userdesktop}\Flapkine"; Filename: "{app}\Flapkine.exe"; Tasks: desktopicon; IconFilename: "{app}\Flapkine.exe"
Name: "{group}\Uninstall Flapkine"; Filename: "{uninstallexe}"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"
