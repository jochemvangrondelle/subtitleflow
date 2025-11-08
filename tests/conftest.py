# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Pytest configuration and fixtures."""

import tempfile
from collections.abc import Generator
from datetime import timedelta
from pathlib import Path

import pytest

from subtitleflow.common.models.config import AppConfig
from subtitleflow.common.models.subtitle import Subtitle, SubtitleFile
from subtitleflow.common.services.cache import CacheService


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_subtitle() -> Subtitle:
    """Create a sample subtitle."""
    return Subtitle(
        index=1, start=timedelta(seconds=0), end=timedelta(seconds=2), content="Hello, world!"
    )


@pytest.fixture
def sample_subtitle_file(temp_dir: Path) -> SubtitleFile:
    """Create a sample subtitle file."""
    subtitles = [
        Subtitle(
            index=1, start=timedelta(seconds=0), end=timedelta(seconds=2), content="Hello, world!"
        ),
        Subtitle(
            index=2, start=timedelta(seconds=2), end=timedelta(seconds=4), content="This is a test."
        ),
        Subtitle(
            index=3, start=timedelta(seconds=4), end=timedelta(seconds=6), content="♪ Music line ♪"
        ),
    ]

    file_path = temp_dir / "test.srt"
    subtitle_file = SubtitleFile(path=str(file_path), subtitles=subtitles)
    subtitle_file.save(str(file_path))

    return subtitle_file


@pytest.fixture
def app_config() -> AppConfig:
    """Create test app configuration."""
    return AppConfig(
        ollama_url="http://127.0.0.1:11434",
        grammar_models=["test-model"],
        translation_models=["test-model"],
        judge_model="test-model",
        context_window=3,
        max_retries=3,
        cache_file=":memory:",
    )


@pytest.fixture
def cache_service(temp_dir: Path) -> CacheService:
    """Create cache service with temporary file."""
    cache_file = temp_dir / "test_cache.json"
    return CacheService(str(cache_file))
