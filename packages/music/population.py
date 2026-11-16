"""Candidate manifests and deterministic proposal generation."""
from dataclasses import asdict, dataclass
import hashlib
from itertools import product
import json
import random
from .reduce import ReductionConfig, reduce_to_piano
from .midi import write_midi

SPACE = tuple(product(range(48,73,2), range(1,6), range(7,13)))

@dataclass(frozen=True)
class Candidate:
    id: str
    config: ReductionConfig


def candidate(config):
    config.validate()
    payload=json.dumps(asdict(config),sort_keys=True,separators=(',',':')).encode()
    return Candidate('candidate-'+hashlib.sha256(payload).hexdigest()[:16],config)


def initialize_population(size=100, seed=0):
    if type(size) is not int or not 1<=size<=len(SPACE):
        raise ValueError(f'População deve ter entre 1 e {len(SPACE)} candidatos.')
    if type(seed) is not int or not 0<=seed<2**32:
        raise ValueError('Semente deve ser inteiro entre 0 e 2^32−1.')
    baseline=(60,3,12)
    pool=[p for p in SPACE if p!=baseline]
    chosen=[baseline,*random.Random(seed).sample(pool,size-1)]
    return {'schema_version':1,'population_version':'0.1.0','generation':0,
            'seed':seed,'size':size,'baseline_id':candidate(ReductionConfig()).id,
            'candidates':[asdict(candidate(ReductionConfig(*p))) for p in chosen]}


def load_population(manifest):
    if manifest.get('schema_version')!=1 or manifest.get('population_version')!='0.1.0' or (type(manifest.get('generation')) is not int or manifest['generation']<0):
        raise ValueError('Versão/geração de população não suportada.')
    rows=manifest.get('candidates')
    if not isinstance(rows,list) or not 1<=len(rows)<=len(SPACE) or manifest.get('size')!=len(rows):
        raise ValueError('Quantidade de candidatos inválida.')
    result=[]
    for row in rows:
        try:
            config=ReductionConfig(**row['config'])
            if tuple(asdict(config).values()) not in SPACE: raise ValueError('Parâmetros fora do espaço inicial.')
            item=candidate(config)
            if row['id']!=item.id: raise ValueError('Identificador não corresponde aos parâmetros.')
        except (KeyError,TypeError) as exc:
            raise ValueError('Candidato inválido.') from exc
        result.append(item)
    if len({c.id for c in result})!=len(result): raise ValueError('Candidatos repetidos.')
    if manifest.get('baseline_id')!=result[0].id or result[0].config!=ReductionConfig():
        raise ValueError('Baseline inicial ausente.')
    return result


def generate_proposals(source, manifest):
    """Yield bounded results; same source analysis reused, no audio rendered."""
    for item in load_population(manifest):
        try:
            score,report=reduce_to_piano(source,item.config)
            midi=write_midi(score)
            # Distinct parameters do not imply distinct musical output.
            signature=sorted((n.track,n.pitch,n.start_tick,n.end_tick,n.velocity) for n in score.notes)
            yield {'id':item.id,'status':'generated','score':None,
                   'output_notes':len(score.notes),'discard_counts':report['discard_counts'],
                   'musical_sha256':hashlib.sha256(json.dumps(signature,separators=(',',':')).encode()).hexdigest(),
                   'midi_sha256':hashlib.sha256(midi).hexdigest()},midi
        except ValueError as exc:
            yield {'id':item.id,'status':'failed','score':None,'error':str(exc)},None


def population_digest(manifest):
    load_population(manifest)
    return hashlib.sha256(json.dumps(manifest,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()
