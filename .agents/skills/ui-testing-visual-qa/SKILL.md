---
name: ui-testing-visual-qa
description: Testing protocols and automation procedures for frontend interfaces, Playwright browser automation, visual regression screenshot comparison, responsive viewport validation, and accessibility compliance testing. Use when verifying user interfaces.
---

# UI Testing, Visual Regression & Frontend QA

This skill defines automated verification procedures for creative audio and voice studio user interfaces.

## 1. Automated Browser Testing with Playwright
- **Core Workflow Testing:**
  1. *Profile Creation Flow:* Upload mock reference audio $\rightarrow$ fill metadata $\rightarrow$ verify profile card appears in inspector.
  2. *Synthesis Flow:* Enter prompt text $\rightarrow$ select voice $\rightarrow$ trigger synthesis $\rightarrow$ assert progress bar reaches 100% $\rightarrow$ assert audio element is populated and playable.
  3. *Error State Handling:* Upload corrupted file $\rightarrow$ assert user-friendly error banner appears without console unhandled exceptions.

## 2. Visual Regression & Responsive Matrix
- **Pixel-Diff Testing:**
  - Capture baseline screenshots of primary views (Dark Theme and Light Theme).
  - Assert visual drift threshold $\le 0.2\%$ across component updates.
- **Viewport Testing Matrix:**
  - Desktop Studio: $1920\times 1080$, $1440\times 900$.
  - Compact Laptop / Windowed App: $1280\times 800$, $1024\times 768$.
  - Confirm collapsible sidebars maintain usable workflow canvas without horizontal scrollbars.

## 3. Automated Accessibility Auditing
- Execute automated WCAG 2.1 AA audits using `@axe-core/playwright` or equivalent.
- Zero critical violations allowed on color contrast, focus rings, or button accessibility labels.
