# -*- coding: utf-8 -*-
"""er083_c1_positive_control_01_eval.py
C1陽性対照Trialの**機械判定**(事前固定。判定基準は C1_POSITIVE_CONTROL_DESIGN_01.md §5)と、盲検パック作成、費用集計。API 0。
内容の善し悪し(ストーリー性維持・理解しやすさ・誤帰属/因果/網羅化の有無)は盲検rubric(別process・ラベル隠蔽)で判定し、ここでは判定しない。

  python er083_c1_positive_control_01_eval.py --design <matrix.json> --out-root <dir> [--dry-run] [--blind-pack <md>] [--cost-summary]

機械判定(評価項目 → 判定):
 1 必要な背景Factを追加したか      : 陽性Ledgerで C1セルの採用IDが expected_core を含む(sample毎)。2/2で POS_ADDED_2of2
 2 不必要なFactを追加していないか  : 期待外追加(= 【背景補完】付き∖(expected_core∪expected_ok)、およびマーカー無しの追加)= extras。陰性Ledgerは追加0で NEG_PASS
 4 Writer入力経路への反映          : 決定論的追跡(採用ID→annotation.json facts[].ledger_ids→契約検証V1-V10→rules_sha256不変)。本文使用のキーワードは参考値(本判定は盲検)
 (3・5・6 は盲検rubric)
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys

import er083_b3_background_fact_trial_01_lib as lib
import er053_b3_deterministic_producer_01 as annot

# 事前固定(設計書 §5)
SAMPLES_REQUIRED = 2                 # 陽性: C1が2/2 sampleで期待Factを追加
MAX_SELECTED = 5                     # 総採用6件以上は問題(前Trial rubric軸3)


def _cells(out_root: str, design: dict, dry_run: bool) -> list:
    base = os.path.join(out_root, "_dryrun") if dry_run else out_root
    rows = []
    for L in design["ledgers"]:
        for cond in design["conditions"]:
            for s in design["samples"]:
                d = os.path.join(base, L["id"], cond, f"s{s}")
                mp = os.path.join(d, "trial_meta.json")
                if not os.path.isfile(mp):
                    continue
                m = json.loads(lib.read_text(mp))
                m["_dir"], m["_ledger"], m["_cond"], m["_sample"] = d, L["id"], cond, s
                rows.append(m)
    return rows


def trace_writer_path(cell: dict, fact_id: str) -> dict:
    """項目4(機械部分): 追加Factが既存のWriter入力経路(producer→契約→W-1入力)に乗ることを決定論的に確認する。LLM 0。"""
    d = cell["_dir"]
    stage = os.path.join(d, "storyline_b3")
    out = {"fact_id": fact_id, "in_selected": fact_id in ((cell.get("analysis") or {}).get("selected_fact_ids") or [])}
    ap = os.path.join(stage, "annotation.json")
    if os.path.isfile(ap):
        ann = json.loads(lib.read_text(ap))
        out["in_sidecar_facts"] = any(fact_id in (f.get("ledger_ids") or []) for f in ann.get("facts", []))
    else:
        out["in_sidecar_facts"] = False
    wp = os.path.join(stage, "writer_constraints.txt")
    out["writer_constraints_present"] = os.path.isfile(wp)
    try:
        from er053_b3_annotation_contract_01 import validate_annotated_b3
        validate_annotated_b3(d)
        out["contract_v1_v10"] = "PASS"
    except Exception as e:                               # 契約違反=Writer到達不可
        out["contract_v1_v10"] = f"FAIL: {type(e).__name__}: {str(e)[:160]}"
    out["rules_sha256"] = (cell.get("producer") or {}).get("rules_sha256")
    out["rules_sha256_unchanged"] = out["rules_sha256"] == annot.rules_sha256()
    return out


def writer_text_hint(cell: dict, keywords: list) -> dict:
    """参考値: W-1本文(revision2.md)に期待Factを示すキーワードが含まれるか。これは本判定ではない(本判定は盲検rubric)。"""
    p = os.path.join(cell["_dir"], "ja_writer", "revision2.md")
    if not os.path.isfile(p):
        return {"ja_text_present": False}
    t = lib.read_text(p)
    return {"ja_text_present": True, "keywords": {k: (k in t) for k in keywords}, "chars": len(t)}


def judge_ledger(L: dict, rows: list) -> dict:
    mine = [r for r in rows if r["_ledger"] == L["id"]]
    base = sorted([r for r in mine if r["_cond"] == "baseline"], key=lambda r: r["_sample"])
    c1 = sorted([r for r in mine if r["_cond"] == "C1"], key=lambda r: r["_sample"])
    core, ok = set(L["expected_core"]), set(L["expected_ok"])
    baseline_union = set(L["prior_baseline_selection"])
    for r in base:
        baseline_union |= set((r.get("analysis") or {}).get("selected_fact_ids") or [])
    base_hits = [bool(core & set((r.get("analysis") or {}).get("selected_fact_ids") or [])) for r in base]
    per = []
    for r in c1:
        an = r.get("analysis") or {}
        sel, supp = set(an.get("selected_fact_ids") or []), set(an.get("supplement_fact_ids") or [])
        extras_marked = sorted(supp - core - ok)
        unmarked_new = sorted((sel - supp) - baseline_union - core - ok)
        per.append({
            "sample": r["_sample"], "selected": an.get("selected_fact_ids"), "supplement": sorted(supp),
            "core_hit": bool(core & sel), "core_marked": bool(core & supp), "extras_marked": extras_marked, "unmarked_new": unmarked_new,
            "n_selected": an.get("n_selected"), "over_max_selected": (an.get("n_selected") or 0) > MAX_SELECTED,
            "min2_met_only_via_supplement": an.get("min2_met_only_via_supplement"), "status": r.get("status"),
            "final_result_call": r.get("final_result_call"), "recheck_note": an.get("background_confirm_note"),
            "trace": {f: trace_writer_path(r, f) for f in sorted(core & sel)},
        })
    out = {"ledger_id": L["id"], "role": L["role"], "baseline_hits": base_hits, "baseline_union": sorted(baseline_union), "c1": per}
    extras_total = sum(len(p["extras_marked"]) + len(p["unmarked_new"]) for p in per)
    flags = []
    if any(p["min2_met_only_via_supplement"] for p in per):
        flags.append("MIN2_ONLY_VIA_SUPPLEMENT")
    if any(p["over_max_selected"] for p in per):
        flags.append("OVER_MAX_SELECTED")
    if any(p["core_hit"] and not p["core_marked"] for p in per):
        flags.append("CORE_ADDED_WITHOUT_MARKER")
    if any(str(p["status"]).startswith("B3_MIN2_STOP") for p in per):
        flags.append("B3_MIN2_STOP")
    out["extras_total"], out["flags"] = extras_total, flags
    if L["role"] == "positive":
        n = len(per)
        hits = sum(p["core_hit"] for p in per)
        if n < SAMPLES_REQUIRED:
            v = "INCOMPLETE"
        elif hits == n and all(base_hits) and len(base_hits) >= 1:
            v = "NONDISCRIMINATING"           # Baselineも全sampleで期待Factを採用: C1の効果と分離できない
        elif hits == n:
            v = "POS_ADDED_2of2"
        elif hits > 0:
            v = "POS_PARTIAL"
        else:
            v = "POS_NOT_ADDED"
    else:
        n = len(per)
        v = "INCOMPLETE" if n < SAMPLES_REQUIRED else ("NEG_PASS" if all(not p["supplement"] and not p["unmarked_new"] for p in per) else "NEG_FAIL")
    out["verdict"] = v
    return out


def overall(judged: list) -> dict:
    pos = [j for j in judged if j["role"] == "positive"]
    neg = [j for j in judged if j["role"] == "negative"]
    vs = {j["ledger_id"]: j["verdict"] for j in judged}
    flags = sorted({f for j in judged for f in j["flags"]})
    pos_eval = [j for j in pos if j["verdict"] != "NONDISCRIMINATING"]   # Baselineも採用した陽性Ledgerは効果を分離できないため判定から除く
    if any(v == "INCOMPLETE" for v in vs.values()):
        label = "INCOMPLETE"
    elif any(j["verdict"] == "NEG_FAIL" for j in neg) or (pos_eval and all(j["verdict"] == "POS_NOT_ADDED" for j in pos_eval)):
        label = "REJECTED_CANDIDATE_MACHINE"          # 陰性で追加、または判別可能な陽性で全く追加しない
    elif (pos_eval and all(j["verdict"] == "POS_ADDED_2of2" for j in pos_eval) and all(j["verdict"] == "NEG_PASS" for j in neg)
          and not any(j["extras_total"] for j in judged) and not flags):
        label = "VALIDATED_CANDIDATE_MACHINE"         # 残り: Writer到達・本文使用・盲検rubric(項目3・5・6)
    else:
        label = "MIXED_NEEDS_FABLE_REPLAN"            # 一部のみ成功/全陽性がNONDISCRIMINATING/期待外追加あり: 原因分析→修正再検証 or 判断候補
    return {"label": label, "per_ledger": vs, "flags": flags,
            "note": "機械判定のみ。VALIDATED化には Writer到達(trace)・本文使用・盲検rubric(項目3・5・6)が必要。Production採用は人間ユーザーのみ"}


def blind_pack(rows: list, design: dict, pack_path: str, seed: int = 20261020) -> dict:
    """W-1記事(baseline/C1)をA/Bに伏せた盲検パック。key別ファイル。記事が無いledgerは出さない。"""
    rng = random.Random(seed)
    key, parts = {}, ["# C1陽性対照 盲検パック(記事ラベル・条件名・Fact IDは伏せてある。rubric=C1_POSITIVE_CONTROL_DESIGN_01.md §6)\n"]
    for L in design["ledgers"]:
        arts = []
        for cond in ("baseline", "C1"):
            for r in sorted([r for r in rows if r["_ledger"] == L["id"] and r["_cond"] == cond], key=lambda r: r["_sample"]):
                p = os.path.join(r["_dir"], "ja_writer", "revision2.md")
                if os.path.isfile(p):
                    arts.append((cond, r["_sample"], lib.read_text(p)))
                    break
        if len(arts) < 2:
            continue
        rng.shuffle(arts)
        parts.append(f"\n## 題材{len(key) + 1}\n- テーマ: {L['topic'][:80]}\n")
        key[L["id"]] = {}
        for i, (cond, s, text) in enumerate(arts):
            label = "AB"[i]
            key[L["id"]][label] = {"cond": cond, "sample": s}
            parts.append(f"\n### 記事{label}\n\n{text}\n")
    lib.write_text(pack_path, "".join(parts))
    lib.write_json(os.path.join(os.path.dirname(pack_path), "blind_key.json"), key)
    return key


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--design", required=True)
    ap.add_argument("--out-root", required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--blind-pack", default=None)
    ap.add_argument("--cost-summary", action="store_true")
    a = ap.parse_args(argv)
    design = json.loads(lib.read_text(a.design))
    out_root = os.path.abspath(a.out_root)
    if a.cost_summary:
        print(json.dumps(lib.cost_summary_tree(out_root), ensure_ascii=False, indent=2))
        return 0
    rows = _cells(out_root, design, a.dry_run)
    judged = [judge_ledger(L, rows) for L in design["ledgers"]]
    result = {"dry_run": a.dry_run, "n_cells": len(rows), "judged": judged, "overall": overall(judged),
              "writer_hint": {}}
    for L in design["ledgers"]:
        for r in rows:
            if r["_ledger"] == L["id"] and L["usage_keywords"]:
                kws = sorted({k for v in L["usage_keywords"].values() for k in v})
                h = writer_text_hint(r, kws)
                if h.get("ja_text_present"):
                    result["writer_hint"][f"{L['id']}:{r['_cond']}:s{r['_sample']}"] = h
    if a.dry_run:
        result["overall"]["note"] = "[DRY-RUN: 合成応答による経路確認のみ。このラベルは実LLM結果ではない] " + result["overall"]["note"]
    if a.blind_pack:
        result["blind_key"] = blind_pack(rows, design, os.path.abspath(a.blind_pack))
    out_p = os.path.join(out_root, "_dryrun" if a.dry_run else "", "c1_posctrl_eval.json")
    lib.write_json(out_p, result)
    print(json.dumps({"overall": result["overall"], "n_cells": len(rows), "out": out_p}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
