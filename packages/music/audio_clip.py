"""Bounded local audio preparation for experiments; no transcription or URL fetching."""
from array import array
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import wave

MAX_FILE_BYTES = 100 * 1024**2

def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024**2),b''):
            h.update(chunk)
    return h.hexdigest()

def run(command):
    try:
        return subprocess.run(command,check=True,capture_output=True,text=True,timeout=60).stdout
    except (subprocess.CalledProcessError,subprocess.TimeoutExpired) as exc:
        raise ValueError('Não foi possível analisar ou decodificar o áudio dentro do limite.') from exc

def prepare_clip(source, destination, start=0.0, seconds=20.0):
    source=Path(source).resolve(); destination=Path(destination)
    if not all(isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) for v in (start,seconds)) or start<0 or not 1<=seconds<=30:
        raise ValueError('Início deve ser finito e não negativo; trecho deve ter entre 1 e 30 segundos.')
    if not source.is_file() or not 0<source.stat().st_size<=MAX_FILE_BYTES:
        raise ValueError('Escolha um arquivo local não vazio de até 100 MiB.')
    for tool in ('ffmpeg','ffprobe'):
        if not shutil.which(tool): raise RuntimeError(f'{tool} não disponível no servidor.')
    info=json.loads(run(['ffprobe','-v','error','-protocol_whitelist','file,pipe','-show_format','-show_streams','-of','json',str(source)]))
    fmt=info.get('format',{}); formats=set(fmt.get('format_name','').split(','))
    streams=[s for s in info.get('streams',[]) if s.get('codec_type')=='audio']
    duration=float(fmt.get('duration',0))
    if not formats.intersection({'mp3','wav','flac'}) or not streams or not math.isfinite(duration) or not 0<duration<=1800:
        raise ValueError('Áudio deve ser MP3, WAV ou FLAC válido, com duração de até 30 minutos.')
    if start>=duration:
        raise ValueError('O início solicitado está fora da duração do áudio.')
    version=run(['ffmpeg','-version']).splitlines()[0]
    key={'preparer_version':'0.1.0','source_sha256':digest(source),'start_seconds':float(start),
         'requested_seconds':float(seconds),'sample_rate':22050,'channels':1,'pcm_bits':16,'ffmpeg_version':version}
    if destination.exists():
        try:
            report=json.loads((destination/'clip.json').read_text())
            if report['cache_key']==key and digest(destination/'clip.wav')==report['clip_sha256']:
                return {**report,'cache_hit':True}
        except (OSError,ValueError,KeyError,TypeError):
            pass
        raise ValueError('Destino existente não corresponde a um cache íntegro; escolha uma pasta nova.')
    destination.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='piano-clip-',dir=destination.parent) as folder:
        root=Path(folder); output=root/'clip.wav'
        run(['ffmpeg','-nostdin','-v','error','-protocol_whitelist','file,pipe','-i',str(source),
             '-ss',str(start),'-t',str(seconds),'-map','0:a:0','-vn','-ac','1','-ar','22050','-c:a','pcm_s16le',str(output)])
        with wave.open(str(output),'rb') as wav:
            frames=wav.getnframes(); raw=wav.readframes(frames)
            if wav.getnchannels()!=1 or wav.getframerate()!=22050 or wav.getsampwidth()!=2 or not frames:
                raise ValueError('Trecho decodificado inválido ou vazio.')
        samples=array('h',raw)
        if sys.byteorder!='little': samples.byteswap()
        peak=max(abs(v) for v in samples)
        actual=frames/22050
        report={'cache_key':key,'source_format':fmt['format_name'],'source_duration_seconds':duration,
                'actual_seconds':actual,'clipped_at_end':actual<seconds-.05,'clip_sha256':digest(output),
                'peak_pcm16':peak,'silent':peak==0,'cache_hit':False,
                'warnings':['Mistura para mono pode cancelar sinais fora de fase; não normaliza volume nem remove silêncio.',
                            'Recorte temporal, sem identificação automática de frases ou seções.']}
        (root/'clip.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        # Reserve destination exclusively; never replace existing user files.
        destination.mkdir()
        try:
            shutil.copyfile(output,destination/'clip.wav')
            shutil.copyfile(root/'clip.json',destination/'clip.json')
        except BaseException:
            shutil.rmtree(destination)
            raise
    return report
