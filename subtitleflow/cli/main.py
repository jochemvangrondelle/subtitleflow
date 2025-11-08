# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Main CLI application using Typer and Rich."""

import logging
from pathlib import Path

import typer
from rich.console import Console
from rich.logging import RichHandler

from subtitleflow import __version__
from subtitleflow.cli.commands import (
    handle_fix,
    handle_process_video,
    handle_transcribe,
    handle_translate,
)

app = typer.Typer(
    name="subtitleflow",
    help="AI-powered subtitle translation and correction tool",
    add_completion=False,
)
console = Console()
logger = logging.getLogger(__name__)


def setup_logging(log_level: str = "INFO") -> None:
    """Setup rich logging with TRACE level support."""
    TRACE = 5
    logging.addLevelName(TRACE, "TRACE")

    if log_level.upper() == "TRACE":
        level = TRACE
    else:
        level = getattr(logging, log_level.upper(), logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=False)],
    )

    # Suppress verbose HTTP trace logs
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpcore.connection").setLevel(logging.WARNING)
    logging.getLogger("httpcore.http11").setLevel(logging.WARNING)


@app.command()
def fix(
    input_file: Path = typer.Argument(..., help="Input SRT file"),
    output_file: Path = typer.Argument(..., help="Output SRT file"),
    grammar_models: str = typer.Option(
        "qwen2.5:7b,gemma3:4b",
        "--grammar-models",
        "-g",
        help="Comma-separated list of models for grammar correction",
    ),
    judge_model: str = typer.Option(
        "qwen2.5:7b", "--judge-model", "-j", help="Model to judge best candidate"
    ),
    context_window: int = typer.Option(
        3, "--context", "-c", help="Number of surrounding lines for context"
    ),
    log_level: str = typer.Option("INFO", "--log-level", "-l", help="Logging level"),
    no_cache: bool = typer.Option(False, "--no-cache", help="Disable caching"),
) -> None:
    """Fix grammar and spelling mistakes in subtitles."""
    setup_logging(log_level)
    handle_fix(
        input_file=input_file,
        output_file=output_file,
        grammar_models=grammar_models,
        judge_model=judge_model,
        context_window=context_window,
        log_level=log_level,
        no_cache=no_cache,
    )


@app.command()
def translate(
    input_file: Path = typer.Argument(..., help="Input SRT file"),
    output_file: Path = typer.Argument(..., help="Output SRT file"),
    language: str = typer.Option("dutch", "--lang", "-l", help="Target language"),
    translation_models: str = typer.Option(
        "llama3.2:3b,qwen2.5:7b,stablelm2:1.6b",
        "--translation-models",
        "-t",
        help="Comma-separated list of models for translation",
    ),
    judge_model: str = typer.Option(
        "qwen2.5:7b", "--judge-model", "-j", help="Model to judge best candidate"
    ),
    context_window: int = typer.Option(
        3, "--context", "-c", help="Number of surrounding lines for context"
    ),
    log_level: str = typer.Option("INFO", "--log-level", help="Logging level"),
    no_cache: bool = typer.Option(False, "--no-cache", help="Disable caching"),
) -> None:
    """Translate subtitles to a single language."""
    setup_logging(log_level)
    handle_translate(
        input_file=input_file,
        output_file=output_file,
        language=language,
        translation_models=translation_models,
        judge_model=judge_model,
        context_window=context_window,
        log_level=log_level,
        no_cache=no_cache,
    )


@app.command()
def transcribe(
    video_file: Path = typer.Argument(..., help="Input video file (mp4, mov, mkv)"),
    output_file: Path | None = typer.Option(
        None, "--output", "-o", help="Output SRT file (default: video.srt)"
    ),
    model: str = typer.Option(
        "large-v2",
        "--model",
        "-m",
        help="WhisperX model (tiny, base, small, medium, large-v2, large-v3)",
    ),
    language: str = typer.Option("en", "--language", "-l", help="Language code (en, nl, es, etc.)"),
    device: str = typer.Option("cuda", "--device", "-d", help="Device (cuda or cpu)"),
    batch_size: int = typer.Option(4, "--batch-size", "-b", help="Batch size for processing"),
    log_level: str = typer.Option("INFO", "--log-level", help="Logging level"),
) -> None:
    """Transcribe video to subtitles using WhisperX."""
    setup_logging(log_level)
    handle_transcribe(
        video_file=video_file,
        output_file=output_file,
        model=model,
        language=language,
        device=device,
        batch_size=batch_size,
    )


@app.command()
def process_video(
    video_file: Path = typer.Argument(..., help="Input video file"),
    languages: str = typer.Option(
        "dutch,spanish", "--langs", "-l", help="Comma-separated target languages"
    ),
    skip_transcribe: bool = typer.Option(
        False, "--skip-transcribe", help="Skip transcription if SRT already exists"
    ),
    skip_grammar: bool = typer.Option(False, "--skip-grammar", help="Skip grammar correction"),
    transcribe_model: str = typer.Option(
        "large-v2", "--transcribe-model", help="WhisperX model for transcription"
    ),
    log_level: str = typer.Option("INFO", "--log-level", help="Logging level"),
) -> None:
    """Complete workflow: Transcribe video, fix grammar, and translate to multiple languages."""
    setup_logging(log_level)
    handle_process_video(
        video_file=video_file,
        languages=languages,
        skip_transcribe=skip_transcribe,
        skip_grammar=skip_grammar,
        transcribe_model=transcribe_model,
        log_level=log_level,
    )


@app.command()
def version() -> None:
    """Show version information."""
    console.print(f"subtitleflow version {__version__}")


if __name__ == "__main__":
    app()
