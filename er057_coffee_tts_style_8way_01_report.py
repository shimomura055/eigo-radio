# -*- coding: utf-8 -*-
import os, json, hashlib
ROOT = os.path.dirname(os.path.abspath(__file__)); O = os.path.join(ROOT, "er057_output", "coffee_tts_style_8way_01")
m = json.load(open(f"{O}/measurements_02.json", encoding="utf-8")); T = m["takes"]
gl = [json.loads(l) for l in open(f"{O}/generation_log_02.jsonl", encoding="utf-8")]
ok = [r for r in gl if r.get("status") == "OK"]
tts = sum(r["tts_cost_jpy"] for r in ok); asr = sum(r["asr_cost_jpy_est"] for r in ok)
cost = {"tts_jpy": round(tts, 3), "asr_jpy_est": round(asr, 3), "total_jpy_est": round(tts + asr, 3), "budget_jpy": 60, "n_calls": len(ok), "n_tech_failures": sum(1 for r in gl if r.get("event") == "TTS_TECH_FAILURE"),
        "input_tokens": sum(r["input_tokens"] for r in ok), "output_tokens": sum(r["output_tokens"] for r in ok),
        "model_versions": sorted({r["model_version"] for r in ok}), "pricing": "gemini-3.8-flash-lite-tts Standard $0.5/$6.0 per 1M, USD/JPY 160; ASR推定式(請求画面未確認)", "estimate_median": 43.4}
json.dump(cost, open(f"{O}/cost_02.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
pre = json.load(open(f"{O}/state_guard_pre.json")); post = json.load(open(f"{O}/state_guard_post.json"))
json.dump({"pre": pre, "post": post, "changed": [k for k in pre if pre[k] != post[k]], "note": "本Trialは上記へ書込まない(B.patch_validator_telemetryでprocess内リストへ差替)。changedが空でない場合は並行別タスク(④/③等)の更新。"}, open(f"{O}/state_guard_02.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
def avg(a, b): return round((a + b) / 2, 1)
L = ["# MEASUREMENTS_02 (FAMILY-X-COFFEE-TTS-STYLE-8WAY-AB-TRIAL-01 委任_02、機械指標。費用0、faster-whisper small local)", "",
     "注意: 数値だけで最良を決めない(足切りしない)。選抜はユーザー試聴。Std=減速6%適用後(聴取音声)の実測で、尺・無音は減速前の約1.06倍。Std 6%減速後ASRは省略(減速前Primary ASR 1回のみ、Trial限定)。WPM=ref語数(Std117/Adv131)/尺。",
     "無音: -40dBFS以下・50ms以上。文末無音=参照文末とASR語のdifflib整列で特定(最終文除く)。中=文末以外の小無音。", "",
     "## 1. 候補別サマリー(Take1 / Take2)", "", "| 候補 | Lv | WPM T1/T2 | 差 | 発話WPM(500ms超除外) | 文末無音平均ms T1/T2 | 最大ms | 文中無音本数 T1/T2 | 総時間s T1/T2 | 300ms+本数 | 800ms+長無音 | Primary ASR | 警告 |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
for c in "ABCDEFGH":
    for lv in ("std", "adv"):
        a, b = T[f"{c}_{lv}_part1_t1"], T[f"{c}_{lv}_part1_t2"]
        w = []
        for t, tag in ((a, "T1"), (b, "T2")):
            if not t["asr_verified"]: w.append(f"{tag}:ASR NG({t['primary_asr']})")
            if t["wpm"] > 195: w.append(f"{tag}:WPM>195")
            if t["wpm"] < 150: w.append(f"{tag}:WPM<150")
            if not t["tail_last3_match"]: w.append(f"{tag}:末尾不一致")
            if t["anomaly_medium_plus"]: w.append(f"{tag}:異音medium")
        L.append(f"| {c} | {lv} | {a['wpm']}/{b['wpm']} | {abs(a['wpm']-b['wpm']):.1f} | {a['speech_wpm500']}/{b['speech_wpm500']} | {a['end_pause_ms']['mean']}/{b['end_pause_ms']['mean']} | {a['end_pause_ms']['max']}/{b['end_pause_ms']['max']} | {a['mid']['n']}/{b['mid']['n']} | {a['mid']['total_s']}/{b['mid']['total_s']} | {a['mid']['n300']}/{b['mid']['n300']} | {len(a['long800'])}/{len(b['long800'])} | {a['primary_asr']}/{b['primary_asr']} | {'; '.join(w) or '-'} |")
for lv, nm in (("std", "現行v5 Std Part1(slow6, sha 6546b00f7805)"), ("adv", "現行v5 Adv Part1(sha 8b616edca69c)")):
    v = m["v5"][lv]; L.append(f"| v5参考 | {lv} | {v['wpm']} | - | {v['speech_wpm500']} | {v['end_pause_ms']['mean']} | {v['end_pause_ms']['max']} | {v['mid']['n']} | {v['mid']['total_s']} | {v['mid']['n300']} | {len(v['long800'])} | (既存) | {nm} |")
L += ["", "## 2. 文末無音分布(ms区分 0-50/50-150/150-300/300-500/500-800/800-1200/1200+)", "", "| take | 分布 | 平均/中央/最大 |", "|---|---|---|"]
for k, t in T.items():
    e = t["end_pause_ms"]; L.append(f"| {k} | {list(e['hist'].values())} | {e['mean']}/{e['median']}/{e['max']} |")
for lv in ("std", "adv"):
    e = m["v5"][lv]["end_pause_ms"]; L.append(f"| v5_{lv} | {list(e['hist'].values())} | {e['mean']}/{e['median']}/{e['max']} |")
L += ["", "## 3. 800ms以上の長無音位置(文末・文中問わず)", "", "| take | 位置s | ms | 直前語→直後語 |", "|---|---|---|---|"]
for k, t in list(T.items()) + [(f"v5_{lv}", m["v5"][lv]) for lv in ("std", "adv")]:
    for x in t["long800"]: L.append(f"| {k} | {x['t']} | {x['ms']} | {x['prev']} -> {x['next']} |")
L += ["", "## 4. 音量・語尾・異音", "", "| take | RMS dBFS | peak dBFS | 末尾3語一致 | ASR語数 | 異音検知(全/medium以上) |", "|---|---|---|---|---|---|"]
for k, t in list(T.items()) + [(f"v5_{lv}", m["v5"][lv]) for lv in ("std", "adv")]:
    L.append(f"| {k} | {t['rms_dbfs']} | {t['peak_dbfs']} | {t['tail_last3_match']} | {t['asr_words']} | {len(t['anomalies'])}/{t['anomaly_medium_plus']} |")
L += ["", "## 5. Take間ばらつき(候補x Lv)", "", "| 候補/Lv | WPM差 | 文末無音平均差ms | 文中無音本数 | 800ms+本数 |", "|---|---|---|---|---|"]
for k, v in m["by_cand_level"].items(): L.append(f"| {k} | {v['wpm_diff']} | {v['end_mean_diff']} | {v['mid_n']} | {v['long800_n']} |")
L += ["", "## 6. 候補ごとの機械指標上の所見(目標1=間/3=明瞭さ/5=自然速度のみ機械指標あり。2・4(明るさ・抑揚)は聴感でのみ判断。数値だけで最良を決めない)", ""]
def mean2(c, lv, f): return round((f(T[f"{c}_{lv}_part1_t1"]) + f(T[f"{c}_{lv}_part1_t2"])) / 2, 1)
L += ["| 候補 | WPM平均 Std/Adv | 文末無音平均 Std/Adv | 文中無音総時間s Std/Adv | 所見 |", "|---|---|---|---|---|"]
v5s, v5a = m["v5"]["std"], m["v5"]["adv"]
notes = {}
for c in "ABCDEFGH":
    ws, wa = mean2(c, "std", lambda t: t["wpm"]), mean2(c, "adv", lambda t: t["wpm"])
    es, ea = mean2(c, "std", lambda t: t["end_pause_ms"]["mean"]), mean2(c, "adv", lambda t: t["end_pause_ms"]["mean"])
    ms, ma = mean2(c, "std", lambda t: t["mid"]["total_s"]), mean2(c, "adv", lambda t: t["mid"]["total_s"])
    s = []
    s.append(f"v5比 文末無音 Std {es-v5s['end_pause_ms']['mean']:+.0f}ms / Adv {ea-v5a['end_pause_ms']['mean']:+.0f}ms、文中無音総時間 Std {ms-v5s['mid']['total_s']:+.1f}s / Adv {ma-v5a['mid']['total_s']:+.1f}s")
    if max(ws, wa) > 195 or max(T[f'{c}_{lv}_part1_t{n}']['wpm'] for lv in ('std', 'adv') for n in (1, 2)) > 195: s.append("WPM195超のtakeあり(速すぎ注意)")
    if min(T[f'{c}_{lv}_part1_t{n}']['wpm'] for lv in ('std', 'adv') for n in (1, 2)) < 150: s.append("WPM150未満のtakeあり")
    bad = [k for k, t in T.items() if t["cand"] == c and not t["asr_verified"]]
    if bad: s.append("ASR NG: " + ",".join(bad))
    L.append(f"| {c} | {ws}/{wa} | {es}/{ea} | {ms}/{ma} | {'; '.join(s)} |")
L += ["", f"生成: raw wav sha256は32件すべて異なる={m['raw_sha_all_distinct']}。v5参考sha一致: std {v5s['sha12']}, adv {v5a['sha12']}。"]
open(f"{O}/MEASUREMENTS_02.md", "w", encoding="utf-8").write("\n".join(L))
print(json.dumps(cost, ensure_ascii=False)); print(json.dumps(post == pre))
