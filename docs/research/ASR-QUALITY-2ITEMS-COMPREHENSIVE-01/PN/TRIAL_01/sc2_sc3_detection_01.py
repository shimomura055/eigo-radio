# -*- coding: utf-8 -*-
"""SC-2(検出recall・層別)/SC-3(精度)。D3(保存X記事19+Z脚本2)とD4(合成16段落)。LLMはcache経由(gpt-6-luna)。
recall は2段で報告: (a)detected = goldのsurfaceが表に載った(grade不問) (b)usable = ruleでeligible tokenを持つgoldのうち declared/confirmed になった割合。
層 needs_table = 出現sentenceで既存 proper_noun_evidence が成立しない(表が実際に必要な層)。"""
import sys, os, json, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common_01 import *
from synthetic_corpus_01 import P
GIP = "--general-in-phrase" in sys.argv
REP = 0
llm = cached_llm(REP)
SPLIT = re.compile(r"(?<!Mrs\.)(?<!Mr\.)(?<!Dr\.)(?<!St\.)(?<![A-Z]\.)(?<=[.!?])\s+")


def sents(text):
    return [s for s in SPLIT.split(text.strip()) if s]


def gold_eligible(g, text, lower_seen):
    """goldエンティティが、ruleでeligible tokenを持つか(表の判定とは独立に再計算)。"""
    ws = ret.words(g["surface"])
    n = 0
    for w in ws:
        if len(w.fold) == 1 and len(ws) >= 2:
            continue
        ok, _ = ret._token_class(w.fold, g["category"], lowercase_seen=lower_seen, cmu_has=pol._default_cmu_has, zipf=pol._default_zipf)
        n += ok
    return n > 0


res = {"d4": [], "d3": {}, "params": {"general_in_phrase": GIP}}
tot = collections.Counter()
bycat = collections.defaultdict(collections.Counter)
lay = collections.Counter()
nongold_grants = []
for para in P:
    segs = [ret.Seg(s) for s in sents(para["text"])]
    tb = ret.build_entity_table(segs, llm=llm, usage_log=USAGE_LOG, tag=para["id"])
    tb.general_in_phrase = GIP
    lower_seen = ret._lowercase_forms([para["text"]])
    gold_toks = set()
    for g in para["gold"]:
        gws = tuple(w.fold for w in ret.words(g["surface"]))
        gold_toks |= set(gws)
        ent = next((e for e in tb.entries if tuple(e.words) == gws), None)
        overl = [e for e in tb.entries if set(e.words) & set(gws)]
        if ent is None and overl:
            ent = next((e for e in overl if e.usable), overl[0])
        elig = gold_eligible(g, para["text"], lower_seen)
        det = ent is not None
        need = set(w.fold for w in ret.words(g["surface"]) if ret._token_class(w.fold, g["category"], lowercase_seen=lower_seen, cmu_has=pol._default_cmu_has, zipf=pol._default_zipf)[0]
                   and not (len(w.fold) == 1))
        cover = set()
        for e in overl:
            if e.usable:
                cover |= set(e.eligible)
        usable = bool(need) and need <= cover
        rec = {"para": para["id"], "surface": g["surface"], "category": g["category"], "expect": g["expect"], "rule_eligible": elig, "detected": det,
               "grade": ent.grade if ent else None, "usable": usable, "table_category": ent.category if ent else None, "notes": ent.notes if ent else None}
        # 出現sentenceごとの層(既存evidence成立有無)
        occ_layers = []
        for s in segs:
            if g["surface"].split()[0].lower() in s.text.lower() or g["surface"].lower() in s.text.lower():
                toks = [w.fold for w in ret.words(g["surface"]) if w.fold not in pol._FUNCTION_WORDS]
                elig_toks = [t for t in toks if ret._token_class(t, g["category"], lowercase_seen=lower_seen, cmu_has=pol._default_cmu_has, zipf=pol._default_zipf)[0]]
                has_det = any(pol.proper_noun_evidence(t, s.text, ledger_surfaces=frozenset(), role="FULL_STORY")[0] for t in elig_toks) if elig_toks else None
                gr, _ = tb.grant_for_phrase(s.text, [w.fold for w in ret.words(g['surface'])]) if (elig_toks and usable) else (frozenset(), None)
                occ_layers.append({"det_evidence": has_det, "table_grant": bool(gr)})
        rec["occurrences"] = occ_layers
        res["d4"].append(rec)
        key = g["category"]
        if elig:
            tot["gold_eligible"] += 1
            bycat[key]["gold_eligible"] += 1
            tot["usable"] += usable
            bycat[key]["usable"] += usable
            for o in occ_layers:
                if o["det_evidence"] is False:
                    lay["needs_table_occ"] += 1
                    lay["needs_table_occ_granted"] += o["table_grant"]
        tot["gold_all"] += 1
        tot["detected"] += det
        bycat[key]["gold_all"] += 1
        bycat[key]["detected"] += det
    # 精度: 表が grant を出すtokenが gold token でなければ誤り(全sentence・全tokenを総当たり)
    for s in segs:
        for w in ret.words(s.text):
            gr, info = tb.grant_for_phrase(s.text, [w.fold])
            if gr and w.fold not in gold_toks:
                nongold_grants.append({"para": para["id"], "token": w.fold, "sentence": s.text[:80], "info": info})
    for ngw in para["neg"]:
        for s in segs:
            gr, _ = tb.grant_for_phrase(s.text, [ngw])
            if gr:
                nongold_grants.append({"para": para["id"], "token": ngw, "sentence": s.text[:80], "why": "neg_word_granted"})
    # 表のusable entryがgoldに無いもの
    for e in tb.entries:
        if e.usable and not any(set(e.words) & set(w.fold for w in ret.words(g["surface"])) for g in para["gold"]):
            nongold_grants.append({"para": para["id"], "entry": e.surface, "why": "usable_entry_not_in_gold"})
res["d4_summary"] = {"overall": dict(tot), "by_category": {k: dict(v) for k, v in bycat.items()}, "layers": dict(lay),
                     "nongold_grants": nongold_grants}
# ---- D3
d3gold = json.load(open(os.path.join(HERE, "d3_gold_01.json"), encoding="utf-8"))
gold_set = {tuple(ret.words(s)[i].fold for i in range(len(ret.words(s)))) for s in d3gold["true_entities"]}
d3_nong, d3_n_usable, d3_total = [], 0, 0
for f in d3_files():
    segs = load_segments(f)
    tb = ret.build_entity_table(segs, llm=llm, usage_log=USAGE_LOG, tag=f)
    tb.general_in_phrase = GIP
    for e in tb.entries:
        d3_total += 1
        if e.usable:
            d3_n_usable += 1
            if tuple(e.words) not in gold_set:
                d3_nong.append({"file": f, "entry": e.surface, "grade": e.grade})
    gtoks = set(t for g in gold_set for t in g)
    for s in segs:
        for w in ret.words(s.text):
            gr, info = tb.grant_for_phrase(s.text, [w.fold])
            if gr and w.fold not in gtoks:
                d3_nong.append({"file": f, "token": w.fold, "sentence": s.text[:80]})
res["d3_summary"] = {"entries": d3_total, "usable": d3_n_usable, "nongold_grants": d3_nong}
json.dump(res, open(os.path.join(HERE, "sc2_sc3_detection_01_result%s.json" % ("_gip" if GIP else "")), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(res["d4_summary"], ensure_ascii=False, indent=1)[:3500])
print(json.dumps(res["d3_summary"], ensure_ascii=False, indent=1)[:1500])
print("spend", ret.spend_so_far(USAGE_LOG))
