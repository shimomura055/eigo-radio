# -*- coding: utf-8 -*-
"""blind_page_01.py  Blind比較ページ生成(無課金)。対応表はBLIND_MAP_01.json(trial dir)に別保存。ページにはモデル名・案名・文字数等を出さない。
使い方: python blind_page_01.py A C D E   (R2を持つ案のみ。B案は再生成STOPのため現時点では含まれない)"""
import hashlib, html, json, os, random, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SEED = 20261011
CIRC = "①②③④⑤"
arms = sys.argv[1:] or ["A", "C", "D", "E"]
order = list(arms)
random.Random(SEED).shuffle(order)
texts = {a: open(os.path.join(HERE, "runs", a, "export", "r2.md"), encoding="utf-8").read().strip() for a in arms}
mapping = {CIRC[i]: a for i, a in enumerate(order)}
def render(a):
    lines = texts[a].split("\n")
    title = html.escape(lines[0].strip())
    paras = [p.strip() for p in "\n".join(lines[1:]).split("\n\n") if p.strip()]
    return f'<h2>{title}</h2>\n' + "\n".join(f"<p>{html.escape(p).replace(chr(10), '<br>')}</p>" for p in paras)
tabs = "".join(f'<button type="button" class="tab" role="tab" data-i="{i}" aria-selected="{"true" if i == 0 else "false"}">記事{CIRC[i]}</button>' for i in range(len(order)))
arts = "".join(f'<article class="art" data-i="{i}"{"" if i == 0 else " hidden"}>\n{render(a)}\n</article>\n' for i, a in enumerate(order))
page = f"""<!DOCTYPE html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>記事比較(ユーザー評価用)</title>
<style>body{{font-family:sans-serif;max-width:760px;margin:1em auto;padding:0 1em;line-height:1.8}}.tab{{font-size:1em;padding:.5em 1em;margin:0 .3em .5em 0;border:1px solid #888;background:#f4f4f4;cursor:pointer}}.tab[aria-selected=true]{{background:#333;color:#fff}}h2{{font-size:1.25em}}.note{{color:#555;font-size:.9em}}</style></head>
<body>
<h1>記事比較</h1>
<p class="note">{len(order)}本の日本語記事です(音声なし)。記事{CIRC[0]}〜{CIRC[len(order)-1]}は順不同で、順番に優劣の意味はありません。タブで切り替えて全文を読み比べてください。</p>
<div role="tablist">{tabs}</div>
{arts}
<script>
var tabs=document.querySelectorAll('.tab'),arts=document.querySelectorAll('.art');
tabs.forEach(function(t){{t.addEventListener('click',function(){{var i=t.getAttribute('data-i');
tabs.forEach(function(x){{x.setAttribute('aria-selected',x.getAttribute('data-i')===i?'true':'false')}});
arts.forEach(function(a){{a.hidden=(a.getAttribute('data-i')!==i)}});}});}});
</script>
</body></html>
"""
outdir = os.path.join(ROOT, "user_test", "ja_quality_model_allocation_01")
os.makedirs(outdir, exist_ok=True)
open(os.path.join(outdir, "index.html"), "w", encoding="utf-8", newline="\n").write(page)
# 漏洩検査: 骨格(記事本文を除く)に手掛かり語なし / 記事本文にモデル名なし
skeleton = re.sub(r"<article.*?</article>", "", page, flags=re.S)
bad_skel = re.findall(r"gpt|luna|astra|sol\b|案|model|モデル|文字|字数", skeleton, flags=re.I)
bad_body = re.findall(r"gpt|luna|astra|\bsol\b", arts, flags=re.I)
assert not bad_skel and not bad_body, (bad_skel, bad_body)
bm = {"seed": SEED, "method": "random.Random(seed).shuffle(arms in given order)", "input_order": arms, "assignment": mapping,
      "r2_sha256": {a: hashlib.sha256(texts[a].encode("utf-8")).hexdigest() for a in arms},
      "note": "Blind評価後に開示。チャット報告本文には書かない。B案はR2未生成のため未収録(STOP)。"}
json.dump(bm, open(os.path.join(HERE, "BLIND_MAP_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("page written; n=", len(order), "leak_check=OK")
