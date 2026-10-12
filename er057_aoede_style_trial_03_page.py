# -*- coding: utf-8 -*-
"""集計(measurements.json/MEASUREMENTS_03.md)+試聴ページ生成。API費用0。"""
import os, sys, json, html
import numpy as np, soundfile as sf, lameenc
ROOT = "C:/Users/tensh/eigo-radio"; sys.path.insert(0, ROOT)
import er057_aoede_style_trial_03_gen as G, er057_tone_trial_final_build_03 as B
OUT = f"{ROOT}/er057_output/aoede_style_trial_03"; PG = f"{ROOT}/user_test/coffee_aoede_style_trial_03"; AU = f"{PG}/audio"
os.makedirs(AU, exist_ok=True)
ids = ["P0"] + list(G.CANDS)
M = {c: json.load(open(f"{OUT}/m/{c}.json", encoding="utf-8")) for c in ids}
gl = [json.loads(l) for l in open(f"{OUT}/generation_log_03.jsonl", encoding="utf-8")]
pg = [json.loads(l) for l in open(f"{ROOT}/er057_output/pace_trial_02/generation_log_02.jsonl", encoding="utf-8")]
ASR = {}
for r in pg:
    if r.get("job") == "PD8_adv_part1":
        ASR["P0"] = {"cls": r["classification"], "verified": r["verified"], "attempts": 1, "asr_text": r["asr_text"]}
for c in G.CANDS:
    rs = [r for r in gl if r.get("cand") == c and r.get("status") == "OK"]
    last = rs[-1]
    ASR[c] = {"cls": last["classification"], "verified": last["verified"], "attempts": len(rs), "asr_text": last["asr_text"], "first_attempt_cls": rs[0]["classification"]}
base = M["P0"]; rows = {}
for c in ids:
    m = M[c]; p5, p3 = m["pause"]["500"], m["pause"]["300"]
    rows[c] = {"duration_s": m["duration_s"], "wpm_overall": m["wpm_overall"], "wpm_speech500": p5["wpm_speech"], "wpm_speech300": p3["wpm_speech"],
               "diff_overall_pct": round((m["wpm_overall"] / base["wpm_overall"] - 1) * 100, 1),
               "diff_speech500_pct": round((p5["wpm_speech"] / base["pause"]["500"]["wpm_speech"] - 1) * 100, 1),
               "dur_diff_s": round(m["duration_s"] - base["duration_s"], 2), "pause500_n_mid": p5["n_mid"], "pause500_total_mid_s": p5["total_mid_s"], "pause500_max_s": p5["max_mid_s"],
               "pause300_n_all": p3["n_all"], "pause300_total_all_s": p3["total_all_s"], "pause_total_diff_s": round(p5["total_all_s"] - base["pause"]["500"]["total_all_s"], 2),
               "asr": ASR[c], "audio_qa": m["audio_qa"], "local_whisper": m["local_whisper_medium_diff"], "sha256": m["sha256"]}
def mark(c):
    r = rows[c]; t = r["wpm_overall"]; d = r["diff_overall_pct"]
    s = "P0(基準)" if c == "P0" else ("P0比±5%以内" if abs(d) <= 5 else "P0比±5%超(要確認)")
    ref = "Pace-02参照 175-185" if 175 <= t <= 185 else ("Pace-02参照 175未満" if t < 175 else "Pace-02参照 185-190" if t <= 190 else "Pace-02参照 190超")
    return s, ref
json.dump({"sample": "Coffee v3 Advanced Part1 (PD8 adv_part1)", "tts_model": B.MODEL, "voice": B.VOICE, "rows": rows,
           "note": "許容差はPace Trial-02基準(目標約180/<=190/175-185優先)を参照した暫定評価値。P0比+-5%は本Trial限定の暫定目安であり、Production合格基準ではない。"},
          open(f"{OUT}/measurements.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
L = ["| ID | 特徴 | 総秒 | 全体WPM | 発話WPM(500ms) | 発話WPM(300ms) | P0比 全体% | P0比 発話% | 秒差 | 文間無音(500ms)数/計s/最長s | 全無音量差s | 暫定目安 |", "|" + "---|" * 12]
for c in ids:
    r = rows[c]; a, b = mark(c); jp = "現行PD8(基準)" if c == "P0" else G.CANDS[c][0]
    L.append(f"| {c} | {jp} | {r['duration_s']} | {r['wpm_overall']} | {r['wpm_speech500']} | {r['wpm_speech300']} | {r['diff_overall_pct']:+.1f} | {r['diff_speech500_pct']:+.1f} | {r['dur_diff_s']:+.2f} | {r['pause500_n_mid']}/{r['pause500_total_mid_s']}/{r['pause500_max_s']} | {r['pause_total_diff_s']:+.2f} | {b} / {a} |")
L += ["", "| ID | Primary ASR | 試行数 | peak dBFS | headroom dB | clip(>=0.999)数 | RMS dBFS | local whisper(medium)差分 |", "|---|---|---|---|---|---|---|---|"]
for c in ids:
    r = rows[c]; q = r["audio_qa"]; w = r["local_whisper"]
    L.append(f"| {c} | {r['asr']['cls']}({'verified' if r['asr']['verified'] else 'NOT verified'}) | {r['asr']['attempts']} | {q['peak_dbfs']} | {q['headroom_db']} | {q['clip_samples_ge_0.999']} | {q['rms_dbfs']} | {json.dumps(w, ensure_ascii=False)[:200]} |")
open(f"{OUT}/MEASUREMENTS_03.md", "w", encoding="utf-8").write("\n".join(L))

def mp3(x, sr, path, kbps=96):
    e = lameenc.Encoder(); e.set_bit_rate(kbps); e.set_in_sample_rate(sr); e.set_channels(1); e.set_quality(2)
    open(path, "wb").write(e.encode((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes()) + e.flush())
for c in ids:
    x, sr = sf.read(f"{OUT}/audio/{c}.wav", dtype="float64"); x = x.mean(axis=1) if x.ndim > 1 else x
    mp3(x, sr, f"{AU}/{c}.mp3")
script = [j for j in B.jobs_def() if j["id"] == "adv_part1"][0]["tts_input"]
def feat(c): return "現行Coffee v3 Advanced使用のStyle(PD8)。比較基準。" if c == "P0" else G.CANDS[c][2]
rowsh = ""
for c in ids:
    r = rows[c]; a, b = mark(c); st = G.PD8 if c == "P0" else G.style_of(c); jp = "現行PD8(基準)" if c == "P0" else G.CANDS[c][0]
    rowsh += (f"<tr id='{c}'><td class='id'><b>{c}</b><br>{html.escape(jp)}<br><span class='sec'>{html.escape(feat(c))}</span></td>"
              f"<td class='play'><audio controls preload='none' src='audio/{c}.mp3'></audio></td>"
              f"<td><table class='w'><tr><th>総再生秒数</th><td>{r['duration_s']} 秒 (P0比 {r['dur_diff_s']:+.2f})</td></tr><tr><th>全体WPM(無音含む)</th><td><b>{r['wpm_overall']}</b> (P0比 {r['diff_overall_pct']:+.1f}%)</td></tr>"
              f"<tr><th>発話WPM(無音除く、500ms基準)</th><td><b>{r['wpm_speech500']}</b> (P0比 {r['diff_speech500_pct']:+.1f}%) / 300ms基準 {r['wpm_speech300']}</td></tr>"
              f"<tr><th>文間無音(500ms以上)</th><td>{r['pause500_n_mid']}個 計{r['pause500_total_mid_s']}秒 最長{r['pause500_max_s']}秒 (全無音量 P0比 {r['pause_total_diff_s']:+.2f}秒)</td></tr>"
              f"<tr><th>目安(暫定)</th><td>{b} / {a}</td></tr>"
              f"<tr><th>Primary ASR / 音質</th><td>{r['asr']['cls']} / peak {r['audio_qa']['peak_dbfs']} dBFS、clip {r['audio_qa']['clip_samples_ge_0.999']}件</td></tr></table>"
              f"<details><summary>Prompt全文(style)</summary><div class='script'>{html.escape(st)}</div></details></td></tr>")
body = f"""<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><title>Coffee Aoede Style改善 試聴(P0〜P8)</title><meta name='viewport' content='width=device-width, initial-scale=1'><style>body{{font-family:sans-serif;max-width:1100px;margin:1em auto;padding:0 1em;line-height:1.5}}table{{border-collapse:collapse;width:100%;margin-bottom:1.2em}}th,td{{border:1px solid #ccc;padding:6px;vertical-align:top;text-align:left}}td.id{{width:200px}}td.play{{min-width:380px;width:380px}}td.play audio{{width:100%;min-width:360px}}.sec{{color:#666;font-size:.85em}}.script{{background:#f6f6f6;padding:6px;margin:3px 0;font-size:.9em;white-space:pre-wrap}}table.w th{{width:210px;font-weight:normal;background:#fafafa}}.note{{background:#fff8e0;padding:6px}}</style></head><body>
<h1>Coffee Aoede Style改善 試聴(P0〜P8)</h1>
<p class='note'>FAMILY-X-COFFEE-AOEDE-STYLE-TRIAL-03。試聴用の検証結果です(Productionへは未反映、採用は未決定)。Coffee v3 Advanced Full StoryのPart1を共通サンプルに、声(Aoede)・モデル(gemini-3.8-flash-lite-tts)・原稿・機械的な速度変更なしを全て同一にし、Style文(Prompt)だけを変えた9本です。P0は現行(PD8)の既存音声、P1〜P8は新規。速度は変えない前提で、抑揚・明るさ・明瞭さの変化を聴いて比べてください。WPM=1分あたりの英語の語数。速度の目安はPace Trial-02基準の参照値による暫定表示で、品質PASSを意味しません。</p>
<h2>同一原稿(全9本共通)</h2><div class='script'>{html.escape(script)}</div>
<table><thead><tr><th>ID・特徴</th><th>再生</th><th>測定値・Prompt</th></tr></thead>{rowsh}</table>
</body></html>"""
open(f"{PG}/index.html", "w", encoding="utf-8").write(body)
print(open(f"{OUT}/MEASUREMENTS_03.md", encoding="utf-8").read())
