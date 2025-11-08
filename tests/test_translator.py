# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Tests for translator service."""

from unittest.mock import Mock

import pytest

from subtitleflow.common.clients.ollama import OllamaClient
from subtitleflow.common.models.config import AppConfig
from subtitleflow.common.models.subtitle import SubtitleFile
from subtitleflow.common.services.cache import CacheService
from subtitleflow.common.services.judge import JudgeService
from subtitleflow.translate.service import TranslationService


class TestTranslationService:
    """Tests for TranslationService."""

    @pytest.fixture
    def translation_service(self, app_config: AppConfig) -> TranslationService:
        """Create translation service with mocks."""
        mock_client = Mock(spec=OllamaClient)
        mock_cache = Mock(spec=CacheService)
        mock_judge = Mock(spec=JudgeService)

        return TranslationService(
            config=app_config, client=mock_client, cache=mock_cache, judge=mock_judge
        )

    def test_translate_single_model(
        self, translation_service: TranslationService, sample_subtitle_file: SubtitleFile
    ) -> None:
        """Test translation with single model."""
        # Mock batch translator
        translation_service.batch_translator.translate_all = Mock(return_value=["Hallo wereld"])

        result = translation_service.translate(sample_subtitle_file, "dutch")

        assert len(result.subtitles) == 1
        assert result.subtitles[0].content == "Hallo wereld"

    def test_translate_multiple_models(
        self, translation_service: TranslationService, sample_subtitle_file: SubtitleFile
    ) -> None:
        """Test translation with multiple models and judge."""
        # Mock batch translator to return different translations
        translation_service.batch_translator.translate_all = Mock(
            side_effect=[["Hallo wereld"], ["Hallo wereldje"]]
        )
        # Mock judge to select first candidate
        from subtitleflow.common.models.translation import Candidate

        translation_service.judge.select_best = Mock(
            return_value=Candidate(model="test-model", text="Hallo wereld")
        )

        result = translation_service.translate(sample_subtitle_file, "dutch")

        assert len(result.subtitles) == 1
        assert translation_service.judge.select_best.called
