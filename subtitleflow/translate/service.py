# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Translation service for subtitleflow."""

import logging
from collections.abc import Callable

from subtitleflow.common.clients.ollama import OllamaClient
from subtitleflow.common.models.config import AppConfig
from subtitleflow.common.models.subtitle import Subtitle, SubtitleFile
from subtitleflow.common.models.translation import Candidate
from subtitleflow.common.services.cache import CacheService
from subtitleflow.common.services.judge import JudgeService
from subtitleflow.translate.batch_translator import BatchTranslator

logger = logging.getLogger(__name__)


class TranslationService:
    """Service for translating subtitles to different languages."""

    def __init__(
        self,
        config: AppConfig,
        client: OllamaClient,
        cache: CacheService,
        judge: JudgeService,
    ) -> None:
        """
        Initialize translation service.

        Args:
            config: Application configuration
            client: Ollama client
            cache: Cache service
            judge: Judge service for selecting best translations
        """
        self.config = config
        self.client = client
        self.cache = cache
        self.judge = judge
        self.batch_translator = BatchTranslator(client, batch_size=10, cache=cache)

    def translate(
        self,
        subtitle_file: SubtitleFile,
        target_language: str,
        display_callback: Callable | None = None,
    ) -> SubtitleFile:
        """
        Translate subtitle file to a single language using smart batching.

        Args:
            subtitle_file: Input subtitle file
            target_language: Target language name
            display_callback: Optional callback for displaying results (CLI only)

        Returns:
            Translated subtitle file
        """
        logger.info(f"Starting translation to {target_language} on {len(subtitle_file)} subtitles")
        logger.info(f"Using models: {', '.join(self.config.translation_models)}")

        translated_subtitles = []

        # Use batch translation for each model, then judge
        if len(self.config.translation_models) == 1:
            # Single model - use batch translation directly
            model = self.config.translation_models[0]
            translations = self.batch_translator.translate_all(
                subtitle_file.subtitles,
                model,
                target_language,
                context_window=self.config.context_window,
                display_callback=display_callback,
            )

            for i, translation in enumerate(translations):
                translated = Subtitle(
                    index=subtitle_file.subtitles[i].index,
                    start=subtitle_file.subtitles[i].start,
                    end=subtitle_file.subtitles[i].end,
                    content=translation,
                )
                translated_subtitles.append(translated)
        else:
            # Multiple models - batch translate with each sequentially, then judge
            logger.info(
                f"Translating with {len(self.config.translation_models)} models sequentially"
            )

            # Process each model sequentially
            all_model_translations = {}
            for model in self.config.translation_models:
                logger.info(f"  [{model}] Translating to {target_language}...")
                translations = self.batch_translator.translate_all(
                    subtitle_file.subtitles,
                    model,
                    target_language,
                    context_window=self.config.context_window,
                    display_callback=display_callback,
                )
                all_model_translations[model] = translations

            # Judge each subtitle
            previous_translations = []
            for i, subtitle in enumerate(subtitle_file.subtitles):
                # Create candidates from all models
                candidates = []
                for model, translations in all_model_translations.items():
                    candidate = Candidate(model=model, text=translations[i])
                    candidates.append(candidate)

                # Select best
                if len(candidates) == 1:
                    best = candidates[0]
                else:
                    best = self.judge.select_best(
                        subtitle.content,
                        candidates,
                        language=target_language,
                        previous_translations=previous_translations,
                    )

                # Create translated subtitle
                translated = Subtitle(
                    index=subtitle.index, start=subtitle.start, end=subtitle.end, content=best.text
                )
                translated_subtitles.append(translated)
                previous_translations.append(best.text)

        logger.info(f"Translation to {target_language} complete")

        return SubtitleFile(
            path=subtitle_file.path, subtitles=translated_subtitles, encoding=subtitle_file.encoding
        )
