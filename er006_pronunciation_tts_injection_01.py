# ============================================================
# er006_pronunciation_tts_injection_01.py
# ER-006-PRONUNCIATION-LEDGER-SECONDARY-ASR-01: TTSへの発音ヒント注入
# ============================================================
# Pronunciation Ledgerに登録済みの固有名詞がsegmentのtextに含まれる
# 場合のみ、style instruction側へ発音ヒントを追記する。
#
# 重要な制約(タスク仕様§6を厳守):
#   - spoken text本文(text)は一切変更しない
#   - article textを書き換えない
#   - 本文の綴りをphonetic spellingへ置換しない
#   - visible scriptを変えない
#   - 固有名詞専用whitelistは作らない(Ledgerに登録された任意の固有名詞
#     が対象になる汎用ロジックであり、個別語をコードへハードコードしない)
#
# er003_b1_p4c_audio.build_tts_prompt(text, style_prefix)自体は変更せず、
# 呼び出し側でstyle_prefixだけをこの関数で拡張してから渡す(既存の
# Structured Separation構造・既存呼び出し元への影響ゼロ)。

from __future__ import annotations

import er006_pronunciation_ledger_01 as ledger

PRONUNCIATION_BLOCK_HEADER = (
    "\n\nPronunciation notes (for the proper nouns that appear in the text below only — "
    "do not alter the spelling or wording of the text itself, this is guidance for how to "
    "voice these specific words):\n"
)


def augment_style_prefix_with_pronunciation(style_prefix: str, text: str,
                                             min_confidence: str = "medium") -> tuple[str, list[dict]]:
    """textの中にLedger登録済みの固有名詞があれば、style_prefixの末尾へ
    発音ヒントを追記して返す。無ければstyle_prefixをそのまま返す。
    戻り値は(拡張後style_prefix, 使用したLedger entryのリスト)。"""
    hits = ledger.get_hint_for_text(text, min_confidence=min_confidence)
    if not hits:
        return style_prefix, []
    lines = [PRONUNCIATION_BLOCK_HEADER.strip()]
    for h in hits:
        lines.append(f'- "{h["surface"]}" is pronounced approximately "{h["pronunciation_hint"]}".')
    augmented = style_prefix.rstrip() + "\n\n" + "\n".join(lines)
    return augmented, hits
