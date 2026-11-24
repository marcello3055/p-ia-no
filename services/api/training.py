"""Bounded single-process development jobs from operator-registered cached pairs."""
import fcntl
import hashlib
import json
from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field
from packages.music.midi import MAX_BYTES, read_midi
from packages.music.evaluate import EvaluationConfig
from packages.music.session import atomic_json, run_session
from services.api.sessions import ID


def sha(data):return hashlib.sha256(data).hexdigest()

def register_analysis(store,pair_id,source,reference,provenance):
    """Operator-only; no arbitrary filesystem paths accepted from web requests."""
    if not ID.fullmatch(pair_id):raise ValueError('Invalid pair')
    with store.connect() as db:
        pair=db.execute('SELECT * FROM pairs WHERE id=?',(pair_id,)).fetchone()
    if pair is None:raise ValueError('Pair missing')
    for data in (source,reference):
        if len(data)>MAX_BYTES or not read_midi(data).notes:raise ValueError('Invalid symbolic analysis')
    if not provenance:raise ValueError('Provenance required')
    folder=store.root/'analyzed-pairs'/pair_id;folder.mkdir(parents=True,exist_ok=False)
    (folder/'source.mid').write_bytes(source);(folder/'reference.mid').write_bytes(reference)
    manifest={'pair_id':pair_id,'source_sha256':sha(source),'reference_sha256':sha(reference),
      'base_audio_sha256':store.get_audio(pair['base_id'])['sha256'],
      'reference_audio_sha256':store.get_audio(pair['reference_id'])['sha256'],
      'alignment':'provisional','provenance':provenance}
    atomic_json(folder/'analysis.json',manifest)
    return manifest


def load_analysis(store,pair_id):
    if not ID.fullmatch(pair_id):raise ValueError('Invalid pair')
    folder=store.root/'analyzed-pairs'/pair_id
    if folder.is_symlink():raise ValueError('Invalid cache')
    paths=[folder/n for n in ('analysis.json','source.mid','reference.mid')]
    for p in paths:
        if p.is_symlink() or not p.is_file() or p.stat().st_size>MAX_BYTES:raise ValueError('Invalid cache')
    manifest=json.loads(paths[0].read_text());source=paths[1].read_bytes();reference=paths[2].read_bytes()
    if manifest['pair_id']!=pair_id or sha(source)!=manifest['source_sha256'] or sha(reference)!=manifest['reference_sha256']:raise ValueError('Changed cache')
    with store.connect() as db:pair=db.execute('SELECT * FROM pairs WHERE id=?',(pair_id,)).fetchone()
    if pair is None:raise ValueError('Missing pair')
    for role,key in [('base','base_id'),('reference','reference_id')]:
        audio=store.get_audio(pair[key]);path=store.files/audio['filename']
        if path.is_symlink() or not path.is_file() or sha(path.read_bytes())!=manifest[role+'_audio_sha256']:raise ValueError('Changed audio')
    return manifest,source,reference

class StartJob(BaseModel):
    pair_id:str=Field(min_length=1,max_length=80)
    generations:int=Field(default=3,ge=0,le=3,strict=True)
    acknowledge_provisional:bool=False


def training_router(store):
    router=APIRouter(prefix='/api/training');jobs=store.root/'training-jobs';jobs.mkdir(exist_ok=True)
    def lock():
        handle=(jobs/'.worker.lock').open('a')
        try:fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:handle.close();raise HTTPException(409,'Já existe uma sessão em execução.')
        return handle
    @router.get('/pairs')
    def ready():
        result=[]
        root=store.root/'analyzed-pairs'
        for folder in sorted(root.iterdir()) if root.exists() else []:
            try:
                manifest,_,_=load_analysis(store,folder.name)
                result.append({'pair_id':folder.name,'alignment':manifest['alignment']})
            except (ValueError,KeyError,OSError,HTTPException):continue
        return {'pairs':result}
    def work(handle,path,state,manifest,source,reference):
        try:
            state['state']='running';atomic_json(path,state)
            session=store.root/state['session_id']
            for generation in range(state['target_generation']+1):
                run_session(source,reference,session,generation,resume=generation>0,
                    evaluation_config=EvaluationConfig(time_unit='seconds',onset_tolerance=.2,duration_absolute_tolerance=.2),
                    ranking_profile='clean-melody-v1')
                if generation==0:
                    (session/'source.mid').write_bytes(source);(session/'reference.mid').write_bytes(reference)
                    atomic_json(session/'analysis-provenance.json',manifest)
                state['completed_generation']=generation;atomic_json(path,state)
            state['state']='completed'
        except Exception:
            state['state']='failed';state['error']='Processamento interrompido. Checkpoints completos foram preservados.'
        finally:
            try:atomic_json(path,state)
            finally:handle.close()
    @router.post('/jobs',status_code=202)
    def start(body:StartJob,background:BackgroundTasks):
        if not body.acknowledge_provisional:raise HTTPException(422,'Confirme o uso experimental do alinhamento provisório.')
        try:manifest,source,reference=load_analysis(store,body.pair_id)
        except (ValueError,KeyError,OSError,HTTPException):raise HTTPException(409,'Par sem análise válida. Prepare a análise antes de iniciar.')
        handle=lock();job_id=uuid4().hex;path=jobs/(job_id+'.json')
        state={'id':job_id,'pair_id':body.pair_id,'session_id':'train-'+job_id,'state':'queued',
               'completed_generation':-1,'target_generation':body.generations,'population_size':100,
               'experimental':True,'ranking_profile':'clean-melody-v1'}
        try:atomic_json(path,state)
        except BaseException:handle.close();raise
        background.add_task(work,handle,path,state.copy(),manifest,source,reference)
        return state
    @router.get('/jobs/{job_id}')
    def status(job_id:str):
        if not ID.fullmatch(job_id):raise HTTPException(404,'Tarefa não encontrada.')
        path=jobs/(job_id+'.json')
        if not path.is_file() or path.is_symlink():raise HTTPException(404,'Tarefa não encontrada.')
        state=json.loads(path.read_text())
        if state['state'] in ('queued','running'):
            try:handle=lock()
            except HTTPException:return state
            try:
                state['state']='interrupted';state['error']='Servidor reiniciado; checkpoints preservados. Não houve retomada automática.'
                atomic_json(path,state)
            finally:handle.close()
        return state
    return router
