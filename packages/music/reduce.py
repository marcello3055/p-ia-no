"""Deterministic baseline reduction; no melody recognition or learned model."""
from collections import Counter
from dataclasses import asdict, dataclass, replace
from itertools import groupby
from .midi import Event, Score

@dataclass(frozen=True)
class ReductionConfig:
    split_pitch: int = 60
    max_notes_per_hand: int = 3
    max_span: int = 12

    def validate(self):
        for value, low, high in [(self.split_pitch,22,108),(self.max_notes_per_hand,1,5),(self.max_span,0,12)]:
            if type(value) is not int or not low <= value <= high:
                raise ValueError('Configuração de mãos inválida.')


def reduce_to_piano(source: Score, config: ReductionConfig = ReductionConfig()):
    config.validate()
    selected, decisions = [], []
    active = [[], []]
    indexed = sorted(enumerate(source.notes), key=lambda pair: pair[1].start_tick)
    for tick, group in groupby(indexed, key=lambda pair: pair[1].start_tick):
        active = [[n for n in hand if n.end_tick > tick] for hand in active]
        # Lower pitches first on the left; higher first on the right.
        ordered = sorted(group, key=lambda pair: (
            pair[1].pitch >= config.split_pitch,
            pair[1].pitch if pair[1].pitch < config.split_pitch else -pair[1].pitch,
            -pair[1].velocity, pair[0]))
        for index, note in ordered:
            hand = int(note.pitch >= config.split_pitch)
            pitches = [n.pitch for n in active[hand]]
            reason = None
            if note.channel == 9:
                reason = 'percussion'
            elif not 21 <= note.pitch <= 108:
                reason = 'outside_piano_range'
            elif note.end_tick <= tick:
                reason = 'nonpositive_duration'
            elif note.pitch in pitches:
                reason = 'overlapping_same_pitch'
            elif len(pitches) >= config.max_notes_per_hand:
                reason = 'hand_polyphony'
            elif pitches and max(*pitches,note.pitch)-min(*pitches,note.pitch) > config.max_span:
                reason = 'hand_span'
            decisions.append({'source_index':index,'hand':'right' if hand else 'left',
                              'kept':reason is None,'reason':reason or 'selected'})
            if reason is None:
                # Note-offs precede new attacks at an equal tick. Program is earlier.
                output = replace(note, track=hand+1, channel=0, start_order=1, end_order=0)
                selected.append(output)
                active[hand].append(output)
    if not selected:
        raise ValueError('Nenhuma nota utilizável para redução pianística.')
    # Canonical tempo map also resolves conflicting source tempos consistently.
    events = [Event(0,t['tick'],i,True,{'type':'set_tempo','tempo':t['microseconds_per_quarter']})
              for i,t in enumerate(source.tempo_map())]
    for event in sorted(source.events,key=lambda e:(e.tick,e.track,e.order)):
        if event.meta and event.message['type'] in ('time_signature','key_signature'):
            events.append(Event(0,event.tick,len(events),True,dict(event.message)))
    events.append(Event(0,0,-1,False,{'type':'program_change','channel':0,'program':0}))
    for track,name in enumerate(('P-IA-NO piano','Left hand','Right hand')):
        events.append(Event(track,0,-2,True,{'type':'track_name','name':name}))
    end = max([*source.track_ends,*(n.end_tick for n in selected),*(e.tick for e in events)])
    warnings = ['Redução heurística: voz aguda não comprova melodia. Limites de mão não garantem tocabilidade.',
                'Pedal, controladores, pitch bend e instrumentos da origem removidos; sem interpretação nova.']
    output = Score(source.ticks_per_beat,1,[end]*3,selected,events,warnings)
    report = {'schema_version':1,'reducer_version':'0.1.0','config':asdict(config),
              'input_notes':len(source.notes),'output_notes':len(selected),
              'discard_counts':dict(Counter(d['reason'] for d in decisions if not d['kept'])),
              'decisions':sorted(decisions,key=lambda d:d['source_index']),
              'source_warnings':list(source.warnings),'limitations':warnings}
    return output, report
