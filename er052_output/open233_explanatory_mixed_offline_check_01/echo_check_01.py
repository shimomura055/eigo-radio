# -*- coding: utf-8 -*-
"""OPEN-233-SELF-RECOVERY-TRIAL-01 委任_57 作業3-1: エコー確認(標準ライブラリのみ、LLM/API呼び出し無し、既存ファイルは編集しない)。

`prior_issues`の`claim_in_article`には、確定範囲`claim_span_text`(複数範囲は記事順に改行連結)が渡される
(runner `run_instance`の`prior_issues`)。その複数範囲の連結文字列を、次周回のRecheck(以降の周回のstage2_results、
`claim_text`/`dev.claim_in_article`)が、改行または連結の形でそのまま返した例があるかを数える。
対象: instance JSON(er052_output/open233_self_recovery_flow_runner_01_*/instances_*/*.json)のうち、
stage2_resultsに`claim_span_text`が記録されている周回(委任_42以降の新方式)。
判定: ある周回cの複数範囲claim_span_text(「\n」を含む)について、次周回(c+1)の全stage2_resultsの
`claim_text`と`dev.claim_in_article`が、(a)連結文字列と空白正規化後に完全一致、(b)連結文字列を部分文字列として含む、
(c)連結文字列の範囲のうち2つ以上を含む(記事順・連結順問わず)、のいずれかに当たるものを数える。
"""
import glob, json, os, re, sys
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ER = os.path.abspath(os.path.join(HERE, "..", ""))

def ws(s):
    return re.sub(r"\s+", " ", s or "").strip()

n_files = n_cycles_with_span = n_multi = n_single = 0
echo_a = echo_b = echo_c = 0
n_next_checked = 0
examples = []
for f in sorted(glob.glob(os.path.join(ER, "open233_self_recovery_flow_runner_01_*", "instances_*", "*.json"))):
    try:
        d = json.load(open(f, encoding="utf-8"))
    except Exception:
        continue
    if "cycles" not in d:
        continue
    n_files += 1
    cyc = d["cycles"]
    for i, c in enumerate(cyc):
        for s in c.get("stage2_results", []):
            span = s.get("claim_span_text")
            if not span:
                continue
            n_cycles_with_span += 1
            parts = [p for p in span.split("\n") if p.strip()]
            if len(parts) < 2:
                n_single += 1
                continue
            n_multi += 1
            if i + 1 >= len(cyc):
                continue
            joined = ws(" ".join(parts))
            nxt = cyc[i + 1].get("stage2_results", [])
            n_next_checked += 1
            hit = None
            for t in nxt:
                for cand in (t.get("claim_text"), (t.get("dev") or {}).get("claim_in_article")):
                    cn = ws(cand)
                    if not cn:
                        continue
                    if cn == joined:
                        echo_a += 1; hit = ("a", cand)
                    elif joined in cn:
                        echo_b += 1; hit = ("b", cand)
                    else:
                        k = sum(1 for p in parts if ws(p) and ws(p) in cn)
                        if k >= 2:
                            echo_c += 1; hit = ("c", cand)
                    if hit:
                        break
                if hit:
                    break
            if hit and len(examples) < 20:
                examples.append({"file": os.path.relpath(f, ER).replace("\\", "/"), "cycle": c.get("cycle"), "kind": hit[0],
                                 "prior_span": span, "next_claim": hit[1]})

# ---------- 再構成方式: 実記録のclaim_span_textが10件(全て単一範囲)しか残っていないため、runnerの
# `annotate_claim_span_identity`と同じく「cycle開始時点の本文(en_text_before_rewrite等)でclaim_textを照合して確定範囲を再構成」し、
# 複数範囲になるものを`prior_issues`へ渡った文字列とみなす(check_01.pyの`base_resolve`=runner照合のコピー、委任_49再生と一致を自己検証済み)。
sys.path.insert(0, HERE)
import check_01 as c1
rc = {"n_blocking_claims_reconstructed": 0, "n_resolved": 0, "n_multi_range": 0, "n_multi_with_next_cycle": 0,
      "echo_exact(a)": 0, "echo_contains_joined(b)": 0, "echo_contains_2plus_ranges(c)": 0, "examples": [], "multi_range_examples": []}
for dd in sorted(glob.glob(os.path.join(ER, "open233_self_recovery_flow_runner_01_rep*"))):
    nm = os.path.basename(dd).split("_01_", 1)[1]
    m = re.match(r"rep(\d+)$", nm)
    if not m or int(m.group(1)) < 7:
        continue
    for f in sorted(glob.glob(os.path.join(dd, "instances_*", "*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        if "cycles" not in d:
            continue
        cyc = d["cycles"]
        for i, c in enumerate(cyc):
            en, ja = c1.cycle_texts(cyc, i)
            if en is None and ja is None:
                continue
            for s in c.get("stage2_results", []):
                if s.get("materiality") != "BLOCKING":
                    continue
                rc["n_blocking_claims_reconstructed"] += 1
                r = c1.base_resolve(s.get("claim_text") or "", en, ja, True)
                if r["status"] != "resolved":
                    continue
                rc["n_resolved"] += 1
                parts = [p for p in r["ranges"] if p.strip()]
                if len(parts) < 2:
                    continue
                rc["n_multi_range"] += 1
                if len(rc["multi_range_examples"]) < 5:
                    rc["multi_range_examples"].append({"file": os.path.relpath(f, ER).replace("\\", "/"), "cycle": c.get("cycle"),
                                                       "claim_span_text(再構成)": "\n".join(parts)})
                if i + 1 >= len(cyc):
                    continue
                rc["n_multi_with_next_cycle"] += 1
                joined = ws(" ".join(parts))
                hit = None
                for t in cyc[i + 1].get("stage2_results", []):
                    for cand in (t.get("claim_text"), (t.get("dev") or {}).get("claim_in_article")):
                        cn = ws(cand)
                        if not cn:
                            continue
                        if cn == joined:
                            rc["echo_exact(a)"] += 1; hit = ("a", cand)
                        elif joined in cn:
                            rc["echo_contains_joined(b)"] += 1; hit = ("b", cand)
                        elif sum(1 for p in parts if ws(p) in cn) >= 2:
                            rc["echo_contains_2plus_ranges(c)"] += 1; hit = ("c", cand)
                        if hit:
                            break
                    if hit:
                        break
                if hit and len(rc["examples"]) < 20:
                    rc["examples"].append({"file": os.path.relpath(f, ER).replace("\\", "/"), "cycle": c.get("cycle"),
                                           "kind": hit[0], "prior_span": "\n".join(parts), "next_claim": hit[1]})
res = {"reconstructed": rc, "n_instance_files": n_files, "n_stage2_results_with_claim_span_text": n_cycles_with_span,
       "n_single_range": n_single, "n_multi_range(改行連結あり)": n_multi,
       "n_multi_range_with_next_cycle": n_next_checked,
       "echo_exact(a)": echo_a, "echo_contains_joined(b)": echo_b, "echo_contains_2plus_ranges(c)": echo_c,
       "examples": examples}
json.dump(res, open(os.path.join(HERE, "echo_check_01_result.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1))
