# ============================================================
# er011_open113_local_rewrite_contract_tightening_trial_01.py
# OPEN-113-LOCAL-REWRITE-CONTRACT-TIGHTENING-TRIAL-01
# ============================================================
# 目的: Local RewriteがLedger Deviation MAJORを解消する際に、unsupportedな
# 意味を別のLedger Factで埋め合わせることで、同じPoint内の既存文と意味
# 重複を起こす問題(No.18 B1 / OPEN-112 Trial-05 / Point Two)を、
# Local Rewrite Prompt契約の改善だけで防げるかを検証する。
#
# 対象: Prompt契約の改善のみ。Post-Rewrite Semantic Checker等の新規QAは
# 追加しない。Production(er010_ledger_local_rewrite_09.py /
# er003_v1_n3_01_articles_generate.py)は一切変更しない。
#
# 到達してよいStatus: REJECTED / VALIDATED / USER_DECISION_REQUIRED のみ。
# APPROVED_FOR_PRODUCTION・PRODUCTION_WIRED不可。
#
# 設計方針: 既存Local Rewrite(er010_ledger_local_rewrite_09.py)と同じ
# 3段階escalating attempt構造(1回のgenerate call + 1回のcheck call)を
# そのまま踏襲し、追加API callを増やさない。変更するのはprompt文言のみ:
#   - REWRITE_SYSTEM_PROMPT_V2: unrelated fact substitution・既出Factの
#     言い換え再提示・新Fact追加を明示的に禁止し、DELETEを正式な選択肢
#     として追加。
#   - ATTEMPT{1,2,3}_TEMPLATE_V2: 対象文の前後1文だけでなく、その文が
#     属する「Point全体」をcontextとして渡す(既存callの入力を増やす
#     だけで、call数自体は増やさない)。
#
# Fixture: 過去のProduction/Trial実行データから、対象文・issue・
# explanation・flags・Point全体・前後文を実ファイルから復元する
# (新しいNGケースを作為的に作らない)。Ledger Deviation Checkerの判定
# ・Fact Ledgerはすべて実データ・実APIを使用(モック不使用)。
from __future__ import annotations

import json
import os
import re
import time

if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as gen
import er010_ledger_local_rewrite_09 as local_rewrite

OUT_DIR = "er011_output/open113_local_rewrite_contract_tightening_trial_01"

# ============================================================
# Layer 1: 新Local Rewrite契約(Trial専用、Productionには一切書き込まない)
# ============================================================
REWRITE_SYSTEM_PROMPT_V2 = """You are a professional Writer fixing a fact deviation flagged by a \
Ledger Deviation Checker, for a local, minimal rewrite (not a full regeneration). This is a Trial \
variant of the rewrite contract (OPEN-113-LOCAL-REWRITE-CONTRACT-TIGHTENING-TRIAL-01) — it exists to \
test a narrower contract than the current Production one.

You are shown the flagged sentence, the reason it deviates from the Verified Fact Ledger, and the \
full Point (the paragraph/section) it belongs to, so you can see what has already been said nearby.

Follow this priority order, in this order:
1. Remove ONLY the unsupported meaning from the flagged sentence.
2. Shrink the flagged sentence's claim down to what the Ledger actually supports for THIS sentence — \
do not widen it or redirect it to a different topic.
3. If the Point still works without the flagged sentence (removing it does not break the logic or \
flow of the surrounding sentences), delete it instead of forcing a replacement.
4. Do NOT reach for a different Ledger fact to fill the gap the deviation left behind.
5. Do NOT repeat, restate, or lightly reword a fact or meaning that the same Point already states \
elsewhere. If your rewrite would end up saying essentially the same thing as an existing sentence in \
that Point, delete the flagged sentence instead of writing it.
6. Do NOT add a new fact, a new causal implication, or a new solution/recommendation claim beyond the \
flagged sentence's original role.

Explicitly forbidden:
- Substituting an unrelated Ledger fact for the one the sentence was actually about.
- Filling the gap with a nearby Ledger fact just because it happens to be Ledger-compliant.
- Paraphrasing a fact or meaning that the same Point already states elsewhere.
- Replacing one unsupported claim with a different unsupported claim.
- Turning the sentence into a flat fact statement that ignores its original logical role in the Point.

Output format:
- If deletion (rule 3 or rule 5 above) is the right call, return ONLY this exact token and nothing \
else: DELETE_SENTENCE
- Otherwise, return ONLY the revised sentence(s) — no explanation, no quotation marks around it.
- Do NOT add emoji (or any emoji) to the revised text. Do NOT add unnecessary Markdown bold \
(**...**) formatting. Keep formatting clean and plain."""

ATTEMPT1_TEMPLATE_V2 = """[Verified Fact Ledger]
{ledger_text}

[The full Point this sentence belongs to — read this first so you know what is already said there]
{point_context}

[Sentence flagged as a Ledger deviation]
{ng_sentence}

[Checker's issue]
{issue}

Decide: revise the flagged sentence following the priority order above, or return DELETE_SENTENCE if \
the Point works without it, or if a compliant rewrite would just repeat something the Point above \
already says."""

ATTEMPT2_TEMPLATE_V2 = """[Verified Fact Ledger]
{ledger_text}

[The full Point this sentence belongs to]
{point_context}

[Sentence still flagged after a first attempt]
{ng_sentence}

[Checker's issue]
{issue}

[Checker's explanation]
{explanation}

[Flags the checker marked true]
{flags}

Your previous attempt did not resolve this deviation. Follow the priority order again, paying \
specific attention to the flags above. Remember: do not fill the gap with a different Ledger fact, \
and do not repeat something the Point above already says. If a compliant, non-duplicate rewrite is \
not possible, return DELETE_SENTENCE."""

ATTEMPT3_TEMPLATE_V2 = """[Verified Fact Ledger]
{ledger_text}

[The full Point this sentence belongs to]
{point_context}

[Sentence still flagged after two attempts]
{ng_sentence}

[Checker's issue]
{issue}

This is the final attempt. If you can find a narrow, Ledger-compliant, non-duplicate rewrite, return \
it. Otherwise, return DELETE_SENTENCE — do not force a replacement by substituting a different \
Ledger fact just to pass the checker."""


def generate_rewrite_v2(client, model: str, reasoning_effort: str, prompt: str) -> str:
    response = client.responses.create(
        model=model,
        reasoning={"effort": reasoning_effort},
        input=[
            {"role": "developer", "content": REWRITE_SYSTEM_PROMPT_V2},
            {"role": "user", "content": prompt},
        ],
    )
    return response.output_text.strip()


def _resolve_check_text(candidate_text: str, before_ctx: str, after_ctx: str):
    if candidate_text.strip() == "DELETE_SENTENCE":
        joined = " ".join(t for t in [before_ctx, after_ctx] if t).strip()
        return joined, "DELETE"
    return f"{before_ctx} {candidate_text} {after_ctx}".strip(), "REWRITE"


def rewrite_ng_item_v2(client, model: str, reasoning_effort: str, verified_ledger_text: str,
                        point_context: str, ng_sentence: str, deviation: dict, before_ctx: str,
                        after_ctx: str, run_check_window_fn) -> dict:
    flags_true = [k for k in vfl01.DEVIATION_FLAG_KEYS if deviation.get(k)]
    attempts = []
    accepted_text, accepted, human_review, action = None, False, False, None

    prompt1 = ATTEMPT1_TEMPLATE_V2.format(
        ledger_text=verified_ledger_text, point_context=point_context, ng_sentence=ng_sentence,
        issue=deviation["issue"])
    text1 = generate_rewrite_v2(client, model, reasoning_effort, prompt1)
    window1, action1 = _resolve_check_text(text1, before_ctx, after_ctx)
    check1 = run_check_window_fn(window1)
    attempts.append({"attempt": 1, "text": text1, "action": action1,
                      "ledger_status": check1["overall_status"]})
    if check1["overall_status"] == "LEDGER_COMPLIANT":
        accepted_text, accepted, action = text1, True, action1
    else:
        prev1 = ng_sentence if action1 == "DELETE" else text1
        prompt2 = ATTEMPT2_TEMPLATE_V2.format(
            ledger_text=verified_ledger_text, point_context=point_context, ng_sentence=prev1,
            issue=deviation["issue"], explanation=deviation["explanation"],
            flags=", ".join(flags_true) or "(none)")
        text2 = generate_rewrite_v2(client, model, reasoning_effort, prompt2)
        window2, action2 = _resolve_check_text(text2, before_ctx, after_ctx)
        check2 = run_check_window_fn(window2)
        attempts.append({"attempt": 2, "text": text2, "action": action2,
                          "ledger_status": check2["overall_status"]})
        if check2["overall_status"] == "LEDGER_COMPLIANT":
            accepted_text, accepted, action = text2, True, action2
        else:
            prev2 = prev1 if action2 == "DELETE" else text2
            prompt3 = ATTEMPT3_TEMPLATE_V2.format(
                ledger_text=verified_ledger_text, point_context=point_context, ng_sentence=prev2,
                issue=deviation["issue"])
            text3 = generate_rewrite_v2(client, model, reasoning_effort, prompt3)
            window3, action3 = _resolve_check_text(text3, before_ctx, after_ctx)
            check3 = run_check_window_fn(window3)
            attempts.append({"attempt": 3, "text": text3, "action": action3,
                              "ledger_status": check3["overall_status"]})
            if check3["overall_status"] == "LEDGER_COMPLIANT":
                accepted_text, accepted, action = text3, True, action3
            else:
                accepted_text, accepted, human_review, action = text3, False, True, action3

    return {
        "original_ng_sentence": ng_sentence, "issue": deviation["issue"],
        "explanation": deviation["explanation"], "flags": flags_true, "attempts": attempts,
        "final_text": accepted_text, "final_action": action, "resolved": accepted,
        "human_review_required": human_review,
    }


def apply_rewrites_v2(article_text: str, results: list) -> str:
    updated = article_text
    for r in results:
        if not r.get("resolved") or not r.get("final_text"):
            continue
        if r["final_action"] == "DELETE":
            for needle in (f" {r['original_ng_sentence']}", r["original_ng_sentence"]):
                if needle in updated:
                    updated = updated.replace(needle, "", 1)
                    break
        elif r["original_ng_sentence"] in updated:
            updated = updated.replace(r["original_ng_sentence"], r["final_text"], 1)
    return re.sub(r"[ \t]{2,}", " ", updated)


# ============================================================
# Section抽出(point_context復元用のヘルパー、machinery不使用の単純split)
# ============================================================
def extract_section(article_text: str, needle: str) -> str:
    lines = article_text.splitlines()
    sections, current = [], []
    for line in lines:
        if line.startswith("#"):
            if current:
                sections.append("\n".join(current).strip())
            current = [line]
        else:
            current.append(line)
    if current:
        sections.append("\n".join(current).strip())
    for sec in sections:
        if needle in sec:
            return sec
    raise ValueError(f"section containing {needle!r} not found")


def reconstruct_pre_rewrite_article(final_article_text: str, items: list) -> str:
    """final_article_text(Local Rewrite後)から、original_ng_sentence/final_textの
    対応関係を逆replaceして、Local Rewrite前の記事本文を復元する(production側の
    apply_rewritesが行う単純str.replaceの逆操作、新しいNGケースを作らない)。"""
    pre = final_article_text
    for it in items:
        pre = pre.replace(it["final_text"], it["original_ng_sentence"], 1)
    return pre


# ============================================================
# Fixture定義(実ファイルから復元、新規NGケース捏造なし)
# ============================================================
def _load(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def build_fixtures() -> list:
    fixtures = []

    # --- Fixture 1: 既知ケース(No.18 B1B Point Two, OPEN-112 Trial-05) ---
    b1b_ledger = _load(
        "er011_output/open112_a_family_4layer_prompt_trial_05/research/verified_fact_ledger.txt")
    b1b_final_article = _load(
        "er011_output/open112_a_family_4layer_prompt_trial_05/b1b_run01/article.md")
    b1b_items = [{
        "original_ng_sentence": "Clear response windows could ease it.",
        "final_text": ("The survey found that a majority of teens reported feeling a need to "
                        "respond immediately to texts, social media messages, and other "
                        "notifications."),
        "issue": ("調査は10代の多数派が即時返信の必要を感じると報告しただけで、明確な返信時間帯を"
                   "設けることでその圧力が軽減されることは検証していない。"),
        "explanation": ("Ledgerにない具体的な対策効果を追加し、返信時間帯が圧力を軽減するという"
                         "因果的含意を加えている。Hookではないため緩和しない。"),
        "flags": {"changed_fact": True, "changed_causality": True, "unsupported_new_claim": True},
    }]
    fixtures.append({
        "id": "known_case_no18_b1b_point_two",
        "label": "No.18 B1B Point Two(既知ケース、OPEN-112 Trial-05)",
        "ledger_text": b1b_ledger,
        "final_article_text": b1b_final_article,
        "items": b1b_items,
        "ledger_model": gen.routing.require_model(gen._writer_process("B1B"), gen.routing.WRITER_MODEL),
        "baseline_final_text": b1b_items[0]["final_text"],
        "baseline_attempts": 2,
        "baseline_word_count_point_two": 81,
    })

    # --- Fixture 2 (regression): No.9 tip_screens A2 "Customers are starting to push back" ---
    tip_ledger = _load("er006_output/pool_pilot_01/pool_n9_tip_screens/research/verified_fact_ledger.txt")
    tip_final_article = _load("er006_output/pool_pilot_01/pool_n9_tip_screens/a2/article.md")
    tip_items = [
        {
            "original_ng_sentence": ("The feeling of “I must leave a tip” also fell, from "
                                      "66 percent in September 2025 to 59 percent in 2026."),
            "final_text": ("Among consumers prompted by a digital screen to tip, the share who felt "
                            "they had to leave a tip fell from 66 percent in September 2025 to 59 "
                            "percent in 2026."),
            "issue": ("Ledgerでの59％は「デジタル画面がチップを促すとき」にチップを残さなければ"
                       "ならないと感じる回答者の割合である。記事はこの画面提示時という条件を外し、"
                       "一般的なチップ義務感の変化として述べている。"),
            "explanation": "数値と比較方向は正しいが、対象となる状況の条件を外して範囲を一般化している。",
            "flags": {"changed_scope": True},
        },
        {
            "original_ng_sentence": "But they show that many customers are becoming tired of being guided by the screen.",
            "final_text": "But they suggest that many customers are increasingly pushing back against digital prompts to tip.",
            "issue": ("調査はチップが不合理だという認識、チップを減らしているという自己申告、"
                       "カスタム額の選択などを記述しているが、「画面に導かれることに疲れている」"
                       "という心理状態を直接測定していない。"),
            "explanation": ("記述的な自己申告結果から、画面が原因で顧客が疲弊しているという具体的な"
                             "心理・因果解釈を追加している。直前の「因果の証明ではない」という但し書き"
                             "だけでは、この新しい断定を支えない。"),
            "flags": {"changed_fact": True, "changed_causality": True, "changed_certainty": True,
                      "unsupported_new_claim": True},
        },
    ]
    fixtures.append({
        "id": "regression_no9_tip_screens_a2_pushback",
        "label": "No.9 tip_screens A2「Customers are starting to push back」(regression、2件)",
        "ledger_text": tip_ledger,
        "final_article_text": tip_final_article,
        "items": tip_items,
        "ledger_model": gen.routing.require_model(gen._writer_process("A2"), gen.routing.WRITER_MODEL),
        "baseline_final_text": None,
        "baseline_attempts": 1,
        "baseline_word_count_point_two": None,
    })

    # --- Fixture 3 (regression): No.18 notifications A2 "In one line" certainty softening ---
    n18a2_ledger = _load("er006_output/pool_pilot_01/pool_n18_notifications/research/verified_fact_ledger.txt")
    n18a2_final_article = _load("er006_output/pool_pilot_01/pool_n18_notifications/a2/article.md")
    n18a2_items = [{
        "original_ng_sentence": "“I did not check it” does not always mean “it had no effect.”",
        "final_text": "“I did not check it” does not necessarily mean “it had no effect.”",
        "issue": ("通知を確認しなかった場合でも効果があり得るという結論自体はLedgerの実験結果に"
                   "基づくが、「always」を用いて、特定の実験条件・参加者で確認された結果を一般的な"
                   "判断規則へ広げている。Hookとして扱える一文でも、changed_certaintyは緩和されない。"),
        "explanation": "実験結果を一般的な断定へ拡張する「always」相当の表現。Hookのためchanged_scopeは報告対象外としたが、changed_certaintyは明確に該当する。",
        "flags": {"changed_certainty": True},
    }]
    fixtures.append({
        "id": "regression_no18_notifications_a2_in_one_line",
        "label": "No.18 notifications A2「In one line」certainty softening(regression、単純ケース)",
        "ledger_text": n18a2_ledger,
        "final_article_text": n18a2_final_article,
        "items": n18a2_items,
        "ledger_model": gen.routing.require_model(gen._writer_process("A2"), gen.routing.WRITER_MODEL),
        "baseline_final_text": n18a2_items[0]["final_text"],
        "baseline_attempts": 1,
        "baseline_word_count_point_two": None,
    })

    return fixtures


def run_fixture(client, fixture: dict) -> dict:
    pre_article = reconstruct_pre_rewrite_article(fixture["final_article_text"], fixture["items"])
    point_context = extract_section(pre_article, fixture["items"][0]["original_ng_sentence"])
    sentences = local_rewrite.split_sentences(pre_article)
    ledger_text = fixture["ledger_text"]
    ledger_model = fixture["ledger_model"]

    def _run_check_window(window_text: str) -> dict:
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
        print(f"[OPEN-113][{fixture['id']}] item開始: {ng_sentence[:60]}...")
        r = rewrite_ng_item_v2(client, ledger_model, gen.REASONING_EFFORT, ledger_text, point_context,
                                ng_sentence, deviation, before_ctx, after_ctx, _run_check_window)
        r["location_method"] = location_method
        r["before_ctx"] = before_ctx
        r["after_ctx"] = after_ctx
        item_results.append(r)
        print(f"[OPEN-113][{fixture['id']}] item完了: action={r['final_action']} "
              f"resolved={r['resolved']} attempts={len(r['attempts'])}")

    new_article = apply_rewrites_v2(pre_article, item_results)
    # point_contextはLocal Rewrite前のsection全体を丸ごと保持しているため、
    # 記事全文に対してではなく、このpoint_context文字列自体に同じ置換/削除を
    # 直接適用する(見出し(##/###)を挟むとlocal_rewrite.split_sentences()が
    # 文分割に失敗し、new_article側でneedle探索する方式は壊れるため)。
    new_point_context = apply_rewrites_v2(point_context, item_results)

    print(f"[OPEN-113][{fixture['id']}] cycle後、Ledger全体(全文)を再判定...")
    full_recheck = vfl01.run_deviation_check(client, ledger_text, new_article, model=ledger_model,
                                              hook_aware=True)
    full_recheck_parsed = full_recheck["parsed"]

    return {
        "fixture_id": fixture["id"], "label": fixture["label"],
        "pre_article": pre_article, "point_context_before": point_context,
        "item_results": item_results, "new_article": new_article,
        "new_point_context": new_point_context,
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
    fixtures = build_fixtures()
    results = {}
    for fixture in fixtures:
        cache_path = f"{OUT_DIR}/{fixture['id']}.json"
        if os.path.exists(cache_path):
            with open(cache_path, encoding="utf-8") as f:
                res = json.load(f)
            results[fixture["id"]] = res
            print(f"[OPEN-113][{fixture['id']}] キャッシュ済み結果を再利用します(再API呼び出しなし)。"
                  f"full_recheck_overall_status={res['full_recheck_overall_status']}")
            continue
        t0 = time.time()
        res = run_fixture(client, fixture)
        res["elapsed_seconds"] = round(time.time() - t0, 1)
        results[fixture["id"]] = res
        with open(f"{OUT_DIR}/{fixture['id']}.json", "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=2, default=str)
        print(f"[OPEN-113][{fixture['id']}] 完了。full_recheck_overall_status="
              f"{res['full_recheck_overall_status']} major={res['full_recheck_major_count']} "
              f"api_calls={res['api_call_count']} elapsed={res['elapsed_seconds']}s")

    with open(f"{OUT_DIR}/trial01_summary.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    print(f"[OPEN-113] 完了。summary -> {OUT_DIR}/trial01_summary.json")
    return results


if __name__ == "__main__":
    main()
