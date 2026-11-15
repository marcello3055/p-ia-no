"""Offline piano rendering through the system FluidSynth library; no audio device."""
import ctypes as C
import ctypes.util
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import wave
from .midi import MAX_BYTES, read_midi

DEFAULT_SOUNDFONT = Path('/usr/share/sounds/sf2/TimGM6mb.sf2')
RATE = 44100

def _library():
    name = ctypes.util.find_library('fluidsynth')
    if not name:
        raise RuntimeError('Biblioteca libfluidsynth não disponível.')
    lib = C.CDLL(name)
    signatures = {
        'new_fluid_settings': (C.c_void_p, []),
        'delete_fluid_settings': (None, [C.c_void_p]),
        'fluid_settings_setnum': (C.c_int, [C.c_void_p,C.c_char_p,C.c_double]),
        'fluid_settings_setint': (C.c_int, [C.c_void_p,C.c_char_p,C.c_int]),
        'new_fluid_synth': (C.c_void_p,[C.c_void_p]),
        'delete_fluid_synth': (None,[C.c_void_p]),
        'fluid_synth_sfload': (C.c_int,[C.c_void_p,C.c_char_p,C.c_int]),
        'fluid_synth_program_select': (C.c_int,[C.c_void_p,C.c_int,C.c_int,C.c_int,C.c_int]),
        'fluid_synth_noteon': (C.c_int,[C.c_void_p,C.c_int,C.c_int,C.c_int]),
        'fluid_synth_noteoff': (C.c_int,[C.c_void_p,C.c_int,C.c_int]),
        'fluid_synth_write_s16': (C.c_int,[C.c_void_p,C.c_int,C.c_void_p,C.c_int,C.c_int,C.c_void_p,C.c_int,C.c_int]),
        'fluid_version_str': (C.c_char_p,[]),
    }
    for name,(result,args) in signatures.items():
        fn=getattr(lib,name); fn.restype=result; fn.argtypes=args
    return lib

def render_piano(midi_path, destination, soundfont=DEFAULT_SOUNDFONT):
    """New directory only. Bounded 120-second prototype; fixed piano bank 0/program 0.

    Input must be the reducer's single-channel output. No input controllers applied.
    """
    destination=Path(destination); soundfont=Path(soundfont)
    if destination.exists():
        raise ValueError('Destino já existe; escolha uma pasta nova.')
    if not soundfont.is_file():
        raise ValueError('SoundFont ausente.')
    if not shutil.which('ffmpeg'):
        raise RuntimeError('FFmpeg não disponível.')
    with Path(midi_path).open('rb') as f:
        data=f.read(MAX_BYTES+1)
    score=read_midi(data)
    if not score.notes or any(n.channel != 0 or not 21 <= n.pitch <=108 or n.end_tick<=n.start_tick for n in score.notes):
        raise ValueError('Esperado MIDI reduzido: notas positivas, canal 0 e extensão de piano.')
    for e in score.events:
        if not e.meta and not (e.message['type']=='program_change' and e.message['channel']==0 and e.message['program']==0):
            raise ValueError('MIDI contém controladores/instrumentos não suportados; reduza primeiro.')
    rows=score.to_dict()
    duration=rows['duration_seconds']
    if duration>120:
        raise ValueError('Protótipo limitado a 120 segundos por renderização.')
    timeline=[]
    for n in rows['notes']:
        if round((n['start_seconds']+n['duration_seconds'])*RATE) <= round(n['start_seconds']*RATE):
            raise ValueError('Nota curta demais para a resolução de áudio.')
        timeline.extend([(round(n['start_seconds']*RATE),1,n['pitch'],n['velocity']),
                         (round((n['start_seconds']+n['duration_seconds'])*RATE),0,n['pitch'],0)])
    timeline.sort()
    active=set()
    for _,on,pitch,_ in timeline:
        if on:
            if pitch in active:
                raise ValueError('Altura sobreposta entre trilhas; reduza primeiro.')
            active.add(pitch)
        else:
            active.discard(pitch)
    lib=_library(); settings=lib.new_fluid_settings(); synth=None
    if not settings:
        raise RuntimeError('Falha ao criar configurações do sintetizador.')
    created=False
    try:
        for key,value in [(b'synth.sample-rate',RATE),(b'synth.gain',0.2)]:
            if lib.fluid_settings_setnum(settings,key,value)!=0:
                raise RuntimeError('Configuração FluidSynth indisponível.')
        for key,value in [(b'synth.reverb.active',0),(b'synth.chorus.active',0),(b'synth.cpu-cores',1)]:
            if lib.fluid_settings_setint(settings,key,value)!=0:
                raise RuntimeError('Configuração FluidSynth indisponível.')
        synth=lib.new_fluid_synth(settings)
        if not synth:
            raise RuntimeError('Falha ao criar sintetizador.')
        sfid=lib.fluid_synth_sfload(synth,str(soundfont).encode(),0)
        if sfid<0 or lib.fluid_synth_program_select(synth,0,sfid,0,0)!=0:
            raise ValueError('SoundFont não contém piano no banco 0/programa 0.')
        with tempfile.TemporaryDirectory(prefix='p-ia-no-render-') as folder:
            root=Path(folder); wav=root/'piano.wav'; peak=0; cursor=0
            with wave.open(str(wav),'wb') as output:
                output.setparams((2,2,RATE,0,'NONE','not compressed'))
                def emit(frames):
                    nonlocal peak
                    while frames>0:
                        count=min(frames,4096); buffer=(C.c_int16*(count*2))()
                        if lib.fluid_synth_write_s16(synth,count,buffer,0,2,buffer,1,2)!=0:
                            raise RuntimeError('Falha na síntese.')
                        peak=max(peak,max(abs(v) for v in buffer))
                        raw=bytes(buffer)
                        if sys.byteorder!='little':
                            import array
                            swapped=array.array('h'); swapped.frombytes(raw); swapped.byteswap(); raw=swapped.tobytes()
                        output.writeframesraw(raw); frames-=count
                for frame,on,pitch,velocity in timeline:
                    emit(frame-cursor); cursor=frame
                    result=lib.fluid_synth_noteon(synth,0,pitch,velocity) if on else lib.fluid_synth_noteoff(synth,0,pitch)
                    if result!=0:
                        raise RuntimeError('Falha ao executar evento de nota.')
                total=round((duration+3)*RATE)
                emit(total-cursor)
            if peak==0 or peak>=32767:
                raise ValueError('Áudio silencioso ou saturado; ajuste a entrada/ganho.')
            ff=subprocess.run(['ffmpeg','-nostdin','-v','error','-n','-i',str(wav),'-codec:a','libmp3lame','-b:a','192k',str(root/'piano.mp3')],capture_output=True,text=True,timeout=60)
            if ff.returncode:
                raise RuntimeError('Falha na codificação MP3: '+ff.stderr[-500:])
            report={'renderer_version':'0.1.0','fluidsynth_version':lib.fluid_version_str().decode(),
                    'ffmpeg_version':subprocess.check_output(['ffmpeg','-version'],text=True).splitlines()[0],
                    'soundfont':soundfont.name,'soundfont_sha256':hashlib.sha256(soundfont.read_bytes()).hexdigest(),
                    'input_sha256':hashlib.sha256(data).hexdigest(),'sample_rate':RATE,'channels':2,
                    'gain':0.2,'bank':0,'program':0,'reverb':False,'chorus':False,'tail_seconds':3,
                    'duration_seconds':total/RATE,'peak_pcm16':peak,'notes':len(score.notes),
                    'output_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (wav,root/'piano.mp3')},
                    'limitations':['Sem expressão nova, pedal ou avaliação auditiva. Piano inicial, não qualidade final.']}
            (root/'render.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
            destination.mkdir(parents=False); created=True
            for p in root.iterdir():
                shutil.copyfile(p,destination/p.name)
        return report
    except BaseException:
        if created:
            shutil.rmtree(destination)
        raise
    finally:
        if synth:
            lib.delete_fluid_synth(synth)
        lib.delete_fluid_settings(settings)
