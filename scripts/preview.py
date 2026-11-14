"""Adapter for the preview host's standard web-server arguments."""
import argparse
import uvicorn
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
parser = argparse.ArgumentParser()
parser.add_argument('--host', default='127.0.0.1')
parser.add_argument('--port', type=int, default=8000)
parser.add_argument('--strictPort', action='store_true')
args = parser.parse_args()
uvicorn.run('services.api.main:app', host=args.host, port=args.port)
