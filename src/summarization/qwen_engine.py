import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from typing import Dict, Any, List, Optional
import re

from src.summarization.base import SummarizationEngine

class QwenEngine(SummarizationEngine):
    """Qwen3 local summarization engine"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self.model_name = config.get('model_name', 'Qwen/Qwen2.5-3B-Instruct')
        self.device = config.get('device', 'auto')
        self.max_tokens = config.get('max_tokens', 1000)
        self.temperature = config.get('temperature', 0.7)

    def initialize(self) -> bool:
        """Initialize Qwen model"""
        try:
            # Auto-detect device
            if self.device == 'auto':
                if torch.cuda.is_available():
                    self.device = 'cuda'
                elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                    self.device = 'mps'
                else:
                    self.device = 'cpu'

            print(f"Loading Qwen model '{self.model_name}' on device '{self.device}'...")

            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )

            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device != 'cpu' else torch.float32,
                device_map=self.device if self.device != 'cpu' else None,
                trust_remote_code=True
            )

            # Create text generation pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                torch_dtype=torch.float16 if self.device != 'cpu' else torch.float32,
                device_map=self.device if self.device != 'cpu' else None
            )

            self.is_initialized = True
            print("Qwen model loaded successfully")
            return True

        except Exception as e:
            print(f"Failed to initialize Qwen: {e}")
            return False

    def _generate_response(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """Generate response using Qwen model"""
        if not self.is_initialized:
            raise RuntimeError("QwenEngine not initialized")

        try:
            messages = [{"role": "user", "content": prompt}]
            prompt_text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )

            outputs = self.pipeline(
                prompt_text,
                max_new_tokens=max_tokens or self.max_tokens,
                temperature=self.temperature,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )

            # Extract the generated text
            response = outputs[0]['generated_text']
            # Remove the prompt from the response
            response = response[len(prompt_text):].strip()

            return response

        except Exception as e:
            print(f"Error generating response: {e}")
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
                    if action_item:
                        action_items.append(action_item)

            return action_items[:10]  # Limit to 10 action items

        except Exception as e:
            print(f"Error extracting action items: {e}")
            return []

    def extract_key_points(self, text: str) -> List[str]:
        """Extract key points from meeting text"""
        prompt = f"""Please extract the key points and main topics discussed in the following meeting transcript.
List each key point as a separate bullet point.

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
                    if key_point:
                        key_points.append(key_point)

            return key_points[:8]  # Limit to 8 key points

        except Exception as e:
            print(f"Error extracting key points: {e}")
            return []

    def cleanup(self):
        """Clean up model resources"""
        if self.pipeline is not None:
            del self.pipeline
        if self.model is not None:
            del self.model
        if self.tokenizer is not None:
            del self.tokenizer

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        self.pipeline = None
        self.model = None
        self.tokenizer = None
        self.is_initialized = False