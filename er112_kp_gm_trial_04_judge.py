# -*- coding: utf-8 -*-
"""FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_14: 課題① Sonnet参考Judge(最終判定はFable盲検。参考値のみ)。Trial_03のJUDGE_INSTR(3値 P/T/F)を再利用し、費用台帳は本Trialのものに記録する。
出力: er112_output/kp_gm_trial_04/judge/sonnet_labels.json  形式 {"<row#>:<col>": "PASS|THIN|FAIL"} (盲検表fable_blind_04.mdと同じ行・列ID。字義訳の区別はこのJudgeでは行わない)
"""
from __future__ import annotations

import hashlib, json, os, re, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed

os.environ.setdefault("KP04_INSPECT_VERSION", "v2")
os.environ.setdefault("KP04_INSPECT_EFFORT", "low")
import er112_kp_gm_trial_04 as X                      # noqa: E402
import er112_kp_gm_trial_03 as T3                     # noqa: E402
import er098_kp_six_model_trial_01_common as CM       # noqa: E402

OUT = X.OUT
sys.stdout.reconfigure(encoding="utf-8")
JMODEL = T3.JMODEL
LAB = {"P": "PASS", "T": "THIN", "F": "FAIL"}


def main(cap):
    keymap = json.load(open(OUT / "fable_blind_04_key.json", encoding="utf-8"))
    A = X.all_kps()
    gold = T3.gold_final()
    rows = []
    for rk, v in keymap.items():
        kp = A[v["key"]]
        for col, c in v["cols"].items():
            row = dict(kind="G", key_phrase=kp["key"], source_sentence=kp["sent"], gloss=c["gloss"])
            if v["key"] in gold and kp["tier"] == "hard":
                g = gold[v["key"]]
                row["gold_reference"] = "用法=%s / 許容される意味=%s / 不可=%s" % (g["usage"], g["ok_ja"], g["ng_ja"])
            row["id"] = "%s:%s" % (rk, col)
            rows.append(row)
    done = {}
    p = OUT / "judge" / "sonnet_labels.json"
    if p.exists():
        done = json.load(open(p, encoding="utf-8"))
    todo = [r for r in rows if r["id"] not in done]
    batches = [todo[i:i + T3.JBATCH] for i in range(0, len(todo), T3.JBATCH)]
    print("judge rows", len(rows), "todo", len(todo), "batches", len(batches), flush=True)

    def w(b):
        if X.stop() or X.total() >= cap:
            return ("SKIP", len(b))
        body = T3.JUDGE_INSTR + "\n".join("%d. %s" % (i, json.dumps({k: v for k, v in r.items() if k != "id"}, ensure_ascii=False)) for i, r in enumerate(b, 1))
        bd = CM.build_body("anthropic", JMODEL, body)
        r = CM.call_with_retry("anthropic", JMODEL, bd)
        if not r["ok"]:
            return ("ERR", str(r["attempts"])[:200])
        cost = CM.cost_usd(JMODEL, r["usage"]) * CM.USD_JPY
        X.ledger_add(dict(kind="judge", judge=JMODEL, n=len(b), usage=r["usage"], cost_jpy=round(cost, 5), ts=time.strftime("%Y-%m-%dT%H:%M:%S")))
        got = {}
        for ln in r["text"].splitlines():
            m = T3._L3.match(ln)
            if m and 1 <= int(m.group(1)) <= len(b):
                got[b[int(m.group(1)) - 1]["id"]] = LAB[m.group(2)]
        return ("OK", got, round(cost, 4))
    with ThreadPoolExecutor(3) as ex:
        for f in as_completed([ex.submit(w, b) for b in batches]):
            r = f.result()
            if r[0] == "OK":
                done.update(r[1])
                print("OK", len(r[1]), r[2], "cum=%.3f" % X.total(), flush=True)
            else:
                print(r, flush=True)
    (OUT / "judge").mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(done, ensure_ascii=False, indent=1), encoding="utf-8")
    print("labels", len(done), "of", len(rows))


if __name__ == "__main__":
    main(float(sys.argv[1]) if len(sys.argv) > 1 else X.CAP_JPY)
