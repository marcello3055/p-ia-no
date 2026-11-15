import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient
from services.api.main import create_app
from packages.music.midi import write_midi
from test_evaluate import score

class MidiApiTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.client = TestClient(create_app(self.root))
        self.addCleanup(self.client.close)
        self.midi = write_midi(score([(60,0,1),(64,1,1)]))

    def compare(self, body=None, **params):
        return self.client.post('/api/midi/compare', params={'reference_bytes':len(self.midi),**params},
            content=self.midi*2 if body is None else body, headers={'Content-Type':'application/octet-stream'})

    def test_result_and_hashes_without_persistence(self):
        response = self.compare()
        self.assertEqual(response.status_code,200)
        result=response.json()
        self.assertEqual(result['pitch_and_onset']['f1'],1)
        self.assertEqual(result['sources']['reference_sha256'],hashlib.sha256(self.midi).hexdigest())
        self.assertEqual(self.client.get('/api/audio').json(),[])
        self.assertEqual(list((self.root/'audio').iterdir()),[])

    def test_changed_notes_and_parameters(self):
        other=write_midi(score([(60,0,1),(65,1,1)]))
        result=self.compare(self.midi+other,time_unit='seconds',onset_tolerance=.05).json()
        self.assertEqual(result['pitch_and_onset']['recall'],.5)
        self.assertEqual(result['config']['onset_tolerance'],.05)
        self.assertEqual(result['config']['time_unit'],'seconds')

    def test_invalid_midi_and_empty_second_file(self):
        self.assertEqual(self.compare(self.midi+b'broken').status_code,422)
        self.assertEqual(self.compare(self.midi).status_code,422)
        empty=write_midi(score([]))
        self.assertEqual(self.compare(empty+self.midi,reference_bytes=len(empty)).status_code,422)

    def test_invalid_config_and_reference_length(self):
        for params in [{'reference_bytes':0},{'reference_bytes':5*1024**2+1},
                       {'time_unit':'ticks'},{'duration_relative':2},{'onset_tolerance':-1}]:
            with self.subTest(params=params): self.assertEqual(self.compare(**params).status_code,422)

    def test_wrong_media_type_and_declared_oversize(self):
        self.assertEqual(self.client.post('/api/midi/compare?reference_bytes=1',json={}).status_code,415)
        response=self.client.post('/api/midi/compare?reference_bytes=1',content=b'a',
            headers={'Content-Type':'application/octet-stream','Content-Length':str(11*1024**2)})
        self.assertEqual(response.status_code,413)

    def test_streaming_oversize_without_content_length(self):
        with patch('services.api.midi_compare.MAX_BODY',10):
            response=self.client.post('/api/midi/compare?reference_bytes=1',content=iter([b'a'*8,b'b'*8]),
                headers={'Content-Type':'application/octet-stream'})
        self.assertEqual(response.status_code,413)
