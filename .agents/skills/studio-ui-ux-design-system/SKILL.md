---
name: studio-ui-ux-design-system
description: Design system, user experience, and visual design guidelines for high-end creative audio production workstations, voice cloning studios, and AI speech interfaces. Use when designing information architecture, layouts, dark-mode palettes, and studio ergonomics.
---

# Studio UI/UX & Creative Audio Design System

This skill provides design standards, information architecture (IA), and aesthetic principles for building a professional AI voice cloning and audio production studio.

## 1. Information Architecture & Studio Workspace Layout
Audio and voice production applications demand dense, focused workspaces with zero extraneous visual clutter:
- **Three-Zone Workspace Composition:**
  1. *Global Navigation & Session Bar:* Brand identity, engine selector, hardware indicator (CPU/RAM telemetry), and global settings.
  2. *Primary Workflow Canvas:* Contextual workspace for reference recording, prompt voice design, or dubbing timeline.
  3. *Audio Inspector & Library Pane:* Collapsible right-hand panel for saved voice profiles, audio metadata, waveform diagnostics, and WAV export history.
- **Visual Hierarchy & Ergonomics:**
  - Avoid generic SaaS/admin dashboard cards and oversized metric tiles.
  - Prioritize primary action anchors: Record Reference, Synthesize Speech, and Audition Playback.
  - Maintain a strict 4px/8px modular spacing grid throughout all components.

## 2. Visual Design & Theme System
- **Dark-Theme-First Aesthetic:**
  - Audio and creative software operate predominantly in dark environments to minimize eye fatigue during extended editing sessions.
  - *Base Surface:* `#0d1117` / `#161b22` (neutral dark slate; avoid pure black `#000000` to prevent harsh contrast).
  - *Elevated Cards/Panels:* `#1c2128` with subtle border `#30363d` (1px solid).
  - *Primary Accent (Accent / Playback):* `#6366f1` (Indigo) or `#38bdf8` (Cyan) with accessible contrast ratio $\ge 4.5:1$ against dark surfaces.
  - *Audio Indicator Accents:* `#10b981` (Signal OK / Green), `#f59e0b` (Warning / Yellow), `#ef4444` (Clipping / Red).
- **Typography Scale:**
  - Monospace font for numerical telemetry, timecodes, frequencies, sample rates, and decibel levels (`ui-monospace`, `SFMono-Regular`, `Consolas`).
  - Proportional geometric sans-serif for UI labels, titles, and text inputs (`Inter`, `Segoe UI`, `-apple-system`).

## 3. Interaction Design & Workflow Optimization
- **Zero-Friction Audio Ingest:** Drag-and-drop zone with instant visual audio validation (duration, channels, sample rate).
- **Progressive Disclosure:** Advanced neural synthesis knobs (temperature, top_p, flow steps, speed) tucked behind expandable disclosure drawers so novice creators aren't overwhelmed while power users retain deep control.
- **State Feedback:** Definite states for Idle, Ingesting, Analyzing, Synthesizing (with real-time progress percentage), and Playback Ready.
