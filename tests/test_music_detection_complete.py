# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Complete tests for music detection utilities."""

from subtitleflow.common.utils.music_detection import (
    is_music_line,
    reconstruct_with_translation,
    split_music_and_text,
)


class TestMusicDetectionComplete:
    """Comprehensive tests for music detection."""

    def test_is_music_line_single_note(self) -> None:
        """Test detection with single musical note."""
        assert is_music_line("♪ Song ♪") is True
        assert is_music_line("♫ Music ♫") is True
        assert is_music_line("♪") is True
        assert is_music_line("♫") is True

    def test_is_music_line_mixed_text(self) -> None:
        """Test detection in mixed text."""
        assert is_music_line("Some text ♪ more text") is True
        assert is_music_line("♪ Start") is True
        assert is_music_line("End ♫") is True

    def test_split_only_music(self) -> None:
        """Test splitting text with only music."""
        text = "♪ La la la ♪"
        has_music, music_lines, text_lines, _structure = split_music_and_text(text)

        assert has_music is True
        assert len(music_lines) == 1
        assert len(text_lines) == 0
        assert music_lines[0] == "♪ La la la ♪"

    def test_split_only_text(self) -> None:
        """Test splitting text with no music."""
        text = "Just regular text\nMore text"
        has_music, music_lines, text_lines, _structure = split_music_and_text(text)

        assert has_music is False
        assert len(music_lines) == 0
        assert len(text_lines) == 2

    def test_split_mixed_multiple_lines(self) -> None:
        """Test splitting with multiple mixed lines."""
        text = "Regular line 1\n♪ Music line ♪\nRegular line 2\n♫ Music line 2 ♫"
        has_music, music_lines, text_lines, structure = split_music_and_text(text)

        assert has_music is True
        assert len(music_lines) == 2
        assert len(text_lines) == 2
        assert len(structure) == 4

    def test_reconstruct_simple(self) -> None:
        """Test reconstruction with simple structure."""
        structure = [
            ("Text line", False),
            ("♪ Music ♪", True),
        ]
        translation = "Translated line"

        result = reconstruct_with_translation(structure, translation)

        assert "Translated line" in result
        assert "♪ Music ♪" in result

    def test_reconstruct_multiple_text_lines(self) -> None:
        """Test reconstruction with multiple text lines."""
        structure = [
            ("Line 1", False),
            ("Line 2", False),
            ("♪ Music ♪", True),
        ]
        translation = "Translation 1\nTranslation 2"

        result = reconstruct_with_translation(structure, translation)

        assert "Translation 1" in result
        assert "Translation 2" in result
        assert "♪ Music ♪" in result

    def test_reconstruct_fewer_translations(self) -> None:
        """Test reconstruction when translation has fewer lines."""
        structure = [
            ("Line 1", False),
            ("Line 2", False),
            ("Line 3", False),
        ]
        translation = "Translation 1"

        result = reconstruct_with_translation(structure, translation)
        lines = result.split("\n")

        # Should use translation for first, keep original for rest
        assert lines[0] == "Translation 1"
        assert lines[1] == "Line 2"  # Fallback to original

    def test_reconstruct_only_music(self) -> None:
        """Test reconstruction with only music lines."""
        structure = [
            ("♪ Song 1 ♪", True),
            ("♫ Song 2 ♫", True),
        ]
        translation = ""

        result = reconstruct_with_translation(structure, translation)

        assert "♪ Song 1 ♪" in result
        assert "♫ Song 2 ♫" in result

    def test_reconstruct_preserves_order(self) -> None:
        """Test that reconstruction preserves original order."""
        structure = [
            ("Text 1", False),
            ("♪ Music 1 ♪", True),
            ("Text 2", False),
            ("♫ Music 2 ♫", True),
        ]
        translation = "Trans 1\nTrans 2"

        result = reconstruct_with_translation(structure, translation)
        lines = result.split("\n")

        assert lines[0] == "Trans 1"
        assert lines[1] == "♪ Music 1 ♪"
        assert lines[2] == "Trans 2"
        assert lines[3] == "♫ Music 2 ♫"
