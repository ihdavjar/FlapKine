#define MyAppVersion "0.2.0"

[Setup]
AppName=FlapKine
AppVersion={#MyAppVersion}
DefaultDirName={autopf}\FlapKine
DefaultGroupName=FlapKine
OutputBaseFilename=FlapKine-{#MyAppVersion}-x64-setup
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
DisableProgramGroupPage=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "..\dist\Flapkine\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{group}\FlapKine"; Filename: "{app}\FlapKine.exe"; IconFilename: "{app}\FlapKine.exe"
Name: "{userdesktop}\FlapKine"; Filename: "{app}\FlapKine.exe"; Tasks: desktopicon; IconFilename: "{app}\FlapKine.exe"
Name: "{group}\Uninstall FlapKine"; Filename: "{uninstallexe}"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"
