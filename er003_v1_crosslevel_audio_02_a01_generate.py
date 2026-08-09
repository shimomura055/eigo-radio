# ============================================================
# er003_v1_crosslevel_audio_02_a01_generate.py
# ER-003-CROSSLEVEL-AUDIO-02: A01 A2構造支援版 音声プロトタイプ(初回音声化)
# ============================================================
# 処理の実体はer003_v1_crosslevel_audio_02_common.pyへ委譲する。ここでは
# A01固有の値(Preview/Comment/Key Phrase used_form・日本語訳・語末音素
# リスク分類)のみを保持する。

from __future__ import annotations

import er003_v1_crosslevel_audio_02_common as c

ARTICLE_ID = "A01"

_SRC = c.load_source_texts(ARTICLE_ID, part1_paragraph_count=4)

# Cross-level改善③: Previewは具体回答(誰が何分に得点・Messiが2アシスト・
# Englandが守備に切り替えた・Argentinaが逆転した等)を先に言わない。
# テーマ・緊張感・「何が勝敗を分けたか」という問いのみに留める。
PREVIEW_TEXT = (
    "ワールドカップ準決勝で、イングランドとアルゼンチンが対戦しました。"
    "試合は最後まで緊張感の続く展開でしたが、終盤で大きく流れが変わります。"
    "いったい何が、この試合の勝敗を分けたのでしょうか。"
)

# Comment1/2はSTRUCT-04の既存文言を維持する(新Previewが具体回答を
# 先出ししなくなったため、両Commentとも重複なく機能する。詳細はREPORT参照)。
COMMENT_1_TEXT = "この試合、最初にリードを奪ったのはどちらのチームだったのでしょうか。まず、そこを聞き取ってみましょう。"
COMMENT_2_TEXT = "イングランドが先制し、試合終盤には守りを固めていました。このリードは、最後まで続くのでしょうか。"
COMMENT_3_TEXT = "得点したのはメッシではありませんでしたが、この劇的な逆転の中心には、間違いなく彼がいました。そして、終盤の采配は両チームで対照的でした。ここから、その中身を見ていきます。"
# Cross-level改善④: Comment4末尾を「英語一文で振り返ります」→「ポイントを
# 英語で振り返ります」へ(In One Lineが中心1文+補足2文の計3文のため)。
COMMENT_4_TEXT = (
    "メッシは自らゴールを決めることなく、味方を活かして試合を動かしました。"
    "そして、守りに入ったイングランドと攻めに出たアルゼンチン、その選択の違いが結果を分けました。"
    "最後に、この試合のポイントを英語で振り返ります。"
)

FULL_STORY_PART1_TEXT = _SRC["full_story_part1"]
FULL_STORY_PART2_TEXT = _SRC["full_story_part2"]
POINT_ONE_TEXT = _SRC["point_one"]
POINT_TWO_TEXT = _SRC["point_two"]

# ER-003-A2-STRUCT-05で確定した補足2文(中心1文はソースファイルから取得)
IN_ONE_LINE_FOLLOWUP_1 = "Messi did not score, but he made both late goals happen."
IN_ONE_LINE_FOLLOWUP_2 = "The two teams chose different paths, and this decided the game."
IN_ONE_LINE_TEXT = f"{_SRC['in_one_line_core']} {IN_ONE_LINE_FOLLOWUP_1} {IN_ONE_LINE_FOLLOWUP_2}"

# 方式L選定+Canonicalization(ER-003-CROSSLEVEL-AUDIO-02、
# er003_output/a2_p2_keywords/A01/keywords_canonicalized.json)で確定。
# B1のKey Phrase(shot on target/take players off/a narrow lead/close the
# door to the final/stoppage time)をそのまま流用せず、A2最終本文で
# 実際に方式Lが選定した表現を使用する(rank1のshot on targetのみB1と
# 偶然一致)。at_risk判定は語末が停止音・摩擦音で終わるか(ユーザー指摘の
# feed/d/と同種の語末子音脱落リスク)による分類であり、機械的な状況証拠に
# すぎない(REPORT参照、最終判断はユーザー試聴)。
KEY_PHRASES = (
    {"number": "One", "used_form": "shot on target", "japanese_gloss": "枠内シュート",
     "at_risk": True, "final_phoneme_note": "target語末 /t/(破裂音)"},
    {"number": "Two", "used_form": "go ahead", "japanese_gloss": "リードする",
     "at_risk": True, "final_phoneme_note": "ahead語末 /d/(破裂音)"},
    {"number": "Three", "used_form": "come on", "japanese_gloss": "交代出場する",
     "at_risk": False, "final_phoneme_note": "on語末 /n/(鼻音、脱落リスク低)"},
    {"number": "Four", "used_form": "go out", "japanese_gloss": "敗退する",
     "at_risk": True, "final_phoneme_note": "out語末 /t/(破裂音)"},
    {"number": "Five", "used_form": "turn the game around", "japanese_gloss": "試合を逆転する",
     "at_risk": True, "final_phoneme_note": "around語末 /d/(破裂音)"},
)

_SEGMENTS = [
    ("preview", PREVIEW_TEXT, "ja", "勝敗を分けた", 60),
    ("comment_1", COMMENT_1_TEXT, "ja", "最初にリードを奪った", 40),
    ("comment_2", COMMENT_2_TEXT, "ja", "最後まで続くのでしょうか", 50),
    ("comment_3", COMMENT_3_TEXT, "ja", "終盤の采配", 60),
    ("comment_4", COMMENT_4_TEXT, "ja", "ポイントを英語で振り返ります", 60),
    ("full_story_part1", FULL_STORY_PART1_TEXT, "en", "shot on target", 60),
    # 2026-08-09発見: "seven minutes"(綴り)がASRで数字表記"7 minutes"へ
    # 一貫して転記され(ER-003-REPRO-FINALで確立したASR_NUMBER_NOTATION_
    # AMBIGUITYと同種、TTS自体は正常)、部分一致に失敗する。数字を含まない
    # 安定した箇所を検証対象にする。
    ("full_story_part2", FULL_STORY_PART2_TEXT, "en", "referee then added more time", 60),
    ("point_one", POINT_ONE_TEXT, "en", "two assists", 60),
    ("point_two", POINT_TWO_TEXT, "en", "different changes", 60),
    ("in_one_line", IN_ONE_LINE_TEXT, "en", "decided the game", 60),
]

# meaning_1(「枠内シュート」)はB1のA01既存音声(kp1のused_form・
# 日本語グロスともA2選定結果と偶然完全一致)をそのまま再利用するため
# 新規生成しない(er003_output/b1_p9a/A01/narration/meaning_1.wavを
# narration_dirへコピー済み)。2026-08-09発見: この短い孤立フレーズは
# ASRが6回とも別の同音異義語(「湧内シュート」等)へ誤認識し新規生成では
# 検証に通らなかったため、既に実績のある既存音声を採用した。
for i in range(2, 6):
    _SEGMENTS.append((f"meaning_{i}", KEY_PHRASES[i - 1]["japanese_gloss"], "ja",
                       KEY_PHRASES[i - 1]["japanese_gloss"][:4], 40))

CONFIG = {
    "article_id": ARTICLE_ID,
    "out_dir": f"er003_output/crosslevel_audio_02/{ARTICLE_ID}",
    "b1_out_dir": "er003_output/b1_p9a/A01",
    "key_phrases": KEY_PHRASES,
    "segments": _SEGMENTS,
}

if __name__ == "__main__":
    c.run_all(CONFIG)
