"""Development API. Audio is stored locally, not in permanent cloud storage."""
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from services.api.storage import Store

def create_app(data_dir=None, max_bytes=100 * 1024**2, quota_bytes=1024**3):
    root = Path(data_dir or os.environ.get('PIANO_DATA_DIR', Path(__file__).resolve().parents[2] / 'data'))
    store = Store(root, max_bytes, quota_bytes)
    app = FastAPI(title='P-IA-NO', version='0.0.4', docs_url=None, redoc_url=None)
    app.include_router(store.router())
    @app.get('/api/health')
    def health():
        return {'status': 'ok', 'service': 'p-ia-no-api', 'version': '0.0.4',
                'capabilities': {'uploads': True, 'training': False, 'arrangement': False},
                'storage': 'development-local'}
    web_dist = Path(__file__).resolve().parents[2] / 'apps/web/dist'
    if web_dist.is_dir():
        app.mount('/', StaticFiles(directory=web_dist, html=True), name='web')
    return app
app = create_app()
