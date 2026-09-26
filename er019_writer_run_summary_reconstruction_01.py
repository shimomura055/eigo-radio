# ============================================================
# er019_writer_run_summary_reconstruction_01.py
# NEWS-FAMILY-X-B3-FACT-SELECTION-PRODUCTION-WIRING-01(Fable差し戻し1回目、
# Gate 3 #13対応)
# ============================================================
# 目的: er012_e_family_entertainment_two_level_runner_01.run_writer_stage()
# を`only="advanced"`/`only="standard"`へ分けて複数回呼んだ既存run
# (例: er019 production runner run_01)について、旧実装のバグ
# (呼び出しごとにwriter_run_summary.jsonを丸ごと上書きし、先に書いた
# stageのevidenceキーが消える)によって"advanced"キーが失われた
# writer_run_summary.jsonを、**手作業ではなくプログラムで**、
# 既存の生ログ(raw_usage_log.jsonl)と既存監査ファイル
# (b1b/audit/deviation_check.json、a2/audit/deviation_check.json、
# b1b/article.md、a2/article.md)から再構成する。
#
# 本ファイルはrun_writer_stage()自体を再実行しない(API呼び出し0)。
# 既に保存済みのファイルのみを読み、構造的に確実な事実(コード上の
# 呼び出し順序: generate -> deviation_check -> [MAJORなら再度
# generate -> deviation_check])だけから値を導出する。導出できない
# フィールドは絶対に推測で埋めず、該当stageを"reconstruction_status":
# "AMBIGUOUS_REQUIRES_MANUAL_REVIEW"として明示し、既存キーを保持する。
#
# 前提(コード上の不変条件、er012_e_family_entertainment_two_level_
# runner_01.run_writer_stage()を参照):
#   - `only="advanced"`のブロックは
#     generate_advanced_adaptation() -> run_deviation_check() の順に
#     API callを行い、MAJORなら同じ順序でもう1往復だけ行う
#     (最大4 call、最小2 call)。`only="standard"`も同型。
#   - er005_cost_logger.logging_context(theme, stage)配下のattempt_number
#     はプロセス起動ごとに(theme, stage, segment, provider, api)単位で
#     1から数え直される(モジュールレベルの_ATTEMPT_COUNTERSがプロセス
#     生存期間内でのみ有効なため)。よってattempt_number==1は
#     「新しいCLIプロセス実行(=新しいrun_writer_stage呼び出し系列)の
#     開始」を示す信頼できる境界信号として使える。
#   - 現在ディスク上のb1b/article.md・b1b/audit/deviation_check.json
#     (a2側も同様)は、そのstageについて最後に成功した呼び出しの
#     成果物である(失敗[persistent MAJOR]で終わった呼び出しは
#     article.md/parts.jsonを保存しないため、常に最後の成功呼び出しの
#     内容が残る)。したがって「そのstageタグの最後のinvocation
#     グループ」を使えば、ディスク上の現物と整合する。
#
# 実行方法:
#   .venv/Scripts/python.exe er019_writer_run_summary_reconstruction_01.py \
#       --out-dir er019_output/family_x_b3_production_wiring_01/run_01 \
#       [--dry-run]
# ============================================================
from __future__ import annotations

import argparse
import json
import os
import sys
import time

# Windows既定コンソールcodepage(cp932)ではタイトル中のem-dash等が
# UnicodeEncodeErrorになるため、標準出力をUTF-8へ固定する
# (ファイルへのjson.dump側は元々ensure_ascii=Falseでencoding="utf-8"
# 指定済みで問題なし。ここは標準出力の表示のみの対応)。
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import er003_v1_n3_01_advanced_adaptation_generate as adv_gen
import er003_v1_n3_01_standard_a2_generate as std_gen
import er012_e_family_entertainment_two_level_runner_01 as efam

MANAGEMENT_ID = "NEWS-FAMILY-X-B3-FACT-SELECTION-PRODUCTION-WIRING-01"

STAGE_DIRS = {"advanced": "b1b", "standard": "a2"}
STAGE_MODULES = {"advanced": adv_gen, "standard": std_gen}


def load_raw_log_entries(raw_log_path: str) -> list[dict]:
    entries = []
    if not os.path.exists(raw_log_path):
        return entries
    with open(raw_log_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entries.append(json.loads(line))
    return entries


def select_invocation_groups(entries: list[dict], stage: str) -> list[list[dict]]:
    """該当stageタグのAPI call entryを、プロセス実行(invocation)単位で
    グループ化する(attempt_number==1で新グループ開始、既存不変条件を
    利用。詳細はモジュールdocstring参照)。"""
    stage_entries = [
        e for e in entries
        if e.get("stage") == stage and e.get("provider") == "openai" and e.get("success")
    ]
    groups: list[list[dict]] = []
    for e in stage_entries:
        if e.get("attempt_number") == 1 or not groups:
            groups.append([e])
        else:
            groups[-1].append(e)
    return groups


def _reconstruct_stage_evidence(stage: str, out_dir: str, groups: list[list[dict]]) -> tuple[dict | None, str | None]:
    """1 stage("advanced"/"standard")分のevidenceを再構成する。
    戻り値: (evidence_dict または None, ambiguous理由文字列 または None)。"""
    if not groups:
        return None, f"raw_usage_log.jsonlに stage={stage!r} のentryが存在しません。"
    last_group = groups[-1]
    if len(last_group) not in (2, 4):
        return None, (
            f"stage={stage!r} の最終invocationのraw log entry数が{len(last_group)}件"
            "(期待値2[generate+deviation]または4[generate+deviation+再generate+再deviation])"
            "のため、コード上の呼び出し順序の不変条件が成立しません。自動再構成を行わず"
            "手動確認へ回します(推測で値を埋めません)。"
        )
    generate_entry = last_group[-2]
    deviation_entry_ts = last_group[-1].get("timestamp")

    module = STAGE_MODULES[stage]
    stage_dir = f"{out_dir}/{STAGE_DIRS[stage]}"
    article_path = f"{stage_dir}/article.md"
    deviation_path = f"{stage_dir}/audit/deviation_check.json"

    model_actual = generate_entry.get("model_id")
    model_requested = module.routing.require_model(module.PROCESS_LABEL, module.routing.WRITER_MODEL)
    usage = {
        "input_tokens": generate_entry.get("input_tokens"),
        "cached_input_tokens": generate_entry.get("cached_input_tokens"),
        "output_tokens": generate_entry.get("output_tokens"),
        "reasoning_tokens": generate_entry.get("reasoning_tokens"),
    }
    price_fn = module._load_pricing()
    cost_usd, cost_jpy = module._compute_cost_jpy(
        price_fn, model_actual,
        usage["input_tokens"] or 0, usage["cached_input_tokens"] or 0, usage["output_tokens"] or 0)

    article_text = efam.load_text(article_path) if os.path.exists(article_path) else ""
    deviation_status = None
    if os.path.exists(deviation_path):
        deviation_status = efam.load_json(deviation_path).get("overall_status")

    evidence = {
        "process_label": module.PROCESS_LABEL,
        "model_id_requested": model_requested,
        "model_id_actual": model_actual,
        "fallback_detected": model_actual != model_requested,
        "response_id": generate_entry.get("response_id"),
        "structure_status": "STRUCTURE_PASS",  # article.mdが存在する時点でgenerate_*側の
                                                 # STRUCTURE_PASS Gateを通過済み(RuntimeErrorに
                                                 # ならず保存されているため確実)。
        "attempts": 1,       # 構造Gate内部retryは、entry数が2/4ちょうどであること
                              # (=deviation retry以外の余分なAPI callが無いこと)から
                              # 消去法で1と確定できる(上のlen(last_group)検証を参照)。
        "retried": False,
        "retried_for_deviation": len(last_group) == 4,
        "deviation_overall_status": deviation_status,
        "usage": usage,
        "cost_usd": cost_usd,
        "cost_jpy": cost_jpy,
        "elapsed_seconds": generate_entry.get("elapsed_seconds"),
        "title": efam._extract_title(article_text),
    }
    if stage == "standard":
        adv_article_path = f"{out_dir}/b1b/article.md"
        adv_article_text = efam.load_text(adv_article_path) if os.path.exists(adv_article_path) else ""
        evidence["checks"] = std_gen.run_checks(adv_article_text, article_text)
    return evidence, None


def reconstruct_writer_run_summary(out_dir: str) -> dict:
    """out_dir配下のraw_usage_log.jsonl + 既存監査ファイルから、
    writer_run_summary.json相当の内容をプログラムで再構成し、
    由来(provenance)付きのdictを返す(ファイルへの書き込みは行わない、
    呼び出し元がsave_reconstructed_summary()等で明示的に保存する)。"""
    raw_log_path = f"{out_dir}/raw_usage_log.jsonl"
    entries = load_raw_log_entries(raw_log_path)

    result: dict = {}
    stage_notes: dict = {}
    source_response_ids: dict = {}

    for stage in ("advanced", "standard"):
        groups = select_invocation_groups(entries, stage)
        evidence, ambiguous_reason = _reconstruct_stage_evidence(stage, out_dir, groups)
        if evidence is not None:
            result[stage] = evidence
            source_response_ids[stage] = {
                "generate_response_id": evidence["response_id"],
                "invocation_group_size": len(groups[-1]) if groups else 0,
                "invocation_group_index_used": len(groups) - 1 if groups else None,
                "total_invocation_groups_found": len(groups),
            }
        else:
            stage_notes[stage] = ambiguous_reason

    provenance = {
        "method": "programmatic_reconstruction_from_raw_logs",
        "management_id": MANAGEMENT_ID,
        "reconstructed_by": "er019_writer_run_summary_reconstruction_01.reconstruct_writer_run_summary",
        "reconstructed_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "source_files": {
            "raw_usage_log": raw_log_path,
            "advanced_article": f"{out_dir}/b1b/article.md",
            "advanced_deviation_check": f"{out_dir}/b1b/audit/deviation_check.json",
            "standard_article": f"{out_dir}/a2/article.md",
            "standard_deviation_check": f"{out_dir}/a2/audit/deviation_check.json",
        },
        "source_response_ids": source_response_ids,
        "ambiguous_stages": stage_notes,
        "invariants_relied_upon": [
            "run_writer_stage()内のAPI呼び出し順序はgenerate->deviation_check"
            "(MAJORなら再度generate->deviation_check)で固定(コード読解により確認、"
            "推測ではない)。",
            "er005_cost_logger.attempt_numberはプロセス起動ごとに1から再カウントされる"
            "(_ATTEMPT_COUNTERSがモジュールレベルでプロセス生存期間のみ有効)ため、"
            "attempt_number==1を新invocationの開始境界として利用できる。",
            "ディスク上のarticle.md/deviation_check.jsonは、そのstageで最後に成功した"
            "呼び出しの成果物(persistent MAJOR停止時は保存されないため)。",
        ],
    }
    result["_reconstruction_provenance"] = provenance
    return result


def save_reconstructed_summary(out_dir: str, backup_suffix: str = "_pre_gate3_fix_buggy_overwrite") -> dict:
    """writer_run_summary.jsonを再構成結果で置き換える。置き換え前の
    (バグで上書きされ壊れていた)ファイルは削除せず、
    writer_run_summary{backup_suffix}.jsonとして退避保存する
    (2-3 Artifact supersession、削除しない)。"""
    reconstructed = reconstruct_writer_run_summary(out_dir)
    summary_path = f"{out_dir}/writer_run_summary.json"
    if os.path.exists(summary_path):
        with open(summary_path, encoding="utf-8") as f:
            old_content = f.read()
        backup_path = f"{out_dir}/writer_run_summary{backup_suffix}.json"
        with open(backup_path, "w", encoding="utf-8") as f:
            f.write(old_content)
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(reconstructed, f, ensure_ascii=False, indent=2)
    return reconstructed


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="run_writer_stage()分割呼び出しでadvanced/standard evidenceが"
                     "欠落したwriter_run_summary.jsonを、raw_usage_log.jsonl等の"
                     "既存生ログからプログラムで再構成する(API呼び出し0)。")
    parser.add_argument("--out-dir", required=True,
                         help="er019 production runnerのrun出力dir"
                              "(例: er019_output/family_x_b3_production_wiring_01/run_01)")
    parser.add_argument("--dry-run", action="store_true",
                         help="ファイルへ保存せず、再構成結果を標準出力へ表示するのみ。")
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()
    if args.dry_run:
        result = reconstruct_writer_run_summary(args.out_dir)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        result = save_reconstructed_summary(args.out_dir)
        print(f"[WRITER-SUMMARY-RECONSTRUCTION] {args.out_dir}/writer_run_summary.json を再構成・保存しました。")
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
