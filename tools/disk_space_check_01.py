"""disk_space_check_01: disk_guard_01 --hook の薄い別名(旧単独実装は撤去、DISK-GUARD-AUTO-CLEANUP-01 R-7)。
空き容量を1行で表示(常にrc=0)。WARN以上は「Fableは即時報告すること」付き。引数はdisk_guard_01へそのまま渡す。API 0。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import disk_guard_01  # noqa: E402

if __name__ == "__main__":
    _rc = disk_guard_01.main(["--hook"] + sys.argv[1:])
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(_rc)  # stdin読取threadが残っても確実に終了
