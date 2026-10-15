# JullBrain Enterprise — Legal Document Intelligence Platform

> **Plataforma Enterprise de Inteligencia Documental Legal estilo NotebookLM especializada en departamentos jurídicos, cumplimiento normativo, auditoría y gobierno corporativo. Operación 100% LOCAL (air-gapped), impulsada por IBM Granite 3.3 8B, IBM Docling, Open WebUI, OpenSearch y PostgreSQL + pgvector.**

[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue)](https://python.org) [![Licencia Apache 2.0](https://img.shields.io/badge/Licencia-Apache%202.0-blue.svg)](LICENSE) [![Podman Desktop](https://img.shields.io/badge/Podman-Rootless%20OCI-purple)](https://podman-desktop.io) [![IBM Granite](https://img.shields.io/badge/IBM-Granite%203.3%208B-blue)](https://huggingface.co/ibm-granite) [![Open WebUI](https://img.shields.io/badge/UI-Open%20WebUI-green)](https://github.com/open-webui/open-webui)

---

## 🏛️ Descripción General

**JullBrain Enterprise** transforma documentos complejos (contratos, reglamentos, gacetas oficiales, normas ISO, expedientes judiciales) en una base de conocimiento activa sin alucinaciones.

### 🌟 Pilares de la Arquitectura Enterprise:
1. **Inferencia 100% Local (CPU Optimized):** Inferencia con `ibm-granite/granite-3.3-8b-instruct-GGUF` calibrada para servidores con 16 GB o 32 GB RAM.
2. **Componentes Oficiales IBM:** Extracción con IBM Docling + DocTags, Embeddings con IBM Granite Embedding 311M Multilingual R2, Guardrails con IBM Granite Guardian y IBM Prompt Templates.
3. **Interfaz Oficial (Open WebUI):** Chat documental, workspaces, notebooks y colaboración impulsados por Open WebUI vía API REST de Pipelines.
4. **Búsqueda Híbrida OpenSearch:** Motor léxico BM25 + k-NN Vectorial + Fusión Recíproca de Rangos (RRF) + Cross-Encoder Reranker.
5. **Cuadernos Independientes (Expedientes):** Firma criptográfica inmutable **SHA-256** por expediente y borrado transaccional con rollback.
6. **Reglas RAG Estrictas Cero Alucinación:** `temperature=0.0`, citas obligatorias estructuradas y aviso automático de falta de evidencia o contradicciones normativas.
7. **Contenerización Podman Multi-Etapa:** Scripts automáticos de compilación, exportación e importación `.bat` (Windows) y `.sh` (Linux) para despliegue en entornos *air-gapped*.

---

## 🛠️ Estructura Completa del Proyecto

```text
JullBrain/
├── app.py                         # Dashboard administrativo Plotly Dash + Flask + DBC
├── convert_normativas.py          # Ingesta documental con IBM Docling (PDF, DOCX, PPTX, XLSX, TXT, CSV, HTML, MD, EPUB, imágenes)
├── legalizer.py                   # Chunking jerárquico legal y detección regex de artículos
├── metadata_extractor.py         # Extracción de YAML Frontmatter y hash SHA-256
├── validator.py                   # Validación cruzada PDF vs Markdown e indicador de confianza
├── granite_embedder.py            # Generación de embeddings con IBM Granite Embedding R2
├── granite_guardian_guardrail.py # Guardrails de seguridad IBM Granite Guardian
├── opensearch_indexer.py         # Motor de búsqueda híbrida BM25 + Vector + RRF + Reranker
├── notebook_manager.py            # Gestor de Cuadernos/Expedientes con SHA-256 y Rollback
├── audit_logger.py                # Registro de auditoría inmutable (RBAC, JWT, UTC, IP)
├── openwebui_pipeline.py          # Pipeline de integración con Open WebUI API
├── db_schema.sql                  # Esquema relacional y vectorial PostgreSQL + pgvector
├── pipeline_config.json           # Configuración técnica persistente del sistema
├── requirements.txt               # Dependencias Python de producción
├── Dockerfile / Containerfile     # Multi-stage build OCI optimizado para Podman
├── compose.yaml                   # Orquestación Podman Compose (Open WebUI, OpenSearch, Postgres, JullBrain API)
├── podman-compose.yml             # Alias de compatibilidad Podman Compose
├── build_podman.bat / .sh         # Script de construcción automática (Windows / Linux)
├── export_image.bat / .sh         # Script de exportación a .tar (Windows / Linux)
├── import_image.bat / .sh         # Script de importación desde .tar (Windows / Linux)
├── tests/                         # Suite de pruebas unitarias e integración
└── docs/                          # Documentación Técnica, Manuales de Usuario/Admin y UML
```

---

## 🚀 Guía Rápida de Despliegue con Podman

### 1. Construir la Imagen OCI

- **Windows:** Ejecutar `build_podman.bat`
- **Linux:** Ejecutar `./build_podman.sh`

### 2. Exportar la Imagen Portátil (Air-Gapped)

- **Windows:** Ejecutar `export_image.bat`
- **Linux:** Ejecutar `./export_image.sh`
*Resultado:* Genera el archivo único `jullbrain.tar`.

### 3. Importar en Otro Equipo

- **Windows:** Ejecutar `import_image.bat`
- **Linux:** Ejecutar `./import_image.sh`

### 4. Lanzar el Stack Enterprise Completo

```bash
podman-compose -f compose.yaml up -d
```
- **Open WebUI (Interfaz de Usuario):** `http://localhost:3000`
- **Plotly Dash (Dashboard Administrativo):** `http://localhost:8050`

---

## 📚 Documentación y Manuales

- [Manual Técnico](docs/TECHNICAL_MANUAL.md)
- [Manual de Usuario](docs/USER_MANUAL.md)
- [Manual de Administración](docs/ADMIN_MANUAL.md)
- [Diagramas UML y Arquitectura](docs/UML_DIAGRAMS.md)
- [Registro de Cambios (Changelog)](docs/CHANGELOG.md)
- [Guía Detallada de Podman](README_PODMAN.md)
