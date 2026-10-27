"""F班(委任_06F) evidence用 フォーム送信payload(v2)生成。--actor evidenceで使う(ユーザー確定ではない)。
候補doc(kp_candidates.json)から ①3件・②1〜2件・③2件以上 を決定的に選ぶ(活用形を含む候補を③に優先)。API 0。
"""
import argparse, json, re, sys


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def inflected(c):
    uf = (c.get("used_form") or "").lower()
    sp = (c.get("selection_phrase") or "").lower()
    toks = re.findall(r"[a-z']+", uf)
    return uf != sp or any(re.search(r"(ed|ing|s|es)$", t) and len(t) > 4 for t in toks)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kp-dir", required=True)
    ap.add_argument("--level", required=True)
    ap.add_argument("--slug", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--prefer", default="", help="①に優先する語句(カンマ区切り)")
    ap.add_argument("--n2", type=int, default=2)
    ap.add_argument("--n3", type=int, default=2)
    ap.add_argument("--grammar-sidecar", default=None, help="既存confirmed_grammar.json(items流用)。無ければ文法0件")
    ap.add_argument("--exclude", default="", help="除外する語句(カンマ区切り。redundant_with同士の同時採用を避ける)")
    ap.add_argument("--show", action="store_true")
    a = ap.parse_args()
    d = load(f"{a.kp_dir}/kp_candidates.json")
    cs = sorted(d["candidates"], key=lambda c: c.get("ai_rank", 99))
    if a.show:
        for c in cs:
            print(c["candidate_id"], c.get("ai_rank"), repr(c.get("used_form")), "|", repr(c.get("selection_phrase")), "| sel=", c.get("human_selectable"), "auto=", c.get("auto_eligible"), "infl=", inflected(c), "flags=", c.get("flags"))
    ok = [c for c in cs if c.get("human_selectable") and c.get("auto_eligible")]
    exc = {p.strip().lower() for p in a.exclude.split(",") if p.strip()}
    ok = [c for c in ok if (c.get("used_form") or "").lower() not in exc]
    pref = [p.strip().lower() for p in a.prefer.split(",") if p.strip()]
    cat1 = []
    for p in pref:
        for c in ok:
            if (c.get("used_form") or "").lower() == p and c not in cat1 and len(cat1) < 3:
                cat1.append(c)
    for c in ok:
        if len(cat1) < 3 and c not in cat1:
            cat1.append(c)
    rest = [c for c in ok if c not in cat1]
    # ③: 活用形を含む候補を優先(2件以上)。②: 残りのai_rank上位
    strict = [c for c in rest if (c.get("used_form") or "").lower() != (c.get("selection_phrase") or "").lower()]   # 表示形(活用形)が語句と異なる候補を最優先
    infl = strict + [c for c in rest if c not in strict and inflected(c)]
    cat3 = infl[: a.n3]
    rest2 = [c for c in rest if c not in cat3]
    cat2 = rest2[: a.n2]
    if len(cat3) < a.n3:
        cat3 += [c for c in rest2[a.n2:]][: a.n3 - len(cat3)]
    if len(cat3) < 2 or len(cat2) < 1:
        sys.exit(f"候補不足: cat1={len(cat1)} cat2={len(cat2)} cat3={len(cat3)} (ok={len(ok)})")

    def it(c, n):
        return {"term": c.get("used_form"), "category": n, "category_label": f"cat{n}", "ja_gloss": c.get("japanese_gloss"), "ja_gloss_status": "official",
                "candidate_id": c["candidate_id"], "kind": c.get("kind") or "phrase"}
    gram = []
    if a.grammar_sidecar:
        sc = load(a.grammar_sidecar)
        for g in sc.get("items") or []:
            gram.append({"id": g["id"], "candidate_id": g["id"], "title": g["title"], "explanation_full": g["explanation_full"], "explanation_status": g["explanation_status"],
                         "explanation_sha256": g.get("explanation_sha256"), "example": g.get("example")})
    payload = {"schema": "eigo_radio_selection_result_v2", "schema_version": 2, "schema_minor": 1,
               "article": {"slug": a.slug, "level": a.level, "text_sha256": d.get("text_sha256"), "candidates_sha256": d["candidates_sha256"]},
               "selection": {"key_phrase": [it(c, 1) for c in cat1], "extra_explanation": [it(c, 2) for c in cat2], "meaning_display": [it(c, 3) for c in cat3], "grammar": gram},
               "comment": "[EVIDENCE_RUN] ユーザー確定ではない。SLOT-23-CONSUMER-DESIGN-01 委任_06F runtime evidence用(actor=evidence)",
               "ai_reference": {"for_reference_only": True, "items": []}, "evidence_run": True}
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    print("cat1", [c["used_form"] for c in cat1]); print("cat2", [c["used_form"] for c in cat2]); print("cat3", [c["used_form"] for c in cat3]); print("grammar", [g["id"] for g in gram])


main()
