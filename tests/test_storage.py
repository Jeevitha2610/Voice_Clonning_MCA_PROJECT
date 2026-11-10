"""Unit tests for secure media storage and anti-path-traversal guards."""

from pathlib import Path
import pytest

from VoiceStudio.exceptions import StorageSecurityError
from VoiceStudio.storage.media import StorageService


@pytest.fixture
def storage(tmp_path: Path) -> StorageService:
    """Fixture providing an isolated StorageService."""
    base = tmp_path / "app_data"
    uploads = base / "uploads"
    outputs = base / "outputs"
    return StorageService(base_dir=base, uploads_dir=uploads, outputs_dir=outputs)


def test_save_valid_upload(storage: StorageService):
    """Test saving a legitimate audio upload within size limits."""
    content = b"RIFF....WAVEfmt ...."
    saved_path = storage.save_upload(content, "recording.wav")
    assert saved_path.exists()
    assert saved_path.suffix == ".wav"
    assert saved_path.read_bytes() == content


def test_reject_oversized_upload(storage: StorageService):
    """Test rejection of payload exceeding configured maximum size."""
    storage.max_size_bytes = 100
    huge_data = b"0" * 101
    with pytest.raises(StorageSecurityError, match="exceeds maximum permitted limit"):
        storage.save_upload(huge_data, "large.wav")


def test_reject_unsupported_extension(storage: StorageService):
    """Test rejection of non-audio or unauthorized file types."""
    with pytest.raises(StorageSecurityError, match="Unsupported audio extension"):
        storage.save_upload(b"payload", "exploit.exe")


def test_path_traversal_defense(storage: StorageService):
    """Test rejection of attempts to access outside the storage root."""
    evil_path = Path("/etc/passwd") if Path("/").exists() else Path("C:/Windows/System32/cmd.exe")
    with pytest.raises(StorageSecurityError, match="escapes authorized directory"):
        storage.validate_path(evil_path)


def test_allocate_output_path(storage: StorageService):
    """Test generating a safe destination path for audio synthesis output."""
    out_path = storage.allocate_output_path(prefix="speech", extension=".wav")
    assert out_path.parent == storage.outputs_dir
    assert out_path.name.startswith("speech_")
    assert out_path.suffix == ".wav"
