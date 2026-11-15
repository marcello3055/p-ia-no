#!/usr/bin/env bash
set -eu
cd "$(dirname "$0")/.."
uv venv .venv-audio --python 3.12
# Explicit ONNX environment: upstream metadata otherwise pulls incompatible TF.
uv pip install --python .venv-audio/bin/python --no-deps -r experiments/audio-requirements.lock
