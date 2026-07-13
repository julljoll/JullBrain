# Skill 08 — Verificación Post-Generación y Trazabilidad de Citas

## 1. Rol responsable
**R2 (implementación) + R3 (criterio jurídico de qué constituye una cita válida) + R7 (integridad forense de la cadena cita→fuente)**.

## 2. Propósito
Es el **módulo central de mitigación de alucinación** del proyecto. Verifica, después de cada generación (Skill 07), que cada cita `[chunk_id]` corresponda efectivamente a un fragmento existente en la base vectorial y que su contenido respalde razonablemente la afirmación — implementando la tipología del estudio Stanford RegLab: **fabricación** (cita a un chunk_id inexistente) y **desanclaje/misgrounding** (cita a un chunk real que no respalda lo afirmado).

## 3. Entradas
- Respuesta generada por la Skill 07, con sus `citas_usadas`.
- Índice de chunks reales (Skill 05) para contraste.

## 4. Salidas
- Respuesta anotada con estado por afirmación: `anclado` (verde) / `desanclado` (ámbar) / `no_encontrado` (rojo).
- Registro de auditoría de verificación (para la Skill 10).

## 5. Dependencias tecnológicas
Python 3.11+. Opcionalmente un segundo paso de verificación semántica con el propio Granite en modo "verificador" (rol distinto al de generación).

## 6. Reglas obligatorias
1. **Nunca se fuerza una cita.** Si no se puede verificar el respaldo, se marca `no_encontrado` — no se elimina la afirmación silenciosamente ni se le asigna una cita "aproximada".
2. La verificación de existencia (`chunk_id` real) es obligatoria y automática al 100%. La verificación de respaldo semántico (¿el chunk realmente sostiene la afirmación?) es asistida por modelo pero **siempre auditable por revisión humana** — no es definitiva por sí sola.
3. Cada verificación queda registrada con timestamp y `version_corpus` usada (Skill 06), para reconstrucción forense posterior.
4. Esta skill es la última puerta antes de que cualquier texto llegue al operador jurídico — ninguna otra skill puede saltarla.

## 7. Implementación de referencia

```python
# skills/08_trazabilidad_citas/verificacion.py
import re
import json
from datetime import datetime

def extraer_citas(texto: str) -> list:
    return re.findall(r"\[([\w\-]+)\]", texto)

def verificar_existencia(chunk_id: str, indice_chunks: dict) -> bool:
    """indice_chunks: dict {chunk_id: {"texto":..., "folio_origen":..., ...}}"""
    return chunk_id in indice_chunks

def verificar_respaldo_semantico(afirmacion: str, chunk_texto: str, verificador_llm) -> str:
    """
    verificador_llm: función que llama a Granite en un rol de VERIFICADOR (prompt distinto
    al generador, temperatura 0), respondiendo solo "RESPALDADO" o "NO_RESPALDADO".
    Nunca se usa el mismo turno de generación para autoverificarse.
    """
    prompt_verificador = f"""Eres un verificador estricto. No generes texto nuevo.
Fragmento fuente: "{chunk_texto}"
Afirmación a verificar: "{afirmacion}"
¿El fragmento fuente respalda razonablemente la afirmación? Responde únicamente "RESPALDADO" o "NO_RESPALDADO"."""
    resultado = verificador_llm(prompt_verificador, temperature=0.0)
    return "anclado" if "RESPALDADO" in resultado.upper() and "NO_RESPALDADO" not in resultado.upper() else "desanclado"

def verificar_respuesta(respuesta_texto: str, indice_chunks: dict, verificador_llm=None) -> dict:
    citas = extraer_citas(respuesta_texto)
    resultados = []

    for chunk_id in set(citas):
        existe = verificar_existencia(chunk_id, indice_chunks)
        if not existe:
            resultados.append({
                "chunk_id": chunk_id,
                "estado": "no_encontrado",
                "categoria_stanford": "fabricacion",
            })
            continue

        estado = "anclado"
        categoria = None
        if verificador_llm:
            # Verificación semántica opcional; siempre queda sujeta a revisión humana
            estado = verificar_respaldo_semantico(
                respuesta_texto, indice_chunks[chunk_id]["texto"], verificador_llm
            )
            categoria = "desanclaje" if estado == "desanclado" else None

        resultados.append({
            "chunk_id": chunk_id,
            "estado": estado,
            "categoria_stanford": categoria,
        })

    registro_auditoria = {
        "timestamp": datetime.utcnow().isoformat(),
        "total_citas": len(citas),
        "citas_ancladas": sum(1 for r in resultados if r["estado"] == "anclado"),
        "citas_desancladas": sum(1 for r in resultados if r["estado"] == "desanclado"),
        "citas_no_encontradas": sum(1 for r in resultados if r["estado"] == "no_encontrado"),
        "detalle": resultados,
    }
    return registro_auditoria
```

## 8. Criterios de aceptación
- [ ] Prueba adversarial: inyectar manualmente un `chunk_id` inexistente en una respuesta y confirmar que se clasifica `no_encontrado`/`fabricacion`.
- [ ] Prueba de desanclaje: citar un chunk real pero de contenido no relacionado, y confirmar detección de `desanclado`.
- [ ] Tasa de anclaje verificable ≥ 90% sobre el set de prueba (meta del Capítulo VI del proyecto).
- [ ] 100% de las verificaciones quedan registradas con timestamp y `version_corpus`.

## 9. Relación con otras skills
Puerta de salida obligatoria de la Skill 07. Alimenta directamente la Skill 09 (los proyectos de decisión pasan por la misma verificación) y la Skill 10 (fuente primaria de datos para medir tasa de alucinación).
