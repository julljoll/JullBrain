# Skill 10 — Evaluación de la Tasa de Alucinación (Estudio Piloto)

## 1. Rol responsable
**R3 (diseño metodológico y criterio jurídico de evaluación) + R7 (criterios forenses de rigor probatorio en la rúbrica)**.

## 2. Propósito
Medir, mediante evaluación humana experta ciega, la tasa de alucinación del sistema (fabricación + desanclaje) frente a la línea base del Stanford RegLab (17%-33%), usando una rúbrica adaptada de dicho estudio y reforzada con criterios forenses propios del expediente penal (integridad documental, consistencia cronológica).

## 3. Entradas
- Set de al menos 50 consultas de prueba sobre ≥10 expedientes (simulados o anonimizados).
- Registros de auditoría de la Skill 08 (verificación automática) como insumo, no como sustituto de la evaluación humana.

## 4. Salidas
- Matriz de evaluación por consulta: `correcta_anclada` / `correcta_parcialmente_desanclada` / `desanclada` / `fabricada`.
- Cálculo de tasa de alucinación total, tasa de anclaje verificable, índice Kappa de Cohen inter-evaluador.
- Reporte comparativo contra la línea base Stanford RegLab.

## 5. Dependencias tecnológicas
Python 3.11+ (`scikit-learn` para Kappa de Cohen), planilla de evaluación ciega (dos evaluadores independientes, sin ver la clasificación automática de la Skill 08 mientras evalúan).

## 6. Reglas obligatorias
1. **Evaluación ciega:** los evaluadores humanos no ven la clasificación automática de la Skill 08 al momento de evaluar — evita sesgo de anclaje hacia el propio sistema.
2. Mínimo dos evaluadores independientes por respuesta; toda discrepancia se resuelve por un tercer evaluador, nunca por promedio automático.
3. La rúbrica forense (R7) evalúa adicionalmente si la respuesta respeta el "espejo documental" (Skills 01-03): ¿el sistema reordenó, resumió u omitió contenido de forma que alteraría su lectura por un tercero?
4. El cálculo de Kappa de Cohen se reporta siempre, incluso si es bajo — no se descartan evaluadores para mejorar el número.

## 7. Implementación de referencia

```python
# skills/10_evaluacion_alucinacion/evaluacion.py
from sklearn.metrics import cohen_kappa_score
import json

CATEGORIAS = ["correcta_anclada", "correcta_parcialmente_desanclada", "desanclada", "fabricada"]

def calcular_tasa_alucinacion(evaluaciones: list) -> dict:
    """
    evaluaciones: lista de dicts {"consulta_id": str, "categoria": str}
    (ya consolidadas tras resolver discrepancias entre evaluadores)
    """
    total = len(evaluaciones)
    alucinadas = sum(1 for e in evaluaciones if e["categoria"] in ("desanclada", "fabricada"))
    ancladas_verificables = sum(1 for e in evaluaciones if e["categoria"] == "correcta_anclada")

    return {
        "total_evaluado": total,
        "tasa_alucinacion_total": round(alucinadas / total, 4) if total else None,
        "tasa_anclaje_verificable": round(ancladas_verificables / total, 4) if total else None,
        "linea_base_stanford_min": 0.17,
        "linea_base_stanford_max": 0.33,
        "cumple_meta_minima": (alucinadas / total) < 0.17 if total else None,
    }

def calcular_concordancia_interevaluador(eval_evaluador1: list, eval_evaluador2: list) -> float:
    """
    eval_evaluadorN: lista de categorías en el mismo orden de consultas para cada evaluador.
    """
    return cohen_kappa_score(eval_evaluador1, eval_evaluador2)

def checklist_forense(respuesta_texto: str, elementos_originales: list) -> dict:
    """
    Verificación de espejo documental: ¿todo elemento citable del expediente
    sigue siendo localizable y no fue alterado en su sentido por el resumen?
    Esta función NO decide alucinación; alimenta el criterio forense de la rúbrica humana.
    """
    return {
        "requiere_revision_manual": True,
        "nota_r7": (
            "Verificar manualmente: (1) que ningún folio marcado como 'requiere_revision_humana' "
            "en la Skill 02 fue citado como si estuviera verificado; "
            "(2) que ninguna anomalía cronológica de la Skill 03 fue omitida silenciosamente en la respuesta."
        ),
    }
```

## 8. Criterios de aceptación (metas del proyecto, Capítulo VI)
- [ ] Tasa de alucinación total < 17% (piso de la línea base Stanford RegLab).
- [ ] Tasa de anclaje verificable > 90%.
- [ ] Kappa de Cohen inter-evaluador > 0.7.
- [ ] 100% de las respuestas evaluadas pasaron por el checklist forense antes de consolidar el resultado.

## 9. Relación con otras skills
Consume registros de auditoría de la Skill 08 y anomalías de las Skills 02-03. Su resultado es el entregable central del Capítulo VI (Estudio Piloto) del anteproyecto.
