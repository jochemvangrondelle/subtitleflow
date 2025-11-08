# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Smart batching utilities for subtitle translation."""

import re

from subtitleflow.common.models.subtitle import Subtitle


def is_sentence_start(text: str) -> bool:
    """Check if text starts a complete sentence (not a continuation).

    Returns True if it starts with a capital letter or caption/speaker label.
    Returns False if it starts with ellipsis or lowercase (indicating continuation).

    Args:
        text: The subtitle text to check

    Returns:
        True if this is a sentence start, False if it's a continuation
    """
    if not text:
        return False

    stripped = text.lstrip()

    # Skip captions and speaker labels to check actual content
    # Pattern: [caption] or SPEAKER:
    if stripped.startswith("["):
        # Caption, skip to after closing bracket
        bracket_end = stripped.find("]")
        if bracket_end > 0:
            stripped = stripped[bracket_end + 1 :].lstrip()
    elif re.match(r"^[A-Z][A-Z\s]+:\s*", stripped):
        # Speaker label, skip to after colon
        colon_pos = stripped.find(":")
        if colon_pos > 0:
            stripped = stripped[colon_pos + 1 :].lstrip()

    if not stripped:
        return True  # Empty after labels, treat as valid start

    # Check if starts with ellipsis (continuation)
    if stripped.startswith("..."):
        return False

    # Check if first character is uppercase
    for char in stripped:
        if char.isalpha():
            return char.isupper()

    return True  # No alphabetic characters, treat as valid


def is_sentence_end(text: str) -> bool:
    """Check if text ends a complete sentence (not continued in next subtitle).

    Returns False if it ends with ellipsis, comma, semicolon, or colon.

    Args:
        text: The subtitle text to check

    Returns:
        True if this is a sentence end, False if it continues
    """
    if not text:
        return True

    stripped = text.rstrip()

    # Ends with continuation markers
    return not (stripped.endswith(("...", ",", ";", ":")))


def create_smart_batches(subtitles: list[Subtitle], batch_size: int = 10) -> list[list[Subtitle]]:
    """Create smart batches of subtitles that respect sentence boundaries.

    Groups subtitles into batches, ensuring each batch starts with a complete
    sentence and ends on a complete sentence when possible. Target size is
    batch_size, but may be adjusted to respect boundaries.

    Args:
        subtitles: List of subtitle objects to batch
        batch_size: Target number of subtitles per batch (default 10)

    Returns:
        List of batches, where each batch is a list of Subtitle objects
    """
    batches = []
    i = 0

    while i < len(subtitles):
        # Find a valid start (complete sentence beginning)
        while i < len(subtitles) and not is_sentence_start(subtitles[i].content):
            # Skip continuations at the start, include them with previous batch if possible
            if batches:
                batches[-1].append(subtitles[i])
            i += 1

        if i >= len(subtitles):
            break

        # Start a new batch
        batch = [subtitles[i]]
        i += 1

        # Add subtitles up to batch_size
        while len(batch) < batch_size and i < len(subtitles):
            batch.append(subtitles[i])
            i += 1

        # If we hit batch_size, try to extend to next complete sentence
        # (but don't go beyond batch_size + 3 to avoid too large batches)
        if len(batch) >= batch_size and i < len(subtitles):
            last_text = batch[-1].content
            if not is_sentence_end(last_text):
                # Last subtitle is incomplete, try to include continuations
                extension_count = 0
                while i < len(subtitles) and extension_count < 3:
                    batch.append(subtitles[i])
                    extension_count += 1
                    if is_sentence_end(subtitles[i].content):
                        i += 1
                        break
                    i += 1

        batches.append(batch)

    return batches


def format_batch_for_translation(subtitles: list[Subtitle]) -> str:
    """Format a batch of subtitles for translation with numbering.

    Args:
        subtitles: List of subtitle objects to format

    Returns:
        Formatted string with numbered subtitles like:
        1. subtitle text
        2. subtitle text
        etc.
    """
    lines = []
    for i, sub in enumerate(subtitles, start=1):
        lines.append(f"{i}. {sub.content}")
    return "\n".join(lines)


def parse_batch_response(response: str, expected_count: int) -> list[str]:
    """Parse a numbered batch translation response back into individual translations.

    Args:
        response: The model's response with numbered translations like "1. text"
        expected_count: How many translations we expect

    Returns:
        List of translation strings (may be partial if some items are missing)
        Returns empty list only if no valid numbered items found at all
    """
    import logging

    logger = logging.getLogger(__name__)

    translations = []

    # Debug: log full response with visible newlines
    response_visible = response.replace("\n", "\\n\n")
    logger.log(5, f"Parsing FULL response ({len(response)} chars):")
    logger.log(5, f"{response_visible}")

    # Try to split by numbered markers "N. " where N is a number
    # Pattern: N. followed by content until next N+1. or end
    # CRITICAL: The numbered pattern must be at START of line (after \n or at start ^)
    # This prevents matching numbers that appear mid-line in the content
    for i in range(1, expected_count + 1):
        # Look for "i. " at line start and capture until "i+1. " at line start or end
        # (?:^|\n) ensures we only match numbers at the beginning of a line
        if i < expected_count:
            # Match from "i. " to just before the next "\ni+1. " (at line start)
            # Use negative lookahead to stop BEFORE we hit the next numbered item
            pattern = rf"(?:^|\n){i}\.\s+(.*?)(?=\n{i + 1}\.\s+|\Z)"
        else:
            # Last item: match from "i. " to end
            pattern = rf"(?:^|\n){i}\.\s+(.*?)(?:\Z)"

        logger.log(5, f"Looking for item {i} with pattern: {pattern[:80]}...")
        match = re.search(pattern, response, re.DOTALL | re.MULTILINE)
        if match:
            translation = match.group(1).strip()
            translations.append(translation)
            logger.log(5, f"Parsed item {i}: {translation[:50]}...")
        else:
            # Failed to find this number
            logger.log(5, f"Failed to find item {i} in response")

            # Special case: if this is the last item and we have some translations,
            # check if there's unnumbered text at the end that could be the missing item
            if i == expected_count and translations:
                # Get the last successfully parsed item's end position
                last_pattern = rf"(?:^|\n){i - 1}\.\s+(.*?)(?:\Z)"
                last_match = re.search(last_pattern, response, re.DOTALL | re.MULTILINE)
                if last_match:
                    # Everything after the last numbered item
                    remaining = response[last_match.end() :].strip()
                    if remaining and not remaining.startswith(f"{i}."):
                        # Found unnumbered text - assume it's the last item
                        logger.log(5, f"Found unnumbered text for item {i}: {remaining[:50]}...")
                        translations.append(remaining)
                        break

            # Return partial results (caller will handle missing items)
            break

    # Return partial or complete results (empty list only if nothing found)
    return translations
