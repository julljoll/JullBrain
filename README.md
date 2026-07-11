# JullBrain V-2.0 — Pipeline RAG de Normativas y Formatos (Mi Cerebro Personal)

> Conversión automatizada de PDFs jurídicos y documentos a Markdown estructurado y JSON Jerárquico para sistemas de IA — Powered by IBM Docling y Docker.

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org) [![Licencia MIT](https://img.shields.io/badge/Licencia-MIT-green)](LICENSE) [![IBM Docling](https://img.shields.io/badge/IBM-Docling-purple)](https://github.com/DS4SD/docling) [![Docker](https://img.shields.io/badge/Docker-Enabled-blue)](https://www.docker.com/)

**📖 Documentación completa:** [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | **🗺️ Mapa del framework:** [`FRAMEWORK.md`](FRAMEWORK.md) | **🤖 Skills IA:** [`.AGENTS/_index.md`](.AGENTS/_index.md)

---

## El Problema que Resuelve

Los modelos de lenguaje (LLM) fallan con PDFs de documentos legales y normativos porque:

- Los artículos aparecen fusionados en párrafos de 2,000+ palabras sin separación.
- Las tablas de PDFs se rompen o pierden su estructura.
- No hay metadata legal (Gaceta Oficial, fecha, tipo de instrumento) para filtrar búsquedas RAG.
- El chunking por caracteres o páginas parte artículos a la mitad, generando fragmentos incoherentes.

**JullBrain** convierte esos PDFs en Markdown semánticamente estructurado y en un formato JSON listo (`hierarchical_chunks.json`), con fragmentos inteligentes, listo para ingestarse en **RAGFlow**. Todo esto de forma 100% aislada gracias a **Docker**.

---

## Arquitectura del Pipeline V-2.0

```text
[iniciar_conversion.bat]     ← Interfaz de inicio (Control Visual, Ctrl+C)
       │
       ▼
[Docker Compose]             ← Entorno aislado Python (Sin instalaciones host)
       │
       ▼
normativas_pdf/
       │
       ▼
[IBM Docling + OCR]          ← Extracción profunda + Hierarchical Chunker (JSON)
       │
       ▼
[legalizer.py]               ← Jerarquía: TÍTULO › CAPÍTULO › Artículo
       │
       ▼
[metadata_extractor.py]      ← YAML frontmatter: Gaceta, fecha, SHA-256
       │
       ▼
[validator.py]               ← Integridad: secuencia, duplicados, corruptos
       │
       ├──────────────────────────────────────────────────────────────┐
       ▼                                                              ▼
normativas_rag/                                          normativas_chunks/
  ley-completa.md                                          hierarchical_chunks.json
                                                                      │
                                                                      ▼
                                                                  RAGFlow
```

---

## Módulos del Sistema

| Módulo | Función |
|--------|---------|
| `convert_normativas.py` | Motor principal: Orquestación Docling, Barras de Progreso Visuales (`rich`), Caché SHA-256 y manejo `Ctrl+C`. |
| `legalizer.py` | Detecta jerarquía (TÍTULO/CAPÍTULO/Artículo) y genera TOC interactivos en Markdown. |
| `HierarchicalChunker` | Integrado vía Docling. Extrae chunks semánticos listos para RAGFlow. |
| `metadata_extractor.py` | Inyecta YAML frontmatter con Gaceta, fecha, tipo de documento y huella digital (SHA-256). |
| `validator.py` | Verifica secuencia numérica, previene duplicados y detecta artículos corruptos o cortos. |
| `iniciar_conversion.bat` | Menú interactivo inteligente. Verifica estado de Chocolatey y Docker sin pedir permisos de admin por defecto. |

---

## Funciones Avanzadas

**Arquitectura Docker First** — JullBrain V2.0 corre 100% en contenedores. Olvídate de dependencias de PyTorch, problemas de PATH o fallos en Windows. `docker-compose.yml` gestiona todo.

**Progress Bars TTY** — Monitoreo hiper-visual del proceso en consola, forzando las animaciones de carga incluso dentro del contenedor Docker.

**Interrupción Segura (Ctrl+C)** — Puedes detener el análisis en cualquier momento. JullBrain interceptará la señal y guardará a salvo todo el progreso que ya había logrado procesar.

**Recuperación automática de fallos** — Si un lote falla con OCR activo, el sistema reintenta automáticamente sin OCR en ese lote en lugar de interrumpir la conversión.

**Caché SHA-256 dinámica** — Cada PDF procesado se registra en `.conversion_cache/manifest.json`. Si arrastras un archivo sin cambios, lo salta en un milisegundo.

---

## Resultados Actuales

| Documento | Artículos | Tasa de Conversión |
|-----------|-----------|--------------------|
| Código Penal | 640 | 98.3% |
| Código Orgánico Procesal Penal | 355 | 99.4% |
| Ley Especial de Delitos Informáticos | 35 | 100% |
| Ley sobre Mensajes de Datos | 56 | 98.2% |
| Creación del CENIF | 74 | 100% |

---

## Instalación y Ejecución

Solo necesitas tener [Docker Desktop](https://www.docker.com/products/docker-desktop/) en ejecución. Todo el resto es automatizado.

```cmd
:: 1. Clona el proyecto y entra en la carpeta
cd "ruta/a/JullBrain"

:: 2. Ejecuta el orquestador principal
iniciar_conversion.bat
```

> **Autoinstalación**: Si no tienes Docker ni Chocolatey, el archivo `.bat` te lo indicará. Simplemente cierra, haz **Clic Derecho -> Ejecutar como Administrador** sobre el `.bat` y JullBrain descargará e instalará todas las dependencias necesarias de forma desatendida.

---

## Licencia
Distribuido bajo Licencia MIT.
Desarrollado para avanzar en la transformación tecnológica del ecosistema RAG/IA venezolano.
