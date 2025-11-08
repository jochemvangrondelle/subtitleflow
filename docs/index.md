# Subs - AI-Powered Subtitle Translation

Professional subtitle translation and correction using local LLMs via Ollama.

<div class="grid cards" markdown>

-   :material-lightning-bolt:{ .lg .middle } __Fast & Efficient__

    ---

    Batch processing and parallel model execution for maximum performance.

    [:octicons-arrow-right-24: Performance Guide](performance/optimization.md)

-   :material-robot:{ .lg .middle } __Multi-Model Ensemble__

    ---

    Use multiple LLMs and let a judge select the best translation.

    [:octicons-arrow-right-24: User Guide](user-guide/single-translation.md)

-   :material-translate:{ .lg .middle } __Multi-Language Support__

    ---

    Translate to multiple languages simultaneously with context awareness.

    [:octicons-arrow-right-24: Multi-Language](user-guide/multi-translation.md)

-   :material-cog:{ .lg .middle } __Highly Configurable__

    ---

    Fine-tune every aspect from models to context windows.

    [:octicons-arrow-right-24: Configuration](getting-started/configuration.md)

</div>

## Features

- **Grammar Correction**: Fix spelling and grammar mistakes in English subtitles
- **Context-Aware Translation**: Maintains context across subtitles for natural flow
- **Multi-Language Batch**: Translate to multiple languages in one pass
- **Music Detection**: Automatically preserves song lyrics in original language
- **Speaker Labels**: Maintains speaker identification and formatting
- **Intelligent Caching**: Context-aware caching reduces redundant API calls
- **Model Ensemble**: Use multiple models with judge selection for best quality
- **Beautiful CLI**: Rich terminal output with progress and colors

## Quick Example

```bash
# Fix grammar in English subtitles
subs fix input.srt corrected.srt

# Translate to Dutch
subs translate corrected.srt output.nl.srt --lang dutch

# Translate to multiple languages at once
subs translate-multi input.srt --langs "dutch,spanish,french"

# Fix grammar then translate in one command
subs both input.srt output.nl.srt --lang dutch
```

## Architecture Overview

```
┌─────────────┐
│  CLI Layer  │  Typer + Rich for beautiful terminal UX
└──────┬──────┘
       │
┌──────▼──────┐
│  Services   │  Business logic & orchestration
│             │  • TranslatorService
│             │  • JudgeService
│             │  • CacheService
└──────┬──────┘
       │
┌──────▼──────┐
│   Clients   │  External API integrations
│             │  • OllamaClient (official library)
└──────┬──────┘
       │
┌──────▼──────┐
│   Models    │  Domain objects & configuration
└─────────────┘
```

## Why Subs?

### Professional Quality
Built for wedding videos and professional content where quality matters. Multi-model ensemble with judge selection ensures the best possible translations.

### Local & Private
All processing happens locally using Ollama. No data sent to cloud services, complete privacy.

### Context-Aware
Unlike simple line-by-line translation, Subs maintains context across subtitles for natural, flowing translations that respect sentence boundaries and speaker continuity.

### Production Ready
- Comprehensive test suite (80%+ coverage)
- Strict type checking with mypy/pyright
- Clean architecture with separation of concerns
- Extensive error handling and retry logic

## Get Started

Ready to dive in? Start with the [Installation Guide](getting-started/installation.md) or jump straight to the [Quick Start](getting-started/quickstart.md).

## Support

- **Issues**: [GitHub Issues](https://github.com/jochemvangrondelle/subtitleflow/issues)
- **Discussions**: [GitHub Discussions](https://github.com/jochemvangrondelle/subtitleflow/discussions)
- **Documentation**: You're reading it! 📖
