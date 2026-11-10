"""Unit tests for neural speech synthesis, voice embedding extraction, and streaming."""

import numpy as np
import pytest

from VoiceStudio.models import SynthesisRequest, VoiceProfile
from VoiceStudio.synthesis.neural_engine import NeuralVoiceEngine
from VoiceStudio.synthesis.registry import EngineRegistry


@pytest.fixture
def neural_engine() -> NeuralVoiceEngine:
    return NeuralVoiceEngine(sample_rate=24000, device="cpu")


def test_engine_availability(neural_engine: NeuralVoiceEngine):
    """Verify PyTorch CPU availability and engine properties."""
    is_avail, reason = neural_engine.is_available()
    assert is_avail is True
    assert "PyTorch" in reason
    assert neural_engine.engine_name == "pytorch_neural_cpu"
    assert neural_engine.sample_rate == 24000


def test_extract_speaker_embedding(neural_engine: NeuralVoiceEngine):
    """Verify extracting 128-dimensional acoustic timbre vector from audio."""
    # Generate 1s test signal
    sr = 24000
    t = np.linspace(0, 1.0, sr, endpoint=False)
    signal = (0.4 * np.sin(2 * np.pi * 200 * t)).astype(np.float32)

    embedding = neural_engine.extract_speaker_embedding(signal, sr)
    assert len(embedding) == 128
    assert all(isinstance(x, float) for x in embedding)
    # Check that norm is non-zero
    norm = np.linalg.norm(embedding)
    assert 0.95 <= norm <= 1.05


def test_speech_synthesis(neural_engine: NeuralVoiceEngine):
    """Test text-to-speech synthesis with conditioning."""
    profile = VoiceProfile(
        name="Cloned Narrator",
        reference_audio_path="/tmp/ref.wav",
        speaker_embedding=[0.05] * 128,
    )
    req = SynthesisRequest(
        text="Hello and welcome to VoiceStudio.",
        speed=1.0,
        pitch=0.0,
        normalize_loudness=True,
    )
    audio, sr = neural_engine.synthesize(req, profile=profile)
    assert sr == 24000
    assert len(audio) > 0
    assert isinstance(audio, np.ndarray)
    assert np.max(np.abs(audio)) <= 1.0


def test_speech_streaming_chunks(neural_engine: NeuralVoiceEngine):
    """Verify real-time streaming chunks for Server-Sent Events."""
    req = SynthesisRequest(text="One two three four five.")
    chunks = list(neural_engine.synthesize_stream(req, chunk_size_samples=2400))
    assert len(chunks) > 0
    for chunk in chunks:
        assert isinstance(chunk, np.ndarray)
        assert len(chunk) <= 2400


def test_engine_registry():
    """Verify dynamic backend discovery and default routing."""
    registry = EngineRegistry()
    engines = registry.list_engines()
    assert len(engines) >= 1
    assert any(e["engine_name"] == "pytorch_neural_cpu" for e in engines)

    engine = registry.get_engine()
    assert engine.engine_name == "pytorch_neural_cpu"
