# -*- coding: utf-8 -*-
"""委任_03 P3/P4 記事モード実行ドライバ(DEV専用)。マニフェスト(../casebank/p3_manifest_01.json)の記事に対して
d0(¥0) / d2rank / d1v2(D0ゲート + 因果創作) を実行する。ラベルは読まない(ledger_caseの全台帳はblindファイルから取る)。
使い方: python p3_run_01.py --roles arm_new_ja,arm_new_en --detector d2rank --set p3 --max-yen 80 [--resume] [--dry-run]
         --ids a,b,c で記事を直接指定。"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import flagger_lib as L  # noqa: E402
import ledger_restore_01 as LR  # noqa: E402
import run_flagger_01 as R  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CB = os.path.join(HERE, "..", "casebank")


def load_manifest():
    return json.load(open(os.path.join(CB, "p3_manifest_01.json"), encoding="utf-8"))


def build_unit(m):
    if "ledger_path" in m:
        facts = LR.parse_ledger_file(os.path.join(REPO, m["ledger_path"]))
    else:
        b = json.load(open(os.path.join(CB, "casebank_01_%s_blind.json" % m["ledger_split"]), encoding="utf-8"))
        c = next(x for x in b["cases"] if x["case_id"] == m["ledger_case"])
        assert c.get("ledger_complete"), m
        facts = [dict(fact_id=f["fact_id"], text=f["text"]) for f in c["ledger"]]
    text = open(os.path.join(REPO, m["article_path"]), encoding="utf-8").read()
    sents = R._split_sentences(text)
    ss = [dict(sid="s%d" % (i + 1), text=s, before="", after="") for i, s in enumerate(sents)]
    return dict(unit_id=m["article_id"], mode="article", facts=facts, sentences=ss, ledger_complete=True,
                article_path=m["article_path"])


def select(man, roles, ids):
    if ids:
        return [m for m in man if m["article_id"] in ids]
    return [m for m in man if m["role"] in roles]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--roles", default="")
    ap.add_argument("--ids", default="")
    ap.add_argument("--detector", required=True, choices=["d0", "d2rank", "d1v2"])
    ap.add_argument("--set", dest="set_name", required=True)
    ap.add_argument("--model", default="gpt-6.1-sol", choices=sorted(L.MODELS))
    ap.add_argument("--max-yen", type=float)
    ap.add_argument("--total-cap-yen", type=float, default=900.0)
    ap.add_argument("--effort", default="medium")
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    man = select(load_manifest(), set(x for x in a.roles.split(",") if x), set(x for x in a.ids.split(",") if x))
    units = [build_unit(m) for m in man]
    print("units=%d: %s" % (len(units), ", ".join("%s(%ds,%df)" % (u["unit_id"], len(u["sentences"]), len(u["facts"])) for u in units)))
    gate = "d0" if a.detector == "d1v2" else None
    if a.dry_run:
        return R.dry_run(units, a.detector, a.model, a.max_yen, None, gate)
    if a.detector == "d0":
        return R.run_d0(units, a.set_name)
    if a.max_yen is None:
        print("[REFUSED] --max-yen 必須")
        return 2
    return R.run_llm(units, a.detector, a.model, a.set_name, a.max_yen, a.total_cap_yen, None, a.effort, gate, a.resume)


if __name__ == "__main__":
    sys.exit(main())
