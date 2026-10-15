# 🤖 Intervención Detallada Etapa por Etapa de la IA (JullBrain Legal-RAG) en el Caso Penal Venezolano

![Intervención IA Caso Penal SVG](file:///c:/VS%20CODE/CODIGO/JullBrain/docs/intervencion_ia_caso_penal.svg)

---

## ⚖️ Introducción y Principio de Co-pilotaje Judicial

El sistema **JullBrain Legal-RAG** está diseñado para ser un **copiloto analítico de alta precisión** en el proceso penal venezolano. No sustituye la potestad de juzgar consagrada al Poder Judicial ni la titularidad de la acción penal del Ministerio Público, sino que acelera drásticamente la revisión documental, depura vicios procesales y elimina las alucinaciones del modelo mediante verificación semántica y forense en tiempo real.

---

## 📊 Matriz Detallada de Intervención de IA por Etapas

| Etapa Procesal (COPP) | 🤖 Intervención Específica de la IA (JullBrain) | ⚡ Impacto & Agilización Procesal | 🛡️ Mecanismo de Control Humano |
| :--- | :--- | :--- | :--- |
| **1. Ingesta de Denuncia y Actas** *(Art. 265)* | Ingesta OCR ultra-rápida (IBM Docling), extracción de metadatos (Partes, Delito, Folio) y cómputo de Hash SHA-256. | Disponibilidad del expediente digitalizado en **segundos**, eliminando días de tipejo e indexación manual. | El Fiscal del MP valida la integridad del acta. Hash SHA-256 verificado en la metadata. |
| **2. Análisis de Peritajes y Evidencias** *(Art. 223)* | Cruzamiento semántico de peritajes (balística, forense) contra declaraciones. Detección automática de contradicciones. | Identifica vacíos de prueba o contradicciones técnicas al instante, evitando sobreseimientos tardíos. | El Perito e Inspector Forense (R7) verifican los hallazgos en el Visor Dual. |
| **3. Fundamentación de Acusación Fiscal** *(Art. 308)* | Búsqueda atómica de tipos penales, agravantes e inyección asistida de citas jurisprudenciales del TSJ. | Reduce el tiempo de redacción de la acusación de días a **minutos** con 100% de precisión en citas. | Semáforo Verde (Anclado). Firma y aprobación exclusiva del Fiscal del MP. |
| **4. Audiencia Preliminar & Depuración** *(Art. 309)* | Doble Validación Cruzada (Regex vs PyMuPDF). Auditoría de ilicitud probatoria y alertas de faltas de foliatura. | Previene nulidades en Juicio Oral detectando vicios de forma o faltas de foliado con error cero. | El Juez de Control decide sobre la admisibilidad de pruebas o sobreseimiento. |
| **5. Consulta en Audiencia de Juicio** *(Art. 315)* | Búsqueda vectorial instantánea (`<3s`) en debate oral. Ubicación del folio citado con visor dual PDF resaltado. | Elimina recesos en audiencia para buscar carpetas físicas; resolución inmediata de incidencias. | Indicador del Semáforo en Vivo (`app.py`). El Juez de Juicio constata la cita en pantalla. |
| **6. Redacción del Proyecto de Sentencia** *(Art. 346)* | Generación del borrador lógico-jurídico del fallo, garantizando la fundamentación adecuada y anclaje normativo. | Garantiza motivación adecuada (evita inmotivación) y acelera el tipejo de la sentencia. | Firma y decisión 100% exclusiva del Juez de Juicio (Principio CNJ 332/2020: La IA asiste, el Juez decide). |
| **7. Análisis en Casación & Recursos** *(Art. 423/451)* | Detección de inmotivación y cotejo comparativo con la Jurisprudencia Vinculante de la Sala Penal del TSJ. | Acelera la admisión o desestimación de recursos al verificar violaciones directas de norma. | Magistrados de la Corte de Apelaciones y TSJ emiten el fallo definitivo. |
| **8. Cómputo de Pena & Beneficios** *(Art. 471/501)* | Cómputo automatizado auditado de pena y alertas RAG de vencimiento de lapsos procesales para beneficios. | Previene la reclusión indebida por retraso administrativo en el cálculo de redenciones. | Auto de Cómputo dictado y firmado por el Juez de Ejecución de Penas. |

---

## 🛡️ Tres Pilares de Transparencia y Control Anti-Alucinación

1. 🚦 **Semáforo de Confianza Visual (`LLM-as-a-judge`):**
   * 🟢 **VERDE (Score &gt; 90%):** Cita legal totalmente verificada en el corpus normativo cerrado. Copia directa permitida.
   * 🟡 **ÁMBAR (Score 70%-89%):** Ambigüedad interpretativa. Obliga a auditar el contexto en el visor de PDF original.
   * 🔴 **ROJO (Desanclado):** Afirmación no hallada en el expediente o ley. Inyección bloqueada automáticamente.

2. 🔐 **Cadena de Custodia Digital (ISO 27037):**
   * Cómputo de Hash **SHA-256** desde la ingesta.
   * Doble Validación Cruzada (`validator.py`) Regex vs extraction PyMuPDF para garantizar Error Cero.
   * Principio de **Espejo Documental** (R7 Forense).

3. 🏢 **Infraestructura Air-Gapped On-Premise:**
   * Modelos Granite (3B/8B/30B) ejecutados localmente sin salida a Internet.
   * Resguardo absoluto del Secreto de Sumario y la privacidad del expediente penal.

---

> [!TIP]
> **Archivo SVG Generado:** [`docs/intervencion_ia_caso_penal.svg`](file:///c:/VS%20CODE/CODIGO/JullBrain/docs/intervencion_ia_caso_penal.svg)
