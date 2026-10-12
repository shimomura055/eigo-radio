# ============================================================
# er026_family_z_fiction_production_runner_01.py
# 管理ID: FICTION-FAMILY-Z-PRODUCTION-E2E-01 (Phase 1: Production配線の
#         テキスト工程=TTS直前まで)
# ============================================================
# 目的: Family Z(Fiction)専用のProduction entry pointの骨格。
#   Status起点: APPROVED_FOR_PRODUCTION(CURRENT_SPEC.md「Family Z(Fiction)」
#   節 1〜7、Z-1〜Z-4いずれもユーザー確定済み) / WIRING INCOMPLETE
#   (本ファイルはTTS/audio validation/runtime audio evidence未実装)。
#
#   本委任(Phase 1)のスコープ: story_type metadata / rights block /
#   Melos canonical text確定 / Preview・Comment・In One Line / Key Phrase /
#   Connected Speech用segment_id規約整合 / unit test・dry-run / TTS直前
#   までのProduction text成果物作成。
#
#   本委任のスコープ外(実行禁止): TTS / audio validation / runtime audio
#   evidence / listening artifact。stage="tts"/"assemble"はこのファイル内で
#   明示的にNotImplementedErrorとする(読み解決Phase 2の共有TTS入口commit
#   後に別委任で実装予定、ダングリング参照にならないよう呼び出し経路自体は
#   存在させる)。
#
# 並走Agentとの衝突回避のため、以下は「read-only参照(import)のみ」で
# 一切編集しない:
#   - er003_audio_tts_asr_safety.py / er003_v1_n3_01_tts_generate.py /
#     er006_pronunciation_*.py (読み解決Phase 2が編集中)
#   - er019_*.py (Family X Stage 3cが編集中)
#   - docs/pm/PM_GOVERNANCE.md / docs/pm/PM_BRIEF.md (別Agentが編集中)
#   - er012_b_*.py / er013_family_c_*.py (Family A/B/C、Legacy。read-only
#     参照のみ、Z-2方針どおりFamily C既存関数を再利用する)
#
# Family C(er013_family_c_production_01.py)からの再利用(Z-2、
# APPROVED_FOR_PRODUCTION):
#   - plan_story_segments() / build_flat_voice_chunks() / split_into_paragraphs()
#     (Story TTS segmentation原則)
#   - classify_quote_voice_window() (Z-4 Dialogue Voice判定)
#   - generate_family_c_a2_comment() / build_family_c_a2_comment_prompt()
#     (A2 Comment理解ガイド型Contract)
#
# er020_tts_retry_local_rewrite_01.pyは「read-only参照」のみ(編集しない)。
# resolve_narrative_role()/connected_speech_enabled_for()の既存の完全一致
# 文字列判定に対し、Family Z側のsegment_id命名がどこまで整合するか/
# しないかをマッピング表として記録する(§ Connected Speech mapping参照)。
#
# Key Phrase(既存Production経路、未変更): er003_v1_n3_01_scaffold_generate.
# run_key_phrases()を、Family C(A2、Future Story)が実際に呼んでいるのと
# 同じ呼び出しパターンで使う(er013_family_c_episode_trial_10_memory_run.py
# 532行「scaffold.run_key_phrases(article_text, KEY_PHRASE_DIR, ARTICLE_ID,
# "A2", process=None)」と同一パターン)。er003_key_words_production.py
# (retry/gate)・er003_key_words_canonicalization.py(canonicalization)は
# scaffold.run_key_phrases()の内部で未変更のまま呼ばれる。
# ============================================================
from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
import time
import json
import os
import re

import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_iran01_a2_generate as a2gen
import er003_v1_n3_01_scaffold_generate as scaffold
import er006_model_routing_contract_01 as routing
import er013_family_c_production_01 as fam_c
import er018_fiction_external_seed_selection_criteria_trial_02 as trial02
import er020_tts_retry_local_rewrite_01 as tts_role  # read-only参照のみ

MANAGEMENT_ID = "FICTION-FAMILY-Z-PRODUCTION-E2E-01"
THEME_TAG = "FAMILY_Z_FICTION_PRODUCTION_E2E_01"

BUDGET_CAP_JPY = 200.0
BUDGET_WARN_JPY = 150.0


class BudgetGuard:
    """Guardrail: LLM合計コストを追跡し、¥150到達で警告・¥200到達で停止する。
    暴走防止のためのGuardrailであり、Cap到達だけを理由に自動STOPしない
    という予算Cap運用(PM_GOVERNANCE 7-6)とは別に、本委任文が明示した
    ¥200上限(「¥150到達で停止・報告」)をそのまま実装する。"""

    def __init__(self, cap_jpy: float = BUDGET_CAP_JPY, warn_jpy: float = BUDGET_WARN_JPY):
        self.cap_jpy = cap_jpy
        self.warn_jpy = warn_jpy
        self.total_jpy = 0.0
        self.calls: list = []

    def check_before(self, est_jpy: float, label: str) -> None:
        if self.total_jpy + est_jpy > self.cap_jpy:
            raise RuntimeError(
                f"FAMILY_Z_BUDGET_CAP_REACHED: label={label!r} est_jpy={est_jpy} "
                f"current_total={self.total_jpy} cap={self.cap_jpy}")
        if self.total_jpy >= self.warn_jpy:
            print(f"[BudgetGuard][WARN] total_jpy={self.total_jpy} が警告閾値"
                  f"{self.warn_jpy}に到達済み(label={label!r})")

    def add(self, label: str, est_jpy: float) -> None:
        self.total_jpy += est_jpy
        self.calls.append({"label": label, "est_jpy": est_jpy, "running_total_jpy": self.total_jpy})


# ============================================================
# Rights Gate (Z-1, APPROVED_FOR_PRODUCTION, fail-closed)
# ============================================================
RIGHTS_REQUIRED_FIELDS = (
    "author", "author_death_date", "jp_public_domain_basis", "source_url",
    "confirmed_date", "us_copyright_status_record_only", "legal_use_basis",
)


class RightsGateError(RuntimeError):
    pass


def check_rights_gate(rights_block: dict) -> None:
    """Z-1権利Gate(fail-closed)。日本国内PD/適法利用の必須根拠が揃って
    いない場合、text stage自体を停止する(米国PDは記録事項のみで必須
    条件にしない、CURRENT_SPEC.md「Family Z(Fiction)」節 項目3・
    FICTION-FAMILY-Z-RIGHTS-RECHECK-01_REPORT.md §6のユーザー決定どおり)。"""
    missing = [f for f in RIGHTS_REQUIRED_FIELDS if not rights_block.get(f)]
    if missing:
        raise RightsGateError(
            f"FAMILY_Z_RIGHTS_GATE_FAILED: missing_fields={missing}")


# Melosのrights block(FICTION-FAMILY-Z-RIGHTS-RECHECK-01_REPORT.md §6の
# ユーザー決定、および同REPORT §1/recon §1のURAA分析結果を逐語転記。
# 推測で埋めない)。
MELOS_RIGHTS_BLOCK = {
    "author": "太宰治 (Osamu Dazai)",
    "author_death_date": "1948-06-13",
    "jp_public_domain_basis": (
        "日本の著作権保護期間は、2018年末のTPP11整備法による70年化以前は"
        "死後50年だった(1970年法改正)。太宰の没後50年=1998年末で日本の"
        "保護は満了しており、2018年末の70年化はこの1999〜2018年に既に"
        "切れていた作品には遡及しない。太宰の作品は1999-01-01付けで"
        "日本において確定的にパブリックドメイン("
        "FICTION-FAMILY-Z-RIGHTS-RECHECK-01_REPORT.md §1、"
        "en.wikipedia.org/wiki/Copyright_law_of_Japan、"
        "確認2026-09-26、HTTP 200)。Aozora Bunkoが全文ダウンロードファイル"
        "を公開していることも、著作権消滅済み作品のみをホストするAozoraの"
        "運用方針と整合する。"
    ),
    "source_url": "https://www.aozora.gr.jp/cards/000035/files/1567_14913.html",
    "source_card_url": "https://www.aozora.gr.jp/cards/000035/card1567.html",
    "confirmed_date": "2026-09-26",
    "us_copyright_status_record_only": (
        "記録事項(必須条件ではない、日本国内向けサービスのため)。走れメロス"
        "(1940年発表)は1996-01-01時点で日本において保護期間中だったため、"
        "URAA(Uruguay Round Agreements Act)により米国著作権が回復し、"
        "発行日から95年=2035年末まで米国で保護される可能性が高い"
        "(2036年に米国PD化する可能性が高い)。Cornell University Library "
        "\"Copyright Term and the Public Domain in the United States\" "
        "チャート(https://copyright.cornell.edu/publicdomain、確認"
        "2026-09-26、HTTP 200)に基づく判定。最終的な法的判断ではない"
        "(recon_family_z_production_e2e_01.md §1参照)。"
    ),
    "legal_use_basis": (
        "ユーザー正式決定(2026-09-26、FICTION-FAMILY-Z-RIGHTS-RECHECK-01_"
        "REPORT.md §6): 「日本人向け・日本国内向けサービスであるため、"
        "Family Zの権利条件は以下で正式採用: (1)日本国内でPublic Domain、"
        "または日本国内で適法に利用可能であることを必須条件とする "
        "(2)米国PDは必須条件にしない (3)海外向け配信・提供を将来行う場合"
        "のみ、その対象法域のrights確認を追加する (4)原作がPDでも、現代の"
        "第三者翻訳・英訳・挿絵等は別著作物として扱い、権利未確認のものは"
        "流用しない (5)Family Zのadaptationは、確認済み原文/正式Seedから"
        "自前生成する。走れメロスは日本でPD確認済みのため初回Family Z E2E"
        "対象として継続、差し替え不要。本rights方針はAPPROVED_FOR_"
        "PRODUCTION。」"
    ),
    "gate_reference": "FICTION-FAMILY-Z-RIGHTS-RECHECK-01_REPORT.md §6 (2026-09-26)",
}


# ============================================================
# Story Registry (Phase 1では"melos"のみ)
# ============================================================
TRIAL_SEED_DIR = (
    "er018_output/fiction_external_seed_selection_criteria_trial_02/"
    "stories/03_japanese_lit_2"
)

STORY_REGISTRY = {
    "melos": {
        "story_type": "literature",
        "topic_title": "The Three-Day Promise",
        "japanese_title_text": "走れメロス(The Three-Day Promise)",
        # 委任_05: Std日本語タイトルclipのTTS用テキスト(括弧付き英題は日本語TTSに読ませない)。表示用は上記japanese_title_text。
        "japanese_title_tts": "走れメロス",
        "trial_seed_dir": TRIAL_SEED_DIR,
        "rights_block": MELOS_RIGHTS_BLOCK,
        # Z-4 Dialogue Voice適用計画(plan only、TTS未実行)。narrator=Aoede、
        # 登場人物台詞=Erinome/Charon等というCURRENT_SPEC.md「Family Z
        # (Fiction)」節 Z-4追記の参照先をそのまま採用(新しいVoice仕様を
        # 作らない)。
        "voice_keywords": {
            "selinuntius": ["selinuntius"],
            "dionysius": ["dionysius", "ruler"],
        },
        "voice_tts_names_plan": {
            "narrator": "Aoede",
            "selinuntius": "Erinome",
            "dionysius": "Charon",
        },
    },
}


# ============================================================
# Canonical text: 受入条件照合 + 人物名ルール復元(item 2)
# ============================================================
ACCEPT_WORD_RANGE = (280, 420)  # recon根拠: FICTION-EXTERNAL-SEED-SELECTION-
                                 # CRITERIA-TRIAL-02_REPORT.md §2 Gate3


def load_trial_seed_and_story(story_key: str) -> dict:
    cfg = STORY_REGISTRY[story_key]
    seed_dir = cfg["trial_seed_dir"]
    with open(f"{seed_dir}/seed.json", encoding="utf-8") as f:
        seed = json.load(f)
    with open(f"{seed_dir}/story.md", encoding="utf-8") as f:
        raw_trial_text = f.read()
    return {"seed": seed, "raw_trial_text": raw_trial_text}


def strip_markdown_title(raw_text: str) -> tuple:
    """先頭の `### Title` 見出し行を分離し、(title, body)を返す。無ければ
    titleはNone。"""
    m = re.match(r"^###\s+(.+?)\s*\n\n?", raw_text)
    if not m:
        return None, raw_text.strip() + "\n"
    return m.group(1).strip(), raw_text[m.end():].strip() + "\n"


def check_word_count(body_text: str) -> tuple:
    words = body_text.split()
    n = len(words)
    ok = ACCEPT_WORD_RANGE[0] <= n <= ACCEPT_WORD_RANGE[1]
    return ok, n


def check_character_name_rule(body_text: str) -> tuple:
    """[SUPERSEDED 2026-10-12 / 委任_05] 新経路(E2E stage)・run_text_stage は
    er061_family_z_semantic_validator_01.validate_semantic_preservation へ置換済み
    (DECISION_LOG 2026-10-12: 名前の登場有無は判定せず意味保持で判定)。本関数は
    Phase 1 のtest互換のためだけに残置する(新規呼出禁止)。
    CURRENT_SPEC.md「Family Z(Fiction)」節 項目2(人物名変更・不要な
    設定変更をしない)の照合。走れメロス原文の主要人物3名(Melos/
    Selinuntius/Dionysius)のうち、Melos以外の名前が本文から失われている
    場合はFAILとする(役割語[his friend/the ruler]だけへの置換は、
    脇筋人物の「登場人物整理」の範囲を超える人物名の変更にあたる)。"""
    missing = []
    for name in ("Selinuntius", "Dionysius"):
        if name.lower() not in body_text.lower():
            missing.append(name)
    return (len(missing) == 0), missing


def restore_character_names(body_text: str) -> str:
    """[SUPERSEDED 2026-10-12 / 委任_05] 上記 check_character_name_rule と同様に残置のみ
    (新経路・run_text_stageは使わない)。
    人物名ルール(item 2)を満たすための最小限の復元編集。

    LLMによる創作的な書き直しではなく、決定的(deterministic)なテキスト
    置換で行う: 理由は、これは「創作」ではなく既存SSOTルールへの機械的な
    適合(初出時の役割語[the ruler/his friend]に原作人物名を人称同格で
    付記するだけ)であり、決定的処理の方が(a)監査可能($0、diffがそのまま
    証跡になる)、(b)LLM再生成に伴う意図しない副作用[語数変動・トーン変化・
    A2レベル逸脱等]のリスクがない、ため。委任文の「(LLM、¥)」という
    括弧書きの想定とは異なる手段を採ったので、その理由をREPORTへ明記する
    (無断の仕様変更ではなく、あくまでテキスト内容自体は委任文item 2の
    既存ルールへ機械的に適合させるだけであることに注意)。
    他の内容(語数・出来事の順序・A2レベル・段落構成)は一切変更しない。
    """
    text = body_text
    # 1) 統治者の初出("the ruler was afraid of enemies")に同格でDionysiusを付記
    text, n1 = re.subn(
        r"\bthe ruler was afraid of enemies\b",
        "the ruler, Dionysius, was afraid of enemies",
        text, count=1)
    # 2) 友人の初出("Melos's friend stepped forward")に同格でSelinuntiusを付記
    text, n2 = re.subn(
        r"Melos’s friend stepped forward",
        "Melos’s friend, Selinuntius, stepped forward",
        text, count=1)
    if n2 == 0:
        # スマートクォート差異のフォールバック(ASCIIアポストロフィ版)
        text, n2 = re.subn(
            r"Melos's friend stepped forward",
            "Melos's friend, Selinuntius, stepped forward",
            text, count=1)
    if n1 == 0 or n2 == 0:
        raise RuntimeError(
            f"FAMILY_Z_NAME_RESTORE_ANCHOR_NOT_FOUND: ruler_edit={n1} "
            f"friend_edit={n2}(本文の初出フレーズが想定と異なるため、"
            "自動編集の対象箇所が見つからない。手動確認が必要)。")
    return text


def resolve_canonical_text(story_key: str) -> dict:
    """recon記載の受入条件(語数・レベル・構造・Family Z Contract)と照合し、
    満たすならTrialテキストをsha256付きでcanonicalとして採用、満たさない
    項目(人物名ルール)があれば既存SSOT範囲内でのみ最小修正する。"""
    loaded = load_trial_seed_and_story(story_key)
    title, body = strip_markdown_title(loaded["raw_trial_text"])
    word_ok, word_count = check_word_count(body)
    name_ok, missing_names = check_character_name_rule(body)

    trial_sha256 = hashlib.sha256(body.encode("utf-8")).hexdigest()
    edits = []
    if not name_ok:
        body = restore_character_names(body)
        edits.append({
            "reason": "FAMILY_Z_CONTRACT_ITEM_2_NAME_RESTORATION",
            "missing_names_before_edit": missing_names,
            "method": "deterministic_text_substitution_no_llm",
        })
        # 再照合
        name_ok, missing_names = check_character_name_rule(body)
        word_ok, word_count = check_word_count(body)

    final_sha256 = hashlib.sha256(body.encode("utf-8")).hexdigest()
    return {
        "title": title,
        "body": body,
        "word_count": word_count,
        "word_count_ok": word_ok,
        "character_name_rule_ok": name_ok,
        "missing_names_after": missing_names,
        "trial_source_path": f"{STORY_REGISTRY[story_key]['trial_seed_dir']}/story.md",
        "seed_title": loaded["seed"]["title"],
        "trial_sha256": trial_sha256,
        "final_sha256": final_sha256,
        "edits": edits,
        "seed": loaded["seed"],
    }


def resolve_canonical_text_v2(story_key: str) -> dict:
    """委任_05: run_text_stage 用の新canonical解決。旧人物名ルール(restore_character_names)は
    使わず、er061 第1層(決定論, API 0)で意味保持を検査する(Trial本文は改変しない)。
    第1層FAILはSTOP(自動で通さない)。"""
    import er061_family_z_semantic_validator_01 as v61
    loaded = load_trial_seed_and_story(story_key)
    title, body = strip_markdown_title(loaded["raw_trial_text"])
    word_ok, word_count = check_word_count(body)
    anchors = v61.load_anchors()
    layer1 = v61.layer1_check(body, anchors)
    sha = hashlib.sha256(body.encode("utf-8")).hexdigest()
    return {
        "title": title, "body": body, "word_count": word_count, "word_count_ok": word_ok,
        "layer1_verdict": layer1["verdict"], "layer1": layer1, "edits": [],
        "trial_source_path": f"{STORY_REGISTRY[story_key]['trial_seed_dir']}/story.md",
        "seed_title": loaded["seed"]["title"], "trial_sha256": sha, "final_sha256": sha,
        "seed": loaded["seed"],
    }


# ============================================================
# Segment plan (Z-2 reuse) + Connected Speech segment_id mapping (§7)
# ============================================================
def _known_gap_status() -> str:
    """委任_03(er020 _FAMILY_Z_STORY_CLIP_PATTERN追加)で resolve_narrative_role が
    full_story_part{1-3}_c{k} をFULL_STORYと解決するようになった。実resolverで確認する。"""
    ids = ["full_story_part1_c1", "full_story_part2_c7", "full_story_part3_c12"]
    ok = all(tts_role.resolve_narrative_role(i) == "FULL_STORY" and tts_role.connected_speech_enabled_for(i)
             for i in ids)
    if ok:
        return ("RESOLVED_BY_ER020_FAMILY_Z_CLIP_PATTERN(委任_03): full_story_part[1-3]_c[0-9]+ が"
                "FULL_STORY・Connected Speech=True。新経路のclip idはer062 plan_clipsが決定する。"
                "本Phase 1 mappingの『position>3は未解決』は旧命名(story_XXX)の事実記録として残置。")
    return "OPEN_UNRESOLVED(resolve_narrative_role が Family Z clip id を解決しない)"


def build_segment_plan(body_text: str, voice_keywords: dict) -> dict:
    paragraphs = fam_c.split_into_paragraphs(body_text)
    flat = fam_c.build_flat_voice_chunks(paragraphs, voice_keywords)
    segments = fam_c.plan_story_segments(flat)
    reconstructed = fam_c.reconstruct_article_from_segments(segments, paragraphs)
    reconstruction_ok = (reconstructed == body_text)

    mapping_rows = []
    for i, seg in enumerate(segments, start=1):
        raw_id = seg["id"]  # "story_XXX"(Family C既定の命名、resolverと不一致)
        proposed_id = f"full_story_part{i}" if i <= 3 else raw_id
        role = tts_role.resolve_narrative_role(proposed_id)
        connected_speech_ok = tts_role.connected_speech_enabled_for(proposed_id)
        mapping_rows.append({
            "position": i,
            "raw_segment_id": raw_id,
            "voice": seg["voice"],
            "word_count": seg["word_count"],
            "proposed_segment_id": proposed_id,
            "resolved_role": role,
            "connected_speech_enabled": connected_speech_ok,
        })

    narrator_positions = [r["position"] for r in mapping_rows if r["voice"] == "narrator"]
    dialogue_positions = [r["position"] for r in mapping_rows if r["voice"] != "narrator"]
    known_gap = None
    known_gap_status = _known_gap_status()
    if len(segments) > 3 and not known_gap_status.startswith("RESOLVED"):
        known_gap = (
            f"FAMILY_Z_SEGMENT_ID_GAP(known, recon §6/§8-1 既知課題): "
            f"本Storyは{len(segments)}segment(narrator={len(narrator_positions)}件 "
            f"positions={narrator_positions}, dialogue_voice="
            f"{len(dialogue_positions)}件 positions={dialogue_positions})に分割される"
            f"が、er020_tts_retry_local_rewrite_01.resolve_narrative_role()は"
            "\"full_story_part1/2/3\"の3スロットの完全一致文字列しか"
            "FULL_STORYロールとして認識しない。position 4以降"
            "(narrator/dialogue voice問わず)はConnected Speechの適用対象外"
            "のまま(raw_segment_idのまま)であり、これは新しい設計判断では"
            "なくresolve_narrative_role()の既存の完全一致判定をread-only参照"
            "した結果そのままの事実。resolver側にFamily Z用パターンを追加する"
            "か(recon §8-2選択肢(b))、Family Z側のsegment_id命名を作り直すか"
            "(選択肢(a))は本委任のスコープ外の判断であり、Fable/ユーザー判断"
            "を要する。")

    non_narrator_in_first_three = [
        r["position"] for r in mapping_rows if r["position"] <= 3 and r["voice"] != "narrator"
    ]
    mapping_caveat = None
    if non_narrator_in_first_three:
        mapping_caveat = (
            f"CAVEAT: proposed_segment_id(full_story_part1/2/3)はposition"
            "1〜3に機械的・位置基準で割り当てただけであり、voice(誰が話すか)"
            f"は考慮していない。今回のrunでは position={non_narrator_in_first_three}"
            "がnarratorではなくdialogue voice(短い引用符区間)であり、'Full "
            "Story narration'という本来のFULL_STORYロールの意味とは厳密には"
            "ズレる。これは新しい判断ではなく、事実の記録(このrunの実際の"
            "分割結果)であり、Fable/ユーザー判断を要する論点として"
            "known_gapと合わせて報告する。")

    return {
        "segments": segments,
        "reconstruction_matches_canonical_text": reconstruction_ok,
        "segment_id_role_map": mapping_rows,
        "known_gap": known_gap,
        "known_gap_status": known_gap_status,
        "mapping_caveat_voice_mismatch": mapping_caveat,
    }


# 固定segment(Preview/Comment/Topic intro/In One Line)はresolverの完全
# 一致文字列とそのまま整合する(Family Aの既存命名をそのまま踏襲するため)。
FIXED_SEGMENT_IDS = ("topic_intro", "preview", "comment_1", "in_one_line")


def build_fixed_segment_role_map() -> list:
    rows = []
    for seg_id in FIXED_SEGMENT_IDS:
        rows.append({
            "segment_id": seg_id,
            "resolved_role": tts_role.resolve_narrative_role(seg_id),
            "connected_speech_enabled": tts_role.connected_speech_enabled_for(seg_id),
        })
    return rows


# ============================================================
# Preview / Comment / In One Line 生成(Z-2/Z-3、実LLM呼び出し)
# ============================================================
# Family CのA2 Comment理解ガイド型Contract(banned phrase等)を再利用した
# Preview prompt。Family CのFamily C production runnerはPreview文面の
# content authoring自体を「スコープ外(reuse_from必須)」としており、
# Preview文面を実際に生成する関数はFamily Cに存在しないため、Comment
# Contractの禁止語句リスト・understanding-guide方針を流用しつつ、Family Z
# 用に新規のprompt文言のみを本ファイル内に定義する(fam_c本体は編集しない、
# import参照のみ)。
_FAMILY_Z_PREVIEW_ROLE_JA = (
    "あなたは英語学習者向け音声番組で、これから始まる短い物語(A2レベル、"
    "Public Domain文学のリライト)の前に置く短い日本語Previewを書く担当"
    "です。雰囲気作りの声かけ(「聞いてみましょう」等)ではなく、状況設定"
    "(誰が・どんな状況か)を2〜3文・80〜110字程度で簡潔に紹介してください。"
    "結末や物語の山場(主人公が最終的にどうなるか)には触れないでください。"
    "本文にない設定・事実を追加しないでください。"
    + fam_c._BANNED_PHRASES_INSTRUCTION
)


def build_family_z_preview_prompt() -> str:
    return _FAMILY_Z_PREVIEW_ROLE_JA


# In One Line(Z-3): 既存News Writer prompt item 4
# (er003_v1_n3_01_articles_generate.py 167行「In One Line相当の結び
# (「## In one line…」のような見出しの後に1〜2文の結び)」)を、Point構造
# への言及を除去して最小変更流用する。
_FAMILY_Z_IN_ONE_LINE_ROLE_EN = (
    "You are writing the closing \"In One Line\" summary for a short "
    "English-learner audio story (A2 level, a Public Domain literature "
    "adaptation). Write 1-2 sentences in English that capture what the "
    "story's ending means, in the same spirit as a closing remark after "
    "a short story. Do not introduce new facts that are not in the story. "
    "Do not use meta-narration phrases like \"Let's listen\" or "
    "\"What do you think happens next?\"."
)


def build_family_z_in_one_line_prompt() -> str:
    return _FAMILY_Z_IN_ONE_LINE_ROLE_EN


def generate_family_z_preview(client, budget: BudgetGuard, article_text: str,
                               llm_call_cost_jpy: float = 3.0) -> dict:
    label = "family_z_preview_llm_attempt1"
    budget.check_before(llm_call_cost_jpy, label)
    context = f"【物語全文(参考、新しい設定・事実の追加禁止)】\n{article_text}"
    with trial02.cl.logging_context(THEME_TAG, "preview"):
        result = a2gen.run_support_text(client, build_family_z_preview_prompt(), context)
    budget.add(label, llm_call_cost_jpy)
    if result.get("status") != "OK":
        raise RuntimeError(f"FAMILY_Z_PREVIEW_GENERATION_FAILED: {result}")
    return {"text": result["text"].strip(), "prompt": build_family_z_preview_prompt()}


_IN_ONE_LINE_DEVELOPER_MESSAGE = (
    "You write a one-line closing remark in English for a short English-"
    "learner audio story. Always respond in English (this is different "
    "from the Japanese Listening Support manuscripts used elsewhere in "
    "this program)."
)


def generate_family_z_in_one_line(client, budget: BudgetGuard, article_text: str,
                                   llm_call_cost_jpy: float = 3.0, max_attempts: int = 2) -> dict:
    """In One Lineは英語(Family AのIn One Line同様、記事本文と同じ言語)。
    a2gen.run_support_text()はSUPPORT_DEVELOPER_MESSAGEが
    「日本語のListening Support原稿を作成してください。」に固定されており
    (JA Comment/Preview専用)、In One Lineへ流用すると英語指示を無視して
    日本語で返ってくることを実際に確認した(runtime evidence、初回実行時に
    日本語出力を検出したため本関数へ差し替えた)。そのため、In One Lineのみ
    e_axis.generate_story()と同型のraw client呼び出し(英語developer
    message)を使う(a2genのJA固定Contractは一切変更しない)。"""
    label = "family_z_in_one_line_llm_attempt1"
    budget.check_before(llm_call_cost_jpy, label)
    prompt = build_family_z_in_one_line_prompt() + (
        f"\n\n[Full story text, for reference only, do not add new facts]\n{article_text}")
    model = routing.require_model_or_override("A2_WRITER", routing.WRITER_MODEL)
    attempts = []
    with trial02.cl.logging_context(THEME_TAG, "in_one_line"):
        for attempt in range(1, max_attempts + 1):
            response = client.responses.create(
                model=model, reasoning={"effort": "low"},
                input=[
                    {"role": "developer", "content": _IN_ONE_LINE_DEVELOPER_MESSAGE},
                    {"role": "user", "content": prompt},
                ],
            )
            text = (response.output_text or "").strip()
            is_ascii_dominant = bool(text) and (sum(c.isascii() for c in text) / len(text)) > 0.9
            attempts.append({"attempt": attempt, "text": text, "is_ascii_dominant": is_ascii_dominant})
            if is_ascii_dominant:
                break
    budget.add(label, llm_call_cost_jpy)
    final = attempts[-1]
    if not final["text"] or not final["is_ascii_dominant"]:
        raise RuntimeError(f"FAMILY_Z_IN_ONE_LINE_GENERATION_FAILED(not English): {attempts}")
    return {"text": final["text"], "prompt": prompt, "attempts": attempts, "model": model}


def generate_family_z_comment_1(client, budget: BudgetGuard, article_text: str,
                                 llm_call_cost_jpy: float = 3.0) -> dict:
    """Z-2: Family C既存のA2 Comment理解ガイド型Contractをそのまま再利用
    (fam_c.generate_family_c_a2_comment、内部でcheck_a2_comment_quality
    によるretryループを内包)。Comment 1(物語冒頭前)のみ生成する(本Story
    はFull Story 2part程度の短編のため、Family Cのcomment_1〜3全件は必須
    ではない。Comment 2/3が必要かはsegment_plan確定後に判断できるため、
    ここではcomment_1のみ)。"""
    content_facts = (
        "小さな王国の統治者Dionysiusが、疑いだけで人を処刑してしまう恐れ深い"
        "人物であること、羊飼いMelosがその不正を直接批判したことで死刑を"
        "宣告されること、Melosには妹の結婚式に出るための3日間の猶予が与え"
        "られ、その間は友人Selinuntiusが人質として残ることになったこと。"
    )
    label = "family_z_a2_comment_1"
    budget.check_before(llm_call_cost_jpy, label)
    with trial02.cl.logging_context(THEME_TAG, "comment_1"):
        result = fam_c.generate_family_c_a2_comment(
            client, 1, article_text, content_facts,
            budget=None,  # fam_c内部budgetは使わず、本ファイル側BudgetGuardで一元管理
            label_prefix="family_z_a2_comment", llm_call_cost_jpy=llm_call_cost_jpy,
        )
    budget.add(label, llm_call_cost_jpy)
    return result


# ============================================================
# story_type metadata (item 5)
# ============================================================
STORY_TYPE_FIXED_INTRO_TEXT = {
    "literature": None,
    "real_story": "This is a true story.",
    "true_crime": "This is a true crime story.",
}

STORY_TYPE_UI_LABEL = {
    "literature": None,
    "real_story": "REAL STORY",
    "true_crime": "TRUE CRIME",
}


def build_story_type_metadata(story_type: str) -> dict:
    if story_type not in STORY_TYPE_FIXED_INTRO_TEXT:
        raise RuntimeError(f"FAMILY_Z_UNKNOWN_STORY_TYPE: {story_type!r}")
    return {
        "story_type": story_type,
        "fixed_audio_intro_text": STORY_TYPE_FIXED_INTRO_TEXT[story_type],
        "ui_label": STORY_TYPE_UI_LABEL[story_type],
    }


# ============================================================
# Stage: text (Phase 1のメイン成果物)
# ============================================================
def out_dir_for(slug: str, run: str) -> str:
    return f"er026_output/family_z_production_e2e_01/{slug}/{run}"


def run_text_stage(story_key: str, slug: str, run: str, dry_run: bool = False) -> dict:
    cfg = STORY_REGISTRY[story_key]
    check_rights_gate(cfg["rights_block"])

    # 委任_05: 旧人物名検査(旧名前ルール関数。superseded)をer061へ置換。
    canonical = resolve_canonical_text_v2(story_key)
    if not canonical["word_count_ok"]:
        raise RuntimeError(
            f"FAMILY_Z_WORD_COUNT_OUT_OF_RANGE: word_count={canonical['word_count']} "
            f"accept_range={ACCEPT_WORD_RANGE}")
    if canonical["layer1_verdict"] == "FAIL":
        raise RuntimeError(
            f"FAMILY_Z_SEMANTIC_LAYER1_FAIL: {[h['id'] for h in canonical['layer1']['hard_fails']]}")

    segment_plan = build_segment_plan(canonical["body"], cfg["voice_keywords"])
    if not segment_plan["reconstruction_matches_canonical_text"]:
        raise RuntimeError("FAMILY_Z_SEGMENT_RECONSTRUCTION_MISMATCH: "
                            "segments do not reconstruct canonical text exactly")

    fixed_role_map = build_fixed_segment_role_map()
    story_type_meta = build_story_type_metadata(cfg["story_type"])

    plan_summary = {
        "management_id": MANAGEMENT_ID,
        "story_key": story_key,
        "canonical_text": {
            "title": canonical["title"],
            "word_count": canonical["word_count"],
            "trial_sha256": canonical["trial_sha256"],
            "final_sha256": canonical["final_sha256"],
            "edits": canonical["edits"],
            "semantic_layer1_verdict": canonical["layer1_verdict"],
        },
        "story_type_metadata": story_type_meta,
        "rights_block": cfg["rights_block"],
        "segment_id_role_map": segment_plan["segment_id_role_map"],
        "fixed_segment_role_map": fixed_role_map,
        "known_gap": segment_plan["known_gap"],
        "mapping_caveat_voice_mismatch": segment_plan["mapping_caveat_voice_mismatch"],
        "dialogue_voice_plan": {
            "voice_keywords": cfg["voice_keywords"],
            "voice_tts_names_plan": cfg["voice_tts_names_plan"],
            "note": "PLAN ONLY, TTS未実行。narrator=Aoede/Selinuntius=Erinome/"
                     "Dionysius=Charon(CURRENT_SPEC.md Family Z(Fiction)節 Z-4"
                     "追記の参照先をそのまま採用、新しいVoice仕様は作らない)。",
        },
        "tts_stage": "IMPLEMENTED(委任_05): 新E2E stage経路(E2E_STAGES)を使う。本run_text_stageはPhase 1互換。",
    }

    if dry_run:
        # 副作用ゼロ契約: ファイル書き込み・API呼び出しを一切行わない。
        plan_summary["preview"] = None
        plan_summary["comment_1"] = None
        plan_summary["in_one_line"] = None
        plan_summary["dry_run"] = True
        return plan_summary

    budget = BudgetGuard()
    client = vfl01.get_client()
    log_path = f"{out_dir_for(slug, run)}/raw_usage_log.jsonl"
    os.makedirs(out_dir_for(slug, run), exist_ok=True)
    trial02.cl.install(log_path)

    preview = generate_family_z_preview(client, budget, canonical["body"])
    comment_1 = generate_family_z_comment_1(client, budget, canonical["body"])
    in_one_line = generate_family_z_in_one_line(client, budget, canonical["body"])

    plan_summary["preview"] = preview
    plan_summary["comment_1"] = comment_1
    plan_summary["in_one_line"] = in_one_line
    plan_summary["dry_run"] = False
    plan_summary["budget"] = {"total_jpy_est": budget.total_jpy, "calls": budget.calls}

    out_dir = out_dir_for(slug, run)
    os.makedirs(out_dir, exist_ok=True)
    with open(f"{out_dir}/article.md", "w", encoding="utf-8") as f:
        f.write(canonical["body"])
    with open(f"{out_dir}/preview.txt", "w", encoding="utf-8") as f:
        f.write(preview["text"] + "\n")
    with open(f"{out_dir}/in_one_line.txt", "w", encoding="utf-8") as f:
        f.write(in_one_line["text"] + "\n")
    with open(f"{out_dir}/comment_1.json", "w", encoding="utf-8") as f:
        json.dump(comment_1, f, ensure_ascii=False, indent=2)
    segment_plan_serializable = dict(segment_plan)
    segment_plan_serializable["segments"] = [
        {k: v for k, v in s.items() if k != "paragraph_contributions"} for s in segment_plan["segments"]
    ]
    with open(f"{out_dir}/segment_plan.json", "w", encoding="utf-8") as f:
        json.dump(segment_plan_serializable, f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/article_config.json", "w", encoding="utf-8") as f:
        json.dump(plan_summary, f, ensure_ascii=False, indent=2)

    cost = compute_actual_cost_jpy(log_path)
    with open(f"{out_dir}/cost.json", "w", encoding="utf-8") as f:
        json.dump({"budget_estimate": plan_summary["budget"], "actual_usage": cost},
                   f, ensure_ascii=False, indent=2)

    return plan_summary


def _load_model_pricing(model: str) -> dict:
    """WIRING-01 Phase 2(M2): 指定model(routing由来)のinput/cached_input/
    output単価をpricing_snapshot.jsonから引く。無ければPricingNotFoundError。"""
    with open(trial02.PRICING_SNAPSHOT_PATH, encoding="utf-8") as f:
        snapshot = json.load(f)
    pricing = {}
    for entry in snapshot["prices"]:
        if entry.get("provider") == "openai" and entry.get("model") == model \
                and entry.get("tier", "Standard") == "Standard":
            pricing[entry["meter"]] = entry["price"]
    for meter in ("input_tokens", "cached_input_tokens", "output_tokens"):
        if meter not in pricing:
            raise routing.PricingNotFoundError(
                f"[STOP] 単価未登録model: openai/{model} meter={meter}")
    return pricing


def compute_actual_cost_jpy(log_path: str) -> dict:
    """trial02.compute_cost_jpy()と同一ロジックだが、THEME_TAGを本runner
    (FAMILY_Z_FICTION_PRODUCTION_E2E_01)向けに差し替えたもの(単価はrecordの
    model_idごとにpricing_snapshotから引く。WIRING-01 Phase 2 M2)。"""
    if not os.path.exists(log_path):
        return {"total_usd": 0.0, "total_jpy": 0.0, "record_count": 0}
    # WIRING-01 Phase 2(M2): 5.6固定の単価読込/フィルタをrouting由来modelへ。
    # OpenAI recordのmodel単価がpricing_snapshotに無ければPricingNotFoundError
    # (費用が無言で0円になるのを防ぐ、fail-closed)。非OpenAI recordは従来どおり対象外。
    pricing_by_model = {}
    total_usd = 0.0
    record_count = 0
    with open(log_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if rec.get("theme") != THEME_TAG:
                continue
            record_count += 1
            if not rec.get("success", True):
                continue
            model_id = rec.get("model_id")
            if rec.get("provider", "openai") != "openai" or not model_id:
                continue
            if model_id not in pricing_by_model:
                pricing_by_model[model_id] = _load_model_pricing(model_id)
            pricing = pricing_by_model[model_id]
            input_tokens = rec.get("input_tokens") or 0
            cached = rec.get("cached_input_tokens") or 0
            output_tokens = rec.get("output_tokens") or 0
            non_cached_input = max(input_tokens - cached, 0)
            total_usd += (non_cached_input / 1_000_000) * pricing["input_tokens"]
            total_usd += (cached / 1_000_000) * pricing["cached_input_tokens"]
            total_usd += (output_tokens / 1_000_000) * pricing["output_tokens"]
    return {"total_usd": round(total_usd, 6), "total_jpy": round(total_usd * trial02.USD_JPY, 2),
            "record_count": record_count}


# ============================================================
# Stage: keyphrase (既存Production経路、未変更)
# ============================================================
def run_keyphrase_stage(story_key: str, slug: str, run: str, dry_run: bool = False) -> dict:
    if dry_run:
        return {"dry_run": True, "note": "Key Phrase stageはdry-runでは実行しない(¥0保証)。"}
    out_dir = out_dir_for(slug, run)
    article_path = f"{out_dir}/article.md"
    if not os.path.exists(article_path):
        raise RuntimeError(
            "FAMILY_Z_KEYPHRASE_REQUIRES_TEXT_STAGE_FIRST: "
            f"{article_path} が存在しません(先に--stage textを実行してください)。")
    with open(article_path, encoding="utf-8") as f:
        article_text = f.read()
    kp_dir = f"{out_dir}/key_phrases"
    os.makedirs(kp_dir, exist_ok=True)
    # 実usage(gpt-5.6-sol、Key Phrase既定model)の記録用(¥計算はsol単価を
    # 未実装のためrecord_countのみ、既知の欠落として報告する)。
    kp_log_path = f"{kp_dir}/raw_usage_log.jsonl"
    trial02.cl.install(kp_log_path)
    # Family C(A2、Future Story)が実際に呼んでいるのと同一の既存Production
    # 入口・同一パターン(er013_family_c_episode_trial_10_memory_run.py 532行)。
    with trial02.cl.logging_context(THEME_TAG, "key_phrases"):
        result = scaffold.run_key_phrases(article_text, kp_dir, f"family_z_{slug}", "A2", process=None)
    with open(f"{kp_dir}/family_z_keyphrase_stage_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    return result


# ============================================================
# E2E統合 (委任_05, FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01)
# ============================================================
# Fable確定方針(委任_05)の実装。実呼出は--mode realのみ(委任_06で実行)。--mode dry-runは副作用ゼロ、
# --mode mockは全LLM/TTS/ASR/KPを内蔵ダミーに固定する(実API混入防止。04Bの事故再発防止)。
# stage順: seed_check -> writer(r0->r1->r2) -> validate_b1b -> std_adjust -> validate_a2 -> plan ->
#   support -> kp -> tts_b1b/tts_a2 -> provision_shell -> gate -> assemble -> pages -> page_verify
# 04A/04B/04C module(er061/er062/er063)の内部は変更しない(er063のみ、KP第3segment英語解説のため最小拡張)。
import contextlib
import dataclasses
import types

E2E_MANAGEMENT_ID = "FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01"
E2E_THEME_TAG = "FAMILY_Z_MELOS_SOL_PRODUCTION_E2E_01"
E2E_RUN_ROOT = "er026_output/family_z_production_e2e_01"
E2E_PAGES_DIR = "user_test/family_z_melos_01"
E2E_APPROVED_BUDGET_MAX_JPY = 300.0     # 方針8: --approved-budget-jpy 300
E2E_WARN_THRESHOLD_JPY = 200.0          # 方針8: 警告閾値(超過見込みで新規API呼出前にSTOP)
E2E_DEFAULT_RUN = "run_e2e_01"
LEVELS = ("b1b", "a2")                  # b1b=Advanced, a2=Standard(出力dir名のみ。ページにはラベルを出さない)
E2E_STAGES = ("seed_check", "writer", "validate_b1b", "std_adjust", "validate_a2", "plan", "support", "kp",
              "tts_b1b", "tts_a2", "provision_shell", "gate", "assemble", "pages", "page_verify")
E2E_STAGE_EST_JPY = {"writer": 22.0, "validate_b1b": 2.5, "std_adjust": 8.0, "validate_a2": 2.5, "plan": 2.0,
                     "support": 8.0, "kp": 10.0, "tts_b1b": 40.0, "tts_a2": 40.0}
E2E_TTS_CLIP_EST_JPY = 1.0              # clip単位guard(LRが走ると+約1円。事後は次clipのguardで検知)
E2E_KP_EXTRA_REGEN_NAMES = ("kp_expl_b1b",)
LEGACY_STAGES = ("text", "keyphrase")


class FamilyZE2EStop(RuntimeError):
    """E2E統合のSTOP(自動で通さない・自動再生成しない)。"""


class FamilyZBudgetStop(FamilyZE2EStop):
    pass


class FamilyZValidatorStop(FamilyZE2EStop):
    pass


class FamilyZStdParagraphStop(FamilyZE2EStop):
    pass


class FamilyZDialogueOtherStop(FamilyZE2EStop):
    pass


class FamilyZTtsClipFailedStop(FamilyZE2EStop):
    pass


_MODS = None


def _m():
    """er061/er062/er063の遅延import(Phase 1 testの軽量importを保つ)。"""
    global _MODS
    if _MODS is None:
        import er061_family_z_semantic_validator_01 as v61
        import er062_family_z_structure_01 as st
        import er062_family_z_writer_01 as w62
        import er063_family_z_audio_01 as a63
        _MODS = types.SimpleNamespace(v61=v61, st=st, w62=w62, a63=a63)
    return _MODS


# ------------------------------------------------------------
# 予算(方針8): cost_logger installの全API(LLM/TTS/ASR Primary・Secondary/LR)を集計
# ------------------------------------------------------------
class E2EBudget:
    """承認上限(approved)と警告閾値(warn)。guard()は『累計+次の見積 > limit』なら新規API呼出の前にSTOP。
    limit = warn(既定200円)。--ack-warn-thresholdを明示した場合のみ approved(300円)まで進める。"""

    def __init__(self, approved_jpy: float, warn_jpy: float = E2E_WARN_THRESHOLD_JPY, spent_fn=None,
                 ack_warn: bool = False):
        if approved_jpy <= 0:
            raise FamilyZBudgetStop("FAMILY_Z_BUDGET_NOT_APPROVED: --approved-budget-jpy(>0)が必須です")
        if approved_jpy > E2E_APPROVED_BUDGET_MAX_JPY:
            raise FamilyZBudgetStop(
                f"FAMILY_Z_BUDGET_ABOVE_APPROVED_MAX: {approved_jpy} > {E2E_APPROVED_BUDGET_MAX_JPY}"
                "(上限変更はユーザー/Fable承認が必要)")
        self.approved, self.warn, self.ack_warn = float(approved_jpy), float(warn_jpy), bool(ack_warn)
        self.spent_fn = spent_fn or (lambda: 0.0)
        self.log = []

    def spent(self) -> float:
        v = self.spent_fn()
        return float(v[0] if isinstance(v, tuple) else v)

    def limit(self) -> float:
        return self.approved if self.ack_warn else min(self.warn, self.approved)

    def remaining(self) -> float:
        return max(self.limit() - self.spent(), 0.0)

    def guard(self, label: str, est_jpy: float) -> float:
        s = self.spent()
        self.log.append({"label": label, "est_jpy": est_jpy, "spent_jpy": round(s, 4)})
        if s + est_jpy > self.limit():
            kind = "APPROVED_CAP" if self.ack_warn else "WARN_THRESHOLD"
            raise FamilyZBudgetStop(
                f"FAMILY_Z_BUDGET_STOP({kind}): label={label!r} spent={s:.2f} + est={est_jpy:.2f} > "
                f"limit={self.limit():.2f}(warn={self.warn}, approved={self.approved})。"
                "新規API呼出の前に停止しました。続行にはユーザー/Fable確認の上 --ack-warn-threshold を付けて再実行。")
        return s


def make_real_spent_fn(cost_log_path: str):
    def fn():
        import er019_family_x_audio_production_runner_01 as x_runner  # compute_cost_jpy_so_far(読み取り専用)
        return x_runner.compute_cost_jpy_so_far(cost_log_path)[0]
    return fn


# ------------------------------------------------------------
# Context
# ------------------------------------------------------------
@dataclasses.dataclass
class E2EContext:
    story_key: str = "melos"
    slug: str = "melos"
    run: str = E2E_DEFAULT_RUN
    mode: str = "dry-run"                       # dry-run | mock | real
    run_root: str = E2E_RUN_ROOT
    pages_dir: str = E2E_PAGES_DIR
    budget: object = None
    llm_client: object = None
    judge_client: object = None
    hooks: dict = dataclasses.field(default_factory=dict)
    only_clips: object = None
    regenerate_stage: object = None

    @property
    def out_dir(self) -> str:
        return f"{self.run_root}/{self.slug}/{self.run}"

    @property
    def seed_dir(self) -> str:
        return f"{E2E_RUN_ROOT}/{self.slug}/seed"          # Seed/anchorsは不変・固定置き場

    @property
    def anchors_path(self) -> str:
        return f"{E2E_RUN_ROOT}/{self.slug}/validator/anchors.json"

    def stage_context(self, name: str):
        if self.mode != "real":
            return contextlib.nullcontext()
        import er005_cost_logger as cl
        return cl.logging_context(E2E_THEME_TAG, name)


def _guard(ctx, label, est):
    if ctx.budget is not None:
        ctx.budget.guard(label, est)


def _regen_for(ctx, *names):
    return ctx.regenerate_stage if ctx.regenerate_stage in names else None


def _w62_llm(ctx):
    m = _m()
    cap = ctx.budget.remaining() if ctx.budget is not None else 1e9
    return m.w62.LLM(ctx.llm_client, m.w62.Budget(cap, m.w62.DEFAULT_EST))


def _level_text_path(ctx, level):
    return _m().w62.level_text_path(ctx.out_dir, level)


def canonical_article_text(text: str) -> str:
    """原稿(canonical)本文: タイトル行を除き段落を空行区切りで連結。Validator・KP・Gate(article_text)で共通に使う。"""
    st = _m().st
    _t, body = st.split_title_body(text)
    return "\n\n".join(st.clean_body_paragraphs(body))


def _sha(s) -> str:
    return _m().st.sha(s)


def _prov(ctx):
    m = _m()
    return m.w62.Provenance(f"{ctx.out_dir}/writer/provenance.json", ctx.story_key,
                            m.w62.file_sha(f"{ctx.seed_dir}/seed.json"))


# ------------------------------------------------------------
# stage実装
# ------------------------------------------------------------
def stage_seed_check(ctx) -> dict:
    """読み取り専用の事前確認(API 0・書込 0)。Seed凍結sha・anchors完全性・routing key・Style表sha・
    Melos Voice機構・er020 role解決・権利Gateを確認する。"""
    m = _m()
    check_rights_gate(STORY_REGISTRY[ctx.story_key]["rights_block"])
    with open(f"{ctx.seed_dir}/SEED_PROVENANCE.json", encoding="utf-8") as f:
        pinfo = json.load(f)
    seed_files = {}
    for name, meta in pinfo["files"].items():
        actual = m.w62.file_sha(f"{ctx.seed_dir}/{name}")
        if actual != meta["sha256"]:
            raise FamilyZE2EStop(f"FAMILY_Z_SEED_SHA_MISMATCH: {name} {actual[:12]} != {meta['sha256'][:12]}")
        seed_files[name] = actual[:12]
    anchors = m.v61.load_anchors(ctx.anchors_path, ctx.seed_dir)
    keys = ("FAMILY_Z_WRITER_ADV_R0", "FAMILY_Z_WRITER_ADV_R1", "FAMILY_Z_WRITER_ADV_R2", "FAMILY_Z_STD_ADJUST",
            "FAMILY_Z_SEMANTIC_JUDGE", "FAMILY_Z_STORY_SPLIT", "FAMILY_Z_DIALOGUE_ATTRIBUTION")
    models = {k: routing.PROCESS_MODEL_MAP[k] for k in keys}
    style = m.a63.assert_style_table_integrity()
    melos_voice = m.a63.check_melos_voice_mechanism()
    role_ok = all(tts_role.resolve_narrative_role(i) == "FULL_STORY" and tts_role.connected_speech_enabled_for(i)
                  for i in ("full_story_part1_c1", "full_story_part2_c3", "full_story_part3_c20"))
    if not role_ok:
        raise FamilyZE2EStop("FAMILY_Z_ER020_ROLE_PATTERN_NOT_RESOLVING")
    return {"seed_files": seed_files, "anchors_sha256": anchors["sha256_self"][:12], "routing_models": models,
            "style_table_keys": sorted(style), "melos_voice": melos_voice["melos_voice"],
            "melos_voice_status": melos_voice["status"], "er020_full_story_clip_pattern": role_ok,
            "dialogue_voices": m.a63.FAMILY_Z_DIALOGUE_VOICE_TTS_NAMES}


def stage_writer(ctx) -> dict:
    m = _m()
    _guard(ctx, "writer", E2E_STAGE_EST_JPY["writer"])
    llm = _w62_llm(ctx)
    res = m.w62.run_writer_chain(llm, ctx.out_dir, ctx.seed_dir, stages=("r0", "r1", "r2"),
                                 regenerate_stage=_regen_for(ctx, "r0", "r1", "r2"), story_key=ctx.story_key)
    return {"stages": {k: {"status": v["status"], "guardrails": v["guardrails"],
                           "output_sha256": v["entry"]["output_sha256"][:12]} for k, v in res["stages"].items()},
            "llm_spent_jpy": round(llm.budget.spent, 4)}


def stage_validate(ctx, level: str) -> dict:
    """er061 Validator(Adv=level b1b / Std=level a2+adv_text)。FAIL/NEEDS_REVIEWは自動で通さずSTOP。"""
    m = _m()
    out = ctx.out_dir
    cand = canonical_article_text(m.w62.rd(_level_text_path(ctx, level)))
    adv = canonical_article_text(m.w62.rd(_level_text_path(ctx, "b1b"))) if level == "a2" else None
    anchors = m.v61.load_anchors(ctx.anchors_path, ctx.seed_dir)
    vdir = f"{out}/validator/{level}"
    inputs = {"candidate_sha256": _sha(cand), "anchors_sha256": anchors["sha256_self"],
              "adv_sha256": _sha(adv) if adv is not None else None}
    rp, ip = f"{vdir}/validator_result.json", f"{vdir}/inputs.json"
    reused = False
    if os.path.exists(rp) and os.path.exists(ip) and m.w62.rj(ip) == inputs:
        result, reused = m.w62.rj(rp), True
    else:
        _guard(ctx, f"validate_{level}", E2E_STAGE_EST_JPY[f"validate_{level}"])
        tracker = m.v61.CostTracker(cap_jpy=ctx.budget.remaining() if ctx.budget is not None else 1e9)
        result = m.v61.validate_semantic_preservation(
            cand, level, client=ctx.judge_client, anchors=anchors, adv_text=adv, tracker=tracker,
            source_info=m.v61.load_source_info(ctx.seed_dir), out_dir=vdir)
        m.w62.wj(ip, inputs)
    if result["stop_required"]:
        raise FamilyZValidatorStop(
            f"FAMILY_Z_VALIDATOR_{result['verdict']}({level}): reasons={result['reasons']} "
            f"詳細={vdir}/validator_summary.md(自動で通さない。人間判断/明示的な再生成が必要)")
    return {"level": level, "verdict": result["verdict"], "reused": reused, "cost_jpy": result.get("cost_jpy"),
            "reasons": result["reasons"]}


def stage_std_adjust(ctx) -> dict:
    """Std調整。段落数がAdvと不一致なら自動で1回だけ再生成(方針2)、なお不一致ならSTOP。"""
    m = _m()
    _guard(ctx, "std_adjust", E2E_STAGE_EST_JPY["std_adjust"])
    llm = _w62_llm(ctx)
    res = m.w62.run_writer_chain(llm, ctx.out_dir, ctx.seed_dir, stages=("std_adjust",),
                                 regenerate_stage=_regen_for(ctx, "std_adjust"), story_key=ctx.story_key)
    g = res["stages"]["std_adjust"]["guardrails"]
    auto_regen = False
    if not g["std_adv_paragraph_count_match"]:
        prior = [r for r in _prov(ctx).data.get("regenerations", []) if r.get("stage") == "std_adjust"]
        if prior:
            raise FamilyZStdParagraphStop(
                f"FAMILY_Z_STD_PARAGRAPH_MISMATCH(再生成済み): std={g['paragraph_count_std']} "
                f"adv={g['paragraph_count_adv']}。自動再生成は1回のみ。STOP(明示的な --regenerate-stage std_adjust のみ)")
        _guard(ctx, "std_adjust_auto_regen", E2E_STAGE_EST_JPY["std_adjust"])
        llm = _w62_llm(ctx)
        res = m.w62.run_writer_chain(llm, ctx.out_dir, ctx.seed_dir, stages=("std_adjust",),
                                     regenerate_stage="std_adjust", story_key=ctx.story_key)
        auto_regen = True
        g = res["stages"]["std_adjust"]["guardrails"]
        m.w62.wj(f"{ctx.out_dir}/writer/std_auto_realign.json",
                 {"reason": "STD_ADV_PARAGRAPH_COUNT_MISMATCH", "after": {k: g[k] for k in (
                     "paragraph_count_std", "paragraph_count_adv", "std_adv_paragraph_count_match")}})
        if not g["std_adv_paragraph_count_match"]:
            raise FamilyZStdParagraphStop(
                f"FAMILY_Z_STD_PARAGRAPH_MISMATCH(再生成後も不一致): std={g['paragraph_count_std']} "
                f"adv={g['paragraph_count_adv']}。STOP(04Bの独自分割経路は使わない)")
    return {"status": res["stages"]["std_adjust"]["status"], "auto_regenerated": auto_regen, "guardrails": g}


def write_speaker_table(ctx) -> str:
    """全引用の話者表(決定論/LLM/最終)と dialogue clip 一覧。E2E後の人間確認用(方針4。補助フィールドは設けない)。"""
    m = _m()
    out = ctx.out_dir
    lines = ["# 話者表(全引用。人間確認用。LLM判定をそのまま採用、回想・独白の補助フィールドは設けない)", ""]
    for lv, label in (("b1b", "Advanced"), ("a2", "Standard")):
        ap = f"{out}/dialogue_attribution_{lv}.json"
        pp = f"{out}/segment_plan_{lv}.json"
        if not (os.path.exists(ap) and os.path.exists(pp)):
            continue
        att, plan = m.w62.rj(ap), m.w62.rj(pp)
        lines += [f"## {label}", "", "| quote_id | 段落 | 引用 | 決定論 | LLM | 状態 | 根拠 |", "|---|---|---|---|---|---|---|"]
        for r in att.get("rows", []):
            q = (r.get("text") or "").replace("|", "/")
            lines.append(f"| {r['quote_id']} | {r['paragraph_index']} | {q} | {r.get('deterministic')} | "
                         f"{r.get('llm')} | {r.get('status')} | {(r.get('basis') or '').replace('|', '/')[:80]} |")
        lines += ["", "dialogue clip(声がnarrator以外):", "", "| clip | speaker | voice | text |", "|---|---|---|---|"]
        for c in plan["clips"]:
            if c.get("speaker") != "narrator":
                try:
                    voice = m.a63.resolve_dialogue_voice(m.a63.normalize_speaker(c["speaker"]))
                except Exception as e:  # noqa: BLE001
                    voice = f"UNMAPPED({e.__class__.__name__})"
                lines.append(f"| {c['id']} | {c['speaker']} | {voice} | {(c['text'] or '').replace('|', '/')[:90]} |")
        lines.append("")
    path = f"{out}/speaker_table.md"
    m.w62.wt(path, "\n".join(lines) + "\n")
    return path


def _check_plan_after(ctx, level: str) -> dict:
    m = _m()
    plan = m.w62.rj(f"{ctx.out_dir}/segment_plan_{level}.json")
    others = [c["id"] for c in plan["clips"] if c.get("speaker") == "other"]
    if others:
        raise FamilyZDialogueOtherStop(
            f"FAMILY_Z_DIALOGUE_SPEAKER_OTHER({level}): {others}。speaker=otherはSTOP(Melos・王・友以外の話者。人間判断)")
    if level == "a2" and plan.get("split_origin") != "mapped_from_advanced":
        raise FamilyZStdParagraphStop(
            f"FAMILY_Z_STD_PLAN_NOT_ALIGNED: split_origin={plan.get('split_origin')!r}(Advの境界写像のみ許可)")
    return plan


def stage_plan(ctx) -> dict:
    m = _m()
    st, w62 = m.st, m.w62
    _guard(ctx, "plan", E2E_STAGE_EST_JPY["plan"])
    llm = _w62_llm(ctx)
    prov = _prov(ctx)
    summary = {}
    for lv in ("b1b", "a2"):
        if lv == "a2":
            # 方針2: Std境界はAdvの段落indexをそのまま写像。写像できなければ独自分割に回らずSTOP。
            adv_plan = w62.rj(f"{ctx.out_dir}/segment_plan_b1b.json")
            _t, body = st.split_title_body(w62.rd(_level_text_path(ctx, "a2")))
            paras = st.clean_body_paragraphs(body)
            cands = {tuple(c) for c in st.enumerate_split_candidates(st.para_word_counts(paras))}
            if len(paras) != adv_plan["paragraph_count"] or tuple(adv_plan["boundaries"]) not in cands:
                raise FamilyZStdParagraphStop(
                    f"FAMILY_Z_STD_BOUNDARY_NOT_MAPPABLE: std段落={len(paras)} adv段落={adv_plan['paragraph_count']} "
                    f"adv境界={adv_plan['boundaries']}がStdのPart比20-45%を満たさない。独自分割は使わずSTOP")
        r = w62.stage_plan(llm, ctx.out_dir, ctx.slug, ctx.run, lv, prov, ctx.regenerate_stage == f"plan_{lv}")
        plan = _check_plan_after(ctx, lv)
        summary[lv] = {"status": r["status"], "boundaries": plan["boundaries"], "clips": len(plan["clips"]),
                       "split_origin": plan.get("split_origin"), "dialogue_summary": plan.get("dialogue_summary")}
    summary["speaker_table"] = write_speaker_table(ctx)
    return summary


def stage_support(ctx) -> dict:
    m = _m()
    st, w62 = m.st, m.w62
    prov = _prov(ctx)
    summary = {}
    for lv in ("b1b", "a2"):
        text = w62.rd(_level_text_path(ctx, lv))
        plan_path = f"{ctx.out_dir}/segment_plan_{lv}.json"
        plan = w62.rj(plan_path)
        _t, body = st.split_title_body(text)
        parts = st.part_texts(st.clean_body_paragraphs(body), *plan["boundaries"])

        def runner(lv=lv, parts=parts, text=text):
            _guard(ctx, f"support_{lv}", E2E_STAGE_EST_JPY["support"] / 2)
            prior_path = f"{ctx.out_dir}/support/{lv}_support.json"
            prior = None   # 明示再生成時のみ: 既存のPreview/Comment1/2を再利用しComment3だけ再生成(委任_08 Fable判断)
            if ctx.regenerate_stage == f"support_{lv}" and os.path.exists(prior_path):
                prior = w62.rj(prior_path)
                shutil.copyfile(prior_path, prior_path.replace(".json", "_prev_before_c3_limit.json"))
            if lv == "a2":
                res = w62.run_support_std(ctx.llm_client, parts, text, ja_support_fn=ctx.hooks.get("ja_support_fn"),
                                          story_key=ctx.story_key, prior=prior)
            else:
                res = w62.run_support_adv(ctx.llm_client, parts, text, en_support_fn=ctx.hooks.get("en_support_fn"),
                                          story_key=ctx.story_key, prior=prior)
            return st.dumps(res), {}

        r = w62.ensure_stage(prov, f"support_{lv}", _sha(text + w62.file_sha(plan_path)),
                             f"{ctx.out_dir}/support/{lv}_support.json", runner,
                             regenerate=ctx.regenerate_stage == f"support_{lv}")
        summary[lv] = r["status"]
    return summary


def _kp_assets_dir(ctx, level):
    return f"{ctx.out_dir}/{level}/key_phrases"


def install_kp_assets(ctx, level: str) -> str:
    """方針10: er062出力 <run>/key_phrases/<level>/ -> <run>/<level>/key_phrases/keywords_canonicalized.json(既存Gateの参照先)。"""
    src = f"{ctx.out_dir}/key_phrases/{level}/keywords_canonicalized.json"
    if not os.path.exists(src):
        raise FamilyZE2EStop(f"FAMILY_Z_KP_CANONICALIZED_MISSING: {src}")
    dst = f"{_kp_assets_dir(ctx, level)}/keywords_canonicalized.json"
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(src, dst)
    return dst


def stage_kp(ctx) -> dict:
    m = _m()
    st, w62 = m.st, m.w62
    prov = _prov(ctx)
    summary = {}
    for lv in ("b1b", "a2"):
        text = canonical_article_text(w62.rd(_level_text_path(ctx, lv)))

        def runner(lv=lv, text=text):
            _guard(ctx, f"kp_{lv}", E2E_STAGE_EST_JPY["kp"] / 2)
            res = w62.run_kp_stage(lv, text, ctx.out_dir, ctx.slug, kp_fn=ctx.hooks.get("kp_fn"))
            if res.get("status") == "NG_REVIEW_REQUIRED" or not res.get("canonicalization"):
                raise FamilyZE2EStop(f"FAMILY_Z_KP_NOT_PASSED({lv}): status={res.get('status')} "
                                     f"canonicalization={bool(res.get('canonicalization'))}(自動採用しない)")
            return st.dumps(res), {}

        r = w62.ensure_stage(prov, f"kp_{lv}", _sha(text), f"{ctx.out_dir}/key_phrases/{lv}_result.json", runner,
                             regenerate=ctx.regenerate_stage == f"kp_{lv}")
        dst = install_kp_assets(ctx, lv)
        summary[lv] = {"status": r["status"], "assets": dst}
    # 方針6: Adv KP第3segment=英語解説(Coffee最終v3 Adv / X B1と同一構成)。
    kp = w62.rj(f"{_kp_assets_dir(ctx, 'b1b')}/keywords_canonicalized.json")
    items = sorted(kp["items"], key=lambda x: x["rank"])
    sig = _sha(json.dumps([it["display_phrase"] for it in items], ensure_ascii=False))
    ex_path = f"{ctx.out_dir}/key_phrases/b1b/kp_explanations.json"

    def runner_ex():
        import er019_family_x_kp_explanation_01 as kexp
        _guard(ctx, "kp_expl_b1b", 2.0)
        inp = [{"rank": it["rank"], "display_phrase": it["display_phrase"],
                "source_sentence": it.get("source_sentence", ""), "japanese_gloss": it.get("japanese_gloss", "")}
               for it in items]
        res = kexp.generate_kp_explanations(inp, call_fn=ctx.hooks.get("expl_call_fn"), client=ctx.llm_client)
        bad = {r_: v.get("status") for r_, v in res["items"].items() if v.get("status") != "OK"}
        if bad:
            raise FamilyZE2EStop(f"FAMILY_Z_KP_EXPLANATION_NOT_OK: {bad}(Xと同じくTTSへ渡さずSTOP)")
        return st.dumps(res), {}

    r = w62.ensure_stage(prov, "kp_expl_b1b", sig, ex_path, runner_ex, regenerate=ctx.regenerate_stage == "kp_expl_b1b")
    summary["kp_explanations_b1b"] = r["status"]
    return summary


def load_level_inputs(ctx, level: str) -> dict:
    """TTS/Gate/Assemblyが共有する決定論的入力(ファイルから再構成するので各stageを独立に実行できる)。"""
    m = _m()
    w62, a63 = m.w62, m.a63
    out = ctx.out_dir
    text = w62.rd(_level_text_path(ctx, level))
    plan = w62.rj(f"{out}/segment_plan_{level}.json")
    support = w62.rj(f"{out}/support/{level}_support.json")
    kp = w62.rj(f"{_kp_assets_dir(ctx, level)}/keywords_canonicalized.json")
    items = sorted(kp["items"], key=lambda x: x["rank"])
    kp_items = [{"rank": it["rank"], "used_form": it["used_form"], "japanese_gloss": it.get("japanese_gloss", ""),
                 "display_phrase": it["display_phrase"]} for it in items]
    expl = None
    if level == "b1b":
        ex = w62.rj(f"{out}/key_phrases/b1b/kp_explanations.json")
        expl = {int(r): v["english_explanation"] for r, v in ex["items"].items()}
    cfg = STORY_REGISTRY[ctx.story_key]
    comments = {int(n): t for n, t in support["comments"].items()}
    story_clips = plan["clips"]
    spec_plan = a63.build_level_plan(
        level, story_clips, support["preview"], comments, kp_items, cfg["topic_title"],
        cfg.get("japanese_title_tts") if level == "a2" else None, kp_explanations=expl)
    return {"plan": spec_plan, "story_clips": story_clips, "kp_items": kp_items, "kp_explanations": expl,
            "article_text": canonical_article_text(text),
            "shell_names": list(a63.SHELL_ASSET_SOURCES) + [f"kp{it['rank']}_number" for it in kp_items]}


def make_revalidate_fn(ctx):
    """Local Rewrite採択後の再検証(M6)。er061第1層(決定論)を再実行。FAIL(第1層FAIL/PASS→FAILへの悪化)のみSTOP、
    WARN(個別anchor欠落)は非ブロック(原稿自体がWARNでもLRで全clipがSTOPしないため)。"""
    m = _m()
    anchors = m.v61.load_anchors(ctx.anchors_path, ctx.seed_dir)

    def fn(text_before, text_after):
        r = m.v61.revalidate_after_local_rewrite(text_before, text_after, anchors)
        bad = r["stop_required"] or r["regressed_to_fail"]
        return {"verdict": "FAIL" if bad else "PASS", "layer1_verdict": r["verdict"],
                "regressed_to_fail": r["regressed_to_fail"], "diff": r["diff"]}
    return fn


def wrap_generators_with_budget(gens: dict, budget, est_clip_jpy: float = E2E_TTS_CLIP_EST_JPY, state: dict | None = None):
    """clip単位で新規API呼出前にguard。STOP時は例外を投げず『STOPPED結果』を返し(監査記録を失わない)、
    以降のclipも即STOPPED。呼出元がrun_tts_stage完了後に FamilyZBudgetStop を送出する。"""
    state = state if state is not None else {}

    def mk(fn):
        def w(spec, out_path):
            if state.get("stopped") is not None:
                return {"status": "STOPPED", "reason": f"BUDGET_STOP(前clipで停止): {state['stopped']}"}
            if budget is not None:
                try:
                    budget.guard(f"tts:{spec.clip_id}", est_clip_jpy)
                except FamilyZBudgetStop as e:
                    state["stopped"] = str(e)
                    return {"status": "STOPPED", "reason": f"BUDGET_STOP: {e}"}
            return fn(spec, out_path)
        return w
    return {k: mk(f) for k, f in gens.items()}


def stage_tts(ctx, level: str) -> dict:
    m = _m()
    inp = load_level_inputs(ctx, level)
    _guard(ctx, f"tts_{level}", E2E_TTS_CLIP_EST_JPY)
    gens = ctx.hooks.get("tts_generators") or m.a63.real_generators()
    state = {}
    gens = wrap_generators_with_budget(gens, ctx.budget, state=state)
    out = m.a63.run_tts_stage(ctx.out_dir, level, inp["plan"], generators=gens, only_clips=ctx.only_clips,
                              revalidate_fn=make_revalidate_fn(ctx), article_text=inp["article_text"],
                              story_key=ctx.slug)
    if state.get("stopped"):
        raise FamilyZBudgetStop(state["stopped"])
    failed = {k: v for k, v in out["statuses"].items() if v != "OK"}
    if failed:
        raise FamilyZTtsClipFailedStop(
            f"FAMILY_Z_TTS_CLIPS_NOT_OK({level}): {failed}。human_review_queue/attempts を確認し、"
            "承認または --only-clips で当該clipのみ再実行(全体の自動再生成はしない)")
    return {"level": level, "clips": len(out["statuses"]), "results_path": out["results_path"]}


def stage_provision_shell(ctx) -> dict:
    m = _m()
    res = {}
    for lv in LEVELS:
        inp = load_level_inputs(ctx, lv)
        res[lv] = sorted(m.a63.provision_shell_assets(ctx.out_dir, lv, kp_count=len(inp["kp_items"])))
    return res


def stage_gate(ctx) -> dict:
    m = _m()
    res = {}
    for lv in LEVELS:
        inp = load_level_inputs(ctx, lv)
        r = m.a63.run_audio_gate(ctx.out_dir, lv, inp["plan"], inp["shell_names"], article_text=inp["article_text"])
        res[lv] = {"shared_gate": r["shared_gate"], "audio_text_deviation_clips": r["audio_text_deviation_clips"]}
    return res


def stage_assemble(ctx) -> dict:
    m = _m()
    res = {}
    for lv in LEVELS:
        inp = load_level_inputs(ctx, lv)
        tl = m.a63.run_assembly(ctx.out_dir, lv, inp["story_clips"], inp["kp_items"], story_key=ctx.slug,
                                kp_third="explanation" if lv == "b1b" else "japanese")
        res[lv] = {"duration_seconds": round(tl["duration_seconds"], 2), "wav": tl["wav"],
                   "headroom": tl["headroom"]}
    return res


def stage_pages(ctx) -> dict:
    return _m().a63.build_pages(ctx.out_dir, ctx.pages_dir)


def evaluate_page_verify(res: dict) -> list:
    """Playwright --local 結果の合否。seek(通し音声)はhttp.serverがRange非対応のため偽陰性が出るので合否に含めない。"""
    problems = []
    for page, o in res["pages"].items():
        if o.get("http_status") != 200:
            problems.append(f"{page}:http_status={o.get('http_status')}")
        if o.get("plays_failed"):
            problems.append(f"{page}:plays_failed={len(o['plays_failed'])}")
        if o.get("console_errors"):
            problems.append(f"{page}:console_errors={o['console_errors'][:2]}")
        if o.get("http_ge400"):
            problems.append(f"{page}:http_ge400={o['http_ge400'][:2]}")
        for k in ("(m)_no_file_scheme", "(i)_no_A2_B1_label", "(n)_no_kp_label"):
            if not o.get(k):
                problems.append(f"{page}:{k}=False")
        if page != "index.html":
            for k in ("(a)_full_episode_audio", "(b)_preview_row", "(f)_intro_outro_noted", "(k)_tts_mode_stated"):
                if not o.get(k):
                    problems.append(f"{page}:{k}=False")
            if o.get("(c)_comment_rows", 0) < 3:
                problems.append(f"{page}:(c)_comment_rows={o.get('(c)_comment_rows')}")
            for k in ("(d)_story_rows", "(e)_kp_rows"):
                if not o.get(k):
                    problems.append(f"{page}:{k}={o.get(k)}")
    return problems


def stage_page_verify(ctx) -> dict:
    import functools
    import http.server
    import threading
    import er063_family_z_page_verify_01 as pv
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ctx.pages_dir)
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        res = pv.verify(f"http://127.0.0.1:{srv.server_address[1]}/", internal_only=True)
    finally:
        srv.shutdown()
        srv.server_close()
    _m().w62.wj(f"{ctx.out_dir}/page_verify_local.json", res)
    problems = evaluate_page_verify(res)
    if problems:
        raise FamilyZE2EStop(f"FAMILY_Z_PAGE_VERIFY_LOCAL_NG: {problems}(詳細 {ctx.out_dir}/page_verify_local.json)")
    return {"pages": sorted(res["pages"]), "evidence": f"{ctx.out_dir}/page_verify_local.json",
            "note": "--local は内部証跡(公開URL版(m)は別途)"}


@contextlib.contextmanager
def _mock_isolation(ctx):
    """mock時のみ: 共有module(er011)が呼ばれて追記する attempt_history.jsonl をrun配下の専用ファイルへ向ける
    (resume時の archive_prior_tts_results が共有履歴を汚さないため)。real時は何もしない(共有履歴への追記は正規動作)。"""
    if ctx.mode != "mock":
        yield
        return
    import er011_human_review_lock_01 as review_lock
    prev = review_lock.ATTEMPT_HISTORY_PATH
    review_lock.ATTEMPT_HISTORY_PATH = f"{ctx.out_dir}/attempt_history_mock.jsonl"
    try:
        yield
    finally:
        review_lock.ATTEMPT_HISTORY_PATH = prev


def run_stage(ctx, name: str) -> dict:
    fns = {
        "seed_check": stage_seed_check, "writer": stage_writer, "std_adjust": stage_std_adjust, "plan": stage_plan,
        "support": stage_support, "kp": stage_kp, "provision_shell": stage_provision_shell, "gate": stage_gate,
        "assemble": stage_assemble, "pages": stage_pages, "page_verify": stage_page_verify,
    }
    with ctx.stage_context(name), _mock_isolation(ctx):
        if name in ("validate_b1b", "validate_a2"):
            return stage_validate(ctx, name.split("_", 1)[1])
        if name in ("tts_b1b", "tts_a2"):
            return stage_tts(ctx, name.split("_", 1)[1])
        return fns[name](ctx)


def _log_stage(ctx, name, result, t0):
    rec = {"stage": name, "mode": ctx.mode, "elapsed_sec": round(time.time() - t0, 1),
           "spent_jpy_cumulative": round(ctx.budget.spent(), 4) if ctx.budget is not None else None,
           "result_keys": sorted(result) if isinstance(result, dict) else None}
    os.makedirs(ctx.out_dir, exist_ok=True)
    with open(f"{ctx.out_dir}/e2e_stage_log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def run_stages(ctx, stages) -> dict:
    results = {}
    for name in stages:
        t0 = time.time()
        print(f"[E2E] stage={name} mode={ctx.mode} ...", flush=True)
        results[name] = run_stage(ctx, name)
        _log_stage(ctx, name, results[name], t0)
    return results


# ------------------------------------------------------------
# dry-run: 全stage計画のみ(副作用ゼロ。ファイル作成・API呼出・Master Store/telemetry/queue更新なし)
# ------------------------------------------------------------
_STAGE_PLAN_INFO = {
    "seed_check": ("読み取りのみ", [], "-"),
    "writer": ("Sol R0->R1->R2 (FAMILY_Z_WRITER_ADV_R0/R1/R2)", ["writer/r0.md", "r1.md", "r2.md", "provenance.json"], "writer/r2.md"),
    "validate_b1b": ("Validator第2層 (FAMILY_Z_SEMANTIC_JUDGE)", ["validator/b1b/"], "validator/b1b/validator_result.json"),
    "std_adjust": ("Std調整 (FAMILY_Z_STD_ADJUST、段落不一致時のみ自動再生成1回)", ["writer/std.md"], "writer/std.md"),
    "validate_a2": ("Validator第2層 + Std追加検査", ["validator/a2/"], "validator/a2/validator_result.json"),
    "plan": ("分割選択+話者判定 (FAMILY_Z_STORY_SPLIT / FAMILY_Z_DIALOGUE_ATTRIBUTION)", ["segment_plan_{b1b,a2}.json", "speaker_table.md"], "segment_plan_a2.json"),
    "support": ("Preview/Comment (gpt-6-luna support)", ["support/{b1b,a2}_support.json"], "support/a2_support.json"),
    "kp": ("Key Phrase選定+Adv英語解説 (support model)", ["key_phrases/", "{b1b,a2}/key_phrases/keywords_canonicalized.json"], "key_phrases/b1b/kp_explanations.json"),
    "tts_b1b": ("TTS flash-lite + ASR Primary/Secondary + LR(必要時)", ["b1b/narration/", "b1b/audit/tts_generation_results.json"], "b1b/audit/tts_generation_results.json"),
    "tts_a2": ("TTS flash-lite + ASR Primary/Secondary + LR(必要時)", ["a2/narration/", "a2/audit/tts_generation_results.json"], "a2/audit/tts_generation_results.json"),
    "provision_shell": ("API 0 (既存共有shell資産の読取コピー)", ["{b1b,a2}/narration/*shell"], "-"),
    "gate": ("API 0 (M2->M1->品質->既存Gate)", ["{b1b,a2}/audit/gate_result_04C.json"], "b1b/audit/gate_result_04C.json"),
    "assemble": ("API 0 (assembly)", ["{b1b,a2}/assembly/"], "b1b/assembly/timeline.json"),
    "pages": ("API 0 (user_test/family_z_melos_01/)", ["pages_dir"], "-"),
    "page_verify": ("API 0 (Playwright --local)", ["page_verify_local.json"], "page_verify_local.json"),
}


def describe_plan(ctx, stages=E2E_STAGES) -> dict:
    """副作用ゼロ。ディスクは存在確認(os.path.exists)のみ。"""
    rows = []
    for name in stages:
        api, writes, marker = _STAGE_PLAN_INFO[name]
        exists = None if marker == "-" else os.path.exists(f"{ctx.out_dir}/{marker}")
        rows.append({"stage": name, "api": api, "writes": writes,
                     "est_jpy": E2E_STAGE_EST_JPY.get(name, 0.0),
                     "output_exists": exists,
                     "resume": ("provenance sha一致で再利用/不一致STOP" if exists else "新規実行")})
    return {"dry_run": True, "management_id": E2E_MANAGEMENT_ID, "story": ctx.story_key, "out_dir": ctx.out_dir,
            "pages_dir": ctx.pages_dir, "stages": rows,
            "budget": {"approved_max_jpy": E2E_APPROVED_BUDGET_MAX_JPY, "warn_jpy": E2E_WARN_THRESHOLD_JPY},
            "note": "副作用なし(ファイル作成・API呼出・Master Store/telemetry/queue/attempt_history更新なし)"}


# ------------------------------------------------------------
# mock runtime (--mode mock / test): 全LLM/TTS/ASR/KP fnを内蔵ダミーに固定(実API混入防止)
# ------------------------------------------------------------
MOCK_ADV_SOURCE = "er061_fixtures/F1_trial2_r2_normal.md"
_MOCK_KP_CANDIDATES = ("stood before the ruler", "Three men blocked the road", "caught a tree branch",
                       "Rain fell hard all night", "ran on", "dark water covered the bridge", "pulled himself out")


def _mock_std_text(adv_text: str, n_paragraphs: int) -> str:
    """Advの各文末記号の前に ' really' を入れた別文のStd(別文率100%・段落数/順序同一)。"""
    st = _m().st
    title, body = st.split_title_body(adv_text)
    paras = st.clean_body_paragraphs(body)
    if n_paragraphs != len(paras):
        raise AssertionError(f"mock: Std段落数{n_paragraphs}!=Adv{len(paras)}")
    out = [re.sub(r"(?<=[A-Za-z])([.!?])", r" really\1", p) for p in paras]
    return f"# {title or 'Mock'} (easy)\n\n" + "\n\n".join(out) + "\n"


def _mock_attribution(user_message: str) -> str:
    """mock LLM話者判定: 決定論で判定可能な引用は決定論と同じ、判定不能は melos(実LLMの代用。agree/llm_onlyのみ生成)。"""
    st = _m().st
    story = user_message.split("[Story]" + chr(10), 1)[1]
    tag = re.compile(r"\[\[Q:(q\d+_\d+)\]\]")
    ids = tag.findall(story)
    paras = [tag.sub("", p) for p in story.split(chr(10) * 2)]
    quotes = st.extract_quotes(paras)
    det = st.deterministic_attribution(paras, quotes)
    items = [{"quote_id": i, "speaker": det.get(i) or "melos", "basis": "mock"} for i in ids]
    return json.dumps({"attributions": items})


def mock_writer_hook(std_override=None):
    """er062.MockClient用hook。R0/R1/R2はAdv固定文(F1)、Std調整は別文のStd。split/attributionは既定MockResponses。"""
    with open(MOCK_ADV_SOURCE, encoding="utf-8") as f:
        adv = f.read()

    def hook(kw):
        user = kw["input"][-1]["content"]
        fmt = (kw.get("text") or {}).get("format", {})
        if fmt.get("name") == "z_dialogue_attribution":
            return _mock_attribution(user)
        if fmt.get("name"):
            return None
        if "Rewrite this entire story for CEFR A2" in user:
            n = int(re.search(r"exactly (\d+) paragraphs", user).group(1))
            if std_override:
                return std_override(n, adv)
            return _mock_std_text(adv, n)
        return adv
    return hook


class MockJudgeClient:
    """er061 judge用。全anchorを『preserved』として返す(evidence_quoteは両levelの文に逐語存在する語句)。"""

    def __init__(self, overrides: dict | None = None):
        self.calls = []
        self.overrides = overrides or {}
        self.responses = types.SimpleNamespace(create=self._create)

    def _create(self, **kw):
        m = _m()
        self.calls.append(kw)
        anchors = m.v61.load_anchors()
        items = []
        for a in anchors["anchors"]:
            it = {"anchor_id": a["id"], "category": a["category"], "status": "preserved", "severity": "none",
                  "evidence_quote": "Melos stood before the ruler", "note": "mock"}
            it.update(self.overrides.get(a["id"], {}))
            items.append(it)
        return types.SimpleNamespace(
            output_text=json.dumps({"items": items}, ensure_ascii=False), model=kw["model"],
            id=f"mock_judge_{len(self.calls)}",
            usage=types.SimpleNamespace(input_tokens=3000, output_tokens=1500,
                                        input_tokens_details=types.SimpleNamespace(cached_tokens=0)))


def mock_ja_support_fn(client, role, context, model=None):
    return {"status": "OK", "text": "羊飼いの男が、疑い深い王の前に立たされる場面です。男には妹の結婚式を控えた事情があり、"
                                    "ある大きな決断を迫られています。"}


def mock_en_support_fn(client, role, context, model=None):
    return {"status": "OK", "text": "A shepherd stands before a ruler who trusts no one. His sister's wedding is near, "
                                    "and he faces a hard choice."}


def mock_kp_fn(text, kp_dir, article_id, source_level, process=None, **kw):
    spans = [s for s in _MOCK_KP_CANDIDATES if s in text][:5]
    if len(spans) < 5:
        raise AssertionError(f"mock KP: 本文に実在する候補が{len(spans)}件しかない")
    os.makedirs(kp_dir, exist_ok=True)
    items = [{"rank": i, "source_span": s, "source_sentence": s, "display_phrase": s, "key_phrase": s, "used_form": s,
              "japanese_gloss": f"意味{i}"} for i, s in enumerate(spans, 1)]
    doc = {"items": items, "overall_status": "CANONICALIZATION_PASS", "article_id": article_id,
           "canonicalization_version": "mock", "source_level": source_level}
    with open(f"{kp_dir}/keywords_canonicalized.json", "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    return {"selection": {"status": "KEY_WORDS_STRUCTURE_PASS"}, "canonicalization": {"status": "CANONICALIZATION_PASS"},
            "redundancy_qa": {"status": "REDUNDANCY_OK"}, "redundancy_retry_log": []}


def mock_expl_call_fn(user_message: str):
    import er019_family_x_kp_explanation_01 as kexp
    phrases = re.findall(r'phrase: "(.*?)"', user_message)
    parsed = {"explanations": [{"phrase": p, "english_explanation": "to be in front of someone with power"}
                               for p in phrases]}
    return parsed, kexp.MODEL, {"input_tokens": 100, "cached_input_tokens": 0, "output_tokens": 50}, "mock_expl"


def mock_tts_generators() -> dict:
    """発話長を語数から決める偽TTS(tone wav)。Std Story clipは6%減速の証跡(_original.wav + slowdown_applied)付き。"""
    import numpy as np
    import er002_common as common
    a63 = _m().a63

    def duration_of(spec):
        if spec.language == "ja":
            return 0.8 + len(spec.text) / 7.0
        return 0.8 + len(spec.text.split()) / 2.8

    def write_tone(path, seconds):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        t = np.arange(int(common.SAMPLE_RATE * seconds)) / common.SAMPLE_RATE
        common.write_wav_float(path, (0.2 * np.sin(2 * np.pi * 220 * t)).astype("float32"), common.SAMPLE_RATE, 1)

    def make(kind):
        def fn(spec, out_path):
            d = duration_of(spec)
            is_std_story = spec.level == "a2" and a63._CLIP_ID_RE.fullmatch(spec.clip_id)
            write_tone(out_path, d * (1.06 if is_std_story else 1.0))
            r = {"status": "OK", "asr_text": spec.text, "disfluency_checked": True, "text": spec.text,
                 "standard_attempts_log": [{"attempt": 1, "instruction_type": "english_style_prefix_wide_margin",
                                            "style_prefix": {"sha256": "ab" * 32, "head200": "mock"},
                                            "tts_model_id": "mock-tts", "voice": spec.voice}]}
            if is_std_story:
                write_tone(out_path.replace(".wav", "_original.wav"), d)
                r["slowdown_applied"] = True
                r["slowdown_info"] = {"src_duration_seconds": d, "dst_duration_seconds": d * 1.06}
            return r
        return fn
    return {k: make(k) for k in ("narrator", "dialogue", "topic_intro", "preview", "comment", "japanese_title",
                                 "kp_en", "kp_ja", "kp_expl_en")}


def build_mock_context(run_root: str, run: str = "run_mock", pages_dir: str | None = None,
                       writer_hook=None, judge_client=None, tts_generators=None) -> E2EContext:
    m = _m()
    ctx = E2EContext(mode="mock", run=run, run_root=run_root,
                     pages_dir=pages_dir or f"{run_root}/melos/{run}/pages_mock")
    ctx.llm_client = m.w62.MockClient(writer_hook or mock_writer_hook())
    ctx.judge_client = judge_client or MockJudgeClient()
    ctx.hooks = {"ja_support_fn": mock_ja_support_fn, "en_support_fn": mock_en_support_fn, "kp_fn": mock_kp_fn,
                 "expl_call_fn": mock_expl_call_fn, "tts_generators": tts_generators or mock_tts_generators()}
    ctx.budget = E2EBudget(E2E_APPROVED_BUDGET_MAX_JPY, E2E_WARN_THRESHOLD_JPY, spent_fn=lambda: 0.0)
    return ctx


# ------------------------------------------------------------
# real runtime (--mode real: 委任_06のE2Eでのみ使用。本委任では実行しない)
# ------------------------------------------------------------
def build_real_context(args) -> E2EContext:
    """--mode real専用。承認予算の検証を最初に行い(未承認ならAPI client/ログ/ディレクトリを一切作らずSTOP)、
    その後にcost_logger installと実clientを構築する。"""
    ctx = E2EContext(story_key=args.story, slug=args.slug or args.story, run=args.run, mode="real")
    cost_log = f"{ctx.out_dir}/cost_log.jsonl"
    ctx.budget = E2EBudget(args.approved_budget_jpy, args.warn_threshold_jpy, spent_fn=make_real_spent_fn(cost_log),
                           ack_warn=args.ack_warn_threshold)       # 未承認/上限超過ならここでSTOP(副作用なし)
    from dotenv import load_dotenv
    load_dotenv()
    if args.tts_execution_mode:
        os.environ["TTS_EXECUTION_MODE"] = args.tts_execution_mode
    os.makedirs(ctx.out_dir, exist_ok=True)
    import er005_cost_logger as cl
    cl.install(cost_log)
    m = _m()
    ctx.llm_client = vfl01.get_client()
    ctx.judge_client = m.v61.get_openai_client()
    return ctx


# ============================================================
# CLI
# ============================================================
def _legacy_main(args, slug):
    if args.stage == "text":
        result = run_text_stage(args.story, slug, args.run, dry_run=args.dry_run)
        print(json.dumps({"stage": "text", "dry_run": args.dry_run,
                           "word_count": result["canonical_text"]["word_count"]}, ensure_ascii=False))
    if args.stage == "keyphrase":
        run_keyphrase_stage(args.story, slug, args.run, dry_run=args.dry_run)
        print(json.dumps({"stage": "keyphrase", "dry_run": args.dry_run}, ensure_ascii=False))


def build_parser():
    parser = argparse.ArgumentParser(description="Family Z (Fiction) Production runner: E2E統合(委任_05)")
    parser.add_argument("--story", default="melos", choices=list(STORY_REGISTRY.keys()))
    parser.add_argument("--slug", default=None, help="出力ディレクトリ名(既定: --storyと同じ)")
    parser.add_argument("--run", default=E2E_DEFAULT_RUN)
    parser.add_argument("--stage", default="all", choices=list(E2E_STAGES) + ["all"] + list(LEGACY_STAGES))
    parser.add_argument("--mode", default="dry-run", choices=("dry-run", "mock", "real"))
    parser.add_argument("--dry-run", action="store_true", help="legacy(Phase 1 text/keyphrase)互換。--mode dry-run と同じ")
    parser.add_argument("--only-clips", default=None, help="カンマ区切りclip id(TTS stageの当該clipのみ再実行)")
    parser.add_argument("--regenerate-stage", default=None,
                        choices=list(_m().w62.ALL_STAGE_NAMES) + list(E2E_KP_EXTRA_REGEN_NAMES),
                        help="明示指定したstageだけ再生成(自動再生成は行わない)")
    parser.add_argument("--approved-budget-jpy", type=float, default=0.0, help=f"real必須(上限{E2E_APPROVED_BUDGET_MAX_JPY})")
    parser.add_argument("--warn-threshold-jpy", type=float, default=E2E_WARN_THRESHOLD_JPY)
    parser.add_argument("--ack-warn-threshold", action="store_true", help="警告閾値超過後の続行を承認(approvedまで)")
    parser.add_argument("--tts-execution-mode", default="STANDARD", choices=("STANDARD", "BATCH"))
    parser.add_argument("--stop-after", default=None, choices=list(E2E_STAGES))
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    slug = args.slug or args.story
    args.slug = slug
    if args.dry_run:
        args.mode = "dry-run"
    if args.stage in LEGACY_STAGES:
        _legacy_main(args, slug)
        return 0

    stages = list(E2E_STAGES) if args.stage == "all" else [args.stage]
    if args.stop_after:
        stages = stages[: stages.index(args.stop_after) + 1]
    only = {c.strip() for c in args.only_clips.split(",") if c.strip()} if args.only_clips else None

    if args.mode == "dry-run":
        ctx = E2EContext(story_key=args.story, slug=slug, run=args.run, mode="dry-run")
        plan = describe_plan(ctx, stages)
        try:
            plan["preflight"] = stage_seed_check(ctx)       # 読み取りのみ
        except Exception as e:  # noqa: BLE001
            plan["preflight"] = {"error": f"{e.__class__.__name__}: {e}"}
        print(json.dumps(plan, ensure_ascii=False, indent=1, default=str))
        return 0
    try:
        if args.mode == "mock":
            ctx = build_mock_context(E2E_RUN_ROOT, run=f"{args.run}_mock",
                                     pages_dir=f"{E2E_RUN_ROOT}/{slug}/{args.run}_mock/pages_mock")
        else:
            ctx = build_real_context(args)
        ctx.only_clips, ctx.regenerate_stage = only, args.regenerate_stage
        results = run_stages(ctx, stages)
        summary = {"management_id": E2E_MANAGEMENT_ID, "mode": ctx.mode, "stages": list(results),
                   "spent_jpy": round(ctx.budget.spent(), 4) if ctx.budget is not None else None}
        print(json.dumps(summary, ensure_ascii=False))
        return 0
    except Exception as e:  # noqa: BLE001  (STOP: 自動retry/再生成/迂回はしない)
        print(f"[STOP] {e.__class__.__name__}: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
