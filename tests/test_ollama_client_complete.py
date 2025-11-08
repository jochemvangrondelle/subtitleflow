# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Complete tests for OllamaClient."""

from unittest.mock import Mock, patch

import ollama
import pytest

from subtitleflow.common.clients.ollama import OllamaClient


class TestOllamaClient:
    """Test OllamaClient."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        from subtitleflow.common.models.config import AppConfig

        config = AppConfig(ollama_url="http://127.0.0.1:11434")
        self.client = OllamaClient(config)

    def test_init_default_url(self) -> None:
        """Test OllamaClient initialization with default URL."""
        from subtitleflow.common.models.config import AppConfig

        config = AppConfig()
        client = OllamaClient(config)
        assert client.config.ollama_base_url == "http://127.0.0.1:11434"

    def test_init_custom_url(self) -> None:
        """Test OllamaClient initialization with custom URL."""
        from subtitleflow.common.models.config import AppConfig

        config = AppConfig(ollama_url="http://custom:8080")
        client = OllamaClient(config)
        assert client.config.ollama_base_url == "http://custom:8080"

    def test_init_with_trailing_slash(self) -> None:
        """Test OllamaClient initialization with trailing slash."""
        from subtitleflow.common.models.config import AppConfig

        config = AppConfig(ollama_url="http://127.0.0.1:11434/")
        client = OllamaClient(config)
        assert client.config.ollama_base_url == "http://127.0.0.1:11434"

    def test_init_with_api_path(self) -> None:
        """Test OllamaClient initialization with API path."""
        from subtitleflow.common.models.config import AppConfig

        config = AppConfig(ollama_url="http://127.0.0.1:11434/api/generate")
        client = OllamaClient(config)
        assert client.config.ollama_base_url == "http://127.0.0.1:11434"

    @patch("ollama.health")
    def test_health_check_success(self, mock_health) -> None:
        """Test successful health check."""
        mock_health.return_value = {"status": "ok"}

        result = self.client.health_check()

        assert result is True
        mock_health.assert_called_once_with(host="http://127.0.0.1:11434")

    @patch("ollama.health")
    def test_health_check_failure(self, mock_health) -> None:
        """Test failed health check."""
        mock_health.side_effect = Exception("Connection failed")

        result = self.client.health_check()

        assert result is False

    @patch("ollama.health")
    def test_health_check_custom_host(self, mock_health) -> None:
        """Test health check with custom host."""
        mock_health.return_value = {"status": "ok"}

        from subtitleflow.common.models.config import AppConfig

        config = AppConfig(ollama_url="http://custom:8080")
        client = OllamaClient(config)
        result = client.health_check()

        assert result is True
        mock_health.assert_called_once_with(host="http://custom:8080")

    @patch("ollama.chat")
    def test_generate_chat_mode(self, mock_chat) -> None:
        """Test generate method in chat mode."""
        mock_response = Mock()
        mock_response.message.content = "Test response"
        mock_chat.return_value = mock_response

        result = self.client.generate("test-model", "Test prompt")

        assert result == "Test response"
        mock_chat.assert_called_once_with(
            model="test-model",
            messages=[{"role": "user", "content": "Test prompt"}],
            options={"temperature": 0.7},
        )

    @patch("ollama.chat")
    def test_generate_with_temperature(self, mock_chat) -> None:
        """Test generate method with custom temperature."""
        mock_response = Mock()
        mock_response.message.content = "Test response"
        mock_chat.return_value = mock_response

        result = self.client.generate("test-model", "Test prompt", temperature=0.5)

        assert result == "Test response"
        mock_chat.assert_called_once_with(
            model="test-model",
            messages=[{"role": "user", "content": "Test prompt"}],
            options={"temperature": 0.5},
        )

    @patch("ollama.chat")
    def test_generate_with_streaming(self, mock_chat) -> None:
        """Test generate method with streaming."""
        mock_response = Mock()
        mock_response.message.content = "Test response"
        mock_chat.return_value = mock_response

        result = self.client.generate("test-model", "Test prompt", stream=True)

        assert result == "Test response"
        mock_chat.assert_called_once_with(
            model="test-model",
            messages=[{"role": "user", "content": "Test prompt"}],
            options={"temperature": 0.7},
            stream=True,
        )

    @patch("ollama.chat")
    def test_generate_chat_error(self, mock_chat) -> None:
        """Test generate method with chat error."""
        mock_chat.side_effect = ollama.ResponseError("Chat error", 500)

        with pytest.raises(RuntimeError, match="Chat error"):
            self.client.generate("test-model", "Test prompt")

    @patch("ollama.chat")
    def test_generate_chat_error_with_status_code(self, mock_chat) -> None:
        """Test generate method with chat error and status code."""
        mock_chat.side_effect = ollama.ResponseError("Chat error", 404)

        with pytest.raises(RuntimeError, match="Chat error"):
            self.client.generate("test-model", "Test prompt")

    @patch("ollama.chat")
    def test_generate_chat_error_without_message(self, mock_chat) -> None:
        """Test generate method with chat error without message."""
        mock_chat.side_effect = ollama.ResponseError("", 500)

        with pytest.raises(RuntimeError, match="Ollama API error"):
            self.client.generate("test-model", "Test prompt")

    @patch("ollama.generate")
    def test_generate_generate_mode(self, mock_generate) -> None:
        """Test generate method in generate mode."""
        mock_response = Mock()
        mock_response.response = "Test response"
        mock_generate.return_value = mock_response

        # Mock the chat method to raise an exception to trigger generate mode
        with patch("ollama.chat", side_effect=Exception("Chat not available")):
            result = self.client.generate("test-model", "Test prompt")

        assert result == "Test response"
        mock_generate.assert_called_once_with(
            model="test-model", prompt="Test prompt", options={"temperature": 0.7}
        )

    @patch("ollama.generate")
    def test_generate_generate_mode_with_temperature(self, mock_generate) -> None:
        """Test generate method in generate mode with custom temperature."""
        mock_response = Mock()
        mock_response.response = "Test response"
        mock_generate.return_value = mock_response

        with patch("ollama.chat", side_effect=Exception("Chat not available")):
            result = self.client.generate("test-model", "Test prompt", temperature=0.3)

        assert result == "Test response"
        mock_generate.assert_called_once_with(
            model="test-model", prompt="Test prompt", options={"temperature": 0.3}
        )

    @patch("ollama.generate")
    def test_generate_generate_mode_with_streaming(self, mock_generate) -> None:
        """Test generate method in generate mode with streaming."""
        mock_response = Mock()
        mock_response.response = "Test response"
        mock_generate.return_value = mock_response

        with patch("ollama.chat", side_effect=Exception("Chat not available")):
            result = self.client.generate("test-model", "Test prompt", stream=True)

        assert result == "Test response"
        mock_generate.assert_called_once_with(
            model="test-model", prompt="Test prompt", options={"temperature": 0.7}, stream=True
        )

    @patch("ollama.generate")
    def test_generate_generate_error(self, mock_generate) -> None:
        """Test generate method with generate error."""
        mock_generate.side_effect = ollama.ResponseError("Generate error", 500)

        with (
            patch("ollama.chat", side_effect=Exception("Chat not available")),
            pytest.raises(RuntimeError, match="Generate error"),
        ):
            self.client.generate("test-model", "Test prompt")

    @patch("ollama.generate")
    def test_generate_both_methods_fail(self, mock_generate) -> None:
        """Test generate method when both chat and generate fail."""
        mock_generate.side_effect = Exception("Generate failed")

        with (
            patch("ollama.chat", side_effect=Exception("Chat failed")),
            pytest.raises(RuntimeError, match="Both chat and generate methods failed"),
        ):
            self.client.generate("test-model", "Test prompt")

    @patch("ollama.generate")
    def test_generate_generate_error_with_status_code(self, mock_generate) -> None:
        """Test generate method with generate error and status code."""
        mock_generate.side_effect = ollama.ResponseError("Generate error", 404)

        with (
            patch("ollama.chat", side_effect=Exception("Chat not available")),
            pytest.raises(RuntimeError, match="Generate error"),
        ):
            self.client.generate("test-model", "Test prompt")

    @patch("ollama.generate")
    def test_generate_generate_error_without_message(self, mock_generate) -> None:
        """Test generate method with generate error without message."""
        mock_generate.side_effect = ollama.ResponseError("", 500)

        with (
            patch("ollama.chat", side_effect=Exception("Chat not available")),
            pytest.raises(RuntimeError, match="Ollama API error"),
        ):
            self.client.generate("test-model", "Test prompt")

    def test_generate_empty_prompt(self) -> None:
        """Test generate method with empty prompt."""
        with patch("ollama.chat") as mock_chat:
            mock_response = Mock()
            mock_response.message.content = ""
            mock_chat.return_value = mock_response

            result = self.client.generate("test-model", "")

            assert result == ""

    def test_generate_none_prompt(self) -> None:
        """Test generate method with None prompt."""
        with patch("ollama.chat") as mock_chat:
            mock_response = Mock()
            mock_response.message.content = "None"
            mock_chat.return_value = mock_response

            result = self.client.generate("test-model", None)

            assert result == "None"

    def test_generate_very_long_prompt(self) -> None:
        """Test generate method with very long prompt."""
        long_prompt = "Test " * 1000

        with patch("ollama.chat") as mock_chat:
            mock_response = Mock()
            mock_response.message.content = "Response"
            mock_chat.return_value = mock_response

            result = self.client.generate("test-model", long_prompt)

            assert result == "Response"
            mock_chat.assert_called_once_with(
                model="test-model",
                messages=[{"role": "user", "content": long_prompt}],
                options={"temperature": 0.7},
            )

    def test_generate_special_characters(self) -> None:
        """Test generate method with special characters in prompt."""
        special_prompt = "Test with émojis 🎉 and special chars: !@#$%^&*()"

        with patch("ollama.chat") as mock_chat:
            mock_response = Mock()
            mock_response.message.content = "Response"
            mock_chat.return_value = mock_response

            result = self.client.generate("test-model", special_prompt)

            assert result == "Response"
            mock_chat.assert_called_once_with(
                model="test-model",
                messages=[{"role": "user", "content": special_prompt}],
                options={"temperature": 0.7},
            )

    def test_generate_unicode_prompt(self) -> None:
        """Test generate method with unicode prompt."""
        unicode_prompt = "测试中文和日本語と한국어"

        with patch("ollama.chat") as mock_chat:
            mock_response = Mock()
            mock_response.message.content = "Response"
            mock_chat.return_value = mock_response

            result = self.client.generate("test-model", unicode_prompt)

            assert result == "Response"
            mock_chat.assert_called_once_with(
                model="test-model",
                messages=[{"role": "user", "content": unicode_prompt}],
                options={"temperature": 0.7},
            )
