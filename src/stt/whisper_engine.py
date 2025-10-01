import whisper
import numpy as np
import torch
from typing import Dict, Any, Optional, Union
import warnings
warnings.filterwarnings("ignore")

from src.stt.base import STTEngine

class WhisperEngine(STTEngine):
    """OpenAI Whisper STT Engine"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model = None
        self.model_size = config.get('model_size', 'base')
        self.language = config.get('language', 'auto')
        self.device = config.get('device', 'auto')

    def initialize(self) -> bool:
        """Initialize Whisper model"""
        try:
            # Auto-detect device
            if self.device == 'auto':
                if torch.cuda.is_available():
                    self.device = 'cuda'
                elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                    self.device = 'mps'
                else:
                    self.device = 'cpu'

            print(f"Loading Whisper model '{self.model_size}' on device '{self.device}'...")
            self.model = whisper.load_model(self.model_size, device=self.device)
            self.is_initialized = True
            print(f"Whisper model loaded successfully")
            return True

        except Exception as e:
            print(f"Failed to initialize Whisper: {e}")
            return False

    def transcribe(self, audio_data: Union[str, np.ndarray]) -> Dict[str, Any]:
        """Transcribe audio file or numpy array"""
        if not self.is_initialized:
            raise RuntimeError("WhisperEngine not initialized")

        try:
            # Handle different input types
            if isinstance(audio_data, str):
                # File path
                result = self.model.transcribe(
                    audio_data,
                    language=None if self.language == 'auto' else self.language,
                    verbose=False
                )
            else:
                # Numpy array - ensure it's float32 and normalized
                if audio_data.dtype != np.float32:
                    audio_data = audio_data.astype(np.float32)

                # Normalize audio if needed
                if audio_data.max() > 1.0:
                    audio_data = audio_data / np.max(np.abs(audio_data))

                result = self.model.transcribe(
                    audio_data,
                    language=None if self.language == 'auto' else self.language,
                    verbose=False
                )

            # Format response
            segments = []
            if 'segments' in result:
                for segment in result['segments']:
                    segments.append({
                        'start': segment['start'],
                        'end': segment['end'],
                        'text': segment['text'].strip(),
                        'confidence': segment.get('avg_logprob', 0.0)
                    })

            return {
                'text': result['text'].strip(),
                'language': result.get('language', 'unknown'),
                'segments': segments,
                'confidence': sum([s.get('avg_logprob', 0.0) for s in result.get('segments', [])]) / max(len(result.get('segments', [])), 1)
            }

        except Exception as e:
            return {
                'text': '',
                'error': str(e),
                'confidence': 0.0,
                'segments': []
            }

    def transcribe_stream(self, audio_chunk: np.ndarray) -> Optional[str]:
        """Transcribe streaming audio chunk"""
        if not self.is_initialized:
            return None

        try:
            # For streaming, we'll use a simplified approach
            # In production, you might want to use a more sophisticated streaming solution
            if len(audio_chunk) < 16000:  # Less than 1 second of audio
                return None

            if audio_chunk.dtype != np.float32:
                audio_chunk = audio_chunk.astype(np.float32)

            if audio_chunk.max() > 1.0:
                audio_chunk = audio_chunk / np.max(np.abs(audio_chunk))

            result = self.model.transcribe(audio_chunk, language=None if self.language == 'auto' else self.language, verbose=False)
            return result['text'].strip() if result['text'].strip() else None

        except Exception as e:
            print(f"Streaming transcription error: {e}")
            return None

    def get_supported_languages(self) -> list[str]:
        """Get supported languages"""
        return [
            'auto', 'af', 'am', 'ar', 'as', 'az', 'ba', 'be', 'bg', 'bn', 'bo', 'br', 'bs', 'ca',
            'cs', 'cy', 'da', 'de', 'el', 'en', 'es', 'et', 'eu', 'fa', 'fi', 'fo', 'fr', 'gl',
            'gu', 'ha', 'haw', 'he', 'hi', 'hr', 'ht', 'hu', 'hy', 'id', 'is', 'it', 'ja', 'jw',
            'ka', 'kk', 'km', 'kn', 'ko', 'la', 'lb', 'ln', 'lo', 'lt', 'lv', 'mg', 'mi', 'mk',
            'ml', 'mn', 'mr', 'ms', 'mt', 'my', 'ne', 'nl', 'nn', 'no', 'oc', 'pa', 'pl', 'ps',
            'pt', 'ro', 'ru', 'sa', 'sd', 'si', 'sk', 'sl', 'sn', 'so', 'sq', 'sr', 'su', 'sv',
            'sw', 'ta', 'te', 'tg', 'th', 'tk', 'tl', 'tr', 'tt', 'uk', 'ur', 'uz', 'vi', 'yi',
            'yo', 'zh'
        ]

    def set_language(self, language: str) -> bool:
        """Set language for transcription"""
        if language in self.get_supported_languages():
            self.language = language
            return True
        return False

    def cleanup(self):
        """Clean up model resources"""
        if self.model is not None:
            del self.model
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        self.model = None
        self.is_initialized = False