# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Common utilities for subtitleflow."""

from subtitleflow.common.utils.batch_cache import BatchCache
from subtitleflow.common.utils.batching import (
    create_smart_batches,
    format_batch_for_translation,
    parse_batch_response,
)
from subtitleflow.common.utils.context_builder import build_translation_context
from subtitleflow.common.utils.display import (
    log_context,
    log_correction_batch,
    log_translation_batch,
)
from subtitleflow.common.utils.music_detection import is_music_line
from subtitleflow.common.utils.music_separator import (
    reconstruct_with_music,
    separate_music_from_subtitles,
)
from subtitleflow.common.utils.subtitle_utils import (
    is_caption_line,
    is_duplicate_subtitle,
)
from subtitleflow.common.utils.text_processing import (
    clean_ai_response,
    enforce_continuation_casing,
    enforce_ellipsis_continuation,
    preserve_formatting,
)

__all__ = [
    "BatchCache",
    "build_translation_context",
    "clean_ai_response",
    "create_smart_batches",
    "enforce_continuation_casing",
    "enforce_ellipsis_continuation",
    "format_batch_for_translation",
    "is_caption_line",
    "is_duplicate_subtitle",
    "is_music_line",
    "log_context",
    "log_correction_batch",
    "log_translation_batch",
    "parse_batch_response",
    "preserve_formatting",
    "reconstruct_with_music",
    "separate_music_from_subtitles",
]
