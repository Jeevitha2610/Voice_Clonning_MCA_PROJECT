# End-to-End (E2E) Playwright Test Report: VoiceStudio

**Execution Timestamp:** 2026-11-11 14:17:14 UTC  
**Test Browser:** Chromium (Headless, 1440x900)  
**Test Target:** `http://127.0.0.1:8899`  

## 1. Automated Test Execution Summary

| Test Phase | Result | Details |
| :--- | :--- | :--- |
| **UI Workspace & Profile Cards** | `PASSED` | Loaded 11 voice profiles (presets + test clones) |
| **Swami Vivekananda (Test Voice) Web Cloning & Progress** | `PASSED` | Progressed smoothly through 27 updates to 100% in 25.9s (<120s) |
| **Aria Prime (Preset Voice) Web Synthesis** | `PASSED` | Reached 100% with studio waveform & telemetry |
| **Dr. A.P.J. Abdul Kalam (Test Voice) Verification** | `PASSED` | Profile active & neural clone WAV verified |
| **S. Janaki (Test Voice) Verification** | `PASSED` | Profile active & neural clone WAV verified |

## 2. Live Web Progress Log for `Swami Vivekananda (Test Voice)`

The following real-time progress updates were captured directly from the DOM (`#progressPercentage`, `#progressStatusText`, `#progressSubtext`) during live synthesis of **Swami Vivekananda (Test Voice)**:

```text
[  0.1s]  15% | Loading OmniVoice neural voice cloning engine on CPU for 'Swami Vivekananda (Test Voice)'... (Voice: Swami Vivekananda (Test Voice) • Progress: 15% • Elapsed: 0.0s)
[  0.6s]  45% | Cloning 'Swami Vivekananda (Test Voice)' [Step 1/8]: Neural acoustic decoding (45%)... (Voice: Swami Vivekananda (Test Voice) • Progress: 45% • Elapsed: 0.5s)
[  1.7s]  46% | Cloning 'Swami Vivekananda (Test Voice)' [Step 1/8]: Synthesizing vocal timbre (46%)... (Voice: Swami Vivekananda (Test Voice) • Progress: 46% • Elapsed: 1.5s)
[  2.8s]  47% | Cloning 'Swami Vivekananda (Test Voice)' [Step 1/8]: Synthesizing vocal timbre (47%)... (Voice: Swami Vivekananda (Test Voice) • Progress: 47% • Elapsed: 2.8s)
[  3.9s]  51% | Cloning 'Swami Vivekananda (Test Voice)' [Step 2/8]: Synthesizing vocal timbre (51%)... (Voice: Swami Vivekananda (Test Voice) • Progress: 51% • Elapsed: 3.8s)
[  5.1s]  52% | Cloning 'Swami Vivekananda (Test Voice)' [Step 2/8]: Synthesizing vocal timbre (52%)... (Voice: Swami Vivekananda (Test Voice) • Progress: 52% • Elapsed: 4.9s)
[  6.5s]  53% | Cloning 'Swami Vivekananda (Test Voice)' [Step 2/8]: Synthesizing vocal timbre (53%)... (Voice: Swami Vivekananda (Test Voice) • Progress: 53% • Elapsed: 6.3s)
[  6.9s]  56% | Cloning 'Swami Vivekananda (Test Voice)' [Step 3/8]: Neural acoustic decoding (56%)... (Voice: Swami Vivekananda (Test Voice) • Progress: 56% • Elapsed: 6.8s)
[  7.4s]  57% | Cloning 'Swami Vivekananda (Test Voice)' [Step 3/8]: Synthesizing vocal timbre (57%)... (Voice: Swami Vivekananda (Test Voice) • Progress: 57% • Elapsed: 7.3s)
[  8.9s]  58% | Cloning 'Swami Vivekananda (Test Voice)' [Step 3/8]: Synthesizing vocal timbre (58%)... (Voice: Swami Vivekananda (Test Voice) • Progress: 58% • Elapsed: 8.8s)
[ 10.0s]  62% | Cloning 'Swami Vivekananda (Test Voice)' [Step 4/8]: Synthesizing vocal timbre (62%)... (Voice: Swami Vivekananda (Test Voice) • Progress: 62% • Elapsed: 9.8s)
[ 11.1s]  63% | Cloning 'Swami Vivekananda (Test Voice)' [Step 4/8]: Synthesizing vocal timbre (63%)... (Voice: Swami Vivekananda (Test Voice) • Progress: 63% • Elapsed: 11.0s)
[ 12.2s]  64% | Cloning 'Swami Vivekananda (Test Voice)' [Step 4/8]: Synthesizing vocal timbre (64%)... (Voice: Swami Vivekananda (Test Voice) • Progress: 64% • Elapsed: 12.1s)
[ 12.9s]  67% | Cloning 'Swami Vivekananda (Test Voice)' [Step 5/8]: Neural acoustic decoding (67%)... (Voice: Swami Vivekananda (Test Voice) • Progress: 67% • Elapsed: 12.8s)
[ 13.7s]  68% | Cloning 'Swami Vivekananda (Test Voice)' [Step 5/8]: Synthesizing vocal timbre (68%)... (Voice: Swami Vivekananda (Test Voice) • Progress: 68% • Elapsed: 13.5s)
[ 14.8s]  69% | Cloning 'Swami Vivekananda (Test Voice)' [Step 5/8]: Synthesizing vocal timbre (69%)... (Voice: Swami Vivekananda (Test Voice) • Progress: 69% • Elapsed: 14.5s)
[ 15.9s]  73% | Cloning 'Swami Vivekananda (Test Voice)' [Step 6/8]: Synthesizing vocal timbre (73%)... (Voice: Swami Vivekananda (Test Voice) • Progress: 73% • Elapsed: 15.8s)
[ 17.3s]  74% | Cloning 'Swami Vivekananda (Test Voice)' [Step 6/8]: Synthesizing vocal timbre (74%)... (Voice: Swami Vivekananda (Test Voice) • Progress: 74% • Elapsed: 17.3s)
[ 18.5s]  75% | Cloning 'Swami Vivekananda (Test Voice)' [Step 6/8]: Synthesizing vocal timbre (75%)... (Voice: Swami Vivekananda (Test Voice) • Progress: 75% • Elapsed: 18.3s)
[ 18.8s]  77% | Cloning 'Swami Vivekananda (Test Voice)' [Step 7/8]: Neural acoustic decoding (77%)... (Voice: Swami Vivekananda (Test Voice) • Progress: 77% • Elapsed: 18.8s)
[ 19.6s]  78% | Cloning 'Swami Vivekananda (Test Voice)' [Step 7/8]: Synthesizing vocal timbre (78%)... (Voice: Swami Vivekananda (Test Voice) • Progress: 78% • Elapsed: 19.5s)
[ 20.7s]  79% | Cloning 'Swami Vivekananda (Test Voice)' [Step 7/8]: Synthesizing vocal timbre (79%)... (Voice: Swami Vivekananda (Test Voice) • Progress: 79% • Elapsed: 20.6s)
[ 21.8s]  83% | Cloning 'Swami Vivekananda (Test Voice)' [Step 8/8]: Neural acoustic decoding (83%)... (Voice: Swami Vivekananda (Test Voice) • Progress: 84% • Elapsed: 21.7s)
[ 22.1s]  84% | Cloning 'Swami Vivekananda (Test Voice)' [Step 8/8]: Synthesizing vocal timbre (84%)... (Voice: Swami Vivekananda (Test Voice) • Progress: 84% • Elapsed: 22.0s)
[ 23.2s]  85% | Cloning 'Swami Vivekananda (Test Voice)' [Step 8/8]: Synthesizing vocal timbre (85%)... (Voice: Swami Vivekananda (Test Voice) • Progress: 85% • Elapsed: 23.0s)
[ 24.4s]  86% | Cloning 'Swami Vivekananda (Test Voice)' [Step 8/8]: Synthesizing vocal timbre (86%)... (Voice: Swami Vivekananda (Test Voice) • Progress: 86% • Elapsed: 24.3s)
[ 25.9s] 100% | Speech synthesis complete for 'Swami Vivekananda (Test Voice)'! (Voice: Swami Vivekananda (Test Voice) • Progress: 100% • Elapsed: 25.9s)
```

## 3. Verified Synthetic TTS Audio Files (`.wav`) in `NEW-Test-Outcomes/`

| Audio File | Duration | Sample Rate | SNR (dB) | Loudness (LUFS) | Peak | Speech Envelope CV | QA Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `e2e_synthesis_output.wav` | 4.96s | 24000 Hz | 35.0 dB | -20.0 LUFS | 0.673 | 0.77 (Natural Speech) | `PASSED` |
| `janiki_cloned_output.wav` | 8.64s | 24000 Hz | 36.8 dB | -13.6 LUFS | 0.994 | 0.70 (Natural Speech) | `PASSED` |
| `kalam_cloned_output.wav` | 10.88s | 24000 Hz | 15.7 dB | -23.8 LUFS | 0.494 | 0.69 (Natural Speech) | `PASSED` |
| `swamiji_cloned_output.wav` | 4.64s | 24000 Hz | 38.1 dB | -20.0 LUFS | 0.668 | 0.89 (Natural Speech) | `PASSED` |
| `swamiji_web_e2e_cloned.wav` | 4.64s | 24000 Hz | 38.1 dB | -20.0 LUFS | 0.668 | 0.89 (Natural Speech) | `PASSED` |

## 4. Visual Evidence & Screenshots Captured

- **`01_initial_studio_view.png`**: Captured during Playwright E2E test flow
- **`02_swamiji_voice_selected.png`**: Captured during Playwright E2E test flow
- **`03_swamiji_progress_early.png`**: Captured during Playwright E2E test flow
- **`04_swamiji_progress_mid_step.png`**: Captured during Playwright E2E test flow
- **`05_swamiji_completed_100pct.png`**: Captured during Playwright E2E test flow
- **`06_aria_prime_preset_completed_100pct.png`**: Captured during Playwright E2E test flow
- **`07_kalam_voice_selected_ready.png`**: Captured during Playwright E2E test flow
- **`08_janaki_voice_selected_ready.png`**: Captured during Playwright E2E test flow
