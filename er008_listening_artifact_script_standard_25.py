# ============================================================
# er008_listening_artifact_script_standard_25.py
# ER-008-N8-CLOSEOUT-GOVERNANCE-25 (5): 今後ユーザーへ提示する試聴Artifactは、
# 実際に放送される全script(スピーチ本文を持つ全segment)を同じページへ全文
# 掲載することを標準仕様とする。この一覧はer003_v1_n3_01_assemble.pyの
# build_a2_timeline()/build_b1_timeline()が実際に組み立てるsegment順序を
# そのまま反映しており(架空の一覧ではない)、今後の試聴Artifact生成script は
# check_full_script_coverage() で欠落が無いことを確認してから公開すること。
#
# スコープ外(スクリプト本文を持たないためチェック対象にしない): Intro/Outro
# ジングル、Notification/Point Notificationの効果音、silence pause。これらは
# 「script」ではなく音のみのため掲載義務が無い(user要求の「script全文」の対象外)。
# ============================================================
from __future__ import annotations

# 各要素: (segment_key, 表示ラベル, スクリプト本文を持つか)
A2_REQUIRED_SEGMENTS = [
    ("welcome", "Welcome", True),
    ("topic_intro", "Topic Intro", True),
    ("japanese_title", "Japanese Title (A2)", True),
    ("preview_intro", "Preview Intro", True),
    ("point_explanation", "Point Explanation", True),
    ("preview", "Preview", True),
    ("key_phrases_intro", "Key Phrases Intro", True),
    ("key_phrase_en", "Key Phrase (English, 全件)", True),
    ("key_phrase_ja", "Key Phrase (Japanese gloss, 全件)", True),
    ("full_story_intro", "Full Story Intro", True),
    ("comment_1", "Comment 1", True),
    ("full_story_part1", "Full Story Part 1", True),
    ("comment_2", "Comment 2", True),
    ("full_story_part2", "Full Story Part 2", True),
    ("comment_3", "Comment 3", True),
    ("point_one_heading", "Point One Heading", True),
    ("point_one", "Point One", True),
    ("point_two_heading", "Point Two Heading", True),
    ("point_two", "Point Two", True),
    ("comment_4", "Comment 4", True),
    ("in_one_line", "In One Line", True),
]

# B1にはJapanese title segment・Point explanation segmentが存在しない
# (build_b1_timeline()に対応するparts参照が無いことを確認済み)。
B1_REQUIRED_SEGMENTS = [
    ("welcome", "Welcome (Charon)", True),
    ("topic_intro", "Topic Intro (Charon)", True),
    ("preview_intro", "Preview Intro (Charon)", True),
    ("preview", "Preview (Charon)", True),
    ("key_phrases_intro", "Key Phrases Intro (Charon)", True),
    ("key_phrase_en", "Key Phrase (English, 全件)", True),
    ("key_phrase_ja", "Key Phrase (Japanese gloss, 全件)", True),
    ("full_story_intro", "Full Story Intro (Charon)", True),
    ("comment_1", "Comment 1 (Charon)", True),
    ("full_story_part1", "Full Story Part 1 (Aoede)", True),
    ("comment_2", "Comment 2 (Charon)", True),
    ("full_story_part2", "Full Story Part 2 (Aoede)", True),
    ("comment_3", "Comment 3 (Charon, Bridge)", True),
    ("point_one_heading", "Point One Heading (Aoede)", True),
    ("point_one", "Point One (Aoede)", True),
    ("point_two_heading", "Point Two Heading (Aoede)", True),
    ("point_two", "Point Two (Aoede)", True),
    ("comment_4", "Comment 4 (Charon)", True),
    ("in_one_line", "In One Line (Aoede)", True),
]

REQUIRED_SEGMENTS_BY_LEVEL = {"A2": A2_REQUIRED_SEGMENTS, "B1": B1_REQUIRED_SEGMENTS}


def check_full_script_coverage(
    level: str,
    present_segment_keys: set,
    key_phrase_count: int,
    key_phrase_en_present: int,
    key_phrase_ja_present: int,
) -> list[str]:
    """試聴Artifactが放送全segmentのscriptを掲載しているか確認する。

    present_segment_keys: Artifact生成scriptが実際にscript本文ブロックを
        描画したsegment_keyの集合(key_phrase_en/key_phrase_jaはper-phraseの
        個数チェックを別途行うため、1件でも描画していればこの集合に含めてよい)。
    key_phrase_count: この記事の実際のKey Phrase件数(keywords_canonicalized.json等から取得)。
    key_phrase_en_present / key_phrase_ja_present: Artifactへ実際に掲載したKey Phrase
        EN/JA(gloss)の件数。

    戻り値: 欠落しているsegment/項目のラベルのリスト(空なら欠落無し)。
    """
    required = REQUIRED_SEGMENTS_BY_LEVEL.get(level)
    if required is None:
        raise ValueError(f"unknown level: {level!r} (expected 'A2' or 'B1')")

    missing = []
    for key, label, has_script in required:
        if not has_script:
            continue
        if key not in present_segment_keys:
            missing.append(label)

    if key_phrase_en_present < key_phrase_count:
        missing.append(f"Key Phrase EN ({key_phrase_en_present}/{key_phrase_count}件のみ掲載)")
    if key_phrase_ja_present < key_phrase_count:
        missing.append(f"Key Phrase JA/gloss ({key_phrase_ja_present}/{key_phrase_count}件のみ掲載)")

    return missing
