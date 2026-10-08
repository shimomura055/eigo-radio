# -*- coding: utf-8 -*-
"""注記者用の自己完結プロンプト20本を生成する。決定論・API支出0。仕様v2・テンプレは逐語。
CLI: python build_prompts_01.py   (annotation/ 直下で実行。出力 prompts/, PROMPT_SHA256.json, AMBIGUOUS_FACT_MAP.json)"""
import hashlib, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(HERE)
sys.path.insert(0, BASE)
import b3_annotation_merge_01 as mg  # noqa: E402
rd = lambda p: open(p, encoding="utf-8", newline="").read()
sha = lambda b: hashlib.sha256(b).hexdigest()
SLUGS = ["byd_recall", "central_bank_mortgage", "hormuz", "inbound_tourism", "meta", "openai_copyright",
         "semiconductor_earnings", "small_bag", "space_weapons", "streaming_price"]
spec_p = os.path.join(BASE, "B3_ANNOTATION_SPEC_v2_ANNOTATOR.md")
tmpl = rd(os.path.join(BASE, "ANNOTATION_DELEGATION_TEMPLATE_v2.md"))
spec = rd(spec_p); spec_sha = sha(open(spec_p, "rb").read())
clar = rd(os.path.join(BASE, "stage_r", "SPEC_V2_CLARIFICATIONS.md"))
ca = re.search(r"^\(a\).*$", clar, re.M).group(0); cb = re.search(r"^\(b\).*$", clar, re.M).group(0)

HEADER = """【最初に必ず読む: このファイルの扱い】
- あなたが読んでよいファイルは、この1ファイルだけです。この1回の読み込みが、唯一許される道具(ツール)の使用です。
- このファイル以外のファイルを読まない。Grep・Globで探さない。コマンドを実行しない。Webを使わない。リポジトリ内の他のファイル(過去の注記、評価、仕様の他版など)には一切触れない。
- 読んだ後は、道具を一切使わず、下の「依頼文」の指示どおりに返答の本文だけで答える。ファイルを作らない・保存しない。

--------------------------------------------------------------------------------
【依頼文(ここから)】
"""
APPX = """
【依頼文の末尾: 運用上の明確化(仕様の規則変更ではなく、未定義の場合の適用方法)】
""" + ca + "\n" + cb + """

【返答の受け取り方】
返答の本文は、呼び出し側(あなたではない)が annotation/out/{ANN}/{SLUG}/ 以下に保存します。あなたは保存しません。返答は仕様の「6 出力の形式」(=== ANNOTATED_BRIEF_BEGIN === 等の区切りを使う形式)のとおりに、本文だけで返します。
【依頼文(ここまで)】
"""
ledger_re = re.compile(r"^\[(VERIFIED|AMBIGUOUS)[^\]]*\]\s*([^:\s]+):", re.M)
rows, shas, amb_map = [], {}, {}
for slug in SLUGS:
    d = os.path.join(BASE, "stage_r", slug)
    bp = os.path.join(d, "storyline_b3", "selected_brief.md")
    brief = rd(bp); ledger = rd(os.path.join(d, "research_ledger", "verified_fact_ledger.txt"))
    ev = json.load(open(os.path.join(d, "storyline_b3", "fact_selection_evidence.json"), encoding="utf-8"))
    ftxt = ev["selected_fact_brief_text"]
    extra = ""
    nl = lambda t: t.replace(chr(13)+chr(10), chr(10)).replace(chr(13), chr(10))
    strip_fmt = lambda t: re.sub(r"\s+|# Selected Fact Brief|## Storyline|## Selected Facts|Storyline:|素材:", "", nl(t))
    if strip_fmt(ftxt) not in strip_fmt(brief):
        extra = ("\n【参考: 事実選定記録の本文(元のニュース欄と異なる場合のみ付記)】\n" + ftxt + "\n")
    recs = ledger_re.findall(ledger)
    amb_ids = [i for s, i in recs if s == "AMBIGUOUS"]
    sel = list(ev["selected_fact_ids"])
    amb_map[slug] = {"ledger_records": len(recs), "ambiguous_ledger_ids": amb_ids,
                     "selected_ids": sel, "ambiguous_selected": [i for i in sel if i in amb_ids]}
    bsha = sha(open(bp, "rb").read())
    texts = {}
    for ann in "AB":
        body = mg.build_delegation(tmpl, ann, slug, spec, brief, ledger, spec_sha, bsha)
        full = HEADER + body + extra + APPX.replace("{ANN}", ann).replace("{SLUG}", slug)
        fn = f"{slug}__{ann}.md"
        open(os.path.join(HERE, "prompts", fn), "w", encoding="utf-8", newline="").write(full)
        shas[fn] = sha(full.encode("utf-8")); texts[ann] = full
    norm = lambda t, a, s=slug: t.replace(f"annotation/out/{a}/", "annotation/out/X/")
    # A/B差分 = 注記者名とout先だけ: 注記者名の置換箇所を正規化して一致確認
    na = norm(texts["A"], "A").replace("注記者は A です", "注記者は X です").replace("`annotator` には A", "`annotator` には X")
    nb = norm(texts["B"], "B").replace("注記者は B です", "注記者は X です").replace("`annotator` には B", "`annotator` には X")
    rows.append({"slug": slug, "lines": texts["A"].count("\n") + 1, "ledger_records": len(recs),
                 "brief_facts": len(re.findall(r"（[A-Z]+-?\d+(?:[,、 ]+[A-Z]+-?\d+)*）|\(\s*[A-Z]+-?\d+\s*\)", brief)),
                 "selected_fact_ids": len(sel), "ab_identical_after_normalization": na == nb,
                 "extra_fact_text_appended": bool(extra), "brief_sha256": bsha})
json.dump({"spec_sha256": spec_sha, "template_sha256": sha(open(os.path.join(BASE, "ANNOTATION_DELEGATION_TEMPLATE_v2.md"), "rb").read()),
           "prompts": shas, "themes": rows, "ab_all_identical": all(r["ab_identical_after_normalization"] for r in rows)},
          open(os.path.join(HERE, "PROMPT_SHA256.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
json.dump(amb_map, open(os.path.join(HERE, "AMBIGUOUS_FACT_MAP.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
for r in rows: print(r)
