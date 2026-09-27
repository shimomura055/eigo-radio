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


def _format_hints_block(hits: list[dict]) -> str:
    lines = [PRONUNCIATION_BLOCK_HEADER.strip()]
    for h in hits:
        lines.append(f'- "{h["surface"]}" is pronounced approximately "{h["pronunciation_hint"]}".')
    return "\n".join(lines)


def apply_precomputed_hints_to_style_prefix(style_prefix: str, hits: list[dict]) -> str:
    """PRONUNCIATION-RESOLUTION-PHASE-3(修正2回目、Opus L2所見S3是正):
    既に(Ledgerアクセス済みで)確定しているhitsリスト(`get_hint_for_text`/
    `augment_style_prefix_with_pronunciation`が返したものと同じ形状、
    `surface`/`pronunciation_hint`キーを持つdictのlist)を、Ledgerへ
    再アクセスせずそのまま別のbase style_prefix(技術的fallbackの
    MINIMAL_INSTRUCTION_PREFIX等)へ適用するための純粋な文字列整形
    ヘルパー。新規web lookup・新規Ledger読み取りは一切発生しない。
    hitsが空ならstyle_prefixをそのまま返す。"""
    if not hits:
        return style_prefix
    return style_prefix.rstrip() + "\n\n" + _format_hints_block(hits)


def augment_style_prefix_with_pronunciation(style_prefix: str, text: str,
                                             min_confidence: str = "medium") -> tuple[str, list[dict]]:
    """textの中にLedger登録済みの固有名詞があれば、style_prefixの末尾へ
    発音ヒントを追記して返す。無ければstyle_prefixをそのまま返す。
    戻り値は(拡張後style_prefix, 使用したLedger entryのリスト)。

    PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01(Sonnet修正
    1回目、Opus L2 BLOCKER-1是正(ii)): `entity_type=="cascade_unresolved_
    entity"`(ASR Cascade Human Review packaging専用、TTS注入用に設計
    されたものではない)のentryはTTS注入対象から除外する(ASR Phrase
    List用途[er003_v1_repro01_main_generate.pyの直接呼び出し]は
    `get_hint_for_text`を素通しで呼ぶため引き続き対象内、この関数
    経由のTTS注入のみを絞る)。あわせて、本番Ledgerで個別に隔離済み
    (`tts_injection_disabled=true`)のentryも除外する(4節)。"""
    hits = ledger.get_hint_for_text(
        text, min_confidence=min_confidence,
        exclude_entity_types={ledger.CASCADE_UNRESOLVED_ENTITY_TYPE},
        apply_tts_injection_filter=True)
    if not hits:
        return style_prefix, []
    return apply_precomputed_hints_to_style_prefix(style_prefix, hits), hits
