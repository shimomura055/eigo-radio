#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
docs/pm/tools/measure_delegation_task.py

PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-TRIAL-DESIGN-01(施策1 Trial)向けの
read-only計測ツール。Production/QA/Promptには一切関与しない($0、API呼び出しなし)。

目的: 1件のSonnet/Opus委任(taskId)について、施策1 Trial設計書が定義する
指標(tool_uses、累積usage、最終ターンcontext、tool_result文字数、
同一ファイル再読率、全文Read率、duration)をJSONで出力する。

taskIdの解決順序(F-1恒久手順に準拠、docs/pm/PM_GOVERNANCE.md F-1節参照):
  1. <PROJECTS_BASE>/*/subagents/agent-<taskId>.jsonl (非0バイト)
  2. docs/pm/transcripts/<taskId>_recovered.jsonl (F-1退避済み代替)
どちらも見つからない/0バイトの場合はエラーを返す(推測しない)。

分析ロジックはPM-TOKEN-EFFICIENCY-E1-D1-REMEASUREMENT-01のscratchpad
`remeasure_e1_d1_01.py`のanalyze_task()と同一定義を踏襲し、
er011_pm_agent_read_audit_01.py(無変更)のclassify_path/
bash_command_read_targets/tool_result_text_len/extract_mgmt_idを
importして再利用する(同一定義の再利用、独自の再定義はしない)。

使い方:
  python docs/pm/tools/measure_delegation_task.py --task-id <taskId>
  python docs/pm/tools/measure_delegation_task.py --task-id <taskId> --pretty

出力(stdout, JSON 1件):
  {
    "task_id": ...,
    "source": "subagents"|"docs/pm/transcripts recovered",
    "source_path": ...,
    "tool_uses": ...,               # Read/Grep/Glob/Bash呼び出し回数(結果を伴うもの)
    "cumulative_usage": ...,        # 全ターンのinput+output+cache_read+cache_creation合計
    "final_context_size": ...,      # 最終ターンのinput+cache_read+cache_creation
    "tool_result_total_chars": ...,
    "same_file_reread_rate": ...,   # 文字ベース
    "full_read_rate_by_chars": ...,
    "full_read_rate_by_calls": ...,
    "duration_seconds": ...,        # first_ts〜last_tsの差(秒)
    "n_turns": ...,
    "edit_write_count": ...,
    "models_seen": [...]
  }
"""
import argparse
import glob
import json
import os
import re
import sys
from datetime import datetime

REPO_ROOT = r"C:\Users\tensh\eigo-radio"
PROJECTS_BASE = r"C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio"
TRANSCRIPTS_DIR = os.path.join(REPO_ROOT, "docs", "pm", "transcripts")

sys.path.insert(0, REPO_ROOT)
import er011_pm_agent_read_audit_01 as audit  # noqa: E402

extract_mgmt_id = audit.extract_mgmt_id
classify_path = audit.classify_path
bash_command_read_targets = audit.bash_command_read_targets
tool_result_text_len = audit.tool_result_text_len


def resolve_transcript_path(task_id):
    """F-1恒久手順の解決順序どおり: (1) subagents/agent-<id>.jsonl 非0バイト、
    (2) docs/pm/transcripts/<id>_recovered.jsonl。見つからなければ None。"""
    candidates = glob.glob(
        os.path.join(PROJECTS_BASE, "*", "subagents", f"agent-{task_id}.jsonl")
    )
    for c in candidates:
        if os.path.isfile(c) and os.path.getsize(c) > 0:
            return c, "subagents"

    recovered = os.path.join(TRANSCRIPTS_DIR, f"{task_id}_recovered.jsonl")
    if os.path.isfile(recovered) and os.path.getsize(recovered) > 0:
        return recovered, "docs/pm/transcripts recovered"

    return None, None


def parse_ts(ts):
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


def analyze_task(path):
    """PM-TOKEN-EFFICIENCY-E1-D1-REMEASUREMENT-01のanalyze_task()と同一定義。"""
    pending_tool_use = {}
    file_seen = set()
    total_chars = 0
    reread_chars = 0
    read_calls = 0
    read_chars = 0
    full_read_calls = 0
    full_read_chars = 0
    prod_code_chars = 0
    git_chars = 0
    tool_call_count = 0
    edit_write_count = 0
    usage_by_msgid = {}
    first_ts = None
    last_ts = None
    model_seen = set()

    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except Exception:
                continue
            if not isinstance(d, dict):
                continue
            ts = d.get("timestamp")
            if ts:
                if first_ts is None:
                    first_ts = ts
                last_ts = ts
            dtype = d.get("type")

            if dtype == "assistant":
                msg = d.get("message", {})
                model = msg.get("model")
                if model:
                    model_seen.add(model)
                mid = msg.get("id")
                usage = msg.get("usage")
                if mid and usage:
                    usage_by_msgid[mid] = usage
                content = msg.get("content", [])
                if isinstance(content, list):
                    for c in content:
                        if isinstance(c, dict) and c.get("type") == "tool_use":
                            pending_tool_use[c.get("id")] = {
                                "name": c.get("name"),
                                "input": c.get("input", {}) or {},
                            }

            if dtype == "user":
                msg = d.get("message", {})
                content = msg.get("content")
                if isinstance(content, list):
                    for c in content:
                        if isinstance(c, dict) and c.get("type") == "tool_result":
                            tu = pending_tool_use.pop(c.get("tool_use_id"), None)
                            if tu is None:
                                continue
                            name = tu["name"]
                            tinput = tu["input"]
                            if name in ("Edit", "Write", "MultiEdit"):
                                edit_write_count += 1
                                continue
                            if name not in ("Read", "Grep", "Glob", "Bash"):
                                continue
                            chars = tool_result_text_len(c.get("content"))
                            tool_call_count += 1
                            total_chars += chars
                            file_key = None
                            if name == "Read":
                                fp = tinput.get("file_path")
                                offset = tinput.get("offset")
                                limit = tinput.get("limit")
                                read_calls += 1
                                read_chars += chars
                                is_full = offset is None and limit is None
                                if is_full:
                                    full_read_calls += 1
                                    full_read_chars += chars
                                cat = classify_path(fp)
                                if cat == "production_code_er0x_py":
                                    prod_code_chars += chars
                                file_key = fp
                            elif name == "Grep":
                                gpath = tinput.get("path")
                                cat = classify_path(gpath) if gpath else "unknown"
                                if cat == "production_code_er0x_py":
                                    prod_code_chars += chars
                                file_key = gpath
                            elif name == "Glob":
                                file_key = tinput.get("path") or tinput.get("pattern")
                            elif name == "Bash":
                                cmd = tinput.get("command", "") or ""
                                is_read_like, cats, matched_files = bash_command_read_targets(cmd)
                                if "production_code_er0x_py" in cats:
                                    prod_code_chars += chars
                                if re.search(r"(^|[\s;&|])git\s", cmd) or cmd.strip().startswith("git "):
                                    git_chars += chars
                                file_key = matched_files[0] if matched_files else None

                            if file_key:
                                fk_norm = file_key.replace("\\", "/").lower()
                                if fk_norm in file_seen:
                                    reread_chars += chars
                                else:
                                    file_seen.add(fk_norm)

    sum_input = sum_output = sum_cache_read = sum_cache_creation = 0
    for mid, u in usage_by_msgid.items():
        sum_input += u.get("input_tokens", 0) or 0
        sum_output += u.get("output_tokens", 0) or 0
        sum_cache_read += u.get("cache_read_input_tokens", 0) or 0
        sum_cache_creation += u.get("cache_creation_input_tokens", 0) or 0
    cumulative_usage = sum_input + sum_output + sum_cache_read + sum_cache_creation

    final_context = None
    if usage_by_msgid:
        last_mid = list(usage_by_msgid.keys())[-1]
        u = usage_by_msgid[last_mid]
        final_context = (
            (u.get("input_tokens", 0) or 0)
            + (u.get("cache_read_input_tokens", 0) or 0)
            + (u.get("cache_creation_input_tokens", 0) or 0)
        )

    duration_seconds = None
    t0 = parse_ts(first_ts)
    t1 = parse_ts(last_ts)
    if t0 and t1:
        duration_seconds = (t1 - t0).total_seconds()

    return {
        "tool_uses": tool_call_count,
        "cumulative_usage": cumulative_usage,
        "final_context_size": final_context,
        "tool_result_total_chars": total_chars,
        "same_file_reread_rate": (reread_chars / total_chars) if total_chars else None,
        "full_read_rate_by_chars": (full_read_chars / read_chars) if read_chars else None,
        "full_read_rate_by_calls": (full_read_calls / read_calls) if read_calls else None,
        "read_calls": read_calls,
        "prod_code_ratio": (prod_code_chars / total_chars) if total_chars else None,
        "git_ratio": (git_chars / total_chars) if total_chars else None,
        "duration_seconds": duration_seconds,
        "n_turns": len(usage_by_msgid),
        "edit_write_count": edit_write_count,
        "models_seen": sorted(model_seen),
        "first_ts": first_ts,
        "last_ts": last_ts,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--task-id", required=True, help="agentId/taskId (agent-<id>.jsonlの<id>部分)")
    ap.add_argument("--pretty", action="store_true", help="JSONを整形出力する")
    args = ap.parse_args()

    path, source = resolve_transcript_path(args.task_id)
    if not path:
        print(json.dumps({
            "task_id": args.task_id,
            "error": "transcript not found (checked subagents/agent-<id>.jsonl and "
                     "docs/pm/transcripts/<id>_recovered.jsonl; not 0-byte substitute made)",
        }, ensure_ascii=False, indent=2 if args.pretty else None))
        sys.exit(1)

    metrics = analyze_task(path)
    result = {"task_id": args.task_id, "source": source, "source_path": path}
    result.update(metrics)
    print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()
