# ============================================================
# er016_topic_discovery_eval_01.py
# TOPIC-DISCOVERY-ANGLE-INTEGRATED-3WAY-TRIAL-01(Fable/ユーザー設計、
# 2026-09-25)
# ============================================================
# 目的: USER_EVAL_TOPIC_DISCOVERY_3WAY.md へのユーザー評価(○/△/×)を
# blind_map.jsonで各モデルへ復元し、モデル別 ○率/○+△率/×率/Top10重複
# (統合グループのサイズ)/独自候補(他モデルに無いseed)のHit率(○) を
# 算出する。Production実装ではない。
#
# 本Trialは3-way実行がcost_estimate.jsonの時点でSTOP(¥200超過見込み)と
# なったため、実データでのTop10/blind_map/user_evalは存在しない。本
# ファイルは委任文の要求どおり --dry-run でのみ動作確認する。--dry-run
# 時、out_dir配下にblind_map.jsonが無ければ、3アーム×少数件のダミー
# blind_map/topic_packagesを合成し、集計ロジックのみを検証する
# (実データではない。ダミーと明記する)。
#
# 使い方:
#   python er016_topic_discovery_eval_01.py --out-dir <dir> \
#       --user-eval <path> --dry-run
# ============================================================
from __future__ import annotations

import argparse
import json
import os

ARM_ORDER = ["L", "S", "T"]


def out_path(out_dir: str, *parts: str) -> str:
    return os.path.join(out_dir, *parts)


def save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def load_json(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ------------------------------------------------------------
# ダミーデータ生成(--dry-run かつ blind_map.json が無い場合のみ)。
# 3アーム × 4件(うち1グループはL×Sで統合=重複あり、1件はTのみ独自)。
# DUMMY値であることをファイル名・中身双方に明記する。
# ------------------------------------------------------------
def _generate_dummy(out_dir: str):
    blind_map_dummy = {
        "1": {"arms": ["L", "S"], "packages": [{"arm": "L", "index": 0},
                                                 {"arm": "S", "index": 0}]},
        "2": {"arms": ["L"], "packages": [{"arm": "L", "index": 1}]},
        "3": {"arms": ["S"], "packages": [{"arm": "S", "index": 1}]},
        "4": {"arms": ["T"], "packages": [{"arm": "T", "index": 0}]},
        "5": {"arms": ["T", "S"], "packages": [{"arm": "T", "index": 1},
                                                {"arm": "S", "index": 2}]},
        "6": {"arms": ["L"], "packages": [{"arm": "L", "index": 2}]},
    }
    blind_map_path = out_path(out_dir, "blind_map_DUMMY_generated.json")
    save_json(blind_map_path, blind_map_dummy)

    user_eval_dummy = {
        "1": "○", "2": "△", "3": "×", "4": "○", "5": "○", "6": "×",
        "_note": "DUMMY(dry-run動作確認用、実ユーザー評価ではない)",
    }
    user_eval_path = out_path(out_dir, "user_eval_DUMMY.json")
    if not os.path.exists(user_eval_path):
        save_json(user_eval_path, user_eval_dummy)
    return blind_map_path, user_eval_path


# ------------------------------------------------------------
# 集計ロジック
# ------------------------------------------------------------
def _rating_value(v):
    return v in ("○", "○(採用したい)")


def _partial_or_better(v):
    return v in ("○", "△", "○(採用したい)", "△(どちらとも)")


def compute_eval(blind_map: dict, user_eval: dict) -> dict:
    per_model = {arm: {"total_appearances": 0, "circle": 0, "circle_or_triangle": 0,
                        "cross": 0, "merged_group_count": 0,
                        "unique_total": 0, "unique_circle": 0}
                 for arm in ARM_ORDER}

    for no, entry in blind_map.items():
        rating = user_eval.get(str(no)) or user_eval.get(no)
        arms_here = entry.get("arms", [])
        is_merged = len(entry.get("packages", [])) > 1
        for arm in set(arms_here):
            if arm not in per_model:
                continue
            per_model[arm]["total_appearances"] += 1
            if is_merged:
                per_model[arm]["merged_group_count"] += 1
            else:
                per_model[arm]["unique_total"] += 1
            if rating is not None:
                if _rating_value(rating):
                    per_model[arm]["circle"] += 1
                    if not is_merged:
                        per_model[arm]["unique_circle"] += 1
                if _partial_or_better(rating):
                    per_model[arm]["circle_or_triangle"] += 1
                if rating in ("×",):
                    per_model[arm]["cross"] += 1

    result = {}
    for arm, s in per_model.items():
        total = s["total_appearances"]
        result[arm] = {
            **s,
            "circle_rate": round(s["circle"] / total, 3) if total else None,
            "circle_or_triangle_rate": round(s["circle_or_triangle"] / total, 3) if total else None,
            "cross_rate": round(s["cross"] / total, 3) if total else None,
            "unique_candidate_hit_rate": round(s["unique_circle"] / s["unique_total"], 3)
            if s["unique_total"] else None,
        }
    return result


def cmd_eval(args):
    out_dir = args.out_dir
    blind_map_path = out_path(out_dir, "blind_map.json")
    is_dummy = False
    if args.dry_run and not os.path.exists(blind_map_path):
        blind_map_path, generated_user_eval_path = _generate_dummy(out_dir)
        is_dummy = True
        print(f"[DUMMY] blind_map.jsonが無いためダミーを生成: {blind_map_path}")
        if not args.user_eval:
            args.user_eval = generated_user_eval_path

    blind_map = load_json(blind_map_path)
    user_eval = load_json(args.user_eval)

    result = compute_eval(blind_map, user_eval)
    output = {
        "dry_run": bool(args.dry_run),
        "is_dummy_data": is_dummy,
        "blind_map_path_used": blind_map_path,
        "user_eval_path_used": args.user_eval,
        "per_model": result,
        "note": "is_dummy_data=trueの場合、本結果はロジック動作確認のみで"
                "あり、実際のモデル品質を示すものではない。"
                "TOPIC-DISCOVERY-ANGLE-INTEGRATED-3WAY-TRIAL-01は"
                "cost_estimate.jsonの時点でSTOPしたため、実データは存在しない。",
    }
    save_json(out_path(out_dir, "eval_result.json" if not is_dummy
                        else "eval_result_DUMMY.json"), output)
    print(json.dumps(output, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--user-eval", required=False)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    cmd_eval(args)


if __name__ == "__main__":
    main()
