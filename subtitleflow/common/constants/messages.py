# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Common log messages and user-facing strings."""

# Status messages
MSG_SUCCESS = "✓"
MSG_ERROR = "❌"
MSG_WARNING = "⚠️"
MSG_INFO = "ℹ️"

# File operations
MSG_FILE_NOT_FOUND = "❌ {file_type} file not found: {path}"
MSG_FILE_LOADED = "✓ Loaded {count} subtitles"
MSG_FILE_SAVED = "✓ Output saved to: {path}"

# Ollama server
MSG_OLLAMA_ACCESSIBLE = "✓ Ollama server accessible"
MSG_OLLAMA_NOT_ACCESSIBLE = "❌ Ollama server not accessible"
MSG_OLLAMA_CONNECTION_ERROR = "❌ Cannot connect to Ollama server: {error}\n   Server URL: {url}\n   Is Ollama running? Start it with: ollama serve"

# Models
MSG_MODELS_AVAILABLE = "✓ All models available"
MSG_MODELS_MISSING = "❌ Missing models: {models}"
MSG_MODEL_NOT_FOUND = "❌ Model '{model}' not found\n   Install the model with: ollama pull {model}\n   Or check available models with: ollama list"
MSG_MODEL_INSTALL = "  ollama pull {model}"

# Processing
MSG_STARTING = "Starting {operation}..."
MSG_COMPLETE = "✓ {operation} complete"
MSG_PROCESSING = "Processing {item}..."
MSG_BATCH_PROCESSING = "=== Batch {current}/{total} === ({count} subtitles)"

# Cache
MSG_CACHE_HIT = "Cache HIT for {section}: {text}..."
MSG_CACHE_MISS = "Cache MISS for {section}: {text}..."
MSG_ALL_CACHED = "All {count} items found in cache, skipping API call"
MSG_DEDUPLICATED = "Deduplicated batch: {total} items → {unique} unique items"
MSG_CACHE_STATS = "Cache: {cached}/{total} items found in cache"

# Errors and warnings
MSG_EMPTY_RESPONSE = "⚠️ Empty response from [{model}], attempt {attempt}/{max_retries}"
MSG_PARSING_FAILED = "⚠️ Batch parsing failed for {count} subtitles"
MSG_PARTIAL_PARSE = "⚠️ Partial parse: got {got}/{expected} {items}"
MSG_EMPTY_CORRECTION = "⚠️ Empty correction for subtitle {index}: '{content}'"
MSG_EMPTY_TRANSLATION = "⚠️ Empty translation for subtitle {index}: '{content}'"
MSG_CLEANING_REMOVED_ALL = "⚠️ Cleaning removed all content for: '{original}' (was: '{cleaned}')"
MSG_MISSING_RESULT = "Missing {type} at position {position}, using original"
MSG_BATCH_FAILED = "⚠️ [{model}] Batch {batch} failed, using original text"
MSG_JUDGE_FAILED = "⚠️ Judge failed for subtitle {index}: {error}, using first model's result"

# Music lines
MSG_MUSIC_SKIP = "Found {count} music lines (will skip {operation}), {regular} regular subtitles"
MSG_MUSIC_PRESERVED = "Kept music line at index {index}: {content}..."

# Duplicates
MSG_DUPLICATES_REMOVED = "Removed {count} consecutive duplicate subtitles"
MSG_DUPLICATE_INDEX = "Removing duplicate subtitle at index {index}: '{content}'"

# Context
MSG_CONTEXT_PREVIOUS = "Context (previous {type}):"

# GPU
MSG_GPU_CHECK = "Checking GPU memory..."
MSG_GPU_INSUFFICIENT = "❌ Insufficient GPU memory: {message}"

# Transcription
MSG_TRANSCRIBING = "🎬 Transcribing: {file}"
MSG_TRANSCRIBING_OUTPUT = "📝 Output: {file}"
MSG_TRANSCRIBING_COMPLETE = "✅ Transcription complete: {file}"
MSG_EXTRACTING_AUDIO = "🎧 Extracting audio..."
MSG_AUDIO_EXTRACTED = "✓ Audio extracted"
MSG_TRANSCRIBING_WITH_WHISPER = "🗣️ Transcribing with WhisperX (model: {model})..."
MSG_CONVERTING_TO_SRT = "📝 Converting to SRT format..."

# Translation
MSG_TRANSLATING = "🌍 Translating to {language}..."
MSG_TRANSLATION_COMPLETE = "✓ Translation complete"

# Grammar correction
MSG_GRAMMAR_STARTING = "Starting grammar correction on {count} subtitles"
MSG_GRAMMAR_MODELS = "Using models: {models}"
MSG_GRAMMAR_COMPLETE = "Grammar correction complete"
MSG_FINAL_COUNT = "Final subtitle count: {count} (removed {duplicates} duplicates)"

# Version
MSG_VERSION = "subtitleflow version {version}"
