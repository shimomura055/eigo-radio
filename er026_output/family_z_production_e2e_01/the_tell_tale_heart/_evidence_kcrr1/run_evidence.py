# -*- coding: utf-8 -*-
"""KP-CANON-REVIEW-REQUIRED-FIX-01 委任_01 runtime evidence(DEV注入。Production run dirへは書かない)。
入力: 『告げ口心臓』Std(a2)本文(保存済みselector promptから復元)+ 保存済み`vulture's`選定。
 mode A(実API最小): 選定#1のみ保存済みselection注入(vulture's含む)、canonicalizationは実Luna、再選定は実API。Z既定のkp_fn
        (w62.run_kp_with_outer_retry_fulltext = X/Z共通 sc.run_kp_with_outer_retry)を通す。
 mode B(API 0): 同じ入力で、canonicalization応答を保存済み(旧run)のQA FAIL行で再生。再選定も保存済みで固定 -> 上限到達 -> OUTER_RETRY_EXHAUSTED。
mode C(API 0): Bと同じだが全itemが保存済みvulture's相当のQA FAIL -> 通算3周とも不合格 -> OUTER_RETRY_EXHAUSTED。
usage: .venv/Scripts/python.exe run_evidence.py A|B|C
"""
import json, os, sys, time
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 4))
sys.path.insert(0, REPO); os.chdir(REPO)
from unittest import mock
import er003_key_words_canonicalization as kc
import er003_v1_n3_01_scaffold_generate as sc
import er105_kp_fulltext_selector_01 as ft
import er062_family_z_writer_01 as w62

SAVED = "er026_output/family_z_production_e2e_01/the_tell_tale_heart/_bak_pre04/kp_try1/a2/outer_retry"
OUT = os.path.dirname(os.path.abspath(__file__))
mode = sys.argv[1]
prompt = open(f"{SAVED}/attempt_1/keywords_selector_prompt.txt", encoding="utf-8").read()
text = prompt.split(ft.BODY_DELIMITER, 1)[1]
INJECT1 = {"items": [{"phrase": "in heaven and on earth", "word_count": 5}, {"phrase": "vulture's", "word_count": 1},
                     {"phrase": "metal catch", "word_count": 2}]}
orig_selector = ft.make_selector_fn
orig_canon = kc.make_canonicalization_fn
calls = {"selector": 0, "canon": 0, "real_selector": 0, "real_canon": 0}
log = []

def sel_factory(msg, **kw):
    calls["selector"] += 1
    n = calls["selector"]
    if n == 1:
        def fn():
            return json.dumps(INJECT1), "gpt-6-luna", "injected_saved_selection"
        return fn
    if mode == "A":
        calls["real_selector"] += 1
        return orig_selector(msg, **kw)
    def fn2():   # mode B: 以降は固定(vulture's を含み続ける選定。除外語gateが再選択を弾く/残りitemでcanonicalizationへ)
        return json.dumps(INJECT1), "gpt-6-luna", f"injected_{n}"
    return fn2

def canon_factory(um, **kw):
    calls["canon"] += 1
    if mode == "A":
        calls["real_canon"] += 1
        return orig_canon(um, **kw)
    saved = json.load(open(f"{SAVED}/attempt_3/canonicalization_runtime_metadata.json", encoding="utf-8"))["attempts_detail"][-1]["parsed"]["items"]
    by_phrase = {r["key_phrase"]: r for r in saved}
    marker = "【Key Phrase候補(JSON)】\n"
    items, _ = json.JSONDecoder().raw_decode(um.split(marker, 1)[1].lstrip())
    rows = []
    for it in items:
        r = dict(by_phrase.get(it["display_phrase"]) or {})
        if not r:   # 保存済みに無い語は全PASS行で埋める(構造は合格)
            r = {"key_phrase": it["display_phrase"], "changed_from_display_phrase": False, "normalization_reason": "none", "reasoning": "replay"}
            for f in kc.QA_FIELDS:
                r[f] = "PASS"
        if mode == "C":   # 全itemが保存済みvulture'sと同じQA FAILを持つ(再選定でも解消しない場合)
            vf = by_phrase["vulture's"]
            r.update({k: v for k, v in vf.items() if k.startswith("qa_")})
        r["rank"] = it["rank"]
        rows.append(r)
    def fn():
        return json.dumps({"items": rows}, ensure_ascii=False), "replay-saved", "replay"
    return fn

# gloss alignmentはmode Bでは実APIを避けるためfake(対象0件なら呼ばれない)
d = f"{OUT}/mode_{mode}/kp"
os.makedirs(d, exist_ok=True)
t0 = time.time()
patches = [mock.patch.object(ft, "make_selector_fn", sel_factory)]
if mode in ("B", "C"):
    import er003_key_words_gloss_alignment as ga
    import er011_key_phrase_set_redundancy_qa_01 as rq
    sys.path.insert(0, REPO)
    from er003_test_kp_fulltext_wiring_01 import fake_gloss_factory, fake_red_factory
    patches += [mock.patch.object(kc, "make_canonicalization_fn", canon_factory),
                mock.patch.object(ga, "make_alignment_fn", fake_gloss_factory()),
                mock.patch.object(rq, "make_redundancy_qa_fn", fake_red_factory([]))]
for p in patches: p.start()
try:
    res = w62.run_kp_with_outer_retry_fulltext(text, d, f"kcrr1_evidence_{mode}", "A2", process="A2_SUPPORT")
finally:
    for p in patches: p.stop()
summ = {"mode": mode, "elapsed_sec": round(time.time() - t0, 1), "calls": calls, "final_status": res.get("status"),
        "canonicalization_status": (res.get("canonicalization") or {}).get("status"),
        "kp_final_exists": os.path.exists(f"{d}/keywords_canonicalized.json"),
        "stale": sorted(x for x in os.listdir(d) if x.startswith("keywords_canonicalized.STALE")),
        "outer_retry_log": [{k: v for k, v in e.items() if k in ("outer_attempt", "selection_phrases", "selection_status", "canonicalization_status",
                             "review_required_ranks", "excluded_phrases_added", "excluded_phrases_in", "excluded_phrase_reselected", "redundancy_status")}
                            for e in res["outer_retry_log"]]}
if os.path.exists(f"{d}/keywords_canonicalized.json"):
    doc = json.load(open(f"{d}/keywords_canonicalized.json", encoding="utf-8"))
    summ["adopted_items"] = [(i["display_phrase"], i["key_phrase"], i.get("qa_overall_status")) for i in doc["items"]]
json.dump(summ, open(f"{OUT}/summary_{mode}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(json.dumps(summ, ensure_ascii=False, indent=2))
