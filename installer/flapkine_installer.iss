[Setup]
AppName=Flapkine
AppVersion=0.1.0
DefaultDirName={autopf}\Flapkine
DefaultGroupName=Flapkine
OutputBaseFilename=setup_flapkine
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
DisableProgramGroupPage=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "dist\FlapkineApp\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{group}\Flapkine"; Filename: "{app}\Flapkine.exe"
Name: "{userdesktop}\Flapkine"; Filename: "{app}\FlapkineApp.exe"; Tasks: desktopicon
Name: "{group}\Uninstall Flapkine"; Filename: "{uninstallexe}"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"