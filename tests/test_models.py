# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Tests for domain models."""

from datetime import timedelta

from subtitleflow.common.models.config import AppConfig, get_language_code
from subtitleflow.common.models.subtitle import Subtitle, SubtitleFile
from subtitleflow.common.models.translation import Candidate, TranslationResult


class TestSubtitle:
    """Tests for Subtitle model."""

    def test_subtitle_creation(self) -> None:
        """Test creating a subtitle."""
        sub = Subtitle(
            index=1, start=timedelta(seconds=0), end=timedelta(seconds=2), content="Test content"
        )
        assert sub.index == 1
        assert sub.content == "Test content"
        assert sub.duration == timedelta(seconds=2)

    def test_subtitle_duration(self) -> None:
        """Test subtitle duration calculation."""
        sub = Subtitle(
            index=1, start=timedelta(seconds=1), end=timedelta(seconds=5), content="Test"
        )
        assert sub.duration == timedelta(seconds=4)


class TestSubtitleFile:
    """Tests for SubtitleFile model."""

    def test_subtitle_file_load_save(self, sample_subtitle_file: SubtitleFile) -> None:
        """Test loading and saving subtitle files."""
        # Load the file we just created
        loaded = SubtitleFile.load(sample_subtitle_file.path)

        assert len(loaded) == 3
        assert loaded[0].content == "Hello, world!"
        assert loaded[2].content == "♪ Music line ♪"

    def test_subtitle_file_length(self, sample_subtitle_file: SubtitleFile) -> None:
        """Test subtitle file length."""
        assert len(sample_subtitle_file) == 3

    def test_subtitle_file_indexing(self, sample_subtitle_file: SubtitleFile) -> None:
        """Test subtitle file indexing."""
        assert sample_subtitle_file[0].content == "Hello, world!"
        assert sample_subtitle_file[1].content == "This is a test."


class TestCandidate:
    """Tests for Candidate model."""

    def test_candidate_creation(self) -> None:
        """Test creating a candidate."""
        candidate = Candidate(model="test-model", text="Translated text")
        assert candidate.model == "test-model"
        assert candidate.text == "Translated text"

    def test_candidate_preview(self) -> None:
        """Test candidate preview truncation."""
        long_text = "a" * 300
        candidate = Candidate(model="test", text=long_text)

        assert len(candidate.preview) == 243  # 240 + "..."
        assert candidate.preview.endswith("...")

    def test_candidate_preview_short(self) -> None:
        """Test candidate preview with short text."""
        candidate = Candidate(model="test", text="Short")
        assert candidate.preview == "Short"


class TestTranslationResult:
    """Tests for TranslationResult model."""

    def test_translation_result_creation(self, sample_subtitle: Subtitle) -> None:
        """Test creating a translation result."""
        translated = Subtitle(
            index=1, start=sample_subtitle.start, end=sample_subtitle.end, content="Hola, mundo!"
        )

        result = TranslationResult(original=sample_subtitle, translated=translated, cache_hit=True)

        assert result.original.content == "Hello, world!"
        assert result.translated.content == "Hola, mundo!"
        assert result.from_cache is True


class TestConfig:
    """Tests for configuration models."""

    def test_app_config_defaults(self) -> None:
        """Test default app configuration."""
        config = AppConfig()

        assert config.ollama_base_url == "http://127.0.0.1:11434"
        assert config.context_window == 3
        assert config.max_retries == 3
        assert config.enable_cache is True

    def test_app_config_urls(self) -> None:
        """Test URL generation."""
        config = AppConfig(ollama_url="http://example.com:11434")

        assert config.ollama_base_url == "http://example.com:11434"
        assert config.ollama_generate_url == "http://example.com:11434/api/generate"
        assert config.ollama_tags_url == "http://example.com:11434/api/tags"

    def test_language_code_lookup(self) -> None:
        """Test language code lookup using langcodes library."""
        # Test by language name (works in multiple languages)
        assert get_language_code("dutch") == "nl"
        assert get_language_code("Dutch") == "nl"
        assert get_language_code("spanish") == "es"
        assert get_language_code("español") == "es"
        assert get_language_code("FRENCH") == "fr"
        assert get_language_code("français") == "fr"

        # Test by existing code (should return same code)
        assert get_language_code("nl") == "nl"
        assert get_language_code("es") == "es"

        # Test various languages
        assert get_language_code("German") == "de"
        assert get_language_code("Italian") == "it"
        assert get_language_code("Portuguese") == "pt"
        assert get_language_code("Russian") == "ru"
        assert get_language_code("Chinese") == "zh"
        assert get_language_code("Japanese") == "ja"
        assert get_language_code("Korean") == "ko"
        assert get_language_code("Arabic") == "ar"
        assert get_language_code("Hindi") == "hi"
