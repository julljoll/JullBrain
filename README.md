# ⚖️ JullBrain V-2.0 — Legal-RAG & Informática Forense

> **Plataforma Enterprise de Inteligencia Documental Legal especializada en normativas, auditoría forense y control judicial venezolano. Operación dual: 100% LOCAL NATIVO OFFLINE (Air-Gapped) y aceleración en la nube con GOOGLE COLAB (GPU T4 gratuita). Impulsada por IBM Granite 3.3 8B, IBM Docling, Hierarchical Chunking y validación criptográfica SHA-256.**

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/julljoll/JullBrain/blob/main/JullBrain_Colab.ipynb)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://python.org)
[![Licencia Apache 2.0](https://img.shields.io/badge/Licencia-Apache%202.0-blue.svg)](LICENSE)
[![IBM Granite](https://img.shields.io/badge/IBM-Granite%203.3%208B-purple.svg)](https://huggingface.co/ibm-granite)
[![IBM Docling](https://img.shields.io/badge/Engine-IBM%20Docling-green.svg)](https://github.com/docling-project/docling)
[![Air-Gapped](https://img.shields.io/badge/Security-100%25%20Air--Gapped-success.svg)](#)

---

## 🏛️ Descripción General

**JullBrain V-2.0** transforma leyes complejas (Constitución, Códigos, Gacetas Oficiales, Resoluciones y Manuales Forenses) en una base de conocimientos estructurada con estricto control de jerarquía jurídica y cero alucinaciones.

### 🌟 Pilares de la Arquitectura:

1. **Operación 100% Local Nativa (Air-Gapped):** Sin dependencias de Docker ni Podman. Corre nativamente en Python con entorno virtual local (`docling_env`) garantizando que ninguna evidencia o consulta salga a internet.
2. **Interfaz Web HTML5/CSS3 Unificada (`http://localhost:8050`):** Centro de operaciones visual con modo oscuro cyber-legal, consola de terminal en tiempo real, gestor de subida de PDFs con cálculo previo de SHA-256 en cliente, y asistente RAG interactivo.
3. **Aceleración Google Colab en 1 Clic:** Cuaderno interactivo [`JullBrain_Colab.ipynb`](JullBrain_Colab.ipynb) listo para procesar volúmenes masivos de leyes utilizando GPU NVIDIA T4 gratuita en la nube.
4. **Motor Híbrido Local Autónomo:** Búsqueda Léxica BM25 + Búsqueda Vectorial por Similitud Coseno con NumPy + Fusión Recíproca de Rangos (RRF) + Cross-Encoder Reranker sin necesidad de levantar clústeres externos.
5. **Cadena de Custodia e Integridad Forense:** Firma criptográfica inmutable **SHA-256** por expediente y doble validación cruzada PDF vs Markdown (Principio de Error Cero).
6. **Reglas RAG Estrictas Anti-Alucinación:** `temperature=0.0`, verificación de citas obligatoria y guardrail de seguridad con IBM Granite Guardian.

---

## 🛠️ Estructura del Repositorio

```text
JullBrain/
├── app.py                         # Backend API REST FastAPI y Servidor Web HTML5
├── web/                           # Interfaz Web Unificada (HTML5, CSS3 Cyber-Legal, JS)
│   ├── index.html                 # Centro de Control, Drag-and-Drop y Consultas RAG
│   ├── styles.css                 # Diseño moderno Dark Mode con acentos verde y dorado
│   └── app.js                     # Lógica cliente, cálculo SHA-256 y streaming de logs
├── JullBrain_Colab.ipynb          # Cuaderno Jupyter oficial para Google Colab con GPU T4
├── orquestador_JullBrain.bat      # Lanzador y Centro de Control nativo para Windows
├── convert_normativas.py          # Ingesta con IBM Docling + Hierarchical Chunking
├── legalizer.py                   # Jerarquía legal venezolana (Libro, Título, Capítulo, Artículo)
├── metadata_extractor.py         # Extracción de YAML Frontmatter y SHA-256
├── validator.py                   # Doble validación cruzada PDF vs MD y reporte de calidad
├── granite_embedder.py            # Embeddings semánticos con IBM Granite Embedding R2
├── granite_guardian_guardrail.py # Guardrails de seguridad y auditoría de anclaje
├── opensearch_indexer.py         # Motor Híbrido Local (BM25 + Vectores NumPy + RRF + Reranker)
├── notebook_manager.py            # Gestor de Cuadernos/Expedientes con firma SHA-256
├── audit_logger.py                # Registro inmutable de eventos y trazabilidad forense
├── openwebui_pipeline.py          # Integración directa con Open WebUI API
├── pipeline_config.json           # Configuración técnica persistente del sistema
├── requirements.txt               # Dependencias Python de producción
├── tests/                         # Suite de QA Testing (Unit, Integration, Air-Gapped)
│   ├── test_qa_offline.py         # 14 pruebas de jerarquía, hashes, búsqueda híbrida y guardrail
│   ├── test_unit.py               # Pruebas unitarias de endpoints y almacenamiento
│   └── test_integration.py        # Pruebas de integración del pipeline RAG
└── docs/                          # Manuales de Arquitectura, Usuario y Guías Forenses
```

---

## 🚀 Puesta en Marcha Rápida en Local (Windows / Linux)

### En Windows:
Basta con hacer doble clic en el archivo orquestador:
```cmd
orquestador_JullBrain.bat
```
El orquestador activará automáticamente el entorno virtual `docling_env` y abrirá la **Interfaz Web HTML5** en tu navegador (`http://localhost:8050`).

### En Linux / Mac o Terminal Manual:
```bash
# 1. Crear y activar entorno virtual
python -m venv docling_env
source docling_env/bin/activate  # En Windows: docling_env\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Iniciar el Centro de Control Web
python app.py
```
Abre tu navegador en: **`http://localhost:8050`**

---

## ☁️ Ejecución en Google Colab desde GitHub

Para procesar leyes pesadas con GPU NVIDIA T4 gratuita sin gastar recursos de tu máquina local:

1. Haz clic en el botón superior **[Open In Colab](https://colab.research.google.com/github/julljoll/JullBrain/blob/main/JullBrain_Colab.ipynb)**.
2. En Google Colab, selecciona en el menú: `Entorno de ejecución` > `Cambiar tipo de entorno de ejecución` > **GPU T4**.
3. Ejecuta las celdas secuencialmente para clonar el repositorio, instalar dependencias, estructurar leyes con IBM Docling y correr consultas RAG.

---

## 🧪 Control de Calidad (QA Testing Air-Gapped)

Para certificar la integridad del sistema en modo 100% desconectado:

```bash
python -m unittest discover tests
```
*Garantiza:*
- ✅ Jerarquía normativa y separación atómica de artículos (COPP, Leyes Especiales).
- ✅ Detección inmediata de alteración o manipulación de expedientes (SHA-256).
- ✅ Búsqueda Híbrida local en memoria y persistencia en disco con 0 ms de retardo.
- ✅ Resistencia ante inyecciones de prompt mediante IBM Granite Guardian.
- ✅ Cero alucinaciones y abstención explícita ante hechos no probados.
- ✅ Aislamiento estricto *air-gapped* sin peticiones salientes de red.

---

## 📄 Licencia

Distribuido bajo la **Licencia Apache 2.0**. Consulte el archivo [LICENSE](LICENSE) para más detalles.
