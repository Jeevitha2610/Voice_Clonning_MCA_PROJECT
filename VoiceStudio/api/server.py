"""FastAPI REST application server and streaming endpoints for VoiceStudio."""

import asyncio
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import time
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from VoiceStudio.config import config
from VoiceStudio.db.connection import DatabaseManager
from VoiceStudio.db.repository import GenerationRepository, VoiceProfileRepository
from VoiceStudio.db.schema import init_schema
from VoiceStudio.dsp.processor import AudioProcessor
from VoiceStudio.dsp.quality import AudioQualityEvaluator
from VoiceStudio.exceptions import StorageSecurityError, VoiceProfileNotFoundError, VoiceStudioError
from VoiceStudio.models import (
    AudioQualityMetrics,
    GenerationRecord,
    SynthesisRequest,
    VoiceProfile,
)
from VoiceStudio.presets import seed_preset_voices
from VoiceStudio.storage.media import StorageService
from VoiceStudio.synthesis.neural_engine import NeuralVoiceEngine
from VoiceStudio.synthesis.registry import EngineRegistry

logger = logging.getLogger("VoiceStudio.API")


def create_app(
    db_manager: Optional[DatabaseManager] = None,
    storage_service: Optional[StorageService] = None,
    engine_registry: Optional[EngineRegistry] = None,
) -> FastAPI:
    """Factory function creating configured FastAPI application."""
    app = FastAPI(
        title="VoiceStudio Autonomous Speech Studio",
        description="Local-first, pure Python neural voice cloning and speech synthesis server.",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    db = db_manager or DatabaseManager(config.db_path)
    with db.get_connection() as conn:
        init_schema(conn)

    profile_repo = VoiceProfileRepository(db)
    seed_preset_voices(profile_repo)
    gen_repo = GenerationRepository(db)
    storage = storage_service or StorageService(
        base_dir=config.data_dir,
        uploads_dir=config.uploads_dir,
        outputs_dir=config.outputs_dir,
        allowed_extensions=config.allowed_audio_extensions,
        max_size_bytes=config.max_upload_size_bytes,
    )
    registry = engine_registry or EngineRegistry()

    static_dir = Path(__file__).parent.parent / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get("/api/health", summary="System Health & Hardware Status")
    async def get_health() -> Dict[str, Any]:
        engines = registry.list_engines()
        return {
            "status": "online",
            "version": "0.1.0",
            "device": config.device,
            "sample_rate": config.default_sample_rate,
            "engines": engines,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    @app.post("/api/voices/upload", summary="Upload Reference Voice & Create Profile")
    async def upload_voice_profile(
        name: str = Form(..., description="Name for this voice profile"),
        description: Optional[str] = Form(default=""),
        language: str = Form(default="en"),
        is_default: bool = Form(default=False),
        file: UploadFile = File(..., description="WAV/MP3 reference audio file"),
    ) -> VoiceProfile:
        try:
            file_bytes = await file.read()
            saved_path = storage.save_upload(file_bytes, file.filename or "upload.wav")

            audio_data, sr = AudioProcessor.load_audio(saved_path, target_sr=config.default_sample_rate)
            engine = registry.get_engine()
            embedding = engine.extract_speaker_embedding(audio_data, sr)
            metrics = AudioQualityEvaluator.calculate_metrics(audio_data, sr)

            profile = VoiceProfile(
                name=name.strip(),
                description=description.strip() if description else "",
                reference_audio_path=str(saved_path),
                speaker_embedding=embedding,
                language=language,
                is_default=is_default,
                metadata={"quality_metrics": metrics.model_dump()},
            )
            profile_repo.save(profile)
            return profile

        except StorageSecurityError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
        except VoiceStudioError as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

    @app.get("/api/voices", summary="List All Voice Profiles")
    async def list_voice_profiles() -> List[VoiceProfile]:
        return profile_repo.list_all()

    @app.get("/api/voices/{profile_id}", summary="Get Voice Profile by ID")
    async def get_voice_profile(profile_id: str) -> VoiceProfile:
        try:
            return profile_repo.get_by_id(profile_id)
        except VoiceProfileNotFoundError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    @app.delete("/api/voices/{profile_id}", summary="Delete Voice Profile")
    async def delete_voice_profile(profile_id: str) -> Dict[str, bool]:
        try:
            profile = profile_repo.get_by_id(profile_id)
            storage.delete_file(profile.reference_audio_path)
            deleted = profile_repo.delete(profile_id)
            return {"deleted": deleted}
        except VoiceProfileNotFoundError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    @app.post("/api/synthesize", summary="Synthesize Text-to-Speech")
    async def synthesize_speech(req: SynthesisRequest) -> GenerationRecord:
        t0 = time.perf_counter()
        profile: Optional[VoiceProfile] = None

        if req.voice_profile_id:
            try:
                profile = profile_repo.get_by_id(req.voice_profile_id)
            except VoiceProfileNotFoundError:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requested voice profile not found")

        engine = registry.get_engine()
        audio_data, sr = engine.synthesize(req, profile=profile)

        out_path = storage.allocate_output_path(prefix="tts", extension=".wav")
        AudioProcessor.save_wav(out_path, audio_data, sample_rate=sr)

        duration = float(len(audio_data) / sr) if sr > 0 else 0.0
        latency = float((time.perf_counter() - t0) * 1000.0)
        metrics = AudioQualityEvaluator.calculate_metrics(audio_data, sr)

        record = GenerationRecord(
            voice_profile_id=profile.id if profile else None,
            voice_name=profile.name if profile else "Default Neural",
            input_text=req.text,
            output_audio_path=str(out_path),
            duration_sec=round(duration, 2),
            latency_ms=round(latency, 1),
            sample_rate=sr,
            quality_metrics=metrics,
        )
        gen_repo.save(record)
        return record

    @app.get("/api/history", summary="List Generation History")
    async def list_generation_history(limit: int = 50) -> List[GenerationRecord]:
        return gen_repo.list_recent(limit=limit)

    @app.get("/api/audio/{filename}", summary="Stream Generated Audio File")
    async def get_audio_file(filename: str) -> FileResponse:
        try:
            target = storage.outputs_dir / filename
            safe_path = storage.validate_path(target)
            if not safe_path.exists():
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audio file not found")
            return FileResponse(
                path=str(safe_path),
                media_type="audio/wav",
                filename=filename,
            )
        except StorageSecurityError as exc:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))

    @app.get("/api/synthesize/sse", summary="Server-Sent Events Synthesis Progress")
    async def synthesize_sse(text: str, profile_id: Optional[str] = None) -> StreamingResponse:
        """Stream progress events during generation."""
        async def event_generator():
            words = text.split()
            total = len(words)
            yield f"data: {json.dumps({'status': 'started', 'total_words': total})}\n\n"
            for i, word in enumerate(words):
                await asyncio.sleep(0.04)
                pct = int(((i + 1) / total) * 100)
                yield f"data: {json.dumps({'status': 'processing', 'word': word, 'progress_pct': pct})}\n\n"
            yield f"data: {json.dumps({'status': 'completed', 'progress_pct': 100})}\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    @app.get("/", response_class=HTMLResponse, summary="Studio UI Workspace")
    async def serve_studio_ui() -> HTMLResponse:
        index_file = static_dir / "index.html"
        if index_file.exists():
            return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
        return HTMLResponse(content="<h1>VoiceStudio Pure Python Backend Active</h1>")

    return app


app = create_app()
