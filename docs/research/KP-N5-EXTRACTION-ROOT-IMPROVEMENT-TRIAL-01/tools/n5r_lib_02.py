"""Trial専用(非Production)。KP-N5-EXTRACTION-ROOT-IMPROVEMENT-TRIAL-01 委任_02 共通部品。TRIAL_PLAN_02.md(事前登録v2)の規則を実装する。
Production module(er138/er105/er119/er030/er108)はimport専用で無編集。flag・設定dict・環境変数による分岐なし(CAP_STOPのみ実行guard用)。"""
import sys, os, json, glob, re, time

ROOT = os.environ.get("N5R_ROOT") or os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
sys.path.insert(0, ROOT)
TD = os.path.join(ROOT, "docs/research/KP-N5-EXTRACTION-ROOT-IMPROVEMENT-TRIAL-01")
EV = os.path.join(TD, "ev02")
FIXTURE = os.path.join(ROOT, "docs/research/KP-GENERALIZATION-N5-PRODUCTION-WIRING-01/fixtures/n5_trial_replay_fixture_01.json")
CAP_STOP = float(os.environ.get("N5R_CAP_STOP", "120.0"))

from dotenv import load_dotenv
load_dotenv("C:/Users/tensh/eigo-radio/.env")
import er005_cost_logger as cl, er053_cost_aggregate_01 as agg
import er138_kp_n5_generalization_01 as n5
import er062_family_z_structure_01 as st
import er030_key_phrase_db_hybrid_core_01 as core

ft = n5.ft


def spent():
    return sum(agg.compute_stage_cost_breakdown_multi(p)["total_jpy"] for p in glob.glob(f"{EV}/cost_log_*.jsonl"))


def install_log(proc):
    cl.install(f"{EV}/cost_log_{proc}.jsonl")


def guard(est=0.8):
    st.check_stop_sentinel("n5r_trial", EV)
    s = spent()
    if s + est > CAP_STOP:
        raise SystemExit(f"cost guard: spent {s:.2f} + est {est} > stop {CAP_STOP}")
    return s


def fixture():
    return json.load(open(FIXTURE, encoding="utf-8"))


def make_ctx(case, proc_label, tag):
    process = "A2_SUPPORT" if case.endswith("_a2") else "B1_SUPPORT"
    return n5.N5Ctx(process, tag=tag, stop_check_fn=lambda w: st.check_stop_sentinel(w, EV), article_id="N5R2_" + case)


# ---------------- 抽出Prompt(Trial専用。表現名を含まない) ----------------
BODY = n5.BODY
HEAD_COMMON = ("1. **本文一致(絶対条件)**: 本文中の連続した語句をそのまま抜き出す。変更・言い換え・創作は禁止。\n"
               "2. **5語以内(絶対条件)**: 6語以上は出力禁止。\n")
DUP_LINE = "同じ語句や、一方が他方を含む類似語句は重ねない。"


def p_L1(t, n=14, dup=True):
    """E1(価値中立): B1の条件4・5を『難易度は問わない』に置換。"""
    return (f"以下の記事から、英語上級者が学ぶ価値のあるフレーズ・表現・イディオム・句動詞・連語・定着した名詞句(2語以上の連続した語句)の**候補を最大{n}個**、広めに挙げてください(後段で絞り込みます。ランキングは不要)。\n\n"
            + HEAD_COMMON + "3. 意味と自然さを保てる最短の形で抜き出す。\n4. 難易度は問わない(易しい表現も除外しない。難易度・学習価値は後段で判定する)。\n"
            + (DUP_LINE if dup else "") + "sentenceは本文中でその語句を含む文をそのまま書く。" + BODY + t)


def p_L3(t, n=40, dup=False):
    """E2: 網羅列挙(難易度・学習価値で絞らない)。"""
    return (f"以下の記事に含まれる、ひと塊で覚える対象になり得る表現を、本文から**漏れなく列挙**してください(最大{n}個)。対象は、句動詞(動詞+副詞/前置詞)、イディオム、固定表現、連語(コロケーション)、前置詞句の定型表現です。"
            "難易度や学習価値の高低で絞らず、基本語だけの表現も除外しないでください(絞り込みは後段で別に行います)。\n\n"
            + HEAD_COMMON + "3. 意味と自然さを保てる最短の形で抜き出す。\n"
            + (DUP_LINE if dup else "") + "同じ表現が本文の複数箇所にある場合は代表1箇所のみ。sentenceは本文中でその語句を含む文をそのまま書く。" + BODY + t)


# ---------------- E5 辞書seed(API 0) ----------------
_PARTS = {"away", "out", "up", "down", "off", "on", "in", "over", "back", "through", "around", "along", "aside", "apart", "forward", "together", "across", "by", "with", "for", "into", "to", "from", "at", "of", "about"}
_SEPDET = {"it", "that", "this", "them", "something", "everything", "things", "thing", "the", "a", "your", "my", "his", "her", "their", "its"}
_MULTI = None


def _multi():
    global _MULTI
    if _MULTI is None:
        wn = n5._wn()
        _MULTI = {l.lower() for l in wn.all_lemma_names() if "_" in l}
    return _MULTI


def e5_find(text):
    """本文語形還元+WordNet多語見出し照合(dict_seed_probe_01.pyと同一ロジック)。returns [surface span] (出現順)。"""
    wn = n5._wn(); MULTI = _multi()
    lem_v = lambda w: wn.morphy(w, "v") or w
    lem_n = lambda w: wn.morphy(w, "n") or w
    tk = re.findall(r"[A-Za-z]+(?:'[a-z]+)?", text); low = [t.lower() for t in tk]; hits = {}
    for n in (2, 3, 4):
        for i in range(len(tk) - n + 1):
            win = low[i:i + n]
            forms = {"_".join(win), "_".join([lem_v(win[0])] + win[1:]), "_".join([lem_n(w) for w in win])}
            if any(f in MULTI for f in forms):
                hits.setdefault(" ".join(tk[i:i + n]), i)
    for i, w in enumerate(low):
        v = lem_v(w)
        for gap in (1, 2, 3):
            j = i + gap + 1
            if j < len(low) and low[j] in _PARTS and f"{v}_{low[j]}" in MULTI and (gap == 1 or low[i + 1] in _SEPDET):
                hits.setdefault(" ".join(tk[i:j + 1]), i)
    return [k for k, _ in sorted(hits.items(), key=lambda kv: kv[1])]


# ---------------- LLM抽出呼出 ----------------
def run_extract(kind, text, ctx, tag):
    """kind in A0/E1/E2。returns (cands[{span,sentence}], info)。技術失敗はN5TechnicalFailureを呼出側へ。"""
    guard(0.6)
    if kind == "A0":
        pr = n5.prompt_B1(text)
    elif kind == "E1":
        pr = p_L1(text, 30)
    elif kind == "E2":
        pr = p_L3(text, 40)
    else:
        raise ValueError(kind)
    t0 = time.time(); k0 = len(ctx.metas)
    with cl.logging_context("N5R2", tag):
        o, m = n5.call_llm("b1", pr, n5.B1_SCHEMA, ctx, label=f"N5R2_{kind}")
    c = [dict(span=x["span"], sentence=x.get("sentence") or "") for x in o["candidates"]]
    return c, calls_info(ctx, k0, time.time() - t0)


def calls_info(ctx, k0, wall):
    ms = ctx.metas[k0:]
    return {"n_calls": len(ms), "cost_jpy": round(sum(m.get("cost_jpy") or 0 for m in ms), 4), "sec": round(sum(m.get("sec") or 0 for m in ms), 1), "wall_sec": round(wall, 1),
            "truncated": sum(1 for m in ms if m.get("json_ok") is False), "attempts_gt1": sum(1 for m in ms if (m.get("attempt") or 1) > 1),
            "metas": [{k: m.get(k) for k in ("stage", "label", "in", "out", "max_out", "attempt", "json_ok", "cost_jpy", "sec")} for m in ms]}


# ---------------- プール構築+SEL(Production pool_and_select er138:1266-1294と同一順序) ----------------
def base_from_fixture(case_obj):
    base = []
    for n, b in enumerate(case_obj["base"], 1):
        base.append({"span": b["span"], "sentence": b.get("sentence") or "", "n5_origin": "P7", "p7_rank": n,
                     "item": {"display_phrase": b["span"], "source_sentence": b.get("sentence") or ""}})
    return base


def pool_and_judge(text, base, cands, units, ctx, tag, log):
    """collect_pool(gate_fn=make_b1_gate, defer_out) -> select -> SEL_DEFERRED(Production同順)。screen_fnは無し(documented difference)。"""
    guard(0.8)
    k0 = len(ctx.metas); t0 = time.time()
    gate = n5.make_b1_gate(units, None)
    defer = []
    pool, rejected = n5.collect_pool(text, [dict(b) for b in base], cands, gate_fn=gate, defer_out=defer)
    with cl.logging_context("N5R2", tag):
        judged = n5.select(text, pool, log, ctx)
        deferred = []
        if defer:
            keep_spans = [c["span"] for c in judged if c["keep"]]
            second = []
            for d in defer:
                b = dict(d["cand"]); n5._fill_sentence(text, b)
                if n5.FRAG.search(b["span"]):
                    continue
                if any(n5._contains(b["span"], k) for k in keep_spans):
                    continue
                if any(n5._contains(b["span"], o["span"]) for o in second):
                    continue
                second.append(b)
            if second:
                rej = n5.select(text, second, log, ctx, label="SEL_DEFERRED")
                judged = judged + rej
                deferred = [{"span": c["span"], "keep": c["keep"]} for c in rej]
    info = calls_info(ctx, k0, time.time() - t0)
    info.update(n_pool=len(pool), n_rejected=len(rejected), n_keep=sum(1 for c in judged if c["keep"]), deferred=deferred, rejected=[{k: r.get(k) for k in ("span", "reasons", "origin", "blocked_by")} for r in rejected])
    return judged, pool, info


def slim(c):
    return {k: c.get(k) for k in ("span", "sentence", "n5_origin", "p7_rank", "cls", "chunk_type", "difficulty", "keep", "passive_fragment", "chunk_reason_ja")}


# ---------------- pick規則 ----------------
RANK = n5.RANK


def _pos(span, text_l):
    s = " ".join(n5.toks(span))
    m = re.search(r"\b" + r"\W+".join(re.escape(t) for t in n5.toks(span)) + r"\b", text_l)
    return m.start() if m else 10 ** 9


def _dedupe_cap(ordered, cap):
    out = []
    for c in ordered:
        dfl = (c.get("display_form") or "").lower()
        if any(n5._contains(c["span"], o["span"]) or n5._contains(o["span"], c["span"]) for o in out):
            continue
        if dfl and any((o.get("display_form") or "").lower() == dfl for o in out):
            continue
        out.append(c)
    return out[:cap]


def pick_R0(judged, cap=7):
    return n5.pick(judged, cap)


def _kd(c, text_l, rank):
    return (rank, 0 if c.get("n5_origin") == "P7" else 1, _pos(c["span"], text_l))


def pick_R0d(judged, text, cap=7):
    tl = text.lower(); ks = [c for c in judged if c["keep"]]
    ks.sort(key=lambda c: _kd(c, tl, RANK.get(c["difficulty"], 1)))
    return _dedupe_cap(ks, cap)


def _r1rank(c):
    r = RANK.get(c["difficulty"], 1)
    return r - 1 if (c["difficulty"] == "easy" and c.get("chunk_type") in ("phrasal_verb", "idiom")) else r


def pick_R1(judged, cap=7):
    ks = [c for c in judged if c["keep"]]
    ks.sort(key=_r1rank)            # stable: tie=入力順
    return _dedupe_cap(ks, cap)


def pick_R1d(judged, text, cap=7):
    tl = text.lower(); ks = [c for c in judged if c["keep"]]
    ks.sort(key=lambda c: _kd(c, tl, _r1rank(c)))
    return _dedupe_cap(ks, cap)


_TYPE_PRIO = {"phrasal_verb": 0, "idiom": 0, "fixed_phrase": 1, "collocation": 1}


def pick_R5(judged, text, k=2, cap=7):
    tl = text.lower(); ks = [c for c in judged if c["keep"]]
    ks.sort(key=lambda c: _kd(c, tl, RANK.get(c["difficulty"], 1)))
    top = _dedupe_cap(ks, cap - k)
    rest = [c for c in ks if c not in top]
    easy = [c for c in rest if c["difficulty"] == "easy"]
    easy.sort(key=lambda c: (_TYPE_PRIO.get(c.get("chunk_type"), 2),) + _kd(c, tl, 0))
    res = list(top)
    for c in easy:
        if len(res) >= cap: break
        if len(res) - len(top) >= k: break
        if not any(n5._contains(c["span"], o["span"]) or n5._contains(o["span"], c["span"]) for o in res):
            res.append(c)
    for c in ks:                          # 不足はR0d順で補う
        if len(res) >= cap: break
        if c in res: continue
        if not any(n5._contains(c["span"], o["span"]) or n5._contains(o["span"], c["span"]) for o in res):
            res.append(c)
    return res[:cap]


def body_recur_trial(span, text):
    """参考A3専用(occ-v1と別物)。probe pool_pick_probe_01.py occ()と同一: 冠詞・代名詞等を除去して順序一致の窓一致をとる(過大になり得る)。"""
    sents = [s for s in re.split(r"(?<=[.!?])\s+", text.replace("\n", " ")) if s.strip()]
    ts = [t for t in n5.toks(span) if t not in n5.PLACE and t not in ("a", "an", "the", "it", "that", "this", "something", "someone")]
    if not ts: return 0
    L = [n5.lemmas(t) for t in ts]; c = 0
    for s in sents:
        tk = n5.toks(s); ok = False
        for i in range(len(tk)):
            if not (L[0] & n5.lemmas(tk[i])): continue
            j = i + 1; k = 1
            while k < len(L) and j < len(tk) and j <= i + len(ts) + 2:
                if L[k] & n5.lemmas(tk[j]): k += 1
                j += 1
            if k == len(L): ok = True; break
        c += ok
    return c


def body_recur_strict(span, text):
    """span語を除去せず連続一致(代名詞/something系は1語のワイルドカードまたは省略可、冠詞は字面一致)。"""
    sents = [s for s in re.split(r"(?<=[.!?])\s+", text.replace("\n", " ")) if s.strip()]
    sp = n5.toks(span); WILD = set(n5.PLACE) | set(n5.PRON)
    def match(a, tk, b):
        if a == len(sp): return True
        t = sp[a]
        if t in WILD:
            if match(a + 1, tk, b): return True
            return b < len(tk) and match(a + 1, tk, b + 1)
        return b < len(tk) and bool(n5.lemmas(t) & n5.lemmas(tk[b])) and match(a + 1, tk, b + 1)
    c = 0
    for s in sents:
        tk = n5.toks(s)
        if any(match(0, tk, i) for i in range(len(tk))): c += 1
    return c


def pick_A3(judged, text, cap=7):
    for c in judged:
        c["body_recur_trial"] = body_recur_trial(c["span"], text)
    ks = [c for c in judged if c["keep"]]
    ks.sort(key=lambda c: RANK.get(c["difficulty"], 1) - (1 if (c["difficulty"] == "easy" and c["body_recur_trial"] >= 3) else 0))
    return _dedupe_cap(ks, cap)


# ---------------- RR(rerank、SEL無変更、1 call) ----------------
RR_SCHEMA = {"name": "kp_rerank", "schema": {"type": "object", "additionalProperties": False, "required": ["order"], "properties": {"order": {"type": "array", "items": {"type": "integer"}}}}}


def prompt_RR(text, cands):
    lines = [f"{i}. {c['span']}\n   文: {c['sentence']}" for i, c in enumerate(cands, 1)]
    return ("次は記事から選ばれた学習候補(ひと塊の表現)です。この記事を学ぶ英語学習者が、ひと塊で覚える価値の高い順に並べてください。"
            "基準: (a)構成語から意味・組合せが予測しにくい (b)辞書見出し・他の文脈でも使える汎用性 (c)記事の内容理解に関わる。"
            "易しい語でできていることを理由に順位を下げない。全候補を一度ずつ、価値の高い順にidで返す。\n\n【候補】\n" + "\n".join(lines) + BODY + text)


def run_rerank(text, judged, ctx, tag, log=None, cap=7):
    """returns (picked, info)。失敗時はR0d(フォールバック、記録)。"""
    ks = [c for c in judged if c["keep"]]
    if not ks:
        return [], {"n_calls": 0, "cost_jpy": 0, "sec": 0, "fallback": "no_keep"}
    guard(0.5)
    k0 = len(ctx.metas); t0 = time.time(); fb = None
    try:
        with cl.logging_context("N5R2", tag):
            o, m = n5.call_llm("sel", prompt_RR(text, ks), RR_SCHEMA, ctx, label="N5R2_RERANK")
        order = []
        for i in o.get("order", []):
            if isinstance(i, int) and 1 <= i <= len(ks) and i not in order:
                order.append(i)
        missing = [i for i in range(1, len(ks) + 1) if i not in order]
        tl = text.lower()
        rest = sorted(missing, key=lambda i: _kd(ks[i - 1], tl, RANK.get(ks[i - 1]["difficulty"], 1)))
        ordered = [ks[i - 1] for i in order + rest]
        picked = _dedupe_cap(ordered, cap)
        n_missing = len(missing)
    except n5.N5TechnicalFailure as e:
        fb = f"RR失敗->R0d: {str(e)[:120]}"
        picked = pick_R0d(judged, text, cap); n_missing = None
    info = calls_info(ctx, k0, time.time() - t0)
    info.update(fallback=fb, n_input=len(ks), n_missing=n_missing)
    return picked, info


# ---------------- 評価regex(TRIAL_PLAN_02 §2-7で固定。評価script内のみ) ----------------
PUT_AWAY = re.compile(r"\bput(?:ting)?(?:\s+(?:it|that|this|something|them|things))?\s+away\b", re.I)
IN_THE_WAY = re.compile(r"\bin the way\b", re.I)
LEAVE_OUT = re.compile(r"\b(leave|leaving|left)\b(?:\s+\w+){0,2}?\s+out\b", re.I)
IN_SIGHT = re.compile(r"\bin sight\b", re.I)
TITLE_PHRASES = re.compile(r"now in session|in session|left out again", re.I)


def hits(strings):
    s = " | ".join(strings)
    return {"put_away": bool(PUT_AWAY.search(s)), "in_the_way": bool(IN_THE_WAY.search(s)), "leave_out": bool(LEAVE_OUT.search(s)), "in_sight": bool(IN_SIGHT.search(s))}


def norm_key(span):
    return " ".join(n5.toks(span))


# ================= Phase 3 (TRIAL_PLAN_03) =================
def _span_rx(span):
    ts = n5.toks(span)
    return re.compile(r"\b" + r"\W+".join(re.escape(t) for t in ts) + r"\b", re.I) if ts else None


def heading_only(span, text):
    """出現が見出し行(#始まり)にのみある句=True。本文行に出現、または出現位置不明=False。"""
    rx = _span_rx(span)
    if rx is None: return False
    lines = text.split("\n")
    in_head = any(rx.search(l) for l in lines if l.lstrip().startswith("#"))
    in_body = any(rx.search(l) for l in lines if l.strip() and not l.lstrip().startswith("#"))
    return in_head and not in_body


def pick_A12(judged, text, cap=7):
    tl = text.lower(); ks = [c for c in judged if c["keep"] and not heading_only(c["span"], text)]
    ks.sort(key=lambda c: _kd(c, tl, _r1rank(c)))
    return _dedupe_cap(ks, cap)


def _body_sentences(text):
    body = "\n".join(l for l in text.split("\n") if l.strip() and not l.lstrip().startswith("#"))
    return [s for s in re.split(r"(?<=[.!?])\s+", body.replace("\n", " ")) if s.strip()]


def pick_A10(judged, text, cap=7):
    sents = _body_sentences(text); n = len(sents); tl = text.lower()
    ks = [c for c in judged if c["keep"]]
    ks.sort(key=lambda c: _kd(c, tl, _r1rank(c)))
    def sec_of(c):
        rx = _span_rx(c["span"])
        for i, s in enumerate(sents):
            if rx and rx.search(s): return min(cap - 1, i * cap // max(1, n))
        return None
    chosen = []
    for k in range(cap):
        for c in ks:
            if sec_of(c) == k and not any(n5._contains(c["span"], o["span"]) or n5._contains(o["span"], c["span"]) for o in chosen):
                chosen.append(c); break
    for c in ks:
        if len(chosen) >= cap: break
        if c not in chosen and not any(n5._contains(c["span"], o["span"]) or n5._contains(o["span"], c["span"]) for o in chosen):
            chosen.append(c)
    chosen.sort(key=lambda c: ks.index(c))
    return chosen[:cap]


SLATE_SCHEMA = {"name": "kp_slate", "schema": {"type": "object", "additionalProperties": False, "required": ["selected"], "properties": {"selected": {"type": "array", "items": {"type": "integer"}}}}}


def prompt_SLATE(text, cands, cap=7):
    lines = [f"{i}. {c['span']}\n   文: {c['sentence']}" for i, c in enumerate(cands, 1)]
    return (f"次は記事から選ばれた学習候補(ひと塊の表現)の一覧です。この記事で学ぶ英語学習者のために、最終候補を**ちょうど{cap}件**選んでください。"
            f"{cap}件全体として、次の観点が偏らない良い構成にしてください: (1)記事の主題・場面を表すうえで中心的な表現 (2)構成語から意味や組合せが予測しにくい慣用表現・句動詞 "
            "(3)他の文脈でも広く使える汎用性の高い固定表現・連語。同じ意味・用法の重複、記事の題名・見出しにしか現れない句は選ばない。易しい語でできていることを理由に除外しない。"
            "選んだ件のidを重要な順に返す。\n\n【候補】\n" + "\n".join(lines) + BODY + text)


def run_slate(text, judged, ctx, tag, cap=7):
    ks = [c for c in judged if c["keep"]]
    if not ks:
        return [], {"n_calls": 0, "cost_jpy": 0, "sec": 0, "fallback": "no_keep"}
    guard(0.5)
    k0 = len(ctx.metas); t0 = time.time(); fb = None; nsel = None
    tl = text.lower()
    try:
        with cl.logging_context("N5R2", tag):
            o, m = n5.call_llm("sel", prompt_SLATE(text, ks, cap), SLATE_SCHEMA, ctx, label="N5R2_SLATE")
        sel = []
        for i in o.get("selected", []):
            if isinstance(i, int) and 1 <= i <= len(ks) and i not in sel: sel.append(i)
        nsel = len(sel)
        chosen = _dedupe_cap([ks[i - 1] for i in sel], cap)
        if len(chosen) < cap:                       # 不足はR1d順で補う(記録)
            for c in sorted(ks, key=lambda c: _kd(c, tl, _r1rank(c))):
                if len(chosen) >= cap: break
                if c not in chosen and not any(n5._contains(c["span"], x["span"]) or n5._contains(x["span"], c["span"]) for x in chosen): chosen.append(c)
        picked = chosen[:cap]
    except n5.N5TechnicalFailure as e:
        fb = f"SLATE失敗->R1d: {str(e)[:120]}"
        picked = pick_R1d(judged, text, cap)
    info = calls_info(ctx, k0, time.time() - t0)
    info.update(fallback=fb, n_input=len(ks), n_selected_valid=nsel)
    return picked, info
