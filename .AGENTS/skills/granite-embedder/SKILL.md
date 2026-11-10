---
name: JullBrain-granite-embedder
description: Skill para el módulo granite_embedder.py de JullBrain en Google Antigravity. Úsalo cuando necesites depurar o extender el motor de embeddings semánticos con IBM Granite Embedding R2, gestionar la bóveda local RAG/modelos_ia/granite_embeddings, ajustar el tamaño de lote o dispositivo de cómputo, o verificar las dimensiones del vector (768 dims).
---

# 🧬 JullBrain — Motor de Embeddings Semánticos IBM Granite (`granite_embedder.py`)

Este skill administra [`granite_embedder.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/granite_embedder.py), el motor de vectorización semántica de **JullBrain v0.2.0** basado exclusivamente en **`ibm-granite/granite-embedding-english-r2`** (`768` dimensiones).

---

## 1. Bóveda Local de Modelos (`RAG/modelos_ia/granite_embeddings`)

Por ciberseguridad Zero-Trust y soporte *Air-Gapped* (tanto en ejecución local como en **Podman** y **Oracle Cloud**):
1. **Prioridad de Carga Local**:
   - `GraniteEmbedder` verifica primero si existen pesos locales (`model.safetensors` o `config.json`) en `RAG/modelos_ia/granite_embeddings`.
   - Si existen, carga el modelo 100% desde el disco local (`local_files_only=True`).
2. **Aprovisionamiento Inicial y Sellado `SHA-256`**:
   - Si la bóveda local aún está vacía y el entorno no está en modo `air_gapped_strict`, descarga `ibm-granite/granite-embedding-english-r2`, lo guarda de forma permanente en `RAG/modelos_ia/granite_embeddings` y sella toda la bóveda `RAG/modelos_ia/` mediante `seal_and_verify_model_vault()` en `vault_manifest_sha256.json`.
3. **Endurecimiento Criptográfico y Zero-Telemetry**:
   - Fuerza `HF_HUB_DISABLE_TELEMETRY=1`, `DO_NOT_TRACK=1` y `trust_remote_code=False` (prohibiendo la ejecución de código arbitrario desde repositorios externos).

---

## 2. Especificaciones Técnicas del Vector

| Parámetro | Valor en JullBrain v0.2.0 |
| :--- | :--- |
| **Modelo Oficial** | `ibm-granite/granite-embedding-english-r2` |
| **Dimensión Vectorial** | `768` (`float32` normalizado L2) |
| **Bóveda Local** | `RAG/modelos_ia/granite_embeddings` |
| **Backend Principal** | `sentence_transformers` (con fallback a `ollama`) |
| **Formato de Salida** | Campo `embedding` + `embedding_model` + `embedding_dim` en `RAG/normativas_chunks/*_chunks.json` |

---

## 3. Comandos de Diagnóstico y Prueba

```powershell
# Diagnóstico del motor Granite Embedding R2 y verificación de la bóveda local
python granite_embedder.py

# Ejecutar pruebas unitarias del embedder
python -m unittest tests/test_core_pipeline.py
```
