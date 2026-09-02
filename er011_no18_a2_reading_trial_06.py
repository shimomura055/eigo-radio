# ============================================================
# er011_no18_a2_reading_trial_06.py
# ER-011-NO18-B1-LISTENING-AND-A2-OPEN111-READING-TRIAL-06 Track B
# ============================================================
# OPEN-111(A2 comment_1「通知音のあとに」がASRで「後」と書き起こされ
# 続けてTRUE_CONTENT_MISMATCHになる問題)の根本原因は、pykakasiが文脈込みで
# すら「の後に」を「のち」読みへ解決してしまうこと(本Trial実行前にpython
# 単体で直接確認済み: kks.convert('通知音の後に作業へ')は「ののちに」を返す)。
#
# 本Trialは、この問題をASR比較専用の「全文文脈保持ひらがなcanonical
# reading」方式で解消できるかを検証する。Writerとは別の専用役割
# (generate_reading_role_hiragana)が、既に確定済みのA2 tts_input_text
# (原文)から文脈を読んだ上で全文ひらがな読みを生成する(pykakasiのような
# 逐語/機械変換ではなく、Approved Writer Modelによる文脈理解読み)。
#
# 新規TTS呼び出しは行わない(既存のA2 narration wavをそのまま再利用、
# comment_1のwavも6回目attemptの実音声が既に保存されている)。ASR側は
# 既存の routing.transcribe() とは別に、ひらがな書き起こしを明示指示する
# prompt付きの直接呼び出しを行い、
#   (a) 実際にひらがな書き起こしが得られるか
#   (b) それが音響レベルの本物のかな認識か、単なる漢字認識後の後処理的な
#       字種変換に過ぎない可能性がないか
# を、既存の(漢字混じりの)通常ASR結果とテキスト上で突き合わせて評価する。
#
# Production配線は一切行わない(既存のer007_ja_asr_validator_01.py /
# er003_v1_n3_01_tts_generate.pyは無変更)。本Trialの結果だけでは
# Production採用を決定しない。

from __future__ import annotations

import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import er003_v1_en_direct_vfl_01_generate as vfl01
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing

OUT_DIR = "er011_output/open111_a2_reading_trial_06"
os.makedirs(OUT_DIR, exist_ok=True)

A2_AUDIT_PATH = "er006_output/pool_pilot_01/pool_n18_notifications_specfix_v2/a2/audit/tts_generation_results.json"
A2_NARRATION_DIR = "er006_output/pool_pilot_01/pool_n18_notifications_specfix_v2/a2/narration"

cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")

client = vfl01.get_client()

READING_MODEL = routing.require_model_or_override(
    "A2_SUPPORT", routing.SUPPORT_MODEL,
    override_reason=None,  # SUPPORT_MODELとWRITER_MODELは同一Approved Modelのため素通り、overrideなし
)

READING_DEVELOPER_MESSAGE = """あなたは「Reading担当」です。Writer(記事執筆)ではありません。
与えられた日本語テキストは、TTS(音声合成)に既に実際に入力される確定済みの文章です。
あなたの仕事は、このテキストが自然な日本語として音読されたときの「読み」を、
全文を通した文脈を踏まえて判断し、一字一字の機械的な変換ではなく、
実際にナレーターがこの文脈でどう読むかを考えて、完全にひらがなだけで出力することです。

厳守事項:
- 出力は完全にひらがなのみ(漢字・カタカナ・ローマ字・算用数字を残さない)。
  カタカナ語(外来語)・数字・記号も、実際に音読される通りのひらがな表記に変換すること。
- 個々の漢字について特定の読みをあらかじめ決め打ちしない(例:「後」を常に
  「あと」または常に「のち」と機械的に決めるのではなく、その文中でどちらが
  自然かを都度判断すること)。
- 単語を追加・削除・言い換えしない。読みだけを出力し、原文の意味・語順・
  句読点の位置に対応する読みの区切りは保持すること(句読点自体は読みには
  含めない)。
- 出力はJSON形式で、{"hiragana_reading": "..."} のみを返すこと。説明や
  前置きは一切含めない。
"""


def call_reading_role(text: str) -> dict:
    response = client.responses.create(
        model=READING_MODEL,
        reasoning={"effort": "medium"},
        text={"format": {"type": "json_schema", "name": "reading_role_output", "schema": {
            "type": "object",
            "properties": {"hiragana_reading": {"type": "string"}},
            "required": ["hiragana_reading"],
            "additionalProperties": False,
        }, "strict": True}},
        input=[
            {"role": "developer", "content": READING_DEVELOPER_MESSAGE},
            {"role": "user", "content": text},
        ],
    )
    raw = response.output_text
    parsed = json.loads(raw)
    return {"hiragana_reading": parsed["hiragana_reading"], "response_id": response.id, "model": response.model}


def call_kana_asr(wav_path: str) -> dict:
    """既存のroutingとは別に、ひらがな書き起こしを明示指示するpromptを
    付けてOpenAI ASRを直接呼ぶ(Trial専用、Production routingは無変更)。"""
    with open(wav_path, "rb") as f:
        resp = client.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",
            file=f,
            language="ja",
            prompt="この音声を、漢字を一切使わずに、聞こえた通りの発音のままひらがなだけで書き起こしてください。",
        )
    return {"kana_asr_text": resp.text}


_HALFWIDTH_PUNCT = "、。・「」『』（）()!?！？…—―‥～〜/／,.　 \n\t"
_KATAKANA_TO_HIRAGANA = {chr(c): chr(c - 0x60) for c in range(0x30A1, 0x30F7)}


def normalize_kana_for_compare(text: str) -> str:
    """比較専用の軽量正規化: 句読点・空白除去、カタカナ->ひらがな変換のみ
    (existing normalize_ja()は漢数字正規化等ひらがな比較には不要な処理を
    含むため、本Trialでは最小限の独自正規化を使う)。"""
    if not text:
        return ""
    out = []
    for ch in text:
        if ch in _HALFWIDTH_PUNCT:
            continue
        out.append(_KATAKANA_TO_HIRAGANA.get(ch, ch))
    return "".join(out)


def contains_kanji(text: str) -> bool:
    return any("一" <= ch <= "鿿" for ch in text)


SEGMENTS_TO_TEST = ["comment_1", "comment_3", "japanese_title", "preview", "comment_2", "comment_4"]


def main():
    audit = json.load(open(A2_AUDIT_PATH, encoding="utf-8"))
    segs = audit["segments"]

    results = {}
    for seg_id in SEGMENTS_TO_TEST:
        seg = segs[seg_id]
        canonical_text = seg.get("canonical_text") or seg.get("text")
        tts_input = seg.get("tts_input_text_after_reading_safety") or canonical_text
        wav_path = seg.get("path") or f"{A2_NARRATION_DIR}/{seg_id}.wav"
        existing_asr_text = seg.get("asr_text")  # None for comment_1(STOPPED)。既存の漢字混じりASR結果(再利用、再呼び出ししない)。

        print(f"[reading_trial_06] {seg_id}: Reading role呼び出し中...")
        with cl.logging_context("no18_a2_open111", f"reading_role_a2_{seg_id}"):
            reading = call_reading_role(tts_input)

        print(f"[reading_trial_06] {seg_id}: かなASR呼び出し中 ({wav_path})...")
        with cl.logging_context("no18_a2_open111", f"kana_asr_a2_{seg_id}"):
            kana_asr = call_kana_asr(wav_path)

        canonical_reading_norm = normalize_kana_for_compare(reading["hiragana_reading"])
        asr_kana_norm = normalize_kana_for_compare(kana_asr["kana_asr_text"])
        match = canonical_reading_norm == asr_kana_norm
        asr_kana_has_kanji = contains_kanji(kana_asr["kana_asr_text"])

        results[seg_id] = {
            "canonical_text": canonical_text,
            "tts_input_text": tts_input,
            "wav_path": wav_path,
            "existing_kanji_asr_text": existing_asr_text,
            "reading_role": {
                "hiragana_reading": reading["hiragana_reading"],
                "model": reading["model"],
                "response_id": reading["response_id"],
            },
            "kana_asr": {
                "raw_text": kana_asr["kana_asr_text"],
                "contains_kanji": asr_kana_has_kanji,
            },
            "normalized_expected": canonical_reading_norm,
            "normalized_actual": asr_kana_norm,
            "match": match,
            "verdict": "PASS" if match else "FAIL",
        }
        print(f"[reading_trial_06] {seg_id}: verdict={results[seg_id]['verdict']} "
              f"asr_kana_has_kanji={asr_kana_has_kanji}")

    with open(f"{OUT_DIR}/reading_trial_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    n_pass = sum(1 for r in results.values() if r["verdict"] == "PASS")
    print(f"[reading_trial_06] 完了。{n_pass}/{len(results)} segment PASS。"
          f"詳細: {OUT_DIR}/reading_trial_results.json")


if __name__ == "__main__":
    main()
