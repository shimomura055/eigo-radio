# -*- coding: utf-8 -*-
"""FAMILY-X-COFFEE-KP-EN-EXPLANATION-PACING-TRIAL-01 試聴ページ生成(API 0)。
Trial dirの生成wav + 既存Production完成音声(参照、read-only)を mp3(lameenc) 化して user_test/coffee_kp_pacing_trial_01/ へ置き、
外部JS不要のindex.htmlを作る。主観評価は未実施(ユーザー試聴待ち)。"""
import html, json, os, sys
import lameenc
import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
TRIAL = "er080_output/coffee_kp_en_explanation_pacing_trial_01"
PG = "user_test/coffee_kp_pacing_trial_01"
PIDS = [f"p{i}" for i in range(8)]


def to_mp3(src, dst, br=128):
    x, sr = sf.read(src, dtype="int16", always_2d=True)
    enc = lameenc.Encoder()
    enc.set_bit_rate(br)
    enc.set_in_sample_rate(sr)
    enc.set_channels(x.shape[1])
    enc.set_quality(2)
    data = enc.encode(np.ascontiguousarray(x).tobytes()) + enc.flush()
    open(dst, "wb").write(data)


def main():
    plan = json.load(open(f"{TRIAL}/audit/plan.json", encoding="utf-8"))
    M = json.load(open(f"{TRIAL}/metrics.json", encoding="utf-8"))
    res = {}
    for ln in open(f"{TRIAL}/audit/clip_results.jsonl", encoding="utf-8"):
        r = json.loads(ln)
        res[(r["prompt"], r["kp"])] = r
    os.makedirs(f"{PG}/audio", exist_ok=True)
    texts = plan["texts"]
    P = plan["prompts"]

    def fmt(m, k, nd=2):
        v = m.get(k) if m else None
        return "-" if v is None else (f"{v:.{nd}f}" if isinstance(v, float) else str(v))

    def mrow(m):
        if not m or "error" in m:
            return "<td colspan='7'>計測なし</td>"
        return (f"<td>{fmt(m,'total_s')}</td><td>{fmt(m,'wpm_span',0)}</td><td>{fmt(m,'inner_pause_count',0)}</td>"
                f"<td>{fmt(m,'inner_pause_total_s')}</td><td>{fmt(m,'inner_pause_max_s')}</td><td>{fmt(m,'inner_pause_ge200ms_count',0)}</td>"
                f"<td>{fmt(m,'tail_silence_s')}</td>")

    H = ["<!doctype html><html lang='ja'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>",
         "<title>Coffee Advanced KP英語解説 Pacing Trial(8 Prompt x 5本)</title>",
         "<style>body{font-family:sans-serif;max-width:1100px;margin:1em auto;padding:0 1em;line-height:1.5}table{border-collapse:collapse;width:100%;margin:.6em 0}"
         "td,th{border:1px solid #bbb;padding:4px 6px;font-size:.92em;vertical-align:top}th{background:#eee}.ref{background:#f3f3e6}.p0{background:#eef6ff}"
         ".txt{font-size:1.15em;background:#fffbe6;padding:8px;border:1px solid #dc9}.note{background:#fdecea;border:1px solid #d99;padding:8px}"
         "code{font-size:.85em;word-break:break-all}audio{width:230px}nav a{margin-right:1em}</style></head><body>",
         "<h1>Coffee Advanced Key Phrase 英語解説 Pacing Trial</h1>",
         "<p class='note'><b>管理ID FAMILY-X-COFFEE-KP-EN-EXPLANATION-PACING-TRIAL-01 / Status: TRIAL(Production未反映)</b><br>"
         "これはTrial(試聴用の比較)です。<b>主観評価(速度・ポーズ・自然さ)は未実施で、ユーザー試聴待ちです。</b>表の数値は参考値で、優劣の結論ではありません。"
         "Coffeeの現行Production Prompt・音声は変更していません。モデル gemini-3.8-flash-lite-tts / Voice Aoede(現行Production同一)。</p>",
         "<nav>" + "".join(f"<a href='#kp{t['kp']}'>KP{t['kp']}</a>" for t in texts) + "<a href='#prompts'>Prompt一覧</a><a href='#summary'>指標平均</a></nav>"]
    for t in texts:
        kp = t["kp"]
        H.append(f"<h2 id='kp{kp}'>KP{kp}: {html.escape(t['phrase'] or '')}</h2><p class='txt'>{html.escape(t['text'])}</p>")
        H.append("<table><tr><th>候補</th><th>狙い</th><th>再生</th><th>全長(s)</th><th>WPM</th><th>文中ポーズ数</th><th>文中ポーズ計(s)</th><th>最長(s)</th><th>200ms以上</th><th>文末無音(s)</th><th>ASR/QA</th></tr>")
        refm = M["reference_production"].get(f"kp{kp}")
        rmp3 = f"audio/ref_kp{kp}.mp3"
        to_mp3(t["prod_wav"], f"{PG}/{rmp3}")
        H.append(f"<tr class='ref'><td>既存Production完成音声(参照)</td><td>Coffee現行完成版の音声(P0と同一Prompt、別take。同条件の比較結果ではない)</td>"
                 f"<td><audio controls preload='none' src='{rmp3}'></audio></td>{mrow(refm)}<td>-</td></tr>")
        for p in PIDS:
            r = res.get((p, kp))
            m = M["clips"].get(f"{p}/kp{kp}")
            if r and r.get("asr_verified") and os.path.isfile(f"{TRIAL}/audio/{p}/kp{kp:02d}.wav"):
                mp3 = f"audio/{p}_kp{kp}.mp3"
                to_mp3(f"{TRIAL}/audio/{p}/kp{kp:02d}.wav", f"{PG}/{mp3}")
                play = f"<audio controls preload='none' src='{mp3}'></audio>"
                qa = f"OK(試行{r['attempts']}回, {html.escape(str(r.get('audio_classification')))})"
            else:
                play, qa, m = "音声なし(QA不合格または未生成)", f"NG/未生成: {html.escape(str(r.get('status') if r else 'none'))}", None
            H.append(f"<tr class='{'p0' if p=='p0' else ''}'><td><b>{p.upper()}</b>{' (現行Prompt新規生成)' if p=='p0' else ''}</td><td>{html.escape(P[p]['aim'])}</td><td>{play}</td>{mrow(m)}<td>{qa}</td></tr>")
        H.append("</table>")
    H.append("<h2 id='prompts'>Prompt一覧(ユーザー指定の8案、逐語)</h2><table><tr><th>候補</th><th>狙い</th><th>Style文字列</th></tr>")
    for p in PIDS:
        H.append(f"<tr><td>{p.upper()}</td><td>{html.escape(P[p]['aim'])}</td><td><code>{html.escape(P[p]['style'])}</code></td></tr>")
    H.append("</table><h2 id='summary'>候補別 指標平均(5本平均、数値上の傾向のみ)</h2>"
             "<table><tr><th>候補</th><th>n</th><th>全長(s)</th><th>WPM(発話区間)</th><th>文中ポーズ数</th><th>文中ポーズ計(s)</th><th>最長(s)</th><th>200ms以上の数</th><th>文末無音(s)</th></tr>")
    for k, v in M["per_prompt_mean"].items():
        name = "既存Production完成音声(参照)" if k == "prod_existing" else k.upper()
        H.append(f"<tr class='{'ref' if k=='prod_existing' else ''}'><td>{name}</td><td>{v['n']}</td><td>{v['total_s']:.2f}</td><td>{v['wpm_span']:.0f}</td><td>{v['inner_pause_count']:.1f}</td>"
                 f"<td>{v['inner_pause_total_s']:.2f}</td><td>{v['inner_pause_max_s']:.2f}</td><td>{v['inner_pause_ge200ms_count']:.1f}</td><td>{v['tail_silence_s']:.2f}</td></tr>")
    H.append("</table><p>指標の定義: RMS(20ms窓/10ms hop)で発話フレームを判定(clip内p95 dB-35dB超)。文中ポーズ=発話の最初と最後の間の80ms以上の無音。"
             "文末無音=最後の発話以降(Production trim余白0.30s由来を含む)。WPM=語数/発話区間x60。</p>"
             "<p>Trial結果はProduction採用ではありません。採用はユーザーの判断(APPROVED_FOR_PRODUCTION)で別途行います。</p></body></html>")
    open(f"{PG}/index.html", "w", encoding="utf-8").write("\n".join(H))
    print("page ok", len(os.listdir(f"{PG}/audio")), "mp3")


if __name__ == "__main__":
    main()
