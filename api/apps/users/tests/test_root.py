from django.test import TestCase, Client


class RootEndpointTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_root_returns_api_info(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('message', data)
        self.assertIn('endpoints', data)
