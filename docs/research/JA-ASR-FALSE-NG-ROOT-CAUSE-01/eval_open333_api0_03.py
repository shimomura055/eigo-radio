# OPEN-333系(しわ↔すわ)是正案 API 0評価。事前登録=OPEN333_PREREGISTERED_01.md §5(v2)。保存済み転写のみ・LLM/ASR/TTS/ネットワーク呼出0(socket guard)。Production file無変更。
# 母集団: open517_api0_eval_04.out.json rows(1,264=既存771+未知493)+合成負例91(eval_b_light_api0_02.out.json synthetic_negative のPrimary転写)+糊付け型の合成sweep。
# 比較: 現行(07A適用後Production HEAD) vs proto E3P / E4 / E3P4 (proto_open333_fix_03)。出力: open333_api0_eval_03.out.json / 標準出力。
# 再現: PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/eval_open333_api0_03.py
import collections, hashlib, json, sys
sys.path.insert(0, "."); sys.path.insert(0, "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01")
import eval_common_02 as E
import proto_open333_fix_03 as P
import er007_ja_asr_validator_01 as javal
import er011_ja_asr_variant_layer_01 as VL

D = "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/"
javal.FEATURE_FLAG_A2_READING_RESOLVER_ENABLED = False
PASSING = E.uj.PASSING_STATES
NEG_SRC = {"N1", "N3", "SYN"}
POS_SRC = {"POS", "MOON"}
rows_in = json.load(open(D + "open517_api0_eval_04.out.json", encoding="utf8"))["rows"]
items = [(r["src"], r["id"], r["canon"], r["asr"], r["fix_state"]) for r in rows_in]
syn = json.load(open(D + "eval_b_light_api0_02.out.json", encoding="utf8"))["synthetic_negative"]
seen = set()
for i, s in enumerate(syn):
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
    with P.apply_in_process(mode, log=log):
        return E.primary_stage(canon, asr, False)


def probe(canon, asr):
    """現行Productionのclassifyが Candidate E 経由か/どのentryか/糊付け残余は何か。"""
    cn, an = javal.normalize_ja(canon), javal.normalize_ja(asr)
    r = javal.classify_ja_asr_match(canon, asr, allow_reading_resolver=False)
    e = "Candidate E" in (r.reason or "")
    p = javal.protected_check_ja(cn, an)
    return {"cls": r.classification, "e_pass": bool(e and r.should_pass), "num_entry": bool(p.number_mismatches),
            "e1_bad": P.audit_e1(cn, an) if e else None, "e3_bad": P.audit_e3(cn, an) if e else None,
            "diffs": [(d["canonical"], d["asr"]) for d in p.content_diffs]}


out_rows, mism = [], []
for src, ident, canon, asr, stored in items:
    b = run(canon, asr)
    if stored is not None and b["state"] != stored:
        mism.append((ident, b["state"], stored))
    pr = probe(canon, asr)
    row = {"src": src, "id": ident, "canon": canon, "asr": asr, "base_state": b["state"], "base_reason": rs(b["reason"]), "base_label": b["label"], "probe": pr}
    for m in P.MODES:
        r = run(canon, asr, m)
        row[m] = {"state": r["state"], "reason": rs(r["reason"]), "label": r["label"]}
    out_rows.append(row)
E.api0_guard_off()
print(f"items: {len(out_rows)} (既存771+未知493+合成負例Primary重複除去後 {sum(1 for r in out_rows if r['src'] == 'SYN')})")
print(f"[parity] 現行Production HEADの再計算 vs eval_04保存fix_state(07A後proto)の不一致: {len(mism)}")
for x in mism[:10]:
    print("   ", x)


def bp(r):
    return r["base_state"] in PASSING


def np_(r, m):
    return r[m]["state"] in PASSING


def key(r, m=None):
    return (r["base_state"], r["base_reason"], r["base_label"]) if m is None else (r[m]["state"], r[m]["reason"], r[m]["label"])


# ---- 影響範囲の棚卸し: Candidate E経由で現にPASSしている行 ----
epass = [r for r in out_rows if bp(r) and r["probe"]["e_pass"]]
print(f"\n== 棚卸し: 現行PASSのうちCandidate E経由 = {len(epass)} 件 / 現行PASS全体 {sum(1 for r in out_rows if bp(r))} 件 ==")
by = collections.Counter((r["src"], "数値entry" if r["probe"]["num_entry"] else "非数値entry") for r in epass)
for k, v in sorted(by.items()):
    print("  ", k, v)
print("-- Candidate E経由PASS全件 --")
for r in epass:
    pr = r["probe"]
    print(f"  {r['src']:5s} {r['id'][-46:]:46s} | {r['canon'][:30]} | {r['asr'][:30]} | {'NUM' if pr['num_entry'] else 'TXT'} E-diffs={pr['diffs']} e1_bad={pr['e1_bad']} e3_bad={pr['e3_bad']}")


def has_kanji(s):
    return any("一" <= ch <= "鿿" for ch in s)


def kind_of(c, a):
    cv, av = VL._kanji_candidate_reading_variants(c), VL._kanji_candidate_reading_variants(a)
    common = sorted((cv or set()) & (av or set()))
    if not common:
        return "共通読みなし(他spanの偶然に依存/Eが検査せず)"
    if has_kanji(c) and has_kanji(a):
        return "漢字<->漢字(共通読み)"
    if has_kanji(c) != has_kanji(a):
        return "漢字<->かな(読み一致)"
    return "かな<->かな(正規化差)"


kc = collections.Counter()
for r in epass:
    for c, a in r["probe"]["diffs"]:
        kc[kind_of(c, a)] += 1
print("\n== E救済spanの規則種別(のべspan数) ==")
for k, v in kc.most_common():
    print("  ", k, v)
vowel = [(r["id"][-30:], c, a) for r in epass for c, a in r["probe"]["diffs"] if c and a and not has_kanji(c + a) and c != a]
print("かな<->かなspan(母音/子音/濁音/長音の置換になりうる型)の件数:", len(vowel), vowel[:5])


def cls_row(r):
    pr = r["probe"]
    glued_bad = bool(pr["num_entry"] and pr["e1_bad"])
    if r["src"] in NEG_SRC:
        return "誤PASS(既知負例=真の読み違い)"
    if glued_bad:
        return "判定不能(実データ・糊付け残余が未説明。音声未確認)"
    return "正しく救済(正常音声/対照。残余なしまたは説明済み)"


print("\n== 分類(Candidate E経由PASS) ==")
cc = collections.Counter((cls_row(r), "数値entry" if r["probe"]["num_entry"] else "非数値entry") for r in epass)
for k, v in sorted(cc.items()):
    print("  ", k, v)

# ---- 各案の効果 ----
res = {}
for m in P.MODES:
    chg = [r for r in out_rows if key(r) != key(r, m)]
    pass_to_ng = [r for r in chg if bp(r) and not np_(r, m)]
    ng_to_pass = [r for r in out_rows if (not bp(r)) and np_(r, m)]
    other = [r for r in chg if r not in pass_to_ng]
    ctrl_ng = [r for r in pass_to_ng if r["src"] not in NEG_SRC]
    neg_blocked = [r for r in pass_to_ng if r["src"] in NEG_SRC]
    base_neg_pass = [r for r in out_rows if r["src"] in NEG_SRC and bp(r)]
    real_base_pass = [r for r in out_rows if bp(r) and r["src"] not in NEG_SRC]
    res[m] = {"changed": len(chg), "pass_to_ng": len(pass_to_ng), "ng_to_pass": len(ng_to_pass), "other_changed": len(other),
              "non_negative_pass_to_ng": len(ctrl_ng), "neg_pass_blocked": len(neg_blocked), "neg_pass_before": len(base_neg_pass),
              "non_negative_pass_before": len(real_base_pass), "regen_increase_pct_of_non_negative_pass": round(100 * len(ctrl_ng) / max(1, len(real_base_pass)), 3)}
    print(f"\n== {m}: 変化 {len(chg)} (PASS->非PASS {len(pass_to_ng)} / 非PASS->PASS {len(ng_to_pass)} / その他 {len(other)}) ==")
    for r in pass_to_ng:
        print(f"   {r['src']:5s} {r['id'][-46:]:46s} | {r['canon'][:32]} | {r['asr'][:32]} | {r['base_state']} -> {r[m]['state']}/{r[m]['reason']}")
    for r in other:
        print("   OTHER", r["id"], key(r), "->", key(r, m))
    print(" ", json.dumps(res[m], ensure_ascii=False))

# ---- 合成sweep: 糊付け型('しわ'の母音/子音/拗音/長音違い + 数値glue)で止まり方を系統確認 ----
base_c = "月のしわ、8,900本超"
sweep = []
for g in ["し", "す", "そ", "しわ", "すわ", "しゃわ", "しわー", "しば", "すば", "しわわ", "ちわ", "しーわ"]:
    sweep.append(("sw", base_c, f"月の{g}八千九百本長"))
    sweep.append(("sw", base_c, f"月の{g}、八千九百本長"))
sweep += [("sw3", "売上は8,900円です", "売上は八千九百えんです"), ("sw3", "売上は8,900円です", "売上は八千九百円です"),
          ("sw3", "売上は8,900円です", "売上は八千九百ドルです"), ("sw3", "売上は8,900円超です", "売上は八千九百円長です"),
          ("sw3", "売上は8,900円超です", "売上は八千九百円腸です")]
E.api0_guard_on()
sw_rows = []
for tag, c, a in sweep:
    b = run(c, a)
    row = {"tag": tag, "canon": c, "asr": a, "base": b["state"], "label": b["label"]}
    for m in P.MODES:
        row[m] = run(c, a, m)["state"]
    sw_rows.append(row)
E.api0_guard_off()
print("\n== 合成sweep(糊付け型) ==")
sw_pass = [x for x in sw_rows if x["base"] in PASSING]
print(f"  sweep {len(sw_rows)}件、base PASS {len(sw_pass)}件")
for x in sw_rows:
    print(f"   {'PASS ' if x['base'] in PASSING else 'NG   '}{x['tag']} {x['canon']} | {x['asr']} | base={x['base']} E3P={x["E3P"]} E4={x["E4"]} E3P4={x["E3P4"]}")
sw_new_pass = [x for x in sw_rows if x["base"] not in PASSING and any(x[m] in PASSING for m in P.MODES)]
print("  sweep 非PASS->PASS:", len(sw_new_pass))

summary = {"items": len(out_rows), "parity_mismatch": len(mism), "e_pass_rows": len(epass), "per_mode": res, "sweep": len(sw_rows), "sweep_base_pass": len(sw_pass), "sweep_new_pass": len(sw_new_pass)}
print("\nsummary:", json.dumps(summary, ensure_ascii=False))
json.dump({"summary": summary, "rows": out_rows, "sweep": sw_rows, "parity_mismatch": mism}, open(D + "open333_api0_eval_03.out.json", "w", encoding="utf8"),
          ensure_ascii=False, indent=1, default=str, sort_keys=True)
print("out sha256:", hashlib.sha256(open(D + "open333_api0_eval_03.out.json", "rb").read()).hexdigest())
