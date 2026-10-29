# -*- coding: utf-8 -*-
"""NUANCE-EXPLANATION-PRODUCTION-WIRING-01 委任_02C Track E: runnerが er0XX_output/ 配下のpathを要求するため、repo外のcopy-runへ NTFS junction を張る/外す(KCP EVIDENCE_Y_01の先例)。
  py .../junction_01.py add    --link er121_output/.../run_nxw_a --target C:/.../NXW02C/y/run_nxw_a
  py .../junction_01.py remove --link er121_output/.../run_nxw_a      (junction自体だけを除去。target内のファイルは消えない)
removeはjunction(reparse point)であることを確認してからos.rmdirする(通常のdirは消さない)。API 0。"""
import argparse
import os
import stat
import sys


def is_junction(p: str) -> bool:
    try:
        st = os.lstat(p)
    except OSError:
        return False
    return bool(getattr(st, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("op", choices=("add", "remove", "check"))
    ap.add_argument("--link", required=True)
    ap.add_argument("--target", default=None)
    a = ap.parse_args(argv)
    link = os.path.abspath(a.link)
    if a.op == "add":
        import _winapi
        if os.path.exists(link) or is_junction(link):
            raise SystemExit(f"既に存在します: {link}")
        if not a.target or not os.path.isdir(a.target):
            raise SystemExit(f"--target がありません: {a.target}")
        os.makedirs(os.path.dirname(link), exist_ok=True)
        _winapi.CreateJunction(os.path.abspath(a.target), link)
        mp = os.path.join(link, "EVIDENCE_COPY_RUN.json")
        if os.path.exists(mp):   # copy-runの印は『runnerが使うpath(junction)』を指す(nuance-issue-specが--runと照合する)
            import json
            mk = json.load(open(mp, encoding="utf-8"))
            mk["copy_run"], mk["storage_path"] = link, os.path.abspath(a.target)
            json.dump(mk, open(mp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"junction added: {link} -> {os.path.abspath(a.target)}")
    elif a.op == "remove":
        if not is_junction(link):
            raise SystemExit(f"junctionではありません(消しません): {link}")
        os.rmdir(link)
        print(f"junction removed: {link}")
    else:
        print(is_junction(link))
    return 0


if __name__ == "__main__":
    sys.exit(main())
