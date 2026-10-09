# -*- coding: utf-8 -*-
"""任意ブロック(OPTIONAL_BLOCK_01 方式A)runner。本編と同じプロンプト・同じ検証・同じ呼び出し関数(run_eval_01)を使い、
入力だけ optional_block_items_01.json(22文、Fact事前対応付け済み)に差し替える。合否外。人間既知・Checker情報の別ファイルは開かない。
使い方: python run_optional_block_01.py --rep 1 --dry-run
        python run_optional_block_01.py --rep 1 --max-yen 15"""
import argparse, os, sys
import run_eval_01 as R

HERE = os.path.dirname(os.path.abspath(__file__))
OPT_ITEMS = os.path.join(HERE, "optional_block_items_01.json")
MODEL = "gpt-6-luna"  # 任意ブロックは主評価者のみ(5.6-lunaは実施しない)


def opt_paths(model, rep):
    return (os.path.join(HERE, "results", "optional_block_%s_rep%d.jsonl" % (model, rep)),
            os.path.join(HERE, "logs", "optional_block_%s_rep%d_raw.jsonl" % (model, rep)))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--rep", type=int, default=1)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--max-yen", type=float, default=None)
    ap.add_argument("--temperature", type=float, default=0.0)
    a = ap.parse_args(argv)
    orig = R.paths
    R.paths = opt_paths
    try:
        items, prompt = R.load_items(OPT_ITEMS), R.load_prompt()
        if a.dry_run:
            return R.dry_run(MODEL, a.rep, items, prompt, a.max_yen, False)
        if a.max_yen is None:
            print("[REFUSED] --max-yen が必須です。")
            return 2
        return R.run(MODEL, a.rep, items, prompt, a.max_yen, a.temperature)
    finally:
        R.paths = orig


if __name__ == "__main__":
    sys.exit(main())
