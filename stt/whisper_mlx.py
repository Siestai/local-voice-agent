"""
Whisper MLX Speech-to-Text Plugin for LiveKit Agents
Optimized for Apple Silicon M4
"""

import asyncio
import logging
import tempfile
from typing import AsyncIterable, Optional
import numpy as np
import soundfile as sf

from livekit import agents
from livekit.agents import stt

try:
    import mlx_whisper
except ImportError:
    raise ImportError(
        "mlx-whisper is not installed. Install it with: pip install mlx-whisper"
    )

logger = logging.getLogger(__name__)


class WhisperMLXSTT(stt.STT):
    """
    Whisper MLX-based Speech-to-Text implementation.
    Uses MLX framework for optimized inference on Apple Silicon.
    """

    def __init__(
        self,
        *,
        model: str = "mlx-community/whisper-large-v3-turbo",
        language: str = "en",
        device: str = "mps",
    ):
        """
        Initialize Whisper MLX STT.

        Args:
            model: HuggingFace model ID or local path
            language: Target language for transcription
            device: Device to use (mps for Apple Silicon)
        """
        super().__init__(
            capabilities=stt.STTCapabilities(streaming=False, interim_results=False)
        )
        self.model = model
        self.language = language
        self.device = device
        self._loaded = False

        logger.info(f"Initialized WhisperMLX with model: {model}")

    async def _ensure_loaded(self):
        """Ensure model is loaded (lazy loading)"""
        if not self._loaded:
            logger.info(f"Loading Whisper model: {self.model}")
            # Model is loaded on first use by mlx_whisper
            self._loaded = True
            logger.info("Whisper model ready")

    def stream(self) -> "WhisperMLXSpeechStream":
        """Create a new speech stream"""
        return WhisperMLXSpeechStream(
            model=self.model,
            language=self.language,
            stt=self,
        )


class WhisperMLXSpeechStream(stt.SpeechStream):
    """
    Speech stream for Whisper MLX.
    Buffers audio and transcribes in chunks.
    """

    def __init__(
        self,
        *,
        model: str,
        language: str,
        stt: WhisperMLXSTT,
    ):
        super().__init__()
        self.model = model
        self.language = language
        self._stt = stt
        self._buffer = []
        self._sample_rate = 16000
        self._min_chunk_duration = 3.0  # Process every 3 seconds minimum
        self._last_transcript_time = 0

    async def _run(self) -> None:
        """Main processing loop"""
        await self._stt._ensure_loaded()

        try:
            async for audio_frame in self._input_stream:
                # Convert audio frame to numpy array
                audio_data = np.frombuffer(audio_frame.data, dtype=np.int16).astype(
                    np.float32
                ) / 32768.0

                self._buffer.extend(audio_data)

                # Process when we have enough data
                buffer_duration = len(self._buffer) / self._sample_rate
                if buffer_duration >= self._min_chunk_duration:
                    await self._process_buffer()

        except Exception as e:
            logger.error(f"Error in speech stream: {e}", exc_info=True)
        finally:
            # Process any remaining audio
            if len(self._buffer) > 0:
                await self._process_buffer()

    async def _process_buffer(self):
        """Process buffered audio and emit transcription"""
        if len(self._buffer) == 0:
            return

        try:
            # Run transcription in thread pool
            loop = asyncio.get_event_loop()
            audio_array = np.array(self._buffer)
            result = await loop.run_in_executor(
                None, self._transcribe, audio_array
            )

            text = result.get("text", "").strip()

            if text:
                logger.debug(f"Transcribed: {text}")

                # Emit final transcript event
                event = stt.SpeechEvent(
                    type=stt.SpeechEventType.FINAL_TRANSCRIPT,
                    alternatives=[
                        stt.SpeechData(
                            text=text,
                            language=self.language,
                            confidence=1.0,
                        )
                    ],
                )
                self._event_ch.send_nowait(event)

            # Clear buffer
            self._buffer = []

        except Exception as e:
            logger.error(f"Error processing audio buffer: {e}", exc_info=True)
            self._buffer = []

    def _transcribe(self, audio_array: np.ndarray) -> dict:
        """
        Transcribe audio array using mlx_whisper.
        Runs in thread pool to avoid blocking.
        """
        try:
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(
                suffix=".wav", delete=False
            ) as temp_file:
                temp_path = temp_file.name
                sf.write(temp_path, audio_array, self._sample_rate)

            # Transcribe using mlx_whisper
            result = mlx_whisper.transcribe(
                temp_path,
                path_or_hf_repo=self.model,
                language=self.language,
                verbose=False,
            )

            # Clean up temp file
            import os
            os.unlink(temp_path)

            return result

        except Exception as e:
            logger.error(f"Transcription error: {e}", exc_info=True)
            return {"text": ""}

    async def aclose(self) -> None:
        """Close the stream"""
        await super().aclose()


# Factory function for easy creation
def create_whisper_stt(
    model: str = "mlx-community/whisper-large-v3-turbo",
    language: str = "en",
) -> WhisperMLXSTT:
    """
    Factory function to create Whisper MLX STT instance.

    Args:
        model: Model to use
        language: Target language

    Returns:
        WhisperMLXSTT instance
    """
    return WhisperMLXSTT(model=model, language=language)
