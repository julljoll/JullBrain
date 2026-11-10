# Manual de Administración y Operaciones — JullBrain v0.2.0

> **Stack IA:** Exclusivamente **IBM** (`IBM Docling` en CPU · `IBM Granite 3.3 8B` · `IBM Granite Embedding R2` · `IBM Granite Guardian 3.2/3.3`)
> **Agente de Ingeniería:** Exclusivamente **Google Antigravity**
> **Entornos Soportados:** Ejecución Local (`orquestador_JullBrain.bat`), Contenedores Nativos **Podman** (Windows / Linux Rootless) y **Oracle Cloud Infrastructure (OCI)**

---

## 🏛️ 1. Operación Local Nativa (100% Air-Gapped Ready)

JullBrain v0.2.0 se ejecuta localmente sobre **Python 3.12 – 3.14 (64-bit)** (configurado por defecto para **Python 3.14**) mediante un único punto de entrada que analiza el hardware del equipo anfitrión.

### Inicio del Sistema en Windows
Ejecuta con doble clic o desde terminal:
```cmd
orquestador_JullBrain.bat
```
Al iniciar, `orquestador_JullBrain.bat` realiza automáticamente:
1. **Análisis de Computadora Host (`gpu_detector.py`):** Detecta núcleos físicos y lógicos del procesador y asigna los hilos óptimos para `IBM Docling` en CPU (`OMP_NUM_THREADS`, `MKL_NUM_THREADS`), verifica la memoria RAM libre y comprueba la disponibilidad de **Podman**.
2. **Inicialización del Núcleo `RAG/` y Bóveda `RAG/modelos_ia/`:** Verifica las carpetas de datos y desactiva toda telemetría externa (`HF_HUB_DISABLE_TELEMETRY=1`, `DO_NOT_TRACK=1`).
3. **Autodiagnóstico del Entorno `docling_env`:** Verifica e instala las dependencias de [`requirements.txt`](file:///c:/VS%20CODE/CODIGO/JullBrain/requirements.txt) sobre Python 3.14/3.12 y lanza la consola interactiva [`orquestador.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/orquestador.py) o el servidor web Zero-Trust [`app.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/app.py).

### Aprovisionamiento y Sellado de Modelos IA Locales (`RAG/modelos_ia/`)
Para descargar los modelos de `IBM Docling` e `IBM Granite Embedding R2` en la bóveda local y sellarlos con `SHA-256` antes de pasar a operación *Air-Gapped*:
```powershell
.\docling_env\Scripts\python.exe convert_normativas.py --bootstrap-models
```

---

## 📤 2. Ingesta y Gestión del Núcleo de Información (`RAG/`)

Toda la información del sistema reside dentro de la carpeta `RAG/`:
- **`RAG/datos_brutos/`:** Coloca aquí los PDFs de leyes, códigos o Gacetas Oficiales organizados por materia (p. ej. `Penal`, `Civil`, `Constitucional`, `Formatos_Word`). Antes de procesarlos, el sistema valida su firma binaria (`%PDF-`) y calcula su hash `SHA-256`.
- **`RAG/Informacion_docling_rag/`:** Almacena los archivos `.md` estructurados (con Encabezado Canónico y YAML Frontmatter) y los `.json` generados por `IBM Docling`.
- **`RAG/normativas_chunks/`:** Almacena los chunks jerárquicos por artículo enriquecidos con vectores de `768` dimensiones (`ibm-granite/granite-embedding-english-r2`).
- **`RAG/modelos_ia/`:** Bóveda local criptográfica de todos los modelos IA (`docling/`, `granite_embeddings/`, `granite_llm/`, `granite_guardian/`, `huggingface/`, `torch/`, `ollama/`) protegida por `vault_manifest_sha256.json`.

---

## 📦 3. Ejecución Nativa en Podman (Windows y Linux Rootless)

JullBrain está configurado nativamente para correr en **Podman** sin privilegios de root (`--security-opt=no-new-privileges`, `--userns=keep-id`):

```bash
# 1. Construir la imagen desde el Containerfile oficial
podman build -f Containerfile -t localhost/jullbrain-ibm:0.2.0 .

# 2. Desplegar el enclave completo (Core + Ollama con modelos en ./RAG/modelos_ia)
podman compose -f podman-compose.yml up -d
```

---

## ☁️ 4. Despliegue en la Nube: Exclusivamente Oracle Cloud (OCI)

La única nube autorizada para el proyecto es **Oracle Cloud Infrastructure (OCI)**, utilizando **Podman** nativo y manteniendo todos los modelos de IA guardados localmente en `/opt/jullbrain/RAG/modelos_ia`:

```bash
bash deploy_oracle.sh
```
La configuración de perfiles Ampere A1 (ARM64) y GPU A10 se gestiona en [`oracle_config.json`](file:///c:/VS%20CODE/CODIGO/JullBrain/oracle_config.json).

---

## 🔐 5. Auditoría Forense `HMAC-SHA256`, Guardrails y Pruebas QA

1. **Cadena de Custodia Criptográfica ([`audit_logger.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/audit_logger.py)):**
   - Todos los eventos quedan firmados en `logs/audit_forensic.jsonl` mediante *hash-chaining* `HMAC-SHA256` (`prev_hash` + `hmac_sha256`) conforme a **ISO/IEC 27037** y **NIST AI RMF**.
2. **Guardrails Cognitivos 6D ([`granite_guardian_guardrail.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/granite_guardian_guardrail.py)):**
   - Filtra Prompt Injection/Jailbreak, contenido HAP, datos personales venezolanos (`Cédula V-/E-`, `RIF`, teléfonos, correos) y verifica el anclaje documental (`Groundedness`).
3. **Suite de Verificación QA (`27` Pruebas Automatizadas):**
   ```powershell
   .\docling_env\Scripts\python.exe -m unittest discover tests -v
   ```
