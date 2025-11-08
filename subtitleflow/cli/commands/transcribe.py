# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Transcribe command implementation."""

import logging
from pathlib import Path

import typer

from subtitleflow.cli.validation import validate_input_file
from subtitleflow.transcribe.service import TranscriptionService

logger = logging.getLogger(__name__)


def handle_transcribe(
    video_file: Path,
    output_file: Path | None,
    model: str,
    language: str,
    device: str,
    batch_size: int,
) -> None:
    """
    Handle transcribe command.

    Args:
        video_file: Input video file
        output_file: Output SRT file (auto-generated if None)
        model: WhisperX model name
        language: Language code
        device: Device (cuda or cpu)
        batch_size: Batch size for processing
    """
    validate_input_file(video_file)

    # Determine output file
    if output_file is None:
        output_file = video_file.parent / f"{video_file.stem}.srt"
    else:
        output_file = Path(output_file)

    logger.info(f"🎬 Transcribing: {video_file}")
    logger.info(f"📝 Output: {output_file}")

    # Use TranscriptionService
    transcription_service = TranscriptionService()
    try:
        transcription_service.transcribe(
            video_file=video_file,
            output_file=output_file,
            model=model,
            language=language,
            device=device,
            batch_size=batch_size,
        )
        logger.info(f"✅ Transcription complete: {output_file}")
    except ImportError:
        logger.exception(
            "❌ WhisperX not installed. Install with: pip install subtitleflow[transcribe]"
        )
        raise typer.Exit(1)
    except Exception as e:
        logger.exception(f"❌ Transcription error: {e}")
        raise typer.Exit(1)
