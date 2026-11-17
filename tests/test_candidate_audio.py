import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from packages.music.midi import write_midi
from packages.music.session import run_session
from services.api.main import create_app
from test_evaluate import score

class CandidateAudioTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.folder=self.root/'session'
        source=write_midi(score([(p,0,1) for p in [36,48,60,64,67,84]]))
        reference=write_midi(score([(36,0,1),(84,0,1)]))
        run_session(source,reference,self.folder,0)
        (self.folder/'source.mid').write_bytes(source)
        ranking=json.loads((self.folder/'generation-00000.json').read_text())['payload']['ranking']
        self.id=ranking['ranking'][0]
        self.expected=next(r['midi_sha256'] for r in ranking['results'] if r['id']==self.id)
        self.client=TestClient(create_app(self.root))
        self.url=f'/api/sessions/session/generations/0/candidates/{self.id}/audio'

    def test_real_mp3_verified_input_cache_and_unchanged_checkpoint(self):
        import subprocess
        from packages.music.render import render_piano
        before=(self.folder/'generation-00000.json').read_bytes()
        with patch('services.api.candidate_audio.render_piano',wraps=render_piano) as renderer:
            response=self.client.post(self.url)
            self.assertEqual(response.status_code,200,response.text[:100] if response.status_code!=200 else '')
            self.assertEqual(response.headers['x-piano-midi-sha256'],self.expected)
            self.assertEqual(response.headers['content-type'],'audio/mpeg')
            again=self.client.post(self.url);self.assertEqual(again.content,response.content)
            self.assertEqual(again.headers['x-piano-cache'],'hit');self.assertEqual(renderer.call_count,1)
        path=self.root/'result.mp3';path.write_bytes(response.content)
        subprocess.run(['ffmpeg','-v','error','-i',str(path),'-f','null','-'],check=True,capture_output=True)
        self.assertEqual(before,(self.folder/'generation-00000.json').read_bytes())
        (self.folder/'source.mid').write_bytes(b'wrong')
        self.assertEqual(self.client.post(self.url).status_code,409)

    def test_missing_candidate_and_renderer(self):
        self.assertEqual(self.client.post(self.url.replace(self.id,'candidate-'+'0'*16)).status_code,404)
        with patch('services.api.candidate_audio.render_piano',side_effect=RuntimeError('missing')):
            self.assertEqual(self.client.post(self.url).status_code,503)

    def test_concurrent_request_rejected(self):
        import threading
        entered=threading.Event();release=threading.Event()
        def blocked(*args):
            entered.set();release.wait(5);raise RuntimeError('test')
        with patch('services.api.candidate_audio.render_piano',side_effect=blocked):
            worker=threading.Thread(target=lambda:self.client.post(self.url));worker.start()
            try:
                self.assertTrue(entered.wait(5))
                self.assertEqual(self.client.post(self.url).status_code,503)
            finally:release.set();worker.join(5)
