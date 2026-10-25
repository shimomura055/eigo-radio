# FAMILY-Z-STUDY-TEXT-TRIAL-01 Trial-05専用script(DEV。Production非参照)。
# Part 2 Step A'(網羅タグ付け -> 候補ごとの絶対判定 -> コードの決定論規則)。Step B・Part 1/3/4はTrial-04を再利用。
#   py run_trial_05.py dry-run      # Prompt書出し・構成確認(API 0)
#   py run_trial_05.py selftest     # mock LLMで規則・組立を確認(API 0)
#   py run_trial_05.py send         # 有料。TRIAL05_PAID_APPROVED=1 必須。1 launchでStep A'全標本 -> Step B
import sys, os, json, re, hashlib, time, itertools, threading
BASE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(BASE, "..", "..", ".."))
sys.path.insert(0, BASE)
import run_trial_04 as t4

PAW_SRC = "er026_output/family_z_production_e2e_01/the_monkeys_paw/run_sf_prod_01/writer/r2.md"
WORKS5 = ["open_window", "ig_nobel", "gift", "paw"]
NSAMP = {"open_window": 6, "ig_nobel": 6, "gift": 3, "paw": 3}

def work_data5(work):
    if work != "paw": return t4.work_data(work)
    text = open(os.path.join(ROOT, PAW_SRC), encoding="utf-8").read()
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    assert paras[0] == "# The Last Wish"; body = paras[1:]
    numbered = "\n\n".join(f"[P{i}] {x}" for i, x in enumerate(body, 1))
    return dict(text=text, body=body, numbered=numbered, kp=[], label="The Last Wish(『猿の手』)")

STEPA5 = """あなたは英語読解指導の専門家です。下の英語本文(Advancedレベル)を、日本語話者の学習者(B1〜B2相当)の読解の観点で点検します。この工程の仕事は、(1)本文の全文を見て、構文上の特徴のある文を漏れなく洗い出すこと、(2)洗い出した文を1文ずつ絶対的に判定することです。解説文は書きません(解説は別の工程が行います)。

# 作品・レベル
- 作品: {label}
- レベル: Advanced

# 本文(段落番号[P1]〜[P{n}]は参照用。引用では番号を書かない)
{numbered}

# 手順
1. 本文を最初から最後まで、すべての文について、下の「価値のある特徴の分類」に該当するかを確認する。該当する文は、数に上限を設けず、すべてfeaturesに列挙する(1段落に複数あれば文ごとに列挙)。どの文にも該当しない段落は、段落番号をno_feature_parasに書く(featuresに載せた段落は書かない)。
2. featuresの各文を、その文だけを見て絶対的に判定する。本文中の他の文との比較や、何件選ぶかを考えて判定を調整してはならない。

# 価値のある特徴の分類(feature_classに書くコード)
- INV: 倒置。場所・方向・否定・時を表す副詞句が文頭に出て、動詞が主語の前に来る(例: Under the bed lay a small box. / Never had she seen such a place.)。伝達部の倒置(said Vera の型)は含まない。
- CLEFT: 疑似分裂文・分裂文(What … is …. / It is … that …. の型)。
- CMP: 比較の省略・倍数比較など、何と何を比べているか(比較の基準)が見えにくい比較。
- HEAVY: 主語が長い・重い。主語の中心から動詞までが離れている、または主語が節・長い句で、動詞を見つけにくい。
- POSTMOD: 名詞から離れた、または重なった後置修飾(後置の分詞句・関係節・前置詞句など)で、修飾先を取り違えやすい。
- FRONT: 文頭に置かれた修飾要素(分詞句・前置詞句・副詞節など)のために、主節の主語や動詞を取り違えやすい。
- APPOS: 同格・挿入・コンマで区切られた要素のため、構造が複数に読める。
- ELL: 省略(動詞・主語・語句の省略、断片文、並列での省略)で、補い方を取り違えやすい。
- SPEC: 特殊な文型(SVOC・二重目的語・使役/知覚動詞+目的語+補語など)で、語の働きを取り違えやすい。
- OTHER: 上記以外の構文上の特徴。other_descに短く書く。

# 基礎項目(これだけで説明が済む文は価値なしとして扱う。作品に関係なく共通)
命令文(命令文+and/orを含む)/ 基本的な接続(and・but・or・so・because・when・if・while・although)/ 前置詞句 / 分詞構文・付帯状況のwithの基本形 / 関係詞の基本用法(whose・関係副詞を含む)/ 基本時制・進行形・完了形・受動態 / 比較級・最上級・as…asの基本形 / 仮定法の基本形 / 動名詞主語の単純形 / the+形容詞 / 伝達部の倒置(said X)/ 疑問文・感嘆文・there is構文・It is…to…の基本形 / to不定詞・動名詞・分詞の基本用法。
- 基礎項目を含む文でも、上の「価値のある特徴の分類」に該当する特徴が文中にあれば、その特徴について判定する(basic_onlyはfalse)。分類に該当する特徴がないのに、基礎項目の「特殊な用法」「重要な表現効果」を理由に価値ありと判定してはならない。
- 基礎項目だけの文はfeaturesに載せなくてよい(載せる場合はtierをC、basic_onlyをtrueにする)。

# featuresの各項目の書き方
- para: 段落番号(例: "P4")。sentence: その文を本文から一字一句そのまま(逐語)。
- feature_class: 上のコード。
- misread_ja: 学習者がこの文の構造をどう取り違えうるかの具体例を日本語で。どの語を主語・動詞・修飾先と誤るか、または省略をどう補い誤るかを、本文の該当語句を引用して書く。構造の取り違えに限る。単語の意味が分からないこと(語彙の誤読)は書かない。具体的に書けない場合は空文字にする。
- misread_quote: 取り違えの起点になる本文中の語句を一字一句そのまま(1〜8語)。書けなければ空文字。
- correct_structure_ja: 正しい構造(主語・動詞・修飾関係)を短く。
- basic_only: この文の説明が上の基礎項目だけで済むならtrue、価値のある特徴の分類に該当する特徴があるならfalse。
- tier: A=構造を取り違えると文意が取れない、または大きく誤る読解上の難所 / B=構造に特徴はあるが、取り違えても大意は文脈からつかめる / C=基礎的で説明の価値が小さい。
- rank: tierがAの項目だけに、tier Aの項目同士の優先順位(1が最優先、整数、重複なし)。A以外はnull。
- construct_ja / points_ja / context_ja: tierがAでbasic_onlyがfalseの項目だけに書く(それ以外は空文字・空配列)。construct_ja=構文の名前(短く)。points_ja=解説で押さえるべき点(最大3つ、短く)。context_ja=その文の本文中での位置づけを1文で(本文に書かれた事実のみ。解釈や評価は書かない)。これらにはユーザー向け解説の材料になるため、難易度・誤解しやすさ・学習価値などの評価語を入れない。

# 出力(JSONオブジェクト1個のみ。前置き・後書き・コードフェンスなし)
{{
  "features": [
    {{"para": "P4", "sentence": "…", "feature_class": "INV", "other_desc": "", "misread_ja": "…", "misread_quote": "…", "correct_structure_ja": "…", "basic_only": false, "tier": "A", "rank": 1, "construct_ja": "…", "points_ja": ["…"], "context_ja": "…"}}
  ],
  "no_feature_paras": ["P1", "P2"]
}}
"""
def stepa5_prompt(d):
    return STEPA5.format(label=d["label"], n=len(d["body"]), numbered=d["numbered"])

# ---------- 決定論規則(LLMを使わない) ----------
def _as_bool(v):
    if isinstance(v, bool): return v
    return str(v).strip().lower() in ("true", "はい", "yes")
def parse_stepa5(txt, d, inp=None):
    m = re.search(r"\{.*\}", txt, re.S); j = json.loads(m.group(0))
    assert isinstance(j.get("features"), list) and isinstance(j.get("no_feature_paras"), list)
    seen = set(); feats = []
    for f in j["features"]:
        f = dict(f); f["resolve_ok"] = True
        try:
            verb, pi, a, b = t4.resolve_verbatim(d, f.get("para"), f.get("sentence", ""))
            f["sentence_llm_raw"] = f["sentence"]; f["sentence_replaced_by_body"] = (verb != f["sentence"]); f["sentence"] = verb
            f["prev"], f["next"] = t4.local_context(d, pi, a, b)
            if inp:
                for it in inp:
                    if t4._qn(it["sentence"]) == t4._qn(verb): f["ref_ja"] = it["sentence_ja"]
            q = (f.get("misread_quote") or "").strip()
            f["misread_quote_in_sentence"] = bool(q) and t4._qn(q) in t4._qn(verb)
        except AssertionError as e:
            f["resolve_ok"] = False; f["resolve_error"] = str(e)[:120]
        key = (f.get("para"), f.get("sentence"))
        if key in seen: f["duplicate"] = True
        seen.add(key); feats.append(f)
    j["features"] = feats
    covered = {f.get("para") for f in feats} | set(j["no_feature_paras"])
    j["uncovered_paras"] = [f"P{i}" for i in range(1, len(d["body"]) + 1) if f"P{i}" not in covered]
    return j
def is_eligible(f):
    """規則: tier A かつ 基礎のみでない かつ 構造取り違え欄が空でない(+文が本文に解決できる・重複でない)。"""
    return bool(f.get("resolve_ok") and not f.get("duplicate") and str(f.get("tier", "")).strip().upper() == "A"
                and not _as_bool(f.get("basic_only", True)) and str(f.get("misread_ja", "")).strip())
def _pnum(f): return int(re.sub(r"\D", "", f["para"]))
def _rank(f):
    try: return float(f.get("rank"))
    except (TypeError, ValueError): return 1e9
def select_rule(feats, k=2):
    el = sorted([f for f in feats if is_eligible(f)], key=lambda f: (_rank(f), _pnum(f)))
    return el[:k]
def to_selected(f):
    """Step B(Trial-04と同一Prompt)用の選定dict。材料欄が欠ければNone(記録のみ)。"""
    if not (f.get("construct_ja") and f.get("points_ja") and f.get("context_ja")): return None
    s = dict(para=f["para"], sentence=f["sentence"], construct_ja=f["construct_ja"], points_ja=list(f["points_ja"])[:3],
             context_ja=f["context_ja"], reason_dev=f"{f.get('feature_class')}: {f.get('misread_ja','')}", prev=f.get("prev", ""), next=f.get("next", ""))
    if f.get("ref_ja"): s["ref_ja"] = f["ref_ja"]
    return s
def sel_to_stepa(feats):
    fs = select_rule(feats)
    sel = [x for x in (to_selected(f) for f in fs) if x]
    return dict(selected=sel, selected_missing_fields=len(fs) - len(sel))

# ---------- (B)オフライン模擬(追加呼出なし。選定文の多数決はしない) ----------
def key_of(f): return (f["para"], f["sentence"])
def sim_B(samples, need=2, frac=None, k=2):
    """samples: parse_stepa5結果のリスト。層A適格が need 回以上(frac指定時は割合以上)の文を母集団に、適格標本のrank平均で最大k件。"""
    cnt = {}; ranks = {}; tierB = {}
    for j in samples:
        for f in j["features"]:
            if not f.get("resolve_ok") or f.get("duplicate"): continue
            if is_eligible(f): cnt[key_of(f)] = cnt.get(key_of(f), 0) + 1; ranks.setdefault(key_of(f), []).append(_rank(f))
            elif str(f.get("tier", "")).upper() == "B": tierB[key_of(f)] = tierB.get(key_of(f), 0) + 1
    thr = need if frac is None else frac * len(samples)
    pop = [x for x, c in cnt.items() if c >= thr - 1e-9]
    pop.sort(key=lambda x: (sum(ranks[x]) / len(ranks[x]), int(re.sub(r"\D", "", x[0]))))
    flagB = [x for x, c in tierB.items() if c >= 2] if not pop else []
    return dict(selected=pop[:k], population=pop, tierA_counts={f"{a}|{b[:40]}": c for (a, b), c in cnt.items()}, fable_report_tierB=flagB)

# ---------- 実行 ----------
_SPENT = {"jpy": 0.0}; _LOCK = threading.Lock(); CAP_A = 6.8; CAP_B = 7.2
def real_llm(prompt, tag):
    assert os.environ.get("TRIAL05_PAID_APPROVED") == "1", "paid call refused"
    cap = CAP_A if "_stepA5_" in tag else CAP_B
    with _LOCK: assert _SPENT["jpy"] < cap, ("cost cap reached; new calls refused", _SPENT, tag)
    from dotenv import load_dotenv; load_dotenv(os.path.join(ROOT, ".env"))
    from openai import OpenAI
    c = OpenAI(); t0 = time.time()
    r = c.responses.create(model="gpt-6-luna", input=[{"role": "user", "content": prompt}])
    el = time.time() - t0; u = r.usage
    cached = getattr(u.input_tokens_details, "cached_tokens", 0)
    usd = (u.input_tokens - cached) * 0.10 / 1e6 + cached * 0.01 / 1e6 + u.output_tokens * 0.50 / 1e6
    d = {"tag": tag, "model_requested": "gpt-6-luna", "model_actual": r.model, "response_id": r.id, "elapsed_sec": round(el, 1),
         "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(), "input_tokens": u.input_tokens, "cached_input_tokens": cached,
         "output_tokens": u.output_tokens, "reasoning_tokens": getattr(u.output_tokens_details, "reasoning_tokens", None),
         "cost_usd": round(usd, 6), "cost_jpy_at_160": round(usd * 160, 4)}
    json.dump(d, open(os.path.join(BASE, f"usage_{tag}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(os.path.join(BASE, f"_raw_{tag}.txt"), "w", encoding="utf-8", newline="\n").write(r.output_text)
    with _LOCK: _SPENT["jpy"] += d["cost_jpy_at_160"]
    return r.output_text, d

def run_stepa5(work, runid, llm):
    d = work_data5(work); inp = t4.load_inputs().get(work) if work != "paw" else None
    r = llm(stepa5_prompt(d), f"05_{runid}_stepA5_{work}")
    j = parse_stepa5(r[0], d, inp)
    j["rule_selected"] = sel_to_stepa(j["features"]); j["usage"] = r[1]
    open(os.path.join(BASE, f"OUTPUT_05_{work}_{runid}_STEPA_DEV.json"), "w", encoding="utf-8", newline="\n").write(json.dumps(j, ensure_ascii=False, indent=1))
    return j

def load_p1p34(work):
    """Trial-04 r1の再利用(無編集)。pawはPart 1/3/4なし。"""
    if work == "paw": return None, None
    p1 = t4.parse_p1(open(os.path.join(BASE, f"_raw_04a_r1_p1_{work}.txt"), encoding="utf-8").read())
    return p1, open(os.path.join(BASE, f"_raw_04_r1_p34_{work}.txt"), encoding="utf-8").read()

def assemble_user5(work, sel, stepb):
    p1, p34 = load_p1p34(work)
    if work == "paw":
        L = ["## Part 2. Grammar & Sentence Structure(ホールドアウト作品のためPart 2のみ)", ""]
        if not sel: L += [t4.ZERO_P2, ""]
        for i, s in enumerate(sel, 1): L += [f"### {i}. 対象となる本文英文", "", f"> {s['sentence']}", "", t4.bold_headings(stepb[i]), ""]
        return "\n".join(L)
    inp = t4.load_inputs()[work]
    return t4.assemble_user(inp, p1, {"selected": sel}, stepb, p34)

def run_stepb(work, tag, sel, llm):
    stepb = {}
    if sel:
        r = llm(t4.stepb_prompt(sel), f"05_{tag}_stepB_{work}")
        stepb = t4.parse_stepb(r[0], len(sel))
    user = assemble_user5(work, sel, stepb)
    open(os.path.join(BASE, f"OUTPUT_05_{work}_{tag}_USER.md"), "w", encoding="utf-8", newline="\n").write(user)
    return user

def consensus_selection(samples):
    b = sim_B(samples, frac=2 / 3); feats = {}
    for j in samples:
        for f in j["features"]:
            if f.get("resolve_ok") and is_eligible(f): feats.setdefault(key_of(f), f)
    return [x for x in (to_selected(feats[k]) for k in b["selected"]) if x]

def batch(llm):
    from concurrent.futures import ThreadPoolExecutor
    jobs = [(w, f"r{i}") for w in WORKS5 for i in range(1, NSAMP[w] + 1)]
    res = {}; errs = {}
    def one(w, r):
        try: res[(w, r)] = run_stepa5(w, r, llm)
        except Exception as e: errs[f"{w}_{r}"] = repr(e)[:300]
    with ThreadPoolExecutor(max_workers=9) as ex: list(ex.map(lambda x: one(*x), jobs))
    # Step B: r1の選定 と 全標本合意選定(異なる場合のみ)。自動再試行なし。
    bj = []
    for w in WORKS5:
        samples = [res[(w, f"r{i}")] for i in range(1, NSAMP[w] + 1) if (w, f"r{i}") in res]
        r1s = res[(w, "r1")]["rule_selected"]["selected"] if (w, "r1") in res else None
        if r1s is not None: bj.append((w, "r1", r1s))
        cons = consensus_selection(samples) if samples else []
        if cons and (r1s is None or [x["sentence"] for x in cons] != [x["sentence"] for x in r1s]): bj.append((w, "cons", cons))
    def two(w, tag, sel):
        try: run_stepb(w, tag, sel, llm)
        except Exception as e: errs[f"stepB_{w}_{tag}"] = repr(e)[:300]
    with ThreadPoolExecutor(max_workers=4) as ex: list(ex.map(lambda x: two(*x), bj))
    json.dump({"errors": errs, "spent_jpy": _SPENT["jpy"], "stepb_jobs": [(w, t, [s["para"] for s in sel]) for w, t, sel in bj]},
              open(os.path.join(BASE, "batch_05_result.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return errs

# ---------- dry-run / selftest ----------
def dry_run():
    out = {}
    for w in WORKS5:
        d = work_data5(w); p = stepa5_prompt(d)
        open(os.path.join(BASE, f"_prompt_05_{w}_stepA5.txt"), "w", encoding="utf-8", newline="\n").write(p)
        out[w] = dict(paras=len(d["body"]), prompt_chars=len(p), sha=hashlib.sha256(p.encode()).hexdigest()[:12])
    # 過剰適合防止: 指示部(本文を除く)に4作品の本文の文を例として含めない
    for w in WORKS5:
        p = open(os.path.join(BASE, f"_prompt_05_{w}_stepA5.txt"), encoding="utf-8").read()
        head = p[:p.index("# 本文")] + p[p.index("# 手順"):]
        for w2 in WORKS5:
            for s in t4._sents("\n\n".join(work_data5(w2)["body"])):
                if len(s) > 25: assert s not in head, ("example leaks work sentence", w2, s[:40])
    json.dump(out, open(os.path.join(BASE, "dryrun_05.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return out

def _mock_feat(d, para, cls, tier, rank, basic, misread="x"):
    s = t4._sents(d["body"][int(para[1:]) - 1])[0]
    return dict(para=para, sentence=s, feature_class=cls, other_desc="", misread_ja=misread, misread_quote=s.split()[0], correct_structure_ja="c", basic_only=basic,
                tier=tier, rank=rank, construct_ja="構文" if tier == "A" else "", points_ja=["p"] if tier == "A" else [], context_ja="ctx" if tier == "A" else "")
def selftest():
    d = work_data5("open_window")
    fs = [_mock_feat(d, "P21", "INV", "A", 1, False), _mock_feat(d, "P1", "OTHER", "A", 2, True), _mock_feat(d, "P23", "OTHER", "A", 3, False, misread=""),
          _mock_feat(d, "P29", "HEAVY", "A", 2, False), _mock_feat(d, "P5", "ELL", "B", None, False), _mock_feat(d, "P7", "ELL", "A", 4, False)]
    fs[-1]["sentence"] = "this sentence is not in the body at all"
    txt = json.dumps(dict(features=fs, no_feature_paras=["P2"]), ensure_ascii=False)
    j = parse_stepa5("前置き " + txt, d)
    sel = select_rule(j["features"])
    assert [f["para"] for f in sel] == ["P21", "P29"], sel          # 基礎のみ・misread空・解決不能は除外、rank順、最大2
    assert j["features"][-1]["resolve_ok"] is False
    assert sel_to_stepa(j["features"])["selected_missing_fields"] == 0
    assert "P3" in j["uncovered_paras"] and "P21" not in j["uncovered_paras"]
    z = parse_stepa5(json.dumps(dict(features=[], no_feature_paras=[])), d); assert select_rule(z["features"]) == []
    a = parse_stepa5(json.dumps(dict(features=[_mock_feat(d, "P21", "INV", "A", 1, False)], no_feature_paras=[])), d)
    b = parse_stepa5(json.dumps(dict(features=[_mock_feat(d, "P29", "HEAVY", "A", 1, False)], no_feature_paras=[])), d)
    c = parse_stepa5(json.dumps(dict(features=[_mock_feat(d, "P21", "INV", "A", 2, False), _mock_feat(d, "P29", "HEAVY", "A", 1, False)], no_feature_paras=[])), d)
    s = sim_B([a, b, c]); assert sorted(x[0] for x in s["selected"]) == ["P21", "P29"], s     # どちらも3回中2回
    s1 = sim_B([a, b, parse_stepa5(json.dumps(dict(features=[], no_feature_paras=[])), d)]); assert s1["selected"] == []   # 3回中1回のみ -> 母集団に入らない
    e = sim_B([a, parse_stepa5(json.dumps(dict(features=[], no_feature_paras=[])), d), parse_stepa5(json.dumps(dict(features=[], no_feature_paras=[])), d)])
    assert e["selected"] == []
    u = assemble_user5("paw", [to_selected(_mock_feat(work_data5("paw"), "P24", "INV", "A", 1, False))], {1: "**x**"}); assert "対象となる本文英文" in u
    assert assemble_user5("paw", [], {}).count(t4.ZERO_P2) == 1
    for w in ("open_window", "ig_nobel", "gift"):
        uu = assemble_user5(w, [to_selected(_mock_feat(work_data5(w), "P5", "INV", "A", 1, False))], {1: "**x**"}); assert "Part 3" in uu
    print("selftest OK")

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "dry-run": print(json.dumps(dry_run(), ensure_ascii=False, indent=1))
    elif cmd == "selftest": selftest()
    elif cmd == "send":
        t0 = time.time(); errs = batch(real_llm)
        open(os.path.join(BASE, "batch_05_elapsed.txt"), "w").write(str(round(time.time() - t0, 1)))
        print("done", errs, _SPENT)
