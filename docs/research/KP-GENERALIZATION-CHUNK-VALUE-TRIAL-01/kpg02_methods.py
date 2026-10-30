# -*- coding: utf-8 -*-
"""KPG-02 Trial専用: 方式D' = D + (1)意味修飾語DROPガード/検証meaning_preserved=falseで元span形へ戻す (2)塊判定2回和集合
(3)someone/something判定・受動形除外 (4)G1/G2型(動詞+一般名詞目的語)の「一般化すれば塊」判定を別枠(alt)で併記。Production非接触。"""
import re
import kpg02_llm as L
import kpg01_validate as V
import kpg01_gen2 as G
from kpg01_methods import prompt_B1, B1_SCHEMA, prompt_B4, B4_SCHEMA, prod_p7_cands, CHUNK_DEFS, BODY
from kpg01_methods2 import _contains

# ---- (1) 意味を担う修飾語のDROP禁止ガード(決定論) ----
NEG = {"not", "no", "never", "n't", "without", "neither", "nor", "nothing"}
CMP = {"more", "less", "most", "least", "fewer", "fewest"}
FUNC = {"the", "a", "an", "this", "that", "these", "those", "his", "her", "their", "its", "my", "your", "our", "one", "some", "any", "every", "each", "such"}


# 節の断片(関係詞・疑問詞で始まる/前置詞+関係詞を含む形)は塊として不可(決定論。塊判定のばらつき対策)
FRAG = re.compile(r"^(whose|which|what|who|whom|where|when|whether|that|how)\b|\b(at|in|on|of|to|for|with|by)\s+(which|whom|whose)\b", re.I)

# 名詞複数形の語形一致(WordNet morphyが'sales'をそのまま見出しとして返し'sale'と一致しない問題の補正。Trial用monkeypatch)
_orig_lemmas = V.lemmas


def _lemmas_plus(tok):
    out = set(_orig_lemmas(tok))
    t = tok.lower().replace("'s", "")
    if t.endswith("ies") and len(t) > 4:
        out.add(t[:-3] + "y")
    elif t.endswith("es") and len(t) > 3:
        out.add(t[:-2])
    if t.endswith("s") and len(t) > 3:
        out.add(t[:-1])
    return out


import threading
_WN_LOCK = threading.RLock()     # NLTK WordNet(zip)はthread-safeでない(並列実行でAssertionError/close AttributeError)ため全アクセスをlock
_orig_wnmw = V.wn_multiword


def _lemmas_locked(tok):
    with _WN_LOCK:
        return _lemmas_plus(tok)


def _wnmw_locked(d):
    with _WN_LOCK:
        return _orig_wnmw(d)


V.lemmas = _lemmas_locked
V.wn_multiword = _wnmw_locked


def is_meaning_modifier(tok):
    with _WN_LOCK:
        return _is_meaning_modifier(tok)


def _is_meaning_modifier(tok):
    t = tok.lower().strip(".,;:!?\"()")
    if t in NEG or t in CMP:
        return True
    if t in FUNC:
        return False
    from nltk.corpus import wordnet as wn
    if t.endswith(("er", "est")):
        base = re.sub(r"(er|est)$", "", t)
        if t not in ("water", "paper", "number", "answer", "order", "matter", "other", "never", "ever") and (
                wn.synsets(base, "a") or wn.synsets(base + "e", "a")):
            return True      # 比較級・最上級(lower, longer, biggest)
    syn = wn.synsets(t)
    if syn:
        pos = {s.pos() for s in syn}
        if pos <= {"a", "s", "r"}:      # 形容詞/副詞のみの語(unexpected, usual等)
            return True
    return False


def guard_tokens(span, tokens):
    """DROPされた意味修飾語のうち、次の非DROP語がCOREのもの(=核の名詞/動詞を修飾)をCOREに戻す。SLOT名詞を修飾するものはDROPのまま。"""
    sp = G.tokenize(span)
    by = {t["n"]: dict(t) for t in tokens}
    restored = []
    n = len(sp)
    for i in range(1, n + 1):
        t = by.get(i)
        if not t or t["label"] != "DROP":
            continue
        if not is_meaning_modifier(sp[i - 1]):
            continue
        j = i + 1
        while j <= n and by.get(j, {}).get("label") == "DROP":
            j += 1
        if j <= n and by[j]["label"] == "CORE":
            t["label"] = "CORE"
            t["lemma"] = sp[i - 1].lower().strip(".,;:!?\"()")
            restored.append(sp[i - 1])
    return list(by.values()), restored


# ---- (2)(3)(4) 塊判定 ----
B2P_SCHEMA = {"name": "kp_rank2", "schema": {"type": "object", "additionalProperties": False, "required": ["judgements"], "properties": {
    "judgements": {"type": "array", "items": {"type": "object", "additionalProperties": False,
        "required": ["id", "cls", "chunk_type", "chunk_reason_ja", "difficulty", "keep", "passive_fragment", "chunk_if_generalized"],
        "properties": {"id": {"type": "integer"}, "cls": {"type": "string", "enum": ["W", "F", "C"]},
                       "chunk_type": {"type": "string", "enum": ["idiom", "phrasal_verb", "collocation", "fixed_phrase", "compound_noun", "none"]},
                       "chunk_reason_ja": {"type": "string"}, "difficulty": {"type": "string", "enum": ["advanced", "upper_intermediate", "easy"]},
                       "keep": {"type": "boolean"}, "passive_fragment": {"type": "boolean"}, "chunk_if_generalized": {"type": "boolean"}}}}}}}

EXTRA_RULES = """
## 追加の判定規則(重要)
(a) **受動態・完了形・不定詞の断片**: 受動態や過去分詞を核に含む形(例: have yet to be done、was given up)は、辞書の見出し語として自然な能動の塊になっていない限り、passive_fragment=trueとしてkeep=falseにする(ただしbe taken aback、be fed up with のように受動形そのものが固定された見出しなら塊として扱ってよい)。
(b) **chunk_if_generalized**: clsがC/Fを問わず、『自由に入れ替わる目的語名詞をsomething/someoneに置き換えた一般形が、学習者用英英辞書の見出し(句動詞・前置詞付き動詞・慣用的な連語)として成立する』場合はtrue(『動詞+前置詞/粒子+目的語』のうち、動詞と前置詞/粒子の組合せ自体が見出しのとき)。名詞を替えると意味が変わる連語、字面どおりの意味の組合せはfalse。C判定やW判定ではfalse。このフラグはkeepの判定とは独立(keepはclsがCかで決める)。
"""


def prompt_B2P(text, cands, reverse=False):
    order = list(range(len(cands)))
    if reverse:
        order = order[::-1]
    lines = []
    for k, idx in enumerate(order, 1):
        c = cands[idx]
        w = V.wn_multiword(c["span"])
        h = f" [WordNet複合語見出し: {'あり' if w else 'なし' if w is False else '-'}(参考。なしでも塊でないとは限らない)]"
        lines.append(f"{k}. {c['span']}{h}\n   文: {c['sentence']}")
    p = ("次は英語記事から抽出された学習候補フレーズです。各候補を評価し、ユーザーが修正せずに選べる候補だけをkeep=trueにしてください。\n\n"
         + CHUNK_DEFS + "\n\n"
         "## 判定手順\n"
         "各候補について(1)W/F/Cの区分、(2)Cなら塊の種類と『なぜこの組合せをひと塊で覚える価値があるか』の1文説明(40字以内)、"
         "(3)難易度(advanced=上級者でも学ぶ価値/upper_intermediate=中上級/easy=易しい)を判定する。\n"
         "keep=trueにできるのは、区分がCで、難易度がeasyでなく、本文語義でのまとまりとして成立し、他の候補と意味・用法が重ならないものだけ。"
         "**候補が不足してもkeepを甘くしない(品質を下げて埋めない)。**\n"
         "難易度の優先: advancedを先に、次にupper_intermediate。\n" + EXTRA_RULES + "\n【候補】\n" + "\n".join(lines) + BODY + text)
    return p, order


# ---- (3) 一般化段の追加規則 ----
GEN_EXTRA = """
7. **人称の判定(someone/something)**: 目的語の位置にある語が、本文の文脈で『人』を指すならSLOT_PERSON(someone)、『物・事』ならSLOT_THING(something)にする。代名詞itでも、文脈で人を指すなら人(例: hear X outのXが人なら hear someone out)。本文の指す対象に合わせる。
8. **意味を担う修飾語はDROPしない**: 形容詞・比較級・否定語・程度語のうち、核の名詞や動詞の意味を決めているものはDROPではなくCOREにする。DROPにしてよいのは文脈語や、SLOTにする名詞の修飾語だけ。
9. 受動態・過去分詞を核に残さない。能動の一般形にできない場合は、無理に一般化せず元の形をそのまま(CORE)にする。
"""


ALT_EXTRA = """
10. **この候補群は『動詞(+前置詞/粒子)の組合せが辞書の見出し語で、目的語名詞は自由に入れ替わる』と判定済みです。** 目的語名詞は原則SLOT_THING(またはSLOT_PERSON)にして『動詞+something+前置詞/粒子/補語』の一般形を作ってください。名詞を別の名詞に替えると表現の意味そのものが失われる場合のみCOREに残し、note_jaに理由を書く。
"""


def prompt_G3(text, sel, alt=False):
    p = G.prompt_G2(text, sel)
    return p.replace("gloss_ja: **一般形", GEN_EXTRA + (ALT_EXTRA if alt else "") + "\ngloss_ja: **一般形", 1)


def _meta(m):
    return {k: m[k] for k in ("model_id", "in", "out", "cost_jpy", "sec")}


def generalize_items(case, kept, log, *, m_gen, eff_gen, tag, m_verify, verify_think, track):
    text = case["text"]
    if not kept:
        return []
    o, m = L.call(m_gen, prompt_G3(text, kept, alt=(track == "alt")), G.G2_SCHEMA, effort=eff_gen, tag=f"{case['id']}:{tag}:GEN:{track}", max_out=6000)
    log["stages"].append({"stage": f"GEN_{track}", **_meta(m)})
    gm = {x["id"]: x for x in o["items"]}
    items = []
    for i, c in enumerate(kept, 1):
        x = gm.get(i)
        if not x:
            log.setdefault("gen_missing", []).append(c["span"])
            continue
        toks, restored = guard_tokens(c["span"], x["tokens"])
        df, err = G.assemble(c["span"], toks)
        if df is None:
            log.setdefault("assemble_failed", []).append({"span": c["span"], "err": err})
            continue
        it = dict(c, display_form=df, gloss_ja=x["gloss_ja"], sense_note_ja=x["sense_note_ja"], generalization_note_ja=x["note_ja"],
                  tokens=[(t["n"], t["label"], t["lemma"]) for t in toks], guard_restored=restored, track=track)
        if restored:
            log.setdefault("guard_restored", []).append({"span": c["span"], "restored": restored, "display_form": df})
        items.append(it)
    vd = {}
    if items:
        o, m = L.call(m_verify, prompt_B4(text, items), B4_SCHEMA, tag=f"{case['id']}:{tag}:VER:{track}", think_budget=verify_think, max_out=4000)
        log["stages"].append({"stage": f"VERIFY_{track}", **_meta(m)})
        vd = {x["id"]: x for x in o["verdicts"]}
    final = []
    for i, c in enumerate(items, 1):
        v = vd.get(i, {})
        c["verify"] = v
        if v.get("verdict") == "REJECT":
            log.setdefault("verify_dropped", []).append({"span": c["span"], "issue": v.get("issue")})
            continue
        if v.get("verdict") == "FIX":
            fx = V.strip_trailing_slot((v.get("fix_display_form") or "").replace(" / ", " ").strip())
            if fx:
                okf, whyf = V.display_check(fx, c["span"])
                if okf:
                    c["display_form_pre_fix"] = c["display_form"]
                    c["display_form"] = fx
                else:
                    log.setdefault("fix_rejected_by_validator", []).append({"span": c["span"], "fix": fx, "why": whyf})
            if v.get("fix_gloss_ja"):
                c["gloss_ja"] = v["fix_gloss_ja"]
        # (1) 検証でmeaning_preserved=false -> 元のspan形へ戻す(決定論)
        if v.get("meaning_preserved") is False:
            orig = " ".join(G.tokenize(c["span"])).lower()
            orig = re.sub(r"[.,;:!?\"()]+$", "", orig)
            if orig != c["display_form"]:
                log.setdefault("reverted_to_span", []).append({"span": c["span"], "from": c["display_form"], "to": orig, "issue": v.get("issue")})
                c["display_form_pre_revert"] = c["display_form"]
                c["display_form"] = orig
                c["reverted"] = True
        ok, why = V.display_check(c["display_form"], c["span"])
        if not ok:
            log.setdefault("validator_dropped", []).append({"span": c["span"], "display_form": c["display_form"], "why": why})
            continue
        final.append(c)
    return final


def pack(c):
    return dict(source_span=c["span"], source_sentence=c["sentence"], display_form=c["display_form"], gloss_ja=c["gloss_ja"],
                chunk_type=c["chunk_type"], chunk_reason_ja=c["chunk_reason_ja"], difficulty=c["difficulty"],
                sense_note_ja=c["sense_note_ja"], generalization_note_ja=c["generalization_note_ja"], verify=c.get("verify"),
                display_form_pre_fix=c.get("display_form_pre_fix"), tokens=c.get("tokens"), guard_restored=c.get("guard_restored"),
                reverted=c.get("reverted", False), display_form_pre_revert=c.get("display_form_pre_revert"), track=c.get("track"),
                sel_votes=c.get("sel_votes"))


def run_D2(case, *, m_sel="gpt-6-luna", eff_sel=None, m_gen="gpt-6-luna", eff_gen=None, m_verify="gemini-3.8-flash", verify_think=0,
           tag="D2", cap=7, passes=2, alt_cap=3):
    text = case["text"]
    log = {"stages": [], "tag": tag}
    base = [dict(c, sentence=c.get("sentence") or "") for c in prod_p7_cands(case)] if case.get("before") else []
    cands = list(base)
    o, m = L.call("gpt-6-luna", prompt_B1(text), B1_SCHEMA, tag=f"{case['id']}:{tag}:B1")
    log["stages"].append({"stage": "B1_overgen", **_meta(m)})
    for c in o["candidates"]:
        if V.span_in_text(c["span"], text) and not any(_contains(c["span"], b["span"]) for b in cands):
            cands.append(c)
    for c in cands:
        if not c.get("sentence"):
            for sent in text.replace("\n", " ").split(". "):
                if V.span_in_text(c["span"], sent):
                    c["sentence"] = sent.strip()
                    break
    log["cands"] = [c["span"] for c in cands]
    log["cands_from_p7"] = [c["span"] for c in base]
    rankmap = {"advanced": 0, "upper_intermediate": 1, "easy": 2}
    votes = {}
    import concurrent.futures as cf

    def _sel(p):
        prompt, order = prompt_B2P(text, cands, reverse=(p % 2 == 1))
        o, m = L.call(m_sel, prompt, B2P_SCHEMA, effort=eff_sel, tag=f"{case['id']}:{tag}:SEL{p}", max_out=7000)
        return p, o, m, order
    with cf.ThreadPoolExecutor(passes) as ex:
        sel_res = list(ex.map(_sel, range(passes)))
    for p, o, m, order in sel_res:
        log["stages"].append({"stage": f"SEL{p}", **_meta(m)})
        for j in o["judgements"]:
            if 1 <= j["id"] <= len(order):
                votes.setdefault(order[j["id"] - 1], []).append(j)
    kept, alt = [], []
    log["judged"] = []

    def okj(j):
        return j["keep"] and j["cls"] == "C" and j["difficulty"] != "easy" and not j["passive_fragment"]
    for idx, c in enumerate(cands):
        js = votes.get(idx, [])
        if not js:
            continue
        easy_veto = any(j["difficulty"] == "easy" and j["cls"] == "C" for j in js)      # 難易度は保守側(どちらかがeasyなら不可)。和集合はC/F境界のばらつきに適用
        good = [j for j in js if okj(j)]
        rep = good[0] if good else js[0]
        log["judged"].append({"span": c["span"], "votes": [(j["cls"], j["difficulty"], j["keep"], j["passive_fragment"], j["chunk_if_generalized"]) for j in js]})
        cc = dict(c, cls=rep["cls"], chunk_type=rep["chunk_type"], chunk_reason_ja=rep["chunk_reason_ja"], difficulty=rep["difficulty"],
                  keep=rep["keep"], sel_votes=len(good))
        if good and not easy_veto and not FRAG.search(c["span"]):
            cc["difficulty"] = min((j["difficulty"] for j in good), key=lambda d: rankmap[d])
            kept.append(cc)
        gjs = [j for j in js if j["chunk_if_generalized"] and not j["passive_fragment"]]
        if gjs:
            gj = gjs[0]
            ca = dict(c, cls="F", chunk_type=gj["chunk_type"] if gj["chunk_type"] != "none" else "phrasal_verb",
                      chunk_reason_ja=gj["chunk_reason_ja"] or "一般化すれば見出し語として成立", difficulty=gj["difficulty"], keep=False, sel_votes=len(gjs))
            alt.append(ca)
    kept.sort(key=lambda c: rankmap[c["difficulty"]])
    kept = kept[:cap]
    alt = [a for a in alt if not any(a["span"] != k["span"] and (_contains(a["span"], k["span"]) or _contains(k["span"], a["span"])) for k in kept)][:alt_cap]
    with cf.ThreadPoolExecutor(2) as ex:
        f1 = ex.submit(generalize_items, case, kept, log, m_gen=m_gen, eff_gen=eff_gen, tag=tag, m_verify=m_verify, verify_think=verify_think, track="main")
        f2 = ex.submit(generalize_items, case, alt, log, m_gen=m_gen, eff_gen=eff_gen, tag=tag, m_verify=m_verify, verify_think=verify_think, track="alt")
        final, alt_final = f1.result(), f2.result()
    mainforms = {(c["span"], c["display_form"].lower()) for c in final}
    alt_final = [c for c in alt_final if (c["span"], c["display_form"].lower()) not in mainforms]
    return {"items": [pack(c) for c in final], "alt_items": [pack(c) for c in alt_final], "log": log}
