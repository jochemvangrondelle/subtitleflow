# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Service initialization utilities for CLI."""

from subtitleflow.common.clients.ollama import OllamaClient
from subtitleflow.common.models.config import AppConfig
from subtitleflow.common.services.cache import CacheService
from subtitleflow.common.services.judge import JudgeService
from subtitleflow.correct.service import GrammarCorrectionService
from subtitleflow.translate.service import TranslationService


def create_services(
    config: AppConfig,
    no_cache: bool = False,
) -> tuple[OllamaClient, CacheService | None, JudgeService]:
    """
    Create common services.

    Args:
        config: Application configuration
        no_cache: Whether to disable caching

    Returns:
        Tuple of (client, cache, judge)
    """
    client = OllamaClient(config)
    cache = CacheService(config.cache_file) if not no_cache else None
    judge = JudgeService(client, config.judge_model)
    return client, cache, judge


def create_grammar_service(
    config: AppConfig,
    client: OllamaClient,
    cache: CacheService | None,
    judge: JudgeService,
) -> GrammarCorrectionService:
    """Create grammar correction service."""
    return GrammarCorrectionService(config, client, cache, judge)


def create_translation_service(
    config: AppConfig,
    client: OllamaClient,
    cache: CacheService | None,
    judge: JudgeService,
) -> TranslationService:
    """Create translation service."""
    return TranslationService(config, client, cache, judge)
