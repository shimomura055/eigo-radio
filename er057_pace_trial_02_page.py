# -*- coding: utf-8 -*-
"""委任_01(PACE-02) 試聴ページ生成(無料)。user_test/coffee_pace_trial_02/ に静的ファイルのみ。"""
import os, sys, json, html
import numpy as np, soundfile as sf, lameenc
ROOT = "C:/Users/tensh/eigo-radio"; sys.path.insert(0, ROOT)
import er057_pace_trial_02_gen as G
OUT = f"{ROOT}/er057_output/pace_trial_02"; PG = f"{ROOT}/user_test/coffee_pace_trial_02"; AU = f"{PG}/audio"
F5 = f"{ROOT}/er057_output/coffee_final_listening_tone_trial_01/part_final/segments"
os.makedirs(AU, exist_ok=True)
S = json.load(open(f"{OUT}/summary_02.json", encoding="utf-8"))
gl = [json.loads(l) for l in open(f"{OUT}/generation_log_02.jsonl", encoding="utf-8")]
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
PROS = json.load(open(f"{OUT}/prosody_02.json", encoding="utf-8"))
PCNT = {"PD8": "Part1 whisperで want to を wanna と聞き取り(口語縮約の可能性、Primary ASRはOK)。Part3 1.4秒付近にclick(medium)。", "PD1": "Primary ASR Part3が1語差(buying->buy)でNG警告(local whisperは同箇所一致=ASR揺れの可能性)。", "PD6": "Part2 39.5秒付近にclick(medium)。", "PD5": "Part3 6.9秒付近にclick(medium)。", "PD2": "Primary ASR Part1がNG警告(want to->wanna 1語。local whisperでは差なし、要試聴)。"}
QUAL = {
 "PD8": "機械指標: ピッチ幅/抑揚はF5と同等(下表)、文間ポーズ増(F5より+3個)、発話部分WPMがF5 219.0->193.6と最も低下(間よりも発声そのものが丁寧になった型)。『flat/sleepyにしない』指示を入れているが、明るさ・低テンション化の有無は聴感未確認。Part1のみ169.8で相対的に遅め。",
 "PD1": "機械指標: ピッチ幅/抑揚はF5と同等、文間ポーズ最多(18個/11.4秒)で余裕は大きい。Part間差13.6と均一(F5 31.5)。報道キャスター調で『smile in the voice』を維持する指示だが、明るさ(upbeat感)が落ちて硬くなっていないかは聴感未確認。",
 "PD6": "機械指標: 抑揚指標はF5同等。Part1 184.3と他Partで差(23.0)。目標範囲外。",
 "PD4": "機械指標: 抑揚指標はF5同等。最速10秒窓258で局所的に速い箇所が残る。目標範囲外。",
 "PD7": "機械指標: Part間差6.4と最も均一(F5 31.5)。局所緩急の指示は全体減速には弱いが、Partごとのばらつき解消には有効。目標範囲外(参考)。",
 "PD2": "機械指標: 削除型。テンポ語除去のみでF5比-7.8 WPM。抑揚指標はF5同等。目標範囲外。",
 "PD3": "機械指標: 文間ポーズ9個で減少(F5 11個)。『間を置け』指示はポーズ増に結びつかなかった。目標範囲外。",
 "PD5": "機械指標: 文間ポーズ7個で最少。lively等の語を残したためか減速は最小。目標範囲外。",
 "F5": "基準(現行F5)。",
}
def tier(t): return "最優先試聴候補(175-185)" if 175 <= t <= 185 else "試聴候補(185-190)" if 185 < t <= 190 else "目標未達・参考(>190)" if t > 190 else "品質確認要(<175)"
def block(c, base=False):
    r = S[c]; jp = "基準(現行F5。既存音声を再利用、再生成なし)" if base else G.CANDS[c][0]
    style = G.style_of_f5() if base else G.style_of(c)
    h = f"<tr id='{c}'><td class='id'><b>{c}</b><br>{html.escape(jp)}<br><span class='sec'>合計WPM <b>{r['total_wpm']}</b></span><br><span class='tier'>{'' if base else tier(r['total_wpm'])}</span></td><td class='play'>"
    for n in (1, 2, 3): h += f"Part{n} ({r['part_wpm'][n-1]} WPM)<br><audio controls preload='none' src='audio/{c}_p{n}.mp3'></audio><br>"
    h += f"<b>3Part連結(Part間0.8秒)</b><br><audio controls preload='none' src='audio/{c}_all.mp3'></audio></td><td class='txt'>"
    h += f"<table class='w'><tr><th>Part1/2/3 WPM</th><td>{' / '.join(str(v) for v in r['part_wpm'])}</td></tr><tr><th>合計 / 発話部分(500ms,300ms)</th><td>{r['total_wpm']} / {r['speech_wpm500']} / {r['speech_wpm300']}</td></tr>"
    h += f"<tr><th>文間ポーズ(500ms以上)</th><td>{r['mid_pauses500']}個 計{r['mid_pause_total500']}秒</td></tr><tr><th>最速10秒窓 / 文単位最大 / Part差</th><td>{r['max_win_wpm']} / {r['max_sent_wpm']} WPM / {r['part_spread']}</td></tr>"
    pr = PROS[c]; h += f"<tr><th>簡易ピッチ/強弱(機械指標)</th><td>中央F0 {pr['f0_median_hz']}Hz、ピッチ幅(p10-p90) {pr['f0_range_st_p10_p90']}半音、強弱幅 {pr['rms_dyn_db_p10_p90']}dB</td></tr>"
    if not base:
        h += f"<tr><th>Primary ASR判定</th><td>{' / '.join(r['asr_primary'])}" + (f" <b>(Part{','.join(map(str, r['asr_ng']))} 内容不一致警告・再生成なし)</b>" if r['asr_ng'] else "") + "</td></tr>"
        h += f"<tr><th>警告</th><td>{', '.join(r['warnings']) or 'なし'}</td></tr><tr><th>異音検知(候補数/medium以上)</th><td>{r['anomaly_n']['all']} / {r['anomaly_n']['medium_plus']}" + (f"<br>{html.escape(PCNT[c])}" if c in PCNT else "") + "</td></tr>"
        h += f"<tr><th>F5からの主要変更点</th><td>{html.escape(G.DIFF[c])}</td></tr>"
    h += f"<tr><th>品質所見</th><td>{html.escape(QUAL[c])}<br><span class='sec'>機械指標と所見の区別: 聴感評価は未実施。WPMが目標内でも品質PASSを意味しない。</span></td></tr>"
    h += f"</table><details><summary>Prompt全文(style)</summary><div class='script'>{html.escape(style)}</div></details></td></tr>"
    return h
order = sorted(S, key=lambda c: S[c]["total_wpm"])
head = "<thead><tr><th>候補</th><th>音声</th><th>実測・Prompt・所見</th></tr></thead>"
rows = "".join(block(c, c == "F5") for c in order)
body = f"""<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><title>Coffee Advanced Full Story Prompt全体調整 試聴</title><meta name='viewport' content='width=device-width, initial-scale=1'><style>body{{font-family:sans-serif;max-width:1180px;margin:1em auto;padding:0 1em;line-height:1.5}}table{{border-collapse:collapse;width:100%;margin-bottom:1.5em}}th,td{{border:1px solid #ccc;padding:6px;vertical-align:top;text-align:left}}td.id{{width:170px}}td.play{{min-width:340px}}td.play audio{{width:100%}}.sec{{color:#666;font-size:.85em}}.tier{{color:#a30;font-size:.85em}}.script{{background:#f6f6f6;padding:4px;margin:3px 0;font-size:.9em;white-space:pre-wrap}}table.w th{{width:210px;font-weight:normal;background:#fafafa}}.note{{background:#fff8e0;padding:6px}}</style></head><body>
<h1>Coffee Advanced Full Story Prompt全体調整 試聴</h1>
<p class='note'>FAMILY-X-COFFEE-ADVANCED-FULLSTORY-PACE-TRIAL-02 委任_01。試聴用の検証結果です(Productionへは未反映、採用は未決定)。Advanced Full Story Part1〜3を、同一原稿・同一モデル(gemini-3.8-flash-lite-tts)・同一声(Aoede)・機械的な速度変更なしで、Style文(Prompt)全体を調整思想の異なる8方向に作り直して生成した8候補と、基準(現行F5)です。合計WPMが遅い順に並べています(F5を同じ表に含む)。一次選別の目安: 175〜185=最優先、185超〜190=試聴候補、190超=目標未達。WPM=1分あたりの英語の語数。品質所見は機械指標のみで、聴感評価はユーザー試聴で確認してください。</p>
<table>{head}{rows}</table>
</body></html>"""
open(f"{PG}/index.html", "w", encoding="utf-8").write(body)
print("order", order, "size_MB", round(sum(os.path.getsize(f"{AU}/{f}") for f in os.listdir(AU)) / 1e6, 1), "sr", sr)
