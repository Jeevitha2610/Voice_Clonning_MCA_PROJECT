"""Comprehensive Command Line Interface for VoiceStudio."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import List, Optional

import numpy as np

from VoiceStudio.config import config
from VoiceStudio.db.connection import DatabaseManager
from VoiceStudio.db.repository import GenerationRepository, VoiceProfileRepository
from VoiceStudio.db.schema import init_schema
from VoiceStudio.dsp.processor import AudioProcessor
from VoiceStudio.dsp.quality import AudioQualityEvaluator
from VoiceStudio.models import SynthesisRequest, VoiceProfile
from VoiceStudio.presets import seed_preset_voices
from VoiceStudio.synthesis.neural_engine import NeuralVoiceEngine


def get_db_and_repos():
    config.ensure_directories()
    db = DatabaseManager(config.db_path)
    with db.get_connection() as conn:
        init_schema(conn)
    profile_repo = VoiceProfileRepository(db)
    seed_preset_voices(profile_repo)
    gen_repo = GenerationRepository(db)
    return db, profile_repo, gen_repo


def cmd_serve(args: argparse.Namespace) -> int:
    """Launch the VoiceStudio FastAPI server and interactive web UI."""
    try:
        import uvicorn
    except ImportError:
        print("[ERROR] uvicorn is not installed. Run: pip install uvicorn")
        return 1

    print("=" * 68)
    print("  VOICESTUDIO - AUTONOMOUS NEURAL SPEECH & CLONING STUDIO")
    print(f"  Interface: http://{args.host}:{args.port}")
    print(f"  Storage:   {config.data_dir}")
    print("=" * 68)
    uvicorn.run("VoiceStudio.api.server:app", host=args.host, port=args.port, reload=args.reload)
    return 0


def cmd_list_voices(args: argparse.Namespace) -> int:
    """Display registered voice profiles."""
    _, profile_repo, _ = get_db_and_repos()
    profiles = profile_repo.list_all()

    if not profiles:
        print("No voice profiles registered yet.")
        return 0

    print("\n" + "=" * 90)
    print(f"{'VOICE ID':<26} | {'NAME':<32} | {'LANG':<5} | {'DEFAULT':<8} | {'TIMBRE EMBEDDING'}")
    print("-" * 90)
    for p in profiles:
        is_def = "YES" if p.is_default else "NO"
        emb_stat = f"{len(p.speaker_embedding)} dims" if p.speaker_embedding else "None"
        print(f"{p.id:<26} | {p.name[:30]:<32} | {p.language:<5} | {is_def:<8} | {emb_stat}")
    print("=" * 90 + "\n")
    return 0


def cmd_clone_voice(args: argparse.Namespace) -> int:
    """Extract speaker embedding from reference audio and create a voice profile."""
    audio_path = Path(args.file).resolve()
    if not audio_path.exists():
        print(f"[ERROR] Audio file not found: {audio_path}")
        return 1

    print(f"[*] Ingesting reference audio: {audio_path}")
    raw_audio, sr = AudioProcessor.load_audio(audio_path, target_sr=config.default_sample_rate)
    metrics = AudioQualityEvaluator.calculate_metrics(raw_audio, sr)
    duration = len(raw_audio) / sr

    print(f"[*] Audio Analysis: Duration={duration:.2f}s, SNR={metrics.snr_db:.1f}dB, Peak={metrics.peak_amplitude:.2f}")
    if metrics.clipping_ratio > 0.01:
        print(f"[WARNING] Detected {metrics.clipping_ratio * 100:.2f}% audio clipping in reference sample.")

    engine = NeuralVoiceEngine(sample_rate=config.default_sample_rate)
    embedding = engine.extract_speaker_embedding(raw_audio, sr)

    _, profile_repo, _ = get_db_and_repos()
    profile = VoiceProfile(
        name=args.name,
        description=args.desc or f"Cloned from {audio_path.name}",
        reference_audio_path=str(audio_path),
        speaker_embedding=embedding,
        language=args.lang,
        is_default=args.default,
        metadata={"cloned_from": audio_path.name, "created_via": "cli"},
    )
    profile_repo.save(profile)
    print(f"[+] Voice profile registered successfully! Profile ID: {profile.id}")
    return 0


def cmd_synthesize(args: argparse.Namespace) -> int:
    """Synthesize speech conditioned on a cloned voice profile or factory preset."""
    text = args.text
    if args.file:
        text_file = Path(args.file).resolve()
        if not text_file.exists():
            print(f"[ERROR] Text file not found: {text_file}")
            return 1
        text = text_file.read_text(encoding="utf-8")

    if not text or not text.strip():
        print("[ERROR] No text provided for speech synthesis.")
        return 1

    _, profile_repo, gen_repo = get_db_and_repos()
    target_profile: Optional[VoiceProfile] = None

    if args.voice_id:
        try:
            target_profile = profile_repo.get_by_id(args.voice_id)
        except Exception as exc:
            print(f"[ERROR] Voice profile not found: {args.voice_id} ({exc})")
            return 1
    else:
        # Pick default preset or first profile
        profiles = profile_repo.list_all()
        target_profile = next((p for p in profiles if p.is_default), profiles[0] if profiles else None)

    voice_name = target_profile.name if target_profile else "Unconditioned"
    print(f"[*] Synthesizing text with voice '{voice_name}'...")
    print(f"[*] Speed: {args.speed}x | Pitch: {args.pitch:+.1f} st | Sample Rate: {config.default_sample_rate}Hz")

    engine = NeuralVoiceEngine(sample_rate=config.default_sample_rate)
    req = SynthesisRequest(
        text=text,
        voice_profile_id=target_profile.id if target_profile else None,
        speed=args.speed,
        pitch=args.pitch,
        normalize_loudness=not args.no_normalize,
        sample_rate=config.default_sample_rate,
    )

    audio, sr = engine.synthesize(req, profile=target_profile)
    out_path = Path(args.out).resolve()
    AudioProcessor.save_wav(out_path, audio, sr)

    metrics = AudioQualityEvaluator.calculate_metrics(audio, sr)
    duration = len(audio) / sr
    print(f"[+] Audio generated successfully: {out_path}")
    print(f"    Duration: {duration:.2f}s | SNR: {metrics.snr_db:.1f}dB | Loudness: {metrics.integrated_lufs:.1f} LUFS")
    return 0


def cmd_assess(args: argparse.Namespace) -> int:
    """Evaluate and print acoustic quality metrics for an audio file."""
    audio_path = Path(args.file).resolve()
    if not audio_path.exists():
        print(f"[ERROR] Audio file not found: {audio_path}")
        return 1

    audio, sr = AudioProcessor.load_audio(audio_path)
    metrics = AudioQualityEvaluator.calculate_metrics(audio, sr)
    duration = len(audio) / sr

    print("\n" + "=" * 50)
    print(f" ACOUSTIC QUALITY AUDIT: {audio_path.name}")
    print("=" * 50)
    print(f"  Duration:         {duration:.2f} seconds")
    print(f"  Sample Rate:      {sr} Hz")
    print(f"  SNR (Signal/Noise): {metrics.snr_db:.2f} dB")
    print(f"  RMS Level:        {metrics.rms_energy:.4f}")
    print(f"  Peak Amplitude:   {metrics.peak_amplitude:.4f}")
    print(f"  Clipping Ratio:   {metrics.clipping_ratio * 100:.3f} %")
    print(f"  EBU R128 Loudness: {metrics.integrated_lufs:.2f} LUFS")
    print(f"  Studio Clean:     {'YES' if metrics.is_clean else 'NO'}")
    print("=" * 50 + "\n")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="voicestudio",
        description="VoiceStudio: High-performance local neural speech synthesis and voice cloning studio.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: serve
    serve_p = subparsers.add_parser("serve", help="Launch FastAPI server and studio web interface")
    serve_p.add_argument("--host", default="127.0.0.1", help="Host address to bind (default: 127.0.0.1)")
    serve_p.add_argument("--port", type=int, default=8000, help="Port to listen on (default: 8000)")
    serve_p.add_argument("--reload", action="store_true", help="Enable auto-reload on code modifications")

    # Subcommand: list-voices
    subparsers.add_parser("list-voices", help="List registered voice profiles and factory presets")

    # Subcommand: clone-voice
    clone_p = subparsers.add_parser("clone-voice", help="Clone voice timbre from reference audio")
    clone_p.add_argument("--name", required=True, help="Human-readable voice label")
    clone_p.add_argument("--file", required=True, help="Path to reference audio file (.wav, .mp3)")
    clone_p.add_argument("--desc", default="", help="Description or tags")
    clone_p.add_argument("--lang", default="en", help="Language code (default: en)")
    clone_p.add_argument("--default", action="store_true", help="Mark as default profile")

    # Subcommand: synthesize
    synth_p = subparsers.add_parser("synthesize", help="Synthesize speech from text")
    synth_p.add_argument("--text", default="", help="Text to speak")
    synth_p.add_argument("--file", default="", help="Path to input text file")
    synth_p.add_argument("--voice-id", default=None, help="Target voice profile ID")
    synth_p.add_argument("--out", default="output.wav", help="Path to output WAV file (default: output.wav)")
    synth_p.add_argument("--speed", type=float, default=1.0, help="Speech speed factor 0.5 - 2.0")
    synth_p.add_argument("--pitch", type=float, default=0.0, help="Pitch shift in semitones (-12 to +12)")
    synth_p.add_argument("--no-normalize", action="store_true", help="Disable EBU R128 loudness normalization")

    # Subcommand: assess
    assess_p = subparsers.add_parser("assess", help="Assess audio quality, SNR, and loudness")
    assess_p.add_argument("--file", required=True, help="Path to audio file to evaluate")

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    handlers = {
        "serve": cmd_serve,
        "list-voices": cmd_list_voices,
        "clone-voice": cmd_clone_voice,
        "synthesize": cmd_synthesize,
        "assess": cmd_assess,
    }

    handler = handlers.get(args.command)
    if not handler:
        parser.print_help()
        return 1

    return handler(args)


if __name__ == "__main__":
    sys.exit(main())
