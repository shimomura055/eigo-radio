# ============================================================
# er016_rerank_eval_01.py
# TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01 評価script
# ============================================================
# 目的: ユーザーが `USER_EVAL_RERANK_POOL.md` へ実際に1-10で評価した後、
# 各モデル(arms/{L,T,S,J}/predictions.json)について
#   - Pearson相関 / Spearman相関 (predicted_score vs user_score)
#   - Top20内のユーザー5点以上率
#   - Top10内のユーザー5点以上率
#   - ユーザー7点以上のRecall(そのモデルのTop20に何%含められたか)
#   - Top20内でユーザー3点以下だった件数(明らかな低評価Topicを上位に
#     置いた数)
# を計算し、md出力する。
#
# 重要: モデル自身のpredicted_scoreだけで勝敗を決めない設計。本scriptは
# ユーザーが実際に評価した後にのみ意味のある比較を行う。
#
# --dry-run: predictions.jsonが存在しない場合でも、score計算ロジック自体
# の動作確認用にダミー(定数シード乱数)predicted_scoreで動かす。dry-run結果
# はTrial評価として扱わない(検証専用)。
# ============================================================
from __future__ import annotations

import argparse
import json
import os
import random
from statistics import mean


def load_json(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_text(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def pearson(xs, ys):
    n = len(xs)
    if n < 2:
        return None
    mx, my = mean(xs), mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    denx = sum((x - mx) ** 2 for x in xs) ** 0.5
    deny = sum((y - my) ** 2 for y in ys) ** 0.5
    if denx == 0 or deny == 0:
        return None
    return num / (denx * deny)


def rank(values):
    # 平均順位法でtie処理
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        avg_rank = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[order[k]] = avg_rank
        i = j + 1
    return ranks


def spearman(xs, ys):
    if len(xs) < 2:
        return None
    rx = rank(xs)
    ry = rank(ys)
    return pearson(rx, ry)


def evaluate_arm(predictions, user_scores):
    """predictions: [{id, predicted_score}], user_scores: {id: score}"""
    paired = [(p["id"], p["predicted_score"], user_scores[p["id"]])
              for p in predictions if p["id"] in user_scores]
    if not paired:
        return {"n_paired": 0}
    ids = [p[0] for p in paired]
    preds = [p[1] for p in paired]
    users = [p[2] for p in paired]

    ranked = sorted(paired, key=lambda t: t[1], reverse=True)
    top20 = ranked[:20]
    top10 = ranked[:10]
    all_ge7 = [t for t in paired if t[2] >= 7]

    top20_ge5 = sum(1 for t in top20 if t[2] >= 5)
    top10_ge5 = sum(1 for t in top10 if t[2] >= 5)
    top20_ids = {t[0] for t in top20}
    recall7 = (
        sum(1 for t in all_ge7 if t[0] in top20_ids) / len(all_ge7)
        if all_ge7 else None
    )
    top20_le3 = sum(1 for t in top20 if t[2] <= 3)

    return {
        "n_paired": len(paired),
        "pearson": pearson(preds, users),
        "spearman": spearman(preds, users),
        "top20_ge5_rate": top20_ge5 / len(top20) if top20 else None,
        "top10_ge5_rate": top10_ge5 / len(top10) if top10 else None,
        "user_ge7_count": len(all_ge7),
        "recall_ge7_in_top20": recall7,
        "top20_le3_count": top20_le3,
    }


def load_predictions(out_dir, arm):
    path = os.path.join(out_dir, "arms", arm, "predictions.json")
    if not os.path.exists(path):
        return None
    return load_json(path)


def dummy_predictions(pool_ids, seed):
    rnd = random.Random(seed)
    return [{"id": i, "predicted_score": rnd.randint(1, 10), "reason": "DUMMY"}
            for i in pool_ids]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--user-scores", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    pool_path = os.path.join(args.out_dir, "candidate_pool.json")
    pool = load_json(pool_path)
    pool_ids = [c["id"] for c in pool]

    if args.dry_run and not os.path.exists(args.user_scores):
        # dry-run用ダミーuser_scoresも生成(存在しなければ)
        dummy_users = {i: random.Random(hash(i)).randint(1, 10) for i in pool_ids}
        save_text(args.user_scores, "")
        with open(args.user_scores, "w", encoding="utf-8") as f:
            json.dump(dummy_users, f, ensure_ascii=False, indent=2)

    user_scores = load_json(args.user_scores)

    arms = ["L", "T", "S", "J"]
    results = {}
    for i, arm in enumerate(arms):
        preds = load_predictions(args.out_dir, arm)
        if preds is None:
            if args.dry_run:
                preds = dummy_predictions(pool_ids, seed=1000 + i)
            else:
                results[arm] = {"status": "NO_PREDICTIONS_FILE"}
                continue
        results[arm] = evaluate_arm(preds, user_scores)

    lines = ["# model_agreement / rerank eval results", ""]
    if args.dry_run:
        lines.append("**DRY-RUN(ダミーpredicted_score/user_scoreによる動作確認"
                      "専用。Trial評価として扱わない)**")
        lines.append("")
    lines.append("| Arm | n_paired | Pearson | Spearman | Top20>=5率 | "
                  "Top10>=5率 | user>=7件数 | Recall(>=7 in Top20) | "
                  "Top20内<=3件数 |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for arm in arms:
        r = results.get(arm, {})
        if r.get("status") == "NO_PREDICTIONS_FILE":
            lines.append(f"| {arm} | - | - | - | - | - | - | - | - (predictions未生成) |")
            continue
        lines.append(
            f"| {arm} | {r.get('n_paired')} | "
            f"{r.get('pearson'):.3f} | {r.get('spearman'):.3f} | "
            f"{r.get('top20_ge5_rate'):.2f} | {r.get('top10_ge5_rate'):.2f} | "
            f"{r.get('user_ge7_count')} | "
            f"{r.get('recall_ge7_in_top20') if r.get('recall_ge7_in_top20') is None else round(r.get('recall_ge7_in_top20'),2)} | "
            f"{r.get('top20_le3_count')} |"
        )

    out_md = os.path.join(args.out_dir, "eval_results.md" if not args.dry_run
                           else "eval_results_DRYRUN.md")
    save_text(out_md, "\n".join(lines) + "\n")
    out_json = out_md.replace(".md", ".json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"[OK] eval written: {out_md}")


if __name__ == "__main__":
    main()
