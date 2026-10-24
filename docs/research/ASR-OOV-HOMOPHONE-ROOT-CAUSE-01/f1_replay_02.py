# f1_replay_02.py -- F1 tokenize ’修正の影響分析(API 0・読取専用)。保存全行をProduction関数で再判定し、結果をJSON保存。fix前後で比較する。
import sys, glob, json
sys.path.insert(0, ".")
import er109_stored_census_01 as C
import er011_b1_connected_speech_validator_01 as csv3
import er011_connected_speech_equivalence_layer_production_01 as eq
import er006_preprod_hardening_01_validation as val
out = sys.argv[1]
if len(sys.argv) > 2 and sys.argv[2] == "old":  # 修正前の tokenize を再現(比較用。Production fileは無変更)
    import re; csv3.tokenize = lambda text: re.findall(r"[A-Za-z']+", text)
rows = []
for f in sorted(glob.glob("**/*tts_generation_results*.json", recursive=True)):
    if ".venv" in f: continue
    rows += C.rows_from_results(f)
rows = [r for r in rows if r["asr"]]
res = {}
for r in rows:
    k = r["canonical"] + "\x00" + r["asr"]
    if k in res: continue
    a = csv3.classify_connected_speech(r["canonical"], r["asr"])
    b = eq.classify_connected_speech_equivalence(r["canonical"], r["asr"])
    c = val.classify_asr_match(r["canonical"], r["asr"])
    res[k] = [a.get("new_judgment"), len(a.get("f1_residual") or []), b.get("layer_judgment"), c.classification, bool(c.should_pass)]
json.dump({"rows": len(rows), "unique": len(res), "res": res}, open(out, "w", encoding="utf-8"), ensure_ascii=False)
print("rows", len(rows), "unique", len(res))
