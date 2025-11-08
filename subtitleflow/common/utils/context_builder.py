# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Context building utilities for translation."""


def build_translation_context(
    completed_translations: list[tuple[str, str]],
    context_window: int,
    language: str,
) -> tuple[str | None, list[tuple[int, str, str]]]:
    """
    Build context lines and display items for translation.

    Args:
        completed_translations: List of (original, translation) tuples
        context_window: Number of previous items to include
        language: Target language

    Returns:
        Tuple of (context_lines string, context_display list)
    """
    if not completed_translations or context_window <= 0:
        return None, []

    start_idx = max(0, len(completed_translations) - context_window)
    context_items = completed_translations[start_idx:]

    context_parts: list[str] = []
    context_display: list[tuple[int, str, str]] = []

    for i, (orig_text, trans_text) in enumerate(context_items):
        neg_idx = -(len(context_items) - i)
        context_parts.append(f"{neg_idx}. {trans_text}")
        context_display.append((neg_idx, orig_text, trans_text))

    context_lines = "\n".join(context_parts) if context_parts else None
    return context_lines, context_display
