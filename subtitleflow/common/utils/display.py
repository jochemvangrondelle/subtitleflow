# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Shared display utilities - logging-based (no Rich dependency)."""

import logging

from subtitleflow.common.models.subtitle import Subtitle

logger = logging.getLogger(__name__)


def log_translation_batch(
    batch: list[Subtitle],
    translations: list[str],
    context_display: list[tuple[int, str, str]],
    language: str,
) -> None:
    """
    Log translation batch information.

    Args:
        batch: Original subtitles
        translations: Translated texts
        context_display: Context items for display
        language: Target language
    """
    logger.info(f"Successfully parsed batch with {len(translations)} translations")

    # Log context if present
    if context_display:
        logger.debug("Context (previous translations):")
        for neg_idx, orig, trans in context_display:
            logger.debug(f"  {neg_idx}. {orig} -> {trans}")

    # Log current batch translations
    for i, (sub, translation) in enumerate(zip(batch, translations, strict=False), 1):
        original_display = sub.content.replace("\n", "\\n")
        translation_display = translation.replace("\n", "\\n")
        logger.info(f"  {i}. {original_display} -> {translation_display}")


def log_correction_batch(
    batch: list[Subtitle],
    corrections: list[str],
    batch_idx: int,
    total_batches: int,
    model_name: str,
) -> None:
    """
    Log correction batch information.

    Args:
        batch: Original subtitles
        corrections: Corrected texts
        batch_idx: Current batch index (0-based)
        total_batches: Total number of batches
        model_name: Name of the model used
    """
    logger.info(f"[{model_name}] Batch {batch_idx + 1}/{total_batches} corrections")

    for i, (sub, corr) in enumerate(zip(batch, corrections, strict=False), 1):
        no_change = sub.content == corr
        original_display = sub.content.replace("\n", "\\n")
        corrected_display = corr.replace("\n", "\\n")
        if no_change:
            logger.debug(f"  {i}. {original_display} (no change)")
        else:
            logger.info(f"  {i}. {original_display} -> {corrected_display}")


def log_context(
    context_items: list[tuple[int, str, str]],
    context_type: str = "corrections",
) -> None:
    """
    Log context information.

    Args:
        context_items: List of (index, original, corrected/translated) tuples
        context_type: Type of context ("corrections" or "translations")
    """
    if not context_items:
        return

    logger.debug(f"Context (previous {context_type}):")
    for neg_idx, orig, corr in context_items:
        logger.debug(f"  {neg_idx}. {orig} -> {corr}")
