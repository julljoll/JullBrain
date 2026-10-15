# ANTEPROYECTO DE LEY ESPECIAL DE CIBERSEGURIDAD PROCESAL E INTEGRIDAD DEL SISTEMA DE JUSTICIA

**República Bolivariana de Venezuela**
**Documento técnico-jurídico de trabajo académico — versión sectorial**

*Reestructuración del "Anteproyecto de Ley Orgánica de Ciberseguridad, Integridad Institucional y Transformación Digital del Estado" para operar como regulación sectorial, acotada al sistema de justicia y a los actos procesales, en lugar de como ley marco transversal a todo el Estado.*

Elaborado con base en:
- Reglamento (UE, Euratom) 2023/2841 (arquitectura de CERT-EU y de la Junta Interinstitucional de Ciberseguridad, adaptada a escala sectorial).
- Boletín *Cybersecurity Basics for Courts*, Joint Technology Committee — COSCA/NACM/NCSC (2025), documento cuyo objeto ya es, en sí mismo, sectorial-judicial.
- Constitución de la República Bolivariana de Venezuela.
- ISO/IEC 27037, 27041, 27042, 27043 (informática forense); RFC 3227; NIST SP 800-86; ISO/IEC 27001, 27035; ISO 37301, 37001; ISO/IEC 42001, 23894.
- Manual Único de Cadena de Custodia de Evidencias (Venezuela, versión final 29-09-2017).

---

## NOTA METODOLÓGICA: QUÉ CAMBIÓ RESPECTO DE LA VERSIÓN GENERAL

| Elemento | Versión general (ley orgánica marco) | Versión sectorial (este documento) |
|---|---|---|
| **Naturaleza** | Ley orgánica transversal a todo el Estado | Ley especial sectorial, propia del sistema de justicia |
| **Ámbito subjetivo** | Los tres Poderes, Poder Ciudadano, Poder Electoral, infraestructura crítica nacional (energía, banca, salud, transporte) | Poder Judicial, Ministerio Público, Defensa Pública, órganos auxiliares de justicia, proveedores tecnológicos del sistema de justicia |
| **Órgano rector** | SUNACIB, autoridad nacional de ciberseguridad para todo el Estado | Dirección Nacional de Ciberseguridad Procesal (DINCIP), órgano técnico del propio sistema de justicia |
| **Procesos de riesgo prioritario (Título VII)** | 8 procesos transversales (contratación pública general, nómina de toda la administración, permisos, aduanas, causas judiciales) | Acotados a los procesos **procesales y de administración de justicia**: causas, evidencia, nómina judicial, ascensos de jueces/fiscales, notificaciones |
| **Relación con infraestructura crítica nacional (energía, salud, banca)** | Objeto directo de la ley | Excluida; queda fuera del ámbito sectorial |
| **Relación con una eventual ley general de ciberseguridad del Estado** | N/A (es la ley general) | Se declara **subsidiaria y de aplicación preferente** para el sector justicia; si existe una ley general posterior, esta opera como *lex specialis* (art. 3°) |

El resultado es un instrumento que puede tramitarse y aprobarse de forma autónoma —sin depender de que exista una ley general de ciberseguridad del Estado— y cuyo objeto encaja con precisión en la categoría **"regulación sectorial sobre ciberseguridad procesal"**.

---

## EXPOSICIÓN DE MOTIVOS

El sistema de justicia venezolano —integrado por el Poder Judicial, el Ministerio Público y la Defensa Pública— gestiona información especialmente sensible: expedientes penales, evidencia digital, datos de víctimas y de investigados, y actos procesales cuya integridad condiciona directamente el debido proceso consagrado en el artículo 49 constitucional. La experiencia documentada por el Joint Technology Committee (COSCA-NACM-NCSC) en su boletín *Cybersecurity Basics for Courts* (2025) —que registra ataques de ransomware contra tribunales de Los Ángeles (julio 2024), Cleveland (febrero-marzo 2025) y la Administrative Office of the U.S. Courts (2025)— confirma que los sistemas judiciales constituyen un objetivo de alto valor para actores maliciosos, y que su defensa requiere una gobernanza técnica propia, distinta de la de otros sectores del Estado.

Al mismo tiempo, los procesos internos del sistema de justicia —la distribución de causas, la custodia de la evidencia, los ascensos y traslados de jueces y fiscales— han sido históricamente señalados como puntos de vulnerabilidad frente a la corrupción y la influencia indebida. Este instrumento busca, con un objeto **sectorial y acotado**, lo que una ley general del Estado abordaría de forma dispersa: dotar específicamente al sistema de justicia de ciberseguridad procesal, régimen probatorio digital robusto y mecanismos de automatización que reduzcan la discrecionalidad no controlada en sus procesos internos de mayor riesgo.

Se adoptan como referencia técnica las normas ISO/IEC 27037, 27041, 27042 y 27043 (informática forense), RFC 3227 y NIST SP 800-86 (recolección y preservación de evidencia digital), ISO/IEC 27001 y 27035 (gestión de seguridad de la información e incidentes) y, para el componente de integridad institucional propio de esta propuesta, ISO 37301, ISO 37001, ISO/IEC 42001 e ISO/IEC 23894.

En ejercicio de la iniciativa legislativa prevista en el artículo 204 constitucional —que habilita al Tribunal Supremo de Justicia a presentar proyectos de ley relativos a la organización y procedimientos judiciales—, se somete a consideración de la Asamblea Nacional el siguiente:

---

## LA ASAMBLEA NACIONAL DE LA REPÚBLICA BOLIVARIANA DE VENEZUELA DECRETA

la siguiente,

# LEY ESPECIAL DE CIBERSEGURIDAD PROCESAL E INTEGRIDAD DEL SISTEMA DE JUSTICIA

---

## TÍTULO I. DISPOSICIONES GENERALES

**Artículo 1°. Objeto.**
Esta Ley tiene por objeto regular la ciberseguridad de los sistemas de información que soportan la función jurisdiccional y de investigación penal, establecer el régimen de integridad, trazabilidad y valor probatorio de la evidencia y los actos digitales del sistema de justicia, y crear un régimen especial de integridad procesal que reduzca, mediante automatización y auditoría continua, la discrecionalidad humana no controlada en los procesos internos del sistema de justicia estructuralmente vulnerables a la corrupción o a la influencia indebida.

**Artículo 2°. Ámbito de aplicación (sectorial).**
Esta Ley se aplica exclusivamente a: 1) el Poder Judicial, incluyendo al Tribunal Supremo de Justicia y todos los circuitos y tribunales de la República; 2) el Ministerio Público; 3) la Defensa Pública; 4) los órganos auxiliares de justicia con funciones periciales, de custodia de evidencia o de registro procesal (peritos informáticos forenses, depósitos judiciales, oficinas de alguacilazgo); y 5) las personas naturales o jurídicas de derecho privado que provean bienes, servicios o infraestructura tecnológica a los sujetos anteriores. Quedan fuera del ámbito de esta Ley los procesos administrativos generales de otros Poderes Públicos, la infraestructura crítica no vinculada a la función judicial, y cualquier materia que corresponda a una eventual ley general de ciberseguridad del Estado.

**Artículo 3°. Relación con otros instrumentos (cláusula de especialidad).**
Esta Ley es de aplicación preferente, por razón de la materia, sobre cualquier ley general de ciberseguridad del Estado que exista o llegare a dictarse, en todo lo relativo a los sujetos y procesos descritos en el artículo 2°, sin perjuicio de la aplicación supletoria de dicha ley general en lo no previsto aquí. Esta Ley no deroga ni sustituye a la Ley Especial contra los Delitos Informáticos, a la Ley de Infogobierno ni a la Ley Orgánica de Amparo sobre Derechos y Garantías Constitucionales, con las cuales se articula.

**Artículo 4°. Principios rectores.**
Rigen esta Ley los principios de legalidad, proporcionalidad, debido proceso, contradicción, seguridad jurídica, trazabilidad, preservación forense continua, mínima intervención humana en lo reglado, y supervisión humana significativa sobre todo sistema automatizado o de inteligencia artificial que produzca efectos sobre un proceso judicial o disciplinario.

**Artículo 5°. Definiciones.**
A los efectos de esta Ley se entiende por:
1. **Ciberseguridad procesal**: conjunto de controles técnicos y organizativos orientados a proteger la confidencialidad, integridad, disponibilidad y trazabilidad de los sistemas de información que soportan actos procesales.
2. **Acto procesal digital**: toda actuación judicial, fiscal o de defensa pública generada, tramitada o registrada por medios electrónicos (auto, sentencia, notificación, diligencia, dictamen pericial).
3. **Sistema de gestión de causas**: plataforma que registra, distribuye y da seguimiento a los expedientes judiciales o fiscales.
4. **Cadena de custodia digital**: procedimiento documentado que garantiza integridad, autenticidad y trazabilidad de la evidencia digital desde su recolección hasta su valoración judicial.
5. **Registro inmutable procesal**: bitácora electrónica protegida criptográficamente que documenta cada acto procesal digital, inalterable incluso por el administrador técnico del sistema.
6. **Preparación forense continua (*forensic readiness*)**: diseño de los sistemas judiciales para preservar automáticamente evidencia digital idónea desde su origen.
7. **CSIRT-Justicia**: equipo técnico especializado de respuesta a incidentes de ciberseguridad del sistema de justicia.

---

## TÍTULO II. INSTITUCIONALIDAD SECTORIAL

### Capítulo I. Dirección Nacional de Ciberseguridad Procesal (DINCIP)

**Artículo 6°. Creación y naturaleza.**
Se crea la Dirección Nacional de Ciberseguridad Procesal (DINCIP), adscrita al Tribunal Supremo de Justicia, con autonomía técnica y funcional, y con relación de coordinación —no de subordinación— con el Ministerio Público y la Defensa Pública, a fin de garantizar su competencia sobre la totalidad del sistema de justicia sin depender de un solo Poder.

**Artículo 7°. Atribuciones.**
Corresponde a la DINCIP: 1) dictar los estándares técnicos de ciberseguridad exigibles a los sistemas de gestión de causas, custodia de evidencia y videoconferencia judicial; 2) coordinar al CSIRT-Justicia; 3) llevar el Registro Nacional de Peritos Informáticos Forenses; 4) ejercer la Oficina de Cumplimiento Digital del Sistema de Justicia prevista en el Título VII; 5) certificar los sistemas de distribución aleatoria de causas; y 6) rendir informe anual público a la Asamblea Nacional y a la Contraloría General de la República.

### Capítulo II. CSIRT-Justicia

**Artículo 8°. Creación y funciones.**
Se crea el CSIRT-Justicia como equipo técnico responsable de la detección, contención, erradicación y recuperación frente a incidentes cibernéticos que afecten al sistema de gestión de causas, la custodia de evidencia digital y los servicios de videoconferencia judicial, en atención a la exposición documentada de los tribunales frente al ransomware (Los Ángeles, julio 2024; Cleveland, febrero-marzo 2025; Administrative Office of the U.S. Courts, 2025).
*Fuente/base normativa: JTC, Cybersecurity Basics for Courts (2025), secciones "State of Cybersecurity in Courts" y "Assembling a Cybersecurity Incident Response Team (CIRT)".*

**Artículo 9°. Ejercicios y capacidades.**
El CSIRT-Justicia realizará ejercicios de simulación al menos dos veces al año y mantendrá un inventario actualizado de capacidades técnicas disponibles en cada circuito judicial y sede fiscal.

### Capítulo III. Junta de Integridad Procesal

**Artículo 10°. Composición y funciones.**
Se crea la Junta de Integridad Procesal, integrada por un representante del Tribunal Supremo de Justicia, uno del Ministerio Público, uno de la Defensa Pública, uno de la Contraloría General de la República y el Director de la DINCIP, quien la coordina. Aprueba la taxonomía de severidad de incidentes del sistema de justicia, el plan de gestión de crisis cibernéticas sectorial y los protocolos operativos estándar de respuesta.
*Fuente/base normativa: Reglamento (UE, Euratom) 2023/2841, art. 23 (adaptado a escala sectorial).*

---

## TÍTULO III. ESTÁNDARES TÉCNICOS APLICABLES A LOS SISTEMAS DEL SISTEMA DE JUSTICIA

**Artículo 11°. Adopción de estándares.**
Los sistemas de gestión de causas, custodia de evidencia, videoconferencia judicial y notificación electrónica implementarán un Sistema de Gestión de Seguridad de la Información conforme a ISO/IEC 27001, con referencia complementaria en ISO/IEC 27035 (gestión de incidentes) e ISO 22301 (continuidad).

**Artículo 12°. Controles mínimos.**
Dichos sistemas implementarán, como mínimo: autenticación multifactor para jueces, fiscales, defensores y personal con acceso a expedientes; principio de mínimo privilegio; segmentación de red respecto de otros sistemas administrativos no judiciales; y cifrado en tránsito y en reposo de los expedientes electrónicos.
*Fuente/base normativa: JTC (2025), secciones "Least Privilege Access" y "Zero Trust Principles".*

**Artículo 13°. Continuidad operativa judicial.**
Cada circuito judicial y sede fiscal contará con un Plan de Continuidad de Operaciones que garantice, ante un incidente cibernético, la disponibilidad de mecanismos alternos de tramitación de causas urgentes (medidas cautelares, habeas corpus, flagrancia), sin dependencia exclusiva de plataformas digitales comprometidas.
*Fuente/base normativa: JTC (2025), sección "Cybersecurity as Part of a COOP".*

---

## TÍTULO IV. DEBIDO PROCESO Y GARANTÍAS EN EL ENTORNO DIGITAL

**Artículo 14°. Debido proceso y prueba electrónica.**
En toda actuación en que se emplee evidencia digital deberá garantizarse el derecho a la defensa, el acceso a las pruebas y el contradictorio, conforme al artículo 49 constitucional. La evidencia digital solo será admisible cuando conste su cadena de custodia conforme al Título VI.

**Artículo 15°. Supervisión humana significativa.**
Ninguna decisión jurisdiccional, fiscal o disciplinaria podrá fundarse exclusivamente en la salida de un sistema automatizado o de inteligencia artificial, sin intervención, revisión y motivación de un juez, fiscal o funcionario competente identificado, quien asume la responsabilidad del acto.

**Artículo 16°. Protección de datos de las partes.**
El tratamiento de datos personales de las partes, víctimas e investigados en los sistemas judiciales observará los principios de licitud, finalidad, minimización y limitación del plazo de conservación, conforme al artículo 28 constitucional.

---

## TÍTULO V. GESTIÓN DE INCIDENTES DEL SISTEMA DE JUSTICIA

**Artículo 17°. Obligación de notificación.**
Todo circuito judicial, fiscalía o dependencia de la Defensa Pública notificará al CSIRT-Justicia cualquier incidente significativo dentro de las veinticuatro (24) horas siguientes a su detección, y presentará informe final dentro de los treinta (30) días continuos siguientes.

**Artículo 18°. Taxonomía de severidad.**
La Junta de Integridad Procesal aprobará una taxonomía común de severidad de incidentes aplicable uniformemente a todo el sistema de justicia.

---

## TÍTULO VI. RÉGIMEN PROBATORIO Y PERITAJE INFORMÁTICO FORENSE (núcleo sectorial de esta Ley)

**Artículo 19°. Cadena de custodia digital.**
La recolección, preservación, embalaje, transporte, análisis y presentación de evidencia digital se realizará conforme a ISO/IEC 27037 (identificación, recolección, adquisición y preservación), ISO/IEC 27041 (idoneidad de métodos), ISO/IEC 27042 (análisis e interpretación) e ISO/IEC 27043 (principios de investigación), en concordancia con el Manual Único de Cadena de Custodia de Evidencias vigente.

**Artículo 20°. Orden de volatilidad.**
La recolección observará el orden de volatilidad de las fuentes —de mayor a menor: memoria y conexiones activas, procesos en ejecución, almacenamiento temporal, medios persistentes, respaldos remotos u offline—, conforme a RFC 3227 y NIST SP 800-86.

**Artículo 21°. Registro Nacional de Peritos Informáticos Forenses.**
La DINCIP llevará el Registro Nacional de Peritos Informáticos Forenses, certificando su idoneidad técnica como auxiliares de justicia, sin perjuicio de las facultades del Ministerio Público y del Poder Judicial.

**Artículo 22°. Preparación forense continua.**
Los sistemas de gestión de causas y custodia de evidencia se diseñarán bajo el principio de preparación forense continua (ISO/IEC 27043), de modo que la evidencia de cualquier acto procesal se preserve automáticamente en condiciones aptas para su valoración judicial.

**Artículo 23°. Valor probatorio de registros electrónicos.**
Los registros electrónicos generados por sistemas certificados conforme a esta Ley, protegidos mediante función hash y sello de tiempo, harán fe salvo prueba en contrario, sin menoscabo del derecho de la contraparte a impugnar su autenticidad conforme al artículo 49 constitucional.

---

## TÍTULO VII. INTEGRIDAD PROCESAL: AUTOMATIZACIÓN ANTICORRUPCIÓN APLICADA AL SISTEMA DE JUSTICIA

> **Aporte diferenciador de esta versión sectorial.** El Título VII no pretende ya automatizar procesos generales del Estado (contratación pública de cualquier ente, nómina de toda la administración), sino, de forma acotada y coherente con el objeto sectorial de esta Ley, **los procesos internos del propio sistema de justicia** donde la discrecionalidad no controlada ha sido históricamente señalada como fuente de riesgo: la asignación de causas, la custodia de la evidencia y la carrera judicial y fiscal.

**Artículo 24°. Procesos de riesgo prioritario del sistema de justicia.**
Se declaran procesos de riesgo prioritario, sujetos a automatización obligatoria: 1) la distribución y asignación aleatoria de causas judiciales y fiscales; 2) la custodia y cadena de evidencia física y digital; 3) los procesos de ascenso, traslado y evaluación de jueces, fiscales y defensores públicos; 4) las notificaciones y actos de comunicación procesal; 5) la contratación de bienes y servicios tecnológicos propios del sistema de justicia; y 6) la administración de nómina y beneficios del personal judicial y fiscal.

**Artículo 25°. Oficina de Cumplimiento Digital del Sistema de Justicia.**
Se crea, dentro de la DINCIP, la Oficina de Cumplimiento Digital del Sistema de Justicia, que opera de forma continua motores de análisis de datos e inteligencia artificial para la detección de anomalías y señales de alerta temprana en los procesos del artículo 24°, conforme a ISO 37301 e ISO 37001.

**Artículo 26°. Distribución aleatoria de causas mediante sistema certificado.**
La asignación de causas se realizará mediante un sistema de distribución aleatoria certificado por la DINCIP, cuyo algoritmo será público, auditable y generará un registro inmutable de cada asignación, sin intervención manual salvo recusación, inhibición o impedimento debidamente motivados.

**Artículo 27°. Segregación de funciones programática.**
Ningún funcionario del sistema de justicia podrá, por sí solo, iniciar, aprobar y ejecutar una misma operación crítica dentro de los procesos del artículo 24° (principio de "cuatro ojos digital").

**Artículo 28°. Registro inmutable de actos procesales.**
Todo acto procesal digital generará automáticamente un registro criptográficamente verificable, que identifique al funcionario interviniente, fecha, hora y acción ejecutada, inalterable incluso por los administradores técnicos del sistema.

**Artículo 29°. Interoperabilidad con órganos de control.**
Los sistemas que soporten los procesos del artículo 24° interoperarán en tiempo real, mediante API seguras, con tableros de acceso directo para la Contraloría General de la República y la Inspectoría General de Tribunales, sin necesidad de solicitud previa.

**Artículo 30°. Auditoría algorítmica continua.**
Todo sistema de inteligencia artificial empleado conforme a este Título será objeto de auditoría algorítmica continua conforme a ISO/IEC 23894 e ISO/IEC 42001, evaluando sesgos, exactitud, deriva del modelo y posibilidad de manipulación interna.

**Artículo 31°. Prohibición de decisión sancionatoria íntegramente automatizada.**
Ninguna sanción disciplinaria contra un juez, fiscal, defensor o funcionario judicial podrá fundarse exclusivamente en una alerta algorítmica; esta constituye un elemento indiciario que debe ser corroborado y motivado por autoridad competente, con pleno respeto del artículo 49 constitucional.

**Artículo 32°. Derecho a explicación y recurso humano.**
Todo funcionario afectado por una alerta automatizada tiene derecho a una explicación comprensible de sus fundamentos y a recurrir ante autoridad humana competente, sin que la naturaleza automatizada del proceso obstaculice su ejercicio.

---

## TÍTULO VIII. RÉGIMEN SANCIONATORIO

**Artículo 33°. Agravante específico.**
Cuando el sujeto activo de una conducta tipificada en la Ley Especial contra los Delitos Informáticos sea un funcionario del sistema de justicia que manipule, desactive o adultere un sistema de automatización, registro inmutable o mecanismo de cumplimiento previsto en el Título VII, la pena se incrementará en una tercera parte.

**Artículo 34°. Infracciones administrativas y sanciones.**
Constituyen infracciones sancionables por la DINCIP, ante la Inspectoría General de Tribunales o el órgano disciplinario competente del Ministerio Público: 1) el incumplimiento de notificación de incidentes; 2) la omisión de controles técnicos del Título III; 3) la elusión de mecanismos de trazabilidad del Título VII. Se sancionan con amonestación, remisión a la jurisdicción disciplinaria, o suspensión de la certificación técnica del sistema, garantizando siempre doble instancia.

---

## TÍTULO IX. COOPERACIÓN

**Artículo 35°. Cooperación con la autoridad nacional de ciberseguridad.**
La DINCIP coordinará con la autoridad nacional de ciberseguridad del Estado, si existiere, el intercambio de indicadores de compromiso relativos a incidentes que afecten al sistema de justicia, sin que ello implique subordinación jerárquica.

**Artículo 36°. Cooperación judicial internacional.**
El Tribunal Supremo de Justicia y el Ministerio Público podrán suscribir acuerdos de cooperación técnica con redes internacionales de ciberseguridad judicial, conforme al artículo 154 constitucional.

---

## TÍTULO X. FORMACIÓN

**Artículo 37°. Capacitación obligatoria del personal judicial.**
Todo juez, fiscal, defensor y funcionario con acceso a sistemas de gestión de causas recibirá capacitación anual obligatoria en ciberseguridad procesal, protección de datos y ética del uso de sistemas automatizados.
*Fuente/base normativa: JTC (2025), sección "Training: A Foundational Element of Cyber Defense".*

---

## TÍTULO XI. DISPOSICIONES TRANSITORIAS Y FINALES

**Artículo 38°. Implementación gradual.**
El sistema de justicia dispondrá de doce (12) meses para certificar sus sistemas conforme al Título III y de veinticuatro (24) meses para completar la migración de los procesos del artículo 24° a los mecanismos de automatización, trazabilidad y auditoría continua del Título VII, priorizando los circuitos judiciales de mayor volumen de causas.

**Artículo 39°. Revisión periódica.**
La DINCIP presentará a la Asamblea Nacional y al Tribunal Supremo de Justicia, dentro del primer año de vigencia y con periodicidad bienal, un informe de implementación.

**Artículo 40°. Vigencia.**
Esta Ley entrará en vigencia a partir de su publicación en la Gaceta Oficial de la República Bolivariana de Venezuela.

---

## ANEXO. MATRIZ DE TRAZABILIDAD NORMATIVA (versión sectorial)

| Título | Fuente internacional | Norma nacional concordante |
|---|---|---|
| I. Disposiciones generales | CRBV, arts. 49, 204 | — |
| II. Institucionalidad sectorial | Reglamento (UE, Euratom) 2023/2841, arts. 3-6, 23 (adaptado) | — |
| III. Estándares técnicos | ISO/IEC 27001, 27035, 22301; JTC (2025) | Normativas SUSCERTE |
| IV. Debido proceso digital | CRBV, arts. 28, 49 | Ley Orgánica de Amparo |
| V. Gestión de incidentes | JTC (2025), "COOP" | — |
| VI. Régimen probatorio forense | ISO/IEC 27037, 27041-27043; RFC 3227; NIST SP 800-86 | Manual Único de Cadena de Custodia de Evidencias |
| VII. Integridad procesal (aporte propio, versión sectorial) | Sin antecedente directo | CRBV, arts. 273-291 |
| VIII. Sancionatorio | — | Ley Especial contra los Delitos Informáticos |
| IX. Cooperación | CRBV, art. 154 | — |
| X. Formación | JTC (2025), "Training" | — |
| XI. Transitorias | Reglamento (UE, Euratom) 2023/2841, arts. 24-26 (adaptado) | CRBV, arts. 202-218 |

---

*Documento de trabajo académico-legislativo. No constituye instrumento jurídico vigente. Al ser un instrumento sectorial cuya iniciativa recae naturalmente en la organización y procedimientos judiciales (art. 204 constitucional), se recomienda tramitarlo con opinión previa vinculante del Tribunal Supremo de Justicia y del Ministerio Público antes de su presentación ante la Asamblea Nacional.*
