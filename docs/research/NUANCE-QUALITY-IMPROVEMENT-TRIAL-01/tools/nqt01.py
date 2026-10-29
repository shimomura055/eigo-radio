# NUANCE-QUALITY-IMPROVEMENT-TRIAL-01 委任_01: DEV/Trial専用。Production Prompt/関数/runnerは編集しない。
# er134は「入力組立・QA Gate(run_candidate内のparse/quote/structural/judge/decide)の参考実行」のためread-only呼出のみ(Production出力・状態は書かない)。
# 使い方: py nqt01.py dry | NQT_PAID=1 py nqt01.py gen [cell ...]   (cell = <target>_<std|adv>)
import sys, os, json, time, threading, importlib.util, hashlib
BASE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.abspath(os.path.join(BASE, "..")); ROOT = os.path.abspath(os.path.join(BASE, "..", "..", "..", ".."))
sys.path.insert(0, ROOT)
import er134_nuance_explanation_01 as er
import er119_kp_human_review_01 as rv
import er121_family_y_structure_01 as ys
CAP_JPY = 40.0
ODIR = os.path.join(OUT, "out"); USAGE_LOG = os.path.join(ODIR, "usage_log.jsonl")
MODEL = "gpt-6-luna"   # 現行Production route (er006_model_routing_contract_01.py:50 SUPPORT_MODEL)
_lock = threading.Lock()
_v = importlib.util.spec_from_file_location("v02a", os.path.join(ROOT, "docs/research/NUANCE-EXPLANATION-PRODUCTION-WIRING-01/tools/nuance_v3_verify_02a.py"))
v02a = importlib.util.module_from_spec(_v); _v.loader.exec_module(v02a)

YS = "er121_output/family_y_production_01/surname_choice/run_02"
def _rj(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f: return json.load(f)

def build_inputs_for(cell, T):
    t, lv = cell.rsplit("_", 1); lvk = "a2" if lv == "std" else "b1b"
    if t == "y_surname":
        kp_dir = os.path.join(ROOT, YS, "key_phrases", lvk)
        sd = os.path.join(ROOT, YS, "a2/study_text" if lvk == "a2" else "study_text")
        text = open(os.path.join(ROOT, YS, "translate", f"{lvk}.md"), encoding="utf-8").read()
        paras = ys.canonical_body(text).split("\n\n")
        return er.build_inputs(family="y", article_id=f"family_y_surname_choice_{lvk}", title="When the husband takes the wife's name: voices", level=lvk, paragraphs=paras,
                               kp_cands=rv.load_candidates(kp_dir), grammar_items=er.grammar_items_of(sd))
    inp, _ = v02a.build(f"{t}_{lv}", T); return inp

CELLS = [f"{t}_{l}" for t in ("y_surname", "ai_island", "tth", "y_redelivery") for l in ("std", "adv")]

# ---------------- 改善版Prompt (Trial専用) ----------------
MARK = "# 手順(内部で考え、出力は最後のJSONのみ)"
NEW_TAIL = """# 解説の作り方(品質改善の中核。explanation_ja等を書くときの方針)
目的: 辞書の訳語や言い換えでは得られない「使い分け」「文脈による意味・印象の変化」を、学習者が具体的な英文の比較で実感できる解説にする。「〜という意味」「〜を示す」といった意味の言い換えの繰り返しは不可。
## 解説タイプを焦点に応じて選ぶ(形式は固定しない)
- comparison型(比較が有効な場合): 本文の1文を土台に、焦点の要素だけを変えた似た英文を並べ、各訳と「何がどう違うか」を示す。並べる英文は2〜4個(本文の文そのものを必ず1個含める。個数を3に揃える必要はない)。条件: (a)本文の文の最小限の書き換えで、焦点の要素以外は同一 (b)すべて実際に使われる自然な英語 (c)本文にない人物・事実・場面を持ち込まない (d)不自然・不正確・ほぼ同義で差が説明できない文は入れない (e)各訳は英語の違いが日本語に反映されるよう訳し分ける。
- context型(比較が不自然・不正確になる/適さない場合): comparisonsは空配列にし、本文の場面・話し手の意図・その表現が生む効果、必要なら同じ表現が別の文脈で変わる例(1つ。本文に無い例であることを明示)で、文脈による含みを具体的に説明する。
- 比較を無理に作らない。自然で正確な比較が作れないなら context型にするか、候補自体を0件にする。
## 「ここが重要」(explanation_ja)
- 比較または文脈の説明を踏まえ、学習者にとっての新しい発見を1〜2文で述べる(例: 日本語訳から想像する意味と、この文脈での実際の働きのずれ)。comparisonsの内容は繰り返さず、そこから導かれる要点と使いどころを書く。
- 全体で{explen}。
## レベル差
- Standard: 比較の英文はA2〜B1語彙・短く単純に。説明は平易な日本語。比較文は2〜3個。
- Advanced: B1〜B2。語感・丁寧さ・含みなど一段細かい差まで扱ってよい。比較文は2〜4個、または文脈の因果まで踏み込んだ説明。
## 正確性
- 事実(語義・用法)は一般に認められた英語の用法に基づき、断定しすぎない。ネイティブが不自然と感じる英文を例として出さない。

# 手順(内部で考え、出力は最後のJSONのみ)
1. 本文から上の焦点に当てはまる候補を最大4つ挙げ、それぞれの焦点を1行で書く。
2. 各候補を、Key Phrase・Word全件および文法コーナー候補との照合と入れ替えテストで確かめ、重複するものを外す。
3. 残った候補を学習価値の4条件で確かめる。さらに、その候補について自然で正確な比較文を作れるか(作れるならcomparison型)、作れなければ文脈の説明だけで学習者に新しい発見を与えられるか(context型)を確かめ、どちらでも価値が弱ければ除外する。
4. 4条件をすべて明確に満たす候補が1件以上あれば最も価値の高い1件を選ぶ。なければ0件にする。
{fixed}
# 出力(JSONのみ。前置き・コードフェンスなし。日本語は読みやすく)
{{
  "rejected_candidates": [{{"expression": "外した候補の英語表現", "focus": "焦点を日本語1行", "reason": "kp_word_overlap または grammar_overlap または low_value または not_nuance または too_basic または grammar_structure または no_natural_comparison または other", "note": "理由を一言"}}],
  "candidate": null または {{
    "expression": "解説の中心的な学習対象の英語表現。比較なら 'A vs B'",
    "focus": "学習上の焦点を日本語1行(40字程度まで)",
    "quote_en": "本文から一字一句そのまま引用した、連続する1〜2文(改変・要約・つなぎ合わせ・段落またぎ禁止)",
    "quote_ja": "quote_enの日本語訳",
    "point_ja": "ポイント。この表現が文脈でどう働くかを1文(60字程度まで)",
    "comparison_type": "comparison または context",
    "comparisons": [{{"label": "A", "en": "英文(本文の文そのものを1個含める)", "ja": "その日本語訳", "note_ja": "この文の含み・印象を1文", "is_text": false}}],
    "explanation_ja": "「ここが重要」にあたる要点解説(上の方針)",
    "differs_from_kp_word_ja": "Key Phrase・Word・文法候補のどれとも焦点が異なる理由を1文",
    "criteria_check": {{"context_specific": "本文の場面での含みを1文", "jp_pitfall": "日本語話者が取り違えやすい点を1文", "level_fit": "このレベルで価値がある理由を1文"}},
    "learning_value_self_rating": "high または mid(4条件がすべて明確ならhigh。1つでも弱いならmidとし、midの場合は候補にせず0件にする)",
    "learning_value_reason_ja": "なぜこのレベルの学習者に価値があるかを1文"
  }},
  "no_candidate_reason_ja": "candidateがnullのときだけ理由を1〜2文。候補ありならnull"
}}
- comparison_typeがcontextのときcomparisonsは空配列[]。comparisonのとき本文の文そのものをis_text=trueとして1個だけ含める(enはquote_enに含まれる文と一致)。

# 制約
- quote_enは本文に実在する文字列のみ。本文にない表現・事実・登場人物の言動を、本文の内容として書かない(比較文は『本文の文を変形した例』と分かる形で、本文の事実を増やさない)。
- 理解度チェック・クイズ・感想は書かない。
"""
EXPLEN = {"a2": "100〜240字", "b1b": "120〜300字"}
FIX_TMPL = "\n# 指定表現(比較実験のため固定)\n解説の中心的な学習対象(expression)は「{e}」に固定する。本文でこの表現を含む箇所から引用を選ぶ。他の候補を選ばない(上の4条件に照らして解説できない場合のみ0件)。\n"

def build_new_prompt(inputs, fixed_expr=None):
    cur = er.build_gen_prompt(inputs)
    head = cur[:cur.index(MARK)]
    fx = FIX_TMPL.format(e=fixed_expr) if fixed_expr else ""
    return head + NEW_TAIL.format(explen=EXPLEN[inputs["level"]], fixed=fx)

def build_fixed_current(inputs, fixed_expr):   # 現行Promptに同じ固定指示だけ加える(同一表現での現行版)
    cur = er.build_gen_prompt(inputs)
    return cur.replace(MARK, FIX_TMPL.format(e=fixed_expr) + "\n" + MARK, 1)

# ---------------- 呼出ラッパ ----------------
def spent():
    if not os.path.exists(USAGE_LOG): return 0.0
    with open(USAGE_LOG, encoding="utf-8") as f: return sum((json.loads(l).get("cost_jpy") or 0) for l in f if l.strip())

def make_fn(client, tag, override_prompt=None, max_out=9000):
    base = er._default_call_fn_factory(client, MODEL, max_out); cnt = [0]
    def fn(prompt):
        assert os.environ.get("NQT_PAID") == "1"
        with _lock:
            if spent() > CAP_JPY: raise RuntimeError("CAP refused")
        cnt[0] += 1; p = override_prompt if override_prompt is not None else prompt
        t0 = time.time(); text, model, usage, rid = base(p); el = round(time.time() - t0, 2)
        cost = er._cost_jpy(model, usage or {})
        os.makedirs(os.path.join(ODIR, "raw"), exist_ok=True)
        with open(os.path.join(ODIR, "raw", f"{tag}_{cnt[0]}.txt"), "w", encoding="utf-8", newline="\n") as f: f.write(text or "")
        with _lock, open(USAGE_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps({"tag": tag, "attempt": cnt[0], "model": model, "response_id": rid, "usage": usage, "cost_jpy": cost, "elapsed_sec": el, "prompt_sha256": hashlib.sha256(p.encode()).hexdigest()}, ensure_ascii=False) + "\n")
        return text, model, usage, rid
    return fn

def check_new_extras(doc, inputs):
    """改善版固有の機械チェック(comparisons構造・本文文の一致)。"""
    c = doc.get("candidate") or (doc.get("rejected_candidate_audit") or {}).get("candidate") or {}
    if not c: return []
    iss = []
    cmpv = c.get("comparisons")
    if not isinstance(cmpv, list): return ["comparisons_missing"]
    t = c.get("comparison_type")
    if t == "context" and cmpv: iss.append("context_but_comparisons_present")
    if t == "comparison":
        if not (2 <= len(cmpv) <= 4): iss.append(f"n_comparisons={len(cmpv)}")
        tx = [x for x in cmpv if x.get("is_text")]
        if len(tx) != 1: iss.append(f"n_is_text={len(tx)}")
        elif er._qn(tx[0].get("en", "")) not in er._qn(inputs["body"]): iss.append("is_text_not_in_body")
        for x in cmpv:
            if not all(isinstance(x.get(k), str) and x[k].strip() for k in ("label", "en", "ja", "note_ja")): iss.append("comparison_field_empty")
    if t not in ("comparison", "context"): iss.append(f"bad_type={t}")
    if not (isinstance(c.get("point_ja"), str) and c["point_ja"].strip()): iss.append("point_ja_missing")
    return iss

def _save(cell, cond, doc):
    json.dump(doc, open(os.path.join(ODIR, f"{cell}_{cond}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

def worker(client, cell, T, res):
    try:
        inputs = build_inputs_for(cell, T); r = {"cell": cell, "level": inputs["level"], "pool_n": len(inputs["pool"]), "grammar_n": len(inputs["grammar"])}
        def run(cond, prompt=None, jmax=5000):
            t0 = time.time()
            d = er.run_candidate(inputs, call_fn=make_fn(client, f"{cell}_{cond}", override_prompt=prompt), judge_fn=make_fn(client, f"{cell}_{cond}j", max_out=jmax))
            r[f"{cond}_wall_sec"] = round(time.time() - t0, 2)
            if cond != "CUR" and cond != "CURFIX": d["trial_extra_issues"] = check_new_extras(d, inputs)
            _save(cell, cond, d)
            r[cond] = {"status": d["status"], "reason": d.get("no_candidate_reason"), "usage": d["usage"], "extra_issues": d.get("trial_extra_issues")}
            return d
        cur = run("CUR")
        cexpr = (cur.get("candidate") or {}).get("expression")
        fixed = cexpr or {"y_surname_std": "at least a little", "y_surname_adv": "at least"}.get(cell)   # Y姓は現行Production候補と同じ表現に固定
        r["fixed_expr"] = fixed
        run("NEW", build_new_prompt(inputs))
        if fixed:
            run("NEWFIX", build_new_prompt(inputs, fixed))
            if not cexpr: run("CURFIX", build_fixed_current(inputs, fixed))
        res[cell] = r
    except Exception as e:
        import traceback; res[cell] = {"cell": cell, "error": repr(e), "tb": traceback.format_exc()}

def main():
    T = v02a.trial.load_targets(); cmd = sys.argv[1]
    if cmd == "dry":
        for c in CELLS:
            i = build_inputs_for(c, T); print(c, i["level"], "pool", len(i["pool"]), "prov", len(i["provisional"]), "gram", len(i["grammar"]), "text_sha", i["text_sha256"][:10], "new_chars", len(build_new_prompt(i)), "cur_chars", len(er.build_gen_prompt(i)))
        return
    os.makedirs(ODIR, exist_ok=True)
    client = v02a.get_client(); cells = sys.argv[2:] or CELLS; res = {}; ths = []
    for c in cells:
        th = threading.Thread(target=worker, args=(client, c, T, res)); th.start(); ths.append(th)
    for th in ths: th.join()
    p = os.path.join(ODIR, "summary_" + time.strftime("%H%M%S") + ".json"); json.dump(res, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "tb"} for k, v in res.items()}, ensure_ascii=False, indent=1)); print("spent_total_jpy", round(spent(), 4))
if __name__ == '__main__':
    main()
