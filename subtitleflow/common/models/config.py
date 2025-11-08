# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Application configuration models."""

import logging
import os
from dataclasses import dataclass, field

import langcodes

logger = logging.getLogger(__name__)


def get_language_code(language: str) -> str:
    """Get ISO 639-1 language code from language name using langcodes library.

    Args:
        language: Language name (e.g., "Dutch", "Spanish") or code (e.g., "nl", "es")

    Returns:
        ISO 639-1 or 639-3 language code

    Examples:
        >>> get_language_code("Dutch")
        'nl'
        >>> get_language_code("español")
        'es'
        >>> get_language_code("nl")
        'nl'
    """
    try:
        # Try to find language by name (works in any language)
        lang = langcodes.find(language)
        return str(lang)
    except LookupError:
        # If not found by name, try to parse as a language tag
        try:
            lang = langcodes.Language.get(language)
            if lang.is_valid():
                return str(lang)
        except Exception:
            pass

        # Fallback: return first 2 characters lowercase
        logger.warning(f"Could not find language code for '{language}', using fallback")
        return language.lower()[:2]


@dataclass
class ModelConfig:
    """Configuration for a single model."""

    name: str
    temperature: float = 0.7
    num_ctx: int = 16384
    top_p: float | None = None
    top_k: int | None = None
    repeat_penalty: float | None = None

    def get_options(self) -> dict[str, any]:
        """Get model options as dict for API calls."""
        options = {
            "temperature": self.temperature,
            "num_ctx": self.num_ctx,
        }

        if self.top_p is not None:
            options["top_p"] = self.top_p
        if self.top_k is not None:
            options["top_k"] = self.top_k
        if self.repeat_penalty is not None:
            options["repeat_penalty"] = self.repeat_penalty

        return options


@dataclass
class AppConfig:
    """Main application configuration."""

    # Ollama settings
    ollama_url: str = field(
        default_factory=lambda: os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
    )

    # Model configuration - SINGLE SOURCE OF TRUTH
    # Grammar correction: Use smaller/faster models (simple task)
    grammar_models: list[str] = field(default_factory=lambda: ["qwen2.5:3b", "gemma3:4b"])

    # Translation: Best multilingual models for ensemble (sequential processing)
    # llama3.2:3b (2GB, Meta's latest), qwen2.5:7b (5GB, best multilingual), stablelm2:1.6b (1GB, fast)
    translation_models: list[str] = field(
        default_factory=lambda: ["llama3.2:3b", "qwen2.5:7b", "stablelm2:1.6b"]
    )

    # Judge: Best multilingual judge for selecting best translation
    judge_model: str = "qwen2.5:7b"  # Best multilingual performance (~5GB VRAM)

    # Language-specific overrides (optional)
    # If a language has specific model recommendations, add them here
    language_model_overrides: dict[str, dict[str, list[str]]] = field(default_factory=dict)
    # Example: {"dutch": {"translation_models": ["qwen2.5:7b", "llama3.2:3b"]}}

    # Processing settings
    context_window: int = 3
    max_retries: int = 3
    timeout: int = 900

    # Performance settings
    batch_size: int = 5  # Number of subtitles per batch
    enable_batching: bool = False  # Batch subtitle processing
    enable_parallel: bool = False  # Parallel model execution (disabled - sequential only)
    max_parallel_models: int = 1  # Max concurrent models (sequential)

    # Cache settings
    cache_file: str = "srt_ollama_cache.json"
    enable_cache: bool = True

    # Output settings
    log_level: str = "INFO"

    @property
    def ollama_base_url(self) -> str:
        """Get base URL without /api/generate and trailing slashes."""
        url = self.ollama_url.rstrip("/")
        url = url.removesuffix("/api/generate")
        return url.rstrip("/")

    @property
    def ollama_generate_url(self) -> str:
        """Get generate endpoint URL."""
        base = self.ollama_base_url
        return f"{base}/api/generate"

    @property
    def ollama_tags_url(self) -> str:
        """Get tags endpoint URL."""
        base = self.ollama_base_url
        return f"{base}/api/tags"

    def apply_language_overrides(self, language: str) -> None:
        """Apply language-specific model overrides if they exist.

        Args:
            language: Target language (e.g., "Dutch", "Spanish", "French")
        """
        lang_lower = language.lower()

        if lang_lower in self.language_model_overrides:
            overrides = self.language_model_overrides[lang_lower]

            if "translation_models" in overrides:
                self.translation_models = overrides["translation_models"]
                logger.info(
                    f"Applied language-specific translation models for {language}: {self.translation_models}"
                )

            if "judge_model" in overrides:
                self.judge_model = overrides["judge_model"]
                logger.info(
                    f"Applied language-specific judge model for {language}: {self.judge_model}"
                )

            if "grammar_models" in overrides:
                self.grammar_models = overrides["grammar_models"]
                logger.info(
                    f"Applied language-specific grammar models for {language}: {self.grammar_models}"
                )

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Create config from environment variables."""
        return cls()
