# KP-OPT-01 委任_02 (Phase 1修正): 固定shortlistの再固定(実タイトル・共通builder・注釈ラベル統一)、C0のProduction実runとのバイト一致確認、
# R1(閉じた語類終わりhitのimportant判定を外すガード)のオフライン集計。Trial専用・Production非接続・有料呼出なし・Wiktionaryはsnapshot再生のみ。
import json
import os
import sys

sys.path.insert(0, os.getcwd())
import er064_kp_opt_01_upstream_core as U  # noqa: E402
import er030_key_phrase_db_hybrid_selector_01 as sel  # noqa: E402

core = U.core
OUT = "er064_output/kp_extraction_selection_opt_01/phase1_fix"
os.makedirs(OUT, exist_ok=True)
snap = U.Snapshot()
dbs = core.load_group1_dbs()

_W = "er019_output/family_x_audio_production_wiring_01"
PROD_PROMPT = {  # Production実runの選定Prompt(候補行を含む)
    "coffee_std": _W + "/coffee_prices__run_v5_ms_01/a2/key_phrases/key_phrases_db_hybrid/keywords_selector_prompt.txt",
    "coffee_adv": _W + "/coffee_prices__run_v5_ms_01/b1b/key_phrases/key_phrases_db_hybrid/keywords_selector_prompt.txt",
    "meta_std": _W + "/meta__run_03/a2/key_phrases/key_phrases_db_hybrid/keywords_selector_prompt.txt",
    "meta_adv": _W + "/meta__run_03/b1b/key_phrases/key_phrases_db_hybrid/keywords_selector_prompt.txt",
    "hormuz_std": _W + "/family_x_b3_diversity_trial_01/hormuz__run_02/a2/key_phrases/keywords_selector_prompt.txt",
    "hormuz_adv": _W + "/family_x_b3_diversity_trial_01/hormuz__run_02/b1b/key_phrases/keywords_selector_prompt.txt",
}


def real_title(key):
    first = U.read_article(key).lstrip().splitlines()[0]
    return first.lstrip("#").strip()


def cand_block(prompt_text):
    return prompt_text[prompt_text.index("【Topic】title:"):prompt_text.index("【選定方針】")]


STAGE1 = {}


def base(key):
    if key not in STAGE1:
        st = core.run_stage1_for_article(U.read_article(key), dbs)
        STAGE1[key] = (st, U.pool_for_article(st)[0])
    return STAGE1[key]


net_misses = []


def replay(key, mode, k, budget):
    st0, pool = base(key)
    rare = [c["canonical_form"] for c in st0["word_survivors"]]
    fn = U.make_order_fn(mode, rare, k=k)
    try:
        with U.patched(fn, snap, allow_net_mw=False, allow_net_uni=False):
            return core.run_stage1_and_shortlist(U.read_article(key), dbs, real_title(key), wiktionary_multiword_lookup_budget=budget)
    except RuntimeError as e:  # 実タイトルでrare単語の選定が変わりsnapshotに無い単語が出た場合のみ、無料のWiktionary照会を許可して記録
        net_misses.append({"key": key, "error": str(e)[:200]})
        with U.patched(fn, snap, allow_net_mw=False, allow_net_uni=True):
            return core.run_stage1_and_shortlist(U.read_article(key), dbs, real_title(key), wiktionary_multiword_lookup_budget=budget)


def mw_survivors(stage1):
    out = {}
    for c in stage1["important_noun_candidates"]:
        if c.get("db_categories") == ["multiword_term"] and c.get("matched_dbs") == ["wiktionary"]:
            out[c["canonical_form"]] = "important"
    for c in stage1["phrase_survivors"]:
        if c.get("db_categories") == ["multiword_term"] and c.get("matched_dbs") == ["wiktionary"]:
            out[c["canonical_form"]] = "demoted"
    return out


EXPAND = ("default", 10, None)
CONFIGS = {  # name -> (source, assemble kwargs)
    "current": (("default", 10, 60), {}),
    "improved": (EXPAND, dict(u2="tierH+S", u3_exclude=True, u3_annotate=True, phrase_cap=20, realign=True, r2=True, r3=True)),
    "alt_precision_guarded": (EXPAND, dict(guard=True, u2="tierH+S", u3_exclude=True, u3_annotate=True, phrase_cap=20, realign=True, r2=True, r3=True)),
    "alt_precision_guarded_r1": (EXPAND, dict(guard=True, r1_guard=True, u2="tierH+S", u3_exclude=True, u3_annotate=True, phrase_cap=20, realign=True, r2=True, r3=True)),
}
P2 = ["coffee_std", "coffee_adv", "meta_std", "meta_adv", "hormuz_std", "hormuz_adv"]

fixed = {"purpose": "KP-OPT-01 委任_02 再固定shortlist。全条件を同一builder(candidate_row_text, 実タイトル, 注釈ラベルはU.LABEL_*)で組立。"
                    "current=Production現行構成の再生(注釈なし) / improved=拡大+U2(H+S,R2)+U3(R3)+U4c(Phase 2では使わない) / "
                    "alt_precision_guarded=improved+窓外demoted hit除外 / alt_precision_guarded_r1=guarded+R1(閉じた語類終わりhitのimportant判定除去)",
         "snapshot": "../phase1_a/wiktionary_snapshot_01.json", "snapshot_sha256": U.sha256_file(U.SNAPSHOT_PATH),
         "label_constants": {"contains": U.LABEL_CONTAINS, "contained_in": U.LABEL_CONTAINED, "fragment_risk": U.LABEL_FRAGMENT},
         "phase2_target_articles": P2, "articles": {}}
metrics = {}
c0_match = {}
sec_r1 = {"per_article": {}}
for key in U.ARTICLES:
    title = real_title(key)
    st0, pool = base(key)
    n2 = sum(1 for p in pool if len(p.split()) == 2)
    cache = {}
    ent = {"article_path": U.ARTICLES[key], "article_sha256": U.sha256_text(U.read_article(key)), "title": title}
    cur_survivors = None
    cur_words = None
    cur_list = None
    cur_tok = 0
    mrow = {}
    for name, (src, kw0) in CONFIGS.items():
        mode, k, b = src
        b = b if b is not None else n2 + U.THREEGRAM_CAP
        if (mode, k, b) not in cache:
            cache[(mode, k, b)] = replay(key, mode, k, b)
        res = cache[(mode, k, b)]
        kw = dict(kw0)
        if kw.pop("guard", False):
            kw["demoted_allow"] = cur_survivors
        out = U.assemble_shortlist(res["stage1"], dbs=dbs, **kw)
        sl = out["shortlist"]
        rows = U.candidate_row_text(sl, out["sentence_reference"], with_annotations=True, pairs=out["containment_pairs"], title=title)
        cl = [c["canonical_form"] for c in sl]
        if name == "current":
            cur_survivors = set(mw_survivors(res["stage1"]))
            cur_list = cl
            cur_words = {c["canonical_form"] for c in sl if c["unit_type"] == "word"}
            cur_tok = U.approx_tokens(rows)
        words = {c["canonical_form"] for c in sl if c["unit_type"] == "word"}
        ent[name] = {"rows_text": rows, "rows_text_sha256": U.sha256_text(rows), "sentence_reference": out["sentence_reference"],
                     "candidates": [{"surface_form": c["surface_form"], "canonical_form": c["canonical_form"], "unit_type": c["unit_type"],
                                     "important_noun_phrase_candidate": bool(c.get("important_noun_phrase_candidate")),
                                     "evidence": sel._compact_evidence_string(c), "fragment_risk": bool(c.get("fragment_risk"))} for c in sl],
                     "containment_pairs": out["containment_pairs"]}
        mrow[name] = {"total": len(sl), "tokens_approx": U.approx_tokens(rows), "token_delta_vs_current": U.approx_tokens(rows) - cur_tok,
                      "words_pushed_out_vs_current": sorted(cur_words - words - set(out["u2_removed_tier_h"])),  # U2 Tier-Hによる意図的除去(lag等)は押し出しに数えない
                      "words_removed_by_u2_tierH": sorted(out["u2_removed_tier_h"]), "added_vs_current": [c for c in cl if c not in cur_list],
                      "removed_vs_current": [c for c in cur_list if c not in cl], "u2_removed_tier_h": out["u2_removed_tier_h"],
                      "tierH_pairs": [(p["small"], p["big"]) for p in out["containment_pairs"] if p["tier"] == "H"],
                      "tierS_pairs": [(p["small"], p["big"]) for p in out["containment_pairs"] if p["tier"] == "S"],
                      "fragment_risk": [c["canonical_form"] for c in sl if c.get("fragment_risk")],
                      "r1_moved_from_important": out["r1_moved_from_important"],
                      "annotation_in_rows": any(x in rows for x in (U.LABEL_CONTAINS, U.LABEL_CONTAINED, U.LABEL_FRAGMENT)),
                      "shortlist": cl, "important_in_shortlist": [c["canonical_form"] for c in sl if c.get("important_noun_phrase_candidate")]}
    fixed["articles"][key] = ent
    metrics[key] = mrow
    if key in PROD_PROMPT:  # C0バイト一致(Production実run)
        p = open(PROD_PROMPT[key], encoding="utf8").read()
        if "【Topic】title:" not in p:  # hormuz run_02のProduction選定Promptは候補一覧方式導入前(旧方式)で、比較対象の候補行が存在しない
            c0_match[key] = {"production_prompt": PROD_PROMPT[key], "byte_identical": None,
                             "note": "Production実runのPromptに候補一覧(【Topic】)が無い(候補一覧方式導入前の旧方式)。バイト一致は判定不能"}
        else:
            pb = cand_block(p)
            ob = cand_block(ent["current"]["rows_text"])
            same = pb == ob
            info = {"production_prompt": PROD_PROMPT[key], "byte_identical": same, "prod_len": len(pb), "ours_len": len(ob)}
            if not same:
                pl, ol = pb.splitlines(), ob.splitlines()
                info["only_in_production"] = [x for x in pl if x not in ol][:12]
                info["only_in_ours"] = [x for x in ol if x not in pl][:12]
            c0_match[key] = info
    g, r1 = mrow["alt_precision_guarded"], mrow["alt_precision_guarded_r1"]
    sec_r1["per_article"][key] = {"guarded_words_pushed_out": g["words_pushed_out_vs_current"], "guarded_r1_words_pushed_out": r1["words_pushed_out_vs_current"],
                                  "r1_moved_from_important": r1["r1_moved_from_important"],
                                  "in_guarded_shortlist_but_not_in_r1": [c for c in g["shortlist"] if c not in r1["shortlist"]],
                                  "in_r1_but_not_guarded": [c for c in r1["shortlist"] if c not in g["shortlist"]],
                                  "guarded_total": g["total"], "r1_total": r1["total"]}
    print(key, {n: (v["total"], len(v["words_pushed_out_vs_current"])) for n, v in mrow.items()}, flush=True)

sec_r1["totals_words_pushed_out"] = {n: sum(len(m[n]["words_pushed_out_vs_current"]) for m in metrics.values()) for n in CONFIGS}
sec_r1["r1_moved_from_important_all"] = sorted({c for v in sec_r1["per_article"].values() for c in v["r1_moved_from_important"]})
sec_r1["multiword_important_kept_in_r1_shortlists"] = sorted({c for m in metrics.values() for c in m["alt_precision_guarded_r1"]["important_in_shortlist"] if len(c.split()) >= 2})
sec_r1["tokens_mean_delta_vs_current"] = {n: round(sum(m[n]["token_delta_vs_current"] for m in metrics.values()) / len(metrics), 1) for n in CONFIGS}
sec_r1["shortlist_mean_total"] = {n: round(sum(m[n]["total"] for m in metrics.values()) / len(metrics), 1) for n in CONFIGS}
body = json.dumps(fixed, ensure_ascii=False, indent=1, sort_keys=True)
open(f"{OUT}/shortlists_fixed_02.json", "w", encoding="utf8", newline="\n").write(body)
open(f"{OUT}/shortlists_fixed_02.sha256.txt", "w", encoding="utf8", newline="\n").write(U.sha256_file(f"{OUT}/shortlists_fixed_02.json") + "  shortlists_fixed_02.json\n")
json.dump(c0_match, open(f"{OUT}/c0_byte_match_02.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
json.dump({"r1": sec_r1, "per_article_metrics": metrics, "network_misses_fallback": net_misses}, open(f"{OUT}/r1_and_metrics_02.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
print("C0 byte match:", {k: v["byte_identical"] for k, v in c0_match.items()})
print("R1 totals:", sec_r1["totals_words_pushed_out"], sec_r1["r1_moved_from_important_all"])
print("net misses:", net_misses)
