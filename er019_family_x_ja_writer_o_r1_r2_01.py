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
# ============================================================
from __future__ import annotations

import hashlib

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


def sha256_text(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def verbatim_shas() -> dict:
    return {
        "r0_prompt_sha256": sha256_text(R0_PROMPT),
        "developer_message_sha256": sha256_text(DEVELOPER_MESSAGE),
        "r1_instruction_sha256": sha256_text(REVISION_INSTRUCTIONS["r1"]),
        "r2_instruction_sha256": sha256_text(REVISION_INSTRUCTIONS["r2"]),
    }


def build_original_prompt(storyline_line: str, selected_fact_brief_text: str) -> str:
    """trial_02.build_prompt()と同一構造(「テーマ：」行を差し替え、
    末尾に[ニュース]欄を追加)。素材はSelected Fact Brief全文。"""
    lines = R0_PROMPT.split("\n")
    new_lines = [f"テーマ：{storyline_line}" if line.startswith("テーマ：") else line
                 for line in lines]
    prompt = "\n".join(new_lines)
    prompt += "\n\n[ニュース]\n" + selected_fact_brief_text
    return prompt


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
    """Original -> r1 -> r2をprevious_response_idで連鎖実行する。
    技術的失敗(previous_response_id不可)時のみ、直前記事全文を貼る
    fallback_full_textへ切替える(trial01/02と同一方針)。
    戻り値: {"stages": {"original": {...}, "r1": {...}, "r2": {...}},
             "final_text": <r2本文>, "chain_method": ...}"""
    prompt_original = build_original_prompt(storyline_line, selected_fact_brief_text)
    response = call_fresh(client, DEVELOPER_MESSAGE, prompt_original, WRITER_EFFORT, "ja_original")
    original_text = response.output_text.strip()
    stages = {
        "original": {
            "text": original_text, "response_id": response.id, "model": response.model,
            "prompt": prompt_original, "developer_message": DEVELOPER_MESSAGE,
        }
    }
    prev_id = response.id
    prev_text = original_text
    chain_method = None

    for stage_key in ("r1", "r2"):
        instruction = REVISION_INSTRUCTIONS[stage_key]
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

    return {
        "stages": stages, "final_text": stages["r2"]["text"],
        "chain_method": chain_method, "verbatim_shas": verbatim_shas(),
        "title": _extract_title(stages["r2"]["text"]),
    }
