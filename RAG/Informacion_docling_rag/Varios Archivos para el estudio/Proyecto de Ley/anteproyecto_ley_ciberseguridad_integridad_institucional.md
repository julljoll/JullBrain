# ANTEPROYECTO DE LEY ORGÁNICA DE CIBERSEGURIDAD, INTEGRIDAD INSTITUCIONAL Y TRANSFORMACIÓN DIGITAL DEL ESTADO

**República Bolivariana de Venezuela**
**Documento técnico-jurídico de trabajo académico — versión mejorada y unificada**

Con Sección Especial de Automatización Anticorrupción, Compliance Digital e Informática Forense Aplicada

Elaborado con base en:
- Reglamento (UE, Euratom) 2023/2841 del Parlamento Europeo y del Consejo, de 13 de diciembre de 2023, por el que se establecen medidas para un elevado nivel común de ciberseguridad en las instituciones, órganos y organismos de la Unión (creación de CERT-EU y de la Junta Interinstitucional de Ciberseguridad, IICB).
- Boletín *Cybersecurity Basics for Courts*, Joint Technology Committee — COSCA/NACM/NCSC (versión 4.0, 15/09/2025).
- Constitución de la República Bolivariana de Venezuela (1999).
- Ley Especial contra los Delitos Informáticos (2001) y Ley de Infogobierno.
- Normas ISO/IEC 27001, 27002, 27032, 27035, 27037, 27041, 27042, 27043, 22301, 23894, 42001, 31000, 37001, 37301, 29148, 25010.
- RFC 3227 (*Guidelines for Evidence Collection and Archiving*), NIST SP 800-86 y NIST SP 800-101.

> **Nota metodológica.** Este es un documento de trabajo académico. No constituye instrumento jurídico vigente. Su incorporación al ordenamiento requiere el trámite constitucional de iniciativa, discusión y sanción previsto en los artículos 202 al 218 de la Constitución de la República Bolivariana de Venezuela (CRBV), así como el respectivo procedimiento de consulta pública que exige el artículo 211 constitucional para los proyectos de ley que puedan afectar derechos.

---

## EXPOSICIÓN DE MOTIVOS

La República Bolivariana de Venezuela reconoce en el artículo 110 constitucional el interés público de la ciencia, la tecnología y la innovación, y en el artículo 141 consagra que la Administración Pública se fundamenta en los principios de honestidad, transparencia, eficacia, eficiencia, responsabilidad y rendición de cuentas. El marco jurídico vigente en materia de ciberseguridad —representado principalmente por la Ley Especial contra los Delitos Informáticos (2001), la Ley de Infogobierno y la Ley sobre Mensajes de Datos y Firmas Electrónicas— fue concebido antes de la consolidación de amenazas como el ransomware como servicio, los ataques a cadenas de suministro de software y el uso malicioso de inteligencia artificial, y carece de mecanismos técnicos que reduzcan la discrecionalidad humana no controlada en procesos institucionales históricamente permeables a la corrupción y al retardo procesal.

Esta propuesta toma como referencia comparada el **Reglamento (UE, Euratom) 2023/2841**, que crea el Equipo de Respuesta a Emergencias Informáticas de las instituciones, órganos y organismos de la Unión (CERT‑EU), la Junta Interinstitucional de Ciberseguridad (IICB), los planes de gestión de crisis cibernética, la reasignación presupuestaria inicial y el régimen de revisión periódica obligatoria (artículos 3 a 6, 9, 23 a 26). Asimismo, incorpora el boletín **"Cybersecurity Basics for Courts"** del Joint Technology Committee (COSCA‑NACM‑NCSC, 2025), que documenta ataques de ransomware contra tribunales de Los Ángeles (julio 2024), Cleveland (febrero‑marzo 2025) y la Administrative Office of the U.S. Courts (2025), y recomienda gobernanza de ciberseguridad, equipos de respuesta a incidentes (CIRT), segmentación de red, arquitectura de confianza cero (*zero trust*), principio de mínimo privilegio, autenticación multifactor, gestión de riesgo de proveedores tecnológicos, seguridad en la nube y planes de continuidad operativa integrados al COOP (*Continuity of Operations Plan*).

El instrumento se articula con el bloque constitucional venezolano: el derecho de acceso a la información y a la protección de datos y autodeterminación informativa (artículo 28), la inviolabilidad de las comunicaciones (artículo 48), el debido proceso (artículo 49), el interés público de la ciencia y la tecnología (artículo 110), los principios de la función pública (artículo 141), la facultad de suscribir tratados que favorezcan la integración latinoamericana (artículo 154) y el control fiscal y moral ejercido por el Poder Ciudadano y la Contraloría General de la República (artículos 273 al 291). Se adoptan además, como marco metodológico defendible, los estándares ISO/IEC 27001 (SGSI), 27002 (controles), 27032 (ciberseguridad), 27035 (gestión de incidentes), 22301 (continuidad de negocio), 27037/27041/27042/27043 (informática forense), 42001 y 23894 (gestión de sistemas y riesgos de inteligencia artificial), 31000 (gestión de riesgos), 37001 (antisoborno) y 37301 (sistemas de gestión de cumplimiento), así como los principios de ingeniería de requisitos ISO/IEC/IEEE 29148 y de calidad de producto de software ISO/IEC 25010, y las guías técnicas RFC 3227 y NIST SP 800‑86 para la recolección y preservación de evidencia digital conforme al orden de volatilidad.

Un componente central y diferenciador de esta propuesta, sin antecedente directo en las normativas de referencia, es la incorporación de un **régimen especial de integridad institucional (Título VII)** que utiliza la ciberseguridad, la inteligencia artificial, la informática forense y los sistemas de gestión de cumplimiento no solo como herramientas defensivas frente a atacantes externos, sino como **mecanismos activos de sustitución o minimización de la intervención humana discrecional** en procesos administrativos y judiciales estructuralmente vulnerables a la corrupción, dotando al Estado de procesos continuos, trazables, auditables y automatizados, siempre bajo supervisión humana significativa y con pleno respeto de las garantías constitucionales del debido proceso. Este componente se desarrolla en profundidad, con su fundamentación técnica y de política pública, en el documento anexo *"Aporte principal: automatización, IA y compliance como sustitución de la discrecionalidad humana en la prevención de la corrupción"*, que acompaña este anteproyecto.

En ejercicio de la iniciativa legislativa prevista en el artículo 204 de la Constitución de la República Bolivariana de Venezuela, se somete a consideración de la Asamblea Nacional el siguiente:

---

## LA ASAMBLEA NACIONAL DE LA REPÚBLICA BOLIVARIANA DE VENEZUELA DECRETA

la siguiente,

# LEY ORGÁNICA DE CIBERSEGURIDAD, INTEGRIDAD INSTITUCIONAL Y TRANSFORMACIÓN DIGITAL DEL ESTADO

---

## TÍTULO I. DISPOSICIONES GENERALES

**Artículo 1°. Objeto.**
La presente Ley tiene por objeto establecer el marco jurídico, institucional y técnico de la ciberseguridad del Estado venezolano; regular la prevención, detección, respuesta y recuperación frente a incidentes cibernéticos; garantizar la protección de la infraestructura digital crítica; fijar el régimen probatorio de la evidencia digital; y establecer un régimen especial de integridad institucional que reduzca, mediante automatización, trazabilidad y auditoría continua, los espacios de discrecionalidad humana asociados a la corrupción administrativa y judicial.

**Artículo 2°. Ámbito de aplicación.**
Esta Ley se aplica a los órganos y entes del Poder Público Nacional, Estadal y Municipal; al Poder Judicial; al Poder Ciudadano; al Poder Electoral; a los operadores de servicios esenciales e infraestructura crítica (energía, agua, banca y pagos, salud, telecomunicaciones, transporte y registros públicos); a las personas naturales y jurídicas de derecho privado que presten servicios o suministren tecnología al Estado (proveedores y terceros de la cadena de suministro digital); y a toda persona que trate datos o sistemas de información dentro del territorio de la República o que produzcan efectos en él.

**Artículo 3°. Principios rectores.**
La aplicación de esta Ley se rige por los principios de: legalidad, proporcionalidad, seguridad jurídica, minimización de datos, seguridad y privacidad desde el diseño y por defecto, mínimo privilegio, defensa en profundidad, confianza cero (*zero trust*), trazabilidad, rendición de cuentas, neutralidad tecnológica, cooperación interinstitucional e internacional, gradualidad en la implementación, proporcionalidad del régimen sancionatorio y **supervisión humana significativa** sobre todo sistema automatizado o de inteligencia artificial que produzca efectos jurídicos sobre las personas.
*Fuente/base normativa: Reglamento (UE, Euratom) 2023/2841, considerandos y art. 1; CRBV, arts. 110, 141; JTC (2025), sección "Zero Trust Principles".*

**Artículo 4°. Definiciones.**
A los efectos de esta Ley se entiende por:
1. **Ciberseguridad**: conjunto de actividades, políticas y controles orientados a proteger la confidencialidad, integridad y disponibilidad de las redes, sistemas e infraestructuras digitales.
2. **Incidente cibernético**: evento que compromete o amenaza comprometer la confidencialidad, integridad o disponibilidad de un sistema de información.
3. **Incidente mayor**: incidente cuya severidad, conforme a la taxonomía común aprobada por la Junta Interinstitucional de Ciberseguridad, afecta la continuidad del Estado, derechos fundamentales o infraestructura crítica.
4. **CSIRT/CERT**: Equipo de Respuesta a Incidentes de Seguridad Informática.
5. **Cadena de custodia digital**: procedimiento documentado que garantiza la integridad, autenticidad y trazabilidad de la evidencia digital desde su identificación y recolección hasta su valoración judicial.
6. **Sistema de inteligencia artificial de alto riesgo**: aquel cuya operación puede afectar derechos fundamentales, la libertad, el patrimonio público o el debido proceso.
7. **Sistema de Gestión de Cumplimiento (Compliance Management System — CMS)**: conjunto de políticas, controles y tecnologías destinadas a prevenir, detectar y remediar el incumplimiento normativo y los actos de corrupción.
8. **Registro inmutable**: bitácora electrónica protegida criptográficamente contra alteración o supresión no autorizada.
9. **Automatización robótica de procesos (RPA)**: tecnología de software que ejecuta tareas administrativas repetitivas conforme a reglas predefinidas y auditables.
10. **Arquitectura de confianza cero (*zero trust*)**: modelo de seguridad que no otorga confianza implícita a ningún usuario, dispositivo o sistema por su ubicación en la red, y exige verificación continua de identidad y contexto.
11. **Segmentación de red**: técnica de división de una red en subredes aisladas para limitar el movimiento lateral de un atacante o de un código malicioso.
12. **Ransomware**: código malicioso que cifra o bloquea el acceso a sistemas o datos, condicionando su liberación al pago de un rescate.
13. **Gestión de riesgo de terceros y de la cadena de suministro digital**: proceso mediante el cual un órgano evalúa y supervisa los riesgos de ciberseguridad derivados de proveedores, contratistas y prestadores de servicios tecnológicos.
14. **Preparación forense continua (*forensic readiness*)**: capacidad de un sistema para preservar automáticamente evidencia digital apta para uso judicial, con anterioridad a la ocurrencia de un ilícito.
15. **Deriva del modelo (*model drift*)**: degradación del desempeño o de la exactitud de un sistema de inteligencia artificial a lo largo del tiempo, respecto de los parámetros con que fue validado.
16. **Explicabilidad algorítmica**: capacidad de un sistema automatizado de producir, en lenguaje comprensible para un operador jurídico no técnico, los fundamentos de una salida o alerta determinada.
*Fuente/base normativa: ISO/IEC 27000, 27032, 27035; JTC (2025), sección "Essential Terminology"; ISO/IEC 42001, 23894.*

---

## TÍTULO II. INSTITUCIONALIDAD Y GOBERNANZA DE LA CIBERSEGURIDAD

### Capítulo I. Superintendencia Nacional de Ciberseguridad y Protección de Datos (SUNACIB)

**Artículo 5°. Creación y naturaleza jurídica.**
Se crea la Superintendencia Nacional de Ciberseguridad y Protección de Datos (SUNACIB), como órgano de rango legal con autonomía funcional, técnica, financiera y de gestión, adscrito administrativamente a la Asamblea Nacional y con relación de coordinación funcional con el Poder Ciudadano, a fin de garantizar su independencia técnica frente a los órganos que le corresponde auditar. El Superintendente o Superintendenta será designado por la Asamblea Nacional, previa postulación de un comité técnico de credenciales integrado por representantes académicos y del Poder Ciudadano, para un período de cinco (5) años, con posibilidad de una única reelección, y solo podrá ser removido antes del vencimiento de su período por causal disciplinaria grave, debidamente sustanciada y con derecho a defensa.

**Artículo 6°. Atribuciones.**
Corresponde a SUNACIB: 1) dictar la Estrategia Nacional de Ciberseguridad y sus actualizaciones bienales; 2) certificar el cumplimiento de los estándares técnicos exigidos en el Título III; 3) coordinar al CERT‑VE y a los CSIRT sectoriales; 4) ejercer la autoridad de protección de datos personales; 5) ejercer la Oficina Nacional de Cumplimiento Digital prevista en el Título VII; 6) mantener el Registro Nacional de Infraestructura Digital Crítica y el Registro Nacional de Peritos Informáticos Forenses; 7) imponer las sanciones administrativas previstas en esta Ley; 8) rendir informe anual público a la Asamblea Nacional y a la Contraloría General de la República; y 9) publicar anualmente indicadores agregados y anonimizados sobre incidentes, tiempos de respuesta y alertas de cumplimiento, en formato de datos abiertos.
*Fuente/base normativa: Reglamento (UE, Euratom) 2023/2841, arts. 3-6 (creación y atribuciones de CERT-EU); CRBV art. 141.*

### Capítulo II. CERT-VE: Equipo Nacional de Respuesta a Incidentes

**Artículo 7°. Creación y funciones.**
Se crea el CERT‑VE, adscrito a SUNACIB, como equipo técnico responsable de la detección, análisis, contención, erradicación y recuperación frente a incidentes cibernéticos que afecten al Poder Público y a la infraestructura crítica nacional. El CERT‑VE mantendrá un inventario actualizado de capacidades técnicas disponibles, con actualización anual obligatoria por parte de cada órgano y ente, y coordinará ejercicios de simulación al menos dos veces al año.

**Artículo 8°. CSIRT sectorial del Poder Judicial.**
Se crea un CSIRT especializado adscrito al Tribunal Supremo de Justicia, encargado de la ciberseguridad de los circuitos judiciales, el sistema de gestión de causas, la custodia de evidencia digital y los servicios de videoconferencia judicial, en atención a la especial exposición de los tribunales frente al secuestro de datos (ransomware) evidenciada en incidentes reales ocurridos en tribunales de Los Ángeles (julio 2024), Cleveland (febrero‑marzo 2025) y en la Administrative Office of the U.S. Courts (2025).
*Fuente/base normativa: JTC, Cybersecurity Basics for Courts (2025), secciones "State of Cybersecurity in Courts" y "Assembling a Cybersecurity Incident Response Team (CIRT)".*

**Artículo 9°. Equipos de Respuesta a Incidentes de Ciberseguridad (CIRT) institucionales.**
Todo órgano o ente de la infraestructura crítica nacional y del Poder Judicial constituirá un CIRT institucional, con roles y responsabilidades documentados, canal de escalamiento definido hacia el CERT‑VE, y ejercicios de mesa (*tabletop exercises*) al menos una vez al año, conforme a las buenas prácticas de conformación de equipos de respuesta a incidentes.
*Fuente/base normativa: JTC (2025), sección "Assembling a Cybersecurity Incident Response Team (CIRT)".*

### Capítulo III. Junta Interinstitucional de Ciberseguridad (JIC)

**Artículo 10°. Composición y funciones.**
Se crea la Junta Interinstitucional de Ciberseguridad, integrada por un representante de cada Poder Público, un representante de la Contraloría General de la República, un representante del Ministerio Público, un representante de la sociedad civil organizada en materia de derechos digitales designado mediante concurso público, y el Superintendente de SUNACIB, quien la coordina. La Junta aprueba el plan de gestión de crisis cibernéticas mayores, la taxonomía común de severidad de incidentes, los protocolos operativos estándar y los canales seguros de comunicación entre entes del Estado.
*Fuente/base normativa: Reglamento (UE, Euratom) 2023/2841, art. 23 (Junta Interinstitucional de Ciberseguridad, IICB) y art. 9(2).*

---

## TÍTULO III. MARCO DE GESTIÓN Y ESTÁNDARES TÉCNICOS

**Artículo 11°. Adopción de estándares internacionales.**
Los órganos y entes sujetos a esta Ley deberán implementar un Sistema de Gestión de Seguridad de la Información conforme a la norma ISO/IEC 27001, adoptando como referencia complementaria la ISO/IEC 27002 (controles), ISO/IEC 27032 (ciberseguridad), ISO/IEC 27035 (gestión de incidentes) e ISO 22301 (continuidad de negocio). SUNACIB dictará el cronograma de certificación gradual por sectores, priorizando infraestructura crítica, el Poder Judicial y los sistemas de contratación pública.

**Artículo 12°. Clasificación de sistemas críticos.**
SUNACIB mantendrá un Registro Nacional de Infraestructura Digital Crítica, clasificando los sistemas según su impacto en la continuidad del Estado, la seguridad ciudadana y los derechos fundamentales, con niveles de exigencia técnica proporcionales a dicha clasificación.

**Artículo 13°. Gestión de riesgos.**
Todo órgano sujeto a esta Ley deberá mantener un proceso continuo de identificación, análisis, tratamiento y monitoreo de riesgos de ciberseguridad conforme a la metodología ISO 31000, documentado y disponible para auditoría por parte de SUNACIB y de la Contraloría General de la República.

**Artículo 14°. Requisitos y calidad de los sistemas de información del Estado.**
El desarrollo, adquisición o contratación de sistemas de información del Estado deberá documentar sus requisitos conforme a la norma ISO/IEC/IEEE 29148 y evaluar su calidad conforme al modelo ISO/IEC 25010 (funcionalidad, fiabilidad, usabilidad, eficiencia de desempeño, seguridad, mantenibilidad, portabilidad y compatibilidad), como condición para su puesta en producción.

**Artículo 15°. Controles mínimos de acceso y arquitectura de confianza cero.**
Todo sistema de información del Estado implementará, como mínimo: autenticación multifactor para el acceso a sistemas críticos y a datos sensibles; principio de mínimo privilegio en la asignación de permisos; segmentación de red que aísle los sistemas que soportan procesos de riesgo prioritario conforme al Título VII; y revisión periódica, no menor a semestral, de los privilegios de acceso otorgados, con revocación inmediata al cese de la relación funcionarial o contractual.
*Fuente/base normativa: JTC (2025), secciones "Least Privilege Access", "Zero Trust Principles" y "Network Segmentation".*

**Artículo 16°. Cifrado y protección de la información.**
La información sensible o de carácter crítico deberá protegerse mediante cifrado en tránsito y en reposo, conforme a algoritmos y longitudes de clave reconocidos internacionalmente, cuya vigencia técnica será actualizada periódicamente por SUNACIB en función de la evolución del estado del arte criptográfico.

**Artículo 17°. Seguridad en servicios de computación en la nube.**
Los órganos y entes que contraten servicios de computación en la nube deberán verificar que el proveedor cuente con certificaciones de seguridad reconocidas internacionalmente, exigir cláusulas contractuales de localización o repatriación de datos, notificación de incidentes, auditoría y portabilidad, y mantener un inventario actualizado de los servicios en la nube utilizados y de la clasificación de los datos alojados en ellos.
*Fuente/base normativa: JTC (2025), sección "Cloud Security Considerations".*

**Artículo 18°. Gestión de riesgo de proveedores y de la cadena de suministro digital.**
SUNACIB dictará el reglamento de gestión de riesgo de terceros, exigible a todo proveedor de bienes o servicios tecnológicos al Estado, que incluirá como mínimo: evaluación previa de postura de ciberseguridad del proveedor; obligación contractual de notificación de incidentes que afecten al Estado; derecho de auditoría; y cláusulas de responsabilidad por incumplimiento de los controles exigidos en este Título.
*Fuente/base normativa: JTC (2025), sección "Vendor and Third-Party Risk Management".*

---

## TÍTULO IV. DERECHOS FUNDAMENTALES Y GARANTÍAS EN EL ENTORNO DIGITAL

**Artículo 19°. Protección de datos personales.**
Toda persona tiene derecho a la protección de sus datos personales conforme al artículo 28 constitucional. Los tratamientos de datos realizados por sistemas automatizados o de inteligencia artificial deberán observar los principios de licitud, finalidad, minimización, exactitud y limitación del plazo de conservación.

**Artículo 20°. Hábeas data digital.**
Toda persona podrá solicitar ante SUNACIB y, subsidiariamente, ante el tribunal competente, el acceso, rectificación, actualización o destrucción de sus datos contenidos en registros públicos o privados que consten en sistemas de información, de conformidad con el artículo 28 constitucional y la Ley Orgánica de Amparo sobre Derechos y Garantías Constitucionales.

**Artículo 21°. Debido proceso y prueba electrónica.**
En toda actuación judicial o administrativa en que se emplee evidencia digital deberá garantizarse el derecho a la defensa, el acceso a las pruebas y el contradictorio, en los términos del artículo 49 constitucional. La evidencia digital solo será admisible cuando conste su cadena de custodia conforme al Título VI de esta Ley.

**Artículo 22°. Supervisión humana significativa.**
Ninguna decisión que restrinja derechos, imponga sanciones o produzca efectos jurídicos adversos sobre una persona podrá fundarse exclusivamente en un tratamiento automatizado o en la salida de un sistema de inteligencia artificial, sin intervención, revisión y motivación de un funcionario competente identificado, quien asume la responsabilidad del acto.

**Artículo 23°. Inviolabilidad de las comunicaciones y proporcionalidad de la vigilancia institucional.**
Los mecanismos de monitoreo, detección de anomalías y auditoría continua previstos en esta Ley respetarán la inviolabilidad de las comunicaciones consagrada en el artículo 48 constitucional; su alcance se limitará a lo estrictamente necesario para la finalidad de ciberseguridad o de prevención de la corrupción declarada, quedando prohibido su uso para fines distintos, incluida la vigilancia política o gremial de funcionarios.

---

## TÍTULO V. GESTIÓN DE INCIDENTES Y NOTIFICACIÓN DE BRECHAS

**Artículo 24°. Obligación de notificación.**
Todo órgano, ente u operador de servicios esenciales deberá notificar al CERT‑VE cualquier incidente significativo dentro de las veinticuatro (24) horas siguientes a su detección, y presentar un informe final dentro de los treinta (30) días continuos siguientes, sin perjuicio de la notificación a los titulares de datos afectados cuando corresponda.

**Artículo 25°. Taxonomía común de severidad.**
La Junta Interinstitucional de Ciberseguridad aprobará una taxonomía común de severidad de incidentes mayores, aplicable de manera uniforme a todos los entes del Estado, a fin de activar de forma proporcional los protocolos de crisis.

**Artículo 26°. Continuidad operativa.**
Todo órgano sujeto a esta Ley deberá contar con un Plan de Continuidad de Operaciones que integre expresamente los escenarios de incidente cibernético, incluyendo procedimientos de comunicación redundante, respaldo desconectado de la red (*offline*) y restauración priorizada de funciones esenciales.
*Fuente/base normativa: JTC (2025), secciones "Cybersecurity as Part of a COOP" y "Communication Planning".*

**Artículo 27°. Ejercicios y simulacros.**
Los órganos sujetos a esta Ley realizarán, como mínimo, un ejercicio de mesa (*tabletop exercise*) anual y una prueba técnica de restauración de respaldo semestral, incluyendo simulacros de phishing dirigidos al personal, cuyos resultados serán reportados a SUNACIB.

---

## TÍTULO VI. RÉGIMEN PROBATORIO Y PERITAJE INFORMÁTICO FORENSE

**Artículo 28°. Cadena de custodia digital.**
La recolección, preservación, embalaje, transporte, análisis y presentación de evidencia digital se realizará conforme a los principios de la informática forense contenidos en las normas ISO/IEC 27037 (identificación, recolección, adquisición y preservación), ISO/IEC 27041 (garantía de idoneidad de métodos de investigación), ISO/IEC 27042 (análisis e interpretación) e ISO/IEC 27043 (principios y procesos de investigación de incidentes), en concordancia con el Manual Único de Cadena de Custodia de Evidencias vigente en el ordenamiento venezolano.

**Artículo 29°. Orden de volatilidad en la recolección de evidencia.**
La recolección de evidencia digital observará el orden de volatilidad de las fuentes de información —de mayor a menor volatilidad: registros y contenidos de memoria, estado de conexiones de red, procesos en ejecución, contenido de almacenamiento temporal, discos y medios de almacenamiento persistente, y respaldos remotos u offline—, conforme a los criterios técnicos reconocidos internacionalmente para la preservación de evidencia digital.
*Fuente/base normativa: RFC 3227, sección "Order of Volatility"; NIST SP 800-86.*

**Artículo 30°. Certificación de peritos informáticos forenses.**
SUNACIB llevará el Registro Nacional de Peritos Informáticos Forenses, que certificará la idoneidad técnica de quienes actúen como auxiliares de justicia en esta materia, conforme a estándares de competencia reconocidos internacionalmente, sin perjuicio de las facultades del Ministerio Público y del Poder Judicial.

**Artículo 31°. Valor probatorio de registros electrónicos.**
Los registros electrónicos generados por sistemas certificados conforme a esta Ley, cuya integridad esté protegida mediante funciones criptográficas de resumen (*hash*) y sello de tiempo, harán fe salvo prueba en contrario, sin menoscabo del derecho de la contraparte a impugnar su autenticidad conforme al artículo 49 constitucional.

---

## TÍTULO VII. INTEGRIDAD INSTITUCIONAL: AUTOMATIZACIÓN ANTICORRUPCIÓN, COMPLIANCE DIGITAL E INFORMÁTICA FORENSE APLICADA

> **SECCIÓN DE ÉNFASIS ESPECIAL DE ESTA PROPUESTA.** A diferencia del Reglamento (UE, Euratom) 2023/2841 y del boletín del JTC, que abordan la ciberseguridad principalmente como defensa frente a amenazas externas, este Título convierte la ciberseguridad, la inteligencia artificial y la informática forense en herramientas activas de prevención de la corrupción interna, sustituyendo o acotando la discrecionalidad humana no controlada en los procesos institucionales de mayor riesgo, y garantizando que dichos procesos sean continuos, trazables, auditables y automatizados. El desarrollo técnico y de política pública de este Título se amplía en el documento *"Aporte principal"* que acompaña este anteproyecto.

### Capítulo I. Objeto y procesos de riesgo prioritario

**Artículo 32°. Objeto de la sección.**
Esta sección tiene por objeto establecer los mecanismos técnicos y de gobernanza mediante los cuales el Estado venezolano reduce, minimiza o sustituye, en la mayor medida jurídicamente admisible, la intervención humana discrecional no controlada en procesos administrativos y judiciales estructuralmente vulnerables a la corrupción, mediante automatización de procesos, inteligencia artificial de apoyo a la decisión, registros inmutables y auditoría continua.

**Artículo 33°. Procesos de riesgo prioritario.**
Se declaran procesos de riesgo prioritario, sujetos a automatización obligatoria conforme a esta sección: 1) los procedimientos de contratación pública y licitación; 2) la distribución y asignación aleatoria de causas judiciales y fiscales; 3) la custodia y cadena de evidencia física y digital; 4) la ejecución y desembolso presupuestario; 5) la administración de nómina y beneficios de funcionarios públicos; 6) el otorgamiento de permisos, licencias y registros públicos; 7) los procesos de ascenso, traslado y evaluación de jueces, fiscales y funcionarios de cuerpos de seguridad; y 8) los procesos aduaneros y de fiscalización tributaria de alto valor.

### Capítulo II. Oficina Nacional de Cumplimiento Digital (Compliance Office)

**Artículo 34°. Creación.**
Se crea, dentro de SUNACIB y con relación de coordinación funcional con la Contraloría General de la República y el Ministerio Público, la Oficina Nacional de Cumplimiento Digital, encargada de administrar el Sistema de Gestión de Cumplimiento (CMS) del Estado venezolano, conforme a los estándares ISO 37301 (sistemas de gestión de cumplimiento) e ISO 37001 (sistemas de gestión antisoborno).

**Artículo 35°. Funciones.**
Corresponde a la Oficina Nacional de Cumplimiento Digital: 1) operar de manera continua motores de análisis de datos y de inteligencia artificial para la detección de anomalías, patrones de riesgo y señales de alerta temprana (*red flags*) en los procesos declarados de riesgo prioritario; 2) administrar un canal de denuncias interoperable con los sistemas de detección de anomalías, que permita correlacionar denuncias ciudadanas con hallazgos algorítmicos; 3) emitir reportes automáticos y periódicos a la Contraloría General de la República, al Ministerio Público y a la Asamblea Nacional; y 4) mantener y actualizar la matriz de riesgo de corrupción institucional.

**Artículo 36°. Independencia técnica y protección del personal.**
El personal técnico de la Oficina Nacional de Cumplimiento Digital gozará de estabilidad reforzada e inamovilidad funcional, y no podrá ser removido sin procedimiento disciplinario motivado ante la Junta Interinstitucional de Ciberseguridad, a fin de garantizar su independencia frente a los órganos auditados.

### Capítulo III. Automatización de procesos administrativos de riesgo

**Artículo 37°. Motores de decisión asistida y automatización robótica de procesos.**
Los procesos declarados de riesgo prioritario en el artículo 33 deberán migrar, dentro de los plazos establecidos en las disposiciones transitorias, a plataformas de automatización robótica de procesos (RPA) y motores de decisión asistida por reglas auditables, que ejecuten las etapas repetitivas y regladas del proceso sin intervención humana directa, reservando la intervención humana a las etapas de excepción expresamente justificadas y documentadas (principio de intervención humana por excepción).

**Artículo 38°. Distribución aleatoria de causas mediante sistema certificado.**
La asignación de causas judiciales y fiscales se realizará mediante un sistema de distribución aleatoria certificado por SUNACIB, cuyo algoritmo de asignación será público, auditable y generará un registro inmutable de cada asignación, sin posibilidad de intervención manual salvo recusación, inhibición o impedimento debidamente motivados y registrados.

**Artículo 39°. Segregación de funciones programática.**
Todo sistema de información que soporte un proceso de riesgo prioritario implementará control de acceso basado en roles y segregación de funciones programática, de modo que ninguna persona natural pueda, por sí sola, iniciar, aprobar y ejecutar una misma operación crítica (principio de "cuatro ojos digital"), sin perjuicio de las responsabilidades jerárquicas que correspondan.

**Artículo 40°. Registro inmutable y trazabilidad.**
Todo acto administrativo o judicial dictado, tramitado o soportado dentro de un proceso de riesgo prioritario generará automáticamente un registro criptográficamente verificable (encadenamiento de resúmenes hash con sello de tiempo, en arquitectura de bitácora inmutable tipo *write once read many* o de libro distribuido), que identifique al funcionario interviniente, la fecha, la hora y la acción ejecutada, y que no podrá ser alterado ni suprimido por ningún usuario del sistema, incluidos los administradores técnicos.

**Artículo 41°. Interoperabilidad con los órganos de control.**
Los sistemas que soporten procesos de riesgo prioritario deberán interoperar en tiempo real, mediante interfaces de programación de aplicaciones (API) seguras, con tableros de control (*dashboards*) de acceso directo para la Contraloría General de la República y el Ministerio Público, sin necesidad de solicitud previa ni intermediación del órgano auditado.

**Artículo 42°. Auditoría algorítmica continua.**
Todo sistema de inteligencia artificial o de automatización empleado en los procesos de riesgo prioritario será objeto de auditoría algorítmica continua conforme a los criterios de gestión de riesgo de sistemas de inteligencia artificial de la norma ISO/IEC 23894 y del sistema de gestión de inteligencia artificial ISO/IEC 42001, evaluando sesgos, exactitud, deriva del modelo (*model drift*) y posibilidad de manipulación por parte de operadores internos.

### Capítulo IV. Informática forense aplicada a la prevención

**Artículo 43°. Preparación forense continua (*forensic readiness*).**
Los sistemas que soporten procesos de riesgo prioritario deberán diseñarse desde su origen bajo el principio de preparación forense continua conforme a la norma ISO/IEC 27043, de manera que la evidencia digital de cualquier acto se preserve automáticamente en condiciones aptas para su posterior valoración judicial, sin necesidad de intervención reactiva ante la sospecha de un ilícito.

**Artículo 44°. Peritaje y explicabilidad algorítmica.**
Cuando un sistema de inteligencia artificial genere una alerta de riesgo (*red flag*) que dé lugar a una investigación disciplinaria, administrativa o penal, la Oficina Nacional de Cumplimiento Digital deberá producir un informe de explicabilidad que describa, en lenguaje comprensible para el operador jurídico, los datos, variables y reglas que motivaron la alerta, el cual formará parte del expediente y podrá ser controvertido por la persona investigada.

### Capítulo V. Garantías frente a la propia automatización

**Artículo 45°. Prohibición de decisión sancionatoria íntegramente automatizada.**
Ninguna sanción disciplinaria, administrativa o penal podrá fundarse exclusivamente en la alerta generada por un sistema automatizado o de inteligencia artificial. La alerta constituye un elemento indiciario que debe ser corroborado, valorado y motivado por un funcionario competente, respetando en todo momento el debido proceso consagrado en el artículo 49 constitucional.

**Artículo 46°. Derecho a explicación y recurso humano.**
Toda persona afectada por una alerta o decisión asistida por un sistema automatizado tiene derecho a obtener una explicación comprensible de sus fundamentos y a interponer los recursos administrativos y judiciales ordinarios ante una autoridad humana competente, sin que la naturaleza automatizada del proceso pueda oponerse como obstáculo para su ejercicio. El recurso jerárquico contra una alerta que dé lugar a medida preventiva de suspensión del cargo deberá resolverse dentro de los quince (15) días hábiles siguientes a su interposición.

**Artículo 47°. Evaluación de impacto en derechos humanos e inteligencia artificial.**
Previo a la implementación de todo sistema de inteligencia artificial de alto riesgo dentro de un proceso de riesgo prioritario, el órgano responsable deberá elaborar y publicar una Evaluación de Impacto en Derechos Humanos e Inteligencia Artificial, que identifique riesgos de discriminación, vulneración del debido proceso y afectación desproporcionada de grupos vulnerables, sujeta a revisión previa de SUNACIB.

---

## TÍTULO VIII. RÉGIMEN SANCIONATORIO

**Artículo 48°. Relación con la Ley Especial contra los Delitos Informáticos.**
Las conductas tipificadas en la Ley Especial contra los Delitos Informáticos se mantienen vigentes en cuanto no colidan con la presente Ley. Cuando el sujeto activo sea un funcionario público que manipule, desactive, elimine o adultere un sistema de automatización, registro inmutable o mecanismo de cumplimiento previsto en el Título VII, la pena aplicable se incrementará en una tercera parte por constituir agravante específico de abuso de función pública.

**Artículo 49°. Infracciones administrativas.**
Constituyen infracciones administrativas sancionables por SUNACIB: 1) el incumplimiento de la obligación de notificación de incidentes; 2) la omisión de implementación de los controles técnicos exigidos en el Título III; 3) la elusión, desactivación o manipulación de los mecanismos de trazabilidad previstos en el Título VII; 4) el incumplimiento de los plazos de migración a procesos automatizados establecidos en las disposiciones transitorias; y 5) el uso de los mecanismos de monitoreo previstos en esta Ley para fines distintos a los autorizados en el artículo 23.

**Artículo 50°. Sanciones.**
Las infracciones se sancionarán con amonestación escrita, multa de hasta diez mil Unidades Tributarias, suspensión temporal de la certificación técnica del sistema afectado, o remisión a la jurisdicción disciplinaria o penal competente, según la gravedad, reincidencia y el daño causado.

**Artículo 51°. Procedimiento sancionatorio.**
El procedimiento administrativo sancionatorio ante SUNACIB garantizará el derecho a ser oído, la presunción de inocencia, el acceso al expediente y la doble instancia administrativa, siendo recurribles sus decisiones ante la jurisdicción contencioso-administrativa.

---

## TÍTULO IX. COOPERACIÓN INTERINSTITUCIONAL E INTERNACIONAL

**Artículo 52°. Cooperación interinstitucional.**
SUNACIB, el CERT‑VE, la Contraloría General de la República, el Ministerio Público y el Tribunal Supremo de Justicia suscribirán acuerdos marco de intercambio seguro de información, en resguardo del secreto de las investigaciones y de los datos personales.

**Artículo 53°. Cooperación internacional.**
El Estado venezolano podrá suscribir acuerdos de cooperación técnica con organismos y redes internacionales de respuesta a incidentes, así como con entidades homólogas a CERT‑EU, en los términos del artículo 154 constitucional, priorizando el intercambio de indicadores de compromiso y buenas prácticas de gestión de crisis cibernética.

---

## TÍTULO X. FORMACIÓN, CULTURA Y CAPACITACIÓN

**Artículo 54°. Formación continua obligatoria.**
Todo funcionario público con acceso a sistemas de información deberá recibir capacitación anual obligatoria en ciberseguridad, protección de datos y ética del uso de sistemas automatizados, incluyendo simulacros periódicos de phishing y respuesta a incidentes.

**Artículo 55°. Certificación del personal técnico.**
El personal técnico responsable de la respuesta a incidentes y de la administración de los sistemas de cumplimiento deberá mantener certificaciones profesionales vigentes reconocidas internacionalmente en ciberseguridad e informática forense.
*Fuente/base normativa: JTC, Cybersecurity Basics for Courts (2025), secciones "Training: A Foundational Element of Cyber Defense" y "Technical Staff Training and Certification".*

**Artículo 56°. Cultura de integridad y canal de denuncia protegido.**
Los órganos sujetos a esta Ley promoverán una cultura de integridad institucional y garantizarán canales de denuncia protegidos, confidenciales e interoperables con el sistema de cumplimiento previsto en el Título VII, con prohibición expresa de represalias contra el denunciante de buena fe.

---

## TÍTULO XI. DISPOSICIONES TRANSITORIAS, DEROGATORIAS Y FINALES

**Artículo 57°. Reasignación presupuestaria inicial.**
A fin de garantizar el funcionamiento inicial de SUNACIB, el CERT‑VE y la Oficina Nacional de Cumplimiento Digital, el Ejecutivo Nacional propondrá la reasignación presupuestaria correspondiente dentro del primer ejercicio fiscal siguiente a la entrada en vigencia de esta Ley.
*Fuente/base normativa: Reglamento (UE, Euratom) 2023/2841, art. 24 (reasignación presupuestaria inicial).*

**Artículo 58°. Implementación gradual.**
Los órganos sujetos a esta Ley dispondrán de dieciocho (18) meses para certificar su Sistema de Gestión de Seguridad de la Información y de treinta y seis (36) meses para completar la migración de los procesos de riesgo prioritario a los mecanismos de automatización, trazabilidad y auditoría continua previstos en el Título VII, sin perjuicio de que SUNACIB priorice sectores conforme al Registro Nacional de Infraestructura Digital Crítica.

**Artículo 59°. Revisión periódica.**
SUNACIB presentará a la Asamblea Nacional, dentro del primer año de vigencia de esta Ley y con periodicidad bienal posterior, un informe sobre su implementación, incluyendo recomendaciones de reforma legislativa.
*Fuente/base normativa: Reglamento (UE, Euratom) 2023/2841, art. 25 (revisión periódica).*

**Artículo 60°. Disposición derogatoria.**
Se derogan las disposiciones de la Ley de Infogobierno, de la Ley Especial contra los Delitos Informáticos y de cualquier otro instrumento normativo de rango legal o sublegal que colidan expresamente con la presente Ley, subsistiendo dichos cuerpos normativos en todo lo que no la contradiga.

**Artículo 61°. Vigencia.**
Esta Ley entrará en vigencia a partir de su publicación en la Gaceta Oficial de la República Bolivariana de Venezuela.

---

## ANEXO. MATRIZ DE TRAZABILIDAD NORMATIVA

*Elaborada conforme a la lógica de trazabilidad de requisitos de la norma ISO/IEC/IEEE 29148, útil para la defensa metodológica del proyecto ante instancias académicas y legislativas.*

| Título de la propuesta | Fuente / norma internacional | Norma nacional concordante |
|---|---|---|
| I. Disposiciones generales | CRBV, arts. 110, 141 | — |
| II. Institucionalidad (SUNACIB, CERT-VE, JIC) | Reglamento (UE, Euratom) 2023/2841, arts. 3-6, 9, 23 | Ley de Infogobierno (institucionalidad TIC vigente) |
| III. Estándares técnicos | ISO/IEC 27001, 27002, 27032, 27035, 22301, 29148, 25010 | Normativas SUSCERTE |
| III. Zero trust, MFA, segmentación, nube, terceros | JTC (2025): "Least Privilege", "Zero Trust", "Network Segmentation", "Cloud Security", "Vendor Risk" | — |
| IV. Derechos fundamentales | CRBV, arts. 28, 48, 49 | Ley Orgánica de Amparo sobre Derechos y Garantías Constitucionales |
| V. Gestión de incidentes | JTC (2025): "COOP", "Communication Planning" | — |
| VI. Régimen probatorio / forense | ISO/IEC 27037, 27041, 27042, 27043; RFC 3227; NIST SP 800-86 | Manual Único de Cadena de Custodia de Evidencias (versión final, 29-09-2017) |
| VII. Integridad institucional (aporte propio) | Sin antecedente directo — desarrollo original de esta propuesta | Constitución, arts. 141, 273-291 (Poder Ciudadano y Contraloría) |
| VIII. Régimen sancionatorio | — | Ley Especial contra los Delitos Informáticos (2001) |
| IX. Cooperación | CRBV, art. 154 | — |
| X. Formación y cultura | JTC (2025): "Training", "Technical Staff Certification" | — |
| XI. Transitorias y finales | Reglamento (UE, Euratom) 2023/2841, arts. 24-26 | CRBV, arts. 202-218 (procedimiento de formación de leyes) |

---

*Documento de trabajo académico-legislativo. No constituye instrumento jurídico vigente; requiere el trámite constitucional de iniciativa, discusión y sanción previsto en los artículos 202 al 218 de la Constitución de la República Bolivariana de Venezuela. Debe complementarse, antes de su presentación formal, con estudio de impacto fiscal, consulta pública sectorial (incluyendo al Poder Judicial, la Contraloría General de la República y organizaciones de sociedad civil en derechos digitales) y opinión técnica de SUSCERTE y del Ministerio con competencia en ciencia y tecnología.*
