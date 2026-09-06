# ============================================================
# er011_tts_attempt_audio_retention_wiring_01_runtime_evidence.py
# ER-011-TTS-ATTEMPT-AUDIO-RETENTION-PRODUCTION-WIRING-01: runtime evidence
# ============================================================
# 目的: attempt音声保全のProduction配線が実Production経路で実際に発火する
# ことを、TTS Standard同期(TTS_EXECUTION_MODE=STANDARD、PM_GOVERNANCE 7-1
# に従い正式リリース前は既定でStandard同期)で1回ずつ実行し確認する。
#
# (1) 英語Key Phrase Component: repro01.generate_key_phrase_component_
#     verified("new normal", ...) — ASR不一致を起こしやすいことが
#     KEYPHRASE-EN-TTS-ROOTCAUSE-DIAGNOSTIC-01で確認済みの実例。
# (2) 日本語gloss: n3_tts.generate_a2_japanese_with_fallback(...) —
#     通常PASSする短い日本語フレーズ。
#
# 出力先: er011_output/tts_attempt_audio_retention_wiring_01/
# Production関数はいずれも無変更で直接呼び出す(monkeypatchなし)。
from __future__ import annotations

import hashlib
import json
import os

os.environ["TTS_EXECUTION_MODE"] = "STANDARD"

import er003_v1_n3_01_tts_generate as n3_tts
import er003_v1_repro01_main_generate as repro01
import er011_human_review_lock_01 as review_lock

OUT_ROOT = "er011_output/tts_attempt_audio_retention_wiring_01"
THEME = "evidence01"
LEVEL = "a2"
NARRATION_DIR = f"{OUT_ROOT}/{THEME}/{LEVEL}/narration"


def _sha256(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _list_attempts(segment_id: str) -> list:
    attempts_dir = f"{NARRATION_DIR}/attempts"
    if not os.path.isdir(attempts_dir):
        return []
    out = []
    for fname in sorted(os.listdir(attempts_dir)):
        if fname.startswith(f"{segment_id}_attempt") and fname.endswith(".wav"):
            wav_path = f"{attempts_dir}/{fname}"
            json_path = wav_path[:-4] + ".json"
            record = {}
            if os.path.exists(json_path):
                with open(json_path, encoding="utf-8") as f:
                    record = json.load(f)
            out.append({
                "wav_filename": fname,
                "wav_path": wav_path,
                "sha256": _sha256(wav_path),
                "json": record,
            })
    return out


def run() -> dict:
    os.makedirs(NARRATION_DIR, exist_ok=True)
    results = {}

    # ------------------------------------------------------------
    # (1) 英語Key Phrase Component: "new normal"
    # ------------------------------------------------------------
    en_out_path = f"{NARRATION_DIR}/kp_new_normal.wav"
    en_result = repro01.generate_key_phrase_component_verified("new normal", en_out_path)
    en_attempts = _list_attempts("kp_new_normal")
    en_final_sha256 = _sha256(en_out_path) if os.path.exists(en_out_path) else None
    results["english_key_phrase"] = {
        "text": "new normal", "out_path": en_out_path,
        "status": en_result.get("status"), "asr_verified": en_result.get("asr_verified"),
        "final_out_path_sha256": en_final_sha256,
        "attempt_files": [
            {"wav_filename": a["wav_filename"], "sha256": a["sha256"],
             "route": a["json"].get("route"), "asr_text": a["json"].get("asr_text"),
             "verified": a["json"].get("verified"),
             "tts_execution_mode": a["json"].get("tts_execution_mode"),
             "model": a["json"].get("model"), "attempt_number": a["json"].get("attempt_number")}
            for a in en_attempts
        ],
    }

    # ------------------------------------------------------------
    # (2) 日本語gloss(通常PASSする短いフレーズ)
    # ------------------------------------------------------------
    ja_out_path = f"{NARRATION_DIR}/gloss_new_normal.wav"
    ja_result = n3_tts.generate_a2_japanese_with_fallback(
        "新しい当たり前", ja_out_path, "新しい")
    ja_attempts = _list_attempts("gloss_new_normal")
    ja_final_sha256 = _sha256(ja_out_path) if os.path.exists(ja_out_path) else None
    results["japanese_gloss"] = {
        "text": "新しい当たり前", "out_path": ja_out_path,
        "status": ja_result.get("status"), "asr_verified": ja_result.get("asr_verified"),
        "final_out_path_sha256": ja_final_sha256,
        "attempt_files": [
            {"wav_filename": a["wav_filename"], "sha256": a["sha256"],
             "route": a["json"].get("route"), "asr_text": a["json"].get("asr_text"),
             "verified": a["json"].get("verified"),
             "tts_execution_mode": a["json"].get("tts_execution_mode"),
             "model": a["json"].get("model"), "attempt_number": a["json"].get("attempt_number")}
            for a in ja_attempts
        ],
    }

    with open(f"{OUT_ROOT}/runtime_evidence_summary.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    _write_player_html(results)
    return results


def _rel(path: str) -> str:
    return os.path.relpath(path, NARRATION_DIR).replace("\\", "/")


def _write_player_html(results: dict) -> None:
    def block(title, r):
        rows = []
        for a in r["attempt_files"]:
            rows.append(
                f'<div class="box"><div class="label">attempt {a["attempt_number"]} '
                f'(route={a["route"]}, tts_execution_mode={a["tts_execution_mode"]}, '
                f'model={a["model"]})</div>'
                f'<audio controls src="attempts/{a["wav_filename"]}"></audio>'
                f'<p class="note">ASR raw: <code>{a["asr_text"]}</code> / verified={a["verified"]} / '
                f'sha256={a["sha256"][:16]}...</p></div>'
            )
        final_name = os.path.basename(r["out_path"])
        return f"""
<h2>{title}</h2>
<p class="note">text=<code>{r['text']}</code> / final status={r['status']} / asr_verified={r['asr_verified']}</p>
<div class="box"><div class="label">最終成果物(out_path) — sha256={ (r['final_out_path_sha256'] or '')[:16] }...</div>
<audio controls src="{final_name}"></audio></div>
{''.join(rows)}
"""

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head><meta charset="UTF-8">
<title>ER-011-TTS-ATTEMPT-AUDIO-RETENTION-PRODUCTION-WIRING-01: runtime evidence</title>
<style>
  body {{ font-family: sans-serif; max-width: 820px; margin: 40px auto; line-height: 1.6; }}
  h1 {{ font-size: 1.2em; }} h2 {{ font-size: 1.05em; margin-top: 28px; }}
  .box {{ border: 1px solid #ccc; border-radius: 8px; padding: 12px; margin-bottom: 12px; }}
  .label {{ font-weight: bold; margin-bottom: 6px; }}
  .note {{ color: #555; font-size: 0.9em; }}
  code {{ background: #f0f0f0; padding: 2px 4px; }}
</style></head>
<body>
<h1>ER-011-TTS-ATTEMPT-AUDIO-RETENTION-PRODUCTION-WIRING-01 runtime evidence</h1>
<p class="note">Production関数(repro01.generate_key_phrase_component_verified /
n3_tts.generate_a2_japanese_with_fallback)を無変更のまま、TTS_EXECUTION_MODE=STANDARDで
実行した結果。各attemptの音声が上書きされず個別に残っていることを確認できます。</p>
{block("(1) 英語Key Phrase Component: new normal", results["english_key_phrase"])}
{block("(2) 日本語gloss: 新しい当たり前", results["japanese_gloss"])}
</body></html>
"""
    with open(f"{NARRATION_DIR}/player.html", "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    r = run()
    print(json.dumps(r, ensure_ascii=False, indent=2, default=str))
