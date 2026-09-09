# ============================================================
# er012_editorial_b_voices_3v_audio_trial_01.py
# 管理ID: EDITORIAL-B-FAMILY-VOICES-3V-AUDIO-TRIAL-01(Lane B、Audio Trial)
# ============================================================
# 目的: B-3V-2で承認された3 Voices基準記事(EDITORIAL-B-FAMILY-VOICES-
# 3V-PERSON-VOICE-TRIAL-02、`b1b_run01_attempt2/article.md`、497語)を
# 実際に音声化し、3 voices/3V required_structure/3V用Comment 2・3文言/
# Voice assignment/TTS QA/Audio Validation Gate(既定OFF+opt-in ON両方)/
# 実測尺/Fact・content integrity/試聴artifactを1本のReportへ記録する
# Audio Trialである。
#
# 禁止事項(委任文どおり): Production module(er012_b_family_voices_
# production_01.py・er012_b_family_production_runner_01.py)・registry
# (er012_b_family_editorial_type_registry_01.py)・Contractは一切編集
# しない。記事再生成なし。2V経路(既存Production)は無変更のまま。SSOT
# (CURRENT_SPEC.md等)・Git操作なし。バックグラウンド待機なし
# (Standard同期のみ)。完了報告後の自動復帰なし。
#
# 設計方針: 既存Production primitiveは全て「引数で呼ぶ」形でそのまま
# 再利用する(voice_name・text・out_pathを渡すだけの既存関数はimportして
# 直接呼ぶ)。新しいロジックが必要な箇所(6区切りparser・3声版parts
# builder・3声版Assembly timeline builder・3声版required_structure・
# 3声版voice availability解決)だけを本ファイルへ新規追加する。
# Production側の2声固定シグネチャ(registry.build_required_structure()・
# er012_b_family_voices_production_01.split_five_voice_sections()・
# build_b1_voices_timeline()・er003_v1_n3_01_assemble.py::load_b1_
# sources())は一切変更せず、本ファイルはそれらをimportして「読むだけ」
# (呼ばない、または3声版として別関数で再実装するだけ)にとどめる。
#
# Comment 2・3の3V版文言: EDITORIAL-B-FAMILY-VOICES-PHASE1-5-3V-4V-
# INTEGRATED-DESIGN-TRIAL-03(design.md B-1)のドラフト文言を、LLM再生成
# せずそのまま使う(EDITORIAL-B-FAMILY-VOICES-3V-PERSON-VOICE-TRIAL-01
# `qa/comments_1_to_4.json`と同じ扱い、TRIAL_ONLY_MANUAL_DRAFT・未承認・
# registryへは書かない)。Comment 1・4は既存確定Contract
# (registry.COMMENT_ROLES)をそのままLLM呼び出しで使う(人数に依存しない
# 文言のため無変更で使用可能)。
#
# 安全機構の対称性(OPEN-121/OPEN-122): Voice A/B(point_one/two)へ適用
# 済みのrepetition QA・connected speech equivalence layerを、Voice 3
# (point_three)にも同一規約(enable_repetition_qa=True、
# enable_connected_speech_equivalence_layer=True)で適用する。disfluency
# QA必須segment(`DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL["B1"]`、
# 共有Production辞書、無変更)にはpoint_one/two/threeいずれも含まれない
# ため(Phase 1と同一の既存仕様、fail-open状態はOPEN-132 Phase 2必須
# 項目(8)として既に記録済み、本Trialで新規対策はしない)。
#
# cost > 120円でSTOP。Human Review Lockが発動した場合は承認代行せずSTOP
# して報告する(record_human_approval()は呼ばない)。
from __future__ import annotations

import json
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

# PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-01: 正式リリース前はStandard同期を使う。
os.environ["TTS_EXECUTION_MODE"] = "STANDARD"

import hashlib

import audio_review_player as player_common
import er002_common as common
import er003_b1_p9a_audio as p9a
import er003_v1_b1_scaffold_01_generate as b1s
import er003_v1_n3_01_assemble as asm
import er003_v1_n3_01_scaffold_generate as sc
import er003_v1_n3_01_tts_generate as tts_gen
import er003_v1_sing01_news_tail_fix as news_tail_fix
import er003_v1_sing01_point_headings_aoede as point_headings
import er003_v1_sing01_voice01_generate as voice01
import er005_cost_logger as cl
import er006_audio_cost_pilot_02_shared_narration as shared_narration
import er006_model_routing_contract_01 as routing
import er012_b_family_editorial_type_registry_01 as registry
import er012_b_family_voices_production_01 as b1prod

# ============================================================
# 入力・出力パス
# ============================================================
ARTICLE_PATH = "er012_output/editorial_b_voices_3v_person_voice_trial_02/b1b_run01_attempt2/article.md"
LEDGER_FRAGMENT_PATH = ("er012_output/editorial_b_voices_3v_person_voice_trial_02/"
                         "b1b_run01_attempt2/audit/ledger_fragment_voices_1_2_3_only.txt")

OUT_DIR = "er012_output/editorial_b_voices_3v_audio_trial_01"
OUT_B1_DIR = f"{OUT_DIR}/b1b"
NARRATION_DIR = f"{OUT_B1_DIR}/narration"
COST_LOG_PATH = f"{OUT_B1_DIR}/audit/raw_usage_log.jsonl"
PRICING_SNAPSHOT_PATH = "er005_output/cost_baseline_01/pricing_snapshot.json"
USD_JPY = 160.0
BUDGET_JPY_CAP = 120.0

THEME = {"theme_id": "b_family_voices_3v_audio_trial_01", "out_dir": OUT_DIR}

# ============================================================
# Voice割当(Fable決定2026-09-09、承認済み候補[registry.VOICE_ASSIGNMENT/
# VOICE_FALLBACK]の枠内。Schedarは既存registryの「voice_a fallback」役割
# から、本3V Trialに限り「Voice 3の本採用候補」へ格上げする[design.md
# B-2で「別途ユーザー承認が必要」と記録済みの論点、Fableが今回明示的に
# 決定した]。registry自体は変更しない、Trial側の割当のみ)。
# ============================================================
VOICE_1 = registry.VOICE_ASSIGNMENT["voice_a"]  # Algieba(応募者)
VOICE_2 = registry.VOICE_ASSIGNMENT["voice_b"]  # Erinome(採用担当)
VOICE_3 = registry.VOICE_FALLBACK["voice_a"]    # Schedar(経営者、本Trialで新規に本採用候補として使用)
NARRATOR = registry.VOICE_ASSIGNMENT["narrator"]  # Aoede(既存Production point_headings.generateに既に固定済み)
COMMENT_VOICE = "Charon"

TARGET_DURATION_MIN_SECONDS = 380.0
TARGET_DURATION_MAX_SECONDS = 400.0


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, default=str)


def sha(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def sha256_file(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


class HumanReviewLockStop(RuntimeError):
    """Human Review Lock発動時にSTOPするための専用例外(承認代行しない)。"""


# ============================================================
# コスト計測(既存Trial/Production runnerと同一計算ロジック、本Trial専用
# ログへ適用。Production側のcompute_cost_jpy_so_far()自体は編集しない、
# 同一ロジックを本Trialファイル内へduplicateする)。
# ============================================================
def _load_pricing():
    prices = load_json(PRICING_SNAPSHOT_PATH)["prices"]

    def price(provider, model, meter):
        return next(p["price"] for p in prices
                    if p["provider"] == provider and p["model"] == model and p["meter"] == meter
                    and p.get("tier", "Standard") == "Standard")
    return price


def compute_cost_jpy_so_far() -> tuple:
    if not os.path.exists(COST_LOG_PATH):
        return 0.0, {}
    price = _load_pricing()
    total_usd = 0.0
    by_provider = {}
    with open(COST_LOG_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            provider = rec.get("provider")
            model = rec.get("model_id") or rec.get("model")
            usd = 0.0
            try:
                if provider in ("gemini", "openai", "openai_asr") and model:
                    in_tok = rec.get("input_tokens") or 0
                    out_tok = rec.get("output_tokens") or 0
                    usd = in_tok * price(provider, model, "input_tokens") / 1e6 \
                        + out_tok * price(provider, model, "output_tokens") / 1e6
            except StopIteration:
                usd = 0.0
            total_usd += usd
            by_provider[provider] = by_provider.get(provider, 0.0) + usd
    jpy = total_usd * USD_JPY
    return jpy, {k: round(v * USD_JPY, 2) for k, v in by_provider.items()}


def assert_budget_ok(note: str = "") -> float:
    jpy, by_provider = compute_cost_jpy_so_far()
    print(f"[3V-AUDIO-TRIAL][cost] so far={jpy:.2f} JPY by_provider={by_provider} ({note})")
    if jpy > BUDGET_JPY_CAP:
        raise RuntimeError(f"[BUDGET_GUARD] cost so far {jpy:.2f} JPY > cap {BUDGET_JPY_CAP} JPY. Stopping ({note}).")
    return jpy


def assert_not_locked(result: dict, segment_name: str) -> None:
    """Human Review Lock発動時は承認代行せずSTOPする(record_human_
    approval()は呼ばない、既存の安全装置をそのまま尊重する)。"""
    if isinstance(result, dict) and result.get("status") == "HUMAN_REVIEW_LOCKED":
        raise HumanReviewLockStop(
            f"[HUMAN_REVIEW_LOCK] segment={segment_name} でHuman Review Lockが発動しました。"
            f"承認代行はせず実行を中止します。詳細: {result}")


# ============================================================
# 6区切り構造parser(3V専用、Trial側新規。b1prod.split_five_voice_
# sections()と同型のロジックだが見出し数が6[hook/voice_1/voice_2/
# voice_3/tension/closing]。b1prod自体は無変更のまま、正規表現定数
# (##/###見出しにマッチ)だけを共有する)。
# ============================================================
SECTION_LABELS_3V = ("hook", "voice_1", "voice_2", "voice_3", "tension", "closing")


def split_six_voice_sections(article_text: str) -> dict | None:
    title_match = re.match(r"^#[ \t]+.+?\s*\n", article_text)
    if not title_match:
        return None
    body = article_text[title_match.end():]
    matches = list(b1prod._HEADING_RE.finditer(body))
    if len(matches) != 6:
        return None
    result = {}
    for i, label in enumerate(SECTION_LABELS_3V):
        heading_text = matches[i].group(2).strip()
        content_start = matches[i].end()
        content_end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        result[f"{label}_heading"] = heading_text
        result[f"{label}_body"] = body[content_start:content_end].strip()
    result["unexpected_preamble_before_first_heading"] = body[:matches[0].start()].strip()
    return result


def build_parts_3v(article_text: str) -> dict:
    sections = split_six_voice_sections(article_text)
    if sections is None:
        raise RuntimeError("6区切り構造(3V)の検出に失敗しました(想定と異なる見出し構成)")
    title = b1prod.extract_title(article_text)
    hook_part1, hook_part2 = b1prod.split_two_balanced_by_sentence(sections["hook_body"])
    return {
        "title": title,
        "part1": hook_part1, "part2": hook_part2,
        "point_one_heading": b1prod.ensure_period(sc.clean_heading(sections["voice_1_heading"])),
        "point_one_body": sections["voice_1_body"],
        "point_two_heading": b1prod.ensure_period(sc.clean_heading(sections["voice_2_heading"])),
        "point_two_body": sections["voice_2_body"],
        "point_three_heading": b1prod.ensure_period(sc.clean_heading(sections["voice_3_heading"])),
        "point_three_body": sections["voice_3_body"],
        "in_one_line": sections["closing_body"],
        "tension_heading": sections["tension_heading"],
        "tension_body": sections["tension_body"],
        "sections": sections,
        "_six_section_headings": {k: sections[k] for k in
                                   ("hook_heading", "voice_1_heading", "voice_2_heading", "voice_3_heading",
                                    "tension_heading", "closing_heading")},
    }


# ============================================================
# 3V required_structure(Trial側正本。registry.build_required_structure()
# は2声固定シグネチャのため呼べない[OPEN-129整合、Reconciliation確認
# 済み]。B_FAMILY_B1_REQUIRED_SEGMENTS[registry、無変更]と同一の役割
# 表記規約でVoice 3分を追加しただけの1段拡張。segment一覧は
# EDITORIAL-B-FAMILY-VOICES-3V-PERSON-VOICE-TRIAL-01
# `required_structure_3v_trial_review.json`(16 segment、point_one/two/
# three命名)と同一)。
# ============================================================
def build_required_structure_3v(voice_1: str, voice_2: str, voice_3: str) -> dict:
    role_resolvers = {
        "narrator_charon": lambda: "Charon",
        "narrator_aoede_en": lambda: "Aoede",
        "voice_1": lambda: voice_1,
        "voice_2": lambda: voice_2,
        "voice_3": lambda: voice_3,
        None: lambda: None,
    }
    required_segments_3v = (
        ("topic_intro", "narrator_charon"), ("preview", "narrator_charon"),
        ("comment_1", "narrator_charon"), ("comment_2", "narrator_charon"),
        ("comment_3", "narrator_charon"), ("comment_4", "narrator_charon"),
        ("point_one_heading", "narrator_aoede_en"), ("point_two_heading", "narrator_aoede_en"),
        ("point_three_heading", "narrator_aoede_en"),
        ("point_one", "voice_1"), ("point_two", "voice_2"), ("point_three", "voice_3"),
        ("full_story_part1", None), ("full_story_part2", None),
        (b1prod.EXTRA_SEGMENT_NAME, None), ("in_one_line", None),
    )
    resolved = tuple((name, role_resolvers[role]()) for name, role in required_segments_3v)
    return {"segments": resolved, "key_phrase_ranks": 5, "key_phrase_subkey_count": 2}


# ============================================================
# Step 0: prepare
# ============================================================
def prepare() -> dict:
    with open(ARTICLE_PATH, encoding="utf-8") as f:
        article_text = f.read()
    parts = build_parts_3v(article_text)
    os.makedirs(f"{OUT_B1_DIR}/audit", exist_ok=True)
    with open(f"{OUT_B1_DIR}/article.md", "w", encoding="utf-8") as f:
        f.write(article_text)
    save_json(f"{OUT_B1_DIR}/parts.json", parts)
    return {"article_text": article_text, "parts": parts}


# ============================================================
# Step 1: Voice可用性確認(3 voices固定、fallback設計なし。Fableが
# Voice 1/2/3をAlgieba/Erinome/Schedarに確定決定済みのため、技術的
# availability不可の場合は独自にfallbackを発明せずSTOPする)。
# ============================================================
def voice_check(parts: dict) -> dict:
    sample_text = b1prod.first_n_sentences(parts["point_one_body"], 3)
    sample_dir = f"{OUT_DIR}/audit/voice_samples"
    results = b1prod.run_voice_availability_check(sample_text, sample_dir, voice_names=(VOICE_1, VOICE_2, VOICE_3))
    save_json(f"{sample_dir}/voice_sample_results.json", {"sample_text": sample_text, "results": results})
    statuses = {v: results.get(v, {}).get("status") for v in (VOICE_1, VOICE_2, VOICE_3)}
    all_ok = all(s == "OK" for s in statuses.values())
    save_json(f"{OUT_DIR}/audit/voice_resolution.json",
              {"voice_1": VOICE_1, "voice_2": VOICE_2, "voice_3": VOICE_3, "statuses": statuses, "all_ok": all_ok})
    if not all_ok:
        raise RuntimeError(f"[VOICE_UNAVAILABLE] 3 voices中に技術的に利用不可なvoiceがあります: {statuses}。"
                            "本Trialでは承認済み割当(Algieba/Erinome/Schedar)以外のfallbackを独自に発明せず"
                            "中止します。")
    return {"voice_1": VOICE_1, "voice_2": VOICE_2, "voice_3": VOICE_3, "statuses": statuses}


# ============================================================
# Step 2: Key Phrase(この3V記事は新規、既存Production再利用対象が
# 存在しないため実際に選定+canonicalization+TTSを実行する)。
# ============================================================
def run_key_phrases(article_text: str) -> dict:
    kp_dir = f"{OUT_B1_DIR}/key_phrases"
    os.makedirs(kp_dir, exist_ok=True)
    selection = b1s.run_key_phrase_selection(article_text, kp_dir)
    print(f"[3V-AUDIO-TRIAL] Key Phrase選定status={selection['status']}")
    if selection["status"] != "KEY_WORDS_STRUCTURE_PASS":
        raise RuntimeError(f"[KEY_PHRASE_SELECTION_FAILED] status={selection['status']}")
    canon = b1s.run_key_phrase_canonicalization(article_text, selection["original_items"], kp_dir)
    print(f"[3V-AUDIO-TRIAL] Key Phrase canonicalization status={canon['status']}")
    if canon["status"] not in ("CANONICALIZATION_PASS", "CANONICALIZATION_REVIEW_REQUIRED"):
        raise RuntimeError(f"[KEY_PHRASE_CANONICALIZATION_FAILED] status={canon['status']}")
    assert_budget_ok("after Key Phrase selection/canonicalization")
    return canon["merged"]


def run_key_phrase_tts(kp_merged: dict) -> dict:
    os.makedirs(NARRATION_DIR, exist_ok=True)
    kp_results = {}
    for item in sorted(kp_merged["items"], key=lambda it: it["rank"]):
        rank = item["rank"]
        used_form = item["used_form"]
        ja_gloss = item["japanese_gloss"]
        ja_gloss_tts, ja_gloss_tts_fallback = tts_gen.resolve_key_phrase_ja_gloss_tts(item)
        print(f"[3V-AUDIO-TRIAL] Key Phrase {rank} 英語Component生成(Aoede、Master Audio Store経由): {used_form!r}...")
        with cl.segment_context(f"kp{rank}_english"):
            en_r = shared_narration.ensure_key_phrase_english_component(
                tts_gen.tts_safe_kp_en(used_form), f"{NARRATION_DIR}/kp{rank}_en.wav")
        assert_not_locked(en_r, f"kp{rank}_english")
        print(f"[3V-AUDIO-TRIAL] Key Phrase {rank} 日本語meaning生成(Charon)...")
        with cl.segment_context(f"kp{rank}_japanese"):
            ja_r = tts_gen.generate_charon_japanese_with_reading_safety(
                ja_gloss_tts, f"{NARRATION_DIR}/kp{rank}_ja_charon.wav", tts_gen.expected_substring_ja(ja_gloss_tts),
                known_key_phrase_terms=[used_form])
        assert_not_locked(ja_r, f"kp{rank}_japanese")
        ja_r["display_gloss"] = ja_gloss
        ja_r["japanese_gloss_tts_fallback_derived"] = ja_gloss_tts_fallback
        kp_results[rank] = {"english": en_r, "japanese": ja_r}
    save_json(f"{OUT_B1_DIR}/audit/kp_tts_results.json", kp_results)
    return kp_results


# ============================================================
# Step 3: Comment 1-4 + Preview
# Comment 1・4: registry確定Contract(COMMENT_ROLES)をそのままLLM呼び出し
# (人数非依存の文言のため無変更で使用可能)。
# Comment 2・3: design.md B-1の3V版ドラフト文言(TRIAL_ONLY_MANUAL_
# DRAFT、LLM再生成なし、未承認・registryへは書かない)。
# ============================================================
VOICES_COMMENT_2_ROLE_3V_DRAFT_TEXT = (
    "Now, you will hear three different voices, one after another. "
    "Each person will share their own view on what you just heard."
)
VOICES_COMMENT_3_ROLE_3V_DRAFT_TEXT = (
    "You have heard three different ways of experiencing the same situation. "
    "Instead of deciding which view is right, let us ask why the situation feels different to each person. "
    "Next, we will look more closely at where that difference comes from."
)
COMMENT_2_3V_SOURCE = ("design.md B-1(EDITORIAL-B-FAMILY-VOICES-PHASE1-5-3V-4V-INTEGRATED-DESIGN-TRIAL-03、"
                        "未承認・Trial-only、registryへは書かない)")


def run_scaffold_3v(parts: dict, article_text: str, sections: dict) -> dict:
    client = b1s.get_client()
    model = routing.require_model("B1_SUPPORT", routing.SUPPORT_MODEL)
    comment_roles = registry.COMMENT_ROLES

    print("[3V-AUDIO-TRIAL] Comment 1(registry確定Contract)生成開始...")
    c1_context = f"【これから聞く本文(The Question)】\n{sections['hook_body']}"
    c1 = b1s.run_support_text(client, comment_roles["comment_1"], c1_context, model=model)

    c2 = {"status": "TRIAL_ONLY_MANUAL_DRAFT_NOT_LLM_GENERATED", "text": VOICES_COMMENT_2_ROLE_3V_DRAFT_TEXT,
          "source": COMMENT_2_3V_SOURCE, "llm_generated": False}
    c3 = {"status": "TRIAL_ONLY_MANUAL_DRAFT_NOT_LLM_GENERATED", "text": VOICES_COMMENT_3_ROLE_3V_DRAFT_TEXT,
          "source": COMMENT_2_3V_SOURCE, "llm_generated": False}

    print("[3V-AUDIO-TRIAL] Comment 4(registry確定Contract)生成開始...")
    c4_context = (f"【聞き終えた内容(視点の違いの深掘り)】\n{parts['tension_body']}\n\n"
                  f"【これから聞く結びの見出しのみ(内容は伏せる)】\n{sections['closing_heading']}")
    c4 = b1s.run_support_text(client, comment_roles["comment_4"], c4_context, model=model)

    print("[3V-AUDIO-TRIAL] Preview(既存Production Prompt、無変更)生成開始...")
    preview_role = b1s.PREVIEW_ROLE.format(comment_1=c1.get("text") or "(生成失敗)", comment_2=c2["text"])
    preview_context = f"【エピソード全文(参考、新しいFactの追加禁止)】\n{article_text}"
    preview = b1s.run_support_text(client, preview_role, preview_context, model=model)

    results = {"preview": preview, "comment_1": c1, "comment_2": c2, "comment_3": c3, "comment_4": c4}
    os.makedirs(f"{OUT_B1_DIR}/audit", exist_ok=True)
    with open(f"{OUT_B1_DIR}/b1_support_texts.json", "w", encoding="utf-8") as f:
        json.dump({k: v.get("text") for k, v in results.items()}, f, ensure_ascii=False, indent=2)
    with open(f"{OUT_B1_DIR}/audit/b1_support_generation.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    assert_budget_ok("after scaffold(Comment/Preview)")
    return {"support": results, "support_status": {k: v.get("status") for k, v in results.items()}}


# ============================================================
# Step 4: TTS(既存Production primitiveを引数で呼ぶだけ。新関数追加は
# 本ファイル内のみ)。
# ============================================================
def run_tts_3v(parts: dict, support_texts: dict, voice_1: str, voice_2: str, voice_3: str) -> dict:
    shared_narration.ensure_all_shared_narration_b1(NARRATION_DIR)  # Production、無変更(Master Audio Store経由)

    results = {}
    topic_intro_text = f"Today's topic is {parts['title']}."
    print("[3V-AUDIO-TRIAL] topic_intro生成(Charon)...")
    with cl.segment_context("topic_intro"):
        results["topic_intro"] = voice01.generate_charon_english(
            tts_gen.tts_safe_number_words_en(tts_gen.tts_safe_en(topic_intro_text)), f"{NARRATION_DIR}/topic_intro.wav")
    assert_not_locked(results["topic_intro"], "topic_intro")
    results["topic_intro"]["canonical_text"] = topic_intro_text
    assert_budget_ok("after topic_intro TTS")

    for name in ("preview", "comment_1", "comment_2", "comment_3", "comment_4"):
        text = support_texts[name]
        print(f"[3V-AUDIO-TRIAL] {name}生成(Charon、registry Comment Contract/3V draft)...")
        with cl.segment_context(name):
            results[name] = voice01.generate_charon_english(
                tts_gen.tts_safe_number_words_en(tts_gen.tts_safe_en(text)), f"{NARRATION_DIR}/{name}.wav",
                style_prefix_override=tts_gen.B1_PREVIEW_STYLE_PREFIX_CALM, disfluency_qa=True)
        assert_not_locked(results[name], name)
        results[name]["canonical_text"] = text
    assert_budget_ok("after preview/comment TTS")

    for name in ("point_one_heading", "point_two_heading", "point_three_heading"):
        text = parts[name]
        sc.assert_no_point_number_label(text, name)
        print(f"[3V-AUDIO-TRIAL] {name}生成(Narrator=Aoede、Production point_headings.generate、無変更)...")
        with cl.segment_context(name):
            results[name] = point_headings.generate(
                tts_gen.tts_safe_number_words_en(tts_gen.tts_safe_en(text)), f"{NARRATION_DIR}/{name}.wav")
        assert_not_locked(results[name], name)
        results[name]["canonical_text"] = text
    assert_budget_ok("after Narrator heading TTS")

    # OPEN-121/OPEN-122安全機構の対称性: Voice A/B(Phase 1)と同一規約で
    # Voice 3(point_three)にもenable_connected_speech_equivalence_layer=
    # True・enable_repetition_qa=Trueを明示適用する。
    for name, text, voice_name in (
        ("point_one", parts["point_one_body"], voice_1),
        ("point_two", parts["point_two_body"], voice_2),
        ("point_three", parts["point_three_body"], voice_3),
    ):
        sc.assert_no_point_number_label(text, name)
        print(f"[3V-AUDIO-TRIAL] {name}生成({voice_name}、Production generate_voice_body_wide_margin、引数で呼ぶ)...")
        with cl.segment_context(name):
            results[name] = b1prod.generate_voice_body_wide_margin(
                tts_gen.tts_safe_news_en(text), f"{NARRATION_DIR}/{name}.wav", voice_name,
                enable_connected_speech_equivalence_layer=True, enable_repetition_qa=True)
        assert_not_locked(results[name], name)
        results[name]["canonical_text"] = text
    assert_budget_ok("after Voice 1/2/3 TTS")

    for name, text in (
        ("full_story_part1", parts["part1"]), ("full_story_part2", parts["part2"]),
        (b1prod.EXTRA_SEGMENT_NAME, parts["tension_body"]), ("in_one_line", parts["in_one_line"]),
    ):
        print(f"[3V-AUDIO-TRIAL] {name}生成(Aoede、既存Production news_tail_fix.generate_news_narration_wide_margin、"
              "無変更)...")
        with cl.segment_context(name):
            results[name] = news_tail_fix.generate_news_narration_wide_margin(
                tts_gen.tts_safe_news_en(text), f"{NARRATION_DIR}/{name}.wav",
                # Phase 1と同一規約(A-Family full_story_part1/2相当のみ
                # OPEN-121/OPEN-122対象、Tension/Closingは対象外)。
                disfluency_qa=(name == "in_one_line"),
                enable_connected_speech_equivalence_layer=(name in ("full_story_part1", "full_story_part2")),
                enable_repetition_qa=(name in ("full_story_part1", "full_story_part2")))
        assert_not_locked(results[name], name)
        results[name]["canonical_text"] = text
    assert_budget_ok("after Hook/Tension/Closing TTS")

    return results


def finalize_tts_results_3v(new_results: dict, kp_results: dict) -> dict:
    data = {"segments": new_results, "key_phrases": {}}
    for rank, kp in kp_results.items():
        data["key_phrases"][str(rank)] = {"english": kp["english"], "japanese": kp["japanese"]}
    save_json(f"{OUT_B1_DIR}/audit/tts_generation_results.json", data)
    all_status = {k: v.get("status") for k, v in new_results.items()}
    save_json(f"{OUT_B1_DIR}/run_summary_tts.json", {"segment_status": all_status})
    print(f"[3V-AUDIO-TRIAL] TTS完了。segment_status={all_status}")
    return data


# ============================================================
# Step 4.5: Audio Validation Gate(既定OFF経路+opt-in ON経路、両方を
# 明示的に検証・記録する。実assemblyはOFF経路[既存load_b1_sources()と
# 同一の既定挙動]で行う。ON経路はOPEN-129 opt-in引数を直接渡す形での
# 検証のみ[assembly自体はgateしない、比較evidence用])。
# ============================================================
def run_audio_gate_both_paths(voice_1: str, voice_2: str, voice_3: str) -> dict:
    result = {"default_off": None, "opt_in_on": None}
    try:
        asm.verify_episode_audio_validation_gate(OUT_B1_DIR, "B1", required_structure=None)
        result["default_off"] = {"status": "PASS"}
    except RuntimeError as e:
        result["default_off"] = {"status": "BLOCKED", "error": str(e)}

    required_structure_3v = build_required_structure_3v(voice_1, voice_2, voice_3)
    save_json(f"{OUT_B1_DIR}/audit/required_structure_3v.json", required_structure_3v)
    try:
        asm.verify_episode_audio_validation_gate(OUT_B1_DIR, "B1", required_structure=required_structure_3v)
        result["opt_in_on"] = {"status": "PASS"}
    except RuntimeError as e:
        result["opt_in_on"] = {"status": "BLOCKED", "error": str(e)}

    save_json(f"{OUT_B1_DIR}/audit/audio_gate_both_paths.json", result)
    print(f"[3V-AUDIO-TRIAL] Audio Validation Gate: default_off={result['default_off']['status']} "
          f"opt_in_on={result['opt_in_on']['status']}")
    return result


# ============================================================
# Step 5: Assembly(3V専用loader+timeline builder、Trial側新規。既存
# load_b1_sources()/build_b1_voices_timeline()は無変更のまま[2声固定
# シグネチャのため3声には使えない]。apply_b1_gain()/assemble_with_
# timeline()/apply_headroom_safety_valve()はgeneric実装[dict/list
# iterateのみ、voice数へ依存しない]のためProduction、無変更のまま
# そのまま再利用する)。
# ============================================================
def load_b1_sources_3v(out_dir: str) -> dict:
    narration_dir = f"{out_dir}/narration"
    # 既定OFF経路のGate検証(既存load_b1_sources()と同一の既定挙動)。
    asm.verify_episode_audio_validation_gate(out_dir, "B1")
    asm.copy_b1_shared_assets(narration_dir)  # Production、無変更

    intro = p9a.load_and_resample_to_target(p9a.INTRO_MP3_PATH)
    notification = p9a.load_and_resample_to_target(p9a.NOTIFICATION_MP3_PATH)
    point_notification = p9a.load_and_resample_to_target(asm.POINT_NOTIFICATION_MP3_PATH)
    outro = p9a.load_and_resample_to_target(p9a.OUTRO_MP3_PATH)

    narration = {}
    for name in ("welcome", "preview_intro", "key_phrases_intro", "full_story_intro"):
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/{name}_charon.wav")
        assert sr == common.SAMPLE_RATE
        narration[name] = mono
    for name in ("num_one", "num_two", "num_three", "num_four", "num_five"):
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/{name}_charon.wav")
        assert sr == common.SAMPLE_RATE
        narration[name] = mono
    mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/topic_intro.wav")
    assert sr == common.SAMPLE_RATE
    narration["topic_intro"] = mono

    b1_segments = {}
    for name in ("full_story_part1", "full_story_part2", "point_one", "point_two", "point_three",
                  b1prod.EXTRA_SEGMENT_NAME):
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/{name}.wav")
        assert sr == common.SAMPLE_RATE
        b1_segments[name] = mono
    for name in ("comment_1", "comment_2", "comment_3", "comment_4", "preview"):
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/{name}.wav")
        assert sr == common.SAMPLE_RATE
        b1_segments[name] = mono
    mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/in_one_line.wav")
    assert sr == common.SAMPLE_RATE
    b1_segments["in_one_line"] = mono
    for name in ("point_one_heading", "point_two_heading", "point_three_heading"):
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/{name}.wav")
        assert sr == common.SAMPLE_RATE
        b1_segments[name] = mono

    kp = load_json(f"{out_dir}/key_phrases/keywords_canonicalized.json")
    kp_items = sorted(kp["items"], key=lambda it: it["rank"])
    key_phrase_components, key_phrase_meanings = {}, {}
    for item in kp_items:
        rank = item["rank"]
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/kp{rank}_en.wav")
        key_phrase_components[rank] = mono
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/kp{rank}_ja_charon.wav")
        key_phrase_meanings[rank] = mono

    return {"intro": intro, "notification": notification, "point_notification": point_notification, "outro": outro,
            "narration": narration, "b1_segments": b1_segments,
            "key_phrase_components": key_phrase_components, "key_phrase_meanings": key_phrase_meanings,
            "kp_items": kp_items}


def build_b1_voices_timeline_3v(parts: dict, voice_1: str, voice_2: str, voice_3: str) -> list:
    """Hook/Comment1/Voice1(heading+body)/Comment2/Voice2(heading+body)/
    Voice3(heading+body)/Comment3/Tension/Comment4/Closingという、3V
    構造(6区切り)のtimelineを構築する(既存build_b1_voices_timeline()
    [2声固定]と同一のPause定数・Key Phrase位置規約を踏襲し、Voice 3の
    Point Notification/heading/body 1ブロックだけを新規挿入した)。"""
    key_phrase_blocks = asm.build_b1_key_phrase_blocks(parts)  # Production、無変更
    b1 = parts["b1_segments"]

    seq = [
        ("Intro", parts["intro"]),
        ("Welcome (Charon)", parts["welcome"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
        ("Topic intro (Charon)", parts["topic_intro"]),
        ("pause_0.65", p9a.silence_stereo(0.65)),
        ("Notification 1", parts["notification"]),
        ("pause_0.4", p9a.silence_stereo(0.4)),
        ("Preview intro (Charon)", parts["preview_intro"]),
        ("pause_0.65", p9a.silence_stereo(0.65)),
        ("Preview (Charon)", b1["preview"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
        ("Notification 2", parts["notification"]),
        ("pause_0.4", p9a.silence_stereo(0.4)),
        ("Key phrases intro (Charon)", parts["key_phrases_intro"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
    ]
    kp_labels = tuple(f"Key Phrase {i}" for i in range(1, len(key_phrase_blocks) + 1))
    for label, block in zip(kp_labels, key_phrase_blocks):
        seq.append((label, block))

    seq += [
        ("Notification 3", parts["notification"]),
        ("pause_0.4", p9a.silence_stereo(0.4)),
        ("Full story intro (Charon)", parts["full_story_intro"]),
        ("pause_1.0", p9a.silence_stereo(asm.AOEDE_TO_CHARON_PAUSE_SECONDS)),
        ("Comment 1 (Charon)", b1["comment_1"]),
        ("pause_0.8", p9a.silence_stereo(asm.CHARON_TO_AOEDE_PAUSE_SECONDS)),
        ("Hook Part 1: The Question (Aoede, no heading)", b1["full_story_part1"]),
        ("pause_0.25_hook_internal", p9a.silence_stereo(0.25)),
        ("Hook Part 2: The Question (Aoede, no heading)", b1["full_story_part2"]),
        ("pause_1.0", p9a.silence_stereo(asm.AOEDE_TO_CHARON_PAUSE_SECONDS)),
        ("Comment 2 (Charon, bridge to Voices, 3V draft wording)", b1["comment_2"]),
        ("pause_0.5_notification_entry", p9a.silence_stereo(asm.NOTIFICATION_ENTRY_PAUSE_SECONDS)),
        ("Point Notification (Voice 1 cue, existing SFX reuse)", parts["point_notification"]),
        ("Narrator: Voice 1 heading (Aoede)", b1["point_one_heading"]),
        ("pause_0.7_heading_to_body", p9a.silence_stereo(asm.HEADING_TO_BODY_PAUSE_SECONDS_B1)),
        (f"Voice 1 body ({voice_1})", b1["point_one"]),
        ("pause_0.5_notification_entry", p9a.silence_stereo(asm.NOTIFICATION_ENTRY_PAUSE_SECONDS)),
        ("Point Notification (Voice 2 cue, existing SFX reuse)", parts["point_notification"]),
        ("Narrator: Voice 2 heading (Aoede)", b1["point_two_heading"]),
        ("pause_0.7_heading_to_body", p9a.silence_stereo(asm.HEADING_TO_BODY_PAUSE_SECONDS_B1)),
        (f"Voice 2 body ({voice_2})", b1["point_two"]),
        ("pause_0.5_notification_entry", p9a.silence_stereo(asm.NOTIFICATION_ENTRY_PAUSE_SECONDS)),
        ("Point Notification (Voice 3 cue, existing SFX reuse)", parts["point_notification"]),
        ("Narrator: Voice 3 heading (Aoede)", b1["point_three_heading"]),
        ("pause_0.7_heading_to_body", p9a.silence_stereo(asm.HEADING_TO_BODY_PAUSE_SECONDS_B1)),
        (f"Voice 3 body ({voice_3})", b1["point_three"]),
        ("pause_1.0", p9a.silence_stereo(asm.AOEDE_TO_CHARON_PAUSE_SECONDS)),
        ("Comment 3 (Charon, 3V draft wording)", b1["comment_3"]),
        ("pause_0.8", p9a.silence_stereo(asm.CHARON_TO_AOEDE_PAUSE_SECONDS)),
        ("Tension: Why They See It Differently (Aoede, no heading)", b1[b1prod.EXTRA_SEGMENT_NAME]),
        ("pause_1.0", p9a.silence_stereo(asm.AOEDE_TO_CHARON_PAUSE_SECONDS)),
        ("Comment 4 (Charon)", b1["comment_4"]),
        ("pause_0.8", p9a.silence_stereo(asm.CHARON_TO_AOEDE_PAUSE_SECONDS)),
        ("Closing: What This Question Really Means (Aoede, no heading, In One Line)", b1["in_one_line"]),
        ("pause_0.8_in_one_line_to_outro", p9a.silence_stereo(asm.IN_ONE_LINE_TO_OUTRO_PAUSE_SECONDS)),
        ("Outro (Charon)", parts["outro"]),
    ]
    return seq


def run_assembly_3v(voice_1: str, voice_2: str, voice_3: str) -> dict:
    os.makedirs(f"{OUT_B1_DIR}/assembled", exist_ok=True)
    os.makedirs(f"{OUT_B1_DIR}/audit", exist_ok=True)

    try:
        sources = load_b1_sources_3v(OUT_B1_DIR)
    except RuntimeError as e:
        print(f"[3V-AUDIO-TRIAL] Assembly GATE_BLOCKED(override無し、報告のみ): {e}")
        summary = {"status": "GATE_BLOCKED", "error": str(e), "voice_1": voice_1, "voice_2": voice_2, "voice_3": voice_3}
        save_json(f"{OUT_B1_DIR}/run_summary_assemble.json", summary)
        return summary

    parts = asm.apply_b1_gain(sources)  # Production、無変更(汎用実装のため3声でもそのまま動作)
    seq = build_b1_voices_timeline_3v(parts, voice_1, voice_2, voice_3)  # Trial側新規(3声専用)
    result = asm.assemble_with_timeline(seq)  # Production、無変更(汎用list処理)
    headroom = asm.apply_headroom_safety_valve(result["assembled"], seq)  # Production、無変更
    assembled = headroom["assembled"]

    out_path = f"{OUT_B1_DIR}/assembled/B_Family_3V_Audio_Trial_01_B1B.wav"
    save_json(f"{OUT_B1_DIR}/audit/gain_report.json", parts["gain_report"])
    save_json(f"{OUT_B1_DIR}/audit/timeline.json", result["timeline"])
    save_json(f"{OUT_B1_DIR}/audit/headroom_report.json", headroom["report"])
    common.write_wav_float(out_path, assembled, asm.SR, 2)
    metrics = common.measure_metrics(assembled[:, 0], asm.SR)

    duration = result["total_duration_seconds"]
    duration_vs_target = {
        "target_min_seconds": TARGET_DURATION_MIN_SECONDS, "target_max_seconds": TARGET_DURATION_MAX_SECONDS,
        "actual_seconds": duration, "within_target_range": TARGET_DURATION_MIN_SECONDS <= duration <= TARGET_DURATION_MAX_SECONDS,
    }
    summary = {
        "status": "OK", "out_path": out_path, "duration_seconds": duration,
        "clipping_detected": metrics["clipping_detected"], "peak": round(p9a.peak(assembled), 5),
        "sample_rate": asm.SR, "channels": 2, "headroom_safety_valve": headroom["report"],
        "voice_1": voice_1, "voice_2": voice_2, "voice_3": voice_3, "duration_vs_target": duration_vs_target,
    }
    save_json(f"{OUT_B1_DIR}/run_summary_assemble.json", summary)
    print(f"[3V-AUDIO-TRIAL] Assembly status={summary['status']} duration={duration} "
          f"(target {TARGET_DURATION_MIN_SECONDS}-{TARGET_DURATION_MAX_SECONDS}s) "
          f"peak={summary['peak']} clipping={summary['clipping_detected']}")
    return summary


# ============================================================
# Step 6: 標準player.html(Gate 7 (a)〜(l)準拠、audio_review_player.py経由)
# ============================================================
def _row_info_3v(label: str, parts: dict, support_texts: dict, voice_1: str, voice_2: str, voice_3: str,
                  kp_by_rank: dict) -> dict:
    charon = "Charon"
    if label == "Intro":
        return {"text": "音楽ジングル(ナレーションなし、読み上げなし)。Intro.mp3をそのまま再生。",
                "voice": None, "audio": None, "sfx": True}
    if label == "Outro (Charon)":
        return {"text": "音楽ジングル(ナレーションなし、読み上げなし)。outro.mp3をそのまま再生。"
                        "ラベルに(Charon)とあるが実際はTTS読み上げではない固定音源。",
                "voice": None, "audio": None, "sfx": True}
    if label.startswith("Notification ") or label.startswith("Point Notification"):
        return {"text": "効果音(読み上げなし)", "voice": None, "audio": None, "sfx": True}
    if label == "Welcome (Charon)":
        return {"text": shared_narration.FIXED_ENGLISH_TEXTS["welcome"], "voice": charon,
                "audio": f"{NARRATION_DIR}/welcome_charon.wav", "sfx": False}
    if label == "Topic intro (Charon)":
        return {"text": f"Today's topic is {parts['title']}.", "voice": charon,
                "audio": f"{NARRATION_DIR}/topic_intro.wav", "sfx": False}
    if label == "Preview intro (Charon)":
        return {"text": shared_narration.FIXED_ENGLISH_TEXTS["preview_intro"], "voice": charon,
                "audio": f"{NARRATION_DIR}/preview_intro_charon.wav", "sfx": False}
    if label == "Preview (Charon)":
        return {"text": support_texts["preview"], "voice": charon,
                "audio": f"{NARRATION_DIR}/preview.wav", "sfx": False}
    if label == "Key phrases intro (Charon)":
        return {"text": shared_narration.FIXED_ENGLISH_TEXTS["key_phrases_intro"], "voice": charon,
                "audio": f"{NARRATION_DIR}/key_phrases_intro_charon.wav", "sfx": False}
    if label.startswith("Key Phrase "):
        rank = int(label.split(" ")[-1])
        kp = kp_by_rank[rank]
        en = kp["used_form"]
        ja = kp["japanese_gloss"]
        ja_tts = kp.get("japanese_gloss_tts", ja)
        text = f"EN: {en}<br>JA(表示): {ja}" + ("" if ja_tts == ja else f"<br>JA(TTS用): {ja_tts}")
        return {"text": text, "voice": "Aoede(EN)/Charon(JA)",
                "audio": (f"{NARRATION_DIR}/kp{rank}_en.wav", f"{NARRATION_DIR}/kp{rank}_ja_charon.wav"),
                "sfx": False}
    if label == "Full story intro (Charon)":
        return {"text": shared_narration.FIXED_ENGLISH_TEXTS["full_story_intro"], "voice": charon,
                "audio": f"{NARRATION_DIR}/full_story_intro_charon.wav", "sfx": False}
    if label.startswith("Comment 1 "):
        return {"text": support_texts["comment_1"], "voice": charon, "audio": f"{NARRATION_DIR}/comment_1.wav", "sfx": False}
    if label.startswith("Comment 2 "):
        return {"text": support_texts["comment_2"], "voice": charon, "audio": f"{NARRATION_DIR}/comment_2.wav", "sfx": False}
    if label.startswith("Comment 3 "):
        return {"text": support_texts["comment_3"], "voice": charon, "audio": f"{NARRATION_DIR}/comment_3.wav", "sfx": False}
    if label.startswith("Comment 4 "):
        return {"text": support_texts["comment_4"], "voice": charon, "audio": f"{NARRATION_DIR}/comment_4.wav", "sfx": False}
    if label.startswith("Hook Part 1"):
        return {"text": parts["part1"], "voice": "Aoede", "audio": f"{NARRATION_DIR}/full_story_part1.wav", "sfx": False}
    if label.startswith("Hook Part 2"):
        return {"text": parts["part2"], "voice": "Aoede", "audio": f"{NARRATION_DIR}/full_story_part2.wav", "sfx": False}
    if label.startswith("Narrator: Voice 1 heading"):
        return {"text": parts["point_one_heading"], "voice": "Aoede (Narrator)",
                "audio": f"{NARRATION_DIR}/point_one_heading.wav", "sfx": False}
    if label.startswith("Voice 1 body"):
        return {"text": parts["point_one_body"], "voice": voice_1, "audio": f"{NARRATION_DIR}/point_one.wav", "sfx": False}
    if label.startswith("Narrator: Voice 2 heading"):
        return {"text": parts["point_two_heading"], "voice": "Aoede (Narrator)",
                "audio": f"{NARRATION_DIR}/point_two_heading.wav", "sfx": False}
    if label.startswith("Voice 2 body"):
        return {"text": parts["point_two_body"], "voice": voice_2, "audio": f"{NARRATION_DIR}/point_two.wav", "sfx": False}
    if label.startswith("Narrator: Voice 3 heading"):
        return {"text": parts["point_three_heading"], "voice": "Aoede (Narrator)",
                "audio": f"{NARRATION_DIR}/point_three_heading.wav", "sfx": False}
    if label.startswith("Voice 3 body"):
        return {"text": parts["point_three_body"], "voice": voice_3, "audio": f"{NARRATION_DIR}/point_three.wav", "sfx": False}
    if label.startswith("Tension:"):
        return {"text": parts["tension_body"], "voice": "Aoede",
                "audio": f"{NARRATION_DIR}/{b1prod.EXTRA_SEGMENT_NAME}.wav", "sfx": False}
    if label.startswith("Closing:"):
        return {"text": parts["in_one_line"], "voice": "Aoede", "audio": f"{NARRATION_DIR}/in_one_line.wav", "sfx": False}
    return {"text": "【未取得】このラベルに対応するscript textを本スクリプトのマッピングで特定できませんでした。",
            "voice": None, "audio": None, "sfx": False}


def build_player_html_3v(assemble_summary: dict, timeline: list, parts: dict, support_texts: dict,
                          voice_1: str, voice_2: str, voice_3: str, gate_results: dict) -> str:
    kp_data = load_json(f"{OUT_B1_DIR}/key_phrases/keywords_canonicalized.json")
    kp_by_rank = {item["rank"]: item for item in kp_data["items"]}
    abs_url = player_common.abs_file_url

    rows = []
    for entry in timeline:
        label = entry["part"]
        if label.startswith("pause_"):
            continue
        info = _row_info_3v(label, parts, support_texts, voice_1, voice_2, voice_3, kp_by_rank)
        sec = entry["start_seconds"]
        voice_disp = info["voice"] or ("SFX" if info["sfx"] else "—")
        if info["sfx"]:
            audio_html = "—"
        elif isinstance(info["audio"], tuple):
            audio_html = player_common.render_single_audio_html(tuple(abs_url(p) for p in info["audio"]))
        elif info["audio"]:
            audio_html = player_common.render_single_audio_html(abs_url(info["audio"]))
        else:
            audio_html = "—"
        rows.append(player_common.render_timeline_row(
            sec, label, voice_disp, info["text"], audio_html, missing="未取得" in info["text"]))
    timeline_table = player_common.render_timeline_table(rows)

    kp_rows = []
    for rank in sorted(kp_by_rank):
        kp = kp_by_rank[rank]
        kp_rows.append(f'<tr><td>{rank}</td><td>{kp["used_form"]}</td><td>{kp["japanese_gloss"]}</td>'
                        f'<td>{kp.get("japanese_gloss_tts", kp["japanese_gloss"])}</td>'
                        f'<td>{kp.get("qa_overall_status")}</td></tr>')
    kp_table = ('<table class="kp"><thead><tr><th>#</th><th>English(used_form)</th><th>表示用gloss</th>'
                '<th>TTS用テキスト</th><th>redundancy QA</th></tr></thead>'
                f'<tbody>{"".join(kp_rows)}</tbody></table>')

    episode_audio_url = abs_url(assemble_summary["out_path"])
    dvt = assemble_summary.get("duration_vs_target", {})
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>EDITORIAL-B-FAMILY-VOICES-3V-AUDIO-TRIAL-01 player</title>
<style>
{player_common.PLAYER_STANDARD_CSS}
</style>
<script>
{player_common.SEEK_SCRIPT}
</script>
</head><body>
<h1>EDITORIAL-B-FAMILY-VOICES-3V-AUDIO-TRIAL-01(3 Voices Audio Trial候補、未承認・Production採用前)</h1>
<p class="note">
完成episode(1本化wav、Standard同期、B1のみ、3 Voices)。Audio Trial runner
(er012_editorial_b_voices_3v_audio_trial_01.py)による生成。Production/registryは無編集。
duration={assemble_summary['duration_seconds']}s(目標{dvt.get('target_min_seconds')}〜{dvt.get('target_max_seconds')}s、
範囲内={dvt.get('within_target_range')}) peak={assemble_summary['peak']}
clipping={assemble_summary['clipping_detected']}
headroom_safety_valve_applied={assemble_summary['headroom_safety_valve']['applied']}。
voice_1={voice_1}(応募者) / voice_2={voice_2}(採用担当) / voice_3={voice_3}(経営者)
(Narrator見出しは全てAoede固定、Comment 1-4はCharon固定)。
Audio Validation Gate: 既定OFF経路={gate_results['default_off']['status']} /
opt-in ON経路(3V required_structure)={gate_results['opt_in_on']['status']}。
Comment 2・3は3V版ドラフト文言(design.md B-1、未承認・Trial-only、LLM再生成なし)。
各行に「Seek」「Segment名+voice」「実際に読み上げられたscript」「個別音声」を
同一行に配置(標準player形式、PM-GOVERNANCE-AUDIO-REVIEW-PLAYER-STANDARD-FORMAT-11)。
</p>

<h2>Episode audio</h2>
<audio id="episode_audio" class="main" controls preload="none" src="{episode_audio_url}"></audio>

<h2>タイムライン・全スクリプト(収録順、同一行にSeek+voice+script)</h2>
{timeline_table}

<h2>Key Phrase表(詳細、英語+日本語gloss)</h2>
{kp_table}

</body></html>
"""
    out_path = f"{OUT_DIR}/player.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    return out_path


# ============================================================
# Fact/content integrity check(記事本文とTTS入力の一致確認、byte単位)
# ============================================================
def run_content_integrity_check(article_text: str, parts: dict, kp_merged: dict) -> dict:
    """build_parts_3v()が記事本文から抽出したtext(TTSへ渡すtts_safe_*変換
    前の原文)が、実際の記事本文の該当section内に完全一致で含まれるかを
    確認する(6区切りparserの抽出誤りが無いことのevidence)。TTS入力自体は
    tts_gen.tts_safe_*()による記号正規化[句読点・数字読み等]を経るため、
    その変換後との完全byte一致ではなく、変換前のsource textが記事本文の
    正しい抜粋であることを検証する設計(既存Productionと同じ検証粒度)。"""
    checks = {}
    for key, body_key in (("voice_1", "point_one_body"), ("voice_2", "point_two_body"),
                           ("voice_3", "point_three_body")):
        checks[body_key] = parts[body_key] in article_text
    checks["tension_body"] = parts["tension_body"] in article_text
    checks["in_one_line"] = parts["in_one_line"] in article_text
    checks["hook_part1_and_part2_reconstruct_hook_body"] = (
        (parts["part1"] + " " + parts["part2"]).replace("  ", " ") in
        (parts["sections"]["hook_body"]).replace("  ", " ")
        or (parts["part1"] + parts["part2"]) == parts["sections"]["hook_body"].replace(" ", "")
    )
    all_ok = all(v for k, v in checks.items() if k != "hook_part1_and_part2_reconstruct_hook_body")
    kp_used_forms_in_article = {
        item["used_form"]: (item["used_form"] in article_text) for item in kp_merged["items"]}
    result = {"section_body_substring_checks": checks, "all_section_bodies_verbatim_from_article": all_ok,
              "key_phrase_used_form_appears_in_article": kp_used_forms_in_article}
    save_json(f"{OUT_B1_DIR}/audit/content_integrity_check.json", result)
    return result


# ============================================================
# main
# ============================================================
def main() -> None:
    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)
    cl.install(COST_LOG_PATH)

    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    needs_prep = stage in ("prepare", "voice_check", "kp", "scaffold", "tts", "all")

    if stage in ("prepare", "all"):
        prep = prepare()
    elif needs_prep:
        prep = {"article_text": open(ARTICLE_PATH, encoding="utf-8").read()}
        prep["parts"] = load_json(f"{OUT_B1_DIR}/parts.json")

    if stage in ("voice_check", "all"):
        vc = voice_check(prep["parts"])
        voice_1, voice_2, voice_3 = vc["voice_1"], vc["voice_2"], vc["voice_3"]
    elif stage in ("tts", "assemble", "player", "all"):
        resolution = load_json(f"{OUT_DIR}/audit/voice_resolution.json")
        voice_1, voice_2, voice_3 = resolution["voice_1"], resolution["voice_2"], resolution["voice_3"]

    kp_merged = None
    if stage in ("kp", "all"):
        kp_canon_path = f"{OUT_B1_DIR}/key_phrases/keywords_canonicalized.json"
        if os.path.exists(kp_canon_path):
            # LLM選定/canonicalizationは既に完了済み(前回runで保存済み)の
            # ためLLM呼び出しを重複させない(冪等な再実行、追加費用ゼロ)。
            print("[3V-AUDIO-TRIAL] Key Phrase選定/canonicalizationは既存出力を再利用(重複LLM呼び出しを回避)")
            kp_merged = load_json(kp_canon_path)
        else:
            kp_merged = run_key_phrases(prep["article_text"])
        run_key_phrase_tts(kp_merged)
        assert_budget_ok("after Key Phrase TTS")
    elif stage in ("assemble", "player"):
        kp_merged = load_json(f"{OUT_B1_DIR}/key_phrases/keywords_canonicalized.json")

    if stage in ("scaffold", "all"):
        sections = split_six_voice_sections(prep["article_text"])
        scaffold_result = run_scaffold_3v(prep["parts"], prep["article_text"], sections)
        save_json(f"{OUT_DIR}/audit/scaffold_summary.json", {"support_status": scaffold_result["support_status"]})

    if stage in ("tts", "all"):
        support_texts = load_json(f"{OUT_B1_DIR}/b1_support_texts.json")
        new_results = run_tts_3v(prep["parts"], support_texts, voice_1, voice_2, voice_3)
        kp_tts_results_raw = load_json(f"{OUT_B1_DIR}/audit/kp_tts_results.json")
        kp_tts_results = {int(rank): v for rank, v in kp_tts_results_raw.items()}
        finalize_tts_results_3v(new_results, kp_tts_results)
        run_audio_gate_both_paths(voice_1, voice_2, voice_3)
        run_content_integrity_check(prep["article_text"], prep["parts"],
                                     kp_merged or load_json(f"{OUT_B1_DIR}/key_phrases/keywords_canonicalized.json"))

    if stage in ("assemble", "all"):
        assemble_summary = run_assembly_3v(voice_1, voice_2, voice_3)

    if stage in ("player", "all"):
        parts = load_json(f"{OUT_B1_DIR}/parts.json")
        support_texts = load_json(f"{OUT_B1_DIR}/b1_support_texts.json")
        assemble_summary = load_json(f"{OUT_B1_DIR}/run_summary_assemble.json")
        timeline_path = f"{OUT_B1_DIR}/audit/timeline.json"
        timeline = load_json(timeline_path) if os.path.exists(timeline_path) else []
        gate_results = load_json(f"{OUT_B1_DIR}/audit/audio_gate_both_paths.json")
        if assemble_summary.get("status") == "OK":
            player_path = build_player_html_3v(
                assemble_summary, timeline, parts, support_texts, voice_1, voice_2, voice_3, gate_results)
            print(f"[3V-AUDIO-TRIAL] player.html: {os.path.abspath(player_path)}")
        else:
            print(f"[3V-AUDIO-TRIAL] Assembly未完了(status={assemble_summary.get('status')})のため"
                  "player.htmlは生成しません。")

    jpy, by_provider = compute_cost_jpy_so_far()
    print(f"[3V-AUDIO-TRIAL] 完了(stage={stage})。累積cost={jpy:.2f} JPY by_provider={by_provider}")


if __name__ == "__main__":
    main()
