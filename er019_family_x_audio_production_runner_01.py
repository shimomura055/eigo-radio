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
import sys
import hashlib
import json
import os

import audio_review_player as player_common
import er078_secondary_run_scope_01 as secondary_run_scope  # AUW 委任_05
import er003_v1_b1_scaffold_01_generate as b1s
import er003_v1_crosslevel_audio_02_common as crosslevel_common
import er003_v1_iran01_a2_generate as a2gen
import er019_family_x_std_comment3_z_method_01 as c3z  # FX-STD-COMMENT3-Z-METHOD-PRODUCTION-01: X Std Comment 3 Z方式(2026-10-28ユーザー正式決定)
import er003_v1_n3_01_assemble as asm
import er003_v1_n3_01_scaffold_generate as sc
import er003_v1_n3_01_tts_generate as n3_tts
import er003_v1_sing01_news_tail_fix as news_tail_fix
import er003_v1_sing01_point_headings_aoede as point_headings
import er003_v1_sing01_voice01_generate as voice01
import er005_cost_logger as cl
import er011_human_review_lock_01 as review_lock
import er078_pass_with_warning_registry_01 as pww_registry  # AUW 委任_03: PASS_WITH_WARNING 事後試聴リスト
import er103_pnap_runner_hooks_01 as pnap_hooks  # PNAP 委任_02: 固有名詞アラーム方針のrun scope+完成報告hook(flag OFFなら素通し)
import er103_pronunciation_tts_supply_01 as pnap_supply  # PNAP 委任_02: 固有名詞の発音供給(flag OFF/scope外は恒等)
import er109_xz_scope_01 as er109_scope  # ASR-HOMOPHONE 委任_04: er109(表記違い同音)のrun scope(X)。TTS段の入口decoratorだけで使う(リテラル"X"のみ)
import er006_audio_cost_pilot_02_shared_narration as shared_narration
import er006_model_routing_contract_01 as routing
import er019_family_x_audio_plan_01 as plan
import er019_family_x_kp_explanation_01 as kp_explanation_gen
import er019_family_x_kp_en_k2_store_01 as kp_en_k2_store  # 委任_02A: KP英語K2の2段key(Family X専用module)
import er104_kp_vote_reuse_01 as kp_vote  # KP3V(2026-10-22、ユーザー承認APPROVED_FOR_PRODUCTION): KP英語phrase 3-ASR多数決(OpenAI・Azure・Whisper)
import er081_family_x_in_one_line_01 as fx_iol  # FXPW 委任_04: In One Line scope(Family X専用)
import er019_family_x_style_profile_01 as style_profile_mod
import er019_family_x_validation_inheritance_01 as validation_inheritance
import er020_tts_retry_local_rewrite_01 as retry_primitive
import er127_tts_block_policy_01 as er127  # TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_02: X/Y/Z scope内の統一3回構成ブロック
import er117_chunk_tts_production_01 as chunk_tts  # FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01(X Adv本文=段落単位chunk+0.2秒、APPROVED_FOR_PRODUCTION 2026-10-25)
import er053_review_queue_01 as rq
import er053_risk_flagger_production_01 as rf
import er116_fx_core_numeric_retention_01 as numret  # FX-CORE-NUMERIC-RETENTION 委任_07: J2(A2 support本文の範囲値正規化)のみ使用

MANAGEMENT_ID = "NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01"

# 承認済みの正式TTS backend(Family X、flash-lite統一)。`--tts-backend`の既定値・tts stageのfail-fast Gateが参照する。
FAMILY_X_APPROVED_PRODUCTION_TTS_BACKEND = "speech_metadata_flash_lite"

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
# I4(Opus条件A): chunk TTSのsegment_id(full_story_part{n}_k{j})もFULL_STORYへ解決されること(入れ忘れの即時検出)。
for _seg_id in ("full_story_part1_k1", "full_story_part2_k2", "full_story_part3_k10"):
    if retry_primitive.resolve_narrative_role(_seg_id) != "FULL_STORY":
        raise RuntimeError(
            f"[{MANAGEMENT_ID}] STOP: chunk TTS segment_id={_seg_id!r} が resolve_narrative_role() で FULL_STORY へ解決されません"
            "(er020のchunk ID正規表現が外れています。FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01 C4)")


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
    # FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W1): Heading Readout撤去後の
    # 新構造(v2 segment順序、見出しsub-segmentなし)。旧FAMILY_X_B1_
    # SEGMENT_ORDER/FAMILY_X_A2_SEGMENT_ORDER(heading込み)は無変更のまま
    # 残す(本関数からは呼ばない)。
    order = plan.FAMILY_X_B1_SEGMENT_ORDER_V2 if level == "b1b" else plan.FAMILY_X_A2_SEGMENT_ORDER_V2
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
                if level == "b1b" or plan_role in ("FULL_STORY", "TOPIC_INTRO", "HEADING_READOUT"):
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
        r.get("estimated_seconds", 0.0) for r in rows if r.get("plan_role") in ("FULL_STORY", "HEADING_READOUT"))
    return {
        "level": level,
        "segments": rows,
        "body_word_counts": parts.get("word_counts"),
        "estimated_body_seconds_total": round(body_seconds, 1),
        "no_point_structure": True,
        "no_new_sfx_after_body_start": True,
    }


def run_plan_stage(source_dir: str, out_dir: str, levels: list[str], style_profile: str = "default") -> dict:
    result = {}
    for level in levels:
        article_path = f"{source_dir}/{level}/article.md"
        if not os.path.exists(article_path):
            result[level] = {"status": "SOURCE_ARTICLE_NOT_FOUND", "article_path": article_path}
            continue
        article_text = load_text(article_path)
        try:
            parts = plan.split_family_x_article_text_v2(article_text)
        except RuntimeError as e:
            result[level] = {"status": "SPLIT_FAILED", "error": str(e), "article_path": article_path}
            continue
        if parts.get("status") != "OK":
            result[level] = {"status": "SPLIT_FAILED",
                              "error": f"paragraph_count={parts.get('paragraph_count')}<3(TOO_FEW_PARAGRAPHS)",
                              "article_path": article_path}
            continue

        support_path = f"{out_dir}/{level}/b1_support_texts.json" if level == "b1b" \
            else f"{out_dir}/{level}/a2_support_texts.json"
        support = load_json(support_path) if os.path.exists(support_path) else None

        save_json(f"{out_dir}/{level}/parts.json", parts)
        segment_plan = build_segment_plan(level, parts, support)
        save_json(f"{out_dir}/{level}/segment_plan.json", segment_plan)
        result[level] = {"status": "OK", "article_path": article_path,
                          "article_sha256": sha256_text(article_text), "segment_plan": segment_plan}
        if style_profile != style_profile_mod.PROFILE_DEFAULT:
            # OPEN-300 S2: 非defaultのときだけ、Full StoryのStyle(適用中profileの値。旧候補P8/N01/PD06)と現行Pronunciation Ledger hit
            # (hint追記有無)をplan段階で記録する(読み取りのみ、web lookup無効、課金0)。
            # defaultではkeyを追加しない(バイト同一)。
            import er025_entity_pronunciation_resolver_core_01 as pron_core
            # FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01: Full Story styleは適用中profileの値(旧候補P8/N01/PD06)で記録・判定する。`P8_TEXT`フォールバックは「Full Story旧候補P8」で、KP日本語意味のP8-KP[P8_KP_JA_TEXT]とは別物。
            _fs = style_profile_mod.get_profile(style_profile)["overrides"].get("FULL_STORY")
            _fs_text = _fs["text"] if _fs else style_profile_mod.P8_TEXT
            _fs_sha = _fs["sha256"] if _fs else style_profile_mod.P8_SHA256
            with pron_core.disable_web_lookup_for_test():
                hits = style_profile_mod.compute_ledger_hits(parts, tts_safe_fn=n3_tts.tts_safe_news_en,
                                                             full_story_text=_fs_text)
            result[level]["style_profile_plan"] = {
                "profile_id": style_profile,
                "overridden_roles": style_profile_mod.overridden_roles(style_profile),
                "full_story_style_sha256": _fs_sha,
                "full_story_style_length": len(_fs_text),
                "ledger_hits_web_lookup_disabled": hits,
                "roles_sha256": {r: o["sha256"] for r, o in style_profile_mod.get_profile(style_profile)["overrides"].items()},
            }
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
    article_text = plan.reconstruct_family_x_article_text_v2(parts)
    preview_context = f"【エピソード全文(参考、新しいFactの追加禁止)】\n{article_text}"
    preview = b1s.run_support_text(client, preview_prompt_role, preview_context, model=_b1_support_model())

    results = {"preview": preview, "comment_1": c1, "comment_2": c2, "comment_3": c3, "comment_4": c4}
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    save_json(f"{out_dir}/b1_support_texts.json", {k: v.get("text") for k, v in results.items()})
    save_json(f"{out_dir}/audit/b1_support_generation.json", results)
    return results


def _a2_run_support_text_j2(client, role, context, *, model):
    """A2(日本語)support本文(Preview/Comment1-4)生成の直後にJ2(範囲値『数字〜数字』→『数字から数字』、数字・桁は不変)を適用する。
    FX-CORE-NUMERIC-RETENTION-TRIAL-01 委任_07(ユーザー正式採用J2=USER_05の同一目的の適用点)。Writer段で『から』に統一済みの範囲値を
    support生成LLMが波ダッシュへ書き戻し、TTS用Normalizerが『なになに』と読んでASR NG→STOPした実測(月run_ms_03 comment_2)の是正。"""
    r = a2gen.run_support_text(client, role, context, model=model)
    if isinstance(r, dict) and isinstance(r.get("text"), str):
        new = numret.normalize_ranges(r["text"])
        if new != r["text"]:
            r["j2_raw_text_sha256"] = hashlib.sha256(r["text"].encode("utf-8")).hexdigest()
            r["j2_range_normalized"] = True
            r["text"] = new
    return r


def _a2_comment3_z(client, parts: dict) -> dict:
    """Opus M-3: X Std Comment 3 Z方式の唯一のhelper。初回生成(run_family_x_a2_scaffold)と`--regenerate-support comment_3`が共通で呼ぶ。
    J2(`_a2_run_support_text_j2`)とsupport model(`_a2_support_model()`)を束縛して`c3z.run_comment3_z_method`へ渡す。"""
    return c3z.run_comment3_z_method(
        lambda role, ctx: _a2_run_support_text_j2(client, role, ctx, model=_a2_support_model()), parts)


def run_family_x_a2_scaffold(client, parts: dict, out_dir: str) -> dict:
    """A2(Japanese)Preview/Comment1-4を生成する(単一Voice、a2genの
    Comment1/2/PreviewをそのままJapanese出力で流用)。"""
    print(f"[FAMILY-X-AUDIO-SCAFFOLD] A2 Comment 1生成開始({out_dir})...")
    c1_context = f"【これから聞く本文(本文1、英語)】\n{parts['part1']}"
    c1 = _a2_run_support_text_j2(client, a2gen.COMMENT_1_ROLE, c1_context, model=_a2_support_model())

    print(f"[FAMILY-X-AUDIO-SCAFFOLD] A2 Comment 2生成開始({out_dir})...")
    c2_context = f"【すでに聞いた本文(本文1)】\n{parts['part1']}\n\n【これから聞く本文(本文2)】\n{parts['part2']}"
    c2 = _a2_run_support_text_j2(client, a2gen.COMMENT_2_ROLE, c2_context, model=_a2_support_model())

    print(f"[FAMILY-X-AUDIO-SCAFFOLD] A2 Comment 3生成開始(Z方式 {c3z.COMMENT3_Z_METHOD_VERSION}、{out_dir})...")
    c3 = _a2_comment3_z(client, parts)
    c3.setdefault("comment3_z_audit", {})["c2_c3_overlap_note"] = c3z.compute_c2_c3_overlap_notes(c2.get("text"), c3.get("text"))   # R-5: 非blocking
    if c3.get("status") != "OK" or not isinstance(c3.get("text"), str):
        # Opus M-2: C3が非OKなら下流(C4/Preview=有料LLM)を呼ばず、null入りa2_support_texts.jsonも書かない(却下文・監査はaudit/側のみ)。
        # 停止の実体(marker・rc=3・KP/Part 1/2を実行しない)はrun_theme_scaffold/main()側。
        partial = {"comment_1": c1, "comment_2": c2, "comment_3": c3}
        os.makedirs(f"{out_dir}/audit", exist_ok=True)
        save_json(f"{out_dir}/audit/a2_support_generation.json", partial)
        print(f"[FAMILY-X-AUDIO-SCAFFOLD][STOP] A2 Comment 3が{c3.get('status')}のためComment 4/Previewを生成せず停止します(a2_support_texts.jsonは書きません)。")
        return partial

    print(f"[FAMILY-X-AUDIO-SCAFFOLD] A2 Comment 4生成開始({out_dir})...")
    c4_context = f"【本文1】\n{parts['part1']}\n\n【本文2】\n{parts['part2']}\n\n【本文3】\n{parts['part3']}"
    c4 = _a2_run_support_text_j2(client, plan.FAMILY_X_A2_COMMENT_4_ROLE, c4_context, model=_a2_support_model())

    print(f"[FAMILY-X-AUDIO-SCAFFOLD] A2 Preview生成開始({out_dir})...")
    preview_prompt_role = a2gen.PREVIEW_ROLE.format(
        comment_1=c1.get("text") or "(生成失敗)", comment_2=c2.get("text") or "(生成失敗)")
    article_text = plan.reconstruct_family_x_article_text_v2(parts)
    preview_context = f"【エピソード全文(参考、新しいFactの追加禁止)】\n{article_text}"
    preview = _a2_run_support_text_j2(client, preview_prompt_role, preview_context, model=_a2_support_model())

    results = {"preview": preview, "comment_1": c1, "comment_2": c2, "comment_3": c3, "comment_4": c4}
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    save_json(f"{out_dir}/a2_support_texts.json", {k: v.get("text") for k, v in results.items()})
    save_json(f"{out_dir}/audit/a2_support_generation.json", results)
    return results


SUPPORT_STAGE_FAILED_MARKER = "support_stage_failed.json"


def _sha_text(t: str) -> str:
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def run_regenerate_support_comment3(client, source_dir: str, out_dir: str, *, level: str = "a2", budget_check=None) -> dict:
    """Opus M-3: 既存a2_support_texts.jsonのcomment_3だけをZ方式で再生成する正式経路(`--regenerate-support comment_3`)。
    初回生成と同一helper`_a2_comment3_z`を使う。comment_3以外の4キーのshaが書込み前後で一致することをassertし、KP・Part 2・study_textには触れない。
    audit/a2_support_generation.jsonは上書きせず、元のC1/C2/C4/Previewのaudit記録を保持したままcomment_3だけ差し替え(旧comment_3はcomment_3_history)。
    入力partsは公開本文に合わせる(Opus R-6): source記事から分割したpartsへ、LR台帳のoverlay(er132)を適用したもの。
    非OK時はa2_support_texts.jsonを書かず、markerを置く。"""
    level_out_dir = f"{out_dir}/{level}"
    sp = _support_texts_path(level, level_out_dir)
    if not os.path.exists(sp):
        raise RuntimeError(f"[STOP][regenerate-support] {sp}がありません。再生成の前提となる既存supportがありません。")
    with open(sp, encoding="utf-8") as f:
        prior = json.load(f)
    article_text = load_text(f"{source_dir}/{level}/article.md")
    base_parts = plan.split_family_x_article_text_v2(article_text)
    if base_parts.get("status") != "OK":
        raise RuntimeError(f"[STOP][regenerate-support] {source_dir}/{level}/article.mdを3分割できません")
    import er132_lr_overlay_pages_01 as _e132
    pub_parts, _ = _e132.overlay_level_dir_units(level_out_dir, base_parts)
    keys3 = ("part1", "part2", "part3")
    parts_in = {k: pub_parts[k] for k in keys3}
    print(f"[FAMILY-X-AUDIO-SCAFFOLD] A2 Comment 3だけをZ方式で再生成します({level_out_dir})...")
    c3 = _a2_comment3_z(client, parts_in)
    ev = c3.setdefault("comment3_z_audit", {})
    ev["regenerated_by"] = "--regenerate-support comment_3"
    ev["input_parts_source"] = {"article_md": f"{source_dir}/{level}/article.md",
                                "lr_overlay_applied": any(base_parts[k] != parts_in[k] for k in keys3),
                                "base_parts_sha256": {k: _sha_text(base_parts[k]) for k in keys3},
                                "input_parts_sha256": {k: _sha_text(parts_in[k]) for k in keys3}}
    ev["c2_c3_overlap_note"] = c3z.compute_c2_c3_overlap_notes(prior.get("comment_2"), c3.get("text"))
    audit_path = f"{level_out_dir}/audit/a2_support_generation.json"
    os.makedirs(f"{level_out_dir}/audit", exist_ok=True)
    audit_old = {}
    if os.path.exists(audit_path):
        with open(audit_path, encoding="utf-8") as f:
            audit_old = json.load(f)
    marker = f"{level_out_dir}/{SUPPORT_STAGE_FAILED_MARKER}"
    try:
        new_texts = c3z.merge_regenerated_comment3(prior, c3)
    except ValueError as exc:
        # 非OK: texts不変。却下文・監査は別ファイルへ(元auditも不変)。
        save_json(f"{level_out_dir}/audit/a2_comment3_regeneration_failed.json", c3)
        save_json(marker, {"status": f"SUPPORT_STAGE_FAILED({c3.get('status')})", "level": level, "reason": str(exc),
                           "next_command": "--stage scaffold --level a2 --regenerate-support comment_3 を再実行"})
        return {"status": c3.get("status") or "FAILED", "reason": str(exc)}
    # 書込み前に旧版を退避(一度だけ)。
    bak_t = f"{level_out_dir}/a2_support_texts.before_c3_regen.json"
    if not os.path.exists(bak_t):
        save_json(bak_t, prior)
    bak_a = f"{level_out_dir}/audit/a2_support_generation.before_c3_regen.json"
    if audit_old and not os.path.exists(bak_a):
        save_json(bak_a, audit_old)
    audit_new = dict(audit_old)
    hist = list(audit_new.get("comment_3_history") or [])
    if audit_old.get("comment_3"):
        hist.append(audit_old["comment_3"])
    audit_new["comment_3_history"] = hist
    audit_new["comment_3"] = c3
    save_json(sp, new_texts)
    save_json(audit_path, audit_new)
    if os.path.exists(marker):
        os.remove(marker)
    for k in ("preview", "comment_1", "comment_2", "comment_4"):   # 書込み後に再確認
        assert _sha_text(new_texts[k]) == _sha_text(prior[k])
    if budget_check is not None:
        budget_check("after regenerate-support comment_3")
    return {"status": "OK", "comment_3": c3["text"], "other_keys_sha_unchanged": True}


def _comment3_method_of(level_out_dir: str, *, fresh: bool):
    """summary用: 今回生成したsupportはZ方式version。再利用(resume/--scaffold-only kp)は保存済みaudit/a2_support_generation.jsonの
    comment_3.comment3_z_audit.method_versionを読む。無ければNone+WARN(旧仕様のsupport。hard STOPにしない=Opus R-3)。"""
    if fresh:
        return c3z.COMMENT3_Z_METHOD_VERSION
    try:
        with open(f"{level_out_dir}/audit/a2_support_generation.json", encoding="utf-8") as f:
            v = ((json.load(f).get("comment_3") or {}).get("comment3_z_audit") or {}).get("method_version")
    except (OSError, ValueError):
        v = None
    if v is None:
        print(f"[FAMILY-X-AUDIO-SCAFFOLD][WARN] {level_out_dir}: 再利用するsupportのComment 3は旧仕様(comment3_z_audit.method_versionなし)です。"
              "必要なら `--stage scaffold --level a2 --regenerate-support comment_3` でComment 3だけZ方式へ作り直せます。")
    return v


def _support_texts_path(level: str, level_out_dir: str) -> str:
    return f"{level_out_dir}/b1_support_texts.json" if level == "b1b" else f"{level_out_dir}/a2_support_texts.json"


# FAMILY-X-KP-STAGE-FAIL-CLOSED-FIX-01(KPMP-03 委任_03、2026-10-22): KP stageのfail-closed判定。
# Family Z `er026_family_z_fiction_production_runner_01.stage_kp`(:1486-1494付近)の停止条件と同一リテラル
# (相互参照: Z側を変更する場合はここも揃えること)。Redundancy QA NG確定(NG_REVIEW_REQUIRED)・外側retry尽き・
# canonicalization無し/PASS系以外のKPは、旧attemptの`keywords_canonicalized.json`がdiskに残っていても後段(TTS/assembly)が
# 使わないよう、stageを止める。gloss HR(別key`gloss_alignment_run_status`)は従来どおりHR経路で扱い、ここでは止めない。
KP_STAGE_BLOCKING_RUN_STATUSES = ("NG_REVIEW_REQUIRED", "OUTER_RETRY_EXHAUSTED")   # KPFT 委任_02: 旧db_hybridの記事cap停止statusは撤去
# KP-CANON-REVIEW-REQUIRED-FIX-01(OPEN-504、2026-10-25): 承認済み3状態モデルどおり採用はPASSのみ。REVIEW_REQUIREDは共有外側retryが
# 再選定し、上限到達後はOUTER_RETRY_EXHAUSTEDで止まる(ここは多層防御: 外側retryを経ない保存結果の再利用でも自動採用しない)。
KP_STAGE_PASS_CANON_STATUSES = ("CANONICALIZATION_PASS",)
KP_STAGE_FAILED_MARKER = "kp_stage_failed.json"


def kp_stage_failure_status(kp: dict):
    """PASS系ならNone、停止すべきなら`KP_STAGE_FAILED(<kp_status>)`を返す。"""
    canon = kp.get("canonicalization")
    canon_status = (canon or {}).get("status")
    run_status = kp.get("status")
    if run_status in KP_STAGE_BLOCKING_RUN_STATUSES or not canon or canon_status not in KP_STAGE_PASS_CANON_STATUSES:
        kp_status = run_status if run_status in KP_STAGE_BLOCKING_RUN_STATUSES else (
            canon_status if canon else (kp.get("selection") or {}).get("status"))
        return f"KP_STAGE_FAILED({kp_status})"
    return None


def _kp_stage_failed_markers(out_dir: str, levels: list[str]) -> list[str]:
    return [f"{out_dir}/{lv}/key_phrases/{KP_STAGE_FAILED_MARKER}" for lv in levels
            if os.path.exists(f"{out_dir}/{lv}/key_phrases/{KP_STAGE_FAILED_MARKER}")]


def _kp_already_generated(kp_dir: str) -> list[str]:
    """`--scaffold-only kp`のQ5(iv): KP再生成は1レベル1回まで。既にKP成果物がある場合はその一覧を返す。
    KP Human Review(2026-10-25): review/候補ファイルがある場合は『review再開』経路として許可する(候補の再生成はせず、確定のみ。
    選び直しは`er119_kp_human_review_cli_01 reselect`だけ)ので、生成済みとは数えない。"""
    if _khr().has_review(kp_dir):
        return []
    found = []
    for name in ("keywords_runtime_metadata.json", "keywords_canonicalized.json", "key_phrases_db_hybrid"):
        if os.path.exists(f"{kp_dir}/{name}"):
            found.append(f"{kp_dir}/{name}")
    # KPFT 委任_02: 全文選定の外側retryが最終失敗時に退避した旧attemptの成果物(keywords_canonicalized.STALE_attempt*.json)も
    # 『生成済み』として数える(KP再生成は1レベル1回。本名のファイルが無くても引き直さない)。
    import glob as _glob
    found += sorted(_glob.glob(f"{kp_dir}/keywords_canonicalized.STALE_attempt*.json"))
    return found


# ------------------------------------------------------------
# 学習テキスト Part 1「Vocabulary & Expressions」(FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_14、案α、Advanced=b1b)
# SLOT-23 委任_04C(ユーザー正式決定2026-10-27、Std②=C案・遡及なし): Part 1は`level`引数化。対象level=Advanced(b1b)は常に、Standard(a2)は
# 確定レコードに`display_spec`(マーク付き)があるrunだけ(`part1_levels`)。マーク無しの旧a2 run=従来どおりPart 1なし(バイト同一)。
# 設計: docs/research/FAMILY-Z-STUDY-TEXT-TRIAL-01/PART1_WIRING_DESIGN_01.md §13〜§17 + docs/research/SLOT-23-CONSUMER-DESIGN-01/DESIGN_03.md §A。共通module=er003_kp_general_explanation_01。
# 生成点=run_theme_scaffoldの当該level KP PASS後(+`--stage study_text`で単独再実行)。Opus M1: 失敗はKP失敗と分離した専用marker
# (kp_part1_failed.json)+rc=3、案内は`--stage study_text`(scaffold再実行=support/KP再生成を案内しない)。
# Opus M2: tts/assemble/player入口で存在と最新性(signature)をfail-closed確認。
# 訳欄(T1/T2)の判断記録が無い間は、生成・保存のみでplayer.htmlへも描画しない(M3 (ii))。
# ------------------------------------------------------------
KP_PART1_FAILED_MARKER = "kp_part1_failed.json"
PART1_ALWAYS_LEVEL = "b1b"   # Part 1が常に対象のlevel(Advanced)。Standardはdisplay_spec付き(マーク付き)runだけ(DESIGN_03 §A、遡及なし)


def _part1_gen():
    import er003_kp_general_explanation_01 as p1
    return p1


def _er128():
    """確定内容保護の共通核(er128)。runnerからer128を直接importしない既存方針(Zの`_khr()._cc()`と同じ入口=er119._cc。er128_*のisolation test対象)。"""
    return _khr()._cc()


def _g3():
    """本文ハイライトのG3検査module(er128_kp_highlight_01)。文頭/関数内の`import er128_*`を避ける遅延accessor(er128系のisolation testの方針に合わせる。検査自体は弱めない)。"""
    import importlib
    return importlib.import_module("er128_kp_highlight_01")


def x_display_spec(out_dir: str, level: str):
    """表示有効化判断(SLOT-23、flag非経由=er128.display_spec_of)。確定レコードに`display_spec`があればその値、無ければNone(=旧run・従来描画)。"""
    return _er128().display_spec_of(out_dir, level)


def part1_enabled(out_dir: str, level: str) -> bool:
    """このlevelがPart 1(vocab)の対象か。Advanced(b1b)=常に / Standard(a2)=display_spec付き(マーク付き)runだけ(遡及なし)。"""
    return level == PART1_ALWAYS_LEVEL or bool(x_display_spec(out_dir, level))


def part1_levels(out_dir: str, levels: list) -> list:
    return [lv for lv in levels if part1_enabled(out_dir, lv)]


def _part1_explanations_path(out_dir: str, level: str = "b1b") -> str:
    return f"{out_dir}/{level}/key_phrases/{_part1_gen().EXPLANATIONS_FILENAME}"


def _part1_failed_markers(out_dir: str, levels: list) -> list:
    return [f"{out_dir}/{lv}/key_phrases/{KP_PART1_FAILED_MARKER}" for lv in levels
            if os.path.exists(f"{out_dir}/{lv}/key_phrases/{KP_PART1_FAILED_MARKER}")]


def part1_next_command(source_dir: str, level: str = "b1b") -> str:
    parts = os.path.normpath(source_dir).replace("\\", "/").split("/")
    slug, run = (parts[-2], parts[-1]) if len(parts) >= 2 else ("<slug>", "<run>")
    return (f"`--slug {slug} --run {run} --level {level} --stage study_text`(Part 1だけ再生成。support生成・KP選定をやり直す"
            "scaffold再実行は費用と別KPを生むため行わない)")


def _khr():
    import er119_kp_human_review_01 as khr
    return khr


def _kpw():
    import er119_kp_wiring_01 as kpw
    return kpw


def _slug_of(source_dir: str) -> str:
    parts = os.path.normpath(source_dir).replace("\\", "/").split("/")
    return parts[-2] if len(parts) >= 2 else "unknown"


def _part1_kp_items(out_dir: str, level: str = "b1b") -> list:
    """Part 1(単語解説)の入力の単一アクセサ(KP Human Review M-9)。KP Human Reviewのreviewがあるrunはvocab_confirmed.json
    (最大5件、KP3件を含む)が必須(fail-closed)、reviewが無い旧runだけ従来のkeywords_canonicalized.json(3件)。
    未確定/不整合はKpReviewNotConfirmed/KpReviewInconsistent(いずれもRuntimeError)で止める。"""
    khr = _khr()
    kp_dir = f"{out_dir}/{level}/key_phrases"
    khr.require_final_consistent(kp_dir, level=level)
    return khr.part1_items(kp_dir)


def _part1_ja_gen():
    import er003_kp_source_sentence_ja_01 as ja
    return ja


def _part1_ja_path(out_dir: str, level: str = "b1b") -> str:
    return f"{out_dir}/{level}/key_phrases/{_part1_ja_gen().TRANSLATIONS_FILENAME}"


def generate_part1_ja(client, source_dir: str, out_dir: str, *, level: str = "b1b", call_fn=None, budget_check=None) -> dict:
    """委任_16 T1: 本文引用英文だけを入力に日本語訳を1 callで生成・保存する(解説とは独立。signature一致ならAPI 0で再利用、
    不一致なら自動再生成)。失敗(技術retry1回後も構造NG・入力不正・本文に逐語実在しない引用・model不一致)は
    kp_part1_failed.jsonへ status=KP_PART1_JA_FAILED(...) を書き返す。解説artifactには触れない。level別dir(`{out_dir}/{level}/key_phrases`)に保存。"""
    ja = _part1_ja_gen()
    kp_dir = f"{out_dir}/{level}/key_phrases"
    marker = f"{kp_dir}/{KP_PART1_FAILED_MARKER}"
    path = _part1_ja_path(out_dir, level)
    items = _part1_kp_items(out_dir, level)
    cached = None
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            cached = json.load(f)
    if budget_check is not None:
        budget_check("before kp_part1_ja")
    _parts = os.path.normpath(source_dir).replace("\\", "/").split("/")
    try:
        with cl.logging_context(_parts[-2] if len(_parts) >= 2 else "part1", "kp_part1_ja"):   # 費用ログのstageタグ(訳の原価を単独で集計できる)
            doc = ja.resolve_translations(items, cached, call_fn=call_fn, client=client,
                                          article_text=load_text(f"{source_dir}/{level}/article.md"))
    except (ja.KpSourceSentenceJaError, ja.KpSourceSentenceJaInputError) as exc:
        os.makedirs(kp_dir, exist_ok=True)
        status = f"KP_PART1_JA_FAILED({type(exc).__name__})"
        save_json(marker, {"status": status, "reason": str(exc), "next_command": part1_next_command(source_dir, level)})
        return {"status": status, "reason": str(exc)}
    if not doc.get("reused_from_previous_run"):
        save_json(path, doc)
    return {"status": "OK", "reused": bool(doc.get("reused_from_previous_run")),
            "total_cost_jpy": (doc.get("audit") or {}).get("total_cost_jpy")}


def _require_part1_ja_fresh_x(source_dir: str, out_dir: str, where: str, level: str = "b1b") -> dict:
    """委任_16 T1: 訳の存在と最新性(tts/assemble/player入口)。無い/古いならRuntimeError(STOP、次コマンド付き)。"""
    ja = _part1_ja_gen()
    items = _part1_kp_items(out_dir, level)
    path = _part1_ja_path(out_dir, level)
    doc = None
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
    try:
        ja.require_fresh_translations(items, doc, where=where, next_command=part1_next_command(source_dir, level))
    except ja.KpSourceSentenceJaStale as exc:
        raise RuntimeError(f"[STOP][Part 1] KP_PART1_JA_NOT_READY: {exc}") from exc
    return doc


def generate_part1(client, source_dir: str, out_dir: str, *, level: str = "b1b", call_fn=None, budget_check=None) -> dict:
    """指定levelのPart 1解説を生成・保存する(signature一致ならAPI 0で再利用、不一致なら自動再生成=Xの`kp_expl`系と同型)。
    失敗(技術retry1回後も構造NG・入力不正・model不一致)は専用marker kp_part1_failed.jsonを書き status=KP_PART1_FAILED(...)を返す。
    成功したらmarkerを削除する。例外(budget等)は握りつぶさない。level別dirに保存(b1b/a2相互独立)。"""
    p1 = _part1_gen()
    kp_dir = f"{out_dir}/{level}/key_phrases"
    marker = f"{kp_dir}/{KP_PART1_FAILED_MARKER}"
    path = _part1_explanations_path(out_dir, level)
    items = _part1_kp_items(out_dir, level)
    cached = None
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            cached = json.load(f)
    if budget_check is not None:
        budget_check("before kp_part1")
    _parts = os.path.normpath(source_dir).replace("\\", "/").split("/")
    try:
        with cl.logging_context(_parts[-2] if len(_parts) >= 2 else "part1", "kp_part1"):   # 費用ログのstageタグ(Part 1の原価を単独で集計できる)
            doc = p1.resolve_general_explanations(items, cached, call_fn=call_fn, client=client, level=level)
    except (p1.KpGeneralExplanationError, p1.KpGeneralExplanationInputError) as exc:
        os.makedirs(kp_dir, exist_ok=True)
        status = f"KP_PART1_FAILED({type(exc).__name__})"
        save_json(marker, {"status": status, "reason": str(exc), "next_command": part1_next_command(source_dir, level)})
        return {"status": status, "reason": str(exc)}
    if not doc.get("reused_from_previous_run"):   # 再利用時は保存済みファイルを書き換えない(生成時のaudit/response_idsを保つ)
        save_json(path, doc)
    if os.path.exists(marker):
        os.remove(marker)
    return {"status": "OK", "reused": bool(doc.get("reused_from_previous_run")),
            "total_cost_jpy": (doc.get("audit") or {}).get("total_cost_jpy")}


def generate_part1_all(client, source_dir: str, out_dir: str, *, level: str = "b1b", call_fn=None, ja_call_fn=None, budget_check=None) -> dict:
    """Part 1の生成点(解説1 call + 訳1 call、独立)。解説がOKのときだけ訳へ進む(解説失敗=TTS前STOP)。どちらかの失敗は
    kp_part1_failed.json+status。戻り値statusはOKまたは失敗status、explanation/translationに各結果。"""
    r1 = generate_part1(client, source_dir, out_dir, level=level, call_fn=call_fn, budget_check=budget_check)
    if r1["status"] != "OK":
        return r1
    r2 = generate_part1_ja(client, source_dir, out_dir, level=level, call_fn=ja_call_fn, budget_check=budget_check)
    if r2["status"] != "OK":
        return r2
    costs = [x for x in (r1.get("total_cost_jpy"), r2.get("total_cost_jpy")) if x is not None]
    return {"status": "OK", "reused": bool(r1.get("reused") and r2.get("reused")), "explanation": r1, "translation": r2,
            "total_cost_jpy": round(sum(costs), 4) if costs else None}


def assemble_part1_x(source_dir: str, out_dir: str, *, level: str = "b1b") -> list:
    """Part 1の組立(決定論)+study_text/保存。存在・最新性(Opus M2)・gloss HR/未評価・引用の逐語実在・訳(T1)の最新性をSTOPで確認する。"""
    p1 = _part1_gen()
    items = _part1_kp_items(out_dir, level)
    doc = _require_part1_fresh_x(source_dir, out_dir, "assemble", level)
    ja_doc = _require_part1_ja_fresh_x(source_dir, out_dir, "assemble", level)
    try:
        rows = p1.assemble_part1(items, doc, _part1_ja_gen().translations_by_rank(ja_doc), load_text(f"{source_dir}/{level}/article.md"), level=level)
    except p1.KpGeneralExplanationError as exc:
        raise RuntimeError(f"[STOP][Part 1] 組立NG: {exc}") from exc
    p1.write_study_text(f"{out_dir}/{level}/study_text", rows, level=level)
    return rows


def _require_part1_fresh_x(source_dir: str, out_dir: str, where: str, level: str = "b1b") -> dict:
    """Opus M2: tts/assemble/player入口の確認(存在+signature一致)。無い/古いならRuntimeError(STOP、次コマンド付き)。"""
    p1 = _part1_gen()
    items = _part1_kp_items(out_dir, level)
    path = _part1_explanations_path(out_dir, level)
    doc = None
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
    try:
        p1.require_fresh_general_explanations(items, doc, where=where, next_command=part1_next_command(source_dir, level), level=level)
    except p1.KpGeneralExplanationStale as exc:
        raise RuntimeError(f"[STOP][Part 1] KP_PART1_NOT_READY: {exc}") from exc
    return doc


def run_study_text_stage(client, source_dir: str, out_dir: str, *, level: str = "b1b", call_fn=None, ja_call_fn=None, budget_check=None) -> dict:
    """`--stage study_text`: 既存keywords_canonicalized.jsonからPart 1だけを(再)生成する(KP再選定・support再生成なし)。
    Opus M1の事前確認: KP stage成功済み(kp_stage_failed.jsonなし・KP成果物あり)。成功でkp_part1_failed.jsonを削除、study_text/を保存。"""
    kpf = _kp_stage_failed_markers(out_dir, [level])
    if kpf:
        raise RuntimeError(f"[STOP][Part 1] KP_STAGE_FAILED markerあり(旧attemptのKPを使わない): {kpf}")
    _part1_kp_items(out_dir, level)   # KP成果物なし/空はSTOP
    r = generate_part1_all(client, source_dir, out_dir, level=level, call_fn=call_fn, ja_call_fn=ja_call_fn, budget_check=budget_check)
    if r["status"] != "OK":
        return r
    assemble_part1_x(source_dir, out_dir, level=level)
    return r


def part1_study_html_for_player(source_dir: str, out_dir: str, level: str = "b1b") -> str:
    """player.html用のstudy block。M2確認+study_text/保存は常に行い、描画は訳欄の判断記録がある場合のみ(無ければ空文字)。"""
    p1 = _part1_gen()
    rows = assemble_part1_x(source_dir, out_dir, level=level)
    try:
        return p1.render_html_block(rows)
    except p1.KpGeneralExplanationError as exc:
        raise RuntimeError(f"[STOP][Part 1] 描画NG: {exc}") from exc


# ------------------------------------------------------------
# 学習テキスト Part 2「Grammar & Sentence Structure」(PART2-GRAMMAR-PRODUCTION-WIRING-01 委任_03 / KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01 委任_03、
# ユーザーAPPROVED_FOR_PRODUCTION 2026-10-25。GRAMMAR-PREGEN-ALL-LEVELS-01 委任_03で両level[Std=a2/Adv=b1b]化: 全候補の解説は候補抽出直後に事前生成、finalizeはLLM 0)。設計: docs/research/PART2-GRAMMAR-PRODUCTION-WIRING-01/DESIGN_02.md §3〜§4
# 候補抽出(Step A'')=本文確定直後・KP候補生成(同一待機点)の前 / 確定(Human確認 or 明示宣言)後にStep B(再抽出なし)=Part 1(T1訳)の後。
# 失敗は part2_failed.json + rc=3(案内は`--stage study_text`の1つだけ。scaffold再実行=support/KP再生成を案内しない)。待機はKPと1回にまとめてrc=4。
# ------------------------------------------------------------
def _p2w():
    import er120_part2_wiring_01 as p2w
    return p2w


def _part2_study_dir(out_dir: str, level: str) -> str:
    return _p2w().study_dir_for("x", out_dir, level)


def _part2_inputs_x(source_dir: str, level: str):
    p2w = _p2w()
    article = load_text(f"{source_dir}/{level}/article.md")
    return p2w.g.paragraphs_from_article_md(article), p2w.label_for(article)


def part2_next_command(source_dir: str, level: str = "b1b") -> str:
    """Part 2だけの再実行コマンド案内(level別。`--level <b1b|a2> --stage study_text`)。"""
    _p2w().g.level_name(level)
    parts = os.path.normpath(source_dir).replace("\\", "/").split("/")
    slug, run = (parts[-2], parts[-1]) if len(parts) >= 2 else ("<slug>", "<run>")
    return (f"`--slug {slug} --run {run} --level {level} --stage study_text`(Part 2だけ再実行。support生成・KP選定・Step A''の再抽出をやり直さない。"
            "未確定なら `py er119_kp_human_review_cli_01.py grammar-select --run <out_dir> ...` で決めてから)")


def _part2_pool_x(out_dir: str, level: str):
    """Part 1訳との食い違い検査用pool。Part 1対象level(Advanced、およびマーク付きStandard)のみ。マーク無しStandardは空(検査対象なし)。"""
    if not part1_enabled(out_dir, level):
        return {}
    p2w = _p2w()
    items = _part1_kp_items(out_dir, level)
    jp = _part1_ja_path(out_dir, level)
    return p2w.part1_ref_ja_pool(items, load_json(jp) if os.path.exists(jp) else None)


SCAFFOLD_RESUME_COMMAND = ("同じ `--stage scaffold` コマンドを再実行(この時点ではsupport/KPは未発注のため再生成にならない。"
                           "候補と生成済みの解説は再利用し、未生成分だけ生成する。--regenerate系は使わない)")


def run_part2_candidates_x(client, source_dir: str, out_dir: str, *, level: str, extract_call_fn=None, explain_call_fn=None, budget_check=None,
                           next_command: str | None = None) -> dict:
    """候補抽出(または保存済みの再利用=API 0)+全候補の解説事前生成(Step Bの唯一の呼出点=pregen_stage。resumeは未生成分のみ)+待機/自動確定の評価。
    失敗はpart2_failed.json。returns {"status":"OK","state":"READY"|"PENDING","pending":{...}|None,...} | {"status":"PART2_STAGE_FAILED(...)","reason":...}"""
    p2w = _p2w()
    g = p2w.g
    paragraphs, label = _part2_inputs_x(source_dir, level)
    sd = _part2_study_dir(out_dir, level)
    slug = _slug_of(source_dir)
    names = p2w.stage_names(level)
    guard = (lambda stage, est: budget_check(f"part2 {stage}")) if budget_check else None
    nxt = next_command or part2_next_command(source_dir, level)
    try:
        with cl.logging_context(slug, f"part2_cand_{level}"):
            res = p2w.candidate_stage(sd, level=level, run_dir=out_dir, family="x", slug=slug, paragraphs=paragraphs, label=label, run_hint=out_dir,
                                      extract_call_fn=extract_call_fn, client=client, budget_guard=guard)
    except (g.Part2Error, g.Part2InputError) as exc:
        refused = "CONFIRMED_CONTENT_LOCKED" in str(exc)
        if not refused:   # D4: 確定済み文法の --regenerate-stage 拒否(revoke前)は失敗記録を書かない。次の一手はrevoke案内
            g.write_failed_record(sd, exc, next_command=nxt, stage=names["cand"])
        return {"status": f"PART2_STAGE_FAILED({names['cand']})", "reason": str(exc),
                "next_command": (f"確定済みの文法(Part 2 {level})は変えられません。変える場合は先に `py er128_kp_confirmed_content_01.py revoke --run {out_dir} --level {level} ...` "
                                 "(確定の取消し)を実行。変えないなら何もしない" if refused else nxt)}
    try:
        with cl.logging_context(slug, f"part2_expl_{level}"):
            pre = p2w.pregen_stage(sd, level=level, next_command=nxt, run_hint=out_dir,
                                   explain_call_fn=explain_call_fn, client=client, budget_guard=guard)   # 失敗記録(part2_failed.json)はpregen_stageが書く
    except (g.Part2Error, g.Part2InputError) as exc:
        return {"status": f"PART2_STAGE_FAILED({names['expl']})", "reason": str(exc), "next_command": nxt}
    return {"status": "OK", **res, "pregen": pre}


def run_part2_final_x(client, source_dir: str, out_dir: str, *, level: str, budget_check=None) -> dict:
    """確定済みの文法reviewからfinalize(**LLM 0 call**。解説は事前生成物/凍結値。再抽出もStep Bもしない)。Advancedは Part 1(T1訳)確定後に呼ぶ(訳が参考訳pool)。"""
    p2w = _p2w()
    g = p2w.g
    paragraphs, label = _part2_inputs_x(source_dir, level)
    sd = _part2_study_dir(out_dir, level)
    pool = _part2_pool_x(out_dir, level)
    names = p2w.stage_names(level)
    try:
        out = p2w.finalize_stage(sd, level=level, paragraphs=paragraphs, label=label, ref_ja_pool=pool)
    except g.Part2PendingReview as e:
        return {"status": "PART2_PENDING", "review_status": e.status}
    except p2w.Part2NotConfirmed as exc:   # Part 1訳との食い違いISSUE(失敗ではなく待機=rc=4。解消=別の文法を選ぶ/ユーザー了承)
        pend = dict(p2w.gr.pending_summary(sd, p2w.gr.load_review(sd)), translation_issue=str(exc))
        return {"status": "PART2_TRANSLATION_ISSUE", "review_status": "TRANSLATION_ISSUE", "pending": pend, "reason": str(exc)}
    except (g.Part2Error, g.Part2InputError) as exc:
        g.write_failed_record(sd, exc, next_command=part2_next_command(source_dir, level), stage=names["final"])
        return {"status": f"PART2_STAGE_FAILED({names['final']})", "reason": str(exc)}
    fp = f"{sd}/{g.FAILED_FILENAME}"
    if os.path.exists(fp):
        os.replace(fp, fp.replace(".json", ".resolved.json"))   # 成功したら失敗記録は解決済みへ退避(削除しない)
    return {"status": "OK", "part2_status": out["status"], "reused": out["reused"]}


def _require_part2_fresh_x(source_dir: str, out_dir: str, where: str, *, level: str) -> dict:
    """M-2: tts/assemble/player入口と公開ページbuilderの確認(存在+最新性+確定との一致)。未確定=Part2NotConfirmed(rc=4)、無い/古い=RuntimeError(STOP rc=3)。"""
    p2w = _p2w()
    g = p2w.g
    paragraphs, label = _part2_inputs_x(source_dir, level)
    pool = _part2_pool_x(out_dir, level)
    try:
        return p2w.require_final(_part2_study_dir(out_dir, level), paragraphs, label, level=level, next_command=part2_next_command(source_dir, level),
                                 where=where, ref_ja_pool=pool)
    except p2w.Part2NotConfirmed:
        raise
    except (g.Part2Error, g.Part2InputError) as exc:
        raise RuntimeError(f"[STOP][Part 2] PART2_NOT_READY: {exc}") from exc


def _part2_failed_markers(out_dir: str, levels: list) -> list:
    g = _p2w().g
    return [f"{_part2_study_dir(out_dir, lv)}/{g.FAILED_FILENAME}" for lv in levels
            if os.path.exists(f"{_part2_study_dir(out_dir, lv)}/{g.FAILED_FILENAME}")]


def _scaffold_part2_final(client, source_dir: str, out_dir: str, level: str, result: dict, budget_check, done_note: str):
    """scaffold内のPart 2 finalize(LLM 0)。失敗=stage statusを返す(None=OK/待機)。Part 1訳との食い違いISSUEは失敗ではなく待機(result[level]['part2_pending']へ。rc=4)。"""
    _p2f = run_part2_final_x(client, source_dir, out_dir, level=level, budget_check=budget_check)
    result[level]["part2"] = _p2f
    if _p2f["status"] == "OK":
        return None
    if _p2f["status"] == "PART2_TRANSLATION_ISSUE":
        result[level]["part2_pending"] = _p2f["pending"]
        print(f"[FAMILY-X-AUDIO-SCAFFOLD] {level}: 待機中: 文法(Part 2)の訳がPart 1の訳と食い違っています(ユーザー確認待ち): {_p2f.get('reason')}")
        return None
    result[level]["part2_stage_status"] = _p2f["status"]
    print(f"[FAMILY-X-AUDIO-SCAFFOLD][STOP] {level}: {_p2f['status']}: {_p2f.get('reason')}"
          f"({done_note}。TTS前に停止。次の一手: {part2_next_command(source_dir, level)})")
    return _p2f["status"]


def run_theme_scaffold(client, source_dir: str, out_dir: str, levels: list[str],
                        scaffold_only: str | None = None, budget_check=None,
                        kp_backend: str = "fulltext_p2", part1_call_fn=None, part1_ja_call_fn=None,
                        part2_extract_call_fn=None, part2_explain_call_fn=None) -> dict:
    """既存sc.run_key_phrases()(選定+canonicalization+redundancy QA)を
    Family X本文へそのまま適用する(記事冒頭Key Phrasesは既存Family A
    既定構成をそのまま再利用する、本委任文の前提どおり)。

    kp_backend(KPFT 委任_02、2026-10-22): Family X通常記事は全文選定(Prompt 2・最大3件、"fulltext_p2")を既定で使う。
    選定失敗はX/Z共通の外側retry後にfail-closedで停止し、旧5件経路(db_hybrid/Strategy L)へfallbackしない。
    他Family(A/B/C)の`sc.run_key_phrases`呼び出しはこの引数を渡さないため既定"strategy_l"のまま無変更。"""
    # FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01(Opus Q5条件、`--scaffold-only kp`):
    #  (i) `sc.run_key_phrases(..., kp_backend=kp_backend)`呼出は下記の同じ行を通す(support生成ブロックのみskip)
    #  (ii) `record_scaffold_article_sha`と`scaffold_run_summary`/`kp_backend_used`記録は維持
    #  (iii) support成果物(sha照合済みcopy)がout_dirに無ければSTOP
    #  (iv) KP再生成は1レベル1回(既にKP成果物があればSTOP、NGでも引き直さない)
    if scaffold_only not in (None, "kp"):
        raise ValueError(f"scaffold_onlyはNoneまたは'kp'のみ: {scaffold_only!r}")
    result = {}
    for level in levels:
        article_path = f"{source_dir}/{level}/article.md"
        article_text = load_text(article_path)
        parts = plan.split_family_x_article_text_v2(article_text)
        if parts.get("status") != "OK":
            raise RuntimeError(
                f"[STOP] Family X audio scaffold: {article_path}のparagraph_count="
                f"{parts.get('paragraph_count')}<3のため3分割できません(TOO_FEW_PARAGRAPHS)。"
                "Writer stageのparagraph retryが既に使用済みのはずのため、本文を手で直さず"
                "STOPします。"
            )
        level_out_dir = f"{out_dir}/{level}"
        save_json(f"{level_out_dir}/parts.json", parts)
        # C3-1(RISK-FLAGGER-PRODUCTION-WIRING-01): scaffold時点の元記事sha256を記録する
        # (TTS直前の三者sha照合[scaffold時sha == source記事sha == Queue sha]の1者目)。
        record_scaffold_article_sha(out_dir, level, article_path)

        kp_dir = f"{level_out_dir}/key_phrases"
        # Part 2(文法): 候補抽出を本文確定直後・KP候補生成(同一待機点)の前に実行する。失敗はsupport/KPを発注する前に止める(再開でsupport再生成なし)。
        # `--scaffold-only kp`(KPだけの再実行)では実行しない(tts前の入口検査が`--stage study_text`を案内する)。resumeは保存済み候補でAPI 0。
        _p2c = None
        if scaffold_only is None:   # 両level(Standard=a2もAdvanced=b1bも)で候補抽出+解説の事前生成を行う
            _p2c = run_part2_candidates_x(client, source_dir, out_dir, level=level, extract_call_fn=part2_extract_call_fn,
                                          explain_call_fn=part2_explain_call_fn, budget_check=budget_check, next_command=SCAFFOLD_RESUME_COMMAND)
            if _p2c["status"] != "OK":
                result[level] = {"parts": parts, "part2_stage_status": _p2c["status"], "part2_reason": _p2c.get("reason"), "part2_next_command": _p2c.get("next_command")}
                print(f"[FAMILY-X-AUDIO-SCAFFOLD][STOP] {level}: {_p2c['status']}: {_p2c.get('reason')}"
                      f"(support/KPは未発注。次の一手: {_p2c.get('next_command')})")
                break
        _p2_pending = _p2c["pending"] if (_p2c is not None and _p2c["state"] == "PENDING") else None
        # KP Human Review M-4: review/候補ファイルが有効(本文shaが一致)なら、rc=4待機後の再開で有料のsupportを再生成しない
        # (文面が変わり費用がかかるため)。support成果物が無ければSTOP。本文が変わっていれば従来どおりsupportから作り直す。
        _resume_review = scaffold_only is None and _kpw().review_resume_valid(kp_dir, article_text)
        if scaffold_only == "kp":
            _sp = _support_texts_path(level, level_out_dir)
            if not os.path.exists(_sp):
                raise RuntimeError(
                    f"[STOP][scaffold-only kp] support成果物が{_sp}にありません。承認済みPreview/Commentの"
                    "sha照合済みcopyをout_dirへ置いてから実行してください(support文面は再生成しません)。")
            _done = _kp_already_generated(kp_dir)
            if _done:
                raise RuntimeError(
                    f"[STOP][scaffold-only kp] {level}のKey Phraseは既に生成済みです({_done})。"
                    "KP再生成は1レベル1回までです(NGでも引き直しません)。Fableへ報告してください。")
            support = {}
        elif _resume_review:
            _sp = _support_texts_path(level, level_out_dir)
            if not os.path.exists(_sp):
                raise RuntimeError(
                    f"[STOP][KP review再開] {level}: 有効なKP review/候補がありますがsupport成果物({_sp})がありません。"
                    "supportを再生成すると文面が変わるため、自動では再生成しません(Fableへ報告してください)。")
            print(f"[FAMILY-X-AUDIO-SCAFFOLD] {level}: KP review再開(support生成・KP選定はskip。確定のみ実行)")
            support = {}
        elif level == "b1b":
            support = run_family_x_b1_scaffold(client, parts, level_out_dir)
        else:
            support = run_family_x_a2_scaffold(client, parts, level_out_dir)

        # Opus M-2: A2 Comment 3がfail-closed(非OK)ならKP(有料)・Part 1/2のfinalizeへ進まず、専用markerとsupport_stage_statusを残して停止する。
        _sup_marker = f"{level_out_dir}/{SUPPORT_STAGE_FAILED_MARKER}"
        if level != "b1b" and support and (support.get("comment_3") or {}).get("status") not in (None, "OK"):
            _c3s = support["comment_3"].get("status")
            save_json(_sup_marker, {"status": f"SUPPORT_STAGE_FAILED({_c3s})", "level": level, "comment_3_status": _c3s,
                                    "next_command": f"--stage scaffold を再実行(KP未実施のため support を再生成します)"})
            result[level] = {"parts": parts, "support": {k: v.get("status") for k, v in support.items()},
                             "support_stage_status": f"SUPPORT_STAGE_FAILED({_c3s})",
                             "comment3_method": c3z.COMMENT3_Z_METHOD_VERSION}
            print(f"[FAMILY-X-AUDIO-SCAFFOLD][STOP] {level}: SUPPORT_STAGE_FAILED({_c3s})(KP/Part 1/Part 2/TTSは実行しない。"
                  "次の一手: 同じ--stage scaffoldコマンドを再実行[KP未実施なのでsupportから再生成されます])")
            break
        elif os.path.exists(_sup_marker) and support:
            os.remove(_sup_marker)   # 成功時はmarkerを削除(KP markerと同型)

        # (下は変更なし: kp_dir定義は上へ移動済み)
        article_id = f"FAMILY_X_AUDIO_{os.path.basename(out_dir)}_{level}"
        kp_process = "B1_SUPPORT" if level == "b1b" else "A2_SUPPORT"
        if kp_backend == "fulltext_p2":
            # KP Human Review(2026-10-25、ユーザーAPPROVED_FOR_PRODUCTION): 候補(最大8)生成→Human確認/明示の不在宣言→finalize。
            # 共有関数sc.run_key_phrasesは通らない(A/B/C・Y Trialは従来の3件経路のまま)。宣言なし=待機(rc=4)。
            kp = _kpw().run_kp_with_review(text=article_text, kp_dir=kp_dir, run_dir=out_dir, family="x", slug=_slug_of(source_dir),
                                           level=level, article_id=article_id, stop_run_dir=out_dir, run_hint=out_dir)
        else:   # 非Production互換(test/Trial)。X Productionは常にfulltext_p2
            kp = sc.run_key_phrases(article_text, kp_dir, article_id, level, process=kp_process,
                                     kp_backend=kp_backend, stop_run_dir=out_dir)
        kp_status = (kp["canonicalization"] or {}).get("status") if kp["canonicalization"] else kp["selection"]["status"]
        print(f"[FAMILY-X-AUDIO-SCAFFOLD] {level}: key phrase status={kp_status}")
        _kr = kp.get("kp_review") or {}
        if _kr.get("state") == "PENDING":
            # 失敗ではなく待機。残levelの候補も生成してから、main()がまとめてrc=4で止める(Part 1・TTSなど有料の後続へは進まない)。
            result[level] = {"parts": parts, "support": {k: v.get("status") for k, v in support.items()},
                             "key_phrases_status": "KP_REVIEW_PENDING", "kp_backend_used": None, "kp_review_state": "PENDING",
                             "kp_review_pending": _kr["pending"]}
            if _p2_pending is not None:
                result[level]["part2_pending"] = _p2_pending
            print(f"[FAMILY-X-AUDIO-SCAFFOLD] {level}: 待機中: Human確認待ち(依頼書: {_kr['pending'].get('request_md')})")
            continue
        # fail-closed(KPMP-03 委任_03): PASS系以外はstageを止める(Zと対称)。ただしsummary(kp_run_status/gloss HR event等、
        # OF-KGCPW-04/16)は欠落させず全て記録してから、下のloop末尾でmarker+kp_stage_statusを付けて残levelを実行せず終了する。
        # 実際のrc≠0停止はmain()側(result内のkp_stage_statusを検出してFamilyXKPStageFailed)。markerは成功時に削除する。
        _marker = f"{kp_dir}/{KP_STAGE_FAILED_MARKER}"
        _fail = kp_stage_failure_status(kp)
        if _fail is None and os.path.exists(_marker):
            os.remove(_marker)

        # 修正1回目(Opus L2所見B2、2026-09-27): result[level]へ
        # kp_backend_usedを載せる(entry_point.jsonへの反映はmain()側で
        # scaffold stage完了後に行う)。
        kp_backend_used = (kp.get("selection") or {}).get("kp_backend_used")

        result[level] = {"parts": parts, "support": {k: v.get("status") for k, v in support.items()},
                          "key_phrases_status": kp_status, "kp_backend_used": kp_backend_used}
        if level != "b1b":   # Opus M-5/R-3: Comment 3の方式versionをlevel別summaryへ記録(再利用時は保存済みauditのversion有無=WARN)
            result[level]["comment3_method"] = _comment3_method_of(level_out_dir, fresh=bool(support))
        if _kr:
            result[level]["kp_review"] = {k: _kr.get(k) for k in ("state", "status", "signature", "round")}
        # KGCPW(OF-KGCPW-04/11/16): gloss再整合は無条件。KP段のtop-level status(kp_run_status)と
        # gloss停止(gloss_alignment_run_status)は別キーで記録する(NG_REVIEW_REQUIREDとHRが重なっても隠れない)。
        _canon = kp.get("canonicalization") or {}
        result[level]["gloss_alignment_human_review_events"] = kp.get("gloss_alignment_human_review_events") or []
        result[level]["kp_run_status"] = kp.get("status")
        result[level]["gloss_alignment_run_status"] = kp.get("gloss_alignment_run_status")
        result[level]["gloss_alignment_status"] = _canon.get("gloss_alignment_status")
        result[level]["gloss_alignment_flag"] = _gloss_align_mod().flag_effective()
        result[level]["gloss_alignment_metrics"] = _canon.get("gloss_alignment_metrics")
        if scaffold_only:
            result[level]["scaffold_only"] = scaffold_only
        if _fail is not None:
            os.makedirs(kp_dir, exist_ok=True)
            save_json(_marker, {"status": _fail, "level": level, "kp_status": kp_status,
                                "kp_run_status": kp.get("status")})
            result[level]["kp_stage_status"] = _fail
            print(f"[FAMILY-X-AUDIO-SCAFFOLD][STOP] {level}: {_fail}(自動採用しない・HR Lockへ送らない・後段TTS/assemblyは実行しない)")
        _part1_fail = None
        _part2_fail = None
        if _p2_pending is not None:
            result[level]["part2_pending"] = _p2_pending   # 文法のHuman確認待ち: Part 1・TTS等の有料の後続へ進まない(KPと1回にまとめてmainがrc=4)
            print(f"[FAMILY-X-AUDIO-SCAFFOLD] {level}: 待機中: 文法(Part 2)のHuman確認待ち(依頼書: {_p2_pending.get('request_md')})")
        elif _fail is None and part1_enabled(out_dir, level):
            # 委任_14: 学習テキスト Part 1(Advanced、およびSLOT-23のマーク付きStandard)。KP PASS後・TTS前。失敗はKP失敗と分離した専用marker+part1_stage_status(Opus M1)。
            _p1r = generate_part1_all(client, source_dir, out_dir, level=level, call_fn=part1_call_fn, ja_call_fn=part1_ja_call_fn, budget_check=budget_check)
            result[level]["part1"] = _p1r
            if _p1r["status"] != "OK":
                _part1_fail = _p1r["status"]
                result[level]["part1_stage_status"] = _part1_fail
                print(f"[FAMILY-X-AUDIO-SCAFFOLD][STOP] {level}: {_part1_fail}: {_p1r.get('reason')}"
                      f"(KPは確定済み。TTS前に停止。次の一手: {part1_next_command(source_dir, level)})")
            else:
                try:   # 組立+study_text/保存。gloss HR/未評価はHR経路(既存)で扱うため、ここでは保留にして止めない
                    assemble_part1_x(source_dir, out_dir, level=level)
                    result[level]["study_text"] = "saved"
                except RuntimeError as exc:
                    result[level]["study_text"] = f"deferred: {exc}"
                if _p2c is not None:   # Part 2: 確定済みの文法reviewからfinalize(LLM 0・再抽出なし)。Part 1の訳が参考訳pool
                    _part2_fail = _scaffold_part2_final(client, source_dir, out_dir, level, result, budget_check, "KP・Part 1は確定済み")
        elif _fail is None and _p2c is not None:
            # マーク無しStandard(a2、遡及なし): Part 1は無い。KP確定後に文法をfinalize(LLM 0)。TTSの前提にはしない(文法はページ専用)
            _part2_fail = _scaffold_part2_final(client, source_dir, out_dir, level, result, budget_check, "KPは確定済み")
        if budget_check is not None:
            budget_check(f"after scaffold {level}")
        if _fail is not None or _part1_fail is not None or _part2_fail is not None:
            break   # 残levelのAPI呼出をしない(Zはstage失敗で停止)
    save_json(f"{out_dir}/scaffold_run_summary.json", result)
    return result


# ============================================================
# Stage: tts(実API呼び出しあり。Stage 1では実行しない)
# ============================================================
_BODY_SEGMENT_NAMES = ("full_story_part1", "full_story_part2", "full_story_part3")

# FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W3、2026-09-29、Opus L2
# 所見MAJOR-3是正): 可変segment(japanese_title/topic_intro/preview/
# comment_*/full_story_*/heading/in_one_line)のstyle仕様(J3/E2/
# japanese_titleへのJ3適用等)を変更するたびに、この値をbumpする。
# tts_generation_results.jsonのトップレベルへ保存し、_generate_or_reuse
# がcacheのversionと比較する。値が不一致または欠落(旧run・旧cache)の
# 場合は可変segmentの再利用を行わない。
#
# W5(2026-09-29、Standard KP日本語意味へのJ3配線[正式決定]+Opus L2所見
# MAJOR-1是正): Key Phrase側の"explanation"(Advanced英語解説)・
# "japanese_meaning"(Standard日本語意味)roleのreuse判定
# (`_generate_or_reuse_kp`のrequire_style_version=True)も、この同じ
# top-level値を参照するようになった(shell固定phrase・KPの"english"
# role[Master Store経由、別途versioning]は引き続きこの値を参照しない)。
# 本バージョンをbumpすることで、japanese_meaningへJ3を初適用する前に
# 生成済みの旧音声(既定JAPANESE_STYLE_PREFIXのまま)が黙ってreuseされる
# ことを防ぐ。
FAMILY_X_VARIABLE_ROLE_STYLE_VERSION = "v3_j3_kp_meaning_and_explanation_guard"


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


# FAMILY-X-COFFEE-FINAL-V5-PRODUCTION-WIRING-01: 必要なsegmentだけを生成する明示CLI(--only-segments)。
# 既定None=全segment(従来とバイト同一)。指定時は対象外segment/Key Phrase componentを生成せず
# status="SKIPPED_NOT_SELECTED"を記録し(Audio Validation Gateは非OKとして扱いAssemblyを止める)、
# shared narrationの確保も行わない。assemble stageとの併用はmain()が拒否する。
_ONLY_SEGMENTS: set | None = None


import re as _re_only_segments
_VALID_ONLY_SEGMENT_RE = _re_only_segments.compile(
    r"^(topic_intro|japanese_title|preview|in_one_line|comment_[1-9]\d*|full_story_part[1-9]\d*(_k[1-9]\d*)?"
    r"|kp[1-5]_(english|explanation|japanese_meaning))$")


def validate_only_segments_args(stage: str, dry_run: bool, level: str, raw: str):
    """--only-segmentsの入力検証(委任_03、OPEN-329)。戻り値=(選択set, エラー文字列|None)。
    tts stage(--dry-runなし)専用 / 空指定禁止 / 未知segment名を拒否 /
    --level both併用禁止(同一指定が両levelへ及ぶハザード。a2またはb1bを明示すること)。"""
    if stage != "tts" or dry_run:
        return None, "--only-segmentsは--stage tts(--dry-runなし)でのみ使えます。"
    sel = {x.strip() for x in raw.split(",") if x.strip()}
    if not sel:
        return None, "--only-segmentsが空です。"
    if level == "both":
        return None, "--only-segmentsは--level both併用禁止です(--level a2または--level b1bを明示してください)。"
    unknown = sorted(x for x in sel if not _VALID_ONLY_SEGMENT_RE.match(x))
    if unknown:
        return None, f"--only-segmentsに未知のsegment名があります: {unknown}"
    # CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01(ユーザー正式承認2026-10-26): Standardもchunk化するため、Std(a2)の_k指定拒否(旧I5)を撤去した。
    # _kは本文part(full_story_part{n})にのみ付く(_VALID_ONLY_SEGMENT_REが保証)。in_one_line/comment等への_kは未知segment名として拒否される。
    return sel, None


def _chunk_parent_selected(label: str) -> bool:
    """chunk id(full_story_part{n}_k{j})は、親(full_story_part{n})が選択されていれば選択扱い(I5)。"""
    p = chunk_tts.parse_chunk_id(label)
    return bool(p and _ONLY_SEGMENTS is not None and p[0] in _ONLY_SEGMENTS)


def _only_segments_skip(label: str):
    if _ONLY_SEGMENTS is not None and label not in _ONLY_SEGMENTS and not _chunk_parent_selected(label):
        return {"status": "SKIPPED_NOT_SELECTED", "reason": "--only-segmentsに含まれないため生成しません"}
    return None


def _gloss_align_mod():
    import er003_key_words_gloss_alignment as _ga
    return _ga


def _gloss_alignment_hr_unresolved(kp):
    """関所: artifactにHuman Review待ち(gloss_alignment_status=FAILED_HUMAN_REVIEW_REQUIRED、旧版の"FAILED"含む)の
    itemがあれば、そのitem一覧を返す。さらに(OF-KGCPW-08)再整合の対象なのにgloss_alignment_statusが無い=ON化前・未評価の
    itemも、`_unevaluated=True`付きで返す(決定論・LLM 0。対象0件の成果物は通過)。HR解消(resolve_gloss)後は
    HUMAN_RESOLVEDになり通過する。
    ITEM1(2026-10-19、人称・指示対象整合): collect_unevaluatedは消費側の定義(select_consumer_unevaluated)=従来の未評価 ∪
    決定論の人称語突合で不整合のitem。X runnerはここでSTOPするだけで修復経路は持たない(Zのstage_kp関所のみが修復する。
    census上Xの不整合artifactは0件。OPEN_ITEMSに『X: 修復経路なし・STOPのみ』を記録)。"""
    _ga = _gloss_align_mod()
    out = list(_ga.collect_unresolved(kp))
    out += [{**it, "_unevaluated": True} for it in _ga.collect_unevaluated(kp)]
    return out


def _gloss_hr_levels_from_artifacts(out_dir: str, levels: list | None = None) -> dict:
    """OF-KGCPW-05: 最終行/rc判定の基準=ディスク上のartifactのcollect_unresolved(報告書ファイルの有無ではない)。
    戻り値 {level: [rank,...]}(HR待ちのlevelのみ)。"""
    import glob as _glob
    _ga = _gloss_align_mod()
    res = {}
    for pth in sorted(_glob.glob(f"{out_dir}/*/key_phrases/keywords_canonicalized.json")):
        lv = os.path.basename(os.path.dirname(os.path.dirname(pth)))
        if levels is not None and lv not in levels:
            continue
        try:
            with open(pth, encoding="utf-8") as _f:
                doc = json.load(_f)
        except (OSError, ValueError):
            continue
        un = _ga.collect_unresolved(doc)
        if un:
            res[lv] = [it.get("rank") for it in un]
    return res


def _gloss_alignment_stopped_entry(unresolved: list, role: str) -> dict:
    """`_only_segments_skip`と同型の非OK status(0 API call)。Audio Validation Gateは非許可statusとして
    UNVALIDATED扱い(record_human_approvalの承認対象にも含まれない)にし、assemblyを拒否する。"""
    import er003_key_words_gloss_alignment as _ga
    ranks = [it.get("rank") for it in unresolved]
    if any(it.get("_unevaluated") for it in unresolved):
        reason = (f"{_ga.UNEVALUATED_REASON}(rank={ranks})のため、このlevelのKP segment({role})はTTS/LLMを"
                  "実行しません(0 API call)。")
    else:
        reason = (f"KP日本語glossの再整合が成立せずHuman Review待ち(rank={ranks})のため、このlevelのKP segment"
                  f"({role})はTTS/LLMを実行しません(0 API call)。GLOSS_ALIGNMENT_HUMAN_REVIEW_01.md参照。"
                  "resolve_gloss後に再実行してください。")
    return {"status": _ga.STOPPED_STATUS, "reason": reason, "gloss_alignment_ranks": ranks}


def _gloss_alignment_stopped_kp_results(kp_items: list, unresolved: list, roles: tuple) -> dict:
    """当該levelのKP segment全体(全rank・全role)を保留する(Opus (h): KP再生成が5件全体に影響するため)。"""
    return {it["rank"]: {role: _gloss_alignment_stopped_entry(unresolved, f"kp{it['rank']}_{role}") for role in roles}
            for it in kp_items}


def _with_recorded_sha256(generate_fn):
    """委任_03(是正③の再発防止): 新規生成でstatus=OKとなったsegment entryに、最終wavのsha256を記録する
    (既にshaがあれば不変)。`--only-segments`で非選択になった次回runでも、sha256付きの検証済みentryは
    REUSED_VALIDATEDとして引き継げる(shaが無いと引継ぎ証拠不足でSKIPPED_NOT_SELECTEDに上書きされ、
    正式Validation済みの音声がGateでUNVALIDATED扱いになる既存不具合の根本是正)。Gate・生成物は変更しない。"""
    def wrapped():
        result = generate_fn()
        try:
            if (isinstance(result, dict) and result.get("status") == "OK" and not result.get("sha256")
                    and result.get("path") and os.path.exists(result["path"])):
                result["sha256"] = validation_inheritance.sha256_file(result["path"])
        except OSError:
            pass
        return result
    return wrapped


def _mark_asr_judgement_inherited(reused: dict) -> None:
    """AUW 委任_03(additive): 前回runの音声を再利用する場合、元の`asr_judgement`(PASS_WITH_WARNING等)を
    `asr_judgement_inherited`へ移し、事後試聴リストが再利用音声の元のWARNINGを継承して表示できるようにする。"""
    if "asr_judgement" in reused:
        reused["asr_judgement_inherited"] = reused.pop("asr_judgement")


def _reuse_guard_blocks(cached_result: dict | None, label: str, *, kp_vote_gate_follows: bool = False) -> dict | None:
    """AUW 委任_06c(OF-AUW-C-03、ADDENDUM §3-1): 前回resultsのOK entryを再利用する前に、保存転写のみ(API 0)を現行の統一judgeへ
    通す。値ガードDIFF/否定差(`reuse_blocked` markを含む)ならguard情報dictを返す(=呼出側は再利用せず再生成する)。
    転写が無い/判定不能な旧entryは従来どおり再利用(None)。"""
    import er078_reuse_value_guard_01 as _rvg
    g = _rvg.guard_entry(cached_result, label=label, kp_vote_gate_follows=kp_vote_gate_follows)
    return g if g.get("blocked") else None


def _regenerate_after_reuse_block(generate_fn, guard_info: dict):
    r = generate_fn()
    if isinstance(r, dict):
        r["reuse_value_guard_blocked_previous"] = {k: guard_info.get(k) for k in ("reason", "reason_code", "unified_state")}
    return r


def _generate_or_reuse(cached: dict | None, name: str, wav_path: str, generate_fn, expected_text: str | None = None):
    generate_fn = secondary_run_scope.guard_generate(_with_recorded_sha256(generate_fn), name)  # 委任_06c: circuit open中は技術STOP
    """前回run(同一out_dir)のOK segmentを再利用する。Stage 3c(見出し
    sub-segment分離)で判明した安全性ギャップの修正: 従来はstatus=="OK"+
    wavファイル存在のみで再利用可否を判定していたが、これだと
    full_story_part2/3のように「segment_idは同じだがcanonical textが
    変わった」場合(本文2/3から見出し文が除去された等)、古い(異なる文面の)
    音声を誤って再利用してしまう。expected_textが渡された場合は、cache
    されたcanonical_textと完全一致する場合のみ再利用する(不一致時は
    generate_fn()で必ず再生成し、古い音声の使い回しを防ぐ)。expected_text
    省略時(既存呼び出し元、後方互換)は従来どおりの挙動を維持する。

    FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W3、Opus L2所見MAJOR-3
    是正): cachedのトップレベル"style_version"が現行の
    FAMILY_X_VARIABLE_ROLE_STYLE_VERSIONと不一致・欠落の場合、可変
    segmentのreuseを一切行わない(必ずgenerate_fn()で再生成する)。
    旧cache(本是正以前のrun)にはこのキー自体が無いため既定でNoneとなり、
    確実に不一致(=再生成)になる。"""
    _skip = _only_segments_skip(name)
    if _skip is not None:
        # FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01(是正②、OPEN-346②): 非選択segmentでも、同一out_dirの前回results
        # entryが正式Validation済み(status=OK・asr_verified・entry.sha256==現在wav・canonical_text一致)の場合に限り、
        # SKIPPED_NOT_SELECTEDで上書きせず検証済みentryを引き継ぐ(label=REUSED_VALIDATED)。証拠が揃わなければ従来どおり
        # SKIPPED(=Gate BLOCK維持)。Gateの判定は変更していない。
        _inh = validation_inheritance.try_inherit_from_cached(
            (cached.get("segments") or {}).get(name) if cached else None, wav_path, expected_text,
            cached.get("style_version") if cached else None, FAMILY_X_VARIABLE_ROLE_STYLE_VERSION,
            {"kind": "same_out_dir_previous_results", "label": name})
        return _inh if _inh is not None else _skip
    if cached is not None and cached.get("style_version") != FAMILY_X_VARIABLE_ROLE_STYLE_VERSION:
        return generate_fn()
    cached_result = (cached.get("segments") or {}).get(name) if cached else None
    if cached_result and cached_result.get("status") == "OK" and os.path.exists(wav_path):
        if expected_text is not None and cached_result.get("canonical_text") != expected_text:
            return generate_fn()
        _blk = _reuse_guard_blocks(cached_result, name)
        if _blk is not None:
            return _regenerate_after_reuse_block(generate_fn, _blk)
        reused = dict(cached_result)
        reused["reused_from_previous_run"] = True
        _mark_asr_judgement_inherited(reused)
        return reused
    return generate_fn()


def _generate_or_reuse_kp(cached: dict | None, rank: int, role: str, wav_path: str, generate_fn,
                           expected_text: str | None = None, require_style_version: bool = False):
    """FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W5、Opus L2所見MAJOR-1
    是正、2026-09-29): 従来はstatus=="OK"+ファイル存在のみでreuseしており、
    role="explanation"(KP英語解説、LLM生成のため文面が変わりうる)・
    role="japanese_meaning"(Standard KP日本語意味、W5でJ3 styleを新規
    適用)のいずれもtext/style_versionの不一致を検知できなかった
    (`_generate_or_reuse`が可変segmentに対して既に持つガードと同型の
    穴)。

    expected_text指定時: cachedの"canonical_text"と一致する場合のみ
    reuse(不一致ならgenerate_fn()で再生成)。
    require_style_version=True指定時: cached(トップレベルのdict、
    tts_generation_results.json全体)の"style_version"が現行の
    FAMILY_X_VARIABLE_ROLE_STYLE_VERSIONと一致する場合のみreuse対象に
    する(不一致・欠落なら常に再生成)。role="english"(Key Phraseの
    使用形そのもの、Master Store側のversioningで別途管理)は既定どおり
    require_style_version=Falseのまま(この引数を渡さない呼び出し元は
    従来どおりの挙動)。"""
    generate_fn = secondary_run_scope.guard_generate(generate_fn, f"kp{rank}_{role}")  # 委任_06c: circuit open中は技術STOP
    if role == "english":
        generate_fn = kp_vote.guard_whisper(generate_fn, f"kp{rank}_{role}")   # KP3V(P-08): Whisper事前確認/circuit open中はTTSを回さず技術STOP
    _skip = _only_segments_skip(f"kp{rank}_{role}")
    if _skip is not None:
        # 是正②: 上記_generate_or_reuseと同じ証拠つき引継ぎ(Key Phrase component版)。
        _kp_cache0 = (cached.get("key_phrases") or {}) if cached else {}
        _cached_kp = (_kp_cache0.get(str(rank)) or _kp_cache0.get(rank) or {}).get(role) if _kp_cache0 else None
        _inh = validation_inheritance.try_inherit_from_cached(
            _cached_kp, wav_path, expected_text,
            cached.get("style_version") if cached else None, FAMILY_X_VARIABLE_ROLE_STYLE_VERSION,
            {"kind": "same_out_dir_previous_results", "label": f"kp{rank}_{role}"},
            # KP3V(再利用点2): KP英語phraseの引継ぎは両Provider PASSの保存証跡を要する(API 0・fail-closed)。
            kp_vote_canonical=(n3_tts.tts_safe_kp_en(expected_text) if (role == "english" and kp_vote.vote_enabled() and expected_text)
                               else None),
            kp_vote_required=bool(role == "english" and kp_vote.vote_enabled()))
        return _inh if _inh is not None else _skip
    if require_style_version and cached is not None and cached.get("style_version") != FAMILY_X_VARIABLE_ROLE_STYLE_VERSION:
        return generate_fn()
    kp_cache = (cached.get("key_phrases") or {}) if cached else {}
    cached_result = (kp_cache.get(str(rank)) or kp_cache.get(rank) or {}).get(role) if kp_cache else None
    if cached_result and cached_result.get("status") == "OK" and os.path.exists(wav_path):
        if expected_text is not None and cached_result.get("canonical_text") != expected_text:
            return generate_fn()
        _blk = _reuse_guard_blocks(cached_result, f"kp{rank}_{role}",
                                   kp_vote_gate_follows=bool(role == "english" and kp_vote.vote_enabled()))   # OF-KPQ-P-01: 直後にkp_vote_reuse_okが続く
        if _blk is not None:
            return _regenerate_after_reuse_block(generate_fn, _blk)
        _kd = None
        if role == "english" and kp_vote.vote_enabled():
            # KP3V(OF-KPD-P-03、再利用点1): 前回results再利用は両Provider PASSの証跡を要する(fail-closed)。
            # 証跡が無ければS1(Azure 1回)、NGなら再生成(Store gate経由)、Azure障害は技術STOP(再利用も再生成もしない)。
            _kd = kp_vote.kp_vote_reuse_ok(
                cached_result, wav_path=wav_path, canonical_text=n3_tts.tts_safe_kp_en(expected_text or ""),
                allow_s1=bool(expected_text), label=f"kp{rank}_{role}")
            if _kd["action"] == kp_vote.ACTION_TECHNICAL_STOP:
                return kp_vote.technical_stop_entry(f"kp{rank}_{role}", _kd)
            if not _kd["ok"]:
                _r = generate_fn()
                if isinstance(_r, dict):
                    _r["kp_dual_reuse_gate_previous"] = {"reason": _kd["reason"], "action": _kd["action"]}
                return _r
        reused = dict(cached_result)
        reused["reused_from_previous_run"] = True
        if _kd is not None and _kd.get("kp_dual_check") is not None:
            reused["kp_dual_check"] = _kd["kp_dual_check"]
        _mark_asr_judgement_inherited(reused)
        return reused
    return generate_fn()


# FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W4、2026-09-29): Advanced
# (B1B)Key Phrase英語解説(explanation_en)のTTS生成。KEY-PHRASE-ADVANCED-
# ENGLISH-EXPLANATION-TRIAL-02/-AUDIO-STYLE-TRIAL-04(er041/er046)で検証
# 済みの呼び出しパターン(repro01.generate_narration_snippet_verified_
# strict、短いphrase専用のKEY_PHRASE_MINIMAL系ではなく通常の英語style
# 経路を使う。解説文はphraseより長い自然文のため、tts_safe_kp_enでは
# なくn3_tts.tts_safe_enで正規化する)をそのままProduction配線する。
# Family X runner専用の新関数として本ファイルに置く(共有資産
# er003_v1_n3_01_tts_generate.pyは無変更のまま維持する、
# er019_family_x_pointless_01_test_01.FamilyAUnchangedTestが同ファイルの
# working tree diff=0を機械的に強制しているため)。
KP_EXPLANATION_MAX_ATTEMPTS = 3   # 1ブロックの試行数。AUW 委任_05(OF-AUW-12): 旧2 -> 3。X/Y/Z scope内は ①②=解説Style → 180秒 → ③=Fallback(minimal・Secondary必須)、LRなし(TTS統一委任_02、_kp_explanation_unified)。scope外(A/B/C)は従来の同一Style3回


def generate_key_phrase_explanation_en_verified(explanation_text: str, out_path: str,
                                                 style_prefix_override: str,
                                                 tts_backend: str = "structured_separation") -> dict:
    # TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_02(2026-10-26): X/Y/Z scope内(単一flag読取関数 er127.unified_flow_active)のみ
    # 統一3回構成(①②=解説Style → 180秒 → ③=Fallback Style[minimal・Secondary必須]、LRなし)。scope外(A/B/C)は従来コードのまま。
    if er127.unified_flow_active():
        return _kp_explanation_unified(explanation_text, out_path, style_prefix_override, tts_backend)
    import er003_v1_repro01_main_generate as repro01
    text = n3_tts.tts_safe_en(explanation_text)
    return repro01.generate_narration_snippet_verified_strict(
        text, "en", out_path, text,
        # AUW 委任_05(OF-AUW-12、DESIGN_02_ADDENDUM_01 §9): scope外の同一Style3回構成(X/Y/Z scope内は上の_kp_explanation_unifiedで ①②→180秒→③Fallback)
        # (旧Trial値max_attempts=2の継承を3回へ。KP解説の回数変更はこの1点のみ。Prompt/閾値/他回数は不変)。
        max_extra_chars=max(20, len(text) // 2), max_attempts=KP_EXPLANATION_MAX_ATTEMPTS,
        safety_margin_seconds=repro01.KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS,
        style_prefix_override=style_prefix_override, disfluency_qa=True,
        asr_prompt=repro01.KEY_PHRASE_EN_ASR_NO_TRANSLATE_PROMPT,
        enable_non_latin_cascade=True, tts_backend=tts_backend)


@review_lock.guarded_generate("en")      # 2段呼出を外側guard1つで包む(L6と同方式: 内側guardがreentrancyでcheck/recordしない)
@er127.with_block("L5", fingerprint_params=("style_prefix_override", "tts_backend"))
def _kp_explanation_unified(explanation_text: str, out_path: str, style_prefix_override: str,
                            tts_backend: str = "structured_separation", *, _blk=None) -> dict:
    import er003_v1_repro01_main_generate as repro01
    text = n3_tts.tts_safe_en(explanation_text)
    common_kw = dict(
        max_extra_chars=max(20, len(text) // 2), safety_margin_seconds=repro01.KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS,
        disfluency_qa=True, asr_prompt=repro01.KEY_PHRASE_EN_ASR_NO_TRANSLATE_PROMPT, enable_non_latin_cascade=True,
        tts_backend=tts_backend, total_slots=KP_EXPLANATION_MAX_ATTEMPTS)
    primary = repro01.generate_narration_snippet_verified_strict(
        text, "en", out_path, text, max_attempts=KP_EXPLANATION_MAX_ATTEMPTS - 1, style_prefix_override=style_prefix_override,
        slot_offset=0, **common_kw, **er127.stage_kwargs(_blk, 0))
    if primary.get("status") == "OK":
        primary["fallback_used"] = False
        return primary
    if er127._is_tech_stop(er127.last_attempt_of(primary)):
        primary["fallback_used"] = False
        return primary                      # 技術STOP(Secondary不可等)は③・HRに進めない(従来どおり)
    fb = repro01.generate_narration_snippet_verified_strict(
        text, "en", out_path, text, max_attempts=1, style_prefix_override=repro01.MINIMAL_INSTRUCTION_PREFIX,
        slot_offset=KP_EXPLANATION_MAX_ATTEMPTS - 1, force_secondary=True, **common_kw,
        **er127.stage_kwargs(_blk, KP_EXPLANATION_MAX_ATTEMPTS - 1))      # ③の直前に180秒(blk.step(3))
    fb["fallback_used"] = True
    fb["fallback_attempts_log"] = primary.get("attempts_log")           # record_outcomeの実TTS計上(=3): L6と同じ会計
    fb["minimal_attempts_log"] = fb.get("attempts_log")
    if fb.get("status") != "OK" and not er127._is_tech_stop(er127.last_attempt_of(fb)):
        er127.register_terminal_hr(out_path=out_path, canonical_text=text, attempt=er127.last_attempt_of(fb), lock_text=text)
    return fb


# TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-02(修正3回目、
# 2026-09-28、Opus L2所見BL-2是正): shared_narration.ensure_all_shared_
# narration_b1/a2()の戻り値statusをこれまで呼び出し元(本ファイル)が
# 一切見ておらず、下位のvoice01.generate_charon_englishはASR実行前に
# write_wav_floatするため、3 attempt全滅(status!=OK)でも最後の不合格
# 音声(実例: num_two_charon.wav、asr_text="Ту"、TRUE_CONTENT_MISMATCH)
# がファイルとして残り、Audio Validation Gate(tts_generation_results.json
# のsegments/key_phrasesのみ走査)の対象外のままAssemblyへ素通りしていた
# (Opus L2所見BL-2、実データ2026-09-28 num_two_retry_evidence_flx2.json
# で顕在化を確認)。blast radiusをFamily X内に限定するため、assemble.py
# (共有Gate関数)自体は無変更のまま、本runner内でのみ検知・記録・STOPする。
class SharedNarrationBlockedError(RuntimeError):
    """共有narration(固定shell)segmentが1件でもstatus!=OKの場合に送出する。
    review_lock(audit/review_lock_state.json)・human_review_queue.jsonl
    (er006_secondary_asr_01経由)への記録は、既存のguarded_generate/
    secondary_asr.evaluate_attempt_with_cascade機構により、この例外を
    送出する前に既に完了している(本例外は追加の記録ではなく、後続処理
    [同一run内の他segment生成・Assembly stage]への進行を止めるための
    ゲートである)。"""


def _summarize_shared_narration(raw: dict) -> dict:
    return {
        name: {
            "status": r.get("status"),
            "reused": r.get("reused"),
            "master_audio_id": r.get("master_audio_id"),
            "asr_text": r.get("asr_text"),
            "attempts": len(r.get("attempts_log") or []),
        }
        for name, r in raw.items()
    }


def _assert_shared_narration_ok(shared_narration_status: dict, level: str) -> None:
    non_ok = {name: v["status"] for name, v in shared_narration_status.items() if v["status"] != "OK"}
    if non_ok:
        raise SharedNarrationBlockedError(
            f"[{level}] 共有narration(shell)segmentがSTOPPEDです: {non_ok} 。"
            "review_lock/human_review_queueへは既存機構経由で記録済み。"
            "audit/tts_generation_results.jsonのshared_narrationを確認し、"
            "Human Review完了(承認/REGENERATE_APPROVED)後に再実行してください。"
        )


def _shared_narration_gate_blocked_summary(out_dir: str) -> dict | None:
    """Assembly stage側の防御(defense-in-depth): TTS stageと同一プロセス
    内で完結せず`--stage assemble`が独立実行された場合でも、直前のtts
    stageで記録されたtts_generation_results.jsonのshared_narrationに
    非OKが残っていればAssemblyへ進ませない。ファイルが無い場合(旧run・
    未実行等)はNoneを返し、既存の他Gate(KP scaffold欠落等)に判断を
    委ねる(新たな前提を追加しない)。"""
    path = f"{out_dir}/audit/tts_generation_results.json"
    if not os.path.exists(path):
        return None
    data = load_json(path)
    shared = data.get("shared_narration") or {}
    non_ok = {name: v.get("status") for name, v in shared.items() if v.get("status") != "OK"}
    if not non_ok:
        return None
    return {
        "status": "BLOCKED_SHARED_NARRATION_NOT_OK",
        "reason": f"共有narration(shell)segmentがSTOPPEDのままです: {non_ok} 。"
                  "Human Review完了まではAssemblyを実行しません(Opus L2所見BL-2)。",
        "shared_narration_non_ok": non_ok,
    }


def _pnap_supply(original: str, shaped: str) -> str:
    """PNAP 委任_02(5-4): 固有名詞の発音供給(綴り置換)をtext整形点の直後に1回挟む。flag OFF・run scope外・KPでは恒等(shapedをそのまま返す)。
    共有`er003_v1_n3_01_tts_generate`は編集しない(27-7)。"""
    return pnap_supply.supply_for_tts(original, shaped, static_overrides=getattr(n3_tts, "_EN_NAME_PRONUNCIATION_OVERRIDES", None))


# ============================================================
# FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01(X Advanced本文=段落単位chunk TTS+0.2秒、APPROVED_FOR_PRODUCTION 2026-10-25、ユーザー正式決定B0.2)
# chunkは通常のsegment entry(segment_id=full_story_part{n}_k{j})。in_one_line・他segmentは従来どおり(分岐前に抜ける)。Standard(a2)本文もchunk化する(2026-10-26ユーザー正式承認): chunkごとに既存の6%減速を適用→0.2秒無音挿入(_generate_x_body_part_chunked_a2)。
# 親(full_story_part{n})は『生chunkを0.2秒無音で連結したwav』+親集約entry(statusはplanのchunk id一覧から導出、失敗時も常に書く)。
# ============================================================
def _x_chunk_plans(parts: dict) -> dict:
    """b1b本文3 partのchunk plan(決定論。段落が1つのpartは chunked=False=従来の1 call)。"""
    return chunk_tts.plan_x_parts(parts)


def _x_drop_chunked_parent_cache(cached: dict | None, plans: dict) -> dict | None:
    """chunk化しなくなったpart(段落が1つに変わった等)の前回chunk集約entryは再利用しない(従来経路の再利用判定に混ぜない)。"""
    if not cached:
        return cached
    segs = cached.get("segments") or {}
    drop = [pid for pid, p in plans.items() if not p.get("chunked") and (segs.get(pid) or {}).get("chunk_tts")]
    if not drop:
        return cached
    out = dict(cached)
    out["segments"] = {k: v for k, v in segs.items() if k not in drop}
    return out


def _x_chunk_parent_display(plan: dict, segments: dict) -> dict:
    """I7: 親集約entryの表示用項目(voice/model/style要約)。style_profile/style_prefixはchunk側が正(親へ複製しない=M1)。"""
    first = (segments.get(plan["chunks"][0]["chunk_id"]) or {}) if plan.get("chunks") else {}
    d = {k: first[k] for k in ("voice", "model", "tts_model_id", "tts_backend") if k in first}
    sp = first.get("style_prefix")
    d["style"] = {"instruction_label": "FULL_STORY(chunked, see chunk_tts)",
                  "style_prefix_sha256": sha256_text(sp) if isinstance(sp, str) else None}
    d["asr_verified"] = all((segments.get(c["chunk_id"]) or {}).get("asr_verified") is True for c in plan["chunks"])
    d["clip_kind"] = "narrator"
    return d


def _refresh_x_chunk_parents(out_dir: str, parts: dict, segments: dict, plans: dict, level: str = "b1b") -> dict:
    """M2(a)(b)(d): chunk化したpartの親集約entryを(再)構築して segments に書く(冪等)。generate末尾と、assembleの入口(style gateより前)で呼ぶ。
    level="a2"(Standard): 親wav=減速後chunk wavの生連結なので、全chunk減速済みのときだけ親にslowdown_applied=Trueを集約する(er117.std_parent_slowdown_fields)。"""
    ap = asm.human_approval_path(out_dir)
    approvals = load_json(ap) if os.path.exists(ap) else {}
    out = {}
    for pid, plan in plans.items():
        if not plan.get("chunked"):
            continue
        display = _x_chunk_parent_display(plan, segments)
        if level == chunk_tts.STD_LEVEL:
            display.update(chunk_tts.std_parent_slowdown_fields(plan, segments))
        out[pid] = chunk_tts.refresh_parent_status(
            plan, segments, approvals, asm._segment_gate_status, narration_dir=f"{out_dir}/narration",
            parent_text=parts["part" + pid[-1]], display=display)
    return out


def _generate_x_body_part_chunked(plan: dict, cached: dict | None, narration_dir: str, results: dict, role_style, style_profile: str,
                                  tts_backend: str) -> None:
    """chunkごとに従来の本文partと『同じ呼出』(news_tail_fix.generate_news_narration_wide_margin、同一Voice/Style/model/Gate/retry/fallback)。
    chunk失敗(status!=OK)後も後続chunkの生成を続ける(R1。OK chunkは再利用されるので再課金は無く、未生成entryを作らない)。直列(chunk順)。"""
    n = len(plan["chunks"])
    for c in plan["chunks"]:
        cid, ctext = c["chunk_id"], c["text"]
        with cl.segment_context(cid):
            results[cid] = _generate_or_reuse(
                cached, cid, f"{narration_dir}/{cid}.wav",
                lambda ctext=ctext, cid=cid: news_tail_fix.generate_news_narration_wide_margin(
                    _pnap_supply(ctext, n3_tts.tts_safe_news_en(ctext)), f"{narration_dir}/{cid}.wav",
                    disfluency_qa=False,
                    enable_connected_speech_equivalence_layer=retry_primitive.connected_speech_enabled_for(cid),
                    enable_repetition_qa=True, enable_pronunciation_resolver=True,
                    style_prefix_override=role_style("FULL_STORY"), tts_backend=tts_backend),
                expected_text=ctext)
        results[cid]["canonical_text"] = ctext
        chunk_tts.attach_chunk_meta(results[cid], plan["parent_id"], c, n)
        # M1: Style profileの記録は『chunkごと』(親は対象外。親へchunk1の値をコピーしない)
        if not validation_inheritance.is_untouched_entry(results[cid]):
            style_profile_mod.attach_segment_profile_record(results[cid], style_profile, "FULL_STORY", role_style("FULL_STORY"))


def _generate_x_body_part_chunked_a2(plan: dict, cached: dict | None, narration_dir: str, results: dict, role_style_slower, style_profile: str,
                                     tts_backend: str) -> None:
    """Standard(a2)本文part用(CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01、ユーザー正式承認2026-10-26)。chunkごとに、非chunkのStd本文partと『同じ呼出』
    (n3_tts.generate_a2_segment_with_slowdown = TTS→6%減速(atempo)→減速後ASR再検証、同一Voice/Style[減速instruction込み]/model/Gate/retry/fallback、
    通算TTS3回の予算もchunk単位)を適用する。減速はchunk wavに対してだけ掛かり、0.2秒の無音は連結時(減速後)に挿入する=ポーズは減速されない。
    chunk失敗(status!=OK)後も後続chunkの生成を続ける(R1)。直列(chunk順)。"""
    n = len(plan["chunks"])
    for c in plan["chunks"]:
        cid, ctext = c["chunk_id"], c["text"]
        tts_input = _pnap_supply(ctext, n3_tts.tts_safe_news_en(ctext))
        sub = n3_tts.first_words(ctext)
        with cl.segment_context(cid):
            results[cid] = _generate_or_reuse(
                cached, cid, f"{narration_dir}/{cid}.wav",
                lambda tts_input=tts_input, sub=sub, cid=cid: n3_tts.generate_a2_segment_with_slowdown(
                    tts_input, f"{narration_dir}/{cid}.wav", sub,
                    style_prefix_override=(role_style_slower("FULL_STORY") or n3_tts.A2_ENGLISH_STYLE_PREFIX_SLOWER),
                    disfluency_qa=False,
                    enable_connected_speech_equivalence_layer=retry_primitive.connected_speech_enabled_for(cid),
                    enable_repetition_qa=True, tts_backend=tts_backend),
                expected_text=ctext)
        results[cid]["canonical_text"] = ctext
        chunk_tts.attach_chunk_meta(results[cid], plan["parent_id"], c, n, level=chunk_tts.STD_LEVEL)
        if not validation_inheritance.is_untouched_entry(results[cid]):
            style_profile_mod.attach_segment_profile_record(results[cid], style_profile, "FULL_STORY", role_style_slower("FULL_STORY"))


def _x_std_chunk_slowdown_blocked(out_dir: str) -> dict | None:
    """Std(a2)組立前Gate: chunk化したpartの全chunkが『chunk単位で』6%減速済み(slowdown_applied)であること。
    共有Gate(asm.verify_episode_audio_validation_gate)はchunk idをA2_SLOWDOWN_TARGET_SEGMENTSに持たないため、ここで補う(回避ではなく追加)。
    人間承認(record_human_approval)でも減速欠落は迂回できない(承認は共有Gateのstatusにしか効かない)。"""
    rp, pp = f"{out_dir}/audit/tts_generation_results.json", f"{out_dir}/parts.json"
    if not (os.path.exists(rp) and os.path.exists(pp)):
        return None
    segs = load_json(rp).get("segments") or {}
    plans = _x_effective_chunk_plans(out_dir, load_json(pp))
    bad = []
    for pid, plan in plans.items():
        bad += chunk_tts.std_chunk_slowdown_violations(plan, segs)
    if not bad:
        return None
    return {"status": "BLOCKED_STD_CHUNK_SLOWDOWN_GATE", "blocked": bad,
            "reason": "Std本文chunkに6%減速(chunk単位)の証跡がありません。本runnerはこのGateを回避しません。"}


def _x_effective_chunk_plans(out_dir: str, parts: dict) -> dict:
    """gate/assemble用: 本方式導入前に生成された結果(親entryのみ・chunk entryなし)は従来経路のまま扱う(既存runの再組立を壊さない)。"""
    plans = _x_chunk_plans(parts)
    rp = f"{out_dir}/audit/tts_generation_results.json"
    segs = (load_json(rp).get("segments") or {}) if os.path.exists(rp) else {}
    return {pid: chunk_tts.effective_plan(p, segs) for pid, p in plans.items()}


@secondary_run_scope.with_secondary_run  # AUW 委任_05: run単位SecondaryCache+circuit breaker
@fx_iol.family_x_in_one_line_scope()  # FXPW 委任_04: LR gate 8_sentence_count_unchanged をFamily X TTS段のみで有効化
@pnap_hooks.family_scope("X", "b1b")  # PNAP 委任_02: 固有名詞アラーム方針のrun scope(X)+finallyの完成報告hook。flag OFFなら素通し
@er109_scope.family_scope("X")  # ASR-HOMOPHONE 委任_04: er109 run scope(X)。例外・STOP時もfinallyで復元
def generate_family_x_b1_segments(
        theme_out_dir: str,
        # TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-01(2026-09-27、
        # 既定"structured_separation"で既存挙動とbyte-identical): このrunnerが
        # 唯一、明示的に"speech_metadata_flash_lite"を渡せる呼び出し元
        # (Dangling Reference Check、設計書§(d))。主記事12segment
        # (topic_intro/preview/comment_1-4/full_story_part1-3[+heading]/
        # in_one_line)が対象。
        # FAMILY-X-02(2026-09-28、ユーザー確定仕様C): Key Phrase
        # (shared_narration経由のMaster Audio Store)も含め、Family X
        # ではFlash-Liteへ原則統一する。tts_backendを
        # `_generate_key_phrase_segments_b1`/`shared_narration.
        # ensure_all_shared_narration_b1`へそのまま転送する(Master
        # Audio Keyは`tts_model_id`を含むため、Flash-Lite分は既存
        # Structured Separation資産と衝突せず別キーで保存される、
        # 設計はer006_audio_cost_pilot_02_shared_narration.py参照)。
        tts_backend: str = "structured_separation",
        # FAMILY-X-COFFEE-P8-FINAL-AUDIO-AND-PRODUCTION-WIRING-01 委任_02
        # (OPEN-300): "default"は現行とバイト同一。"coffee_p8"はCoffee Full Story限定の
        # Style置換(runnerはresolve_run_profile経由の値だけを渡す)。
        style_profile: str = "default") -> dict:
    """既存Production低レベル関数(voice01.generate_charon_english/
    news_tail_fix.generate_news_narration_wide_margin)をそのまま呼ぶ。
    Comment/Preview=Charon英語、本文/In One Line=Aoede(News本文)、
    Key Phrase=既存Master Audio Store経由(shared_narration)。"""
    import er033_tts_flash_lite_family_x_styles_01 as fl_styles

    # M5: profile != defaultでlegacy backendなら課金前にSTOP(P8が黙って落ちるのを防ぐ)。
    style_profile_mod.assert_profile_backend(style_profile, tts_backend)

    def _base_role_style(role: str) -> str | None:
        # Family Xランナーのみがrole別style定数を参照する(Dangling
        # Reference Check、設計書§(d))。既定backendではNoneを返し、
        # 各下位関数のstyle_prefix_override=Noneと同じ(既存挙動)。
        if tts_backend != "speech_metadata_flash_lite":
            return None
        return fl_styles.FAMILY_X_ROLE_STYLE_EN.get(role)

    def _role_style(role: str) -> str | None:
        # 単一解決関数経由(defaultはbase_getter素通し=バイト同一)。
        return style_profile_mod.resolve_role_style(style_profile, role, "b1b", _base_role_style)

    out_dir = f"{theme_out_dir}/b1b"
    narration_dir = f"{out_dir}/narration"
    os.makedirs(narration_dir, exist_ok=True)

    parts = load_json(f"{out_dir}/parts.json")
    support = load_json(f"{out_dir}/b1_support_texts.json")
    kp_path = f"{out_dir}/key_phrases/keywords_canonicalized.json"
    # small_bag run_02(Stage 3c実行時)で発見: Key Phrase選定が構造Gate
    # (KEY_WORDS_STRUCTURE_INVALID等)でSTOPし、keywords_canonicalized.json
    # 自体が書かれないケースがある(既存Key Phrase Gateの正常動作、Gateを
    # 回避・再試行はしない)。そのままload_jsonすると未処理の
    # FileNotFoundErrorでtts stage全体がクラッシュし、full_story等の
    # 他segmentの結果すら得られなくなるため、無い場合はkp=Noneとして
    # Key Phrase生成のみ明示的にスキップし、他segmentは生成を継続する。
    kp = load_json(kp_path) if os.path.exists(kp_path) else None

    shared_narration_raw_b1 = ({} if _ONLY_SEGMENTS is not None else
                               shared_narration.ensure_all_shared_narration_b1(narration_dir, tts_backend=tts_backend))
    shared_narration_status = _summarize_shared_narration(shared_narration_raw_b1)
    _chunk_plans = _x_chunk_plans(parts)
    # 再計画禁止(resume): 同一本文・同一版で保存済みplanと分割が食い違えば課金前にSTOP。planは本文の純関数。
    chunk_tts.reconcile_saved_plan(f"{out_dir}/audit/chunk_plan_b1b.json", _chunk_plans)
    _unk = chunk_tts.unknown_chunk_ids_in_selection(_chunk_plans, _ONLY_SEGMENTS)   # Opus R3(c): planに無いchunk id指定は課金前に拒否
    if _unk:
        raise chunk_tts.ChunkIntegrityError(f"--only-segmentsにplanへ存在しないchunk idがあります(課金前に拒否): {_unk}")
    # I1: planner_versionが現行と異なる前回chunk entryは再利用しない(版を上げた後に旧chunkが再利用されて整合検査STOPになるのを防ぐ)
    _cached = _x_drop_chunked_parent_cache(chunk_tts.drop_stale_chunk_entries(_load_cached_tts_results(out_dir)), _chunk_plans)
    # Opus M1(2026-10-26): 親もそのchunk idも--only-segmentsに含まれず前回cacheが旧方式(親entryのみ)の本文は、従来経路(親名で検証済みentryを引継ぎ)に残す。
    # chunk化すると本文chunkが前回cacheに無くSKIPPEDになり、親が CHUNKS_NOT_ALL_VALIDATED で上書きされ検証済み本文が失われるため。本文を含む通常のresumeは従来どおりchunk化。
    _chunk_plans = chunk_tts.apply_legacy_partial_retry(_chunk_plans, _cached, _ONLY_SEGMENTS)

    results = {}
    topic_intro_text = f"Today's topic is {parts['title']}."
    with cl.segment_context("topic_intro"):
        results["topic_intro"] = _generate_or_reuse(
            _cached, "topic_intro", f"{narration_dir}/topic_intro.wav", lambda: voice01.generate_charon_english(
                _pnap_supply(topic_intro_text, n3_tts.tts_safe_number_words_en(n3_tts.tts_safe_en(topic_intro_text))),
                f"{narration_dir}/topic_intro.wav",
                enable_connected_speech_equivalence_layer=retry_primitive.connected_speech_enabled_for(
                    "topic_intro"),
                # PRONUNCIATION-RESOLUTION-PHASE-3-B1B-EN-WIRING-AND-JA-
                # VALIDATOR-PUNCT-01(OPEN-197是正): Family X runnerのみが
                # 明示的にTrueを渡す(Family A/B/C legacy呼び出し元は無変更)。
                enable_pronunciation_resolver=True,
                style_prefix_override=_role_style("TOPIC_INTRO"),
                tts_backend=tts_backend), expected_text=topic_intro_text)
    results["topic_intro"]["canonical_text"] = topic_intro_text

    for name in ("preview", "comment_1", "comment_2", "comment_3", "comment_4"):
        text = support[name]
        with cl.segment_context(name):
            results[name] = _generate_or_reuse(
                _cached, name, f"{narration_dir}/{name}.wav", lambda text=text, name=name: voice01.generate_charon_english(
                    _pnap_supply(text, n3_tts.tts_safe_number_words_en(n3_tts.tts_safe_en(text))), f"{narration_dir}/{name}.wav",
                    # TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-01: 既定
                    # backendでは_role_style()がNoneを返すため、既存のB1_PREVIEW_
                    # STYLE_PREFIX_CALMのまま(byte-identical)。flash-lite backend
                    # 選択時のみTrial実測済みの短いrole style("calm, conversational")
                    # を優先する。
                    style_prefix_override=(_role_style("PREVIEW" if name == "preview" else "COMMENT")
                                            or n3_tts.B1_PREVIEW_STYLE_PREFIX_CALM),
                    disfluency_qa=True,
                    enable_connected_speech_equivalence_layer=retry_primitive.connected_speech_enabled_for(name),
                    # PRONUNCIATION-RESOLUTION-PHASE-3-B1B-EN-WIRING-AND-JA-
                    # VALIDATOR-PUNCT-01(OPEN-197是正): Family X runnerのみ。
                    enable_pronunciation_resolver=True, tts_backend=tts_backend),
                expected_text=text)
        results[name]["canonical_text"] = text
        # 委任_03(OF-Y8): Adv Preview(E1)のM4記録。profileにPREVIEW overrideがあるときだけ付く
        # (default/他profileは何も書かない=バイト同一)。Comment 1〜4は対象外。
        if name == "preview" and not validation_inheritance.is_untouched_entry(results[name]):
            style_profile_mod.attach_segment_profile_record(
                results[name], style_profile, style_profile_mod.ROLE_PREVIEW, _role_style("PREVIEW"))

    # FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W1、2026-09-29): Heading
    # Readout撤去(旧Stage 3cのfull_story_part2_heading/full_story_part3_
    # headingサブsegment生成を削除)。新構造は本文が段落境界で決定論的に
    # part1/part2/part3へ3分割済み(見出し文が存在しない)ため、本文3
    # segmentすべてを同一loop・同一TTS呼び出し(news_tail_fix.generate_
    # news_narration_wide_margin、既存関数無変更)で生成する。
    for name, text in (
        ("full_story_part1", parts["part1"]), ("full_story_part2", parts["part2"]),
        ("full_story_part3", parts["part3"]), ("in_one_line", parts["in_one_line"]),
    ):
        if name in _BODY_SEGMENT_NAMES and _chunk_plans[name]["chunked"]:
            # 本文partが2段落以上: 段落単位chunkで生成(親集約entryはループ後に常に書く)。1段落のpartは下の従来経路(1 call)。
            _generate_x_body_part_chunked(_chunk_plans[name], _cached, narration_dir, results, _role_style, style_profile, tts_backend)
            continue
        with cl.segment_context(name):
            results[name] = _generate_or_reuse(
                _cached, name, f"{narration_dir}/{name}.wav",
                lambda text=text, name=name: news_tail_fix.generate_news_narration_wide_margin(
                    _pnap_supply(text, n3_tts.tts_safe_news_en(text)), f"{narration_dir}/{name}.wav",
                    disfluency_qa=(name == "in_one_line"),
                    enable_connected_speech_equivalence_layer=retry_primitive.connected_speech_enabled_for(name),
                    enable_repetition_qa=(name in _BODY_SEGMENT_NAMES),
                    # PRONUNCIATION-RESOLUTION-PHASE-3-B1B-EN-WIRING-AND-JA-
                    # VALIDATOR-PUNCT-01(OPEN-198是正): Family X runnerのみ。
                    # 技術的fallback(発話区間検出失敗時のみ)経路にのみ効く
                    # (標準ENGLISH_STYLE_PREFIX経路は無変更、§本Phase範囲外)。
                    enable_pronunciation_resolver=True,
                    style_prefix_override=_role_style("IN_ONE_LINE" if name == "in_one_line" else "FULL_STORY"),
                    tts_backend=tts_backend), expected_text=text)
        results[name]["canonical_text"] = text
        # M4/S3: 上書き対象roleのsegmentにだけ、hint追記前のStyle sha(style_base_sha256)を記録する。
        # 非対象(default/IN_ONE_LINE)は何も書かない(新keyなし)。
        _seg_role = "IN_ONE_LINE" if name == "in_one_line" else "FULL_STORY"
        if not validation_inheritance.is_untouched_entry(results[name]):
            style_profile_mod.attach_segment_profile_record(results[name], style_profile, _seg_role,
                                                             _role_style(_seg_role))

    # M2(a)(b)(d): chunk化したpartの親集約entry(失敗・未生成でも常に書く。statusはplanのchunk id一覧から導出)+親wav(生連結)
    _refresh_x_chunk_parents(out_dir, parts, results, _chunk_plans)

    if kp is not None:
        kp_results, kp_explanation_text_bundle = _generate_key_phrase_segments_b1(
            kp, narration_dir, _cached, tts_backend=tts_backend, style_profile=style_profile)
    else:
        kp_results, kp_explanation_text_bundle = {}, None
    kp_scaffold_status = "OK" if kp is not None else "KP_SCAFFOLD_JSON_MISSING(upstream key phrase Gateで未生成)"

    all_status = {k: v.get("status") for k, v in results.items()}
    # FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W4): Advanced(b1b)の中間
    # segmentが日本語意味(旧"japanese"role)から英語解説(新"explanation"
    # role)へ変わったため、run_summary_tts.jsonのkey_phrase_statusも
    # 追従する(a2側のkp_status["ja"]表記は無変更、別関数)。
    kp_status = {r: {"en": v["english"].get("status"), "explanation": v["explanation"].get("status")}
                 for r, v in kp_results.items()}
    if any(pl.get("chunked") for pl in _chunk_plans.values()):   # C7: chunk TTSのruntime evidence(分割位置・種別・attempts/fallback/LR/ASR判定)
        save_json(f"{out_dir}/audit/chunk_tts_evidence_b1b.json",
                  {"planner_version": chunk_tts.CHUNK_PLANNER_VERSION, "style_profile": style_profile, "tts_backend": tts_backend,
                   "parents": {pid: chunk_tts.evidence_record(pl, results) for pid, pl in _chunk_plans.items() if pl.get("chunked")}})
    review_lock.archive_prior_tts_results(f"{out_dir}/audit/tts_generation_results.json")
    save_json(f"{out_dir}/audit/tts_generation_results.json",
              {"segments": results, "key_phrases": kp_results, "shared_narration": shared_narration_status,
               "kp_scaffold_status": kp_scaffold_status, "tts_backend": tts_backend,
               # FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W4): run単位の
               # 英語解説text cache(_resolve_kp_explanations_textが次回
               # runで参照する)。
               "key_phrase_explanations_text": kp_explanation_text_bundle,
               # FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W3、Opus L2所見
               # MAJOR-3是正): 可変segment reuse判定用のcache version guard。
               "style_version": FAMILY_X_VARIABLE_ROLE_STYLE_VERSION,
               **({"only_segments": sorted(_ONLY_SEGMENTS)} if _ONLY_SEGMENTS is not None else {})})
    # AUW 委任_03: 生成完了hook。tts_generation_results.json確定直後に事後試聴リスト(PASS_WITH_WARNING)を再導出して
    # audit/pass_with_warning_listening_list.jsonへ出力する。失敗しても生成は失敗させない(warningログのみ、非ブロッキング)。
    pww_registry.write_listening_list_safe(out_dir)
    save_json(f"{out_dir}/run_summary_tts.json",
              {"segment_status": all_status, "key_phrase_status": kp_status,
               "shared_narration_status": {k: v["status"] for k, v in shared_narration_status.items()},
               "kp_scaffold_status": kp_scaffold_status, "tts_backend": tts_backend})
    # Opus L2所見BL-2: 監査記録の保存後にSTOPする(記録自体は必ず残す)。
    _assert_shared_narration_ok(shared_narration_status, "b1b")
    return {"segment_status": all_status, "key_phrase_status": kp_status,
            "shared_narration_status": {k: v["status"] for k, v in shared_narration_status.items()},
            "kp_scaffold_status": kp_scaffold_status, "tts_backend": tts_backend}


def _resolve_kp_explanations_text(kp_items: list, cached: dict | None) -> dict:
    """FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W4): Advanced(b1b)Key
    Phrase英語解説(explanation_en)のtext生成/reuse。5件まとめて1 callで
    生成する(er019_family_x_kp_explanation_01)ため、rank単位のcache
    (_generate_or_reuse_kp、音声segment用)とは別に、run単位のtext cache
    (cached["key_phrase_explanations_text"])を見る。canonical phrase
    (display_phrase)の並びが前回runと完全一致する場合のみreuseし、1件
    でも変化していれば5件まとめて再生成する(部分reuseはしない、5件
    バッチ生成という性質上)。"""
    # KPFT 委任_02(OF-KPFT-P-03): 全文選定itemの解説は音声・試聴ページと同じ形(used_form)に対して生成する。旧artifact/A/B/Cはdisplay_phrase。
    signature = [kp_explanation_gen.explanation_phrase(it) for it in kp_items]
    # OF-KGCPW-06: glossは解説LLMの入力。gloss_alignment_status付きitemが1件でもあれば、gloss_signature
    # (display_phrase/key_phrase/glossの並び)の一致を必須にする(欠落も不一致=再生成)。status無しartifact
    # (ON化前/対象0件)は従来署名で互換。
    gloss_signature = [[kp_explanation_gen.explanation_phrase(it), it.get("key_phrase"), it.get("japanese_gloss", "")] for it in kp_items]
    _has_status = any(it.get("gloss_alignment_status") for it in kp_items)
    cached_bundle = (cached or {}).get("key_phrase_explanations_text")
    if (cached_bundle and cached_bundle.get("phrases_signature") == signature
            and (not _has_status or cached_bundle.get("gloss_signature") == gloss_signature)):
        reused = dict(cached_bundle)
        reused["reused_from_previous_run"] = True
        return reused
    input_items = [{"rank": it["rank"], "display_phrase": kp_explanation_gen.explanation_phrase(it),
                    "source_sentence": it.get("source_sentence", ""),
                    "japanese_gloss": it.get("japanese_gloss", "")} for it in kp_items]
    result = kp_explanation_gen.generate_kp_explanations(input_items)
    result["phrases_signature"] = signature
    result["gloss_signature"] = gloss_signature
    result["reused_from_previous_run"] = False
    return result


def _kp_english_generate_fn(style_profile: str, level: str, tts_backend: str, used_form: str, wav_path: str):
    """KP英語音声の生成closureと適用Style(K2またはNone)を返す。
    委任_02A(Opus条件A R-01): profileにKP_EN overrideがある(fx_20261016)ときだけ、承認済みK2をMaster Audio Storeの
    2段key(kp_en_k2_store.ensure_key_phrase_english_component_styled)経由で生成する。default・旧profileは従来の
    ensure_key_phrase_english_component(旧key・MINIMAL style)のまま=バイト同一。
    戻り値: (generate_fn, k2_style_text_or_None)。"""
    k2 = style_profile_mod.resolve_role_style(style_profile, style_profile_mod.ROLE_KP_EN, level, lambda _r: None)
    safe = n3_tts.tts_safe_kp_en(used_form)
    if k2 is None:
        # KP3V(P-04): 共有関数(Family A/B/Cと共有・不変)ではなくX専用関数から、同一構造のMasterAudioKey(+vote1)で
        # `vote_pass_required=True`の生成を呼ぶ(KP_THREE_ASR_VOTE_ENABLED=Falseなら共有関数へ委譲=旧挙動とバイト同一)。
        return (lambda: kp_vote.ensure_key_phrase_english_component_x_vote(
            safe, wav_path, tts_backend=tts_backend)), None
    return (lambda: kp_en_k2_store.ensure_key_phrase_english_component_styled(
        safe, wav_path, style_text=k2, style_id=style_profile_mod.KP_EN_STORE_STYLE_ID, style_tag="k2",
        tts_backend=tts_backend)), k2


def _generate_key_phrase_segments_b1(kp: dict, narration_dir: str, cached: dict | None = None,
                                      tts_backend: str = "structured_separation",
                                      style_profile: str = "default") -> dict:
    # FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W4、2026-09-29ユーザー
    # 正式決定): Advanced(B1B)Key Phraseの中間segmentを、日本語意味
    # (旧"japanese"role)から英語解説(新"explanation"role、Variant B
    # style)へ変更する。末尾の英語Phraseは新規segmentを生成せず、常に
    # 先頭("english"role、en_r)と同一wav path/同一cache entry/同一
    # Master Audio Storeキーを参照する(下記"phrase_repeat"、reuseで
    # 追加TTS call 0)。Standard(a2)側は本変更の対象外(無変更、別関数
    # `_generate_key_phrase_segments_a2`)。
    import er033_tts_flash_lite_family_x_styles_01 as fl_styles

    # W5(Opus L2所見MAJOR-3是正): KP解説styleも_role_style()と同じbackend
    # ゲートに揃える(既定backendではNone=下位関数の既定style、
    # speech_metadata_flash_lite選択時のみVariant Bを適用)。従来は
    # backendに関わらず無条件でVariant Bを渡しており、legacy backend
    # (未検証の組み合わせ)にもVariant Bが適用されてしまっていた。
    def _base_kp_explanation_style(_role: str) -> str | None:
        if tts_backend != "speech_metadata_flash_lite":
            return None
        return fl_styles.KEY_PHRASE_EXPLANATION_EN

    def _kp_explanation_style() -> str | None:
        # FAMILY-X-COFFEE-FINAL-V5-PRODUCTION-WIRING-01: 単一解決関数経由(defaultはbase素通し=バイト同一、
        # coffee_final_v5のAdv KP英英解説のみP3)。
        return style_profile_mod.resolve_role_style(
            style_profile, style_profile_mod.ROLE_KP_EXPLANATION_EN, "b1b", _base_kp_explanation_style)

    kp_items = sorted(kp["items"], key=lambda it: it["rank"])
    # 委任_02(関所): gloss再整合がHuman Review待ちのlevelは、解説LLM(glossが入力)もTTSも実行しない(0 API call)。
    _gloss_hr = _gloss_alignment_hr_unresolved(kp)
    if _gloss_hr:
        print(f"[FAMILY-X-AUDIO][STOP] KP gloss Human Review待ち(rank={[x.get('rank') for x in _gloss_hr]}): "
              "B1解説LLM/KP TTSを実行しません(0 API call)。")
        return _gloss_alignment_stopped_kp_results(kp_items, _gloss_hr, ("english", "explanation", "phrase_repeat")), None
    explanation_bundle = _resolve_kp_explanations_text(kp_items, cached)
    explanation_by_rank = explanation_bundle["items"]

    kp_results = {}
    for item in kp_items:
        rank = item["rank"]
        used_form = item["used_form"]
        # 委任_02A: fx_20261016ではK2(2段key)、それ以外は従来経路(バイト同一)。
        _kp_en_fn, _kp_en_k2 = _kp_english_generate_fn(
            style_profile, "b1b", tts_backend, used_form, f"{narration_dir}/kp{rank}_en.wav")
        with cl.segment_context(f"kp{rank}_english"):
            en_r = _generate_or_reuse_kp(
                cached, rank, "english", f"{narration_dir}/kp{rank}_en.wav",
                _kp_en_fn,
                # W5(Opus L2所見MAJOR-1、english role text guard): used_form
                # が変わった場合に古い音声を誤ってreuseしないようにする。
                expected_text=used_form)
        en_r["canonical_text"] = used_form
        # M4/S3: KP_EN overrideがあるprofileのときだけ、hint追記前のStyle sha(K2)を記録する(default/旧profileは新keyなし)。
        if not validation_inheritance.is_untouched_entry(en_r):
            style_profile_mod.attach_segment_profile_record(en_r, style_profile, style_profile_mod.ROLE_KP_EN, _kp_en_k2)

        explanation_row = explanation_by_rank.get(rank) or explanation_by_rank.get(str(rank)) or {}
        explanation_text = explanation_row.get("english_explanation") or ""
        text_gate_status = explanation_row.get("status")
        # W5(Opus L2所見BLOCKER-1是正、2026-09-29): text-gate status が
        # "OK"以外(NG/NG_PHRASE_MISMATCH/parse失敗によるstatus欠落等)の
        # rankはTTSを一切呼ばず、fail-closedでSTOPPEDにする。空文字/未検証
        # の英語解説文をTTSへ渡す経路を排除する(既存
        # verify_episode_audio_validation_gateがkp{rank}_explanation=
        # STOPPEDでassemblyをblockし、既存record_human_approval()経路で
        # 人間承認できる)。
        if text_gate_status != "OK":
            with cl.segment_context(f"kp{rank}_explanation_en"):
                expl_r = {
                    "status": "STOPPED",
                    "reason": (
                        f"text-gate status={text_gate_status!r}のためTTSを実行せず"
                        "STOPしました(BLOCKER-1是正、Human Review承認[record_"
                        "human_approval()]後に再実行するか、Key Phrase解説textの"
                        "再生成が必要です)。"
                    ),
                    "new_fact_tokens": (explanation_row.get("qa") or {}).get("new_fact_tokens"),
                }
        else:
            with cl.segment_context(f"kp{rank}_explanation_en"):
                expl_r = _generate_or_reuse_kp(
                    cached, rank, "explanation", f"{narration_dir}/kp{rank}_explanation_en.wav",
                    lambda explanation_text=explanation_text,
                    rank=rank: generate_key_phrase_explanation_en_verified(
                        explanation_text, f"{narration_dir}/kp{rank}_explanation_en.wav",
                        style_prefix_override=_kp_explanation_style(), tts_backend=tts_backend),
                    # W5(Opus L2所見MAJOR-1是正): text一致+style_version一致の
                    # 両方をreuse条件にする(可変segmentの_generate_or_reuseと
                    # 同一方針)。
                    expected_text=explanation_text, require_style_version=True)
        expl_r["explanation_text"] = explanation_text
        expl_r["canonical_text"] = explanation_text
        # M4/S3: profile対象(coffee_final_v5のP3)のときだけ、hint追記前のStyle shaを記録する(defaultは新keyなし)。
        if not validation_inheritance.is_untouched_entry(expl_r):
            style_profile_mod.attach_segment_profile_record(
                expl_r, style_profile, style_profile_mod.ROLE_KP_EXPLANATION_EN, _kp_explanation_style())
        expl_r["explanation_qa"] = explanation_row.get("qa")
        expl_r["explanation_status_from_text_gate"] = text_gate_status
        expl_r["display_gloss"] = item["japanese_gloss"]

        # 末尾の英語Phrase再掲: 新規generateはせず、en_rをそのまま複製
        # する(同一wav path/同一sha256/同一canonical_text/同一status)。
        # Audio Validation Gate(er003_v1_n3_01_assemble.py、無変更)は
        # sub_entry単位でstatus/pathを走査するため、この複製entryも
        # 既存Gateとそのまま整合する。
        phrase_repeat_r = dict(en_r)
        phrase_repeat_r["phrase_repeat_source"] = "same_as_first"
        kp_results[rank] = {"english": en_r, "explanation": expl_r, "phrase_repeat": phrase_repeat_r}
    return kp_results, explanation_bundle


@secondary_run_scope.with_secondary_run  # AUW 委任_05: run単位SecondaryCache+circuit breaker
@fx_iol.family_x_in_one_line_scope()  # FXPW 委任_04: LR gate 8_sentence_count_unchanged をFamily X TTS段のみで有効化
@pnap_hooks.family_scope("X", "a2")  # PNAP 委任_02: 固有名詞アラーム方針のrun scope(X)+finallyの完成報告hook。flag OFFなら素通し
@er109_scope.family_scope("X")  # ASR-HOMOPHONE 委任_04: er109 run scope(X)。例外・STOP時もfinallyで復元
def generate_family_x_a2_segments(
        theme_out_dir: str, japanese_title: str,
        # TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-01/02
        # (既定"structured_separation"で既存挙動とbyte-identical)。
        # FAMILY-X-02(2026-09-28、ユーザー確定仕様B-2、Fable決定訂正):
        # role別6-role styleはStandard(A2)/Advanced(B1B)両方の基本仕様。
        # A2固有の速度調整(A2_SLOWER_PACE_INSTRUCTION+6%減速post-process)
        # は_role_style_slower()で6-role styleと連結する(下記関数内
        # 参照)、既存の承認済み速度仕様は失わせない。Key Phraseは
        # tts_backend引数をそのまま`_generate_key_phrase_segments_a2`へ
        # 転送する(FAMILY-X-02 C: Key Phrase含めFlash-Lite統一)。
        tts_backend: str = "structured_separation",
        # OPEN-300: B1と同じ(既定"default"=バイト同一)。Std例外はS1参照
        # (COFFEE-P8-STD-VERBATIM-EXCEPTION-01、er019_family_x_style_profile_01.py)。
        style_profile: str = "default") -> dict:
    """既存Production低レベル関数(crosslevel_common.generate_english_
    segment_with_fallback経由のn3_tts.generate_a2_segment_with_slowdown、
    n3_tts.generate_a2_japanese_with_reading_safety)をそのまま呼ぶ。

    TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-02(2026-09-28、
    ユーザー確定仕様B-2、Fable決定訂正): 「A2(Standard)はrole別style
    非対応のまま」というFAMILY-X-01 Phase 1-3の設計判断を撤回する。
    6-role styleはStandard/Advanced両方へ適用する基本仕様であり、
    Standard固有の速度調整仕様(既承認`n3_tts.A2_SLOWER_PACE_INSTRUCTION`
    + 6% time-stretch post-process)は失わせない。flash-lite backend
    選択時のみ、speech_metadata.styleへ「6-role短い descriptor」+
    「既承認の減速instruction(逐語)」を連結した文字列を渡す
    (post-process自体は`generate_a2_segment_with_slowdown`内で無変更)。
    TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01(Phase B、2026-09-28):
    上記docstringの「JA segment(japanese_title/preview/comment_1-4)は
    style_prefix_override自体を持たないため無変更」を更新する。
    `generate_a2_japanese_with_reading_safety`/`with_fallback`へ
    `style_prefix_override`引数を追加し、preview/comment_1-4のみ
    `_role_style_ja()`(下記)経由でJ3(TTS-VARIABLE-SPOKEN-ROLE-STYLE-
    TRIAL-02実測・ユーザー承認)を渡す。japanese_titleはTrial-02の
    JA_SEGMENTS対象外のため当時は無変更(既存JAPANESE_STYLE_PREFIX/
    minimal instructionテキストをそのまま流用)としていた。

    FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W3、2026-09-29、Opus L2
    所見MAJOR-1是正・ユーザー正式決定): 上記の判断を撤回する。japanese_
    titleもpreview/comment_1-4と同一の`_role_style_ja()`(同一関数・同一
    backendゲート)を渡すよう統一した。理由: 同一A2記事内でjapanese_
    title(旧仕様のまま=長文JAPANESE_STYLE_PREFIX)とpreview/comment
    (J3)のstyleが混在し、誰も通しで試聴していなかった(Opus L2所見
    MAJOR-1)。既定backendでは`_role_style_ja()`はNoneを返すため、
    既存挙動(JAPANESE_STYLE_PREFIXのまま)に影響はない。"""
    import er033_tts_flash_lite_family_x_styles_01 as fl_styles

    # M5: profile != defaultでlegacy backendなら課金前にSTOP。
    style_profile_mod.assert_profile_backend(style_profile, tts_backend)

    def _base_role_style(role: str) -> str | None:
        if tts_backend != "speech_metadata_flash_lite":
            return None
        return fl_styles.FAMILY_X_ROLE_STYLE_EN.get(role)

    def _role_style(role: str) -> str | None:
        # 単一解決関数経由(defaultはbase_getter素通し=バイト同一)。
        return style_profile_mod.resolve_role_style(style_profile, role, "a2", _base_role_style)

    def _base_role_style_slower(role: str) -> str | None:
        # Standard固有: 6-role短styleと既承認の減速instruction(逐語、
        # ER-008-A2-TIMESTRETCH-ABC-10でユーザーが試聴・承認した文言)を
        # 連結する。base(6-role)がNone(既定backend)の場合はNoneのまま
        # (既存呼び出し元の挙動を一切変えない)。
        base = _base_role_style(role)
        if base is None:
            return None
        # N-7是正(修正3回目、2026-09-28、Opus L2所見): legacy
        # A2_ENGLISH_STYLE_PREFIX_SLOWERはer003_v1_n3_01_tts_generate.py:80
        # でモジュール読み込み時にassert_no_wpm_specification()検査済みだが、
        # この合成文字列(6-role短style+減速instruction)は検査されておらず
        # ガードが非対称だった(現行値にWPM数値記述は無く実害なし)。
        combined = f"{base}\n{n3_tts.A2_SLOWER_PACE_INSTRUCTION.strip()}"
        import er002_common as common
        common.assert_no_wpm_specification(combined)
        return combined

    def _role_style_slower(role: str) -> str | None:
        # S1(COFFEE-P8-STD-VERBATIM-EXCEPTION-01): coffee_p8のFULL_STORYはP8逐語
        # (A2_SLOWER_PACE_INSTRUCTIONを連結しない)+生成後6%減速。defaultは従来の連結のまま。
        return style_profile_mod.resolve_role_style(style_profile, role, "a2", _base_role_style_slower)

    # TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01(Phase B、2026-09-28):
    # ユーザー正式決定(J3、APPROVED_FOR_PRODUCTION、TTS-VARIABLE-SPOKEN-
    # ROLE-STYLE-TRIAL-02)。EN側_role_style()と同じbackendゲート
    # (speech_metadata_flash_lite明示時のみ)。既定backendではNoneを返し、
    # generate_a2_japanese_with_reading_safetyのstyle_prefix_override既定
    # None(=JAPANESE_STYLE_PREFIXのまま)と同じ挙動(他Family無影響)。
    # Family Xランナーのみが参照する(Dangling Reference Check、EN側と対称)。
    # 適用範囲はStandard(A2)のpreview/comment_1〜4のみ(japanese_title/Key
    # Phraseは対象外、Trial-02のJA_SEGMENTS_REQUIRED/OPTIONALに合わせる)。
    def _role_style_ja() -> str | None:
        if tts_backend != "speech_metadata_flash_lite":
            return None
        return fl_styles.FAMILY_X_ROLE_STYLE_JA

    def _role_style_ja_support() -> str | None:
        # FAMILY-X-COFFEE-FINAL-V5-PRODUCTION-WIRING-01: Std preview/comment_1〜4のみ(japanese_title・
        # Key Phrase日本語意味は対象外)。defaultはbase(_role_style_ja)素通し=バイト同一。
        # coffee_final_v5のみR2(日本語Aoede、ユーザー承認済み)。
        return style_profile_mod.resolve_role_style(
            style_profile, style_profile_mod.ROLE_SUPPORT_JA, "a2", lambda _r: _role_style_ja())

    out_dir = f"{theme_out_dir}/a2"
    narration_dir = f"{out_dir}/narration"
    os.makedirs(narration_dir, exist_ok=True)

    parts = load_json(f"{out_dir}/parts.json")
    support = load_json(f"{out_dir}/a2_support_texts.json")
    _bad_support = [k for k in ("preview", "comment_1", "comment_2", "comment_3", "comment_4")
                    if not isinstance(support.get(k), str) or not support[k].strip()]
    if os.path.exists(f"{out_dir}/{SUPPORT_STAGE_FAILED_MARKER}"):
        raise RuntimeError(f"[STOP] A2 support stageが失敗markerを残しています({out_dir}/{SUPPORT_STAGE_FAILED_MARKER})。有料TTSの前に停止しました。"
                           "`--stage scaffold`(初回)または`--regenerate-support comment_3`で作り直してください。")
    if _bad_support:   # Opus M-2(d): 有料TTSの前に、null/空のsupport文面を止める(b1bは対象外=記録のみ)
        raise RuntimeError(f"[STOP] A2 supportの文面が空/欠落です({_bad_support})。有料TTSの前に停止しました。"
                           "`--stage scaffold`(初回)または`--regenerate-support comment_3`で文面を作り直してください。")
    kp_path = f"{out_dir}/key_phrases/keywords_canonicalized.json"
    # generate_family_x_b1_segments()と同じ理由(Key Phrase構造Gate STOP時に
    # keywords_canonicalized.jsonが存在しないケースへの防御、Gate自体は
    # 回避しない)。
    kp = load_json(kp_path) if os.path.exists(kp_path) else None

    shared_narration_raw_a2 = ({} if _ONLY_SEGMENTS is not None else
                               shared_narration.ensure_all_shared_narration_a2(narration_dir, tts_backend=tts_backend))
    shared_narration_status = _summarize_shared_narration(shared_narration_raw_a2)
    # CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01(ユーザー正式承認2026-10-26): Std本文partもX Advと同じ段落境界planで分割し(段落2未満は従来の1 call)、
    # chunkごとに既存の6%減速処理を適用→0.2秒無音を挿入して連結する。再計画禁止(resume)・stale版/減速証跡なしcacheの再利用拒否もAdvと同じ。
    _chunk_plans = _x_chunk_plans(parts)
    chunk_tts.reconcile_saved_plan(f"{out_dir}/audit/chunk_plan_a2.json", _chunk_plans)
    _unk = chunk_tts.unknown_chunk_ids_in_selection(_chunk_plans, _ONLY_SEGMENTS)   # Opus R3(c): planに無いchunk id指定は課金前に拒否
    if _unk:
        raise chunk_tts.ChunkIntegrityError(f"--only-segmentsにplanへ存在しないchunk idがあります(課金前に拒否): {_unk}")
    _cached = chunk_tts.drop_cached_std_chunks_without_slowdown(
        _x_drop_chunked_parent_cache(chunk_tts.drop_stale_chunk_entries(_load_cached_tts_results(out_dir)), _chunk_plans))
    # Opus M1(2026-10-26): b1b(Adv)側と同じ。旧方式Std結果への『本文以外』の部分指定retryで検証済み本文を失わない(従来経路で引継ぎ)。
    _chunk_plans = chunk_tts.apply_legacy_partial_retry(_chunk_plans, _cached, _ONLY_SEGMENTS)

    results = {}
    topic_intro_tts_title = parts.get("title_tts", parts["title"])
    topic_intro_text = f"Today's topic is {parts['title']}."
    topic_intro_tts_text = f"Today's topic is {topic_intro_tts_title}."
    with cl.segment_context("topic_intro"):
        results["topic_intro"] = _generate_or_reuse(
            _cached, "topic_intro", f"{narration_dir}/topic_intro.wav",
            lambda: crosslevel_common.generate_english_segment_with_fallback(
                _pnap_supply(topic_intro_tts_text, n3_tts.tts_safe_number_words_en(n3_tts.tts_safe_en(topic_intro_tts_text))),
                f"{narration_dir}/topic_intro.wav", n3_tts.first_words(parts["title"], 3), max_extra_chars=30,
                style_prefix_override=_role_style("TOPIC_INTRO"),
                enable_connected_speech_equivalence_layer=retry_primitive.connected_speech_enabled_for(
                    "topic_intro"), tts_backend=tts_backend), expected_text=topic_intro_text)
    results["topic_intro"]["canonical_text"] = topic_intro_text

    with cl.segment_context("japanese_title"):
        results["japanese_title"] = _generate_or_reuse(
            _cached, "japanese_title", f"{narration_dir}/japanese_title.wav",
            lambda: n3_tts.generate_a2_japanese_with_reading_safety(
                japanese_title, f"{narration_dir}/japanese_title.wav",
                n3_tts.expected_substring_ja(japanese_title), max_extra_chars=30,
                # FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W3、Opus L2所見
                # MAJOR-1是正、ユーザー正式決定): japanese_titleもpreview/
                # comment_1-4と同一のJ3(_role_style_ja())へ統一する
                # (同一関数・同一backendゲート。既定backendではNoneのまま
                # =従来JAPANESE_STYLE_PREFIX、既存挙動に影響なし)。従来は
                # japanese_titleだけJ3対象外のまま残り、Flash-Lite backend
                # 選択時に同一A2記事内でstyleが混在していた。
                style_prefix_override=_role_style_ja(),
                tts_backend=tts_backend), expected_text=japanese_title)

    for name in ("preview", "comment_1", "comment_2", "comment_3", "comment_4"):
        text = support[name]
        with cl.segment_context(name):
            results[name] = _generate_or_reuse(
                _cached, name, f"{narration_dir}/{name}.wav",
                lambda text=text: n3_tts.generate_a2_japanese_with_reading_safety(
                    text, f"{narration_dir}/{name}.wav", n3_tts.expected_substring_ja(text),
                    style_prefix_override=_role_style_ja_support(),
                    tts_backend=tts_backend), expected_text=text)
        # M4/S3: profile対象(coffee_final_v5のR2)のときだけ記録(defaultは新keyなし)。
        if not validation_inheritance.is_untouched_entry(results[name]):
            style_profile_mod.attach_segment_profile_record(
                results[name], style_profile, style_profile_mod.ROLE_SUPPORT_JA, _role_style_ja_support())

    # FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W1、2026-09-29): Heading
    # Readout撤去(旧Stage 3cのfull_story_part2_heading/full_story_part3_
    # headingサブsegment生成を削除)。新構造は本文が段落境界で決定論的に
    # part1/part2/part3へ3分割済みのため、本文3segmentすべてを同一loop・
    # 同一TTS呼び出し(n3_tts.generate_a2_segment_with_slowdown、既存関数
    # 無変更・6%減速)で生成する。
    for name, text in (
        ("full_story_part1", parts["part1"]), ("full_story_part2", parts["part2"]),
        ("full_story_part3", parts["part3"]), ("in_one_line", parts["in_one_line"]),
    ):
        if name in _BODY_SEGMENT_NAMES and _chunk_plans[name]["chunked"]:
            # 本文partが2段落以上: 段落単位chunk+chunkごとの6%減速(親集約entryはループ後に常に書く)。1段落のpartは下の従来経路(1 call)。
            _generate_x_body_part_chunked_a2(_chunk_plans[name], _cached, narration_dir, results, _role_style_slower, style_profile, tts_backend)
            continue
        tts_input = _pnap_supply(text, n3_tts.tts_safe_news_en(text))
        sub = n3_tts.first_words(text)
        with cl.segment_context(name):
            results[name] = _generate_or_reuse(
                _cached, name, f"{narration_dir}/{name}.wav",
                lambda tts_input=tts_input, sub=sub, name=name: n3_tts.generate_a2_segment_with_slowdown(
                    tts_input, f"{narration_dir}/{name}.wav", sub,
                    style_prefix_override=(_role_style_slower("IN_ONE_LINE" if name == "in_one_line" else "FULL_STORY")
                                            or n3_tts.A2_ENGLISH_STYLE_PREFIX_SLOWER),
                    disfluency_qa=(name == "in_one_line"),
                    enable_connected_speech_equivalence_layer=retry_primitive.connected_speech_enabled_for(name),
                    enable_repetition_qa=(name in _BODY_SEGMENT_NAMES), tts_backend=tts_backend), expected_text=text)
        results[name]["canonical_text"] = text
        # M4/S3: 上書き対象roleのsegmentにだけ記録(非対象は新keyを書かない)。
        _seg_role = "IN_ONE_LINE" if name == "in_one_line" else "FULL_STORY"
        if not validation_inheritance.is_untouched_entry(results[name]):
            style_profile_mod.attach_segment_profile_record(results[name], style_profile, _seg_role,
                                                             _role_style_slower(_seg_role))

    # M2(a)(b)(d): chunk化したpartの親集約entry(失敗・未生成でも常に書く)+親wav(減速後chunkの生連結+0.2秒)+減速集約
    _refresh_x_chunk_parents(out_dir, parts, results, _chunk_plans, level="a2")

    kp_results = _generate_key_phrase_segments_a2(kp, narration_dir, _cached,
                                                   tts_backend=tts_backend,
                                                   style_profile=style_profile) if kp is not None else {}
    kp_scaffold_status = "OK" if kp is not None else "KP_SCAFFOLD_JSON_MISSING(upstream key phrase Gateで未生成)"

    all_status = {k: v.get("status") for k, v in results.items()}
    kp_status = {r: {"en": v["english"].get("status"), "ja": v["japanese_meaning"].get("status")}
                 for r, v in kp_results.items()}
    if any(pl.get("chunked") for pl in _chunk_plans.values()):   # C7: Std chunk TTSのruntime evidence(分割位置・種別・chunk別減速・attempts/fallback/LR/ASR判定)
        save_json(f"{out_dir}/audit/chunk_tts_evidence_a2.json",
                  {"planner_version": chunk_tts.CHUNK_PLANNER_VERSION, "level": "a2", "composition": chunk_tts.STD_SLOWDOWN_COMPOSITION,
                   "style_profile": style_profile, "tts_backend": tts_backend,
                   "parents": {pid: chunk_tts.evidence_record(pl, results) for pid, pl in _chunk_plans.items() if pl.get("chunked")}})
    review_lock.archive_prior_tts_results(f"{out_dir}/audit/tts_generation_results.json")
    save_json(f"{out_dir}/audit/tts_generation_results.json",
              {"segments": results, "key_phrases": kp_results, "shared_narration": shared_narration_status,
               "kp_scaffold_status": kp_scaffold_status, "tts_backend": tts_backend,
               # FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W3、Opus L2所見
               # MAJOR-3是正): 可変segment reuse判定用のcache version guard。
               "style_version": FAMILY_X_VARIABLE_ROLE_STYLE_VERSION,
               **({"only_segments": sorted(_ONLY_SEGMENTS)} if _ONLY_SEGMENTS is not None else {})})
    # AUW 委任_03: 生成完了hook。tts_generation_results.json確定直後に事後試聴リスト(PASS_WITH_WARNING)を再導出して
    # audit/pass_with_warning_listening_list.jsonへ出力する。失敗しても生成は失敗させない(warningログのみ、非ブロッキング)。
    pww_registry.write_listening_list_safe(out_dir, completion_label="Family X a2(Standard)")   # JA-ASR-V2-BETA 委任_02A: a2(日本語音声あり)は最終制作報告ブロックも標準出力へ(例外を投げない・非ブロッキング)
    save_json(f"{out_dir}/run_summary_tts.json",
              {"segment_status": all_status, "key_phrase_status": kp_status,
               "shared_narration_status": {k: v["status"] for k, v in shared_narration_status.items()},
               "kp_scaffold_status": kp_scaffold_status, "tts_backend": tts_backend})
    # Opus L2所見BL-2: 監査記録の保存後にSTOPする(記録自体は必ず残す)。
    _assert_shared_narration_ok(shared_narration_status, "a2")
    return {"segment_status": all_status, "key_phrase_status": kp_status,
            "shared_narration_status": {k: v["status"] for k, v in shared_narration_status.items()},
            "kp_scaffold_status": kp_scaffold_status, "tts_backend": tts_backend}


def _generate_key_phrase_segments_a2(kp: dict, narration_dir: str, cached: dict | None = None,
                                      tts_backend: str = "structured_separation",
                                      style_profile: str = "default") -> dict:
    # W5(2026-09-29ユーザー正式決定APPROVED_FOR_PRODUCTION、Standard KP
    # 日本語意味へのJ3配線): japanese_title/preview/comment_1-4と同一の
    # _role_style_ja()(同一関数ロジック・同一backendゲート)をStandard KP
    # 日本語意味(japanese_meaning)へも適用する。既定backendではNoneを
    # 返し既存挙動(既定JAPANESE_STYLE_PREFIX)のまま(他のJapanese Roleへ
    # 波及しない、本関数内のみのlocal helper)。
    import er033_tts_flash_lite_family_x_styles_01 as fl_styles

    def _role_style_ja() -> str | None:
        if tts_backend != "speech_metadata_flash_lite":
            return None
        return fl_styles.FAMILY_X_ROLE_STYLE_JA

    def _role_style_ja_kp_meaning() -> str | None:
        # 委任_02A: Std KP日本語意味。fx_20261016ではP8-KP(別role KP_JA_MEANING、旧Full Story候補P8とは別物)。
        # default・旧profileはbase(_role_style_ja=J3)素通し=バイト同一。
        return style_profile_mod.resolve_role_style(
            style_profile, style_profile_mod.ROLE_KP_JA_MEANING, "a2", lambda _r: _role_style_ja())

    kp_items = sorted(kp["items"], key=lambda it: it["rank"])
    # 委任_02(関所): gloss再整合がHuman Review待ちのlevelは、KP segment全体のTTSを実行しない(0 API call)。
    _gloss_hr = _gloss_alignment_hr_unresolved(kp)
    if _gloss_hr:
        print(f"[FAMILY-X-AUDIO][STOP] KP gloss Human Review待ち(rank={[x.get('rank') for x in _gloss_hr]}): "
              "KP TTSを実行しません(0 API call)。")
        return _gloss_alignment_stopped_kp_results(kp_items, _gloss_hr, ("english", "japanese_meaning"))
    kp_results = {}
    for i, item in enumerate(kp_items, start=1):
        rank = item["rank"]
        used_form = item["used_form"]
        ja_gloss_tts, ja_gloss_tts_fallback = n3_tts.resolve_key_phrase_ja_gloss_tts(item)
        # 委任_02A: fx_20261016ではK2(2段key)、それ以外は従来経路(バイト同一)。
        _kp_en_fn, _kp_en_k2 = _kp_english_generate_fn(
            style_profile, "a2", tts_backend, used_form, f"{narration_dir}/kp{rank}_en.wav")
        with cl.segment_context(f"kp{rank}_english"):
            en_r = _generate_or_reuse_kp(
                cached, rank, "english", f"{narration_dir}/kp{rank}_en.wav",
                _kp_en_fn,
                # W5(Opus L2所見MAJOR-1、english role text guard)。
                expected_text=used_form)
        en_r["canonical_text"] = used_form
        if not validation_inheritance.is_untouched_entry(en_r):
            style_profile_mod.attach_segment_profile_record(en_r, style_profile, style_profile_mod.ROLE_KP_EN, _kp_en_k2)
        with cl.segment_context(f"kp{rank}_japanese_meaning"):
            ja_r = _generate_or_reuse_kp(
                cached, rank, "japanese_meaning", f"{narration_dir}/meaning_{i}.wav",
                lambda ja_gloss_tts=ja_gloss_tts, used_form=used_form,
                i=i: n3_tts.generate_a2_japanese_with_reading_safety(
                    ja_gloss_tts, f"{narration_dir}/meaning_{i}.wav", n3_tts.expected_substring_ja(ja_gloss_tts),
                    max_extra_chars=30, known_key_phrase_terms=[used_form],
                    style_prefix_override=_role_style_ja_kp_meaning(), tts_backend=tts_backend),
                # W5(J3配線に伴うMAJOR-1系guard、Standard KP日本語意味に
                # もtext guard+style_version guardを適用する)。
                expected_text=ja_gloss_tts, require_style_version=True)
        ja_r["canonical_text"] = ja_gloss_tts
        # M4/S3: KP_JA_MEANING overrideがあるprofile(fx_20261016のP8-KP)のときだけ記録(default/旧profileは新keyなし)。
        if not validation_inheritance.is_untouched_entry(ja_r):
            style_profile_mod.attach_segment_profile_record(
                ja_r, style_profile, style_profile_mod.ROLE_KP_JA_MEANING, _role_style_ja_kp_meaning())
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


def _assembled_filename_theme_component(theme_id: str) -> str:
    """Stage 3f実行時に発見(OPEN-193/204のGate修正で初めて到達したcode
    path): `--slug`にサブディレクトリ区切り(例: `family_x_b3_diversity_
    trial_01/hormuz`)を含む場合、`theme_id.upper()`をそのまま組み立てた
    出力filenameに"/"が残り、`{out_dir}/assembled/`配下に存在しない
    親directoryへの書き込みとしてFileNotFoundErrorになる(Assembly Gate
    修正前はこのcode pathへ到達しなかったため未発見だった、Family X
    以外の既存A/B/C Familyのfilename生成ロジックには影響しない)。
    filenameとしてのみ"/"を"_"に置換する(directory構造・player.html
    表示用theme_idは無変更)。"""
    return theme_id.upper().replace("/", "_")


def load_family_x_b1_sources(theme_out_dir: str, source_dir: str | None = None) -> dict:
    out_dir = f"{theme_out_dir}/b1b"
    narration_dir = f"{out_dir}/narration"
    # OPEN-193/OPEN-204(2026-09-27起票、Stage 3f修正): article.mdをout_dirへ
    # 手動コピーする回避策(OPEN-193)に頼らず、run_plan_stage/run_theme_
    # scaffoldと同じ正規ソース(source_dir/b1b/article.md)を直接読み込み、
    # article_textとしてGateへ渡す(KEY-PHRASE-SOURCE-CONSISTENCY-GATE-01
    # commit 8f197a74/1d69aa97にFamily X runner側が未追従だった配線漏れ
    # [OPEN-204]を解消)。source_dir省略時は既存の出力先候補
    # [out_dir/article.md等]によるfallback解決に委ねる(後方互換)。
    article_text = None
    if source_dir is not None:
        article_path = f"{source_dir}/b1b/article.md"
        if os.path.exists(article_path):
            article_text = load_text(article_path)
    asm.verify_episode_audio_validation_gate(out_dir, "B1", article_text=article_text)

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

    # FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01(I8/M2): chunk化したpartは、音声を読む前に整合検査(chunk集合・順序・語数・版・本文)と
    # 『親wav==ディスク上のchunk wavの生連結』(整数サンプル完全一致)を確認する。合格した親wavだけをtarget_rmsの基準に使う。
    parts_json = load_json(f"{out_dir}/parts.json")
    chunk_plans = _x_effective_chunk_plans(out_dir, parts_json)
    _res_path = f"{out_dir}/audit/tts_generation_results.json"
    _segs = (load_json(_res_path).get("segments") or {}) if os.path.exists(_res_path) else {}
    body_chunks, chunk_plan_used = {}, {}
    for pid, plan in chunk_plans.items():
        if not plan.get("chunked"):
            continue
        ids = chunk_tts.chunk_ids(plan)
        chunk_tts.verify_parent_integrity(plan, parts_json["part" + pid[-1]], {i: _segs[i] for i in ids if i in _segs}, _segs.get(pid))
        paths = [f"{narration_dir}/{i}.wav" for i in ids]
        chunk_tts.verify_raw_parent(f"{narration_dir}/{pid}.wav", paths)
        monos = []
        for pth in paths:
            m_, sr_, _, _ = common.read_wav_float(pth)
            assert sr_ == common.SAMPLE_RATE
            monos.append(m_)
        body_chunks[pid] = monos
        chunk_plan_used[pid] = plan

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
        # FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W4、2026-09-29ユーザー
        # 正式決定): Advanced(b1b)の中間segmentを日本語意味からEnglish
        # 解説(explanation_en)へ変更。`key_phrase_meanings`という変数名/
        # dict keyは、共有Production資産(er003_v1_n3_01_assemble.py::
        # build_b1_key_phrase_blocks、Family A/B/C/News/Z等が共有する
        # 既存関数)がこのままの名前でparts["key_phrase_meanings"]を
        # 参照するため、無変更のまま維持する(共有assemble関数自体は
        # 一切変更しない)。中身(実際に読み込むwavファイル)だけを
        # explanation_enへ差し替える(Family X b1bローダーのみの変更)。
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/kp{rank}_explanation_en.wav")
        key_phrase_meanings[rank] = mono

    return {"intro": intro, "notification": notification, "outro": outro,
            "narration": narration, "b1_segments": b1_segments,
            "key_phrase_components": key_phrase_components, "key_phrase_meanings": key_phrase_meanings,
            "kp_items": kp_items, "body_chunks": body_chunks, "chunk_plans": chunk_plan_used}


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
        # FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W4): b1bはexplanation_en
        # 音声(旧"key_phrase_ja_{rank}"ラベルは日本語音声時代のもの、
        # gain_report内の表示ラベルのみ変更、辞書keyの構造は無変更)。
        gained = gain_to_rms(mono, target_rms, f"key_phrase_explanation_{rank}")
        key_phrase_meaning_stereo[rank] = p9a.mono_24k_to_stereo_target(gained)
    result["key_phrase_components"] = key_phrase_stereo
    result["key_phrase_meanings"] = key_phrase_meaning_stereo

    b1_stereo = {}
    body_chunks = sources.get("body_chunks") or {}
    for name, mono in sources["b1_segments"].items():
        if name == "preview":
            continue
        if name in body_chunks:
            # chunk別gain(同一target_rms、peak<=0.95)→chunk間に固定無音0.2秒→連結(crossfade無し)→既存と同じ48kHz stereo化。
            # gain式はp9a.compute_gain_for_target_rmsを引数で渡して共用(I2)。親全体のgainは掛けていないので親keyにgain値を書かない(I7)。
            composed, rep_ = chunk_tts.compose_gained_parent(
                body_chunks[name], target_rms, gain_fn=p9a.compute_gain_for_target_rms, rms_fn=p9a.rms, peak_fn=p9a.peak)
            gain_report[f"b1_{name}"] = {"chunked": True, "note": "親全体のgainは掛けていない。chunk別gain・RMS・peakは chunk_tts を参照"}
            gain_report.setdefault("chunk_tts", {})[name] = rep_
            b1_stereo[name] = p9a.mono_24k_to_stereo_target(composed)
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


def _style_profile_gate_blocked_summary(theme_out_dir: str, out_dir: str, level: str) -> dict | None:
    """OPEN-300 M3(Opus条件Aレビュー反映): Assembly前のStyle profile Gate。Family X runnerの
    stage_assemble内でのみ呼ぶ(共有assembleは不変)。固定記録(audit/style_profile.json)が
    無い/defaultなら何もしない(Noneを返す=既存挙動とバイト同一)。非defaultのとき、profile対象
    segmentがprofileのStyleで生成されていない(minimal_fallback/local_rewrite_recovery/Std fallback等)場合は、
    record_human_approvalによる人間承認が無い限りBLOCKする。"""
    record = style_profile_mod.read_record(theme_out_dir)
    if record is None:
        return None
    profile_id = style_profile_mod.verify_record(record)
    if profile_id == style_profile_mod.PROFILE_DEFAULT:
        return None
    results_path = f"{out_dir}/audit/tts_generation_results.json"
    results = load_json(results_path) if os.path.exists(results_path) else {}
    approvals_path = asm.human_approval_path(out_dir)
    approvals = load_json(approvals_path) if os.path.exists(approvals_path) else {}
    gate = style_profile_mod.m3_assembly_gate(profile_id, level, results, approvals, level_dir=out_dir)   # B-wire(UD-3): 採用take分類核(正常LR/Fallback=警告、異常=BLOCK)
    save_json(f"{out_dir}/audit/style_profile_gate.json", gate)
    # 非ブロッキングwarning(例: KP英語がK2でなく承認済み4回構成のENGLISH_LOCK fallbackで生成された)は
    # 最終報告で見落とされないようstdoutへ列挙する(Gate判定は変えない)。
    for _w in gate.get("warnings") or []:
        print(f"[WARN][STYLE-PROFILE][M3] {level} {_w['segment']}: {_w['warning']}")
    if gate["status"] == "PASS":
        return None
    return {"status": "BLOCKED_STYLE_PROFILE_GATE", "profile_id": profile_id, "blocked": gate["blocked"],
            "warnings": gate.get("warnings") or [],
            "reason": "profile対象segmentが承認済みprofileのStyleで生成されていません(M3 Gate)。人間承認(record_human_approval)が"
                      "無い限りAssemblyを拒否します。本runnerはこのGateを回避しません。"}


def _assert_no_gloss_alignment_hr(level_out_dir: str, level: str) -> None:
    """委任_02(関所・assembly前): keywords_canonicalized.jsonにgloss Human Review待ちitemが残っていれば、
    tts_generation_results.jsonの有無に関わらず(Gateはresultsが無いと即returnするため)assemblyを拒否する。
    HR待ちに加え、ON化前・未評価itemも拒否する(OF-KGCPW-08)。"""
    import json as _json
    kp_path = f"{level_out_dir}/key_phrases/keywords_canonicalized.json"
    with open(kp_path, encoding="utf-8") as _f:
        _hr = _gloss_alignment_hr_unresolved(_json.load(_f))
    if _hr:
        raise RuntimeError(
            f"EPISODE_BLOCKED_BY_GLOSS_ALIGNMENT: {level}のepisode assemblyを中止しました。KP日本語glossの再整合が成立せず"
            f"Human Review待ちのitemがあります(rank={[x.get('rank') for x in _hr]})。"
            f"resolve_gloss({_gloss_align_mod().HR_RESOLVE_RUNBOOK})で確定するかKPを再生成してから、TTS段を再実行してください。"
            + (f"(未評価: {_gloss_align_mod().UNEVALUATED_REASON})" if any(x.get("_unevaluated") for x in _hr) else ""))


def _attach_kp_vote_audit(summary: dict, out_dir: str, level: str) -> None:
    """KP3V(Fable判断で採用): 組立時の非blocking監査。blockingゲート化はしない(ユーザー判断の範囲外)。"""
    if not kp_vote.vote_enabled():
        return
    try:
        res = load_json(f"{out_dir}/audit/tts_generation_results.json")
        summary["kp_vote_audit"] = kp_vote.assembly_audit(res, level)
    except Exception as exc:   # 監査の失敗で組立を止めない
        summary["kp_vote_audit"] = {"enabled": True, "error": f"{type(exc).__name__}: {exc}", "blocking": False}


def _chunk_parent_refresh_x(out_dir: str, level: str = "b1b") -> None:
    """tts_generation_results.json上のchunk親集約entryを(再)構築して保存する(chunk化したpartが無い/legacy結果ならファイルに触れない)。"""
    rp = f"{out_dir}/audit/tts_generation_results.json"
    pp = f"{out_dir}/parts.json"
    if not (os.path.exists(rp) and os.path.exists(pp)):
        return
    data = load_json(rp)
    parts = load_json(pp)
    plans = _x_effective_chunk_plans(out_dir, parts)
    if not any(pl.get("chunked") for pl in plans.values()):
        return
    _refresh_x_chunk_parents(out_dir, parts, data.setdefault("segments", {}), plans, level)
    save_json(rp, data)


def _chunk_assembly_summary_x(plans: dict, gain_chunks: dict, timeline: list) -> dict:
    """組立のruntime evidence: 分割位置・種別・chunk数・0.2秒の実測offset(part内/episode内)・chunk別gain/RMS/peak(cap発動を含む)。"""
    starts = {}
    for item in timeline:
        label = item.get("part", "")
        if label.startswith("Full Story Part "):
            starts[f"full_story_part{label.split()[3]}"] = item["start_seconds"]
    out = {"planner_version": chunk_tts.CHUNK_PLANNER_VERSION, "extra_pause_seconds": chunk_tts.EXTRA_PAUSE_SECONDS, "parents": {}}
    for pid, plan in plans.items():
        rep_ = gain_chunks.get(pid) or {}
        base = starts.get(pid)
        out["parents"][pid] = {
            "chunk_ids": chunk_tts.chunk_ids(plan), "words": [c["words"] for c in plan["chunks"]],
            "boundary_kinds": [c["boundary_kind"] for c in plan["chunks"]],
            "part_start_in_episode_s": base, "gap_offsets_in_part_s": rep_.get("boundary_offsets_s"),
            "gap_offsets_in_episode_s": ([[round(base + a, 4), round(base + b, 4)] for a, b in rep_.get("boundary_offsets_s") or []]
                                          if base is not None else None),
            "gains": rep_.get("gains"), "pre_rms": rep_.get("pre_rms"), "post_rms": rep_.get("post_rms"),
            "peak_after": rep_.get("peak_after"), "peak_capped": rep_.get("peak_capped"), "chunk_samples": rep_.get("chunk_samples")}
    return out


def stage_assemble_family_x_b1(theme_out_dir: str, theme_id: str, source_dir: str | None = None) -> dict:
    out_dir = f"{theme_out_dir}/b1b"
    os.makedirs(f"{out_dir}/assembled", exist_ok=True)
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    # small_bag run_02(Stage 3c実行時)で発見: Key Phrase選定が構造Gateで
    # STOPし、keywords_canonicalized.json自体が存在しない場合、そのまま
    # 進むとFileNotFoundErrorで未処理クラッシュする(既存Key Phrase Gateを
    # 回避する意図ではなく、既に上流でBLOCKED済みであることをplayer.html
    # 生成まで到達できる形で明示的に記録するための防御)。
    if not os.path.exists(f"{out_dir}/key_phrases/keywords_canonicalized.json"):
        summary = {"status": "BLOCKED_KP_SCAFFOLD_MISSING",
                   "reason": "key_phrases/keywords_canonicalized.jsonが存在しません"
                             "(上流のKey Phrase構造Gate[KEY_WORDS_STRUCTURE_INVALID等]でSTOP、"
                             "本runnerはこのGateを回避しません)。"}
        save_json(f"{out_dir}/run_summary_assemble.json", summary)
        return summary
    _assert_no_gloss_alignment_hr(out_dir, "B1")
    # Opus L2所見BL-2(defense-in-depth): shared_narration(shell)segmentが
    # 非OKのまま記録されていれば、既存Gate(asm.verify_episode_audio_
    # validation_gate、segments/key_phrasesのみ走査で構造的に対象外)より
    # 前でAssemblyを拒否する。assemble.py自体は無変更。
    shared_blocked = _shared_narration_gate_blocked_summary(out_dir)
    if shared_blocked is not None:
        save_json(f"{out_dir}/run_summary_assemble.json", shared_blocked)
        return shared_blocked
    # M2(c): Style profile Gate・共有Gateより前に、chunk親集約entry(status・親wav・human_approved_chunks)を再構築する
    # (STOPPED chunkの人間承認後は、親entry/親wavが古いまま・無いままになるため。generate後の承認→再assembleで親も通る)。
    _chunk_parent_refresh_x(out_dir)
    # LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01 B3(UD-1): 三者一致Gate(表示=TTS入力=ASR正解)。不一致・位置不能・overlay未適用=技術STOP(HRキューへ入れない)。M3/Style Gateより前。
    import er132_lr_overlay_pages_01 as _er132
    _lr_blocked = _er132.assemble_gate_summary(theme_out_dir, "b1b", not_rendered_clip_ids=_er132.X_NOT_RENDERED_CLIP_IDS)
    if _lr_blocked is not None:
        save_json(f"{out_dir}/run_summary_assemble.json", _lr_blocked)
        return _lr_blocked
    style_blocked = _style_profile_gate_blocked_summary(theme_out_dir, out_dir, "b1b")
    if style_blocked is not None:
        save_json(f"{out_dir}/run_summary_assemble.json", style_blocked)
        return style_blocked
    sources = load_family_x_b1_sources(theme_out_dir, source_dir=source_dir)
    parts = apply_family_x_b1_gain(sources)
    seq = build_family_x_b1_timeline(parts)
    result = asm.assemble_with_timeline(seq)
    headroom = asm.apply_headroom_safety_valve(result["assembled"], seq)
    assembled = headroom["assembled"]

    out_path = f"{out_dir}/assembled/Family_X_Audio_B1_{_assembled_filename_theme_component(theme_id)}.wav"
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
    if sources.get("body_chunks"):
        summary["chunk_tts"] = _chunk_assembly_summary_x(sources["chunk_plans"], parts["gain_report"].get("chunk_tts") or {}, result["timeline"])
        save_json(f"{out_dir}/audit/chunk_tts_assembly_b1b.json", summary["chunk_tts"])
    _attach_kp_vote_audit(summary, out_dir, "b1b")   # KP3V: 非blocking監査(KP英語phraseのvote証跡欠落を警告+summary記録)
    pnap_hooks.attach_alarm_audit(summary, out_dir, "b1b")   # PNAP 委任_02: 固有名詞アラーム要約を組立summaryへ埋め込み(非blocking・flag OFFは何も付けない)
    save_json(f"{out_dir}/run_summary_assemble.json", summary)
    return summary


def load_family_x_a2_sources(theme_out_dir: str, source_dir: str | None = None) -> dict:
    out_dir = f"{theme_out_dir}/a2"
    narration_dir = f"{out_dir}/narration"
    # OPEN-193/OPEN-204(2026-09-27起票、Stage 3f修正): load_family_x_b1_
    # sources()と同じ理由でarticle_textを正規ソースから読み込みGateへ渡す。
    article_text = None
    if source_dir is not None:
        article_path = f"{source_dir}/a2/article.md"
        if os.path.exists(article_path):
            article_text = load_text(article_path)
    asm.verify_episode_audio_validation_gate(out_dir, "A2", article_text=article_text)

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

    # CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01: chunk化したStd本文partは、音声を読む前に整合検査(chunk集合・順序・語数・版・本文)と
    # 『親wav==ディスク上の(減速後)chunk wavの生連結』(整数サンプル完全一致)を確認する(Advと同じ手順・同じ関数)。
    parts_json = load_json(f"{out_dir}/parts.json")
    chunk_plans = _x_effective_chunk_plans(out_dir, parts_json)
    _res_path = f"{out_dir}/audit/tts_generation_results.json"
    _segs = (load_json(_res_path).get("segments") or {}) if os.path.exists(_res_path) else {}
    body_chunks, chunk_plan_used = {}, {}
    for pid, plan in chunk_plans.items():
        if not plan.get("chunked"):
            continue
        ids = chunk_tts.chunk_ids(plan)
        chunk_tts.verify_parent_integrity(plan, parts_json["part" + pid[-1]], {i: _segs[i] for i in ids if i in _segs}, _segs.get(pid))
        # Opus R1(2026-10-26): chunk単位の6%減速証跡検査を、共有Gateと同じくload関数の中にも置く(stage関数外の直接呼出でも検査を通す。
        # 人間承認では迂回しない)。R2により減速前後長の記録欠落も違反。
        _bad = chunk_tts.std_chunk_slowdown_violations(plan, _segs)
        if _bad:
            raise chunk_tts.ChunkIntegrityError(f"BLOCKED_STD_CHUNK_SLOWDOWN_GATE({pid}): {_bad}")
        paths = [f"{narration_dir}/{i}.wav" for i in ids]
        chunk_tts.verify_raw_parent(f"{narration_dir}/{pid}.wav", paths)
        monos = []
        for pth in paths:
            m_, sr_, _, _ = common.read_wav_float(pth)
            assert sr_ == common.SAMPLE_RATE
            monos.append(m_)
        body_chunks[pid] = monos
        chunk_plan_used[pid] = plan

    a2_segments = {}
    for name in ("comment_1", "comment_2", "comment_3", "comment_4",
                  "full_story_part1", "full_story_part2",
                  "full_story_part3", "in_one_line"):
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/{name}.wav")
        assert sr == common.SAMPLE_RATE
        a2_segments[name] = mono

    return {"intro": intro, "notification": notification, "outro": outro,
            "preview_mono": preview_mono, "narration": narration,
            "key_phrase_components": key_phrase_components, "a2_segments": a2_segments, "kp_items": kp_items,
            "body_chunks": body_chunks, "chunk_plans": chunk_plan_used}


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
    body_chunks = sources.get("body_chunks") or {}
    for name, mono in sources["a2_segments"].items():
        if name in body_chunks:
            # Std chunk: chunk別gain(同一target_rms、peak<=0.95、各chunkは減速後wav)→chunk間に固定無音0.2秒(減速対象外)→連結→48kHz stereo化(Advと同一関数)。
            composed, rep_ = chunk_tts.compose_gained_parent(
                body_chunks[name], target_rms, gain_fn=p9a.compute_gain_for_target_rms, rms_fn=p9a.rms, peak_fn=p9a.peak)
            gain_report[f"a2_{name}"] = {"chunked": True, "note": "親全体のgainは掛けていない。chunk別gain・RMS・peakは chunk_tts を参照"}
            gain_report.setdefault("chunk_tts", {})[name] = rep_
            a2_stereo[name] = p9a.mono_24k_to_stereo_target(composed)
            continue
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


def stage_assemble_family_x_a2(theme_out_dir: str, theme_id: str, source_dir: str | None = None) -> dict:
    out_dir = f"{theme_out_dir}/a2"
    os.makedirs(f"{out_dir}/assembled", exist_ok=True)
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    # stage_assemble_family_x_b1()と同じ防御(対称性のため、A2側でも同じ
    # 状況が起きた場合に備える)。
    if not os.path.exists(f"{out_dir}/key_phrases/keywords_canonicalized.json"):
        summary = {"status": "BLOCKED_KP_SCAFFOLD_MISSING",
                   "reason": "key_phrases/keywords_canonicalized.jsonが存在しません"
                             "(上流のKey Phrase構造Gate[KEY_WORDS_STRUCTURE_INVALID等]でSTOP、"
                             "本runnerはこのGateを回避しません)。"}
        save_json(f"{out_dir}/run_summary_assemble.json", summary)
        return summary
    _assert_no_gloss_alignment_hr(out_dir, "A2")
    # stage_assemble_family_x_b1()と同じ防御(BL-2、defense-in-depth)。
    shared_blocked = _shared_narration_gate_blocked_summary(out_dir)
    if shared_blocked is not None:
        save_json(f"{out_dir}/run_summary_assemble.json", shared_blocked)
        return shared_blocked
    # CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01: Style profile Gate・共有Gateより前に、chunk親集約entry(status・親wav・human_approved_chunks・減速集約)を
    # 再構築し(M2(c)、Advと同じ)、全chunkのchunk単位6%減速を確認する(共有Gateはchunk idの減速を見ないため追加。回避しない)。
    _chunk_parent_refresh_x(out_dir, "a2")
    std_chunk_blocked = _x_std_chunk_slowdown_blocked(out_dir)
    if std_chunk_blocked is not None:
        save_json(f"{out_dir}/run_summary_assemble.json", std_chunk_blocked)
        return std_chunk_blocked
    # LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01 B3(UD-1): 三者一致Gate(b1と同じ。M3/Style Gateより前)。
    import er132_lr_overlay_pages_01 as _er132
    _lr_blocked = _er132.assemble_gate_summary(theme_out_dir, "a2", not_rendered_clip_ids=_er132.X_NOT_RENDERED_CLIP_IDS)
    if _lr_blocked is not None:
        save_json(f"{out_dir}/run_summary_assemble.json", _lr_blocked)
        return _lr_blocked
    style_blocked = _style_profile_gate_blocked_summary(theme_out_dir, out_dir, "a2")
    if style_blocked is not None:
        save_json(f"{out_dir}/run_summary_assemble.json", style_blocked)
        return style_blocked
    sources = load_family_x_a2_sources(theme_out_dir, source_dir=source_dir)
    parts = apply_family_x_a2_gain(sources)
    seq = build_family_x_a2_timeline(parts)
    result = asm.assemble_with_timeline(seq)
    headroom = asm.apply_headroom_safety_valve(result["assembled"], seq)
    assembled = headroom["assembled"]

    out_path = f"{out_dir}/assembled/Family_X_Audio_A2_{_assembled_filename_theme_component(theme_id)}.wav"
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
    if sources.get("body_chunks"):
        summary["chunk_tts"] = _chunk_assembly_summary_x(sources["chunk_plans"], parts["gain_report"].get("chunk_tts") or {}, result["timeline"])
        summary["chunk_tts"]["level"] = "a2"
        summary["chunk_tts"]["composition"] = chunk_tts.STD_SLOWDOWN_COMPOSITION
        save_json(f"{out_dir}/audit/chunk_tts_assembly_a2.json", summary["chunk_tts"])
    _attach_kp_vote_audit(summary, out_dir, "a2")   # KP3V: 非blocking監査(KP英語phraseのvote証跡欠落を警告+summary記録)
    pnap_hooks.attach_alarm_audit(summary, out_dir, "a2")   # PNAP 委任_02: 固有名詞アラーム要約を組立summaryへ埋め込み(非blocking・flag OFFは何も付けない)
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
        try:
            return next(p["price"] for p in prices
                        if p["provider"] == provider and p["model"] == model and p["meter"] == meter
                        and p.get("tier", "Standard") == "Standard")
        except StopIteration as e:
            # C3-2(G-4): fail-closed。単価未登録を0円扱いにしない(efam._load_pricingと同じ
            # PricingNotFoundError)。cost_usd付きレコードはprice()を呼ばない(下記)。
            raise routing.PricingNotFoundError(
                f"[STOP] 単価未登録model: {provider}/{model} meter={meter}") from e
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
            # SF-1是正(修正3回目、2026-09-28、Opus L2所見): Batch経路
            # (provider="gemini_batch"、er006_batch_tts_wiring_01.py:154)は
            # 既にcost_usd/cost_jpyを実額でrecへ記録済み(:167-169、
            # pricing_snapshot.jsonのflash-lite Batch tier単価から算出済み)
            # にもかかわらず、本関数はprovider in (gemini/openai/openai_asr)
            # のみをtoken基準で再計算しており、Batch分は常に0円扱いだった
            # (既定BATCHでもtts-backend=speech_metadata_flash_liteへ到達
            # 可能になったため、既定実行モードでのbudget guardが盲目に
            # なる運用リスク)。recに既にcost_usdがあれば、providerに
            # 関わらずそれを実額としてそのまま採用する(token単価による
            # 二重計算はしない)。
            if rec.get("cost_usd") is not None:
                usd = rec["cost_usd"]
            else:
                # C3-2(G-4): 旧`except StopIteration: usd = 0.0`(fail-open)を撤去。単価未登録は
                # price()がPricingNotFoundErrorを送出し、Budget Guardが盲目にならない。
                if provider == "azure":
                    usd = cl.azure_stt_cost_usd(rec, price)
                elif provider in ("gemini", "openai", "openai_asr") and model:
                    in_tok = rec.get("input_tokens") or 0
                    out_tok = rec.get("output_tokens") or 0
                    usd = in_tok * price(provider, model, "input_tokens") / 1e6 \
                        + out_tok * price(provider, model, "output_tokens") / 1e6
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
                        kp_by_rank: dict, japanese_title: str | None,
                        kp_explanations_by_rank: dict | None = None) -> dict:
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
        if level == "b1b":
            # FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W4): Advanced中間は
            # 英語解説(explanation_en)。末尾のEnglish Phraseは新規生成では
            # なく先頭(kp{rank}_en.wav)と同一wavを再掲するため、audio
            # tupleの1件目と3件目に同じpathを渡す(reuseを表示上も明示)。
            expl_row = (kp_explanations_by_rank or {}).get(rank) or (kp_explanations_by_rank or {}).get(str(rank)) or {}
            explanation_text = expl_row.get("explanation") or expl_row.get("explanation_text") or "(未取得)"
            text = (f"EN: {kp['used_form']}<br>EXPLANATION: {explanation_text}"
                    f"<br>EN (repeat, same audio file as above): {kp['used_form']}")
            audio = (f"{narration_dir}/kp{rank}_en.wav", f"{narration_dir}/kp{rank}_explanation_en.wav",
                     f"{narration_dir}/kp{rank}_en.wav")
        else:
            text = f"EN: {kp['used_form']}<br>JA: {kp['japanese_gloss']}"
            audio = (f"{narration_dir}/kp{rank}_en.wav", f"{narration_dir}/meaning_{idx}.wav")
        return {"text": text, "voice": voice, "audio": audio, "sfx": False}
    if label.startswith("Full story intro"):
        return {"text": "(共有固定Full story intro)", "voice": voice, "audio": None, "sfx": False}
    for i in (1, 2, 3, 4):
        if label.startswith(f"Comment {i}"):
            return {"text": support[f"comment_{i}"], "voice": voice,
                    "audio": f"{narration_dir}/comment_{i}.wav", "sfx": False}
    # FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W1): Heading Readout撤去後は
    # "Full Story Part N Heading"ラベル自体がv2 segment順序に存在しない
    # ため、本文3つ(part1/part2/part3)のみを判定すればよい。
    for i in (1, 2, 3):
        if label.startswith(f"Full Story Part {i}"):
            return {"text": parts[f"part{i}"], "voice": voice,
                    "audio": f"{narration_dir}/full_story_part{i}.wav", "sfx": False}
    if label.startswith("In One Line"):
        return {"text": parts["in_one_line"], "voice": voice,
                "audio": f"{narration_dir}/in_one_line.wav", "sfx": False}
    return {"text": "(共有固定segment、記事固有scriptなし)", "voice": None, "audio": None, "sfx": False}


# ============================================================
# SLOT-23 委任_04C: 学習項目①②③の本文ハイライト(Family X配線。設計=docs/research/SLOT-23-CONSUMER-DESIGN-01/DESIGN_03.md §B/§C、契約=CONTRACT_03.md)
# 表示有効化=確定レコードのdisplay_spec(er128.display_spec_of、flag非経由)が真のrun・levelだけ。無い=従来描画(バイト同一)。
# 解決は共通 er_learning_highlight_01.resolve_highlights 1箇所、描画は共通 render_script_html 1箇所。特定不能(ISSUE)はページ生成前にSTOP(fail-closed)。
# 表示範囲(DisplayUnit)=ページに表示される本文単位すべて: Full Story Part 1-3 + In One Line(Fable決定。Full Story外の「In one line」節にのみ出現する語句もISSUEにしない)。
# ============================================================
HIGHLIGHT_X_UNIT_KEYS = ("full_story_part1", "full_story_part2", "full_story_part3", "in_one_line")
# ハイライトを出すplayer(display_spec付きrun)だけが使うCSS=PLAYER_STANDARD_CSS + 共通HIGHLIGHT_CSS(単一定数)。PLAYER_STANDARD_CSS本体(共有module audio_review_player)は不変
# =マーク無しrun・他Familyのplayerのバイト同一を保つ。
import er_learning_highlight_01 as _hl_const
PLAYER_CSS_WITH_HIGHLIGHT = player_common.PLAYER_STANDARD_CSS + "\n" + _hl_const.HIGHLIGHT_CSS


class HighlightStop(RuntimeError):
    """ハイライト解決のISSUE(fail-closed)。ページを作らない。args[0]に原因コードを含む。"""


def x_display_units(parts: dict) -> list:
    """Xの表示単位列(表示順)。parts.json の part1-3 + in_one_line(あれば)。texts=段落/節の本文そのまま(player/公開ページがscriptとして出す文字列)。"""
    units = [{"key": f"full_story_part{i}", "texts": [parts[f"part{i}"]], "joiner": " "} for i in (1, 2, 3)]
    if (parts.get("in_one_line") or "").strip():
        units.append({"key": "in_one_line", "texts": [parts["in_one_line"]], "joiner": " "})
    return units


def x_source_dir_of(out_dir: str) -> str:
    """候補生成に使った本文のあるsource_dir(entry_point.jsonに記録。`{source_dir}/{level}/article.md`=候補生成の入力本文。`<run>/<lv>/article.md`決め打ち禁止=M1)。"""
    ep = f"{out_dir}/entry_point.json"
    if not os.path.exists(ep):
        raise HighlightStop(f"X_HIGHLIGHT_SOURCE_DIR_UNKNOWN: {ep}がありません(本文の取得元が不明)")
    sd = load_json(ep).get("source_dir")
    if not sd:
        raise HighlightStop(f"X_HIGHLIGHT_SOURCE_DIR_UNKNOWN: {ep}にsource_dirがありません")
    return sd


def resolve_x_highlights(out_dir: str, level: str, *, source_dir: str | None = None, lr_rebound: bool = False):
    """display_spec付きのrun・levelだけ解決して返す。display_spec無し=None(従来描画)。ISSUE=HighlightStop(原因コード付き。部分適用・黙って落とすことはしない)。
    入力: article_text=`{source_dir}/{level}/article.md`(text_sha256一致必須=HL_TEXT_SHA_MISMATCH)、候補doc=`{out_dir}/{level}/key_phrases/kp_candidates.json`、
    items=`items_from_record(確定レコード)`、DisplayUnit=x_display_units(parts.json)。"""
    if not x_display_spec(out_dir, level):
        return None
    import er_learning_highlight_01 as hl
    kp_dir = f"{out_dir}/{level}/key_phrases"
    rec = _er128().load_record(kp_dir)
    if rec is None:
        raise HighlightStop(f"X_HIGHLIGHT_RECORD_MISSING: {kp_dir}の確定レコードがありません")
    cands_path = f"{kp_dir}/kp_candidates.json"
    if not os.path.exists(cands_path):
        raise HighlightStop(f"X_HIGHLIGHT_CANDIDATES_MISSING: {cands_path}がありません")
    sd = source_dir or x_source_dir_of(out_dir)
    article_text = load_text(f"{sd}/{level}/article.md")
    parts = load_json(f"{out_dir}/{level}/parts.json")
    # LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01 B3(UD-1): ハイライトはLR後の表示本文(overlay)で解決する(描画と同じ文字列。LR無し=同一objectでlr_rebound不変)。
    import er132_lr_overlay_pages_01 as _er132
    _parts_disp, _ = _er132.overlay_level_dir_units(f"{out_dir}/{level}", parts)
    lr_rebound = lr_rebound or (_parts_disp is not parts)
    res = hl.resolve_highlights(article_text, load_json(cands_path), hl.items_from_record(rec), x_display_units(_parts_disp), lr_rebound=lr_rebound)
    if res["status"] != "OK":
        view = hl.contract_view(res)
        codes = [f"{i['code']}(A班名={a['code']}):{i.get('candidate_id')}" for i, a in zip(view["issues"], res["issues"])]
        raise HighlightStop(f"X_HIGHLIGHT_UNRESOLVED({level}): {'; '.join(codes)}。ページ・playerを作りません(部分適用なし)。"
                            "原因を確認してください(本文のLocal Rewrite後の語句消失・候補docと本文の不一致 等)。")
    return res


def x_script_cell_html(text: str, unit_key: str, result: dict, *, chunk_texts=None, audience: str = "public") -> str:
    """ハイライトありrunのplayer用script cell(HTMLエスケープ+装飾+当該Part直後の③訳リスト)。devの⏸は装飾の外(共通render_script_html)。"""
    import er_learning_highlight_01 as hl
    import er_user_listening_page_common_01 as _uc
    hls = hl.highlights_for_text(result, unit_key, 0)
    bpos = _uc._chunk_boundary_positions(text, chunk_texts) if (audience == _uc.AUDIENCE_DEV and chunk_texts) else []
    return hl.render_script_html(text, hls, bpos, " " + _uc._CHUNK_MARKER_HTML) + hl.meaning_list_html(hl.meanings_for_unit(result, unit_key))


PART1_HEADING_MARK = "<h3>Vocabulary &amp; Expressions</h3>"


def validate_part1_block_count(section_html: str, level: str, *, where: str = "") -> int:
    """Part 1ブロックの積極検出(SLOT-23 M11、DESIGN_03 §A-4)。vocab対象level(Advanced、およびマーク付きStandard)では当該level節にPart 1が**ちょうど1個**
    (0個=判断記録なし等で黙って欠落、2個=重複、いずれもSTOP)。判断記録(T1/T2)が無いと0個になる。戻り値=個数。"""
    n = section_html.count(PART1_HEADING_MARK)
    if n != 1:
        raise RuntimeError(f"[STOP][Part 1] X_PART1_BLOCK_COUNT({level}{(' ' + where) if where else ''}): 学習テキスト Part 1のブロックが{n}個です(ちょうど1個のはず)。"
                           "0個=訳欄の判断記録なし・生成漏れ、2個=重複。ページ・playerを作りません。")
    return n


def verify_x_level_page(section_html: str, level: str, result: dict | None, out_dir: str, *, audience: str = "public", script_texts=None) -> None:
    """player/公開ページの当該level節の検査(display_spec付きrunだけ。無い=何もしない=従来どおり)。
    (1) G3: 装飾・③訳・本文不変・public混入(er128_kp_highlight_01.verify_highlights、kill switch時はSKIPPED_DISABLED) (2) Part 1がちょうど1個。違反=RuntimeError(STOP)。"""
    if not x_display_spec(out_dir, level):
        return
    if result is not None:
        g = _g3().verify_highlights(section_html, {"result": result, "audience": audience, "script_texts": script_texts})
        if g["status"] == "FAIL":
            raise RuntimeError(f"[STOP][Highlight] X_HIGHLIGHT_G3_FAIL({level}): " + "; ".join(f"{p['code']}:{p.get('candidate_id')}:{p['detail']}" for p in g["problems"][:8]))
    validate_part1_block_count(section_html, level)


def resolve_x_highlights_for_levels(out_dir: str, levels: list, *, source_dir: str | None = None) -> dict:
    """{level: resolve_x_highlights結果|None}(両level分)。assemble済み(status=OK)かつ`levels`に含まれるlevelだけ解決し、他はNone。ISSUE=HighlightStop。"""
    out = {}
    for lv in ("b1b", "a2"):
        asm = f"{out_dir}/{lv}/run_summary_assemble.json"
        ok = lv in levels and os.path.exists(asm) and load_json(asm).get("status") == "OK"
        out[lv] = resolve_x_highlights(out_dir, lv, source_dir=source_dir) if ok else None
    return out


def verify_x_player(out_dir: str, player_path: str, levels: list, hl_by_level: dict, *, audience: str = "public") -> None:
    """生成済みplayerの、display_spec付きlevel節のG3+Part 1ちょうど1個の検査(マーク無しlevelは何もしない)。違反=RuntimeError/ValueError(呼出側がSTOP)。"""
    text = None
    for lv in levels:
        if not x_display_spec(out_dir, lv):
            continue
        if text is None:
            with open(player_path, encoding="utf-8") as f:
                text = f.read()
        verify_x_level_page(player_level_section(text, lv), lv, hl_by_level.get(lv), out_dir, audience=audience)


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


def _build_level_table(level_dir: str, level: str, japanese_title: str | None = None, audience: str = "public", highlights: dict | None = None) -> str:
    """audience(委任_08): "public"(既定)=従来とバイト同一(マーカーなし) / "dev"=Full Story本文に実TTS Chunk境界(audit/chunk_plan_<level>.json)の⏸(開発確認用)。
    highlights(SLOT-23): resolve_x_highlightsの結果。None=従来とバイト同一(未escapeのscript文字列)。指定時のみFull Story/In One Lineのscript cellを
    escape+装飾+当該Part直後の③訳リストに切替(M13)、表の前に凡例1行、表示範囲外の③訳は表の後に置く。"""
    import er_user_listening_page_common_01 as _uc
    _uc.normalize_audience(audience)
    _plans = _uc.load_chunk_plans(f"{level_dir}/audit/chunk_plan_{level}.json") if audience == _uc.AUDIENCE_DEV else {}
    assemble_summary = load_json(f"{level_dir}/run_summary_assemble.json")
    if assemble_summary.get("status") != "OK":
        return f"<p style='color:#b00'>Assembly未完了(status={assemble_summary.get('status')})。table省略。</p>"
    timeline = load_json(f"{level_dir}/audit/timeline.json")
    parts = load_json(f"{level_dir}/parts.json")
    narration_dir = f"{level_dir}/narration"
    kp = load_json(f"{level_dir}/key_phrases/keywords_canonicalized.json")
    if _gloss_alignment_hr_unresolved(kp):   # 委任_02: HR待ちglossをpage/playerに出さない(多重防御。通常はassemble未完了で到達しない)
        return "<p style='color:#b00'>KP日本語glossがHuman Review待ちのためtable省略。</p>"
    kp_by_rank = {item["rank"]: item for item in kp["items"]}
    abs_url = player_common.abs_file_url
    support = load_json(f"{level_dir}/{'b1_support_texts.json' if level == 'b1b' else 'a2_support_texts.json'}")
    # LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01 B3(UD-1): 表示本文へLR後の英文を反映(派生overlay。parts.json/support原本は不変。LR無し=同一objectでbyte同一)。
    import er132_lr_overlay_pages_01 as _er132
    parts, support = _er132.overlay_level_dir_units(level_dir, parts, support)
    # FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W4): Advanced(b1b)の
    # player行に英語解説(explanation_en)textを表示するため、
    # tts_generation_results.jsonのkey_phrases[rank]["explanation"]を読む
    # (Family X runner自身の出力ファイルのみ、共有KPデータ構造
    # keywords_canonicalized.jsonへは書き込まない)。
    kp_explanations_by_rank = None
    if level == "b1b":
        tts_results_path = f"{level_dir}/audit/tts_generation_results.json"
        if os.path.exists(tts_results_path):
            tts_results = load_json(tts_results_path)
            kp_explanations_by_rank = {
                int(r): {"explanation": v.get("explanation", {}).get("explanation_text")}
                for r, v in (tts_results.get("key_phrases") or {}).items()
            }

    rows = []
    for entry in timeline:
        label = entry["part"]
        if label.startswith("pause_"):
            continue
        info = _row_info_family_x(label, level, parts, support, narration_dir, kp_by_rank, japanese_title,
                                   kp_explanations_by_rank=kp_explanations_by_rank)
        _m_fs = _re_only_segments.match(r"Full Story Part ([123])", label)
        _hl_unit = f"full_story_part{_m_fs.group(1)}" if _m_fs else ("in_one_line" if label.startswith("In One Line") else None)
        if highlights is not None and _hl_unit is not None:
            _cts = _uc.chunk_texts_of_plan(_plans.get(_hl_unit)) if (_m_fs and audience == _uc.AUDIENCE_DEV) else None
            info = dict(info, text=x_script_cell_html(info["text"], _hl_unit, highlights, chunk_texts=_cts, audience=audience))
        elif _m_fs and audience == _uc.AUDIENCE_DEV and _uc.chunk_texts_of_plan(_plans.get(f"full_story_part{_m_fs.group(1)}")):
            info = dict(info, text=_uc.script_html_with_chunk_markers(info["text"], _uc.chunk_texts_of_plan(_plans[f"full_story_part{_m_fs.group(1)}"])))
        sec = entry["start_seconds"]
        voice_disp = info["voice"] or ("SFX" if info["sfx"] else "—")
        if info["sfx"] or not info["audio"]:
            audio_html = "—"
        elif isinstance(info["audio"], tuple):
            audio_html = player_common.render_single_audio_html(tuple(abs_url(p) for p in info["audio"]))
        else:
            audio_html = player_common.render_single_audio_html(abs_url(info["audio"]))
        rows.append(player_common.render_timeline_row(sec, label, voice_disp, info["text"], audio_html, missing=False))
    if highlights is not None:
        import er_learning_highlight_01 as _hl
        _legend = _hl.legend_html() if highlights.get("stats", {}).get("decorated") else ""
        return _legend + player_common.render_timeline_table(rows) + _hl.meaning_list_html(_hl.meanings_for_unit(highlights, None))
    return player_common.render_timeline_table(rows)


PLAYER_LEVEL_HEADINGS = {"b1b": "<h2>Advanced(B1)</h2>", "a2": "<h2>Standard(A2)</h2>"}


def player_level_section(player_html: str, level: str) -> str:
    """player.htmlから**当該levelの節**を切り出す(節単位の4者一致検査用)。Advanced=`<h2>Advanced(B1)</h2>`〜`<h2>Standard(A2)</h2>`の手前 /
    Standard=`<h2>Standard(A2)</h2>`〜後続の事後試聴リスト(`<h3>Advanced(B1)</h3>`)の手前。見出しが無い/重複はValueError(fail-closed)。"""
    head = PLAYER_LEVEL_HEADINGS[level]
    if player_html.count(head) != 1:
        raise ValueError(f"player.htmlのlevel見出し {head} が{player_html.count(head)}個あります(ちょうど1個のはず)")
    start = player_html.index(head)
    other = PLAYER_LEVEL_HEADINGS["a2" if level == "b1b" else "b1b"]
    ends = [i for i in (player_html.find(other, start + len(head)), player_html.find("<h3>Advanced(B1)</h3>", start), player_html.find("</body>", start)) if i >= 0]
    return player_html[start:min(ends)]


def build_player_html(theme_out_dir: str, theme_id: str, japanese_title: str | None, study_html: str = "", study_html_a2: str = "",
                      audience: str = "public", highlights_by_level: dict | None = None) -> str:
    """audience(委任_08): "public"(既定)=Chunk境界マーカーなし(従来とバイト同一) / "dev"=開発確認用(player_dev.htmlへ出力。player.htmlを上書きしない)。
    highlights_by_level(SLOT-23): {level: resolve_x_highlights結果|None}。省略(None)=assemble済みlevelごとにresolve_x_highlightsで自動解決
    (display_spec無しのrun=全levelNone=従来とバイト同一)。ISSUEはHighlightStop(playerを作らない)。"""
    import er_user_listening_page_common_01 as _uc
    _uc.normalize_audience(audience)
    abs_url = player_common.abs_file_url
    b1b_summary = _load_assemble_summary(f"{theme_out_dir}/b1b/run_summary_assemble.json")
    a2_summary = _load_assemble_summary(f"{theme_out_dir}/a2/run_summary_assemble.json")

    _hres = dict(highlights_by_level) if highlights_by_level is not None else {}
    if highlights_by_level is None:   # SLOT-23: display_spec付きrun・assemble済みlevelだけ解決(無い=None=従来描画)
        for _lvh, _sm in (("b1b", b1b_summary), ("a2", a2_summary)):
            _hres[_lvh] = resolve_x_highlights(theme_out_dir, _lvh) if _sm.get("status") == "OK" else None

    b1b_audio_html = f'<h2>Advanced(B1)</h2><p style="color:#b00">status={b1b_summary.get("status")}</p>'
    if b1b_summary.get("status") == "OK":
        b1b_table = _add_seek_target(_build_level_table(f"{theme_out_dir}/b1b", "b1b", audience=audience, highlights=_hres.get("b1b")), "episode_audio_b1b")
        b1b_audio_html = (f'<h2>Advanced(B1)</h2>'
                           f'<audio id="episode_audio_b1b" class="main" controls preload="none" '
                           f'src="{abs_url(b1b_summary["out_path"])}"></audio>'
                           f'<p class="note">duration={b1b_summary["duration_seconds"]}s '
                           f'peak={b1b_summary["peak"]} clipping={b1b_summary["clipping_detected"]}</p>'
                           f'{b1b_table}')

    a2_audio_html = f'<h2>Standard(A2)</h2><p style="color:#b00">status={a2_summary.get("status")}</p>'
    if a2_summary.get("status") == "OK":
        a2_table = _add_seek_target(
            _build_level_table(f"{theme_out_dir}/a2", "a2", japanese_title, audience=audience, highlights=_hres.get("a2")), "episode_audio_a2")
        a2_audio_html = (f'<h2>Standard(A2)</h2>'
                          f'<audio id="episode_audio_a2" class="main" controls preload="none" '
                          f'src="{abs_url(a2_summary["out_path"])}"></audio>'
                          f'<p class="note">duration={a2_summary["duration_seconds"]}s '
                          f'peak={a2_summary["peak"]} clipping={a2_summary["clipping_detected"]}</p>'
                          f'{a2_table}')

    # AUW 委任_03: 事後試聴リスト(PASS_WITH_WARNING)節。0件でも節を出す(「0件」と明記)。非ブロッキング。
    pww_sections_html = chr(10).join(
        f"<h3>{lvl_label}</h3>" + pww_registry.render_html_section(
            pww_registry.load_listening_list(f"{theme_out_dir}/{lvl_dir}"), href_fn=lambda e: abs_url(e["audio_path"]) if e.get("audio_path") else "")
        for lvl_dir, lvl_label in (("b1b", "Advanced(B1)"), ("a2", "Standard(A2)")))

    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>{MANAGEMENT_ID} player({theme_id})</title>
<style>
{PLAYER_CSS_WITH_HIGHLIGHT if any(_hres.get(_k) is not None for _k in ("b1b", "a2")) else player_common.PLAYER_STANDARD_CSS}
</style>
<script>
{_TWO_LEVEL_SEEK_SCRIPT}
</script>
</head><body>
<h1>{MANAGEMENT_ID}({theme_id})</h1>
<p class="note">Family X(Entertainment News)音声構造Stage 3a runtime。
Comment1→本文1→Comment2→本文2→Comment3→本文3→Comment4→In One Line(Point構造なし)。</p>
{b1b_audio_html}{study_html}
{a2_audio_html}{study_html_a2}
{pww_sections_html}
</body></html>
"""
    out_path = f"{theme_out_dir}/player.html" if audience == _uc.AUDIENCE_PUBLIC else f"{theme_out_dir}/player_dev.html"
    if audience == _uc.AUDIENCE_PUBLIC and _uc.count_chunk_markers(html):
        raise RuntimeError("FAMILY_X_PUBLIC_PLAYER_HAS_CHUNK_MARKER: 公開用playerに開発用Chunk境界マーカーがあります(出力しない)")
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
                         choices=("plan", "scaffold", "study_text", "tts", "assemble", "player", "all"))
    parser.add_argument("--page-audience", default="public", choices=("public", "dev"),
                         help="player stageの表示対象(委任_08)。public(既定)=Chunk境界マーカーなしのplayer.html。dev=開発確認用player_dev.htmlのみ実TTS Chunk境界に⏸を表示。")
    parser.add_argument("--dry-run", action="store_true",
                         help="API呼び出しを一切行わずplanのみ出力する(--stage plan相当を強制)。")
    parser.add_argument("--out-dir", default=None,
                         help="既定: er019_output/family_x_audio_production_wiring_01/<slug>__<run>")
    parser.add_argument("--budget-jpy", type=float, default=150.0,
                         help="scaffold/tts stage後のBudget Guard上限(既定150円、超過でRuntimeError)。")
    # TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-01/02(既定
    # "structured_separation"=現行モデル、既存挙動と完全に同一): SDK
    # 2.25.0はProduction `.venv`へ導入済み(FAMILY-X-01 Phase 2、
    # 2026-09-28)のため、speech_metadata_flash_lite指定時は実際に
    # Flash-Liteで生成される(Gate 3の16項目は全16件完了済み、
    # `PRODUCTION_WIRED`化はOpus L2レビュー後にFableが判定)。
    # 委任_02A(Opus条件A R-07、2026-10-16): Family Xの承認済みbackend(flash-lite統一)を既定にする。
    # 既定がlegacyだと、CLI指定忘れで承認済みprofile(fx_20261016)が適用されず(source=default_no_record_legacy_backend)
    # tts stageは課金前STOPになる、という「指定忘れ」事故を構造的に防ぐ(ユーザー指示§4)。legacy backend(Trial/regression)は
    # `--tts-backend structured_separation --allow-legacy-backend`の明示指定が必要。assert_production_tts_backend等のfail-closedは不変。
    parser.add_argument("--tts-backend", default=FAMILY_X_APPROVED_PRODUCTION_TTS_BACKEND,
                         choices=("structured_separation", "speech_metadata_flash_lite"),
                         help="既定speech_metadata_flash_lite(承認済み正式backend、2026-10-16以降)。"
                              "structured_separation(旧gemini-2.5-pro-preview-tts/3.1-flash-tts-preview、Trial/regression用)は"
                              "--allow-legacy-backendとの併用が必要。speech_metadata_flash_lite指定時は"
                              "gemini-3.8-flash-lite-ttsのspeech_metadata方式(Family X、"
                              "主記事segment+Key Phrase[共有narration含む]の両方が対象、"
                              "FAMILY-X-02のユーザー確定仕様CでKey Phraseも統一)。")
    # W5(Opus L2所見MAJOR-3是正、2026-09-29): E2E Production実行は
    # --tts-backend speech_metadata_flash_lite(承認済み正式backend)が
    # 必須。CLIフラグ1個の抜けで legacy backend のまま tts stage が
    # 走ると、¥150〜250を無駄にした上「どの承認仕様にも一致しない
    # 半新規episode」が全Gateを通過してしまう実害があった。legacy
    # backendはTrial/regression用途のみ、この明示flagがある場合に限り
    # 許可する(既存テスト互換のため)。
    parser.add_argument("--allow-legacy-backend", action="store_true",
                         help="tts_backend=structured_separation(承認済み正式backend以外)での"
                              "tts stage実行を明示的に許可する(Trial/regression用途のみ、"
                              "Production E2Eでは使用しないこと)。")
    # OPEN-300(FAMILY-X-COFFEE-P8-FINAL-AUDIO-AND-PRODUCTION-WIRING-01 委任_02): 既定None
    # (未指定)。未指定で固定記録(audit/style_profile.json)が無ければ"default"(現行とバイト同一、
    # 新key/fileを書かない)、記録があれば記録を採用(resume)。coffee_p8は新しいout_dirでのみ実行可
    # (M2)、speech_metadata_flash_lite backend必須(M5)。
    parser.add_argument("--style-profile", default=None, choices=tuple(style_profile_mod.STYLE_PROFILES),
                         help="Style profile。未指定: 記録があれば記録を採用(resume)、記録も既存run stateもない新規out_dirは"
                              "fx_20261017(承認済み6仕様: Full Story=PD06/Std Preview・Comment=S3[2026-10-17正式採用、旧R2]/Adv Preview=E1/Adv KP解説=P7/"
                              "KP英語=K2/Std KP日本語意味=P8-KP、2026-10-17以降の既定。fx_20261016[Std日本語=R2]は既存runのresume互換のみ)、既存run stateがある"
                              "out_dirは課金前にSTOP(従来styleでresumeするなら`--style-profile default`を明示)。"
                              "coffee_p8=Coffee限定P8置換、coffee_n01_r2_p3=N01+R2+P3(Coffee用)。")
    # FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01(Opus Q5): KPだけを再生成する最小CLI。--stage scaffold専用。
    parser.add_argument("--kp-review", default=None, choices=("wait", "auto"),
                         help="KP Human Review。既定(指定なし)=待機(Humanの選択か明示の不在宣言が必要。rc=4)。auto=このrunについて不在を明示宣言する"
                              "(要 --kp-review-by/--kp-review-reason。AIが宣言する場合は --kp-review-user-ref 必須)。")
    parser.add_argument("--kp-review-by", default=None)
    parser.add_argument("--kp-review-reason", default=None)
    parser.add_argument("--kp-review-user-ref", default="")
    parser.add_argument("--scaffold-only", default=None, choices=("kp",),
                         help="kp: scaffold stageでKey Phrase(M2P0)のみ再生成する(Preview/Comment等のsupport文面は"
                              "再生成しない。support成果物がout_dirに無ければSTOP、KP再生成は1レベル1回)。--stage scaffold専用。")
    # FAMILY-X-COFFEE-FINAL-V5-PRODUCTION-WIRING-01: 必要なsegmentだけを生成する(既定None=全segment、従来と同一)。
    # 例: --only-segments preview,comment_1,comment_4 / kp1_explanation,kp2_explanation。
    # tts stage専用(assemble/all/playerとの併用は拒否)。対象外はstatus=SKIPPED_NOT_SELECTEDとして記録され、
    # Audio Validation GateがAssemblyを止める。
    parser.add_argument("--regenerate-support", default=None, choices=("comment_3",),
                         help="comment_3: 既存a2_support_texts.jsonのComment 3だけをZ方式で再生成する(Opus M-3)。--stage scaffold --level a2専用。"
                              "他4キー(preview/comment_1/2/4)・KP・Part 2・study_textは不変(shaをassert)。TTSは続けて--stage tts --only-segments comment_3。")
    parser.add_argument("--only-segments", default=None,
                         help="カンマ区切りのsegment名(例: preview,comment_1 / kp1_explanation)。tts stage専用。")
    return parser


# W5(Opus L2所見MAJOR-3是正): tts stage開始前のbackend fail-fast Gate。
# (定数本体はbuild_arg_parserが既定値に使うため、上方[ファイル前方]で定義済み)


def assert_production_tts_backend(tts_backend: str, allow_legacy_backend: bool) -> None:
    """tts stage(実際の課金が発生する処理)を開始する前に、承認済み正式
    backend(speech_metadata_flash_lite)であることを確認する。legacy
    backend(structured_separation、既定値)はTrial/regression用途の
    明示opt-in(--allow-legacy-backend)がある場合のみ許可する。これに
    よりCLIフラグ1個の抜けで「どの承認仕様にも一致しない半新規episode」
    が全Gateを通過してしまう事故(Opus L2所見MAJOR-3)を防ぐ。"""
    if tts_backend == FAMILY_X_APPROVED_PRODUCTION_TTS_BACKEND:
        return
    if allow_legacy_backend:
        return
    raise RuntimeError(
        f"[STOP][MAJOR-3] tts_backend={tts_backend!r}は、Production E2Eの承認済み"
        f"正式backend({FAMILY_X_APPROVED_PRODUCTION_TTS_BACKEND!r})ではありません。"
        "legacy backendを意図的に使う場合(Trial/regression用途のみ)は"
        "--allow-legacy-backendを明示してください。tts stageは実行していません"
        "(課金前にSTOPしました)。")


# ------------------------------------------------------------
# C3-1: TTS直前のRisk Flagger保険(RISK-FLAGGER-PRODUCTION-WIRING-01, DESIGN_03 4-2/15-2 #8)
# 三者sha照合 = (1) scaffold時に記録した元記事sha256 (2) 現在のsource記事(source_dir/<level>/article.md)のsha256
#              (3) Review Queue上の(article_id, level, article_sha256)。
# 三者が一致しない、または該当Queueが無い場合は、その場でRisk Flaggerを実行(非Blocking、Level明示、
# producer/run_label記録)してからTTSへ進む。RF_UNAVAILABLE/PARTIAL/Queue保存失敗でもTTSは止めない。
# 例外として伝播するのは予算超過STOP(rf.BudgetCheckStop)と記事sha変化(rf.ArticleModifiedError)のみ。
# ------------------------------------------------------------
SCAFFOLD_SHA_RECORD = "audit/scaffold_article_sha256.json"
RF_TTS_GUARD_RECORD = "audit/rf_tts_guard.json"


def file_sha256(path: str) -> str:
    """Review Queue(rf module)と同じ定義: ファイルのraw bytesのsha256。"""
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def record_scaffold_article_sha(out_dir: str, level: str, article_path: str) -> str:
    """scaffold時の元記事sha256を out_dir/audit/scaffold_article_sha256.json の [level] へ記録(既存levelは保持)。"""
    p = f"{out_dir}/{SCAFFOLD_SHA_RECORD}"
    data = load_json(p) if os.path.exists(p) else {}
    sha = file_sha256(article_path)
    data[level] = {"article_sha256": sha, "article_path": article_path}
    save_json(p, data)
    return sha


def _read_scaffold_sha(out_dir: str, level: str):
    p = f"{out_dir}/{SCAFFOLD_SHA_RECORD}"
    if not os.path.exists(p):
        return None
    try:
        return (load_json(p).get(level) or {}).get("article_sha256")
    except (OSError, ValueError):
        return None


def _queue_shas(source_dir: str, article_id: str, level: str, queue_root: str) -> set:
    """Review Queue(index.jsonl)と、Queue保存失敗時のfallback(source_dir/risk_flagger_fallback/<level>__*/queue.json)上の
    (article_id, level)に対応するarticle_sha256の集合。"""
    shas = set()
    try:
        for e in rq.read_index(queue_root):
            if e.get("article_id") == article_id and e.get("article_level") == level and e.get("article_sha256"):
                shas.add(e["article_sha256"])
    except (OSError, ValueError):
        pass
    fb_root = f"{source_dir}/risk_flagger_fallback"
    if os.path.isdir(fb_root):
        for name in os.listdir(fb_root):
            qp = os.path.join(fb_root, name, "queue.json")
            try:
                if name.startswith(f"{rq.safe_component(level)}__") and os.path.exists(qp):
                    q = load_json(qp)
                    if q.get("article_id") == article_id and q.get("article_level") == level and q.get("article_sha256"):
                        shas.add(q["article_sha256"])
            except (OSError, ValueError):
                pass
    return shas


def _derived_sha_warning(source_dir: str, level: str):
    """S3-2: a2の派生元(b1b)sha不一致は警告記録のみ(判定・STOPに使わない)。"""
    if level != "a2":
        return None
    p = f"{source_dir}/a2/audit/derived_from_advanced_sha256.json"
    b1b = f"{source_dir}/b1b/article.md"
    if not (os.path.exists(p) and os.path.exists(b1b)):
        return None
    try:
        recorded = load_json(p).get("derived_from_advanced_sha256")
        now = file_sha256(b1b)
    except (OSError, ValueError):
        return None
    if recorded and recorded != now:
        return {"warning": "a2_derived_from_advanced_sha_mismatch(観測のみ)", "recorded": recorded, "current_b1b": now}
    return None


def _annotation_producer(source_dir: str):
    try:
        return load_json(f"{source_dir}/ja_writer/runtime_evidence.json").get("annotation_manifest_producer")
    except (OSError, ValueError):
        return None


def ensure_rf_record(source_dir: str, out_dir: str, level: str, budget_jpy: float, run_label: str | None = None,
                     queue_root: str | None = None, rf_runner=None) -> dict:
    """TTS直前の三者sha照合。一致ならRF実行なし(action=verified)、不一致/Queueなしならその場でRF+Queue保存(action=rf_executed)。
    rf_runner: test用差し替え(既定 rf.run_risk_flagger)。戻り値は out_dir/audit/rf_tts_guard.json の [level] にも記録。"""
    assert level in ("a2", "b1b"), level
    queue_root = queue_root or rq.QUEUE_ROOT          # 呼出時に解決(test/運用でQUEUE_ROOTを差し替え可能)
    article_path = f"{source_dir}/{level}/article.md"
    article_id = rq.derive_article_id(source_dir)
    src_sha = file_sha256(article_path)
    scaffold_sha = _read_scaffold_sha(out_dir, level)
    queue_shas = _queue_shas(source_dir, article_id, level, queue_root)
    reasons = []
    if scaffold_sha is None:
        reasons.append("scaffold_sha_missing")
    elif scaffold_sha != src_sha:
        reasons.append("scaffold_sha_ne_source_sha")
    if not queue_shas:
        reasons.append("no_queue_record")
    elif src_sha not in queue_shas:
        reasons.append("source_sha_ne_queue_sha")
    rec = {"level": level, "article_id": article_id, "scaffold_sha256": scaffold_sha, "source_sha256": src_sha,
           "queue_shas": sorted(queue_shas), "match": not reasons, "mismatch_reasons": reasons,
           "action": "verified", "rf_status": None, "queue_saved": None, "warnings": []}
    w = _derived_sha_warning(source_dir, level)
    if w:
        rec["warnings"].append(w)
        print(f"[FAMILY-X-AUDIO-RUNNER][WARN] {level}: {w['warning']}(警告記録のみ)")
    if not reasons:
        print(f"[FAMILY-X-AUDIO-RUNNER][rf_guard] {level}: 三者sha一致(scaffold == source == Queue)。RF再実行なし。")
    else:
        rec["action"] = "rf_executed"
        print(f"[FAMILY-X-AUDIO-RUNNER][rf_guard] {level}: 三者sha不一致/Queueなし({','.join(reasons)})。"
              "TTS前にRisk Flaggerを実行します(非Blocking)。")
        runner_fn = rf_runner or rf.run_risk_flagger
        label = f"audio_tts_guard:{run_label}" if run_label else "audio_tts_guard"
        try:
            result = runner_fn(
                article_path=article_path, ledger_path=f"{source_dir}/research_ledger/verified_fact_ledger.txt",
                article_id=article_id, article_level=level, out_dir=out_dir, producer=_annotation_producer(source_dir),
                run_label=label, budget_check=lambda: assert_budget_ok(out_dir, budget_jpy, f"rf_guard {level}"))
            saved = rq.save_queue(result, out_dir=out_dir, root=queue_root)
            rec.update(rf_status=result.get("status"), rf_reason=result.get("reason"), rf_run_id=result.get("rf_run_id"),
                       queue_saved=saved.get("saved"), run_label=label, issue_count=len(result.get("issues", [])))
        except (rf.BudgetCheckStop, rf.ArticleModifiedError):
            raise
        except Exception as exc:  # noqa: BLE001 - 非Blocking: RF側の想定外もRF_UNAVAILABLEとして可視化しTTSへ進む
            rec.update(rf_status="RF_UNAVAILABLE", rf_reason=f"audio_wrapper_exception: {type(exc).__name__}", run_label=label)
            print(f"[WARN][RF] {level}: 想定外の例外 {type(exc).__name__}: {str(exc)[:200]}(非Blocking: TTSへ進みます)")
        if file_sha256(article_path) != src_sha:
            raise rf.ArticleModifiedError(f"article sha changed across RF in audio guard: {article_path}")
    p = f"{out_dir}/{RF_TTS_GUARD_RECORD}"
    data = load_json(p) if os.path.exists(p) else {}
    data[level] = rec
    save_json(p, data)
    return rec


def print_gloss_hr_final_line(out_dir: str, levels: list | None = None) -> str:
    """委任_02(「届いた」条件③): runner終了時の最終stdoutに、gloss再整合のHuman Review待ちを専用1行で明示する。
    判定基準=ディスク上のartifactのcollect_unresolved(OF-KGCPW-05。報告書ファイルの有無ではない=resolve後に誤報しない)。
    HR待ちが無ければ何も出さず空文字。報告書pathは履歴として併記。"""
    import glob as _glob
    _ga = _gloss_align_mod()
    hr_levels = _gloss_hr_levels_from_artifacts(out_dir, levels)
    if not hr_levels:
        return ""
    events = []
    _sum_path = f"{out_dir}/scaffold_run_summary.json"
    if os.path.exists(_sum_path):
        with open(_sum_path, encoding="utf-8") as _f:
            _sum = json.load(_f)
        events = [ev for lv in _sum.values() if isinstance(lv, dict)
                  for ev in (lv.get("gloss_alignment_human_review_events") or [])]
    reports = sorted(_glob.glob(f"{out_dir}/*/key_phrases/{_ga.HR_REPORT_MD}"))
    line = (f"[GLOSS-ALIGN][HUMAN-REVIEW-REQUIRED][FINAL] levels={hr_levels} events={len(events)} reports={reports} "
            "gloss再整合が成立せず対象levelのKP segment/完成を停止中です。ユーザーへ必ず報告してください。")
    print(line)
    return line


MIGRATE_MANAGED_ID = "FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01"


def _maybe_migrate_style_profile_record(argv: list) -> bool:
    """`--migrate-style-profile-record`が指定された場合のみ、固定記録を上位集合profileへ1回限り移行して終了する
    (API呼出なし・生成なし)。M2(既存run stateありで新規記録禁止)の唯一の例外で、監査記録を必須とする。"""
    if "--migrate-style-profile-record" not in argv:
        return False
    mp = argparse.ArgumentParser(add_help=False)
    mp.add_argument("--migrate-style-profile-record", action="store_true")
    mp.add_argument("--out-dir", required=True)
    mp.add_argument("--from", dest="migrate_from", required=True)
    mp.add_argument("--to", dest="migrate_to", required=True)
    mp.add_argument("--reason", required=True)
    mp.add_argument("--managed-id", default=MIGRATE_MANAGED_ID)
    margs, _unknown = mp.parse_known_args(argv)
    rec = style_profile_mod.migrate_record(margs.out_dir, margs.migrate_from, margs.migrate_to,
                                           margs.reason, margs.managed_id)
    print(f"[STYLE-PROFILE][MIGRATED] {margs.migrate_from} -> {margs.migrate_to} "
          f"added_roles={rec['migration']['added_roles']} archived={rec['migration']['archived_old_record']}")
    return True


def main() -> None:
    if _maybe_migrate_style_profile_record(sys.argv[1:]):
        return
    parser = build_arg_parser()
    args = parser.parse_args()

    global _ONLY_SEGMENTS
    if args.only_segments is not None:
        _sel, _err = validate_only_segments_args(args.stage, args.dry_run, args.level, args.only_segments)
        if _err:
            parser.error(_err)
        _ONLY_SEGMENTS = _sel

    if args.scaffold_only is not None and args.stage != "scaffold":
        parser.error("--scaffold-onlyは--stage scaffoldでのみ使えます。")
    if args.regenerate_support is not None and (args.stage != "scaffold" or args.level != "a2" or args.scaffold_only is not None
                                                or args.dry_run):
        parser.error("--regenerate-supportは--stage scaffold --level a2(--dry-run/--scaffold-onlyなし)でのみ使えます。")
    if args.kp_review == "auto" and not (args.kp_review_by and args.kp_review_reason):
        parser.error("--kp-review auto には --kp-review-by と --kp-review-reason が必要です(自動確定は明示宣言のみ)。")
    source_dir = f"er019_output/{args.slug}/{args.run}"
    out_dir = derive_out_dir(args.slug, args.run, args.out_dir)
    # OPEN-300: style profileは課金・ファイル作成前に決定する。M5(backend)→M2/固定記録の順で、
    # いずれかでSTOPした場合はout_dir/記録を作らない。
    _profile_id, _profile_source = style_profile_mod.resolve_run_profile(
        out_dir, args.style_profile, write=False, tts_backend=args.tts_backend)
    style_profile_mod.assert_profile_backend(_profile_id, args.tts_backend)
    _profile_id, _profile_source = style_profile_mod.resolve_run_profile(
        out_dir, args.style_profile, write=True, tts_backend=args.tts_backend)
    # R-07: 旧profileでresume中/legacy backendで承認済みprofile未適用、を目立たせる(CLI指定を忘れた場合の気付き用、非機能)。
    _profile_warn = style_profile_mod.profile_resolution_warning(_profile_id, _profile_source)
    if _profile_warn:
        print(_profile_warn)
    os.makedirs(out_dir, exist_ok=True)

    levels = ["a2", "b1b"] if args.level == "both" else [args.level]

    ja_title_info = derive_japanese_title(source_dir)
    japanese_title = ja_title_info["japanese_title"]
    if "a2" in levels and not japanese_title:
        print(f"[FAMILY-X-AUDIO-RUNNER][WARN] japanese_titleが取得できませんでした"
              f"(source_dir={source_dir}/ja_writer 不在)。A2のJapanese title segmentは"
              f"英語placeholderのまま生成されるため、実行前に要確認。")

    # OF-KGCPW-11: gloss再整合の実効flag(ON/OFFと取得元)をrun開始時にstdoutとentry_point/summaryへ記録する。
    _gloss_flag_effective = _gloss_align_mod().announce_flag()
    save_json(f"{out_dir}/entry_point.json", {
        "gloss_alignment_flag": _gloss_flag_effective,
        "runner": "er019_family_x_audio_production_runner_01.py",
        "management_id": MANAGEMENT_ID, "slug": args.slug, "run": args.run,
        "source_dir": source_dir, "levels": levels, "stage": args.stage, "dry_run": args.dry_run,
        "japanese_title": japanese_title, "japanese_title_source": ja_title_info["source"],
        "budget_jpy": args.budget_jpy,
        # TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-01/02: 実際に
        # 使われたTTS backend(既定structured_separation)をrun全体の
        # traceabilityとして記録する(N-10是正、2026-09-28: FAMILY-X-02
        # 以降はKey Phrase[共有narration含む]も同じbackendへ統一される、
        # 「Key PhraseはPhase 1範囲外につき常にstructured_separation」は
        # 過去の一時的な設計判断でありもう成立しない)。
        "tts_backend": args.tts_backend,
        # W5(MAJOR-3是正): legacy backend実行を明示許可したかどうかの記録。
        "allow_legacy_backend": args.allow_legacy_backend,
        # S3: defaultでは新keyを書かない(entry_point.jsonもバイト同一の構造)。
        **({"style_profile": _profile_id, "style_profile_source": _profile_source}
           if _profile_id != style_profile_mod.PROFILE_DEFAULT else {}),
        **({"only_segments": sorted(_ONLY_SEGMENTS)} if _ONLY_SEGMENTS is not None else {}),
        **({"scaffold_only": args.scaffold_only} if args.scaffold_only else {}),
    })

    if args.dry_run or args.stage == "plan":
        result = run_plan_stage(source_dir, out_dir, levels, style_profile=_profile_id)
        save_json(f"{out_dir}/plan_run_result.json", result)
        print(f"[FAMILY-X-AUDIO-RUNNER] plan完了(API呼び出しゼロ円)。out_dir={out_dir}")
        for level, r in result.items():
            print(f"  {level}: status={r.get('status')}")
        return

    # scaffold/tts/assemble stageは実API呼び出しを伴う(Stage 1では
    # 呼び出さない。Stage 2以降で本CLIから--stage scaffold等を実行する)。
    # cost loggerのinstall/raw_usage_log.jsonl作成もこの分岐以降のみ行う
    # (--dry-run/--stage planは常に¥0・副作用ゼロを維持する既存契約を保つ)。
    try:
        cl.install(f"{out_dir}/raw_usage_log.jsonl")
        import er003_v1_en_direct_vfl_01_generate as vfl01
        client = vfl01.get_client()
        if args.kp_review == "auto":   # 明示引数のときだけ宣言を記録する(宣言ファイルが自動確定の唯一の読取元)
            try:
                _kpw().declare_from_runner_args(out_dir, by=args.kp_review_by, reason=args.kp_review_reason, user_ref=args.kp_review_user_ref)
            except _khr().KpReviewError as exc:
                print(f"[FAMILY-X-AUDIO-RUNNER][STOP] {exc}")
                sys.exit(3)

        if args.regenerate_support == "comment_3":
            with cl.logging_context(args.slug, "scaffold"):
                _rg = run_regenerate_support_comment3(
                    client, source_dir, out_dir, budget_check=lambda note: assert_budget_ok(out_dir, args.budget_jpy, note))
            assert_budget_ok(out_dir, args.budget_jpy, "after regenerate-support comment_3")
            if _rg["status"] != "OK":
                print(f"[FAMILY-X-AUDIO-RUNNER][STOP] {_rg['status']}: Comment 3再生成に失敗(a2_support_texts.jsonは変更していません)。")
                sys.exit(3)
            print("[FAMILY-X-AUDIO-RUNNER] Comment 3再生成OK。次: --stage tts --level a2 --only-segments comment_3")
            return
        if args.stage in ("scaffold", "all"):
            with cl.logging_context(args.slug, "scaffold"):
                scaffold_result = run_theme_scaffold(
                    client, source_dir, out_dir, levels, scaffold_only=args.scaffold_only,
                    budget_check=lambda note: assert_budget_ok(out_dir, args.budget_jpy, note))
            assert_budget_ok(out_dir, args.budget_jpy, "after scaffold")
            _sup_fail = {lv: (scaffold_result.get(lv) or {}).get("support_stage_status") for lv in levels
                         if (scaffold_result.get(lv) or {}).get("support_stage_status")}
            if _sup_fail:   # Opus M-2(c): Comment 3 fail-closed。rc=3、entry_pointへ記録、KP/Part/TTSへ進まない
                _ep = f"{out_dir}/entry_point.json"
                if os.path.exists(_ep):
                    with open(_ep, encoding="utf-8") as f:
                        _epd = json.load(f)
                    _epd["support_stage_status"] = _sup_fail
                    save_json(_ep, _epd)
                print(f"[FAMILY-X-AUDIO-RUNNER][STOP] {_sup_fail}: A2 Comment 3(Z方式)が先取りlint等でfail-closed。KP/Part 1/2/TTSは未実行。"
                      "次の一手: 同じ--stage scaffoldコマンドを再実行(KP未実施なのでsupportから再生成されます。却下文はaudit/a2_support_generation.json)。")
                sys.exit(3)
            _kp_fail = {lv: (scaffold_result.get(lv) or {}).get("kp_stage_status") for lv in levels
                        if (scaffold_result.get(lv) or {}).get("kp_stage_status")}
            if _kp_fail:   # fail-closed(KPMP-03 委任_03): rc=3。entry_pointへStatus記録、後段(tts/assemble/player)へ進まない
                _ep = f"{out_dir}/entry_point.json"
                if os.path.exists(_ep):
                    with open(_ep, encoding="utf-8") as f:
                        _epd = json.load(f)
                    _epd["kp_stage_status"] = _kp_fail
                    save_json(_ep, _epd)
                print(f"[FAMILY-X-AUDIO-RUNNER][STOP] {_kp_fail}: KP stage fail-closed(技術STOP、HR Lockへ送らない)。"
                      "原因確認後に同stageを再実行してください。")
                sys.exit(3)
            _p1_fail = {lv: (scaffold_result.get(lv) or {}).get("part1_stage_status") for lv in levels
                        if (scaffold_result.get(lv) or {}).get("part1_stage_status")}
            if _p1_fail:   # 委任_14 Opus M1: Part 1失敗はKP失敗と分離(専用marker kp_part1_failed.json)。rc=3、案内は--stage study_text
                _ep = f"{out_dir}/entry_point.json"
                if os.path.exists(_ep):
                    with open(_ep, encoding="utf-8") as f:
                        _epd = json.load(f)
                    _epd["part1_stage_status"] = _p1_fail
                    save_json(_ep, _epd)
                print(f"[FAMILY-X-AUDIO-RUNNER][STOP] {_p1_fail}: 学習テキスト Part 1の生成に失敗(KPは確定済み・TTS前に停止)。"
                      f"次の一手: {part1_next_command(source_dir, next(iter(_p1_fail)))}。scaffold stageの再実行はしないでください(support/KPが再生成され費用・別KPになります)。")
                sys.exit(3)
            _p2_fail = {lv: (scaffold_result.get(lv) or {}).get("part2_stage_status") for lv in levels
                        if (scaffold_result.get(lv) or {}).get("part2_stage_status")}
            if _p2_fail:   # Part 2(文法)の失敗はKP・Part 1の失敗と分離(専用marker part2_failed.json)。rc=3、案内は--stage study_text
                _ep = f"{out_dir}/entry_point.json"
                if os.path.exists(_ep):
                    with open(_ep, encoding="utf-8") as f:
                        _epd = json.load(f)
                    _epd["part2_stage_status"] = _p2_fail
                    save_json(_ep, _epd)
                print(f"[FAMILY-X-AUDIO-RUNNER][STOP] {_p2_fail}: 学習テキスト Part 2(文法)の生成に失敗(TTS前に停止)。"
                      f"次の一手: {(scaffold_result.get(next(iter(_p2_fail))) or {}).get('part2_next_command') or part2_next_command(source_dir, next(iter(_p2_fail)))}。"
                      "support/KPの発注後に止まった場合はscaffold stageの再実行はしないでください(support/KPが再生成され費用・別KPになります)。")
                sys.exit(3)
            _kp_pending = {lv: (scaffold_result.get(lv) or {}).get("kp_review_pending") for lv in levels
                           if (scaffold_result.get(lv) or {}).get("kp_review_state") == "PENDING"}
            _p2_pend = [(scaffold_result.get(lv) or {}).get("part2_pending") for lv in levels if (scaffold_result.get(lv) or {}).get("part2_pending")]
            if _kp_pending or _p2_pend:   # Human Review待ち(KP・文法。失敗ではない)。rc=4を1回。候補は生成済み。再開は同じコマンドを1つだけ再実行(support/選定/抽出は再生成されない)
                _ep = f"{out_dir}/entry_point.json"
                if os.path.exists(_ep):
                    with open(_ep, encoding="utf-8") as f:
                        _epd = json.load(f)
                    _epd["kp_review_status"] = {lv: "PENDING_REVIEW" for lv in _kp_pending}
                    if _p2_pend:
                        _epd["part2_review_status"] = _p2_pend[0].get("status")
                    save_json(_ep, _epd)
                print(_kpw().pending_banner(list(_kp_pending.values()) + _p2_pend, restart_command="py " + " ".join(sys.argv), run_dir=out_dir))
                sys.exit(_khr().EXIT_CODE_PENDING)
            # 修正1回目(Opus L2所見B2、2026-09-27): scaffold完了後、
            # entry_point.jsonへlevelごとのkp_backend_usedを追記する
            # (per-article traceability、既存フィールドは保持したまま追加)。
            entry_point_path = f"{out_dir}/entry_point.json"
            if os.path.exists(entry_point_path):
                with open(entry_point_path, encoding="utf-8") as f:
                    entry_point = json.load(f)
                entry_point["kp_backend_used_by_level"] = {
                    level: (scaffold_result.get(level) or {}).get("kp_backend_used") for level in levels
                }
                save_json(entry_point_path, entry_point)

        _p2_pend_now = []
        if args.stage == "study_text":
            # Part 2: 候補抽出+解説の事前生成は両level(--levelで選ばれたもの)で行う。KP成功を前提にしない(KPの確定待ち/KP markerがあっても抽出・待機の評価は行う)。resumeはAPI 0。
            for _lv in levels:
                _p2c_now = run_part2_candidates_x(client, source_dir, out_dir, level=_lv, budget_check=lambda note: assert_budget_ok(out_dir, args.budget_jpy, note))
                if _p2c_now["status"] != "OK":
                    print(f"[FAMILY-X-AUDIO-RUNNER][STOP] {_p2c_now['status']}: {_p2c_now.get('reason')}。次の一手: {_p2c_now.get('next_command') or part2_next_command(source_dir, _lv)}")
                    sys.exit(3)
                if _p2c_now["state"] == "PENDING":
                    _p2_pend_now.append(_p2c_now["pending"])
        if args.stage in ("study_text", "tts", "assemble", "player", "all"):
            # KP Human Review: 全consumerの入口で確定物の整合を確認する(未確定=待機rc=4 / 不整合・旧KP混入=STOP rc=3)。review無しの旧runは従来どおり。
            for _lv in levels:
                try:
                    _khr().require_final_consistent(f"{out_dir}/{_lv}/key_phrases", level=_lv)
                except _khr().KpReviewNotConfirmed as exc:
                    print(_kpw().pending_banner([{"level": _lv, "request_md": _khr().paths(f"{out_dir}/{_lv}/key_phrases")["request"]}] + _p2_pend_now,
                                                restart_command="py " + " ".join(sys.argv), run_dir=out_dir) + f"\n  詳細: {exc}")
                    sys.exit(_khr().EXIT_CODE_PENDING)
                except _khr().KpReviewInconsistent as exc:
                    print(f"[FAMILY-X-AUDIO-RUNNER][STOP] {exc}")
                    sys.exit(3)
        if args.stage == "study_text":
            # 委任_14 Opus M1: study_textだけを(再)生成する単独stage(KP再選定・support再生成なし)。Part 1(API=1 call以内)はAdvanced(b1b)のみ、
            # Part 2(文法)は両level(Standard=a2もAdvanced=b1bも。解説は候補抽出stageで事前生成済み=finalizeはLLM 0)。
            if _p2_pend_now:   # 文法のHuman確認待ち: Part 1(有料)へ進まず待機(rc=4)
                print(_kpw().pending_banner(_p2_pend_now, restart_command="py " + " ".join(sys.argv), run_dir=out_dir))
                sys.exit(_khr().EXIT_CODE_PENDING)
            for _lv1 in part1_levels(out_dir, levels):   # SLOT-23: Advanced、およびマーク付きStandard(マーク無しa2=従来どおりPart 1なし)
                try:
                    with cl.logging_context(args.slug, "kp_part1"):
                        _p1r = run_study_text_stage(client, source_dir, out_dir, level=_lv1,
                                                    budget_check=lambda note: assert_budget_ok(out_dir, args.budget_jpy, note))
                except RuntimeError as exc:
                    print(f"[FAMILY-X-AUDIO-RUNNER][STOP] {exc}")
                    sys.exit(3)
                assert_budget_ok(out_dir, args.budget_jpy, f"after study_text {_lv1}")
                if _p1r["status"] != "OK":
                    print(f"[FAMILY-X-AUDIO-RUNNER][STOP] {_p1r['status']}: {_p1r.get('reason')}。次の一手: 原因確認後に{part1_next_command(source_dir, _lv1)}を再実行。")
                    sys.exit(3)
                print(f"[FAMILY-X-AUDIO-RUNNER] study_text ({_lv1}) OK: {_p1r}")
            for _lv in levels:
                _p2f = run_part2_final_x(client, source_dir, out_dir, level=_lv, budget_check=lambda note: assert_budget_ok(out_dir, args.budget_jpy, note))
                assert_budget_ok(out_dir, args.budget_jpy, f"after study_text part2 {_lv}")
                if _p2f["status"] == "PART2_TRANSLATION_ISSUE":   # 失敗ではなく待機(rc=4)
                    print(_kpw().pending_banner([_p2f["pending"]], restart_command="py " + " ".join(sys.argv), run_dir=out_dir) + f"\n  詳細: {_p2f.get('reason')}")
                    sys.exit(_khr().EXIT_CODE_PENDING)
                if _p2f["status"] != "OK":
                    print(f"[FAMILY-X-AUDIO-RUNNER][STOP] {_p2f['status']}: {_p2f.get('reason')}。次の一手: {part2_next_command(source_dir, _lv)}")
                    sys.exit(3)
                print(f"[FAMILY-X-AUDIO-RUNNER] study_text Part 2 ({_lv}) OK: {_p2f}")

        if args.stage in ("tts", "assemble", "all"):
            _p2f_markers = _part2_failed_markers(out_dir, levels)
            if _p2f_markers:
                print(f"[FAMILY-X-AUDIO-RUNNER][STOP] PART2_FAILED markerあり(Part 2未生成のままTTSへ進まない): {_p2f_markers}。次の一手: {part2_next_command(source_dir, 'b1b' if 'b1b' in levels else levels[0])}")
                sys.exit(3)
            _kpf = _kp_stage_failed_markers(out_dir, levels)
            if _kpf:
                print(f"[FAMILY-X-AUDIO-RUNNER][STOP] KP_STAGE_FAILED markerあり(旧attemptのKPを後段で使わない): {_kpf}")
                sys.exit(3)
            _p1f = _part1_failed_markers(out_dir, levels)
            if _p1f:
                _p1f_lv = next(lv for lv in levels if f"{out_dir}/{lv}/key_phrases/{KP_PART1_FAILED_MARKER}" in _p1f)
                print(f"[FAMILY-X-AUDIO-RUNNER][STOP] KP_PART1_FAILED markerあり(Part 1未生成のままTTSへ進まない): {_p1f}。"
                      f"次の一手: {part1_next_command(source_dir, _p1f_lv)}")
                sys.exit(3)
        if args.stage in ("tts", "assemble", "player", "all") and part1_levels(out_dir, levels):
            # 委任_14 Opus M2: Part 1(Vocabulary & Expressions)の存在と最新性を、後段の入口でfail-closed確認する
            # (Part 1導入前のrun再開・KP変更後の再生成忘れでPart 1なし/古い解説のまま進めない)。SLOT-23: マーク付きStandardも対象。
            try:
                for _lv1 in part1_levels(out_dir, levels):
                    _require_part1_fresh_x(source_dir, out_dir, f"--stage {args.stage}", _lv1)
                    _require_part1_ja_fresh_x(source_dir, out_dir, f"--stage {args.stage}", _lv1)
            except RuntimeError as exc:
                print(f"[FAMILY-X-AUDIO-RUNNER][STOP] {exc}")
                sys.exit(3)
        if args.stage in ("tts", "assemble", "player", "all") and "b1b" in levels:
            # Part 2(文法)も同様に、存在・最新性・確定との一致をfail-closed確認(M-2)。未確定=rc=4待機、無い/古い=STOP rc=3
            # (tts/assemble入口はAdvancedのみ=従来どおり。Standardの文法はページ専用で音声の前提にしない。Standardはplayer入口で確認する)
            try:
                _require_part2_fresh_x(source_dir, out_dir, f"--stage {args.stage}", level="b1b")
            except _p2w().Part2NotConfirmed as exc:
                print(_kpw().pending_banner(exc.pending, restart_command="py " + " ".join(sys.argv), run_dir=out_dir) + f"\n  詳細: {exc}")
                sys.exit(_khr().EXIT_CODE_PENDING)
            except RuntimeError as exc:
                print(f"[FAMILY-X-AUDIO-RUNNER][STOP] {exc}")
                sys.exit(3)

        if args.stage in ("tts", "all"):
            # W5(Opus L2所見MAJOR-3是正): 課金が発生するTTS呼び出し(下の
            # generate_family_x_*_segments())の直前でbackendをfail-fastする。
            assert_production_tts_backend(args.tts_backend, args.allow_legacy_backend)
            # C3-1: TTS直前のRisk Flagger保険(三者sha照合。`--stage tts`単独でも抜けない)。RFは
            # cl.logging_contextの外で呼ぶ契約(RF moduleが条件ごとに自前でstage tagを張る)。
            # 非Blocking: RF_UNAVAILABLE/PARTIAL/Queue保存失敗でもTTSへ進む。
            for level in levels:
                ensure_rf_record(source_dir, out_dir, level, args.budget_jpy)
            with cl.logging_context(args.slug, "tts"):
                for level in levels:
                    if level == "b1b":
                        generate_family_x_b1_segments(out_dir, tts_backend=args.tts_backend, style_profile=_profile_id)
                    else:
                        # 日本語titleは実行時に決定したja_title_info(ja_writer正式path
                        # 由来)を使う(以前はa2/article.mdの英語titleをそのまま渡す
                        # placeholderだった、Stage 3aで判明したbugの最小修正)。
                        generate_family_x_a2_segments(
                            out_dir, japanese_title=japanese_title or "(japanese title unavailable)",
                            tts_backend=args.tts_backend, style_profile=_profile_id)
                    # Opus必須9: 全stage累計(KP/TTS/ASR/Azure、raw_usage_log.jsonlの全provider)をlevelごとにも確認する
                    # (既存の上限・Guardの意味は変えず、チェック頻度のみ増やす)。
                    assert_budget_ok(out_dir, args.budget_jpy, f"after tts {level}")
            assert_budget_ok(out_dir, args.budget_jpy, "after tts")

        if args.stage in ("assemble", "all"):
            for level in levels:
                # OF-KGCPW-19: gloss停止(EPISODE_BLOCKED_BY_GLOSS_ALIGNMENT)はlevel単位で捕捉し、健全なlevelは続行する。
                # HR levelはrun_summary_assemble.jsonへBLOCKED記録(既存のEPISODE_BLOCKED_BY_*形式)。rcは末尾で2。
                try:
                    if level == "b1b":
                        stage_assemble_family_x_b1(out_dir, args.slug, source_dir=source_dir)
                    else:
                        stage_assemble_family_x_a2(out_dir, args.slug, source_dir=source_dir)
                except RuntimeError as exc:
                    if not str(exc).startswith("EPISODE_BLOCKED_BY_GLOSS_ALIGNMENT"):
                        raise
                    save_json(f"{out_dir}/{level}/run_summary_assemble.json",
                              {"status": "EPISODE_BLOCKED_BY_GLOSS_ALIGNMENT", "reason": str(exc)})
                    print(f"[FAMILY-X-AUDIO-RUNNER][BLOCKED] {level}: {exc}")

        if args.stage in ("player", "all"):
            _study_html = ""
            _study_html_a2 = ""
            _part1_htmls = {}   # level -> Part 1 block(SLOT-23: Advanced、およびマーク付きStandard。訳欄の判断記録が無い間は空文字=従来とバイト同一)
            _p2_results = {}   # level -> Part 2結果(両levelの文法。player入口で存在・最新性・確定との一致を確認)
            for _lv1 in part1_levels(out_dir, levels):   # 委任_14: Part 1 study block
                try:
                    _part1_htmls[_lv1] = part1_study_html_for_player(source_dir, out_dir, level=_lv1)
                except RuntimeError as exc:
                    print(f"[FAMILY-X-AUDIO-RUNNER][STOP] {exc}")
                    sys.exit(3)
            _part1_html = _part1_htmls.get("b1b", "")
            for _lv in levels:
                # Part 2(文法): Advancedは Part 1ブロック直後、Standardは a2節に同じテンプレートで連結(R-1/R-2: 共通builder compose_page_html 1つだけ)
                try:
                    _p2_results[_lv] = _require_part2_fresh_x(source_dir, out_dir, "player", level=_lv)
                except _p2w().Part2NotConfirmed as exc:
                    print(_kpw().pending_banner(exc.pending, restart_command="py " + " ".join(sys.argv), run_dir=out_dir) + f"\n  詳細: {exc}")
                    sys.exit(_khr().EXIT_CODE_PENDING)
                except RuntimeError as exc:
                    print(f"[FAMILY-X-AUDIO-RUNNER][STOP] {exc}")
                    sys.exit(3)
            if "b1b" in _p2_results:
                _study_html = _p2w().compose_page_html(_part1_html, _p2_results["b1b"], nuance=_p2w().nuance_for_display(_part2_study_dir(out_dir, "b1b"), level="b1b"))
            if "a2" in _p2_results:
                _study_html_a2 = _p2w().compose_page_html(_part1_htmls.get("a2", ""), _p2_results["a2"], nuance=_p2w().nuance_for_display(_part2_study_dir(out_dir, "a2"), level="a2"))   # Part 1: マーク付きStandardのみ(遡及なし)。Part 1→Part 2→ニュアンス解説の順
            # SLOT-23: 本文ハイライト(display_spec付きrun・levelだけ。無い=None=従来バイト同一)。解決不能(ISSUE)はplayer生成前にSTOP(fail-closed)
            try:
                _hl_by_level = resolve_x_highlights_for_levels(out_dir, levels, source_dir=source_dir)
            except (HighlightStop, ValueError) as exc:
                print(f"[FAMILY-X-AUDIO-RUNNER][STOP] {exc}")
                sys.exit(3)
            player_path = build_player_html(out_dir, args.slug, japanese_title, study_html=_study_html, study_html_a2=_study_html_a2,
                                           audience=getattr(args, "page_audience", "public"), highlights_by_level=_hl_by_level)
            try:   # 表示有効(display_spec付き)levelのG3(装飾・③訳・本文不変・public混入)+Part 1ちょうど1個。マーク無しlevelは何もしない
                verify_x_player(out_dir, player_path, levels, _hl_by_level, audience=getattr(args, "page_audience", "public"))
            except (RuntimeError, ValueError) as exc:
                print(f"[FAMILY-X-AUDIO-RUNNER][STOP] {exc}")
                sys.exit(3)
            if _p2_results:   # R-3: 確定 <-> part2_result.json <-> study_text/*.md <-> player.html の**当該levelの節**の一致(節単位。不一致=STOP)
                with open(player_path, encoding="utf-8") as _pf:
                    _player_text = _pf.read()
                for _lv in _p2_results:
                    try:
                        _pp, _plabel = _part2_inputs_x(source_dir, _lv)
                        _p2w().verify_outputs(_part2_study_dir(out_dir, _lv), _pp, _plabel, level=_lv, next_command=part2_next_command(source_dir, _lv), where=f"player({_lv})",
                                              md_path=f"{_part2_study_dir(out_dir, _lv)}/{_p2w().g.PART2_FILE_STEM}.md", html_text=player_level_section(_player_text, _lv))
                    except (_p2w().g.Part2Error, _p2w().g.Part2InputError, ValueError) as exc:
                        print(f"[FAMILY-X-AUDIO-RUNNER][STOP] PART2_OUTPUT_MISMATCH({_lv}): {exc}")
                        sys.exit(3)
            print(f"[FAMILY-X-AUDIO-RUNNER] player.html: {os.path.abspath(player_path)}")
            # 検証5(KP Human Review): 選定結果=実際に音声化・公開された内容(確定JSON<->KP artifact<->TTS結果<->study_text<->ページ)。不一致=STOP。
            for _lv in levels:
                _asm = f"{out_dir}/{_lv}/run_summary_assemble.json"
                _asm_ok = os.path.exists(_asm) and load_json(_asm).get("status") == "OK"
                _tts = f"{out_dir}/{_lv}/audit/tts_generation_results.json"
                try:
                    _khr().verify_selection_matches_outputs(
                        f"{out_dir}/{_lv}/key_phrases", level=_lv, tts_results_path=(_tts if os.path.exists(_tts) else None),
                        study_text_json=(f"{out_dir}/{_lv}/study_text/{_part1_gen().PART1_FILE_STEM}.json" if _lv in _part1_htmls else None),
                        page_paths=([player_path] if _asm_ok else None),
                        vocab_page_paths=([player_path] if _part1_htmls.get(_lv) else None))
                except _khr().KpReviewInconsistent as exc:
                    print(f"[FAMILY-X-AUDIO-RUNNER][STOP] {exc}")
                    sys.exit(3)

    finally:
        # OF-KGCPW-03: 例外(--stage allのEPISODE_BLOCKED等)で途中終了しても最終stdoutの1行を必ず出す(try/finally)。
        print_gloss_hr_final_line(out_dir, levels)
    final_jpy, by_provider = compute_cost_jpy_so_far(f"{out_dir}/raw_usage_log.jsonl")
    print(f"[FAMILY-X-AUDIO-RUNNER] stage={args.stage} 完了。out_dir={out_dir} "
          f"累計費用(JPY)={final_jpy:.2f} by_provider={by_provider}")
    # OF-KGCPW-04: いずれかのlevelにgloss HR未解決が残っていればrc=2(Zと一致)。
    if _gloss_hr_levels_from_artifacts(out_dir, levels):
        sys.exit(2)


if __name__ == "__main__":
    main()
