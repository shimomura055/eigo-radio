# ============================================================
# er034_key_phrase_db_hybrid_source_reference_contract_trial_06_contract.py
# KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-TRIAL-06 (Phase B)
# ============================================================
# Fable設計レビュー決定(docs/pm/design_kp_source_reference_contract_01.md
# §13-14、B改良版=候補ID方式+非ブロッキングの取り違え検知)の実装。
#
# 既存selector schema(er003_key_words_min_unit._ITEM_SCHEMA_PROPERTIES、
# Production/Trial-04/05が共有する_ITEM_SCHEMA_PROPERTIES)から
# `source_sentence`/`source_span`を除去し、代わりに
# `source_candidate_id`(enum、当該呼び出しのshortlist候補IDのみ許可)を
# 必須化する。LLMには本文文字列を一切書かせず、shortlist候補が既に
# 決定論的に保持している`surface_form`/`source_span`/`context_sentence_id`
# から、Python側で`source_sentence`/`source_span`を復元してから既存
# Production validator(`p2g.validate_min_unit_selection`)へそのまま渡す。
#
# `surface_echo`(任意に見えるが本schemaでは必須文字列)は、モデルが選んだ
# つもりの表現を短く書かせ、復元結果(candidate.surface_form/source_span)
# と正規化比較して不一致なら`candidate_mismatch_suspected=True`を記録する
# だけの非ブロッキングチェックである(validatorのPASS/INVALID判定には
# 一切使わない、STOPさせない)。
#
# 本ファイルはProduction module(er003_key_words_min_unit /
# er003_key_words_production / er003_key_phrase_source_gate_01 /
# er030_key_phrase_db_hybrid_selector_01)を読み取り専用でimportし、
# 無変更のまま再利用する(schemaはコピーして差分適用、validator/
# source gate判定ロジック自体は複製しない)。
# ============================================================

from __future__ import annotations

import time
from typing import Callable, Optional

import er003_key_words_min_unit as p2g
import er003_key_words_production as prod
import er009_n1_routing_governance_10_actual_model_cost as pricing
import er030_key_phrase_db_hybrid_selector_01 as selector01

CANDIDATE_ID_PREFIX = "C"


# ------------------------------------------------------------
# 候補ID付与(attach_compact_context相当の処理への軽量拡張、Trial層のみ、
# 既存er028_key_phrase_db_hybrid_trial_03_stage1.attach_compact_contextは
# 無変更のまま使う)。
# ------------------------------------------------------------
def assign_candidate_ids(shortlist: list) -> dict:
    """shortlist(既にcontext_sentence_id付与済み)の各候補へ、呼び出し内で
    閉じた一意なcandidate_id(C1, C2, ...)を出現順に付与する。戻り値の
    `id_to_candidate`はcandidate_id -> 候補dict(source_span/surface_form/
    context_sentence_idを含む)。"""
    id_to_candidate = {}
    shortlist_with_ids = []
    for i, c in enumerate(shortlist, start=1):
        cid = f"{CANDIDATE_ID_PREFIX}{i}"
        c2 = dict(c)
        c2["candidate_id"] = cid
        shortlist_with_ids.append(c2)
        id_to_candidate[cid] = c2
    return {
        "shortlist_with_ids": shortlist_with_ids,
        "id_to_candidate": id_to_candidate,
        "candidate_ids": list(id_to_candidate.keys()),
    }


# ------------------------------------------------------------
# schema: 既存_ITEM_SCHEMA_PROPERTIES/_ITEM_REQUIRED_FIELDSから
# source_span/source_sentenceを除去し、source_candidate_id(enum)/
# surface_echoを同じ位置に差し込む(既存p2g/prodのschema定義自体は
# 変更しない、コピーして差分適用)。
# ------------------------------------------------------------
def build_item_schema_properties(candidate_ids: list) -> dict:
    props = {}
    for key, spec in p2g._ITEM_SCHEMA_PROPERTIES.items():
        if key == "source_span":
            props["source_candidate_id"] = {"type": "string", "enum": list(candidate_ids)}
            continue
        if key == "source_sentence":
            props["surface_echo"] = {"type": "string"}
            continue
        props[key] = spec
    return props


def build_item_required_fields() -> tuple:
    fields = []
    for key in p2g._ITEM_REQUIRED_FIELDS:
        if key == "source_span":
            fields.append("source_candidate_id")
        elif key == "source_sentence":
            fields.append("surface_echo")
        else:
            fields.append(key)
    return tuple(fields)


def build_json_schema(candidate_ids: list) -> dict:
    props = build_item_schema_properties(candidate_ids)
    required = list(build_item_required_fields())
    return {
        "name": "b2_key_words_source_reference_contract_selection",
        "schema": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "minItems": prod.PRODUCTION_ITEM_COUNT,
                    "maxItems": prod.PRODUCTION_ITEM_COUNT,
                    "items": {
                        "type": "object",
                        "properties": props,
                        "required": required,
                        "additionalProperties": False,
                    },
                },
            },
            "required": ["items"],
            "additionalProperties": False,
        },
        "strict": True,
    }


# ------------------------------------------------------------
# prompt: 既存SELECTION_GUIDANCE(er030_key_phrase_db_hybrid_selector_01.
# SELECTION_GUIDANCE)から「source_sentenceをそのまま使用」指示を除去し、
# candidate ID選定+surface_echo指示へ差し替える。他の選定方針(5件中
# 1件以上重要語区分・CEFR非優先等)は無変更のまま維持する。
# ------------------------------------------------------------
SOURCE_REFERENCE_SELECTION_GUIDANCE = """
【選定方針】
- 最終的に選ぶ5件は、必ず下記の候補一覧の中から選んでください。候補に
  無い新しい表現を作らないでください。
- 5個のうち少なくとも1個は、[重要な単語・単語群候補]区分から選んで
  ください(記事理解・再利用価値の高い重要な名詞・専門用語・複合語)。
- 残りは、[phrase / idiom / phrasal verb候補]区分を優先してください。
  良い候補が不足する場合のみ[word候補]区分で補ってください。
- CEFR難易度・語彙レベルを主要な判断軸にしないでください。
- 各itemのsource_candidate_idには、下記候補一覧の各行に付与されている
  candidate ID(例: C7)のうち、実際に選んだ候補のIDを1つだけ指定して
  ください。本文の文字列そのもの(元のsource_sentence/source_span相当の
  自由記述)は一切書かないでください。
- surface_echoには、選んだ候補が表す表現を短く(1〜6語程度)書いて
  ください。これは内部確認用の参考情報であり、正誤判定には使用しません。
"""


def format_candidate_line_with_id(c: dict, display_type_fn: Callable[[dict], str],
                                   evidence_fn: Callable[[dict], str]) -> str:
    cid = c["candidate_id"]
    sid = c.get("context_sentence_id") or "?"
    return (f"- id: {cid} | candidate: \"{c['surface_form']}\" | type: {display_type_fn(c)} | "
            f"occ: {c.get('occurrence_count_in_article', '?')} | "
            f"evidence: {evidence_fn(c)} | sentence: {sid}")


def build_lightweight_user_message(article_title: str, shortlist_with_ids: list,
                                    sentence_reference: dict, static_instructions: str,
                                    display_type_fn: Optional[Callable[[dict], str]] = None,
                                    evidence_fn: Optional[Callable[[dict], str]] = None) -> str:
    """既存er030.build_lightweight_user_messageと同じ構成(重要語/phrase/
    word区分・SENTENCE REFERENCE表)に、各候補行へcandidate ID(id: Cx)を
    追加しただけの派生版。SENTENCE REFERENCE表は文脈提示のためだけに残す
    (LLMがそこから文字列をコピーしてschemaへ書く経路はもう存在しない、
    schema自体にsource_sentence/source_spanが無いため構造的に不可能)。"""
    display_type_fn = display_type_fn or selector01._display_type
    evidence_fn = evidence_fn or selector01._compact_evidence_string

    important = [c for c in shortlist_with_ids if c.get("important_noun_phrase_candidate")]
    phrase = [c for c in shortlist_with_ids
              if not c.get("important_noun_phrase_candidate") and c["unit_type"] != "word"]
    word = [c for c in shortlist_with_ids
            if not c.get("important_noun_phrase_candidate") and c["unit_type"] == "word"]

    lines = [static_instructions.rstrip(), ""]
    lines.append(f"【Topic】title: {article_title}")
    lines.append("")
    lines.append("【重要な単語・単語群候補】")
    if important:
        lines.extend(format_candidate_line_with_id(c, display_type_fn, evidence_fn) for c in important)
    else:
        lines.append("(なし)")
    lines.append("")
    lines.append("【phrase / idiom / phrasal verb候補】")
    if phrase:
        lines.extend(format_candidate_line_with_id(c, display_type_fn, evidence_fn) for c in phrase)
    else:
        lines.append("(なし)")
    lines.append("")
    lines.append("【word候補】")
    if word:
        lines.extend(format_candidate_line_with_id(c, display_type_fn, evidence_fn) for c in word)
    else:
        lines.append("(なし)")
    lines.append("")
    lines.append("【SENTENCE REFERENCE】(文脈参照専用。この表の文字列をそのままitemへ書かないでください)")
    for sid in sorted(sentence_reference, key=lambda s: int(s[1:])):
        lines.append(f'{sid}: "{sentence_reference[sid]}"')
    lines.append(SOURCE_REFERENCE_SELECTION_GUIDANCE.rstrip())
    return "\n".join(lines) + "\n"


# ------------------------------------------------------------
# API呼び出し(既存er030._make_instrumented_selector_factoryと同じ計測
# パターン、schemaだけ候補ID方式のものに差し替え)。
# ------------------------------------------------------------
def _usage_dict(usage) -> dict:
    return selector01._usage_dict(usage)


def make_instrumented_selector_factory(user_message: str, model: str, candidate_ids: list,
                                        usage_sink: list, contract_violation_sink: list = None,
                                        client=None):
    schema = build_json_schema(candidate_ids)

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
                text={"format": {"type": "json_schema", **schema}},
                input=[
                    {"role": "developer", "content": prod.SELECTOR_DEVELOPER_MESSAGE},
                    {"role": "user", "content": user_message},
                ],
            )
            elapsed = time.time() - t0
            if response.model != model:
                if contract_violation_sink is not None:
                    contract_violation_sink.append(
                        {"expected_model": model, "actual_model": response.model})
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


# ------------------------------------------------------------
# 候補ID解決+復元(決定論的): source_span = candidate["surface_form"]、
# source_sentence = sentence_reference[candidate["context_sentence_id"]]
# (無ければsource_spanそのもの、既存attach_compact_contextがcontext_
# sentence_idを付与できなかった稀なケースへのfallback)。
#
# 実装上の注意(Trial-06実データで発見、修正1回目): 候補dictの
# `source_span`フィールドは、候補生成カテゴリによっては「短い句」では
# なく「その句が最初に出現した文全体」を保持している(既存共有Stage1
# `er027_key_phrase_db_hybrid_trial_02_stage1.find_repeated_compound_
# noun_candidates`480行、`"source_span": first_seen_source.get(merge_
# key, best_surface)`が文全体を代入している)。これは旧来の自由記述
# 契約では一切参照されない内部フィールドだったため無害だったが(LLMが
# 自分でsource_span/source_sentenceを自由生成していたため)、候補ID
# 契約ではこのフィールドをそのまま使うとvalidatorの
# 「source_spanがsource_sentence内に存在しない」判定に落ちる
# (実データ: meta_a2/meta_b1b/hormuz_b1b/aihiring_b1/melos_a2で発生、
# REPORT参照)。設計書§3(b)・§14の推奨どおり、`surface_form`
# (Stage 1のn-gram抽出時点で本文からの実測トークン列として決定済み)を
# source_spanの復元元として使う(既存Stage1コード自体は無変更のまま、
# Trial層がどのフィールドを読むかだけを変更する)。
# ------------------------------------------------------------
def restore_source_fields(items: list, id_to_candidate: dict, sentence_reference: dict) -> dict:
    restored_items = []
    unresolved = []
    mismatch_count = 0
    mismatch_details = []
    for i, item in enumerate(items):
        cid = item.get("source_candidate_id")
        candidate = id_to_candidate.get(cid)
        if candidate is None:
            unresolved.append({"index": i, "source_candidate_id": cid})
            restored_items.append(dict(item))
            continue
        source_span = candidate.get("surface_form") or candidate.get("source_span")
        sid = candidate.get("context_sentence_id")
        source_sentence = sentence_reference.get(sid) if sid else None
        if not source_sentence:
            source_sentence = source_span

        new_item = dict(item)
        new_item["source_span"] = source_span
        new_item["source_sentence"] = source_sentence
        new_item["resolved_candidate_id"] = cid
        new_item["resolved_candidate_surface_form"] = candidate.get("surface_form")

        surface_echo = item.get("surface_echo") or ""
        mismatch = False
        if surface_echo.strip():
            norm_echo = p2g._normalize_for_match(surface_echo)
            norm_surface = p2g._normalize_for_match(candidate.get("surface_form") or "")
            norm_span = p2g._normalize_for_match(source_span or "")
            if norm_echo != norm_surface and norm_echo != norm_span and \
                    norm_echo not in norm_surface and norm_surface not in norm_echo:
                mismatch = True
        new_item["candidate_mismatch_suspected"] = mismatch
        if mismatch:
            mismatch_count += 1
            mismatch_details.append({
                "index": i, "source_candidate_id": cid, "surface_echo": surface_echo,
                "candidate_surface_form": candidate.get("surface_form"),
            })
        restored_items.append(new_item)
    return {
        "items": restored_items, "unresolved": unresolved,
        "mismatch_count": mismatch_count, "mismatch_details": mismatch_details,
    }


# ------------------------------------------------------------
# gate: parse(既存p2g.parse_selector_json、無変更)-> candidate_id解決
# (新規)-> source_sentence/source_spanを代入(新規)->
# p2g.validate_min_unit_selection(既存、無変更)、という順に呼ぶ薄い
# オーケストレーション関数。既存run_production_selection_gateは
# parse直後にvalidateする一体型のためこの用途には使えず(§8の設計
# レビュー結論どおり)、Trial層に新規実装する。1本文1 call(max_attempts
# 相当の再試行はしない、既存DB Hybrid selectorのmax_attempts=1と同じ
# 原則)。
# ------------------------------------------------------------
def run_source_reference_contract_gate(
        article_id: str, make_selector_factory: Callable[[], Callable], article_text: str,
        id_to_candidate: dict, sentence_reference: dict,
        strategy_id: str = prod.STANDARD_STRATEGY_ID) -> dict:
    selector_fn = make_selector_factory()
    try:
        raw_text, model_id, response_id = selector_fn()
    except Exception as e:
        return {
            "status": "TECHNICAL_GENERATION_FAILED", "parsed": None, "model_id": None,
            "response_id": None, "error": f"{type(e).__name__}: {e}", "raw_text": None,
            "restore_telemetry": {}, "source_gate_missing": [],
        }

    try:
        parsed = p2g.parse_selector_json(raw_text)
    except Exception as e:
        return {
            "status": "PARSE_FAILED", "parsed": None, "model_id": model_id,
            "response_id": response_id, "error": str(e), "raw_text": raw_text,
            "restore_telemetry": {}, "source_gate_missing": [],
        }

    restore_result = restore_source_fields(parsed.get("items", []), id_to_candidate, sentence_reference)
    if restore_result["unresolved"]:
        # schemaのenum制約により通常発生しないはずの防御的分岐(§12(iii))。
        return {
            "status": "UNRESOLVED_CANDIDATE_ID", "parsed": parsed, "model_id": model_id,
            "response_id": response_id, "raw_text": raw_text,
            "restore_telemetry": restore_result, "source_gate_missing": [],
        }

    parsed_restored = dict(parsed)
    parsed_restored["items"] = restore_result["items"]
    parsed_with_metadata = prod.attach_runtime_metadata(parsed_restored, article_id, strategy_id)
    validation = p2g.validate_min_unit_selection(
        parsed_with_metadata, article_text, expected_item_count=prod.PRODUCTION_ITEM_COUNT)

    # 既存er030の生article照合Gate相当ロジックをそのまま再利用(複製しない)。
    source_gate_missing = []
    if validation["status"] == "KEY_WORDS_STRUCTURE_PASS":
        source_gate_missing = selector01._verify_source_spans_against_raw_article(
            parsed_with_metadata["items"], article_text)

    return {
        "status": validation["status"], "parsed": parsed_with_metadata,
        "validation_reasons": validation["reasons"], "item_reasons": validation["item_reasons"],
        "model_id": model_id, "response_id": response_id, "raw_text": raw_text,
        "restore_telemetry": restore_result, "source_gate_missing": source_gate_missing,
    }


def cost_jpy_for_usage(model_id: str, usage: dict) -> float:
    return pricing.cost_jpy_for_call(
        "openai", model_id, usage.get("input_tokens"),
        usage.get("cached_input_tokens"), usage.get("output_tokens"))


# ------------------------------------------------------------
# 診断用(API呼び出しなし、費用¥0): shortlist全件(選定される5件だけで
# なく)について、`surface_form`(復元に使うsource_span)が
# `context_sentence_id`が指すsentence_referenceの文に実在するかを
# 機械確認する。実装修正1回目(source_span→surface_form切り替え)の
# 網羅性を、追加API呼び出しなしで事前に確認するための関数。
# ------------------------------------------------------------
def audit_shortlist_source_span_consistency(shortlist_with_ids: list, sentence_reference: dict) -> dict:
    inconsistent = []
    no_context_sentence = []
    for c in shortlist_with_ids:
        surface_form = c.get("surface_form")
        sid = c.get("context_sentence_id")
        if not sid:
            no_context_sentence.append({"candidate_id": c.get("candidate_id"), "surface_form": surface_form})
            continue
        sentence = sentence_reference.get(sid, "")
        if p2g._normalize_for_match(surface_form or "") not in p2g._normalize_for_match(sentence):
            inconsistent.append({
                "candidate_id": c.get("candidate_id"), "surface_form": surface_form,
                "context_sentence_id": sid, "sentence": sentence,
                "matched_dbs": c.get("matched_dbs"),
            })
    return {
        "total_candidates": len(shortlist_with_ids),
        "inconsistent_count": len(inconsistent),
        "inconsistent": inconsistent,
        "no_context_sentence_count": len(no_context_sentence),
        "no_context_sentence": no_context_sentence,
    }
