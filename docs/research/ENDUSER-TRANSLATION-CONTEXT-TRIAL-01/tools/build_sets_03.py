# 評価セット構築(TRIAL_PLAN_02 §2)。公開済み10記事の article.json から、生成対象partと金標準サンプルpartを決定論で抽出する。出力=ev05_sets/eval_sets_03.json
import json, os, re, sys, hashlib
ROOT = sys.argv[1]; OUT = sys.argv[2]
DEV = ["family_x_ai_chat_sponsored_persuasion_01", "family_x_jwst_mystery_emission_line_01", "family_x_moon_shrinking_reselect_01", "family_y_production_redelivery_fee_03", "family_z_melos_kphr_evidence_r3"]
HELD = ["family_x_meta_waddle_world_01", "family_x_untidiness_family_resource_01", "family_y_production_surname_choice_01", "family_z_yuki_onna_01", "family_z_in_a_grove_01"]
CJK = re.compile(r"[぀-ヿ㐀-鿿]")
GEN_KINDS = {"preview", "story", "comment", "oneline"}
out = {"dev": [], "heldout": []}
for split, lst in (("dev", DEV), ("heldout", HELD)):
    for slug in lst:
        a = json.load(open(os.path.join(ROOT, "user_test", slug, "enduser", "data", "article.json"), encoding="utf-8"))
        fam = a["family"]
        for lv, L in a["levels"].items():
            parts = []
            for p in L["parts"]:
                if "paragraphs" not in p or p["kind"] not in GEN_KINDS: continue
                sents = [{"sid": s["sid"], "en": s["text"], "para": pi} for pi, pa in enumerate(p["paragraphs"]) for s in pa if not CJK.search(s["text"])]
                if not sents: continue
                parts.append((p, sents))
            # 金標準サンプル: X/Yで承認済み訳(ja_source != generated)を持つstory partから、記事ごとに1 part(sha1決定論。Std/Adv交互)
            for p, sents in parts:
                gen = (p.get("ja_source") == "generated") or (fam == "Z")
                gold = fam in ("X", "Y") and p["kind"] == "story" and p.get("ja_source") != "generated"
                if gold:
                    # 記事内のstory part全体から決定論で1つ: 選ばれた(level, key)のみ残す
                    continue
                if not gen: continue
                out[split].append({"slug": slug, "family": fam, "level": lv, "part": p["key"], "kind": p["kind"], "stratum": "gen", "paragraphs": p["paragraphs"] and None, "sentences": sents, "title": a.get("topic_en", "")})
        # gold pick
        cands = []
        for lv, L in a["levels"].items():
            for p in L["parts"]:
                if fam in ("X", "Y") and p.get("kind") == "story" and p.get("ja_source") != "generated" and "paragraphs" in p:
                    sents = [{"sid": s["sid"], "en": s["text"], "para": pi} for pi, pa in enumerate(p["paragraphs"]) for s in pa if not CJK.search(s["text"])]
                    if sents: cands.append((lv, p, sents))
        if cands:
            cands.sort(key=lambda c: hashlib.sha1((slug + c[0] + c[1]["key"]).encode()).hexdigest())
            lv, p, sents = cands[0]
            ja = p.get("ja")
            out[split].append({"slug": slug, "family": fam, "level": lv, "part": p["key"], "kind": "story", "stratum": "gold", "sentences": sents, "title": a.get("topic_en", ""), "approved_ja_ref": ja})
for sp in out:
    for e in out[sp]: e.pop("paragraphs", None)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
import collections
for sp in out:
    c = collections.Counter(); sc = collections.Counter()
    for e in out[sp]: c[(e["family"], e["stratum"])] += 1; sc[(e["family"], e["stratum"])] += len(e["sentences"])
    print(sp, "parts", len(out[sp]), "sents", sum(len(e["sentences"]) for e in out[sp]), dict(c), dict(sc))
