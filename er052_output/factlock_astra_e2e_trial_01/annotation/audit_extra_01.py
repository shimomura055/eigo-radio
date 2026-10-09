# -*- coding: utf-8 -*-
"""委任_09 補助監査(既存2監査スクリプトは非編集)。tool_use を全件列挙し、
許可=Read(自分のプロンプト) / Write(自分のreply.md) と照合。Bash等は全て『許可外ツール』、Bashの内容がreply.mdへの書込みのみかも記録。
CLI: --transcript --annotator --slug --out"""
import argparse, json, re
ap = argparse.ArgumentParser(); ap.add_argument("--transcript"); ap.add_argument("--annotator"); ap.add_argument("--slug"); ap.add_argument("--out")
a = ap.parse_args()
BS = chr(92)
own_prompt = f"annotation/prompts/{a.slug}__{a.annotator}.md"; own_reply = f"annotation/out/{a.annotator}/{a.slug}/reply.md"
norm = lambda p: (p or "").replace(BS, "/")
uses = []
for ln in open(a.transcript, encoding="utf-8"):
    d = json.loads(ln)
    m = d.get("message", {}); c = m.get("content")
    if d.get("type") == "assistant" and isinstance(c, list):
        for x in c:
            if x.get("type") == "tool_use":
                uses.append({"tool": x["name"], "input": x.get("input", {})})
rows, viol = [], []
for u in uses:
    t, i = u["tool"], u["input"]
    if t == "Read":
        ok = norm(i.get("file_path")).endswith(own_prompt); rows.append({"tool": t, "target": i.get("file_path"), "allowed": ok})
        if not ok: viol.append(rows[-1])
    elif t == "Write":
        ok = norm(i.get("file_path")).endswith(own_reply); rows.append({"tool": t, "target": i.get("file_path"), "allowed": ok})
        if not ok: viol.append(rows[-1])
    elif t == "SubagentHandback":
        rows.append({"tool": t, "target": None, "allowed": True, "note": "最終報告(環境が付与した返却手段)"})
    else:
        cmd = i.get("command", "") if t == "Bash" else json.dumps(i, ensure_ascii=False)
        nc = norm(cmd)
        others = [p for p in re.findall(r"[A-Za-z]:/[^\s\"']+", nc) if not p.endswith(own_reply) and "annotation/out/" + a.annotator + "/" + a.slug not in p]
        r = {"tool": t, "allowed": False, "command_head": cmd[:200], "touches_own_reply": own_reply in nc, "other_abs_paths_in_command": others[:5]}
        rows.append(r); viol.append(r)
out = {"slug": a.slug, "annotator": a.annotator, "tool_use_count": len(uses), "tool_uses": rows, "disallowed_tool_uses": viol,
       "verdict": "PASS_ONLY_ALLOWED" if not viol else "DISALLOWED_TOOL_USE"}
json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=2); print(a.slug, a.annotator, out["verdict"], len(uses), [r["tool"] for r in rows])
