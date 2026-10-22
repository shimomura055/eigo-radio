# -*- coding: utf-8 -*-
"""第2巡 判定arm群(Trial専用。Production判定・正式Ledger・Validatorを変更/importしない)。
R1_V4/R1_EXT=第1巡のarm(基準)。N1..N6=Opus Step B 案1の新arm(累積)。
 N1_DEGEM : 語境界の同一子音の縮約を許容(S2R-03)
 N2_WEAK  : +弱化母音の同一視(ASR側が無強勢の母音とcandidateの弱化母音クラス同士)(S2R-04a)
 N3_SUP2  : +2出所以上の支持(弱化母音同一視下)で受理集合を拡張。取得根拠(tierA/媒体合意)があれば推定は捨てる(S2R-04b)
 N4_ASRG2P: +ASR側CMU未収録語へG2P+アクセント記号正規化(S2R-05)
 N5_UND   : +母音1つ差の不一致は(独立2エンジン以上が同一綴りを返さない限り)NGでなく判定不能(S2R-07)
 N6_W2    : +ローカルWhisper small/mediumが共にMISMATCHでなく少なくとも1つMATCH(Production外の追加エンジン。比較用)
LLMのofficial自己申告はどの関数も読まない(S2R-08)。Primaryの正しい綴り(EXACT)は単独でPASS根拠に数えない(S2R-06: PASSには音素照合MATCHが少なくとも1つ必要)。"""
import itertools, os, re, sys, unicodedata
sys.path.insert(0, os.getcwd())
import er100_pnps_stage2_trial_01_replay as RP
from er100_pnps_stage2_trial_01_common import norm_tokens

VOWELS = {"AA", "AE", "AH", "AO", "AW", "AY", "EH", "ER", "EY", "IH", "IY", "OW", "OY", "UH", "UW"}
WEAK = {"AH", "IH", "UH", "ER", "OW", "AA"}   # 無強勢位置で弱化し得る母音(ASR側が無強勢のときのみ有効)
ARMS = ["R1_V4", "R1_EXT", "N1_DEGEM", "N2_WEAK", "N3_SUP2", "N4_ASRG2P", "N5_UND", "N6_W2"]
OPTS = {
    "R1_V4": {}, "R1_EXT": {},
    "N1_DEGEM": {"degem": 1},
    "N2_WEAK": {"degem": 1, "weak": 1},
    "N3_SUP2": {"degem": 1, "weak": 1, "sup2": 1},
    "N4_ASRG2P": {"degem": 1, "weak": 1, "sup2": 1, "asrg2p": 1},
    "N5_UND": {"degem": 1, "weak": 1, "sup2": 1, "asrg2p": 1, "und": 1},
    "N6_W2": {"degem": 1, "weak": 1, "sup2": 1, "asrg2p": 1, "und": 1, "w2": 1},
}
_G2P = []
_CMU = {}


def strip_accents(t):
    return "".join(c for c in unicodedata.normalize("NFKD", t) if not unicodedata.combining(c))


def norm2(text):
    return norm_tokens(strip_accents(text or ""))


def g2p_tok(tok):
    from g2p_en import G2p
    if not _G2P:
        _G2P.append(G2p())
    ph = [p for p in _G2P[0](tok) if re.match(r"[A-Z]+\d?$", p)]
    return tuple(ph) if ph else None


def cmu_with_stress(tok):
    import pronouncing
    k = tok.lower().strip("'")
    if k not in _CMU:
        _CMU[k] = [tuple(x.split()) for x in pronouncing.phones_for_word(k)]
    return _CMU[k]


def variants(toks, asrg2p, cap=64):
    """ASR側token列→音素列(stress付き)の異読集合。未収録でG2P不使用ならNone(OOV)。"""
    vs = []
    for t in toks:
        c = cmu_with_stress(t)
        if not c:
            if not asrg2p:
                return None
            if len(t) < 4 or not re.search(r"[aeiouy]", t):   # 短い/母音字なしの断片(kt等)はG2Pが捏造するため対象外(判定不能のまま)
                return None
            g = g2p_tok(strip_accents(t))
            if not g:
                return None
            c = [g]
        vs.append(c)
    n = 1
    for v in vs:
        n *= len(v)
    if n > cap:
        return None
    return {tuple(x for part in combo for x in part) for combo in itertools.product(*vs)}


def _bare(p):
    return re.sub(r"\d", "", p)


def eq_phone(a, c, weak):
    """a=ASR側(stress付き), c=candidate(stress無し)。"""
    ab = _bare(a)
    if ab == c:
        return True
    return bool(weak and ab in WEAK and c in WEAK and not a.endswith(("1", "2")))


def seq_eq(asr, cand, weak):
    return len(asr) == len(cand) and all(eq_phone(a, c, weak) for a, c in zip(asr, cand))


def near_vowel(asr, cand):
    """子音が全て一致し母音がちょうど1つだけ異なる。"""
    if len(asr) != len(cand):
        return False
    diff = 0
    for a, c in zip(asr, cand):
        ab = _bare(a)
        if ab == c:
            continue
        if ab in VOWELS and c in VOWELS:
            diff += 1
        else:
            return False
    return diff == 1


def cand_variants(cand, nextfirst, degem):
    out = [tuple(cand)]
    if degem and nextfirst and cand and cand[-1] == nextfirst and cand[-1] not in VOWELS and len(cand) > 2:
        out.append(tuple(cand[:-1]))   # 語境界の同一子音は1つに縮約される
    return out


def obs_label(word, toks, accset, nextfirst, o):
    """-> (label, detail)。label: EXACT/MATCH/NEAR_VOWEL/MISMATCH/OOV/UNALIGNED"""
    if toks is None:
        return "UNALIGNED", ""
    toks = list(norm2(" ".join(toks))) if o.get("asrg2p") else list(toks)
    if len(toks) == 1 and toks[0] == word:
        return "EXACT", word
    vs = variants(toks, o.get("asrg2p"))
    if vs is None:
        return "OOV", " ".join(toks)
    weak = o.get("weak")
    near = False
    for c in accset:
        for cv in cand_variants(c, nextfirst, o.get("degem")):
            for a in vs:
                if seq_eq(a, cv, weak):
                    return "MATCH", " ".join(toks)
                if near_vowel(a, cv):
                    near = True
    return ("NEAR_VOWEL" if near else "MISMATCH"), " ".join(toks)


def nextfirst_of(canon, word):
    toks = norm2(canon)
    if word in toks:
        i = toks.index(word)
        if i + 1 < len(toks):
            c = cmu_with_stress(toks[i + 1])
            if c:
                return _bare(c[0][0])
    return None


def build_arm_sets(W, S, A, nbest):
    """W=語, S=RP.build_sets()[W], A=RP.accepted()[W]。official自己申告は読まない。"""
    ident = RP.IDENTITY[W][0]
    nb = {tuple(c["arpa"]) for c in ((nbest or {}).get(W, {}).get("candidates") or []) if c.get("arpa")}
    srcs = {"E2": set(S["E2"]), "E3": set(S["E3"]) | nb}
    ret = {x["arpa"] for x in S["retrieved"]} if ident != "NOT_CONFIRMED_SAME_ENTITY" else set()
    cands = srcs["E2"] | srcs["E3"] | ret

    def sup(c):
        n = 0
        for s in (srcs["E2"], srcs["E3"], ret):
            if any(seq_eq(tuple(x), c, True) or seq_eq(tuple(c), x, True) for x in s):
                n += 1
        return n
    sup2 = {c for c in cands if sup(c) >= 2}
    auth = A["tierA"] | A["media_consensus"]
    n3 = auth if auth else (set(A["V4"]) | A["single_plus_est"] | sup2)
    return {"R1_V4": A["V4"], "R1_EXT": A["EXT"], "n3": n3, "sup2": sup2,
            "sources": {k: sorted(" ".join(a) for a in v) for k, v in srcs.items()}, "retrieved": sorted(" ".join(a) for a in ret)}


def judge(word, canon, obs, armsets, arm):
    """obs: engine key -> token list|None。primary*/secondary*/azure=Production系、whisper_*=ローカル(同一世代のみ)。whisperREF_*は使わない。"""
    o = OPTS[arm]
    acc = armsets["R1_V4"] if arm == "R1_V4" else armsets["R1_EXT"] if arm == "R1_EXT" else armsets["n3"]
    nf = nextfirst_of(canon, word)
    prod, wh = [], []
    for k, v in obs.items():
        if v is None or k.startswith("whisperREF"):
            continue
        lab, det = obs_label(word, v, acc, nf, o)
        if lab == "NEAR_VOWEL" and not o.get("und"):
            lab = "MISMATCH"
        (wh if k.startswith("whisper") else prod).append((k, lab, det, tuple(v)))
    npl = [l for _, l, _, _ in prod]
    if not acc:
        return {"verdict": "HR_MAINTAINED(推定不成立)", "prod": prod, "wh": wh}
    if npl and all(l in ("MATCH", "EXACT") for l in npl) and "MATCH" in npl:
        v = "PASS_WITH_WARNING"
        if o.get("w2"):
            wl = [l for _, l, _, _ in wh]
            if not wl or any(l not in ("MATCH", "EXACT") for l in wl) or "MATCH" not in wl:
                v = "HR_MAINTAINED(Whisper不一致/未観測)"
    elif "MISMATCH" in npl and "OOV" not in npl:
        v = "NG"
    elif o.get("und") and "NEAR_VOWEL" in npl and "OOV" not in npl:
        seqs = [s for _, l, _, s in prod + wh if l == "NEAR_VOWEL"]
        v = "NG" if len(seqs) >= 2 and len(set(seqs)) == 1 else "HR_MAINTAINED(判定不能: 母音1つ差のみでエンジン間不一致)"
    else:
        v = "HR_MAINTAINED(判定不能)"
    return {"verdict": v, "prod": prod, "wh": wh}


def prod_pass_proxy(word, obs):
    """現行Production判定の再現プロキシ: PrimaryまたはAzure(cascade)が対象語を正しい綴りで返せば通る。実判定ではない(限界として開示)。"""
    for k, v in obs.items():
        if v is None or k.startswith("whisper"):
            continue
        if len(v) == 1 and v[0] == word:
            return True
    return False
