# OPEN-517 F1+F2 / OPEN-523 / OPEN-524 の Production適用後 API 0再評価(JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_07A)。保存済み転写のみ・LLM/ASR/TTS呼出0(socket guard)。
# 目的: Production関数(er078_asr_unified_judge_01 / er078_asr_value_guard_01 / adapter)の判定が、proto v4(DEV正本。事前登録=OPEN517_PREREGISTERED_02.md)と
#       『完全一致(差分0)』することの証明。OPEN-523/524(合格範囲を狭める同時適用)の影響は『定数OFFでv4と完全一致』『ONで差分は列挙』の2段で示す。
# 入力: (A) 既存771+未知493=1264件(open517_api0_eval_04.out.json の v4 結果[fix_state/fix_reason/fix_warn/fix_label]を基準値として照合。再現可能=同out.jsonはv4 proto実行の保存値)
#       (B) 合成: sweep_open517_04.py の系統スイープ全件 + 基準7合成負例24件 + 受入固定例 を、proto v4純関数(reading_match_final_gate。523/524定数OFFのProduction value_guardを基底)と
#           Production(unified_judge、READING_MATCH PASS)の最終ゲート判定で突合。
# 実行: リポジトリrootで PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/eval_open517_api0_prod_01.py   出力: open517_api0_prod_01.out.json
import collections, contextlib, hashlib, json, sys
sys.path.insert(0, "."); sys.path.insert(0, "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01")
import eval_common_02 as E
import proto_value_gate_fix_04 as F4
import er078_asr_unified_judge_01 as uj
import er078_asr_value_guard_01 as vg
import er066_ja_asr_orthographic_equivalence_01_trial as tr

D = "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/"
READ = ("PHONETIC_MATCH", "READING_RESOLVED_MATCH")
PASSING = uj.PASSING_STATES
v4 = json.load(open(D + "open517_api0_eval_04.out.json", encoding="utf8"))["rows"]
KNOWN_NEG = {"N1-er066a-028", "N1-er066b-020", "N1-er066b-022", "N1-prodbug-006", "N1-prodbug-007", "N1-new-042", "N1-new-044", "N1-new-057", "N3-02"}


def _rs(x): return "primary_pass" if str(x).startswith("primary_pass") else x


@contextlib.contextmanager
def guards(on524, on523):
    o5, o3 = vg.KANA_WORD_BOUNDARY_CHECK, vg.WEAK_KANA_REGION_COMPAT
    vg.KANA_WORD_BOUNDARY_CHECK, vg.WEAK_KANA_REGION_COMPAT = on524, on523
    try:
        yield
    finally:
        vg.KANA_WORD_BOUNDARY_CHECK, vg.WEAK_KANA_REGION_COMPAT = o5, o3


# ---------------- (A) 既存771+未知493 ----------------
E.api0_guard_on()
rowsA = []
for r in v4:
    out = {"src": r["src"], "id": r["id"], "canon": r["canon"], "asr": r["asr"], "base_state": r["base_state"], "base_label": r["base_label"],
           "v4": (r["fix_state"], _rs(r["fix_reason"]), r["fix_label"], tuple(r["fix_warn"]))}
    for name, (a, b) in (("prod_off", (False, False)), ("prod_on", (True, True))):
        with guards(a, b):
            p = E.primary_stage(r["canon"], r["asr"], False)
        out[name] = (p["state"], _rs(p["reason"]), p["label"], tuple(sorted(p["warnings"])))
    rowsA.append(out)
E.api0_guard_off()


def v4sig(o): return (o["v4"][0], o["v4"][1], o["v4"][2], tuple(sorted(o["v4"][3])))


diffA_off = [o for o in rowsA if o["prod_off"] != v4sig(o)]
diffA_on = [o for o in rowsA if o["prod_on"] != v4sig(o)]
print(f"(A) items {len(rowsA)} (corpus {sum(1 for o in rowsA if not o['src'].startswith('U:'))} / unknown {sum(1 for o in rowsA if o['src'].startswith('U:'))})")
print(f"(A) Production(523/524 OFF) vs proto v4 差分: {len(diffA_off)}")
for o in diffA_off[:20]: print("   OFFDIFF", o["src"], o["id"][-40:], o["canon"][:24], "|", o["asr"][:24], o["v4"], "->", o["prod_off"])
print(f"(A) Production(523/524 ON) vs proto v4 差分: {len(diffA_on)}")
for o in diffA_on[:20]: print("   ONDIFF", o["src"], o["id"][-40:], o["canon"][:24], "|", o["asr"][:24], o["v4"], "->", o["prod_on"])
normal = [o for o in rowsA if o["src"] in ("P4", "POS") and o["base_state"] in PASSING and o["base_label"] in READ]
ng_normal = [o for o in normal if o["prod_on"][0] not in PASSING]
print(f"(A) 正常attempt(P4+正例のREADING_MATCH PASS) {len(normal)}件 のNG化/降格(Production ON): {len(ng_normal)}")
kn = [o for o in rowsA if o["id"] in KNOWN_NEG]
k_ok = len(kn) == 9 and all(o["base_state"] in PASSING and o["prod_on"][0] not in PASSING for o in kn)
print(f"(A) 既知負例9件がPASS以外へ(Production ON): {k_ok}")
base_read_pass = [o for o in rowsA if o["base_state"] in PASSING and o["base_label"] in READ]
now_pass = [o for o in base_read_pass if o["prod_on"][0] in PASSING]
print(f"(A) 現行READING_MATCH PASS {len(base_read_pass)} -> 是正後もPASS {len(now_pass)}; NG->PASS(広がり): {sum(1 for o in rowsA if o['base_state'] not in PASSING and o['prod_on'][0] in PASSING)}")
unk = [o for o in rowsA if o["src"].startswith("U:")]
print(f"(A) 未知データ{len(unk)}件の判定変化(現行->Production ON): {sum(1 for o in unk if (o['base_state'], ) != (o['prod_on'][0],))}")
accept = {}
for key in ("N3-02", "N3-07", "N3-21"):
    for o in rowsA:
        if o["id"] == key:
            accept[key] = {"canon": o["canon"], "asr": o["asr"], "base": o["base_state"], "label": o["base_label"], "prod_on": o["prod_on"][:2]}
for k, v in accept.items(): print("   ACCEPT", k, v)

# ---------------- (B) 合成 ----------------
UNITS = ["day", "day_span", "person", "hour", "hour_span", "minute", "second", "month", "month_span", "year", "year_span", "age", "kai", "ken", "ko",
         "week", "yen", "floor", "gen", "mai", "dai", "bai", "do", "km", "hon", "haku", "ban", "go", "tsu"]
NS = list(range(1, 31)) + [40, 50, 60, 70, 80, 90, 100, 200, 300, 400, 600, 800, 1000, 3000, 8000, 10000]
syn = []
for u in UNITS:
    surf = vg.COUNTERS[u][0]
    for n in NS:
        if u == "tsu" and n > 10:
            continue
        for r in [x for x in tr._cands(n, u) if x]:
            syn.append(("A", f"それは{n}{surf}です", f"それは{r}です"))
            syn.append(("C", f"それは{r}です", f"それは{n}{surf}です"))
            for m in {max(1, n - 1), n + 1, n * 2, n + 10}:
                if m == n or (u == "tsu" and m > 10):
                    continue
                syn.append(("B", f"それは{m}{surf}です", f"それは{r}です"))
                syn.append(("B_rev", f"それは{r}です", f"それは{m}{surf}です"))
            m = n + 3
            if not (u == "tsu" and m > 10):
                syn.append(("D_ok", f"{n}{surf}と{m}{surf}です", f"{r}と{m}{surf}です"))
                syn.append(("D_ng", f"{n}{surf}と{m}{surf}です", f"{r}と{m + 1}{surf}です"))
M2_NEG = [("とおくの町で7日", "とおくの町で8日、なのか"), ("とおくの町で7日滞在", "とおくの町で8日滞在なのか"), ("とおくの町で8日", "とおくの町で9日、しようか"),
          ("7日に会う。何なのか", "8日に会う。何なのか"), ("8日に会う。どうしようか", "9日に会う。どうしようか")]
M3_NEG = [("10人で行く", "さんじゅうにんで行く"), ("百円です", "にひゃくえんです"), ("十代の若者", "にじゅうだいの若者"), ("2時に会う", "にじゅうじに会う"),
          ("三十人で行く", "じゅうにんで行く"), ("二百円です", "ひゃくえんです"), ("1日に会う", "じゅういちにちに会う")]
SOKU_NEG = [("3本ください", "さんほんください"), ("3分待つ", "さんふん待つ"), ("8本です", "はちほんです"), ("6歳の子", "ろくさんの子"), ("三日待った", "さんにち待った")]
TWIN_NEG = [("三人と三人", "さんにんと四人"), ("3日と3日", "みっかと4日"), ("3日と3日", "4日とみっか"), ("三人と三人で", "四人とさんにんで")]
NEGATION_NEG = [("三日間は待たない", "みっかかんは待つ"), ("三日間待たない", "みっかかん待つ"), ("一番ではない", "いちばんである")]
for tag, grp in (("M2", M2_NEG), ("M3", M3_NEG), ("SOKU", SOKU_NEG), ("TWIN", TWIN_NEG), ("NEGATION", NEGATION_NEG)):
    syn += [(tag, c, a) for c, a in grp]
syn += [("O524", c, a) for c, a in [("4日に会う", "にじゅうよっかに会う"), ("4日に会う", "さんじゅうよっかに会う"), ("24日に会う", "にじゅうよっかに会う"), ("3日待つ", "みっかかん待つ"),
                                    ("にじゅうよっかに会う", "さんじゅうよっかに会う")]]
syn += [("O523", c, a) for c, a in [("6日に会う", "なのかに会う"), ("7日に会う", "なのかに会う"), ("8日に会う", "ようかに会う"), ("9日に会う", "ようかに会う"), ("10人で行く", "とおで行く"),
                                    ("なのかに会う", "6日に会う"), ("7日に会う。何なのか", "7日に会う。何なのか")]]
syn += [("ACC", c, a) for c, a in [("8,900本です", "89,000本です"), ("月のしわ、8,900本超", "月のすわ、8,900本超"), ("三日待ちます", "さんにち待ちます"), ("三日待ちます", "みっか待ちます"),
                                   ("体の活動が一番低い", "体の活動がいちばん低い")]]
syn = list(dict.fromkeys(syn))


class Sec:
    calls = 0

    def __call__(self, ctx):
        Sec.calls += 1
        return "x"


def prod_gate(c, a):
    r = uj.unified_judge(uj.AttemptCtx(canonical_text=c, wav_sha256="s", audio_seconds=1.0),
                         uj.PrimaryResult(True, a, label="PHONETIC_MATCH", equivalence_basis="READING_MATCH"), Sec(), lang="ja", role="comment")
    if r.reason_code in ("final_gate_value_diff", "final_gate_negation_diff"):
        return "NG_PROTECTED"
    if r.audit_record.get("p3_entry") == "primary_pass_demoted_ambiguous_value":
        return "DEMOTE_P3"
    return "PASS"


res = collections.defaultdict(dict)
with guards(False, False):
    ref = {(k, c, a): F4.reading_match_final_gate(c, a).state for k, c, a in syn}      # proto v4(基底=523/524 OFFのProduction value_guard)
    refw = {(k, c, a): F4.reading_match_final_gate(c, a).warnings for k, c, a in syn}
    p_off = {(k, c, a): prod_gate(c, a) for k, c, a in syn}
with guards(True, True):
    p_on = {(k, c, a): prod_gate(c, a) for k, c, a in syn}
diffB_off = [k for k in ref if ref[k] != p_off[k]]
diffB_on = [k for k in ref if ref[k] != p_on[k]]
print(f"(B) synthetic items {len(syn)}; Production(523/524 OFF) vs proto v4 差分: {len(diffB_off)}")
for k in diffB_off[:10]: print("   OFFDIFF", k, ref[k], p_off[k])
print(f"(B) Production(523/524 ON) vs proto v4 差分: {len(diffB_on)}")
widen = [k for k in diffB_on if ref[k] != "PASS" and p_on[k] == "PASS"]
narrow = [k for k in diffB_on if ref[k] == "PASS" and p_on[k] != "PASS"]
other = [k for k in diffB_on if k not in widen and k not in narrow]
print(f"(B)   ONの差分: 広がり(非PASS->PASS)={len(widen)} / 狭まり(PASS->非PASS)={len(narrow)} / その他(NG_PROTECTED<->DEMOTE)={len(other)}")
for k in diffB_on[:60]: print("   ONDIFF", k[0], k[1], "|", k[2], ref[k], "->", p_on[k])
cnt = collections.Counter((k[0], p_on[k]) for k in syn)
bad_pass = sum(v for (kd, st), v in cnt.items() if kd in ("B", "B_rev", "D_ng", "M2", "M3", "SOKU", "TWIN", "NEGATION") and st == "PASS")
fn = sum(v for (kd, st), v in cnt.items() if kd in ("A", "C", "D_ok") and st != "PASS")
fn_ref = sum(1 for k in syn if k[0] in ("A", "C", "D_ok") and ref[k] != "PASS")
print(f"(B) 誤PASS(Production ON; B/B_rev/D_ng/基準7合成負例): {bad_pass}; 誤NG(A/C/D_ok で非PASS) Production ON: {fn} / proto v4: {fn_ref}")
summary = {"A_items": len(rowsA), "A_diff_off": len(diffA_off), "A_diff_on": len(diffA_on), "A_normal": len(normal), "A_normal_ng": len(ng_normal), "A_known_neg_ok": k_ok,
           "A_base_read_pass": len(base_read_pass), "A_remain_pass": len(now_pass),
           "B_items": len(syn), "B_diff_off": len(diffB_off), "B_diff_on": len(diffB_on), "B_on_widen": len(widen), "B_on_narrow": len(narrow),
           "B_false_pass": bad_pass, "B_false_ng_prod": fn, "B_false_ng_v4": fn_ref}
print("summary:", json.dumps(summary, ensure_ascii=False))
json.dump({"summary": summary, "accept": accept, "A_diff_on": diffA_on, "A_diff_off": diffA_off,
           "B_diff_on": [[*k, ref[k], p_on[k]] for k in diffB_on], "B_diff_off": [[*k, ref[k], p_off[k]] for k in diffB_off],
           "B_counts": {f"{k[0]}/{k[1]}": v for k, v in sorted(cnt.items())}}, open(D + "open517_api0_prod_01.out.json", "w", encoding="utf8"), ensure_ascii=False, indent=1, default=str)
print("out sha256:", hashlib.sha256(open(D + "open517_api0_prod_01.out.json", "rb").read()).hexdigest())
