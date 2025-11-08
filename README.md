# SubtitleFlow - AI-Powered Subtitle Translation

Professional subtitle translation and correction tool using local LLMs via Ollama.

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Start Ollama and SubtitleFlow services
docker-compose up -d

# Process a video (transcribe + fix + translate)
docker-compose exec subtitleflow uv run python -m subtitleflow process-video /app/data/video.mp4 --langs "dutch,spanish"

# Or use the CLI directly
docker-compose exec subtitleflow uv run python -m subtitleflow transcribe /app/data/video.mp4
docker-compose exec subtitleflow uv run python -m subtitleflow translate /app/data/video.srt /app/output/video.nl.srt --lang dutch
```

### Local Installation

```bash
# Install dependencies
uv pip install -e ".[dev]"

# Transcribe video to subtitles
uv run python -m subtitleflow transcribe video.mp4

# Fix grammar in subtitles
uv run python -m subtitleflow fix input.srt corrected.srt

# Translate to Dutch
uv run python -m subtitleflow translate input.srt output.nl.srt --lang dutch

# Complete workflow: transcribe + fix + translate
uv run python -m subtitleflow process-video video.mp4 --langs "dutch,spanish"
```

## ✨ Features

- **Multi-Model Ensemble**: Use multiple LLMs with intelligent judge selection
- **Context-Aware Translation**: Maintains context across subtitles for natural flow
- **Grammar Correction**: Conservative AI-based spelling and grammar fixes
- **Multi-Language Support**: Translate to multiple languages simultaneously
- **Music Detection**: Automatically preserves song lyrics in original language
- **Speaker Labels**: Maintains speaker identification and formatting
- **Smart Caching**: Context-aware cache reduces redundant API calls
- **Beautiful CLI**: Rich terminal output with progress and colors
- **Production Ready**: Comprehensive test suite, type checking, and documentation

## 📖 Installation

This project supports multiple deployment options:

### Option 1: Docker Deployment (Recommended)

**Best for:** Production deployments, isolated environments, GPU servers

```bash
# Clone repository
git clone https://github.com/jochemvangrondelle/subtitleflow.git
cd subs

# Start services (Ollama + SubtitleFlow)
docker-compose up -d

# Pull required models
docker-compose exec ollama ollama pull llama3.2:3b
docker-compose exec ollama ollama pull qwen2.5:7b
docker-compose exec ollama ollama pull stablelm2:1.6b

# Verify services
docker-compose ps
```

**Features:**
- ✅ Integrated Ollama server (no external setup needed)
- ✅ GPU support via NVIDIA Container Toolkit
- ✅ Isolated environment
- ✅ Easy scaling and management

### Option 2: External Ollama Server

**Best for:** Development, existing Ollama installations

```bash
# Install Ollama separately
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama server
ollama serve

# Install SubtitleFlow
uv pip install -e ".[dev]"

# Configure Ollama URL (if not default)
export OLLAMA_HOST=http://localhost:11434
```

### Option 3: OpenRouter / External API

**Best for:** Cloud deployments, no local GPU

Configure via environment variables:
```bash
export OLLAMA_HOST=https://openrouter.ai/api/v1
export OLLAMA_API_KEY=your-api-key
```

### Python Installation

```bash
# Using uv (recommended)
uv pip install -e .

# With development dependencies
uv pip install -e ".[dev]"

# With WhisperX support (for transcription)
uv pip install -e ".[dev]" whisperx
```

## 📖 Usage

### Complete Workflow (Recommended)

Process a video from start to finish:

```bash
# Transcribe video, fix grammar, and translate to multiple languages
uv run python -m subtitleflow process-video video.mp4 --langs "dutch,spanish"

# Skip transcription if SRT already exists
uv run python -m subtitleflow process-video video.mp4 --langs "dutch" --skip-transcribe

# Skip grammar correction
uv run python -m subtitleflow process-video video.mp4 --langs "dutch" --skip-grammar
```

### Individual Commands

```bash
# Transcribe video to subtitles (requires WhisperX)
uv run python -m subtitleflow transcribe video.mp4 --model large-v2

# Fix grammar in subtitles
uv run python -m subtitleflow fix input.srt corrected.srt

# Translate to single language
uv run python -m subtitleflow translate input.srt output.nl.srt --lang dutch

# Translate to multiple languages
uv run python -m subtitleflow translate-multi input.srt --langs "dutch,spanish,french"

# Fix then translate
uv run python -m subtitleflow both input.srt output.nl.srt --lang dutch
```

### Advanced Options

```bash
# Custom models
subtitleflow translate input.srt output.nl.srt \
  --lang dutch \
  --translation-models "qwen2.5:14b,mistral-nemo:12b" \
  --judge-model "qwen2.5:14b"

# Adjust context window
subtitleflow translate input.srt output.nl.srt \
  --lang dutch \
  --context 5

# Debug logging
subtitleflow translate input.srt output.nl.srt \
  --lang dutch \
  --log-level DEBUG
```

### Command Reference

#### `subtitleflow fix`

Fix grammar and spelling in subtitle files.

```bash
subtitleflow fix INPUT.srt OUTPUT.srt [OPTIONS]

Options:
  --grammar-model TEXT    Model for grammar correction (default: qwen2.5:7b)
  --context INTEGER        Context window size (default: 3)
  --log-level TEXT        Log level: DEBUG, INFO, WARNING, ERROR (default: INFO)
```

#### `subtitleflow translate`

Translate subtitles to a single target language.

```bash
subtitleflow translate INPUT.srt OUTPUT.srt --lang LANGUAGE [OPTIONS]

Options:
  --lang TEXT             Target language (required)
  --translation-models TEXT  Comma-separated translation models
  --judge-model TEXT      Model for judging translations
  --context INTEGER       Context window size (default: 3)
  --log-level TEXT        Log level (default: INFO)
```

#### `subtitleflow translate-multi`

Translate subtitles to multiple languages simultaneously.

```bash
subtitleflow translate-multi INPUT.srt --langs "lang1,lang2,..." [OPTIONS]

Options:
  --langs TEXT            Comma-separated target languages (required)
  --translation-models TEXT  Comma-separated translation models
  --judge-model TEXT      Model for judging translations
  --context INTEGER       Context window size (default: 3)
  --log-level TEXT        Log level (default: INFO)
```

#### `subtitleflow both`

Fix grammar then translate in one command.

```bash
subtitleflow both INPUT.srt OUTPUT.srt --lang LANGUAGE [OPTIONS]

Options:
  Same as translate command, plus:
  --grammar-model TEXT    Model for grammar correction
```

## 🎯 Model Selection

### Recommended Configurations

**8GB VRAM (Default):**
```bash
--translation-models "llama3.2:3b,qwen2.5:7b,stablelm2:1.6b"
--judge-model "qwen2.5:7b"
```

**16GB VRAM (High Quality):**
```bash
--translation-models "qwen2.5:14b,mistral-nemo:12b,llama3.1:8b"
--judge-model "qwen2.5:14b"
```

**4GB VRAM (Low Memory):**
```bash
--translation-models "stablelm2:1.6b,phi3:3.8b"
--judge-model "phi3:3.8b"
```

See [Model Selection Guide](docs/user-guide/models.md) for detailed recommendations.

## 📚 Documentation

Comprehensive documentation is available at [docs/](docs/):

- [Getting Started](docs/getting-started/installation.md) - Installation and setup
- [Quick Start](docs/getting-started/quickstart.md) - Basic tutorial
- [User Guide](docs/user-guide/) - Detailed usage instructions
- [Performance](docs/performance/) - Optimization guides
- [API Reference](docs/api/) - Python API documentation

## 🐳 Docker Deployment

### Quick Start

```bash
# Start all services (Ollama + SubtitleFlow + Docs)
docker-compose up -d

# Pull required models
docker-compose exec ollama ollama pull llama3.2:3b
docker-compose exec ollama ollama pull qwen2.5:7b
docker-compose exec ollama ollama pull stablelm2:1.6b

# Process a video
docker-compose exec subtitleflow uv run python -m subtitleflow process-video /app/data/video.mp4 --langs "dutch,spanish"

# View documentation locally
# Open http://localhost:8000 in your browser
```

### Configuration

**Environment Variables:**
- `OLLAMA_HOST`: Ollama server URL (default: `http://ollama:11434` in Docker)
- `LOG_LEVEL`: Logging level (default: `INFO`)

**Volumes:**
- `./data`: Input video files
- `./output`: Output subtitle files
- `./cache`: Translation cache

**Services:**
- `ollama`: Ollama server (port 11434)
- `subtitleflow`: Main application
- `docs`: Documentation server (port 8000) - view docs at http://localhost:8000

**GPU Support:**
Requires NVIDIA Container Toolkit. Install with:
```bash
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

### Using External Ollama

To use an external Ollama server instead of the Docker service:

```yaml
# docker-compose.override.yml
services:
  subs:
    environment:
      - OLLAMA_HOST=http://host.docker.internal:11434
    depends_on: []  # Remove dependency on ollama service
```

### Using OpenRouter / Cloud APIs

```yaml
# docker-compose.override.yml
services:
  subs:
    environment:
      - OLLAMA_HOST=https://openrouter.ai/api/v1
      - OLLAMA_API_KEY=${OPENROUTER_API_KEY}
    depends_on: []  # Remove dependency on ollama service
```

## 🛠️ Development

### Setup

```bash
# Clone repository
git clone https://github.com/jochemvangrondelle/subtitleflow.git
cd subs

# Install with dev dependencies
uv pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
make test

# With coverage
make test-cov

# Specific test file
uv run pytest tests/test_translator.py
```

### Code Quality

```bash
# Lint
make lint

# Format
make format

# Type check
make type-check

# All checks
make check-all
```

### Building Documentation

```bash
# Build docs
make docs

# Serve locally
make docs-serve
```

## 📊 Project Status

- ✅ **Production Ready**: Comprehensive test suite (80%+ coverage)
- ✅ **Type Safe**: Strict type checking with mypy/pyright
- ✅ **Well Documented**: Complete documentation with MkDocs
- ✅ **CI/CD**: Automated testing and linting
- ✅ **Clean Architecture**: Modular design with separation of concerns

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run `make check-all`
6. Submit a pull request

## 📄 License

This work is licensed under the [PolyForm Noncommercial License 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0/).

See the [LICENSE](LICENSE) file for the full license text.

**Note**: This license permits noncommercial use only. Commercial use is not permitted under this license.

## 🙏 Acknowledgments

- Built with [Ollama](https://ollama.com/) for local LLM inference
- Uses [whisperx](https://github.com/m-bain/whisperX) for transcription
- Uses [srt](https://github.com/cdown/srt) for subtitle file handling
- Powered by [Typer](https://typer.tiangolo.com/) and [Rich](https://github.com/Textualize/rich) for CLI

## 🔗 Links

- **Documentation**: [Read the Docs](https://subtitleflow.readthedocs.io)
- **Issues**: [GitHub Issues](https://github.com/jochemvangrondelle/subtitleflow/issues)
- **Discussions**: [GitHub Discussions](https://github.com/jochemvangrondelle/subtitleflow/discussions)

---

**Version**: 2.0.0
**Status**: ✅ Production Ready
