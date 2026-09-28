# ============================================================
# er019_family_x_audio_plan_01.py
# NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01 (Stage 1)
# ============================================================
# Family X(Entertainment News)後工程(3分割・Comment役割マッピング・
# segment順序plan)のうち、API呼び出しを一切含まない純粋ヘルパーのみを
# 集約する(LLM/TTS/ASR呼び出しは行わない、常に¥0)。既存Production
# module(er003_*/er012_*/er019_family_x_entertainment_production_
# runner_01.py/er020_*/er006_*)は本ファイルでも一切編集しない
# (importのみ)。
#
# 正式仕様: CURRENT_SPEC.md「Family X(Entertainment News)音声構造」節
# (2026-09-26新設、PM-USER-DECISIONS-SSOT-CONSOLIDATION-04、
# APPROVED_FOR_PRODUCTION)。
#   Comment1 -> 本文1 -> Comment2 -> 本文2 -> Comment3 -> 本文3 ->
#   Comment4 -> In One Line
#   本文1 = Title + 1つ目の見出し直前まで(単一segment。Family Aのように
#     part1/part2へ機械的に2分割しない)。
#   本文2 = 1つ目の見出し + 2つ目の見出し直前まで。
#   本文3 = 2つ目の見出し + In One Line直前まで。
#   Point One/Two相当の構造・Point Notification効果音・Point前置き
#   (「ポイント解説」等)は一切使わない。記事冒頭(Welcome/Topic intro/
#   Preview/Key Phrases等)と末尾(Outro)は既存Family A A2/B1 Production
#   既定構成をそのまま再利用する(CURRENT_SPEC Family X節に別段の記載が
#   ないため)。
#
# DESIGN NOTE(Stage 1解釈、Stage 3bで見直し・Stage 3cで変更確定):
#   Stage 1〜3bでは本文2/3の見出しテキストを本文segment(full_story_
#   part2/3)と同一TTS呼び出しで読み上げていた。Stage 3b(Hormuz記事)の
#   runtime実行で、この方式が原因と判明したSTOPPED 2件(A2 full_story_
#   part2/B1B full_story_part2、見出し文と本文冒頭の語句反復をrepetition
#   QAが誤検知/見出し境界がASR上で後続文と連結)が発生した
#   (`NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01_REPORT.md`§Stage 3b参照)。
#   Stage 3c(本管理ID、Fable/ユーザー確認済みの技術的実装変更、CURRENT_
#   SPECの音声構造・順序・効果音方針自体は無変更)で、見出しを同一スロット
#   内の独立した短いTTS呼び出し(sub-segment、segment_id=
#   full_story_part2_heading/full_story_part3_heading)へ分離した。
#   Family A B1の`point_one_heading`/`point_two_heading`
#   (`er003_v1_sing01_point_headings_aoede.generate`、既存Production関数)
#   と同じ機構をB1Bで再利用し、A2はFamily A A2の同機構
#   (`er003_v1_n3_01_tts_generate.generate_a2_segment_with_slowdown`、
#   style_prefix=A2_ENGLISH_STYLE_PREFIX_SLOWER)を再利用する(新規TTS
#   経路は作らない)。新segment_idはer020_tts_retry_local_rewrite_01.
#   NON_APPLICABLE_SEGMENT_IDS(point_one_heading/point_two_headingのみ
#   ハードコード)に含まれないため、resolve_narrative_role()はNoneを返し
#   connected_speech_enabled_for()はFalseになる(er020編集禁止のため。
#   ただしFamily Aのpoint_one_heading扱い[HEADING_READOUT→Connected
#   Speech非適用]と実質的な効果は同一=Falseであり、挙動差はない)。
#   音声上の順序は「見出し→本文」で同一スロット内に連続、間の間隔は
#   新規pause値を追加せずFamily A既存の見出し→本文pause定数を再利用する
#   (B1B: `er003_v1_n3_01_assemble.HEADING_TO_BODY_PAUSE_SECONDS_B1`、
#   A2: `er003_v1_crosslevel_audio_02_common.POINT_EXPLANATION_PAUSE_
#   SECONDS`、いずれも0.7秒・既存値、asm/crosslevel_common自体は無編集)。
# ============================================================
from __future__ import annotations

import re

import er003_v1_n3_01_scaffold_generate as sc  # clean_heading()のみ再利用(既存関数、無変更)

_MD_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")


def _strip_markdown_bold(s: str) -> str:
    return _MD_BOLD_RE.sub(r"\1", s or "")


def _word_count_en(s: str) -> int:
    return len(re.findall(r"[A-Za-z']+", s or ""))


def split_family_x_article_text(text: str) -> dict:
    """Family X article.md(# Title -> 本文1 -> ### 見出し1 -> 本文2 ->
    ### 見出し2 -> 本文3 -> ## In one line)を分割する。

    構造契約(満たさない場合RuntimeError): ###見出しがちょうど2つ、
    かつ『## In one line』見出しが存在すること。本文1が空でないこと。
    """
    title_match = re.match(r"^#\s+(.+?)\s*\n", text)
    title = title_match.group(1).strip() if title_match else ""
    body_start = title_match.end() if title_match else 0

    h3_matches = list(re.finditer(r"^###\s+(.+?)\s*$", text, flags=re.MULTILINE))
    if len(h3_matches) != 2:
        raise RuntimeError(
            f"[FAMILY-X-SPLIT] ###見出しがちょうど2つではありません(検出数: {len(h3_matches)})。"
            "Family Xの3分割にはTitle+###見出し2つ+『## In one line』の構造契約が必要です。")

    in_one_line_match = re.search(
        r"^##\s+In [Oo]ne [Ll]ine[…\.]*\s*\n(.+)", text, flags=re.MULTILINE | re.DOTALL)
    if not in_one_line_match:
        raise RuntimeError("[FAMILY-X-SPLIT] 『## In one line』見出しが見つかりません")

    if h3_matches[1].start() < h3_matches[0].end() or in_one_line_match.start() < h3_matches[1].end():
        raise RuntimeError("[FAMILY-X-SPLIT] 見出し/In one lineの出現順序が不正です")

    heading1_raw = h3_matches[0].group(1)
    heading2_raw = h3_matches[1].group(1)
    heading1 = sc.clean_heading(heading1_raw)
    heading2 = sc.clean_heading(heading2_raw)

    part1_text = text[body_start:h3_matches[0].start()].strip()
    body2_text = text[h3_matches[0].end():h3_matches[1].start()].strip()
    body3_text = text[h3_matches[1].end():in_one_line_match.start()].strip()
    in_one_line_text = in_one_line_match.group(1).strip()

    if not part1_text:
        raise RuntimeError("[FAMILY-X-SPLIT] 本文1(Title後、1つ目の見出し前)が空です")

    title = _strip_markdown_bold(title)
    part1_text = _strip_markdown_bold(part1_text)
    heading1 = _strip_markdown_bold(heading1)
    body2_text = _strip_markdown_bold(body2_text)
    heading2 = _strip_markdown_bold(heading2)
    body3_text = _strip_markdown_bold(body3_text)
    in_one_line_text = _strip_markdown_bold(in_one_line_text)

    # 本文2/3 = 見出し + content(DESIGN NOTE参照、見出しをsegment先頭に
    # 含める解釈)。contentが空(見出し直後に本文が無い)場合は見出しのみ。
    part2_text = f"{heading1}\n\n{body2_text}" if body2_text else heading1
    part3_text = f"{heading2}\n\n{body3_text}" if body3_text else heading2

    return {
        "title": title,
        "part1": part1_text,
        "heading1": heading1, "body2": body2_text, "part2": part2_text,
        "heading2": heading2, "body3": body3_text, "part3": part3_text,
        "in_one_line": in_one_line_text,
        "word_counts": {
            "part1": _word_count_en(part1_text), "part2": _word_count_en(part2_text),
            "part3": _word_count_en(part3_text), "in_one_line": _word_count_en(in_one_line_text),
        },
    }


# ============================================================
# FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W1、2026-09-29、ユーザー
# 正式決定APPROVED_FOR_PRODUCTION): 新記事構造(途中Heading廃止・忠実
# 英訳・段落境界での決定論的3分割)向けのsplit関数。上のsplit_family_x_
# article_text()(###見出し2つ前提、Stage 1〜3c仕様)は一切変更しない
# (旧仕様との比較・後方互換確認に残す)。アルゴリズム本体は
# er003_v1_n3_01_scaffold_generate.split_family_x_article_text_v2()
# (Family X Writer stage[er012_e_family_entertainment_two_level_
# runner_01.run_writer_stage()]のparts.json生成と共通実装)をそのまま
# 使う(重複実装しない)。
# ============================================================
def split_family_x_article_text_v2(text: str) -> dict:
    """新構造(# Title -> 本文[段落、見出しなし] ->『## In one line』)を
    part1/part2/part3+in_one_lineへ分割する。『## In one line』が見つか
    らない場合のみRuntimeError、paragraph_count<3の場合はstatus=
    "TOO_FEW_PARAGRAPHS"を返す(旧split_family_x_article_text()の###
    見出し2つ必須・無retryクラッシュ[OPEN-228]は新経路に存在しない)。"""
    return sc.split_family_x_article_text_v2(text)


def reconstruct_family_x_article_text(parts: dict) -> str:
    """Preview/Key Phrase生成のcontext用に、Family Xの構造からMarkdown
    全文を再構成する(語は一切変更しない、既存内容の再結合のみ)。"""
    return (f"# {parts['title']}\n\n{parts['part1']}\n\n"
            f"### {parts['heading1']}\n\n{parts['body2']}\n\n"
            f"### {parts['heading2']}\n\n{parts['body3']}\n\n"
            f"## In one line\n{parts['in_one_line']}")


def reconstruct_family_x_article_text_v2(parts: dict) -> str:
    """FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W1): 新構造(見出し廃止)
    向けのreconstruct。split_family_x_article_text_v2()が返すpart1/2/3
    (見出しを含まない)を単純に段落として連結する(語は一切変更しない)。"""
    return (f"# {parts['title']}\n\n{parts['part1']}\n\n{parts['part2']}\n\n{parts['part3']}\n\n"
            f"## In one line\n{parts['in_one_line']}")


# ============================================================
# Comment/Preview role(Point前提を除去した新規role、既存Prompt本体は
# 改変しない。Comment 1・2・Preview roleは既存Family A(b1s/a2gen)の
# ものを無変更のままimportして使う[呼び出し側でimport]。ここでは
# Comment 3・4のみ、Family X用のrole文言を新規定義する)。
# ============================================================
# B1(英語Comment、Advanced/Charon)
FAMILY_X_B1_COMMENT_3_ROLE = """あなたはPodcastのナビゲーターです。リスナーは本文の第1部・第2部を
すでに聞き終わり、これから本文の第3部を聞きます。その間に流す、
Comment 3(役割: Mid-story Recovery + Bridge to Part 3)を書いてください。

役割: ここまでの内容の核心を短く整理し、第3部で何を聞けばよいかを示します。
第3部の結論を先に言ってはいけません。新しいFactを追加しないでください。
易しい英語で2〜3文にしてください。

【重要・出力への制約】出力する文章自体に"Part 1"・"Part 2"・"Part 3"・"Full Story"のような
制作内部の構造ラベルを含めないでください。リスナーは番組の内部構成を意識しません。"""

FAMILY_X_B1_COMMENT_4_ROLE = """あなたはPodcastのナビゲーターです。リスナーは本文の第3部を含む
本文全体をすでに聞き終わり、これからIn One Line(結びのまとめ)を聞きます。
その間に流す、Comment 4(役割: Story Recovery + Bridge to In One Line)を
書いてください。

役割: 記事全体の意味を軽く回収し、In One Lineへつなぎます。本文を再説明し
すぎないでください。2〜3文にしてください。

注意: In One Lineの実際のsentence数は記事により異なります(1文とは限り
ません)。「一文で」「one sentenceで」「一言で」等、sentence数を断定する
表現は使わないでください。

【重要・出力への制約】出力する文章自体に"Part 1"・"Part 2"・"Part 3"・"Full Story"のような
制作内部の構造ラベルを含めないでください。リスナーは番組の内部構成を意識しません。"""

# A2(日本語Comment、Standard/単一Voice)
FAMILY_X_A2_COMMENT_3_ROLE = """あなたはPodcastのナビゲーターです。リスナーは本文の第1部・第2部を
すでに聞き終わり、これから本文の第3部を聞きます。その間に流す、
Comment 3(役割: Mid-story Recovery + Bridge to Part 3)を日本語で
書いてください。

役割: ここまでの内容の核心を短く整理し、第3部で何を聞けばよいかを示します。
第3部の結論を先に言ってはいけません。新しいFactを追加しないでください。
易しい日本語で2〜3文にしてください。

【重要・出力への制約】出力する文章自体に"Part 1"・"Part 2"・"Part 3"・"Full Story"のような
制作内部の構造ラベルを含めないでください。リスナーは番組の内部構成を意識しません。"""

FAMILY_X_A2_COMMENT_4_ROLE = """あなたはPodcastのナビゲーターです。リスナーは本文の第3部を含む
本文全体をすでに聞き終わり、これからIn One Line(結びのまとめ、英語)を
聞きます。その間に流す、Comment 4(役割: Story Recovery + Bridge to In One
Line)を日本語で書いてください。

役割: 記事全体の意味を軽く回収し、In One Lineへつなぎます。本文を再説明し
すぎないでください。2〜3文にしてください。

【重要・出力への制約】出力する文章自体に"Part 1"・"Part 2"・"Part 3"・"Full Story"のような
制作内部の構造ラベルを含めないでください。リスナーは番組の内部構成を意識しません。

注意: In One Lineの実際のsentence数は記事により異なります(1文とは限り
ません)。「一文で」「one sentenceで」「一言で」等、sentence数を断定する
表現は使わないでください。"""


# ============================================================
# Segment順序plan(dry-run/assembly timeline builderの単一ソース)
# ============================================================
# 各entry: (segment_label, segment_id_or_None[SFX/固定共有segmentはNone], plan_role)
# plan_role: dry-run表示用の粗い分類(実際のnarrative role判定は
# er020_tts_retry_local_rewrite_01.resolve_narrative_role()を正とする、
# 呼び出し側[runner]でsegment_id経由により再確認する)。
FAMILY_X_B1_SEGMENT_ORDER = (
    ("Intro", None, "SFX"),
    ("Welcome (Charon)", None, "FIXED_SHARED"),
    ("Topic intro (Charon)", "topic_intro", "TOPIC_INTRO"),
    ("Notification 1", None, "SFX"),
    ("Preview intro (Charon)", None, "FIXED_SHARED"),
    ("Preview (Charon)", "preview", "PREVIEW"),
    ("Notification 2", None, "SFX"),
    ("Key phrases intro (Charon)", None, "FIXED_SHARED"),
    ("Key Phrase 1..N", None, "KEY_PHRASE"),
    ("Notification 3", None, "SFX"),
    ("Full story intro (Charon)", None, "FIXED_SHARED"),
    ("Comment 1 (Charon)", "comment_1", "COMMENT"),
    ("Full Story Part 1 (Aoede)", "full_story_part1", "FULL_STORY"),
    ("Comment 2 (Charon)", "comment_2", "COMMENT"),
    # Stage 3c: 見出しsub-segment(本文2直前、同一スロット・SFXなしで連続)。
    ("Full Story Part 2 Heading (Aoede)", "full_story_part2_heading", "HEADING_READOUT"),
    ("Full Story Part 2 (Aoede)", "full_story_part2", "FULL_STORY"),
    ("Comment 3 (Charon)", "comment_3", "COMMENT"),
    ("Full Story Part 3 Heading (Aoede)", "full_story_part3_heading", "HEADING_READOUT"),
    ("Full Story Part 3 (Aoede)", "full_story_part3", "FULL_STORY"),
    ("Comment 4 (Charon)", "comment_4", "COMMENT"),
    ("In One Line (Aoede)", "in_one_line", "IN_ONE_LINE"),
    ("Outro (Charon)", None, "SFX"),
)

# FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W1、2026-09-29): 新記事構造
# (Heading Readout撤去)向けのsegment順序。上のFAMILY_X_B1_SEGMENT_ORDER
# (旧、見出しsub-segment込み)は無変更のまま残す。組立順はComment1->
# 本文1->Comment2->本文2->Comment3->本文3->Comment4->In One Line
# (見出しsub-segmentは存在しない)。
FAMILY_X_B1_SEGMENT_ORDER_V2 = (
    ("Intro", None, "SFX"),
    ("Welcome (Charon)", None, "FIXED_SHARED"),
    ("Topic intro (Charon)", "topic_intro", "TOPIC_INTRO"),
    ("Notification 1", None, "SFX"),
    ("Preview intro (Charon)", None, "FIXED_SHARED"),
    ("Preview (Charon)", "preview", "PREVIEW"),
    ("Notification 2", None, "SFX"),
    ("Key phrases intro (Charon)", None, "FIXED_SHARED"),
    ("Key Phrase 1..N", None, "KEY_PHRASE"),
    ("Notification 3", None, "SFX"),
    ("Full story intro (Charon)", None, "FIXED_SHARED"),
    ("Comment 1 (Charon)", "comment_1", "COMMENT"),
    ("Full Story Part 1 (Aoede)", "full_story_part1", "FULL_STORY"),
    ("Comment 2 (Charon)", "comment_2", "COMMENT"),
    ("Full Story Part 2 (Aoede)", "full_story_part2", "FULL_STORY"),
    ("Comment 3 (Charon)", "comment_3", "COMMENT"),
    ("Full Story Part 3 (Aoede)", "full_story_part3", "FULL_STORY"),
    ("Comment 4 (Charon)", "comment_4", "COMMENT"),
    ("In One Line (Aoede)", "in_one_line", "IN_ONE_LINE"),
    ("Outro (Charon)", None, "SFX"),
)

# A2は既存Family Aの"Point explanation"(Point構造を説明する固定前置き)
# segmentを使わない(CURRENT_SPEC Family X節: 「ポイント解説」等のPoint
# 前置きも使わない、Commentで自然につなぐ)。
FAMILY_X_A2_SEGMENT_ORDER = (
    ("Intro", None, "SFX"),
    ("Welcome", None, "FIXED_SHARED"),
    ("Topic intro", "topic_intro", "TOPIC_INTRO"),
    ("Japanese title", "japanese_title", "JAPANESE_TITLE"),
    ("Notification 1", None, "SFX"),
    ("Preview intro", None, "FIXED_SHARED"),
    ("Preview", "preview", "PREVIEW"),
    ("Notification 2", None, "SFX"),
    ("Key phrases intro", None, "FIXED_SHARED"),
    ("Key Phrase 1..N", None, "KEY_PHRASE"),
    ("Notification 3", None, "SFX"),
    ("Full story intro", None, "FIXED_SHARED"),
    ("Comment 1", "comment_1", "COMMENT"),
    ("Full Story Part 1", "full_story_part1", "FULL_STORY"),
    ("Comment 2", "comment_2", "COMMENT"),
    # Stage 3c: 見出しsub-segment(本文2直前、同一スロット・SFXなしで連続)。
    ("Full Story Part 2 Heading", "full_story_part2_heading", "HEADING_READOUT"),
    ("Full Story Part 2", "full_story_part2", "FULL_STORY"),
    ("Comment 3", "comment_3", "COMMENT"),
    ("Full Story Part 3 Heading", "full_story_part3_heading", "HEADING_READOUT"),
    ("Full Story Part 3", "full_story_part3", "FULL_STORY"),
    ("Comment 4", "comment_4", "COMMENT"),
    ("In One Line", "in_one_line", "IN_ONE_LINE"),
    ("Outro", None, "SFX"),
)

# FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W1、2026-09-29): 新記事構造
# (Heading Readout撤去)向けのA2 segment順序。上のFAMILY_X_A2_SEGMENT_
# ORDER(旧、見出しsub-segment込み)は無変更のまま残す。
FAMILY_X_A2_SEGMENT_ORDER_V2 = (
    ("Intro", None, "SFX"),
    ("Welcome", None, "FIXED_SHARED"),
    ("Topic intro", "topic_intro", "TOPIC_INTRO"),
    ("Japanese title", "japanese_title", "JAPANESE_TITLE"),
    ("Notification 1", None, "SFX"),
    ("Preview intro", None, "FIXED_SHARED"),
    ("Preview", "preview", "PREVIEW"),
    ("Notification 2", None, "SFX"),
    ("Key phrases intro", None, "FIXED_SHARED"),
    ("Key Phrase 1..N", None, "KEY_PHRASE"),
    ("Notification 3", None, "SFX"),
    ("Full story intro", None, "FIXED_SHARED"),
    ("Comment 1", "comment_1", "COMMENT"),
    ("Full Story Part 1", "full_story_part1", "FULL_STORY"),
    ("Comment 2", "comment_2", "COMMENT"),
    ("Full Story Part 2", "full_story_part2", "FULL_STORY"),
    ("Comment 3", "comment_3", "COMMENT"),
    ("Full Story Part 3", "full_story_part3", "FULL_STORY"),
    ("Comment 4", "comment_4", "COMMENT"),
    ("In One Line", "in_one_line", "IN_ONE_LINE"),
    ("Outro", None, "SFX"),
)


# dry-run見積り専用の粗いWPM/CPM(Gate化しない、参考値のみ)。
_ENGLISH_WPM = 150.0
_JAPANESE_CPM = 350.0


def estimate_seconds_english(text: str, wpm: float = _ENGLISH_WPM) -> float:
    words = _word_count_en(text)
    return round(words / wpm * 60.0, 1) if wpm else 0.0


def estimate_seconds_japanese(text: str, cpm: float = _JAPANESE_CPM) -> float:
    chars = len(re.sub(r"\s", "", text or ""))
    return round(chars / cpm * 60.0, 1) if cpm else 0.0
