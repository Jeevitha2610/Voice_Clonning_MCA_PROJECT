---
name: docling
description: Document parsing, multi-format ingestion, and structural understanding for PDFs, DOCX, PPTX, HTML, audio transcripts, and Markdown. Use when extracting structured text, layout, tables, and document metadata for RAG, voice studio scripting, and agent pipelines.
---

# Docling: Universal Document & Script Parsing

Docling parses diverse and unstructured documents (PDF, DOCX, PPTX, HTML, Whisper audio transcripts, Markdown) into structured, type-safe representations with high fidelity layout and table structure.

## Capabilities

1. **Document Parsing**:
   - Universal document conversion (`PDF`, `DOCX`, `PPTX`, `HTML`, `Audio Transcripts`).
   - Structural layout preservation (headings, reading order, sections, footnotes).
   - Accurate table extraction with column and cell alignment.
2. **Chunking & RAG Preparation**:
   - Semantic chunking respecting document boundaries and hierarchy.
   - Metadata tagging (source, page numbers, timestamps, section tags).
3. **Voice Studio Pipeline Integration**:
   - Ingest script documents, voice actor transcripts, subtitles (SRT/VTT), and screenplay formatting.
   - Clean, normalize, and segment text chunks optimized for zero-shot TTS and speech synthesis models.

## Usage in Python

```python
from docling.document_converter import DocumentConverter

converter = DocumentConverter()
result = converter.convert("path/to/script_or_document.pdf")
doc = result.document

# Export clean Markdown or structured JSON
markdown_text = doc.export_to_markdown()
```

## Best Practices
- Cache parsed document representations locally to prevent repeated parsing.
- Normalize phonemes, acronyms, and SSML tags extracted from screenplay/transcript formats.
- When parsing audio transcripts or dubbing scripts, retain timecodes and speaker labels for multi-speaker synthesis.
