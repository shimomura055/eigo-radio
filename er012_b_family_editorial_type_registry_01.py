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

import re

# ============================================================
# Voice assignment(2026-09-08 ユーザー承認、APPROVED_FOR_PRODUCTION)
# ============================================================
VOICE_ASSIGNMENT = {
    "voice_a": "Algieba",
    "voice_b": "Erinome",
    "narrator": "Aoede",  # 既存Production point_headings.generate()に既に固定済み
    # EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1-01(2026-09-10
    # ユーザー正式決定): 3V(3声Voice構成)専用のVoice 3。voice_a側の
    # fallback候補(VOICE_FALLBACK["voice_a"])と同一の声を、3V構成では
    # 本採用の第3声として使う(3V Audio Trial-01実績)。2V経路
    # (voice_a/voice_b/narrator)は本キー追加による影響を受けない。
    "voice_c": "Schedar",
}
# API側で声が技術的に使えない場合のみ切り替える(第一候補優先、Trial-09実績)。
# voice_cにはfallbackキーを設けない(2026-09-10ユーザー決定:
# 「Voice 3は当面専用fallback声を持たない。技術的に使用不可の場合は
# 独自の代替声を発明せず、本文TTS[generate_voice_body_wide_margin]が
# 既に備える既存Human Review Lock[guarded_generate]へ委ねる」)。
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

# EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1-01(2026-09-10
# ユーザー正式決定): Comment 2・3は、Voice数(2V/3V)専用の定数を増やさず、
# 既存2V版の文言をVoice数非依存の汎用表現へ最小限だけ書き換えて共用する
# (3V専用の別Contractを新設しない)。変更点は「One Voice/Another Voice」
# 等の具体的な声の個数・名前を指す表現の除去・一般化のみであり、Comment 2
# (Hookの問いから複数Voiceへの橋渡し)・Comment 3(「正しさの判定」ではなく
# 「なぜ違って感じるか」への視点移動)という役割・意味自体は2V版から一切
# 変更していない(2V記事の生成結果へ与える影響は、声の個数を明示しない
# 言い回しへの言い換えのみと判断した)。
VOICES_COMMENT_2_ROLE = """あなたはPodcastのナビゲーターです。リスナーはThe Question(冒頭の
問いかけ)をすでに聞き終わり、これから、この問いに対する異なる立場からの一人称の
語りを、声を変えながら順番に聞きます。その間に流す、Comment 2
(役割: Hookの問いから「ここから異なるVoiceを聞く」への橋渡し)を書いてください。

役割: The Questionで示された問いを受け、「ここから、違う視点を持つ声を順番に
聞いていく」ことへリスナーを橋渡しします。

以下は避けてください:
- これから聞く各Voiceの具体的な内容の先取り
- これから聞く見出しの文言そのものを、この時点で言うこと(見出しはこの直後に
  Narratorが読み上げます)
- "Point One"・"Point Two"のような表現

1〜2文にしてください。

【重要・出力への制約】出力する文章自体に制作内部の構造ラベルを含めないでください。"""

VOICES_COMMENT_3_ROLE = """あなたはPodcastのナビゲーターです。リスナーは、ある問いに対する
異なる立場からの一人称の語りをすべて聞き終わり、
これから「なぜ同じ状況を人によって違って感じるのか」という視点の深掘りを聞きます。
その間に流す、Comment 3(役割: 「どちらが正しいか」ではなく「なぜ違って感じるのか」
への視点の移動)を書いてください。

役割: 複数の声を聞き終えたリスナーの意識を、「どちらが正しいか」という判定ではなく、
「なぜ同じ状況が人によって違って感じられるのか」という問いへ移します。

以下は避けてください:
- これから聞く深掘り部分の答え(視点の違いの正体)を先に説明すること
- いずれかの声を「正しい」「間違っている」と評価すること

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

# ============================================================
# B-Family A2(2026-09-09 ユーザー正式決定、APPROVED_FOR_PRODUCTION。
# 管理ID: EDITORIAL-B-FAMILY-VOICES-A2-PRODUCTION-WIRING-01、Gate 3)
# ============================================================
# 声・物理構造(5区切り)はB1と同一(VOICE_ASSIGNMENT/VOICE_FALLBACK/
# SECTION_LABELS/TENSION_SLOT_APPROVED_NAME/EXTRA_SEGMENT_NAME/
# COMMENT_ROLES[役割定義そのもの]をそのまま流用する)。A2固有の差分
# (Audio Gate level・slowdown対象・Comment出力言語・日本語タイトル・
# OPEN-129整合用required segments)のみここに追加する。出典:
# EDITORIAL-B-FAMILY-VOICES-A2-FREE-ADDRESS-COMPLETION-TRIAL-02/
# ...-CROSS-AUDIT-AND-FIX-03/...-SLOWDOWN-AND-KEYPHRASE-REGEN-04の各Report。

# Audio Validation Gateのlevel引数(標準"A2"文字列は使わない。理由:
# 標準"A2"は"point_one"/"point_two"という名前へ「A2 slowdown必須」チェックを
# 強制するが、B-Familyのpoint_one/two相当はVoice A/B[Algieba/Erinome]で
# あり同名の別物のため誤爆する。既存の安全機構[VALIDATED/HUMAN_APPROVED状態
# チェック・asset hash staleness]は無変更のまま有効)。
B_FAMILY_A2_AUDIO_GATE_LEVEL = "B_FAMILY_A2"

# 標準A2の既存6% slowdown(A2_ENGLISH_STYLE_PREFIX_SLOWER + 6% time-stretch
# post-process、er003_v1_n3_01_tts_generate.py無変更)を適用する対象segment。
# Voice A/B本文(point_one/point_two相当)を含む(ユーザー決定2026-09-08、
# EDITORIAL-B-FAMILY-VOICES-A2-SLOWDOWN-AND-KEYPHRASE-REGEN-04)。
B_FAMILY_A2_SLOWDOWN_TARGET_SEGMENTS = (
    "point_one_heading", "point_two_heading",
    "full_story_part1", "full_story_part2",
    "point_one", "point_two",
    EXTRA_SEGMENT_NAME,  # "tension_reflection"
    "in_one_line",
)

# Comment 1-4・Previewの出力言語(ユーザー決定B-A2-6: COMMENT_ROLESの役割
# 定義そのものは維持したまま、出力言語のみ標準A2規約[日本語・Aoede]へ。
# B1はCharon英語のまま無変更)。
B_FAMILY_A2_COMMENT_LANGUAGE = "ja"
B_FAMILY_A2_COMMENT_VOICE = "Aoede"

# 日本語タイトル(標準A2既存規約=er003_v1_n3_01_tts_generate.JAPANESE_TITLES
# と同じ「記事[theme]ごとに人手で直訳を用意する」パターンをB-Familyへも
# 適用する。新しい主張・数字は追加しない、原文タイトルの直訳のみ)。
B_FAMILY_A2_JAPANESE_TITLE_REQUIRED = True
B_FAMILY_A2_JAPANESE_TITLES = {
    # EDITORIAL-B-FAMILY-VOICES-A2-CROSS-AUDIT-AND-FIX-03(B-2)で追加した
    # 直訳文言、ユーザー最終承認版(_04)まで無変更。
    "b_voices_a2_free_address": "一つのオフィスに、働く場所についての二つの考え方",
}

# OPEN-129整合(Gate 3 item 8): Audio Validation Gate自体は「構造上あるべき
# segment数との一致」を検証しない既知の未対策事項(OPEN-129、共有Gateは
# 変更しない)。B-Family A2 Production runner側の完全性チェック(段数・
# voice割当の一致)専用に、期待されるsegment一覧+期待voice roleをここへ
# 定義する(この一覧自体はGateではなく、Lane B runner側のassertion専用の
# データ)。"voice_a"/"voice_b"は実際に解決されたvoice名(fallback込み)と
# 突き合わせる。
B_FAMILY_A2_REQUIRED_SEGMENTS = (
    ("topic_intro", "narrator_charon"),
    ("japanese_title", "narrator_aoede_ja"),
    ("preview", "narrator_aoede_ja"),
    ("comment_1", "narrator_aoede_ja"), ("comment_2", "narrator_aoede_ja"),
    ("comment_3", "narrator_aoede_ja"), ("comment_4", "narrator_aoede_ja"),
    ("point_one_heading", "narrator"), ("point_two_heading", "narrator"),
    ("point_one", "voice_a"), ("point_two", "voice_b"),
    ("full_story_part1", "narrator"), ("full_story_part2", "narrator"),
    (EXTRA_SEGMENT_NAME, "narrator"), ("in_one_line", "narrator"),
)

B_FAMILY_A2_CONFIG = {
    "audio_gate_level": B_FAMILY_A2_AUDIO_GATE_LEVEL,
    "slowdown_target_segments": B_FAMILY_A2_SLOWDOWN_TARGET_SEGMENTS,
    "comment_language": B_FAMILY_A2_COMMENT_LANGUAGE,
    "comment_voice": B_FAMILY_A2_COMMENT_VOICE,
    "japanese_title_required": B_FAMILY_A2_JAPANESE_TITLE_REQUIRED,
    "japanese_titles": B_FAMILY_A2_JAPANESE_TITLES,
    "required_segments": B_FAMILY_A2_REQUIRED_SEGMENTS,
    # OPEN-129-AUDIO-GATE-STRUCTURAL-COMPLETENESS-PRODUCTION-WIRING-01:
    # Key Phrase側の完全性チェック用(件数ベース、命名drift対応)。既存
    # `required_segments`/`check_required_segments_completeness()`は無変更。
    "key_phrase_ranks": 5,
    "key_phrase_subkey_count": 2,
}

# ============================================================
# OPEN-129-AUDIO-GATE-STRUCTURAL-COMPLETENESS-PRODUCTION-WIRING-01:
# B-Family B1用required_segments(正本、role文字列+voice_a/voice_b)。
# OPEN-129-AUDIO-GATE-STRUCTURAL-COMPLETENESS-TRIAL-01のB_FAMILY_B1
# spec(12/12検知・既存episode false reject 0で実証済み)と同一の
# segment一覧+voice roleを転記した(role文字列表記のみ本registryの既存
# 命名規約[narrator_charon/narrator_aoede_ja等]に合わせて追加)。
# full_story_part1/2・tension_reflection・in_one_lineは、既存Production
# データ実測でvoiceフィールドが常にNone(未記録)であるため、
# expected_voice=Noneとして「記録が無いことは既知の後方互換」として扱う
# (false reject防止、Trial-01 Part 3と同じ扱い)。
# ============================================================
B_FAMILY_B1_REQUIRED_SEGMENTS = (
    ("topic_intro", "narrator_charon"), ("preview", "narrator_charon"),
    ("comment_1", "narrator_charon"), ("comment_2", "narrator_charon"),
    ("comment_3", "narrator_charon"), ("comment_4", "narrator_charon"),
    ("point_one_heading", "narrator_aoede_en"), ("point_two_heading", "narrator_aoede_en"),
    ("point_one", "voice_a"), ("point_two", "voice_b"),
    ("full_story_part1", None), ("full_story_part2", None),
    (EXTRA_SEGMENT_NAME, None), ("in_one_line", None),
)

B_FAMILY_B1_CONFIG = {
    "required_segments": B_FAMILY_B1_REQUIRED_SEGMENTS,
    "key_phrase_ranks": 5,
    "key_phrase_subkey_count": 2,
}

# ============================================================
# EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1-01(2026-09-10
# ユーザー正式決定): B-Family B1用3V(3声Voice構成)required_segments。
# segment命名は`point_one`/`point_two`/`point_three`(3V Audio Trial実績を
# 採用、ユーザー確定)。B_FAMILY_B1_REQUIRED_SEGMENTS(2V、無変更)に
# Voice 3分(point_three_heading・point_three)を1段追加しただけの構成で、
# er012_editorial_b_voices_3v_audio_trial_01.py::build_required_structure_3v()
# (Trial側の暫定正本)と同一のsegment一覧・順序・役割表記(role文字列のみ、
# 本registryの既存命名規約[voice_a/voice_b]へvoice_cを追加する形へ統一)。
# 本追加により、Trial側の暫定正本はregistry側へ統合され(2重定義解消)、
# 3V required_structureの正本はここ1箇所になる。
# ============================================================
B_FAMILY_B1_3V_REQUIRED_SEGMENTS = (
    ("topic_intro", "narrator_charon"), ("preview", "narrator_charon"),
    ("comment_1", "narrator_charon"), ("comment_2", "narrator_charon"),
    ("comment_3", "narrator_charon"), ("comment_4", "narrator_charon"),
    ("point_one_heading", "narrator_aoede_en"), ("point_two_heading", "narrator_aoede_en"),
    ("point_three_heading", "narrator_aoede_en"),
    ("point_one", "voice_a"), ("point_two", "voice_b"), ("point_three", "voice_c"),
    ("full_story_part1", None), ("full_story_part2", None),
    (EXTRA_SEGMENT_NAME, None), ("in_one_line", None),
)

B_FAMILY_B1_3V_CONFIG = {
    "required_segments": B_FAMILY_B1_3V_REQUIRED_SEGMENTS,
    "key_phrase_ranks": 5,
    "key_phrase_subkey_count": 2,
}

# ============================================================
# OPEN-131-MULTI-VOICE-FACT-ATTRIBUTION-PRODUCTION-WIRING-01:
# Fact Checker候補A'(Voice別evidenceタグ+「Voice本文は出典明記不要
# (ただし事実誤り・実在人物引用は従来どおり検証)」の opt-in ルール)。
# 出典: EDITORIAL-B-FAMILY-MULTI-VOICE-FACT-ATTRIBUTION-TRIAL-01/02
# (ユーザー決定2026-09-09、APPROVED_FOR_PRODUCTION、Gate 3条件充足時のみ
# PRODUCTION_WIRED)。既定OFF。B-Family Production runner側のみが、
# `family == "B"` かつ本フラグTrueのときだけ`build_voice_attribution_
# block()`を呼び、`build_fact_check_prompt(..., voice_attribution_block=)`
# へ渡す。A-Family経路(er006_pool_pilot_01_writer.py等)はこのフラグ・
# 関数を一切参照しない。
# ============================================================
FACT_ATTRIBUTION_MODE_DEFAULT = False  # opt-in、既定OFF(mandatory化していない)

# Ledger中の[VOICE_n_EVIDENCE]タグ行を抽出する正規表現。3V/4Vも
# タグ名(VOICE_3_EVIDENCE等)を追加するだけで自動的に拾える設計
# (Trial-02第8節で確認済みのprompt側非ハードコードと同じ考え方)。
_VOICE_EVIDENCE_LINE_RE = re.compile(r"^\[VOICE_(\d+)_EVIDENCE\].*$", re.MULTILINE)

VOICE_ATTRIBUTION_RULE_TEXT = (
    "【複数Voice構成の記事における事実帰属ルール(B-Family Voices固有、opt-in、"
    "EDITORIAL-B-FAMILY-MULTI-VOICE-FACT-ATTRIBUTION-TRIAL-01/02で検証済みの"
    "候補A')】\n"
    "この記事のVoice本文(一人称の合成personaによる語り)は、下記のVerified "
    "Fact Ledgerの該当[VOICE_n_EVIDENCE]evidenceを一人称の語りへ翻案した"
    "ものです。Voice本文中の主張が、そのVoiceに割り当てられたLedger evidence"
    "(下記抜粋)の内容と実質的に対応している場合、本文中に出典・調査名・"
    "数値を逐一明記していないことだけを理由に、unsupported_specific_claimsへ"
    "計上したり、REVIEW_REQUIRED/FAILと判定したりしないでください。\n"
    "ただし、以下は従来どおり検証対象としてください(免除の対象外):\n"
    "- Voice本文の内容がLedger evidenceの数値・調査主体・結果を改変・捏造"
    "している場合\n"
    "- Voice本文中に実在する名前付き個人の発言として具体的に帰属される主張\n"
    "- Voice本文以外の地の文(Tension/Closing等)での客観的主張・出典明示が"
    "本来期待される表現\n"
)


def build_voice_attribution_block(ledger_text: str) -> str:
    """Ledgerの[VOICE_n_EVIDENCE]タグ行から始まるevidenceブロック全体
    (fact本文の折り返し・source/URL/counter_or_limitation/verification等の
    継続行を含む)を抽出し、opt-inルール文言と結合したblockを返す
    (`er002_ja_web_research_r3.build_fact_check_prompt()`の
    `voice_attribution_block`引数へそのまま渡す想定)。該当タグが1件も
    無ければ空文字列を返す(誤ってルールだけを渡してしまうことを防ぐ、
    fail-closed)。

    OPEN-131-ATTRIBUTION-BLOCK-MULTILINE-FIX-02: 修正前はタグが乗る物理1行
    のみを抽出しており、実Ledger(例:
    `er012_output/editorial_b_voices_trial_07/research/
    verified_fact_ledger.txt`)のように1 evidenceがfact本文の折り返し・
    `source:`/URL/`counter_or_limitation:`/`verification:`の複数行に
    またがる場合、2行目以降が欠落していた。終端規約(実Ledgerの書式から
    確定): 各evidenceエントリは空行1つで次のエントリ・次の`[...]`タグ・
    `===...===`セクション見出しと区切られている(Trial-07 Ledger実測、
    途中に空行が入るエントリは無い)。このため、タグ行から開始し、次に
    現れる「空行」「`[`で始まる行」「`===`で始まる行」のいずれかの直前
    までを1エントリとして抽出する。"""
    lines = (ledger_text or "").splitlines()
    evidence_lines: list = []
    in_block = False
    for line in lines:
        stripped = line.strip()
        if re.match(r"^\[VOICE_\d+_EVIDENCE\]", stripped):
            in_block = True
            evidence_lines.append(line)
            continue
        if in_block:
            if stripped == "" or stripped.startswith("[") or stripped.startswith("==="):
                in_block = False
                continue
            evidence_lines.append(line)
    if not evidence_lines:
        return ""
    evidence_block = "\n".join(evidence_lines)
    return (
        f"{VOICE_ATTRIBUTION_RULE_TEXT}\n"
        f"【Voice別 Verified Fact Ledger evidence(抜粋)】\n{evidence_block}\n"
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
        "a2": B_FAMILY_A2_CONFIG,
        "b1": B_FAMILY_B1_CONFIG,
        "b1_3v": B_FAMILY_B1_3V_CONFIG,
        "fact_attribution_mode": FACT_ATTRIBUTION_MODE_DEFAULT,
    },
}


def get_editorial_type(editorial_type: str = "b_family_voices") -> dict:
    return EDITORIAL_TYPES[editorial_type]


def get_editorial_type_a2(editorial_type: str = "b_family_voices") -> dict:
    """A2固有設定のみを返す(EDITORIAL-B-FAMILY-VOICES-A2-PRODUCTION-WIRING-01)。"""
    return EDITORIAL_TYPES[editorial_type]["a2"]


def get_editorial_type_b1(editorial_type: str = "b_family_voices") -> dict:
    """B1固有設定のみを返す(OPEN-129-AUDIO-GATE-STRUCTURAL-COMPLETENESS-
    PRODUCTION-WIRING-01)。"""
    return EDITORIAL_TYPES[editorial_type]["b1"]


def get_editorial_type_b1_3v(editorial_type: str = "b_family_voices") -> dict:
    """B1 3V(3声Voice構成)固有設定のみを返す(EDITORIAL-B-FAMILY-VOICES-
    3V-PRODUCTION-WIRING-PHASE1-01)。"""
    return EDITORIAL_TYPES[editorial_type]["b1_3v"]


def is_fact_attribution_mode_enabled(editorial_type: str = "b_family_voices") -> bool:
    """OPEN-131: `family == "B"` かつ `fact_attribution_mode` がTrueの場合
    のみTrueを返す(コードレベルgating、Trial-02第6節の設計結論どおり
    prompt側の意味理解だけに依存しない)。"""
    et = EDITORIAL_TYPES[editorial_type]
    return et.get("family") == "B" and bool(et.get("fact_attribution_mode"))


# ============================================================
# OPEN-129-AUDIO-GATE-STRUCTURAL-COMPLETENESS-PRODUCTION-WIRING-01:
# registry正本(required_segments、role文字列)から、Gate側
# `verify_episode_audio_validation_gate(required_structure=...)`へ渡す
# 解決済み構造(role文字列を実際のvoice名へ解決したもの)を組み立てる。
# Gate側はこの関数の出力を参照して検証するだけで、別の正本を持たない。
# ============================================================
_ROLE_TO_VOICE_RESOLVERS = {
    "narrator_charon": lambda voice_a, voice_b: "Charon",
    "narrator_aoede_en": lambda voice_a, voice_b: "Aoede",
    "narrator_aoede_ja": lambda voice_a, voice_b: "Aoede",
    "narrator": lambda voice_a, voice_b: "Aoede",
    "voice_a": lambda voice_a, voice_b: voice_a,
    "voice_b": lambda voice_a, voice_b: voice_b,
    None: lambda voice_a, voice_b: None,
}

# EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1-01: 3V(voice_c対応)
# 専用の3引数版resolver。既存_ROLE_TO_VOICE_RESOLVERS(2引数、上記)は
# 無変更のまま温存し、voice_c指定時のみこちらを使う(2V呼び出し経路への
# 影響ゼロ)。
_ROLE_TO_VOICE_RESOLVERS_3V = {
    "narrator_charon": lambda voice_a, voice_b, voice_c: "Charon",
    "narrator_aoede_en": lambda voice_a, voice_b, voice_c: "Aoede",
    "voice_a": lambda voice_a, voice_b, voice_c: voice_a,
    "voice_b": lambda voice_a, voice_b, voice_c: voice_b,
    "voice_c": lambda voice_a, voice_b, voice_c: voice_c,
    None: lambda voice_a, voice_b, voice_c: None,
}


def build_required_structure(level: str, voice_a: str, voice_b: str,
                              editorial_type: str = "b_family_voices",
                              voice_c: str | None = None) -> dict:
    """level: "b1" または "a2"。OPEN-129 Gate opt-in引数(required_structure)
    へそのまま渡せる辞書を返す。

    EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1-01: `voice_c`は
    完全後方互換の追加引数(既定None)。voice_cを渡さない既存呼び出しは
    従来どおり2V用の`cfg["b1"]`/`cfg["a2"]`+`_ROLE_TO_VOICE_RESOLVERS`
    (2引数版、無変更)を使い、出力はbyte単位で従来と同一。level="b1"かつ
    voice_cが指定された場合のみ、3V用`cfg["b1_3v"]`+
    `_ROLE_TO_VOICE_RESOLVERS_3V`(3引数版)を使う(level="a2"側にvoice_c
    指定時の3V分岐は無い、3VはB1のみ対応のTrial実績のため)。"""
    et = EDITORIAL_TYPES[editorial_type]
    if level == "b1" and voice_c is not None:
        cfg = et["b1_3v"]
        resolved = tuple(
            (name, _ROLE_TO_VOICE_RESOLVERS_3V[role](voice_a, voice_b, voice_c))
            for name, role in cfg["required_segments"]
        )
        return {
            "segments": resolved,
            "key_phrase_ranks": cfg["key_phrase_ranks"],
            "key_phrase_subkey_count": cfg["key_phrase_subkey_count"],
        }
    if level == "b1":
        cfg = et["b1"]
    elif level == "a2":
        cfg = et["a2"]
    else:
        raise ValueError(f"unknown level: {level!r}")
    resolved = tuple(
        (name, _ROLE_TO_VOICE_RESOLVERS[role](voice_a, voice_b))
        for name, role in cfg["required_segments"]
    )
    return {
        "segments": resolved,
        "key_phrase_ranks": cfg["key_phrase_ranks"],
        "key_phrase_subkey_count": cfg["key_phrase_subkey_count"],
    }
