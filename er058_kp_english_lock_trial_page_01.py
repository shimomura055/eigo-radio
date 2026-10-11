# -*- coding: utf-8 -*-
"""Trial D 試聴ページ生成(ローカル処理のみ、API/Production書込なし)。Blindにしない(版と内容は明記)、名称は中立(版1〜4)。"""
import os, sys, json, html
sys.path.insert(0, os.getcwd())
import numpy as np
import soundfile as sf
import er002_common as common
import er003_b1_p9a_audio as p9a
import er058_kp_english_lock_trial_01 as T

PAGE = f"{T.ROOT}/user_test/kp_english_lock_trial_01"
AUD = f"{PAGE}/audio"
os.makedirs(AUD, exist_ok=True)
TARGET = json.load(open(f"{T.G.TONE}/audit/gain_report.json", encoding="utf-8"))["target_rms"]
P = T.prompts()
rows = {r["id"]: r for r in json.load(open(f"{T.OUT}/eval_D.json", encoding="utf-8"))}
LBL = {"V1": "版1", "V2": "版2", "V3": "版3", "V4": "版4"}
DESC = {"V1": "現行Productionの指示文(Minimal)", "V2": "「ひとかたまりで・音程の動きを小さく」だけの短い指示", "V3": "版2に、冠詞の弱形・過剰強調防止・英語として発音・語末まで発話を短く足した版(簡潔統合)",
        "V4": "版2に、現行の冠詞弱形の長文と現行English Lock文を逐語で足した版(完全統合)"}


def norm(mono):
    gain = p9a.compute_gain_for_target_rms(mono, TARGET)
    return p9a.mono_24k_to_stereo_target(mono * gain)


H = ["""<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Key Phrase英語 Prompt比較 Trial D(試聴用・Trial)</title>
<style>body{font-family:sans-serif;max-width:980px;margin:1em auto;padding:0 1em;line-height:1.5}h2{border-bottom:2px solid #888;margin-top:1.5em}
.set{border:1px solid #ccc;border-radius:6px;padding:.4em 1em;margin:.8em 0}.a{display:flex;align-items:center;gap:.6em;margin:.2em 0;flex-wrap:wrap}.a .lbl{min-width:4em;font-weight:bold}
.a .v{font-size:.8em;color:#06c;min-width:4em}.a .s{font-size:.9em;color:#333;min-width:9em}.a .m{font-size:.75em;color:#555;flex:1 1 18em}audio{height:32px;min-width:360px}pre{white-space:pre-wrap;background:#f5f5f5;padding:.5em;font-size:.8em}.note{color:#555;font-size:.9em}</style></head><body>
<h1>Key Phrase英語 Prompt比較 Trial D(試聴用・Trial)</h1>
<p class="note">Production未採用のTrialです。8語を4種類の指示文で各1回生成しました(同一model=gemini-3.8-flash-lite-tts、Voice=Aoede、Standard同期、Productionと同一のtrim)。順番は版1〜4で固定、Blindではありません。
各行にASR結果(OpenAI Primary、逐語prompt付き)とローカルwhisper転写を併記しています。自動評価は全32件で内容一致でしたが、自然さ・リズム・語尾・強調・明瞭さは耳で確認してください(ピッチ解析は未実施)。どれが良いかはこのページでは判定していません。標本は各1回のみで統計的な優劣は言えません。</p>
<h2>各版の指示文</h2>"""]
for v, (n, s) in P.items():
    H.append(f"<details><summary>{LBL[v]}: {html.escape(DESC[v])}(文字数{len(s)})</summary><pre>{html.escape(s)}</pre></details>")
for i, w in enumerate(T.WORDS, 1):
    H.append(f'<h2>{i}. {html.escape(w)}</h2><p class="note">選定理由: {html.escape(T.WHY[w])}</p><div class="set">')
    for v in P:
        id_ = f"{v}_{i}"
        mono = common.read_wav_float(f"{T.RAW}/{id_}.wav")[0]
        st = norm(mono)
        sf.write(f"{AUD}/{id_}.mp3", np.clip(st, -1, 1), p9a.TARGET_SAMPLE_RATE, format="MP3")
        r = rows[id_]
        meta = f"長さ{r['dur']}s / ASR: {r['asr']!r}({r['classification']}) / local whisper: {r['whisper_small']!r}"
        H.append(f'<div class="a"><span class="lbl">{LBL[v]}</span><audio controls preload="none" src="audio/{id_}.mp3"></audio><span class="v">Aoede</span>'
                 f'<span class="s">{html.escape(r["word"])}</span><span class="m">{html.escape(meta)}</span></div>')
    H.append("</div>")
H.append("</body></html>")
open(f"{PAGE}/index.html", "w", encoding="utf-8").write("\n".join(H))
print("ok", len(os.listdir(AUD)))
