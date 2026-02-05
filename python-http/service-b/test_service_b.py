import unittest
import json
from unittest.mock import patch, MagicMock
from app import app


class TestServiceB(unittest.TestCase):
    """Test suite for Service B endpoints"""

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

    @patch('requests.get')
    def test_call_echo_success(self, mock_get):
        """Test /call-echo endpoint when Service A is available"""
        # Mock Service A response
        mock_response = MagicMock()
        mock_response.json.return_value = {'echo': 'hello'}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        response = self.client.get('/call-echo?msg=hello')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['service_b'], 'ok')
        self.assertEqual(data['service_a']['echo'], 'hello')

    @patch('requests.get')
    def test_call_echo_service_a_timeout(self, mock_get):
        """Test /call-echo endpoint when Service A times out"""
        # Mock timeout exception
        mock_get.side_effect = Exception('Timeout')

        response = self.client.get('/call-echo?msg=hello')
        self.assertEqual(response.status_code, 503)
        data = json.loads(response.data)
        self.assertEqual(data['service_b'], 'ok')
        self.assertEqual(data['service_a'], 'unavailable')

    @patch('requests.get')
    def test_call_echo_empty_message(self, mock_get):
        """Test /call-echo endpoint with no message parameter"""
        mock_response = MagicMock()
        mock_response.json.return_value = {'echo': ''}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        response = self.client.get('/call-echo')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['service_a']['echo'], '')

    @patch('requests.get')
    def test_transform_success(self, mock_get):
        """Test /transform endpoint when both Service A endpoints work"""
        # Mock both Service A responses
        mock_response_echo = MagicMock()
        mock_response_echo.json.return_value = {'echo': 'hello'}
        mock_response_echo.raise_for_status.return_value = None

        mock_response_reverse = MagicMock()
        mock_response_reverse.json.return_value = {'reversed': 'olleh'}
        mock_response_reverse.raise_for_status.return_value = None

        mock_get.side_effect = [mock_response_echo, mock_response_reverse]

        response = self.client.get('/transform?msg=hello')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['service_b'], 'ok')
        self.assertEqual(data['echo']['echo'], 'hello')
        self.assertEqual(data['reversed']['reversed'], 'olleh')

    @patch('requests.get')
    def test_transform_service_a_unavailable(self, mock_get):
        """Test /transform endpoint when Service A is unavailable"""
        # Mock exception
        mock_get.side_effect = Exception('Connection refused')

        response = self.client.get('/transform?msg=hello')
        self.assertEqual(response.status_code, 503)
        data = json.loads(response.data)
        self.assertEqual(data['service_b'], 'ok')
        self.assertEqual(data['service_a'], 'unavailable')

    @patch('requests.get')
    def test_transform_echo_fails_reverse_succeeds(self, mock_get):
        """Test /transform endpoint when only /echo fails"""
        # Mock echo fails, reverse succeeds
        mock_get.side_effect = [Exception('Echo failed'), MagicMock()]

        response = self.client.get('/transform?msg=hello')
        self.assertEqual(response.status_code, 503)
        data = json.loads(response.data)
        self.assertEqual(data['service_a'], 'unavailable')

    @patch('requests.get')
    def test_transform_empty_message(self, mock_get):
        """Test /transform endpoint with empty message"""
        mock_response_echo = MagicMock()
        mock_response_echo.json.return_value = {'echo': ''}
        mock_response_echo.raise_for_status.return_value = None

        mock_response_reverse = MagicMock()
        mock_response_reverse.json.return_value = {'reversed': ''}
        mock_response_reverse.raise_for_status.return_value = None

        mock_get.side_effect = [mock_response_echo, mock_response_reverse]

        response = self.client.get('/transform')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['echo']['echo'], '')
        self.assertEqual(data['reversed']['reversed'], '')


if __name__ == '__main__':
    unittest.main()
