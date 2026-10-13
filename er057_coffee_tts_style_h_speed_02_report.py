# -*- coding: utf-8 -*-
import os, json
ROOT = os.path.dirname(os.path.abspath(__file__)); O = os.path.join(ROOT, "er057_output", "coffee_tts_style_h_speed_02")
m = json.load(open(f"{O}/measurements_02.json", encoding="utf-8")); T = m["takes"]; A = m["by_cand_level"]; BL = m["baselines"]; PEN = m["speed_penalties"]
gl = [json.loads(l) for l in open(f"{O}/generation_log_02.jsonl", encoding="utf-8")]
ok = [r for r in gl if r.get("status") == "OK" and not r.get("reused_from")]
tts = sum(r["tts_cost_jpy"] for r in ok); asr = sum(r["asr_cost_jpy_est"] for r in ok)
cost = {"tts_jpy": round(tts, 3), "asr_jpy_est": round(asr, 3), "total_jpy_est": round(tts + asr, 3), "budget_jpy": 60, "n_new_calls": len(ok), "n_reused": sum(1 for r in gl if r.get("reused_from")),
        "n_tech_failures": sum(1 for r in gl if r.get("event") == "TTS_TECH_FAILURE"),
        "input_tokens": sum(r["input_tokens"] for r in ok), "output_tokens": sum(r["output_tokens"] for r in ok),
        "model_requested": sorted({r["model_requested"] for r in ok}), "model_versions": sorted({r["model_version"] for r in ok}), "voice": sorted({r["voice"] for r in ok}),
        "pricing": "gemini-3.8-flash-lite-tts Standard $0.5/$6.0 per 1M, USD/JPY 160; ASR推定式(請求画面未確認)", "estimate_central": 39.55, "estimate_high_plus_retry": 53.39}
json.dump(cost, open(f"{O}/cost_02.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
L = ["# MEASUREMENTS_02 (FAMILY-X-COFFEE-TTS-STYLE-H-SPEED-TRIAL-02 委任_02、機械指標。費用0、faster-whisper small local)", "",
     "注意: 数値だけで最良を決めない(足切りしない)。選抜はユーザー試聴。Std=減速6%適用後(聴取音声)の実測。Std減速後ASRは省略(減速前Primary ASR 1回のみ、Trial限定)。WPM=ref語数(Std117/Adv131)/尺。",
     "無音: -40dBFS以下・50ms以上。文末無音=参照文末とASR語のdifflib整列で特定(最終文除く)。文中=文末以外の小無音。H0 Take1/2は8way(H)の同一音声を再利用(sha一致確認済)。", "",
     "## 0. 基準", "", "| Lv | 現行v5 | H0 Take1 | H0 3take平均 | H0 T1/T2平均(参考) |", "|---|---|---|---|---|"]
for lv in ("std", "adv"): b = BL[lv]; L.append(f"| {lv} | {b['v5_wpm']} | {b['h0_t1_wpm']} | {b['h0_mean3']} | {b['h0_mean_t1t2']} |")
L += ["", "## 1. 候補別WPM(3take)", "", "| 候補 | Lv | T1/T2/T3 | 平均 | 最小 | 最大 | 最大差 | 最速take | 速度減点(180達成のため現行より速くしない) |", "|---|---|---|---|---|---|---|---|---|"]
for c in ["H0", "H1", "H2", "H3", "H4", "H5"]:
    for lv in ("std", "adv"):
        a = A[f"{c}_{lv}"]; L.append(f"| {c} | {lv} | {'/'.join(str(x) for x in a['wpm'])} | {a['wpm_mean']} | {a['wpm_min']} | {a['wpm_max']} | {a['wpm_range']} | T{a['fastest_take']} ({a['fastest_wpm']}) | {'; '.join(PEN[f'{c}_{lv}']) or '-'} |")
L += ["", "## 2. 無音・語尾・ASR(3take集約)", "", "| 候補 | Lv | 文末無音平均ms T1/T2/T3 | 3take平均 | 中央値平均 | 最大ms | 文中無音本数 | 文中総時間s | 300ms+本数 | 800ms+本数 | ASR NG take | 末尾語が長いtake(参考) |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
for c in ["H0", "H1", "H2", "H3", "H4", "H5"]:
    for lv in ("std", "adv"):
        a = A[f"{c}_{lv}"]; L.append(f"| {c} | {lv} | {'/'.join(str(x) for x in a['end_mean'])} | {a['end_mean_avg']} | {a['end_median_avg']} | {a['end_max']} | {'/'.join(str(x) for x in a['mid_n'])} | {'/'.join(str(x) for x in a['mid_total_s'])} | {'/'.join(str(x) for x in a['n300'])} | {'/'.join(str(x) for x in a['long800_n'])} | {a['asr_ng'] or '-'} | {['T'+str(x) for x in a['last_long']] or '-'} |")
for lv in ("std", "adv"):
    v = m["v5"][lv]; e = v["end_pause_ms"]; L.append(f"| v5参考 | {lv} | {e['mean']} | {e['mean']} | {e['median']} | {e['max']} | {v['mid']['n']} | {v['mid']['total_s']} | {v['mid']['n300']} | {len(v['long800'])} | (既存) | - |")
L += ["", f"末尾語継続長の中央値(全take): {m['last_word_median_ms']}ms。中央値の1.5倍超を参考フラグ(ASR語タイムスタンプ依存で精度は低い)。", "",
      "## 3. 文末無音分布(ms区分 0-50/50-150/150-300/300-500/500-800/800-1200/1200+)", "", "| take | 分布 | 平均/中央/最大 |", "|---|---|---|"]
for k, t in T.items():
    e = t["end_pause_ms"]; L.append(f"| {k} | {list(e['hist'].values())} | {e['mean']}/{e['median']}/{e['max']} |")
for lv in ("std", "adv"):
    e = m["v5"][lv]["end_pause_ms"]; L.append(f"| v5_{lv} | {list(e['hist'].values())} | {e['mean']}/{e['median']}/{e['max']} |")
L += ["", "## 4. 800ms以上の長無音位置", "", "| take | 位置s | ms | 直前語->直後語 |", "|---|---|---|---|"]
for k, t in list(T.items()) + [(f"v5_{lv}", m["v5"][lv]) for lv in ("std", "adv")]:
    for x in t["long800"]: L.append(f"| {k} | {x['t']} | {x['ms']} | {x['prev']} -> {x['next']} |")
L += ["", "## 5. 音量・語尾・異音", "", "| take | RMS dBFS | peak dBFS | 末尾3語一致 | ASR語数 | 末尾語/継続ms | 異音(全/medium+) | Primary ASR |", "|---|---|---|---|---|---|---|---|"]
for k, t in list(T.items()) + [(f"v5_{lv}", m["v5"][lv]) for lv in ("std", "adv")]:
    L.append(f"| {k} | {t['rms_dbfs']} | {t['peak_dbfs']} | {t['tail_last3_match']} | {t['asr_words']} | {t['last_word']}/{t['last_word_dur_ms']} | {len(t['anomalies'])}/{t['anomaly_medium_plus']} | {t.get('primary_asr', '(既存)')} |")
L += ["", f"生成: 新規32件のraw wav sha256を含む全{m['n_takes']}件のraw sha256がすべて異なる={m['raw_sha_all_distinct']}。"]
open(f"{O}/MEASUREMENTS_02.md", "w", encoding="utf-8").write("\n".join(L))
print(json.dumps(cost, ensure_ascii=False))
