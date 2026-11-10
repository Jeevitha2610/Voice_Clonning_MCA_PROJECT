"""Unified exception hierarchy for VoiceStudio."""

from typing import Optional


class VoiceStudioError(Exception):
    """Base exception for all VoiceStudio domain errors."""

    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class StorageSecurityError(VoiceStudioError):
    """Raised when an audio file path violates security boundaries or traversal guards."""
    pass


class AudioProcessingError(VoiceStudioError):
    """Raised when audio conversion, decoding, resampling, or normalization fails."""
    pass


class VoiceProfileNotFoundError(VoiceStudioError):
    """Raised when a requested voice profile ID cannot be located in storage."""
    pass


class SynthesisError(VoiceStudioError):
    """Raised when neural speech synthesis or voice cloning fails."""
    pass


class DatabaseError(VoiceStudioError):
    """Raised when SQLite database operations fail."""
    pass


class ModelUnavailableError(VoiceStudioError):
    """Raised when a requested neural TTS model checkpoint is unavailable or cannot run."""
    pass
