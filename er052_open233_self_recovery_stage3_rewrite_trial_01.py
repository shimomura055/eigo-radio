# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_stage3_rewrite_trial_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (Self-Recovery Flow, Phase 1 ⑤、委任_08 作業B)
# ============================================================
# 目的: design書§9-1⑤(Stage3型別Rewrite成功率実測)を、rewrite_kind別に
# 実行するharness。
#
# スコープ確定(本ファイル内の委任_08時点の判断、報告書へ明記):
# - delete型(B1-c/B3/B4-a)は、design§4-5どおりLLMを経由しない決定論的
#   削除で扱う(E-1/E-2で機構差が生じない共通baselineとして1回のみ測定)。
# - replace_with_ledger_value型は、design§5-2の origin=translation 限定
#   ルールに従いEN局所Rewrite(E-1 vs E-2)の対象とする。er009_changed_actor/
#   changed_number(EN-native、JA原文なしのためtranslation相当)を使用。
# - narrow_scope型は、design§5-1の origin=ja_source 限定ルールに従いJA側
#   paired local rewrite(J-1 vs J-2)の対象とする。hormuz_run03_standard
#   (HF-009、ja_source)を使用。
# - J-1/J-2の「JA Fact Check」「EN Deviation Check(Recheck)」は、本Trialでは
#   既存のVerified Fact Ledger Deviation Checker(V4A variant、
#   er051_open233_checker_trial_variant_01.run_trial_deviation_check)を
#   JA/EN両方の文面に適用する近似で代用する(真のProduction JA Fact
#   Check[er002_ja_web_research_r3系]・JA Writer O cascade
#   [er019_family_x_ja_writer_o_r1_r2_01.py]は本Trialでは呼び出さない
#   =読み取り専用の遵守と、予算・実装時間の制約による意図的なスコープ
#   縮小。§5-4の「句点分割移植」相当のJA文分割も本Trialでは対象文を
#   直接指定する簡易実装とし、汎用モジュール化はしていない)。
#
# 重要な設計制約(既存er051/er052系Trialと同一原則):
# - Production code(er003/er009/er010/er012/er019)は一切変更しない
#   (er010.generate_rewriteのcostログ取得のみ、本プロセス内のモンキー
#   パッチでusageを記録する。API呼び出しパラメータ自体は無変更、
#   ディスク上のer010ファイルは一切変更しない)。
# - Model Routing Contractは経由しない。
# - API keyは環境変数のみ。保存jsonにはprompt本体ではなくsha256のみ記録。
from __future__ import annotations

import hashlib
import json
import os
import re
import time

import er003_v1_en_direct_vfl_01_generate as vfl01
import er009_ledger_deviation_recalibration_02_test as er009t
import er010_ledger_local_rewrite_09 as er010
import er050_gpt6_checker_comparison_trial_01 as g6
import er051_open233_checker_trial_variant_01 as trial
import er052_open233_self_recovery_stage2_production_01 as s2p

OUT_DIR = "er052_output/open233_self_recovery_stage3_rewrite_trial_01"
BUDGET_STATE_PATH = f"{OUT_DIR}/budget_state_c233l_b.json"
TOTAL_BUDGET_JPY = 30.0  # 委任_08 作業B Guardrail
MAX_RETRIES_PER_CALL = 2
MAX_CONSECUTIVE_ERRORS = 3
MODEL = "gpt-6-luna"


class TrialAbort(RuntimeError):
    pass


def load_budget_state() -> dict:
    if os.path.exists(BUDGET_STATE_PATH):
        with open(BUDGET_STATE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []}


def save_budget_state(state: dict) -> None:
    os.makedirs(os.path.dirname(BUDGET_STATE_PATH), exist_ok=True)
    with open(BUDGET_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def check_budget(state: dict) -> None:
    if state["cumulative_jpy"] >= TOTAL_BUDGET_JPY:
        raise TrialAbort(f"累計¥{state['cumulative_jpy']:.3f}が委任_08 作業B Guardrail¥{TOTAL_BUDGET_JPY}に到達")


def save_json(path: str, payload: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def record_call(state: dict, consecutive_errors: list, label: str, cost_jpy: float, ok: bool) -> None:
    state["cumulative_calls"] += 1
    if ok:
        state["cumulative_jpy"] += cost_jpy
        state["history"].append({"label": label, "cost_jpy": cost_jpy})
        consecutive_errors[0] = 0
    else:
        state["cumulative_errors"] += 1
        consecutive_errors[0] += 1
    save_budget_state(state)
    if consecutive_errors[0] >= MAX_CONSECUTIVE_ERRORS:
        raise TrialAbort(f"API errorが{MAX_CONSECUTIVE_ERRORS}call連続(STOP条件)")


# ------------------------------------------------------------
# 共通: V4A variant checkerをrun_check_window_fn / Recheckとして使う
# ------------------------------------------------------------
def make_check_fn(client, state, consecutive_errors, ledger_text, call_log, label_prefix):
    def fn(window_text):
        check_budget(state)
        last_err = None
        res = None
        for _ in range(1 + MAX_RETRIES_PER_CALL):
            try:
                res = trial.run_trial_deviation_check(client, ledger_text, window_text, model=MODEL, variant="V4A")
                break
            except Exception as e:  # noqa: BLE001
                last_err = f"{type(e).__name__}: {e}"
                time.sleep(1.0)
        if res is not None:
            cost = round(s2p.official_cost_jpy(res["usage"]), 4)
            call_log.append({"label": f"{label_prefix}_check", "cost_jpy": cost, "usage": res["usage"],
                              "overall_status": res["parsed"]["overall_status"],
                              "prompt_sha256": s2p.sha256_text(res["prompt"])})
            record_call(state, consecutive_errors, f"{label_prefix}_check", cost, True)
            return res["parsed"]
        call_log.append({"label": f"{label_prefix}_check", "error": last_err})
        record_call(state, consecutive_errors, f"{label_prefix}_check", 0.0, False)
        return {"overall_status": "LEDGER_DEVIATION", "deviations": [], "_error": last_err}
    return fn


def simple_llm_call(client, state, consecutive_errors, call_log, label, developer_msg, prompt, model=MODEL):
    check_budget(state)
    last_err = None
    for _ in range(1 + MAX_RETRIES_PER_CALL):
        try:
            t0 = time.time()
            response = client.responses.create(
                model=model, reasoning={"effort": vfl01.REASONING_EFFORT},
                input=[{"role": "developer", "content": developer_msg}, {"role": "user", "content": prompt}],
            )
            elapsed = round(time.time() - t0, 3)
            usage = s2p._extract_usage(response)
            cost = round(s2p.official_cost_jpy(usage), 4)
            call_log.append({"label": label, "cost_jpy": cost, "usage": usage, "elapsed_seconds": elapsed,
                              "prompt_sha256": s2p.sha256_text(prompt), "output_text": response.output_text})
            record_call(state, consecutive_errors, label, cost, True)
            return response.output_text.strip()
        except Exception as e:  # noqa: BLE001
            last_err = f"{type(e).__name__}: {e}"
            time.sleep(1.0)
    call_log.append({"label": label, "error": last_err})
    record_call(state, consecutive_errors, label, 0.0, False)
    return None


# ------------------------------------------------------------
# (1) delete型: B1-c(JA)/B3(EN)/B4-a(EN) — 決定論的削除 + Recheck 1call
# ------------------------------------------------------------
DELETE_TARGETS = [
    {
        "sub_id": "B1-c", "lang": "ja",
        "ng_sentence": "投資家が気にしているのは、20％の料金案が残るかどうかだけではない。"
                       "米国とイランの間で攻撃が続いていること、海が封鎖される心配があること、"
                       "タンカーが安全に航行できるか不安が残っていることだ。",
        "fixture_id": "B1",
    },
    {
        "sub_id": "B3", "lang": "en",
        "ng_sentence_anchor": "Concerns about US-Iran attacks",
        "fixture_id": "B3",
    },
    {
        "sub_id": "B4-a", "lang": "en",
        "ng_sentence": "A person can take over when AI alone has trouble.",
        "fixture_id": "B4",
    },
]

_DANGLING_STARTERS_EN = ("this", "that", "it", "these", "those", "so", "therefore", "such")
_DANGLING_STARTERS_JA = ("そのため", "それ", "これ", "その", "この", "このため", "そこで")


def dangling_reference_check(remaining_text: str, deleted_sentence: str, lang: str) -> dict:
    """E-2の追加後処理(¥0): 削除文の直後に来ていた文が、代名詞・接続詞で
    始まっていないかを検出する(書き換えはしない、フラグ立てのみ)。"""
    idx = remaining_text.find(deleted_sentence[:20]) if deleted_sentence[:20] in remaining_text else -1
    # 削除済みなので、削除前後の文脈は呼び出し側が別途保持する前提。
    # ここでは簡易に「削除箇所直後に想定される代名詞・接続詞」の有無だけを
    # remaining_text全体に対して機械的に検出したことを記録する(Trial観測用)。
    starters = _DANGLING_STARTERS_JA if lang == "ja" else _DANGLING_STARTERS_EN
    hits = [s for s in starters if s in remaining_text]
    return {"checked": True, "starters_found_nearby": hits[:5]}


def run_delete_type(client, state, consecutive_errors) -> list:
    fixtures = {f["id"]: f for f in g6.step2_fixtures()}
    out = []
    for target in DELETE_TARGETS:
        fixture = fixtures[target["fixture_id"]]
        article_text = fixture["article_text"]
        if "ng_sentence" in target:
            ng = target["ng_sentence"]
            found = ng in article_text
        else:
            anchor = target["ng_sentence_anchor"]
            idx = article_text.find(anchor)
            found = idx != -1
            ng = article_text[idx:].strip() if found else anchor
        updated_text = article_text.replace(ng, "", 1) if found else article_text
        call_log = []
        check_fn = make_check_fn(client, state, consecutive_errors, fixture["ledger_text"], call_log,
                                  f"delete_{target['sub_id']}")
        recheck = check_fn(updated_text) if found else {"overall_status": "SKIPPED_NOT_FOUND"}
        dangling = dangling_reference_check(updated_text, ng, target["lang"])
        row = {
            "sub_id": target["sub_id"], "lang": target["lang"], "exact_match_found": found,
            "ng_sentence_deleted": ng, "recheck_overall_status": recheck.get("overall_status"),
            "resolved": recheck.get("overall_status") == "LEDGER_COMPLIANT",
            "dangling_reference_check": dangling, "call_log": call_log,
            "total_cost_jpy": round(sum(c.get("cost_jpy", 0.0) for c in call_log), 4),
        }
        out.append(row)
        save_json(f"{OUT_DIR}/delete_type/{target['sub_id']}.json", row)
    return out


# ------------------------------------------------------------
# (2) replace_with_ledger_value型: er009_changed_actor/changed_number
#     E-1(er010.rewrite_ng_item、既存骨格そのまま呼び出し)
#     vs E-2(最小1-shot Prompt)
# ------------------------------------------------------------
REPLACE_TARGETS = [
    {
        "sub_id": "er009_changed_actor",
        "article_text": er009t.FIXTURES["changed_actor"],
        "deviation": {
            "issue": "研究主体をHarvard Business Schoolのチームと特定していますが、Ledgerが示す"
                     "研究者はKareem HaggagとGiovanni Paciで、Harvard Business Schoolとの関係は"
                     "確認されていません。",
            "explanation": "Harvard Business School所属というLedgerにない具体的事実を加え、"
                           "研究主体を置き換えている。",
            "changed_fact": True, "changed_scope": False, "changed_causality": False,
            "changed_certainty": False, "changed_number": False, "changed_actor": True,
            "changed_negation": False, "changed_comparison": False, "changed_time": False,
            "unsupported_new_claim": True,
        },
        "e2_rewrite_hint": "Replace the actor 'A team at Harvard Business School' with a neutral "
                           "term consistent with the Ledger (e.g., 'Researchers' or 'The study'), "
                           "since the Ledger does not confirm Harvard Business School as the "
                           "research affiliation.",
        "verify_fn": lambda text: "harvard" not in text.lower(),
        "verify_desc": "'Harvard'が本文から消えていること",
    },
    {
        "sub_id": "er009_changed_number",
        "article_text": er009t.FIXTURES["changed_number"],
        "deviation": {
            "issue": "記事は対象取引数を「3,000万件超」としているが、Ledgerが確認しているのは"
                     "「1,300万件超」であり、3,000万件超という数値は裏付けられていない。",
            "explanation": "取引数について、Ledgerの「1,300万件超」から記事が「3,000万件超」へ"
                           "数値を変更している。",
            "changed_fact": True, "changed_scope": False, "changed_causality": False,
            "changed_certainty": False, "changed_number": True, "changed_actor": False,
            "changed_negation": False, "changed_comparison": False, "changed_time": False,
            "unsupported_new_claim": False,
        },
        "e2_rewrite_hint": "Replace 'more than 30 million' with the Ledger-verified figure "
                           "'more than 13 million'.",
        "verify_fn": lambda text: "13 million" in text.lower(),
        "verify_desc": "'13 million'が本文に出現すること",
    },
]

E2_MINIMAL_DEVELOPER_MSG = (
    "You are fixing a fact deviation flagged by a Ledger Deviation Checker, using the smallest "
    "possible edit (single-shot, no escalation)."
)
E2_MINIMAL_PROMPT_TEMPLATE = """[Verified Fact Ledger]
{ledger_text}

[Sentence flagged as a Ledger deviation]
{ng_sentence}

[Checker's issue]
{issue}

[Rewrite hint]
{rewrite_hint}

Rewrite ONLY this sentence to resolve the issue, replacing the incorrect element with what the \
Ledger actually supports. Keep everything else in the sentence unchanged. Return ONLY the revised \
sentence, nothing else."""


def run_e1_for_target(client, state, consecutive_errors, target: dict) -> dict:
    call_log = []
    orig_generate_rewrite = er010.generate_rewrite

    def patched_generate_rewrite(client_, model, reasoning_effort, prompt):
        check_budget(state)
        last_err = None
        for _ in range(1 + MAX_RETRIES_PER_CALL):
            try:
                t0 = time.time()
                response = client_.responses.create(
                    model=model, reasoning={"effort": reasoning_effort},
                    input=[{"role": "developer", "content": er010.REWRITE_SYSTEM_PROMPT},
                           {"role": "user", "content": prompt}],
                )
                elapsed = round(time.time() - t0, 3)
                usage = s2p._extract_usage(response)
                cost = round(s2p.official_cost_jpy(usage), 4)
                call_log.append({"label": f"e1_{target['sub_id']}_rewrite", "cost_jpy": cost,
                                  "usage": usage, "elapsed_seconds": elapsed,
                                  "prompt_sha256": s2p.sha256_text(prompt)})
                record_call(state, consecutive_errors, f"e1_{target['sub_id']}_rewrite", cost, True)
                return response.output_text.strip()
            except Exception as e:  # noqa: BLE001
                last_err = f"{type(e).__name__}: {e}"
                time.sleep(1.0)
        call_log.append({"label": f"e1_{target['sub_id']}_rewrite", "error": last_err})
        record_call(state, consecutive_errors, f"e1_{target['sub_id']}_rewrite", 0.0, False)
        raise RuntimeError(last_err)

    er010.generate_rewrite = patched_generate_rewrite
    try:
        article_text = target["article_text"]
        ledger_text = er009t.LEDGER_TEXT
        check_fn = make_check_fn(client, state, consecutive_errors, ledger_text, call_log,
                                  f"e1_{target['sub_id']}")
        t0 = time.time()
        result = er010.rewrite_ng_item(
            client=client, model=MODEL, reasoning_effort=vfl01.REASONING_EFFORT,
            verified_ledger_text=ledger_text, point_context=article_text,
            ng_sentence=article_text, deviation=target["deviation"], before_ctx="", after_ctx="",
            run_check_window_fn=check_fn, use_target_sentence_matching=False,
        )
        elapsed = round(time.time() - t0, 3)
    finally:
        er010.generate_rewrite = orig_generate_rewrite

    verified = target["verify_fn"](result["final_text"] or "")
    return {
        "method": "E-1", "sub_id": target["sub_id"], "resolved": result["resolved"],
        "human_review_required": result["human_review_required"], "n_attempts": len(result["attempts"]),
        "final_text": result["final_text"], "machine_verified": verified,
        "verify_desc": target["verify_desc"], "attempts": result["attempts"],
        "elapsed_seconds": elapsed, "call_log": call_log,
        "total_cost_jpy": round(sum(c.get("cost_jpy", 0.0) for c in call_log), 4),
    }


def run_e2_for_target(client, state, consecutive_errors, target: dict) -> dict:
    call_log = []
    ledger_text = er009t.LEDGER_TEXT
    prompt = E2_MINIMAL_PROMPT_TEMPLATE.format(
        ledger_text=ledger_text, ng_sentence=target["article_text"],
        issue=target["deviation"]["issue"], rewrite_hint=target["e2_rewrite_hint"],
    )
    t0 = time.time()
    revised = simple_llm_call(client, state, consecutive_errors, call_log,
                               f"e2_{target['sub_id']}_rewrite", E2_MINIMAL_DEVELOPER_MSG, prompt)
    elapsed_gen = round(time.time() - t0, 3)
    verified = target["verify_fn"](revised or "")
    check_fn = make_check_fn(client, state, consecutive_errors, ledger_text, call_log,
                              f"e2_{target['sub_id']}")
    recheck = check_fn(revised or target["article_text"])
    resolved = recheck.get("overall_status") == "LEDGER_COMPLIANT"
    return {
        "method": "E-2", "sub_id": target["sub_id"], "resolved": resolved,
        "n_attempts": 1, "final_text": revised, "machine_verified": verified,
        "verify_desc": target["verify_desc"], "recheck_overall_status": recheck.get("overall_status"),
        "elapsed_seconds_generation": elapsed_gen, "call_log": call_log,
        "total_cost_jpy": round(sum(c.get("cost_jpy", 0.0) for c in call_log), 4),
    }


# ------------------------------------------------------------
# (3) narrow_scope型: hormuz_run03_standard(HF-009) J-1 vs J-2
# ------------------------------------------------------------
HORMUZ_JA_BEFORE = "報道時点では約二点六パーセント高で、一バレル八十五ドルを超えていました。"
HORMUZ_JA_TARGET = "このとき確認できるのは、撤回の直後に原油価格が全面的に下落したわけではない、ということです。"
HORMUZ_JA_AFTER = "同じ時間帯には、アメリカとイランの攻撃、海上封鎖、タンカーの安全への懸念が続いていました。"
HORMUZ_EN_BEFORE = "At the time of reporting, they were up about 2.6 percent, above 85 dollars a barrel."
HORMUZ_EN_TARGET = "Oil prices did not fall across the whole market after the plan was withdrawn."
HORMUZ_EN_AFTER = "At the same time, attacks by the United States and Iran continued."
HORMUZ_REWRITE_HINT = (
    "Narrow the claim's scope to match the Ledger: HF-009 only supports that Brent crude oil "
    "futures prices briefly pulled back and then returned to a high level; it does not establish "
    "that oil prices in general, or across the whole market, avoided falling. Narrow the sentence "
    "so it refers specifically to Brent crude futures, not the whole oil market."
)

J1_DEVELOPER_MSG = (
    "You are a bilingual (Japanese/English) editor performing a minimal, local, paired edit to fix "
    "a Ledger scope deviation. Edit ONLY the flagged sentence pair (JA + its EN counterpart). Do not "
    "change anything else."
)
J1_PROMPT_TEMPLATE = """[Verified Fact Ledger]
{ledger_text}

[JA target sentence (with before/after for context only)]
before: {ja_before}
TARGET: {ja_target}
after: {ja_after}

[EN target sentence (with before/after for context only)]
before: {en_before}
TARGET: {en_target}
after: {en_after}

[rewrite_hint]
{rewrite_hint}

Revise ONLY the JA target sentence and ONLY the EN target sentence (do not touch before/after). \
Return strict JSON: {{"ja_revised": "...", "en_revised": "..."}}"""

J2_DEVELOPER_MSG = (
    "You are the JA article writer. You must revise the full JA article to fix ONE flagged "
    "sentence, while keeping every other sentence character-for-character identical."
)
J2_PROMPT_TEMPLATE = """[Verified Fact Ledger]
{ledger_text}

[Full JA article]
{ja_full_text}

[Sentence to fix]
{ja_target}

[Checker's issue / rewrite_hint]
{rewrite_hint}

Rewrite ONLY the sentence above (narrow its scope per the rewrite_hint). Do NOT change any other \
sentence in the article, not even punctuation or spacing. Return the FULL revised JA article text, \
nothing else (no explanation, no code fences)."""

J2_TRANSLATE_DEVELOPER_MSG = "You are translating a single revised Japanese sentence into English, matching the style of the surrounding English article."
J2_TRANSLATE_PROMPT_TEMPLATE = """[Surrounding English context]
before: {en_before}
after: {en_after}

[Revised Japanese sentence to translate]
{ja_revised_target}

Translate the revised Japanese sentence into English in a style consistent with the surrounding \
context. Return ONLY the translated English sentence, nothing else."""


def extract_json_obj(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n|```$", "", text).strip()
    return json.loads(text)


def run_j1(client, state, consecutive_errors, fixture: dict) -> dict:
    call_log = []
    ledger_text = fixture["ledger_text"]
    prompt = J1_PROMPT_TEMPLATE.format(
        ledger_text=ledger_text, ja_before=HORMUZ_JA_BEFORE, ja_target=HORMUZ_JA_TARGET,
        ja_after=HORMUZ_JA_AFTER, en_before=HORMUZ_EN_BEFORE, en_target=HORMUZ_EN_TARGET,
        en_after=HORMUZ_EN_AFTER, rewrite_hint=HORMUZ_REWRITE_HINT,
    )
    raw = simple_llm_call(client, state, consecutive_errors, call_log, "j1_paired_rewrite",
                           J1_DEVELOPER_MSG, prompt)
    try:
        parsed = extract_json_obj(raw) if raw else {}
    except Exception:  # noqa: BLE001
        parsed = {}
    ja_revised = parsed.get("ja_revised", "")
    en_revised = parsed.get("en_revised", "")

    ja_full_original = fixture["source_article_text"]
    en_full_original = fixture["article_text"]
    ja_found = HORMUZ_JA_TARGET in ja_full_original
    en_found = HORMUZ_EN_TARGET in en_full_original
    ja_updated = ja_full_original.replace(HORMUZ_JA_TARGET, ja_revised, 1) if (ja_found and ja_revised) else ja_full_original
    en_updated = en_full_original.replace(HORMUZ_EN_TARGET, en_revised, 1) if (en_found and en_revised) else en_full_original

    # 削除・変更が外側の文へ及んでいないかの機械diff(¥0)
    outside_diff_ja = 0 if ja_updated.replace(ja_revised, "", 1) == ja_full_original.replace(HORMUZ_JA_TARGET, "", 1) else "unknown(non_exact_replace)"

    ja_check_fn = make_check_fn(client, state, consecutive_errors, ledger_text, call_log, "j1_ja_factcheck")
    ja_check = ja_check_fn(ja_updated)
    en_check_fn = make_check_fn(client, state, consecutive_errors, ledger_text, call_log, "j1_en_recheck")
    en_check = en_check_fn(en_updated)

    return {
        "method": "J-1", "sub_id": "hormuz_HF009_narrow_scope",
        "ja_found": ja_found, "en_found": en_found,
        "ja_revised": ja_revised, "en_revised": en_revised,
        "ja_check_overall_status": ja_check.get("overall_status"),
        "en_check_overall_status": en_check.get("overall_status"),
        "resolved": (ja_check.get("overall_status") == "LEDGER_COMPLIANT"
                     and en_check.get("overall_status") == "LEDGER_COMPLIANT"),
        "outside_target_diff_ja": outside_diff_ja,
        "call_log": call_log, "total_cost_jpy": round(sum(c.get("cost_jpy", 0.0) for c in call_log), 4),
    }


def count_sentence_diff_ja(original: str, updated: str, target_sentence: str) -> dict:
    def split_ja(text: str) -> list:
        return [s for s in re.split(r"(?<=。)", text) if s.strip()]
    orig_sents = split_ja(original)
    upd_sents = split_ja(updated)
    orig_non_target = [s for s in orig_sents if s.strip() != target_sentence.strip()]
    upd_non_target = [s for s in upd_sents if s.strip() != target_sentence.strip()]
    # 対象文以外で長さが変わった場合、素朴に集合比較(順序無視)で差分検出
    changed = len(set(orig_non_target) ^ set(upd_non_target))
    return {"n_orig_non_target_sentences": len(orig_non_target),
            "n_upd_non_target_sentences": len(upd_non_target),
            "n_non_target_sentences_changed_symmetric_diff": changed}


def run_j2(client, state, consecutive_errors, fixture: dict) -> dict:
    call_log = []
    ledger_text = fixture["ledger_text"]
    ja_full_original = fixture["source_article_text"]
    en_full_original = fixture["article_text"]

    prompt = J2_PROMPT_TEMPLATE.format(
        ledger_text=ledger_text, ja_full_text=ja_full_original, ja_target=HORMUZ_JA_TARGET,
        rewrite_hint=HORMUZ_REWRITE_HINT,
    )
    ja_full_revised = simple_llm_call(client, state, consecutive_errors, call_log, "j2_ja_full_regen",
                                       J2_DEVELOPER_MSG, prompt) or ja_full_original

    diff_stats = count_sentence_diff_ja(ja_full_original, ja_full_revised, HORMUZ_JA_TARGET)

    # 対象文の改訂結果を抽出(素朴に「元のtarget文が本文から消え、代わりに
    # 何らかの文が挿入されているか」を確認する目的の簡易抽出。抽出できない
    # 場合はfull textのdiffのみで評価する)
    trans_prompt = J2_TRANSLATE_PROMPT_TEMPLATE.format(
        en_before=HORMUZ_EN_BEFORE, en_after=HORMUZ_EN_AFTER, ja_revised_target=ja_full_revised,
    )
    # 対象文だけを渡す(全文を渡すと翻訳が不安定になるため、全文revised内の
    # target文相当箇所をヒューリスティックに使う。厳密な抽出は行わず、
    # J-2の「全文を書き直す」という設計上の性質どおり、全文revisedそのものを
    # 参考情報として渡した上でtarget文の位置の役割を担う一文を訳させる)
    en_revised_target = simple_llm_call(client, state, consecutive_errors, call_log,
                                         "j2_translate_target", J2_TRANSLATE_DEVELOPER_MSG, trans_prompt)

    en_found = HORMUZ_EN_TARGET in en_full_original
    en_updated = (en_full_original.replace(HORMUZ_EN_TARGET, en_revised_target, 1)
                  if (en_found and en_revised_target) else en_full_original)

    ja_check_fn = make_check_fn(client, state, consecutive_errors, ledger_text, call_log, "j2_ja_factcheck")
    ja_check = ja_check_fn(ja_full_revised)
    en_check_fn = make_check_fn(client, state, consecutive_errors, ledger_text, call_log, "j2_en_recheck")
    en_check = en_check_fn(en_updated)

    return {
        "method": "J-2", "sub_id": "hormuz_HF009_narrow_scope",
        "ja_full_revised": ja_full_revised, "en_revised_target": en_revised_target,
        "diff_stats_outside_target": diff_stats,
        "ja_check_overall_status": ja_check.get("overall_status"),
        "en_check_overall_status": en_check.get("overall_status"),
        "resolved": (ja_check.get("overall_status") == "LEDGER_COMPLIANT"
                     and en_check.get("overall_status") == "LEDGER_COMPLIANT"),
        "call_log": call_log, "total_cost_jpy": round(sum(c.get("cost_jpy", 0.0) for c in call_log), 4),
    }


def main():
    client = vfl01.get_client()
    state = load_budget_state()
    consecutive_errors = [0]
    results = {}
    stopped, stop_reason = False, None

    try:
        results["delete_type"] = run_delete_type(client, state, consecutive_errors)

        replace_results = []
        for target in REPLACE_TARGETS:
            e1 = run_e1_for_target(client, state, consecutive_errors, target)
            save_json(f"{OUT_DIR}/replace_type/{target['sub_id']}_E1.json", e1)
            replace_results.append(e1)
            e2 = run_e2_for_target(client, state, consecutive_errors, target)
            save_json(f"{OUT_DIR}/replace_type/{target['sub_id']}_E2.json", e2)
            replace_results.append(e2)
        results["replace_type"] = replace_results

        hormuz_fixture = {f["id"]: f for f in g6.step3_fixtures()}["hormuz_run03_standard"]
        j1 = run_j1(client, state, consecutive_errors, hormuz_fixture)
        save_json(f"{OUT_DIR}/narrow_scope_type/J1.json", j1)
        j2 = run_j2(client, state, consecutive_errors, hormuz_fixture)
        save_json(f"{OUT_DIR}/narrow_scope_type/J2.json", j2)
        results["narrow_scope_type"] = [j1, j2]
    except TrialAbort as e:
        stopped = True
        stop_reason = str(e)

    summary = {
        "stopped": stopped, "stop_reason": stop_reason,
        "cumulative_jpy": round(state["cumulative_jpy"], 4),
        "cumulative_calls": state["cumulative_calls"],
        "cumulative_errors": state["cumulative_errors"],
    }
    save_json(f"{OUT_DIR}/summary_stage3_rewrite_trial.json", {"summary": summary, "results": results})
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
