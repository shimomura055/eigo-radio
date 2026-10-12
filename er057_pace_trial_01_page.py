# -*- coding: utf-8 -*-
"""委任_02 試聴ページ生成(無料)。user_test/coffee_pace_trial_01/ に静的ファイルのみ。"""
import os, sys, json, html
import numpy as np, soundfile as sf, lameenc
ROOT = "C:/Users/tensh/eigo-radio"; sys.path.insert(0, ROOT)
import er057_pace_trial_01_gen as G
OUT = f"{ROOT}/er057_output/pace_trial_01"; PG = f"{ROOT}/user_test/coffee_pace_trial_01"; AU = f"{PG}/audio"
F5 = f"{ROOT}/er057_output/coffee_final_listening_tone_trial_01/part_final/segments"
os.makedirs(AU, exist_ok=True)
S = json.load(open(f"{OUT}/summary_01.json", encoding="utf-8"))
gl = [json.loads(l) for l in open(f"{OUT}/generation_log_01.jsonl", encoding="utf-8")]
asrj = {(r["cand"], r["part"]): r for r in gl if r.get("cand")}
def mp3(x, sr, path, kbps=96):
    e = lameenc.Encoder(); e.set_bit_rate(kbps); e.set_in_sample_rate(sr); e.set_channels(1); e.set_quality(2)
    open(path, "wb").write(e.encode((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes()) + e.flush())
def build_audio(name, paths):
    xs = []
    for i, p in enumerate(paths, 1):
        x, sr = sf.read(p, dtype="float64"); x = x.mean(axis=1) if x.ndim > 1 else x
        mp3(x, sr, f"{AU}/{name}_p{i}.mp3"); xs.append(x)
    gap = np.zeros(int(sr * 0.8)); cat = np.concatenate([xs[0], gap, xs[1], gap, xs[2]])
    mp3(cat, sr, f"{AU}/{name}_all.mp3"); return sr
for c in G.CANDS: build_audio(c, [f"{OUT}/attempts/{c}_adv_part{n}.wav" for n in (1, 2, 3)])
sr = build_audio("F5", [f"{F5}/adv_part{n}_f5.wav" for n in (1, 2, 3)])
def block(c, base=False):
    r = S[c]; jp = "基準(Final v2 Advanced Full Storyの既存音声。再生成なし)" if base else G.CANDS[c][0]
    style = G.style_of_f5() if base else G.style_of(c)
    h = f"<tr id='{c}'><td class='id'><b>{c}</b><br>{html.escape(jp)}<br><span class='sec'>合計WPM <b>{r['total_wpm']}</b></span></td><td class='play'>"
    for n in (1, 2, 3): h += f"Part{n} ({r['part_wpm'][n-1]} WPM)<br><audio controls preload='none' src='audio/{c}_p{n}.mp3'></audio><br>"
    h += f"<b>3Part連結(Part間0.8秒)</b><br><audio controls preload='none' src='audio/{c}_all.mp3'></audio></td><td class='txt'>"
    h += f"<table class='w'><tr><th>Part1/2/3 WPM</th><td>{' / '.join(str(v) for v in r['part_wpm'])}</td></tr><tr><th>合計 / 発話部分(500ms,300ms)</th><td>{r['total_wpm']} / {r['speech_wpm500']} / {r['speech_wpm300']}</td></tr>"
    h += f"<tr><th>文間ポーズ(500ms以上)</th><td>{r['mid_pauses500']}個 計{r['mid_pause_total500']}秒</td></tr><tr><th>最速10秒窓 / 文単位最大</th><td>{r['max_win_wpm']} / {r['max_sent_wpm']} WPM</td></tr>"
    if not base:
        h += f"<tr><th>Primary ASR判定</th><td>{' / '.join(r['asr_primary'])}" + (f" <b>(Part{','.join(map(str, r['asr_ng']))} 内容不一致警告・再生成なし)</b>" if r['asr_ng'] else "") + "</td></tr>"
        h += f"<tr><th>警告</th><td>{', '.join(r['warnings']) or 'なし'}</td></tr><tr><th>異音検知(候補数/medium以上)</th><td>{r['anomaly_n']['all']} / {r['anomaly_n']['medium_plus']}</td></tr>"
    h += f"</table><details><summary>Prompt(style)</summary><div class='script'>{html.escape(style)}</div></details></td></tr>"
    return h
pas = sorted([c for c in G.CANDS if S[c]["primary"] == "PASS"], key=lambda c: -S[c]["total_wpm"])
exc = sorted([c for c in G.CANDS if S[c]["primary"] != "PASS"], key=lambda c: S[c]["total_wpm"])
head = "<thead><tr><th>候補</th><th>音声</th><th>実測・Prompt</th></tr></thead>"
body = f"""<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><title>Coffee Advanced Full Story ペース候補 試聴</title><meta name='viewport' content='width=device-width, initial-scale=1'><style>body{{font-family:sans-serif;max-width:1180px;margin:1em auto;padding:0 1em;line-height:1.5}}table{{border-collapse:collapse;width:100%;margin-bottom:1.5em}}th,td{{border:1px solid #ccc;padding:6px;vertical-align:top;text-align:left}}td.id{{width:170px}}td.play{{min-width:340px}}td.play audio{{width:100%}}.sec{{color:#666;font-size:.85em}}.script{{background:#f6f6f6;padding:4px;margin:3px 0;font-size:.9em;white-space:pre-wrap}}table.w th{{width:210px;font-weight:normal;background:#fafafa}}.note{{background:#fff8e0;padding:6px}}</style></head><body>
<h1>Coffee Advanced Full Story テンポ候補 試聴</h1>
<p class='note'>FAMILY-X-COFFEE-ADVANCED-FULLSTORY-PACE-TRIAL-01 委任_02。試聴用の検証結果です(Productionへは未反映、採用は未決定)。Advanced Full Story Part1〜3を、同一原稿・同一モデル(gemini-3.8-flash-lite-tts)・同一声(Aoede)・機械的な速度変更なしで、Style文の調整方向だけを変えて生成した8候補と、基準(現行F5)です。合計WPM 170〜200 を一次選別の目安にしています。WPM=1分あたりの英語の語数。</p>
<h2>基準</h2><table>{head}{block('F5', True)}</table>
<h2>一次選別を通過した候補(合計WPM順、{len(pas)}件)</h2><table>{head}{''.join(block(c) for c in pas)}</table>
<h2>参考: 範囲外(170〜200外)の候補({len(exc)}件)</h2><p>聴き比べの参考として残しています。</p><table>{head}{''.join(block(c) for c in exc)}</table>
</body></html>"""
open(f"{PG}/index.html", "w", encoding="utf-8").write(body)
print("pass", pas, "exc", exc, "size_MB", round(sum(os.path.getsize(f"{AU}/{f}") for f in os.listdir(AU)) / 1e6, 1), "sr", sr)
