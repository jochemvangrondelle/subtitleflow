# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Tests for Ollama client."""

from unittest.mock import Mock, patch

from subtitleflow.common.clients.ollama import OllamaClient
from subtitleflow.common.models.config import AppConfig


class TestOllamaClient:
    """Tests for OllamaClient."""

    def test_client_initialization(self, app_config: AppConfig) -> None:
        """Test client initialization."""
        client = OllamaClient(app_config)

        assert client.config == app_config
        assert client.client is not None

    @patch("subtitleflow.common.clients.ollama.Client")
    def test_check_server_success(self, mock_client_class: Mock, app_config: AppConfig) -> None:
        """Test successful server check."""
        mock_client = Mock()
        mock_client.list.return_value = {"models": []}
        mock_client_class.return_value = mock_client

        client = OllamaClient(app_config)
        client.client = mock_client

        assert client.check_health() is True

    @patch("subtitleflow.common.clients.ollama.Client")
    def test_check_server_failure(self, mock_client_class: Mock, app_config: AppConfig) -> None:
        """Test failed server check."""
        mock_client = Mock()
        mock_client.ps.side_effect = Exception("Connection failed")
        mock_client_class.return_value = mock_client

        client = OllamaClient(app_config)
        client.client = mock_client

        assert client.check_health() is False

    @patch("subtitleflow.common.clients.ollama.Client")
    def test_check_model_exists(self, mock_client_class: Mock, app_config: AppConfig) -> None:
        """Test model existence check."""
        mock_client = Mock()
        mock_client.list.return_value = {
            "models": [
                {"name": "model1:latest"},
                {"name": "model2:latest"},
            ]
        }
        mock_client_class.return_value = mock_client

        client = OllamaClient(app_config)
        client.client = mock_client

        assert client.check_model_exists("model1") is True
        assert client.check_model_exists("model1:latest") is True
        assert client.check_model_exists("nonexistent") is False

    @patch("subtitleflow.common.clients.ollama.Client")
    def test_generate_success(self, mock_client_class: Mock, app_config: AppConfig) -> None:
        """Test successful text generation."""
        mock_client = Mock()
        # Mock streaming response
        mock_response = [{"response": "Generated text", "done": True}]
        mock_client.generate.return_value = mock_response
        mock_client_class.return_value = mock_client

        client = OllamaClient(app_config)
        client.client = mock_client

        result = client.generate("test-model", "Test prompt")

        assert result == "Generated text"
        mock_client.generate.assert_called()

    @patch("subtitleflow.common.clients.ollama.Client")
    def test_generate_with_retry(self, mock_client_class: Mock, app_config: AppConfig) -> None:
        """Test text generation with retry."""
        mock_client = Mock()
        # First call fails, second succeeds
        mock_client.generate.side_effect = [
            Exception("Temporary error"),
            [{"response": "Generated text", "done": True}],
        ]
        mock_client_class.return_value = mock_client

        client = OllamaClient(app_config)
        client.client = mock_client

        result = client.generate("test-model", "Test prompt", max_retries=2)

        assert result == "Generated text"
        assert mock_client.generate.call_count == 2

    @patch("subtitleflow.common.clients.ollama.Client")
    def test_generate_empty_response(self, mock_client_class: Mock, app_config: AppConfig) -> None:
        """Test handling of empty response."""
        mock_client = Mock()
        mock_client.generate.side_effect = [
            [{"response": "", "done": True}],
            [{"response": "Valid response", "done": True}],
        ]
        mock_client_class.return_value = mock_client

        client = OllamaClient(app_config)
        client.client = mock_client

        result = client.generate("test-model", "Test prompt", max_retries=2)

        assert result == "Valid response"

    @patch("subtitleflow.common.clients.ollama.Client")
    def test_get_model_options_qwen3(self, mock_client_class: Mock, app_config: AppConfig) -> None:
        """Test model options for Qwen3 models."""
        client = OllamaClient(app_config)

        options = client._get_model_options("qwen3:7b")

        assert options["temperature"] == 0.7
        assert "top_p" in options
        assert "top_k" in options

    @patch("subtitleflow.common.clients.ollama.Client")
    def test_get_model_options_default(
        self, mock_client_class: Mock, app_config: AppConfig
    ) -> None:
        """Test model options for default models."""
        client = OllamaClient(app_config)

        options = client._get_model_options("other-model")

        assert options["temperature"] == 0.1
        assert "top_p" in options
        assert "repeat_penalty" in options
