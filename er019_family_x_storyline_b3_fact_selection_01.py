# ============================================================
# er019_family_x_storyline_b3_fact_selection_01.py
# NEWS-FAMILY-X-B3-FACT-SELECTION-PRODUCTION-WIRING-01
# ============================================================
# 目的: Full Fact Ledger(Verified Fact Ledger)を入力に、LLM 1 callで
#   (1) 記事として一本化しやすい中心Storylineを1つ決定
#   (2) Storylineを1行で明示
#   (3) 全FactへB3の4テストを適用
#   (4) 採用/除外を決定
#   (5) 必要最小Factだけを「Selected Fact Brief」として出力
# する、Production正式module(ユーザー確定事項2026-09-26、B3は
# APPROVED_FOR_PRODUCTION)。
#
# B3の4テスト定義(ユーザー確定事項5、逐語)はFACT_TEST_DEFINITIONS_JAへ
# そのまま反映する。Trial(er015_family_x_writer_fact_selection_trial_02.py)
# のFACT_TESTS辞書はSonnetが手動判定したハードコードでありPromptとして
# 再利用できないため、本moduleではLLM 1 callによる自動判定として新規実装
# する(Trial artifactへの参照は行わない)。
#
# 技術retry方針: API呼び出し失敗・JSON不正・Fact ID不整合(Full Ledgerに
# 存在しないfact_idを返す等)は1回だけ同一入力で再試行し、なお失敗する
# 場合はSTOPする(既存Production方針[vfl01.run_writer_with_technical_retry
# 等]と同じ「技術retryのみ、内容の善し悪しでは再試行しない」思想に揃える。
# 新しいGate/Human Reviewは追加しない)。
# ============================================================
from __future__ import annotations

import hashlib
import json
import re
import time

import er005_cost_logger as cl

THEME_TAG = "NEWS_FAMILY_X_B3_FACT_SELECTION_PRODUCTION_01"

# ユーザー確定事項5の逐語(変更禁止)。
FACT_TEST_DEFINITIONS_JA = """\
Test1: そのFactを削除しても中心Storylineを理解できるか。YESなら原則除外。
Test2: そのFactは他Factとの因果関係に実際に使われるか。NOなら原則除外。
Test3: そのFactがないとStoryline上重要な「なぜ?」が説明できなくなるか。NOなら原則除外。
Test4: そのFactを残した理由が「面白い/具体的/数字がある/珍しい/補足として便利」だけではないか。YESなら原則除外。"""

DEVELOPER_MESSAGE = (
    "あなたはNews記事のFact選定を行うEditorです。Full Fact Ledgerの中から"
    "記事として一本化しやすい中心Storylineを1つ決定し、そのStorylineに"
    "本当に必要な最小限のFactだけを選び出してください。記事本文そのものは"
    "書きません。"
)

USER_PROMPT_TEMPLATE = """以下は、あるテーマについてWeb調査で収集し独立検証済みのFull Fact Ledgerです。

【テーマ】
{topic}

【Full Fact Ledger】
{ledger_text}

あなたの仕事は次の5つです。

1. このFull Ledgerの中から、記事として一本化しやすい中心Storyline(のちの記事が伝える「何が起きて、なぜそうなったか」という一続きの筋)を1つ決定してください。
2. 決定したStorylineを1行の日本語で明示してください(これが後工程でWriterへ渡すテーマ文としてそのまま使われます)。
3. Full Ledgerの全fact_idそれぞれについて、以下4つのテストを適用してください。

{fact_test_definitions}

4. 各Factについて、4テストの回答を踏まえてselected(採用)/excluded(除外)を決定し、理由(reason)を記載してください。判定に迷うFactについては、迷った理由も含めてreasonへ記載して構いません。
5. 採用したFactだけを使って、Writerへそのまま渡す「Selected Fact Brief」(必要最小限のFactを簡潔にまとめた文章。冒頭にStorylineの1行を含める)を作成してください。Selected Fact Briefは記事本文そのものではなく、Writerへの素材です。

【採用Fact数についての注意】
目安は3〜5件です。Hard ruleではありませんが、6件以上採用する場合は、本当にそれら全てが中心Storylineの理解に必要かをもう一度自問し、recheck_noteフィールドへその検討内容を明記してください(3件未満でも、Storylineが単独で成立するなら構いません)。5件以下の場合、recheck_noteはnullにしてください。

【出力】
JSON schemaの指示に従い、以下を出力してください:
- selected_storyline: 決定したStorylineの1行
- fact_tests: Full Ledgerの全fact_idについて、test1_answer/test2_answer/test3_answer/test4_answer(いずれも"YES"か"NO")・reason・decision("selected"か"excluded")
- selected_fact_ids: 採用したfact_idのリスト(fact_testsでdecision="selected"のものと一致させること)
- selected_fact_brief: Writerへ渡すSelected Fact Brief本文(Storylineの1行を含む)
- recheck_note: 採用Fact数が6件以上の場合のみ記入。5件以下の場合はnull。

【重要】fact_idは、上記Full Ledgerに実在するfact_idのみを使用してください。Ledgerに存在しないfact_idを作り出さないでください。"""

RETRY_APPEND_NOTE = (
    "\n\n【前回出力の修正指示】前回の出力は技術的に無効でした"
    "(JSON不正、またはFull Ledgerに存在しないfact_idを含んでいました)。"
    "Full Ledgerに実在するfact_idのみを使い、指定のJSON schemaに厳密に従って"
    "再出力してください。"
)

STORYLINE_B3_JSON_SCHEMA = {
    "name": "storyline_b3_fact_selection",
    "schema": {
        "type": "object",
        "properties": {
            "selected_storyline": {"type": "string"},
            "fact_tests": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "fact_id": {"type": "string"},
                        "test1_answer": {"type": "string", "enum": ["YES", "NO"]},
                        "test2_answer": {"type": "string", "enum": ["YES", "NO"]},
                        "test3_answer": {"type": "string", "enum": ["YES", "NO"]},
                        "test4_answer": {"type": "string", "enum": ["YES", "NO"]},
                        "decision": {"type": "string", "enum": ["selected", "excluded"]},
                        "reason": {"type": "string"},
                    },
                    "required": [
                        "fact_id", "test1_answer", "test2_answer", "test3_answer",
                        "test4_answer", "decision", "reason",
                    ],
                    "additionalProperties": False,
                },
            },
            "selected_fact_ids": {"type": "array", "items": {"type": "string"}},
            "selected_fact_brief": {"type": "string"},
            "recheck_note": {"type": ["string", "null"]},
        },
        "required": [
            "selected_storyline", "fact_tests", "selected_fact_ids",
            "selected_fact_brief", "recheck_note",
        ],
        "additionalProperties": False,
    },
    "strict": True,
}

FACT_ID_LINE_RE = re.compile(r"^\[(?:VERIFIED|AMBIGUOUS[^\]]*)\]\s+([A-Za-z0-9_\-]+):", re.MULTILINE)


def sha256_text(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def prompt_shas() -> dict:
    return {
        "developer_message_sha256": sha256_text(DEVELOPER_MESSAGE),
        "user_prompt_template_sha256": sha256_text(USER_PROMPT_TEMPLATE),
        "fact_test_definitions_sha256": sha256_text(FACT_TEST_DEFINITIONS_JA),
    }


def extract_fact_ids_from_ledger(ledger_text: str) -> list:
    return sorted(set(FACT_ID_LINE_RE.findall(ledger_text or "")))


def build_user_prompt(topic: str, ledger_text: str) -> str:
    return USER_PROMPT_TEMPLATE.format(
        topic=topic, ledger_text=ledger_text,
        fact_test_definitions=FACT_TEST_DEFINITIONS_JA,
    )


def validate_selection_output(parsed: dict, ledger_fact_ids: list) -> list:
    """技術的整合性エラーのリストを返す(空リスト=技術的に有効)。
    内容の善し悪し(Storylineが面白いか等)は判定しない。"""
    errors = []
    ledger_ids_set = set(ledger_fact_ids)
    fact_tests = parsed.get("fact_tests") or []
    tested_ids = [ft.get("fact_id") for ft in fact_tests]
    unknown_ids = [fid for fid in tested_ids if fid not in ledger_ids_set]
    if unknown_ids:
        errors.append(f"UNKNOWN_FACT_ID_IN_FACT_TESTS: {unknown_ids}")
    missing_ids = [fid for fid in ledger_fact_ids if fid not in tested_ids]
    if missing_ids:
        errors.append(f"LEDGER_FACT_ID_NOT_TESTED: {missing_ids}")
    selected_ids = parsed.get("selected_fact_ids") or []
    unknown_selected = [fid for fid in selected_ids if fid not in ledger_ids_set]
    if unknown_selected:
        errors.append(f"UNKNOWN_FACT_ID_IN_SELECTED: {unknown_selected}")
    decision_selected = {ft["fact_id"] for ft in fact_tests if ft.get("decision") == "selected"}
    if set(selected_ids) != decision_selected:
        errors.append(
            f"SELECTED_FACT_IDS_MISMATCH: selected_fact_ids={sorted(selected_ids)} "
            f"vs fact_tests(decision=selected)={sorted(decision_selected)}"
        )
    if not (parsed.get("selected_storyline") or "").strip():
        errors.append("EMPTY_SELECTED_STORYLINE")
    if not (parsed.get("selected_fact_brief") or "").strip():
        errors.append("EMPTY_SELECTED_FACT_BRIEF")
    if len(selected_ids) >= 6 and not (parsed.get("recheck_note") or "").strip():
        errors.append("RECHECK_NOTE_MISSING_FOR_6_OR_MORE_SELECTED")
    return errors


def _call_once(client, topic: str, ledger_text: str, model: str, effort: str,
                stage_tag: str, extra_note: str = "") -> dict:
    user_prompt = build_user_prompt(topic, ledger_text) + extra_note
    t0 = time.time()
    with cl.logging_context(THEME_TAG, stage_tag):
        response = client.responses.create(
            model=model,
            reasoning={"effort": effort},
            text={"format": {"type": "json_schema", **STORYLINE_B3_JSON_SCHEMA}},
            input=[
                {"role": "developer", "content": DEVELOPER_MESSAGE},
                {"role": "user", "content": user_prompt},
            ],
        )
    latency = time.time() - t0
    parsed = json.loads(response.output_text)
    return {
        "user_prompt": user_prompt, "raw_text": response.output_text, "parsed": parsed,
        "model": response.model, "response_id": response.id, "latency_seconds": latency,
    }


def run_storyline_b3_selection(client, topic: str, ledger_text: str,
                                model: str, effort: str) -> dict:
    """戻り値: {"parsed", "model", "response_id", "latency_seconds",
    "attempts", "retried", "validation_errors_by_attempt", "prompt_shas"}
    技術的に2回とも失敗した場合はRuntimeErrorをSTOPとして送出する。"""
    ledger_fact_ids = extract_fact_ids_from_ledger(ledger_text)
    attempts_log = []
    last_exc = None
    for attempt in (1, 2):
        extra_note = "" if attempt == 1 else RETRY_APPEND_NOTE
        try:
            result = _call_once(client, topic, ledger_text, model, effort,
                                 stage_tag="storyline_b3", extra_note=extra_note)
        except (json.JSONDecodeError, Exception) as exc:  # noqa: BLE001
            attempts_log.append({"attempt": attempt, "error": str(exc)[:500]})
            last_exc = exc
            continue
        errors = validate_selection_output(result["parsed"], ledger_fact_ids)
        # RECHECK_NOTE_MISSING_FOR_6_OR_MORE_SELECTEDはsoft warning(内容面の
        # 注意喚起であり、technical retryの対象にはしない)。
        hard_errors = [e for e in errors if not e.startswith("RECHECK_NOTE_MISSING")]
        attempts_log.append({"attempt": attempt, "validation_errors": errors})
        if not hard_errors:
            return {
                "parsed": result["parsed"], "model": result["model"],
                "response_id": result["response_id"],
                "latency_seconds": result["latency_seconds"],
                "attempts": attempt, "retried": attempt > 1,
                "soft_warnings": errors,
                "ledger_fact_ids": ledger_fact_ids,
                "attempts_log": attempts_log,
                "prompt_shas": prompt_shas(),
            }
    raise RuntimeError(
        "[STOP] Storyline+B3 Fact Selection: 2回試行しても技術的に有効な出力を得られませんでした。"
        f" attempts_log={attempts_log} last_exc={last_exc}"
    )


def build_full_ledger_record(topic: str, ledger_text: str, ledger_fact_ids: list) -> dict:
    return {"topic": topic, "ledger_text": ledger_text, "fact_ids": ledger_fact_ids}


def build_selected_brief_markdown(selection_result: dict) -> str:
    """NEWS-FAMILY-X-B3-FACT-SELECTION-PRODUCTION-WIRING-01(Fable差し戻し1回目、
    Gate 3 #2バグ修正): Prompt指示5「(採用したFactだけを使って)Selected Fact
    Briefを作成してください...冒頭にStorylineの1行を含める」に従い、LLMが返す
    selected_fact_brief自体の先頭にStoryline文をそのまま含めてくることがある
    (実測: run_01で完全一致で確認)。本関数は別途「## Storyline」見出しで
    Storylineを1回だけ明示するため、selected_fact_briefの先頭がStoryline文と
    完全一致する場合はその重複部分を取り除く(LLMが言い換えて完全一致しない
    場合は元のテキストをそのまま使い、憶測で改変しない)。"""
    parsed = selection_result["parsed"]
    storyline = parsed["selected_storyline"]
    fact_brief = parsed["selected_fact_brief"]

    fact_brief_dedup = fact_brief
    if fact_brief.startswith(storyline):
        fact_brief_dedup = fact_brief[len(storyline):].lstrip("\n")

    lines = [
        f"# Selected Fact Brief",
        "",
        f"## Storyline",
        storyline,
        "",
        "## Selected Facts",
        fact_brief_dedup,
    ]
    return "\n".join(lines) + "\n"
