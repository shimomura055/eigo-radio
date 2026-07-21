# ============================================================
# er003_v1_p2i_approve.py
# ER-003-P2I: B2 Key Words選定方式Lの正式採用・3記事のApproved化
# ============================================================
# ER-003-P2Gで生成・検証済みの各記事L方式(Listening Blocker Ranking)
# Rank 1〜5を、API再実行なしで正式candidateへ昇格する。項目の差し替え・
# 日本語グロスの手修正は一切行わない。P2G成果物は変更しない。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_p2i_approve.py

from __future__ import annotations

import json
import os

import er003_b2_key_words as p2d
import er003_ja_to_en_translation as er003

P2G_ROOT = "er003_output/p2g"
P2I_ROOT = "er003_output/p2i"
ARTICLE_IDS = ("A01", "A02", "ADD03")
PRODUCTION_ITEM_COUNT = 5
SELECTED_STRATEGY = "L"
SELECTED_STRATEGY_NAME = "Listening Blocker Ranking"

ADOPTION_RATIONALE = (
    "製品仕様で使用するTop 5の評価はLとUが同点であり、ユーザーの定性的比較でも明確な優劣はなかった。"
    "そのうえでLは、個別学習者プロファイルへの依存がなく、"
    "「初回リスニングで理解を止める可能性が高い表現を選ぶ」という単純で説明可能な原則を持つため、標準方式として採用する。"
)


class CanonicalMismatchError(ValueError):
    """P2G canonical成果物との不一致(勝手に修正せず停止する)。"""


def load_blind_mapping(article_id: str) -> dict:
    with open(f"{P2G_ROOT}/{article_id}/blind_mapping.json", encoding="utf-8") as f:
        return json.load(f)


def load_l_selection(article_id: str) -> tuple:
    """記事のblind mappingからL方式のSetラベルを特定し、P2G canonical
    selectionを読み込む。mappingはファイルから読み、推測しない。"""
    mapping = load_blind_mapping(article_id)
    l_set_label = next((label for label, sid in mapping.items() if sid == SELECTED_STRATEGY), None)
    if l_set_label is None:
        raise CanonicalMismatchError(f"{article_id}: blind_mappingにL方式が見つかりません")
    path = f"{P2G_ROOT}/{article_id}/{SELECTED_STRATEGY}/key_words_selection.json"
    with open(path, encoding="utf-8") as f:
        raw_text = f.read()
    return json.loads(raw_text), path, er003.sha256_text(raw_text), l_set_label


def load_form_qa_for_item(article_id: str, rank: int) -> dict:
    with open(f"{P2G_ROOT}/{article_id}/form_qa.json", encoding="utf-8") as f:
        form_qa = json.load(f)
    qa_result = form_qa["parsed_result"]
    qa_set = next((s for s in qa_result["sets"] if s["runtime_strategy_id"] == SELECTED_STRATEGY), None)
    if qa_set is None:
        return {}
    return next((it for it in qa_set["items"] if it["rank"] == rank), {})


def build_approved(article_id: str) -> dict:
    selection, source_path, source_sha256, l_set_label = load_l_selection(article_id)

    top5_items = sorted([it for it in selection["items"] if it["rank"] <= 5], key=lambda it: it["rank"])
    if len(top5_items) != PRODUCTION_ITEM_COUNT:
        raise CanonicalMismatchError(
            f"{article_id}: L方式のRank1-5が{PRODUCTION_ITEM_COUNT}件でありません(実際: {len(top5_items)}件)")

    items = []
    for item in top5_items:
        qa = load_form_qa_for_item(article_id, item["rank"])
        approved_item = dict(item)
        approved_item["p2g_extraction_form_qa"] = {
            "form_verdict": qa.get("form_verdict"),
            "minimal_unit": qa.get("minimal_unit"),
            "not_a_clause": qa.get("not_a_clause"),
            "canonical_form": qa.get("canonical_form"),
            "source_fidelity": qa.get("source_fidelity"),
            "gloss_match": qa.get("gloss_match"),
            "notes": qa.get("notes"),
        }
        items.append(approved_item)

    approved = {
        "article_id": article_id,
        "decision_id": "ER-003-P2I",
        "selection_strategy": SELECTED_STRATEGY,
        "selection_strategy_name": SELECTED_STRATEGY_NAME,
        "production_item_count": PRODUCTION_ITEM_COUNT,
        "source_experiment": "ER-003-P2G",
        "source_strategy_result_path": source_path,
        "source_strategy_result_sha256": source_sha256,
        "source_blind_set_label": l_set_label,
        "source_ranks": [it["rank"] for it in top5_items],
        "items": items,
        "api_regeneration": False,
        "manual_item_replacement": False,
        "manual_gloss_edit": False,
    }
    return approved


def build_approval_metadata(article_id: str, approved: dict) -> dict:
    return {
        "decision_id": "ER-003-P2I",
        "article_id": article_id,
        "user_decision": "ADOPT_STRATEGY_L_AS_STANDARD",
        "adoption_rationale": ADOPTION_RATIONALE,
        "score_record": {
            "top5_total_max_30": {"L": 24, "U": 24, "P": 22},
            "total_max_60": {"L": 46, "U": 48, "P": 33},
            "note": "Top5(製品採用範囲)はL/Uが同点。Total(Rank1-10全体)はUがLを2点上回る。"
                   "Lの採用はスコアでの勝利ではなく、Top5同点後のtie-breakとして記録する。",
        },
        "strategy_u_disposition": "NOT_ADOPTED_RETAINED_AS_FUTURE_PERSONALIZATION_CANDIDATE",
        "strategy_p_disposition": "EXCLUDED_FROM_STANDARD_CANDIDATES",
        "api_regeneration": False,
        "item_replacement": False,
        "gloss_manual_edit": False,
        "production_item_count_unchanged": PRODUCTION_ITEM_COUNT,
        "source_strategy_result_path": approved["source_strategy_result_path"],
        "source_strategy_result_sha256": approved["source_strategy_result_sha256"],
        "approved_items_sha256": None,  # approve_article()で確定後に埋める
    }


def build_reading_copy(items: list) -> str:
    """検証済みのP2G canonical Top5から決定的に構成する。rankフィールド
    をorder名へ読み替えるだけの薄いアダプタで、実際の構築ロジックは
    P2Dのbuild_key_words_reading_copyをそのまま再利用する。"""
    adapted_items = [{**item, "order": item["rank"]} for item in items]
    return p2d.build_key_words_reading_copy(adapted_items)


def approve_article(article_id: str) -> dict:
    approved = build_approved(article_id)

    out_dir = f"{P2I_ROOT}/{article_id}"
    os.makedirs(out_dir, exist_ok=True)

    approved_path = f"{out_dir}/key_words_approved.json"
    with open(approved_path, "w", encoding="utf-8") as f:
        json.dump(approved, f, ensure_ascii=False, indent=2)
    with open(approved_path, encoding="utf-8") as f:
        approved_sha256 = er003.sha256_text(f.read())
    with open(f"{out_dir}/key_words_approved_sha256.txt", "w", encoding="utf-8") as f:
        f.write(approved_sha256)

    reading_copy = build_reading_copy(approved["items"])
    with open(f"{out_dir}/key_words_approved_reading_copy.md", "w", encoding="utf-8") as f:
        f.write(reading_copy)

    approval = build_approval_metadata(article_id, approved)
    approval["approved_items_sha256"] = approved_sha256
    with open(f"{out_dir}/key_words_approval.json", "w", encoding="utf-8") as f:
        json.dump(approval, f, ensure_ascii=False, indent=2)

    return {
        "article_id": article_id, "approved_path": approved_path, "approved_sha256": approved_sha256,
        "items": [{"rank": it["rank"], "display_phrase": it["display_phrase"], "ja_gloss": it["ja_gloss"]}
                  for it in approved["items"]],
    }


if __name__ == "__main__":
    results = {}
    for article_id in ARTICLE_IDS:
        results[article_id] = approve_article(article_id)
        print(f"{article_id}: approved (sha256={results[article_id]['approved_sha256'][:12]}...)")

    with open(f"{P2I_ROOT}/p2i_approval_summary.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("done.")
