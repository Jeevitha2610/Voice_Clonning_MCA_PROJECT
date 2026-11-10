"""Integration and contract tests for FastAPI REST and SSE endpoints."""

import io
from pathlib import Path
import numpy as np
import pytest
import soundfile as sf
from starlette.testclient import TestClient

from VoiceStudio.api.server import create_app
from VoiceStudio.db.connection import DatabaseManager
from VoiceStudio.storage.media import StorageService
from VoiceStudio.synthesis.registry import EngineRegistry


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    """Fixture providing a TestClient connected to isolated test storage and database."""
    base_dir = tmp_path / "app_data"
    uploads_dir = base_dir / "uploads"
    outputs_dir = base_dir / "outputs"
    db_file = base_dir / "test.db"

    db_manager = DatabaseManager(db_file)
    storage = StorageService(base_dir=base_dir, uploads_dir=uploads_dir, outputs_dir=outputs_dir)
    registry = EngineRegistry()

    app = create_app(
        db_manager=db_manager,
        storage_service=storage,
        engine_registry=registry,
    )
    return TestClient(app)


def test_health_endpoint(client: TestClient):
    """Test system health check reporting online status and engines."""
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "online"
    assert data["version"] == "0.1.0"
    assert len(data["engines"]) >= 1


def test_voice_upload_and_synthesis_flow(client: TestClient):
    """Test full voice profile upload followed by conditioned text-to-speech generation."""
    # 1. Create a dummy reference WAV in memory
    sr = 24000
    t = np.linspace(0, 0.5, int(sr * 0.5), endpoint=False)
    wav_bytes = io.BytesIO()
    sf.write(wav_bytes, (0.4 * np.sin(2 * np.pi * 220 * t)).astype(np.float32), sr, format="WAV")
    wav_bytes.seek(0)

    # 2. Upload voice reference
    upload_resp = client.post(
        "/api/voices/upload",
        data={"name": "Sarah Studio", "description": "Crisp narration voice", "language": "en"},
        files={"file": ("sarah_sample.wav", wav_bytes, "audio/wav")},
    )
    assert upload_resp.status_code == 200
    profile = upload_resp.json()
    assert profile["name"] == "Sarah Studio"
    assert profile["id"] is not None
    assert len(profile["speaker_embedding"]) == 128

    profile_id = profile["id"]

    # 3. List voice profiles
    list_resp = client.get("/api/voices")
    assert list_resp.status_code == 200
    profiles = list_resp.json()
    assert len(profiles) == 1
    assert profiles[0]["id"] == profile_id

    # 4. Synthesize speech using the uploaded voice profile
    synth_resp = client.post(
        "/api/synthesize",
        json={
            "text": "Autonomous speech generation verified successfully.",
            "voice_profile_id": profile_id,
            "speed": 1.1,
            "pitch": 0.0,
            "normalize_loudness": True,
        },
    )
    assert synth_resp.status_code == 200
    record = synth_resp.json()
    assert record["voice_name"] == "Sarah Studio"
    assert record["duration_sec"] > 0
    assert record["quality_metrics"]["is_clean"] is True

    # 5. Check generation history
    hist_resp = client.get("/api/history")
    assert hist_resp.status_code == 200
    history = hist_resp.json()
    assert len(history) == 1
    assert history[0]["id"] == record["id"]

    # 6. Delete voice profile
    del_resp = client.delete(f"/api/voices/{profile_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["deleted"] is True


def test_sse_progress_stream(client: TestClient):
    """Verify Server-Sent Events (SSE) streaming output."""
    resp = client.get("/api/synthesize/sse?text=Hello+Voice+Studio")
    assert resp.status_code == 200
    assert "text/event-stream" in resp.headers["content-type"]
    text_content = resp.text
    assert "data: " in text_content
    assert "completed" in text_content
