import unittest
from fastapi.testclient import TestClient
from services.api.main import app
class ApiTest(unittest.TestCase):
    def test_health_is_real_and_does_not_claim_music_features(self):
        with TestClient(app) as client:
            response = client.get('/api/health')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['service'], 'p-ia-no-api')
            self.assertFalse(any(response.json()['capabilities'].values()))
    def test_unimplemented_arrangement_does_not_accept_requests(self):
        with TestClient(app) as client:
            self.assertIn(client.post('/api/arrange').status_code, (404, 405))
if __name__ == '__main__': unittest.main()
