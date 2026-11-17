"""Development API. Audio is stored locally, not in permanent cloud storage."""
import asyncio
import tempfile
import shutil
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
from services.api.backup import export_backup
from fastapi.staticfiles import StaticFiles
from services.api.storage import Store
from services.api.midi_compare import compare_router
from services.api.piano import piano_router
from services.api.sessions import sessions_router
from services.api.candidate_audio import candidate_audio_router

def create_app(data_dir=None, max_bytes=100 * 1024**2, quota_bytes=1024**3):
    root = Path(data_dir or os.environ.get('PIANO_DATA_DIR', Path(__file__).resolve().parents[2] / 'data'))
    store = Store(root, max_bytes, quota_bytes)
    app = FastAPI(title='P-IA-NO', version='0.0.4', docs_url=None, redoc_url=None)
    app.include_router(store.router())
    app.include_router(compare_router())
    app.include_router(piano_router())
    app.include_router(sessions_router(root))
    app.include_router(candidate_audio_router(root))
    @app.get('/api/backup')
    async def download_backup():
        temporary = Path(tempfile.mkdtemp(prefix='piano-export-'))
        path = temporary / 'P-IA-NO-dados.zip'
        try:
            async with store.lock:
                await asyncio.to_thread(export_backup, store, path)
        except Exception:
            shutil.rmtree(temporary)
            raise HTTPException(409, 'Não foi possível criar o backup. Verifique a integridade e a disponibilidade dos arquivos.')
        return FileResponse(path, filename='P-IA-NO-dados.zip', media_type='application/zip',
                            headers={'Cache-Control': 'no-store'},
                            background=BackgroundTask(shutil.rmtree, temporary))

    @app.get('/api/health')
    def health():
        return {'status': 'ok', 'service': 'p-ia-no-api', 'version': '0.0.4',
                'capabilities': {'uploads': True, 'training': False, 'arrangement': False, 'experimental_midi_piano': True},
                'storage': 'development-local'}
    web_dist = Path(__file__).resolve().parents[2] / 'apps/web/dist'
    if web_dist.is_dir():
        app.mount('/', StaticFiles(directory=web_dist, html=True), name='web')
    return app
app = create_app()
