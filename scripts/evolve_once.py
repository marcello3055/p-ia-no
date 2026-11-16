"""One supervised symbolic cycle; no arbitrary saved diagnostic rankings accepted."""
import argparse,json,hashlib,shutil,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from packages.music.midi import MAX_BYTES,read_midi
from packages.music.population import initialize_population
from packages.music.ranking import rank_population
from packages.music.evolution import next_generation
p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('reference',type=Path);p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--seed',type=int,default=0);a=p.parse_args();created=False
try:
    if a.output_dir.exists():raise ValueError('Destino existente.')
    def load(path):
        with path.open('rb') as f:data=f.read(MAX_BYTES+1)
        return read_midi(data),hashlib.sha256(data).hexdigest()
    source,source_hash=load(a.source);reference,ref_hash=load(a.reference)
    initial=initialize_population(seed=a.seed); before=rank_population(source,reference,initial)
    following=next_generation(initial,before,seed=a.seed)
    after=rank_population(source,reference,following,weights=before['weights'])
    summary={'source_sha256':source_hash,'reference_sha256':ref_hash,'before':before['best_score'],'after':after['best_score'],
             'difference':after['best_score']-before['best_score'],'population_size':following['size'],
             'generation':following['generation'],'origins':{o:sum(r['origin']==o for r in following['evolution']['lineage']) for o in ['baseline','elite','immigrant','offspring','diversity_fill']},
             'limitations':['Uma geração, referência simbólica fornecida; sem demonstração de generalização ou melhoria auditiva.']}
    a.output_dir.mkdir(parents=True);created=True
    for name,value in [('population-0',initial),('ranking-0',before),('population-1',following),('ranking-1',after),('summary',summary)]:
        (a.output_dir/(name+'.json')).write_text(json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
    print(json.dumps(summary,ensure_ascii=False))
except Exception as exc:
    if created:shutil.rmtree(a.output_dir)
    print(f'Falha: {exc}',file=sys.stderr);sys.exit(1)
