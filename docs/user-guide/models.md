# Model Selection Guide

Learn how to choose the best models for your translation needs.

## Recommended Model Configuration

### 8GB VRAM (Default)

Best balance of quality and memory efficiency:

```bash
subs translate input.srt output.nl.srt \
  --lang dutch \
  --translation-models "llama3.2:3b,qwen2.5:7b,stablelm2:1.6b" \
  --judge-model "qwen2.5:7b"
```

**Models:**

- `llama3.2:3b` (2GB VRAM) - Meta's latest, excellent multilingual
- `qwen2.5:7b` (5GB VRAM) - Best overall, 29 languages
- `stablelm2:1.6b` (1GB VRAM) - Fast and reliable

**Total Peak VRAM:** ~7GB (sequential processing)

### 16GB VRAM (High Quality)

For maximum translation quality:

```bash
subs translate input.srt output.nl.srt \
  --lang dutch \
  --translation-models "qwen2.5:14b,mistral-nemo:12b,llama3.1:8b" \
  --judge-model "qwen2.5:14b"
```

**Models:**

- `qwen2.5:14b` (8GB VRAM) - Highest quality
- `mistral-nemo:12b` (7GB VRAM) - Excellent alternative
- `llama3.1:8b` (5GB VRAM) - Strong multilingual

### 4GB VRAM (Low Memory)

For systems with limited VRAM:

```bash
subs translate input.srt output.nl.srt \
  --lang dutch \
  --translation-models "stablelm2:1.6b,phi3:3.8b" \
  --judge-model "phi3:3.8b"
```

## Model Installation

Install models with Ollama:

```bash
# For 8GB setup (recommended)
ollama pull llama3.2:3b
ollama pull qwen2.5:7b
ollama pull stablelm2:1.6b

# For 16GB setup
ollama pull qwen2.5:14b
ollama pull mistral-nemo:12b
ollama pull llama3.1:8b

# Verify installation
ollama list
```

## Language Support

### Multilingual Champions

Models with best multilingual support:

1. **qwen2.5:7b** - 29 languages officially supported
2. **llama3.2:3b** - 8 languages, excellent quality
3. **gemma2:9b** - Good European language support

### Specialized Models

- **Dutch**: `bramvanroy/geitje-7b-ultra:Q8_0` - Native Dutch specialist
- **German**: `qwen2.5:14b` - Excellent German support
- **Spanish**: `llama3.2:3b` - Strong Spanish performance
- **French**: `mistral-nemo:12b` - French company, excellent French

## Model Selection Criteria

### For Grammar Correction

Use a single reliable model:

```bash
subs fix input.srt corrected.srt --grammar-model "qwen2.5:7b"
```

**Best models:**

- `qwen2.5:7b` - Conservative, accurate corrections
- `gemma2:9b` - Good balance of speed and quality

### For Translation

Use multiple models with a judge:

```bash
subs translate input.srt output.nl.srt \
  --lang dutch \
  --translation-models "model1,model2,model3" \
  --judge-model "qwen2.5:7b"
```

**Best judges:**

- `qwen2.5:14b` - Best overall judge, excellent multilingual
- `qwen2.5:7b` - Good lightweight judge
- `gemma2:9b` - Fast judging

### Number of Models

- **1 model**: Fastest, good for simple content
- **2-3 models**: Recommended, good quality/speed balance
- **4+ models**: Best quality, slower processing

## License Information

All recommended models are **open-source** and **commercially usable**:

- **Apache 2.0**: Qwen, Mistral, StableLM
- **Meta License**: LLaMA (free for commercial use)
- **Gemma License**: Google Gemma (free)
- **MIT**: Various smaller models

No license keys or API tokens required!

## Memory Usage

Models run **sequentially**, not simultaneously:

```
Time →

Model 1: [███████]
Model 2:          [███████]
Model 3:                   [███████]
Judge:                              [███]

Peak VRAM = Largest single model
```

**Example (3 models):**

- llama3.2:3b → 2GB
- qwen2.5:7b → 5GB ← Peak usage
- stablelm2:1.6b → 1GB
- **Total Peak:** 5GB (not 2+5+1=8GB!)

## Performance Tips

### Speed Optimization

1. **Use smaller models**: `stablelm2:1.6b`, `phi3:3.8b`
2. **Reduce model count**: 2 models instead of 4
3. **Lower context window**: `--context 1` instead of default 3

### Quality Optimization

1. **Use larger models**: `qwen2.5:14b`, `llama3.1:70b`
2. **More candidates**: 4-5 translation models
3. **Better judge**: `qwen2.5:14b` or `qwen2.5:32b`
4. **More context**: `--context 5`

### Balance

The default configuration balances speed and quality:

- 3 models of varied sizes
- Good judge (qwen2.5:7b)
- Reasonable context (3 lines)
- Fits in 8GB VRAM

## Advanced: Custom Model Configuration

### For Specific Languages

**Dutch:**

```bash
--translation-models "bramvanroy/geitje-7b-ultra:Q8_0,qwen2.5:7b,llama3.2:3b"
```

**German:**

```bash
--translation-models "qwen2.5:14b,mistral-nemo:12b,llama3.1:8b"
```

### For Technical Content

Use larger, more capable models:

```bash
--translation-models "qwen2.5:32b,llama3.1:70b" \
--judge-model "qwen2.5:32b"
```

### For Fast Batch Processing

Use lightweight models:

```bash
--translation-models "stablelm2:1.6b,phi3:3.8b" \
--judge-model "phi3:3.8b"
```

## Troubleshooting

### Out of Memory (OOM)

**Symptom:** Ollama crashes or becomes unresponsive

**Solution:**

1. Use smaller models
2. Reduce number of models
3. Check available VRAM: `nvidia-smi`

### Poor Translation Quality

**Symptom:** Unnatural or incorrect translations

**Solution:**

1. Use larger/better models
2. Increase number of models (more candidates for judge)
3. Add more context: `--context 5`
4. Use language-specific models

### Slow Performance

**Symptom:** Processing takes too long

**Solution:**

1. Use smaller models
2. Reduce model count
3. Enable batch processing (if available)
4. Use GPU acceleration (check with `nvidia-smi`)

## See Also

- [Configuration Guide](../getting-started/configuration.md) - Configure model settings
- [Performance Guide](../performance/optimization.md) - Optimize for speed
- [Troubleshooting](troubleshooting.md) - Common issues and solutions
