"""Repository access layer for voice profiles and generation history."""

from datetime import datetime, timezone
import json
from typing import List, Optional

from VoiceStudio.db.connection import DatabaseManager
from VoiceStudio.exceptions import DatabaseError, VoiceProfileNotFoundError
from VoiceStudio.models import AudioQualityMetrics, GenerationRecord, VoiceProfile


class VoiceProfileRepository:
    """Data access repository for conditioned Voice Profiles."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        self.db = db_manager

    def save(self, profile: VoiceProfile) -> VoiceProfile:
        """Insert or update a VoiceProfile."""
        sql = """
        INSERT INTO voice_profiles (
            id, name, description, reference_audio_path, transcript,
            speaker_embedding_json, language, is_default, created_at, metadata_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            name=excluded.name,
            description=excluded.description,
            reference_audio_path=excluded.reference_audio_path,
            transcript=excluded.transcript,
            speaker_embedding_json=excluded.speaker_embedding_json,
            language=excluded.language,
            is_default=excluded.is_default,
            metadata_json=excluded.metadata_json;
        """
        emb_json = json.dumps(profile.speaker_embedding) if profile.speaker_embedding else None
        meta_json = json.dumps(profile.metadata) if profile.metadata else None

        try:
            with self.db.get_connection() as conn:
                conn.execute(
                    sql,
                    (
                        profile.id,
                        profile.name,
                        profile.description,
                        profile.reference_audio_path,
                        profile.transcript,
                        emb_json,
                        profile.language,
                        1 if profile.is_default else 0,
                        profile.created_at.isoformat(),
                        meta_json,
                    ),
                )
            return profile
        except Exception as exc:
            raise DatabaseError(f"Failed to save voice profile {profile.id}: {exc}") from exc

    def get_by_id(self, profile_id: str) -> VoiceProfile:
        """Retrieve a voice profile by its unique ID."""
        sql = "SELECT * FROM voice_profiles WHERE id = ?;"
        try:
            with self.db.get_connection() as conn:
                row = conn.execute(sql, (profile_id,)).fetchone()
                if not row:
                    raise VoiceProfileNotFoundError(f"Voice profile {profile_id} not found")
                return self._row_to_model(row)
        except VoiceProfileNotFoundError:
            raise
        except Exception as exc:
            raise DatabaseError(f"Error fetching profile {profile_id}: {exc}") from exc

    def list_all(self) -> List[VoiceProfile]:
        """List all registered voice profiles ordered by creation date."""
        sql = "SELECT * FROM voice_profiles ORDER BY is_default DESC, created_at DESC;"
        try:
            with self.db.get_connection() as conn:
                rows = conn.execute(sql).fetchall()
                return [self._row_to_model(r) for r in rows]
        except Exception as exc:
            raise DatabaseError(f"Error listing voice profiles: {exc}") from exc

    def delete(self, profile_id: str) -> bool:
        """Delete a voice profile by ID."""
        sql = "DELETE FROM voice_profiles WHERE id = ?;"
        try:
            with self.db.get_connection() as conn:
                cursor = conn.execute(sql, (profile_id,))
                return cursor.rowcount > 0
        except Exception as exc:
            raise DatabaseError(f"Error deleting voice profile {profile_id}: {exc}") from exc

    def _row_to_model(self, row) -> VoiceProfile:
        emb = json.loads(row["speaker_embedding_json"]) if row["speaker_embedding_json"] else None
        meta = json.loads(row["metadata_json"]) if row["metadata_json"] else {}
        created = datetime.fromisoformat(row["created_at"])
        return VoiceProfile(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            reference_audio_path=row["reference_audio_path"],
            transcript=row["transcript"],
            speaker_embedding=emb,
            language=row["language"],
            is_default=bool(row["is_default"]),
            created_at=created,
            metadata=meta,
        )


class GenerationRepository:
    """Data access repository for TTS generation history and audit logs."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        self.db = db_manager

    def save(self, record: GenerationRecord) -> GenerationRecord:
        """Insert a generation record."""
        sql = """
        INSERT INTO generation_records (
            id, voice_profile_id, voice_name, input_text, output_audio_path,
            duration_sec, latency_ms, sample_rate, quality_metrics_json, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        metrics_json = record.quality_metrics.model_dump_json() if record.quality_metrics else None
        try:
            with self.db.get_connection() as conn:
                conn.execute(
                    sql,
                    (
                        record.id,
                        record.voice_profile_id,
                        record.voice_name,
                        record.input_text,
                        record.output_audio_path,
                        record.duration_sec,
                        record.latency_ms,
                        record.sample_rate,
                        metrics_json,
                        record.created_at.isoformat(),
                    ),
                )
            return record
        except Exception as exc:
            raise DatabaseError(f"Failed to save generation record {record.id}: {exc}") from exc

    def list_recent(self, limit: int = 50) -> List[GenerationRecord]:
        """Fetch recent speech generations."""
        sql = "SELECT * FROM generation_records ORDER BY created_at DESC LIMIT ?;"
        try:
            with self.db.get_connection() as conn:
                rows = conn.execute(sql, (limit,)).fetchall()
                results = []
                for row in rows:
                    metrics = None
                    if row["quality_metrics_json"]:
                        metrics = AudioQualityMetrics.model_validate_json(row["quality_metrics_json"])
                    created = datetime.fromisoformat(row["created_at"])
                    results.append(
                        GenerationRecord(
                            id=row["id"],
                            voice_profile_id=row["voice_profile_id"],
                            voice_name=row["voice_name"],
                            input_text=row["input_text"],
                            output_audio_path=row["output_audio_path"],
                            duration_sec=row["duration_sec"],
                            latency_ms=row["latency_ms"],
                            sample_rate=row["sample_rate"],
                            quality_metrics=metrics,
                            created_at=created,
                        )
                    )
                return results
        except Exception as exc:
            raise DatabaseError(f"Error fetching generation history: {exc}") from exc
