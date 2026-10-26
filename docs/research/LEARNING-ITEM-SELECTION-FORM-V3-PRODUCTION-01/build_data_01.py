# -*- coding: utf-8 -*-
"""猿の手 Advanced の試作候補データ(DEV Trial-02由来)を user_test/selection_form_v3/data/ へ書き出す。read-only入力、API 0。"""
import json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SRC = os.path.join(ROOT, "docs/research/KP-CANDIDATE-PHRASE7-WORD5-TRIAL-02/runs/monkeys_paw__b1b__p7w5__r1/trial_result.json")
OUT = os.path.join(ROOT, "user_test/selection_form_v3/data")
sys.path.insert(0, os.path.join(ROOT, "docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/tools"))
import export_form_data_01 as xf      # gloss_status / reason_info を共有(委任_02。日本語訳・理由はTrial-02既存doc値の再利用でAI再生成なし)
d = json.load(open(SRC, encoding="utf-8"))
phrases, words = [], []
for c in d["doc"]["candidates"]:
    rj, rsrc = xf.reason_info(c)
    item = {"id": c["candidate_id"], "term": c["used_form"], "meaning_ja": c["japanese_gloss"], "excerpt": c["source_sentence"],
            "ja_gloss": c["japanese_gloss"], "ja_gloss_status": xf.gloss_status(c, "DEV_TRIAL"),
            "ja_gloss_source": "Trial-02 trial_result.json candidates[].japanese_gloss(再利用。AI再生成なし)",
            "reason_ja": rj, "reason_source": rsrc, "origin": c.get("origin")}
    if c.get("rescue"):
        item["flag"] = "rescued"
        item["flag_note_ja"] = "KP救済済み(" + ",".join(c["rescue"].get("codes", [])) + ")"
    (words if c.get("origin") == "call2" else phrases).append(item)
data = {
    "schema": "eigo_radio_selection_article_v1", "slug": "monkeys_paw", "level": "b1b", "level_label": "Advanced",
    "name": "猿の手", "family": "Z",
    "source": {"kind": "DEV_TRIAL", "trial": "KP-CANDIDATE-PHRASE7-WORD5-TRIAL-02", "run": "monkeys_paw__b1b__p7w5__r1",
               "text_sha256": d["text_sha256"], "model_id": d["doc"]["model_id"],
               "note_ja": "この候補はDEV Trial-02由来(Production候補生成Promptは現行のまま。7+5 Promptは未採用)。"},
    "phrases": phrases, "words": words,
    "grammar": [],
    "grammar_note_ja": "候補なし・要生成(この記事のPart 2文法解説候補は未生成です。仮データは入れていません)",
}
os.makedirs(OUT, exist_ok=True)
json.dump(data, open(os.path.join(OUT, "monkeys_paw__b1b.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(phrases), len(words), [p["term"] for p in phrases], [w["term"] for w in words])
