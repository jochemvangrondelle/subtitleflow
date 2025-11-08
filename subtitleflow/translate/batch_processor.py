# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Batch translation processing with caching and deduplication."""

import logging
from typing import cast

from subtitleflow.common.clients.ollama import OllamaClient
from subtitleflow.common.constants.display import SEPARATOR_DOUBLE
from subtitleflow.common.constants.prompts import TRANSLATE_INSTR
from subtitleflow.common.models.subtitle import Subtitle
from subtitleflow.common.services.cache import CacheService
from subtitleflow.common.utils.batch_cache import BatchCache
from subtitleflow.common.utils.batching import format_batch_for_translation, parse_batch_response
from subtitleflow.common.utils.text_processing import (
    clean_ai_response,
    enforce_continuation_casing,
    enforce_ellipsis_continuation,
    preserve_formatting,
)

logger = logging.getLogger(__name__)


class TranslationBatchProcessor:
    """Handles batch translation with caching and deduplication."""

    def __init__(
        self,
        client: OllamaClient,
        cache: CacheService | None,
    ) -> None:
        """
        Initialize batch processor.

        Args:
            client: Ollama client
            cache: Optional cache service
        """
        self.client = client
        self.batch_cache = BatchCache(cache)

    def translate_batch(
        self,
        batch: list[Subtitle],
        model: str,
        language: str,
        context_lines: str | None = None,
    ) -> list[str]:
        """
        Translate a batch of subtitles with deduplication and caching.

        Args:
            batch: List of subtitles to translate
            model: Model name
            language: Target language
            context_lines: Optional context lines string

        Returns:
            List of translated texts
        """
        context_list = context_lines.split("\n") if context_lines else []

        # Deduplicate and check cache
        cache_data = self.batch_cache.deduplicate_and_cache(
            batch=batch,
            section="translate",
            model=model,
            context_list=context_list,
            language=language,
        )

        unique_subtitles = cache_data["unique_subtitles"]
        position_map = cache_data["position_map"]
        cached_results = cache_data["cached_results"]

        # If all cached, return early
        if len(cached_results) == len(unique_subtitles):
            logger.debug(f"All {len(unique_subtitles)} items found in cache, skipping API call")
            return self.batch_cache.map_to_batch_order(batch, position_map, cached_results)

        # Get uncached items
        uncached_result = self.batch_cache.get_uncached_items(unique_subtitles, cached_results)
        uncached_subtitles = uncached_result[0]
        uncached_indices = cast("list[int]", uncached_result[1])

        # Translate uncached items
        uncached_translations = self._translate_uncached(
            uncached_subtitles, model, language, context_lines
        )

        # Merge results
        unique_translations = self.batch_cache.merge_results(
            unique_subtitles=unique_subtitles,
            cached_results=cached_results,
            uncached_subtitles=uncached_subtitles,
            uncached_indices=uncached_indices,
            uncached_results=uncached_translations,
            section="translate",
            model=model,
            context_list=context_list,
            language=language,
        )

        # Map to batch order
        translations = self.batch_cache.map_to_batch_order(batch, position_map, unique_translations)

        # Clean and format
        return self._clean_translations(batch, translations, language)

    def _translate_uncached(
        self,
        uncached_subtitles: list[Subtitle],
        model: str,
        language: str,
        context_lines: str | None,
    ) -> list[str]:
        """Translate uncached subtitles via API."""
        batch_text = format_batch_for_translation(uncached_subtitles)

        if context_lines:
            subtitle_list = f"""{SEPARATOR_DOUBLE}
CONTEXT (previous {language} translations for continuity - DO NOT OUTPUT THESE):
{context_lines}
{SEPARATOR_DOUBLE}

ENGLISH SUBTITLES TO TRANSLATE TO {language.upper()} (numbered 1-{len(uncached_subtitles)}):
{batch_text}
{SEPARATOR_DOUBLE}"""
        else:
            subtitle_list = batch_text

        prompt = (
            TRANSLATE_INSTR.format(
                num_subtitles=len(uncached_subtitles),
                lang=language,
                subtitle_list=subtitle_list,
            )
            + f"""

{SEPARATOR_DOUBLE}
YOUR {language.upper()} TRANSLATIONS (respond with ONLY these {len(uncached_subtitles)} numbered lines):
{SEPARATOR_DOUBLE}
1."""
        )

        max_tokens = min(len(uncached_subtitles) * 100 + 300, 2048)

        logger.debug(
            f"[TRANSLATION_BATCH] Translating {len(uncached_subtitles)} uncached items "
            f"(max_tokens={max_tokens})"
        )

        response = self.client.generate(model, prompt, temperature=0.3, max_tokens=max_tokens)

        # Prepend "1." if not present
        full_response = "1. " + response if not response.strip().startswith("1.") else response

        return parse_batch_response(full_response, len(uncached_subtitles))

    def _clean_translations(
        self,
        batch: list[Subtitle],
        translations: list[str],
        language: str,
    ) -> list[str]:
        """Clean and format translations."""
        if not translations:
            logger.warning(f"⚠️  Batch parsing failed for {len(batch)} subtitles")
            return []

        if len(translations) != len(batch):
            logger.warning(f"⚠️  Partial parse: got {len(translations)}/{len(batch)} translations")

        cleaned: list[str] = []
        for i, (sub, translation) in enumerate(zip(batch, translations, strict=False)):
            if not translation or len(translation.strip()) == 0:
                logger.warning(f"⚠️  Empty translation for subtitle {i + 1}: '{sub.content}'")

            cleaned_trans = clean_ai_response(translation)
            cleaned_trans = preserve_formatting(sub.content, cleaned_trans)
            cleaned_trans = enforce_ellipsis_continuation(sub.content, cleaned_trans)
            cleaned_trans = enforce_continuation_casing(sub.content, cleaned_trans, language)

            if sub.content and not cleaned_trans:
                logger.warning(
                    f"⚠️  Cleaning removed all content for: '{sub.content}' (was: '{translation}')"
                )

            cleaned.append(cleaned_trans)

        return cleaned
