"""API 0。(1) Z repair経路(ga.align_glosses(only_ranks=...)、current glossあり)が新経路0回であること(実Z artifact使用)、
(2) 混在batch(gloss有+null)が正式module経由で2 callになること(実Z artifactのitem流用・fake LLM)。"""
import copy, json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *([".."] * 4)))
sys.path.insert(0, ROOT); os.chdir(ROOT)
import er003_key_words_gloss_alignment as ga

Z = "er026_output/family_z_production_e2e_01/the_monkeys_paw/run_kpgm35_01/key_phrases/b1b/keywords_canonicalized.json"
kp = json.load(open(Z, encoding="utf-8"))
seen = []


def factory(msg):
    if "catch someone" in msg:
        seen.append((type(msg).__name__, "person-repair"))
        def fn0():
            return json.dumps({"items": [{"rank": 1, "current_gloss_consistent": False, "japanese_gloss": "人の注意を引く", "qa_reflects_all_key_phrase_words": "PASS", "reasoning": "fake", "added_word_mappings": []}]}, ensure_ascii=False), "gpt-6-luna", "fake"
        fn0.last_usage = None
        return fn0
    seen.append((type(msg).__name__, "【新規生成の規則】" in msg and "【範囲の規則" in msg))
    ranks = [int(x) for x in __import__("re").findall(r'"rank": (\d+)', msg.split("【対象項目】", 1)[1])]
    rows = []
    for r in ranks:
        it = next(i for i in kp["items"] if i["rank"] == r)
        row = {"rank": r, "current_gloss_consistent": True, "japanese_gloss": it["japanese_gloss"], "qa_reflects_all_key_phrase_words": "PASS",
               "reasoning": "fake", "added_word_mappings": []}
        if isinstance(msg, ga.NewGenMessage):
            row.update({"current_gloss_consistent": False, "meaning_in_text_en": "m", "naive_ja": "n", "naive_ja_conveys": "yes"})
        rows.append(row)

    def fn():
        return json.dumps({"items": rows}, ensure_ascii=False), "gpt-6-luna", "fake"
    fn.last_usage = None
    return fn


# (1) Z repair: 人称不整合を作った項目のみ only_ranks
rep = copy.deepcopy(kp)
rep["items"][0].update({"key_phrase": "catch someone's attention", "used_form": "catch someone's attention", "display_phrase": "catch your attention",
                         "normalization_reason": ga.PERSON_NORMALIZATION_REASON, "japanese_gloss": "あなたの注意を引く"})   # 人称不整合(Z repair対象)を人工的に作る
out = ga.align_glosses(rep, "ART", factory, enabled=True, only_ranks=[1])
r1 = {"calls": list(seen), "n_newgen_calls": out["meaning_stage"]["n_newgen_calls"], "stage": out["meaning_stage"]["stage"],
      "n_repaired": out["meaning_stage"].get("n_repaired")}
seen.clear()
# (2) 混在: item1=gloss有(legacy)、item2/3=gloss null + fulltext_source_ref(newgen)
mix = copy.deepcopy(kp)
for it in mix["items"][1:]:
    it["japanese_gloss"] = None
    for k in [k for k in it if k.startswith("gloss_")] + ["japanese_gloss_tts"]:
        it.pop(k, None)
mix["items"][0].update(rep["items"][0])           # glossあり+人称不整合=legacy側の再整合対象
mix["items"][0].pop("gloss_alignment", None)
mix["items"][0].pop("gloss_alignment_status", None)
out2 = ga.align_glosses(mix, "ART", factory, enabled=True, only_ranks=None)
r2 = {"targets": out2["targets"], "calls": list(seen), "meaning_stage": out2["meaning_stage"],
      "attempt_paths": [a.get("path") for a in out2["attempts"]]}
res = {"z_repair_check": r1, "mixed_check": r2}
json.dump(res, open(os.path.join(os.path.dirname(__file__), "z_repair_and_mixed_check_35.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1))
