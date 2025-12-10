"""
MLX Language Model Plugin for LiveKit Agents
Optimized for Apple Silicon M4
"""

import asyncio
import logging
from typing import Optional

from livekit.agents import llm

try:
    import mlx_lm
except ImportError:
    raise ImportError(
        "mlx-lm is not installed. Install it with: pip install mlx-lm"
    )

logger = logging.getLogger(__name__)


class MLXLLM(llm.LLM):
    """
    MLX-based Language Model implementation.
    Uses MLX framework for optimized inference on Apple Silicon.
    """

    def __init__(
        self,
        *,
        model: str = "mlx-community/Meta-Llama-3.1-8B-Instruct-4bit",
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
    ):
        """
        Initialize MLX LLM.

        Args:
            model: HuggingFace model ID or local path
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
        """
        super().__init__()
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self._loaded = False
        self._model = None
        self._tokenizer = None

        logger.info(f"Initialized MLX LLM with model: {model}")

    async def _ensure_loaded(self):
        """Ensure model is loaded (lazy loading)"""
        if not self._loaded:
            logger.info(f"Loading MLX model: {self.model}")
            loop = asyncio.get_event_loop()
            
            # Load model and tokenizer in thread pool
            self._model, self._tokenizer = await loop.run_in_executor(
                None,
                lambda: mlx_lm.load(self.model)
            )
            
            self._loaded = True
            logger.info("MLX model ready")

    def chat(
        self,
        *,
        chat_ctx: llm.ChatContext,
        temperature: Optional[float] = None,
        n: int = 1,
    ) -> "MLXLLMStream":
        """Create a chat completion stream"""
        return MLXLLMStream(
            model=self._model,
            tokenizer=self._tokenizer,
            chat_ctx=chat_ctx,
            llm=self,
            temperature=temperature or self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
        )


class MLXLLMStream(llm.LLMStream):
    """
    LLM stream for MLX.
    Generates text completions using MLX models.
    """

    def __init__(
        self,
        *,
        model,
        tokenizer,
        chat_ctx: llm.ChatContext,
        llm: MLXLLM,
        temperature: float,
        max_tokens: int,
        top_p: float,
    ):
        super().__init__(chat_ctx=chat_ctx)
        self._model = model
        self._tokenizer = tokenizer
        self._llm = llm
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._top_p = top_p

    async def _run(self) -> None:
        """Main processing loop"""
        await self._llm._ensure_loaded()

        try:
            # Format messages for the model
            prompt = self._format_messages(self._chat_ctx.messages)
            
            # Generate response in thread pool
            loop = asyncio.get_event_loop()
            response_text = await loop.run_in_executor(
                None,
                self._generate,
                prompt
            )

            # Create completion chunk
            chunk = llm.ChatChunk(
                choices=[
                    llm.Choice(
                        delta=llm.ChoiceDelta(
                            role="assistant",
                            content=response_text,
                        ),
                        index=0,
                    )
                ]
            )

            # Send the chunk
            self._event_ch.send_nowait(chunk)

            logger.debug(f"Generated response: {response_text[:100]}...")

        except Exception as e:
            logger.error(f"Error in LLM stream: {e}", exc_info=True)

    def _format_messages(self, messages: list) -> str:
        """
        Format chat messages into a prompt string.
        Adapts to the model's expected format.
        """
        prompt_parts = []
        
        for msg in messages:
            role = msg.role
            content = msg.content
            
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        prompt_parts.append("Assistant:")
        return "\n\n".join(prompt_parts)

    def _generate(self, prompt: str) -> str:
        """
        Generate text using MLX model.
        Runs in thread pool to avoid blocking.
        """
        try:
            # Generate using mlx_lm
            response = mlx_lm.generate(
                self._model,
                self._tokenizer,
                prompt=prompt,
                max_tokens=self._max_tokens,
                temp=self._temperature,
                top_p=self._top_p,
                verbose=False,
            )

            return response.strip()

        except Exception as e:
            logger.error(f"Generation error: {e}", exc_info=True)
            return "I apologize, but I encountered an error processing your request."

    async def aclose(self) -> None:
        """Close the stream"""
        await super().aclose()


# Factory function for easy creation
def create_mlx_llm(
    model: str = "mlx-community/Meta-Llama-3.1-8B-Instruct-4bit",
    max_tokens: int = 512,
    temperature: float = 0.7,
) -> MLXLLM:
    """
    Factory function to create MLX LLM instance.

    Args:
        model: Model to use
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature

    Returns:
        MLXLLM instance
    """
    return MLXLLM(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
    )
