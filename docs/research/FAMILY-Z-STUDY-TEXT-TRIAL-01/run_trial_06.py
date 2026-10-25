# FAMILY-Z-STUDY-TEXT-TRIAL-01 Trial-06専用script(DEV。Production非参照)。
# Part 2 Step A''(全文タグ付け: 分類コード+misread_target/quote、tier/rank廃止) -> コードの決定論規則(2段クラス・同一クラス1件・中クラス追加条件) -> Step B。
# 根拠: OPUS_REVIEW_04.md(条件B)。基準: PREREGISTERED_CRITERIA_06.md(有料生成前commit)。
#   py run_trial_06.py dry-run          # Prompt書出し・例の本文非含有assert(API 0)
#   py run_trial_06.py selftest         # mock LLMで規則・予約方式費用ガード・組立を確認(API 0)
#   .venv\Scripts\python.exe run_trial_06.py send-a   # 有料(Step A'' 18 call)。TRIAL06_PAID_APPROVED=1 必須
#   .venv\Scripts\python.exe run_trial_06.py send-b   # 有料(Step B)。合格時のみ。TRIAL06_PAID_APPROVED=1 必須
import sys, os, json, re, hashlib, time, glob, threading
BASE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(BASE, "..", "..", ".."))
sys.path.insert(0, BASE)
import run_trial_04 as t4

FZ = "er026_output/family_z_production_e2e_01"
SRC6 = {"paw": (f"{FZ}/the_monkeys_paw/run_sf_prod_01/writer/r2.md", "The Last Wish(『猿の手』)"),
        "tth": (f"{FZ}/the_tell_tale_heart/run_sf_prod_01/writer/r2.md", "Listen Carefully(『告げ口心臓』)"),
        "promise": (f"{FZ}/after_twenty_years/run_sf_prod_01/writer/r2.md", "The Promise(『二十年後』)")}
WORKS6 = ["open_window", "ig_nobel", "gift", "paw", "tth", "promise"]
NSAMP = 3
NAME_JA = {"open_window": "開いた窓", "ig_nobel": "イグ・ノーベル賞2026", "gift": "賢者の贈り物", "paw": "猿の手(開発用)", "tth": "告げ口心臓(新ホールドアウト)", "promise": "二十年後(平易な本文)"}

def work_data6(work):
    if work not in SRC6: return t4.work_data(work)
    path, label = SRC6[work]
    text = open(os.path.join(ROOT, path), encoding="utf-8").read()
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    assert paras[0].startswith("# "); body = paras[1:]
    numbered = "\n\n".join(f"[P{i}] {x}" for i, x in enumerate(body, 1))
    return dict(text=text, body=body, numbered=numbered, kp=[], label=label)

# ---------- 分類(事前登録で固定。PREREGISTERED_CRITERIA_06 §1) ----------
STRONG = ["INV", "CLEFT", "CMP"]
MID = ["FRONT", "HEAVY", "POSTMOD", "SPEC", "ELL", "APPOS"]
PRIORITY = STRONG + MID                       # INV>CLEFT>CMP>FRONT>HEAVY>POSTMOD>SPEC>ELL>APPOS。OTHERは記録のみ
TARGETS = {"SUBJECT", "VERB", "MODIFIEE", "OMITTED"}

STEPA6 = """あなたは英語読解指導の専門家です。下の英語本文(Advancedレベル)を、日本語話者の学習者(B1〜B2相当)の読解の観点で点検します。この工程の仕事は、本文の全文を見て、構文上の特徴のある文に「分類コード」を付けて漏れなく洗い出すことです。どの文を解説するかの選択は、この工程では行いません(別の工程が決まった規則で行います)。解説文も書きません。

# 作品・レベル
- 作品: {label}
- レベル: Advanced

# 本文(段落番号[P1]〜[P{n}]は参照用。引用では番号を書かない)
{numbered}

# 手順
1. 本文を最初から最後まで、すべての文について、下の「分類コード」に該当する特徴があるかを確認する。該当する文は、数に上限を設けず、すべてfeaturesに列挙する(1段落に複数あれば文ごとに列挙)。どの文にも該当しない段落は、段落番号をno_feature_parasに書く(featuresに載せた段落は書かない)。
2. featuresの各文について、その文だけを見て、分類コードと、構造の取り違えの起点を答える。他の文との比較、どれが重要か、何件挙げるか、といった相対的な判断はしない。文の「難しさの程度」や「重要度」は答えない(分類と事実だけを答える)。

# 分類コード(feature_classに書く)
- INV: 倒置。場所・方向・否定・時を表す副詞句が文頭に出て、動詞が主語の前に来る(例: Under the bed lay a small box. / Never had she seen such a place.)。伝達部の倒置(said Vera の型)は含まない。
- CLEFT: 疑似分裂文・分裂文(例: What the committee needed was more time. / It was in March that the plan changed.)。
- CMP: 比較の基準(何と何を比べているか)が見えにくい比較。倍数比較・as以降の省略など(例: The new bridge is twice as long as the old one. / She earns three times what he does.)。
- FRONT: 文頭に置かれた修飾要素(分詞句・前置詞句・副詞節・形容詞句・as/thoughによる前置など)のために、主節の主語や動詞を取り違えやすい(例: Hard as it was to admit, she had been wrong.)。
- HEAVY: 主語が長い・重い。主語の中心から動詞までが離れている、または主語が節・長い句で、動詞を見つけにくい(例: The decision to postpone the vote until after the holidays surprised everyone.)。
- POSTMOD: 名詞から離れた、または重なった後置修飾(後置の分詞句・関係節・前置詞句など)で、修飾先を取り違えやすい(例: He found a letter on the table by the window addressed to his brother.)。
- SPEC: 目的語と補語の境界が見えにくい特殊な文型に限る。形式目的語it(例: She found it impossible to refuse such an offer.)、目的語が長いもの、wish+目的語+形容詞/副詞(例: I wish my brother here.)など。
- ELL: 前の文や前の部分から動詞・主語・比較の基準を補わないと構造が取れない省略(例: Tom likes tea, and Anna coffee.)。
- APPOS: 同格・挿入・コンマで区切られた要素のため、構造が複数に読める(例: My neighbour's daughter, a doctor in Leeds, called.)。
- OTHER: 上記以外の構文上の特徴。other_descに短く書く。

# 基礎項目(これだけで説明が済む文は価値なしとして扱い、basic_onlyをtrueにする。作品に関係なく共通)
命令文(命令文+and/orを含む)/ 基本的な接続(and・but・or・so・because・when・if・while・although)/ 前置詞句 / 分詞構文・付帯状況のwithの基本形 / 関係詞の基本用法(whose・関係副詞を含む)/ 基本時制・進行形・完了形・受動態 / 比較級・最上級・as…asの基本形 / 仮定法の基本形 / 動名詞主語の単純形 / the+形容詞 / 伝達部の倒置(said X)/ 伝達部(said X、he explained等)に付く同格・挿入 / 疑問文・感嘆文・there is構文・It is…to…の基本形 / to不定詞・動名詞・分詞の基本用法 / 使役動詞・知覚動詞+目的語+原形/分詞、keep/make/find+目的語+補語の基本形 / 会話の断片・間投詞・一語や短い語句だけの返答。
- 基礎項目を含む文でも、上の分類コードに該当する特徴が文中にあれば、その特徴について答える(basic_onlyはfalse)。分類コードに該当する特徴がないのに、基礎項目の「特殊な用法」「表現効果」を理由に分類してはならない。
- 基礎項目だけの文はfeaturesに載せなくてよい(載せる場合は、feature_classをOTHER、basic_onlyをtrueにし、材料欄は空にする)。

# featuresの各項目の書き方(各欄は短く)
- para: 段落番号(例: "P4")。sentence: その文を本文から一字一句そのまま(逐語。文頭・文末の引用符は書かなくてよい)。
- feature_class: 上のコード。
- misread_target: 学習者が構造を取り違える対象。SUBJECT(主語)/ VERB(動詞)/ MODIFIEE(修飾先)/ OMITTED(省略された語句の補い方)のいずれか1つ。取り違えの対象を具体的に挙げられない場合は空文字。
- misread_quote: 取り違えの起点になる本文中の語句を一字一句そのまま(1〜8語)。挙げられなければ空文字。
- misread_ja: 学習者がどう取り違えうるかを日本語で1文。構造の取り違え(主語・動詞・修飾先・省略の補い方)に限り、単語の意味が分からないこと(語彙の誤読)は書かない。
- correct_structure_ja: 正しい構造(主語・動詞・修飾関係)を日本語で1文。
- subject_span / main_verb: その文の主語の語句と主動詞を、文中から一字一句そのまま。該当がなければ空文字。
- basic_only: この文の説明が上の基礎項目だけで済むならtrue、分類コードに該当する特徴があるならfalse。
- construct_ja / points_ja / context_ja: basic_onlyがfalseでfeature_classがOTHERでない項目だけに書く(それ以外は空文字・空配列)。construct_ja=構文の名前(短く)。points_ja=解説で押さえるべき点(最大2つ、短く)。context_ja=その文の本文中での位置づけを1文で(本文に書かれた事実のみ。解釈や評価は書かない)。これらはユーザー向け解説の材料になるため、難易度・誤解しやすさ・学習価値などの評価語を入れない。

# 出力(JSONオブジェクト1個のみ。前置き・後書き・コードフェンスなし)
{{
  "features": [
    {{"para": "P4", "sentence": "…", "feature_class": "INV", "other_desc": "", "misread_target": "SUBJECT", "misread_quote": "…", "misread_ja": "…", "correct_structure_ja": "…", "subject_span": "…", "main_verb": "…", "basic_only": false, "construct_ja": "…", "points_ja": ["…"], "context_ja": "…"}}
  ],
  "no_feature_paras": ["P1", "P2"]
}}
"""
def stepa6_prompt(d):
    return STEPA6.format(label=d["label"], n=len(d["body"]), numbered=d["numbered"])

# ---------- resolve_verbatim改修(Opus必須修正2): 文頭・文末の引用符を除去してから照合 ----------
_QCH = "“”‘’\"'`"
def strip_quotes(s):
    s = (s or "").strip()
    while s and s[0] in _QCH: s = s[1:].lstrip()
    # 文末の引用符は、直前が文末記号のときだけ除去(所有格のアポストロフィを削らない)
    while len(s) >= 2 and s[-1] in _QCH and s[-2] in ".!?…,:;—-": s = s[:-1].rstrip()
    return s
def resolve6(d, para, sentence):
    try: return t4.resolve_verbatim(d, para, sentence)
    except AssertionError:
        s2 = strip_quotes(sentence)
        if s2 == (sentence or "").strip() or not s2: raise
        return t4.resolve_verbatim(d, para, s2)

# ---------- 解析・決定論規則(LLMを使わない) ----------
def _as_bool(v):
    if isinstance(v, bool): return v
    return str(v).strip().lower() in ("true", "はい", "yes")
def parse_stepa6(txt, d, inp=None):
    m = re.search(r"\{.*\}", txt, re.S); j = json.loads(m.group(0))
    assert isinstance(j.get("features"), list) and isinstance(j.get("no_feature_paras"), list)
    seen = set(); feats = []
    for idx, f in enumerate(j["features"]):
        f = dict(f); f["resolve_ok"] = True; f["order"] = idx
        try:
            verb, pi, a, b = resolve6(d, f.get("para"), f.get("sentence", ""))
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
def _cls(f): return str(f.get("feature_class", "")).strip().upper()
def _pnum(f): return int(re.sub(r"\D", "", f["para"]))
def base_ok(f):
    return bool(f.get("resolve_ok") and not f.get("duplicate") and _cls(f) in PRIORITY and not _as_bool(f.get("basic_only", True)))
def materials_ok(f):
    return bool(str(f.get("construct_ja", "")).strip() and isinstance(f.get("points_ja"), list) and any(str(x).strip() for x in f["points_ja"]) and str(f.get("context_ja", "")).strip())
def mid_cond(f):
    return str(f.get("misread_target", "")).strip().upper() in TARGETS and bool(f.get("misread_quote_in_sentence"))
def eligible_main(f):
    """主規則の適格: 基礎のみでない・OTHER除外・材料欄あり、かつ 強クラスはそのまま/中クラスは misread_target∈列挙 かつ misread_quote逐語。"""
    return base_ok(f) and materials_ok(f) and (_cls(f) in STRONG or mid_cond(f))
def _order_key(f): return (PRIORITY.index(_cls(f)), _pnum(f), f.get("order", 0))
def select_main(feats, k=2):
    """適格を (クラス優先順, 段落番号, 出現順) に並べ、同一クラス・同一段落は1件まで、最大k件。適格0なら0件(0件を既定にはしない)。"""
    out = []; used_cls = set(); used_para = set()
    for f in sorted([f for f in feats if eligible_main(f)], key=_order_key):
        if _cls(f) in used_cls or f["para"] in used_para: continue
        out.append(f); used_cls.add(_cls(f)); used_para.add(f["para"])
        if len(out) >= k: break
    return out
def select_cmp_orig(feats, k=2):
    """比較用(合否に使わない): 元のwhat-if規則=クラス優先順、基礎のみ除外・misread_ja非空、同一クラス制約なし・追加条件なし。"""
    el = sorted([f for f in feats if base_ok(f) and str(f.get("misread_ja", "")).strip()], key=_order_key)
    return el[:k]
def select_cmp_nosame(feats, k=2):
    """比較用(合否に使わない): 主規則の適格条件のまま、同一クラス制約・段落重複排除を外した版。"""
    return sorted([f for f in feats if eligible_main(f)], key=_order_key)[:k]
def to_selected(f):
    if not materials_ok(f): return None
    s = dict(para=f["para"], sentence=f["sentence"], construct_ja=f["construct_ja"], points_ja=[str(x) for x in f["points_ja"]][:3],
             context_ja=f["context_ja"], reason_dev=f"{_cls(f)}/{f.get('misread_target','')}: {f.get('misread_ja','')}", prev=f.get("prev", ""), next=f.get("next", ""))
    if f.get("ref_ja"): s["ref_ja"] = f["ref_ja"]
    return s
def sel_record(f): return dict(para=f["para"], sentence=f["sentence"], feature_class=_cls(f), misread_target=f.get("misread_target", ""),
                               misread_quote=f.get("misread_quote", ""), subject_span=f.get("subject_span", ""), main_verb=f.get("main_verb", ""))
def sel_to_stepa(feats):
    fs = select_main(feats)
    return dict(selected=[x for x in (to_selected(f) for f in fs) if x], records=[sel_record(f) for f in fs])

# ---------- 費用ガード: 予約方式(Opus必須修正1) ----------
class Refused(Exception): pass
class Budget:
    """spent(実費確定分)+reserved(実行中callの最大見込み額)+今回の最大見込み額 <= cap のときだけcallを開始する。
    満たさないときは他のcallの完了(予約→実費への置換)を待ち、単独でも満たさなければ拒否(Refused)。
    各callは max_output_tokens で出力費の上限を持つため、最大見込み額(hard)は実費の保証上限になる。"""
    def __init__(self, cap, spent0=0.0):
        self.cap = cap; self.spent = spent0; self.reserved = 0.0; self.cv = threading.Condition(); self.log = []; self.aborted = False
    def acquire(self, hard, tag):
        with self.cv:
            while True:
                if self.aborted: raise Refused(("aborted", tag))
                if self.spent + self.reserved + hard <= self.cap + 1e-9:
                    self.reserved += hard; self.log.append(("start", tag, round(self.spent, 4), round(self.reserved, 4))); return
                if self.reserved <= 1e-12: raise Refused(("cap", tag, round(self.spent, 4), hard, self.cap))
                self.cv.wait(timeout=5)
    def release(self, hard, actual, tag):
        with self.cv:
            self.reserved -= hard; self.spent += actual; self.log.append(("end", tag, round(actual, 4), round(self.spent, 4))); self.cv.notify_all()
    def abort(self):
        with self.cv: self.aborted = True; self.cv.notify_all()
def hard_cost_jpy(prompt, max_out):
    """最大見込み額(円@160)。入力は文字数を1文字=1tokenと保守的に見積る。出力はmax_output_tokens分(reasoning含む)。"""
    return (len(prompt) * 0.10 / 1e6 + max_out * 0.50 / 1e6) * 160
def usage_spent():
    tot = 0.0
    for p in glob.glob(os.path.join(BASE, "usage_06_*.json")): tot += json.load(open(p, encoding="utf-8"))["cost_jpy_at_160"]
    return tot

MAXOUT_A = 13000; MAXOUT_B = 6000
CAP_A = 12.6   # 本委任上限14円のうちStep B用に1.4円を残す
CAP_ALL = 14.0
_ERR = {"n": 0}; _ERR_LOCK = threading.Lock()
def make_real_llm(budget, maxout_for):
    def real_llm(prompt, tag):
        assert os.environ.get("TRIAL06_PAID_APPROVED") == "1", "paid call refused"
        maxout = maxout_for(tag); hard = hard_cost_jpy(prompt, maxout)
        budget.acquire(hard, tag)
        actual = 0.0
        try:
            from dotenv import load_dotenv; load_dotenv(os.path.join(ROOT, ".env"))
            from openai import OpenAI
            c = OpenAI(); t0 = time.time()
            r = c.responses.create(model="gpt-6-luna", input=[{"role": "user", "content": prompt}], max_output_tokens=maxout)
            el = time.time() - t0; u = r.usage
            cached = getattr(u.input_tokens_details, "cached_tokens", 0)
            usd = (u.input_tokens - cached) * 0.10 / 1e6 + cached * 0.01 / 1e6 + u.output_tokens * 0.50 / 1e6
            actual = usd * 160
            d = {"tag": tag, "model_requested": "gpt-6-luna", "model_actual": r.model, "response_id": r.id, "status": getattr(r, "status", None), "elapsed_sec": round(el, 1),
                 "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(), "input_tokens": u.input_tokens, "cached_input_tokens": cached,
                 "output_tokens": u.output_tokens, "reasoning_tokens": getattr(u.output_tokens_details, "reasoning_tokens", None),
                 "max_output_tokens": maxout, "hard_reserved_jpy": round(hard, 4), "cost_usd": round(usd, 6), "cost_jpy_at_160": round(actual, 4)}
            json.dump(d, open(os.path.join(BASE, f"usage_06_{tag}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            open(os.path.join(BASE, f"_raw_06_{tag}.txt"), "w", encoding="utf-8", newline="\n").write(r.output_text or "")
            return r.output_text, d
        except Refused: raise
        except Exception:
            with _ERR_LOCK:
                _ERR["n"] += 1
                if _ERR["n"] >= 2: budget.abort()      # 原因不明の失敗が2回 -> 新規call停止(STOP規則)
            raise
        finally:
            budget.release(hard, actual, tag)
    return real_llm

# ---------- 実行 ----------
def run_stepa6(work, runid, llm):
    d = work_data6(work); inp = t4.load_inputs().get(work) if work in t4.WORKS else None
    tag = f"06_{runid}_stepA6_{work}"
    r = llm(stepa6_prompt(d), tag)
    path = os.path.join(BASE, f"OUTPUT_06_{work}_{runid}_STEPA_DEV.json")
    try:
        j = parse_stepa6(r[0], d, inp)
    except Exception as e:
        j = dict(parse_error=repr(e)[:300], raw_file=f"_raw_{tag}.txt", features=[], no_feature_paras=[], uncovered_paras=[])
    j["rule_selected"] = sel_to_stepa(j["features"]); j["usage"] = r[1]
    open(path, "w", encoding="utf-8", newline="\n").write(json.dumps(j, ensure_ascii=False, indent=1))
    return j

def assemble_user6(work, sel, stepb):
    L = ["## Part 2. Grammar & Sentence Structure", ""]
    if not sel: L += [t4.ZERO_P2, ""]
    for i, s in enumerate(sel, 1): L += [f"### {i}. 対象となる本文英文", "", f"> {s['sentence']}", "", t4.bold_headings(stepb[i]), ""]
    return "\n".join(L)
def assemble_dev6(work, sel_records, usage, user_name):
    L = [f"# OUTPUT_06 DEV記録(開発者向け。ユーザー向け本文ではない) {work}", "", f"ユーザー向けPart 2: `{user_name}`", "", "## 選定(Step A''の決定論規則)", "", "```json", json.dumps(sel_records, ensure_ascii=False, indent=1), "```", "", "## usage (Step B)", ""]
    if usage: L.append(f"model={usage['model_actual']} sec={usage['elapsed_sec']} in={usage['input_tokens']} out={usage['output_tokens']} reasoning={usage['reasoning_tokens']} 円={usage['cost_jpy_at_160']}")
    else: L.append("Step B callなし(選定0件)")
    return "\n".join(L) + "\n"
def run_stepb6(work, runid, llm):
    A = json.load(open(os.path.join(BASE, f"OUTPUT_06_{work}_{runid}_STEPA_DEV.json"), encoding="utf-8"))
    sel = A["rule_selected"]["selected"]; stepb = {}; usage = None
    if sel:
        r = llm(t4.stepb_prompt(sel), f"06_{runid}_stepB_{work}"); usage = r[1]
        stepb = t4.parse_stepb(r[0], len(sel))
    un = f"OUTPUT_06_{work}_{runid}_USER.md"
    open(os.path.join(BASE, un), "w", encoding="utf-8", newline="\n").write(assemble_user6(work, sel, stepb))
    open(os.path.join(BASE, f"OUTPUT_06_{work}_{runid}_DEV.md"), "w", encoding="utf-8", newline="\n").write(assemble_dev6(work, A["rule_selected"]["records"], usage, un))

def batch_a(llm):
    from concurrent.futures import ThreadPoolExecutor
    jobs = [(w, f"r{i}") for i in range(1, NSAMP + 1) for w in WORKS6]; errs = {}
    def one(w, r):
        try: run_stepa6(w, r, llm)
        except Exception as e: errs[f"{w}_{r}"] = repr(e)[:300]
    with ThreadPoolExecutor(max_workers=len(jobs)) as ex: list(ex.map(lambda x: one(*x), jobs))
    return errs
def batch_b(llm):
    from concurrent.futures import ThreadPoolExecutor
    errs = {}
    def one(w):
        try: run_stepb6(w, "r1", llm)
        except Exception as e: errs[f"stepB_{w}"] = repr(e)[:300]
    with ThreadPoolExecutor(max_workers=len(WORKS6)) as ex: list(ex.map(one, WORKS6))
    return errs

# ---------- dry-run / selftest ----------
def _head(p): return p[:p.index("# 本文")] + p[p.index("# 手順"):]
def leak_check():
    for w in WORKS6:
        h = _head(stepa6_prompt(work_data6(w)))
        for w2 in WORKS6:
            for s in t4._sents("\n\n".join(work_data6(w2)["body"])):
                if len(s) > 15: assert s not in h, ("example leaks work sentence", w2, s[:40])
    # Prompt例(英文)の個別照合: 指示部の英語の例文が、どの作品本文にも逐語で含まれない
    h = _head(stepa6_prompt(work_data6("gift")))
    alltext = " ".join(" ".join(work_data6(w)["body"]) for w in WORKS6)
    for ex in re.findall(r"[A-Z][A-Za-z' ,]+?[.!]", h):
        if len(ex.split()) >= 4: assert ex.strip() not in alltext, ("example in work body", ex)
def dry_run():
    out = {}
    for w in WORKS6:
        d = work_data6(w); p = stepa6_prompt(d)
        open(os.path.join(BASE, f"_prompt_06_{w}_stepA6.txt"), "w", encoding="utf-8", newline="\n").write(p)
        out[w] = dict(paras=len(d["body"]), prompt_chars=len(p), hard_jpy=round(hard_cost_jpy(p, MAXOUT_A), 3), sha=hashlib.sha256(p.encode()).hexdigest()[:12])
    leak_check()
    out["worst_case_all_18_jpy"] = round(sum(v["hard_jpy"] for v in out.values() if isinstance(v, dict)) * NSAMP, 2)
    json.dump(out, open(os.path.join(BASE, "dryrun_06.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return out

def _mf(d, para, cls, basic=False, target="SUBJECT", si=0, mq=None, mat=True):
    s = t4._sents(d["body"][int(para[1:]) - 1])[si]
    return dict(para=para, sentence=s, feature_class=cls, other_desc="", misread_target=target, misread_quote=(s.split()[0] if mq is None else mq), misread_ja="x",
                correct_structure_ja="c", subject_span="", main_verb="", basic_only=basic,
                construct_ja="構文" if mat else "", points_ja=["p"] if mat else [], context_ja="ctx" if mat else "")
def _parse(d, feats): return parse_stepa6(json.dumps(dict(features=feats, no_feature_paras=[]), ensure_ascii=False), d)
def selftest():
    d = work_data6("open_window")
    # --- resolve: 引用符除去
    s = t4._sents(d["body"][20])[0]
    for variant in ("“" + s + "”", "\"" + s + "\""):
        v = resolve6(d, "P21", variant)[0]; assert v == s, (variant, v)
    assert strip_quotes("“Hello there.”") == "Hello there." and strip_quotes("the dogs’") == "the dogs’"
    # --- 規則(合成データ): 優先順・同一クラス1件・中クラス追加条件・OTHER/基礎除外・0件
    fs = [_mf(d, "P21", "FRONT"), _mf(d, "P29", "INV"), _mf(d, "P5", "INV"), _mf(d, "P7", "CMP"), _mf(d, "P3", "ELL", target=""), _mf(d, "P1", "OTHER"), _mf(d, "P23", "CLEFT", basic=True)]
    j = _parse(d, fs)
    sel = select_main(j["features"]); assert [(f["para"], _cls(f)) for f in sel] == [("P5", "INV"), ("P7", "CMP")], [(f["para"], _cls(f)) for f in sel]   # INV 2件目(P29)は選ばない/CLEFT(基礎のみ)除外
    assert [f["para"] for f in select_cmp_orig(j["features"])] == ["P5", "P29"]      # 比較規則は同一クラス制約なし
    assert [f["para"] for f in select_cmp_nosame(j["features"])] == ["P5", "P29"]
    # 中クラス追加条件: target空 / quoteが文に無い / 材料欠落 は不適格、条件を満たせば適格
    j2 = _parse(d, [_mf(d, "P3", "ELL", target=""), _mf(d, "P5", "HEAVY", mq="zzz not in sentence"), _mf(d, "P7", "POSTMOD", mat=False), _mf(d, "P29", "SPEC")])
    assert [f["para"] for f in select_main(j2["features"])] == ["P29"], select_main(j2["features"])
    j3 = _parse(d, [_mf(d, "P1", "OTHER"), _mf(d, "P3", "ELL", basic=True), _mf(d, "P5", "APPOS", target="BAD")]); assert select_main(j3["features"]) == []   # 0件
    assert select_main(_parse(d, [])["features"]) == []
    # 同一段落は1件(2文以上の段落を探して、同じ段落の別文を別クラスで列挙)
    pm = next(i for i, x in enumerate(d["body"], 1) if len(t4._sents(x)) >= 2 and i not in (5, 29))
    j4 = _parse(d, [_mf(d, f"P{pm}", "FRONT", si=0), _mf(d, f"P{pm}", "HEAVY", si=1, mq=t4._sents(d["body"][pm - 1])[1].split()[0]), _mf(d, "P5", "SPEC")])
    assert [_cls(f) for f in select_main(j4["features"])] == ["FRONT", "SPEC"], [_cls(f) for f in select_main(j4["features"])]       # 同一段落のHEAVYは除外
    # 解決不能・重複
    bad = _mf(d, "P21", "INV"); bad["sentence"] = "this sentence is not in the body"
    jb = _parse(d, [bad, _mf(d, "P21", "INV"), _mf(d, "P21", "INV")]); assert jb["features"][0]["resolve_ok"] is False and jb["features"][2].get("duplicate")
    assert [f["para"] for f in select_main(jb["features"])] == ["P21"]
    # 6作品の読込・段落数
    for w in WORKS6: assert len(work_data6(w)["body"]) >= 10, w
    # assemble
    sr = to_selected(_mf(work_data6("tth"), "P15", "INV", si=0)); u = assemble_user6("tth", [sr], {1: "【日本語訳】\n訳\n【文法・構文の仕組み】\n説明"}); assert "対象となる本文英文" in u and "**日本語訳**" in u
    assert t4.ZERO_P2 in assemble_user6("promise", [], {})
    # --- 費用ガード(予約方式): 並列でも spent <= cap、単独で収まらなければ拒否
    import random, threading as th
    from concurrent.futures import ThreadPoolExecutor
    bg = Budget(cap=10.0, spent0=0.0); peak = {"v": 0.0}
    def mock(i):
        hard = 1.0
        try: bg.acquire(hard, f"t{i}")
        except Refused: return "refused"
        try:
            time.sleep(0.01); actual = random.uniform(0.2, 1.0)
            with bg.cv: peak["v"] = max(peak["v"], bg.spent + bg.reserved)
        finally: bg.release(hard, actual, f"t{i}")
        return "ok"
    with ThreadPoolExecutor(max_workers=30) as ex: res = list(ex.map(mock, range(30)))
    assert bg.spent <= 10.0 + 1e-9 and peak["v"] <= 10.0 + 1e-9 and "ok" in res, (bg.spent, peak, res.count("ok"))
    b2 = Budget(cap=1.0, spent0=0.95)
    try: b2.acquire(0.5, "x"); raise SystemExit("must refuse")
    except Refused: pass
    b3 = Budget(cap=3.5); b3.acquire(1.0, "a"); b3.acquire(1.0, "b"); b3.acquire(1.0, "c")     # 開始時点で予約済み: 4本目は完了待ち
    got = {}
    t = th.Thread(daemon=True, target=lambda: (b3.acquire(1.0, "d"), got.setdefault("d", True))); t.start(); time.sleep(0.2); assert "d" not in got
    b3.release(1.0, 0.3, "a"); t.join(timeout=10); assert got.get("d")
    # 想定外の高コストでも 起動前判定がspent+reserved基準であること(旧方式=累計のみ判定の再発防止)
    b4 = Budget(cap=2.0, spent0=1.5)
    try: b4.acquire(0.9, "y"); raise SystemExit("must refuse (spent 1.5 + hard 0.9 > 2.0)")
    except Refused: pass
    # --- 最大見込み額の妥当性: 全6作品の保守的 hard が 1.3円未満(max_output_tokens=13000)
    for w in WORKS6: assert hard_cost_jpy(stepa6_prompt(work_data6(w)), MAXOUT_A) < 1.3
    leak_check()
    print("selftest OK")

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "dry-run": print(json.dumps(dry_run(), ensure_ascii=False, indent=1))
    elif cmd == "selftest": selftest()
    elif cmd == "send-a":
        bg = Budget(CAP_A, usage_spent()); t0 = time.time()
        errs = batch_a(make_real_llm(bg, lambda tag: MAXOUT_A))
        json.dump({"errors": errs, "spent_jpy": bg.spent, "log": bg.log, "elapsed": round(time.time() - t0, 1)}, open(os.path.join(BASE, "batch_06a_result.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("done", errs, round(bg.spent, 4))
    elif cmd == "send-b":
        bg = Budget(CAP_ALL, usage_spent()); t0 = time.time()
        errs = batch_b(make_real_llm(bg, lambda tag: MAXOUT_B))
        json.dump({"errors": errs, "spent_jpy": bg.spent, "log": bg.log, "elapsed": round(time.time() - t0, 1)}, open(os.path.join(BASE, "batch_06b_result.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("done", errs, round(bg.spent, 4))
