"""Experimental chroma subsequence alignment. Proposed correspondence, not confidence."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from packages.music.audio_clip import digest
import numpy as np
import librosa


def decode(path):
    raw=subprocess.run(['ffmpeg','-v','error','-nostdin','-protocol_whitelist','file,pipe','-i',str(path),'-t','600','-ac','1','-ar','11025','-f','f32le','pipe:1'],capture_output=True,check=True,timeout=60).stdout
    return np.frombuffer(raw,dtype='<f4')

def align(query,target):
    q=librosa.feature.chroma_stft(y=query,sr=11025,n_fft=4096,hop_length=2048)
    t=librosa.feature.chroma_stft(y=target,sr=11025,n_fft=4096,hop_length=2048)
    # Zero vectors must remain finite under cosine distance.
    q=q+1e-8; t=t+1e-8
    costs,path=librosa.sequence.dtw(X=q,Y=t,metric='cosine',subseq=True)
    hop=2048/11025
    path=path[::-1]
    points=[]
    for i in np.unique(path[:,0]):
        js=path[path[:,0]==i,1]
        points.append([float(i*hop),float(np.median(js)*hop)])
    # Report separated alternative endpoints, without calling them probabilities.
    values=costs[-1]/q.shape[1]
    alternatives=[]
    for j in np.argsort(values):
        if all(abs(j-a['frame'])>round(10/hop) for a in alternatives):
            alternatives.append({'frame':int(j),'end_seconds':float(j*hop),'mean_cost':float(values[j])})
        if len(alternatives)==3: break
    return {'method':'chroma-stft-cosine-subsequence-dtw','hop_seconds':hop,
            'target_start_seconds':float(path[0,1]*hop),'target_end_seconds':float(path[-1,1]*hop),
            'mean_path_cost':float(costs[-1,path[-1,1]]/len(path)),
            'mapping_query_to_target_seconds':points,'alternative_endpoints':alternatives,
            'status':'proposed_unverified','limitations':['Chroma ignora oitavas e instrumentos; repetições podem gerar correspondências ambíguas.','Custo DTW não é confiança calibrada.','Precisão temporal limitada pelo hop; validar auditivamente antes de treinamento.']}

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('query',type=Path); p.add_argument('target',type=Path); p.add_argument('--output',type=Path,required=True); a=p.parse_args()
    if a.output.exists(): raise ValueError('Destino existente')
    report=align(decode(a.query),decode(a.target))
    report['sources']={'query_sha256':digest(a.query),'target_sha256':digest(a.target)}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('x') as f: json.dump(report,f,indent=2,ensure_ascii=False)
    print(json.dumps({k:v for k,v in report.items() if k not in ['mapping_query_to_target_seconds','sources']}))
