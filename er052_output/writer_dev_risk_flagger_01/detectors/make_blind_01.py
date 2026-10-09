# -*- coding: utf-8 -*-
"""ラベル分離ステップ(委任_01B -> 委任_02 P0で強化)。casebank_01.json から
  (a) split別の盲検ファイル casebank_01_<split>_blind.json  (split = dev / holdout / synthetic_dev / synthetic_holdout)
  (b) 集計専用ラベルファイル casebank_01_labels.json (case_id/syn_id -> ラベル群)
を生成する。検出器(run_flagger_01.py)は *_blind.json だけを読み、*_labels.json は aggregate_flagger_01.py だけが読む。

盲検ケースの中身(これだけ): case_id, lang, fact{id,text}, sentence, context{before,after}, ledger[{fact_id,text}], ledger_complete
 - fact.src / context.source / ラベル・出典・notes・split・事故タイプ等は全て落とす(flagger_lib.LABEL_KEYS)。
 - ledger = fact.srcから復元した『当該記事の全台帳』(ledger_restore_01.py)。判定対象は sentence のみ。
合成参考(synthetic_reference)は case_id=syn_id の擬似ケースにして、実ケースのどこかで解決済みの台帳(同一fact_id)を全台帳として付ける。
合成の方向反転系(S-01/S-04〜S-07/S-10)の事故タイプを『方向反転(別Fact)』へ訂正(Opus所見4)。ラベル側のみ。
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import flagger_lib as L  # noqa: E402
import ledger_restore_01 as LR  # noqa: E402

LABEL_KEYS = L.LABEL_KEYS

# 事故系統(KPI4)。legacy_idsに含まれるものを known_incident として付与(ラベル側のみ)。
KNOWN_INCIDENT_BY_LEGACY = {
    "WE-K01": "Rollback方向反転", "WE-K03": "Rollback方向反転", "S-12": "Rollback方向反転", "S-13": "Rollback方向反転",
    "meta-p2r2-02": "開示対象の取り違え", "sw-p2r2-02": "『初めて』の範囲拡張", "hormuz-T0M0r2-01": "20%の対象入替",
    "RC-K16": "時期の創作", "Safety-B3": "因果・仕組みの創作", "Safety-B4-a": "因果・仕組みの創作", "RC-K20": "因果・仕組みの創作",
}
# 『重大と同一Factの忠実文』(hard-negative)。K12/K08/K09/RC-K10/S0系(Opus所見10)。
HARD_NEG_LEGACY = {"WE-K12", "WE-K08", "WE-K09", "RC-K10", "S0-1", "S0-2", "S0-3"}
# 合成の方向反転系: 台帳と別Factの方向を入れ替えた文(accident_typeを訂正)
SYN_DIRECTION_REVERSAL = {"S-01", "S-04", "S-05", "S-06", "S-07", "S-10"}
SYN_TYPE_FIX = "方向反転(別Fact)"


def neg_group(case):
    ids = set(case.get("legacy_ids") or [])
    if ids & HARD_NEG_LEGACY:
        return "hard_negative"
    t = str(case.get("accident_type") or "")
    if "境界" in t or "軽微" in t:
        return "boundary"
    return "clear"


def _blind_case(c, restored):
    fact = c.get("fact") or {}
    ctx = c.get("context") or {}
    r = restored[c["case_id"]]
    return dict(case_id=c["case_id"], lang=c.get("lang", ""),
                fact=dict(id=fact.get("id"), text=fact.get("text")),
                sentence=c["sentence"], context=dict(before=ctx.get("before", ""), after=ctx.get("after", "")),
                ledger=r["ledger"], ledger_complete=r["ledger_complete"])


def split_casebank(data):
    """data: casebank_01.json全体 -> (blind_by_split, labels, report)。"""
    cases = data["cases"]
    syns = data.get("synthetic_reference", [])
    pseudo = []
    for s in syns:
        pseudo.append(dict(case_id=s["syn_id"], lang="EN", fact=dict(id=s["fact_id"], text=s["ledger_text"], src=None),
                           sentence=s["sentence"], context=dict(before="", after=""), split="synthetic_" + s["split"]))
    restored = LR.restore_for_cases(cases + pseudo)
    blind, labels, report = {}, {}, {}
    for c in cases:
        blind.setdefault(c["split"], []).append(_blind_case(c, restored))
        lab = {k: v for k, v in c.items() if k in LABEL_KEYS}
        lab["split"] = c["split"]
        lab["neg_group"] = neg_group(c) if c["label"] != "重大" else None
        lab["hard_negative"] = lab["neg_group"] == "hard_negative"
        lab["known_incident"] = next((KNOWN_INCIDENT_BY_LEGACY[i] for i in (c.get("legacy_ids") or [])
                                      if i in KNOWN_INCIDENT_BY_LEGACY), None)
        labels[c["case_id"]] = lab
        report[c["case_id"]] = restored[c["case_id"]]["origin"]
    for s, p in zip(syns, pseudo):
        sp = p["split"]
        blind.setdefault(sp, []).append(_blind_case(p, restored))
        typ = SYN_TYPE_FIX if s["syn_id"] in SYN_DIRECTION_REVERSAL else s["accident_type"]
        labels[s["syn_id"]] = dict(label="重大", label_basis=s.get("label_basis", ""), accident_type=typ,
                                   accident_type_original=s["accident_type"], split=sp, synthetic=True,
                                   neg_group=None, hard_negative=False, legacy_ids=[s["syn_id"]],
                                   known_incident=KNOWN_INCIDENT_BY_LEGACY.get(s["syn_id"]))
        report[s["syn_id"]] = restored[s["syn_id"]]["origin"]
    return blind, labels, report


def main(argv=None):
    argv = argv or sys.argv[1:]
    if not argv:
        print("usage: make_blind_01.py casebank_01.json [out_dir]")
        return 2
    src = argv[0]
    out_dir = argv[1] if len(argv) > 1 else os.path.dirname(os.path.abspath(src))
    with open(src, encoding="utf-8") as f:
        data = json.load(f)
    blind, labels, report = split_casebank(data)
    stem = os.path.splitext(os.path.basename(src))[0]
    for sp, cs in sorted(blind.items()):
        bp = os.path.join(out_dir, "%s_%s_blind.json" % (stem, sp))
        with open(bp, "w", encoding="utf-8") as f:
            json.dump({"cases": cs}, f, ensure_ascii=False, indent=1)
        print("blind[%s]=%s (%d cases)" % (sp, bp, len(cs)))
    lp = os.path.join(out_dir, stem + "_labels.json")
    with open(lp, "w", encoding="utf-8") as f:
        json.dump(labels, f, ensure_ascii=False, indent=1)
    rp = os.path.join(out_dir, stem + "_ledger_origin.json")
    with open(rp, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)
    print("labels=%s (%d) ledger_origin=%s" % (lp, len(labels), rp))
    return 0


if __name__ == "__main__":
    sys.exit(main())
