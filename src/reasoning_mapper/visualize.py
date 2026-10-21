# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2026 Tucuxi, Inc.
"""Render map/patterns.yaml as an interactive 3D orchestration graph (one HTML file),
and as a Mermaid flowchart (graph.mmd) for a README or anywhere else that renders Mermaid.

Tier 3 patterns are the hubs. Edges are the relationships the map records:
orchestration (tier 3 -> the tier 1/2 patterns it calls on), works_with between
tier 3 patterns, and, off by default, raw co-occurrence. Links that `rmap link
--judge` proposed are drawn in their own colour, so they can be reviewed apart
from links the episodes support. Patterns nothing orchestrates are flagged.

The page embeds the map and nothing else. It loads 3d-force-graph, three and
three-spritetext from a CDN, so it needs a network connection to draw; no map
data is sent anywhere. The output is deterministic, so it can be diffed.
"""

from __future__ import annotations

import json
from pathlib import Path

from .mapping import load_map

LIBS = ["https://unpkg.com/three@0.160.0/build/three.min.js",
        "https://unpkg.com/three-spritetext@1.8.2/dist/three-spritetext.min.js",
        "https://unpkg.com/3d-force-graph@1.73.0/dist/3d-force-graph.min.js"]


def graph_data(m: dict) -> dict:
    pats = {p["id"]: p for p in m.get("patterns") or []}
    nodes, links, seen = [], [], set()

    def basis(a, b):
        lb = (pats[a].get("link_basis") or {}).get(b) or (pats[b].get("link_basis") or {}).get(a) or {}
        return {k: lb[k] for k in ("shared_episodes", "lift", "judged") if k in lb}

    def add(kind, a, b):
        key = (kind, *sorted((a, b))) if kind != "orchestrates" else (kind, a, b)
        if a in pats and b in pats and a != b and key not in seen:
            seen.add(key)
            bs = basis(a, b)
            links.append({"source": a, "target": b, "kind": kind, "judged": "judged" in bs, "basis": bs})

    for a, p in pats.items():
        if p.get("tier") == 3:
            for b in p.get("source_skills") or []:
                add("orchestrates", a, b)
            for b in p.get("works_with") or []:
                add("works_with", a, b)
        else:
            for b in p.get("orchestrated_by") or []:
                add("orchestrates", b, a)
    for a, p in pats.items():
        for b in p.get("co_occurs_with") or []:
            if not any(k[0] != "co_occurs" and set(k[1:]) == {a, b} for k in seen):
                add("co_occurs", a, b)

    orchestrated = {l["target"] for l in links if l["kind"] == "orchestrates"}
    orchestrating = {l["source"] for l in links if l["kind"] == "orchestrates"}
    for a, p in pats.items():
        t = p.get("tier")
        nodes.append({
            "id": a, "tier": t, "name": p.get("name") or a,
            "description": (p.get("description") or "").strip(),
            "when": (p.get("when_to_apply") or "").strip() if isinstance(p.get("when_to_apply"), str)
                    else p.get("when_to_apply") or "",
            "steps": p.get("steps") or [],
            "aligns": p.get("aligns_with") or [],
            "episodes": ((p.get("support") or {}).get("episodes")) or 0,
            "orphan": (t in (1, 2) and a not in orchestrated) or (t == 3 and a not in orchestrating),
        })
    return {"expert": m.get("expert_label") or "the expert", "nodes": nodes, "links": links}


def render(m: dict) -> str:
    data = json.dumps(graph_data(m), ensure_ascii=False, sort_keys=True).replace("</", "<\\/")
    scripts = "\n".join(f'<script src="{u}"></script>' for u in LIBS)
    return PAGE.replace("/*DATA*/null", data).replace("<!--LIBS-->", scripts)


def mermaid(m: dict) -> str:
    """The same graph as a Mermaid flowchart, for places that render Mermaid but not
    JavaScript (a GitHub README). Tier 3 on top, coloured amber, tier 2 green and
    tier 1 blue (the 3D page uses the same colours); solid arrows are orchestration from
    episodes, dashed arrows are model-proposed. works_with links between tier 3
    peers are left out: Mermaid would rank one peer above the other."""
    g = graph_data(m)
    ids = {n["id"]: f"n{i}" for i, n in enumerate(g["nodes"])}
    label = lambda s: s.replace('"', "#quot;")
    out = ["flowchart TB"]
    # colour carries the tier: subgraph boxes put their titles where the arrows enter
    for t in (3, 2, 1):
        out += [f'  {ids[n["id"]]}["{label(n["name"])}"]' for n in g["nodes"] if n["tier"] == t]
    for l in g["links"]:
        a, b = ids[l["source"]], ids[l["target"]]
        if l["kind"] == "orchestrates":
            out.append(f"  {a} -.->|proposed| {b}" if l["judged"] else f"  {a} --> {b}")
    out += ["  classDef t3 fill:#f2b84b,stroke:#9a6b10,color:#1d1d1b",
            "  classDef t2 fill:#7bd389,stroke:#2e7d4f,color:#1d1d1b",
            "  classDef t1 fill:#5aa9e6,stroke:#245f8f,color:#1d1d1b",
            "  classDef flagged stroke:#d33,stroke-width:3px"]
    for t in (3, 2, 1):
        ns = [ids[n["id"]] for n in g["nodes"] if n["tier"] == t]
        if ns:
            out.append(f"  class {','.join(ns)} t{t}")
    flagged = [ids[n["id"]] for n in g["nodes"] if n["orphan"]]
    if flagged:
        out.append(f"  class {','.join(flagged)} flagged")
    return "\n".join(out) + "\n"


def write(map_path: Path, out: Path) -> dict:
    m = load_map(map_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(m))
    out.with_suffix(".mmd").write_text(mermaid(m))
    g = graph_data(m)
    kinds = {}
    for l in g["links"]:
        kinds[l["kind"]] = kinds.get(l["kind"], 0) + 1
    return {"patterns": len(g["nodes"]), "links": kinds,
            "judged links": sum(l["judged"] for l in g["links"]),
            "flagged (unorchestrated / orchestrating nothing)": sum(n["orphan"] for n in g["nodes"]),
            "wrote": [str(out), str(out.with_suffix(".mmd"))]}


PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Reasoning Map</title>
<style>
:root { --bg:#0e1116; --panel:rgba(20,24,31,.92); --ink:#e7e9ee; --muted:#9aa3b2; --line:#2a313d;
        --t1:#5aa9e6; --t2:#7bd389; --t3:#f2b84b; --judged:#e07be0; --works:#f2b84b; --co:#6b7486; --warn:#ff6b6b; }
* { box-sizing:border-box; }
html, body { margin:0; height:100%; background:var(--bg); color:var(--ink);
             font:14px/1.45 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; overflow:hidden; }
#graph { position:fixed; inset:0; }
.box { position:fixed; background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:12px 14px;
       backdrop-filter:blur(6px); }
#controls { top:12px; left:12px; width:250px; max-height:calc(100% - 24px); overflow:auto; }
#controls h1 { font-size:15px; margin:0 0 2px; }
#controls .sub { color:var(--muted); font-size:12px; margin-bottom:10px; }
#controls h2 { font-size:11px; text-transform:uppercase; letter-spacing:.06em; color:var(--muted); margin:12px 0 6px; }
label.row { display:flex; align-items:center; gap:8px; margin:4px 0; cursor:pointer; }
.sw { width:12px; height:12px; border-radius:50%; display:inline-block; }
.ln { width:18px; height:3px; border-radius:2px; display:inline-block; }
input[type=search] { width:100%; font:inherit; color:var(--ink); background:#0b0e13; border:1px solid var(--line);
                     border-radius:6px; padding:5px 8px; }
button { font:inherit; color:var(--ink); background:#1b212b; border:1px solid var(--line); border-radius:6px;
         padding:4px 10px; cursor:pointer; }
#panel { top:12px; right:12px; width:340px; max-height:calc(100% - 24px); overflow:auto; display:none; }
#panel h3 { margin:0 0 4px; font-size:16px; }
#panel .tier { font-size:12px; color:var(--muted); }
#panel h4 { font-size:11px; text-transform:uppercase; letter-spacing:.06em; color:var(--muted); margin:12px 0 4px; }
#panel ol, #panel ul { margin:0; padding-left:18px; }
#panel a { color:var(--ink); text-decoration:underline dotted; cursor:pointer; }
#panel .why { color:var(--muted); font-size:12px; }
.flag { color:var(--warn); font-size:12px; margin-top:6px; }
#close { float:right; }
#nolib { position:fixed; inset:0; display:none; align-items:center; justify-content:center; color:var(--muted); }
@media (max-width:700px) { #controls { width:calc(100% - 24px); max-height:40%; } #panel { top:auto; bottom:12px; width:calc(100% - 24px); max-height:50%; } }
</style>
<!--LIBS-->
</head>
<body>
<div id="graph"></div>
<div id="nolib">The 3D libraries did not load. This page needs a network connection to fetch them.</div>
<div id="controls" class="box">
  <h1>Reasoning map</h1>
  <div class="sub" id="stats"></div>
  <input id="q" type="search" placeholder="find a pattern">
  <h2>Tiers</h2>
  <label class="row"><input type="checkbox" data-tier="3" checked><span class="sw" style="background:var(--t3)"></span>3 orchestration</label>
  <label class="row"><input type="checkbox" data-tier="2" checked><span class="sw" style="background:var(--t2)"></span>2 behavioral</label>
  <label class="row"><input type="checkbox" data-tier="1" checked><span class="sw" style="background:var(--t1)"></span>1 structural</label>
  <h2>Links</h2>
  <label class="row"><input type="checkbox" data-kind="orchestrates" checked><span class="ln" style="background:var(--ink)"></span>orchestrates (from episodes)</label>
  <label class="row"><input type="checkbox" data-kind="judged" checked><span class="ln" style="background:var(--judged)"></span>orchestrates (model-proposed)</label>
  <label class="row"><input type="checkbox" data-kind="works_with" checked><span class="ln" style="background:var(--works)"></span>works with</label>
  <label class="row"><input type="checkbox" data-kind="co_occurs"><span class="ln" style="background:var(--co)"></span>co-occurs</label>
  <h2>View</h2>
  <label class="row"><input type="checkbox" id="labels" checked>labels on every pattern</label>
  <label class="row"><input type="checkbox" id="flow" checked>show flow along links</label>
  <label class="row"><input type="checkbox" id="orphans">only flagged patterns</label>
  <div style="margin-top:10px"><button id="reset">Reset view</button></div>
</div>
<div id="panel" class="box"><button id="close">×</button><div id="pbody"></div></div>
<script>
const DATA = /*DATA*/null;
const C = { 1: "#5aa9e6", 2: "#7bd389", 3: "#f2b84b", judged: "#e07be0", works_with: "#f2b84b", co_occurs: "#6b7486", orchestrates: "#e7e9ee", warn: "#ff6b6b" };
const TIER = { 1: "Tier 1 · structural", 2: "Tier 2 · behavioral", 3: "Tier 3 · orchestration" };
const byId = Object.fromEntries(DATA.nodes.map(n => [n.id, n]));
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const kindOf = l => l.kind === "orchestrates" && l.judged ? "judged" : l.kind;
const nid = x => typeof x === "object" ? x.id : x;
const state = { tiers: new Set([1, 2, 3]), kinds: new Set(["orchestrates", "judged", "works_with"]), q: "", orphans: false, focus: null };

const counts = DATA.links.reduce((a, l) => (a[kindOf(l)] = (a[kindOf(l)] || 0) + 1, a), {});
document.getElementById("stats").textContent =
  `${DATA.expert} · ${DATA.nodes.length} patterns · ${(counts.orchestrates || 0) + (counts.judged || 0)} orchestration links` +
  (counts.judged ? ` (${counts.judged} model-proposed)` : "") +
  ` · ${DATA.nodes.filter(n => n.orphan).length} flagged`;

// on a large map every label at once is unreadable: tier 3 labels only, until asked
if (DATA.nodes.length > 40) document.getElementById("labels").checked = false;
if (typeof ForceGraph3D === "undefined") { document.getElementById("nolib").style.display = "flex"; throw new Error("libraries missing"); }

const nbrs = {};
DATA.links.forEach(l => { (nbrs[l.source] ||= new Set()).add(l.target); (nbrs[l.target] ||= new Set()).add(l.source); });

function visible() {
  const q = state.q.toLowerCase();
  let nodes = DATA.nodes.filter(n => state.tiers.has(n.tier) && (!state.orphans || n.orphan));
  const ids = new Set(nodes.map(n => n.id));
  const links = DATA.links.filter(l => state.kinds.has(kindOf(l)) && ids.has(nid(l.source)) && ids.has(nid(l.target)));
  return { nodes, links, match: q ? new Set(nodes.filter(n => (n.name + " " + n.id).toLowerCase().includes(q)).map(n => n.id)) : null };
}

const size = n => (n.tier === 3 ? 6 : 3) + Math.sqrt(n.episodes || 1) * 1.6;
const dim = n => {
  const v = cur.match;
  if (v && !v.has(n.id)) return true;
  if (state.focus && n.id !== state.focus && !(nbrs[state.focus] || new Set()).has(n.id)) return true;
  return false;
};
let cur = visible();

const Graph = ForceGraph3D()(document.getElementById("graph"))
  .backgroundColor("#0e1116")
  .graphData({ nodes: cur.nodes, links: cur.links })
  .nodeId("id")
  .nodeVal(n => size(n))
  .nodeLabel(n => `<b>${esc(n.name)}</b><br>${TIER[n.tier]}${n.episodes ? ` · ${n.episodes} episodes` : ""}`)
  .nodeThreeObjectExtend(true)
  .nodeThreeObject(n => {
    if (!(n.tier === 3 || document.getElementById("labels").checked)) return null;
    const s = new SpriteText(n.name.length > 42 ? n.name.slice(0, 40) + "…" : n.name);
    s.color = dim(n) ? "rgba(231,233,238,.25)" : "#e7e9ee";
    s.textHeight = n.tier === 3 ? 5 : 3.6;
    s.position.y = size(n) * 0.9 + 3;
    return s;
  })
  .nodeColor(n => dim(n) ? "rgba(120,128,140,.25)" : n.orphan ? C.warn : C[n.tier])
  .nodeOpacity(0.92)
  .linkColor(l => C[kindOf(l)])
  .linkOpacity(0.55)
  .linkWidth(l => l.kind === "co_occurs" ? 0 : l.kind === "works_with" ? 0.6 : 1.1)
  .linkVisibility(l => !state.focus || nid(l.source) === state.focus || nid(l.target) === state.focus)
  .linkDirectionalArrowLength(l => l.kind === "orchestrates" ? 3.2 : 0)
  .linkDirectionalArrowRelPos(1)
  .linkDirectionalParticles(l => l.kind === "orchestrates" && document.getElementById("flow").checked ? 2 : 0)
  .linkDirectionalParticleWidth(1.4)
  .linkDirectionalParticleSpeed(0.006)
  .onNodeClick(n => focus(n.id))
  .onBackgroundClick(() => unfocus());

Graph.d3Force("charge").strength(-160);
Graph.d3Force("link").distance(l => l.kind === "co_occurs" ? 120 : 60);

function refresh() {
  cur = visible();
  Graph.graphData({ nodes: cur.nodes, links: cur.links });
}
// re-setting an accessor (as a fresh function) is what makes the graph re-evaluate it
function restyle() {
  const nc = Graph.nodeColor(), no = Graph.nodeThreeObject(), lv = Graph.linkVisibility();
  Graph.nodeColor(n => nc(n)).nodeThreeObject(n => no(n)).linkVisibility(l => lv(l));
}

function linkTo(id) { const n = byId[id]; return n ? `<a data-go="${esc(id)}">${esc(n.name)}</a>` : esc(id); }
function why(a, b) {
  const l = DATA.links.find(l => (nid(l.source) === a && nid(l.target) === b) || (nid(l.source) === b && nid(l.target) === a));
  if (!l) return "";
  const s = l.basis || {};
  return s.judged !== undefined ? ` <span class="why">· proposed: ${esc(s.judged)}</span>`
       : s.shared_episodes ? ` <span class="why">· ${s.shared_episodes} shared episodes, lift ${s.lift}</span>` : "";
}
function focus(id) {
  const n = byId[id]; if (!n) return;
  state.focus = id; restyle();
  const rel = k => DATA.links.filter(l => l.kind === k);
  const orch = rel("orchestrates"), works = rel("works_with");
  const down = orch.filter(l => nid(l.source) === id).map(l => nid(l.target));
  const up = orch.filter(l => nid(l.target) === id).map(l => nid(l.source));
  const peers = works.filter(l => nid(l.source) === id || nid(l.target) === id).map(l => nid(l.source) === id ? nid(l.target) : nid(l.source));
  const list = (title, ids) => ids.length ? `<h4>${title}</h4><ul>${ids.map(b => `<li>${linkTo(b)}${why(id, b)}</li>`).join("")}</ul>` : "";
  const when = Array.isArray(n.when) ? `<ul>${n.when.map(w => `<li>${esc(w)}</li>`).join("")}</ul>` : esc(n.when);
  document.getElementById("pbody").innerHTML = `
    <h3>${esc(n.name)}</h3><div class="tier">${TIER[n.tier]}${n.episodes ? ` · seen in ${n.episodes} episodes` : ""}</div>
    ${n.orphan ? `<div class="flag">${n.tier === 3 ? "Orchestrates nothing yet." : "Nothing orchestrates this yet."}</div>` : ""}
    ${n.description ? `<p>${esc(n.description)}</p>` : ""}
    ${n.when ? `<h4>When to apply</h4>${when}` : ""}
    ${n.steps.length ? `<h4>Steps</h4><ol>${n.steps.map(s => `<li>${esc(typeof s === "string" ? s : JSON.stringify(s))}</li>`).join("")}</ol>` : ""}
    ${list("Orchestrates", down)}${list("Orchestrated by", up)}${list("Works with", peers)}
    ${n.aligns.length ? `<h4>Builds on</h4><div class="why">${n.aligns.map(esc).join(", ")}</div>` : ""}`;
  document.getElementById("panel").style.display = "block";
  document.querySelectorAll("#pbody a[data-go]").forEach(a => a.onclick = () => focus(a.dataset.go));
  const node = cur.nodes.find(x => x.id === id);
  if (node && node.x !== undefined) {
    const d = 220, r = 1 + d / Math.hypot(node.x || 1, node.y || 1, node.z || 1);
    Graph.cameraPosition({ x: node.x * r, y: node.y * r, z: node.z * r }, node, 1000);
  }
}
function unfocus() { state.focus = null; document.getElementById("panel").style.display = "none"; restyle(); }

document.querySelectorAll("[data-tier]").forEach(el => el.onchange = () => { el.checked ? state.tiers.add(+el.dataset.tier) : state.tiers.delete(+el.dataset.tier); refresh(); });
document.querySelectorAll("[data-kind]").forEach(el => el.onchange = () => { el.checked ? state.kinds.add(el.dataset.kind) : state.kinds.delete(el.dataset.kind); refresh(); });
document.getElementById("labels").onchange = restyle;
document.getElementById("flow").onchange = () => { const p = Graph.linkDirectionalParticles(); Graph.linkDirectionalParticles(l => p(l)); };
document.getElementById("orphans").onchange = e => { state.orphans = e.target.checked; refresh(); };
document.getElementById("q").oninput = e => {
  state.q = e.target.value; cur.match = visible().match; restyle();
  if (cur.match && cur.match.size === 1) focus([...cur.match][0]);
};
document.getElementById("close").onclick = unfocus;
// frame the whole graph from outside its farthest node (zoomToFit can land inside it)
function fit(ms = 800) {
  const r = Math.max(40, ...Graph.graphData().nodes.map(n => Math.hypot(n.x || 0, n.y || 0, n.z || 0)));
  Graph.cameraPosition({ x: 0, y: r * 0.3, z: r * 2.6 + 60 }, { x: 0, y: 0, z: 0 }, ms);
}
let framed = false;
Graph.onEngineStop(() => { if (!framed) { framed = true; fit(); } });
document.getElementById("reset").onclick = () => { unfocus(); fit(); };
</script>
</body>
</html>
"""
