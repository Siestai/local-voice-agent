#!/usr/bin/env python3
"""
Voice Clone Setup Utility
Pre-encodes reference audio for faster TTS inference
"""

import os
import sys
import argparse
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_voice_clone(
    audio_path: str, text_path: str, output_dir: str = "./voice_clones"
):
    """
    Pre-encode reference audio for voice cloning.

    Args:
        audio_path: Path to reference audio file (.wav)
        text_path: Path to reference text transcript
        output_dir: Output directory for encoded files
    """
    try:
        import torch
        from neuttsair.neutts import NeuTTSAir
    except ImportError as e:
        logger.error(f"Required package not installed: {e}")
        logger.error("Please install: pip install torch neuttsair")
        sys.exit(1)

    # Validate inputs
    if not os.path.exists(audio_path):
        logger.error(f"Audio file not found: {audio_path}")
        sys.exit(1)

    if not os.path.exists(text_path):
        logger.error(f"Text file not found: {text_path}")
        sys.exit(1)

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Determine output paths
    base_name = Path(audio_path).stem
    codes_path = os.path.join(output_dir, f"{base_name}.pt")
    text_output_path = os.path.join(output_dir, f"{base_name}.txt")

    logger.info("=" * 60)
    logger.info("Voice Clone Setup")
    logger.info("=" * 60)
    logger.info(f"Audio file: {audio_path}")
    logger.info(f"Text file: {text_path}")
    logger.info(f"Output directory: {output_dir}")
    logger.info("")

    # Load NeuTTS Air model
    logger.info("Loading NeuTTS Air model...")
    logger.info("(This may take a minute on first run)")

    tts = NeuTTSAir(
        backbone_repo="neuphonic/neutts-air-q4-gguf",
        backbone_device="mps",  # Use Apple Silicon
        codec_repo="neuphonic/neucodec",
        codec_device="mps",
    )

    logger.info("✓ Model loaded")

    # Encode reference audio
    logger.info(f"Encoding reference audio: {audio_path}")
    ref_codes = tts.encode_reference(audio_path)
    logger.info("✓ Audio encoded")

    # Save encoded codes
    logger.info(f"Saving encoded codes to: {codes_path}")
    torch.save(ref_codes, codes_path)
    logger.info("✓ Codes saved")

    # Copy text file
    with open(text_path, "r") as f:
        text_content = f.read()

    with open(text_output_path, "w") as f:
        f.write(text_content)

    logger.info(f"✓ Text copied to: {text_output_path}")

    # Summary
    logger.info("")
    logger.info("=" * 60)
    logger.info("Setup Complete!")
    logger.info("=" * 60)
    logger.info("")
    logger.info("Generated files:")
    logger.info(f"  Codes: {codes_path}")
    logger.info(f"  Text:  {text_output_path}")
    logger.info("")
    logger.info("To use this voice in your agent, update .env:")
    logger.info(f"  VOICE_CLONE_CODES={codes_path}")
    logger.info(f"  VOICE_CLONE_TEXT={text_output_path}")
    logger.info("")


def main():
    parser = argparse.ArgumentParser(
        description="Pre-encode reference audio for voice cloning"
    )
    parser.add_argument(
        "audio", help="Path to reference audio file (.wav, 3-15 seconds)"
    )
    parser.add_argument("text", help="Path to text transcript of the audio")
    parser.add_argument(
        "--output-dir",
        default="./voice_clones",
        help="Output directory (default: ./voice_clones)",
    )

    args = parser.parse_args()

    setup_voice_clone(args.audio, args.text, args.output_dir)


if __name__ == "__main__":
    main()
