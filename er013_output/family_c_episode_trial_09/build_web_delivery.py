# ============================================================
# er013_output/family_c_episode_trial_09/build_web_delivery.py
# 管理ID: USER-TEST-AUDIO-COMPLETION-01-FAMILYC
# ============================================================
# 目的: Family C Trial-09(VALIDATED、home_robots)の既存採用済み完成音声
# (assembled wav)・個別segment音声(38件)を、GitHub上でWeb再生可能な形へ
# 単純変換する。音声内容・Voice構成・Preview・Key Phrase・support・Story
# 本文・segment構成は一切変更しない(再生成禁止、新規TTS/ASR API呼び出し
# なし、追加費用¥0)。
#
# 変換手段: 既存前例(er011_open145_towels_trial11_a2_mp3_export_01.py::
# export_mp3()、元は er003_v1_b1_scaffold_audio_01_generate.py)と同じ
# soundfile.write(..., format="MP3")を再利用する(新規pip installなし、
# venv既存のsoundfile/libsndfile MPEG-1/2 Audioサポートを使用)。
#
# player.html再生成: 既存共通module audio_review_player.py
# (PM-GOVERNANCE-AUDIO-REVIEW-PLAYER-STANDARD-FORMAT-11準拠)をそのまま
# 再利用し、er013_family_c_episode_trial_09_run.py::build_player_html()と
# 同じ行構成ロジックを、既存JSON(segments.json/keywords_canonicalized.json/
# audit/run_summary_assemble.json/preview.txt/support_ja.md)から再構成する。
# 音声生成・アセンブルは一切行わない(既存wavを読み込んでmp3化するのみ)。
from __future__ import annotations

import json
import os

import soundfile as sf

import audio_review_player as player_mod

OUT_DIR = "er013_output/family_c_episode_trial_09/home_robots"
AUDIO_DIR = f"{OUT_DIR}/audio"
WEB_DIR = f"{OUT_DIR}/web"
WEB_SEG_DIR = f"{WEB_DIR}/segments"
ASSEMBLED_WAV = f"{OUT_DIR}/assembled/family_c_home_robots_trial_09.wav"
ASSEMBLED_MP3_NAME = "family_c_home_robots_trial_09.mp3"

TOPIC_INTRO_EN_TEXT = "Home Robots"
TOPIC_INTRO_JA_TEXT = "ホームロボット"


def convert_one(wav_path: str, mp3_path: str) -> dict:
    data, sr = sf.read(wav_path)
    sf.write(mp3_path, data, sr, format="MP3")
    wav_bytes = os.path.getsize(wav_path)
    mp3_bytes = os.path.getsize(mp3_path)
    info = sf.info(mp3_path)
    return {
        "wav_path": wav_path, "mp3_path": mp3_path,
        "wav_bytes": wav_bytes, "mp3_bytes": mp3_bytes,
        "sample_rate": sr, "channels": (data.shape[1] if data.ndim > 1 else 1),
        "duration_seconds": round(info.frames / info.samplerate, 3),
    }


def convert_all() -> dict:
    os.makedirs(WEB_DIR, exist_ok=True)
    os.makedirs(WEB_SEG_DIR, exist_ok=True)

    results = []
    # 1) 完成episode
    ep_mp3 = f"{WEB_DIR}/{ASSEMBLED_MP3_NAME}"
    results.append({"kind": "episode", **convert_one(ASSEMBLED_WAV, ep_mp3)})

    # 2) 個別segment音声(38件、audio/配下の*.wavすべて)
    wav_names = sorted(
        n for n in os.listdir(AUDIO_DIR) if n.endswith(".wav")
    )
    for name in wav_names:
        stem = name[:-4]
        wav_path = f"{AUDIO_DIR}/{name}"
        mp3_path = f"{WEB_SEG_DIR}/{stem}.mp3"
        results.append({"kind": "segment", "segment_id": stem, **convert_one(wav_path, mp3_path)})

    return {"episode_mp3": ep_mp3, "segment_count": len(wav_names), "conversions": results}


def _load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def build_player_html_relative() -> None:
    """既存build_player_html()と同じ行構成ロジックを、相対パス(mp3)で
    再構成する。音声生成・アセンブルは行わない(既存JSONを読むだけ)。"""
    segments = _load_json(f"{OUT_DIR}/segments.json")
    kp_data = _load_json(f"{OUT_DIR}/key_phrases/keywords_canonicalized.json")
    run_summary = _load_json(f"{OUT_DIR}/audit/run_summary_assemble.json")
    preview_text = _load_text(f"{OUT_DIR}/preview.txt")
    support_md = _load_text(f"{OUT_DIR}/support_ja.md")

    # support_ja.md の2セクションから本文だけを抽出(見出し行を除く非空行)。
    support_lines = [ln.strip() for ln in support_md.splitlines() if ln.strip()]
    support_paragraphs = [ln for ln in support_lines if not ln.startswith("##")]
    support_1_text, support_2_text = support_paragraphs[0], support_paragraphs[1]

    seg_by_id = {s["id"]: s for s in segments}
    kp_by_rank = {it["rank"]: it for it in kp_data["items"]}
    label_to_text = {
        "topic_intro_en": (TOPIC_INTRO_EN_TEXT, "narrator(Aoede)"),
        "topic_intro_ja": (TOPIC_INTRO_JA_TEXT, "narrator(Aoede)"),
        "preview_ja": (preview_text, "narrator(Aoede)"),
        "support_1_ja": (support_1_text, "narrator(Aoede)"),
        "support_2_ja": (support_2_text, "narrator(Aoede)"),
    }

    def rel_seg_url(stem: str) -> str:
        return f"./web/segments/{stem}.mp3"

    rows = []
    for entry in run_summary["timeline"]:
        name = entry["part"]
        start = entry["start_seconds"]
        if name.startswith("_silence_"):
            continue
        if name.startswith("key_phrase_"):
            rank = int(name.split("_")[-1])
            it = kp_by_rank[rank]
            script = f"{rank}. {it['used_form']} / {it.get('japanese_gloss')}"
            audio_urls = [rel_seg_url(f"kp{rank}_number"), rel_seg_url(f"kp{rank}_english"),
                          rel_seg_url(f"kp{rank}_japanese")]
            audio_html = player_mod.render_single_audio_html(audio_urls)
            rows.append(player_mod.render_timeline_row(start, name, "Aoede(number/en/ja gloss)",
                                                         script, audio_html))
            continue
        if name in label_to_text:
            text, voice_disp = label_to_text[name]
            audio_html = player_mod.render_single_audio_html(rel_seg_url(name))
            rows.append(player_mod.render_timeline_row(start, name, voice_disp, text, audio_html))
            continue
        seg = seg_by_id.get(name)
        if seg is not None:
            voice_disp = "Aoede(narrator)" if seg["voice"] == "narrator" else "Charon(robot)"
            audio_html = player_mod.render_single_audio_html(rel_seg_url(name))
            rows.append(player_mod.render_timeline_row(start, name, voice_disp, seg["tts_text"], audio_html))

    table_html = player_mod.render_timeline_table(rows)
    episode_url = f"./web/{ASSEMBLED_MP3_NAME}"
    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>Family C Trial-09: Home Robots</title>
<style>{player_mod.PLAYER_STANDARD_CSS}</style>
<script>{player_mod.SEEK_SCRIPT}</script>
</head><body>
<h1>Family C Future — Home Robots(Trial-09完成episode候補 / Level: A2)</h1>
<p>duration={run_summary['duration_seconds']}s / peak={run_summary['peak_after_headroom']}</p>
<audio id="episode_audio" class="main" controls preload="none" src="{episode_url}"></audio>
{table_html}
</body></html>"""
    with open(f"{OUT_DIR}/player.html", "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    conv_result = convert_all()
    build_player_html_relative()
    with open(f"{OUT_DIR}/web_delivery.json", "w", encoding="utf-8") as f:
        json.dump(conv_result, f, ensure_ascii=False, indent=2)
    print(f"[WEB-DELIVERY] episode_mp3={conv_result['episode_mp3']} "
          f"segments={conv_result['segment_count']}")
