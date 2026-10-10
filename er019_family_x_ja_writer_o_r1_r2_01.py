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
# RISK-FLAGGER-PRODUCTION-WIRING-01 Phase 2 C2(2026-10-10): 旧Fact Checker(Original直後/R2直後の
# 台帳照合・指摘起点の再生成・Fact用STOP例外)を物理削除した(案P)。
# 本moduleのOriginal→R1→R2(Luna連鎖)は、Production正式経路では
# 新Writer W-1(Production module名はFactLock JA Writer)に置換されて呼ばれない(Trial互換のため残置)。
# 残るのは技術QA(音声化禁止記号Validator[JASymbolCheckStopError]、previous_response_id fallback)と、
# W-1が参照するProduction資産(R0_PROMPT/DEVELOPER_MESSAGE/SYMBOL_PREVENTION_BLOCK_JA/
# CONCRETENESS_CONTROL_AN3_BLOCK/REVISION_INSTRUCTIONS)のみ。
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
    "- 時刻は「午前11時4分」のように日本語で書いてください"
    "(「11:04」のような数字とコロンの記号表記は使わないでください)。\n"
    "- URLやメールアドレスは書かないでください。絵文字も使わないでください。"
)

# FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01(2026-09-28): Trial
# (er037/er039)のA3+N2(AN3、ユーザー正式決定APPROVED_FOR_PRODUCTION)を
# 逐語で移設。R0_PROMPT自体は無変更、build_original_prompt()で別途追記
# する(SYMBOL_PREVENTION_BLOCK_JAと同型パターン)。「数字を0にする」とは
# 定義しない(定性的な抑制指示であり数値目標ではない)。
CONCRETENESS_CONTROL_AN3_BLOCK = (
    "\n\n数字・時刻は基本的に使わないでください。記事の理解に本当に必要な場合"
    "だけ、最小限に使ってください。\n"
    "人名・企業名・地名などの固有名詞は、話の理解に必要な場合だけ使い、それ"
    "以外は一般的な言い方にしてください。"
)


def sha256_text(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def verbatim_shas() -> dict:
    return {
        "r0_prompt_sha256": sha256_text(R0_PROMPT),
        "developer_message_sha256": sha256_text(DEVELOPER_MESSAGE),
        "r1_instruction_sha256": sha256_text(REVISION_INSTRUCTIONS["r1"]),
        "r2_instruction_sha256": sha256_text(REVISION_INSTRUCTIONS["r2"]),
        # FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01(2026-09-28): 追加
        "concreteness_an3_block_sha256": sha256_text(CONCRETENESS_CONTROL_AN3_BLOCK),
    }


def build_original_prompt(storyline_line: str, selected_fact_brief_text: str) -> str:
    """trial_02.build_prompt()と同一構造(「テーマ：」行を差し替え、
    末尾に[ニュース]欄を追加)。素材はSelected Fact Brief全文。
    (C2: 旧Fact Checker起点の追加引数・台帳再掲ブロックは撤去に伴い削除。)"""
    lines = R0_PROMPT.split("\n")
    new_lines = [f"テーマ：{storyline_line}" if line.startswith("テーマ：") else line
                 for line in lines]
    prompt = "\n".join(new_lines)
    prompt += "\n\n[ニュース]\n" + selected_fact_brief_text
    prompt += SYMBOL_PREVENTION_BLOCK_JA
    prompt += CONCRETENESS_CONTROL_AN3_BLOCK  # FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01
    return prompt


class JASymbolCheckStopError(RuntimeError):
    """音声化禁止記号Validator(技術QA、T-01/T-02)で、1回の再生成後も禁止記号が残った場合のSTOP
    (本文を手で直さない)。呼び出し側(runner)がrejected_ja_<stage>.mdを保存できるよう属性を保持する。
    (C2: 旧Fact用STOP例外と共用だった例外クラスから記号QA専用へ分離。挙動は記号QA側は不変。)"""

    def __init__(self, stage: str, message: str, rejected_text: str, findings: list):
        super().__init__(message)
        self.stage = stage
        self.rejected_text = rejected_text
        self.findings = findings


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


def run_ja_writer_o_r1_r2(client, storyline_line: str, selected_fact_brief_text: str) -> dict:
    """Original -> r1 -> r2をprevious_response_idで連鎖実行する(Luna連鎖、Trial互換のため残置。
    Production正式経路[er019 entertainment runner]は新Writer W-1を
    使い、本関数は呼ばない)。技術的失敗(previous_response_id不可)時のみ、直前記事全文を貼る
    fallback_full_textへ切替える(trial01/02と同一方針)。

    音声化禁止記号Validator(技術QA、Layer 2)は常に適用し、検出時は1回だけ再生成、なお残れば
    JASymbolCheckStopErrorでSTOPする。旧Fact Check(台帳照合+指摘起点の再生成)はC2で撤去済み。

    戻り値: {"stages": {"original": {...}, "r1": {...}, "r2": {...}},
             "final_text": <r2本文>, "chain_method": ..., "verbatim_shas": ..., "title": ...}"""
    prompt_original = build_original_prompt(storyline_line, selected_fact_brief_text)
    response = call_fresh(client, DEVELOPER_MESSAGE, prompt_original, WRITER_EFFORT, "ja_original")
    original_text = response.output_text.strip()
    stages = {
        "original": {
            "text": original_text, "response_id": response.id, "model": response.model,
            "prompt": prompt_original, "developer_message": DEVELOPER_MESSAGE,
        }
    }

    # TTS-SYMBOL-NORMALIZATION-ALL-FAMILY-PRODUCTION-WIRING-01(Layer 2、
    # 2026-09-27): 音声化禁止記号を検出する。1回だけ再生成し、なお解消しなければ
    # JASymbolCheckStopErrorでSTOPする(retry 1回→再検査→STOPパターン)。
    original_symbol_findings = safety.detect_prohibited_symbols(original_text, language="ja")
    if safety.symbol_gate_requires_stop(original_symbol_findings):
        print(f"[JA-WRITER][ja_original] 音声化禁止記号を検出。1回だけ再生成します"
              f"(count={len(original_symbol_findings)})...")
        symbol_prompt = build_original_prompt(storyline_line, selected_fact_brief_text) + (
            "\n\n" + safety.build_symbol_violation_prompt_note(original_symbol_findings))
        response_sym = call_fresh(client, DEVELOPER_MESSAGE, symbol_prompt, WRITER_EFFORT,
                                   "ja_original_symbol_must_fix")
        rewritten_sym = response_sym.output_text.strip()
        recheck_findings = safety.detect_prohibited_symbols(rewritten_sym, language="ja")
        if safety.symbol_gate_requires_stop(recheck_findings):
            raise JASymbolCheckStopError(
                stage="original_symbol",
                message="[STOP] JA_SYMBOL_CHECK_STOP: JA Original音声化禁止記号Check、"
                        f"再生成後も禁止記号が残りました(findings={recheck_findings})。"
                        "本文を手で直さずSTOPします。",
                rejected_text=rewritten_sym, findings=original_symbol_findings,
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

    # TTS-SYMBOL-NORMALIZATION-ALL-FAMILY-PRODUCTION-WIRING-01(Layer 2): originalと同じ理由で、
    # R2(=最終final_text、japanese_titleの抽出元)にも音声化禁止記号Validatorを適用する
    # (Meta STOP実例のA2 japanese_title「…」は、まさにこのR2最終テキストのtitleから抽出されたもの)。
    r2_final_text = stages["r2"]["text"]
    r2_symbol_findings = safety.detect_prohibited_symbols(r2_final_text, language="ja")
    if safety.symbol_gate_requires_stop(r2_symbol_findings):
        print(f"[JA-WRITER][ja_r2] 音声化禁止記号を検出。R1からのrevisionとして"
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
            raise JASymbolCheckStopError(
                stage="r2_symbol",
                message="[STOP] JA_SYMBOL_CHECK_STOP: JA R2音声化禁止記号Check、"
                        f"再生成後も禁止記号が残りました(findings={recheck_r2_findings})。"
                        "本文を手で直さずSTOPします。",
                rejected_text=rewritten_r2_sym, findings=r2_symbol_findings,
            )
        stages["r2"] = {
            **stages["r2"], "text": rewritten_r2_sym, "response_id": response_sym.id,
            "model": response_sym.model, "symbol_must_fix_applied": True,
            "symbol_findings": r2_symbol_findings, "symbol_must_fix_chain_method": used_method_sym,
            "pre_symbol_must_fix_response_id": stages["r2"]["response_id"],
        }

    return {
        "stages": stages, "final_text": stages["r2"]["text"],
        "chain_method": chain_method, "verbatim_shas": verbatim_shas(),
        "title": _extract_title(stages["r2"]["text"]),
    }
