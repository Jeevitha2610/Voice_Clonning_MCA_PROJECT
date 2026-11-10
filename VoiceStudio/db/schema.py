"""Database schema definitions and table initializations for VoiceStudio."""

import sqlite3

SCHEMA_DDL = """
CREATE TABLE IF NOT EXISTS voice_profiles (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    reference_audio_path TEXT NOT NULL,
    transcript TEXT,
    speaker_embedding_json TEXT,
    language TEXT NOT NULL DEFAULT 'en',
    is_default INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    metadata_json TEXT
);

CREATE TABLE IF NOT EXISTS generation_records (
    id TEXT PRIMARY KEY,
    voice_profile_id TEXT,
    voice_name TEXT NOT NULL,
    input_text TEXT NOT NULL,
    output_audio_path TEXT NOT NULL,
    duration_sec REAL NOT NULL,
    latency_ms REAL NOT NULL,
    sample_rate INTEGER NOT NULL DEFAULT 24000,
    quality_metrics_json TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (voice_profile_id) REFERENCES voice_profiles(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_voice_profiles_created ON voice_profiles(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_generation_records_created ON generation_records(created_at DESC);
"""


def init_schema(conn: sqlite3.Connection) -> None:
    """Execute initial schema creation DDL."""
    with conn:
        conn.executescript(SCHEMA_DDL)
