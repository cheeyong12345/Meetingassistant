from src.summarization.manager import SummarizationManager
from src.summarization.base import SummarizationEngine

# Qwen engine is optional (requires transformers which may not be available on RISC-V)
try:
    from src.summarization.qwen_engine import QwenEngine
    QWEN_AVAILABLE = True
except ImportError as e:
    QwenEngine = None
    QWEN_AVAILABLE = False
    import logging
    logging.warning(f"Qwen engine not available: {e}")
    logging.info("App can work without Qwen - use Ollama or other engines")

# Ollama engine
try:
    from src.summarization.ollama_engine import OllamaEngine
    OLLAMA_AVAILABLE = True
except ImportError:
    OllamaEngine = None
    OLLAMA_AVAILABLE = False

__all__ = ['SummarizationManager', 'SummarizationEngine', 'QwenEngine', 'OllamaEngine', 'QWEN_AVAILABLE', 'OLLAMA_AVAILABLE']