# Copyright (c) 2025 SubtitleFlow Team
#
# This work is licensed under the PolyForm Noncommercial License 1.0.0.
# To view a copy of this license, visit https://polyformproject.org/licenses/noncommercial/1.0.0/
# or send a letter to PolyForm Project, PO Box 1866, Mountain View, CA 94042.
#

"""Transcription service for subtitleflow using WhisperX."""

import logging
import subprocess
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


class TranscriptionService:
    """Service for transcribing video files to subtitles using WhisperX."""

    def transcribe(
        self,
        video_file: Path,
        output_file: Path,
        model: str = "large-v2",
        language: str = "en",
        device: str = "cuda",
        batch_size: int = 4,
    ) -> Path:
        """
        Transcribe video file to SRT subtitles using WhisperX.

        Args:
            video_file: Input video file path
            output_file: Output SRT file path
            model: WhisperX model name (tiny, base, small, medium, large-v2, large-v3)
            language: Language code (en, nl, es, etc.)
            device: Device to use (cuda or cpu)
            batch_size: Batch size for processing

        Returns:
            Path to output SRT file

        Raises:
            ImportError: If WhisperX is not installed
            subprocess.CalledProcessError: If FFmpeg fails
            Exception: For other transcription errors
        """
        if not video_file.exists():
            msg = f"Video file not found: {video_file}"
            raise FileNotFoundError(msg)

        # Lazy import - only import when actually used
        try:
            import whisperx
        except ImportError as e:
            msg = "WhisperX not installed. Install with: pip install subtitleflow[transcribe]"
            raise ImportError(msg) from e

        # Extract audio to temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_audio:
            tmp_audio_path = tmp_audio.name

        try:
            logger.info("🎧 Extracting audio...")
            subprocess.run(
                [
                    "ffmpeg",
                    "-hide_banner",
                    "-loglevel",
                    "warning",
                    "-i",
                    str(video_file),
                    "-vn",
                    "-ac",
                    "1",
                    "-ar",
                    "16000",
                    "-c:a",
                    "pcm_s16le",
                    "-y",
                    tmp_audio_path,
                ],
                check=True,
            )
            logger.info("✓ Audio extracted")

            # Transcribe with WhisperX
            logger.info(f"🗣️ Transcribing with WhisperX (model: {model})...")
            result = whisperx.load_audio(tmp_audio_path)
            model_obj = whisperx.load_model(
                model, device=device, compute_type="float16" if device == "cuda" else "int8"
            )
            result = whisperx.transcribe(
                result, model_obj, language=language, batch_size=batch_size
            )

            # Convert to SRT
            logger.info("📝 Converting to SRT format...")
            with open(output_file, "w", encoding="utf-8") as f:
                for i, segment in enumerate(result["segments"], 1):
                    start = segment["start"]
                    end = segment["end"]
                    text = segment["text"].strip()

                    # Format timestamps
                    def format_timestamp(seconds: float) -> str:
                        hours = int(seconds // 3600)
                        minutes = int((seconds % 3600) // 60)
                        secs = seconds % 60
                        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}".replace(".", ",")

                    f.write(f"{i}\n")
                    f.write(f"{format_timestamp(start)} --> {format_timestamp(end)}\n")
                    f.write(f"{text}\n\n")

            logger.info(f"✅ Transcription complete: {output_file}")
            return output_file

        except subprocess.CalledProcessError as e:
            logger.exception(f"❌ FFmpeg error: {e}")
            raise
        except Exception as e:
            logger.exception(f"❌ Transcription error: {e}")
            raise
        finally:
            # Clean up temporary audio file
            if Path(tmp_audio_path).exists():
                Path(tmp_audio_path).unlink()
