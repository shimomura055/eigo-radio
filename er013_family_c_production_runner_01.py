# ============================================================
# er013_family_c_production_runner_01.py
# 管理ID: FAMILY-C-SEGMENT-COMMENT-PRODUCTION-WIRING-AND-USER-TEST-INVENTORY-01
#         (委任A: Family C 2仕様のProduction wiring)
# ============================================================
# 目的: `er013_family_c_production_01.py`(Family C Story TTS segmentation
# 原則+A2 Comment理解ガイド型Contract、APPROVED_FOR_PRODUCTION)を実際に
# 呼び出すFamily C正式Production runner。記事固有の設定(本文path・Voice
# keyword・scene boundary・Comment content等)はJSON設定ファイル
# (`er013_output/family_c_production/<article>/article_config.json`)から
# 読み、本runnerが固定値で上書きすることはない。
#
# モード:
#   --plan-only        : TTSなし。plan_story_segments()の結果のみ
#                         evidence/segmentation_plan.json へ出力する(¥0)。
#   --comments-only     : level="a2"のみ対応。A2 Comment理解ガイド型Contract
#                         (generate_family_c_a2_comment)経由でComment 1〜3を
#                         実際にLLM生成し、evidence/a2_comment_runtime_
#                         evidence.json へ保存する(LLM費用のみ、TTSなし)。
#                         level="b1"で指定された場合は構造的にRuntimeError
#                         とする(B1誤適用防止)。
#
# 初回生成・retry・regeneration・fallback・resumeのいずれの呼び出し元からも
# `plan_story_segments()`と`generate_family_c_a2_comment()`
# (内部で`check_a2_comment_quality()`によるretryループを内包)という同一の
# Production関数を経由する。本runnerはTrial script
# (`er013_family_c_episode_trial_1[012]_*.py`)を一切import・参照しない。
# ============================================================
from __future__ import annotations

import argparse
import json
import os
import time

import er013_family_c_production_01 as fam_c


def load_config(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_article_paragraphs(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        text = f.read()
    return fam_c.split_into_paragraphs(text)


def build_plan_for_level(level_cfg: dict) -> dict:
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
    reconstruction_ok = (reconstructed == original)

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
        "reconstruction_matches_original": reconstruction_ok,
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--level", choices=["a2", "b1"], required=True)
    parser.add_argument("--plan-only", action="store_true")
    parser.add_argument("--comments-only", action="store_true")
    parser.add_argument("--no-tts", action="store_true")
    parser.add_argument("--budget-jpy", type=float, default=10.0)
    args = parser.parse_args()

    config = load_config(args.config)
    out_dir = os.path.dirname(os.path.abspath(args.config))

    if args.plan_only:
        run_plan_only(config, args.level, out_dir)
        return
    if args.comments_only:
        run_comments_only(config, args.level, out_dir, args.budget_jpy, args.no_tts)
        return

    raise SystemExit(
        "本runnerは今回のProduction Wiring委任(runtime evidence: --plan-only /"
        " --comments-only --no-tts)のみをサポートします。実TTSを伴う全体生成"
        "経路は本委任のQCD注意(不要な再生成禁止・完成音声の再TTS禁止)により"
        "本タスクでは実行しません。")


if __name__ == "__main__":
    main()
