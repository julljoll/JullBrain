$packageName = 'quibor'
$installDir = 'C:\Quibor'
$zipUrl = 'https://github.com/julljoll/IBM-DOCLING/archive/refs/heads/main.zip'

Write-Host "====================================================================="
Write-Host "  Instalando QUIBOR V-1.0 - Sistema RAG de Normativas Legales"
Write-Host "====================================================================="

# 1. Crear directorio temporal
$tempDir = Join-Path $env:TEMP 'quibor-install'
if (Test-Path $tempDir) {
    Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
}
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
$zipPath = Join-Path $tempDir 'quibor.zip'

# 2. Descargar el archivo ZIP desde GitHub
Write-Host "[1/5] Descargando el código fuente desde el repositorio en GitHub..."
try {
    Get-ChocolateyWebFile -PackageName $packageName -FileFullPath $zipPath -Url $zipUrl
} catch {
    Write-Warning "No se pudo descargar el archivo ZIP. Asegúrese de que la URL en el script de Chocolatey es válida:"
    Write-Warning $zipUrl
    throw $_
}

# 3. Extraer el archivo ZIP en la carpeta temporal
Write-Host "[2/5] Extrayendo archivos temporales..."
Get-ChocolateyUnzip -FileFullPath $zipPath -Destination $tempDir

# 4. Mover archivos a la ubicación final C:\Quibor
Write-Host "[3/5] Instalando archivos en la ruta de destino ($installDir)..."
# Los ZIP de GitHub contienen una carpeta raíz (por ejemplo, 'IBM-DOCLING-main')
$extractedSubDir = Get-ChildItem -Path $tempDir -Directory | Select-Object -First 1

if ($extractedSubDir) {
    if (Test-Path $installDir) {
        Write-Host "Detectada instalación previa. Limpiando directorio de destino..."
        # Evitar eliminar archivos de datos del usuario si existen, pero aquí hacemos una instalación limpia
        Remove-Item $installDir -Recurse -Force -ErrorAction SilentlyContinue
    }
    New-Item -ItemType Directory -Force -Path $installDir | Out-Null
    
    # Copiar recursivamente
    Copy-Item -Path "$($extractedSubDir.FullName)\*" -Destination $installDir -Recurse -Force
} else {
    throw "Error: No se pudo identificar la carpeta raíz extraída del archivo ZIP de GitHub."
}

# 5. Limpieza de archivos temporales de descarga
Write-Host "[4/5] Limpiando archivos temporales..."
Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue

# 6. Crear acceso directo en el Escritorio con el icono circular amarillo
Write-Host "[5/5] Creando acceso directo en el Escritorio con icono personalizado..."
$desktopPath = [System.Environment]::GetFolderPath('Desktop')
$shortcutPath = Join-Path $desktopPath 'QUIBOR.lnk'

try {
    $wshShell = New-Object -ComObject WScript.Shell
    $shortcut = $wshShell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = "$installDir\iniciar_conversion.bat"
    $shortcut.WorkingDirectory = $installDir
    
    # El archivo .ico ya se incluye en la raíz del repositorio descargado
    $iconPath = "$installDir\quibor.ico"
    if (Test-Path $iconPath) {
        $shortcut.IconLocation = $iconPath
    } else {
        Write-Warning "El archivo de icono quibor.ico no se encontró en la carpeta de instalación."
    }
    
    $shortcut.Save()
    Write-Host "[OK] Acceso directo 'QUIBOR' creado en el Escritorio."
} catch {
    Write-Warning "No se pudo crear el acceso directo en el Escritorio: $_"
}

Write-Host "====================================================================="
Write-Host "  Instalación completada con éxito en: $installDir"
Write-Host "  La primera ejecución configurará el entorno virtual 'docling_env'."
Write-Host "====================================================================="
