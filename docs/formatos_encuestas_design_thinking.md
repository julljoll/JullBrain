# 🎨 Formatos de Investigación UX y Design Thinking — JullBrain Legal-RAG

## 📌 Sustentación de las Primeras Etapas (Comprender, Empatizar y Definir el Problema)

Para fundamentar rigurosamente el diseño centrado en el usuario (DCU) y certificar la adopción del sistema **JullBrain Legal-RAG** ante jurados universitarios e instituciones judiciales, se crearon **3 formatos visuales vectoriales en SVG** basados en **3 técnicas distintas e independientes** de recolección de datos de campo.

---

## 🛠️ Los 3 Formatos y Técnicas Creadas

### 1. 📊 Formato 1: Encuesta Cuantitativa/Cualitativa de Fricción Operativa (Escala Likert & Priorización)
* **Imagen SVG**: [`docs/encuesta_dt_1_cuestionario_empatia.svg`](file:///c:/VS%20CODE/CODIGO/JullBrain/docs/encuesta_dt_1_cuestionario_empatia.svg)
* **Técnica UX**: **Encuesta de Fricción Operativa y Ranking de Dolores de Usuario (Likert 1-5 + Priorización 1-4)**.
* **Propósito**: Cuantificar la carga de trabajo manual, los tiempos perdidos en la lectura física de expedientes, la frecuencia de diferimiento de audiencias preliminares y los requerimientos mínimos de confianza del operador de justicia.
* **Roles a Evaluar**: Jueces de Control, Fiscales del Ministerio Público, Defensores Públicos y Secretarios de Sala.
* **Secciones**:
  * **Sección A**: 4 preguntas diagnósticas en Escala Likert de 5 puntos (Tiempo dedicado a lectura, frecuencia de diferimientos por vicios de foliatura, fricción en cálculo manual de penas Art. 375 COPP, utilidad del informe previo).
  * **Sección B**: Matriz de ranking de 4 Puntos de Dolor principales (Vicios de Foliatura, Admisibilidad Probatoria, Cómputo de Penas Manual, Temor a Alucinación en IA).
  * **Sección C**: Preguntas cualitativas de respuesta abierta sobre garantías mínimas de anclaje normativo y experiencia de uso.

---

### 2. 🧠 Formato 2: Mapa de Empatía del Operador de Justicia (IBM Enterprise Design Thinking Template)
* **Imagen SVG**: [`docs/encuesta_dt_2_mapa_empatia_juridico.svg`](file:///c:/VS%20CODE/CODIGO/JullBrain/docs/encuesta_dt_2_mapa_empatia_juridico.svg)
* **Técnica UX**: **Mapa de Empatía de 6 Cuadrantes (IBM Enterprise Design Thinking)**.
* **Propósito**: Mapear la experiencia holística, cognitiva y emocional del operador durante simulaciones de audiencia o sesiones con prototipos navegables (Protocolo *Think-Aloud*).
* **Estructura de Cuadrantes**:
  1. **¿Qué Piensa y Siente?**: Preocupaciones por la dignidad humana, retardo procesal y temor a alucinaciones o citas inexactas.
  2. **¿Qué Ve?**: Entorno con carpetas físicas abultadas, hojas sueltas, defensores en espera y pantallas saturadas.
  3. **¿Qué Oye?**: Exigencias del TSJ para agilizar causas, quejas de imputados y advertencias sobre vicios formales.
  4. **¿Qué Dice y Hace?**: Diferimientos obligados por foliaturas enmendadas, cálculos en borrador y defensa de la justicia expedita (CRBV Art. 26).
  5. **PAINS (Frustraciones y Dolores)**: Pérdida de horas útiles de despacho, inseguridad de cómputo manual y rechazo a cajas negras.
  6. **GAINS (Resultados Anhelados)**: Capacidad de despachar 8-10 audiencias/día con Semáforo Verde (100% anclado) e informe en 1 clic.

---

### 3. 🗺️ Formato 3: Mapa de Viaje del Usuario Procesal (As-Is User Journey Map & Auditoría)
* **Imagen SVG**: [`docs/encuesta_dt_3_user_journey_asis.svg`](file:///c:/VS%20CODE/CODIGO/JullBrain/docs/encuesta_dt_3_user_journey_asis.svg)
* **Técnica UX**: **User Journey Mapping Procesal ("As-Is" vs "To-Be") y Auditoría de Tiempos**.
* **Propósito**: Trazar el recorrido paso a paso de la carpeta penal física desde su ingesta en URDD hasta la emisión del Auto de Apertura a Juicio o Sobreseimiento.
* **5 Etapas Mapeadas**:
  1. **Ingesta en URDD** (Recepción de acusación física, estampado de sellos).
  2. **Auditoría y Foliado en Sala** (Foliación a mano por el Secretario, cosido con pabilo).
  3. **Notificaciones y Boletas** (Envío de boletas de traslado a retenes; *punto crítico de diferimiento*).
  4. **Audiencia Preliminar (COPP Art. 309)** (Debate probatorio, revisión a contrarreloj y cálculo de pena).
  5. **Emisión de Auto y Sentencia** (Redacción, tipejo manual de datos y firma del fallo).
* **Dimensiones por Etapa**: Acción del Operador, Artefacto Utilizado, Curva Emocional (😊/😐/😩), Puntos de Dolor y **Oportunidad de Intervención RAG** (Filtros F1 a F4).

---

## 🚦 Aplicación Práctica en la Fase de Validación

```
┌──────────────────────────────┐
│  FORMATO 1: CUESTIONARIO     │ ──> Levanta Métricas Cuantitativas Iniciales (Fase 01)
└──────────────────────────────┘
               │
               ▼
┌──────────────────────────────┐
│  FORMATO 2: MAPA DE EMPATÍA  │ ──> Captura Sesiones Think-Aloud con Prototipo (Fase 01-02)
└──────────────────────────────┘
               │
               ▼
┌──────────────────────────────┐
│  FORMATO 3: USER JOURNEY     │ ──> Identifica Cuellos de Botella As-Is y Oportunidades RAG (Fase 02)
└──────────────────────────────┘
```

1. **Protocolo Think-Aloud (Fase 01)**: El evaluador le entrega el prototipo interactivo (Plotly Dash / HTML) al Juez o Fiscal y utiliza el **Formato 2** para registrar en notas adhesivas sus expresiones verbales instantáneas.
2. **Auditoría de Tiempos (Fase 02)**: Se utiliza el **Formato 3** junto al Secretario de Sala para comparar los tiempos de foliado manual vs la aceleración RAG con `validator.py`.
3. **Justificación Constitucional e ISO**: Todas las observaciones recolectadas alimentan la Matriz de Requerimientos bajo los estándares **ISO/IEC 29148** (Ingeniería de Requisitos) e **ISO 9241-210** (Diseño Centrado en el Usuario).
