from dataclasses import replace
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import mido
from packages.music.evaluate import EvaluationConfig, evaluate
from packages.music.midi import Note, Event, Score, write_midi

def score(values, resolution=1000, tempo=500000):
    # Each tuple: pitch, start in quarter notes, duration in quarter notes.
    notes = [Note(i, 0, pitch, 80, 0, round(start*resolution), round((start+duration)*resolution), 1, 2)
             for i, (pitch, start, duration) in enumerate(values)]
    return Score(resolution, 1, [n.end_tick for n in notes] or [0], notes,
                 [Event(0, 0, 0, True, {'type': 'set_tempo', 'tempo': tempo})], [])

class EvaluationTests(unittest.TestCase):
    def test_identical(self):
        result = evaluate(score([(60,0,1),(64,0,1)]), score([(60,0,1),(64,0,1)]))
        self.assertEqual(result['pitch_onset_and_duration']['f1'], 1)
        self.assertEqual(result['matched_errors']['onset_mae'], 0)

    def test_missing_extra_wrong_pitch(self):
        result = evaluate(score([(60,0,1),(62,1,1)]), score([(60,0,1),(65,1,1),(67,2,1)]))
        self.assertEqual(result['pitch_and_onset']['precision'], 1/3)
        self.assertEqual(result['pitch_and_onset']['recall'], .5)
        self.assertEqual(result['unmatched_reference_indices'], [1])
        self.assertEqual(result['unmatched_candidate_indices'], [1,2])

    def test_candidate_duplicate_cannot_reuse_reference(self):
        result = evaluate(score([(60,0,1)]), score([(60,0,1),(60,0,1)]))
        self.assertEqual(result['counts']['matched_pitch_onset'], 1)
        self.assertEqual(result['pitch_and_onset']['precision'], .5)

    def test_chronological_matching_avoids_nearest_neighbor_trap(self):
        result = evaluate(score([(60,0,.01),(60,.08,.01)]), score([(60,.05,.01),(60,.12,.01)]),
                          EvaluationConfig(onset_tolerance=.06))
        self.assertEqual(result['counts']['matched_pitch_onset'], 2)
        self.assertEqual([r['candidate_index'] for r in result['matches']], [0,1])

    def test_boundary_and_delayed_notes(self):
        reference = score([(60,0,1)])
        self.assertEqual(evaluate(reference, score([(60,.1,1)]))['counts']['matched_pitch_onset'], 1)
        delayed = evaluate(reference, score([(60,.101,1)]))
        self.assertEqual(delayed['pitch_and_onset']['f1'], 0)
        self.assertEqual(delayed['pitch_inventory_only']['f1'], 1)
        self.assertIsNone(delayed['matched_errors']['onset_mae'])

    def test_duration_error_does_not_hide_good_onset(self):
        result = evaluate(score([(60,0,1)]), score([(60,0,2)]))
        self.assertEqual(result['pitch_and_onset']['f1'], 1)
        self.assertEqual(result['pitch_onset_and_duration']['f1'], 0)
        self.assertEqual(result['matched_errors']['duration_mae'], 1)

    def test_tempo_and_resolution_are_distinguished(self):
        reference = score([(60,1,1)], resolution=480)
        candidate = score([(60,1,1)], resolution=960, tempo=1000000)
        self.assertEqual(evaluate(reference,candidate)['pitch_onset_and_duration']['f1'],1)
        self.assertEqual(evaluate(reference,candidate,EvaluationConfig(time_unit='seconds'))['pitch_and_onset']['f1'],0)

    def test_empty_candidate_and_empty_reference(self):
        result = evaluate(score([(60,0,1)]), score([]))
        self.assertEqual(result['pitch_and_onset']['f1'], 0)
        self.assertIsNone(result['matched_errors']['duration_match_rate'])
        with self.assertRaises(ValueError): evaluate(score([]), score([]))

    def test_invalid_tolerances(self):
        for value in [-1, float('nan'), float('inf')]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                evaluate(score([(60,0,1)]), score([]), EvaluationConfig(onset_tolerance=value))

    def test_percussion_excluded_and_tracks_ignored(self):
        reference = score([(60,0,1),(35,0,1)])
        reference.notes[1] = replace(reference.notes[1], channel=9)
        result = evaluate(reference, score([(60,0,1)]))
        self.assertEqual(result['counts']['excluded_reference'],1)
        self.assertEqual(result['pitch_and_onset']['recall'],1)
        self.assertEqual(evaluate(reference,score([(60,0,1)]),EvaluationConfig(include_percussion=True))['pitch_and_onset']['recall'],.5)

    def test_cli_report_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            midi, report = root/'a.mid', root/'report.json'
            midi.write_bytes(write_midi(score([(60,0,1)])))
            cmd=[sys.executable,'scripts/compare_midi.py',str(midi),str(midi),'--output',str(report)]
            run=subprocess.run(cmd,capture_output=True)
            self.assertEqual(run.returncode,0,run.stderr)
            self.assertEqual(json.loads(report.read_text())['pitch_and_onset']['f1'],1)
            original=report.read_bytes()
            self.assertNotEqual(subprocess.run(cmd,capture_output=True).returncode,0)
            self.assertEqual(report.read_bytes(),original)
