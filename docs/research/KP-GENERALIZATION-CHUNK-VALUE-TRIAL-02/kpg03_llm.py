# -*- coding: utf-8 -*-
"""KP-GENERALIZATION-CHUNK-VALUE-TRIAL-02 Trial専用LLM wrapper。
kpg02_llmを土台に: (1)専用費用台帳 (2)Cap(個別Cap/フェーズCap)超過で新規call拒否 (3)出力上限・thinking明示を強制
(4)mock(API 0、入力tokenは実測推定・出力tokenは過去実測の経験値で費用概算) (5)deepseek独立判定(非thinking+max_tokens)。
mock時は cache の読書きも本物の台帳も触らない。Production module非依存。"""
import os, sys, json, re, time, hashlib, threading
HERE = os.path.dirname(os.path.abspath(__file__))
OLD = os.path.join(HERE, "..", "KP-GENERALIZATION-CHUNK-VALUE-TRIAL-01")
sys.path.insert(0, OLD)
import kpg02_llm as B

WORK = os.path.join(HERE, "kpg03_work"); os.makedirs(WORK, exist_ok=True)
REAL_LEDGER = os.path.join(WORK, "cost_ledger.jsonl")
MOCK_LEDGER = os.path.join(WORK, "mock_ledger.jsonl")
CAP = float(os.environ.get("KPG3_CAP", "120"))     # 本Trial個別Cap(円)。Fable設定。引上げ禁止
WARN_RATIO = 0.8
PHASE_LIMIT = None                                  # フェーズ停止点(絶対値、円)。run側が設定
MOCK = False
B.LEDGER = REAL_LEDGER


class CapReached(RuntimeError):
    pass


def set_mock(v):
    global MOCK
    MOCK = bool(v)
    B.LEDGER = MOCK_LEDGER if MOCK else REAL_LEDGER


def total_cost():
    return B.total_cost()


def set_phase_cap(extra_jpy):
    """現在の累計 + extra_jpy を超える新規callを拒否(フェーズ停止点)。"""
    global PHASE_LIMIT
    PHASE_LIMIT = B.total_cost() + extra_jpy if extra_jpy else None


def _guard():
    t = B.total_cost()
    lim = CAP if PHASE_LIMIT is None else min(CAP, PHASE_LIMIT)
    if not MOCK and t >= lim:
        raise CapReached(f"累計¥{t:.2f} >= 上限¥{lim:.2f}(Cap¥{CAP}/phase)。新規callを拒否")
    if not MOCK and t >= CAP * WARN_RATIO and not getattr(_guard, "warned", False):
        _guard.warned = True
        print(f"[WARN] 累計¥{t:.2f}がCap¥{CAP}の{int(WARN_RATIO*100)}%に到達。Fableへ事前報告が必要", file=sys.stderr, flush=True)


def call(model, user, schema=None, *, system=None, effort=None, tag="", max_out=None, think_budget=None, use_cache=True):
    if max_out is None:
        raise ValueError("max_out必須(出力上限を明示)")
    if model.startswith("gemini-") and think_budget is None:
        raise ValueError("gemini: think_budget必須(非thinkingは0を明示)")
    if MOCK:
        return _mock(model, user, schema, system, tag, effort)
    _guard()
    return B.call(model, user, schema, system=system, effort=effort, tag=tag, max_out=max_out, think_budget=think_budget, use_cache=use_cache)


def call_ds(model, user, *, system=None, tag="", max_tokens=1500, use_cache=True):
    """DeepSeek独立判定。thinking無効+max_tokens明示。returns (json, meta)"""
    if MOCK:
        return _mock(model, user, {"name": "ds_judge"}, system, tag, None)
    _guard()
    key = hashlib.sha256(json.dumps(["ds3", model, user, system, max_tokens], ensure_ascii=False).encode()).hexdigest()[:24]
    cp = os.path.join(B.CACHE_DIR, "k3_" + key + ".json")
    if use_cache and os.path.exists(cp):
        d = json.load(open(cp, encoding="utf-8")); d["meta"]["cached"] = True
        return d["out"], d["meta"]
    B._load_env()
    from openai import OpenAI
    cl = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")
    t0 = time.time()
    msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": user}]
    r = cl.chat.completions.create(model=model, messages=msgs, response_format={"type": "json_object"}, max_tokens=max_tokens,
                                   extra_body={"thinking": {"type": "disabled"}})
    text = r.choices[0].message.content
    u = r.usage
    cost = B._cost(model, u.prompt_tokens, u.completion_tokens)
    meta = {"model_req": model, "model_id": r.model, "tag": tag, "in": u.prompt_tokens, "out": u.completion_tokens, "reasoning": 0,
            "cost_jpy": round(cost, 4), "sec": round(time.time() - t0, 1), "cached": False}
    B._ledger({**meta, "ts": time.strftime("%Y-%m-%dT%H:%M:%S")})
    out = json.loads(text)
    json.dump({"out": out, "meta": meta}, open(cp, "w", encoding="utf-8"), ensure_ascii=False)
    return out, meta


# ---------------- mock ----------------
# 出力token/候補の経験値(過去ledger実測: luna SEL≈3000/20cand→130、sol B2 776/14→55、GEN luna 1516/20→75、gemini VER 342/7→50)
OUT_PER = {("sel", "gpt-6-luna"): 130, ("sel", "gpt-6.1-sol"): 60, ("gen", "gpt-6-luna"): 75, ("gen", "gpt-6.1-sol"): 40, ("ver", "gemini"): 50,
           ("gate", "gemini"): 70, ("judge", "gemini"): 28, ("judge", "ds"): 40}


def _est_tokens(s):
    return int(len(re.findall(r"[A-Za-z0-9']+", s)) * 1.3 + len(re.findall(r"[^\x00-\x7f]", s)) * 0.9 + 1)


def _seg(user):
    return user.split("【候補】")[-1].split("【記事本文】")[0]


def _mock(model, user, schema, system, tag, effort):
    name = (schema or {}).get("name", "text")
    s = _seg(user)
    nm = max(1, len(re.findall(r"^\d+\. ", s, re.M)))
    out, kind = None, None
    if name == "kp_extract":
        txt = user.split("【記事本文】\n")[-1]
        sents = [x.strip() for x in re.split(r"(?<=[.!?])\s+", txt.replace("\n", " ")) if len(x.split()) >= 6]
        cands = []
        for st in sents:
            w = st.split()
            for k in (2, 4):
                if len(w) > k + 3 and len(cands) < 14:
                    cands.append({"span": " ".join(w[k:k + 3]).strip(".,;:!?\"()"), "sentence": st})
        out, kind = {"candidates": cands}, "ext"
    elif name.startswith("kp_rank3"):
        out = {"judgements": [{"id": i, "cls": "C" if i % 3 else "F", "chunk_type": "phrasal_verb" if i % 3 else "none", "reason_ja": "mock",
                               "difficulty": ["advanced", "upper_intermediate", "easy"][i % 3], "keep": bool(i % 3), "passive_fragment": False} for i in range(1, nm + 1)]}
        kind = "sel"
    elif name == "kp_gen_tokens4":
        toks = re.findall(r"^\s+トークン: (.+)$", s, re.M)
        items = []
        for i, line in enumerate(toks, 1):
            ts = re.findall(r"\[(\d+)\]([^\s\[]+)", line)
            tl = []
            for n, w in ts:
                n = int(n)
                lab = "CORE" if n <= 2 else ("SLOT_THING" if n == 3 else "DROP")
                tl.append({"n": n, "label": lab, "lemma": re.sub(r"[^\w'\-]", "", w.lower()) if lab == "CORE" else ""})
            items.append({"id": i, "tokens": tl, "gloss_ja": "mock意味", "sense_note_ja": "mock", "note_ja": "mock"})
        out, kind = {"items": items}, "gen"
    elif name in ("kp_verify", "kp_verify_gate"):
        n2 = max(1, len(re.findall(r"^\d+\. 本文の語句", user, re.M)))
        vs = []
        for i in range(1, n2 + 1):
            v = {"id": i, "verdict": "OK", "meaning_preserved": True, "gloss_consistent": True, "natural_headword": True, "issue": "", "fix_display_form": "", "fix_gloss_ja": ""}
            if name == "kp_verify_gate":
                v.update(gate_cls="C" if i % 4 else "F", gate_code="OK" if i % 4 else "FREE_COMBINATION")
            vs.append(v)
        out, kind = {"verdicts": vs}, ("gate" if name == "kp_verify_gate" else "ver")
        nm = n2
    elif name in ("kp_judge3", "ds_judge"):
        n2 = max(1, len(re.findall(r"^\d+\. 表示形", user, re.M)))
        out = {"judgements": [{"id": i, "cls": "C", "free_combo": False, "generalization_ok": True, "meaning_ok": True, "selectable": True, "code": "OK"} for i in range(1, n2 + 1)]}
        kind = "judge"
        nm = n2
    else:
        raise ValueError("mock未対応schema: " + name)
    fam = "gemini" if model.startswith("gemini") else ("ds" if model.startswith("deepseek") else model)
    k = (kind if kind in ("sel", "gen", "ver", "gate", "judge") else "sel", fam)
    per = OUT_PER.get(k) or OUT_PER.get((k[0], "gpt-6-luna"), 60)
    tin, tout = _est_tokens((system or "") + user), (per * nm if kind != "ext" else 1900)
    cost = B._cost(model, tin, tout)
    meta = {"model_req": model, "model_id": "MOCK", "tag": tag, "in": tin, "out": tout, "reasoning": 0, "cost_jpy": round(cost, 4), "sec": 0.0, "cached": False, "mock": True}
    B._ledger({**meta, "ts": time.strftime("%Y-%m-%dT%H:%M:%S")})
    return out, meta
