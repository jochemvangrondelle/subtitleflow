# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Batch translation service for improved performance."""

import logging
from collections.abc import Callable

from subtitleflow.common.clients.ollama import OllamaClient
from subtitleflow.common.constants.messages import MSG_BATCH_PROCESSING
from subtitleflow.common.models.subtitle import Subtitle
from subtitleflow.common.services.cache import CacheService
from subtitleflow.common.utils.batching import create_smart_batches
from subtitleflow.common.utils.context_builder import build_translation_context
from subtitleflow.common.utils.display import log_translation_batch
from subtitleflow.common.utils.music_separator import (
    reconstruct_with_music,
    separate_music_from_subtitles,
)
from subtitleflow.translate.batch_processor import TranslationBatchProcessor

logger = logging.getLogger(__name__)


class BatchTranslator:
    """Handles batch translation of multiple subtitles with smart batching."""

    def __init__(
        self, client: OllamaClient, batch_size: int = 10, cache: CacheService | None = None
    ) -> None:
        """
        Initialize batch translator.

        Args:
            client: Ollama client for API calls
            batch_size: Number of subtitles per batch (default 10)
            cache: Optional cache service for translation caching
        """
        self.client = client
        self.batch_size = batch_size
        self.cache = cache
        self.processor = TranslationBatchProcessor(client, cache)

    def translate_all(
        self,
        subtitles: list[Subtitle],
        model: str,
        language: str,
        context_window: int = 3,
        previous_translations: list[str] | None = None,
        display_callback: Callable | None = None,
    ) -> list[str]:
        """
        Translate all subtitles using smart batching.

        Args:
            subtitles: List of all subtitles to translate
            model: Model name to use
            language: Target language
            context_window: Number of previous subtitles for context
            previous_translations: List of previous translations for continuity

        Returns:
            List of translated texts (one per subtitle)
        """
        if not subtitles:
            return []

        # Separate music lines
        music_indices, non_music_subtitles = separate_music_from_subtitles(subtitles)

        # Create batches
        batches = self._create_batches(non_music_subtitles)

        # Translate batches
        non_music_translations = self._translate_batches(
            batches, model, language, context_window, display_callback
        )

        # Reconstruct with music lines
        return reconstruct_with_music(subtitles, music_indices, non_music_translations)

    def _create_batches(
        self, non_music_subtitles: list[tuple[int, Subtitle]]
    ) -> list[list[Subtitle]]:
        """Create smart batches from non-music subtitles."""
        if not non_music_subtitles:
            return []

        just_subs = [sub for _, sub in non_music_subtitles]
        batches = create_smart_batches(just_subs, self.batch_size)
        logger.info(
            f"Created {len(batches)} smart batches for {len(non_music_subtitles)} non-music subtitles"
        )
        return batches

    def _translate_batches(
        self,
        batches: list[list[Subtitle]],
        model: str,
        language: str,
        context_window: int,
        display_callback: Callable | None = None,
    ) -> list[str]:
        """Translate all batches with context."""
        completed_translations: list[tuple[str, str]] = []
        non_music_translations: list[str] = []

        for batch_idx, batch in enumerate(batches):
            logger.info(
                MSG_BATCH_PROCESSING.format(
                    current=batch_idx + 1, total=len(batches), count=len(batch)
                )
            )

            # Build context
            context_lines, context_display = build_translation_context(
                completed_translations, context_window, language
            )

            # Translate batch
            batch_translations = self._process_batch(
                batch,
                model,
                language,
                context_lines,
                context_display,
                batch_idx,
                len(batches),
                display_callback,
            )

            # Update results
            non_music_translations.extend(batch_translations)
            for sub, translation in zip(batch, batch_translations, strict=False):
                completed_translations.append((sub.content, translation))

        return non_music_translations

    def _process_batch(
        self,
        batch: list[Subtitle],
        model: str,
        language: str,
        context_lines: str | None,
        context_display: list[tuple[int, str, str]],
        batch_idx: int,
        total_batches: int,
        display_callback: Callable | None = None,
    ) -> list[str]:
        """Process a single batch with error handling."""
        batch_translations = self.processor.translate_batch(batch, model, language, context_lines)

        # Handle failures
        if not batch_translations:
            return self._handle_batch_failure(batch, model, language, context_lines)
        if len(batch_translations) < len(batch):
            return self._handle_partial_batch(
                batch, batch_translations, model, language, context_lines
            )
        if len(batch_translations) > len(batch):
            logger.warning(
                f"⚠️  Too many results: got {len(batch_translations)}, expected {len(batch)}"
            )
            batch_translations = batch_translations[: len(batch)]

        # Log successful batch
        log_translation_batch(batch, batch_translations, context_display, language)

        # Optional Rich display (CLI only)
        if display_callback:
            display_callback(batch, batch_translations, context_display, language)

        return batch_translations

    def _handle_batch_failure(
        self, batch: list[Subtitle], model: str, language: str, context_lines: str | None
    ) -> list[str]:
        """Handle complete batch failure by translating individually."""
        logger.warning(
            f"⚠️  Batch parsing completely failed, translating all {len(batch)} as single-item batches..."
        )
        batch_translations: list[str] = []
        for sub in batch:
            single_result = self.processor.translate_batch([sub], model, language, context_lines)
            if single_result:
                batch_translations.append(single_result[0])
            else:
                logger.error(f"❌ Failed to translate: {sub.content[:50]}...")
                batch_translations.append(sub.content)
        return batch_translations

    def _handle_partial_batch(
        self,
        batch: list[Subtitle],
        batch_translations: list[str],
        model: str,
        language: str,
        context_lines: str | None,
    ) -> list[str]:
        """Handle partial batch success by translating missing items."""
        missing_count = len(batch) - len(batch_translations)
        logger.warning(
            f"⚠️  Batch parsing incomplete: got {len(batch_translations)}/{len(batch)} translations, "
            f"translating {missing_count} missing items..."
        )

        for i in range(len(batch_translations), len(batch)):
            single_result = self.processor.translate_batch(
                [batch[i]], model, language, context_lines
            )
            if single_result:
                batch_translations.append(single_result[0])
            else:
                logger.error(f"❌ Failed to translate: {batch[i].content[:50]}...")
                batch_translations.append(batch[i].content)

        logger.info("✓ Completed batch with partial results + individual translations")
        return batch_translations
