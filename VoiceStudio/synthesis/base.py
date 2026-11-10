"""Abstract base class and contract for VoiceStudio speech synthesis engines."""

import abc
from typing import Generator, List, Optional, Tuple

import numpy as np

from VoiceStudio.models import SynthesisRequest, VoiceProfile


class TTSBackend(abc.ABC):
    """Abstract speech synthesis engine interface."""

    @property
    @abc.abstractmethod
    def engine_name(self) -> str:
        """Unique identifier for this synthesis backend."""
        pass

    @property
    @abc.abstractmethod
    def sample_rate(self) -> int:
        """Native output sample rate in Hz."""
        pass

    @abc.abstractmethod
    def is_available(self) -> Tuple[bool, str]:
        """Preflight check validating engine dependencies, hardware, and weights."""
        pass

    @abc.abstractmethod
    def extract_speaker_embedding(self, audio: np.ndarray, sample_rate: int) -> List[float]:
        """Extract a 128-dimensional acoustic speaker embedding vector from reference audio."""
        pass

    @abc.abstractmethod
    def synthesize(
        self,
        request: SynthesisRequest,
        profile: Optional[VoiceProfile] = None,
    ) -> Tuple[np.ndarray, int]:
        """Perform end-to-end speech synthesis, returning float32 audio array and sample rate."""
        pass

    @abc.abstractmethod
    def synthesize_stream(
        self,
        request: SynthesisRequest,
        profile: Optional[VoiceProfile] = None,
        chunk_size_samples: int = 4800,
    ) -> Generator[np.ndarray, None, None]:
        """Stream synthesized audio chunks in real time (e.g. for SSE or low-latency playback)."""
        pass
