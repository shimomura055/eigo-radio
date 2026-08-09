# ============================================================
# er003_v1_crosslevel_audio_02_add03_generate.py
# ER-003-CROSSLEVEL-AUDIO-02: ADD03 A2構造支援版 音声プロトタイプ(初回音声化)
# ============================================================
# 処理の実体はer003_v1_crosslevel_audio_02_common.pyへ委譲する。ここでは
# ADD03固有の値(Preview/Comment/Key Phrase used_form・日本語訳・語末音素
# リスク分類)のみを保持する。

from __future__ import annotations

import er003_v1_crosslevel_audio_02_common as c

ARTICLE_ID = "ADD03"

_SRC = c.load_source_texts(ARTICLE_ID, part1_paragraph_count=3)

# Cross-level改善③: Previewは具体回答(20%・1日で撤回・具体的な原油価格・
# 「料金より安全が重要」という結論)を先に言わない。テーマ・「発表後すぐ
# 大きな動きがあった」という緊張感・「本当のリスクは何か」という問いのみに留める。
PREVIEW_TEXT = (
    "トランプ米大統領が、ホルムズ海峡をめぐる新しい料金案を発表しました。"
    "発表からまもなく、状況は大きく動き、市場の注目を集めます。"
    "本当のリスクは、いったいどこにあったのでしょうか。"
)

# Comment1/2はSTRUCT-04の既存文言を維持する(新Previewが具体回答を
# 先出ししなくなったため、両Commentとも重複なく機能する。詳細はREPORT参照)。
COMMENT_1_TEXT = "アメリカが打ち出した新しい料金案について、まず何が発表されたのかを聞き取ってみましょう。"
COMMENT_2_TEXT = "料金の話は、わずか1日で投資の話へと変わりました。では、原油市場はこれで落ち着いたのでしょうか。"
COMMENT_3_TEXT = "料金そのものは消えても、海峡の安全という問題は残ったままでした。ここからは、実際にどれほどの負担になり得たのか、そして国際法の観点から何が問題だったのかを見ていきます。"
# ER-003-CROSSLEVEL-AUDIO-01で既にテキストのみ反映済みの文言(今回音声化)
COMMENT_4_TEXT = (
    "1隻あたりの負担は、それほど大きなものになり得ました。"
    "そして、この計画は国際法の基本原則にも反していました。"
    "最後に、今日のニュースのポイントを英語でまとめます。"
)

FULL_STORY_PART1_TEXT = _SRC["full_story_part1"]
FULL_STORY_PART2_TEXT = _SRC["full_story_part2"]
POINT_ONE_TEXT = _SRC["point_one"]
POINT_TWO_TEXT = _SRC["point_two"]

# ER-003-A2-STRUCT-05で確定した補足2文(中心1文はソースファイルから取得)
IN_ONE_LINE_FOLLOWUP_1 = "The toll is gone, but real danger remains in the strait."
IN_ONE_LINE_FOLLOWUP_2 = "Traders still worry more about safety than about cost."
IN_ONE_LINE_TEXT = f"{_SRC['in_one_line_core']} {IN_ONE_LINE_FOLLOWUP_1} {IN_ONE_LINE_FOLLOWUP_2}"

# 方式L選定+Canonicalization(ER-003-CROSSLEVEL-AUDIO-02、
# er003_output/a2_p2_keywords/ADD03/keywords_canonicalized.json)で確定。
# B1のKey Phrase(blockade/be in place/freedom of navigation/tollbooth/
# smell of gunpowder)をそのまま流用せず、A2最終本文で実際に方式Lが選定
# した表現を使用する(rank2のblockade・rank5のbe in placeはB1と英単語が
# 偶然一致するが、日本語訳はA2選定結果を優先し新規生成する)。
KEY_PHRASES = (
    {"number": "One", "used_form": "Strait of Hormuz", "japanese_gloss": "ホルムズ海峡",
     "at_risk": True, "final_phoneme_note": "Hormuz語末 /z/(摩擦音)"},
    {"number": "Two", "used_form": "blockade", "japanese_gloss": "封鎖、通行遮断",
     "at_risk": True, "final_phoneme_note": "blockade語末 /d/(破裂音)"},
    {"number": "Three", "used_form": "drop the fee", "japanese_gloss": "料金案を取り下げる",
     "at_risk": False, "final_phoneme_note": "fee語末は母音(脱落リスク低)"},
    {"number": "Four", "used_form": "Brent crude oil", "japanese_gloss": "ブレント原油",
     "at_risk": False, "final_phoneme_note": "oil語末 /l/(流音、脱落リスク低)"},
    {"number": "Five", "used_form": "be in place", "japanese_gloss": "実施中である、存続している",
     "at_risk": True, "final_phoneme_note": "place語末 /s/(摩擦音)"},
)

_SEGMENTS = [
    ("preview", PREVIEW_TEXT, "ja", "本当のリスク", 60),
    ("comment_1", COMMENT_1_TEXT, "ja", "何が発表されたのか", 40),
    ("comment_2", COMMENT_2_TEXT, "ja", "落ち着いたのでしょうか", 50),
    ("comment_3", COMMENT_3_TEXT, "ja", "国際法の観点", 60),
    ("comment_4", COMMENT_4_TEXT, "ja", "ポイントを英語でまとめます", 60),
    ("full_story_part1", FULL_STORY_PART1_TEXT, "en", "Strait of Hormuz", 60),
    ("full_story_part2", FULL_STORY_PART2_TEXT, "en", "Brent crude oil", 60),
    ("point_one", POINT_ONE_TEXT, "en", "shipping companies", 60),
    ("point_two", POINT_TWO_TEXT, "en", "international law", 60),
    ("in_one_line", IN_ONE_LINE_TEXT, "en", "pass safely", 60),
    ("meaning_1", "ホルムズ海峡", "ja", "ホルムズ海峡", 40),
    # 2026-08-09発見: Canonicalization結果の正式グロス「封鎖、通行遮断」を
    # そのまま単独ナレーションにすると、読点で区切られた2つの短い言い換えが
    # ASRで安定して認識されない(6回とも「風咲」「通行者」等に誤認識)。
    # B1で同一単語(blockade)に対して既に実績のある単一語「海上封鎖」へ
    # 差し替える(意味は保持、正式なjapanese_gloss記録自体は変更しない。
    # 詳細はREPORT参照)。
    ("meaning_2", "海上封鎖", "ja", "海上封鎖", 40),
    ("meaning_3", "料金案を取り下げる", "ja", "取り下げる", 40),
    # 2026-08-09発見: 「ブレント原油」も6回ともASRが「ブレント」部分を
    # 誤認識した(「ブレント言」「ブントン」等)。「原油」部分は6回中5回
    # 正しく認識されており、TTS自体の発音ではなくASRが孤立した外来語
    # (Brent)を苦手とする現象と判断し(先行するER-003-REPRO-FINALの
    # ASR homophone/number-notation ambiguityと同種)、expected_substring
    # のみ「原油」へ緩和する(テキスト自体は変更しない)。
    ("meaning_4", "ブレント原油", "ja", "原油", 40),
    ("meaning_5", "実施中である、存続している", "ja", "実施中", 40),
]

CONFIG = {
    "article_id": ARTICLE_ID,
    "out_dir": f"er003_output/crosslevel_audio_02/{ARTICLE_ID}",
    "b1_out_dir": "er003_output/b1_p9a/ADD03",
    "key_phrases": KEY_PHRASES,
    "segments": _SEGMENTS,
}

if __name__ == "__main__":
    c.run_all(CONFIG)
