# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Complete tests for BatchTranslator service."""

from datetime import timedelta
from unittest.mock import Mock

from subtitleflow.common.models.subtitle import Subtitle
from subtitleflow.translate.batch_translator import BatchTranslator


class TestBatchTranslator:
    """Test BatchTranslator service."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.mock_client = Mock()
        self.batch_translator = BatchTranslator(
            self.mock_client, batch_size=2
        )  # Smaller batch size for testing

    def test_init(self) -> None:
        """Test BatchTranslator initialization."""
        assert self.batch_translator.client == self.mock_client
        assert self.batch_translator.batch_size == 2  # Matches setup_method

    def test_translate_all_empty_list(self) -> None:
        """Test translate_all with empty subtitle list."""
        result = self.batch_translator.translate_all([], "test-model", "dutch")
        assert result == []

    def test_translate_all_single_subtitle(self) -> None:
        """Test translate_all with single subtitle."""
        subtitle = Subtitle(
            index=1,
            start=timedelta(seconds=0),
            end=timedelta(seconds=1),
            content="Hello world",
        )
        # Mock the processor.translate_batch method
        self.batch_translator.processor.translate_batch = Mock(return_value=["Hallo wereld"])

        result = self.batch_translator.translate_all([subtitle], "test-model", "dutch")

        assert result == ["Hallo wereld"]
        self.batch_translator.processor.translate_batch.assert_called()

    def test_translate_all_multiple_subtitles(self) -> None:
        """Test translate_all with multiple subtitles."""
        subtitles = [
            Subtitle(
                index=1,
                start=timedelta(seconds=0),
                end=timedelta(seconds=1),
                content="Hello world",
            ),
            Subtitle(
                index=2,
                start=timedelta(seconds=1),
                end=timedelta(seconds=2),
                content="How are you?",
            ),
            Subtitle(
                index=3,
                start=timedelta(seconds=2),
                end=timedelta(seconds=3),
                content="Good morning",
            ),
        ]

        # Mock the processor.translate_batch method to return results based on batch size
        # Track which translations have been returned
        translations = ["Hallo wereld", "Hoe gaat het?", "Goedemorgen"]
        translation_index = [0]  # Use list to allow modification in nested function

        def mock_translate_batch(batch, *args, **kwargs):
            batch_size = len(batch)
            result = translations[translation_index[0] : translation_index[0] + batch_size]
            translation_index[0] += batch_size
            return result

        self.batch_translator.processor.translate_batch = Mock(side_effect=mock_translate_batch)

        result = self.batch_translator.translate_all(subtitles, "test-model", "dutch")

        expected = ["Hallo wereld", "Hoe gaat het?", "Goedemorgen"]
        assert result == expected

    def test_translate_all_with_music_lines(self) -> None:
        """Test translate_all preserves music lines."""
        subtitles = [
            Subtitle(
                index=1,
                start=timedelta(seconds=0),
                end=timedelta(seconds=1),
                content="Hello world",
            ),
            Subtitle(
                index=2,
                start=timedelta(seconds=1),
                end=timedelta(seconds=2),
                content="♪ Music line ♪",
            ),
            Subtitle(
                index=3,
                start=timedelta(seconds=2),
                end=timedelta(seconds=3),
                content="How are you?",
            ),
        ]

        # Mock the processor.translate_batch method
        self.batch_translator.processor.translate_batch = Mock(
            return_value=["Hallo wereld", "Hoe gaat het?"]
        )

        result = self.batch_translator.translate_all(subtitles, "test-model", "dutch")

        # Music line should be preserved as-is
        assert result == ["Hallo wereld", "♪ Music line ♪", "Hoe gaat het?"]

    def test_translate_all_with_context(self) -> None:
        """Test translate_all uses context window."""
        subtitles = [
            Subtitle(
                index=i,
                start=timedelta(seconds=i),
                end=timedelta(seconds=i + 1),
                content=f"Subtitle {i}",
            )
            for i in range(1, 6)
        ]

        # Mock the processor.translate_batch method
        self.batch_translator.processor.translate_batch = Mock(
            side_effect=[
                ["Trans 1", "Trans 2"],
                ["Trans 3", "Trans 4"],
                ["Trans 5"],
            ]
        )

        result = self.batch_translator.translate_all(
            subtitles, "test-model", "dutch", context_window=2
        )

        assert len(result) == 5
        # Verify processor was called
        assert self.batch_translator.processor.translate_batch.call_count >= 1
