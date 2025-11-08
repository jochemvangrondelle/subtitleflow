# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Translation domain models."""

from dataclasses import dataclass, field
from typing import Any

from subtitleflow.common.models.subtitle import Subtitle


@dataclass
class Candidate:
    """A translation candidate from a model."""

    model: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def preview(self) -> str:
        """Get a preview of the translation."""
        return self.text[:240] + ("..." if len(self.text) > 240 else "")


@dataclass
class TranslationResult:
    """Result of translating a single subtitle."""

    original: Subtitle
    translated: Subtitle
    candidates: list[Candidate] = field(default_factory=list)
    selected_by_judge: bool = False
    cache_hit: bool = False

    @property
    def from_cache(self) -> bool:
        """Alias for cache_hit."""
        return self.cache_hit


@dataclass
class MultiLanguageResult:
    """Result of translating to multiple languages."""

    original: Subtitle
    translations: dict[str, Subtitle]  # language -> translated subtitle
    candidates: dict[str, list[Candidate]] = field(default_factory=dict)  # language -> candidates
    selected_by_judge: bool = False
    cache_hit: bool = False
