# -*- coding: utf-8 -*-
"""SC-10(OF-PN2-06): (1)受理に使った実体entryだけから復元した表(表sha不一致・LLM 0 call)で、元の受理が再現されること。
(2)Local Rewrite相当: 1 segment を書き換えた場合に merge_for_local_rewrite で表が減らず、他segmentの判定が変わらないこと(NERは変更segmentのみ)。"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common_01 import *
# LLM呼出禁止(再判定経路でNERを呼んだら即失敗)
def _forbid(*a, **k):
    raise AssertionError("LLM call in re-judgement path")
ret.llm_ner_real = _forbid
tabs = {k: ret.EntityTable.from_dict(v) for k, v in json.load(open(os.path.join(HERE, "entity_tables_hr_01.json"), encoding="utf-8")).items()}
rows = [(i, r) for i, r, c in load_hr_rows() if not c]
res = {"rejudged": 0, "same": 0, "diff": [], "table_sha_mismatch_cases": 0}
for i, r in rows:
    kw = inputs_for(r)
    if kw is None:
        continue
    k, segs, how = group_key_and_segments(r)
    tb = tabs[k]
    for lm, led in (("cur", ledger_tokens(False)), ("excl", ledger_tokens(True))):
        d = run_trial(kw, led, tb)
        if not d.accept or "entity_table" not in d.detail:
            continue
        saved = d.detail["entity_table"]["entries_used"]
        tb2 = ret.table_from_saved_entries(saved)
        d2 = run_trial(kw, led, tb2)
        res["rejudged"] += 1
        if tb2.sha256() != tb.sha256():
            res["table_sha_mismatch_cases"] += 1
        sig = lambda x: (x.accept, x.reason, [(y.canonical, y.asr_primary, y.asr_secondary) for y in x.diffs])
        if sig(d) == sig(d2):
            res["same"] += 1
        else:
            res["diff"].append({"i": i, "lm": lm, "orig_sig": sig(d), "saved_sig": sig(d2)})
# LR: open window group で c14 のsegmentを書き換えて(Bertie行を 'Bertie' → 'Bertie' のまま語を変更)、変更segmentのみNERして和集合
k_ow, segs_ow, _ = group_key_and_segments(next(r for i, r in rows if i == 118))
base = tabs[k_ow]
changed = [ret.Seg(text=s.text.replace("white coat", "grey coat"), role=s.role, segment_id=s.segment_id) for s in segs_ow if "white coat" in s.text]
merged = ret.merge_for_local_rewrite(base, changed, llm=cached_llm(0), usage_log=USAGE_LOG)
res["lr"] = {"changed_segments": len(changed), "base_entries": len(base.entries), "merged_entries": len(merged.entries),
             "not_shrunk": {e.surface for e in base.entries} <= {e.surface for e in merged.entries},
             "bertie_row_decisions_same": []}
for i in (118, 120, 121):
    kw = inputs_for(next(r for j, r in rows if j == i))
    a = run_trial(kw, ledger_tokens(False), base); b = run_trial(kw, ledger_tokens(False), merged)
    res["lr"]["bertie_row_decisions_same"].append((i, a.accept, b.accept))
# NER失敗でも既存entry維持
merged2 = ret.merge_for_local_rewrite(base, changed, llm=lambda t, p: (_ for _ in ()).throw(RuntimeError("x")))
res["lr"]["ner_failure_keeps_entries"] = len(merged2.entries) >= len(base.entries)
res["PASS"] = res["rejudged"] > 0 and not res["diff"] and res["lr"]["not_shrunk"] and all(x[1] == x[2] for x in res["lr"]["bertie_row_decisions_same"]) and res["lr"]["ner_failure_keeps_entries"]
json.dump(res, open(os.path.join(HERE, "sc10_rejudge_lr_01_result.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print(json.dumps(res, ensure_ascii=False, indent=1, default=str))
