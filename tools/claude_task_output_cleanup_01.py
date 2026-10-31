"""claude_task_output_cleanup_01: Claude Code task出力(*.output)の掃除。dry-run既定、--applyで削除。

A1: サイズ>200MB かつ 最終更新60分以上前
A2: 現セッション以外のsessionフォルダの .output で最終更新24時間以上前
現セッション(--current-session)の200MB以下ファイル、直近60分以内更新ファイルは対象外。API 0・他へ未配線。
"""
import argparse
import glob
import os
import sys
import time

BASE = os.path.expandvars(r"%LOCALAPPDATA%\Temp\claude\C--Users-tensh-eigo-radio")


def candidates(base, current, now):
    for f in glob.glob(os.path.join(base, "*", "tasks", "*.output")):
        try:
            st = os.stat(f)
        except OSError:
            continue
        age = now - st.st_mtime
        sess = os.path.basename(os.path.dirname(os.path.dirname(f)))
        if st.st_size > 200 * 1024 ** 2 and age > 3600:
            yield "A1", f, st.st_size, st.st_mtime
        elif sess != current and age > 86400:
            yield "A2", f, st.st_size, st.st_mtime


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=BASE)
    ap.add_argument("--current-session", default="")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args(argv)
    now = time.time()
    n = tot = 0
    for cls, f, sz, mt in candidates(a.base, a.current_session, now):
        print(f"{cls}\t{sz}\t{time.strftime('%F %T', time.localtime(mt))}\t{f}", end="")
        if a.apply:
            try:
                os.remove(f)
                print("\tdeleted")
            except OSError as e:
                print(f"\tFAIL {e}")
                continue
        else:
            print("\tdry-run")
        n += 1
        tot += sz
    print(f"{'applied' if a.apply else 'dry-run'}: files={n} gb={tot / 1024 ** 3:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
