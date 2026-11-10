"""Core domain models and typed data contracts for VoiceStudio."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid

from pydantic import BaseModel, Field, field_validator


class AudioQualityMetrics(BaseModel):
    """Objective audio quality and signal evaluation metrics."""
    snr_db: float = Field(..., description="Signal-to-Noise Ratio in decibels")
    peak_amplitude: float = Field(..., description="Peak normalized amplitude (0.0 to 1.0)")
    rms_energy: float = Field(..., description="Root-Mean-Square energy level")
    clipping_ratio: float = Field(default=0.0, description="Percentage of clipped samples")
    integrated_lufs: float = Field(default=-23.0, description="EBU R128 integrated loudness in LUFS")
    is_clean: bool = Field(default=True, description="Whether signal passes studio quality thresholds")


class AudioSegment(BaseModel):
    """Metadata representing an audio slice or recorded waveform file."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    file_path: str = Field(..., description="Absolute or relative path to the audio file on disk")
    sample_rate: int = Field(default=24000, description="Sampling rate in Hz (e.g. 16000, 22050, 24000)")
    channels: int = Field(default=1, description="Number of audio channels (1=mono, 2=stereo)")
    duration_sec: float = Field(..., description="Total audio length in seconds")
    format: str = Field(default="wav", description="Audio container format")
    quality_metrics: Optional[AudioQualityMetrics] = Field(default=None)


class VoiceProfile(BaseModel):
    """Conditioned voice profile extracted from authorized reference audio."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., min_length=1, max_length=120, description="Human-readable voice label")
    description: Optional[str] = Field(default="", description="Optional description or tags")
    reference_audio_path: str = Field(..., description="Path to the source reference audio file")
    transcript: Optional[str] = Field(default=None, description="Reference audio transcript if known")
    speaker_embedding: Optional[List[float]] = Field(default=None, description="Acoustic speaker embedding vector")
    language: str = Field(default="en", description="Primary language code (e.g. 'en', 'es', 'de')")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_default: bool = Field(default=False, description="Whether this is the default studio profile")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SynthesisRequest(BaseModel):
    """Specification for text-to-speech synthesis or voice cloning generation."""
    text: str = Field(..., min_length=1, description="Input text to synthesize")
    voice_profile_id: Optional[str] = Field(default=None, description="Target voice profile ID")
    reference_audio_path: Optional[str] = Field(default=None, description="Direct reference audio for zero-shot cloning")
    speed: float = Field(default=1.0, ge=0.5, le=2.0, description="Playback speed factor (0.5x to 2.0x)")
    pitch: float = Field(default=0.0, ge=-12.0, le=12.0, description="Pitch shift in semitones (-12 to +12)")
    language: str = Field(default="en", description="Output speech language code")
    sample_rate: int = Field(default=24000, description="Desired output sample rate")
    normalize_loudness: bool = Field(default=True, description="Apply EBU R128 loudness normalization")

    @field_validator("text")
    @classmethod
    def validate_non_empty_text(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Input text cannot be blank or whitespace-only")
        return trimmed


class GenerationRecord(BaseModel):
    """Audit and playback record for a completed speech synthesis event."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    voice_profile_id: Optional[str] = Field(default=None)
    voice_name: Optional[str] = Field(default="Default")
    input_text: str = Field(...)
    output_audio_path: str = Field(...)
    duration_sec: float = Field(...)
    latency_ms: float = Field(..., description="Inference latency in milliseconds")
    sample_rate: int = Field(default=24000)
    quality_metrics: Optional[AudioQualityMetrics] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
