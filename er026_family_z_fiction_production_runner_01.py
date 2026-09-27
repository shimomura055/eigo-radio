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
    """CURRENT_SPEC.md「Family Z(Fiction)」節 項目2(人物名変更・不要な
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
    """人物名ルール(item 2)を満たすための最小限の復元編集。

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


# ============================================================
# Segment plan (Z-2 reuse) + Connected Speech segment_id mapping (§7)
# ============================================================
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
    if len(segments) > 3:
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

    canonical = resolve_canonical_text(story_key)
    if not canonical["word_count_ok"]:
        raise RuntimeError(
            f"FAMILY_Z_WORD_COUNT_OUT_OF_RANGE: word_count={canonical['word_count']} "
            f"accept_range={ACCEPT_WORD_RANGE}")
    if not canonical["character_name_rule_ok"]:
        raise RuntimeError(
            f"FAMILY_Z_NAME_RULE_STILL_FAILING_AFTER_EDIT: "
            f"missing={canonical['missing_names_after']}")

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
        "tts_stage": "NOT_IMPLEMENTED_IN_THIS_PHASE (see stage_tts())",
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


def compute_actual_cost_jpy(log_path: str) -> dict:
    """trial02.compute_cost_jpy()と同一ロジックだが、THEME_TAGを本runner
    (FAMILY_Z_FICTION_PRODUCTION_E2E_01)向けに差し替えたもの(pricing読み
    込み自体はtrial02.load_pricing()をそのまま再利用)。"""
    if not os.path.exists(log_path):
        return {"total_usd": 0.0, "total_jpy": 0.0, "record_count": 0}
    pricing = trial02.load_pricing()
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
            if rec.get("model_id") != "gpt-5.6-luna":
                continue
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
# Stage: tts / assemble (本委任スコープ外、明示スタブ)
# ============================================================
def stage_tts(*_args, **_kwargs):
    raise NotImplementedError(
        "FAMILY_Z_TTS_STAGE_NOT_IMPLEMENTED_IN_THIS_PHASE: TTS/audio validation/"
        "runtime audio evidence/listening artifactは"
        "FICTION-FAMILY-Z-PRODUCTION-E2E-01のPhase 1(本委任)の対象外です。"
        "読み解決Phase 2(共有TTS入口)のcommit後、別委任でこのstageを実装"
        "します。既承認TTS仕様(CURRENT_SPEC.md「Family Z(Fiction)」節 項目6: "
        "attempt1→即時attempt2→10分cool-down→attempt3→NGならLocal Rewrite+"
        "Natural English QA、Connected Speechは5 role[Full Story/Comment/"
        "Preview/Topic intro/In One Line]へ適用)を、本stageは変更せずそのまま"
        "呼び出す予定です。")


def stage_assemble(*_args, **_kwargs):
    raise NotImplementedError(
        "FAMILY_Z_ASSEMBLE_STAGE_NOT_IMPLEMENTED_IN_THIS_PHASE: "
        "stage_tts()と同じ理由でPhase 1の対象外です。")


# ============================================================
# CLI
# ============================================================
def main():
    parser = argparse.ArgumentParser(description="Family Z (Fiction) Production runner (Phase 1: text stages)")
    parser.add_argument("--story", default="melos", choices=list(STORY_REGISTRY.keys()))
    parser.add_argument("--slug", default=None, help="出力ディレクトリ名(既定: --storyと同じ)")
    parser.add_argument("--run", default="run_01")
    parser.add_argument("--stage", default="text", choices=["text", "keyphrase", "all", "tts", "assemble"])
    parser.add_argument("--stop-after", default=None, choices=[None, "text", "keyphrase"])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    slug = args.slug or args.story

    if args.stage == "tts":
        stage_tts()
        return
    if args.stage == "assemble":
        stage_assemble()
        return

    if args.stage in ("text", "all"):
        result = run_text_stage(args.story, slug, args.run, dry_run=args.dry_run)
        print(json.dumps({"stage": "text", "dry_run": args.dry_run,
                           "word_count": result["canonical_text"]["word_count"]}, ensure_ascii=False))
        if args.stop_after == "text":
            return

    if args.stage in ("keyphrase", "all"):
        result = run_keyphrase_stage(args.story, slug, args.run, dry_run=args.dry_run)
        print(json.dumps({"stage": "keyphrase", "dry_run": args.dry_run,
                           "status": result.get("selection", {}).get("status")
                           if isinstance(result.get("selection"), dict) else result.get("status")},
                          ensure_ascii=False))
        if args.stop_after == "keyphrase":
            return


if __name__ == "__main__":
    main()
