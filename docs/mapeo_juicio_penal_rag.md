# ⚖️ Mapeo del Juicio Penal Venezolano (COPP) en la Arquitectura Legal-RAG JullBrain

![Juicio Penal Venezolano RAG SVG](file:///c:/VS%20CODE/CODIGO/JullBrain/docs/mapeo_juicio_penal_rag.svg)

---

## 🏛️ Introducción y Marco Constitucional

El juzgamiento penal en Venezuela se rige por el **Código Orgánico Procesal Penal (COPP)** bajo los principios del **Debido Proceso** contemplados en el **Artículo 49 de la Constitución de la República Bolivariana de Venezuela (CRBV)**.

El sistema **JullBrain Legal-RAG** interconecta cada una de las 5 fases procesales penal con una capa tecnológica especializada de **ingesta documental, chunking atómico, embeddings de alta densidad semántica (Granite R2), vectorización en RAGFlow y auditoría en tiempo real mediante el Semáforo de Confianza Jurídica**.

---

## 📜 1. Desglose Fase por Fase: COPP vs. Pipeline RAG

### 1️⃣ Fase Preparatoria / Investigación (Art. 262 y ss. COPP)
* **Finalidad Legal:** Determinar la existencia de un hecho punible, identificar autores y recabar elementos de convicción a cargo del Ministerio Público y órganos de investigación penal (CICPC, GNB, etc.).
* **Integración Pipeline RAG:**
  * **Ingesta OCR Avanzada:** Procesamiento de actas policiales, denuncias y dictámenes periciales mediante **IBM Docling Engine**.
  * **Cadena de Custodia Digital (ISO 27037):** Registro automático de Hash **SHA-256** (`metadata_extractor.py`) para certificar la no alteración del documento digitalizado.
  * **Chunking Atómico (`legalizer.py`):** Fragmentación limpia preservando foliatura y número de actas.
* **Roles a Cargo:** **R2** (Desarrollador Python Fullstack) + **R7** (IA Forense Penal).

### 2️⃣ Fase Intermedia / Audiencia Preliminar (Art. 309 y ss. COPP)
* **Finalidad Legal:** Evaluar la Acusación Fiscal presentante ante el Juez de Control, depurar vicios formales y decidir la admisibilidad o rechazo de las pruebas ofrecias por las partes.
* **Integración Pipeline RAG:**
  * **Auditoría de Foliatura (`validator.py`):** Verificación automatizada del orden secuencial de folios, alertando sobre saltos o inconsistencias.
  * **Matriz de Admisibilidad Probatoria:** Cotejo semántico de licitud y pertinencia de pruebas contra el COPP y la CRBV.
  * **Evaluación de Excepciones:** Recuperación híbrida de causales de sobreseimiento (Art. 300 COPP).
* **Roles a Cargo:** **R3** (Legaltech) + **R7** (IA Forense Penal).

### 3️⃣ Fase de Juicio Oral y Público (Art. 315 y ss. COPP)
* **Finalidad Legal:** Debate oral, contradicción, evacuación de pruebas testimoniales/periciales y pronunciamiento de la Sentencia Definitiva por el Juez de Juicio.
* **Integración Pipeline RAG:**
  * **Búsqueda Vectorial en Tiempo Real (&lt;3s):** Consultas durante el debate oral utilizando Granite Embedding R2 sobre la Vector DB de RAGFlow.
  * **Semáforo de Confianza Jurídica (`app.py`):** Auditoría visual tricolor en vivo:
    * 🟢 **Verde:** Cita normativa anclada con coincidencia exacta y hash verificado.
    * 🟡 **Ámbar:** Ambigüedad o divergencia jurisprudencial (requiere confirmación en visor PDF).
    * 🔴 **Rojo:** Afirmación no hallada en el corpus cerrado (bloqueo automático).
  * **Cotejo de Testimoniales vs. Actas:** Detección inmediata de contradicciones entre declaraciones orales y actas iniciales.
* **Roles a Cargo:** **R1** (Arquitecto IA) + **R4** (UX/UI DCU).

### 4️⃣ Fase de Impugnación / Recursos (Art. 423 y ss. COPP)
* **Finalidad Legal:** Revisión por la Corte de Apelaciones o la Sala de Casación Penal del Tribunal Supremo de Justicia (TSJ) de resoluciones impugnadas por vicios de juzgamiento o inmotivación.
* **Integración Pipeline RAG:**
  * **Detección de Vicios de Sentencia:** Análisis automatizado de inmotivación (Art. 444 COPP).
  * **Cotejo de Jurisprudencia TSJ:** Búsqueda y comparación con las sentencias vinculantes de la Sala de Casación Penal.
  * **Auditoría de Alucinación:** Evaluación Stanford RegLab para garantizar que no existan argumentos desanclados.
* **Roles a Cargo:** **R3** (Legaltech) + **R1** (Arquitecto IA).

### 5️⃣ Fase de Ejecución de Sentencia (Art. 471 y ss. COPP)
* **Finalidad Legal:** Velar por el cumplimiento de la pena, cómputo definitivo y tramitación de beneficios procesales (libertad condicional, confinamieto, redención por trabajo o estudio).
* **Integración Pipeline RAG:**
  * **Cómputo Automatizado Auditado:** Cálculo preciso de física pena transcurrida y remisión por trabajo/estudio.
  * **Monitoreo de Lapsos Legales:** Alertas RAG programadas cuando el penado cumple las condiciones legales para optar a un beneficio (Art. 501 COPP).
  * **Ficha Histórica de Custodia:** Expediente penal cerrado y archivado con validación SHA-256.
* **Roles a Cargo:** **R2** (Python Fullstack) + **R7** (IA Forense Penal).

---

## 🛡️ Principios Forenses No Negociables (R7)

1. **Integridad de Hash SHA-256:** Ningún archivo ingresa a la base vectorial sin sellado criptográfico inicial.
2. **Reporte de Anomalías de Folio:** Toda alteración o fecha inconsistente es reportada al Juez; nunca se oculta o altera el archivo original.
3. **Principio de Espejo Documental:** El Markdown generado refleja exactamente el contenido del PDF del expediente.
4. **Supervisión Humana Obligatoria:** Ningún borrador o proyecto de auto tiene validez jurídica sin la firma física/digital del operador judicial responsable.

---

> [!TIP]
> **Archivo SVG Generado:** [`docs/mapeo_juicio_penal_rag.svg`](file:///c:/VS%20CODE/CODIGO/JullBrain/docs/mapeo_juicio_penal_rag.svg)
