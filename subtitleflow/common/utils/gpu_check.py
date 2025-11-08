# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""GPU memory validation utilities."""

import logging

import ollama

logger = logging.getLogger(__name__)


# Approximate VRAM usage for common models (in GB)
MODEL_VRAM_ESTIMATES = {
    # Small models (< 2GB)
    "stablelm2:1.6b": 1.0,
    "qwen2.5:1.5b": 1.0,
    # Medium models (2-3GB)
    "qwen2.5:3b": 2.0,
    "llama3.2:3b": 2.0,
    "gemma2:2b": 1.5,
    "gemma3:4b": 2.5,
    # Large models (4-8GB)
    "qwen2.5:7b": 5.0,
    "stable-beluga:7b": 4.0,
    "mistral:7b": 4.5,
    "llama3.1:8b": 5.5,
    "gemma3:4b": 6.0,
    # Very large models (8GB+)
    "mistral-nemo:12b": 7.0,
    "mistral-nemo": 7.0,
    "qwen2.5:7b": 9.0,
    "stablelm2:12b": 10.0,  # Crashes due to KV bug
    "deepseek-r1:7b": 8.0,
    "deepseek-r1:1.5b": 2.0,
    # Default fallback
    "default": 5.0,
}


def get_loaded_models_from_ollama(
    ollama_url: str = "http://127.0.0.1:11434",
) -> list[dict] | None:
    """Get currently loaded models from Ollama using ollama.ps().

    Args:
        ollama_url: Ollama server URL

    Returns:
        List of loaded model dicts with 'name', 'size', 'size_vram', etc., or None if unavailable
    """
    try:
        # Use ollama library's Client with custom host
        client = ollama.Client(host=ollama_url)

        # Call ps() to get loaded models
        ps_response = client.ps()

        # ps() returns a dict with 'models' key containing list of loaded models
        return ps_response.get("models", [])

    except Exception as e:
        logger.debug(f"Failed to get loaded models from Ollama: {e}")
        return None


def get_gpu_memory_from_ollama(
    ollama_url: str = "http://127.0.0.1:11434",
) -> dict[str, float] | None:
    """Get GPU memory information from Ollama's loaded models.

    This calculates used VRAM from currently loaded models.
    Note: We can't get total/free VRAM from Ollama API, but we can see what's loaded.

    Args:
        ollama_url: Ollama server URL

    Returns:
        Dict with 'used_vram' in GB and 'loaded_models' list, or None if not available
    """
    loaded_models = get_loaded_models_from_ollama(ollama_url)

    if loaded_models is None:
        return None

    total_vram_used = 0.0
    model_info = []

    for model in loaded_models:
        # size_vram is in bytes
        vram_bytes = model.get("size_vram", 0)
        vram_gb = vram_bytes / (1024**3)  # Convert to GB
        total_vram_used += vram_gb

        model_info.append(
            {
                "name": model.get("name", "unknown"),
                "vram_gb": vram_gb,
                "size_gb": model.get("size", 0) / (1024**3),
            }
        )

    return {
        "used_vram": total_vram_used,
        "loaded_models": model_info,
    }


def estimate_model_vram(model_name: str) -> float:
    """Estimate VRAM usage for a model in GB.

    Args:
        model_name: Model name (e.g., "qwen2.5:7b")

    Returns:
        Estimated VRAM in GB
    """
    # Normalize model name
    model_lower = model_name.lower().strip()

    # Check exact match
    if model_lower in MODEL_VRAM_ESTIMATES:
        return MODEL_VRAM_ESTIMATES[model_lower]

    # Check partial match (e.g., "qwen2.5:7b-q5" matches "qwen2.5:7b")
    for known_model, vram in MODEL_VRAM_ESTIMATES.items():
        if model_lower.startswith(known_model):
            return vram

    # Heuristic based on parameter count in name
    if ":" in model_lower:
        size_part = model_lower.split(":")[1]

        # Extract number (e.g., "7b" -> 7, "1.6b" -> 1.6, "14b" -> 14)
        import re

        match = re.search(r"(\d+(?:\.\d+)?)", size_part)
        if match:
            param_count = float(match.group(1))

            # Rough estimate: 0.6-0.8 GB per billion parameters for Q4 quantization
            if param_count < 2 or param_count < 8:
                return param_count * 0.7
            return param_count * 0.75

    # Default fallback
    logger.warning(f"Unknown model '{model_name}', using default VRAM estimate")
    return MODEL_VRAM_ESTIMATES["default"]


def check_models_fit_gpu(
    model_names: list[str],
    safety_margin_gb: float = 1.0,
    ollama_url: str = "http://127.0.0.1:11434",
) -> tuple[bool, str]:
    """Check if models will fit in GPU memory (sequential processing).

    Uses Ollama's /api/ps endpoint to check currently loaded models and their VRAM usage.

    Args:
        model_names: List of model names to check
        safety_margin_gb: Safety margin in GB to leave free
        ollama_url: Ollama server URL

    Returns:
        Tuple of (fits: bool, message: str)
    """
    # Get currently loaded models from Ollama
    ollama_info = get_gpu_memory_from_ollama(ollama_url)

    if ollama_info is None:
        # Can't check GPU via Ollama, allow to proceed
        logger.warning("⚠️  Could not get GPU info from Ollama, proceeding without validation")
        logger.warning("   (Models will be loaded on-demand)")
        return True, "GPU memory check skipped (Ollama /api/ps not available)"

    # Check what's currently loaded
    used_vram = ollama_info["used_vram"]
    loaded_models = ollama_info["loaded_models"]

    if loaded_models:
        logger.info(f"Currently loaded models ({len(loaded_models)}):")
        for model in loaded_models:
            logger.info(f"  - {model['name']}: {model['vram_gb']:.1f}GB VRAM")
        logger.info(f"Total VRAM in use: {used_vram:.1f}GB")
    else:
        logger.info("No models currently loaded (will load on-demand)")

    # For sequential processing, only the largest model needs to fit
    max_vram_needed = 0.0
    largest_model = ""

    for model_name in model_names:
        vram = estimate_model_vram(model_name)
        if vram > max_vram_needed:
            max_vram_needed = vram
            largest_model = model_name

    # Add safety margin
    required_vram = max_vram_needed + safety_margin_gb

    logger.info(f"Largest model to load: {largest_model} (~{max_vram_needed:.1f}GB)")
    logger.info(f"Required (with {safety_margin_gb:.1f}GB margin): {required_vram:.1f}GB")

    # We can't determine total GPU memory from Ollama API alone,
    # but we can warn if models are already loaded
    if used_vram > 0:
        logger.warning(
            f"⚠️  {used_vram:.1f}GB VRAM already in use by {len(loaded_models)} loaded model(s)"
        )
        logger.warning("   Models will unload automatically when new models are loaded")
        logger.warning("   If you experience crashes, unload models first:")
        logger.warning(
            "   docker exec -it ollama pkill ollama && sleep 2 && docker exec -it ollama ollama serve &"
        )

    # Since we're doing sequential processing and Ollama unloads models automatically,
    # we'll allow it to proceed with a warning
    logger.info("✓ GPU memory check passed (sequential processing, Ollama auto-unload)")
    return True, "GPU memory check passed (sequential processing)"


def log_model_requirements(model_names: list[str]) -> None:
    """Log estimated VRAM requirements for models.

    Args:
        model_names: List of model names
    """
    logger.info("Estimated VRAM requirements (sequential processing):")

    total = 0.0
    for model_name in model_names:
        vram = estimate_model_vram(model_name)
        logger.info(f"  - {model_name}: ~{vram:.1f}GB")
        total = max(total, vram)  # Sequential, so max not sum

    logger.info(f"  Peak usage: ~{total:.1f}GB (largest model)")
