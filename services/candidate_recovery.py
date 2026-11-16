"""Rebuild exactly one evaluated candidate and verify its saved MIDI digest."""
import hashlib
from pathlib import Path
from fastapi import HTTPException
from services.api.sessions import history
from packages.music.midi import MAX_BYTES, read_midi, write_midi
from packages.music.reduce import ReductionConfig, reduce_to_piano


def current_code_hashes():
    music=Path(__file__).resolve().parents[1]/'packages/music'
    return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(music.glob('*.py'))}


def recover_candidate(folder, generation, candidate_id, source_path=None):
    folder=Path(folder)
    snapshot=history(folder,generation,include_checkpoint=True)
    settings=snapshot['settings']; checkpoint=snapshot['checkpoint']
    candidates={c['id']:c for c in checkpoint['population']['candidates']}
    results={r['id']:r for r in checkpoint['ranking']['results']}
    if candidate_id not in candidates or candidate_id not in results:
        raise HTTPException(404,'Candidato não encontrado nesta geração.')
    result=results[candidate_id]
    if result['status']!='evaluated':
        raise ValueError('Candidato não possui proposta avaliada.')
    if current_code_hashes()!=settings['code_sha256']:
        raise ValueError('Recupere a versão original do código musical.')
    path=Path(source_path) if source_path is not None else folder/'source.mid'
    if path.is_symlink() or not path.is_file():
        raise ValueError('Fonte MIDI original indisponível.')
    with path.open('rb') as handle: source=handle.read(MAX_BYTES+1)
    if len(source)>MAX_BYTES or hashlib.sha256(source).hexdigest()!=settings['source_sha256']:
        raise ValueError('Fonte não corresponde à sessão.')
    proposal,_=reduce_to_piano(read_midi(source),ReductionConfig(**candidates[candidate_id]['config']))
    midi=write_midi(proposal)
    if hashlib.sha256(midi).hexdigest()!=result['midi_sha256']:
        raise ValueError('Proposta reproduzida difere daquela avaliada.')
    return midi
