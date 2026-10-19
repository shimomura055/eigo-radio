# -*- coding: utf-8 -*-
"""ITEM1 実LLM Regression(FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01 委任_05、Opus_E F1-5)。

目的: 承認済み①(人称・指示対象整合)の受入evidence。記事・特定表現に依存しない合成item(英語KP+具体人称の候補+旧日本語意味+文脈文)を、
Production経路の `er003_key_words_gloss_alignment.align_glosses`(決定論の人称語突合+理由付きretry込み)へそのまま通し、
(1) 不定の人称が日本語でも不定のまま保たれるか (2) 同一KPを「代わり」義/「立場」義の2文脈に置いたとき文脈が語義選択にだけ効くか
(3) 健全な対照itemが不必要に書き換えられないか、を確認する。
モデル: Production経路(gloss再整合)と同一(routing.SUPPORT_MODEL、process=A2_SUPPORT)。検証対象が本番経路のため(25節の「最新でない理由」に該当)。
有料: 1 batch(全itemを1リクエスト、Productionと同じ形)。最大2 attempt(既存retry上限)。上限は--budget-jpy(既定3円)。
"""
from __future__ import annotations

import argparse
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, REPO)

import er003_key_words_gloss_alignment as ga  # noqa: E402

REASON = "generalize_person_dependent_reference"

# id, KP(一般形), 候補(具体人称), 旧日本語意味(stale), 文脈文, 語義の期待(いずれかを含む), 不定標識が必要か
ITEMS = [
    ("P1a", "in someone's place", "in your place", "あなたの代わりに",
     "My friend will work in your place tomorrow, so you can rest.", ("代わり", "かわり", "代理", "替わり"), True),
    ("P1b", "in someone's place", "in your place", "あなたの立場で",
     "If I were in your place, I would say no to the offer.", ("立場", "身になって", "状況"), True),
    ("P2", "catch someone's attention", "catch their attention", "彼らの注意を引く",
     "The bright sign managed to catch their attention from far away.", ("注意", "気", "目"), True),
    ("P3", "tell someone off", "tell him off", "彼を叱る",
     "The teacher had to tell him off for being late again.", ("叱", "怒", "しか"), True),
    ("P4", "keep an eye on someone", "keep an eye on her", "彼女を見守る",
     "Could you keep an eye on her while I make a phone call?", ("見守", "見張", "目を", "気を配", "注意", "世話"), True),
    ("P5", "at one's own pace", "at your own pace", "あなたのペースで",
     "Please work through the lessons at your own pace.", ("ペース", "速さ", "自分"), False),
    ("P6", "take care of oneself", "take care of yourself", "あなた自身を大切にする",
     "You should take care of yourself during the busy season.", ("大切", "大事", "気を付け", "気をつけ", "世話", "体", "労"), False),
    ("P7", "give someone a hand", "give me a hand", "私に手を貸す",
     "Could you give me a hand with these boxes?", ("手", "助け", "手伝"), True),
    ("P8", "lose one's temper", "lose my temper", "私は腹を立てる",
     "I try not to lose my temper when the train is late.", ("腹", "怒", "かっと", "カッと", "冷静", "我慢"), False),
    ("P9", "not someone's cup of tea", "not my cup of tea", "私の好みではない",
     "Horror movies are really not my cup of tea.", ("好み", "趣味", "得意", "性に合"), True),
    ("P10", "put oneself in someone's shoes", "put yourself in my shoes", "あなたが私の立場に身を置く",
     "Try to put yourself in my shoes before you judge me.", ("立場", "身", "気持ち", "状況"), False),
    ("C1", "shock someone's wallet", "shock your wallet", "財布に響く",
     "The new price may shock your wallet at the end of the month.", ("財布", "出費", "家計"), False),
]


def build_merged() -> dict:
    items = []
    for i, (iid, kp, disp, gloss, sent, _, _) in enumerate(ITEMS, 1):
        items.append({"rank": i, "source_span": disp, "source_sentence": sent, "display_phrase": disp, "key_phrase": kp,
                      "used_form": kp, "japanese_gloss": gloss, "japanese_gloss_tts": gloss,
                      "changed_from_display_phrase": True, "normalization_reason": REASON,
                      "kp_extends_beyond_candidate": False, "gloss_review_hint": False})
    return {"items": items, "overall_status": "CANONICALIZATION_PASS"}


INDEF_MARKERS = ("誰か", "だれか", "人", "相手", "自分", "他人")


def judge(iid, kp, gloss, expect_any, need_marker, status, old_gloss):
    checks = {
        "alignment_status_ALIGNED": status == ga.STATUS_ALIGNED,
        "no_concrete_person_word(production_check)": ga.person_reference_mismatch(kp, gloss) is None,
        "sense_expected": any(w in gloss for w in expect_any),
        "indefinite_marker": (not need_marker) or any(m in gloss for m in INDEF_MARKERS),
    }
    return all(checks.values()), checks


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget-jpy", type=float, default=3.0)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    # 事前(API 0): 対象選定の確認
    merged = build_merged()
    targets = ga.select_generation_targets(merged["items"])
    assert len(targets) == len(ITEMS), "全itemが生成用の対象になること"
    offline = {
        "controls_not_targeted": all(not ga.select_generation_targets([{"rank": 1, "display_phrase": d, "key_phrase": k, "japanese_gloss": g}])
                                     for k, d, g in (("tell me off", "tell me off", "私を叱る"), ("thank you", "thank you", "あなたに感謝する"))),
        "consumer_unevaluated_before": [x["rank"] for x in ga.collect_unevaluated(merged)],
    }

    import er006_model_routing_contract_01 as routing
    import er005_cost_logger as cl
    import er062_family_z_structure_01 as st
    out_dir = os.path.dirname(os.path.abspath(a.out))
    raw_log = os.path.join(out_dir, "item1_llm_regression_05_raw_usage_log.jsonl")
    st.check_stop_sentinel("item1_llm_regression_05", out_dir)
    cl.install(raw_log)
    st.install_api_stop_guard()
    model = routing.require_model("A2_SUPPORT", routing.SUPPORT_MODEL)

    def factory(msg: str):
        return ga.make_alignment_fn(msg, model=model)

    # 概算の事前guard(実測1回約0.06円/6 item。12 item x 最大2 attemptでも1円未満)
    est = 0.06 * (len(ITEMS) / 6.0) * 2
    if est > a.budget_jpy:
        print(f"[STOP] 概算{est:.2f}円が上限{a.budget_jpy}円を超える")
        return 3
    article = "\n".join(it[4] for it in ITEMS)
    with cl.logging_context("item1_llm_regression_05", "kp_gloss_alignment"):
        res = ga.align_glosses(merged, article, factory, out_dir=os.path.join(out_dir, "item1_llm_regression_05_artifacts"),
                               article_id="item1_regression_05", enabled=True)
    new_by = {it["rank"]: it for it in res["merged"]["items"]}
    rows, all_ok = [], True
    for i, (iid, kp, disp, old, sent, expect_any, need_marker) in enumerate(ITEMS, 1):
        it = new_by[i]
        ok, checks = judge(iid, kp, it["japanese_gloss"], expect_any, need_marker, it.get("gloss_alignment_status"), old)
        attempts = len((res.get("item_log") or {}).get(i, []))
        rows.append({"id": iid, "key_phrase": kp, "context": sent, "old_gloss": old, "new_gloss": it["japanese_gloss"],
                     "status": it.get("gloss_alignment_status"), "attempts": attempts, "expect_sense_any": list(expect_any),
                     "pass": ok, "checks": checks})
        all_ok = all_ok and ok
    # 実費(raw_usage_logから実測。F-1)
    import er009_n1_routing_governance_10_actual_model_cost as pricing
    cost_raw, n_calls, toks = 0.0, 0, {"in": 0, "out": 0}
    for line in open(raw_log, encoding="utf-8"):
        e = json.loads(line)
        if not e.get("success"):
            continue
        n_calls += 1
        toks["in"] += e.get("input_tokens") or 0
        toks["out"] += e.get("output_tokens") or 0
        cost_raw += pricing.cost_jpy_for_call(e.get("provider", "openai"), e.get("model_id"), e.get("input_tokens"),
                                              e.get("cached_input_tokens"), e.get("output_tokens"))
    result = {"managed_id": "FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01 委任_05", "model": model,
              "model_note": "Production経路(gloss再整合)と同一モデル。検証対象が本番経路のため(25節の最新でない理由)",
              "align_status": res["status"], "targets": res["targets"], "unresolved_ranks": res.get("unresolved_ranks"),
              "attempts_summary": [{k: v for k, v in at.items() if k not in ("parsed",)} for at in res["attempts"]],
              "all_pass": all_ok, "rows": rows, "offline": offline,
              "cost": {"align_cost_jpy": res.get("cost_jpy"), "raw_usage_log_cost_jpy": round(cost_raw, 4),
                       "raw_usage_log_calls": n_calls, "tokens": toks, "source": raw_log, "budget_jpy": a.budget_jpy},
              "constraint_text_sha256": __import__("hashlib").sha256(ga.PERSON_CONSTRAINT_TEXT.encode("utf-8")).hexdigest()}
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"status={res['status']} all_pass={all_ok} cost_raw={cost_raw:.4f}JPY calls={n_calls}")
    for r in rows:
        print(f"[{'PASS' if r['pass'] else 'FAIL'}] {r['id']}: {r['key_phrase']} | {r['old_gloss']} -> {r['new_gloss']} "
              f"(status={r['status']}, attempts={r['attempts']})")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
