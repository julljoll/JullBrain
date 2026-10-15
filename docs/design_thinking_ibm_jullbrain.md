# 🎨 Marco Metodológico: Design Thinking & IBM Enterprise Design Thinking (DCU) en JullBrain Legal-RAG

![JullBrain IBM Design Thinking SVG](file:///c:/VS%20CODE/CODIGO/JullBrain/docs/design_thinking_ibm_jullbrain.svg)

---

## ⚖️ Introducción y Enfoque de Diseño Centrado en el Usuario (DCU / UCD)

El desarrollo del ecosistema **JullBrain Legal-RAG** adopta los principios internacionales de **Diseño Centrado en el Usuario** (ISO/IEC 9241-210) y el marco de trabajo **IBM Enterprise Design Thinking**. 

Dado que el dominio de aplicación abarca el **Sector Jurídico-Penal y la Informática Forense**, el sistema no busca sustituir el juicio reflexivo humano, sino acelerar la capacidad analítica de los operadores de justicia sin vulnerar la cadena de custodia ni arriesgar alucinaciones jurídicas (*Principio CNJ N.° 332/2020: "El sistema acelera, nunca decide ni sustituye la firma humana"*).

---

## 🔄 1. Las 5 Etapas Clásicas de Design Thinking aplicadas a JullBrain

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  1. EMPATIZAR   │───>│   2. DEFINIR    │───>│    3. IDEAR     │───>│  4. PROTOTIPAR  │───>│   5. EVALUAR    │
│   (Empathize)   │    │    (Define)     │    │    (Ideate)     │    │   (Prototype)   │    │     (Test)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 1. Empatizar (Empathize)
* **Objetivo:** Comprender las profundas fricciones cognitivas y operativas que enfrentan los **Jueces, Fiscales Penales, Defensores Públicos y Peritos Informáticos Forenses**.
* **Investigación & Artefactos:**
  * **Personas Jurídicas:** Identificación del *Fiscal Penal* (saturado por volúmenes masivos de folios), el *Perito Forense* (enfocado en integridad probatoria ISO 27037) y el *Juez de Juicio* (quien exige 100% certeza normativa sin desanclaje).
  * **Journey Maps:** Mapeo del flujo de revisión penal desde la ingesta del expediente hasta la redacción del proyecto de sentencia.
  * **Puntos de Dolor:** Temor justificado a las alucinaciones de modelos de lenguaje comerciales de "caja negra" y pérdida del rastreo de folios originales.
* **Líderes de Fase:** **R4** (Consultor UX/UI) + **R7** (IA Forense).

### 2. Definir (Define)
* **Objetivo:** Sintetizar la investigación en requerimientos claros, métricas de éxito e hipótesis de valor para el operador.
* **IBM Hills (Colinas de Valor):**
  * **Who (Quién):** Jueces y Fiscales Penales en fase de investigación o juzgamiento.
  * **What (Qué):** Auditar la precisión de citas legales y la consistencia de foliatura penal en menos de **3 segundos**.
  * **Wow (Resultado Asombroso):** 100% de trazabilidad computable con evidencia del PDF original highlighted y Semáforo Verde de confianza.
* **No Negociables:** Corpus cerrado versionado, abstención obligatoria si no existe respaldo normativo y ejecución 100% *Air-Gapped* (on-premise).
* **Líderes de Fase:** **R3** (Legaltech) + **R1** (Arquitecto IA).

### 3. Idear (Ideate)
* **Objetivo:** Co-diseñar soluciones técnicas y visuales que resuelvan el problema de la alucinación y garanticen auditabilidad.
* **Soluciones Arquitectónicas Diseñadas:**
  * **Chunking Atómico Legal:** Fragmentación estricta por artículo individual (IBM Docling + Regex Legalizer).
  * **Granite Embedding R2:** Modelo de embeddings vectoriales de alta densidad enfocado en jerarquías legales.
  * **Semáforo de Confianza Visual:** Interfaz UX con estado tricolor continuo (Verde = Anclado, Ámbar = Revisión Humana, Rojo = Alucinación/Desanclado).
* **Líderes de Fase:** **R1** (Arquitecto IA) + **R4** (UX/UI) + **R2** (Senior Fullstack).

### 4. Prototipar (Prototype)
* **Objetivo:** Construir los módulos funcionales ejecutables en Python nativo, Dash y RAGFlow.
* **Componentes Construidos:**
  * `metadata_extractor.py`: Extracción de YAML Frontmatter y Hash SHA-256 de evidencia.
  * `legalizer.py`: Estructuración jerárquica (TÍTULO / CAPÍTULO / Artículo).
  * `granite_embedder.py`: Motor de vectorización local con Ollama / Sentence-Transformers.
  * `validator.py`: Módulo de Doble Validación Cruzada (Regex vs. PyMuPDF) y auditoría.
  * `app.py`: Panel de Control Visual responsivo en Plotly Dash.
* **Líderes de Fase:** **R2** (Desarrollador Python Fullstack) + **R6** (Orquestador Pipeline).

### 5. Evaluar / Probar (Test)
* **Objetivo:** Auditar el rigor probatorio, la tasa de alucinación y la usabilidad en vivo.
* **Métricas y Protocolos:**
  * **Doble Validación Cruzada:** Comparación de conteo de artículos entre el Markdown legalizado y la extracción directa del PDF original vía PyMuPDF (Error Cero).
  * **Rúbrica Stanford RegLab:** Clasificación de respuestas según fabricación vs. desanclaje (*misgrounding*).
  * **Protocolo Think-Aloud:** Pruebas de usabilidad en tiempo real con operadores jurídicos simulando un juicio penal.
  * **Auditoría Forense R7:** Inspección de la foliatura y cadena de custodia documental.
* **Líderes de Fase:** **R5** (Agile Facilitador) + **R7** (IA Forense) + **R3** (Legaltech).

---

## 🔁 2. El Bucle Continuo de IBM (The Loop)

```
        ┌───────────────────────────┐
        │    1. OBSERVAR (Observe)  │
        │ Ingesta & Feedback Real   │
        └─────────────┬─────────────┘
                      │
                      ▼
        ┌───────────────────────────┐
        │   2. REFLEXIONAR (Reflect)│
        │  Alineación Roles R1-R7   │
        └─────────────┬─────────────┘
                      │
                      ▼
        ┌───────────────────────────┐
        │      3. HACER (Make)      │
        │ Prototipado & Semáforo UI │
        └─────────────┬─────────────┘
                      │
                      └──── Lazo de Retroalimentación Continua ────┘
```

1. **Observe (Observar):** Recopilación incesante de datos del expediente, actas penal y retroalimentación de los jueces durante la simulación de consultas jurídicas.
2. **Reflect (Reflexionar):** Alineación del equipo multidisciplinario en Sprints quincenales (Scrum/Kanban). Evaluación obligatoria de la columna Kanban **"Verificación Anti-Alucinación"** antes de dar por completada cualquier historia.
3. **Make (Hacer):** Desarrollo rápido de mejoras en el dashboard de Plotly Dash, ajustes en la temperatura de inferencia del LLM (Granite) y refinamiento de las regex de partición.

---

## 🔑 3. Las Tres Llaves de IBM (IBM Keys)

| Llave IBM | Definición | Implementación en JullBrain |
| :--- | :--- | :--- |
| 🏔️ **Hills (Colinas)** | Objetivos enfocados en el valor del usuario (*Who, What, Wow*). | **Quién:** Jueces/Fiscales.<br>**Qué:** Verificar citas y folios en &lt; 3 seg.<br>**Wow:** 100% trazabilidad visual con Semáforo Verde y PDF sincronizado. |
| 🎬 **Playbacks** | Demostraciones continuas para alinear expectativas. | Presentaciones quincenales ante jurados académicos y peritos para certificar la transparencia del RAG y evitar el sesgo de caja negra. |
| 🤝 **Sponsor Users** | Integración del usuario final en el diseño. | Co-diseño directo con Peritos Informáticos y Fiscales que prueban y validan la interfaz antes de cada versión. |

---

## 🖥️ 4. Capa de Interfaz UX/UI: El Semáforo de Confianza Jurídica

La interfaz de usuario del dashboard (`app.py`) aplica el principio de **Transparencia Algorítmica**, clasificando las afirmaciones generadas en tres niveles visuales sin ambigüedad:

* 🟢 **VERDE — ANCLADO (100% Preciso):** La cita legal existe textualmente en el corpus normativo cerrado o en el expediente. Enlace directo al PDF con resalte.
* 🟡 **ÁMBAR — REVISIÓN HUMANA (Requiere Confirmación):** Existe ambigüedad interpretativa o divergencia en criterios jurisprudenciales (confianza 70%-89%). El sistema solicita verificación explícita del operador.
* 🔴 **ROJO — DESANCLADO / ALUCINACIÓN (Bloqueo Automático):** La cita o antecedente no fue hallado en el corpus. El sistema se abstiene de inyectar el texto en proyectos de resolución.

---

## 👥 5. Matriz de Roles Multidisciplinarios (R1 a R7)

* **R1 — Arquitecto IA / LLM Senior:** Diseño del pipeline RAG, cuantización/despliegue de Granite 3B/8B/30B y arquitectura air-gapped.
* **R2 — Desarrollador Python Fullstack:** Implementación del código modular (`metadata_extractor`, `legalizer`, `granite_embedder`, `validator`) y Dash UI.
* **R3 — Especialista en Legaltech:** Respaldo normativo venezolano (COPP, LOCTI, Infogobierno), ISO 42001 e ISO 25010.
* **R4 — Consultor UX/UI DCU (Líder IBM EDT):** Personas jurídicas, Journey Maps, Wireframes Figma y diseño del Semáforo de Confianza.
* **R5 — Facilitador de Metodologías Ágiles:** Sprints quincenales, Backlog y columna Kanban de verificación anti-alucinación.
* **R6 — Orquestador del Agente:** Coordinación armónica e integración de los roles R1 a R5 y R7.
* **R7 — Experto en IA Forense y Procesos Penal:** Auditoría de cadena de custodia (ISO 27037), consistencia de foliatura penal e integridad documental.

---

> [!TIP]
> **Archivo SVG Generado:** El diagrama vectorial interactivo se encuentra disponible en [`docs/design_thinking_ibm_jullbrain.svg`](file:///c:/VS%20CODE/CODIGO/JullBrain/docs/design_thinking_ibm_jullbrain.svg).
