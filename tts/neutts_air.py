"""
NeuTTS Air Text-to-Speech Plugin for LiveKit Agents
Optimized for Apple Silicon M4 with voice cloning
"""

import asyncio
import logging
from typing import AsyncIterable, Optional
import numpy as np
import torch

from livekit import agents, rtc
from livekit.agents import tts

logger = logging.getLogger(__name__)


class NeuTTSAirTTS(tts.TTS):
    """
    NeuTTS Air-based Text-to-Speech implementation.
    Supports voice cloning with reference audio.
    """

    def __init__(
        self,
        *,
        backbone_repo: str = "neuphonic/neutts-air-q4-gguf",
        codec_repo: str = "neuphonic/neucodec-onnx-decoder",
        device: str = "mps",
        ref_audio_path: Optional[str] = None,
        ref_text_path: Optional[str] = None,
        ref_codes_path: Optional[str] = None,
        sample_rate: int = 24000,
    ):
        """
        Initialize NeuTTS Air TTS.

        Args:
            backbone_repo: HuggingFace repo for backbone model
            codec_repo: HuggingFace repo for codec
            device: Device to use (mps for Apple Silicon)
            ref_audio_path: Path to reference audio for voice cloning
            ref_text_path: Path to reference text transcript
            ref_codes_path: Path to pre-encoded reference codes (faster)
            sample_rate: Audio sample rate
        """
        super().__init__(
            capabilities=tts.TTSCapabilities(streaming=False),
            sample_rate=sample_rate,
            num_channels=1,
        )

        self.backbone_repo = backbone_repo
        self.codec_repo = codec_repo
        self.device = device
        self.ref_audio_path = ref_audio_path
        self.ref_text_path = ref_text_path
        self.ref_codes_path = ref_codes_path

        self._tts_engine = None
        self._ref_codes = None
        self._ref_text = None
        self._loaded = False

        logger.info(f"Initialized NeuTTS Air with backbone: {backbone_repo}")

    async def _ensure_loaded(self):
        """Lazy load the model and reference"""
        if not self._loaded:
            logger.info("Loading NeuTTS Air model...")
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._load_model)
            self._loaded = True
            logger.info("NeuTTS Air model loaded successfully")

    def _load_model(self):
        """Load model in thread pool (blocking operation)"""
        try:
            # Import here to avoid loading if not used
            from neuttsair.neutts import NeuTTSAir

            # Load TTS engine
            self._tts_engine = NeuTTSAir(
                backbone_repo=self.backbone_repo,
                backbone_device=self.device,
                codec_repo=self.codec_repo,
                codec_device=self.device,
            )

            # Load reference for voice cloning
            if self.ref_codes_path:
                # Use pre-encoded codes (fastest)
                logger.info(f"Loading pre-encoded voice codes: {self.ref_codes_path}")
                self._ref_codes = torch.load(self.ref_codes_path)
            elif self.ref_audio_path:
                # Encode on the fly
                logger.info(f"Encoding reference audio: {self.ref_audio_path}")
                self._ref_codes = self._tts_engine.encode_reference(self.ref_audio_path)

            # Load reference text
            if self.ref_text_path:
                with open(self.ref_text_path, "r") as f:
                    self._ref_text = f.read().strip()
                    logger.info(f"Loaded reference text: {len(self._ref_text)} chars")

        except ImportError:
            logger.error(
                "NeuTTS Air is not installed. Please install from: "
                "https://github.com/neuphonic/neutts-air"
            )
            raise

    def synthesize(self, text: str) -> "ChunkedStream":
        """Synthesize text to speech"""
        return NeuTTSAirStream(
            text=text,
            tts_engine=self._tts_engine,
            ref_codes=self._ref_codes,
            ref_text=self._ref_text,
            sample_rate=self._sample_rate,
            tts=self,
        )


class NeuTTSAirStream(tts.ChunkedStream):
    """
    Streaming TTS output for NeuTTS Air.
    """

    def __init__(
        self,
        *,
        text: str,
        tts_engine,
        ref_codes,
        ref_text: Optional[str],
        sample_rate: int,
        tts: NeuTTSAirTTS,
    ):
        super().__init__()
        self._text = text
        self._tts_engine = tts_engine
        self._ref_codes = ref_codes
        self._ref_text = ref_text
        self._sample_rate = sample_rate
        self._tts = tts
        self._sentence_stream = self._sentence_tokenizer(text)

    @staticmethod
    def _sentence_tokenizer(text: str):
        """Simple sentence tokenizer"""
        # Split on sentence boundaries
        import re

        sentences = re.split(r"(?<=[.!?])\s+", text)
        for sentence in sentences:
            if sentence.strip():
                yield sentence.strip()

    async def _run(self) -> None:
        """Generate audio stream"""
        await self._tts._ensure_loaded()

        try:
            # Process each sentence
            for sentence in self._sentence_stream:
                if not sentence:
                    continue

                logger.debug(f"Synthesizing: {sentence}")

                # Run synthesis in thread pool
                loop = asyncio.get_event_loop()
                audio_data = await loop.run_in_executor(
                    None, self._synthesize_sentence, sentence
                )

                if audio_data is not None and len(audio_data) > 0:
                    # Convert to audio frame
                    frame = rtc.AudioFrame(
                        data=audio_data.tobytes(),
                        sample_rate=self._sample_rate,
                        num_channels=1,
                        samples_per_channel=len(audio_data),
                    )

                    # Emit synthesized audio event
                    event = tts.SynthesizedAudio(
                        request_id="",
                        segment_id="",
                        frame=frame,
                        text=sentence,
                    )

                    self._event_ch.send_nowait(event)

        except Exception as e:
            logger.error(f"Error in TTS stream: {e}", exc_info=True)

    def _synthesize_sentence(self, text: str) -> Optional[np.ndarray]:
        """
        Synthesize a single sentence.
        Runs in thread pool to avoid blocking.
        """
        try:
            # Run inference
            wav = self._tts_engine.infer(
                text,
                self._ref_codes,
                self._ref_text,
            )

            # Convert to int16
            audio_int16 = (wav * 32767).astype(np.int16)
            return audio_int16

        except Exception as e:
            logger.error(f"Synthesis error: {e}", exc_info=True)
            return None

    async def aclose(self) -> None:
        """Close the stream"""
        await super().aclose()


# Factory function
def create_neutts_tts(
    backbone_repo: str = "neuphonic/neutts-air-q4-gguf",
    codec_repo: str = "neuphonic/neucodec-onnx-decoder",
    ref_codes_path: Optional[str] = None,
    ref_text_path: Optional[str] = None,
) -> NeuTTSAirTTS:
    """
    Factory function to create NeuTTS Air TTS instance.

    Args:
        backbone_repo: Backbone model repo
        codec_repo: Codec repo
        ref_codes_path: Pre-encoded reference codes
        ref_text_path: Reference text path

    Returns:
        NeuTTSAirTTS instance
    """
    return NeuTTSAirTTS(
        backbone_repo=backbone_repo,
        codec_repo=codec_repo,
        ref_codes_path=ref_codes_path,
        ref_text_path=ref_text_path,
    )
