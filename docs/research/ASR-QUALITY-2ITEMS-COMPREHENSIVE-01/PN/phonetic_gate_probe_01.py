# -*- coding: utf-8 -*-
"""設計入力(API 0): entity_table由来evidenceに追加する「音素近接ゲート」の分離能を、保存済みの受理済み差分(正例=承認方針の中心例)と
合成の負例(別語への聞き違い)で測る。特徴量付き編集距離(ARPAbet)。語はCMU辞書→無ければg2p_en。"""
import sys, json, itertools
sys.path.insert(0, ".")
import pronouncing
try:
    from g2p_en import G2p
    _g2p = G2p()
except Exception as e:  # noqa
    _g2p = None
VOWELS = set("AA AE AH AO AW AY EH ER EY IH IY OW OY UH UW".split())
VOICE = {"P": "B", "T": "D", "K": "G", "F": "V", "S": "Z", "SH": "ZH", "CH": "JH", "TH": "DH"}
VOICE.update({v: k for k, v in list(VOICE.items())})
PLACE = {"P": "lab", "B": "lab", "M": "lab", "F": "labdent", "V": "labdent", "TH": "dent", "DH": "dent", "T": "alv", "D": "alv", "S": "alv", "Z": "alv", "N": "alv", "L": "alv", "R": "alv",
         "SH": "post", "ZH": "post", "CH": "post", "JH": "post", "K": "vel", "G": "vel", "NG": "vel", "HH": "glot", "Y": "pal", "W": "lab"}
def strip(p): return "".join(c for c in p if not c.isdigit())
def phones(word):
    w = word.lower().strip("'")
    ps = pronouncing.phones_for_word(w)
    if ps: return [strip(p) for p in ps[0].split()], "cmu"
    if _g2p is not None:
        return [strip(p) for p in _g2p(w) if p.strip() and p[0].isalpha()], "g2p"
    return None, "none"
def sub(a, b):
    if a == b: return 0.0
    va, vb = a in VOWELS, b in VOWELS
    if va and vb: return 0.4 if a in ("AH", "IH", "ER") or b in ("AH", "IH", "ER") else 0.5
    if va != vb: return 1.0
    if VOICE.get(a) == b: return 0.25 if {a, b} == {"T", "D"} else 0.3   # 有声/無声のみ差(T/Dは米語フラップで実質同音になりうる)
    if PLACE.get(a) == PLACE.get(b) and a in "MN" or b in "MN" and PLACE.get(a) == PLACE.get(b): return 0.4
    return 0.8
def dist(x, y):
    n, m = len(x), len(y)
    D = [[0.0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1): D[i][0] = D[i - 1][0] + (0.6 if x[i - 1] in VOWELS else 1.0)
    for j in range(1, m + 1): D[0][j] = D[0][j - 1] + (0.6 if y[j - 1] in VOWELS else 1.0)
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            D[i][j] = min(D[i - 1][j] + (0.6 if x[i - 1] in VOWELS else 1.0), D[i][j - 1] + (0.6 if y[j - 1] in VOWELS else 1.0), D[i - 1][j - 1] + sub(x[i - 1], y[j - 1]))
    return D[n][m] / max(n, m, 1)
def span_dist(c, a):
    pc, pa = [], []
    for w in c.split(): 
        p, _ = phones(w)
        if p is None: return None
        pc += p
    for w in a.split():
        p, _ = phones(w)
        if p is None: return None
        pa += p
    return round(dist(pc, pa), 3)
if __name__ == "__main__":
    q = json.load(open("docs/research/ASR-QUALITY-2ITEMS-COMPREHENSIVE-01/PN/quant_hr_queue_01_result.json", encoding="utf-8"))
    pos = []
    for o in q:
        if o["contaminated"] or "skip" in o or not o["accept"]: continue
        for c, a, s in o["diffs"]:
            d = span_dist(c, a); pos.append((d, c, a))
    pos = sorted({(d, c, a) for d, c, a in pos if d is not None})
    print("POS n=%d (承認方針の受理済み差分, canonical->ASR Primary)" % len(pos))
    for d, c, a in pos: print("  %.3f %s -> %s" % (d, c, a))
    extra = [("bertie", "birdie")]
    print("TARGET", [(c, a, span_dist(c, a)) for c, a in extra])
    neg = [("bertie", "party"), ("bertie", "berry"), ("vera", "very"), ("vera", "bear"), ("framton", "farm"), ("meta", "metal"), ("reuters", "writers"), ("brent", "brand"),
           ("hormuz", "horses"), ("mark", "mike"), ("rose", "ross"), ("elle", "ally"), ("vogue", "vote"), ("nuttel", "nothing"), ("kristie", "kitchen"), ("hanshin", "handshake"),
           ("toteme", "tomato"), ("altuzarra", "alter"), ("bisnow", "business"), ("iran", "iron"), ("chanel", "channel")]
    print("NEG synthetic (別語への聞き違い):")
    for c, a in neg: print("  %.3f %s -> %s" % (span_dist(c, a), c, a))
