# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Deduplication logic for subtitle correction."""

import logging

from subtitleflow.common.models.subtitle import Subtitle
from subtitleflow.common.utils.music_detection import is_music_line
from subtitleflow.common.utils.subtitle_utils import (
    is_caption_line,
    is_duplicate_subtitle,
)

logger = logging.getLogger(__name__)


def remove_duplicates(subtitles: list[Subtitle]) -> tuple[list[Subtitle], set[int]]:
    """
    Remove consecutive duplicate subtitles.

    Args:
        subtitles: List of subtitles to deduplicate

    Returns:
        Tuple of (deduplicated subtitles, set of removed indices)
    """
    deduplicated: list[Subtitle] = []
    duplicate_indices: set[int] = set()

    for idx, subtitle in enumerate(subtitles):
        # Skip duplicate detection for music and captions
        if is_music_line(subtitle.content) or is_caption_line(subtitle.content):
            deduplicated.append(subtitle)
            continue

        if idx > 0:
            previous = subtitles[idx - 1]
            # Only check for duplicates in non-music, non-caption lines
            if not is_music_line(previous.content) and not is_caption_line(previous.content):
                if is_duplicate_subtitle(subtitle.content, previous.content):
                    duplicate_indices.add(idx)
                    logger.debug(
                        f"Removing duplicate subtitle at index {idx}: '{subtitle.content[:60]}'"
                    )
                    continue

        deduplicated.append(subtitle)

    if duplicate_indices:
        logger.info(f"Removed {len(duplicate_indices)} consecutive duplicate subtitles")
        logger.debug(f"Duplicate indices: {sorted(duplicate_indices)}")

    return deduplicated, duplicate_indices


def separate_music_lines(
    subtitles: list[Subtitle],
) -> tuple[dict[int, str], list[tuple[int, Subtitle]]]:
    """
    Separate music lines from regular subtitles.

    Args:
        subtitles: List of subtitles to separate

    Returns:
        Tuple of (music_indices dict, list of (index, subtitle) for non-music)
    """
    music_indices: dict[int, str] = {}
    non_music_subtitles: list[tuple[int, Subtitle]] = []

    for idx, subtitle in enumerate(subtitles):
        if is_music_line(subtitle.content):
            music_indices[idx] = subtitle.content
            logger.debug(f"Skipping music line at index {idx}: {subtitle.content[:50]}")
        else:
            non_music_subtitles.append((idx, subtitle))

    logger.info(
        f"Found {len(music_indices)} music lines (will skip correction), "
        f"{len(non_music_subtitles)} regular subtitles"
    )

    return music_indices, non_music_subtitles
