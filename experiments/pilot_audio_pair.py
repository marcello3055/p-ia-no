"""Small supervised pilot using cached audio transcriptions and a provisional map."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from packages.music.midi import Note, Score, write_midi
from packages.music.time_map import warp_reference
from packages.music.session import run_session, atomic_json
from packages.music.render import render_piano
from services.candidate_recovery import recover_candidate
from services.session_backup import export_session


def main():
    p=argparse.ArgumentParser();p.add_argument('--source-report',type=Path,required=True)
    p.add_argument('--pair',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--allow-provisional-pilot',action='store_true');a=p.parse_args()
    if not a.allow_provisional_pilot: raise ValueError('Explicit provisional pilot opt-in required')
    if a.output.exists(): raise ValueError('Output exists; preserve previous pilot')
    source_path=a.source_report; ref_path=a.pair/'comparison/reference-estimates.json';alignment_path=a.pair/'alignment.json'
    report=json.loads(source_path.read_text());alignment=json.loads(alignment_path.read_text())
    for role in ('source','reference'):
        meta=json.loads((a.pair/role/'clip.json').read_text())
        actual=hashlib.sha256((a.pair/role/'clip.wav').read_bytes()).hexdigest()
        if meta['clip_sha256']!=actual: raise ValueError('Clip hash mismatch')
        if role=='source' and report['clip']['clip_sha256']!=actual: raise ValueError('Wrong source report')
    if alignment['sources']['query_sha256']!=report['clip']['clip_sha256']:raise ValueError('Wrong alignment source')
    regions=alignment['human_regions']
    if [regions[k] for k in ('source_start','source_end','reference_start','reference_end')] != [24.5,50,20,38]:
        raise ValueError('This bounded pilot expects the approved Tifa excerpt regions')
    if alignment['sources']['target_sha256'] != json.loads((a.pair/'reference/clip.json').read_text())['cache_key']['source_sha256']:
        raise ValueError('Wrong reference recording')
    ref,warp=warp_reference(json.loads(ref_path.read_text()),alignment['mapping_query_to_target_seconds'],20.)
    notes=[Note(0,0,e['pitch'],max(1,min(127,round(e['activation']*127))),0,round(e['start_seconds']*960),round(e['end_seconds']*960),1,0) for e in report['estimates']]
    source=Score(480,1,[round(report['clip']['actual_seconds']*960)],notes,[],[])
    source_bytes,reference_bytes=write_midi(source),write_midi(ref)
    a.output.mkdir(parents=True)
    provenance={'status':'experimental_provisional_alignment','approved_arranger':False,'musical_alignment_validated':False,
                'scope':'One Tifa excerpt; generation 0 plus 3 evolutionary generations; 100 candidates each; seed 0.',
                'alignment_choice':'Previous human-region DTW, provisional. Bounded alternative did not improve cached-note diagnostics.',
                'human_regions':alignment['human_regions'],'warping':warp,
                'inputs_sha256':{str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in (source_path,ref_path,alignment_path)},
                'limitations':['No fresh transcription; uncertain notes on both sides.',
                'Reference estimates provenance relies on existing experiment directory; no original per-file clip manifest.',
                'Original diagnostic rankings remain unchanged and are NOT consumed by evolution.',
                'Default session evaluator: onset 0.1 quarter = 50 ms at these MIDI tempos, stricter than earlier 200 ms diagnostic.',
                'No melody recognition, expressive interpretation, generalization or auditory improvement demonstrated.']}
    atomic_json(a.output/'pilot.json',provenance)
    started=time.perf_counter();session=a.output/'session'
    result=run_session(source_bytes,reference_bytes,session,3,seed=0)
    (session/'source.mid').write_bytes(source_bytes);(session/'reference.mid').write_bytes(reference_bytes)
    first=json.loads((session/'generation-00000.json').read_text())['payload']['ranking']
    last=json.loads((session/'generation-00003.json').read_text())['payload']['ranking']
    rows=[]
    for label,g,cid,ranking in [('baseline',0,first['baseline_id'],first),('best',3,last['best_candidate_ids'][0],last)]:
        midi=recover_candidate(session,g,cid);path=a.output/f'{label}.mid';path.write_bytes(midi)
        rendered=render_piano(path,a.output/label)
        row=next(r for r in ranking['results'] if r['id']==cid)
        rows.append({'label':label,'generation':g,'candidate':cid,'score':row['score'],'criteria':row['criteria'],
                     'midi_sha256':hashlib.sha256(midi).hexdigest(),'render':rendered})
    verified=run_session(source_bytes,reference_bytes,session,3,resume=True,seed=0)
    assert verified['checkpoint_sha256']==result['checkpoint_sha256']
    export_session(session,session/'source.mid',session/'reference.mid',a.output/'session-backup.zip')
    summary={**provenance,'run':result,'evaluated_candidate_slots':sum(json.loads(f.read_text())['payload']['ranking']['evaluated'] for f in session.glob('generation-*.json')),
             'baseline_score':first['baseline_score'],'best_final_score':last['best_score'],'renders':rows,
             'elapsed_seconds':time.perf_counter()-started,'resume_verification':'passed',
             'same_midi':rows[0]['midi_sha256']==rows[1]['midi_sha256']}
    atomic_json(a.output/'result.json',summary)
    print(json.dumps(summary,ensure_ascii=False))

if __name__=='__main__':main()
