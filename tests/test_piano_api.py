import base64
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from packages.music.midi import write_midi,read_midi
from services.api.main import create_app
from test_evaluate import score

class PianoApiTests(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory()
        self.client=TestClient(create_app(Path(self.folder.name)))
    def tearDown(self):
        self.client.close(); self.folder.cleanup()
    def post(self,data):
        return self.client.post('/api/experimental/piano',content=data,headers={'Content-Type':'application/octet-stream'})
    def test_real_generation_files_and_no_library_persistence(self):
        r=self.post(write_midi(score([(48,0,1),(60,0,1),(64,0,1),(67,0,1),(72,0,1)])))
        self.assertEqual(r.status_code,200,r.text[:200])
        body=r.json(); files={f['name']:base64.b64decode(f['base64']) for f in body['files']}
        self.assertEqual(set(files),{'piano.mid','piano.wav','piano.mp3'})
        self.assertEqual(len(read_midi(files['piano.mid']).notes),4)
        self.assertEqual(files['piano.wav'][:4],b'RIFF')
        self.assertGreater(len(files['piano.mp3']),1000)
        self.assertEqual(body['report']['rendering']['notes'],4)
        self.assertFalse(list(Path(self.folder.name).rglob('*.mp3')))
    def test_bad_type_invalid_empty_and_oversize(self):
        self.assertEqual(self.client.post('/api/experimental/piano',content=b'bad').status_code,415)
        for data in (b'',b'not midi'):
            self.assertEqual(self.post(data).status_code,422)
        self.assertEqual(self.post(b'x'*(5*1024**2+1)).status_code,413)
    def test_long_input_and_missing_renderer(self):
        self.assertEqual(self.post(write_midi(score([(60,0,250)]))).status_code,422)
        with patch('services.api.piano.render_piano',side_effect=RuntimeError('missing')):
            self.assertEqual(self.post(write_midi(score([(60,0,1)]))).status_code,503)
