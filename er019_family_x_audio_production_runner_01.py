# ============================================================
# er019_family_x_audio_production_runner_01.py
# NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01 (Stage 1: 実装+オフラインtest)
# ============================================================
# Family X(Entertainment News)の後工程(3分割・Comment配置・TTS・
# Assembly)のProduction配線。ユーザー正式採用済み(APPROVED_FOR_
# PRODUCTION、2026-09-27)の音声構造(CURRENT_SPEC.md「Family X
# (Entertainment News)音声構造」節)を実装する。
#
# 本Stage(Stage 1)ではTTS/ASR/LLMの実API呼び出しを一切行わない
# (--dry-run既定、常に¥0)。scaffold/tts stageのコードはStage 2以降で
# 実行する(本ファイルにも実装するが、本セッションでは実行しない)。
#
# 既存Production module(er003_*/er012_*/
# er019_family_x_entertainment_production_runner_01.py/er020_*/
# er006_*)は一切編集しない(import・関数呼び出しのみ)。既存関数の
# 変更が不可欠と判明した場合はSTOPし、RESULT_PACKETへ必要変更点を記録
# する方針(本ファイルのdocstring/コメントに個別のSTOP検討記録あり)。
#
# 実行方法:
#   .venv/Scripts/python.exe er019_family_x_audio_production_runner_01.py \
#       --slug <er019_output配下のディレクトリ名> --run <run_01等> \
#       --level a2|b1b|both --stage plan|scaffold|tts|assemble|all \
#       [--dry-run] [--out-dir <出力先、既定は自動導出>]
#
# 入力article.mdの場所: er019_output/<slug>/<run>/{b1b,a2}/article.md
# (Family X正式runner`er019_family_x_entertainment_production_
# runner_01.py`の出力規約と同一)。
# 出力先(既定): er019_output/family_x_audio_production_wiring_01/
#   <slug>__<run>/{b1b,a2}/...(入力ディレクトリを汚さない。他の
#   management IDの既存出力[例: family_x_b3_production_wiring_01]を
#   上書きしないため、専用の新規出力ツリーへ書く)。
# ============================================================
from __future__ import annotations

import argparse
import hashlib
import json
import os

import audio_review_player as player_common
import er003_v1_b1_scaffold_01_generate as b1s
import er003_v1_crosslevel_audio_02_common as crosslevel_common
import er003_v1_iran01_a2_generate as a2gen
import er003_v1_n3_01_assemble as asm
import er003_v1_n3_01_scaffold_generate as sc
import er003_v1_n3_01_tts_generate as n3_tts
import er003_v1_sing01_news_tail_fix as news_tail_fix
import er003_v1_sing01_voice01_generate as voice01
import er005_cost_logger as cl
import er006_audio_cost_pilot_02_shared_narration as shared_narration
import er006_model_routing_contract_01 as routing
import er019_family_x_audio_plan_01 as plan
import er020_tts_retry_local_rewrite_01 as retry_primitive

MANAGEMENT_ID = "NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01"

# 要件3の確認結果(コードで確認、STOP不要): full_story_part1/2/3は
# er020_tts_retry_local_rewrite_01.resolve_narrative_role()に既に
# ハードコードされておりFULL_STORYへ解決される(er020編集不要)。
_REQUIRED_FULL_STORY_SEGMENT_IDS = ("full_story_part1", "full_story_part2", "full_story_part3")
for _seg_id in _REQUIRED_FULL_STORY_SEGMENT_IDS:
    _role = retry_primitive.resolve_narrative_role(_seg_id)
    if _role != "FULL_STORY":
        raise RuntimeError(
            f"[{MANAGEMENT_ID}] STOP: segment_id={_seg_id!r} が"
            f"resolve_narrative_role()でFULL_STORYへ解決されません(実際: {_role!r})。"
            "er020_tts_retry_local_rewrite_01.pyの編集が必要になるため、実装せず"
            "RESULT_PACKETへ報告してください。")


# ------------------------------------------------------------
# 共通ヘルパー
# ------------------------------------------------------------
def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, default=str)


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def save_text(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def _b1_support_model() -> str:
    return routing.require_model("B1_SUPPORT", routing.SUPPORT_MODEL)


def _a2_support_model() -> str:
    return routing.require_model("A2_SUPPORT", routing.SUPPORT_MODEL)


def derive_out_dir(source_slug: str, source_run: str, out_dir_override: str | None) -> str:
    if out_dir_override:
        return out_dir_override
    return f"er019_output/family_x_audio_production_wiring_01/{source_slug}__{source_run}"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ------------------------------------------------------------
# Stage 3a(実行時に判明した所有ファイル内バグの最小修正、実行本体は
# 別途RESULT_PACKETへ報告):
#   1. A2 segment_id="japanese_title"(FAMILY_X_A2_SEGMENT_ORDER)の実際の
#      読み上げ対象は日本語タイトルでなければならないが、Stage 1時点の
#      main()はa2/article.mdの英語titleをそのまま渡すplaceholderだった
#      (Stage 1では--stage all未実行のため顕在化しなかった)。本Runの
#      入力directory(source_dir直下)には既存正式path
#      (NEWS-FAMILY-X-JA-FACT-CHECK-PRODUCTION-WIRING-01)が生成した
#      ja_writer/runtime_evidence.json["title"]が存在するため、これを
#      日本語タイトルの一次ソースとする(無ければrevision2.md/original.md
#      の一行目、それも無ければ旧placeholder動作にfall backしてログへ
#      警告を残す)。
#   2. run_plan_stage()のarticle_sha256が常にNone固定になっていたため、
#      実際のsha256を計算するよう修正する(入力article.md不変性の記録用)。
# ------------------------------------------------------------
def derive_japanese_title(source_dir: str) -> dict:
    """戻り値: {"japanese_title": str, "source": str}。"""
    evidence_path = f"{source_dir}/ja_writer/runtime_evidence.json"
    if os.path.exists(evidence_path):
        evidence = load_json(evidence_path)
        title = evidence.get("title")
        if title:
            return {"japanese_title": title, "source": evidence_path}
    for name in ("revision2.md", "revision1.md", "original.md"):
        p = f"{source_dir}/ja_writer/{name}"
        if os.path.exists(p):
            first_line = load_text(p).splitlines()[0].strip()
            if first_line:
                return {"japanese_title": first_line, "source": p}
    return {"japanese_title": None, "source": None}


# ============================================================
# Stage: plan(dry-run、API呼び出しなし)
# ============================================================
def build_segment_plan(level: str, parts: dict, support: dict | None = None) -> dict:
    """level="b1b"|"a2"。supportがNone(scaffold未実行)の場合、Comment/
    Previewのtextはplan上「(未生成)」として扱う(dry-runでも実行可能)。"""
    order = plan.FAMILY_X_B1_SEGMENT_ORDER if level == "b1b" else plan.FAMILY_X_A2_SEGMENT_ORDER
    text_by_segment_id = {
        "full_story_part1": parts["part1"], "full_story_part2": parts["part2"],
        "full_story_part3": parts["part3"], "in_one_line": parts["in_one_line"],
    }
    if support:
        for name in ("preview", "comment_1", "comment_2", "comment_3", "comment_4"):
            text_by_segment_id[name] = support.get(name)

    rows = []
    for label, segment_id, plan_role in order:
        entry = {"label": label, "segment_id": segment_id, "plan_role": plan_role}
        if segment_id and segment_id in text_by_segment_id:
            text = text_by_segment_id[segment_id]
            entry["text_available"] = text is not None
            if text is not None:
                if level == "b1b" or plan_role == "FULL_STORY" or plan_role in ("TOPIC_INTRO",):
                    entry["estimated_seconds"] = plan.estimate_seconds_english(text)
                else:
                    entry["estimated_seconds"] = plan.estimate_seconds_japanese(text)
        else:
            entry["text_available"] = None  # SFX/固定共有/Key Phrase(件数はscaffold実行後に確定)
        # narrative role確認(要件3、経路ごとの個別ハードコードではなく
        # 単一関数を必ず参照する)。
        if segment_id:
            entry["resolved_narrative_role"] = retry_primitive.resolve_narrative_role(segment_id)
            entry["connected_speech_enabled"] = retry_primitive.connected_speech_enabled_for(segment_id)
        rows.append(entry)

    body_seconds = sum(
        r.get("estimated_seconds", 0.0) for r in rows if r.get("plan_role") == "FULL_STORY")
    return {
        "level": level,
        "segments": rows,
        "body_word_counts": parts.get("word_counts"),
        "estimated_body_seconds_total": round(body_seconds, 1),
        "no_point_structure": True,
        "no_new_sfx_after_body_start": True,
    }


def run_plan_stage(source_dir: str, out_dir: str, levels: list[str]) -> dict:
    result = {}
    for level in levels:
        article_path = f"{source_dir}/{level}/article.md"
        if not os.path.exists(article_path):
            result[level] = {"status": "SOURCE_ARTICLE_NOT_FOUND", "article_path": article_path}
            continue
        article_text = load_text(article_path)
        try:
            parts = plan.split_family_x_article_text(article_text)
        except RuntimeError as e:
            result[level] = {"status": "SPLIT_FAILED", "error": str(e), "article_path": article_path}
            continue

        support_path = f"{out_dir}/{level}/b1_support_texts.json" if level == "b1b" \
            else f"{out_dir}/{level}/a2_support_texts.json"
        support = load_json(support_path) if os.path.exists(support_path) else None

        save_json(f"{out_dir}/{level}/parts.json", parts)
        segment_plan = build_segment_plan(level, parts, support)
        save_json(f"{out_dir}/{level}/segment_plan.json", segment_plan)
        result[level] = {"status": "OK", "article_path": article_path,
                          "article_sha256": sha256_text(article_text), "segment_plan": segment_plan}
    return result


# ============================================================
# Stage: scaffold(Comment1-4/Preview生成 + Key Phrase、実API呼び出し
# あり。Stage 1では実行しない)
# ============================================================
def run_family_x_b1_scaffold(client, parts: dict, out_dir: str) -> dict:
    """B1(English)Preview/Comment1-4を生成する。Comment1/2/PreviewはPoint
    前提を持たないため既存b1s.COMMENT_1_ROLE/COMMENT_2_ROLE/PREVIEW_ROLEを
    無変更のまま流用する。Comment3/4のみFamily X用role
    (er019_family_x_audio_plan_01.FAMILY_X_B1_COMMENT_3/4_ROLE)を使う。"""
    print(f"[FAMILY-X-AUDIO-SCAFFOLD] B1 Comment 1生成開始({out_dir})...")
    c1_context = f"【これから聞く本文(本文1)】\n{parts['part1']}"
    c1 = b1s.run_support_text(client, b1s.COMMENT_1_ROLE, c1_context, model=_b1_support_model())

    print(f"[FAMILY-X-AUDIO-SCAFFOLD] B1 Comment 2生成開始({out_dir})...")
    c2_context = f"【すでに聞いた本文(本文1)】\n{parts['part1']}\n\n【これから聞く本文(本文2)】\n{parts['part2']}"
    c2 = b1s.run_support_text(client, b1s.COMMENT_2_ROLE, c2_context, model=_b1_support_model())

    print(f"[FAMILY-X-AUDIO-SCAFFOLD] B1 Comment 3生成開始({out_dir})...")
    c3_context = f"【本文1】\n{parts['part1']}\n\n【本文2】\n{parts['part2']}"
    c3 = b1s.run_support_text(client, plan.FAMILY_X_B1_COMMENT_3_ROLE, c3_context, model=_b1_support_model())

    print(f"[FAMILY-X-AUDIO-SCAFFOLD] B1 Comment 4生成開始({out_dir})...")
    c4_context = f"【本文1】\n{parts['part1']}\n\n【本文2】\n{parts['part2']}\n\n【本文3】\n{parts['part3']}"
    c4 = b1s.run_support_text(client, plan.FAMILY_X_B1_COMMENT_4_ROLE, c4_context, model=_b1_support_model())

    print(f"[FAMILY-X-AUDIO-SCAFFOLD] B1 Preview生成開始({out_dir})...")
    preview_prompt_role = b1s.PREVIEW_ROLE.format(
        comment_1=c1.get("text") or "(生成失敗)", comment_2=c2.get("text") or "(生成失敗)")
    article_text = plan.reconstruct_family_x_article_text(parts)
    preview_context = f"【エピソード全文(参考、新しいFactの追加禁止)】\n{article_text}"
    preview = b1s.run_support_text(client, preview_prompt_role, preview_context, model=_b1_support_model())

    results = {"preview": preview, "comment_1": c1, "comment_2": c2, "comment_3": c3, "comment_4": c4}
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    save_json(f"{out_dir}/b1_support_texts.json", {k: v.get("text") for k, v in results.items()})
    save_json(f"{out_dir}/audit/b1_support_generation.json", results)
    return results


def run_family_x_a2_scaffold(client, parts: dict, out_dir: str) -> dict:
    """A2(Japanese)Preview/Comment1-4を生成する(単一Voice、a2genの
    Comment1/2/PreviewをそのままJapanese出力で流用)。"""
    print(f"[FAMILY-X-AUDIO-SCAFFOLD] A2 Comment 1生成開始({out_dir})...")
    c1_context = f"【これから聞く本文(本文1、英語)】\n{parts['part1']}"
    c1 = a2gen.run_support_text(client, a2gen.COMMENT_1_ROLE, c1_context, model=_a2_support_model())

    print(f"[FAMILY-X-AUDIO-SCAFFOLD] A2 Comment 2生成開始({out_dir})...")
    c2_context = f"【すでに聞いた本文(本文1)】\n{parts['part1']}\n\n【これから聞く本文(本文2)】\n{parts['part2']}"
    c2 = a2gen.run_support_text(client, a2gen.COMMENT_2_ROLE, c2_context, model=_a2_support_model())

    print(f"[FAMILY-X-AUDIO-SCAFFOLD] A2 Comment 3生成開始({out_dir})...")
    c3_context = f"【本文1】\n{parts['part1']}\n\n【本文2】\n{parts['part2']}"
    c3 = a2gen.run_support_text(client, plan.FAMILY_X_A2_COMMENT_3_ROLE, c3_context, model=_a2_support_model())

    print(f"[FAMILY-X-AUDIO-SCAFFOLD] A2 Comment 4生成開始({out_dir})...")
    c4_context = f"【本文1】\n{parts['part1']}\n\n【本文2】\n{parts['part2']}\n\n【本文3】\n{parts['part3']}"
    c4 = a2gen.run_support_text(client, plan.FAMILY_X_A2_COMMENT_4_ROLE, c4_context, model=_a2_support_model())

    print(f"[FAMILY-X-AUDIO-SCAFFOLD] A2 Preview生成開始({out_dir})...")
    preview_prompt_role = a2gen.PREVIEW_ROLE.format(
        comment_1=c1.get("text") or "(生成失敗)", comment_2=c2.get("text") or "(生成失敗)")
    article_text = plan.reconstruct_family_x_article_text(parts)
    preview_context = f"【エピソード全文(参考、新しいFactの追加禁止)】\n{article_text}"
    preview = a2gen.run_support_text(client, preview_prompt_role, preview_context, model=_a2_support_model())

    results = {"preview": preview, "comment_1": c1, "comment_2": c2, "comment_3": c3, "comment_4": c4}
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    save_json(f"{out_dir}/a2_support_texts.json", {k: v.get("text") for k, v in results.items()})
    save_json(f"{out_dir}/audit/a2_support_generation.json", results)
    return results


def run_theme_scaffold(client, source_dir: str, out_dir: str, levels: list[str]) -> dict:
    """既存sc.run_key_phrases()(選定+canonicalization+redundancy QA)を
    Family X本文へそのまま適用する(記事冒頭Key Phrasesは既存Family A
    既定構成をそのまま再利用する、本委任文の前提どおり)。"""
    result = {}
    for level in levels:
        article_path = f"{source_dir}/{level}/article.md"
        article_text = load_text(article_path)
        parts = plan.split_family_x_article_text(article_text)
        level_out_dir = f"{out_dir}/{level}"
        save_json(f"{level_out_dir}/parts.json", parts)

        if level == "b1b":
            support = run_family_x_b1_scaffold(client, parts, level_out_dir)
        else:
            support = run_family_x_a2_scaffold(client, parts, level_out_dir)

        kp_dir = f"{level_out_dir}/key_phrases"
        article_id = f"FAMILY_X_AUDIO_{os.path.basename(out_dir)}_{level}"
        kp_process = "B1_SUPPORT" if level == "b1b" else "A2_SUPPORT"
        kp = sc.run_key_phrases(article_text, kp_dir, article_id, level, process=kp_process)
        kp_status = (kp["canonicalization"] or {}).get("status") if kp["canonicalization"] else kp["selection"]["status"]
        print(f"[FAMILY-X-AUDIO-SCAFFOLD] {level}: key phrase status={kp_status}")

        result[level] = {"parts": parts, "support": {k: v.get("status") for k, v in support.items()},
                          "key_phrases_status": kp_status}
    save_json(f"{out_dir}/scaffold_run_summary.json", result)
    return result


# ============================================================
# Stage: tts(実API呼び出しあり。Stage 1では実行しない)
# ============================================================
_BODY_SEGMENT_NAMES = ("full_story_part1", "full_story_part2", "full_story_part3")


# ============================================================
# TTS-SYMBOL-NORMALIZATION-ALL-FAMILY-PRODUCTION-WIRING-01(2026-09-27):
# 前回run(同一out_dir)でstatus=="OK"だったsegment/Key Phrase componentは
# TTS呼び出しをスキップして再利用する(既存Gateの再判定自体は回避しない
# ——前回STOPPEDだったsegmentは対象外のまま常にgenerate_fn()で再実行し、
# 新Normalizer/GateでOKになるかを実際に確認する。wavファイルが実在しない
# 場合も再実行する)。
# ============================================================
def _load_cached_tts_results(out_dir: str) -> dict | None:
    cache_path = f"{out_dir}/audit/tts_generation_results.json"
    if not os.path.exists(cache_path):
        return None
    try:
        return load_json(cache_path)
    except Exception:
        return None


def _generate_or_reuse(cached: dict | None, name: str, wav_path: str, generate_fn):
    cached_result = (cached.get("segments") or {}).get(name) if cached else None
    if cached_result and cached_result.get("status") == "OK" and os.path.exists(wav_path):
        reused = dict(cached_result)
        reused["reused_from_previous_run"] = True
        return reused
    return generate_fn()


def _generate_or_reuse_kp(cached: dict | None, rank: int, role: str, wav_path: str, generate_fn):
    kp_cache = (cached.get("key_phrases") or {}) if cached else {}
    cached_result = (kp_cache.get(str(rank)) or kp_cache.get(rank) or {}).get(role) if kp_cache else None
    if cached_result and cached_result.get("status") == "OK" and os.path.exists(wav_path):
        reused = dict(cached_result)
        reused["reused_from_previous_run"] = True
        return reused
    return generate_fn()


def generate_family_x_b1_segments(theme_out_dir: str) -> dict:
    """既存Production低レベル関数(voice01.generate_charon_english/
    news_tail_fix.generate_news_narration_wide_margin)をそのまま呼ぶ。
    Comment/Preview=Charon英語、本文/In One Line=Aoede(News本文)、
    Key Phrase=既存Master Audio Store経由(shared_narration)。"""
    out_dir = f"{theme_out_dir}/b1b"
    narration_dir = f"{out_dir}/narration"
    os.makedirs(narration_dir, exist_ok=True)

    parts = load_json(f"{out_dir}/parts.json")
    support = load_json(f"{out_dir}/b1_support_texts.json")
    kp = load_json(f"{out_dir}/key_phrases/keywords_canonicalized.json")

    shared_narration.ensure_all_shared_narration_b1(narration_dir)
    _cached = _load_cached_tts_results(out_dir)

    results = {}
    topic_intro_text = f"Today's topic is {parts['title']}."
    with cl.segment_context("topic_intro"):
        results["topic_intro"] = _generate_or_reuse(
            _cached, "topic_intro", f"{narration_dir}/topic_intro.wav", lambda: voice01.generate_charon_english(
                n3_tts.tts_safe_number_words_en(n3_tts.tts_safe_en(topic_intro_text)),
                f"{narration_dir}/topic_intro.wav",
                enable_connected_speech_equivalence_layer=retry_primitive.connected_speech_enabled_for(
                    "topic_intro")))
    results["topic_intro"]["canonical_text"] = topic_intro_text

    for name in ("preview", "comment_1", "comment_2", "comment_3", "comment_4"):
        text = support[name]
        with cl.segment_context(name):
            results[name] = _generate_or_reuse(
                _cached, name, f"{narration_dir}/{name}.wav", lambda text=text, name=name: voice01.generate_charon_english(
                    n3_tts.tts_safe_number_words_en(n3_tts.tts_safe_en(text)), f"{narration_dir}/{name}.wav",
                    style_prefix_override=n3_tts.B1_PREVIEW_STYLE_PREFIX_CALM, disfluency_qa=True,
                    enable_connected_speech_equivalence_layer=retry_primitive.connected_speech_enabled_for(name)))
        results[name]["canonical_text"] = text

    for name, text in (
        ("full_story_part1", parts["part1"]), ("full_story_part2", parts["part2"]),
        ("full_story_part3", parts["part3"]), ("in_one_line", parts["in_one_line"]),
    ):
        with cl.segment_context(name):
            results[name] = _generate_or_reuse(
                _cached, name, f"{narration_dir}/{name}.wav",
                lambda text=text, name=name: news_tail_fix.generate_news_narration_wide_margin(
                    n3_tts.tts_safe_news_en(text), f"{narration_dir}/{name}.wav",
                    disfluency_qa=(name == "in_one_line"),
                    enable_connected_speech_equivalence_layer=retry_primitive.connected_speech_enabled_for(name),
                    enable_repetition_qa=(name in _BODY_SEGMENT_NAMES)))
        results[name]["canonical_text"] = text

    kp_results = _generate_key_phrase_segments_b1(kp, narration_dir, _cached)

    all_status = {k: v.get("status") for k, v in results.items()}
    kp_status = {r: {"en": v["english"].get("status"), "ja": v["japanese"].get("status")}
                 for r, v in kp_results.items()}
    save_json(f"{out_dir}/audit/tts_generation_results.json", {"segments": results, "key_phrases": kp_results})
    save_json(f"{out_dir}/run_summary_tts.json", {"segment_status": all_status, "key_phrase_status": kp_status})
    return {"segment_status": all_status, "key_phrase_status": kp_status}


def _generate_key_phrase_segments_b1(kp: dict, narration_dir: str, cached: dict | None = None) -> dict:
    kp_items = sorted(kp["items"], key=lambda it: it["rank"])
    kp_results = {}
    for item in kp_items:
        rank = item["rank"]
        used_form = item["used_form"]
        ja_gloss_tts, ja_gloss_tts_fallback = n3_tts.resolve_key_phrase_ja_gloss_tts(item)
        with cl.segment_context(f"kp{rank}_english"):
            en_r = _generate_or_reuse_kp(
                cached, rank, "english", f"{narration_dir}/kp{rank}_en.wav",
                lambda used_form=used_form, rank=rank: shared_narration.ensure_key_phrase_english_component(
                    n3_tts.tts_safe_kp_en(used_form), f"{narration_dir}/kp{rank}_en.wav"))
        with cl.segment_context(f"kp{rank}_japanese"):
            ja_r = _generate_or_reuse_kp(
                cached, rank, "japanese", f"{narration_dir}/kp{rank}_ja_charon.wav",
                lambda ja_gloss_tts=ja_gloss_tts, used_form=used_form,
                rank=rank: n3_tts.generate_charon_japanese_with_reading_safety(
                    ja_gloss_tts, f"{narration_dir}/kp{rank}_ja_charon.wav",
                    n3_tts.expected_substring_ja(ja_gloss_tts), known_key_phrase_terms=[used_form]))
        ja_r["display_gloss"] = item["japanese_gloss"]
        ja_r["japanese_gloss_tts_fallback_derived"] = ja_gloss_tts_fallback
        kp_results[rank] = {"english": en_r, "japanese": ja_r}
    return kp_results


def generate_family_x_a2_segments(theme_out_dir: str, japanese_title: str) -> dict:
    """既存Production低レベル関数(crosslevel_common.generate_english_
    segment_with_fallback経由のn3_tts.generate_a2_segment_with_slowdown、
    n3_tts.generate_a2_japanese_with_reading_safety)をそのまま呼ぶ。"""
    out_dir = f"{theme_out_dir}/a2"
    narration_dir = f"{out_dir}/narration"
    os.makedirs(narration_dir, exist_ok=True)

    parts = load_json(f"{out_dir}/parts.json")
    support = load_json(f"{out_dir}/a2_support_texts.json")
    kp = load_json(f"{out_dir}/key_phrases/keywords_canonicalized.json")

    shared_narration.ensure_all_shared_narration_a2(narration_dir)
    _cached = _load_cached_tts_results(out_dir)

    results = {}
    topic_intro_tts_title = parts.get("title_tts", parts["title"])
    topic_intro_text = f"Today's topic is {parts['title']}."
    topic_intro_tts_text = f"Today's topic is {topic_intro_tts_title}."
    with cl.segment_context("topic_intro"):
        results["topic_intro"] = _generate_or_reuse(
            _cached, "topic_intro", f"{narration_dir}/topic_intro.wav",
            lambda: crosslevel_common.generate_english_segment_with_fallback(
                n3_tts.tts_safe_number_words_en(n3_tts.tts_safe_en(topic_intro_tts_text)),
                f"{narration_dir}/topic_intro.wav", n3_tts.first_words(parts["title"], 3), max_extra_chars=30,
                enable_connected_speech_equivalence_layer=retry_primitive.connected_speech_enabled_for(
                    "topic_intro")))
    results["topic_intro"]["canonical_text"] = topic_intro_text

    with cl.segment_context("japanese_title"):
        results["japanese_title"] = _generate_or_reuse(
            _cached, "japanese_title", f"{narration_dir}/japanese_title.wav",
            lambda: n3_tts.generate_a2_japanese_with_reading_safety(
                japanese_title, f"{narration_dir}/japanese_title.wav",
                n3_tts.expected_substring_ja(japanese_title), max_extra_chars=30))

    for name in ("preview", "comment_1", "comment_2", "comment_3", "comment_4"):
        text = support[name]
        with cl.segment_context(name):
            results[name] = _generate_or_reuse(
                _cached, name, f"{narration_dir}/{name}.wav",
                lambda text=text: n3_tts.generate_a2_japanese_with_reading_safety(
                    text, f"{narration_dir}/{name}.wav", n3_tts.expected_substring_ja(text)))

    for name, text in (
        ("full_story_part1", parts["part1"]), ("full_story_part2", parts["part2"]),
        ("full_story_part3", parts["part3"]), ("in_one_line", parts["in_one_line"]),
    ):
        tts_input = n3_tts.tts_safe_news_en(text)
        sub = n3_tts.first_words(text)
        with cl.segment_context(name):
            results[name] = _generate_or_reuse(
                _cached, name, f"{narration_dir}/{name}.wav",
                lambda tts_input=tts_input, sub=sub, name=name: n3_tts.generate_a2_segment_with_slowdown(
                    tts_input, f"{narration_dir}/{name}.wav", sub,
                    style_prefix_override=n3_tts.A2_ENGLISH_STYLE_PREFIX_SLOWER,
                    disfluency_qa=(name == "in_one_line"),
                    enable_connected_speech_equivalence_layer=retry_primitive.connected_speech_enabled_for(name),
                    enable_repetition_qa=(name in _BODY_SEGMENT_NAMES)))
        results[name]["canonical_text"] = text

    kp_results = _generate_key_phrase_segments_a2(kp, narration_dir, _cached)

    all_status = {k: v.get("status") for k, v in results.items()}
    kp_status = {r: {"en": v["english"].get("status"), "ja": v["japanese_meaning"].get("status")}
                 for r, v in kp_results.items()}
    save_json(f"{out_dir}/audit/tts_generation_results.json", {"segments": results, "key_phrases": kp_results})
    save_json(f"{out_dir}/run_summary_tts.json", {"segment_status": all_status, "key_phrase_status": kp_status})
    return {"segment_status": all_status, "key_phrase_status": kp_status}


def _generate_key_phrase_segments_a2(kp: dict, narration_dir: str, cached: dict | None = None) -> dict:
    kp_items = sorted(kp["items"], key=lambda it: it["rank"])
    kp_results = {}
    for i, item in enumerate(kp_items, start=1):
        rank = item["rank"]
        used_form = item["used_form"]
        ja_gloss_tts, ja_gloss_tts_fallback = n3_tts.resolve_key_phrase_ja_gloss_tts(item)
        with cl.segment_context(f"kp{rank}_english"):
            en_r = _generate_or_reuse_kp(
                cached, rank, "english", f"{narration_dir}/kp{rank}_en.wav",
                lambda used_form=used_form, rank=rank: shared_narration.ensure_key_phrase_english_component(
                    n3_tts.tts_safe_kp_en(used_form), f"{narration_dir}/kp{rank}_en.wav"))
        with cl.segment_context(f"kp{rank}_japanese_meaning"):
            ja_r = _generate_or_reuse_kp(
                cached, rank, "japanese_meaning", f"{narration_dir}/meaning_{i}.wav",
                lambda ja_gloss_tts=ja_gloss_tts, used_form=used_form,
                i=i: n3_tts.generate_a2_japanese_with_reading_safety(
                    ja_gloss_tts, f"{narration_dir}/meaning_{i}.wav", n3_tts.expected_substring_ja(ja_gloss_tts),
                    max_extra_chars=30, known_key_phrase_terms=[used_form]))
        ja_r["display_gloss"] = item["japanese_gloss"]
        ja_r["japanese_gloss_tts_fallback_derived"] = ja_gloss_tts_fallback
        kp_results[rank] = {"english": en_r, "japanese_meaning": ja_r}
    return kp_results


# ============================================================
# Stage: assemble(既存asm.verify_episode_audio_validation_gate/
# assemble_with_timeline/apply_headroom_safety_valve/build_b1_key_
# phrase_blocks・build_a2_key_phrase_blocks/pause定数・gain定数は
# er003_v1_n3_01_assemble.py(asm)から無変更のまま再利用する。
# timeline builder・source loader・gain適用は、Point前提(Point
# Notification/Point見出し/Point本文)を持つ既存asm関数をそのまま流用
# できないため、Family X専用に新規定義する[pointless trial踏襲]。
# ============================================================
import er002_common as common  # noqa: E402
import er003_b1_p9a_audio as p9a  # noqa: E402

SR = asm.SR


def load_family_x_b1_sources(theme_out_dir: str) -> dict:
    out_dir = f"{theme_out_dir}/b1b"
    narration_dir = f"{out_dir}/narration"
    asm.verify_episode_audio_validation_gate(out_dir, "B1")

    intro = p9a.load_and_resample_to_target(p9a.INTRO_MP3_PATH)
    notification = p9a.load_and_resample_to_target(p9a.NOTIFICATION_MP3_PATH)
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
    for name in ("full_story_part1", "full_story_part2", "full_story_part3",
                  "comment_1", "comment_2", "comment_3", "comment_4", "preview", "in_one_line"):
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

    return {"intro": intro, "notification": notification, "outro": outro,
            "narration": narration, "b1_segments": b1_segments,
            "key_phrase_components": key_phrase_components, "key_phrase_meanings": key_phrase_meanings,
            "kp_items": kp_items}


def apply_family_x_b1_gain(sources: dict) -> dict:
    preview_mono = sources["b1_segments"]["preview"]
    full_story_part1_mono = sources["b1_segments"]["full_story_part1"]
    target_rms = (p9a.rms(preview_mono) + p9a.rms(full_story_part1_mono)) / 2
    gain_report = {"target_rms": round(target_rms, 5)}

    def gain_to_rms(data, target, label):
        gain = p9a.compute_gain_for_target_rms(data, target)
        gained = data * gain
        gain_report[label] = {"gain": round(float(gain), 4), "rms_before": round(p9a.rms(data), 5),
                               "rms_after": round(p9a.rms(gained), 5), "peak_after": round(p9a.peak(gained), 5)}
        return gained

    result = {}
    result["intro"] = gain_to_rms(sources["intro"]["samples"], target_rms, "intro")
    result["notification"] = gain_to_rms(sources["notification"]["samples"], target_rms, "notification")

    intro_final_rms = p9a.rms(result["intro"])
    outro_matched = sources["outro"]["samples"] * p9a.compute_gain_for_target_rms(
        sources["outro"]["samples"], intro_final_rms)
    outro_v2 = outro_matched * asm.OUTRO_EXTRA_GAIN_LINEAR
    outro_v3 = outro_v2 * asm.OUTRO_FURTHER_EXTRA_GAIN_LINEAR
    result["outro"] = outro_v3
    gain_report["outro"] = {
        "matched_to": "intro_post_gain_rms", "intro_post_gain_rms": round(intro_final_rms, 5),
        "rms_after_match": round(p9a.rms(outro_matched), 5),
        "rms_final": round(p9a.rms(outro_v3), 5), "peak_final": round(p9a.peak(outro_v3), 5),
    }

    result["preview"] = p9a.mono_24k_to_stereo_target(preview_mono)
    gain_report["preview"] = {"gain": 1.0, "note": "無加工(RMSアンカー)"}

    for name, mono in sources["narration"].items():
        gained = gain_to_rms(mono, target_rms, name)
        result[name] = p9a.mono_24k_to_stereo_target(gained)

    key_phrase_stereo, key_phrase_meaning_stereo = {}, {}
    for rank, mono in sources["key_phrase_components"].items():
        gained = gain_to_rms(mono, target_rms, f"key_phrase_en_{rank}")
        key_phrase_stereo[rank] = p9a.mono_24k_to_stereo_target(gained)
    for rank, mono in sources["key_phrase_meanings"].items():
        gained = gain_to_rms(mono, target_rms, f"key_phrase_ja_{rank}")
        key_phrase_meaning_stereo[rank] = p9a.mono_24k_to_stereo_target(gained)
    result["key_phrase_components"] = key_phrase_stereo
    result["key_phrase_meanings"] = key_phrase_meaning_stereo

    b1_stereo = {}
    for name, mono in sources["b1_segments"].items():
        if name == "preview":
            continue
        gained = gain_to_rms(mono, target_rms, f"b1_{name}")
        b1_stereo[name] = p9a.mono_24k_to_stereo_target(gained)
    b1_stereo["preview"] = result["preview"]
    result["b1_segments"] = b1_stereo

    result["kp_items"] = sources["kp_items"]
    result["gain_report"] = gain_report
    return result


def build_family_x_b1_timeline(parts: dict) -> list:
    key_phrase_blocks = asm.build_b1_key_phrase_blocks(parts)
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
        ("Full Story Part 1 (Aoede)", b1["full_story_part1"]),
        ("pause_1.0", p9a.silence_stereo(asm.AOEDE_TO_CHARON_PAUSE_SECONDS)),
        ("Comment 2 (Charon)", b1["comment_2"]),
        ("pause_0.8", p9a.silence_stereo(asm.CHARON_TO_AOEDE_PAUSE_SECONDS)),
        ("Full Story Part 2 (Aoede)", b1["full_story_part2"]),
        ("pause_1.0", p9a.silence_stereo(asm.AOEDE_TO_CHARON_PAUSE_SECONDS)),
        ("Comment 3 (Charon, Bridge to Part 3)", b1["comment_3"]),
        ("pause_0.8", p9a.silence_stereo(asm.CHARON_TO_AOEDE_PAUSE_SECONDS)),
        ("Full Story Part 3 (Aoede)", b1["full_story_part3"]),
        ("pause_1.0", p9a.silence_stereo(asm.AOEDE_TO_CHARON_PAUSE_SECONDS)),
        ("Comment 4 (Charon)", b1["comment_4"]),
        ("pause_0.8", p9a.silence_stereo(asm.CHARON_TO_AOEDE_PAUSE_SECONDS)),
        ("In One Line (Aoede)", b1["in_one_line"]),
        ("pause_0.8_in_one_line_to_outro", p9a.silence_stereo(asm.IN_ONE_LINE_TO_OUTRO_PAUSE_SECONDS)),
        ("Outro (Charon)", parts["outro"]),
    ]
    return seq


def stage_assemble_family_x_b1(theme_out_dir: str, theme_id: str) -> dict:
    out_dir = f"{theme_out_dir}/b1b"
    os.makedirs(f"{out_dir}/assembled", exist_ok=True)
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    sources = load_family_x_b1_sources(theme_out_dir)
    parts = apply_family_x_b1_gain(sources)
    seq = build_family_x_b1_timeline(parts)
    result = asm.assemble_with_timeline(seq)
    headroom = asm.apply_headroom_safety_valve(result["assembled"], seq)
    assembled = headroom["assembled"]

    out_path = f"{out_dir}/assembled/Family_X_Audio_B1_{theme_id.upper()}.wav"
    save_json(f"{out_dir}/audit/gain_report.json", parts["gain_report"])
    save_json(f"{out_dir}/audit/timeline.json", result["timeline"])
    save_json(f"{out_dir}/audit/headroom_report.json", headroom["report"])

    common.write_wav_float(out_path, assembled, SR, 2)
    metrics = common.measure_metrics(assembled[:, 0], SR)
    summary = {
        "status": "OK", "out_path": out_path, "duration_seconds": result["total_duration_seconds"],
        "clipping_detected": metrics["clipping_detected"], "peak": round(p9a.peak(assembled), 5),
        "sample_rate": SR, "channels": 2, "headroom_safety_valve": headroom["report"],
    }
    save_json(f"{out_dir}/run_summary_assemble.json", summary)
    return summary


def load_family_x_a2_sources(theme_out_dir: str) -> dict:
    out_dir = f"{theme_out_dir}/a2"
    narration_dir = f"{out_dir}/narration"
    asm.verify_episode_audio_validation_gate(out_dir, "A2")

    intro = p9a.load_and_resample_to_target(p9a.INTRO_MP3_PATH)
    notification = p9a.load_and_resample_to_target(p9a.NOTIFICATION_MP3_PATH)
    outro = p9a.load_and_resample_to_target(p9a.OUTRO_MP3_PATH)

    preview_mono, preview_sr, _, _ = common.read_wav_float(f"{narration_dir}/preview.wav")
    assert preview_sr == common.SAMPLE_RATE

    narration = {}
    for name in ("welcome", "preview_intro", "key_phrases_intro", "full_story_intro",
                  "num_one", "num_two", "num_three", "num_four", "num_five"):
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/{name}.wav")
        assert sr == common.SAMPLE_RATE
        narration[name] = mono
    for name in ("topic_intro", "japanese_title"):
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/{name}.wav")
        assert sr == common.SAMPLE_RATE
        narration[name] = mono

    kp = load_json(f"{out_dir}/key_phrases/keywords_canonicalized.json")
    kp_items = sorted(kp["items"], key=lambda it: it["rank"])
    key_phrase_components = {}
    for i, item in enumerate(kp_items, start=1):
        rank = item["rank"]
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/kp{rank}_en.wav")
        key_phrase_components[rank] = mono
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/meaning_{i}.wav")
        narration[f"meaning_{i}"] = mono

    a2_segments = {}
    for name in ("comment_1", "comment_2", "comment_3", "comment_4",
                  "full_story_part1", "full_story_part2", "full_story_part3", "in_one_line"):
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/{name}.wav")
        assert sr == common.SAMPLE_RATE
        a2_segments[name] = mono

    return {"intro": intro, "notification": notification, "outro": outro,
            "preview_mono": preview_mono, "narration": narration,
            "key_phrase_components": key_phrase_components, "a2_segments": a2_segments, "kp_items": kp_items}


def apply_family_x_a2_gain(sources: dict) -> dict:
    target_rms = (p9a.rms(sources["preview_mono"]) + p9a.rms(sources["a2_segments"]["full_story_part1"])) / 2
    gain_report = {"target_rms": round(target_rms, 5)}

    def gain_to_rms(data, target, label):
        gain = p9a.compute_gain_for_target_rms(data, target)
        gained = data * gain
        gain_report[label] = {"gain": round(float(gain), 4), "rms_before": round(p9a.rms(data), 5),
                               "rms_after": round(p9a.rms(gained), 5), "peak_after": round(p9a.peak(gained), 5)}
        return gained

    result = {}
    result["intro"] = gain_to_rms(sources["intro"]["samples"], target_rms, "intro")
    result["notification"] = gain_to_rms(sources["notification"]["samples"], target_rms, "notification")

    intro_final_rms = p9a.rms(result["intro"])
    outro_matched = sources["outro"]["samples"] * p9a.compute_gain_for_target_rms(
        sources["outro"]["samples"], intro_final_rms)
    outro_final = outro_matched * asm.OUTRO_EXTRA_GAIN_LINEAR
    result["outro"] = outro_final
    gain_report["outro"] = {
        "matched_to": "intro_post_gain_rms", "intro_post_gain_rms": round(intro_final_rms, 5),
        "rms_after_match": round(p9a.rms(outro_matched), 5),
        "extra_gain_linear": round(float(asm.OUTRO_EXTRA_GAIN_LINEAR), 4),
        "rms_final": round(p9a.rms(outro_final), 5), "peak_final": round(p9a.peak(outro_final), 5),
    }

    result["preview"] = p9a.mono_24k_to_stereo_target(sources["preview_mono"])
    gain_report["preview"] = {"gain": 1.0, "note": "無加工(新規Preview音声を保持)"}

    for name, mono in sources["narration"].items():
        gained = gain_to_rms(mono, target_rms, name)
        result[name] = p9a.mono_24k_to_stereo_target(gained)

    key_phrase_stereo = {}
    for number, mono in sources["key_phrase_components"].items():
        gained = gain_to_rms(mono, target_rms, f"key_phrase_en_{number}")
        key_phrase_stereo[number] = p9a.mono_24k_to_stereo_target(gained)
    result["key_phrase_components"] = key_phrase_stereo

    a2_stereo = {}
    for name, mono in sources["a2_segments"].items():
        gained = gain_to_rms(mono, target_rms, f"a2_{name}")
        a2_stereo[name] = p9a.mono_24k_to_stereo_target(gained)
    result["a2_segments"] = a2_stereo

    result["kp_items"] = sources["kp_items"]
    result["gain_report"] = gain_report
    return result


def build_family_x_a2_timeline(parts: dict) -> list:
    key_phrase_blocks = asm.build_a2_key_phrase_blocks(parts)
    a2 = parts["a2_segments"]

    seq = [
        ("Intro", parts["intro"]),
        ("Welcome", parts["welcome"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
        ("Topic intro", parts["topic_intro"]),
        ("pause_0.65", p9a.silence_stereo(0.65)),
        ("Japanese title", parts["japanese_title"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
        ("Notification 1", parts["notification"]),
        ("pause_0.4", p9a.silence_stereo(0.4)),
        ("Preview intro", parts["preview_intro"]),
        ("pause_0.65", p9a.silence_stereo(0.65)),
        # 注: 既存Family Aの"Point explanation"固定segmentはFamily Xでは
        # 使わない(CURRENT_SPEC Family X節: Point前置きを使わない)。
        ("Preview", parts["preview"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
        ("Notification 2", parts["notification"]),
        ("pause_0.4", p9a.silence_stereo(0.4)),
        ("Key phrases intro", parts["key_phrases_intro"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
    ]
    kp_labels = tuple(f"Key Phrase {i + 1}" for i in range(len(key_phrase_blocks)))
    for label, block in zip(kp_labels, key_phrase_blocks):
        seq.append((label, block))

    seq += [
        ("Notification 3", parts["notification"]),
        ("pause_0.4", p9a.silence_stereo(0.4)),
        ("Full story intro", parts["full_story_intro"]),
        ("pause_1.0_en_to_ja", p9a.silence_stereo(1.0)),
        ("Comment 1", a2["comment_1"]),
        ("pause_0.8_ja_to_en", p9a.silence_stereo(0.8)),
        ("Full Story Part 1", a2["full_story_part1"]),
        ("pause_1.0_en_to_ja", p9a.silence_stereo(1.0)),
        ("Comment 2", a2["comment_2"]),
        ("pause_0.8_ja_to_en", p9a.silence_stereo(0.8)),
        ("Full Story Part 2", a2["full_story_part2"]),
        ("pause_1.0_en_to_ja", p9a.silence_stereo(1.0)),
        ("Comment 3", a2["comment_3"]),
        ("pause_0.8_ja_to_en", p9a.silence_stereo(0.8)),
        ("Full Story Part 3", a2["full_story_part3"]),
        ("pause_1.0_en_to_ja", p9a.silence_stereo(1.0)),
        ("Comment 4", a2["comment_4"]),
        ("pause_0.8_ja_to_en", p9a.silence_stereo(0.8)),
        ("In One Line", a2["in_one_line"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
        ("Outro", parts["outro"]),
    ]
    return seq


def stage_assemble_family_x_a2(theme_out_dir: str, theme_id: str) -> dict:
    out_dir = f"{theme_out_dir}/a2"
    os.makedirs(f"{out_dir}/assembled", exist_ok=True)
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    sources = load_family_x_a2_sources(theme_out_dir)
    parts = apply_family_x_a2_gain(sources)
    seq = build_family_x_a2_timeline(parts)
    result = asm.assemble_with_timeline(seq)
    headroom = asm.apply_headroom_safety_valve(result["assembled"], seq)
    assembled = headroom["assembled"]

    out_path = f"{out_dir}/assembled/Family_X_Audio_A2_{theme_id.upper()}.wav"
    save_json(f"{out_dir}/audit/gain_report.json", parts["gain_report"])
    save_json(f"{out_dir}/audit/timeline.json", result["timeline"])
    save_json(f"{out_dir}/audit/headroom_report.json", headroom["report"])

    common.write_wav_float(out_path, assembled, SR, 2)
    metrics = common.measure_metrics(assembled[:, 0], SR)
    summary = {
        "status": "OK", "out_path": out_path, "duration_seconds": result["total_duration_seconds"],
        "clipping_detected": metrics["clipping_detected"], "peak": round(p9a.peak(assembled), 5),
        "sample_rate": SR, "channels": 2, "headroom_safety_valve": headroom["report"],
    }
    save_json(f"{out_dir}/run_summary_assemble.json", summary)
    return summary


# ============================================================
# コスト計測(er012_e_family_entertainment_two_level_runner_01.pyと同一
# ロジック[PRICING_SNAPSHOT_PATH/USD_JPY]、本runner専用ログへ適用する
#独立実装。既存ファイルは編集しない)。
# ============================================================
PRICING_SNAPSHOT_PATH = "er005_output/cost_baseline_01/pricing_snapshot.json"
USD_JPY = 160.0


def _load_pricing():
    prices = load_json(PRICING_SNAPSHOT_PATH)["prices"]

    def price(provider, model, meter):
        return next(p["price"] for p in prices
                    if p["provider"] == provider and p["model"] == model and p["meter"] == meter
                    and p.get("tier", "Standard") == "Standard")
    return price


def compute_cost_jpy_so_far(cost_log_path: str) -> tuple:
    if not os.path.exists(cost_log_path):
        return 0.0, {}
    price = _load_pricing()
    total_usd = 0.0
    by_provider = {}
    with open(cost_log_path, encoding="utf-8") as f:
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


def assert_budget_ok(out_dir: str, budget_jpy: float, note: str = "") -> float:
    cost_log_path = f"{out_dir}/raw_usage_log.jsonl"
    jpy, by_provider = compute_cost_jpy_so_far(cost_log_path)
    print(f"[FAMILY-X-AUDIO-RUNNER][cost] so far={jpy:.2f} JPY by_provider={by_provider} ({note})")
    if jpy > budget_jpy:
        raise RuntimeError(
            f"[BUDGET_GUARD] cost so far {jpy:.2f} JPY > cap {budget_jpy} JPY. Stopping ({note}).")
    return jpy


# ============================================================
# player.html(既存Family A/Family X標準フォーマット、audio_review_
# player.py[player_common]を再利用。Gate 7 (a)〜(l)必須列を満たす)。
# ============================================================
def _load_assemble_summary(path: str) -> dict:
    if not os.path.exists(path):
        return {"status": "NOT_ATTEMPTED_OR_GATE_BLOCKED_BEFORE_SUMMARY_WRITE"}
    return load_json(path)


def _row_info_family_x(label: str, level: str, parts: dict, support: dict, narration_dir: str,
                        kp_by_rank: dict, japanese_title: str | None) -> dict:
    voice = "Charon" if level == "b1b" else "Aoede"
    if label in ("Intro", "Outro"):
        return {"text": "音楽ジングル/固定音源(読み上げなし)。", "voice": None, "audio": None, "sfx": True}
    if label.startswith("Notification"):
        return {"text": "効果音(読み上げなし)", "voice": None, "audio": None, "sfx": True}
    if label == "Welcome":
        return {"text": "(共有固定Welcome)", "voice": voice, "audio": None, "sfx": False}
    if label.startswith("Topic intro"):
        return {"text": f"Today's topic is {parts['title']}.", "voice": voice,
                "audio": f"{narration_dir}/topic_intro.wav", "sfx": False}
    if label == "Japanese title":
        return {"text": japanese_title or "(未取得)", "voice": voice,
                "audio": f"{narration_dir}/japanese_title.wav", "sfx": False}
    if label.startswith("Preview intro"):
        return {"text": "(共有固定Preview intro)", "voice": voice, "audio": None, "sfx": False}
    if label.startswith("Preview"):
        return {"text": support["preview"], "voice": voice, "audio": f"{narration_dir}/preview.wav", "sfx": False}
    if label.startswith("Key phrases intro"):
        return {"text": "(共有固定Key phrases intro)", "voice": voice, "audio": None, "sfx": False}
    if label.startswith("Key Phrase "):
        rank = int(label.split(" ")[-1])
        kp = kp_by_rank[rank]
        idx = sorted(kp_by_rank).index(rank) + 1
        text = f"EN: {kp['used_form']}<br>JA: {kp['japanese_gloss']}"
        if level == "b1b":
            audio = (f"{narration_dir}/kp{rank}_en.wav", f"{narration_dir}/kp{rank}_ja_charon.wav")
        else:
            audio = (f"{narration_dir}/kp{rank}_en.wav", f"{narration_dir}/meaning_{idx}.wav")
        return {"text": text, "voice": voice, "audio": audio, "sfx": False}
    if label.startswith("Full story intro"):
        return {"text": "(共有固定Full story intro)", "voice": voice, "audio": None, "sfx": False}
    for i in (1, 2, 3, 4):
        if label.startswith(f"Comment {i}"):
            return {"text": support[f"comment_{i}"], "voice": voice,
                    "audio": f"{narration_dir}/comment_{i}.wav", "sfx": False}
    for i in (1, 2, 3):
        if label.startswith(f"Full Story Part {i}"):
            return {"text": parts[f"part{i}"], "voice": voice,
                    "audio": f"{narration_dir}/full_story_part{i}.wav", "sfx": False}
    if label.startswith("In One Line"):
        return {"text": parts["in_one_line"], "voice": voice,
                "audio": f"{narration_dir}/in_one_line.wav", "sfx": False}
    return {"text": "(共有固定segment、記事固有scriptなし)", "voice": None, "audio": None, "sfx": False}


# 既存player_common.SEEK_SCRIPTは単一id("episode_audio")固定のため、
# 1ページにAdvanced/Standard 2レベル分のepisode音声を並べる本player
# (既存player_common利用側の慣例id"episode_audio_b1b"/"episode_audio_a2"、
# docs/pm/tools/translation_reprint_check.py参照)では使えない。button側に
# data-target属性を追加しレベル別に正しいaudio要素へseekする、本runner
# 専用の小さなJSへ差し替える(player_common本体は無編集)。
_TWO_LEVEL_SEEK_SCRIPT = """
function seekTarget(sec, targetId) {
  var id = targetId || 'episode_audio';
  var a = document.getElementById(id);
  if (!a) return;
  a.currentTime = parseFloat(sec);
  a.play();
}
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll("button.seek").forEach(function (btn) {
    btn.addEventListener("click", function () {
      seekTarget(btn.getAttribute("data-sec"), btn.getAttribute("data-target"));
    });
  });
});
""".strip("\n")


def _add_seek_target(table_html: str, target_id: str) -> str:
    return table_html.replace(
        '<button class="seek" data-sec="', f'<button class="seek" data-target="{target_id}" data-sec="')


def _build_level_table(level_dir: str, level: str, japanese_title: str | None = None) -> str:
    assemble_summary = load_json(f"{level_dir}/run_summary_assemble.json")
    if assemble_summary.get("status") != "OK":
        return f"<p style='color:#b00'>Assembly未完了(status={assemble_summary.get('status')})。table省略。</p>"
    timeline = load_json(f"{level_dir}/audit/timeline.json")
    parts = load_json(f"{level_dir}/parts.json")
    narration_dir = f"{level_dir}/narration"
    kp = load_json(f"{level_dir}/key_phrases/keywords_canonicalized.json")
    kp_by_rank = {item["rank"]: item for item in kp["items"]}
    abs_url = player_common.abs_file_url
    support = load_json(f"{level_dir}/{'b1_support_texts.json' if level == 'b1b' else 'a2_support_texts.json'}")

    rows = []
    for entry in timeline:
        label = entry["part"]
        if label.startswith("pause_"):
            continue
        info = _row_info_family_x(label, level, parts, support, narration_dir, kp_by_rank, japanese_title)
        sec = entry["start_seconds"]
        voice_disp = info["voice"] or ("SFX" if info["sfx"] else "—")
        if info["sfx"] or not info["audio"]:
            audio_html = "—"
        elif isinstance(info["audio"], tuple):
            audio_html = player_common.render_single_audio_html(tuple(abs_url(p) for p in info["audio"]))
        else:
            audio_html = player_common.render_single_audio_html(abs_url(info["audio"]))
        rows.append(player_common.render_timeline_row(sec, label, voice_disp, info["text"], audio_html, missing=False))
    return player_common.render_timeline_table(rows)


def build_player_html(theme_out_dir: str, theme_id: str, japanese_title: str | None) -> str:
    abs_url = player_common.abs_file_url
    b1b_summary = _load_assemble_summary(f"{theme_out_dir}/b1b/run_summary_assemble.json")
    a2_summary = _load_assemble_summary(f"{theme_out_dir}/a2/run_summary_assemble.json")

    b1b_audio_html = f'<h2>Advanced(B1)</h2><p style="color:#b00">status={b1b_summary.get("status")}</p>'
    if b1b_summary.get("status") == "OK":
        b1b_table = _add_seek_target(_build_level_table(f"{theme_out_dir}/b1b", "b1b"), "episode_audio_b1b")
        b1b_audio_html = (f'<h2>Advanced(B1)</h2>'
                           f'<audio id="episode_audio_b1b" class="main" controls preload="none" '
                           f'src="{abs_url(b1b_summary["out_path"])}"></audio>'
                           f'<p class="note">duration={b1b_summary["duration_seconds"]}s '
                           f'peak={b1b_summary["peak"]} clipping={b1b_summary["clipping_detected"]}</p>'
                           f'{b1b_table}')

    a2_audio_html = f'<h2>Standard(A2)</h2><p style="color:#b00">status={a2_summary.get("status")}</p>'
    if a2_summary.get("status") == "OK":
        a2_table = _add_seek_target(
            _build_level_table(f"{theme_out_dir}/a2", "a2", japanese_title), "episode_audio_a2")
        a2_audio_html = (f'<h2>Standard(A2)</h2>'
                          f'<audio id="episode_audio_a2" class="main" controls preload="none" '
                          f'src="{abs_url(a2_summary["out_path"])}"></audio>'
                          f'<p class="note">duration={a2_summary["duration_seconds"]}s '
                          f'peak={a2_summary["peak"]} clipping={a2_summary["clipping_detected"]}</p>'
                          f'{a2_table}')

    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>{MANAGEMENT_ID} player({theme_id})</title>
<style>
{player_common.PLAYER_STANDARD_CSS}
</style>
<script>
{_TWO_LEVEL_SEEK_SCRIPT}
</script>
</head><body>
<h1>{MANAGEMENT_ID}({theme_id})</h1>
<p class="note">Family X(Entertainment News)音声構造Stage 3a runtime。
Comment1→本文1→Comment2→本文2→Comment3→本文3→Comment4→In One Line(Point構造なし)。</p>
{b1b_audio_html}
{a2_audio_html}
</body></html>
"""
    out_path = f"{theme_out_dir}/player.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    return out_path


# ============================================================
# CLI
# ============================================================
def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", required=True,
                         help="入力article.mdのある er019_output配下ディレクトリ名"
                              "(例: family_x_b3_production_wiring_01)。")
    parser.add_argument("--run", required=True, help="例: run_01")
    parser.add_argument("--level", default="both", choices=("a2", "b1b", "both"))
    parser.add_argument("--stage", default="plan",
                         choices=("plan", "scaffold", "tts", "assemble", "player", "all"))
    parser.add_argument("--dry-run", action="store_true",
                         help="API呼び出しを一切行わずplanのみ出力する(--stage plan相当を強制)。")
    parser.add_argument("--out-dir", default=None,
                         help="既定: er019_output/family_x_audio_production_wiring_01/<slug>__<run>")
    parser.add_argument("--budget-jpy", type=float, default=150.0,
                         help="scaffold/tts stage後のBudget Guard上限(既定150円、超過でRuntimeError)。")
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    source_dir = f"er019_output/{args.slug}/{args.run}"
    out_dir = derive_out_dir(args.slug, args.run, args.out_dir)
    os.makedirs(out_dir, exist_ok=True)

    levels = ["a2", "b1b"] if args.level == "both" else [args.level]

    ja_title_info = derive_japanese_title(source_dir)
    japanese_title = ja_title_info["japanese_title"]
    if "a2" in levels and not japanese_title:
        print(f"[FAMILY-X-AUDIO-RUNNER][WARN] japanese_titleが取得できませんでした"
              f"(source_dir={source_dir}/ja_writer 不在)。A2のJapanese title segmentは"
              f"英語placeholderのまま生成されるため、実行前に要確認。")

    save_json(f"{out_dir}/entry_point.json", {
        "runner": "er019_family_x_audio_production_runner_01.py",
        "management_id": MANAGEMENT_ID, "slug": args.slug, "run": args.run,
        "source_dir": source_dir, "levels": levels, "stage": args.stage, "dry_run": args.dry_run,
        "japanese_title": japanese_title, "japanese_title_source": ja_title_info["source"],
        "budget_jpy": args.budget_jpy,
    })

    if args.dry_run or args.stage == "plan":
        result = run_plan_stage(source_dir, out_dir, levels)
        save_json(f"{out_dir}/plan_run_result.json", result)
        print(f"[FAMILY-X-AUDIO-RUNNER] plan完了(API呼び出しゼロ円)。out_dir={out_dir}")
        for level, r in result.items():
            print(f"  {level}: status={r.get('status')}")
        return

    # scaffold/tts/assemble stageは実API呼び出しを伴う(Stage 1では
    # 呼び出さない。Stage 2以降で本CLIから--stage scaffold等を実行する)。
    # cost loggerのinstall/raw_usage_log.jsonl作成もこの分岐以降のみ行う
    # (--dry-run/--stage planは常に¥0・副作用ゼロを維持する既存契約を保つ)。
    cl.install(f"{out_dir}/raw_usage_log.jsonl")
    import er003_v1_en_direct_vfl_01_generate as vfl01
    client = vfl01.get_client()

    if args.stage in ("scaffold", "all"):
        with cl.logging_context(args.slug, "scaffold"):
            run_theme_scaffold(client, source_dir, out_dir, levels)
        assert_budget_ok(out_dir, args.budget_jpy, "after scaffold")

    if args.stage in ("tts", "all"):
        with cl.logging_context(args.slug, "tts"):
            for level in levels:
                if level == "b1b":
                    generate_family_x_b1_segments(out_dir)
                else:
                    # 日本語titleは実行時に決定したja_title_info(ja_writer正式path
                    # 由来)を使う(以前はa2/article.mdの英語titleをそのまま渡す
                    # placeholderだった、Stage 3aで判明したbugの最小修正)。
                    generate_family_x_a2_segments(
                        out_dir, japanese_title=japanese_title or "(japanese title unavailable)")
        assert_budget_ok(out_dir, args.budget_jpy, "after tts")

    if args.stage in ("assemble", "all"):
        for level in levels:
            if level == "b1b":
                stage_assemble_family_x_b1(out_dir, args.slug)
            else:
                stage_assemble_family_x_a2(out_dir, args.slug)

    if args.stage in ("player", "all"):
        player_path = build_player_html(out_dir, args.slug, japanese_title)
        print(f"[FAMILY-X-AUDIO-RUNNER] player.html: {os.path.abspath(player_path)}")

    final_jpy, by_provider = compute_cost_jpy_so_far(f"{out_dir}/raw_usage_log.jsonl")
    print(f"[FAMILY-X-AUDIO-RUNNER] stage={args.stage} 完了。out_dir={out_dir} "
          f"累計費用(JPY)={final_jpy:.2f} by_provider={by_provider}")


if __name__ == "__main__":
    main()
