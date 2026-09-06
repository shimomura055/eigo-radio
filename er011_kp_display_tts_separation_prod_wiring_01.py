# ============================================================
# er011_kp_display_tts_separation_prod_wiring_01.py
# KEYPHRASE-DISPLAY-TTS-SEPARATION-PROD-WIRING-01: Runtime evidence
# ============================================================
# 目的: Gate 3チェックリストのRuntime evidence要件を満たす。Theme 2 B1
# (Trial-12 article.md)を入力に、Production正式経路(選定Prompt→
# canonicalization→Key Phrase日本語gloss TTS)を1回実行し、
#   (1) 表示用glossに「～」「〜」が含まれる場合、TTS用フィールドで
#       「なになに」変換が実際に発火することを確認する(選定結果に
#       含まれない場合は、既知の実gloss入力で同じProduction関数経路を
#       直接駆動して発火を実証する)。
#   (2) 数値placeholder型(「ソロ旅行を～％とする」)は変換されず、
#       既存のplaceholder gateで(TTS API呼び出し自体を行わずに)
#       ブロックされることを実証する。
#   (3) 実際のmodel_id/routing/tts_execution_mode=STANDARDを記録する。
#   (4) 表示用フィールド(japanese_gloss)とTTS用フィールド
#       (japanese_gloss_tts)の両方がartifact(keywords_canonicalized.json)
#       に保存されていることを確認する。
#
# TTSはStandard同期(TTS_EXECUTION_MODE=STANDARD)を使う
# (docs/pm/PM_GOVERNANCE.md 7節: 正式リリース前はStandard同期)。
# Production関数(sc.run_key_phrases/tts_gen.generate_charon_japanese_
# with_reading_safety/kwc.convert_display_gloss_to_tts_text/tts_gen.
# resolve_key_phrase_ja_gloss_tts)はすべて無変更のまま直接呼び出す
# (monkeypatchなし)。

from __future__ import annotations

import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

# PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-01: 正式リリース前はStandard同期を使う。
os.environ["TTS_EXECUTION_MODE"] = "STANDARD"

import er003_key_words_canonicalization as kwc
import er003_v1_n3_01_scaffold_generate as sc
import er003_v1_n3_01_tts_generate as tts_gen
import er005_cost_logger as cl

OUT_DIR = "er011_output/kp_display_tts_separation_prod_wiring_01"
ARTICLE_PATH = "er011_output/open112_trend_theme2_b_a2_b1_text_trial_12/b1b_run01/article.md"
ARTICLE_ID = "THEME2_B1_KPDISPLAYTTS_PRODWIRING01"
SOURCE_LEVEL = "B1-B(N3-01, direct generation)"

# 既知のgloss(OPEN-117-KEYPHRASE-DISPLAY-TTS-SEPARATION-TRIAL-02実データ、
# Theme 2 A2 rank5「not fully match」で実際に選定された表示用gloss)。
# 今回の選定結果に「～」「〜」を含むglossが1件も無かった場合、この既知
# 入力で同じProduction関数経路(convert_display_gloss_to_tts_text→
# generate_charon_japanese_with_reading_safety)を直接駆動し、変換の
# 実発火を実証する。
KNOWN_LEADING_TILDE_GLOSS = "～と完全には一致しない"

# 既知の数値placeholder型gloss(Trial-02実データ、Theme 2 B1 rank2
# 「put solo travel at」)。変換対象外の位置に「～」が残るため、TTS
# 呼び出し前にgateでブロックされることを実証する。
KNOWN_NUMERIC_PLACEHOLDER_GLOSS = "ソロ旅行を～％とする"


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def run_key_phrase_ja_tts(item: dict, out_dir: str, label: str) -> dict:
    """Production関数(tts_gen.resolve_key_phrase_ja_gloss_tts→tts_gen.
    generate_charon_japanese_with_reading_safety)をそのまま呼ぶ。"""
    ja_gloss = item["japanese_gloss"]
    ja_gloss_tts, used_fallback = tts_gen.resolve_key_phrase_ja_gloss_tts(item)
    out_path = f"{out_dir}/{label}.wav"
    with cl.segment_context(label):
        r = tts_gen.generate_charon_japanese_with_reading_safety(
            ja_gloss_tts, out_path, tts_gen.expected_substring_ja(ja_gloss_tts),
            known_key_phrase_terms=[item.get("used_form")])
    r["display_gloss"] = ja_gloss
    r["japanese_gloss_tts_used"] = ja_gloss_tts
    r["japanese_gloss_tts_fallback_derived"] = used_fallback
    r["conversion_fired"] = (ja_gloss_tts != ja_gloss)
    return r


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")

    article_text = load_text(ARTICLE_PATH)
    theme_out_dir = f"{OUT_DIR}/b1b"
    # ER-003-N3-01の正式呼び出し規約(er003_v1_n3_01_scaffold_generate.py::
    # run_theme_articles()、491行目)と同じ「out_dir/key_phrases」構造を
    # そのまま使う。
    kp_dir = f"{theme_out_dir}/key_phrases"
    os.makedirs(f"{theme_out_dir}/audit", exist_ok=True)

    print("[EVIDENCE] Step 1: Production Key Phrase選定→canonicalization→"
          "redundancy QA (sc.run_key_phrases, 無変更のProduction関数)...")
    with cl.logging_context("kp_display_tts_prod_wiring_01", "keyphrase_b1b"):
        kp_result = sc.run_key_phrases(article_text, kp_dir, ARTICLE_ID, SOURCE_LEVEL, process="B1_SUPPORT")

    sel_status = kp_result["selection"]["status"]
    canon_status = kp_result["canonicalization"]["status"] if kp_result["canonicalization"] else None
    redundancy_status = kp_result["redundancy_qa"]["status"] if kp_result.get("redundancy_qa") else None
    print(f"[EVIDENCE] selection={sel_status} canonicalization={canon_status} redundancy_qa={redundancy_status}")

    with open(f"{theme_out_dir}/audit/run_key_phrases_result_summary.json", "w", encoding="utf-8") as f:
        json.dump({
            "selection_status": sel_status, "canonicalization_status": canon_status,
            "redundancy_qa_status": redundancy_status,
            "redundancy_retry_log": kp_result.get("redundancy_retry_log"),
        }, f, ensure_ascii=False, indent=2, default=str)

    assert sel_status == "KEY_WORDS_STRUCTURE_PASS", f"選定失敗: {sel_status}"
    assert canon_status in ("CANONICALIZATION_PASS", "CANONICALIZATION_REVIEW_REQUIRED"), \
        f"canonicalization失敗: {canon_status}"

    merged_items = kp_result["canonicalization"]["merged"]["items"]
    print(f"[EVIDENCE] Step 1完了。選定5件の表示用/TTS用gloss:")
    for it in sorted(merged_items, key=lambda x: x["rank"]):
        print(f"  rank{it['rank']} used_form={it['used_form']!r} "
              f"japanese_gloss={it['japanese_gloss']!r} japanese_gloss_tts={it['japanese_gloss_tts']!r}")

    # (4) 表示用フィールドとTTS用フィールドの両方がartifactに保存されている
    # ことを確認する(keywords_canonicalized.json自体がProduction関数
    # run_key_phrase_canonicalization()により既に書き出し済み)。
    canon_artifact_path = f"{kp_dir}/keywords_canonicalized.json"
    assert os.path.exists(canon_artifact_path), f"canonicalization artifactが見つかりません: {canon_artifact_path}"
    with open(canon_artifact_path, encoding="utf-8") as f:
        artifact = json.load(f)
    for it in artifact["items"]:
        assert "japanese_gloss" in it and "japanese_gloss_tts" in it, \
            f"artifactにjapanese_gloss/japanese_gloss_ttsの両方が無い: rank {it.get('rank')}"
    print(f"[EVIDENCE] (4) artifact確認OK: {canon_artifact_path} の全itemsに"
          "japanese_gloss(表示用)とjapanese_gloss_tts(TTS用)の両方が存在する。")

    # Step 2: 選定された5件のKey Phrase日本語glossを、Production関数
    # (resolve_key_phrase_ja_gloss_tts→generate_charon_japanese_with_
    # reading_safety)でTTS(Standard同期)+ASR検証する。
    print("[EVIDENCE] Step 2: 選定5件の日本語gloss TTS(Standard同期)+ASR検証...")
    narration_dir = f"{theme_out_dir}/narration"
    os.makedirs(narration_dir, exist_ok=True)
    kp_tts_results = {}
    natural_conversion_fired = False
    with cl.logging_context("kp_display_tts_prod_wiring_01", "kp_ja_tts_b1b"):
        for it in sorted(merged_items, key=lambda x: x["rank"]):
            rank = it["rank"]
            label = f"kp{rank}_ja_charon"
            r = run_key_phrase_ja_tts(it, narration_dir, label)
            kp_tts_results[rank] = r
            if r["conversion_fired"]:
                natural_conversion_fired = True
            print(f"  rank{rank}: status={r.get('status')} conversion_fired={r['conversion_fired']}")

    with open(f"{theme_out_dir}/audit/kp_ja_tts_results.json", "w", encoding="utf-8") as f:
        json.dump(kp_tts_results, f, ensure_ascii=False, indent=2, default=str)

    # (1) 変換が選定結果内で自然発火しなかった場合、既知gloss入力で同じ
    # Production関数経路を直接駆動して発火を実証する。
    forced_conversion_result = None
    if not natural_conversion_fired:
        print("[EVIDENCE] 選定5件には「～」「〜」を含む表示用glossが無かったため、"
              "既知gloss入力で同じProduction関数経路を直接駆動して発火を実証する...")
        forced_item = {
            "rank": "forced_known_gloss", "used_form": "not fully match",
            "japanese_gloss": KNOWN_LEADING_TILDE_GLOSS,
            "japanese_gloss_tts": kwc.convert_display_gloss_to_tts_text(KNOWN_LEADING_TILDE_GLOSS),
        }
        with cl.logging_context("kp_display_tts_prod_wiring_01", "kp_ja_tts_b1b_forced"):
            forced_conversion_result = run_key_phrase_ja_tts(forced_item, narration_dir, "forced_leading_tilde_ja_charon")
        print(f"  forced_known_gloss: status={forced_conversion_result.get('status')} "
              f"conversion_fired={forced_conversion_result['conversion_fired']} "
              f"display={forced_conversion_result['display_gloss']!r} "
              f"tts_text={forced_conversion_result['japanese_gloss_tts_used']!r}")
        with open(f"{theme_out_dir}/audit/forced_leading_tilde_conversion_result.json", "w", encoding="utf-8") as f:
            json.dump(forced_conversion_result, f, ensure_ascii=False, indent=2, default=str)

    # (2) 数値placeholder型は変換されず、既存のplaceholder gateでTTS呼び出し
    # 自体を行わずにブロックされることを実証する(既知の実gloss入力)。
    print("[EVIDENCE] Step 3: 数値placeholder型(既知gloss)がgateでブロックされることを確認...")
    numeric_tts_text = kwc.convert_display_gloss_to_tts_text(KNOWN_NUMERIC_PLACEHOLDER_GLOSS)
    assert numeric_tts_text == KNOWN_NUMERIC_PLACEHOLDER_GLOSS, \
        f"数値placeholder型が変換されてしまった(仕様B違反): {numeric_tts_text!r}"
    numeric_out_path = f"{narration_dir}/numeric_placeholder_gate_check.wav"
    numeric_gate_result = tts_gen.generate_charon_japanese_with_reading_safety(
        numeric_tts_text, numeric_out_path, tts_gen.expected_substring_ja(numeric_tts_text))
    print(f"  status={numeric_gate_result.get('status')} reason={numeric_gate_result.get('reason')}")
    assert numeric_gate_result["status"] == "STOPPED", \
        f"数値placeholder型がgateでブロックされなかった: {numeric_gate_result}"
    assert not os.path.exists(numeric_out_path), \
        "数値placeholder型で音声ファイルが生成されてしまった(TTS API呼び出しが発生した可能性)"
    with open(f"{theme_out_dir}/audit/numeric_placeholder_gate_check_result.json", "w", encoding="utf-8") as f:
        json.dump({
            "display_gloss": KNOWN_NUMERIC_PLACEHOLDER_GLOSS, "tts_text_after_conversion": numeric_tts_text,
            "result": numeric_gate_result,
        }, f, ensure_ascii=False, indent=2, default=str)

    # (3) raw_usage_log.jsonl(er005_cost_logger、Production Gemini呼び出しを
    # 直接patchして記録する既存の公式ログ)から、実際のmodel_id/routing/
    # tts_execution_mode=STANDARDを抽出する(returnされたdictにはmodel情報を
    # 含まないため、公式cost logの実記録から確認する)。
    tts_api_calls = []
    with open(f"{OUT_DIR}/raw_usage_log.jsonl", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            if entry.get("api") == "models.generate_content(TTS)":
                tts_api_calls.append(entry)
    tts_model_ids = sorted({e.get("model_id") for e in tts_api_calls if e.get("model_id")})
    tts_execution_modes = sorted({e.get("tts_execution_mode") for e in tts_api_calls if e.get("tts_execution_mode")})
    print(f"[EVIDENCE] (3) raw_usage_log.jsonlより: TTS API呼び出し{len(tts_api_calls)}件、"
          f"model_id={tts_model_ids} tts_execution_mode={tts_execution_modes}")

    summary = {
        "article_id": ARTICLE_ID, "article_path": ARTICLE_PATH, "source_level": SOURCE_LEVEL,
        "tts_execution_mode_env": os.environ.get("TTS_EXECUTION_MODE"),
        "selection_status": sel_status, "canonicalization_status": canon_status,
        "redundancy_qa_status": redundancy_status,
        "natural_conversion_fired_in_selection": natural_conversion_fired,
        "forced_conversion_used": forced_conversion_result is not None,
        "numeric_placeholder_gate_blocked": numeric_gate_result["status"] == "STOPPED",
        "numeric_placeholder_no_tts_call_evidence": not os.path.exists(numeric_out_path),
        "canonicalization_artifact_path": canon_artifact_path,
        "tts_api_call_count": len(tts_api_calls),
        "tts_model_ids_observed": tts_model_ids,
        "tts_execution_modes_observed": tts_execution_modes,
    }
    with open(f"{OUT_DIR}/run_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print("[EVIDENCE] 完了。summary:", json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
