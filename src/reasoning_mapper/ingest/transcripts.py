# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2026 Tucuxi, Inc.
"""Think-aloud sessions: the richest source this tool reads.

Email preserves the decision and, once trust exists, little of the route. Decks
preserve the answer. A think-aloud session over a real problem carries problem,
route and answer together. See docs/THINK_ALOUD.md for how to run one.

Accepts .txt/.md transcripts, .vtt/.srt captions, and audio (.m4a .mp3 .wav)
transcribed locally with faster-whisper (`pip install reasoning-mapper[audio]`).
"""

from __future__ import annotations

import re
from pathlib import Path

from . import insert_text

AUDIO = {".m4a", ".mp3", ".wav", ".mp4", ".aac", ".flac", ".ogg"}
CAPTION_TIME = re.compile(r"^\d{1,2}:\d{2}(:\d{2})?[.,]\d{3}\s+-->\s+.*$")


def read_captions(p: Path) -> str:
    lines = []
    for line in p.read_text(errors="replace").splitlines():
        s = line.strip()
        if not s or s == "WEBVTT" or s.isdigit() or CAPTION_TIME.match(s):
            continue
        if lines and lines[-1] == s:          # captions repeat across cues
            continue
        lines.append(s)
    return "\n".join(lines)


def transcribe(p: Path, model_size: str = "small") -> str:
    try:
        from faster_whisper import WhisperModel
    except ImportError as e:
        raise SystemExit("audio needs: pip install 'reasoning-mapper[audio]'") from e
    model = WhisperModel(model_size, device="auto", compute_type="int8")
    segments, _ = model.transcribe(str(p), vad_filter=True)
    return "\n".join(s.text.strip() for s in segments)


def ingest_transcripts(conn, source: str, path: Path) -> str:
    files = [path] if path.is_file() else sorted(p for p in path.rglob("*") if p.is_file())
    new = 0
    for p in files:
        ext = p.suffix.lower()
        if ext in {".txt", ".md"}:
            text = p.read_text(errors="replace")
        elif ext in {".vtt", ".srt"}:
            text = read_captions(p)
        elif ext in AUDIO:
            cached = p.with_suffix(p.suffix + ".txt")
            if cached.exists():
                text = cached.read_text()
            else:
                text = transcribe(p)
                cached.write_text(text)        # transcription is slow; keep it beside the audio
        else:
            continue
        if text.strip() and insert_text(conn, "sessions", source, p, p.stem, text):
            new += 1
    return f"{source}: {new} new think-aloud sessions"
