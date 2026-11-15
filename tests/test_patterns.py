import unittest
from packages.music.evaluate import evaluate, EvaluationConfig
from test_evaluate import score

class PatternTests(unittest.TestCase):
    def test_octave_change_preserves_pitch_class_but_not_exact_notes(self):
        r=evaluate(score([(60,0,1),(64,1,1)]),score([(72,0,1),(76,1,1)]))
        self.assertEqual(r['pitch_and_onset']['f1'],0)
        self.assertEqual(r['pitch_class_diagnostics']['global_distribution_overlap'],1)
        self.assertEqual(r['pitch_class_diagnostics']['temporal_pitch_class_jaccard'],1)

    def test_same_global_distribution_different_order(self):
        r=evaluate(score([(60,0,1),(64,1,1)]),score([(64,0,1),(60,1,1)]))['pitch_class_diagnostics']
        self.assertEqual(r['global_distribution_overlap'],1)
        self.assertEqual(r['temporal_pitch_class_jaccard'],0)

    def test_partial_chord_and_shared_silence(self):
        r=evaluate(score([(60,100,1),(64,100,1),(67,100,1)]),score([(60,100,1),(65,100,1),(69,100,1)]))['pitch_class_diagnostics']
        self.assertAlmostEqual(r['global_distribution_overlap'],1/3)
        self.assertAlmostEqual(r['temporal_pitch_class_jaccard'],1/5)

    def test_chord_density_does_not_multiply_attacks_or_temporal_classes(self):
        r=evaluate(score([(60,0,1)]),score([(60,0,1),(72,0,1)]))
        self.assertEqual(r['rhythm_diagnostics']['candidate_attack_count'],1)
        self.assertEqual(r['rhythm_diagnostics']['f1'],1)
        self.assertEqual(r['pitch_class_diagnostics']['temporal_pitch_class_jaccard'],1)

    def test_shift_and_scale_preserve_relative_pattern_only(self):
        r=evaluate(score([(60,0,.1),(60,1,.1),(60,3,.1)]),score([(70,10,.1),(70,12,.1),(70,16,.1)]))['rhythm_diagnostics']
        self.assertEqual(r['f1'],0)
        self.assertEqual(r['relative_interval_similarity'],1)

    def test_rhythm_change(self):
        r=evaluate(score([(60,0,.1),(60,1,.1),(60,3,.1)]),score([(60,0,.1),(60,2,.1),(60,3,.1)]))['rhythm_diagnostics']
        self.assertAlmostEqual(r['relative_interval_similarity'],2/3)
        self.assertAlmostEqual(r['f1'],2/3)

    def test_undefined_short_pattern_and_unequal_count(self):
        for candidate in [[(60,0,1)],[(60,0,.1),(60,1,.1),(60,2,.1),(60,3,.1)]]:
            r=evaluate(score([(60,0,.1),(60,1,.1),(60,2,.1)]),score(candidate))['rhythm_diagnostics']
            self.assertIsNone(r['relative_interval_similarity'])
            self.assertTrue(r['relative_interval_unavailable_reason'])

    def test_no_duration_and_empty_candidate(self):
        r=evaluate(score([(60,0,0)]),score([]))
        self.assertIsNone(r['pitch_class_diagnostics']['global_distribution_overlap'])
        self.assertIsNone(r['pitch_class_diagnostics']['temporal_pitch_class_jaccard'])
        self.assertEqual(r['rhythm_diagnostics']['f1'],0)
        r=evaluate(score([(60,0,1)]),score([]))['pitch_class_diagnostics']
        self.assertEqual(r['global_distribution_overlap'],0)
        self.assertEqual(r['temporal_pitch_class_jaccard'],0)

    def test_seconds_versus_quarters(self):
        a=score([(60,0,.5),(64,1,.5),(67,2,.5)])
        b=score([(60,0,.5),(64,1,.5),(67,2,.5)],tempo=1000000)
        self.assertEqual(evaluate(a,b)['pitch_class_diagnostics']['temporal_pitch_class_jaccard'],1)
        seconds=evaluate(a,b,EvaluationConfig(time_unit='seconds'))
        self.assertLess(seconds['pitch_class_diagnostics']['temporal_pitch_class_jaccard'],1)
        self.assertEqual(seconds['rhythm_diagnostics']['relative_interval_similarity'],1)
