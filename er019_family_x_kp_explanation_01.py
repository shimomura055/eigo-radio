# ============================================================
# er019_family_x_kp_explanation_01.py
# FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01 (W4)
# ============================================================
# 目的: Advanced(B1B)Key Phraseの中間segmentである英語解説
# (explanation_en)のtext生成をProduction正式経路へ配線する。
#
# text仕様(Prompt/schema/語数上限/禁止事項)は
# KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-TRIAL-02
# (er041_key_phrase_advanced_english_explanation_trial_02.py)で
# ユーザーが`APPROVED_FOR_PRODUCTION`と正式決定したB候補仕様を
# 逐語転記する(改変・別候補の追加は一切しない)。転記の忠実性は
# PROMPT_SHA256(このファイル内のPrompt定数から機械的に算出)を
# er041の同一定数から算出したハッシュとテストで突き合わせて保証する
# (`er019_family_x_kp_structure_wiring_01_test_01.py`参照)。
#
# 音声Style(Variant B)は本モジュールの対象外(TTS呼び出し側=
# er003_v1_n3_01_tts_generate.generate_key_phrase_explanation_en_verified
# + er033_tts_flash_lite_family_x_styles_01.KEY_PHRASE_EXPLANATION_EN)。
#
# 完全隔離の対象外(Production module): Key Phrase選定・canonicalization
# 自体(er003_key_words_*、er030_*)は一切変更しない。本モジュールは
# 既に選定・canonicalization済みのKey Phrase item(display_phrase/
# source_sentence/japanese_gloss)を入力として受け取るだけである。
# ============================================================

from __future__ import annotations

import hashlib
import json
import re

import er006_model_routing_contract_01 as routing
import er009_n1_routing_governance_10_actual_model_cost as pricing

MANAGEMENT_ID = "FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01"
SOURCE_TRIAL_MANAGEMENT_ID = "KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-TRIAL-02"

# ER-006-MODEL-ROUTING-CONTRACT-01: 新規process。既存のKey Phrase選定
# (B1_SUPPORT/A2_SUPPORT)と同じApproved Model(SUPPORT_MODEL=
# "gpt-5.6-luna")を使う(新規モデル追加なし)。
MODEL_ROUTING_PROCESS = "KEY_PHRASE_ADVANCED_EXPLANATION"
MODEL = "gpt-5.6-luna"
REASONING_EFFORT = "medium"

# er041_key_phrase_advanced_english_explanation_trial_02.MAX_WORDSの
# 逐語転記(前回実測ベースの語数上限、新規に決めた閾値ではない)。
MAX_WORDS = 15

# er041のEXPLANATION_EN_SPEC_SENTENCE(=er017_key_phrase_level_spec_
# trial_01.ADVANCED_USER_TEMPLATEのexplanation_enフィールド定義文)を
# 逐語転記。
EXPLANATION_EN_SPEC_SENTENCE = (
    "a short, simple English explanation of the meaning — one sentence, "
    "plain words, easier than the phrase itself; not a dictionary "
    "definition. Example style: \"raise privacy concerns\" -> \"to make "
    "people worry about how personal information is used or protected\""
)

# er041.DEVELOPER_MESSAGEの逐語転記。
DEVELOPER_MESSAGE = (
    "You write short English explanations for Key Phrases that Japanese "
    "adult learners are studying in an English-learning news audio "
    "program. The phrases are already chosen; do not change them."
)

# er041.USER_TEMPLATE_HEADERの逐語転記。
USER_TEMPLATE_HEADER = f"""For each of the 5 Key Phrases below, write ONE short English
explanation of its meaning for an ADVANCED (CEFR B1) English learner.

Explanation instruction (reused from a prior approved Trial spec):
{EXPLANATION_EN_SPEC_SENTENCE}

Additional rules for this task:
- The phrase itself must NOT be changed. Return it exactly as given.
- Do not add any name, number, or fact that is not already in the
  phrase or in the source sentence given below.
- Do not just translate the Japanese reference meaning word-for-word.
  Write a natural English explanation of the same meaning.
- The explanation should still make sense if the phrase is used in a
  different context, not only in this one news story.

Key Phrases:
"""

# er041.USER_TEMPLATE_FOOTERの逐語転記。
USER_TEMPLATE_FOOTER = (
    '\nReturn JSON only: {"explanations": [ {"phrase": ..., '
    '"english_explanation": ...} x5 ]}'
)

# er041.EXPLANATION_JSON_SCHEMAの逐語転記(5固定はTrial-02実測時点の
# Key Phrase件数[Advanced 4+1構成]を反映したもの、PROMPT_SHA256の算出
# 基準としてそのまま保持する)。
EXPLANATION_JSON_SCHEMA = {
    "name": "key_phrase_advanced_english_explanation_trial_02",
    "schema": {
        "type": "object",
        "properties": {
            "explanations": {
                "type": "array",
                "minItems": 5,
                "maxItems": 5,
                "items": {
                    "type": "object",
                    "properties": {
                        "phrase": {"type": "string"},
                        "english_explanation": {"type": "string"},
                    },
                    "required": ["phrase", "english_explanation"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["explanations"],
        "additionalProperties": False,
    },
    "strict": True,
}


# W5(Opus L2所見N-7是正、2026-09-29): 実際のKey Phrase件数
# (len(items))からminItems/maxItemsを導出する(5固定を廃止)。件数が
# 5以外になった場合でも、schema自体が実際の件数と食い違って
# parse失敗→技術retry消費→ExplanationGenerationErrorという不要な
# 高コスト失敗を起こさないようにする。PROMPT_SHA256(逐語性の機械証拠)
# はEXPLANATION_JSON_SCHEMA(5固定、Trial-02実測時点の値)から算出した
# ままにする(この値は「Trial-02のPromptを忠実転記したか」の検証専用
# であり、実行時に使われるschemaそのものではない)。
def _build_explanation_json_schema(n: int) -> dict:
    schema = json.loads(json.dumps(EXPLANATION_JSON_SCHEMA))
    schema["schema"]["properties"]["explanations"]["minItems"] = n
    schema["schema"]["properties"]["explanations"]["maxItems"] = n
    return schema

# Prompt逐語性の機械的証拠(このファイル単独で算出。er041の同一定数から
# 算出したハッシュと一致することをtestで確認する)。
_PROMPT_TEXT_FOR_HASH = "␟".join(
    [DEVELOPER_MESSAGE, USER_TEMPLATE_HEADER, USER_TEMPLATE_FOOTER,
     json.dumps(EXPLANATION_JSON_SCHEMA, sort_keys=True)])
PROMPT_SHA256 = hashlib.sha256(_PROMPT_TEXT_FOR_HASH.encode("utf-8")).hexdigest()


def build_explanation_user_message(items: list[dict]) -> str:
    """er041._build_explanation_user_messageと同一ロジック(逐語転記)。
    items各要素は{"display_phrase", "source_sentence", "japanese_gloss"}
    (keywords_canonicalized.jsonのitem、rank昇順ソート済み前提)。"""
    lines = [USER_TEMPLATE_HEADER]
    for i, it in enumerate(items, start=1):
        lines.append(
            f'{i}. phrase: "{it["display_phrase"]}"\n'
            f'   source_sentence: "{it["source_sentence"]}"\n'
            f'   japanese_reference_meaning (for accuracy check only, do '
            f'not translate literally): "{it["japanese_gloss"]}"\n'
        )
    lines.append(USER_TEMPLATE_FOOTER)
    return "".join(lines)


def _new_fact_candidates(explanation: str, phrase: str, source_sentence: str) -> list[str]:
    """er041._new_fact_candidatesと同一ロジック(逐語転記)。解説文中の
    大文字語頭語(文頭を除く)・数字トークンのうち、phrase/source_sentence
    に(大小無視で)出現しないものを新規Fact候補として返す。"""
    haystack = (phrase + " " + source_sentence).lower()
    tokens = re.findall(r"[A-Za-z0-9']+", explanation)
    candidates = []
    for i, tok in enumerate(tokens):
        is_number = tok[0].isdigit()
        is_cap_word = tok[0].isupper() and i > 0 and tok.lower() not in ("i",)
        if not (is_number or is_cap_word):
            continue
        if tok.lower() in haystack:
            continue
        candidates.append(tok)
    return candidates


def validate_explanation_qa(explanation: str, phrase: str, source_sentence: str,
                             max_words: int = MAX_WORDS) -> dict:
    """er041 cmd_evaluateの決定論的チェック(語数上限・新規Fact混入)を、
    Production validator(NG→技術retry対象)として使えるbool判定付きで
    再構成したもの(判定基準自体は逐語転記、新しい基準は追加しない)。"""
    words = re.findall(r"[A-Za-z']+", explanation or "")
    word_count = len(words)
    within_max_words = word_count <= max_words
    new_fact_tokens = _new_fact_candidates(explanation or "", phrase, source_sentence)
    passed = within_max_words and not new_fact_tokens
    return {
        "word_count": word_count, "within_max_words": within_max_words,
        "max_words": max_words, "new_fact_tokens": new_fact_tokens,
        "passed": passed,
    }


class ExplanationGenerationError(RuntimeError):
    """explanation生成が技術retry(1回)を使い切っても回復しなかった場合。"""


def _usage_dict(usage) -> dict:
    if usage is None:
        return {}
    d = {"input_tokens": getattr(usage, "input_tokens", None),
         "output_tokens": getattr(usage, "output_tokens", None)}
    in_details = getattr(usage, "input_tokens_details", None)
    if in_details is not None:
        d["cached_input_tokens"] = getattr(in_details, "cached_tokens", None)
    return d


def _default_call_fn_factory(client, model: str, schema: dict | None = None):
    """本番用call_fn(OpenAI Responses API、既存Production Key Phrase
    選定[er030_key_phrase_db_hybrid_selector_01._make_instrumented_
    selector_factory]と同一の呼び出しパターン)。test/mockでは
    generate_kp_explanations(call_fn=...)へ差し替える。

    schema省略時はEXPLANATION_JSON_SCHEMA(5固定)のまま(既存挙動、
    後方互換)。generate_kp_explanations()は実際のitems件数から算出した
    schemaを渡す(N-7是正)。"""
    schema = schema if schema is not None else EXPLANATION_JSON_SCHEMA

    def call_fn(user_message: str):
        response = client.responses.create(
            model=model,
            reasoning={"effort": REASONING_EFFORT},
            text={"format": {"type": "json_schema", **schema}},
            input=[
                {"role": "developer", "content": DEVELOPER_MESSAGE},
                {"role": "user", "content": user_message},
            ],
        )
        text = (getattr(response, "output_text", None) or "").strip()
        parsed = json.loads(text) if text else None
        return parsed, response.model, _usage_dict(getattr(response, "usage", None)), response.id
    return call_fn


def generate_kp_explanations(items: list[dict], call_fn=None, client=None) -> dict:
    """Advanced(B1B)Key Phrase 5件(4+1構成)まとめて1 callで英語解説
    (explanation_en)を生成する。

    items: [{"rank", "display_phrase", "source_sentence", "japanese_gloss"}, ...]

    戻り値: {"items": {rank: {"english_explanation": str|None, "qa": dict|None,
             "status": "OK"|"NG"|"NG_PHRASE_MISMATCH"}}, "audit": {...}}

    FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W5、Opus L2所見BLOCKER-1
    是正、2026-09-29): 旧仕様は技術retry(1回)後もQA NGが残る場合、
    "NG_ACCEPTED_AFTER_RETRY"という「採用」ステータスにして呼び出し側
    (runner)がそのままTTSへ渡していた。この挙動は「安全≠成功」原則・
    他工程(deviation MAJOR→retry1回→なおMAJORならSTOP)と非整合だった
    ため廃止する。技術retry後もQA NGが残るrankは"NG"のまま返す(採用は
    しない)。呼び出し側(runner._generate_key_phrase_segments_b1)は
    status!="OK"のrankをTTS呼び出し前にfail-closed(STOPPED)する。

    技術retry方針(既存踏襲、合計最大1回): (1)schema/parse失敗、または
    (2)QA(語数・新規Fact混入)不合格が1件でもある場合、バッチ全体を1回だけ
    再生成する。既にparse失敗でretryを使い切っている場合はQA起因の
    追加retryはしない(合計技術retry上限1回を厳守)。"""
    model = routing.require_model(MODEL_ROUTING_PROCESS, MODEL)
    if call_fn is None:
        if client is None:
            import er003_v1_b1_scaffold_01_generate as b1s
            client = b1s.get_client()
        # N-7是正: schemaのminItems/maxItemsを実際のitems件数から算出する
        # (5固定廃止)。
        call_fn = _default_call_fn_factory(client, model, _build_explanation_json_schema(len(items)))

    user_message = build_explanation_user_message(items)
    calls_log = []

    def attempt():
        parsed, response_model, usage, response_id = call_fn(user_message)
        call_record = {"response_model": response_model, "usage": usage, "response_id": response_id}
        if response_model != model:
            call_record["model_contract_violation"] = True
            calls_log.append(call_record)
            raise ExplanationGenerationError(
                f"応答モデルが不一致です(期待: {model}, 実際: {response_model})。"
                "fallbackせずSTOPします(ER-006-MODEL-ROUTING-CONTRACT-01)。")
        try:
            cost_jpy = pricing.cost_jpy_for_call(
                "openai", response_model, usage.get("input_tokens"),
                usage.get("cached_input_tokens"), usage.get("output_tokens"))
            call_record["cost_jpy"] = cost_jpy
        except pricing.UnknownModelPricingError:
            call_record["cost_jpy"] = None
        calls_log.append(call_record)
        if not parsed or "explanations" not in parsed or len(parsed["explanations"]) != len(items):
            return None
        return {row["phrase"]: row["english_explanation"] for row in parsed["explanations"]}

    by_phrase = attempt()
    retried_for_parse = False
    if by_phrase is None:
        retried_for_parse = True
        by_phrase = attempt()
        if by_phrase is None:
            raise ExplanationGenerationError(
                "explanation生成が2回(初回+技術retry1回)ともschema/parseに"
                "失敗しました。")

    def _evaluate(by_phrase_map: dict) -> dict:
        out = {}
        for it in items:
            phrase = it["display_phrase"]
            explanation = by_phrase_map.get(phrase)
            if explanation is None:
                out[it["rank"]] = {"english_explanation": None, "qa": None,
                                    "status": "NG_PHRASE_MISMATCH"}
                continue
            qa = validate_explanation_qa(explanation, phrase, it["source_sentence"])
            out[it["rank"]] = {"english_explanation": explanation, "qa": qa,
                                "status": "OK" if qa["passed"] else "NG"}
        return out

    results = _evaluate(by_phrase)
    qa_failed = any(v["status"] != "OK" for v in results.values())

    retried_for_qa = False
    if qa_failed and not retried_for_parse:
        retried_for_qa = True
        by_phrase_retry = attempt()
        if by_phrase_retry is not None:
            retried_results = _evaluate(by_phrase_retry)
            for rank, row in retried_results.items():
                if row["status"] == "OK":
                    results[rank] = row
                elif results[rank]["status"] != "OK":
                    # W5(Opus L2所見BLOCKER-1是正): 技術retry後もQA NGが
                    # 残る場合、"NG_ACCEPTED_AFTER_RETRY"という採用ステータス
                    # は使わず、retry後の実際のstatus("NG"または
                    # "NG_PHRASE_MISMATCH")をそのまま記録する(fail-closed、
                    # 呼び出し側でTTSを呼ばずSTOPPEDにする)。
                    results[rank] = row

    audit = {
        "management_id": MANAGEMENT_ID,
        "source_trial_management_id": SOURCE_TRIAL_MANAGEMENT_ID,
        "model": model, "prompt_sha256": PROMPT_SHA256, "max_words": MAX_WORDS,
        "calls": calls_log, "retried_for_parse": retried_for_parse, "retried_for_qa": retried_for_qa,
    }
    return {"items": results, "audit": audit}
