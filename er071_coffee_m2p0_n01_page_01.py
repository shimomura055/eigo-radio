# -*- coding: utf-8 -*-
"""FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01 委任_02: Coffee M2P0+N01 試聴ページ生成(Trial専用静的ページ、有料APIなし)。
出力: user_test/coffee_m2p0_n01_01/{index.html, audio/*.mp3}
内容: (1) Advanced 通し全編(M2P0 KP + N01 Full Story、Trial assemblerで組立) + timeline切出し (2) Standard Full Story 3 partの単体音声(N01+6%減速、
Production runner生成。StdはKP生成失敗のため完成版エピソードなし=参考clipのみ)。file:/// や C:\\ を含めない。"""
from __future__ import annotations
import os, sys, json, html, shutil

import soundfile as sf

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import er057_tone_trial_final_build_03_asm as A  # noqa: E402

esc = html.escape
B = os.path.join(ROOT, "er071_output", "m2p0_n01_production_wiring_01", "coffee_build_02")
RUN = os.path.join(ROOT, "er019_output", "family_x_audio_production_wiring_01", "coffee_prices__run_m2p0_n01_01")
WEB = os.path.join(ROOT, "user_test", "coffee_m2p0_n01_01")
AUD = os.path.join(WEB, "audio")


def rj(p):
    return json.load(open(p, encoding="utf-8"))


def main():
    os.makedirs(AUD, exist_ok=True)
    man = rj(os.path.join(B, "assembly_manifest_m2p0_n01_02.json"))["levels"]["adv"]
    x, sr = sf.read(os.path.join(ROOT, man["wav"]), dtype="float32")
    shutil.copyfile(os.path.join(ROOT, man["mp3"]), os.path.join(AUD, "Coffee_Advanced_m2p0_n01.mp3"))
    kp = sorted(rj(os.path.join(RUN, "b1b", "key_phrases", "keywords_canonicalized.json"))["items"], key=lambda it: it["rank"])
    kpres = rj(os.path.join(RUN, "b1b", "audit", "tts_generation_results.json"))["key_phrases"]
    parts = rj(os.path.join(RUN, "b1b", "parts.json"))
    rows, kpn = [], 0
    for e in man["timeline"]:
        part = e["part"]
        if part.startswith("pause"):
            continue
        s, d = e["start_seconds"], e["duration_seconds"]
        fn = f"adv_{len(rows):02d}.mp3"
        A.to_mp3(x[int(round(s * sr)): int(round((s + d) * sr))], os.path.join(AUD, fn), br="96k")
        pl = part.lower()
        note, body = "", ""
        if pl.startswith("key phrase "):
            kpn += 1
            it = kp[kpn - 1]
            body = f"<table class='kp'><tr><td>{esc(it['key_phrase'])}</td><td>{esc(str(kpres[str(it['rank'])]['explanation'].get('text', '')))}</td></tr></table>"
            note = "新KP(M2P0、Production runner生成。KP英語+P3英語解説)"
        elif pl.startswith("full story part"):
            n = int(part.split("Part ")[1][0])
            body = "<div class='script'>" + esc(parts[f"part{n}"]).replace("\n", "<br>") + "</div>"
            note = "N01(Production runner生成、Style sha d1956c91…、Advancedは減速なし)"
        else:
            note = "固定音源 / v5承認済み音声の再利用(Trial assembler経由)"
        rows.append((part, s, d, fn, note, body))
    std_clips = []
    for n in (1, 2, 3):
        src = os.path.join(RUN, "a2", "narration", f"full_story_part{n}.wav")
        fn = f"std_fs_part{n}.mp3"
        import subprocess
        subprocess.run([A.FFMPEG, "-y", "-loglevel", "error", "-i", src, "-ac", "1", "-b:a", "96k", os.path.join(AUD, fn)], check=True)
        std_clips.append((n, fn, rj(os.path.join(RUN, "a2", "parts.json"))[f"part{n}"]))
    css = """<style>body{font-family:sans-serif;max-width:1100px;margin:1em auto;padding:0 1em;line-height:1.5}table{border-collapse:collapse;width:100%;margin-bottom:1.5em}
th,td{border:1px solid #ccc;padding:6px;vertical-align:top;text-align:left}td.play{min-width:340px}td.play audio,audio{width:100%}.sec{color:#666;font-size:.85em}
.script{background:#f6f6f6;padding:4px;margin:3px 0;font-size:.95em}.note{background:#fff8e0;padding:3px;margin:3px 0;font-size:.85em}
.kp td{border:1px solid #ccc;padding:4px 10px;width:50%}.combo{background:#eef6ff;padding:10px;border:1px solid #99c;margin-bottom:1em}.warn{background:#fff0f0;padding:10px;border:1px solid #c66;margin-bottom:1em}</style>"""
    disc = ("<div class='warn'><b>開示</b><ul>"
            "<li>これはTrial用assemblerによる試聴版です(Production runnerの <code>--stage assemble</code>(M3 Gate/Audio Validation Gate)は通していません)。"
            "再生成部分(KP・Full Story)はProduction runner(<code>--style-profile coffee_n01_r2_p3</code>)で生成。</li>"
            "<li>Advanced: 新KP(M2P0)5件 + Full Story=N01。Preview/Comment/In One Line/固定音源はv5承認済み音声を再利用。M3 Gate(オフライン実行)=PASS。</li>"
            "<li>Standard: Key Phrase生成(M2P0)がCANONICALIZATION_INVALID(既存retry上限2回で不合格、KP再生成は1レベル1回の上限のため再実行せず)。"
            "よってStandardの完成版エピソードはありません。参考として Full Story N01音声(+6%減速)3 partのみ掲載します。Part2はN01の初回attempt不合格→"
            "minimal fallback(N01ではないtake)で合格のため、M3 GateではBLOCK(人間承認待ち)です。</li></ul></div>")
    trs = "".join(f"<tr><td><b>{esc(p)}</b><br><span class='sec'>{s:.1f}秒〜 ({d:.1f}秒)</span></td><td class='play'><audio controls preload='none' src='audio/{fn}'></audio></td>"
                  f"<td><div class='note'>{esc(note)}</div>{body}</td></tr>" for p, s, d, fn, note, body in rows)
    sc = "".join(f"<tr><td><b>Std Full Story Part {n}</b></td><td class='play'><audio controls preload='none' src='audio/{fn}'></audio></td>"
                 f"<td><div class='note'>N01 + 6%減速(Production runner生成)" + (" / 初回N01 attempt不合格のためminimal fallback take" if n == 2 else "") + f"</div><div class='script'>{esc(t).replace(chr(10), '<br>')}</div></td></tr>"
                 for n, fn, t in std_clips)
    pg = (f"<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><title>Coffee M2P0+N01 試聴</title><meta name='viewport' content='width=device-width, initial-scale=1'>{css}</head><body>"
          f"<h1>Coffee M2P0 + N01 試聴版</h1>{disc}"
          f"<h2 id='adv'>Advanced(通し全編 {man['duration_seconds']:.0f}秒)</h2><div class='combo'><audio id='main_adv' controls preload='none' src='audio/Coffee_Advanced_m2p0_n01.mp3'></audio></div>"
          f"<table><thead><tr><th>パート</th><th>音声</th><th>由来・Script</th></tr></thead><tbody>{trs}</tbody></table>"
          f"<h2 id='std'>Standard(参考: Full Story N01 + 6%減速のみ)</h2><table><thead><tr><th>パート</th><th>音声</th><th>由来・Script</th></tr></thead><tbody>{sc}</tbody></table>"
          "</body></html>")
    assert "file:///" not in pg and "C:\\" not in pg and "C:/" not in pg
    open(os.path.join(WEB, "index.html"), "w", encoding="utf-8").write(pg)
    print("page written", len(rows), "rows")


if __name__ == "__main__":
    main()
