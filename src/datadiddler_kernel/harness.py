#!/usr/bin/env python3
"""
harness.py

Pipeline Harness v1 (machine-only).

Runs module CLIs in fixed order; writes:
- run_manifest.json
- stage_status.ndjson
- compiled/GroundedDatasetBlock.vN.json
- render/, evidence/, thread_index.json
- optional diff.json if --from-gdb provided

No prose. Deterministic given inputs and explicit tool paths/configs.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(p: Path, obj: Any) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_ndjson(p: Path, rows: List[Dict[str, Any]]) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def run_cmd(cmd: List[str]) -> Tuple[int, str, str]:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def main() -> int:
    ap = argparse.ArgumentParser(prog="harness", add_help=True)
    ap.add_argument("--in-dir", required=True)
    ap.add_argument("--work-dir", required=True)
    ap.add_argument("--project-id", required=True)
    ap.add_argument("--version", type=int, required=True)
    ap.add_argument("--tools", required=True)
    ap.add_argument("--schema", required=True)
    ap.add_argument("--separator-config", required=True)
    ap.add_argument("--tagger-config", required=True)
    ap.add_argument("--evidence-policy", required=False)
    ap.add_argument("--evidence-heuristics", required=False)
    ap.add_argument("--diff-schema", required=False)
    ap.add_argument("--from-gdb", default=None)
    args = ap.parse_args()

    in_dir = Path(args.in_dir).resolve()
    work = Path(args.work_dir).resolve()
    work.mkdir(parents=True, exist_ok=True)

    tools = json.loads(Path(args.tools).read_text(encoding="utf-8"))
    schema = Path(args.schema).resolve()

    manifest = {
        "generated_at": utc_now(),
        "project_id": args.project_id,
        "version": args.version,
        "inputs": {"in_dir": str(in_dir)},
        "tools": {
            k: {
                "path": v,
                "sha256": sha256_file(Path(v)) if Path(v).is_file() else None
            }
            for k, v in tools.items()
        },
        "configs": {
            "separator": {
                "path": args.separator_config,
                "sha256": sha256_file(Path(args.separator_config))
            },
            "tagger": {
                "path": args.tagger_config,
                "sha256": sha256_file(Path(args.tagger_config))
            }
        }
    }

    if args.evidence_policy:
        manifest["configs"]["evidence_policy"] = {
            "path": args.evidence_policy,
            "sha256": sha256_file(Path(args.evidence_policy))
        }

    if args.evidence_heuristics:
        manifest["configs"]["evidence_heuristics"] = {
            "path": args.evidence_heuristics,
            "sha256": sha256_file(Path(args.evidence_heuristics))
        }

    write_json(work / "run_manifest.json", manifest)

    status_rows: List[Dict[str, Any]] = []

    # Stage 1: rake
    rake_out = work / "stage_rake"
    rake_out.mkdir(parents=True, exist_ok=True)
    cmd = ["python", tools["rake"], "ingest",
           "--in", str(in_dir),
           "--out-dir", str(rake_out),
           "--project-id", args.project_id]
    rc, so, se = run_cmd(cmd)
    status_rows.append({"stage": "rake", "rc": rc, "out_dir": str(rake_out), "stdout": so, "stderr": se})
    if rc != 0:
        write_ndjson(work / "stage_status.ndjson", status_rows)
        return 2

    # Stage 2: separator
    sep_out = work / "stage_separator"
    sep_out.mkdir(parents=True, exist_ok=True)
    cmd = ["python", tools["separator"], "run",
           "--documents", str(rake_out / "documents.ndjson"),
           "--text", str(rake_out / "text_artifacts.ndjson"),
           "--config", str(Path(args.separator_config).resolve()),
           "--out-dir", str(sep_out)]
    rc, so, se = run_cmd(cmd)
    status_rows.append({"stage": "separator", "rc": rc, "out_dir": str(sep_out), "stdout": so, "stderr": se})
    if rc != 0:
        write_ndjson(work / "stage_status.ndjson", status_rows)
        return 2

    # Stage 3: tagger
    tag_out = work / "stage_tagger"
    tag_out.mkdir(parents=True, exist_ok=True)
    cmd = ["python", tools["tagger"], "run",
           "--triage", str(sep_out / "triage.ndjson"),
           "--documents", str(rake_out / "documents.ndjson"),
           "--text", str(rake_out / "text_artifacts.ndjson"),
           "--config", str(Path(args.tagger_config).resolve()),
           "--out-dir", str(tag_out)]
    rc, so, se = run_cmd(cmd)
    status_rows.append({"stage": "tagger", "rc": rc, "out_dir": str(tag_out), "stdout": so, "stderr": se})
    if rc != 0:
        write_ndjson(work / "stage_status.ndjson", status_rows)
        return 2

    # Stage 4: packager (weaver removed; threads placeholder retained)
    pkg_in = work / "stage_packager_in"
    pkg_in.mkdir(parents=True, exist_ok=True)
    for src, dst in [
        (rake_out / "documents.ndjson", pkg_in / "documents.ndjson"),
        (sep_out / "triage.ndjson", pkg_in / "triage.ndjson"),
        (tag_out / "entities.ndjson", pkg_in / "entities.ndjson"),
        (tag_out / "events.ndjson", pkg_in / "events.ndjson"),
        (tag_out / "claims.ndjson", pkg_in / "claims.ndjson"),
        (tag_out / "edges.ndjson", pkg_in / "edges.ndjson"),
    ]:
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

    # Compatibility placeholder: packager still expects threads.ndjson
    write_ndjson(pkg_in / "threads.ndjson", [])

    compiled = work / "compiled"
    compiled.mkdir(parents=True, exist_ok=True)
    out_gdb = compiled / f"GroundedDatasetBlock.v{args.version}.json"

    cmd = ["python", tools["packager"],
           "--in-dir", str(pkg_in),
           "--out", str(out_gdb),
           "--project-id", args.project_id,
           "--version", str(args.version),
           "--validate", "0",
           "--schema", str(schema)]
    rc, so, se = run_cmd(cmd)
    status_rows.append({"stage": "packager", "rc": rc, "out_path": str(out_gdb), "stdout": so, "stderr": se})
    if rc != 0:
        write_ndjson(work / "stage_status.ndjson", status_rows)
        return 2

    # Renderer
    render_out = work / "render"
    render_out.mkdir(parents=True, exist_ok=True)
    cmd = ["python", tools["renderer"], "--in", str(out_gdb), "--out-dir", str(render_out), "--schema", str(schema)]
    rc, so, se = run_cmd(cmd)
    status_rows.append({"stage": "renderer", "rc": rc, "out_dir": str(render_out), "stdout": so, "stderr": se})

    # Indexer
    idx_out = work / "thread_index.json"
    cmd = ["python", tools["indexer"], "--rendered-dir", str(render_out), "--out", str(idx_out)]
    rc4, so4, se4 = run_cmd(cmd)
    status_rows.append({"stage": "indexer", "rc": rc4, "out_path": str(idx_out), "stdout": so4, "stderr": se4})

    write_ndjson(work / "stage_status.ndjson", status_rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())