"""Experimental upper voice; not verified melody recognition."""
import math

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

