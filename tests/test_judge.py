# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Tests for judge service."""

from unittest.mock import Mock

from subtitleflow.common.models.translation import Candidate
from subtitleflow.common.services.judge import JudgeService


class TestJudgeService:
    """Tests for JudgeService."""

    def test_select_best_single_candidate(self) -> None:
        """Test selection with single candidate."""
        mock_client = Mock()
        judge = JudgeService(mock_client, "test-model")

        candidates = [Candidate(model="model1", text="Translation 1")]

        result = judge.select_best("Original", candidates)

        assert result == candidates[0]
        # Should not call client for single candidate
        mock_client.generate.assert_not_called()

    def test_select_best_multiple_candidates(self) -> None:
        """Test selection with multiple candidates."""
        mock_client = Mock()
        mock_client.generate.return_value = "2"

        judge = JudgeService(mock_client, "test-model")

        candidates = [
            Candidate(model="model1", text="Translation 1"),
            Candidate(model="model2", text="Translation 2"),
            Candidate(model="model3", text="Translation 3"),
        ]

        result = judge.select_best("Original", candidates, language="spanish")

        assert result == candidates[1]
        mock_client.generate.assert_called_once()

    def test_select_best_invalid_response_fallback(self) -> None:
        """Test fallback when judge returns invalid response."""
        mock_client = Mock()
        mock_client.generate.return_value = "invalid"

        judge = JudgeService(mock_client, "test-model")

        candidates = [
            Candidate(model="model1", text="Translation 1"),
            Candidate(model="model2", text="Translation 2"),
        ]

        result = judge.select_best("Original", candidates)

        # Should fallback to first candidate
        assert result == candidates[0]

    def test_select_best_with_previous_translations(self) -> None:
        """Test selection with context from previous translations."""
        mock_client = Mock()
        mock_client.generate.return_value = "1"

        judge = JudgeService(mock_client, "test-model")

        candidates = [Candidate(model="model1", text="Translation")]
        previous = ["Previous translation 1", "Previous translation 2"]

        judge.select_best("Original", candidates, previous_translations=previous)

        # Check that previous translations were included in prompt
        call_args = mock_client.generate.call_args
        if call_args:
            prompt = call_args[0][1]
            assert "Previous translation" in prompt

    def test_select_best_multi(self) -> None:
        """Test multi-language candidate selection."""
        mock_client = Mock()
        mock_client.generate.return_value = "1"

        judge = JudgeService(mock_client, "test-model")

        candidates_by_lang = {
            "dutch": [
                Candidate(model="model1", text="Dutch 1"),
                Candidate(model="model2", text="Dutch 2"),
            ],
            "spanish": [
                Candidate(model="model1", text="Spanish 1"),
                Candidate(model="model2", text="Spanish 2"),
            ],
        }

        results = judge.select_best_multi("Original", candidates_by_lang)

        assert len(results) == 2
        assert "dutch" in results
        assert "spanish" in results
        assert results["dutch"].text == "Dutch 1"
        assert results["spanish"].text == "Spanish 1"
