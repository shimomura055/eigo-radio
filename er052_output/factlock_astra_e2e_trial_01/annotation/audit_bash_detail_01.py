# -*- coding: utf-8 -*-
"""委任_09: Bashを使った注記者について、コマンド骨格(heredoc本文を除く)を抽出し、reply.md書込み以外の動作が無いかを確認。
併せて全注記者について SubagentHandback本文 と 保存済み reply.md の一致を確認。"""
import json, re, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
out = {}
for N in "AB":
    for s in "byd_recall central_bank_mortgage hormuz inbound_tourism meta openai_copyright semiconductor_earnings small_bag space_weapons streaming_price".split():
        O = os.path.join(HERE, "out", N, s)
        recs = [json.loads(l) for l in open(os.path.join(O, "transcript.jsonl"), encoding="utf-8")]
        uses = [x for r in recs if r.get("type") == "assistant" and isinstance(r["message"]["content"], list) for x in r["message"]["content"] if x.get("type") == "tool_use"]
        bash = [u["input"].get("command", "") for u in uses if u["name"] == "Bash"]
        skel = []
        for c in bash:
            m = re.match(r"(.*?<<'?(\w+)'?\n)(.*)\n\2\s*$", c, re.S)
            skel.append(m.group(1) if m else c[:200])
        hb = [u["input"].get("message", "") for u in uses if u["name"] == "SubagentHandback"]
        rep = open(os.path.join(O, "reply.md"), encoding="utf-8", newline="").read().replace("\r\n", "\n")
        wr = [u["input"].get("content", "") for u in uses if u["name"] == "Write"]
        body_bash = [re.match(r".*?<<'?(\w+)'?\n(.*)\n\1\s*$", c, re.S).group(2) if re.match(r".*?<<'?(\w+)'?\n(.*)\n\1\s*$", c, re.S) else None for c in bash]
        out[f"{s}__{N}"] = {"bash_skeletons": skel, "n_tool_uses": len(uses),
                            "handback_equals_reply": bool(hb) and hb[-1].strip() == rep.strip(),
                            "written_content_equals_reply": [ (w.strip() == rep.strip()) for w in wr] + [ (b is not None and b.strip() == rep.strip()) for b in body_bash]}
json.dump(out, open(os.path.join(HERE, "audit", "bash_detail.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
for k, v in sorted(out.items()): print(k, v["bash_skeletons"], v["handback_equals_reply"], v["written_content_equals_reply"])
