# KP-OPT-01 Phase1-A: U1/予算拡大/U2/U3/U4のオフライン検証。snapshot注入で run_stage1_and_shortlist を全体再生(Trial専用、Production非接続、有料呼出なし)。
import collections
import glob
import json
import os
import sys

sys.path.insert(0, os.getcwd())
import er064_kp_opt_01_upstream_core as U  # noqa: E402

core = U.core
ext = U.ext
OUT = U.OUT_DIR
import er030_key_phrase_db_hybrid_selector_01 as sel  # noqa: E402


def dump(name, obj):
    json.dump(obj, open(f"{OUT}/{name}", "w", encoding="utf8"), ensure_ascii=False, indent=1)


snap = U.Snapshot()
dbs = core.load_group1_dbs()


def title_of(key):
    return U.TITLES[U.article_theme(key)]


STAGE1 = {}
POOLS = {}


def base(key):
    if key not in STAGE1:
        st = core.run_stage1_for_article(U.read_article(key), dbs)
        STAGE1[key] = st
        POOLS[key] = U.pool_for_article(st)[0]
    return STAGE1[key], POOLS[key]


def replay(key, mode, k, budget):
    """run_stage1_and_shortlist をsnapshot注入で全体再生。戻り: (result, queried候補list)"""
    st0, pool = base(key)
    rare = [c["canonical_form"] for c in st0["word_survivors"]]
    fn = U.make_order_fn(mode, rare, k=k)
    queried = []

    def rec(sents, ex, budget=40):
        r = fn(sents, ex, budget)
        queried.extend(r)
        return r
    with U.patched(rec, snap, allow_net_mw=False, allow_net_uni=True):
        res = core.run_stage1_and_shortlist(U.read_article(key), dbs, title_of(key), wiktionary_multiword_lookup_budget=budget)
    return res, queried


def mw_survivors(stage1):
    """gate・名詞句判定・重複除去を通ったonline multiword hit(canonical_form -> 'important'/'demoted')"""
    out = {}
    for c in stage1["important_noun_candidates"]:
        if c.get("db_categories") == ["multiword_term"] and c.get("matched_dbs") == ["wiktionary"]:
            out[c["canonical_form"]] = "important"
    for c in stage1["phrase_survivors"]:
        if c.get("db_categories") == ["multiword_term"] and c.get("matched_dbs") == ["wiktionary"]:
            out[c["canonical_form"]] = "demoted"
    return out


def words_in_shortlist(sl):
    return {c["canonical_form"] for c in sl if c["unit_type"] == "word"}


# ============================================================
# 1. U1 vs 予算拡大 vs 両方
# ============================================================
CFG1 = [  # name, mode, k, budget(None = n2+3gram cap)
    ("cur60", "default", 10, 60),
    ("u1_k10_60(固有名詞込み)", "u1", 10, 60),
    ("u1np_k10_60(固有名詞除外)", "u1np", 10, 60),
    ("u1np_k20_60", "u1np", 20, 60),
    ("u1np3_k10_60(2語+3語優先)", "u1np3", 10, 60),
    ("cur120", "default", 10, 120),
    ("u1np_k10_120", "u1np", 10, 120),
    ("expand(2語全件+3語上限100)", "default", 10, None),
    ("both(U1np+expand)", "u1np", 10, None),
]

latency = snap.batch_stats("multiword")["mean_request_latency_sec"]
sec1 = {"latency_sec_per_request(実測平均)": latency, "http429_total_in_snapshot": snap.d["http429_total"], "per_article": {}}
GT = {}
for key in U.ARTICLES:
    st0, pool = base(key)
    n2 = sum(1 for p in pool if len(p.split()) == 2)
    n3 = len(pool) - n2
    # ground truth: プール全件(2語+3語全件)を照会した場合に生き残る multiword hit
    resgt, qgt = replay(key, "default", 10, len(pool))
    gt = mw_survivors(resgt["stage1"])
    GT[key] = gt
    cur_hits = None
    rows = {}
    cur_words = None
    for name, mode, k, budget in CFG1:
        b = budget if budget is not None else n2 + U.THREEGRAM_CAP
        res, q = replay(key, mode, k, b)
        sv = mw_survivors(res["stage1"])
        n_q = len(set(q))
        calls, secs = U.estimate_lookup_seconds(n_q, latency)
        sl = res["shortlist_info"]["shortlist"]
        if name == "cur60":
            cur_hits = set(sv)
            cur_words = words_in_shortlist(sl)
        missed = sorted(set(gt) - set(sv))
        # time lag型: 取りこぼした hit が現行shortlistのword候補を含む(包含される単語がshortlistにいる)
        lagtype = [m for m in missed if any(w in [U._stem(t) for t in m.split()] or w in m.split() for w in (cur_words or []))]
        rows[name] = {"queried": n_q, "queried_2gram": sum(1 for x in set(q) if len(x.split()) == 2),
                      "queried_3gram": sum(1 for x in set(q) if len(x.split()) == 3),
                      "survivor_hits": sorted(sv), "survivor_n": len(sv),
                      "new_vs_cur60": sorted(set(sv) - cur_hits) if cur_hits is not None else [],
                      "lost_vs_cur60": sorted(cur_hits - set(sv)) if cur_hits is not None else [],
                      "missed_vs_ground_truth": missed, "ground_truth_n": len(gt), "lag_type_missed(現行shortlist word包含)": lagtype,
                      "est_api_calls": calls, "est_lookup_seconds": secs,
                      "queried_set_hash": U.sha256_text("\n".join(sorted(set(q))))[:12]}
        if name == "cur60":
            rows[name]["lag_type_missed_before"] = lagtype
    sec1["per_article"][key] = {"pool_2gram": n2, "pool_3gram": n3, "ground_truth_survivors": gt, "configs": rows,
                                "time_lag_in_pool_rank": (pool.index("time lag") + 1) if "time lag" in pool else None}
    print(key, {n: (r["survivor_n"], len(r["new_vs_cur60"]), len(r["lost_vs_cur60"]), len(r["missed_vs_ground_truth"])) for n, r in rows.items()}, flush=True)

# 集計(config別)
agg = {}
for name, *_ in CFG1:
    a = {"survivor_total": 0, "new_total": 0, "lost_total": 0, "missed_total": 0, "gt_total": 0, "lagtype_missed_total": 0, "queried_total": 0, "est_seconds_total": 0.0, "est_calls_total": 0}
    for key, v in sec1["per_article"].items():
        r = v["configs"][name]
        a["survivor_total"] += r["survivor_n"]; a["new_total"] += len(r["new_vs_cur60"]); a["lost_total"] += len(r["lost_vs_cur60"])
        a["missed_total"] += len(r["missed_vs_ground_truth"]); a["gt_total"] += r["ground_truth_n"]
        a["lagtype_missed_total"] += len(r["lag_type_missed(現行shortlist word包含)"]); a["queried_total"] += r["queried"]
        a["est_seconds_total"] += r["est_lookup_seconds"]; a["est_calls_total"] += r["est_api_calls"]
    a["est_seconds_per_article_level"] = round(a["est_seconds_total"] / len(U.ARTICLES), 1)
    agg[name] = a
sec1["aggregate"] = agg
# cache効果: 全記事での照会ユニーク数 vs 記事別合計
expand_total = sum(v["configs"]["expand(2語全件+3語上限100)"]["queried"] for v in sec1["per_article"].values())
all_union = set()
for key in U.ARTICLES:
    _, pool = base(key)
    n2 = sum(1 for p in pool if len(p.split()) == 2)
    all_union |= set(pool[: n2 + U.THREEGRAM_CAP])
sec1["cache_effect_expand"] = {"sum_per_article_queries": expand_total, "unique_across_10_article_levels": len(all_union)}
sec1["measured_batches"] = {"multiword": snap.batch_stats("multiword"), "multiword_lower": snap.batch_stats("multiword_lower")}
# 小文字variant: 現行表記(文頭大文字等)での照会と小文字照会の差
lv = {"lower_variant_queries": len(snap.d["multiword_lower"]), "extra_hits_if_lowercased": []}
for t, v in snap.d["multiword_lower"].items():
    if v["hit"]:
        orig_hit = any(snap.d["multiword"].get(x, {}).get("hit") for x in snap.d["multiword"] if x.lower() == t and x != t)
        lv["extra_hits_if_lowercased"].append({"lower": t, "case_form_hit": bool(orig_hit)})
sec1["lowercase_query_normalization"] = lv
dump("u1_vs_budget_expand_01.json", sec1)

# ============================================================
# 2. shortlist到達の全体再生 + U2/U3/U4
# ============================================================
EXPAND = ("default", 10, None)
STACKS = {
    "S0_current": dict(src=("default", 10, 60), kw={}),
    "S1_U1np": dict(src=("u1np", 10, 60), kw={}),
    "S2_expand": dict(src=EXPAND, kw={}),
    "S3a_expand+U2(Tier-H+S)": dict(src=EXPAND, kw=dict(u2="tierH+S")),
    "S3b_expand+U2(Tier-S注釈のみ)": dict(src=EXPAND, kw=dict(u2="tierS")),
    "S4_expand+U3(除外+fragment_risk注釈)": dict(src=EXPAND, kw=dict(u3_exclude=True, u3_annotate=True)),
    "S5a_expand+U4(cap20)": dict(src=EXPAND, kw=dict(phrase_cap=20)),
    "S5b_expand+U4(demoted整列のみ)": dict(src=EXPAND, kw=dict(realign=True)),
    "S5c_expand+U4(cap20+整列)": dict(src=EXPAND, kw=dict(phrase_cap=20, realign=True)),
    "S5d_expand+U4(出現順タイブレーク,cap15)": dict(src=EXPAND, kw=dict(tiebreak_pos=True)),
    "S6_U1np+U2H+U3+U4c(予算60据置)": dict(src=("u1np", 10, 60), kw=dict(u2="tierH+S", u3_exclude=True, u3_annotate=True, phrase_cap=20, realign=True)),
    "S7_improved(expand+U2H+U3+U4c)": dict(src=EXPAND, kw=dict(u2="tierH+S", u3_exclude=True, u3_annotate=True, phrase_cap=20, realign=True)),
    "S7b_improved_U2tierS(expand+U2S+U3+U4c)": dict(src=EXPAND, kw=dict(u2="tierS", u3_exclude=True, u3_annotate=True, phrase_cap=20, realign=True)),
    "S8_expand+精度ガード(窓外のdemoted hitを入れない)": dict(src=EXPAND, kw=dict(guard=True)),
    "S9_precision_guarded_improved(S8+U2H+U3+U4c)": dict(src=EXPAND, kw=dict(guard=True, u2="tierH+S", u3_exclude=True, u3_annotate=True, phrase_cap=20, realign=True)),
}


def canon_list(sl):
    return [c["canonical_form"] for c in sl]


sec2 = {"per_article": {}}
FIXED = {}
cur_tokens = {}
for key in U.ARTICLES:
    st0, pool = base(key)
    n2 = sum(1 for p in pool if len(p.split()) == 2)
    per = {}
    cache_res = {}
    for sname, cfg in STACKS.items():
        mode, k, b = cfg["src"]
        b = b if b is not None else n2 + U.THREEGRAM_CAP
        rk = (mode, k, b)
        if rk not in cache_res:
            cache_res[rk] = replay(key, mode, k, b)
        res, q = cache_res[rk]
        # stage1は再生ごとに新しいdictだが、assembleは非破壊(dict浅いコピー+新リスト)
        kw = dict(cfg["kw"])
        if kw.pop("guard", False):
            kw["demoted_allow"] = set(sec1["per_article"][key]["configs"]["cur60"]["survivor_hits"])
        out = U.assemble_shortlist(res["stage1"], dbs=dbs, **kw)
        sl = out["shortlist"]
        txt_plain = U.candidate_row_text(sl, out["sentence_reference"], with_annotations=False)
        txt_ann = U.candidate_row_text(sl, out["sentence_reference"], with_annotations=True, pairs=out["containment_pairs"])
        tok = U.approx_tokens(txt_ann)
        if sname == "S0_current":
            cur_tokens[key] = U.approx_tokens(txt_plain)
            cur_list = canon_list(sl)
        cl = canon_list(sl)
        stg = res["stage1"]
        dem = stg["wiktionary_multiword_lookup"]["hits_demoted_to_phrase_after_pos_refine"]
        per[sname] = {
            "counts": out["counts"], "total": len(sl), "tokens_approx": tok, "tokens_plain_approx": U.approx_tokens(txt_plain),
            "token_delta_vs_current": tok - cur_tokens[key],
            "added_vs_current": [c for c in cl if c not in cur_list], "removed_vs_current": [c for c in cur_list if c not in cl],
            "multiword_online_hits_in_shortlist": [c for c in cl if c in mw_survivors(stg)],
            "demoted_to_phrase_in_stage1": dem,
            "demoted_in_shortlist": [d for d in dem if d in cl],
            "demoted_cut_by_cap": [d for d in dem if d not in cl],
            "u2_removed_tier_h": out["u2_removed_tier_h"], "u2_pairs": out["containment_pairs"],
            "u3_excluded_closed_only": out["u3_excluded_closed_only"],
            "u3_fragment_risk": [c["canonical_form"] for c in sl if c.get("fragment_risk")],
            "shortlist": cl,
            "time_lag_in_shortlist": "time lag" in cl, "lag_in_shortlist": "lag" in cl,
            "phrase_survivors_total": len(stg["phrase_survivors"]),
        }
        if sname in ("S0_current", "S7_improved(expand+U2H+U3+U4c)", "S7b_improved_U2tierS(expand+U2S+U3+U4c)", "S9_precision_guarded_improved(S8+U2H+U3+U4c)"):
            FIXED.setdefault(key, {})[sname] = {
                "rows_text": txt_ann, "rows_text_sha256": U.sha256_text(txt_ann),
                "sentence_reference": out["sentence_reference"],
                "candidates": [{"surface_form": c["surface_form"], "canonical_form": c["canonical_form"], "unit_type": c["unit_type"],
                                "important_noun_phrase_candidate": bool(c.get("important_noun_phrase_candidate")),
                                "evidence": sel._compact_evidence_string(c), "occ": c.get("occurrence_count_in_article"),
                                "sentence_id": c.get("context_sentence_id"), "fragment_risk": bool(c.get("fragment_risk"))} for c in sl],
                "containment_pairs": out["containment_pairs"]}
    sec2["per_article"][key] = per
    print(key, {s: (v["total"], v["tokens_approx"]) for s, v in per.items()}, flush=True)

# 集計
agg2 = {}
for sname in STACKS:
    a = {"shortlist_total": 0, "tokens_delta_total": 0, "added": 0, "removed": 0}
    for key, per in sec2["per_article"].items():
        v = per[sname]
        a["shortlist_total"] += v["total"]; a["tokens_delta_total"] += v["token_delta_vs_current"]
        a["added"] += len(v["added_vs_current"]); a["removed"] += len(v["removed_vs_current"])
    a["mean_shortlist"] = round(a["shortlist_total"] / len(U.ARTICLES), 1)
    a["mean_token_delta"] = round(a["tokens_delta_total"] / len(U.ARTICLES), 1)
    agg2[sname] = a
sec2["aggregate"] = agg2
dump("shortlist_replay_01.json", sec2)

# --- demoted_to_phrase がcapで切られる問題の集計 (U4) ---
dem_tab = {}
for key, per in sec2["per_article"].items():
    row = {}
    for sname in ("S2_expand", "S5a_expand+U4(cap20)", "S5b_expand+U4(demoted整列のみ)", "S5c_expand+U4(cap20+整列)", "S5d_expand+U4(出現順タイブレーク,cap15)"):
        v = per[sname]
        row[sname] = {"demoted_total": len(v["demoted_to_phrase_in_stage1"]), "in_shortlist": len(v["demoted_in_shortlist"]), "cut": v["demoted_cut_by_cap"],
                      "phrase_slots": v["counts"]["phrase"]}
    dem_tab[key] = {"phrase_survivors_total": per["S2_expand"]["phrase_survivors_total"], **row}
dump("u4_demoted_cap_01.json", dem_tab)

# --- 固定shortlist(Phase 2入力) ---
fixed_out = {"purpose": "KP-OPT-01 Phase 2へ渡す固定shortlist (current=現行構成の再生 / improved=expand+U2(Tier-H+S)+U3(除外+fragment_risk注釈)+U4(cap20+整列) / alt_u2_tierS_only=improvedのU2をTier-S注釈のみに / alt_precision_guarded=improved+窓外のdemoted hit(一般的な短い複数語)をphraseへ入れない精度ガード)",
             "snapshot": "wiktionary_snapshot_01.json", "snapshot_sha256": U.sha256_file(U.SNAPSHOT_PATH),
             "phase2_target_articles": ["coffee_std", "coffee_adv", "meta_std", "meta_adv", "hormuz_std", "hormuz_adv"],
             "articles": {}}
for key, d in FIXED.items():
    ent = {"article_path": U.ARTICLES[key], "article_sha256": U.sha256_text(U.read_article(key))}
    ent["current"] = d["S0_current"]
    ent["improved"] = d["S7_improved(expand+U2H+U3+U4c)"]
    ent["alt_u2_tierS_only"] = d["S7b_improved_U2tierS(expand+U2S+U3+U4c)"]
    ent["alt_precision_guarded"] = d["S9_precision_guarded_improved(S8+U2H+U3+U4c)"]
    fixed_out["articles"][key] = ent
body = json.dumps(fixed_out, ensure_ascii=False, indent=1, sort_keys=True)
open(f"{OUT}/shortlists_improved_01.json", "w", encoding="utf8").write(body)
open(f"{OUT}/shortlists_improved_01.sha256.txt", "w", encoding="utf8", newline="\n").write(U.sha256_file(f"{OUT}/shortlists_improved_01.json") + "  shortlists_improved_01.json\n")

# ============================================================
# 3. U3 断片検出の誤除外集計
# ============================================================
sec3 = {"existing_closed_set_size": len(U.CLOSED), "per_article": {}, "dictionary_scan": {}, "extractor_span_scan": {}}
wk = dbs["wiktionary"]
for key in U.ARTICLES:
    res, q = replay(key, "default", 10, 10 ** 6)
    st = res["stage1"]
    allc = list(st["phrase_survivors"]) + list(st["important_noun_candidates"])
    closed_only = [{"canonical": c["canonical_form"], "matched_dbs": c.get("matched_dbs"), "db_categories": c.get("db_categories")} for c in allc if U.all_closed_only(c["surface_form"])]
    frag = [{"canonical": c["canonical_form"], "matched_dbs": c.get("matched_dbs")} for c in allc
            if U.fragment_risk(c["surface_form"], U.is_dictionary_registered(c) or c["canonical_form"] in wk)]
    sec3["per_article"][key] = {"phrase_and_important_candidates": len(allc), "closed_only_excluded_by_U3i": closed_only,
                                "fragment_risk_annotated_U3ii": frag}
# 既知の正当な成句(誤除外の目視判定用の正例リスト): 閉じた語類のみ/先頭が閉じた語類の定着表現
LEGIT_IDIOMS = {"as well", "at all", "in fact", "of course", "so far", "as if", "as is", "in case", "at least", "at last", "by far", "so what",
                "so that", "as such", "in all", "on and on", "at once", "as for", "as to", "to date", "in short", "at first", "on time", "in time",
                "by the way", "in order to", "in front of", "on the other hand", "at the same time", "as long as", "as soon as", "in spite of",
                "on a regular basis", "on top of", "in a row", "at that point"}
ex_closed_all = [t for t in wk if 2 <= len(t.split()) <= 5 and all(x in U.CLOSED for x in t.split())]
sec3["dictionary_scan"] = {"wiktionary_titles_total": len(wk), "all_closed_class_titles_2to5words(U3(i)の理論上の影響範囲)": len(ex_closed_all),
                           "examples": sorted(ex_closed_all)[:60], "legit_idiom_whitelist_hits_in_closed_titles": sorted(t for t in ex_closed_all if t in LEGIT_IDIOMS),
                           "legit_whitelist_with_nonclosed_word_not_affected": sorted(t for t in LEGIT_IDIOMS if t in wk and t not in ex_closed_all)}
# 拡張した閉じた語類(all/well/up/out等を加える)を使うと誤除外が増えることの実測(U3(i)で拡張を採るべきでない根拠)
X_EXTRA = {"all", "well", "up", "out", "off", "down", "over", "back", "just", "only", "also", "too", "very", "more", "most", "much", "many",
           "few", "each", "every", "such", "other", "another", "after", "before", "again", "still", "even", "now", "far", "ever", "never", "always", "any", "some", "one", "course", "fact", "least", "once", "first", "last", "time", "case", "short", "date"}
X_EXTRA -= {"course", "fact", "least", "once", "first", "last", "time", "case", "short", "date"}  # 内容語は拡張に含めない
ex_closed_x = [t for t in wk if 2 <= len(t.split()) <= 5 and all(x in (U.CLOSED | X_EXTRA) for x in t.split())]
sec3["dictionary_scan"]["extended_set(all/well/up/out/...)_titles"] = len(ex_closed_x)
sec3["dictionary_scan"]["extended_legit_whitelist_hit"] = sorted(t for t in ex_closed_x if t in LEGIT_IDIOMS)
# extractor span (LLM抽出, 辞書外) への fragment_risk 注釈
import er064_kp_opt_01_upstream_prefetch_01 as PF  # noqa: E402
spans = PF.extractor_spans()
fl = []
for s in spans:
    reg = (s in wk) or snap.d["multiword"].get(s, {}).get("hit", False)
    fl.append({"span": s, "registered": bool(reg), "fragment_risk": U.fragment_risk(s, reg), "closed_only": U.all_closed_only(s)})
# 記事内に出現する「閉じた語類のみのDB見出し」(ゲート前)の件数: U3(i)の理論的な誤除外リスクの記事別実測
import re as _re
pres = {}
for key in U.ARTICLES:
    low = " ".join(" ".join(u["tokens"]).lower() for u in base(key)[0]["sentence_units"])
    toks = _re.findall(r"[a-z']+", low)
    ng = set()
    for n in range(2, 6):
        for i in range(len(toks) - n + 1):
            ng.add(" ".join(toks[i:i + n]))
    pres[key] = sorted(t for t in ex_closed_all if t in ng)
sec3["closed_only_db_titles_present_in_article_before_gate"] = pres
sec3["extractor_span_scan"] = {"unique_spans(2語以上)": len(spans), "flagged": [x["span"] for x in fl if x["fragment_risk"]],
                               "flagged_excluding_aux_starts(be/have/do/modal)": [x["span"] for x in fl if x["fragment_risk"] and x["span"].split()[0] not in {"is","are","was","were","be","been","being","do","does","did","has","have","had","can","could","may","might","must","should","will","would"}],
                               "registered_but_would_start_with_closed(注釈対象外)": [x["span"] for x in fl if x["registered"] and x["span"].split()[0] in U.FRAG_START]}
dump("u3_fragment_01.json", sec3)
print("U3 closed-only in articles:", {k: len(v["closed_only_excluded_by_U3i"]) for k, v in sec3["per_article"].items()})
print("done run_01")
