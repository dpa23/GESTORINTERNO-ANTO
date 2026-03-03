#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# deploy.sh — Instalación completa del Gestor Interno Anto
# Correr como root en Debian minimal recién instalado
# Uso: bash deploy.sh
# ─────────────────────────────────────────────────────────────────────────────

set -e

# ─── Detectar IP ─────────────────────────────────────────────────────────────
IP=$(hostname -I | awk '{print $1}')
echo ""
echo "=========================================="
echo "  Gestor Interno Anto — Instalador"
echo "  IP detectada: $IP"
echo "=========================================="
echo ""

# ─── 1. Dependencias del sistema ─────────────────────────────────────────────
echo "[1/7] Instalando dependencias del sistema..."
apt-get update
apt-get install -y git python3 python3-pip python3-venv curl wget
echo "      OK sistema"

# ─── 2. Node.js 20 LTS ───────────────────────────────────────────────────────
echo "[2/7] Instalando Node.js 20..."
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs
echo "      OK Node $(node --version)"

# ─── 3. Clonar repositorio ───────────────────────────────────────────────────
echo "[3/7] Clonando repositorio..."
REPO_DIR="/opt/gestor-anto"

if [ -d "$REPO_DIR" ]; then
    echo "      Repositorio ya existe, actualizando..."
    cd "$REPO_DIR" && git pull
else
    git clone https://github.com/dpa23/GESTORINTERNO-ANTO.git "$REPO_DIR"
    cd "$REPO_DIR"
fi
echo "      OK repositorio en $REPO_DIR"

# ─── 4. Configurar IP en el frontend ─────────────────────────────────────────
echo "[4/7] Configurando IP $IP en el frontend..."

for FILE in frontend-sys/src/stores/menu.js \
            frontend-sys/src/stores/pedidos.js \
            frontend-sys/src/stores/gerencia.js; do
    if [ -f "$REPO_DIR/$FILE" ]; then
        sed -i "s|http://[0-9.]*:8000|http://$IP:8000|g" "$REPO_DIR/$FILE"
        sed -i "s|ws://[0-9.]*:8000|ws://$IP:8000|g" "$REPO_DIR/$FILE"
        echo "      OK $FILE"
    fi
done

# ─── 5. Backend ───────────────────────────────────────────────────────────────
echo "[5/7] Configurando backend Python..."
cd "$REPO_DIR/backend-sys"
python3 -m venv ~/venv
source ~/venv/bin/activate
pip install fastapi uvicorn

mkdir -p output-back
if [ ! -f output-back/registros.json ];   then echo "[]" > output-back/registros.json;   fi
if [ ! -f output-back/pedidos_act.json ]; then echo "[]" > output-back/pedidos_act.json; fi
echo "      OK backend"

# ─── 6. Frontend ──────────────────────────────────────────────────────────────
echo "[6/7] Instalando dependencias frontend..."
cd "$REPO_DIR/frontend-sys"
npm install
echo "      OK frontend"

# ─── 7. Systemd ───────────────────────────────────────────────────────────────
echo "[7/7] Configurando servicios systemd..."

cat > /etc/systemd/system/anto-backend.service << EOF
[Unit]
Description=Gestor Interno Anto Backend
After=network.target

[Service]
User=root
WorkingDirectory=$REPO_DIR/backend-sys
ExecStart=/root/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

cat > /etc/systemd/system/anto-frontend.service << EOF
[Unit]
Description=Gestor Interno Anto Frontend
After=network.target anto-backend.service

[Service]
User=root
WorkingDirectory=$REPO_DIR/frontend-sys
ExecStart=/usr/bin/npm run dev -- --host
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable anto-backend anto-frontend
systemctl start anto-backend anto-frontend

# ─── Resumen ──────────────────────────────────────────────────────────────────
echo ""
echo "=========================================="
echo "  Instalacion completa"
echo ""
echo "  Backend:  http://$IP:8000"
echo "  Frontend: http://$IP:5173"
echo ""
echo "  Cocina:   http://$IP:5173/cocina"
echo "  Camarero: http://$IP:5173/camarero"
echo "  Caja:     http://$IP:5173/caja"
echo "  Pedidos:  http://$IP:5173/pedidos"
echo "  Gerencia: http://$IP:5173/gerencia"
echo ""
echo "  Para actualizar:"
echo "  cd $REPO_DIR && git pull && systemctl restart anto-backend anto-frontend"
echo "=========================================="

echo "  Comandos útiles:"
echo "  sudo systemctl status anto-backend"
echo "  sudo systemctl status anto-frontend"
echo "  sudo systemctl restart anto-backend"
echo "=========================================="
