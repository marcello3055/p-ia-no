import unittest
from experiments.melody_guide import upper_voice, guarded
from packages.music.evaluate import evaluate
from test_evaluate import score

class MelodyGuideTests(unittest.TestCase):
    def test_accompaniment_can_be_removed_but_upper_melody_cannot(self):
        ref=score([(72,0,1),(74,1,1),(48,0,1),(52,1,1)])
        guide=upper_voice(ref)['reference_indices']
        self.assertEqual(guide,[0,1])
        baseline=evaluate(ref,ref)
        self.assertTrue(guarded(evaluate(ref,score([(72,0,1),(74,1,1)])),guide,baseline)['eligible'])
        self.assertFalse(guarded(evaluate(ref,score([(72,0,1),(48,0,1),(52,1,1)])),guide,baseline)['eligible'])
    def test_low_arpeggios_and_short_high_spike_do_not_replace_sustained_voice(self):
        ref=score([(72,0,4),(48,0,1),(52,1,1),(55,2,1),(96,1,.1)])
        self.assertEqual(upper_voice(ref)['reference_indices'],[0])
    def test_empty_and_uncovered_guide_never_pass_vacuously(self):
        self.assertEqual(upper_voice(score([]))['reference_indices'],[])
        ref=score([(72,0,1)]);empty=evaluate(ref,score([]))
        self.assertFalse(guarded(empty,[],empty)['eligible'])
        self.assertFalse(guarded(evaluate(ref,ref),[0],empty)['eligible'])
    def test_octave_and_silence_fail_preservation(self):
        ref=score([(72,0,1)]);baseline=evaluate(ref,ref)
        for notes in ([],[(60,0,1)]):
            self.assertFalse(guarded(evaluate(ref,score(notes)),[0],baseline)['eligible'])
    def test_inner_voice_limitation_is_explicit(self):
        # If the actual melody is 60 and sustained accompaniment is 84,
        # the heuristic picks 84. This fixture documents a known failure.
        self.assertEqual(upper_voice(score([(60,0,1),(84,0,1)]))['reference_indices'],[1])
    def test_threshold_validation(self):
        for duration,exposure in [(0,.5),(-1,.5),(float('nan'),.5),(.12,0),(.12,2)]:
            with self.assertRaises(ValueError):upper_voice(score([]),duration,exposure)
