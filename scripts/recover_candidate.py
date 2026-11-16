"""Recover a verified proposal, without reranking or training."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from services.candidate_recovery import recover_candidate
p=argparse.ArgumentParser()
p.add_argument('--session',type=Path,required=True)
p.add_argument('--generation',type=int,required=True)
p.add_argument('--candidate',required=True)
p.add_argument('--source',type=Path)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args()
try:
    data=recover_candidate(a.session,a.generation,a.candidate,a.source)
    with a.output.open('xb') as handle: handle.write(data)
    print(f'Proposta verificada: {a.output} ({len(data)} bytes).')
except Exception as exc:
    print(f'Falha: {exc}',file=sys.stderr);sys.exit(1)
