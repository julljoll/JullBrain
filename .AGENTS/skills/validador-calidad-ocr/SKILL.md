---
name: JullBrain-validador-calidad-ocr
description: Skill para los módulos validator.py, audit_logger.py y granite_guardian_guardrail.py de JullBrain en Google Antigravity. Úsalo cuando necesites verificar la integridad de artículos después de la conversión, ejecutar la doble validación cruzada contra el PDF original, auditar la cadena HMAC-SHA256 o configurar los guardrails de ciberseguridad IBM Granite Guardian.
---

# 🛡️ JullBrain — Validador Forense de Calidad OCR y Ciberseguridad IBM (`validator.py` · `audit_logger.py` · `granite_guardian_guardrail.py`)

Este skill integra la validación de calidad documental (Principio 10: Error Cero) con las capas de ciberseguridad forense de **IBM** implementadas en **JullBrain v0.2.0**.

---

## 1. Doble Validación Cruzada en [`validator.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/validator.py)

Ningún documento convertido en `RAG/Informacion_docling_rag/` alcanza el estado `OK` sin aprobar dos verificaciones independientes:
1. **Validación Interna del Markdown (`validate_document`)**:
   - Comprueba la presencia y validez del YAML frontmatter.
   - Verifica la secuencia numérica continua de artículos (`Artículo 1` ... `Artículo N`), reportando artículos faltantes, duplicados o fragmentos corruptos (`< 30` caracteres).
2. **Validación Cruzada contra el PDF Original (`cross_validate_against_pdf`)**:
   - Extrae directamente el texto del PDF en `RAG/datos_brutos/` mediante **PyMuPDF (`fitz`)** y contabiliza los encabezados de artículos en el documento fuente.
   - Contrasta ambos conjuntos de artículos para garantizar que `IBM Docling` no haya omitido ninguna página ni fusionado artículos.

---

## 2. Ciberseguridad Forense en [`audit_logger.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/audit_logger.py)

1. **Cadena Criptográfica Inmutable (`HMAC-SHA256-CHAIN`)**:
   - Cada evento registrado en `logs/audit_forensic.jsonl` enlaza el hash del registro previo (`prev_hash`) y calcula una firma `HMAC-SHA256` verificable en tiempo constante (`hmac.compare_digest`) mediante `verify_log_integrity()`.
2. **Sellado de Bóveda de Modelos IA (`seal_and_verify_model_vault`)**:
   - Genera y verifica `RAG/modelos_ia/vault_manifest_sha256.json` para detectar cualquier alteración o envenenamiento de pesos (`Model Tampering`).
3. **Inspección de Magic Bytes (`validate_pdf_magic_bytes`)**:
   - Verifica que todo archivo en `RAG/datos_brutos/` posea la firma binaria `%PDF-` y un tamaño válido antes de procesarlo.

---

## 3. Guardrails Cognitivos en [`granite_guardian_guardrail.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/granite_guardian_guardrail.py)

Implementa evaluación de riesgos en 6 dimensiones con **IBM Granite Guardian 3.2/3.3**:
- **Pre-Inferencia (`check_prompt_safety`)**:
  1. `jailbreak_prompt_injection`: Bloquea intentos de evasión de reglas jurídicas o inyección de instrucciones.
  2. `harm_hap`: Bloquea lenguaje de odio, abuso o solicitud de actos ilícitos.
  3. `pii_exposure`: Detecta y redacta PII venezolano (Cédula `V-/E-`, `RIF`, teléfonos, correos).
- **Post-Inferencia (`verify_groundedness`)**:
  4. `groundedness`: Verifica que toda cita de artículo (`Art. X`) exista realmente en los chunks recuperados de `RAG/normativas_chunks/`.
  5. `context_relevance` y 6. `answer_relevance`.
