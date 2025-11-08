# Single Language Translation

Translate subtitles to one target language.

## Quick Start

```bash
# Translate to Dutch
subs translate input.srt output.nl.srt --lang dutch

# Translate to Spanish
subs translate input.srt output.es.srt --lang spanish

# Translate to French
subs translate input.srt output.fr.srt --lang french
```

## Basic Translation

### Default Configuration

```bash
subs translate input.srt output.nl.srt --lang dutch
```

This uses:
- 3 translation models (ensemble)
- Judge to select best translation
- Context window of 3 subtitles
- Smart caching

### Custom Models

```bash
subs translate input.srt output.nl.srt \
  --lang dutch \
  --translation-models "qwen2.5:14b,mistral-nemo:12b" \
  --judge-model "qwen2.5:14b"
```

### Single Model (No Judge)

```bash
subs translate input.srt output.nl.srt \
  --lang dutch \
  --translation-models "qwen2.5:7b"
```

## Supported Languages

Subs supports all languages supported by your chosen models:

### Most Common

- **Dutch** (Nederlands)
- **Spanish** (Español)
- **French** (Français)
- **German** (Deutsch)
- **Italian** (Italiano)
- **Portuguese** (Português)
- **Chinese** (中文)
- **Japanese** (日本語)
- **Korean** (한국어)

### Language-Specific Optimization

**Dutch:**
```bash
subs translate input.srt output.nl.srt \
  --lang dutch \
  --translation-models "bramvanroy/geitje-7b-ultra:Q8_0,qwen2.5:7b"
```

**Spanish:**
```bash
subs translate input.srt output.es.srt \
  --lang spanish \
  --translation-models "llama3.2:3b,qwen2.5:7b"
```

**German:**
```bash
subs translate input.srt output.de.srt \
  --lang german \
  --translation-models "qwen2.5:14b,mistral-nemo:12b"
```

## Context-Aware Translation

Subs maintains context across subtitles for natural translations:

```
Subtitle 10: "I went to the market"
Subtitle 11: "bought some vegetables"  ← Current
Subtitle 12: "and then went home"

Context helps translate:
- "bought" as continuation (no subject needed in some languages)
- "and then" as sentence connector
- Maintains past tense throughout
```

### Adjust Context

```bash
# Minimal context (faster, less accurate)
subs translate input.srt output.srt --lang dutch --context 1

# Default (balanced)
subs translate input.srt output.srt --lang dutch --context 3

# Maximum context (slower, more accurate)
subs translate input.srt output.srt --lang dutch --context 5
```

## Multi-Model Ensemble

Using multiple models improves quality through diversity:

```
English: "I love you"

Model 1: "Ik hou van je"
Model 2: "Ik houd van je"
Model 3: "Ik hou van jou"

Judge: Selects best → "Ik hou van je"
```

### Number of Models

```bash
# Single model (fast)
--translation-models "qwen2.5:7b"

# Two models (balanced)
--translation-models "qwen2.5:7b,llama3.2:3b"

# Three models (recommended)
--translation-models "qwen2.5:7b,llama3.2:3b,stablelm2:1.6b"

# Many models (highest quality)
--translation-models "qwen2.5:14b,mistral-nemo:12b,llama3.1:8b,gemma2:9b"
```

## Output Formats

Subs preserves the SRT format exactly:

**Input (input.srt):**
```
1
00:00:01,000 --> 00:00:03,000
Hello, how are you?

2
00:00:03,500 --> 00:00:05,500
I'm doing great, thank you!
```

**Output (output.nl.srt):**
```
1
00:00:01,000 --> 00:00:03,000
Hallo, hoe gaat het met je?

2
00:00:03,500 --> 00:00:05,500
Het gaat geweldig met me, dank je!
```

## Special Content Handling

### Music and Songs

Music notation is automatically preserved:

```
Input:  ♪ Dancing in the moonlight ♪
Output: ♪ Dancing in the moonlight ♪  (unchanged)
```

### Speaker Labels

Speaker labels are handled intelligently:

```
Input:  JOHN: Good morning everyone
Output: JOHN: Goedemorgen iedereen  (name preserved, text translated)

Input:  NARRATOR: Once upon a time
Output: VERTELLER: Er was eens  (role translated)
```

### Closed Captions

Brackets and their contents are translated:

```
Input:  [Music playing]
Output: [Muziek speelt]

Input:  [Door closes]
Output: [Deur sluit]
```

## Complete Workflow Example

### Wedding Video Translation

```bash
# Step 1: Transcribe (external tool like Whisper)
whisper wedding.mp4 --output wedding.srt

# Step 2: Fix grammar
subs fix wedding.srt wedding-corrected.srt

# Step 3: Translate to Dutch
subs translate wedding-corrected.srt wedding.nl.srt \
  --lang dutch \
  --translation-models "qwen2.5:7b,llama3.2:3b,stablelm2:1.6b" \
  --judge-model "qwen2.5:7b" \
  --context 5

# Step 4: Review
diff -y wedding.srt wedding.nl.srt | less
```

## Performance Tuning

### Fast Translation

```bash
subs translate input.srt output.nl.srt \
  --lang dutch \
  --translation-models "stablelm2:1.6b" \
  --context 1
```

**Expected:** ~3x faster than default

### Quality Translation

```bash
subs translate input.srt output.nl.srt \
  --lang dutch \
  --translation-models "qwen2.5:14b,mistral-nemo:12b,llama3.1:8b" \
  --judge-model "qwen2.5:14b" \
  --context 5
```

**Expected:** ~2x slower but significantly better

## Debugging

### Enable Debug Logging

```bash
subs translate input.srt output.nl.srt \
  --lang dutch \
  --log-level DEBUG
```

Shows:
- Each subtitle being processed
- All model responses
- Judge decisions
- Cache hits/misses
- Performance metrics

### Check Specific Subtitle

View debug output to see translation candidates:

```
DEBUG: Processing subtitle 42: "I love you"
DEBUG: Model qwen2.5:7b: "Ik hou van je"
DEBUG: Model llama3.2:3b: "Ik houd van jou"
DEBUG: Model stablelm2:1.6b: "Ik hou van je"
DEBUG: Judge selected: Model 1 (qwen2.5:7b)
```

## Batch Processing

Translate multiple files:

```bash
# Using shell loop
for file in *.srt; do
  subs translate "$file" "${file%.srt}.nl.srt" --lang dutch
done

# Using find
find . -name "*.srt" -exec sh -c '
  subs translate "$1" "${1%.srt}.nl.srt" --lang dutch
' _ {} \;
```

## Caching

Translations are cached for reuse:

```bash
# First run: Builds cache (slower)
subs translate input.srt output.nl.srt --lang dutch

# Second run: Uses cache (instant)
subs translate input.srt output.nl.srt --lang dutch

# Force fresh translation: Delete cache
rm srt_ollama_cache.json
subs translate input.srt output.nl.srt --lang dutch
```

## Common Patterns

### Translate Multiple Versions

```bash
# Original
subs translate original.srt output.nl.srt --lang dutch

# Corrected version
subs fix original.srt corrected.srt
subs translate corrected.srt output-corrected.nl.srt --lang dutch

# Compare
diff output.nl.srt output-corrected.nl.srt
```

### Different Quality Settings

```bash
# Draft (fast)
subs translate input.srt draft.nl.srt \
  --lang dutch \
  --translation-models "stablelm2:1.6b"

# Final (high quality)
subs translate input.srt final.nl.srt \
  --lang dutch \
  --translation-models "qwen2.5:14b,mistral-nemo:12b" \
  --judge-model "qwen2.5:14b" \
  --context 5

# Compare
diff draft.nl.srt final.nl.srt
```

## Troubleshooting

### Poor Translation Quality

Try:
- Larger/better models
- More translation models (ensemble)
- More context (`--context 5`)
- Language-specific models

### Translations Don't Make Sense

Check:
- Is context too small? (`--context 3` minimum)
- Are models suitable for target language?
- Is source grammar correct? (Run `fix` first)

### Some Subtitles Not Translated

Enable debug logging and check for errors:
```bash
subs translate input.srt output.nl.srt --lang dutch --log-level DEBUG
```

## See Also

- [Multi-Language Translation](multi-translation.md) - Translate to multiple languages
- [Grammar Correction](grammar-correction.md) - Fix before translating
- [Model Selection](models.md) - Choose best models
- [Performance](../performance/optimization.md) - Optimize speed
