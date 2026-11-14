#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
command -v ffprobe >/dev/null || { echo "FFmpeg/ffprobe é necessário para validar os áudios."; exit 1; }
python3.12 -m venv .venv
.venv/bin/python -m pip install --require-hashes -r requirements.lock
npm --prefix apps/web ci --no-audit --no-fund
npm --prefix apps/web run build
