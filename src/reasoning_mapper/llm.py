# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2026 Tucuxi, Inc.
"""Model backends: local Ollama, the Claude API, and replay (recorded responses,
for tests and the worked example).

Three roles, which should not all be the same model:

    extract   reads episodes and names reasoning moves
    annotate  lists identifiers for redaction
    verify    audits redaction - use a different model FAMILY from annotate, or it
              shares the annotator's blind spots and grades its own work

The cloud backend refuses any text not marked as redacted, and refuses entirely
unless `privacy.allow_cloud` is true.
"""

from __future__ import annotations

import hashlib
import json
import re
import urllib.request
from pathlib import Path

import numpy as np


class CloudRefused(RuntimeError):
    pass


def parse_json(t: str | None):
    """Tolerate prose around the object and a truncated tail."""
    if not t or "{" not in t:
        return None
    frag = t[t.find("{"):]
    try:
        return json.loads(frag[:frag.rfind("}") + 1])
    except ValueError:
        pass
    buf = frag
    if buf.count('"') % 2:
        buf += '"'
    buf = re.sub(r",\s*$", "", buf)
    for _ in range(12):
        buf += "]" if buf.count("[") > buf.count("]") else "}"
        try:
            return json.loads(buf)
        except ValueError:
            continue
    return None


def _post(url: str, body: dict, timeout: int) -> dict:
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


class LLM:
    def __init__(self, project):
        self.m = project["models"]
        self.allow_cloud = bool(project["privacy"]["allow_cloud"])
        self.backend = self.m["backend"]
        self.root = project.root
        self._client = None

    def model_for(self, role: str) -> str:
        if self.backend == "anthropic":
            return self.m["anthropic_model"]
        if self.backend == "replay":
            return "replay"
        name = self.m.get(f"{role}_model") or self.m.get("extract_model")
        if not name:
            raise SystemExit(f"models.{role}_model is not set in rmap.yaml")
        return name

    def _local(self, role: str) -> str:
        name = self.m.get(f"{role}_model")
        if not name:
            raise SystemExit(f"models.{role}_model is not set in rmap.yaml "
                             f"(redaction models always run locally, even with the anthropic backend)")
        return name

    def has_model(self, role: str) -> bool:
        return self.backend == "replay" or bool(self.m.get(f"{role}_model"))

    def complete_json(self, prompt: str, *, role: str, task: str, key: str,
                      redacted: bool, max_tokens: int = 1600):
        """Returns (parsed_or_None, raw_text, model_name).

        Only `extract` may use the cloud. Redaction roles see text before it is
        clean, so they always run locally."""
        backend = self.backend
        if role != "extract" and backend == "anthropic":
            backend = "ollama"
        model = self.model_for(role) if backend == self.backend else self._local(role)
        if backend == "replay":
            return self._replay(task, key)
        if backend == "anthropic":
            if not self.allow_cloud:
                raise CloudRefused("privacy.allow_cloud is false; refusing to send text off this machine")
            if not redacted:
                raise CloudRefused(f"{key}: text has not passed redaction; refusing to send it")
            raw = self._anthropic(model, prompt, max_tokens)
        else:
            # Under the JSON grammar a local model can stall emitting whitespace until
            # the token cap (seen on a few real episodes in a hundred). A little temperature frees
            # most; dropping the grammar frees the rest. Only used after a failure.
            for fmt, temp in (("json", 0), ("json", 0.3), (None, 0)):
                body = {"model": model, "prompt": prompt if fmt else prompt + "\n\nReturn only the JSON object.",
                        "stream": False, "think": False, "keep_alive": self.m["keep_alive"],
                        "options": {"temperature": temp, "num_ctx": self.m["num_ctx"],
                                    "num_predict": max_tokens}}
                if fmt:
                    body["format"] = fmt
                raw = _post(f"{self.m['host']}/api/generate", body, self.m["timeout"]).get("response") or ""
                if parse_json(raw) is not None:
                    break
        if self.m.get("record_dir"):
            self._record(task, key, raw)
        return parse_json(raw), raw, model

    def _path(self, base: str, task: str, key: str) -> Path:
        d = Path(base)
        if not d.is_absolute():
            d = self.root / d
        return d / task / (re.sub(r"[^\w.-]", "_", key) + ".json")

    def _record(self, task: str, key: str, raw: str) -> None:
        """Keep every real response: an audit trail, and replay fixtures for tests."""
        p = self._path(self.m["record_dir"], task, key)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(raw)

    def _anthropic(self, model: str, prompt: str, max_tokens: int) -> str:
        if self._client is None:
            try:
                import anthropic
            except ImportError as e:
                raise SystemExit("pip install 'reasoning-mapper[anthropic]'") from e
            self._client = anthropic.Anthropic()
        msg = self._client.messages.create(
            model=model, max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt + "\n\nReturn only the JSON object."}])
        return "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")

    def _replay(self, task: str, key: str):
        p = self._path(self.m["replay_dir"] or "replay", task, key)
        if not p.exists():
            return None, "", "replay"
        raw = p.read_text()
        return parse_json(raw), raw, "replay"


class Embedder:
    """`ollama` for real use. `hashing` is a deterministic, dependency-free
    character-n-gram embedding for tests and the worked example; it measures
    spelling, not meaning, and should fail the known-answer check on real data."""

    def __init__(self, project, dims: int = 1024):
        self.m = project["models"]
        self.kind = self.m["embed_backend"]
        self.dims = dims

    @property
    def name(self) -> str:
        return f"{self.kind}:{self.m['embed_model']}" if self.kind == "ollama" else self.kind

    def __call__(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, self.dims), dtype=np.float32)
        if self.kind == "hashing":
            V = np.vstack([self._hash(t) for t in texts])
        elif self.kind == "ollama":
            out = []
            for i in range(0, len(texts), 64):
                d = _post(f"{self.m['host']}/api/embed",
                          {"model": self.m["embed_model"], "input": texts[i:i + 64],
                           "keep_alive": self.m["keep_alive"]},
                          self.m["timeout"])
                out.extend(d["embeddings"])
            V = np.array(out, dtype=np.float32)
        else:
            raise SystemExit(f"unknown embed_backend {self.kind!r}")
        return V / (np.linalg.norm(V, axis=1, keepdims=True) + 1e-9)

    def _hash(self, t: str) -> np.ndarray:
        v = np.zeros(self.dims, dtype=np.float32)
        t = f" {t.lower()} "
        grams = [t[i:i + n] for n in (3, 4) for i in range(len(t) - n + 1)]
        grams += [f"w:{w}" for w in re.findall(r"[a-z0-9]+", t)] * 2
        for g in grams:
            h = int(hashlib.md5(g.encode()).hexdigest()[:8], 16)
            v[h % self.dims] += 1.0 if (h >> 31) & 1 else -1.0
        return v
