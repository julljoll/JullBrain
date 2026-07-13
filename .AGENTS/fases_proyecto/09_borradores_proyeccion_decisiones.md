# Skill 09 — Proyección de Decisión (Borradores Fundamentados)

## 1. Rol responsable
**R3 (qué alternativas son jurídicamente razonables y cómo se fundamentan) + R4 (cómo se presenta como borrador, no como decisión)**.

## 2. Propósito
A solicitud expresa del operador jurídico, generar hasta tres alternativas jurídicamente razonables (calificaciones jurídicas posibles, medidas cautelares aplicables, etc.), cada una con su fundamento citado y verificado — presentadas siempre como borrador editable, nunca como resultado final. Es la función equivalente a la "predicción" de Prometea, pero limitada por la salvaguarda de la Resolución CNJ n.° 332/2020: el sistema nunca decide.

## 3. Entradas
- Solicitud explícita del operador ("genera proyectos de decisión sobre X").
- Chunks del expediente y de la normativa relevante (vía Skill 05).

## 4. Salidas
- Hasta 3 alternativas, cada una con: fundamento normativo citado, fundamento fáctico citado, nivel de confianza declarado, y el rótulo obligatorio `BORRADOR — requiere validación humana`.

## 5. Dependencias tecnológicas
Skill 07 (generación) + Skill 08 (verificación), reutilizadas — esta skill no genera texto por fuera de ese pipeline.

## 6. Reglas obligatorias
1. **Solo se activa a solicitud explícita** del operador jurídico — nunca se generan proyectos de decisión de forma proactiva o automática junto a una consulta de análisis simple.
2. Cada alternativa pasa por la Skill 08 igual que cualquier otra afirmación — sin excepción por tratarse de una "propuesta".
3. El rótulo de borrador y la ausencia de efecto jurídico deben ser visualmente inequívocos en la interfaz (responsabilidad conjunta con R4) — no basta con un texto pequeño al pie.
4. Ninguna alternativa se presenta sin al menos una cita verificada de tipo `anclado`. Si ninguna alternativa logra respaldo suficiente, el sistema se abstiene de proyectar y lo comunica explícitamente.

## 7. Implementación de referencia

```python
# skills/09_proyeccion_decision/proyeccion.py
from typing import List

PROMPT_PROYECCION = """Genera hasta 3 alternativas jurídicamente razonables para la siguiente
consulta, basándote EXCLUSIVAMENTE en el contexto proporcionado. Cada alternativa debe:
- Citar su fundamento normativo con [chunk_id]
- Citar su fundamento fáctico (evidencia del expediente) con [chunk_id]
- Incluir un nivel de confianza (alto/medio/bajo) según la solidez del respaldo documental
No decidas cuál alternativa es la correcta. No emitas juicio de valor sobre culpabilidad.
Si el contexto no permite fundamentar ninguna alternativa con al menos una cita verificable,
responde: "No hay respaldo documental suficiente para proyectar alternativas."
"""

def generar_proyecto_decision(consulta: str, chunks_contexto: list, generar_fn, verificar_fn, indice_chunks: dict) -> dict:
    resultado_generacion = generar_fn(
        pregunta=f"{PROMPT_PROYECCION}\n\nConsulta del operador: {consulta}",
        chunks_contexto=chunks_contexto,
    )

    if resultado_generacion["abstencion"]:
        return {"estado": "abstencion", "mensaje": resultado_generacion["respuesta"]}

    verificacion = verificar_fn(resultado_generacion["respuesta"], indice_chunks)

    if verificacion["citas_ancladas"] == 0:
        return {
            "estado": "abstencion",
            "mensaje": "Ninguna alternativa alcanzó respaldo documental verificable. "
                       "Se recomienda análisis manual directo del expediente.",
        }

    return {
        "estado": "borrador_generado",
        "rotulo_obligatorio": "BORRADOR — requiere validación humana. Sin efecto jurídico.",
        "contenido": resultado_generacion["respuesta"],
        "verificacion": verificacion,
    }
```

## 8. Criterios de aceptación
- [ ] 100% de los proyectos de decisión generados en pruebas incluyen el rótulo de borrador de forma explícita en el objeto de salida.
- [ ] Ningún proyecto de decisión se entrega con cero citas ancladas.
- [ ] Prueba de interfaz (con R4): el usuario de prueba, en think-aloud, identifica sin ayuda que el contenido no es una decisión tomada.

## 9. Relación con otras skills
Reutiliza Skill 07 y Skill 08. Su diseño de presentación depende de la Skill 00 (wireframe validado). Alimenta a la Skill 10 como categoría separada de evaluación (dado que el estándar de éxito del Capítulo VI exige 100% de marcado como borrador).
