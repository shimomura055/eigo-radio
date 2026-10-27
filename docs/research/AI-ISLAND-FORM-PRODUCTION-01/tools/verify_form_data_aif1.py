# -*- coding: utf-8 -*-
# AI-ISLAND-FORM-PRODUCTION-01: フォーム登録データ(user_test/selection_form_v3/data/ai_island_temple__{a2,b1b}__prod.json)と元データ(kp_candidates.json / grammar_explanations.json)の逐語照合。API 0。
import json, hashlib, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = "."
KP = "er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_kp75_ev_01/%s/key_phrases/kp_candidates.json"
GP = "docs/research/AI-ISLAND-FORM-PRODUCTION-01/grammar_prep_out/%s/study_text/"
ART = "er019_output/ai_island_temple/run_ai_01/%s/article.md"
bad = 0
def chk(name, ok, d=""):
    global bad
    print(("PASS " if ok else "FAIL ") + name + (" :: " + d if d else ""))
    bad += (not ok)
for l in ("a2", "b1b"):
    f = json.load(open(f"user_test/selection_form_v3/data/ai_island_temple__{l}__prod.json", encoding="utf-8"))
    kp = json.load(open(KP % l, encoding="utf-8"))
    by = {c["candidate_id"]: c for c in kp["candidates"]}
    items = f["phrases"] + f["words"]
    chk(f"{l} candidates_sha256 == source doc", f["candidates_sha256"] == kp["candidates_sha256"] and f["candidates_sha256_source"] == "candidate_doc_field")
    chk(f"{l} 10 candidates, all ids in source, no extras/missing", sorted(e["id"] for e in items) == sorted(by) and not f.get("overflow"))
    chk(f"{l} term==used_form, gloss==japanese_gloss, reason==reason_ja, excerpt==source_sentence, rank, kind verbatim",
        all(e["term"] == by[e["id"]]["used_form"] and e["ja_gloss"] == by[e["id"]]["japanese_gloss"] == e["meaning_ja"] and e["reason_ja"] == by[e["id"]]["reason_ja"]
            and e["excerpt"] == by[e["id"]]["source_sentence"] and e["ai_rank"] == by[e["id"]]["ai_rank"] and e["kind"] == by[e["id"]]["kind"] for e in items))
    chk(f"{l} ja_gloss_status: all official (0 provisional/missing)", all(e["ja_gloss_status"] == "official" for e in items), str({e["ja_gloss_status"] for e in items}))
    art = open(ART % l, encoding="utf-8").read()
    nq = lambda t: t.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')   # 引用符の字種差のみ吸収(本文は curly、source_sentenceはstraight)
    chk(f"{l} every candidate excerpt appears in current approved article.md (quote glyph normalized)", all(nq(e["excerpt"]) in nq(art) for e in items))
    chk(f"{l} cap 12 / 7+5", f["cap"] == 12 and f["cap_by_kind"] == {"phrase": 7, "word": 5} and len(f["phrases"]) <= 7 and len(f["words"]) <= 5)
    sm = json.load(open(f"docs/research/AI-ISLAND-FORM-PRODUCTION-01/grammar_prep_out/summary_{l}.json", encoding="utf-8"))
    cand = json.load(open(GP % l + "grammar_candidates.json", encoding="utf-8"))
    ex = json.load(open(GP % l + "grammar_explanations.json", encoding="utf-8"))
    exb = {i["candidate_id"]: i for i in ex["items"]}
    cb = {c["candidate_id"]: c for c in cand["candidates"]}
    chk(f"{l} grammar ids == candidate doc ids == explanations ids ({len(f['grammar'])})", [g["id"] for g in f["grammar"]] == [c["candidate_id"] for c in cand["candidates"]] == [i["candidate_id"] for i in ex["items"]])
    chk(f"{l} grammar title==construct_ja, body==explanation_md (verbatim), example==sentence, sha==sha256(explanation_md)",
        all(g["title"] == cb[g["id"]]["construct_ja"] and g["body"] == g["explanation_full"] == exb[g["id"]]["explanation_md"] and g["example"] == cb[g["id"]]["sentence"]
            and g["explanation_sha256"] == hashlib.sha256(exb[g["id"]]["explanation_md"].encode("utf-8")).hexdigest() == exb[g["id"]]["explanation_sha256"] for g in f["grammar"]))
    chk(f"{l} grammar example sentence appears verbatim in approved article.md", all(g["example"] in art for g in f["grammar"]))
    chk(f"{l} grammar source: text_sha256 equals KP doc text_sha256 (same body)", cand["text_sha256"] != "" and f["grammar_source"]["text_sha256"] == cand["text_sha256"] and f["source"]["text_sha256"] == kp["text_sha256"])
    chk(f"{l} explanations ref_ja=None, model=gpt-6-luna, StepB prompt sha recorded", sm["ref_ja"] is None and ex["model"] == "gpt-6-luna" and ex["stepb_prompt_sha256"] == sm["stepb_prompt_sha256"])
    chk(f"{l} all explanations source=pregen (presented before selection)", all(i["source"] == "pregen" for i in ex["items"]))
print("SUMMARY bad=%d" % bad)
sys.exit(1 if bad else 0)
