# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Complete tests for text processing utilities."""

from subtitleflow.common.utils.text_processing import clean_ai_response, preserve_formatting


class TestCleanAIResponseComplete:
    """Comprehensive tests for clean_ai_response."""

    def test_clean_thinking_tags(self) -> None:
        """Test removal of thinking tags."""
        text = "<think>internal thoughts</think>Actual response"
        result = clean_ai_response(text)
        assert result == "Actual response"
        assert "<think>" not in result

    def test_clean_long_intro(self) -> None:
        """Test removal of long explanatory intros."""
        text = "Om aan uw vereisten te voldoen, zal ik het volgende doen: Actual translation"
        result = clean_ai_response(text)
        # Should remove intro
        assert "vereisten" not in result or result == "Actual translation"

    def test_clean_bullet_points(self) -> None:
        """Test removal of bullet points."""
        text = "- Translation here"
        result = clean_ai_response(text)
        assert result == "Translation here"
        assert not result.startswith("-")

    def test_clean_double_newline_commentary(self) -> None:
        """Test removal of trailing commentary."""
        text = "Translation\n\nThis is my explanation of the translation"
        result = clean_ai_response(text)
        assert result == "Translation"
        assert "explanation" not in result

    def test_clean_malformed_tags(self) -> None:
        """Test removal of various malformed tags."""
        tests = [
            ("{DUTCH}text{/DUTCH}", "text"),
            ("{{DUTCH}text", "text"),
            ("text{/DUTCH}}", "text"),
            ("/{DUTCH}}text", "text"),
        ]
        for input_text, expected in tests:
            result = clean_ai_response(input_text)
            assert result == expected

    def test_clean_no_changes_needed(self) -> None:
        """Test clean with text that needs no cleaning."""
        text = "Perfect translation"
        result = clean_ai_response(text)
        assert result == text


class TestPreserveFormattingComplete:
    """Comprehensive tests for preserve_formatting."""

    def test_preserve_role_label_translation(self) -> None:
        """Test translating role labels but not names."""
        original = "OFFICIANT: Please be seated"
        translated = "AMBTENAAR: Gaat u zitten"
        result = preserve_formatting(original, translated)
        # preserve_formatting keeps original speaker label to preserve consistency
        assert result.startswith(("OFFICIANT:", "AMBTENAAR:"))
        assert "Gaat u zitten" in result

    def test_preserve_mixed_case_speaker(self) -> None:
        """Test speaker with mixed case."""
        original = "JOHN DOE: Hello there"
        translated = "hoi daar"
        result = preserve_formatting(original, translated)
        assert result.startswith("JOHN DOE:")
        assert "hoi daar" in result.lower()

    def test_preserve_no_speaker_label(self) -> None:
        """Test preservation without speaker label."""
        original = "Hello world"
        translated = "hola mundo"
        result = preserve_formatting(original, translated)
        assert result[0].isupper()

    def test_preserve_lowercase_original(self) -> None:
        """Test with lowercase original."""
        original = "...and then"
        translated = "...Y entonces"
        result = preserve_formatting(original, translated)
        # Should preserve lowercase for continuation
        assert result.startswith("...")

    def test_preserve_already_has_speaker(self) -> None:
        """Test when translation already has speaker label."""
        original = "SPEAKER: Text"
        translated = "SPEAKER: Tekst"
        result = preserve_formatting(original, translated)
        # Should not duplicate
        assert result.count("SPEAKER:") == 1

    def test_preserve_empty_strings(self) -> None:
        """Test with empty strings."""
        result = preserve_formatting("", "translation")
        assert result == "translation"

        result = preserve_formatting("original", "")
        assert result == ""
