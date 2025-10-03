"""
Whisper.cpp STT Engine for RISC-V.

Uses whisper.cpp C++ implementation which doesn't require PyTorch.
Perfect for RISC-V systems where PyTorch is not available.
"""

import subprocess
import tempfile
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union
import logging
import os
import wave

from src.stt.base import STTEngine

logger = logging.getLogger(__name__)


class WhisperCppEngine(STTEngine):
    """Whisper.cpp STT Engine (no PyTorch needed)"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model_size = config.get('model_size', 'base')
        self.language = config.get('language', 'auto')

        # Whisper.cpp paths
        self.whisper_cpp_dir = Path.home() / "whisper.cpp"
        self.binary_path = self.whisper_cpp_dir / "main"
        self.model_path = self.whisper_cpp_dir / f"models/ggml-{self.model_size}.bin"

        # Additional options
        self.threads = config.get('threads', 4)
        self.translate = config.get('translate', False)

    def initialize(self) -> bool:
        """Initialize Whisper.cpp engine"""
        try:
            # Check if whisper.cpp is installed
            if not self.whisper_cpp_dir.exists():
                logger.error(
                    f"Whisper.cpp not found at {self.whisper_cpp_dir}\n"
                    f"Install it with: bash RISCV_INSTALL_WHISPER_CPP.sh"
                )
                return False

            if not self.binary_path.exists():
                logger.error(f"Whisper.cpp binary not found at {self.binary_path}")
                return False

            if not self.model_path.exists():
                logger.error(f"Whisper model not found at {self.model_path}")
                return False

            # Test binary
            result = subprocess.run(
                [str(self.binary_path), "-h"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                logger.error("Whisper.cpp binary test failed")
                return False

            self.is_initialized = True
            logger.info(f"Whisper.cpp initialized successfully (model: {self.model_size})")
            logger.info(f"  Binary: {self.binary_path}")
            logger.info(f"  Model: {self.model_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Whisper.cpp: {e}")
            return False

    def transcribe(
        self,
        audio: Union[str, bytes],
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribe audio using whisper.cpp.

        Args:
            audio: Audio file path or bytes
            language: Language code (e.g., 'en', 'zh')

        Returns:
            Dictionary with 'text' and 'success' keys
        """
        if not self.is_initialized:
            return {
                'text': '',
                'success': False,
                'error': 'Engine not initialized'
            }

        try:
            # Handle audio input
            if isinstance(audio, bytes):
                # Save to temporary WAV file
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                    tmp.write(audio)
                    audio_path = tmp.name
                temp_file = True
            else:
                audio_path = audio
                temp_file = False

            # Convert to 16kHz WAV if needed
            audio_path = self._ensure_wav_format(audio_path)

            # Build command
            cmd = [
                str(self.binary_path),
                '-m', str(self.model_path),
                '-f', audio_path,
                '-t', str(self.threads),
                '--output-txt',  # Output as text
                '--no-timestamps'  # No timestamps for cleaner output
            ]

            # Add language if specified
            lang = language or self.language
            if lang and lang != 'auto':
                cmd.extend(['-l', lang])

            # Add translate option
            if self.translate:
                cmd.append('--translate')

            # Run whisper.cpp
            logger.debug(f"Running: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                cwd=str(self.whisper_cpp_dir)
            )

            # Clean up temp file
            if temp_file:
                try:
                    os.unlink(audio_path)
                except:
                    pass

            if result.returncode != 0:
                logger.error(f"Whisper.cpp failed: {result.stderr}")
                return {
                    'text': '',
                    'success': False,
                    'error': result.stderr
                }

            # Extract text from output
            # whisper.cpp outputs text to stdout
            text = result.stdout.strip()

            # Remove any progress indicators or extra info
            lines = text.split('\n')
            # Take only the transcription lines (skip progress/info lines)
            transcription = ' '.join([
                line.strip() for line in lines
                if line.strip() and not line.startswith('[')
            ])

            logger.info(f"Transcription successful ({len(transcription)} chars)")

            return {
                'text': transcription,
                'success': True,
                'language': lang
            }

        except subprocess.TimeoutExpired:
            logger.error("Whisper.cpp transcription timeout")
            return {
                'text': '',
                'success': False,
                'error': 'Transcription timeout'
            }
        except Exception as e:
            logger.error(f"Transcription error: {e}", exc_info=True)
            return {
                'text': '',
                'success': False,
                'error': str(e)
            }

    def transcribe_stream(self, audio_chunk: bytes) -> Dict[str, Any]:
        """
        Stream transcription not directly supported by whisper.cpp.
        We buffer chunks and transcribe when enough data is accumulated.
        """
        # For now, return empty - streaming needs more complex buffering
        logger.warning("Stream transcription not yet implemented for whisper.cpp")
        return {
            'text': '',
            'partial': True,
            'success': True
        }

    def _ensure_wav_format(self, audio_path: str) -> str:
        """
        Ensure audio is in WAV format with 16kHz sample rate.

        Args:
            audio_path: Path to audio file

        Returns:
            Path to WAV file (original or converted)
        """
        try:
            # Check if it's already a WAV file
            if audio_path.endswith('.wav'):
                # Check sample rate
                with wave.open(audio_path, 'rb') as wav:
                    if wav.getframerate() == 16000:
                        return audio_path

            # Convert to 16kHz WAV using ffmpeg
            output_path = audio_path.replace(
                Path(audio_path).suffix,
                '_16k.wav'
            )

            cmd = [
                'ffmpeg',
                '-i', audio_path,
                '-ar', '16000',  # 16kHz sample rate
                '-ac', '1',  # Mono
                '-y',  # Overwrite
                output_path
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=60
            )

            if result.returncode == 0:
                return output_path
            else:
                logger.warning(f"ffmpeg conversion failed, using original: {result.stderr}")
                return audio_path

        except Exception as e:
            logger.warning(f"Audio conversion failed: {e}, using original")
            return audio_path

    def cleanup(self):
        """Clean up resources"""
        self.is_initialized = False
        logger.info("Whisper.cpp engine cleaned up")
