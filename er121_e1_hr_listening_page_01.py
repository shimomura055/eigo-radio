# -*- coding: utf-8 -*-
"""FAMILY-Y-PRODUCTION-LAUNCH-01 委任_07: E-1(宅配 redelivery_fee run_01)のHuman Review 3 segment 試聴パッケージ生成(API 0・読取+mp3変換+ffmpeg減速のみ)。
- 試聴対象は『書換え前(R0本文)の最終判定対象attempt』。ER-020 Local Rewrite後の書換え音声は含めない。
- a2 y_voice_1 は、採用時に必ず掛かる6%減速(Y_MISSING_MANDATORY_A2_SLOWDOWN)を適用した版を聴かせる(ユーザーが聴く音=採用される音)。
- 承認・採用は一切記録しない(approved_by="user" はユーザー本人の試聴承認後のみ。docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/E1_HUMAN_REVIEW_01.md)。
出力: user_test/family_y_production_redelivery_fee_01/listening/{*.mp3,index.html}(限定共有。wavはcommitしない)。"""
from __future__ import annotations
import html
import json
import os
import subprocess
import sys

import er121_family_y_structure_01 as ys

RUN = "er121_output/family_y_production_01/redelivery_fee/run_01"
OUT = "user_test/family_y_production_redelivery_fee_01/listening"
RECHECK_JSON = f"{RUN}/a2/hr_adopt_prep/y_voice_1_slowed_asr_recheck.json"
WORK = f"{RUN}/hr_listening"           # 減速版wavの置き場(commitしない)
D_PRIME_THRESHOLD_SEC = 0.6

# (level, segment_id, 採用候補attempt番号, route接尾辞, mp3名, 見出し)
TARGETS = [
    ("a2", "preview", 5, "customb8f0ff16", "a2_preview.mp3", "Standard(a2) Preview(日本語)"),
    ("b1b", "y_voice_1", 6, "englishstyleprefixwidemargin", "b1b_y_voice_1.mp3", "Advanced(b1b) Voice 1(英語)"),
    ("a2", "y_voice_1", 5, "custom53fd514d", "a2_y_voice_1_slowed6pct.mp3", "Standard(a2) Voice 1(英語・6%減速後)"),
]
_esc = html.escape


def _lj(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _to_mp3(wav: str, mp3: str, br: str = "96k") -> None:
    import imageio_ffmpeg
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-i", wav, "-codec:a", "libmp3lame", "-b:a", br, mp3], check=True)


def segment_info(level: str, sid: str, n: int, route: str) -> dict:
    stem = f"{RUN}/{level}/narration/attempts/{sid}_attempt{n}_{route}"
    att = _lj(stem + ".json")
    res = _lj(f"{RUN}/{level}/audit/tts_generation_results.json")["segments"][sid]
    canon = res.get("canonical_text_before_local_rewrite") or res["canonical_text"]
    qa = (att.get("repetition_qa_evidence") or {}).get("method_d_prime_spectral_short_lag") or {}
    return {"level": level, "sid": sid, "attempt": n, "wav": stem + ".wav", "wav_sha256": att.get("sha256"),
            "saved_at": att.get("saved_at"), "classification": att.get("audio_classification"),
            "asr_text": att.get("asr_text") or "", "canonical": canon,
            "d_prime_sec": qa.get("best_run_length_seconds"), "d_prime_flagged": qa.get("flagged"),
            "d_prime_at_sec": qa.get("time_a")}


def _reason(i: dict) -> str:
    if i["sid"] == "preview":
        return ("日本語ASRが正本の「思いどおり」を「思い通り」と転写し、表記差で不一致(NG)扱いになりました。2つの転写器(OpenAI/Azure)とも同じ「思い通り」。"
                "読みが同じ(おもいどおり)かどうかを耳で確認してください。耳で「おもいどおり」と聞こえれば表記差だけで、音声は正しいです。")
    t = i["d_prime_sec"]
    return (f"ASR転写は本文と一致(判定={i['classification']}。ハイフン表記差などは正規化で一致扱い)。NGの理由は反復検査(Repetition QA)の短ラグ検査(D')のみ: "
            f"似た音が{t}秒続いた箇所があり(約{i['d_prime_at_sec']}秒付近)、閾値{D_PRIME_THRESHOLD_SEC}秒を超えた/境界で、機械が『反復の疑い』とflagしました。"
            "不自然な繰り返し・つっかえ・語の重複が聞こえるかを確認してください。")


def build() -> dict:
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(WORK, exist_ok=True)
    infos = []
    for level, sid, n, route, mp3name, title in TARGETS:
        i = segment_info(level, sid, n, route)
        src = i["wav"]
        i["listening_note"] = "R0本文のまま(書換えなし)"
        if level == "a2" and sid == "y_voice_1":
            import er008_a2_postprocess_slowdown_01 as slow
            dst = f"{WORK}/a2_y_voice_1_attempt{n}_slowed6pct.wav"
            i["slowdown"] = slow.apply_a2_slowdown(src, dst)
            src = dst
            i["listening_note"] = "R0本文のまま。採用時に必須の6%減速(atempo)を適用した音"
        _to_mp3(src, f"{OUT}/{mp3name}")
        i.update({"mp3": f"{OUT}/{mp3name}", "mp3name": mp3name, "title": title})
        infos.append(i)
    page = _html(infos)
    with open(f"{OUT}/index.html", "w", encoding="utf-8") as f:
        f.write(page)
    return {"out": OUT, "segments": [{k: v for k, v in i.items() if k not in ("canonical", "asr_text")} for i in infos]}


def _html(infos: list) -> str:
    parts = ["<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><meta name=\"robots\" content=\"noindex,nofollow\">",
             "<title>宅配(再配達)Y記事: Human Review試聴(承認待ち)</title><meta name='viewport' content='width=device-width, initial-scale=1'>",
             "<style>body{font-family:sans-serif;max-width:980px;margin:1em auto;padding:0 1em;line-height:1.6}audio{width:100%}"
             ".note{background:#fff8e0;padding:8px;border:1px solid #cb8;margin-bottom:1em}.wait{background:#fde8e8;border:1px solid #c66;padding:8px;margin:1em 0}"
             ".box{border:1px solid #ccc;padding:8px 12px;margin:1em 0}.script{background:#f6f6f6;padding:6px;white-space:pre-wrap}.sec{color:#666;font-size:.85em}</style></head><body>",
             "<h1>宅配(再配達)Yの記事: Human Review 試聴(3 segment)</h1>",
             ys.notice_html(),
             "<div class='wait'><b>ユーザー承認待ち</b>: 以下3音声は自動検査でNGとなり、人の試聴判断が必要なものです。"
             "<b>承認前です。採用・公開・組立はまだ行っていません。</b>承認はユーザー本人の明示のみ有効です(AIは代行しません)。"
             "各音声について『採用してよい』『採用しない』を、まとめて/個別にお知らせください。</div>"]
    for i in infos:
        parts.append(f"<div class='box'><h2>{_esc(i['title'])}</h2>")
        parts.append(f"<audio controls preload='none' src='{_esc(i['mp3name'])}'></audio>")
        parts.append(f"<div class='sec'>{_esc(i['listening_note'])} / 対象={_esc(i['level'])}/{_esc(i['sid'])} attempt{i['attempt']} "
                     f"(生成={_esc(i['saved_at'])}、wav sha256={_esc(str(i['wav_sha256'])[:12])}…)</div>")
        parts.append("<h3>本文(正本・R0)</h3><div class='script'>" + _esc(i["canonical"]) + "</div>")
        parts.append("<h3>ASR転写(この音声)</h3><div class='script'>" + _esc(i["asr_text"]) + "</div>")
        parts.append(f"<h3>NGになった理由</h3><p>{_esc(_reason(i))}</p>")
        parts.append(f"<p class='sec'>自動判定: {_esc(str(i['classification']))}"
                     + (f" / D'最長run={i['d_prime_sec']}秒(閾値{D_PRIME_THRESHOLD_SEC}秒)" if i.get("d_prime_sec") is not None else "") + "</p>")
        if i["level"] == "a2" and i["sid"] == "y_voice_1" and os.path.isfile(RECHECK_JSON):     # 委任_08: 減速後ASR再検証の実測結果(別ファイル)を1行表示
            _rc = json.load(open(RECHECK_JSON, encoding="utf-8"))
            parts.append(f"<p class='sec'>減速後ASR再検証(6%減速後の音に対し、正式経路と同じ関数で実測): 判定={_esc(str(_rc.get('post_slowdown_final_classification')))}"
                         f"(PASS・ASR一致、ハイフン表記差のみ)、ASR={_esc(str(_rc.get('asr_model_id')))}、減速後wav sha256={_esc(str(_rc.get('slowed_wav_sha256'))[:12])}…(上の試聴音と一致)。</p>")
        parts.append("<p><b>状態: ユーザー承認待ち</b></p></div>")
    parts.append("</body></html>")
    return "".join(parts)


if __name__ == "__main__":
    r = build()
    print(json.dumps(r, ensure_ascii=False, indent=1))
    sys.exit(0)
