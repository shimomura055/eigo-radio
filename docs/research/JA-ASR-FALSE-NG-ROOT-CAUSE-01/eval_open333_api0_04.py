# OPEN-333系(しわ↔すわ)是正案 E3 v3[P-1なし]・E4 の API 0 評価。事前登録=OPEN333_PREREGISTERED_02.md。保存済み転写のみ・LLM/ASR/TTS/ネットワーク呼出0(socket guard)。
# 比較: 現行HEAD Production(er011のE3 flagが存在する場合は False に固定) vs proto E3 / E3V (proto_open333_fix_04) / E3V_E4 / E3V_E4E (proto_open333_fix_05)。
# 出力: open333_api0_eval_04.out.json / 標準出力(.out.txt)。再現: PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/eval_open333_api0_04.py
import collections, hashlib, json, sys
sys.path.insert(0, "."); sys.path.insert(0, "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01")
import eval_common_02 as E
import proto_open333_fix_04 as P4
import proto_open333_fix_05 as P5
import sweep_cases_open333_02 as SW
import sweep_cases_open333_e4_01 as E4C
import er007_ja_asr_validator_01 as javal
import er011_ja_asr_variant_layer_01 as VL
import er007_ja_secondary_asr_01 as sec

D = "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/"
javal.FEATURE_FLAG_A2_READING_RESOLVER_ENABLED = False
for _f in ("CANDIDATE_E_FULL_DIFF_CHECK", "CANDIDATE_E_VALUE_GUARD_CHECK"):
    if hasattr(VL, _f):
        setattr(VL, _f, False)       # 比較基準=現行HEAD挙動(Production側にE3が入っていても評価の基準は適用前)
PASSING = E.uj.PASSING_STATES
NEG_SRC = {"N1", "N3", "SYN"}
MODES = [("E3", P4, "E3"), ("E3V", P4, "E3V"), ("E3V_E4", P5, "E3V_E4"), ("E3V_E4E", P5, "E3V_E4E")]
MN = [m[0] for m in MODES]

rows_in = json.load(open(D + "open517_api0_eval_04.out.json", encoding="utf8"))["rows"]
items = [(r["src"], r["id"], r["canon"], r["asr"], r["fix_state"]) for r in rows_in]
bl = json.load(open(D + "eval_b_light_api0_02.out.json", encoding="utf8"))
seen = set()
for i, s in enumerate(bl["synthetic_negative"]):
    k = (s["canon"], s["primary"])
    if k in seen:
        continue
    seen.add(k)
    items.append(("SYN", f"syn-{i:03d}:{s['group']}:{s['type'][:40]}", s["canon"], s["primary"], None))
E.api0_guard_on()


def rs(x):
    return "primary_pass" if str(x).startswith("primary_pass") else x


def run(canon, asr, mode=None, log=None):
    if mode is None:
        return E.primary_stage(canon, asr, False)
    _, mod, mname = next(m for m in MODES if m[0] == mode)
    with mod.apply_in_process(mname, log=log):
        return E.primary_stage(canon, asr, False)


def probe(canon, asr):
    cn, an = javal.normalize_ja(canon), javal.normalize_ja(asr)
    r = javal.classify_ja_asr_match(canon, asr, allow_reading_resolver=False)
    e = "Candidate E" in (r.reason or "")
    p = javal.protected_check_ja(cn, an)
    return {"cls": r.classification, "e_pass": bool(e and r.should_pass), "num_entry": bool(p.number_mismatches),
            "e3_bad": P4.audit_e3(cn, an) if e else None, "veto": P4.value_veto(canon, asr) if e else None,
            "diffs": [(d["canonical"], d["asr"]) for d in p.content_diffs],
            "casc": [(d["canonical"], d["asr"], bool(d["entity_like"])) for d in p.content_diffs if d["cascade_eligible"]]}


def key(r, m=None):
    return (r["base_state"], r["base_reason"], r["base_label"]) if m is None else (r[m]["state"], r[m]["reason"], r[m]["label"])


out_rows, mism = [], []
for src, ident, canon, asr, stored in items:
    b = run(canon, asr)
    if stored is not None and b["state"] != stored:
        mism.append((ident, b["state"], stored))
    row = {"src": src, "id": ident, "canon": canon, "asr": asr, "base_state": b["state"], "base_reason": rs(b["reason"]), "base_label": b["label"], "probe": probe(canon, asr)}
    for m in MN:
        r = run(canon, asr, m)
        row[m] = {"state": r["state"], "reason": rs(r["reason"]), "label": r["label"]}
    out_rows.append(row)
print(f"items: {len(out_rows)}  [parity] 現行HEADの再計算 vs eval_04保存fix_state(07A後proto)の不一致: {len(mism)}")


def bp(r):
    return r["base_state"] in PASSING


def np_(r, m):
    return r[m]["state"] in PASSING


epass = [r for r in out_rows if bp(r) and r["probe"]["e_pass"]]
print(f"\n== 棚卸し: 現行PASSのうちCandidate E経由 {len(epass)} / 現行PASS全体 {sum(1 for r in out_rows if bp(r))} ==")
print(" 内訳:", dict(collections.Counter((r["src"], "数値entry" if r["probe"]["num_entry"] else "非数値entry") for r in epass)))
res = {}
for m in MN:
    chg = [r for r in out_rows if key(r) != key(r, m)]
    p2n = [r for r in chg if bp(r) and not np_(r, m)]
    n2p = [r for r in out_rows if (not bp(r)) and np_(r, m)]
    other = [r for r in chg if r not in p2n]
    ctrl_ng = [r for r in p2n if r["src"] not in NEG_SRC]
    neg_blocked = [r for r in p2n if r["src"] in NEG_SRC]
    real_base = [r for r in out_rows if bp(r) and r["src"] not in NEG_SRC]
    outside = [r for r in chg if not (r["probe"]["e_pass"] and bp(r))]
    res[m] = {"changed": len(chg), "pass_to_ng": len(p2n), "ng_to_pass": len(n2p), "other_changed": len(other), "changed_outside_E_pass_rows": len(outside),
              "non_negative_pass_to_ng": len(ctrl_ng), "neg_pass_blocked": len(neg_blocked), "neg_pass_before": sum(1 for r in out_rows if r["src"] in NEG_SRC and bp(r)),
              "non_negative_pass_before": len(real_base), "regen_increase_pct": round(100 * len(ctrl_ng) / max(1, len(real_base)), 3)}
    print(f"\n== {m}: 変化 {len(chg)} (PASS->非PASS {len(p2n)} / 非PASS->PASS {len(n2p)} / その他 {len(other)} / E経由PASS行の外の変化 {len(outside)}) ==")
    for r in p2n:
        print(f"   {r['src']:5s} {r['id'][-46:]:46s} | {r['canon'][:32]} | {r['asr'][:32]} | {r['base_state']} -> {r[m]['state']}/{r[m]['reason']}")
    for r in other:
        print("   OTHER", r["id"], key(r), "->", key(r, m))
    print(" ", json.dumps(res[m], ensure_ascii=False))
print("\n== E3 と E3V の差(行) ==")
dd = [r for r in out_rows if key(r, "E3") != key(r, "E3V")]
print(" 件数:", len(dd))
for r in dd:
    print("   ", r["id"][-40:], key(r, "E3"), "->", key(r, "E3V"))

# ---- M-3 sweep ----
print("\n== M-3 sweep(8クラス + 旧v2 sweep) ==")
sw_rows = []
for cls, c, a, tag, note in SW.CASES:
    b = run(c, a)
    pr = probe(c, a)
    row = {"cls": cls, "canon": c, "asr": a, "tag": tag, "note": note, "base": b["state"], "base_reason": rs(b["reason"]), "base_label": b["label"],
           "reach_E_num": bool(pr["e_pass"] and pr["num_entry"]), "base_cls": pr["cls"]}
    for m in MN:
        r = run(c, a, m)
        row[m] = {"state": r["state"], "reason": rs(r["reason"]), "label": r["label"]}
    sw_rows.append(row)


def sw_viol(x, m):
    """keep: 合否(PASS/非PASS)が現行と同一であるべき(NG->NGのreason差は違反にしない。別途OTHERとして開示)。block: 現行PASSなら非PASSになるべき。"""
    if x["tag"] == "keep":
        return (x["base"] in PASSING) != (x[m]["state"] in PASSING)
    return x["base"] in PASSING and x[m]["state"] in PASSING


def audit_viol(x):
    """関数レベル(現行がEに到達しない行も含めて検査): keepは非数値差の拒否が空であるべき / blockは拒否が非空であるべき。"""
    cn, an = javal.normalize_ja(x["canon"]), javal.normalize_ja(x["asr"])
    bad = P4.audit_e3(cn, an)
    return (bool(bad) if x["tag"] == "keep" else (not bad)), bad


bycls = collections.defaultdict(list)
for x in sw_rows:
    bycls[x["cls"]].append(x)
for cl in sorted(bycls):
    xs = bycls[cl]
    print(f" クラス{cl}: {len(xs)}件 / 現行PASS {sum(1 for x in xs if x['base'] in PASSING)} / E数値entry到達 {sum(1 for x in xs if x['reach_E_num'])} / " +
          " ".join(f"{m}:違反{sum(1 for x in xs if sw_viol(x, m))}" for m in MN[:2]))
for x in sw_rows:
    print(f"  c{x['cls']} {x['tag']:5s} base={'PASS' if x['base'] in PASSING else 'NG  '}{'(E)' if x['reach_E_num'] else '   '} E3={'PASS' if x['E3']['state'] in PASSING else 'NG  '} "
          f"E3V={'PASS' if x['E3V']['state'] in PASSING else 'NG  '} | {x['canon']} | {x['asr']} | {x['note']}" +
          (" <-違反E3" if sw_viol(x, "E3") else "") + (" <-違反E3V" if sw_viol(x, "E3V") else ""))
print(" -- 関数レベル(audit_e3単体。現行がEに到達しない行も含む) --")
av = []
for x in sw_rows:
    v, bad = audit_viol(x)
    x["audit_bad"] = bad
    x["audit_viol"] = v
    if v:
        av.append(x)
for cl in sorted(bycls):
    xs = bycls[cl]
    print(f"   クラス{cl}: {len(xs)}件 keep={sum(1 for x in xs if x['tag']=='keep')} block={sum(1 for x in xs if x['tag']=='block')} audit違反={sum(1 for x in xs if x['audit_viol'])}")
for x in av:
    print(f"   audit違反: c{x['cls']} {x['tag']} | {x['canon']} | {x['asr']} | audit_bad={x['audit_bad']} | {x['note']}")
sw_new_pass = [x for x in sw_rows if x["base"] not in PASSING and any(x[m]["state"] in PASSING for m in MN)]
print(" sweep 非PASS->PASS:", len(sw_new_pass))
base_c = "月のしわ、8,900本超"
old = []
for g in ["し", "す", "そ", "しわ", "すわ", "しゃわ", "しわー", "しば", "すば", "しわわ", "ちわ", "しーわ"]:
    old += [(base_c, f"月の{g}八千九百本長"), (base_c, f"月の{g}、八千九百本長")]
old += [("売上は8,900円です", "売上は八千九百えんです"), ("売上は8,900円です", "売上は八千九百円です"), ("売上は8,900円です", "売上は八千九百ドルです"),
        ("売上は8,900円超です", "売上は八千九百円長です"), ("売上は8,900円超です", "売上は八千九百円腸です")]
old_rows = []
for c, a in old:
    b = run(c, a)
    row = {"canon": c, "asr": a, "base": b["state"]}
    for m in MN:
        row[m] = run(c, a, m)["state"]
    old_rows.append(row)
op = [x for x in old_rows if x["base"] in PASSING]
print(f" 旧v2 sweep {len(old_rows)}件 / 現行PASS {len(op)} / E3後PASS {sum(1 for x in old_rows if x['E3'] in PASSING)} / E3V後PASS {sum(1 for x in old_rows if x['E3V'] in PASSING)} / "
      f"非PASS->PASS {sum(1 for x in old_rows if x['base'] not in PASSING and any(x[m] in PASSING for m in MN))}")
for x in old_rows:
    if x["base"] in PASSING:
        print(f"   {x['canon']} | {x['asr']} | base=PASS E3={x['E3']} E3V={x['E3V']}")

# ---- E4 ---
print("\n== E4(便乗PASS): 負例/対照/コスト ==")
e4rows = []
for x in E4C.build():
    b = run(x["canon"], x["asr"])
    pr = probe(x["canon"], x["asr"])
    row = dict(x, base=b["state"], base_reason=rs(b["reason"]), reach_E=bool(pr["e_pass"]), casc=pr["casc"])
    for m in MN:
        r = run(x["canon"], x["asr"], m)
        row[m] = {"state": r["state"], "reason": rs(r["reason"])}
    e4rows.append(row)
for kind in ("neg", "cost", "ctrl"):
    xs = [x for x in e4rows if x["kind"] == kind]
    print(f" kind={kind}: {len(xs)}件 / 現行PASS {sum(1 for x in xs if x['base'] in PASSING)} (うちE経由 {sum(1 for x in xs if x['reach_E'] and x['base'] in PASSING)}) / " +
          " ".join(f"{m}後PASS={sum(1 for x in xs if x[m]['state'] in PASSING)}" for m in MN))
for ent in ("txt", "num"):
    for kind in ("neg", "cost", "ctrl"):
        xs = [x for x in e4rows if x["kind"] == kind and x["entry"] == ent]
        print(f"   entry={ent} kind={kind}: {len(xs)}件 / 現行PASS {sum(1 for x in xs if x['base'] in PASSING)} / " + " ".join(f"{m}後PASS={sum(1 for x in xs if x[m]['state'] in PASSING)}" for m in MN))
neg = [x for x in e4rows if x["kind"] == "neg"]
print(" -- neg: ラベル別 現行PASS(便乗)/E3V_E4後PASS/E3V_E4E後PASS --")
for lb in sorted({x["label"] for x in neg}):
    xs = [x for x in neg if x["label"] == lb]
    print(f"   {lb:34s} n={len(xs):2d} 現行PASS={sum(1 for x in xs if x['base'] in PASSING):2d} E4後PASS={sum(1 for x in xs if x['E3V_E4']['state'] in PASSING):2d} "
          f"E4E後PASS={sum(1 for x in xs if x['E3V_E4E']['state'] in PASSING):2d}")
print(" -- cost ラベル別 --")
for lb in sorted({x["label"] for x in e4rows if x["kind"] == "cost"}):
    xs = [x for x in e4rows if x["kind"] == "cost" and x["label"] == lb]
    print(f"   {lb:34s} n={len(xs):2d} 現行PASS={sum(1 for x in xs if x['base'] in PASSING):2d} E4後PASS={sum(1 for x in xs if x['E3V_E4']['state'] in PASSING):2d} "
          f"E4E後PASS={sum(1 for x in xs if x['E3V_E4E']['state'] in PASSING):2d}")
e4_n2p = [x for x in e4rows if x["base"] not in PASSING and any(x[m]["state"] in PASSING for m in MN)]
ctrl_chg = [x for x in e4rows if x["kind"] == "ctrl" and any((x[m]["state"], x[m]["reason"]) != (x["base"], x["base_reason"]) for m in MN)]
print(" E4行 非PASS->PASS:", len(e4_n2p), "/ ctrl の変化:", len(ctrl_chg))

print("\n== 実データ(1,327行): E4がE3V単独に対して動かす行 ==")
for m in ("E3V_E4", "E3V_E4E"):
    ds = [r for r in out_rows if key(r, m) != key(r, "E3V")]
    print(f" {m}: {len(ds)}件")
    for r in ds:
        print(f"   {r['src']:5s} {r['id'][-34:]:34s} | {r['canon'][:28]} | {r['asr'][:28]} | casc={r['probe']['casc']} {r['E3V']['state']} -> {r[m]['state']}")

# ---- M-2: Secondary ----
print("\n== M-2 Secondary転写 ==")
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
prim_as_sec = list(dict.fromkeys([("primary_as_secondary", r["canon"], r["asr"]) for r in out_rows if r["asr"]]))


def sec_sim(canon, stext, mode=None):
    def f():
        c1 = javal.classify_ja_asr_match(canon, stext, allow_reading_resolver=False)
        c2 = sec._apply_variant_layer_voicing_upgrade(canon, stext, c1)
        return (c1.classification, c2.classification, c1.classification in sec.SCG_PASS_CLASSIFICATIONS, bool(sec._orthographic_reading_confirmed(c2)))
    if mode is None:
        return f()
    _, mod, mname = next(m for m in MODES if m[0] == mode)
    with mod.apply_in_process(mname):
        return f()


sec_res = {}
for name, pairs in (("stored_secondary", sec_pairs), ("all_primary_as_secondary", prim_as_sec)):
    chg = {m: [] for m in MN}
    acc_chg = {m: [] for m in MN}
    for tag, c, s in pairs:
        b = sec_sim(c, s)
        for m in MN:
            r = sec_sim(c, s, m)
            if r != b:
                chg[m].append((tag, c[:30], s[:30], b[:2], r[:2]))
            if r[2:] != b[2:]:
                acc_chg[m].append((tag, c[:30], s[:30], b[2:], r[2:]))
    sec_res[name] = {"n": len(pairs), "label_changes": {m: len(chg[m]) for m in MN}, "accept_changes": {m: len(acc_chg[m]) for m in MN}}
    print(f" {name}: n={len(pairs)} ラベル変化 {sec_res[name]['label_changes']} / 受理(SCG_PASS・orth)変化 {sec_res[name]['accept_changes']}")
    for m in MN:
        for x in chg[m][:8]:
            print(f"    [{m}] ラベル変化: {x}")
E.api0_guard_off()

summary = {"items": len(out_rows), "parity_mismatch": len(mism), "e_pass_rows": len(epass), "per_mode": res, "sweep": len(sw_rows),
           "sweep_viol": {m: sum(1 for x in sw_rows if sw_viol(x, m)) for m in MN[:2]}, "sweep_audit_viol": len(av),
           "sweep_new_pass": len(sw_new_pass), "e4": {"rows": len(e4rows), "n2p": len(e4_n2p), "ctrl_changed": len(ctrl_chg)}, "secondary": sec_res}
print("\nsummary:", json.dumps(summary, ensure_ascii=False))
json.dump({"summary": summary, "rows": out_rows, "sweep": sw_rows, "old_sweep": old_rows, "e4": e4rows, "parity_mismatch": mism},
          open(D + "open333_api0_eval_04.out.json", "w", encoding="utf8"), ensure_ascii=False, indent=1, default=str, sort_keys=True)
print("out sha256:", hashlib.sha256(open(D + "open333_api0_eval_04.out.json", "rb").read()).hexdigest())
