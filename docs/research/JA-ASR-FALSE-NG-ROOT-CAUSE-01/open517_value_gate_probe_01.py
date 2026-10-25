# OPEN-517 是正案(READING_MATCH PASSに値ガード最終確認を適用)の API 0 影響調査。実装ではない(Production無変更)。
# 対象: 現行PrimaryがPHONETIC_MATCH/READING_RESOLVED_MATCHでPASSした保存転写(P-4 421ユニーク)・N-1・N-3(OpenAI転写)。
# 各件に value_guard(canon, asr) と negation_diff を当て、「是正案を入れたらNGに変わる件」を列挙する。
import collections, json, sys
sys.path.insert(0, "."); sys.path.insert(0, "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01")
import eval_common_02 as E
import n1_pairs_01 as N1
import er078_asr_value_guard_01 as vg
from er078_asr_unified_judge_01 import negation_diff
D = "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/"
E.api0_guard_on()
READ = ("PHONETIC_MATCH", "READING_RESOLVED_MATCH")
rows = []
def probe(src, ident, canon, asr):
    b = E.primary_stage(canon, asr, False)
    if not b["primary_pass"] or b["label"] not in READ:
        return
    g = vg.value_guard(canon, asr, "ja"); neg = bool(negation_diff(canon, asr, "ja"))
    rows.append({"src": src, "id": ident, "canon": canon, "asr": asr, "label": b["label"], "value_guard": g.kind, "negation_diff": neg,
                 "would_ng": g.kind in (vg.DIFF, vg.AMBIGUOUS) or neg})
seen = set()
for r in json.load(open(D + "attempt_pool_01.json", encoding="utf8")):
    k = (r["canon"], r["primary"])
    if k in seen: continue
    seen.add(k); probe("P4", r["file"] + ":" + str(r["seg"]), r["canon"], r["primary"])
for p in N1.all_pairs():
    probe("N1", p["id"], p["canon"], p["asr"])
for c in json.load(open(D + "phase3_run/../n3_clips_01.json", encoding="utf8")):
    pass
log = [json.loads(l) for l in open(D + "phase3_run/usage_log.jsonl", encoding="utf8")]
clips = {c["id"]: c for c in json.load(open(D + "n3_clips_01.json", encoding="utf8"))}
for r in log:
    if r["stage"] == "N3_asr":
        probe("N3", r["item"], clips[r["item"]]["canonical"], r["openai_text"])
cnt = collections.Counter((r["src"], r["value_guard"], r["negation_diff"]) for r in rows)
print("READING_MATCH PASS total:", len(rows), "by src:", dict(collections.Counter(r["src"] for r in rows)))
print("value_guard kind x negation_diff:", {str(k): v for k, v in cnt.items()})
print("would become NG under the proposed fix:", sum(r["would_ng"] for r in rows))
for r in rows:
    if r["would_ng"]: print(" ", r["src"], r["id"], r["label"], r["value_guard"], r["negation_diff"], "|", r["canon"][:40], "|", r["asr"][:40])
json.dump(rows, open(D + "open517_value_gate_probe_01.out.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
E.api0_guard_off()
