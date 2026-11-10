"""Unit tests for SQLite WAL connection and repository operations."""

from pathlib import Path
import pytest

from VoiceStudio.db.connection import DatabaseManager
from VoiceStudio.db.repository import GenerationRepository, VoiceProfileRepository
from VoiceStudio.db.schema import init_schema
from VoiceStudio.exceptions import VoiceProfileNotFoundError
from VoiceStudio.models import AudioQualityMetrics, GenerationRecord, VoiceProfile


@pytest.fixture
def test_db(tmp_path: Path) -> DatabaseManager:
    """Fixture providing an initialized SQLite database in a temporary directory."""
    db_file = tmp_path / "test_voicestudio.db"
    manager = DatabaseManager(db_file)
    with manager.get_connection() as conn:
        init_schema(conn)
    return manager


def test_voice_profile_crud(test_db: DatabaseManager):
    """Verify create, read, list, and delete operations on VoiceProfileRepository."""
    repo = VoiceProfileRepository(test_db)

    profile = VoiceProfile(
        name="Elena - Warm Voice",
        description="Warm corporate narration profile",
        reference_audio_path="/uploads/elena_sample.wav",
        speaker_embedding=[0.01, -0.42, 0.77],
        language="en",
        is_default=True,
    )
    saved = repo.save(profile)
    assert saved.id == profile.id

    fetched = repo.get_by_id(profile.id)
    assert fetched.name == "Elena - Warm Voice"
    assert fetched.speaker_embedding == [0.01, -0.42, 0.77]
    assert fetched.is_default is True

    all_profiles = repo.list_all()
    assert len(all_profiles) == 1

    deleted = repo.delete(profile.id)
    assert deleted is True

    with pytest.raises(VoiceProfileNotFoundError):
        repo.get_by_id(profile.id)


def test_generation_record_persistence(test_db: DatabaseManager):
    """Verify persisting and querying audio generation records."""
    repo = GenerationRepository(test_db)

    metrics = AudioQualityMetrics(
        snr_db=32.4,
        peak_amplitude=0.88,
        rms_energy=0.12,
        clipping_ratio=0.0,
        integrated_lufs=-22.8,
        is_clean=True,
    )
    rec = GenerationRecord(
        voice_name="Elena",
        input_text="The swift brown fox jumped over the fence.",
        output_audio_path="/outputs/gen_audio_01.wav",
        duration_sec=2.85,
        latency_ms=142.0,
        quality_metrics=metrics,
    )
    repo.save(rec)

    history = repo.list_recent(limit=10)
    assert len(history) == 1
    item = history[0]
    assert item.voice_name == "Elena"
    assert item.duration_sec == 2.85
    assert item.quality_metrics is not None
    assert item.quality_metrics.snr_db == 32.4
