# ============================================================
# er003_v1_p2c_approve.py
# ER-003-P2C: B2概要のPodcast語り口確定(API呼び出しなし)
# ============================================================
# ER-003-P2Bで生成した3記事の概要(summary_en_reading_copy.md)は変更せず、
# ユーザー承認済みの軽微編集(教材紹介的な"This episode ..."開始を、
# ナレーターとリスナーを含む"We'll look at ..."というPodcast調の開始に
# 置き換える)を適用した確定文面を新規保存する。APIは一切呼ばない。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_p2c_approve.py

from __future__ import annotations

import difflib
import json
import os

import er003_b2_summary as s
import er003_ja_to_en_translation as er003

OUTPUT_ROOT = "er003_output/p2b"

# ユーザー(プロジェクト責任者)が承認した確定文面。Claude Codeが内容を
# 作文したものではなく、指示された文面をそのまま保存する。
APPROVED_SUMMARIES = {
    "A01": (
        "## Before You Listen\n\n"
        "We'll look at a tense World Cup match between England and Argentina, with a place in the final at stake. "
        "As you listen, notice how late decisions and key players shape the game."
    ),
    "A02": (
        "## Before You Listen\n\n"
        "We'll look at a UK plan to change how social media apps work at night for teenagers. "
        "As you listen, notice how the settings work, why users can change them, and what two studies suggest."
    ),
    "ADD03": (
        "## Before You Listen\n\n"
        "We'll look at how a U.S. plan for ships using the Strait of Hormuz changed and affected oil markets. "
        "As you listen, notice what worried oil markets and shipping companies."
    ),
}

APPROVED_CHANGES = [
    "Replace instructional 'This episode ...' opening with inclusive Podcast-style 'We'll look at ...' opening",
    "Use approved second-sentence wording",
]


def approve_summary(topic_id: str) -> dict:
    out_dir = f"{OUTPUT_ROOT}/{topic_id}"
    source_path = f"{out_dir}/summary_en_reading_copy.md"
    with open(source_path, encoding="utf-8") as f:
        source_text = f.read()
    source_sha256 = er003.sha256_text(source_text)

    approved_text = APPROVED_SUMMARIES[topic_id]

    structure = s.validate_summary_structure(approved_text)
    if structure["status"] != "B2_SUMMARY_STRUCTURE_PASS":
        raise ValueError(f"{topic_id}: 承認済み文面が構造ゲートに合格しません: {structure['reasons']}")
    if not structure["opening_ok"]:
        raise ValueError(f"{topic_id}: 承認済み文面が第一文開始要件を満たしません")

    approved_path = f"{out_dir}/summary_en_approved.md"
    with open(approved_path, "w", encoding="utf-8") as f:
        f.write(approved_text)
    approved_sha256 = er003.sha256_text(approved_text)
    with open(f"{out_dir}/summary_approved_sha256.txt", "w", encoding="utf-8") as f:
        f.write(approved_sha256)

    approval = {
        "article_id": topic_id,
        "decision_id": "ER-003-P2C",
        "source_generated_summary_path": source_path,
        "source_generated_summary_sha256": source_sha256,
        "approved_summary_path": approved_path,
        "approved_summary_sha256": approved_sha256,
        "approval_type": "USER_APPROVED_LIGHT_EDIT",
        "approved_changes": APPROVED_CHANGES,
        "api_regeneration": False,
        "post_approval_llm_rewrite": False,
    }
    with open(f"{out_dir}/summary_approval.json", "w", encoding="utf-8") as f:
        json.dump(approval, f, ensure_ascii=False, indent=2)

    metrics = s.compute_summary_metrics(approved_text)
    metrics["opening_ok"] = structure["opening_ok"]
    metrics["structure_status"] = structure["status"]
    with open(f"{out_dir}/summary_approved_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    diff_lines = list(difflib.unified_diff(
        source_text.splitlines(keepends=True), approved_text.splitlines(keepends=True),
        fromfile="summary_en_reading_copy.md", tofile="summary_en_approved.md",
    ))
    with open(f"{out_dir}/summary_approved_diff.txt", "w", encoding="utf-8") as f:
        f.writelines(diff_lines)

    return {
        "topic_id": topic_id, "source_sha256": source_sha256, "approved_sha256": approved_sha256,
        "metrics": metrics, "diff": "".join(diff_lines),
    }


if __name__ == "__main__":
    results = {}
    for topic_id in ("A01", "A02", "ADD03"):
        results[topic_id] = approve_summary(topic_id)
        print(f"{topic_id}: approved (sha256={results[topic_id]['approved_sha256'][:12]}...)")
    with open(os.path.join(OUTPUT_ROOT, "p2c_approval_summary.json"), "w", encoding="utf-8") as f:
        json.dump({k: {kk: vv for kk, vv in v.items() if kk != "diff"} for k, v in results.items()},
                   f, ensure_ascii=False, indent=2)
    print("done.")
