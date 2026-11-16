"""Private evolution-session archives. No code execution or generic ZIP extraction."""
import fcntl
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import re
import shutil
import tempfile
import zipfile
from packages.music.midi import MAX_BYTES
from packages.music.session import run_session

MAX_TOTAL = 64 * 1024 * 1024
MAX_ENTRY = 16 * 1024 * 1024
MAX_FILES = 10004
NAME = re.compile(r'(session\.json|source\.mid|reference\.mid|generation-[0-9]{5}\.json)\Z')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def environment():
    return {'python': platform.python_version(), 'mido': importlib.metadata.version('mido')}


def read_bounded(path, limit):
    if path.is_symlink() or not path.is_file():
        raise ValueError('Arquivo regular obrigatório.')
    with path.open('rb') as handle:
        data = handle.read(limit + 1)
    if len(data) > limit:
        raise ValueError('Arquivo excede limite do pacote.')
    return data


def validate_snapshot(folder):
    settings = json.loads((folder/'session.json').read_text())
    checkpoints = list(folder.glob('generation-*.json'))
    if not checkpoints:
        raise ValueError('Sessão sem checkpoint completo.')
    return run_session((folder/'source.mid').read_bytes(), (folder/'reference.mid').read_bytes(),
                       folder, len(checkpoints)-1, resume=True, seed=settings['seed'])


def export_session(directory, source, reference, output):
    directory, source, reference, output = map(Path, (directory, source, reference, output))
    if output.exists():
        raise FileExistsError('Pacote de destino já existe.')
    if not directory.is_dir():
        raise ValueError('Sessão inexistente.')
    with (directory/'.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ValueError('Sessão em execução; exporte entre gerações ou após concluir.') from exc
        paths = [directory/'session.json', *sorted(directory.glob('generation-*.json'))]
        if len(paths) + 2 > MAX_FILES:
            raise ValueError('Quantidade de arquivos excedida.')
        files = {'source.mid': read_bounded(source, MAX_BYTES),
                 'reference.mid': read_bounded(reference, MAX_BYTES)}
        for path in paths:
            if not NAME.fullmatch(path.name):
                raise ValueError('Nome de checkpoint inválido.')
            files[path.name] = read_bounded(path, MAX_ENTRY)
            if sum(map(len, files.values())) > MAX_TOTAL:
                raise ValueError('Sessão excede 64 MiB; divida o projeto antes de exportar.')
    with tempfile.TemporaryDirectory() as name:
        snapshot = Path(name)
        for filename, data in files.items():
            (snapshot/filename).write_bytes(data)
        result = validate_snapshot(snapshot)
    manifest = {'version': 1, 'environment': environment(),
                'files': {name: {'bytes': len(data), 'sha256': sha(data)} for name, data in files.items()}}
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.session-export-', dir=output.parent)
    os.close(fd)
    try:
        with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr('manifest.json', json.dumps(manifest, sort_keys=True))
            for name, data in files.items():
                archive.writestr(name, data)
        if Path(temporary).stat().st_size > MAX_TOTAL:
            raise ValueError('Pacote excede 64 MiB.')
        with open(temporary, 'rb') as handle:
            os.fsync(handle.fileno())
        os.link(temporary, output)  # atomic publish, fails rather than overwrite
    finally:
        Path(temporary).unlink(missing_ok=True)
    return {'archive': str(output), 'generation': result['generation'], 'files': len(files)}


def restore_session(archive_path, destination):
    archive_path, destination = Path(archive_path), Path(destination)
    if destination.exists():
        raise FileExistsError('Restauração exige pasta nova.')
    if archive_path.stat().st_size > MAX_TOTAL:
        raise ValueError('Pacote excede 64 MiB.')
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix='.session-restore-', dir=destination.parent))
    try:
        with zipfile.ZipFile(archive_path) as archive:
            entries = archive.infolist()
            names = [info.filename for info in entries]
            if (len(entries) > MAX_FILES+1 or len(names) != len(set(names))
                    or 'manifest.json' not in names):
                raise ValueError('Pacote duplicado ou incompleto.')
            total = 0
            for info in entries:
                if info.filename != 'manifest.json' and not NAME.fullmatch(info.filename):
                    raise ValueError('Caminho não permitido no pacote.')
                mode = (info.external_attr >> 16) & 0o170000
                if mode not in (0, 0o100000) or info.flag_bits & 1:
                    raise ValueError('Links, diretórios e arquivos cifrados não são permitidos.')
                total += info.file_size
                if info.file_size > MAX_ENTRY or total > MAX_TOTAL:
                    raise ValueError('Conteúdo descompactado excede limite.')
            manifest = json.loads(archive.read('manifest.json'))
            if manifest.get('version') != 1 or manifest.get('environment') != environment():
                raise ValueError('Versão ou ambiente incompatível; recupere as dependências originais.')
            if set(manifest['files']) != set(names)-{'manifest.json'}:
                raise ValueError('Inventário não corresponde ao conteúdo.')
            if not {'source.mid','reference.mid','session.json'} <= set(manifest['files']):
                raise ValueError('Entradas obrigatórias ausentes.')
            for name, expected in manifest['files'].items():
                data = archive.read(name)
                if len(data) != expected['bytes'] or sha(data) != expected['sha256']:
                    raise ValueError('Integridade do arquivo inválida.')
                if name.endswith('.mid') and len(data) > MAX_BYTES:
                    raise ValueError('MIDI excede limite.')
                (staging/name).write_bytes(data)
        result = validate_snapshot(staging)
        # mkdir is exclusive, including against concurrent restore attempts.
        destination.mkdir()
        try:
            os.replace(staging, destination)  # publish the complete validated directory
        except BaseException:
            shutil.rmtree(destination)
            raise
        return {'directory': str(destination), 'generation': result['generation'],
                'checkpoint_sha256': result['checkpoint_sha256']}
    finally:
        if staging.exists():
            shutil.rmtree(staging)
