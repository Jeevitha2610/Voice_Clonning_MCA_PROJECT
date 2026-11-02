---
name: security-performance-audit
description: Protocols for application security, voice consent verification, ethical voice cloning guardrails, path traversal prevention, hardware profiling, and performance benchmarks. Use during security audits, resource optimization, and compliance verification.
---

# Security, Ethics & Performance Auditing

This skill defines mandatory security controls, ethical voice cloning policies, and performance profiling guidelines.

## 1. Ethical Voice Cloning & Consent Controls
- **Explicit Consent Logging**: Every created voice profile must record an explicit consent declaration, timestamp, and speaker authorization ID.
- **Reference Preservation**: Original reference audio must never be overwritten or mutated.
- **AI-Generated Speech Disclosure**: Audio metadata chunks (INFO chunk / ID3 tags / AudioSeal watermark) must mark synthesized files as synthetic media.

## 2. Security Hardening
- **Path Traversal Defense**: Resolve all paths relative to designated application roots; reject paths containing `..`, null bytes, or non-canonical separators.
- **Upload Hardening**: Restrict file extensions to `.wav`, `.mp3`, `.ogg`, `.flac`; enforce maximum file size (25 MB); verify binary magic numbers.
- **Zero-Network Confidentiality**: Ensure no user audio or reference recordings are ever transmitted to external third-party cloud APIs unless explicitly enabled.

## 3. Hardware & Performance Profiling
- **Real-Time Factor (RTF)**: $\text{RTF} = \frac{\text{Generation Time (s)}}{\text{Audio Duration (s)}}$.
  - Target RTF on CPU: $\text{RTF} \le 1.0$ (faster than real-time playback).
- **Memory Footprint**: Peak memory consumption during inference must not exceed 2.0 GB.
- **Latency**: First-packet latency $\le 800\text{ms}$ for real-time streaming preview.
