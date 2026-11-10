"""Application configuration and runtime environment settings for VoiceStudio."""

import os
from pathlib import Path
from typing import Set

from pydantic import BaseModel, Field


class AppConfig(BaseModel):
    """Central configuration for VoiceStudio execution and local storage."""

    # Base paths
    base_dir: Path = Field(default_factory=lambda: Path(os.getcwd()))
    data_dir: Path = Field(default_factory=lambda: Path(os.getcwd()) / "data")
    uploads_dir: Path = Field(default_factory=lambda: Path(os.getcwd()) / "data" / "uploads")
    outputs_dir: Path = Field(default_factory=lambda: Path(os.getcwd()) / "data" / "outputs")
    db_path: Path = Field(default_factory=lambda: Path(os.getcwd()) / "data" / "voicestudio.db")

    # Audio synthesis & DSP defaults
    default_sample_rate: int = Field(default=24000, description="Default synthesis sample rate in Hz")
    target_lufs: float = Field(default=-23.0, description="EBU R128 broadcast loudness target")
    max_upload_size_bytes: int = Field(default=25 * 1024 * 1024, description="Maximum upload size (25MB)")
    allowed_audio_extensions: Set[str] = Field(
        default_factory=lambda: {".wav", ".mp3", ".flac", ".ogg"}
    )

    # Runtime device & model settings
    device: str = Field(default="cpu", description="Execution device for PyTorch inference (cpu/cuda)")
    enable_wal: bool = Field(default=True, description="Enable SQLite Write-Ahead Logging")
    server_host: str = Field(default="127.0.0.1", description="FastAPI host binding")
    server_port: int = Field(default=8000, description="FastAPI port binding")

    def ensure_directories(self) -> None:
        """Create required data and media directories if they do not exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        self.outputs_dir.mkdir(parents=True, exist_ok=True)


# Global singleton instance
config = AppConfig()
config.ensure_directories()
