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
# FAMILY-X-B3-FACT-MIN2-PRODUCTION-01(M3): VERIFIED判定はproducerと同一のparse_ledger(ambiguousフラグ)を使う(定義を1つに統一)。
from er053_b3_deterministic_producer_01 import parse_ledger as _producer_parse_ledger

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
`[VERIFIED]`のFactから最低2件を採用してください(`[AMBIGUOUS]`のFactは採用してもかまいませんが、最低2件には数えません)。数合わせのための関連性の低いFactの追加は不可です。6件以上採用する場合は、本当にそれら全てが中心Storylineの理解に必要かをもう一度自問し、recheck_noteフィールドへその検討内容を明記してください。5件以下の場合、recheck_noteはnullにしてください。

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

# FAMILY-X-B3-FACT-MIN2-PRODUCTION-01(2026-10-19ユーザー正式決定、Opusレビュー_F M1): 採用FactのうちVERIFIEDが
# 下限未満のときだけ1回行う再評価callの追記note(テンプレート。sha固定)。4テスト定義・DEVELOPER_MESSAGE・JSON schemaは不変。
MIN_VERIFIED_SELECTED_DEFAULT = 2
REEVAL_APPEND_NOTE_TEMPLATE = (
    "\n\n【再評価の指示】初回の選定では、採用Factのうち`[VERIFIED]`のFactが最低2件に届きませんでした"
    "(初回は検証済みFactが1件以下でした)。以下の方針でやり直してください。"
    "\n1. 上記【テーマ】の範囲内で、中心Storylineを見直してかまいません。ただし【テーマ】から外れるStorylineは不可です。"
    "\n2. 4つのテストは、見直したStorylineに対して全Factへ改めて適用してください。採用/除外の判定は、テストの回答と整合させてください"
    "(テストの回答を変えずに採用判定だけを変えることは禁止です)。"
    "\n3. 数合わせのために、関連性の低いFactや`[AMBIGUOUS]`のFactを検証済みとして扱ってはいけません。"
    "最低2件に届かない場合は、各Factのreasonにその理由を書いてください。"
    "\n4. 初回のStorylineと採用Factは参考情報です(初回のreasonは引き継がず、改めて判断してください)。"
    "\n   初回のStoryline: {first_storyline}"
    "\n   初回の採用fact_id: {first_selected_ids}"
)


class B3MinFactsStop(RuntimeError):
    """採用Fact下限(VERIFIEDのみ算入)未達のSTOP。`record`にb3_min2_stop_record.json用dictを持つ
    (reason: LEDGER_VERIFIED_LT2 / REEVAL_STILL_LT2 / REEVAL_INVALID / SELECTED_VERIFIED_LT2_AT_RUNNER_GUARD)。"""

    def __init__(self, message: str, record: dict | None = None):
        super().__init__(message)
        self.record = record or {}


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


def verified_fact_ids(ledger_text: str) -> list:
    """Ledger内の`[VERIFIED]`のfact_id(producerのparse_ledgerのambiguous=Falseと同一定義)。"""
    facts, order = _producer_parse_ledger(ledger_text or "")
    return [fid for fid in order if not facts[fid]["ambiguous"]]


def count_selected_verified(selected_ids, ledger_text: str) -> int:
    """採用IDのうち`[VERIFIED]`の件数(下限2件の算定式。b3 moduleとrunnerガードで共有)。"""
    verified = set(verified_fact_ids(ledger_text))
    return len({fid for fid in (selected_ids or []) if fid in verified})


def reeval_note_sha() -> str:
    return sha256_text(REEVAL_APPEND_NOTE_TEMPLATE)


def build_reeval_note(first_parsed: dict) -> str:
    return REEVAL_APPEND_NOTE_TEMPLATE.format(
        first_storyline=(first_parsed.get("selected_storyline") or "").strip(),
        first_selected_ids=", ".join(first_parsed.get("selected_fact_ids") or []) or "(なし)")


def detect_selected_despite_all_tests_exclude(parsed: dict) -> list:
    """4テストの回答がすべて除外側(Test1=YES・Test2=NO・Test3=NO・Test4=YES)なのに採用されたFactのID。
    soft warningとしてevidenceへ記録するのみ(retry/STOP/採用数算定には使わない)。"""
    out = []
    for ft in parsed.get("fact_tests") or []:
        if (ft.get("decision") == "selected" and ft.get("test1_answer") == "YES"
                and ft.get("test2_answer") == "NO" and ft.get("test3_answer") == "NO"
                and ft.get("test4_answer") == "YES"):
            out.append(ft.get("fact_id"))
    return out


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
                stage_tag: str, extra_note: str = "", variant: dict | None = None) -> dict:
    user_prompt = build_user_prompt(topic, ledger_text) + extra_note
    text_kw = {"format": {"type": "json_schema", **STORYLINE_B3_JSON_SCHEMA}}
    if variant is not None:
        # FX-CORE-NUMERIC-RETENTION-TRIAL-01 委任_07(APPROVED_FOR_PRODUCTION 2026-10-25): Family Xのnews runnerだけが渡す
        # v4 variant(er116.variant())。user message末尾へ指示文を追記し、schemaは**deepcopyへ**欄を足す(STORYLINE_B3_JSON_SCHEMA定数は不変=
        # Y Trial等のimport契約を変えない)。variant=None(既定)は従来とバイト同一。
        user_prompt = user_prompt + variant["addendum"]
        text_kw = variant["text_transform"](text_kw)
    t0 = time.time()
    with cl.logging_context(THEME_TAG, stage_tag):
        response = client.responses.create(
            model=model,
            reasoning={"effort": effort},
            text=text_kw,
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


def _stop_record(reason: str, ledger_text: str, parsed: dict | None, extra: dict | None = None) -> dict:
    rec = {
        "reason": reason, "floor": MIN_VERIFIED_SELECTED_DEFAULT, "counted": "VERIFIED",
        "ledger_verified_fact_ids": verified_fact_ids(ledger_text),
        "selected_fact_ids": list((parsed or {}).get("selected_fact_ids") or []),
        "selected_verified_n": count_selected_verified((parsed or {}).get("selected_fact_ids"), ledger_text),
        "fact_reasons": [{"fact_id": ft.get("fact_id"), "decision": ft.get("decision"), "reason": ft.get("reason")}
                         for ft in ((parsed or {}).get("fact_tests") or [])],
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    if extra:
        rec.update(extra)
    return rec


def _technical_attempts(client, topic: str, ledger_text: str, model: str, effort: str,
                         ledger_fact_ids: list, variant: dict | None = None) -> dict:
    """初回選定(技術retry最大2 attempt、従来どおり)。技術的に2回とも失敗した場合はRuntimeErrorをSTOPとして送出する。"""
    attempts_log = []
    last_exc = None
    for attempt in (1, 2):
        extra_note = "" if attempt == 1 else RETRY_APPEND_NOTE
        try:
            result = _call_once(client, topic, ledger_text, model, effort,
                                 stage_tag="storyline_b3", extra_note=extra_note, variant=variant)
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
            return {"result": result, "attempt": attempt, "errors": errors, "attempts_log": attempts_log}
    raise RuntimeError(
        "[STOP] Storyline+B3 Fact Selection: 2回試行しても技術的に有効な出力を得られませんでした。"
        f" attempts_log={attempts_log} last_exc={last_exc}"
    )


def run_storyline_b3_selection(client, topic: str, ledger_text: str,
                                model: str, effort: str,
                                min_verified_selected: int | None = MIN_VERIFIED_SELECTED_DEFAULT,
                                variant: dict | None = None) -> dict:
    """戻り値: {"parsed", "model", "response_id", "latency_seconds",
    "attempts", "retried", "validation_errors_by_attempt", "prompt_shas", "min2_policy", ...}
    技術的に2回とも失敗した場合はRuntimeErrorをSTOPとして送出する。

    FAMILY-X-B3-FACT-MIN2-PRODUCTION-01: min_verified_selected(既定2、Production既定ON)>0のとき、
    (1) Ledgerの[VERIFIED]が下限未満ならAPI呼出前に B3MinFactsStop(LEDGER_VERIFIED_LT2)、
    (2) 初回選定の採用IDのうち[VERIFIED]が下限未満なら、再評価callを1回だけ行う(技術retry枠とは別。最悪合計3 call)、
    (3) 再評価の出力が技術的に不正(REEVAL_INVALID)、または再評価後も下限未満(REEVAL_STILL_LT2)なら B3MinFactsStop、
    (4) 再評価で下限を満たしたら、Storyline/fact_tests/採用ID/Briefの全てを再評価call出力1回分で置換する(初回と混ぜない)。
    コードはFactを選ばない(補完・追加なし)。Noneまたは0を渡すと下限強制なし(旧挙動。Trial側の明示用)。"""
    ledger_fact_ids = extract_fact_ids_from_ledger(ledger_text)
    floor = int(min_verified_selected or 0)
    if floor > 0 and len(verified_fact_ids(ledger_text)) < floor:
        raise B3MinFactsStop(
            f"[STOP] B3採用Fact下限: Ledgerの[VERIFIED]が{floor}件未満のためAPI呼出前に停止しました"
            f"(verified={verified_fact_ids(ledger_text)})。",
            _stop_record("LEDGER_VERIFIED_LT2", ledger_text, None))

    first = _technical_attempts(client, topic, ledger_text, model, effort, ledger_fact_ids, variant=variant)
    result, attempt = first["result"], first["attempt"]
    attempts_log = list(first["attempts_log"])
    errors = first["errors"]
    first_parsed = result["parsed"]
    first_verified_n = count_selected_verified(first_parsed.get("selected_fact_ids"), ledger_text)
    min2_policy = {
        "floor": floor, "counted": "VERIFIED", "enforced": floor > 0,
        "first_pass_selected_ids": list(first_parsed.get("selected_fact_ids") or []),
        "first_pass_verified_n": first_verified_n, "reevaluated": False,
        "reeval_note_sha256": reeval_note_sha(),
    }
    final = result
    if floor > 0 and first_verified_n < floor:
        min2_policy["reevaluated"] = True
        min2_policy["first_attempt"] = {   # 参考情報のみ(採用判定には使わない)
            "selected_storyline": first_parsed.get("selected_storyline"),
            "selected_fact_ids": list(first_parsed.get("selected_fact_ids") or []),
            "response_id": result.get("response_id")}
        try:
            re_result = _call_once(client, topic, ledger_text, model, effort, stage_tag="storyline_b3",
                                    extra_note=build_reeval_note(first_parsed), variant=variant)
        except (json.JSONDecodeError, Exception) as exc:  # noqa: BLE001
            attempts_log.append({"attempt": "reeval", "error": str(exc)[:500]})
            raise B3MinFactsStop(
                f"[STOP] B3採用Fact下限: 再評価callが技術的に失敗しました: {str(exc)[:200]}",
                _stop_record("REEVAL_INVALID", ledger_text, first_parsed, {"reeval_error": str(exc)[:500]})) from exc
        re_errors = validate_selection_output(re_result["parsed"], ledger_fact_ids)
        re_hard = [e for e in re_errors if not e.startswith("RECHECK_NOTE_MISSING")]
        attempts_log.append({"attempt": "reeval", "validation_errors": re_errors})
        if re_hard:
            raise B3MinFactsStop(
                f"[STOP] B3採用Fact下限: 再評価の出力が技術的に不正でした: {re_hard}",
                _stop_record("REEVAL_INVALID", ledger_text, re_result["parsed"], {"reeval_validation_errors": re_hard}))
        re_verified_n = count_selected_verified(re_result["parsed"].get("selected_fact_ids"), ledger_text)
        min2_policy["reeval_verified_n"] = re_verified_n
        if re_verified_n < floor:
            raise B3MinFactsStop(
                f"[STOP] B3採用Fact下限: 再評価後も採用IDのうち[VERIFIED]が{floor}件未満です(n={re_verified_n})。",
                _stop_record("REEVAL_STILL_LT2", ledger_text, re_result["parsed"],
                             {"first_pass_selected_ids": min2_policy["first_pass_selected_ids"]}))
        final, errors = re_result, re_errors      # M4: 再評価call出力1回分で全置換
    min2_policy["final_selected_ids"] = list(final["parsed"].get("selected_fact_ids") or [])
    min2_policy["final_verified_n"] = count_selected_verified(final["parsed"].get("selected_fact_ids"), ledger_text)
    soft = list(errors)
    despite = detect_selected_despite_all_tests_exclude(final["parsed"])
    if despite:
        soft.append(f"SELECTED_DESPITE_ALL_TESTS_EXCLUDE: {despite}")
    return {
        "parsed": final["parsed"], "model": final["model"],
        "response_id": final["response_id"],
        "latency_seconds": final["latency_seconds"],
        "attempts": attempt, "retried": attempt > 1,
        "soft_warnings": soft,
        "ledger_fact_ids": ledger_fact_ids,
        "attempts_log": attempts_log,
        "prompt_shas": prompt_shas(),
        "min2_policy": min2_policy,
    }


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
