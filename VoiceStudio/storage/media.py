"""Secure audio media storage service with path isolation and validation."""

import os
from pathlib import Path
import re
from typing import Optional, Set
import uuid

from VoiceStudio.exceptions import StorageSecurityError


class StorageService:
    """Provides path-traversal-guarded storage for reference audio and synthesis artifacts."""

    def __init__(
        self,
        base_dir: Path,
        uploads_dir: Path,
        outputs_dir: Path,
        allowed_extensions: Optional[Set[str]] = None,
        max_size_bytes: int = 25 * 1024 * 1024,
    ) -> None:
        self.base_dir = Path(base_dir).resolve()
        self.uploads_dir = Path(uploads_dir).resolve()
        self.outputs_dir = Path(outputs_dir).resolve()
        self.allowed_extensions = allowed_extensions or {".wav", ".mp3", ".flac", ".ogg"}
        self.max_size_bytes = max_size_bytes

        # Ensure isolated folders exist
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        self.outputs_dir.mkdir(parents=True, exist_ok=True)

    def save_upload(self, file_bytes: bytes, filename: str) -> Path:
        """Validate, sanitize, and persist an uploaded reference audio file."""
        if len(file_bytes) > self.max_size_bytes:
            raise StorageSecurityError(
                f"File size exceeds maximum permitted limit ({len(file_bytes)} > {self.max_size_bytes} bytes)"
            )

        ext = Path(filename).suffix.lower()
        if ext not in self.allowed_extensions:
            raise StorageSecurityError(
                f"Unsupported audio extension '{ext}'. Permitted: {', '.join(sorted(self.allowed_extensions))}"
            )

        # Generate non-colliding UUID name
        safe_id = uuid.uuid4().hex
        target_path = self.uploads_dir / f"ref_{safe_id}{ext}"
        self.validate_path(target_path)

        target_path.write_bytes(file_bytes)
        return target_path

    def allocate_output_path(self, prefix: str = "synth", extension: str = ".wav") -> Path:
        """Allocate a secure, non-colliding destination path for generated audio."""
        safe_id = uuid.uuid4().hex
        ext = extension if extension.startswith(".") else f".{extension}"
        target = self.outputs_dir / f"{prefix}_{safe_id}{ext}"
        self.validate_path(target)
        return target

    def validate_path(self, path: Path | str) -> Path:
        """Verify that the target path does not escape storage boundaries (anti-path-traversal)."""
        resolved = Path(path).resolve()
        try:
            # Check if resolved path is subpath of base_dir, uploads_dir, or outputs_dir
            is_in_uploads = resolved.is_relative_to(self.uploads_dir)
            is_in_outputs = resolved.is_relative_to(self.outputs_dir)
            is_in_base = resolved.is_relative_to(self.base_dir)

            if not (is_in_uploads or is_in_outputs or is_in_base):
                raise StorageSecurityError(f"Access denied: path escapes authorized directory: {path}")
        except ValueError as exc:
            raise StorageSecurityError(f"Path validation failed for {path}: {exc}") from exc

        return resolved

    def delete_file(self, path: Path | str) -> bool:
        """Safely delete a file within storage boundaries."""
        target = self.validate_path(path)
        if target.exists() and target.is_file():
            target.unlink()
            return True
        return False
