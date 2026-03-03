#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# deploy.sh — Instalación completa del Gestor Interno Anto
# Correr como root o con sudo en Debian minimal recién instalado
# Uso: bash deploy.sh
# ─────────────────────────────────────────────────────────────────────────────

set -e  # Detener si algo falla

# ─── Detectar IP de la máquina ───────────────────────────────────────────────
IP=$(hostname -I | awk '{print $1}')
echo ""
echo "=========================================="
echo "  Gestor Interno Anto — Instalador"
echo "  IP detectada: $IP"
echo "=========================================="
echo ""

# ─── 1. Dependencias del sistema ─────────────────────────────────────────────
echo "[1/6] Instalando dependencias del sistema..."
apt-get update -qq
apt-get install -y git python3 python3-pip python3-venv curl wget -qq

# Node.js 20 LTS
curl -fsSL https://deb.nodesource.com/setup_20.x | bash - -qq
apt-get install -y nodejs -qq

echo "      ✓ Python $(python3 --version), Node $(node --version), npm $(npm --version)"

# ─── 2. Clonar repositorio ───────────────────────────────────────────────────
echo "[2/6] Clonando repositorio..."
REPO_DIR="/opt/gestor-anto"

if [ -d "$REPO_DIR" ]; then
  echo "      Repositorio ya existe, actualizando..."
  cd "$REPO_DIR" && git pull
else
  git clone https://github.com/dpa23/GESTORINTERNO-ANTO.git "$REPO_DIR"
  cd "$REPO_DIR"
fi

# ─── 3. Configurar IP en el frontend ─────────────────────────────────────────
echo "[3/6] Configurando IP $IP en el frontend..."

# Reemplaza la IP en menu.js y pedidos.js y gerencia.js
for FILE in frontend-sys/src/stores/menu.js \
            frontend-sys/src/stores/pedidos.js \
            frontend-sys/src/stores/gerencia.js; do
  if [ -f "$FILE" ]; then
    # Reemplaza cualquier IP:puerto en las constantes API y WS
    sed -i "s|http://[0-9.]*:8000|http://$IP:8000|g" "$FILE"
    sed -i "s|ws://[0-9.]*:8000|ws://$IP:8000|g" "$FILE"
    echo "      ✓ $FILE"
  fi
done

# ─── 4. Backend — venv y dependencias ────────────────────────────────────────
echo "[4/6] Configurando backend Python..."
cd "$REPO_DIR/backend-sys"
python3 -m venv ~/venv
source ~/venv/bin/activate
pip install fastapi uvicorn --quiet

# Crear carpeta de outputs si no existe
mkdir -p output-back
touch output-back/registros.json
echo "[]" > output-back/registros.json
touch output-back/pedidos_act.json
echo "[]" > output-back/pedidos_act.json

echo "      ✓ Backend listo"

# ─── 5. Frontend — instalar dependencias y build ─────────────────────────────
echo "[5/6] Configurando frontend Vue..."
cd "$REPO_DIR/frontend-sys"
npm install --silent

echo "      ✓ Frontend listo"

# ─── 6. Crear servicios systemd ──────────────────────────────────────────────
echo "[6/6] Configurando arranque automático con systemd..."

# Servicio backend
cat > /etc/systemd/system/anto-backend.service << EOF
[Unit]
Description=Gestor Interno Anto — Backend FastAPI
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

# Servicio frontend
cat > /etc/systemd/system/anto-frontend.service << EOF
[Unit]
Description=Gestor Interno Anto — Frontend Vue
After=network.target anto-backend.service

[Service]
User=root
WorkingDirectory=$REPO_DIR/frontend-sys
ExecStart=/usr/bin/npm run dev -- --host
Restart=always
RestartSec=3
Environment=NODE_ENV=development

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable anto-backend anto-frontend
systemctl start anto-backend anto-frontend

# ─── Resumen final ────────────────────────────────────────────────────────────
echo ""
echo "=========================================="
echo "  ✅ Instalación completa"
echo ""
echo "  Backend:  http://$IP:8000"
echo "  Frontend: http://$IP:5173"
echo ""
echo "  Vistas disponibles:"
echo "  → Cocina:    http://$IP:5173/cocina"
echo "  → Camarero:  http://$IP:5173/camarero"
echo "  → Caja:      http://$IP:5173/caja"
echo "  → Pedidos:   http://$IP:5173/pedidos"
echo "  → Gerencia:  http://$IP:5173/gerencia"
echo ""
echo "  Comandos útiles:"
echo "  sudo systemctl status anto-backend"
echo "  sudo systemctl status anto-frontend"
echo "  sudo systemctl restart anto-backend"
echo "=========================================="
