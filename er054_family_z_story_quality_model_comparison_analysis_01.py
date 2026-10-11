# -*- coding: utf-8 -*-
"""FAMILY-Z-STORY-QUALITY-MODEL-COMPARISON-TRIAL-01 分析script(Trial専用、API呼出なし)。

driverが書いた 方式×作品×rep のjsonを読み、スコア分布・順位・方式間Spearman・極端結果・根拠整合候補・引用検証・
再現性・方式間割れ作品・L05・人間確認推奨を自動集計して SCORE_TABLE_01.md / ANALYSIS_01.md を生成する。
「候補」は機械抽出であり確定判定ではない(根拠妥当性・原作理解の誤りはClaude/人が確認する)。
過去評価結果(封印)は読まない。
"""
from __future__ import annotations

import argparse
import difflib
import glob
import json
import math
import os
import re
import statistics as st

import er054_family_z_story_quality_model_comparison_trial_01 as drv

METHODS = drv.METHODS
AXES = drv.AXES
VERDICT_PT = {"PASS": 2, "WEAK": 1, "FAIL": 0}

# 自己申告の弱点語彙(「魅力が失われる」「困難」等)。否定(〜ない等)が直後にある場合は除外する。
WEAK_RE = re.compile(r"(失われ|失う|失い|薄ま|薄れ|困難|難し|削る|削ると|削れ|消え|損な|弱い|弱く|乏しい|不足|限定的|依存|犠牲|再現できな|収まらな|収まりきら)")
NEG_RE = re.compile(r"^.{0,4}(ない|ず|ぬ|ません|なかっ|にくい)")
HIGH_SCORE = 4          # 1〜5点方式で「高スコア」とみなす下限
RANK_SPREAD_THRESH = 4  # 方式間で順位差がこれ以上(9作品中)なら割れ作品
EXTREME_RATE = 0.8      # 満点(最低点)率がこれ以上なら天井(床)
LOW_VARIANCE_RANGE = 0.15  # 作品平均(0-1正規化)の最大-最小がこれ未満なら識別力不足候補


# ------------------------------------------------------------ 基本関数(testで使用)
def axis_score(method: str, result: dict, ax: str) -> float:
    return float(VERDICT_PT[result[ax]["verdict"]]) if method == "B" else float(result[ax]["score"])


def primary_norm(method: str, result: dict) -> float:
    """方式共通の0〜1正規化スコア(軸の平均)。A/C/D: (平均-1)/4、B: PASS=2/WEAK=1/FAIL=0の平均/2。"""
    vals = [axis_score(method, result, ax) for ax in AXES[method]]
    mean = sum(vals) / len(vals)
    return mean / 2.0 if method == "B" else (mean - 1.0) / 4.0


def overall_norm(method: str, result: dict) -> float:
    o = result["overall"]
    return VERDICT_PT[o["verdict"]] / 2.0 if method == "B" else (o["score"] - 1) / 4.0


def is_full(method: str, result: dict) -> bool:
    mx = 2 if method == "B" else 5
    return all(axis_score(method, result, ax) == mx for ax in AXES[method])


def is_floor(method: str, result: dict) -> bool:
    mn = 0 if method == "B" else 1
    return all(axis_score(method, result, ax) == mn for ax in AXES[method])


def ranks(values: list) -> list:
    """大きい値が1位。同値は平均順位。"""
    order = sorted(range(len(values)), key=lambda i: -values[i])
    r = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def spearman(x: list, y: list):
    """Spearman順位相関(同値は平均順位のPearson)。片方の分散が0ならNone。"""
    if len(x) != len(y) or len(x) < 2:
        return None
    rx, ry = ranks(x), ranks(y)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    sxx = sum((a - mx) ** 2 for a in rx)
    syy = sum((b - my) ** 2 for b in ry)
    if sxx == 0 or syy == 0:
        return None
    return sum((a - mx) * (b - my) for a, b in zip(rx, ry)) / math.sqrt(sxx * syy)


def _weak_hit(text: str):
    """弱点語彙を含み、かつ直後が否定でないものを返す。"""
    hits = []
    for m in WEAK_RE.finditer(text or ""):
        if NEG_RE.match(text[m.end():m.end() + 6]):
            continue
        hits.append(m.group(1))
    return hits


def detect_contradictions(method: str, result: dict) -> list:
    """根拠とスコアの矛盾候補(機械抽出。人が確認)。戻り値: [{kind, axis, detail}]。"""
    out = []
    for ax in AXES[method]:
        if method == "D" and ax == "loss_severity":
            continue  # この軸は理由文が「失われる量」そのものを述べるため語彙判定の対象外(下の構造判定で扱う)
        high = (result[ax]["verdict"] == "PASS") if method == "B" else (result[ax]["score"] >= HIGH_SCORE)
        text = result[ax]["reason"] + (" " + result[ax]["weakness"] if method == "B" and result[ax]["weakness"] != "なし" else "")
        hits = _weak_hit(text)
        if high and hits:
            out.append({"kind": "weak_word_vs_high_score", "axis": ax, "detail": f"高評価なのに弱点語彙 {sorted(set(hits))}"})
    if method == "D":
        highs = [x for x in result.get("lost_in_compression", []) if x["severity"] == "high"]
        if highs and result["loss_severity"]["score"] >= HIGH_SCORE:
            out.append({"kind": "lost_high_vs_loss_severity_score", "axis": "loss_severity",
                        "detail": f"severity=highの損失{len(highs)}件を列挙しながら loss_severity={result['loss_severity']['score']}"})
        if len(highs) >= 2 and result["overall"]["score"] >= HIGH_SCORE:
            out.append({"kind": "lost_high_vs_overall", "axis": "overall", "detail": f"severity=high{len(highs)}件なのに総合{result['overall']['score']}"})
    if method == "B":
        cc = result["consistency_check"]
        if cc["contradictions_found"] and not cc["verdicts_revised"]:
            out.append({"kind": "self_reported_contradiction_not_revised", "axis": "consistency_check",
                        "detail": f"矛盾{len(cc['contradictions_found'])}件を自己申告したが判定を修正していない"})
    # 総合と軸平均の乖離
    if method != "B":
        mean = sum(result[ax]["score"] for ax in AXES[method]) / 4
        if abs(result["overall"]["score"] - mean) >= 2:
            out.append({"kind": "overall_axes_gap", "axis": "overall", "detail": f"総合{result['overall']['score']} vs 軸平均{mean:.2f}"})
    return out


def bigrams(s: str) -> set:
    s = re.sub(r"\s", "", s or "")
    return {s[i:i + 2] for i in range(len(s) - 1)}


def jaccard(a: str, b: str) -> float:
    A, B = bigrams(a), bigrams(b)
    return len(A & B) / len(A | B) if (A | B) else 1.0


def classify_unverified(quote: str, source_text: str) -> str:
    """文字列不一致の引用を分類: near(表記ゆれ・軽微な欠落)かabsent(原文に存在しない)。どちらも原作理解の誤りとは別の『文字列不一致』。"""
    q, src = drv.normalize_ws(quote), drv.normalize_ws(source_text)
    if not q:
        return "absent"
    m = difflib.SequenceMatcher(None, q, src, autojunk=False).find_longest_match(0, len(q), 0, len(src))
    return "near" if m.size / len(q) >= 0.8 else "absent"


# ------------------------------------------------------------ 読込・集計
def load_records(in_dir: str) -> list:
    recs = []
    for p in sorted(glob.glob(os.path.join(in_dir, "*", "[ABCD]", "L*_rep*.json"))):
        drv.assert_not_sealed(p)
        with open(p, encoding="utf-8") as f:
            recs.append(json.load(f))
    return recs


def analyze(recs: list, sources: dict | None = None) -> dict:
    ok = [r for r in recs if "result" in r]
    works = sorted({r["work_id"] for r in ok})
    methods = [m for m in METHODS if any(r["method"] == m for r in ok)]
    by = {}
    for r in ok:
        by.setdefault((r["method"], r["work_id"]), {})[r["rep"]] = r
    A = {"works": works, "methods": methods, "n_ok": len(ok), "n_err": len(recs) - len(ok)}

    # 作品別×方式: rep平均(0-1)と順位
    mean_norm = {m: {w: st.mean(primary_norm(m, x["result"]) for x in by[(m, w)].values()) for w in works if (m, w) in by} for m in methods}
    A["mean_norm"] = mean_norm
    A["mean_overall_norm"] = {m: {w: st.mean(overall_norm(m, x["result"]) for x in by[(m, w)].values()) for w in works if (m, w) in by} for m in methods}
    A["rank"] = {}
    for m in methods:
        ws = [w for w in works if w in mean_norm[m]]
        rk = ranks([mean_norm[m][w] for w in ws])
        A["rank"][m] = dict(zip(ws, rk))

    # 方式別分布
    dist = {}
    for m in methods:
        runs = [x["result"] for (mm, w), reps in by.items() if mm == m for x in reps.values()]
        axvals = [axis_score(m, r, ax) for r in runs for ax in AXES[m]]
        wm = list(mean_norm[m].values())
        mx = 2 if m == "B" else 5
        mn = 0 if m == "B" else 1
        dist[m] = {"n_runs": len(runs), "axis_mean": round(st.mean(axvals), 3), "axis_sd": round(st.pstdev(axvals), 3),
                   "work_mean_norm_mean": round(st.mean(wm), 3), "work_mean_norm_sd": round(st.pstdev(wm), 3),
                   "work_range_norm": round(max(wm) - min(wm), 3),
                   "full_run_rate": round(sum(is_full(m, r) for r in runs) / len(runs), 3),
                   "floor_run_rate": round(sum(is_floor(m, r) for r in runs) / len(runs), 3),
                   "axis_max_rate": round(sum(v == mx for v in axvals) / len(axvals), 3),
                   "axis_min_rate": round(sum(v == mn for v in axvals) / len(axvals), 3),
                   "axis_histogram": {str(k): axvals.count(k) for k in sorted(set(axvals))}}
    A["distribution"] = dist

    # 極端結果検出
    ext = {}
    for m in methods:
        d, flags = dist[m], []
        if d["full_run_rate"] >= EXTREME_RATE:
            flags.append("天井(全軸満点の実行が80%以上=識別力不足)")
        if d["floor_run_rate"] >= EXTREME_RATE:
            flags.append("床(全軸最低の実行が80%以上)")
        if d["work_mean_norm_sd"] == 0:
            flags.append("分散ゼロ(全作品が同一スコア)")
        elif d["work_range_norm"] < LOW_VARIANCE_RANGE:
            flags.append(f"低分散(作品平均の幅{d['work_range_norm']}<{LOW_VARIANCE_RANGE})")
        ext[m] = flags
    A["extreme"] = ext

    # 方式間Spearman(作品平均)
    corr = {}
    for i, a in enumerate(methods):
        for b in methods[i + 1:]:
            ws = [w for w in works if w in mean_norm[a] and w in mean_norm[b]]
            corr[f"{a}-{b}"] = spearman([mean_norm[a][w] for w in ws], [mean_norm[b][w] for w in ws])
    A["spearman_between_methods"] = corr

    # 順位が大きく割れる作品
    split = []
    for w in works:
        rs = {m: A["rank"][m][w] for m in methods if w in A["rank"][m]}
        if rs and max(rs.values()) - min(rs.values()) >= RANK_SPREAD_THRESH:
            split.append({"work": w, "ranks": rs, "spread": max(rs.values()) - min(rs.values())})
    A["split_works"] = sorted(split, key=lambda x: -x["spread"])
    A["L05"] = {m: {"mean_norm": mean_norm[m].get("L05"), "rank": A["rank"][m].get("L05"),
                    "axis_scores": {ax: [axis_score(m, x["result"], ax) for x in by[(m, "L05")].values()] for ax in AXES[m]} if (m, "L05") in by else None}
                for m in methods}

    # 再現性(rep間)
    stab = {}
    for m in methods:
        diffs, agree, tot = [], 0, 0
        r1, r2 = {}, {}
        for w in works:
            reps = by.get((m, w), {})
            if len(reps) >= 2:
                a, b = reps[min(reps)], reps[max(reps)]
                diffs.append(abs(primary_norm(m, a["result"]) - primary_norm(m, b["result"])))
                r1[w], r2[w] = primary_norm(m, a["result"]), primary_norm(m, b["result"])
                for ax in AXES[m]:
                    tot += 1
                    agree += axis_score(m, a["result"], ax) == axis_score(m, b["result"], ax)
        ws = sorted(r1)
        stab[m] = {"mean_abs_diff_norm": round(st.mean(diffs), 3) if diffs else None, "max_abs_diff_norm": round(max(diffs), 3) if diffs else None,
                   "axis_exact_agreement": round(agree / tot, 3) if tot else None,
                   "spearman_rep1_rep2": spearman([r1[w] for w in ws], [r2[w] for w in ws]) if len(ws) > 2 else None,
                   "n_pairs": len(diffs)}
    A["stability"] = stab

    # 根拠整合(矛盾候補)
    contra = []
    for r in ok:
        for c in detect_contradictions(r["method"], r["result"]):
            contra.append({"method": r["method"], "work": r["work_id"], "rep": r["rep"], **c})
    A["contradictions"] = contra

    # 引用: 文字列一致率と不一致の分類(原作理解の誤りとは別)
    quote = {}
    unverified = []
    for m in methods:
        tot = bad = 0
        for (mm, w), reps in by.items():
            if mm != m:
                continue
            for x in reps.values():
                qv = x["quote_verification"]
                tot += qv["quote_total"]
                bad += qv["unverified_quote_count"]
                if qv["unverified_quote_count"] and sources and w in sources:
                    for ax in AXES[m]:
                        for q, okf in zip(x["result"][ax]["evidence_quotes"], qv["per_axis"][ax]):
                            if not okf:
                                unverified.append({"method": m, "work": w, "rep": x["rep"], "axis": ax, "quote": q,
                                                   "class": classify_unverified(q, sources[w])})
        quote[m] = {"quotes": tot, "unverified": bad, "match_rate": round(1 - bad / tot, 3) if tot else None}
    A["quote"] = quote
    A["unverified_quotes"] = unverified

    # 原作理解の誤り候補(機械抽出。確定ではない)
    und = []
    if sources:
        for r in ok:
            src = drv.normalize_ws(sources.get(r["work_id"], ""))
            for name in r["result"]["key_facts"]["main_characters"]:
                head = re.split(r"[(（\s]", name)[0]
                if head and src and drv.normalize_ws(head) not in src and len(head) >= 2:
                    und.append({"kind": "character_not_in_source", "method": r["method"], "work": r["work_id"], "rep": r["rep"], "detail": name})
    for w in works:
        evs = [(r["method"], r["rep"], r["result"]["key_facts"]["central_event"]) for r in ok if r["work_id"] == w]
        sims = [jaccard(a[2], b[2]) for i, a in enumerate(evs) for b in evs[i + 1:]]
        if sims and st.mean(sims) < 0.15:
            und.append({"kind": "central_event_divergence", "work": w, "detail": f"中心事件の記述が方式・rep間で大きく異なる(2gram Jaccard平均{st.mean(sims):.2f})"})
    A["understanding_candidates"] = und

    # 人間確認推奨
    human = []
    for m in methods:
        rk = A["rank"][m]
        top = min(rk, key=rk.get)
        bot = max(rk, key=rk.get)
        human.append({"method": m, "top": top, "bottom": bot})
    A["human_review"] = {"per_method_top_bottom": human, "split_works": [s["work"] for s in A["split_works"]], "always": ["L05"]}

    # 運用面(時間・費用)
    ops = {}
    for m in methods:
        rs = [r for r in ok if r["method"] == m]
        costs = [r["cost_jpy"] for r in rs if r.get("cost_jpy") is not None]
        ops[m] = {"calls": len(rs), "mean_elapsed_sec": round(st.mean(r["elapsed_sec"] for r in rs), 2),
                  "total_cost_jpy": round(sum(costs), 3) if costs else None,
                  "mean_output_tokens": round(st.mean(r["usage"]["output_tokens"] for r in rs if r.get("usage")), 0) if any(r.get("usage") for r in rs) else None}
    A["ops"] = ops
    A["actual_model_ids"] = sorted({str(r.get("actual_model_id")) for r in ok})
    return A


# ------------------------------------------------------------ 出力
def _fmt(v, nd=2):
    return "-" if v is None else f"{v:.{nd}f}"


def render_score_table(A: dict, title_note: str) -> str:
    L = [f"# SCORE_TABLE_01 {title_note}", "", "正規化スコア=軸平均を0〜100%へ(A/C/D: (平均-1)/4、B: PASS=2/WEAK=1/FAIL=0の平均/2)。rep平均。()内は順位(1=最高、同値は平均順位)。", ""]
    ms = A["methods"]
    L.append("| 作品 | " + " | ".join(f"方式{m}" for m in ms) + " |")
    L.append("|---|" + "---|" * len(ms))
    for w in A["works"]:
        L.append(f"| {w} | " + " | ".join(f"{A['mean_norm'][m].get(w, float('nan')) * 100:.0f}% ({A['rank'][m].get(w, 0):.1f})" for m in ms) + " |")
    L += ["", "## 方式別の分布", "", "| 方式 | runs | 軸平均 | 軸SD | 作品平均の幅 | 全軸満点率 | 全軸最低率 | 軸満点率 | 軸最低率 |", "|---|---|---|---|---|---|---|---|---|"]
    for m in ms:
        d = A["distribution"][m]
        L.append(f"| {m} | {d['n_runs']} | {d['axis_mean']} | {d['axis_sd']} | {d['work_range_norm']} | {d['full_run_rate']} | {d['floor_run_rate']} | {d['axis_max_rate']} | {d['axis_min_rate']} |")
    L += ["", "軸別ヒストグラム: " + "; ".join(f"{m}={A['distribution'][m]['axis_histogram']}" for m in ms), "",
          "## 方式間Spearman(作品平均)", ""] + [f"- {k}: {_fmt(v)}" for k, v in A["spearman_between_methods"].items()]
    return "\n".join(L) + "\n"


def render_analysis(A: dict, title_note: str) -> str:
    L = [f"# ANALYSIS_01 {title_note}", "", "本書は機械集計。『候補』は確定判定ではなく、Claude/人が根拠の妥当性を確認する(AI評価だけで最終FIXしない)。", "",
         f"- 解析対象: 成功{A['n_ok']}件 / 失敗・欠損{A['n_err']}件 / actual model_id: {A['actual_model_ids']}", "",
         "## 1. 極端結果の検出", ""]
    L += [f"- 方式{m}: " + ("; ".join(f) if f else "検出なし") for m, f in A["extreme"].items()]
    L += ["", "## 2. 再現性(同一方式N回の差=LLMゆらぎ)", "", "| 方式 | 作品ペア数 | rep間の差の平均(0-1) | 最大 | 軸一致率 | Spearman(rep1,rep2) |", "|---|---|---|---|---|---|"]
    for m, s in A["stability"].items():
        L.append(f"| {m} | {s['n_pairs']} | {_fmt(s['mean_abs_diff_norm'], 3)} | {_fmt(s['max_abs_diff_norm'], 3)} | {_fmt(s['axis_exact_agreement'], 3)} | {_fmt(s['spearman_rep1_rep2'])} |")
    L += ["", "切り分け: 同一方式のrep間差=LLMゆらぎ、方式間の順位差=Prompt/基準差。rep間の順位相関が高く方式間相関が低ければPrompt設計差、rep間相関自体が低ければLLM能力/ゆらぎ。", "",
          "## 3. 方式間で順位が大きく割れる作品", ""]
    L += [f"- {s['work']}: 順位差{s['spread']} {s['ranks']}" for s in A["split_works"]] or ["- なし"]
    L += ["", "## 4. L05(交尾)の方式別評価", ""]
    for m, v in A["L05"].items():
        L.append(f"- 方式{m}: 正規化{_fmt(v['mean_norm'], 2)} 順位{v['rank']} 軸別={v['axis_scores']}")
    L += ["", "## 5. 根拠とスコアの矛盾候補(機械抽出)", "", f"候補{len(A['contradictions'])}件(弱点語彙判定は文脈を見ないため偽陽性を含む)。", ""]
    L += [f"- 方式{c['method']} {c['work']} rep{c['rep']} [{c['kind']}] {c['axis']}: {c['detail']}" for c in A["contradictions"][:80]]
    L += ["", "## 6. 引用の文字列一致率(原作理解の誤りとは別集計)", "", "| 方式 | 引用数 | 不一致 | 一致率 |", "|---|---|---|---|"]
    L += [f"| {m} | {q['quotes']} | {q['unverified']} | {_fmt(q['match_rate'], 3)} |" for m, q in A["quote"].items()]
    cls = {}
    for u in A["unverified_quotes"]:
        cls[u["class"]] = cls.get(u["class"], 0) + 1
    L += ["", f"不一致の内訳: {cls}(near=表記ゆれ・軽微な欠落、absent=原文に存在しない)。", "",
          "## 7. 原作理解の誤り候補(機械抽出。確定は人/Claude)", ""]
    L += [f"- [{u['kind']}] {u.get('method', '')} {u['work']} {u.get('detail')}" for u in A["understanding_candidates"][:60]] or ["- なし"]
    L += ["", "## 8. 運用(時間・費用)", "", "| 方式 | calls | 平均秒 | 平均出力tok | 実費(円) |", "|---|---|---|---|---|"]
    L += [f"| {m} | {o['calls']} | {o['mean_elapsed_sec']} | {o['mean_output_tokens']} | {o['total_cost_jpy']} |" for m, o in A["ops"].items()]
    h = A["human_review"]
    L += ["", "## 9. 人間確認推奨作品", "", "- 各方式の最高/最低: " + "; ".join(f"{x['method']}: 最高{x['top']}/最低{x['bottom']}" for x in h["per_method_top_bottom"]),
          f"- 割れ作品: {h['split_works']}", f"- 常に確認: {h['always']}(重要検証対象『交尾』)", "",
          "## 10. 推奨・次点・不採用(人/Fableが記入。雛形)", "", "- 最有望: (未記入)", "- 次点: (未記入)", "- 不採用: (未記入、理由付き)", "- 限界・追加検証条件: (未記入)"]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in-dir", default=os.path.join(drv.OUT_BASE, "mock_run"))
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--note", default="(MOCK乾式。実評価ではない)")
    args = ap.parse_args()
    recs = load_records(args.in_dir)
    sources = {w: drv.build_unit(w)["text"] for w in {r["work_id"] for r in recs}}
    A = analyze(recs, sources)
    out = args.out_dir or args.in_dir
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "SCORE_TABLE_01.md"), "w", encoding="utf-8") as f:
        f.write(render_score_table(A, args.note))
    with open(os.path.join(out, "ANALYSIS_01.md"), "w", encoding="utf-8") as f:
        f.write(render_analysis(A, args.note))
    with open(os.path.join(out, "analysis_01.json"), "w", encoding="utf-8") as f:
        json.dump(A, f, ensure_ascii=False, indent=2, default=str)
    print(f"works={len(A['works'])} methods={A['methods']} ok={A['n_ok']} err={A['n_err']} contradictions={len(A['contradictions'])} -> {out}")


if __name__ == "__main__":
    main()
