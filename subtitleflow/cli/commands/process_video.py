# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Process video command implementation."""

import logging
import subprocess
from pathlib import Path

import typer

from subtitleflow.cli.validation import validate_input_file
from subtitleflow.common.models.config import get_language_code

logger = logging.getLogger(__name__)


def handle_process_video(
    video_file: Path,
    languages: str,
    skip_transcribe: bool,
    skip_grammar: bool,
    transcribe_model: str,
    log_level: str,
) -> None:
    """
    Handle process_video command.

    Args:
        video_file: Input video file
        languages: Comma-separated target languages
        skip_transcribe: Skip transcription if SRT exists
        skip_grammar: Skip grammar correction
        transcribe_model: WhisperX model for transcription
        log_level: Logging level
    """
    validate_input_file(video_file)

    base_name = video_file.stem
    video_dir = video_file.parent
    srt_file = video_dir / f"{base_name}.srt"
    corrected_file = video_dir / f"{base_name}.corrected.srt"

    # Step 1: Transcribe
    if not skip_transcribe and not srt_file.exists():
        logger.info("Step 1: Transcribing video...")
        subprocess.run(
            [
                "python",
                "-m",
                "subtitleflow",
                "transcribe",
                str(video_file),
                "--output",
                str(srt_file),
                "--model",
                transcribe_model,
                "--log-level",
                log_level,
            ],
            check=True,
        )
    elif srt_file.exists():
        logger.info(f"✓ Using existing subtitle file: {srt_file}")
    else:
        logger.error(f"❌ No subtitle file found and transcription skipped: {srt_file}")
        raise typer.Exit(1)

    # Step 2: Grammar correction
    working_file = srt_file
    if not skip_grammar:
        if corrected_file.exists():
            logger.info(f"✓ Using existing corrected file: {corrected_file}")
            working_file = corrected_file
        else:
            logger.info("Step 2: Fixing grammar...")
            subprocess.run(
                [
                    "python",
                    "-m",
                    "subtitleflow",
                    "fix",
                    str(srt_file),
                    str(corrected_file),
                    "--log-level",
                    log_level,
                ],
                check=True,
            )
            working_file = corrected_file
    else:
        logger.info("⏭️  Skipping grammar correction")

    # Step 3: Translate to each language
    lang_list = [lang.strip() for lang in languages.split(",")]
    logger.info(f"Step 3: Translating to {len(lang_list)} language(s)...")

    for lang in lang_list:
        lang_code = get_language_code(lang)
        output_file = video_dir / f"{base_name}.{lang_code}.srt"

        logger.info(f"🌍 Translating to {lang}...")
        subprocess.run(
            [
                "python",
                "-m",
                "subtitleflow",
                "translate",
                str(working_file),
                str(output_file),
                "--lang",
                lang,
                "--log-level",
                log_level,
            ],
            check=True,
        )

    # Log output files
    logger.info("✅ Processing complete!")
    logger.info("📁 Output files:")
    logger.info(f"   • Subtitle: {srt_file}")
    if corrected_file.exists():
        logger.info(f"   • Corrected: {corrected_file}")
    for lang in lang_list:
        lang_code = get_language_code(lang)
        output_file = video_dir / f"{base_name}.{lang_code}.srt"
        logger.info(f"   • {lang.title()}: {output_file}")
