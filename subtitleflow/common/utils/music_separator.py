# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Utilities for separating music lines from regular subtitles."""

import logging

from subtitleflow.common.models.subtitle import Subtitle
from subtitleflow.common.utils.music_detection import is_music_line

logger = logging.getLogger(__name__)


def separate_music_from_subtitles(
    subtitles: list[Subtitle],
) -> tuple[list[int], list[tuple[int, Subtitle]]]:
    """
    Separate music lines from regular subtitles.

    Args:
        subtitles: List of subtitles to separate

    Returns:
        Tuple of (music_indices list, list of (index, subtitle) for non-music)
    """
    music_indices: list[int] = []
    non_music_subtitles: list[tuple[int, Subtitle]] = []

    for idx, sub in enumerate(subtitles):
        if is_music_line(sub.content):
            music_indices.append(idx)
        else:
            non_music_subtitles.append((idx, sub))

    logger.info(
        f"Found {len(music_indices)} music lines (will skip processing), "
        f"{len(non_music_subtitles)} regular subtitles"
    )

    return music_indices, non_music_subtitles


def reconstruct_with_music(
    subtitles: list[Subtitle],
    music_indices: list[int],
    processed_results: list[str],
) -> list[str]:
    """
    Reconstruct full result list with music lines in original positions.

    Args:
        subtitles: Original subtitles
        music_indices: List of indices that are music lines
        processed_results: Processed results for non-music subtitles

    Returns:
        Full list with music lines preserved
    """
    all_results: list[str] = []
    processed_idx = 0

    for idx in range(len(subtitles)):
        if idx in music_indices:
            all_results.append(subtitles[idx].content)
            logger.debug(f"Kept music line at index {idx}: {subtitles[idx].content[:50]}...")
        elif processed_idx < len(processed_results):
            all_results.append(processed_results[processed_idx])
            processed_idx += 1
        else:
            logger.error(f"❌ Ran out of processed results at idx={idx}")
            all_results.append(subtitles[idx].content)

    return all_results
