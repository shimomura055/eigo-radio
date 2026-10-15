"""per-file pytest runner (AUW 委任_03b). summary行(N passed, M failed)をregexで解析し、FAILED行も収集する。
usage: run_tests_per_file.py OUT.json [glob-prefix ...]"""
import concurrent.futures as cf
import glob
import json
import os
import re
import subprocess
import sys

PY = os.path.join(".venv", "Scripts", "python.exe")
out_path = sys.argv[1]
prefixes = sys.argv[2:] or ["er006", "er007", "er011", "er019", "er020", "er021", "er026", "er064", "er078"]

files = []
for pre in prefixes:
    files += glob.glob(pre + "*test*.py")
files = sorted(set(f for f in files if os.path.isfile(f)))

SUMMARY_RE = re.compile(r"=+ (?P<body>.*?) in [\d.]+s.*=+\s*$", re.M)
COUNT_RE = re.compile(r"(\d+) (passed|failed|error|errors|skipped|xfailed|xpassed|deselected|warnings?|subtests passed)")


def run(f):
    try:
        p = subprocess.run([PY, "-m", "pytest", f, "-q", "--tb=no", "-p", "no:cacheprovider", "-W", "ignore"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900)
        txt = p.stdout + "\n" + p.stderr
        rc = p.returncode
    except subprocess.TimeoutExpired as e:
        return f, {"rc": "TIMEOUT", "passed": 0, "failed": 0, "fails": [], "summary": "TIMEOUT"}
    counts = {"passed": 0, "failed": 0, "error": 0}
    last = ""
    for line in txt.splitlines():
        if re.search(r"\bin [\d.]+s\b", line) and COUNT_RE.search(line):
            last = line.strip(" =")
    for n, k in COUNT_RE.findall(last):
        k = {"errors": "error"}.get(k, k)
        if k in counts:
            counts[k] += int(n)
    fails = sorted(set(l.strip() for l in txt.splitlines() if l.startswith(("FAILED ", "ERROR "))))
    return f, {"rc": rc, "passed": counts["passed"], "failed": counts["failed"], "error": counts["error"],
               "fails": fails, "summary": last}


res = {}
with cf.ThreadPoolExecutor(max_workers=int(os.environ.get("W","1"))) as ex:
    for f, r in ex.map(run, files):
        res[f] = r
json.dump(res, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
tp = sum(r["passed"] for r in res.values())
tf = sum(r["failed"] + r.get("error", 0) for r in res.values())
print(f"files={len(res)} passed={tp} failed+error={tf}")
