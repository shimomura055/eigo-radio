# -*- coding: utf-8 -*-
"""CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 委任_02: Y runtime evidence用のdev入力を作る(API 0)。
実在Y run(er121_output/family_y_production_01/redelivery_fee/run_01)を新slug/runへcopyし(pages・hr_listening・logs・snapshotは除外)、
a2/b1b の parts.json の y_voice_2 だけに『文の境界で空行(段落区切り)を挿入』する。本文の文字列は空白差以外同一(検証して書く)。
実記事・公開dir・run_01は一切変更しない。
使い方: py make_y_multipara_dev_input_01.py --src <run_01> --dst <RUN_ROOT/slug/run> --segment y_voice_2 --paragraphs 3 --out <json>
"""
import argparse
import json
import os
import re
import shutil

ap = argparse.ArgumentParser()
ap.add_argument("--src", required=True)
ap.add_argument("--dst", required=True)
ap.add_argument("--segment", default="y_voice_2")
ap.add_argument("--paragraphs", type=int, default=3)
ap.add_argument("--out", required=True)
a = ap.parse_args()

EXCLUDE_DIRS = {"pages", "hr_listening", "_ypl6_pre_snapshot"}
EXCLUDE_FILES_RE = re.compile(r"(^console_.*\.log$|^adopt_apply_.*\.log$|^stop_check_.*\.json$|^launch\d+_epoch\.txt$|^run_launch_log\.jsonl$)")


def ignore(d, names):
    skip = []
    for n in names:
        p = os.path.join(d, n)
        if os.path.isdir(p) and n in EXCLUDE_DIRS and os.path.abspath(d) == os.path.abspath(a.src):
            skip.append(n)
        elif os.path.isfile(p) and EXCLUDE_FILES_RE.search(n) and os.path.abspath(d) == os.path.abspath(a.src):
            skip.append(n)
    return skip


assert not os.path.exists(a.dst), "dstが既に存在します(上書きしない)"
shutil.copytree(a.src, a.dst, ignore=ignore)


def split_sentences(t):
    # 文境界 = 終止符/疑問符/感嘆符 + 空白 + 次の大文字/引用開始(Yの本文は英語散文)
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z“\"'])", t.strip())
    return [p for p in parts if p]


def make_paragraphs(t, n):
    sents = split_sentences(t)
    assert len(sents) >= n, (len(sents), n)
    words = [len(s.split()) for s in sents]
    total = sum(words)
    target = total / n
    groups, cur, acc = [], [], 0
    for s, w in zip(sents, words):
        cur.append(s)
        acc += w
        if len(groups) < n - 1 and acc >= target * (len(groups) + 1) - 1e-9 and len(sents) - (sum(len(g) for g in groups) + len(cur)) >= (n - 1 - len(groups)):
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)
    return "\n\n".join(" ".join(g) for g in groups), [sum(len(s.split()) for s in g) for g in groups]


report = {"src": a.src, "dst": a.dst, "segment": a.segment, "levels": {}}
for lv in ("a2", "b1b"):
    pj = os.path.join(a.dst, lv, "parts.json")
    doc = json.load(open(pj, encoding="utf-8"))
    old = doc["segments"][a.segment]
    new, wc = make_paragraphs(old, a.paragraphs)
    assert " ".join(old.split()) == " ".join(new.split()), "本文文字列が空白差以外で異なる"
    doc["segments"][a.segment] = new
    json.dump(doc, open(pj, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    report["levels"][lv] = {"paragraph_words": wc, "words_total": sum(wc), "text_identical_modulo_whitespace": True,
                            "inserted_blank_lines": new.count("\n\n"), "new_text": new}
json.dump(report, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "new_text"} for k, v in report["levels"].items()}, ensure_ascii=False))
