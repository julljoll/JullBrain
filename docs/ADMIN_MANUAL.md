# Manual de Administración y Operaciones — JullBrain V-2.0

---

## 🏛️ 1. Operación Local Nativa (100% Air-Gapped)

JullBrain V-2.0 opera nativamente en **Python 3.12** sin depender de contenedores (Docker/Podman) ni servicios en la nube. Todas las operaciones se ejecutan de manera aislada y autónoma en la estación de trabajo o servidor local.

### Inicio del Sistema

- **En Windows:**
  Doble clic en:
  ```cmd
  orquestador_JullBrain.bat
  ```
  Esto inicializará el entorno virtual `docling_env` y abrirá la **Interfaz Web HTML5** en:
  `http://localhost:8050`

- **En Linux / Servidor:**
  ```bash
  source docling_env/bin/activate
  python app.py
  ```

---

## 📤 2. Ingesta y Gestión de Normativas (`RAG/datos_brutos`)

Para incorporar leyes o sentencias al corpus:
1. Desde la **Interfaz Web**: pestaña *Carga de Normativas*, selecciona la categoría jurídica y sube el PDF. El navegador calcula automáticamente el hash SHA-256 para la cadena de custodia digital antes de guardar el archivo en `RAG/datos_brutos/<categoría>/`.
2. Desde **Consola / Explorador**: copia directamente los PDFs en `RAG/datos_brutos/<Categoría>/` (ej: `Penal`, `Civil`, `Informatica`).

---

## ☁️ 3. Operación en la Nube con Google Colab

Para procesar grandes volúmenes de documentos legales con aceleración GPU sin carga local:
1. Abre el cuaderno interactivo [`JullBrain_Colab.ipynb`](../JullBrain_Colab.ipynb) en Google Colab con el botón oficial.
2. Selecciona **GPU NVIDIA T4** en el entorno de ejecución.
3. Ejecuta las celdas para sincronizar con GitHub, procesar los PDFs mediante Docling, validar la jerarquía legal y generar los embeddings semánticos.

---

## 🔐 4. Auditoría, Integridad SHA-256 y Cadena de Custodia

JullBrain mantiene trazabilidad forense continua conforme al estándar **ISO/IEC 27037**:
- Cada expediente / cuaderno está sellado con un hash criptográfico **SHA-256 inmutable**. Si cualquier archivo es manipulado externamente, el sistema bloquea el acceso inmediatamente lanzando `NotebookIntegrityError`.
- Los eventos de creación, lectura, carga de documentos y consultas RAG quedan registrados en el log append-only [`audit_trail.jsonl`](../audit_trail.jsonl).

---

## 🧪 5. Verificación de Integridad del Sistema (QA Testing)

Para validar el funcionamiento del sistema en cualquier momento:
```bash
python -m unittest discover tests
```
Certifica en menos de 10 segundos las 24 pruebas críticas de jerarquía jurídica, algoritmos de búsqueda híbrida, guardrails anti-alucinación y aislamiento *air-gapped*.
