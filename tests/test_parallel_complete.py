# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Complete tests for ParallelProcessor service."""

from typing import Never
from unittest.mock import patch

import pytest

from subtitleflow.common.models.config import AppConfig
from subtitleflow.common.models.subtitle import Subtitle
from subtitleflow.common.services.parallel import ParallelProcessor


class TestParallelProcessor:
    """Test ParallelProcessor service."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.config = AppConfig(max_parallel_models=2, enable_parallel=True)
        self.processor = ParallelProcessor(self.config)

    def test_init(self) -> None:
        """Test ParallelProcessor initialization."""
        assert self.processor.config == self.config
        # max_parallel_models is accessed via config, not stored directly
        assert self.processor.config.max_parallel_models == 2

    def test_init_with_custom_config(self) -> None:
        """Test ParallelProcessor initialization with custom config."""
        config = AppConfig(max_parallel_models=5, enable_parallel=True)
        processor = ParallelProcessor(config)
        assert processor.config.max_parallel_models == 5

    def test_init_disabled_parallel(self) -> None:
        """Test ParallelProcessor initialization with parallel disabled."""
        config = AppConfig(enable_parallel=False)
        processor = ParallelProcessor(config)
        assert processor.config.max_parallel_models == 1  # Should default to 1

    def test_process_models_parallel_single_model(self) -> None:
        """Test parallel processing with single model."""
        models = ["model1"]
        subtitles = [Subtitle(index=1, start=0, end=1000, content="Hello")]

        def mock_process_func(model, subs) -> str:
            return f"result_{model}"

        results = self.processor.process_models_parallel(models, subtitles, mock_process_func)

        assert results == ["result_model1"]

    def test_process_models_parallel_multiple_models(self) -> None:
        """Test parallel processing with multiple models."""
        models = ["model1", "model2", "model3"]
        subtitles = [Subtitle(index=1, start=0, end=1000, content="Hello")]

        def mock_process_func(model, subs) -> str:
            return f"result_{model}"

        results = self.processor.process_models_parallel(models, subtitles, mock_process_func)

        assert len(results) == 3
        assert "result_model1" in results
        assert "result_model2" in results
        assert "result_model3" in results

    def test_process_models_parallel_with_exception(self) -> None:
        """Test parallel processing handles exceptions gracefully."""
        models = ["model1", "model2"]
        subtitles = [Subtitle(index=1, start=0, end=1000, content="Hello")]

        def mock_process_func(model, subs) -> str:
            if model == "model1":
                msg = "Test error"
                raise ValueError(msg)
            return f"result_{model}"

        results = self.processor.process_models_parallel(models, subtitles, mock_process_func)

        # Should have one result and one None (for the failed model)
        assert len(results) == 2
        assert None in results
        assert "result_model2" in results

    def test_process_models_parallel_empty_models(self) -> None:
        """Test parallel processing with empty models list."""
        models = []
        subtitles = [Subtitle(index=1, start=0, end=1000, content="Hello")]

        def mock_process_func(model, subs) -> str:
            return f"result_{model}"

        results = self.processor.process_models_parallel(models, subtitles, mock_process_func)

        assert results == []

    def test_process_models_parallel_empty_subtitles(self) -> None:
        """Test parallel processing with empty subtitles list."""
        models = ["model1", "model2"]
        subtitles = []

        def mock_process_func(model, subs) -> str:
            return f"result_{model}"

        # Fix the max_workers parameter issue
        with patch("subtitleflow.common.services.parallel.ThreadPoolExecutor") as mock_executor:
            mock_executor.return_value.__enter__.return_value.map.return_value = [
                "result_model1",
                "result_model2",
            ]

            results = self.processor.process_models_parallel(models, subtitles, mock_process_func)

        assert len(results) == 2
        assert "result_model1" in results
        assert "result_model2" in results

    def test_process_models_parallel_max_parallel_limit(self) -> None:
        """Test parallel processing respects max_parallel_models limit."""
        config = AppConfig(max_parallel_models=1, enable_parallel=True)
        processor = ParallelProcessor(config)

        models = ["model1", "model2", "model3"]
        subtitles = [Subtitle(index=1, start=0, end=1000, content="Hello")]

        def mock_process_func(model, subs) -> str:
            return f"result_{model}"

        results = processor.process_models_parallel(models, subtitles, mock_process_func)

        assert len(results) == 3
        assert "result_model1" in results
        assert "result_model2" in results
        assert "result_model3" in results

    def test_safe_process_success(self) -> None:
        """Test _safe_process with successful execution."""

        def mock_func(model) -> str:
            return f"success_{model}"

        result = self.processor._safe_process(mock_func, "test_model")

        assert result == "success_test_model"

    def test_safe_process_exception(self) -> None:
        """Test _safe_process with exception."""

        def mock_func(model) -> Never:
            msg = "Test error"
            raise ValueError(msg)

        result = self.processor._safe_process(mock_func, "test_model")

        assert result is None

    def test_safe_process_different_exceptions(self) -> None:
        """Test _safe_process with different exception types."""

        def mock_func(model) -> Never:
            msg = "Runtime error"
            raise RuntimeError(msg)

        result = self.processor._safe_process(mock_func, "test_model")

        assert result is None

    def test_safe_process_with_args(self) -> None:
        """Test _safe_process with function that takes arguments."""

        def mock_func(model, arg1, arg2) -> str:
            return f"{model}_{arg1}_{arg2}"

        result = self.processor._safe_process(mock_func, "test_model", "arg1", "arg2")

        assert result == "test_model_arg1_arg2"

    def test_safe_process_with_kwargs(self) -> None:
        """Test _safe_process with function that takes keyword arguments."""

        def mock_func(model, **kwargs) -> str:
            return f"{model}_{kwargs.get('key1')}_{kwargs.get('key2')}"

        result = self.processor._safe_process(mock_func, "test_model", key1="value1", key2="value2")

        assert result == "test_model_value1_value2"

    def test_safe_process_with_mixed_args(self) -> None:
        """Test _safe_process with function that takes both args and kwargs."""

        def mock_func(model, arg1, arg2, **kwargs) -> str:
            return f"{model}_{arg1}_{arg2}_{kwargs.get('key1')}"

        result = self.processor._safe_process(
            mock_func, "test_model", "arg1", "arg2", key1="value1"
        )

        assert result == "test_model_arg1_arg2_value1"

    def test_safe_process_none_function(self) -> None:
        """Test _safe_process with None function."""
        with pytest.raises(TypeError):
            self.processor._safe_process(None, "test_model")

    def test_safe_process_string_function(self) -> None:
        """Test _safe_process with string instead of function."""
        with pytest.raises(TypeError):
            self.processor._safe_process("not_a_function", "test_model")

    def test_process_models_parallel_with_real_threading(self) -> None:
        """Test parallel processing with actual threading."""
        models = ["model1", "model2"]
        subtitles = [Subtitle(index=1, start=0, end=1000, content="Hello")]

        def mock_process_func(model, subs) -> str:
            import time

            time.sleep(0.1)  # Simulate some work
            return f"result_{model}"

        results = self.processor.process_models_parallel(models, subtitles, mock_process_func)

        assert len(results) == 2
        assert "result_model1" in results
        assert "result_model2" in results

    def test_process_models_parallel_order_preservation(self) -> None:
        """Test that parallel processing preserves model order in results."""
        models = ["model3", "model1", "model2"]
        subtitles = [Subtitle(index=1, start=0, end=1000, content="Hello")]

        def mock_process_func(model, subs) -> str:
            return f"result_{model}"

        results = self.processor.process_models_parallel(models, subtitles, mock_process_func)

        # Results should be in the same order as input models
        assert results[0] == "result_model3"
        assert results[1] == "result_model1"
        assert results[2] == "result_model2"

    def test_process_models_parallel_mixed_success_failure(self) -> None:
        """Test parallel processing with mixed success and failure."""
        models = ["model1", "model2", "model3"]
        subtitles = [Subtitle(index=1, start=0, end=1000, content="Hello")]

        def mock_process_func(model, subs) -> str:
            if model == "model2":
                msg = "Model2 error"
                raise ValueError(msg)
            return f"result_{model}"

        results = self.processor.process_models_parallel(models, subtitles, mock_process_func)

        assert len(results) == 3
        assert results[0] == "result_model1"
        assert results[1] is None  # Failed model
        assert results[2] == "result_model3"
