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
    item = {"id": c["candidate_id"], "candidate_id": c["candidate_id"], "kind": xf.kind_of(c), "kind_source": xf.kind_source_of(c), "term": c["used_form"], "meaning_ja": c["japanese_gloss"], "excerpt": c["source_sentence"],
            "ja_gloss": c["japanese_gloss"], "ja_gloss_status": xf.gloss_status(c, "DEV_TRIAL"),
            "ja_gloss_source": "Trial-02 trial_result.json candidates[].japanese_gloss(再利用。AI再生成なし)",
            "reason_ja": rj, "reason_source": rsrc, "origin": c.get("origin")}
    if c.get("rescue"):
        item["flag"] = "rescued"
        item["flag_note_ja"] = "KP救済済み(" + ",".join(c["rescue"].get("codes", [])) + ")"
    (words if c.get("origin") == "call2" else phrases).append(item)
sha, sha_src = xf.sha_info(d["doc"], "DEV_TRIAL")      # Trial-02 docは自己sha無し→null(捏造しない)
data = {
    "schema": "eigo_radio_selection_article_v1", "slug": "monkeys_paw", "level": "b1b", "level_label": "Advanced",
    "name": "猿の手", "family": "Z",
    "candidates_sha256": sha, "candidates_sha256_source": sha_src, "source_kp_candidates_path": os.path.relpath(SRC, ROOT).replace(os.sep, "/"),
    "source": {"kind": "DEV_TRIAL", "trial": "KP-CANDIDATE-PHRASE7-WORD5-TRIAL-02", "run": "monkeys_paw__b1b__p7w5__r1",
               "text_sha256": d["text_sha256"], "model_id": d["doc"]["model_id"],
               "note_ja": "この候補はDEV Trial-02由来(Production候補生成Promptは現行のまま。7+5 Promptは未採用)。"},
    "phrases": phrases, "words": words,
    "grammar": [],
    "grammar_note_ja": "候補なし・要生成(この記事のPart 2文法解説候補は未生成です。仮データは入れていません)",
}
os.makedirs(OUT, exist_ok=True)
json.dump(data, open(os.path.join(OUT, "monkeys_paw__b1b.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print([(i["term"], i["kind"], i["kind_source"]) for i in phrases + words]); print(len(phrases), len(words), [p["term"] for p in phrases], [w["term"] for w in words])


# ---------------------------------------------------------------------------------------------------------------------
# 委任_04(2026-10-27): P7/W5'(KP_CANDIDATE_MAX 12・kind別cap 7/5)配線後の6経路evidence doc(run_kp75_ev_01)をフォームデータへ。API 0。
# 実行: py docs\research\LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01\build_data_01.py --kp75
# 旧3+5 doc(run_kpbf_ev_01)由来の同名__prod.jsonはdata/legacy/へ退避(上書き前)。AI理由・日本語訳は候補docの値を逐語(再生成なし)。
# ---------------------------------------------------------------------------------------------------------------------
KP75_NOTE = "Production正式経路(P7/W5'・候補上限12=フレーズ最大7+単語最大5・補完機能ON)で生成した候補です。選定フォームのテスト表示で、Production未連携。"
KP75 = [  # (出力ファイル, slug, level, 表示名, family, run, 候補docの相対path)
    ("ai_island_temple__a2__prod.json", "ai_island_temple_prod", "a2", "AIの仮想の島｜Production候補・7+5 evidence", "X", "ai_island_temple__run_kp75_ev_01", "er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_kp75_ev_01/a2/key_phrases/kp_candidates.json"),
    ("ai_island_temple__b1b__prod.json", "ai_island_temple_prod", "b1b", "AIの仮想の島｜Production候補・7+5 evidence", "X", "ai_island_temple__run_kp75_ev_01", "er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_kp75_ev_01/b1b/key_phrases/kp_candidates.json"),
    ("uk_train_speaker_playback__a2__prod.json", "uk_train_speaker_playback_prod", "a2", "英国の電車マナー｜Production候補・7+5 evidence", "X", "uk_train_speaker_playback__run_kp75_ev_01", "er019_output/family_x_audio_production_wiring_01/uk_train_speaker_playback__run_kp75_ev_01/a2/key_phrases/kp_candidates.json"),
    ("uk_train_speaker_playback__b1b__prod.json", "uk_train_speaker_playback_prod", "b1b", "英国の電車マナー｜Production候補・7+5 evidence", "X", "uk_train_speaker_playback__run_kp75_ev_01", "er019_output/family_x_audio_production_wiring_01/uk_train_speaker_playback__run_kp75_ev_01/b1b/key_phrases/kp_candidates.json"),
    ("redelivery_fee__a2__prod.json", "redelivery_fee_prod", "a2", "再配達手数料｜Production候補・7+5 evidence", "Y", "redelivery_fee/run_kp75_ev_01", "er121_output/family_y_production_01/redelivery_fee/run_kp75_ev_01/key_phrases/a2/kp_candidates.json"),
    ("redelivery_fee__b1b__prod.json", "redelivery_fee_prod", "b1b", "再配達手数料｜Production候補・7+5 evidence", "Y", "redelivery_fee/run_kp75_ev_01", "er121_output/family_y_production_01/redelivery_fee/run_kp75_ev_01/key_phrases/b1b/kp_candidates.json"),
    ("melos__a2__prod.json", "melos_prod", "a2", "走れメロス｜Production候補・7+5 evidence", "Z", "melos/run_kp75_ev_01", "er026_output/family_z_production_e2e_01/melos/run_kp75_ev_01/key_phrases/a2/kp_candidates.json"),
    ("melos__b1b__prod.json", "melos_prod", "b1b", "走れメロス｜Production候補・7+5 evidence", "Z", "melos/run_kp75_ev_01", "er026_output/family_z_production_e2e_01/melos/run_kp75_ev_01/key_phrases/b1b/kp_candidates.json"),
]


def build_kp75():
    import shutil
    legacy = os.path.join(OUT, "legacy")
    os.makedirs(legacy, exist_ok=True)
    moved = []
    for fn, slug, level, name, fam, run, rel in KP75:
        dst = os.path.join(OUT, fn)
        if os.path.exists(dst):                       # 旧3+5版(run_kpbf_ev_01)なら退避。既に7+5版(再実行)なら退避しない
            old = json.load(open(dst, encoding="utf-8"))
            if "run_kpbf_ev_01" in (old.get("source") or {}).get("run", "") and not os.path.exists(os.path.join(legacy, fn)):
                shutil.move(dst, os.path.join(legacy, fn)); moved.append(fn)
        doc = json.load(open(os.path.join(ROOT, rel), encoding="utf-8"))
        out = xf.convert(doc, slug=slug, level=level, name=name, family=fam, run=run, source_kind="PRODUCTION_FORMAL_PATH", note_ja=KP75_NOTE, cand_path=os.path.join(ROOT, rel))
        json.dump(out, open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(fn, len(out["phrases"]), len(out["words"]), out["cap"], out["cap_by_kind"], out["shortfall_note_ja"])
    print("moved_to_legacy:", moved)


if __name__ == "__main__" and "--kp75" in sys.argv:
    build_kp75()
