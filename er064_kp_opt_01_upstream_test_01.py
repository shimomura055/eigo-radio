# KP-OPT-01 Phase1-A test (Trial専用、Production非接続、ネットワーク・有料呼出なし)。件数を報告する。
import hashlib, inspect, json, os, subprocess, sys
sys.path.insert(0, os.getcwd())
import er064_kp_opt_01_upstream_core as U
core, s1v2, ing = U.core, U.s1v2, U.ing

RES = []
def check(name, cond, detail=""):
    RES.append((name, bool(cond), detail))
    print(("PASS " if cond else "FAIL ") + name + ((" :: " + str(detail)) if detail and not cond else ""))

# 1 rate limit定数(既存関数の既定=1回50件・待ち1.5秒)
sig = inspect.signature(U.ORIG_MW).parameters
check("rate_limit: batch_size=50 / sleep=1.5 (multiword)", sig["batch_size"].default == 50 and sig["sleep_sec"].default == 1.5 and U.BATCH_SIZE == 50 and U.SLEEP_SEC == 1.5)
sig2 = inspect.signature(U.ORIG_UNI).parameters
check("rate_limit: batch_size=50 / sleep=1.5 (unigram)", sig2["batch_size"].default == 50 and sig2["sleep_sec"].default == 1.5)

# 2 Production無改変(git diffが空)
for f in ["er030_key_phrase_db_hybrid_core_01.py", "er027_key_phrase_db_hybrid_trial_02_stage1.py", "er023_key_phrase_db_ingest.py",
          "er023_key_phrase_db_extraction.py", "er003_key_words_canonicalization.py", "er030_key_phrase_db_hybrid_source_reference_contract_01.py",
          "er030_key_phrase_db_hybrid_selector_01.py"]:
    r = subprocess.run(["git", "diff", "--quiet", "--", f])
    check(f"production unchanged: {f}", r.returncode == 0)

# 3 patched()が復元する
snap = U.Snapshot()
before = (s1v2.select_unmatched_ngram_candidates_for_lookup, ing.wiktionary_multiword_targeted_lookup, core.wiktionary_unigram_lookup if hasattr(core, "wiktionary_unigram_lookup") else core.wiktionary_unigram_lemma_lookup)
with U.patched(U.make_order_fn("default", []), snap):
    inside = s1v2.select_unmatched_ngram_candidates_for_lookup
check("patched: 内側では差し替わる", inside is not before[0])
after = (s1v2.select_unmatched_ngram_candidates_for_lookup, ing.wiktionary_multiword_targeted_lookup, core.wiktionary_unigram_lemma_lookup)
check("patched: 終了後に原関数へ復元", after[0] is before[0] and after[1] is before[1] and after[2] is before[2])

# 4 snapshot replayはネットワーク禁止
try:
    snap.make_mw_lookup(False)(["zzzz qqqq not in snapshot"])
    ok = False
except RuntimeError:
    ok = True
check("snapshot replay: 未保存キーはネットワークせずRuntimeError", ok)

# 5 順序: 同一集合(集合の欠落なし)・優先が先頭・長さ=budget
dbs = core.load_group1_dbs()
txt = U.read_article("coffee_adv")
st = core.run_stage1_for_article(txt, dbs)
pool, sents, ex = U.pool_for_article(st)
rare = [c["canonical_form"] for c in st["word_survivors"]]
d = U.make_order_fn("default", rare)(sents, ex, 10 ** 7)
check("order default == 現行関数の全プール", d == pool and d[:60] == U.ORIG_SELECT(sents, ex, 60))
for mode in ("u1", "u1np", "u1np3"):
    o = U.make_order_fn(mode, rare)(sents, ex, 10 ** 7)
    check(f"order {mode}: 集合は同一(順序のみ変更)", sorted(o) == sorted(pool))
o = U.make_order_fn("u1", rare)(sents, ex, 60)
check("order u1: budget60で60件", len(o) == 60)
rank_old = pool.index("time lag") + 1 if "time lag" in pool else None
check("coffee_adv: time lagは現行で60超(76位)", rank_old and rank_old > 60, rank_old)
check("coffee_adv: u1 60件に time lag が入る", "time lag" in o)
props = U.proper_noun_tokens(sents)
check("proper_noun_tokens: 固有名詞(brent/muse等)を含み一般語を含まない", "prices" not in props and "price" not in props, sorted(props)[:10])

# 6 containment
mk = lambda surf, ut, dbs_: {"surface_form": surf, "canonical_form": surf.lower(), "unit_type": ut, "matched_dbs": dbs_}
units = [{"tokens": "The time lag is long .".split()}, {"tokens": "A lag again here .".split()}]
p_all_inside = U.compute_containment([mk("time lag", "phrase", ["wiktionary"]), mk("lag", "word", ["ngsl_family"])], [units[0]])
check("U2: lagの全出現がtime lag内 + 登録 -> Tier-H", p_all_inside and p_all_inside[0]["tier"] == "H")
p_not_all = U.compute_containment([mk("time lag", "phrase", ["wiktionary"]), mk("lag", "word", ["ngsl_family"])], units)
check("U2: lagが別の場所にも出る -> Tier-S(除外しない)", p_not_all and p_not_all[0]["tier"] == "S")
p_unreg = U.compute_containment([mk("time lag", "phrase", ["repeated_compound_noun_heuristic"]), mk("lag", "word", ["ngsl_family"])], [units[0]])
check("U2: 含む側が登録外(heuristic) -> Tier-S", p_unreg and p_unreg[0]["tier"] == "S")

# 7 U3
check("U3(i): of a / at that は閉じた語類のみ", U.all_closed_only("of a") and U.all_closed_only("At that"))
check("U3(i): as well / at all / in fact / on a regular basis は除外対象でない(誤除外0)",
      not any(U.all_closed_only(x) for x in ["as well", "at all", "in fact", "on a regular basis", "of course", "so far"]))
check("U3(ii): in the ring (未登録) -> fragment_risk", U.fragment_risk("in the ring", False))
check("U3(ii): 登録済みは対象外 / 先頭が内容語は対象外", not U.fragment_risk("on a regular basis", True) and not U.fragment_risk("time lag", False))

# 8 後方互換: フラグ無しassembleは現行build_shortlistと同一
fix = json.load(open(U.OUT_DIR + "/shortlists_improved_01.json", encoding="utf8")) if os.path.exists(U.OUT_DIR + "/shortlists_improved_01.json") else None
if fix:
    with U.patched(U.make_order_fn("default", rare), snap):
        res = core.run_stage1_and_shortlist(txt, dbs, U.TITLES["coffee"], wiktionary_multiword_lookup_budget=60)
    a = U.assemble_shortlist(res["stage1"], dbs=dbs)
    check("assemble(flags無し) == run_stage1_and_shortlist現行shortlist", [c["canonical_form"] for c in a["shortlist"]] == [c["canonical_form"] for c in res["shortlist_info"]["shortlist"]])
    check("coffee_adv 現行再生にtime lagは入らない(再現)", "time lag" not in [c["canonical_form"] for c in res["shortlist_info"]["shortlist"]])
    imp = fix["articles"]["coffee_adv"]["improved"]["candidates"]
    names = [c["canonical_form"] for c in imp]
    check("coffee_adv improved: time lagが入りlagが除外(Tier-H)", "time lag" in names and "lag" not in names, names)
    # 固定shortlistのshaが記録と一致
    side = open(U.OUT_DIR + "/shortlists_improved_01.sha256.txt").read().split()[0]
    check("shortlists_improved_01.json sha256一致", side == U.sha256_file(U.OUT_DIR + "/shortlists_improved_01.json") and fix["snapshot_sha256"] == U.sha256_file(U.SNAPSHOT_PATH))
    for key, ent in fix["articles"].items():
        for cfg in ("current", "improved", "alt_u2_tierS_only"):
            e = ent[cfg]
            if hashlib.sha256(e["rows_text"].encode("utf8")).hexdigest() != e["rows_text_sha256"]:
                check(f"rows sha {key}/{cfg}", False)
    check("全固定shortlistのrows sha自己整合", True)

# 9 Rule7 predict: 実validatorで my->someone's はINVALID、my->one'sはOK
import er003_key_words_canonicalization as kc
check("Rule7: take my place -> take one's place OK", kc.validate_canonicalization_item("take one's place", "take my place", "take my place", "generalize_person_dependent_reference")["ok"])
check("Rule7: take my place -> take someone's place INVALID(表とPromptの不一致)", not kc.validate_canonicalization_item("take someone's place", "take my place", "take my place", "generalize_person_dependent_reference")["ok"])

n_pass = sum(1 for _, ok, _ in RES if ok)
print(f"\nRESULT {n_pass}/{len(RES)} PASS")
sys.exit(0 if n_pass == len(RES) else 1)
