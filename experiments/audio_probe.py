"""Controlled CPU transcription experiment; synthetic fixtures, not orchestral validation.
Run in .venv-audio. New output directory required; fixtures and raw model results stay outside Git.
"""
import argparse
import ctypes as C
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time
import wave
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from packages.music.midi import Note, Score, write_midi
from packages.music.render import _library, DEFAULT_SOUNDFONT
from packages.music.evaluate import evaluate, EvaluationConfig


def fixture(root, name, voices):
    """voices = [(program, [(pitch, start_seconds, duration_seconds), ...])]."""
    lib=_library(); settings=lib.new_fluid_settings(); synth=None
    try:
        lib.fluid_settings_setnum(settings,b'synth.sample-rate',22050)
        lib.fluid_settings_setnum(settings,b'synth.gain',.15)
        lib.fluid_settings_setint(settings,b'synth.reverb.active',0)
        lib.fluid_settings_setint(settings,b'synth.chorus.active',0)
        synth=lib.new_fluid_synth(settings)
        if not synth: raise RuntimeError('Synth unavailable')
        sf=lib.fluid_synth_sfload(synth,str(DEFAULT_SOUNDFONT).encode(),0)
        if sf<0: raise RuntimeError('SoundFont unavailable')
        events=[]; notes=[]
        for channel,(program,sequence) in enumerate(voices):
            if lib.fluid_synth_program_select(synth,channel,sf,0,program)!=0: raise RuntimeError('Preset unavailable')
            for pitch,start,duration in sequence:
                events.extend([(round(start*22050),1,channel,pitch),(round((start+duration)*22050),0,channel,pitch)])
                notes.append(Note(channel,channel,pitch,85,0,round(start*960),round((start+duration)*960),1,0))
        reference=Score(480,1,[max(n.end_tick for n in notes)]*len(voices),notes,[],[])
        (root/f'{name}-reference.mid').write_bytes(write_midi(reference))
        cursor=0; peak=0
        with wave.open(str(root/f'{name}.wav'),'wb') as wav:
            wav.setparams((2,2,22050,0,'NONE','not compressed'))
            def emit(frames):
                nonlocal peak
                while frames>0:
                    count=min(frames,4096); buffer=(C.c_int16*(count*2))()
                    if lib.fluid_synth_write_s16(synth,count,buffer,0,2,buffer,1,2)!=0: raise RuntimeError('Synthesis failed')
                    peak=max(peak,max(abs(x) for x in buffer))
                    wav.writeframesraw(bytes(buffer)); frames-=count
            for frame,on,channel,pitch in sorted(events):
                emit(frame-cursor); cursor=frame
                status=lib.fluid_synth_noteon(synth,channel,pitch,85) if on else lib.fluid_synth_noteoff(synth,channel,pitch)
                if status!=0: raise RuntimeError('Note failed')
            emit(22050)
        if not 0<peak<32767: raise RuntimeError('Silent/clipped fixture')
        subprocess.run(['ffmpeg','-v','error','-nostdin','-n','-i',str(root/f'{name}.wav'),'-codec:a','libmp3lame','-b:a','192k',str(root/f'{name}.mp3')],check=True,timeout=30)
        return reference
    finally:
        if synth: lib.delete_fluid_synth(synth)
        lib.delete_fluid_settings(settings)


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--output-dir',type=Path,required=True); args=parser.parse_args()
    if sys.byteorder!='little': raise RuntimeError('Fixture generator currently requires little endian')
    args.output_dir.mkdir(parents=True,exist_ok=False)
    # Imported only in the isolated experiment environment.
    import basic_pitch
    from basic_pitch.inference import Model, predict
    import onnxruntime as ort
    import numpy as np
    model_path=Path(basic_pitch.__file__).parent/'saved_models/icassp_2022/nmp.onnx'
    started=time.perf_counter()
    model=Model(model_path)
    # Explicitly constrain CPU threads and reuse one loaded model for all cases.
    options=ort.SessionOptions(); options.intra_op_num_threads=2; options.inter_op_num_threads=1
    model.model=ort.InferenceSession(str(model_path),sess_options=options,providers=['CPUExecutionProvider'])
    load_seconds=time.perf_counter()-started
    melody=[(p,.5+i*.75,.55) for i,p in enumerate([60,64,67,72,71,67,64,60])]
    chords=[(p,.5+i*1.5,1.2) for i,chord in enumerate([[48,60,64,67],[53,60,65,69],[55,62,67,71],[48,60,64,72]]) for p in chord]
    fixtures={'piano_melody':[(0,melody)],'piano_chords':[(0,chords)],
              'synthetic_ensemble':[(73,melody),(48,[(p-12,t,d) for p,t,d in chords])]}
    results={}
    for name,voices in fixtures.items():
        reference=fixture(args.output_dir,name,voices)
        audio=args.output_dir/f'{name}.mp3'
        start=time.perf_counter()
        raw,midi,events=predict(audio,model,multiple_pitch_bends=False)
        seconds=time.perf_counter()-start
        midi.write(str(args.output_dir/f'{name}-raw.mid'))
        np.savez_compressed(args.output_dir/f'{name}-activations.npz',**raw)
        # One track per estimated note avoids ambiguous overlaps; pitch bends ignored explicitly.
        notes=[Note(i,0,int(p),max(1,min(127,round(float(a)*127))),0,round(float(s)*960),round(float(e)*960),1,0)
               for i,(s,e,p,a,_) in enumerate(events)]
        candidate=Score(480,1,[max([0,*[n.end_tick for n in notes]])],notes,[],[])
        metrics=evaluate(reference,candidate,EvaluationConfig(time_unit='seconds',onset_tolerance=.1,duration_absolute_tolerance=.15,duration_relative_tolerance=.2))
        (args.output_dir/f'{name}-evaluation.json').write_text(json.dumps(metrics,indent=2))
        results[name]={'reference_notes':len(reference.notes),'estimated_notes':len(notes),'inference_seconds':seconds,
                       'pitch_onset':metrics['pitch_and_onset'],'pitch_onset_duration':metrics['pitch_onset_and_duration'],
                       'matched_errors':metrics['matched_errors'],'audio_sha256':hashlib.sha256(audio.read_bytes()).hexdigest(),
                       'estimated_events':[{'start':float(s),'end':float(e),'pitch':int(p),'activation':float(a)} for s,e,p,a,_ in events]}
        print(name,json.dumps({k:v for k,v in results[name].items() if k!='estimated_events'}),flush=True)
    report={'experiment':'audio-probe-0.1','versions':{p:importlib.metadata.version(p) for p in ['basic-pitch','onnxruntime','numpy','librosa','pretty-midi']},
            'model_sha256':hashlib.sha256(model_path.read_bytes()).hexdigest(),'soundfont_sha256':hashlib.sha256(DEFAULT_SOUNDFONT.read_bytes()).hexdigest(),
            'providers':model.model.get_providers(),'model_load_seconds':load_seconds,'peak_rss_mib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,
            'thresholds':{'onset':.5,'frame':.3,'minimum_note_ms':127.7,'melodia_trick':True},'results':results,
            'limitations':['Synthetic small fixtures; not real orchestra or generalization evidence.','No training, tuning, alignment or source separation.','Activation is not calibrated confidence.','Timing includes cold preprocessing/JIT for first case; excludes fixture synthesis.','Pitch bends omitted from evaluation; no expressivity evaluation.']}
    (args.output_dir/'report.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__': main()
