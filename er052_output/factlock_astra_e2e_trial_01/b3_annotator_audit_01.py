# -*- coding: utf-8 -*-
"""注記者(subagent)の事後監査。決定論・LLM不使用・API支出0。

隔離手段 (ii): subagent の transcript(jsonl)から tool_use を抽出し、Read/Grep/Glob/Bash/Web系で開いた/検索した
パスと検索語を、参照禁止リストと照合する。結果は JSON で保存する。
隔離手段 (i) (入力を依頼文へ貼り付け、出力も本文で返させる) が守られていれば、tool_use は0件のはずである。
tool_use が1件でもあれば記録し(NOTE)、禁止リストに該当すれば VIOLATION とする。Webツールは常に VIOLATION。
CLI: --transcript <jsonl or json> --out <結果json> [--allow-substring <許可する語> ...]
終了コード: 違反なし=0 / VIOLATION=1
"""
import argparse
import json
import re
import sys

FORBIDDEN = [
    r"selected_brief_factlock", r"ANNOTATION_LOG", r"annotate_briefs", r"astra_revise_matrix_02",
    r"prep_inputs", r"core_numbers", r"B3_ANNOTATION_SPEC_v1", r"B3_ANNOTATION_SPEC_v2(?!_ANNOTATOR)",
    r"OLD4_EXPECTED", r"OPUS_POINTS", r"factlock_writer_trial_01[\\/]briefs", r"factlock_astra_e2e_trial_01",
    r"RESULT", r"REPORT", r"PREREGISTRATION", r"DESIGN_E2E", r"DECISION_LOG", r"OPEN_ITEMS", r"CURRENT_SPEC",
    r"eval", r"annotation\.json", r"ANNOTATION_DELEGATION_TEMPLATE",
]
WEB_TOOLS = ("WebSearch", "WebFetch")


def iter_tool_uses(node):
    if isinstance(node, dict):
        if node.get("type") == "tool_use" and "name" in node:
            yield node
        for v in node.values():
            yield from iter_tool_uses(v)
    elif isinstance(node, list):
        for v in node:
            yield from iter_tool_uses(v)


def load_records(text):
    text = text.strip()
    try:
        return [json.loads(text)]
    except ValueError:
        out = []
        for line in text.split("\n"):
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except ValueError:
                    pass
        return out


def audit(text, allow=()):
    uses = [u for rec in load_records(text) for u in iter_tool_uses(rec)]
    rows, violations = [], []
    for u in uses:
        name, inp = u["name"], u.get("input", {}) or {}
        targets = [str(v) for k, v in inp.items() if k in ("file_path", "path", "pattern", "command", "glob", "url", "query", "notebook_path")]
        hit = []
        for t in targets:
            for pat in FORBIDDEN:
                if re.search(pat, t, re.I) and not any(a in t for a in allow):
                    hit.append(pat)
        is_web = name in WEB_TOOLS or name.startswith("mcp__")
        rows.append({"tool": name, "targets": targets, "forbidden_hits": sorted(set(hit)), "web_or_mcp": is_web})
        if hit or is_web:
            violations.append(rows[-1])
    return {"tool_use_count": len(uses), "violations": violations, "tool_uses": rows,
            "verdict": "VIOLATION" if violations else ("PASS_WITH_TOOL_USE_NOTE" if uses else "PASS_NO_TOOL_USE")}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--transcript", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--allow-substring", action="append", default=[])
    a = ap.parse_args(argv)
    res = audit(open(a.transcript, encoding="utf-8").read(), a.allow_substring)
    open(a.out, "w", encoding="utf-8").write(json.dumps(res, ensure_ascii=False, indent=2))
    print(res["verdict"], res["tool_use_count"])
    return 1 if res["verdict"] == "VIOLATION" else 0


if __name__ == "__main__":
    sys.exit(main())
