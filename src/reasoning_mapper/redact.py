# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2026 Tucuxi, Inc.
"""Input-side redaction, with an independent audit.

Why input-side
--------------
Asking the extraction model to "replace names with [PERSON]" in its output works
on short snippets and fails on long, entity-dense episodes - on the archive this
was developed on it failed on every episode tested at episode scale. A model cannot
emit a name it was never shown, so the INPUT is redacted.

Three layers
------------
1. A vocabulary floor built from the corpus itself (correspondent names, address
   local-parts, mail domains, recurring capitalised non-dictionary tokens), so
   coverage is auditable. Strong on mail, where the identifiers ARE the
   correspondents; weak on documents, which name people and companies merely
   discussed.
2. A local model lists identifiers (high recall; over-flagging is cheap), and
   they are replaced deterministically.
3. A model from a DIFFERENT family audits the result without seeing the
   annotator's list. Whatever it still finds is replaced and audited once more.
   An episode is `verified` only when the audit comes back clean.

Aliases are stable within an episode ([PERSON_1], [COMPANY_A]) rather than flat
tags: reasoning about "where comparable companies sit" is ABOUT telling companies
apart, and a single [COMPANY] tag collapses "we are stricter than they are" into
"we are stricter than us". Numbers, dates and thresholds are never tagged - they
carry no identity and they are what makes a procedure discriminating.
"""

from __future__ import annotations

import collections
import functools
import re

from .store import dumps, loads

COMMON = set("""the and for you are but not with this that from have has had was were will would
can could should may might must shall about after all also any because been before being below
between both each few further here how into itself more most other our out over own same some
such than then there these they through under until very what when where which while who whom why
your yours just don now his her him she he it its them their we us me my no of on or so to up
re fw fwd cc bcc subject sent date please thanks thank regards best kind hi hello dear sincerely
attached attachment email mail team project program note issue risk case draft review call meeting
update status question answer yes ok okay good great let know need want think see first second
third next last new old inc llc ltd corp corporation company group department division office
monday tuesday wednesday thursday friday saturday sunday today tomorrow yesterday week month year
january february march april june july august september october november december""".split())

MAIL_PROVIDERS = {"gmail", "googlemail", "yahoo", "hotmail", "outlook", "live", "msn", "aol",
                  "icloud", "me", "mac", "proton", "protonmail", "fastmail", "gmx", "zoho", "mail"}
TLDISH = {"com", "net", "org", "co", "uk", "de", "jp", "cn", "io", "edu", "gov", "us", "ca",
          "au", "fr", "in", "mail", "email", "corp", "local", "inc"}

EMAIL = re.compile(r"[\w.+-]+@[\w.-]+\.\w+")
PHONE = re.compile(r"\b(?:\+?\d{1,2}[\s.-])?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}\b")
URL = re.compile(r"https?://\S+|www\.\S+")
# Models list "2011", "(3)" or "99.9 percent" as identifiers; numbers carry no
# identity and are what makes a procedure specific. A name has a capital letter.
NAMELIKE = re.compile(r"[A-Z]")
TAG = re.compile(r"\[(?:PERSON|COMPANY|PRODUCT|IDENT|EMAIL)_[A-Z0-9]+\]|\[(?:URL|PHONE)\]")


@functools.lru_cache(maxsize=1)
def english() -> frozenset:
    """System word list, if there is one: anything in it is not a codename."""
    for p in ("/usr/share/dict/words", "/usr/dict/words"):
        try:
            with open(p) as fh:
                return frozenset(w.strip().lower() for w in fh if len(w.strip()) >= 3)
        except OSError:
            continue
    return frozenset()


def build_vocab(conn, extra=(), keep=()) -> dict[str, set[str]]:
    keep = {k.lower() for k in keep}
    person, company = collections.Counter(), collections.Counter()
    for (n,) in conn.execute("SELECT from_name FROM messages WHERE from_name IS NOT NULL"):
        for p in re.split(r"[,\s]+", n.strip()):
            if len(p) >= 3 and p.isalpha():
                person[p.lower()] += 1
    addrs = [r[0] for r in conn.execute("SELECT from_address FROM messages WHERE from_address IS NOT NULL")]
    for col in ("to_addresses", "cc_addresses"):
        for (v,) in conn.execute(f"SELECT {col} FROM messages"):
            addrs += loads(v, [])
    for a in addrs:
        local, _, dom = str(a).lower().partition("@")
        parts = [p for p in dom.split(".") if p not in TLDISH]
        if parts and parts[-1] not in MAIL_PROVIDERS:
            company[parts[-1]] += 1
        for p in re.split(r"[.\-_+]", local):
            if len(p) >= 3 and p.isalpha():
                person[p] += 1
    # codenames: capitalised almost always, not English, and recurring
    cap, low = collections.Counter(), collections.Counter()
    texts = [r[0] for r in conn.execute("SELECT authored_text FROM messages WHERE authored_text IS NOT NULL")]
    texts += [r[0] for r in conn.execute("SELECT text FROM documents")]
    texts += [r[0] for r in conn.execute("SELECT text FROM sessions")]
    for t in texts:
        for m in re.finditer(r"\b([A-Za-z][A-Za-z0-9]{3,})\b", t or ""):
            w = m.group(1)
            (cap if w[0].isupper() else low)[w.lower()] += 1
    EN = english()
    # Real first names are often dictionary words (Grant, Chase, Bill). They are
    # NOT filtered by the dictionary: over-redaction is cheap, a leaked name is not.
    P = {t for t, c in person.items() if c >= 2 and t not in COMMON and t not in keep}
    C = {t for t in company if len(t) >= 3 and t not in COMMON and t not in EN and t not in keep}
    PR = {w for w, c in cap.items() if c >= 3 and w not in EN and w not in COMMON
          and low.get(w, 0) <= 0.25 * c and w not in P and w not in C and w not in keep}
    X = {e.lower() for e in extra}
    return {"PERSON": P, "COMPANY": C, "PRODUCT": PR, "IDENT": X}


class Redactor:
    """Consistent pseudonymisation, stable within one episode."""

    def __init__(self, vocab: dict[str, set[str]]):
        self.map: dict[tuple[str, str], str] = {}
        self.counts = collections.Counter()
        self.rx = []
        for kind in ("IDENT", "COMPANY", "PRODUCT", "PERSON"):    # most specific first
            words = sorted((w for w in vocab.get(kind, ()) if len(w) >= 3), key=len, reverse=True)
            if words:
                # Any casing ("Osprey", "OSPREY", "kWillow"), but a vocabulary word must
                # carry a capital where it occurs: lower-case "grant"/"chase" are verbs.
                alts = "|".join(re.escape(w) for w in words)
                self.rx.append((kind, re.compile(rf"(?<![\w\[])({alts})(?![\w\]])", re.I)))

    def alias(self, kind: str, key: str) -> str:
        k = (kind, key.lower())
        if k not in self.map:
            self.counts[kind] += 1
            n = self.counts[kind]
            self.map[k] = (f"[COMPANY_{chr(64 + n)}]" if kind == "COMPANY" and n <= 26
                           else f"[{kind}_{n}]")
        return self.map[k]

    def replace_names(self, text: str, names: dict[str, list[str]]) -> str:
        items = [(nm, kind) for kind, lst in names.items() for nm in lst]
        for nm, kind in sorted(items, key=lambda x: -len(x[0])):   # "Jane Q. Doe" before "Jane"
            if not re.search(r"[A-Za-z0-9]", nm) or TAG.fullmatch(nm):
                continue
            pat = re.compile(r"(?<![\w\[])" + re.escape(nm) + r"(?![\w\]])", re.I)
            if pat.search(text):
                text = pat.sub(self.alias(kind, nm), text)
        return text

    def floor(self, text: str) -> str:
        text = EMAIL.sub(lambda m: self.alias("EMAIL", m.group(0)), text)
        text = URL.sub("[URL]", text)
        text = PHONE.sub("[PHONE]", text)
        for kind, rx in self.rx:
            text = rx.sub(lambda m, k=kind: self.alias(k, m.group(1))
                          if k == "IDENT" or not m.group(1).islower() else m.group(1), text)
        return text

    def legend(self) -> dict[str, str]:
        return {v: k[1] for k, v in self.map.items()}


ANNOTATE = """List every identifier in this text. Be exhaustive: missing one is far worse than including something harmless.

Include: personal names (including first-name-only and signatures), company, firm, agency and organisation names, product, project and programme names, internal codenames (short alphanumeric tags count), street addresses, and case, ticket, docket or account numbers.

Do NOT include: job titles, generic words, dates, amounts, or ordinary terms of the profession.

Return ONLY JSON, names exactly as they appear:
{{"people": [], "companies": [], "products": [], "other_identifiers": []}}

TEXT:
{body}"""

VERIFY = """This text has been redacted: identifiers were replaced with tags like [PERSON_1], [COMPANY_A], [PRODUCT_3].

Find anything that ESCAPED redaction: any personal name, company or organisation name, product name, internal codename, address, or case/ticket number still visible in plain text. Ignore the bracketed tags; they are correct. Do not report job titles, roles, or public laws and standards.

Return ONLY JSON:
{{"residual_identifiers": [], "clean": true}}

REDACTED TEXT:
{body}"""

CAT2KIND = {"people": "PERSON", "companies": "COMPANY", "products": "PRODUCT",
            "other_identifiers": "IDENT"}


def chunks(text: str, size: int = 5000, overlap: int = 400):
    i = 0
    while i < len(text):
        yield i, text[i:i + size]
        if i + size >= len(text):
            break
        i += size - overlap


def annotate(llm, eid: str, text: str) -> dict[str, list[str]]:
    found = collections.defaultdict(set)
    for n, (_, ch) in enumerate(chunks(text)):
        j, _, _ = llm.complete_json(ANNOTATE.format(body=ch), role="annotate",
                                    task="annotate", key=f"{eid}#{n}", redacted=False, max_tokens=1500)
        for cat, kind in CAT2KIND.items():
            for v in (j or {}).get(cat) or []:
                v = str(v).strip()
                if 2 < len(v) < 80 and NAMELIKE.search(v):
                    found[kind].add(v)
    return {k: sorted(v) for k, v in found.items()}


def verify(llm, eid: str, text: str, keep=(), attempt: int = 0) -> list[str] | None:
    """Residual identifiers, or None if the audit itself failed. A verifier that
    returned nothing has not said the text is clean."""
    keep = {k.lower() for k in keep}
    out = set()
    for n, (_, ch) in enumerate(chunks(text)):
        j, _, _ = llm.complete_json(VERIFY.format(body=ch), role="verify", task="verify",
                                    key=f"{eid}#{attempt}#{n}", redacted=True, max_tokens=900)
        if not isinstance(j, dict) or "residual_identifiers" not in j:
            return None
        for v in j.get("residual_identifiers") or []:
            v = str(v).strip()
            # only count what is really there, and never a tag
            if (2 < len(v) < 80 and NAMELIKE.search(v) and not _kept(v, keep) and not TAG.search(v)
                    and re.search(rf"(?<![\w]){re.escape(v)}(?![\w])", text)):
                out.add(v)
    return sorted(out)


def _kept(v: str, keep) -> bool:
    """A listed entity that is, or sits inside, a keep term ("the Clean Air Act")."""
    v = v.lower()
    return any(k == v or k in v or v in k for k in keep)


def _mask(text: str, keep) -> tuple[str, list[str]]:
    """Hide keep terms from every replacement pass; vocabulary words inside a
    statute's name would otherwise be tagged one by one."""
    held: list[str] = []
    for k in sorted(keep, key=len, reverse=True):
        def hold(m):
            held.append(m.group(0))
            return f"\x00{len(held) - 1}\x00"
        text = re.sub(rf"(?<![\w]){re.escape(k)}(?![\w])", hold, text, flags=re.I)
    return text, held


def _unmask(text: str, held: list[str]) -> str:
    return re.sub(r"\x00(\d+)\x00", lambda m: held[int(m.group(1))], text)


def redact_episode(llm, vocab, eid: str, text: str, keep=(), use_models: bool = True):
    """Returns (redacted, legend, residual, verified)."""
    r = Redactor(vocab)
    kept = {x.lower() for x in keep}
    out, held = _mask(text, kept)
    if use_models:
        found = {k: [v for v in vs if not _kept(v, kept)]
                 for k, vs in annotate(llm, eid, text).items()}
        out = r.replace_names(out, found)
    out = _unmask(r.floor(out), held)
    if not use_models:
        return out, r.legend(), [], None
    resid = verify(llm, eid, out, kept)
    if resid:
        masked, held = _mask(out, kept)
        out = _unmask(r.replace_names(masked, {"IDENT": resid}), held)
        resid = verify(llm, eid, out, kept, attempt=1)
    if resid is None:
        return out, r.legend(), ["verifier gave no usable answer"], None
    return out, r.legend(), resid, (0 if resid else 1)


def run(conn, project, llm, limit: int | None = None, redo: bool = False,
        types=None, sample: int | None = None, seed: int = 0) -> dict:
    """Redact the episode types `extract` reads (by default). `sample` draws a
    seeded random subset, for a first pass over a large archive."""
    import random
    from .episodes import EXTRACT_BY_DEFAULT
    types = list(types or EXTRACT_BY_DEFAULT)
    priv = project["privacy"]
    vocab = build_vocab(conn, priv["extra_identifiers"], priv["keep_terms"])
    use_models = llm.has_model("annotate") and llm.has_model("verify")
    rows = conn.execute(
        f"""SELECT id, text FROM episodes WHERE episode_type IN ({','.join('?' * len(types))})
            {"" if redo else "AND redacted IS NULL"} ORDER BY id""", types).fetchall()
    if sample and sample < len(rows):
        rows = sorted(random.Random(seed).sample(rows, sample), key=lambda r: r["id"])
    if limit:
        rows = rows[:limit]
    stats = collections.Counter()
    for row in rows:
        red, legend, resid, ok = redact_episode(llm, vocab, row["id"], row["text"],
                                                priv["keep_terms"], use_models)
        conn.execute("UPDATE episodes SET redacted=?, legend=?, residual=?, verified=? WHERE id=?",
                     (red, dumps(legend), dumps(resid), ok, row["id"]))
        stats["clean" if ok == 1 else "residual" if ok == 0 else "unverified"] += 1
        conn.commit()
    return {"vocabulary": {k: len(v) for k, v in vocab.items()}, "models": use_models, **stats}
