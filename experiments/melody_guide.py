"""Experimental upper-voice guide, not general melody recognition."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from experiments.cleanliness_review import assess
from packages.music.evaluate import evaluate, EvaluationConfig
from packages.music.midi import read_midi
from services.api.sessions import history


def upper_voice(score, minimum_seconds=.12, minimum_exposure=.5):
    """Select sustained notes exposed as highest eligible pitch for >= half duration.
    Short notes cannot mask longer notes; ignored channel 9 matches evaluator defaults.
    No candidate preference is used to derive the guide.
    """
    if not math.isfinite(minimum_seconds) or minimum_seconds<=0 or not 0<minimum_exposure<=1:
        raise ValueError('Invalid guide thresholds')
    notes=score.to_dict()['notes']
    eligible=[(i,n) for i,n in enumerate(notes) if n['channel']!=9 and n['duration_seconds']>=minimum_seconds]
    boundaries=sorted({t for _,n in eligible for t in (n['start_seconds'],n['start_seconds']+n['duration_seconds'])})
    exposed={i:0. for i,_ in eligible}
    for a,b in zip(boundaries,boundaries[1:]):
        mid=(a+b)/2
        active=[(i,n) for i,n in eligible if n['start_seconds']<=mid<n['start_seconds']+n['duration_seconds']]
        if active:
            highest=max(n['pitch'] for _,n in active)
            for i,n in active:
                if n['pitch']==highest:exposed[i]+=b-a
    fractions={i:min(1.,exposed[i]/n['duration_seconds']) for i,n in eligible}
    return {'reference_indices':sorted(i for i,f in fractions.items() if f+1e-9>=minimum_exposure),
            'minimum_seconds':minimum_seconds,'minimum_exposure':minimum_exposure,
            'status':'heuristic_unverified','method':'duration_filtered_upper_voice'}


def guarded(report, guide_indices, baseline_report):
    guide=set(guide_indices)
    protected=guide & {m['reference_index'] for m in baseline_report['matches']}
    result=assess(report,protected)
    matches=guide & {m['reference_index'] for m in report['matches']}
    result.update(guide_notes=len(guide),protected_guide_notes=len(protected),matched_guide_notes=len(matches),
                  guide_coverage=len(matches)/len(guide) if guide else None)
    # Do not silently accept every candidate if the baseline covers no guide note.
    result['eligible']=result['eligible'] and bool(protected)
    return result


def review(session,preferred):
    history(session)
    settings=json.loads((session/'session.json').read_text())
    reference_bytes=(session/'reference.mid').read_bytes()
    if hashlib.sha256(reference_bytes).hexdigest()!=settings['reference_sha256']:raise ValueError('Reference changed')
    reference=read_midi(reference_bytes);guide=upper_voice(reference)
    checkpoints=[json.loads(p.read_text()) for p in sorted(session.glob('generation-*.json'))]
    first=checkpoints[0]['payload']['ranking'];config=first['evaluation_config']
    baseline=next(r for r in first['results'] if r['id']==first['baseline_id'])
    baseline_report=first['evaluations'][baseline['evaluation_key']]
    rows={}
    for checkpoint in checkpoints:
        ranking=checkpoint['payload']['ranking']
        if ranking['evaluation_config']!=config:raise ValueError('Mixed configurations')
        for row in ranking['results']:
            if row['status']=='evaluated' and row['midi_sha256'] not in rows:
                rows[row['midi_sha256']]={'id':row['id'],'midi_sha256':row['midi_sha256'],'generation':ranking['generation'],
                  **guarded(ranking['evaluations'][row['evaluation_key']],guide['reference_indices'],baseline_report)}
    preferred_bytes=preferred.read_bytes()
    preferred_report=evaluate(reference,read_midi(preferred_bytes),EvaluationConfig(**config))
    chosen=guarded(preferred_report,guide['reference_indices'],baseline_report)
    chosen['midi_sha256']=hashlib.sha256(preferred_bytes).hexdigest()
    eligible=sorted((r for r in rows.values() if r['eligible']),key=lambda r:(-r['f_beta'],r['midi_sha256']))
    return {'status':'experimental_guide_not_integrated','training_allowed':False,'guide':guide,
      'reference_sha256':settings['reference_sha256'],'checkpoint_sha256':checkpoints[-1]['sha256'],
      'unique_cached_proposals':len(rows),'eligible_proposals':len(eligible),
      'baseline':guarded(baseline_report,guide['reference_indices'],baseline_report),'human_preferred':chosen,
      'top':eligible[:5],'limitations':['Upper voice is a hypothesis, not verified melody; fails for inner/bass melodies and high accompaniment.',
      'Duration filtering can exclude short melodic notes; selected reference is itself transcribed and provisionally warped.',
      'Guard protects only guide notes already matched by baseline; full guide coverage is reported separately.',
      'No weights or thresholds fitted to the human preference; no new training or audio rendered.']}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--session',type=Path,required=True);p.add_argument('--preferred',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    result=review(a.session,a.preferred)
    with a.output.open('x') as f:json.dump(result,f,indent=2,ensure_ascii=False);f.write('\n')
    print(json.dumps(result,ensure_ascii=False))
