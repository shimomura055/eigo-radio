# -*- coding: utf-8 -*-
"""FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01 委任_03 Trial専用runner(Production経路ではない。Production module無改変)。
判断LLMのPrompt/検証V1〜V7は Trial_01 の overlay module を無改変で再利用する(モデルのみ gpt-6-luna へ変更)。
各stepは独立process(自動retryラッパなし)。
  --step build_prompts     (API 0: dataset全記事の判定Prompt生成+旧Prompt同一性確認)
  --step judge --variant luna_high --articles a,b,c   (有料: Luna判断)
  --step evaluate          (API 0: 事前登録ラベルとの照合、Sol対Luna)
Guardrail: 委任_03全体 JPY300(案件見積)。本ファイルのguardはROOT配下全logの合計が GUARD_STOP_JPY 超で新規call前停止。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time

import er003_v1_en_direct_vfl_01_generate as vfl01
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er053_cost_aggregate_01 as ca
import er053_family_x_factlock_ja_writer_01 as w1
import er090_b3_core_number_rounding_trial_01_overlay as ov
import er090_b3_core_number_rounding_trial_02_labels as lab

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "er090_output", "b3_core_number_rounding_trial_02")
T1 = os.path.join(HERE, "er090_output", "b3_core_number_rounding_trial_01")
GUARD_STOP_JPY = 270.0           # 案件見積JPY300に対する停止線(超過見込みで新規call前停止)
THEME_TAG = "FAMILY_X_B3_CORE_NUMBER_ROUNDING_TRIAL_01_D03"
LUNA_MODEL = "gpt-6-luna"
OVERRIDE_REASON = ("ユーザー指示(2026-10-22)による原価低減Trial: 丸め判断LLMをSol(gpt-6.1-sol)からLuna(gpt-6-luna)へ変更して比較。"
                   "B3本体・Production経路は無変更")
VARIANTS = {   # variant -> (model, effort)
    "luna_high": (LUNA_MODEL, "high"),
    "luna_medium": (LUNA_MODEL, "medium"),
    "luna_low": (LUNA_MODEL, "low"),
    "sol_high": ("gpt-6.1-sol", "high"),     # semi公平比較用(Trial_01のsemiはv1 Prompt)。Production routing(FAMILY_X_STORYLINE_B3)と一致
}
# 旧評価セットのSol基準(Trial_01 judge dir) -> article_id
PRIOR_SRC = {"A": "art_a31992b5", "coffee": "art_1e4c771e", "boredom": "art_701612d8", "semi": "art_36b2c87d"}


def sha_text(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def save_json(p, o):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(o, f, ensure_ascii=False, indent=2)


def load_json(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def total_cost_jpy() -> float:
    tot = 0.0
    for dp, _dn, fn in os.walk(ROOT):
        if "raw_usage_log.jsonl" in fn:
            tot += ca.compute_stage_cost_breakdown_multi(os.path.join(dp, "raw_usage_log.jsonl"))["total_jpy"]
    return round(tot, 3)


def guard(note=""):
    t = total_cost_jpy()
    print(f"[ROUNDING-TRIAL-D03][guard] cumulative={t:.3f} JPY (stop>{GUARD_STOP_JPY}) {note}")
    if t > GUARD_STOP_JPY:
        raise RuntimeError(f"[GUARDRAIL_STOP] cumulative {t} JPY > {GUARD_STOP_JPY} ({note})")


def article_dir(aid):
    return os.path.join(ROOT, "dataset", aid)


def load_article(aid):
    d = article_dir(aid)
    sc = load_json(os.path.join(d, "storyline_b3", "annotation.json"))
    ledger_text = open(os.path.join(d, "research_ledger", "verified_fact_ledger.txt"), encoding="utf-8").read()
    annotated = open(os.path.join(d, "storyline_b3", "selected_brief_annotated.md"), encoding="utf-8").read()
    story, facts_text = w1.parse_brief_md(annotated)
    cpath = os.path.join(d, "storyline_b3", "writer_constraints.txt")
    cons = open(cpath, encoding="utf-8").read() if os.path.exists(cpath) else ""
    return {"sidecar": sc, "ledger_text": ledger_text, "story": story, "facts_text": facts_text, "constraints": cons}


def build_prompt(aid):
    a = load_article(aid)
    recs = ov.parse_ledger_records(a["ledger_text"])
    return ov.build_judge_user_prompt(storyline=a["story"], facts_text=a["facts_text"], constraints_text=a["constraints"],
                                      sidecar=a["sidecar"], ledger_records=recs), a


def selected_manifest():
    """ラベル登録済み(=本Trialの対象)記事のみ。同テーマの別Ledger重複(hormuz/sewer/space等)はdataset_manifestに残すが対象外。"""
    labeled = {k[0] for k in lab.LABELS}
    return [m for m in load_json(os.path.join(ROOT, "dataset_manifest.json")) if m["article_id"] in labeled and m["n_core_concepts"] > 0]


def dataset_ids():
    return [m["article_id"] for m in selected_manifest()]


def step_build_prompts():
    res = {}
    for aid in dataset_ids():
        p, _ = build_prompt(aid)
        res[aid] = {"prompt_sha256": sha_text(p), "chars": len(p)}
    # 旧Trial_01 Promptとの同一性(評価セット4記事)
    same = {}
    for src, aid in PRIOR_SRC.items():
        tag = "A_rep1" if src == "A" else src
        old = open(os.path.join(T1, "judge", tag, "prompt.txt"), encoding="utf-8").read()
        new, _ = build_prompt(aid)
        same[src] = {"article": aid, "identical_to_trial01_prompt": old == new, "old_sha": sha_text(old), "new_sha": sha_text(new)}
    save_json(os.path.join(ROOT, "evidence", "prompt_manifest.json"), {"prompts": res, "prior_identity": same})
    print(json.dumps(same, ensure_ascii=False, indent=1))
    print("prompts:", len(res))


def judge_call(client, user_prompt, tag, variant):
    model_id, effort = VARIANTS[variant]
    model = routing.require_model_or_override("FAMILY_X_STORYLINE_B3", model_id, OVERRIDE_REASON)
    t0 = time.time()
    with cl.logging_context(THEME_TAG, tag):
        resp = client.responses.create(
            model=model, reasoning={"effort": effort},
            text={"format": {"type": "json_schema", **ov.JUDGE_JSON_SCHEMA}},
            input=[{"role": "developer", "content": ov.JUDGE_DEVELOPER_MESSAGE}, {"role": "user", "content": user_prompt}])
    u = getattr(resp, "usage", None)
    usage = {"input_tokens": getattr(u, "input_tokens", None), "output_tokens": getattr(u, "output_tokens", None),
             "reasoning_tokens": getattr(getattr(u, "output_tokens_details", None), "reasoning_tokens", None)} if u else {}
    return {"parsed": json.loads(resp.output_text), "raw_text": resp.output_text, "model": resp.model, "response_id": resp.id,
            "sec": round(time.time() - t0, 1), "effort": effort, "usage": usage}


def step_judge(variant, articles, rep):
    out_root = os.path.join(ROOT, "judge", f"{variant}_rep{rep}")
    cl.install(os.path.join(out_root, "raw_usage_log.jsonl"))
    client = vfl01.get_client()
    for aid in articles:
        out = os.path.join(out_root, aid)
        if os.path.exists(os.path.join(out, "overlay.json")):
            print("[judge] skip existing", variant, rep, aid)
            continue
        guard(f"before judge {variant} {aid}")
        prompt, a = build_prompt(aid)
        os.makedirs(out, exist_ok=True)
        open(os.path.join(out, "prompt.txt"), "w", encoding="utf-8", newline="\n").write(prompt)
        r = judge_call(client, prompt, f"judge_{variant}_r{rep}_{aid}", variant)
        save_json(os.path.join(out, "response.json"), r)
        overlay = ov.build_overlay(a["sidecar"], r["parsed"])
        overlay.update({"article_id": aid, "judge_model": r["model"], "judge_response_id": r["response_id"], "effort": r["effort"], "variant": variant})
        save_json(os.path.join(out, "overlay.json"), overlay)
        print(f"[judge] {variant} r{rep} {aid}: model={r['model']} approx_ok={overlay['n_approximate_ok']} violations={overlay['violations']} sec={r['sec']} usage={r['usage']}")


# ------------------------------------------------------------------ coverage (API 0)
def step_coverage():
    """dataset(機械選定された実中核数値)のユーザー§3の7カテゴリ充足を、表記から機械的に分類する。1数値が複数カテゴリに該当しうる。"""
    import re as _re
    man = selected_manifest()
    cats = {k: [] for k in ("C1_large_count_amount", "C2_decimal_ratio_precision", "C3_threshold_qualifier_close_compare",
                            "C4_date_count_small_quantity", "C5_multi_number_related_fact", "C6_already_hedged", "C7_same_form_context_dependent")}
    n_concepts = 0
    labeled = {"A": 0, "E": 0, "B": 0}
    for m in man:
        by_fact = {}
        for c in m["core"]:
            for i in c["ledger_ids"]:
                by_fact.setdefault(i, []).append(c["concept"])
        for c in m["core"]:
            n_concepts += 1
            s0 = c["surfaces"][0]
            key = (m["article_id"], s0)
            labeled[lab.LABELS[key]] += 1
            tag = f"{m['article_id']}:{s0}"
            v = ov.parse_surface(s0)["value"]
            if c["kind"] == "date_time" or _re.search(r"(年|月|日|回|件|分|人|か月|^\d{1,2}$)", s0) and (v is None or v < 1000):
                cats["C4_date_count_small_quantity"].append(tag)
            if v is not None and v >= 1000 and c["kind"] != "date_time" and not _re.search(r"[年月日]", s0):
                cats["C1_large_count_amount"].append(tag)
            if _re.search(r"[%％]|\.\d", s0) or c["kind"] == "range":
                cats["C2_decimal_ratio_precision"].append(tag)
            if any(q in s0 for q in ov.QUALIFIER_WORDS) or "対" in s0 or any(x["concept"] != c["concept"] and set(x["ledger_ids"]) & set(c["ledger_ids"]) and x["surfaces"][0].replace(",", "")[:3] != s0.replace(",", "")[:3] and "ドル" in s0 and "ドル" in x["surfaces"][0] for x in m["core"]):
                cats["C3_threshold_qualifier_close_compare"].append(tag)
            if max(len(by_fact.get(i, [])) for i in c["ledger_ids"]) >= 2:
                cats["C5_multi_number_related_fact"].append(tag)
            if any(h in s0 for h in ov.HEDGE_WORDS):
                cats["C6_already_hedged"].append(tag)
    # C7: 同じ"形"(大きな人数/台数 vs 小さな死傷者数・件数)で A/E が分かれる実例をラベルから列挙
    c7 = [("art_a31992b5:最大134,515人(A)", "art_4f7d28b0:309人(E)"), ("art_9d9f7170:141,006(A)", "art_9d9f7170:15(E)"),
          ("art_701612d8:1,332(A)", "art_701612d8:最大50(E)"), ("art_36b2c87d:295億9,100万ドル(B)", "art_36b2c87d:約348億ドル(E)"),
          ("art_06ae3dca:183,211台(A)", "art_06ae3dca:142,895台(B)")]
    cats["C7_same_form_context_dependent"] = [f"{a} vs {b}" for a, b in c7]
    out = {"articles_distinct_ledger": len(man), "articles_with_core": len(man), "facts_total": sum(m["n_facts"] for m in man),
           "core_concepts_total": n_concepts, "core_surfaces_total": sum(m["n_core_surfaces"] for m in man),
           "label_distribution": labeled, "category_counts": {k: len(v) for k, v in cats.items()}, "category_members": cats,
           "artificial_fixtures": 0, "note": "人工fixtureは使用しない(7カテゴリが実中核数値で充足されるため)"}
    save_json(os.path.join(ROOT, "evidence", "coverage.json"), out)
    print(json.dumps({k: v for k, v in out.items() if k != "category_members"}, ensure_ascii=False, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", required=True, choices=("build_prompts", "judge", "coverage"))
    ap.add_argument("--variant", choices=tuple(VARIANTS))
    ap.add_argument("--articles", default="")
    ap.add_argument("--rep", type=int, default=1)
    a = ap.parse_args()
    os.makedirs(ROOT, exist_ok=True)
    if a.step == "build_prompts":
        step_build_prompts()
    elif a.step == "coverage":
        step_coverage()
    elif a.step == "judge":
        arts = [x for x in a.articles.split(",") if x] or dataset_ids()
        step_judge(a.variant, arts, a.rep)


if __name__ == "__main__":
    main()
