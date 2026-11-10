"""Unit tests for AudioProcessor and AudioQualityEvaluator."""

from pathlib import Path
import numpy as np
import pytest

from VoiceStudio.dsp.processor import AudioProcessor
from VoiceStudio.dsp.quality import AudioQualityEvaluator


@pytest.fixture
def sample_sine_wave() -> np.ndarray:
    """Generate 1 second of 440Hz sine wave at 24000Hz sampling rate."""
    sr = 24000
    t = np.linspace(0, 1.0, sr, endpoint=False)
    # Amplitude 0.5
    return (0.5 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)


def test_wav_save_and_load(tmp_path: Path, sample_sine_wave: np.ndarray):
    """Test saving a waveform to WAV and reloading with resampling."""
    wav_path = tmp_path / "test_tone.wav"
    AudioProcessor.save_wav(wav_path, sample_sine_wave, sample_rate=24000)
    assert wav_path.exists()

    loaded_audio, loaded_sr = AudioProcessor.load_audio(wav_path, target_sr=16000)
    assert loaded_sr == 16000
    assert len(loaded_audio) == 16000
    assert np.max(np.abs(loaded_audio)) > 0.45


def test_quality_metrics_calculation(sample_sine_wave: np.ndarray):
    """Test SNR, peak amplitude, and RMS energy calculation."""
    metrics = AudioQualityEvaluator.calculate_metrics(sample_sine_wave, sample_rate=24000)
    assert 0.49 <= metrics.peak_amplitude <= 0.51
    assert 0.34 <= metrics.rms_energy <= 0.36
    assert metrics.clipping_ratio == 0.0
    assert metrics.is_clean is True


def test_clipping_detection():
    """Test accurate detection of heavily clipped samples."""
    clipped_audio = np.ones(1000, dtype=np.float32)
    metrics = AudioQualityEvaluator.calculate_metrics(clipped_audio, sample_rate=24000)
    assert metrics.clipping_ratio == 1.0
    assert metrics.is_clean is False


def test_loudness_normalization(sample_sine_wave: np.ndarray):
    """Test normalizing audio to a specific LUFS target."""
    target_lufs = -18.0
    normalized = AudioQualityEvaluator.normalize_loudness(
        sample_sine_wave, sample_rate=24000, target_lufs=target_lufs
    )
    metrics = AudioQualityEvaluator.calculate_metrics(normalized, sample_rate=24000)
    # Check that loudness increased towards target without clipping
    assert metrics.integrated_lufs > -22.0
    assert metrics.peak_amplitude <= 0.99
