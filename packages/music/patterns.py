"""Basic pitch-class and attack-pattern diagnostics, not harmonic analysis."""
from collections import defaultdict

NAMES = ['C', 'C♯', 'D', 'D♯', 'E', 'F', 'F♯', 'G', 'G♯', 'A', 'A♯', 'B']

def pitch_classes(reference, candidate):
    def histogram(notes):
        values = [0.0] * 12
        for note in notes:
            values[note['pitch'] % 12] += note['duration']
        total = sum(values)
        return values, [value / total for value in values] if total else None
    ref_weight, ref = histogram(reference)
    cand_weight, cand = histogram(candidate)
    # Silence is not counted as agreement. If reference has no duration, undefined.
    overlap = sum(min(a, b) for a, b in zip(ref, cand)) if ref and cand else 0.0 if ref else None
    timeline = defaultdict(list)
    for side, notes in enumerate((reference, candidate)):
        for note in notes:
            if note['duration'] > 0:
                pitch_class = note['pitch'] % 12
                timeline[note['start']].append((side, pitch_class, 1))
                timeline[note['start'] + note['duration']].append((side, pitch_class, -1))
    active = [[0] * 12, [0] * 12]
    previous = 0.0
    intersection = union = 0.0
    for time in sorted(timeline):
        elapsed = time - previous
        intersection += elapsed * sum(a > 0 and b > 0 for a, b in zip(*active))
        union += elapsed * sum(a > 0 or b > 0 for a, b in zip(*active))
        for side, pc, delta in timeline[time]:
            active[side][pc] += delta
        previous = time
    return {
        'class_order': NAMES, 'reference_duration_weights': ref_weight,
        'candidate_duration_weights': cand_weight,
        'reference_distribution': ref, 'candidate_distribution': cand,
        'global_distribution_overlap': overlap,
        'temporal_pitch_class_jaccard': intersection / union if union else None,
        'intersection_class_time': intersection, 'union_class_time': union,
        'interpretation': 'Ignora oitavas; não reconhece acordes, tonalidade ou função harmônica. Distribuição global ignora ordem; comparação temporal exige alinhamento.'
    }

def attack_patterns(reference, candidate, tolerance):
    # Exactly simultaneous notes form one attack, irrespective of chord density.
    left = sorted({note['start'] for note in reference})
    right = sorted({note['start'] for note in candidate})
    i = j = matched = 0
    while i < len(left) and j < len(right):
        delta = right[j] - left[i]
        if abs(delta) <= tolerance + 1e-12:
            matched += 1; i += 1; j += 1
        elif delta < 0:
            j += 1
        else:
            i += 1
    precision = matched / len(right) if right else 0.0
    recall = matched / len(left) if left else 0.0
    reference_intervals = [b-a for a,b in zip(left, left[1:])]
    candidate_intervals = [b-a for a,b in zip(right, right[1:])]
    similarity = None
    reason = None
    if len(left) < 3 or len(right) < 3:
        reason = 'São necessários pelo menos três ataques em cada arquivo para comparar o padrão relativo.'
    elif len(left) != len(right):
        reason = 'Quantidade de ataques diferente: padrão relativo não calculado, sem alinhamento automático.'
    else:
        total_ref, total_cand = sum(reference_intervals), sum(candidate_intervals)
        distance = sum(abs(a/total_ref - b/total_cand) for a,b in zip(reference_intervals,candidate_intervals))
        similarity = max(0.0, min(1.0, 1 - distance / 2))
    return {
        'reference_attack_count': len(left), 'candidate_attack_count': len(right), 'matched_attacks': matched,
        'precision': precision, 'recall': recall,
        'f1': 2 * precision * recall / (precision + recall) if precision + recall else 0.0,
        'reference_intervals': reference_intervals, 'candidate_intervals': candidate_intervals,
        'relative_interval_similarity': similarity, 'relative_interval_unavailable_reason': reason,
        'interpretation': 'Ataques simultâneos contam uma vez; alturas e durações não entram nesta métrica. Padrão relativo ignora deslocamento global e escala uniforme de tempo, não rubato.'
    }
