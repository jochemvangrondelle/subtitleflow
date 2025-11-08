# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Tests for cache service."""

from pathlib import Path

from subtitleflow.common.services.cache import CacheService


class TestCacheService:
    """Tests for CacheService."""

    def test_cache_initialization(self, cache_service: CacheService) -> None:
        """Test cache initialization."""
        assert cache_service.cache is not None
        assert "fix" in cache_service.cache
        assert "translate" in cache_service.cache

    def test_cache_set_and_get(self, cache_service: CacheService) -> None:
        """Test setting and getting cache values."""
        cache_service.set(
            section="translate",
            model="test-model",
            text="Hello",
            context_before=["Previous line"],
            value="Hola",
            language="spanish",
        )

        result = cache_service.get(
            section="translate",
            model="test-model",
            text="Hello",
            context_before=["Previous line"],
            language="spanish",
        )

        assert result == "Hola"

    def test_cache_miss(self, cache_service: CacheService) -> None:
        """Test cache miss returns None."""
        result = cache_service.get(
            section="translate",
            model="nonexistent",
            text="Hello",
            context_before=[],
            language="spanish",
        )

        assert result is None

    def test_cache_context_sensitivity(self, cache_service: CacheService) -> None:
        """Test that cache is context-aware."""
        # Set with context A
        cache_service.set(
            section="translate",
            model="test-model",
            text="Hello",
            context_before=["Context A"],
            value="Translation A",
            language="spanish",
        )

        # Set with context B
        cache_service.set(
            section="translate",
            model="test-model",
            text="Hello",
            context_before=["Context B"],
            value="Translation B",
            language="spanish",
        )

        # Get with context A
        result_a = cache_service.get(
            section="translate",
            model="test-model",
            text="Hello",
            context_before=["Context A"],
            language="spanish",
        )

        # Get with context B
        result_b = cache_service.get(
            section="translate",
            model="test-model",
            text="Hello",
            context_before=["Context B"],
            language="spanish",
        )

        assert result_a == "Translation A"
        assert result_b == "Translation B"

    def test_cache_multi_language(self, cache_service: CacheService) -> None:
        """Test caching multi-language results."""
        translations = {"dutch": "Hallo", "spanish": "Hola"}

        cache_service.set(
            section="translate",
            model="test-model",
            text="Hello",
            context_before=[],
            value=translations,
            languages=["dutch", "spanish"],
        )

        result = cache_service.get(
            section="translate",
            model="test-model",
            text="Hello",
            context_before=[],
            languages=["dutch", "spanish"],
        )

        assert result == translations

    def test_cache_clear_section(self, cache_service: CacheService) -> None:
        """Test clearing a cache section."""
        cache_service.set(
            section="translate",
            model="test-model",
            text="Hello",
            context_before=[],
            value="Hola",
            language="spanish",
        )

        cache_service.clear(section="translate")

        result = cache_service.get(
            section="translate",
            model="test-model",
            text="Hello",
            context_before=[],
            language="spanish",
        )

        assert result is None

    def test_cache_clear_all(self, cache_service: CacheService) -> None:
        """Test clearing entire cache."""
        cache_service.set(
            section="translate",
            model="test-model",
            text="Hello",
            context_before=[],
            value="Hola",
            language="spanish",
        )

        cache_service.clear()

        assert cache_service.cache == {"fix": {}, "translate": {}}

    def test_cache_persistence(self, temp_dir: Path) -> None:
        """Test cache persistence to disk."""
        cache_file = temp_dir / "cache.json"

        # Create cache and add data
        cache1 = CacheService(str(cache_file))
        cache1.set(
            section="translate",
            model="test-model",
            text="Hello",
            context_before=[],
            value="Hola",
            language="spanish",
        )

        # Load new cache from same file
        cache2 = CacheService(str(cache_file))
        result = cache2.get(
            section="translate",
            model="test-model",
            text="Hello",
            context_before=[],
            language="spanish",
        )

        assert result == "Hola"
