# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Batch processing logic for grammar correction."""

import logging

from subtitleflow.common.clients.ollama import OllamaClient
from subtitleflow.common.constants.display import SEPARATOR_THIN
from subtitleflow.common.models.config import AppConfig
from subtitleflow.common.models.subtitle import Subtitle
from subtitleflow.common.services.cache import CacheService
from subtitleflow.common.utils.batch_cache import BatchCache
from subtitleflow.common.utils.batching import parse_batch_response
from subtitleflow.common.utils.text_processing import clean_ai_response, preserve_formatting
from subtitleflow.correct.prompts import build_grammar_prompt

logger = logging.getLogger(__name__)


class BatchCorrector:
    """Handles batch correction with caching and deduplication."""

    def __init__(
        self,
        config: AppConfig,
        client: OllamaClient,
        cache: CacheService | None,
    ) -> None:
        """
        Initialize batch corrector.

        Args:
            config: Application configuration
            client: Ollama client
            cache: Optional cache service
        """
        self.config = config
        self.client = client
        self.batch_cache = BatchCache(cache)

    def correct_batch(
        self,
        batch: list[Subtitle],
        context_lines: str | None = None,
        model: str | None = None,
    ) -> list[str]:
        """
        Correct a batch of subtitles with deduplication and caching.

        Args:
            batch: List of subtitles to correct
            context_lines: Optional context lines string
            model: Model name (uses first grammar model if None)

        Returns:
            List of corrected texts
        """
        if model is None:
            model = self.config.grammar_models[0]

        context_list = context_lines.split("\n") if context_lines else []

        # Deduplicate and check cache using shared utility
        cache_data = self.batch_cache.deduplicate_and_cache(
            batch=batch,
            section="fix",
            model=model,
            context_list=context_list,
        )

        unique_subtitles = cache_data["unique_subtitles"]
        position_map = cache_data["position_map"]
        cached_results = cache_data["cached_results"]

        # If all cached, return early
        if len(cached_results) == len(unique_subtitles):
            logger.debug(f"All {len(unique_subtitles)} items found in cache, skipping API call")
            return self.batch_cache.map_to_batch_order(batch, position_map, cached_results)

        # Get uncached items
        uncached_subtitles, uncached_indices = self.batch_cache.get_uncached_items(
            unique_subtitles, cached_results
        )

        # Correct uncached items
        uncached_corrections = self._correct_uncached(uncached_subtitles, context_lines, model)

        # Merge cached and fresh corrections
        unique_corrections = self.batch_cache.merge_results(
            unique_subtitles=unique_subtitles,
            cached_results=cached_results,
            uncached_subtitles=uncached_subtitles,
            uncached_indices=uncached_indices,
            uncached_results=uncached_corrections,
            section="fix",
            model=model,
            context_list=context_list,
        )

        # Map back to batch order
        corrections = self.batch_cache.map_to_batch_order(batch, position_map, unique_corrections)

        # Clean and preserve formatting
        return self._clean_corrections(batch, corrections)

    def _correct_uncached(
        self,
        uncached_subtitles: list[Subtitle],
        context_lines: str | None,
        model: str,
    ) -> list[str]:
        """Correct uncached subtitles via API."""
        prompt, max_tokens = build_grammar_prompt(uncached_subtitles, context_lines)

        logger.debug(
            f"[GRAMMAR_BATCH] Correcting {len(uncached_subtitles)} uncached items "
            f"(max_tokens={max_tokens})"
        )

        response = self.client.generate(model, prompt, temperature=0.2, max_tokens=max_tokens)

        logger.debug(f"{SEPARATOR_THIN} RAW RESPONSE FROM [{model}] {SEPARATOR_THIN}")
        logger.debug(f"{response}")
        logger.debug(f"{SEPARATOR_THIN} END RAW RESPONSE {SEPARATOR_THIN}")

        return parse_batch_response(response, len(uncached_subtitles))

    def _clean_corrections(
        self,
        batch: list[Subtitle],
        corrections: list[str],
    ) -> list[str]:
        """Clean corrections and preserve formatting."""
        if not corrections:
            logger.warning(f"⚠️  Batch parsing failed for {len(batch)} subtitles")
            return []

        if len(corrections) < len(batch):
            logger.warning(f"⚠️  Partial parse: got {len(corrections)}/{len(batch)} corrections")

        cleaned_corrections: list[str] = []
        for i, (sub, corr) in enumerate(zip(batch, corrections, strict=False)):
            if not corr or len(corr.strip()) == 0:
                logger.warning(f"⚠️  Empty correction for subtitle {i + 1}: '{sub.content}'")
                logger.debug(f"Raw correction was: '{corr}'")

            cleaned_corr = clean_ai_response(corr)
            cleaned_corr = preserve_formatting(sub.content, cleaned_corr)
            cleaned_corrections.append(cleaned_corr)

        return cleaned_corrections
