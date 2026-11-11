"""Audio signal processing pipeline for resampling, channel downmixing, and WAV I/O."""

import math
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import scipy.signal
import soundfile as sf

from VoiceStudio.exceptions import AudioProcessingError


class AudioProcessor:
    """Handles audio loading, conversion, channel downmixing, and sample rate conversion."""

    @staticmethod
    def load_audio(
        file_path: Path | str,
        target_sr: int = 24000,
        max_duration_sec: Optional[float] = None,
    ) -> Tuple[np.ndarray, int]:
        """Read an audio file from disk, convert to mono float32, and resample to target_sr."""
        path = Path(file_path)
        if not path.exists():
            raise AudioProcessingError(f"Audio file does not exist: {file_path}")

        try:
            frames = -1
            if max_duration_sec is not None and max_duration_sec > 0:
                info = sf.info(str(path))
                frames = int(max_duration_sec * info.samplerate)
            data, sr = sf.read(str(path), frames=frames, dtype="float32")
        except Exception as exc:
            raise AudioProcessingError(f"Failed to decode audio file {file_path}: {exc}") from exc

        # Convert to mono if multichannel
        if data.ndim > 1:
            data = np.mean(data, axis=1)

        # Resample if sample rate doesn't match
        if sr != target_sr:
            data = AudioProcessor.resample(data, sr, target_sr)
            sr = target_sr

        # Ensure float32 in [-1.0, 1.0] range
        max_val = np.max(np.abs(data)) if len(data) > 0 else 0.0
        if max_val > 1.0:
            data = data / max_val

        return data.astype(np.float32), sr

    @staticmethod
    def extract_best_voice_slice(
        audio: np.ndarray,
        sample_rate: int = 24000,
        slice_sec: float = 5.5,
    ) -> np.ndarray:
        """Select the highest-energy speech window and normalize its level for voice cloning."""
        if len(audio) == 0:
            return audio

        target_len = int(slice_sec * sample_rate)
        if len(audio) <= target_len:
            best_slice = audio.copy()
        else:
            hop = max(1, int(0.5 * sample_rate))
            best_rms = -1.0
            best_start = 0
            max_search = min(len(audio) - target_len, int(25.0 * sample_rate))
            for start in range(0, max_search + 1, hop):
                window = audio[start : start + target_len]
                rms = float(np.sqrt(np.mean(window**2)))
                if rms > best_rms:
                    best_rms = rms
                    best_start = start
            best_slice = audio[best_start : best_start + target_len].copy()

        # Normalize RMS to ~0.15 with peak ceiling at 0.92 so quiet references clone loudly
        rms = float(np.sqrt(np.mean(best_slice**2)))
        if rms > 1e-5:
            best_slice = best_slice * (0.15 / rms)
        peak = float(np.max(np.abs(best_slice)))
        if peak > 0.92:
            best_slice = best_slice * (0.92 / peak)

        return best_slice.astype(np.float32)

    @staticmethod
    def resample(audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
        """High-precision sample rate conversion using polyphase filtering."""
        if orig_sr == target_sr or len(audio) == 0:
            return audio

        try:
            gcd = math.gcd(int(orig_sr), int(target_sr))
            up = int(target_sr) // gcd
            down = int(orig_sr) // gcd
            if up <= 1000 and down <= 1000:
                resampled = scipy.signal.resample_poly(audio, up, down)
            else:
                num_target_samples = int(round(len(audio) * float(target_sr) / orig_sr))
                resampled = scipy.signal.resample(audio, num_target_samples)
            return resampled.astype(np.float32)
        except Exception as exc:
            raise AudioProcessingError(f"Resampling from {orig_sr}Hz to {target_sr}Hz failed: {exc}") from exc

    @staticmethod
    def save_wav(file_path: Path | str, audio: np.ndarray, sample_rate: int = 24000) -> Path:
        """Write a 1D float32 audio array to a standard PCM 16-bit or 32-bit float WAV."""
        out_path = Path(file_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        # Clamp to [-1.0, 1.0] to prevent integer wrap-around distortion
        clipped = np.clip(audio, -1.0, 1.0)
        try:
            sf.write(str(out_path), clipped, sample_rate, subtype="PCM_16")
            return out_path
        except Exception as exc:
            raise AudioProcessingError(f"Failed to write WAV file to {file_path}: {exc}") from exc
