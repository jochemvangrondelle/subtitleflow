# Troubleshooting Guide

Solutions for common issues and errors.

## Pre-Flight Checks

Subs automatically validates before processing:

1. ✓ Ollama server is running
2. ✓ All required models are installed
3. ✓ Input file exists

This **fail-fast** approach prevents wasted time.

## Common Errors

### Ollama Server Not Running

**Error:**

```
❌ Cannot connect to Ollama server
   Server URL: http://127.0.0.1:11434
   Is Ollama running? Start it with: ollama serve
```

**Solutions:**

```bash
# Start Ollama server
ollama serve

# Check if already running
ps aux | grep ollama

# Check if listening on correct port
netstat -tulpn | grep 11434

# Use custom URL if needed
export OLLAMA_HOST=http://localhost:11434
```

### Model Not Installed

**Error:**

```
❌ Model 'qwen2.5:7b' not found
   Install with: ollama pull qwen2.5:7b
```

**Solutions:**

```bash
# Install the specific model
ollama pull qwen2.5:7b

# List installed models
ollama list

# Search available models
ollama search qwen
```

### Input File Not Found

**Error:**

```
❌ Input file not found: video.srt
```

**Solutions:**

```bash
# Check file exists
ls -la video.srt

# Use absolute path
subs translate /full/path/to/video.srt output.srt

# Check current directory
pwd
```

### Empty or Invalid Response

**Error:**

```
⚠️ Empty response from model after cleaning
   Retrying with higher temperature...
```

**What it means:** The model returned an empty or invalid response.

**Automatic handling:**

- Retries up to 3 times
- Increases temperature on retry
- Falls back to next model if all retries fail

**Manual solutions:**

```bash
# Try a different model
subs translate input.srt output.srt \
  --translation-models "qwen2.5:14b" \
  --lang dutch

# Increase temperature manually (experimental)
# This requires code modification - use different models instead

# Test model directly
ollama run qwen2.5:7b "Translate to Dutch: Hello world"
```

### Out of Memory (OOM)

**Symptom:** Ollama crashes, system freezes, or CUDA errors

**Solutions:**

```bash
# Check VRAM usage
nvidia-smi

# Use smaller models
subs translate input.srt output.srt \
  --translation-models "stablelm2:1.6b,phi3:3.8b"

# Reduce number of models
subs translate input.srt output.srt \
  --translation-models "qwen2.5:7b"

# Close other GPU applications
# (browsers, other AI tools)
```

### Slow Performance

**Symptom:** Processing takes very long

**Solutions:**

```bash
# Use smaller/faster models
subs translate input.srt output.srt \
  --translation-models "llama3.2:3b,stablelm2:1.6b"

# Reduce model count
subs translate input.srt output.srt \
  --translation-models "qwen2.5:7b"

# Reduce context window
subs translate input.srt output.srt \
  --context 1

# Check GPU is being used
nvidia-smi  # Should show ollama using GPU

# Ensure models are GPU-accelerated
ollama run qwen2.5:7b --verbose "test"
```

### Poor Translation Quality

**Symptom:** Unnatural, incorrect, or inconsistent translations

**Solutions:**

```bash
# Use more/better models
subs translate input.srt output.srt \
  --translation-models "qwen2.5:14b,mistral-nemo:12b,llama3.1:8b" \
  --judge-model "qwen2.5:14b"

# Increase context window
subs translate input.srt output.srt \
  --context 5

# Use language-specific models
# For Dutch:
subs translate input.srt output.srt \
  --translation-models "bramvanroy/geitje-7b-ultra:Q8_0,qwen2.5:7b" \
  --lang dutch

# Enable debug logging
subs translate input.srt output.srt \
  --log-level DEBUG
```

### Judge Returning Invalid Response

**Symptom:** Warning about judge fallback

**Solutions:**

```bash
# Use a better judge model
subs translate input.srt output.srt \
  --judge-model "qwen2.5:14b"

# Simplify: use just one translation model (no judge needed)
subs translate input.srt output.srt \
  --translation-models "qwen2.5:7b"
```

### Cache Issues

**Symptom:** Old/stale translations, unexpected results

**Solutions:**

```bash
# Clear cache
rm srt_ollama_cache.json

# Verify cache file is valid JSON
cat srt_ollama_cache.json | jq .

# Disable cache (not currently supported - delete cache file instead)
rm srt_ollama_cache.json && subs translate ...
```

## Debug Mode

Enable detailed logging:

```bash
subs translate input.srt output.srt \
  --log-level DEBUG \
  --lang dutch
```

**Debug output includes:**

- Each subtitle being processed
- Model responses
- Cache hits/misses
- Judge decisions
- Retry attempts
- Performance metrics

## Testing Ollama

Verify Ollama is working correctly:

```bash
# Test server connection
curl http://localhost:11434/api/version

# Test model directly
ollama run qwen2.5:7b "Translate to Dutch: Hello, how are you?"

# List installed models
ollama list

# Check model info
ollama show qwen2.5:7b

# Monitor VRAM usage during processing
watch -n 1 nvidia-smi
```

## Known Issues

### DeepSeek-R1 Thinking Mode

**Issue:** DeepSeek-R1 models may return thinking tags

**Status:** Handled automatically - thinking tags are stripped

**Workaround:** Use qwen2.5:7b as judge instead

### Multi-Line Subtitles

**Issue:** Very long subtitles may exceed context window

**Status:** Handled automatically - text is truncated if needed

**Workaround:** Split long subtitles or increase model context size

### Special Characters

**Issue:** Some special characters may not translate correctly

**Status:** Known limitation of some models

**Workaround:** Use models with better Unicode support (qwen2.5:14b)

## Performance Benchmarks

Expected processing times (100 subtitles):

| Configuration | Time | Notes |
|--------------|------|-------|
| 1 model (3b) | ~30s | Fast |
| 3 models (3b-7b) | ~90s | Recommended |
| 3 models (7b-14b) | ~150s | High quality |
| 1 model (70b) | ~300s | Best quality, slow |

*Benchmarks on RTX 3090 with nvme SSD*

## Getting Help

Still stuck? Try these resources:

1. **GitHub Issues:** [Report a bug](https://github.com/jochemvangrondelle/subtitleflow/issues)
2. **Discussions:** [Ask a question](https://github.com/jochemvangrondelle/subtitleflow/discussions)
3. **Ollama Docs:** [Ollama Documentation](https://ollama.com/docs)
4. **Check logs:** Look at debug output with `--log-level DEBUG`

## See Also

- [Configuration Guide](../getting-started/configuration.md)
- [Model Selection](models.md)
- [Performance Optimization](../performance/optimization.md)
