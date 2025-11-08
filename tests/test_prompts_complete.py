# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Complete tests for prompts module."""

from subtitleflow.common.constants.prompts import (
    GRAMMAR_INSTR,
    JUDGE_INSTR,
    TRANSLATE_INSTR,
)
from subtitleflow.common.utils.prompts import build_prompt


class TestPrompts:
    """Test prompt constants and functions."""

    def test_grammar_instr_exists(self) -> None:
        """Test GRAMMAR_INSTR constant exists and has content."""
        assert GRAMMAR_INSTR is not None
        assert len(GRAMMAR_INSTR) > 100
        assert "grammar" in GRAMMAR_INSTR.lower()

    def test_judge_instr_exists(self) -> None:
        """Test JUDGE_INSTR constant exists and has content."""
        assert JUDGE_INSTR is not None
        assert len(JUDGE_INSTR) > 100
        assert "judge" in JUDGE_INSTR.lower() or "evaluator" in JUDGE_INSTR.lower()

    def test_translate_instr_exists(self) -> None:
        """Test TRANSLATE_INSTR constant exists and has content."""
        assert TRANSLATE_INSTR is not None
        assert len(TRANSLATE_INSTR) > 100
        assert "translate" in TRANSLATE_INSTR.lower()

    def test_build_prompt_single_language(self) -> None:
        """Test build_prompt with single language."""
        text = "Hello world"
        ctx_before = ["Previous line"]

        result = build_prompt(TRANSLATE_INSTR, text, ctx_before, lang="dutch")

        assert "Hello world" in result
        assert "dutch" in result
        assert "Previous line" in result
        assert "Subtitle to process:" in result

    def test_build_prompt_multi_language(self) -> None:
        """Test build_prompt with multiple languages."""
        text = "Hello world"
        ctx_before = ["Previous line"]
        langs = ["dutch", "spanish"]

        result = build_prompt(TRANSLATE_INSTR, text, ctx_before, langs=langs)

        assert "Hello world" in result
        assert "dutch" in result
        assert "spanish" in result
        assert "Previous line" in result

    def test_build_prompt_no_language(self) -> None:
        """Test build_prompt without language (grammar mode)."""
        text = "Hello world"
        ctx_before = ["Previous line"]

        result = build_prompt(GRAMMAR_INSTR, text, ctx_before)

        assert "Hello world" in result
        assert "Previous line" in result
        assert "Subtitle to process:" in result

    def test_build_prompt_no_context(self) -> None:
        """Test build_prompt without context."""
        text = "Hello world"

        result = build_prompt(TRANSLATE_INSTR, text, [], lang="dutch")

        assert "Hello world" in result
        assert "dutch" in result
        assert "Previous English lines" not in result

    def test_build_prompt_with_translated_before(self) -> None:
        """Test build_prompt with translated_before context."""
        text = "Hello world"
        ctx_before = ["Previous line"]
        langs = ["dutch", "spanish"]
        translated_before = {
            "dutch": ["Hallo wereld", "Hoe gaat het?"],
            "spanish": ["Hola mundo", "¿Cómo estás?"],
        }

        result = build_prompt(
            TRANSLATE_INSTR,
            text,
            ctx_before,
            langs=langs,
            translated_before=translated_before,
        )

        assert "Hello world" in result
        assert "Hallo wereld" in result
        assert "Hoe gaat het?" in result
        assert "Hola mundo" in result
        assert "¿Cómo estás?" in result
        assert "Previously translated lines" in result

    def test_build_prompt_continuation_detection(self) -> None:
        """Test build_prompt detects continuation from comma."""
        text = "Hello world"
        ctx_before = ["Previous line,"]  # Ends with comma

        result = build_prompt(TRANSLATE_INSTR, text, ctx_before, lang="dutch")

        assert "CONTINUES that sentence" in result

    def test_build_prompt_no_continuation(self) -> None:
        """Test build_prompt without continuation detection."""
        text = "Hello world"
        ctx_before = ["Previous line."]  # Ends with period

        result = build_prompt(TRANSLATE_INSTR, text, ctx_before, lang="dutch")

        assert "CONTINUES that sentence" not in result

    def test_build_prompt_empty_text(self) -> None:
        """Test build_prompt with empty text."""
        text = ""
        ctx_before = ["Previous line"]

        result = build_prompt(TRANSLATE_INSTR, text, ctx_before, lang="dutch")

        assert "dutch" in result
        assert "Previous line" in result

    def test_build_prompt_none_text(self) -> None:
        """Test build_prompt with None text."""
        text = None
        ctx_before = ["Previous line"]

        result = build_prompt(TRANSLATE_INSTR, text, ctx_before, lang="dutch")

        assert "dutch" in result
        assert "Previous line" in result

    def test_build_prompt_long_context(self) -> None:
        """Test build_prompt with long context."""
        text = "Hello world"
        ctx_before = [f"Line {i}" for i in range(10)]

        result = build_prompt(TRANSLATE_INSTR, text, ctx_before, lang="dutch")

        assert "Hello world" in result
        assert "Line 0" in result
        assert "Line 9" in result

    def test_build_prompt_many_languages(self) -> None:
        """Test build_prompt with many languages."""
        text = "Hello world"
        ctx_before = ["Previous line"]
        langs = ["dutch", "spanish", "french", "german", "italian"]

        result = build_prompt(TRANSLATE_INSTR, text, ctx_before, langs=langs)

        assert "Hello world" in result
        for lang in langs:
            assert lang in result

    def test_build_prompt_special_characters(self) -> None:
        """Test build_prompt with special characters."""
        text = "Hello world! @#$%^&*()"
        ctx_before = ["Previous line with émojis 🎉"]

        result = build_prompt(TRANSLATE_INSTR, text, ctx_before, lang="dutch")

        assert "Hello world! @#$%^&*()" in result
        assert "Previous line with émojis 🎉" in result

    def test_build_prompt_unicode(self) -> None:
        """Test build_prompt with unicode text."""
        text = "测试中文"
        ctx_before = ["日本語のテスト"]

        result = build_prompt(TRANSLATE_INSTR, text, ctx_before, lang="dutch")

        assert "测试中文" in result
        assert "日本語のテスト" in result

    def test_build_prompt_instruction_formatting(self) -> None:
        """Test build_prompt properly formats instruction templates."""
        text = "Hello world"
        ctx_before = []

        # Test with instruction that has format placeholders
        result = build_prompt(TRANSLATE_INSTR, text, ctx_before, lang="dutch")

        # Should not have any unformatted placeholders
        assert "{lang}" not in result
        assert "dutch" in result

    def test_build_prompt_multi_language_formatting(self) -> None:
        """Test build_prompt properly formats multi-language instruction templates."""
        text = "Hello world"
        ctx_before = []
        langs = ["dutch", "spanish"]

        result = build_prompt(TRANSLATE_INSTR, text, ctx_before, langs=langs)

        # Should not have any unformatted placeholders
        assert "{langs}" not in result
        assert "{num_langs}" not in result
        assert "dutch" in result
        assert "spanish" in result
