---
name: JullBrain-granite-embedder
description: >
  Skill para el módulo granite_embedder.py de JullBrain.
  Úsalo cuando necesites: depurar o extender el motor de embeddings semánticos,
  cambiar el backend (sentence-transformers / Ollama), ajustar el tamaño de lote
  o dispositivo de cómputo, integrar los chunks embebidos con RAGFlow,
  o diagnosticar errores de carga del modelo Granite Embedding R2.
  También aplica cuando el usuario mencione: vectores, embeddings, sentence-transformers,
  Ollama embeddings, granite-embedding-english-r2, o dimensiones del vector.
---

# Skill: JullBrain Granite Embedder

## Propósito

`granite_embedder.py` es el motor de embeddings semánticos del pipeline JullBrain.
Convierte los chunks de `hierarchical_chunks.json` en vectores numéricos de alta dimensión
usando el modelo **IBM Granite Embedding R2** (`ibm-granite/granite-embedding-english-r2`),
con soporte para dos backends: `sentence-transformers` (local Python) y `Ollama` (API REST).

---

## Arquitectura del Módulo

```
granite_embedder.py
│
├── load_embedding_config()          ← Lee pipeline_config.json
│
└── GraniteEmbedder (clase)
    ├── __init__(model, backend, device, batch_size, ollama_url)
    ├── _ensure_model()              ← Lazy loading del modelo
    ├── _load_st_model()             ← Backend sentence-transformers
    ├── _check_ollama_connection()   ← Backend Ollama
    │
    ├── embed_text(text) → list[float]
    ├── embed_chunks(chunks, text_field, progress_callback) → list[dict]
    ├── embed_chunks_file(input_path, output_path) → Path
    └── validate_model_health() → dict
```

---

## Parámetros de Configuración (`pipeline_config.json`)

| Clave | Tipo | Default | Descripción |
|---|---|---|---|
| `ragflow_embedding_model` | str | `ibm-granite/granite-embedding-english-r2` | Nombre del modelo (HF ID u Ollama name) |
| `embedding_backend` | str | `sentence-transformers` | Motor: `sentence-transformers` o `ollama` |
| `embedding_batch_size` | int | `32` | Chunks por lote en `embed_chunks()` |
| `embedding_device` | str | `cpu` | Dispositivo: `cpu`, `cuda`, `mps` |

---

## Formato de Salida (JSON)

Cada chunk en `hierarchical_chunks_embedded.json` tiene todos los campos originales
**más** los siguientes campos añadidos (principio de espejo documental — R7):

```json
{
  "content": "Artículo 1. La presente Ley...",
  "article_id": "art_001",
  "metadata": { ... },
  "embedding": [0.012345, -0.023456, ...],
  "embedding_model": "ibm-granite/granite-embedding-english-r2",
  "embedding_dim": 768
}
```

> **NUNCA** se modifica `content`, `article_id`, ni ningún campo de `metadata`.

---

## Modelo Activo: Granite Embedding R2

| Propiedad | Valor |
|---|---|
| HuggingFace ID | `ibm-granite/granite-embedding-english-r2` |
| Parámetros | 149M |
| Dimensión del Vector | 768 |
| Contexto Máximo | 8 192 tokens |
| Arquitectura | ModernBERT (Bi-encoder) |
| Licencia | Apache 2.0 |
| Generación | R2 (reemplaza al legado 30m R1) |

---

## Uso CLI

```bash
# Verificar salud del modelo
python granite_embedder.py --health

# Generar embedding para un texto
python granite_embedder.py --embed-text "Artículo 1. La presente Ley..."

# Embeber todos los chunks de un archivo
python granite_embedder.py --embed-file normativas_chunks/ley_xyz/hierarchical_chunks.json

# Usar backend Ollama
python granite_embedder.py --health --backend ollama
```

---

## Uso Python API

```python
from granite_embedder import GraniteEmbedder

# Instanciar (lee configuración de pipeline_config.json)
embedder = GraniteEmbedder()

# Embedding de texto puntual
vec = embedder.embed_text("Artículo 1. La presente Ley...")
print(f"Dimensión: {len(vec)}")  # 768

# Embeber archivo completo de chunks
out_path = embedder.embed_chunks_file(
    input_path="normativas_chunks/ley_xyz/hierarchical_chunks.json"
)
# Resultado: normativas_chunks/ley_xyz/hierarchical_chunks_embedded.json

# Verificar estado del modelo
health = embedder.validate_model_health()
# {"status": "ok", "model": "ibm-granite/...", "dim": 768, "load_time_s": 45.2, ...}
```

---

## Integración con RAGFlow

### Backend sentence-transformers
Los vectores se generan localmente y se guardan en `*_embedded.json`.
Para inyectarlos en RAGFlow, usa la API REST de ingesta de RAGFlow
con los campos `content` y `embedding` de cada chunk.

### Backend Ollama
```bash
ollama pull granite-embedding
# RAGFlow → Settings → Models → Add Model
# Type: Embedding | Base URL: http://localhost:11434/v1
# Model ID: granite-embedding
```

---

## Diagnóstico de Errores Comunes

| Error | Causa | Solución |
|---|---|---|
| `ImportError: sentence-transformers` | Librería no instalada | `pip install sentence-transformers>=3.0.0` |
| `ConnectionError: Ollama` | Ollama no está corriendo | `ollama serve` y verificar en `localhost:11434` |
| `FileNotFoundError: pipeline_config.json` | Config no encontrada | El módulo usa defaults, verificar ruta |
| Dimensión 384 en lugar de 768 | Modelo incorrecto (model small o 30m) | Verificar `ragflow_embedding_model` en config |
| `CUDA out of memory` | GPU sin capacidad suficiente | Cambiar `embedding_device` a `cpu` |
| `DLL load failed while importing hf_xet` | Windows bloquea la DLL de hf_xet por política de Control de Aplicaciones | **Desinstalar hf_xet del entorno virtual:** `pip uninstall hf_xet -y`. Esto fuerza a huggingface_hub a usar descarga HTTP estándar. ✅ **Verificado en producción (JullBrain v2, 2026-07)** |

---

## Notas de Diseño (R7 — Integridad Forense)

1. **Espejo documental**: `embed_chunks()` crea copias `dict(chunk)` — el original no se muta.
2. **Abstención explícita**: Si el modelo no carga, el error se propaga limpiamente; no hay silencio.
3. **Trazabilidad**: Cada chunk embebido registra `embedding_model` y `embedding_dim` para auditoría.
4. **Corpus cerrado**: El nombre del modelo viene de `pipeline_config.json`, nunca hardcodeado.
