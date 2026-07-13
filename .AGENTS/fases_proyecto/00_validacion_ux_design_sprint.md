# Skill 00 — Design Sprint de Validación

## 1. Rol responsable
**R4 — Consultor/a UX/UI (Diseño Centrado en el Usuario)**, con revisión de R7 en la definición de necesidades forenses de los usuarios jurídicos.

## 2. Propósito
Validar el problema y el concepto de solución **antes** de comprometer recursos de desarrollo (Fase I en adelante), mediante un Design Sprint de 5 días (Google Ventures), con usuarios jurídicos reales o simulados (juez, fiscal, defensor).

## 3. Entradas
- Journey map actual del proceso de revisión de expedientes (sin IA).
- Acceso a al menos 1 operador jurídico por perfil (juez/fiscal/defensor) o simulación fundamentada por docentes de derecho penal.

## 4. Salidas
- Prototipo navegable de alta fidelidad (Figma, archivo "JullBrain").
- Informe de hallazgos de la prueba de usabilidad del día 5.
- Personas jurídicas validadas (ver apartado 6).

## 5. Dependencias tecnológicas
Figma. No depende de ningún componente del stack RAG — es intencionalmente previo.

## 6. Reglas obligatorias
1. El sprint se ejecuta **antes** de escribir código de ingesta (Skill 01). No se invierte en pipeline sin validar el concepto de interfaz.
2. Las tres personas jurídicas (Juez, Fiscal, Defensor Público) deben validarse con al menos una entrevista real o simulada cada una — no se asumen sin evidencia.
3. El prototipo debe incluir, desde esta fase, el indicador de estado por afirmación (verde/ámbar/rojo) — no se agrega después como "mejora de UX".
4. Ningún hallazgo negativo de la prueba de usabilidad se descarta sin justificación documentada.

## 7. Guion de referencia (cronograma del sprint)

| Día | Actividad | Técnica UX | Responsable |
|-----|-----------|-----------|-------------|
| 1 | Mapear el problema actual | Journey Map | R4 |
| 2 | Bocetar soluciones divergentes | Crazy 8's / Sketching | R4 |
| 3 | Decidir flujo crítico a prototipar | Storyboard | R4 + R6 |
| 4 | Construir prototipo navegable | Prototipado en Figma | R4 |
| 5 | Testear con usuarios jurídicos reales | Entrevista + Prueba de usabilidad (think-aloud) | R4 + R7 (validación de necesidades forenses) |

## 8. Preguntas guía para las entrevistas (día 1 y día 5)
- ¿Cómo distingue hoy, sin IA, un dato verificado de uno que solo "recuerda haber leído"?
- ¿Qué información necesita ver para confiar en un resumen cronológico de un expediente que no leyó completo?
- ¿Qué lo haría rechazar o desconfiar de un "proyecto de decisión" generado por un sistema?

## 9. Criterios de aceptación
- [ ] Prototipo probado con al menos un usuario por persona jurídica.
- [ ] Los tres estados (anclado/desanclado/no verificado) fueron comprendidos sin explicación adicional por el usuario de prueba.
- [ ] Informe de hallazgos entregado antes de iniciar la Skill 01.

## 10. Relación con otras skills
Insumo directo del diseño de interfaz que se implementa transversalmente sobre las Skills 08 (trazabilidad) y 09 (proyección de decisión).
