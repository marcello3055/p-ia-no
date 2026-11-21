import unittest
from experiments.cleanliness_review import assess
from packages.music.evaluate import evaluate
from test_evaluate import score

class CleanlinessReviewTests(unittest.TestCase):
    def test_extra_notes_penalized_without_rewarding_lost_reference_notes(self):
        ref=score([(60,0,1),(64,1,2)])
        clean=evaluate(ref,ref)
        noisy=evaluate(ref,score([(60,0,1),(64,1,2),(80,0,1)]))
        partial=evaluate(ref,score([(60,0,1)]))
        protected={m['reference_index'] for m in clean['matches']}
        self.assertGreater(assess(clean,protected)['f_beta'],assess(noisy,protected)['f_beta'])
        self.assertTrue(assess(clean,protected)['eligible'])
        self.assertFalse(assess(partial,protected)['eligible'])
        self.assertFalse(assess(evaluate(ref,score([])),protected)['eligible'])
        self.assertFalse(assess(evaluate(ref,score([])),set())['eligible'])
    def test_octave_change_is_not_claimed_to_preserve_notes(self):
        ref=score([(60,0,1)])
        self.assertFalse(assess(evaluate(ref,score([(72,0,1)])),{0})['eligible'])
    def test_invalid_beta(self):
        for beta in (0,-1,float('nan'),float('inf')):
            with self.assertRaises(ValueError):assess({},set(),beta)
