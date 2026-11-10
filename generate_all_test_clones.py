"""Batch generate neural voice clones for the user reference samples on CPU."""

import time
from pathlib import Path
import soundfile as sf
import numpy as np
import torch
from omnivoice import OmniVoice

from VoiceStudio.config import config
from VoiceStudio.db.connection import DatabaseManager
from VoiceStudio.db.repository import VoiceProfileRepository
from VoiceStudio.db.schema import init_schema
from VoiceStudio.dsp.processor import AudioProcessor
from VoiceStudio.models import VoiceProfile

def main():
    print("[*] Loading cached OmniVoice neural cloner on CPU...", flush=True)
    t0 = time.time()
    model = OmniVoice.from_pretrained("k2-fsa/OmniVoice")
    print(f"[+] Model loaded in {time.time() - t0:.2f}s! Device: {model.device}", flush=True)

    out_dir = Path("test_clones")
    out_dir.mkdir(exist_ok=True)

    # 1. Database setup
    config.ensure_directories()
    db = DatabaseManager(config.db_path)
    with db.get_connection() as conn:
        init_schema(conn)
    repo = VoiceProfileRepository(db)

    samples = [
        {
            "id": "test-voice-kalam",
            "name": "Dr. A.P.J. Abdul Kalam (Test Voice)",
            "file": "user-voice/APJ_abdul_kalam.mp3",
            "ref_text": "My message, especially to young people is to have courage to think differently and to conquer the problems.",
            "test_script": "Dream, dream, dream. Dreams transform into thoughts.",
            "out_file": "test_clones/kalam_cloned_output.wav",
            "slice_sec": 8.0,
        },
        {
            "id": "test-voice-janiki",
            "name": "S. Janaki (Test Voice)",
            "file": "user-voice/janiki.mp3",
            "ref_text": "Music is the language of emotion and peace.",
            "test_script": "Music is the divine sound of love and harmony.",
            "out_file": "test_clones/janiki_cloned_output.wav",
            "slice_sec": 8.0,
        },
        {
            "id": "test-voice-swamiji",
            "name": "Swami Vivekananda (Test Voice)",
            "file": "user-voice/swamiji.mp3",
            "ref_text": "Sisters and brothers of America, it fills my heart with joy unspeakable to rise in response to the warm welcome.",
            "test_script": "Arise, awake, and stop not until the goal is reached.",
            "out_file": "test_clones/swamiji_cloned_output.wav",
            "slice_sec": 8.0,
        },
    ]

    for item in samples:
        out_path = Path(item["out_file"])
        if out_path.exists():
            print(f"[+] Output already exists for {item['name']}: {out_path}", flush=True)
        else:
            print(f"\n[*] Processing clone: {item['name']} from {item['file']}...", flush=True)
            # Load and slice 8-10 seconds of reference audio
            raw_audio, sr = AudioProcessor.load_audio(item["file"], target_sr=model.sampling_rate)
            max_samples = int(item["slice_sec"] * model.sampling_rate)
            sliced_audio = raw_audio[:max_samples]

            # Save temporary slice WAV for OmniVoice
            tmp_slice = out_dir / f"tmp_slice_{item['id']}.wav"
            AudioProcessor.save_wav(tmp_slice, sliced_audio, model.sampling_rate)

            # Create voice clone prompt
            t_prompt = time.time()
            prompt = model.create_voice_clone_prompt(
                ref_audio=str(tmp_slice),
                ref_text=item["ref_text"],
                preprocess_prompt=True,
            )
            print(f"[+] Prompt created in {time.time() - t_prompt:.2f}s!", flush=True)
            tmp_slice.unlink(missing_ok=True)

            # Synthesize in cloned voice
            print(f"[*] Synthesizing script: '{item['test_script']}'...", flush=True)
            t_gen = time.time()
            outputs = model.generate(
                text=item["test_script"],
                voice_clone_prompt=prompt,
                speed=1.0,
            )
            audio = outputs[0]
            print(f"[+] Generated in {time.time() - t_gen:.2f}s!", flush=True)

            # Save final WAV
            sf.write(str(out_path), audio, model.sampling_rate)
            print(f"[+] Saved cloned output: {out_path} ({len(audio)/model.sampling_rate:.2f}s)", flush=True)

        # Register profile in SQLite (is_default=False strictly)
        profile = VoiceProfile(
            id=item["id"],
            name=item["name"],
            description=f"Neural zero-shot cloned voice from {Path(item['file']).name} (testing only)",
            reference_audio_path=item["file"],
            transcript=item["ref_text"],
            language="en",
            is_default=False, # STRICT REQUIREMENT: Never default
            metadata={"test_sample": True, "source_file": item["file"]},
        )
        repo.save(profile)
        print(f"[+] Registered profile {profile.id} in database (is_default={profile.is_default})", flush=True)

    print("\n[ALL TEST CLONES COMPLETED SUCCESSFULLY]")

if __name__ == "__main__":
    main()
