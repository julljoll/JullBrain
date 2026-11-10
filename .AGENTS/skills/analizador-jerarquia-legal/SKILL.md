---
name: JullBrain-analizador-jerarquia-legal
description: Skill especializado en el módulo legalizer.py de JullBrain para Google Antigravity. Úsalo cuando artículos venezolanos no se detectan correctamente, la jerarquía TÍTULO/CAPÍTULO/SECCIÓN/Artículo está mal anidada, necesitas agregar soporte para un nuevo patrón de ley o gaceta venezolana, o los artículos se fusionan entre sí.
---

# ⚖️ JullBrain — Analizador de Jerarquía Legal Venezolana (`legalizer.py`)

Este skill guía el mantenimiento y extensión de [`legalizer.py`](file:///c:/VS%20CODE/CODIGO/JullBrain/legalizer.py), el motor determinista que transforma el Markdown crudo de `IBM Docling` en una jerarquía normativa estricta antes y después de la fragmentación para **RAGFlow**.

---

## 1. Jerarquía Normativa Estricta en Markdown

| Nivel Jerárquico | Nivel Markdown | Patrón en Legislación Venezolana |
| :--- | :--- | :--- |
| **Libro / Parte** | `#` (`H1`) | `LIBRO PRIMERO`, `PARTE PRIMERA` |
| **Título** | `#` (`H1`) | `TÍTULO I`, `TÍTULO PRELIMINAR` |
| **Capítulo** | `##` (`H2`) | `CAPÍTULO I`, `CAPÍTULO ÚNICO` |
| **Sección** | `###` (`H3`) | `Sección Primera`, `SECCIÓN I` |
| **Artículo** | `###` (`H3`) | `Artículo 1.`, `Artículo 15.-`, `ARTÍCULO 20°` |
| **Disposiciones** | `##` (`H2`) | `DISPOSICIONES TRANSITORIAS / DEROGATORIAS / FINALES` |

---

## 2. Reglas de Oro al Modificar `legalizer.py`

1. **Separación de Artículos Fusionados (`split_merged_articles`)**:
   - Los PDFs de Gaceta Oficial a doble columna suelen fusionar el final de un artículo con el inicio del siguiente en el mismo párrafo.
   - Asegúrate de que la expresión regular distinga entre un **inicio real de artículo** (`Artículo 12. El que...`) y una **referencia interna** en medio de una oración (`...conforme al artículo 12 de esta Ley...`).
2. **Principio de Espejo Documental (Requisito Forense R7)**:
   - `legalizer.py` sólo estructura encabezados, saltos de línea y limpieza de artefactos de paginación; **jamás** debe alterar, resumir ni suprimir palabras del texto normativo original.
3. **Encabezado Canónico y Footer Vacío (Principio 9)**:
   - El documento Markdown resultante debe conservar intacto el encabezado canónico al inicio y no añadir ningún pie de página al final.
4. **Verificación Obligatoria**:
   - Tras cualquier ajuste en `legalizer.py`, ejecuta la suite de pruebas:
     ```powershell
     python -m unittest tests/test_core_pipeline.py
     ```
