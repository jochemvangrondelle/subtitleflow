# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Translate command implementation."""

import logging
from pathlib import Path

from rich.console import Console

from subtitleflow.cli.display import display_translation_batch
from subtitleflow.cli.services import create_services, create_translation_service
from subtitleflow.cli.validation import (
    validate_gpu,
    validate_input_file,
    validate_models,
    validate_ollama_server,
)
from subtitleflow.common.models.config import AppConfig
from subtitleflow.common.models.subtitle import Subtitle, SubtitleFile

logger = logging.getLogger(__name__)
console = Console()


def handle_translate(
    input_file: Path,
    output_file: Path,
    language: str,
    translation_models: str,
    judge_model: str,
    context_window: int,
    log_level: str,
    no_cache: bool,
) -> None:
    """
    Handle translate command.

    Args:
        input_file: Input SRT file
        output_file: Output SRT file
        language: Target language
        translation_models: Comma-separated translation models
        judge_model: Judge model name
        context_window: Context window size
        log_level: Logging level
        no_cache: Whether to disable cache
    """
    validate_input_file(input_file)

    # Setup configuration
    config = AppConfig.from_env()
    config.translation_models = [m.strip() for m in translation_models.split(",")]
    config.judge_model = judge_model
    config.context_window = context_window
    config.log_level = log_level

    # Initialize services
    client, cache, judge = create_services(config, no_cache)
    # Type checker has issues with tuple unpacking, so we use type: ignore
    translation_service = create_translation_service(config, client, cache, judge)  # type: ignore[arg-type]

    # Validate server and models
    validate_ollama_server(client)
    all_models = set(config.translation_models) | {config.judge_model}
    validate_models(client, list(all_models))
    validate_gpu(config, list(all_models))

    # Load and process
    logger.info(f"Loading subtitles from {input_file}...")
    subtitle_file = SubtitleFile.load(str(input_file))
    logger.info(f"✓ Loaded {len(subtitle_file)} subtitles")

    logger.info(f"Starting translation to {language}...")
    logger.info(f"Models: {', '.join(config.translation_models)}")
    logger.info(f"Judge: {config.judge_model}")

    # Create display callback for Rich output
    def display_callback(
        batch: list[Subtitle],
        translations: list[str],
        context_display: list[tuple[int, str, str]],
        language: str,
    ) -> None:
        """Display translation batch using Rich."""
        display_translation_batch(console, batch, translations, context_display, language)

    translated = translation_service.translate(  # type: ignore[assignment]
        subtitle_file, language, display_callback=display_callback
    )

    # Save output
    translated.save(str(output_file))
    logger.info("✓ Translation complete")
    logger.info(f"Output saved to: {output_file}")
