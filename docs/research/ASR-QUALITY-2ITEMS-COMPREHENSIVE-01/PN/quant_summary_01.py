# -*- coding: utf-8 -*-
"""quant_hr_queue_01_result.json(88 real events)を原因クラス×固有名詞カテゴリで集計(API 0)。カテゴリは語の手動ラベル(下表。判断の透明化のため固定)。"""
import json, collections
d = json.load(open("docs/research/ASR-QUALITY-2ITEMS-COMPREHENSIVE-01/PN/quant_hr_queue_01_result.json", encoding="utf-8"))
CAT = {"bisnow": "organization(media)", "mimoun": "person", "l mimoun": "person", "gruen": "person", "kristie": "person", "kristie tse": "person",
       "stephen reicher": "person", "ganis": "person", "zabelina": "person", "lindberg": "person", "meink": "brand_product", "toteme": "brand_product",
       "altuzarra": "brand_product", "kallmeyer": "person", "khaite": "brand_product", "canele": "brand_product(food)", "melos": "person(fiction)",
       "muse": "brand_product", "minaudiere": "brand_product(term)", "bertie": "person(fiction)", "mini": "general_word"}
def cat_of(o):
    names = [c for c, a, b in o["pd"]] if o["pd"] else []
    cs = {CAT.get(n) for n in names if n in CAT}
    return sorted(c for c in cs if c) or ["-"]
real = [o for o in d if not o["contaminated"] and "skip" not in o]
def klass(o, key_acc="accept", key_rsn="reason"):
    if o[key_acc]: return "A_accepted"
    r = o[key_rsn]
    if r == "NO_PROPER_NOUN_EVIDENCE": return "B_no_evidence"
    if r == "SECONDARY_NOT_ENTITY_ONLY": return "C_secondary_span_merge"
    if r in ("ASR_SIDES_ALL_GENERAL_WORDS", "CANONICAL_TOKEN_IS_GENERAL_WORD"): return "D_general_word_block"
    if r in ("SECONDARY_ONLY_NOISE_LIMIT",): return "C2_secondary_noise"
    return "E_non_entity_cause(" + r + ")"
for label, ka, kr in (("CURRENT_LEDGER(registered状態で再評価)", "accept", "reason"), ("EMPTY_LEDGER(初見語=Ledger未登録を再現)", "accept_noledger", "reason_noledger")):
    print("==", label)
    c = collections.Counter(klass(o, ka, kr) for o in real)
    for k, v in sorted(c.items()): print("  ", k, v)
    print("   entity-only candidate pool (A+B+C+C2+D) =", sum(v for k, v in c.items() if k[0] in "ABCD"))
    bycat = collections.defaultdict(collections.Counter)
    for o in real:
        k = klass(o, ka, kr)
        if k[0] in "ABCD":
            for ct in cat_of(o): bycat[ct][k] += 1
    for ct, cc in sorted(bycat.items()): print("   cat", ct, dict(cc))
print("== C(secondary span merge) detail")
for o in real:
    if o["reason"] == "SECONDARY_NOT_ENTITY_ONLY": print("  ", o["i"], o["detail"].get("canonical"), "->", o["detail"].get("asr_secondary"))
