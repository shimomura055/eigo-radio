"""ASR-TIME-NUMERAL-EQUIVALENCE-01 委任_02 TEST_MATRIX_02 実行器(API 0)。
 py test_matrix_02.py [--modules DIR] [--json out.json] : DIR未指定=現在のworking tree、`--modules base_HEAD`=修正前(HEAD)。
 ケース = TEST_MATRIX_01(test_matrix_01.pyの表)+ 委任_02追加(er021_time_numeral_test_01.CASES: Opus追加test全件)。
 期待 EQ=最終判定PASS系 / NE=PASS不可 / REF・PIN=観測のみ(PINは現行値を固定)。judge=Primary 1本(Secondary不可)の最終state。
"""
import sys, os, argparse, json
ap = argparse.ArgumentParser(); ap.add_argument("--modules"); ap.add_argument("--json"); a = ap.parse_args()
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, R)
if a.modules: sys.path.insert(0, os.path.abspath(a.modules))
if a.json: a.json = os.path.abspath(a.json)
os.chdir(R)
import er078_asr_value_guard_01 as vg
import er021_time_numeral_test_01 as T   # CASES + judge_primary(telemetry no-op)
src = open(os.path.join(HERE, "test_matrix_01.py"), encoding="utf-8").read().split("rows = []")[0]
src = src[src.index("PASS = ("):]
ns = {"vg": vg}; exec(src, ns)
cases = [(("M01", c, x, e, "FULL_STORY", n)) for (g, c, x, e, b, n) in ns["C"]] + [(g, c, x, e, role, n) for (g, c, x, e, role, n) in T.CASES]
rows = []; bad = 0
for g, c, x, e, role, n in cases:
    try: k = vg.value_guard(c, x, "en").kind
    except Exception: k = "ERR"
    try: st, rc, cls = T.judge_primary(c, x, role)
    except Exception as ex: st, rc = "ERR", str(ex)[:40]
    final = st in T.PASS_STATES
    if isinstance(e, tuple): exp, ok = "PIN" + ("+" if e[1] else "-"), final == e[1]
    elif e == "REF": exp, ok = "REF", True
    else: exp, ok = e, final == (e == "EQ")
    bad += (not ok)
    rows.append({"g": g, "role": role, "canon": c, "asr": x, "expect": exp, "vg": k, "final": final, "state": st, "reason": rc, "ok": ok, "note": n})
for r in rows:
    print(("OK " if r["ok"] else "BAD"), f"{r['g']:8} {r['role'][:4]} exp={r['expect']:5} judge={r['state']}/{r['reason']} vg={r['vg']:8} | {r['canon']!r} || {r['asr']!r}  {r['note']}")
print("modules:", T.t1.__file__); print("cases", len(rows), "mismatch_vs_expectation", bad)
if a.json: json.dump(rows, open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
