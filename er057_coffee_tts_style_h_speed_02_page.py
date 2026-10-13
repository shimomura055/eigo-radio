# -*- coding: utf-8 -*-
import os, json, html, hashlib
import numpy as np, soundfile as sf, lameenc
ROOT = os.path.dirname(os.path.abspath(__file__)); O = f"{ROOT}/er057_output/coffee_tts_style_h_speed_02"; PG = f"{ROOT}/user_test/coffee_style_h_speed_02"; AU = f"{PG}/audio"
os.makedirs(AU, exist_ok=True)
m = json.load(open(f"{O}/measurements_02.json", encoding="utf-8")); T = m["takes"]; A = m["by_cand_level"]; BL = m["baselines"]; PEN = m["speed_penalties"]
P = json.load(open(f"{O}/prompts_h_speed_01.json", encoding="utf-8"))["candidates"]
def mp3(src, dst):
    x, sr = sf.read(src, dtype="float64"); x = x.mean(axis=1) if x.ndim > 1 else x
    e = lameenc.Encoder(); e.set_bit_rate(96); e.set_in_sample_rate(sr); e.set_channels(1); e.set_quality(2)
    open(dst, "wb").write(e.encode((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes()) + e.flush())
V5 = {"std": "er057_output/coffee_final_v4/segments/std_part1_slow6.wav", "adv": "er057_output/coffee_final_v4/segments/adv_part1_raw.wav"}
for lv in V5: mp3(f"{ROOT}/{V5[lv]}", f"{AU}/v5_{lv}.mp3")
for k, t in T.items(): mp3(f"{ROOT}/{t['path']}", f"{AU}/{k.replace('_part1','')}.mp3")
ASRNOTE = {"H1_std_part1_t1": "ASR差分: its->his(fist)、there is->there's。聴感で確認してください。", "H3_std_part1_t2": "ASR差分: its->his(fist)。聴感で確認してください。",
           "H2_adv_part1_t3": "ASR差分: 'do'が1語挿入(When do you see...)。聴感で確認してください。", "H0_std_part1_t2": "ASR差分: said->says、organization->organisation(前回と同一音声)。聴感で確認してください。"}
def met(k):
    t = T[k]; e = t["end_pause_ms"]
    s = f"WPM {t['wpm']}(発話WPM {t['speech_wpm500']}) / 文末無音 平均{e['mean']}ms 最大{e['max']}ms / 文中無音 {t['mid']['n']}本 計{t['mid']['total_s']}s(300ms+: {t['mid']['n300']}本) / 末尾語 {t['last_word_dur_ms']}ms"
    w = []
    if not t["asr_verified"]: w.append("ASR警告(" + t["primary_asr"] + ")")
    if not t["tail_last3_match"]: w.append("末尾が原稿と不一致")
    if t["wpm"] > 195: w.append("WPM195超")
    if t["wpm"] < 150: w.append("WPM150未満")
    if t["anomaly_medium_plus"]: w.append("異音検知medium")
    if t["long800"]: w.append("800ms以上の長無音: " + ", ".join(f"{x['ms']}ms({x['prev']}->{x['next']})" for x in t["long800"]))
    if t["last_word_long_flag"]: w.append("文末語が長め")
    out = s + (f"<br><span class='w'>注意: {' / '.join(w)}</span>" if w else "")
    if k in ASRNOTE: out += f"<br><span class='w'>{ASRNOTE[k]}</span>"
    return out
def card(c):
    P_ = P[c]; h = f"<section id='{c}'><h2>{c}: {html.escape(P_['label'])}</h2>"
    h += f"<p class='s'>語数 {P_['words']}語 / {P_['chars']}字 / 速度制御: {html.escape(P_['speed_control_method'])}</p>"
    if c == "H0": h += "<p class='n'>H0のTake1/Take2は前回(8way候補H)と<b>同一の音声</b>です。Take3のみ今回の新規生成。</p>"
    for lv, nm in (("std", "Standard Part1(6%減速後)"), ("adv", "Advanced Part1")):
        k = lambda n: f"{c}_{lv}_part1_t{n}"
        a = A[f"{c}_{lv}"]
        h += f"<h3>{nm}</h3><p class='s'>3take平均 {a['wpm_mean']} / 最小 {a['wpm_min']} / 最大 {a['wpm_max']} / 最大差 {a['wpm_range']} / 最速 Take{a['fastest_take']}({a['fastest_wpm']})</p>"
        if PEN[f"{c}_{lv}"]: h += f"<p class='w'>速度の注意(180達成のため現行より速くしない): {'; '.join(PEN[f'{c}_{lv}'])}</p>"
        h += f"<p><b>Take1</b><br><audio controls preload='none' src='audio/{c}_{lv}_t1.mp3'></audio><br><span class='s'>{met(k(1))}</span></p>"
        for n in (2, 3):
            h += f"<details><summary>Take{n}(再現性確認)</summary><audio controls preload='none' src='audio/{c}_{lv}_t{n}.mp3'></audio><br><span class='s'>{met(k(n))}</span></details>"
    sh = hashlib.sha256(P_["style"].encode()).hexdigest()[:8]
    h += f"<details><summary>Prompt全文(sha {sh}、{P_['chars']}字、{P_['words']}語)</summary><div class='sc'>{html.escape(P_['style'])}</div><p class='s'>設計意図: {html.escape(P_['design_intent'])}</p><p class='s'>想定副作用: {html.escape(P_['expected_side_effects'])}</p></details></section>"
    return h
b = "".join(card(c) for c in ["H0", "H1", "H2", "H3", "H4", "H5"])
top = "<section id='ref'><h2>比較基準</h2><p class='s'>現行v5(再生成なし)と、前回高評価だったH Take1(= 今回のH0 Take1と同一音声)です。</p>"
for lv, nm in (("std", "Standard Part1(6%減速後)"), ("adv", "Advanced Part1")):
    v = m["v5"][lv]; e = v["end_pause_ms"]; h0 = T[f"H0_{lv}_part1_t1"]
    top += f"<h3>{nm}</h3><p><b>現行v5</b><br><audio controls preload='none' src='audio/v5_{lv}.mp3'></audio><br><span class='s'>WPM {v['wpm']} / 文末無音 平均{e['mean']}ms 最大{e['max']}ms / 文中無音 {v['mid']['n']}本 計{v['mid']['total_s']}s</span></p>"
    top += f"<p><b>前回H Take1(H0 Take1と同一)</b><br><audio controls preload='none' src='audio/H0_{lv}_t1.mp3'></audio><br><span class='s'>{met(f'H0_{lv}_part1_t1')}</span></p>"
top += "</section>"
rows = ""
for lv in ("std", "adv"):
    for c in ["H0", "H1", "H2", "H3", "H4", "H5"]:
        a = A[f"{c}_{lv}"]; f = "<br>".join(PEN[f"{c}_{lv}"]) or "-"
        rows += f"<tr><td>{c}</td><td>{lv}</td><td>{'/'.join(str(x) for x in a['wpm'])}</td><td>{a['wpm_mean']}</td><td>{a['wpm_min']}</td><td>{a['wpm_max']}</td><td>{a['wpm_range']}</td><td>T{a['fastest_take']}</td><td>{a['end_mean_avg']}</td><td>{a['mid_total_avg']}</td><td>{f}</td></tr>"
bl = " / ".join(f"{lv}: v5 {BL[lv]['v5_wpm']}, H0 T1 {BL[lv]['h0_t1_wpm']}, H0 3take平均 {BL[lv]['h0_mean3']}" for lv in ("std", "adv"))
summ = f"<section id='summary'><h2>候補別サマリ(WPM 3take)</h2><p class='s'>基準 {bl}</p><div style='overflow-x:auto'><table><tr><th>候補</th><th>Lv</th><th>T1/T2/T3</th><th>平均</th><th>最小</th><th>最大</th><th>最大差</th><th>最速</th><th>文末無音平均ms</th><th>文中無音計s</th><th>速度の注意</th></tr>{rows}</table></div></section>"
html_ = f"""<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'><title>Coffee TTS Style H速度調整 試聴</title><style>body{{font-family:sans-serif;max-width:720px;margin:0 auto;padding:8px 12px;line-height:1.55}}section{{border-top:2px solid #888;margin-top:18px;padding-top:6px}}audio{{width:100%}}.s{{color:#555;font-size:.85em}}.w{{color:#b30;font-size:.85em}}.n{{background:#fff8e0;padding:6px}}.sc{{background:#f4f4f4;padding:6px;white-space:pre-wrap;font-size:.9em}}h2{{font-size:1.15em}}h3{{font-size:1em;margin:10px 0 2px}}table{{border-collapse:collapse;font-size:.75em}}td,th{{border:1px solid #bbb;padding:2px 4px}}</style></head><body>
<h1>Coffee TTS Style H速度調整 試聴</h1>
<p class='n'>FAMILY-X-COFFEE-TTS-STYLE-H-SPEED-TRIAL-02。試聴用の検証です(Production未反映、採用は未決定)。前回高評価だったH(= H0)を土台に、速さのばらつきを抑える5つのPrompt案(H1〜H5)を、同じ原稿(Part1のみ)・同じ声(Aoede)・同じモデルで3回ずつ生成しました。目的は180 WPMに近づけることではなく、<b>現行より速くせず、自然で聞き取りやすく、take間のばらつきが小さいこと</b>です。</p>
<p><b>聴き方:</b> (1) 上の比較基準(現行v5、前回H Take1)を聴いて基準を耳に入れる。 (2) 各候補の<b>Take1</b>(Standard/Advanced)を聴き比べて選ぶ。 (3) 気に入った候補の<b>Take2・Take3</b>(折りたたみ)を聴いて、同じ傾向が出るか(再現性)を確認する。</p>
<p class='s'>WPM=1分あたりの英語の語数。無音・WPMは機械指標で参考値です(数値だけで良し悪しは決まりません)。Standardは既存の6%減速を適用済みで、減速後ASR確認は省略し、減速前の音声で1回だけ内容確認しています(Trial限定)。ASR警告があっても再生成していません。声質(明るさ・抑揚)は機械指標では判断できないため、ぜひ聴いて判断してください。</p>
<p class='s'>一覧: <a href='#ref'>基準</a> <a href='#summary'>サマリ表</a> {' '.join(f"<a href='#{c}'>{c}</a>" for c in ['H0','H1','H2','H3','H4','H5'])}</p>
{top}{summ}{b}</body></html>"""
open(f"{PG}/index.html", "w", encoding="utf-8").write(html_)
print(len(os.listdir(AU)), "mp3")
