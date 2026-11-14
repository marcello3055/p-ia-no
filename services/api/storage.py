"""Single-user development storage. Never expose publicly without authentication."""
import asyncio
import hashlib
import json
import math
import sqlite3
import subprocess
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, field_validator

class PairInput(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    base_id: str
    reference_id: str

    @field_validator('name')
    @classmethod
    def clean_name(cls, value):
        value = value.strip()
        if not value:
            raise ValueError('Informe um nome para o par.')
        return value

class Store:
    def __init__(self, root: Path, max_bytes=100 * 1024**2, quota_bytes=1024**3):
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.files = self.root / 'audio'
        self.files.mkdir(exist_ok=True, mode=0o700)
        self.db_path = self.root / 'piano.sqlite3'
        self.max_bytes = max_bytes
        self.quota_bytes = quota_bytes
        self.lock = asyncio.Lock()  # one API process only in this development version
        with self.connect() as db:
            db.executescript('''
            CREATE TABLE IF NOT EXISTS audio (
                id TEXT PRIMARY KEY, name TEXT NOT NULL, filename TEXT NOT NULL,
                sha256 TEXT UNIQUE NOT NULL, size INTEGER NOT NULL,
                duration REAL NOT NULL, mime TEXT NOT NULL, created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS pairs (
                id TEXT PRIMARY KEY, name TEXT NOT NULL,
                base_id TEXT NOT NULL REFERENCES audio(id),
                reference_id TEXT NOT NULL REFERENCES audio(id), created_at TEXT NOT NULL,
                UNIQUE(base_id, reference_id)
            );
            ''')

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.db_path)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON')
        try:
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    def get_audio(self, file_id):
        with self.connect() as db:
            row = db.execute('SELECT * FROM audio WHERE id=?', (file_id,)).fetchone()
        if row is None:
            raise HTTPException(404, 'Áudio não encontrado.')
        return dict(row)

    @staticmethod
    def public(row):
        return {key: row[key] for key in ('id', 'name', 'size', 'duration', 'created_at')}

    @staticmethod
    def probe(path, extension):
        try:
            result = subprocess.run([
                'ffprobe', '-v', 'error', '-protocol_whitelist', 'file',
                '-show_entries', 'format=format_name,duration:stream=codec_type',
                '-of', 'json', str(path)
            ], capture_output=True, timeout=10, check=True)
            info = json.loads(result.stdout)
            duration = float(info['format']['duration'])
            formats = info['format']['format_name'].split(',')
            if extension[1:] not in formats or not any(s.get('codec_type') == 'audio' for s in info.get('streams', [])):
                raise ValueError('Unexpected audio format')
            if not math.isfinite(duration) or not 0 < duration <= 1800:
                raise ValueError('Unsupported duration')
            return duration
        except FileNotFoundError:
            raise HTTPException(503, 'Validador de áudio indisponível no servidor.')
        except (subprocess.SubprocessError, ValueError, KeyError, TypeError):
            raise HTTPException(422, 'Áudio inválido, formato incompatível ou duração superior a 30 minutos.')

    def router(self):
        router = APIRouter(prefix='/api')

        @router.get('/audio')
        def list_audio():
            with self.connect() as db:
                rows = db.execute('SELECT * FROM audio ORDER BY created_at DESC').fetchall()
            return [self.public(row) for row in rows]

        @router.post('/audio')
        async def upload(request: Request, filename: str):
            # Deliberately raw bytes: no multipart buffering or extra dependency.
            if request.headers.get('content-type', '').split(';')[0] != 'application/octet-stream':
                raise HTTPException(415, 'Envie o conteúdo binário do áudio.')
            if not filename or len(filename) > 240 or '/' in filename or '\\' in filename or any(ord(c) < 32 for c in filename):
                raise HTTPException(422, 'Nome de arquivo inválido.')
            extension = Path(filename).suffix.lower()
            if extension not in {'.mp3', '.wav', '.flac'}:
                raise HTTPException(415, 'Selecione MP3, WAV ou FLAC.')
            length = request.headers.get('content-length')
            if length:
                try:
                    if int(length) < 1 or int(length) > self.max_bytes:
                        raise HTTPException(413, 'Arquivo vazio ou acima do limite de 100 MiB.')
                except ValueError:
                    raise HTTPException(400, 'Tamanho de envio inválido.')
            async with self.lock:
                used = sum(p.stat().st_size for p in self.files.iterdir() if p.is_file())
                file_id = uuid4().hex
                temporary = self.files / (file_id + '.part')
                final = self.files / (file_id + extension)
                size = 0
                digest = hashlib.sha256()
                committed = False
                try:
                    with temporary.open('xb') as output:
                        async for chunk in request.stream():
                            size += len(chunk)
                            if size > self.max_bytes:
                                raise HTTPException(413, 'Arquivo acima do limite de 100 MiB.')
                            if used + size > self.quota_bytes:
                                raise HTTPException(507, 'Armazenamento de desenvolvimento cheio (limite de 1 GiB).')
                            digest.update(chunk)
                            output.write(chunk)
                    if not size:
                        raise HTTPException(422, 'Arquivo vazio.')
                    sha = digest.hexdigest()
                    with self.connect() as db:
                        old = db.execute('SELECT * FROM audio WHERE sha256=?', (sha,)).fetchone()
                    if old:
                        if Path(old['filename']).suffix != extension:
                            raise HTTPException(422, 'A extensão não corresponde ao formato do áudio.')
                        if not (self.files / old['filename']).is_file():
                            raise HTTPException(409, 'Registro encontrado, mas o arquivo está ausente. Recuperação necessária.')
                        return self.public(old)
                    duration = await asyncio.to_thread(self.probe, temporary, extension)
                    mime = {'.wav': 'audio/wav', '.mp3': 'audio/mpeg', '.flac': 'audio/flac'}[extension]
                    temporary.replace(final)
                    row = (file_id, filename, final.name, sha, size, duration, mime, datetime.now(timezone.utc).isoformat())
                    with self.connect() as db:
                        db.execute('INSERT INTO audio VALUES (?,?,?,?,?,?,?,?)', row)
                    committed = True
                    return self.public(self.get_audio(file_id))
                finally:
                    temporary.unlink(missing_ok=True)
                    if not committed:
                        final.unlink(missing_ok=True)

        @router.get('/audio/{file_id}/content')
        def content(file_id: str):
            row = self.get_audio(file_id)
            path = self.files / row['filename']
            if not path.is_file():
                raise HTTPException(404, 'O arquivo não está mais disponível neste ambiente.')
            return FileResponse(path, media_type=row['mime'], headers={'Cache-Control': 'private, no-store', 'X-Content-Type-Options': 'nosniff'})

        @router.get('/pairs')
        def list_pairs():
            with self.connect() as db:
                rows = db.execute('SELECT * FROM pairs ORDER BY created_at DESC').fetchall()
            return [dict(row) for row in rows]

        @router.post('/pairs')
        def create_pair(pair: PairInput):
            self.get_audio(pair.base_id)
            self.get_audio(pair.reference_id)
            with self.connect() as db:
                # Retrying a save must not create duplicate pairs.
                db.execute('INSERT OR IGNORE INTO pairs VALUES (?,?,?,?,?)',
                           (uuid4().hex, pair.name, pair.base_id, pair.reference_id, datetime.now(timezone.utc).isoformat()))
                row = db.execute('SELECT * FROM pairs WHERE base_id=? AND reference_id=?',
                                 (pair.base_id, pair.reference_id)).fetchone()
            return dict(row)
        return router
