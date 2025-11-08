# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Shared utilities for subtitle processing."""

import logging
import re

logger = logging.getLogger(__name__)


def is_duplicate_subtitle(current: str, previous: str, threshold: float = 0.98) -> bool:
    """
    Check if current subtitle is a duplicate of the previous one.

    Args:
        current: Current subtitle text
        previous: Previous subtitle text
        threshold: Similarity threshold (0.0-1.0), default 0.98 for 98% match

    Returns:
        True if current is a VERY SIMILAR duplicate of previous
    """

    # Normalize: remove punctuation and extra whitespace, lowercase
    # BUT keep speaker labels to distinguish different conversations
    def normalize(text: str) -> str:
        # Preserve speaker structure by keeping colons
        # Remove other punctuation
        text = re.sub(r"[^\w\s:]", "", text)
        # Lowercase and collapse whitespace
        return " ".join(text.lower().split())

    norm_current = normalize(current)
    norm_previous = normalize(previous)

    # Empty after normalization
    if not norm_current or not norm_previous:
        return False

    # Exact match after normalization (true duplicate)
    if norm_current == norm_previous:
        return True

    # For non-exact matches, require VERY high similarity (98%+)
    # This prevents false positives from multi-speaker subtitles with shared phrases
    # Use Levenshtein-like ratio: 2 * matches / (len1 + len2)
    matches = sum(1 for a, b in zip(norm_current, norm_previous, strict=False) if a == b)
    total_len = len(norm_current) + len(norm_previous)

    if total_len == 0:
        return False

    # Different lengths = probably different subtitles
    len_diff = abs(len(norm_current) - len(norm_previous))
    if len_diff > 5:  # Allow 5 char difference max
        logger.log(5, f"Length diff too large: {len_diff}")
        return False

    similarity = (2.0 * matches) / total_len

    logger.log(5, f"Similarity: {similarity:.2f} between '{current[:40]}' and '{previous[:40]}'")

    return similarity >= threshold


def is_caption_line(text: str) -> bool:
    """
    Check if line is a caption like [applause], [laughter], etc.

    Args:
        text: Text to check

    Returns:
        True if text is a caption line
    """
    stripped = text.strip()
    return bool(re.match(r"^\[.+\]$", stripped))
