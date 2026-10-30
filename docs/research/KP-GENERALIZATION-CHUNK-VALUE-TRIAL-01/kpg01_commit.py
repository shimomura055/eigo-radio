# -*- coding: utf-8 -*-
"""自分のファイルだけを、origin/main基準の一時worktreeでcommit→push(並行Workerの未commit差分を巻き込まない)。
usage: kpg01_commit.py <msgfile> <ssot.json> <file1> <file2> ...   ssot.json: {"open": row, "dl": line, "at": row}(あれば行を置換/追加)"""
import json, os, subprocess, sys, shutil, tempfile
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
def sh(*a, cwd=ROOT, check=True):
    r = subprocess.run(a, cwd=cwd, capture_output=True, text=True, encoding="utf-8")
    if check and r.returncode: raise SystemExit(f"FAIL {a}: {r.stderr[:500]}")
    return r.stdout.strip()
def upsert_line(path, key, newline, after_key=None, after_first_line=False):
    L = open(path, encoding="utf-8").read().split("\n")
    idx = [i for i, l in enumerate(L) if l.startswith(key)]
    if idx: L[idx[0]] = newline
    elif after_first_line:
        j = next(i for i, l in enumerate(L) if l.startswith("**管理ID"))
        L.insert(j + 1, newline)
    else:
        j = max(i for i, l in enumerate(L) if l.startswith(after_key))
        L.insert(j + 1, newline)
    open(path, "w", encoding="utf-8", newline="\n").write("\n".join(L))
def attempt(msg, ssot, files):
    sh("git", "fetch", "origin", "-q")
    wt = os.path.join(tempfile.gettempdir(), "kpg01_wt")
    if os.path.exists(wt): sh("git", "worktree", "remove", "--force", wt, check=False)
    sh("git", "worktree", "add", "--no-checkout", "--detach", wt, "origin/main")
    try:
        sh("git", "sparse-checkout", "init", "--no-cone", cwd=wt)
        paths = ["/OPEN_ITEMS.md", "/DECISION_LOG.md", "/docs/pm/ACTIVE_TASK.md", "/docs/pm/USER_DECISION_REGISTER_01.md"] + ["/" + f for f in files]
        sh("git", "sparse-checkout", "set", "--no-cone", *paths, cwd=wt)
        sh("git", "checkout", "--detach", "origin/main", cwd=wt)
        for f in files:
            dst = os.path.join(wt, f); os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(os.path.join(ROOT, f), dst)
        targets = []
        if ssot.get("open"):
            op = os.path.join(wt, "OPEN_ITEMS.md")
            no = ssot.get("open_no", "618")
            if ssot.get("restore_from"):   # 他Workerの行を誤って上書きした場合の復元: 指定commitの同番号行を戻す
                rk, rc = ssot["restore_key"], ssot["restore_from"]
                orig = [l for l in sh("git", "show", rc + ":OPEN_ITEMS.md", cwd=ROOT).split("\n") if l.startswith(rk)][0]
                Lr = open(op, encoding="utf-8").read().split("\n")
                ix = [i for i, l in enumerate(Lr) if l.startswith(rk)]
                assert ix and "KP-GENERALIZATION-CHUNK-VALUE-TRIAL-01" in Lr[ix[0]][:200], "復元対象行が想定と異なる"
                Lr[ix[0]] = orig
                open(op, "w", encoding="utf-8", newline="\n").write("\n".join(Lr))
            key = "| OPEN-%s |" % no
            ex = [l for l in open(op, encoding="utf-8").read().split("\n") if l.startswith(key)]
            assert not ex or "KP-GENERALIZATION-CHUNK-VALUE-TRIAL-01" in ex[0][:200], "他Workerの行を上書きしようとしている: " + key
            upsert_line(op, key, ssot["open"], after_key="| OPEN-6"); targets.append("OPEN_ITEMS.md")
        if ssot.get("dl"):
            upsert_line(os.path.join(wt, "DECISION_LOG.md"), "- 2026-10-30 | KP-GENERALIZATION-CHUNK-VALUE-TRIAL-01-DECISION-01", ssot["dl"], after_first_line=True); targets.append("DECISION_LOG.md")
        if ssot.get("at"):
            upsert_line(os.path.join(wt, "docs/pm/ACTIVE_TASK.md"), "(KG)KP-GENERALIZATION-CHUNK-VALUE-TRIAL-01", ssot["at"], after_key="(X)FY-FZ-FEMALE-VOICE-RANK-01"); targets.append("docs/pm/ACTIVE_TASK.md")
        if ssot.get("udr"):
            import re
            rp = os.path.join(wt, "docs/pm/USER_DECISION_REGISTER_01.md")
            L = open(rp, encoding="utf-8").read().split("\n")
            ex = [i for i, l in enumerate(L) if l.startswith("- `#") and "KP-GENERALIZATION-CHUNK-VALUE-TRIAL-01" in l[:200]]
            if ex:
                num = int(re.match(r"- `#(\d+)", L[ex[0]]).group(1)); L[ex[0]] = "- `#%d %s" % (num, ssot["udr"])
            else:
                nums = [int(m.group(1)) for l in L for m in [re.match(r"- `#(\d+) ", l)] if m]
                num = max(nums) + 1
                last = max(i for i, l in enumerate(L) if re.match(r"- `#\d+ ", l))
                L.insert(last + 1, "- `#%d %s" % (num, ssot["udr"]))
            open(rp, "w", encoding="utf-8", newline="\n").write("\n".join(L))
            targets.append("docs/pm/USER_DECISION_REGISTER_01.md")
            print("UDR number", num)
        sh("git", "add", "-f", *files, *targets, cwd=wt)
        sh("git", "-c", "user.name=Keisuke Shimomura", "-c", "user.email=shimomura622@gmail.com", "commit", "-q", "-m", msg, cwd=wt)
        h = sh("git", "rev-parse", "--short", "HEAD", cwd=wt)
        r = subprocess.run(["git", "push", "origin", "HEAD:main"], cwd=wt, capture_output=True, text=True, encoding="utf-8")
        print("commit", h, "push rc", r.returncode, (r.stderr or r.stdout)[-300:])
        if r.returncode == 0:
            print("stat", sh("git", "show", "--stat", "--oneline", "HEAD", cwd=wt)[:800])
        return r.returncode == 0
    finally:
        sh("git", "worktree", "remove", "--force", wt, check=False)


if __name__ == "__main__":
    msg = open(sys.argv[1], encoding="utf-8").read(); ssot = json.load(open(sys.argv[2], encoding="utf-8")); files = sys.argv[3:]
    for i in range(3):
        if attempt(msg, ssot, files): break
        print("retry", i + 1)
