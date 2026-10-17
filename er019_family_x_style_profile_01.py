# ============================================================
# er019_family_x_style_profile_01.py
# FAMILY-X-COFFEE-P8-FINAL-AUDIO-AND-PRODUCTION-WIRING-01 委任_02
# (OPEN-300、設計書 docs/pm/design/2026-10-12_COFFEE-P8-PRODUCTION-WIRING-DESIGN-02.md)
# ============================================================
# 目的: Coffee Full Story限定のStyle置換(P8、ユーザー決定2026-10-12、
# APPROVED_FOR_PRODUCTION[Coffee限定]、Production未配線=PRODUCTION_WIRED未達)を、
# Family X runner(er019_family_x_audio_production_runner_01.py)へ
# 「明示CLI --style-profile + out_dir固定記録」で配線するための副作用の少ない
# 定数+純関数module。runnerからのみimportされる(Dangling Reference Check)。
#
# 重要な不変条件:
#   - "default" profileは現行とバイト同一(resolve_role_style は base_getter を素通し)。
#     defaultでは新しいkey/fileを一切書かない(S3)。
#   - 共有module(er003/er006/er011/er033定数/Master Store)は一切変更しない。
#   - Phase 1 = Coffee Full Story(FULL_STORY role)のみ。他Role(K2/M2/A5/B5/E1/R2等)は
#     後続Phase(OPEN申し送り、設計書S5)。
#   - OPEN-298(全記事共通Style展開)・OPEN-299(In One Line 2文方針)は範囲外。
#
# S1(Coffee限定の決定ID付き例外 COFFEE-P8-STD-VERBATIM-EXCEPTION-01、
# DECISION_LOG 2026-10-12): Standard(A2)のFull Storyは、通常の
# `er003_v1_n3_01_tts_generate.py`説明文(「A2_ENGLISH_STYLE_PREFIX_SLOWER[自然言語の
# 『わずかに遅く』instruction]を渡し、instruction+6% time-stretchの承認済み組合せを
# 正確に再現すること」)および現行runnerの`_role_style_slower`(6-role短style+
# A2_SLOWER_PACE_INSTRUCTIONを連結)とは異なり、**P8逐語(減速指示を連結しない)+
# 生成後6%減速(post-process自体は共有module側で無変更)**とする。根拠: Coffee v3 Std は
# P8(旧PD8)逐語+6%減速でユーザーが試聴・承認した組合せである。この例外はCoffee
# profile("coffee_p8")限定であり、defaultのStandard仕様・他記事・共有moduleは不変。
# テスト(er019_family_x_style_profile_01_test_01.py)で固定する。
# ============================================================
from __future__ import annotations

import hashlib
import json
import os
import time

DESIGN_ID = "COFFEE-P8-PRODUCTION-WIRING-DESIGN-02"
# FAMILY-X-COFFEE-FINAL-V5-PRODUCTION-WIRING-01 委任_01(2026-10-12、ユーザー正式決定B/C):
# profile "coffee_final_v5" = coffee_p8(Full Story=P8) + Std Preview/Comment1〜4=R2 + Adv KP英英解説=P3。
# 全てCoffee限定(他記事/他Familyへ横展開しない)。既存機構(resolve_role_style/記録/M2/M3/M4/M5)を
# roleごとに拡張しただけで、新しい構造ではない。
V5_DESIGN_ID = "FAMILY-X-COFFEE-FINAL-V5-PRODUCTION-WIRING-01"
STD_VERBATIM_EXCEPTION_ID = "COFFEE-P8-STD-VERBATIM-EXCEPTION-01"

# P8原文(逐語): er057_output/aoede_style_trial_03/prompts/prompts_aoede_style_03.md の
# "## P8" 節コードブロック。402文字。数値WPM・速度倍率は含まない。
P8_TEXT = (
    "Warm, bright, cozy storytelling in the manner of a well-loved radio feature: unhurried, "
    "richly expressive, with full vowels and gentle emphasis, never flat or sleepy. "
    "Let the pitch rise and fall a little more on key words. "
    "Add a touch more brightness and a hint of a smile in the voice, while staying unhurried. "
    "Articulate crisply: distinct consonants, clean word endings, every syllable clearly heard."
)
P8_SHA256 = "3eadf4f6f788b822c90f17ba56d893bccb5fab840358cf48845472cd4f4e5595"
P8_LENGTH = 402

# R2原文(逐語、Standard日本語Aoede Style Trial-02、ユーザー承認済み 2026-10-12): 168文字。
# 出典: er057_output/ja_aoede_style_trial_02/prompts/prompts_R.md "## R2" 節コードブロック。
R2_TEXT = (
    "明るく、温かみのある話し方で。身近な人にちょっとした話題を教えてあげるように、"
    "自然な抑揚と軽やかなリズムをつけてください。ニュース番組としての明瞭さは保ち、"
    "演技がかった話し方は避けてください。句読点の記号そのものに反応して声の高さを変えないでください。"
    "読点は短い息継ぎの間、句点はやや長めの間として、音程は変えずに自然に置いてください。"
)
R2_SHA256 = "625826c1187b6381fe36ff444f1f568fc1f68d639d6a6a8931e728463692252f"
R2_LENGTH = 168

# P3原文(逐語、Adv KP英英解説Style Trial-01、ユーザー正式選択済み 2026-10-12): 141文字。
# = 現行P0(KEY_PHRASE_EXPLANATION_EN)+半角空白1つ+差分句(P3)。
# 出典: er057_output/kp_en_explanation_style_trial_01/prompts/prompts_kp_en_explanation_style_01.md "## P3" 節。
P3_TEXT = (
    "clear, precise, at a measured pace, without dragging "
    "Let the sentence flow from its first word to its last, without stopping partway through."
)
P3_SHA256 = "a8aaec591ef6d9acb42532cc0c84b6edfb2f75991e713d413c565b7e27677acc"
P3_LENGTH = 141

# N01原文(逐語、FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01、ユーザー正式決定2026-10-13: メイン音声Prompt=N01
# APPROVED_FOR_PRODUCTION、Family X/Z)。202文字・37語・2文。数値WPM・速度倍率・unhurried/slowly・位置語を含まない。
# 出典: er057_output/coffee_tts_style_h_speed_04/round5/prompts_r5.json candidates.N01.style。
# Std/Adv共通に同一文言。Stdも逐語(減速instruction非連結)+生成後6%減速(共有module側、無変更)。
# 対象はFull Story narration(Std/Adv part1-3)のみ。"sharing a true story"の意味ズレ(Fiction=Family Z)は
# USER_DECISION_REQUIRED N-2(文言は変更しない)。
N01_TEXT = (
    "A cheerful, kind storyteller sharing a true story at a pace a little slower than usual. "
    "Bring each sentence to its natural close, then go directly on to the next, including where the story takes a turn."
)
N01_SHA256 = "d1956c91c925d197e27cf1204d7ed17248a96bef096b082fb1bd0846106a0477"
N01_LENGTH = 202

# E1原文(逐語、Adv Preview[英語・Charon] Style Trial、ユーザー承認済み。正本: er057_tone_trial_tts_gen_01.py
# SPECS["E"]["E1"][2]、CURRENT_SPEC「E1」承認sha先頭8862317ff766)。68文字。数値WPM・速度倍率を含まない。
# FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01 委任_03(OF-Y8): Adv Preview(b1b "preview" segmentのみ)へ配線。
E1_TEXT = "calm, composed news anchor; steady and unhurried, clear and natural."
E1_SHA256 = "8862317ff76693ff519ddfa956260a8cce2d540763333b54096b63161d84f641"
E1_LENGTH = 68

# ------------------------------------------------------------
# FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01 委任_02A(2026-10-16、ユーザー正式承認済み6仕様の既定化)
# 新既定profile "fx_20261016" 用の4定数。全て承認済み正本からの逐語コピー(定数とsha/長さは_verify_constantsがimport時に検証、
# さらにソース突合testが正本ファイルと逐語比較する)。数値WPM・速度倍率を含まない。
# ------------------------------------------------------------
# PD06(Full Story narration[Std/Adv part1-3]、ユーザー承認済み): 177文字。
# 正本: er057_output/pace_trial_02/prompts/prompts_pace_02.md "## PD6" 節コードブロック。
# Stdも逐語(A2減速instruction非連結、std_append_slower_instruction=False)+生成後6%減速(共有module側、既存維持)。
PD06_TEXT = (
    "Speak directly to one listener with warmth and a smile in your voice; calm, steady and reassuring, "
    "like a favorite morning radio host, while keeping the news clear and credible."
)
PD06_SHA256 = "3a680861e4d9d1bc46ddba4dc1fc91f26c68f9f9c5e5e450a85fcba7fda43c2d"
PD06_LENGTH = 177

# P7(Adv KP英語解説音声、#96判断済み・ユーザー承認): 136文字。正本: er080_coffee_kp_pacing_trial_01.py:35 "p7"。
# 旧P3(Coffee限定profile用)とは別定数・別sha(P3は不変)。
P7_TEXT = (
    "Speak clearly at a slightly relaxed, natural pace. Keep a steady rhythm, with brief transitions "
    "between phrases and no drawn-out pauses."
)
P7_SHA256 = "0518000694e31ef7de6602401b7fa9abd3beb45654e95714817930582020b9fc"
P7_LENGTH = 136

# K2(KP英語音声[Std/Adv]、ユーザー承認済み): 332文字 = K2文 + 共通guard(B_GUARD)。
# 正本: er057_tone_trial_kp_ja_gen_01.py:38-39 B_SPECS["K2"] + :33 B_GUARD。Family Z `_K2`(er063:120)と同一。
K2_TEXT = (
    "Say the phrase as one single, smoothly connected chunk of meaning, as if the words belong together and "
    "are not read one by one. Keep the pitch movement small and continuous across the whole phrase. Say only "
    "this phrase, exactly once, without adding, omitting, or changing any words, and make sure the final "
    "sound is actually spoken."
)
K2_SHA256 = "9d905cfe6c040cd001c4e7877327044f540a72bd315776f2c297e0f58f7aea42"
K2_LENGTH = 332

# P8-KP(Std KP日本語意味、ユーザー承認済み): 93文字。正本: er057_std_kp_ja_style_trial_02.py:25 PROMPTS["P8"]。
# 注意: 既存の`P8_TEXT`(上、402文字)は「Full Story旧候補P8」(Aoede Trial-03、coffee_p8/coffee_final_v5の固定記録が参照)で
# 全く別物。本定数は別名`P8_KP_JA_TEXT`・別role`KP_JA_MEANING`で明確に分離する(同名P8の混同防止、ユーザー指示§4)。
P8_KP_JA_TEXT = (
    "落ち着いたニュースキャスターのように、明瞭で安定した声で読み上げてください。自然な抑揚を保ちながら、"
    "短い言葉の意味を端的に伝えてください。大げさな強調や演技的な感情表現は避けてください。"
)
P8_KP_JA_SHA256 = "b12c8721eab8434b78d129c93491c0a826f229f4528e024d58de960e1ad191e7"
P8_KP_JA_LENGTH = 93

# ------------------------------------------------------------
# FAMILY-X-STD-JA-S3-ADOPTION-AND-WIRING-01 Phase B 委任_03(2026-10-17、ユーザー正式承認 APPROVED_FOR_PRODUCTION):
# S3「親しみのあるニュースナレーター」を Family X全体のStandard日本語解説(Preview/Comment1〜4 = role SUPPORT_JA)の
# 正式Styleとして採用(旧: R2)。共通指示込みStyle全文(199字、sha 060c08fd…)。逐語コピー(調整禁止)。
# 正本: er057_output/ja_support_calm_style_trial_04/PROMPTS_01.md "## S3" 節コードブロック(Trial-04、共通指示84字込み)。
# 定数とsha/長さは_verify_constantsがimport時に検証し、ソース突合testが正本ファイルと逐語比較する。
# ------------------------------------------------------------
SUPPORT_JA_STYLE_S3_20261017 = (
    "温かみと親しみのあるニュースナレーターとして、落ち着いた、明瞭な声で伝えてください。"
    "声の調子は安定させ、重要な言葉や対比にだけ控えめな抑揚をつけてください。"
    "文末は軽く下げて自然に収め、聞き手が内容を追いやすい流れで読んでください。"
    "句読点は自然な間として扱い、記号だけを理由に声の高さを変えないでください。"
    "問いかけは穏やかに読み、語尾を大きく跳ね上げないでください。"
    "演技がかった強調は避けてください。"
)
SUPPORT_JA_STYLE_S3_SHA256 = "060c08fde003cf7c2d15c654da96d3f857b8e7a9bd79eac31814ceaf7c923f33"
SUPPORT_JA_STYLE_S3_LENGTH = 199

# Master Audio Store上のKP英語(K2)keyの識別子(旧`key_phrase_english_component`[MINIMAL style]とは別id)。
# keyの`style_instruction_version`は"{trim_policy}+k2.{K2 sha12}"(primary)/"{trim_policy}+lock.{ENGLISH_LOCK sha12}"(fallback)、
# `instruction_path`は"primary"/"english_lock_fallback"。M3はこのkeyでK2由来音声かどうかを判定する。
KP_EN_STORE_STYLE_ID = "key_phrase_english_component_k2"
KP_EN_STORE_PATH_PRIMARY = "primary"
KP_EN_STORE_PATH_FALLBACK = "english_lock_fallback"

PROFILE_DEFAULT = "default"
# 非推奨(2026-10-16以降、新規runの既定はfx_20261016): 以下の旧profileは既存out_dirの固定記録検証(resume)のため残置する。
PROFILE_COFFEE_P8 = "coffee_p8"
PROFILE_COFFEE_FINAL_V5 = "coffee_final_v5"
# FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01: N01(Full Story)。新規out_dir(記録なし・CLI指定なし・run stateなし)の
# 既定profile(必須5 B': FAMILY_X_ROLE_STYLE_EN定数は書き換えず、既存のprofile機構[sha検証・固定記録・M2/M5/M3 Gate]を使う)。
PROFILE_N01 = "n01"
# Coffee用結合profile: Full Story=N01 + Std Preview/Comment1〜4=R2 + Adv KP英英解説=P3(必須6、明示CLI指定専用)。
PROFILE_COFFEE_N01_R2_P3 = "coffee_n01_r2_p3"
# 委任_03(OF-Y8): coffee_n01_r2_p3 + Adv Preview=E1。既存profileは不変(上位集合として新設)。
PROFILE_COFFEE_N01_R2_P3_E1 = "coffee_n01_r2_p3_e1"
# `resolve_run_profile`が「記録なし・CLI指定なし・run stateなし」の新規out_dirへ解決するprofile。
# 委任_02A(2026-10-16): 新規run既定をfx_20261016へ切替(ユーザー指示§4「6仕様をFamily Xの既定profileとして適用する。
# CLIによる特別指定を忘れた場合でも、承認済みStyleが自動適用されるようにする」)。
PROFILE_FX_20261016 = "fx_20261016"
# 委任_03 Phase B(2026-10-17、ユーザー正式承認): 新規run既定をfx_20261017へ切替。fx_20261016からの差分はSUPPORT_JAのR2→S3のみ。
# fx_20261016は既存out_dir(固定記録がfx_20261016のrun)のresume互換のためだけに残置する(新規runの既定ではない)。
PROFILE_FX_20261017 = "fx_20261017"
DEFAULT_NEW_RUN_PROFILE = PROFILE_FX_20261017

# role名(Std JA Preview/Comment1〜4、Adv KP英英解説)
ROLE_SUPPORT_JA = "SUPPORT_JA"
ROLE_KP_EXPLANATION_EN = "KP_EXPLANATION_EN"
ROLE_PREVIEW = "PREVIEW"  # Adv(b1b)のPreview(英語)のみ。Comment 1〜4は対象外(Style正本は未決)。
# 委任_02A: KP音声のrole(segmentでなくkey_phrases[rank]配下)。KP_JA_MEANINGは旧Full Story候補P8とは別role/別定数。
ROLE_KP_EN = "KP_EN"                  # KP英語音声(Std/Adv)。Master Audio Store keyで識別(K2 2段key)。
ROLE_KP_JA_MEANING = "KP_JA_MEANING"  # Std KP日本語意味(P8-KP)。
# roleごとのkey_phrases[rank]内の結果キー。
ROLE_KP_RESULT_KEY = {ROLE_KP_EN: "english", ROLE_KP_JA_MEANING: "japanese_meaning", ROLE_KP_EXPLANATION_EN: "explanation"}

# 上書き対象role -> そのroleに対応するsegment名(runner側のsegment名)。
ROLE_SEGMENTS = {
    "FULL_STORY": ("full_story_part1", "full_story_part2", "full_story_part3"),
    # Std(a2)のみ。japanese_title・Key Phrase日本語意味・IN_ONE_LINEは対象外。
    ROLE_SUPPORT_JA: ("preview", "comment_1", "comment_2", "comment_3", "comment_4"),
    ROLE_PREVIEW: ("preview",),
}
# roleが適用されるlevel("a2"=Standard、"b1b"=Advanced)。levelが対象外ならbase_getterを素通し。
ROLE_LEVELS = {
    "FULL_STORY": ("a2", "b1b"),
    ROLE_SUPPORT_JA: ("a2",),
    ROLE_KP_EXPLANATION_EN: ("b1b",),
    ROLE_PREVIEW: ("b1b",),
    ROLE_KP_EN: ("a2", "b1b"),
    ROLE_KP_JA_MEANING: ("a2",),
}

_FULL_STORY_OVERRIDE = {
    "text": P8_TEXT, "sha256": P8_SHA256,
    # S1: Standardは逐語(減速指示非連結)+生成後6%減速(共有module側)。
    "std_append_slower_instruction": False,
}

_FULL_STORY_OVERRIDE_N01 = {
    "text": N01_TEXT, "sha256": N01_SHA256,
    # Std/Advとも逐語(減速指示非連結)+生成後6%減速(共有module側、無変更)。S1のStd逐語例外をN01でも踏襲。
    "std_append_slower_instruction": False,
}

STYLE_PROFILES = {
    PROFILE_DEFAULT: {"overrides": {}},
    PROFILE_COFFEE_P8: {
        "overrides": {"FULL_STORY": dict(_FULL_STORY_OVERRIDE)},
    },
    # V5: P8(Full Story) + R2(Std Preview/Comment1〜4) + P3(Adv KP英英解説)。Coffee限定。
    PROFILE_COFFEE_FINAL_V5: {
        "overrides": {
            "FULL_STORY": dict(_FULL_STORY_OVERRIDE),
            ROLE_SUPPORT_JA: {"text": R2_TEXT, "sha256": R2_SHA256},
            ROLE_KP_EXPLANATION_EN: {"text": P3_TEXT, "sha256": P3_SHA256},
        },
    },
    PROFILE_N01: {"overrides": {"FULL_STORY": dict(_FULL_STORY_OVERRIDE_N01)}},
    # N01(Full Story) + R2(Std Preview/Comment1〜4) + P3(Adv KP英英解説)。Coffee(明示CLI)用。
    PROFILE_COFFEE_N01_R2_P3: {
        "overrides": {
            "FULL_STORY": dict(_FULL_STORY_OVERRIDE_N01),
            ROLE_SUPPORT_JA: {"text": R2_TEXT, "sha256": R2_SHA256},
            ROLE_KP_EXPLANATION_EN: {"text": P3_TEXT, "sha256": P3_SHA256},
        },
    },
    # N01(Full Story) + R2(Std) + P3(Adv KP英英解説) + E1(Adv Preview)。Coffee(明示CLI)用。
    PROFILE_COFFEE_N01_R2_P3_E1: {
        "overrides": {
            "FULL_STORY": dict(_FULL_STORY_OVERRIDE_N01),
            ROLE_SUPPORT_JA: {"text": R2_TEXT, "sha256": R2_SHA256},
            ROLE_KP_EXPLANATION_EN: {"text": P3_TEXT, "sha256": P3_SHA256},
            ROLE_PREVIEW: {"text": E1_TEXT, "sha256": E1_SHA256},
        },
    },
}

# 委任_02A: 新既定profile。Full Story=PD06 + Std Preview/Comment1〜4=R2 + Adv Preview=E1 + Adv KP英語解説=P7 + KP英語=K2 + Std KP日本語意味=P8-KP。
# (FAMILY_X_VARIABLE_ROLE_STYLE_VERSIONはbumpしない[R-12]: 旧profileのcache-version guardを変えず、新profileの区別は
#  style_profile.json固定記録[M2/M3]とMaster Audio Store key[K2 id/version]で行うため。)
STYLE_PROFILES[PROFILE_FX_20261016] = {
    "overrides": {
        "FULL_STORY": {"text": PD06_TEXT, "sha256": PD06_SHA256, "std_append_slower_instruction": False},
        ROLE_SUPPORT_JA: {"text": R2_TEXT, "sha256": R2_SHA256},
        ROLE_PREVIEW: {"text": E1_TEXT, "sha256": E1_SHA256},
        ROLE_KP_EXPLANATION_EN: {"text": P7_TEXT, "sha256": P7_SHA256},
        ROLE_KP_EN: {"text": K2_TEXT, "sha256": K2_SHA256},
        ROLE_KP_JA_MEANING: {"text": P8_KP_JA_TEXT, "sha256": P8_KP_JA_SHA256},
    },
}

# 委任_03 Phase B: 新既定profile fx_20261017 = fx_20261016(FULL_STORY/PREVIEW/KP_EXPLANATION_EN/KP_EN/KP_JA_MEANINGは同一sha)
# + SUPPORT_JAのみS3(R2を置換)。overrideのrole集合はfx_20261016と同一。
STYLE_PROFILES[PROFILE_FX_20261017] = {
    "overrides": {
        **{role: dict(o) for role, o in STYLE_PROFILES[PROFILE_FX_20261016]["overrides"].items() if role != ROLE_SUPPORT_JA},
        ROLE_SUPPORT_JA: {"text": SUPPORT_JA_STYLE_S3_20261017, "sha256": SUPPORT_JA_STYLE_S3_SHA256},
    },
}

# roleごとのlevel情報を記録へ含めるprofile(V5以降の複数role profile)。
_PROFILES_RECORDING_LEVELS = (PROFILE_COFFEE_FINAL_V5, PROFILE_COFFEE_N01_R2_P3, PROFILE_COFFEE_N01_R2_P3_E1,
                              PROFILE_FX_20261016, PROFILE_FX_20261017)

PROFILE_RECORD_RELPATH = "audit/style_profile.json"
APPROVED_BACKEND = "speech_metadata_flash_lite"

# M2: これらのうち1つでも存在するout_dirでは、新規にprofile記録を作れない
# (Review Lock/人間承認はtext shaのみで照合され、Styleを区別しないため)。
_RUN_STATE_FILES = ("tts_generation_results.json", "review_lock_state.json", "human_approved_segments.json")


class StyleProfileStop(RuntimeError):
    """USER_DECISION_REQUIRED相当のSTOP(課金前に止める)。"""


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _verify_constants() -> None:
    import er002_common as common
    for label, text, sha, length in (("P8", P8_TEXT, P8_SHA256, P8_LENGTH), ("R2", R2_TEXT, R2_SHA256, R2_LENGTH),
                                     ("P3", P3_TEXT, P3_SHA256, P3_LENGTH), ("N01", N01_TEXT, N01_SHA256, N01_LENGTH),
                                     ("E1", E1_TEXT, E1_SHA256, E1_LENGTH),
                                     ("PD06", PD06_TEXT, PD06_SHA256, PD06_LENGTH), ("P7", P7_TEXT, P7_SHA256, P7_LENGTH),
                                     ("K2", K2_TEXT, K2_SHA256, K2_LENGTH),
                                     ("P8_KP_JA", P8_KP_JA_TEXT, P8_KP_JA_SHA256, P8_KP_JA_LENGTH),
                                     ("S3_SUPPORT_JA", SUPPORT_JA_STYLE_S3_20261017, SUPPORT_JA_STYLE_S3_SHA256,
                                      SUPPORT_JA_STYLE_S3_LENGTH)):
        if sha256_text(text) != sha or len(text) != length:
            raise StyleProfileStop(
                f"[STOP][STYLE-PROFILE] {label}定数のsha256/長さが原典と一致しません"
                f"(sha={sha256_text(text)}, len={len(text)})。コード改変の疑い。")
        common.assert_no_wpm_specification(text)


_verify_constants()  # import時にも検証(不一致=即STOP)


def get_profile(profile_id: str) -> dict:
    if profile_id not in STYLE_PROFILES:
        raise StyleProfileStop(f"[STOP][STYLE-PROFILE] 未知のstyle profile: {profile_id!r}"
                                f"(choices={sorted(STYLE_PROFILES)})")
    return STYLE_PROFILES[profile_id]


def overridden_roles(profile_id: str) -> list[str]:
    return sorted(get_profile(profile_id)["overrides"])


def overridden_segment_names(profile_id: str, level: str | None = None) -> list[str]:
    """segment名(runner側)。KP英英解説はsegmentではなくkey_phrases配下のため含まない。
    levelを渡すとそのlevelに適用されるroleのsegmentだけを返す(既定None=全level、従来互換)。"""
    names = []
    for role in overridden_roles(profile_id):
        if level is not None and level not in ROLE_LEVELS.get(role, ("a2", "b1b")):
            continue
        names.extend(ROLE_SEGMENTS.get(role, ()))
    return names


def resolve_role_style(profile_id: str, role: str, level: str, base_getter):
    """単一解決関数(runnerの_role_style/_role_style_slowerは全てここを経由する)。
    profileにそのroleのoverrideが無ければ base_getter(role) を素通しで返す
    (default・他roleはバイト同一)。overrideがあれば検証済みtextを返す。
    level("a2"|"b1b")はStd/Advの区別用。P8は両levelとも逐語(Stdも減速指示を連結しない、S1)。
    SUPPORT_JA(R2)はa2のみ、KP_EXPLANATION_EN(P3)はb1bのみ(対象外levelはbase_getter素通し)。"""
    override = get_profile(profile_id)["overrides"].get(role)
    if override is None:
        return base_getter(role)
    if level not in ("a2", "b1b"):
        raise StyleProfileStop(f"[STOP][STYLE-PROFILE] 不正なlevel: {level!r}")
    if level not in ROLE_LEVELS.get(role, ("a2", "b1b")):
        return base_getter(role)
    text = override["text"]
    if sha256_text(text) != override["sha256"]:
        raise StyleProfileStop(f"[STOP][STYLE-PROFILE] profile={profile_id} role={role} のsha256不一致")
    return text


def has_role_override(profile_id: str, role: str, level: str) -> bool:
    """profileにそのroleのoverrideがあり、かつlevelに適用されるか(KP音声の分岐用。runnerが
    「K2経路[Store 2段key]を使うか/従来経路か」を決めるのに使う。default・旧profileでは常にFalse)。"""
    if role not in get_profile(profile_id)["overrides"]:
        return False
    return level in ROLE_LEVELS.get(role, ("a2", "b1b"))


def profile_resolution_warning(profile_id: str, source: str) -> str | None:
    """R-07: CLI未指定時の「旧profileで動いている/新profileが適用されていない」ことを目立たせる[WARN]文(任意・非機能)。
    - source=="record"かつprofile!=DEFAULT_NEW_RUN_PROFILE: 旧profileでresume中(記録が正、黙って新profileへ切替わらない)。
    - source=="default_no_record_legacy_backend": legacy backendのため承認済み新profileは適用不可(tts stageは課金前STOP)。"""
    if source == "record" and profile_id != DEFAULT_NEW_RUN_PROFILE:
        return (f"[WARN][STYLE-PROFILE] 旧profileでresume中(profile={profile_id!r}、新規run既定={DEFAULT_NEW_RUN_PROFILE!r}ではありません)。"
                "固定記録(audit/style_profile.json)が正のため旧Styleのまま継続します。承認済みの新Styleを使う場合は新しいout_dirで実行してください。")
    if source == "default_no_record_legacy_backend":
        return (f"[WARN][STYLE-PROFILE] tts_backendがlegacyのため承認済みprofile({DEFAULT_NEW_RUN_PROFILE!r})を適用していません"
                f"(profile=default)。--tts-backend {APPROVED_BACKEND} を指定してください(tts stageはlegacy backendでは課金前にSTOPします)。")
    return None


def assert_profile_backend(profile_id: str, tts_backend: str) -> None:
    """M5: profile != default のとき tts_backend は speech_metadata_flash_lite 必須
    (--allow-legacy-backend でも同じ)。legacy backendでは_role_style()がNoneを返し
    P8が黙って落ちるため、課金前にSTOPする。"""
    if profile_id != PROFILE_DEFAULT and tts_backend != APPROVED_BACKEND:
        raise StyleProfileStop(
            f"[STOP][M5][USER_DECISION_REQUIRED] style profile {profile_id!r}は"
            f"tts_backend={APPROVED_BACKEND!r}でのみ実行できます(現在={tts_backend!r}、"
            "--allow-legacy-backendでも不可)。課金前にSTOPしました。")


# ------------------------------------------------------------
# 固定記録(out_dir/audit/style_profile.json)
# ------------------------------------------------------------
def record_path(out_dir: str) -> str:
    return f"{out_dir}/{PROFILE_RECORD_RELPATH}"


def build_record(profile_id: str) -> dict:
    profile = get_profile(profile_id)
    return {
        "profile_id": profile_id, "design_id": DESIGN_ID,
        "overridden_roles": overridden_roles(profile_id),
        "roles": {role: {"sha256": o["sha256"], "length": len(o["text"]),
                          **({"std_append_slower_instruction": o["std_append_slower_instruction"]}
                             if "std_append_slower_instruction" in o else {}),
                          **({"levels": list(ROLE_LEVELS[role])} if profile_id in _PROFILES_RECORDING_LEVELS else {})}
                  for role, o in profile["overrides"].items()},
        "std_verbatim_exception_id": STD_VERBATIM_EXCEPTION_ID,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }


def read_record(out_dir: str) -> dict | None:
    path = record_path(out_dir)
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:  # 壊れた記録=fail-closed
        raise StyleProfileStop(f"[STOP][STYLE-PROFILE] {path} を読めません: {type(e).__name__}") from e


def verify_record(record: dict) -> str:
    """記録が現行コードのprofile定義(roleごとのsha256)と一致することを検証し、profile_idを返す。"""
    profile_id = record.get("profile_id")
    profile = get_profile(profile_id)
    for role, o in profile["overrides"].items():
        rec_role = (record.get("roles") or {}).get(role) or {}
        if rec_role.get("sha256") != o["sha256"]:
            raise StyleProfileStop(
                f"[STOP][STYLE-PROFILE] 記録されたprofile={profile_id} role={role} のsha256が現行定義と不一致です"
                f"(記録={rec_role.get('sha256')}, 現行={o['sha256']})。")
    if sorted(record.get("overridden_roles") or []) != overridden_roles(profile_id):
        raise StyleProfileStop("[STOP][STYLE-PROFILE] 記録のoverridden_rolesが現行定義と不一致です。")
    return profile_id


def existing_run_artifacts(out_dir: str) -> list[str]:
    """M2: out_dir直下および各level(a2/b1b)のaudit/配下で、Review Lock/人間承認/TTS結果の
    いずれかが既に存在するパスを返す。"""
    found = []
    for base in (out_dir, f"{out_dir}/a2", f"{out_dir}/b1b"):
        for name in _RUN_STATE_FILES:
            path = f"{base}/audit/{name}"
            if os.path.exists(path):
                found.append(path)
    return found


def resolve_run_profile(out_dir: str, cli_profile: str | None, write: bool = True,
                        tts_backend: str | None = None) -> tuple[str, str]:
    """run全体のprofileを決定する。戻り値は (profile_id, source)。
    - 固定記録がある場合は記録を正とする。CLI未指定なら記録を採用(resume)。CLI明示で
      記録と食い違う場合はSTOP(silentにdefaultへ戻らない/途中でprofileが混在しない)。
    - 記録が無い場合:
        * CLI `default`(明示): 従来どおりdefault(新規file/keyは書かない、S3)。既存run(記録なし)のresume用。
        * CLI未指定(FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01、必須5 B'): run stateが無い新規out_dirは
          DEFAULT_NEW_RUN_PROFILE(2026-10-17以降fx_20261017、2026-10-16はfx_20261016)へ解決し固定記録を作成する(Family Xの承認済み6仕様の既定)。
          既存run state(Review Lock/人間承認/TTS結果)があるout_dirは、Style混在を防ぐため課金前にSTOPする
          (`--style-profile default`を明示してresume)。tts_backendがspeech_metadata_flash_lite以外
          (legacy backend、Trial/regression用)の場合は従来どおりdefault(M5によりN01は適用できない)。
        * CLI指定profile(coffee_p8 / n01 / coffee_n01_r2_p3等): 既存run記録(M2)があればSTOP、無ければ記録を作成する。"""
    if cli_profile is not None:
        get_profile(cli_profile)
    record = read_record(out_dir)
    if record is not None:
        recorded = verify_record(record)
        if cli_profile is not None and cli_profile != recorded:
            raise StyleProfileStop(
                f"[STOP][USER_DECISION_REQUIRED] --style-profile={cli_profile!r} が{record_path(out_dir)}の"
                f"固定記録({recorded!r})と食い違います。途中でprofileを変更できません。")
        return recorded, "record"
    if cli_profile == PROFILE_DEFAULT:
        return PROFILE_DEFAULT, "default_no_record"
    existing = existing_run_artifacts(out_dir)
    if cli_profile is None:
        if tts_backend is not None and tts_backend != APPROVED_BACKEND:
            return PROFILE_DEFAULT, "default_no_record_legacy_backend"
        if existing:
            raise StyleProfileStop(
                f"[STOP][M2][USER_DECISION_REQUIRED] 既存のrun記録があるout_dirで、style profileの固定記録がありません"
                f"(既定profile={DEFAULT_NEW_RUN_PROFILE!r}は新規out_dirにのみ適用されます。Review Lock/人間承認は"
                f"text shaのみで照合されStyleを区別しないため、既存runへの途中適用はStyle混在を招きます)。"
                f"既存の記録: {existing}。従来のstyleでresumeする場合は`--style-profile default`を明示してください。"
                f"style_profile.jsonは作成していません。")
        profile_id, source = DEFAULT_NEW_RUN_PROFILE, f"default_new_run_{DEFAULT_NEW_RUN_PROFILE}"
    else:
        if existing:
            raise StyleProfileStop(
                f"[STOP][M2][USER_DECISION_REQUIRED] --style-profile={cli_profile!r} は新しいout_dirでのみ実行できます"
                f"(Review Lock/人間承認はtext shaのみで照合されStyleを区別しないため、既存run記録の混在を防ぐ)。"
                f"既存の記録: {existing}。style_profile.jsonは作成していません。")
        profile_id, source = cli_profile, "cli_new_record"
    if write:
        os.makedirs(os.path.dirname(record_path(out_dir)), exist_ok=True)
        with open(record_path(out_dir), "w", encoding="utf-8") as f:
            json.dump(build_record(profile_id), f, ensure_ascii=False, indent=2)
    return profile_id, source


# ------------------------------------------------------------
# segment記録(S3: 上書き対象roleのsegmentにだけ付ける)
# ------------------------------------------------------------
def segment_profile_record(profile_id: str, role: str, applied_style: str | None):
    """上書き対象roleのsegmentにだけ付ける記録。非対象(default/他role)はNone(新keyを書かない)。
    style_base_sha256 = hint追記前にrunnerが渡したStyle文字列のsha256(M4)。"""
    override = get_profile(profile_id)["overrides"].get(role)
    if override is None:
        return None
    return {
        "profile_id": profile_id, "role": role, "expected_base_sha256": override["sha256"],
        "style_base_sha256": sha256_text(applied_style) if applied_style is not None else None,
    }


def attach_segment_profile_record(entry: dict, profile_id: str, role: str, applied_style: str | None) -> dict:
    rec = segment_profile_record(profile_id, role, applied_style)
    if rec is not None:
        entry["style_profile"] = rec
    return entry


# ------------------------------------------------------------
# M4: runtime evidence判定(hint追記を考慮)
# ------------------------------------------------------------
def _final_style_record(entry: dict, level: str) -> dict | None:
    """segment結果から実送信Style(hint追記後)のsha256/head200/lenを取り出す。
    Adv(news_tail_fix)=top-level style_prefix(文字列)、Std(repro01)=attempts_log末尾のstyle_prefix(record)。"""
    sp = entry.get("style_prefix")
    if isinstance(sp, str):
        if sp.startswith("<default:"):
            return None
        return {"sha256": sha256_text(sp), "head200": sp[:200], "len": len(sp)}
    if isinstance(sp, dict):
        return sp
    for att in reversed(entry.get("attempts_log") or []):
        rec = att.get("style_prefix") if isinstance(att, dict) else None
        if isinstance(rec, dict):
            return rec
    return None


def evaluate_segment_evidence(entry: dict, level: str, profile_id: str = PROFILE_COFFEE_P8,
                              role: str = "FULL_STORY") -> dict:
    """M4判定。base sha==role原文 かつ hintなしなら最終sha==原文、hintありなら先頭200字==原文[:200]
    (+ cache_hits列挙)。roleはFULL_STORY(P8)/KP_EXPLANATION_EN(P3)=英語(最終style記録あり)。
    SUPPORT_JA(R2)=日本語は発音hint追記が無く、attempt側にstyle記録も無いため、base shaのみで判定する
    (最終送信styleはraw_usage_log/attemptsのinstruction_textで別途実測する)。"""
    override = get_profile(profile_id)["overrides"][role]
    exp_sha, exp_text = override["sha256"], override["text"]
    reasons = []
    prof = entry.get("style_profile") or {}
    base_ok = prof.get("style_base_sha256") == exp_sha
    if not base_ok:
        reasons.append("STYLE_BASE_SHA_MISMATCH_OR_MISSING")
    if role in (ROLE_SUPPORT_JA, ROLE_KP_JA_MEANING):
        # 日本語role(R2/P8-KP)は発音hint追記が無くattempt側のstyle記録も無いため、base shaのみで判定する。
        # 既知制約(R-09): 日本語roleのM4は「意図したsha」の確認のみで、最終送信styleの実測はraw_usage_log/attemptsの
        # instruction_textで別途行う(将来migrate設計の条件)。
        return {"pass": base_ok and not reasons, "base_sha_ok": base_ok, "hint_applied": False,
                "cache_hits": [], "final_style_record": None, "reasons": reasons}
    if role == ROLE_KP_EN:
        # 再利用entry(Master Audio Store hit)は生成時のattempt styleを持たない(qa_evidenceのみ復元)ため、最終style判定は
        # 「今回新規生成かつ非fallback」のときだけ行う。再利用entryの正当性はStore key(kp_en_store_key_check)で判定する。
        if entry.get("reused") is True or entry.get("fallback_used") is True:
            return {"pass": base_ok and not reasons, "base_sha_ok": base_ok, "hint_applied": False,
                    "cache_hits": [], "final_style_record": None, "reasons": reasons,
                    "final_style_checked": False}
    info = entry.get("en_pronunciation_resolver_info") or {}
    hint_applied = bool(info.get("hints_applied"))
    cache_hits = [h.get("surface", h) if isinstance(h, dict) else h for h in (info.get("cache_hits") or [])]
    final = _final_style_record(entry, level)
    final_ok = False
    if final is None:
        reasons.append("FINAL_STYLE_RECORD_MISSING")
    elif hint_applied:
        # 原文が200字未満(P3=141字)だとhead200にhint冒頭が混ざるため、==ではなくstartswithで判定する。
        final_ok = (str(final.get("head200") or "").startswith(exp_text[:200])) and (final.get("len", 0) >= len(exp_text))
        if not final_ok:
            reasons.append("FINAL_STYLE_HEAD200_MISMATCH_WITH_HINT")
    else:
        final_ok = final.get("sha256") == exp_sha
        if not final_ok:
            reasons.append("FINAL_STYLE_SHA_MISMATCH_NO_HINT")
    return {"pass": base_ok and final_ok and not reasons, "base_sha_ok": base_ok, "hint_applied": hint_applied,
            "cache_hits": cache_hits, "final_style_record": final, "reasons": reasons}


def kp_en_store_key_check(entry: dict, profile_id: str) -> dict:
    """KP_EN(K2)のMaster Audio Store key判定(R-01/R-02)。entry["master_audio_key"]で:
      - style_instruction_idがK2用id(KP_EN_STORE_STYLE_ID)であること(旧`key_phrase_english_component`=MINIMAL style由来は不可)
      - instruction_path=="primary"の場合: style_instruction_versionに`+k2.<K2 sha12>`を含むこと(K2文が変われば不一致)
      - instruction_path=="english_lock_fallback"の場合: 承認済み4回構成の後半(ENGLISH_LOCK)で生成された音声=WARNING(非ブロッキング)
      - それ以外のpath/key欠落は違反
    戻り値: {"violations": [...], "warnings": [...]}。"""
    exp_sha = get_profile(profile_id)["overrides"][ROLE_KP_EN]["sha256"]
    key = entry.get("master_audio_key")
    violations, warnings = [], []
    if not isinstance(key, dict):
        violations.append("KP_EN_STORE_KEY_MISSING")
        return {"violations": violations, "warnings": warnings}
    if key.get("style_instruction_id") != KP_EN_STORE_STYLE_ID:
        violations.append("KP_EN_STORE_KEY_ID_MISMATCH")
    path = key.get("instruction_path")
    if path == KP_EN_STORE_PATH_PRIMARY:
        if f"+k2.{exp_sha[:12]}" not in str(key.get("style_instruction_version") or ""):
            violations.append("KP_EN_STORE_KEY_VERSION_MISMATCH")
    elif path == KP_EN_STORE_PATH_FALLBACK:
        warnings.append("KP_EN_ENGLISH_LOCK_FALLBACK_AUDIO_NOT_K2")
    else:
        violations.append("KP_EN_STORE_KEY_PATH_INVALID")
    if entry.get("fallback_used") is True and path != KP_EN_STORE_PATH_FALLBACK:
        # 新規生成でfallback_used=Trueなのにkeyがfallback pathでない=Store keyの付け間違い(K2 primary扱いにしてはならない)
        violations.append("KP_EN_FALLBACK_USED_BUT_KEY_NOT_FALLBACK_PATH")
    return {"violations": violations, "warnings": warnings}


# ------------------------------------------------------------
# M3: Assembly前Gate(Family X runnerのstage_assemble内でのみ呼ぶ。共有assembleは不変)
# ------------------------------------------------------------
def _approved(approvals: dict, name: str, entry: dict) -> bool:
    approval = (approvals or {}).get(name)
    if not approval:
        return False
    canon = entry.get("canonical_text") or entry.get("text") or ""
    return approval.get("canonical_text_sha256") == sha256_text(canon)


def _gate_targets(profile_id: str, level: str, results: dict) -> list[tuple[str, str, dict | None]]:
    """(gate上の名前, role, entry or None)の列。KP英英解説はkey_phrases[rank]["explanation"]から取る。"""
    segments = (results or {}).get("segments") or {}
    targets = []
    for role in overridden_roles(profile_id):
        if level not in ROLE_LEVELS.get(role, ("a2", "b1b")):
            continue
        if role in ROLE_KP_RESULT_KEY:
            # KP系role(KP_EXPLANATION_EN/KP_EN/KP_JA_MEANING)はsegmentsでなくkey_phrases[rank][結果キー]から取る。
            rkey = ROLE_KP_RESULT_KEY[role]
            kps = (results or {}).get("key_phrases") or {}
            if not kps:
                label = "kp_explanation" if role == ROLE_KP_EXPLANATION_EN else f"kp_{rkey}"
                targets.append((f"{label}(no key_phrases record)", role, None))
            for rank in sorted(kps, key=lambda k: int(k)):
                targets.append((f"kp{rank}_{rkey}", role, (kps[rank] or {}).get(rkey)))
            continue
        for name in ROLE_SEGMENTS.get(role, ()):
            targets.append((name, role, segments.get(name)))
    return targets


def m3_assembly_gate(profile_id: str, level: str, results: dict, approvals: dict | None = None) -> dict:
    """profile対象role各segmentについて:
      - style_profile.style_base_sha256 == そのroleの原文sha
      - FULL_STORY(Adv): style_prefix が原文で始まる / instruction_type != minimal_fallback
      - FULL_STORY(Std)/SUPPORT_JA: fallback_used が False(minimal instruction fallbackはroleのStyleを落とす)
      - local_rewrite_recovery なし
      - KP_EXPLANATION_EN: status OK
      - M4のFinal Style判定(英語role、hintあり/なし)
    を満たさない場合、record_human_approval(人間承認、canonical text sha一致)が無ければBLOCK。
    profile==default なら何もしない(PASS)。"""
    if profile_id == PROFILE_DEFAULT:
        return {"status": "PASS", "profile_id": profile_id, "checked": [], "blocked": [], "human_approved": []}
    checked, blocked, human_approved, warnings = [], [], [], []
    for name, role, entry in _gate_targets(profile_id, level, results):
        violations = []
        if entry is None:
            violations.append("NO_SEGMENT_RECORD")
        else:
            exp_text = get_profile(profile_id)["overrides"][role]["text"]
            if entry.get("status") not in (None, "OK") and role == ROLE_KP_EXPLANATION_EN:
                violations.append("KP_EXPLANATION_STATUS_NOT_OK")
            ev = evaluate_segment_evidence(entry, level, profile_id, role)
            violations.extend(ev["reasons"])
            if role == "FULL_STORY":
                if level == "b1b":
                    sp = entry.get("style_prefix")
                    if not (isinstance(sp, str) and sp.startswith(exp_text)):
                        violations.append("ADV_STYLE_PREFIX_NOT_PROFILE_PREFIXED")
                    if entry.get("instruction_type") == "minimal_fallback":
                        violations.append("ADV_MINIMAL_FALLBACK")
                else:
                    if entry.get("fallback_used") is not False:
                        violations.append("STD_FALLBACK_USED_OR_UNKNOWN")
            elif role == ROLE_SUPPORT_JA:
                if entry.get("fallback_used") is not False:
                    violations.append("JA_FALLBACK_USED_OR_UNKNOWN")
            elif role == ROLE_KP_JA_MEANING:
                # P8-KP(Std KP日本語意味): SUPPORT_JAと同等。fallback_used is False必須(JAのfallbackはroleのStyleを落とす)。
                if entry.get("fallback_used") is not False:
                    violations.append("KP_JA_MEANING_FALLBACK_USED_OR_UNKNOWN")
                if entry.get("status") not in (None, "OK"):
                    violations.append("KP_JA_MEANING_STATUS_NOT_OK")
            elif role == ROLE_KP_EN:
                # K2: base sha(上のevaluate_segment_evidence)+Store key判定。新規生成かつ非fallbackのときだけ最終style判定も行われる。
                if entry.get("status") not in (None, "OK"):
                    violations.append("KP_EN_STATUS_NOT_OK")
                kc = kp_en_store_key_check(entry, profile_id)
                violations.extend(kc["violations"])
                for w in kc["warnings"]:
                    warnings.append({"segment": name, "warning": w})
            elif role == ROLE_PREVIEW:
                # Adv Preview(E1): 実送信styleがE1で始まる/minimal_fallback(E1を落とす)でない。
                sp = entry.get("style_prefix")
                if not (isinstance(sp, str) and sp.startswith(exp_text)):
                    violations.append("PREVIEW_STYLE_PREFIX_NOT_E1_PREFIXED")
                if entry.get("instruction_type") == "minimal_fallback":
                    violations.append("PREVIEW_MINIMAL_FALLBACK")
            if entry.get("local_rewrite_recovery"):
                violations.append("LOCAL_REWRITE_RECOVERY")
        checked.append(name)
        if violations:
            if entry is not None and _approved(approvals, name, entry):
                human_approved.append({"segment": name, "violations": violations})
            else:
                blocked.append({"segment": name, "violations": violations})
    # warnings: 非ブロッキング(承認済み4回構成のfallback音声など)。runnerがstdoutとgate出力に列挙する。
    return {"status": "BLOCK" if blocked else "PASS", "profile_id": profile_id, "level": level,
            "checked": checked, "blocked": blocked, "human_approved": human_approved, "warnings": warnings}



# ------------------------------------------------------------
# 記録移行(委任_03 OF-Y8): 既存out_dirのstyle_profile.jsonを上位集合profileへ1回限り明示的に移行する。
# 通常のresolve_run_profile(M2)は既存run state有りで新規記録を禁止する。移行はこの関数(明示CLI経由)のみ例外。
# ------------------------------------------------------------
MIGRATED_FROM_RELPATH_TMPL = "audit/style_profile_migrated_from_{n:02d}.json"


def _canonical_sha(obj) -> str:
    return sha256_text(json.dumps(obj, ensure_ascii=False, sort_keys=True))


def migrate_record(out_dir: str, from_profile: str, to_profile: str, reason: str, managed_id: str,
                   now: str | None = None) -> dict:
    """条件: (1)固定記録が存在しprofile_id==from_profile かつ現行定義でverify通過、(2)from!=to、
    (3)移行先のoverride role集合が移行元の上位集合で、移行元の全roleの文言shaが移行先と一致、(4)reason/managed_id非空。
    動作: 旧記録を audit/style_profile_migrated_from_NN.json へ退避(上書きしない)→新記録にmigration情報を含めて書く。"""
    if not (reason or "").strip() or not (managed_id or "").strip():
        raise StyleProfileStop("[STOP][STYLE-PROFILE][MIGRATE] --reasonとManaged-IDは必須です。")
    if from_profile == to_profile:
        raise StyleProfileStop("[STOP][STYLE-PROFILE][MIGRATE] 移行元と移行先が同一です。")
    get_profile(from_profile)
    get_profile(to_profile)
    old = read_record(out_dir)
    if old is None:
        raise StyleProfileStop("[STOP][STYLE-PROFILE][MIGRATE] 移行元の固定記録がありません。")
    if old.get("profile_id") != from_profile:
        raise StyleProfileStop(f"[STOP][STYLE-PROFILE][MIGRATE] 記録のprofile_id({old.get('profile_id')!r})が--from({from_profile!r})と不一致です。")
    verify_record(old)
    from_over = get_profile(from_profile)["overrides"]
    to_over = get_profile(to_profile)["overrides"]
    missing = sorted(set(from_over) - set(to_over))
    if missing:
        raise StyleProfileStop(f"[STOP][STYLE-PROFILE][MIGRATE] 移行先が移行元のrole集合の上位集合ではありません(欠落role={missing})。")
    for role, o in from_over.items():
        if to_over[role]["sha256"] != o["sha256"]:
            raise StyleProfileStop(f"[STOP][STYLE-PROFILE][MIGRATE] role={role}の文言shaが移行先と一致しません(既存roleの変更は不可)。")
    old_path = record_path(out_dir)
    with open(old_path, "rb") as f:
        old_bytes_sha = hashlib.sha256(f.read()).hexdigest()
    n = 1
    while os.path.exists(f"{out_dir}/{MIGRATED_FROM_RELPATH_TMPL.format(n=n)}"):
        n += 1
    archive = f"{out_dir}/{MIGRATED_FROM_RELPATH_TMPL.format(n=n)}"
    new_rec = build_record(to_profile)
    new_sha = _canonical_sha({k: new_rec[k] for k in ("profile_id", "overridden_roles", "roles")})
    ts = now or time.strftime("%Y-%m-%dT%H:%M:%S")
    new_rec["migration"] = {"from": from_profile, "to": to_profile, "reason": reason, "managed_id": managed_id,
                            "timestamp": ts, "old_sha": old_bytes_sha, "new_sha": new_sha,
                            "archived_old_record": os.path.basename(archive),
                            "added_roles": sorted(set(to_over) - set(from_over))}
    os.replace(old_path, archive)
    with open(old_path, "w", encoding="utf-8") as f:
        json.dump(new_rec, f, ensure_ascii=False, indent=2)
    verify_record(read_record(out_dir))
    return new_rec

# ------------------------------------------------------------
# S2: plan段階のPronunciation Ledger hit計算(読み取りのみ、web lookup無効、課金0)
# ------------------------------------------------------------
def compute_ledger_hits(parts: dict, tts_safe_fn=None, full_story_text: str = P8_TEXT) -> dict:
    # 注: 既定引数のP8_TEXT・戻り値の`augmented_startswith_p8`/`p8_len`は「Full Story旧候補P8」(402文字)の互換キー。
    # 現行profile(N01/PD06等)ではrunnerが適用中profileのFull Story textを`full_story_text`で渡す(KP日本語意味のP8-KPとは無関係)。
    """Full Story各part(part1..3)について、現行Pronunciation Ledger(cache)のhintが
    P8へ追記されるかを事前計算する。augment_style_prefix_with_pronunciation を直接呼ぶ
    (resolve_and_augment_en_style_prefixの第1段と同一。低confidence再research[web]は呼ばない)。"""
    import er006_pronunciation_tts_injection_01 as en_injection
    out = {}
    for key in ("part1", "part2", "part3"):
        text = parts.get(key)
        if text is None:
            continue
        safe = tts_safe_fn(text) if tts_safe_fn else text
        augmented, hits = en_injection.augment_style_prefix_with_pronunciation(full_story_text, safe, min_confidence="medium")
        out[f"full_story_{key}"] = {
            "hint_applied": bool(hits),
            "cache_hits": [{"surface": h.get("surface"), "confidence": h.get("confidence")} for h in hits],
            "p8_len": len(full_story_text), "augmented_len": len(augmented),
            # key名は後方互換(中身は適用中profileのFull Story style[P8またはN01]で判定)
            "augmented_startswith_p8": augmented.startswith(full_story_text),
            "augmented_startswith_full_story_style": augmented.startswith(full_story_text),
        }
    return out
