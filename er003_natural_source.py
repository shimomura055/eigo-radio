# ============================================================
# er003_natural_source.py
# ER-003-P2 Part A: Natural English Sourceの確定
# ============================================================
# ER-003-P1B(固定構造付き自然英訳)の出力をユーザーが確認し、A01のみ
# 2つの見出し文言を軽微修正した上で、"Natural English Source"(内部
# 基準原稿)として確定する。P1Bのraw成果物は一切上書きしない。
#
# A02・ADD03はP1B本文をそのままNatural English Sourceとして採用する。

from __future__ import annotations

import hashlib
from typing import Optional

P1B_RAW_ARTICLE_PATHS = {
    "A01": "er003_output/p1b/A01/translated_en_raw.md",
    "A02": "er003_output/p1b/A02/translated_en_raw.md",
    "ADD03": "er003_output/p1b/ADD03/translated_en_raw.md",
}

NATURAL_SOURCE_OUTPUT_DIR = {
    "A01": "er003_output/p1b/A01",
    "A02": "er003_output/p1b/A02",
    "ADD03": "er003_output/p1b/ADD03",
}

# A01のみ、ユーザー承認済みの2見出し軽微修正(本文・タイトル・導入・
# 数字・固有名詞・出来事の順序は一切変更しない)
A01_APPROVED_HEADING_EDITS = [
    {
        "before": "Point One: Messi Wasn't the Scorer—He Was the Finisher",
        "after": "Point One: Messi Wasn't the Scorer—He Was the Creator",
        "reason": "'finisher'は実際に得点を決める選手という意味に聞こえ、直後の本文(得点はしていない)と衝突するため。",
    },
    {
        "before": "Point Two: One Team Substituted to Defend; the Other, to Win",
        "after": "Point Two: One Team Substituted to Defend; the Other, to Attack",
        "reason": "'to win'は元の日本語「攻める交代」より含意が強いため。'to Attack'のほうが日本語原稿との整合性が高い。",
    },
]

# A02・ADD03は変更なし。fidelity QAで指摘された注意事項は
# approval metadataへ記録するだけで、本文の自動修正は行わない。
A02_CARRIED_FORWARD_QA_NOTES = [
    "一部の因果表現(produced等)が日本語より強く聞こえる可能性がある。",
    "自動再生・おすすめフィードが午前0時〜6時に限定されるかどうかの範囲表現に、日本語との解釈上の差がある。",
    "最長文が61語あり、B2調整時には意味を強めず、長文を自然に分割することを検討する。",
]


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_p1b_raw_article(topic_id: str) -> str:
    with open(P1B_RAW_ARTICLE_PATHS[topic_id], encoding="utf-8") as f:
        return f.read()


def build_natural_source_text(topic_id: str, p1b_raw_text: Optional[str] = None) -> str:
    """A01は承認済み2見出しだけを置換する。A02・ADD03はP1B本文と
    byte-for-byte同一のテキストを返す。"""
    text = p1b_raw_text if p1b_raw_text is not None else load_p1b_raw_article(topic_id)
    if topic_id == "A01":
        for edit in A01_APPROVED_HEADING_EDITS:
            if edit["before"] not in text:
                raise ValueError(f"期待する見出しが見つかりません: {edit['before']!r}")
            text = text.replace(edit["before"], edit["after"], 1)
    return text


def build_approval_metadata(topic_id: str, p1b_raw_text: str, natural_source_text: str) -> dict:
    metadata = {
        "topic_id": topic_id,
        "source_raw_path": P1B_RAW_ARTICLE_PATHS[topic_id],
        "p1b_raw_sha256": sha256_text(p1b_raw_text),
        "natural_source_sha256": sha256_text(natural_source_text),
        "edits": A01_APPROVED_HEADING_EDITS if topic_id == "A01" else [],
        "identical_to_p1b_raw": natural_source_text == p1b_raw_text,
    }
    if topic_id == "A02":
        metadata["qa_notes_carried_forward"] = A02_CARRIED_FORWARD_QA_NOTES
    if topic_id in ("A01", "A02"):
        metadata["legacy_run_note"] = (
            "ATTEMPT_1_BODY_NOT_PRESERVED_IN_LEGACY_P1B_RUN: "
            "このP1B実行では初回構造ゲート不合格となった1回目の本文を保存していなかった"
            "(保存仕様の改善はER-003-P2以降の実行にのみ適用される)。"
        )
    return metadata
