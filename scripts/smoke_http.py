"""Launch a temporary server, check built UI/API, then always terminate it."""
import json, socket, subprocess, sys, time
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError
root = Path(__file__).resolve().parents[1]
assert (root / 'apps/web/dist/index.html').is_file(), 'Build frontend first'
with socket.socket() as sock:
    sock.bind(('127.0.0.1', 0))
    port = sock.getsockname()[1]
process = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'services.api.main:app',
                            '--host', '127.0.0.1', '--port', str(port)], cwd=root,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
base = f'http://127.0.0.1:{port}'
try:
    for attempt in range(100):
        if process.poll() is not None:
            raise RuntimeError('Server stopped unexpectedly')
        try:
            with urlopen(base + '/api/health', timeout=1) as response:
                data = json.load(response)
            break
        except URLError:
            time.sleep(0.1)
    else:
        raise RuntimeError('Server did not start')
    assert data['status'] == 'ok' and data['service'] == 'p-ia-no-api'
    with urlopen(base, timeout=2) as response:
        assert response.status == 200 and 'P-IA-NO' in response.read().decode()
    for asset in (root / 'apps/web/dist/assets').iterdir():
        with urlopen(base + '/assets/' + asset.name, timeout=2) as response:
            assert response.status == 200 and response.read() == asset.read_bytes()
    print('PASS: real HTTP API, built HTML and every compiled asset')
finally:
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
