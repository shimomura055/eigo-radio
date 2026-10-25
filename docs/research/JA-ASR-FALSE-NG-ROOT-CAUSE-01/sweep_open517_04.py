# OPEN-517 v4 系統的スイープ(補助的な汎化検証。API 0。基準ではなく開示=OPEN517_EVAL_02に結果を記載)。
# 実コーパスの未知データには『かな書き数詞』がほぼ無い(EVAL_02参照)ため、期待読み表×助数詞×値を機械的に総当たりして
#   A: 正しいかな読み(原稿=数字+助数詞 / 転写=かな読み) -> PASSであること(誤NG率)。弱い読み(なのか/ようか/とお)は除外が仕様なので別計上。
#   B: 誤った値のかな読み(同じ助数詞で別の値 m != n) -> PASS以外であること(誤PASS=0が必須)。
#   C: 逆向き(原稿=かな読み / 転写=数字) の A/B。
#   D: 2atom文(原稿 "n1 s1 と n2 s2" / 転写 一方がかな)で、F2が他方の差(値違い)を隠さないこと。
# 判定は純関数 proto_value_gate_fix_04.reading_match_final_gate(READING_MATCH PASSのPrimary最終ゲート)。再現: PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/sweep_open517_04.py
import collections, json, random, sys
sys.path.insert(0, "."); sys.path.insert(0, "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01")
import proto_value_gate_fix_04 as F
import proto_value_gate_fix_03 as F3
import er078_asr_value_guard_01 as vg
import er066_ja_asr_orthographic_equivalence_01_trial as tr

UNITS = ["day", "day_span", "person", "hour", "hour_span", "minute", "second", "month", "month_span", "year", "year_span", "age", "kai", "ken", "ko",
         "week", "yen", "floor", "gen", "mai", "dai", "bai", "do", "km", "hon", "haku", "ban", "go", "tsu"]
NS = list(range(1, 31)) + [40, 50, 60, 70, 80, 90, 100, 200, 300, 400, 600, 800, 1000, 3000, 8000, 10000]
WEAK = set(vg.WEAK_KANA_NUMERALS)
st = collections.Counter()
examples = collections.defaultdict(list)


def reads(n, u):
    return [r for r in tr._cands(n, u) if r]


def rec(kind, c, a, res, v3=None):
    st[(kind, res)] += 1
    if len(examples[(kind, res)]) < 6:
        examples[(kind, res)].append((c, a, v3))


random.seed(0)
for u in UNITS:
    surf = vg.COUNTERS[u][0]
    for n in NS:
        if u == "tsu" and n > 10:
            continue
        for r in reads(n, u):
            weak = r in WEAK
            # A: 原稿 数字 / 転写 かな(正しい読み)
            c, a = f"それは{n}{surf}です", f"それは{r}です"
            res = F.reading_match_final_gate(c, a).state
            rec("A_weak" if weak else "A", c, a, res, F3.reading_match_final_gate(c, a).state)
            # C: 原稿 かな / 転写 数字
            c, a = f"それは{r}です", f"それは{n}{surf}です"
            res = F.reading_match_final_gate(c, a).state
            rec("C_weak" if weak else "C", c, a, res, F3.reading_match_final_gate(c, a).state)
            # B: 誤った値のかな読み
            for m in {max(1, n - 1), n + 1, n * 2, n + 10}:
                if m == n or (u == "tsu" and m > 10):
                    continue
                c, a = f"それは{m}{surf}です", f"それは{r}です"
                res = F.reading_match_final_gate(c, a).state
                rec("B", c, a, res, F3.reading_match_final_gate(c, a).state)
                c2, a2 = f"それは{r}です", f"それは{m}{surf}です"
                res = F.reading_match_final_gate(c2, a2).state
                rec("B_rev", c2, a2, res, F3.reading_match_final_gate(c2, a2).state)
            # D: 2atom文。n1(かな化) と n2(数字)。n2を別の値に変えた転写は必ずNG
            m = n + 3
            if not (u == "tsu" and m > 10):
                c = f"{n}{surf}と{m}{surf}です"
                a_ok = f"{r}と{m}{surf}です"
                a_ng = f"{r}と{m + 1}{surf}です"
                rec("D_ok", c, a_ok, F.reading_match_final_gate(c, a_ok).state, F3.reading_match_final_gate(c, a_ok).state)
                rec("D_ng", c, a_ng, F.reading_match_final_gate(c, a_ng).state, F3.reading_match_final_gate(c, a_ng).state)
print("kind/result counts (v4):")
for k in sorted(st): print("  ", k, st[k])
bad_pass = sum(v for (k, r), v in st.items() if k in ("B", "B_rev", "D_ng") and r == "PASS")
print("誤PASS(B/B_rev/D_ng で PASS)件数 v4:", bad_pass)
for k in ("B", "B_rev", "D_ng"):
    for ex in examples.get((k, "PASS"), []): print("   FALSE_PASS", k, ex)
fn = sum(v for (k, r), v in st.items() if k in ("A", "C", "D_ok") and r != "PASS")
print("誤NG(A/C/D_ok で PASS以外、弱い読みは除く)件数 v4:", fn)
for k in ("A", "C", "D_ok"):
    for r in ("NG_PROTECTED", "DEMOTE_P3"):
        for ex in examples.get((k, r), []): print("   FALSE_NG", k, r, ex)
print("(参考)A_weak/C_weak(弱い読み=仕様で置換対象外): ", {k: v for k, v in st.items() if k[0] in ("A_weak", "C_weak")})
print("== v3との比較 ==")
v3bad = 0
# examplesはv3列を持つが件数は別に数える
cnt3 = collections.Counter()
random.seed(0)
for u in UNITS:
    surf = vg.COUNTERS[u][0]
    for n in NS:
        if u == "tsu" and n > 10:
            continue
        for r in reads(n, u):
            for m in {max(1, n - 1), n + 1, n * 2, n + 10}:
                if m == n or (u == "tsu" and m > 10):
                    continue
                if F3.reading_match_final_gate(f"それは{m}{surf}です", f"それは{r}です").state == "PASS": cnt3["B_false_pass"] += 1
                if F3.reading_match_final_gate(f"それは{r}です", f"それは{m}{surf}です").state == "PASS": cnt3["B_rev_false_pass"] += 1
            m = n + 3
            if not (u == "tsu" and m > 10):
                c = f"{n}{surf}と{m}{surf}です"
                if F3.reading_match_final_gate(c, f"{r}と{m + 1}{surf}です").state == "PASS": cnt3["D_ng_false_pass"] += 1
print("v3 誤PASS:", dict(cnt3))
