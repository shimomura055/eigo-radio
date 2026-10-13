# Round3 Stage0 表の機械生成 ¥0: b1供給品質表・Tier H削除・揺れ・目視精度ラベル集計、およびM2P0/M2P5(既存Round1/2 run)のCI付き要約。
# 出力: round3/stage0_analysis_r3.json, tierh_deletions_r3.json, report_tables_r3.md
import glob
import itertools
import json
import os
import random
import sys

sys.path.insert(0, os.getcwd())
OUT = "er064_output/kp_integrated_opt_01/round3"
R2 = "er064_output/kp_integrated_opt_01/round2"
NEG = ("N1", "D6", "D5", "R3")

# 目視精度ラベル(sonnet-worker暫定、Fable/ユーザーが覆してよい)。キー=(記事id, LLMの生span小文字)。
# 正=非透明/比喩/句動詞として抽出対象に妥当 / 誤=透明・基本表現の偽陽性 / 粒度不良=切り方が不適(断片・助動詞/副詞付き・主語欠落等)
LABELS = {
    ("R3", "sleep inertia"): "正", ("R3", "under way"): "正", ("R3", "gets the first word"): "誤",
    ("D6", "make up"): "正",
    ("coffee_adv", "your wallet pumps its fist"): "正", ("coffee_adv", "wallet pumps its fist"): "正",
    ("coffee_adv", "in the ring"): "粒度不良", ("coffee_adv", "unseen clock of its own"): "正",
    ("coffee_adv", "had been behind price increases"): "粒度不良", ("coffee_adv", "figures in the ring"): "正",
    ("coffee_std", "in the ring just yet"): "粒度不良", ("coffee_std", "your wallet pumps its fist"): "正", ("coffee_std", "wallet pumps its fist"): "正",
    ("coffee_std", "its own hidden clock"): "正", ("coffee_std", "numbers in the ring"): "正", ("coffee_std", "hidden clock"): "正",
    ("coffee_std", "in the ring"): "粒度不良", ("coffee_std", "own hidden clock"): "粒度不良",
    ("hormuz_adv", "gave back"): "正", ("hormuz_adv", "stood at center stage"): "正", ("hormuz_adv", "curtain rose"): "正",
    ("hormuz_std", "stood at center stage"): "正", ("hormuz_std", "gave back some gains"): "正", ("hormuz_std", "refuses to stay down"): "正",
    ("meta_adv", "behind the scenes"): "正", ("meta_adv", "a small twist"): "誤", ("meta_adv", "on the other end"): "粒度不良",
    ("meta_std", "in stock"): "誤", ("meta_std", "behind the scenes"): "正",
    ("semi_adv", "catches the eye"): "正", ("semi_adv", "skip over this"): "粒度不良", ("semi_adv", "fit for leading roles"): "正",
    ("semi_std", "take the seat"): "正", ("semi_std", "switch off quietly"): "粒度不良", ("semi_std", "your eyes feel heavy"): "粒度不良",
    ("smallbag_adv", "having a big moment"): "正", ("smallbag_adv", "carry the mood"): "正", ("smallbag_adv", "sits on the throne"): "正",
    ("smallbag_std", "having a big moment"): "正", ("smallbag_std", "on the throne"): "粒度不良", ("smallbag_std", "carry the mood"): "正",
}


def jacc(a, b):
    return len(a & b) / len(a | b) if a | b else 1.0


def load():
    recs = []
    for f in sorted(glob.glob(f"{OUT}/b1/*/run*.json")):
        recs.append(json.load(open(f, encoding="utf-8")))
    return recs


def stage0(recs):
    rows, labelled = [], {"正": 0, "誤": 0, "粒度不良": 0, "未ラベル": 0}
    nv_total = nv_bad = zero = 0
    th = {}
    for r in recs:
        b = r["built"]
        raw = b["raw_items"]
        lab = []
        for it in raw:
            l = LABELS.get((r["id"], it["span"].lower()), "未ラベル")
            labelled[l] += 1
            lab.append((it["span"], l))
        if not raw:
            zero += 1
        else:
            nv_total += len(raw)
            nv_bad += sum(1 for v in b["verbatim"] if not v["verbatim"])
        rows.append({"id": r["id"], "level": r["level"], "run": r["run"], "raw_n": b["raw_item_count"],
                     "verbatim_n": sum(1 for v in b["verbatim"] if v["verbatim"]), "accepted": [c["surface_form"] for c in b["accepted"]],
                     "accepted_ranks": [c["llm_rank"] for c in b["accepted"]],
                     "dup_removed": [d["span"] for d in b["duplicate_of_existing"]], "rejected": [(x.get("span"), x.get("reason")) for x in b["rejected"]],
                     "over_cap": b["over_cap"], "narrow_guard_hits": [h["span"] for h in b["narrow_guard_hits"]], "labels": lab,
                     "b1_reserved_final": r.get("b1_added_final"), "tier_h_deleted_existing": r.get("tier_h_deleted_existing"),
                     "tier_h_deleted_b1": r.get("tier_h_deleted_b1"), "cost_jpy": r["cost_jpy"], "reasoning_tokens": r["reasoning_tokens"],
                     "elapsed_sec": r["elapsed_sec"], "interpretation_ranks": [it["rank"] for it in raw]})
        if r["id"] not in NEG:
            th.setdefault(r["id"], []).append({"run": r["run"], "deleted_existing": r["tier_h_deleted_existing"], "deleted_b1": r["tier_h_deleted_b1"],
                                                "recompute_base_drop": r.get("tier_h_recompute_base")})
    jit = {}
    for key in ("coffee_std", "coffee_adv"):
        sets = [frozenset(x.lower() for x in rr["accepted"]) for rr in rows if rr["id"] == key]
        # dup(b2と重複した語句)も含めた「LLMが挙げた語句」集合(coreが同じなら同一視しにくいので生spanで)
        raws = [frozenset(l[0].lower() for l in rr["labels"]) for rr in rows if rr["id"] == key]
        pairs = list(itertools.combinations(sets, 2))
        pr = list(itertools.combinations(raws, 2))
        jit[key] = {"accepted_sets": [sorted(s) for s in sets], "jaccard_accepted_mean": round(sum(jacc(a, b) for a, b in pairs) / len(pairs), 3),
                    "jaccard_rawspan_mean": round(sum(jacc(a, b) for a, b in pr) / len(pr), 3)}
    pre_first = [rr for rr in rows if rr["run"] == 1 and rr["id"] not in NEG]
    tot_acc = sum(len(rr["accepted"]) for rr in rows if rr["id"] not in NEG)
    neg = {n: next(rr for rr in rows if rr["id"] == n) for n in NEG}
    res = {"rows": rows, "label_counts_raw_items": labelled,
           "label_precision_raw": round(labelled["正"] / max(sum(labelled.values()) - labelled["未ラベル"], 1), 3),
           "nonverbatim": {"outputs_in_calls_with_output": nv_total, "nonverbatim": nv_bad, "zero_output_calls": zero},
           "jitter": jit, "negative_controls": {n: {"raw_n": v["raw_n"], "accepted": v["accepted"], "dup": v["dup_removed"]} for n, v in neg.items()},
           "negative_accepted_mean_per_call": round(sum(len(v["accepted"]) for v in neg.values()) / 4, 2),
           "accepted_total_eval_calls": tot_acc, "cost_total": round(sum(r["cost_jpy"] for r in recs), 4),
           "cost_per_call_mean": round(sum(r["cost_jpy"] for r in recs) / len(recs), 4),
           "elapsed_mean": round(sum(r["elapsed_sec"] for r in recs) / len(recs), 1)}
    json.dump(res, open(f"{OUT}/stage0_analysis_r3.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"note": "追加後のcompute_containment(r2=True)再計算でTier Hにより削除された既存候補(記事x抽出run)。空配列=削除なし", "by_article": th,
               "total_deleted_existing": sum(len(x["deleted_existing"] or []) for v in th.values() for x in v),
               "total_deleted_b1": sum(len(x["deleted_b1"] or []) for v in th.values() for x in v)},
              open(f"{OUT}/tierh_deletions_r3.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return res


def boot(xs_std, xs_adv, B=5000, seed=3):
    rnd = random.Random(seed)
    def mean(xs):
        return sum(xs) / len(xs)
    out = []
    for _ in range(B):
        a = mean([rnd.choice(xs_std) for _ in xs_std]) if xs_std else 0
        b = mean([rnd.choice(xs_adv) for _ in xs_adv]) if xs_adv else 0
        out.append(a + b)
    out.sort()
    return round(out[int(0.025 * B)], 1), round(out[int(0.975 * B)], 1)


def existing_table():
    A = json.load(open(f"{R2}/analysis_r2.json", encoding="utf-8"))
    L = ["| 条件(既存run、b1なし) | Std score(n) | Adv score(n) | 合算 [95%CI] | pump Std/Adv | time lag Adv | 低優先枠/run Std/Adv | 全gate PASS | 費用/job | reasoning tok sel Std/Adv |", "|---|---|---|---|---|---|---|---|---|---|"]
    out = {}
    for c in ("M2P0", "M2P5"):
        s, a = A[f"coffee_std_{c}"], A[f"coffee_adv_{c}"]
        ss = [r["score"]["score"] for r in s["runs"] if r.get("score")]
        aa = [r["score"]["score"] for r in a["runs"] if r.get("score")]
        lo, hi = boot(ss, aa)
        tot = sum(ss) / len(ss) + sum(aa) / len(aa)
        out[c] = {"std_mean": sum(ss) / len(ss), "adv_mean": sum(aa) / len(aa), "total": tot, "ci": [lo, hi], "n_std": len(ss), "n_adv": len(aa)}
        L.append(f"| {c} | {sum(ss)/len(ss):.1f} (n={len(ss)}) | {sum(aa)/len(aa):.1f} (n={len(aa)}) | {tot:.1f} [{lo}, {hi}] | {s['adopt_full'].get('1',0)}/{s['n_valid']} , {a['adopt_full'].get('1',0)}/{a['n_valid']} | {a['adopt_full'].get('4',0)}/{a['n_valid']} | {s['low_slots_per_run']} / {a['low_slots_per_run']} | {s['all_gate_pass']}/{s['n']} , {a['all_gate_pass']}/{a['n']} | {s['cost_mean']} / {a['cost_mean']} | {s['reasoning_tokens_sel_mean']} / {a['reasoning_tokens_sel_mean']} |")
    json.dump(out, open(f"{OUT}/existing_summary_r3.json", "w", encoding="utf-8"), indent=1)
    return L


def md(res):
    L = ["# report_tables_r3 (自動生成。Stage 0 b1供給品質。Stage 1は事前登録Go条件不成立のため未実施)", "", "## b1供給品質(抽出run単位)",
         "| 記事 | run | LLM生件数 | 逐語 | b2等との重複除外 | reject | accepted(rank順) | b1予約(Tier H後) | Tier H削除(既存) | 縮約ガード発動 | 費用 | reasoning tok | 秒 |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in res["rows"]:
        L.append(f"| {r['id']} | {r['run']} | {r['raw_n']} | {r['verbatim_n']}/{r['raw_n']} | {r['dup_removed']} | {r['rejected']} | {r['accepted']} | {r['b1_reserved_final']} | {r['tier_h_deleted_existing']} | {r['narrow_guard_hits']} | {r['cost_jpy']} | {r['reasoning_tokens']} | {r['elapsed_sec']} |")
    L += ["", "## 目視精度ラベル(LLM生span単位、暫定)", f"{res['label_counts_raw_items']} 精度(正/ラベル済)={res['label_precision_raw']}", ""]
    for r in res["rows"]:
        L.append(f"- {r['id']} run{r['run']}: " + " / ".join(f"{s}={l}" for s, l in r["labels"]))
    L += ["", "## 揺れ(Coffee)", json.dumps(res["jitter"], ensure_ascii=False, indent=1), "", "## 陰性対照", json.dumps(res["negative_controls"], ensure_ascii=False), f"accepted平均/呼出={res['negative_accepted_mean_per_call']}",
          "", "## 既存run(Round1/2)のCI付き要約(b1なし)"] + existing_table()
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    res = stage0(load())
    open(f"{OUT}/report_tables_r3.md", "w", encoding="utf-8").write(md(res))
    print(json.dumps({k: res[k] for k in ("label_counts_raw_items", "label_precision_raw", "nonverbatim", "jitter", "negative_accepted_mean_per_call", "cost_total", "cost_per_call_mean", "elapsed_mean")}, ensure_ascii=False, indent=1))
