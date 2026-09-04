# ============================================================
# er011_open113_point_context_only_trial_03.py
# OPEN-113-POINT-CONTEXT-ONLY-TRIAL-AND-POSTCHECK-INTEGRATION-AUDIT-03
# ============================================================
# 目的: 現行Production Local Rewrite(er010_ledger_local_rewrite_09.py)の
# System Prompt・Rule文言・出力形式・Retry回数・DELETE機能(なし)・
# Ledger再チェックロジック・NG条件を一切変更せず、Rewriteモデルへの入力に
# 「対象文が属するPoint全体」をcontextとして追加するだけで、Trial-01/02が
# 対象とした重複・過剰修正ケースにどう影響するかを検証する。
#
# Trial-01/02との違い:
# - Trial-01: Point context追加 + Prompt契約変更(DELETE追加等)を同時実施
#   → 単独効果を評価できなかった。
# - Trial-02: 階層Prompt契約(STEP1-4)を追加 → 過剰DELETE改善せず、
#   既知ケースが未解決に退行しREJECTED。
# - Trial-03(本ファイル): 変更変数を1点のみに絞る。現行Production Rule
#   文言(REWRITE_SYSTEM_PROMPT)はer010から直接importし、一切書き換えない。
#   3段階escalating attempt構造・DELETE機能なし・Retry上限3回・Ledger
#   再チェック呼び出し方法も現行のまま。ATTEMPT{1,2,3}_TEMPLATEには、
#   「[The full Point this sentence belongs to — reference only]」という
#   ラベル付きセクションを追加するのみで、新しいRule文(重複するな/
#   DELETEを優先せよ/flowを維持せよ等)は一切追加しない。
#
# Fixture: Trial-01のbuild_fixtures()/extract_section()/
# reconstruct_pre_rewrite_article()をそのまま再利用する(新しいNGケースを
# 作為的に作らない、Trial-01/02と同一の4件で比較可能にする)。
#
# 到達してよいStatus: REJECTED / VALIDATED / USER_DECISION_REQUIRED のみ。
# APPROVED_FOR_PRODUCTION・PRODUCTION_WIRED不可。Production code変更なし。
from __future__ import annotations

import json
import os
import time

if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as gen
import er010_ledger_local_rewrite_09 as local_rewrite
import er011_open113_local_rewrite_contract_tightening_trial_01 as trial01

OUT_DIR = "er011_output/open113_point_context_only_trial_03"

# ============================================================
# 現行ProductionのREWRITE_SYSTEM_PROMPTをそのまま使う(再定義・変更なし)。
# ============================================================
REWRITE_SYSTEM_PROMPT_PRODUCTION = local_rewrite.REWRITE_SYSTEM_PROMPT

# 現行Productionのテンプレートに、「Point全体を参考として見せるだけ」の
# セクションを1つ追加する。既存の指示文(ルール文)は一字一句変更しない。
# 新しいルール文("重複するな"等)も追加しない — ラベルと生テキストのみ。
POINT_CONTEXT_BLOCK = """[The full Point this sentence belongs to — shown for reference only]
{point_context}

"""

REWRITE_ATTEMPT1_TEMPLATE_PC = (
    "[Verified Fact Ledger]\n{ledger_text}\n\n"
    + POINT_CONTEXT_BLOCK
    + "[Sentence flagged as a Ledger deviation]\n{ng_sentence}\n\n"
      "[Checker's issue]\n{issue}\n\n"
      "Rewrite this sentence following the rules above. Return only the revised sentence."
)

REWRITE_ATTEMPT2_TEMPLATE_PC = (
    "[Verified Fact Ledger]\n{ledger_text}\n\n"
    + POINT_CONTEXT_BLOCK
    + "[Sentence still flagged after a first rewrite attempt]\n{ng_sentence}\n\n"
      "[Checker's issue]\n{issue}\n\n"
      "[Checker's explanation]\n{explanation}\n\n"
      "[Flags the checker marked true]\n{flags}\n\n"
      "Your previous rewrite still did not resolve this deviation. Rewrite it again, paying specific "
      "attention to the flags above. Return only the revised sentence."
)

REWRITE_ATTEMPT3_TEMPLATE_PC = (
    "[Verified Fact Ledger]\n{ledger_text}\n\n"
    + POINT_CONTEXT_BLOCK
    + "[Sentence still flagged after two rewrite attempts]\n{ng_sentence}\n\n"
      "[Checker's issue]\n{issue}\n\n"
      "This is the final attempt: use a Scope-safe fallback. Make the evidence's scope naturally "
      "explicit in the sentence (choose whichever fits the sentence naturally, do not just "
      "mechanically prepend a fixed phrase): \"In this study...\", \"Among these passengers...\", "
      "\"In these taxi rides...\", \"The study suggests...\", \"In this case...\", or similar. Keep as "
      "much of the original meaning and interest as possible. Return only the revised sentence."
)

# テンプレート文言が現行Productionの各行と一字一句一致していること自体を
# importテスト側で機械的に確認できるよう、Production側の行を集合として
# 保持しておく(このモジュール内では未使用、検証スクリプト用)。
_PRODUCTION_INSTRUCTION_LINES = {
    line for tmpl in (
        local_rewrite.REWRITE_ATTEMPT1_TEMPLATE, local_rewrite.REWRITE_ATTEMPT2_TEMPLATE,
        local_rewrite.REWRITE_ATTEMPT3_TEMPLATE,
    ) for line in tmpl.splitlines() if line.strip()
}


def rewrite_ng_item_point_ctx(client, model: str, reasoning_effort: str, verified_ledger_text: str,
                               point_context: str, ng_sentence: str, deviation: dict, before_ctx: str,
                               after_ctx: str, run_check_window_fn) -> dict:
    """er010_ledger_local_rewrite_09.rewrite_ng_itemと同一の制御フロー
    (3段階escalating attempt、DELETE機能なし、Retry上限3回、Ledger再チェック
    呼び出し方法も同一)。差分はプロンプトへpoint_contextを追加している点の
    みで、Rule文言・出力形式・NG条件は一切変更していない。"""
    flags_true = [k for k in vfl01.DEVIATION_FLAG_KEYS if deviation.get(k)]
    attempts = []
    accepted_text, accepted, human_review = None, False, False

    prompt1 = REWRITE_ATTEMPT1_TEMPLATE_PC.format(
        ledger_text=verified_ledger_text, point_context=point_context, ng_sentence=ng_sentence,
        issue=deviation["issue"])
    text1 = local_rewrite.generate_rewrite(client, model, reasoning_effort, prompt1)
    check1 = run_check_window_fn(f"{before_ctx} {text1} {after_ctx}".strip())
    attempts.append({"attempt": 1, "text": text1, "ledger_status": check1["overall_status"]})
    if check1["overall_status"] == "LEDGER_COMPLIANT":
        accepted_text, accepted = text1, True
    else:
        prompt2 = REWRITE_ATTEMPT2_TEMPLATE_PC.format(
            ledger_text=verified_ledger_text, point_context=point_context, ng_sentence=text1,
            issue=deviation["issue"], explanation=deviation["explanation"],
            flags=", ".join(flags_true) or "(none)")
        text2 = local_rewrite.generate_rewrite(client, model, reasoning_effort, prompt2)
        check2 = run_check_window_fn(f"{before_ctx} {text2} {after_ctx}".strip())
        attempts.append({"attempt": 2, "text": text2, "ledger_status": check2["overall_status"]})
        if check2["overall_status"] == "LEDGER_COMPLIANT":
            accepted_text, accepted = text2, True
        else:
            prompt3 = REWRITE_ATTEMPT3_TEMPLATE_PC.format(
                ledger_text=verified_ledger_text, point_context=point_context, ng_sentence=text2,
                issue=deviation["issue"])
            text3 = local_rewrite.generate_rewrite(client, model, reasoning_effort, prompt3)
            check3 = run_check_window_fn(f"{before_ctx} {text3} {after_ctx}".strip())
            attempts.append({"attempt": 3, "text": text3, "ledger_status": check3["overall_status"]})
            if check3["overall_status"] == "LEDGER_COMPLIANT":
                accepted_text, accepted = text3, True
            else:
                accepted_text, accepted, human_review = text3, False, True

    return {
        "original_ng_sentence": ng_sentence, "issue": deviation["issue"],
        "explanation": deviation["explanation"], "flags": flags_true, "attempts": attempts,
        "final_text": accepted_text, "resolved": accepted, "human_review_required": human_review,
    }


def run_fixture(client, fixture: dict) -> dict:
    pre_article = trial01.reconstruct_pre_rewrite_article(fixture["final_article_text"], fixture["items"])
    point_context = trial01.extract_section(pre_article, fixture["items"][0]["original_ng_sentence"])
    sentences = local_rewrite.split_sentences(pre_article)
    ledger_text = fixture["ledger_text"]
    ledger_model = fixture["ledger_model"]

    def _run_check_window(window_text: str) -> dict:
        # 現行Productionと同一: attempt単位のcheckは前後1文の窓のみで判定
        # する(Point全体ではない)。この関数の入力範囲自体はTrial-03でも
        # 変更しない(変更変数はRewrite生成側の入力のみ)。
        r = vfl01.run_deviation_check(client, ledger_text, window_text, model=ledger_model,
                                       hook_aware=True)
        return r["parsed"]

    item_results = []
    for item in fixture["items"]:
        ng_sentence = item["original_ng_sentence"]
        target, location_method = local_rewrite.locate_target_sentence(ng_sentence, pre_article)
        if target is None:
            target = ng_sentence
            location_method = "fixture_literal"
        try:
            sidx = sentences.index(target)
        except ValueError:
            sidx = -1
        before_ctx = sentences[sidx - 1] if 0 <= sidx - 1 else ""
        after_ctx = sentences[sidx + 1] if 0 <= sidx and sidx + 1 < len(sentences) else ""

        deviation = {"issue": item["issue"], "explanation": item["explanation"], **item["flags"]}
        print(f"[OPEN-113-T03][{fixture['id']}] item開始: {ng_sentence[:60]}...")
        r = rewrite_ng_item_point_ctx(client, ledger_model, gen.REASONING_EFFORT, ledger_text,
                                       point_context, ng_sentence, deviation, before_ctx, after_ctx,
                                       _run_check_window)
        r["location_method"] = location_method
        r["before_ctx"] = before_ctx
        r["after_ctx"] = after_ctx
        item_results.append(r)
        print(f"[OPEN-113-T03][{fixture['id']}] item完了: resolved={r['resolved']} "
              f"attempts={len(r['attempts'])} human_review={r['human_review_required']}")

    # 現行Productionのapply_rewrites()をそのまま使う(DELETE機能なし)。
    new_article = local_rewrite.apply_rewrites(pre_article, item_results)
    new_point_context = local_rewrite.apply_rewrites(point_context, item_results)

    print(f"[OPEN-113-T03][{fixture['id']}] cycle後、Ledger全体(全文)を再判定...")
    full_recheck = vfl01.run_deviation_check(client, ledger_text, new_article, model=ledger_model,
                                              hook_aware=True)
    full_recheck_parsed = full_recheck["parsed"]

    # 意味重複の簡易判定(read-onlyの目視補助用、正式な判定機構ではない):
    # Rewrite後文が、同一Point内の「他の」文と語彙的にどれだけ重なるかを
    # 記録する。新Validatorではなく、報告用の参考指標に留める。
    duplication_notes = []
    for r in item_results:
        if not r.get("resolved") or not r.get("final_text"):
            continue
        final_text = r["final_text"]
        other_sentences = [s for s in local_rewrite.split_sentences(new_point_context)
                            if s.strip() and s.strip() != final_text.strip()]
        duplication_notes.append({
            "final_text": final_text,
            "other_point_sentences_count": len(other_sentences),
        })

    return {
        "fixture_id": fixture["id"], "label": fixture["label"],
        "pre_article": pre_article, "point_context_before": point_context,
        "item_results": item_results, "new_article": new_article,
        "new_point_context": new_point_context,
        "duplication_notes": duplication_notes,
        "full_recheck_overall_status": full_recheck_parsed["overall_status"],
        "full_recheck_major_count": sum(
            1 for d in full_recheck_parsed["deviations"] if d["severity"] == "MAJOR"),
        "full_recheck_deviations": full_recheck_parsed["deviations"],
        "point_context_word_count_before": len(point_context.split()),
        "point_context_word_count_after": len(new_point_context.split()),
        "api_call_count": sum(len(r["attempts"]) * 2 for r in item_results) + 1,
    }


def main() -> dict:
    os.makedirs(OUT_DIR, exist_ok=True)
    client = vfl01.get_client()
    fixtures = trial01.build_fixtures()
    results = {}
    for fixture in fixtures:
        cache_path = f"{OUT_DIR}/{fixture['id']}.json"
        if os.path.exists(cache_path):
            with open(cache_path, encoding="utf-8") as f:
                res = json.load(f)
            results[fixture["id"]] = res
            print(f"[OPEN-113-T03][{fixture['id']}] キャッシュ済み結果を再利用します(再API呼び出しなし)。"
                  f"full_recheck_overall_status={res['full_recheck_overall_status']}")
            continue
        t0 = time.time()
        res = run_fixture(client, fixture)
        res["elapsed_seconds"] = round(time.time() - t0, 1)
        results[fixture["id"]] = res
        with open(f"{OUT_DIR}/{fixture['id']}.json", "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=2, default=str)
        print(f"[OPEN-113-T03][{fixture['id']}] 完了。full_recheck_overall_status="
              f"{res['full_recheck_overall_status']} major={res['full_recheck_major_count']} "
              f"api_calls={res['api_call_count']} elapsed={res['elapsed_seconds']}s")

    with open(f"{OUT_DIR}/trial03_summary.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    print(f"[OPEN-113-T03] 完了。summary -> {OUT_DIR}/trial03_summary.json")
    return results


if __name__ == "__main__":
    main()
