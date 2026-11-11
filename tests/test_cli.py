"""Automated tests for VoiceStudio Command Line Interface (CLI)."""

import io
from pathlib import Path
import numpy as np
import pytest
import soundfile as sf

from VoiceStudio.cli import main
from VoiceStudio.config import config


@pytest.fixture(autouse=True)
def isolated_cli_storage(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure CLI tests operate on an isolated temporary database and media directory."""
    monkeypatch.setattr(config, "data_dir", tmp_path / "cli_data")
    monkeypatch.setattr(config, "db_path", tmp_path / "cli_data" / "test_cli.db")
    monkeypatch.setattr(config, "uploads_dir", tmp_path / "cli_data" / "uploads")
    monkeypatch.setattr(config, "outputs_dir", tmp_path / "cli_data" / "outputs")


@pytest.fixture
def sample_wav(tmp_path: Path) -> Path:
    sr = 24000
    t = np.linspace(0, 0.4, int(sr * 0.4), endpoint=False)
    audio = (0.5 * np.sin(2 * np.pi * 300 * t)).astype(np.float32)
    wav_path = tmp_path / "sample.wav"
    sf.write(str(wav_path), audio, sr)
    return wav_path


def test_cli_list_voices(capsys):
    ret = main(["list-voices"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "VOICE ID" in captured.out
    assert "Aria Prime" in captured.out


def test_cli_assess_audio(sample_wav: Path, capsys):
    ret = main(["assess", "--file", str(sample_wav)])
    assert ret == 0
    captured = capsys.readouterr()
    assert "ACOUSTIC QUALITY AUDIT" in captured.out
    assert "SNR" in captured.out
    assert "Sample Rate" in captured.out


def test_cli_clone_voice(sample_wav: Path, capsys):
    ret = main([
        "clone-voice",
        "--name", "CLI Voice Test",
        "--file", str(sample_wav),
        "--desc", "Cloned via automated test",
        "--lang", "en",
    ])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Voice profile registered successfully!" in captured.out


def test_cli_synthesize(tmp_path: Path, capsys):
    out_wav = tmp_path / "cli_synth_out.wav"
    ret = main([
        "synthesize",
        "--text", "Hello CLI speech testing.",
        "--out", str(out_wav),
        "--speed", "1.0",
        "--pitch", "0.0",
    ])
    assert ret == 0
    assert out_wav.exists()
    assert out_wav.stat().st_size > 44  # Valid WAV header + samples
    captured = capsys.readouterr()
    assert "Audio generated successfully" in captured.out
