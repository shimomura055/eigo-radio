"""PNMH-PLAN-01: ASR-THREE-WAY-COMPARISON-TRIAL-01 の保存転写(asr_raw.jsonl、読み取り専用)に現行/提案判定を再適用(API 0)。
そのTrialの設定・出力は変更しない(読むだけ。書込みは本dirのみ)。**ラベル付き(normal/problem)データ**で新規誤PASSの有無を見る。"""
import sys, os, json, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
import proto_multiword_span_01 as P
val = P.val
import er006_secondary_asr_01 as sec
T = os.path.join(ROOT, "er091_output", "asr_three_way_trial_01")
man = {}
for l in open(os.path.join(T, "dataset_manifest.jsonl"), encoding="utf8"):
    o = json.loads(l); man[o["id"]] = o
rows = []
for l in open(os.path.join(T, "results", "asr_raw.jsonl"), encoding="utf8"):
    o = json.loads(l)
    if o.get("text") and o["id"] in man:
        rows.append((o["id"], o["method"], o.get("cond"), o["text"]))
def judge(c, a):
    r = val.classify_asr_match(c, a)
    if r.should_pass: return True
    if (sec.is_entity_like_mismatch(r) or sec.is_homophone_candidate_mismatch(r)) and sec._step_alternate_pass(r): return True
    return False
before = [judge(man[i]["canonical"], t) for i, m, c, t in rows]
P.install_proto()
after = [judge(man[i]["canonical"], t) for i, m, c, t in rows]
chg = [(rows[k], man[rows[k][0]]) for k in range(len(rows)) if before[k] != after[k]]
by = collections.Counter((man[i]["label_class"], m) for i, m, c, t in rows)
out = {"n_transcripts": len(rows), "n_audio": len({r[0] for r in rows}), "by_label_method": {f"{k[0]}|{k[1]}": v for k, v in by.items()},
       "n_changed": len(chg), "changed": [dict(id=r[0], method=r[1], cond=r[2], text=r[3], canonical=m["canonical"], label_class=m["label_class"]) for r, m in chg],
       "problem_new_pass": sum(1 for r, m in chg if m["label_class"] == "problem" and not before[rows.index(r)] and after[rows.index(r)])}
json.dump(out, open(os.path.join(HERE, "replay_asr3way_cache_result_01.json"), "w", encoding="utf8", newline="\n"), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "changed"}, ensure_ascii=False, indent=1)); print(out["changed"])
