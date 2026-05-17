"""Tests for EasyRouter API client wrapper."""

import os
from unittest.mock import Mock, patch

import pytest

from scripts.ai_filter.easyrouter_client import EasyRouterClient


class TestEasyRouterClient:
    """Test suite for EasyRouterClient."""

    def test_client_initialization(self):
        """Test client initializes with environment variables."""
        with patch.dict(os.environ, {
            'EASYROUTER_API_KEY': 'test-key',
            'EASYROUTER_BASE_URL': 'https://api.easyrouter.test'
        }):
            client = EasyRouterClient()
            assert client.api_key == 'test-key'
            assert client.base_url == 'https://api.easyrouter.test'

    def test_successful_api_call(self):
        """Test successful API call returns expected format."""
        with patch.dict(os.environ, {
            'EASYROUTER_API_KEY': 'test-key',
            'EASYROUTER_BASE_URL': 'https://api.easyrouter.test'
        }):
            client = EasyRouterClient()

            # Mock the requests.post call
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'choices': [{
                    'message': {
                        'content': 'Test response'
                    }
                }],
                'usage': {
                    'total_tokens': 100
                }
            }

            with patch('requests.post', return_value=mock_response):
                result = client.call_model(
                    model='gpt-4o-mini',
                    system_prompt='You are a helpful assistant.',
                    user_prompt='Hello',
                    temperature=0.7,
                    max_tokens=500
                )

                assert result['content'] == 'Test response'
                assert result['tokens'] == 100

    def test_api_error_handling(self):
        """Test API error raises appropriate exception."""
        with patch.dict(os.environ, {
            'EASYROUTER_API_KEY': 'test-key',
            'EASYROUTER_BASE_URL': 'https://api.easyrouter.test'
        }):
            client = EasyRouterClient()

            # Mock failed API call
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.raise_for_status.side_effect = Exception('API Error')

            with patch('requests.post', return_value=mock_response):
                with pytest.raises(Exception) as exc_info:
                    client.call_model(
                        model='gpt-4o-mini',
                        system_prompt='You are a helpful assistant.',
                        user_prompt='Hello',
                        temperature=0.7,
                        max_tokens=500
                    )

                assert 'API Error' in str(exc_info.value)

    def test_missing_api_key_raises_error(self, monkeypatch):
        """Client should raise error when API key is missing."""
        # Clear all environment variables
        monkeypatch.delenv("EASYROUTER_API_KEY", raising=False)
        monkeypatch.delenv("EASYROUTER_BASE_URL", raising=False)

        with pytest.raises(ValueError) as exc_info:
            EasyRouterClient()

        assert "EASYROUTER_API_KEY" in str(exc_info.value)
