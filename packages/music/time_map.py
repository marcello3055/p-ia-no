"""Map reference note times to source excerpt time using a proposed DTW path."""
from bisect import bisect_right
import math
from .midi import Note,Score

def warp_reference(events, mapping, clip_start):
    if not math.isfinite(clip_start) or clip_start<0 or len(mapping)<2:
        raise ValueError('Mapa temporal inválido.')
    points=[]
    for query,target in mapping:
        if not all(math.isfinite(v) and v>=0 for v in (query,target)):
            raise ValueError('Mapa temporal não finito.')
        if points and (query<=points[-1][0] or target<points[-1][1]):
            raise ValueError('Mapa deve ser monotônico.')
        points.append((query,target))
    grouped={}
    for q,t in points: grouped.setdefault(t,[]).append(q)
    xs=sorted(grouped); ys=[sum(grouped[t])/len(grouped[t]) for t in xs]
    if len(xs)<2: raise ValueError('Mapa sem extensão temporal.')
    def interp(t):
        i=min(len(xs)-2,max(0,bisect_right(xs,t)-1))
        return ys[i]+(t-xs[i])*(ys[i+1]-ys[i])/(xs[i+1]-xs[i])
    notes=[]; excluded=collapsed=clipped=0
    for e in events:
        start=float(e['start_seconds'])+clip_start; end=float(e['end_seconds'])+clip_start
        if end<=xs[0] or start>=xs[-1]: excluded+=1; continue
        a=max(start,xs[0]); b=min(end,xs[-1]); clipped+=int(a!=start or b!=end)
        s=round(interp(a)*960); f=round(interp(b)*960)
        if f<=s: collapsed+=1; continue
        notes.append(Note(0,0,int(e['pitch']),80,0,s,f,1,0))
    return Score(480,1,[round(ys[-1]*960)],notes,[],['Referência transcrita e alinhamento DTW não verificados.']),{'excluded_outside_mapping':excluded,'collapsed_after_warp':collapsed,'clipped_at_boundaries':clipped,'mapped_notes':len(notes)}
