import json
import tempfile
import unittest
from pathlib import Path
from packages.music.ranking import rank_population
from packages.music.population import initialize_population
from packages.music.session import run_session
from packages.music.midi import write_midi
from services.session_backup import export_session,restore_session
from test_evaluate import score

class ProfileTests(unittest.TestCase):
    def test_components_and_no_hard_guide_rejection(self):
        source=score([(48,0,1),(72,0,1),(50,1,1),(74,1,1)])
        r=rank_population(source,source,initialize_population(10),profile='clean-melody-v1')
        self.assertEqual(r['evaluated'],10)
        self.assertEqual(r['guide_note_count'],2)
        self.assertAlmostEqual(sum(r['weights'].values()),1)
        for row in r['results']:
            self.assertAlmostEqual(row['score'],sum(row['contributions'].values()))
            self.assertIn('cleanliness',row['criteria'])
            self.assertIn('melody_guide',row['criteria'])
    def test_empty_guide_is_explicit_and_does_not_invent_coverage(self):
        s=score([(72,0,.05)])
        r=rank_population(s,s,initialize_population(1),profile='clean-melody-v1')
        self.assertEqual(r['guide_note_count'],0)
        self.assertIsNone(r['results'][0]['criteria']['melody_guide'])
        self.assertEqual(r['results'][0]['contributions']['melody_guide'],0)
    def test_resume_profile_lock_and_backup(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);folder=root/'s';data=write_midi(score([(72,0,1)]))
            run_session(data,data,folder,0,ranking_profile='clean-melody-v1')
            run_session(data,data,folder,1,resume=True)
            saved=json.loads((folder/'generation-00001.json').read_text())['payload']['ranking']
            self.assertEqual(saved['ranking_profile'],'clean-melody-v1')
            with self.assertRaises(ValueError):run_session(data,data,folder,2,resume=True,ranking_profile='standard')
            (folder/'source.mid').write_bytes(data);(folder/'reference.mid').write_bytes(data)
            export_session(folder,folder/'source.mid',folder/'reference.mid',root/'s.zip')
            restore_session(root/'s.zip',root/'restored')
            self.assertEqual(run_session(data,data,folder,1,resume=True),run_session(data,data,root/'restored',1,resume=True))
