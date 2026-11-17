"""Controlled tests in the existing isolated audio environment."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from experiments.audit_alignment import bounded_path,map_diagnostics

cost=np.abs(np.arange(20)[:,None]-np.arange(20)[None,:]).astype(float)
m=bounded_path(cost,10,10,20)['mapping_query_to_target_seconds']
assert np.allclose(m,np.column_stack((np.linspace(0,10,20),20+np.linspace(0,10,20))))
# Different duration and deliberately attractive flat rows cannot collapse time.
cost=np.ones((40,30));cost[10:25,15]=0
m=bounded_path(cost,25.5,18,20)['mapping_query_to_target_seconds']
d=map_diagnostics(m)
assert m[0]==[0.,20.] and m[-1]==[25.5,38.]
assert d['flat_runs']==0 and d['min_local_reference_per_source']>0
assert d['max_local_reference_per_source']<=2*18/29/(25.5/39)+1e-10
assert map_diagnostics([[0,0],[1,0],[2,0],[3,1]])['longest_flat_source_seconds']==2
for bad in ([[0,1],[1,0]],[[0,0],[0,1]]):
 try:map_diagnostics(bad)
 except ValueError:pass
 else:raise AssertionError('invalid map accepted')
print('PASS: identity, endpoints, positive bounded slope, flat-run audit and invalid maps.')
