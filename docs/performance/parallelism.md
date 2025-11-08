# Parallelism

Run multiple models concurrently for faster ensemble processing.

## Overview

When using multiple models, process them in parallel:

**Sequential (current):**
```
Model 1: [===========================] 60s
Model 2:                               [===========================] 60s
Total: 120s
```

**Parallel (optimized):**
```
Model 1: [===========================] 60s
Model 2: [===========================] 60s
Total: 60s (same time as single model!)
```

## Implementation

### Thread-Based Parallelism

For I/O-bound operations (API calls):

```python
from concurrent.futures import ThreadPoolExecutor

def translate_with_parallelism(subtitle, models):
    with ThreadPoolExecutor(max_workers=len(models)) as executor:
        futures = [executor.submit(translate, model, subtitle) for model in models]
        results = [f.result() for f in futures]
    return results
```

### Process-Based Parallelism

For CPU-bound operations:

```python
from multiprocessing import Pool

with Pool(processes=len(models)) as pool:
    results = pool.starmap(translate, [(m, sub) for m in models])
```

## Configuration

```python
config.enable_parallel = True
config.max_parallel_models = 3  # Limit concurrent models
```

## Benefits

- **Speed**: 2x-3x faster with 2-3 models
- **Efficiency**: Better hardware utilization
- **Scalability**: Easy to add more models

## Considerations

### Memory Usage

Each model needs VRAM/RAM:
- 7B model: ~8GB VRAM
- 14B model: ~16GB VRAM

**Example:** 3x qwen3:14b = ~48GB VRAM needed

**Solution:** Use model rotation or sequential for large models.

### CPU Overhead

Thread/process creation has overhead. Only beneficial for:
- 2+ models
- Long-running operations (>1s per subtitle)

### Error Handling

One model failure shouldn't crash all:

```python
try:
    result = model.generate(prompt)
except Exception as e:
    logger.warning(f"Model {model} failed: {e}")
    result = None  # Continue with other models
```

## Hybrid Approach

Combine batching + parallelism:

```python
# Process batches in parallel across models
batch_size = 5
parallel_models = 3

# Each model processes its batch simultaneously
with ThreadPoolExecutor(max_workers=parallel_models) as executor:
    futures = []
    for model in models:
        future = executor.submit(process_batch, model, batch)
        futures.append(future)
    results = [f.result() for f in futures]
```

## Performance Comparison

| Method | Time (100 subs) | Speedup |
|--------|-----------------|---------|
| Sequential, 1 model | 90s | 1x |
| Sequential, 3 models | 270s | 0.33x |
| Parallel, 3 models | 95s | 0.95x |
| Batch + Parallel | 35s | 2.6x |

*Times with mixed models on M2 Pro*

## Best Practices

1. **Start with threads**: Easier, sufficient for most cases
2. **Limit parallelism**: Don't exceed CPU/GPU capacity
3. **Monitor resources**: Watch RAM/VRAM usage
4. **Fallback**: Have sequential backup if parallel fails
5. **Cache warmup**: Parallel model loading can be slow
