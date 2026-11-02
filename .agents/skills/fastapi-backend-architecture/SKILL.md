---
name: fastapi-backend-architecture
description: Guidelines and runbooks for building modular FastAPI application servers, asynchronous REST/SSE streaming endpoints, SQLite WAL database repositories, and secure audio file management. Use when designing backend routes, storage models, and API interfaces.
---

# FastAPI Backend & Data Storage Architecture

This skill governs the backend API design, database schemas, and audio streaming architecture for the Voice Cloning Studio.

## 1. Application Architecture & Routers
- **FastAPI Core (`api/app.py`)**: Mounts modular sub-routers with clear URI namespaces:
  - `/api/v1/profiles`: Voice profile creation, retrieval, updates, and deletion.
  - `/api/v1/synthesize`: Text-to-speech generation and audio rendering.
  - `/api/v1/clone`: Reference audio upload, validation, and timbre extraction.
  - `/api/v1/models`: Local model status, downloads, and readiness checks.
  - `/health`: System and hardware status (CPU, RAM, engine availability).

## 2. Asynchronous Execution & Non-Blocking Design
- Heavy neural inference (PyTorch / ONNX) MUST run in an isolated threadpool (`asyncio.to_thread` or `concurrent.futures.ThreadPoolExecutor`) to prevent stalling the Uvicorn event loop.
- Long-running generation jobs stream real-time progress via Server-Sent Events (SSE) or WebSocket.

## 3. Database Layer (SQLite + WAL Mode)
- **Engine**: Local SQLite database stored at `data/studio.db`.
- **Concurrency**: Enable Write-Ahead Logging (`PRAGMA journal_mode=WAL;`) and busy timeouts (`PRAGMA busy_timeout=5000;`) for robust concurrent multi-threaded access.
- **Tables**:
  - `voice_profiles`: ID, name, reference_audio_path, transcript, consent_date, created_at.
  - `generation_history`: ID, profile_id, input_text, audio_output_path, duration_sec, engine_name, timestamp.
  - `model_cache`: Model ID, local_path, sha256_hash, status.

## 4. Secure File Management
- All uploads stored under a quarantined directory (`data/uploads/`) with random UUID filenames.
- Validate MIME type, file headers (`RIFF....WAVE`), and file size (max 25 MB).
- Reject path traversal attempts (`..`, absolute paths, Windows drive specifiers).
