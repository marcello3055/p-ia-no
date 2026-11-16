"""End-to-end DTW inside human-specified regions; no global subsequence search."""
import argparse,json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from packages.music.audio_clip import prepare_clip,digest
from experiments.align_reference import decode
import librosa
import numpy as np
from scipy.spatial.distance import cdist


def anchored_path(query,target,query_seconds,target_seconds,target_start,band=.15):
    if not 0<band<=.5 or min(query_seconds,target_seconds)<=0:
        raise ValueError('Durações/corredor inválidos.')
    q=librosa.feature.chroma_stft(y=query,sr=11025,n_fft=4096,hop_length=1024)+1e-8
    t=librosa.feature.chroma_stft(y=target,sr=11025,n_fft=4096,hop_length=1024)+1e-8
    cost=cdist(q.T,t.T,metric='cosine')
    nq,nt=cost.shape
    outside=np.abs(np.linspace(0,1,nq)[:,None]-np.linspace(0,1,nt)[None,:])>band
    cost[outside]=np.inf
    accumulated,path=librosa.sequence.dtw(C=cost,subseq=False)
    path=path[::-1]
    mapping=[]
    for i in range(nq):
        js=path[path[:,0]==i,1]
        mapping.append([float(i/(nq-1)*query_seconds),float(target_start+np.median(js)/(nt-1)*target_seconds)])
    mapping[0]=[0.0,float(target_start)]
    mapping[-1]=[float(query_seconds),float(target_start+target_seconds)]
    return {'method':'human-regions-normalized-corridor-endpoint-dtw','normalized_band':band,
            'target_start_seconds':target_start,'target_end_seconds':target_start+target_seconds,
            'mapping_query_to_target_seconds':mapping,
            'mean_path_cost':float(accumulated[-1,-1]/len(path)),
            'max_normalized_deviation':float(max(abs(i/(nq-1)-j/(nt-1)) for i,j in path)),
            'status':'human_regions_internal_warp_unverified',
            'region_confirmed_by_user':True,'internal_warp_verified':False,
            'limitations':['Regiões indicadas pelo usuário; 24,5 s é escolha intermediária dentro de 24–25 s.',
                           'DTW interno limitado a corredor de 15% do progresso normalizado; não valida rubato/ataques.',
                           'Custo não é probabilidade. Pontuação não equivale a qualidade musical.']}

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('query',type=Path); p.add_argument('reference',type=Path); p.add_argument('--output-dir',type=Path,required=True); a=p.parse_args()
    a.output_dir.mkdir(parents=True,exist_ok=False)
    source=prepare_clip(a.query,a.output_dir/'source',24.5,25.5)
    target=prepare_clip(a.reference,a.output_dir/'reference',20,18)
    r=anchored_path(decode(a.output_dir/'source/clip.wav'),decode(a.output_dir/'reference/clip.wav'),25.5,18,20)
    r['sources']={'query_sha256':source['clip_sha256'],'target_sha256':digest(a.reference)}
    r['human_regions']={'source_start':24.5,'source_end':50,'reference_start':20,'reference_end':38,'source_start_uncertainty_seconds':[24,25]}
    (a.output_dir/'alignment.json').write_text(json.dumps(r,indent=2,ensure_ascii=False))
    print(json.dumps({k:v for k,v in r.items() if k!='mapping_query_to_target_seconds'}))
