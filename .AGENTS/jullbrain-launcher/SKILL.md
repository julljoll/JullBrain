---
name: JullBrain-launcher
description: >
  Skill para administrar, proteger y modificar la lógica visual y estructural del orquestador iniciar_conversion.bat.
  Úsalo siempre que el usuario pida: modificar el .bat, arreglar problemas de consola que se cierra automáticamente, 
  actualizar el menú de inicio en CMD, o problemas de ejecución de permisos de administrador al abrir la ventana.
compatibility:
  tools: [bash_tool, create_file, str_replace, view]
---

# JullBrain Launcher (`iniciar_conversion.bat`)

Este "Skill" existe para proteger la integridad del archivo `.bat` principal de JullBrain. Los agentes de IA frecuentemente corrompen este archivo al modificarlo (por problemas de codificación de Windows), lo que resulta en que la ventana de la consola parpadee y se cierre inmediatamente al ejecutarse.

## Reglas Críticas (Encoding y Saltos de Línea)
1. El archivo `iniciar_conversion.bat` **DEBE** guardarse estrictamente con codificación **UTF-8 SIN BOM** y saltos de línea **CRLF**.
2. **ACCIÓN OBLIGATORIA:** Cada vez que la IA utilice herramientas de edición de archivos (`write_to_file`, `replace_file_content`) sobre el archivo `.bat`, deberá ejecutar INMEDIATAMENTE este comando en PowerShell para reparar la codificación y evitar que el script quede inservible:

```powershell
$path = 'c:\VS CODE\CODIGO\JullBrain\iniciar_conversion.bat'
$content = Get-Content $path -Raw
$content = $content -replace "`r`n", "`n" -replace "`n", "`r`n"
$utf8NoBom = New-Object System.Text.UTF8Encoding $False
[System.IO.File]::WriteAllText($path, $content, $utf8NoBom)
```

## Estructura Lógica Obligatoria
Cualquier cambio futuro al script `.bat` debe mantener intactas estas 4 fases en este orden específico. Si se reescribe el script, NO OMITIR el arte ASCII ni los colores.

1. **Auto-Elevación de Privilegios**:
   Debe estar al inicio (después del setup de colores) para garantizar que el script pida permisos de Administrador antes de chocar con comandos prohibidos.
   ```bat
   net session >nul 2>&1
   if %errorlevel% neq 0 (
       powershell -Command "Start-Process '%~f0' -Verb RunAs"
       exit /b
   )
   ```

2. **Interfaz Gráfica (ASCII y Colores)**:
   Se deben declarar las variables de color usando `prompt #$H#$E#` (Ej: `%COLOR_H1%`, `%BG_COLOR%`, `%COLOR_TXT%`). El logo de "JullBrain" en arte ASCII de bloques (`██`) es obligatorio y debe imprimirse al inicio de cada ejecución.

3. **Verificación de Chocolatey y Docker**:
   Se debe comprobar si están instalados con `where choco` y `where docker`. 
   - Si Chocolatey no está, se usa un comando de PowerShell en el bloque para instalarlo.
   - Si Docker no está, se instala usando Chocolatey.
   - Si el motor no corre (verificando `docker info`), se detiene el script con `pause`.

4. **Ejecución del Pipeline en Docker Compose**:
   La carga final de todo el sistema se realiza lanzando la imagen construida (aislada):
   ```bat
   docker compose build jullbrain
   docker compose run --rm jullbrain
   ```

*(Fin de las directrices del Launcher)*
