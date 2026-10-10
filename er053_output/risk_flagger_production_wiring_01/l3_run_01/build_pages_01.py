# -*- coding: utf-8 -*-
"""RISK-FLAGGER-PRODUCTION-WIRING-01 delegation 18: L3 coffee_prices listening page build.
No API calls; local conversion/static generation only.
wav->mp3 uses the same procedure as er014 build_web_player_common.wav_to_mp3
(soundfile, format=MP3, default bitrate).
Run from repo root with .venv python (PYTHONUTF8=1)."""
import html, json, os, re, soundfile as sf

R = "er019_output/family_x_audio_production_wiring_01/coffee_prices__run_l3_01"
OUT = "user_test/coffee_prices_l3_01"
EV = "er053_output/risk_flagger_production_wiring_01/l3_run_01"
LV = {"a2": ("Standard", "Family_X_Audio_A2_COFFEE_PRICES.wav"),
      "b1b": ("Advanced", "Family_X_Audio_B1_COFFEE_PRICES.wav")}
E = html.escape
FILE = "file:///C:/Users/tensh/eigo-radio/" + R + "/"


def wav2mp3(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    d, sr = sf.read(src)
    sf.write(dst, d, sr, format="MP3")


def dur(path):
    i = sf.info(path)
    return round(i.frames / i.samplerate, 3)


player = open(f"{R}/player.html", encoding="utf-8").read()
head = player[:player.index("<body>")]
body = player[player.index("<body>") + 6:]
sec = {"b1b": body[body.index("<h2>Advanced"):body.index("<h2>Standard")],
       "a2": body[body.index("<h2>Standard"):]}
sec = {k: v.replace("</body>", "").replace("</html>", "") for k, v in sec.items()}

manifest = {}
ep_dur = {}
for lv, (lab, wav) in LV.items():
    s = sec[lv]
    if lv == "b1b":
        # player template labelled Advanced KP rows voice=Charon, but tts_generation_results.json shows Aoede (english and explanation)
        s = re.sub(r'(Key Phrase \d</b><br><small>voice=)Charon', r'\1Aoede', s)
        # Advanced KP: display only. "EN / EXPLANATION" slash form -> unified.html kpParts() 2 columns, no label strings.
        s = re.sub(r'EN: ([^<]*)<br>EXPLANATION: ([^<]*)<br>EN \(repeat[^<]*\): [^<]*</td>', r'\1 / \2</td>', s)
    ep_src = f"{R}/{lv}/assembled/{wav}"
    wav2mp3(ep_src, f"{OUT}/{lv}/web/episode.mp3")
    ep_dur[lv] = dur(ep_src)
    s = s.replace(FILE + f"{lv}/assembled/{wav}", "web/episode.mp3")
    rx = re.compile(r'src="' + re.escape(FILE) + lv + r'/narration/([A-Za-z0-9_]+)\.wav"')
    segs = sorted(set(rx.findall(s)))
    for n in segs:
        wav2mp3(f"{R}/{lv}/narration/{n}.wav", f"{OUT}/{lv}/web/segments/{n}.mp3")
    s = rx.sub(r'src="web/segments/\1.mp3"', s)
    assert "file:///" not in s and "C:\\" not in s, lv
    h = head.replace("NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01 player(coffee_prices)", f"Coffee Prices L3 - {lab}")
    page = (h + f'<body>\n<h1>Coffee Prices (L3 run_l3_01, Production) - {lab}</h1>\n' + s + "\n</body></html>\n")
    with open(f"{OUT}/{lv}/player.html", "w", encoding="utf-8", newline="\n") as f:
        f.write(page)
    manifest[lv] = {"segment_mp3": segs}
with open(f"{EV}/pages_build_manifest_01.json", "w", encoding="utf-8") as f:
    json.dump({"episode_duration_sec": ep_dur, **manifest}, f, ensure_ascii=False, indent=2)

# ---------- index.html (same composition as user_test/family_x_refresh_e2e_01/index.html) ----------
ep = json.load(open(f"{R}/entry_point.json", encoding="utf-8"))
ja_title = ep["japanese_title"]
order = ["topic_intro", "japanese_title", "preview", "comment_1", "comment_2", "comment_3", "comment_4",
         "full_story_part1", "full_story_part2", "full_story_part3", "in_one_line"]


def seg_table(res, lv):
    o = ['<table class="seg"><thead><tr><th>segment</th><th>status</th><th>model</th><th>voice</th>'
         '<th>duration(sec)</th><th>ASR verified</th><th>style_prefix(全文)</th></tr></thead><tbody>']
    n = 0
    for k in order:
        v = res["segments"].get(k)
        if not v:
            continue
        n += 1
        d = v.get("duration_seconds")
        if d is None:
            d = dur(f"{R}/{lv}/narration/{k}.wav")
        sp = E(v.get("style_prefix", "")).replace("\n", "<br>")
        o.append(f'<tr><td>{k}</td><td>{v["status"]}</td><td>{E(v["model"])}</td><td>{E(v["voice"])}</td>'
                 f'<td>{d}</td><td>{v.get("asr_verified")}</td><td class="style">{sp}</td></tr>')
    o.append("</tbody></table>")
    return "\n".join(o), n


def shell_table(res):
    o = ['<table class="seg"><thead><tr><th>shell</th><th>status</th><th>reused</th>'
         '<th>master_audio_id(本run)</th></tr></thead><tbody>']
    for k, v in res["shared_narration"].items():
        o.append(f'<tr><td>{k}</td><td>{v["status"]}</td><td>{v.get("reused")}</td><td>{v.get("master_audio_id")}</td></tr>')
    o.append("</tbody></table>")
    return "\n".join(o)


b1p = sec["b1b"]


def adv_phrase(r):
    m = re.search(r"Key Phrase %d</b>.*?EN: (.*?)<br>" % r, b1p, re.S)
    return E(m.group(1)) if m else "(未取得)"


parts = []
nseg = {}
for lv, (lab, wav) in LV.items():
    res = json.load(open(f"{R}/{lv}/audit/tts_generation_results.json", encoding="utf-8"))
    st, n = seg_table(res, lv)
    nseg[lv] = n
    sp = f'<h2>Coffee Prices: {lab}</h2>\n<audio controls preload="none" src="{lv}/web/episode.mp3"></audio>\n'
    sp += (f'<p class="meta">duration: {ep_dur[lv]}s / clipping: False / segment数: {n} / '
           f'tts_backend: {res["tts_backend"]} / style_version: {res["style_version"]}</p>\n')
    sp += f"<h3>可変segment一覧({lab})</h3>\n{st}\n"
    kp = res["key_phrases"]
    if lv == "a2":
        sp += (f'<h3>Key Phrase構造({lab}: Phrase to 日本語意味[J3] to 同一Phrase再生)</h3>\n'
               '<table class="seg"><thead><tr><th>rank</th><th>Phrase(英語)</th><th>english status</th>'
               '<th>english reused / master_audio_id</th><th>日本語意味(J3)</th><th>style_prefix(全文)</th>'
               '<th>status</th></tr></thead><tbody>\n')
        for r in sorted(kp, key=int):
            e, j = kp[r]["english"], kp[r]["japanese_meaning"]
            sp += (f'<tr><td>{r}</td><td>{E(e["text"])}</td><td>{e["status"]}</td>'
                   f'<td>{e.get("reused")} / {e.get("master_audio_id")}</td><td>{E(j["text"])}</td>'
                   f'<td class="style">{E(j["style_prefix"])}</td><td>{j["status"]}</td></tr>\n')
        sp += "</tbody></table>\n"
    else:
        sp += (f'<h3>Key Phrase構造({lab}: Phrase to 英語解説[Variant B] to 同一Phrase再生)</h3>\n'
               '<table class="seg"><thead><tr><th>rank</th><th>Phrase(英語)</th>'
               '<th>english reused / master_audio_id</th><th>解説(explanation、全文)</th>'
               '<th>style_prefix(全文)</th><th>解説 voice</th><th>phrase_repeat検証</th></tr></thead><tbody>\n')
        for r in sorted(kp, key=int):
            e, x, pr = kp[r]["english"], kp[r]["explanation"], kp[r]["phrase_repeat"]
            same = (pr.get("path") == e.get("path")) and (pr.get("master_audio_id") == e.get("master_audio_id"))
            sp += (f'<tr><td>{r}</td><td>{adv_phrase(int(r))}</td><td>{e.get("reused")} / {e.get("master_audio_id")}</td>'
                   f'<td>{E(x["text"])}</td><td class="style">{E(x["style_prefix"])}</td><td>{E(x["voice"])}</td>'
                   f'<td>phrase_repeat = english と同一path/master_audio_id: {same}</td></tr>\n')
        sp += "</tbody></table>\n"
    en_styles = {}
    for r in sorted(kp, key=int):
        sx = kp[r]["english"].get("style_prefix")
        if sx:
            en_styles.setdefault(sx, []).append(r)
    sp += '<p class="meta">Key Phrase 英語component(Phrase本体)のstyle_prefix(全文、master reuse分はreuse元のstyleのためここには出ない):</p>\n<table class="seg"><thead><tr><th>rank</th><th>style_prefix(全文)</th></tr></thead><tbody>\n'
    for sx, rk in en_styles.items():
        sp += f'<tr><td>{",".join(rk)}</td><td class="style">{E(sx).replace(chr(10), "<br>")}</td></tr>\n'
    sp += "</tbody></table>\n"
    sp += "<h3>固定shell Champion(Production Master Store)</h3>\n" + shell_table(res) + "\n"
    parts.append(sp)

page = f'''<!DOCTYPE html>
<html lang="ja"><head><meta charset="utf-8">
<title>Coffee Prices L3 run_l3_01 (Production正式経路)</title>
<style>
body {{ font-family: "Meiryo","Hiragino Kaku Gothic ProN",sans-serif; max-width: 1200px; margin: 2em auto; line-height:1.6; color:#111; padding: 0 1em; }}
h1 {{ font-size: 1.4em; }}
h2 {{ border-bottom: 2px solid #333; padding-bottom:4px; margin-top:2em; }}
h3 {{ margin-top:1.5em; border-left:6px solid #888; padding-left:8px; }}
.note {{ background:#fffbe6; border:1px solid #e0d080; padding:10px 14px; font-size:0.92em; margin:14px 0; }}
audio {{ width:100%; min-width:360px; height:36px; display:block; margin:8px 0; }}
table.seg {{ border-collapse: collapse; width: 100%; margin: 8px 0 22px 0; font-size: 0.83em; }}
table.seg th, table.seg td {{ border: 1px solid #ccc; padding: 5px 7px; vertical-align: top; text-align:left; }}
table.seg th {{ background:#f0f0f0; }}
td.style {{ max-width: 340px; }}
p.meta {{ font-size:0.85em; color:#444; }}
</style></head>
<body>
<h1>Coffee Prices(コーヒー価格はなぜ上がっている?)L3 run_l3_01(Production正式経路、Standard/Advanced完成)</h1>
<div class="note">
管理ID: <b>RISK-FLAGGER-PRODUCTION-WIRING-01</b>(委任_18、2026-10-11)。日本語タイトル: {E(ja_title)}。
本ページは最終L3(Family X Production正式経路、<code>er019_family_x_audio_production_runner_01.py</code>、
<code>--tts-backend speech_metadata_flash_lite</code>)で生成した完成音声のStandard/Advancedです。
<code>PRODUCTION_WIRED</code>の最終判定は人間ユーザー承認であり、本ページはevidence配布のみです。
</div>
{chr(10).join(parts)}
</body></html>
'''
with open(f"{OUT}/index.html", "w", encoding="utf-8", newline="\n") as f:
    f.write(page)
print("done", ep_dur, nseg)
