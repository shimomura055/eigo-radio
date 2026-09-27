# ============================================================
# er030_key_phrase_db_hybrid_selector_01.py
# KEY-PHRASE-DB-HYBRID-FAMILY-X-PRODUCTION-WIRING-01
# ============================================================
# DB Hybrid方式(Primary)のSelector層: er030_key_phrase_db_hybrid_core_01
# (Stage1候補生成+shortlist組み立て、ロジック無変更で昇格)が返す
# compact shortlistから、既存Production Strategy L選定gate
# (`er003_key_words_production.run_production_selection_gate`、
# schema/model/validator一切無変更)を1回だけ呼び出す軽量prompt経由の
# 選定を行う。
#
# Fallback設計(ユーザー正式決定、2026-09-27): 以下のいずれかに該当する
# 場合、`DbHybridFailure`を送出する(呼び出し元
# `er003_v1_n3_01_scaffold_generate.run_key_phrase_selection`が捕捉し、
# 既存Strategy L全文方式[本文全体をprompt送信する既存経路]へ
# fallbackする)。
#   - SHORTLIST_TOO_SMALL: shortlist件数が閾値未満(機械screeningが
#     ほぼ機能しない短い/特殊な記事、5件を安全に選べない可能性が高い)
#   - TECHNICAL_GENERATION_FAILED/PARSE_FAILED/KEY_WORDS_STRUCTURE_INVALID:
#     既存run_production_selection_gate()自体が返すstatus(P2G/P2Iの
#     既存validatorが不合格と判定、コード変更なし)
#   - SELECTOR_EXCEPTION: Stage1/shortlist構築自体が例外を送出(DB読込
#     失敗・Wiktionary API異常等)
#   - COST_GUARD_EXCEEDED: 1記事あたりの実測費用が安全域(Trial-04実測
#     最大¥2.03の約2.5倍、¥5.0)を超過(reasoning token異常増加等の
#     runaway検知)
#
# 費用計測(cost_jpy)はProduction共有pricing module
# (er009_n1_routing_governance_10_actual_model_cost)を再利用する
# (新しい価格表は作らない)。SELECTION_GUIDANCE/extract_static_
# instructions/extract_article_title/assert_no_full_article_bodyは
# er028_key_phrase_db_hybrid_trial_03_run(Trial-03確定版、既に複数の
# 既存Production隣接scriptが共有依存として読み取り専用でimportしている
# frozen text/pure-function utility)をそのまま再利用し、Production側で
# 別テキストとして複製しない(SELECTION_GUIDANCE文言の将来的な乖離を防ぐ)。
# ============================================================

from __future__ import annotations

import json
import os
import time

import er003_b1_p2_keywords as bk
import er003_key_words_production as prod
import er006_model_routing_contract_01 as routing
import er009_n1_routing_governance_10_actual_model_cost as pricing
import er028_key_phrase_db_hybrid_trial_03_run as base
import er030_key_phrase_db_hybrid_core_01 as core

# Trial-04実測(12本文合計¥12.8159、最大¥2.0284/記事)の約2.5倍を安全域と
# する(runaway reasoning token検知、通常記事はこの閾値に到達しない)。
DEFAULT_COST_GUARD_JPY = 5.0

# Trial-04実測(12本文全件20〜24件)の下限を下回るほど機械screeningが
# 機能していない記事は、DB Hybrid方式の前提(十分な候補プールから
# モデルが5件選ぶ)が崩れているとみなし、Strategy L全文方式へ委ねる。
MIN_SHORTLIST_COUNT = 8


class DbHybridFailure(Exception):
    """DB Hybrid selectorが失敗し、呼び出し元がStrategy L全文方式へ
    fallbackすべきことを示す。telemetryには可能な限りcost_jpy/model_id等
    実測情報を含める(fallback発火の観測可能性を確保する)。"""

    def __init__(self, reason_code: str, message: str, telemetry: dict = None):
        super().__init__(message)
        self.reason_code = reason_code
        self.telemetry = telemetry or {}


def _usage_dict(usage) -> dict:
    if usage is None:
        return {}
    d = {"input_tokens": getattr(usage, "input_tokens", None),
         "output_tokens": getattr(usage, "output_tokens", None),
         "total_tokens": getattr(usage, "total_tokens", None)}
    in_details = getattr(usage, "input_tokens_details", None)
    if in_details is not None:
        d["cached_input_tokens"] = getattr(in_details, "cached_tokens", None)
    out_details = getattr(usage, "output_tokens_details", None)
    if out_details is not None:
        d["reasoning_tokens"] = getattr(out_details, "reasoning_tokens", None)
    return d


def _make_instrumented_selector_factory(user_message: str, model: str, usage_sink: list, client=None):
    """既存Trial cost tracking(er028_key_phrase_db_hybrid_trial_03_run.
    make_instrumented_selector_factory)と同じ計測パターンを、Production
    定数(prod.*)のみを使って再構成したもの(選定ロジック自体は
    prod.run_production_selection_gate/prod.SELECTOR_JSON_SCHEMA等の
    既存Production資産をそのまま呼び出すだけで、新しい判定ロジックは
    含まない)。"""
    def factory():
        nonlocal client
        if client is None:
            from dotenv import load_dotenv
            load_dotenv()
            from openai import OpenAI
            client = OpenAI()

        def fn():
            t0 = time.time()
            response = client.responses.create(
                model=model,
                reasoning={"effort": prod.SELECTOR_REASONING_EFFORT},
                text={"format": {"type": "json_schema", **prod.SELECTOR_JSON_SCHEMA}},
                input=[
                    {"role": "developer", "content": prod.SELECTOR_DEVELOPER_MESSAGE},
                    {"role": "user", "content": user_message},
                ],
            )
            elapsed = time.time() - t0
            if response.model != model:
                raise prod.SelectorModelMismatchError(
                    f"応答モデルが不一致です(期待: {model}, 実際: {response.model})")
            text = getattr(response, "output_text", None)
            usage_sink.append({
                "response_id": response.id, "model": response.model,
                "usage": _usage_dict(getattr(response, "usage", None)),
                "elapsed_sec": round(elapsed, 3),
            })
            if not text or not text.strip():
                import er003_ja_to_en_translation as er003
                raise er003.restore.GenerationEmptyOrBrokenError("selector応答が空です")
            return text, response.model, response.id

        fn.model = model
        fn.reasoning_effort = prod.SELECTOR_REASONING_EFFORT
        fn.uses_web_search_tool = False
        fn.uses_structured_output = True
        return fn

    return factory


def _display_type(c: dict) -> str:
    if c.get("important_noun_phrase_candidate"):
        if c.get("unit_type") == "word":
            return "important_word"
        return "noun_phrase"
    return c["unit_type"]


def format_candidate_line(c: dict) -> str:
    sid = c.get("context_sentence_id") or "?"
    return (f"- candidate: \"{c['surface_form']}\" | type: {_display_type(c)} | "
            f"occ: {c.get('occurrence_count_in_article', '?')} | "
            f"evidence: {base._compact_evidence_string(c)} | sentence: {sid}")


def build_lightweight_user_message(article_title: str, shortlist_info: dict,
                                    sentence_reference: dict, static_instructions: str) -> str:
    """KEY-PHRASE-DB-HYBRID-TRIAL-04(er029_key_phrase_db_hybrid_trial_04_
    run.build_lightweight_user_message_v4)と同一のprompt構成(Fix Bの
    important_word表示区別を含む)。article全文は一切含まない。"""
    important = [c for c in shortlist_info["shortlist"] if c.get("important_noun_phrase_candidate")]
    phrase = [c for c in shortlist_info["shortlist"]
              if not c.get("important_noun_phrase_candidate") and c["unit_type"] != "word"]
    word = [c for c in shortlist_info["shortlist"]
            if not c.get("important_noun_phrase_candidate") and c["unit_type"] == "word"]

    lines = [static_instructions.rstrip(), ""]
    lines.append(f"【Topic】title: {article_title}")
    lines.append("")
    lines.append("【重要な単語・単語群候補】")
    if important:
        lines.extend(format_candidate_line(c) for c in important)
    else:
        lines.append("(なし)")
    lines.append("")
    lines.append("【phrase / idiom / phrasal verb候補】")
    if phrase:
        lines.extend(format_candidate_line(c) for c in phrase)
    else:
        lines.append("(なし)")
    lines.append("")
    lines.append("【word候補】")
    if word:
        lines.extend(format_candidate_line(c) for c in word)
    else:
        lines.append("(なし)")
    lines.append("")
    lines.append("【SENTENCE REFERENCE】")
    for sid in sorted(sentence_reference, key=lambda s: int(s[1:])):
        lines.append(f'{sid}: "{sentence_reference[sid]}"')
    lines.append(base.SELECTION_GUIDANCE.rstrip())
    return "\n".join(lines) + "\n"


def _serializable_stage1(st: dict) -> dict:
    keys_to_drop = {"sentence_units"}
    return {k: v for k, v in st.items() if k not in keys_to_drop}


def run_db_hybrid_selection(article_text: str, out_dir: str, article_id: str, source_level: str,
                             process: str = None, diagnostic_note: str = None,
                             dbs: dict = None, cost_guard_jpy: float = None) -> dict:
    """DB Hybrid方式でKey Phrase選定gateを1回実行する。戻り値は既存
    `run_key_phrase_selection`(Strategy L全文方式)と同じ最小契約
    (`status`/`parsed`/`original_items`)を満たし、追加でtelemetry用の
    `cost_jpy`/`model_id`/`shortlist_total_count`/`kp_backend`を含む。

    失敗時(shortlist過少・validator不合格・例外・cost guard超過)は
    `DbHybridFailure`を送出する(呼び出し元がStrategy Lへfallback)。

    `cost_guard_jpy`(既定`DEFAULT_COST_GUARD_JPY`)は、fallback実発火の
    runtime evidence取得時にのみ、evidence/testスクリプトが明示的に
    小さい値へ上書きするための引数(通常のProduction配線からは渡さない、
    既定値のまま使う)。"""
    os.makedirs(out_dir, exist_ok=True)
    guard = cost_guard_jpy if cost_guard_jpy is not None else DEFAULT_COST_GUARD_JPY
    dbs = dbs if dbs is not None else core.load_group1_dbs()
    title = base.extract_article_title(article_text)

    try:
        s1r = core.run_stage1_and_shortlist(article_text, dbs, title)
    except Exception as e:
        raise DbHybridFailure(
            "SELECTOR_EXCEPTION", f"stage1/shortlist構築に失敗しました: {type(e).__name__}: {e}",
            telemetry={"reason_code": "SELECTOR_EXCEPTION", "error": f"{type(e).__name__}: {e}"}) from e

    stage1, shortlist_info = s1r["stage1"], s1r["shortlist_info"]
    shortlist_count = shortlist_info["shortlist_total_count"]

    with open(os.path.join(out_dir, "db_hybrid_stage1_debug.json"), "w", encoding="utf-8") as f:
        json.dump(_serializable_stage1(stage1), f, ensure_ascii=False, indent=2)

    if shortlist_count < MIN_SHORTLIST_COUNT:
        raise DbHybridFailure(
            "SHORTLIST_TOO_SMALL",
            f"shortlist件数({shortlist_count})が閾値({MIN_SHORTLIST_COUNT})未満です",
            telemetry={"reason_code": "SHORTLIST_TOO_SMALL", "shortlist_total_count": shortlist_count})

    static_instructions = base.extract_static_instructions(bk.load_prompt_template())
    lightweight_message = build_lightweight_user_message(
        title, shortlist_info, shortlist_info["sentence_reference"], static_instructions)
    if diagnostic_note:
        lightweight_message = lightweight_message + "\n\n" + diagnostic_note
    base.assert_no_full_article_body(lightweight_message, article_text)
    with open(os.path.join(out_dir, "keywords_selector_prompt.txt"), "w", encoding="utf-8") as f:
        f.write(lightweight_message)

    model = routing.require_model(process, routing.SUPPORT_MODEL) if process else prod.SELECTOR_MODEL
    usage_sink = []
    factory = _make_instrumented_selector_factory(lightweight_message, model, usage_sink)
    parsed, status, attempts, model_id, response_id = prod.run_production_selection_gate(
        article_id, factory, article_text, strategy_id=prod.STANDARD_STRATEGY_ID, max_attempts=1,
    )
    usage_entry = usage_sink[0] if usage_sink else {"usage": {}}
    usage = usage_entry.get("usage", {})
    cost_jpy = pricing.cost_jpy_for_call(
        "openai", model_id or model, usage.get("input_tokens"),
        usage.get("cached_input_tokens"), usage.get("output_tokens"))

    runtime_metadata = {
        "article_id": article_id, "strategy_id": prod.STANDARD_STRATEGY_ID, "source_level": source_level,
        "kp_backend": "db_hybrid", "final_status": status, "model_id": model_id, "response_id": response_id,
        "cost_jpy": round(cost_jpy, 4), "usage": usage,
        "shortlist_total_count": shortlist_count,
        "shortlist_info": {
            "phrase_included_count": shortlist_info["phrase_included_count"],
            "important_noun_included_count": shortlist_info["important_noun_included_count"],
            "word_included_count": shortlist_info["word_included_count"],
        },
        "attempts_detail": [{k: v for k, v in a.items() if k != "raw_text"} for a in attempts],
    }
    with open(os.path.join(out_dir, "keywords_runtime_metadata.json"), "w", encoding="utf-8") as f:
        json.dump(runtime_metadata, f, ensure_ascii=False, indent=2)

    if status != "KEY_WORDS_STRUCTURE_PASS":
        raise DbHybridFailure(
            status, f"DB Hybrid selector gateがPASSしませんでした(status={status})",
            telemetry={"reason_code": status, "cost_jpy": round(cost_jpy, 4), "model_id": model_id,
                       "shortlist_total_count": shortlist_count})

    if cost_jpy > guard:
        raise DbHybridFailure(
            "COST_GUARD_EXCEEDED",
            f"1記事あたりの実測費用(JPY {cost_jpy:.4f})が安全域(JPY {guard})を超過しました",
            telemetry={"reason_code": "COST_GUARD_EXCEEDED", "cost_jpy": round(cost_jpy, 4),
                       "model_id": model_id, "shortlist_total_count": shortlist_count})

    result = {
        "status": status, "parsed": parsed, "original_items": parsed["items"],
        "model_id": model_id, "response_id": response_id, "cost_jpy": round(cost_jpy, 4),
        "shortlist_total_count": shortlist_count, "kp_backend": "db_hybrid",
        "attempts_detail": [{k: v for k, v in a.items() if k != "raw_text"} for a in attempts],
    }
    return result
