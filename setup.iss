#define MyAppName "FourAir社区专用Chrome多开管理器"
#define MyAppVersion "1.1"
#define MyAppPublisher "FourAir"
#define MyAppURL "https://github.com/EXLF/browsers"
#define MyAppExeName "chrome_manager.exe"

[Setup]
; 注: AppId的值为单独标识该应用程序。
; 不要在其他安装程序中使用相同的AppId值。
AppId={{F7A6B47E-1234-4567-8901-ABCDEFGHIJKL}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
; 移除以下行，以在管理员安装的情况下运行安装程序（安装用于所有用户）。
PrivilegesRequired=lowest
OutputDir=installer
OutputBaseFilename=ChromeManager_Setup
SetupIconFile=chrome_manager\resources\logo.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "chinesesimp"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
Source: "dist\chrome_manager\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\chrome_manager\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent 