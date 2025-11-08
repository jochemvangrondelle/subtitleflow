# Installation

## Prerequisites

Before installing SubtitleFlow, ensure you have:

- **Python 3.9 or higher**
- **Ollama** installed and running ([Download Ollama](https://ollama.com))
- **uv** (recommended) or pip for package management
- **NVIDIA GPU** (recommended for transcription and translation) with CUDA support
- **FFmpeg** (required for video transcription)

## GPU Requirements

### For Translation (Ollama)

SubtitleFlow uses Ollama for translation, which benefits significantly from GPU acceleration:

- **Minimum**: 4GB VRAM (for small models like `stablelm2:1.6b`)
- **Recommended**: 8GB VRAM (for models like `qwen2.5:7b`, `llama3.2:3b`)
- **Optimal**: 16GB+ VRAM (for larger models like `qwen2.5:14b`)

### For Transcription (WhisperX)

WhisperX requires CUDA for GPU acceleration:

- **CUDA 11.8 or higher** (recommended)
- **cuDNN 8.6 or higher**
- **NVIDIA GPU** with compute capability 7.0+ (Volta, Turing, Ampere, Ada, Hopper)
- **Minimum**: 4GB VRAM (for `base` model)
- **Recommended**: 8GB+ VRAM (for `large-v2` or `large-v3` models)

### GPU Setup

#### Install NVIDIA Drivers

=== "Ubuntu/Debian"
    ```bash
    # Check GPU
    lspci | grep -i nvidia
    
    # Install drivers (adjust version as needed)
    sudo apt update
    sudo apt install -y nvidia-driver-535  # or latest version
    sudo reboot
    ```

=== "Arch Linux"
    ```bash
    sudo pacman -S nvidia nvidia-utils
    sudo reboot
    ```

=== "macOS"
    macOS doesn't support NVIDIA GPUs. Use CPU mode or Apple Silicon GPU acceleration (if available).

#### Install CUDA Toolkit

=== "Ubuntu/Debian"
    ```bash
    # Download CUDA 11.8 (or latest compatible version)
    wget https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda_11.8.0_520.61.05_linux.run
    sudo sh cuda_11.8.0_520.61.05_linux.run
    
    # Add to PATH
    echo 'export PATH=/usr/local/cuda-11.8/bin:$PATH' >> ~/.bashrc
    echo 'export LD_LIBRARY_PATH=/usr/local/cuda-11.8/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
    source ~/.bashrc
    ```

=== "Arch Linux"
    ```bash
    sudo pacman -S cuda
    ```

#### Verify GPU Setup

```bash
# Check NVIDIA driver
nvidia-smi

# Check CUDA
nvcc --version

# Test GPU availability
python -c "import torch; print(torch.cuda.is_available())"
```

## Install FFmpeg

FFmpeg is required for video transcription:

=== "Ubuntu/Debian"
    ```bash
    sudo apt update
    sudo apt install -y ffmpeg
    ```

=== "macOS"
    ```bash
    brew install ffmpeg
    ```

=== "Windows"
    Download from [ffmpeg.org](https://ffmpeg.org/download.html) or use:
    ```powershell
    winget install ffmpeg
    ```

## Install Ollama

SubtitleFlow requires Ollama to run the language models locally.

=== "macOS"
    ```bash
    brew install ollama
    ollama serve
    ```

=== "Linux"
    ```bash
    curl -fsSL https://ollama.com/install.sh | sh
    ollama serve
    ```

=== "Windows"
    Download from [ollama.com](https://ollama.com/download) and run the installer.

### Pull Required Models

Pull at least one model for translation:

```bash
# Recommended models for 8GB VRAM (default)
ollama pull llama3.2:3b      # 2GB VRAM - Excellent multilingual
ollama pull qwen2.5:7b       # 5GB VRAM - Best overall quality
ollama pull stablelm2:1.6b   # 1GB VRAM - Fast and reliable

# For grammar correction
ollama pull qwen2.5:3b       # 2GB VRAM
ollama pull gemma3:4b        # 2GB VRAM
```

## Install SubtitleFlow

### Using uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer:

```bash
# Install uv if you haven't
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/jochemvangrondelle/subs.git
cd subs

# Create virtual environment and install
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

### Using pip

```bash
git clone https://github.com/jochemvangrondelle/subs.git
cd subs

python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

### Install WhisperX (for Transcription)

To enable video transcription, install WhisperX with GPU support:

```bash
# Activate your virtual environment first
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install WhisperX with CUDA support
pip install whisperx

# Or install via optional dependency
uv pip install -e ".[transcribe]"
```

**Note**: WhisperX will automatically use GPU if CUDA is available. For CPU-only systems, it will fall back to CPU (much slower).

### Development Installation

If you want to contribute or run tests:

```bash
uv pip install -e ".[dev]"
```

This installs additional development dependencies:
- pytest & pytest-cov (testing)
- mypy & pyright (type checking)
- ruff (linting & formatting)
- mkdocs-material (documentation)

## Verify Installation

Check that everything is working:

```bash
# Check SubtitleFlow is installed
subtitleflow version

# Check Ollama connection
ollama list

# Check models are available
ollama list | grep -E "(qwen2.5|llama3.2|stablelm2)"

# Verify GPU for Ollama (should show GPU usage)
nvidia-smi

# Test WhisperX GPU support
python -c "import whisperx; print('WhisperX installed successfully')"
```

## Configuration

### Environment Variables

SubtitleFlow supports the following environment variables:

```bash
# Ollama server URL (default: http://127.0.0.1:11434)
export OLLAMA_URL="http://127.0.0.1:11434"

# For Docker deployments
export OLLAMA_HOST="http://ollama:11434"
```

### Cache Location

By default, SubtitleFlow creates a cache file `srt_ollama_cache.json` in the current directory. This cache stores translation results to avoid redundant API calls.

## Next Steps

Now that you have SubtitleFlow installed, check out the [Quick Start Guide](quickstart.md) to start translating subtitles!

## Troubleshooting

### Ollama Connection Issues

If you see "Cannot connect to Ollama server":

1. Check Ollama is running: `ollama list`
2. Check the URL: `echo $OLLAMA_URL`
3. Try restarting Ollama: `ollama serve`
4. Verify firewall settings if using remote Ollama

### GPU Not Detected

If GPU is not being used:

```bash
# Check NVIDIA driver
nvidia-smi

# Check CUDA installation
nvcc --version

# Verify PyTorch CUDA support
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"

# Check Ollama GPU usage
ollama run qwen2.5:7b "test"  # Monitor with: watch -n 1 nvidia-smi
```

### WhisperX Installation Issues

If WhisperX fails to install or use GPU:

```bash
# Reinstall with explicit CUDA support
pip uninstall whisperx
pip install whisperx --no-cache-dir

# For CPU-only systems, WhisperX will work but be slower
# No special installation needed
```

### Model Not Found

If you see "Model not found":

```bash
# List available models
ollama list

# Pull the missing model
ollama pull qwen2.5:7b

# Verify model is available
ollama show qwen2.5:7b
```

### Permission Errors

If you get permission errors during installation:

```bash
# Don't use sudo with pip/uv
# Instead, use a virtual environment (recommended above)

# If you must use system Python, use --user flag
pip install --user -e .
```

### FFmpeg Not Found

If transcription fails with "ffmpeg not found":

```bash
# Verify FFmpeg is installed
ffmpeg -version

# Add to PATH if needed (Linux)
export PATH=$PATH:/usr/bin

# On macOS with Homebrew
brew install ffmpeg
```

### CUDA Out of Memory

If you encounter CUDA OOM errors:

1. Use smaller models: `--translation-models "stablelm2:1.6b"`
2. Reduce batch size for WhisperX: `--batch-size 2`
3. Close other GPU applications
4. Use CPU mode as fallback: `--device cpu` (for WhisperX)
