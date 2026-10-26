# -*- coding: utf-8 -*-
"""FAMILY-Y-VOICE1-MALE7-TRIAL-01: 生成計画の決定論生成(API 0)。ラウンドロビン順序・起動ごとの開始Voice回転・batch分割。
使い方: py ym7_plan_01.py phase1 --out plan_phase1.json [--nbatch 3]
        py ym7_plan_01.py phase2 --voices Fenrir,Orus,Algieba --out plan_phase2.json [--nbatch 3] [--first-take 3]"""
import argparse, json

NEW_VOICES = ["Fenrir", "Orus", "Puck", "Iapetus", "Sadaltager"]
CELLS = [(lv, b) for b in (1, 2, 3) for lv in ("a2", "b1b")]          # 6 cell(本文×レベル)


CONTROL = {"voice": "Algieba", "cells": [("a2", 1), ("b1b", 1)]}     # Phase 1のみ: Algieba本文1は再利用が過去日(run_01/候補take)のみ→同一セッションの対照(各2 take)


def build(voices, takes, first_take, nbatch, control=False):
    """items: ラウンド(take序数)→cell→Voiceの順に並べ、Voice位置を (j + cell_idx + round) で回転=特定Voiceが常に先頭/末尾にならない。"""
    items = []
    for r in range(takes):
        for ci, (lv, b) in enumerate(CELLS):
            vs = list(voices) + ([CONTROL["voice"]] if control and (lv, b) in CONTROL["cells"] and CONTROL["voice"] not in voices else [])
            n = len(vs)
            for j in range(n):
                v = vs[(j + ci + r) % n]
                items.append({"level": lv, "body": b, "voice": v, "take": first_take + r})
    cnt = {}                                    # (batch,voice)→件数、(batch,)→総数。決定論的な貪欲割当=各batchのVoice数を均す
    tot = [0] * nbatch
    for i, it in enumerate(items):
        it["seq"] = i
        bi = min(range(nbatch), key=lambda x: (cnt.get((x, it["voice"]), 0), tot[x], (x - i) % nbatch))
        cnt[(bi, it["voice"])] = cnt.get((bi, it["voice"]), 0) + 1
        tot[bi] += 1
        it["batch"] = bi + 1                    # 各batch内も元のラウンドロビン順を保つ
    return items


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("phase", choices=("phase1", "phase2"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--nbatch", type=int, default=3)
    ap.add_argument("--voices", default=",".join(NEW_VOICES))
    ap.add_argument("--takes", type=int, default=2)
    ap.add_argument("--first-take", type=int, default=1)
    ap.add_argument("--control", action="store_true", help="Phase 1: Algieba本文1の同一セッション対照を含める")
    a = ap.parse_args(argv)
    voices = a.voices.split(",")
    items = build(voices, a.takes, a.first_take, a.nbatch, a.control)
    json.dump({"phase": a.phase, "voices": voices, "nbatch": a.nbatch, "n_items": len(items), "items": items}, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(a.out, len(items), "items")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
