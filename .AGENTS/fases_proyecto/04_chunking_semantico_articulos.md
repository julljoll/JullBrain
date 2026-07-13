# Skill 04 — Chunking Jurídico Atómico

## 1. Rol responsable
**R1 — Arquitecto/a de IA y LLM Senior**.

## 2. Propósito
Fragmentar el expediente ya estructurado y ordenado (Skill 03) y el corpus normativo (Skill 06) en unidades semánticas ("chunks") que respeten las unidades procesales y normativas naturales — nunca mezclando más de un artículo de ley o más de un acto procesal por chunk. Este es el principio de **chunking atómico a nivel de artículo** que sostiene toda la trazabilidad posterior.

## 3. Entradas
- `linea_cronologica.json` (Skill 03) para el expediente.
- Corpus normativo estructurado (Skill 06) para las normas.

## 4. Salidas
- `chunks_expediente.json` y `chunks_normativa.json`, cada chunk con: `chunk_id`, `texto`, `folio_origen` o `articulo_origen`, `tipo_acto` o `norma_fuente`, `orden_cronologico` (si aplica).

## 5. Dependencias tecnológicas
Python 3.11+. No requiere modelo de lenguaje — es una etapa determinística, no generativa.

## 6. Reglas obligatorias
1. **Un chunk, una unidad.** Un chunk del expediente no cruza dos actos procesales distintos. Un chunk normativo no cruza dos artículos distintos.
2. Tamaño de chunk gobernado por unidad lógica, no por conteo fijo de tokens — un artículo corto es un chunk corto; uno largo se subdivide por incisos, nunca a mitad de oración.
3. Cada chunk conserva referencia exacta y verificable a su origen (folio o número de artículo) — sin esto, la Skill 08 no puede funcionar.

## 7. Implementación de referencia

```python
# skills/04_chunking_juridico/chunking.py
import json
import re
from pathlib import Path

def chunk_expediente(expediente_id: str, data_dir: str = "data/structured"):
    path = Path(data_dir) / expediente_id / "linea_cronologica.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    chunks = []
    for el in data["elementos_ordenados"]:
        # Un elemento cronológico ya representa una unidad procesal (Skill 03);
        # aquí solo se valida que no deba subdividirse por longitud excesiva.
        chunks.append({
            "chunk_id": f"{expediente_id}-{el['elemento_id']}",
            "texto": el["texto"],
            "folio_origen": el["folio_origen"],
            "tipo_acto": el["tipo_acto"],
            "orden_cronologico": el["orden_cronologico"],
        })

    out_path = Path(data_dir) / expediente_id / "chunks_expediente.json"
    out_path.write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")
    return chunks

PATRON_ARTICULO = re.compile(r"(Art[íi]culo\s+\d+[°º]?\.?)", re.IGNORECASE)

def chunk_normativa(texto_norma: str, fuente: str) -> list:
    """
    Divide un texto normativo en chunks atómicos por artículo.
    Nunca produce un chunk que abarque más de un artículo.
    """
    partes = PATRON_ARTICULO.split(texto_norma)
    chunks = []
    articulo_actual = None
    buffer = ""

    for parte in partes:
        if PATRON_ARTICULO.match(parte):
            if articulo_actual and buffer.strip():
                chunks.append({
                    "chunk_id": f"{fuente}-{articulo_actual}",
                    "texto": buffer.strip(),
                    "articulo_origen": articulo_actual,
                    "norma_fuente": fuente,
                })
            articulo_actual = parte.strip()
            buffer = ""
        else:
            buffer += parte

    if articulo_actual and buffer.strip():
        chunks.append({
            "chunk_id": f"{fuente}-{articulo_actual}",
            "texto": buffer.strip(),
            "articulo_origen": articulo_actual,
            "norma_fuente": fuente,
        })

    return chunks
```

## 8. Criterios de aceptación
- [ ] Prueba manual sobre al menos 10 artículos del COPP: ningún chunk contiene texto de dos artículos.
- [ ] Todo chunk del expediente conserva `folio_origen` y `orden_cronologico`.
- [ ] Ningún chunk queda sin `chunk_id` único.

## 9. Relación con otras skills
Entrada directa de la Skill 05 (indexación vectorial). Su granularidad determina la precisión de la Skill 08 (trazabilidad de citas).
