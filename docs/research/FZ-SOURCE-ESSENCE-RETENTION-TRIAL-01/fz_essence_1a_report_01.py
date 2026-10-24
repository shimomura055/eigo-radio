# -*- coding: utf-8 -*-
"""1a結果の決定論集計+盲検コード付き比較原稿の生成(LLM呼出0)。
出力: <1a dir>/metrics_1a.json, <1a dir>/BLIND_1A.md(コードA〜Fのみ・アーム名なし), <1a dir>/BLIND_KEY_1A.json(読了後に開く)"""
import os, sys, json, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fz_essence_metrics_01 as m   # noqa: E402

BASE = "er026_output/family_z_dev_trials/fz_essence_01/the_tell_tale_heart/1a"
R0_REF = {"fp": 44, "tp": 23, "you": 4}


def verdict(x):
    fp, tp, you, words = x["fp_narration"], x["tp_narration"], x["you_narration"], x["words"]
    return {"reversed": fp <= 5 and tp > fp,
            "P": fp >= 30 and fp > tp and 2 <= you <= 8 and 330 <= words <= 470}


def main():
    rows = {}
    for arm in ("i", "ii", "iii"):
        for k in (1, 2):
            p = f"{BASE}/{arm}_s{k}/r1.md"
            if os.path.exists(p):
                x = m.metrics(open(p, encoding="utf-8").read())
                x.update(verdict(x))
                rows[f"{arm}_s{k}"] = x
    json.dump(rows, open(f"{BASE}/metrics_1a.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for k, v in rows.items():
        print(k, v)
    keys = sorted(rows)
    rnd = random.Random(20261025)
    order = keys[:]
    rnd.shuffle(order)
    codes = {c: k for c, k in zip("ABCDEF", order)}
    json.dump(codes, open(f"{BASE}/BLIND_KEY_1A.json", "w", encoding="utf-8"), indent=1)
    out = ["# BLIND_1A: 1a R1出力の盲検読み用(アーム名なし。対応表は BLIND_KEY_1A.json、読了後に開く)", ""]
    for c in "ABCDEF":
        if c in codes:
            out += [f"## コード {c}", "", open(f"{BASE}/{codes[c]}/r1.md", encoding="utf-8").read().strip(), ""]
    open(f"{BASE}/BLIND_1A.md", "w", encoding="utf-8").write("\n".join(out))


if __name__ == "__main__":
    main()
