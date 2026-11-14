import io
import tempfile
import unittest
import wave
from pathlib import Path
from fastapi.testclient import TestClient
from services.api.main import create_app

def wav_bytes(value=0):
    output = io.BytesIO()
    with wave.open(output, 'wb') as wav:
        wav.setparams((1, 2, 8000, 0, 'NONE', 'not compressed'))
        wav.writeframes(value.to_bytes(2, 'little', signed=True) * 8000)
    return output.getvalue()

class StorageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.client = TestClient(create_app(self.root))
        self.addCleanup(self.client.close)

    def upload(self, body=None, name='example.wav', client=None):
        return (client or self.client).post('/api/audio', params={'filename': name},
                    content=wav_bytes() if body is None else body,
                    headers={'Content-Type': 'application/octet-stream'})

    def test_saved_pair_and_audio_survive_new_app_and_support_seek(self):
        base = self.upload().json()
        piano = self.upload(wav_bytes(10), 'piano.wav').json()
        payload = {'name': 'Example pair', 'base_id': base['id'], 'reference_id': piano['id']}
        pair = self.client.post('/api/pairs', json=payload)
        self.assertEqual(pair.status_code, 200)
        self.assertEqual(self.client.post('/api/pairs', json=payload).json()['id'], pair.json()['id'])
        with TestClient(create_app(self.root)) as reopened:
            self.assertEqual(len(reopened.get('/api/pairs').json()), 1)
            self.assertEqual(len(reopened.get('/api/audio').json()), 2)
            response = reopened.get(f"/api/audio/{base['id']}/content")
            self.assertEqual(response.content, wav_bytes())
            seek = reopened.get(f"/api/audio/{base['id']}/content", headers={'Range': 'bytes=0-43'})
            self.assertEqual(seek.status_code, 206)
            self.assertEqual(seek.content, wav_bytes()[:44])

    def test_duplicate_audio_reuses_identity(self):
        first = self.upload().json()
        second = self.upload(name='renamed.wav').json()
        self.assertEqual(first['id'], second['id'])
        self.assertEqual(len(self.client.get('/api/audio').json()), 1)
        self.assertEqual(self.upload(name='renamed.mp3').status_code, 422)

    def test_corrupt_empty_wrong_extension_and_traversal_leave_no_files(self):
        for body, name, status in [(b'bad', 'bad.wav', 422), (b'', 'empty.wav', 413),
                                   (wav_bytes(), 'x.txt', 415), (wav_bytes(), '../x.wav', 422),
                                   (wav_bytes(), 'fake.mp3', 422)]:
            with self.subTest(name=name):
                self.assertEqual(self.upload(body, name).status_code, status)
        self.assertEqual(list((self.root / 'audio').iterdir()), [])
        self.assertEqual(self.client.get('/api/audio').json(), [])

    def test_streaming_limit_and_quota_clean_partial_files(self):
        for kwargs, status in [({'max_bytes': 10}, 413), ({'quota_bytes': 10}, 507)]:
            with TestClient(create_app(self.root, **kwargs)) as client:
                response = client.post('/api/audio?filename=test.wav',
                    content=iter([b'a' * 8, b'b' * 8]), headers={'Content-Type': 'application/octet-stream'})
                self.assertEqual(response.status_code, status)
            self.assertEqual(list((self.root / 'audio').iterdir()), [])

    def test_missing_audio_and_bad_pair_are_rejected(self):
        self.assertEqual(self.client.get('/api/audio/unknown/content').status_code, 404)
        payload = {'name': 'Test', 'base_id': 'missing', 'reference_id': 'missing'}
        self.assertEqual(self.client.post('/api/pairs', json=payload).status_code, 404)
        payload['name'] = '   '
        self.assertEqual(self.client.post('/api/pairs', json=payload).status_code, 422)

    def test_file_disappeared_returns_clear_error(self):
        audio = self.upload().json()
        next((self.root / 'audio').glob('*.wav')).unlink()
        self.assertEqual(self.client.get(f"/api/audio/{audio['id']}/content").status_code, 404)
