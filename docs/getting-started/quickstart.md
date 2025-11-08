# Quick Start

Get up and running with SubtitleFlow in 5 minutes!

## Basic Workflow

The typical workflow is:

1. **Transcribe** video to subtitles using Whisper (if starting from video)
2. **Fix grammar** in your English subtitles (optional but recommended)
3. **Translate** to your target language(s)
4. **Review** and enjoy!

## Your First Translation

### Step 1: Transcribe Video (If Starting from Video)

If you have a video file and need subtitles, transcribe it first:

```bash
subtitleflow transcribe video.mp4 \
  --model large-v2 \
  --language en \
  --device cuda
```

**What this does:**
- Extracts audio from video using FFmpeg
- Transcribes using WhisperX (large-v2 model)
- Creates SRT subtitle file with timestamps
- Supports GPU acceleration (CUDA) for faster processing

**Model options:**
- `tiny` - Fastest, lowest accuracy
- `base` - Good balance
- `small` - Better accuracy
- `medium` - High accuracy
- `large-v2` - Best accuracy (default)
- `large-v3` - Latest, best accuracy

**Note:** Requires WhisperX: `pip install subtitleflow[transcribe]`

### Step 2: Fix Grammar (Optional)

Clean up any typos or grammar mistakes:

```bash
subtitleflow fix input.srt corrected.srt \
  --grammar-models "qwen2.5:7b,gemma3:4b" \
  --judge-model "qwen2.5:7b"
```

**What this does:**
- Uses multiple models (qwen2.5:7b and gemma3:4b) to fix spelling/grammar
- A judge model picks the best correction
- Preserves formatting, speaker labels, and music markers

### Step 3: Translate

Translate the corrected file to Dutch:

```bash
subtitleflow translate corrected.srt output.nl.srt \
  --lang dutch \
  --translation-models "llama3.2:3b,qwen2.5:7b,stablelm2:1.6b"
```

**What this does:**
- Translates using multiple models for better quality
- Judge selects best translation per subtitle
- Maintains context across subtitles
- Preserves music in English

### All-in-One Command

Process a video from start to finish:

```bash
subtitleflow process-video video.mp4 \
  --langs "dutch,spanish" \
  --transcribe-model large-v2
```

This will:
1. Transcribe video to `video.srt`
2. Fix grammar and save to `video.corrected.srt`
3. Translate to multiple languages
4. Save final outputs to `video.nl.srt`, `video.es.srt`, etc.

## Multi-Language Translation

The `process-video` command automatically translates to multiple languages:

```bash
subtitleflow process-video video.mp4 \
  --langs "dutch,spanish,french"
```

This creates:
- `video.nl.srt` (Dutch)
- `video.es.srt` (Spanish)
- `video.fr.srt` (French)

**If you already have an SRT file**, you can translate to multiple languages by running translate multiple times:

```bash
subtitleflow translate input.srt input.nl.srt --lang dutch
subtitleflow translate input.srt input.es.srt --lang spanish
subtitleflow translate input.srt input.fr.srt --lang french
```

Or use `process-video` with `--skip-transcribe` if you have the original video file:

```bash
subtitleflow process-video video.mp4 \
  --langs "dutch,spanish,french" \
  --skip-transcribe
```

## Real-World Example

Let's say you have a wedding video subtitle file `wedding.en.srt`:

```srt
1
00:00:00,000 --> 00:00:03,000
OFFICIANT: Wel come everyone to this
beautiful ceremony.

2
00:00:03,000 --> 00:00:06,000
We are gathered here today to celebrate
the union of John and Sarah.

3
00:00:06,000 --> 00:00:09,000
♪ Here comes the bride ♪
```

### Transcribe Video

If starting from a video file:

```bash
subtitleflow transcribe wedding.mp4 \
  --output wedding.en.srt \
  --model large-v2
```

### Fix Grammar

```bash
subtitleflow fix wedding.en.srt wedding.en.corrected.srt
```

**Result:**
```srt
1
00:00:00,000 --> 00:00:03,000
OFFICIANT: Welcome everyone to this
beautiful ceremony.

2
00:00:03,000 --> 00:00:06,000
We are gathered here today to celebrate
the union of John and Sarah.

3
00:00:06,000 --> 00:00:09,000
♪ Here comes the bride ♪
```

Notice "Wel come" → "Welcome"

### Translate to Dutch

```bash
subtitleflow translate wedding.en.corrected.srt wedding.nl.srt --lang dutch
```

**Result:**
```srt
1
00:00:00,000 --> 00:00:03,000
CEREMONIEMEESTER: Welkom iedereen bij deze
prachtige ceremonie.

2
00:00:03,000 --> 00:00:06,000
We zijn hier vandaag samengekomen om de
vereniging van John en Sarah te vieren.

3
00:00:06,000 --> 00:00:09,000
♪ Here comes the bride ♪
```

Notice:
- "OFFICIANT" → "CEREMONIEMEESTER" (role translated)
- Music lyrics stay in English
- Natural, flowing Dutch

## Common Options

### Transcription Options

Control transcription quality and speed:

```bash
subtitleflow transcribe video.mp4 \
  --model large-v2 \          # Model size (tiny to large-v3)
  --language en \              # Language code
  --device cuda \              # cuda or cpu
  --batch-size 4               # Batch size for processing
```

### Context Window

Control how much context to provide (default: 3 lines):

```bash
subtitleflow translate input.srt output.srt --context 5
```

More context = better translations but slower

### Custom Models

Use different models:

```bash
subtitleflow translate input.srt output.srt \
  --translation-models "llama3.2:3b,qwen2.5:7b" \
  --judge-model "qwen2.5:7b"
```

### Log Level

See more details:

```bash
subtitleflow translate input.srt output.srt --log-level DEBUG
```

## Performance Tips

1. **Transcription**: Use smaller models (`base` or `small`) for faster transcription
2. **Use faster models** for drafts: `gemma3:4b` is quick
3. **Reduce context window** for speed: `--context 1`
4. **Single model** skips judging: `--translation-models "qwen2.5:7b"`
5. **GPU acceleration**: Use `--device cuda` for transcription if available
6. **Cache is automatic**: Re-running is fast!

## What's Next?

- Learn about [Configuration](configuration.md)
- Read the [User Guide](../user-guide/grammar-correction.md)
- Check [Performance Optimization](../performance/optimization.md)
