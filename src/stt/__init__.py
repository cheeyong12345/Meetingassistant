from src.stt.manager import STTManager
from src.stt.base import STTEngine
from src.stt.vosk_engine import VoskEngine

# Whisper is optional (requires PyTorch which may not be available on RISC-V)
try:
    from src.stt.whisper_engine import WhisperEngine
    WHISPER_AVAILABLE = True
except ImportError:
    WhisperEngine = None
    WHISPER_AVAILABLE = False

__all__ = ['STTManager', 'STTEngine', 'WhisperEngine', 'VoskEngine', 'WHISPER_AVAILABLE']