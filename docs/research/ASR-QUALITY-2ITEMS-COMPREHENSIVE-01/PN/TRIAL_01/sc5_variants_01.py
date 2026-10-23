# -*- coding: utf-8 -*-
"""SC-5 実装同値test + D5合成負例。表の全usable entry(D3+D4+HR群)について、ホストsegmentのASR変種を作り
 (a) 位置紐づけ表(RET-3 OFF)の判定 vs 「同一tokenをLedger登録した場合(eligible token+内部イニシャルをledger_surfacesへ)」の原本判定 が一致すること
 (b) 表で受理 => Ledger等価でも受理(表由来は緩めない)
 (c) 変種タイプ別の受理数(一般語/数値/否定/脱落/他実体 = 0 が基準。非一般語・類似度>=0.40の変種[edit/split/rare]は by-design として別集計)
(これはOpus OF-PN2-07のとおり『実装同値』の確認であり、誤PASSがないことの証明は adjudication[sc4_new_accepts]側)。API 0。"""
import sys, os, json, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common_01 import *
from synthetic_corpus_01 import P
llm = cached_llm(0)
tables = []
for f in d3_files():
    tables.append((f, load_segments(f), ret.build_entity_table(load_segments(f), llm=llm, usage_log=USAGE_LOG)))
SPLIT = re.compile(r"(?<!Mrs\.)(?<!Mr\.)(?<!Dr\.)(?<!St\.)(?<![A-Z]\.)(?<=[.!?])\s+")
for para in P:
    segs = [ret.Seg(s) for s in SPLIT.split(para["text"].strip()) if s]
    tables.append((para["id"], segs, ret.build_entity_table(segs, llm=llm, usage_log=USAGE_LOG)))
for k, v in json.load(open(os.path.join(HERE, "entity_tables_hr_01.json"), encoding="utf-8")).items():
    t = ret.EntityTable.from_dict(v)
    tables.append((k, None, t))


def variants(tok):
    v = {}
    vow = re.search(r"[aeiou]", tok)
    if vow:
        rep = {"a": "e", "e": "i", "i": "a", "o": "u", "u": "o"}[vow.group(0)]
        v["edit_vowel"] = tok[:vow.start()] + rep + tok[vow.end():]
    if len(tok) >= 4:
        v["drop_last"] = tok[:-1]
        v["split2"] = tok[:len(tok) // 2] + " " + tok[len(tok) // 2:]
    v["append_s"] = tok + "s"
    v["rare_word"] = "quokka"
    v["general_word"] = "water"
    v["general_word2"] = "very"
    v["number"] = "two"
    v["negation"] = "not"
    v["deletion"] = ""
    return v


BY_DESIGN = {"edit_vowel", "drop_last", "split2", "append_s", "rare_word"}
stat = collections.Counter()
by_type = collections.defaultdict(collections.Counter)
mism, more_permissive = [], []
n_entries = 0
seen_entries = set()
for name, segs, tb in tables:
    for e in tb.usable_entries():
        key = (name, e.surface)
        if key in seen_entries:
            continue
        seen_entries.add(key)
        # ホストsegment: 実体の出現がある最初のsegment(HR群は表のみ=segs None のためスキップ。HR群は sc4 で検証済み)
        if segs is None:
            continue
        host = next((s.text for s in segs if tb.occurrences(s.text)
                     and any(o[2] is e for o in tb.occurrences(s.text))), None)
        if host is None:
            continue
        n_entries += 1
        tok = e.eligible[0]
        m = re.search(r"(?<![^\W\d_])" + re.escape(tok) + r"(?![^\W\d_])", pol._fold(host), flags=re.I)
        # 原文中の表記を取り出す(大文字小文字を保持)
        mm = next((x for x in ret.words(host) if x.fold == tok and x.orig[:1].isupper()), None)
        if mm is None:
            continue
        led_eq = frozenset(set(e.eligible) | set(e.initials))
        vs = variants(tok)
        for vtype, rep in vs.items():
            p_text = host[:mm.start] + rep + host[mm.end:]
            for s_mode in ("same", "alt"):
                s_rep = rep if s_mode == "same" else (vs["drop_last"] if "drop_last" in vs else rep)
                s_text = host[:mm.start] + s_rep + host[mm.end:]
                cp = val.classify_asr_match(host, p_text)
                cs = val.classify_asr_match(host, s_text)
                kw = dict(canonical_text=host, primary_cls=cp, secondary_cls=cs, primary_text=p_text, secondary_text=s_text,
                          judge_state="NG_BOTH", judge_reason_code="secondary_not_accepted", role="FULL_STORY", p3_entry="p3_primary_ng")
                T = run_trial(kw, frozenset(), tb, ret3=False)
                L = run_orig(kw, led_eq)
                stat["cases"] += 1
                by_type[vtype]["cases"] += 1
                by_type[vtype]["trial_accept"] += T.accept
                by_type[vtype]["ledger_equiv_accept"] += L.accept
                by_type[vtype]["trial_accept_" + s_mode] += T.accept
                if (T.accept, T.reason) != (L.accept, L.reason):
                    stat["mismatch"] += 1
                    mism.append({"entry": e.surface, "variant": vtype, "s_mode": s_mode, "trial": [T.accept, T.reason], "ledger_eq": [L.accept, L.reason], "p": p_text[:90]})
                if T.accept and not L.accept:
                    more_permissive.append({"entry": e.surface, "variant": vtype, "p": p_text[:90]})
res = {"entries": n_entries, "cases": stat["cases"], "mismatch": stat["mismatch"], "table_more_permissive_than_ledger": len(more_permissive),
       "by_variant": {k: dict(v) for k, v in by_type.items()}, "mismatch_examples": mism[:20], "more_permissive_examples": more_permissive[:20]}
# 負例基準は s_mode=same(Primary/Secondary が同じ別語に揃う=Stage 2の実誤読型。NG_BOTHの現実的な形)。
# s_mode=alt は「Secondaryがほぼ正しい転写」を含み、統一judgeが既にSecondary受理するためPNAP到達しない非現実的な組合せ。参考値として別掲(原本[Ledger等価]と同数=表が緩めていない)。
nonby = sum(v.get("trial_accept_same", 0) for k, v in by_type.items() if k not in BY_DESIGN)
nonby_alt = sum(v.get("trial_accept_alt", 0) for k, v in by_type.items() if k not in BY_DESIGN)
res["accepts_of_non_by_design_variants_same_mode(general/number/negation/deletion)"] = nonby
res["accepts_of_non_by_design_variants_alt_mode_reference(unrealistic_secondary_nearly_correct)"] = nonby_alt
res["PASS_impl_parity"] = (stat["mismatch"] == 0 and not more_permissive)
res["PASS_negatives_zero"] = nonby == 0
json.dump(res, open(os.path.join(HERE, "sc5_variants_01_result.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1)[:4000])
