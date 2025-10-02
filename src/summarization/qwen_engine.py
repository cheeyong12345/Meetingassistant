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
        """Summarize meeting transcript with improved prompt"""
        prompt = f"""You are an expert meeting summarizer. Analyze the transcript and create a professional summary.

TRANSCRIPT:
{text}

INSTRUCTIONS:
1. Write a brief overview (2-3 sentences) summarizing the main purpose
2. Extract 3-5 key discussion points
3. List any action items or decisions mentioned
4. Keep the summary concise - aim for 30-40% of original length
5. Use clear, professional language
6. DO NOT copy sentences verbatim - paraphrase and condense

SUMMARY FORMAT:
**Overview:**
[Brief 2-3 sentence summary of the meeting]

**Key Points:**
• [Main point 1]
• [Main point 2]
• [Main point 3]

**Action Items:**
• [Action item 1 if any]

**Decisions:**
• [Decision 1 if any]

Now provide the summary:"""

        try:
            summary = self._generate_response(prompt, max_tokens or 800)

            # Validate summary is not just copying
            if summary and len(summary) < len(text) * 0.9:
                return {
                    'summary': summary,
                    'success': True
                }
            else:
                # Fallback to extractive summary
                return {
                    'summary': self._extractive_summary(text),
                    'success': True,
                    'fallback': True
                }
        except Exception as e:
            return {
                'summary': self._extractive_summary(text),
                'success': True,
                'fallback': True,
                'error': str(e)
            }

    def _extractive_summary(self, text: str) -> str:
        """Simple extractive summarization fallback"""
        sentences = [s.strip() for s in text.split('.') if s.strip()]

        # Take first sentence, middle sentences, and last sentence
        if len(sentences) <= 3:
            return '. '.join(sentences) + '.'

        summary_sentences = [
            sentences[0],  # First sentence
            sentences[len(sentences)//2],  # Middle
            sentences[-1]  # Last sentence
        ]

        return "**Summary (Key Points):**\n\n" + '. '.join(summary_sentences) + '.'

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