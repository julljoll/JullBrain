# Skill 06 — Carga y Versionado del Corpus Normativo

## 1. Rol responsable
**R1 (arquitectura de versionado) + R3 (curaduría normativa: qué normas, qué versión, qué vigencia)**.

## 2. Propósito
Mantener el corpus normativo (COPP y leyes conexas) como un conjunto **cerrado y versionado** que alimenta la Skill 05, distinto y desacoplado de los expedientes individuales, con control explícito de qué versión de qué norma está vigente en el sistema en un momento dado.

## 3. Entradas
- Texto oficial de las normas a cargar (COPP, LOCTI, Ley de Infogobierno, Ley Especial contra los Delitos Informáticos).
- Fecha de vigencia / última reforma de cada norma.

## 4. Salidas
- `corpus_normativo_vX.json`: manifiesto versionado de normas cargadas, con hash de contenido por norma.
- Chunks normativos indexados (vía Skill 04 + 05) etiquetados con `version_corpus`.

## 5. Dependencias tecnológicas
Python 3.11+ (hashlib para control de integridad), RAGFlow (Skill 05).

## 6. Reglas obligatorias
1. **Corpus cerrado:** el sistema en producción no navega ni consulta fuentes normativas externas en tiempo real — solo lo cargado y versionado explícitamente. Cualquier actualización es un evento auditado, no automático.
2. Cada versión del corpus tiene un identificador único e inmutable (`version_corpus`); no se sobrescribe una versión existente, se publica una nueva.
3. Toda cita generada por el sistema (Skill 07/08) debe poder trazarse a una `version_corpus` específica — esto es lo que permite defender ante un jurado o auditoría qué versión de la ley se usó para un caso dado.
4. Ninguna norma se carga sin verificación de fuente oficial por R3 — no se acepta texto normativo de fuentes no oficiales.

## 7. Implementación de referencia

```python
# skills/06_normativa_rag/versionado.py
import hashlib
import json
from datetime import date
from pathlib import Path

def generar_manifiesto_corpus(normas: list, version_corpus: str, output_dir: str = "data/normativa"):
    """
    normas: lista de dicts {"nombre": str, "texto": str, "fecha_vigencia": str, "fuente_oficial": str}
    """
    manifiesto = {
        "version_corpus": version_corpus,
        "fecha_publicacion": date.today().isoformat(),
        "normas": [],
    }

    for norma in normas:
        hash_contenido = hashlib.sha256(norma["texto"].encode("utf-8")).hexdigest()
        manifiesto["normas"].append({
            "nombre": norma["nombre"],
            "fecha_vigencia": norma["fecha_vigencia"],
            "fuente_oficial": norma["fuente_oficial"],
            "hash_sha256": hash_contenido,
        })

    out_path = Path(output_dir) / f"corpus_normativo_{version_corpus}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(manifiesto, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifiesto

def verificar_integridad(norma_texto: str, hash_esperado: str) -> bool:
    """Verifica que el texto normativo indexado no haya sido alterado respecto al manifiesto."""
    return hashlib.sha256(norma_texto.encode("utf-8")).hexdigest() == hash_esperado
```

## 8. Criterios de aceptación
- [ ] Manifiesto de corpus generado y verificable por hash para cada versión publicada.
- [ ] Ninguna norma cargada sin `fuente_oficial` registrada.
- [ ] Prueba: alterar un carácter de una norma indexada y confirmar que `verificar_integridad()` lo detecta.

## 9. Relación con otras skills
Alimenta la Skill 04 (chunking normativo) y la Skill 05 (indexación). La `version_corpus` se propaga hasta la Skill 08, donde cada cita queda ligada a la versión normativa usada.
