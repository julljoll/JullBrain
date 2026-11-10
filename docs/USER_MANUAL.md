# Manual de Usuario — JullBrain v0.2.0 (Plataforma Legal-RAG con Tecnología IBM)

---

## 🚀 Introducción

Bienvenido a **JullBrain v0.2.0**, el sistema soberano de Inteligencia Documental Jurídica e Informática Forense impulsado exclusivamente por tecnología de IA de **IBM** (`IBM Docling`, `IBM Granite 3.3 8B`, `IBM Granite Embedding R2` e `IBM Granite Guardian 3.2/3.3`).

---

## 💻 1. Acceso al Sistema

### 1. Consola Interactiva TUI (Ejecución Local Recomendada)
- **Inicio:** Ejecuta [`orquestador_JullBrain.bat`](file:///c:/VS%20CODE/CODIGO/JullBrain/orquestador_JullBrain.bat).
- **Funciones del Menú Principal (`orquestador.py`):**
  1. Conversión de normativas PDF/Word en `RAG/datos_brutos/` con `IBM Docling` en CPU.
  2. Generación de embeddings semánticos `IBM Granite Embedding R2` (`768` dims) en `RAG/normativas_chunks/`.
  3. Validación cruzada de calidad (`validator.py`) y auditoría de integridad de la bóveda `RAG/modelos_ia/`.
  4. Ejecución de la suite de pruebas QA y ciberseguridad (`tests/`).

### 2. Servidor Web & API Zero-Trust (`app.py`)
- **URL Local:** `http://localhost:8050` (o `http://localhost:8080` en **Podman** / **Oracle Cloud**)
- **Uso:** Estado del nodo, subida verificada de PDFs con validación `%PDF-` y `SHA-256`, gestión de expedientes y consultas RAG.

### 3. Interfaz de Chat Documental (Open WebUI Pipeline)
- **Conector:** [`openwebui_pipeline.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/openwebui_pipeline.py)
- **Uso:** Consultas jurídicas conversacionales ancladas a los cuadernos de `RAG/notebooks_db/`.

---

## 📁 2. Gestión de Cuadernos / Expedientes (`RAG/notebooks_db/`)

1. Cada expediente creado recibe automáticamente una firma criptográfica **SHA-256 inmutable** conforme a **ISO/IEC 27037**.
2. Al subir un documento PDF mediante `/api/v1/upload` o colocarlo en `RAG/datos_brutos/`, el sistema verifica sus *magic bytes* (`%PDF-`) y calcula su huella `SHA-256`.
3. Si un expediente es alterado externamente en disco, el sistema bloquea su lectura inmediatamente (`NotebookIntegrityError`) y registra la alerta en `logs/audit_forensic.jsonl`.

---

## 🔍 3. Reglas de Consulta Jurídica y Ciberseguridad IBM Granite Guardian

Todas las consultas pasan por el guardrail de 6 dimensiones **IBM Granite Guardian**:

- **Protección de Datos Personales (PII Venezolano):** Detecta y protege números de Cédula (`V-/E-`), `RIF`, teléfonos y correos electrónicos.
- **Defensa contra Inyección de Instrucciones:** Bloquea cualquier intento de ignorar las reglas procesales o fabricar artículos inexistentes.
- **Garantía Cero Alucinación y Abstención Explícita:** El sistema responde **únicamente** con evidencia contenida en `RAG/normativas_chunks/`. Si no existe respaldo documental, responde exactamente:
  > *"No encontré evidencia suficiente en los documentos cargados para responder esta pregunta."*
- **Citas Legales Verificadas (`Groundedness`):** Cada respuesta incluye Documento, Página, Capítulo, Artículo, Fragmento Literal y Nivel de Confianza (%).
