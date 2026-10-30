# -*- coding: utf-8 -*-
"""新armの実読ラベルを kpg04_work/audit/new_arm_labels.json に追記/更新する小道具(API 0)。
使い方(Pythonから): from kpg04_label import add; add(["N1a"], "untidi_a2", "hear something out", "ARG_TYPE", "strict", "理由")
ラベルが無い項目は『S軸・N軸とも問題なし(そのまま選べる)』として扱う。実読済みの範囲は judged() で記録(未実読をOK扱いにしない)。"""
import os, json
HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "kpg04_work", "audit", "new_arm_labels.json")


def _load():
    return json.load(open(P, encoding="utf-8")) if os.path.exists(P) else {"labels": [], "judged": []}


def add(arms, case, display_form, code, level, reason):
    d = _load()
    for arm in arms:
        d["labels"] = [x for x in d["labels"] if not (x["arm"] == arm and x["case"] == case and x["display_form"] == display_form)]
        d["labels"].append(dict(arm=arm, case=case, display_form=display_form, code=code, level=level, reason=reason))
    json.dump(d, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def judged(arms, cases):
    d = _load()
    for arm in arms:
        for c in cases:
            if [arm, c] not in d["judged"]:
                d["judged"].append([arm, c])
    json.dump(d, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
