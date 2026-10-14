# -*- coding: utf-8 -*-
"""FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01 委任_04: Coffee 完成版試聴ページ生成(有料APIなし)。
出力: user_test/coffee_m2p0_n01_final_03/{index.html, audio/*.mp3}
内容: Std/Advとも Production runner `--stage assemble` の正式assemble出力(Audio Validation Gate/M3通過)の通し全編 + timeline切出し +
Key Phrase表(最終英語KP / 日本語gloss / TTS読み) + WPM・文末ポーズ表(6%減速後Std WPM含む)。file:/// や C:\\ を含めない。"""
from __future__ import annotations
import html, json, os, subprocess, sys

import imageio_ffmpeg
import soundfile as sf

ROOT = os.path.dirname(os.path.abspath(__file__))
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
esc = html.escape
RUN = os.path.join(ROOT, "er019_output", "family_x_audio_production_wiring_01", "coffee_prices__run_m2p0_n01_01")
EV = os.path.join(ROOT, "er071_output", "m2p0_n01_production_wiring_01", "completion_04")
WEB = os.path.join(ROOT, "user_test", "coffee_m2p0_n01_final_03")
AUD = os.path.join(WEB, "audio")


def rj(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def mp3(wav_slice, sr, out, br="96k"):
    tmp = out + ".tmp.wav"
    sf.write(tmp, wav_slice, sr)
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", tmp, "-codec:a", "libmp3lame", "-b:a", br, out], check=True)
    os.remove(tmp)


def level_block(level_key, d, label, assembled_name, show_gloss):
    base = os.path.join(RUN, d)
    wav = os.path.join(base, "assembled", assembled_name)
    x, sr = sf.read(wav, dtype="float32")
    full = f"Coffee_{label}_final_03.mp3"
    mp3(x, sr, os.path.join(AUD, full), br="128k")
    tl = rj(os.path.join(base, "audit", "timeline.json"))
    parts = rj(os.path.join(base, "parts.json"))
    kp = sorted(rj(os.path.join(base, "key_phrases", "keywords_canonicalized.json"))["items"], key=lambda it: it["rank"])
    rows, kpn = [], 0
    for e in tl:
        part = e["part"]
        if part.startswith("pause"):
            continue
        s, dur = e["start_seconds"], e["duration_seconds"]
        fn = f"{level_key}_{len(rows):02d}.mp3"
        mp3(x[int(round(s * sr)): int(round((s + dur) * sr))] if x.ndim == 1 else x[int(round(s * sr)): int(round((s + dur) * sr)), :], sr,
            os.path.join(AUD, fn))
        pl = part.lower()
        body = ""
        if pl.startswith("key phrase ") and pl.split()[-1].isdigit():
            kpn += 1
            it = kp[kpn - 1]
            if show_gloss:
                body = (f"<table class='kp'><tr><th>英語KP</th><th>日本語gloss(表示)</th><th>TTS読み</th></tr><tr><td>{esc(it['key_phrase'])}</td>"
                        f"<td>{esc(str(it.get('japanese_gloss')))}</td><td>{esc(str(it.get('japanese_gloss_tts')))}</td></tr></table>")
            else:
                body = f"<table class='kp'><tr><th>英語KP(AdvはKP英語+英英解説。日本語glossは音声に使いません)</th></tr><tr><td>{esc(it['key_phrase'])}</td></tr></table>"
        elif pl.startswith("full story part"):
            n = int(part.split("Part ")[1][0]) if "Part " in part else int(pl.split("part")[1].strip()[0])
            body = "<div class='script'>" + esc(parts[f"part{n}"]).replace("\n", "<br>") + "</div>"
        rows.append((part, s, dur, fn, body))
    return full, x.shape[0] / sr, rows, kp


def main():
    os.makedirs(AUD, exist_ok=True)
    sp = rj(os.path.join(EV, "measure", "speed_pause_04.json"))
    adv_full, adv_dur, adv_rows, adv_kp = level_block("adv", "b1b", "Advanced", "Family_X_Audio_B1_COFFEE_PRICES.wav", False)
    std_full, std_dur, std_rows, std_kp = level_block("std", "a2", "Standard", "Family_X_Audio_A2_COFFEE_PRICES.wav", True)
    css = """<style>body{font-family:sans-serif;max-width:1100px;margin:1em auto;padding:0 1em;line-height:1.5}table{border-collapse:collapse;width:100%;margin-bottom:1.5em}
th,td{border:1px solid #ccc;padding:6px;vertical-align:top;text-align:left}td.play{min-width:340px}td.play audio,audio{width:100%}.sec{color:#666;font-size:.85em}
.script{background:#f6f6f6;padding:4px;margin:3px 0;font-size:.95em}.kp td,.kp th{border:1px solid #ccc;padding:4px 10px;width:33%}.combo{background:#eef6ff;padding:10px;border:1px solid #99c;margin-bottom:1em}
.note{background:#fff8e0;padding:8px;border:1px solid #cb8;margin-bottom:1em}.num td,.num th{text-align:right}.num td:first-child,.num th:first-child{text-align:left}</style>"""

    def metrics_row(key, name):
        lv = sp["levels"][key]
        return (f"<tr><td>{name}</td><td>{lv['total_wpm']}</td><td>{lv['total_words']}</td><td>{lv['total_dur_s']}</td>"
                f"<td>{lv['sentence_end_pause_mean_ms']}</td><td>{lv['sentence_end_pause_max_ms']}</td><td>{lv['n_long_silence_ge_800ms_total']}</td></tr>")

    ref = sp["trial_reference_values_NOT_a_production_gate"]
    metrics = ("<h2 id='metrics'>速度・文末ポーズ(Full Story 3 part合計、実測)</h2><table class='num'><thead><tr><th>Level</th><th>WPM</th><th>語数</th><th>総秒</th>"
               "<th>文末ポーズ平均(ms)</th><th>文末ポーズ最大(ms)</th><th>800ms以上の無音数</th></tr></thead><tbody>"
               + metrics_row("std", "Standard(N01 + 6%減速後)") + metrics_row("adv", "Advanced(N01、減速なし)")
               + "</tbody></table><div class='note'>参考値(Trial、<b>Productionの合否基準ではありません</b>): Std WPM "
               f"{ref['std_wpm_post_slowdown'][0]}±{ref['std_wpm_post_slowdown'][1]} / Adv WPM {ref['adv_wpm'][0]}±{ref['adv_wpm'][1]} / 文末ポーズ平均 Std&le;{ref['sentence_end_mean_ms_max']['std']}ms・"
               f"Adv&le;{ref['sentence_end_mean_ms_max']['adv']}ms / 800ms以上の無音&le;{ref['long_silence_ge_800ms_max']}。CURRENT_SPECはStd英語ナレーション約135WPMを『目安』(hard constraintではない)としています。"
               "聴感判断(速度・間・聴きやすさ)はこのページで行います(判断タイミング合意済み、UDR #49)。</div>")

    def table(rows):
        return "".join(
            f"<tr><td><b>{esc(p)}</b><br><span class='sec'>{s:.1f}秒〜 ({d:.1f}秒)</span></td><td class='play'><audio controls preload='none' src='audio/{fn}'></audio></td><td>{body}</td></tr>"
            for p, s, d, fn, body in rows)

    kp_hdr = "<thead><tr><th>パート</th><th>音声</th><th>Script / Key Phrase</th></tr></thead>"
    disc = ("<div class='note'><b>完成版(Production runner <code>--stage assemble</code>)</b>: Audio Validation Gate・M3(Style/Full Story)を通過した正式assemble出力です。"
            "Standardの最終Key Phrase『based on interviews』の日本語glossは、canonicalization後に最終KP基準で再整合(gloss alignment工程)した"
            "『インタビューをもとにした』(TTS読みも同じ)です。</div>")
    pg = (f"<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><title>Coffee 完成版試聴(final_03)</title><meta name='viewport' content='width=device-width, initial-scale=1'>{css}</head><body>"
          f"<h1>Coffee 完成版 試聴(Standard / Advanced)</h1>{disc}{metrics}"
          f"<h2 id='std'>Standard(通し全編 {std_dur:.0f}秒)</h2><div class='combo'><audio id='main_std' controls preload='none' src='audio/{std_full}'></audio></div>"
          f"<table>{kp_hdr}<tbody>{table(std_rows)}</tbody></table>"
          f"<h2 id='adv'>Advanced(通し全編 {adv_dur:.0f}秒)</h2><div class='combo'><audio id='main_adv' controls preload='none' src='audio/{adv_full}'></audio></div>"
          f"<table>{kp_hdr}<tbody>{table(adv_rows)}</tbody></table></body></html>")
    assert "file:///" not in pg and "C:\\" not in pg and "C:/" not in pg
    with open(os.path.join(WEB, "index.html"), "w", encoding="utf-8") as f:
        f.write(pg)
    print("page written", len(std_rows), len(adv_rows))


if __name__ == "__main__":
    main()
