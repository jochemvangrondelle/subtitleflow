# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Tests for utility functions."""

from subtitleflow.common.utils.music_detection import (
    is_music_line,
    reconstruct_with_translation,
    split_music_and_text,
)
from subtitleflow.common.utils.text_processing import clean_ai_response, preserve_formatting


class TestMusicDetection:
    """Tests for music detection utilities."""

    def test_is_music_line_with_notes(self) -> None:
        """Test music detection with note symbols."""
        assert is_music_line("♪ La la la ♪") is True
        assert is_music_line("♫ Music here ♫") is True
        assert is_music_line("Regular text") is False

    def test_split_music_and_text(self) -> None:
        """Test splitting mixed music and text."""
        text = "Hello world\n♪ Music ♪\nMore text"
        has_music, music_lines, text_lines, _structure = split_music_and_text(text)

        assert has_music is True
        assert len(music_lines) == 1
        assert len(text_lines) == 2
        assert "♪ Music ♪" in music_lines
        assert "Hello world" in text_lines

    def test_split_no_music(self) -> None:
        """Test splitting text with no music."""
        text = "Line 1\nLine 2"
        has_music, music_lines, text_lines, _structure = split_music_and_text(text)

        assert has_music is False
        assert len(music_lines) == 0
        assert len(text_lines) == 2

    def test_reconstruct_with_translation(self) -> None:
        """Test reconstructing text with translation."""
        structure = [("Hello", False), ("♪ Music ♪", True), ("World", False)]
        translation = "Hola\nMundo"

        result = reconstruct_with_translation(structure, translation)

        assert "♪ Music ♪" in result
        assert "Hola" in result
        assert "Mundo" in result


class TestTextProcessing:
    """Tests for text processing utilities."""

    def test_clean_ai_response_basic(self) -> None:
        """Test basic cleaning of AI response."""
        text = "  Translation: Hello world  "
        result = clean_ai_response(text)
        assert result == "Hello world"

    def test_clean_ai_response_with_quotes(self) -> None:
        """Test cleaning quoted responses."""
        text = '"Hello world"'
        result = clean_ai_response(text)
        assert result == "Hello world"

    def test_clean_ai_response_with_numbers(self) -> None:
        """Test cleaning numbered responses."""
        text = "1. Hello world"
        result = clean_ai_response(text)
        assert result == "Hello world"

    def test_clean_ai_response_with_tags(self) -> None:
        """Test cleaning language tags."""
        text = "{{DUTCH}}Hallo wereld{{/DUTCH}}"
        result = clean_ai_response(text)
        assert result == "Hallo wereld"

    def test_clean_ai_response_with_prefix(self) -> None:
        """Test cleaning common prefixes."""
        text = "Here is: The translation"
        result = clean_ai_response(text)
        assert result == "The translation"

    def test_clean_ai_response_duplication(self) -> None:
        """Test cleaning duplicated responses."""
        text = "Hello/Hello"
        result = clean_ai_response(text)
        assert result == "Hello"

    def test_preserve_formatting_with_speaker(self) -> None:
        """Test preserving speaker labels."""
        original = "JOHN: Hello there"
        translated = "john: hola"
        result = preserve_formatting(original, translated)

        assert result.startswith("JOHN:")
        assert "hola" in result.lower()

    def test_preserve_formatting_capitalization(self) -> None:
        """Test preserving capitalization."""
        original = "Hello world"
        translated = "hola mundo"
        result = preserve_formatting(original, translated)

        assert result[0].isupper()

    def test_preserve_formatting_lowercase_continuation(self) -> None:
        """Test preserving lowercase for continuations."""
        original = "...and then"
        translated = "...y entonces"
        result = preserve_formatting(original, translated)

        assert result.startswith("...")

    def test_preserve_formatting_speaker_removal(self) -> None:
        """Test removing duplicate speaker labels."""
        original = "SPEAKER: Hello"
        translated = "SPEAKER: Hola"
        result = preserve_formatting(original, translated)

        # Should keep speaker label but not duplicate it
        assert result.count("SPEAKER:") == 1
