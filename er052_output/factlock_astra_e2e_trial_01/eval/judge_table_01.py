# -*- coding: utf-8 -*-
"""FACTLOCK-ASTRA-E2E-TRIAL-01 委任_15: 事前登録の判定線への機械照合表を作る(API呼出なし)。

入力: runs/final_aggregate/aggregate_final.json、runs/<theme>/<arm>/ の成果物の有無、eval/labels_merged.jsonl
出力: eval/judge_table_01.json(数値と機械判定)。EVAL_E2E_01.md 2節はこの出力を転記する。
機械判定=事前登録(PREREGISTRATION_01.md 2節、n=9・予定run各腕18に読み替え)の線への機械的当てはめのみ。
Fable最終判定はここでは書かない(空欄)。ラベルはSonnet暫定推測であり、確定値ではない。

注意(集計scriptとの食い違い、EVAL 3-4節):
 - aggregate_final.json の旧腕『EN advanced STOP』は、旧腕で Standard が STOP した記事(small_bag, byd_recall)を
   Advanced の欄に入れている。ここでは成果物(b1b/article.md=Advanced本文、a2/article.md=Standard本文)の有無から
   STOPのレベルを決め直す。
 - aggregate_final.json の『M1発火』はStandard側が『attempt2ファイルの存在』=must-fix再生成であり、M1ではない
   (REPORT §110: M1はAdvanced枝のみ)。ここでは runログの [OPEN243_M1] 文字列で数え直す。
"""
import json
import math
import os
import glob
import re

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
RUNS = os.path.join(ROOT, "runs")
THEMES_OLD4 = ["meta", "hormuz", "space_weapons", "small_bag"]
THEMES_NEW5 = ["byd_recall", "central_bank_mortgage", "openai_copyright", "semiconductor_earnings", "streaming_price"]
THEMES = THEMES_OLD4 + THEMES_NEW5
N = 9
PLANNED = 18  # 腕あたり予定run(9テーマ x Adv/Std)

# ---- 最終本文に残る軽微(判定線2-2)。worker が『最終(出荷)本文の残存』として列挙した項目の手写し。
# (theme, arm, 列, 項目数, 根拠row_id, 内容)。列: JA / EN-Adv / EN-Std。JA由来のEN持ち越しはJA列のみ(事前登録2-2 v2)。
# 同一箇所の断片重複・同型の複数箇所(例: 不在断定の4箇所)は1項目にまとめる(claim単位)。row_idは labels_merged.jsonl の row_id。
FINAL_MINOR_ITEMS = [
    ("meta", "new", "EN-Std", 1, "w1-84", "Std『mistake to start a test』条件省略(次文で復元)"),
    ("hormuz", "new", "EN-Std", 2, "w1-104,w1-105", "『quite an impact』修辞/『should not say the 20% plan pushed prices up』過度の否定(w1-114は後者の断片重複)"),
    ("space_weapons", "new", "JA", 1, "w1-49", "不在・秘匿の断定(『性能表は伏せたまま』等、境界B-02)"),
    ("space_weapons", "new", "EN-Adv", 1, "w1-77", "Rewrite後も『missiles』複数形が残存(translation)"),
    ("space_weapons", "old", "JA", 1, "w1-62", "『装置の名前も…明らかにされていません』不在・非公開の断定(境界B-03)"),
    ("space_weapons", "old", "EN-Adv", 1, "w1-72", "『U.S. forces』(統合軍→米軍の一般化の継承、translation)"),
    ("space_weapons", "old", "EN-Std", 1, "w1-74", "『first public statement』『初めて』の対象ずれ(translation)"),
    ("small_bag", "old", "JA", 3, "w2-97", "『ランウェイならでは』排他/記事+ランウェイ一般化/『調べた結果ではない』"),
    ("byd_recall", "new", "JA", 2, "w2-195", "見出し冒頭の無留保な現象描写(境界B-05)/『実況を続けてしまう状態』"),
    ("byd_recall", "new", "EN-Adv", 2, "w2-196", "要約『極端な場合』条件欠落/『A recall notice…named』単数(低確信)"),
    ("byd_recall", "old", "JA", 3, "w2-198", "交換の因果付与/『ことがあります』(低確信)/公告単数(低確信)"),
    ("byd_recall", "old", "EN-Adv", 1, "w2-199", "要約の条件・中国限定の欠落"),
    # v2(委任_16、Opusレビュー論点2): openai新 w3-40(見出し『AI訴訟は…』の一般化)は記事がEN Adv STOPで未出荷の本文のため、
    # 『出荷最終本文の残存』から除外(旧v1では新JA列に1件計上されていた)。除外した記録は EXCLUDED_UNSHIPPED に残す。
    ("openai_copyright", "old", "EN-Std", 1, "w3-38", "見出し『They Want AI Models Destroyed』の限定脱落(JA見出しには無い=EN段)"),
    ("semiconductor_earnings", "old", "JA", 1, "w3-56", "免責の範囲拡張(低確信)"),
    ("semiconductor_earnings", "old", "EN-Std", 1, "w3-83", "Checker Rewrite起因: 限定句『not the whole semiconductor segment』が消えた"),
    ("streaming_price", "old", "JA", 1, "w3-98", "新規契約者9/23の時制(未来形、低確信、境界B-11)"),
    ("streaming_price", "old", "EN-Adv", 1, "w3-116", "年額がPremiumと明記されない(低確信)"),
    ("streaming_price", "old", "EN-Std", 1, "w3-117", "Checker Rewrite起因: Premium月額差額の文が消えた"),
    ("streaming_price", "new", "JA", 1, "w3-121", "見出しの米国限定欠落"),
    ("streaming_price", "new", "EN-Std", 2, "w3-139", "『a different day for each person』過一般化/『The price list tells you how much you will pay』第三者請求の例外脱落"),
]


EXCLUDED_UNSHIPPED = [
    ("openai_copyright", "new", "JA", 1, "w3-40", "見出し『AI訴訟は…』の一般化(記事はEN Adv STOPで未出荷。v1では計上、v2で除外)"),
]


def exists(*p):
    return os.path.exists(os.path.join(RUNS, *p))


def runlog_m1_fired(theme, arm):
    n = 0
    for f in glob.glob(os.path.join(RUNS, theme, arm, "logs", "*.log")):
        with open(f, encoding="utf-8", errors="replace") as fh:
            n += fh.read().count("[OPEN243_M1]")
    return n


def reach(theme, arm):
    ja = exists(theme, arm, "ja_writer", "revision2.md")
    adv = exists(theme, arm, "b1b", "article.md")
    std = exists(theme, arm, "a2", "article.md")
    adv_attempted = exists(theme, arm, "b1b", "audit") and ja
    std_attempted = exists(theme, arm, "a2", "audit") and ja
    return {"ja": ja, "adv": adv, "std": std, "adv_attempted": adv_attempted, "std_attempted": std_attempted}


def binom_tail(k, n, p=0.5):
    return sum(math.comb(n, i) * p**i * (1 - p) ** (n - i) for i in range(k, n + 1))


def load_pt():
    d = json.load(open(os.path.join(RUNS, "final_aggregate", "aggregate_final.json"), encoding="utf-8"))
    pt = {}
    for x in d["aggregate_all"]["per_theme"]:
        pt[(x["theme"], x["arm"])] = x
    return d, pt


def main():
    d, pt = load_pt()
    out = {"n_themes": N, "planned_runs_per_arm": PLANNED}

    # ---------- 到達・STOP(成果物から決め直し)
    R = {}
    for t in THEMES:
        for a in ("new", "old"):
            r = reach(t, a)
            x = pt[(t, a)]
            ja_stop = bool(x.get("ja_stop")) or (not r["ja"])
            # EN STOP: JA完走 かつ AdvまたはStd本文が無い。Advが無ければAdv STOP(Stdは未到達)。Advがあって
            # Std本文が無く Std を試行(auditあり)していれば Std STOP。
            en_adv_stop = r["ja"] and not r["adv"]
            en_std_stop = r["ja"] and r["adv"] and (not r["std"]) and r["std_attempted"]
            R[(t, a)] = {**r, "ja_stop": ja_stop, "en_adv_stop": en_adv_stop, "en_std_stop": en_std_stop,
                         "first_ja_recheck": bool(x.get("first_ja_recheck")),
                         "b1": x.get("b1_recovery", 0),
                         "rewrite_runs": sum(1 for lv in ("advanced", "standard")
                                             if x["checker"].get(lv, {}).get("rewrite")),
                         "human_review_runs": sum(1 for lv in ("advanced", "standard")
                                                  if x["checker"].get(lv, {}).get("human_review")),
                         "checker_adv": x["checker"].get("advanced", {}).get("final_state"),
                         "checker_std": x["checker"].get("standard", {}).get("final_state"),
                         "en_adv_major": x["en"]["advanced"].get("n_major", 0), "en_adv_tr": x["en"]["advanced"].get("n_translation", 0),
                         "en_adv_js": x["en"]["advanced"].get("n_ja_source", 0),
                         "en_std_major": x["en"]["standard"].get("n_major", 0), "en_std_tr": x["en"]["standard"].get("n_translation", 0),
                         "en_std_js": x["en"]["standard"].get("n_ja_source", 0),
                         "ja_fc_major": (x["ja_fc"] or {}).get("n_major"), "ii": x.get("ii_new_specific_final"),
                         "ii_delta": x.get("ii_delta_vs_r0"),
                         "m1_logged": runlog_m1_fired(t, a)}
    out["reach"] = {f"{t}/{a}": v for (t, a), v in R.items()}

    def arm_sum(a, key):
        return sum(1 for t in THEMES if R[(t, a)][key])

    stop = {}
    for a in ("new", "old"):
        stop[a] = {"ja_stop_articles": arm_sum(a, "ja_stop"),
                   "en_adv_stop": arm_sum(a, "en_adv_stop"), "en_std_stop": arm_sum(a, "en_std_stop"),
                   "adv_shipped": arm_sum(a, "adv"), "std_shipped": arm_sum(a, "std")}
    out["stop"] = stop
    # aggregate_final.json の帰属との比較(食い違いの記録)
    agg_all = d["aggregate_all"]["arms"]
    out["aggregate_json_attribution"] = {
        a: {"en_adv_stop": agg_all[a]["H_en"]["advanced"]["stop"], "en_std_stop": agg_all[a]["H_en"]["standard"]["stop"],
            "m1_fired_adv": agg_all[a]["H_en"]["advanced"]["m1_fired"], "m1_fired_std": agg_all[a]["H_en"]["standard"]["m1_fired"]}
        for a in ("new", "old")}
    out["m1_logged_by_runlog"] = {a: sum(R[(t, a)]["m1_logged"] for t in THEMES) for a in ("new", "old")}
    out["m1_logged_themes"] = [f"{t}/{a}" for t in THEMES for a in ("new", "old") if R[(t, a)]["m1_logged"]]

    # ---------- 人手介入必要率(集計scriptと同じ定義: JA STOP=2 run、EN STOP=1 run、影STOP=2、Human Review=1)
    hi = {}
    per_theme_hi = {}
    for a in ("new", "old"):
        tot = 0
        for t in THEMES:
            r = R[(t, a)]
            v = (2 if r["ja_stop"] else 0) + (1 if r["en_adv_stop"] else 0) + (1 if r["en_std_stop"] else 0) + r["human_review_runs"]
            per_theme_hi[(t, a)] = v
            tot += v
        hi[a] = {"events": tot, "rate": round(tot / PLANNED, 3)}
    # 感度: Advanced STOPでStandardが未到達になる分も1 run加算した場合
    hi_sens = {}
    for a in ("new", "old"):
        tot = 0
        for t in THEMES:
            r = R[(t, a)]
            v = per_theme_hi[(t, a)] + (1 if (r["en_adv_stop"]) else 0)
            tot += v
        hi_sens[a] = {"events": tot, "rate": round(tot / PLANNED, 3)}
    out["human_intervention"] = {"main": hi, "sensitivity_adv_stop_kills_std": hi_sens,
                                 "per_theme_new_vs_old": {t: [per_theme_hi[(t, "new")], per_theme_hi[(t, "old")]] for t in THEMES}}
    for stratum, th in (("old4", THEMES_OLD4), ("new5", THEMES_NEW5)):
        s = {a: sum(per_theme_hi[(t, a)] for t in th) for a in ("new", "old")}
        out["human_intervention"][stratum] = {"events": s, "rate": {a: round(s[a] / (len(th) * 2), 3) for a in s}}

    # ---------- Rewrite率
    rw = {a: sum(R[(t, a)]["rewrite_runs"] for t in THEMES) for a in ("new", "old")}
    out["rewrite"] = {"runs": rw, "rate": {a: round(rw[a] / PLANNED, 3) for a in rw},
                      "per_theme_new_vs_old": {t: [R[(t, "new")]["rewrite_runs"], R[(t, "old")]["rewrite_runs"]] for t in THEMES},
                      "checker_runs_done": {a: sum(1 for t in THEMES for lv in ("checker_adv", "checker_std") if R[(t, a)][lv] not in (None, "-")) for a in ("new", "old")}}
    hr = {a: sum(R[(t, a)]["human_review_runs"] for t in THEMES) for a in ("new", "old")}
    out["human_review"] = {"runs": hr}

    # ---------- EN STOP率・EN初回MAJOR(レベル別)
    en = {}
    for lv, stopkey, majk, trk, jsk in (("Adv", "en_adv_stop", "en_adv_major", "en_adv_tr", "en_adv_js"),
                                      ("Std", "en_std_stop", "en_std_major", "en_std_tr", "en_std_js")):
        en[lv] = {}
        for a in ("new", "old"):
            en[lv][a] = {"stop_articles": arm_sum(a, stopkey), "stop_rate": round(arm_sum(a, stopkey) / N, 3),
                         "initial_major": sum(R[(t, a)][majk] or 0 for t in THEMES),
                         "translation_major": sum(R[(t, a)][trk] or 0 for t in THEMES),
                         "ja_source_major": sum(R[(t, a)][jsk] or 0 for t in THEMES),
                         "translation_major_per_article": round(sum(R[(t, a)][trk] or 0 for t in THEMES) / N, 3)}
    out["en"] = en

    # ---------- 軽微(2-2)
    cols = ["JA", "EN-Adv", "EN-Std"]
    item = {}
    for t, a, c, n, rid, desc in FINAL_MINOR_ITEMS:
        item[(t, a, c)] = item.get((t, a, c), 0) + n
    out["final_minor_items_total"] = {f"{c}/{a}": sum(v for (t, aa, cc), v in item.items() if aa == a and cc == c)
                                      for c in cols for a in ("new", "old")}

    def body_ok(t, a, col):
        r = R[(t, a)]
        return {"JA": r["ja"], "EN-Adv": r["adv"], "EN-Std": r["std"]}[col]

    mn = {}
    for col in cols:
        pairs = [(t, item.get((t, "new", col), 0), item.get((t, "old", col), 0)) for t in THEMES
                 if body_ok(t, "new", col) and body_ok(t, "old", col)]
        nb = {a: sum(1 for t in THEMES if body_ok(t, a, col)) for a in ("new", "old")}
        tot = {a: sum(item.get((t, a, col), 0) for t in THEMES if body_ok(t, a, col)) for a in ("new", "old")}
        pn = sum(p[1] for p in pairs)
        po = sum(p[2] for p in pairs)
        nf = sum(1 for p in pairs if p[1] < p[2])
        no = sum(1 for p in pairs if p[1] > p[2])
        ties = sum(1 for p in pairs if p[1] == p[2])
        mean_new = pn / len(pairs) if pairs else None
        mean_old = po / len(pairs) if pairs else None
        # 判定
        total_pair = pn + po
        if total_pair <= 5:
            v = "判定不能(床効果: 対応のある対の総件数5以下)"
        else:
            dec = nf + no
            good = mean_new <= mean_old * 0.75 and nf > dec / 2 and nf >= 6
            bad = mean_new >= mean_old * 1.25 and no >= 6
            v = "良化" if good else ("悪化" if bad else "同等")
        mn[col] = {"bodies_shipped": nb, "items_all_shipped": tot, "paired_n": len(pairs), "paired_new": pn, "paired_old": po,
                   "mean_new": None if mean_new is None else round(mean_new, 2),
                   "mean_old": None if mean_old is None else round(mean_old, 2),
                   "new_fewer_pairs": nf, "new_more_pairs": no, "ties": ties,
                   "pairs": {p[0]: [p[1], p[2]] for p in pairs}, "machine_verdict": v,
                   "sign_test_p_one_sided_new_fewer": None if (nf + no) == 0 else round(binom_tail(nf, nf + no), 3)}
    # EN列(Adv+Std合算)
    pairs_en = []
    for col in ("EN-Adv", "EN-Std"):
        for t in THEMES:
            if body_ok(t, "new", col) and body_ok(t, "old", col):
                pairs_en.append((t, col, item.get((t, "new", col), 0), item.get((t, "old", col), 0)))
    pn = sum(p[2] for p in pairs_en); po = sum(p[3] for p in pairs_en)
    nf = sum(1 for p in pairs_en if p[2] < p[3]); no = sum(1 for p in pairs_en if p[2] > p[3])
    mn["EN(Adv+Std合算)"] = {"paired_n": len(pairs_en), "paired_new": pn, "paired_old": po,
                            "new_fewer_pairs": nf, "new_more_pairs": no,
                            "ties": sum(1 for p in pairs_en if p[2] == p[3]),
                            "machine_verdict": "判定不能(床効果)" if pn + po <= 5 else
                            ("良化" if (pn / len(pairs_en)) <= 0.75 * (po / len(pairs_en)) and nf > (nf + no) / 2 and nf >= 6
                             else ("悪化" if (pn / len(pairs_en)) >= 1.25 * (po / len(pairs_en)) and no >= 6 else "同等"))}
    out["minor_2_2"] = mn
    out["final_minor_item_table"] = [dict(zip(["theme", "arm", "col", "n", "row_ids", "desc"], x)) for x in FINAL_MINOR_ITEMS]

    # ---------- 重大(2-1): labels_merged から
    rows = [json.loads(l) for l in open(os.path.join(BASE, "labels_merged.jsonl"), encoding="utf-8")]
    major_rows = [r for r in rows if r["n_sev"] == "重大"]
    out["severe_rows"] = [{"row_id": r["row_id"], "theme": r["theme"], "arm": r["arm"], "body": r["n_body"],
                           "shipped": r["n_shipped"], "boundary": r["n_boundary"], "claim": r["claim_text"][:90]}
                          for r in major_rows]
    out["severe_in_shipped_final_bodies"] = {"new": 0, "old": 0,
                                              "note": "3 workerとも出荷(採用)された最終本文の重大は0。重大ラベルはmeta/oldのrejected本文(STOPで阻止)の境界1件(行w1-11)と同STOP妥当性行(w1-14)のみ"}

    # ---------- (ii) とJA FC
    out["ja_fc_ii"] = {a: {"fc_major_r2": sum(R[(t, a)]["ja_fc_major"] or 0 for t in THEMES),
                           "ii_final": sum(R[(t, a)]["ii"] or 0 for t in THEMES if R[(t, a)]["ii"] is not None),
                           "ii_delta_vs_r0": sum(R[(t, a)]["ii_delta"] or 0 for t in THEMES if R[(t, a)]["ii_delta"] is not None),
                           "ja_done_articles": sum(1 for t in THEMES if R[(t, a)]["ja"])} for a in ("new", "old")}
    # (ii)検出に付いたラベル(dup除外)
    ii_rows = [r for r in rows if r["dup_primary"] and (r["orig"].get("kind") == "ii" or
               (r["worker"] == 3 and re.search(r"(^|[^a-z])ii", str(r["orig"].get("stage", "")))))]
    lab = {}
    for r in ii_rows:
        k = (r["arm"], r["n_sev"])
        lab[f"{r['arm']}/{r['n_sev']}"] = lab.get(f"{r['arm']}/{r['n_sev']}", 0) + 1
    out["ii_label_rows_unique"] = lab

    # ---------- 初回JA_RECHECK・B1・費用
    out["first_ja_recheck"] = {a: sum(1 for t in THEMES if R[(t, a)]["first_ja_recheck"]) for a in ("new", "old")}
    out["b1"] = {"fired": d["aggregate_all"]["arms"]["new"]["N_shadow_stop_b1"]["b1_recoveries"],
                 "denied": d["aggregate_all"]["arms"]["new"]["N_shadow_stop_b1"]["b1_denied"],
                 "cost_raw_est": d["cost"]["b1_estimated"]["raw"]}
    cost = d["cost"]
    out["cost"] = {"ledger_total": cost["total"], "astra": cost["astra"], "b1_est": cost["b1_estimated"]}
    # テーマ別費用(raw)
    th_cost = {}
    for t in THEMES:
        for a in ("new", "old"):
            th_cost[f"{t}/{a}"] = None
    out["note"] = "費用のテーマ/腕別は AGGREGATE.md 7節を参照(本scriptでは再計算しない)"

    # ---------- 符号検定(テーマ単位の対)
    def sign(pairs):
        nf = sum(1 for n_, o_ in pairs if n_ < o_)
        no = sum(1 for n_, o_ in pairs if n_ > o_)
        return {"new_better": nf, "old_better": no, "ties": len(pairs) - nf - no,
                "p_one_sided_new_better": None if nf + no == 0 else round(binom_tail(nf, nf + no), 3)}
    out["sign_tests"] = {
        "人手介入(件/テーマ)": sign([(per_theme_hi[(t, "new")], per_theme_hi[(t, "old")]) for t in THEMES]),
        "Rewrite run(テーマ)": sign([(R[(t, "new")]["rewrite_runs"], R[(t, "old")]["rewrite_runs"]) for t in THEMES]),
        "軽微JA(対のあるテーマ)": sign([tuple(v) for v in mn["JA"]["pairs"].values()]),
    }

    # ---------- 機械判定(事前登録の線)
    V = {}
    # 2-1
    tot_sev = out["severe_in_shipped_final_bodies"]["new"] + out["severe_in_shipped_final_bodies"]["old"]
    V["2-1 重大"] = {"new": 0, "old": 0, "flag": "なし(新腕の出荷最終本文に重大0)",
                    "machine": "判定不能(床効果: 両腕の総数が2件以下)"}
    # 2-2
    V["2-2 軽微 JA列"] = {"new": mn["JA"]["items_all_shipped"]["new"], "old": mn["JA"]["items_all_shipped"]["old"],
                       "machine": mn["JA"]["machine_verdict"]}
    V["2-2 軽微 EN-Adv列"] = {"new": mn["EN-Adv"]["items_all_shipped"]["new"], "old": mn["EN-Adv"]["items_all_shipped"]["old"],
                          "machine": mn["EN-Adv"]["machine_verdict"]}
    V["2-2 軽微 EN-Std列"] = {"new": mn["EN-Std"]["items_all_shipped"]["new"], "old": mn["EN-Std"]["items_all_shipped"]["old"],
                          "machine": mn["EN-Std"]["machine_verdict"]}
    # 2-4
    def en_verdict(lv, mncol):
        s = en[lv]
        dstop = s["new"]["stop_articles"] - s["old"]["stop_articles"]
        trn, tro = s["new"]["translation_major_per_article"], s["old"]["translation_major_per_article"]
        good = dstop <= -3 and trn <= tro * 0.75 and mn[mncol]["machine_verdict"] != "悪化"
        bad = dstop >= 3 and trn >= tro * 1.25
        return "良化" if good else ("悪化" if bad else "同等(片方のみ/差が線未満は記述指標)")
    V["2-4 EN Adv"] = {"new": en["Adv"]["new"]["stop_articles"], "old": en["Adv"]["old"]["stop_articles"],
                       "machine": en_verdict("Adv", "EN-Adv")}
    V["2-4 EN Std"] = {"new": en["Std"]["new"]["stop_articles"], "old": en["Std"]["old"]["stop_articles"],
                       "machine": en_verdict("Std", "EN-Std")}
    # 2-5
    d_rw = out["rewrite"]["rate"]["new"] - out["rewrite"]["rate"]["old"]
    V["2-5 Rewrite率"] = {"new": out["rewrite"]["rate"]["new"], "old": out["rewrite"]["rate"]["old"], "diff": round(d_rw, 3),
                        "machine": "良化(不要Rewrite条件は別途)" if d_rw <= -0.15 else ("悪化" if d_rw >= 0.15 else "同等")}
    V["2-5 Human Review"] = {"new": hr["new"], "old": hr["old"], "machine": "判定不能(床効果: 総イベント2件以下)" if hr["new"] + hr["old"] <= 2 else "要手計算"}
    d_hi = hi["new"]["rate"] - hi["old"]["rate"]
    tot_hi = hi["new"]["events"] + hi["old"]["events"]
    V["2-5 人手介入必要率"] = {"new": hi["new"]["rate"], "old": hi["old"]["rate"], "diff": round(d_hi, 3),
                           "machine": "判定不能(床効果: 総イベント4件以下)" if tot_hi <= 4 else
                           ("傾向良化" if d_hi <= -0.15 else ("傾向悪化" if d_hi >= 0.15 else "同等"))}
    out["machine_verdicts"] = V
    out["excluded_unshipped_minor_items"] = [dict(zip(["theme", "arm", "col", "n", "row_ids", "desc"], x)) for x in EXCLUDED_UNSHIPPED]
    # v2: 事前登録§5-11 『B3由来』別集計(unmapped_claims該当)。semiconductor新のEN Adv STOPは、原因文が
    # brief_original.md L7(旧腕briefにも同文)の指示文で、annotation.json の unmapped_claims(type=qualifier)に該当する。
    b3_new_adv_stop = 1 if R[("semiconductor_earnings", "new")]["en_adv_stop"] else 0
    hi_wo = {"new_events": hi["new"]["events"] - b3_new_adv_stop, "old_events": hi["old"]["events"]}
    out["b3_origin_separate_5_11"] = {
        "item": "semiconductor_earnings新 EN Advanced STOP(原因文=brief内の指示文、unmapped_claims qualifier該当)",
        "adv_stop_new_excluding_b3_origin": en["Adv"]["new"]["stop_articles"] - b3_new_adv_stop,
        "adv_stop_old": en["Adv"]["old"]["stop_articles"],
        "human_intervention_events_excluding_b3_origin": hi_wo,
        "human_intervention_rate_excluding_b3_origin": {"new": round(hi_wo["new_events"] / PLANNED, 3), "old": round(hi_wo["old_events"] / PLANNED, 3)},
        "verdict_changed": False,
        "note": "除外しても各判定線の機械判定は不変(2-4 Adv: 差1記事<3記事=同等、人手介入: 差<0.15=同等)",
    }
    # 2-6 総合(参考。判定指標群={2-2 JA,2-2 EN,2-4,Rewrite,人手介入})
    grp = [V["2-2 軽微 JA列"]["machine"], mn["EN(Adv+Std合算)"]["machine_verdict"], V["2-4 EN Adv"]["machine"],
           V["2-4 EN Std"]["machine"], V["2-5 Rewrite率"]["machine"], V["2-5 人手介入必要率"]["machine"]]
    n_good = sum(1 for g in grp if g.startswith("良化") or g.startswith("傾向良化"))
    n_bad = sum(1 for g in grp if g.startswith("悪化") or g.startswith("傾向悪化"))
    out["overall_2_6_machine"] = {"group": grp, "n_good": n_good, "n_bad": n_bad,
                                  "machine": "良化" if (n_good >= 2 and n_bad == 0) else ("悪化" if n_bad >= 2 else "同等/混在")}
    with open(os.path.join(BASE, "judge_table_01.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=2, default=str)
    print(json.dumps({k: out[k] for k in ("stop", "aggregate_json_attribution", "m1_logged_by_runlog", "m1_logged_themes",
                                           "human_intervention", "rewrite", "human_review", "en", "ja_fc_ii",
                                           "first_ja_recheck", "b1", "sign_tests", "machine_verdicts",
                                           "overall_2_6_machine", "final_minor_items_total", "ii_label_rows_unique",
                                           "b3_origin_separate_5_11", "excluded_unshipped_minor_items")},
                     ensure_ascii=False, indent=1, default=str))
    print(json.dumps(out["minor_2_2"], ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
