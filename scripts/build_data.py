"""Turn a hub database export into the mirror's public data files.

Usage: python3 scripts/build_data.py <export_dir> [data_dir]
<export_dir> holds ArtifactData out_dir exports: library_index/, sessions/, headlines/ (one JSON file per doc).
Only whitelisted fields from those three collections are published. Takes, study log, reviews,
requests, intake, runs and any user ids never leave the hub.
"""
import json, sys, pathlib, datetime, re

src = pathlib.Path(sys.argv[1])
out = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else pathlib.Path(__file__).parent.parent / "data")
URL = re.compile(r"^https?://", re.I)

def docs(coll):
    d = src / coll
    if not d.is_dir():
        sys.exit(f"missing export folder: {d}")
    for f in sorted(d.glob("*.json")):
        doc = json.loads(f.read_text())
        doc = doc.get("data", doc) if isinstance(doc.get("data"), dict) else doc
        yield f.stem, doc

def txt(v, n=20000):
    return v[:n] if isinstance(v, str) else ("" if v is None else str(v)[:n])

def url(v):
    v = txt(v, 2000)
    return v if URL.match(v) else ""

def topics(v):
    return [txt(t, 40) for t in v][:8] if isinstance(v, list) else []

library = [{
    "id": i, "title": txt(d.get("title"), 400), "authors": txt(d.get("authors"), 300), "org": txt(d.get("org"), 300),
    "year": txt(d.get("year"), 10), "url": url(d.get("url")), "tier": txt(d.get("tier"), 4), "topics": topics(d.get("topics")),
    "is_fundamental": bool(d.get("is_fundamental")), "why": txt(d.get("why"), 1500),
} for i, d in docs("library_index")]

def section(x):
    o = {"h": txt(x.get("h"), 200), "body": txt(x.get("body")), "hold": txt(x.get("hold"), 600)}
    p = x.get("probe")
    if isinstance(p, dict) and p.get("q"):
        o["probe"] = {"q": txt(p.get("q"), 1000), "a": txt(p.get("a"), 2000)}
    return o

sessions = [{
    "id": i, "paper_id": txt(d.get("paper_id"), 200), "title": txt(d.get("title"), 400), "byline": txt(d.get("byline"), 400),
    "tier": txt(d.get("tier"), 4), "topics": topics(d.get("topics")), "kind": txt(d.get("kind"), 20), "minutes": txt(d.get("minutes"), 6),
    "sections": [section(x) for x in d.get("sections") or [] if isinstance(x, dict)], "receipt": txt(d.get("receipt"), 4000),
    "status": d.get("status") if d.get("status") in ("ready", "done", "needs_review") else "ready",
    "created_at": txt(d.get("created_at"), 40), "completed_at": txt(d.get("completed_at"), 40),
} for i, d in docs("sessions") if d.get("status") in ("ready", "done", "needs_review", None)]

headlines = [{
    "id": i, "text": txt(d.get("text"), 300), "url": url(d.get("url")), "tier": txt(d.get("tier"), 4), "date": txt(d.get("date"), 40),
    "benchmark_flag": bool(d.get("benchmark_flag")),
} for i, d in docs("headlines")]

out.mkdir(parents=True, exist_ok=True)
w = lambda name, obj: (out / name).write_text(json.dumps(obj, ensure_ascii=False, indent=1) + "\n")
w("library.json", library); w("sessions.json", sessions); w("headlines.json", headlines)
w("meta.json", {"generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                "counts": {"library": len(library), "sessions": len(sessions), "headlines": len(headlines)}})
print(f"library {len(library)} · sessions {len(sessions)} · headlines {len(headlines)} -> {out}")
