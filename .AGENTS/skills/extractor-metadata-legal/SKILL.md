---
name: JullBrain-extractor-metadata-legal
description: Skill para el módulo metadata_extractor.py de JullBrain en Google Antigravity. Úsalo cuando necesites extraer o corregir el YAML frontmatter de normativas venezolanas, agregar número de Gaceta Oficial, fecha de publicación o tipo de instrumento, calcular el hash SHA-256 de un PDF en RAG/datos_brutos, o diseñar filtros de búsqueda RAG basados en metadata.
---

# 🏛️ JullBrain — Extractor de Metadata Legal y Forense (`metadata_extractor.py`)

Este skill gobierna [`metadata_extractor.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/metadata_extractor.py), responsable de extraer metadatos jurídicos venezolanos y huellas criptográficas `SHA-256` para cada documento procesado desde `RAG/datos_brutos/`.

---

## 1. Esquema Oficial de Metadata YAML (`v0.2.0`)

Cada archivo Markdown generado en `RAG/Informacion_docling_rag/` incluye un bloque YAML frontmatter inmediatamente después del encabezado canónico:

```yaml
---
titulo: "Código Orgánico Procesal Penal"
tipo_instrumento: "Código Orgánico"
gaceta_oficial: "6.644 Extraordinario"
fecha_publicacion: "17 de septiembre de 2021"
ente_emisor: "Asamblea Nacional"
materia: "Derecho Procesal Penal"
estado_vigencia: "Vigente"
total_articulos: 520
archivo_origen: "copp_2021.pdf"
sha256_origen: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
fecha_procesamiento_utc: "2026-11-10T17:30:00Z"
motor_extraccion: "IBM Docling (CPU) + IBM Granite Embedding R2"
---
```

---

## 2. Reglas de Extracción y Trazabilidad Forense

1. **Hash Criptográfico Obligatorio (`SHA-256`)**:
   - Todo documento PDF o Word en `RAG/datos_brutos/` debe tener su hash `SHA-256` calculado sobre los bytes originales antes de cualquier transformación (`compute_file_sha256()`).
2. **Detección de Gaceta Oficial Venezolana**:
   - Soporta numeración ordinaria y extraordinaria (`Gaceta Oficial N° 39.123`, `G.O.E. N° 6.155 Extraordinario`, con o sin puntos de miles).
3. **Abstención Explícita en Metadata**:
   - Si un dato (como el número de Gaceta o la fecha exacta) no aparece en el documento, se registra como `"No especificado"` — **jamás** se adivina ni se inventa (Principios 5 y 7).
4. **Propagación a Chunks de RAGFlow (`RAG/normativas_chunks/`)**:
   - Los metadatos extraídos se inyectan en cada chunk JSON generado por `convert_normativas.py` para permitir filtrado híbrido en `opensearch_indexer.py` y `RAGFlow`.
