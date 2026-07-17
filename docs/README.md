# JullBrain — Documentación Técnica

Bienvenido a la documentación técnica de JullBrain **V-2.1**.

## Índice de Documentación

| Documento | Descripción |
|---|---|
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Arquitectura completa V-2.1: pipeline de 6 etapas, 7 paneles Streamlit, tabla `pipeline_config.json` |
| [`../FRAMEWORK.md`](../FRAMEWORK.md) | Mapa del repositorio organizado como framework IBM |
| [`../README.md`](../README.md) | README principal del proyecto |

---

## Skills de IA (`.agents/skills/`)

| Skill | Descripción |
|---|---|
| [`conversor-pdf-a-rag`](../.agents/skills/conversor-pdf-a-rag/SKILL.md) | Pipeline maestro: PDF → Markdown → JSON → RAGFlow |
| [`analizador-jerarquia-legal`](../.agents/skills/analizador-jerarquia-legal/SKILL.md) | Depuración de `legalizer.py`: jerarquía TÍTULO/CAPÍTULO/Artículo |
| [`extractor-metadata-legal`](../.agents/skills/extractor-metadata-legal/SKILL.md) | YAML frontmatter, Gaceta Oficial, SHA-256 |
| [`validador-calidad-ocr`](../.agents/skills/validador-calidad-ocr/SKILL.md) | Integridad de artículos, validación cruzada PyMuPDF |
| [`granite-embedder`](../.agents/skills/granite-embedder/SKILL.md) | **[NUEVO V-2.1]** Motor de embeddings semánticos Granite R2 multilingüe |
| [`controlador-iniciador-bat`](../.agents/skills/controlador-iniciador-bat/SKILL.md) | Administración del orquestador `.bat` |

---

## Guías Rápidas

- [Instalación y ejecución](../README.md#instalación-y-ejecución)
- [Módulos del sistema](../README.md#módulos-del-sistema)
- [Compatibilidad IBM Granite](../README.md#compatibilidad-con-ibm-granite)
- [Motor de Embeddings](../README.md#nota-sobre-el-modelo-de-embeddings)
