# -*- coding: utf-8 -*-
"""OPEN-436の枠で一般語entry `mini`(cascade_unresolved_entity)を隔離(ledger_disabled)し、前後のPhrase List差分・M1候補集合差分を記録する(API 0)。
使い方: .venv/Scripts/python.exe <this> [--apply]   (--applyなし=dry-run: 前の計測のみ)"""
import json, os, shutil, sys, time
sys.path.insert(0, os.getcwd())
import er006_pronunciation_ledger_01 as pl
import er006_m1_multi_candidate_01 as m1

APPLY = "--apply" in sys.argv
LP = pl.LEDGER_PATH
HRQ = "er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl"
AH = "er011_output/attempt_history.jsonl"
rows = [json.loads(l) for l in open(HRQ, encoding="utf8") if l.strip()]
before_ledger = json.load(open(LP, encoding="utf8"))
texts = {r["canonical_text"] for r in rows if isinstance(r.get("canonical_text"), str)}
for l in open(AH, encoding="utf8"):
    if l.strip():
        try:
            d = json.loads(l)
        except Exception:
            continue
        if isinstance(d.get("canonical_text"), str):
            texts.add(d["canonical_text"])
texts |= {e["surface"] for e in before_ledger.values()}
texts = sorted(texts)

def snap():
    led = json.load(open(LP, encoding="utf8"))
    ph = {t: sorted(h["canonical_spelling"] for h in pl.get_hint_for_text(t, min_confidence="low")) for t in texts}
    hs = {t: m1.freeze_candidates(t, ledger_snapshot=led, segment_started_at=None).candidate_set_hash for t in texts}
    return ph, hs

ph0, hs0 = snap()
mini = [k for k, e in before_ledger.items() if e["surface"].strip().lower() == "mini"]
assert len(mini) == 1, mini
print("texts", len(texts), "mini ledger_id", mini[0], "already_disabled", before_ledger[mini[0]].get("ledger_disabled"))
if not APPLY:
    sys.exit(0)
bk = "er006_output/pronunciation_ledger_01/backup/ledger_before_PNPS1_mini_20261022.json"
assert not os.path.exists(bk)
shutil.copyfile(LP, bk)
reason = ("PNPS Stage1 E-2(OPEN-436の枠): 一般英単語'mini'を調査用typeで登録した誤entry(OPEN-436 validatorに掛からず有効のままASR Phrase Listへ供給されていた)。"
          "削除せずledger_disabledで隔離(Phrase List/M1 C2/TTS/再researchの全用途から除外、履歴保持)。backup=" + bk)
pl.set_ledger_disabled(mini[0], reason)
after_ledger = json.load(open(LP, encoding="utf8"))
changed = [k for k in before_ledger if before_ledger[k] != after_ledger[k]]
ph1, hs1 = snap()
dph = [(t, sorted(set(ph0[t]) - set(ph1[t])), sorted(set(ph1[t]) - set(ph0[t]))) for t in texts if ph0[t] != ph1[t]]
dhs = [t for t in texts if hs0[t] != hs1[t]]
res = {"texts": len(texts), "mini_ledger_id": mini[0], "changed_entries": changed, "changed_fields": sorted(k for k in after_ledger[mini[0]] if before_ledger[mini[0]].get(k) != after_ledger[mini[0]][k]),
       "entries_before": len(before_ledger), "entries_after": len(after_ledger), "phrase_list_differing_texts": len(dph),
       "phrase_list_removed_only_mini": all(r == ["mini"] and not a for _, r, a in dph), "phrase_list_examples": [(t[:70], r, a) for t, r, a in dph[:4]],
       "m1_candidate_set_hash_differing": len(dhs), "backup": bk, "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
print(json.dumps(res, ensure_ascii=False, indent=1))
json.dump(res, open("docs/research/PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02/mini_isolation_01_result.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
