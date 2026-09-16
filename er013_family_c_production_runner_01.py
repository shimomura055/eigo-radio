# ============================================================
# er013_family_c_production_runner_01.py
# 管理ID: FAMILY-C-SEGMENT-COMMENT-PRODUCTION-WIRING-AND-USER-TEST-INVENTORY-01
#         (委任A: Family C 2仕様のProduction wiring / 差し戻し1回目)
# ============================================================
# 目的: `er013_family_c_production_01.py`(Family C Story TTS segmentation
# 原則+A2 Comment理解ガイド型Contract、APPROVED_FOR_PRODUCTION)を実際に
# 呼び出すFamily C正式Production runner。記事固有の設定(本文path・Voice
# keyword・scene boundary・Comment content等)はJSON設定ファイル
# (`er013_output/family_c_production/<article>/article_config.json`)から
# 読み、本runnerが固定値で上書きすることはない。
#
# モード:
#   --plan-only         : TTSなし。plan_story_segments()の結果のみ
#                         evidence/segmentation_plan_<level>.json へ出力する(¥0)。
#   --comments-only     : level="a2"のみ対応。A2 Comment理解ガイド型Contract
#                         (generate_family_c_a2_comment)経由でComment 1〜3を
#                         実際にLLM生成し、evidence/a2_comment_runtime_
#                         evidence.json へ保存する(LLM費用のみ、TTSなし)。
#                         level="b1"で指定された場合は構造的にRuntimeError
#                         とする(B1誤適用防止)。
#   (フラグなし)         : 全体生成経路(Story TTS→ASR整合→Comment→Assembly→
#                         Audio Validation Gate→player→web_delivery)。
#                         --resume(既定True)によりsha256一致segmentをskipし、
#                         --only-segments指定segmentのみ強制再生成する
#                         (regeneration)。
#
# 初回生成・retry・regeneration・fallback・resumeのいずれの呼び出し元からも
# `plan_story_segments()`と`generate_family_c_a2_comment()`
# (内部で`check_a2_comment_quality()`によるretryループを内包)という同一の
# Production関数を経由する。Story本文TTSは記事非依存の既存Production関数
# (`er003_v1_repro01_main_generate.generate_narration_snippet_verified_strict`
# [narrator]・`er003_v1_sing01_voice01_generate.generate_charon_english`
# [device系固定voice]・`er012_b_family_voices_production_01.
# generate_voice_body_wide_margin`[記事固有voice_name])を経由し、いずれも
# 内部にASR検証+retry cascadeを内包する(Trial-11/12で実際にVALIDATEDと
# 判定された既存呼び出しパターンをそのまま踏襲、新しいTTS cascade設計は
# 導入しない)。
#
# 本runnerを含む本ファイルはTrial script
# (`er013_family_c_episode_trial_1[012]_*.py`)を一切import・参照しない
# (Trial scriptの実装パターンは設計の参考にしたのみ)。
#
# スコープ外(本Wiring委任の対象外、明示的にエラーとする): Key Phrase選定・
# canonicalization等の記事固有content curation、および記事非依存
# shared nav asset(Welcome/Preview intro等)が既存Production共有資産にも
# reuse_fromにも存在しない場合のfrom-scratch音声生成。これらはStory TTS
# segmentation・A2 Comment Contractのwiringとは別の既存content-authoring
# 工程の管轄であり、本委任(2-A/2-B)の対象ではない。
# ============================================================
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import time

import numpy as np

import er002_common as common
import er003_b1_p9a_audio as p9a
import er003_v1_n3_01_assemble as assemble_mod
import er003_v1_repro01_main_generate as repro01
import er003_v1_sing01_voice01_generate as voice01
import er005_cost_logger as cl
import er006_asr_provider_routing_01 as asr_routing
import er012_b_family_voices_production_01 as bvoices

import audio_review_player as player_mod

import er013_family_c_production_01 as fam_c

SR = p9a.TARGET_SAMPLE_RATE  # 48000 (assembled stereo)
MONO_SR = common.SAMPLE_RATE  # 24000 (TTS output)

TTS_CALL_EST_JPY = 0.9
LLM_CALL_EST_JPY = 1.8
ASR_DIAG_CALL_EST_JPY = 0.3

# 記事非依存の既存Production共有asset(Trial-10以前から確立済み、
# `er003_v1_n3_01_assemble.py`のB1_SHARED_SOURCE_DIR/B1_SHARED_NAMESと同一)。
# ここにハードコードした値はassemble_mod側の値を直接参照するのみで、独自の
# 新しいsourceを定義しない。
_SHARED_NAV_SRC_NAME = {
    "welcome.wav": "welcome_charon.wav",
    "preview_intro.wav": "preview_intro_charon.wav",
    "key_phrases_intro.wav": "key_phrases_intro_charon.wav",
    "full_story_intro.wav": "full_story_intro_charon.wav",
}
_SHARED_NUMBER_SRC_NAME = {
    "kp1_number.wav": "num_one_charon.wav",
    "kp2_number.wav": "num_two_charon.wav",
    "kp3_number.wav": "num_three_charon.wav",
    "kp4_number.wav": "num_four_charon.wav",
    "kp5_number.wav": "num_five_charon.wav",
}


def load_config(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_article_paragraphs(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        text = f.read()
    return fam_c.split_into_paragraphs(text)


def build_segments_for_level(level_cfg: dict) -> tuple:
    """記事固有設定(article_config.json)からplan_story_segments()の完全な
    segment列(tts_text等を含む、TTS/regeneration/resumeで使う実体)を作る。
    reconstruction一致検証を含む(不一致ならSTOPする、Trial script群と同じ
    安全確認)。"""
    paragraphs = load_article_paragraphs(level_cfg["article_path"])
    expected = level_cfg.get("expected_paragraph_count")
    if expected is not None and len(paragraphs) != expected:
        raise RuntimeError(
            f"UNEXPECTED_PARAGRAPH_COUNT: expected={expected} actual={len(paragraphs)} "
            f"path={level_cfg['article_path']}")

    voice_keywords = level_cfg.get("voice_keywords", {})
    quote_voice_override_paragraphs = {
        int(k): v for k, v in level_cfg.get("quote_voice_override_paragraphs", {}).items()}
    display_paragraph_voice = {
        int(k): v for k, v in level_cfg.get("display_paragraph_voice", {}).items()}
    restrict = level_cfg.get("restrict_quote_splitting_to_paragraphs")

    flat_chunks = fam_c.build_flat_voice_chunks(
        paragraphs, voice_keywords,
        display_paragraph_voice=display_paragraph_voice,
        quote_voice_override_paragraphs=quote_voice_override_paragraphs,
        restrict_quote_splitting_to_paragraphs=restrict,
    )

    force_split = level_cfg.get("force_split_before_paragraphs", [])
    segments = fam_c.plan_story_segments(
        flat_chunks, force_split_before_paragraphs=set(force_split))

    reconstructed = fam_c.reconstruct_article_from_segments(segments, paragraphs)
    original = "\n\n".join(paragraphs)
    if reconstructed != original:
        raise RuntimeError(
            "STORY_SEGMENT_RECONSTRUCTION_MISMATCH: 生成前チェックに失敗しました"
            "(segment再構成が元記事と一致しません)。")
    return segments, paragraphs


def build_plan_for_level(level_cfg: dict) -> dict:
    segments, _paragraphs = build_segments_for_level(level_cfg)
    plan_rows = fam_c.build_segmentation_plan_report(segments)
    word_counts = [r["word_count"] for r in plan_rows]
    warning_count = sum(len(r["warnings"]) for r in plan_rows)
    return {
        "policy": ("Family C Story TTS segmentation原則(APPROVED_FOR_PRODUCTION、"
                   "2026-09-16)。同一Voice連続を優先して統合し、Voice変化点・"
                   "呼び出し側指定のforce_split_before_paragraphs(Comment挿入位置・"
                   "scene boundary)でのみ分割する。概ね100語以内を運用目安とし、"
                   "120語を大きく超えない。150語超過は自動分割を試み、単一段落で"
                   "分割不能な場合のみwarningとして記録する(生成をブロックしない)。"),
        "segment_count": len(plan_rows),
        "min_word_count": min(word_counts) if word_counts else 0,
        "max_word_count": max(word_counts) if word_counts else 0,
        "warning_count": warning_count,
        "reconstruction_matches_original": True,
        "segments": plan_rows,
    }


def run_plan_only(config: dict, level: str, out_dir: str) -> dict:
    level_cfg = config["levels"][level]
    plan = build_plan_for_level(level_cfg)
    os.makedirs(f"{out_dir}/evidence", exist_ok=True)
    out_path = f"{out_dir}/evidence/segmentation_plan_{level}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)
    print(f"[PLAN-ONLY] article={config.get('article_id')} level={level} "
          f"segment_count={plan['segment_count']} "
          f"min_word_count={plan['min_word_count']} max_word_count={plan['max_word_count']} "
          f"warning_count={plan['warning_count']} "
          f"reconstruction_matches_original={plan['reconstruction_matches_original']}")
    for r in plan["segments"]:
        print(f"  {r['id']:10s} voice={r['voice']:9s} words={r['word_count']:3d} "
              f"paragraphs={r['paragraph_range']} warnings={r['warnings']}")
    return plan


class BudgetTracker:
    """`er013_family_c_episode_trial_11_memory_run.BudgetTracker`と同一
    インターフェース(check_before/add)の独立実装(Trial script非依存)。"""

    def __init__(self, cap_jpy: float, log_path: str):
        self.cap = cap_jpy
        self.spent = 0.0
        self.log_path = log_path
        self.records: list = []

    def check_before(self, estimated_next_jpy: float, label: str) -> None:
        projected = self.spent + estimated_next_jpy
        if projected > self.cap:
            raise RuntimeError(
                f"BUDGET_WOULD_EXCEED: stage '{label}' の見込み追加費用(推定)"
                f"¥{estimated_next_jpy:.2f}を加えると累計¥{projected:.2f}が"
                f"上限¥{self.cap:.2f}を超えます。ここで停止します。")

    def add(self, label: str, kind: str, count: int, unit_jpy: float, meta: dict | None = None) -> None:
        jpy = count * unit_jpy
        self.spent += jpy
        rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "label": label, "kind": kind,
               "count": count, "unit_jpy_estimate": unit_jpy,
               "jpy_estimate": round(jpy, 4), "cumulative_jpy_estimate": round(self.spent, 4),
               "meta": meta or {}}
        self.records.append(rec)
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def run_comments_only(config: dict, level: str, out_dir: str, budget_jpy: float, no_tts: bool) -> dict:
    if level != "a2":
        # 構造的ガード: A2 Comment理解ガイド型ContractはB1へ適用しない。
        fam_c.guard_a2_only(level)
    if not no_tts:
        raise RuntimeError(
            "COMMENTS_ONLY_REQUIRES_NO_TTS: --comments-onlyは--no-ttsとの併用のみ"
            "対応します(TTS呼び出しは行いません、無駄な音声再生成を避けるため)。")

    level_cfg = config["levels"][level]
    paragraphs = load_article_paragraphs(level_cfg["article_path"])
    article_text = "\n\n".join(paragraphs)
    comments_cfg = level_cfg.get("comments", {})
    if not comments_cfg:
        raise RuntimeError("NO_COMMENTS_CONFIG: article_configにcommentsセクションがありません。")

    import er003_v1_iran01_a2_generate as a2gen
    client = a2gen.get_client()

    os.makedirs(f"{out_dir}/evidence", exist_ok=True)
    budget = BudgetTracker(budget_jpy, f"{out_dir}/evidence/a2_comment_raw_usage_log.jsonl")

    results = {}
    for num_str, cmt_cfg in sorted(comments_cfg.items(), key=lambda kv: int(kv[0])):
        comment_num = int(num_str)
        result = fam_c.generate_family_c_a2_comment(
            client, comment_num, article_text,
            cmt_cfg.get("content_facts", ""),
            scene_transition=cmt_cfg.get("scene_transition", ""),
            extra_instructions=level_cfg.get("extra_instructions", ""),
            budget=budget,
            label_prefix=f"family_c_a2_comment_runtime_evidence_{config.get('article_id')}",
        )
        quality_ok, quality_reasons = fam_c.check_a2_comment_quality(result["text"])
        results[str(comment_num)] = {
            "generated_text": result["text"],
            "model": result["model"],
            "contract": result["contract"],
            "attempts": result["attempts"],
            "quality_check": {"ok": quality_ok, "reasons": quality_reasons},
            "trial_reference_text": cmt_cfg.get("trial_reference_text"),
            "trial_source": cmt_cfg.get("trial_source"),
        }

    evidence = {
        "article_id": config.get("article_id"),
        "level": level,
        "contract_module": "er013_family_c_production_01.py",
        "routing": "er003_v1_iran01_a2_generate.run_support_text",
        "model": a2gen.MODEL,
        "cost_jpy_estimate_total": round(budget.spent, 4),
        "banned_patterns": fam_c.FAMILY_C_A2_COMMENT_BANNED_PATTERNS,
        "comments": results,
    }
    out_path = f"{out_dir}/evidence/a2_comment_runtime_evidence.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(evidence, f, ensure_ascii=False, indent=2)
    print(f"[COMMENTS-ONLY] article={config.get('article_id')} level={level} "
          f"cost_jpy_estimate={budget.spent:.2f}")
    for n, r in results.items():
        print(f"  comment_{n}: ok={r['quality_check']['ok']} reasons={r['quality_check']['reasons']}")
        print(f"    text={r['generated_text']}")
    return evidence


# ============================================================
# 全体生成経路(初回生成/retry/regeneration/fallback/resume)
# ============================================================
def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _ok_marker_path(out_path: str) -> str:
    return out_path + ".ok"


def _ok_meta_path(out_path: str) -> str:
    return out_path + ".ok.meta.json"


def _copy_with_ok(src: str, dst: str) -> None:
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if not os.path.exists(dst):
        shutil.copyfile(src, dst)
    ok_src, ok_dst = src + ".ok", dst + ".ok"
    if os.path.exists(ok_src) and not os.path.exists(ok_dst):
        shutil.copyfile(ok_src, ok_dst)
    elif not os.path.exists(ok_dst):
        with open(ok_dst, "w", encoding="utf-8") as f:
            f.write("ok")


def purge_segment_outputs(audio_dir: str, seg_id: str) -> None:
    """`--only-segments`regeneration: 指定segmentのwav/.ok/meta/debugのみ
    削除し、再TTSを強制する(他segmentのresumeには影響しない)。"""
    base = f"{audio_dir}/{seg_id}.wav"
    for suffix in ("", ".ok", ".ok.meta.json", ".debug.json"):
        p = base + suffix
        if os.path.exists(p):
            os.remove(p)


def resumable_reuse(out_path: str, expected_text_sha256: str) -> dict | None:
    """既存wav+.okがあり、記録済みtts_text sha256が現在のplanと一致する
    場合のみresume(skip)する。sha256不一致(本文変更等)またはmeta欠如かつ
    レガシー.ok(Trial由来コピー)の場合は、現時点のtext基準でmetaを新規に
    書き込みresumeを許可する(初回のreuse_fromコピー直後を想定)。"""
    if not (os.path.exists(out_path) and os.path.exists(_ok_marker_path(out_path))):
        return None
    meta_path = _ok_meta_path(out_path)
    if os.path.exists(meta_path):
        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)
        if meta.get("tts_text_sha256") != expected_text_sha256:
            return None
    else:
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump({"tts_text_sha256": expected_text_sha256,
                       "wav_sha256": p9a.sha256_file(out_path),
                       "upgraded_from_legacy_ok": True}, f, ensure_ascii=False, indent=2)
    return {"status": "REUSED_EXISTING_FILE", "path": out_path, "sha256": p9a.sha256_file(out_path)}


def mark_ok(r: dict, out_path: str, text_sha256: str) -> None:
    if r.get("status") in ("OK", "REUSED_EXISTING_FILE"):
        with open(_ok_marker_path(out_path), "w", encoding="utf-8") as f:
            f.write("ok")
        with open(_ok_meta_path(out_path), "w", encoding="utf-8") as f:
            json.dump({"tts_text_sha256": text_sha256, "wav_sha256": p9a.sha256_file(out_path)},
                      f, ensure_ascii=False, indent=2)
    else:
        with open(out_path + ".debug.json", "w", encoding="utf-8") as f:
            json.dump(r, f, ensure_ascii=False, indent=2, default=str)


def tts_call_for_voice(voice: str, text: str, out_path: str, label: str, budget: BudgetTracker,
                        voice_tts_names: dict) -> dict:
    """既存Production TTS関数への唯一の分岐点(retry/fallback cascadeは
    各関数の内部実装にすでに内包されている、Trial-11/12でVALIDATED済みの
    呼び出しパターンをそのまま踏襲): narrator=verified_strict(標準複数
    attempt cascade)、device=Charon固定voice、その他はvoice_tts_names
    (article_config)で指定されたvoice_nameでgenerate_voice_body_wide_margin
    (内部に独自のASR検証+attempt cascadeを持つ)を呼ぶ。"""
    budget.check_before(TTS_CALL_EST_JPY, label)
    if voice == "narrator":
        expected_substring = text[:20]
        r = repro01.generate_narration_snippet_verified_strict(text, "en", out_path, expected_substring)
        budget.add(label, "tts", 1, TTS_CALL_EST_JPY, {"status": r.get("status"), "language": "en",
                                                        "fn": "generate_narration_snippet_verified_strict"})
        return r
    if voice == "device":
        r = voice01.generate_charon_english(text, out_path)
        budget.add(label, "tts", 1, TTS_CALL_EST_JPY, {"status": r.get("status"),
                                                        "fn": "generate_charon_english"})
        return r
    voice_name = voice_tts_names.get(voice)
    if voice_name is None:
        raise RuntimeError(
            f"UNKNOWN_VOICE_NO_MAPPING: voice={voice!r}をarticle_configの"
            "levels.<level>.voice_tts_namesに追加してください(narrator/deviceは"
            "固定voiceのため設定不要)。")
    r = bvoices.generate_voice_body_wide_margin(text, out_path, voice_name)
    budget.add(label, "tts", 1, TTS_CALL_EST_JPY, {"status": r.get("status"), "voice_name": voice_name,
                                                    "fn": "generate_voice_body_wide_margin"})
    return r


def to_audit_entry(r: dict, canonical_text: str, reused: bool, asr_text=None) -> dict:
    if reused or r.get("status") == "REUSED_EXISTING_FILE":
        return {"status": "OK", "path": r.get("path"), "sha256": r.get("sha256"),
                "canonical_text": canonical_text, "disfluency_checked": True, "reused": True,
                "asr_text": asr_text}
    return {
        "status": r.get("status"), "path": r.get("path"), "sha256": r.get("sha256"),
        "canonical_text": canonical_text,
        "disfluency_checked": bool(r.get("disfluency_checked", False)),
        "asr_text": asr_text if asr_text is not None else r.get("asr_text"),
    }


def get_or_run_asr(seg_id: str, wav_path: str, language: str, budget: BudgetTracker,
                    prev_segments_audit: dict, wav_sha256: str) -> tuple:
    """ASRキャッシュは音声sha256一致時のみ再利用する。不一致・キャッシュ
    無しの場合は必ず現物ASRを実行する(名前のみキャッシュは使わない)。"""
    prev = (prev_segments_audit or {}).get(seg_id)
    if prev and prev.get("sha256") == wav_sha256 and prev.get("asr_text") is not None:
        return prev["asr_text"], True
    asr_lang = "en-US" if language == "en" else "ja-JP"
    budget.check_before(ASR_DIAG_CALL_EST_JPY, f"{seg_id}_asr_diag")
    text, err = asr_routing.transcribe(wav_path, asr_lang)
    budget.add(f"{seg_id}_asr_diag", "asr_diag", 1, ASR_DIAG_CALL_EST_JPY, {"error": err})
    return text, False


def _normalize_loose(text) -> str:
    import re
    if text is None:
        return ""
    t = text.lower()
    t = re.sub(r"[^\w\s]", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def provision_fixed_wav_asset(name: str, out_dir: str, audio_dir: str, reuse_from: str | None) -> dict:
    """記事固有だがcontent自体は既存(topic_intro等の書き起こしをこのrunner
    で新規に書かない)固定wav asset、またはKey Phrase等のcuration成果物の
    provisioning。優先順位: (1)既にaudio_dir内に存在, (2)reuse_from,
    (3)記事非依存の既存共有Production資産(Welcome/Preview intro/番号読み上げ
    のみ), それでも無ければ明示的にエラーとする(スコープ外のfrom-scratch
    content生成をこのrunnerが黙って諦めることはない)。"""
    dst = f"{audio_dir}/{name}"
    if os.path.exists(dst) and os.path.exists(dst + ".ok"):
        return {"source": "already_present", "path": dst}
    if reuse_from:
        src = f"{reuse_from}/audio/{name}"
        if os.path.exists(src):
            _copy_with_ok(src, dst)
            return {"source": "reuse_from", "path": dst}
    if name in _SHARED_NAV_SRC_NAME:
        src = f"{assemble_mod.B1_SHARED_SOURCE_DIR}/{_SHARED_NAV_SRC_NAME[name]}"
        _copy_with_ok(src, dst)
        return {"source": "shared_production_asset", "path": dst}
    if name in _SHARED_NUMBER_SRC_NAME:
        src = f"{assemble_mod.B1_SHARED_SOURCE_DIR}/{_SHARED_NUMBER_SRC_NAME[name]}"
        _copy_with_ok(src, dst)
        return {"source": "shared_production_asset", "path": dst}
    raise RuntimeError(
        f"ASSET_NOT_AVAILABLE({name}): reuse_fromにも既存共有Production資産にも"
        "見つかりません。Key Phrase選定等のcontent curationのfrom-scratch生成は"
        "本Wiring委任(Story TTS segmentation/A2 Comment Contract)のスコープ外です。"
        "article_configにreuse_fromを指定するか、既存asset生成scriptで用意して"
        "ください。")


def run_simple_narrator_asset(name: str, text: str, language: str, out_dir: str, audio_dir: str,
                               budget: BudgetTracker, reuse_from: str | None, resume: bool) -> tuple:
    """topic_intro_en/japanese_title/preview等、記事固有のtextが
    article_configに含まれる単純narrator asset。sha256(text)に基づき
    resumeし、無ければ既存Production narrator TTS関数で新規生成できる
    (Key Phrase等と異なりfrom-scratch生成が可能な単純asset)。"""
    out_path = f"{audio_dir}/{name}"
    text_sha = _sha256_text(text)
    reused = resumable_reuse(out_path, text_sha) if resume else None
    if reused is None and reuse_from:
        src = f"{reuse_from}/audio/{name}"
        if os.path.exists(src):
            _copy_with_ok(src, out_path)
            reused = resumable_reuse(out_path, text_sha)
    if reused is not None:
        return reused, True
    r = tts_call_for_voice("narrator", text, out_path, name.removesuffix(".wav"), budget, {})
    mark_ok(r, out_path, text_sha)
    if r.get("status") != "OK":
        raise RuntimeError(f"SIMPLE_ASSET_TTS_FAILED({name}): {r}")
    return r, False


def load_mono(path: str) -> np.ndarray:
    mono, sr, _, _ = common.read_wav_float(path)
    assert sr == MONO_SR, f"unexpected sample rate: {sr} (path={path})"
    return mono


def build_family_c_episode_sequence(*, audio_dir: str, target_rms: float, gs, gs_already_stereo,
                                     intro_gained, notification_gained, outro_gained,
                                     kp_blocks: list, story_segments: list, comment_wavs: dict,
                                     comment_after_segment_id: dict, has_japanese_title: bool,
                                     preview_asset_name: str) -> list:
    """Family C A2/B1共通の episode timeline構築(Trial-11 Memory A2/
    Trial-12 Twins A2・B1で確立されたStage H+I構成の一般化、pause値は
    Trial-11/12と同一のmodule定数)。level差(Japanese title有無/preview
    asset名/comment挿入位置)はすべて引数経由で渡す(固定値で上書きしない)。"""
    seq = []

    def sil(seconds: float) -> None:
        seq.append((f"_silence_{seconds}", p9a.silence_stereo(seconds, SR)))

    def load(name: str) -> np.ndarray:
        return load_mono(f"{audio_dir}/{name}")

    seq.append(("Intro", intro_gained))
    seq.append(("Welcome (Charon)", gs(load("welcome.wav"), "welcome")))
    sil(0.5)
    seq.append(("Topic intro", gs(load("topic_intro_en.wav"), "topic_intro_en")))
    sil(0.65)
    if has_japanese_title:
        seq.append(("Japanese title", gs(load("japanese_title.wav"), "japanese_title")))
        sil(0.5)
    seq.append(("Notification 1", notification_gained))
    sil(0.4)
    seq.append(("Preview intro (Charon)", gs(load("preview_intro.wav"), "preview_intro")))
    sil(0.65)
    seq.append(("Preview", gs(load(preview_asset_name), preview_asset_name.removesuffix(".wav"))))
    sil(0.5)
    seq.append(("Notification 2", notification_gained))
    sil(0.4)
    seq.append(("Key phrases intro (Charon)", gs(load("key_phrases_intro.wav"), "key_phrases_intro")))
    sil(0.5)
    for rank, num_path, en_path, ja_path in kp_blocks:
        num_stereo = gs(load_mono(num_path), f"kp{rank}_number")
        en_stereo = gs(load_mono(en_path), f"kp{rank}_english")
        ja_stereo = gs(load_mono(ja_path), f"kp{rank}_japanese")
        block = p9a.build_key_phrase_block(
            num_stereo, en_stereo, ja_stereo, SR,
            numbering_pause_seconds=assemble_mod.A2_KEY_PHRASE_NUMBERING_PAUSE_SECONDS)
        seq.append((f"key_phrase_{rank}", block))
    seq.append(("Notification 3", notification_gained))
    sil(0.4)
    seq.append(("Full story intro (Charon)", gs(load("full_story_intro.wav"), "full_story_intro")))
    sil(1.0)

    seq.append(("Comment 1", gs(load_mono(comment_wavs[1]), "comment_1")))
    sil(0.8)

    for seg in story_segments:
        seq.append((seg["id"], gs(load_mono(seg["audio_path"]), seg["id"])))
        # kind(split/merge)はTrial-11/12で"voice!=narratorは常に短いVoice
        # 境界segment(split)"という関係が成立していたことに基づく(production_01
        # 自体は`kind`フィールドを持たないため、ここでvoiceから導出する)。
        sil(0.2 if seg["voice"] != "narrator" else 0.5)
        if seg["id"] == comment_after_segment_id.get("2"):
            sil(1.0)
            seq.append(("Comment 2", gs(load_mono(comment_wavs[2]), "comment_2")))
            sil(0.8)
        if seg["id"] == comment_after_segment_id.get("3"):
            sil(1.0)
            seq.append(("Comment 3", gs(load_mono(comment_wavs[3]), "comment_3")))
            sil(0.8)

    sil(0.5)
    seq.append(("Outro", outro_gained))
    return seq


def run_comments_stage_a2(level_cfg: dict, out_dir: str, audio_dir: str, article_text: str,
                           budget: BudgetTracker, reuse_from: str | None, resume: bool,
                           only_segments: set, article_id: str) -> dict:
    comments_cfg = level_cfg.get("comments", {})
    if not comments_cfg:
        raise RuntimeError("NO_COMMENTS_CONFIG: article_configにcommentsセクションがありません。")

    comments_md_path = f"{out_dir}/comments_ja.md"
    forced_comment_regen = bool(only_segments & {f"comment_{n}" for n in (1, 2, 3)})
    if (not os.path.exists(comments_md_path) and reuse_from
            and os.path.exists(f"{reuse_from}/comments_ja.md") and not forced_comment_regen):
        # 初回のreuse_from populate: 承認済みComment本文をそのままコピーする
        # (LLMの毎回再課金を避ける。これはComment内容の初回生成を隠すのでは
        # なく、初回生成は`--comments-only`で既に別途evidence済みのため、
        # このresume経路では既存本文を再利用するという設計)。
        shutil.copyfile(f"{reuse_from}/comments_ja.md", comments_md_path)
    comment_texts: dict = {}
    if os.path.exists(comments_md_path) and not forced_comment_regen:
        with open(comments_md_path, encoding="utf-8") as f:
            existing_md_text = f.read()
        for num_str in comments_cfg:
            n = int(num_str)
            marker = f"## Comment {n}\n\n"
            after = existing_md_text.split(marker, 1)[1]
            comment_texts[n] = after.split("\n\n", 1)[0].strip()
    else:
        import er003_v1_iran01_a2_generate as a2gen
        client = a2gen.get_client()
        for num_str, cmt_cfg in sorted(comments_cfg.items(), key=lambda kv: int(kv[0])):
            n = int(num_str)
            result = fam_c.generate_family_c_a2_comment(
                client, n, article_text, cmt_cfg.get("content_facts", ""),
                scene_transition=cmt_cfg.get("scene_transition", ""),
                extra_instructions=level_cfg.get("extra_instructions", ""),
                budget=budget, label_prefix=f"family_c_a2_comment_{article_id}")
            comment_texts[n] = result["text"]
        with open(comments_md_path, "w", encoding="utf-8") as f:
            for num_str in sorted(comments_cfg, key=int):
                n = int(num_str)
                f.write(f"## Comment {n}\n\n{comment_texts[n]}\n\n")

    comment_wavs = {}
    audit = {}
    for n, text in comment_texts.items():
        name = f"comment_{n}_ja.wav"
        out_path = f"{audio_dir}/{name}"
        text_sha = _sha256_text(text)
        reused = resumable_reuse(out_path, text_sha) if resume else None
        if reused is None and reuse_from:
            src = f"{reuse_from}/audio/{name}"
            if os.path.exists(src):
                _copy_with_ok(src, out_path)
                reused = resumable_reuse(out_path, text_sha)
        if reused is not None:
            r = reused
            was_resumed = True
        else:
            r = tts_call_for_voice("narrator", text, out_path, f"comment_{n}_ja", budget, {})
            mark_ok(r, out_path, text_sha)
            if r.get("status") != "OK":
                raise RuntimeError(f"COMMENT_TTS_FAILED(comment_{n}): {r}")
            was_resumed = False
        comment_wavs[n] = out_path
        audit[f"comment_{n}_ja"] = to_audit_entry(r, text, was_resumed)
    return {"comment_texts": comment_texts, "comment_wavs": comment_wavs, "audit": audit}


def run_full_generation(config: dict, level: str, out_root: str, budget_jpy: float,
                         only_segments: list | None, resume: bool) -> dict:
    if level not in ("a2", "b1"):
        raise RuntimeError(f"UNKNOWN_LEVEL: {level!r}")
    level_cfg = config["levels"][level]
    article_id = config.get("article_id", "unknown")
    only_segments_set = set(only_segments or [])

    out_dir = f"{out_root}/{level}"
    audio_dir = f"{out_dir}/audio"
    assembled_dir = f"{out_dir}/assembled"
    kp_dir = f"{out_dir}/key_phrases"
    audit_dir = f"{out_dir}/audit"
    web_dir = f"{out_dir}/web"
    for d in (audio_dir, assembled_dir, kp_dir, audit_dir, web_dir, f"{web_dir}/segments"):
        os.makedirs(d, exist_ok=True)

    cl.install(f"{audit_dir}/er005_cost_log.jsonl")
    budget = BudgetTracker(budget_jpy, f"{out_dir}/raw_usage_log.jsonl")

    reuse_from = level_cfg.get("reuse_from")
    prev_audit = {}
    if reuse_from and os.path.exists(f"{reuse_from}/audit/tts_generation_results.json"):
        with open(f"{reuse_from}/audit/tts_generation_results.json", encoding="utf-8") as f:
            prev_audit = json.load(f)
    # tts_generation_results.jsonのasr_textは新規生成直後にしか埋まらない
    # (Trial実測、resume/reuse系entryはNoneのことが多い)ため、実際にASRを
    # 実行済みの正である player_display_audio_consistency.json/
    # comment_consistency.jsonからasr_textを補完する(sha256はtts_generation_
    # results.json側のみが保持、両者をsegment_idで突き合わせて初めて
    # 「sha256一致時のみキャッシュ再利用」の判定に使える形になる)。
    if reuse_from and "segments" in prev_audit:
        if os.path.exists(f"{reuse_from}/player_display_audio_consistency.json"):
            with open(f"{reuse_from}/player_display_audio_consistency.json", encoding="utf-8") as f:
                for row in json.load(f):
                    sid = row.get("segment_id")
                    if sid in prev_audit["segments"] and row.get("asr_text") is not None:
                        prev_audit["segments"][sid]["asr_text"] = row["asr_text"]
        if os.path.exists(f"{reuse_from}/comment_consistency.json"):
            with open(f"{reuse_from}/comment_consistency.json", encoding="utf-8") as f:
                for row in json.load(f):
                    sid = f"comment_{row.get('comment')}_ja"
                    if sid in prev_audit["segments"] and row.get("asr_text") is not None:
                        prev_audit["segments"][sid]["asr_text"] = row["asr_text"]

    segments, paragraphs = build_segments_for_level(level_cfg)
    article_text = "\n\n".join(paragraphs)

    # --only-segments regeneration: 対象segmentのwav/.ok/metaのみ削除して
    # 強制再生成する(他segmentのresumeへは影響しない)。
    for seg in segments:
        if seg["id"] in only_segments_set:
            purge_segment_outputs(audio_dir, seg["id"])
    for name in ("comment_1_ja", "comment_2_ja", "comment_3_ja", "comment_1_en",
                 "comment_2_en", "comment_3_en"):
        if name.rsplit("_", 1)[0] in only_segments_set or name in only_segments_set:
            purge_segment_outputs(audio_dir, name)

    voice_tts_names = level_cfg.get("voice_tts_names", {})

    # === Stage: Story segment TTS(初回生成/regeneration/resume/fallback) ===
    audit_segments: dict = {}
    tts_report = []
    for seg in segments:
        out_path = f"{audio_dir}/{seg['id']}.wav"
        text_sha = _sha256_text(seg["tts_text"])
        force_regen = seg["id"] in only_segments_set
        reused = None if force_regen else (resumable_reuse(out_path, text_sha) if resume else None)
        if reused is None and reuse_from and not force_regen:
            src = f"{reuse_from}/audio/{seg['id']}.wav"
            if os.path.exists(src):
                _copy_with_ok(src, out_path)
                reused = resumable_reuse(out_path, text_sha)
        if reused is not None:
            r = reused
            was_resumed = True
        else:
            r = tts_call_for_voice(seg["voice"], seg["tts_text"], out_path, seg["id"], budget,
                                    voice_tts_names)
            mark_ok(r, out_path, text_sha)
            if r.get("status") != "OK":
                raise RuntimeError(f"STORY_TTS_FAILED({seg['id']}): {r}")
            was_resumed = False
        seg["audio_path"] = out_path
        audit_segments[seg["id"]] = to_audit_entry(r, seg["tts_text"], was_resumed)
        tts_report.append({"id": seg["id"], "voice": seg["voice"], "resumed": was_resumed,
                            "status": r.get("status"), "forced_regeneration": force_regen})

    with open(f"{out_dir}/segments.json", "w", encoding="utf-8") as f:
        json.dump([{k: v for k, v in s.items() if k != "paragraph_contributions"} for s in segments],
                  f, ensure_ascii=False, indent=2)

    # === Stage: ASR consistency(現物wav、sha256一致時のみキャッシュ再利用) ===
    consistency_rows = []
    for seg in segments:
        wav_sha = p9a.sha256_file(seg["audio_path"])
        asr_text, cache_hit = get_or_run_asr(
            seg["id"], seg["audio_path"], "en", budget,
            prev_audit.get("segments"), wav_sha)
        audit_segments[seg["id"]]["asr_text"] = asr_text
        audit_segments[seg["id"]]["sha256"] = wav_sha
        consistency_rows.append({
            "segment_id": seg["id"], "voice": seg["voice"],
            "canonical_text": seg["tts_text"], "tts_input_text": seg["tts_text"],
            "asr_text": asr_text, "asr_cache_hit": cache_hit,
            "match": _normalize_loose(asr_text) == _normalize_loose(seg["tts_text"]),
        })

    # === Stage: Comment(level別、B1はA2 Contractを一切呼ばない) ===
    if level == "a2":
        comments_result = run_comments_stage_a2(
            level_cfg, out_dir, audio_dir, article_text, budget, reuse_from, resume,
            only_segments_set, article_id)
        comment_texts = comments_result["comment_texts"]
        comment_wavs = comments_result["comment_wavs"]
        audit_segments.update(comments_result["audit"])
        for n, path in comment_wavs.items():
            wav_sha = p9a.sha256_file(path)
            asr_text, cache_hit = get_or_run_asr(
                f"comment_{n}_ja", path, "ja", budget, prev_audit.get("segments"), wav_sha)
            audit_segments[f"comment_{n}_ja"]["asr_text"] = asr_text
            audit_segments[f"comment_{n}_ja"]["sha256"] = wav_sha
        preview_asset_name = "preview_ja.wav"
        has_japanese_title = True
        comment_after_segment_id = level_cfg.get("comment_after_segment_id", {})
    else:
        # B1: A2 Comment理解ガイド型Contract(fam_c.generate_family_c_a2_comment)
        # は構造的に一切呼ばない。B1 Comment/Previewは既存B1 Support経路
        # (er003_v1_b1_scaffold_01_generate)がcontent authoringを担う別工程
        # であり、本Wiring委任(2-A/2-B)のスコープはStory TTS/A2 Contractの
        # wiringのため、B1側のcomment contentがarticle_configに未提供の場合は
        # ここで明示的に停止する(A2 Contractへ黙って流用することは絶対に
        # しない)。
        b1_comments_cfg = level_cfg.get("comments")
        if not b1_comments_cfg:
            raise RuntimeError(
                "B1_COMMENT_CONTENT_NOT_PROVIDED: B1 CommentはA2 Comment理解"
                "ガイド型Contractを使用しません(誤適用防止のガード、guard_a2_only"
                "と同じ設計方針)。article_configのlevels.b1.commentsへ既存B1 "
                "Support経路(er003_v1_b1_scaffold_01_generate)で生成済みの"
                "content(textとaudio)を指定してください。本委任の対象は"
                "Story TTS segmentationのB1適用であり、B1 Commentのfrom-scratch"
                "content生成は対象外です。")
        raise NotImplementedError(
            "B1_FULL_ASSEMBLY_NOT_EXERCISED_IN_THIS_DELEGATION: B1のComment/"
            "Assembly全体生成pathは本差し戻し委任ではruntime evidence対象外"
            "(--plan-onlyのみ実行、無駄な音声再生成を避けるため)。Story TTS"
            "segmentation(上記で完了済み)はA2/B1共通で実際に動作する。")

    # === Stage: 非Story固定asset(Welcome等の共有資産+記事固有topic_intro等) ===
    topic_title = level_cfg.get("topic_title")
    japanese_title_text = level_cfg.get("japanese_title_text")
    if not topic_title:
        raise RuntimeError("TOPIC_TITLE_NOT_PROVIDED: article_configにtopic_titleがありません。")
    topic_intro_text = f"Today's topic is {topic_title}."
    _r, topic_reused = run_simple_narrator_asset(
        "topic_intro_en.wav", topic_intro_text, "en", out_dir, audio_dir, budget, reuse_from, resume)
    audit_segments["topic_intro_en"] = to_audit_entry(_r, topic_intro_text, topic_reused)

    if has_japanese_title:
        if not japanese_title_text:
            raise RuntimeError("JAPANESE_TITLE_TEXT_NOT_PROVIDED: article_configに"
                                "japanese_title_textがありません。")
        _r, jt_reused = run_simple_narrator_asset(
            "japanese_title.wav", japanese_title_text, "ja", out_dir, audio_dir, budget, reuse_from, resume)
        audit_segments["japanese_title"] = to_audit_entry(_r, japanese_title_text, jt_reused)

    preview_text = None
    preview_txt_path = f"{out_dir}/preview.txt"
    if reuse_from and os.path.exists(f"{reuse_from}/preview.txt") and not os.path.exists(preview_txt_path):
        shutil.copyfile(f"{reuse_from}/preview.txt", preview_txt_path)
    if os.path.exists(preview_txt_path):
        with open(preview_txt_path, encoding="utf-8") as f:
            preview_text = f.read().strip()
    if not preview_text:
        raise RuntimeError("PREVIEW_TEXT_NOT_AVAILABLE: preview.txt がreuse_fromにも"
                            "生成済み出力にもありません(Preview文面のcontent authoring"
                            "は本Wiring委任のスコープ外)。")
    _r, preview_reused = run_simple_narrator_asset(
        preview_asset_name, preview_text, "ja", out_dir, audio_dir, budget, reuse_from, resume)
    audit_segments[preview_asset_name.removesuffix(".wav")] = to_audit_entry(_r, preview_text, preview_reused)

    for name in ("welcome.wav", "preview_intro.wav", "key_phrases_intro.wav", "full_story_intro.wav"):
        info = provision_fixed_wav_asset(name, out_dir, audio_dir, reuse_from)
        audit_segments.setdefault(name.removesuffix(".wav"), {
            "status": "OK", "path": info["path"], "sha256": p9a.sha256_file(info["path"]),
            "canonical_text": None, "disfluency_checked": True, "reused": True, "asr_text": None,
        })

    # === Stage: Key Phrase(content curationはスコープ外、reuse_from必須) ===
    if reuse_from and os.path.isdir(f"{reuse_from}/key_phrases") and not os.listdir(kp_dir):
        shutil.copytree(f"{reuse_from}/key_phrases", kp_dir, dirs_exist_ok=True)
    kp_items_path = f"{kp_dir}/keywords_canonicalized.json"
    if not os.path.exists(kp_items_path):
        raise RuntimeError("KEY_PHRASE_CURATION_NOT_AVAILABLE: keywords_canonicalized.jsonが"
                            "ありません(Key Phrase選定content curationは本Wiring委任の"
                            "スコープ外、reuse_fromが必要です)。")
    with open(kp_items_path, encoding="utf-8") as f:
        kp_items = sorted(json.load(f)["items"], key=lambda it: it["rank"])
    kp_blocks = []
    audit_key_phrases = {}
    prev_kp_audit = prev_audit.get("key_phrases", {})
    for item in kp_items:
        rank = item["rank"]
        sub_audit = {}
        paths = {}
        for kind, name in (("number", f"kp{rank}_number.wav"), ("english", f"kp{rank}_english.wav"),
                           ("japanese", f"kp{rank}_japanese.wav")):
            info = provision_fixed_wav_asset(name, out_dir, audio_dir, reuse_from)
            paths[kind] = info["path"]
            prev_entry = (prev_kp_audit.get(str(rank), {}) or {}).get(kind, {})
            sub_audit[kind] = {"status": "OK", "path": info["path"], "sha256": p9a.sha256_file(info["path"]),
                               "canonical_text": prev_entry.get("canonical_text"), "disfluency_checked": True,
                               "reused": True, "asr_text": prev_entry.get("asr_text")}
        audit_key_phrases[str(rank)] = sub_audit
        kp_blocks.append((rank, paths["number"], paths["english"], paths["japanese"]))
    if os.path.exists(f"{reuse_from}/key_phrase_consistency.json") if reuse_from else False:
        shutil.copyfile(f"{reuse_from}/key_phrase_consistency.json", f"{out_dir}/key_phrase_consistency.json")

    # === Stage: gain + timeline構築 + Assembly ===
    intro_mp3 = p9a.load_and_resample_to_target(p9a.INTRO_MP3_PATH)
    outro_mp3 = p9a.load_and_resample_to_target(p9a.OUTRO_MP3_PATH)
    notification_mp3 = p9a.load_and_resample_to_target(p9a.NOTIFICATION_MP3_PATH)

    gain_report: dict = {}

    def gs(mono: np.ndarray, label: str) -> np.ndarray:
        gain = p9a.compute_gain_for_target_rms(mono, target_rms)
        gained = mono * gain
        gain_report[label] = {"gain": round(float(gain), 4), "rms_before": round(p9a.rms(mono), 5),
                               "rms_after": round(p9a.rms(gained), 5), "peak_after": round(p9a.peak(gained), 5)}
        return p9a.mono_24k_to_stereo_target(gained)

    def gs_already_stereo(data: np.ndarray, label: str) -> np.ndarray:
        gain = p9a.compute_gain_for_target_rms(data, target_rms)
        gained = data * gain
        gain_report[label] = {"gain": round(float(gain), 4), "rms_before": round(p9a.rms(data), 5),
                               "rms_after": round(p9a.rms(gained), 5), "peak_after": round(p9a.peak(gained), 5)}
        return gained

    preview_mono = load_mono(f"{audio_dir}/{preview_asset_name}")
    first_story_mono = load_mono(segments[0]["audio_path"])
    target_rms = (p9a.rms(preview_mono) + p9a.rms(first_story_mono)) / 2
    gain_report["target_rms"] = round(float(target_rms), 5)

    intro_gained = gs_already_stereo(intro_mp3["samples"], "intro")
    notification_gained = gs_already_stereo(notification_mp3["samples"], "notification")
    intro_final_rms = p9a.rms(intro_gained)
    outro_matched = outro_mp3["samples"] * p9a.compute_gain_for_target_rms(outro_mp3["samples"], intro_final_rms)
    outro_gained = outro_matched * assemble_mod.OUTRO_EXTRA_GAIN_LINEAR
    gain_report["outro"] = {
        "matched_to": "intro_post_gain_rms", "intro_post_gain_rms": round(intro_final_rms, 5),
        "rms_after_match": round(p9a.rms(outro_matched), 5),
        "extra_gain_linear": round(float(assemble_mod.OUTRO_EXTRA_GAIN_LINEAR), 4),
        "rms_final": round(p9a.rms(outro_gained), 5), "peak_final": round(p9a.peak(outro_gained), 5),
    }

    seq = build_family_c_episode_sequence(
        audio_dir=audio_dir, target_rms=target_rms, gs=gs, gs_already_stereo=gs_already_stereo,
        intro_gained=intro_gained, notification_gained=notification_gained, outro_gained=outro_gained,
        kp_blocks=kp_blocks, story_segments=segments, comment_wavs=comment_wavs,
        comment_after_segment_id=comment_after_segment_id, has_japanese_title=has_japanese_title,
        preview_asset_name=preview_asset_name)

    with open(f"{audit_dir}/gain_report.json", "w", encoding="utf-8") as f:
        json.dump(gain_report, f, ensure_ascii=False, indent=2)

    assembled_result = assemble_mod.assemble_with_timeline(seq)
    safety_result = assemble_mod.apply_headroom_safety_valve(assembled_result["assembled"], seq)
    with open(f"{audit_dir}/headroom_report.json", "w", encoding="utf-8") as f:
        json.dump(safety_result["report"], f, ensure_ascii=False, indent=2)

    final_path = f"{assembled_dir}/family_c_production_{article_id}_{level}.wav"
    common.write_wav_float(final_path, safety_result["assembled"], SR, 2)

    run_summary = {
        "duration_seconds": assembled_result["total_duration_seconds"],
        "peak_before_headroom": safety_result["report"]["peak_before"],
        "peak_after_headroom": safety_result["report"]["peak_after"],
        "headroom_applied": safety_result["report"]["applied"],
        "timeline": assembled_result["timeline"],
    }
    with open(f"{audit_dir}/run_summary_assemble.json", "w", encoding="utf-8") as f:
        json.dump(run_summary, f, ensure_ascii=False, indent=2)

    # === Stage: tts_generation_results.json(Gate入力) + Audio Validation Gate ===
    with open(f"{audit_dir}/tts_generation_results.json", "w", encoding="utf-8") as f:
        json.dump({"segments": audit_segments, "key_phrases": audit_key_phrases}, f,
                  ensure_ascii=False, indent=2)

    level_string = f"FAMILY_C_PRODUCTION_{level.upper()}"
    gate_error = None
    try:
        assemble_mod.verify_episode_audio_validation_gate(out_dir, level_string)
        gate_status = "PASS"
    except RuntimeError as e:
        gate_status = "BLOCKED"
        gate_error = str(e)
    with open(f"{out_dir}/audio_validation.json", "w", encoding="utf-8") as f:
        json.dump({"status": gate_status, "level": level_string, "error": gate_error}, f,
                  ensure_ascii=False, indent=2)

    with open(f"{out_dir}/player_display_audio_consistency.json", "w", encoding="utf-8") as f:
        json.dump(consistency_rows, f, ensure_ascii=False, indent=2)

    # === Stage: mp3化(evidence用player、ユーザー実検証用ではない) ===
    web_result = convert_all_to_mp3(audio_dir, assembled_dir, web_dir,
                                     f"family_c_production_{article_id}_{level}.wav")
    write_evidence_player(out_dir, web_dir, run_summary, seq, article_id, level)

    cost_summary = {
        "budget_cap_jpy": budget_jpy, "total_estimate_jpy": round(budget.spent, 4),
        "records": budget.records, "gate_status": gate_status,
    }
    with open(f"{out_dir}/cost_summary.json", "w", encoding="utf-8") as f:
        json.dump(cost_summary, f, ensure_ascii=False, indent=2)

    summary = {
        "level": level, "out_dir": out_dir, "gate_status": gate_status,
        "duration_seconds": run_summary["duration_seconds"],
        "cost_jpy_estimate": round(budget.spent, 4),
        "tts_report": tts_report,
        "tts_resumed_count": sum(1 for r in tts_report if r["resumed"]),
        "tts_total_count": len(tts_report),
        "asr_cache_hit_count": sum(1 for r in consistency_rows if r["asr_cache_hit"]),
        "asr_total_count": len(consistency_rows),
        "episode_wav": final_path, "episode_mp3": web_result.get("episode_mp3"),
    }
    print(f"[FULL-GENERATION] level={level} gate={gate_status} "
          f"duration={run_summary['duration_seconds']}s "
          f"tts_resumed={summary['tts_resumed_count']}/{summary['tts_total_count']} "
          f"asr_cache_hit={summary['asr_cache_hit_count']}/{summary['asr_total_count']} "
          f"cost_estimate=Y{budget.spent:.2f}")
    return summary


def convert_all_to_mp3(audio_dir: str, assembled_dir: str, web_dir: str, episode_wav_name: str) -> dict:
    import soundfile as sf

    web_seg_dir = f"{web_dir}/segments"
    os.makedirs(web_seg_dir, exist_ok=True)

    def convert_one(wav_path: str, mp3_path: str) -> dict:
        data, sr = sf.read(wav_path)
        sf.write(mp3_path, data, sr, format="MP3")
        return {"wav_path": wav_path, "mp3_path": mp3_path,
                "wav_bytes": os.path.getsize(wav_path), "mp3_bytes": os.path.getsize(mp3_path)}

    results = []
    ep_wav = f"{assembled_dir}/{episode_wav_name}"
    ep_mp3 = f"{web_dir}/{episode_wav_name.removesuffix('.wav')}.mp3"
    results.append({"kind": "episode", **convert_one(ep_wav, ep_mp3)})

    wav_names = sorted(n for n in os.listdir(audio_dir) if n.endswith(".wav"))
    for name in wav_names:
        stem = name[:-4]
        results.append({"kind": "segment", "segment_id": stem,
                         **convert_one(f"{audio_dir}/{name}", f"{web_seg_dir}/{stem}.mp3")})

    web_result = {"episode_mp3": ep_mp3, "segment_count": len(wav_names), "conversions": results,
                  "note": "evidence専用出力(ユーザー実検証用playerには未掲載)。"}
    out_dir = os.path.dirname(web_dir)
    with open(f"{out_dir}/web_delivery.json", "w", encoding="utf-8") as f:
        json.dump(web_result, f, ensure_ascii=False, indent=2)
    return web_result


def write_evidence_player(out_dir: str, web_dir: str, run_summary: dict, seq: list,
                           article_id: str, level: str) -> None:
    rows = []
    for entry in run_summary["timeline"]:
        name = entry["part"]
        start = entry["start_seconds"]
        if name.startswith("_silence_"):
            continue
        seg_id = name if not name.startswith("key_phrase_") else name
        audio_html = player_mod.render_single_audio_html(f"./web/segments/{seg_id}.mp3")
        rows.append(player_mod.render_timeline_row(start, name, "(evidence, 詳細な話者表記省略)",
                                                     "(evidence player: 台本テキストは"
                                                     "audit/tts_generation_results.json参照)",
                                                     audio_html))
    table_html = player_mod.render_timeline_table(rows)
    episode_url = f"./web/family_c_production_{article_id}_{level}.mp3"
    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>Family C Production evidence player: {article_id} {level}</title>
<style>{player_mod.PLAYER_STANDARD_CSS}</style>
<script>{player_mod.SEEK_SCRIPT}</script>
</head><body>
<h1>Family C Production Wiring runtime evidence(ユーザー実検証用ではない)</h1>
<p>duration={run_summary['duration_seconds']}s</p>
<audio id="episode_audio" class="main" controls preload="none" src="{episode_url}"></audio>
{table_html}
</body></html>"""
    with open(f"{out_dir}/player.html", "w", encoding="utf-8") as f:
        f.write(html)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--level", choices=["a2", "b1"], required=True)
    parser.add_argument("--plan-only", action="store_true")
    parser.add_argument("--comments-only", action="store_true")
    parser.add_argument("--no-tts", action="store_true")
    parser.add_argument("--budget-jpy", type=float, default=10.0)
    parser.add_argument("--only-segments", nargs="+", default=None)
    parser.add_argument("--resume", dest="resume", action="store_true", default=True)
    parser.add_argument("--no-resume", dest="resume", action="store_false")
    args = parser.parse_args()

    config = load_config(args.config)
    out_dir = os.path.dirname(os.path.abspath(args.config))

    if args.plan_only:
        run_plan_only(config, args.level, out_dir)
        return
    if args.comments_only:
        run_comments_only(config, args.level, out_dir, args.budget_jpy, args.no_tts)
        return

    run_full_generation(config, args.level, out_dir, args.budget_jpy, args.only_segments, args.resume)


if __name__ == "__main__":
    main()
