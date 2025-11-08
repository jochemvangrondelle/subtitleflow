# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Constants for subtitleflow - messages, prompts, and display formatting."""

from subtitleflow.common.constants.display import (
    SEPARATOR,
    SEPARATOR_DOUBLE,
    SEPARATOR_THIN,
)
from subtitleflow.common.constants.messages import (
    MSG_CACHE_HIT,
    MSG_CACHE_MISS,
    MSG_COMPLETE,
    MSG_DEDUPLICATED,
    MSG_EMPTY_RESPONSE,
    MSG_ERROR,
    MSG_FILE_NOT_FOUND,
    MSG_MODEL_NOT_FOUND,
    MSG_MODELS_AVAILABLE,
    MSG_MODELS_MISSING,
    MSG_OLLAMA_ACCESSIBLE,
    MSG_OLLAMA_NOT_ACCESSIBLE,
    MSG_PARSING_FAILED,
    MSG_PARTIAL_PARSE,
    MSG_SUCCESS,
    MSG_WARNING,
)
from subtitleflow.common.constants.prompts import (
    GRAMMAR_INSTR,
    JUDGE_INSTR,
    TRANSLATE_INSTR,
)

__all__ = [
    # Prompts
    "GRAMMAR_INSTR",
    "JUDGE_INSTR",
    # Messages
    "MSG_CACHE_HIT",
    "MSG_CACHE_MISS",
    "MSG_COMPLETE",
    "MSG_DEDUPLICATED",
    "MSG_EMPTY_RESPONSE",
    "MSG_ERROR",
    "MSG_FILE_NOT_FOUND",
    "MSG_MODELS_AVAILABLE",
    "MSG_MODELS_MISSING",
    "MSG_MODEL_NOT_FOUND",
    "MSG_OLLAMA_ACCESSIBLE",
    "MSG_OLLAMA_NOT_ACCESSIBLE",
    "MSG_PARSING_FAILED",
    "MSG_PARTIAL_PARSE",
    "MSG_SUCCESS",
    "MSG_WARNING",
    # Display
    "SEPARATOR",
    "SEPARATOR_DOUBLE",
    "SEPARATOR_THIN",
    "TRANSLATE_INSTR",
]
