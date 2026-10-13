# -*- coding: utf-8 -*-
"""Round6 listen 試聴ページ生成(API0)。wav -> mp3(96kbps mono, lameenc、既存ページ er057_coffee_tts_style_h_speed_02_page.py と同方式)。"""
import os, json, html, hashlib, shutil
import numpy as np, soundfile as sf, lameenc
ROOT = os.path.dirname(os.path.abspath(__file__)); O = f"{ROOT}/er057_output/coffee_tts_style_h_speed_04/round6_listen"; PG = f"{ROOT}/user_test/coffee_style_h_speed_04"; AU = f"{PG}/audio"
os.makedirs(AU, exist_ok=True)
m = json.load(open(f"{O}/measurements_r6.json", encoding="utf-8")); T = m["takes"]; C = json.load(open(f"{O}/classification_r6.json", encoding="utf-8")); J = C["per_job"]; AG = C["agg"]
P2 = json.load(open(f"{ROOT}/er057_output/coffee_tts_style_h_speed_03/round2/prompts_r2.json", encoding="utf-8"))["candidates"]
STY = {"K06": P2["K06"]["style"], "K01": P2["K01"]["style"]}
H0S = json.load(open(f"{ROOT}/er057_output/coffee_tts_style_h_speed_02/prompts_h_speed_01.json", encoding="utf-8"))["candidates"]["H0"]["style"]
conv = {}
def mp3(src, dst):
    x, sr = sf.read(src, dtype="float64"); x = x.mean(axis=1) if x.ndim > 1 else x
    e = lameenc.Encoder(); e.set_bit_rate(96); e.set_in_sample_rate(sr); e.set_channels(1); e.set_quality(2)
    open(dst, "wb").write(e.encode((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes()) + e.flush())
    conv[os.path.basename(dst)] = {"src_wav": os.path.relpath(src, ROOT).replace("\\", "/"), "src_wav_sha256": hashlib.sha256(open(src, "rb").read()).hexdigest(), "mp3_sha256": hashlib.sha256(open(dst, "rb").read()).hexdigest()}
for k, t in T.items(): mp3(f"{ROOT}/{t['path']}", f"{AU}/{k.replace('_part1','')}.mp3")
SRC02 = f"{ROOT}/user_test/coffee_style_h_speed_02/audio"
for n in ("H0_std_t1", "H0_adv_t1", "v5_std", "v5_adv"):
    shutil.copyfile(f"{SRC02}/{n}.mp3", f"{AU}/{n}.mp3"); conv[n + ".mp3"] = {"copied_from": f"user_test/coffee_style_h_speed_02/audio/{n}.mp3", "mp3_sha256": hashlib.sha256(open(f"{AU}/{n}.mp3", "rb").read()).hexdigest()}
json.dump(conv, open(f"{O}/audio_conversion_r6.json", "w", encoding="utf-8"), indent=1)
def met(t, lv, passinfo=None):
    e = t["end_pause_ms"]
    w = f"{t['wpm']}" if lv == "adv" else f"Std実測(6%減速後) {t['wpm']} / raw換算 {round(t['wpm']/0.94,1)}"
    w = ("Adv実測 " + w) if lv == "adv" else w
    s = f"WPM {w} / 文末無音 平均{e['mean']}ms(最大{e['max']}ms) / 800ms以上の長無音 {len(t['long800'])}本"
    if t["long800"]: s += "(" + ", ".join(f"{x['ms']}ms:{x['prev']}->{x['next']}" for x in t["long800"]) + ")"
    s += f" / ASR(減速前音声) {t.get('primary_asr','-')}" + ("" if t.get("asr_verified", True) else " <b>[ASR不一致: his挿入]</b>") + f" / 異音検知 medium以上 {t['anomaly_medium_plus']}件"
    return s
def card(c, lv, nm):
    k = lambda n: f"{c}_{lv}_part1_t{n}"; a = AG[f"{c}_{lv}"]
    h = f"<section id='{c}_{lv}'><h2>{c} {nm}</h2><p class='s'>3take合格 <b>{a['pass_count']}/3</b>(Take別: {' / '.join(a['classes'])})。WPM範囲 {a['wpm_range'][0]}-{a['wpm_range'][1]}(幅{a['wpm_spread']})、文末平均範囲 {a['end_range'][0]}-{a['end_range'][1]}ms(幅{a['end_spread']}ms)。合格基準: {'Std実測151-163' if lv=='std' else 'Adv実測161-173'}WPM・文末平均{'498' if lv=='std' else '593'}ms以下・800ms+長無音1本以下・ASR/異音OK。</p>"
    for n in (1, 2, 3):
        t = T[k(n)]
        h += f"<p><b>Take{n}</b> [{J[k(n)]['cls']}]<br><audio controls preload='none' src='audio/{c}_{lv}_t{n}.mp3'></audio><br><span class='s'>{met(t, lv)}</span></p>"
    h += f"<details open><summary>Prompt全文(sha {hashlib.sha256(STY[c].encode()).hexdigest()[:8]})</summary><div class='sc'>{html.escape(STY[c])}</div></details></section>"
    return h
ref = "<section id='ref'><h2>比較用(再生成なし)</h2><p class='s'>Part1(約45秒)の比較です。現行v5はFull Story全体も下に置きました(既存ファイルへの参照、再生成なし)。</p>"
for lv, nm in (("std", "Standard"), ("adv", "Advanced")):
    h0 = m["H0_t1"][lv]; v5 = m["v5"][lv]
    ref += f"<h3>{nm}</h3><p><b>H0 Take1</b>(前回高評価のPrompt)<br><audio controls preload='none' src='audio/H0_{lv}_t1.mp3'></audio><br><span class='s'>{met(h0, lv)}</span></p>"
    ref += f"<p><b>現行v5 Part1</b><br><audio controls preload='none' src='audio/v5_{lv}.mp3'></audio><br><span class='s'>{met(v5, lv)}(ASR結果は本ページでは未測定)</span></p>"
    ref += f"<p><b>現行v5 Full Story</b><br><audio controls preload='none' src='../coffee_final_v5/audio/Coffee_{'Standard' if lv=='std' else 'Advanced'}_final_v5.mp3'></audio><br><span class='s'>全編。数値はPart1のものを参照してください。</span></p>"
ref += f"<details><summary>H0 Prompt全文</summary><div class='sc'>{html.escape(H0S)}</div></details></section>"
html_ = f"""<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'><title>Coffee TTS Style H速度調整 Std/Adv別Prompt試聴</title><style>body{{font-family:sans-serif;max-width:720px;margin:0 auto;padding:8px 12px;line-height:1.55}}section{{border-top:2px solid #888;margin-top:18px;padding-top:6px}}audio{{width:100%}}.s{{color:#555;font-size:.85em}}.w{{color:#b30;font-size:.85em}}.n{{background:#fff8e0;padding:6px;font-weight:bold}}.sc{{background:#f4f4f4;padding:6px;white-space:pre-wrap;font-size:.9em}}h2{{font-size:1.15em}}h3{{font-size:1em;margin:10px 0 2px}}</style></head><body>
<h1>Coffee TTS Style H速度調整 Std/Adv別Prompt 試聴</h1>
<p class='n'>暫定成果物。採用判断なし(Trial、VALIDATED上限)。単一PromptでのStd/Adv両合格は未達のため、レベル別Promptの試聴用です。</p>
<p class='s'>FAMILY-X-COFFEE-TTS-STYLE-H-SPEED-TRIAL-04 委任_03。Standardは「K06」、Advancedは「K01」というそれぞれ別のPromptで、同じ原稿(Part1)・同じ声(Aoede)・同じモデル(gemini-3.8-flash-lite-tts)で3回ずつ生成しました。Standardは既存の6%減速を適用済みです。WPM=1分あたりの英語の語数で、無音・WPMは機械指標の参考値です。ASRは減速前の音声に対して1回だけ行いました(ASR不一致があっても再生成していません)。声の明るさ・抑揚は機械指標では判断できないため、ぜひ聴いて判断してください。</p>
<p class='s'>一覧: <a href='#ref'>比較用</a> <a href='#K06_std'>K06 Std</a> <a href='#K01_adv'>K01 Adv</a></p>
{card('K06','std','Standard Part1(6%減速後)')}{card('K01','adv','Advanced Part1')}{ref}</body></html>"""
open(f"{PG}/index.html", "w", encoding="utf-8").write(html_)
print(len(os.listdir(AU)), "mp3")
