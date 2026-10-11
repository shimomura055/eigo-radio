# -*- coding: utf-8 -*-
import json, html
OUT = "er053_output/tts_voice_tone_brightness_trial_01"
rows = [json.loads(l) for l in open(f"{OUT}/results_01.jsonl", encoding="utf-8")]
LEVEL = {"J0_CURRENT": "0 現行(J3)", "J1_BRIGHT": "1 少し明るい", "J2_BRIGHT": "2 明るく親しみやすい", "J3_BRIGHT": "3 かなり明るく軽快",
         "E0_CURRENT": "0 現行", "E1_UPBEAT": "1 少し明るい", "E2_UPBEAT": "2 明るく親しみやすい", "E3_UPBEAT": "3 かなり明るく軽快"}
def block(lang, title):
    s = [f"<h2>{title}</h2>"]
    for r in rows:
        if r["language"] != lang: continue
        s.append(f'<div class="c"><h3>{r["sample_id"]}(トーン水準 {LEVEL[r["sample_id"]]})</h3>'
                 f'<audio controls preload="none" style="min-width:360px;width:100%" src="{r["sample_id"]}.mp3"></audio>'
                 f'<p class="s">Style指示: {html.escape(r["style"])}</p>'
                 f'<p class="s">長さ {r["duration_s_raw"]}秒 / ASR: {r["asr_classification"]}</p></div>')
    return "\n".join(s)
ja = rows[0]["manuscript"]; en = [r for r in rows if r["language"] == "en"][0]["manuscript"]
page = f"""<!DOCTYPE html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Family X 声のトーン(明るさ)比較 Trial</title>
<style>body{{font-family:Meiryo,"Hiragino Kaku Gothic ProN",sans-serif;max-width:760px;margin:1em auto;padding:0 1em;line-height:1.6;color:#111}}
.c{{border:1px solid #ccc;border-radius:8px;padding:.6em 1em;margin:.8em 0}}h3{{margin:.2em 0}}.s{{font-size:.85em;color:#444;margin:.3em 0}}.m{{background:#f4f4f4;padding:.6em 1em;border-radius:6px}}</style></head><body>
<h1>声のトーン(明るさ)比較 Trial</h1>
<p>Voice・TTSモデル(gemini-3.8-flash-lite-tts)・原稿・速度・音量はすべて同じ。違うのはStyle指示だけです。0が現行、数字が大きいほど明るくなる想定です(Trial、Production未採用)。</p>
<h2>日本語ナレーター(Aoede、Standard想定)</h2>
<p class="m">原稿: {html.escape(ja)}</p>
{block("ja", "日本語 4案")[len("<h2>日本語 4案</h2>"):]}
<h2>英語 Preview/Comment(Charon、Advanced想定)</h2>
<p class="m">原稿: {html.escape(en)}</p>
{block("en", "英語 4案")[len("<h2>英語 4案</h2>"):]}
<h2>旧日本語TTS参考音源</h2>
<p>未特定(ユーザーが好評価した旧方式の日本語ナレーター音源をSSOTから特定できなかったため、掲載なし)。</p>
</body></html>"""
open("user_test/tts_voice_tone_brightness_01/index.html", "w", encoding="utf-8").write(page)
tot = sum(r.get("est_cost_usd", 0) for r in rows)
print(len(page), "est_tts_usd", round(tot, 5), "jpy", round(tot * 160, 2))
