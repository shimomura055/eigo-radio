# -*- coding: utf-8 -*-
"""MEASUREMENTS_01.md + 試聴ページ生成(API費用0)。"""
import os, sys, json, html
ROOT = "C:/Users/tensh/eigo-radio"; sys.path.insert(0, ROOT)
import er057_kp_expl_style_trial_01_gen as G
OUT = f"{ROOT}/er057_output/kp_en_explanation_style_trial_01"; PG = f"{ROOT}/user_test/coffee_kp_explanation_style_trial_01"
M = json.load(open(f"{OUT}/measurements.json", encoding="utf-8"))
ids = ["P0"] + [f"P{i}" for i in range(1, 9)]
JP = {"P0": "現行Variant B(基準・再生成)", **{k: v[0] for k, v in G.ADD.items()}}
FEAT = {"P0": "現行の英語解説Style(KEY_PHRASE_EXPLANATION_EN)をv4と同条件(sync)で再生成。比較基準。", "P1": "文の途中で長く止まらず1つの連続した句として言う指示を追加。", "P2": "語どうしを自然につなぎ、句間は最小限の息継ぎだけにする指示を追加。",
        "P3": "文頭から文末まで途中で止まらず流れる指示を追加。", "P4": "最後の語をはっきり自然に終え、尻すぼみ・引き延ばしをしない指示を追加(文末処理)。", "P5": "親切な先生が短く自然に定義を説明する口調の指示を追加(速度・無音の直接指示なし)。",
        "P6": "P1(連続性)+P4(文末処理)。", "P7": "P2(つながり)+P5(説明口調)。", "P8": "P1+P4+P5 のバランス型。"}
L = ["# MEASUREMENTS_01(FAMILY-X-COFFEE-KP-EN-EXPLANATION-STYLE-TRIAL-01)", "",
     "測定: 全パターン同一script `er057_kp_expl_style_trial_01_measure.py`(+lib `er057_kp_expl_lib_01.py`)。-40dBFS / frame20ms / hop10ms(`measure_wpm_01.py`方式を再実装、元scriptはimport時に全処理が走るため再利用不可)。語数=tts_input空白区切り英数字語(7語)。",
     "指標定義: 発話WPM(500ms)= 語数/(総秒-500ms以上の無音)。本clipは短く500ms以上の無音が無いため全体WPMと同値(表では省略)。**発話WPM(core)= 語数/(先頭・末尾の無音を除いた区間から、文中150ms以上の無音を除いた秒)**=本clipで発話速度を無音と切り分ける実質の主指標。全体WPM=語数/総秒(先頭・末尾の無音含む)。",
     "P0比%は各パターンr1(試聴ページの音声)対P0 r1。3サンプル平均(r1〜r3)は同一Prompt再生成のノイズ対策(候補追加ではない)。", ""]
for kp, r in M.items():
    rows, agg = r["rows"], r["agg3"]
    L += [f"## KP{kp}: `{r['text']}` ({r['words']}語)" + (" ← 主対象(無音測定で選定)" if kp == "4" else " ← 2件目"), "",
          "### A. 試聴音声(r1)の測定", "", "| ID | 総秒 | 全体WPM | 発話WPM(core) | core P0比% | 全体WPM P0比% | 文中無音(>=150ms)数/計s/最長s | 先頭/末尾無音s | 解説前後の境界無音s(前/後) | Primary ASR | peak(gain後) |", "|" + "---|" * 11]
    for c in ["P0v4"] + ids:
        m = rows[c]; mx = max([q["dur"] for q in m["mid150"]], default=0)
        asr = "v4実音声(参考)" if c == "P0v4" else f"{m['asr']['classification']}({'verified' if m['asr']['verified'] else 'NOT'}, a{m['asr']['attempt']})"
        L.append(f"| {c} | {m['duration_s']} | {m['wpm_total']} | {m['speech_wpm_core']} | {m['d_core_wpm_pct']:+.1f} | {m['d_wpm_total_pct']:+.1f} | {m['mid150_n']}/{m['mid150_total_s']}/{mx} | {m['head_s']}/{m['tail_s']} | {m['gap_before_s']}/{m['gap_after_s']} | {asr} | {m['peak_after_gain']} |")
    L += ["", f"### B. 3サンプル平均(r1〜r3、同一Prompt。P0の3サンプル間ばらつき: core WPM {r['noise_P0_3samples']['core_wpm']}、文中無音計s {r['noise_P0_3samples']['mid150_total_s']})", "",
          "| ID | core WPM 平均(各回) | core P0平均比% | 全体WPM平均 | 全体P0平均比% | 総秒平均 | 文中無音計s 平均(各回) | 文中無音 P0平均差s | 全ASR verified |", "|" + "---|" * 9]
    for c in ids:
        a = agg[c]
        L.append(f"| {c} | {a['core_wpm_mean']} ({', '.join(str(x) for x in a['core_wpm_each'])}) | {a['d_core_wpm_pct_vs_P0mean']:+.1f} | {a['wpm_total_mean']} | {a['d_wpm_total_pct_vs_P0mean']:+.1f} | {a['duration_mean']} | {a['mid150_total_mean_s']} ({', '.join(str(x) for x in a['mid150_total_each'])}) | {a['d_mid150_total_s_vs_P0mean']:+.3f} | {a['all_asr_verified']} |")
    L += [""]
open(f"{OUT}/MEASUREMENTS_01.md", "w", encoding="utf-8").write("\n".join(L))


def tr(kp, c):
    r = M[kp]; m = r["rows"][c]; a = r["agg3"].get(c)
    jp = "v4実使用音声(参考・現行Production経路BATCH)" if c == "P0v4" else JP[c]
    feat = "Coffee v4 Advanced に実際に入っている解説clip(参考)。" if c == "P0v4" else FEAT[c]
    st = G.P0 if c in ("P0", "P0v4") else G.style_of(c)
    mx = max([q["dur"] for q in m["mid150"]], default=0)
    ag = ""
    if a:
        ag = (f"<tr><th>3サンプル平均(同一Prompt)</th><td>core WPM <b>{a['core_wpm_mean']}</b> (P0平均比 {a['d_core_wpm_pct_vs_P0mean']:+.1f}%) / 全体WPM {a['wpm_total_mean']} (P0平均比 {a['d_wpm_total_pct_vs_P0mean']:+.1f}%) / 総秒 {a['duration_mean']} / 文中無音計 {a['mid150_total_mean_s']}秒 (P0平均差 {a['d_mid150_total_s_vs_P0mean']:+.3f}秒)</td></tr>")
    asr = "v4実音声(参考)" if c == "P0v4" else f"{m['asr']['classification']} ({'verified' if m['asr']['verified'] else 'NOT verified'})"
    return (f"<tr id='kp{kp}_{c}'><td class='id'><b>{c}</b><br>{html.escape(jp)}<br><span class='sec'>{html.escape(feat)}</span></td>"
            f"<td class='play'>Phrase→解説→Phrase<br><audio controls preload='none' src='audio/kp{kp}_{c}_seq.mp3'></audio><br>解説のみ<br><audio controls preload='none' src='audio/kp{kp}_{c}_solo.mp3'></audio></td>"
            f"<td><table class='w'><tr><th>総再生秒(解説のみ)</th><td>{m['duration_s']} 秒 (P0比 {m['d_duration_s']:+.2f})</td></tr>"
            f"<tr><th>発話WPM(core、無音除く)</th><td><b>{m['speech_wpm_core']}</b> (P0比 {m['d_core_wpm_pct']:+.1f}%)</td></tr>"
            f"<tr><th>全体WPM(無音含む)</th><td>{m['wpm_total']} (P0比 {m['d_wpm_total_pct']:+.1f}%)</td></tr>"
            f"<tr><th>文中無音(150ms以上)</th><td>{m['mid150_n']}回 計{m['mid150_total_s']}秒 最長{mx}秒</td></tr>"
            f"<tr><th>先頭/末尾の無音</th><td>{m['head_s']} / {m['tail_s']} 秒 (解説前後の境界無音 {m['gap_before_s']} / {m['gap_after_s']} 秒、固定0.4秒pause含む)</td></tr>"
            f"{ag}<tr><th>ASR / 音質</th><td>{asr} / peak {m['peak_after_gain']} (gain後)</td></tr></table>"
            f"<details><summary>Style全文</summary><div class='script'>{html.escape(st)}</div></details></td></tr>")


secs = ""
for kp, r in M.items():
    secs += f"<h2>KP{kp}: 「{html.escape(r['text'])}」" + (" (主対象)" if kp == "4" else " (2件目)") + f"</h2><p>同一原稿(全行共通): <b>{html.escape(r['text'])}</b> ({r['words']}語)。Phrase clipはv4のものを再利用(gain・間の0.4秒pauseもProduction同一規則)。</p><table><thead><tr><th>ID・特徴</th><th>再生</th><th>測定値・Style</th></tr></thead>"
    secs += "".join(tr(kp, c) for c in ["P0v4"] + ids) + "</table>"
CSS = "body{font-family:sans-serif;max-width:1150px;margin:1em auto;padding:0 1em;line-height:1.5}table{border-collapse:collapse;width:100%;margin-bottom:1.2em}th,td{border:1px solid #ccc;padding:6px;vertical-align:top;text-align:left}td.id{width:200px}td.play{min-width:380px;width:380px}td.play audio{width:100%;min-width:360px}.sec{color:#666;font-size:.85em}.script{background:#f6f6f6;padding:6px;margin:3px 0;font-size:.9em;white-space:pre-wrap}table.w th{width:210px;font-weight:normal;background:#fafafa}.note{background:#fff8e0;padding:6px}"
NOTE = ("FAMILY-X-COFFEE-KP-EN-EXPLANATION-STYLE-TRIAL-01。試聴用の検証結果です(Productionへは未反映、採用は未決定)。Advanced Key Phrase「英語Phrase→英語解説→英語Phrase」の真ん中の解説clipだけを、Style文(Prompt)を変えて作り直し、Phrase(v4のもの)の間に差し替えて連続再生できるようにしました。"
        "声(Aoede)・モデル(gemini-3.8-flash-lite-tts)・解説原稿・Phrase・pause(0.4秒)は全て同一です。WPM=1分あたりの英語の語数。"
        "<b>注意</b>: 解説clipは7語・約3秒と短く、TTS生成ごとのばらつきが大きいため、各パターンは同一Promptを3回生成した平均値も併記しています。解説の前後の無音は、機械的に付く固定margin(約0.3秒)+固定pause(0.4秒)が大半で、Styleで変わるのは主に文の途中の短い間です。測定値は暫定で、品質PASSを意味しません。聴いて判断してください。")
body = f"<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><title>Coffee KP英語解説 Style改善 試聴(P0〜P8)</title><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body><h1>Coffee KP英語解説 Style改善 試聴(P0〜P8)</h1><p class='note'>{NOTE}</p>{secs}</body></html>"
os.makedirs(PG, exist_ok=True)
open(f"{PG}/index.html", "w", encoding="utf-8").write(body)
print("ok", len(body))
