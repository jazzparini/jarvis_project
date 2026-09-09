#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# Script de Despliegue de JARVIS en VPS (Debian / Ubuntu / Google Cloud VM)
# ==============================================================================

INSTALL_DIR="/opt/jarvis"
SERVICE_NAME="jarvis"
APP_USER="jarvis"

echo "==> 1. Creando usuario de servicio y directorios..."
if ! id -u "$APP_USER" >/dev/null 2>&1; then
    sudo useradd -r -s /bin/false -d "$INSTALL_DIR" "$APP_USER"
fi

sudo mkdir -p "$INSTALL_DIR" "$INSTALL_DIR/data"
sudo chown -R "$APP_USER:$APP_USER" "$INSTALL_DIR"

echo "==> 2. Copiando archivos del proyecto a $INSTALL_DIR..."
# Asume que se ejecuta desde la raíz del repositorio clonado
sudo cp -r app pyproject.toml README.md "$INSTALL_DIR/"

if [ ! -f "$INSTALL_DIR/.env" ]; then
    if [ -f ".env" ]; then
        sudo cp .env "$INSTALL_DIR/.env"
    else
        sudo cp .env.example "$INSTALL_DIR/.env"
        echo "⚠️  Se creó un archivo .env base en $INSTALL_DIR/.env. Por favor edítalo con tus credenciales."
    fi
fi

echo "==> 3. Configurando entorno virtual Python..."
sudo apt-get update && sudo apt-get install -y python3-venv python3-pip

if [ ! -d "$INSTALL_DIR/.venv" ]; then
    sudo python3 -m venv "$INSTALL_DIR/.venv"
fi

sudo "$INSTALL_DIR/.venv/bin/pip" install --upgrade pip
sudo "$INSTALL_DIR/.venv/bin/pip" install -e "$INSTALL_DIR"

echo "==> 4. Ajustando permisos..."
sudo chown -R "$APP_USER:$APP_USER" "$INSTALL_DIR"
sudo chmod 600 "$INSTALL_DIR/.env"

echo "==> 5. Instalando y arrancando servicio systemd..."
sudo cp deploy/jarvis.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"

echo "==> 6. Estado del servicio:"
sudo systemctl status "$SERVICE_NAME" --no-pager

echo ""
echo "✅ Despliegue completado."
echo "Para ver los logs en tiempo real: sudo journalctl -u $SERVICE_NAME -f"
