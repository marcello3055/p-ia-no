"""Bounded symbolic evolution with atomic, verified generation checkpoints (Linux)."""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import tempfile
from .midi import read_midi
from .population import initialize_population, population_digest
from .ranking import rank_population
from .evolution import next_generation


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def atomic_json(path, value):
    fd, name = tempfile.mkstemp(prefix='.pending-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as handle:
            json.dump(value, handle, sort_keys=True, ensure_ascii=False, allow_nan=False)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def run_session(source_bytes, reference_bytes, directory, target_generation, *, resume=False, seed=0):
    """Target is absolute (0 = initial ranking); at most 100 new generations per call.

    The operator must supply aligned symbolic inputs. Does not consume saved audio
    diagnostic rankings or certify their transcription/alignment.
    """
    if type(target_generation) is not int or not 0 <= target_generation <= 10000:
        raise ValueError('Geração de destino inválida (0–10000).')
    initial = initialize_population(seed=seed)
    source, reference = read_midi(source_bytes), read_midi(reference_bytes)
    # Refuse resuming after implementation changes; no silent mixing of algorithms.
    code_hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in sorted(Path(__file__).parent.glob('*.py'))}
    settings = {'version': 1, 'seed': seed, 'population_size': 100,
                'source_sha256': hashlib.sha256(source_bytes).hexdigest(),
                'reference_sha256': hashlib.sha256(reference_bytes).hexdigest(),
                'code_sha256': code_hashes}
    directory = Path(directory)
    if resume:
        if not directory.is_dir():
            raise ValueError('Sessão inexistente.')
    else:
        if target_generation > 100:
            raise ValueError('Limite de 100 gerações novas por execução.')
        directory.mkdir(parents=True, exist_ok=False)
    with (directory / '.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ValueError('Sessão já está em execução.') from exc
        config_path = directory / 'session.json'
        if resume:
            if json.loads(config_path.read_text()) != settings:
                raise ValueError('Áudios simbólicos, semente ou implementação diferentes da sessão.')
        else:
            atomic_json(config_path, settings)
        files = sorted(directory.glob('generation-*.json'))
        previous = None
        history = []
        for generation, path in enumerate(files):
            if path.name != f'generation-{generation:05d}.json':
                raise ValueError('Checkpoint ausente ou fora de sequência.')
            envelope = json.loads(path.read_text())
            payload = envelope['payload']
            if envelope['sha256'] != digest(payload):
                raise ValueError('Checkpoint corrompido.')
            population, ranking = payload['population'], payload['ranking']
            if (payload['settings_sha256'] != digest(settings)
                    or payload['previous_sha256'] != (previous['sha256'] if previous else None)
                    or population['generation'] != generation
                    or ranking['generation'] != generation
                    or ranking['population_sha256'] != population_digest(population)
                    or ranking.get('training_allowed') is False
                    or ranking.get('status', '').startswith(('diagnostic', 'rejected'))):
                raise ValueError('Checkpoint incompatível ou diagnóstico.')
            previous = envelope
            history.append({'generation': generation, 'best_score': ranking['best_score']})
        current = len(files) - 1
        if target_generation < current:
            raise ValueError('Destino anterior ao checkpoint salvo.')
        if target_generation - max(current, 0) > 100:
            raise ValueError('Limite de 100 gerações novas por execução.')
        for generation in range(current + 1, target_generation + 1):
            population = (initial if previous is None else next_generation(
                previous['payload']['population'], previous['payload']['ranking'],
                seed=(seed + generation) % (2**32)))
            ranking = rank_population(source, reference, population)
            payload = {'settings_sha256': digest(settings),
                       'previous_sha256': previous['sha256'] if previous else None,
                       'population': population, 'ranking': ranking}
            envelope = {'sha256': digest(payload), 'payload': payload}
            atomic_json(directory / f'generation-{generation:05d}.json', envelope)
            previous = envelope
            history.append({'generation': generation, 'best_score': ranking['best_score']})
        return {'generation': target_generation, 'population_size': 100, 'history': history,
                'checkpoint_sha256': previous['sha256'],
                'limitations': ['Referência simbólica alinhada pelo operador; sem evidência de generalização ou melhoria auditiva.']}
