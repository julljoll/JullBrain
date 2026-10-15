# Manual de Administración y Operaciones — JullBrain Enterprise

---

## 🐋 1. Operación de Contenedores con Podman

JullBrain está diseñado para operar nativamente en entornos **Podman Rootless** sin depender de Docker ni servicios en la nube.

### Construcción de la Imagen OCI

- **Windows:**
  ```cmd
  build_podman.bat
  ```
- **Linux:**
  ```bash
  chmod +x build_podman.sh
  ./build_podman.sh
  ```

---

## 📦 2. Exportación e Importación de Imágenes Air-Gapped

Para trasladar el sistema a un equipo o servidor sin conexión a Internet:

### Exportar en el Equipo de Origen:
- **Windows:** Ejecutar `export_image.bat`
- **Linux:** Ejecutar `./export_image.sh`
- *Resultado:* Se generará el archivo único portátil `jullbrain.tar`.

### Importar en el Equipo de Destino:
1. Copia el archivo `jullbrain.tar` al nuevo equipo.
2. Ejecuta el script de importación:
   - **Windows:** `import_image.bat`
   - **Linux:** `./import_image.sh`

---

## 🚀 3. Orquestación Completa con Podman Compose

Para lanzar el stack completo (JullBrain API, Open WebUI, OpenSearch y PostgreSQL + pgvector):

```bash
podman-compose -f compose.yaml up -d
```

### Puertos Expuestos:
- **`8050`:** JullBrain Administrative Dashboard
- **`3000`:** Interfaz de usuario Open WebUI
- **`9200`:** Motor de búsqueda OpenSearch
- **`5432`:** Base de datos PostgreSQL + pgvector

---

## 🔐 4. Auditoría e Inspección de Seguridad

Para auditar la cadena de custodia y la verificación de firmas SHA-256:
- Revisa el registro de auditoría en la base de datos PostgreSQL (`audit_logs`) o en el archivo append-only local [`audit_trail.jsonl`](file:///c:/VS%20CODE/CODIGO/JullBrain/audit_trail.jsonl).
