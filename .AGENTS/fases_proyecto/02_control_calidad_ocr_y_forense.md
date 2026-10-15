# Skill 02 — Control de Calidad OCR y Verificación Forense de Integridad

## 1. Rol responsable
**R2 (implementación) + R7 (criterios forenses de integridad documental)**.

## 2. Propósito
Evaluar la confiabilidad del texto extraído por OCR sobre documentos escaneados de baja calidad (actas manuscritas, sellos, escaneos antiguos) y aplicar un primer nivel de verificación forense de integridad documental — sin pronunciarse sobre autenticidad ni veracidad de contenido, solo sobre consistencia formal.

## 3. Entradas
- Salida de la Skill 01 (`metadatos_posicion.json`) con score de confianza OCR por elemento (si Docling lo expone) o generado en esta skill.

## 4. Salidas
- Reporte de calidad OCR por documento y por elemento.
- Lista de elementos bajo umbral, marcados `requiere_revision_humana: true`.
- Reporte forense de anomalías formales (ver apartado 7.2).

## 5. Dependencias tecnológicas
Docling (modelos de visión / SmolDocling), Python 3.11+.

## 6. Reglas obligatorias
1. **Nunca se "corrige" automáticamente** un texto de baja confianza — se marca para revisión humana. Corregir silenciosamente equivale a fabricar contenido (Skill 08 lo rechazaría, pero el riesgo se previene aquí).
2. El umbral de confianza es configurable pero debe quedar documentado y versionado (no se cambia "a ojo" entre expedientes).
3. Las anomalías forenses detectadas (apartado 7.2) se **reportan**, nunca se interpretan como prueba de alteración — esa valoración es exclusivamente humana.

## 7. Implementación de referencia

### 7.1 Control de calidad OCR

```python
# skills/02_ocr_calidad/quality_check.py
import json
from pathlib import Path

UMBRAL_CONFIANZA = 0.75  # documentado y versionado; ajustar solo con justificación registrada

def evaluar_calidad(expediente_id: str, data_dir: str = "data/structured"):
    path = Path(data_dir) / expediente_id / "metadatos_posicion.json"
    elementos = json.loads(path.read_text(encoding="utf-8"))

    reporte = []
    for el in elementos:
        confianza = el.get("confianza_ocr", 1.0)  # 1.0 si es texto nativo (no escaneado)
        requiere_revision = confianza < UMBRAL_CONFIANZA
        reporte.append({
            "elemento_id": el["elemento_id"],
            "folio_origen": el["folio_origen"],
            "confianza_ocr": confianza,
            "requiere_revision_humana": requiere_revision,
        })
        el["requiere_revision_humana"] = requiere_revision

    path.write_text(json.dumps(elementos, ensure_ascii=False, indent=2), encoding="utf-8")

    resumen = {
        "expediente_id": expediente_id,
        "total_elementos": len(reporte),
        "elementos_bajo_umbral": sum(r["requiere_revision_humana"] for r in reporte),
        "umbral_usado": UMBRAL_CONFIANZA,
    }
    return resumen, reporte
```

### 7.2 Verificación forense de anomalías formales (R7)

Chequeos de **consistencia formal**, no de contenido (esto no es un peritaje de autenticidad, es una señal de alerta para el operador humano):

```python
# skills/02_ocr_calidad/forense_integridad.py
def detectar_anomalias_formales(elementos: list) -> list:
    """
    Detecta señales formales que ameritan revisión humana:
    - saltos de folio (numeración no consecutiva)
    - elementos sin folio asignado
    - duplicados exactos de folio
    Nunca concluye alteración; solo reporta la anomalía y su ubicación.
    """
    anomalias = []
    folios_vistos = {}
    folio_anterior = None

    for el in elementos:
        folio = el.get("folio_origen")
        if folio is None:
            anomalias.append({"tipo": "folio_ausente", "elemento_id": el["elemento_id"]})
            continue
        if folio in folios_vistos:
            anomalias.append({
                "tipo": "folio_duplicado",
                "elemento_id": el["elemento_id"],
                "folio": folio,
                "elemento_previo": folios_vistos[folio],
            })
        folios_vistos[folio] = el["elemento_id"]

        if folio_anterior is not None and isinstance(folio, int) and isinstance(folio_anterior, int):
            if folio < folio_anterior:
                anomalias.append({
                    "tipo": "folio_fuera_de_secuencia",
                    "elemento_id": el["elemento_id"],
                    "folio": folio,
                    "folio_anterior": folio_anterior,
                })
        folio_anterior = folio if isinstance(folio, int) else folio_anterior

    return anomalias
```

## 8. Criterios de aceptación
- [ ] Todo elemento con confianza OCR bajo el umbral queda marcado, nunca omitido ni auto-corregido.
- [ ] Reporte de anomalías formales generado por cada expediente, aunque esté vacío.
- [ ] Umbral de confianza documentado en el reporte de salida (trazabilidad de la propia configuración).

## 9. Relación con otras skills
Consume la salida de Skill 01. Su reporte de anomalías alimenta la Skill 03 (estructuración cronológica) y la Skill 10 (evaluación), donde una anomalía no resuelta debe reflejarse como riesgo en la medición de confiabilidad.
