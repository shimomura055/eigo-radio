# ============================================================
# er019_family_x_ja_writer_o_r1_r2_01.py
# NEWS-FAMILY-X-B3-FACT-SELECTION-PRODUCTION-WIRING-01
# ============================================================
# 目的: 日本語Entertainment Writer(Original→R1→R2、P7、既承認
# `APPROVED_FOR_PRODUCTION / WIRING INCOMPLETE`、CURRENT_SPEC.md L828)を
# Production正式pathへ配線する。P7 Prompt本文・Developer message・
# Revision指示文(r1/r2)は、
# er015_news_original_baseline_repro_01.R0_PROMPT/DEVELOPER_MESSAGEおよび
# er015_news_iterative_entertainment_trial_01.REVISION_INSTRUCTIONS["r1"/"r2"]
# から**逐語**で移設したものであり、一字一句変更していない(sha256は
# er019_family_x_ja_writer_o_r1_r2_01_test_01.pyでTrialの値と比較検証する)。
# Revision方式(Original)自体・語数目安・出力形式は変更しない。
#
# Trial(er015_news_iterative_entertainment_trial_02.py)との違いは入力素材
# のみ: Trialは「Sonnetが手動で書いた2〜3文の中立素材」だったが、本moduleは
# B3(er019_family_x_storyline_b3_fact_selection_01.py)が生成した
# Selected Fact Briefをそのまま[ニュース]欄へ渡す。「テーマ：」行は
# B3が決定したselected_storyline(1行)へ差し替える。
#
# 連鎖方式(trial01/02と同一): previous_response_idで直前応答に連鎖させ、
# userメッセージとして修正指示文のみを送る。previous_response_idが使えない
# 場合のみ、直前記事全文を貼るフォールバック方式に切り替える。
#
# 本moduleはOriginal→R1→R2で停止する(R3は生成しない、正式フローの
# 「Original→R1→R2」に一致させる)。
#
# NEWS-FAMILY-X-JA-FACT-CHECK-PRODUCTION-WIRING-01(Stage 1、2026-09-27、
# ユーザー正式決定によりAPPROVED_FOR_PRODUCTION)で追加: full_ledger_text
# (Full Ledger、Storyline+B3が参照した検証済み事実全量)が渡された場合、
# Original直後・R2直後にvfl01.run_deviation_check()でJA記事自体をFull
# Ledgerへ照合するFact Checkを行う。MAJORなら「以下の指摘を必ず解消する」
# must-fixブロック付きで1回だけ再生成し、再Checkでもなお解消しなければ
# JAFactCheckStopErrorを送出してSTOPする(本文を手で直さない、既存
# run_writer_stage[er012]のSTOP方針と同じ設計)。full_ledger_textが
# Noneの場合(既存/他呼び出し元)は一切のFact Check処理を行わず、従来の
# Original→R1→R2のみの挙動と完全に同じ(後方互換)。
# ============================================================
from __future__ import annotations

import hashlib

import er003_audio_tts_asr_safety as safety
import er005_cost_logger as cl
import er003_v1_en_direct_vfl_01_generate as vfl01

THEME_TAG = "NEWS_FAMILY_X_B3_JA_WRITER_PRODUCTION_01"
WRITER_MODEL = vfl01.MODEL              # "gpt-5.6-luna" (= routing.WRITER_MODEL)
WRITER_EFFORT = vfl01.REASONING_EFFORT  # "high"

# er015_news_original_baseline_repro_01.R0_PROMPTの逐語コピー(一字一句同一)。
R0_PROMPT = """以下のニュースを、友人に「これ、ちょっと面白くない？」と話すような読み物にしてください。

ニュースの中から、最も意外な事実ではなく、最も面白い「見方」を一つ選んでください。その見方に必要な事実だけを使い、ニュース全体を説明しようとしないでください。

語り口は自然で軽快にします。新聞、行政資料、学校教材のような文章にはしません。難しい内容は、短く簡単な日本語に言い換えてください。日本語を勉強している外国人が、音声で一度聞いて理解できる程度を目安にします。

遠い地域だけの特殊な話に見える場合は、読者の暮らしや、より大きな社会の変化とのつながりを一度だけ示してください。ただし、話を無理に広げる必要はありません。

事実関係は厳守し、架空の出来事や発言は加えません。

テーマ：老朽化する下水道をめぐり、一部自治体が合併浄化槽への切り替えを検討

長さ：800～1000字

出力はタイトルと本文のみ。"""

# er015_news_original_baseline_repro_01.DEVELOPER_MESSAGEの逐語コピー。
DEVELOPER_MESSAGE = "あなたは日本語のニュースを分かりやすく面白く伝える書き手です。"

# er015_news_iterative_entertainment_trial_01.REVISION_INSTRUCTIONS["r1"/"r2"]
# の逐語コピー(r3は本moduleでは使わない、正式フローはOriginal→R1→R2まで)。
REVISION_INSTRUCTIONS = {
    "r1": "この記事を、事実関係は変えずに、もっとエンターテインメント性の高い記事に修正してください。",
    "r2": "この記事を、事実関係は変えずに、さらにもっとエンターテインメント性の高い記事に修正してください。",
}

# TTS-SYMBOL-NORMALIZATION-ALL-FAMILY-PRODUCTION-WIRING-01(Layer 1、
# 2026-09-27): R0_PROMPT/DEVELOPER_MESSAGE/REVISION_INSTRUCTIONSは
# Trialからの逐語コピー(verbatim_shas()で監査)であり、文言自体は変更
# しない。この予防ブロックは、build_original_prompt()・r1/r2
# instructionの組み立て時に別途追記する(既存の逐語コピーは無変更)。
SYMBOL_PREVENTION_BLOCK_JA = (
    "\n\n【音声化できない記号の禁止】\nこの記事は音声(TTS)で読み上げられます。"
    "タイトル・本文で以下の記号を使用しないでください:\n"
    "- 波ダッシュ「〜」「～」は、具体的な内容を省略した言い換えとして使わないでください。"
    "書くべき内容を実際に書いてください。\n"
    "- 三点リーダー「…」「……」は使わないでください。間を置きたい場合は句点・読点で表現してください。\n"
    "- スラッシュ「/」は使わないでください。「と」「または」で書いてください。\n"
    "- 括弧「()」「（）」「[]」は使わないでください(鉤括弧「」は対象外です)。\n"
    "- コロン「:」「：」・セミコロン「;」「；」は使わないでください。\n"
    "- URLやメールアドレスは書かないでください。絵文字も使わないでください。"
)


def sha256_text(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def verbatim_shas() -> dict:
    return {
        "r0_prompt_sha256": sha256_text(R0_PROMPT),
        "developer_message_sha256": sha256_text(DEVELOPER_MESSAGE),
        "r1_instruction_sha256": sha256_text(REVISION_INSTRUCTIONS["r1"]),
        "r2_instruction_sha256": sha256_text(REVISION_INSTRUCTIONS["r2"]),
    }


def build_must_fix_block(must_fix: list, full_ledger_text: str) -> str:
    """NEWS-FAMILY-X-JA-FACT-CHECK-PRODUCTION-WIRING-01: 「以下の指摘を
    必ず解消する(Ledger原文を提示し、それに整合させる)」ブロック。
    Fact ID/claim_in_article/issue/explanationを渡す。"""
    lines = [
        "【必ず解消すべき指摘(Fact Check MAJOR)】",
        "以下の指摘を必ず解消してください。指摘に対応する記述は、下記の"
        "Full Ledger原文に厳密に整合させてください(Ledgerにない断定・"
        "因果・数値・主体・時期・比較・否定・一般化を残さないこと)。",
    ]
    for i, item in enumerate(must_fix or [], start=1):
        lines.append(
            f"{i}. Fact ID: {item.get('fact_id') or '(不明)'} / "
            f"該当箇所: {item.get('claim_in_article', '')} / "
            f"指摘: {item.get('issue', '')} / "
            f"理由: {item.get('explanation', '')}"
        )
    lines.append("")
    lines.append("【Full Ledger原文(再掲)】")
    lines.append(full_ledger_text or "")
    return "\n".join(lines)


def build_original_prompt(storyline_line: str, selected_fact_brief_text: str,
                           must_fix: list | None = None, full_ledger_text: str | None = None) -> str:
    """trial_02.build_prompt()と同一構造(「テーマ：」行を差し替え、
    末尾に[ニュース]欄を追加)。素材はSelected Fact Brief全文。

    must_fix/full_ledger_text(NEWS-FAMILY-X-JA-FACT-CHECK-PRODUCTION-
    WIRING-01で追加、既定None)は、JA Original Fact CheckでMAJORだった
    場合のmust-fix Rewriteでのみ指定する。既存呼び出し(省略)の挙動は
    一切変わらない。"""
    lines = R0_PROMPT.split("\n")
    new_lines = [f"テーマ：{storyline_line}" if line.startswith("テーマ：") else line
                 for line in lines]
    prompt = "\n".join(new_lines)
    prompt += "\n\n[ニュース]\n" + selected_fact_brief_text
    prompt += SYMBOL_PREVENTION_BLOCK_JA
    if must_fix:
        prompt += "\n\n" + build_must_fix_block(must_fix, full_ledger_text or "")
    return prompt


class JAFactCheckStopError(RuntimeError):
    """NEWS-FAMILY-X-JA-FACT-CHECK-PRODUCTION-WIRING-01: JA Original/R2の
    Fact CheckでMAJORが解消されなかった場合のSTOP(本文を手で直さない)。
    呼び出し側(runner)がrejected_ja_<stage>.mdとaudit/deviation_checksを
    保存できるよう、必要な情報を属性として保持する。"""

    def __init__(self, stage: str, message: str, rejected_text: str,
                 checks: list, must_fix_used: list):
        super().__init__(message)
        self.stage = stage
        self.rejected_text = rejected_text
        self.checks = checks
        self.must_fix_used = must_fix_used


def _major_deviations(check_result: dict) -> list:
    return [d for d in check_result["parsed"].get("deviations", []) if d.get("severity") == "MAJOR"]


def _must_fix_from_deviations(major_devs: list) -> list:
    return [
        {
            "fact_id": d.get("related_fact_id", ""),
            "claim_in_article": d.get("claim_in_article", ""),
            "issue": d.get("issue", ""),
            "explanation": d.get("explanation", ""),
        }
        for d in major_devs
    ]


def _extract_title(article_text: str) -> str:
    for line in article_text.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    lines = [l for l in article_text.splitlines() if l.strip()]
    return lines[0].strip() if lines else ""


def call_fresh(client, developer: str, user: str, effort: str, stage: str):
    kwargs = dict(
        model=WRITER_MODEL,
        reasoning={"effort": effort},
        input=[
            {"role": "developer", "content": developer},
            {"role": "user", "content": user},
        ],
    )
    with cl.logging_context(THEME_TAG, stage):
        response = client.responses.create(**kwargs)
    return response


def call_with_previous_response_id(client, user: str, effort: str, previous_response_id: str, stage: str):
    kwargs = dict(
        model=WRITER_MODEL,
        reasoning={"effort": effort},
        previous_response_id=previous_response_id,
        input=[{"role": "user", "content": user}],
    )
    with cl.logging_context(THEME_TAG, stage):
        response = client.responses.create(**kwargs)
    return response


def run_ja_writer_o_r1_r2(client, storyline_line: str, selected_fact_brief_text: str,
                           full_ledger_text: str | None = None) -> dict:
    """Original -> r1 -> r2をprevious_response_idで連鎖実行する。
    技術的失敗(previous_response_id不可)時のみ、直前記事全文を貼る
    fallback_full_textへ切替える(trial01/02と同一方針)。

    full_ledger_text(NEWS-FAMILY-X-JA-FACT-CHECK-PRODUCTION-WIRING-01で
    追加、既定None)が渡された場合のみ、Original直後・R2直後にFact Check
    (vfl01.run_deviation_check、Full Ledger vs JA記事)を行う。MAJORなら
    must-fix Rewrite 1回→再Check、なおMAJORならJAFactCheckStopErrorを
    送出する(呼び出し側=runnerがrejected_ja_<stage>.md保存等を行い
    STOPする)。Noneの場合はFact Check自体を行わず、従来と完全に同じ
    挙動(後方互換)。
    戻り値: {"stages": {"original": {...}, "r1": {...}, "r2": {...}},
             "final_text": <r2本文>, "chain_method": ...,
             "fact_checks": {"original": {...}, "r2": {...}} (Fact Check
             実行時のみ)}"""
    prompt_original = build_original_prompt(storyline_line, selected_fact_brief_text)
    response = call_fresh(client, DEVELOPER_MESSAGE, prompt_original, WRITER_EFFORT, "ja_original")
    original_text = response.output_text.strip()
    stages = {
        "original": {
            "text": original_text, "response_id": response.id, "model": response.model,
            "prompt": prompt_original, "developer_message": DEVELOPER_MESSAGE,
        }
    }
    fact_checks = {}

    if full_ledger_text is not None:
        with cl.logging_context(THEME_TAG, "ja_original_check"):
            check1 = vfl01.run_deviation_check(client, full_ledger_text, original_text,
                                                hook_aware=False, include_related_fact_id=True)
        checks_log = [check1]
        status1 = check1["parsed"].get("overall_status")
        final_status = status1
        must_fix_applied = False
        must_fix_used = []
        if status1 == "LEDGER_DEVIATION":
            must_fix_applied = True
            major_devs = _major_deviations(check1)
            must_fix_used = _must_fix_from_deviations(major_devs)
            print(f"[JA-WRITER][ja_original] Fact Check MAJOR。must-fixで1回だけ再生成します"
                  f"(major_count={len(major_devs)})...")
            prompt_must_fix = build_original_prompt(
                storyline_line, selected_fact_brief_text,
                must_fix=must_fix_used, full_ledger_text=full_ledger_text)
            response_mf = call_fresh(client, DEVELOPER_MESSAGE, prompt_must_fix, WRITER_EFFORT,
                                      "ja_original_must_fix")
            rewritten_text = response_mf.output_text.strip()
            with cl.logging_context(THEME_TAG, "ja_original_check_retry"):
                check2 = vfl01.run_deviation_check(client, full_ledger_text, rewritten_text,
                                                    hook_aware=False, include_related_fact_id=True,
                                                    prior_issues=must_fix_used)
            checks_log.append(check2)
            final_status = check2["parsed"].get("overall_status")
            all_resolved = check2["parsed"].get("all_prior_issues_resolved", False)
            if not (final_status == "LEDGER_COMPLIANT" and all_resolved):
                raise JAFactCheckStopError(
                    stage="original",
                    message="[STOP] JA_FACT_CHECK_STOP: JA Original Fact Check、"
                            "must-fix Rewrite後もMAJOR、または前回指摘の未解消が残りました"
                            f"(overall_status={final_status}, all_prior_issues_resolved={all_resolved})。"
                            "本文を手で直さずSTOPします。",
                    rejected_text=rewritten_text, checks=checks_log, must_fix_used=must_fix_used,
                )
            original_text = rewritten_text
            stages["original"] = {
                "text": original_text, "response_id": response_mf.id, "model": response_mf.model,
                "prompt": prompt_must_fix, "developer_message": DEVELOPER_MESSAGE,
                "must_fix_applied": True, "must_fix": must_fix_used,
                "pre_must_fix_response_id": response.id,
            }
        fact_checks["original"] = {
            "checks": checks_log, "must_fix_applied": must_fix_applied,
            "must_fix_used": must_fix_used, "final_status": final_status,
        }

    # TTS-SYMBOL-NORMALIZATION-ALL-FAMILY-PRODUCTION-WIRING-01(Layer 2、
    # 2026-09-27): Fact Checkとは独立に(full_ledger_text=Noneの後方互換
    # 呼び出しでも常に)、音声化禁止記号を検出する。1回だけmust-fixで
    # 再生成し、なお解消しなければJAFactCheckStopErrorでSTOPする(既存の
    # Fact Check must-fix機構と同型のretry 1回→再Check→STOPパターン)。
    original_symbol_findings = safety.detect_prohibited_symbols(original_text, language="ja")
    if safety.symbol_gate_requires_stop(original_symbol_findings):
        print(f"[JA-WRITER][ja_original] 音声化禁止記号を検出。must-fixで1回だけ再生成します"
              f"(count={len(original_symbol_findings)})...")
        symbol_prompt = build_original_prompt(storyline_line, selected_fact_brief_text) + (
            "\n\n" + safety.build_symbol_violation_prompt_note(original_symbol_findings))
        response_sym = call_fresh(client, DEVELOPER_MESSAGE, symbol_prompt, WRITER_EFFORT,
                                   "ja_original_symbol_must_fix")
        rewritten_sym = response_sym.output_text.strip()
        recheck_findings = safety.detect_prohibited_symbols(rewritten_sym, language="ja")
        if safety.symbol_gate_requires_stop(recheck_findings):
            raise JAFactCheckStopError(
                stage="original_symbol",
                message="[STOP] JA_SYMBOL_CHECK_STOP: JA Original音声化禁止記号Check、"
                        f"must-fix Rewrite後も禁止記号が残りました(findings={recheck_findings})。"
                        "本文を手で直さずSTOPします。",
                rejected_text=rewritten_sym, checks=[], must_fix_used=original_symbol_findings,
            )
        original_text = rewritten_sym
        stages["original"] = {
            **stages["original"], "text": original_text, "response_id": response_sym.id,
            "model": response_sym.model, "symbol_must_fix_applied": True,
            "symbol_findings": original_symbol_findings,
            "pre_symbol_must_fix_response_id": stages["original"]["response_id"],
        }

    prev_id = stages["original"]["response_id"]
    prev_text = original_text
    chain_method = None

    for stage_key in ("r1", "r2"):
        instruction = REVISION_INSTRUCTIONS[stage_key] + SYMBOL_PREVENTION_BLOCK_JA
        used_method = None
        response = None
        if chain_method != "fallback_full_text":
            try:
                response = call_with_previous_response_id(
                    client, instruction, WRITER_EFFORT, prev_id, f"ja_{stage_key}")
                used_method = "previous_response_id"
            except Exception as exc:  # noqa: BLE001 - 技術的失敗時のみフォールバック
                print(f"[WARN][ja_writer] previous_response_id失敗、フォールバックへ切替"
                      f"({stage_key}): {exc}")
                response = None
        if response is None:
            fallback_user = f"以下の記事:\n\n{prev_text}\n\n{instruction}"
            response = call_fresh(client, DEVELOPER_MESSAGE, fallback_user, WRITER_EFFORT,
                                   f"ja_{stage_key}")
            used_method = "fallback_full_text"
        chain_method = used_method
        article_text = response.output_text.strip()
        stages[stage_key] = {
            "text": article_text, "response_id": response.id, "model": response.model,
            "instruction": instruction, "chain_method": used_method,
            "previous_response_id_used": prev_id if used_method == "previous_response_id" else None,
        }
        prev_id = response.id
        prev_text = article_text

    if full_ledger_text is not None:
        r2_text = stages["r2"]["text"]
        with cl.logging_context(THEME_TAG, "ja_r2_check"):
            checkR2_1 = vfl01.run_deviation_check(client, full_ledger_text, r2_text,
                                                   hook_aware=False, include_related_fact_id=True)
        checksR2_log = [checkR2_1]
        statusR2_1 = checkR2_1["parsed"].get("overall_status")
        finalR2_status = statusR2_1
        must_fix_applied_r2 = False
        must_fix_used_r2 = []
        if statusR2_1 == "LEDGER_DEVIATION":
            must_fix_applied_r2 = True
            major_devs_r2 = _major_deviations(checkR2_1)
            must_fix_used_r2 = _must_fix_from_deviations(major_devs_r2)
            print(f"[JA-WRITER][ja_r2] Fact Check MAJOR。R1からのrevisionとしてmust-fixで"
                  f"1回だけ再生成します(major_count={len(major_devs_r2)})...")
            r2_must_fix_instruction = (
                REVISION_INSTRUCTIONS["r2"] + "\n\n" +
                build_must_fix_block(must_fix_used_r2, full_ledger_text)
            )
            r1_response_id = stages["r1"]["response_id"]
            used_method_mf = None
            response_mf = None
            try:
                response_mf = call_with_previous_response_id(
                    client, r2_must_fix_instruction, WRITER_EFFORT, r1_response_id, "ja_r2_must_fix")
                used_method_mf = "previous_response_id"
            except Exception as exc:  # noqa: BLE001 - 技術的失敗時のみフォールバック
                print(f"[WARN][ja_writer] previous_response_id失敗、フォールバックへ切替"
                      f"(ja_r2_must_fix): {exc}")
                response_mf = None
            if response_mf is None:
                fallback_user = f"以下の記事:\n\n{stages['r1']['text']}\n\n{r2_must_fix_instruction}"
                response_mf = call_fresh(client, DEVELOPER_MESSAGE, fallback_user, WRITER_EFFORT,
                                          "ja_r2_must_fix")
                used_method_mf = "fallback_full_text"
            rewritten_r2 = response_mf.output_text.strip()
            with cl.logging_context(THEME_TAG, "ja_r2_check_retry"):
                checkR2_2 = vfl01.run_deviation_check(client, full_ledger_text, rewritten_r2,
                                                       hook_aware=False, include_related_fact_id=True,
                                                       prior_issues=must_fix_used_r2)
            checksR2_log.append(checkR2_2)
            finalR2_status = checkR2_2["parsed"].get("overall_status")
            all_resolved_r2 = checkR2_2["parsed"].get("all_prior_issues_resolved", False)
            if not (finalR2_status == "LEDGER_COMPLIANT" and all_resolved_r2):
                raise JAFactCheckStopError(
                    stage="r2",
                    message="[STOP] JA_FACT_CHECK_STOP: JA R2 Fact Check、"
                            "must-fix Rewrite後もMAJOR、または前回指摘の未解消が残りました"
                            f"(overall_status={finalR2_status}, "
                            f"all_prior_issues_resolved={all_resolved_r2})。"
                            "本文を手で直さずSTOPします。",
                    rejected_text=rewritten_r2, checks=checksR2_log, must_fix_used=must_fix_used_r2,
                )
            stages["r2"] = {
                **stages["r2"], "text": rewritten_r2, "response_id": response_mf.id,
                "model": response_mf.model, "must_fix_applied": True,
                "must_fix": must_fix_used_r2, "must_fix_chain_method": used_method_mf,
                "pre_must_fix_response_id": stages["r2"]["response_id"],
            }
        fact_checks["r2"] = {
            "checks": checksR2_log, "must_fix_applied": must_fix_applied_r2,
            "must_fix_used": must_fix_used_r2, "final_status": finalR2_status,
        }

    # TTS-SYMBOL-NORMALIZATION-ALL-FAMILY-PRODUCTION-WIRING-01(Layer 2、
    # 2026-09-27): originalと同じ理由で、R2(=最終final_text、japanese_
    # titleの抽出元)にもFact Checkと独立に音声化禁止記号Validatorを適用
    # する(Meta STOP実例のA2 japanese_title「…」は、まさにこのR2最終
    # テキストのtitleから抽出されたもの)。
    r2_final_text = stages["r2"]["text"]
    r2_symbol_findings = safety.detect_prohibited_symbols(r2_final_text, language="ja")
    if safety.symbol_gate_requires_stop(r2_symbol_findings):
        print(f"[JA-WRITER][ja_r2] 音声化禁止記号を検出。R1からのrevisionとしてmust-fixで"
              f"1回だけ再生成します(count={len(r2_symbol_findings)})...")
        r2_symbol_instruction = (
            REVISION_INSTRUCTIONS["r2"] + SYMBOL_PREVENTION_BLOCK_JA + "\n\n"
            + safety.build_symbol_violation_prompt_note(r2_symbol_findings)
        )
        r1_response_id_for_symbol = stages["r1"]["response_id"]
        used_method_sym = None
        response_sym = None
        try:
            response_sym = call_with_previous_response_id(
                client, r2_symbol_instruction, WRITER_EFFORT, r1_response_id_for_symbol, "ja_r2_symbol_must_fix")
            used_method_sym = "previous_response_id"
        except Exception as exc:  # noqa: BLE001 - 技術的失敗時のみフォールバック
            print(f"[WARN][ja_writer] previous_response_id失敗、フォールバックへ切替"
                  f"(ja_r2_symbol_must_fix): {exc}")
            response_sym = None
        if response_sym is None:
            fallback_user = f"以下の記事:\n\n{stages['r1']['text']}\n\n{r2_symbol_instruction}"
            response_sym = call_fresh(client, DEVELOPER_MESSAGE, fallback_user, WRITER_EFFORT,
                                       "ja_r2_symbol_must_fix")
            used_method_sym = "fallback_full_text"
        rewritten_r2_sym = response_sym.output_text.strip()
        recheck_r2_findings = safety.detect_prohibited_symbols(rewritten_r2_sym, language="ja")
        if safety.symbol_gate_requires_stop(recheck_r2_findings):
            raise JAFactCheckStopError(
                stage="r2_symbol",
                message="[STOP] JA_SYMBOL_CHECK_STOP: JA R2音声化禁止記号Check、"
                        f"must-fix Rewrite後も禁止記号が残りました(findings={recheck_r2_findings})。"
                        "本文を手で直さずSTOPします。",
                rejected_text=rewritten_r2_sym, checks=[], must_fix_used=r2_symbol_findings,
            )
        stages["r2"] = {
            **stages["r2"], "text": rewritten_r2_sym, "response_id": response_sym.id,
            "model": response_sym.model, "symbol_must_fix_applied": True,
            "symbol_findings": r2_symbol_findings, "symbol_must_fix_chain_method": used_method_sym,
            "pre_symbol_must_fix_response_id": stages["r2"]["response_id"],
        }

    result = {
        "stages": stages, "final_text": stages["r2"]["text"],
        "chain_method": chain_method, "verbatim_shas": verbatim_shas(),
        "title": _extract_title(stages["r2"]["text"]),
    }
    if full_ledger_text is not None:
        result["fact_checks"] = fact_checks
    return result
