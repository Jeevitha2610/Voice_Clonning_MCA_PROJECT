---
name: python-voice-engineering
description: Guide for developing high-performance Python speech synthesis, zero-shot voice cloning, PyTorch/ONNX neural inference, audio signal processing (DSP), and audio quality assessment. Use when implementing or debugging voice models, audio conversion, and audio quality metrics.
---

# Python Voice Engineering & Audio DSP

This skill defines the technical standards, numerical procedures, and neural execution guidelines for building local-first Python voice cloning systems.

## 1. Multi-Engine Neural TTS Protocol
Every voice synthesis engine must adhere to the abstract `TTSBackend` contract:
- **`generate(text, voice_profile, language, speed) -> AudioSegment`**
- Standardized audio output: Float32 waveform normalized in `[-1.0, 1.0]`, mono channel, constant sample rate (typically 16kHz, 22.05kHz, or 24kHz).
- Preflight validation: Check weight integrity, VRAM/RAM budgets, and license acceptance before execution.

## 2. Zero-Shot Voice Cloning Logic
Zero-shot cloning uses acoustic conditioning vectors extracted from reference recordings:
1. **Reference Validation:**
   - Duration: Minimum 3.0s, optimal 5.0s–15.0s, maximum 30.0s.
   - Quality check: SNR > 15 dB, zero clipping, minimum 0.5s active speech.
2. **Preprocessing:**
   - Convert to 16kHz mono WAV using 64-bit IEEE float intermediate buffers.
   - High-pass filter at 50 Hz to remove DC offset and handling rumble.
3. **Conditioning:**
   - Extract acoustic timbre embeddings.
   - Pass embeddings to the acoustic generator or flow-matching diffusion model.

## 3. Audio Signal Processing (DSP) & Loudness
- **EBU R128 Normalization:** Target integrated loudness of -23.0 LUFS (broadcast standard) or -16.0 LUFS (podcast/streaming).
- **True Peak Limiting:** Bound peak amplitude to -1.0 dBTP to eliminate inter-sample clipping upon playback and lossy encoding.
- **Silence Trimming:** Trim leading/trailing digital silence exceeding 200ms while preserving natural speech pauses.

## 4. Objective Audio Quality Evaluation
Evaluate generated speech across four automated metrics:
- **Non-Zero Energy Ratio:** $\frac{\sum |x[n]| > 10^{-4}}{N} > 0.40$ (ensures speech is present, not dead air).
- **Clipping Detection:** Count of samples $|x[n]| \ge 0.999$. Must be 0.
- **Estimated SNR:** Signal-to-noise ratio $\ge 18\text{ dB}$.
- **Duration Plausibility:** Audio duration must match estimated reading speed (approx. 2.5–3.5 words/second).
