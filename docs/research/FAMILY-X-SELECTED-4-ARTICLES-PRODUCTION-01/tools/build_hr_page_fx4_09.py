# -*- coding: utf-8 -*-
"""FAMILY-X-SELECTED-4 委任_09: ⑨Meta Adv(b1b) Vocabulary & Expressions 第3項目「latter」英語音声のHR試聴ページ(API 0)。
掲載=判断対象の最終attempt(attempt4)1本のみ(PM_GOVERNANCE 30-5、er_hr_listing_policy_01経由)。attempt1-3はASR NGで非掲載(内部記録のみ)。
データ元は環境変数FX4_DATA_ROOT(既定=カレント)。"""
import html, json, os, subprocess, sys
sys.path.insert(0, os.getcwd())
import imageio_ffmpeg
import er_hr_listing_policy_01 as hrl
FF = imageio_ffmpeg.get_ffmpeg_exe()
ROOT = os.environ.get("FX4_DATA_ROOT", ".")
A = ROOT + "/er019_output/family_x_audio_production_wiring_01/meta_waddle_world__run_fx4_01/b1b/narration/attempts/"
OUT = "user_test/family_x_meta_waddle_world_hr_02/"
SHA4 = "1c033d171323c97e333e11a3e313552a957da1d9379eb90fb74743a58990e981"
TAKES = [
    {"id": "attempt1_styled", "asr_state": "TRUE_CONTENT_MISMATCH(OpenAI/Azureとも Ladder)"},
    {"id": "attempt2_styled", "asr_state": "TRUE_CONTENT_MISMATCH(OpenAI/Azureとも Ladder)"},
    {"id": "attempt3_english_lock", "asr_state": "TRUE_CONTENT_MISMATCH(OpenAI/Azureとも Ladder)"},
    # 最終attempt: 判断を明示要求(同音語のためASRでは確定不能)
    {"id": "attempt4_english_lock_final", "asr_state": "NG_BOTH(Ladder: 米音flap-tで同音、ASR判別不能)", "user_judgment_requested": True,
     "file": A + "vocab_extra_3_en_attempt4_custom31eb2f72.wav"},
]
LISTED, OMITTED = hrl.select_listing_takes(TAKES)
assert [t["id"] for t in LISTED] == ["attempt4_english_lock_final"]
import hashlib
assert hashlib.sha256(open(LISTED[0]["file"], "rb").read()).hexdigest() == SHA4
os.makedirs(OUT + "audio", exist_ok=True)
subprocess.run([FF, "-y", "-loglevel", "error", "-i", LISTED[0]["file"], "-b:a", "96k", OUT + "audio/vocab_latter_attempt4.mp3"], check=True)
page = """<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>メタ(AIペット)Advanced「latter」英語音声 要判断1音声(Human Review用)</title><style>body{font-family:sans-serif;max-width:900px;margin:1em auto;padding:0 .6em;line-height:1.6}audio{width:100%;max-width:480px}.note{background:#f4f4f4;padding:.5em;border-radius:6px}</style></head><body>
<h1>Human Review用・正式公開ではありません</h1>
<p class="note">記事: ⑨ AIペットは、たまごっちの次のブームになる？ / <b>Advanced</b>・Vocabulary &amp; Expressions 第3項目「latter」の英語音声。この1音声だけがユーザー判断待ちです(他の項目・音声は自動検査に合格済み)。</p>
<h2>聴いて判断してほしい点</h2>
<p><b>「latter」(ラタァ=後者)と聞き取れるか</b>。1単語(約1秒)の音声です。米国発音では latter と ladder がほぼ同じ音(間の t が弾音になる)になるため、自動の音声認識は毎回「Ladder」と書き起こして一致を確定できませんでした。人の耳での確認をお願いします。</p>
<h2>判断対象の音声(1つ)</h2>
<p><audio controls preload="none" src="audio/vocab_latter_attempt4.mp3"></audio><br>最終試行(試行4)の音声</p>
<h3>この項目の表示内容(記事での表示)</h3>
<ul><li>単語: <b>latter</b>(本文中の意味: 後者)</li>
<li>本文の英文: However, the <b>latter</b> is not a rule about who can use the app.</li>
<li>解説: 二つのものを挙げたあとで「後者」を指す語。前者を指す former と対になる。</li></ul>
<h2>お願い</h2>
<ol><li><b>採用</b>: 「latter」と聞こえる(または自然な発音として問題ない)なら、この音声を採用します。</li><li><b>再生成を承認</b>: 「latter」に聞こえない/不自然なら、別の音声の再生成を承認してください(承認があるまで再生成はしません)。</li></ol>
<p class="note">補足: 他の3回の試行(試行1〜3)も同じく「Ladder」と認識され自動検査に通らなかったため、このページには載せていません(内部記録に保持)。標準retry・英語固定指示によるfallbackは発動済みで、自動で救済できる手段は残っていません。</p>
<p><small>自動検査の事実の並記であり、音声の良否の断定ではありません。採用はユーザー判断です。</small></p></body></html>"""
open(OUT + "index.html", "w", encoding="utf-8").write(page)
json.dump({"listed": [t["id"] for t in LISTED], "omitted_from_page": hrl.omitted_internal_record(OMITTED)},
          open("docs/research/FAMILY-X-SELECTED-4-ARTICLES-PRODUCTION-01/hr_page_listing_policy_record_09.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok", [t["id"] for t in LISTED])
