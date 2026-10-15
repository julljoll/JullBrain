# Guía de Contenerización y Operación con Podman — JullBrain Enterprise

Esta guía detalla los pasos para construir, exportar, transferir, importar y ejecutar el contenedor OCI de **JullBrain** en entornos **100% locales (air-gapped)** usando Podman.

---

## 🛠️ 1. Requisitos Previos

- **Podman CLI / Podman Desktop** instalado en el sistema.
  - Windows: [Podman Desktop para Windows](https://podman-desktop.io/)
  - Linux: Instalar `podman` desde el gestor de paquetes (`apt install podman` o `dnf install podman`).

---

## 🏗️ 2. Construcción de la Imagen OCI

El proceso detecta automáticamente el nombre del proyecto y construye una imagen optimizada multi-etapa ejecutándose sin privilegios de root (`appuser`).

### Windows:
```cmd
build_podman.bat
```

### Linux:
```bash
chmod +x build_podman.sh
./build_podman.sh
```

---

## 📦 3. Exportación a Paquete TAR Transportable

Genera un único archivo `.tar` portátil para trasladar la plataforma a otros equipos o servidores sin acceso a Internet.

### Windows:
```cmd
export_image.bat
```

### Linux:
```bash
chmod +x export_image.sh
./export_image.sh
```

*Resultado:* Se creará el paquete `jullbrain.tar` en el directorio raíz.

---

## 🚚 4. Transferencia e Importación en Otro Equipo

1. Copia el archivo `jullbrain.tar` (por pendrive, red local u otro medio seguro) a cualquier computadora que tenga Podman instalado.
2. Ejecuta el script de importación en la nueva máquina:

### Windows:
```cmd
import_image.bat
```

### Linux:
```bash
chmod +x import_image.sh
./import_image.sh
```

---

## 🚀 5. Ejecución del Contenedor e Interfaz Open WebUI

### Opción A: Stack Completo Enterprise (Open WebUI + OpenSearch + Postgres)
```bash
podman-compose -f compose.yaml up -d
```
- **Open WebUI (Interfaz Oficial de Usuario):** `http://localhost:8080`
- **JullBrain API Backend (FastAPI):** `http://localhost:8050`

### Opción B: Lanzar Contenedor Open WebUI Individual
```bash
podman run -d -p 8080:8080 --name open_webui -e OLLAMA_BASE_URL=http://host.containers.internal:11434 ghcr.io/open-webui/open-webui:main
```
Accede a la interfaz en `http://localhost:8080`.

---

## 🔄 6. Actualización de la Imagen

1. Realiza los cambios necesarios en el código fuente.
2. Reconstruye la imagen ejecutando `build_podman.bat` (Windows) o `./build_podman.sh` (Linux).
3. Exporta la nueva versión con `export_image.bat` o `./export_image.sh`.
