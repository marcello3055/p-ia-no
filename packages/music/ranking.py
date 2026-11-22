"""Supervised symbolic ranking for a candidate population; not an artistic judgement."""
from dataclasses import asdict
import math
from .guide import upper_voice
from .evaluate import EvaluationConfig, evaluate
from .midi import read_midi
from .population import load_population, generate_proposals, population_digest

DEFAULT_WEIGHTS={'pitch_onset':.5,'duration':.25,'pitch_classes':.15,'attacks':.1}

def normalized_weights(weights=None):
    weights=dict(DEFAULT_WEIGHTS if weights is None else weights)
    if set(weights)!=set(DEFAULT_WEIGHTS):
        raise ValueError('Informe exatamente os quatro pesos documentados.')
    if any(type(v) not in (int,float) or not math.isfinite(v) or v<0 for v in weights.values()):
        raise ValueError('Pesos devem ser números finitos e não negativos.')
    total=sum(weights.values())
    if not math.isfinite(total) or total<=0:
        raise ValueError('A soma dos pesos deve ser positiva e finita.')
    return {k:v/total for k,v in weights.items()}


def criteria(report):
    return {'pitch_onset':report['pitch_and_onset']['f1'],
            'duration':report['pitch_onset_and_duration']['f1'],
            'pitch_classes':report['pitch_class_diagnostics']['temporal_pitch_class_jaccard'],
            'attacks':report['rhythm_diagnostics']['f1']}


def rank_population(source,reference,manifest,weights=None,config=None, profile="standard"):
    if profile not in ("standard", "clean-melody-v1"):
        raise ValueError("Perfil de avaliação desconhecido.")
    load_population(manifest)
    weights=normalized_weights(weights); config=config or EvaluationConfig()
    # Reject invalid/empty references before generating a population.
    self_report=evaluate(reference,reference,config)
    if any(value is None and weights[key]>0 for key,value in criteria(self_report).items()):
        raise ValueError('Referência não permite calcular um critério com peso positivo.')
    guide=set(upper_voice(reference)['reference_indices']) if profile=='clean-melody-v1' else set()
    if profile=='clean-melody-v1':
        weights={k:v*.6 for k,v in weights.items()}
        weights.update(cleanliness=.3, melody_guide=.1)
    rows=[]; cache={}; evaluations={}
    for generated,midi in generate_proposals(source,manifest):
        row={**generated,'rank':None,'criteria':None,'contributions':None}
        if midi is not None:
            key=generated['midi_sha256']
            if key not in cache:
                report=evaluate(reference,read_midi(midi),config)
                values=criteria(report)
                if profile=='clean-melody-v1':
                    precision=report['pitch_and_onset']['precision']; recall=report['pitch_and_onset']['recall']
                    denominator=.25*precision+recall
                    values['cleanliness']=1.25*precision*recall/denominator if denominator else 0.
                    matched={m['reference_index'] for m in report['matches']}
                    values['melody_guide']=len(guide & matched)/len(guide) if guide else None
                if any(v is None and weights[k]>0 and k!="melody_guide" for k,v in values.items()):
                    raise ValueError('Critério ativo indefinido; classificação interrompida.')
                contributions={k:(weights[k]*v if v is not None else 0.0) for k,v in values.items()}
                cache[key]=(values,contributions,sum(contributions.values()))
                evaluations[key]=report
            values,contributions,score=cache[key]
            row.update(status='evaluated',criteria=dict(values),contributions=dict(contributions),score=score,evaluation_key=key)
        rows.append(row)
    eligible=sorted((r for r in rows if r['status']=='evaluated'),key=lambda r:(-r['score'],r['id']))
    rank=0; last_score=None
    for position,row in enumerate(eligible,1):
        if row['score']!=last_score: rank=position
        row['rank']=rank; last_score=row['score']
    best=eligible[0]['score'] if eligible else None
    best_ids=[r['id'] for r in eligible if r['score']==best]
    baseline=next(r for r in rows if r['id']==manifest['baseline_id'])
    return {'schema_version':1,'ranker_version':'0.1.0','evaluator_version':'0.2.0','generation':manifest['generation'],'population_sha256':population_digest(manifest),
            'ranking_profile':profile,'guide_note_count':len(guide),'weights':weights,'evaluation_config':asdict(config),'population_size':len(rows),
            'evaluated':len(eligible),'failed':len(rows)-len(eligible),'unique_evaluations':len(cache),
            'ranking':[r['id'] for r in eligible],'best_score':best,'best_candidate_ids':best_ids,
            'baseline_id':baseline['id'],'baseline_score':baseline['score'],
            'best_minus_baseline':best-baseline['score'] if best is not None and baseline['score'] is not None else None,
            'results':rows,'evaluations':evaluations,
            'limitations':['Correspondência com uma referência simbólica alinhada, não qualidade artística.',
                           'Sem reconhecimento de melodia principal, harmonia funcional, expressividade ou avaliação completa de tocabilidade.',
                           'Sem currículo, mínimos por critério ou generalização demonstrada.',
                           'Empates recebem mesma posição; ordenação por ID serve apenas para reprodução.',
                           'Pesos iniciais convencionais, não calibrados por preferência humana.']}
