"""MIDI 0/1 to an explicit note representation and back; no audio synthesis."""
from bisect import bisect_right
from collections import defaultdict
from dataclasses import asdict, dataclass
from io import BytesIO
import mido

MAX_BYTES = 5 * 1024**2
MAX_EVENTS = 100000

@dataclass(frozen=True)
class Note:
    track: int
    channel: int
    pitch: int
    velocity: int
    release_velocity: int
    start_tick: int
    end_tick: int
    start_order: int
    end_order: int

@dataclass(frozen=True)
class Event:
    track: int
    tick: int
    order: int
    meta: bool
    message: dict

@dataclass
class Score:
    ticks_per_beat: int
    midi_type: int
    track_ends: list[int]
    notes: list[Note]
    events: list[Event]
    warnings: list[str]

    def tempo_map(self):
        changes = {0: 500000}
        for event in sorted(self.events, key=lambda e: (e.tick, e.track, e.order)):
            if event.message['type'] == 'set_tempo':
                changes[event.tick] = event.message['tempo']
        result = []
        seconds = 0.0
        previous_tick, previous_tempo = 0, 500000
        for tick, tempo in sorted(changes.items()):
            seconds += (tick - previous_tick) * previous_tempo / self.ticks_per_beat / 1e6
            result.append({'tick': tick, 'seconds': seconds, 'microseconds_per_quarter': tempo})
            previous_tick, previous_tempo = tick, tempo
        return result

    def to_dict(self):
        tempos = self.tempo_map()
        ticks = [entry['tick'] for entry in tempos]
        def seconds(tick):
            entry = tempos[bisect_right(ticks, tick) - 1]
            return entry['seconds'] + (tick - entry['tick']) * entry['microseconds_per_quarter'] / self.ticks_per_beat / 1e6
        notes = []
        for note in self.notes:
            row = asdict(note)
            row.update(start_quarters=note.start_tick / self.ticks_per_beat,
                       duration_quarters=(note.end_tick - note.start_tick) / self.ticks_per_beat,
                       start_seconds=seconds(note.start_tick),
                       duration_seconds=seconds(note.end_tick) - seconds(note.start_tick),
                       source='midi', role=None, hand=None, confidence=None)
            notes.append(row)
        return {'schema_version': 1, 'ticks_per_beat': self.ticks_per_beat,
                'midi_type': self.midi_type, 'track_ends': self.track_ends,
                'duration_seconds': seconds(max([0, *self.track_ends, *(n.end_tick for n in self.notes), *(e.tick for e in self.events)])),
                'tempo_map': tempos, 'notes': notes,
                'events': [asdict(event) for event in self.events], 'warnings': self.warnings}

def read_midi(data: bytes) -> Score:
    if not data or len(data) > MAX_BYTES:
        raise ValueError('MIDI vazio ou maior que 5 MiB.')
    try:
        midi = mido.MidiFile(file=BytesIO(data), clip=False)
    except (ValueError, EOFError, OSError, KeyError, IndexError) as exc:
        raise ValueError('Arquivo MIDI inválido.') from exc
    if midi.type not in (0, 1) or not 1 <= midi.ticks_per_beat <= 32767:
        raise ValueError('Somente MIDI tipo 0/1 com resolução PPQN; tipo 2 e SMPTE não são suportados.')
    if not 1 <= len(midi.tracks) <= 128 or sum(map(len, midi.tracks)) > MAX_EVENTS:
        raise ValueError('Número de trilhas/eventos acima do limite.')
    notes, events, ends, warnings = [], [], [], set()
    tempos = {}
    for track_index, track in enumerate(midi.tracks):
        tick, active = 0, {}
        for order, message in enumerate(track):
            tick += message.time
            if not 0 <= tick <= 2**31 - 1:
                raise ValueError('Linha temporal inválida ou excessiva.')
            if message.type in ('note_on', 'note_off'):
                key = (message.channel, message.note)
                if message.type == 'note_on' and message.velocity > 0:
                    if key in active:
                        raise ValueError('Notas da mesma altura/canal sobrepostas na mesma trilha: pareamento ambíguo.')
                    active[key] = (tick, order, message.velocity)
                else:
                    if key not in active:
                        raise ValueError('Fim de nota sem início correspondente.')
                    start, start_order, velocity = active.pop(key)
                    release = message.velocity if message.type == 'note_off' else 0
                    notes.append(Note(track_index, key[0], key[1], velocity, release, start, tick, start_order, order))
                continue
            if message.type == 'end_of_track':
                continue
            if message.type == 'sysex':
                warnings.add('SysEx omitido; dados específicos de instrumento não são reexportados.')
                continue
            if message.type == 'set_tempo':
                if message.tempo <= 0:
                    raise ValueError('Andamento MIDI inválido.')
                if tick in tempos and tempos[tick] != message.tempo:
                    warnings.add('Tempos conflitantes no mesmo tick: prevalece o último na ordem de trilha/evento.')
                tempos[tick] = message.tempo
            if message.type == 'pitchwheel':
                warnings.add('Pitch bend preservado como evento; a altura das notas representa a tecla MIDI.')
            payload = message.dict()
            payload.pop('time', None)
            events.append(Event(track_index, tick, order, message.is_meta, payload))
        if active:
            raise ValueError('Nota sem encerramento; não foi inventada uma duração.')
        ends.append(tick)
    return Score(midi.ticks_per_beat, midi.type, ends,
                 sorted(notes, key=lambda n: (n.start_tick, n.track, n.start_order)), events, sorted(warnings))

def write_midi(score: Score) -> bytes:
    """Export from symbolic notes/events, rather than returning the original bytes."""
    if score.midi_type not in (0, 1) or not 1 <= score.ticks_per_beat <= 32767:
        raise ValueError('Tipo MIDI ou resolução inválidos.')
    tracks = len(score.track_ends)
    if not 1 <= tracks <= 128 or (score.midi_type == 0 and tracks != 1):
        raise ValueError('Número de trilhas inválido.')
    if len(score.notes) * 2 + len(score.events) > MAX_EVENTS:
        raise ValueError('Eventos demais.')
    scheduled = defaultdict(list)
    def add(track, tick, order, message):
        if type(track) is not int or not 0 <= track < tracks or type(tick) is not int or not 0 <= tick <= 2**31 - 1:
            raise ValueError('Trilha ou tick inválido.')
        scheduled[track].append((tick, order, message))
    for note in score.notes:
        if note.end_tick < note.start_tick or note.velocity <= 0:
            raise ValueError('Duração ou intensidade de nota inválida.')
        add(note.track, note.start_tick, note.start_order, mido.Message('note_on', channel=note.channel, note=note.pitch, velocity=note.velocity))
        add(note.track, note.end_tick, note.end_order, mido.Message('note_off', channel=note.channel, note=note.pitch, velocity=note.release_velocity))
    for event in score.events:
        if event.message['type'] in ('note_on', 'note_off', 'end_of_track', 'sysex'):
            raise ValueError('Evento não permitido nesta coleção.')
        payload = {**event.message, 'time': 0}
        message = mido.MetaMessage.from_dict(payload) if event.meta else mido.Message.from_dict(payload)
        add(event.track, event.tick, event.order, message)
    midi = mido.MidiFile(type=score.midi_type, ticks_per_beat=score.ticks_per_beat)
    for index, end in enumerate(score.track_ends):
        if type(end) is not int or not 0 <= end <= 2**31 - 1:
            raise ValueError('Fim de trilha inválido.')
        track, previous = mido.MidiTrack(), 0
        for tick, order, message in sorted(scheduled[index], key=lambda x: (x[0], x[1])):
            track.append(message.copy(time=tick - previous))
            previous = tick
        track.append(mido.MetaMessage('end_of_track', time=max(end, previous) - previous))
        midi.tracks.append(track)
    output = BytesIO()
    midi.save(file=output)
    result = output.getvalue()
    # Validate note pairing after edits, including boundary event ordering.
    read_midi(result)
    return result
