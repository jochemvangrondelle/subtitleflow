# Advanced Features

Advanced usage patterns and features.

## Environment Variables

### Ollama Configuration

```bash
# Custom Ollama server
export OLLAMA_HOST=http://192.168.1.100:11434

# Run translation
subs translate input.srt output.srt --lang dutch
```

### Logging Level

```bash
# Set default log level
export SUBS_LOG_LEVEL=DEBUG

# All commands now use DEBUG
subs translate input.srt output.srt --lang dutch
```

## Cache Management

### Cache Location

Default: `./srt_ollama_cache.json`

### Cache Structure

```json
{
  "hash_key": {
    "response": "translated text",
    "model": "qwen2.5:7b",
    "timestamp": "2025-01-01T12:00:00"
  }
}
```

### Cache Key Format

```
key = hash(text + context + language + model + mode)
```

### Custom Cache Location

```python
from subs.services.cache import CacheService

cache = CacheService(cache_file="custom_cache.json")
```

### Cache Statistics

```bash
# View cache size
ls -lh srt_ollama_cache.json

# Count cached entries
cat srt_ollama_cache.json | jq 'length'

# View specific entry
cat srt_ollama_cache.json | jq '."hash_key_here"'
```

## Performance Profiling

### Time Each Phase

```bash
time subs fix input.srt corrected.srt
time subs translate corrected.srt output.nl.srt --lang dutch
```

### Monitor GPU Usage

```bash
# Terminal 1: Run translation
subs translate input.srt output.nl.srt --lang dutch

# Terminal 2: Monitor GPU
watch -n 0.5 nvidia-smi
```

### Detailed Performance Metrics

Enable debug logging for timing information:

```bash
subs translate input.srt output.nl.srt \
  --lang dutch \
  --log-level DEBUG \
  2>&1 | grep "time\|took\|duration"
```

## Custom Model Configuration

### Testing New Models

```bash
# Try experimental model
ollama pull experimental-model:latest

subs translate input.srt output.srt \
  --lang dutch \
  --translation-models "experimental-model:latest,qwen2.5:7b"
```

### Model Comparison

```bash
# Translate with different models
subs translate input.srt output-qwen.nl.srt \
  --lang dutch \
  --translation-models "qwen2.5:7b"

subs translate input.srt output-llama.nl.srt \
  --lang dutch \
  --translation-models "llama3.2:3b"

# Compare results
diff -y output-qwen.nl.srt output-llama.nl.srt | less
```

## Programmatic Usage

### Python API

```python
from subs.models.config import AppConfig
from subs.services.translator import TranslatorService
from subs.clients.ollama import OllamaClient
from subs.models.subtitle import SubtitleFile

# Initialize
config = AppConfig()
client = OllamaClient(config.ollama_url)
translator = TranslatorService(client, config)

# Load subtitles
subtitle_file = SubtitleFile.load("input.srt")

# Translate
result = translator.translate(
    subtitles=subtitle_file.subtitles,
    target_lang="Dutch",
    models=["qwen2.5:7b", "llama3.2:3b"],
    judge_model="qwen2.5:7b",
    context_window=3
)

# Save
result.save("output.nl.srt")
```

### Custom Pipeline

```python
from subs.models.config import AppConfig
from subs.services.translator import TranslatorService
from subs.services.judge import JudgeService
from subs.clients.ollama import OllamaClient

config = AppConfig()
client = OllamaClient()
translator = TranslatorService(client, config)
judge = JudgeService(client)

# Custom workflow
for subtitle in subtitles:
    # Get translations from multiple models
    candidates = []
    for model in ["qwen2.5:7b", "llama3.2:3b"]:
        translation = translator.translate_single(
            subtitle, model, "Dutch", context
        )
        candidates.append(translation)

    # Judge selects best
    best = judge.select_best(
        subtitle.text, candidates, "Dutch", context
    )

    subtitle.text = best
```

## Integration with Other Tools

### Whisper for Transcription

```bash
# Transcribe with Whisper
whisper video.mp4 --output video.srt --language en

# Fix and translate
subs fix video.srt video-corrected.srt
subs translate video-corrected.srt video.nl.srt --lang dutch
```

### FFmpeg for Video Processing

```bash
# Burn subtitles into video
ffmpeg -i video.mp4 -vf subtitles=video.nl.srt output.mp4

# Create separate subtitle tracks
ffmpeg -i video.mp4 \
  -i video.nl.srt \
  -i video.es.srt \
  -c copy -c:s mov_text \
  -metadata:s:s:0 language=nld \
  -metadata:s:s:1 language=spa \
  output.mp4
```

### Batch Processing Script

```bash
#!/bin/bash
# process_videos.sh

for video in *.mp4; do
  base="${video%.mp4}"

  # Transcribe
  whisper "$video" --output "${base}.srt"

  # Fix grammar
  subs fix "${base}.srt" "${base}-corrected.srt"

  # Translate to multiple languages
  subs translate-multi "${base}-corrected.srt" \
    --langs "dutch,spanish,french"

  echo "Processed: $video"
done
```

## Error Recovery

### Handling Interruptions

Subs is resumable thanks to caching:

```bash
# Start processing (interrupted at subtitle 50)
subs translate long-video.srt output.nl.srt --lang dutch
^C  # Interrupted

# Resume (subtitles 1-50 are cached)
subs translate long-video.srt output.nl.srt --lang dutch
# Continues from where it left off
```

### Retry Failed Subtitles

If some subtitles fail:

```bash
# Enable debug to see failures
subs translate input.srt output.nl.srt \
  --lang dutch \
  --log-level DEBUG > translation.log 2>&1

# Identify failed subtitles
grep "ERROR" translation.log

# Clear cache and retry with different model
rm srt_ollama_cache.json
subs translate input.srt output.nl.srt \
  --lang dutch \
  --translation-models "qwen2.5:14b"
```

## Quality Assurance

### Validation Script

```python
import srt

def validate_translation(source_file, target_file):
    """Validate translated subtitles."""
    with open(source_file) as f:
        source = list(srt.parse(f.read()))

    with open(target_file) as f:
        target = list(srt.parse(f.read()))

    # Check counts match
    assert len(source) == len(target), "Subtitle count mismatch"

    # Check timings match
    for s, t in zip(source, target):
        assert s.start == t.start, f"Start time mismatch: {s.index}"
        assert s.end == t.end, f"End time mismatch: {s.index}"

    print("✓ Validation passed")

validate_translation("input.srt", "output.nl.srt")
```

### Spot Checking

```python
import random
import srt

def spot_check(source_file, target_file, n=10):
    """Randomly sample n subtitles for manual review."""
    with open(source_file) as f:
        source = list(srt.parse(f.read()))

    with open(target_file) as f:
        target = list(srt.parse(f.read()))

    indices = random.sample(range(len(source)), n)

    for i in indices:
        print(f"\n--- Subtitle {source[i].index} ---")
        print(f"Source: {source[i].content}")
        print(f"Target: {target[i].content}")
        input("Press Enter for next...")

spot_check("input.srt", "output.nl.srt")
```

## Optimization Techniques

### Pre-warming Models

Load models before processing:

```bash
# Pre-load models
ollama run qwen2.5:7b "test" > /dev/null
ollama run llama3.2:3b "test" > /dev/null

# Now translate (models already in memory)
subs translate input.srt output.nl.srt --lang dutch
```

### Parallel File Processing

Process multiple files in parallel:

```bash
# Using GNU parallel
parallel -j 3 'subs translate {} {.}.nl.srt --lang dutch' ::: *.srt

# Using xargs
find . -name "*.srt" | xargs -P 3 -I {} sh -c '
  subs translate "$1" "${1%.srt}.nl.srt" --lang dutch
' _ {}
```

**Note:** Requires sufficient VRAM for parallel Ollama instances.

## Debugging Techniques

### Verbose Ollama Logging

```bash
# Enable Ollama debug logs
OLLAMA_DEBUG=1 ollama serve

# In another terminal
subs translate input.srt output.nl.srt --lang dutch --log-level DEBUG
```

### Network Traffic Inspection

```bash
# Monitor Ollama API calls
tcpdump -i lo -A -s 0 'tcp port 11434'

# In another terminal
subs translate input.srt output.nl.srt --lang dutch
```

### Python Debugger

```python
import pdb
from subs.cli.main import app

# Set breakpoint
pdb.set_trace()

# Run CLI
app()
```

## Security Considerations

### Local Processing

All processing happens locally:
- No data sent to external APIs
- No internet required (after model download)
- Complete privacy

### Model Verification

Verify model integrity:

```bash
# Show model info
ollama show qwen2.5:7b

# List installed models
ollama list

# Verify official source
# All models from official Ollama library
```

### Cache Security

Cache file is plain JSON:

```bash
# Review cache
cat srt_ollama_cache.json | jq .

# Encrypt cache (optional)
gpg -c srt_ollama_cache.json
rm srt_ollama_cache.json

# Decrypt when needed
gpg -d srt_ollama_cache.json.gpg > srt_ollama_cache.json
```

## Troubleshooting Advanced Issues

### Memory Leaks

If Ollama memory grows:

```bash
# Restart Ollama
pkill ollama
ollama serve

# Resume translation
subs translate input.srt output.nl.srt --lang dutch
```

### Model Corruption

If model produces garbage:

```bash
# Remove corrupted model
ollama rm qwen2.5:7b

# Re-download
ollama pull qwen2.5:7b

# Verify
ollama run qwen2.5:7b "Test translation"
```

### Cache Corruption

If cache is invalid:

```bash
# Check cache validity
cat srt_ollama_cache.json | jq . > /dev/null

# If invalid, delete
rm srt_ollama_cache.json

# Restart translation
subs translate input.srt output.nl.srt --lang dutch
```

## See Also

- [API Reference](../api/services.md) - Python API documentation
- [Development Guide](../development/contributing.md) - Contribute to Subs
- [Performance Guide](../performance/optimization.md) - Optimization techniques
