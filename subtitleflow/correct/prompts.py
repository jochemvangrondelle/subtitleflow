# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Prompt building for grammar correction."""

from subtitleflow.common.constants.display import SEPARATOR_DOUBLE
from subtitleflow.common.constants.prompts import GRAMMAR_INSTR
from subtitleflow.common.models.subtitle import Subtitle
from subtitleflow.common.utils.batching import format_batch_for_translation


def build_grammar_prompt(
    subtitles: list[Subtitle],
    context_lines: str | None = None,
) -> tuple[str, int]:
    """
    Build grammar correction prompt for batch.

    Args:
        subtitles: List of subtitles to correct
        context_lines: Optional context lines string

    Returns:
        Tuple of (prompt string, max_tokens)
    """
    batch_text = format_batch_for_translation(subtitles)

    if context_lines:
        subtitle_list = f"""{SEPARATOR_DOUBLE}
CONTEXT (previous corrected subtitles for continuity - DO NOT OUTPUT THESE):
{context_lines}
{SEPARATOR_DOUBLE}

SUBTITLES TO CORRECT (numbered 1-{len(subtitles)}):
{batch_text}
{SEPARATOR_DOUBLE}"""
    else:
        subtitle_list = batch_text

    prompt = f"""{GRAMMAR_INSTR}

You will receive {len(subtitles)} numbered subtitles below.

{subtitle_list}

CRITICAL OUTPUT REQUIREMENTS:
✗ DO NOT echo back context lines
✗ DO NOT include original text in your response
✗ DO NOT use "=" or other separators
✓ Return ONLY the {len(subtitles)} numbered corrected lines

{SEPARATOR_DOUBLE}
YOUR CORRECTIONS (respond with ONLY these {len(subtitles)} numbered lines):
{SEPARATOR_DOUBLE}
1."""

    # Calculate appropriate max_tokens based on batch size
    # Each subtitle: ~50 tokens output max, add buffer for numbering/formatting
    max_tokens = min(len(subtitles) * 75 + 200, 2048)

    return prompt, max_tokens
