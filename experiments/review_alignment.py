"""Independent cached-note checks and a short, unwarped listening comparison.
Scores are diagnostic, not a validated evaluator or permission to train.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import wave
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np


def profile(notes, times):
    result = np.zeros((len(times), 12))
    for n in notes:
        mask = (times >= n['start_seconds']) & (times < n['end_seconds'])
        result[mask, n['pitch'] % 12] += n['activation']
    return result


def compare(notes, reference, mapping, start, end, reference_start):
    """Sample note-derived pitch classes; retain silence as missing evidence."""
    times = np.arange(start, end, .05)
    mapping = np.asarray(mapping)
    target = np.interp(times, mapping[:, 0], mapping[:, 1]) - reference_start
    source_profile, target_profile = profile(notes, times), profile(reference, target)
    norms = np.linalg.norm(source_profile, axis=1) * np.linalg.norm(target_profile, axis=1)
    active = norms > 0
    similarity = np.sum(source_profile * target_profile, axis=1)[active] / norms[active]
    attacks = [n for n in notes if start <= n['start_seconds'] < end]
    hits = 0
    for n in attacks:
        t = np.interp(n['start_seconds'], mapping[:, 0], mapping[:, 1]) - reference_start
        hits += any(r['pitch'] % 12 == n['pitch'] % 12 and abs(r['start_seconds'] - t) <= .2 for r in reference)
    return {'note_chroma_cosine': float(similarity.mean()) if active.any() else None,
            'active_sample_fraction': float(active.mean()), 'source_attacks': len(attacks),
            'same_pitch_class_attack_hits_within_200ms': hits,
            'attack_hit_fraction': hits / len(attacks) if attacks else None}


def listening(pair, sections, output):
    """Original PCM snippets, no stretching, normalization or pitch changes."""
    chunks = []; timeline = []; cursor = 0.; params = None
    for role, start, end, label in sections:
        with wave.open(str(pair / role / 'clip.wav'), 'rb') as w:
            current = (w.getnchannels(), w.getsampwidth(), w.getframerate())
            if params is not None and params != current: raise ValueError('Incompatible WAV formats')
            params = current
            if not 0 <= start < end <= w.getnframes()/w.getframerate(): raise ValueError('Invalid clip bounds')
            first, last = round(start*params[2]), round(end*params[2])
            w.setpos(first); chunks.append(w.readframes(last-first))
            length = (last-first)/params[2]
        timeline.append({'label':label, 'starts_in_comparison':cursor, 'ends_in_comparison':cursor+length})
        chunks.append(bytes(params[0]*params[1]*params[2])); cursor += length+1
    with wave.open(str(output), 'wb') as w:
        w.setnchannels(params[0]); w.setsampwidth(params[1]); w.setframerate(params[2]); w.writeframes(b''.join(chunks))
    return timeline


def main():
    p=argparse.ArgumentParser();p.add_argument('--pair',type=Path,required=True);p.add_argument('--source-analysis',type=Path,required=True)
    p.add_argument('--proposed',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists(): raise ValueError('Output already exists')
    originals=json.loads((a.pair/'alignment.json').read_text()); proposed=json.loads(a.proposed.read_text())
    regions=originals['human_regions']
    if proposed['human_regions'] != regions: raise ValueError('Different regions')
    metadata={role:json.loads((a.pair/role/'clip.json').read_text()) for role in ('source','reference')}
    for role,meta in metadata.items():
        if hashlib.sha256((a.pair/role/'clip.wav').read_bytes()).hexdigest()!=meta['clip_sha256']: raise ValueError('Clip hash mismatch')
    source_report=json.loads(a.source_analysis.read_text())
    if source_report['clip']['clip_sha256']!=metadata['source']['clip_sha256']: raise ValueError('Wrong source transcription')
    notes=source_report['estimates']; reference_path=a.pair/'comparison/reference-estimates.json'
    reference=json.loads(reference_path.read_text())
    maps={'previous':originals['mapping_query_to_target_seconds'],'bounded':proposed['mapping_query_to_target_seconds']}
    windows=[]
    for start,end in [(0,25.5),(12,15),(15,18),(18,21),(21,24)]:
        windows.append({'source_absolute_seconds':[regions['source_start']+start,regions['source_start']+end],
                        'comparisons':{key:compare(notes,reference,m,start,end,regions['reference_start']) for key,m in maps.items()}})
    a.output.mkdir(parents=True)
    sections=[('source',15,21,'OST 39,5–45,5 s')]
    for key,m in maps.items():
        m=np.array(m);lo,hi=np.interp([15,21],m[:,0],m[:,1]);sections.append(('reference',lo-20,hi-20,f'{key}: piano {lo:.3f}–{hi:.3f} s'))
    timeline=listening(a.pair,sections,a.output/'comparison.wav')
    subprocess.run(['ffmpeg','-v','error','-nostdin','-i',str(a.output/'comparison.wav'),'-codec:a','libmp3lame','-b:a','128k',str(a.output/'comparison.mp3')],check=True)
    inputs=[a.pair/'alignment.json',a.proposed,a.source_analysis,reference_path]
    report={'status':'independent_note_diagnostic_requires_listening','training_allowed':False,
            'method':'50 ms samples of activation-weighted pitch-class profiles; same-class source attack matches within 200 ms',
            'limitations':['Transcriptions are uncertain and share the same model; not ground truth.',
                          'Pitch classes ignore octave, voice identity and ordering inside chords.',
                          'Attack hits permit many-to-one matches; not note precision or recall.',
                          'Reference estimates have no original clip provenance manifest; input hash recorded, pairing relies on existing experiment directory.',
                          'No subjective listening performed by this script; no automatic musical approval.'],
            'inputs_sha256':{str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in inputs},
            'windows':windows,'listening_order':timeline}
    (a.output/'review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False))


if __name__=='__main__': main()
