# -*- coding: utf-8 -*-
import os, json, html, hashlib
import numpy as np, soundfile as sf, lameenc
ROOT = os.path.dirname(os.path.abspath(__file__)); O = f"{ROOT}/er057_output/coffee_tts_style_8way_01"; PG = f"{ROOT}/user_test/coffee_style_8way_01"; AU = f"{PG}/audio"
os.makedirs(AU, exist_ok=True)
m = json.load(open(f"{O}/measurements_02.json", encoding="utf-8")); T = m["takes"]
P = json.load(open(f"{O}/prompts_8way_01.json", encoding="utf-8"))["candidates"]
def mp3(src, dst):
    x, sr = sf.read(src, dtype="float64"); x = x.mean(axis=1) if x.ndim > 1 else x
    e = lameenc.Encoder(); e.set_bit_rate(96); e.set_in_sample_rate(sr); e.set_channels(1); e.set_quality(2)
    open(dst, "wb").write(e.encode((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes()) + e.flush())
V5 = {"std": "er057_output/coffee_final_v4/segments/std_part1_slow6.wav", "adv": "er057_output/coffee_final_v4/segments/adv_part1_raw.wav"}
for lv in V5: mp3(f"{ROOT}/{V5[lv]}", f"{AU}/v5_{lv}.mp3")
for k, t in T.items(): mp3(f"{ROOT}/{t['path']}", f"{AU}/{k.replace('_part1','')}.mp3")
def met(t):
    e = t["end_pause_ms"]; s = f"WPM {t['wpm']} / 文末無音 平均{e['mean']}ms 最大{e['max']}ms / 文中無音 {t['mid']['n']}本 計{t['mid']['total_s']}s"
    w = []
    if not t["asr_verified"]: w.append("ASR警告(" + t["primary_asr"] + ")")
    if not t["tail_last3_match"]: w.append("末尾が原稿と不一致")
    if t["wpm"] > 195: w.append("WPM195超")
    if t["wpm"] < 150: w.append("WPM150未満")
    if t["anomaly_medium_plus"]: w.append("異音検知medium")
    if t["long800"]: w.append("800ms以上の長無音あり")
    return s + (f"<br><span class='w'>注意: {' / '.join(w)}</span>" if w else "")
SPEC = {"B_adv_part1_t2": "ASRの結果、原稿に無い一文(Now it's a great time to be a coffee lover)が末尾に追加されている可能性。再生成せず参考表示。", "H_std_part1_t2": "ASRはsaid->says、organization->organisationの差(聴感確認用)。"}
def card(c):
    P_ = P[c]; h = f"<section id='{c}'><h2>{c}: {html.escape(P_['label'])}</h2>"
    if c == "A": h += "<p class='n'>現行v5と同条件(同一Prompt)で新規に2回生成したもの。下の「現行v5参考」とは別take。</p>"
    for lv, nm in (("std", "Standard Part1(6%減速後)"), ("adv", "Advanced Part1")):
        t1, t2 = T[f"{c}_{lv}_part1_t1"], T[f"{c}_{lv}_part1_t2"]
        h += f"<h3>{nm}</h3><p><b>Take1</b><br><audio controls preload='none' src='audio/{c}_{lv}_t1.mp3'></audio><br><span class='s'>{met(t1)}</span></p>"
        h += f"<details><summary>Take2(再現性確認)</summary><audio controls preload='none' src='audio/{c}_{lv}_t2.mp3'></audio><br><span class='s'>{met(t2)}</span>"
        for k in (f"{c}_{lv}_part1_t2", f"{c}_{lv}_part1_t1"):
            if k in SPEC: h += f"<br><span class='w'>{SPEC[k]}</span>"
        h += "</details>"
    sh = hashlib.sha256(P_["style"].encode()).hexdigest()[:8]
    h += f"<details><summary>Prompt全文(sha {sh}、{P_['chars']}字)</summary><div class='sc'>{html.escape(P_['style'])}</div><p class='s'>設計意図: {html.escape(P_['design_intent'])}</p></details></section>"
    return h
b = "".join(card(c) for c in "ABCDEFGH")
ref = "<section id='v5'><h2>現行v5参考(再生成なし)</h2><p class='n'>現行のv5 Part1音声そのまま。比較用。</p>"
for lv, nm in (("std", "Standard Part1(6%減速後)"), ("adv", "Advanced Part1")):
    v = m["v5"][lv]; e = v["end_pause_ms"]
    ref += f"<h3>{nm}</h3><audio controls preload='none' src='audio/v5_{lv}.mp3'></audio><br><span class='s'>WPM {v['wpm']} / 文末無音 平均{e['mean']}ms 最大{e['max']}ms / 文中無音 {v['mid']['n']}本 計{v['mid']['total_s']}s / sha {v['sha12']}</span>"
ref += "</section>"
html_ = f"""<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'><title>Coffee TTS Style 8方式 試聴</title><style>body{{font-family:sans-serif;max-width:720px;margin:0 auto;padding:8px 12px;line-height:1.55}}section{{border-top:2px solid #888;margin-top:18px;padding-top:6px}}audio{{width:100%}}.s{{color:#555;font-size:.85em}}.w{{color:#b30;font-size:.85em}}.n{{background:#fff8e0;padding:6px}}.sc{{background:#f4f4f4;padding:6px;white-space:pre-wrap;font-size:.9em}}h2{{font-size:1.15em}}h3{{font-size:1em;margin:10px 0 2px}}</style></head><body>
<h1>Coffee TTS Style 8方式 試聴</h1>
<p class='n'>FAMILY-X-COFFEE-TTS-STYLE-8WAY-AB-TRIAL-01。試聴用の検証です(Production未反映、採用は未決定)。同じ原稿(Part1のみ)・同じ声(Aoede)・同じモデルで、Prompt(Style文)だけをA〜Hの8方式に変えました。</p>
<p><b>聴き方:</b> (1) まず各候補の<b>Take1</b>(Standard/Advanced)を聴き比べて選ぶ。 (2) 気に入った候補の<b>Take2</b>(折りたたみ)を聴いて、同じ傾向が出るか(再現性)を確認する。</p>
<p class='s'>WPM=1分あたりの英語の語数。無音・WPMは機械指標で参考値です(数値だけで良し悪しは決まりません)。Standardは既存の6%減速を適用済み。Standardの減速後ASR確認は省略し、減速前の音声で1回だけ内容確認しています(Trial限定)。ASR警告があっても再生成していません。</p>
<p class='s'>一覧: {' '.join(f"<a href='#{c}'>{c}</a>" for c in 'ABCDEFGH')} <a href='#v5'>v5参考</a></p>
{b}{ref}</body></html>"""
open(f"{PG}/index.html", "w", encoding="utf-8").write(html_)
print(len(os.listdir(AU)), "mp3")
