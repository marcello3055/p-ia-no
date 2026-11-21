"""Offline precision-oriented scoring with a conservative matched-note guard.
Not a melody recognizer; never changes saved rankings or authorizes training.
"""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from packages.music.session import digest
from packages.music.evaluate import evaluate, EvaluationConfig
from packages.music.midi import read_midi
from services.api.sessions import history


def assess(report, protected, beta=.5):
    if beta <= 0 or not __import__('math').isfinite(beta):
        raise ValueError('Beta must be positive and finite')
    matched={m['reference_index'] for m in report['matches']}
    precision=report['pitch_and_onset']['precision']; recall=report['pitch_and_onset']['recall']
    denominator=beta*beta*precision+recall
    value=(1+beta*beta)*precision*recall/denominator if denominator else 0.
    missing=sorted(set(protected)-matched)
    count=report['counts']['candidate'];hits=report['counts']['matched_pitch_onset']
    return {'f_beta':value,'beta':beta,'precision':precision,'recall':recall,
            'notes_without_match':count-hits,'notes':count,'missing_protected_reference_indices':missing,
            'eligible':not missing and bool(matched)}


def review(session, preferred_midi):
    session=Path(session)
    # Validate saved history once; no proposal generation or new transcription.
    history(session)
    checkpoints=[json.loads(p.read_text())['payload'] for p in sorted(session.glob('generation-*.json'))]
    first=checkpoints[0]['ranking'];settings=json.loads((session/'session.json').read_text())
    config=first['evaluation_config']
    baseline=next(r for r in first['results'] if r['id']==first['baseline_id'])
    protected={m['reference_index'] for m in first['evaluations'][baseline['evaluation_key']]['matches']}
    rows={}
    for p in checkpoints:
        ranking=p['ranking']
        if ranking['evaluation_config'] != config:raise ValueError('Mixed evaluator configurations')
        for row in ranking['results']:
            if row['status']!='evaluated':continue
            key=row['midi_sha256']
            if key not in rows:
                rows[key]={'id':row['id'],'midi_sha256':key,'generation':ranking['generation'],
                           'original_score':row['score'],**assess(ranking['evaluations'][row['evaluation_key']],protected)}
    import hashlib
    reference=(session/'reference.mid').read_bytes()
    if hashlib.sha256(reference).hexdigest()!=settings['reference_sha256']:raise ValueError('Reference changed')
    preferred_bytes=Path(preferred_midi).read_bytes()
    preferred=assess(evaluate(read_midi(reference),read_midi(preferred_bytes),EvaluationConfig(**config)),protected)
    preferred['midi_sha256']=hashlib.sha256(preferred_bytes).hexdigest()
    eligible=sorted((r for r in rows.values() if r['eligible']),key=lambda r:(-r['f_beta'],r['midi_sha256']))
    return {'status':'offline_experiment_not_integrated','training_allowed':False,'beta':.5,
            'configuration':config,'protected_matches':len(protected),'unique_cached_proposals':len(rows),
            'eligible_proposals':len(eligible),'baseline':assess(first['evaluations'][baseline['evaluation_key']],protected),
            'human_preferred':preferred,'top':eligible[:5],
            'checkpoint_sha256':json.loads(sorted(session.glob('generation-*.json'))[-1].read_text())['sha256'],
            'limitations':['Unmatched notes may be correct accompaniment or transcription/alignment errors.',
            'Guard preserves only baseline matched reference notes; it does NOT recognize or guarantee melody.',
            'F0.5 emphasizes precision; beta fixed before results, not fitted to one human preference.',
            'One pair and one preference are calibration evidence, not generalization validation.']}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--session',type=Path,required=True);p.add_argument('--preferred',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    result=review(a.session,a.preferred)
    with a.output.open('x') as f:json.dump(result,f,indent=2,ensure_ascii=False);f.write('\n')
    print(json.dumps(result,ensure_ascii=False))
