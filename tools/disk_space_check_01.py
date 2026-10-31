"""disk_space_check_01: 空きGBを表示し、閾値未満ならrc=2。API 0・他へ未配線。"""
import argparse
import shutil
import sys


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", default="C:\\")
    ap.add_argument("--min-gb", type=float, default=10.0)
    a = ap.parse_args(argv)
    u = shutil.disk_usage(a.path)
    free = u.free / 1024 ** 3
    print(f"free_gb={free:.2f} total_gb={u.total / 1024 ** 3:.2f} min_gb={a.min_gb}")
    if free < a.min_gb:
        print("LOW_DISK: below threshold", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
