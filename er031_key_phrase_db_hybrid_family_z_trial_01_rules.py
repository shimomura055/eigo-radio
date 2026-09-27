# ============================================================
# er031_key_phrase_db_hybrid_family_z_trial_01_rules.py
# KEY-PHRASE-DB-HYBRID-FAMILY-Z-CORE-APPLICABILITY-TRIAL-01
# ============================================================
# Family X向けCommon DB Hybrid Core(er029_key_phrase_db_hybrid_trial_04、
# baseline commit 57b61273)は一切変更しない(import/read-onlyのみ)。
#
# 本ファイルは、Family Z(Fiction/Story)固有の「最終選定Prompt/weight/
# category priority」差分だけを閉じ込める。Stage 1候補生成(DB照合・
# 機械screening・rare single word/quote-aware segmentation)は
# er029_key_phrase_db_hybrid_trial_04_run.run_stage1_and_shortlist_v4を
# 無変更のまま再利用し、本ファイルはそのshortlist_infoを受け取って
# 最終選定LLMへ渡すprompt文言(SELECTION_GUIDANCE相当)だけをZ条件(Z1)向けに
# 差し替える。新しいDB・新しいStage1ロジック・新しいcandidate生成規則は
# 一切追加しない。
#
# Z0(比較対照): er029の`build_lightweight_user_message_v4`
# (=base.SELECTION_GUIDANCE、"少なくとも1個は重要語区分、CEFR難易度を
# 主軸にしない"等)をそのまま使う。Z1で変える差分は以下の3点のみ:
#   (a) 本文がFiction/Story(ニュース解説記事ではない)であることの明記
#       (プロンプト注記)。
#   (b) [phrase/idiom/phrasal verb候補]区分から選ぶ最低数を1個から2個へ
#       引き上げる(category priorityの重み付け変更。良い候補が無い場合の
#       緩和ルールも明記し、無理に不自然な選定を強制しない)。
#   (c) 候補一覧に含まれない登場人物名・固有名詞は選ばない旨の明記
#       (Stage 1側は元々proper nounを候補化しないため実質的な変更は
#       生じないが、fiction特有の誤解＝「主人公の名前を重要語として
#       選んでしまう」を明示的に防ぐ注記)。
# ============================================================

from __future__ import annotations

import er028_key_phrase_db_hybrid_trial_03_run as base
import er029_key_phrase_db_hybrid_trial_04_run as run4

# --- Z0: Core標準のSELECTION_GUIDANCEをそのまま再利用する(無変更) ---
CORE_SELECTION_GUIDANCE = base.SELECTION_GUIDANCE
build_lightweight_user_message_z0 = run4.build_lightweight_user_message_v4
format_candidate_line_z0 = run4.format_candidate_line_v4

# --- Z1: Family Z固有の最終選定guidance(prompt注記+weight/category priority差分) ---
FAMILY_Z_SELECTION_GUIDANCE = """
【選定方針】
- 本文はニュース解説記事ではなく、短い物語(Fiction/Story、A2/B1向け
  Public Domain文学の書き直し)です。事実・数値の解説語彙ではなく、
  物語の展開・約束・危機・心情の変化を理解するために必要な表現を
  優先してください。
- 最終的に選ぶ5件は、必ず下記の候補一覧の中から選んでください。候補に
  無い新しい表現を作らないでください。候補一覧に登場人物名・固有名詞は
  含まれていません。含まれていない以上、登場人物名を新たに選定語として
  作らないでください。
- 5個のうち少なくとも2個は、[phrase / idiom / phrasal verb候補]区分
  (会話・行動描写に現れる複数語表現)から選んでください。同区分に
  意味が十分に自然で記事理解に重要な候補が2個に満たない場合に限り、
  1個まで減らして構いません(無理に不自然な候補を選ぶことは避ける)。
- 残りは、[重要な単語・単語群候補]区分から少なくとも1個は選んで
  ください。良い候補が不足する場合のみ[word候補]区分で補ってください。
- CEFR難易度・語彙レベルを主要な判断軸にしないでください。
- 各itemのsource_sentenceは、必ず【SENTENCE REFERENCE】に列挙されている
  文をそのまま(一字一句、改変せず)使用してください。新しい文を作らない
  でください。source_spanは、そのsource_sentence内に実際に現れる形
  (元の活用形・大文字小文字を含む)の一部分にしてください。
"""


def build_lightweight_user_message_z1(article_title: str, shortlist_info: dict,
                                       sentence_reference: dict, static_instructions: str) -> str:
    """run4.build_lightweight_user_message_v4と同じcandidate整形
    (format_candidate_line_v4、Core無変更)を使うが、末尾のSELECTION_
    GUIDANCEだけをFAMILY_Z_SELECTION_GUIDANCEへ差し替える。candidate一覧・
    shortlist・sentence referenceの中身自体はCoreが生成したshortlist_info
    をそのまま使う(Family Z側での候補の追加・削除・並べ替えは行わない)。"""
    important = [c for c in shortlist_info["shortlist"] if c.get("important_noun_phrase_candidate")]
    phrase = [c for c in shortlist_info["shortlist"]
              if not c.get("important_noun_phrase_candidate") and c["unit_type"] != "word"]
    word = [c for c in shortlist_info["shortlist"]
            if not c.get("important_noun_phrase_candidate") and c["unit_type"] == "word"]

    lines = [static_instructions.rstrip(), ""]
    lines.append(f"【Topic】title: {article_title}")
    lines.append("")
    lines.append("【重要な単語・単語群候補】")
    if important:
        lines.extend(format_candidate_line_z0(c) for c in important)
    else:
        lines.append("(なし)")
    lines.append("")
    lines.append("【phrase / idiom / phrasal verb候補】")
    if phrase:
        lines.extend(format_candidate_line_z0(c) for c in phrase)
    else:
        lines.append("(なし)")
    lines.append("")
    lines.append("【word候補】")
    if word:
        lines.extend(format_candidate_line_z0(c) for c in word)
    else:
        lines.append("(なし)")
    lines.append("")
    lines.append("【SENTENCE REFERENCE】")
    for sid in sorted(sentence_reference, key=lambda s: int(s[1:])):
        lines.append(f'{sid}: "{sentence_reference[sid]}"')
    lines.append(FAMILY_Z_SELECTION_GUIDANCE.rstrip())
    return "\n".join(lines) + "\n"
