# Manual de Usuario — JullBrain Enterprise Legal Platform

---

## 🚀 Introducción

Bienvenido a **JullBrain Enterprise**, la plataforma de Inteligencia Documental Legal diseñada específicamente para departamentos jurídicos, auditoría, cumplimiento normativo y gobierno corporativo.

---

## 💻 1. Acceso al Sistema

### Interfaz Principal (Open WebUI)
- **URL:** `http://localhost:3000`
- **Uso:** Consultas de chat, carga de documentos, creación de cuadernos/expedientes y consulta de citas legales.

### Panel de Control Administrativo (Plotly Dash)
- **URL:** `http://localhost:8050`
- **Uso:** Monitoreo del pipeline de conversión, auditoría inmutable, estado de la base de datos y métricas de calidad OCR.

---

## 📁 2. Gestión de Cuadernos / Expedientes (Estilo NotebookLM)

1. En **Open WebUI**, dirígete a la sección de **Workspaces / Cuadernos**.
2. Haz clic en **Crear Nuevo Cuaderno** y asigna un nombre al expediente (ej. `Auditoría Contratos 2026`).
3. El sistema asignará automáticamente un hash **SHA-256 inmutable** para garantizar la integridad y cadena de custodia documental.
4. Carga tus documentos normativos (`.pdf`, `.docx`, `.pptx`, `.xlsx`, `.txt`, `.csv`, `.html`, `.md`, `.epub` o imágenes escaneadas).

---

## 🔍 3. Realizar Consultas Jurídicas

Escribe tus preguntas normativas en el chat. JullBrain evaluará la evidencia documental recuperada y responderá bajo reglas estrictas:

- **Garantía Cero Alucinación:** El sistema responde **únicamente** con evidencia contenida en los expedientes cargados.
- **Citas Legales Obligatorias:** Cada respuesta incluirá la referencia exacta al Documento, Página, Capítulo, Artículo, Cláusula, Fragmento Literal y Nivel de Confianza (%).
- **Mensaje Fallback:** Si no existe suficiente evidencia documental en los archivos cargados, la plataforma indicará exactamente:
  > *"No encontré evidencia suficiente en los documentos cargados para responder esta pregunta."*
- **Aviso de Contradicciones:** Si dos normas o contratos se oponen entre sí, el sistema mostrará ambas citas con el aviso:
  > *"Se encontraron documentos con información contradictoria."*
