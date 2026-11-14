"""Integration check: save, terminate the process, restart, retrieve exact bytes."""
import io
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
from urllib.request import Request, urlopen
from urllib.error import URLError
import wave

root = Path(__file__).resolve().parents[1]
def wav_bytes(value):
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wav:
        wav.setparams((1, 2, 8000, 0, 'NONE', 'not compressed'))
        wav.writeframes(value.to_bytes(2, 'little', signed=True) * 8000)
    return buffer.getvalue()

def start(directory):
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    process = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'services.api.main:app',
        '--host', '127.0.0.1', '--port', str(port)], cwd=root,
        env={**os.environ, 'PIANO_DATA_DIR': directory}, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    base = f'http://127.0.0.1:{port}'
    for _ in range(100):
        try:
            with urlopen(base + '/api/health', timeout=1):
                return process, base
        except URLError:
            if process.poll() is not None:
                raise RuntimeError('Server exited')
            time.sleep(.1)
    stop(process)
    raise RuntimeError('Server did not start')

def stop(process):
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()

def request(base, path, body=None, mime='application/json'):
    with urlopen(Request(base + path, data=body, headers={'Content-Type': mime}), timeout=15) as response:
        return response.read()

with tempfile.TemporaryDirectory() as directory:
    process, base = start(directory)
    try:
        a = json.loads(request(base, '/api/audio?filename=base.wav', wav_bytes(0), 'application/octet-stream'))
        b = json.loads(request(base, '/api/audio?filename=piano.wav', wav_bytes(4), 'application/octet-stream'))
        payload = {'name': 'Restart test', 'base_id': a['id'], 'reference_id': b['id']}
        saved = json.loads(request(base, '/api/pairs', json.dumps(payload).encode()))
    finally:
        stop(process)
    process, base = start(directory)
    try:
        assert json.loads(request(base, '/api/pairs'))[0]['id'] == saved['id']
        assert request(base, f"/api/audio/{a['id']}/content") == wav_bytes(0)
        assert request(base, f"/api/audio/{b['id']}/content") == wav_bytes(4)
        print('PASS: pair and exact audio bytes survive actual server process restart')
    finally:
        stop(process)
