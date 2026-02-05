import unittest
import json
from app import app


class TestServiceA(unittest.TestCase):
    """Test suite for Service A endpoints"""

    def setUp(self):
        """Set up test client before each test"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_health_endpoint(self):
        """Test /health endpoint returns ok status"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'ok')

    def test_echo_simple_message(self):
        """Test /echo endpoint with a simple message"""
        response = self.client.get('/echo?msg=hello')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['echo'], 'hello')

    def test_echo_empty_message(self):
        """Test /echo endpoint with no message parameter"""
        response = self.client.get('/echo')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['echo'], '')

    def test_echo_special_characters(self):
        """Test /echo endpoint with special characters"""
        response = self.client.get('/echo?msg=hello%20world%21')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['echo'], 'hello world!')

    def test_reverse_simple_message(self):
        """Test /reverse endpoint with a simple message"""
        response = self.client.get('/reverse?msg=hello')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['reversed'], 'olleh')

    def test_reverse_empty_message(self):
        """Test /reverse endpoint with no message parameter"""
        response = self.client.get('/reverse')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['reversed'], '')

    def test_reverse_palindrome(self):
        """Test /reverse endpoint with a palindrome"""
        response = self.client.get('/reverse?msg=racecar')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['reversed'], 'racecar')

    def test_reverse_with_spaces(self):
        """Test /reverse endpoint with spaces"""
        response = self.client.get('/reverse?msg=hello%20world')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['reversed'], 'dlrow olleh')

    def test_reverse_single_character(self):
        """Test /reverse endpoint with single character"""
        response = self.client.get('/reverse?msg=a')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['reversed'], 'a')


if __name__ == '__main__':
    unittest.main()
