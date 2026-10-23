# -*- coding: utf-8 -*-
"""FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_02: 最終集計(API 0)。Fable抜取り用一覧と主要指標をer112_output/kp_gm_trial_01/へ書き出す。DEV専用。"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import er003_key_words_canonicalization as kc   # noqa: E402
import er112_kp_gm_eval_01 as ev   # noqa: E402
import er112_kp_gm_judge_01 as jd   # noqa: E402
import er112_kp_gm_trial_01 as tr   # noqa: E402

OUT = ROOT / "er112_output" / "kp_gm_trial_01"
JARMS = {"prod", "a1g", "a12", "a123s", "a3v2", "a1gE0", "a1gE2", "a1gE3"}


def main():
    # 0) 入力prompt断片の保存(再現用)
    inp = OUT / "inputs"
    tpl = (ROOT / kc.FULLTEXT_PROMPT_TEMPLATE_PATH).read_text(encoding="utf-8")
    (inp / "a1_template_final.txt").write_text(tr.build_a1_template(tpl), encoding="utf-8")
    (inp / "a2_extra.txt").write_text(tr.A2_EXTRA, encoding="utf-8")
    (inp / "a3_extra_v1_v2_v3.txt").write_text("[v1]\n" + tr.A3_EXTRA + "\n[v2]\n" + tr.A3_EXTRA_V2 + "\n[v3]\n" + tr.A3_EXTRA_V3, encoding="utf-8")

    res = ev.load_results()
    rows = ev.items_table(res)
    jrows, ref = jd.build_rows(JARMS, hard_only=True)
    caches = {j: jd.load_cache(j) for j in ("sonnet", "sol")}
    # id -> verdicts
    by_item = defaultdict(list)
    for rid, rr in ref.items():
        for (arm, rep, uid, rank, kind) in rr:
            vs = {j: (caches[j].get(rid) or {}).get("verdict") for j in caches}
            by_item[(arm, rep, uid, rank)].append((kind, jrows[rid], vs))

    lines = ["# Fable抜取り用一覧(難例×arm×rep、Judge判定つき)", "",
             "arm: prod=記録済みProduction出力(baseline 1標本) / a1g=A-1のみ(gloss・説明は現行Prompt) / a12=A-1+A-2 / a123s=A-1+A-2+A-3 v1+Std/Adv共有 / a3v2=A-1+A-2+A-3 v2 / "
             "a1gE0・E2・E3=A-1のみのitemsに対し説明段を現行/A-3 v2/A-3 v3で各3回。Judge欄: S=Sonnet5.5, X=Sol6.1(1=良い側の総合PASS、0=NG、-=未判定)。", ""]
    hard = sorted([x for x in rows if x["hard"] and x["arm"] in JARMS], key=lambda z: (z["display"].lower(), z["arm"], z["rep"], z["unit"]))
    cur = None
    for x in hard:
        if cur != x["display"].lower():
            cur = x["display"].lower()
            lines += ["", f"## {x['display']}"]
        tags = []
        for kind, row, vs in by_item.get((x["arm"], x["rep"], x["unit"], x["rank"]), []):
            if kind not in ("G", "E2", "P"):
                continue
            s = vs["sonnet"]
            o = vs["sol"]
            tags.append(f"{kind}:S{'-' if s is None else int(jd.verdict_ok(kind, s))}/X{'-' if o is None else int(jd.verdict_ok(kind, o))}")
        lines.append(f"- {x['arm']} r{x['rep']} [{x['unit'][-26:]}] key=`{x['key']}` | 意味={x['gloss']} | 説明={x['expl']} | {' '.join(tags)}")
    (OUT / "fable_sampling_list.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # 1) 主要指標 json
    summary = {}
    for arm in ("prod", "base_c", "a1_c", "a1g", "a12", "a123s", "a3v2", "a1gE0", "a1gE2", "a1gE3"):
        rs = [r for k, r in res.items() if k[0] == arm and not ev.UBY[k[2]]["synthetic"] and r.get("items") is not None or (k[0] == arm and r.get("canon_status") == "CANONICALIZATION_INVALID")]
        rs = [r for k, r in res.items() if k[0] == arm and not ev.UBY[k[2]]["synthetic"] and (r.get("items") is not None or r.get("canon_status") == "CANONICALIZATION_INVALID")]
        if not rs:
            continue
        summary[arm] = dict(units=len(rs), canon=dict(Counter(r.get("canon_status") for r in rs)),
                            retry_units=sum(1 for r in rs if len(r.get("canon_attempts") or []) > 1))
    # judge集計(arm別、両judge PASS)
    judged = {}
    for kinds in ("G", "E", "E2", "P"):
        pass
    (OUT / "summary_units.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    print("wrote fable_sampling_list.md", len(lines))


if __name__ == "__main__":
    main()
