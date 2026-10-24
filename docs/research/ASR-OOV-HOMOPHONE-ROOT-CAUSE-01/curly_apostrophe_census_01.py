# curly_apostrophe_census_01.py -- F1(er011_b1_connected_speech_validator_01.tokenize)が ’ を語構成文字として扱わない件の実データ影響(API 0・読取専用)。
import sys, glob, collections, json
sys.path.insert(0, ".")
import er109_stored_census_01 as C
import er011_b1_connected_speech_validator_01 as csv3
import er006_preprod_hardening_01_validation as val
rows = []
for f in sorted(glob.glob("**/*tts_generation_results*.json", recursive=True)):
    if ".venv" in f: continue
    rows += C.rows_from_results(f)
rows = [r for r in rows if r["asr"]]
curly = [r for r in rows if "’" in r["asr"]]
print("全行", len(rows), "ASR転写に’を含む行", len(curly), f"({100*len(curly)/len(rows):.1f}%)")
ng = [r for r in curly if r["stored_cls"] not in C.PASS_LABELS and r["stored_cls"]]
print("うち保存分類が非PASS", len(ng))
chg = []; seen = set()
for r in ng:
    k = (r["canonical"], r["asr"])
    if k in seen: continue
    seen.add(k)
    a = csv3.classify_connected_speech(r["canonical"], r["asr"])
    b = csv3.classify_connected_speech(r["canonical"], r["asr"].replace("’", "'"))
    if (a.get("new_judgment"), bool(a.get("f1_residual"))) != (b.get("new_judgment"), bool(b.get("f1_residual"))):
        chg.append({"src": r["src"], "seg": r["seg"], "attempt": r["attempt"], "raw": (a.get("new_judgment"), len(a.get("f1_residual") or [])), "norm": (b.get("new_judgment"), len(b.get("f1_residual") or [])), "stored_cls": r["stored_cls"], "final_status": r["final_status"]})
print("ユニーク非PASS(canonical,asr)ペア", len(seen), "’正規化でF1結果が変わるペア", len(chg))
c = collections.Counter((x["raw"][0], x["norm"][0]) for x in chg); print(c)
json.dump({"rows": len(rows), "curly_rows": len(curly), "ng_curly": len(ng), "changed_pairs": chg}, open("docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01/curly_apostrophe_census_01_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
