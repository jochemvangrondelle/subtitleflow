# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Cache service for translations and corrections."""

import hashlib
import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class CacheService:
    """Context-aware caching for translations."""

    def __init__(self, cache_file: str = "srt_ollama_cache.json") -> None:
        """
        Initialize cache service.

        Args:
            cache_file: Path to cache file
        """
        self.cache_file = Path(cache_file)
        self.cache: dict[str, dict] = {"fix": {}, "translate": {}}
        self._load()

    def _load(self) -> None:
        """Load cache from disk."""
        if self.cache_file.exists():
            try:
                with self.cache_file.open(encoding="utf-8") as f:
                    self.cache = json.load(f)
                logger.debug(f"Loaded cache from {self.cache_file}")
            except Exception as e:
                logger.warning(f"Could not load cache: {e}")
                self.cache = {"fix": {}, "translate": {}}

    def save(self) -> None:
        """Save cache to disk."""
        try:
            with self.cache_file.open("w", encoding="utf-8") as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
            logger.debug(f"Saved cache to {self.cache_file}")
        except Exception as e:
            logger.warning(f"Could not save cache: {e}")

    def _build_cache_key(
        self,
        text: str,
        context_before: list[str],
        languages: list[str] | None = None,
        language: str | None = None,
    ) -> str:
        """
        Build context-aware cache key.

        Args:
            text: Subtitle text to translate
            context_before: Previous subtitle lines
            languages: Multiple target languages
            language: Single target language

        Returns:
            Cache key string
        """
        # Get immediate previous subtitle (most important for context)
        prev_subtitle = context_before[-1] if context_before else "NONE"
        # Truncate if too long to keep cache keys manageable
        prev_subtitle_short = prev_subtitle[:100] if len(prev_subtitle) > 100 else prev_subtitle

        # Hash the broader context (all previous N lines) for additional context
        context_hash = (
            hashlib.md5("||".join(context_before).encode("utf-8")).hexdigest()[:8]
            if context_before
            else "NOCTX"
        )

        # Build language string
        if languages:
            langs_str = ",".join(sorted(languages))
        elif language:
            langs_str = language
        else:
            langs_str = ""

        # Build comprehensive cache key
        return f"{text}||PREV:{prev_subtitle_short}||CTX:{context_hash}||LANGS:{langs_str}"

    def get(
        self,
        section: str,
        model: str,
        text: str,
        context_before: list[str],
        languages: list[str] | None = None,
        language: str | None = None,
    ) -> Any | None:
        """
        Get cached result.

        Args:
            section: Cache section ("fix" or "translate")
            model: Model name
            text: Subtitle text
            context_before: Previous subtitle lines
            languages: Multiple target languages
            language: Single target language

        Returns:
            Cached result or None if not found
        """
        cache_key = self._build_cache_key(text, context_before, languages, language)

        if section not in self.cache:
            return None

        if model not in self.cache[section]:
            return None

        return self.cache[section][model].get(cache_key)

    def set(
        self,
        section: str,
        model: str,
        text: str,
        context_before: list[str],
        value: Any,
        languages: list[str] | None = None,
        language: str | None = None,
    ) -> None:
        """
        Set cached result.

        Args:
            section: Cache section ("fix" or "translate")
            model: Model name
            text: Subtitle text
            context_before: Previous subtitle lines
            value: Value to cache
            languages: Multiple target languages
            language: Single target language
        """
        cache_key = self._build_cache_key(text, context_before, languages, language)

        if section not in self.cache:
            self.cache[section] = {}

        if model not in self.cache[section]:
            self.cache[section][model] = {}

        self.cache[section][model][cache_key] = value
        self.save()

    def get_section(self, section: str) -> dict:
        """Get entire cache section."""
        return self.cache.get(section, {})

    def clear(self, section: str | None = None) -> None:
        """
        Clear cache.

        Args:
            section: Section to clear, or None to clear all
        """
        if section:
            self.cache[section] = {}
        else:
            self.cache = {"fix": {}, "translate": {}}
        self.save()
