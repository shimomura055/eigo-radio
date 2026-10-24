"""OPEN-487 TEST_MATRIX(API 0): `py test_matrix_487_01.py [--modules DIR] [--json out]`。判定=Primary 1本(Secondary不可)の最終state(judge_sim_01.judge_primary)。
EQ=PASS系 / NE=PASS不可 / REF=観測のみ。"""
import sys, os, argparse, json
ap = argparse.ArgumentParser(); ap.add_argument("--modules"); ap.add_argument("--json"); a = ap.parse_args()
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, R)
if a.modules: sys.path.insert(0, os.path.abspath(a.modules))
if a.json: a.json = os.path.abspath(a.json)
sys.path.append(HERE); os.chdir(R)
import judge_sim_01 as js
import er078_asr_value_guard_01 as vg
C = [
 # --- 誤PASSの是正(NE) ---
 ("T487", "one hundred thirty people", "1:30 people", "NE", "報告原例"),
 ("T487", "1:30 people", "one hundred thirty people", "NE", "逆向き"),
 ("T487", "one hundred and thirty people", "1:30 people", "NE", ""),
 ("T487", "130 people", "1:30 people", "NE", "digits<->time+名詞"),
 ("T487", "It was one hundred thirty.", "It was 1:30.", "NE", "文末"),
 ("T487", "one hundred twenty", "1:20", "NE", ""),
 ("T487", "two hundred fifteen people", "2:15 people", "NE", ""),
 ("T487", "I saw 130 people", "I saw 1:30 people", "NE", ""),
 ("T487", "one hundred thirty people", "1 30 people", "NE", "ASRが空白区切り数字"),
 ("T487", "10 30", "1030", "NE", "桁連結と空白区切りは別物"),
 ("T487", "at 10 30", "at 1030", "NE", ""),
 ("EQ", "nine fifty people", "9 50 people", "EQ", "OPEN-482時刻形統一で同一視(意図どおり)"),
 ("T487", "twenty twenty-six", "20 26", "NE", "年と空白区切り"),
 ("T487", "3 10-minute rounds", "310 minute rounds", "NE", ""),
 # --- 維持すべき正常系(EQ) ---
 ("EQ", "one hundred thirty people", "130 people", "EQ", ""),
 ("EQ", "130 people", "one hundred thirty people", "EQ", ""),
 ("EQ", "At ten thirty", "At 10:30", "EQ", "OPEN-482"),
 ("EQ", "At 10:30", "At ten thirty", "EQ", ""),
 ("EQ", "At 10 thirty", "At 10:30", "EQ", ""),
 ("EQ", "At ten thirty", "At 10 30", "EQ", ""),
 ("EQ", "At 1:30", "At one thirty", "EQ", ""),
 ("EQ", "At one thirty", "At 1:30", "EQ", ""),
 ("EQ", "At two fifteen", "At 2:15", "EQ", ""),
 ("EQ", "At nineteen thirty", "At 19:30", "EQ", "24時間表記(現行PASS)"),
 ("EQ", "At 19:30", "At nineteen thirty", "EQ", ""),
 ("EQ", "at fourteen fifteen", "at 14:15", "EQ", ""),
 ("EQ", "In nineteen ninety nine", "In 1999", "EQ", "年号"),
 ("EQ", "In 1999", "In nineteen ninety nine", "EQ", ""),
 ("EQ", "In twenty twenty six", "In 2026", "EQ", ""),
 ("EQ", "In twenty twenty", "In 2020", "EQ", ""),
 ("EQ", "between 9 and 11", "between nine and eleven", "EQ", "OPEN-489"),
 ("EQ", "one hundred and ten", "110", "EQ", ""),
 ("EQ", "two thousand and five", "2005", "EQ", ""),
 ("EQ", "ten thirty five", "10:35", "EQ", ""),
 ("EQ", "ten thirty-five", "1035", "REF", "ASR桁連結(現行の扱いを観測)"),
 ("EQ", "storymaking", "story making", "EQ", "複合語分かち書き"),
 ("EQ", "blitzscaling", "blitz-scaling", "EQ", ""),
 ("EQ", "covid 19", "covid19", "EQ", "文字+数字境界"),
 ("EQ", "e mail", "email", "EQ", ""),
 ("EQ", "a wide-scale empirical study", "Widescale empirical study.", "EQ", "冠詞除外despace"),
 ("EQ", "Wi-Fi 6", "wifi 6", "EQ", ""),
 ("EQ", "3,000 people", "3000 people", "EQ", "桁区切り"),
 ("EQ", "1,000,000 dollars", "1000000 dollars", "REF", "既存別事象OPEN-492候補"),
 ("EQ", "3.5 percent", "three point five percent", "EQ", ""),
 ("EQ", "Room 12", "Room twelve", "EQ", ""),
 ("EQ", "20 percent", "twenty percent", "EQ", ""),
 ("EQ", "The 2020s", "The twenty twenties", "REF", ""),
 # --- 境界(REF=現行値を観測してA案の影響を開示) ---
 ("REF", "At 1:30", "At 130", "REF", "ASRが桁連結で書く: 現行は偶然PASS"),
 ("REF", "At 130", "At 1:30", "REF", ""),
 ("REF", "At 1030", "At 10:30", "REF", "er109承認同値(X/Z)"),
 ("REF", "At 10:30", "At 1030", "REF", ""),
 ("REF", "Room 1030", "Room 10:30", "REF", ""),
 ("REF", "At 3:45", "At 345", "REF", ""),
 ("REF", "3 4 5", "345", "REF", ""),
 ("REF", "tel 555 1234", "tel 5551234", "REF", "電話番号の分かち書き"),
 ("REF", "1 000", "1000", "REF", "桁区切りスペース"),
]
rows = []; bad = 0
for g, c, x, e, n in C:
    try: k = vg.value_guard(c, x, "en").kind
    except Exception: k = "ERR"
    try: st, rc, cls = js.judge_primary(c, x, "FULL_STORY")
    except Exception as ex: st, rc, cls = "ERR", str(ex)[:40], ""
    final = st in js.PASS_STATES
    ok = True if e == "REF" else (final == (e == "EQ"))
    bad += (not ok)
    rows.append({"g": g, "canon": c, "asr": x, "expect": e, "vg": k, "final": final, "state": st, "reason": rc, "cls": cls, "ok": ok, "note": n})
    print(("OK " if ok else "BAD"), f"{g:5} exp={e:3} {'PASS' if final else 'NG  '} {st}/{rc[:34]} vg={k:8} cls={cls} | {c!r} || {x!r} {n}")
print("cases", len(rows), "mismatch", bad)
if a.json: json.dump(rows, open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
