import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from packages.music.midi import write_midi
from packages.music.session import run_session, digest
from services.api.main import create_app
from services.candidate_recovery import recover_candidate
from test_evaluate import score

class CandidateRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.folder=self.root/'session'
        self.source=write_midi(score([(p,0,1) for p in [36,48,60,67,84]]))
        reference=write_midi(score([(36,0,1),(84,0,1)]))
        run_session(self.source,reference,self.folder,0)
        (self.folder/'source.mid').write_bytes(self.source)
        self.path=self.folder/'generation-00000.json'
        self.envelope=json.loads(self.path.read_text())
        ranking=self.envelope['payload']['ranking']
        self.candidate=ranking['ranking'][0]
        self.result=next(r for r in ranking['results'] if r['id']==self.candidate)
        self.client=TestClient(create_app(self.root))
        self.url=f'/api/sessions/session/generations/0/candidates/{self.candidate}/midi'

    def test_exact_bytes_without_evaluation_or_mutation(self):
        before=self.path.read_bytes()
        with patch('packages.music.ranking.rank_population',side_effect=AssertionError('reranking')):
            data=recover_candidate(self.folder,0,self.candidate)
        self.assertEqual(hashlib.sha256(data).hexdigest(),self.result['midi_sha256'])
        self.assertEqual(before,self.path.read_bytes())
        response=self.client.get(self.url)
        self.assertEqual(response.status_code,200);self.assertEqual(response.content,data)
        self.assertEqual(response.headers['content-type'],'audio/midi')

    def test_wrong_missing_and_symlink_source(self):
        path=self.folder/'source.mid';path.write_bytes(b'wrong')
        self.assertEqual(self.client.get(self.url).status_code,409)
        path.unlink();self.assertEqual(self.client.get(self.url).status_code,409)
        target=self.root/'source.mid';target.write_bytes(self.source);path.symlink_to(target)
        self.assertEqual(self.client.get(self.url).status_code,409)

    def test_unknown_candidate_and_generation(self):
        self.assertEqual(self.client.get(self.url.replace(self.candidate,'candidate-'+'0'*16)).status_code,404)
        self.assertEqual(self.client.get(self.url.replace('/generations/0/','/generations/9/')).status_code,404)

    def test_mismatching_reconstructed_output(self):
        row=next(r for r in self.envelope['payload']['ranking']['results'] if r['id']==self.candidate)
        row['midi_sha256']='0'*64
        self.envelope['sha256']=digest(self.envelope['payload']);self.path.write_text(json.dumps(self.envelope))
        self.assertEqual(self.client.get(self.url).status_code,409)

    def test_changed_code_refused(self):
        with patch('services.candidate_recovery.current_code_hashes',return_value={}):
            with self.assertRaisesRegex(ValueError,'código musical'):recover_candidate(self.folder,0,self.candidate)
