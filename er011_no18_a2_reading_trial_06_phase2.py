# ============================================================
# er011_no18_a2_reading_trial_06_phase2.py
# ER-011-NO18-B1-LISTENING-AND-A2-OPEN111-READING-TRIAL-06 Track B Phase 2
# ============================================================
# Phase 1(er011_no18_a2_reading_trial_06.py)で判明した事実:
# OpenAI gpt-4o-mini-transcribeへ「ひらがなのみで書き起こしてください」と
# promptで指示しても、6segment全てで通常の漢字混じり書き起こしと
# ほぼ同一の結果しか返らなかった(かな書き起こし指示は事実上無視される)。
# これは「漢字認識→後処理でかな変換」ですらなく、そもそもASR側が
# 字種(orthography)をpromptで制御できないという、より基本的な制約。
#
# Phase 2はこれを受けて、比較方式を1段組み替える:
#   (A) canonical_text(確定済み原文) -> Reading role(文脈込みLLM) -> ひらがな
#   (B) 既存の通常ASR結果(漢字混じり、追加TTS/ASR呼び出しなし、既存JSON
#       流用) -> (B-1) pykakasi機械変換 でひらがな化
#                (B-2) 同じReading role(LLM) でひらがな化
# (A) vs (B-1)、(A) vs (B-2) の両方を比較し、
#   - (B-1)は元のValidatorと同じ機構(pykakasi)をASR側に適用しただけ
#     なので、OPEN-111と同じ読み誤りを再現するはず(=解決しないことの確認)
#   - (B-2)は「ASR側もWriterの原文というヒントなしに、文脈だけで正しく
#     あと/のちを判定できるか」という、より厳しいテスト
# を切り分ける。新規TTS呼び出しは行わない。

from __future__ import annotations

import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import pykakasi

import er003_v1_en_direct_vfl_01_generate as vfl01
import er005_cost_logger as cl
import er011_no18_a2_reading_trial_06 as t06

OUT_DIR = t06.OUT_DIR
A2_AUDIT_PATH = t06.A2_AUDIT_PATH

cl.install(f"{OUT_DIR}/raw_usage_log_phase2.jsonl")
client = vfl01.get_client()
t06.client = client  # phase1と同じclient/model routingをそのまま再利用

kks = pykakasi.kakasi()


def kakasi_hiragana(text: str) -> str:
    return "".join(r["hira"] for r in kks.convert(text))


def get_asr_text_for_segment(seg_id: str, seg: dict) -> str:
    """既存JSONの再利用のみ(新規ASR呼び出しなし)。comment_1はSTOPPEDのため
    トップレベルasr_textがNoneなので、standard_attempts_logの最終(6回目)
    attemptのasr_textを使う(既に保存済みの実測値、新規生成ではない)。"""
    if seg.get("asr_text"):
        return seg["asr_text"]
    log = seg.get("standard_attempts_log") or []
    if log:
        return log[-1]["asr_text"]
    raise ValueError(f"{seg_id}: 既存ASRテキストが見つかりません")


def main():
    phase1 = json.load(open(f"{OUT_DIR}/reading_trial_results.json", encoding="utf-8"))
    audit = json.load(open(A2_AUDIT_PATH, encoding="utf-8"))
    segs = audit["segments"]

    results = {}
    for seg_id in t06.SEGMENTS_TO_TEST:
        seg = segs[seg_id]
        asr_kanji_text = get_asr_text_for_segment(seg_id, seg)
        canonical_reading = phase1[seg_id]["reading_role"]["hiragana_reading"]
        canonical_reading_norm = t06.normalize_kana_for_compare(canonical_reading)

        b1_kakasi = kakasi_hiragana(asr_kanji_text)
        b1_norm = t06.normalize_kana_for_compare(b1_kakasi)

        print(f"[phase2] {seg_id}: ASR結果へReading role適用中...")
        with cl.logging_context("no18_a2_open111", f"reading_role_asr_side_a2_{seg_id}"):
            b2 = t06.call_reading_role(asr_kanji_text)
        b2_norm = t06.normalize_kana_for_compare(b2["hiragana_reading"])

        results[seg_id] = {
            "asr_kanji_text": asr_kanji_text,
            "canonical_reading": canonical_reading,
            "asr_reading_via_kakasi_B1": b1_kakasi,
            "asr_reading_via_reading_role_B2": b2["hiragana_reading"],
            "match_A_vs_B1_kakasi": canonical_reading_norm == b1_norm,
            "match_A_vs_B2_reading_role": canonical_reading_norm == b2_norm,
        }
        print(f"[phase2] {seg_id}: A_vs_B1(kakasi)={results[seg_id]['match_A_vs_B1_kakasi']} "
              f"A_vs_B2(reading_role)={results[seg_id]['match_A_vs_B2_reading_role']}")

    with open(f"{OUT_DIR}/reading_trial_phase2_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    n_b1 = sum(1 for r in results.values() if r["match_A_vs_B1_kakasi"])
    n_b2 = sum(1 for r in results.values() if r["match_A_vs_B2_reading_role"])
    print(f"[phase2] 完了。B1(kakasi)={n_b1}/{len(results)} PASS, B2(reading_role)={n_b2}/{len(results)} PASS")


if __name__ == "__main__":
    main()
