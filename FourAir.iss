; Inno Setup脚本文件
; 用于打包FourAir浏览器多开管理器

#define MyAppName "FourAir浏览器多开管理器"
#define MyAppVersion "1.1.0"
#define MyAppPublisher "FourAir Community"
#define MyAppURL "https://github.com/EXLF/browsers"
#define MyAppExeName "FourAir浏览器多开管理器.exe"

[Setup]
; 应用程序基本信息
AppId={{F0415AB4-A30D-4CF7-B1F3-D2F345A7E123}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
; 启用压缩以减少安装包体积
Compression=lzma2/ultra64
SolidCompression=yes
; 为桌面图标添加选项
PrivilegesRequired=admin
OutputBaseFilename=FourAir浏览器多开管理器_安装程序
SetupIconFile=chrome_manager\resources\logo.ico
WizardStyle=modern
; 新版Inno Setup已默认支持Unicode，无需额外设置
UsePreviousAppDir=yes
CloseApplications=yes
CloseApplicationsFilter=*{#MyAppExeName}

[Languages]
Name: "chinese"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "在桌面上创建图标"; GroupDescription: "附加图标:"; Flags: unchecked
Name: "quicklaunchicon"; Description: "在快速启动栏创建图标"; GroupDescription: "附加图标:"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; 主程序 - 检查文件是否存在
#if FileExists("dist\"+MyAppExeName)
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
#else
#error 找不到主程序文件，请先运行PyInstaller生成可执行文件
#endif

; 数据目录
Source: "chrome_manager\resources\*"; DestDir: "{app}\resources\"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; 创建开始菜单和桌面图标
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; 安装完成后运行
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Dirs]
; 创建数据目录
Name: "{commonappdata}\ChromeShortcuts"; Flags: uninsneveruninstall

[Registry]
; 添加注册表信息
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppName}"; ValueType: string; ValueName: "DisplayIcon"; ValueData: "{app}\{#MyAppExeName}"
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppName}"; ValueType: string; ValueName: "DisplayVersion"; ValueData: "{#MyAppVersion}"
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppName}"; ValueType: string; ValueName: "Publisher"; ValueData: "{#MyAppPublisher}" 