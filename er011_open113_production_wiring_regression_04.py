# ============================================================
# er011_open113_production_wiring_regression_04.py
# OPEN-113-POINT-CONTEXT-PRODUCTION-WIRING-AND-NO18-B1-REGEN-04
# ============================================================
# 目的: OPEN-113 Trial-03でVALIDATEDとなり、今回er010_ledger_local_rewrite_09.py
# (Production)へ正式配線したPoint-context-only方式を、Trial専用の再実装
# ではなく、実際のProduction関数(local_rewrite.rewrite_ng_item /
# local_rewrite.extract_point_context / local_rewrite.apply_rewrites)を
# 直接呼び出してRegressionする。
#
# Trial-03との違い: Trial-03は比較のため専用のPC付きtemplate/関数
# (REWRITE_ATTEMPT{1,2,3}_TEMPLATE_PC・rewrite_ng_item_point_ctx)を
# 独自定義していたが、本スクリプトはそれらを一切使わず、
# er010_ledger_local_rewrite_09.pyへ配線済みの本番関数のみを呼び出す
# (Trial専用実装ではないことの証明)。
#
# Fixture: Trial-01のbuild_fixtures()/reconstruct_pre_rewrite_article()を
# そのまま再利用する(新しいNGケースを作らない、Trial-01/02/03と同一の
# 4件で比較可能にする)。fixtureデータの再利用であり、Trial側のRewrite
# ロジック(extract_section等)はimportしない。
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

OUT_DIR = "er011_output/open113_production_wiring_regression_04"


def run_fixture(client, fixture: dict) -> dict:
    pre_article = trial01.reconstruct_pre_rewrite_article(fixture["final_article_text"], fixture["items"])
    sentences = local_rewrite.split_sentences(pre_article)
    ledger_text = fixture["ledger_text"]
    ledger_model = fixture["ledger_model"]

    def _run_check_window(window_text: str) -> dict:
        r = vfl01.run_deviation_check(client, ledger_text, window_text, model=ledger_model,
                                       hook_aware=True)
        return r["parsed"]

    item_results = []
    article_text = pre_article
    for item in fixture["items"]:
        ng_sentence = item["original_ng_sentence"]
        target, location_method = local_rewrite.locate_target_sentence(ng_sentence, article_text)
        if target is None:
            target = ng_sentence
            location_method = "fixture_literal"
        try:
            sidx = sentences.index(target)
        except ValueError:
            sidx = -1
        before_ctx = sentences[sidx - 1] if 0 <= sidx - 1 else ""
        after_ctx = sentences[sidx + 1] if 0 <= sidx and sidx + 1 < len(sentences) else ""

        # OPEN-113-POINT-CONTEXT-PRODUCTION-WIRING-04: Production配線と全く
        # 同一の手順(er003_v1_n3_01_articles_generate.pyのrun_one_pattern内
        # local rewriteループと同じ呼び出し順)。Trial専用の再実装は使わない。
        point_context = local_rewrite.extract_point_context(article_text, target)
        point_context_found = point_context is not None
        if point_context is None:
            point_context = f"{before_ctx} {target} {after_ctx}".strip()

        deviation = {"issue": item["issue"], "explanation": item["explanation"], **item["flags"]}
        print(f"[OPEN-113-PROD-REGRESSION-04][{fixture['id']}] item開始: {ng_sentence[:60]}...")
        r = local_rewrite.rewrite_ng_item(client, ledger_model, gen.REASONING_EFFORT, ledger_text,
                                           point_context, ng_sentence, deviation, before_ctx,
                                           after_ctx, _run_check_window)
        r["location_method"] = location_method
        r["before_ctx"] = before_ctx
        r["after_ctx"] = after_ctx
        r["point_context_found"] = point_context_found
        r["point_context"] = point_context
        item_results.append(r)
        print(f"[OPEN-113-PROD-REGRESSION-04][{fixture['id']}] item完了: resolved={r['resolved']} "
              f"attempts={len(r['attempts'])} human_review={r['human_review_required']} "
              f"point_context_found={point_context_found}")

    # 現行Productionのapply_rewrites()をそのまま使う(DELETE機能なし)。
    new_article = local_rewrite.apply_rewrites(pre_article, item_results)

    print(f"[OPEN-113-PROD-REGRESSION-04][{fixture['id']}] cycle後、Ledger全体(全文)を再判定...")
    full_recheck = vfl01.run_deviation_check(client, ledger_text, new_article, model=ledger_model,
                                              hook_aware=True)
    full_recheck_parsed = full_recheck["parsed"]

    # 意味重複の簡易判定(read-onlyの目視補助用、正式な判定機構ではない、
    # Trial-03と同一の参考指標)。
    duplication_notes = []
    for r in item_results:
        if not r.get("resolved") or not r.get("final_text"):
            continue
        final_text = r["final_text"]
        point_ctx_after = local_rewrite.extract_point_context(new_article, final_text) or ""
        other_sentences = [s for s in local_rewrite.split_sentences(point_ctx_after)
                            if s.strip() and s.strip() != final_text.strip()]
        duplication_notes.append({
            "final_text": final_text,
            "other_point_sentences_count": len(other_sentences),
        })

    return {
        "fixture_id": fixture["id"], "label": fixture["label"],
        "pre_article": pre_article,
        "item_results": item_results, "new_article": new_article,
        "duplication_notes": duplication_notes,
        "full_recheck_overall_status": full_recheck_parsed["overall_status"],
        "full_recheck_major_count": sum(
            1 for d in full_recheck_parsed["deviations"] if d["severity"] == "MAJOR"),
        "full_recheck_deviations": full_recheck_parsed["deviations"],
        "api_call_count": sum(len(r["attempts"]) * 2 for r in item_results) + 1,
        "all_point_context_found": all(r["point_context_found"] for r in item_results),
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
            print(f"[OPEN-113-PROD-REGRESSION-04][{fixture['id']}] キャッシュ済み結果を再利用します"
                  f"(再API呼び出しなし)。full_recheck_overall_status={res['full_recheck_overall_status']}")
            continue
        t0 = time.time()
        res = run_fixture(client, fixture)
        res["elapsed_seconds"] = round(time.time() - t0, 1)
        results[fixture["id"]] = res
        with open(f"{OUT_DIR}/{fixture['id']}.json", "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=2, default=str)
        print(f"[OPEN-113-PROD-REGRESSION-04][{fixture['id']}] 完了。full_recheck_overall_status="
              f"{res['full_recheck_overall_status']} major={res['full_recheck_major_count']} "
              f"api_calls={res['api_call_count']} elapsed={res['elapsed_seconds']}s "
              f"all_point_context_found={res['all_point_context_found']}")

    with open(f"{OUT_DIR}/regression04_summary.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    print(f"[OPEN-113-PROD-REGRESSION-04] 完了。summary -> {OUT_DIR}/regression04_summary.json")
    return results


if __name__ == "__main__":
    main()
