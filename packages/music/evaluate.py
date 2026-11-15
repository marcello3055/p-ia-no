"""Explainable symbolic correspondence, not an artistic-quality score."""
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
import math
from .midi import Score

@dataclass(frozen=True)
class EvaluationConfig:
    time_unit: str = 'quarters'
    onset_tolerance: float = .1
    duration_absolute_tolerance: float = .1
    duration_relative_tolerance: float = .2
    include_percussion: bool = False

    def validate(self):
        if self.time_unit not in ('quarters', 'seconds'):
            raise ValueError('Unidade temporal deve ser quarters ou seconds.')
        for value in (self.onset_tolerance, self.duration_absolute_tolerance, self.duration_relative_tolerance):
            if not math.isfinite(value) or value < 0:
                raise ValueError('Tolerâncias devem ser finitas e não negativas.')

def metrics(matches, reference_count, candidate_count):
    precision = matches / candidate_count if candidate_count else 0.0
    recall = matches / reference_count
    return {'precision': precision, 'recall': recall,
            'f1': 2 * precision * recall / (precision + recall) if precision + recall else 0.0}

def evaluate(reference: Score, candidate: Score, config: EvaluationConfig | None = None):
    config = config or EvaluationConfig()
    config.validate()
    def rows(score):
        values = []
        for index, note in enumerate(score.to_dict()['notes']):
            if not config.include_percussion and note['channel'] == 9:
                continue
            start, duration = note['start_' + config.time_unit], note['duration_' + config.time_unit]
            if not all(math.isfinite(v) and v >= 0 for v in (start, duration)) or not 0 <= note['pitch'] <= 127:
                raise ValueError('Representação contém nota inválida.')
            values.append({'index': index, 'pitch': note['pitch'], 'start': start, 'duration': duration})
        return values
    ref, cand = rows(reference), rows(candidate)
    if not ref:
        raise ValueError('Referência sem notas avaliáveis; nenhuma pontuação foi calculada.')
    ref_groups, cand_groups = defaultdict(list), defaultdict(list)
    for note in ref:
        ref_groups[note['pitch']].append(note)
    for note in cand:
        cand_groups[note['pitch']].append(note)
    matched = []
    # Equal-pitch, ordered interval matching. Maximum cardinality, not minimum error.
    # Each note can participate once. No nearest-neighbor reuse or note duplication.
    for pitch in sorted(ref_groups):
        left = sorted(ref_groups[pitch], key=lambda x: (x['start'], x['index']))
        right = sorted(cand_groups[pitch], key=lambda x: (x['start'], x['index']))
        i = j = 0
        while i < len(left) and j < len(right):
            a, b = left[i], right[j]
            error = b['start'] - a['start']
            if abs(error) <= config.onset_tolerance + 1e-12:
                duration_error = b['duration'] - a['duration']
                limit = max(config.duration_absolute_tolerance, config.duration_relative_tolerance * a['duration'])
                matched.append({'reference_index': a['index'], 'candidate_index': b['index'], 'pitch': pitch,
                                'onset_error': error, 'duration_error': duration_error,
                                'duration_tolerance': limit, 'duration_match': abs(duration_error) <= limit + 1e-12})
                i += 1
                j += 1
            elif error < 0:
                j += 1
            else:
                i += 1
    matched.sort(key=lambda x: x['reference_index'])
    ref_used = {row['reference_index'] for row in matched}
    cand_used = {row['candidate_index'] for row in matched}
    duration_matches = sum(row['duration_match'] for row in matched)
    # Multiset overlap: deliberately ignores time; it is a diagnostic only.
    inventory = sum((Counter(n['pitch'] for n in ref) & Counter(n['pitch'] for n in cand)).values())
    mae = lambda key: sum(abs(row[key]) for row in matched) / len(matched) if matched else None
    return {
        'schema_version': 1, 'evaluator_version': '0.1.0', 'config': asdict(config),
        'counts': {'reference': len(ref), 'candidate': len(cand), 'matched_pitch_onset': len(matched),
                   'matched_with_duration': duration_matches,
                   'excluded_reference': len(reference.notes) - len(ref),
                   'excluded_candidate': len(candidate.notes) - len(cand)},
        'pitch_inventory_only': metrics(inventory, len(ref), len(cand)),
        'pitch_and_onset': metrics(len(matched), len(ref), len(cand)),
        'pitch_onset_and_duration': metrics(duration_matches, len(ref), len(cand)),
        'matched_errors': {'onset_mae': mae('onset_error'), 'duration_mae': mae('duration_error'),
                           'duration_match_rate': duration_matches / len(matched) if matched else None,
                           'sample_count': len(matched), 'time_unit': config.time_unit},
        'matches': matched,
        'unmatched_reference_indices': [n['index'] for n in ref if n['index'] not in ref_used],
        'unmatched_candidate_indices': [n['index'] for n in cand if n['index'] not in cand_used],
        'warnings': sorted(set(reference.warnings + candidate.warnings)),
        'limitations': [
            'Correspondência simbólica; não mede qualidade artística, harmonia funcional, tocabilidade ou expressividade.',
            'Sem alinhamento automático: diferenças de introdução, repetição ou rubato podem reduzir a correspondência.',
            'quarters compara a grade de semínimas; seconds compara cada execução com seu próprio mapa de andamento.',
            'Pareamento cronológico por altura: maximiza quantidade, mas não minimiza erro nem otimiza duração.',
            'Erros médios usam apenas notas pareadas; consulte também precisão/recall e contagens.',
            'Trilhas e canais não precisam coincidir; canal 10 MIDI (índice 9) é excluído por padrão.',
            'Pitch refere-se à tecla MIDI; duração não inclui sustentação do pedal.'
        ]
    }
