"""Bounded, ephemeral MIDI comparison; neither MIDI is stored."""
import asyncio
import hashlib
from fastapi import APIRouter, HTTPException, Query, Request
from packages.music.midi import MAX_BYTES, read_midi
from packages.music.evaluate import EvaluationConfig, evaluate

MAX_BODY = 2 * MAX_BYTES

def compare_router():
    router = APIRouter(prefix='/api/midi')
    lock = asyncio.Lock()

    @router.post('/compare')
    async def compare(request: Request,
                      reference_bytes: int = Query(ge=1, le=MAX_BYTES),
                      time_unit: str = Query(default='quarters', pattern='^(quarters|seconds)$'),
                      onset_tolerance: float = Query(default=.1, ge=0, le=10),
                      duration_tolerance: float = Query(default=.1, ge=0, le=10),
                      duration_relative: float = Query(default=.2, ge=0, le=1)):
        if request.headers.get('content-type', '').split(';')[0] != 'application/octet-stream':
            raise HTTPException(415, 'Envie os dois arquivos MIDI como conteúdo binário.')
        length = request.headers.get('content-length')
        if length:
            try:
                if int(length) > MAX_BODY:
                    raise HTTPException(413, 'Envio acima do limite de 10 MiB.')
            except ValueError:
                raise HTTPException(400, 'Tamanho de envio inválido.')
        if lock.locked():
            raise HTTPException(503, 'Uma comparação está em andamento. Tente novamente em instantes.')
        async with lock:
            body = bytearray()
            async for chunk in request.stream():
                if len(body) + len(chunk) > MAX_BODY:
                    raise HTTPException(413, 'Envio acima do limite de 10 MiB.')
                body.extend(chunk)
            if not 1 <= len(body) - reference_bytes <= MAX_BYTES:
                raise HTTPException(422, 'Selecione dois MIDIs não vazios, de até 5 MiB cada.')
            reference, candidate = bytes(body[:reference_bytes]), bytes(body[reference_bytes:])
            config = EvaluationConfig(time_unit, onset_tolerance, duration_tolerance, duration_relative)
            def work():
                result = evaluate(read_midi(reference), read_midi(candidate), config)
                result['sources'] = {'reference_sha256': hashlib.sha256(reference).hexdigest(),
                                     'candidate_sha256': hashlib.sha256(candidate).hexdigest()}
                return result
            try:
                return await asyncio.to_thread(work)
            except (ValueError, EOFError, OSError, KeyError, IndexError) as exc:
                raise HTTPException(422, str(exc))
    return router
