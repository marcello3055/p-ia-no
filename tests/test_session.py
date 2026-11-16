import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from packages.music.midi import write_midi
from packages.music.session import run_session, atomic_json
from test_evaluate import score


class SessionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = write_midi(score([(p, 0, 1) for p in [36,48,60,64,67,72,84]]))
        self.reference = write_midi(score([(36,0,1),(84,0,1)]))

    def run_at(self, name, generation, **kwargs):
        return run_session(self.source, self.reference, self.root/name, generation, **kwargs)

    def test_resume_identical_to_continuous_and_no_recompute(self):
        full = self.run_at('full', 3)
        self.run_at('split', 1)
        split = self.run_at('split', 3, resume=True)
        self.assertEqual(full, split)
        for path in (self.root/'full').glob('generation-*.json'):
            self.assertEqual(path.read_bytes(), (self.root/'split'/path.name).read_bytes())
        with patch('packages.music.session.rank_population', side_effect=AssertionError('recomputed')):
            self.assertEqual(split, self.run_at('split', 3, resume=True))

    def test_interruption_preserves_complete_checkpoint(self):
        self.run_at('split', 0)
        with patch('packages.music.session.atomic_json', side_effect=OSError('interrupted')):
            with self.assertRaises(OSError): self.run_at('split', 1, resume=True)
        self.assertEqual(len(list((self.root/'split').glob('generation-*.json'))), 1)
        self.assertEqual(self.run_at('split', 2, resume=True), self.run_at('full', 2))

    def test_corruption_and_missing_generation_rejected(self):
        self.run_at('bad', 1)
        path = self.root/'bad'/'generation-00001.json'
        value = json.loads(path.read_text()); value['payload']['ranking']['best_score'] = -1
        path.write_text(json.dumps(value))
        with self.assertRaises(ValueError): self.run_at('bad', 2, resume=True)
        (self.root/'bad'/'generation-00000.json').unlink()
        with self.assertRaises(ValueError): self.run_at('bad', 2, resume=True)

    def test_inputs_overwrite_limits_and_seed(self):
        self.run_at('run', 1)
        with self.assertRaises(FileExistsError): self.run_at('run', 1)
        with self.assertRaises(ValueError): self.run_at('run', 2, resume=True, seed=1)
        with self.assertRaises(ValueError):
            run_session(self.reference, self.reference, self.root/'run', 2, resume=True)
        for generation in [-1, True, 101]:
            with self.assertRaises(ValueError): self.run_at('new', generation)
        with self.assertRaises(ValueError): self.run_at('run', 0, resume=True)

    def test_atomic_failure_leaves_original(self):
        path = self.root/'checkpoint.json'; atomic_json(path, {'old':True})
        with patch('packages.music.session.os.replace', side_effect=OSError('disk error')):
            with self.assertRaises(OSError): atomic_json(path, {'new':True})
        self.assertEqual(json.loads(path.read_text()), {'old':True})
        self.assertEqual(list(self.root.glob('.pending-*')), [])

    def test_concurrent_session_rejected(self):
        import fcntl
        self.run_at('locked', 0)
        with (self.root/'locked'/'.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            with self.assertRaises(ValueError): self.run_at('locked', 1, resume=True)
