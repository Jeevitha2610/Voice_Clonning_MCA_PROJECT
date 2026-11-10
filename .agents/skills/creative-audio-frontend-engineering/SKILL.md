---
name: creative-audio-frontend-engineering
description: Engineering guidelines for building creative audio web and desktop interfaces, Web Audio API integration, HTML5 Canvas waveform visualization, media scrubbers, drag-and-drop file ingestion, and accessible keyboard navigation. Use when implementing frontend audio components.
---

# Creative Audio Frontend Engineering & Component Architecture

This skill governs the frontend implementation of real-time audio players, visualizers, file uploaders, and accessible controls.

## 1. Web Audio & Waveform Visualization
- **Canvas Waveform Rendering:**
  - High-performance, 60fps rendering using HTML5 `<canvas>` with `requestAnimationFrame`.
  - Draw precomputed audio RMS peak blocks for static waveforms; draw smoothed frequency bins for live audition.
  - Interactive scrubbing: Clicking or dragging across the waveform sets `audio.currentTime` with sub-frame accuracy.
- **Audio Scrubber & Transport Bar:**
  - Standard audio controls: Play/Pause (Spacebar), Loop Toggle, Playback Rate ($0.5\times\text{--}2.0\times$), Timecode (`00:00.000`), and Direct WAV Download.
  - Non-blocking audio decode: Read binary chunks using `AudioContext.decodeAudioData` in asynchronous background promises.

## 2. Component Architecture & State Management
- **Modular Component Breakdown:**
  - `VoiceProfileSelector`: Dropdown/grid displaying authorized voice avatars, language badges, and timbre previews.
  - `ReferenceAudioUploader`: Drag-and-drop target accepting `.wav`, `.mp3`, `.flac`, checking file size limit ($\le 25\text{MB}$), and decoding headers client-side.
  - `SynthesisWorkspace`: Multi-line text entry with character counter, speed slider, and language selector.
  - `AudioPreviewInspector`: Waveform visualizer, EBU R128 compliance badge, and WAV export trigger.
- **Micro-Interactions & Restrained Motion:**
  - Smooth 150ms–200ms transitions (`cubic-bezier(0.16, 1, 0.3, 1)`) for panel collapses and button states.
  - Pulsing subtle glowing border on active audio recording/playback; avoid distracting layout-shifting animations.

## 3. Accessibility & Keyboard Navigation (WCAG 2.1 AA)
- **Keyboard Shortcuts:**
  - `Space`: Toggle Play/Pause on active audio.
  - `Ctrl + Enter` / `Cmd + Enter`: Trigger speech synthesis.
  - `Escape`: Cancel modal or dismiss upload drawer.
- **ARIA Standards:**
  - Ensure all custom sliders have `role="slider"`, `aria-valuemin`, `aria-valuemax`, and `aria-valuenow`.
  - Accessible names on all audio transport buttons (`aria-label="Play reference recording"`).
