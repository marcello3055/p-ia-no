import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient
from services.api.main import create_app
from services.api.storage import Store
from services.api.training import register_analysis,sha
from packages.music.midi import write_midi
from test_evaluate import score

class TrainingJobsTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.store=Store(self.root)
        with self.store.connect() as db:
            for i in ['base','ref']:
                raw=i.encode();(self.store.files/(i+'.mp3')).write_bytes(raw)
                db.execute('INSERT INTO audio VALUES (?,?,?,?,?,?,?,?)',(i,i,i+'.mp3',sha(raw),len(raw),1.,'audio/mpeg','now'))
            db.execute('INSERT INTO pairs VALUES (?,?,?,?,?)',('pair','test','base','ref','now'))
        midi=write_midi(score([(72,0,1),(74,1,1)]))
        register_analysis(self.store,'pair',midi,midi,{'test_fixture':True})
        self.client=TestClient(create_app(self.root))
    def test_real_job_and_history(self):
        self.assertEqual(len(self.client.get('/api/training/pairs').json()['pairs']),1)
        r=self.client.post('/api/training/jobs',json={'pair_id':'pair','generations':1,'acknowledge_provisional':True})
        self.assertEqual(r.status_code,202);state=self.client.get('/api/training/jobs/'+r.json()['id']).json()
        self.assertEqual(state['state'],'completed');self.assertEqual(state['completed_generation'],1)
        self.assertEqual(self.client.get('/api/sessions/'+state['session_id']).json()['generation'],1)
        self.assertTrue((self.root/state['session_id']/'analysis-provenance.json').exists())
    def test_invalid_unacknowledged_and_changed_cache(self):
        for body in [{'pair_id':'pair'},{'pair_id':'pair','generations':4,'acknowledge_provisional':True}]:
            self.assertEqual(self.client.post('/api/training/jobs',json=body).status_code,422)
        p=self.root/'analyzed-pairs/pair/source.mid';p.write_bytes(b'changed')
        self.assertEqual(self.client.post('/api/training/jobs',json={'pair_id':'pair','acknowledge_provisional':True}).status_code,409)
        self.assertEqual(self.client.get('/api/training/pairs').json(),{'pairs':[]})
    def test_failure_and_restart_visible(self):
        with patch('services.api.training.run_session',side_effect=RuntimeError('private path')):
            r=self.client.post('/api/training/jobs',json={'pair_id':'pair','acknowledge_provisional':True})
        path=self.root/'training-jobs'/ (r.json()['id']+'.json')
        state=json.loads(path.read_text());self.assertEqual(state['state'],'failed');self.assertNotIn('private path',str(state))
        state['state']='running';path.write_text(json.dumps(state))
        self.assertEqual(self.client.get('/api/training/jobs/'+state['id']).json()['state'],'interrupted')
    def test_worker_lock(self):
        import fcntl
        with (self.root/'training-jobs/.worker.lock').open('a') as handle:
            fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
            self.assertEqual(self.client.post('/api/training/jobs',json={'pair_id':'pair','acknowledge_provisional':True}).status_code,409)
