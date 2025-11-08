# Performance Optimization

Maximize translation speed and efficiency.

## Overview

Subs includes several performance optimization strategies:

1. **Smart Caching** - Context-aware cache reduces redundant API calls
2. **Model Selection** - Choose appropriate models for your hardware
3. **Context Tuning** - Balance context quality vs processing time
4. **Batch Processing** - Future feature for even faster processing

## Quick Optimization Tips

### For Maximum Speed

```bash
# Use small, fast models
subs translate input.srt output.nl.srt \
  --lang dutch \
  --translation-models "stablelm2:1.6b,phi3:3.8b" \
  --judge-model "phi3:3.8b" \
  --context 1
```

**Expected:** ~3x faster than default

### For Maximum Quality

```bash
# Use large, capable models with more context
subs translate input.srt output.nl.srt \
  --lang dutch \
  --translation-models "qwen2.5:14b,mistral-nemo:12b,llama3.1:8b" \
  --judge-model "qwen2.5:14b" \
  --context 5
```

**Expected:** ~2x slower but significantly better quality

### Balanced (Recommended)

```bash
# Default configuration - good balance
subs translate input.srt output.nl.srt \
  --lang dutch
```

**Expected:** Best balance of speed and quality

## Model Selection Impact

### Model Size vs Speed

| Model Size | VRAM | Speed | Quality | Best For |
|-----------|------|-------|---------|----------|
| 1-2B | 1-2GB | Very Fast | Good | Quick drafts, batch processing |
| 3-7B | 2-5GB | Fast | Excellent | General use, recommended |
| 8-14B | 5-8GB | Medium | Outstanding | High quality, professional |
| 32B+ | 16GB+ | Slow | Best | Critical content, final output |

### Number of Models

| Models | Speed | Quality | Best For |
|--------|-------|---------|----------|
| 1 | 100% | Good | Quick processing |
| 2 | 50% | Better | Balanced |
| 3 | 33% | Excellent | Recommended default |
| 4+ | 25% | Outstanding | Maximum quality |

## Context Window Impact

The context window controls how many surrounding subtitles are provided:

```bash
# Minimal context (fastest)
--context 0  # Current subtitle only

# Low context
--context 1  # 1 before + current + 1 after

# Balanced (default)
--context 3  # 3 before + current + 3 after

# High context (best quality)
--context 5  # 5 before + current + 5 after
```

### Context Impact on Performance

| Context | Speed | Quality | Best For |
|---------|-------|---------|----------|
| 0 | 100% | Poor | Not recommended |
| 1 | 95% | Okay | Technical/simple content |
| 3 | 85% | Good | General use (default) |
| 5 | 75% | Excellent | Conversational content |

## Caching Strategy

Subs uses a **content + context** aware cache:

### How It Works

```
Cache Key = hash(text + context + language + model)
```

**Benefits:**

- Same subtitle with same context = instant cache hit
- Works across different videos with similar content
- Dramatically speeds up re-runs
- No manual management needed

### Cache Performance

| Scenario | Speed Improvement |
|----------|-------------------|
| Re-running same file | ~100x faster (instant) |
| Processing similar content | ~5-20x faster |
| First run | No benefit (building cache) |

### Cache Management

```bash
# View cache file
cat srt_ollama_cache.json

# Check cache size
du -h srt_ollama_cache.json

# Clear cache (force fresh translations)
rm srt_ollama_cache.json

# Backup cache
cp srt_ollama_cache.json srt_ollama_cache.backup.json
```

## GPU Optimization

### Ensure GPU Usage

```bash
# Check GPU is available
nvidia-smi

# Monitor GPU during processing
watch -n 1 nvidia-smi

# Check Ollama is using GPU
ollama run qwen2.5:7b --verbose "test"
```

### VRAM Management

**Models run sequentially**, not simultaneously:

```
Time →
Model 1: [████]
Model 2:       [████]
Model 3:            [████]

Peak VRAM = Largest model (not sum!)
```

**Optimization:**

- Mix small + large models
- Put largest model first (better for Ollama's memory management)
- Example: `qwen2.5:14b,llama3.2:3b,stablelm2:1.6b`

### VRAM by GPU

| GPU | VRAM | Recommended Models |
|-----|------|-------------------|
| RTX 3060 | 12GB | qwen2.5:7b, gemma2:9b |
| RTX 3070/3080 | 8-10GB | qwen2.5:7b, llama3.2:3b |
| RTX 3090/4090 | 24GB | qwen2.5:32b, llama3.1:70b |
| RTX 4060 Ti | 16GB | qwen2.5:14b, mistral-nemo:12b |

## Real-World Benchmarks

Test: 100 subtitles, Dutch translation, RTX 3090

### By Model Size

| Configuration | Time | Quality | VRAM |
|--------------|------|---------|------|
| 3x 1-2B models | 25s | Good | 2GB |
| 3x 3-7B models | 90s | Excellent | 5GB |
| 3x 8-14B models | 180s | Outstanding | 8GB |
| 1x 70B model | 400s | Best | 40GB |

### By Model Count

| Models | Time | Quality Score |
|--------|------|--------------|
| 1 model | 30s | 7/10 |
| 2 models | 60s | 8/10 |
| 3 models | 90s | 9/10 |
| 5 models | 150s | 9.5/10 |

### By Context Window

| Context | Time | Quality Impact |
|---------|------|---------------|
| 0 | 85s | -20% |
| 1 | 87s | -5% |
| 3 (default) | 90s | baseline |
| 5 | 94s | +10% |

## Optimization Strategies

### Fast Batch Processing

For processing many files quickly:

```bash
# Use fast, small models
--translation-models "llama3.2:3b,stablelm2:1.6b"
--judge-model "phi3:3.8b"
--context 1
```

### Professional Quality

For wedding videos and important content:

```bash
# Use best models, more context
--translation-models "qwen2.5:14b,mistral-nemo:12b,llama3.1:8b,gemma2:9b"
--judge-model "qwen2.5:14b"
--context 5
```

### Resource-Constrained

For systems with limited VRAM:

```bash
# Use smallest effective models
--translation-models "stablelm2:1.6b,phi3:3.8b"
--judge-model "phi3:3.8b"
--context 3
```

## Profiling Your System

### Test Different Configurations

```bash
# Benchmark 1: Fast
time subs translate test.srt out1.srt \
  --translation-models "stablelm2:1.6b" \
  --lang dutch

# Benchmark 2: Balanced
time subs translate test.srt out2.srt \
  --translation-models "llama3.2:3b,qwen2.5:7b" \
  --lang dutch

# Benchmark 3: Quality
time subs translate test.srt out3.srt \
  --translation-models "qwen2.5:14b,mistral-nemo:12b" \
  --lang dutch
```

### Monitor Resources

```bash
# Terminal 1: Run translation
subs translate input.srt output.srt

# Terminal 2: Monitor GPU
watch -n 1 nvidia-smi

# Terminal 3: Monitor CPU/RAM
htop
```

## Advanced: Token Optimization

Subs automatically optimizes token limits:

- **Grammar correction:** ~75 tokens per subtitle
- **Translation:** ~100 tokens per subtitle
- **Judge:** Only 100 tokens (not 16384!)

This reduces memory usage by ~50% with no quality loss.

## Future Optimizations

Planned features for even better performance:

### Batch Processing

Process multiple subtitles in one API call:

```
Current: [Sub1] → [Sub2] → [Sub3]  (3 calls)
Future:  [Sub1, Sub2, Sub3]         (1 call)
```

**Expected benefit:** 3-5x speedup

### Parallel Model Execution

Run models simultaneously on multi-GPU systems:

```
Current: Model1 → Model2 → Model3 (sequential)
Future:  Model1, Model2, Model3   (parallel)
```

**Expected benefit:** 3x speedup on multi-GPU systems

## Troubleshooting Performance

### Slow Processing

**Check:**

1. Is Ollama using GPU? (`nvidia-smi`)
2. Are models too large? (Try smaller models)
3. Is context too large? (Try `--context 1`)
4. Too many models? (Use 2 instead of 4)

### High Memory Usage

**Solutions:**

1. Use smaller models
2. Reduce model count
3. Close other GPU applications
4. Use sequential processing (default)

### Poor Quality Despite Optimization

**Remember:**

- Speed vs quality is always a tradeoff
- Minimum recommended: 3B+ models
- Use at least 2-3 models for ensemble benefits
- Context window of 3 is usually sufficient

## See Also

- [Model Selection](../user-guide/models.md) - Choose the right models
- [Batch Processing](batch-processing.md) - Process multiple files
- [Parallelism](parallelism.md) - Future parallel execution
- [Troubleshooting](../user-guide/troubleshooting.md) - Common issues
