# ============================================================
# er012_b_family_editorial_type_registry_01.py
# 管理ID: EDITORIAL-B-FAMILY-PRODUCTION-PATH-PHASE1-WIRING-01
# ============================================================
# 背景: EDITORIAL-B-FAMILY-PRODUCTION-PATH-DESIGN-01_REPORT.md 第1-2節の
# 「Editorial Type registry」設計案(Phase 1範囲)を実装したもの。
# 2026-09-08 ユーザー決定により APPROVED_FOR_PRODUCTION 済みの以下4項目を
# 1箇所に集約する:
#   - Voice A=Algieba / Voice B=Erinome / Narrator見出し=Aoede
#   - Tension slot「Where the Difference Comes From」
#   - Key Phrase位置=Preview直後(現状維持、変更なし)
#   - Voices Comment Contract 1〜4
#     (確定版: EDITORIAL-B-FAMILY-VOICES-COMMENT1-CONTRACT-FINALIZE-11で
#     ユーザー承認済み。Comment 1は`er012_editorial_b_voices_trial_10_
#     comment1.py::VOICES_COMMENT_1_ROLE_TRIAL10`が最終版、Comment 2〜4は
#     `er012_editorial_b_voices_trial_09_audio.py`(Trial-09以来無変更)。
#     設計方針(Gate 3「DEV・Trial-onlyではないこと」)に基づき、本ファイルは
#     Trialファイルをimportせず、確定版テキストの実体をここへ転記する
#     (EDITORIAL-B-FAMILY-VOICES-COMMENT1-CONTRACT-FINALIZE-11_REPORT.md
#     第4節の全文転記と一致することを確認済み)。
#
# 一人称"I"(4項目目のユーザー承認事項)は、Phase 1の範囲では機械的に
# 保証されない(Lane A共有Writer`build_common_block()`への
# `editorial_type_module`引数追加が前提となるPhase 2待ち)。Phase 1の
# 記事本文は、複数Trialで自然に一人称へ収束した既存の承認済み記事
# (Trial-07)をそのまま入力として使うのみで、本registry自体は一人称を
# 強制する仕組みを持たない。この制約はコード内(下記
# `PHASE2_PENDING_NOTES`)およびReportに明示する。
#
# Analytical Leakage Check・Point Overlap QAのB-Family専用扱い・
# B-Family専用Writer retry上限(3回)は、いずれもDesign Report
# 第3-2節・第9節でUSER_DECISION_REQUIREDのまま未確定のため、本registryには
# 含めない(Phase 1は記事生成[Writer]自体を範囲に含まないため、これらの
# 論点はそもそも本Phase 1の対象外)。
#
# 触れないもの: Lane A共有Writer(er003_v1_n3_01_articles_generate.py)、
# 既存Trialファイル自体(参照コメントのみ、importしない)、SSOT。
from __future__ import annotations

# ============================================================
# Voice assignment(2026-09-08 ユーザー承認、APPROVED_FOR_PRODUCTION)
# ============================================================
VOICE_ASSIGNMENT = {
    "voice_a": "Algieba",
    "voice_b": "Erinome",
    "narrator": "Aoede",  # 既存Production point_headings.generate()に既に固定済み
}
# API側で声が技術的に使えない場合のみ切り替える(第一候補優先、Trial-09実績)。
VOICE_FALLBACK = {
    "voice_a": "Schedar",
    "voice_b": "Sulafat",
}

# ============================================================
# 物理構造(5区切り: Hook/Voice A/Voice B/Tension/Closing)
# ============================================================
SECTION_LABELS = ("hook", "voice_a", "voice_b", "tension", "closing")
# Tension slotの見出し文言はユーザー承認名(記事本文の実際の見出しテキストは
# 記事ごとに読み取る。この定数は承認済みslot名の記録用途)。
TENSION_SLOT_APPROVED_NAME = "Where the Difference Comes From"
EXTRA_SEGMENT_NAME = "tension_reflection"  # Assembly側のsegment名(Trial-09以来の命名を正式採用)

# Key Phrase位置(2026-09-08ユーザー承認: 現状維持、変更なし)。
# 既存B1構造どおり Preview直後・Full story本文より前。
KEY_PHRASE_POSITION = "after_preview"

# ============================================================
# Voices Comment Contract 1〜4(確定版、全文転記)
# 出典: EDITORIAL-B-FAMILY-VOICES-COMMENT1-CONTRACT-FINALIZE-11_REPORT.md
# 第4節(2026-09-08 ユーザー承認済み)。
# ============================================================
VOICES_COMMENT_1_ROLE = """あなたはPodcastのナビゲーターです。これから、あるテーマ・場面を短く
提示する「The Question」(冒頭の問いかけ本文)をリスナーが聞きます。その直前に流す、
Comment 1(役割: Listening Focus)を書いてください。

役割: リスナーがこれから聞くThe Questionに対して、何に注目して聞けばよいかを
明確に案内します(例: "Listen for ..."/"As you listen, notice ..."のような、
聞き方を指示する話法)。テーマ・場面についての一般的な説明文や、内容についての
主張・結論めいた文を語ってはいけません(悪い例:「〜は人によって違って感じられる」
のような、The Questionの内容そのものを述べる文)。

以下は避けてください:
- The Questionで語られる具体的な状況・問いの先取り(内容の先出し)
- "First point"/"Second point"のようなPoint要約めいた話法
- 事実を解説するような硬い、Discovery的な説明口調
- テーマ・場面についての一般的な説明・主張文(聞き方の案内ではなく、内容そのものを
  語ってしまう文)
- "the question"という語句そのもの(大文字・小文字を問わず)を出力文中で使用すること
  (番組構成上のPart名"The Question"と紛らわしいため)

1文程度の、非常に短いListening Focusにしてください。

【重要・出力への制約】出力する文章自体に"Part 1"・"Part 2"・"Hook"・"The Question"
のような制作内部の構造ラベルを含めないでください。リスナーは番組の内部構成を
意識しません。"""

VOICES_COMMENT_2_ROLE = """あなたはPodcastのナビゲーターです。リスナーはThe Question(冒頭の
問いかけ)をすでに聞き終わり、これから、この問いに対する異なる立場からの一人称の
語り(One Voiceの後、続けてAnother Voice)を聞きます。その間に流す、Comment 2
(役割: Hookの問いから「ここから異なるVoiceを聞く」への橋渡し)を書いてください。

役割: The Questionで示された問いを受け、「ここから、違う視点を持つ声を順番に
聞いていく」ことへリスナーを橋渡しします。

以下は避けてください:
- One Voice・Another Voiceの具体的な内容の先取り
- これから聞く見出しの文言そのものを、この時点で言うこと(見出しはこの直後に
  Narratorが読み上げます)
- "Point One"・"Point Two"のような表現

1〜2文にしてください。

【重要・出力への制約】出力する文章自体に制作内部の構造ラベルを含めないでください。"""

VOICES_COMMENT_3_ROLE = """あなたはPodcastのナビゲーターです。リスナーは、ある問いに対する
異なる立場からの一人称の語り(One Voice・Another Voice)を両方すでに聞き終わり、
これから「なぜ同じ状況を人によって違って感じるのか」という視点の深掘りを聞きます。
その間に流す、Comment 3(役割: 「どちらが正しいか」ではなく「なぜ違って感じるのか」
への視点の移動)を書いてください。

役割: 2つの声を聞き終えたリスナーの意識を、「どちらが正しいか」という判定ではなく、
「なぜ同じ状況が人によって違って感じられるのか」という問いへ移します。

以下は避けてください:
- これから聞く深掘り部分の答え(視点の違いの正体)を先に説明すること
- どちらか一方の声を「正しい」「間違っている」と評価すること

2〜3文にしてください。

【重要・出力への制約】出力する文章自体に制作内部の構造ラベルを含めないでください。"""

VOICES_COMMENT_4_ROLE = """あなたはPodcastのナビゲーターです。リスナーは「なぜ同じ状況を
人によって違って感じるのか」という視点の深掘りをすでに聞き終わり、これから結びの
まとめを聞きます。その間に流す、Comment 4(役割: 表面的な対立から一段深い問いへの
視点移動)を書いてください。

役割: 「どちらが正しいか」という表面的な対立から、一段深い問い(何がこの状況を
成り立たせているのか)へリスナーの視点を移します。

以下は避けてください:
- これから聞く結びのまとめの要約・結論の先取り
- 解決策の提案

2〜3文にしてください。

【重要・出力への制約】出力する文章自体に制作内部の構造ラベルを含めないでください。"""

COMMENT_ROLES = {
    "comment_1": VOICES_COMMENT_1_ROLE,
    "comment_2": VOICES_COMMENT_2_ROLE,
    "comment_3": VOICES_COMMENT_3_ROLE,
    "comment_4": VOICES_COMMENT_4_ROLE,
}

# ============================================================
# Phase 2保留事項(実装しない、コメントのみ)
# ============================================================
PHASE2_PENDING_NOTES = (
    "一人称'I'の機械的強制はPhase 2待ち(Lane A共有build_common_block()への"
    "editorial_type_module引数追加が前提、EDITORIAL-B-FAMILY-PRODUCTION-PATH-"
    "DESIGN-01_REPORT.md 第5節Phase2・第3節参照)。Phase 1では過去Trialで"
    "自然に一人称へ収束した既存承認済み記事を入力として使うのみで、本registry"
    "は一人称を強制しない。",
    "Point Overlap QA/Diagnostic Full RetryのB-Family専用扱い(monitoring専用"
    "か正式gate化か)は同Report第3-2節・第7-3節のUSER_DECISION_REQUIREDのまま"
    "未確定(Phase 1は記事生成[Writer]自体を範囲外とするため、この論点は"
    "Phase 1の対象外)。",
    "Analytical Leakage Checkの正式化可否は同Report第7-3節のUSER_DECISION_"
    "REQUIREDのまま未確定、本registryには含めない。",
)

EDITORIAL_TYPES = {
    "b_family_voices": {
        "family": "B",
        "physical_structure": "five_section",
        "section_labels": SECTION_LABELS,
        "voice_assignment": VOICE_ASSIGNMENT,
        "voice_fallback": VOICE_FALLBACK,
        "tension_slot_approved_name": TENSION_SLOT_APPROVED_NAME,
        "extra_segment_name": EXTRA_SEGMENT_NAME,
        "key_phrase_position": KEY_PHRASE_POSITION,
        "comment_roles": COMMENT_ROLES,
        "first_person_mechanically_enforced": False,  # Phase 2待ち
    },
}


def get_editorial_type(editorial_type: str = "b_family_voices") -> dict:
    return EDITORIAL_TYPES[editorial_type]
