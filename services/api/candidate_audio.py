"""Render verified candidates directly; bounded process-local MP3 cache."""
import asyncio
from collections import OrderedDict
import hashlib
from pathlib import Path
import re
import tempfile
import anyio
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from packages.music.render import DEFAULT_SOUNDFONT, render_piano
from services.api.sessions import ID, MAX_GENERATIONS
from services.candidate_recovery import recover_candidate

MAX_CACHE_BYTES = 24 * 1024 * 1024


def candidate_audio_router(root):
    root = Path(root)
    router = APIRouter(prefix='/api/sessions')
    lock = asyncio.Lock()
    cache = OrderedDict()

    @router.post('/{session_id}/generations/{generation}/candidates/{candidate_id}/audio')
    async def audio(session_id: str, generation: int, candidate_id: str):
        if not ID.fullmatch(session_id) or not 0 <= generation < MAX_GENERATIONS or not re.fullmatch(r'candidate-[0-9a-f]{16}', candidate_id):
            raise HTTPException(404, 'Candidato não encontrado.')
        folder = root/session_id
        if folder.is_symlink() or not folder.is_dir():
            raise HTTPException(404, 'Sessão não encontrada.')
        if lock.locked():
            raise HTTPException(503, 'Outro áudio está sendo preparado. Tente novamente em instantes.')
        async with lock:
            def work():
                # Always verify provenance, including on cache hits.
                midi = recover_candidate(folder, generation, candidate_id)
                midi_hash = hashlib.sha256(midi).hexdigest()
                if not DEFAULT_SOUNDFONT.is_file():
                    raise RuntimeError('Piano virtual indisponível.')
                key = (midi_hash, hashlib.sha256(DEFAULT_SOUNDFONT.read_bytes()).hexdigest())
                if key in cache:
                    cache.move_to_end(key)
                    return cache[key], midi_hash, 'hit'
                with tempfile.TemporaryDirectory(prefix='piano-candidate-') as temporary:
                    path = Path(temporary)
                    (path/'candidate.mid').write_bytes(midi)
                    report = render_piano(path/'candidate.mid', path/'render')
                    if report['input_sha256'] != midi_hash:
                        raise ValueError('Renderização não corresponde à proposta verificada.')
                    data = (path/'render/piano.mp3').read_bytes()
                    if hashlib.sha256(data).hexdigest() != report['output_sha256']['piano.mp3']:
                        raise ValueError('Integridade do áudio inválida.')
                if len(data) > MAX_CACHE_BYTES:
                    raise ValueError('Áudio excede limite de armazenamento temporário.')
                cache[key] = data
                while len(cache) > 8 or sum(map(len, cache.values())) > MAX_CACHE_BYTES:
                    cache.popitem(last=False)
                return data, midi_hash, 'miss'
            try:
                data, midi_hash, cache_status = await anyio.to_thread.run_sync(work)
            except HTTPException:
                raise
            except (ValueError, KeyError, TypeError, AttributeError, EOFError) as exc:
                raise HTTPException(409, 'Proposta incompatível: confira fonte, checkpoint e limite de 120 segundos.') from exc
            except (RuntimeError, OSError) as exc:
                raise HTTPException(503, 'Não foi possível preparar o piano. O agente deve verificar a fonte e o renderizador.') from exc
        return Response(data, media_type='audio/mpeg', headers={
            'Content-Disposition': f'attachment; filename="generation-{generation}-{candidate_id}.mp3"',
            'Cache-Control': 'no-store', 'X-Piano-Midi-SHA256': midi_hash, 'X-Piano-Cache': cache_status})
    return router
