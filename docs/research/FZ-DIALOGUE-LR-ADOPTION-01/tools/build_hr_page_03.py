# -*- coding: utf-8 -*-
"""FZ-DIALOGUE-LR-ADOPTION-01 委任_04: c6 HR試聴ページ(API 0)。"""
import html, subprocess, os, imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
RUN = "er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01/b1b/narration/attempts/"
OUT = "user_test/family_z_in_a_grove_hr_03/"
import json, sys
sys.path.insert(0, os.getcwd())
import er_hr_listing_policy_01 as hrl          # 委任_05: 掲載対象=判断対象音声のみ(ユーザー決定USER_02 §2、PM_GOVERNANCE 30-5)
TAKES = [{"id": "try1", "label": "①", "asr_state": "NG_BOTH"}, {"id": "try2", "label": "②", "asr_state": "NG_BOTH"},
         {"id": "try3", "label": "③", "asr_state": "PASS", "attempt_file": 4}, {"id": "try4", "label": "④", "asr_state": "PASS_WITH_WARNING", "attempt_file": 5},
         {"id": "try5", "label": "⑤", "asr_state": "NG_BOTH", "attempt_file": 6}, {"id": "try6", "label": "⑥", "asr_state": "NG_BOTH", "attempt_file": 7}]
LISTED, OMITTED = hrl.select_listing_takes(TAKES)
ATT = {t["id"]: t["attempt_file"] for t in LISTED}
for k, n in ATT.items():
    src = f"{RUN}full_story_part3_c6_attempt{n}_englishstyleprefixwidemargin.wav"
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", src, "-b:a", "96k", f"{OUT}audio/c6_{k}.mp3"], check=True)
BEFORE = ("My wife said, 'Take me anywhere.' Then she pointed at me. 'Kill that man.' He pushed her away and asked me whether she should live or die. For that, I almost forgave him. But she fled. He cut one rope and left. I rose from the cedar and picked up the small dagger she had dropped. I stabbed myself in the chest. The thicket fell silent. Then someone crept towards me on soft feet. ")
TAIL = " unseen hand quietly drew the dagger from my chest. I sank for ever into the darkness."
e = html.escape
before = e(BEFORE) + "<b>An</b>" + e(TAIL)
after = e(BEFORE) + '<b style="color:#d00">Some</b>' + e(TAIL)
def aud(k): return f"<audio controls preload='none' src='audio/c6_{k}.mp3'></audio>"
rows = [
 ("③", "従来Dialogue(Fallback)", "<b>LR前</b>", "ASR合格(NORMALIZED_MATCH)・繰り返し検査のみflag", "ASR合格", "d' 0.73秒 > 閾値0.6秒", aud("try3")),
 ("④", "ctx(LR後 1回目)", '<b style="color:#d00">LR後</b>(An→Some)', "PASS_WITH_WARNING・繰り返し検査のみflag", "ASR合格(NORMALIZED_MATCH)", "d' 0.68秒 > 閾値0.6秒", aud("try4")),
]
tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
page = f"""<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>藪の中 Advanced 要判断1音声 LR後(Human Review用)</title><style>body{{font-family:sans-serif;max-width:1100px;margin:1em auto;padding:0 .6em}}table{{border-collapse:collapse;width:100%;font-size:.9em}}td,th{{border:1px solid #bbb;padding:5px;vertical-align:top}}th{{background:#eee}}audio{{width:240px;max-width:100%}}.tbl{{overflow-x:auto}}.note{{background:#f4f4f4;padding:.5em;border-radius:6px}}</style></head><body>
<h1>Human Review用・正式公開ではありません</h1>
<p class="note"><b>ユーザー決定(2026-10-29): ③(LR前本文・従来Dialogue)を採用済み</b>。④(LR後)は不採用。本ページは判断対象だった2音声のみ掲載しています。</p>
<p>『藪の中』Advancedの32音声のうち31は合格し、<b>本編パート3・6番目(武弘=Takehiro・Voice: Puck、91語)</b>だけが、新方式(Local Rewrite=LR を含む最大TTS6回)の全試行を使い切って止まっています。</p>
<h2>本文(LR前 / LR後)</h2>
<p><b>LR前</b>(①〜③):<br><code>{before}</code></p>
<p><b>LR後</b>(④。変更は1語のみ、赤字):<br><code>{after}</code></p>
<p class="note">変更理由: ①で「An unseen」が「and unseen」と聞こえた(認識誤り)ため、文意を変えずに1語だけ「An→Some」へ書き換え。意味・事実・確定済みの表現(sank for ever、on soft feet)は変更なし。</p>
<h2>試行一覧(判断対象の2音声。LR後本文は④)</h2>
<div class="tbl"><table><tr><th>試行</th><th>方式</th><th>本文</th><th>Gate結果</th><th>ASR判定</th><th>繰り返し検査 d'(短間隔)</th><th>再生</th></tr>{tr}</table></div>
<p class="note">聴いてほしい点: 全体が武弘の声(Puck)で自然か、つかえ・読みの崩れ・繰り返しがないか。③と④は自動検査で「ASR合格、繰り返し検査(d')のみ閾値超過」の同型です。①②⑤⑥はASR NGで比較判断が不要なため掲載していません(試行記録は内部に保持)。</p>
<h2>お願い</h2>
<ol><li><b>採用</b>: ③(LR前本文)または④(LR後本文)のうち、聴いて問題なければ採用できます。</li><li><b>再生成を承認</b>: どちらも採用できない場合、次の新しい最大6回サイクルを1回承認(概算¥15〜19)。成功の保証はありません。</li><li>d'閾値(0.6秒)そのものの見直しはユーザー判断事項です(OPEN-594)。</li></ol>
<p class="note">採用はユーザー判断です。採用時は候補ページにLR Before/After(赤字)とFallback(濃い青)の表示が付きます(④採用ならLR後本文が表示本文になります)。</p>
<p class="note">参考: OPEN-594(d'手法の偽陽性疑い。きこり/Algieba)、Standard part1_c3(3試行とも自動検査は要確認だったが、試聴で問題なしと判断)と同型の可能性があります。耳で聴いて問題なければ採用でき、それが最も早く低コストです。</p>
<p><small>自動検査の事実の並記であり、音声の良否の断定ではありません。</small></p></body></html>"""
open(OUT + "index.html", "w", encoding="utf-8").write(page)
json.dump({"omitted_from_page": hrl.omitted_internal_record(OMITTED), "listed": [t["id"] for t in LISTED]}, open("docs/research/FZ-DIALOGUE-LR-ADOPTION-01/hr_03_listing_policy_record_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok", [t["id"] for t in LISTED])
