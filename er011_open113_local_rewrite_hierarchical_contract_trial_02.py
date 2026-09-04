# ============================================================
# er011_open113_local_rewrite_hierarchical_contract_trial_02.py
# OPEN-113-LOCAL-REWRITE-HIERARCHICAL-CONTRACT-TRIAL-02
# ============================================================
# 目的: Trial-01で確認された「既知の意味重複は解消できたが、DELETEへ寄り
# すぎる(過剰DELETE)」というtrade-offを、Local Rewriteの優先順位を
#   STEP1 意味維持の最小REWRITE
#   STEP2 安全な縮退REWRITE
#   STEP3 DELETE
#   STEP4 NG(無理に修正しない)
# という厳密な階層として明示することで解消できるかを検証する。
#
# 対象: Prompt契約の改善のみ。Post-Rewrite Semantic Checker等の新規QAは
# 追加しない。Production(er010_ledger_local_rewrite_09.py /
# er003_v1_n3_01_articles_generate.py)は一切変更しない。
#
# 到達してよいStatus: REJECTED / VALIDATED / USER_DECISION_REQUIRED のみ。
# APPROVED_FOR_PRODUCTION・PRODUCTION_WIRED不可。
#
# Fixture: Trial-01(er011_open113_local_rewrite_contract_tightening_trial_01.py)
# が実ファイルから復元した3 fixture・4 item(No.18 B1既知ケース、No.9
# tip_screens #1/#2、No.18 notifications A2)をそのまま再利用する。今回の
# 仕様が指定する検証対象4ケースと完全に一致するため、新しいfixtureは作らない。
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

OUT_DIR = "er011_output/open113_local_rewrite_hierarchical_contract_trial_02"

# ============================================================
# Layer 1: 新Local Rewrite契約(Trial専用、Productionには一切書き込まない)
# ============================================================
REWRITE_SYSTEM_PROMPT_V3 = """You are a professional Writer fixing a fact deviation flagged by a \
Ledger Deviation Checker, for a local, minimal rewrite (not a full regeneration). This is Trial-02 of \
the rewrite contract (OPEN-113-LOCAL-REWRITE-HIERARCHICAL-CONTRACT-TRIAL-02) — it tests a strict, \
hierarchical decision order between rewriting and deleting, because an earlier Trial found that \
allowing deletion too freely caused good, safe rewrites to be deleted instead.

You are shown the flagged sentence, the reason it deviates from the Verified Fact Ledger, and the \
full Point (the paragraph/section) it belongs to, so you can see what has already been said nearby.

You MUST evaluate the following four steps IN ORDER, and stop at the first one that genuinely \
applies. Do not skip ahead to a later step just because it feels safer, easier, or shorter — a later \
step is only allowed when every earlier step is truly impossible.

STEP 1 — Meaning-preserving minimal rewrite (always try this first):
Make the smallest possible edit that removes only the unsupported part of the flagged sentence, while \
keeping its original central meaning and its original logical role in the Point unchanged. Typical \
examples: a certainty adjustment, a narrower scope, a wording correction, limiting a quantified or \
generalized expression. If an edit like this exists, use it and stop here.

STEP 2 — Safe scope-reduced rewrite (only if Step 1 is genuinely impossible):
If no minimal edit can keep the sentence's original central meaning, weaken the claim down to only \
what the Ledger actually supports for THIS sentence. Typical examples: a causal claim becomes an \
observation, a solution/recommendation claim becomes a limitation statement, a strong certainty \
becomes a qualified interpretation. Keep the sentence's original logical role as much as possible, \
and do not let the Point lose its central value. If a rewrite like this exists, use it and stop here \
— do not proceed to Step 3.

STEP 3 — Delete (only if Steps 1 and 2 are both genuinely impossible):
Delete the flagged sentence only when no compliant rewrite from Step 1 or Step 2 exists. Before \
deleting, confirm the Point without the sentence is still: grammatically natural, naturally connected \
between the surrounding sentences, logically complete, not missing necessary information, and free of \
any unnatural jump. Do not delete merely to shorten word count, and do not delete merely because it \
feels like the safer option — delete only when Step 1 and Step 2 are truly not possible.

STEP 4 — NG (only if Steps 1, 2, and 3 all fail):
If no compliant rewrite is possible AND deleting the sentence would break the Point's grammar, flow, \
or logic, do not force any change. Report NG instead of inventing a fix.

In every step, these rules always apply:
- Never substitute a different Ledger fact for the one the flagged sentence was actually about.
- Never fill the gap with a nearby Ledger fact just because it happens to be Ledger-compliant.
- Never repeat, restate, or lightly reword a fact or meaning that the same Point already states \
elsewhere — if your Step 1/2 rewrite would end up saying essentially the same thing as an existing \
sentence in that Point, that step does not actually apply; move to the next step.
- Never add a new fact, a new causal implication, or a new solution/recommendation claim.
- Never rewrite the whole Point or the whole article — only the flagged sentence.
- Being Ledger-compliant alone does not justify a rewrite that damages the sentence's quality, \
naturalness, or the Point's flow.

Output format — respond with EXACTLY two lines, nothing else:
Line 1: one of these four tags only, matching the step you actually used: STEP1 / STEP2 / STEP3 / STEP4
Line 2:
- for STEP1 or STEP2: the revised sentence(s) only — no explanation, no quotation marks around it, no \
emoji, no unnecessary Markdown bold (**...**) formatting.
- for STEP3: the exact token DELETE_SENTENCE
- for STEP4: the exact token LOCAL_REWRITE_NG"""

ATTEMPT1_TEMPLATE_V3 = """[Verified Fact Ledger]
{ledger_text}

[The full Point this sentence belongs to — read this first so you know what is already said there]
{point_context}

[Sentence flagged as a Ledger deviation]
{ng_sentence}

[Checker's issue]
{issue}

Work through STEP 1 -> STEP 2 -> STEP 3 -> STEP 4 in order and stop at the first one that genuinely \
applies. Respond in the required two-line format."""

ATTEMPT2_TEMPLATE_V3 = """[Verified Fact Ledger]
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

Your previous attempt did not resolve this deviation. Work through STEP 1 -> STEP 2 -> STEP 3 -> \
STEP 4 again, paying specific attention to the flags above. Remember: do not fill the gap with a \
different Ledger fact, and do not repeat something the Point above already says. Respond in the \
required two-line format."""

ATTEMPT3_TEMPLATE_V3 = """[Verified Fact Ledger]
{ledger_text}

[The full Point this sentence belongs to]
{point_context}

[Sentence still flagged after two attempts]
{ng_sentence}

[Checker's issue]
{issue}

This is the final attempt. Work through STEP 1 -> STEP 2 -> STEP 3 -> STEP 4 one more time, honestly. \
If a genuinely minimal or safely scope-reduced rewrite exists, use it (STEP1/STEP2) — do not jump to \
STEP3 just because this is the last attempt. Only use STEP3 if deletion is truly safe, and only use \
STEP4 if nothing else works. Respond in the required two-line format."""


def generate_rewrite_v3(client, model: str, reasoning_effort: str, prompt: str) -> str:
    response = client.responses.create(
        model=model,
        reasoning={"effort": reasoning_effort},
        input=[
            {"role": "developer", "content": REWRITE_SYSTEM_PROMPT_V3},
            {"role": "user", "content": prompt},
        ],
    )
    return response.output_text.strip()


def _parse_step_output(raw: str):
    """モデル出力の1行目からSTEPタグを取り出す。タグを付け忘れた場合は
    内容から推定するフォールバックのみ行い、ケース固有の誘導はしない。"""
    lines = [ln for ln in raw.strip().splitlines() if ln.strip() != ""]
    if lines:
        first = lines[0].strip().upper()
        for tag in ("STEP1", "STEP2", "STEP3", "STEP4"):
            if first.startswith(tag):
                rest = "\n".join(lines[1:]).strip()
                return tag, rest
    content = raw.strip()
    if content == "DELETE_SENTENCE":
        return "STEP3", content
    if content == "LOCAL_REWRITE_NG":
        return "STEP4", content
    return "STEP1", content


def _resolve_check_text_v3(step: str, content: str, before_ctx: str, after_ctx: str):
    if step == "STEP3":
        joined = " ".join(t for t in [before_ctx, after_ctx] if t).strip()
        return joined, "DELETE"
    return f"{before_ctx} {content} {after_ctx}".strip(), "REWRITE"


def rewrite_ng_item_v3(client, model: str, reasoning_effort: str, verified_ledger_text: str,
                        point_context: str, ng_sentence: str, deviation: dict, before_ctx: str,
                        after_ctx: str, run_check_window_fn) -> dict:
    flags_true = [k for k in vfl01.DEVIATION_FLAG_KEYS if deviation.get(k)]
    attempts = []
    accepted_text, accepted, human_review, action, final_step = None, False, False, None, None
    prev = ng_sentence

    templates = [ATTEMPT1_TEMPLATE_V3, ATTEMPT2_TEMPLATE_V3, ATTEMPT3_TEMPLATE_V3]
    for attempt_no in (1, 2, 3):
        if attempt_no == 1:
            prompt = templates[0].format(ledger_text=verified_ledger_text, point_context=point_context,
                                          ng_sentence=ng_sentence, issue=deviation["issue"])
        elif attempt_no == 2:
            prompt = templates[1].format(ledger_text=verified_ledger_text, point_context=point_context,
                                          ng_sentence=prev, issue=deviation["issue"],
                                          explanation=deviation["explanation"],
                                          flags=", ".join(flags_true) or "(none)")
        else:
            prompt = templates[2].format(ledger_text=verified_ledger_text, point_context=point_context,
                                          ng_sentence=prev, issue=deviation["issue"])

        raw = generate_rewrite_v3(client, model, reasoning_effort, prompt)
        step, content = _parse_step_output(raw)

        if step == "STEP4":
            attempts.append({"attempt": attempt_no, "raw": raw, "step": step, "text": content,
                              "action": "NG", "ledger_status": None})
            accepted_text, accepted, human_review, action, final_step = None, False, True, "NG", "STEP4"
            break

        window, act = _resolve_check_text_v3(step, content, before_ctx, after_ctx)
        check = run_check_window_fn(window)
        attempts.append({"attempt": attempt_no, "raw": raw, "step": step, "text": content,
                          "action": act, "ledger_status": check["overall_status"]})
        if check["overall_status"] == "LEDGER_COMPLIANT":
            accepted_text, accepted, action, final_step = content, True, act, step
            break
        prev = ng_sentence if act == "DELETE" else content
        if attempt_no == 3:
            accepted_text, accepted, human_review, action, final_step = content, False, True, act, step

    return {
        "original_ng_sentence": ng_sentence, "issue": deviation["issue"],
        "explanation": deviation["explanation"], "flags": flags_true, "attempts": attempts,
        "final_text": accepted_text, "final_action": action, "final_step": final_step,
        "resolved": accepted, "human_review_required": human_review,
    }


def apply_rewrites_v3(article_text: str, results: list) -> str:
    import re
    updated = article_text
    for r in results:
        if not r.get("resolved") or r["final_action"] == "NG" or not r.get("final_text"):
            continue
        if r["final_action"] == "DELETE":
            for needle in (f" {r['original_ng_sentence']}", r["original_ng_sentence"]):
                if needle in updated:
                    updated = updated.replace(needle, "", 1)
                    break
        elif r["original_ng_sentence"] in updated:
            updated = updated.replace(r["original_ng_sentence"], r["final_text"], 1)
    return re.sub(r"[ \t]{2,}", " ", updated)


def run_fixture(client, fixture: dict) -> dict:
    pre_article = trial01.reconstruct_pre_rewrite_article(fixture["final_article_text"], fixture["items"])
    point_context = trial01.extract_section(pre_article, fixture["items"][0]["original_ng_sentence"])
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
        print(f"[OPEN-113-T02][{fixture['id']}] item開始: {ng_sentence[:60]}...")
        r = rewrite_ng_item_v3(client, ledger_model, gen.REASONING_EFFORT, ledger_text, point_context,
                                ng_sentence, deviation, before_ctx, after_ctx, _run_check_window)
        r["location_method"] = location_method
        r["before_ctx"] = before_ctx
        r["after_ctx"] = after_ctx
        item_results.append(r)
        print(f"[OPEN-113-T02][{fixture['id']}] item完了: step={r['final_step']} "
              f"action={r['final_action']} resolved={r['resolved']} attempts={len(r['attempts'])}")

    new_article = apply_rewrites_v3(pre_article, item_results)
    new_point_context = apply_rewrites_v3(point_context, item_results)

    print(f"[OPEN-113-T02][{fixture['id']}] cycle後、Ledger全体(全文)を再判定...")
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
        "api_call_count": sum(len(r["attempts"]) * 2 - (1 if r["final_step"] == "STEP4" else 0)
                               for r in item_results) + 1,
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
            print(f"[OPEN-113-T02][{fixture['id']}] キャッシュ済み結果を再利用します(再API呼び出しなし)。"
                  f"full_recheck_overall_status={res['full_recheck_overall_status']}")
            continue
        t0 = time.time()
        res = run_fixture(client, fixture)
        res["elapsed_seconds"] = round(time.time() - t0, 1)
        results[fixture["id"]] = res
        with open(f"{OUT_DIR}/{fixture['id']}.json", "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=2, default=str)
        print(f"[OPEN-113-T02][{fixture['id']}] 完了。full_recheck_overall_status="
              f"{res['full_recheck_overall_status']} major={res['full_recheck_major_count']} "
              f"api_calls={res['api_call_count']} elapsed={res['elapsed_seconds']}s")

    with open(f"{OUT_DIR}/trial02_summary.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    print(f"[OPEN-113-T02] 完了。summary -> {OUT_DIR}/trial02_summary.json")
    return results


if __name__ == "__main__":
    main()
