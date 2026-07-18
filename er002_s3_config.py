# ============================================================
# er002_s3_config.py
# ER-002-S3-P0: 本番6記事バッチの構成凍結
# ============================================================
# S3の実行構成(B1/B2/B3の3バッチ、6記事・8話者)と、受入集計から除外する
# 実行(S2のA04・A01/A02の独立再実行)を固定する設定。この工程では実API
# 呼び出しを一切行わない(定義のみ)。

from __future__ import annotations

EXPERIMENT_VERSION = "ER-002-v1.0"

# ============================================================
# バッチ構成: 6記事・8音声(A04/A05はAoede+Charonの2話者=A/B対象)
# ============================================================
S3_BATCHES = {
    "B1": [
        {"article_id": "A01", "genre": "sports", "voices": ["Aoede"], "ab_test": False},
        {"article_id": "A02", "genre": "social_life", "voices": ["Charon"], "ab_test": False},
    ],
    "B2": [
        {"article_id": "A03", "genre": "entertainment", "voices": ["Aoede"], "ab_test": False},
        {"article_id": "A06", "genre": "politics_public", "voices": ["Charon"], "ab_test": False},
    ],
    "B3": [
        {
            "article_id": "A04", "genre": "technology", "voices": ["Aoede", "Charon"], "ab_test": True,
            "note": (
                "ER-002-S2で扱ったA04(Meta Muse Image記事)とは別の新規トピック候補取得・"
                "新規記事選定・新規台本生成を行う。S2の実行結果はS3の受入集計に含めない。"
            ),
        },
        {"article_id": "A05", "genre": "business_consumer", "voices": ["Aoede", "Charon"], "ab_test": True},
    ],
}


def flatten_s3_batches() -> list[dict]:
    """全バッチを1つのリストへ展開する。"""
    flat = []
    for batch_name, articles in S3_BATCHES.items():
        for article in articles:
            flat.append({**article, "batch": batch_name})
    return flat


def total_article_count() -> int:
    return len(flatten_s3_batches())


def total_voice_slot_count() -> int:
    """記事×話者の合計スロット数(A01=1, A02=1, A03=1, A06=1, A04=2, A05=2 → 8)。"""
    return sum(len(a["voices"]) for a in flatten_s3_batches())


# ============================================================
# 独立再実行: A01・A02を同一情報源・同一設定で再実行する(受入集計には含めない)
# ============================================================
INDEPENDENT_RERUNS = [
    {
        "article_id": "A01", "rerun_of": "A01", "genre": "sports",
        "condition": "same_source_same_settings",
        "runs_after": "初回6記事(B1〜B3)の生成完了後",
        "included_in_acceptance_tally": False,
    },
    {
        "article_id": "A02", "rerun_of": "A02", "genre": "social_life",
        "condition": "same_source_same_settings",
        "runs_after": "初回6記事(B1〜B3)の生成完了後",
        "included_in_acceptance_tally": False,
    },
]


# ============================================================
# S3の受入集計から明示的に除外する過去の実行
# ============================================================
EXCLUDED_FROM_S3_ACCEPTANCE_TALLY = [
    {
        "experiment_id": "ER-002-S2",
        "article_id": "A04",
        "commit_hash": "774294570acc4931193d8ca5a05b278f7e5a128a",
        "reason": (
            "S2は実APIフローのスモークテストであり、S3では同じarticle_id=A04で"
            "新規トピック選定・新規台本生成を行う。S2の結果はS3の受入集計に含めない。"
        ),
    },
    {
        "experiment_id": "ER-002-S3",
        "article_id": "A01 (rerun)",
        "reason": "機械的再現性確認用の独立再実行であり、本番6記事の1本としては数えない。",
    },
    {
        "experiment_id": "ER-002-S3",
        "article_id": "A02 (rerun)",
        "reason": "機械的再現性確認用の独立再実行であり、本番6記事の1本としては数えない。",
    },
]


def is_included_in_acceptance_tally(experiment_id: str, article_id: str) -> bool:
    """(experiment_id, article_id)の組がS3の受入集計対象かどうかを判定する。"""
    for excluded in EXCLUDED_FROM_S3_ACCEPTANCE_TALLY:
        if excluded["experiment_id"] == experiment_id and excluded["article_id"] == article_id:
            return False
    return True
