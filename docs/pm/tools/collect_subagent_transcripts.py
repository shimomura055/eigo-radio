#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
collect_subagent_transcripts.py

管理ID: PM-TOKEN-EFFICIENCY-F1-ZERO-BYTE-TRANSCRIPT-ROOT-CAUSE-01
性質: 観測性改善Trial(提案)。Production経路ではない。運用ルール恒久変更ではない。

背景(原因の要約):
  Claude Codeのsubagent委任完了通知<task-notification>が指す
  tasks/<taskId>.output は、harness側の書き込みが不安定であり、
  約1/3のケースで「作成はされるが一度も書き込まれない」まま
  (birth時刻==modify時刻)恒久的に0バイトで残ることが判明した。
  一方、Claude Code自身が標準で逐次追記しているsubagentの
  完全な会話ログが、同じセッションディレクトリ配下の
    <projectDir>/<sessionId>/subagents/agent-<taskId>.jsonl
  に実行中からリアルタイムで書かれており、tasks/*.outputが0バイトの
  場合でもこちらは高確率(観測ではa-prefixの全件=100%)で
  完全な内容を保持している。

このスクリプトの機能:
  1. tasks_dir 配下の 0バイトの *.output を列挙する。
  2. 各taskIdについて subagents_dir/agent-<taskId>.jsonl が存在し、
     かつサイズが0でなければ「復元可能」と判定する。
  3. --apply指定時のみ、docs/pm/transcripts/ 配下へ
     "<taskId>_recovered.jsonl" という新規ファイル名で追記コピーする
     (既存ファイルの上書き・削除は一切行わない)。
  4. --transcripts-dir配下に既に "<taskId>*.output" や
     "<taskId>_recovered.jsonl" が存在する場合はスキップする
     (二重コピー防止)。
  5. 合計コピーサイズが --max-total-mb (既定20MB) を超える場合は
     そこで打ち切り、残りは件数のみ報告する(サイズ上限超過分は
     コピーしない)。

安全性:
  - 読み取り専用のソース走査+新規ファイル追加のみ。既存ファイルの
    上書き・削除・移動は行わない。
  - API呼び出し、SSOT編集、Git操作は一切行わない。
  - 既定はdry-run(--applyを渡すまで実際には書き込まない)。
"""
import argparse
import os
import sys
import glob


def human_mb(n):
    return n / (1024 * 1024)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tasks-dir", required=True,
                     help="harnessのtasks出力ディレクトリ (tasks/*.output)")
    ap.add_argument("--subagents-dir", required=True,
                     help="Claude Code自身のsubagentログディレクトリ (subagents/agent-*.jsonl)")
    ap.add_argument("--transcripts-dir", required=True,
                     help="復元先 (docs/pm/transcripts/)")
    ap.add_argument("--max-total-mb", type=float, default=20.0,
                     help="今回の実行で追加コピーする合計サイズ上限(MB)")
    ap.add_argument("--apply", action="store_true",
                     help="指定時のみ実際にファイルを書き込む(既定はdry-run)")
    ap.add_argument("--only-existing-placeholders", action="store_true",
                     help="transcripts-dirに既に<taskId>*.outputとして"
                          "退避済み(0バイトのまま)のtaskIdだけを対象にする。"
                          "repoサイズ影響を抑えつつ、既に報告済みの0バイト"
                          "ケースだけを補修したい場合に使う。")
    args = ap.parse_args()

    zero_outputs = []
    for path in glob.glob(os.path.join(args.tasks_dir, "*.output")):
        try:
            if os.path.getsize(path) == 0:
                zero_outputs.append(path)
        except OSError:
            continue

    if args.only_existing_placeholders:
        placeholder_ids = set()
        for p in glob.glob(os.path.join(args.transcripts_dir, "*.output")):
            base = os.path.basename(p)
            name_no_ext = os.path.splitext(base)[0]
            # ファイル名は "<管理ID>_<ラベル>_<taskId>" の形式。
            # taskIdは末尾のアンダースコア区切りトークン。
            task_id = name_no_ext.rsplit("_", 1)[-1]
            if os.path.getsize(p) == 0:
                placeholder_ids.add(task_id)
        zero_outputs = [p for p in zero_outputs
                         if os.path.splitext(os.path.basename(p))[0] in placeholder_ids]

    recoverable = []
    for path in zero_outputs:
        task_id = os.path.splitext(os.path.basename(path))[0]
        alt_path = os.path.join(args.subagents_dir, "agent-%s.jsonl" % task_id)
        if os.path.exists(alt_path) and os.path.getsize(alt_path) > 0:
            recoverable.append((task_id, alt_path, os.path.getsize(alt_path)))

    print("zero-byte tasks/*.output: %d" % len(zero_outputs))
    print("recoverable via subagents/*.jsonl: %d" % len(recoverable))

    already_present = set()
    for p in glob.glob(os.path.join(args.transcripts_dir, "*")):
        already_present.add(os.path.basename(p))

    total_bytes = 0
    max_bytes = int(args.max_total_mb * 1024 * 1024)
    copied = []
    skipped_exists = []
    skipped_size_cap = []

    for task_id, alt_path, size in recoverable:
        dest_name = "%s_recovered.jsonl" % task_id
        already = any(dest_name == name or name.startswith(task_id)
                       for name in already_present)
        if already:
            skipped_exists.append(task_id)
            continue
        if total_bytes + size > max_bytes:
            skipped_size_cap.append((task_id, size))
            continue
        dest_path = os.path.join(args.transcripts_dir, dest_name)
        if args.apply:
            with open(alt_path, "rb") as src, open(dest_path, "wb") as dst:
                dst.write(src.read())
        copied.append((task_id, dest_path, size))
        total_bytes += size

    mode = "APPLY" if args.apply else "DRY-RUN"
    print("mode: %s" % mode)
    print("copied (or would copy): %d files, %.2f MB" % (len(copied), human_mb(total_bytes)))
    for task_id, dest_path, size in copied:
        print("  + %s  (%.2f MB) -> %s" % (task_id, human_mb(size), dest_path))
    print("skipped (already present in transcripts-dir): %d" % len(skipped_exists))
    print("skipped (size cap reached, not copied): %d" % len(skipped_size_cap))
    for task_id, size in skipped_size_cap:
        print("  ! %s  (%.2f MB)" % (task_id, human_mb(size)))

    return 0


if __name__ == "__main__":
    sys.exit(main())
