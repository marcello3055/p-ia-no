"""One bounded genetic generation; immutable inputs and explicit ancestry."""
from dataclasses import asdict
import math
import random
from .population import SPACE, candidate, load_population, population_digest
from .reduce import ReductionConfig

GENES=(tuple(range(48,73,2)),tuple(range(1,6)),tuple(range(7,13)))

def next_generation(manifest,ranking,seed=0,elite_count=10,immigrant_count=10,mutation_rate=.3):
    items=load_population(manifest); n=len(items)
    if ranking.get('training_allowed') is False or ranking.get('status','').startswith(('diagnostic','rejected')):
        raise ValueError('Ranking diagnóstico/rejeitado não pode orientar reprodução.')
    if ranking.get('population_sha256')!=population_digest(manifest) or ranking.get('generation')!=manifest['generation']:
        raise ValueError('Ranking não corresponde a esta população/geração.')
    if type(seed) is not int or not 0<=seed<2**32: raise ValueError('Semente inválida.')
    if type(elite_count) is not int or not 1<=elite_count<=n: raise ValueError('Quantidade de elites inválida.')
    if type(immigrant_count) is not int or not 0<=immigrant_count<n: raise ValueError('Quantidade de imigrantes inválida.')
    if type(mutation_rate) not in (int,float) or not math.isfinite(mutation_rate) or not 0<=mutation_rate<=1: raise ValueError('Taxa de mutação inválida.')
    rows=ranking.get('results',[]); by_id={i.id:i for i in items}
    if len(rows)!=n or {r['id'] for r in rows}!=set(by_id): raise ValueError('Resultados incompletos ou repetidos.')
    successful=[]
    for r in rows:
        if r['status']=='evaluated':
            if type(r['score']) not in (int,float) or not math.isfinite(r['score']) or not 0<=r['score']<=1: raise ValueError('Score inválido.')
            successful.append(r)
        elif r['status']!='failed' or r['score'] is not None: raise ValueError('Estado de avaliação inválido.')
    if not successful: raise ValueError('Nenhum candidato avaliado para selecionar.')
    ordered=sorted(successful,key=lambda r:(-r['score'],r['id']))
    rng=random.Random(seed)
    # Prefer distinct musical outputs among elites, always preserve the top score.
    diverse=[]; duplicates=[]; signatures=set()
    for r in ordered:
        sig=r['musical_sha256']
        (duplicates if sig in signatures else diverse).append(r)
        signatures.add(sig)
    elites=(diverse+duplicates)[:elite_count]
    chosen=[]; seen=set(); lineage=[]
    def add(item,origin,parents=(),mutated_gene=None):
        if item.id in seen: return False
        chosen.append(asdict(item)); seen.add(item.id)
        lineage.append({'id':item.id,'origin':origin,'parents':list(parents),'mutated_gene':mutated_gene})
        return True
    add(items[0],'baseline')
    for row in elites: add(by_id[row['id']],'elite',(row['id'],))
    if len(chosen)+immigrant_count>n: raise ValueError('Baseline, elites e imigrantes excedem população.')
    # Reserve random immigrants before breeding; no duplicate configuration in generation.
    available=[candidate(ReductionConfig(*p)) for p in SPACE]
    available=[i for i in available if i.id not in seen]
    for item in rng.sample(available,immigrant_count): add(item,'immigrant')
    pool=ordered[:max(2,min(len(ordered),max(elite_count*2,2)))]
    attempts=0
    while len(chosen)<n and attempts<n*20:
        attempts+=1
        a,b=rng.choices(pool,k=2)
        av=tuple(asdict(by_id[a['id']].config).values()); bv=tuple(asdict(by_id[b['id']].config).values())
        genes=[rng.choice((x,y)) for x,y in zip(av,bv)]
        mutation=None
        if rng.random()<mutation_rate:
            mutation=rng.randrange(3)
            genes[mutation]=rng.choice([v for v in GENES[mutation] if v!=genes[mutation]])
        add(candidate(ReductionConfig(*genes)),'offspring',(a['id'],b['id']),mutation)
    # Finite search space: bounded fallback guarantees termination even near saturation.
    remaining=[i for i in available if i.id not in seen]
    for item in rng.sample(remaining,n-len(chosen)): add(item,'diversity_fill')
    new={**manifest,'generation':manifest['generation']+1,'seed':seed,'candidates':chosen,
         'evolution':{'version':'0.1.0','parent_population_sha256':population_digest(manifest),
                      'elite_count_requested':elite_count,'immigrant_count':immigrant_count,
                      'mutation_rate':mutation_rate,'attempts':attempts,'lineage':lineage}}
    load_population(new)
    return new
