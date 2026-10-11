# -*- coding: utf-8 -*-
import json, html
OUT = "er053_output/tts_full_story_tone_trial_01"
rows = [json.loads(l) for l in open(f"{OUT}/results_01.jsonl", encoding="utf-8")]
DESC = {"F0": "現行(落ち着いたニュース調)", "F1": "少し明るい", "F1.5": "中間(穏やかに明るく親しみやすい)", "F2": "明るく親しみやすい"}
ms = rows[0]["tts_input_text"]
cards = "\n".join(
 f'<div class="c"><h3>{r["sample_id"]}: {DESC[r["sample_id"]]}</h3>'
 f'<audio controls preload="none" style="min-width:360px;width:100%" src="{r["sample_id"]}.mp3"></audio>'
 f'<p class="s">Style指示: {html.escape(r["style"])}</p><p class="s">長さ {r["duration_s_raw"]}秒</p></div>' for r in rows)
page = f"""<!DOCTYPE html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Full Story トーン比較 Trial</title>
<style>body{{font-family:Meiryo,sans-serif;max-width:760px;margin:1em auto;padding:0 1em;line-height:1.6;color:#111}}
.c{{border:1px solid #ccc;border-radius:8px;padding:.6em 1em;margin:.8em 0}}h3{{margin:.2em 0}}.s{{font-size:.85em;color:#444;margin:.3em 0}}.m{{background:#f4f4f4;padding:.6em 1em;border-radius:6px}}</style></head><body>
<h1>Full Story トーン比較 Trial</h1>
<p>Voice(Aoede)・モデル(gemini-3.8-flash-lite-tts)・原稿・通常速度・音量は全案同じ。違うのはStyle指示だけです(Trial、Production未採用)。</p>
<p class="m">原稿: {html.escape(ms)}</p>
{cards}
</body></html>"""
open("user_test/tts_full_story_tone_01/index.html", "w", encoding="utf-8").write(page)
