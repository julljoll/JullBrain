---
name: JullBrain-controlador-iniciador-bat
description: >
  Skill para administrar, proteger y modificar la lógica visual y estructural del orquestador orquestador_JullBrain.bat.
  Úsalo siempre que el usuario pida: modificar el .bat, arreglar problemas de consola que se cierra automáticamente, 
  actualizar el menú de inicio en CMD, o problemas de ejecución de permisos de administrador al abrir la ventana.
compatibility:
  tools: [bash_tool, create_file, str_replace, view]
---

# JullBrain Launcher (`orquestador_JullBrain.bat`)

Este "Skill" existe para proteger la integridad del archivo `.bat` principal de JullBrain. Los agentes de IA frecuentemente corrompen este archivo al modificarlo (por problemas de codificación de Windows), lo que resulta en que la ventana de la consola parpadee y se cierre inmediatamente al ejecutarse.

## Reglas Críticas (Encoding y Saltos de Línea)
1. El archivo `orquestador_JullBrain.bat` **DEBE** guardarse estrictamente con codificación **UTF-8 SIN BOM** y saltos de línea **CRLF**.
2. **ACCIÓN OBLIGATORIA:** Cada vez que la IA utilice herramientas de edición de archivos (`write_to_file`, `replace_file_content`) sobre el archivo `.bat`, deberá ejecutar INMEDIATAMENTE este comando en PowerShell para reparar la codificación y evitar que el script quede inservible:

```powershell
$path = 'c:\VS CODE\CODIGO\JullBrain\orquestador_JullBrain.bat'
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

3. **Verificación de Python y Entorno Virtual**:
   Se debe comprobar si existe la carpeta del entorno virtual `docling_env` local y su intérprete `python.exe`.
   - Si no existe el venv, se comprueba la presencia de Python global con `where python`. Si está presente, se crea el entorno con `python -m venv docling_env`.
   - Si Python global no se encuentra, se muestra un mensaje de error solicitando su instalación.

4. **Instalación de Dependencias y Ejecución del Pipeline**:
   Se activa el entorno virtual y se instalan las dependencias usando `pip install -r requirements.txt`. Finalmente se ejecuta el orquestador principal:
   ```bat
   python convert_normativas.py
   ```

*(Fin de las directrices del Launcher)*
