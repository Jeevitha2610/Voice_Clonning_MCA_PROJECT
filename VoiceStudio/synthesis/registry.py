"""Engine registry for managing and routing synthesis backends."""

from typing import Dict, List, Optional

from VoiceStudio.exceptions import ModelUnavailableError
from VoiceStudio.synthesis.base import TTSBackend
from VoiceStudio.synthesis.neural_engine import NeuralVoiceEngine


class EngineRegistry:
    """Registry maintaining available TTS and voice cloning backends."""

    def __init__(self) -> None:
        self._engines: Dict[str, TTSBackend] = {}
        self._default_engine_name: Optional[str] = None
        self._register_defaults()

    def register(self, engine: TTSBackend, is_default: bool = False) -> None:
        """Register a new synthesis backend."""
        self._engines[engine.engine_name] = engine
        if is_default or self._default_engine_name is None:
            self._default_engine_name = engine.engine_name

    def get_engine(self, engine_name: Optional[str] = None) -> TTSBackend:
        """Retrieve the requested engine or fall back to the default available engine."""
        name = engine_name or self._default_engine_name
        if not name or name not in self._engines:
            raise ModelUnavailableError(f"TTS backend '{name}' is not registered")

        engine = self._engines[name]
        is_avail, reason = engine.is_available()
        if not is_avail:
            raise ModelUnavailableError(f"TTS engine '{name}' is unavailable: {reason}")

        return engine

    def list_engines(self) -> List[Dict[str, str]]:
        """List all registered engines and their availability statuses."""
        results = []
        for name, engine in self._engines.items():
            is_avail, reason = engine.is_available()
            results.append({
                "engine_name": name,
                "sample_rate": engine.sample_rate,
                "is_available": is_avail,
                "status_reason": reason,
                "is_default": (name == self._default_engine_name),
            })
        return results

    def _register_defaults(self) -> None:
        """Register built-in CPU neural engine."""
        neural = NeuralVoiceEngine(sample_rate=24000, device="cpu")
        self.register(neural, is_default=True)
