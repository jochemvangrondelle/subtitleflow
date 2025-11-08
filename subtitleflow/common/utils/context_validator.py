# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Context window validation and automatic adjustment utilities."""

import logging

import langcodes

logger = logging.getLogger(__name__)

# Language expansion factors (how much longer translations are vs English)
LANGUAGE_EXPANSION_FACTORS = {
    # Romance languages (moderate expansion)
    "french": 1.15,
    "spanish": 1.10,
    "italian": 1.10,
    "portuguese": 1.15,
    # Germanic languages (can be verbose)
    "dutch": 1.30,  # Dutch can be quite verbose
    "german": 1.30,  # German compound words and grammar
    "danish": 1.20,
    "swedish": 1.20,
    "norwegian": 1.20,
    # Slavic languages (variable)
    "russian": 1.10,
    "polish": 1.15,
    "czech": 1.15,
    # Asian languages (usually shorter)
    "chinese": 0.80,
    "japanese": 0.85,
    "korean": 0.90,
    # Other languages
    "finnish": 1.40,  # Highly inflected, can be very verbose
    "turkish": 1.25,
    "arabic": 1.05,
    "hindi": 1.10,
    # Default for unknown languages
    "default": 1.20,  # Conservative 20% expansion
}


def estimate_tokens(text: str) -> int:
    """
    Estimate token count for text.

    Rule of thumb: 1 token ≈ 4 characters for English
    More conservative for multilingual content.

    Args:
        text: Input text

    Returns:
        Estimated token count
    """
    # Conservative estimate: 3.5 chars per token (accounts for multilingual)
    return int(len(text) / 3.5)


def get_expansion_factor(target_language: str | None = None) -> float:
    """
    Get translation expansion factor for target language.

    Some languages are more verbose than English and translations
    will be longer than the source text.

    Uses langcodes library to normalize language codes/names.

    Args:
        target_language: Target language name (e.g., "dutch", "nl", "deu")

    Returns:
        Expansion factor (1.0 = same length, 1.3 = 30% longer)
    """
    if not target_language:
        return LANGUAGE_EXPANSION_FACTORS["default"]

    # Normalize using langcodes library
    try:
        # Parse language tag and get autonym (language's name for itself)
        lang = langcodes.Language.get(target_language)

        # Get the base language code (e.g., "nl" from "nl-NL")
        lang_code = lang.language if lang.language else None

        if not lang_code:
            return LANGUAGE_EXPANSION_FACTORS["default"]

        # Try to get English name for the language
        try:
            lang_name = lang.language_name("en").lower()
        except (LookupError, AttributeError):
            # If we can't get the name, use the code
            lang_name = lang_code

        # Check both the English name and the ISO code
        for key in [lang_name, lang_code]:
            if key in LANGUAGE_EXPANSION_FACTORS:
                return LANGUAGE_EXPANSION_FACTORS[key]

        # Fall back to checking if it's a 3-letter ISO code
        try:
            alpha3 = lang.to_alpha3()
            # Map common 3-letter codes
            alpha3_map = {
                "nld": "dutch",
                "deu": "german",
                "fra": "french",
                "spa": "spanish",
                "ita": "italian",
                "por": "portuguese",
                "rus": "russian",
                "zho": "chinese",
                "jpn": "japanese",
                "kor": "korean",
                "ara": "arabic",
                "hin": "hindi",
                "fin": "finnish",
                "tur": "turkish",
                "pol": "polish",
                "ces": "czech",
                "dan": "danish",
                "swe": "swedish",
                "nor": "norwegian",
            }
            if alpha3 in alpha3_map:
                return LANGUAGE_EXPANSION_FACTORS[alpha3_map[alpha3]]
        except (LookupError, AttributeError):
            pass

    except Exception as e:
        # If langcodes fails, fall back to simple string matching
        logger.debug(f"langcodes failed for '{target_language}': {e}, using fallback")
        lang_lower = target_language.lower().strip()
        return LANGUAGE_EXPANSION_FACTORS.get(lang_lower, LANGUAGE_EXPANSION_FACTORS["default"])

    # Default fallback
    return LANGUAGE_EXPANSION_FACTORS["default"]


def validate_context_fit(
    prompt_text: str,
    expected_output_tokens: int,
    num_ctx: int,
    safety_margin: float = 0.1,
    target_language: str | None = None,
) -> tuple[bool, int, str]:
    """
    Validate if prompt + output will fit in context window.

    IMPORTANT: Accounts for translation expansion - some languages (Dutch, German, Finnish)
    can be 20-40% more verbose than English source text.

    Args:
        prompt_text: Full prompt text (including context and batch)
        expected_output_tokens: Expected number of output tokens (pre-expansion)
        num_ctx: Context window size
        safety_margin: Reserve this fraction as safety buffer (default 10%)
        target_language: Target language (for expansion factor calculation)

    Returns:
        Tuple of (fits: bool, tokens_needed: int, recommendation: str)
    """
    # Estimate input tokens
    input_tokens = estimate_tokens(prompt_text)

    # Apply language expansion factor to output tokens
    expansion_factor = get_expansion_factor(target_language)
    adjusted_output_tokens = int(expected_output_tokens * expansion_factor)

    # Log expansion if significant
    if expansion_factor > 1.15:
        logger.debug(
            f"Applying {expansion_factor}x expansion factor for {target_language or 'unknown'} language"
        )
        logger.debug(f"  Output tokens: {expected_output_tokens} → {adjusted_output_tokens}")

    # Calculate total needed
    total_needed = input_tokens + adjusted_output_tokens

    # Apply safety margin
    safe_limit = int(num_ctx * (1 - safety_margin))

    # Check if it fits
    fits = total_needed <= safe_limit

    # Generate recommendation
    if fits:
        utilization = (total_needed / safe_limit) * 100
        lang_note = (
            f" ({target_language}, {expansion_factor}x)"
            if target_language and expansion_factor != 1.0
            else ""
        )
        if utilization > 80:
            recommendation = f"⚠️  High context usage ({utilization:.1f}%{lang_note}) - consider reducing batch size"
        else:
            recommendation = f"✓ Context usage OK ({utilization:.1f}%{lang_note})"
    else:
        overflow = total_needed - safe_limit
        recommendation = f"❌ Context overflow by {overflow} tokens - will auto-adjust"

    return fits, total_needed, recommendation


def calculate_safe_batch_size(
    prompt_template_tokens: int,
    context_tokens: int,
    avg_subtitle_tokens: int,
    avg_output_per_subtitle: int,
    num_ctx: int,
    safety_margin: float = 0.1,
    target_language: str | None = None,
) -> int:
    """
    Calculate maximum safe batch size that fits in context window.

    IMPORTANT: Accounts for translation expansion when target_language is provided.

    Args:
        prompt_template_tokens: Base prompt template size
        context_tokens: Previous context size
        avg_subtitle_tokens: Average tokens per subtitle input
        avg_output_per_subtitle: Average tokens per subtitle output (will be expanded)
        num_ctx: Context window size
        safety_margin: Reserve this fraction as safety buffer
        target_language: Target language (for expansion factor)

    Returns:
        Maximum safe batch size
    """
    # Available tokens after prompt and context
    safe_limit = int(num_ctx * (1 - safety_margin))
    available = safe_limit - prompt_template_tokens - context_tokens

    # Apply language expansion factor to output
    expansion_factor = get_expansion_factor(target_language)
    adjusted_output_per_subtitle = int(avg_output_per_subtitle * expansion_factor)

    # Tokens needed per subtitle (input + expanded output + numbering overhead)
    tokens_per_subtitle = avg_subtitle_tokens + adjusted_output_per_subtitle + 5

    # Calculate max batch size
    max_batch_size = max(1, int(available / tokens_per_subtitle))

    lang_info = f" ({target_language}, {expansion_factor}x)" if target_language else ""
    logger.debug(f"Context budget: {safe_limit} tokens")
    logger.debug(f"  Template: {prompt_template_tokens}")
    logger.debug(f"  Context: {context_tokens}")
    logger.debug(f"  Available: {available}")
    logger.debug(
        f"  Per subtitle: {tokens_per_subtitle} (input:{avg_subtitle_tokens} + output:{adjusted_output_per_subtitle}{lang_info} + overhead:5)"
    )
    logger.debug(f"  Max batch: {max_batch_size}")

    return max_batch_size


def auto_adjust_batch(
    batch: list,
    prompt_template: str,
    context_text: str,
    num_ctx: int,
    avg_output_per_item: int = 100,
    target_language: str | None = None,
) -> tuple[list, bool, str]:
    """
    Automatically adjust batch size if it won't fit in context.

    IMPORTANT: Accounts for translation expansion when target_language is provided.

    Args:
        batch: List of items to process
        prompt_template: Prompt template (without batch content)
        context_text: Context text (previous items)
        num_ctx: Context window size
        avg_output_per_item: Expected output tokens per item (will be expanded)
        target_language: Target language (for expansion factor)

    Returns:
        Tuple of (adjusted_batch: List, was_split: bool, reason: str)
    """
    # Calculate average subtitle size from batch
    if batch:
        avg_item_tokens = sum(estimate_tokens(str(item)) for item in batch) // len(batch)
    else:
        avg_item_tokens = 50  # Default estimate

    # Estimate prompt tokens
    prompt_tokens = estimate_tokens(prompt_template)
    context_tokens = estimate_tokens(context_text) if context_text else 0

    # Apply language expansion factor to output
    expansion_factor = get_expansion_factor(target_language)
    adjusted_output_per_item = int(avg_output_per_item * expansion_factor)

    # Calculate expected total for current batch
    batch_input_tokens = sum(estimate_tokens(str(item)) for item in batch)
    batch_output_tokens = len(batch) * adjusted_output_per_item
    total_tokens = prompt_tokens + context_tokens + batch_input_tokens + batch_output_tokens

    # Check if it fits (with 10% safety margin)
    safe_limit = int(num_ctx * 0.9)

    if total_tokens <= safe_limit:
        # Fits comfortably
        lang_note = f", {target_language} {expansion_factor}x" if target_language else ""
        return (
            batch,
            False,
            f"Batch fits in context ({total_tokens}/{safe_limit} tokens{lang_note})",
        )

    # Need to split - calculate safe batch size
    safe_batch_size = calculate_safe_batch_size(
        prompt_tokens,
        context_tokens,
        avg_item_tokens,
        avg_output_per_item,
        num_ctx,
        target_language=target_language,
    )

    if safe_batch_size >= len(batch):
        # Should fit but our estimate was wrong - warn but proceed
        logger.warning(
            "⚠️  Context estimate suggests overflow but calculated batch size OK - proceeding"
        )
        return batch, False, "Proceeding with caution"

    # Split batch
    adjusted_batch = batch[:safe_batch_size]
    lang_note = (
        f" (with {expansion_factor}x {target_language} expansion)"
        if target_language and expansion_factor > 1.1
        else ""
    )
    reason = f"Batch too large for context{lang_note} ({total_tokens}/{safe_limit} tokens) - split {len(batch)} → {safe_batch_size}"

    logger.warning(f"⚠️  {reason}")

    return adjusted_batch, True, reason


def reduce_context_intelligently(
    context_items: list[tuple[str, str]], target_tokens: int
) -> list[tuple[str, str]]:
    """
    Reduce context items to fit within target token budget.

    Keeps most recent items (most relevant for continuity).

    Args:
        context_items: List of (original, translated) pairs
        target_tokens: Target token count

    Returns:
        Reduced context items
    """
    if not context_items:
        return []

    # Start from most recent and work backwards
    reduced = []
    current_tokens = 0

    for item in reversed(context_items):
        item_tokens = estimate_tokens(item[0]) + estimate_tokens(item[1])

        if current_tokens + item_tokens <= target_tokens:
            reduced.insert(0, item)  # Insert at beginning to maintain order
            current_tokens += item_tokens
        else:
            break

    if len(reduced) < len(context_items):
        logger.debug(
            f"Reduced context: {len(context_items)} → {len(reduced)} items ({current_tokens} tokens)"
        )

    return reduced
