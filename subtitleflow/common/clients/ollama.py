# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Ollama API client using official library."""

import logging
from typing import Any

from ollama import Client, ResponseError

from subtitleflow.common.constants.messages import (
    MSG_OLLAMA_CONNECTION_ERROR,
)
from subtitleflow.common.models.config import AppConfig

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for interacting with Ollama API using official library."""

    def __init__(self, config: AppConfig) -> None:
        """
        Initialize Ollama client.

        Args:
            config: Application configuration
        """
        self.config = config
        self.client = Client(host=config.ollama_base_url)

    def check_health(self) -> bool:
        """Check if Ollama server is running and accessible."""
        try:
            # Use ollama library's ps() for health check (fast and lightweight)
            self.client.ps()
            return True
        except Exception as e:
            logger.exception(
                MSG_OLLAMA_CONNECTION_ERROR.format(  # type: ignore[attr-defined]
                    error=e, url=self.config.ollama_base_url
                )
            )
            return False

    def health_check(self) -> bool:
        """Alias for check_health() for compatibility."""
        return self.check_health()

    def check_model_exists(self, model: str) -> bool:
        """Check if a model is installed in Ollama."""
        try:
            models_list = self.client.list()
            # Handle both dict and object responses
            models: Any
            if hasattr(models_list, "models"):
                models = models_list.models
            elif isinstance(models_list, dict) and "models" in models_list:
                models = models_list["models"]
            else:
                models = models_list

            model_names: list[str] = []
            for m in models:
                if hasattr(m, "name"):
                    model_names.append(str(m.name))  # type: ignore[attr-defined]
                elif isinstance(m, dict):
                    name = m.get("name") or m.get("model") or ""  # type: ignore[assignment,arg-type]
                    model_names.append(str(name))  # type: ignore[arg-type]
                else:
                    model_names.append(str(m))

            # Check for exact match or with :latest tag
            model_base = model.split(":")[0] if ":" in model else model
            for available in model_names:
                if available == model or available.startswith(f"{model_base}:"):
                    return True
            return False
        except Exception as e:
            logger.warning(f"Could not verify model '{model}' exists: {e}")
            return True  # Assume it exists if we can't check

    def _get_model_options(
        self, model: str, temperature: float | None = None, max_tokens: int | None = None
    ) -> dict[str, Any]:
        """
        Get optimal options for a model.

        Args:
            model: Model name
            temperature: Sampling temperature (auto-detected if None)
            max_tokens: Maximum output tokens (task-specific if provided)
        """
        # Auto-detect temperature if not provided
        if temperature is None:
            temperature = 0.7 if model.startswith("qwen3") else 0.1

        # Context window: 8192 is sufficient for subtitle batches
        # (saves GPU memory vs default 16384)
        num_ctx = getattr(self.config, "num_ctx", 8192)

        options: dict[str, Any] = {
            "temperature": temperature,
            "num_ctx": num_ctx,
        }

        # Determine max output tokens
        if max_tokens is None:
            # Default: 1024 tokens = ~10-20 subtitle translations
            # Subtitles are short (typically 10-100 chars each)
            max_tokens = 1024

        if model.startswith("qwen3"):
            # Qwen3 non-thinking mode best practices
            options.update(
                {
                    "top_p": 0.8,
                    "top_k": 20,
                    "min_p": 0.0,
                    "repeat_penalty": 1.0,
                    "num_predict": max_tokens,
                }
            )
        else:
            # Default parameters for other models
            options.update(
                {
                    "top_p": 0.9,
                    "repeat_penalty": 1.1,
                    "num_predict": max_tokens,
                }
            )

        return options

    def generate(
        self,
        model: str,
        prompt: str,
        temperature: float | None = None,
        max_tokens: int | None = None,
        max_retries: int | None = None,
    ) -> str:
        """
        Generate text using Ollama API with retry logic.

        Note: Returns RAW response without cleaning (for batch processing).
        Cleaning should be done by caller if needed.

        Args:
            model: Model name
            prompt: Input prompt
            temperature: Sampling temperature (auto-detected if None)
            max_tokens: Maximum output tokens (task-specific optimization)
            max_retries: Maximum retry attempts (uses config default if None)

        Returns:
            Generated text (raw, no cleaning)

        Raises:
            RuntimeError: If generation fails after all retries
        """
        if max_retries is None:
            max_retries = self.config.max_retries

        options = self._get_model_options(model, temperature, max_tokens)

        # TRACE: Log full prompt (very verbose)
        logger.log(5, f"═══ API Request to [{model}] ═══")
        logger.log(5, f"Prompt ({len(prompt)} chars):\n{prompt}")
        logger.log(5, f"Options: {options}")

        for attempt in range(max_retries):
            try:
                # Build generate kwargs - use streaming
                generate_kwargs: dict[str, Any] = {
                    "model": model,
                    "prompt": prompt,
                    "stream": True,
                    "options": options,
                }

                # For reasoning models (Qwen3, DeepSeek-R1), explicitly disable thinking mode
                # to get direct responses instead of reasoning process
                if model.startswith(("qwen3", "deepseek-r1")):
                    generate_kwargs["think"] = False

                # Use streaming to match actual ollama library behavior
                response_stream = self.client.generate(**generate_kwargs)  # type: ignore[assignment]

                # Collect streaming response
                resp = ""
                thinking = ""
                for chunk in response_stream:  # type: ignore[assignment]
                    chunk_dict: dict[str, Any] = chunk if isinstance(chunk, dict) else {}  # type: ignore[assignment]
                    if chunk_dict.get("response"):
                        resp += str(chunk_dict["response"])
                    if chunk_dict.get("thinking"):
                        thinking += str(chunk_dict["thinking"])
                    if chunk_dict.get("done"):
                        break

                # Create response dict for compatibility with existing extraction logic
                response: dict[str, str] = {"response": resp, "thinking": thinking}

                # Log response type for debugging
                logger.log(
                    5,
                    f"Response type: {type(response)}, has 'response' attr: {hasattr(response, 'response')}",
                )

                # Handle reasoning models (DeepSeek-R1, etc.) that use 'thinking' field
                # Safely extract response text
                try:
                    resp = response.get("response", "")
                    thinking = response.get("thinking", "")
                    logger.log(5, f"Dict response: resp={type(resp)}, thinking={type(thinking)}")

                    # Convert to string and strip
                    resp = str(resp).strip() if resp else ""
                    thinking = str(thinking).strip() if thinking else ""

                    # Final validation
                    if not resp and not thinking:
                        logger.warning("⚠️ Both resp and thinking are empty after extraction")
                        logger.warning(f"Original response type: {type(response)}")
                        logger.warning(
                            f"Original response (first 200 chars): {str(response)[:200]}"
                        )

                except Exception as extract_error:
                    logger.warning(
                        f"⚠️ Error extracting response from [{model}]: {extract_error}, attempt {attempt + 1}/{max_retries}"
                    )
                    logger.warning(f"Response type was: {type(response)}")
                    if attempt < max_retries - 1:
                        continue
                    msg = f"Failed to extract response: {extract_error}"
                    raise ValueError(msg) from extract_error

                # If response is empty but thinking has content, use thinking
                # (happens with reasoning models that hit token limits)
                if not resp and thinking:
                    logger.debug(
                        f"Using 'thinking' field from reasoning model [{model}] (response field empty)"
                    )
                    resp = thinking

                # TRACE: Log full response (very verbose)
                logger.log(5, f"═══ API Response from [{model}] ═══")
                logger.log(5, f"Response ({len(resp)} chars):\n{resp}")
                if thinking and thinking != resp:
                    logger.log(5, f"Thinking ({len(thinking)} chars):\n{thinking}")

                # Validate response is not empty
                if not resp:
                    logger.warning(
                        f"⚠️ Empty response from [{model}], attempt {attempt + 1}/{max_retries}"
                    )
                    if attempt < max_retries - 1:
                        continue
                    msg = "Empty response from model"
                    raise ValueError(msg)

                # Return raw response (caller will parse/clean as needed)
                return resp

            except ResponseError as e:
                if e.status_code == 404:
                    logger.exception(f"❌ Model '{model}' not found")
                    logger.exception(f"   Install the model with: ollama pull {model}")
                    logger.exception("   Or check available models with: ollama list")
                    msg = f"Model '{model}' not available. Run: ollama pull {model}"
                    raise RuntimeError(msg) from e
                logger.warning(
                    f"⚠️ Ollama error for [{model}], attempt {attempt + 1}/{max_retries}: {e.error}"
                )
                if attempt == max_retries - 1:
                    msg = f"Ollama error: {e.error}"
                    raise RuntimeError(msg) from e

            except Exception as e:
                logger.warning(
                    f"⚠️ Request failed for [{model}], attempt {attempt + 1}/{max_retries}: {e}"
                )
                if attempt == max_retries - 1:
                    raise

        msg = f"Failed to get valid response from {model} after {max_retries} attempts"
        raise RuntimeError(msg)
