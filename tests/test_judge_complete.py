# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Complete tests for judge service."""

from unittest.mock import Mock

from subtitleflow.common.models.translation import Candidate
from subtitleflow.common.services.judge import JudgeService


class TestJudgeServiceComplete:
    """Comprehensive tests for JudgeService."""

    def test_select_best_with_context(self) -> None:
        """Test selection with previous context."""
        mock_client = Mock()
        mock_client.generate.return_value = "1"

        judge = JudgeService(mock_client, "test-model")

        candidates = [
            Candidate("model1", "Option 1"),
            Candidate("model2", "Option 2"),
        ]
        previous = ["Previous translation 1", "Previous translation 2"]

        result = judge.select_best("Original text", candidates, previous_translations=previous)

        assert result.text == "Option 1"
        # Verify context was passed in prompt
        call_args = mock_client.generate.call_args
        prompt = call_args[0][1]
        assert "Previous translation" in prompt

    def test_select_best_with_language(self) -> None:
        """Test selection with language specified."""
        mock_client = Mock()
        mock_client.generate.return_value = "2"

        judge = JudgeService(mock_client, "test-model")

        candidates = [
            Candidate("model1", "Dutch 1"),
            Candidate("model2", "Dutch 2"),
        ]

        result = judge.select_best("Original", candidates, language="dutch")

        assert result.text == "Dutch 2"

    def test_select_best_text_match_fallback(self) -> None:
        """Test fallback to text matching."""
        mock_client = Mock()
        mock_client.generate.return_value = "Dutch 2"  # Exact text match

        judge = JudgeService(mock_client, "test-model")

        candidates = [
            Candidate("model1", "Dutch 1"),
            Candidate("model2", "Dutch 2"),
        ]

        result = judge.select_best("Original", candidates)

        assert result.text == "Dutch 2"

    def test_select_best_out_of_range(self) -> None:
        """Test handling of out-of-range selection."""
        mock_client = Mock()
        mock_client.generate.return_value = "99"  # Invalid number

        judge = JudgeService(mock_client, "test-model")

        candidates = [
            Candidate("model1", "Option 1"),
            Candidate("model2", "Option 2"),
        ]

        result = judge.select_best("Original", candidates)

        # Should fallback to first candidate
        assert result.text == "Option 1"

    def test_select_best_multi_all_languages(self) -> None:
        """Test multi-language selection for all languages."""
        mock_client = Mock()
        mock_client.generate.return_value = "1"

        judge = JudgeService(mock_client, "test-model")

        candidates_by_lang = {
            "dutch": [
                Candidate("model1", "NL 1"),
                Candidate("model2", "NL 2"),
            ],
            "spanish": [
                Candidate("model1", "ES 1"),
                Candidate("model2", "ES 2"),
            ],
            "french": [
                Candidate("model1", "FR 1"),
                Candidate("model2", "FR 2"),
            ],
        }

        results = judge.select_best_multi("Original", candidates_by_lang)

        assert len(results) == 3
        assert all(lang in results for lang in ["dutch", "spanish", "french"])
        # Verify all results are Candidate objects with text
        assert all(isinstance(results[lang], Candidate) for lang in results)
        assert all(results[lang].text for lang in results)

    def test_select_best_multi_with_context(self) -> None:
        """Test multi-language selection with context."""
        mock_client = Mock()
        mock_client.generate.return_value = "2"

        judge = JudgeService(mock_client, "test-model")

        candidates_by_lang = {
            "dutch": [
                Candidate("model1", "NL 1"),
                Candidate("model2", "NL 2"),
            ],
        }

        previous = {"dutch": ["Previous NL 1", "Previous NL 2"]}

        results = judge.select_best_multi(
            "Original", candidates_by_lang, previous_translations_by_lang=previous
        )

        assert results["dutch"].text == "NL 2"
