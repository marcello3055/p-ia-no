"""Create/replay initial candidate population from one symbolic input."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from packages.music.midi import MAX_BYTES, read_midi
from packages.music.population import initialize_population,load_population,generate_proposals
parser=argparse.ArgumentParser(description='Gerar população inicial experimental, sem evolução.')
parser.add_argument('input',type=Path)
parser.add_argument('--output-dir',type=Path,required=True)
parser.add_argument('--size',type=int,default=100)
parser.add_argument('--seed',type=int,default=0)
parser.add_argument('--population',type=Path,help='Reutilizar manifesto; size/seed não são aplicados.')
args=parser.parse_args()
created=False
try:
    manifest=json.loads(args.population.read_text()) if args.population else initialize_population(args.size,args.seed)
    load_population(manifest)
    with args.input.open('rb') as f: data=f.read(MAX_BYTES+1)
    source=read_midi(data)
    args.output_dir.mkdir(parents=True,exist_ok=False); created=True
    (args.output_dir/'population.json').write_text(json.dumps(manifest,indent=2)+'\n')
    results=[]
    for result,midi in generate_proposals(source,manifest):
        if midi is not None: (args.output_dir/(result['id']+'.mid')).write_bytes(midi)
        results.append(result)
    generated=[r for r in results if r['status']=='generated']
    report={'schema_version':1,'generation':0,'source_sha256':hashlib.sha256(data).hexdigest(),
            'source_notes':len(source.notes),'population_size':len(results),'generated':len(generated),
            'failed':len(results)-len(generated),'distinct_musical_outputs':len({r['musical_sha256'] for r in generated}),
            'evaluated':0,'best_candidate':None,'results':results,
            'limitations':['Sem avaliação, seleção, reprodução, melhoria comprovada ou aprendizado.','Parâmetros distintos podem gerar a mesma música.']}
    (args.output_dir/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('results','limitations')},ensure_ascii=False))
except Exception as exc:
    if created: shutil.rmtree(args.output_dir)
    print(f'Falha: {exc}',file=sys.stderr); sys.exit(1)
