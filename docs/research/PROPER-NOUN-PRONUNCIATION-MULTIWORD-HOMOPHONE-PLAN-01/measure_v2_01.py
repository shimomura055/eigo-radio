"""PNMH-PLAN-01 委任_02 (API 0・Production無変更・メモリ上source patchのみ): Opusレビュー(R-01/02/03/04/05/07)の
オフライン再計測。出力 measure_v2_result_01.json / triples461_review_list_01.json。
構成(CFG): stress(ストレス込み比較) / rep('all'|'entity'|'always') / g4('single'|'le2'|'zipf5'|'none') / g5(canonical側3字以上)。
設計: 最も緩い構成(permissive)でpairs_02全件を再判定して変化集合Sを得る。他構成は全てpermissiveの部分集合なのでSのみ再判定する。"""
import re, sys, os, json, inspect, itertools, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
os.chdir(ROOT); sys.path.insert(0, ROOT)
HERE = os.path.dirname(os.path.abspath(__file__))
import pronouncing
from wordfreq import zipf_frequency
import er006_preprod_hardening_01_validation as val
import er006_secondary_asr_01 as sec
import er021_en_asr_semantic_equivalence_production_01 as se
se.append_telemetry_log = lambda *a, **k: None   # 副作用なし

MAX_SIDE, MAX_JOINT = 3, 64
# V8: 2字tokenは閉じた機能語集合のみ許可(wordfreq等の新規依存なし)
FW2 = {"us", "on", "to", "in", "of", "by", "at", "it", "is", "as", "or", "an", "my", "me", "he", "we", "be", "do", "go", "up", "so", "no", "if", "am", "ok"}
CFG = {"off": True, "stress": False, "rep": "all", "g4": "single", "g5": True}
_TOK_OK = re.compile(r"^[a-z][a-z']*$")


def _strip(p):
    return re.sub(r"\d", "", p)


def variants(tok, rep, stress):
    ps = pronouncing.phones_for_word(tok)
    if not ps:
        return None
    if rep:
        ps = ps[:1]
    return sorted({tuple((p if stress else _strip(p)).split()) for p in ps})


def joint(tokens, rep, stress):
    vs = []
    for t in tokens:
        v = variants(t, rep, stress)
        if v is None:
            return None
        vs.append(v)
    n = 1
    for v in vs:
        n *= len(v)
    if n > MAX_JOINT:
        return None
    return {tuple(x for part in combo for x in part) for combo in itertools.product(*vs)}


def mw(c, a, entity_like=False, detail=None, cfg=None):
    cfg = cfg or CFG
    d = detail if detail is not None else {}
    c, a = list(c), list(a)
    if cfg.get("off"):
        d["why"] = "off"; return False
    if not c or not a:
        d["why"] = "empty"; return False
    if len(c) == 1 and len(a) == 1:
        d["why"] = "1to1"; return False
    if not (len(c) == 1 or len(a) == 1):
        d["why"] = "both_multi"; return False
    if max(len(c), len(a)) > MAX_SIDE:
        d["why"] = "too_long"; return False
    toks = c + a
    if any(not _TOK_OK.match(t) for t in toks):
        d["why"] = "non_alpha"; return False
    if any(t in val._NEGATION_WORDS or val._is_number(t) for t in toks):
        d["why"] = "num_neg"; return False
    multi = c if len(c) > 1 else a
    g4 = cfg["g4"]
    if g4 != "none":
        for t in multi:
            if (g4 == "single" and len(t) < 2) or (g4 == "le2" and len(t) <= 2) or \
               (g4 == "fw2" and (len(t) < 2 or (len(t) == 2 and t not in FW2))) or \
               (g4 == "zipf5" and (len(t) < 2 or (len(t) == 2 and zipf_frequency(t, "en") < 5.0))):
                d["why"] = "g4"; return False
    if cfg["g5"] and any(len(t) < 3 for t in c):
        d["why"] = "g5"; return False
    rep = cfg["rep"] == "always" or (cfg["rep"] == "entity" and entity_like)
    vc, va = joint(c, rep, cfg["stress"]), joint(a, rep, cfg["stress"])
    if vc is None or va is None:
        d["why"] = "oov_or_many"; return False
    ok = bool(vc & va)
    d["why"] = "equal" if ok else "differs"
    return ok


_src = inspect.getsource(val.protected_check)
_OLD = "                    homophone_candidate = bool(result_h)\n"
_NEW = _OLD + ("                if not homophone_candidate and PROTO_MULTIWORD(canon_span, asr_span, entity_like):\n"
               "                    homophone_candidate = True\n")
assert _OLD in _src
val.__dict__["PROTO_MULTIWORD"] = mw
exec(compile(_src.replace(_OLD, _NEW), "<proto2>", "exec"), val.__dict__)   # CFG['off']=Trueの間は現行と同一挙動


def judge(c, a):
    r = val.classify_asr_match(c, a)
    final = "PASS" if r.should_pass else None
    if final is None and (sec.is_entity_like_mismatch(r) or sec.is_homophone_candidate_mismatch(r)):
        lab = sec._step_alternate_pass(r)
        if lab:
            final = "PASS:" + lab
    return r.classification, (final or "NOT_PASS"), r


def setcfg(**k):
    CFG.clear(); CFG.update({"off": False, "stress": False, "rep": "all", "g4": "single", "g5": True}); CFG.update(k)


def diffs_of(r):
    return [(d["canonical"], d["asr"], d["entity_like"], d["homophone_candidate"]) for d in r.protected.content_word_diffs]


out = {}
# ------------------------------------------------------------ R-05: pairs_02 再適用
pairs = [json.loads(l) for l in open(os.path.join(HERE, "pairs_02.jsonl"), encoding="utf8")]
CFG["off"] = True
before = [judge(p["canonical"], p["asr"])[:2] for p in pairs]
setcfg(g4="none", g5=False)   # permissive
perm = [judge(p["canonical"], p["asr"])[:2] for p in pairs]
S = [i for i in range(len(pairs)) if perm[i] != before[i]]
CONFIGS = {
    "V1_base(ストレス無視,全variant,G4=1字,G5)": dict(),
    "V2_stress込み": dict(stress=True),
    "V3_entity_likeのみ代表variant限定": dict(rep="entity"),
    "V4_常に代表variant限定": dict(rep="always"),
    "V5_G4を2字以下に強化": dict(g4="le2"),
    "V6_G4:2字tokenはzipf>=5.0のみ": dict(g4="zipf5"),
    "V7_stress込み+entity代表限定": dict(stress=True, rep="entity"),
    "V8_G4:2字tokenは機能語集合のみ": dict(g4="fw2"),
}
res_pairs = {}
for name, kw in CONFIGS.items():
    setcfg(**kw)
    ch = []
    for i in S:
        a = judge(pairs[i]["canonical"], pairs[i]["asr"])[:2]
        if a != before[i]:
            ch.append({"idx": i, "canonical": pairs[i]["canonical"][:90], "asr": pairs[i]["asr"][:90], "before": before[i], "after": a,
                       "origins": pairs[i]["origins"], "src": pairs[i]["sources"][0][:100]})
    res_pairs[name] = {"n_changed": len(ch),
                       "pass_to_ng": sum(1 for c in ch if c["before"][1] != "NOT_PASS" and c["after"][1] == "NOT_PASS"),
                       "ng_to_pass": sum(1 for c in ch if c["before"][1] == "NOT_PASS" and c["after"][1] != "NOT_PASS"),
                       "items": ch if name.startswith("V1") else [(c["idx"], c["before"][1], c["after"][1]) for c in ch]}
cnt = collections.Counter()
for i in S:
    for o in pairs[i]["origins"]:
        cnt[o] += 1
out["R05_pairs02_replay"] = {
    "n_pairs": len(pairs), "origin_totals": dict(collections.Counter(o for p in pairs for o in p["origins"])),
    "permissive_n_changed": len(S), "permissive_changed_by_origin": dict(cnt),
    "permissive_changed_list": [{"idx": i, "c": pairs[i]["canonical"][:70], "a": pairs[i]["asr"][:70], "b": perm[i], "origins": pairs[i]["origins"]} for i in S][:30],
    "configs": res_pairs}

# ------------------------------------------------------------ R-01/R-03/R-07: 461組
vocab = set()
VOCAB01 = os.environ.get("VOCAB01") == "1"   # 1: 委任_01と同じ語彙(pairs_01のcanonicalのみ)で461組を再現
SUF = "_vocab01" if VOCAB01 else ""
for p in (pairs if not VOCAB01 else [q for q in pairs if "pairs_01" in q["origins"]]):
    for t in val.tokenize(p["canonical"]):
        if re.fullmatch(r"[a-z']{2,}", t):
            vocab.add(t)
vocab = sorted(w for w in vocab if pronouncing.phones_for_word(w))


def ph(w):
    return pronouncing.phones_for_word(w)


def nos(p):
    return tuple(_strip(p).split())


def sts(p):
    return tuple(p.split())


byseq = collections.defaultdict(set)
for w in vocab:
    for p in ph(w):
        byseq[nos(p)].add(w)
trip = {}
for w1 in vocab:
    for w2 in vocab:
        if len(w1) < 2 or len(w2) < 2:
            continue
        for p1 in ph(w1):
            for p2 in ph(w2):
                for X in byseq.get(nos(p1) + nos(p2), ()):
                    if len(X) >= 3 and X != w1 + w2 and X not in (w1, w2):
                        t = trip.setdefault((X, w1, w2), {"stress_exact_any": False, "rep_X_any_w": False, "rep_w_any_X": False, "rep_all": False})
                        if sts(p1) + sts(p2) in {sts(q) for q in ph(X)}:
                            t["stress_exact_any"] = True
                        repX = nos(ph(X)[0])
                        repw = nos(ph(w1)[0]) + nos(ph(w2)[0])
                        if nos(p1) + nos(p2) == repX:
                            t["rep_X_any_w"] = True
                        if repw in {nos(q) for q in ph(X)}:
                            t["rep_w_any_X"] = True
                        if repw == repX:
                            t["rep_all"] = True
n = len(trip)
sw = val._STOPWORDS
rows = []
for (X, w1, w2), t in sorted(trip.items()):
    rows.append({"X": X, "w1": w1, "w2": w2, "stress_exact": t["stress_exact_any"], "rep_all": t["rep_all"], "rep_X_any_w": t["rep_X_any_w"],
                 "rep_w_any_X": t["rep_w_any_X"], "stopword_in_pair": (w1 in sw or w2 in sw),
                 "only_nonrep": not (t["rep_all"] or t["rep_X_any_w"] or t["rep_w_any_X"]), "stress_removed_only": not t["stress_exact_any"]})


def guard_counts(**kw):
    setcfg(**kw)
    return {"canonX_asr_multi": sum(1 for (X, w1, w2) in trip if mw([X], [w1, w2])),
            "canonMulti_asrX": sum(1 for (X, w1, w2) in trip if mw([w1, w2], [X]))}


res461 = {"n_triples": n,
          "stress_exact": sum(1 for r in rows if r["stress_exact"]),
          "stress_removed_only": sum(1 for r in rows if r["stress_removed_only"]),
          "rep_all(X代表=w1代表+w2代表)": sum(1 for r in rows if r["rep_all"]),
          "rep_X_any_w": sum(1 for r in rows if r["rep_X_any_w"]),
          "rep_w_any_X": sum(1 for r in rows if r["rep_w_any_X"]),
          "only_nonrep(代表以外のvariantでのみ一致)": sum(1 for r in rows if r["only_nonrep"]),
          "stopword_pair": sum(1 for r in rows if r["stopword_in_pair"]),
          "stopword_pair_and_only_nonrep": sum(1 for r in rows if r["stopword_in_pair"] and r["only_nonrep"]),
          "stress_exact_and_rep_all": sum(1 for r in rows if r["stress_exact"] and r["rep_all"]),
          "stress_removed_only_and_only_nonrep": sum(1 for r in rows if r["stress_removed_only"] and r["only_nonrep"])}
res461["guarded"] = {name: guard_counts(**kw) for name, kw in CONFIGS.items()}
res461["permissive(ガード無)"] = guard_counts(g4="none", g5=False)
out["R01_R03_R07_triples461"] = res461
json.dump(rows, open(os.path.join(HERE, "triples_review_list_01%s.json" % SUF), "w", encoding="utf8", newline="\n"), ensure_ascii=False, indent=0)

# ------------------------------------------------------------ R-02: Bi-us対策案の副作用
cases_bi = [("bias", "bi us"), ("bias", "by us"), ("byus", "bi us"), ("byus", "buy us"), ("byus", "by us"), ("onto", "on to"),
            ("already", "all ready"), ("melos", "mellow s")]
bi = {}
for name, kw in CONFIGS.items():
    setcfg(**kw)
    bi[name] = {f"{x}->{y}": mw(x.split(), y.split()) for x, y in cases_bi}
out["R02_bius_countermeasures_span_level"] = bi
S1, S2 = "The service is called bias now.", "The service is called Bi-us now."
CFG["off"] = True
out["R02_bius_sentence_current_code"] = judge(S1, S2)[:2]
for nm, kw in (("V1", {}), ("V5", dict(g4="le2")), ("V6", dict(g4="zipf5")), ("V8", dict(g4="fw2"))):
    setcfg(**kw)
    out[f"R02_bius_sentence_after_{nm}"] = judge(S1, S2)[:2]
out["R02_tokenize_Bi-us"] = val.tokenize("Bi-us")

# ------------------------------------------------------------ R-03: Tse->sea(既存の穴、現行コード)
CFG["off"] = True
tse = {}
for c_, a_ in [("Kristie Tse spoke first.", "Kristie Sea spoke first."), ("Tse spoke first.", "Sea spoke first."),
               ("Tse spoke first.", "See spoke first."), ("Tse spoke first.", "C spoke first."), ("Kristie spoke first.", "Christie spoke first.")]:
    r = judge(c_, a_)
    tse[f"{c_} -> {a_}"] = {"cls": r[0], "final": r[1], "diffs": diffs_of(r[2])}
out["R03_tse_sea_current_code"] = tse
cap = collections.Counter()
for p in pairs:
    for m in re.finditer(r"(?<=[a-z,;] )([A-Z][a-z']{2,})\b", p["canonical"]):
        cap[m.group(1).lower()] += 1
hole = []
for w, nw in cap.items():
    ps = ph(w)
    if not ps or len(ps) < 2:
        continue
    rep = nos(ps[0])
    for q in ps[1:]:
        if nos(q) == rep:
            continue
        for y in byseq.get(nos(q), ()):
            if y != w and rep not in {nos(z) for z in ph(y)}:
                hole.append((w, y, nw))
hole = sorted(set(hole))
out["R03_entity_hole_scan"] = {"n_midsentence_capitalized_words": len(cap), "n_in_cmu_with_multi_variant": sum(1 for w in cap if len(ph(w)) >= 2),
                               "n_hole_pairs(canonical大文字語の非代表variantでのみ同音になる語)": len(hole),
                               "n_distinct_canonical_words_in_holes": len({h[0] for h in hole}), "examples": hole[:40]}

# ------------------------------------------------------------ R-04 (a)-(d)
cases_r4 = {
    "a_number_exception": ("byUs has two apps.", "Buy us has to apps."),
    "a_number_exception_control_1to1": ("Bias has two apps.", "Buys has to apps."),
    "a_number_exception_control_1to1_homophone": ("Bias has two apps.", "Byus has to apps."),
    "c_connected_speech_mix": ("Please check this stuff with byUs now.", "Please check this tough with buy us now."),
    "c_other_content_diff_mix": ("Walk uphill slowly with byUs.", "Walk a pill slowly with buy us."),
    "c_proper_noun_diff_mix": ("Melos met byUs today.", "Mellow s met buy us today."),
    "d_f1_residual": ("He said the byUs team won the match.", "He said the buy us team won the match."),
    "base_positive": ("The service is called byUs now.", "The service is called buy us now."),
}
r4 = {}
for k, (c_, a_) in cases_r4.items():
    CFG["off"] = True
    b_ = judge(c_, a_)
    setcfg()
    a2 = judge(c_, a_)
    r4[k] = {"canonical": c_, "asr": a_, "before": (b_[0], b_[1]), "after": (a2[0], a2[1]), "diffs_after": diffs_of(a2[2])}
out["R04_behavior_change_points"] = r4
CFG["off"] = True
cb = val.classify_asr_match("Melos met byUs today.", "Melos met buy us today.")
setcfg()
ca = val.classify_asr_match("Melos met byUs today.", "Melos met buy us today.")
out["R04_b_m1_secondary_contradiction_input"] = {"secondary_text": "Melos met buy us today.", "before": cb.classification, "after": ca.classification}
CFG["off"] = True
json.dump(out, open(os.path.join(HERE, "measure_v2_result_01%s.json" % SUF), "w", encoding="utf8", newline="\n"), ensure_ascii=False, indent=1, default=str)
print(json.dumps({k: v for k, v in out.items() if k != "R05_pairs02_replay"}, ensure_ascii=False, indent=1, default=str)[:14000])
print(json.dumps(out["R05_pairs02_replay"], ensure_ascii=False, indent=1, default=str)[:6000])
