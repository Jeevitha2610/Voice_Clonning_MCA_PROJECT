"""Audio signal processing pipeline for resampling, channel downmixing, and WAV I/O."""

from pathlib import Path
from typing import Tuple

import numpy as np
import scipy.signal
import soundfile as sf

from VoiceStudio.exceptions import AudioProcessingError


class AudioProcessor:
    """Handles audio loading, conversion, channel downmixing, and sample rate conversion."""

    @staticmethod
    def load_audio(file_path: Path | str, target_sr: int = 24000) -> Tuple[np.ndarray, int]:
        """Read an audio file from disk, convert to mono float32, and resample to target_sr."""
        path = Path(file_path)
        if not path.exists():
            raise AudioProcessingError(f"Audio file does not exist: {file_path}")

        try:
            data, sr = sf.read(str(path), dtype="float32")
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
    def resample(audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
        """High-precision sample rate conversion using polyphase or FFT resampling."""
        if orig_sr == target_sr or len(audio) == 0:
            return audio

        num_target_samples = int(round(len(audio) * float(target_sr) / orig_sr))
        try:
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
