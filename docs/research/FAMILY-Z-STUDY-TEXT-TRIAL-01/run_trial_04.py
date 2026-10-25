# FAMILY-Z-STUDY-TEXT-TRIAL-01 Trial-04専用script(DEV。Production非参照)。
# 上流設計改善: Part 1=本文背景なし別LLM / Part 2=Step A(選定)->Step B(執筆) / Part 3-4=Trial-03(03d)のPromptをそのまま別callで生成。
# 使い方:
#   py run_trial_04.py make-inputs        # INPUT_04.json を Trial-03(03d第1標本)から生成(API 0)
#   py run_trial_04.py dry-run            # 全Promptを _prompt_04_*.txt に書き出し、Part 1に本文背景が混入していないか確認(API 0)
#   py run_trial_04.py selftest           # mock LLMで 工程接続・組立(USER/DEV分離)を確認(API 0)
#   py run_trial_04.py send <work> <run> [alpha|beta]  # 有料。環境変数 TRIAL04_PAID_APPROVED=1 が無い限り実行しない(委任_09でFable Go後のみ)
import sys, os, json, re, hashlib, time
BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(BASE, "..", "..", ".."))
sys.path.insert(0, BASE)
import run_trial_03 as r3
import run_trial_01 as t1

WORKS = ["gift", "ig_nobel", "open_window"]

# ---------- 入力(既存工程の確定値) ----------
def work_data(work):
    """本文(番号付き)/KP(英語表現, 本文中の意味[Production KP gloss], 本文引用英文)/本文生テキスト。Trial-03と同一入力。"""
    if work == "gift":
        text = t1.TEXT; body = t1.body; kp = t1.KP
    else:
        w = r3.WORKS[work]; text = r3.read(w["src"]); _, body = r3.paras_of(text, w["dol"]); kp = w["kp"]
        for _, _, s, _ in kp: assert s in text
    numbered = "\n\n".join(f"[P{i}] {x}" for i, x in enumerate(body, 1))
    label = "The Gift of the Magi(『賢者の贈り物』)" if work == "gift" else r3.WORKS[work]["label"]
    return dict(text=text, body=body, numbered=numbered, kp=[(k, g, s) for k, g, s, _ in kp], label=label)

def load_inputs():
    """INPUT_04.json: 引用英文の日本語訳はTrial-03(03d第1標本)の確定訳を固定して再利用(既存工程の確定値として扱う)。"""
    return json.load(open(os.path.join(BASE, "INPUT_04.json"), encoding="utf-8"))

def extract_ja_from_03d():
    out = {}
    for w in WORKS:
        t = open(os.path.join(BASE, f"OUTPUT_03d_{w}_RAW.md"), encoding="utf-8").read()
        vals = []
        for m in re.finditer(r"英文の日本語訳:\*\*[ \t]*\n?[ \t]*(.+)", t):
            vals.append(m.group(1).strip().strip("「」").strip())
        assert len(vals) == 3, (w, vals)
        d = work_data(w)
        out[w] = [dict(kp=k, gloss_in_text_ja=g, sentence=s, sentence_ja=vals[i]) for i, (k, g, s) in enumerate(d["kp"])]
    return out

# ---------- Prompt: Part 1 (本文背景なし別LLM) ----------
P1_HEAD = """あなたは英語表現の解説を書く英語教育の専門家です。日本語話者の英語学習者(B1〜B2相当)向けに、下の英語表現それぞれの「一般的な解説」を日本語で書いてください。

# 前提
- 解説の対象は、英語表現そのものです。特定の文章・場面・物語には依存せず、その表現が英語で一般にどう使われるか、学習者が実際に使えるようになる知識を説明します。
- この依頼では、表現が使われていた記事・文脈は共有されていません。文脈を想像・推測して解説に織り込まないでください。
"""
P1_BETA_NOTE = """- 各表現には、参考として「本文での意味」(日本語、別工程で確定済み)が添えられています。これは、同じ形の表現が複数の意味・用法を持つ場合にどの意味の表現かを特定するための目印です。解説は、この意味に偏らず、表現の核となる意味と一般的な用法全体から説明してください。そのうえで、この意味が表現の用法全体の中でどこに位置づくかが自然に読み取れるようにし、この意味と矛盾する説明はしないでください。この意味そのものを言い換えて繰り返すことは目的ではありません。
"""
P1_BODY = """
# 解説の書き方
各表現について、学習者が自分の英語に取り入れられるように、次の観点から学習価値の高い内容を、必要十分な量の自然な日本語の文章で説明してください。すべての観点を機械的に列挙する必要はありません。
- 表現の核となる意味
- 主要な用法と、使われる場面
- よく使われるコロケーション(語の組み合わせ)
- 重要な類義語・近似表現との違い
- 自然に存在する比喩的・拡張的な用法
- 複合表現(語が組み合わさってできた語句)では、学習価値の中心となる語句(その語の一般的な使い方を知ると応用がきく部分)を中心に説明してよい。
- 使用頻度の順位(「最も一般的」「よく使われる順に」など)を、根拠なく断定しない。類義語との違いも、過度に断定せず、自然な英語として正確に説明する。
- 自然に存在する用法だけを書き、不自然な用法・用例を創作しない。すべての観点を無理に当てはめない。
- 文法の解説(構造・活用・語順など)には脱線しない。
- 説明の水増しをしない。「ほかの場面で使うと」という独立した追加例文は書かない(語句の組み合わせを示すコロケーションの表記は可)。

# 出力形式
Markdownのみ。表現ごとに次の形式で、前置き・後書きは付けない。
### 1. (英語表現)
(解説文。自然な日本語の文章。箇条書きは必要な場合のみ)
### 2. ...
"""
def p1_prompt(kps, arm):
    if arm == "beta":
        items = "\n".join(f"{i}. 英語表現: {k}\n   本文での意味: {g}" for i, (k, g, s) in enumerate(kps, 1))
        head = P1_HEAD + P1_BETA_NOTE
    else:
        items = "\n".join(f"{i}. 英語表現: {k}" for i, (k, g, s) in enumerate(kps, 1))
        head = P1_HEAD
    return head + "\n# 解説する英語表現\n" + items + "\n" + P1_BODY

# ---------- Prompt: Part 2 Step A (選定) ----------
STEPA = """あなたは英語読解指導の専門家です。下の英語本文(Advancedレベル)から、日本語話者の学習者(B1〜B2相当)が読解でつまずきやすく、文法・構文の解説によって理解が深まる英文を選びます。この工程では解説文は書きません(解説は別の工程が行います)。選定だけを行ってください。

# 作品・レベル
- 作品: {label}
- レベル: Advanced

# 本文(段落番号[P1]〜[P{n}]は参照用。引用では番号を書かない)
{numbered}

# 選定の観点
- 文法・構文の難しさ
- 文の構造を誤解しやすいか(主語・動詞・修飾関係・情報のつながりをつかみにくいか)
- 通常の語順・構造との違い
- 構文によって生じる意味やニュアンス
- 解説による学習価値(解説を読むと、その文の理解がどれだけ深まるか)
文法用語の難しさそのものは評価しない。
- 優先して検討する文の例: 語順が通常と異なる文、長い修飾語句・挿入・省略・並列・比較表現が重なって構造が見えにくい文、字面どおりに読むと意味を取り違えやすく構文の理解が必要な文。これらは例であり、該当する文が本文になければ無理に選ばない。
- 基礎的な文法項目(命令文、基本的な接続、前置詞句、分詞構文や付帯状況のwithなどの基本形、関係詞の基本用法、基本的な時制・受動態・比較・仮定法など)を説明するだけの選定はしない。特殊な用法や重要な表現効果がある場合に限る。
- 選ぶ文は0〜2個。解説価値の高い文が本文にない場合は0個とする。基礎的な文法項目を埋め草として選ばない。無理に2個選ばない。
- 本文全体から候補の文を複数検討し、解説価値が最も高い文を選ぶ。

# 出力(JSONオブジェクト1個のみ。前置き・後書き・コードフェンスなし)
{{
  "candidates_considered": [{{"para": "P4", "note": "検討した候補の文について、採否の理由を1行"}}],
  "selected": [
    {{
      "para": "P4",
      "sentence": "選んだ1文を本文から一字一句そのまま(逐語)",
      "construct_ja": "構文の名前(短く)",
      "points_ja": ["解説で押さえるべき点(最大3つ、短く)"],
      "context_ja": "その文の本文中での位置づけを1文で(本文に書かれた事実のみ。解釈や評価は書かない)",
      "reason_dev": "選定理由(開発者向けの記録。1〜2文。この欄はユーザー向け解説には使われない)"
    }}
  ],
  "none_reason_dev": "selectedが空のとき、その理由を1文。空でなければ空文字"
}}
- candidates_consideredは、検討した候補を最大5件(選んだ文を含む)。
- selectedは0〜2件。0件なら空配列。
- construct_ja・points_ja・context_jaは、ユーザー向け解説の材料になる。文の内容として書き、難易度・誤解しやすさ・学習価値などの評価語を入れない。
"""
def stepa_prompt(d):
    return STEPA.format(label=d["label"], n=len(d["body"]), numbered=d["numbered"])

# ---------- Prompt: Part 2 Step B (執筆) ----------
STEPB = """あなたは英語学習の解説を書く執筆者です。別の工程で選ばれた英文と構文について、日本語話者の学習者(B1〜B2相当)が読んで理解できる解説を、自然で分かりやすい日本語で書いてください。この工程では英文の選定は行いません。渡された英文と構文をそのまま解説します。

# 解説する英文(別工程で確定済み)
{items}

# 書き方
各英文について、次の順序で書く。
1. 日本語訳(自然な訳)
2. 文法・構文の仕組み: 渡された「構文」と「押さえる点」を、文のどの部分が何の働きをしているかを英文の該当箇所を示して具体的に説明する。教科書的な一般説明で終わらず、この英文を読み解く助けになる説明にする。
3. 通常の表現・語順との比較: 比較するとこの英文の仕組みが分かりやすくなる場合だけ書く。本文にない英文を示すときは「比較用」と明記し、本文の引用と区別する。不要なら、この項目自体を出力しない。
4. 意味・ニュアンス・表現効果: その構文によって、意味・ニュアンス・焦点・表現効果がどうなるか。「本文での位置づけ」の事実と結びつけて説明する。

- 学習者がそのまま読んで価値を感じられる、読みやすい文章にする。形式的・冗長な説明、同じ内容の繰り返しをしない。
- ユーザー向けの解説であり、選定理由・難易度の評価・品質の判定・工程への言及(「選ばれた」「学習価値が高い」「Advancedの学習者でも難しい」等)は一切書かない。
- 本文にない事実・登場人物の言動を作らない。「本文での位置づけ」に書かれた事実の範囲で述べる。
- 「前の文」「後の文」は、対象の英文を読み解くための本文の前後関係の参考である(解説する対象は各項目の「英文」のみ)。前後の文を引用するときも一字一句そのまま(逐語)引用する。
- 「参考訳」が渡されている場合は、それと矛盾しない日本語訳にする(同じ英文に食い違う訳を並べない)。
- 本文の英文を引用するときは、渡された英文から一字一句そのまま(逐語)引用する。
- 英文そのものの再掲(見出しとしての掲載)は不要(別途表示される)。

# 出力形式
Markdownのみ。前置き・後書きなし。英文ごとに、次の区切りと見出し行を使う。
=====ITEM 1=====
【日本語訳】
(...)
【文法・構文の仕組み】
(...)
【通常の表現・語順との比較】(不要なら、この見出し行と本文ごと出力しない)
(...)
【意味・ニュアンス・表現効果】
(...)
=====ITEM 2=====(英文が2つのときだけ。同じ形式)
"""
def stepb_items(selected):
    out = []
    for i, s in enumerate(selected, 1):
        pts = "\n".join(f"     - {p}" for p in s["points_ja"])
        blk = f"[{i}] 英文: {s['sentence']}\n   構文: {s['construct_ja']}\n   押さえる点:\n{pts}\n   本文での位置づけ: {s['context_ja']}"
        if s.get("prev"): blk += f"\n   前の文(本文): {s['prev']}"
        if s.get("next"): blk += f"\n   後の文(本文): {s['next']}"
        if s.get("ref_ja"): blk += f"\n   参考訳(別工程で確定済み): {s['ref_ja']}"
        out.append(blk)
    return "\n".join(out)
def stepb_prompt(selected):
    return STEPB.format(items=stepb_items(selected))

# ---------- Prompt: Part 3/4 (Trial-03 03dのPart 3/4ブロックをそのまま。Part 1/2は別工程) ----------
def p34_prompt(work, part2_note_text, part1_note_text="<<Part 1の解説>>"):
    full = r3.build(work, "03d")
    a = full.index("## Part 1. Vocabulary"); b = full.index("## Part 3. Nuance")
    p = full[:a] + full[b:]
    p = r3.sub_once(p, "# 出力する内容(4つのPartをすべて、この順序・この見出しで)", f"# Part 1の解説(別工程で確定済み。Part 3はこれらと内容を重複させない)\n{part1_note_text}\n\n# Part 2で扱う文(別工程で確定済み。Part 3はこれらと内容を重複させない)\n{part2_note_text}\n\n# 出力する内容(Part 3とPart 4のみ、この順序・この見出しで。Part 1・Part 2は別工程で作成済み)")
    p = r3.sub_once(p, "出力はMarkdownのみ。上記の見出し(## Part 1〜4)構成を守り", "出力はMarkdownのみ。上記の見出し(## Part 3、## Part 4)構成を守り")
    blk = lambda s: s[s.index("## Part 3. Nuance"):s.index("\n# 制約")]
    assert blk(p) == blk(full)  # Part 3/4ブロックは03dと完全一致
    return p

def part1_note(inp, p1):
    return "\n".join(f"- {it['kp']}: {p1[i][1]}" for i, it in enumerate(inp, 1))

def part2_note(selected):
    if not selected: return "なし(Part 2は0件)"
    return "\n".join(f"- {s['sentence']}(構文: {s['construct_ja']})" for s in selected)

# ---------- 組立(決定論。LLMを使わない) ----------
ZERO_P2 = "今回の本文には、このPartで特に取り上げる難所となる構文はありませんでした。"
def parse_p1(txt, n=3):
    parts = re.split(r"(?m)^### (\d+)\.\s*(.*)$", txt)
    res = {}
    for i in range(1, len(parts), 3):
        res[int(parts[i])] = (parts[i + 1].strip(), parts[i + 2].strip())
    assert sorted(res) == list(range(1, n + 1)), list(res)
    return res
def _qn(x):  # 長さ保存の正規化(曲がった引用符/アポストロフィ -> 直線)
    return x.replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"')
def resolve_verbatim(d, para, sentence):
    """M1: 本文の該当段落から文を引き当て、本文側の逐語文字列を返す。見つからなければ例外(自動再試行しない)。構造上の保証であり判定器ではない。"""
    m = re.fullmatch(r"P(\d+)", str(para).strip())
    assert m and 1 <= int(m.group(1)) <= len(d["body"]), ("bad para", para)
    pi = int(m.group(1)) - 1; body = d["body"][pi]
    toks = _qn(sentence).split(); assert toks, "empty sentence"
    mm = re.search(r"\s+".join(re.escape(t) for t in toks), _qn(body))
    assert mm, ("sentence not found in para", para, sentence[:60])
    return body[mm.start():mm.end()], pi, mm.start(), mm.end()
_SENT_RE = re.compile(r".+?[.!?\u2026]+[\u201d\"\u2019']?(?=\s|$)|.+?$", re.S)
def _sents(t): return [x.strip() for x in _SENT_RE.findall(t) if x.strip()]
def local_context(d, pi, a, b):
    """R1: 選定文の前後1文を本文から逐語で取る(段落をまたぐ)。"""
    T = "\n\n".join(d["body"]); off = sum(len(x) + 2 for x in d["body"][:pi])
    bef = _sents(T[:off + a]); aft = _sents(T[off + b:])
    return (bef[-1] if bef else ""), (aft[0] if aft else "")
def parse_stepa(txt, d=None, inp=None):
    m = re.search(r"\{.*\}", txt, re.S)
    j = json.loads(m.group(0))
    assert len(j["selected"]) <= 2
    for s in j["selected"]:
        for k in ("para", "sentence", "construct_ja", "points_ja", "context_ja", "reason_dev"): assert k in s, k
        if d is not None:
            verb, pi, a, b = resolve_verbatim(d, s["para"], s["sentence"])
            s["sentence_llm_raw"] = s["sentence"]; s["sentence_replaced_by_body"] = (verb != s["sentence"]); s["sentence"] = verb
            s["prev"], s["next"] = local_context(d, pi, a, b)
            if inp:  # R4: KPの引用英文と一致したら固定訳を参考訳として渡す
                for it in inp:
                    if _qn(it["sentence"]) == _qn(verb): s["ref_ja"] = it["sentence_ja"]
    return j
def parse_stepb(txt, n):
    items = re.split(r"(?m)^=====ITEM (\d+)=====\s*$", txt)
    res = {int(items[i]): items[i + 1].strip() for i in range(1, len(items), 2)}
    assert sorted(res) == list(range(1, n + 1)), list(res)
    return res
def bold_headings(t):
    return re.sub(r"(?m)^【(.+?)】\s*$", r"**\1**", t)

def assemble_user(inp, p1, stepa, stepb, p34):
    L = ["## Part 1. Vocabulary & Expressions", ""]
    for i, it in enumerate(inp, 1):
        L += [f"### {i}. {it['kp']}", "",
              f"1. **英語表現:** {it['kp']}",
              f"2. **日本語の意味(本文中での意味):** {it['gloss_in_text_ja']}",
              f"3. **本文中の英文:**  \n   “{it['sentence']}”",
              f"4. **英文の日本語訳:**  \n   {it['sentence_ja']}",
              "5. **解説:**", "", p1[i][1], ""]
    L += ["## Part 2. Grammar & Sentence Structure", ""]
    sel = stepa["selected"]
    if not sel: L += [ZERO_P2, ""]
    for i, s in enumerate(sel, 1):
        L += [f"### {i}. 対象となる本文英文", "", f"> {s['sentence']}", "", bold_headings(stepb[i]), ""]
    L += [p34.strip(), ""]
    return "\n".join(L)

def assemble_dev(work, runid, stepa, usages, user_path):
    L = [f"# OUTPUT_04 DEV記録(開発者向け。ユーザー向け本文ではない) {work} {runid}", "", f"ユーザー向け完成形: `{os.path.basename(user_path)}`", "",
         "## Step A: 候補・選定理由(DEV専用。ユーザー向け本文へは渡していない)", "", "```json", json.dumps(stepa, ensure_ascii=False, indent=1), "```", "", "## usage", "", "| tag | model | sec | in | cached | out | reasoning | 円(@160) |", "|---|---|---|---|---|---|---|---|"]
    for u in usages:
        L.append(f"| {u['tag']} | {u['model_actual']} | {u['elapsed_sec']} | {u['input_tokens']} | {u['cached_input_tokens']} | {u['output_tokens']} | {u['reasoning_tokens']} | {u['cost_jpy_at_160']} |")
    return "\n".join(L) + "\n"

# ---------- 実行(LLM呼出は注入) ----------
def run_pipeline(work, runid, llm, arm="alpha"):
    d = work_data(work); inp = load_inputs()[work]
    kps = [(x["kp"], x["gloss_in_text_ja"], x["sentence"]) for x in inp]
    # 並列: Part 1 と Step A は独立。Step A -> (Step B || Part 3/4) は依存。
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=2) as ex:
        f1 = ex.submit(llm, p1_prompt(kps, arm), f"04{arm[0]}_{runid}_p1_{work}")
        fa = ex.submit(llm, stepa_prompt(d), f"04_{runid}_stepA_{work}")
        r1, ra = f1.result(), fa.result()
    stepa = parse_stepa(ra[0], d, inp); sel = stepa["selected"]
    p1 = parse_p1(r1[0])
    with ThreadPoolExecutor(max_workers=2) as ex:
        fb = ex.submit(llm, stepb_prompt(sel), f"04_{runid}_stepB_{work}") if sel else None
        f34 = ex.submit(llm, p34_prompt(work, part2_note(sel), part1_note(inp, p1)), f"04_{runid}_p34_{work}")
        rb = fb.result() if fb else None; r34 = f34.result()
    stepb = parse_stepb(rb[0], len(sel)) if sel else {}
    user = assemble_user(inp, p1, stepa, stepb, r34[0])
    usages = [x[1] for x in (r1, ra, rb, r34) if x]
    return user, stepa, usages

import threading
_SPENT = {"jpy": 0.0}; _LOCK = threading.Lock(); CAP_JPY = 18.0  # 委任_09上限20円に対する安全余裕(新規call拒否)
def real_llm(prompt, tag):
    assert os.environ.get("TRIAL04_PAID_APPROVED") == "1", "paid call refused (Phase 0 / 委任_09 Fable Go required)"
    with _LOCK: assert _SPENT["jpy"] < CAP_JPY, ("cost cap reached; new calls refused", _SPENT)
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

# ---------- R5/β腕: 単独実行 ----------
def run_p1_only(work, runid, llm, arm):
    inp = load_inputs()[work]; kps = [(x["kp"], x["gloss_in_text_ja"], x["sentence"]) for x in inp]
    r = llm(p1_prompt(kps, arm), f"04{arm[0]}_{runid}_p1_{work}"); parse_p1(r[0])
    open(os.path.join(BASE, f"OUTPUT_04_{work}_{runid}_P1{arm.upper()}.md"), "w", encoding="utf-8", newline="\n").write(r[0])
    return r[1]
def run_stepa_only(work, runid, llm):
    d = work_data(work); inp = load_inputs()[work]
    r = llm(stepa_prompt(d), f"04_{runid}_stepA_{work}")
    j = parse_stepa(r[0], d, inp)
    open(os.path.join(BASE, f"OUTPUT_04_{work}_{runid}_STEPA_DEV.json"), "w", encoding="utf-8", newline="\n").write(json.dumps(j, ensure_ascii=False, indent=1))
    return r[1]
def run_full(work, runid, llm):
    user, stepa, us = run_pipeline(work, runid, llm, arm="alpha")
    up = os.path.join(BASE, f"OUTPUT_04_{work}_{runid}_USER.md"); dp = os.path.join(BASE, f"OUTPUT_04_{work}_{runid}_DEV.md")
    open(up, "w", encoding="utf-8", newline="\n").write(user); open(dp, "w", encoding="utf-8", newline="\n").write(assemble_dev(work, runid, stepa, us, up))
    return us
def batch(llm):
    """委任_09の全構成を1 launchで実行(各job失敗は記録のみ。自動再試行しない)。"""
    from concurrent.futures import ThreadPoolExecutor
    jobs = []
    for w in WORKS:
        for r in ("r1", "r2"): jobs.append((f"full_{w}_{r}", lambda w=w, r=r: run_full(w, r, llm)))
    for w in WORKS:
        for r in ("r1", "r2"): jobs.append((f"p1beta_{w}_{r}", lambda w=w, r=r: run_p1_only(w, r, llm, "beta")))
        for r in ("r3", "r4"): jobs.append((f"stepA_{w}_{r}", lambda w=w, r=r: run_stepa_only(w, r, llm)))
    errs = {}
    def go(j):
        name, fn = j
        try: fn(); return name, None
        except BaseException as e: return name, repr(e)
    with ThreadPoolExecutor(max_workers=9) as ex:
        for name, e in ex.map(go, jobs):
            print(name, "OK" if e is None else "ERR " + e, flush=True)
            if e: errs[name] = e
    json.dump(dict(errors=errs, spent_jpy=_SPENT["jpy"]), open(os.path.join(BASE, "batch_04_result.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("spent_jpy", _SPENT["jpy"], "errors", len(errs))

# ---------- Part 1 混入確認(dry-run用。新設Checkerではなく、Prompt作成時の確認) ----------
_STOP_CAPS = {"The", "A", "An", "I", "In", "It", "He", "She", "They", "We", "This", "That", "But", "And", "Yet", "Then", "His", "Her", "Not", "Nothing", "At", "One", "Will", "Please", "Look", "Cut", "Twenty", "Still", "Suddenly", "Footsteps", "Inside", "Outside", "Each", "Finally", "Slowly", "For", "By", "Like", "How", "Give", "My", "On", "No", "If", "When", "As", "So", "What", "There", "Here", "Now", "After", "Is", "Do", "Or", "To", "Of", "You", "Yes", "Let"}
def leak_check(prompt, d):
    """Part 1 Promptに本文固有情報が混入していないことを確認: 本文の語4-gram(KP語句内を除く)・KPの引用文・本文中の大文字語(固有名詞候補)・作品を示す日本語語。"""
    issues = []
    toks = lambda s: re.findall(r"[a-z']+", s.lower().replace("’", "'"))
    pj = " ".join(toks(prompt))
    kpwords = " ".join(" ".join(toks(k)) for k, _, _ in d["kp"])
    btoks = toks(d["text"])
    for i in range(len(btoks) - 3):
        g = " ".join(btoks[i:i + 4])
        if g in pj and g not in kpwords: issues.append(("4gram", g))
    for _, _, s in d["kp"]:
        if s in prompt: issues.append(("sentence", s[:40]))
    for name in set(re.findall(r"\b[A-Z][a-z]+\b", d["text"])):
        if name in _STOP_CAPS: continue
        if re.search(r"\b" + re.escape(name) + r"\b", prompt): issues.append(("capword?", name))
    for ja in ("賢者", "開いた窓", "イグ・ノーベル", "ゴキブリ", "ジム", "デラ", "ヴェラ", "ノーベル"):
        if ja in prompt: issues.append(("ja_term", ja))
    return sorted(set(issues))

def dry_run():
    res = {}
    ins = load_inputs()
    for w in WORKS:
        d = work_data(w); kps = [(x["kp"], x["gloss_in_text_ja"], x["sentence"]) for x in ins[w]]
        assert [k for k, _, _ in kps] == [k for k, _, _ in d["kp"]]
        prompts = {"p1a": p1_prompt(kps, "alpha"), "p1b": p1_prompt(kps, "beta"), "stepA": stepa_prompt(d),
                   "stepB": stepb_prompt([dict(sentence="<<StepAが選んだ英文>>", construct_ja="<<構文名>>", points_ja=["<<要点>>"], context_ja="<<位置づけ>>")]),
                   "p34": p34_prompt(w, "<<StepAが選んだ英文(0件なら『なし』)>>")}
        for k, p in prompts.items():
            open(os.path.join(BASE, f"_prompt_04_{w}_{k}.txt"), "w", encoding="utf-8", newline="\n").write(p)
        leaks = {k: leak_check(prompts[k], d) for k in ("p1a", "p1b")}
        res[w] = {k: dict(chars=len(p), sha=hashlib.sha256(p.encode()).hexdigest()[:16]) for k, p in prompts.items()}
        res[w]["p1_leaks"] = leaks
        print(w, {k: len(p) for k, p in prompts.items()}, "P1 leaks:", leaks)
    json.dump(res, open(os.path.join(BASE, "dryrun_04.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

def selftest():
    def mock(prompt, tag):
        u = dict(tag=tag, model_actual="MOCK", elapsed_sec=0, input_tokens=0, cached_input_tokens=0, output_tokens=0, reasoning_tokens=0, cost_jpy_at_160=0)
        if "_p1_" in tag: return "### 1. a\nAAA\n### 2. b\nBBB\n### 3. c\nCCC", u
        if "_stepA_" in tag:
            if "zero" in tag: return json.dumps(dict(candidates_considered=[], selected=[], none_reason_dev="none")), u
            return "```json\n" + json.dumps(dict(candidates_considered=[dict(para="P1", note="x")], selected=[dict(para="P6", sentence="Outside a hair-goods shop, she paused just long enough to catch her breath.", construct_ja="倒置", points_ja=["p"], context_ja="c", reason_dev="DEVREASON")], none_reason_dev="")) + "\n```", u
        if "_stepB_" in tag: return "=====ITEM 1=====\n【日本語訳】\nT\n【文法・構文の仕組み】\nM\n【意味・ニュアンス・表現効果】\nE", u
        return "## Part 3. Nuance & Deeper Understanding\nx\n\n## Part 4. Think & Express\ny", u
    # M1/R1/R4 単体確認
    dg = work_data("gift"); ingift = load_inputs()["gift"]
    v, pi, a, b = resolve_verbatim(dg, "P4", "One was Jim's gold watch, handed down from his grandfather to his father, and then to him.")
    assert v == "One was Jim\u2019s gold watch, handed down from his grandfather to his father, and then to him.", v
    pv, nx = local_context(dg, pi, a, b); assert pv == "They owned two things that made them proud." and nx == "The other was Della\u2019s long brown hair.", (pv, nx)
    v5, pi5, a5, b5 = resolve_verbatim(dg, "P3", "Then she caught sight of herself in the mirror.")
    pv5, nx5 = local_context(dg, pi5, a5, b5); assert pv5 == "For a while, she cried on their shabby couch." and nx5.startswith("They owned"), (pv5, nx5)
    j = parse_stepa(json.dumps(dict(candidates_considered=[], selected=[dict(para="P3", sentence="Then she caught sight of herself in the mirror.", construct_ja="x", points_ja=["p"], context_ja="c", reason_dev="r")], none_reason_dev="")), dg, ingift)
    assert j["selected"][0].get("ref_ja"), "R4 ref_ja"
    try:
        parse_stepa(json.dumps(dict(candidates_considered=[], selected=[dict(para="P4", sentence="One was Jim's silver watch.", construct_ja="x", points_ja=["p"], context_ja="c", reason_dev="r")], none_reason_dev="")), dg, ingift); raise SystemExit("M1 should raise")
    except AssertionError: pass
    sb = stepb_prompt(j["selected"]); assert "前の文(本文): For a while" in sb and "後の文(本文): They owned" in sb and "参考訳" in sb
    user, stepa, us = run_pipeline("gift", "mock", mock)
    assert "DEVREASON" not in user and "候補" not in user and "選定理由" not in user
    assert "**日本語訳**" in user and "> Outside a hair-goods shop" in user and "5. **解説:**" in user and "実用性を重視した解説" not in user
    zu, _, us0 = run_pipeline("gift", "zero", mock)
    assert ZERO_P2 in zu and len(us0) == 3  # 0件: Step B呼出なし(3 call)
    assert len(us) == 4
    print("selftest OK (mock). calls: normal=4, zero-selection=3")
    print(user[:1200])

if __name__ == "__main__":
    m = sys.argv[1]
    if m == "make-inputs":
        json.dump(extract_ja_from_03d(), open(os.path.join(BASE, "INPUT_04.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    elif m == "dry-run": dry_run()
    elif m == "selftest": selftest()
    elif m == "batch": batch(real_llm)
    elif m == "send-p1": run_p1_only(sys.argv[2], sys.argv[3], real_llm, sys.argv[4])
    elif m == "send-stepa": run_stepa_only(sys.argv[2], sys.argv[3], real_llm)
    elif m == "send":
        work, runid = sys.argv[2], sys.argv[3]
        user, stepa, us = run_pipeline(work, runid, real_llm, arm=(sys.argv[4] if len(sys.argv) > 4 else "alpha"))
        up = os.path.join(BASE, f"OUTPUT_04_{work}_{runid}_USER.md"); dp = os.path.join(BASE, f"OUTPUT_04_{work}_{runid}_DEV.md")
        open(up, "w", encoding="utf-8", newline="\n").write(user); open(dp, "w", encoding="utf-8", newline="\n").write(assemble_dev(work, runid, stepa, us, up))
