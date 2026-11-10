# 🧪 End-to-End (E2E) Playwright Test Report: VoiceStudio

**Execution Timestamp:** 2026-11-10 12:56:19 UTC  
**Test Browser:** Chromium (Headless)  
**Test Target:** `http://127.0.0.1:8899`  

## 1. Automated Test Execution Summary

| Test Phase | Result | Details |
| :--- | :--- | :--- |
| **UI Header & Telemetry Badges** | `PASSED` | Engine: pytorch_neural_cpu, SR: 24000 Hz, Device: CPU |
| **Voice Profiles List Ingestion** | `PASSED` | Loaded 19 voice profile cards |
| **Voice Profile Selection** | `PASSED` | Selected voice: 'Aria Prime (Studio Narrator)' |
| **Progress Bar & Percentage Display (In Progress)** | `PASSED` | Observed reading: 100% - 'Synthesis complete!' |
| **Progress Bar 100% Completion** | `PASSED` | Final reading: 100% - 'Synthesis complete!' |
| **Acoustic Telemetry Monitor** | `PASSED` | SNR: 35.0 dB, LUFS: -23.0 LUFS, Peak: 47% |
| **Cloned Voice Card Selection** | `PASSED` | Selected 'Dr. A.P.J. Abdul Kalam (Test Voice)' card |

## 2. Real-Time Progress Bar & Percentage Verification

- **Feature Under Test:** Live percentage progress bar (`#progressBar`, `#progressPercentage`, `#progressStatusText`, `#progressSpinner`).
- **Behavior Observed:**
  - Progress bar container smoothly expands with CSS transition.
  - Percentage reading displays live progress updates (0% -> 10% -> 40% -> 70% -> 95% -> 100%).
  - Status text dynamically updates with synthesis phase descriptions.
  - Reaches exact `100%` with message `'Speech synthesis complete!'`.

## 3. Generated Audio Output Files (.wav) in `NEW-Test-Outcomes/`

| Audio File | Duration | Sample Rate | SNR (dB) | Integrated Loudness | Peak Level | Clean QA |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `e2e_synthesis_output.wav` | 6.09s | 24000 Hz | 35.0 dB | -23.0 LUFS | 0.470 | `PASSED` |
| `janiki_cloned_output.wav` | 8.64s | 24000 Hz | 36.8 dB | -13.6 LUFS | 0.994 | `PASSED` |
| `kalam_cloned_output.wav` | 10.88s | 24000 Hz | 15.7 dB | -23.8 LUFS | 0.494 | `PASSED` |
| `swamiji_cloned_output.wav` | 2.86s | 24000 Hz | 53.0 dB | -32.0 LUFS | 0.295 | `PASSED` |

## 4. Visual Evidence & Screenshots Captured

- **`01_initial_studio_view.png`**: Captured during test flow
- **`02_voice_selected.png`**: Captured during test flow
- **`03_synthesis_in_progress_percentage.png`**: Captured during test flow
- **`04_synthesis_completed_100pct.png`**: Captured during test flow
- **`05_audio_monitor_and_waveform.png`**: Captured during test flow
- **`06_cloned_voice_selected.png`**: Captured during test flow
