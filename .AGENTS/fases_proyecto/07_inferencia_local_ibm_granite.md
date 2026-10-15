# Skill 07 — Orquestación de Inferencia con IBM Granite (Ollama local)

## 1. Rol responsable
**R1 (diseño del prompt de sistema y política de generación) + R2 (implementación de la orquestación)**.

## 2. Propósito
Generar el análisis en lenguaje natural del expediente, condicionado estrictamente a los chunks recuperados por la Skill 05, con temperatura baja, instrucción de citación obligatoria y **abstención explícita** cuando no exista respaldo documental suficiente.

## 3. Entradas
- Consulta del operador jurídico (lenguaje natural).
- Chunks recuperados por `retrieve()` (Skill 05), con su metadato de origen.

## 4. Salidas
- Respuesta generada, estructurada por afirmación, cada una con cita de folio/artículo o marcada `no_verificado`.

## 5. Dependencias tecnológicas
Ollama (despliegue local de Granite 4.1, 8B recomendado para el piloto), Python 3.11+.

## 6. Reglas obligatorias
1. **Temperatura baja fija** (≤ 0.2) — no configurable por el usuario final, para reducir varianza no verificable.
2. **Prohibición de responder sin fragmentos recuperados.** Si `retrieve()` no devuelve chunks relevantes, el sistema debe abstenerse explícitamente, nunca generar desde conocimiento paramétrico del modelo.
3. El prompt de sistema exige que cada afirmación individual quede asociada a un `chunk_id` citado — no se acepta una respuesta con citas "globales" al final del texto.
4. Ninguna respuesta se entrega al usuario sin pasar antes por la Skill 08 (verificación post-generación).

## 7. Implementación de referencia

```python
# skills/07_granite_inferencia/inferencia.py
import requests
import json

OLLAMA_API = "http://localhost:11434/api/generate"
MODELO = "granite4.1:8b"

SYSTEM_PROMPT = """Eres un asistente de análisis documental para expedientes penales venezolanos.
Reglas estrictas:
1. Responde EXCLUSIVAMENTE con base en los fragmentos de contexto proporcionados.
2. Cada afirmación debe citar el chunk_id exacto del fragmento que la sustenta, en el formato [chunk_id].
3. Si el contexto no contiene información suficiente para responder con certeza, debes decir explícitamente
   "No se encuentra información suficiente en el expediente/normativa cargada para responder esto"
   en lugar de inferir, suponer o completar con conocimiento general.
4. No emitas juicios de culpabilidad, inocencia ni valoraciones de prueba. Solo organiza y cita.
5. No generes una decisión: si te piden un proyecto de decisión, marca la respuesta como "BORRADOR - requiere validación humana".
"""

def generar_respuesta(pregunta: str, chunks_contexto: list) -> dict:
    contexto_texto = "\n\n".join(
        f"[{c['metadata']['chunk_id']}] (folio: {c['metadata'].get('folio_origen')}, "
        f"artículo: {c['metadata'].get('articulo_origen')}):\n{c['content']}"
        for c in chunks_contexto
    )

    if not chunks_contexto:
        return {
            "respuesta": "No se encuentra información suficiente en el expediente/normativa cargada para responder esto.",
            "abstencion": True,
            "citas_usadas": [],
        }

    prompt_completo = f"{SYSTEM_PROMPT}\n\nCONTEXTO:\n{contexto_texto}\n\nPREGUNTA: {pregunta}\n\nRESPUESTA:"

    resp = requests.post(OLLAMA_API, json={
        "model": MODELO,
        "prompt": prompt_completo,
        "stream": False,
        "options": {"temperature": 0.15, "top_p": 0.9},
    })
    resp.raise_for_status()
    texto_generado = resp.json()["response"]

    return {
        "respuesta": texto_generado,
        "abstencion": "no se encuentra información suficiente" in texto_generado.lower(),
        "citas_usadas": [c["metadata"]["chunk_id"] for c in chunks_contexto],
    }
```

## 8. Criterios de aceptación
- [ ] Prueba con contexto vacío: el sistema se abstiene explícitamente, no alucina.
- [ ] Prueba con contexto irrelevante a la pregunta: el sistema no fuerza una cita fuera de tema.
- [ ] Muestreo de 10 respuestas: 100% incluyen al menos un `[chunk_id]` por afirmación factual, salvo en abstención.

## 9. Relación con otras skills
Consume Skill 05. Su salida pasa obligatoriamente por la Skill 08 antes de llegar al usuario.
