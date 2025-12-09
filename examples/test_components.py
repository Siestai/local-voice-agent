#!/usr/bin/env python3
"""
Quick test script to verify all components are working
"""

import asyncio
import logging
from rich.console import Console

console = Console()
logging.basicConfig(level=logging.INFO)


async def test_stt():
    """Test Speech-to-Text"""
    console.print("[cyan]Testing STT (Whisper MLX)...[/cyan]")
    try:
        from stt import WhisperMLXSTT

        stt = WhisperMLXSTT(
            model="mlx-community/whisper-large-v3-turbo", language="en"
        )
        console.print("[green]✓ STT initialized successfully[/green]")
        return True
    except Exception as e:
        console.print(f"[red]✗ STT failed: {e}[/red]")
        return False


async def test_llm():
    """Test Language Model"""
    console.print("[cyan]Testing LLM (MLX)...[/cyan]")
    try:
        from llm import MLXLLM

        llm = MLXLLM(
            model="mlx-community/Meta-Llama-3.1-8B-Instruct-4bit",
            max_tokens=100,
        )
        console.print("[green]✓ LLM initialized successfully[/green]")
        return True
    except Exception as e:
        console.print(f"[red]✗ LLM failed: {e}[/red]")
        return False


async def test_tts():
    """Test Text-to-Speech"""
    console.print("[cyan]Testing TTS (NeuTTS Air)...[/cyan]")
    try:
        from tts import NeuTTSAirTTS

        tts = NeuTTSAirTTS(
            backbone_repo="neuphonic/neutts-air-q4-gguf",
            codec_repo="neuphonic/neucodec-onnx-decoder",
        )
        console.print("[green]✓ TTS initialized successfully[/green]")
        return True
    except Exception as e:
        console.print(f"[red]✗ TTS failed: {e}[/red]")
        return False


async def test_livekit_connection():
    """Test LiveKit connection"""
    console.print("[cyan]Testing LiveKit connection...[/cyan]")
    try:
        import os
        import aiohttp
        from dotenv import load_dotenv

        load_dotenv()

        url = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
        http_url = url.replace("ws://", "http://").replace("wss://", "https://")

        async with aiohttp.ClientSession() as session:
            async with session.get(http_url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status in [200, 404]:  # 404 is OK, means server is running
                    console.print("[green]✓ LiveKit server is reachable[/green]")
                    return True
                else:
                    console.print(f"[yellow]⚠ Unexpected status: {resp.status}[/yellow]")
                    return False
    except Exception as e:
        console.print(f"[red]✗ LiveKit connection failed: {e}[/red]")
        console.print("[yellow]Make sure LiveKit server is running[/yellow]")
        return False


async def main():
    """Run all tests"""
    console.print("\n[bold]Voice Agent Component Tests[/bold]\n")

    results = []

    # Test each component
    results.append(("STT", await test_stt()))
    console.print()

    results.append(("LLM", await test_llm()))
    console.print()

    results.append(("TTS", await test_tts()))
    console.print()

    results.append(("LiveKit", await test_livekit_connection()))
    console.print()

    # Summary
    console.print("[bold]Summary:[/bold]")
    all_passed = True
    for name, passed in results:
        status = "[green]✓[/green]" if passed else "[red]✗[/red]"
        console.print(f"  {status} {name}")
        if not passed:
            all_passed = False

    console.print()

    if all_passed:
        console.print("[bold green]All tests passed! 🎉[/bold green]")
        console.print("\nYou're ready to run the agent:")
        console.print("  [cyan]python agent.py dev[/cyan]")
    else:
        console.print("[bold red]Some tests failed[/bold red]")
        console.print("\nPlease check:")
        console.print("  1. Dependencies are installed: [cyan]pip install -r requirements.txt[/cyan]")
        console.print("  2. NeuTTS Air is installed: [cyan]make install-neutts[/cyan]")
        console.print("  3. LiveKit server is running: [cyan]make start[/cyan] (in server directory)")

    console.print()


if __name__ == "__main__":
    asyncio.run(main())
