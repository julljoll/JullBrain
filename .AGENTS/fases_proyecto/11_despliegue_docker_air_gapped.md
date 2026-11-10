# Fase 11 — Despliegue Soberano en Podman (Windows/Linux) y Oracle Cloud (Air-Gapped)

## 1. Rol responsable
**R2 — Desarrollador/a Python, Podman & Oracle Cloud Full-Stack** (aprovisionamiento, contenedores rootless e infraestructura).

## 2. Propósito
Aprovisionar la instancia completa de **JullBrain v0.2.0** (`IBM Docling` en CPU + `IBM Granite 3.3` + `IBM Granite Embedding R2` + `IBM Granite Guardian 3.2`) utilizando **Podman** nativo en modo *rootless* (tanto en Windows como en Linux) o sobre **Oracle Cloud Infrastructure (OCI)**, manteniendo todos los modelos de IA guardados localmente en `RAG/modelos_ia/` sin depender de conexiones salientes en producción.

## 3. Entradas
- Núcleo de datos y modelos locales en `RAG/` (`RAG/datos_brutos`, `RAG/modelos_ia`, `RAG/Informacion_docling_rag`, `RAG/normativas_chunks`).
- `Containerfile` y `podman-compose.yml` configurados para ejecución sin privilegios (`--security-opt=no-new-privileges`, `--userns=keep-id`).

## 4. Salidas
- Contenedores `jullbrain-core` y `jullbrain-ollama` ejecutándose bajo **Podman**.
- Bóveda de modelos `RAG/modelos_ia/` sellada y verificada con `SHA-256` (`vault_manifest_sha256.json`).
- Verificación de aislamiento de red y cero telemetría (`HF_HUB_DISABLE_TELEMETRY=1`, `DO_NOT_TRACK=1`).

## 5. Dependencias tecnológicas
Podman 4.x / 5.x, `podman-compose`, Python 3.12–3.14.

## 6. Reglas obligatorias
1. **Modelos IA locales en `RAG/modelos_ia/`:** tanto en ejecución local como en Oracle Cloud / Podman, los pesos de `IBM Docling` e `IBM Granite` deben residir en el volumen local `RAG/modelos_ia/`.
2. **Podman Rootless:** los contenedores deben ejecutarse sin demonios con privilegios root y con `--security-opt=no-new-privileges`.
3. **Air-Gapped Ready:** una vez descargados y sellados los modelos con `--bootstrap-models`, el entorno puede operar con `HF_HUB_OFFLINE=1` sin acceso a internet.

## 7. Comandos de Referencia (Podman en Windows o Linux)

```bash
# 1. Construir imagen nativa con Podman
podman build -f Containerfile -t localhost/jullbrain-ibm:0.2.0 .

# 2. Levantar el enclave completo con Podman Compose
podman compose -f podman-compose.yml up -d

# 3. Desplegar en Oracle Cloud (OCI)
bash deploy_oracle.sh
```

## 8. Criterios de aceptación
- [x] `podman build -f Containerfile` construye la imagen sin privilegios de root.
- [x] `RAG/modelos_ia/` se monta de forma persistente dentro del contenedor (`/app/RAG/modelos_ia`).
- [x] `deploy_oracle.sh` aprovisiona la instancia en Oracle Cloud exclusivamente con Podman y tecnología IBM.
