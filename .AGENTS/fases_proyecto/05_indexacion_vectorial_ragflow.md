# Skill 05 — Indexación y Recuperación con RAGFlow

## 1. Rol responsable
**R1 (diseño de la estrategia de recuperación) + R2 (implementación/integración API)**.

## 2. Propósito
Generar representaciones vectoriales (embeddings) de los chunks producidos en la Skill 04 e indexarlos en RAGFlow, habilitando recuperación semántica híbrida (vectorial + palabras clave) con referencia exacta al folio o artículo de origen.

## 3. Entradas
- `chunks_expediente.json` y `chunks_normativa.json` (Skill 04).

## 4. Salidas
- Colecciones indexadas en RAGFlow (una por expediente + una para el corpus normativo versionado).
- Función de recuperación `retrieve(query, expediente_id, top_k)` que devuelve chunks con su metadato de origen intacto.

## 5. Dependencias tecnológicas
RAGFlow (API REST, despliegue local vía Docker), Granite Embedding (modelo de embeddings multilingüe), Python 3.11+.

## 6. Reglas obligatorias
1. El expediente y el corpus normativo se indexan en **colecciones separadas** — nunca se mezclan, porque tienen ciclos de actualización distintos (el expediente es estático una vez cargado; la normativa se versiona, ver Skill 06).
2. Toda recuperación debe devolver el metadato de origen (`folio_origen` o `articulo_origen`) junto con el texto — sin esto, la Skill 08 no puede verificar nada.
3. La recuperación híbrida (vectorial + keyword) es obligatoria, no opcional — la búsqueda solo vectorial pierde coincidencias exactas de número de artículo o de folio, críticas en contexto jurídico.

## 7. Implementación de referencia

```python
# skills/05_ragflow_indexado/indexado.py
import requests
import json
from pathlib import Path

RAGFLOW_API = "http://localhost:9380/api/v1"
API_KEY = "TU_API_KEY_LOCAL"  # nunca hardcodear en producción; usar variable de entorno

HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

def crear_coleccion(nombre: str) -> str:
    resp = requests.post(
        f"{RAGFLOW_API}/datasets",
        headers=HEADERS,
        json={"name": nombre, "embedding_model": "granite-embedding"},
    )
    resp.raise_for_status()
    return resp.json()["data"]["id"]

def indexar_chunks(dataset_id: str, chunks: list):
    """
    Sube chunks ya fragmentados (Skill 04) preservando metadato de origen.
    RAGFlow no debe re-fragmentar: el chunking ya se hizo con criterio jurídico.
    """
    documentos = []
    for chunk in chunks:
        documentos.append({
            "content": chunk["texto"],
            "metadata": {
                "chunk_id": chunk["chunk_id"],
                "folio_origen": chunk.get("folio_origen"),
                "articulo_origen": chunk.get("articulo_origen"),
                "tipo_acto": chunk.get("tipo_acto"),
                "orden_cronologico": chunk.get("orden_cronologico"),
            },
        })
    resp = requests.post(
        f"{RAGFLOW_API}/datasets/{dataset_id}/documents/bulk",
        headers=HEADERS,
        json={"documents": documentos, "chunking_method": "none"},  # ya viene fragmentado
    )
    resp.raise_for_status()
    return resp.json()

def retrieve(query: str, dataset_id: str, top_k: int = 8) -> list:
    resp = requests.post(
        f"{RAGFLOW_API}/retrieval",
        headers=HEADERS,
        json={"question": query, "dataset_ids": [dataset_id], "top_k": top_k, "hybrid_search": True},
    )
    resp.raise_for_status()
    resultados = resp.json()["data"]["chunks"]
    # Verificación mínima: todo resultado debe traer su metadato de origen
    for r in resultados:
        assert r["metadata"].get("folio_origen") or r["metadata"].get("articulo_origen"), \
            "Chunk recuperado sin referencia de origen — violación de trazabilidad"
    return resultados
```

## 8. Criterios de aceptación
- [ ] Colección de expediente y colección normativa verificablemente separadas.
- [ ] 100% de los resultados de `retrieve()` traen metadato de origen no nulo.
- [ ] Prueba de recuperación híbrida: una consulta por número de artículo exacto (p. ej. "artículo 236 COPP") recupera el chunk correcto en el top-3.

## 9. Relación con otras skills
Consume Skill 04. Es la capa que la Skill 07 (inferencia) consulta antes de generar cualquier respuesta.
