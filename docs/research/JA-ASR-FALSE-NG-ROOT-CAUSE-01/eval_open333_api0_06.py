# OPEN-333系 E4(便乗PASS)・E4-N(E3副作用の整合化)の API 0 評価。事前登録=OPEN333_E4_PREREGISTERED_01.md。保存済み転写のみ・LLM/ASR/TTS/ネットワーク呼出0(socket guard)。
# 比較基準 = 現行HEAD Production(E3適用済み。er011のE3 flagはTrueのまま)。arms: HEAD / F05_E4(proto_05 E3V_E4) / F06_E4(proto_06 E4) / F06_E4N / F06_E4_E4N。
# Cascade(Azure)はAPI 0ではstub。『Cascade行き』= 統一judgeのP3到達(audit p3_entry非null)。保存Secondary転写がある行は、その転写をAzure応答として注入した判定も併記。
# 再現: PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/eval_open333_api0_06.py   出力: open333_e4_eval_01.out.json
import collections, contextlib, hashlib, json, sys
sys.path.insert(0, "."); sys.path.insert(0, "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01")
import eval_common_02 as E
import proto_open333_fix_04 as P4
import proto_open333_fix_05 as P5
import proto_open333_fix_06 as P6
import sweep_cases_open333_02 as SW
import sweep_cases_open333_e4_01 as E4C
import sweep_cases_open333_e4_02 as E4D
import er007_ja_asr_validator_01 as javal
import er011_ja_asr_variant_layer_01 as VL
import er007_ja_secondary_asr_01 as sec

D = "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/"
javal.FEATURE_FLAG_A2_READING_RESOLVER_ENABLED = False
assert VL.CANDIDATE_E_FULL_DIFF_CHECK is True and VL.CANDIDATE_E_VALUE_GUARD_CHECK is True, "比較基準はE3適用済みHEAD"
PASSING = E.uj.PASSING_STATES
NEG_SRC = {"N1", "N3", "SYN"}
ARMS = [("F05_E4", P5, "E3V_E4"), ("F06_E4", P6, "E4"), ("F06_E4N", P6, "E4N"), ("F06_E4_E4N", P6, "E4_E4N")]
AN = [a[0] for a in ARMS]
CASCADE_YEN = 0.2667

rows_in = json.load(open(D + "open517_api0_eval_04.out.json", encoding="utf8"))["rows"]
items = [(r["src"], r["id"], r["canon"], r["asr"]) for r in rows_in]
bl = json.load(open(D + "eval_b_light_api0_02.out.json", encoding="utf8"))
seen = set()
for i, s in enumerate(bl["synthetic_negative"]):
    k = (s["canon"], s["primary"])
    if k in seen:
        continue
    seen.add(k)
    items.append(("SYN", f"syn-{i:03d}:{s['group']}:{s['type'][:40]}", s["canon"], s["primary"]))
prev04 = {(r["canon"], r["asr"]): r for r in json.load(open(D + "open333_api0_eval_04.out.json", encoding="utf8"))["rows"]}
STORED_SEC = {}
for k in ("moon", "n3", "hist"):
    for x in bl[k]:
        if x.get("secondary") and x.get("canon") and x.get("primary"):
            STORED_SEC[(x["canon"], x["primary"])] = x["secondary"]
if bl.get("melos") and bl["melos"].get("secondary") and bl["melos"].get("primary"):
    STORED_SEC[(bl["melos"]["canon"], bl["melos"]["primary"])] = bl["melos"]["secondary"]
for s in bl["synthetic_negative"]:
    if s.get("secondary"):
        STORED_SEC[(s["canon"], s["primary"])] = s["secondary"]
E.api0_guard_on()


def rs(x):
    return "primary_pass" if str(x).startswith("primary_pass") else x


def stage(canon, asr, arm=None, secondary_text=None):
    orig_az = sec._azure_stt_strict
    if secondary_text is None:
        sec._azure_stt_strict = lambda p, language="ja-JP", timeout_seconds=90: (None, "api0_stub_no_call")
    else:
        sec._azure_stt_strict = lambda p, language="ja-JP", timeout_seconds=90: (secondary_text, None)
    cm = contextlib.nullcontext()
    if arm is not None:
        _, mod, mname = next(a for a in ARMS if a[0] == arm)
        cm = mod.apply_in_process(mname)
    try:
        with cm:
            r = sec.evaluate_attempt_ja_with_cascade_detail(canon, asr, E.dummy_wav(), cascade_enabled=True, attempt_ctx={"max_len": 400})
    finally:
        sec._azure_stt_strict = orig_az
    j = r["asr_judgement"]
    state = j.get("state")
    cls = r["classification"].classification if r.get("classification") is not None else None
    p3 = j.get("p3_entry")
    return {"state": state, "reason": rs(j.get("reason_code")), "label": cls, "p3": p3, "klass": ("PASS" if state in PASSING else ("CASC" if p3 else "NG"))}


def key(x):
    return (x["state"], x["reason"], x["label"])


def kind(h, a):
    """HEADに対する遷移種別。"""
    if key(h) == key(a):
        return "不変"
    hk, ak = h["klass"], a["klass"]
    if hk != "PASS" and ak == "PASS":
        return "非PASS→PASS(違反)"
    if hk == "PASS" and ak == "CASC":
        return "PASS→Cascade"
    if hk == "PASS" and ak == "NG":
        return "PASS→即NG(違反)"
    if hk == "NG" and ak == "CASC":
        return "拒否→Cascade"
    if hk == "CASC" and ak == "NG":
        return "Cascade→即NG(違反)"
    if hk == ak:
        return f"同種内変化({hk})"
    return f"その他({hk}→{ak})"


def run_all(canon, asr, stored=None):
    out = {"HEAD": stage(canon, asr)}
    for a in AN:
        out[a] = stage(canon, asr, a)
    if stored is not None:
        out["sec_HEAD"] = stage(canon, asr, None, stored)
        for a in AN:
            out["sec_" + a] = stage(canon, asr, a, stored)
    return out


def probe(canon, asr):
    cn, an = javal.normalize_ja(canon), javal.normalize_ja(asr)
    r = javal.classify_ja_asr_match(canon, asr, allow_reading_resolver=False)
    p = javal.protected_check_ja(cn, an)
    return {"cls": r.classification, "e_pass": bool("Candidate E" in (r.reason or "") and r.should_pass), "num_entry": bool(p.number_mismatches),
            "casc": [(d["canonical"], d["asr"], bool(d["entity_like"]), bool(d["phonetic_uncertain"])) for d in p.content_diffs if d["cascade_eligible"]],
            "e4n_items": [(i["canonical"], i["asr"], i["cascade_eligible"]) for i in P6.audit_e3_classified(cn, an)] if p.number_mismatches else None}


def tally(rows, arms=AN):
    t = {}
    for a in arms:
        c = collections.Counter(kind(r["HEAD"], r[a]) for r in rows)
        t[a] = dict(c)
    return t


# ---- 1. 実データ+合成負例 1,327行 ----
real_rows, parity_bad = [], []
for src, ident, canon, asr in items:
    stored = STORED_SEC.get((canon, asr))
    r = run_all(canon, asr, stored)
    row = {"src": src, "id": ident, "canon": canon, "asr": asr, "has_stored_secondary": stored is not None, "stored_secondary": stored, "probe": probe(canon, asr), **r}
    p = prev04.get((canon, asr))
    if p is not None and key(r["HEAD"]) != (p["E3V"]["state"], p["E3V"]["reason"], p["E3V"]["label"]):
        parity_bad.append((ident, key(r["HEAD"]), (p["E3V"]["state"], p["E3V"]["reason"], p["E3V"]["label"])))
    real_rows.append(row)
print(f"[実データ+SYN] 行数 {len(real_rows)} / 保存Secondary転写あり {sum(1 for r in real_rows if r['has_stored_secondary'])} / "
      f"[parity] HEAD(E3適用済み) vs 前回評価E3V(eval_04保存)の不一致 {len(parity_bad)}")
for x in parity_bad[:10]:
    print("  PARITY差:", x)
nonneg = [r for r in real_rows if r["src"] not in NEG_SRC]
head_pass_nonneg = [r for r in nonneg if r["HEAD"]["klass"] == "PASS"]
print(f"HEAD: 全PASS {sum(1 for r in real_rows if r['HEAD']['klass']=='PASS')} / 負例以外のPASS {len(head_pass_nonneg)} / Cascade到達 {sum(1 for r in real_rows if r['HEAD']['klass']=='CASC')} / 即NG {sum(1 for r in real_rows if r['HEAD']['klass']=='NG')}")
print("[実データ] HEADとの遷移種別:", json.dumps(tally(real_rows), ensure_ascii=False))
for a in AN:
    ch = [r for r in real_rows if kind(r["HEAD"], r[a]) != "不変"]
    print(f"\n== 実データ {a}: HEADから変わる行 {len(ch)} ==")
    for r in ch:
        print(f"   {r['src']:5s} {r['id'][-34:]:34s} | {r['canon'][:26]} | {r['asr'][:26]} | {kind(r['HEAD'], r[a])} | {r['HEAD']['state']}/{r['HEAD']['reason']} -> {r[a]['state']}/{r[a]['reason']} | casc={r['probe']['casc']}")
        if r["has_stored_secondary"]:
            print(f"         保存Secondary転写で: HEAD={r['sec_HEAD']['state']}  {a}={r['sec_'+a]['state']} ({r['sec_'+a]['reason']})")
print("\n== 保存Secondary転写がある行: 転写注入後の最終判定のHEADとの差 ==")
srows = [r for r in real_rows if r["has_stored_secondary"]]
for a in AN:
    d = [r for r in srows if key(r["sec_HEAD"]) != key(r["sec_" + a])]
    n2p = [r for r in srows if r["sec_HEAD"]["klass"] != "PASS" and r["sec_" + a]["klass"] == "PASS"]
    p2n = [r for r in srows if r["sec_HEAD"]["klass"] == "PASS" and r["sec_" + a]["klass"] != "PASS"]
    print(f" {a}: 対象{len(srows)}行 / 判定が変わる{len(d)} / 非PASS→PASS {len(n2p)} / PASS→非PASS {len(p2n)}")
    for r in d + n2p + p2n:
        print(f"    {r['id'][-34:]} | {r['canon'][:22]} | {r['sec_HEAD']['state']}/{r['sec_HEAD']['reason']} -> {r['sec_'+a]['state']}/{r['sec_'+a]['reason']}")

# ---- 2. M-3 sweep 40 + 旧v2 sweep 29 ----
sw_rows = []
for cls, c, a, tag, note in SW.CASES:
    r = run_all(c, a)
    sw_rows.append({"cls": cls, "canon": c, "asr": a, "tag": tag, "note": note, **r})
base_c = "月のしわ、8,900本超"
old = []
for g in ["し", "す", "そ", "しわ", "すわ", "しゃわ", "しわー", "しば", "すば", "しわわ", "ちわ", "しーわ"]:
    old += [(base_c, f"月の{g}八千九百本長"), (base_c, f"月の{g}、八千九百本長")]
old += [("売上は8,900円です", "売上は八千九百えんです"), ("売上は8,900円です", "売上は八千九百円です"), ("売上は8,900円です", "売上は八千九百ドルです"),
        ("売上は8,900円超です", "売上は八千九百円長です"), ("売上は8,900円超です", "売上は八千九百円腸です")]
old_rows = [{"canon": c, "asr": a, **run_all(c, a)} for c, a in old]
print("\n== sweep(M-3 40 + 旧29) ==")
for nm, rr in (("M-3 sweep", sw_rows), ("旧v2 sweep", old_rows)):
    print(f" {nm} {len(rr)}件: HEAD PASS {sum(1 for r in rr if r['HEAD']['klass']=='PASS')} / 遷移 {json.dumps(tally(rr), ensure_ascii=False)}")
    for a in AN:
        for r in rr:
            if kind(r["HEAD"], r[a]) != "不変":
                print(f"    {a} {kind(r['HEAD'], r[a])}: {r['canon']} | {r['asr']} | {r['HEAD']['state']} -> {r[a]['state']}")

# ---- 3. E4 / E4-N 負例・対照・cost ----
e4rows = []
for x in E4C.build() + E4D.build():
    r = run_all(x["canon"], x["asr"])
    pr = probe(x["canon"], x["asr"])
    e4rows.append({**x, **r, "reach_E": pr["e_pass"], "num_entry": pr["num_entry"], "e4n_items": pr["e4n_items"]})
print(f"\n== E4/E4-N 行 {len(e4rows)}件 ==")


def dist(rr, m):
    c = collections.Counter(r[m]["klass"] for r in rr)
    return f"PASS={c.get('PASS',0)} Cascade={c.get('CASC',0)} 即NG={c.get('NG',0)}"


groups = collections.OrderedDict()
for r in e4rows:
    groups.setdefault((r["kind"], r["entry"]), []).append(r)
for (kd, en), rr in groups.items():
    print(f" kind={kd:15s} entry={en} n={len(rr):3d} | HEAD: {dist(rr,'HEAD')}")
    for a in AN:
        print(f"      {a:11s}: {dist(rr, a)}  遷移={dict(collections.Counter(kind(r['HEAD'], r[a]) for r in rr))}")
print("\n -- ラベル別(neg/neg_hira): HEAD PASS数 → 各arm PASS数 / Cascade数 --")
for kd in ("neg", "neg_hira"):
    labs = sorted({r["label"] for r in e4rows if r["kind"] == kd})
    for lb in labs:
        rr = [r for r in e4rows if r["kind"] == kd and r["label"] == lb]
        print(f"   {kd:8s} {lb:30s} n={len(rr):2d} HEAD_PASS={sum(1 for r in rr if r['HEAD']['klass']=='PASS'):2d} " + " ".join(f"{a}:P{sum(1 for r in rr if r[a]['klass']=='PASS')}/C{sum(1 for r in rr if r[a]['klass']=='CASC')}" for a in AN))
print("\n -- cost(正常な等価表記): ラベル別 HEAD→arm --")
for lb in sorted({r["label"] for r in e4rows if r["kind"] == "cost"}):
    for en in ("txt", "num"):
        rr = [r for r in e4rows if r["kind"] == "cost" and r["label"] == lb and r["entry"] == en]
        print(f"   {lb:24s} {en} n={len(rr)} HEAD:[{dist(rr,'HEAD')}] " + " ".join(f"{a}:[{dist(rr,a)}]" for a in ("F06_E4", "F06_E4_E4N")))
print("\n -- e4n_keep_reject(名の差+しわ→すわ型): arm別 --")
rr = [r for r in e4rows if r["kind"] == "e4n_keep_reject"]
for r in rr:
    print(f"    {r['canon']} | {r['asr']} | HEAD={r['HEAD']['state']}/{r['HEAD']['reason']} E4N={r['F06_E4N']['state']}/{r['F06_E4N']['reason']} items={r['e4n_items']}")
print("\n -- out_of_scope(乗り物なし数値entryのcascade差): 不変であるべき --")
rr = [r for r in e4rows if r["kind"] == "out_of_scope"]
print("   遷移:", json.dumps(tally(rr), ensure_ascii=False), "/ HEAD分布:", dist(rr, "HEAD"))
n2p_e4 = [r for r in e4rows if r["HEAD"]["klass"] != "PASS" and any(r[a]["klass"] == "PASS" for a in AN)]
ctrl_chg = [r for r in e4rows if r["kind"] == "ctrl" and any(key(r[a]) != key(r["HEAD"]) for a in AN)]
print(" E4行 非PASS→PASS:", len(n2p_e4), "/ ctrl の変化:", len(ctrl_chg))
neg_all = [r for r in e4rows if r["kind"] in ("neg", "neg_hira")]
print(f" 負例(neg {sum(1 for r in e4rows if r['kind']=='neg')} + neg_hira {sum(1 for r in e4rows if r['kind']=='neg_hira')}): HEAD PASS {sum(1 for r in neg_all if r['HEAD']['klass']=='PASS')} / " +
      " ".join(f"{a} PASS={sum(1 for r in neg_all if r[a]['klass']=='PASS')}" for a in AN))
allrows = real_rows + sw_rows + old_rows + e4rows
eq = sum(1 for r in allrows if key(r["F05_E4"]) == key(r["F06_E4"]))
print(f"\n[同値性] F05_E4 と F06_E4 の判定key一致: {eq}/{len(allrows)}")

# ---- 4. 全件の遷移種別 ----
print("\n== 全母集団(実データ+SYN+sweep+旧sweep+E4行)のHEADとの遷移種別 ==")
overall = tally(allrows)
for a in AN:
    print(f" {a}: {json.dumps(overall[a], ensure_ascii=False)}")
viol = {a: sum(v for k, v in overall[a].items() if "違反" in k) for a in AN}
print(" 違反(非PASS→PASS / PASS→即NG / Cascade→即NG)件数:", viol)

# ---- 5. QCD ----
print("\n== QCD(実データ1,327行ベース。Cascade 1回=%.4f円) ==" % CASCADE_YEN)
qcd = {}
for a in AN:
    p2c = sum(1 for r in real_rows if kind(r["HEAD"], r[a]) == "PASS→Cascade")
    n2c = sum(1 for r in real_rows if kind(r["HEAD"], r[a]) == "拒否→Cascade")
    p2c_nn = sum(1 for r in nonneg if kind(r["HEAD"], r[a]) == "PASS→Cascade")
    qcd[a] = {"pass_to_cascade_all": p2c, "reject_to_cascade_all": n2c, "pass_to_cascade_nonneg": p2c_nn,
              "cascade_yen_per_segment_nonneg": round(p2c_nn * CASCADE_YEN / max(1, len(head_pass_nonneg)), 5),
              "pass_to_cascade_pct_of_nonneg_pass": round(100 * p2c_nn / max(1, len(head_pass_nonneg)), 3)}
    print(" ", a, json.dumps(qcd[a], ensure_ascii=False))

# ---- 6. Secondary受理(M-2) ----
sec_pairs = []
for k in ("moon", "n3", "hist"):
    for x in bl[k]:
        s = x.get("secondary")
        if s and x.get("canon"):
            sec_pairs.append((k, x["canon"], s))
if bl.get("melos") and bl["melos"].get("secondary"):
    sec_pairs.append(("melos", bl["melos"]["canon"], bl["melos"]["secondary"]))
for s in bl["synthetic_negative"]:
    if s.get("secondary"):
        sec_pairs.append(("syn", s["canon"], s["secondary"]))
sec_pairs = list(dict.fromkeys(sec_pairs))
prim_as_sec = list(dict.fromkeys([("primary_as_secondary", r["canon"], r["asr"]) for r in real_rows if r["asr"]]))


def sec_sim(canon, stext, arm=None):
    cm = contextlib.nullcontext()
    if arm is not None:
        _, mod, mname = next(a for a in ARMS if a[0] == arm)
        cm = mod.apply_in_process(mname)
    with cm:
        c1 = javal.classify_ja_asr_match(canon, stext, allow_reading_resolver=False)
        c2 = sec._apply_variant_layer_voicing_upgrade(canon, stext, c1)
        return (c1.classification, c2.classification, c1.classification in sec.SCG_PASS_CLASSIFICATIONS, bool(sec._orthographic_reading_confirmed(c2)))


sec_res = {}
for name, pairs in (("stored_secondary", sec_pairs), ("all_primary_as_secondary", prim_as_sec)):
    lc = {a: 0 for a in AN}
    ac = {a: 0 for a in AN}
    for tag, c, s in pairs:
        b = sec_sim(c, s)
        for a in AN:
            r = sec_sim(c, s, a)
            lc[a] += int(r[:2] != b[:2])
            ac[a] += int(r[2:] != b[2:])
    sec_res[name] = {"n": len(pairs), "label_changes": lc, "accept_changes": ac}
    print(f"\n[Secondary受理] {name}: n={len(pairs)} ラベル変化 {lc} / 受理(SCG_PASS・orth)変化 {ac}")
E.api0_guard_off()

summary = {"real_rows": len(real_rows), "parity_bad": len(parity_bad), "stored_secondary_rows": len(srows), "all_rows": len(allrows), "violations": viol,
           "overall": overall, "qcd": qcd, "secondary": sec_res, "e4_rows": len(e4rows), "ctrl_changed": len(ctrl_chg), "e4_n2p": len(n2p_e4)}
print("\nsummary:", json.dumps(summary, ensure_ascii=False))
json.dump({"summary": summary, "real": real_rows, "sweep": sw_rows, "old_sweep": old_rows, "e4": e4rows}, open(D + "open333_e4_eval_01.out.json", "w", encoding="utf8"),
          ensure_ascii=False, indent=1, default=str, sort_keys=True)
print("out sha256:", hashlib.sha256(open(D + "open333_e4_eval_01.out.json", "rb").read()).hexdigest())
