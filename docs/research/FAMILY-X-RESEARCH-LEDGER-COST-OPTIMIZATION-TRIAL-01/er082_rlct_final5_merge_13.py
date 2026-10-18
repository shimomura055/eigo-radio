# RLCT 委任_13: 5記事最終集計(新設計列、R-B7)。LLM/API呼出なし。
# 数値は既存の実測集計 aggregate.json(1a: coffee, inbound[M2c/M3c含む]) と aggregate_1b_all.json(1b 3記事)の行のみ。
# 新しい推定値は作らない。本scriptが行うのは同一列の和・比率(合算)のみ。
import argparse
import json
from pathlib import Path

ROOT = Path("er082_output/rlct_trial_01")
ART = ["coffee_prices", "inbound_tourism", "streaming_price", "openai_copyright", "central_bank_mortgage"]
# 新設計列: M2/M3 -> coffee=M2,M3 / inbound=M2c,M3c / 1b=M2,M3
NEWMETH = {
    "coffee_prices": {"M2": "M2", "M3": "M3"},
    "inbound_tourism": {"M2": "M2c", "M3": "M3c"},
    "streaming_price": {"M2": "M2", "M3": "M3"},
    "openai_copyright": {"M2": "M2", "M3": "M3"},
    "central_bank_mortgage": {"M2": "M2", "M3": "M3"},
}
COLS = ["M0", "M0b", "M1", "M2", "M3"]


def load():
    rows = json.loads((ROOT / "aggregate.json").read_text(encoding="utf-8"))["rows"] + \
        json.loads((ROOT / "aggregate_1b_all.json").read_text(encoding="utf-8"))["rows"]
    return {(r["article"], r["method"]): r for r in rows}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-md", required=True)
    ap.add_argument("--out-json", required=True)
    a = ap.parse_args()
    R = load()
    per = {}
    for art in ART:
        per[art] = {}
        for col in COLS:
            m = NEWMETH[art].get(col, col)
            r = R[(art, m)]
            d = dict(method_row=m, trial_llm=r["trial_llm_jpy"], trial_ws=r["trial_web_search_jpy"],
                     trial_total=r["trial_total_jpy"], ws_calls=r["web_search_calls"], queries=r["query_count"],
                     by_action=r["by_action_type"], reselect_count=r["reselect_count"], confirm_count=r["confirm_pass_count"],
                     b3_reselect=r["b3_reselect_jpy"], b3_confirm=r["b3_confirm_jpy"],
                     prod_eq=r["production_equivalent_jpy"], saving=r["saving_vs_M0_jpy"], saving_pct=r["saving_vs_M0_pct"],
                     soft_cap_exceeded=len(r["soft_cap_exceeded_requests"]))
            # inbound M2c/M3c: 実効Trial費用 = 補正元(旧M2/M3)+補正のみ(STAGE_1A_CORRECTION_01 §1,§8と同じ加算)
            if m in ("M2c", "M3c"):
                src = R[(art, r["corrected_from"])]
                d["effective_trial_total"] = round(src["trial_total_jpy"] + r["trial_total_jpy"], 3)
                d["effective_note"] = "補正元%s %s + 補正 %s" % (r["corrected_from"], src["trial_total_jpy"], r["trial_total_jpy"])
            else:
                d["effective_trial_total"] = r["trial_total_jpy"]
            per[art][col] = d
    ref_m0p = {art: R.get((art, "M0p")) for art in ART}
    old_inbound = {m: R[("inbound_tourism", m)] for m in ("M2", "M3")}
    tot = {}
    for col in COLS:
        tot[col] = dict(
            prod_eq=round(sum(per[x][col]["prod_eq"] for x in ART), 3),
            trial_effective=round(sum(per[x][col]["effective_trial_total"] for x in ART), 3),
            trial_llm=round(sum(per[x][col]["trial_llm"] for x in ART), 3),
            trial_ws=round(sum(per[x][col]["trial_ws"] for x in ART), 3),
            ws_calls=sum(per[x][col]["ws_calls"] for x in ART),
            queries=sum(per[x][col]["queries"] for x in ART),
            b3_reselect=round(sum(per[x][col]["b3_reselect"] for x in ART), 3),
            b3_confirm=round(sum(per[x][col]["b3_confirm"] for x in ART), 3),
            reselect_n=sum((per[x][col]["reselect_count"] or 0) for x in ART),
            confirm_n=sum((per[x][col]["confirm_count"] or 0) for x in ART),
            soft_cap_exceeded=sum(per[x][col]["soft_cap_exceeded"] for x in ART),
        )
    base = tot["M0"]["prod_eq"]
    for col in COLS:
        s = round(base - tot[col]["prod_eq"], 3)
        tot[col]["saving_vs_M0"] = s
        tot[col]["saving_pct"] = round(100.0 * s / base, 1)
        sv = [per[x][col]["saving"] for x in ART]
        tot[col]["signs"] = "".join("+" if v > 0 else ("-" if v < 0 else "0") for v in sv)
        pct = [per[x][col]["saving_pct"] for x in ART]
        tot[col]["pct_min"] = min(pct)
        tot[col]["pct_max"] = max(pct)
        tot[col]["pct_mean_of_articles"] = round(sum(pct) / len(pct), 1)
        tot[col]["n_plus"] = sum(1 for v in sv if v > 0)
        tot[col]["n_minus"] = sum(1 for v in sv if v < 0)
    out = dict(
        articles=ART, columns=COLS, new_design_methods=NEWMETH, per_article=per, totals=tot,
        m0p_reference={x: (None if r is None else dict(trial_total=r["trial_total_jpy"], ws_calls=r["web_search_calls"], queries=r["query_count"], by_action=r["by_action_type"])) for x, r in ref_m0p.items()},
        old_inbound_reference={m: dict(trial_total=r["trial_total_jpy"], prod_eq=r["production_equivalent_jpy"], saving=r["saving_vs_M0_jpy"], saving_pct=r["saving_vs_M0_pct"]) for m, r in old_inbound.items()},
        note="数値は aggregate.json(1a)・aggregate_1b_all.json(1b)の行のみ。合計・率は同一列の合算。旧inbound M2/M3は参考行で母数に入れない(R-B7)。本番換算=aggregate.pyの定義(Research+Ledger+B3[+再選定/確認]を共有分も帰属)。")
    Path(a.out_json).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

    L = ["# RLCT 5記事最終集計(新設計列, 委任_13)", "",
         "MEASURED(実測): 数値は`aggregate.json`(1a)・`aggregate_1b_all.json`(1b)の既存実測行のみ。合計・率は同一列の合算(新しい推定値なし)。",
         "新設計列: Coffee M2/M3(確認パス不要・同一経路)+inbound M2c/M3c(確認パス後)+1b 3記事 M2/M3(R-B7)。旧inbound M2/M3は参考行で母数に含めない。M0pは参考列。", "",
         "## 表1 本番換算JPY・対M0削減(記事別)", "",
         "| 記事 | M0 | M0b(削減JPY/%) | M1(削減JPY/%) | M2新設計(削減JPY/%) | M3新設計(削減JPY/%) |", "|---|---|---|---|---|---|"]
    for art in ART:
        p = per[art]
        L.append("| %s | %s | " % (art, p["M0"]["prod_eq"]) + " | ".join("%s (%+.3f/%+.1f%%)" % (p[c]["prod_eq"], p[c]["saving"], p[c]["saving_pct"]) for c in COLS[1:]) + " |")
    L.append("| **5記事合計** | %s | " % tot["M0"]["prod_eq"] + " | ".join("%s (%+.3f/%+.1f%%)" % (tot[c]["prod_eq"], tot[c]["saving_vs_M0"], tot[c]["saving_pct"]) for c in COLS[1:]) + " |")
    L.append("| 符号(Coffee,inbound,streaming,openai,central) | - | " + " | ".join("%s(+%d/-%d, 記事別%%範囲 %s〜%s)" % (tot[c]["signs"], tot[c]["n_plus"], tot[c]["n_minus"], tot[c]["pct_min"], tot[c]["pct_max"]) for c in COLS[1:]) + " |")
    L += ["", "注: 削減JPYの正=M0より安い。M0bは自然ばらつき(ノイズ幅)の基準。", "",
          "## 表2 Trial実費の内訳(検索ツール呼出・クエリ・LLM・Web検索手数料を別列、再選定/確認パス費用を分離)", "",
          "| 記事 | 方式(行) | Trial実費JPY | LLM | Web検索手数料 | 検索ツール呼出 | クエリ | 呼出種別 | 再選定/確認パス回数 | 再選定B3 JPY | 確認B3 JPY |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for art in ART:
        for c in COLS:
            d = per[art][c]
            eff = d["effective_trial_total"]
            effs = "%s" % eff + (" (=%s)" % d["effective_note"] if "effective_note" in d else "")
            L.append("| %s | %s(%s) | %s | %s | %s | %s | %s | %s | %s/%s | %s | %s |" % (art, c, d["method_row"], effs, d["trial_llm"], d["trial_ws"], d["ws_calls"], d["queries"], d["by_action"], d["reselect_count"], d["confirm_count"], d["b3_reselect"], d["b3_confirm"]))
        r = ref_m0p[art]
        if r:
            L.append("| %s | M0p(参考,Ledger検証のみ) | %s | %s | %s | %s | %s | %s | - | - | - |" % (art, r["trial_total_jpy"], r["trial_llm_jpy"], r["trial_web_search_jpy"], r["web_search_calls"], r["query_count"], r["by_action_type"]))
    L += ["", "注: inbound M2c/M3c行のLLM/検索/呼出は補正のみ分(新規検証0)。実費はTrial実費列に補正元との加算を併記。M3系は初回B3をM2と共有(Trial実費はM3側に初回B3を含まない)。Coffee M0のB3は既存再利用でTrial費用0。", "",
          "## 表3 方式別合計(5記事)", "",
          "| 方式 | 本番換算合計JPY | 対M0削減JPY | 対M0削減% | Trial実費合計(実効) | LLM | Web検索手数料 | 検索呼出 | クエリ | 再選定B3 JPY | 確認B3 JPY | 再選定/確認パス回数 | ソフト上限超過request |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in COLS:
        t = tot[c]
        L.append("| %s | %s | %+.3f | %+.1f%% | %s | %s | %s | %s | %s | %s | %s | %s/%s | %s |" % (c, t["prod_eq"], t["saving_vs_M0"], t["saving_pct"], t["trial_effective"], t["trial_llm"], t["trial_ws"], t["ws_calls"], t["queries"], t["b3_reselect"], t["b3_confirm"], t["reselect_n"], t["confirm_n"], t["soft_cap_exceeded"]))
    L += ["", "注: 表3のLLM/Web検索手数料/検索呼出/クエリ列は各行の自列(inbound M2c/M3cは補正分のみ)の合算で、Trial実費合計(実効)は補正元込み。", "",
          "## 参考: 旧設計 inbound M2/M3(修正前、母数に入れない)", "", "| 方式 | 本番換算 | 対M0削減JPY/% |", "|---|---|---|"]
    for m, r in old_inbound.items():
        L.append("| 旧%s | %s | %s/%s%% |" % (m, r["production_equivalent_jpy"], r["saving_vs_M0_jpy"], r["saving_vs_M0_pct"]))
    Path(a.out_md).write_text("\n".join(L) + "\n", encoding="utf-8")
    print("ok")


if __name__ == "__main__":
    main()
