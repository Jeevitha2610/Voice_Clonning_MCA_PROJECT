---
name: autonomous-testing-debugging
description: Procedures and automated workflows for pytest testing, continuous verification, self-debugging, error isolation, and root-cause repair in Python speech applications. Use when writing tests, debugging failed inference, and verifying audio pipelines.
---

# Autonomous Testing & Self-Repair Workflows

This skill defines mandatory self-testing, verification, and regression prevention rules.

## 1. Multi-Tier Testing Pyramid
1. **Unit Tests (`tests/unit/`)**:
   - `test_audio.py`: Audio format decoding, WAV header verification, corruption handling.
   - `test_security.py`: Path traversal fuzzing, upload boundary checks.
   - `test_db.py`: SQLite transaction atomicity, profile CRUD operations.
2. **Audio & DSP Tests (`tests/audio/`)**:
   - Verify sample rate stability, zero DC offset, peak amplitude bounding.
   - Test EBU R128 loudness matching accuracy within $\pm 0.5\text{ LUFS}$.
3. **Real Inference Tests (`tests/inference/`)**:
   - Load engine weights on host CPU.
   - Run synthesis using an authorized reference audio fixture.
   - Verify output WAV file: non-empty (>1000 bytes), decodable by standard PCM reader, non-zero energy (>0.40).
4. **API Integration Tests (`tests/api/`)**:
   - Use `fastapi.testclient.TestClient` to test full HTTP life-cycle.

## 2. Mandatory Self-Debugging Loop
When a test fails, execute this exact sequence:
1. **Capture Full Diagnostic Traceback**: Isolate the exact exception and frame.
2. **Classify Root Cause**:
   - *Code Defect*: Syntax, type mismatch, logic error.
   - *Dependency / Environment*: Missing package, wheel incompatibility, Python 3.14 deprecation.
   - *Hardware / Platform*: CPU-only limitation, Windows path delimiter issue.
   - *Data / Model*: Corrupted weights, malformed WAV fixture.
3. **Apply Minimal Surgical Fix**: Modify only the offending component.
4. **Run Regression Pass**: Re-execute the failed test plus all previously passing tests.
5. **Record Finding**: Document the failure, root cause, and remedy in `TEST_REPORT.md`.
