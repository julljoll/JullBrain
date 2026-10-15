; ===================================================================
;  JullBrain - Instalador Windows
;  Creado con Inno Setup 6
;  Autor: Jull Ortiz | Apache License 2.0 (C) 2026
; ===================================================================

#define AppName    "JullBrain"
#define AppVersion "2.0"
#define AppPublisher "Jull Ortiz"
#define AppURL     "https://sha256.us"
#define AppExeName "JullBrain.exe"
#define AppId      "{{A7F3D8C2-4B1E-4F9A-B2D6-8C5E1F3A7B4D}"

[Setup]
AppId={#AppId}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} v{#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
DefaultDirName={autopf}\JullBrain
DefaultGroupName={#AppName}
DisableProgramGroupPage=no
OutputDir=dist
OutputBaseFilename=JullBrain_Instalador
SetupIconFile=..\jullbrain.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
WizardResizable=no
UninstallDisplayIcon={app}\jullbrain.ico
UninstallDisplayName={#AppName}
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog
MinVersion=10.0.17763
DisableWelcomePage=no
LicenseFile=LICENSE.txt
; Colores del asistente (fondo oscuro, texto dorado)
WizardImageFile=compiler:WizModernImage.bmp
WizardSmallImageFile=compiler:WizModernSmallImage.bmp

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[CustomMessages]
spanish.InstallPython=Instalando dependencias y entorno Python...
spanish.ConfiguringVenv=Configurando entorno virtual (esto puede tardar varios minutos)...
spanish.DependenciesNote=NOTA: La primera configuracion requiere conexion a Internet para descargar las dependencias de IA.

[Tasks]
Name: "desktopicon";    Description: "Crear icono en el Escritorio";    GroupDescription: "Iconos adicionales:"
Name: "quicklaunchicon"; Description: "Crear icono en la barra de tareas"; GroupDescription: "Iconos adicionales:"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; --- Ejecutable GUI compilado con Flet ---
Source: "..\dist\JullBrain.exe";      DestDir: "{app}"; Flags: ignoreversion

; --- Scripts Python principales ---
Source: "..\convert_normativas.py";     DestDir: "{app}"; Flags: ignoreversion
Source: "..\legalizer.py";              DestDir: "{app}"; Flags: ignoreversion
Source: "..\metadata_extractor.py";     DestDir: "{app}"; Flags: ignoreversion
Source: "..\validator.py";              DestDir: "{app}"; Flags: ignoreversion
Source: "..\chunker.py";                DestDir: "{app}"; Flags: ignoreversion
Source: "..\jullbrain_icon_generator.py";  DestDir: "{app}"; Flags: ignoreversion

; --- Scripts de inicio ---
Source: "..\iniciar_conversion.bat";    DestDir: "{app}"; Flags: ignoreversion
Source: "post_install.bat";             DestDir: "{app}"; Flags: ignoreversion deleteafterinstall

; --- Iconos y recursos graficos ---
Source: "..\jullbrain.ico";  DestDir: "{app}"; Flags: ignoreversion
Source: "..\jullbrain.png";  DestDir: "{app}"; Flags: ignoreversion

; --- Documentacion ---
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion

; --- Carpetas de datos (se crean vacias para que el usuario coloque sus archivos) ---
; (Las carpetas se crean en [Dirs])

[Dirs]
; Carpetas de entrada y salida
Name: "{app}\normativas_pdf";    Permissions: users-modify
Name: "{app}\normativas_rag";    Permissions: users-modify
Name: "{app}\normativas_chunks"; Permissions: users-modify
Name: "{app}\formatos_word";     Permissions: users-modify
Name: "{app}\formatos_rag";      Permissions: users-modify
Name: "{app}\.conversion_cache"; Permissions: users-modify

[Icons]
; --- Acceso directo principal en el Menu Inicio ---
Name: "{group}\{#AppName}";                      Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\jullbrain.ico"; WorkingDir: "{app}"
Name: "{group}\Carpeta normativas_pdf (PDFs)";   Filename: "{app}\normativas_pdf";         IconFilename: "{sys}\shell32.dll"; IconIndex: 3
Name: "{group}\Carpeta formatos_word (Word)";    Filename: "{app}\formatos_word";          IconFilename: "{sys}\shell32.dll"; IconIndex: 3
Name: "{group}\Carpeta normativas_rag (Salida PDF)"; Filename: "{app}\normativas_rag";     IconFilename: "{sys}\shell32.dll"; IconIndex: 3
Name: "{group}\Carpeta formatos_rag (Salida Word)";  Filename: "{app}\formatos_rag";       IconFilename: "{sys}\shell32.dll"; IconIndex: 3
Name: "{group}\Desinstalar {#AppName}";          Filename: "{uninstallexe}"; IconFilename: "{app}\jullbrain.ico"

; --- Icono en el Escritorio (opcional) ---
Name: "{autodesktop}\{#AppName}";    Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\jullbrain.ico"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
; Ejecutar el script de post-instalacion para crear el venv e instalar dependencias
Filename: "{cmd}"; Parameters: "/C ""{app}\post_install.bat"" ""{app}"""; StatusMsg: "Configurando entorno Python y dependencias IA (puede tardar 5-15 min)..."; Flags: runhidden waituntilterminated

; Ofrecer abrir el programa al terminar
Filename: "{app}\{#AppExeName}"; Description: "Iniciar {#AppName} ahora"; Flags: nowait postinstall skipifsilent unchecked

[UninstallDelete]
Type: filesandordirs; Name: "{app}\docling_env"
Type: filesandordirs; Name: "{app}\__pycache__"
Type: filesandordirs; Name: "{app}\.conversion_cache"

[Code]
// ==============================================================
//  Pagina de bienvenida personalizada con informacion del sistema
// ==============================================================

procedure InitializeWizard();
var
  WelcomePage: TWizardPage;
begin
  // No se requiere codigo extra, Inno Setup maneja la pagina de bienvenida
end;

// Verificar Python antes de instalar
function InitializeSetup(): Boolean;
var
  PythonPath: String;
  ResultCode: Integer;
begin
  Result := True;
  
  // Buscar Python en el PATH
  if not Exec('cmd.exe', '/C python --version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    if MsgBox(
      'Python 3.10 o superior no fue encontrado en el sistema.' + Chr(13) + Chr(10) +
      Chr(13) + Chr(10) +
      'JullBrain requiere Python 3.10+ para funcionar.' + Chr(13) + Chr(10) +
      Chr(13) + Chr(10) +
      'Puede descargar Python gratuitamente desde:' + Chr(13) + Chr(10) +
      'https://www.python.org/downloads/' + Chr(13) + Chr(10) +
      Chr(13) + Chr(10) +
      'Presione SI para continuar la instalacion de todas formas,' + Chr(13) + Chr(10) +
      '(post_install.bat intentara configurar Python)' + Chr(13) + Chr(10) +
      'o NO para cancelar e instalar Python primero.',
      mbConfirmation, MB_YESNO) = IDNO then
    begin
      Result := False;
    end;
  end;
end;
