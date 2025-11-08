# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Parallel processing utilities."""

import logging
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import TypeVar

from subtitleflow.common.models.config import AppConfig

logger = logging.getLogger(__name__)

T = TypeVar("T")
R = TypeVar("R")


class ParallelProcessor:
    """Handles parallel execution of operations."""

    def __init__(self, config: AppConfig) -> None:
        """
        Initialize parallel processor.

        Args:
            config: Application configuration
        """
        self.config = config

    def process_models_parallel(
        self,
        models: list[str],
        subtitles: list,
        process_func: Callable,
        max_workers: int | None = None,
    ) -> list[R]:
        """
        Process multiple models in parallel.

        Args:
            models: List of model names
            subtitles: List of subtitles to process
            process_func: Function to call for each model (model, subtitles) -> result
            max_workers: Max parallel workers (defaults to config)

        Returns:
            List of results in same order as models
        """
        if not models:
            return []

        if not self.config.enable_parallel or len(models) == 1:
            # Sequential processing
            return [process_func(model, subtitles) for model in models]

        if max_workers is None:
            max_workers = min(len(models), self.config.max_parallel_models)

        if max_workers <= 0:
            max_workers = 1

        logger.debug(f"Processing {len(models)} models in parallel (max workers: {max_workers})")

        results: list[tuple[int, R]] = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_model = {
                executor.submit(self._safe_process, process_func, model, subtitles): (i, model)
                for i, model in enumerate(models)
            }

            # Collect results as they complete
            for future in as_completed(future_to_model):
                idx, _model = future_to_model[future]
                result = future.result()  # _safe_process already handles exceptions
                results.append((idx, result))

        # Sort by original index to maintain order
        results.sort(key=lambda x: x[0])

        return [r for _, r in results]  # Include None values for failed models

    def _safe_process(self, process_func: Callable, *args, **kwargs) -> R | None:
        """
        Safely process a model with error handling.

        Args:
            process_func: Function to call
            *args: Positional arguments to pass to process_func
            **kwargs: Keyword arguments to pass to process_func

        Returns:
            Result from process_func, or None if an exception occurs
        """
        try:
            logger.debug(f"Processing with args: {args}, kwargs: {kwargs}")
            result = process_func(*args, **kwargs)
            logger.debug("Completed processing")
            return result
        except Exception as e:
            logger.exception(f"Error processing: {e}")
            return None
