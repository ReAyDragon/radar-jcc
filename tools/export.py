#!/usr/bin/env python3
"""Build data.json for the Radar JCC Pokémon app from an ArtifactData export.

Usage: python3 tools/export.py <export_dir> [output=data.json]

<export_dir> is the out_dir used with ArtifactData "list" on the collections
"releases" and "meta": it holds releases/<id>.json, meta/veille.json and
meta/journal.json. Writes the file only when its content changed, and prints
"changed" or "unchanged".
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def load(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: export.py <export_dir> [output]")
    src = Path(sys.argv[1])
    out = Path(sys.argv[2] if len(sys.argv) > 2 else "data.json")

    releases = []
    for f in sorted((src / "releases").glob("*.json")):
        doc = load(f)
        if isinstance(doc, dict):
            releases.append({"id": f.stem, **doc})
    releases.sort(key=lambda r: (r.get("date") or "9999", r.get("name") or ""))

    veille = load(src / "meta" / "veille.json") or {}
    journal = (load(src / "meta" / "journal.json") or {}).get("entries") or []
    journal = sorted(journal, key=lambda j: j.get("at", ""), reverse=True)[:40]

    body = {"veille": veille, "journal": journal, "releases": releases}
    old = load(out) if out.exists() else None
    if old and {k: old.get(k) for k in body} == body:
        print("unchanged")
        return
    body = {"generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"), **body}
    out.write_text(json.dumps(body, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("changed")


if __name__ == "__main__":
    main()
