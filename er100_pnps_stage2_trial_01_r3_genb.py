# -*- coding: utf-8 -*-
"""第3巡 追加phase(Guardrail内、同一設計の拡張): 第1phaseで制御できなかったMeink/Altuzarraの別綴り置換(R2)。
 Meink s02 x {Meank, Meenck}、Altuzarra alt_short x {Ahl-too-ZAH-rah(取得した読み綴りそのまま), Altoozarra} 各2 take = 8音声。1回だけ起動。
 保護対象は個別比較(attempt_historyは他processの追記があり得るため、追記のみ[先頭prefixのsha一致]かを検査して記録、他3ファイルは完全一致をassert)。"""
import hashlib, json, os, re, sys
sys.path.insert(0, os.getcwd())
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import er100_pnps_stage2_trial_01_r3_gen as X
G = X.G
R3 = X.R3
G.GUARD_STOP = 52.0
VARIANTS = [("s02", "meink", "Meank", "meank"), ("s02", "meink", "Meenck", "meenck"), ("alt_short", "altuzarra", "Ahl-too-ZAH-rah", "ahl"), ("alt_short", "altuzarra", "Altoozarra", "altoozarra")]


def main():
    settings = json.load(open(X.R2 / "plan.json", encoding="utf-8"))["tts_settings"]
    items = []
    for sid, w, rep, wtok in VARIANTS:
        canon = X.seg_text(sid)
        ttext = X.replace_word(canon, X.SUPPLY[w]["orig"], rep)
        it = {"id": f"{sid}_{w}_R2_{rep}", "canon": ttext, "tts_text": ttext, "words": [wtok], "word": w, "orig_canon": canon, "supplied": rep, "rep_full": rep,
              "arm": "R2", "wrong": False, "sid": sid, "tier": X.SUPPLY[w]["tier"], "family": "X"}
        for t in ("t1", "t2"):
            items.append((it, dict(settings), t))
    before = G.protect_snapshot()
    json.dump(before, open(R3 / "protect_before_b.json", "w"), indent=1)
    out = []

    def work(x):
        it, st, tag = x
        r = G.process(it, st, tag)
        for k in ("arm", "wrong", "sid", "tier", "supplied", "orig_canon", "rep_full"):
            r[k] = it[k]
        return r
    with ThreadPoolExecutor(max_workers=3) as ex:
        for r in ex.map(work, items):
            out.append(r)
            print(r["id"], r["take"], r.get("sec"), r.get("error", ""), round(G.ledger_total(), 2), flush=True)
            json.dump(out, open(R3 / "gen_b.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    after = G.protect_snapshot()
    json.dump(after, open(R3 / "protect_after_b.json", "w"), indent=1)
    note = {}
    for p in before:
        if before[p] == after[p]:
            note[p] = "unchanged"
        else:
            n0 = before[p]["lines"]
            h = hashlib.sha256()
            with open(p, "rb") as f:
                for i, l in enumerate(f):
                    if i >= n0:
                        break
                    h.update(l)
            note[p] = {"changed": True, "append_only": h.hexdigest() == before[p]["sha256"], "lines_before": n0, "lines_after": after[p]["lines"]}
    json.dump(note, open(R3 / "protect_note_b.json", "w"), indent=1)
    print("PROTECT", json.dumps(note))
    bad = [p for p in note if p != "er011_output/attempt_history.jsonl" and note[p] != "unchanged"]
    assert not bad, bad
    print("DONE ledger total jpy", round(G.ledger_total(), 3))


if __name__ == "__main__":
    main()
