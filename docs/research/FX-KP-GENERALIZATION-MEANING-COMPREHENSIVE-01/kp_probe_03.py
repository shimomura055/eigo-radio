# -*- coding: utf-8 -*-
# ROOT_CAUSE_02 原因切り分けprobe-03(DEV専用・Production/Prompt不触。Prompt案の最終化ではなく因果の切り分けが目的)
# 問い: (H1)Adv説明は日本語参考意味(gloss)から狭さ/逐語を輸入するか (H2)文脈量(1文 vs 全文)の効果
#       (H3)『本文での用法を特定→中心義(英語1文)を先に決める』構造(sense-first)はStd/Advを安定させるか
#       (H4)gloss Promptの『すべての語を反映』句の除去でStd逐語が減るか
# arms: G0=現行gloss / G1=G0から『(目的語・補語・修飾語を含むすべての語)』除去 / G2=sense-first(usage_sentence,usage_type,core_sense_en→gloss)
#       E0=現行説明(1文+G0 gloss) / E1=1文のみ(gloss無) / E2=1文+gloss+全文 / E3=1文+G2 gloss+G2 core_sense_en
import json, os, sys, re, time, threading, hashlib, glob
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\Users\tensh\eigo-radio"); os.chdir(ROOT); sys.path.insert(0, str(ROOT))
D = ROOT / "docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01"
LEDGER = D / "kp_probe_03_paid_calls.jsonl"; RES = D / "kp_probe_03_results.jsonl"
CAP = 14.0   # 委任_06 上限15円の内数(安全マージン)
import er019_family_x_kp_explanation_01 as kx
import er003_key_words_gloss_alignment as ga
import er009_n1_routing_governance_10_actual_model_cost as pricing
import er003_v1_b1_scaffold_01_generate as b1s
MODEL = kx.MODEL
_lock = threading.Lock()
KEYS = ["draw a line", "pull someone under", "shine a light on", "reach for someone's wallet", "Carry the Load", "brace yourself for",
        "apply one's findings", "refueling support", "execution bell", "leap into action", "take the wheel", "bring in", "hold on", "letter of introduction"]


def total():
    if not LEDGER.exists():
        return 0.0
    return sum(json.loads(l).get("cost_jpy", 0) for l in LEDGER.read_text(encoding="utf-8").splitlines() if l.strip())


def stop():
    return any(p.exists() for p in (D / "STOP", D / "STOP_ALL", ROOT / "er026_output/family_z_production_e2e_01/STOP_ALL"))


def article_of(run, sentence):
    for lv in ("b1b", "a2"):
        p = ROOT / run / lv / "key_phrases" / "gloss_alignment_prompt.txt"
        if p.exists():
            t = p.read_text(encoding="utf-8")
            if "【記事本文(参考)】\n" in t:
                a = t.split("【記事本文(参考)】\n", 1)[1]
                if sentence[:40] in a.replace(chr(0x2019), "'"):
                    return a
        p = ROOT / run / lv / "key_phrases" / "canonicalization_prompt.txt"
        if p.exists():
            t = p.read_text(encoding="utf-8")
            m = "【記事本文(参考、文脈確認用)】\n"
            if m in t:
                a = t.split(m, 1)[1].split("\n\n【Key Phrase候補", 1)[0]
                if sentence[:40] in a.replace(chr(0x2019), "'"):
                    return a
    return None


def load_kps():
    units = {u["unit_id"]: u for u in json.load(open(ROOT / "er112_output/kp_gm_trial_01/inputs/units.json", encoding="utf-8"))["units"]}
    a3 = json.load(open(ROOT / "er112_output/kp_gm_trial_01/a3_verify/units_a3verify.json", encoding="utf-8"))
    out = {}
    for f in glob.glob(str(ROOT / "er112_output/kp_gm_trial_01/runs/a1gE0/rep1/*/result.json")):
        r = json.load(open(f, encoding="utf-8"))
        for it in r.get("items") or []:
            if it["key_phrase"] in KEYS and it["key_phrase"] not in out:
                u = units[r["unit_id"]]
                out[it["key_phrase"]] = dict(key=it["key_phrase"], display=it["display_phrase"], sent=it["source_sentence"], article=u["article_text"], run=u["run"])
    for u in a3:
        for it in u["items"]:
            k = it["used_form"]
            if k in KEYS and k not in out:
                art = article_of(u["run"], it["source_sentence"])
                if art is None:
                    for uu in units.values():
                        if it["source_sentence"][:40] in uu["article_text"].replace(chr(0x2019), "'"):
                            art = uu["article_text"]
                            break
                out[k] = dict(key=k, display=it["display_phrase"], sent=it["source_sentence"], article=art, run=u["run"])
    miss = [k for k in KEYS if k not in out or not out[k]["article"]]
    return out, miss


G2_BLOCK = (
    "【語義の決め方(この項目のjapanese_glossを書く前に、次の順で必ず行う)】\n"
    "1. usage_sentence: 【記事本文】のうち、key_phraseが使われている文を1つ、そのまま引用する。\n"
    "2. usage_type: その文での用法を literal(字義どおり) / figurative(慣用・比喩) / phrasal(句動詞・コロケーション) / term(名詞句・用語) から選ぶ。\n"
    "3. core_sense_en: その用法でkey_phrase全体が表す『中心義』を英語1文で書く。記事固有の固有名詞・数値・状況・条件を入れず、別の場面でも通用する形にする。"
    "ただし本文の用法の意味から離れた一般義へ逃げてはならない。\n"
    "4. japanese_gloss: core_sense_enに従って書く。慣用・比喩はフレーズ全体の意味にし、語ごとの直訳にしない。意味は1つに絞る。\n\n")


def g2_schema():
    import copy
    s = copy.deepcopy(ga.GLOSS_ALIGNMENT_JSON_SCHEMA)
    it = s["schema"]["properties"]["items"]["items"]
    props = {"rank": it["properties"]["rank"],
             "usage_sentence": {"type": "string"},
             "usage_type": {"type": "string", "enum": ["literal", "figurative", "phrasal", "term"]},
             "core_sense_en": {"type": "string"}}
    props.update({k: v for k, v in it["properties"].items() if k != "rank"})
    it["properties"] = props
    it["required"] = ["rank", "usage_sentence", "usage_type", "core_sense_en"] + [r for r in it["required"] if r != "rank"]
    s["name"] = "key_phrase_gloss_sense_first_probe"
    return s


client = None


def cost_of(r):
    u = kx._usage_dict(r.usage)
    return pricing.cost_jpy_for_call("openai", r.model, u.get("input_tokens"), u.get("cached_input_tokens"), u.get("output_tokens")), u


def log_cost(rec):
    with _lock:
        with open(LEDGER, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def done_keys():
    return set(load_res())


def save(rec):
    with _lock:
        with open(RES, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def load_res():
    d = {}
    if RES.exists():
        for l in RES.read_text(encoding="utf-8").splitlines():
            if l.strip():
                r = json.loads(l)
                d[(r["arm"], r["key"], r["rep"])] = r
    return d


def gloss_call(arm, kp, rep):
    tgt = [{"rank": 1, "key_phrase": kp["key"], "display_phrase": kp["display"], "japanese_gloss": None, "source_sentence": kp["sent"],
            "fulltext_source_ref": "fulltext_exact_v1"}]
    msg = ga.build_user_message_corrected(tgt, kp["article"])
    schema = ga.GLOSS_ALIGNMENT_JSON_SCHEMA
    if arm == "G1":
        assert "(目的語・補語・修飾語を含むすべての語)" in msg
        msg = msg.replace("(目的語・補語・修飾語を含むすべての語)", "")
    elif arm == "G2":
        assert "【日本語グロスの規則(承認済み選定Promptと同一)】" in msg
        msg = msg.replace("【日本語グロスの規則(承認済み選定Promptと同一)】", G2_BLOCK + "【日本語グロスの規則(承認済み選定Promptと同一)】", 1)
        schema = g2_schema()
    r = client.responses.create(model=MODEL, reasoning={"effort": "high"}, text={"format": {"type": "json_schema", **schema}},
                                input=[{"role": "developer", "content": ga.DEVELOPER_MESSAGE}, {"role": "user", "content": msg}])
    c, u = cost_of(r)
    it = json.loads(r.output_text)["items"][0]
    return it, c, u


def expl_schema():
    return {"name": "kp_expl_probe", "strict": True, "schema": {"type": "object", "properties": {"explanations": {"type": "array", "items": {
        "type": "object", "properties": {"phrase": {"type": "string"}, "english_explanation": {"type": "string"}},
        "required": ["phrase", "english_explanation"], "additionalProperties": False}}}, "required": ["explanations"], "additionalProperties": False}}


def expl_call(arm, kp, rep, gloss, sense):
    item = {"display_phrase": kp["key"], "source_sentence": kp["sent"], "japanese_gloss": gloss}
    msg = kx.build_explanation_user_message([item])
    if arm == "E1":
        msg2 = re.sub(r"   japanese_reference_meaning[^\n]*\n", "", msg)
        assert msg2 != msg
        msg = msg2
    elif arm == "E2":
        msg = msg.replace("\nReturn JSON only", "\nFull article (for context):\n" + kp["article"] + "\n\nReturn JSON only", 1)
    elif arm == "E3":
        add = ('   central_sense (fixed earlier from the whole article; base your explanation on this sense, '
               'rewritten as ONE plain sentence): "%s"\n' % sense)
        msg = msg.replace('\nReturn JSON only', add + '\nReturn JSON only', 1)
    r = client.responses.create(model=MODEL, reasoning={"effort": kx.REASONING_EFFORT}, text={"format": {"type": "json_schema", **expl_schema()}},
                                input=[{"role": "developer", "content": kx.DEVELOPER_MESSAGE}, {"role": "user", "content": msg}])
    c, u = cost_of(r)
    t = json.loads(r.output_text)["explanations"][0]["english_explanation"]
    return t, c, u, msg


def run_g(arms, reps, kps):
    done = done_keys()
    jobs = []
    for arm in arms:
        for rep in reps:
            for k, kp in kps.items():
                if (arm, k, rep) not in done:
                    jobs.append((arm, k, rep, kp))
    print("G jobs", len(jobs), flush=True)

    def w(j):
        arm, k, rep, kp = j
        if stop() or total() >= CAP:
            return ("SKIP", arm, k, rep)
        it, c, u = gloss_call(arm, kp, rep)
        log_cost(dict(kind="gloss", arm=arm, key=k, rep=rep, usage=u, cost_jpy=round(c, 5)))
        save(dict(arm=arm, key=k, rep=rep, kind="G", gloss=it["japanese_gloss"], sense=it.get("core_sense_en"), usage_type=it.get("usage_type"),
                  usage_sentence=it.get("usage_sentence"), reasoning=it.get("reasoning"), qa=it.get("qa_reflects_all_key_phrase_words")))
        return (arm, k, rep, round(c, 4))
    with ThreadPoolExecutor(6) as ex:
        for f in as_completed([ex.submit(w, j) for j in jobs]):
            print(f.result(), "cum=%.3f" % total(), flush=True)


def run_e(arms, reps, kps):
    res = load_res()
    done = set(res)
    jobs = []
    for arm in arms:
        for rep in reps:
            for k, kp in kps.items():
                if (arm, k, rep) in done:
                    continue
                if arm == "E3":
                    g = res.get(("G2", k, rep))
                    if not g:
                        continue
                    jobs.append((arm, k, rep, kp, g["gloss"], g["sense"]))
                else:
                    g = res.get(("G0", k, rep))
                    if not g:
                        continue
                    jobs.append((arm, k, rep, kp, g["gloss"], None))
    print("E jobs", len(jobs), flush=True)

    def w(j):
        arm, k, rep, kp, gloss, sense = j
        if stop() or total() >= CAP:
            return ("SKIP", arm, k, rep)
        t, c, u, msg = expl_call(arm, kp, rep, gloss, sense)
        log_cost(dict(kind="expl", arm=arm, key=k, rep=rep, usage=u, cost_jpy=round(c, 5)))
        save(dict(arm=arm, key=k, rep=rep, kind="E", sent=kp["sent"], gloss_in=(None if arm == "E1" else gloss), sense_in=sense, text=t))
        return (arm, k, rep, round(c, 4))
    with ThreadPoolExecutor(6) as ex:
        for f in as_completed([ex.submit(w, j) for j in jobs]):
            print(f.result(), "cum=%.3f" % total(), flush=True)


if __name__ == "__main__":
    kps, miss = load_kps()
    if sys.argv[1] == "prep":
        print("found", len(kps), "missing/noarticle", miss)
        for k, v in kps.items():
            print(k, "|", v["display"], "|", v["sent"][:70], "| art", len(v["article"] or ""))
        sys.exit(0)
    assert not miss, miss
    client = b1s.get_client()
    if sys.argv[1] == "g":
        run_g(sys.argv[2].split(","), [int(x) for x in sys.argv[3].split(",")], kps)
    elif sys.argv[1] == "e":
        run_e(sys.argv[2].split(","), [int(x) for x in sys.argv[3].split(",")], kps)
