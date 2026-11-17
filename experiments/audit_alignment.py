"""Audit temporal distortions and propose bounded DTW; never approves training."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))


def map_diagnostics(mapping):
    import math
    if len(mapping)<2: raise ValueError('Mapa curto.')
    flat=[]; start=None; ratios=[]; jumps=[]
    for a,b in zip(mapping,mapping[1:]):
        dq=b[0]-a[0]; dt=b[1]-a[1]
        if not all(math.isfinite(v) for v in (*a,*b)) or dq<=0 or dt<0:
            raise ValueError('Mapa não monotônico/finito.')
        ratios.append(dt/dq);jumps.append(dt)
        if dt==0:
            if start is None:start=a[0]
        elif start is not None:
            flat.append(a[0]-start);start=None
    if start is not None:flat.append(mapping[-1][0]-start)
    return {'points':len(mapping),'flat_runs':len(flat),'longest_flat_source_seconds':max(flat,default=0),
            'largest_reference_step_seconds':max(jumps),'min_local_reference_per_source':min(ratios),
            'max_local_reference_per_source':max(ratios)}


def bounded_path(cost,query_seconds,target_seconds,target_start,band=.15):
    import numpy as np
    import librosa
    if cost.ndim!=2 or min(cost.shape)<2 or min(query_seconds,target_seconds)<=0 or not 0<band<=.5:
        raise ValueError('Dimensões/durações inválidas.')
    nq,nt=cost.shape
    cost=cost.copy()
    cost[np.abs(np.linspace(0,1,nq)[:,None]-np.linspace(0,1,nt)[None,:])>band]=np.inf
    accumulated,path=librosa.sequence.dtw(C=cost,step_sizes_sigma=np.array([[1,1],[1,2],[2,1]]))
    path=path[::-1]
    # Every step advances both axes. Fill skipped source frames by interpolation.
    xs=path[:,0]/(nq-1)*query_seconds
    ys=target_start+path[:,1]/(nt-1)*target_seconds
    mapping=np.column_stack((np.linspace(0,query_seconds,nq),np.interp(np.linspace(0,query_seconds,nq),xs,ys))).tolist()
    return {'method':'bounded-step-dtw-experimental','mapping_query_to_target_seconds':mapping,
            'target_start_seconds':target_start,'target_end_seconds':target_start+target_seconds,
            'normalized_band':band,'steps':[[1,1],[1,2],[2,1]],
            'mean_path_cost':float(accumulated[-1,-1]/len(path)),
            'status':'experimental_requires_musical_review','internal_warp_verified':False,'training_allowed':False}


def main():
    import numpy as np
    import librosa
    from scipy.spatial.distance import cdist
    from experiments.align_reference import decode
    p=argparse.ArgumentParser();p.add_argument('--pair',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise ValueError('Destino existente.')
    original=json.loads((a.pair/'alignment.json').read_text());regions=original['human_regions']
    clips=[a.pair/r/'clip.wav' for r in ('source','reference')]
    for role,path in zip(('source','reference'),clips):
        meta=json.loads((a.pair/role/'clip.json').read_text())
        if hashlib.sha256(path.read_bytes()).hexdigest()!=meta['clip_sha256']:raise ValueError('Recorte alterado.')
    features=[librosa.feature.chroma_stft(y=decode(path),sr=11025,n_fft=4096,hop_length=1024)+1e-8 for path in clips]
    cost=cdist(features[0].T,features[1].T,metric='cosine')
    duration=regions['source_end']-regions['source_start'];target_duration=regions['reference_end']-regions['reference_start']
    proposed=bounded_path(cost,duration,target_duration,regions['reference_start'])
    proposed.update(human_regions=regions,sources=original['sources'])
    old=original['mapping_query_to_target_seconds'];new=proposed['mapping_query_to_target_seconds']
    report={'original':map_diagnostics(old),'proposed':map_diagnostics(new),
            'max_reference_time_change_seconds':float(max(abs(np.interp(q,np.array(old)[:,0],np.array(old)[:,1])-t) for q,t in new)),
            'checkpoints':[{'source_absolute_seconds':float(regions['source_start']+q),
                            'original_reference_seconds':float(np.interp(q,np.array(old)[:,0],np.array(old)[:,1])),
                            'proposed_reference_seconds':float(np.interp(q,np.array(new)[:,0],np.array(new)[:,1]))} for q in [0,3,6,9,12,15,18,21,24,duration]],
            'status':'temporal_distortion_audited_not_musically_validated','training_allowed':False,
            'limitations':['Limites de inclinação evitam colapsos, mas não demonstram correspondência musical.',
                           'Custos de caminhos com diferentes passos não são diretamente comparáveis.',
                           'Nenhuma transcrição refeita; nenhum ranking usado para seleção.']}
    a.output.mkdir(parents=True)
    (a.output/'alignment-proposed.json').write_text(json.dumps(proposed,indent=2))
    (a.output/'audit.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    np.savez_compressed(a.output/'features.npz',source=features[0],reference=features[1])
    print(json.dumps(report,ensure_ascii=False))


if __name__=='__main__':main()
