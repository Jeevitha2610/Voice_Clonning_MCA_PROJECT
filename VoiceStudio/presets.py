"""Built-in neural voice presets and automatic catalog seeding for VoiceStudio."""

from datetime import datetime, timezone
from typing import List

from VoiceStudio.db.repository import VoiceProfileRepository
from VoiceStudio.models import VoiceProfile


def get_default_presets() -> List[VoiceProfile]:
    """Return calibrated factory voice profiles with diverse acoustic characteristics."""
    now = datetime.now(timezone.utc)

    # Factory preset 1: Aria Prime (Neutral / Studio Narrator)
    aria_emb = [0.08 * (1.0 + 0.2 * (i % 7)) for i in range(128)]
    aria = VoiceProfile(
        id="preset-aria-prime",
        name="Aria Prime (Studio Narrator)",
        description="Balanced, clear broadcast narrator with wide dynamic range and natural presence.",
        reference_audio_path="builtin://aria-prime",
        language="en",
        is_default=True,
        speaker_embedding=aria_emb,
        created_at=now,
        metadata={"f0_shift": 45.0, "category": "narrator", "style": "natural"},
    )

    # Factory preset 2: Atlas Echo (Deep Broadcast / Radio Host)
    atlas_emb = [-0.12 * (1.0 + 0.15 * (i % 5)) for i in range(128)]
    atlas = VoiceProfile(
        id="preset-atlas-echo",
        name="Atlas Echo (Deep Radio)",
        description="Resonant, authoritative low-frequency broadcast voice with warm sub-harmonics.",
        reference_audio_path="builtin://atlas-echo",
        language="en",
        is_default=False,
        speaker_embedding=atlas_emb,
        created_at=now,
        metadata={"f0_shift": -35.0, "category": "broadcast", "style": "deep"},
    )

    # Factory preset 3: Nova Clarity (Crisp Technical Narrator)
    nova_emb = [0.15 * (1.0 + 0.25 * (i % 9)) for i in range(128)]
    nova = VoiceProfile(
        id="preset-nova-clarity",
        name="Nova Clarity (Crisp Technical)",
        description="Precise, articulate voice with high-frequency clarity ideal for documentation and tech audio.",
        reference_audio_path="builtin://nova-clarity",
        language="en",
        is_default=False,
        speaker_embedding=nova_emb,
        created_at=now,
        metadata={"f0_shift": 70.0, "category": "technical", "style": "bright"},
    )

    # Factory preset 4: Orion Warmth (Calm Storyteller / Audiobook)
    orion_emb = [-0.04 * (1.0 + 0.1 * (i % 4)) for i in range(128)]
    orion = VoiceProfile(
        id="preset-orion-warmth",
        name="Orion Warmth (Calm Storyteller)",
        description="Gentle, soothing cadence with natural intimacy for audiobooks, poetry, and meditation.",
        reference_audio_path="builtin://orion-warmth",
        language="en",
        is_default=False,
        speaker_embedding=orion_emb,
        created_at=now,
        metadata={"f0_shift": -10.0, "category": "storyteller", "style": "warm"},
    )

    return [aria, atlas, nova, orion]


def seed_preset_voices(repo: VoiceProfileRepository, force: bool = False) -> List[VoiceProfile]:
    """Seed factory voice presets into the database if empty or if force=True."""
    existing = repo.list_all()
    if existing and not force:
        return existing

    presets = get_default_presets()
    seeded = []
    for preset in presets:
        saved = repo.save(preset)
        seeded.append(saved)
    return seeded
