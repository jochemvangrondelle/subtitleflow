# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Context building utilities for grammar correction."""

from subtitleflow.common.utils.music_detection import is_music_line


def build_context_lines(
    completed_corrections: list[tuple[str, str]],
    context_window: int,
) -> str | None:
    """
    Build context lines string from completed corrections.

    Args:
        completed_corrections: List of (original, corrected) tuples
        context_window: Number of previous corrections to include

    Returns:
        Context lines string or None if no context
    """
    if not completed_corrections or context_window <= 0:
        return None

    # Filter out music lines from context
    non_music_context = [
        (orig, corr) for orig, corr in completed_corrections if not is_music_line(orig)
    ]

    if not non_music_context:
        return None

    start_idx = max(0, len(non_music_context) - context_window)
    context_items = non_music_context[start_idx:]

    context_parts = []
    for i, (_orig_text, corr_text) in enumerate(context_items):
        neg_idx = -(len(context_items) - i)
        context_parts.append(f"{neg_idx}. {corr_text}")

    return "\n".join(context_parts) if context_parts else None


def build_context_display(
    completed_corrections: list[tuple[str, str]],
    context_window: int,
) -> list[tuple[int, str, str]]:
    """
    Build context display items for Rich tables.

    Args:
        completed_corrections: List of (original, corrected) tuples
        context_window: Number of previous corrections to include

    Returns:
        List of (negative_index, original, corrected) tuples
    """
    if not completed_corrections or context_window <= 0:
        return []

    # Filter out music lines from context
    non_music_context = [
        (orig, corr) for orig, corr in completed_corrections if not is_music_line(orig)
    ]

    if not non_music_context:
        return []

    start_idx = max(0, len(non_music_context) - context_window)
    context_items = non_music_context[start_idx:]

    context_display = []
    for i, (orig_text, corr_text) in enumerate(context_items):
        neg_idx = -(len(context_items) - i)
        context_display.append((neg_idx, orig_text, corr_text))

    return context_display
