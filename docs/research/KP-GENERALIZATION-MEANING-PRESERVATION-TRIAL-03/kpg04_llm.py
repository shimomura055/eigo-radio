# -*- coding: utf-8 -*-
"""KP-GENERALIZATION-MEANING-PRESERVATION-TRIAL-03 Trial専用LLM wrapper(Production module非依存)。
安全装置: (1)Cap=環境変数KPG4_CAP(既定0=有料call全拒否。Fableが委任_02で確定するまで0) (2)フェーズ停止点(set_phase_cap)
(3)max_out/think_budget必須 (4)専用台帳kpg04_work/cost_ledger.jsonl (5)mock(API 0) (6)kpg03_llm.call/call_dsは無効化
(kpg03_llmのCAP=120/台帳を誤って使わせないため。import時にkpg03_llmのcallを例外化する)。"""
import os, sys, json, re, time, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
OLD1 = os.path.join(HERE, "..", "KP-GENERALIZATION-CHUNK-VALUE-TRIAL-01")
OLD2 = os.path.join(HERE, "..", "KP-GENERALIZATION-CHUNK-VALUE-TRIAL-02")
sys.path.insert(0, OLD1); sys.path.insert(0, OLD2)
import kpg02_llm as B
import kpg03_llm as L3          # _mock(旧schema)の流用と、旧call無効化のためだけに使う


def _forbidden(*a, **k):
    raise RuntimeError("kpg03_llm.call/call_dsはKPG-04では使用禁止(Cap/台帳が別。kpg04_llm.callを使うこと)")


L3.call = _forbidden
L3.call_ds = _forbidden

WORK = os.path.join(HERE, "kpg04_work"); os.makedirs(WORK, exist_ok=True)
REAL_LEDGER = os.path.join(WORK, "cost_ledger.jsonl")
MOCK_LEDGER = os.path.join(WORK, "mock_ledger.jsonl")
CAP = float(os.environ.get("KPG4_CAP", "0"))      # 既定0=有料call拒否。Fableが委任_02で確定
WARN_RATIO = 0.8
PHASE_LIMIT = None
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
    global PHASE_LIMIT
    PHASE_LIMIT = B.total_cost() + extra_jpy if extra_jpy else None


def _guard():
    t = B.total_cost()
    lim = CAP if PHASE_LIMIT is None else min(CAP, PHASE_LIMIT)
    if not MOCK and (CAP <= 0 or t >= lim):
        raise CapReached(f"累計¥{t:.2f} >= 上限¥{lim:.2f}(KPG4_CAP=¥{CAP}/phase)。新規有料callを拒否")
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


def call_ds(model, user, *, system=None, tag="", max_tokens=1500, use_cache=True, mock_name="ds_judge"):
    """DeepSeek独立判定(非thinking+max_tokens明示)。"""
    if MOCK:
        return _mock(model, user, {"name": mock_name}, system, tag, None)
    _guard()
    key = hashlib.sha256(json.dumps(["ds4", model, user, system, max_tokens], ensure_ascii=False).encode()).hexdigest()[:24]
    cp = os.path.join(B.CACHE_DIR, "k4_" + key + ".json")
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
    u = r.usage
    cost = B._cost(model, u.prompt_tokens, u.completion_tokens)
    meta = {"model_req": model, "model_id": r.model, "tag": tag, "in": u.prompt_tokens, "out": u.completion_tokens, "reasoning": 0,
            "cost_jpy": round(cost, 4), "sec": round(time.time() - t0, 1), "cached": False}
    B._ledger({**meta, "ts": time.strftime("%Y-%m-%dT%H:%M:%S")})
    out = json.loads(r.choices[0].message.content)
    json.dump({"out": out, "meta": meta}, open(cp, "w", encoding="utf-8"), ensure_ascii=False)
    return out, meta


# ---------------- mock(API 0。新schema対応。旧schemaはkpg03の_mockへ委譲) ----------------
def _n_items(user):
    seg = user.split("【候補】")[-1].split("【記事本文】")[0]
    return max(1, len(re.findall(r"^\d+\. ", seg, re.M)))


def _meta(model, user, kind_tokens, tag):
    tin = L3._est_tokens(user)
    cost = B._cost(model, tin, kind_tokens)
    return {"model_req": model, "model_id": "MOCK", "tag": tag, "in": tin, "out": kind_tokens, "reasoning": 0, "cost_jpy": round(cost, 4), "sec": 0.0, "cached": False, "mock": True}


def _mock(model, user, schema, system, tag, effort):
    name = (schema or {}).get("name", "text")
    if name == "kp_gen_tokens5":
        seg = user.split("【候補】")[-1].split("【記事本文】")[0]
        items = []
        for i, line in enumerate(re.findall(r"^\s+トークン: (.+)$", seg, re.M), 1):
            tl = []
            for n, w in re.findall(r"\[(\d+)\]([^\s\[]+)", line):
                n = int(n)
                lab = "CORE" if n <= 2 else ("SLOT_THING" if n == 3 else "DROP")
                tl.append({"n": n, "label": lab, "lemma": re.sub(r"[^\w'\-]", "", w.lower()) if lab == "CORE" else ""})
            hw = " ".join((t["lemma"] if t["label"] == "CORE" else "something") for t in tl if t["label"] != "DROP")
            items.append({"id": i, "source_sense_ja": "mock語義", "arg_notes": [{"n": 3, "referent_ja": "mock", "kind": "thing"}], "headword_frame": hw,
                          "frame_change": ["OBJECT_SLOT"], "tokens": tl, "gloss_ja": "mock意味", "sense_note_ja": "mock", "note_ja": "mock"})
        out = {"items": items}
        m = _meta(model, user, 130 * max(1, len(items)), tag)
    elif name == "kp_verify5":
        n = max(1, len(re.findall(r"^\d+\. 本文の語句", user, re.M)))
        out = {"verdicts": [{"id": i, "verdict": "OK", "meaning_preserved": True, "gloss_consistent": True, "natural_headword": True, "issue": "", "fix_display_form": "", "fix_gloss_ja": "",
                             "source_sense_ja": "mock", "frame_preserved": "SAME", "argument_type_ok": True} for i in range(1, n + 1)]}
        m = _meta(model, user, 70 * n, tag)
    elif name == "kp_check5":
        n = max(1, len(re.findall(r"^\d+\. 本文の語句", user, re.M)))
        out = {"checks": [{"id": i, "context_sense_ja": "mock", "example_en": "mock example", "relation": "SAME", "fix_display_form": "", "fix_gloss_ja": "", "reason_ja": ""} for i in range(1, n + 1)]}
        m = _meta(model, user, 90 * n, tag)
    else:
        return L3._mock(model, user, schema, system, tag, effort)
    B._ledger({**m, "ts": time.strftime("%Y-%m-%dT%H:%M:%S")})
    return out, m
