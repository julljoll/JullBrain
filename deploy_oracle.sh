#!/bin/bash
# deploy_oracle.sh — JullBrain v0.1.0
# Despliegue automatizado en Oracle Cloud ARM Free Tier
# Ubuntu 22.04 LTS / Ampere A1 (aarch64)
# Ejecutar con: bash deploy_oracle.sh

set -euo pipefail

REPO_URL="https://github.com/julljoll/JullBrain.git"
INSTALL_DIR="/opt/jullbrain"
SERVICE_USER="ubuntu"
PORT=8050

echo "════════════════════════════════════════════════════════"
echo "  JullBrain v0.1.0 — Despliegue Oracle Cloud ARM"
echo "════════════════════════════════════════════════════════"

# 1. Actualizar sistema base
echo "[1/8] Actualizando paquetes del sistema..."
sudo apt-get update -qq
sudo apt-get upgrade -yq
sudo apt-get install -yq python3.11 python3.11-venv python3.11-dev \
    git nginx certbot python3-certbot-nginx curl build-essential

# 2. Clonar o actualizar repositorio
echo "[2/8] Clonando/actualizando repositorio..."
if [ -d "$INSTALL_DIR/.git" ]; then
    cd "$INSTALL_DIR" && git pull origin main
else
    sudo git clone "$REPO_URL" "$INSTALL_DIR"
    sudo chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"
fi
cd "$INSTALL_DIR"

# 3. Crear entorno virtual Python 3.11 ARM
echo "[3/8] Creando entorno virtual Python 3.11..."
python3.11 -m venv .venv_oracle
source .venv_oracle/bin/activate

# 4. Instalar torch CPU para ARM (índice especial requerido)
echo "[4/8] Instalando PyTorch para CPU ARM..."
pip install --upgrade pip --quiet
pip install torch --index-url https://download.pytorch.org/whl/cpu --quiet

# 5. Instalar dependencias Oracle
echo "[5/8] Instalando dependencias de Oracle Cloud..."
pip install -r requirements_oracle.txt --quiet

# 6. Crear carpetas RAG requeridas
echo "[6/8] Creando estructura de directorios RAG..."
mkdir -p RAG/datos_brutos RAG/Informacion_docling_rag RAG/notebooks_db RAG/lightrag_db
touch RAG/notebooks_db/.gitkeep RAG/lightrag_db/.gitkeep

# 7. Configurar servicio systemd
echo "[7/8] Configurando servicio systemd jullbrain..."
sudo tee /etc/systemd/system/jullbrain.service > /dev/null << EOF
[Unit]
Description=JullBrain v0.1.0 Legal-RAG API
After=network.target
Wants=network-online.target

[Service]
Type=exec
User=${SERVICE_USER}
WorkingDirectory=${INSTALL_DIR}
Environment=JULLBRAIN_ENV=oracle
Environment=HF_HUB_DISABLE_XET_STORAGE=1
ExecStart=${INSTALL_DIR}/.venv_oracle/bin/gunicorn app:app \
    --workers 2 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 127.0.0.1:${PORT} \
    --timeout 300 \
    --log-level info \
    --access-logfile - \
    --error-logfile -
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable jullbrain
sudo systemctl start jullbrain

# 8. Verificar que el servicio está activo
echo "[8/8] Verificando servicio..."
sleep 3
if systemctl is-active --quiet jullbrain; then
    echo "✅ Servicio jullbrain activo en puerto ${PORT}."
    echo ""
    echo "╔══════════════════════════════════════════════════════╗"
    echo "║  JullBrain v0.1.0 desplegado exitosamente             ║"
    echo "║  API interna: http://127.0.0.1:${PORT}                  ║"
    echo "║  Próximo paso [MANUAL]: configurar nginx + certbot   ║"
    echo "╚══════════════════════════════════════════════════════╝"
else
    echo "❌ Error: el servicio no arrancó. Revisa con: journalctl -u jullbrain -n 50"
    exit 1
fi
