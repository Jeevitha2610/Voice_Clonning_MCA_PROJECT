"""Unit tests for VoiceStudio domain models and exception hierarchy."""

import pytest
from pydantic import ValidationError

from VoiceStudio.exceptions import (
    AudioProcessingError,
    DatabaseError,
    ModelUnavailableError,
    StorageSecurityError,
    SynthesisError,
    VoiceProfileNotFoundError,
    VoiceStudioError,
)
from VoiceStudio.models import (
    AudioQualityMetrics,
    AudioSegment,
    GenerationRecord,
    SynthesisRequest,
    VoiceProfile,
)


def test_exception_hierarchy():
    """Verify that all domain exceptions derive from VoiceStudioError."""
    assert issubclass(StorageSecurityError, VoiceStudioError)
    assert issubclass(AudioProcessingError, VoiceStudioError)
    assert issubclass(VoiceProfileNotFoundError, VoiceStudioError)
    assert issubclass(SynthesisError, VoiceStudioError)
    assert issubclass(DatabaseError, VoiceStudioError)
    assert issubclass(ModelUnavailableError, VoiceStudioError)

    err = AudioProcessingError("Resampling failed", details={"rate": -1})
    assert str(err) == "Resampling failed"
    assert err.details["rate"] == -1


def test_audio_quality_metrics_model():
    """Test valid instantiation and defaults of AudioQualityMetrics."""
    metrics = AudioQualityMetrics(
        snr_db=28.5,
        peak_amplitude=0.92,
        rms_energy=0.15,
        clipping_ratio=0.0,
        integrated_lufs=-18.2,
        is_clean=True,
    )
    assert metrics.snr_db == 28.5
    assert metrics.is_clean is True
    assert metrics.clipping_ratio == 0.0


def test_voice_profile_creation():
    """Test creating a valid VoiceProfile with embeddings and metadata."""
    profile = VoiceProfile(
        name="Alex - Studio Narrator",
        description="Neutral, warm narration tone",
        reference_audio_path="/data/audio/alex_ref.wav",
        speaker_embedding=[0.12, -0.05, 0.88],
        language="en",
    )
    assert profile.name == "Alex - Studio Narrator"
    assert len(profile.speaker_embedding) == 3
    assert profile.id is not None
    assert profile.created_at is not None


def test_synthesis_request_validation():
    """Test synthesis request input boundaries and validation rules."""
    req = SynthesisRequest(
        text="Welcome to VoiceStudio autonomous speech engine.",
        speed=1.25,
        pitch=2.0,
        normalize_loudness=True,
    )
    assert req.speed == 1.25
    assert req.pitch == 2.0
    assert req.normalize_loudness is True

    # Empty text must raise validation error
    with pytest.raises(ValidationError):
        SynthesisRequest(text="   ")

    # Invalid speed factor (< 0.5 or > 2.0) must fail
    with pytest.raises(ValidationError):
        SynthesisRequest(text="Hello", speed=3.5)


def test_generation_record_serialization():
    """Test serialization of completed synthesis generation record."""
    rec = GenerationRecord(
        input_text="Testing audio output",
        output_audio_path="/data/outputs/gen_1.wav",
        duration_sec=3.4,
        latency_ms=185.0,
    )
    dumped = rec.model_dump()
    assert dumped["duration_sec"] == 3.4
    assert dumped["latency_ms"] == 185.0
    assert "created_at" in dumped
