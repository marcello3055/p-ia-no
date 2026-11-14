"""Portable data-only backups. No SQL, executable objects or arbitrary extraction."""
import hashlib
import json
import math
import os
import shutil
import stat
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from services.api.storage import Store

MAX_TOTAL = 1024**3
MAX_FILE = 100 * 1024**2
MAX_MANIFEST = 8 * 1024**2
MAX_ENTRIES = 10000
MIMES = {'.wav': 'audio/wav', '.mp3': 'audio/mpeg', '.flac': 'audio/flac'}
AUDIO_COLUMNS = ('id', 'name', 'filename', 'sha256', 'size', 'duration', 'mime', 'created_at')
PAIR_COLUMNS = ('id', 'name', 'base_id', 'reference_id', 'created_at')

class Audio(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    id: str = Field(pattern=r'^[a-f0-9]{32}$')
    name: str = Field(min_length=1, max_length=240)
    filename: str
    sha256: str = Field(pattern=r'^[a-f0-9]{64}$')
    size: int = Field(gt=0, le=MAX_FILE)
    duration: float = Field(gt=0, le=1800, allow_inf_nan=False)
    mime: str
    created_at: str = Field(max_length=64)

    @model_validator(mode='after')
    def validate_audio(self):
        extension = Path(self.filename).suffix
        if extension not in MIMES or self.filename != self.id + extension or self.mime != MIMES[extension]:
            raise ValueError('Nome interno ou formato inválido.')
        if '/' in self.name or '\\' in self.name or any(ord(c) < 32 for c in self.name):
            raise ValueError('Nome original inválido.')
        datetime.fromisoformat(self.created_at)
        return self

class Pair(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    id: str = Field(pattern=r'^[a-f0-9]{32}$')
    name: str = Field(min_length=1, max_length=120)
    base_id: str = Field(pattern=r'^[a-f0-9]{32}$')
    reference_id: str = Field(pattern=r'^[a-f0-9]{32}$')
    created_at: str = Field(max_length=64)

    @field_validator('created_at')
    @classmethod
    def validate_date(cls, value):
        datetime.fromisoformat(value)
        return value

class Manifest(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    schema_version: int
    created_at: str = Field(max_length=64)
    audio: list[Audio] = Field(max_length=MAX_ENTRIES - 1)
    pairs: list[Pair] = Field(max_length=MAX_ENTRIES)

    @model_validator(mode='after')
    def validate_graph(self):
        if self.schema_version != 1:
            raise ValueError('Versão de backup não suportada.')
        datetime.fromisoformat(self.created_at)
        ids = {a.id for a in self.audio}
        if len(ids) != len(self.audio) or len({a.sha256 for a in self.audio}) != len(self.audio):
            raise ValueError('Áudios duplicados no manifesto.')
        if len({p.id for p in self.pairs}) != len(self.pairs) or len({(p.base_id, p.reference_id) for p in self.pairs}) != len(self.pairs):
            raise ValueError('Pares duplicados.')
        if any(p.base_id not in ids or p.reference_id not in ids for p in self.pairs):
            raise ValueError('Par com referência ausente.')
        if sum(a.size for a in self.audio) > MAX_TOTAL:
            raise ValueError('Backup excede a quota de 1 GiB.')
        return self

def checked_copy(source, target, record):
    digest = hashlib.sha256()
    size = 0
    while chunk := source.read(1024**2):
        size += len(chunk)
        if size > record.size:
            raise ValueError('Tamanho de áudio divergente.')
        target.write(chunk)
        digest.update(chunk)
    if size != record.size or digest.hexdigest() != record.sha256:
        raise ValueError('Falha de integridade SHA-256 ou tamanho.')

def export_backup(store: Store, destination: Path):
    """Snapshot immutable audio plus a transactionally consistent set of records.

    Caller must stop external writers (CLI) or hold store.lock (API).
    """
    destination = Path(destination).absolute()
    if destination.exists() or destination.is_symlink():
        raise FileExistsError('O destino já existe; nenhum arquivo foi sobrescrito.')
    with store.connect() as db:
        db.execute('BEGIN')
        audio = [dict(row) for row in db.execute('SELECT * FROM audio ORDER BY id')]
        pairs = [dict(row) for row in db.execute('SELECT * FROM pairs ORDER BY id')]
    manifest = Manifest.model_validate({'schema_version': 1, 'created_at': datetime.now(timezone.utc).isoformat(), 'audio': audio, 'pairs': pairs})
    metadata = manifest.model_dump_json(indent=2).encode()
    if len(metadata) > MAX_MANIFEST:
        raise ValueError('Manifesto grande demais.')
    fd, temporary_name = tempfile.mkstemp(prefix='.piano-backup-', dir=destination.parent)
    os.close(fd)
    temporary = Path(temporary_name)
    try:
        with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_STORED) as archive:
            archive.writestr('manifest.json', metadata)
            for record in manifest.audio:
                path = store.files / record.filename
                if path.is_symlink():
                    raise ValueError('Link simbólico não permitido.')
                with path.open('rb') as source, archive.open('audio/' + record.filename, 'w') as target:
                    checked_copy(source, target, record)
        # Atomic publication, no overwrite even if another writer creates destination.
        os.link(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)
    return {'audio_count': len(manifest.audio), 'pair_count': len(manifest.pairs)}

def restore_backup(archive_path: Path, destination: Path):
    """Only creates a new data directory. Removes its own output on any failure."""
    destination = Path(destination).absolute()
    if destination.exists() or destination.is_symlink():
        raise FileExistsError('Restaure em uma pasta nova; dados existentes não serão alterados.')
    if Path(archive_path).stat().st_size > MAX_TOTAL + MAX_MANIFEST + 16 * 1024**2:
        raise ValueError('Arquivo de backup grande demais.')
    with zipfile.ZipFile(archive_path) as archive:
        entries = archive.infolist()
        names = [entry.filename for entry in entries]
        if len(names) > MAX_ENTRIES or len(set(names)) != len(names) or 'manifest.json' not in names:
            raise ValueError('Estrutura de backup inválida ou duplicada.')
        for entry in entries:
            kind = stat.S_IFMT(entry.external_attr >> 16)
            if kind not in (0, stat.S_IFREG) or entry.flag_bits & 1 or entry.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
                raise ValueError('Tipo de entrada não permitido.')
        if archive.getinfo('manifest.json').file_size > MAX_MANIFEST:
            raise ValueError('Manifesto grande demais.')
        manifest = Manifest.model_validate_json(archive.read('manifest.json'))
        expected = {'manifest.json'} | {'audio/' + record.filename for record in manifest.audio}
        if set(names) != expected:
            raise ValueError('Arquivos inesperados ou ausentes; caminhos não autorizados.')
        for record in manifest.audio:
            if archive.getinfo('audio/' + record.filename).file_size != record.size:
                raise ValueError('Tamanho declarado divergente.')
        destination.mkdir(mode=0o700)  # exclusive; never merge or replace
        try:
            store = Store(destination)
            for record in manifest.audio:
                path = store.files / record.filename
                with archive.open('audio/' + record.filename) as source, path.open('xb') as target:
                    checked_copy(source, target, record)
                duration = Store.probe(path, path.suffix)
                if not math.isclose(duration, record.duration, abs_tol=.1):
                    raise ValueError('Duração real diverge do manifesto.')
            with store.connect() as db:
                db.executemany('INSERT INTO audio VALUES (?,?,?,?,?,?,?,?)',
                               [tuple(getattr(record, col) for col in AUDIO_COLUMNS) for record in manifest.audio])
                db.executemany('INSERT INTO pairs VALUES (?,?,?,?,?)',
                               [tuple(getattr(record, col) for col in PAIR_COLUMNS) for record in manifest.pairs])
        except BaseException:
            shutil.rmtree(destination)
            raise
    return {'audio_count': len(manifest.audio), 'pair_count': len(manifest.pairs)}
