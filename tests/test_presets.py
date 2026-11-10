"""Tests for factory voice presets and database seeding."""

from pathlib import Path
import pytest

from VoiceStudio.db.connection import DatabaseManager
from VoiceStudio.db.repository import VoiceProfileRepository
from VoiceStudio.db.schema import init_schema
from VoiceStudio.models import SynthesisRequest
from VoiceStudio.presets import get_default_presets, seed_preset_voices
from VoiceStudio.synthesis.neural_engine import NeuralVoiceEngine


def test_default_presets_structure():
    presets = get_default_presets()
    assert len(presets) == 4
    preset_ids = [p.id for p in presets]
    assert len(set(preset_ids)) == 4

    for p in presets:
        assert len(p.speaker_embedding) == 128
        assert p.metadata is not None
        assert "f0_shift" in p.metadata
        assert p.language == "en"
        assert p.reference_audio_path is not None


def test_seed_preset_voices_persistence(tmp_path: Path):
    db_path = tmp_path / "test_presets.db"
    db = DatabaseManager(db_path)
    with db.get_connection() as conn:
        init_schema(conn)

    repo = VoiceProfileRepository(db)
    assert len(repo.list_all()) == 0

    # Seed presets
    seeded = seed_preset_voices(repo)
    assert len(seeded) == 4

    profiles = repo.list_all()
    assert len(profiles) == 4

    # Idempotence: Calling seed again should not duplicate
    seeded_again = seed_preset_voices(repo, force=False)
    assert len(seeded_again) == 4
    assert len(repo.list_all()) == 4


def test_synthesis_with_preset_voice():
    presets = get_default_presets()
    deep_voice = next(p for p in presets if p.id == "preset-atlas-echo")
    bright_voice = next(p for p in presets if p.id == "preset-nova-clarity")

    engine = NeuralVoiceEngine(sample_rate=24000)
    req = SynthesisRequest(text="Neural voice cloning active", pitch=0.0, speed=1.0)

    audio_deep, sr_deep = engine.synthesize(req, profile=deep_voice)
    audio_bright, sr_bright = engine.synthesize(req, profile=bright_voice)

    assert len(audio_deep) > 0
    assert len(audio_bright) > 0
    assert sr_deep == 24000
    assert sr_bright == 24000
