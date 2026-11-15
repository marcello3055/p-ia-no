"""Ephemeral, single-process experimental reduction/rendering endpoint."""
import asyncio
import base64
import json
from pathlib import Path
import tempfile
import anyio
from fastapi import APIRouter, HTTPException, Request
from packages.music.midi import MAX_BYTES, read_midi, write_midi
from packages.music.reduce import reduce_to_piano
from packages.music.render import render_piano


def piano_router():
    router=APIRouter(prefix='/api/experimental')
    lock=asyncio.Lock()

    @router.post('/piano')
    async def piano(request: Request):
        if request.headers.get('content-type','').split(';')[0]!='application/octet-stream':
            raise HTTPException(415,'Envie um MIDI como conteúdo binário.')
        if lock.locked():
            raise HTTPException(503,'Uma geração está em andamento. Tente novamente em instantes.')
        async with lock:
            data=bytearray()
            async for chunk in request.stream():
                if len(data)+len(chunk)>MAX_BYTES:
                    raise HTTPException(413,'Limite de 5 MiB por MIDI.')
                data.extend(chunk)
            def work():
                source=read_midi(bytes(data))
                if source.to_dict()['duration_seconds']>120:
                    raise ValueError('Use um trecho de até 120 segundos neste protótipo.')
                reduced,selection=reduce_to_piano(source)
                with tempfile.TemporaryDirectory(prefix='piano-web-') as folder:
                    root=Path(folder); midi=root/'piano.mid'
                    midi.write_bytes(write_midi(reduced))
                    rendering=render_piano(midi,root/'output')
                    report={'selection':selection,'rendering':rendering}
                    files=[]
                    for path,mime in [(midi,'audio/midi'),(root/'output/piano.wav','audio/wav'),(root/'output/piano.mp3','audio/mpeg')]:
                        files.append({'name':path.name,'mime':mime,'base64':base64.b64encode(path.read_bytes()).decode()})
                    return {'files':files,'report':report}
            try:
                # Default non-abandoning worker keeps cleanup and lock until completion.
                return await anyio.to_thread.run_sync(work)
            except (ValueError,EOFError,KeyError,IndexError) as exc:
                raise HTTPException(422,str(exc))
            except (RuntimeError,OSError) as exc:
                raise HTTPException(503,'Renderizador indisponível. O agente deve verificar as dependências do servidor.') from exc
    return router
