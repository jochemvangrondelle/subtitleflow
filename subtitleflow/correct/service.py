# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Grammar correction service for subtitleflow."""

import logging
from collections.abc import Callable
from typing import Any, cast

from subtitleflow.common.clients.ollama import OllamaClient
from subtitleflow.common.constants.messages import (
    MSG_BATCH_FAILED,
    MSG_FINAL_COUNT,
    MSG_GRAMMAR_COMPLETE,
    MSG_GRAMMAR_MODELS,
    MSG_GRAMMAR_STARTING,
    MSG_JUDGE_FAILED,
)
from subtitleflow.common.models.config import AppConfig
from subtitleflow.common.models.subtitle import Subtitle, SubtitleFile
from subtitleflow.common.models.translation import Candidate
from subtitleflow.common.services.cache import CacheService
from subtitleflow.common.services.judge import JudgeService
from subtitleflow.common.utils.batching import create_smart_batches
from subtitleflow.common.utils.display import log_context, log_correction_batch
from subtitleflow.correct.batch_processor import BatchCorrector
from subtitleflow.correct.context import build_context_display, build_context_lines
from subtitleflow.correct.deduplication import remove_duplicates, separate_music_lines

logger = logging.getLogger(__name__)


class GrammarCorrectionService:
    """Service for correcting grammar and spelling in subtitles."""

    def __init__(
        self,
        config: AppConfig,
        client: OllamaClient,
        cache: CacheService,
        judge: JudgeService,
    ) -> None:
        """
        Initialize grammar correction service.

        Args:
            config: Application configuration
            client: Ollama client
            cache: Cache service
            judge: Judge service for selecting best corrections
        """
        self.config = config
        self.client = client
        self.cache = cache
        self.judge = judge
        self.batch_corrector = BatchCorrector(config, client, cache)

    def correct(
        self,
        subtitle_file: SubtitleFile,
        display_callback: Callable[..., Any] | None = None,
    ) -> SubtitleFile:
        """
        Correct grammar/spelling in subtitle file using batch processing.

        Args:
            subtitle_file: Input subtitle file
            display_callback: Optional callback for displaying results (CLI only)

        Returns:
            Corrected subtitle file with duplicates removed
        """
        logger.info(MSG_GRAMMAR_STARTING.format(count=len(subtitle_file)))  # type: ignore[attr-defined]
        logger.info(MSG_GRAMMAR_MODELS.format(models=", ".join(self.config.grammar_models)))  # type: ignore[attr-defined]

        # Step 1: Remove duplicates
        dedup_result = remove_duplicates(subtitle_file.subtitles)
        deduplicated_subtitles = dedup_result[0]
        duplicate_indices = cast("set[int]", dedup_result[1])

        # Step 2: Separate music lines
        music_result = separate_music_lines(deduplicated_subtitles)
        music_indices = music_result[0]
        non_music_subtitles_tuples = cast("list[tuple[int, Subtitle]]", music_result[1])

        # Step 3: Create batches
        batches = self._create_batches(non_music_subtitles_tuples)

        # Step 4: Process with all models
        all_models_all_batches = self._process_all_models(batches, display_callback)

        # Step 5: Judge and select best corrections
        non_music_corrections, _completed_corrections = self._judge_all_batches(
            batches, all_models_all_batches, display_callback
        )

        # Step 6: Reconstruct final file
        return self._reconstruct_file(
            subtitle_file,
            deduplicated_subtitles,
            music_indices,
            non_music_corrections,
            duplicate_indices,
        )

    def _create_batches(
        self, non_music_subtitles: list[tuple[int, Subtitle]]
    ) -> list[list[Subtitle]]:
        """Create smart batches from non-music subtitles."""
        if not non_music_subtitles:
            return []

        just_subs = [sub for _, sub in non_music_subtitles]
        batches = create_smart_batches(just_subs, batch_size=10)
        logger.info(f"Created {len(batches)} batches for grammar correction")
        return batches

    def _process_all_models(
        self,
        batches: list[list[Subtitle]],
        display_callback: Callable[..., Any] | None = None,
    ) -> dict[str, list[list[str]]]:
        """Process all batches with all models."""
        logger.info(f"Correcting with {len(self.config.grammar_models)} models sequentially")
        all_models_all_batches: dict[str, list[list[str]]] = {}

        for model in self.config.grammar_models:
            logger.info(f"  [{model}] Processing ALL {len(batches)} batches...")
            model_all_batches: list[list[str]] = []
            completed_corrections_for_model: list[tuple[str, str]] = []

            for batch_idx, batch in enumerate(batches):
                logger.info(
                    f"    [{model}] Batch {batch_idx + 1}/{len(batches)} ({len(batch)} subtitles)"
                )

                context_lines = build_context_lines(
                    completed_corrections_for_model, self.config.context_window
                )

                batch_corrections = self.batch_corrector.correct_batch(
                    batch, context_lines, model=model
                )

                if batch_corrections and len(batch_corrections) == len(batch):
                    model_all_batches.append(batch_corrections)

                    # Log batch results
                    log_correction_batch(batch, batch_corrections, batch_idx, len(batches), model)

                    # Optional Rich display (CLI only)
                    if display_callback:
                        display_callback(batch, batch_corrections, batch_idx, len(batches), model)

                    # Update context
                    for sub, corr in zip(batch, batch_corrections, strict=False):
                        completed_corrections_for_model.append((sub.content, corr))
                else:
                    logger.warning(MSG_BATCH_FAILED.format(model=model, batch=batch_idx + 1))  # type: ignore[attr-defined]
                    model_all_batches.append([sub.content for sub in batch])

            all_models_all_batches[model] = model_all_batches
            logger.info(f"  ✓ [{model}] Completed all {len(batches)} batches")

        return all_models_all_batches

    def _judge_all_batches(
        self,
        batches: list[list[Subtitle]],
        all_models_all_batches: dict[str, list[list[str]]],
        display_callback: Callable[..., Any] | None = None,
    ) -> tuple[list[str], list[tuple[str, str]]]:
        """Judge between models for each batch."""
        logger.info(f"Judging between {len(self.config.grammar_models)} models...")
        non_music_corrections: list[str] = []
        completed_corrections: list[tuple[str, str]] = []

        for batch_idx, batch in enumerate(batches):
            logger.info(
                f"=== Judging Batch {batch_idx + 1}/{len(batches)} === ({len(batch)} subtitles)"
            )

            context_display = build_context_display(
                completed_corrections, self.config.context_window
            )

            # Collect corrections from all models
            all_model_corrections = self._collect_model_corrections(
                all_models_all_batches, batch_idx
            )

            # Judge or use single model
            batch_corrections = self._judge_batch(
                batch, all_model_corrections, completed_corrections
            )

            # Log results
            log_context(context_display, context_type="corrections")
            log_correction_batch(batch, batch_corrections, batch_idx, len(batches), "judged")

            # Optional Rich display (CLI only)
            if display_callback:
                display_callback(batch, batch_corrections, batch_idx, len(batches), context_display)

            # Update results
            non_music_corrections.extend(batch_corrections)
            for sub, corrected in zip(batch, batch_corrections, strict=False):
                completed_corrections.append((sub.content, corrected))

        return non_music_corrections, completed_corrections

    def _collect_model_corrections(
        self, all_models_all_batches: dict[str, list[list[str]]], batch_idx: int
    ) -> dict[str, list[str]]:
        """Collect corrections from all models for a batch."""
        all_model_corrections: dict[str, list[str]] = {}
        for model_name, model_batches in all_models_all_batches.items():
            if batch_idx < len(model_batches):
                all_model_corrections[model_name] = model_batches[batch_idx]
        return all_model_corrections

    def _judge_batch(
        self,
        batch: list[Subtitle],
        all_model_corrections: dict[str, list[str]],
        completed_corrections: list[tuple[str, str]],
    ) -> list[str]:
        """Judge corrections from multiple models."""
        if len(all_model_corrections) > 1:
            logger.debug(f"Judging corrections from {len(all_model_corrections)} models")
            return self._judge_corrections(batch, all_model_corrections, completed_corrections)
        if len(all_model_corrections) == 1:
            logger.debug("Using single model result (no judging needed)")
            return next(iter(all_model_corrections.values()))

        logger.error("❌ All models failed for batch")
        return [sub.content for sub in batch]

    def _judge_corrections(
        self,
        batch: list[Subtitle],
        all_model_corrections: dict[str, list[str]],
        completed_corrections: list[tuple[str, str]],
    ) -> list[str]:
        """
        Judge corrections from multiple models and select the best.

        Args:
            batch: Original subtitles
            all_model_corrections: Dict mapping model name to list of corrections
            completed_corrections: Previous (original, corrected) pairs for context

        Returns:
            List of best corrections (one per subtitle in batch)
        """
        judged_corrections: list[str] = []

        for i, subtitle in enumerate(batch):
            candidates = self._get_candidates_for_subtitle(all_model_corrections, i)

            # If all identical, skip judging
            unique_candidates = set(candidates.values())
            if len(unique_candidates) == 1:
                judged_corrections.append(next(iter(unique_candidates)))
                logger.debug(
                    f"All models returned identical correction for: {subtitle.content[:50]}..."
                )
                continue

            # Build context for judge
            prev_texts = self._build_judge_context(completed_corrections)

            # Call judge
            try:
                candidate_objs = [
                    Candidate(text=correction, model=model_name)
                    for model_name, correction in candidates.items()
                ]

                best_candidate = self.judge.select_best(
                    original_text=subtitle.content,
                    candidates=candidate_objs,
                    language="English",
                    previous_translations=prev_texts,
                )
                judged_corrections.append(best_candidate.text)
                logger.debug(
                    f"Judge selected best correction from {best_candidate.model} "
                    f"for: {subtitle.content[:30]}..."
                )
            except Exception as e:
                logger.warning(MSG_JUDGE_FAILED.format(index=i, error=e))  # type: ignore[attr-defined]
                judged_corrections.append(next(iter(candidates.values())))

        return judged_corrections

    def _get_candidates_for_subtitle(
        self, all_model_corrections: dict[str, list[str]], index: int
    ) -> dict[str, str]:
        """Get candidate corrections for a subtitle from all models."""
        candidates: dict[str, str] = {}
        for model_name, corrections_list in all_model_corrections.items():
            if index < len(corrections_list):
                candidates[model_name] = corrections_list[index]
        return candidates

    def _build_judge_context(
        self, completed_corrections: list[tuple[str, str]]
    ) -> list[str] | None:
        """Build context list for judge."""
        if not completed_corrections or self.config.context_window <= 0:
            return None

        start_idx = max(0, len(completed_corrections) - self.config.context_window)
        return [corr for _, corr in completed_corrections[start_idx:]]

    def _reconstruct_file(
        self,
        subtitle_file: SubtitleFile,
        deduplicated_subtitles: list[Subtitle],
        music_indices: dict[int, str],
        non_music_corrections: list[str],
        duplicate_indices: "set[int]",
    ) -> SubtitleFile:
        """Reconstruct final subtitle file."""
        # Reconstruct full correction list
        all_corrections: list[str] = []
        non_music_idx = 0

        for idx in range(len(deduplicated_subtitles)):
            if idx in music_indices:
                all_corrections.append(music_indices[idx])
            elif non_music_idx < len(non_music_corrections):
                all_corrections.append(non_music_corrections[non_music_idx])
                non_music_idx += 1
            else:
                logger.error(
                    f"❌ BUG: Ran out of non_music_corrections at idx={idx}, "
                    f"non_music_idx={non_music_idx}"
                )
                all_corrections.append(deduplicated_subtitles[idx].content)

        # Build corrected subtitle list
        corrected_subtitles: list[Subtitle] = []
        for subtitle, corrected_text in zip(deduplicated_subtitles, all_corrections, strict=False):
            corrected = Subtitle(
                index=subtitle.index,
                start=subtitle.start,
                end=subtitle.end,
                content=corrected_text,
            )
            corrected_subtitles.append(corrected)

        # Re-index sequentially
        for i, subtitle in enumerate(corrected_subtitles, start=1):
            subtitle.index = i

        logger.info(
            MSG_FINAL_COUNT.format(  # type: ignore[attr-defined]
                count=len(corrected_subtitles), duplicates=len(duplicate_indices)
            )
        )
        logger.info(MSG_GRAMMAR_COMPLETE)  # type: ignore[attr-defined]

        return SubtitleFile(
            path=subtitle_file.path,
            subtitles=corrected_subtitles,
            encoding=subtitle_file.encoding,
        )
