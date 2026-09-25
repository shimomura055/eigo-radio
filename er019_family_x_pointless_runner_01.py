# ============================================================
# er019_family_x_pointless_runner_01.py
# NEWS-FAMILY-X-POINTLESS-TRIAL-01 Phase B(Trial専用runner、DEV/Trial
# path。Production正式経路[er012_e_family_entertainment_two_level_
# runner_01.py]とは完全に別のスクリプトであり、Family Aの既存出力
# [er012_output/...]には一切書き込まない)
# ============================================================
# 設計書: docs/pm/recon_family_x_pointless_trial_01.md
#
# Point構造(Point One/Two・Point Notification効果音・Key Phrase)を
# 持たないFamily X(3分割)のE2E runner。既存Family A記事(article.md)の
# Main Story部分のみを再利用し(Writer再実行なし、Point節は内容ごと
# 破棄)、Comment 1-4(3/4のみPoint前提を除去した新role)→TTS→Assembly→
# player.htmlまでを実行する。Key Phraseは生成しない。
#
# stage構成・budget guard・--tts-mode/--batch-reason CLIは既存
# er012_e_family_entertainment_two_level_runner_01.py(Production正式
# runner)と同型のパターンを踏襲するが、themeのwriter stageは「既存
# article.md読み込み+3分割」に差し替える(新しいWriter/Ledger呼び出しは
# 行わない)。コスト計算ロジック(compute_cost_jpy_so_far/assert_budget_
# ok/_load_pricing)は同一の正本を保つため、er012 runnerから読み取り
#専用でimportして再利用する(コピーしない、Family A側ファイルへの
# 書き込みは一切ない)。
#
# 実行方法:
#   .venv/Scripts/python.exe er019_family_x_pointless_runner_01.py \
#       --source-article-md <既存Family A article.mdのpath> --slug meta \
#       --out-dir er019_output/family_x_pointless_trial_01/meta \
#       --budget-jpy 35 \
#       --stage dry-run|writer|scaffold|tts|assemble|player|all \
#       [--tts-mode STANDARD|BATCH(既定STANDARD)] [--batch-reason "..."]

from __future__ import annotations

import argparse
import json
import os
import time

import audio_review_player as player_common
import er005_cost_logger as cl
import er012_e_family_entertainment_two_level_runner_01 as e2l_runner
import er019_family_x_pointless_assemble_01 as fx_asm
import er019_family_x_pointless_scaffold_01 as fx_sc
import er019_family_x_pointless_tts_01 as fx_tts

DEFAULT_SOURCE_ARTICLE_MD = "er012_output/e_family_two_level_wiring_01/meta/b1b/article.md"


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


# ------------------------------------------------------------
# dry-run(PM_GOVERNANCE 7-5: API呼び出し前にsegment一覧・件数を出力する)
# ------------------------------------------------------------
def run_dry_run(source_article_md: str, out_dir: str) -> dict:
    article_text = load_text(source_article_md)
    parts = fx_sc.split_article_text_3way(article_text)

    planned_llm_text_calls = ["preview", "comment_1", "comment_2", "comment_3", "comment_4"]
    planned_tts_segments = [
        "topic_intro", "preview", "comment_1", "comment_2", "comment_3", "comment_4",
        "full_story_part1", "full_story_part2", "full_story_part3", "in_one_line",
    ]
    planned_shared_narration_reuse = ["welcome_charon", "preview_intro_charon", "full_story_intro_charon"]

    report = {
        "source_article_md": source_article_md,
        "split_word_counts": parts["split_word_counts"],
        "planned_llm_text_calls": planned_llm_text_calls,
        "planned_llm_text_call_count": len(planned_llm_text_calls),
        "planned_tts_segments": planned_tts_segments,
        "planned_tts_segment_count": len(planned_tts_segments),
        "planned_shared_narration_reuse_via_master_audio_store": planned_shared_narration_reuse,
        "key_phrase_generation": "NONE(Fable指示によりこのTrialでは生成しない)",
        "point_segments": "NONE(point_one/two_heading・point_one/two・Point Notification効果音は一切含まない)",
        "regeneration_risk_check": "Family A側の既存出力(er012_output/e_family_two_level_wiring_01/...)へは"
                                    "一切書き込まない。全出力はer019_output/family_x_pointless_trial_01/配下の新規path。",
    }
    save_json(f"{out_dir}/dry_run_report.json", report)
    print("[FAMILY-X-RUNNER][dry-run] " + json.dumps(report, ensure_ascii=False, indent=2))
    return report


# ------------------------------------------------------------
# writer stage(新規Writer呼び出しなし。既存article.mdの3分割のみ)
# ------------------------------------------------------------
def run_writer_stage(source_article_md: str, out_dir: str) -> dict:
    b1b_dir = f"{out_dir}/b1b"
    os.makedirs(f"{b1b_dir}/audit", exist_ok=True)
    article_text = load_text(source_article_md)
    parts = fx_sc.split_article_text_3way(article_text)
    # 由来確認用に、参照した既存Family A article.mdをそのままコピー保存する
    # (Family A側の原本ファイル自体は一切変更しない、読み取り専用参照)。
    save_text(f"{b1b_dir}/source_article_reference.md", article_text)
    save_json(f"{b1b_dir}/parts.json", parts)
    print(f"[FAMILY-X-RUNNER] writer stage完了: part1={parts['split_word_counts']['part1']}語 "
          f"part2={parts['split_word_counts']['part2']}語 part3={parts['split_word_counts']['part3']}語")
    return parts


# ------------------------------------------------------------
# scaffold / tts / assemble stage
# ------------------------------------------------------------
def run_scaffold_stage(client, theme: dict) -> dict:
    b1b_dir = f"{theme['out_dir']}/b1b"
    parts = load_json(f"{b1b_dir}/parts.json")
    return fx_sc.run_family_x_b1_scaffold(client, parts, b1b_dir)


def run_tts_stage(theme: dict) -> dict:
    return fx_tts.generate_family_x_b1_segments(theme)


def run_assemble_stage(theme: dict) -> dict:
    out_dir = theme["out_dir"]
    try:
        result = fx_asm.stage_assemble_family_x_b1(theme)
    except RuntimeError as e:
        print(f"[FAMILY-X-RUNNER][assemble/b1b] GATE_BLOCKED(override無し、報告のみ): {e}")
        result = {"status": "GATE_BLOCKED", "error": str(e)}
        save_json(f"{out_dir}/b1b/run_summary_assemble.json", result)
    return {"b1b": result}


# ------------------------------------------------------------
# player.html(既存audio_review_player共有ヘルパーを再利用)
# ------------------------------------------------------------
def _row_info_family_x_b1b(label: str, parts: dict, support: dict, narration_dir: str) -> dict:
    charon, aoede = "Charon", "Aoede"
    if label in ("Intro", "Outro (Charon)"):
        return {"text": "音楽ジングル/固定音源(読み上げなし)。", "voice": None, "audio": None, "sfx": True}
    if label.startswith("Notification"):
        return {"text": "効果音(読み上げなし)", "voice": None, "audio": None, "sfx": True}
    if label == "Welcome (Charon)":
        return {"text": "(共有固定Welcome、Master Audio Store)", "voice": charon,
                "audio": f"{narration_dir}/welcome_charon.wav", "sfx": False}
    if label == "Topic intro (Charon)":
        return {"text": f"Today's topic is {parts['title']}.", "voice": charon,
                "audio": f"{narration_dir}/topic_intro.wav", "sfx": False}
    if label == "Preview intro (Charon)":
        return {"text": "(共有固定Preview intro)", "voice": charon,
                "audio": f"{narration_dir}/preview_intro_charon.wav", "sfx": False}
    if label == "Preview (Charon)":
        return {"text": support["preview"], "voice": charon, "audio": f"{narration_dir}/preview.wav", "sfx": False}
    if label == "Full story intro (Charon)":
        return {"text": "(共有固定Full story intro)", "voice": charon,
                "audio": f"{narration_dir}/full_story_intro_charon.wav", "sfx": False}
    if label.startswith("Comment 1"):
        return {"text": support["comment_1"], "voice": charon, "audio": f"{narration_dir}/comment_1.wav", "sfx": False}
    if label.startswith("Comment 2"):
        return {"text": support["comment_2"], "voice": charon, "audio": f"{narration_dir}/comment_2.wav", "sfx": False}
    if label.startswith("Comment 3"):
        return {"text": support["comment_3"], "voice": charon, "audio": f"{narration_dir}/comment_3.wav", "sfx": False}
    if label.startswith("Comment 4"):
        return {"text": support["comment_4"], "voice": charon, "audio": f"{narration_dir}/comment_4.wav", "sfx": False}
    if label.startswith("Full Story Part 1"):
        return {"text": parts["part1"], "voice": aoede, "audio": f"{narration_dir}/full_story_part1.wav", "sfx": False}
    if label.startswith("Full Story Part 2"):
        return {"text": parts["part2"], "voice": aoede, "audio": f"{narration_dir}/full_story_part2.wav", "sfx": False}
    if label.startswith("Full Story Part 3"):
        return {"text": parts["part3"], "voice": aoede, "audio": f"{narration_dir}/full_story_part3.wav", "sfx": False}
    if label.startswith("In One Line"):
        return {"text": parts["in_one_line"], "voice": aoede, "audio": f"{narration_dir}/in_one_line.wav", "sfx": False}
    return {"text": "(共有固定segment、記事固有scriptなし)", "voice": None, "audio": None, "sfx": False}


def _build_family_x_b1b_table(level_dir: str) -> str:
    assemble_summary = load_json(f"{level_dir}/run_summary_assemble.json")
    if assemble_summary.get("status") != "OK":
        return f"<p style='color:#b00'>Assembly未完了(status={assemble_summary.get('status')})。table省略。</p>"
    timeline = load_json(f"{level_dir}/audit/timeline.json")
    parts = load_json(f"{level_dir}/parts.json")
    narration_dir = f"{level_dir}/narration"
    support = load_json(f"{level_dir}/b1_support_texts.json")
    abs_url = player_common.abs_file_url

    rows = []
    for entry in timeline:
        label = entry["part"]
        if label.startswith("pause_"):
            continue
        info = _row_info_family_x_b1b(label, parts, support, narration_dir)
        sec = entry["start_seconds"]
        voice_disp = info["voice"] or ("SFX" if info["sfx"] else "—")
        if info["sfx"] or not info["audio"]:
            audio_html = "—"
        else:
            audio_html = player_common.render_single_audio_html(abs_url(info["audio"]))
        rows.append(player_common.render_timeline_row(sec, label, voice_disp, info["text"], audio_html, missing=False))
    return player_common.render_timeline_table(rows)


def _build_individual_segments_table(level_dir: str) -> str:
    """Full episode assemblyがGATE_BLOCKEDでも、個別にVALIDATED/HUMAN_
    REVIEW_LOCKEDになったsegmentごとの音声はレビューできるようにする
    (安全≠成功原則: 未完成状態を隠さず、何がblockしているかを明示する)。"""
    results_path = f"{level_dir}/audit/tts_generation_results.json"
    if not os.path.exists(results_path):
        return "<p>segmentがまだ1件も生成されていません。</p>"
    data = load_json(results_path)
    parts = load_json(f"{level_dir}/parts.json")
    support = load_json(f"{level_dir}/b1_support_texts.json")
    narration_dir = f"{level_dir}/narration"
    abs_url = player_common.abs_file_url

    rows = []
    order = ["topic_intro", "preview", "comment_1", "full_story_part1", "comment_2", "full_story_part2",
             "comment_3", "full_story_part3", "comment_4", "in_one_line"]
    for name in order:
        entry = data.get("segments", {}).get(name)
        if entry is None:
            continue
        status = entry.get("status")
        text = entry.get("canonical_text") or "(text未取得)"
        wav_path = f"{narration_dir}/{name}.wav"
        audio_html = player_common.render_single_audio_html(abs_url(wav_path)) if os.path.exists(wav_path) else "—"
        label = f"{name} [{status}]"
        rows.append(player_common.render_timeline_row(0.0, label, "Charon/Aoede", text, audio_html, missing=False))
    return player_common.render_timeline_table(rows)


def build_player_html(theme: dict) -> str:
    out_dir = theme["out_dir"]
    abs_url = player_common.abs_file_url
    b1b_summary_path = f"{out_dir}/b1b/run_summary_assemble.json"
    b1b_summary = load_json(b1b_summary_path) if os.path.exists(b1b_summary_path) else \
        {"status": "NOT_ATTEMPTED_OR_GATE_BLOCKED_BEFORE_SUMMARY_WRITE"}

    if b1b_summary.get("status") == "OK":
        b1b_audio_html = (f'<h2>Family X(Pointless, B1、3分割)</h2>'
                           f'<audio class="main" controls preload="none" '
                           f'src="{abs_url(b1b_summary["out_path"])}"></audio>'
                           f'<p class="note">duration={b1b_summary["duration_seconds"]}s '
                           f'peak={b1b_summary["peak"]} clipping={b1b_summary["clipping_detected"]}</p>'
                           f'{_build_family_x_b1b_table(f"{out_dir}/b1b")}')
    else:
        b1b_audio_html = (f'<h2>Family X(Pointless, B1)</h2>'
                           f'<p style="color:#b00">Full episode assembly: status={b1b_summary.get("status")} '
                           f'(Audio Validation GateでBLOCKED。下記の個別segment単位で試聴・レビュー可能)</p>'
                           f'{_build_individual_segments_table(f"{out_dir}/b1b")}')

    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>NEWS-FAMILY-X-POINTLESS-TRIAL-01 player({theme['theme_id']})</title>
<style>
{player_common.PLAYER_STANDARD_CSS}
</style>
<script>
{player_common.SEEK_SCRIPT}
</script>
</head><body>
<h1>NEWS-FAMILY-X-POINTLESS-TRIAL-01({theme['theme_id']})</h1>
<p class="note">Trialスクリプト(er019_family_x_pointless_runner_01.py)による生成。
Point構造(Point One/Two・Point Notification効果音・Key Phrase)を持たない、
本文3分割構成(Comment1→Part1→Comment2→Part2→Comment3→Part3→Comment4→In One Line)。
最大分類VALIDATED、Production採用ではない。</p>
{b1b_audio_html}
</body></html>
"""
    out_path = f"{out_dir}/player.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    return out_path


# ------------------------------------------------------------
# CLI
# ------------------------------------------------------------
def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-article-md", default=DEFAULT_SOURCE_ARTICLE_MD,
                         help="再利用する既存Family A article.mdのpath(Writer再実行なし)")
    parser.add_argument("--slug", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--budget-jpy", type=float, default=35.0)
    parser.add_argument("--stage", default="all",
                         choices=("dry-run", "writer", "scaffold", "tts", "assemble", "player", "all"))
    parser.add_argument("--tts-mode", default="STANDARD", choices=("STANDARD", "BATCH"),
                         help="TTS実行方式(既定STANDARD、PM_GOVERNANCE.md 7-1)。"
                              "BATCH指定時は--batch-reason必須(7-2の例外条件)。")
    parser.add_argument("--batch-reason", default=None,
                         help="--tts-mode BATCH指定時に必須。PM_GOVERNANCE.md 7-2の例外条件に該当する理由を明記する。")
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    if args.tts_mode == "BATCH" and not args.batch_reason:
        parser.error("--tts-mode BATCH を指定する場合は --batch-reason で"
                      "PM_GOVERNANCE.md 7-2の例外条件に該当する理由を明示すること。")

    os.environ["TTS_EXECUTION_MODE"] = args.tts_mode
    os.makedirs(args.out_dir, exist_ok=True)

    if args.stage == "dry-run":
        run_dry_run(args.source_article_md, args.out_dir)
        return

    cl.install(f"{args.out_dir}/raw_usage_log.jsonl")

    save_json(f"{args.out_dir}/entry_point.json", {
        "runner": "er019_family_x_pointless_runner_01.py",
        "source_article_md": args.source_article_md,
        "source_article_md_sha256": e2l_runner.sha256_file(args.source_article_md),
        "slug": args.slug,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "tts_execution_mode": args.tts_mode,
        "tts_batch_reason": args.batch_reason,
        "note": "NEWS-FAMILY-X-POINTLESS-TRIAL-01 Phase B。DEV/Trial path、"
                "Production正式runnerではない。Key Phrase生成なし、Point構造なし。",
    })

    theme = {"theme_id": args.slug, "out_dir": args.out_dir}

    if args.stage in ("writer", "all"):
        run_writer_stage(args.source_article_md, args.out_dir)
        e2l_runner.assert_budget_ok(args.out_dir, args.budget_jpy, "after writer")

    if args.stage in ("scaffold", "all"):
        client = fx_sc.get_client()
        run_scaffold_stage(client, theme)
        e2l_runner.assert_budget_ok(args.out_dir, args.budget_jpy, "after scaffold")

    if args.stage in ("tts", "all"):
        run_tts_stage(theme)
        e2l_runner.assert_budget_ok(args.out_dir, args.budget_jpy, "after tts")

    if args.stage in ("assemble", "all"):
        run_assemble_stage(theme)

    if args.stage in ("player", "all"):
        player_path = build_player_html(theme)
        print(f"[FAMILY-X-RUNNER] player.html: {os.path.abspath(player_path)}")

    final_jpy, by_provider = e2l_runner.compute_cost_jpy_so_far(f"{args.out_dir}/raw_usage_log.jsonl")
    print(f"[FAMILY-X-RUNNER] 完了。stage={args.stage} 累計費用(JPY)={final_jpy:.2f} by_provider={by_provider}")


if __name__ == "__main__":
    main()
