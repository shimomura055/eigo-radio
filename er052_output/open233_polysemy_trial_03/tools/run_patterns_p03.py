# -*- coding: utf-8 -*-
"""run_patterns_p03: パターン×テーマの並列バッチ(DEV/Trial専用)。--dry-runはAPI非呼出。
各ジョブはgen_notes_p03.pyをsubprocess実行し、runs/batch_log.jsonlへ集約。"""
import argparse, json, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
TRIAL = HERE.parent
ROOT = HERE.parents[2]


def build_jobs(patterns, slugs, targets, runs_dir, budget, extra=()):
    jobs = []
    for p in patterns:
        for s in slugs:
            th = targets[s]
            cmd = [sys.executable, str(HERE / "gen_notes_p03.py"), "--pattern", p, "--ledger-txt", th["txt"],
                   "--append-to-txt", th["txt"], "--budget-jpy", str(budget), "--out-dir", str(Path(runs_dir) / p / s)]
            if th.get("draft") and th.get("verif"):
                cmd += ["--draft", th["draft"], "--verif", th["verif"]]
            jobs.append({"pattern": p, "slug": s, "cmd": cmd + list(extra)})
    return jobs


def run_job(j):
    t = time.time()
    r = subprocess.run(j["cmd"], capture_output=True, text=True, encoding="utf-8", cwd=str(ROOT))
    return {"pattern": j["pattern"], "slug": j["slug"], "returncode": r.returncode, "sec": round(time.time() - t, 1),
            "stdout": r.stdout.strip()[-500:], "stderr": r.stderr.strip()[-500:]}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--patterns", required=True)
    ap.add_argument("--slugs", required=True)
    ap.add_argument("--targets", default=str(TRIAL / "eval" / "targets.json"))
    ap.add_argument("--runs-dir", default=str(TRIAL / "runs"))
    ap.add_argument("--parallel", type=int, default=3)
    ap.add_argument("--budget-jpy-per-call", type=float, default=5.0)
    ap.add_argument("--web-search", choices=["none", "url_only"], default="none")
    ap.add_argument("--max-chars", type=int, default=None)
    ap.add_argument("--max-notes", type=int, default=None)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-existing-notes", action="store_true")
    ap.add_argument("--run-tag", default="")
    ap.add_argument("--holdout", default=str(TRIAL / "eval" / "holdout.json"))
    a = ap.parse_args(argv)
    targets = json.loads(Path(a.targets).read_text(encoding="utf-8"))["themes"]
    if Path(a.holdout).exists():  # holdout(正解表なし)もslug指定で実行可能にする
        for k, v in json.loads(Path(a.holdout).read_text(encoding="utf-8"))["themes"].items():
            targets.setdefault(k, v)
    extra = ["--web-search", a.web_search]
    if a.max_chars is not None:
        extra += ["--max-chars", str(a.max_chars)]
    if a.no_existing_notes:
        extra.append("--no-existing-notes")
    if a.max_notes is not None:
        extra += ["--max-notes", str(a.max_notes)]
    if a.dry_run:
        extra.append("--dry-run")
    runs_dir = str(Path(a.runs_dir) / a.run_tag) if a.run_tag else a.runs_dir
    jobs = build_jobs(a.patterns.split(","), a.slugs.split(","), targets, runs_dir, a.budget_jpy_per_call, extra)
    with ThreadPoolExecutor(max_workers=a.parallel) as ex:
        results = list(ex.map(run_job, jobs))
    log = Path(runs_dir) / "batch_log.jsonl"
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as f:
        for r in results:
            r["dry_run"] = a.dry_run
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            print(json.dumps(r, ensure_ascii=False))
    return 0 if all(r["returncode"] == 0 for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
