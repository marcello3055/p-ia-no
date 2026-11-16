"""Agent-operated supervised evaluation; reads inputs once and writes a new checkpoint."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from packages.music.midi import MAX_BYTES,read_midi
from packages.music.population import initialize_population
from packages.music.ranking import rank_population
from packages.music.evaluate import EvaluationConfig
parser=argparse.ArgumentParser(description='Classificar candidatos por correspondência MIDI supervisionada.')
parser.add_argument('input',type=Path)
parser.add_argument('reference',type=Path)
parser.add_argument('--output-dir',type=Path,required=True)
parser.add_argument('--population',type=Path)
parser.add_argument('--weights',type=Path,help='JSON com os quatro pesos.')
parser.add_argument('--size',type=int,default=100)
parser.add_argument('--seed',type=int,default=0)
parser.add_argument('--time-unit',choices=['quarters','seconds'],default='quarters')
args=parser.parse_args(); created=False
try:
    if args.output_dir.exists(): raise ValueError('Destino já existe; escolha uma pasta nova.')
    def load(path):
        with path.open('rb') as f: data=f.read(MAX_BYTES+1)
        return read_midi(data),hashlib.sha256(data).hexdigest()
    source,source_hash=load(args.input); reference,reference_hash=load(args.reference)
    manifest=json.loads(args.population.read_text()) if args.population else initialize_population(args.size,args.seed)
    weights=json.loads(args.weights.read_text()) if args.weights else None
    report=rank_population(source,reference,manifest,weights,EvaluationConfig(time_unit=args.time_unit))
    report['sources']={'input_sha256':source_hash,'reference_sha256':reference_hash}
    args.output_dir.mkdir(parents=True,exist_ok=False); created=True
    for name,value in [('population.json',manifest),('ranking.json',report)]:
        (args.output_dir/name).write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:report[k] for k in ['evaluated','failed','unique_evaluations','best_score','baseline_score','best_minus_baseline']}))
except Exception as exc:
    if created: shutil.rmtree(args.output_dir)
    print(f'Falha: {exc}',file=sys.stderr); sys.exit(1)
