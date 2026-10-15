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

MANAGEMENT_ID = "FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01"
SUB_TASK_ID = "04C"
TTS_BACKEND = "speech_metadata_flash_lite"
FAMILY_Z_ROLE_STYLE_VERSION = "z_v2_pd8_r2_e1_e2up_k2_m2_kpx_20261012"  # v2: Adv KP第3segment(英語解説)のStyle追加(委任_05)
DEFAULT_SLUG = "melos"
LEVEL_DIR = {"std": "a2", "adv": "b1b"}  # a2=Standard、b1b=Advanced(出力ディレクトリ名のみ。ページ表示にはラベルを出さない)
GATE_LEVEL_STRING = {"a2": "A2", "b1b": "B1"}

SLOWDOWN_RATIO_MIN = 1.03
SLOWDOWN_RATIO_MAX = 1.09

_CLIP_ID_RE = re.compile(r"full_story_part([1-3])_c([0-9]+)")


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


class FamilyZNarratorStyleMismatchStop(FamilyZAudioStop):
    """run単位のnarrator style label記録と現行定義が食い違う(FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01 Opus必須7)。
    既存Z run dir(Melos等)はPD8で生成済み。N01へ途中切替するとrun内でnarrator styleが混在するため課金前にSTOPする。"""


class FamilyZVoiceMappingStop(FamilyZAudioStop):
    """Dialogue speakerに対応するVoiceが無い。"""


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
# 1. Z専用 Role -> Style 定数表(原典逐語、sha256で固定)
#    X定数(FAMILY_X_ROLE_STYLE_*)は不変。runtimeはここ(Z定数自身)のshaをassertする。
#    原典: PD8=er057_output/pace_trial_02/prompts/prompts_pace_02.md、R2=
#    er057_output/ja_aoede_style_trial_02/prompts/prompts_R.md、
#    A5/B5/E1/E2_UPBEAT=er057_output/coffee_final_listening_tone_trial_01/part_AEF/prompts/、
#    K2/M2=同part_BCD/prompts/。
# ============================================================
_PD8 = ("Warm, bright, cozy storytelling in the manner of a well-loved radio feature: unhurried, "
        "richly expressive, with full vowels and gentle emphasis, never flat or sleepy.")
_A2_SLOW_INSTRUCTION = (
    "Speak at a slightly slower, relaxed pace than natural adult narration, while keeping the delivery "
    "smooth, conversational, and natural. Do not exaggerate pauses or sound instructional.")
_R2 = ("明るく、温かみのある話し方で。身近な人にちょっとした話題を教えてあげるように、自然な抑揚と軽やかなリズムをつけてください。"
       "ニュース番組としての明瞭さは保ち、演技がかった話し方は避けてください。"
       "句読点の記号そのものに反応して声の高さを変えないでください。"
       "読点は短い息継ぎの間、句点はやや長めの間として、音程は変えずに自然に置いてください。")
_E1 = "calm, composed news anchor; steady and unhurried, clear and natural."
_E2_UPBEAT = ("warm, upbeat and engaging; friendly conversational delivery with lively but natural intonation.")
_K2 = ("Say the phrase as one single, smoothly connected chunk of meaning, as if the words belong together and "
       "are not read one by one. Keep the pitch movement small and continuous across the whole phrase. Say only "
       "this phrase, exactly once, without adding, omitting, or changing any words, and make sure the final "
       "sound is actually spoken.")
_M2 = "一つの意味のまとまりとして、途切れさせずに滑らかに、ひと息で読んでください。単語ごとに区切らず、抑揚の上下も小さく自然にしてください。"
# 参考(Zでは適用しない、shell/固定音声は既存Masterを使うため): Coffee Trial採用のA5/B5。原典照合のみ。
_A5 = "warm greeting that lands gently; the show name finishes with a soft, natural falling close, not clipped or rushed at the end."
_B5 = "friendly lead-in that lands gently; the last word settles with a soft, natural falling close, not clipped or rushed at the end."
# X既存承認Role Style(Xで運用中のTOPIC_INTRO / 日本語J3)。Zはtopic_intro_en/japanese_titleに限りこれを使う。
_X_TOPIC_INTRO = ("brief, clear, engaging news topic introduction with natural emphasis on the topic; "
                  "not dramatic.")
_X_JA_J3 = ("落ち着いた、自然な話し言葉で。意味の流れ・強調点・転換に応じて表情豊かに抑揚をつけてください。"
            "演技がかった話し方は避けてください。")

# 委任_05: Advanced KP第3segment(英語解説、Coffee最終v3 Advと同一構成)。X既存承認のKP解説Style
# (er033 KEY_PHRASE_EXPLANATION_EN)の逐語コピー。Xは不変(一致をtestで固定)。
_X_KP_EXPLANATION_EN = "clear, precise, at a measured pace, without dragging"

# N01(ユーザー正式決定2026-10-13 APPROVED_FOR_PRODUCTION、FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01): Full Story narrationの
# メイン音声Prompt。Xの`er019_family_x_style_profile_01.N01_TEXT`と同一文言の逐語copy(Xは不変・一致をtestで固定)。
# Std/Adv共通、Stdも逐語(旧PD8_A2SLOWの減速instruction連結は廃止。生成後6%減速・減速後再検証は共有module側で無変更)。
# 対象=narrator役のFull Story clip(短い帰属句narrator clipを含む)。Dialogue voices・Preview・Comment・KP等は対象外。
# 「sharing a true story」はFiction(Family Z)と意味がずれる可能性があり、USER_DECISION_REQUIRED N-2(文言は変更しない)。
_N01 = ("A cheerful, kind storyteller sharing a true story at a pace a little slower than usual. "
        "Bring each sentence to its natural close, then go directly on to the next, including where the story takes a turn.")

# 原典照合値(2026-10-12実装時に原典ファイルから抽出して一致確認済み。runtimeはTrialファイルへ依存しない)
_STYLE_SHA256 = {
    "N01": "d1956c91c925d197e27cf1204d7ed17248a96bef096b082fb1bd0846106a0477",
    "PD8": "329ff46a5ec3877f7dc23375e14ee8a806efeff7cfe27963492a3cf95d182226",
    "PD8_A2SLOW": "74b456cacf74af0ad08636776dc32fc35e041f869ecc7d60ecab190cf99a1f91",
    "R2": "625826c1187b6381fe36ff444f1f568fc1f68d639d6a6a8931e728463692252f",
    "E1": "8862317ff76693ff519ddfa956260a8cce2d540763333b54096b63161d84f641",
    "E2_UPBEAT": "37c52d6ec2377109c4f960ac0f4693ec54f6ee1dcaf5a8fec42ad718e155553e",
    "K2": "9d905cfe6c040cd001c4e7877327044f540a72bd315776f2c297e0f58f7aea42",
    "M2": "e7617e15c29e43cb76668d77e6c7102671754aae810fb15cd9367294f71a228d",
    "A5": "2c530b21d351db177e1a808b328a0a5dbdd58850782074c5b611129b7dafdfc1",
    "B5": "5e28dd287f20588137aae35a058d4bf30da91c4bdf75bd07dd2a61d176d24989",
}

_STYLE_TEXT = {
    "N01": _N01,
    "PD8": _PD8,
    "PD8_A2SLOW": _PD8 + "\n" + _A2_SLOW_INSTRUCTION,
    "R2": _R2, "E1": _E1, "E2_UPBEAT": _E2_UPBEAT, "K2": _K2, "M2": _M2, "A5": _A5, "B5": _B5,
}

# role key -> 仕様。text=Noneは「Zで独自styleを渡さない(従来/既存Master)」。
FAMILY_Z_ROLE_STYLE = {
    "NARRATOR_FULL_STORY_ADV": {
        "style_label": "N01", "text": _N01, "voice": "Aoede", "language": "en",
        "origin": "er057_output/coffee_tts_style_h_speed_04/round5/prompts_r5.json candidates.N01.style(旧PD8から2026-10-13置換)",
        "path": "news_tail_fix.generate_news_narration_wide_margin"},
    "NARRATOR_FULL_STORY_STD": {
        "style_label": "N01", "text": _N01, "voice": "Aoede", "language": "en",
        "origin": "N01逐語(Std減速instruction非連結。旧PD8_A2SLOW[PD8+A2減速instruction連結]から2026-10-13置換)",
        "path": "n3_tts.generate_a2_segment_with_slowdown(6%減速)"},
    "DIALOGUE_ADV": {
        "style_label": "existing_dialogue_style(ENGLISH_STYLE_PREFIX)", "text": None, "voice": "per-speaker", "language": "en",
        "origin": "er012 generate_voice_body_wide_margin 既定(style_prefix_override=None)。PD8は混入しない",
        "path": "er012.generate_voice_body_wide_margin"},
    "DIALOGUE_STD": {
        "style_label": "existing_dialogue_style+A2_SLOWER(n3_tts.A2_ENGLISH_STYLE_PREFIX_SLOWER)", "text": None, "voice": "per-speaker",
        "language": "en", "origin": "er012 Voice A/B Std既存仕様(A2_ENGLISH_STYLE_PREFIX_SLOWER+6%後処理)。PD8は混入しない",
        "path": "er012.generate_voice_body_wide_margin + n3_tts.apply_a2_slowdown_postprocess"},
    "STD_JA_PREVIEW": {"style_label": "R2", "text": _R2, "voice": "Aoede", "language": "ja",
                       "origin": "er057_output/ja_aoede_style_trial_02/prompts/prompts_R.md ## R2(OPEN-303: R2で確定)",
                       "path": "n3_tts.generate_a2_japanese_with_reading_safety"},
    "STD_JA_COMMENT": {"style_label": "R2", "text": _R2, "voice": "Aoede", "language": "ja",
                       "origin": "同上", "path": "n3_tts.generate_a2_japanese_with_reading_safety"},
    "ADV_EN_PREVIEW": {"style_label": "E1", "text": _E1, "voice": "Charon", "language": "en",
                       "origin": "coffee_final_listening_tone_trial_01/part_AEF/prompts/prompts_E.md ## E1(Coffee Adv Preview採用)",
                       "path": "voice01.generate_charon_english"},
    "ADV_EN_COMMENT": {"style_label": "E2_UPBEAT", "text": _E2_UPBEAT, "voice": "Charon", "language": "en",
                       "origin": "prompts_E.md Baseline = er057_tone_trial_tts_gen_01.EN_COMMENT_E2_UPBEAT(Coffee Adv Comment採用)",
                       "path": "voice01.generate_charon_english"},
    "KP_EN": {"style_label": "K2", "text": _K2, "voice": "Aoede", "language": "en",
              "origin": "coffee_final_listening_tone_trial_01/part_BCD/prompts/prompts_B.md ## K2",
              "path": "repro01.generate_narration_snippet_verified_strict(K2 primary / 既存ENGLISH_LOCK fallback)"},
    "KP_JA": {"style_label": "M2", "text": _M2, "voice": "Aoede", "language": "ja",
              "origin": "coffee_final_listening_tone_trial_01/part_BCD/prompts/prompts_C.md ## M2",
              "path": "n3_tts.generate_a2_japanese_with_reading_safety"},
    "TOPIC_INTRO_EN": {"style_label": "X_TOPIC_INTRO(既存承認)", "text": _X_TOPIC_INTRO, "voice": "Aoede/Charon", "language": "en",
                       "origin": "er033 FAMILY_X_ROLE_STYLE_EN['TOPIC_INTRO'] の逐語コピー(Xは不変)", "path": "crosslevel/voice01"},
    "JAPANESE_TITLE": {"style_label": "X_J3(既存承認)", "text": _X_JA_J3, "voice": "Aoede", "language": "ja",
                       "origin": "er033 FAMILY_X_ROLE_STYLE_JA(J3)の逐語コピー(Xは不変)", "path": "n3_tts.generate_a2_japanese_with_reading_safety"},
    "KP_EXPL_EN": {"style_label": "X_KP_EXPLANATION_EN(既存承認)", "text": _X_KP_EXPLANATION_EN, "voice": "Aoede", "language": "en",
                   "origin": "er033 KEY_PHRASE_EXPLANATION_EN の逐語コピー(Xは不変。Coffee最終v3 Advのkp解説は既存承認Style=Pと同一)",
                   "path": "er019.generate_key_phrase_explanation_en_verified"},
    "SHELL": {"style_label": "既存Master/共有Production資産(変更なし)", "text": None, "voice": "Charon", "language": "en",
              "origin": "assemble_mod.B1_SHARED_SOURCE_DIR(読み取りコピーのみ、Master Store書込なし)", "path": "copy"},
}

# 実装時の原典ファイル照合対象 (key -> (relative path, heading))
_ORIGIN_FILES = {
    "PD8": ("er057_output/pace_trial_02/prompts/prompts_pace_02.md", "## PD8"),
    "R2": ("er057_output/ja_aoede_style_trial_02/prompts/prompts_R.md", "## R2"),
    "A5": ("er057_output/coffee_final_listening_tone_trial_01/part_AEF/prompts/prompts_A.md", "## A5"),
    "B5": ("er057_output/coffee_final_listening_tone_trial_01/part_AEF/prompts/prompts_B.md", "## B5"),
    "E1": ("er057_output/coffee_final_listening_tone_trial_01/part_AEF/prompts/prompts_E.md", "## E1"),
    "K2": ("er057_output/coffee_final_listening_tone_trial_01/part_BCD/prompts/prompts_B.md", "## K2"),
    "M2": ("er057_output/coffee_final_listening_tone_trial_01/part_BCD/prompts/prompts_C.md", "## M2"),
}


def style_prefix_sha256(text) -> str | None:
    return None if text is None else _sha256_text(text)


def assert_style_table_integrity() -> dict:
    """runtime assert: Z定数自身のshaが記録値と一致すること(Trialファイルへのruntime依存なし)。"""
    report = {}
    for key, text in _STYLE_TEXT.items():
        actual = _sha256_text(text)
        if actual != _STYLE_SHA256[key]:
            raise FamilyZStyleIntegrityStop(f"Z Style定数 {key} のsha256が記録値と不一致: {actual} != {_STYLE_SHA256[key]}")
        report[key] = actual
    for role, spec in FAMILY_Z_ROLE_STYLE.items():
        if spec["text"] is not None and spec["style_label"] in _STYLE_SHA256 and _sha256_text(spec["text"]) != _STYLE_SHA256[spec["style_label"]]:
            raise FamilyZStyleIntegrityStop(f"role {role} のtextがStyle {spec['style_label']} と一致しません")
    return report


def role_style_sha256(role_key: str):
    return style_prefix_sha256(FAMILY_Z_ROLE_STYLE[role_key]["text"])


def _extract_fenced_after(path: str, heading: str) -> str:
    t = _read_text(path)
    i = t.index(heading)
    m = re.search(r"```\n(.*?)\n```", t[i:], re.S)
    return m.group(1)


def verify_styles_against_origin(repo_root: str = ".") -> dict:
    """実装時1回(および任意のevidence再生成)用: 原典ファイルから逐語抽出しsha256を照合する。
    runtimeでは呼ばない(Trialファイルへのruntime依存を作らない)。"""
    out = {}
    for key, (rel, heading) in _ORIGIN_FILES.items():
        p = os.path.join(repo_root, rel)
        text = _extract_fenced_after(p, heading)
        sha = _sha256_text(text)
        out[key] = {"origin": rel, "heading": heading, "origin_sha256": sha, "z_sha256": _STYLE_SHA256[key],
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
#    melos用の値のみ未定義だったため追加する。PROVISIONAL_UNAPPROVED: Voice選定は
#    ユーザー/Fable承認事項(Family C 'brother'の運用実績Voice Algieba を暫定値とする)。
# ============================================================
FAMILY_Z_DIALOGUE_VOICE_KEYWORDS = {
    # 挿入順=判定優先順(最初に一致したvoiceを採用)。Melos台詞を王/友への言及より優先する。
    "melos": ["melos"],
    "selinuntius": ["selinuntius", "friend"],
    "dionysius": ["dionysius", "ruler", "king", "tyrant"],
}
FAMILY_Z_DIALOGUE_VOICE_TTS_NAMES = {
    "narrator": "Aoede",
    "melos": "Algieba",        # PROVISIONAL_UNAPPROVED(新規割当、要ユーザー承認)
    "selinuntius": "Erinome",
    "dionysius": "Charon",
}
MELOS_VOICE_STATUS = "PROVISIONAL_UNAPPROVED"


# er062(04B)のsegment_planは speaker=melos/king/friend/other、voice_role=dialogue:<speaker> を出す。
# er063のVoice割当(Z-4: dionysius=Charon / selinuntius=Erinome)へ写像する。other等は未対応でSTOP。
SPEAKER_ALIASES = {"king": "dionysius", "friend": "selinuntius", "melos": "melos", "narrator": "narrator",
                   "dionysius": "dionysius", "selinuntius": "selinuntius"}


def normalize_speaker(raw: str) -> str:
    key = (raw or "narrator").split(":")[-1]
    if key not in SPEAKER_ALIASES:
        raise FamilyZVoiceMappingStop(f"未対応のspeaker {raw!r}(対応: {sorted(SPEAKER_ALIASES)})")
    return SPEAKER_ALIASES[key]


def resolve_dialogue_voice(speaker: str) -> str:
    try:
        return FAMILY_Z_DIALOGUE_VOICE_TTS_NAMES[speaker]
    except KeyError:
        raise FamilyZVoiceMappingStop(f"speaker={speaker!r} に対応するVoiceがFAMILY_Z_DIALOGUE_VOICE_TTS_NAMESにありません")


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
                     kp_explanations: dict | None = None) -> list:
    """生成が必要なClipSpec列を組む。story_clips=[{id,part,voice(speaker key or 'narrator'),text}]。
    shell/番号(welcome等)は provision_shell_assets で別途コピー(TTSなし)。"""
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
        speaker = normalize_speaker(c.get("speaker") or c.get("voice_role") or c.get("voice") or "narrator")
        kind = "narrator" if speaker == "narrator" else "dialogue"
        voice = resolve_dialogue_voice(speaker)
        plan.append(ClipSpec(c["id"], level, kind, c["text"], voice=voice, speaker=speaker,
                             role_key=role_key_for(kind, level, speaker), part=int(m.group(1)), language="en"))
    return plan


# ============================================================
# 3-N. run単位のnarrator style label記録(Opus必須7): 既存Z run dir(PD8生成済み)へのN01混在を課金前にSTOP
# ============================================================
NARRATOR_STYLE_RECORD_RELPATH = "audit/narrator_style_record.json"


def expected_narrator_style(level: str) -> dict:
    role_key = "NARRATOR_FULL_STORY_ADV" if level == "b1b" else "NARRATOR_FULL_STORY_STD"
    spec = FAMILY_Z_ROLE_STYLE[role_key]
    return {"role_style_key": role_key, "style_label": spec["style_label"],
            "style_prefix_sha256": style_prefix_sha256(spec["text"])}


def inspect_run_narrator_style(level_dir: str, level: str, cached: dict | None) -> dict:
    """読み取りのみ。status: NEW_RUN / RECORD_MATCH / RECORD_MISMATCH / ENTRIES_MATCH_NO_RECORD /
    LEGACY_NARRATOR_ENTRIES_MISMATCH。*_MISMATCHは呼び出し側でSTOPする。"""
    exp = expected_narrator_style(level)
    rec_path = f"{level_dir}/{NARRATOR_STYLE_RECORD_RELPATH}"
    if os.path.exists(rec_path):
        rec = _read_json(rec_path)
        ok = (rec.get("style_label") == exp["style_label"]
              and rec.get("style_prefix_sha256") == exp["style_prefix_sha256"])
        return {"status": "RECORD_MATCH" if ok else "RECORD_MISMATCH", "expected": exp, "recorded": rec}
    mismatches, seen = [], 0
    for clip_id, e in ((cached or {}).get("segments") or {}).items():
        if (e or {}).get("clip_kind") != "narrator" and not str((e or {}).get("role_style_key", "")).startswith("NARRATOR_"):
            continue
        seen += 1
        st = (e or {}).get("style") or {}
        if st.get("instruction_label") != exp["style_label"] or st.get("style_prefix_sha256") != exp["style_prefix_sha256"]:
            mismatches.append({"clip_id": clip_id, "recorded_label": st.get("instruction_label"),
                               "recorded_sha256": st.get("style_prefix_sha256")})
    if mismatches:
        return {"status": "LEGACY_NARRATOR_ENTRIES_MISMATCH", "expected": exp, "mismatches": mismatches}
    return {"status": "ENTRIES_MATCH_NO_RECORD" if seen else "NEW_RUN", "expected": exp, "narrator_entries": seen}


def assert_run_narrator_style(level_dir: str, level: str, cached: dict | None, *, write: bool = True) -> dict:
    info = inspect_run_narrator_style(level_dir, level, cached)
    if info["status"] in ("RECORD_MISMATCH", "LEGACY_NARRATOR_ENTRIES_MISMATCH"):
        raise FamilyZNarratorStyleMismatchStop(
            f"[STOP][N01] {level_dir} のnarrator styleが現行定義(N01)と一致しません: {info['status']} "
            f"(期待={info['expected']['style_label']}/{info['expected']['style_prefix_sha256']}, "
            f"{info.get('recorded') or info.get('mismatches')})。既存runはPD8等の旧styleで生成済みです。"
            "run内でnarrator styleが混在するため、課金前にSTOPしました(新規run dirで実行してください。記録は変更していません)。")
    if write and info["status"] in ("NEW_RUN", "ENTRIES_MATCH_NO_RECORD"):
        os.makedirs(f"{level_dir}/audit", exist_ok=True)
        _write_json(f"{level_dir}/{NARRATOR_STYLE_RECORD_RELPATH}", {
            **info["expected"], "level": level, "management_id": "FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01",
            "n01_sha256": _STYLE_SHA256["N01"]})
    return info


# ============================================================
# 4. M4: Z専用 generate_or_reuse_z(Xの_generate_or_reuseは呼ばない/不変)
# ============================================================
def style_text_for(spec: ClipSpec):
    """そのclipで実際に渡すstyle_prefix_override(None=従来Dialogue style/既存挙動)。"""
    if spec.kind == "dialogue":
        if spec.level == "a2":
            import er003_v1_n3_01_tts_generate as n3_tts
            return n3_tts.A2_ENGLISH_STYLE_PREFIX_SLOWER
        return None
    return FAMILY_Z_ROLE_STYLE[spec.role_key]["text"]


def build_reuse_key(spec: ClipSpec) -> dict:
    return {
        "canonical_text_sha256": _sha256_text(spec.text),
        "role_style_version": FAMILY_Z_ROLE_STYLE_VERSION,
        "voice": spec.voice,
        "style_prefix_sha256": style_prefix_sha256(style_text_for(spec)),
        "tts_backend": TTS_BACKEND,
    }


def generate_or_reuse_z(cached_entry: dict | None, spec: ClipSpec, wav_path: str, generate_fn) -> dict:
    """判定キー {canonical_text, FAMILY_Z_ROLE_STYLE_VERSION, voice, style prefix sha256, tts_backend}
    の全一致のみ再利用。キーはentryの reuse_key に保存。1つでも異なれば再生成。
    再利用時はwav実在・status OK・sha256一致(stale検知)も要求。"""
    generate_fn = secondary_run_scope.guard_generate(generate_fn, str(spec.clip_id))  # 委任_06c: circuit open中は技術STOP
    key = build_reuse_key(spec)
    if cached_entry and cached_entry.get("status") == "OK" and cached_entry.get("reuse_key") == key and os.path.exists(wav_path):
        recorded = cached_entry.get("sha256")
        if recorded is None or _sha_file(wav_path) == recorded:
            # AUW 委任_06c(OF-AUW-C-03、ADDENDUM §3-1): 再利用前に保存転写のみ(API 0)を現行の統一judgeへ通し、値ガードDIFF/否定差
            # (`reuse_blocked` mark含む)なら再利用せず再生成する。転写が無い/判定不能なentryは従来どおり再利用。
            import er078_reuse_value_guard_01 as _rvg
            _g = _rvg.guard_entry(cached_entry, label=str(spec.clip_id), canonical_text=None)
            if _g.get("blocked"):
                _r = generate_fn()
                if isinstance(_r, dict):
                    _r["reuse_value_guard_blocked_previous"] = {k: _g.get(k) for k in ("reason", "reason_code", "unified_state")}
                return _r
            reused = dict(cached_entry)
            reused["reused_from_previous_run"] = True
            if "asr_judgement" in reused:   # AUW 委任_03: 再利用音声の元のWARNINGを継承(asr_judgement_inherited)
                reused["asr_judgement_inherited"] = reused.pop("asr_judgement")
            return reused
    return generate_fn()


# ============================================================
# 5. 実TTS generator(遅延import、testではgeneratorsを差し替える)
# ============================================================
def _norm_for_tts(spec: ClipSpec) -> str:
    import er003_v1_n3_01_tts_generate as n3_tts
    if spec.kind in ("narrator", "dialogue"):
        return n3_tts.tts_safe_news_en(spec.text)
    if spec.kind in ("topic_intro", "preview", "comment") and spec.language == "en":
        return n3_tts.tts_safe_number_words_en(n3_tts.tts_safe_en(spec.text))
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
        if spec.level == "a2":
            # Std: 既存Voice A/B Std仕様(A2_ENGLISH_STYLE_PREFIX_SLOWER + 6%後処理)。PD8は渡さない。
            # 委任_06c(OF-AUW-C-08、原文L204「最大3回のTTS生成フロー」): 減速後NGでも通算TTS3回の残予算で取り直す外側ループ
            # (旧: 減速後NGは再生成せずSTOPPED)。Dialogue固有のPrompt(A2_ENGLISH_STYLE_PREFIX_SLOWER)・Voice・話者帰属は不変。
            return n3_tts.generate_with_a2_slowdown_outer_loop(
                spec.clip_id, text, out_path,
                lambda max_attempts: bvoices.generate_voice_body_wide_margin(
                    text, out_path, spec.voice, max_attempts=max_attempts,
                    style_prefix_override=n3_tts.A2_ENGLISH_STYLE_PREFIX_SLOWER))
        return bvoices.generate_voice_body_wide_margin(text, out_path, spec.voice)  # style_prefix_overrideを渡さない

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
        text = _norm_for_tts(spec)
        primary = repro01.generate_narration_snippet_verified_strict(
            text, "en", out_path, text, max_extra_chars=10, max_attempts=repro01.KEY_PHRASE_MINIMAL_MAX_ATTEMPTS,
            safety_margin_seconds=repro01.KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS, disfluency_qa=True,
            style_prefix_override=style_text_for(spec), asr_prompt=repro01.KEY_PHRASE_EN_ASR_NO_TRANSLATE_PROMPT,
            enable_non_latin_cascade=True, tts_backend=TTS_BACKEND,
            slot_offset=0, total_slots=repro01.KEY_PHRASE_TOTAL_MAX_ATTEMPTS)  # AUW 委任_05: 4回構成の前半(HR queue対象外)
        if primary.get("status") == "OK":
            primary["fallback_used"] = False
            return primary
        fb = repro01.generate_narration_snippet_verified_strict(
            text, "en", out_path, text, max_extra_chars=10, max_attempts=repro01.KEY_PHRASE_ENGLISH_LOCK_MAX_ATTEMPTS,
            safety_margin_seconds=repro01.KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS, disfluency_qa=True,
            style_prefix_override=repro01.KEY_PHRASE_ENGLISH_LOCK_INSTRUCTION,
            asr_prompt=repro01.KEY_PHRASE_EN_ASR_NO_TRANSLATE_PROMPT, enable_non_latin_cascade=True,
            tts_backend=TTS_BACKEND,
            slot_offset=repro01.KEY_PHRASE_MINIMAL_MAX_ATTEMPTS,
            total_slots=repro01.KEY_PHRASE_TOTAL_MAX_ATTEMPTS)  # AUW 委任_05: 4回構成の後半(最終slot)
        fb["fallback_used"] = True
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
            out.append({
                "phase": phase, "attempt": a.get("attempt"),
                "instruction_type": a.get("instruction_type"),
                "instruction_label": a.get("instruction_label") or a.get("instruction_type"),
                "style_prefix_sha256": _style_record_sha(sp),
                "style_prefix_head": (sp.get("head200") if isinstance(sp, dict) else (sp if isinstance(sp, str) else None)),
                "tts_model_id": a.get("tts_model_id") or meta.get("model"), "voice": a.get("voice") or meta.get("voice"),
                "audio_classification": a.get("audio_classification"), "verified": a.get("verified"),
                "asr_text": a.get("asr_text"),
            })
    return out


def _sha_file(path: str):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _wav_duration(path: str):
    import soundfile as sf
    return float(sf.info(path).duration)


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
                  "style_prefix_sha256": style_sha, "effective_style_prefix_sha256": _effective_style_sha(spec, style_sha),
                  "fallback_used": bool(result.get("fallback_used") or fallback_attempts),
                  "fallback_attempts": [{"instruction_label": a["instruction_label"],
                                         "style_prefix_sha256": a["style_prefix_sha256"],
                                         "style_prefix_head": a["style_prefix_head"]} for a in fallback_attempts]},
        "reuse_key": build_reuse_key(spec),
        "slowdown_ratio": ratio, "attempts": attempts,
        "cooldown_occurred": bool(stop_events), "cooldown_events": stop_events,
        "audio_text_deviation": deviation,
        "tts_generations_used": result.get("tts_generations_used"),
        # AUW 委任_03(additive): 統一ASR判定の監査record(PASS_WITH_WARNING等)。事後試聴リストの入力。
        "asr_judgement": result.get("asr_judgement"),
    }
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
def run_tts_stage(run_dir: str, level: str, plan: list, *, generators: dict | None = None, dry_run: bool = False,
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
        _c = _merge_checkpoint(load_results(level_dir), load_checkpoint(level_dir))
        return {"dry_run": True, "planned": planned, "writes": 0,
                "narrator_style_record": inspect_run_narrator_style(level_dir, level, _c)}
    cached = load_results(level_dir)
    cached = _merge_checkpoint(cached, load_checkpoint(level_dir))   # 委任_10: process中断時もOK clipを再利用(再課金しない)
    # Opus必須7: 生成器(TTS client)を作る前・課金前に、run単位のnarrator style label記録を確認する。
    assert_run_narrator_style(level_dir, level, cached, write=False)
    gens = generators or real_generators()
    os.makedirs(narr, exist_ok=True)
    os.makedirs(f"{level_dir}/audit", exist_ok=True)
    assert_run_narrator_style(level_dir, level, cached, write=True)
    segments, key_phrases, evidence = {}, {}, []
    deferred_stop = None
    import er005_cost_logger as cl
    for spec in plan:
        out_path = f"{narr}/{spec.wav_name()}"
        if not layout_is_valid(out_path):
            raise FamilyZAudioStop(f"narration配置が不正です(.../<run>/<level>/narration/<segment>.wav): {out_path}")
        if only_clips and spec.clip_id not in only_clips:
            prev = _cached_entry(cached, spec)
            if prev is not None:
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
        _store(segments, key_phrases, spec, entry)
        evidence.append(_evidence_row(spec, out_path, entry))
        save_checkpoint(level_dir, segments, key_phrases)
        if deferred_stop is not None:
            break
    import er011_human_review_lock_01 as review_lock
    results_path = f"{level_dir}/audit/tts_generation_results.json"
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
        "reused": bool(entry.get("reused_from_previous_run")), "duration_seconds": entry.get("duration_seconds"),
        "cost_jpy": entry.get("cost_jpy"),
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


def verify_std_english_slowdown(level_dir: str, required_clip_entries: dict, narration_dir: str | None = None) -> dict:
    """M1: 全Std英語Story clip(narrator・dialogue、_cN含む、Human Review採択も対象)で
    slowdown_applied is True、または _original.wav と現行wavの再生時間比∈[1.03,1.09]を要求する。
    (比 = 現行/original。減速後の方が長い。設計書は逆向きの記載だが、既存Gate
    _segment_missing_mandatory_a2_slowdownと同じ向きに揃える。)
    required_clip_entries: {clip_id: entry}。例外なし、1つでも不合格ならGate前にSTOP。"""
    narration_dir = narration_dir or f"{level_dir}/narration"
    failures, detail = [], {}
    for cid, entry in required_clip_entries.items():
        if not _CLIP_ID_RE.fullmatch(cid):
            continue
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
    if failures:
        raise FamilyZSlowdownGateStop(f"Std英語Story clipに6%減速の証跡がありません: {failures}")
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
    ids = required_clip_ids(plan, shell_names)
    m2 = assert_tts_results_complete(level_dir, ids)
    data = _read_json(f"{level_dir}/audit/tts_generation_results.json")
    entries = {cid: _lookup_entry(data, cid) for cid in ids}
    slow = None
    if level == "a2":
        slow = verify_std_english_slowdown(level_dir, {k: v for k, v in entries.items() if _CLIP_ID_RE.fullmatch(k)})
    problems = check_clip_audio_quality(f"{level_dir}/narration", {k: v for k, v in entries.items() if v and v.get("clip_kind")})
    if problems:
        raise FamilyZAudioStop(f"clip品質確認でNG: {problems}")
    deviations = {k: v["audio_text_deviation"] for k, v in entries.items() if v and v.get("audio_text_deviation")}
    result = {"m2_complete": True, "m1_slowdown": slow, "audio_text_deviation_clips": sorted(deviations),
              "audio_text_deviations": m2["audio_text_deviations"],
              "article_text_source": "canonical(原稿のまま)", "shared_gate": "skipped" if skip_shared_gate else "PASS"}
    if not skip_shared_gate:
        import er003_v1_n3_01_assemble as asm
        asm.verify_episode_audio_validation_gate(level_dir, GATE_LEVEL_STRING[level], article_text=article_text)
    os.makedirs(f"{level_dir}/audit", exist_ok=True)
    _write_json(f"{level_dir}/audit/gate_result_{SUB_TASK_ID}.json", result)
    return result


# ============================================================
# 9. Assembly(Family C assemble_with_timeline / sequence builderを再利用)
# ============================================================
SHELL_ASSET_SOURCES = {
    "welcome": "welcome_charon.wav", "preview_intro": "preview_intro_charon.wav",
    "key_phrases_intro": "key_phrases_intro_charon.wav", "full_story_intro": "full_story_intro_charon.wav",
}
NUMBER_ASSET_SOURCES = {f"kp{i}_number": f"num_{w}_charon.wav" for i, w in enumerate(["one", "two", "three", "four", "five"], 1)}


def provision_shell_assets(run_dir: str, level: str, kp_count: int = 5, *, dry_run: bool = False) -> dict:
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
                     intro_gained, notification_gained, outro_gained, kp_third: str = "japanese") -> list:
    """Z sequence: Intro(Literature導入なし)->Welcome->Topic->(Std: JA title)->Preview->KP->Comment1->
    Story Part1(clips)->Comment2->Part2->Comment3->Part3->Outro(In One Lineなし)。Family Cのbuilderをそのまま利用。"""
    import er013_family_c_production_runner_01 as runner_c
    story_segments = [{"id": c["id"], "audio_path": f"{narr_dir}/{c['id']}.wav",
                       "voice": normalize_speaker(c.get("speaker") or c.get("voice_role") or c.get("voice") or "narrator")}
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
                 kp_third: str = "japanese") -> dict:
    """gain -> sequence -> assemble_with_timeline -> headroom safety valve -> wav + timeline.json。"""
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

    def load_mono(path):
        return common.read_wav_float(path)[0]

    target_rms = (p9a.rms(load_mono(f"{narr}/preview.wav")) + p9a.rms(load_mono(f"{narr}/{story_clips[0]['id']}.wav"))) / 2
    gain_report["target_rms"] = round(float(target_rms), 5)

    def gs(mono, label):
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
                           kp_third=kp_third)
    res = asm.assemble_with_timeline(seq)
    safety = asm.apply_headroom_safety_valve(res["assembled"], seq)
    os.makedirs(f"{level_dir}/assembly", exist_ok=True)
    wav = f"{level_dir}/assembly/Family_Z_{story_key}_{level}.wav"
    common.write_wav_float(wav, safety["assembled"], SR, 2)
    timeline = {"story_key": story_key, "level": level, "wav": wav, "duration_seconds": res["total_duration_seconds"],
                "timeline": res["timeline"], "headroom": safety["report"], "gain_report": gain_report,
                "sequence_order": [n for n, _ in seq if not n.startswith("_silence_")]}
    _write_json(f"{level_dir}/assembly/timeline.json", timeline)
    return timeline


# ============================================================
# 10. 試聴ページ生成(user_test/family_z_melos_01/{index,standard,advanced}.html)
#     file:/// 禁止、(A2)/(B1)/B1Bラベル非表示、Key Phrasesは左=英語/右=日本語の2列。
# ============================================================
PAGES_DIR = "user_test/family_z_melos_01"
_FORBIDDEN_LABEL_RE = re.compile(r"\(A2\)|\(B1\)|B1B")


def _esc(s) -> str:
    import html
    return html.escape("" if s is None else str(s))


def build_listening_page_html(level_label: str, rows: list, kp_rows: list, full_audio_rel: str, duration: float,
                              tts_mode: str = "Standard同期(TTS_EXECUTION_MODE=STANDARD)",
                              warn_section_html: str = "") -> str:
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
    return (f"<!doctype html><html lang='ja'><head><meta charset='utf-8'><title>走れメロス {level_label} 試聴</title>"
            "<style>body{font-family:sans-serif;max-width:1180px;margin:1em auto;padding:0 1em;line-height:1.5}"
            "table{border-collapse:collapse;width:100%;margin-bottom:1.2em}th,td{border:1px solid #ccc;padding:6px;vertical-align:top;text-align:left}"
            "td.play{min-width:360px}td.play audio{width:100%}.script{background:#f6f6f6;padding:4px;white-space:pre-wrap}"
            ".note{background:#fff8e0;padding:3px;font-size:.85em}.voice{color:#555;font-size:.85em}"
            "table.kp td{width:50%}.combo{background:#eef6ff;padding:10px;border:1px solid #99c}</style></head><body>"
            f"<h1>走れメロス {level_label}</h1><p>TTS方式: {_esc(tts_mode)}</p>"
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


def build_page_rows(run_dir: str, level: str, audio_rel_prefix: str, audio_out_dir: str) -> tuple:
    """timeline.json + tts_generation_results.json から試聴ページの行を作り、timelineスライスのmp3を書き出す。
    戻り値=(rows, kp_rows, full_mp3_name, duration)。テキスト未取得のsegmentは『未取得』と明記(推測補完なし)。"""
    import soundfile as sf
    level_dir = f"{run_dir}/{level}"
    tl = _read_json(f"{level_dir}/assembly/timeline.json")
    data = _read_json(f"{level_dir}/audit/tts_generation_results.json")
    x, sr = sf.read(tl["wav"], dtype="float32")
    os.makedirs(audio_out_dir, exist_ok=True)
    full_name = f"Melos_{level}_full.mp3"
    sf.write(f"{audio_out_dir}/{full_name}", x, sr, format="MP3")
    rows, kp_rows = [], []
    for i, e in enumerate(tl["timeline"]):
        part = e["part"]
        if part.startswith("_silence_"):
            continue
        s, d = e["start_seconds"], e["duration_seconds"]
        fn = f"{level}_{len(rows):02d}.mp3"
        sf.write(f"{audio_out_dir}/{fn}", x[int(round(s * sr)): int(round((s + d) * sr))], sr, format="MP3")
        cid = part_to_clip_id(part)
        entry = _lookup_entry(data, cid) if cid else None
        row = {"part": part, "clip_id": cid, "start": s, "dur": d, "file": f"{audio_rel_prefix}{fn}", "voice": "-", "style": "-",
               "script": "(音楽・通知音。読み上げなし)" if part.startswith(("Intro", "Outro", "Notification")) else "未取得", "notes": []}
        if entry:
            row["voice"] = entry.get("voice", "-")
            row["style"] = (entry.get("style") or {}).get("instruction_label", "-")
            row["script"] = entry.get("canonical_text") or FIXED_SHELL_TEXT.get(cid, "未取得")
            if entry.get("slowdown_applied"):
                row["notes"].append(f"6%減速適用(比 {entry.get('slowdown_ratio')})" if entry.get("slowdown_ratio") else "6%減速適用")
            if entry.get("audio_text_deviation"):
                row["notes"].append("Local Rewrite採用(音声は原稿から変更: " + entry["audio_text_deviation"].get("diff_summary", "") + ")")
        if part.startswith("key_phrase_"):
            n = part.split("_")[-1]
            kp = (data.get("key_phrases") or {}).get(n) or {}
            en = (kp.get("english") or {}).get("canonical_text", "未取得")
            ja = (kp.get("japanese_meaning") or kp.get("explanation") or {}).get("canonical_text", "未取得")
            kp_rows.append((en, ja))
            row["script"] = f"{en} / {ja}"
            row["voice"] = "Aoede(KP) / Charon(番号)"
            row["style"] = "K2 / M2"
        rows.append(row)
    return rows, kp_rows, full_name, tl["duration_seconds"]


def build_pages(run_dir: str, pages_dir: str = PAGES_DIR) -> dict:
    """user_test/family_z_melos_01/{index,standard,advanced}.html を生成する(静的ファイルのみ)。"""
    os.makedirs(pages_dir, exist_ok=True)
    out = {}
    warn_sections = []
    for level, fname, label in (("a2", "standard.html", "Standard"), ("b1b", "advanced.html", "Advanced")):
        audio_dir = f"{pages_dir}/audio_{label.lower()}"
        rows, kp_rows, full, dur = build_page_rows(run_dir, level, f"audio_{label.lower()}/", audio_dir)
        # AUW 委任_03: 事後試聴リスト(PASS_WITH_WARNING)節(0件でも節を出す)。mp3リンクは当該partの試聴ページ内mp3。
        import er078_pass_with_warning_registry_01 as _pww
        warn_entries = _pww.load_listening_list(f"{run_dir}/{level}")
        clip_to_file = {r.get("clip_id"): r["file"] for r in rows if r.get("clip_id")}
        warn_html = _pww.render_html_section(
            warn_entries, href_fn=lambda e: clip_to_file.get(_warn_entry_to_clip_id(e.get("entry_key", "")), ""))
        warn_sections.append((label, warn_html))
        html_text = build_listening_page_html(label, rows, kp_rows, f"audio_{label.lower()}/{full}", dur,
                                              warn_section_html=warn_html)
        lint = lint_page_html(html_text)
        if any(lint.values()):
            raise FamilyZAudioStop(f"試聴ページlint NG ({label}): {lint}")
        with open(f"{pages_dir}/{fname}", "w", encoding="utf-8") as f:
            f.write(html_text)
        out[label] = {"page": f"{pages_dir}/{fname}", "rows": len(rows), "kp_rows": len(kp_rows), "lint": lint}
    with open(f"{pages_dir}/index.html", "w", encoding="utf-8") as f:
        f.write(build_index_html(warn_sections))
    return out


def _warn_entry_to_clip_id(entry_key: str):
    """事後試聴リストのentry_key(tts_generation_results.json内のpath)をtimeline rowのclip_idへ対応づける。
    対応するrow(mp3)が無いものはNone(リンクなし表示)。"""
    parts = entry_key.split("/")
    if len(parts) == 2 and parts[0] == "segments":
        return parts[1]
    if len(parts) == 3 and parts[0] == "key_phrases" and parts[2] == "english":
        return f"kp{parts[1]}_en"
    return None


def build_index_html(warn_sections=None) -> str:
    """warn_sections=[(level_label, section_html)]: AUW 委任_03の『事後試聴リスト(PASS_WITH_WARNING)』節(0件でも節を出す)。"""
    extra = "".join(f"<h2>{_esc(lbl)}</h2>{sec_html}" for lbl, sec_html in (warn_sections or []))
    return ("<!doctype html><html lang='ja'><head><meta charset='utf-8'><title>走れメロス 試聴</title></head><body>"
            "<h1>走れメロス 試聴</h1><ul><li><a href='standard.html'>Standard</a></li>"
            "<li><a href='advanced.html'>Advanced</a></li></ul>" + extra + "</body></html>")


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
