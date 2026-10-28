# -*- coding: utf-8 -*-
"""FX-MOON-SHRINKING-RESELECT-REMAKE-01 委任_03: 月Std日本語題の試聴・ASR照合ページ(Human Review用、API 0・費用0円)。
今回run(reselect_01)3 attempt + run_ms_03(ユーザー試聴で『どれも問題ありません』)3 attemptを、原稿・各ASR転写・現行判定と並べる。音声の正否は人間が判定する(AIは断定しない)。
出力: user_test/fx_moon_title_asr_listen_01/{index.html, audio/*.mp3}。使い方: .venv/Scripts/python.exe docs/research/FX-MOON-SHRINKING-RESELECT-REMAKE-01/build_title_listen_page_01.py"""
import html, json, os, subprocess, sys
ROOT = os.getcwd()
import imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
esc = html.escape
CANON = "月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密"
W = "user_test/fx_moon_title_asr_listen_01"; os.makedirs(W + "/audio", exist_ok=True)
RUNS = [("今回 reselect_01(2026-10-28)", "reselect_01", "er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01/a2/narration/attempts/", "docs/research/FX-MOON-SHRINKING-RESELECT-REMAKE-01/ja_title_local_whisper_reselect_01.json"),
        ("過去 run_ms_03(2026-10-25。ユーザーは3本とも『問題ありません』と判断、attempt2を個別承認)", "ms_03", "er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_ms_03/a2/narration/attempts/", "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/whisper_local_3wav_01.json")]
FILES = ["japanese_title_attempt1_customb8f0ff16", "japanese_title_attempt2_customb8f0ff16", "japanese_title_attempt3_minimalfallback"]
body = []
for label, tag, d, wj in RUNS:
    wh = json.load(open(wj, encoding="utf-8"))
    body.append(f"<h3>{esc(label)}</h3><div class='tbl'><table><tr><th>attempt</th><th>再生</th><th>OpenAI(Primary)</th><th>Azure(Secondary)</th><th>Whisper small / medium(参考・ローカル)</th><th>本番判定(記録)</th></tr>")
    for i, f in enumerate(FILES, 1):
        a = json.load(open(d + f + ".json", encoding="utf-8")); sc = a.get("scg_info") or {}
        mp3 = f"audio/{tag}_attempt{i}.mp3"
        subprocess.run([FF, "-y", "-loglevel", "error", "-i", d + f + ".wav", "-codec:a", "libmp3lame", "-qscale:a", "4", W + "/" + mp3], check=True)
        ws = wh.get(f"small:{f}.wav", ""); wm = wh.get(f"medium:{f}.wav", "")
        az = sc.get("secondary_transcript") or "(未実行: Primaryの数値が原稿と食い違いP1で打切り=Azure不呼出)"
        body.append(f"<tr><td>#{i}{' (fallback)' if i == 3 else ''}</td><td><audio controls preload='none' src='{mp3}'></audio></td><td><code>{esc(a['asr_text'])}</code></td><td><code>{esc(az)}</code></td><td><code>{esc(ws)}</code><br><code>{esc(wm)}</code></td><td>{esc(str(sc.get('unified_judge_state')))} / {esc(str(sc.get('unified_reason_code')))}</td></tr>")
    body.append("</table></div>")
re = json.load(open("docs/research/FX-MOON-SHRINKING-RESELECT-REMAKE-01/ja_title_reasr_01.out.json", encoding="utf-8"))
body.append("<h3>参考: 今回3音声をOpenAIで4回ずつ再転写した結果(同じ音声でも毎回違う書き方になります)</h3><div class='tbl'><table><tr><th>今回attempt</th><th>OpenAI再転写 x4</th><th>Azure再転写</th></tr>")
for i, r in enumerate(re, 1):
    body.append("<tr><td>#%d</td><td>%s</td><td><code>%s</code></td></tr>" % (i, "<br>".join("<code>%s</code>" % esc(o["text"]) for o in r["openai"]), esc(r["azure"]["text"])))
body.append("</table></div>")
html_s = f"""<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>月Standard日本語題 試聴・ASR照合</title><style>body{{font-family:sans-serif;max-width:1100px;margin:1em auto;padding:0 .6em}}
table{{border-collapse:collapse;width:100%;font-size:.88em}}td,th{{border:1px solid #bbb;padding:5px;vertical-align:top}}th{{background:#eee}}audio{{width:220px;max-width:100%}}.tbl{{overflow-x:auto}}.note{{background:#f4f4f4;padding:.5em;border-radius:6px;font-size:.9em}}</style></head><body>
<h2>月Standard日本語題: 6音声の試聴とASR転写の照合(運営者向け)</h2>
<p>原稿: <code>{esc(CANON)}</code></p>
<p class="note">読み上げの正しい形は「つきのしわ、はっせんきゅうひゃっぽん ちょう！そのおくに ひそむ いわのうわぎの ひみつ」です(「しわ」=皺。助詞の「は」ではなく名詞の「わ」で終わる)。ASRは音が同じでも文字を選ぶため、「月の詩は」「月の死は」「月の氏は」「月野氏は」のように書くことがあります(OpenAI・Azure・ローカルWhisper全てで観測)。<b>ASRの転写は事実の並記であり、発音の正否の断定ではありません。実際に聴いて判断してください。</b>
Whisper(参考)は本番判定では使っておらず、保存wavをローカル(faster-whisper small/medium、費用0)で再転写した参考値です。</p>
<p class="note"><b>聴いてほしい点(1つ)</b>: 各音声の冒頭「月のしわ」の部分が、「つきの・しわ」と自然に聞こえるか(「つきの・し・は」や別の語に聞こえないか)。特に今回#3(fallback)は、OpenAIが「スギノ市は」、Azureが「Sukino氏は」と書いており、冒頭「月の」が別の音に聞こえる可能性があります。</p>
{''.join(body)}
</body></html>"""
open(W + "/index.html", "w", encoding="utf-8").write(html_s)
print("OK", W + "/index.html")
