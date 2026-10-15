# Skill 12 — Departamento de Tecnología e IA por Sede (Modelo Institucional)

## 1. Rol responsable
**R3 (marco normativo del despliegue institucional) + R5 (estructura organizativa y protocolo operativo)**.

## 2. Propósito
Especificar la estructura organizativa y el protocolo de operación del Departamento de Tecnología e Inteligencia Artificial que cada tribunal o fiscalía debe constituir para operar su instancia local (Skill 11) de forma autónoma, air-gapped, y coordinada con otras sedes sin comprometer el aislamiento de red.

## 3. Entradas
- Instancia local aprovisionada (Skill 11).
- Corpus normativo versionado (Skill 06) a sincronizar entre sedes.

## 4. Salidas
- Manual de roles y responsabilidades por sede.
- Protocolo de sincronización normativa entre sedes (transferencia controlada, no conexión directa).
- Bitácora de auditoría local.

## 5. Dependencias tecnológicas
Ninguna herramienta específica — esta skill es organizativa/procedimental, apoyada en los controles técnicos de las Skills 06 y 11.

## 6. Reglas obligatorias
1. Cada sede opera de forma autónoma; ninguna sede tiene acceso remoto directo al servidor de otra sede.
2. La sincronización del corpus normativo (Skill 06) entre sedes se realiza por medio físico verificado o VLAN dedicada sin salida a internet — nunca por sincronización automática permanente.
3. Toda actualización de modelos o corpus queda registrada en la bitácora de auditoría local, con responsable identificado.
4. El ente rector de coordinación técnica (si existe en una fase posterior) emite lineamientos, pero no tiene acceso operativo a los servidores de cada sede.

## 7. Estructura de referencia

| Rol | Responsabilidad principal | Perfil requerido |
|-----|---------------------------|-------------------|
| Administrador(a) del sistema local | Instalación, actualización, respaldo y seguridad del servidor RAG de la sede (ejecuta Skill 11) | Técnico(a)/ingeniero(a) en informática, Linux y Docker |
| Curador(a) normativo y documental | Carga, actualización y control de calidad del corpus normativo y de los expedientes indexados (ejecuta Skills 01-06) | Abogado(a) o asistente jurídico con formación en gestión documental |
| Enlace de trazabilidad y verificación | Revisión periódica del módulo de trazabilidad (Skill 08) | Personal jurídico de la sede, capacitado en el uso del sistema |
| Oficial de seguridad de la información | Control de acceso físico/lógico, respaldos cifrados, cumplimiento del aislamiento de red (verifica Skill 11) | Perfil de ciberseguridad, coordinado con el ente rector |

## 8. Plantilla de bitácora de auditoría

```json
{
  "sede": "Tribunal Penal de Barquisimeto - Circuito X",
  "fecha": "2026-07-12",
  "responsable": "nombre del Administrador del sistema local",
  "accion": "actualizacion_corpus_normativo",
  "version_corpus_anterior": "v1.2",
  "version_corpus_nueva": "v1.3",
  "medio_transferencia": "VLAN dedicada sin salida a internet",
  "verificacion_hash": true,
  "observaciones": ""
}
```

## 9. Criterios de aceptación
- [ ] Manual de roles publicado y asignado a personal identificado antes de cargar el primer expediente real.
- [ ] Protocolo de sincronización probado al menos una vez entre dos sedes simuladas, sin conexión directa entre servidores.
- [ ] Bitácora de auditoría con al menos un registro real de actualización normativa.

## 10. Relación con otras skills
Opera sobre la infraestructura de la Skill 11 y sobre el corpus versionado de la Skill 06. Cierra el ciclo institucional del proyecto descrito en el Capítulo IV.4 del anteproyecto.
