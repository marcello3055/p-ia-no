"""Small synthetic check, run with .venv-audio; does not prove real alignment accuracy."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from experiments.anchored_alignment import anchored_path
from packages.music.time_map import warp_reference
sr=11025
x=np.concatenate([np.sin(2*np.pi*f*np.arange(sr)/sr).astype(np.float32) for f in [220,330,440,550]])
r=anchored_path(x,x,4,4,20)
m=r['mapping_query_to_target_seconds']
assert m[0]==[0,20] and m[-1]==[4,24]
assert r['max_normalized_deviation']<=.15
assert r['mean_path_cost']<1e-6
assert all(b[0]>a[0] and b[1]>=a[1] for a,b in zip(m,m[1:]))
score,_=warp_reference([{'start_seconds':1,'end_seconds':2,'pitch':60}],m,20)
assert abs(score.notes[0].start_tick-960)<100
print('PASS: anchored identity, exact endpoints, monotonicity, corridor and note warp')
