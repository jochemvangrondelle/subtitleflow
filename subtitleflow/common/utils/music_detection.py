# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Music detection and handling utilities."""


def is_music_line(text: str) -> bool:
    """Check if a line contains music markers."""
    return "♪" in text or "♫" in text


def split_music_and_text(text: str) -> tuple[bool, list[str], list[str], list[tuple[str, bool]]]:
    """
    Split subtitle text into music and non-music parts.

    Args:
        text: Subtitle text to split

    Returns:
        Tuple of (has_music, music_lines, text_lines, original_structure)
        where original_structure is a list of tuples: (line_text, is_music_bool)
    """
    lines = text.split("\n")
    music_lines = []
    text_lines = []
    structure = []

    for line in lines:
        if is_music_line(line):
            music_lines.append(line)
            structure.append((line, True))
        else:
            text_lines.append(line)
            structure.append((line, False))

    has_music = len(music_lines) > 0
    return has_music, music_lines, text_lines, structure


def reconstruct_with_translation(structure: list[tuple[str, bool]], translation: str) -> str:
    """
    Reconstruct the subtitle text with translated non-music parts.

    Args:
        structure: List of (original_line, is_music) tuples
        translation: Translated text for non-music lines (may be multi-line)

    Returns:
        Reconstructed subtitle text with music preserved and text translated
    """
    translated_lines = translation.split("\n")
    result_lines = []
    translated_idx = 0

    for original_line, is_music in structure:
        if is_music:
            # Keep music line as-is
            result_lines.append(original_line)
        # Use translated line
        elif translated_idx < len(translated_lines):
            result_lines.append(translated_lines[translated_idx])
            translated_idx += 1
        else:
            # Fallback: keep original if translation has fewer lines
            result_lines.append(original_line)

    return "\n".join(result_lines)
