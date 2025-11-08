# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Shared batch caching and deduplication utilities."""

import logging
from typing import Any

from subtitleflow.common.models.subtitle import Subtitle
from subtitleflow.common.services.cache import CacheService

logger = logging.getLogger(__name__)


class BatchCache:
    """Handles batch-level caching and deduplication."""

    def __init__(self, cache: CacheService | None) -> None:
        """
        Initialize batch cache.

        Args:
            cache: Optional cache service
        """
        self.cache = cache

    def deduplicate_and_cache(
        self,
        batch: list[Subtitle],
        section: str,
        model: str,
        context_list: list[str],
        language: str | None = None,
    ) -> dict[str, Any]:
        """
        Deduplicate batch and check cache for each unique item.

        Args:
            batch: List of subtitles to process
            section: Cache section name ("translate" or "fix")
            model: Model name for cache key
            context_list: Context lines for cache key
            language: Optional language for cache key (for translation)

        Returns:
            Dict with keys: unique_subtitles, unique_map, position_map, cached_results
        """
        unique_subtitles: list[Subtitle] = []
        unique_map: dict[str, int] = {}
        position_map: list[int] = []
        cached_results: dict[int, str] = {}

        for sub in batch:
            content = sub.content
            if content not in unique_map:
                idx = len(unique_subtitles)
                unique_map[content] = idx
                unique_subtitles.append(sub)

                if self.cache:
                    cache_kwargs = {
                        "section": section,
                        "model": model,
                        "text": content,
                        "context_before": context_list,
                    }
                    if language:
                        cache_kwargs["language"] = language

                    cached = self.cache.get(**cache_kwargs)
                    if cached:
                        cached_results[idx] = cached
                        logger.debug(f"Cache HIT for {section}: {content[:50]}...")

            position_map.append(unique_map[content])

        if len(unique_subtitles) < len(batch):
            logger.debug(
                f"Deduplicated batch: {len(batch)} items → {len(unique_subtitles)} unique items"
            )
        if cached_results:
            logger.debug(
                f"Cache: {len(cached_results)}/{len(unique_subtitles)} items found in cache"
            )

        return {
            "unique_subtitles": unique_subtitles,
            "unique_map": unique_map,
            "position_map": position_map,
            "cached_results": cached_results,
        }

    def get_uncached_items(
        self,
        unique_subtitles: list[Subtitle],
        cached_results: dict[int, str],
    ) -> tuple[list[Subtitle], list[int]]:
        """
        Get uncached items from unique subtitles.

        Args:
            unique_subtitles: List of unique subtitles
            cached_results: Dict mapping index to cached result

        Returns:
            Tuple of (uncached_subtitles, uncached_indices)
        """
        uncached_subtitles: list[Subtitle] = []
        uncached_indices: list[int] = []

        for i, sub in enumerate(unique_subtitles):
            if i not in cached_results:
                uncached_indices.append(i)
                uncached_subtitles.append(sub)

        logger.debug(
            f"Sending {len(uncached_subtitles)}/{len(unique_subtitles)} uncached items to API"
        )

        return uncached_subtitles, uncached_indices

    def merge_results(
        self,
        unique_subtitles: list[Subtitle],
        cached_results: dict[int, str],
        uncached_subtitles: list[Subtitle],
        uncached_indices: list[int],
        uncached_results: list[str],
        section: str,
        model: str,
        context_list: list[str],
        language: str | None = None,
    ) -> dict[int, str]:
        """
        Merge cached and fresh results.

        Args:
            unique_subtitles: List of unique subtitles
            cached_results: Dict of cached results
            uncached_subtitles: List of uncached subtitles
            uncached_indices: List of uncached indices
            uncached_results: List of fresh results from API
            section: Cache section name
            model: Model name
            context_list: Context lines
            language: Optional language

        Returns:
            Dict mapping unique index to result
        """
        unique_results: dict[int, str] = {}
        unique_results.update(cached_results)

        for i, uncached_idx in enumerate(uncached_indices):
            if i < len(uncached_results):
                result = uncached_results[i]
                unique_results[uncached_idx] = result

                if self.cache:
                    cache_kwargs = {
                        "section": section,
                        "model": model,
                        "text": uncached_subtitles[i].content,
                        "context_before": context_list,
                        "value": result,
                    }
                    if language:
                        cache_kwargs["language"] = language

                    self.cache.set(**cache_kwargs)

        return unique_results

    def map_to_batch_order(
        self,
        batch: list[Subtitle],
        position_map: list[int],
        unique_results: dict[int, str],
    ) -> list[str]:
        """
        Map unique results back to batch order.

        Args:
            batch: Original batch
            position_map: Map from batch index to unique index
            unique_results: Dict mapping unique index to result

        Returns:
            List of results in batch order
        """
        results: list[str] = []
        for i, pos in enumerate(position_map):
            if pos in unique_results:
                results.append(unique_results[pos])
            else:
                logger.warning(f"Missing result at position {pos}, using original")
                results.append(batch[i].content)

        return results
