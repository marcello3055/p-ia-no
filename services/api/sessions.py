"""Read-only, bounded session history; never evaluates or resumes candidates."""
import fcntl
import json
from pathlib import Path
import re
from fastapi import APIRouter, HTTPException
from packages.music.session import digest
from packages.music.population import population_digest

ID = re.compile(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}\Z')
MAX_TOTAL = 64 * 1024 * 1024
MAX_GENERATIONS = 201


def history(folder):
    total = 0
    def read(path):
        nonlocal total
        if path.is_symlink() or not path.is_file():
            raise ValueError('Arquivo inválido.')
        with path.open('rb') as stream:
            raw = stream.read(min(16*1024*1024, MAX_TOTAL-total)+1)
        total += len(raw)
        if len(raw)>16*1024*1024 or total>MAX_TOTAL:
            raise ValueError('Histórico excede limite de consulta.')
        return json.loads(raw)
    settings = read(folder/'session.json')
    paths = sorted(folder.glob('generation-*.json'))
    if len(paths)>MAX_GENERATIONS:
        raise ValueError('Consulta limitada a 201 checkpoints por sessão.')
    previous = None; rows = []
    for generation,path in enumerate(paths):
        if path.name != f'generation-{generation:05d}.json':
            raise ValueError('Checkpoint ausente.')
        envelope = read(path); payload=envelope['payload']
        population=payload['population']; ranking=payload['ranking']
        if (envelope['sha256']!=digest(payload) or payload['previous_sha256']!=previous
                or payload['settings_sha256']!=digest(settings)
                or population['generation']!=generation or ranking['generation']!=generation
                or ranking['population_sha256']!=population_digest(population)):
            raise ValueError('Integridade inválida.')
        previous=envelope['sha256']
        rows.append({'generation':generation,'best_score':ranking['best_score'],
                     'baseline_score':ranking['baseline_score'],'evaluated':ranking['evaluated'],
                     'failed':ranking['failed'],'unique_evaluations':ranking['unique_evaluations'],
                     'best_candidate_ids':ranking['best_candidate_ids'],
                     'diagnostic':ranking.get('training_allowed') is False or ranking.get('status','').startswith(('diagnostic','rejected'))})
    state='idle'
    lock_path=folder/'.lock'
    if lock_path.is_symlink(): raise ValueError('Lock inválido.')
    if lock_path.is_file():
        with lock_path.open('rb') as lock:
            try: fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError: state='busy'
    return {'id':folder.name,'state':state,'population_size':settings['population_size'],
            'generation':rows[-1]['generation'] if rows else None,'history':rows,
            'limitations':['Pontuação de correspondência simbólica, não nota de qualidade musical.',
                           'Sem processo ativo não significa treinamento concluído.',
                           'Consulta não verifica a correspondência musical dos trechos.']}


def sessions_router(root):
    root=Path(root)
    router=APIRouter(prefix='/api/sessions')
    @router.get('')
    def sessions():
        items=[]
        for folder in sorted(root.iterdir()):
            if folder.is_symlink() or not folder.is_dir() or not ID.fullmatch(folder.name): continue
            if not (folder/'session.json').is_file(): continue
            if len(items)>=50: raise HTTPException(409,'Limite de 50 sessões para consulta.')
            items.append({'id':folder.name})
        return {'sessions':items}
    @router.get('/{session_id}')
    def detail(session_id: str):
        if not ID.fullmatch(session_id): raise HTTPException(404,'Sessão não encontrada.')
        folder=root/session_id
        if folder.is_symlink() or not folder.is_dir() or not (folder/'session.json').is_file():
            raise HTTPException(404,'Sessão não encontrada.')
        try: return history(folder)
        except (ValueError,KeyError,TypeError,AttributeError,OSError):
            raise HTTPException(409,'Histórico indisponível: confira integridade, formato e limite de 201 checkpoints.')
    return router
