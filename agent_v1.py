"""
Local Voice Agent for LiveKit (Updated for livekit-agents v1.3+)
Fully local STT-LLM-TTS pipeline optimized for Mac M4
"""

import asyncio
import logging
import os
from typing import Optional

from livekit import agents, rtc
from livekit.agents import (
    JobContext,
    WorkerOptions,
    cli,
    llm,
)
from livekit.plugins import silero

from dotenv import load_dotenv
from rich.console import Console
from rich.logging import RichHandler

# Import custom plugins
from stt import WhisperMLXSTT
from llm import MLXLLM
from tts import NeuTTSAirTTS

# Load environment variables
load_dotenv()

# Setup rich logging
console = Console()
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console, rich_tracebacks=True)],
)

logger = logging.getLogger(__name__)


class VoiceAgent:
    """Main voice agent class for livekit-agents v1.3+"""

    def __init__(self):
        self.system_prompt = os.getenv(
            "SYSTEM_PROMPT",
            "You are a helpful voice assistant running completely locally on Mac. "
            "Keep your responses concise and natural for voice conversation.",
        )

        # Configuration from environment
        self.config = {
            "stt_model": os.getenv("STT_MODEL", "mlx-community/whisper-large-v3-turbo"),
            "stt_language": os.getenv("STT_LANGUAGE", "en"),
            "llm_model": os.getenv(
                "LLM_MODEL", "mlx-community/Meta-Llama-3.1-8B-Instruct-4bit"
            ),
            "llm_max_tokens": int(os.getenv("LLM_MAX_TOKENS", "512")),
            "llm_temperature": float(os.getenv("LLM_TEMPERATURE", "0.7")),
            "tts_backbone": os.getenv("TTS_BACKBONE", "neuphonic/neutts-air-q4-gguf"),
            "tts_codec": os.getenv("TTS_CODEC", "neuphonic/neucodec-onnx-decoder"),
            "voice_codes": os.getenv("VOICE_CLONE_CODES"),
            "voice_text": os.getenv("VOICE_CLONE_TEXT"),
        }

        logger.info("Voice Agent initialized with configuration:")
        logger.info(f"  STT Model: {self.config['stt_model']}")
        logger.info(f"  LLM Model: {self.config['llm_model']}")
        logger.info(f"  TTS Backbone: {self.config['tts_backbone']}")

    async def entrypoint(self, ctx: JobContext):
        """Main entry point for the voice agent"""
        logger.info(f"Starting voice agent for room: {ctx.room.name}")

        # Connect to room
        await ctx.connect()
        logger.info(f"✓ Connected to room: {ctx.room.name}")

        # Initialize components
        logger.info("Initializing pipeline components...")

        # VAD (Voice Activity Detection)
        vad = silero.VAD.load()
        logger.info("✓ VAD loaded")

        # STT (Whisper MLX)
        stt = WhisperMLXSTT(
            model=self.config["stt_model"],
            language=self.config["stt_language"],
        )
        logger.info("✓ STT initialized")

        # LLM (MLX)
        llm_instance = MLXLLM(
            model=self.config["llm_model"],
            max_tokens=self.config["llm_max_tokens"],
            temperature=self.config["llm_temperature"],
        )
        logger.info("✓ LLM initialized")

        # TTS (NeuTTS Air)
        tts = NeuTTSAirTTS(
            backbone_repo=self.config["tts_backbone"],
            codec_repo=self.config["tts_codec"],
            ref_codes_path=self.config["voice_codes"],
            ref_text_path=self.config["voice_text"],
        )
        logger.info("✓ TTS initialized")

        # Create assistant using the new v1.3+ API
        # Note: The API changed significantly in v1.3+
        # We need to manually handle the voice pipeline
        
        assistant = agents.VoiceAssistant(
            vad=vad,
            stt=stt,
            llm=llm_instance,
            tts=tts,
            chat_ctx=llm.ChatContext().append(
                role="system",
                text=self.system_prompt,
            ),
        )

        # Start the assistant
        assistant.start(ctx.room)
        logger.info("✓ Voice agent started and ready!")

        # Initial greeting
        greeting = (
            "Hello! I'm your local voice assistant running entirely on your Mac. "
            "Everything is processed locally, so your privacy is fully protected. "
            "How can I help you today?"
        )

        await assistant.say(greeting, allow_interruptions=True)
        logger.info("✓ Greeting sent")

        # Keep agent alive
        logger.info("Agent is now active and listening...")


def create_agent():
    """Factory function to create agent instance"""
    return VoiceAgent()


async def entrypoint(ctx: JobContext):
    """Entry point wrapper"""
    agent = create_agent()
    await agent.entrypoint(ctx)


async def request_fnc(req: agents.JobRequest):
    """Accept all job requests"""
    logger.info(f"Received job request for room: {req.room.name}")
    await req.accept(entrypoint)


def main():
    """Main function to run the agent"""
    console.print("[bold green]Local Voice Agent Starting...[/bold green]")
    console.print("[cyan]Optimized for Mac M4 with Apple Silicon[/cyan]")
    console.print("[yellow]Using livekit-agents v1.3+ API[/yellow]")
    console.print()

    # Validate environment
    required_env_vars = ["LIVEKIT_URL", "LIVEKIT_API_KEY", "LIVEKIT_API_SECRET"]
    missing = [var for var in required_env_vars if not os.getenv(var)]

    if missing:
        console.print(
            f"[bold red]Error: Missing required environment variables:[/bold red]"
        )
        for var in missing:
            console.print(f"  - {var}")
        console.print()
        console.print("Please check your .env file")
        return

    # Run agent
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            request_fnc=request_fnc,
        )
    )


if __name__ == "__main__":
    main()
