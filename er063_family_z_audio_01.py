# -*- coding: utf-8 -*-
# ============================================================
# er063_family_z_audio_01.py
# FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_04C(Family Z Audio:
# TTS / Assembly / Dialogue Voice / Gate / 減速検査 / 再利用helper / evidence /
# 試聴ページ生成)。設計は er060_output/melos_production_e2e_01/
# IMPLEMENTATION_DESIGN_02.md(M1〜M6、データ契約4-4、配置M3)。
#
# 位置づけ: DEV/Trial相当の新規Production候補module。Production正式path(X/C/A等の
# 量産経路)・共有module(er003/er011/er012/er013/er019/er020)は一切編集しない
# (import・関数呼出のみ)。X Style定数(FAMILY_X_ROLE_STYLE_EN等)も不変。
# PRODUCTION_WIREDではない(er026統合は後続)。
#
# 設計上の要点:
#  - 重い共有moduleはすべて関数内で遅延import(testでgenerator差し替え可能)。
#  - 実TTS/実LLM呼出はdry_run=Falseかつ明示的に呼んだ時のみ。dry-runは副作用ゼロ。
#  - retry/fallback/regeneration/resume/cool-down/Local Rewrite/Human Review Lockは
#    共有module(crosslevel/n3/er011/er020)の既存承認cascadeをそのまま利用する。
# ============================================================
from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import re
import shutil
from dataclasses import dataclass, field
import er078_secondary_run_scope_01 as secondary_run_scope  # AUW 委任_05
import er104_kp_vote_reuse_01 as kp_vote  # KP3V(2026-10-22、ユーザー承認APPROVED_FOR_PRODUCTION): KP英語phrase 3-ASR多数決(OpenAI・Azure・Whisper)
import er127_tts_block_policy_01 as er127   # TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_02: 統一3回構成ブロック
import er109_xz_scope_01 as er109_scope  # ASR-HOMOPHONE 委任_04: er109(表記違い同音)のrun scope(Z)。TTS段の入口decoratorだけで使う(リテラル"Z"のみ)
# 2026-10-17 委任_15: Xの承認済みStyle定数を**定数として**参照する(コピーしない)。DEFAULT_NEW_RUN_PROFILE・profile解決関数は
# 参照しない(X既定の変更がZへ無言で波及しない。Opus R-C1)。er019のimportは標準ライブラリ+er002_commonのみで循環しない。
import er019_family_x_style_profile_01 as _xs
import er062_family_z_structure_01 as _st   # story別roster/Voice表の出所(LLM呼出なし・純粋関数module)
import er117_chunk_tts_production_01 as chunk_tts   # FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01(Z Adv narrator 100語超=chunk TTS+0.2秒、APPROVED_FOR_PRODUCTION 2026-10-25 B_r1)

MANAGEMENT_ID = "FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01"
SUB_TASK_ID = "04C"
TTS_BACKEND = "speech_metadata_flash_lite"
# 注意(委任_15、Opus R-C2): 下のversion文字列は歴史的名称で、現行の実Style(PD06/S3/E1/K2/P7/P8_KP)とは一致しない。bumpしない
# (reuse_keyは実際に送るStyle文のsha[style_prefix_sha256]を含むため、Style変更したroleの旧clipは再利用されず、E1/K2/E2_UPBEAT/
# Dialogueのkeyは不変)。実際のStyle labelは各entryのstyle_label/shaおよびrun dirのaudit/style_record.jsonを正とする。
FAMILY_Z_ROLE_STYLE_VERSION = "z_v2_pd8_r2_e1_e2up_k2_m2_kpx_20261012"  # v2: Adv KP第3segment(英語解説)のStyle追加(委任_05)
DEFAULT_SLUG = "melos"
LEVEL_DIR = {"std": "a2", "adv": "b1b"}  # a2=Standard、b1b=Advanced(出力ディレクトリ名のみ。ページ表示にはラベルを出さない)
GATE_LEVEL_STRING = {"a2": "A2", "b1b": "B1"}

SLOWDOWN_RATIO_MIN = 1.03
SLOWDOWN_RATIO_MAX = 1.09

# FAMILY-Z-DIALOGUE-SPEED-PRODUCTION-WIRING-01(2026-10-23ユーザー正式決定=APPROVED_FOR_PRODUCTION、OPEN-462/UDR #159): Family Z会話速度仕様 v2。
#   (level, kind) -> 速度処理: (a2,narrator)=6%減速(従来) / (a2,dialogue)=減速なし(旧6%減速を撤去) /
#   (b1b,narrator)=処理なし(従来) / (b1b,dialogue)=生成後に約6%高速化(atempo=1.06、ピッチ保持。Trial Bと同一関数・係数)。
# 速度処理は既存`er008.apply_a2_slowdown`(pct<0=高速化)の再利用のみ。clipのspeed_profileとreuse_key(dialogueのみ)に版を載せる。
Z_SPEED_PROFILE_VERSION = "z_speed_v2"
Z_ADV_DIALOGUE_SPEEDUP_TEMPO = 1.06
Z_ADV_DIALOGUE_SLOWDOWN_PCT = (1.0 / Z_ADV_DIALOGUE_SPEEDUP_TEMPO - 1.0) * 100.0   # -5.660377... (er008のtempo=1/(1+pct/100)=1.06)
Z_STD_NARRATOR_SLOWDOWN_PCT = 6.0
ADV_DIALOGUE_RATIO_MIN, ADV_DIALOGUE_RATIO_MAX = 0.93, 0.96   # 現行wav/原音の長さ比(目標1/1.06=0.9434)
# 極短clip速度Gate(SHORT-CLIP-SPEED-GATE-01、ユーザー正式採用APPROVED_FOR_PRODUCTION 2026-10-24、UDR #181):
# 原音(speed調整前)が1.5秒未満なら比の許容は0.90〜1.00(atempoの固定10〜19ms誤差が極短clipで比に大きく出るため)。
# 1.5秒ちょうど以上は従来の0.93〜0.96。境界は厳密(`< 1.5`のみ短clip扱い)。
ADV_SHORT_CLIP_ORIGINAL_SECONDS = 1.5
ADV_SHORT_CLIP_RATIO_MIN, ADV_SHORT_CLIP_RATIO_MAX = 0.90, 1.00


def adv_dialogue_ratio_range(original_seconds: float) -> tuple:
    """Adv会話の wav/original 長さ比の許容範囲。原音<1.5秒=(0.90,1.00)、>=1.5秒=(0.93,0.96)。"""
    if original_seconds < ADV_SHORT_CLIP_ORIGINAL_SECONDS:
        return ADV_SHORT_CLIP_RATIO_MIN, ADV_SHORT_CLIP_RATIO_MAX
    return ADV_DIALOGUE_RATIO_MIN, ADV_DIALOGUE_RATIO_MAX
STD_DIALOGUE_RATIO_MIN, STD_DIALOGUE_RATIO_MAX = 0.99, 1.01  # Std会話は原音そのまま(_original.wavが残っていれば比≈1)


def speed_profile_name(level: str, kind: str):
    """(level, kind)->速度profile名。story clip(narrator/dialogue)以外はNone(速度処理の対象外=従来どおり)。"""
    table = {("a2", "narrator"): "std_narrator_slow6", ("a2", "dialogue"): "std_dialogue_none",
             ("b1b", "narrator"): "adv_narrator_none", ("b1b", "dialogue"): "adv_dialogue_fast6"}
    return table.get((level, kind))

_CLIP_ID_RE = re.compile(r"full_story_part([1-3])_c([0-9]+)")
# R2(Opus条件A): chunk id(full_story_part{n}_c{k}_k{j})を含めるのはGate箇所(速度Gate)だけ。入力検証(build_level_planのstory clip id)・
# comment_after_segment_ids・part_to_clip_idは厳密な_CLIP_ID_REのまま(親clip idだけを受ける)。group 1,2の位置は_CLIP_ID_REと同じ。
_CLIP_OR_CHUNK_ID_RE = re.compile(r"full_story_part([1-3])_c([0-9]+)(?:_k([1-9][0-9]*))?")


# ============================================================
# 例外(STOP)
# ============================================================
class FamilyZAudioStop(RuntimeError):
    """fail-closedでSTOPする全例外の基底。"""


class FamilyZSlowdownGateStop(FamilyZAudioStop):
    """M1: Std英語Story clipに6%減速証跡が無い。"""


class FamilyZTtsResultsIncompleteStop(FamilyZAudioStop):
    """M2: tts_generation_results.json不在/entry欠落/未採択。"""


class FamilyZDialogueAttributionStop(FamilyZAudioStop):
    """M5: 決定論判定とLLM判定の話者不一致。"""


class FamilyZLocalRewriteStop(FamilyZAudioStop):
    """M6: Local Rewrite後の再検証がFAIL/不可。"""


class FamilyZStyleIntegrityStop(FamilyZAudioStop):
    """Style定数のsha不一致(逐語一致が崩れた)。"""


class FamilyZRunStyleMismatchStop(FamilyZAudioStop):
    """run単位の全Role Style記録(audit/style_record.json)と現行定義が食い違う、または記録が無いのに既存の結果ファイル
    (tts_generation_results.json等)がある(委任_15、Opus R-C4。旧narrator記録[N01時代、FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01
    Opus必須7]を全Roleへ一般化)。旧Style(PD8/N01/R2/M2等)で生成済みのrun dirへ新Styleが混在するのを課金前にSTOPする。"""


FamilyZNarratorStyleMismatchStop = FamilyZRunStyleMismatchStop   # 互換alias(旧名)


class FamilyZStyleActualGateStop(FamilyZAudioStop):
    """FAMILY-Z-STYLE-ACTUAL-GATE-01(OPEN-551): 実送信Style prefixが承認値と不一致/未記録/未実測、role未カバー、Style落ちfallback採用(人間承認なし)。
    audit/style_actual_vs_approved.json に1行ずつの照合表を残してから送出する。人間承認(human_approved_segments.json、canonical text sha一致)で個別clipは解除できる。"""


class FamilyZVoiceMappingStop(FamilyZAudioStop):
    """Dialogue speakerに対応するVoiceが無い。"""


class FamilyZDialogueCtxStop(FamilyZAudioStop):
    """Z dialogue 文脈・感情付きTTS(OPEN-528、APPROVED_FOR_PRODUCTION 2026-10-26)の技術STOP(感情notes生成のLLM失敗[1回再試行後]・attempt state破損・
    従来Dialogue Styleのsha不一致・STOP sentinel中のcooldown中断など)。承認不要・再開可(消費済み試行は永続stateに残り、再開で再実行されない)。"""


def _read_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def _read_json(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: str, obj) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def _sha256_text(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


# ============================================================
# 1. Role -> Style 定数表(2026-10-17ユーザー承認 §2B: Family Xと共通のStyle仕様をZへ適用)
#    共通role(Narrator Full Story=PD06 / Std JA Preview・Comment=S3 / Adv Preview=E1 / KP英語=K2 /
#    Std KP日本語意味=P8-KP / Adv KP英語解説=P7)は、Xの承認済み定数(er019_family_x_style_profile_01)を
#    **定数として参照**する(コピーしない=二重管理の解消、PM_GOVERNANCE 28節、Opus R-C1)。
#    Xの`DEFAULT_NEW_RUN_PROFILE`・profile解決関数には**従属しない**(X既定の変更がZのProductionへ無言で波及しない。
#    Zは下の`_STYLE_SHA256`にliteral shaを固定し、X定数が変わればimport時にSTOP)。
#    Z専用の例外role(TOPIC_INTRO/J3/Adv Comment E2_UPBEAT/Dialogue/SHELL)は現状維持(origin_kind="family_z_specific")。
#    原典: E2_UPBEAT/A5/B5=er057_output/coffee_final_listening_tone_trial_01/part_AEF/prompts/。
# ============================================================
# --- Z専用(例外role)の定数 ---
_E2_UPBEAT = ("warm, upbeat and engaging; friendly conversational delivery with lively but natural intonation.")
# 参考(Zでは適用しない、shell/固定音声は既存Masterを使うため): Coffee Trial採用のA5/B5。原典照合のみ。
_A5 = "warm greeting that lands gently; the show name finishes with a soft, natural falling close, not clipped or rushed at the end."
_B5 = "friendly lead-in that lands gently; the last word settles with a soft, natural falling close, not clipped or rushed at the end."
# X既存承認Role Style(Xで運用中のTOPIC_INTRO / 日本語J3)の逐語コピー。Zはtopic_intro_en/japanese_titleに限りこれを使う
# (承認済みの共通Style表[PD06/S3/E1/K2/P7/P8-KP]に含まれない例外role。Xは不変)。
_X_TOPIC_INTRO = ("brief, clear, engaging news topic introduction with natural emphasis on the topic; "
                  "not dramatic.")
_X_JA_J3 = ("落ち着いた、自然な話し言葉で。意味の流れ・強調点・転換に応じて表情豊かに抑揚をつけてください。"
            "演技がかった話し方は避けてください。")

# 期待sha(literal固定)。共通label(PD06/S3/E1/K2/P7/P8_KP)のtextはXの承認済み定数を参照し、ここのshaと照合する
# (X側が改変されたらassert_style_table_integrityがSTOP)。
_STYLE_SHA256 = {
    "PD06": "3a680861e4d9d1bc46ddba4dc1fc91f26c68f9f9c5e5e450a85fcba7fda43c2d",
    "S3": "060c08fde003cf7c2d15c654da96d3f857b8e7a9bd79eac31814ceaf7c923f33",
    "E1": "8862317ff76693ff519ddfa956260a8cce2d540763333b54096b63161d84f641",
    "K2": "9d905cfe6c040cd001c4e7877327044f540a72bd315776f2c297e0f58f7aea42",
    "P7": "0518000694e31ef7de6602401b7fa9abd3beb45654e95714817930582020b9fc",
    "P8_KP": "b12c8721eab8434b78d129c93491c0a826f229f4528e024d58de960e1ad191e7",
    # --- Z専用 ---
    "E2_UPBEAT": "37c52d6ec2377109c4f960ac0f4693ec54f6ee1dcaf5a8fec42ad718e155553e",
    "X_TOPIC_INTRO": "d16e099cb4f6fd7f87826e48f636c143c31f3c7ad4aaeea13dd3c9ae4a3f724b",
    "X_J3": "ae68e3e6ac8e8dc29069666742ec04d64c823d4c7bdb6c0902797a2cc09fb69b",
    "A5": "2c530b21d351db177e1a808b328a0a5dbdd58850782074c5b611129b7dafdfc1",
    "B5": "5e28dd287f20588137aae35a058d4bf30da91c4bdf75bd07dd2a61d176d24989",
}
_COMMON_STYLE_LABELS = ("PD06", "S3", "E1", "K2", "P7", "P8_KP")   # Xと共通(定数参照)

_STYLE_TEXT = {
    "PD06": _xs.PD06_TEXT, "S3": _xs.SUPPORT_JA_STYLE_S3_20261017, "E1": _xs.E1_TEXT,
    "K2": _xs.K2_TEXT, "P7": _xs.P7_TEXT, "P8_KP": _xs.P8_KP_JA_TEXT,
    "E2_UPBEAT": _E2_UPBEAT, "X_TOPIC_INTRO": _X_TOPIC_INTRO, "X_J3": _X_JA_J3, "A5": _A5, "B5": _B5,
}

_ORIGIN_COMMON = "X共通定数(er019_family_x_style_profile_01.{name})を参照(2026-10-17ユーザー承認§2B)"
_ORIGIN_KIND_COMMON = "x_common_constant"
_ORIGIN_KIND_Z = "family_z_specific"

# role key -> 仕様。text=Noneは「Zで独自styleを渡さない(従来/既存Master)」。
# origin_kind: "x_common_constant"=Xと共通(X定数参照) / "family_z_specific"=Z例外(現状維持)。
FAMILY_Z_ROLE_STYLE = {
    "NARRATOR_FULL_STORY_ADV": {
        "style_label": "PD06", "text": _STYLE_TEXT["PD06"], "voice": "Aoede", "language": "en",
        "origin_kind": _ORIGIN_KIND_COMMON, "origin": _ORIGIN_COMMON.format(name="PD06_TEXT") + "(旧N01から2026-10-17置換)",
        "path": "news_tail_fix.generate_news_narration_wide_margin"},
    "NARRATOR_FULL_STORY_STD": {
        "style_label": "PD06", "text": _STYLE_TEXT["PD06"], "voice": "Aoede", "language": "en",
        "origin_kind": _ORIGIN_KIND_COMMON,
        "origin": _ORIGIN_COMMON.format(name="PD06_TEXT") + "(Std逐語・減速instruction非連結+生成後6%減速。旧N01から置換)",
        "path": "n3_tts.generate_a2_segment_with_slowdown(6%減速)"},
    "DIALOGUE_ADV": {
        "style_label": "existing_dialogue_style(ENGLISH_STYLE_PREFIX)", "text": None, "voice": "per-speaker", "language": "en",
        "origin_kind": _ORIGIN_KIND_Z,
        "origin": "family_z_specific: er012 generate_voice_body_wide_margin 既定(style_prefix_override=None)+生成後約6%高速化(2026-10-23速度仕様v2)。Narrator Styleは混入しない",
        "path": "er012.generate_voice_body_wide_margin + n3_tts.generate_with_a2_slowdown_outer_loop(slowdown_pct=-5.66)"},
    "DIALOGUE_STD": {
        # 注意: style_label末尾の"+post6%"は歴史的名称(旧6%減速)。速度仕様v2(2026-10-23)で減速は撤去済み(実際の速度処理はspeed_profile/reuse_keyが正)。
        # labelはrun単位Style記録(inspect_run_style_record)の照合対象のため、既存run/進行中runをRECORD_MISMATCHにしないようbumpしない。
        "style_label": "existing_dialogue_style(ENGLISH_STYLE_PREFIX)+post6%", "text": None, "voice": "per-speaker",
        "language": "en", "origin_kind": _ORIGIN_KIND_Z,
        "origin": "family_z_specific: Advと同一の既定Dialogue Style(style_prefix_override=None、生成時の減速指示なし)。速度後処理なし(2026-10-23速度仕様v2で旧6%減速を撤去)。Narrator Styleは混入しない",
        "path": "er012.generate_voice_body_wide_margin"},
    "STD_JA_PREVIEW": {"style_label": "S3", "text": _STYLE_TEXT["S3"], "voice": "Aoede", "language": "ja",
                       "origin_kind": _ORIGIN_KIND_COMMON,
                       "origin": _ORIGIN_COMMON.format(name="SUPPORT_JA_STYLE_S3_20261017") + "(旧R2から置換)",
                       "path": "n3_tts.generate_a2_japanese_with_reading_safety"},
    "STD_JA_COMMENT": {"style_label": "S3", "text": _STYLE_TEXT["S3"], "voice": "Aoede", "language": "ja",
                       "origin_kind": _ORIGIN_KIND_COMMON, "origin": "同上(S3)",
                       "path": "n3_tts.generate_a2_japanese_with_reading_safety"},
    "ADV_EN_PREVIEW": {"style_label": "E1", "text": _STYLE_TEXT["E1"], "voice": "Charon", "language": "en",
                       "origin_kind": _ORIGIN_KIND_COMMON, "origin": _ORIGIN_COMMON.format(name="E1_TEXT"),
                       "path": "voice01.generate_charon_english"},
    "ADV_EN_COMMENT": {"style_label": "E2_UPBEAT", "text": _STYLE_TEXT["E2_UPBEAT"], "voice": "Charon", "language": "en",
                       "origin_kind": _ORIGIN_KIND_Z,
                       "origin": "family_z_specific: prompts_E.md Baseline = er057_tone_trial_tts_gen_01.EN_COMMENT_E2_UPBEAT(Coffee Adv Comment採用。"
                                 "ユーザー§2B表に記載なし=現状維持の例外)",
                       "path": "voice01.generate_charon_english"},
    "KP_EN": {"style_label": "K2", "text": _STYLE_TEXT["K2"], "voice": "Aoede", "language": "en",
              "origin_kind": _ORIGIN_KIND_COMMON, "origin": _ORIGIN_COMMON.format(name="K2_TEXT"),
              "path": "repro01.generate_narration_snippet_verified_strict(K2 primary / 既存ENGLISH_LOCK fallback)"},
    "KP_JA": {"style_label": "P8_KP", "text": _STYLE_TEXT["P8_KP"], "voice": "Aoede", "language": "ja",
              "origin_kind": _ORIGIN_KIND_COMMON, "origin": _ORIGIN_COMMON.format(name="P8_KP_JA_TEXT") + "(旧M2から置換)",
              "path": "n3_tts.generate_a2_japanese_with_reading_safety"},
    "TOPIC_INTRO_EN": {"style_label": "X_TOPIC_INTRO", "text": _STYLE_TEXT["X_TOPIC_INTRO"], "voice": "Aoede/Charon", "language": "en",
                       "origin_kind": _ORIGIN_KIND_Z,
                       "origin": "family_z_specific: er033 FAMILY_X_ROLE_STYLE_EN['TOPIC_INTRO'] の逐語コピー(Xは不変・共通Style表の対象外)",
                       "path": "crosslevel/voice01"},
    "JAPANESE_TITLE": {"style_label": "X_J3", "text": _STYLE_TEXT["X_J3"], "voice": "Aoede", "language": "ja",
                       "origin_kind": _ORIGIN_KIND_Z,
                       "origin": "family_z_specific: er033 FAMILY_X_ROLE_STYLE_JA(J3)の逐語コピー(Xは不変・共通Style表の対象外)",
                       "path": "n3_tts.generate_a2_japanese_with_reading_safety"},
    "KP_EXPL_EN": {"style_label": "P7", "text": _STYLE_TEXT["P7"], "voice": "Aoede", "language": "en",
                   "origin_kind": _ORIGIN_KIND_COMMON,
                   "origin": _ORIGIN_COMMON.format(name="P7_TEXT") + "(旧KEY_PHRASE_EXPLANATION_EN逐語コピーから置換)",
                   "path": "er019.generate_key_phrase_explanation_en_verified"},
    "SHELL": {"style_label": "既存Master/共有Production資産(変更なし)", "text": None, "voice": "Charon", "language": "en",
              "origin_kind": _ORIGIN_KIND_Z,
              "origin": "family_z_specific: assemble_mod.B1_SHARED_SOURCE_DIR(読み取りコピーのみ、Master Store書込なし)", "path": "copy"},
}

# Cross-Family共通Style対応表(drift test用、Opus R-C7)。role -> {X: Xの定数名|None, Z: Zのlabel|"EXCEPTION:<理由>"}。
# X_profile_role/X_levelsはXのfx_20261017 profileでのrole名(drift testがX既定profileのshaと突き合わせる)。
# 共通roleのX既定が変わったらdrift testがFAILし、Z配線(またはEXCEPTION登録)を強制する。Zの解決自体はXの既定に従属しない。
CROSS_FAMILY_COMMON_STYLE_MAP = {
    "NARRATOR_FULL_STORY_ADV": {"X": "PD06_TEXT", "X_profile_role": "FULL_STORY", "X_levels": ("b1b",), "Z": "PD06"},
    "NARRATOR_FULL_STORY_STD": {"X": "PD06_TEXT", "X_profile_role": "FULL_STORY", "X_levels": ("a2",), "Z": "PD06"},
    "STD_JA_PREVIEW": {"X": "SUPPORT_JA_STYLE_S3_20261017", "X_profile_role": "SUPPORT_JA", "X_levels": ("a2",), "Z": "S3"},
    "STD_JA_COMMENT": {"X": "SUPPORT_JA_STYLE_S3_20261017", "X_profile_role": "SUPPORT_JA", "X_levels": ("a2",), "Z": "S3"},
    "ADV_EN_PREVIEW": {"X": "E1_TEXT", "X_profile_role": "PREVIEW", "X_levels": ("b1b",), "Z": "E1"},
    "KP_EN": {"X": "K2_TEXT", "X_profile_role": "KP_EN", "X_levels": ("a2", "b1b"), "Z": "K2"},
    "KP_JA": {"X": "P8_KP_JA_TEXT", "X_profile_role": "KP_JA_MEANING", "X_levels": ("a2",), "Z": "P8_KP"},
    "KP_EXPL_EN": {"X": "P7_TEXT", "X_profile_role": "KP_EXPLANATION_EN", "X_levels": ("b1b",), "Z": "P7"},
    "ADV_EN_COMMENT": {"X": None, "Z": "EXCEPTION:E2_UPBEAT(ユーザー§2B表に記載なし・Coffee採用Styleを維持)"},
    "TOPIC_INTRO_EN": {"X": None, "Z": "EXCEPTION:X既存承認TOPIC_INTRO逐語コピー(共通Style表の対象外)"},
    "JAPANESE_TITLE": {"X": None, "Z": "EXCEPTION:X既存承認J3逐語コピー(共通Style表の対象外)"},
    "DIALOGUE_ADV": {"X": None, "Z": "EXCEPTION:Dialogueは既存speaker assignment/Dialogue Style/Voiceを尊重(ユーザー§2B)"},
    "DIALOGUE_STD": {"X": None, "Z": "EXCEPTION:Dialogueは既存speaker assignment/Voiceを尊重(ユーザー§2B)。Std Dialogue生成時StyleはAdv同一の既定Dialogue Style(2026-10-19決定③)"},
    "SHELL": {"X": None, "Z": "EXCEPTION:既存Master/共有資産(TTSなし)"},
}

# 実装時の原典ファイル照合対象 (label -> (relative path, locator))。locator: "## 見出し"=mdのコードブロック /
# "py:<変数>:<key>[:<idx>]"=pyの辞書リテラル。runtimeでは呼ばない(verify_styles_against_origin専用)。
_ORIGIN_FILES = {
    "PD06": ("er057_output/pace_trial_02/prompts/prompts_pace_02.md", "## PD6"),
    "S3": ("er057_output/ja_support_calm_style_trial_04/PROMPTS_01.md", "## S3"),
    "E1": ("er057_output/coffee_final_listening_tone_trial_01/part_AEF/prompts/prompts_E.md", "## E1"),
    "K2": ("er057_output/coffee_final_listening_tone_trial_01/part_BCD/prompts/prompts_B.md", "## K2"),
    "P7": ("er080_coffee_kp_pacing_trial_01.py", "py:PROMPTS:p7:1"),
    "P8_KP": ("er057_std_kp_ja_style_trial_02.py", "py:PROMPTS:P8"),
    "A5": ("er057_output/coffee_final_listening_tone_trial_01/part_AEF/prompts/prompts_A.md", "## A5"),
    "B5": ("er057_output/coffee_final_listening_tone_trial_01/part_AEF/prompts/prompts_B.md", "## B5"),
}


def style_prefix_sha256(text) -> str | None:
    return None if text is None else _sha256_text(text)


def assert_style_table_integrity() -> dict:
    """runtime assert: (1)各label textのsha256がZ側literal固定値と一致(X共通定数が改変されたらSTOP) (2)全roleのtextが
    自labelのtextと一致し、text有りのroleはlabelが固定sha表に存在 (3)共通labelのroleはorigin_kind=x_common_constant、
    それ以外はfamily_z_specific。Trialファイルへのruntime依存なし。"""
    report = {}
    for key, text in _STYLE_TEXT.items():
        actual = _sha256_text(text)
        if actual != _STYLE_SHA256[key]:
            raise FamilyZStyleIntegrityStop(f"Z Style定数 {key} のsha256が記録値と不一致: {actual} != {_STYLE_SHA256[key]}")
        report[key] = actual
    for role, spec in FAMILY_Z_ROLE_STYLE.items():
        if spec["text"] is not None:
            if spec["style_label"] not in _STYLE_SHA256:
                raise FamilyZStyleIntegrityStop(f"role {role} のstyle_label {spec['style_label']!r} が固定sha表にありません")
            if _sha256_text(spec["text"]) != _STYLE_SHA256[spec["style_label"]]:
                raise FamilyZStyleIntegrityStop(f"role {role} のtextがStyle {spec['style_label']} と一致しません")
        common = spec["style_label"] in _COMMON_STYLE_LABELS
        if (spec["origin_kind"] == _ORIGIN_KIND_COMMON) != common:
            raise FamilyZStyleIntegrityStop(
                f"role {role} のorigin_kind={spec['origin_kind']} がstyle_label {spec['style_label']} と整合しません")
    return report


def role_style_sha256(role_key: str):
    return style_prefix_sha256(FAMILY_Z_ROLE_STYLE[role_key]["text"])


def _extract_fenced_after(path: str, heading: str) -> str:
    t = _read_text(path)
    i = t.index(heading)
    m = re.search(r"```\n(.*?)\n```", t[i:], re.S)
    return m.group(1)


def _extract_py_dict_value(path: str, var: str, key: str, idx: int | None):
    import ast
    tree = ast.parse(_read_text(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == var for t in node.targets):
            d = ast.literal_eval(node.value)
            v = d[key]
            return v[idx] if idx is not None else v
    raise KeyError(f"{path}: {var}[{key}] not found")


def verify_styles_against_origin(repo_root: str = ".") -> dict:
    """実装時1回(および任意のevidence再生成)用: 原典ファイルから逐語抽出しsha256を照合する。
    runtimeでは呼ばない(Trialファイルへのruntime依存を作らない)。原典照合先: PD06=pace_trial_02 ## PD6 /
    S3=ja_support_calm_style_trial_04 ## S3 / E1,K2=coffee_final_listening_tone_trial_01 / P7=er080 PROMPTS['p7'][1] /
    P8_KP=er057_std_kp_ja_style_trial_02 PROMPTS['P8']。"""
    out = {}
    for key, (rel, loc) in _ORIGIN_FILES.items():
        p = os.path.join(repo_root, rel)
        if loc.startswith("py:"):
            parts = loc.split(":")
            text = _extract_py_dict_value(p, parts[1], parts[2], int(parts[3]) if len(parts) > 3 else None)
        else:
            text = _extract_fenced_after(p, loc)
            if key == "PD06":
                text = text.strip()
        sha = _sha256_text(text)
        out[key] = {"origin": rel, "locator": loc, "origin_sha256": sha, "z_sha256": _STYLE_SHA256[key],
                    "verbatim_match": sha == _STYLE_SHA256[key] and text == _STYLE_TEXT[key]}
    # E2_UPBEAT: prompts_E.md Baseline(1行コード)
    p = os.path.join(repo_root, "er057_output/coffee_final_listening_tone_trial_01/part_AEF/prompts/prompts_E.md")
    t = _read_text(p)
    base = re.search(r"## Baseline\(現行Style\)\s*\n\s*`([^`]+)`", t).group(1)
    out["E2_UPBEAT"] = {"origin": "part_AEF/prompts/prompts_E.md Baseline", "origin_sha256": _sha256_text(base),
                        "z_sha256": _STYLE_SHA256["E2_UPBEAT"],
                        "verbatim_match": base == _E2_UPBEAT}
    return out


# ============================================================
# 2. Dialogue Voice(Melos別Voiceは「設定追加」のみで既存機構に載る)
#    機構: er013_family_c_production_01.classify_quote_voice_window / build_flat_voice_chunks は
#    voice_keywords(任意のvoice名->keyword)を受け取り、er012.generate_voice_body_wide_margin は
#    任意のvoice_nameを受け取る。コード変更不要。
#    Voice名の割当(narrator=Aoede / selinuntius=Erinome / dionysius=Charon)は
#    er026 STORY_REGISTRY['melos']['voice_tts_names_plan']の参照先(Z-4)に従う。
#    Voice値は er062 の正式Voice表+決定的割当規則(+メロスのpin)から導出される(2026-10-23 APPROVED_FOR_PRODUCTION)。
# ============================================================
# 値の出所は er062_family_z_structure_01.STORY_SPEAKER_CONFIG(story別、Melos=従来値。二重定義せず同一objectを参照)。
FAMILY_Z_DIALOGUE_VOICE_KEYWORDS = _st.STORY_SPEAKER_CONFIG["melos"]["dialogue_voice_keywords"]
FAMILY_Z_DIALOGUE_VOICE_TTS_NAMES = _st.STORY_SPEAKER_CONFIG["melos"]["dialogue_voice_tts_names"]
MELOS_VOICE_STATUS = "APPROVED_FOR_PRODUCTION"   # Algieba=正式男性Voice 1位(2026-10-23ユーザー最終決定)。メロスはpinで既存確定値を維持


# er062(04B)のsegment_planは speaker=melos/king/friend/other、voice_role=dialogue:<speaker> を出す。
# er063のVoice割当(Z-4: dionysius=Charon / selinuntius=Erinome)へ写像する。other等は未対応でSTOP。
SPEAKER_ALIASES = _st.STORY_SPEAKER_CONFIG["melos"]["speaker_aliases"]


def normalize_speaker(raw: str, story_key: str = "melos") -> str:
    key = (raw or "narrator").split(":")[-1]
    aliases = _st.STORY_SPEAKER_CONFIG[story_key]["speaker_aliases"]
    if key not in aliases:
        raise FamilyZVoiceMappingStop(f"未対応のspeaker {raw!r}(対応: {sorted(aliases)})")
    return aliases[key]


def resolve_dialogue_voice(speaker: str, story_key: str = "melos") -> str:
    names = _st.STORY_SPEAKER_CONFIG[story_key]["dialogue_voice_tts_names"]
    try:
        voice = names[speaker]
    except KeyError:
        raise FamilyZVoiceMappingStop(f"speaker={speaker!r} に対応するVoiceがFAMILY_Z_DIALOGUE_VOICE_TTS_NAMESにありません")
    if voice is None:   # 値欠落(未割当=ユーザー判断待ち)の検出。fail-closed(新Gateではない)
        raise FamilyZVoiceMappingStop(
            f"VOICE_UNASSIGNED: story={story_key!r} speaker={speaker!r} のVoiceが未割当です(ユーザー判断待ち。自動割当しない)")
    return voice


def check_melos_voice_mechanism() -> dict:
    """STOP条件の機械確認: 既存Dialogue Voice機構にコード変更なしでmelos別Voiceが載ることを実関数で検証する。"""
    import er013_family_c_production_01 as fam_c
    para = '"I will return," Melos said.'
    chunks = fam_c.build_flat_voice_chunks([para], FAMILY_Z_DIALOGUE_VOICE_KEYWORDS)
    voices = [v for (_p, v, _r) in chunks]
    return {"chunks": [(v, r) for (_p, v, r) in chunks], "melos_quote_routed": "melos" in voices,
            "melos_voice": resolve_dialogue_voice("melos"), "status": MELOS_VOICE_STATUS}


# ------------------------------------------------------------
# M5: 話者判定(決定論 vs LLM。不一致が1件でもあればSTOP、自動採用しない)
# ------------------------------------------------------------
def extract_quotes(paragraphs: list, voice_keywords: dict | None = None, default_voice: str = "narrator") -> list:
    import er013_family_c_production_01 as fam_c
    kw = voice_keywords or FAMILY_Z_DIALOGUE_VOICE_KEYWORDS
    quotes = []
    for pi, para in enumerate(paragraphs):
        for qi, m in enumerate(fam_c.DEFAULT_QUOTE_RE.finditer(para)):
            voice = fam_c.classify_quote_voice_window(para, m.start(), m.end(), kw, default_voice=default_voice)
            quotes.append({"quote_id": f"p{pi}_q{qi}", "paragraph_index": pi, "quote": m.group(0),
                           "deterministic_voice": voice,
                           "context": para[max(0, m.start() - 120): m.end() + 120]})
    return quotes


def compare_attribution(quotes: list, llm_voices: dict) -> list:
    mismatches = []
    for q in quotes:
        llm_v = llm_voices.get(q["quote_id"])
        if llm_v != q["deterministic_voice"]:
            mismatches.append({"quote_id": q["quote_id"], "quote": q["quote"], "context": q["context"],
                               "deterministic_voice": q["deterministic_voice"], "llm_voice": llm_v})
    return mismatches


def assert_dialogue_attribution(paragraphs: list, llm_fn, out_dir: str | None = None, level: str = "") -> dict:
    """全引用について決定論判定とLLM判定を照合する。llm_fn(quotes)->{quote_id: voice}。
    不一致があれば dialogue_override.json に両案を記録してSTOP(人間判断)。一致時のみ確定voice mapを返す。"""
    quotes = extract_quotes(paragraphs)
    llm_voices = llm_fn(quotes) if quotes else {}
    mismatches = compare_attribution(quotes, llm_voices)
    record = {"level": level, "quote_count": len(quotes), "mismatches": mismatches, "quotes": quotes,
              "llm_voices": llm_voices, "status": "STOP_MISMATCH" if mismatches else "AGREED"}
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        with open(f"{out_dir}/dialogue_attribution{('_' + level) if level else ''}.json", "w", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
        if mismatches:
            with open(f"{out_dir}/dialogue_override{('_' + level) if level else ''}.json", "w", encoding="utf-8") as f:
                json.dump({"note": "決定論判定とLLM判定が不一致。自動採用しない。人間判断が必要。", "mismatches": mismatches},
                          f, ensure_ascii=False, indent=2)
    if mismatches:
        raise FamilyZDialogueAttributionStop(
            f"話者判定が{len(mismatches)}件不一致(決定論 vs LLM)。dialogue_override.jsonを確認してください: "
            f"{[m['quote_id'] for m in mismatches]}")
    return {q["quote_id"]: q["deterministic_voice"] for q in quotes}


def default_llm_attribution_fn(client=None):
    """実LLM版(routing FAMILY_Z_DIALOGUE_ATTRIBUTION=gpt-6-luna、各レベル1 call)。dry-run/testでは呼ばない。"""
    def _fn(quotes: list) -> dict:
        import er003_v1_b1_scaffold_01_generate as b1s
        import er006_model_routing_contract_01 as routing
        _check_stop_sentinel(None, "client:er063_attribution")      # 委任_12A: client生成前にSTOP確認
        c = client or b1s.get_client()
        model = routing.require_model("FAMILY_Z_DIALOGUE_ATTRIBUTION", "gpt-6-luna")
        speakers = list(FAMILY_Z_DIALOGUE_VOICE_KEYWORDS) + ["narrator"]
        prompt = ("Each item is a quoted line from a story with its surrounding text. Decide who actually SPEAKS the quoted "
                  f"words (not who is merely mentioned). Allowed speakers: {speakers}. Return JSON "
                  '{"items":[{"quote_id":"...","speaker":"..."}]} covering every quote_id.\n\n'
                  + json.dumps([{"quote_id": q["quote_id"], "quote": q["quote"], "context": q["context"]} for q in quotes],
                               ensure_ascii=False))
        resp = c.responses.create(model=model, input=[{"role": "user", "content": prompt}])
        raw = (resp.output_text or "").strip()
        m = re.search(r"\{.*\}", raw, re.S)
        data = json.loads(m.group(0))
        return {it["quote_id"]: it["speaker"] for it in data.get("items", [])}
    return _fn


# ============================================================
# 3. Clip仕様 / 配置(M3) / segment_id導出
# ============================================================
@dataclass
class ClipSpec:
    clip_id: str                 # Family Cが読むasset名(拡張子なし)。例 full_story_part1_c2 / comment_1 / kp1_en
    level: str                   # "a2" | "b1b"
    kind: str                    # narrator|dialogue|preview|comment|topic_intro|japanese_title|kp_en|kp_ja
    text: str                    # canonical text(原稿)
    voice: str = ""
    speaker: str = "narrator"
    role_key: str = ""
    part: int | None = None
    language: str = "en"
    rank: int | None = None
    extra: dict = field(default_factory=dict)

    def wav_name(self) -> str:
        return f"{self.clip_id}.wav"


def narration_dir_for(run_dir: str, level: str) -> str:
    return f"{run_dir}/{level}/narration".replace("\\", "/")


def derive_segment_id(out_path: str) -> str:
    import er011_human_review_lock_01 as review_lock
    return review_lock.derive_segment_key(out_path)[2]


def layout_is_valid(out_path: str) -> bool:
    import er011_human_review_lock_01 as review_lock
    return review_lock._has_valid_narration_layout(out_path)


def role_key_for(kind: str, level: str, speaker: str = "narrator") -> str:
    adv = level == "b1b"
    if kind == "narrator":
        return "NARRATOR_FULL_STORY_ADV" if adv else "NARRATOR_FULL_STORY_STD"
    if kind == "dialogue":
        return "DIALOGUE_ADV" if adv else "DIALOGUE_STD"
    if kind == "preview":
        return "ADV_EN_PREVIEW" if adv else "STD_JA_PREVIEW"
    if kind == "comment":
        return "ADV_EN_COMMENT" if adv else "STD_JA_COMMENT"
    if kind == "kp_en":
        return "KP_EN"
    if kind == "kp_ja":
        return "KP_JA"
    if kind == "kp_expl_en":
        return "KP_EXPL_EN"
    if kind == "topic_intro":
        return "TOPIC_INTRO_EN"
    if kind == "japanese_title":
        return "JAPANESE_TITLE"
    raise ValueError(kind)


def build_level_plan(level: str, story_clips: list, preview_text: str, comments: dict, kp_items: list,
                     topic_title: str, japanese_title_text: str | None = None,
                     kp_explanations: dict | None = None, story_key: str = "melos", chunk_plans: dict | None = None) -> list:
    """生成が必要なClipSpec列を組む。story_clips=[{id,part,voice(speaker key or 'narrator'),text}]。
    shell/番号(welcome等)は provision_shell_assets で別途コピー(TTSなし)。
    chunk_plans(FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01): {親clip_id: chunk plan}。chunked=Trueの親(Adv narrator 100語超)は親ClipSpecを作らず、
    chunk ClipSpec(clip_id=<親>_k<j>、kind=narrator、extra.chunk=…)へ展開する。None/空/chunked=Falseなら従来と同一(バイト不変)。"""
    plan = []
    adv = level == "b1b"
    plan.append(ClipSpec("topic_intro_en", level, "topic_intro", f"Today's topic is {topic_title}.",
                         voice="Charon" if adv else "Aoede", role_key="TOPIC_INTRO_EN", language="en"))
    if not adv:
        if not japanese_title_text:
            raise FamilyZAudioStop("Std(a2)にはjapanese_title_textが必要です")
        plan.append(ClipSpec("japanese_title", level, "japanese_title", japanese_title_text, voice="Aoede",
                             role_key="JAPANESE_TITLE", language="ja"))
    plan.append(ClipSpec("preview", level, "preview", preview_text, voice="Charon" if adv else "Aoede",
                         role_key=role_key_for("preview", level), language="en" if adv else "ja"))
    for n in (1, 2, 3):
        plan.append(ClipSpec(f"comment_{n}", level, "comment", comments[n], voice="Charon" if adv else "Aoede",
                             role_key=role_key_for("comment", level), language="en" if adv else "ja"))
    for it in sorted(kp_items, key=lambda x: x["rank"]):
        r = it["rank"]
        plan.append(ClipSpec(f"kp{r}_en", level, "kp_en", it["used_form"], voice="Aoede", role_key="KP_EN", rank=r, language="en"))
        if kp_explanations is not None:
            # 委任_05: KP第3segmentは英語解説(Coffee最終v3 Adv / X B1と同一構成)。kp{r}_ja は作らない。
            expl = (kp_explanations.get(r) or kp_explanations.get(str(r)) or "").strip()
            if not expl:
                raise FamilyZAudioStop(f"KP{r}の英語解説textがありません(fail-closed)")
            plan.append(ClipSpec(f"kp{r}_explanation_en", level, "kp_expl_en", expl, voice="Aoede", role_key="KP_EXPL_EN",
                                 rank=r, language="en", extra={"used_form": it["used_form"]}))
            continue
        ja = it.get("japanese_gloss_tts") or it.get("japanese_gloss")
        plan.append(ClipSpec(f"kp{r}_ja", level, "kp_ja", ja, voice="Aoede", role_key="KP_JA", rank=r, language="ja",
                             extra={"used_form": it["used_form"]}))
    for c in story_clips:
        m = _CLIP_ID_RE.fullmatch(c["id"])
        if not m:
            raise FamilyZAudioStop(f"story clip id {c['id']!r} が full_story_part[1-3]_c[0-9]+ に一致しません")
        speaker = normalize_speaker(c.get("speaker") or c.get("voice_role") or c.get("voice") or "narrator", story_key)
        kind = "narrator" if speaker == "narrator" else "dialogue"
        voice = resolve_dialogue_voice(speaker, story_key)
        cp = (chunk_plans or {}).get(c["id"])
        if cp and cp.get("chunked") and kind == "narrator" and level in ("b1b", "a2"):   # CHUNK-TTS-STD 委任_03(M3): Stdも展開(dialogueは対象外のまま)
            n = len(cp["chunks"])
            for ch in cp["chunks"]:
                plan.append(ClipSpec(ch["chunk_id"], level, kind, ch["text"], voice=voice, speaker=speaker,
                                     role_key=role_key_for(kind, level, speaker), part=int(m.group(1)), language="en",
                                     extra={"chunk": {"parent_id": c["id"], "index": ch["index"], "count": n, "words": ch["words"],
                                                      "boundary_kind": ch["boundary_kind"], "planner_version": cp["planner_version"],
                                                      "parent_text": c["text"], "paragraph_info_lost": cp.get("paragraph_info_lost")}}))
            continue
        plan.append(ClipSpec(c["id"], level, kind, c["text"], voice=voice, speaker=speaker,
                             role_key=role_key_for(kind, level, speaker), part=int(m.group(1)), language="en"))
    return plan


def chunk_plans_from_specs(plan: list) -> dict:
    """ClipSpec列から {親clip_id: chunk plan dict} を再構成する(chunk specだけ。plan(原稿)から導出するので保存済みplanは不要)。"""
    out = {}
    for s in plan:
        ch = (s.extra or {}).get("chunk")
        if not ch:
            continue
        p = out.setdefault(ch["parent_id"], {
            "parent_id": ch["parent_id"], "family": "Z", "chunked": True, "planner_version": ch["planner_version"],
            "parent_text": ch["parent_text"], "parent_text_sha256": _sha256_text(ch["parent_text"]),
            "extra_pause_seconds": chunk_tts.EXTRA_PAUSE_SECONDS, "paragraph_info_lost": ch.get("paragraph_info_lost"), "chunks": [],
            "level": s.level, "voice": s.voice, "speaker": s.speaker, "role_key": s.role_key})
        p["chunks"].append({"chunk_id": s.clip_id, "index": ch["index"], "text": s.text, "words": ch["words"], "boundary_kind": ch["boundary_kind"]})
    for p in out.values():
        p["chunks"].sort(key=lambda c: c["index"])
    return out


def _z_chunk_parent_display(plan: dict, segments: dict) -> dict:
    """I7: 親集約entryの表示用項目(ページ行が「-」「未取得」にならない)。Style記録はchunk側が正(親へ複製しない)。"""
    rk = plan["role_key"]
    first = segments.get(plan["chunks"][0]["chunk_id"]) or {}
    sha = ((first.get("style") or {}).get("style_prefix_sha256"))
    disp = {"voice": plan["voice"], "speaker": plan["speaker"], "clip_kind": "narrator", "role_style_key": rk,
            "role": "FULL_STORY", "tts_backend": TTS_BACKEND, "slowdown_applied": None,
            "style": {"instruction_label": FAMILY_Z_ROLE_STYLE[rk]["style_label"] + "(chunked, see chunk_tts)", "style_prefix_sha256": sha},
            "z_adoption": "adopted" if all((segments.get(c["chunk_id"]) or {}).get("z_adoption") in ("adopted", "human_review_adopted")
                                           for c in plan["chunks"]) else "failed"}
    if plan.get("level") == chunk_tts.STD_LEVEL:
        # CHUNK-TTS-STD 委任_03(Opus M3): Stdの親は『全chunkがchunk単位で6%減速済み』のときだけ slowdown_applied=True(明示True/False。
        # 古い親_original.wavの弱い証拠へ落ちない)。Adv(b1b)は従来どおりNone=バイト不変(速度Gateの『Adv Narratorに速度後処理なし』検査を維持)。
        disp.update(chunk_tts.std_parent_slowdown_fields(plan, segments))
    return disp


def refresh_chunk_parents(level_dir: str, plan: list, segments: dict) -> dict:
    """M2(a)(b)(d): chunk化した親clipの集約entryを(再)構築して segments に書く(冪等。失敗・未生成でも常に書く)。TTS stage末尾と、
    gate/assembleの入口で呼ぶ(STOPPED chunkの人間承認後に親entry・親wavが古い/無いのを防ぐ)。"""
    import er003_v1_n3_01_assemble as asm
    ap = f"{level_dir}/audit/human_approved_segments.json"
    approvals = _read_json(ap) if os.path.exists(ap) else {}
    out = {}
    narr = f"{level_dir}/narration"
    for pid, pl in chunk_plans_from_specs(plan).items():
        out[pid] = chunk_tts.refresh_parent_status(pl, segments, approvals, asm._segment_gate_status, narration_dir=narr,
                                                   parent_text=pl["parent_text"], display=_z_chunk_parent_display(pl, segments))
    return out


# ============================================================
# 3-N. run単位の全Role Style記録(委任_15、Opus R-C4): 旧narrator記録(N01時代)を全Roleへ一般化。
#      (a) run dirのaudit/style_record.jsonに全Role(Dialogue/SHELL含む)のstyle_label/style_prefix_sha256/origin_kindを記録し、
#          既存recordと現行定義が不一致なら課金前にSTOP。
#      (b) recordが無いのに既存の結果ファイル(tts_generation_results.json/tts_checkpoint.json/review_lock_state.json/
#          human_approved_segments.json)が存在する場合も課金前にSTOP(Xの_RUN_STATE_FILES方式[er019:291-293]を踏襲)。
#          Review Lock/人間承認はtext shaのみで照合されStyleを区別しないため、旧Style(PD8/N01/R2/M2等)のrunへ新Styleのclipを
#          混在させたり、旧Styleの承認を新Styleの音声へ流用したりしない。
# ============================================================
STYLE_RECORD_RELPATH = "audit/style_record.json"
STYLE_RECORD_SCHEMA = "family_z_style_record_v1"
LEGACY_NARRATOR_STYLE_RECORD_RELPATH = "audit/narrator_style_record.json"   # 旧(N01時代)。もう記録として扱わない
RUN_STATE_FILES = ("tts_generation_results.json", "tts_checkpoint.json", "review_lock_state.json", "human_approved_segments.json")


def expected_style_record(level: str) -> dict:
    """現行定義から期待する全Role Style記録(role -> label/sha/origin_kind)。Dialogue/SHELLはtext=Noneのためshaはnull。"""
    roles = {}
    for role, spec in FAMILY_Z_ROLE_STYLE.items():
        roles[role] = {"style_label": spec["style_label"], "style_prefix_sha256": style_prefix_sha256(spec["text"]),
                       "origin_kind": spec["origin_kind"]}
    return {"schema": STYLE_RECORD_SCHEMA, "level": level, "roles": roles}


def existing_run_state_files(level_dir: str) -> list:
    return [f"{level_dir}/audit/{n}" for n in RUN_STATE_FILES if os.path.exists(f"{level_dir}/audit/{n}")]


def inspect_run_style_record(level_dir: str, level: str) -> dict:
    """読み取りのみ。status: NEW_RUN / RECORD_MATCH / RECORD_MISMATCH / RUN_STATE_WITHOUT_RECORD。
    RECORD_MISMATCH・RUN_STATE_WITHOUT_RECORDは呼び出し側でSTOPする。"""
    exp = expected_style_record(level)
    rec_path = f"{level_dir}/{STYLE_RECORD_RELPATH}"
    if os.path.exists(rec_path):
        rec = _read_json(rec_path)
        diffs = []
        rec_roles = rec.get("roles") or {}
        for role in sorted(set(exp["roles"]) | set(rec_roles)):
            e, r = exp["roles"].get(role), rec_roles.get(role)
            if e is None or r is None or any(e.get(k) != r.get(k) for k in ("style_label", "style_prefix_sha256", "origin_kind")):
                diffs.append({"role": role, "expected": e, "recorded": r})
        return {"status": "RECORD_MATCH" if not diffs and rec.get("schema") == STYLE_RECORD_SCHEMA else "RECORD_MISMATCH",
                "expected": exp, "recorded": rec, "diffs": diffs}
    state = existing_run_state_files(level_dir)
    if state:
        return {"status": "RUN_STATE_WITHOUT_RECORD", "expected": exp, "run_state_files": state,
                "legacy_narrator_record_exists": os.path.exists(f"{level_dir}/{LEGACY_NARRATOR_STYLE_RECORD_RELPATH}")}
    return {"status": "NEW_RUN", "expected": exp}


def assert_run_style_record(level_dir: str, level: str, *, write: bool = True) -> dict:
    info = inspect_run_style_record(level_dir, level)
    if info["status"] == "RECORD_MISMATCH":
        raise FamilyZRunStyleMismatchStop(
            f"[STOP][Z-STYLE] {level_dir} の全Role Style記録が現行定義と一致しません: {info['diffs']}。"
            "run内でStyleが混在するため課金前にSTOPしました(新規run dirで実行してください。記録は変更していません)。")
    if info["status"] == "RUN_STATE_WITHOUT_RECORD":
        raise FamilyZRunStyleMismatchStop(
            f"[STOP][Z-STYLE] {level_dir} にStyle記録({STYLE_RECORD_RELPATH})が無いのに既存の結果ファイルがあります: "
            f"{info['run_state_files']}。旧Style(PD8/N01/R2/M2等)で生成済みのrunの可能性があり、Review Lock/人間承認はStyleを区別しないため、"
            "課金前にSTOPしました(新規run dirで実行してください。結果ファイルは変更していません)。")
    if write and info["status"] == "NEW_RUN":
        os.makedirs(f"{level_dir}/audit", exist_ok=True)
        _write_json(f"{level_dir}/{STYLE_RECORD_RELPATH}", {**info["expected"], "management_id": MANAGEMENT_ID,
                                                           "role_style_version": FAMILY_Z_ROLE_STYLE_VERSION})
    return info


# ============================================================
# 3-C. 新runへの再利用copyの許可リスト(委任_15、Opus R-C4)。音声(wav)・tts結果・HR承認/Lock・audit・narration・assemblyは
#      持ち込まない(新runで全Roleを再生成する。取り込み機構は作らない)。許可=テキスト系の確定成果物のみ。
#      ルールはdeny優先 -> allow -> 既定deny。pathはrun dirからの相対path(posix区切り)。
# ============================================================
REUSE_ALLOW_PREFIXES = ("writer/", "support/", "key_phrases/")
REUSE_ALLOW_PATTERNS = ("segment_plan_*.json", "dialogue_attribution_*.json", "speaker_table.md", "provenance.json")
REUSE_DENY_DIR_SEGMENTS = ("audit", "narration", "assembly", "attempts")   # 任意の深さで拒否
REUSE_DENY_TOP_DIRS = ("a2", "b1b")   # run直下のlevel dir(音声・audit・assembly・導入済みkp asset)は丸ごと持ち込まない
REUSE_DENY_NAME_PATTERNS = ("tts_generation_results*.json", "tts_checkpoint*.json", "review_lock_state*.json",
                            "human_approved_segments*.json", "*_pending_result.json", "*.consumed.json", "*.consumed",
                            "STOP", "STOP_ALL", "audit_stop_sentinel.jsonl", "*.wav", "*.mp3", "cost_log.jsonl",
                            "e2e_stage_log.jsonl", "run_launch_log.jsonl", "page_verify_local.json", "*snapshot*")


def classify_reuse_path(rel_path: str) -> tuple:
    """(\"ALLOW\"|\"DENY\", reason)。rel_pathはrun dirからの相対path。"""
    import fnmatch
    rel = rel_path.replace("\\", "/").lstrip("./")
    parts = rel.split("/")
    name = parts[-1]
    if len(parts) > 1 and parts[0] in REUSE_DENY_TOP_DIRS:
        return "DENY", f"deny_top_dir:{parts[0]}"
    for seg in parts[:-1]:
        if seg in REUSE_DENY_DIR_SEGMENTS:
            return "DENY", f"deny_dir:{seg}"
    for pat in REUSE_DENY_NAME_PATTERNS:
        if fnmatch.fnmatch(name, pat):
            return "DENY", f"deny_name:{pat}"
    if any(rel.startswith(pref) for pref in REUSE_ALLOW_PREFIXES):
        return "ALLOW", "allow_prefix"
    for pat in REUSE_ALLOW_PATTERNS:
        if fnmatch.fnmatch(name, pat) and len(parts) == 1:
            return "ALLOW", f"allow_pattern:{pat}"
    if rel == "writer/provenance.json":
        return "ALLOW", "allow_provenance"
    return "DENY", "default_deny"


def plan_reusable_run_assets(src_run_dir: str) -> dict:
    """読み取りのみ。src runの全fileを許可リストで分類する。"""
    allow, deny = [], []
    for root, _dirs, files in os.walk(src_run_dir):
        for fn in files:
            full = os.path.join(root, fn)
            rel = os.path.relpath(full, src_run_dir).replace("\\", "/")
            verdict, reason = classify_reuse_path(rel)
            (allow if verdict == "ALLOW" else deny).append({"path": rel, "reason": reason})
    return {"allow": sorted(allow, key=lambda d: d["path"]), "deny": sorted(deny, key=lambda d: d["path"])}


def copy_reusable_run_assets(src_run_dir: str, dst_run_dir: str, *, dry_run: bool = True) -> dict:
    """許可リストに該当するfileのみを新run dirへcopyする(dry_run既定True)。dstに既に結果ファイル/Style記録がある場合はSTOP。"""
    if os.path.abspath(src_run_dir) == os.path.abspath(dst_run_dir):
        raise FamilyZRunStyleMismatchStop("[STOP][Z-REUSE] src_run_dir と dst_run_dir が同一です")
    for lv in ("a2", "b1b"):
        if existing_run_state_files(f"{dst_run_dir}/{lv}"):
            raise FamilyZRunStyleMismatchStop(f"[STOP][Z-REUSE] dstに既存の結果ファイルがあります: {dst_run_dir}/{lv}")
    plan = plan_reusable_run_assets(src_run_dir)
    if not dry_run:
        for item in plan["allow"]:
            dst = os.path.join(dst_run_dir, item["path"])
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(os.path.join(src_run_dir, item["path"]), dst)
    return {"dry_run": dry_run, "copied" if not dry_run else "would_copy": len(plan["allow"]), "denied": len(plan["deny"]),
            "plan": plan}


# ============================================================
# 4. M4: Z専用 generate_or_reuse_z(Xの_generate_or_reuseは呼ばない/不変)
# ============================================================
def style_text_for(spec: ClipSpec):
    """そのclipで実際に渡すstyle_prefix_override(None=従来Dialogue style/既存挙動)。"""
    if spec.kind == "dialogue":
        # Std/Adv共通: 既定Dialogue Style(2026-10-19ユーザー決定③。Stdも生成時の減速指示なし。2026-10-23速度仕様v2でStd会話の後処理6%減速は撤去、Adv会話のみ約6%高速化)
        return None
    return FAMILY_Z_ROLE_STYLE[spec.role_key]["text"]


def build_reuse_key(spec: ClipSpec) -> dict:
    key = {
        "canonical_text_sha256": _sha256_text(spec.text),
        "role_style_version": FAMILY_Z_ROLE_STYLE_VERSION,
        "voice": spec.voice,
        "style_prefix_sha256": style_prefix_sha256(style_text_for(spec)),
        "tts_backend": TTS_BACKEND,
    }
    if spec.kind == "dialogue":
        # 速度仕様v2(会話のみ速度処理が変わった)。旧仕様(Std=6%減速済み/Adv=未処理)の保存音声はこのkeyを持たず、不一致=新仕様として再利用されない。
        # 会話以外(Narrator・Preview・KP等)は速度処理が不変のため、keyを変えず既存の再利用を維持する。
        key["speed_profile"] = f"{Z_SPEED_PROFILE_VERSION}:{speed_profile_name(spec.level, spec.kind)}"
        _dc = (spec.extra or {}).get("dialogue_ctx")
        if _dc and _dc.get("policy") == "fz_ctx_v1":
            # FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01(Opus M-5): 文脈・感情付きpolicyのrunでだけ方式識別を載せる(policy=legacy/未解決のdialogueはkeyバイト不変)。
            # 文脈入力(前後セリフ・地の文の決定論抽出)のshaを含めるため、前後の台本が変われば当該clipだけ再生成される。LLM出力(notes)はrun内不変なのでkeyに入れない。
            key["dialogue_tts"] = {"policy": _dc["policy"], "context_input_sha256": _dc["context_input_sha"]}
    ch = (spec.extra or {}).get("chunk")
    if ch:
        # chunk specにのみ追加(planner版・親・index・chunk数・ポーズ)。非chunk specのkeyはバイト不変=従来の再利用を壊さない。
        key.update(chunk_tts.chunk_reuse_key_fields(ch["parent_id"], {"index": ch["index"]}, ch["count"]))
    return key


def build_legacy_reuse_key(spec: ClipSpec) -> dict:
    """速度仕様v2導入前のreuse_key(speed_profileなし)。旧entryが『音声は有効だが速度仕様が旧い』ことの判定にだけ使う(移行専用)。"""
    key = build_reuse_key(spec)
    key.pop("speed_profile", None)
    return key


def generate_or_reuse_z(cached_entry: dict | None, spec: ClipSpec, wav_path: str, generate_fn) -> dict:
    """判定キー {canonical_text, FAMILY_Z_ROLE_STYLE_VERSION, voice, style prefix sha256, tts_backend}
    の全一致のみ再利用。キーはentryの reuse_key に保存。1つでも異なれば再生成。
    再利用時はwav実在・status OK・sha256一致(stale検知)も要求。"""
    generate_fn = secondary_run_scope.guard_generate(generate_fn, str(spec.clip_id))  # 委任_06c: circuit open中は技術STOP
    if spec.kind == "kp_en":
        generate_fn = kp_vote.guard_whisper(generate_fn, str(spec.clip_id))   # KP3V(P-08): Whisper事前確認/circuit open中はTTSを回さず技術STOP
    key = build_reuse_key(spec)
    if cached_entry and cached_entry.get("status") == "OK" and cached_entry.get("reuse_key") == key and os.path.exists(wav_path):
        recorded = cached_entry.get("sha256")
        if recorded is None or _sha_file(wav_path) == recorded:
            # AUW 委任_06c(OF-AUW-C-03、ADDENDUM §3-1): 再利用前に保存転写のみ(API 0)を現行の統一judgeへ通し、値ガードDIFF/否定差
            # (`reuse_blocked` mark含む)なら再利用せず再生成する。転写が無い/判定不能なentryは従来どおり再利用。
            import er078_reuse_value_guard_01 as _rvg
            _g = _rvg.guard_entry(cached_entry, label=str(spec.clip_id), canonical_text=None,
                                  kp_vote_gate_follows=bool(spec.kind == "kp_en" and kp_vote.vote_enabled()))   # OF-KPQ-P-01: 直後にkp_vote_reuse_okが続く
            if _g.get("blocked"):
                _r = generate_fn()
                if isinstance(_r, dict):
                    _r["reuse_value_guard_blocked_previous"] = {k: _g.get(k) for k in ("reason", "reason_code", "unified_state")}
                return _r
            _kd = None
            if spec.kind == "kp_en" and kp_vote.vote_enabled():
                # KP3V(OF-KPD-P-03、再利用点6): KP英語phraseの前回results再利用は両Provider PASSの証跡を要する(fail-closed)。
                # 証跡が無ければS1(Azure 1回)、NGなら再生成、Azure障害は技術STOP(再利用も再生成もしない)。
                _kd = kp_vote.kp_vote_reuse_ok(cached_entry, wav_path=wav_path, canonical_text=_norm_for_tts(spec), allow_s1=True,
                                               label=str(spec.clip_id))
                if _kd["action"] == kp_vote.ACTION_TECHNICAL_STOP:
                    return kp_vote.technical_stop_entry(str(spec.clip_id), _kd)
                if not _kd["ok"]:
                    _r = generate_fn()
                    if isinstance(_r, dict):
                        _r["kp_dual_reuse_gate_previous"] = {"reason": _kd["reason"], "action": _kd["action"]}
                    return _r
            reused = dict(cached_entry)
            reused["reused_from_previous_run"] = True
            if _kd is not None and _kd.get("kp_dual_check") is not None:
                reused["kp_dual_check"] = _kd["kp_dual_check"]
            if "asr_judgement" in reused:   # AUW 委任_03: 再利用音声の元のWARNINGを継承(asr_judgement_inherited)
                reused["asr_judgement_inherited"] = reused.pop("asr_judgement")
            return reused
    return generate_fn()


# ============================================================
# 4-D. Z dialogue 文脈・感情付きTTS(FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01、OPEN-528、APPROVED_FOR_PRODUCTION 2026-10-26)
#      ユーザー仕様: 1回目=文脈・感情付き、NG->即時2回目=文脈・感情付き、NG->180秒->3回目=従来方式(文脈・感情情報を完全除外)、総試行3回(待機は2026-10-26に旧600秒から180秒へ変更、er127.cooldown_core)。
#      設計=docs/research/FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01/DESIGN_02.md。X/Y/B/C/narrator/KPは一切変更しない(Zのdialogueだけ)。
# ============================================================
def prepare_dialogue_ctx(run_dir: str, level: str, plan: list, *, story_key: str = DEFAULT_SLUG, only_clips: set | None = None) -> dict:
    """LLMを呼ばない前処理(Opus M-5)。(1)run単位のdialogue TTS policyを解決・保存 (2)policy=fz_ctx_v1のrunでdialogue specへ extra["dialogue_ctx"]
    (policy・文脈入力sha・明示再生成信号)を付ける。感情notes(LLM)は最初のdialogue生成時にlevel単位で1回だけ作る(保存済みなら0)。
    policy=legacy(既存run・ロールバック)ではspecに何も付けず現行と同一動作。"""
    import er122_fz_ctx_policy_01 as pol
    import er122_fz_ctx_notes_01 as notes
    rec = pol.resolve_run_policy(run_dir, write=True)
    dlg = [s for s in plan if s.kind == "dialogue"]
    if rec["policy"] != pol.POLICY_CTX or not dlg:
        return rec
    level_dir = f"{run_dir}/{level}"
    clips = notes.story_clips_from_plan(plan)
    provider = notes.get_provider(level_dir, notes.resolve_story_key(story_key), clips)
    for s in dlg:
        s.extra["dialogue_ctx"] = {"policy": pol.POLICY_CTX, "context_input_sha": provider.context_input_sha(s.clip_id),
                                   "explicit_regenerate": bool(only_clips and s.clip_id in only_clips), "level_dir": level_dir,
                                   "run_dir": run_dir, "story_key": story_key}
    return rec


def generate_dialogue_ctx(spec: ClipSpec, out_path: str, text: str, dctx: dict) -> dict:
    """dialogue 1 clipの文脈・感情付きTTS。共有ループ(er012_b.generate_voice_body_wide_margin)は単一コピーのまま、attempt_hook(policy)で
    『attempt番号->Style』と『試行前後の記録』だけを差し込む。Std=単一呼出、Adv=外側ループ(減速後ASR再検証つき、通算TTS3回を共有)。"""
    import er003_v1_n3_01_tts_generate as n3_tts
    import er011_human_review_lock_01 as review_lock
    import er012_b_family_voices_production_01 as bvoices
    import er122_fz_ctx_notes_01 as notes
    import er122_fz_ctx_policy_01 as pol

    run_dir, level_dir = dctx["run_dir"], dctx["level_dir"]
    adv = spec.level == "b1b"
    chk = review_lock.check_before_generation(out_path, text, "en")
    if not chk.get("proceed"):
        # Human Review Lock済み(0 API): 既存のblock結果をそのまま返す。notes(LLM)もstateも触らない
        return bvoices.generate_voice_body_wide_margin(text, out_path, spec.voice)
    provider = notes.provider_for_level(level_dir)
    sty = provider.style_for(spec.clip_id)       # level単位1 call(保存済みなら0)。失敗=技術STOP(全clip中立では続行しない)。TTS前
    policy = pol.DialogueAttemptPolicy(
        level_dir, spec.clip_id, text, sty["style"], sty["style_sha256"], out_path=out_path,
        stop_check=lambda where: _check_stop_sentinel(run_dir, where),
        explicit_regenerate=bool(dctx.get("explicit_regenerate")), consuming_regenerate_approval=bool(chk.get("consuming_regenerate_approval")))
    saved = policy.saved_result()
    if saved is not None:       # 確定直後〜checkpoint前に落ちた合格済みclip: 保存結果を採用(API 0。作り直さない)
        return saved
    budget_left = min(policy.remaining(), pol.MAX_TOTAL_ATTEMPTS - policy.prior_generations())
    if not adv:
        r = bvoices.generate_voice_body_wide_margin(text, out_path, spec.voice, max_attempts=policy.remaining(), attempt_hook=policy)
        policy.mark_counted()
    elif budget_left <= 0:
        # 3回消費済み(または行会計で予算なし): 4回目を回さず、STOPPED+Review Lock(HR)で終える(0 API)
        r = bvoices.generate_voice_body_wide_margin(text, out_path, spec.voice, max_attempts=0, attempt_hook=policy)
        policy.mark_counted()
    else:
        passes = {"n": 0}

        def gen(max_attempts):
            if passes["n"] > 0:
                policy.note_final_ng()      # 直前passが減速後検証でNG確定した時刻(cooldownの起点)
            passes["n"] += 1
            # Opus M-2: ループ内の番号と通算nの最終slotを一致させる(外側の行会計の残りと、policyの通算残りの小さい方)
            ma = min(max_attempts, policy.remaining())
            r_ = bvoices.generate_voice_body_wide_margin(text, out_path, spec.voice, max_attempts=ma, attempt_hook=policy)
            policy.mark_counted()
            return r_
        r = n3_tts.generate_with_a2_slowdown_outer_loop(spec.clip_id, text, out_path, gen, slowdown_pct=Z_ADV_DIALOGUE_SLOWDOWN_PCT,
                                                        prior_generations=policy.prior_generations())
    if not isinstance(r, dict):
        return r
    extra = {"ctx_style_sha256": sty["style_sha256"], "context_input_sha256": sty["context_input_sha256"], "note_status": sty["note_status"],
             "speaker_display_source": sty["speaker_display_source"], "emotion_prompt_sha256": sty["emotion_prompt_sha256"],
             # Opus M-3(ii): 行会計で外側予算が先に尽きた/早期終了で従来方式(3回目)に到達せず終わった場合の記録(安全側=STOPPED->HR Lock)
             "terminal_before_fallback": bool(r.get("status") != "OK" and policy.n_started < pol.MAX_TOTAL_ATTEMPTS)}
    try:    # leakage検査は観測のみ(NG理由にしない。ASRの表記違いだけで再生成しない)
        texts = [a.get("asr_text") for a in (r.get("attempts_log") or []) if isinstance(a, dict) and a.get("tts_mode") == "ctx"]
        if policy.st["attempts"] and policy.st["attempts"][-1].get("mode") == "ctx":
            extra["leakage"] = notes.leakage_all_attempts(texts, r.get("asr_text"), sty["ctx"], sty["note"])
    except Exception as e:      # 観測の失敗で生成結果を失わない
        extra["leakage"] = {"observation_only": True, "error": str(e)}
    r["dialogue_tts"] = policy.evidence(extra)
    return policy.finish(r)


# ============================================================
# 5. 実TTS generator(遅延import、testではgeneratorsを差し替える)
# ============================================================
def _pnap_supply(original: str, shaped: str) -> str:
    """PNAP 委任_02(5-4): 固有名詞の発音供給(綴り置換)をtext整形点の直後に1回挟む。flag OFF・run scope外・KPでは恒等(shapedをそのまま返す)。
    共有`er003_v1_n3_01_tts_generate`は編集しない(27-7)。"""
    import er103_pronunciation_tts_supply_01 as _sup
    import er003_v1_n3_01_tts_generate as _n3
    return _sup.supply_for_tts(original, shaped, static_overrides=getattr(_n3, "_EN_NAME_PRONUNCIATION_OVERRIDES", None))


def _norm_for_tts(spec: ClipSpec) -> str:
    import er003_v1_n3_01_tts_generate as n3_tts
    if spec.kind in ("narrator", "dialogue"):
        return _pnap_supply(spec.text, n3_tts.tts_safe_news_en(spec.text))
    if spec.kind in ("topic_intro", "preview", "comment") and spec.language == "en":
        return _pnap_supply(spec.text, n3_tts.tts_safe_number_words_en(n3_tts.tts_safe_en(spec.text)))
    if spec.kind == "kp_en":
        return n3_tts.tts_safe_kp_en(spec.text)
    return spec.text


def real_generators() -> dict:
    """kind -> fn(spec, out_path) -> result dict(共有関数の結果dictをそのまま返す)。"""
    _check_stop_sentinel(None, "client:er063_real_generators")      # 委任_12A: TTS client経路の生成前にSTOP確認
    import er003_v1_n3_01_tts_generate as n3_tts
    import er003_v1_sing01_news_tail_fix as news_tail_fix
    import er003_v1_sing01_voice01_generate as voice01
    import er003_v1_crosslevel_audio_02_common as crosslevel
    import er003_v1_repro01_main_generate as repro01
    import er012_b_family_voices_production_01 as bvoices
    import er020_tts_retry_local_rewrite_01 as retry_primitive
    import er011_human_review_lock_01 as review_lock

    def cs(spec):
        return retry_primitive.connected_speech_enabled_for(spec.clip_id)

    def narrator(spec, out_path):
        text = _norm_for_tts(spec)
        style = style_text_for(spec)
        if spec.level == "b1b":
            return news_tail_fix.generate_news_narration_wide_margin(
                text, out_path, disfluency_qa=False, enable_connected_speech_equivalence_layer=cs(spec),
                enable_repetition_qa=True, enable_pronunciation_resolver=True,
                style_prefix_override=style, tts_backend=TTS_BACKEND)
        return n3_tts.generate_a2_segment_with_slowdown(
            text, out_path, n3_tts.first_words(spec.text), style_prefix_override=style, disfluency_qa=False,
            enable_connected_speech_equivalence_layer=cs(spec), enable_repetition_qa=True, tts_backend=TTS_BACKEND)

    def dialogue(spec, out_path):
        text = _norm_for_tts(spec)
        _dctx = (spec.extra or {}).get("dialogue_ctx")
        if _dctx and _dctx.get("policy") == "fz_ctx_v1":
            # FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01(APPROVED_FOR_PRODUCTION 2026-10-26): 新規runのdialogueは文脈・感情付きTTSが標準(ctx->ctx->180秒->従来方式、総3回。旧600秒は2026-10-26に180秒へ変更)
            return generate_dialogue_ctx(spec, out_path, text, _dctx)
        if spec.level == "b1b":
            # FAMILY-Z-DIALOGUE-SPEED-PRODUCTION-WIRING-01(速度仕様v2): Adv会話は生成後に約6%高速化(atempo=1.06、ピッチ保持。Trial Bと同一関数・係数)。
            # 高速化後の音声を統一judgeで再検証し、NGなら通算TTS3回の残予算で取り直す(旧Std減速と同じ外側ループ=既存のretry上限・ASR検査を維持)。
            # 生成時Styleは従来のまま(Narrator Styleは渡さない)。Voice・話者帰属は不変。
            return n3_tts.generate_with_a2_slowdown_outer_loop(
                spec.clip_id, text, out_path,
                lambda max_attempts: bvoices.generate_voice_body_wide_margin(
                    text, out_path, spec.voice, max_attempts=max_attempts),
                slowdown_pct=Z_ADV_DIALOGUE_SLOWDOWN_PCT)
        # Std会話: 速度後処理なし(旧6%減速を撤去、速度仕様v2)。生成はAdvと同一の既定Dialogue Style(style_prefix_overrideを渡さない)。
        return bvoices.generate_voice_body_wide_margin(text, out_path, spec.voice)

    def charon_en(spec, out_path):
        return voice01.generate_charon_english(
            _norm_for_tts(spec), out_path, style_prefix_override=style_text_for(spec),
            disfluency_qa=(spec.kind in ("preview", "comment")),
            enable_connected_speech_equivalence_layer=cs(spec), enable_pronunciation_resolver=True,
            tts_backend=TTS_BACKEND)

    def topic_intro(spec, out_path):
        if spec.level == "b1b":
            return charon_en(spec, out_path)
        return crosslevel.generate_english_segment_with_fallback(
            _norm_for_tts(spec), out_path, n3_tts.first_words(spec.text.replace("Today's topic is ", ""), 3),
            max_extra_chars=30, style_prefix_override=style_text_for(spec),
            enable_connected_speech_equivalence_layer=cs(spec), tts_backend=TTS_BACKEND)

    def ja_simple(spec, out_path, **kw):
        return n3_tts.generate_a2_japanese_with_reading_safety(
            spec.text, out_path, n3_tts.expected_substring_ja(spec.text), style_prefix_override=style_text_for(spec),
            tts_backend=TTS_BACKEND, **kw)

    def preview(spec, out_path):
        return charon_en(spec, out_path) if spec.level == "b1b" else ja_simple(spec, out_path)

    def kp_en(spec, out_path):
        # AUW 委任_06e(F1): legacy/X入口(`generate_key_phrase_component_verified`、@guarded_generate("en"))と同じく、
        # 2段呼出(MINIMAL×2 → ENGLISH_LOCK×2、2026-09-01ユーザー決定の4回構成)を**外側guard1つ**で包む。
        # 外側guardが無いと1段目の最終STOPPEDを内側guardがLockへ記録し、2段目がHUMAN_REVIEW_LOCKEDで0 APIになり
        # 4回構成が2回で止まった(06d `kp4`)。内側は同一out_pathのreentrancy guardでcheck/recordを行わず、record_outcomeは
        # 最終結果で1回だけ発火する(Lockロジックは無変更)。
        return _kp_en_two_stage(_norm_for_tts(spec), out_path, spec)

    @review_lock.guarded_generate("en")
    @er127.with_block("L6", fingerprint_params=())      # 委任_02(X/Y/Z scope内のみ有効。scope外=_blk None=従来どおり)
    def _kp_en_two_stage(text, out_path, spec, *, _blk=None):
        primary = repro01.generate_narration_snippet_verified_strict(
            text, "en", out_path, text, max_extra_chars=10, max_attempts=repro01.KEY_PHRASE_MINIMAL_MAX_ATTEMPTS,
            safety_margin_seconds=repro01.KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS, disfluency_qa=True,
            style_prefix_override=style_text_for(spec), asr_prompt=repro01.KEY_PHRASE_EN_ASR_NO_TRANSLATE_PROMPT,
            enable_non_latin_cascade=True, tts_backend=TTS_BACKEND,
            slot_offset=0, total_slots=repro01.KEY_PHRASE_TOTAL_MAX_ATTEMPTS,  # AUW 委任_05: 4回構成の前半(HR queue対象外)
            vote_pass_required=kp_vote.vote_enabled(),  # KP3V: KP英語phrase=Primary・Secondary両方PASS必須
            **er127.stage_kwargs(_blk, 0))
        if primary.get("status") == "OK":
            primary["fallback_used"] = False
            return kp_vote.attach_kp_vote_check(primary, out_path, text)
        if kp_vote.vote_enabled() and repro01._vote_circuit_open():
            # KP3V(OF-KPD-P-02の最小緩和): Azure circuit breaker open中はENGLISH_LOCK段のTTSを回さない(技術STOP)
            primary["fallback_used"] = False
            primary["english_lock_skipped_secondary_circuit_open"] = True
            return primary
        fb = repro01.generate_narration_snippet_verified_strict(
            text, "en", out_path, text, max_extra_chars=10, max_attempts=repro01.KEY_PHRASE_ENGLISH_LOCK_MAX_ATTEMPTS,
            safety_margin_seconds=repro01.KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS, disfluency_qa=True,
            style_prefix_override=repro01.KEY_PHRASE_ENGLISH_LOCK_INSTRUCTION,
            asr_prompt=repro01.KEY_PHRASE_EN_ASR_NO_TRANSLATE_PROMPT, enable_non_latin_cascade=True,
            tts_backend=TTS_BACKEND,
            slot_offset=repro01.KEY_PHRASE_MINIMAL_MAX_ATTEMPTS,
            total_slots=repro01.KEY_PHRASE_TOTAL_MAX_ATTEMPTS,  # AUW 委任_05: 4回構成の後半(最終slot)
            vote_pass_required=kp_vote.vote_enabled(),  # KP3V
            **er127.stage_kwargs(_blk, repro01.KEY_PHRASE_MINIMAL_MAX_ATTEMPTS))     # ③(ENGLISH_LOCK段の最初)直前に180秒
        if _blk is not None and _blk.depth == 0 and fb.get("status") != "OK":
            er127.register_terminal_hr(out_path=out_path, canonical_text=text, attempt=er127.last_attempt_of(fb), lock_text=text)   # Opus M-4
        kp_vote.attach_kp_vote_check(fb, out_path, text)
        fb["fallback_used"] = True
        # legacy `generate_key_phrase_component_verified`と同じ会計: record_outcomeの実TTS試行数(=4)のため、1段目の
        # attempts_logをfallback_attempts_logへ載せる(監査用の別名も同じ)。
        fb["fallback_attempts_log"] = primary.get("attempts_log")
        fb["minimal_attempts_log"] = primary.get("attempts_log")
        fb["english_lock_attempts_log"] = fb.get("attempts_log")
        return fb

    def kp_expl_en(spec, out_path):
        import er019_family_x_audio_production_runner_01 as x_runner  # 既存承認のKP英語解説TTS(関数は不変・読み取り利用)
        return x_runner.generate_key_phrase_explanation_en_verified(
            spec.text, out_path, style_prefix_override=style_text_for(spec), tts_backend=TTS_BACKEND)

    def kp_ja(spec, out_path):
        return n3_tts.generate_a2_japanese_with_reading_safety(
            spec.text, out_path, n3_tts.expected_substring_ja(spec.text), max_extra_chars=30,
            known_key_phrase_terms=[spec.extra.get("used_form", "")], style_prefix_override=style_text_for(spec),
            tts_backend=TTS_BACKEND)

    return {"narrator": narrator, "dialogue": dialogue, "topic_intro": topic_intro, "preview": preview,
            "comment": preview, "japanese_title": lambda s, p: ja_simple(s, p), "kp_en": kp_en, "kp_ja": kp_ja, "kp_expl_en": kp_expl_en}


# ============================================================
# 6. entry構築(データ契約4-4、既存Gate形式 segments/key_phrases の拡張) + evidence
# ============================================================
def _style_record_sha(rec):
    if rec is None:
        return None
    if isinstance(rec, dict):
        return rec.get("sha256")
    if isinstance(rec, str):
        return None if rec.startswith("<default") else _sha256_text(rec)
    return None


def _read_attempt_meta(attempt_audio_path) -> dict:
    """review_lock.save_tts_attempt_audio が wav と並べて保存する attempt metadata json(実測 model/voice)。"""
    if not attempt_audio_path:
        return {}
    p = os.path.splitext(attempt_audio_path)[0] + ".json"
    try:
        return _read_json(p) if os.path.exists(p) else {}
    except Exception:
        return {}


def extract_attempt_evidence(result: dict) -> list:
    """標準/fallbackのattempt logsから、clipごとのinstruction_label/style_prefix(sha)/model/voiceを抽出する。"""
    out = []
    std_key = "standard_attempts_log" if result.get("standard_attempts_log") else "attempts_log"
    for phase, key in (("standard", std_key), ("fallback", "fallback_attempts_log")):
        logs = result.get(key)
        if not isinstance(logs, list):
            continue
        for a in logs:
            if not isinstance(a, dict):
                continue
            sp = a.get("style_prefix")
            meta = _read_attempt_meta(a.get("attempt_audio_path"))
            row = {
                "phase": phase, "attempt": a.get("attempt"),
                "instruction_type": a.get("instruction_type"),
                "instruction_label": a.get("instruction_label") or a.get("instruction_type"),
                "style_prefix_sha256": _style_record_sha(sp),
                "style_prefix_head": (sp.get("head200") if isinstance(sp, dict) else (sp if isinstance(sp, str) else None)),
                "tts_model_id": a.get("tts_model_id") or meta.get("model"), "voice": a.get("voice") or meta.get("voice"),
                "audio_classification": a.get("audio_classification"), "verified": a.get("verified"),
                "asr_text": a.get("asr_text"),
            }
            if a.get("tts_mode"):    # additive(dialogue文脈・感情付きTTSのrowだけ。旧rowの形は不変)
                row.update({k: a.get(k) for k in ("tts_mode", "overall_attempt_n", "tts_mode_effective") if a.get(k) is not None})
            out.append(row)
    return out


def _sha_file(path: str):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _wav_duration(path: str):
    import soundfile as sf
    return float(sf.info(path).duration)


def build_speed_profile_record(spec: ClipSpec, result: dict, out_path: str):
    """速度仕様v2のclip単位記録(story clip=narrator/dialogueのみ。他kindはNone)。applied=実際に速度後処理が掛かったか、
    tempo=atempo係数(減速6%=0.943396、Adv会話高速化=1.06、処理なし=None)、original_sha256=処理前原音(_original.wav)のsha。"""
    name = speed_profile_name(spec.level, spec.kind)
    if name is None:
        return None
    applied = bool(result.get("slowdown_applied"))
    sd = result.get("slowdown_info") or {}
    tempo = None
    if applied and sd.get("slowdown_pct_target") is not None:
        tempo = round(1.0 / (1.0 + sd["slowdown_pct_target"] / 100.0), 6)
    orig = result.get("original_path")
    return {"version": Z_SPEED_PROFILE_VERSION, "profile": name, "applied": applied, "tempo": tempo,
            "slowdown_pct_target": sd.get("slowdown_pct_target") if applied else None,
            "original_sha256": _sha_file(orig) if (applied and orig) else None, "source": "generated"}


def build_entry(spec: ClipSpec, out_path: str, result: dict, *, human_approved: bool = False) -> dict:
    import er020_tts_retry_local_rewrite_01 as retry_primitive
    seg_id = derive_segment_id(out_path)
    status = result.get("status")
    attempts = extract_attempt_evidence(result)
    fallback_attempts = [a for a in attempts if a["phase"] == "fallback"]
    stop_events = result.get("cooldown_events") or []
    lr = result.get("local_rewrite_recovery")
    deviation = None
    if result.get("canonical_text_before_local_rewrite") is not None or lr:
        after = None
        try:
            after = lr["selection"]["selected"]["rewritten_segment"]
        except Exception:
            after = result.get("text")
        before = result.get("canonical_text_before_local_rewrite") or spec.text
        deviation = {"clip_id": spec.clip_id, "canonical_text_before_local_rewrite": before,
                     "audio_text_after": after, "diff_summary": _diff_summary(before, after)}
    model_ids = sorted({a["tts_model_id"] for a in attempts if a.get("tts_model_id")} |
                       ({result["tts_model_id"]} if result.get("tts_model_id") else set()) |
                       ({result["model"]} if result.get("model") else set()))
    style_sha = style_prefix_sha256(style_text_for(spec))
    z_adoption = "failed"
    if status == "OK":
        z_adoption = "adopted"
    elif human_approved:
        z_adoption = "human_review_adopted"
    sd = result.get("slowdown_info") or {}
    ratio = None
    if sd.get("dst_duration_seconds") and sd.get("src_duration_seconds"):
        ratio = round(sd["dst_duration_seconds"] / sd["src_duration_seconds"], 4)
    speed_profile = build_speed_profile_record(spec, result, out_path)
    entry = {
        # --- 既存Gate互換 ---
        "status": status, "path": out_path, "sha256": _sha_file(out_path),
        "canonical_text": spec.text, "text": spec.text,
        "disfluency_checked": bool(result.get("disfluency_checked", False)),
        "asr_text": result.get("asr_text"),
        "slowdown_applied": result.get("slowdown_applied"),
        # --- Z拡張(4-4) ---
        "z_adoption": z_adoption, "segment_id": seg_id, "narration_path": out_path,
        "role": retry_primitive.resolve_narrative_role(seg_id),
        "connected_speech_enabled": retry_primitive.connected_speech_enabled_for(seg_id),
        "tts_backend": TTS_BACKEND, "voice": spec.voice, "speaker": spec.speaker, "clip_kind": spec.kind,
        "role_style_key": spec.role_key, "model_ids_measured": model_ids,
        "style": {"instruction_label": FAMILY_Z_ROLE_STYLE[spec.role_key]["style_label"] if spec.kind != "dialogue"
                  else FAMILY_Z_ROLE_STYLE[spec.role_key]["style_label"],
                  "style_prefix_sha256": style_sha, "effective_style_prefix_sha256": _effective_style_sha_for_result(spec, style_sha, result),
                  "fallback_used": bool(result.get("fallback_used") or fallback_attempts),
                  "fallback_attempts": [{"instruction_label": a["instruction_label"],
                                         "style_prefix_sha256": a["style_prefix_sha256"],
                                         "style_prefix_head": a["style_prefix_head"]} for a in fallback_attempts]},
        "reuse_key": build_reuse_key(spec),
        "slowdown_ratio": ratio, "speed_profile": speed_profile, "attempts": attempts,
        "cooldown_occurred": bool(stop_events), "cooldown_events": stop_events,
        "audio_text_deviation": deviation,
        "tts_generations_used": result.get("tts_generations_used"),
        # AUW 委任_03(additive): 統一ASR判定の監査record(PASS_WITH_WARNING等)。事後試聴リストの入力。
        "asr_judgement": result.get("asr_judgement"),
    }
    if (spec.extra or {}).get("chunk") and spec.level == chunk_tts.STD_LEVEL and isinstance(result.get("slowdown_info"), dict):
        # CHUNK-TTS-STD 委任_03(Opus M2/R2): Std chunk entryには減速前後長を記録する(速度Gateがchunk単位の比率を厳格検査する根拠)。
        # chunk以外のentry・Adv entryには付けない(従来とバイト同一)。
        _sd = result["slowdown_info"]
        entry["slowdown_info"] = {k: _sd.get(k) for k in ("slowdown_pct_target", "slowdown_pct_actual", "src_duration_seconds", "dst_duration_seconds")}
    # FAMILY-Z-STYLE-ACTUAL-GATE-01(OPEN-551、additive): leafが実際に送ったStyle prefixの実測記録(採用attempt優先、無ければtop-level style_prefix)。
    # run_audio_gate の z_style_actual_gate がこれを承認値と照合する。意図値(style.style_prefix_sha256)とは別物。
    entry["style_actual"] = build_style_actual_record(spec, result)
    if result.get("kp_dual_check") is not None:   # KP3V(additive): KP英語phraseのみ。両Provider PASSの証跡
        entry["kp_dual_check"] = result["kp_dual_check"]
    if isinstance(result.get("dialogue_tts"), dict):   # FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01(additive): dialogue文脈・感情付きTTSのpolicy・試行・最終方式の証跡
        entry["dialogue_tts"] = result["dialogue_tts"]
    if os.path.exists(out_path):
        try:
            entry["duration_seconds"] = round(_wav_duration(out_path), 3)
        except Exception:
            entry["duration_seconds"] = None
    return entry


def _effective_style_sha(spec: ClipSpec, style_sha):
    """override無し(Adv Dialogue)の場合、実際に送られる既定Style(p9a.ENGLISH_STYLE_PREFIX)のshaを記録する。"""
    if style_sha is not None or spec.kind != "dialogue":
        return style_sha
    try:
        import er003_b1_p9a_audio as p9a
        return style_prefix_sha256(p9a.ENGLISH_STYLE_PREFIX)
    except Exception:
        return None


def _effective_style_sha_for_result(spec: ClipSpec, style_sha, result: dict):
    """採用された試行の実効Style sha(Opus M-8)。文脈・感情付きで採用したclipは ctx style のsha、従来方式fallback/minimal fallbackは既定Dialogue Styleのsha。"""
    dt = result.get("dialogue_tts") if isinstance(result, dict) else None
    if isinstance(dt, dict) and dt.get("final_mode") == "ctx" and dt.get("ctx_style_sha256"):
        return dt["ctx_style_sha256"]
    return _effective_style_sha(spec, style_sha)


def _diff_summary(before: str, after: str) -> str:
    import difflib
    a, b = (before or "").split(), (after or "").split()
    sm = difflib.SequenceMatcher(None, a, b)
    parts = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != "equal":
            parts.append(f"{tag}: {' '.join(a[i1:i2])!r} -> {' '.join(b[j1:j2])!r}")
    return "; ".join(parts) or "(no word-level diff)"


# ============================================================
# 7. TTS stage
# ============================================================
def load_results(level_dir: str) -> dict | None:
    p = f"{level_dir}/audit/tts_generation_results.json"
    if not os.path.exists(p):
        return None
    try:
        return _read_json(p)
    except Exception:
        return None


def _check_stop_sentinel(run_dir: str, where: str) -> None:
    import er062_family_z_structure_01 as _zst
    _zst.check_stop_sentinel(where, run_dir)


def _checkpoint_path(level_dir: str) -> str:
    return f"{level_dir}/audit/tts_checkpoint.json"


def load_checkpoint(level_dir: str) -> dict | None:
    """clip単位の途中経過(委任_10: 実行processが外部要因で中断しても完了済みclipを再課金しない)。"""
    p = _checkpoint_path(level_dir)
    if not os.path.exists(p):
        return None
    try:
        return _read_json(p)
    except Exception:
        return None


def save_checkpoint(level_dir: str, segments: dict, key_phrases: dict) -> None:
    p = _checkpoint_path(level_dir)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"segments": segments, "key_phrases": key_phrases}, f, ensure_ascii=False)
    os.replace(tmp, p)


def prune_cached_to_plan(cached: dict | None, plan: list) -> dict | None:
    """KPFT 委任_02(OF-KPFT-P-09): 前回results/checkpointのうち、現在のplanのclipで、かつreuse_key(本文・style・voice・backend)が
    一致するentryだけを残す。同じrun dirでKPを再生成した(5件->3件、または語句が変わった)後に、旧rank/旧語句の音声entryが
    混入して再利用されることを防ぐ(rank集合ではなくreuse_keyの不一致で刈り込む)。"""
    if not cached:
        return cached
    out = {"segments": {}, "key_phrases": {}}
    for spec in plan:
        prev = _cached_entry(cached, spec)
        if prev is not None and prev.get("reuse_key") in (None, build_reuse_key(spec)):
            _store(out["segments"], out["key_phrases"], spec, prev)
    for k, v in cached.items():
        if k not in ("segments", "key_phrases"):
            out[k] = v
    return out


def _speed_migration_record(spec: ClipSpec, prev: dict, **extra) -> dict:
    return {"from": "legacy(speed_profileなし=速度仕様v1)", "to": f"{Z_SPEED_PROFILE_VERSION}:{speed_profile_name(spec.level, spec.kind)}",
            "tts_calls": 0, "legacy_sha256": prev.get("sha256"), "legacy_duration_seconds": prev.get("duration_seconds"), **extra}


def _migrate_one_std_dialogue(spec: ClipSpec, prev: dict, narr: str, level_dir: str):
    """Std会話: 旧6%減速済みwavを、退避済みの減速前原音(`<id>_original.wav`)へ戻す。TTS・ASR呼出0(原音は生成時にASR検証済み)。
    旧wavは audit/legacy_speed_backup/ へ退避してから戻す。idempotent(既にwav==originalでもentryだけ更新)。条件を満たさなければNone。"""
    cur, orig = f"{narr}/{spec.clip_id}.wav", f"{narr}/{spec.clip_id}_original.wav"
    if not (os.path.exists(cur) and os.path.exists(orig)):
        return None
    already = _sha_file(cur) == _sha_file(orig)
    if not already:
        try:
            ratio = _wav_duration(cur) / _wav_duration(orig)
        except Exception:
            return None
        if prev.get("slowdown_applied") is not True or not (SLOWDOWN_RATIO_MIN <= ratio <= SLOWDOWN_RATIO_MAX):
            return None    # 旧6%減速済みと確認できない音声は移行しない(再生成経路へ)
        bdir = f"{level_dir}/audit/legacy_speed_backup"
        os.makedirs(bdir, exist_ok=True)
        shutil.copyfile(cur, f"{bdir}/{spec.clip_id}_slowed6pct_legacy.wav")
        shutil.copyfile(orig, cur)
    new = dict(prev)
    new.update({"sha256": _sha_file(cur), "duration_seconds": round(_wav_duration(cur), 3), "slowdown_applied": False,
                "slowdown_ratio": None, "reuse_key": build_reuse_key(spec),
                "speed_profile": {"version": Z_SPEED_PROFILE_VERSION, "profile": speed_profile_name(spec.level, spec.kind), "applied": False,
                                  "tempo": None, "slowdown_pct_target": None, "original_sha256": _sha_file(orig),
                                  "source": "migrated_from_original"},
                "speed_migration": _speed_migration_record(spec, prev, asr_recheck="not_required(原音は生成時ASR検証済み・sha不変)")})
    if "asr_judgement" in new:
        new["asr_judgement_legacy_post_slowdown"] = new.pop("asr_judgement")   # 旧(減速後wav)の判定recordは別名へ退避(現行wavの判定ではない)
    return new


def _migrate_one_adv_dialogue(spec: ClipSpec, prev: dict, narr: str, level_dir: str):
    """Adv会話: 未処理の旧wavへ約6%高速化を正式後処理(`apply_a2_slowdown_postprocess(slowdown_pct=-5.66)`+統一judge ASR再検証)で適用する。
    TTS呼出0・ASR 1回/clip。`_original.wav`が残っていれば(高速化だけが先に掛かった中断)それが原音のため、wavへ戻してから適用(二重適用防止)。
    ASR NGなら原音へ戻し、移行せずNone(通常の再生成経路=外側ループのretry上限内)。"""
    import er003_v1_n3_01_tts_generate as n3_tts
    cur, orig = f"{narr}/{spec.clip_id}.wav", f"{narr}/{spec.clip_id}_original.wav"
    if not os.path.exists(cur):
        return None
    if os.path.exists(orig):
        shutil.copyfile(orig, cur)
    before_sha = _sha_file(cur)
    stub = {"status": "OK", "asr_text": prev.get("asr_text"), "audio_text_deviation": prev.get("audio_text_deviation"),
            "duration_seconds": prev.get("duration_seconds"), "text": prev.get("text")}
    res = n3_tts.apply_a2_slowdown_postprocess(spec.clip_id, narr, _norm_for_tts(spec), stub, is_last_slot=True,
                                               log_human_review=False, slowdown_pct=Z_ADV_DIALOGUE_SLOWDOWN_PCT)
    if res.get("status") != "OK" or not res.get("slowdown_applied"):
        if os.path.exists(orig):
            shutil.copyfile(orig, cur)
        return None
    new = dict(prev)
    sd = res.get("slowdown_info") or {}
    ratio = round(sd["dst_duration_seconds"] / sd["src_duration_seconds"], 4) if sd.get("dst_duration_seconds") and sd.get("src_duration_seconds") else None
    new.update({"sha256": _sha_file(cur), "duration_seconds": round(_wav_duration(cur), 3), "slowdown_applied": True,
                "slowdown_ratio": ratio, "reuse_key": build_reuse_key(spec),
                "speed_profile": {**build_speed_profile_record(spec, res, cur), "source": "migrated_via_formal_postprocess"},
                "speed_migration": _speed_migration_record(spec, prev, asr_recheck="unified_judge(apply_a2_slowdown_postprocess)",
                                                           pre_speed_sha256=before_sha,
                                                           post_speed_asr_text=res.get("post_slowdown_asr_text"))})
    if res.get("asr_judgement") is not None:
        new["asr_judgement"] = res["asr_judgement"]
    return new


def migrate_legacy_dialogue_speed(cached: dict | None, plan: list, run_dir: str, level: str) -> tuple:
    """速度仕様v2への移行(TTS再生成なし)。reuse_keyが『速度仕様導入前のkey』と完全一致するOKの会話entryだけを対象に、
    Std=減速前原音へ戻す / Adv=約6%高速化を正式後処理で適用する。移行後entryは新reuse_keyを持つので通常の再利用経路へ乗る。
    移行できない旧entryは触らない(新keyと不一致のままprune_cached_to_planで刈られ、通常の再生成経路[retry上限内]に回る=旧仕様音声が新仕様として再利用されない)。
    戻り値=(cached, report)。"""
    report = []
    if not cached:
        return cached, report
    level_dir = f"{run_dir}/{level}"
    narr = narration_dir_for(run_dir, level)
    import er005_cost_logger as cl
    for spec in plan:
        if spec.kind != "dialogue":
            continue
        prev = _cached_entry(cached, spec)
        if not prev or prev.get("status") != "OK" or "speed_profile" in (prev.get("reuse_key") or {}) or prev.get("speed_profile"):
            continue
        if prev.get("reuse_key") != build_legacy_reuse_key(spec):
            continue
        _check_stop_sentinel(run_dir, f"tts_speed_migrate:{spec.clip_id}")
        with cl.segment_context(spec.clip_id):
            new = (_migrate_one_std_dialogue if spec.level == "a2" else _migrate_one_adv_dialogue)(spec, prev, narr, level_dir)
        report.append({"clip_id": spec.clip_id, "level": spec.level, "migrated": new is not None,
                       "profile": speed_profile_name(spec.level, spec.kind)})
        if new is not None:
            cached["segments"][spec.clip_id] = new
    if report:
        os.makedirs(f"{level_dir}/audit", exist_ok=True)
        _write_json(f"{level_dir}/audit/speed_migration_{SUB_TASK_ID}.json", {"version": Z_SPEED_PROFILE_VERSION, "clips": report})
    return cached, report


def _merge_checkpoint(cached: dict | None, ck: dict | None) -> dict | None:
    if not ck:
        return cached
    out = {"segments": dict((cached or {}).get("segments") or {}),
           "key_phrases": {k: dict(v) for k, v in ((cached or {}).get("key_phrases") or {}).items()}}
    out["segments"].update(ck.get("segments") or {})
    for rank, subs in (ck.get("key_phrases") or {}).items():
        out["key_phrases"].setdefault(rank, {}).update(subs)
    return out


_KP_SUBKEY = {"kp_en": "english", "kp_ja": "japanese_meaning", "kp_expl_en": "explanation"}


def _cached_entry(cached: dict | None, spec: ClipSpec):
    if not cached:
        return None
    if spec.kind in ("kp_en", "kp_ja", "kp_expl_en"):
        sub = _KP_SUBKEY[spec.kind]
        return ((cached.get("key_phrases") or {}).get(str(spec.rank)) or {}).get(sub)
    return (cached.get("segments") or {}).get(spec.clip_id)


@secondary_run_scope.with_secondary_run  # AUW 委任_05: run単位SecondaryCache+circuit breaker
@er109_scope.family_scope("Z")  # ASR-HOMOPHONE 委任_04: er109 run scope(Z)。PNAP hookとは独立(PNAP flag OFFでも有効)。例外・STOP時もfinallyで復元
def run_tts_stage(run_dir: str, level: str, plan: list, *, generators: dict | None = None, dry_run: bool = False,
                  only_clips: set | None = None, revalidate_fn=None, article_text: str | None = None,
                  story_key: str = DEFAULT_SLUG) -> dict:
    """PNAP 委任_02(5-3/5-6/5-7): 固有名詞アラーム方針のrun scope(Z)とfinallyの完成報告hookで`_run_tts_stage_impl`を包む。
    flag(PROPER_NOUN_ALARM_POLICY_ENABLED)がOFF・dry_runのときは従来どおり(scope/hook無し)。"""
    if dry_run:
        return _run_tts_stage_impl(run_dir, level, plan, generators=generators, dry_run=dry_run, only_clips=only_clips,
                                   revalidate_fn=revalidate_fn, article_text=article_text, story_key=story_key)
    import er103_pnap_runner_hooks_01 as _pnap_hooks
    import er103_run_entity_table_01 as _ret   # ASR-QUALITY PN 委任_04(OPEN-472): Run Entity Table構築provider(構築点はhook 1か所。dry_runはここへ来ない=API 0)
    return _pnap_hooks.run_with_alarm_hook(
        "Z", f"{run_dir}/{level}", _run_tts_stage_impl, run_dir, level, plan, generators=generators, dry_run=dry_run,
        only_clips=only_clips, revalidate_fn=revalidate_fn, article_text=article_text, story_key=story_key,
        _ret_provider=(lambda: _ret.ZProvider(run_dir, level, plan)))


def _run_tts_stage_impl(run_dir: str, level: str, plan: list, *, generators: dict | None = None, dry_run: bool = False,
                        only_clips: set | None = None, revalidate_fn=None, article_text: str | None = None,
                        story_key: str = DEFAULT_SLUG) -> dict:
    """plan(ClipSpec列)をTTS生成し audit/tts_generation_results.json(+Z拡張)を書く。
    dry_run=Trueはファイル・Master Store・telemetry・queueへ一切書かず、計画のみ返す。
    Local Rewrite発火clipは audio_text_deviation をprovenanceへ監査記録する(2026-10-12ユーザー決定: er061再検証フックは撤去。
    revalidate_fn引数は互換のため残すが呼ばない)。
    STOPセンチネル(<run>/STOP または STOP_ALL)が存在すれば、各clipの新規API呼出の前に停止する(委任_11)."""
    assert_style_table_integrity()
    level_dir = f"{run_dir}/{level}"
    narr = narration_dir_for(run_dir, level)
    planned = [{"clip_id": s.clip_id, "kind": s.kind, "voice": s.voice, "role_style_key": s.role_key,
                "style_label": FAMILY_Z_ROLE_STYLE[s.role_key]["style_label"], "out_path": f"{narr}/{s.wav_name()}",
                "layout_valid": layout_is_valid(f"{narr}/{s.wav_name()}")} for s in plan]
    if dry_run:
        return {"dry_run": True, "planned": planned, "writes": 0,
                "style_record": inspect_run_style_record(level_dir, level)}
    # 委任_15(Opus R-C4): 生成器(TTS client)を作る前・課金前に、run単位の全Role Style記録(不一致/記録なし+結果ファイル有り=STOP)を確認する。
    assert_run_style_record(level_dir, level, write=False)
    _chunk_plans = chunk_plans_from_specs(plan)
    if only_clips and _chunk_plans:
        # --only-clips <親id> は当該親の全chunkへ展開(<chunk id>直接指定も可)
        only_clips = set(only_clips) | {s.clip_id for s in plan if ((s.extra or {}).get("chunk") or {}).get("parent_id") in only_clips}
    if _chunk_plans:
        # 再計画禁止(resume): 同一本文・同一版で保存済みplanと分割が食い違えば課金前にSTOP(planは原稿の純関数)
        chunk_tts.reconcile_saved_plan(f"{level_dir}/audit/chunk_plan_{level}.json", _chunk_plans)
    # FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01(Opus M-5): LLMを呼ばないrun単位policy解決と文脈入力の付与を、cached読込・reuse_key評価(prune/migrate/再利用)より前に行う。
    prepare_dialogue_ctx(run_dir, level, plan, story_key=story_key, only_clips=only_clips)
    cached = load_results(level_dir)
    if level == chunk_tts.STD_LEVEL:
        # CHUNK-TTS-STD 委任_03(Opus M3): 減速証跡のないStd chunk entryは再利用しない。--only-clipsで選ばれなかったclipの再利用(下の
        # _cached_entry→_store)は generate_or_reuse_z を通らないため、load_results直後に落とす(checkpoint統合後にも再適用)。
        cached = chunk_tts.drop_cached_std_chunks_without_slowdown(cached)
    cached = _merge_checkpoint(cached, load_checkpoint(level_dir))   # 委任_10: process中断時もOK clipを再利用(再課金しない)
    if level == chunk_tts.STD_LEVEL:
        cached = chunk_tts.drop_cached_std_chunks_without_slowdown(cached)
    cached, _speed_migration = migrate_legacy_dialogue_speed(cached, plan, run_dir, level)   # 速度仕様v2: 旧会話entryをTTS再生成なしで移行(ASRはAdvのみ)
    cached = prune_cached_to_plan(cached, plan)   # KPFT 委任_02(OF-KPFT-P-09): 旧rank/旧語句(reuse_key不一致。reuse_keyを持たないentryは判定不能のため従来どおり保持)を再利用経路へ入れない
    gens = generators or real_generators()
    os.makedirs(narr, exist_ok=True)
    os.makedirs(f"{level_dir}/audit", exist_ok=True)
    write_style_actual_marker_if_fresh(level_dir, level)   # FAMILY-Z-STYLE-ACTUAL-GATE-01: 新規levelの開始だけでstrict(本Gate導入後のrun)を記録
    assert_run_style_record(level_dir, level, write=True)
    segments, key_phrases, evidence = {}, {}, []
    deferred_stop = None
    er127.register_stop_check(lambda where: _check_stop_sentinel(run_dir, where))      # 委任_02: 統一3回構成の180秒待機中もZのSTOP sentinelを確認
    import er005_cost_logger as cl
    for spec in plan:
        out_path = f"{narr}/{spec.wav_name()}"
        if not layout_is_valid(out_path):
            raise FamilyZAudioStop(f"narration配置が不正です(.../<run>/<level>/narration/<segment>.wav): {out_path}")
        if only_clips and spec.clip_id not in only_clips:
            prev = _cached_entry(cached, spec)
            # KPFT 委任_02(OF-KPFT-P-09): key照合なしの流用を塞ぐ(同じrun dirでKPを再生成した後の部分再生成で旧語句の音声が混入しうる)。
            if prev is not None and prev.get("reuse_key") in (None, build_reuse_key(spec)):
                _store(segments, key_phrases, spec, prev)
            continue
        cb = _cached_entry(cached, spec)
        gen_fn = gens[spec.kind]
        _check_stop_sentinel(run_dir, f"tts:{spec.clip_id}")       # 委任_11: 各clip(新規API呼出になりうる)の直前
        with cl.segment_context(spec.clip_id):
            entry = generate_or_reuse_z(
                cb, spec, out_path,
                lambda spec=spec, out_path=out_path, gen_fn=gen_fn: build_entry(spec, out_path, gen_fn(spec, out_path)))
        if entry.get("audio_text_deviation") and not entry.get("reused_from_previous_run"):
            try:
                _handle_local_rewrite(entry, spec, article_text, revalidate_fn, story_key, level, run_dir)
            except FamilyZLocalRewriteStop as e:
                deferred_stop = e  # 監査記録を書き終えてからSTOPする(実費をかけた生成結果を失わない)
        entry = normalize_technical_stop_entry(spec, out_path, entry)
        _ch = (spec.extra or {}).get("chunk")
        if _ch:
            chunk_tts.attach_chunk_meta(entry, _ch["parent_id"], {"index": _ch["index"], "words": _ch["words"], "boundary_kind": _ch["boundary_kind"]}, _ch["count"],
                                    level=spec.level)   # Std(a2)のときだけ減速合成方式をchunk_ttsへ記録。Adv(b1b)はバイト不変
        _store(segments, key_phrases, spec, entry)
        evidence.append(_evidence_row(spec, out_path, entry))
        save_checkpoint(level_dir, segments, key_phrases)
        if deferred_stop is not None:
            break
    import er011_human_review_lock_01 as review_lock
    results_path = f"{level_dir}/audit/tts_generation_results.json"
    if _chunk_plans:
        # M2(a)(b)(d): chunk親集約entry(失敗・未生成でも常に書く)+親wav(生連結)。C7: chunk TTSのruntime evidence
        refresh_chunk_parents(level_dir, plan, segments)
        _write_json(f"{level_dir}/audit/chunk_tts_evidence_{level}.json", {
            "level": level, "planner_version": chunk_tts.CHUNK_PLANNER_VERSION, "tts_backend": TTS_BACKEND,
            "parents": {pid: chunk_tts.evidence_record(pl, segments) for pid, pl in _chunk_plans.items()}})
    review_lock.archive_prior_tts_results(results_path)
    doc = {"segments": segments, "key_phrases": key_phrases, "tts_backend": TTS_BACKEND,
           "style_version": FAMILY_Z_ROLE_STYLE_VERSION, "management_id": MANAGEMENT_ID, "level": level}
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    # AUW 委任_03: 生成完了hook。results確定直後に事後試聴リスト(PASS_WITH_WARNING)を再導出して
    # audit/pass_with_warning_listening_list.jsonへ出力(失敗しても生成は失敗させない、非ブロッキング)。
    import er078_pass_with_warning_registry_01 as _pww
    _pww.write_listening_list_safe(level_dir)
    if os.path.exists(_checkpoint_path(level_dir)):
        os.remove(_checkpoint_path(level_dir))        # 最終results確定後は途中経過を残さない(古い内容で上書きされない)
    ev_path = f"{level_dir}/audit/runtime_evidence_{SUB_TASK_ID}.json"
    with open(ev_path, "w", encoding="utf-8") as f:
        json.dump({"level": level, "style_version": FAMILY_Z_ROLE_STYLE_VERSION, "clips": evidence}, f, ensure_ascii=False, indent=2)
    if deferred_stop is not None:
        raise deferred_stop
    return {"dry_run": False, "planned": planned, "results_path": results_path, "evidence_path": ev_path,
            "statuses": {r["clip_id"]: r["status"] for r in evidence}}


def normalize_technical_stop_entry(spec: ClipSpec, out_path: str, entry: dict) -> dict:
    """AUW 委任_06e(F2): circuit open時に`guard_generate`が返す技術STOP entry(`technical_stop=True`、`style`等を持たない最小dict)を、
    通常entryと同じ形(`build_entry`)にして返す。06dの`tstop`ではこのentryが`build_entry`を通らず`_evidence_row`が
    `KeyError: 'style'`で`run_tts_stage`を異常終了させた。status/technical_stop/restartable/approval_required/
    human_review_required/reason/events等の技術STOP固有keyは保持する。音声は生成していないため`sha256`/`duration_seconds`は
    None(前回の残存wavを今回の結果として記録しない)。通常entry(`style`あり)はそのまま返す。"""
    if not (isinstance(entry, dict) and entry.get("technical_stop") is True and "style" not in entry):
        return entry
    base = build_entry(spec, out_path, {"status": entry.get("status")})
    base.update(entry)
    base["sha256"] = None
    base["duration_seconds"] = None
    base["z_adoption"] = "failed"
    return base


def _store(segments: dict, key_phrases: dict, spec: ClipSpec, entry: dict) -> None:
    if spec.kind in ("kp_en", "kp_ja", "kp_expl_en"):
        key_phrases.setdefault(str(spec.rank), {})[_KP_SUBKEY[spec.kind]] = entry
    else:
        segments[spec.clip_id] = entry


def _evidence_row(spec: ClipSpec, out_path: str, entry: dict) -> dict:
    return {
        "clip_id": spec.clip_id, "out_path": out_path, "derived_segment_id": entry.get("segment_id"),
        "role": entry.get("role"), "kind": spec.kind, "voice": entry.get("voice"),
        "model_ids_measured": entry.get("model_ids_measured"), "style_label": entry["style"]["instruction_label"],
        "style_prefix_sha256": entry["style"]["style_prefix_sha256"],
        "effective_style_prefix_sha256": entry["style"].get("effective_style_prefix_sha256"), "fallback_used": entry["style"]["fallback_used"],
        "fallback_attempts": entry["style"]["fallback_attempts"], "attempt_count": len(entry.get("attempts") or []),
        "asr_text": entry.get("asr_text"), "status": entry.get("status"), "z_adoption": entry.get("z_adoption"),
        "local_rewrite_diff": entry.get("audio_text_deviation"), "cooldown_occurred": entry.get("cooldown_occurred"),
        "slowdown_applied": entry.get("slowdown_applied"), "slowdown_ratio": entry.get("slowdown_ratio"),
        "speed_profile": entry.get("speed_profile"),
        "reused": bool(entry.get("reused_from_previous_run")), "duration_seconds": entry.get("duration_seconds"),
        "cost_jpy": entry.get("cost_jpy"),
        **({"dialogue_tts": entry["dialogue_tts"]} if isinstance(entry.get("dialogue_tts"), dict) else {}),
    }


# ------------------------------------------------------------
# M6: Local Rewrite発火時の再検証フック(er061は遅延import。04A未完でもmockで通る)
# ------------------------------------------------------------
def apply_deviation_to_article(article_text: str, before: str, after: str) -> str:
    if not article_text:
        return after or ""
    if before and before in article_text:
        return article_text.replace(before, after, 1)
    norm = lambda s: re.sub(r"\s+", " ", s or "").strip()
    nb, na = norm(before), norm(article_text)
    if nb and nb in na:
        return na.replace(nb, norm(after), 1)
    return article_text + "\n\n" + (after or "")


def _handle_local_rewrite(entry: dict, spec: ClipSpec, article_text, revalidate_fn, story_key: str, level: str,
                          run_dir: str) -> None:
    """Local Rewrite採択clip: audio_text_deviation(原稿とのずれ)を監査記録するのみ。
    2026-10-12ユーザー決定により、er061による再検証(revalidate_after_local_rewrite)は撤去した
    (revalidate_fn は互換のため受けるが呼ばない。STOPもしない)。"""
    dev = entry["audio_text_deviation"]
    entry["local_rewrite_revalidation"] = {"verdict": "NOT_REQUIRED",
                                           "reason": "2026-10-12ユーザー決定: er061再検証フック撤去(audio_text_deviationの監査記録のみ)"}
    # provenance.audio_text_deviations へ追記(canonicalはそのまま。KP gateへは原稿のまま渡す)
    prov_path = f"{run_dir}/writer/provenance.json"
    if os.path.exists(prov_path):
        prov = _read_json(prov_path)
        prov.setdefault("audio_text_deviations", []).append(
            {"clip_id": spec.clip_id, "canonical_text_before_local_rewrite": dev["canonical_text_before_local_rewrite"],
             "audio_text_after": dev["audio_text_after"], "diff_summary": dev["diff_summary"]})
        _write_json(prov_path, prov)


# ============================================================
# 8. Gate(M1 / M2 + 既存Gate)
# ============================================================
def required_clip_ids(plan: list, shell_names: list) -> list:
    return [s.clip_id for s in plan] + list(shell_names)


def _lookup_entry(data: dict, clip_id: str):
    seg = (data.get("segments") or {}).get(clip_id)
    if seg is not None:
        return seg
    m = re.fullmatch(r"kp([0-9]+)_(en|ja|explanation_en)", clip_id)
    if m:
        sub = {"en": "english", "ja": "japanese_meaning", "explanation_en": "explanation"}[m.group(2)]
        return ((data.get("key_phrases") or {}).get(m.group(1)) or {}).get(sub)
    return None


def assert_tts_results_complete(level_dir: str, required_clip_ids_: list) -> dict:
    """M2: Gate呼出の直前に必ず実行。(i)ファイル存在 (ii)JSON読込可 (iii)required全entry存在かつ採択済み。"""
    p = f"{level_dir}/audit/tts_generation_results.json"
    if not os.path.exists(p):
        raise FamilyZTtsResultsIncompleteStop(f"tts_generation_results.json が存在しません: {p}")
    try:
        data = _read_json(p)
    except Exception as e:
        raise FamilyZTtsResultsIncompleteStop(f"tts_generation_results.json を読めません: {e}")
    if not isinstance(data, dict) or not (data.get("segments") or data.get("key_phrases")):
        raise FamilyZTtsResultsIncompleteStop("tts_generation_results.json が空です")
    approvals_p = f"{level_dir}/audit/human_approved_segments.json"
    approvals = _read_json(approvals_p) if os.path.exists(approvals_p) else {}
    missing, not_adopted, deviations = [], [], []
    for cid in required_clip_ids_:
        e = _lookup_entry(data, cid)
        if e is None:
            missing.append(cid)
            continue
        ok = e.get("status") == "OK" or e.get("z_adoption") in ("adopted", "human_review_adopted") and e.get("status") == "OK" \
            or (cid in approvals or f"kp{cid}" in approvals)
        # 2026-10-12ユーザー決定③(原作保持Validator撤廃)+Fable判断(委任_12D): Local Rewrite採択clipは
        # local_rewrite_revalidation.verdict(NOT_REQUIRED)を不採択理由にしない。audio_text_deviationを監査記録として出力する。
        if ok and e.get("audio_text_deviation"):
            dv = e["audio_text_deviation"]
            deviations.append({"clip_id": cid, "canonical_text_before_local_rewrite": dv.get("canonical_text_before_local_rewrite"),
                               "audio_text_after": dv.get("audio_text_after"), "diff_summary": dv.get("diff_summary"),
                               "local_rewrite_revalidation_verdict": (e.get("local_rewrite_revalidation") or {}).get("verdict")})
        if not ok:
            not_adopted.append(f"{cid}={e.get('status')}")
    if missing or not_adopted:
        raise FamilyZTtsResultsIncompleteStop(f"required clip entry 欠落={missing} 未採択={not_adopted}")
    return {"checked": len(required_clip_ids_), "path": p, "audio_text_deviations": deviations}


def _std_chunk_slowdown_check(required_clip_entries: dict, chunk_plans: dict | None) -> dict:
    """CHUNK-TTS-STD 委任_03(Opus M2): Std chunk idの速度Gate(厳格)。chunk entryに slowdown_applied is True と、記録された減速前後長の比
    ∈[1.03,1.09](両長さの記録欠落もNG)を要求する。`_original.wav`の再生時間比による弱い証拠の救済は使わない(chunkは生成時の記録だけが証拠)。
    chunk_plansが渡されればplanの全chunk id(entry欠落=NG)、無ければrequired_clip_entriesに現れたchunk idを検査する。戻り値={chunk_id: detail}、
    違反は {chunk_id: [違反ID…]} を failures として返す。"""
    plans = {}
    for pid, pl in (chunk_plans or {}).items():
        if pl.get("chunked"):
            plans[pid] = pl
    seen = {pl_c["chunk_id"] for pl in plans.values() for pl_c in pl["chunks"]}
    for cid in required_clip_entries:
        m = _CLIP_OR_CHUNK_ID_RE.fullmatch(cid)
        if m and m.group(3) and cid not in seen:
            # planが渡されない/planに無いchunk idも検査対象(抜け道を作らない)。1 chunkだけの擬似planで同じ検査関数を使う。
            plans[f"{cid}__solo"] = {"chunked": True, "parent_id": cid, "chunks": [{"chunk_id": cid, "index": 1}]}
    detail, failures = {}, []
    for pid, pl in plans.items():
        segs = {c["chunk_id"]: required_clip_entries.get(c["chunk_id"]) for c in pl["chunks"]}
        viol = {v["segment"]: v["violations"] for v in chunk_tts.std_chunk_slowdown_violations(pl, segs)}
        for c in pl["chunks"]:
            cid = c["chunk_id"]
            detail[cid] = {"ok": cid not in viol, "why": ";".join(viol.get(cid, [])) or "chunk slowdown_applied=True & ratio ok", "strict": "chunk"}
            if cid in viol:
                failures.append(f"{cid}({detail[cid]['why']})")
    return {"detail": detail, "failures": failures}


def verify_std_english_slowdown(level_dir: str, required_clip_entries: dict, narration_dir: str | None = None,
                                chunk_plans: dict | None = None) -> dict:
    """M1: 全Std英語Story clip(narrator・dialogue、_cN含む、Human Review採択も対象)で
    slowdown_applied is True、または _original.wav と現行wavの再生時間比∈[1.03,1.09]を要求する。
    (比 = 現行/original。減速後の方が長い。設計書は逆向きの記載だが、既存Gate
    _segment_missing_mandatory_a2_slowdownと同じ向きに揃える。)
    required_clip_entries: {clip_id: entry}。例外なし、1つでも不合格ならGate前にSTOP。"""
    narration_dir = narration_dir or f"{level_dir}/narration"
    failures, detail = [], {}
    for cid, entry in required_clip_entries.items():
        if not _CLIP_ID_RE.fullmatch(cid):
            continue   # chunk id(…_c{k}_k{j})は下の厳格検査(_std_chunk_slowdown_check)で扱う
        if (entry or {}).get("clip_kind") == "dialogue":
            continue   # 速度仕様v2: Std会話は減速禁止(verify_z_speed_profileが検査)。本関数は6%減速必須のStd narrator story clipのみ
        ok, why = False, ""
        if (entry or {}).get("slowdown_applied") is True:
            ok, why = True, "slowdown_applied=True"
        else:
            orig, cur = f"{narration_dir}/{cid}_original.wav", f"{narration_dir}/{cid}.wav"
            if os.path.exists(orig) and os.path.exists(cur):
                try:
                    ratio = _wav_duration(cur) / _wav_duration(orig)
                    ok = SLOWDOWN_RATIO_MIN <= ratio <= SLOWDOWN_RATIO_MAX
                    why = f"ratio={ratio:.4f}"
                except Exception as e:
                    why = f"duration unreadable: {e}"
            else:
                why = "no slowdown record and no _original.wav"
        detail[cid] = {"ok": ok, "why": why}
        if not ok:
            failures.append(f"{cid}({why})")
    _ck = _std_chunk_slowdown_check(required_clip_entries, chunk_plans)   # M2: chunk idは厳格(_original.wav弱証拠なし)
    detail.update(_ck["detail"])
    failures.extend(_ck["failures"])
    if failures:
        raise FamilyZSlowdownGateStop(f"Std英語Story clipに6%減速の証跡がありません: {failures}")
    return detail


def verify_z_speed_profile(level: str, required_clip_entries: dict, narration_dir: str) -> dict:
    """速度仕様v2の未適用/誤適用ガード(Gate前、1つでも不合格ならFamilyZSlowdownGateStop)。
    Std(a2): narrator story clip=6%減速必須(verify_std_english_slowdown)、dialogue=減速禁止(speed_profile=std_dialogue_none・
    slowdown_applied非True・`_original.wav`が残っていれば現行wavとの長さ比≈1)。
    Adv(b1b): dialogue=約6%高速化必須(speed_profile.applied・tempo≈1.06・`_original.wav`との長さ比0.93〜0.96)、narrator=処理なし。
    旧仕様の誤適用(Std会話の減速済み/Adv会話の未処理)をここで検知する。Xには影響しない(Zのrun_audio_gateからのみ呼ぶ)。"""
    failures, detail = [], {}
    for cid, e in required_clip_entries.items():
        e = e or {}
        kind = e.get("clip_kind")
        if kind not in ("narrator", "dialogue") or not _CLIP_OR_CHUNK_ID_RE.fullmatch(cid):   # R2: chunk idもAdv narrator(処理なし)の検査対象
            continue
        want = speed_profile_name(level, kind)
        sp = e.get("speed_profile") or {}
        why = None
        orig_sec = ratio = None
        if kind == "dialogue":
            key_sp = (e.get("reuse_key") or {}).get("speed_profile")
            if sp.get("profile") != want or sp.get("version") != Z_SPEED_PROFILE_VERSION:
                why = f"speed_profile不一致(期待={want}/{Z_SPEED_PROFILE_VERSION}, 実={sp.get('profile')}/{sp.get('version')})"
            elif key_sp != f"{Z_SPEED_PROFILE_VERSION}:{want}":
                why = f"reuse_key.speed_profile不一致({key_sp})"
        if why is None and kind == "dialogue":
            orig, cur = f"{narration_dir}/{cid}_original.wav", f"{narration_dir}/{cid}.wav"
            ratio = None
            orig_sec = None
            if os.path.exists(orig) and os.path.exists(cur):
                try:
                    orig_sec = _wav_duration(orig)
                    ratio = _wav_duration(cur) / orig_sec
                except Exception as ex:
                    why = f"duration unreadable: {ex}"
            if why is None and level == "a2":
                if sp.get("applied") or e.get("slowdown_applied") is True:
                    why = "Std会話に速度後処理が掛かっています(旧6%減速の残存)"
                elif ratio is not None and not (STD_DIALOGUE_RATIO_MIN <= ratio <= STD_DIALOGUE_RATIO_MAX):
                    why = f"Std会話wav/original長さ比={ratio:.4f}(≈1必須。減速済み音声の混入疑い)"
            elif why is None and level == "b1b":
                if not sp.get("applied") or e.get("slowdown_applied") is not True:
                    why = "Adv会話に高速化が掛かっていません(未処理=旧仕様)"
                elif abs((sp.get("tempo") or 0) - Z_ADV_DIALOGUE_SPEEDUP_TEMPO) > 0.001:
                    why = f"tempo不一致({sp.get('tempo')})"
                elif ratio is None:
                    why = "_original.wavが無く高速化の証跡を確認できません"
                else:
                    r_min, r_max = adv_dialogue_ratio_range(orig_sec)
                    if not (r_min <= ratio <= r_max):
                        why = f"Adv会話wav/original長さ比={ratio:.4f}({r_min:.2f}〜{r_max:.2f}必須、原音{orig_sec:.3f}秒)"
        elif why is None and kind == "narrator" and level == "b1b":
            if e.get("slowdown_applied") is True:
                why = "Adv Narratorに速度後処理が掛かっています(変更対象外)"
        _d = {"ok": why is None, "why": why or "ok", "profile": want}
        if kind == "dialogue" and level == "b1b" and orig_sec is not None and ratio is not None:
            _d.update({"original_seconds": round(orig_sec, 4), "ratio": round(ratio, 4),
                       "ratio_range": list(adv_dialogue_ratio_range(orig_sec))})
        detail[cid] = _d
        if why is not None:
            failures.append(f"{cid}({why})")
    if failures:
        raise FamilyZSlowdownGateStop(f"速度仕様v2({Z_SPEED_PROFILE_VERSION})違反: {failures}")
    return detail


def check_clip_audio_quality(narration_dir: str, entries: dict, *, peak_max: float = 0.999,
                             silence_rms_min: float = 1e-4) -> dict:
    """peak/clipping/無音/長さ(duration anomaly)の追加確認(既存safety関数を利用)。"""
    import er002_common as common
    import er003_audio_tts_asr_safety as safety
    problems = {}
    for cid, e in entries.items():
        p = f"{narration_dir}/{cid}.wav"
        if not os.path.exists(p):
            problems[cid] = "wav missing"
            continue
        mono = common.read_wav_float(p)[0]
        m = common.measure_metrics(mono, common.SAMPLE_RATE)
        if m["clipping_detected"]:
            problems[cid] = "clipping"
        elif 10 ** (m["rms_dbfs"] / 20) < silence_rms_min:
            problems[cid] = "silent"
        elif e.get("clip_kind") in ("narrator", "dialogue") and e.get("canonical_text"):
            an = safety.detect_duration_anomaly(m["duration_seconds"], e["canonical_text"], "en")
            if an["is_anomaly"]:
                problems[cid] = "duration anomaly"
    return problems


def run_audio_gate(run_dir: str, level: str, plan: list, shell_names: list, *, article_text: str,
                   skip_shared_gate: bool = False) -> dict:
    """Gate呼出の前に M2(存在assert) -> M1(Std減速) -> 品質確認 を実行し、既存
    asm.verify_episode_audio_validation_gate(KP source gate含む)を呼ぶ。article_textは原稿(canonical)のまま渡す
    (Local Rewriteの音声書換テキストは渡さない)。"""
    level_dir = f"{run_dir}/{level}"
    if chunk_plans_from_specs(plan):
        # M2(c): Gate・存在assertより前に、chunk親集約entry(status・親wav・human_approved_chunks)を再構築して保存する
        # (STOPPED chunkの人間承認後は、親entry/親wavが古いまま・無いままになるため)。chunk化したclipが無い(legacy含む)ならファイルに触れない。
        _rp = f"{level_dir}/audit/tts_generation_results.json"
        if os.path.exists(_rp):
            _doc = _read_json(_rp)
            refresh_chunk_parents(level_dir, plan, _doc.setdefault("segments", {}))
            _write_json(_rp, _doc)
    ids = required_clip_ids(plan, shell_names)
    m2 = assert_tts_results_complete(level_dir, ids)
    data = _read_json(f"{level_dir}/audit/tts_generation_results.json")
    entries = {cid: _lookup_entry(data, cid) for cid in ids}
    slow = None
    speed = verify_z_speed_profile(level, {k: v for k, v in entries.items() if _CLIP_OR_CHUNK_ID_RE.fullmatch(k)}, f"{level_dir}/narration")
    if level == "a2":
        slow = verify_std_english_slowdown(level_dir, {k: v for k, v in entries.items() if _CLIP_OR_CHUNK_ID_RE.fullmatch(k)},
                                           chunk_plans=chunk_plans_from_specs(plan))   # M2: chunk idも対象(厳格検査)
    problems = check_clip_audio_quality(f"{level_dir}/narration", {k: v for k, v in entries.items() if v and v.get("clip_kind")})
    if problems:
        raise FamilyZAudioStop(f"clip品質確認でNG: {problems}")
    style_actual = z_style_actual_gate(run_dir, level, plan, entries)   # FAMILY-Z-STYLE-ACTUAL-GATE-01: 実送信Style prefix==承認値(fail-closed。BLOCKは照合表を保存してからSTOP)
    deviations = {k: v["audio_text_deviation"] for k, v in entries.items() if v and v.get("audio_text_deviation")}
    result = {"m2_complete": True, "m1_slowdown": slow, "z_speed_profile": {"version": Z_SPEED_PROFILE_VERSION, "clips": speed}, "audio_text_deviation_clips": sorted(deviations),
              "kp_vote_audit": kp_vote.assembly_audit(data, level),   # KP3V: 非blocking監査(KP英語phraseのvote証跡欠落を警告+記録)
              "audio_text_deviations": m2["audio_text_deviations"],
              "article_text_source": "canonical(原稿のまま)", "shared_gate": "skipped" if skip_shared_gate else "PASS",
              "style_actual_gate": {k: style_actual[k] for k in ("status", "mode", "checked_count", "legacy_unrecorded_count", "human_approved_count", "path")}}
    if not skip_shared_gate:
        import er003_v1_n3_01_assemble as asm
        asm.verify_episode_audio_validation_gate(level_dir, GATE_LEVEL_STRING[level], article_text=article_text)
    os.makedirs(f"{level_dir}/audit", exist_ok=True)
    _write_json(f"{level_dir}/audit/gate_result_{SUB_TASK_ID}.json", result)
    return result



# ============================================================
# 8-S. Style実測照合Gate(OPEN-551、FAMILY-Z-STYLE-ACTUAL-GATE-01 委任_01)
#      再発防止方針(FAMILY-Y-STYLE-PROFILE-FIX-01 PREVENTION_01 (a)): 全Familyの正式経路で「承認Styleと実測(実送信)prefixの照合」を必須化。
#      Y方式(er121 y_style_gate)と同じ構造: 期待集合Z_ROLE_COVERAGEと検査集合の完全一致・fail-closed・audit/style_actual_vs_approved.json。
#      X(er019)・Y(er121)・leaf(er003_v1_*)は一切変更しない。実測はleafの戻り値(採用attemptのstyle_prefix / top-level style_prefix)をZ側(build_entry)で記録する。
#      過去run(本Gate導入前に開始したrun)は遡及BLOCKせず「未記録」警告(マーカー audit/style_actual_gate.json の有無で判定)。
#      設計=docs/research/FAMILY-Z-STYLE-ACTUAL-GATE-01/DESIGN_01.md。
# ============================================================
STYLE_ACTUAL_SCHEMA = "family_z_style_actual_v1"
STYLE_ACTUAL_GATE_ID = "FAMILY-Z-STYLE-ACTUAL-GATE-01"
STYLE_ACTUAL_MARKER_RELPATH = "audit/style_actual_gate.json"
STYLE_ACTUAL_OUT_RELPATH = "audit/style_actual_vs_approved.json"

# level -> role -> 必須か(True=planに1clip以上必須[0件=Z_STYLE_COVERAGE_EMPTY]、False=planにあれば検査・無くても可[Dialogue: 地の文のみの作品がある])。
# SHELLはTTSなし(既存Master資産)のため対象外。FAMILY_Z_ROLE_STYLE/CROSS_FAMILY_COMMON_STYLE_MAPとの完全一致をdriftとして検査する。
Z_ROLE_COVERAGE = {
    "a2": {"NARRATOR_FULL_STORY_STD": True, "DIALOGUE_STD": False, "TOPIC_INTRO_EN": True, "JAPANESE_TITLE": True,
           "STD_JA_PREVIEW": True, "STD_JA_COMMENT": True, "KP_EN": True, "KP_JA": False, "KP_EXPL_EN": False},
    "b1b": {"NARRATOR_FULL_STORY_ADV": True, "DIALOGUE_ADV": False, "TOPIC_INTRO_EN": True, "ADV_EN_PREVIEW": True,
            "ADV_EN_COMMENT": True, "KP_EN": True, "KP_JA": False, "KP_EXPL_EN": False},
}
# 第3KP(Std=日本語意味/Adv=英語解説)はplan builder(kp_explanationsの有無)の責務でlevelごとの固定はしない: どちらか1種以上のroleがplanに存在し、全clipが検査されることを要求する。
Z_ROLE_ANY_OF = {"KP_THIRD": ("KP_JA", "KP_EXPL_EN")}
Z_DIALOGUE_ROLES = ("DIALOGUE_ADV", "DIALOGUE_STD")      # 例外role(CROSS_FAMILY_COMMON_STYLE_MAP "EXCEPTION:Dialogue…")。Style overrideを持たず既定Dialogue Styleを期待
_Z_KP_APPROVAL_SUB = {"kp_en": "english", "kp_ja": "japanese_meaning", "kp_expl_en": "explanation"}


def _style_obs_from(sp):
    """style_prefix値(str=全文 / dict=sha256+len+head200 record / None)を観測dictへ。'<default:…>'ラベル等の実体のない値は未実測(None)。"""
    if isinstance(sp, str):
        if sp.startswith("<default"):
            return None
        return {"sha256": _sha256_text(sp), "len": len(sp), "head200": sp[:200], "form": "full_text"}
    if isinstance(sp, dict) and sp.get("sha256"):
        return {"sha256": sp.get("sha256"), "len": sp.get("len"), "head200": sp.get("head200"), "form": "record"}
    return None


def z_expected_style(role_key: str):
    """role -> 承認(意図)Style {text, sha256, label}。Dialogue(text=None)・SHELLはNone(別規則)。"""
    spec = FAMILY_Z_ROLE_STYLE[role_key]
    if spec["text"] is None:
        return None
    return {"text": spec["text"], "sha256": _STYLE_SHA256[spec["style_label"]], "label": spec["style_label"]}


def build_style_actual_record(spec: ClipSpec, result: dict) -> dict:
    """leaf戻り値から『実際に送ったStyle prefix』の実測記録を作る(API 0・新規計算のみ)。
    優先: (1)採用attempt(fallback段→標準段の順で最後にstyle記録を持つattempt) (2)top-level style_prefix。(1)がある場合top-levelは副次記録に留める
    (統一flowで採用attemptが後段fallbackでもtop-levelが旧段のままの場合に、fallbackのStyle落ちを見逃さないため)。
    どちらも実体(sha)が取れなければ kind='unmeasured'(意図値の自己記録で『一致』とは扱わない=Opus M-4)。"""
    result = result if isinstance(result, dict) else {}
    std_key = "standard_attempts_log" if result.get("standard_attempts_log") else "attempts_log"
    att_obs, att_meta = None, {}
    for phase, key in (("fallback", "fallback_attempts_log"), ("standard", std_key)):
        logs = result.get(key)
        if not isinstance(logs, list):
            continue
        for a in reversed(logs):
            obs = _style_obs_from(a.get("style_prefix")) if isinstance(a, dict) else None
            if obs:
                att_obs, att_meta = obs, {"phase": phase, "attempt": a.get("attempt"), "instruction_type": a.get("instruction_type")}
                break
        if att_obs:
            break
    top_obs = _style_obs_from(result.get("style_prefix"))
    primary, source = (att_obs, "adopted_attempt.style_prefix") if att_obs else ((top_obs, "result.style_prefix") if top_obs else (None, None))
    exp = z_expected_style(spec.role_key)
    rec = {"schema": STYLE_ACTUAL_SCHEMA, "role_key": spec.role_key,
           "kind": "measured" if primary else "unmeasured", "source": source,
           "sha256": (primary or {}).get("sha256"), "len": (primary or {}).get("len"), "head200": (primary or {}).get("head200"),
           "form": (primary or {}).get("form"),
           "hint_applied": bool((result.get("en_pronunciation_resolver_info") or {}).get("hints_applied")),
           "adopted_phase": att_meta.get("phase"), "adopted_instruction_type": att_meta.get("instruction_type") or result.get("instruction_type"),
           "result_fallback_used": bool(result.get("fallback_used")),
           "expected_sha256": (exp or {}).get("sha256")}
    if exp is not None and source == "result.style_prefix" and isinstance(result.get("style_prefix"), str):
        # 全文が見えるときだけ、承認原文で始まるか(hint追記の判定)を全長で記録する。recordのみの場合は記録しない(gateはhead200で判定)。
        rec["startswith_expected"] = result["style_prefix"].startswith(exp["text"])
    if att_obs and top_obs and att_obs["sha256"] != top_obs["sha256"]:
        rec["secondary_top_level"] = {"sha256": top_obs["sha256"], "len": top_obs.get("len")}
    return rec


def _z_prefix_match_with_hint(exp: dict, rec: dict) -> bool:
    et = exp["text"]
    if not (rec.get("hint_applied") and rec.get("head200") and rec.get("len") is not None):
        return False
    if rec.get("startswith_expected") is False:
        return False
    return rec["len"] >= len(et) and str(rec["head200"]).startswith(et[:200])


def write_style_actual_marker_if_fresh(level_dir: str, level: str) -> bool:
    """本Gate導入後に開始した新規levelのrunだけにマーカーを書く(結果/checkpointが既にあるrun=導入前に開始した過去・進行中runには書かない=遡及しない)。"""
    marker = f"{level_dir}/{STYLE_ACTUAL_MARKER_RELPATH}"
    if os.path.exists(marker):
        return False
    if os.path.exists(f"{level_dir}/audit/tts_generation_results.json") or os.path.exists(_checkpoint_path(level_dir)):
        return False
    import time as _t
    os.makedirs(f"{level_dir}/audit", exist_ok=True)
    _write_json(marker, {"schema": STYLE_ACTUAL_SCHEMA, "gate_id": STYLE_ACTUAL_GATE_ID, "level": level,
                         "created_at": _t.strftime("%Y-%m-%dT%H:%M:%S"),
                         "note": "このlevelはStyle実測照合Gate導入後に開始(strict: 未記録/不一致/未実測はBLOCK)。無い場合は過去run扱い(未記録は警告のみ)"})
    return True


def _z_role_table_drift() -> list:
    covered = {r for lv in Z_ROLE_COVERAGE.values() for r in lv}
    exp_roles = set(FAMILY_Z_ROLE_STYLE) - {"SHELL"}
    bad = []
    if covered != exp_roles:
        bad.append({"reason": "Z_STYLE_ROLE_TABLE_DRIFT", "detail": f"covered-only={sorted(covered - exp_roles)} table-only={sorted(exp_roles - covered)}"})
    if set(CROSS_FAMILY_COMMON_STYLE_MAP) != set(FAMILY_Z_ROLE_STYLE):
        bad.append({"reason": "Z_STYLE_ROLE_TABLE_DRIFT", "detail": "CROSS_FAMILY_COMMON_STYLE_MAP != FAMILY_Z_ROLE_STYLE"})
    return bad


def _z_approval_names(spec: ClipSpec) -> list:
    names = [spec.clip_id]
    if spec.kind in _Z_KP_APPROVAL_SUB:
        names.append(f"kp{spec.rank}_{_Z_KP_APPROVAL_SUB[spec.kind]}")
    return names


def _z_row_for_clip(spec: ClipSpec, entry: dict | None, strict_run: bool, approvals: dict, default_dialogue_sha: str) -> dict:
    role = spec.role_key
    exp = z_expected_style(role)
    row = {"level": spec.level, "role": role, "segment": spec.clip_id, "kind": spec.kind,
           "approved_sha256": (exp or {}).get("sha256"), "approved_label": FAMILY_Z_ROLE_STYLE[role]["style_label"],
           "role_origin": "exception" if str(CROSS_FAMILY_COMMON_STYLE_MAP[role]["Z"]).startswith("EXCEPTION") else "common",
           "measured_kind": None, "measured_sha256": None, "measured_len": None, "source": None, "match": None, "check": None,
           "violations": [], "human_approved": False, "z_adoption": (entry or {}).get("z_adoption"), "voice": (entry or {}).get("voice"),
           "fallback_used": ((entry or {}).get("style") or {}).get("fallback_used")}
    if entry is None:
        row["violations"].append("Z_STYLE_ENTRY_MISSING")
        row["check"] = "entry_missing"
        return row
    rec = entry.get("style_actual")
    if not isinstance(rec, dict):
        # 記録なし: 過去run=警告のみ(attemptsから導出できる範囲を参考情報として添える・BLOCKしない) / 導入後run=BLOCK
        att = None
        for a in reversed(entry.get("attempts") or []):
            if a.get("style_prefix_sha256"):
                att = a
                break
        row["legacy_derived_from_attempts"] = ({"sha256": att["style_prefix_sha256"], "phase": att.get("phase"), "instruction_type": att.get("instruction_type")}
                                              if att else None)
        if exp is not None and att:
            row["legacy_derived_matches_approved"] = att["style_prefix_sha256"] == exp["sha256"]
        row["check"] = "unrecorded" if strict_run else "legacy_unrecorded"
        if strict_run:
            row["violations"].append("Z_STYLE_ACTUAL_UNRECORDED")
    else:
        row.update({"measured_kind": rec.get("kind"), "measured_sha256": rec.get("sha256"), "measured_len": rec.get("len"), "source": rec.get("source"),
                    "hint_applied": rec.get("hint_applied"), "adopted_phase": rec.get("adopted_phase"),
                    "adopted_instruction_type": rec.get("adopted_instruction_type")})
        fb_phase = (rec.get("adopted_phase") == "fallback" or "minimal" in str(rec.get("adopted_instruction_type") or "")
                    or rec.get("result_fallback_used") is True)
        if role in Z_DIALOGUE_ROLES:
            # 例外role(Dialogue): Style overrideを渡さず既定Dialogue Style(p9a.ENGLISH_STYLE_PREFIX)。leaf(er012)は送信prefixを返さないため実測は原則取れない。
            # 取れた場合は既定sha(またはctx採用時のctx style sha)との一致を要求。取れない場合は『意図sha(実測なし)』ラベルで、一致扱いにはしない(match=None)が、
            # 意図shaが既定Dialogue Style(またはctx style)と食い違えばBLOCK。従来方式(3回目)への切替はDialogueの承認済み構成でありStyle落ちではない。
            dt = entry.get("dialogue_tts") or {}
            eff = (entry.get("style") or {}).get("effective_style_prefix_sha256")
            ctx_sha = dt.get("ctx_style_sha256") if dt.get("final_mode") == "ctx" else None
            allowed = {default_dialogue_sha} | ({ctx_sha} if ctx_sha else set())
            if rec.get("kind") == "measured":
                ok = rec.get("sha256") in allowed
                row.update({"match": ok, "check": "dialogue_measured"})
                if not ok:
                    row["violations"].append("Z_DIALOGUE_STYLE_ACTUAL_MISMATCH")
            else:
                ok = eff in allowed
                row.update({"match": None, "check": "dialogue_intended_only", "measured_kind": "意図sha(実測なし・leaf非公開)",
                            "measured_sha256": eff, "measurement_gap": True})
                if not ok:
                    row["violations"].append("Z_DIALOGUE_STYLE_INTENDED_MISMATCH")
        else:
            if rec.get("kind") != "measured" or not rec.get("sha256"):
                row.update({"match": False, "check": "unmeasured", "measured_kind": "意図sha(実測なし)", "measured_sha256": None})
                row["violations"].append("Z_STYLE_ACTUAL_UNMEASURED")
            else:
                exact = rec["sha256"] == exp["sha256"]
                hint_ok = (not exact) and _z_prefix_match_with_hint(exp, rec)
                row.update({"match": bool(exact or hint_ok), "check": "exact" if exact else ("prefix_with_hint" if hint_ok else "mismatch")})
                if not (exact or hint_ok):
                    row["violations"].append("Z_STYLE_ACTUAL_MISMATCH")
            if fb_phase and row["violations"]:
                row["violations"].append("Z_STYLE_FALLBACK_ADOPTED")      # Style落ちfallback採用: 人間承認必須(承認Styleのまま送られたfallbackは違反にしない)
    if row["violations"]:
        for nm in _z_approval_names(spec):
            if _xs._approved(approvals, nm, entry):
                row["human_approved"] = True
                break
    return row


def z_style_actual_gate(run_dir: str, level: str, plan: list, entries: dict) -> dict:
    """実送信Style prefixと承認値の照合(fail-closed)。期待集合(planのTTS clip: role×clip)と検査集合の完全一致、必須roleのカバー、
    checked空、未記録、未実測、不一致、Style落ちfallback採用(人間承認なし)をBLOCK。audit/style_actual_vs_approved.json に照合表を残し、BLOCKならFamilyZStyleActualGateStop。
    過去run(マーカー無し)の未記録clipは警告のみ(遡及しない)。記録のあるclipはrun種別によらず厳格に検査。"""
    level_dir = f"{run_dir}/{level}"
    os.makedirs(f"{level_dir}/audit", exist_ok=True)
    strict_run = os.path.exists(f"{level_dir}/{STYLE_ACTUAL_MARKER_RELPATH}")
    approvals_p = f"{level_dir}/audit/human_approved_segments.json"
    approvals = _read_json(approvals_p) if os.path.exists(approvals_p) else {}
    import er003_b1_p9a_audio as _p9a
    default_dialogue_sha = style_prefix_sha256(_p9a.ENGLISH_STYLE_PREFIX)
    cov = Z_ROLE_COVERAGE.get(level) or {}
    rows, blocked, warnings = [], [], []
    for b in _z_role_table_drift():
        blocked.append({"segment": "(table)", "violations": [b["reason"]], "detail": b["detail"]})
    any_recorded = any(isinstance((entries.get(s.clip_id) or {}).get("style_actual"), dict) for s in plan)
    coverage_enforced = strict_run or any_recorded
    plan_roles = {}
    for spec in plan:
        plan_roles.setdefault(spec.role_key, []).append(spec.clip_id)
        if spec.role_key not in cov:
            blocked.append({"segment": f"{spec.role_key}:{spec.clip_id}", "violations": ["Z_STYLE_COVERAGE_UNEXPECTED"]})
            continue
        row = _z_row_for_clip(spec, entries.get(spec.clip_id), strict_run, approvals, default_dialogue_sha)
        rows.append(row)
        if row["violations"] and not row["human_approved"]:
            blocked.append({"segment": spec.clip_id, "role": spec.role_key, "violations": row["violations"]})
        elif row["check"] == "legacy_unrecorded":
            warnings.append({"segment": spec.clip_id, "role": spec.role_key, "warning": "Z_STYLE_ACTUAL_UNRECORDED_LEGACY_RUN"})
            if row.get("legacy_derived_matches_approved") is False:    # 過去runでもattempts_logから不一致が読めるclipは警告で可視化(BLOCKはしない)
                warnings.append({"segment": spec.clip_id, "role": spec.role_key, "warning": "Z_STYLE_LEGACY_DERIVED_MISMATCH",
                                 "derived": row.get("legacy_derived_from_attempts")})
    missing_roles = sorted(r for r, req in cov.items() if req and not plan_roles.get(r))
    missing_roles += sorted(g for g, members in Z_ROLE_ANY_OF.items() if not any(plan_roles.get(m) for m in members))
    checked = [r for r in rows if r["check"] not in ("legacy_unrecorded", "unrecorded", "entry_missing")]
    coverage = {"expected_roles": {r: bool(req) for r, req in cov.items()}, "plan_roles": {r: len(v) for r, v in sorted(plan_roles.items())},
                "missing_required_roles": missing_roles, "expected_clip_count": len(plan), "row_count": len(rows),
                "checked_count": len(checked), "enforced": coverage_enforced}
    if coverage_enforced:
        for r in missing_roles:
            blocked.append({"segment": f"{r}:*", "violations": ["Z_STYLE_COVERAGE_EMPTY"]})
        if len(rows) != len(plan):
            blocked.append({"segment": "(coverage)", "violations": ["Z_STYLE_COVERAGE_MISMATCH"], "detail": f"plan={len(plan)} rows={len(rows)}"})
        if not checked:
            blocked.append({"segment": "(all)", "violations": ["Z_STYLE_CHECKED_EMPTY"]})
    elif missing_roles:
        warnings.append({"warning": "Z_STYLE_COVERAGE_EMPTY_LEGACY_RUN", "roles": missing_roles})
    legacy_n = sum(1 for r in rows if r["check"] == "legacy_unrecorded")
    human_n = sum(1 for r in rows if r["human_approved"])
    res = {"schema": STYLE_ACTUAL_SCHEMA, "gate_id": STYLE_ACTUAL_GATE_ID, "level": level, "status": "BLOCK" if blocked else "PASS",
           "mode": "strict" if strict_run else ("legacy_run_recorded_clips_strict" if any_recorded else "legacy_run_warning_only"),
           "marker_present": strict_run, "coverage": coverage, "blocked": blocked, "warnings": warnings,
           "checked_count": len(checked), "legacy_unrecorded_count": legacy_n, "human_approved_count": human_n,
           "all_match": bool(checked) and all(r["match"] is True for r in checked if r["check"] != "dialogue_intended_only"),
           "rows_count": len(rows), "rows": rows, "path": f"{level_dir}/{STYLE_ACTUAL_OUT_RELPATH}"}
    _write_json(res["path"], res)
    if blocked:
        raise FamilyZStyleActualGateStop(f"Style実測照合Gate BLOCK({level}): " + "; ".join(
            f"{b.get('segment')}={','.join(b['violations'])}" for b in blocked[:12]) + (" …" if len(blocked) > 12 else "")
            + f" (照合表={res['path']}。Style落ちfallback等は人間承認[human_approved_segments.json]が必要)")
    return res


# ============================================================
# 9. Assembly(Family C assemble_with_timeline / sequence builderを再利用)
# ============================================================
SHELL_ASSET_SOURCES = {
    "welcome": "welcome_charon.wav", "preview_intro": "preview_intro_charon.wav",
    "key_phrases_intro": "key_phrases_intro_charon.wav", "full_story_intro": "full_story_intro_charon.wav",
}
NUMBER_ASSET_SOURCES = {f"kp{i}_number": f"num_{w}_charon.wav" for i, w in enumerate(["one", "two", "three", "four", "five"], 1)}


def provision_shell_assets(run_dir: str, level: str, kp_count: int, *, dry_run: bool = False) -> dict:
    """shell/番号は既存共有Production資産を読み取りコピー(Master Store書込なし)。entryはGate互換(status OK+sha)。"""
    import er003_v1_n3_01_assemble as asm
    narr = narration_dir_for(run_dir, level)
    entries = {}
    for name, src_name in {**SHELL_ASSET_SOURCES, **{k: v for k, v in NUMBER_ASSET_SOURCES.items() if int(k[2]) <= kp_count}}.items():
        src, dst = f"{asm.B1_SHARED_SOURCE_DIR}/{src_name}", f"{narr}/{name}.wav"
        if dry_run:
            entries[name] = {"src": src, "dst": dst}
            continue
        os.makedirs(narr, exist_ok=True)
        shutil.copyfile(src, dst)
        entries[name] = {"status": "OK", "path": dst, "sha256": _sha_file(dst), "canonical_text": None,
                         "disfluency_checked": True, "reused": True, "clip_kind": "shell", "voice": "Charon",
                         "segment_id": name, "tts_backend": "existing_master",
                         "style": {"instruction_label": FAMILY_Z_ROLE_STYLE["SHELL"]["style_label"], "style_prefix_sha256": None,
                                   "fallback_used": False}}
    if not dry_run:
        lvl = f"{run_dir}/{level}"
        data = load_results(lvl) or {"segments": {}, "key_phrases": {}}
        data.setdefault("segments", {}).update(entries)
        os.makedirs(f"{lvl}/audit", exist_ok=True)
        _write_json(f"{lvl}/audit/tts_generation_results.json", data)
    return entries


def comment_after_segment_ids(story_clips: list) -> dict:
    """Comment2=Part1最終clipの後、Comment3=Part2最終clipの後。"""
    last = {}
    for c in story_clips:
        m = _CLIP_ID_RE.fullmatch(c["id"])
        last[int(m.group(1))] = c["id"]
    return {"2": last[1], "3": last[2]}


def build_z_sequence(narr_dir: str, *, level: str, story_clips: list, kp_items: list, target_rms, gs, gs_already_stereo,
                     intro_gained, notification_gained, outro_gained, kp_third: str = "japanese",
                     story_key: str = "melos") -> list:
    """Z sequence: Intro(Literature導入なし)->Welcome->Topic->(Std: JA title)->Preview->KP->Comment1->
    Story Part1(clips)->Comment2->Part2->Comment3->Part3->Outro(In One Lineなし)。Family Cのbuilderをそのまま利用。"""
    import er013_family_c_production_runner_01 as runner_c
    story_segments = [{"id": c["id"], "audio_path": f"{narr_dir}/{c['id']}.wav",
                       "voice": normalize_speaker(c.get("speaker") or c.get("voice_role") or c.get("voice") or "narrator", story_key)}
                      for c in story_clips]
    third = "explanation_en" if kp_third == "explanation" else "ja"  # 委任_05: Adv=英語解説(Coffee最終v3 Adv構成)
    kp_blocks = [(it["rank"], f"{narr_dir}/kp{it['rank']}_number.wav", f"{narr_dir}/kp{it['rank']}_en.wav",
                  f"{narr_dir}/kp{it['rank']}_{third}.wav") for it in sorted(kp_items, key=lambda x: x["rank"])]
    comment_wavs = {n: f"{narr_dir}/comment_{n}.wav" for n in (1, 2, 3)}
    return runner_c.build_family_c_episode_sequence(
        audio_dir=narr_dir, target_rms=target_rms, gs=gs, gs_already_stereo=gs_already_stereo,
        intro_gained=intro_gained, notification_gained=notification_gained, outro_gained=outro_gained,
        kp_blocks=kp_blocks, story_segments=story_segments, comment_wavs=comment_wavs,
        comment_after_segment_id=comment_after_segment_ids(story_clips), has_japanese_title=(level == "a2"),
        preview_asset_name="preview.wav")


def run_assembly(run_dir: str, level: str, story_clips: list, kp_items: list, *, story_key: str = DEFAULT_SLUG,
                 kp_third: str = "japanese", chunk_plans: dict | None = None) -> dict:
    """gain -> sequence -> assemble_with_timeline -> headroom safety valve -> wav + timeline.json。
    chunk_plans(I6): {親clip_id: chunk plan}(chunk_plans_from_specs(plan))。chunk化した親は、音声を読む前に整合検査(chunk集合・順序・語数・版・本文)と
    『親wav==ディスク上chunk wavの生連結』を確認し、gain適用時に chunk別gain→0.2秒無音→連結へ差し替える(timelineは親1エントリのまま)。"""
    import numpy as np
    import er002_common as common
    import er003_b1_p9a_audio as p9a
    import er003_v1_n3_01_assemble as asm
    level_dir = f"{run_dir}/{level}"
    narr = narration_dir_for(run_dir, level)
    SR = p9a.TARGET_SAMPLE_RATE
    intro = p9a.load_and_resample_to_target(p9a.INTRO_MP3_PATH)
    outro = p9a.load_and_resample_to_target(p9a.OUTRO_MP3_PATH)
    notif = p9a.load_and_resample_to_target(p9a.NOTIFICATION_MP3_PATH)
    gain_report = {}
    chunk_plans = {pid: pl for pid, pl in (chunk_plans or {}).items() if pl.get("chunked")}
    chunk_gain = {}
    if chunk_plans:
        _res = _read_json(f"{level_dir}/audit/tts_generation_results.json")
        _segs = _res.get("segments") or {}
        _text_of = {c["id"]: c["text"] for c in story_clips}
        for pid, pl in chunk_plans.items():
            _ids = chunk_tts.chunk_ids(pl)
            chunk_tts.verify_parent_integrity(pl, _text_of[pid], {i: _segs[i] for i in _ids if i in _segs}, _segs.get(pid))
            chunk_tts.verify_raw_parent(f"{narr}/{pid}.wav", [f"{narr}/{i}.wav" for i in _ids])

    def load_mono(path):
        return common.read_wav_float(path)[0]

    target_rms = (p9a.rms(load_mono(f"{narr}/preview.wav")) + p9a.rms(load_mono(f"{narr}/{story_clips[0]['id']}.wav"))) / 2
    gain_report["target_rms"] = round(float(target_rms), 5)

    def gs(mono, label):
        if label in chunk_plans:
            # chunk別gain(同一target_rms、peak<=0.95、式はp9a.compute_gain_for_target_rmsを引数で共用=I2)→0.2秒無音→連結→既存と同じ48kHz stereo化。
            # 親全体のgainは掛けていないので親keyにgain値を書かない(I7)。
            monos = [load_mono(f"{narr}/{i}.wav") for i in chunk_tts.chunk_ids(chunk_plans[label])]
            composed, rep_ = chunk_tts.compose_gained_parent(monos, target_rms, gain_fn=p9a.compute_gain_for_target_rms,
                                                              rms_fn=p9a.rms, peak_fn=p9a.peak)
            chunk_gain[label] = rep_
            gain_report[label] = {"chunked": True, "note": "親全体のgainは掛けていない。chunk別gain・RMS・peakは chunk_tts を参照"}
            return p9a.mono_24k_to_stereo_target(composed)
        gain = p9a.compute_gain_for_target_rms(mono, target_rms)
        gained = mono * gain
        gain_report[label] = {"gain": round(float(gain), 4), "rms_after": round(p9a.rms(gained), 5), "peak_after": round(p9a.peak(gained), 5)}
        return p9a.mono_24k_to_stereo_target(gained)

    def gs_stereo(data, label):
        gain = p9a.compute_gain_for_target_rms(data, target_rms)
        gained = data * gain
        gain_report[label] = {"gain": round(float(gain), 4), "rms_after": round(p9a.rms(gained), 5), "peak_after": round(p9a.peak(gained), 5)}
        return gained

    intro_g = gs_stereo(intro["samples"], "intro")
    notif_g = gs_stereo(notif["samples"], "notification")
    outro_m = outro["samples"] * p9a.compute_gain_for_target_rms(outro["samples"], p9a.rms(intro_g))
    outro_g = outro_m * asm.OUTRO_EXTRA_GAIN_LINEAR
    seq = build_z_sequence(narr, level=level, story_clips=story_clips, kp_items=kp_items, target_rms=target_rms, gs=gs,
                           gs_already_stereo=gs_stereo, intro_gained=intro_g, notification_gained=notif_g, outro_gained=outro_g,
                           kp_third=kp_third, story_key=story_key)
    res = asm.assemble_with_timeline(seq)
    safety = asm.apply_headroom_safety_valve(res["assembled"], seq)
    os.makedirs(f"{level_dir}/assembly", exist_ok=True)
    wav = f"{level_dir}/assembly/Family_Z_{story_key}_{level}.wav"
    common.write_wav_float(wav, safety["assembled"], SR, 2)
    timeline = {"story_key": story_key, "level": level, "wav": wav, "duration_seconds": res["total_duration_seconds"],
                "timeline": res["timeline"], "headroom": safety["report"], "gain_report": gain_report,
                "sequence_order": [n for n, _ in seq if not n.startswith("_silence_")]}
    if chunk_gain:
        _starts = {e["part"]: e["start_seconds"] for e in res["timeline"]}
        timeline["chunk_tts"] = {"planner_version": chunk_tts.CHUNK_PLANNER_VERSION, "extra_pause_seconds": chunk_tts.EXTRA_PAUSE_SECONDS, "parents": {
            pid: {"chunk_ids": chunk_tts.chunk_ids(chunk_plans[pid]), "words": [c["words"] for c in chunk_plans[pid]["chunks"]],
                  "boundary_kinds": [c["boundary_kind"] for c in chunk_plans[pid]["chunks"]], "part_start_in_episode_s": _starts.get(pid),
                  "gap_offsets_in_part_s": rep_["boundary_offsets_s"],
                  "gap_offsets_in_episode_s": ([[round(_starts[pid] + a, 4), round(_starts[pid] + b, 4)] for a, b in rep_["boundary_offsets_s"]]
                                                if pid in _starts else None),
                  "gains": rep_["gains"], "pre_rms": rep_["pre_rms"], "post_rms": rep_["post_rms"], "peak_after": rep_["peak_after"],
                  "peak_capped": rep_["peak_capped"], "chunk_samples": rep_["chunk_samples"]} for pid, rep_ in chunk_gain.items()}}
    _write_json(f"{level_dir}/assembly/timeline.json", timeline)
    return timeline


# ============================================================
# 10. 試聴ページ生成(user_test/family_z_melos_02/{index,standard,advanced}.html)
#     file:/// 禁止、(A2)/(B1)/B1Bラベル非表示、Key Phrasesは左=英語/右=日本語の2列。
# ============================================================
PAGES_DIR = "user_test/family_z_melos_02"   # 委任_18: runner E2E_PAGES_DIR(委任_17 B2)と一致。run_e2e_02の試聴ページ(melos_01)を上書きしない。一致はtestで固定
_FORBIDDEN_LABEL_RE = re.compile(r"\(A2\)|\(B1\)|B1B")


def _esc(s) -> str:
    import html
    return html.escape("" if s is None else str(s))


def build_listening_page_html(level_label: str, rows: list, kp_rows: list, full_audio_rel: str, duration: float,
                              tts_mode: str = "Standard同期(TTS_EXECUTION_MODE=STANDARD)",
                              warn_section_html: str = "", page_title: str = "走れメロス") -> str:
    """rows=[{part,start,dur,file,voice,style,script,notes[]}]。level_labelは'Standard'/'Advanced'のみ。"""
    trs = []
    for i, r in enumerate(rows):
        notes = "".join(f"<div class='note'>{_esc(n)}</div>" for n in r.get("notes", []))
        trs.append(
            f"<tr id='r{i}'><td class='id'><b>{_esc(r['part'])}</b><br><span class='sec'>{r['start']:.1f}秒〜 ({r['dur']:.1f}秒)</span><br>"
            f"<button class='jump' data-t='{r['start']}'>全編の位置へ</button></td>"
            f"<td class='play'><audio controls preload='none' src='{_esc(r['file'])}'></audio></td>"
            f"<td class='txt'><div class='voice'>Voice: {_esc(r['voice'])} / Style: {_esc(r['style'])}</div>{notes}"
            f"<div class='script'>{_esc(r['script'])}</div></td></tr>")
    kp = "".join(f"<table class='kp'><tr><td>{_esc(a)}</td><td>{_esc(b)}</td></tr></table>" for a, b in kp_rows)
    return (f"<!doctype html><html lang='ja'><head><meta charset='utf-8'><title>{page_title} {level_label} 試聴</title>"
            "<style>body{font-family:sans-serif;max-width:1180px;margin:1em auto;padding:0 1em;line-height:1.5}"
            "table{border-collapse:collapse;width:100%;margin-bottom:1.2em}th,td{border:1px solid #ccc;padding:6px;vertical-align:top;text-align:left}"
            "td.play{min-width:360px}td.play audio{width:100%}.script{background:#f6f6f6;padding:4px;white-space:pre-wrap}"
            ".note{background:#fff8e0;padding:3px;font-size:.85em}.voice{color:#555;font-size:.85em}"
            "table.kp td{width:50%}.combo{background:#eef6ff;padding:10px;border:1px solid #99c}</style></head><body>"
            f"<h1>{page_title} {level_label}</h1><p>TTS方式: {_esc(tts_mode)}</p>"
            f"<div class='combo'><b>{level_label} 通し全編再生</b>({duration:.0f}秒)<br>"
            f"<audio id='main' controls preload='none' src='{_esc(full_audio_rel)}' style='width:100%'></audio></div>"
            f"<h2>Key Phrases</h2>{kp}"
            "<table><thead><tr><th>パート</th><th>音声</th><th>Voice・Style・Script</th></tr></thead><tbody>"
            + "".join(trs) + "</tbody></table>"
            + warn_section_html +
            "<script>document.querySelectorAll('button.jump').forEach(b=>b.onclick=()=>{const a=document.getElementById('main');"
            "a.currentTime=parseFloat(b.dataset.t);a.play();});</script></body></html>")


FIXED_SHELL_TEXT = {"welcome": "Welcome to English Your Way.", "preview_intro": "Here's a quick preview.",
                    "key_phrases_intro": "Here are today's key phrases.", "full_story_intro": "Now, the full story."}
_PART_LABEL = {
    "Welcome (Charon)": "welcome", "Topic intro": "topic_intro_en", "Japanese title": "japanese_title",
    "Preview intro (Charon)": "preview_intro", "Preview": "preview", "Key phrases intro (Charon)": "key_phrases_intro",
    "Full story intro (Charon)": "full_story_intro", "Comment 1": "comment_1", "Comment 2": "comment_2", "Comment 3": "comment_3",
}


def part_to_clip_id(part: str):
    if part in _PART_LABEL:
        return _PART_LABEL[part]
    if _CLIP_ID_RE.fullmatch(part):
        return part
    m = re.fullmatch(r"key_phrase_([0-9]+)", part)
    if m:
        return f"kp{m.group(1)}_en"
    return None


def build_page_rows(run_dir: str, level: str, audio_rel_prefix: str, audio_out_dir: str, write_audio: bool = True,
                    audio_file_prefix: str = "Melos") -> tuple:
    """timeline.json + tts_generation_results.json から試聴ページの行を作り、timelineスライスのmp3を書き出す。
    戻り値=(rows, kp_rows, full_mp3_name, duration)。テキスト未取得のsegmentは『未取得』と明記(推測補完なし)。
    write_audio=False(委任_19): 既存mp3を再利用し一切書き換えない(存在しなければFamilyZAudioStop)。"""
    import soundfile as sf
    level_dir = f"{run_dir}/{level}"
    tl = _read_json(f"{level_dir}/assembly/timeline.json")
    data = _read_json(f"{level_dir}/audit/tts_generation_results.json")
    x, sr = sf.read(tl["wav"], dtype="float32")
    os.makedirs(audio_out_dir, exist_ok=True)
    full_name = f"{audio_file_prefix}_{level}_full.mp3"
    if write_audio:
        sf.write(f"{audio_out_dir}/{full_name}", x, sr, format="MP3")
    elif not os.path.exists(f"{audio_out_dir}/{full_name}"):
        raise FamilyZAudioStop(f"既存mp3再利用モードだが無い: {audio_out_dir}/{full_name}")
    rows, kp_rows = [], []
    for i, e in enumerate(tl["timeline"]):
        part = e["part"]
        if part.startswith("_silence_"):
            continue
        s, d = e["start_seconds"], e["duration_seconds"]
        fn = f"{level}_{len(rows):02d}.mp3"
        if write_audio:
            sf.write(f"{audio_out_dir}/{fn}", x[int(round(s * sr)): int(round((s + d) * sr))], sr, format="MP3")
        elif not os.path.exists(f"{audio_out_dir}/{fn}"):
            raise FamilyZAudioStop(f"既存mp3再利用モードだが無い: {audio_out_dir}/{fn}")
        cid = part_to_clip_id(part)
        entry = _lookup_entry(data, cid) if cid else None
        row = {"part": part, "clip_id": cid, "start": s, "dur": d, "file": f"{audio_rel_prefix}{fn}", "voice": "-", "style": "-",
               "script": "(音楽・通知音。読み上げなし)" if part.startswith(("Intro", "Outro", "Notification")) else "未取得", "notes": []}
        if entry:
            row["voice"] = entry.get("voice", "-")
            row["style"] = (entry.get("style") or {}).get("instruction_label", "-")
            row["script"] = entry.get("canonical_text") or FIXED_SHELL_TEXT.get(cid, "未取得")
            if entry.get("slowdown_applied"):
                _tempo = (entry.get("speed_profile") or {}).get("tempo")
                _label = "約6%高速化" if (_tempo or 0) > 1.0 else "6%減速"
                row["notes"].append(f"{_label}適用(比 {entry.get('slowdown_ratio')})" if entry.get("slowdown_ratio") else f"{_label}適用")
            if entry.get("audio_text_deviation"):
                row["notes"].append("Local Rewrite採用(音声は原稿から変更: " + entry["audio_text_deviation"].get("diff_summary", "") + ")")
            for _dc in (entry.get("chunk_tts") or {}).get("deviation_chunks") or []:   # I7: chunkのLocal Rewrite注記も親行に出す
                _dv = ((data.get("segments") or {}).get(_dc) or {}).get("audio_text_deviation") or {}
                row["notes"].append(f"Local Rewrite採用({_dc}: 音声は原稿から変更: " + _dv.get("diff_summary", "") + ")")
        if part.startswith("key_phrase_"):
            n = part.split("_")[-1]
            kp = (data.get("key_phrases") or {}).get(n) or {}
            en = (kp.get("english") or {}).get("canonical_text", "未取得")
            ja = (kp.get("japanese_meaning") or kp.get("explanation") or {}).get("canonical_text", "未取得")
            kp_rows.append((en, ja))
            row["script"] = f"{en} / {ja}"
            row["voice"] = "Aoede(KP) / Charon(番号)"
            row["style"] = "K2 / P7" if kp.get("explanation") else "K2 / P8-KP"   # KP英語=K2、第2要素=Adv英語解説P7 / Std日本語意味P8-KP(委任_15)
        rows.append(row)
    return rows, kp_rows, full_name, tl["duration_seconds"]


_SFX_PART_PREFIX = ("Intro", "Outro", "Notification")
_USER_LABEL = {"Welcome (Charon)": "Welcome", "Preview intro (Charon)": "Preview intro",
               "Key phrases intro (Charon)": "Key phrases intro", "Full story intro (Charon)": "Full story intro"}


def _user_page_rows(run_dir: str, level: str, rows: list, kp_rows: list, audio_rel_prefix: str, audio_out_dir: str) -> list:
    """標準フォーマット(er_user_listening_page_common_01)用の行へ変換する(委任_19)。
    効果音行(Intro/Outro/Notification)は除外、Full Storyのclip(full_story_partN_cK)はPart単位に束ねて再生順のscriptを列挙、
    内部情報(Voice/Style/6%減速等)は載せない。Part束ね用mp3は assembled wav からの無料ローカル切り出し(新規ファイルのみ、既存mp3は不変)。"""
    import soundfile as sf
    import er_user_listening_page_common_01 as uc
    tl = _read_json(f"{run_dir}/{level}/assembly/timeline.json")
    x = sr = None
    kw = {}
    kp_path = f"{run_dir}/key_phrases/{level}/keywords_canonicalized.json"
    if os.path.exists(kp_path):
        kw = {int(it["rank"]): it for it in _read_json(kp_path).get("items", [])}
    data = _read_json(f"{run_dir}/{level}/audit/tts_generation_results.json")
    out, i = [], 0
    while i < len(rows):
        r = rows[i]
        part = r["part"]
        if part.startswith(_SFX_PART_PREFIX):
            i += 1
            continue
        m = re.fullmatch(r"full_story_part(\d+)_c\d+", part)
        if m:
            n = m.group(1)
            j = i
            while j < len(rows) and re.fullmatch(rf"full_story_part{n}_c\d+", rows[j]["part"]):
                j += 1
            grp = rows[i:j]
            start, end = grp[0]["start"], grp[-1]["start"] + grp[-1]["dur"]
            fn = f"{level}_p{n}.mp3"
            if x is None:
                x, sr = sf.read(tl["wav"], dtype="float32")
            sf.write(f"{audio_out_dir}/{fn}", x[int(round(start * sr)): int(round(end * sr))], sr, format="MP3")
            voices = []
            for g in grp:
                for v in str(g.get("voice") or "").split(" / "):
                    if v and v != "-" and v not in voices:
                        voices.append(v)
            out.append({"part": f"Full Story Part {n}" + (f" ({' / '.join(voices)})" if voices else ""), "start": start, "dur": end - start, "src": f"{audio_rel_prefix}{fn}",
                        "blocks": [uc.script_block(g["script"]) for g in grp]})
            i = j
            continue
        m = re.fullmatch(r"key_phrase_(\d+)", part)
        if m:
            n = int(m.group(1))
            kp = (data.get("key_phrases") or {}).get(str(n)) or {}
            en = (kp.get("english") or {}).get("canonical_text", "未取得")
            if level == "b1b":
                expl = (kp.get("explanation") or {}).get("canonical_text", "未取得")
                gloss = (kw.get(n) or {}).get("japanese_gloss") or ""
                heads, cells = (["英語", "日本語の意味", "英語での説明"], [en, gloss, expl]) if gloss else (["英語", "英語での説明"], [en, expl])
            else:
                # KP-CONFIRMED-CONTENT-PROTECTION-01 02B M2-b: Stdページの「日本語の意味」はユーザーが確定した表示用japanese_gloss
                # (CURRENT_SPEC:458-469 表示用/TTS用分離)。TTS用canonical_text(「～」→「なになに」等)は表示しない。TTS入力は不変。
                ja = (kw.get(n) or {}).get("japanese_gloss") or (kp.get("japanese_meaning") or {}).get("canonical_text", "未取得")
                heads, cells = ["英語", "日本語の意味"], [en, ja]
            out.append({"part": f"Key Phrase {n}", "start": r["start"], "dur": r["dur"], "src": r["file"],
                        "blocks": [uc.kp_block(heads, cells)]})
            i += 1
            continue
        base = _USER_LABEL.get(part, part)
        voice = r.get("voice")
        if voice and voice != "-" and "(" not in base:   # Gate 7 (h): 使用voice名はラベルに併記(scriptには入れない)
            base = f"{base} ({voice})"
        out.append({"part": base, "start": r["start"], "dur": r["dur"], "src": r["file"],
                    "blocks": [uc.script_block(r["script"])]})
        i += 1
    return out


def build_pages(run_dir: str, pages_dir: str = PAGES_DIR, reuse_existing_audio: bool = False, *,
                page_title: str = "走れメロス", audio_file_prefix: str = "Melos", study_html: str = "") -> dict:
    """user_test/family_z_melos_02/{index,standard,advanced}.html を生成する(静的ファイルのみ)。
    index.html=ユーザー試聴ページ標準フォーマット(Std/Adv 1ページ、通し再生・再生順スクリプト・KP、ASR警告は補助表示。委任_19、
    er_user_listening_page_common_01)。standard.html/advanced.html=Voice/Style付き詳細確認ページ(開発確認用、従来形式)。
    reuse_existing_audio=True: 既存mp3(per-clip/通し全編)を書き換えず再利用(Part束ね用の新規mp3のみ追加)。"""
    import er_user_listening_page_common_01 as uc
    os.makedirs(pages_dir, exist_ok=True)
    out = {}
    warn_sections = []
    user_levels = []
    for level, fname, label in (("a2", "standard.html", "Standard"), ("b1b", "advanced.html", "Advanced")):
        audio_dir = f"{pages_dir}/audio_{label.lower()}"
        rows, kp_rows, full, dur = build_page_rows(run_dir, level, f"audio_{label.lower()}/", audio_dir,
                                                   write_audio=not reuse_existing_audio, audio_file_prefix=audio_file_prefix)
        # AUW 委任_03: 事後試聴リスト(PASS_WITH_WARNING)節(0件でも節を出す)。mp3リンクは当該partの試聴ページ内mp3。
        import er078_pass_with_warning_registry_01 as _pww
        warn_entries = _pww.load_listening_list(f"{run_dir}/{level}")
        clip_to_file = {r.get("clip_id"): r["file"] for r in rows if r.get("clip_id")}
        warn_html = _pww.render_html_section(
            warn_entries, href_fn=lambda e: clip_to_file.get(_warn_entry_to_clip_id(e.get("entry_key", "")), ""))
        warn_sections.append((label, warn_html))
        html_text = build_listening_page_html(label, rows, kp_rows, f"audio_{label.lower()}/{full}", dur,
                                              warn_section_html=warn_html, page_title=page_title)
        lint = lint_page_html(html_text)
        if any(lint.values()):
            raise FamilyZAudioStop(f"試聴ページlint NG ({label}): {lint}")
        with open(f"{pages_dir}/{fname}", "w", encoding="utf-8") as f:
            f.write(html_text)
        user_levels.append({"id": "std" if label == "Standard" else "adv", "label": label, "full_src": f"audio_{label.lower()}/{full}", "duration": dur,
                            "rows": _user_page_rows(run_dir, level, rows, kp_rows, f"audio_{label.lower()}/", audio_dir),
                            # 委任_14: 学習テキストPart 1(Advancedのみ。未指定=従来とバイト同一)
                            **({"study_html": study_html} if (study_html and label == "Advanced") else {})})
        out[label] = {"page": f"{pages_dir}/{fname}", "rows": len(rows), "kp_rows": len(kp_rows), "lint": lint}
    index_html = build_index_html(user_levels, warn_sections, page_title=page_title)
    lint = lint_page_html(index_html)
    chk = uc.check_page(index_html, base_dir=pages_dir)
    if any(lint.values()) or chk["overall"] != "PASS":
        bad = {k: v for k, v in chk["checks"].items() if not v["ok"]}
        raise FamilyZAudioStop(f"ユーザー試聴ページ標準適合NG(index.html): lint={lint} check={bad}")
    with open(f"{pages_dir}/index.html", "w", encoding="utf-8") as f:
        f.write(index_html)
    out["index"] = {"page": f"{pages_dir}/index.html", "standard_check": chk["overall"], "lint": lint}
    return out


def _warn_entry_to_clip_id(entry_key: str):
    """事後試聴リストのentry_key(tts_generation_results.json内のpath)をtimeline rowのclip_idへ対応づける。
    対応するrow(mp3)が無いものはNone(リンクなし表示)。"""
    parts = entry_key.split("/")
    if len(parts) == 2 and parts[0] == "segments":
        m = re.fullmatch(r"(full_story_part[1-3]_c[0-9]+)_k[1-9][0-9]*", parts[1])   # R3: chunkの警告は親clip行へ対応づける
        return m.group(1) if m else parts[1]
    if len(parts) == 3 and parts[0] == "key_phrases" and parts[2] == "english":
        return f"kp{parts[1]}_en"
    return None


def build_index_html(user_levels: list, warn_sections=None, page_title: str = "走れメロス") -> str:
    """ユーザー試聴ページ(標準フォーマット)。warn_sections=[(level_label, section_html)]: AUW 委任_03の『事後試聴リスト』節は
    補助表示(全レベル節の後ろ、折りたたみ)へ置く。standard.html/advanced.htmlは開発確認用の詳細ページとして補助表示から案内。"""
    import er_user_listening_page_common_01 as uc
    warn = "".join(f"<h3>{_esc(lbl)}</h3>{sec_html}" for lbl, sec_html in (warn_sections or []))
    aux = ("<h2 id='aux'>補助情報(試聴の邪魔にならない確認用)</h2>"
           "<details class='aux'><summary>ASR警告(PASS_WITH_WARNING)の事後試聴リスト(参考情報。公開をブロックしません)</summary>"
           f"{warn}</details>"
           "<details class='aux'><summary>詳細確認ページ(開発確認用)</summary>"
           "<a href='standard.html'>Standard 詳細</a> / <a href='advanced.html'>Advanced 詳細</a></details>")
    intro = ("<div class='note'>各レベルの「全編を通し再生」ボタンで冒頭から最後まで通して聴けます。下の表は再生順のスクリプトで、"
             "「全編のこの位置へ」で通し再生をその位置から再生します。冒頭・区切り・末尾の音楽/通知音は読み上げなし(通し再生には含まれます)。"
             "TTS方式: Standard同期(TTS_EXECUTION_MODE=STANDARD)。</div>")
    return uc.render_standard_page(f"{page_title} 試聴(Standard / Advanced)", user_levels, intro_html=intro, aux_html=aux)


def lint_page_html(html_text: str) -> dict:
    return {"file_scheme": ("file:///" in html_text or "C:\\" in html_text or "C:/" in html_text),
            "level_label_leak": bool(_FORBIDDEN_LABEL_RE.search(re.sub(r"<[^>]+>", " ", html_text))),
            "kp_label_leak": bool(re.search(r"English:|英語:|EN:|日本語:|JA:", re.sub(r"<[^>]+>", " ", html_text)))}


# ============================================================
# 11. CLI(dry-runは副作用ゼロ)
# ============================================================
def main() -> None:
    import er_secret_mask_01 as _sm; _sm.install_stream_masking()   # GIT-SECRET-REPAIR-01
    ap = argparse.ArgumentParser(description="Family Z Audio (04C)。実TTSはE2E委任で実施。")
    ap.add_argument("--check", action="store_true", help="Style表sha・Melos Voice機構の自己確認のみ")
    args = ap.parse_args()
    if args.check:
        print(json.dumps({"style_sha": assert_style_table_integrity(), "melos": check_melos_voice_mechanism()},
                         ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
