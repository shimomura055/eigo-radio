# -*- coding: utf-8 -*-
"""FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_07: Std日本語意味・Adv英語説明の品質改善Trial(DEV専用、er112基盤)。
Production file(er003_*/er019_*/runner)は編集しない。importして呼ぶだけ。Trial arm差分はこのfile内のprompt組立で実現(Production関数へのmonkeypatchなし)。
出力: er112_output/kp_gm_trial_02/ 。費用台帳=paid_calls.jsonl。
"""
from __future__ import annotations
import argparse, copy, hashlib, json, os, random, re, sys, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")
OUT = ROOT / "er112_output" / "kp_gm_trial_02"
LEDGER = OUT / "paid_calls.jsonl"
RES = OUT / "results.jsonl"
CAP_JPY = 70.0
RD = ROOT / "docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01"
STOP_PATHS = [OUT / "STOP", OUT / "STOP_ALL", ROOT / "er026_output/family_z_production_e2e_01/STOP_ALL", RD / "STOP"]

import er019_family_x_kp_explanation_01 as kx          # noqa: E402 (Production module: import only)
import er003_key_words_gloss_alignment as ga           # noqa: E402
import er009_n1_routing_governance_10_actual_model_cost as pricing   # noqa: E402
import er003_v1_b1_scaffold_01_generate as b1s         # noqa: E402
import er112_kp_gm_kpset_02 as K                        # noqa: E402

LUNA = kx.MODEL
SOL = "gpt-6.1-sol"
_lock = threading.Lock()

HARD20 = ["draw a line", "pull someone under", "sentence someone to death", "shine a light on", "reach for someone's wallet", "fire the starting gun",
          "Carry the Load", "brace yourself for", "apply one's findings", "refueling support", "execution bell", "leap into action", "take the wheel",
          "bring in", "hold on", "letter of introduction", "on the throne", "off the hook", "turn on its head", "jump to conclusions"]
PRE_A1_DROP = {"draw that line", "pull him under", "pulled him under", "sentence him to death", "reach for one's wallet", "brace oneself for", "jump to that conclusion",
               "turned on its head", "apply its findings", "carry the load"}


def kpset():
    sys.path.insert(0, str(RD))
    import kp_probe_03 as P
    P.KEYS.append("sentence someone to death")
    hard, miss = P.load_kps()
    pool = K.build()
    for k in ["on the throne", "off the hook", "turn on its head", "jump to conclusions", "fire the starting gun"]:
        hard[pool[k.lower()]["key"]] = pool[k.lower()]
    hard = {k.lower(): dict(v, family=v.get("family") or ("Z" if "er026" in (v.get("run") or "") or "family_z" in (v.get("run") or "") else "X")) for k, v in hard.items()}
    assert set(x.lower() for x in HARD20) <= set(hard), set(x.lower() for x in HARD20) - set(hard)
    hard = {k: hard[k] for k in [x.lower() for x in HARD20]}
    normal = [v for k, v in sorted(pool.items()) if k not in hard and k not in PRE_A1_DROP]
    rnd = random.Random(7)
    X = [v for v in normal if v["family"] == "X"]; Z = [v for v in normal if v["family"] == "Z"]
    rnd.shuffle(X); rnd.shuffle(Z)
    nz = min(len(Z), 15)
    sel = X[:55 - nz] + Z[:nz]
    sel.sort(key=lambda v: v["key"].lower())
    allkp = {}
    for k, v in hard.items():
        allkp[k] = dict(v, key=v["key"] if v["key"].lower() == k else v["key"], tier="hard")
    for v in sel:
        allkp[v["key"].lower()] = dict(v, tier="normal")
    return allkp


def stop():
    return any(p.exists() for p in STOP_PATHS)


def total():
    if not LEDGER.exists():
        return 0.0
    t = 0.0
    for l in LEDGER.read_text(encoding="utf-8").splitlines():
        if l.strip():
            try:
                t += json.loads(l).get("cost_jpy", 0)
            except ValueError:
                pass   # 他processが書込み中の行(読取競合)。次回集計で拾う
    return t


def _append_line(path, rec):
    """複数processからの追記で行が交錯しないよう、1行を単一のos.writeで書く。"""
    fd = os.open(str(path), os.O_WRONLY | os.O_APPEND | os.O_CREAT)
    try:
        os.write(fd, (json.dumps(rec, ensure_ascii=False) + chr(10)).encode("utf-8"))
    finally:
        os.close(fd)


def ledger_add(rec):
    with _lock:
        LEDGER.parent.mkdir(parents=True, exist_ok=True)
        _append_line(LEDGER, rec)


def res_add(rec):
    with _lock:
        _append_line(RES, rec)


def load_res():
    d = {}
    if RES.exists():
        for l in RES.read_text(encoding="utf-8").splitlines():
            if l.strip():
                try:
                    r = json.loads(l)
                except ValueError:
                    continue
                d[(r["arm"], r["key"], r["rep"])] = r
    return d


_client = None


def client():
    global _client
    if _client is None:
        _client = b1s.get_client()
    return _client


def cost_of(r, model):
    u = kx._usage_dict(r.usage)
    c = pricing.cost_jpy_for_call("openai", r.model or model, u.get("input_tokens"), u.get("cached_input_tokens"), u.get("output_tokens"))
    return c, u


def art_id(kp):
    return hashlib.sha256(kp["article"].encode("utf-8")).hexdigest()[:10]



# ---------------------------------------------------------------- Std gloss arms
STD_NORMAL = ["a sense of occasion", "behind the scenes", "give way", "keep someone company", "pump one's fist", "think up"]   # 通常KP6件(X4/Z2)


def std_set(A):
    return {k: v for k, v in A.items() if v["tier"] == "hard" or k in STD_NORMAL}


G2_BLOCK = (
    "【語義の決め方(この項目のjapanese_glossを書く前に、次の順で必ず行う)】\n"
    "1. usage_sentence: 【記事本文】のうち、key_phraseが使われている文を1つ、そのまま引用する。\n"
    "2. usage_type: その文での用法を literal(字義どおり) / figurative(慣用・比喩) / phrasal(句動詞・コロケーション) / term(名詞句・用語) から選ぶ。\n"
    "3. core_sense_en: その用法でkey_phrase全体が表す『中心義』を英語1文で書く。記事固有の固有名詞・数値・状況・条件を入れず、別の場面でも通用する形にする。"
    "ただし本文の用法の意味から離れた一般義へ逃げてはならない。\n"
    "4. japanese_gloss: core_sense_enに従って書く。慣用・比喩はフレーズ全体の意味にし、語ごとの直訳にしない。意味は1つに絞る。\n\n")

G3_BLOCK = (
    "【日本語グロスの作り方(新規生成の項目。japanese_glossを書く前に、次の順で必ず行う)】\n"
    "1. candidates: key_phrase全体の意味を表す日本語の案を2〜3案、書く。案は次の優先順で作る: "
    "(a)英和辞典に載っている定訳、(b)その意味に対応する日本語の慣用句・定型表現があればそれ、"
    "(c)定訳も対応する慣用句も無い場合は、中心義を平易な日本語で言い換えたもの。語ごとの直訳・字義訳は案にしない。\n"
    "2. japanese_gloss: candidatesのうち、日本語学習者が聞いてすぐ意味が分かり、key_phrase全体の意味と過不足なく一致する案を1つ選んで書く"
    "(意味は1つに絞り、複数の訳を並べない)。\n\n")


def _schema_with(props_front, required_front, name):
    s = copy.deepcopy(ga.GLOSS_ALIGNMENT_JSON_SCHEMA)
    it = s["schema"]["properties"]["items"]["items"]
    props = {"rank": it["properties"]["rank"]}
    props.update(props_front)
    props.update({k: v for k, v in it["properties"].items() if k != "rank"})
    it["properties"] = props
    it["required"] = ["rank"] + required_front + [r for r in it["required"] if r != "rank"]
    s["name"] = name
    return s


def g2_schema():
    return _schema_with({"usage_sentence": {"type": "string"}, "usage_type": {"type": "string", "enum": ["literal", "figurative", "phrasal", "term"]},
                         "core_sense_en": {"type": "string"}}, ["usage_sentence", "usage_type", "core_sense_en"], "kp_gloss_g2_trial02")


def g3_schema():
    return _schema_with({"candidates": {"type": "array", "items": {"type": "string"}, "minItems": 2, "maxItems": 3}}, ["candidates"], "kp_gloss_g3_trial02")


def gloss_call(base_arm, kps, model):
    tgt = [{"rank": i + 1, "key_phrase": kp["key"], "display_phrase": kp["display"], "japanese_gloss": None, "source_sentence": kp["sent"],
            "fulltext_source_ref": "fulltext_exact_v1"} for i, kp in enumerate(kps)]
    msg = ga.build_user_message_corrected(tgt, kps[0]["article"])
    schema = ga.GLOSS_ALIGNMENT_JSON_SCHEMA
    anchor = "【日本語グロスの規則(承認済み選定Promptと同一)】"
    assert anchor in msg
    if base_arm == "G2":
        msg = msg.replace(anchor, G2_BLOCK + anchor, 1); schema = g2_schema()
    elif base_arm == "G3":
        msg = msg.replace(anchor, G3_BLOCK + anchor, 1); schema = g3_schema()
    r = client().responses.create(model=model, reasoning={"effort": "high"}, text={"format": {"type": "json_schema", **schema}},
                                  input=[{"role": "developer", "content": ga.DEVELOPER_MESSAGE}, {"role": "user", "content": msg}])
    c, u = cost_of(r, model)
    items = json.loads(r.output_text)["items"]
    return items, c, u, r.output_text


def run_gloss(arm, reps, A, only=None, cap=CAP_JPY):
    base = arm.replace("sol", "")
    model = SOL if arm.endswith("sol") else LUNA
    S = std_set(A)
    if only:
        S = {k: v for k, v in S.items() if k in only}
    groups = {}
    for k, kp in S.items():
        groups.setdefault(art_id(kp), []).append(kp)
    done = load_res()
    jobs = [(rep, g) for rep in reps for g in groups.values() if any((arm, kp["key"].lower(), rep) not in done for kp in g)]
    print(arm, "gloss jobs", len(jobs), flush=True)

    def w(j):
        rep, g = j
        if stop() or total() >= cap:
            return ("SKIP", rep, g[0]["key"])
        items, c, u, raw = gloss_call(base, g, model)
        ledger_add(dict(kind="gloss", arm=arm, model=model, keys=[x["key"] for x in g], rep=rep, usage=u, cost_jpy=round(c, 5), ts=time.strftime("%Y-%m-%dT%H:%M:%S")))
        by = {it["rank"]: it for it in items}
        for i, kp in enumerate(g):
            it = by.get(i + 1) or {}
            res_add(dict(arm=arm, key=kp["key"].lower(), rep=rep, kind="G", sent=kp["sent"], gloss=it.get("japanese_gloss"), usage_type=it.get("usage_type"),
                         core_sense=it.get("core_sense_en"), candidates=it.get("candidates"), call_cost_jpy=round(c, 5), n_in_call=len(g)))
        return (arm, rep, [x["key"] for x in g], round(c, 4))
    with ThreadPoolExecutor(6) as ex:
        for f in as_completed([ex.submit(w, j) for j in jobs]):
            print(f.result(), "cum=%.3f" % total(), flush=True)


# ---------------------------------------------------------------- Adv explanation arms
RULE_E1C = ("- First state the core sense of the phrase in core_sense (a general sense that works in any context; do not include details specific to this story), "
            "then write english_explanation from that core sense.\n")
RULE_E4 = ("- First decide how the phrase is used in the source sentence (usage_type: literal / figurative / phrasal / term), then state its core sense in core_sense "
           "(general, no story-specific details), then write english_explanation from that core sense.\n")
_REF_ROW = re.compile(r"   japanese_reference_meaning[^\n]*\n")
_REF_RULE = ("- Do not just translate the Japanese reference meaning word-for-word.\n"
             "  Write a natural English explanation of the same meaning.\n")


def expl_schema(arm):
    props = {"phrase": {"type": "string"}}
    if arm == "E4":
        props["usage_type"] = {"type": "string", "enum": ["literal", "figurative", "phrasal", "term"]}
    if arm in ("E4", "E1c"):
        props["core_sense"] = {"type": "string"}
    props["english_explanation"] = {"type": "string"}
    return {"name": "kp_expl_" + arm.lower() + "_trial02", "strict": True, "schema": {"type": "object", "properties": {"explanations": {"type": "array", "items": {
        "type": "object", "properties": props, "required": list(props), "additionalProperties": False}}}, "required": ["explanations"], "additionalProperties": False}}


def expl_message(arm, kp, gloss):
    msg = kx.build_explanation_user_message([{"display_phrase": kp["key"], "source_sentence": kp["sent"], "japanese_gloss": gloss or "x"}])
    if arm == "E0":
        return msg
    m2 = _REF_ROW.sub("", msg)
    assert m2 != msg
    assert _REF_RULE in m2
    m2 = m2.replace(_REF_RULE, "", 1)
    assert "japanese" not in m2.lower()
    rule = RULE_E4 if arm == "E4" else RULE_E1C if arm == "E1c" else ""
    if rule:
        assert "\nKey Phrases:\n" in m2
        m2 = m2.replace("\nKey Phrases:\n", rule + "\nKey Phrases:\n", 1)
    return m2


def expl_call(arm, kp, gloss):
    msg = expl_message(arm, kp, gloss)
    r = client().responses.create(model=LUNA, reasoning={"effort": kx.REASONING_EFFORT}, text={"format": {"type": "json_schema", **expl_schema(arm)}},
                                  input=[{"role": "developer", "content": kx.DEVELOPER_MESSAGE}, {"role": "user", "content": msg}])
    c, u = cost_of(r, LUNA)
    x = json.loads(r.output_text)["explanations"][0]
    return x, c, u, r.output_text


def run_expl(arm, reps, A, keys=None, gloss_arm=None, cap=CAP_JPY):
    """arm: E0/E1/E1c/E4。E0はgloss_arm(G0等)の出力を入力にし、結果arm名=E0@G0。"""
    res = load_res()
    out_arm = arm if arm != "E0" else "E0@" + gloss_arm
    jobs = []
    for k, kp in A.items():
        if keys and k not in keys:
            continue
        for rep in reps:
            if (out_arm, k, rep) in res:
                continue
            g = None
            if arm == "E0" and gloss_arm == "prod":
                g = kp.get("gloss")
                if not g:
                    continue
            elif arm == "E0":
                gr = res.get((gloss_arm, k, rep)) or res.get((gloss_arm, k, 1))
                if not gr or not gr.get("gloss"):
                    continue
                g = gr["gloss"]
            jobs.append((k, kp, rep, g))
    print(out_arm, "expl jobs", len(jobs), flush=True)

    def w(j):
        k, kp, rep, g = j
        if stop() or total() >= cap:
            return ("SKIP", k, rep)
        x, c, u, raw = expl_call(arm, kp, g)
        ledger_add(dict(kind="expl", arm=out_arm, key=k, rep=rep, usage=u, cost_jpy=round(c, 5), ts=time.strftime("%Y-%m-%dT%H:%M:%S")))
        res_add(dict(arm=out_arm, key=k, rep=rep, kind="E", sent=kp["sent"], gloss_in=g, text=x["english_explanation"], usage_type=x.get("usage_type"),
                     core_sense=x.get("core_sense"), raw=raw, call_cost_jpy=round(c, 5)))
        return (out_arm, k, rep, round(c, 4))
    with ThreadPoolExecutor(6) as ex:
        for f in as_completed([ex.submit(w, j) for j in jobs]):
            print(f.result(), "cum=%.3f" % total(), flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("--arm", default="")
    ap.add_argument("--reps", default="1")
    ap.add_argument("--keys", default="")
    ap.add_argument("--gloss-arm", default="G0")
    ap.add_argument("--set", default="all")
    ap.add_argument("--cap", type=float, default=CAP_JPY)
    a = ap.parse_args()
    if a.cmd == "set":
        A = kpset()
        import collections
        print(len(A), collections.Counter((v["tier"], v["family"]) for v in A.values()))
        for k, v in A.items():
            print(v["tier"], v["family"], "|", v["key"], "|", v["sent"][:90])

    reps = [int(x) for x in a.reps.split(",")]
    keys = [x.strip().lower() for x in a.keys.split("|") if x.strip()] or None
    if a.cmd == "gloss":
        run_gloss(a.arm, reps, kpset(), only=keys, cap=a.cap)
    elif a.cmd == "expl":
        A = kpset()
        if a.set == "hard":
            A = {k: v for k, v in A.items() if v["tier"] == "hard"}
        elif a.set == "normal":
            A = {k: v for k, v in A.items() if v["tier"] == "normal"}
        elif a.set == "std":
            A = std_set(A)
        run_expl(a.arm, reps, A, keys=keys, gloss_arm=a.gloss_arm, cap=a.cap)
