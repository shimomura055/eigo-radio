# -*- coding: utf-8 -*-
"""FAMILY-Z-IN-A-GROVE-PRODUCTION-01 委任_10: Standard HR Lock 2 clip(comment_3 / full_story_part1_c3)の試聴ページ(Human Review用、API 0・費用0)。
Lock/承認操作は一切しない(判断材料の表示のみ)。出力: user_test/family_z_in_a_grove_hr_01/{index.html, audio/*.mp3}。mp3化は音声内容を変えない形式変換のみ。"""
import html, json, os, subprocess, wave
import imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe(); esc = html.escape
RUN = "er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01/a2"
AT = RUN + "/narration/attempts/"
W = "user_test/family_z_in_a_grove_hr_01"; os.makedirs(W + "/audio", exist_ok=True)
res = json.load(open(RUN + "/audit/tts_generation_results.json", encoding="utf-8"))["segments"]
CLIPS = [
 ("comment_3", "コメント3(日本語ナレーション・Aoede)", ["comment_3_attempt1_custom06ec49ff", "comment_3_attempt2_custom06ec49ff", "comment_3_attempt3_minimalfallback"],
  "聴いてほしい点: 人名が「タジョマル」「マサゴ」と聞こえるか(文字起こしAIは別の人名に書き起こしましたが、これは音声の誤りとは限りません)。"),
 ("full_story_part1_c3", "本編パート1・3番目(英語・きこりAlgieba)", ["full_story_part1_c3_attempt1_englishstyleprefixwidemargin", "full_story_part1_c3_attempt2_englishstyleprefixwidemargin", "full_story_part1_c3_attempt3_englishstyleprefixwidemargin"],
  "聴いてほしい点: 文頭付近(0〜2秒)で同じ音・語が繰り返されたり、つかえたりして聞こえないか(自動検査は短い自己類似を検出しましたが、文字起こしは原文と完全一致でした)。"),
]
body = []
for cid, title, files, hint in CLIPS:
    canon = res[cid]["canonical_text"]
    body.append(f"<h2>{esc(title)}</h2><p>原文:<br><code>{esc(canon)}</code></p><p class='note'>{esc(hint)}</p><div class='tbl'><table><tr><th>試行</th><th>再生</th><th>長さ</th><th>文字起こし(ASR)</th><th>自動検査の結果</th></tr>")
    for i, f in enumerate(files, 1):
        a = json.load(open(AT + f + ".json", encoding="utf-8")); wp = AT + f + ".wav"
        with wave.open(wp) as x: dur = x.getnframes() / x.getframerate()
        mp3 = f"audio/{cid}_try{i}.mp3"
        subprocess.run([FF, "-y", "-loglevel", "error", "-i", wp, "-codec:a", "libmp3lame", "-qscale:a", "2", W + "/" + mp3], check=True)
        kind = "従来方式(最終)" if "minimalfallback" in f or a.get("tts_mode") == "legacy_fallback" else "通常"
        if cid == "comment_3":
            sc = a.get("scg_info") or {}
            asr = f"1次: {a['asr_text']}<br>2次(Azure): {sc.get('secondary_transcript')}"
            res_t = f"不一致(人名の聞き取り違い): {esc(a['audio_classification'])}"
            asr = esc(a['asr_text']) + "<br><small>2次(Azure): " + esc(str(sc.get('secondary_transcript'))) + "</small>"
        else:
            dp = a["repetition_qa_evidence"]["method_d_prime_spectral_short_lag"]
            asr = esc(a["asr_text"]) + "<br><small>(原文と完全一致)</small>"
            res_t = f"繰り返し検査: 要確認(連続{dp['run_length_seconds']}秒・間隔{dp['lag']}秒・開始{dp['time_a']}秒付近。基準=0.6秒超)"
        body.append(f"<tr><td>#{i}<br><small>{kind}</small></td><td><audio controls preload='none' src='{mp3}'></audio></td><td>{dur:.1f}秒</td><td>{asr}</td><td>{res_t}</td></tr>")
    body.append("</table></div>")
page = f"""<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>藪の中 Standard 要試聴2音声(Human Review用)</title><style>body{{font-family:sans-serif;max-width:1100px;margin:1em auto;padding:0 .6em}}
table{{border-collapse:collapse;width:100%;font-size:.9em}}td,th{{border:1px solid #bbb;padding:5px;vertical-align:top}}th{{background:#eee}}audio{{width:220px;max-width:100%}}.tbl{{overflow-x:auto}}.note{{background:#f4f4f4;padding:.5em;border-radius:6px}}</style></head><body>
<h1>Human Review用・正式公開ではありません</h1>
<p>『藪の中』Standardの27音声のうち25は自動検査に合格し、次の2音声だけが「人が聴いて判断」に回っています。各音声の3回分の試行を並べました。<b>各試行について、問題ない(採用できる)か、問題あり(NG)かをお聞かせください。</b>自動検査の結果は事実の並記であり、音声の良否の断定ではありません。</p>
{''.join(body)}
</body></html>"""
open(W + "/index.html", "w", encoding="utf-8").write(page); print("OK", W + "/index.html")
