# ============================================================
# er003_p2h_analyze_user_scores.py
# ER-003-P2H: P2Gユーザー評価の取込・ブラインド解除・L/P/U方式比較
# ============================================================
# ユーザーが提供したSet A/B/C・Rank 1-10の90件評価(〇/△/×)を正式入力
# として取り込み、P2Gの決定的成果物(key_words_selection.json/
# blind_mapping.json/form_qa.json)と照合してmappingを解除し、L/P/U
# ごとに再集計する。Key Wordsは再生成せず、製品仕様(5件)も変更しない。
# API呼び出しは一切行わない。
#
# 主キーはarticle_id + blind_set + rankであり、phrase/glossの一致は
# 記録用の付随情報(match_status)であって、行の紐付けには使わない。
# 一致不能な行(P2G側にその記事/Set/rankの項目が存在しない)があれば
# 例外を送出して停止し、勝手に別rankへ移さない。

from __future__ import annotations

import csv
import difflib
import json
import re
import statistics
import unicodedata
from itertools import combinations

RATING_SCORES = {"〇": 2, "△": 1, "×": 0}
ARTICLE_IDS = ("A01", "A02", "ADD03")
SET_LABELS = ("A", "B", "C")
STRATEGY_IDS = ("L", "P", "U")
RANKS = tuple(range(1, 11))
TOP5_RANKS = tuple(range(1, 6))
RANK6_10_RANKS = tuple(range(6, 11))

P2G_ROOT = "er003_output/p2g"
P2H_ROOT = "er003_output/p2h"

RAW_TSV_HEADER = ("article", "set", "rank", "display_phrase", "ja_gloss", "rating")

# 以前の画像集計(監査用に保持。正式値は今回の詳細行から再計算する)。
PRIOR_AGGREGATE_IMAGE = {
    "A01": {"A": 13, "B": 13, "C": 17},
    "A02": {"A": 15, "B": 15, "C": 11},
    "ADD03": {"A": 16, "B": 13, "C": 15},
}


class ReconciliationError(ValueError):
    """P2G成果物と照合できない行がある場合(勝手に別rankへ移さず停止する)。"""


def rating_to_score(symbol: str) -> int:
    if symbol not in RATING_SCORES:
        raise ValueError(f"unknown rating symbol: {symbol!r}")
    return RATING_SCORES[symbol]


def normalize_text(text: str) -> str:
    """NFKC正規化・NBSP→space・連続空白圧縮・大小文字・タイポグラフィック
    アポストロフィの正規化を行う。typo検出・表記ゆれ確認にのみ使い、
    行の紐付け(主キー)には使わない。"""
    t = unicodedata.normalize("NFKC", text or "")
    t = t.replace(" ", " ")
    t = t.translate(str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"'}))
    t = re.sub(r"\s+", " ", t).strip().lower()
    return t


def parse_raw_tsv(text: str) -> list:
    lines = [l for l in text.splitlines() if l.strip()]
    header = lines[0].split("\t")
    rows = []
    for line in lines[1:]:
        fields = line.split("\t")
        row = dict(zip(header, fields))
        row["rank"] = int(row["rank"])
        rows.append(row)
    return rows


def validate_raw_rows(rows: list) -> dict:
    reasons = []
    if len(rows) != 90:
        reasons.append(f"90件でない(実際: {len(rows)}件)")

    seen_keys = set()
    for row in rows:
        key = (row["article"], row["set"], row["rank"])
        if key in seen_keys:
            reasons.append(f"重複キー: {key}")
        seen_keys.add(key)
        if row["rating"] not in RATING_SCORES:
            reasons.append(f"unknown rating symbol: {row['rating']!r} at {key}")

    expected_keys = {(a, s, r) for a in ARTICLE_IDS for s in SET_LABELS for r in RANKS}
    missing = expected_keys - seen_keys
    extra = seen_keys - expected_keys
    if missing:
        reasons.append(f"欠落キー: {sorted(missing)}")
    if extra:
        reasons.append(f"予期しないキー: {sorted(extra)}")

    return {"ok": len(reasons) == 0, "reasons": reasons}


def load_blind_mapping(article_id: str) -> dict:
    with open(f"{P2G_ROOT}/{article_id}/blind_mapping.json", encoding="utf-8") as f:
        return json.load(f)


def load_p2g_selection(article_id: str, strategy_id: str) -> dict:
    with open(f"{P2G_ROOT}/{article_id}/{strategy_id}/key_words_selection.json", encoding="utf-8") as f:
        return json.load(f)


def load_form_qa(article_id: str) -> dict:
    with open(f"{P2G_ROOT}/{article_id}/form_qa.json", encoding="utf-8") as f:
        return json.load(f)


def match_status(user_text: str, canonical_text: str) -> str:
    """行の紐付けには使わない、記録専用の表記ゆれ判定。scoreは変更しない。"""
    nu, nc = normalize_text(user_text), normalize_text(canonical_text)
    if nu == nc:
        return "EXACT_MATCH"
    ratio = difflib.SequenceMatcher(None, nu, nc).ratio()
    if ratio >= 0.85:
        return "LIKELY_TYPO_OR_MINOR_VARIANT"
    return "DIFFERS"


def reconcile_rows(raw_rows: list) -> list:
    """raw_rows(90件)をP2G成果物と照合し、mappingを解除したnormalized
    datasetを返す。主キーはarticle_id + blind_set(生ラベルA/B/C)+rank。
    一致不能な行があればReconciliationErrorを送出して停止する。"""
    # 実際にraw_rowsへ登場する記事のファイルだけを遅延読み込みする
    # (テスト時に一部記事のfixtureしか用意していなくても動作するため、
    # かつ本番実行でも不要なファイルアクセスをしないため)。
    mappings: dict = {}
    selections: dict = {}
    form_qas: dict = {}

    normalized = []
    for row in raw_rows:
        article_id, blind_set, rank = row["article"], row["set"], row["rank"]
        set_label = f"Set {blind_set}"

        if article_id not in mappings:
            mappings[article_id] = load_blind_mapping(article_id)
        mapping = mappings[article_id]
        if set_label not in mapping:
            raise ReconciliationError(f"{article_id}/{set_label}: mappingが見つかりません")
        strategy_id = mapping[set_label]

        cache_key = (article_id, strategy_id)
        if cache_key not in selections:
            selections[cache_key] = load_p2g_selection(article_id, strategy_id)
        selection = selections[cache_key]

        item = next((it for it in selection["items"] if it["rank"] == rank), None)
        if item is None:
            raise ReconciliationError(
                f"{article_id}/{set_label}/rank{rank}: P2G成果物にこのrankの項目がありません")

        if article_id not in form_qas:
            form_qas[article_id] = load_form_qa(article_id)
        qa_result = form_qas[article_id]["parsed_result"]
        qa_set = next((s for s in qa_result["sets"] if s["runtime_strategy_id"] == strategy_id), None)
        qa_item = next((it for it in qa_set["items"] if it["rank"] == rank), None) if qa_set else None

        normalized.append({
            "article_id": article_id,
            "blind_set": blind_set,
            "strategy_id": strategy_id,
            "rank": rank,
            "research_band": item["research_band"],
            "user_input_phrase": row["display_phrase"],
            "canonical_phrase": item["display_phrase"],
            "user_input_gloss": row["ja_gloss"],
            "canonical_gloss": item["ja_gloss"],
            "rating_symbol": row["rating"],
            "score": rating_to_score(row["rating"]),
            "phrase_match_status": match_status(row["display_phrase"], item["display_phrase"]),
            "gloss_match_status": match_status(row["ja_gloss"], item["ja_gloss"]),
            "source_span": item["source_span"],
            "source_sentence": item["source_sentence"],
            "extraction_form_qa_verdict": qa_item["form_verdict"] if qa_item else None,
            "extraction_form_qa_notes": qa_item["notes"] if qa_item else None,
        })

    return normalized


# ============================================================
# 集計
# ============================================================
def _band_rows(rows: list, band: str) -> list:
    return [r for r in rows if r["research_band"] == band]


def _rating_counts(rows: list) -> dict:
    counts = {"〇": 0, "△": 0, "×": 0}
    for r in rows:
        counts[r["rating_symbol"]] += 1
    return counts


def aggregate_by_group(normalized: list, group_keys: tuple) -> dict:
    """group_keysでグループ化し、Top5/Rank6-10/Total score・件数・
    ranking_liftを計算する。"""
    groups: dict = {}
    for row in normalized:
        key = tuple(row[k] for k in group_keys)
        groups.setdefault(key, []).append(row)

    result = {}
    for key, rows in groups.items():
        top5 = _band_rows(rows, "TOP_5")
        rank6_10 = _band_rows(rows, "RANK_6_TO_10")
        top5_score = sum(r["score"] for r in top5)
        rank6_10_score = sum(r["score"] for r in rank6_10)
        top5_avg = top5_score / len(top5) if top5 else 0.0
        rank6_10_avg = rank6_10_score / len(rank6_10) if rank6_10 else 0.0
        counts = _rating_counts(rows)
        top5_counts = _rating_counts(top5)
        result[key] = {
            "top5_score": top5_score,
            "rank6_10_score": rank6_10_score,
            "total_score": top5_score + rank6_10_score,
            "counts": counts,
            "top5_maru_rate": round(top5_counts["〇"] / len(top5), 3) if top5 else 0.0,
            "total_maru_rate": round(counts["〇"] / len(rows), 3) if rows else 0.0,
            "ranking_lift": round(top5_avg - rank6_10_avg, 3),
        }
    return result


def aggregate_by_article_set(normalized: list) -> dict:
    return aggregate_by_group(normalized, ("article_id", "blind_set"))


def aggregate_by_article_strategy(normalized: list) -> dict:
    return aggregate_by_group(normalized, ("article_id", "strategy_id"))


def aggregate_strategy_cross_article(article_strategy_agg: dict) -> dict:
    by_strategy: dict = {}
    for (article_id, strategy_id), stats in article_strategy_agg.items():
        by_strategy.setdefault(strategy_id, []).append((article_id, stats))

    result = {}
    for strategy_id, entries in by_strategy.items():
        top5_total = sum(s["top5_score"] for _, s in entries)
        rank6_10_total = sum(s["rank6_10_score"] for _, s in entries)
        totals_per_article = {a: s["total_score"] for a, s in entries}
        counts = {"〇": 0, "△": 0, "×": 0}
        for _, s in entries:
            for k, v in s["counts"].items():
                counts[k] += v
        lifts = [s["ranking_lift"] for _, s in entries]
        values = list(totals_per_article.values())
        result[strategy_id] = {
            "top5_total": top5_total,
            "rank6_10_total": rank6_10_total,
            "total_total": top5_total + rank6_10_total,
            "counts": counts,
            "totals_per_article": totals_per_article,
            "mean_total_per_article": round(statistics.mean(values), 3),
            "median_total_per_article": statistics.median(values),
            "min_total_per_article": min(values),
            "max_total_per_article": max(values),
            "stdev_total_per_article": round(statistics.pstdev(values), 3) if len(values) > 1 else 0.0,
            "ranking_lift_mean": round(statistics.mean(lifts), 3),
        }
    return result


def compute_rank1_counts(article_strategy_agg: dict) -> dict:
    by_article: dict = {}
    for (article_id, strategy_id), stats in article_strategy_agg.items():
        by_article.setdefault(article_id, {})[strategy_id] = stats["total_score"]

    rank1_counts = {sid: 0 for sid in STRATEGY_IDS}
    tie_articles = []
    winner_by_article = {}
    for article_id, scores in by_article.items():
        max_score = max(scores.values())
        winners = [sid for sid, sc in scores.items() if sc == max_score]
        if len(winners) > 1:
            tie_articles.append(article_id)
        for w in winners:
            rank1_counts[w] += 1
        winner_by_article[article_id] = winners
    return {"rank1_counts": rank1_counts, "tie_articles": tie_articles, "winner_by_article": winner_by_article}


def compute_rank_position_averages(normalized: list) -> dict:
    result = {}
    for strategy_id in STRATEGY_IDS:
        result[strategy_id] = {}
        for rank in RANKS:
            scores = [r["score"] for r in normalized if r["strategy_id"] == strategy_id and r["rank"] == rank]
            result[strategy_id][rank] = round(statistics.mean(scores), 3) if scores else None
    return result


def compute_pairwise(article_strategy_agg: dict) -> dict:
    result = {}
    for a, b in combinations(STRATEGY_IDS, 2):
        per_article = {}
        wins_a = wins_b = ties = 0
        top5_diff_sum = 0
        total_diff_sum = 0
        for article_id in ARTICLE_IDS:
            sa = article_strategy_agg[(article_id, a)]
            sb = article_strategy_agg[(article_id, b)]
            top5_diff = sa["top5_score"] - sb["top5_score"]
            total_diff = sa["total_score"] - sb["total_score"]
            top5_diff_sum += top5_diff
            total_diff_sum += total_diff
            if total_diff > 0:
                wins_a += 1
            elif total_diff < 0:
                wins_b += 1
            else:
                ties += 1
            per_article[article_id] = {"top5_diff": top5_diff, "total_diff": total_diff}
        result[f"{a}_vs_{b}"] = {
            "per_article": per_article,
            "top5_diff_sum": top5_diff_sum,
            "total_diff_sum": total_diff_sum,
            "wins": {a: wins_a, b: wins_b, "ties": ties},
        }
    return result


def reconcile_prior_aggregate(article_set_agg: dict) -> dict:
    result = {}
    for article_id, sets in PRIOR_AGGREGATE_IMAGE.items():
        result[article_id] = {}
        for set_label, prior_value in sets.items():
            recalculated = article_set_agg[(article_id, set_label)]["total_score"]
            result[article_id][set_label] = {
                "prior": prior_value, "recalculated": recalculated, "delta": recalculated - prior_value,
            }
    return result


def extract_qa_fails(normalized: list) -> list:
    return [r for r in normalized if r["extraction_form_qa_verdict"] == "FAIL"]


def compute_verdict_label(cross_article: dict, rank1_info: dict) -> dict:
    """N=3のため統計的有意差は主張しない。数値の目安(top5_total合計の
    差、記事別勝利数)だけに基づく参考ラベルを返す。最終採用はユーザーが
    決める。"""
    ranked = sorted(cross_article.items(), key=lambda kv: -kv[1]["top5_total"])
    best_id, best = ranked[0]
    second_id, second = ranked[1]
    gap = best["top5_total"] - second["top5_total"]
    best_wins_articles = len(
        [a for a, winners in rank1_info["winner_by_article"].items() if winners == [best_id]])

    also_leads_total = best["total_total"] == max(s["total_total"] for s in cross_article.values())

    if best_wins_articles == 3 and also_leads_total and gap >= 3:
        label = "CLEAR_LEADER"
    elif best_wins_articles >= 2 and also_leads_total and gap >= 1:
        label = "NARROW_LEADER"
    elif gap <= 1:
        label = "INCONCLUSIVE"
    else:
        label = "MIXED_BY_ARTICLE"

    return {
        "label": label,
        "leader_strategy_id": best_id,
        "leader_top5_total": best["top5_total"],
        "runner_up_strategy_id": second_id,
        "runner_up_top5_total": second["top5_total"],
        "top5_total_gap": gap,
        "leader_wins_all_three_articles": best_wins_articles == 3,
        "leader_also_leads_total_total": also_leads_total,
    }


# ============================================================
# 保存
# ============================================================
def save_json(path: str, data) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_normalized_csv(path: str, normalized: list) -> None:
    fieldnames = list(normalized[0].keys()) if normalized else []
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in normalized:
            writer.writerow(row)


# ============================================================
# レポート生成(pure functions。ファイルI/Oはmain側で行う)
# ============================================================
def build_prior_reconciliation_markdown(prior_result: dict) -> str:
    lines = ["# ER-003-P2H 以前の集計画像との照合", "",
             "以前の画像集計は監査用に保持し、正式値は今回の詳細行(90件)からPythonで再計算した値とする。", "",
             "| 記事 | Set | 以前の画像 | 再計算値 | 差分 |", "|---|---|---:|---:|---:|"]
    for article_id in ARTICLE_IDS:
        for set_label in SET_LABELS:
            r = prior_result[article_id][set_label]
            lines.append(f"| {article_id} | {set_label} | {r['prior']} | {r['recalculated']} | {r['delta']:+d} |")
    lines.append("")
    return "\n".join(lines)


def build_qa_fail_review_markdown(qa_fails: list) -> str:
    lines = ["# ER-003-P2H Extraction Form QA FAIL 2件の詳細", "",
             "P2Gの`88 PASS / 2 FAIL`のうち、FAILとなった2件を記録する。項目・score・P2G成果物は変更していない。",
             ""]
    for i, r in enumerate(qa_fails, start=1):
        lines.append(f"## FAIL {i}: {r['article_id']} / Set {r['blind_set']} (方式{r['strategy_id']}) / Rank {r['rank']}")
        lines.append("")
        lines.append(f"- phrase: {r['canonical_phrase']}")
        lines.append(f"- source_span: {r['source_span']}")
        lines.append(f"- source_sentence: {r['source_sentence']}")
        lines.append(f"- 日本語グロス: {r['canonical_gloss']}")
        lines.append(f"- Extraction Form QA notes: {r['extraction_form_qa_notes']}")
        lines.append(f"- ユーザー評価: {r['rating_symbol']}(score={r['score']})")
        lines.append("- 方式比較への影響: 該当項目は他のQA PASS項目と同様に集計へ含めている"
                     "(QA結果を理由とした除外・再生成は行っていない)。")
        lines.append("")
    return "\n".join(lines)


def build_strategy_score_analysis_markdown(
    art_set: dict, art_strat: dict, cross: dict, rank1: dict, rank_avg: dict,
    pairwise: dict, prior: dict, verdict: dict, qa_fails: list,
) -> str:
    lines = ["# ER-003-P2H 方式スコア分析", "", "## 1. 評価方法",
             "", "〇=2点、△=1点、×=0点。Top5(rank1-5、製品採用候補層)とRank6-10(取りこぼし確認層)を分離して集計する。"
             "N=3記事のため統計的有意差は主張しない。", ""]

    lines.append("## 2. mapping")
    lines.append("")
    lines.append("ユーザー評価完了後のため、記事別Set→方式の対応を開示する。")
    lines.append("")
    for article_id in ARTICLE_IDS:
        mapping = load_blind_mapping(article_id)
        lines.append(f"- {article_id}: " + ", ".join(f"{k}={v}" for k, v in mapping.items()))
    lines.append("")

    lines.append("## 3. 以前の集計画像との差分")
    lines.append("")
    lines.append("(詳細は`ER-003-P2H_prior_aggregate_reconciliation.md`を参照)")
    lines.append("")
    for article_id in ARTICLE_IDS:
        deltas = [f"{s}:{prior[article_id][s]['delta']:+d}" for s in SET_LABELS]
        lines.append(f"- {article_id}: " + ", ".join(deltas))
    lines.append("")

    lines.append("## 4. 記事別Set集計")
    lines.append("")
    lines.append("| 記事 | Set | Top5 | Rank6-10 | Total | 〇/△/× | ranking_lift |")
    lines.append("|---|---|---:|---:|---:|---|---:|")
    for article_id in ARTICLE_IDS:
        for set_label in SET_LABELS:
            s = art_set[(article_id, set_label)]
            c = s["counts"]
            lines.append(f"| {article_id} | {set_label} | {s['top5_score']} | {s['rank6_10_score']} | "
                         f"{s['total_score']} | {c['〇']}/{c['△']}/{c['×']} | {s['ranking_lift']} |")
    lines.append("")

    lines.append("## 5. 記事別L/P/U集計")
    lines.append("")
    lines.append("| 記事 | 方式 | Top5 | Rank6-10 | Total | 〇/△/× | ranking_lift |")
    lines.append("|---|---|---:|---:|---:|---|---:|")
    for article_id in ARTICLE_IDS:
        for strategy_id in STRATEGY_IDS:
            s = art_strat[(article_id, strategy_id)]
            c = s["counts"]
            lines.append(f"| {article_id} | {strategy_id} | {s['top5_score']} | {s['rank6_10_score']} | "
                         f"{s['total_score']} | {c['〇']}/{c['△']}/{c['×']} | {s['ranking_lift']} |")
    lines.append("")

    lines.append("## 6. Top5比較(3記事合計、最大30)")
    lines.append("")
    lines.append("| 方式 | Top5合計 |")
    lines.append("|---|---:|")
    for strategy_id in STRATEGY_IDS:
        lines.append(f"| {strategy_id} | {cross[strategy_id]['top5_total']} |")
    lines.append("")

    lines.append("## 7. Rank6-10比較(3記事合計、最大30)")
    lines.append("")
    lines.append("| 方式 | Rank6-10合計 |")
    lines.append("|---|---:|")
    for strategy_id in STRATEGY_IDS:
        lines.append(f"| {strategy_id} | {cross[strategy_id]['rank6_10_total']} |")
    lines.append("")

    lines.append("## 8. Total比較(3記事合計、最大60)")
    lines.append("")
    lines.append("| 方式 | Total合計 | 平均/記事 | 中央値 | min | max | 標準偏差 | 〇/△/× |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---|")
    for strategy_id in STRATEGY_IDS:
        s = cross[strategy_id]
        c = s["counts"]
        lines.append(f"| {strategy_id} | {s['total_total']} | {s['mean_total_per_article']} | "
                     f"{s['median_total_per_article']} | {s['min_total_per_article']} | "
                     f"{s['max_total_per_article']} | {s['stdev_total_per_article']} | {c['〇']}/{c['△']}/{c['×']} |")
    lines.append("")

    lines.append("## 9. ranking_lift")
    lines.append("")
    lines.append("| 方式 | ranking_lift平均(3記事) |")
    lines.append("|---|---:|")
    for strategy_id in STRATEGY_IDS:
        lines.append(f"| {strategy_id} | {cross[strategy_id]['ranking_lift_mean']} |")
    lines.append("")

    lines.append("## 10. Rank別平均score(3記事平均)")
    lines.append("")
    lines.append("| Rank | L | P | U |")
    lines.append("|---:|---:|---:|---:|")
    for rank in RANKS:
        lines.append(f"| {rank} | {rank_avg['L'][rank]} | {rank_avg['P'][rank]} | {rank_avg['U'][rank]} |")
    lines.append("")

    lines.append("## 11. pairwise比較")
    lines.append("")
    for pair_key, pair in pairwise.items():
        a, b = pair_key.split("_vs_")
        lines.append(f"### {a} vs {b}")
        lines.append("")
        lines.append(f"- 記事別total_diff({a}-{b}): "
                     + ", ".join(f"{art}:{d['total_diff']:+d}" for art, d in pair["per_article"].items()))
        lines.append(f"- 記事別top5_diff({a}-{b}): "
                     + ", ".join(f"{art}:{d['top5_diff']:+d}" for art, d in pair["per_article"].items()))
        lines.append(f"- 3記事合計total_diff: {pair['total_diff_sum']:+d} / 3記事合計top5_diff: "
                     f"{pair['top5_diff_sum']:+d}")
        lines.append(f"- 勝敗(total_score基準): {pair['wins']}")
        lines.append("")

    lines.append("## 12. QA FAIL 2件")
    lines.append("")
    lines.append("(詳細は`ER-003-P2H_extraction_qa_fail_review.md`を参照)")
    lines.append("")
    for r in qa_fails:
        lines.append(f"- {r['article_id']} / {r['strategy_id']} / Rank {r['rank']}: "
                     f"{r['canonical_phrase']}(評価: {r['rating_symbol']})")
    lines.append("")

    lines.append("## 13. 解釈")
    lines.append("")
    lines.append(f"- 記事内1位(total_score基準)回数: " + ", ".join(
        f"{sid}:{cnt}" for sid, cnt in rank1["rank1_counts"].items()))
    lines.append(f"- 同率1位が生じた記事: {rank1['tie_articles'] or 'なし'}")
    lines.append(f"- Top5合計トップ: {verdict['leader_strategy_id']}({verdict['leader_top5_total']}) "
                 f"/ 僅差: {verdict['runner_up_strategy_id']}({verdict['runner_up_top5_total']}) "
                 f"/ 差: {verdict['top5_total_gap']}")
    lines.append("")

    lines.append("## 14. 限界")
    lines.append("")
    lines.append("- N=3記事のため統計的有意差は主張しない。")
    lines.append("- ユーザー評価はSet単位のブラインド評価であり、方式そのものへの先入観は排除されているが、"
                 "記事ジャンル(スポーツ/社会生活/国際市場)による方式適性の一般化はこの3記事だけでは限定的。")
    lines.append("- Extraction Form QAは形式・忠実性のみのチェックであり、内容の面白さ・自然さは評価していない。")
    lines.append("")

    lines.append("## 15. 次の意思決定候補")
    lines.append("")
    lines.append(f"- 参考ラベル: **{verdict['label']}**"
                 f"(leader={verdict['leader_strategy_id']}, gap={verdict['top5_total_gap']}, "
                 f"3記事とも単独勝利={verdict['leader_wins_all_three_articles']}, "
                 f"Total_totalでも先頭={verdict['leader_also_leads_total_total']})")
    lines.append("- 最終採用はユーザーが決定する。上記の集計・pairwise・QA FAIL詳細を踏まえてご判断ください。")
    lines.append("")

    return "\n".join(lines)
