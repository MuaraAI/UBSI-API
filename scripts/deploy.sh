#!/usr/bin/env bash
set -e

VPS_HOST="curzy-vps-tencent"
REMOTE_DIR="/home/ubuntu/ubsi-api"
REMOTE_VENV="/home/ubuntu/.venvs/ubsi-api"

echo "=== 1. Checking SSH connection to ${VPS_HOST} ==="
ssh -q -o BatchMode=yes -o ConnectTimeout=5 "${VPS_HOST}" "echo 'SSH connection OK'" || {
    echo "ERROR: Cannot connect to ${VPS_HOST} via SSH."
    exit 1
}

echo "=== 2. Preparing remote directory ==="
ssh "${VPS_HOST}" "mkdir -p ${REMOTE_DIR}"

echo "=== 3. Syncing project files ==="
rsync -avz --delete \
    --exclude='.git/' \
    --exclude='.venv/' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='.pytest_cache/' \
    --exclude='tests/' \
    --exclude='.env' \
    ./ "${VPS_HOST}:${REMOTE_DIR}/"

# Sync .env if present locally and absent remotely
if [ -f .env ]; then
    echo "Syncing .env to VPS..."
    rsync -avz .env "${VPS_HOST}:${REMOTE_DIR}/.env"
    ssh "${VPS_HOST}" "chmod 600 '${REMOTE_DIR}/.env'"
fi

echo "=== 4. Setting up Python venv & installing dependencies on VPS ==="
ssh "${VPS_HOST}" "
    if [ ! -d '${REMOTE_VENV}' ]; then
        echo 'Creating virtualenv with Python 3.12 via uv...'
        uv venv '${REMOTE_VENV}' --python 3.12
    fi
    echo 'Installing / updating requirements...'
    uv pip install --python '${REMOTE_VENV}/bin/python' -r '${REMOTE_DIR}/requirements.txt'
"

echo "=== 5. Starting / Restarting service with PM2 ==="
ssh "${VPS_HOST}" "
    cd '${REMOTE_DIR}'
    pm2 restart ecosystem.config.cjs 2>/dev/null || pm2 start ecosystem.config.cjs
    pm2 save
"

echo "=== 6. Verifying health check on VPS ==="
sleep 4
ssh "${VPS_HOST}" "curl -s http://127.0.0.1:8300/health | grep -q '\"status\":\"ok\"' && echo 'Health Check: OK!' || (echo 'Health Check FAILED!'; pm2 logs ubsi-api --lines 20 --nostream; exit 1)"

echo "=== Deployment Completed Successfully! ==="
