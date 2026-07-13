# Skill 03 — Estructuración Cronológica del Expediente

## 1. Rol responsable
**R1 (diseño del ordenamiento) + R7 (detección forense de anomalías cronológicas)**.

## 2. Propósito
Ordenar los fragmentos documentales del expediente según fecha, folio y tipo de acto procesal (denuncia, acta policial, dictamen pericial, audiencia, decisión judicial), generando el eje cronológico sobre el que se apoya todo el análisis posterior — y detectando, sin interpretarlas, inconsistencias temporales.

## 3. Entradas
- Salida de la Skill 02 (elementos con folio, confianza OCR y marcas de revisión).

## 4. Salidas
- `linea_cronologica.json`: elementos ordenados por `orden_cronologico`, con tipo de acto procesal clasificado.
- Reporte de anomalías cronológicas (fechas fuera de secuencia, actos sin fecha, vacíos temporales relevantes).

## 5. Dependencias tecnológicas
Python 3.11+, expresiones regulares o modelo ligero de extracción de fechas (`dateparser`), taxonomía de actos procesales del COPP.

## 6. Reglas obligatorias
1. El orden cronológico se basa en la fecha del acto, **no en el orden de folio**, salvo que la fecha no sea extraíble — en ese caso se usa folio como respaldo y se marca explícitamente `orden_por_folio_no_por_fecha: true`.
2. **Ninguna anomalía cronológica se "resuelve" automáticamente** (p. ej. una decisión judicial fechada antes que la acusación que la origina): se reporta como hallazgo forense para revisión humana obligatoria.
3. La taxonomía de tipos de acto procesal debe estar versionada y basada en el COPP — no se inventan categorías ad hoc.

## 7. Implementación de referencia

```python
# skills/03_estructuracion_cronologica/cronologia.py
import json
import re
from pathlib import Path
from datetime import datetime

TIPOS_ACTO = {
    "denuncia": r"\bdenuncia\b",
    "acta_policial": r"\bacta policial\b",
    "dictamen_pericial": r"\bdictamen pericial\b|\bexperticia\b",
    "audiencia": r"\baudiencia\b",
    "decision_judicial": r"\bsentencia\b|\bauto\b|\bdecisión\b",
}

PATRON_FECHA = re.compile(r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b")

def clasificar_tipo_acto(texto: str) -> str:
    texto_lower = texto.lower()
    for tipo, patron in TIPOS_ACTO.items():
        if re.search(patron, texto_lower):
            return tipo
    return "no_clasificado"

def extraer_fecha(texto: str):
    match = PATRON_FECHA.search(texto)
    if not match:
        return None
    dia, mes, anio = match.groups()
    anio = int(anio) if len(anio) == 4 else 2000 + int(anio)
    try:
        return datetime(anio, int(mes), int(dia)).isoformat()
    except ValueError:
        return None  # fecha inválida: se reporta, no se descarta el elemento

def estructurar_cronologia(expediente_id: str, data_dir: str = "data/structured"):
    path = Path(data_dir) / expediente_id / "metadatos_posicion.json"
    elementos = json.loads(path.read_text(encoding="utf-8"))

    for el in elementos:
        el["tipo_acto"] = clasificar_tipo_acto(el["texto"])
        el["fecha_extraida"] = extraer_fecha(el["texto"])

    con_fecha = [e for e in elementos if e["fecha_extraida"]]
    sin_fecha = [e for e in elementos if not e["fecha_extraida"]]

    con_fecha.sort(key=lambda e: e["fecha_extraida"])
    for i, el in enumerate(con_fecha):
        el["orden_cronologico"] = i
        el["orden_por_folio_no_por_fecha"] = False

    anomalias = detectar_anomalias_cronologicas(con_fecha)

    salida = {
        "expediente_id": expediente_id,
        "elementos_ordenados": con_fecha,
        "elementos_sin_fecha_detectada": sin_fecha,
        "anomalias_cronologicas": anomalias,
    }
    out_path = Path(data_dir) / expediente_id / "linea_cronologica.json"
    out_path.write_text(json.dumps(salida, ensure_ascii=False, indent=2), encoding="utf-8")
    return salida

def detectar_anomalias_cronologicas(elementos_ordenados: list) -> list:
    """
    Regla forense básica: un acto procesal que depende lógicamente de otro
    no debería tener fecha anterior a su antecedente (p. ej. decisión antes
    que la acusación). Aquí se reporta solo el patrón más simple y verificable:
    inversión de tipos de acto con dependencia conocida.
    """
    dependencias = {"decision_judicial": ["denuncia", "acta_policial"]}
    anomalias = []
    fechas_por_tipo = {}

    for el in elementos_ordenados:
        tipo = el["tipo_acto"]
        fechas_por_tipo.setdefault(tipo, []).append(el)

    for tipo_dependiente, antecedentes in dependencias.items():
        if tipo_dependiente not in fechas_por_tipo:
            continue
        primera_dependiente = fechas_por_tipo[tipo_dependiente][0]["fecha_extraida"]
        for antecedente in antecedentes:
            if antecedente in fechas_por_tipo:
                primera_antecedente = fechas_por_tipo[antecedente][0]["fecha_extraida"]
                if primera_dependiente < primera_antecedente:
                    anomalias.append({
                        "tipo": "inversion_cronologica",
                        "acto_posterior_esperado": tipo_dependiente,
                        "acto_anterior_esperado": antecedente,
                        "detalle": "El acto dependiente tiene fecha anterior a su antecedente lógico.",
                    })
    return anomalias
```

## 8. Criterios de aceptación
- [ ] 100% de los elementos con fecha extraíble quedan ordenados con `orden_cronologico`.
- [ ] Elementos sin fecha detectada se listan aparte, nunca se descartan ni se les asigna fecha estimada.
- [ ] Todo hallazgo de `anomalias_cronologicas` se refleja en la interfaz (Skill 00/09) como alerta, no como corrección silenciosa.

## 9. Relación con otras skills
Base para la Skill 04 (chunking) y para el panel de análisis cronológico de la interfaz. Sus anomalías retroalimentan la Skill 10 (evaluación) como factor de riesgo documental.
