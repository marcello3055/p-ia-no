"""Local CPU experiment on a user-provided excerpt; no accuracy claim without reference."""
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import resource
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from packages.music.audio_clip import prepare_clip
from packages.music.midi import Note,Score,write_midi
from packages.music.reduce import reduce_to_piano
from packages.music.render import render_piano


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('input',type=Path)
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--start',type=float,default=30)
    parser.add_argument('--seconds',type=float,default=20)
    args=parser.parse_args()
    root=args.output_dir
    if root.exists(): raise ValueError('Escolha uma pasta nova; resultados existentes não serão sobrescritos.')
    root.mkdir(parents=True)
    clip=prepare_clip(args.input,root/'input',args.start,args.seconds)
    if clip['silent']: raise ValueError('Trecho silencioso; selecione outro início.')
    import basic_pitch
    import numpy as np
    import onnxruntime as ort
    from basic_pitch.inference import Model,predict
    model_path=Path(basic_pitch.__file__).parent/'saved_models/icassp_2022/nmp.onnx'
    model=Model(model_path)
    options=ort.SessionOptions(); options.intra_op_num_threads=2; options.inter_op_num_threads=1
    model.model=ort.InferenceSession(str(model_path),sess_options=options,providers=['CPUExecutionProvider'])
    started=time.perf_counter()
    raw,midi,events=predict(root/'input/clip.wav',model,multiple_pitch_bends=False)
    elapsed=time.perf_counter()-started
    midi.write(str(root/'transcription-raw.mid'))
    np.savez_compressed(root/'activations.npz',**raw)
    notes=[]; estimates=[]
    for i,(start,end,pitch,activation,bends) in enumerate(events):
        start=float(start); end=min(float(end),clip['actual_seconds'])
        if end<=start: continue
        a=float(activation)
        estimates.append({'start_seconds':start,'end_seconds':end,'pitch':int(pitch),'activation':a})
        notes.append(Note(0,0,int(pitch),max(1,min(127,round(a*127))),0,round(start*960),round(end*960),1,0))
    score=Score(480,1,[round(clip['actual_seconds']*960)],notes,[],[])
    reduced,selection=reduce_to_piano(score)
    path=root/'piano.mid'; path.write_bytes(write_midi(reduced))
    rendering=render_piano(path,root/'piano')
    durations=[e['end_seconds']-e['start_seconds'] for e in estimates]
    timeline=sorted([(e['start_seconds'],1) for e in estimates]+[(e['end_seconds'],-1) for e in estimates])
    active=peak=0
    for _,delta in timeline: active+=delta; peak=max(peak,active)
    report={'experiment':'real-clip-0.1','clip':clip,'versions':{p:importlib.metadata.version(p) for p in ['basic-pitch','onnxruntime','librosa','numpy']},
            'model_sha256':hashlib.sha256(model_path.read_bytes()).hexdigest(),'inference_seconds':elapsed,
            'peak_rss_mib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,'provider':model.model.get_providers(),
            'thresholds':{'onset':.5,'frame':.3,'minimum_note_ms':127.7,'melodia_trick':True},
            'estimated_notes':len(notes),'peak_simultaneous_estimates':peak,
            'duration_seconds':{'min':min(durations),'median':float(np.median(durations)),'max':max(durations)},
            'pitch_range':[min(n.pitch for n in notes),max(n.pitch for n in notes)],
            'estimates':estimates,'reduction':selection,'rendering':rendering,
            'reference_metrics':None,
            'limitations':['Sem referência simbólica: precisão, recall e F1 não calculados.',
                           'Ativações não são confiança calibrada; velocidade derivada da ativação não recupera dinâmica original.',
                           'Sem separação instrumental, identificação confiável de melodia, pedal ou rubato novo.',
                           'Limites de simultaneidade/alcance não garantem tocabilidade.',
                           'Resultados são um teste de pipeline, não arranjador aprovado.']}
    (root/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['estimated_notes','peak_simultaneous_estimates','pitch_range','duration_seconds','inference_seconds','peak_rss_mib']}))
    print(json.dumps({'kept':selection['output_notes'],'dropped':selection['discard_counts'],'render_seconds':rendering['duration_seconds']}))

if __name__=='__main__': main()
