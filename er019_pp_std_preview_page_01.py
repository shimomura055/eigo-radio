# -*- coding: utf-8 -*-
"""FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01 委任_05: Standard試聴ページ(Fallback使用箇所の違和感確認用)。API 0。
er019_pp_std_preview_01.pyが出力したmp3とmanifest(marks)を使うだけ。技術情報(ASR・Gate・Style等)は載せない。"""
import html, json, os
ROOT = os.path.dirname(os.path.abspath(__file__))
esc = html.escape
A2 = os.path.join(ROOT, "er019_output", "family_x_audio_production_wiring_01", "paycheck_personality__run_pp_01", "a2")
MAN = os.path.join(ROOT, "docs", "research", "FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01", "std_preview_manifest_01.json")
OUT = os.path.join(ROOT, "user_test", "paycheck_personality_e2e_01", "std_preview", "index.html")


def rj(p):
    return json.load(open(p, encoding="utf-8"))


man = rj(MAN)
assert man["all_match"]
mk = {m["label"]: m for m in man["marks"]}
parts = rj(os.path.join(A2, "parts.json"))
sup = rj(os.path.join(A2, "a2_support_texts.json"))


def para(t):
    return "".join("<p>%s</p>" % esc(x).replace("\n", "<br>") for x in t.split("\n\n"))


def blk(cls, label, body, jump=None, extra=""):
    j = (" <button class='jump' data-t='%s'>通し音声のここから聴く</button>" % jump) if jump is not None else ""
    return "<div class='blk %s'><div class='lab'>%s%s</div>%s%s</div>" % (cls, label, j, extra, body)


script = ""
script += blk("c", "解説コメント1(日本語)", para(sup["comment_1"]), mk["comment_1"]["start"])
script += blk("p", "第1部 (英語)", para(parts["part1"]), mk["part1"]["start"])
script += blk("c", "解説コメント2(日本語)", para(sup["comment_2"]), mk["comment_2"]["start"])
script += blk("p target", "第2部 (英語) &#9664; ここが確認対象", para(parts["part2"]), mk["part2"]["start"])
script += blk("c", "解説コメント3(日本語)", para(sup["comment_3"]), mk["comment_3"]["start"])
script += blk("p", "第3部 (英語)", para(parts["part3"]), mk["part3"]["start"])
script += blk("c", "解説コメント4(日本語)", para(sup["comment_4"]), mk["comment_4"]["start"])
css = ("<style>body{font-family:sans-serif;max-width:900px;margin:1em auto;padding:0 1em;line-height:1.6}audio{width:100%}"
       ".note{background:#fff8e0;border:1px solid #cb8;padding:10px;margin:1em 0}.ask{background:#eef6ff;border:1px solid #99c;padding:10px;margin:1em 0}"
       ".blk{border:1px solid #ccc;padding:6px 10px;margin:8px 0;border-radius:4px}.blk.c{background:#fafafa;color:#444}.lab{font-weight:bold;font-size:.9em;margin-bottom:4px}"
       ".blk.target{background:#ffe9a8;border:3px solid #e08a00}.blk.target .lab{color:#a05000;font-size:1.05em}button{margin:3px 4px 3px 0;padding:6px 10px;font-size:.95em}"
       "button.jump{font-size:.8em;padding:2px 6px}.sm{font-size:.8em;color:#777;margin-top:2em}.tgtbox{background:#ffe9a8;border:2px solid #e08a00;padding:8px;margin:8px 0}</style>")
js = ("<script>const m=document.getElementById('main');"
      "function go(t){m.currentTime=t;m.play();}"
      "document.querySelectorAll('button.jump').forEach(b=>b.addEventListener('click',()=>go(parseFloat(b.dataset.t))));"
      "document.getElementById('goP2').addEventListener('click',()=>go(%s));"
      "document.getElementById('goP1').addEventListener('click',()=>go(%s));"
      "document.getElementById('goP3').addEventListener('click',()=>go(%s));</script>"
      % (mk["part2"]["start"] - 3, mk["part1"]["start"] - 3, mk["part3"]["start"] - 3))
dur = man["preview_duration_s"]
pg = ("<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'><title>Standard 試聴確認(収入と性格)</title><meta name='viewport' content='width=device-width, initial-scale=1'>" + css + "</head><body>"
      "<h1>Standard音声の試聴確認「収入と性格」</h1>"
      "<div class='note'><b>正式採用前の確認用プレビューです(Production完成版ではありません)。</b></div>"
      "<div class='ask'><b>確認してほしいこと</b><br>Full Story第2部のみ、通常と異なる音声生成Styleを使用しています。全体を聴いて、第1部・第3部と比べて声の調子・話し方に違和感がないか確認してください。"
      "<br><br><b>確認のポイント</b>: 第1部→第2部→第3部と聴いたとき、声の調子・話す速さ・落ち着きが揃って聞こえるか。</div>"
      "<h2>1. Standard全体を通して聴く(約%d分%02d秒)</h2>" % (dur // 60, dur % 60)
      + "<audio id='main' controls preload='metadata' src='audio/%s'></audio>" % os.path.basename(man["preview_mp3"])
      + "<p>通し音声の途中へ移動: <button id='goP1'>第1部の少し前から</button><button id='goP2'>第2部の少し前から(確認対象)</button><button id='goP3'>第3部の少し前から</button></p>"
      "<h2>2. 部分ごとに聴き比べる</h2>"
      "<div class='tgtbox'><b>第2部(確認対象)だけ再生</b><br><audio id='p2' controls preload='none' src='audio/part2_only.mp3'></audio></div>"
      "<p><b>比較用: 第1部だけ</b><br><audio id='p1' controls preload='none' src='audio/part1_only.mp3'></audio></p>"
      "<p><b>比較用: 第3部だけ</b><br><audio id='p3' controls preload='none' src='audio/part3_only.mp3'></audio></p>"
      "<h2>3. 台本(第2部の段落が確認対象)</h2>" + script
      + "<p class='sm'>技術詳細(監査用): <a href='../hr_full_story_part2/index.html'>詳細ページ</a></p>" + js + "</body></html>")
assert "file:///" not in pg and "C:\\" not in pg and "C:/" not in pg
open(OUT, "w", encoding="utf-8").write(pg)
print("ok", len(pg))
