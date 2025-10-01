import requests
import json
from typing import Dict, Any, List, Optional
import re

from src.summarization.base import SummarizationEngine

class OllamaEngine(SummarizationEngine):
    """Ollama local summarization engine"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get('base_url', 'http://localhost:11434')
        self.model_name = config.get('model_name', 'qwen2.5:3b')
        self.max_tokens = config.get('max_tokens', 1000)
        self.temperature = config.get('temperature', 0.7)

    def initialize(self) -> bool:
        """Initialize connection to Ollama"""
        try:
            # Test connection to Ollama
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json()
                model_names = [model['name'] for model in models.get('models', [])]

                if self.model_name in model_names:
                    print(f"Connected to Ollama with model '{self.model_name}'")
                    self.is_initialized = True
                    return True
                else:
                    print(f"Model '{self.model_name}' not found in Ollama")
                    print(f"Available models: {model_names}")
                    return False
            else:
                print(f"Failed to connect to Ollama: {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"Failed to initialize Ollama: {e}")
            print("Make sure Ollama is running and accessible")
            return False

    def _generate_response(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """Generate response using Ollama API"""
        if not self.is_initialized:
            raise RuntimeError("OllamaEngine not initialized")

        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens or self.max_tokens,
                    "temperature": self.temperature,
                    "top_p": 0.9,
                    "stop": ["<|endoftext|>", "<|im_end|>"]
                }
            }

            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=120  # 2 minute timeout for generation
            )

            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                print(f"Ollama API error: {response.status_code}")
                return ""

        except requests.exceptions.RequestException as e:
            print(f"Error calling Ollama API: {e}")
            return ""

    def summarize(self, text: str, max_tokens: Optional[int] = None) -> Dict[str, Any]:
        """Summarize meeting transcript"""
        prompt = f"""Please provide a concise summary of the following meeting transcript.
Focus on the main topics discussed, decisions made, and important points raised.

Meeting Transcript:
{text}

Summary:"""

        try:
            summary = self._generate_response(prompt, max_tokens)

            return {
                'summary': summary,
                'success': True
            }
        except Exception as e:
            return {
                'summary': '',
                'success': False,
                'error': str(e)
            }

    def extract_action_items(self, text: str) -> List[str]:
        """Extract action items from meeting text"""
        prompt = f"""Please extract all action items from the following meeting transcript.
List each action item as a separate bullet point. Include who is responsible if mentioned.
Format: - Action item description

Meeting Transcript:
{text}

Action Items:"""

        try:
            response = self._generate_response(prompt, 500)

            # Parse action items from response
            action_items = []
            lines = response.split('\n')

            for line in lines:
                line = line.strip()
                if line and (line.startswith('-') or line.startswith('•') or line.startswith('*') or
                           re.match(r'^\d+\.', line)):
                    # Clean up the action item
                    action_item = re.sub(r'^[-•*\d\.]\s*', '', line)
                    if action_item and len(action_item) > 5:  # Minimum length check
                        action_items.append(action_item)

            return action_items[:10]  # Limit to 10 action items

        except Exception as e:
            print(f"Error extracting action items: {e}")
            return []

    def extract_key_points(self, text: str) -> List[str]:
        """Extract key points from meeting text"""
        prompt = f"""Please extract the key points and main topics discussed in the following meeting transcript.
List each key point as a separate bullet point.
Format: - Key point description

Meeting Transcript:
{text}

Key Points:"""

        try:
            response = self._generate_response(prompt, 500)

            # Parse key points from response
            key_points = []
            lines = response.split('\n')

            for line in lines:
                line = line.strip()
                if line and (line.startswith('-') or line.startswith('•') or line.startswith('*') or
                           re.match(r'^\d+\.', line)):
                    # Clean up the key point
                    key_point = re.sub(r'^[-•*\d\.]\s*', '', line)
                    if key_point and len(key_point) > 5:  # Minimum length check
                        key_points.append(key_point)

            return key_points[:8]  # Limit to 8 key points

        except Exception as e:
            print(f"Error extracting key points: {e}")
            return []

    def get_available_models(self) -> List[str]:
        """Get list of available models in Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json()
                return [model['name'] for model in models.get('models', [])]
            return []
        except Exception:
            return []

    def cleanup(self):
        """Clean up resources (nothing to cleanup for API-based engine)"""
        self.is_initialized = False