# -*- coding: utf-8 -*-
import json, os, subprocess, sys, tempfile
H = os.path.dirname(os.path.abspath(__file__))
R = r"C:\Users\tensh\eigo-radio\er052_output\factlock_astra_e2e_trial_01\annotation\prompts" + "\\"
T = tempfile.mkdtemp()
def w(n, uses):
    open(f"{T}/{n}", "w", encoding="utf-8").write(json.dumps({"message": {"content": [{"type": "tool_use", "name": "Read", "input": {"file_path": u}} for u in uses]}}) + "\n")
w("ok", [R + "hormuz__A.md"]); w("other_annotator", [R + "hormuz__B.md"]); w("claude_md", [r"C:\Users\tensh\eigo-radio\CLAUDE.md"])
open(f"{T}/junk", "w").write("not json\n")
open(f"{T}/none", "w").write(json.dumps({"message": {"content": [{"type": "text", "text": "hi"}]}}) + "\n")
exp = {"ok": 0, "other_annotator": 1, "claude_md": 1, "junk": 1, "none": 0}
bad = 0
for n, e in exp.items():
    r = subprocess.run([sys.executable, os.path.join(H, "audit_strict_01.py"), "--transcript", f"{T}/{n}", "--annotator", "A", "--out", f"{T}/{n}.out"], capture_output=True, text=True)
    print(n, r.stdout.strip(), "rc", r.returncode, "expected", e); bad += r.returncode != e
print("ALL_PASS" if not bad else "FAIL"); sys.exit(bad)
