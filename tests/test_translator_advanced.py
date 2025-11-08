# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Advanced tests for translator service."""

from unittest.mock import Mock

import pytest

from subtitleflow.common.models.config import AppConfig
from subtitleflow.common.models.subtitle import Subtitle, SubtitleFile
from subtitleflow.common.models.translation import Candidate
from subtitleflow.correct.service import GrammarCorrectionService
from subtitleflow.translate.service import TranslationService


class TestGrammarCorrectionAdvanced:
    """Advanced grammar correction service tests."""

    @pytest.fixture
    def grammar_service(self, app_config: AppConfig) -> GrammarCorrectionService:
        """Create mocked grammar correction service."""
        mock_client = Mock()
        mock_cache = Mock()
        mock_judge = Mock()

        return GrammarCorrectionService(
            config=app_config, client=mock_client, cache=mock_cache, judge=mock_judge
        )

    def test_correct_grammar_single_subtitle(
        self, grammar_service: GrammarCorrectionService, sample_subtitle: Subtitle
    ) -> None:
        """Test grammar correction on single subtitle."""
        subtitle_file = SubtitleFile(path="test.srt", subtitles=[sample_subtitle])

        # Mock cache miss and model response
        grammar_service.cache.get.return_value = None
        grammar_service.client.generate.return_value = "1. Corrected text!"
        grammar_service.judge.select_best.return_value = Candidate(
            model="test", text="Corrected text!"
        )

        result = grammar_service.correct(subtitle_file)

        assert len(result.subtitles) == 1
        assert result.subtitles[0].content == "Corrected text!"


class TestTranslationAdvanced:
    """Advanced translation service tests."""

    @pytest.fixture
    def translation_service(self, app_config: AppConfig) -> TranslationService:
        """Create mocked translation service."""
        mock_client = Mock()
        mock_cache = Mock()
        mock_judge = Mock()

        return TranslationService(
            config=app_config, client=mock_client, cache=mock_cache, judge=mock_judge
        )

    def test_translate_with_cache_hit(
        self, translation_service: TranslationService, sample_subtitle: Subtitle
    ) -> None:
        """Test translation with cache hit."""
        subtitle_file = SubtitleFile(path="test.srt", subtitles=[sample_subtitle])

        # Mock batch translator to return cached translation
        translation_service.batch_translator.translate_all = Mock(
            return_value=["Cached translation"]
        )

        result = translation_service.translate(subtitle_file, "dutch")

        assert len(result.subtitles) == 1
        assert result.subtitles[0].content == "Cached translation"
