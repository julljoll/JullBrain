$installDir = 'C:\Quibor'

Write-Host "====================================================================="
Write-Host "  Desinstalando QUIBOR - Eliminando archivos y accesos directos"
Write-Host "====================================================================="

# 1. Eliminar acceso directo del Escritorio
$desktopPath = [System.Environment]::GetFolderPath('Desktop')
$shortcutPath = Join-Path $desktopPath 'QUIBOR.lnk'

if (Test-Path $shortcutPath) {
    Write-Host "Eliminando acceso directo en el Escritorio..."
    Remove-Item $shortcutPath -Force -ErrorAction SilentlyContinue
}

# 2. Eliminar carpeta de instalación C:\Quibor
if (Test-Path $installDir) {
    Write-Host "Eliminando directorio de instalación: $installDir..."
    # Ejecutamos de forma recursiva y forzada para limpiar docling_env y datos
    Remove-Item $installDir -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "====================================================================="
Write-Host "  Desinstalación completada con éxito."
Write-Host "====================================================================="
