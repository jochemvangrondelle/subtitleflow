# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Text processing and cleaning utilities."""

import re


def clean_ai_response(text: str) -> str:
    """Clean up AI responses that may include unwanted prefixes, numbers, or commentary."""
    cleaned = text.strip()

    # Remove Qwen3 thinking tags if present (should be disabled but handle anyway)
    think_pattern = r"<think>.*?</think>\s*"
    cleaned = re.sub(think_pattern, "", cleaned, flags=re.DOTALL)

    # Handle DeepSeek-R1 reasoning output (extract conclusion/final answer)
    # DeepSeek-R1 thinking field often contains long reasoning followed by conclusion
    # Look for patterns like "Therefore, the answer is X" or "Final choice: X" at the end
    if len(cleaned) > 1000:  # Likely reasoning output if very long
        # Try to extract final conclusion (last paragraph or sentence)
        conclusion_patterns = [
            r"(?:Therefore|Thus|So|Hence|In conclusion|Final(?:ly)?)[,:]?\s+(.+?)(?:\n|$)",
            r"(?:The answer is|My choice is|I choose|I select)[:\s]+(.+?)(?:\n|$)",
            r"(?:Candidate|Choice|Option)[:\s]+(\d+)",
        ]
        for pattern in conclusion_patterns:
            match = re.search(pattern, cleaned, flags=re.IGNORECASE)
            if match:
                cleaned = match.group(1).strip()
                break
        else:
            # If no conclusion pattern found, take last non-empty line
            lines = [line.strip() for line in cleaned.split("\n") if line.strip()]
            if lines:
                cleaned = lines[-1]

    # Remove long explanatory introductions
    intro_patterns = [
        r"^.*?(?:vereisten|requirements|translation|translate|subtitle).*?[.:][\s\n]+",
        r"^.*?(?:zal ik|I will|Here is|Hierbij|Below).*?[.:][\s\n]+",
    ]
    for pattern in intro_patterns:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE | re.DOTALL)

    # Remove common prefixes
    patterns = [
        r"^(?:Translation|Translated|Result|Output|Answer|Here is|Here\'s):\s*",
        r"^(?:The translation is|The result is):\s*",
        r"^\d+\.\s+",
        r"^[-*]\s+",
    ]

    for pattern in patterns:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)

    # Remove quotes if the entire text is wrapped in them
    if cleaned.startswith('"') and cleaned.endswith('"'):
        cleaned = cleaned[1:-1]
    if cleaned.startswith("'") and cleaned.endswith("'"):
        cleaned = cleaned[1:-1]

    # Remove language tags like {{DUTCH}}...{{/DUTCH}} or {DUTCH}...{/DUTCH}
    # Also handle malformed tags
    tag_patterns = [
        r"\{\{([A-Z]+)\}\}(.*?)\{\{/\1\}\}",  # {{DUTCH}}...{{/DUTCH}}
        r"\{([A-Z]+)\}(.*?)\{/\1\}",  # {DUTCH}...{/DUTCH}
        r"\{\{?([A-Z]+)\}?\}",  # {{DUTCH}} or {DUTCH} at start
        r"\{/?([A-Z]+)\}?\}",  # {/DUTCH}} or {/DUTCH} at end
    ]
    for pattern in tag_patterns[:2]:  # First two patterns extract content
        cleaned = re.sub(pattern, r"\2", cleaned, flags=re.IGNORECASE | re.DOTALL)
    # Remove any remaining tag fragments
    for pattern in tag_patterns[2:]:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)

    # Remove duplicated responses (e.g., "Hello/Hello" -> "Hello")
    # Check for pattern like "text/text" where both parts are identical
    dup_pattern = r"^(.+?)/\1$"
    match = re.match(dup_pattern, cleaned)
    if match:
        cleaned = match.group(1)

    # Remove trailing commentary
    if "\n\n" in cleaned:
        cleaned = cleaned.split("\n\n")[0]

    return cleaned.strip()


def preserve_formatting(original: str, translated: str) -> str:
    """
    Ensure speaker labels and capitalization are preserved from original to translation.

    Args:
        original: Original English text
        translated: Translated text from AI

    Returns:
        Translated text with speaker label and capitalization preserved
    """
    # Check if original has a speaker label (NAME: pattern)
    speaker_match = re.match(r"^([A-Z][A-Z\s]+):\s*", original)

    if speaker_match:
        speaker_label = speaker_match.group(1) + ": "

        # Remove speaker label from translated if it exists (to avoid duplication)
        translated_no_speaker = re.sub(r"^([A-Z][A-Z\s]+):\s*", "", translated, count=1)

        # If speaker label was removed from translated, add original speaker label back
        if not translated.startswith(speaker_label):
            translated = speaker_label + translated_no_speaker.lstrip()

        # Get the text after speaker label in original
        original_after_speaker = original[len(speaker_label) :]
        translated_after_speaker = translated[len(speaker_label) :]

        # Preserve first character capitalization from original (after speaker)
        if original_after_speaker and translated_after_speaker:
            if original_after_speaker[0].isupper():
                translated_after_speaker = (
                    translated_after_speaker[0].upper() + translated_after_speaker[1:]
                )
            elif original_after_speaker[0].islower() and not translated_after_speaker[0].isupper():
                pass

            translated = speaker_label + translated_after_speaker
    # No speaker label, just preserve capitalization of first character
    elif original and translated:
        # Exception: if original starts with "..." (continuation), keep lowercase
        if not original.startswith("..."):
            if original[0].isupper() and translated[0].islower():
                translated = translated[0].upper() + translated[1:]
            elif original[0].islower() and translated[0].isupper():
                translated = translated[0].lower() + translated[1:]

    return translated


def enforce_ellipsis_continuation(original: str, translated: str) -> str:
    """
    Ensure ellipsis (...) at start/end of original are preserved in translation.
    Handles multi-line subtitles and captions.

    Args:
        original: Original English text
        translated: Translated text from AI

    Returns:
        Translated text with ellipsis properly preserved
    """
    if not original or not translated:
        return translated

    # Process line by line to handle multi-line subtitles
    original_lines = original.split("\n")
    translated_lines = translated.split("\n")

    # If line counts don't match, process as single block
    if len(original_lines) != len(translated_lines):
        # Fallback to simple single-text processing
        result = translated
        if original.startswith("...") and not result.startswith("..."):
            result = "..." + result
        if original.endswith("...") and not result.endswith("..."):
            result = result + "..."
        return result

    # Process each line pair
    result_lines = []
    for orig_line, trans_line in zip(original_lines, translated_lines, strict=False):
        # Skip captions/labels to check actual content
        orig_content = orig_line
        trans_content = trans_line

        # Check for captions [...]
        if orig_line.startswith("["):
            bracket_end = orig_line.find("]")
            if bracket_end > 0:
                orig_content = orig_line[bracket_end + 1 :].lstrip()
                # Find corresponding bracket in translation
                trans_bracket_end = trans_line.find("]")
                if trans_bracket_end > 0:
                    trans_prefix = trans_line[: trans_bracket_end + 1] + " "
                    trans_content = trans_line[trans_bracket_end + 1 :].lstrip()
                else:
                    trans_prefix = ""
            else:
                trans_prefix = ""
        else:
            trans_prefix = ""

        # Check for speaker labels SPEAKER:
        if re.match(r"^[A-Z][A-Z\s]+:\s*", orig_content):
            colon_pos = orig_content.find(":")
            if colon_pos > 0:
                orig_content = orig_content[colon_pos + 1 :].lstrip()
                trans_colon_pos = trans_content.find(":")
                if trans_colon_pos > 0:
                    speaker_part = trans_content[: trans_colon_pos + 1] + " "
                    trans_content = trans_content[trans_colon_pos + 1 :].lstrip()
                    trans_prefix += speaker_part

        # Now check ellipsis on the actual content
        if orig_content.startswith("...") and not trans_content.startswith("..."):
            trans_content = "..." + trans_content
        if orig_content.endswith("...") and not trans_content.endswith("..."):
            trans_content = trans_content + "..."

        # Reconstruct the line
        result_line = trans_prefix + trans_content if trans_prefix else trans_content
        result_lines.append(result_line)

    return "\n".join(result_lines)


def enforce_continuation_casing(original: str, translated: str, lang: str | None = None) -> str:
    """
    Ensure that if original starts with "...", the translation starts with lowercase
    (unless it's a speaker label).

    Args:
        original: Original English text
        translated: Translated text from AI
        lang: Target language (for language-specific rules)

    Returns:
        Translated text with proper continuation casing
    """
    if not original or not translated:
        return translated

    # Check if original starts with continuation
    if not original.lstrip().startswith("..."):
        return translated

    # Check if translation starts with speaker label - if so, leave it
    if re.match(r"^[A-Z][A-Z\s]+:\s*", translated):
        return translated

    # Check if translation starts with caption - if so, leave it
    if translated.lstrip().startswith("["):
        return translated

    # Find first alphabetic character and make it lowercase
    result = list(translated)
    for i, char in enumerate(result):
        if char.isalpha():
            if char.isupper():
                result[i] = char.lower()
            break

    return "".join(result)
