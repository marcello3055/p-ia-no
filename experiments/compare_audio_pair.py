"""Provisional supervised ranking from a proposed alignment; NEVER authorizes training."""
import argparse,json,time
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from packages.music.audio_clip import prepare_clip,digest
from packages.music.midi import Note,Score
from packages.music.time_map import warp_reference
from packages.music.population import initialize_population
from packages.music.ranking import rank_population
from packages.music.evaluate import EvaluationConfig

p=argparse.ArgumentParser(); p.add_argument('reference',type=Path); p.add_argument('--source-report',type=Path,required=True); p.add_argument('--alignment',type=Path,required=True); p.add_argument('--output-dir',type=Path,required=True); a=p.parse_args()
if a.output_dir.exists(): raise ValueError('Destino existente')
alignment=json.loads(a.alignment.read_text())
if digest(a.reference)!=alignment['sources']['target_sha256']: raise ValueError('Referência diferente do alinhamento')
source_report=json.loads(a.source_report.read_text())
if source_report['clip']['clip_sha256']!=alignment['sources']['query_sha256']: raise ValueError('Fonte diferente do alinhamento')
start=max(0,alignment['target_start_seconds']-1)
seconds=alignment['target_end_seconds']+1-start
if not 1<=seconds<=30: raise ValueError('Trecho candidato excede bloco de 30 segundos')
a.output_dir.mkdir(parents=True)
clip=prepare_clip(a.reference,a.output_dir/'reference',start,seconds)
import basic_pitch,numpy as np,onnxruntime as ort
from basic_pitch.inference import Model,predict
model_path=Path(basic_pitch.__file__).parent/'saved_models/icassp_2022/nmp.onnx'
model=Model(model_path); options=ort.SessionOptions(); options.intra_op_num_threads=2; options.inter_op_num_threads=1
model.model=ort.InferenceSession(str(model_path),sess_options=options,providers=['CPUExecutionProvider'])
t=time.perf_counter(); raw,midi,events=predict(a.output_dir/'reference/clip.wav',model); elapsed=time.perf_counter()-t
midi.write(str(a.output_dir/'reference-raw.mid')); np.savez_compressed(a.output_dir/'reference-activations.npz',**raw)
estimates=[{'start_seconds':float(s),'end_seconds':float(e),'pitch':int(p),'activation':float(v)} for s,e,p,v,_ in events]
(a.output_dir/'reference-estimates.json').write_text(json.dumps(estimates,indent=2))
ref,diagnostic=warp_reference(estimates,alignment['mapping_query_to_target_seconds'],start)
notes=[Note(0,0,e['pitch'],max(1,min(127,round(e['activation']*127))),0,round(e['start_seconds']*960),round(e['end_seconds']*960),1,0) for e in source_report['estimates']]
source=Score(480,1,[round(source_report['clip']['actual_seconds']*960)],notes,[],[])
manifest=initialize_population()
r=rank_population(source,ref,manifest,config=EvaluationConfig(time_unit='seconds',onset_tolerance=.2,duration_absolute_tolerance=.2))
r.update(status='diagnostic_only_alignment_unverified',training_allowed=False,
         provenance={'source_report_sha256':digest(a.source_report),'reference_sha256':digest(a.reference),'alignment_sha256':digest(a.alignment),'model_sha256':digest(model_path)},
         alignment=alignment,reference_clip=clip,warping=diagnostic,reference_estimates=len(estimates),reference_inference_seconds=elapsed)
r['limitations']+=['Alinhamento ambíguo; NÃO usar este ranking para seleção/reprodução sem validação.','Ambos os lados derivam de transcrições incertas; score não é precisão nem qualidade artística.','Notas nas bordas podem ser truncadas. Tolerância 200 ms é experimental, não calibrada.']
(a.output_dir/'population.json').write_text(json.dumps(manifest,indent=2))
(a.output_dir/'ranking.json').write_text(json.dumps(r,indent=2,ensure_ascii=False))
print(json.dumps({k:r[k] for k in ['status','training_allowed','evaluated','unique_evaluations','baseline_score','best_score','reference_estimates','warping']}))
