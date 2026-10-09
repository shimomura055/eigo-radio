# -*- coding: utf-8 -*-
"""委任_09: 20 transcript を annotation/out/<N>/<slug>/transcript.jsonl へコピーし、3種の監査を実行して annotation/audit/ に集約する。
transcript の特定は、各jsonl先頭のユーザー発話(固定文言)に自分のプロンプトパスが含まれるかで行う。決定論・API支出0。"""
import glob, json, os, shutil, subprocess, sys, datetime
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(HERE)
SUB = r"C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\f2c17cf7-6207-4666-abec-016808eac6d3\subagents"
SLUGS = "hormuz inbound_tourism streaming_price".split()
BS = chr(92)
m = {}
for f in glob.glob(os.path.join(SUB, "*.jsonl")):
    if datetime.datetime.fromtimestamp(os.stat(f).st_mtime) < datetime.datetime(2026, 10, 9, 9, 15):
        continue
    with open(f, encoding="utf-8") as fh:
        c = json.loads(fh.readline())["message"]["content"]
    if not isinstance(c, str) or not c.startswith("あなたは注記者"):
        continue
    for s in SLUGS:
        for a in "AB":
            if BS + "annotation" + BS + "prompts" + BS + f"{s}__{a}.md" in c:
                m.setdefault(f"{s}__{a}", []).append(f)
env = dict(os.environ, PYTHONUTF8="1")
os.makedirs(os.path.join(HERE, "audit"), exist_ok=True)
summary = {}
py = sys.executable
def run(args):
    return subprocess.run([py] + args, capture_output=True, text=True, env=env, encoding="utf-8", stdin=subprocess.DEVNULL, cwd=BASE)
for k in sorted(SLUGS and [f"{s}__{a}" for s in SLUGS for a in "AB"]):
    s, N = k.split("__")
    if k not in m or len(m[k]) != 1:
        summary[k] = {"verdict": "監査不能", "reason": f"transcript特定数={len(m.get(k, []))}"}; continue
    O = os.path.join("annotation", "out", N, s)
    _t=os.path.join(BASE, O, "transcript.jsonl"); (os.path.exists(_t) and shutil.copyfile(_t, os.path.join(BASE, O, "transcript_v1round.jsonl"))); shutil.copyfile(m[k][0], _t)
    r1 = run([os.path.join("annotation", "audit_strict_01.py"), "--transcript", O + "/transcript.jsonl", "--annotator", N, "--out", f"annotation/audit/v2round_{k}.strict.json"])
    r2 = run(["b3_annotator_audit_01.py", "--transcript", O + "/transcript.jsonl", "--out", f"annotation/audit/v2round_{k}.base.json", "--allow-substring", f"prompts/{k}.md"])
    r3 = run([os.path.join("annotation", "audit_extra_01.py"), "--transcript", O + "/transcript.jsonl", "--annotator", N, "--slug", s, "--out", f"annotation/audit/v2round_{k}.extra.json"])
    ex = json.load(open(os.path.join(BASE, f"annotation/audit/v2round_{k}.extra.json"), encoding="utf-8"))
    summary[k] = {"transcript": os.path.basename(m[k][0]), "strict": r1.stdout.strip(), "base_rc": r2.returncode, "base_out": r2.stdout.strip()[:100],
                  "extra_verdict": ex["verdict"], "tools": [(u["tool"], u.get("allowed")) for u in ex["tool_uses"]],
                  "bash_touching_other_paths": [u.get("other_abs_paths_in_command") for u in ex["tool_uses"] if u["tool"] == "Bash"]}
    print(k, summary[k])
json.dump(summary, open(os.path.join(HERE, "audit", "audit_all_11.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
