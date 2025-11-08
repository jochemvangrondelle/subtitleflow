# Batch Processing

Batch processing allows you to translate multiple subtitles in a single API call, significantly improving throughput.

## Overview

Instead of processing each subtitle individually:
```
Subtitle 1 → Model → Translation 1
Subtitle 2 → Model → Translation 2
Subtitle 3 → Model → Translation 3
```

Batch processing sends multiple subtitles together:
```
[Subtitle 1, 2, 3] → Model → [Translation 1, 2, 3]
```

## Benefits

- **Faster**: Reduces network/API overhead
- **Efficient**: Better GPU utilization
- **Context**: Model sees multiple subtitles at once

## Configuration

Batch size can be configured:

```python
from subs.models.config import AppConfig

config = AppConfig()
config.batch_size = 5  # Process 5 subtitles per batch
config.enable_batching = True
```

## When to Use Batching

**Good for:**
- Simple, standalone subtitles
- Fast models (gemma2, mistral:7b)
- Large subtitle files

**Not recommended for:**
- Complex context-dependent translations
- Very long subtitles (>200 chars)
- Strict sequential context requirements

## How It Works

1. **Group subtitles** into batches of N
2. **Send batch** to model with structured prompt
3. **Parse results** back into individual translations
4. **Validate** each translation

## Example Prompt Structure

```
Translate the following 3 subtitles to Dutch:

[1] Hello, welcome to the ceremony.
[2] We are gathered here today.
[3] To celebrate this special moment.

Respond in format:
[1] {translation}
[2] {translation}
[3] {translation}
```

## Best Practices

1. **Batch size**: Start with 3-5 subtitles
2. **Homogeneous batches**: Group similar-length subtitles
3. **Error handling**: Fallback to individual if batch fails
4. **Context preservation**: Include 1-2 previous subtitles as context

## Performance Comparison

| Method | Time (100 subs) | API Calls |
|--------|-----------------|-----------|
| Individual | ~180s | 100 |
| Batch (5) | ~45s | 20 |
| Batch (10) | ~30s | 10 |

*Times with qwen3:14b on M2 Pro*
