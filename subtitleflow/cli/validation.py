# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Validation utilities for CLI commands."""

import logging
from pathlib import Path

import typer
from rich.console import Console

from subtitleflow.common.clients.ollama import OllamaClient
from subtitleflow.common.constants.messages import (
    MSG_FILE_NOT_FOUND,
    MSG_MODEL_INSTALL,
    MSG_MODELS_AVAILABLE,
    MSG_MODELS_MISSING,
    MSG_OLLAMA_ACCESSIBLE,
    MSG_OLLAMA_NOT_ACCESSIBLE,
)
from subtitleflow.common.models.config import AppConfig
from subtitleflow.common.utils.gpu_check import check_models_fit_gpu, log_model_requirements

logger = logging.getLogger(__name__)
console = Console()


def validate_input_file(input_file: Path) -> None:
    """
    Validate input file exists.

    Args:
        input_file: Path to input file

    Raises:
        typer.Exit: If file doesn't exist
    """
    if not input_file.exists():
        console.print(MSG_FILE_NOT_FOUND.format(file_type="Input", path=input_file))
        raise typer.Exit(1)


def validate_ollama_server(client: OllamaClient) -> None:
    """
    Validate Ollama server is accessible.

    Args:
        client: Ollama client

    Raises:
        typer.Exit: If server not accessible
    """
    logger.info("Checking Ollama server...")
    if not client.check_health():
        logger.error(MSG_OLLAMA_NOT_ACCESSIBLE)
        raise typer.Exit(1)
    logger.info(MSG_OLLAMA_ACCESSIBLE)


def validate_models(client: OllamaClient, models: list[str]) -> None:
    """
    Validate all required models are available.

    Args:
        client: Ollama client
        models: List of model names to check

    Raises:
        typer.Exit: If models are missing
    """
    logger.info("Checking models...")
    missing: list[str] = []
    for model in models:
        if not client.check_model_exists(model):
            missing.append(model)

    if missing:
        logger.error(MSG_MODELS_MISSING.format(models=", ".join(missing)))
        logger.info("Install with:")
        for model in missing:
            logger.info(MSG_MODEL_INSTALL.format(model=model))
        raise typer.Exit(1)

    logger.info(MSG_MODELS_AVAILABLE)


def validate_gpu(config: AppConfig, models: list[str]) -> None:
    """
    Validate GPU has enough memory for models.

    Args:
        config: Application configuration
        models: List of model names

    Raises:
        typer.Exit: If GPU doesn't have enough memory
    """
    log_model_requirements(models)
    fits, message = check_models_fit_gpu(models, safety_margin_gb=1.0, ollama_url=config.ollama_url)
    if not fits:
        logger.error(message)
        raise typer.Exit(1)
