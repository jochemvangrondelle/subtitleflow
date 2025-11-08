# Grammar Correction

Fix spelling and grammar errors in subtitle files.

## Overview

Grammar correction helps clean up transcription errors before translation. It uses conservative AI-based correction that:

- ✓ Fixes spelling mistakes
- ✓ Corrects grammar errors
- ✓ Preserves speaker labels
- ✓ Maintains closed captions (e.g., [Music])
- ✓ Keeps proper names unchanged
- ✗ Does NOT rephrase or rewrite content

## Basic Usage

### Simple Correction

```bash
subs fix input.srt corrected.srt
```

This creates `corrected.srt` with grammar and spelling fixes.

### With Custom Model

```bash
subs fix input.srt corrected.srt --grammar-model "qwen2.5:7b"
```

### With Debug Logging

```bash
subs fix input.srt corrected.srt --log-level DEBUG
```

## Recommended Models

### Best Overall: `qwen2.5:7b`

- **Size:** 4.7GB
- **VRAM:** ~5GB
- **Quality:** Excellent, conservative corrections
- **Speed:** Fast

```bash
subs fix input.srt corrected.srt --grammar-model "qwen2.5:7b"
```

### Fast Option: `gemma2:9b`

- **Size:** 5.4GB
- **VRAM:** ~5GB
- **Quality:** Good
- **Speed:** Very fast

```bash
subs fix input.srt corrected.srt --grammar-model "gemma2:9b"
```

### High Quality: `qwen2.5:14b`

- **Size:** 9GB
- **VRAM:** ~8GB
- **Quality:** Outstanding
- **Speed:** Medium

```bash
subs fix input.srt corrected.srt --grammar-model "qwen2.5:14b"
```

## What Gets Corrected

### Spelling Mistakes

**Before:**
```
I realy love this plaace
```

**After:**
```
I really love this place
```

### Grammar Errors

**Before:**
```
He don't like them apples
```

**After:**
```
He doesn't like those apples
```

### Transcription Errors

**Before:**
```
We're going to the beech to swim
```

**After:**
```
We're going to the beach to swim
```

## What Gets Preserved

### Speaker Labels

**Input:**
```
JOHN: Hello, how are you doing?
MARY: I'm doing good, thanks!
```

**Output (speaker labels unchanged):**
```
JOHN: Hello, how are you doing?
MARY: I'm doing well, thanks!
```

### Closed Captions

**Input:**
```
[Music playing]
[Applause]
[Door closes]
```

**Output (captions preserved):**
```
[Music playing]
[Applause]
[Door closes]
```

### Proper Names

**Input:**
```
Jochem van Grondelle lives in Amsterdam
```

**Output (name unchanged):**
```
Jochem van Grondelle lives in Amsterdam
```

## Context-Aware Correction

Grammar correction uses surrounding subtitles for context:

```
Subtitle 42: "I went to the store"
Subtitle 43: "and then I bought milk"  ← Correcting this one
Subtitle 44: "It was very expensive"

Context helps understand:
- "and then" continues previous sentence
- "I" is the subject (from context)
- Past tense is appropriate
```

### Adjust Context Window

```bash
# Minimal context (faster)
subs fix input.srt corrected.srt --context 1

# Default context
subs fix input.srt corrected.srt --context 3

# More context (better quality)
subs fix input.srt corrected.srt --context 5
```

## Combined Workflows

### Fix Then Translate

Most common workflow for transcribed videos:

```bash
# Step 1: Fix grammar
subs fix input.srt corrected.srt

# Step 2: Translate from corrected version
subs translate corrected.srt output.nl.srt --lang dutch
```

### Fix and Translate in One Command

```bash
subs both input.srt output.nl.srt --lang dutch
```

This:
1. Fixes grammar
2. Translates the corrected version
3. Produces `output.nl.srt`

## Examples

### Wedding Video

```bash
# Transcription often has errors in names/places
subs fix wedding-ceremony.srt wedding-corrected.srt --log-level INFO
```

### Podcast

```bash
# Conversational speech with filler words
subs fix podcast-ep1.srt podcast-clean.srt --context 5
```

### Interview

```bash
# Multiple speakers
subs fix interview.srt interview-corrected.srt --grammar-model "qwen2.5:14b"
```

### Lecture

```bash
# Technical content, needs careful correction
subs fix lecture.srt lecture-corrected.srt \
  --grammar-model "qwen2.5:14b" \
  --context 5 \
  --log-level DEBUG
```

## Performance Tips

### Faster Correction

```bash
# Use smaller model and less context
subs fix input.srt corrected.srt \
  --grammar-model "qwen2.5:3b" \
  --context 1
```

### Higher Quality

```bash
# Use larger model and more context
subs fix input.srt corrected.srt \
  --grammar-model "qwen2.5:14b" \
  --context 5
```

## Troubleshooting

### Over-Correction

**Symptom:** The model rewrites content instead of just fixing errors

**Solution:** Use `qwen2.5:7b` which is more conservative, or file an issue with examples

### Under-Correction

**Symptom:** Obvious errors are not fixed

**Solution:**

```bash
# Try a larger model
subs fix input.srt corrected.srt --grammar-model "qwen2.5:14b"

# Add more context
subs fix input.srt corrected.srt --context 5

# Check debug output
subs fix input.srt corrected.srt --log-level DEBUG
```

### Names Being Changed

**Symptom:** Proper names are "corrected" incorrectly

**Solution:** File an issue with specific examples. The model should preserve proper names.

## Limitations

1. **AI-based:** May occasionally make mistakes
2. **Language:** Optimized for English grammar correction
3. **Idioms:** May over-correct colloquial speech
4. **Slang:** Formal language bias in some models

## Best Practices

1. **Always review:** Check corrected output before translation
2. **Use diff:** Compare original and corrected: `diff input.srt corrected.srt`
3. **Keep original:** Don't delete original transcription
4. **Test first:** Try on a small sample before full video
5. **Choose context:** More context = better quality but slower

## Comparison View

Compare original and corrected side-by-side:

```bash
# Using diff
diff -y input.srt corrected.srt | less

# Using git diff (colored)
git diff --no-index input.srt corrected.srt

# Count changes
diff input.srt corrected.srt | grep -c "^<"
```

## See Also

- [Quick Start](../getting-started/quickstart.md) - Basic tutorial
- [Translation Guide](single-translation.md) - Translate after correction
- [Model Selection](models.md) - Choose the best grammar model
- [Configuration](../getting-started/configuration.md) - Advanced settings
