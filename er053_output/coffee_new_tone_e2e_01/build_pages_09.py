# -*- coding: utf-8 -*-
"""FAMILY-X-COFFEE-NEW-TONE-PRODUCTION-E2E-01 delegation 09 final (Advanced+Standard complete): listening page build.
No API calls; local conversion/static generation only (based on er053_output/risk_flagger_production_wiring_01/l3_run_01/build_pages_01.py).
Run from repo root with .venv python (PYTHONUTF8=1).
Advanced = complete episode (assembled). Standard = HUMAN_REVIEW stop at full_story_part2 -> passed segments only, no episode (marked 未取得)."""
import html, json, os, re, soundfile as sf

R = "er019_output/family_x_audio_production_wiring_01/coffee_prices__run_e_tone_01"
OUT = "user_test/coffee_new_tone_01"
EV = "er053_output/coffee_new_tone_e2e_01"
E = html.escape
FILE = "file:///C:/Users/tensh/eigo-radio-tone/" + R + "/"
ORDER = ["topic_intro", "japanese_title", "preview", "comment_1", "comment_2", "comment_3", "comment_4",
         "full_story_part1", "full_story_part2", "full_story_part3", "in_one_line"]


def wav2mp3(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    d, sr = sf.read(src)
    sf.write(dst, d, sr, format="MP3")


def dur(path):
    i = sf.info(path)
    return round(i.frames / i.samplerate, 3)


def style_src(v):
    al = v.get("attempts_log") or []
    s = v.get("style_source") or (al[-1].get("style_source") if al else None)
    if s is None and v.get("fallback_attempts_log"):
        s = v["fallback_attempts_log"][-1].get("style_source")
    return s or "(従来値: 本件対象外role)"


def n_attempts(v):
    return len(v.get("attempts_log") or []) or (len(v.get("standard_attempts_log") or []) + len(v.get("fallback_attempts_log") or []))


player = open(f"{R}/player.html", encoding="utf-8").read()
head = player[:player.index("<body>")]
body = player[player.index("<body>") + 6:]
b1s = body[body.index("<h2>Advanced"):body.index("<h2>Standard")]

manifest = {}
# ---------------- Advanced (complete) ----------------
lv, lab, wav = "b1b", "Advanced", "Family_X_Audio_B1_COFFEE_PRICES.wav"
s = re.sub(r'(Key Phrase \d</b><br><small>voice=)Charon', r'\1Aoede', b1s)
s = re.sub(r'EN: ([^<]*)<br>EXPLANATION: ([^<]*)<br>EN \(repeat[^<]*\): [^<]*</td>', r'\1 / \2</td>', s)
ep_src = f"{R}/{lv}/assembled/{wav}"
wav2mp3(ep_src, f"{OUT}/{lv}/web/episode.mp3")
ep_dur = {lv: dur(ep_src)}
s = s.replace(FILE + f"{lv}/assembled/{wav}", "web/episode.mp3")
rx = re.compile(r'src="' + re.escape(FILE) + lv + r'/narration/([A-Za-z0-9_]+)\.wav"')
segs = sorted(set(rx.findall(s)))
for n in segs:
    wav2mp3(f"{R}/{lv}/narration/{n}.wav", f"{OUT}/{lv}/web/segments/{n}.mp3")
s = rx.sub(r'src="web/segments/\1.mp3"', s)
s = s.replace("</body>", "").replace("</html>", "").replace("Advanced(B1)", "Advanced")
assert "file:///" not in s and "C:\\" not in s, lv
h = head.replace("NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01 player(coffee_prices)", f"Coffee New Tone - {lab}")
with open(f"{OUT}/{lv}/player.html", "w", encoding="utf-8", newline="\n") as f:
    f.write(h + f'<body>\n<h1>Coffee Prices (new tone E2E, Production) - {lab}</h1>\n' + s + "\n</body></html>\n")
manifest[lv] = {"segment_mp3": segs}

# ---------------- Standard (complete, part2 = Attempt 4 human-approved) ----------------
res_a2 = json.load(open(f"{R}/a2/audit/tts_generation_results.json", encoding="utf-8"))
lv2, wav2 = "a2", "Family_X_Audio_A2_COFFEE_PRICES.wav"
a2b = body[body.index("<h2>Standard"):]
ep2_src = f"{R}/a2/assembled/{wav2}"
wav2mp3(ep2_src, f"{OUT}/a2/web/episode.mp3")
ep_dur["a2"] = dur(ep2_src)
s2 = a2b.replace(FILE + f"a2/assembled/{wav2}", "web/episode.mp3")
rx2 = re.compile(r'src="' + re.escape(FILE) + r'a2/narration/([A-Za-z0-9_]+)\.wav"')
segs2 = sorted(set(rx2.findall(s2)))
for n in segs2:
    wav2mp3(f"{R}/a2/narration/{n}.wav", f"{OUT}/a2/web/segments/{n}.mp3")
s2 = rx2.sub(r'src="web/segments/\1.mp3"', s2)
s2 = s2.replace("</body>", "").replace("</html>", "").replace("Standard(A2)", "Standard")
s2 = re.sub(r'EN: ([^<]*)<br>JA: ([^<]*)</td>', r'\1 / \2</td>', s2)  # Gate(n): no EN:/JA: labels (same policy as Advanced)
NOTE2 = ('<br><small style="color:#a40">[採用音声 = Attempt 4(Local Rewrite後の再TTS)。ユーザー試聴PASS 2026-10-11。'
         '自動ASRは不合格のままの個別Human Approvalで、記事全体の品質承認ではありません。実際に読まれた文面は上記と一部異なります: '
         '「US data」→「data from the United States」/「the two numbers」→「the 2 numbers」/「nine months」→「9 months」/引用符除去]</small>')
s2, nsub = re.subn(r'(<b>Full Story Part 2</b>.*?<td class="txt">)(.*?)(</td>)', lambda m: m.group(1) + m.group(2) + NOTE2 + m.group(3), s2, count=1, flags=re.S)
assert nsub == 1
assert "file:///" not in s2 and "C:\\" not in s2, "a2 leftover file ref"
h2 = head.replace("NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01 player(coffee_prices)", "Coffee New Tone - Standard")
with open(f"{OUT}/a2/player.html", "w", encoding="utf-8", newline="\n") as f:
    f.write(h2 + '<body>\n<h1>Coffee Prices (new tone E2E, Production) - Standard</h1>\n' + s2 + "\n</body></html>\n")
manifest["a2"] = {"segment_mp3": segs2}
with open(f"{EV}/pages_build_manifest_09.json", "w", encoding="utf-8") as f:
    json.dump({"episode_duration_sec": ep_dur, **manifest}, f, ensure_ascii=False, indent=2)
a2_ok = segs2

# ---------------- index.html ----------------
ep = json.load(open(f"{R}/entry_point.json", encoding="utf-8"))
ja_title = ep["japanese_title"]


def seg_rows(res, lv, mp3dir_ok):
    o = ['<table class="seg"><thead><tr><th>segment</th><th>status</th><th>voice</th><th>duration(sec)</th>'
         '<th>試行数</th><th>fallback</th><th>ASR verified</th><th>style_source</th><th>style_prefix(全文)</th>'
         '<th>再生</th></tr></thead><tbody>']
    n = 0
    for k in ORDER:
        v = res["segments"].get(k)
        if not v:
            continue
        n += 1
        hum = (lv == "a2" and k == "full_story_part2" and v.get("status") == "HUMAN_REVIEW_LOCKED")
        ok = v.get("status") == "OK" or hum
        d = v.get("duration_seconds")
        if d is None and ok:
            d = dur(f"{R}/{lv}/narration/{k}.wav")
        sp = E(v.get("style_prefix") or ("F1_5+減速(承認逐語)。Attempt4=Local Rewrite再TTSの実送信値(先頭200字がログ保存)。STYLE_CHECK_09.md参照" if hum else "(記録なし)")).replace("\n", "<br>")
        play = (f'<audio controls preload="none" src="{lv}/web/segments/{k}.mp3"></audio>' if ok and k in mp3dir_ok
                else "未取得")
        o.append(f'<tr><td>{k}</td><td>{"HUMAN_APPROVED(ユーザー試聴PASS 2026-10-11、Attempt 4)" if hum else v.get("status")}</td><td>{E(str(v.get("voice")))}</td><td>{d}</td>'
                 f'<td>{n_attempts(v) if not hum else "4(標準2+fallback1+LR再TTS1)"}</td><td>{v.get("fallback_used") if not hum else "True"}</td><td>{v.get("asr_verified")}</td>'
                 f'<td>{E(style_src(v) if not hum else "approved_role_style:EN_FULLSTORY_F1_5")}</td><td class="style">{sp}</td><td>{play}</td></tr>')
    o.append("</tbody></table>")
    return "\n".join(o), n


def shell_table(res):
    o = ['<table class="seg"><thead><tr><th>shell</th><th>status</th><th>reused</th>'
         '<th>master_audio_id</th></tr></thead><tbody>']
    for k, v in res["shared_narration"].items():
        o.append(f'<tr><td>{k}</td><td>{v["status"]}</td><td>{v.get("reused")}</td><td>{v.get("master_audio_id")}</td></tr>')
    o.append("</tbody></table>")
    return "\n".join(o)


def adv_phrase(r):
    m = re.search(r"Key Phrase %d</b>.*?EN: (.*?)<br>" % r, b1s, re.S)
    return E(m.group(1)) if m else "(未取得)"


res_b = json.load(open(f"{R}/b1b/audit/tts_generation_results.json", encoding="utf-8"))
st_b, n_b = seg_rows(res_b, "b1b", set(segs))
st_a, n_a = seg_rows(res_a2, "a2", set(a2_ok))
kp = res_b["key_phrases"]
sp_b = f'<h2>Coffee Prices: Advanced(完成: 通し再生)</h2>\n<audio controls preload="none" src="b1b/web/episode.mp3"></audio>\n'
sp_b += (f'<p class="meta">duration: {ep_dur["b1b"]}s / segment数: {n_b} / tts_backend: {res_b["tts_backend"]} / '
         f'style_version: {res_b["style_version"]} / TTS方式: Batch(Flash-Lite speech_metadata)</p>\n')
sp_b += f"<h3>可変segment一覧(Advanced、各segmentの再生・style_source)</h3>\n{st_b}\n"
sp_b += ('<h3>Key Phrase構造(Advanced: Phrase to 英語解説 to 同一Phrase再生)</h3>\n'
         '<table class="seg"><thead><tr><th>rank</th><th>Phrase(英語)</th><th>解説(全文)</th><th>解説 voice</th></tr></thead><tbody>\n')
for r in sorted(kp, key=int):
    x = kp[r]["explanation"]
    sp_b += f'<tr><td>{r}</td><td>{adv_phrase(int(r))}</td><td>{E(x["text"])}</td><td>{E(x["voice"])}</td></tr>\n'
sp_b += "</tbody></table>\n<h3>固定shell(Production Master Store、再利用)</h3>\n" + shell_table(res_b) + "\n"
sp_a = (f'<h2>Coffee Prices: Standard(完成: 通し再生)</h2>\n<audio controls preload="none" src="a2/web/episode.mp3"></audio>\n'
        '<div class="note">Standardの<code>full_story_part2</code>は自動ASRが全attemptで不合格でしたが、<b>Attempt 4(Local Rewrite後の再TTS)をユーザーが試聴しPASS・採用承認(2026-10-11)</b>しました(既存の個別Human Approval機構 record_human_approval)。'
        'これはfull_story_part2のみの部分承認で、<b>記事全体の音声品質の承認ではありません</b>(Standard/Advanced完成版の最終試聴で判断)。'
        '採用音声は実際には一部書き換えた文面(「data from the United States」「2 numbers」「9 months」)を読んでいます。試聴用: <a href="part2_review/index.html">part2_review</a>(採用済み)。</div>\n'
        f'<p class="meta">duration: {ep_dur["a2"]}s / segment数: {n_a} / tts_backend: {res_a2["tts_backend"]} / style_version: {res_a2["style_version"]}</p>\n'
        f"<h3>可変segment一覧(Standard)</h3>\n{st_a}\n<h3>固定shell(Standard側、Production Master Storeから再利用[Champion]。Advancedと同一sha256)</h3>\n" + shell_table(res_a2) + "\n")

page = f'''<!DOCTYPE html>
<html lang="ja"><head><meta charset="utf-8">
<title>Coffee Prices 新tone E2E (Production正式経路)</title>
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
<h1>Coffee Prices(新tone: J2/E2_UPBEAT/F1.5)Production正式経路 E2E</h1>
<div class="note">
管理ID: <b>FAMILY-X-COFFEE-NEW-TONE-PRODUCTION-E2E-01</b>(委任_07、2026-10-11)。日本語タイトル: {E(ja_title)}。
日本語記事は承認済み品質マスター(E案)を再生成せず受理(U-1案b)。EN→RF→Queue→支援文→TTS(<code>--tts-backend speech_metadata_flash_lite</code>)→ASR→Assembly。
Advanced・Standardとも完成(Standardのfull_story_part2のみユーザー試聴PASSの個別Human Approval)。<code>PRODUCTION_WIRED</code>等の最終判定は人間ユーザー承認であり、本ページはevidence配布のみです。<br>
<b>全スクリプト(各segment原稿)とKey Phrases(EN/JA)の確認ページ</b>: <a href="a2/player.html">Standard player(通し再生+全スクリプト+Key Phrases EN/JA)</a> / <a href="b1b/player.html">Advanced player(通し再生+全スクリプト+Key Phrases EN/解説)</a>
</div>
{sp_b}
{sp_a}
</body></html>
'''
with open(f"{OUT}/index.html", "w", encoding="utf-8", newline="\n") as f:
    f.write(page)
print("done", ep_dur, n_b, n_a)
