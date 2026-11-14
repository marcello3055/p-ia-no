#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3.12 -m venv .venv
.venv/bin/python -m pip install --require-hashes -r requirements.lock
npm --prefix apps/web ci --no-audit --no-fund
npm --prefix apps/web run build
