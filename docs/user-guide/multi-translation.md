# Multi-Language Translation

Translate subtitles to multiple languages in one command.

## Quick Start

```bash
# Translate to 3 languages at once
subs translate-multi input.srt --langs "dutch,spanish,french"

# Output files:
# - input.nl.srt (Dutch)
# - input.es.srt (Spanish)
# - input.fr.srt (French)
```

## Basic Usage

### Translate to Multiple Languages

```bash
subs translate-multi input.srt --langs "dutch,spanish,german"
```

This creates:
- `input.nl.srt` (Dutch)
- `input.es.srt` (Spanish)
- `input.de.srt` (German)

### With Custom Output Directory

```bash
subs translate-multi video/input.srt \
  --langs "dutch,spanish,french" \
  --output-dir translations/
```

Creates:
- `translations/input.nl.srt`
- `translations/input.es.srt`
- `translations/input.fr.srt`

## Supported Languages

Any language supported by your models:

```bash
# European languages
--langs "dutch,spanish,french,german,italian,portuguese"

# Asian languages
--langs "chinese,japanese,korean"

# Mixed
--langs "dutch,japanese,spanish,german"
```

## Performance

Multi-language translation is **optimized** for efficiency:

### Parallel Processing

Models are reused across languages:

```
Time →
Dutch:   [Model1] [Model2] [Model3] [Judge]
Spanish:          [Model1] [Model2] [Model3] [Judge]
French:                    [Model1] [Model2] [Model3] [Judge]
```

Models stay loaded in VRAM, reducing overhead.

### Shared Caching

Cache is shared across all languages:

```
Subtitle: "I love you"
Context: same for all languages

Cache key: hash(text + context + model + language)

First language: Builds cache
Other languages: Use same cache (different keys per language)
```

## Configuration

### Custom Models Per Language

Not currently supported directly, but you can chain commands:

```bash
# Dutch with specialist model
subs translate input.srt input.nl.srt \
  --lang dutch \
  --translation-models "bramvanroy/geitje-7b-ultra:Q8_0,qwen2.5:7b"

# Spanish with general models
subs translate input.srt input.es.srt \
  --lang spanish \
  --translation-models "qwen2.5:7b,llama3.2:3b"
```

### Context Settings

```bash
# More context for all languages
subs translate-multi input.srt \
  --langs "dutch,spanish,french" \
  --context 5
```

## Output Format

Output files follow SubRip naming convention:

```
input.srt          → Source file
input.nl.srt       → Dutch (Nederlands)
input.es.srt       → Spanish (Español)
input.fr.srt       → French (Français)
input.de.srt       → German (Deutsch)
input.it.srt       → Italian (Italiano)
input.pt.srt       → Portuguese (Português)
input.zh.srt       → Chinese (中文)
input.ja.srt       → Japanese (日本語)
input.ko.srt       → Korean (한국어)
```

## Complete Workflow

### Wedding Video to Multiple Languages

```bash
# Step 1: Transcribe
whisper wedding.mp4 --output wedding.srt

# Step 2: Fix grammar
subs fix wedding.srt wedding-corrected.srt

# Step 3: Translate to all needed languages
subs translate-multi wedding-corrected.srt \
  --langs "dutch,spanish,french,german" \
  --context 5

# Result:
# wedding-corrected.nl.srt
# wedding-corrected.es.srt
# wedding-corrected.fr.srt
# wedding-corrected.de.srt
```

## Performance Comparison

Test: 100 subtitles, 3 languages, RTX 3090

### Sequential (3 separate commands)

```bash
subs translate input.srt output.nl.srt --lang dutch  # 90s
subs translate input.srt output.es.srt --lang spanish  # 90s
subs translate input.srt output.fr.srt --lang french  # 90s
# Total: 270s
```

### Multi-language (1 command)

```bash
subs translate-multi input.srt --langs "dutch,spanish,french"
# Total: ~270s (models reloaded each time)
```

**Note:** Currently similar performance. Future optimizations will improve multi-language speed significantly.

## Best Practices

### For Quality

```bash
subs translate-multi input.srt \
  --langs "dutch,spanish,french" \
  --translation-models "qwen2.5:14b,mistral-nemo:12b" \
  --judge-model "qwen2.5:14b" \
  --context 5
```

### For Speed

```bash
subs translate-multi input.srt \
  --langs "dutch,spanish" \
  --translation-models "stablelm2:1.6b,phi3:3.8b" \
  --context 1
```

### For Consistency

Use the same models for all languages:

```bash
subs translate-multi input.srt \
  --langs "dutch,spanish,french,german" \
  --translation-models "qwen2.5:7b,llama3.2:3b"
```

This ensures consistent translation style across languages.

## Language-Specific Considerations

### Character Set Issues

Some languages require UTF-8 encoding:

```bash
# Verify encoding
file input.nl.srt

# Convert if needed
iconv -f ISO-8859-1 -t UTF-8 input.nl.srt -o input-utf8.nl.srt
```

### RTL Languages (Arabic, Hebrew)

SRT format supports RTL, but playback depends on video player:

```bash
subs translate-multi input.srt --langs "arabic"
# Creates input.ar.srt with RTL text
```

### Asian Languages (Chinese, Japanese, Korean)

No special configuration needed:

```bash
subs translate-multi input.srt --langs "chinese,japanese,korean"
```

Ensure models support these languages:
- `qwen2.5:7b` - Excellent for Chinese
- `qwen2.5:14b` - Good for Japanese/Korean
- `llama3.2:3b` - Basic support

## Batch Processing Multiple Files

Process multiple video files:

```bash
# Shell script
for video in *.mp4; do
  base="${video%.mp4}"
  subs translate-multi "${base}.srt" \
    --langs "dutch,spanish,french"
done
```

## Quality Verification

### Compare Translations

```bash
# View all translations side-by-side
diff -y input.nl.srt input.es.srt | less

# Count differences
diff input.nl.srt input.es.srt | wc -l
```

### Spot Check

```bash
# View specific subtitle across languages
sed -n '10,12p' input.nl.srt
sed -n '10,12p' input.es.srt
sed -n '10,12p' input.fr.srt
```

## Debugging

### Enable Debug Logging

```bash
subs translate-multi input.srt \
  --langs "dutch,spanish" \
  --log-level DEBUG
```

Shows:
- Processing order
- Model responses per language
- Cache statistics per language
- Performance metrics

### Check Individual Language

If one language has issues, translate it separately:

```bash
subs translate input.srt output.es.srt \
  --lang spanish \
  --log-level DEBUG
```

## Advanced Usage

### Progressive Quality

Translate important languages with better models:

```bash
# High quality for primary languages
subs translate input.srt input.nl.srt \
  --lang dutch \
  --translation-models "qwen2.5:14b,mistral-nemo:12b"

subs translate input.srt input.fr.srt \
  --lang french \
  --translation-models "qwen2.5:14b,mistral-nemo:12b"

# Fast for secondary languages
subs translate-multi input.srt \
  --langs "spanish,german,italian" \
  --translation-models "stablelm2:1.6b"
```

### Incremental Translation

Add languages over time:

```bash
# Initial release
subs translate-multi input.srt --langs "dutch,spanish"

# Later: add more languages
subs translate-multi input.srt --langs "french,german"

# Cache is preserved, no re-translation needed
```

## Limitations

1. **Same models for all languages**: Can't specify different models per language in one command
2. **Sequential processing**: Languages processed one after another (future: parallel)
3. **No language-specific context**: Same context window for all languages

## Workarounds

### Different Models Per Language

```bash
# Use separate commands with different models
subs translate input.srt input.nl.srt \
  --lang dutch \
  --translation-models "bramvanroy/geitje-7b-ultra:Q8_0"

subs translate input.srt input.es.srt \
  --lang spanish \
  --translation-models "qwen2.5:7b"
```

### Parallel Processing (Manual)

```bash
# Run in parallel (requires enough VRAM)
subs translate input.srt input.nl.srt --lang dutch &
subs translate input.srt input.es.srt --lang spanish &
subs translate input.srt input.fr.srt --lang french &
wait
```

**Note:** Requires 3x VRAM of your largest model!

## See Also

- [Single Language Translation](single-translation.md) - Detailed translation guide
- [Model Selection](models.md) - Choose best models for languages
- [Performance](../performance/optimization.md) - Optimize speed
- [Configuration](../getting-started/configuration.md) - Advanced settings
