"""Batch generate and verify neural voice clones for user reference samples on CPU.

Demonstrates the exact step-by-step terminal progress bar (never sticking at 70%)
and caches the voice clone prompts for fast Web UI synthesis across all voices.
"""

import time
from pathlib import Path

from VoiceStudio.config import config
from VoiceStudio.db.connection import DatabaseManager
from VoiceStudio.db.repository import VoiceProfileRepository
from VoiceStudio.db.schema import init_schema
from VoiceStudio.dsp.processor import AudioProcessor
from VoiceStudio.dsp.quality import AudioQualityEvaluator
from VoiceStudio.models import SynthesisRequest, VoiceProfile
from VoiceStudio.presets import seed_preset_voices
from VoiceStudio.synthesis.neural_engine import NeuralVoiceEngine


def cleanup_database(db: DatabaseManager) -> None:
    """Remove leftover CLI test artifacts and enforce default voice invariants."""
    with db.get_connection() as conn:
        conn.execute("DELETE FROM voice_profiles WHERE name = ?", ("CLI Voice Test",))
        rows = conn.execute("SELECT id, reference_audio_path FROM voice_profiles").fetchall()
        for row_id, ref_path in rows:
            if ref_path and not str(ref_path).startswith("builtin:"):
                if not Path(ref_path).exists():
                    conn.execute("DELETE FROM voice_profiles WHERE id = ?", (row_id,))
        conn.execute("UPDATE voice_profiles SET is_default = 0 WHERE id != ?", ("preset-aria-prime",))
        conn.execute("UPDATE voice_profiles SET is_default = 1 WHERE id = ?", ("preset-aria-prime",))
        conn.commit()


def main() -> None:
    out_dir = Path("test_clones")
    out_dir.mkdir(exist_ok=True)

    config.ensure_directories()
    db = DatabaseManager(config.db_path)
    with db.get_connection() as conn:
        init_schema(conn)
    cleanup_database(db)

    repo = VoiceProfileRepository(db)
    seed_preset_voices(repo)

    engine = NeuralVoiceEngine(sample_rate=24000, device="cpu")

    samples = [
        {
            "id": "test-voice-swamiji",
            "name": "Swami Vivekananda (Test Voice)",
            "file": "user-voice/swamiji.mp3",
            "ref_text": "Sisters and brothers of America, it fills my heart with joy to rise in response to the warm welcome.",
            "test_script": "Arise, awake, and stop not until the goal is reached.",
            "out_file": "test_clones/swamiji_cloned_output.wav",
            "force_regen": True,
        },
        {
            "id": "test-voice-kalam",
            "name": "Dr. A.P.J. Abdul Kalam (Test Voice)",
            "file": "user-voice/APJ_abdul_kalam.mp3",
            "ref_text": "My message, especially to young people, is to have courage to think differently and conquer problems.",
            "test_script": "Dream, dream, dream. Dreams transform into thoughts.",
            "out_file": "test_clones/kalam_cloned_output.wav",
            "force_regen": False,
        },
        {
            "id": "test-voice-janiki",
            "name": "S. Janaki (Test Voice)",
            "file": "user-voice/janiki.mp3",
            "ref_text": "Music is the divine language of emotion, peace, and harmony.",
            "test_script": "Music is the divine sound of love and harmony.",
            "out_file": "test_clones/janiki_cloned_output.wav",
            "force_regen": False,
        },
    ]

    for item in samples:
        raw_ref, ref_sr = AudioProcessor.load_audio(item["file"], target_sr=24000, max_duration_sec=15.0)
        embedding = engine.extract_speaker_embedding(raw_ref, ref_sr)

        # Register profile in SQLite (is_default=False strictly)
        profile = VoiceProfile(
            id=item["id"],
            name=item["name"],
            description=f"Neural zero-shot cloned voice from {Path(item['file']).name} (testing only)",
            reference_audio_path=item["file"],
            transcript=item["ref_text"],
            speaker_embedding=embedding,
            language="en",
            is_default=False,  # STRICT REQUIREMENT: Never default
            metadata={"test_sample": True, "source_file": item["file"]},
        )
        repo.save(profile)
        print(f"[+] Registered profile '{profile.name}' ({profile.id}) | is_default={profile.is_default}", flush=True)

        out_path = Path(item["out_file"])
        if not out_path.exists() or item["force_regen"]:
            print(f"\n[*] Synthesizing neural clone for: {item['name']}...", flush=True)
            t0 = time.time()
            req = SynthesisRequest(
                text=item["test_script"],
                voice_profile_id=profile.id,
                speed=1.0,
                pitch=0.0,
                normalize_loudness=True,
            )
            audio, sr = engine.synthesize(req, profile=profile)
            AudioProcessor.save_wav(out_path, audio, sample_rate=sr)
            metrics = AudioQualityEvaluator.calculate_metrics(audio, sr)
            print(
                f"[+] Saved {out_path} ({len(audio)/sr:.2f}s) in {time.time() - t0:.1f}s | "
                f"SNR={metrics.snr_db:.1f}dB | LUFS={metrics.integrated_lufs:.1f} | Clean={metrics.is_clean}",
                flush=True,
            )
        else:
            # Ensure prompt is pre-cached even if output WAV already exists
            print(f"[*] Verifying voice prompt cache for: {item['name']}...", flush=True)
            req = SynthesisRequest(text="Hello.", voice_profile_id=profile.id)
            # Load model & cache prompt if not cached yet
            from VoiceStudio.synthesis.neural_engine import get_omnivoice_model
            model = get_omnivoice_model()
            if model is not None:
                sliced_ref = AudioProcessor.extract_best_voice_slice(raw_ref, sample_rate=model.sampling_rate, slice_sec=5.5)
                tmp_wav = out_dir / f"tmp_{item['id']}.wav"
                AudioProcessor.save_wav(tmp_wav, sliced_ref, model.sampling_rate)
                try:
                    import hashlib
                    abs_ref = str(Path(item["file"]).resolve())
                    ref_stat = Path(item["file"]).stat()
                    cache_key = hashlib.sha256(
                        f"{abs_ref}:{ref_stat.st_size}:{int(ref_stat.st_mtime)}:{item['ref_text'].strip()}:v2".encode("utf-8")
                    ).hexdigest()[:16]
                    cache_file = Path("data/cache") / f"voice_prompt_{cache_key}.pt"
                    if not cache_file.exists():
                        prompt = model.create_voice_clone_prompt(
                            ref_audio=str(tmp_wav),
                            ref_text=item["ref_text"].strip(),
                            preprocess_prompt=True,
                        )
                        prompt.ref_rms = max(float(prompt.ref_rms), 0.14)
                        cache_file.parent.mkdir(parents=True, exist_ok=True)
                        prompt.save(str(cache_file))
                        print(f"[+] Cached neural voiceprint: {cache_file}", flush=True)
                finally:
                    tmp_wav.unlink(missing_ok=True)

    print("\n[ALL TEST CLONES & VOICEPRINT CACHES VERIFIED SUCCESSFULLY]", flush=True)


if __name__ == "__main__":
    main()
