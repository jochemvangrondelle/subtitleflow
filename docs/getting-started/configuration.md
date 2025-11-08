# Configuration

Subs is highly configurable to match your workflow and requirements.

## Model Configuration

### Grammar Models

For English grammar/spelling correction:

```bash
subs fix input.srt output.srt \
  --grammar-models "qwen3:14b,gemma2:9b,llama3:8b"
```

**Recommendations:**
- **Fast**: `gemma2:9b` (single model)
- **Quality**: `qwen3:14b,gemma2:9b` (ensemble)
- **Best**: `qwen3:14b,gemma2:9b,llama3:70b` (slower but excellent)

### Translation Models

For translating to target languages:

```bash
subs translate input.srt output.srt \
  --translation-models "qwen3:14b,mistral-nemo:12b"
```

**Recommendations:**
- **Fast**: `mistral:7b` (single model)
- **Quality**: `qwen3:14b,mistral-nemo:12b` (ensemble)
- **Best**: `qwen3:14b,llama3:70b` (requires more VRAM)

### Judge Model

Selects best result when using multiple models:

```bash
--judge-model "qwen3:14b"
```

**Tips:**
- Use your strongest model as judge
- Judge model should understand both source and target languages
- Setting judge = one of your workers saves a model load

## Context Window

How many previous subtitles to consider for context:

```bash
--context 3  # Default
--context 5  # More context (better but slower)
--context 1  # Less context (faster but may miss continuations)
```

**When to adjust:**
- **Increase** for complex dialogues with many sentence continuations
- **Decrease** for simple content or speed
- **Default (3)** works well for most content

## Language Configuration

### Single Language

```bash
subs translate input.srt output.srt --lang dutch
```

Supported languages:
- Dutch (`dutch` or `nl`)
- Spanish (`spanish` or `es`)
- French (`french` or `fr`)
- German (`german` or `de`)
- Italian (`italian` or `it`)
- Portuguese (`portuguese` or `pt`)
- Russian (`russian` or `ru`)
- Chinese (`chinese` or `zh`)
- Japanese (`japanese` or `ja`)
- Korean (`korean` or `ko`)
- Arabic (`arabic` or `ar`)
- Hindi (`hindi` or `hi`)

### Multiple Languages

```bash
subs translate-multi input.srt \
  --langs "dutch,spanish,french,german"
```

**Batch Efficiency:**
- Multi-language mode translates all languages in one pass per model
- Significantly faster than running translate multiple times
- Recommended for 2+ target languages

## Output Configuration

### Output Naming

Single language:
```bash
# Explicit output name
subs translate input.srt output.nl.srt --lang dutch

# Will create: output.nl.srt
```

Multi-language:
```bash
# Specify output directory
subs translate-multi input.en.srt --output-dir ./subs --langs "dutch,spanish"

# Will create:
#   ./subs/input.nl.srt
#   ./subs/input.es.srt
```

File naming follows SubRip conventions:
- `filename.{language_code}.srt`
- Language codes: ISO 639-1 (nl, es, fr, etc.)

## Logging

Control output verbosity:

```bash
--log-level INFO    # Default: Show progress
--log-level DEBUG   # Verbose: Show all details
--log-level WARNING # Quiet: Only warnings/errors
--log-level ERROR   # Silent: Only errors
```

**Debug mode shows:**
- Every subtitle being processed
- Model outputs before judging
- Cache hits/misses
- API calls and timing

## Environment Variables

### Ollama URL

```bash
export OLLAMA_URL="http://127.0.0.1:11434"
# or
export OLLAMA_URL="http://remote-server:11434"
```

### Cache File Location

Currently hardcoded to `srt_ollama_cache.json` in working directory. Customization coming soon.

## Advanced Configuration

### Model-Specific Parameters

Subs automatically optimizes parameters per model:

**Qwen3 models:**
- Temperature: 0.7
- top_p: 0.8
- top_k: 20
- Thinking mode: disabled

**Other models:**
- Temperature: 0.1 (more deterministic)
- top_p: 0.9
- repeat_penalty: 1.1

These are auto-configured in `OllamaClient._get_model_options()`.

### Retry Logic

Automatic retry with exponential backoff:
- Max retries: 3 (configurable in code)
- Timeout: 900 seconds per call
- Handles transient Ollama errors

## Configuration File

Currently, configuration is via CLI args. Configuration file support coming soon:

```yaml
# Future: subs.config.yaml
models:
  grammar: [qwen3:14b, gemma2:9b]
  translation: [qwen3:14b, mistral-nemo:12b]
  judge: qwen3:14b

context_window: 3
cache_file: ~/.cache/subs/cache.json

ollama:
  url: http://127.0.0.1:11434
  timeout: 900
```

## Performance Tuning

See [Performance Optimization](../performance/optimization.md) for detailed tuning guide.

**Quick tips:**
- Single model = no judging overhead
- Smaller models = faster
- Reduce context window = faster
- Cache warms up after first run
