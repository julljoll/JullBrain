# Registro de Cambios (Changelog) — JullBrain Enterprise

## [2.0.0-Enterprise] - 2026-07-31

### 🚀 Nuevas Características Enterprise
- **Integración con Open WebUI:** Configuración oficial como interfaz web del sistema mediante pipelines de API (`openwebui_pipeline.py`).
- **Standard de IA IBM Granite:** Adopción obligatoria del modelo LLM `ibm-granite/granite-3.3-8b-instruct-GGUF` con parámetros de inferencia ultra-precisos (`temp=0.0`, `top_p=0.05`, `top_k=20`, `repeat_penalty=1.15`).
- **Motor de Búsqueda Híbrida OpenSearch (`opensearch_indexer.py`):** Combinación de búsqueda léxica BM25, k-NN vectorial, Fusión Recíproca de Rangos (RRF) y Cross-Encoder Reranker.
- **Cuadernos Independientes NotebookLM (`notebook_manager.py`):** Firma criptográfica **SHA-256** por expediente y borrado transaccional con rollback.
- **Base de Datos PostgreSQL + pgvector (`db_schema.sql`):** Persistencia de expedientes, documentos, vectores y auditoría.
- **Auditoría Inmutable (`audit_logger.py`):** Firmas SHA-256 en logs de eventos con timestamps UTC e IP.
- **Contenerización OCI Multi-Etapa Podman:** `Containerfile`, `compose.yaml` y scripts `.bat` (Windows) y `.sh` (Linux) para construir, exportar `.tar` e importar en redes air-gapped.
- **Suite de Pruebas Automatizadas:** `tests/test_unit.py` y `tests/test_integration.py`.

### 🛡️ Mejoras de Seguridad y Rendimiento
- Ejecución en contenedor bajo usuario no-root `appuser` (UID 1000).
- Despliegue 100% local sin llamadas a Internet ni APIs externas.
- Inferencia optimizada para CPU (16 GB / 32 GB RAM).
