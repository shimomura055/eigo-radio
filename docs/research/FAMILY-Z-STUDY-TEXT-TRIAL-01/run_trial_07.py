# FAMILY-Z-STUDY-TEXT-TRIAL-01 Trial-07専用script(DEV。Production非参照)。run_trial_06.pyから派生。
# Part 2: 文法解説は最大1件・該当なければ0件。Step A''(全文タグ付け: 分類+front_kind+teaching_value) -> コードの決定論規則(1件選定) -> Step B。
# 引用文連結対策: resolve7(段落境界をまたぐ連結の検出と再解決) + verify_single_span(選定文が単一段落内の逐語spanである検証)。
# 基準: PREREGISTERED_CRITERIA_07.md(有料生成前commit)。
#   py run_trial_07.py dry-run          # Prompt書出し・例の本文非含有assert・見積(API 0)
#   py run_trial_07.py selftest         # mock LLMで規則・連結回帰・0件経路・費用ガードを確認(API 0)
#   .venv\Scripts\python.exe run_trial_07.py send-a   # 有料(Step A''。TRIAL07_PAID_APPROVED=1 必須)
#   .venv\Scripts\python.exe run_trial_07.py send-b   # 有料(Step B。合格時のみ。TRIAL07_PAID_APPROVED=1 必須)
import sys, os, json, re, hashlib, time, glob, threading
BASE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(BASE, "..", "..", ".."))
sys.path.insert(0, BASE)
import run_trial_04 as t4
import run_trial_06 as t6
from run_trial_06 import Budget, Refused, hard_cost_jpy, strip_quotes

# ---------- 作品(Trial-06の6作品 + 新ホールドアウト2作品。いずれも既存本文。新規生成なし) ----------
FZ = "er026_output/family_z_production_e2e_01"
SRC7 = {"boredom": ("er019_output/boredom_aggression/run_bape_01/b1b/article.md", "If You Had to Watch a Stone for Five Minutes, Would Your “Bad-Guy Switch” Turn On?(Family Xの解説記事・退屈と攻撃性)", True),
        "melos": (f"{FZ}/melos/run_e2e_06/writer/r2.md", "Before the Last Light(『走れメロス』・Family Z)", False)}
WORKS7 = ["open_window", "ig_nobel", "gift", "paw", "tth", "promise", "boredom", "melos"]
NSAMP7 = {"open_window": 3, "ig_nobel": 2, "gift": 3, "paw": 2, "tth": 2, "promise": 2, "boredom": 2, "melos": 2}   # 計18 call(Trial-06で問題のあった2作品=N=3、他はN=2。上限12円内に収める)
NAME_JA = dict(t6.NAME_JA, boredom="退屈と攻撃性(新ホールドアウト・難所あり)", melos="走れメロス(新ホールドアウト・平易)")
def work_data7(work):
    if work not in SRC7: return t6.work_data6(work)
    path, label, dol = SRC7[work]
    text = open(os.path.join(ROOT, path), encoding="utf-8").read()
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    assert paras[0].startswith("# "); body = paras[1:]
    if dol:
        i = [k for k, p in enumerate(body) if p.startswith("## In one line")]; assert len(i) == 1; body = body[:i[0]]
    numbered = "\n\n".join(f"[P{i}] {x}" for i, x in enumerate(body, 1))
    return dict(text=text, body=body, numbered=numbered, kp=[], label=label)

# ---------- 分類・規則(事前登録 PREREGISTERED_CRITERIA_07 §1 で固定) ----------
STRONG = ["INV", "CLEFT", "CMP"]
MID = ["FRONT", "HEAVY", "POSTMOD", "SPEC", "ELL", "APPOS"]
PRIORITY = STRONG + MID                       # 優先順位は06と同一。OTHERは記録のみ
TARGETS = {"SUBJECT", "VERB", "MODIFIEE", "OMITTED"}
FRONT_OK = {"PARTICIPLE", "ADJECTIVE", "AS_THOUGH", "NESTED_OR_LONG", "OBJECT_OR_COMPLEMENT"}   # FRONTとして採用できる文頭要素
FRONT_BASIC = {"CLAUSE_SIMPLE", "PHRASE_SHORT"}                                                  # 単純な文頭配置=基礎(採用しない)

STEPA7 = """あなたは英語読解指導の専門家です。下の英語本文(Advancedレベル)を、日本語話者の学習者(B1〜B2相当)の読解の観点で点検します。この工程の仕事は、本文の全文を見て、構文上の特徴のある文に「分類コード」を付けて漏れなく洗い出すことです。どの文を解説するかの選択は、この工程では行いません(別の工程が決まった規則で、最大1件を選びます。該当がなければ0件です)。解説文も書きません。

# 作品・レベル
- 作品: {label}
- レベル: Advanced

# 本文(段落番号[P1]〜[P{n}]は参照用。引用では番号を書かない)
{numbered}

# 手順
1. 本文を最初から最後まで、段落を1つずつ確認し、すべての文について、下の「分類コード」に該当する特徴があるかを確認する。該当する文は、数に上限を設けず、すべてfeaturesに列挙する(1段落に複数あれば文ごとに列挙)。特にINV・CLEFT・CMPの3つは、全段落で見落としがないか最後にもう一度確認する。どの文にも該当しない段落は、段落番号をno_feature_parasに書く(featuresに載せた段落は書かない)。
2. featuresの各文について、その文だけを見て、分類コードと、構造の取り違えの起点を答える。他の文との比較、どれが重要か、何件挙げるか、といった相対的な判断はしない。

# 分類コード(feature_classに書く)
- INV: 倒置。場所・方向・否定・時を表す副詞句が文頭に出て、動詞が主語の前に来る(例: Under the bed lay a small box. / Never had she seen such a place.)。伝達部の倒置(said Vera の型)は含まない。
- CLEFT: 疑似分裂文・分裂文(例: What the committee needed was more time. / It was in March that the plan changed.)。
- CMP: 比較の基準(何と何を比べているか)が見えにくい比較。倍数比較・as以降の省略・than以降が前置詞句や代名詞だけで何と比べるかを補う必要があるもの(例: The new bridge is twice as long as the old one. / She earns three times what he does. / Cats were calmer after the vet than after the move.)。
- FRONT: 文頭に置かれた要素のために、主節の主語や動詞を取り違えやすい文。**文頭要素の種類をfront_kindに必ず書く**(下記)。
- HEAVY: 主語が長い・重い。主語の中心から動詞までが離れている、または主語が節・長い句で、動詞を見つけにくい(例: The decision to postpone the vote until after the holidays surprised everyone.)。
- POSTMOD: 名詞から離れた、または重なった後置修飾(後置の分詞句・関係節・前置詞句など)で、修飾先を取り違えやすい(例: He found a letter on the table by the window addressed to his brother.)。
- SPEC: 目的語と補語の境界が見えにくい特殊な文型に限る。形式目的語it(例: She found it impossible to refuse such an offer.)、目的語が長いもの、wish+目的語+形容詞/副詞(例: I wish my brother here.)など。
- ELL: 前の文や前の部分から、**別の主語の動詞・比較の基準を補わないと構造が取れない**省略(例: Tom likes tea, and Anna coffee.)。補った語句をomitted_wordsに書く。同じ主語が続く並列(He opened the door, then left.)・省略された関係代名詞・会話の断片はELLにしない。
- APPOS: 同格・挿入・コンマで区切られた要素のため、構造が複数に読める(例: My neighbour's daughter, a doctor in Leeds, called.)。
- OTHER: 上記以外の構文上の特徴。

# FRONTのfront_kind(FRONTの文だけに書く。それ以外の分類では空文字)
- CLAUSE_SIMPLE: 文頭が、時・理由・条件などの副詞節(before/after/when/if/because/although/while + 主語 + 動詞)。主節の主語と動詞が普通に読める単純な形。**基礎であり、FRONTにしない**(basic_onlyをtrue)。
- PHRASE_SHORT: 文頭が、短い副詞・前置詞句・時や場所の語句(Then, / In the morning, / At the gate,)。**基礎であり、FRONTにしない**。
- PARTICIPLE: 文頭が分詞句(Hidden behind the door, the boy waited. / Having lost the key, she knocked.)で、分詞の意味上の主語や主節の主語が取りにくい。
- ADJECTIVE: 文頭が形容詞句・名詞句の独立した修飾(Calm and sure of himself, he spoke.)。
- AS_THOUGH: as/though/although/much asによる倒置的な前置(Hard as it was to admit, she had been wrong.)。
- NESTED_OR_LONG: 文頭要素が長く(おおむね10語以上)、その中にさらに節や修飾が入って、主節の主語や動詞の位置が見えにくい(例: Regardless of how little each member had been told, the team agreed to go on.)。
- OBJECT_OR_COMPLEMENT: 目的語や補語が文頭に出ている(例: This I could not forgive.)。
- 文頭に従属節や前置詞句が「置かれているだけ」という理由でFRONTにしてはならない(単純な文頭配置は基礎)。文頭要素が複雑で、読み方が実際に難しくなっている場合だけ、上のPARTICIPLE〜OBJECT_OR_COMPLEMENTを選ぶ。

# 基礎項目(これだけで説明が済む文は価値なしとして扱い、basic_onlyをtrueにする。作品に関係なく共通)
命令文(命令文+and/orを含む)/ 基本的な接続(and・but・or・so・because・when・if・while・although・before・after)と、それらが導く文頭・文中の単純な副詞節 / 前置詞句 / 分詞構文・付帯状況のwithの基本形 / 関係詞の基本用法(whose・関係副詞・省略された関係代名詞を含む)/ 基本時制・進行形・完了形・受動態 / 比較級・最上級・as…asの基本形 / 仮定法の基本形 / 動名詞主語の単純形 / the+形容詞 / 伝達部の倒置(said X)/ 伝達部(said X、he explained等)に付く同格・挿入 / 疑問文・感嘆文・there is構文・It is…to…の基本形 / to不定詞・動名詞・分詞の基本用法 / 使役動詞・知覚動詞+目的語+原形/分詞、keep/make/find+目的語+補語の基本形 / 会話の断片・間投詞・一語や短い語句だけの返答。
- 基礎項目を含む文でも、上の分類コードに該当する特徴が文中にあれば、その特徴について答える(basic_onlyはfalse)。分類コードに該当する特徴がないのに、基礎項目の「特殊な用法」「表現効果」を理由に分類してはならない。
- 基礎項目だけの文はfeaturesに載せなくてよい(載せる場合は、feature_classをOTHER、basic_onlyをtrueにし、材料欄は空にする)。

# 学習価値の確認(teaching_valueとteaching_value_ja。basic_onlyがfalseの項目に書く)
- teaching_value: HIGH または LOW。HIGH=基礎項目の説明では足りず、この文の構造を理解する説明に学習者が一般の英文でも再利用できる読み方が含まれる(同じ型が他の英文でも出会う)。かつ、読み違えると文意が大きく変わる、または日本語に引き写しにくい。LOW=上記を満たさない(その文脈だけの用法、すぐ読み取れる短い文、基礎項目の言い換えで済む)。
- teaching_value_ja: HIGHの場合、この文の解説で学習者が身につけられる読み方を1句で(例: 場所の副詞句が文頭に出ると主語と動詞の順が逆になる)。LOWの場合は空文字でよい。

# featuresの各項目の書き方(各欄は短く)
- para: 段落番号(例: "P4")。sentence: **その1つの段落の中にある1つの文**を、本文から一字一句そのまま(逐語。文頭・文末の引用符は書かなくてよい)。**段落をまたいで文を連結してはならない**(文がコロンで終わっていて次の段落が引用になっていても、次の段落の引用はsentenceに含めず、コロンまでを書く)。
- feature_class: 上のコード。front_kind: 上のコード(FRONT以外は空文字)。
- misread_target: 学習者が構造を取り違える対象。SUBJECT(主語)/ VERB(動詞)/ MODIFIEE(修飾先)/ OMITTED(省略された語句の補い方)のいずれか1つ。取り違えの対象を具体的に挙げられない場合は空文字。
- misread_quote: 取り違えの起点になる本文中の語句を一字一句そのまま(1〜8語)。挙げられなければ空文字。
- misread_ja: 学習者がどう取り違えうるかを日本語で1文。構造の取り違え(主語・動詞・修飾先・省略の補い方)に限り、単語の意味が分からないこと(語彙の誤読)は書かない。
- omitted_words: ELLの場合のみ、補う語句(本文にない語を書いてよい)。それ以外は空文字。
- basic_only: この文の説明が上の基礎項目だけで済むならtrue、分類コードに該当する特徴があるならfalse。
- construct_ja / points_ja / context_ja: basic_onlyがfalseでfeature_classがOTHERでない項目だけに書く(それ以外は空文字・空配列)。construct_ja=構文の名前(短く)。points_ja=解説で押さえるべき点(最大2つ、短く)。context_ja=その文の本文中での位置づけを1文で(本文に書かれた事実のみ。解釈や評価は書かない)。これらはユーザー向け解説の材料になるため、難易度・誤解しやすさ・学習価値などの評価語を入れない。

# 出力(JSONオブジェクト1個のみ。前置き・後書き・コードフェンスなし)
{{
  "features": [
    {{"para": "P4", "sentence": "…", "feature_class": "INV", "front_kind": "", "misread_target": "SUBJECT", "misread_quote": "…", "misread_ja": "…", "omitted_words": "", "basic_only": false, "teaching_value": "HIGH", "teaching_value_ja": "…", "construct_ja": "…", "points_ja": ["…"], "context_ja": "…"}}
  ],
  "no_feature_paras": ["P1", "P2"]
}}
"""
def stepa7_prompt(d): return STEPA7.format(label=d["label"], n=len(d["body"]), numbered=d["numbered"])

# ---------- 引用文連結の検出と再解決(Trial-06 open_window r2: P21 + 次段落P22の引用を連結して返しresolve失敗) ----------
def _tok(s): return t4._qn(s).split()
def _para_tokens(d, i): return _tok(d["body"][i])
def _tn(t): return t.strip("\"'")   # 語の前後の引用符・アポストロフィ記号を無視して比較(両側に同じ正規化)
def resolve7(d, para, sentence):
    """resolve6を先に試し、失敗した場合に限り段落境界をまたぐ連結を検出して再解決する。
    連結と認める条件(厳格): 返された語列が (主張段落の末尾) + (直後の段落の先頭から連続) に厳密に一致する、
    または (直前の段落の末尾) + (主張段落の先頭から連続) に厳密に一致する。一致しなければ従来どおり失敗(誤修復しない)。
    戻り値: (本文側逐語, 段落index, a, b, flag) flag=None|"cross_para_trimmed_tail"|"cross_para_trimmed_head"。"""
    try:
        v, pi, a, b = t6.resolve6(d, para, sentence); return v, pi, a, b, None
    except AssertionError as e0:
        err = e0
    m = re.fullmatch(r"P(\d+)", str(para).strip())
    if not m or not (1 <= int(m.group(1)) <= len(d["body"])): raise err
    pi = int(m.group(1)) - 1; toks = [_tn(x) for x in _tok(sentence)]
    if not toks: raise err
    ptoks = [_tn(x) for x in _para_tokens(d, pi)]; praw = _para_tokens(d, pi)
    # (a) 主張段落の末尾 + 次段落以降の先頭
    if pi + 1 < len(d["body"]):
        nxt = []
        for j in range(pi + 1, min(pi + 4, len(d["body"]))): nxt += [_tn(x) for x in _para_tokens(d, j)]
        for k in range(len(toks) - 1, 0, -1):                       # 主張段落側に残すのは最長のprefix(残りが次段落側)
            pre, rest = toks[:k], toks[k:]
            if len(pre) <= len(ptoks) and ptoks[-len(pre):] == pre and nxt[:len(rest)] == rest:
                v, pi2, a, b = t4.resolve_verbatim(d, para, " ".join(praw[-len(pre):])); return v, pi2, a, b, "cross_para_trimmed_tail"
    # (b) 直前段落の末尾 + 主張段落の先頭
    if pi > 0:
        prv = []
        for j in range(max(0, pi - 3), pi): prv += [_tn(x) for x in _para_tokens(d, j)]
        for k in range(1, len(toks)):                               # 主張段落側に残すのは最長のsuffix
            head, suf = toks[:k], toks[k:]
            if len(suf) <= len(ptoks) and ptoks[:len(suf)] == suf and len(head) <= len(prv) and prv[-len(head):] == head:
                v, pi2, a, b = t4.resolve_verbatim(d, para, " ".join(praw[:len(suf)])); return v, pi2, a, b, "cross_para_trimmed_head"
    raise err
def verify_single_span(d, para, sentence):
    """抽出検証: sentenceが主張段落1つの中の連続した逐語spanであり、段落区切りを含まない。(連結・改変の最終検査)"""
    m = re.fullmatch(r"P(\d+)", str(para).strip())
    if not m or not (1 <= int(m.group(1)) <= len(d["body"])): return False
    body = d["body"][int(m.group(1)) - 1]
    return bool(sentence) and "\n" not in sentence and sentence in body

# ---------- 解析 ----------
def _as_bool(v): return t6._as_bool(v)
def parse_stepa7(txt, d, inp=None):
    m = re.search(r"\{.*\}", txt, re.S); j = json.loads(m.group(0))
    assert isinstance(j.get("features"), list) and isinstance(j.get("no_feature_paras"), list)
    seen = set(); feats = []
    for idx, f in enumerate(j["features"]):
        f = dict(f); f["resolve_ok"] = True; f["order"] = idx; f["cross_para_flag"] = None
        try:
            verb, pi, a, b, flag = resolve7(d, f.get("para"), f.get("sentence", ""))
            f["sentence_llm_raw"] = f["sentence"]; f["sentence_replaced_by_body"] = (verb != f["sentence"]); f["sentence"] = verb; f["cross_para_flag"] = flag
            f["single_span_ok"] = verify_single_span(d, f.get("para"), verb)
            f["prev"], f["next"] = t4.local_context(d, pi, a, b)
            if inp:
                for it in inp:
                    if t4._qn(it["sentence"]) == t4._qn(verb): f["ref_ja"] = it["sentence_ja"]
            q = (f.get("misread_quote") or "").strip()
            f["misread_quote_in_sentence"] = bool(q) and t4._qn(q) in t4._qn(verb)
            if not f["single_span_ok"]: f["resolve_ok"] = False; f["resolve_error"] = "single_span_check_failed"
        except AssertionError as e:
            f["resolve_ok"] = False; f["resolve_error"] = str(e)[:120]
        key = (f.get("para"), f.get("sentence"))
        if key in seen: f["duplicate"] = True
        seen.add(key); feats.append(f)
    j["features"] = feats
    covered = {f.get("para") for f in feats} | set(j["no_feature_paras"])
    j["uncovered_paras"] = [f"P{i}" for i in range(1, len(d["body"]) + 1) if f"P{i}" not in covered]
    return j

# ---------- 決定論規則: 1件選定(0件可) ----------
def _cls(f): return str(f.get("feature_class", "")).strip().upper()
def _pnum(f): return int(re.sub(r"\D", "", f["para"]))
def base_ok(f): return bool(f.get("resolve_ok") and not f.get("duplicate") and _cls(f) in PRIORITY and not _as_bool(f.get("basic_only", True)))
def materials_ok(f): return t6.materials_ok(f)
def mid_cond(f): return str(f.get("misread_target", "")).strip().upper() in TARGETS and bool(f.get("misread_quote_in_sentence"))
def front_ok(f): return str(f.get("front_kind", "")).strip().upper() in FRONT_OK
def teaching_ok(f): return str(f.get("teaching_value", "")).strip().upper() == "HIGH" and bool(str(f.get("teaching_value_ja", "")).strip())
def eligible7(f):
    """適格: 基礎のみでない・OTHER除外・材料欄あり・teaching_value=HIGH(+teaching_value_ja)。
    中クラスはさらに misread_target∈列挙 かつ misread_quote逐語。FRONTはfront_kind∈FRONT_OK(CLAUSE_SIMPLE/PHRASE_SHORTは不適格)。ELLはomitted_words非空。"""
    if not (base_ok(f) and materials_ok(f) and teaching_ok(f)): return False
    if _cls(f) in STRONG: return True
    if not mid_cond(f): return False
    if _cls(f) == "FRONT" and not front_ok(f): return False
    if _cls(f) == "ELL" and not str(f.get("omitted_words", "")).strip(): return False
    return True
def _order_key(f): return (PRIORITY.index(_cls(f)), _pnum(f), f.get("order", 0))
def select_one(feats):
    """適格を (クラス優先順, 段落番号, 出現順) に並べ先頭1件。適格0なら0件(0件を既定にはしない・件数を満たすための選定はしない)。"""
    el = sorted([f for f in feats if eligible7(f)], key=_order_key)
    return el[:1]
def to_selected(f):
    s = t6.to_selected(f)
    if s: s["teaching_value_ja"] = f.get("teaching_value_ja", "")
    return s
def sel_record(f):
    return dict(para=f["para"], sentence=f["sentence"], feature_class=_cls(f), front_kind=f.get("front_kind", ""), misread_target=f.get("misread_target", ""),
                misread_quote=f.get("misread_quote", ""), teaching_value=f.get("teaching_value", ""), teaching_value_ja=f.get("teaching_value_ja", ""),
                cross_para_flag=f.get("cross_para_flag"), single_span_ok=f.get("single_span_ok"))
def sel_to_stepa(feats):
    fs = select_one(feats)
    return dict(selected=[x for x in (to_selected(f) for f in fs) if x], records=[sel_record(f) for f in fs])

# ---------- 費用ガード(06の予約方式Budgetを使用) ----------
MAXOUT_A = 13000; MAXOUT_B = 6000
CAP_A = 10.8; CAP_ALL = 12.0   # 本委任上限12円。Step B用に1.2円を残す
def usage_spent():
    return sum(json.load(open(p, encoding="utf-8"))["cost_jpy_at_160"] for p in glob.glob(os.path.join(BASE, "usage_07_*.json")))
_ERR = {"n": 0}; _ERR_LOCK = threading.Lock()
def make_real_llm(budget, maxout_for):
    def real_llm(prompt, tag):
        assert os.environ.get("TRIAL07_PAID_APPROVED") == "1", "paid call refused"
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
            json.dump(d, open(os.path.join(BASE, f"usage_07_{tag}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            open(os.path.join(BASE, f"_raw_07_{tag}.txt"), "w", encoding="utf-8", newline="\n").write(r.output_text or "")
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
def run_stepa7(work, runid, llm):
    d = work_data7(work); inp = t4.load_inputs().get(work) if work in t4.WORKS else None
    tag = f"07_{runid}_stepA7_{work}"
    r = llm(stepa7_prompt(d), tag)
    path = os.path.join(BASE, f"OUTPUT_07_{work}_{runid}_STEPA_DEV.json")
    try: j = parse_stepa7(r[0], d, inp)
    except Exception as e: j = dict(parse_error=repr(e)[:300], raw_file=f"_raw_{tag}.txt", features=[], no_feature_paras=[], uncovered_paras=[])
    j["rule_selected"] = sel_to_stepa(j["features"]); j["usage"] = r[1]
    open(path, "w", encoding="utf-8", newline="\n").write(json.dumps(j, ensure_ascii=False, indent=1))
    return j

def assemble_user7(work, sel, stepb):
    L = ["## Part 2. Grammar & Sentence Structure", ""]
    if not sel: L += [t4.ZERO_P2, ""]
    for i, s in enumerate(sel, 1): L += [f"### {i}. 対象となる本文英文", "", f"> {s['sentence']}", "", t4.bold_headings(stepb[i]), ""]
    return "\n".join(L)
def assemble_dev7(work, sel_records, usage, user_name):
    L = [f"# OUTPUT_07 DEV記録(開発者向け。ユーザー向け本文ではない) {work}", "", f"ユーザー向けPart 2: `{user_name}`", "", "## 選定(Step A''の決定論規則・最大1件)", "", "```json", json.dumps(sel_records, ensure_ascii=False, indent=1), "```", "", "## usage (Step B)", ""]
    if usage: L.append(f"model={usage['model_actual']} sec={usage['elapsed_sec']} in={usage['input_tokens']} out={usage['output_tokens']} reasoning={usage['reasoning_tokens']} 円={usage['cost_jpy_at_160']}")
    else: L.append("Step B callなし(選定0件)")
    return "\n".join(L) + "\n"
def run_stepb7(work, runid, llm):
    A = json.load(open(os.path.join(BASE, f"OUTPUT_07_{work}_{runid}_STEPA_DEV.json"), encoding="utf-8"))
    sel = A["rule_selected"]["selected"]; stepb = {}; usage = None
    if sel:
        r = llm(t4.stepb_prompt(sel), f"07_{runid}_stepB_{work}"); usage = r[1]
        stepb = t4.parse_stepb(r[0], len(sel))
    un = f"OUTPUT_07_{work}_{runid}_USER.md"
    open(os.path.join(BASE, un), "w", encoding="utf-8", newline="\n").write(assemble_user7(work, sel, stepb))
    open(os.path.join(BASE, f"OUTPUT_07_{work}_{runid}_DEV.md"), "w", encoding="utf-8", newline="\n").write(assemble_dev7(work, A["rule_selected"]["records"], usage, un))

def batch_a(llm):
    from concurrent.futures import ThreadPoolExecutor
    jobs = [(w, f"r{i}") for w in WORKS7 for i in range(1, NSAMP7[w] + 1)]; errs = {}
    def one(w, r):
        try: run_stepa7(w, r, llm)
        except Exception as e: errs[f"{w}_{r}"] = repr(e)[:300]
    with ThreadPoolExecutor(max_workers=len(jobs)) as ex: list(ex.map(lambda x: one(*x), jobs))
    return errs
def batch_b(llm):
    from concurrent.futures import ThreadPoolExecutor
    errs = {}
    def one(w):
        try: run_stepb7(w, "r1", llm)
        except Exception as e: errs[f"stepB_{w}"] = repr(e)[:300]
    with ThreadPoolExecutor(max_workers=len(WORKS7)) as ex: list(ex.map(one, WORKS7))
    return errs

# ---------- dry-run / selftest ----------
def _head(p): return p[:p.index("# 本文")] + p[p.index("# 手順"):]
def leak_check():
    for w in WORKS7:
        h = _head(stepa7_prompt(work_data7(w)))
        for w2 in WORKS7:
            for s in t4._sents("\n\n".join(work_data7(w2)["body"])):
                if len(s) > 15: assert s not in h, ("example leaks work sentence", w2, s[:40])
    h = _head(stepa7_prompt(work_data7("gift")))
    alltext = " ".join(" ".join(work_data7(w)["body"]) for w in WORKS7)
    for ex in re.findall(r"[A-Z][A-Za-z' ,]+?[.!]", h):
        if len(ex.split()) >= 4: assert ex.strip() not in alltext, ("example in work body", ex)
    for blk in re.findall(r"\(例: ([^)]*)\)", h):
        for e in blk.split(" / "):
            e = e.strip().rstrip(".")
            if len(e.split()) >= 4: assert t4._qn(e) not in t4._qn(alltext), ("example phrase in work body", e)
def dry_run():
    out = {}
    for w in WORKS7:
        d = work_data7(w); p = stepa7_prompt(d)
        open(os.path.join(BASE, f"_prompt_07_{w}_stepA7.txt"), "w", encoding="utf-8", newline="\n").write(p)
        out[w] = dict(paras=len(d["body"]), n=NSAMP7[w], prompt_chars=len(p), hard_jpy=round(hard_cost_jpy(p, MAXOUT_A), 3), sha=hashlib.sha256(p.encode()).hexdigest()[:12])
    leak_check()
    out["n_calls"] = sum(NSAMP7.values())
    out["worst_case_all_jpy"] = round(sum(v["hard_jpy"] * v["n"] for v in out.values() if isinstance(v, dict)), 2)
    json.dump(out, open(os.path.join(BASE, "dryrun_07.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return out

def _mf(d, para, cls, basic=False, target="SUBJECT", si=0, mq=None, mat=True, fk="", tv="HIGH", om=""):
    s = t4._sents(d["body"][int(para[1:]) - 1])[si]
    return dict(para=para, sentence=s, feature_class=cls, front_kind=fk, misread_target=target, misread_quote=(s.split()[0] if mq is None else mq), misread_ja="x",
                omitted_words=om, basic_only=basic, teaching_value=tv, teaching_value_ja=("読み方" if tv == "HIGH" else ""),
                construct_ja="構文" if mat else "", points_ja=["p"] if mat else [], context_ja="ctx" if mat else "")
def _parse(d, feats): return parse_stepa7(json.dumps(dict(features=feats, no_feature_paras=[]), ensure_ascii=False), d)
OW_R2_P21_RAW = "Across the quiet garden came a young voice: “Bertie, why do you bound?”"     # Trial-06 OUTPUT_06_open_window_r2 の返却値(固定データ)
def selftest():
    d = work_data7("open_window")
    # --- 1. 引用文連結の回帰テスト(Trial-06 open_window r2 の再現)
    p21 = d["body"][20]; p22 = d["body"][21]
    assert p21 == "Across the quiet garden came a young voice:" and p22.startswith("“Bertie"), (p21, p22)
    fixed = None
    f6 = os.path.join(BASE, "OUTPUT_06_open_window_r2_STEPA_DEV.json")
    if os.path.exists(f6):                    # 固定データ: Trial-06の実出力に残る返却値と一致することを確認
        j6 = json.load(open(f6, encoding="utf-8")); fixed = [f for f in j6["features"] if f["para"] == "P21"][0]
        assert fixed["sentence"] == OW_R2_P21_RAW and fixed["resolve_ok"] is False, (fixed["sentence"], fixed["resolve_ok"])
    try: t6.resolve6(d, "P21", OW_R2_P21_RAW); raise SystemExit("resolve6 must fail on cross-paragraph concatenation (root cause)")
    except AssertionError: pass
    v, pi, a, b, flag = resolve7(d, "P21", OW_R2_P21_RAW); assert (v, pi, flag) == (p21, 20, "cross_para_trimmed_tail"), (v, flag)
    assert verify_single_span(d, "P21", v)
    assert not verify_single_span(d, "P21", OW_R2_P21_RAW)                      # 連結文そのものは単一span検証に不合格
    if fixed:                                  # 実出力のfeatures全体をparse7に通してP21が復元される(featureが脱落しない)
        feats6 = []
        for f in j6["features"]:
            f = dict(f); f["sentence"] = f.get("sentence_llm_raw", f["sentence"]); feats6.append(f)
        j7 = parse_stepa7(json.dumps(dict(features=feats6, no_feature_paras=j6["no_feature_paras"]), ensure_ascii=False), d)
        f21 = [f for f in j7["features"] if f["para"] == "P21"][0]
        assert f21["resolve_ok"] and f21["sentence"] == p21 and f21["cross_para_flag"] == "cross_para_trimmed_tail" and f21["single_span_ok"], f21
    # 逆向き(後段落に主張): P22を主張し前段落の末尾が付いた連結
    vh = resolve7(d, "P22", p21 + " " + p22); assert vh[0] == p22 and vh[4] == "cross_para_trimmed_head", vh
    # 誤修復しない: 境界でない連結・全く別の語は失敗のまま
    for bad in ("Across the quiet garden " + p22, p21 + " Framton could scarcely breathe.", "Across the quiet garden came a young voice: totally different words"):
        try: resolve7(d, "P21", bad); raise SystemExit(("must not repair", bad))
        except AssertionError: pass
    # 既存動作の維持: 通常の文・引用符付き
    s = t4._sents(d["body"][28])[0]
    for variant in (s, "“" + s + "”"): rv = resolve7(d, "P29", variant); assert rv[0] == s and rv[4] is None
    # 複数文段落の末尾文 + 次段落の先頭文が連結された場合
    i2 = next(i for i in range(len(d["body"]) - 1) if len(t4._sents(d["body"][i])) >= 2)
    last = t4._sents(d["body"][i2])[-1]; nxt_first = t4._sents(d["body"][i2 + 1])[0]
    rv = resolve7(d, f"P{i2+1}", last + " " + nxt_first); assert rv[0] == last and rv[4] == "cross_para_trimmed_tail", rv
    # --- 2. 規則: 最大1件・0件経路
    fs = [_mf(d, "P21", "FRONT", fk="PARTICIPLE"), _mf(d, "P29", "INV"), _mf(d, "P5", "INV"), _mf(d, "P7", "CMP"), _mf(d, "P1", "OTHER"), _mf(d, "P23", "CLEFT", basic=True)]
    j = _parse(d, fs); sel = select_one(j["features"])
    assert len(sel) == 1 and (sel[0]["para"], _cls(sel[0])) == ("P5", "INV"), [(f["para"], _cls(f)) for f in sel]          # 強クラス優先・同クラスは段落順・1件のみ
    for fk in ("CLAUSE_SIMPLE", "PHRASE_SHORT", ""):                      # 単純な文頭配置(Before A, B / After A, B)は不適格
        assert select_one(_parse(d, [_mf(d, "P12", "FRONT", fk=fk)])["features"]) == [], fk
    for fk in sorted(FRONT_OK):                                           # 複雑な文頭要素は適格
        assert [f["para"] for f in select_one(_parse(d, [_mf(d, "P12", "FRONT", fk=fk)])["features"])] == ["P12"], fk
    assert select_one(_parse(d, [_mf(d, "P5", "INV", tv="LOW")])["features"]) == []                 # 学習価値LOWは強クラスでも不適格
    e = _mf(d, "P5", "INV"); e["teaching_value_ja"] = ""; assert select_one(_parse(d, [e])["features"]) == []
    assert select_one(_parse(d, [_mf(d, "P3", "HEAVY", target="")])["features"]) == []
    assert select_one(_parse(d, [_mf(d, "P5", "HEAVY", mq="zzz not in sentence")])["features"]) == []
    assert select_one(_parse(d, [_mf(d, "P3", "ELL", om="")])["features"]) == [] and len(select_one(_parse(d, [_mf(d, "P3", "ELL", om="can change")])["features"])) == 1
    assert select_one(_parse(d, [_mf(d, "P7", "POSTMOD", mat=False)])["features"]) == []
    j0 = _parse(d, [_mf(d, "P1", "OTHER"), _mf(d, "P3", "ELL", basic=True), _mf(d, "P5", "APPOS", target="BAD"), _mf(d, "P12", "FRONT", fk="CLAUSE_SIMPLE")])
    r0 = sel_to_stepa(j0["features"]); assert r0["selected"] == [] and r0["records"] == []          # 0件経路
    assert t4.ZERO_P2 in assemble_user7("promise", [], {}) and "###" not in assemble_user7("promise", [], {})
    assert select_one(_parse(d, [])["features"]) == []
    bad = _mf(d, "P21", "INV"); bad["sentence"] = "this sentence is not in the body"
    jb = _parse(d, [bad, _mf(d, "P29", "INV"), _mf(d, "P29", "INV")]); assert jb["features"][0]["resolve_ok"] is False and jb["features"][2].get("duplicate")
    assert [f["para"] for f in select_one(jb["features"])] == ["P29"]
    for w in WORKS7: assert len(work_data7(w)["body"]) >= 10, w
    sr = to_selected(_mf(work_data7("tth"), "P15", "INV")); u = assemble_user7("tth", [sr], {1: "【日本語訳】\n訳\n【文法・構文の仕組み】\n説明"}); assert "対象となる本文英文" in u and "**日本語訳**" in u
    # --- 3. 費用ガード(予約方式。06のBudgetを再利用)
    import random
    from concurrent.futures import ThreadPoolExecutor
    bg = Budget(cap=10.0, spent0=0.0); peak = {"v": 0.0}
    def mock(i):
        try: bg.acquire(1.0, f"t{i}")
        except Refused: return "refused"
        try:
            time.sleep(0.01); actual = random.uniform(0.2, 1.0)
            with bg.cv: peak["v"] = max(peak["v"], bg.spent + bg.reserved)
        finally: bg.release(1.0, actual, f"t{i}")
        return "ok"
    with ThreadPoolExecutor(max_workers=30) as ex: res = list(ex.map(mock, range(30)))
    assert bg.spent <= 10.0 + 1e-9 and peak["v"] <= 10.0 + 1e-9 and "ok" in res
    b2 = Budget(cap=1.0, spent0=0.95)
    try: b2.acquire(0.5, "x"); raise SystemExit("must refuse")
    except Refused: pass
    for w in WORKS7: assert hard_cost_jpy(stepa7_prompt(work_data7(w)), MAXOUT_A) < 1.3
    leak_check()
    print("selftest OK")

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "dry-run": print(json.dumps(dry_run(), ensure_ascii=False, indent=1))
    elif cmd == "selftest": selftest()
    elif cmd == "send-a":
        bg = Budget(CAP_A, usage_spent()); t0 = time.time()
        errs = batch_a(make_real_llm(bg, lambda tag: MAXOUT_A))
        json.dump({"errors": errs, "spent_jpy": bg.spent, "log": bg.log, "elapsed": round(time.time() - t0, 1)}, open(os.path.join(BASE, "batch_07a_result.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("done", errs, round(bg.spent, 4))
    elif cmd == "send-b":
        bg = Budget(CAP_ALL, usage_spent()); t0 = time.time()
        errs = batch_b(make_real_llm(bg, lambda tag: MAXOUT_B))
        json.dump({"errors": errs, "spent_jpy": bg.spent, "log": bg.log, "elapsed": round(time.time() - t0, 1)}, open(os.path.join(BASE, "batch_07b_result.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("done", errs, round(bg.spent, 4))
