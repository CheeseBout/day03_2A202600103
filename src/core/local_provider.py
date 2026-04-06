import time
import os
from typing import Dict, Any, Optional, Generator
from llama_cpp import Llama
from src.core.llm_provider import LLMProvider

class LocalProvider(LLMProvider):
    """
    LLM Provider for local models using llama-cpp-python.
    Optimized for CPU usage with GGUF models.
    """
    def __init__(self, model_path: str, n_ctx: int = 4096, n_threads: Optional[int] = None):
        """
        Initialize the local Llama model.
        Args:
            model_path: Path to the .gguf model file.
            n_ctx: Context window size.
            n_threads: Number of CPU threads to use. Defaults to all available.
        """
        super().__init__(model_name=os.path.basename(model_path))
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}. Please download it first.")

        # n_threads=None will use all available cores
        self.llm = Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_threads=n_threads,
            verbose=False
        )

    def _build_messages(self, prompt: str, system_prompt: Optional[str] = None):
        """Build a messages list for the chat completion API."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return messages

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        start_time = time.time()

        messages = self._build_messages(prompt, system_prompt)

        response = self.llm.create_chat_completion(
            messages=messages,
            max_tokens=1024,
            stop=["Observation:"],
        )

        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)

        content = response["choices"][0]["message"]["content"].strip()
        usage = {
            "prompt_tokens": response["usage"]["prompt_tokens"],
            "completion_tokens": response["usage"]["completion_tokens"],
            "total_tokens": response["usage"]["total_tokens"]
        }

        return {
            "content": content,
            "usage": usage,
            "latency_ms": latency_ms,
            "provider": "local"
        }

    def stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        messages = self._build_messages(prompt, system_prompt)

        stream = self.llm.create_chat_completion(
            messages=messages,
            max_tokens=1024,
            stop=["Observation:"],
            stream=True
        )

        for chunk in stream:
            delta = chunk["choices"][0].get("delta", {})
            token = delta.get("content", "")
            if token:
                yield token
