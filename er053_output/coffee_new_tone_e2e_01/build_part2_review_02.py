# -*- coding: utf-8 -*-
"""FAMILY-X-COFFEE-NEW-TONE-PRODUCTION-E2E-01 delegation 08: part2 Human Review page build.
No API calls. Local wav->mp3 conversion + static html only. Run from worktree root with main-tree .venv python (PYTHONUTF8=1)."""
import html, json, os, re, difflib, soundfile as sf

E = html.escape
R = "er019_output/family_x_audio_production_wiring_01/coffee_prices__run_e_tone_01/a2"
OUT = "user_test/coffee_new_tone_01/part2_review"
A = R + "/narration/attempts/full_story_part2_"
parts = json.load(open(R + "/parts.json", encoding="utf-8"))
SCRIPT = parts["part2"]
q = [json.loads(l) for l in open("er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl", encoding="utf-8")]
lr_q = q[-1]
assert lr_q["timestamp"].startswith("2026-10-11T15:35")
LR_SCRIPT = lr_q["canonical_text"]


def aj(n):
    return json.load(open(A + n + ".json", encoding="utf-8"))


def wav2mp3(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    d, sr = sf.read(src)
    sf.write(dst, d, sr, format="MP3")
    return round(len(d) / sr, 2)


NUM = {"2": "two", "9": "nine"}


def norm_tokens(t):
    t = t.replace("’", "'").replace("“", '"').replace("”", '"').replace("raw-bean", "raw bean")
    out = []
    for m in re.finditer(r"U\.S\.|[A-Za-z]+(?:'[a-z]+)?|\d+(?:\.\d+)?%?", t):
        w = "us" if m.group(0) == "U.S." else m.group(0).lower()
        out.append((NUM.get(w, w), m.start(), m.end()))
    return out


def diff(script, asr):
    s, a = norm_tokens(script), norm_tokens(asr)
    sm = difflib.SequenceMatcher(None, [x[0] for x in s], [x[0] for x in a], autojunk=False)
    marks, items = [], []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            continue
        marks += [(a[j][1], a[j][2]) for j in range(j1, j2)]
        sw = " ".join(script[s[i][1]:s[i][2]] for i in range(i1, i2)) or "(なし)"
        aw = " ".join(asr[a[j][1]:a[j][2]] for j in range(j1, j2)) or "(なし)"
        ctx = " ".join(script[s[k][1]:s[k][2]] for k in range(max(0, i1 - 3), i1))
        items.append((ctx, sw, aw))
    return marks, items


def hl_asr(asr, marks):
    res, pos = [], 0
    for st, en in sorted(marks):
        res.append(E(asr[pos:st]))
        res.append('<mark class="d">' + E(asr[st:en]) + "</mark>")
        pos = en
    res.append(E(asr[pos:]))
    return "".join(res).replace("\n", "<br>")


def hl_script(t):
    h = E(t)
    for pat in (r"6\.1%", r"nine months", r"9 months", r"two numbers", r"2 numbers", r"coffee cost"):
        h = re.sub("(" + pat + ")", r'<b class="num">\1</b>', h)
    return h.replace("\n", "<br>")


def steps_html(steps):
    out = []
    for s in steps:
        cls = s.get("classification", "")
        out.append('<li><code>%s</code> (%s): <span class="%s">%s</span><details><summary>転写全文</summary><div class="asr">%s</div></details></li>'
                   % (E(s["step"]), E(s["provider"]), "ok" if cls == "NORMALIZED_MATCH" else "ng", E(cls), E(s["text"]).replace("\n", "<br>")))
    return "<ul>" + "".join(out) + "</ul>"


a1, a2, a3, a4 = aj("attempt1_customf1837a73"), aj("attempt2_customf1837a73"), aj("attempt3_customf1837a73"), aj("attempt4_minimalfallback")
specs = [
    dict(n="ref", title="参考: 減速前の初回TTS(attempts/…attempt1、15:13)", kind="初回TTS(減速前の原音声)", wav=A + "attempt1_customf1837a73.wav", mp3="ref_attempt1_original.mp3",
         style_source="approved_role_style:EN_FULLSTORY_F1_5(標準経路)", style=a1["instruction_text"], script=SCRIPT, asr=a1["asr_text"], cls=a1["audio_classification"],
         steps=a1["cascade_steps"], reason="Primary ASRは NORMALIZED_MATCH(合格)。ただし最終の自動フローはこの音声を採用せず再試行に進んだ(下記attempt 1以降)。聴き比べの基準として掲載。"),
    dict(n="1", title="attempt 1(標準・1回目、attempts/…attempt2、15:16)", kind="標準", wav=A + "attempt2_customf1837a73.wav", mp3="attempt1_standard.mp3",
         style_source="approved_role_style:EN_FULLSTORY_F1_5(標準経路)", style=a2["instruction_text"], script=SCRIPT, asr=a2["asr_text"], cls=a2["audio_classification"], steps=a2["cascade_steps"],
         reason="Primary ASRが TRUE_CONTENT_MISMATCH。原稿の過去形 showed が show(現在形)に、coffee cost が coffee costs に聞こえた。"),
    dict(n="2", title="attempt 2(標準・2回目、attempts/…attempt3、15:19)", kind="標準", wav=A + "attempt3_customf1837a73.wav", mp3="attempt2_standard.mp3",
         style_source="approved_role_style:EN_FULLSTORY_F1_5(標準経路)", style=a3["instruction_text"], script=SCRIPT, asr=a3["asr_text"], cls=a3["audio_classification"], steps=a3["cascade_steps"],
         reason="Primary ASR x2は ASR_VALIDATION_UNCERTAIN。Azure Secondary x2は TRUE_CONTENT_MISMATCH。coffee cost が coffee costs に聞こえた(showedは一致)。この後10分cool-down。"),
    dict(n="3", title="attempt 3(fallback、attempts/…attempt4_minimalfallback、15:32)", kind="fallback(承認Style維持)", wav=A + "attempt4_minimalfallback.wav", mp3="attempt3_fallback.mp3",
         style_source=a4["style_source"], style=a4["style_prefix"], script=SCRIPT, asr=a4["asr_text"], cls=a4["audio_classification"], steps=None,
         reason="TRUE_CONTENT_MISMATCH。ASR転写は(数詞・時制を含め)原稿と語句単位で一致して見えるのに不合格判定(ASR転写中に段落区切りの改行が入っている点が他と異なる)。判定の内部根拠は記録なし(scg_info=null)。したがって実際に読み違えているのかは人間の耳で要確認。"),
    dict(n="4", title="attempt 4(Local Rewrite後の再TTS、最終 narration/full_story_part2.wav、15:35)", kind="Local Rewrite", wav=R + "/narration/full_story_part2.wav", mp3="attempt4_local_rewrite.mp3",
         style_source="approved_role_style:EN_FULLSTORY_F1_5(標準経路+減速。この最終wavのstyle_sourceは個別json未保存、runの設定値)", style=a2["instruction_text"], script=LR_SCRIPT, asr=lr_q["steps"][0]["text"], cls="TRUE_CONTENT_MISMATCH(最終判定)",
         steps=lr_q["steps"], reason="書き換え文面(data from the United States / 2 numbers / 9 months)。Primary ASRは NORMALIZED_MATCH(合格)だが、Azure Secondary(強制実行)が 'raw bean' を 'Robbing/Robbins' と転写し TRUE_CONTENT_MISMATCH。Azure側の転写誤りの可能性があり、人間の耳で確認が必要。"),
]

cards = []
for sp in specs:
    dur = wav2mp3(sp["wav"], "%s/%s" % (OUT, sp["mp3"]))
    marks, items = diff(sp["script"], sp["asr"])
    diff_li = "".join('<li>…%s <b>[原稿: %s]</b> → <mark class="d">[ASR: %s]</mark></li>' % (E(c), E(s), E(a)) for c, s, a in items) or "<li>語句差分なし(正規化後)</li>"
    for st in (sp["steps"] or []):
        if st["provider"] == "azure" and st["step"] in ("secondary_forced", "secondary_1"):
            _, it2 = diff(sp["script"], st["text"])
            diff_li += "<li><b>Azure Secondary(%s)の差分</b>: " % E(st["step"]) + " / ".join("%s [原稿: %s] → [Azure: %s]" % (E(c), E(s), E(a)) for c, s, a in it2) + "</li>"
    steps = steps_html(sp["steps"]) if sp["steps"] else "<p>(個別attemptのcascade記録なし。attempts/…json の asr_text と audio_classification のみ)</p>"
    cards.append("""<section class="card" id="a%(n)s">
<h2>%(title)s</h2>
<audio controls preload="none" src="%(mp3)s"></audio>
<table class="meta"><tr><th>種別</th><td>%(kind)s</td><th>音声長</th><td>%(dur)s秒</td></tr>
<tr><th>style_source</th><td colspan="3"><code>%(ss)s</code></td></tr>
<tr><th>style_prefix</th><td colspan="3">%(style)s</td></tr>
<tr><th>voice / backend</th><td colspan="3">Aoede / speech_metadata_flash_lite(gemini-3.8-flash-lite-tts、BATCH)</td></tr>
<tr><th>ASR判定</th><td colspan="3" class="ng"><b>%(cls)s</b></td></tr>
<tr><th>判定理由</th><td colspan="3">%(reason)s</td></tr></table>
<h3>ASR転写(差分を黄色でハイライト)</h3>
<div class="asr">%(asr)s</div>
<h3>原稿との語句差分(数詞・大小文字・句読点は正規化後に比較)</h3>
<ul>%(diff)s</ul>
<details><summary>ASR cascade各step(Primary / Azure Secondary)</summary>%(steps)s</details>
<div class="check"><b>ユーザー判断欄(表示のみ・入力は保存されません)</b><br>
&#9744; 原稿どおりに読めている &nbsp; &#9744; 一部読み違い(箇所: ______) &nbsp; &#9744; 数値「6.1%%」「nine months」は正しい &nbsp; &#9744; 時制(showed / cost)の違いは気にならない &nbsp; &#9744; Production採用可</div>
</section>""" % dict(n=sp["n"], title=E(sp["title"]), mp3=sp["mp3"], kind=E(sp["kind"]), dur=dur, ss=E(sp["style_source"]),
                       style=E(sp["style"]).replace("\n", "<br>"), cls=E(sp["cls"]), reason=E(sp["reason"]),
                       asr=hl_asr(sp["asr"], marks), diff=diff_li, steps=steps))

page = """<!DOCTYPE html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Coffee Prices Standard full_story_part2 Human Review(試聴用)</title>
<style>
body{font-family:"Meiryo","Hiragino Kaku Gothic ProN",sans-serif;max-width:1000px;margin:1.5em auto;padding:0 1em;line-height:1.6;color:#111}
h1{font-size:1.4em} h2{border-bottom:2px solid #333;padding-bottom:4px;margin-top:2em;font-size:1.15em} h3{font-size:1em;margin:1em 0 .3em;border-left:5px solid #888;padding-left:8px}
audio{width:100%%;min-width:360px;height:36px;display:block;margin:8px 0}
table.meta{border-collapse:collapse;width:100%%;font-size:.88em} table.meta th,table.meta td{border:1px solid #bbb;padding:5px 7px;text-align:left;vertical-align:top} table.meta th{background:#f0f0f0;white-space:nowrap}
.asr{background:#f7f7f7;border:1px solid #ddd;padding:8px 10px;font-size:.92em} mark.d{background:#ffe066;padding:0 2px} .ng{color:#b00} .ok{color:#070} b.num{background:#d8ecff}
.note{background:#fffbe6;border:1px solid #e0d080;padding:10px 14px;font-size:.92em;margin:14px 0} .check{background:#eef7ee;border:1px solid #9c9;padding:8px 12px;margin-top:10px;font-size:.92em}
.script{background:#fff;border:1px solid #999;padding:10px 14px} .card{margin-bottom:2.5em} details{margin:6px 0}
</style></head><body>
<h1>Coffee Prices(新tone) Standard <code>full_story_part2</code> Human Review(試聴用)</h1>
<div class="note"><b>管理ID: FAMILY-X-COFFEE-NEW-TONE-PRODUCTION-E2E-01(委任_08)</b>。Standardの<code>full_story_part2</code>は標準2回+fallback1回(承認Style維持)+Local Rewrite再TTSのすべてでASR不合格となり、Human Review待ちです。
<b>聞いてほしい点</b>: (1)「原稿どおりに読めているか」(特に数値 6.1%% / nine months、時制 showed と cost)、(2)各attemptの読み方(tone・テンポ)の違い。
ASR不合格が「TTSの実際の読み違い」か「ASRの転写誤り」かは<b>未確定(ユーザー試聴待ち)</b>です。承認(REGENERATE_APPROVED等)は人間ユーザーのみが行い、本ページはevidence配布のみです。
<br><a href="../index.html">&larr; 通しページ(Advanced完成episode / Standard合格segment)へ戻る</a></div>
<h2>原稿(part2 canonical全文。数値・時制の注目箇所を青で強調)</h2>
<div class="script">%(script)s</div>
<p style="font-size:.85em">※attempt 4(Local Rewrite)のみ、次の書き換え文面で再TTSされています(差分: 「US data」→「data from the United States」、「the two numbers」→「the 2 numbers」、「nine months」→「9 months」、引用符除去):<br><span class="script" style="display:block;margin-top:4px">%(lr)s</span></p>
%(cards)s
<p style="font-size:.85em;color:#444">出典: %(R)s(attempts/*.wav|json, audit/review_lock_state.json)、er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl。保存済み音声をmp3化しただけで新規生成・API呼出なし。attempt番号は本ページ上の通し番号で、ファイル名のattemptN表記(attempt2〜4)とは異なります(各見出しに実ファイル名を併記)。</p>
</body></html>
""" % dict(script=hl_script(SCRIPT), lr=hl_script(LR_SCRIPT), cards="".join(cards), R=E(R))
page = page.replace("%%", "%")
open("%s/index.html" % OUT, "w", encoding="utf-8", newline="\n").write(page)

ip = "user_test/coffee_new_tone_01/index.html"
t = open(ip, encoding="utf-8").read()
LINK = '<div class="note"><b>Standard full_story_part2 のHuman Review用ページ</b>: <a href="part2_review/index.html">part2_review/index.html</a>(4 attemptの音声・ASR転写・差分・判定理由を並べて試聴できます。承認は人間ユーザーのみ)</div>\n'
if "part2_review/index.html" not in t:
    marker = '<p class="meta">segment数: 11'
    assert marker in t
    t = t.replace(marker, LINK + marker, 1)
    t = t.replace("<td>未取得(Human Review待ち)</td>", '<td>未取得(通し)。<a href="part2_review/index.html">4 attempt試聴ページ</a></td>')
    open(ip, "w", encoding="utf-8", newline="\n").write(t)
print("built", [s["mp3"] for s in specs])
