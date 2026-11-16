import fcntl
import json
from pathlib import Path
import tempfile
import unittest
from fastapi.testclient import TestClient
from services.api.main import create_app
from packages.music.session import run_session
from packages.music.midi import write_midi
from test_evaluate import score

class SessionApiTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name); self.folder=self.root/'test-session'
        self.client=TestClient(create_app(self.root))
        self.data=write_midi(score([(36,0,1),(84,0,1)]))

    def seed(self): run_session(self.data,self.data,self.folder,1)

    def test_empty_and_missing(self):
        self.assertEqual(self.client.get('/api/sessions').json(),{'sessions':[]})
        self.assertEqual(self.client.get('/api/sessions/missing').status_code,404)

    def test_real_history_readonly_and_busy(self):
        self.seed()
        before={p.name:p.read_bytes() for p in self.folder.glob('*.json')}
        response=self.client.get('/api/sessions/test-session'); self.assertEqual(response.status_code,200)
        data=response.json(); self.assertEqual(data['generation'],1)
        self.assertEqual(data['history'][0]['evaluated'],100)
        self.assertEqual(data['state'],'idle')
        self.assertNotIn('source_sha256',data)
        self.assertEqual(before,{p.name:p.read_bytes() for p in self.folder.glob('*.json')})
        with (self.folder/'.lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            self.assertEqual(self.client.get('/api/sessions/test-session').json()['state'],'busy')

    def test_corruption_is_error(self):
        self.seed(); path=self.folder/'generation-00001.json'
        value=json.loads(path.read_text()); value['payload']['ranking']['best_score']=.123
        path.write_text(json.dumps(value))
        self.assertEqual(self.client.get('/api/sessions/test-session').status_code,409)

    def test_symlink_and_invalid_id(self):
        self.seed(); (self.root/'alias').symlink_to(self.folder,target_is_directory=True)
        self.assertEqual(self.client.get('/api/sessions').json()['sessions'],[{'id':'test-session'}])
        self.assertEqual(self.client.get('/api/sessions/alias').status_code,404)
        self.assertEqual(self.client.get('/api/sessions/.lock').status_code,404)

    def test_limit_and_incomplete_session(self):
        self.seed()
        from unittest.mock import patch
        with patch('services.api.sessions.MAX_GENERATIONS',1):
            self.assertEqual(self.client.get('/api/sessions/test-session').status_code,409)
        (self.folder/'generation-00001.json').unlink()
        (self.folder/'generation-00000.json').unlink()
        data=self.client.get('/api/sessions/test-session').json()
        self.assertEqual(data['history'],[]); self.assertIsNone(data['generation'])

    def test_candidate_criteria_match_saved_values(self):
        self.seed()
        checkpoint=json.loads((self.folder/'generation-00001.json').read_text())['payload']
        response=self.client.get('/api/sessions/test-session/generations/1')
        self.assertEqual(response.status_code,200)
        data=response.json(); self.assertEqual(len(data['candidates']),10)
        self.assertEqual(data['weights'],checkpoint['ranking']['weights'])
        saved={r['id']:r for r in checkpoint['ranking']['results']}
        self.assertEqual([r['id'] for r in data['candidates']],checkpoint['ranking']['ranking'][:10])
        for candidate in data['candidates']:
            self.assertEqual(candidate['criteria'],saved[candidate['id']]['criteria'])
            self.assertAlmostEqual(sum(candidate['contributions'].values()),candidate['score'])
        self.assertEqual(data['best_tie_count'],len(checkpoint['ranking']['best_candidate_ids']))

    def test_candidate_missing_and_corrupt(self):
        self.seed()
        for generation in [-1,2,201]:
            self.assertEqual(self.client.get(f'/api/sessions/test-session/generations/{generation}').status_code,404)
        (self.folder/'generation-00000.json').write_text('{}')
        self.assertEqual(self.client.get('/api/sessions/test-session/generations/1').status_code,409)
