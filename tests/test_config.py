"""Unit tests for VoiceStudio configuration management."""

from pathlib import Path
import tempfile

from VoiceStudio.config import AppConfig


def test_app_config_defaults():
    """Verify default configuration values and directory resolution."""
    cfg = AppConfig()
    assert cfg.default_sample_rate == 24000
    assert cfg.target_lufs == -23.0
    assert cfg.device == "cpu"
    assert cfg.max_upload_size_bytes == 25 * 1024 * 1024
    assert ".wav" in cfg.allowed_audio_extensions


def test_ensure_directories(tmp_path: Path):
    """Verify that ensure_directories safely creates necessary directory tree."""
    custom_data = tmp_path / "custom_data"
    cfg = AppConfig(
        data_dir=custom_data,
        uploads_dir=custom_data / "uploads",
        outputs_dir=custom_data / "outputs",
        db_path=custom_data / "app.db",
    )
    assert not custom_data.exists()
    cfg.ensure_directories()
    assert custom_data.exists()
    assert (custom_data / "uploads").exists()
    assert (custom_data / "outputs").exists()
