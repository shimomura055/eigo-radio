# -*- coding: utf-8 -*-
"""FAMILY-X-SELECTED-4 委任_04 H1: ⑨Std full_story_part3_k2 HR試聴ページ(API 0)。掲載=判断対象音声のみ(PM_GOVERNANCE 30-5、er_hr_listing_policy_01経由)。"""
import html, json, os, subprocess, sys
sys.path.insert(0, os.getcwd())
import imageio_ffmpeg
import er_hr_listing_policy_01 as hrl
FF = imageio_ffmpeg.get_ffmpeg_exe()
A = "er019_output/family_x_audio_production_wiring_01/meta_waddle_world__run_fx4_01/a2/narration/attempts/"
OUT = "user_test/family_x_meta_waddle_world_hr_01/"
TAKES = [
    # 試行1(減速前=ASR合格)を6%減速した、実際に採用される形の音声。減速後ASRが's欠落と転写したため自動では確定できず、耳での判断を求める(ASR NGだが判断要求を明示)
    {"id": "t1_slowed", "asr_state": "TRUE_CONTENT_MISMATCH(減速後ASR: 's脱落のみ)", "user_judgment_requested": True, "file": A + "full_story_part3_k2_attempt2_postslowdown.wav"},
    # 試行2・3: 音声自体に's無し(ASR転写でも'sなし・Secondary未承認)=判断対象でないため非掲載
    {"id": "t2", "asr_state": "TRUE_CONTENT_MISMATCH"},
    {"id": "t3", "asr_state": "TRUE_CONTENT_MISMATCH"},
]
LISTED, OMITTED = hrl.select_listing_takes(TAKES)
subprocess.run([FF, "-y", "-loglevel", "error", "-i", TAKES[0]["file"], "-b:a", "96k", OUT + "audio/k2_t1_slowed.mp3"], check=True)
e = html.escape
TEXT = "We still do not know if it will become a craze like Tamagotchi. Will It's free, so I'll try it turn into I want to see this pet for a little while today, too? A place to try it out and a seat kept for it every day are different. What is missing from an adult's smartphone? A new resident? Or a little room in the day to care about someone?"
text_html = e(TEXT).replace("adult&#x27;s", "<b style='color:#d00'>adult&#x27;s</b>")
page = f"""<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>メタ(AIペット)Standard 要判断1音声(Human Review用)</title><style>body{{font-family:sans-serif;max-width:900px;margin:1em auto;padding:0 .6em;line-height:1.6}}td,th{{border:1px solid #bbb;padding:5px;vertical-align:top}}table{{border-collapse:collapse;width:100%}}audio{{width:100%;max-width:480px}}.note{{background:#f4f4f4;padding:.5em;border-radius:6px}}</style></head><body>
<h1>Human Review用・正式公開ではありません</h1>
<p class="note">記事: ⑨ AIペットは、たまごっちの次のブームになる？ / <b>Standard</b>・本編パート3の後半(71語)。この1音声だけがユーザー判断待ちです(Standardの他の音声・Advancedは自動検査に合格済み)。</p>
<h2>聴いて判断してほしい点</h2>
<p>赤字の <b style="color:#d00">adult's smartphone</b>(「大人の」スマホ)で、<b>adult の直後に「's(ズ)」が聞こえるか</b>。聞こえれば原文どおり、「adult smartphone」に聞こえて欠落していれば誤りです。それ以外は自動検査で原文どおりと確認できています。</p>
<p>本文(TTSに渡した文。引用符は音声化のため除去済み):<br><code>{text_html}</code></p>
<h2>判断対象の音声(1つ)</h2>
<table><tr><th>音声</th><th>自動検査の事実</th></tr>
<tr><td><audio controls preload="none" src="audio/k2_t1_slowed.mp3"></audio><br>試行1(6%減速後=実際に採用される形)</td>
<td>減速前の音声は自動検査(音声認識)に合格(adult's と認識)。同じ音声を6%減速した後の再検証では、認識結果が「adult smartphone」となり 's の1語だけ不一致(それ以外の全単語は一致)。減速で 's が消えたのか、認識が聞き落としただけなのかは機械では判定できません。</td></tr></table>
<h2>お願い</h2>
<ol><li><b>採用</b>: 's が聞こえる(または聞き流して問題ない)なら、この音声を採用します。</li><li><b>再生成を承認</b>: 's が欠落している/不自然なら再生成を承認してください(Standardのみ)。</li></ol>
<p class="note">補足: 他の2回の試行(試行2・3)は音声自体に 's が無い(認識結果も欠落・Secondary認識も不承認)ためこのページには載せていません(内部記録に保持)。標準retry(2回)+fallback(1回)とLocal Rewrite(候補なし)は発動済みで、自動で救済できる手段は残っていません。</p>
<p><small>自動検査の事実の並記であり、音声の良否の断定ではありません。採用はユーザー判断です。</small></p></body></html>"""
open(OUT + "index.html", "w", encoding="utf-8").write(page)
json.dump({"listed": [t["id"] for t in LISTED], "omitted_from_page": hrl.omitted_internal_record(OMITTED)}, open("docs/research/FAMILY-X-SELECTED-4-ARTICLES-PRODUCTION-01/hr_page_listing_policy_record_04.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok", [t["id"] for t in LISTED])
