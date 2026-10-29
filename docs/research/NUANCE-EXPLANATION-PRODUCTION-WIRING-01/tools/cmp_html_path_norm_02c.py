import sys, difflib
a = open(sys.argv[1], encoding="utf-8").read().replace("/.claude/worktrees/agent-acf55df00e2f1530c", "").replace("run_nxm1", "run_reselect_01")
b = open(sys.argv[2], encoding="utf-8").read().replace("/.claude/worktrees/agent-acf55df00e2f1530c", "").replace("run_nxm1", "run_reselect_01")
print("equal_after_path_norm", a == b, len(a), len(b))
if a != b:
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    n = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != "equal":
            print(tag, repr(a[max(0, i1 - 40):i2 + 40])[:300], "=>", repr(b[max(0, j1 - 40):j2 + 40])[:300])
            n += 1
            if n > 6:
                break
