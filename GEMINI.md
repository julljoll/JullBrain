# 🧠 Instrucciones Maestras para Google Antigravity — JullBrain v0.2.0

Este repositorio está configurado y optimizado **exclusivamente para Google Antigravity** como único agente de ingeniería y orquestación.

## Reglas Arquitectónicas Esenciales
1. **Tecnología de IA Exclusiva IBM**:
   - Extracción documental: `IBM Docling` ejecutándose en **CPU** con detección automática de núcleos/hilos al iniciar [`orquestador_JullBrain.bat`](file:///c:/VS%20CODE/CODIGO/JullBrain/orquestador_JullBrain.bat).
   - Embeddings: `ibm-granite/granite-embedding-english-r2` (`768` dims) en [`granite_embedder.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/granite_embedder.py).
   - Inferencia LLM: `ibm-granite/granite-3.3-8b-instruct-GGUF` (Temperatura `0.0 - 0.1`).
   - Ciberseguridad Cognitiva: `ibm-granite/granite-guardian-3.2-5b` (6 dimensiones) en [`granite_guardian_guardrail.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/granite_guardian_guardrail.py).
2. **Núcleo Único de Información (`RAG/`)**:
   - Datos brutos: `RAG/datos_brutos/`
   - Salida Markdown + JSON Docling: `RAG/Informacion_docling_rag/`
   - Chunks jerárquicos enriquecidos: `RAG/normativas_chunks/`
   - Bóveda local criptográfica de modelos IA: `RAG/modelos_ia/` (`docling/`, `granite_embeddings/`, `granite_llm/`, `granite_guardian/`, `huggingface/`, `torch/`, `ollama/`)
   - Bases de datos locales: `RAG/notebooks_db/` y `RAG/lightrag_db/`
3. **Ejecución Local, Podman y Oracle Cloud**:
   - Ejecución local: exclusivamente mediante [`orquestador_JullBrain.bat`](file:///c:/VS%20CODE/CODIGO/JullBrain/orquestador_JullBrain.bat) sobre Python `3.12 - 3.14` (configurado por defecto en esta estación para `Python 3.14`).
   - Contenedores: nativamente en **Podman** (Windows y Linux Rootless) mediante [`Containerfile`](file:///c:/VS%20CODE/CODIGO/JullBrain/Containerfile) y [`podman-compose.yml`](file:///c:/VS%20CODE/CODIGO/JullBrain/podman-compose.yml).
   - Nube: únicamente **Oracle Cloud Infrastructure (OCI)** mediante [`deploy_oracle.sh`](file:///c:/VS%20CODE/CODIGO/JullBrain/deploy_oracle.sh) y [`oracle_config.json`](file:///c:/VS%20CODE/CODIGO/JullBrain/oracle_config.json).
   - Prohibido reintroducir Chocolatey, Streamlit, instaladores `.exe`/`.spec`, Google Colab, IBM Cloud Serverless o agentes de IA ajenos a Google Antigravity.

Consulta [`.agents/AGENTS.md`](file:///c:/VS%20CODE/CODIGO/JullBrain/.agents/AGENTS.md) y los skills en `.agents/skills/` para las directrices detalladas de cada módulo.
