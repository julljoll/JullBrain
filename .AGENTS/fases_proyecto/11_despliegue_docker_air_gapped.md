# Skill 11 — Despliegue Local On-Premise (Air-Gapped)

## 1. Rol responsable
**R2 — Desarrollador/a Python/API Full-Stack** (aprovisionamiento e infraestructura).

## 2. Propósito
Aprovisionar la instancia local completa del sistema (Docling + RAGFlow + Granite vía Ollama) sobre el hardware mínimo especificado (Capítulo V del anteproyecto), operando sin conexión saliente a internet.

## 3. Entradas
- Hardware según especificación mínima: GPU ≥16GB VRAM, 32GB RAM, 1TB NVMe, Ubuntu Server 24.04 LTS.
- Imágenes de contenedor de RAGFlow, modelo Granite 4.1 (8B recomendado para el piloto) descargado previamente en un entorno con internet y transferido por medio verificado (no por sincronización directa en producción).

## 4. Salidas
- Instancia funcional local: `docling` (librería Python), `ragflow` (contenedor), `ollama` + `granite4.1:8b` (contenedor), base de datos vectorial persistente.
- Documento de verificación de aislamiento de red.

## 5. Dependencias tecnológicas
Docker, Docker Compose, CUDA 12.x, Python 3.11+.

## 6. Reglas obligatorias
1. **Air-gapped en producción:** una vez aprovisionado, el servidor no debe tener salida a internet — solo red local para acceso de operadores autorizados.
2. Toda actualización (modelo, corpus normativo, dependencias) se transfiere por medio físico o VLAN controlada verificada, nunca por `docker pull` directo desde el servidor en producción.
3. El firewall debe bloquear explícitamente tráfico saliente, no solo confiar en la ausencia de configuración de red externa.

## 7. Implementación de referencia

```yaml
# skills/11_despliegue_local/docker-compose.yml
version: "3.8"

services:
  ragflow:
    image: infiniflow/ragflow:latest
    ports:
      - "9380:9380"
    volumes:
      - ragflow_data:/data
    environment:
      - DOC_ENGINE=elasticsearch
    networks:
      - red_interna
    restart: unless-stopped

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_models:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    networks:
      - red_interna
    restart: unless-stopped

  vector_db:
    image: elasticsearch:8.14.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    volumes:
      - vector_data:/usr/share/elasticsearch/data
    networks:
      - red_interna
    restart: unless-stopped

networks:
  red_interna:
    driver: bridge
    internal: true  # sin salida a internet — cumple air-gapped a nivel de red Docker

volumes:
  ragflow_data:
  ollama_models:
  vector_data:
```

```bash
# skills/11_despliegue_local/verificar_aislamiento.sh
#!/bin/bash
# Verifica que el servidor no tenga salida a internet activa (prueba de aislamiento)
echo "Verificando aislamiento de red (debe fallar toda conexión saliente)..."
if curl -s --max-time 3 https://www.google.com > /dev/null; then
  echo "ALERTA: el servidor tiene salida a internet. Revisar firewall antes de cargar expedientes reales."
  exit 1
else
  echo "OK: sin salida a internet detectada."
  exit 0
fi
```

## 8. Criterios de aceptación
- [ ] `docker compose up` levanta los tres servicios sin errores en el hardware mínimo.
- [ ] `verificar_aislamiento.sh` confirma ausencia de salida a internet tras el aprovisionamiento final.
- [ ] Prueba de carga de un expediente simulado de extremo a extremo (Skills 01→08) funcionando en la instancia local.

## 9. Relación con otras skills
Es la infraestructura sobre la que corren todas las skills 01-10. Precede a la Skill 12 (que define quién opera esta instancia en cada sede).
