# ============================================================
# er008_n8_wait_and_date_fix_retts_22.py
# ER-008-N8-FINAL-CONTENT-COMPRESSION-RETRY-22 Item 1/3/9:
# No.8のA2/B1で、article.md/parts.jsonへ手動で反映した2件のテキスト
# 修正(1: "wait"の意味衝突解消、3: Evidence Compression新ルールに
# よる日付圧縮)を、実際に影響を受けたfull_story_part1/part2の4segment
# だけ再TTS/ASRする。他のsegment(Point/Comment/Key Phrase等)は本文が
# 変わっていないため、既存のVALIDATED/HUMAN_APPROVED assetをそのまま
# 再利用する(不要な全TTS再生成はしない)。
#
# canonical_textがparts.json更新により変わっているため、er011_human_
# review_lock_01は自動的に「新しいsegmentのバージョン」として扱い、
# 通常のAUTO_PROCESSINGを許可する(明示的なapprove_regenerateは不要)。
# ============================================================
import json

import er003_v1_n3_01_tts_generate as tg
import er005_cost_logger as cl

A2_DIR = "er006_output/pool_pilot_01/pool_n8_airport_line/a2"
B1_DIR = "er006_output/pool_pilot_01/pool_n8_airport_line/b1b"
BASE = "er006_output/pool_pilot_01/pool_n8_airport_line"


def _update_segment(out_dir, name, new_result):
    audit_path = f"{out_dir}/audit/tts_generation_results.json"
    with open(audit_path, encoding="utf-8") as f:
        data = json.load(f)
    data["segments"][name] = new_result
    with open(audit_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def regen_a2():
    parts = tg.load_json(f"{A2_DIR}/parts.json")
    narration_dir = f"{A2_DIR}/narration"
    report = {}
    for name, text in (("full_story_part1", parts["part1"]), ("full_story_part2", parts["part2"])):
        tts_input = tg.tts_safe_news_en(text)
        print(f"[ER-22][A2] {name} 再生成開始...")
        result = tg.generate_a2_segment_with_slowdown(
            tts_input, f"{narration_dir}/{name}.wav", tg.first_words(text),
            style_prefix_override=tg.A2_ENGLISH_STYLE_PREFIX_SLOWER, disfluency_qa=False)
        result["canonical_text"] = text
        print(f"[ER-22][A2] {name} status={result.get('status')} asr_verified={result.get('asr_verified')} "
              f"asr_text={result.get('asr_text')!r}")
        _update_segment(A2_DIR, name, result)
        report[name] = {"status": result.get("status"), "asr_verified": result.get("asr_verified"),
                         "asr_text": result.get("asr_text"), "sha256": result.get("sha256")}
    return report


def regen_b1():
    parts = tg.load_json(f"{B1_DIR}/parts.json")
    narration_dir = f"{B1_DIR}/narration"
    report = {}
    for name, text in (("full_story_part1", parts["part1"]), ("full_story_part2", parts["part2"])):
        tts_input = tg.tts_safe_news_en(text)
        print(f"[ER-22][B1] {name} 再生成開始...")
        result = tg.news_tail_fix.generate_news_narration_wide_margin(
            tts_input, f"{narration_dir}/{name}.wav", disfluency_qa=False)
        result["canonical_text"] = text
        print(f"[ER-22][B1] {name} status={result.get('status')} asr_verified={result.get('asr_verified')} "
              f"asr_text={result.get('asr_text')!r}")
        _update_segment(B1_DIR, name, result)
        report[name] = {"status": result.get("status"), "asr_verified": result.get("asr_verified"),
                         "asr_text": result.get("asr_text"), "sha256": result.get("sha256")}
    return report


if __name__ == "__main__":
    # ER-22: B1側(news_tail_fix経由のAzure ASR cascade)がer005_cost_logger.
    # record()を直接呼ぶため、cl.install()未実行だとRuntimeErrorになる
    # (A2側はOpenAI SDK呼び出しのみのため、install()未実行でも例外にはならず
    # 単にコストが記録されないだけだった)。No.8既存のraw_usage_log.jsonlへ
    # 引き続き追記する。
    cl.install(f"{BASE}/raw_usage_log.jsonl")
    a2_report = regen_a2()
    b1_report = regen_b1()
    summary = {"a2": a2_report, "b1": b1_report}
    with open("er008_output/n8_wait_and_date_fix_retts_22_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
