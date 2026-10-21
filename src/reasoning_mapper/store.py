# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2026 Tucuxi, Inc.
"""SQLite store. One file per project, holding raw text: keep it off shared drives
and out of version control."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS messages (
    id             INTEGER PRIMARY KEY,
    source         TEXT NOT NULL,          -- which configured source it came from
    source_ref     TEXT NOT NULL,          -- position within that source
    message_id     TEXT,
    in_reply_to    TEXT,
    refs           TEXT DEFAULT '[]',
    subject        TEXT,
    date           TEXT,                   -- ISO 8601, UTC where known
    from_address   TEXT,
    from_name      TEXT,
    to_addresses   TEXT DEFAULT '[]',
    cc_addresses   TEXT DEFAULT '[]',
    folder         TEXT,
    body_text      TEXT DEFAULT '',
    authored_text  TEXT,                   -- body with quoted replies removed
    authored_chars INTEGER,
    is_expert      INTEGER DEFAULT 0,
    ingest_note    TEXT,                   -- why a field could not be read, if one could not
    UNIQUE (source, source_ref)
);
CREATE TABLE IF NOT EXISTS documents (
    id                 INTEGER PRIMARY KEY,
    source             TEXT NOT NULL,
    path               TEXT NOT NULL,
    title              TEXT,
    text               TEXT NOT NULL,
    authored_by_expert INTEGER DEFAULT 1,
    sha256             TEXT UNIQUE
);
CREATE TABLE IF NOT EXISTS sessions (
    id      INTEGER PRIMARY KEY,
    source  TEXT NOT NULL,
    path    TEXT NOT NULL,
    title   TEXT,
    text    TEXT NOT NULL,
    sha256  TEXT UNIQUE
);
CREATE TABLE IF NOT EXISTS threads (
    thread_key            TEXT PRIMARY KEY,
    n_messages            INTEGER,
    first_date            TEXT,
    last_date             TEXT,
    episode_type          TEXT,
    expert_authored_chars INTEGER
);
CREATE TABLE IF NOT EXISTS thread_members (
    thread_key TEXT NOT NULL,
    message    INTEGER NOT NULL REFERENCES messages(id),
    position   INTEGER NOT NULL,
    PRIMARY KEY (thread_key, message)
);
CREATE TABLE IF NOT EXISTS episodes (
    id            TEXT PRIMARY KEY,        -- thread:<key> | doc:<id>:<chunk> | session:<id>:<chunk>
    kind          TEXT NOT NULL,           -- thread | document | session
    episode_type  TEXT,
    n_turns       INTEGER,
    text          TEXT NOT NULL,           -- assembled, unredacted
    redacted      TEXT,
    legend        TEXT,                    -- tag -> original; local audit only
    residual      TEXT,                    -- identifiers the verifier still found
    verified      INTEGER                  -- 1 clean, 0 residuals found, NULL not yet checked
);
CREATE TABLE IF NOT EXISTS extractions (
    episode_id     TEXT NOT NULL REFERENCES episodes(id),
    prompt_version TEXT NOT NULL,
    model          TEXT,
    output         TEXT,
    error          TEXT,
    PRIMARY KEY (episode_id, prompt_version)
);
CREATE TABLE IF NOT EXISTS items (
    id         INTEGER PRIMARY KEY,
    episode_id TEXT NOT NULL REFERENCES episodes(id),
    kind       TEXT NOT NULL,              -- move | consideration
    name       TEXT NOT NULL,
    detail     TEXT
);
CREATE TABLE IF NOT EXISTS calibration (
    instrument TEXT PRIMARY KEY,
    passed     INTEGER NOT NULL,
    score      INTEGER,
    total      INTEGER,
    detail     TEXT,
    at         TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_messages_mid ON messages(message_id);
CREATE INDEX IF NOT EXISTS idx_items_kind ON items(kind);
"""


def connect(path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(SCHEMA)
    return conn


def dumps(v) -> str:
    return json.dumps(v, ensure_ascii=False, default=str)


def loads(v, default=None):
    if v is None:
        return default
    try:
        return json.loads(v)
    except (TypeError, ValueError):
        return default
