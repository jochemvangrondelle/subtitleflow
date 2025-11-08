# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Fix command implementation."""

import logging
from pathlib import Path

from rich.console import Console

from subtitleflow.cli.display import display_correction_batch, display_judged_batch
from subtitleflow.cli.services import create_grammar_service, create_services
from subtitleflow.cli.validation import validate_input_file, validate_models, validate_ollama_server
from subtitleflow.common.models.config import AppConfig
from subtitleflow.common.models.subtitle import Subtitle, SubtitleFile

logger = logging.getLogger(__name__)
console = Console()


def handle_fix(
    input_file: Path,
    output_file: Path,
    grammar_models: str,
    judge_model: str,
    context_window: int,
    log_level: str,
    no_cache: bool,
) -> None:
    """
    Handle fix command.

    Args:
        input_file: Input SRT file
        output_file: Output SRT file
        grammar_models: Comma-separated grammar models
        judge_model: Judge model name
        context_window: Context window size
        log_level: Logging level
        no_cache: Whether to disable cache
    """
    validate_input_file(input_file)

    # Setup configuration
    config = AppConfig.from_env()
    config.grammar_models = [m.strip() for m in grammar_models.split(",")]
    config.judge_model = judge_model
    config.context_window = context_window
    config.log_level = log_level

    # Initialize services
    client, cache, judge = create_services(config, no_cache)
    grammar_service = create_grammar_service(config, client, cache, judge)

    # Validate server and models
    validate_ollama_server(client)
    all_models = set(config.grammar_models) | {config.judge_model}
    validate_models(client, list(all_models))

    # Load and process
    logger.info(f"Loading subtitles from {input_file}...")
    subtitle_file = SubtitleFile.load(str(input_file))
    logger.info(f"✓ Loaded {len(subtitle_file)} subtitles")

    logger.info("Starting grammar correction...")
    logger.info(f"Models: {', '.join(config.grammar_models)}")

    # Create display callbacks for Rich output
    def display_batch_callback(
        batch: list[Subtitle],
        corrections: list[str],
        batch_idx: int,
        total_batches: int,
        model: str,
    ) -> None:
        """Display batch corrections using Rich."""
        display_correction_batch(console, batch, corrections, batch_idx, total_batches, model)

    def display_judged_callback(
        batch: list[Subtitle],
        corrections: list[str],
        batch_idx: int,
        total_batches: int,
        context_display: list,
    ) -> None:
        """Display judged batch using Rich."""
        display_judged_batch(console, batch, corrections, batch_idx, total_batches, context_display)

    # Use a wrapper callback that handles both cases
    def display_callback(*args, **kwargs) -> None:
        """Unified display callback."""
        if len(args) == 5 and isinstance(args[4], str):  # Batch correction
            display_batch_callback(*args)
        elif len(args) == 5:  # Judged batch
            display_judged_callback(*args)

    corrected = grammar_service.correct(subtitle_file, display_callback=display_callback)

    # Save output
    corrected.save(str(output_file))
    logger.info("✓ Grammar correction complete")
    logger.info(f"Output saved to: {output_file}")
