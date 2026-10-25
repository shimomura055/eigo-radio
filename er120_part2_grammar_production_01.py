# ============================================================
# er120_part2_grammar_production_01.py
# PART2-GRAMMAR-PRODUCTION-WIRING-01 委任_01(2026-10-25)
# 学習テキスト Part 2「Grammar & Sentence Structure」+ Trial-08構文選定方式 の Production module(Family X/Y/Z共通)
# ============================================================
# 承認: ユーザー2026-10-25 APPROVED_FOR_PRODUCTION(原文 docs/pm/delegation_log/2026-10-25_PART2-GRAMMAR-PRODUCTION-WIRING-01_USER.md)。
#   (1) Part 2 文法・構文解説(Trial-07で検証した機能) (2) Trial-08構文選定方式(Tier1=倒置以外の適格 > Tier2=倒置 > Tier3=なし)。
#   Tier内順位の改善・HIGH判定の安定化・OTHER分類の拡張は承認対象外(本moduleは一切行わない)。
# 設計: docs/research/PART2-GRAMMAR-PRODUCTION-WIRING-01/DESIGN_01.md。既存仕様の固定: 同EXISTING_SPEC_CHECK_01.md。
#
# 状態: module本体のみ(委任_01)。runner(er019/er026/er062)・er119(HR共通核)・公開ページへは未配線。
#   したがって本moduleを呼ぶProduction経路は現時点で存在せず(PRODUCTION_WIREDではない)、API呼出も発生しない。
#   routing登録(STUDY_TEXT_GRAMMAR_EXTRACT / STUDY_TEXT_GRAMMAR_EXPLAIN → SUPPORT_MODEL)は次委任のer006追記で行う(REQUIRED_ROUTING_ENTRIES)。
#   登録前は routing.require_model が ModelContractViolation を出す(fail-closed)。
#
# Trial-07/08の規則の移植(逐語):
#   Step A'' Prompt = Trial-08のSTEPA8(Trial-07 STEPA7の再確認指示1文のみ差替) / Step B Prompt = Trial-04 STEPB / 分類・適格条件eligible7・
#   Tier順位select_tiered・resolve7(段落境界連結の再解決)・verify_single_span・逐語一致検査・最大1件・0件許容 を同一ロジックで移植。
#   Prompt byte一致・全29標本のraw応答再parse→select_tiered一致を test で固定する(Trial資産はtestでのみ読み、本moduleはimportしない)。
#
# 本moduleは docs/research のTrial資産をimportしない(Dangling Reference禁止)。
# ============================================================
from __future__ import annotations

import hashlib
import html
import json
import os
import re
import time
import unicodedata

import er006_model_routing_contract_01 as routing

MANAGEMENT_ID = "PART2-GRAMMAR-PRODUCTION-WIRING-01"
PROCESS_EXTRACT = "STUDY_TEXT_GRAMMAR_EXTRACT"
PROCESS_EXPLAIN = "STUDY_TEXT_GRAMMAR_EXPLAIN"
MODEL = routing.SUPPORT_MODEL            # gpt-6-luna(Trial-07/08と同一・現行SUPPORT_MODEL)
REQUIRED_ROUTING_ENTRIES = {PROCESS_EXTRACT: "SUPPORT_MODEL", PROCESS_EXPLAIN: "SUPPORT_MODEL"}   # 次委任でer006 PROCESS_MODEL_MAPへ追記
LEVEL = "Advanced"                       # Trial-07/08は全てAdvanced本文。Standard(a2)への拡張は新仕様=行わない
SCHEMA_CANDIDATES = "grammar_candidates_v1"
SCHEMA_RESULT = "part2_grammar_v1"
CANDIDATES_FILENAME = "grammar_candidates.json"
RESULT_FILENAME = "part2_result.json"
PART2_FILE_STEM = "part2_grammar_sentence_structure"
MAXOUT_EXTRACT = 13000                   # Trial-07/08のMAXOUT_A
MAXOUT_EXPLAIN = 6000                    # Trial-07のMAXOUT_B
TOP_N = 2                                # HR: TOP1/TOP2(ユーザー正式決定)

# ------------------------------------------------------------
# Prompt(Trial逐語。sha固定。byte一致をtestで固定)
# ------------------------------------------------------------
STEPA_PROMPT = """あなたは英語読解指導の専門家です。下の英語本文(Advancedレベル)を、日本語話者の学習者(B1〜B2相当)の読解の観点で点検します。この工程の仕事は、本文の全文を見て、構文上の特徴のある文に「分類コード」を付けて漏れなく洗い出すことです。どの文を解説するかの選択は、この工程では行いません(別の工程が決まった規則で、最大1件を選びます。該当がなければ0件です)。解説文も書きません。

# 作品・レベル
- 作品: {label}
- レベル: Advanced

# 本文(段落番号[P1]〜[P{n}]は参照用。引用では番号を書かない)
{numbered}

# 手順
1. 本文を最初から最後まで、段落を1つずつ確認し、すべての文について、下の「分類コード」に該当する特徴があるかを確認する。該当する文は、数に上限を設けず、すべてfeaturesに列挙する(1段落に複数あれば文ごとに列挙)。特にINV以外の分類(CLEFT・CMP・FRONT・HEAVY・POSTMOD・SPEC・ELL・APPOS)について、全段落で見落としがないか最後にもう一度確認する。どの文にも該当しない段落は、段落番号をno_feature_parasに書く(featuresに載せた段落は書かない)。
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

STEPB_PROMPT = """あなたは英語学習の解説を書く執筆者です。別の工程で選ばれた英文と構文について、日本語話者の学習者(B1〜B2相当)が読んで理解できる解説を、自然で分かりやすい日本語で書いてください。この工程では英文の選定は行いません。渡された英文と構文をそのまま解説します。

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

STEPA_PROMPT_SHA256 = hashlib.sha256(STEPA_PROMPT.encode("utf-8")).hexdigest()
STEPB_PROMPT_SHA256 = hashlib.sha256(STEPB_PROMPT.encode("utf-8")).hexdigest()
ZERO_P2 = "今回の本文には、このPartで特に取り上げる難所となる構文はありませんでした。"   # Trial-04 ZERO_P2(0件時の文面)
PAGE_FORBIDDEN_RE = re.compile(r"\(A2\)|\(B1\)|B1B|English:|英語:|EN:|日本語:|JA:")   # Part 1と同じ(ページ非表示語)
EXPLANATION_HEADINGS = ["日本語訳", "文法・構文の仕組み", "通常の表現・語順との比較", "意味・ニュアンス・表現効果"]
EXPLANATION_REQUIRED = ["日本語訳", "文法・構文の仕組み", "意味・ニュアンス・表現効果"]    # 比較は「不要なら出力しない」(Prompt)

# ------------------------------------------------------------
# 例外
# ------------------------------------------------------------
class Part2Error(RuntimeError):
    """Part 2の生成失敗(fail-closed。呼出側はSTOPして次コマンドを案内する)。"""


class Part2InputError(ValueError):
    """入力不正(課金前に拒否)。"""


class Part2StructureError(ValueError):
    """LLM応答の構造不正(技術retry対象)。"""


class Part2Stale(Part2Error):
    """保存済みartifactが無い/古い(使う側のfail-closed確認)。"""


class Part2ReviewError(ValueError):
    """Human reviewの内容が不正(選択肢外・候補外・stale)。"""


# ------------------------------------------------------------
# 本文の取り出し(Trial work_data7と同一ロジック)
# ------------------------------------------------------------
def paragraphs_from_article_md(text: str, *, stop_heading_prefixes: tuple = ("## In one line",)) -> list:
    """X: 先頭 `# ` タイトル段落を除き、空行区切りの段落列。stop_heading_prefixes始まりの段落以降(末尾の要約節)は除く。
    Z: er026 `canonical_article_text(text).split("\\n\\n")` と一致(melos r2で29段落一致を確認)なので、Zの呼出側はそれを直接渡してよい。"""
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not paras or not paras[0].startswith("# "):
        raise Part2InputError("先頭が `# ` タイトル行ではありません")
    body = paras[1:]
    for k, p in enumerate(body):
        if any(p.startswith(h) for h in stop_heading_prefixes):
            body = body[:k]
            break
    if not body:
        raise Part2InputError("本文段落がありません")
    return body


def numbered_body(paragraphs: list) -> str:
    return "\n\n".join(f"[P{i}] {x}" for i, x in enumerate(paragraphs, 1))


def _check_paragraphs(paragraphs) -> list:
    if not isinstance(paragraphs, (list, tuple)) or not paragraphs or not all(isinstance(p, str) and p.strip() for p in paragraphs):
        raise Part2InputError("paragraphsは非空文字列のlistである必要があります")
    return list(paragraphs)


def text_sha256(paragraphs: list) -> str:
    return hashlib.sha256("\n\n".join(paragraphs).encode("utf-8")).hexdigest()


def stepa_prompt(paragraphs: list, label: str) -> str:
    paragraphs = _check_paragraphs(paragraphs)
    if not isinstance(label, str) or not label.strip() or "\n" in label:
        raise Part2InputError("labelは1行の非空文字列")
    return STEPA_PROMPT.format(label=label, n=len(paragraphs), numbered=numbered_body(paragraphs))


# ------------------------------------------------------------
# 逐語解決(Trial run_trial_04/06/07から逐語移植)
# ------------------------------------------------------------
_QCH = "“”‘’\"'`"


def _qn(x: str) -> str:   # 長さ保存の正規化(曲がった引用符/アポストロフィ -> 直線)
    return x.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')


def strip_quotes(s):
    s = (s or "").strip()
    while s and s[0] in _QCH:
        s = s[1:].lstrip()
    # 文末の引用符は、直前が文末記号のときだけ除去(所有格のアポストロフィを削らない)
    while len(s) >= 2 and s[-1] in _QCH and s[-2] in ".!?…,:;—-":
        s = s[:-1].rstrip()
    return s


def resolve_verbatim(d, para, sentence):
    """本文の該当段落から文を引き当て、本文側の逐語文字列を返す。見つからなければAssertionError(自動再試行しない)。"""
    m = re.fullmatch(r"P(\d+)", str(para).strip())
    assert m and 1 <= int(m.group(1)) <= len(d["body"]), ("bad para", para)
    pi = int(m.group(1)) - 1
    body = d["body"][pi]
    toks = _qn(sentence).split()
    assert toks, "empty sentence"
    mm = re.search(r"\s+".join(re.escape(t) for t in toks), _qn(body))
    assert mm, ("sentence not found in para", para, sentence[:60])
    return body[mm.start():mm.end()], pi, mm.start(), mm.end()


def resolve6(d, para, sentence):
    try:
        return resolve_verbatim(d, para, sentence)
    except AssertionError:
        s2 = strip_quotes(sentence)
        if s2 == (sentence or "").strip() or not s2:
            raise
        return resolve_verbatim(d, para, s2)


_SENT_RE = re.compile(r".+?[.!?…]+[”\"’']?(?=\s|$)|.+?$", re.S)


def _sents(t):
    return [x.strip() for x in _SENT_RE.findall(t) if x.strip()]


def local_context(d, pi, a, b):
    """選定文の前後1文を本文から逐語で取る(段落をまたぐ)。"""
    T = "\n\n".join(d["body"])
    off = sum(len(x) + 2 for x in d["body"][:pi])
    bef = _sents(T[:off + a])
    aft = _sents(T[off + b:])
    return (bef[-1] if bef else ""), (aft[0] if aft else "")


def _tok(s):
    return _qn(s).split()


def _para_tokens(d, i):
    return _tok(d["body"][i])


def _tn(t):
    return t.strip("\"'")   # 語の前後の引用符・アポストロフィ記号を無視して比較(両側に同じ正規化)


def resolve7(d, para, sentence):
    """resolve6を先に試し、失敗した場合に限り段落境界をまたぐ連結を検出して再解決する(Trial-07 resolve7と同一)。
    戻り値: (本文側逐語, 段落index, a, b, flag) flag=None|"cross_para_trimmed_tail"|"cross_para_trimmed_head"。"""
    try:
        v, pi, a, b = resolve6(d, para, sentence)
        return v, pi, a, b, None
    except AssertionError as e0:
        err = e0
    m = re.fullmatch(r"P(\d+)", str(para).strip())
    if not m or not (1 <= int(m.group(1)) <= len(d["body"])):
        raise err
    pi = int(m.group(1)) - 1
    toks = [_tn(x) for x in _tok(sentence)]
    if not toks:
        raise err
    ptoks = [_tn(x) for x in _para_tokens(d, pi)]
    praw = _para_tokens(d, pi)
    if pi + 1 < len(d["body"]):                                      # (a) 主張段落の末尾 + 次段落以降の先頭
        nxt = []
        for j in range(pi + 1, min(pi + 4, len(d["body"]))):
            nxt += [_tn(x) for x in _para_tokens(d, j)]
        for k in range(len(toks) - 1, 0, -1):
            pre, rest = toks[:k], toks[k:]
            if len(pre) <= len(ptoks) and ptoks[-len(pre):] == pre and nxt[:len(rest)] == rest:
                v, pi2, a, b = resolve_verbatim(d, para, " ".join(praw[-len(pre):]))
                return v, pi2, a, b, "cross_para_trimmed_tail"
    if pi > 0:                                                       # (b) 直前段落の末尾 + 主張段落の先頭
        prv = []
        for j in range(max(0, pi - 3), pi):
            prv += [_tn(x) for x in _para_tokens(d, j)]
        for k in range(1, len(toks)):
            head, suf = toks[:k], toks[k:]
            if len(suf) <= len(ptoks) and ptoks[:len(suf)] == suf and len(head) <= len(prv) and prv[-len(head):] == head:
                v, pi2, a, b = resolve_verbatim(d, para, " ".join(praw[:len(suf)]))
                return v, pi2, a, b, "cross_para_trimmed_head"
    raise err


def verify_single_span(d, para, sentence):
    """sentenceが主張段落1つの中の連続した逐語spanであり、段落区切りを含まない(連結・改変の最終検査)。"""
    m = re.fullmatch(r"P(\d+)", str(para).strip())
    if not m or not (1 <= int(m.group(1)) <= len(d["body"])):
        return False
    body = d["body"][int(m.group(1)) - 1]
    return bool(sentence) and "\n" not in sentence and sentence in body


# ------------------------------------------------------------
# 分類・適格条件(Trial-07 eligible7 / Trial-08 select_tiered と同一)
# ------------------------------------------------------------
STRONG = ["INV", "CLEFT", "CMP"]
MID = ["FRONT", "HEAVY", "POSTMOD", "SPEC", "ELL", "APPOS"]
PRIORITY = STRONG + MID                       # Tier内順位(INV>CLEFT>CMP>FRONT>HEAVY>POSTMOD>SPEC>ELL>APPOS)。承認対象外のため変更しない
TARGETS = {"SUBJECT", "VERB", "MODIFIEE", "OMITTED"}
FRONT_OK = {"PARTICIPLE", "ADJECTIVE", "AS_THOUGH", "NESTED_OR_LONG", "OBJECT_OR_COMPLEMENT"}


def _as_bool(v):
    if isinstance(v, bool):
        return v
    return str(v).strip().lower() in ("true", "はい", "yes")


def _cls(f):
    return str(f.get("feature_class", "")).strip().upper()


def _pnum(f):
    return int(re.sub(r"\D", "", f["para"]))


def base_ok(f):
    return bool(f.get("resolve_ok") and not f.get("duplicate") and _cls(f) in PRIORITY and not _as_bool(f.get("basic_only", True)))


def materials_ok(f):
    return bool(str(f.get("construct_ja", "")).strip() and isinstance(f.get("points_ja"), list)
                and any(str(x).strip() for x in f["points_ja"]) and str(f.get("context_ja", "")).strip())


def mid_cond(f):
    return str(f.get("misread_target", "")).strip().upper() in TARGETS and bool(f.get("misread_quote_in_sentence"))


def front_ok(f):
    return str(f.get("front_kind", "")).strip().upper() in FRONT_OK


def teaching_ok(f):
    return str(f.get("teaching_value", "")).strip().upper() == "HIGH" and bool(str(f.get("teaching_value_ja", "")).strip())


def eligible7(f):
    """適格: 基礎のみでない・OTHER除外・材料欄あり・teaching_value=HIGH(+teaching_value_ja)。
    中クラスはさらに misread_target∈列挙 かつ misread_quote逐語。FRONTはfront_kind∈FRONT_OK。ELLはomitted_words非空。"""
    if not (base_ok(f) and materials_ok(f) and teaching_ok(f)):
        return False
    if _cls(f) in STRONG:
        return True
    if not mid_cond(f):
        return False
    if _cls(f) == "FRONT" and not front_ok(f):
        return False
    if _cls(f) == "ELL" and not str(f.get("omitted_words", "")).strip():
        return False
    return True


def _order_key(f):
    return (PRIORITY.index(_cls(f)), _pnum(f), f.get("order", 0))


def is_inv(f):
    return _cls(f) == "INV"


def select_tiered(feats):
    """Trial-08 select_tieredと同一: Tier1=INV以外の適格をTrial-07の順位で並べ、Tier1が空のときだけTier2=適格なINV。両方空なら0件。最大1件。"""
    el = [f for f in feats if eligible7(f)]
    t1 = sorted([f for f in el if not is_inv(f)], key=_order_key)
    t2 = sorted([f for f in el if is_inv(f)], key=_order_key)
    return (t1 + t2)[:1], ("T1" if t1 else ("T2" if t2 else "T3"))


def rank_eligible(feats):
    """HR用の順位付き全適格list(TOP1/TOP2+残り)。順序は select_tiered と同一(Tier1全件 → Tier2全件)で、先頭は常に select_tiered の1件と一致する。
    追加LLM callなし。同一(段落, 文)の重複は先頭のみ(2位=同一文を除く次の適格)。戻り値: [(feature, tier), ...]"""
    el = [f for f in feats if eligible7(f)]
    t1 = sorted([f for f in el if not is_inv(f)], key=_order_key)
    t2 = sorted([f for f in el if is_inv(f)], key=_order_key)
    out, seen = [], set()
    for tier, grp in (("T1", t1), ("T2", t2)):
        for f in grp:
            k = (f.get("para"), _qn(f.get("sentence", "")))
            if k in seen:
                continue
            seen.add(k)
            out.append((f, tier))
    return out


def tier_table(feats):
    """全featureの適格/不適格理由(監査用。Trial-08 tier_tableと同一内容)。"""
    out = []
    for f in feats:
        c = _cls(f)
        why = []
        if not f.get("resolve_ok"):
            why.append("resolve_fail")
        if f.get("basic_only") in (True, "true", "True"):
            why.append("basic_only")
        if not materials_ok(f):
            why.append("no_materials")
        if not teaching_ok(f):
            why.append("TV=" + str(f.get("teaching_value")))
        if c in MID and not mid_cond(f):
            why.append("mid_cond")
        if c == "FRONT" and not front_ok(f):
            why.append("front_kind=" + str(f.get("front_kind")))
        if c == "ELL" and not str(f.get("omitted_words", "")).strip():
            why.append("ELL_no_omitted")
        if c not in PRIORITY:
            why.append("class=" + c)
        elig = eligible7(f)
        out.append(dict(para=f.get("para"), cls=c, tier=(("T2" if is_inv(f) else "T1") if elig else None), eligible=elig,
                        why_not=([] if elig else why), tv=f.get("teaching_value"), tv_ja=f.get("teaching_value_ja"),
                        front_kind=f.get("front_kind"), sentence=f.get("sentence"), single_span_ok=f.get("single_span_ok"),
                        cross_para_flag=f.get("cross_para_flag")))
    return out


# ------------------------------------------------------------
# Step A'' 応答のparse(Trial-07 parse_stepa7と同一。ref_ja(KP照合)は持たない)
# ------------------------------------------------------------
def parse_candidates(txt: str, paragraphs: list) -> dict:
    """LLM応答 → featuresに逐語解決・単一span検証を付けたdict。JSON/形が不正なら Part2StructureError(=技術retry対象。0件扱いにしない)。"""
    d = {"body": list(paragraphs)}
    try:
        m = re.search(r"\{.*\}", txt or "", re.S)
        if not m:
            raise ValueError("JSON object not found")
        j = json.loads(m.group(0))
        if not (isinstance(j.get("features"), list) and isinstance(j.get("no_feature_paras"), list)):
            raise ValueError("features/no_feature_paras missing")
        if not all(isinstance(f, dict) for f in j["features"]):
            raise ValueError("feature is not an object")
    except (ValueError, TypeError) as e:
        raise Part2StructureError(f"Step A''応答が不正: {e}") from e
    seen = set()
    feats = []
    for idx, f in enumerate(j["features"]):
        f = dict(f)
        f["resolve_ok"] = True
        f["order"] = idx
        f["cross_para_flag"] = None
        try:
            verb, pi, a, b, flag = resolve7(d, f.get("para"), f.get("sentence", ""))
            f["sentence_llm_raw"] = f.get("sentence", "")
            f["sentence_replaced_by_body"] = (verb != f["sentence_llm_raw"])
            f["sentence"] = verb
            f["cross_para_flag"] = flag
            f["single_span_ok"] = verify_single_span(d, f.get("para"), verb)
            f["prev"], f["next"] = local_context(d, pi, a, b)
            q = (f.get("misread_quote") or "").strip()
            f["misread_quote_in_sentence"] = bool(q) and _qn(q) in _qn(verb)
            if not f["single_span_ok"]:
                f["resolve_ok"] = False
                f["resolve_error"] = "single_span_check_failed"
        except AssertionError as e:
            f["resolve_ok"] = False
            f["resolve_error"] = str(e)[:120]
        key = (f.get("para"), f.get("sentence"))
        if key in seen:
            f["duplicate"] = True
        seen.add(key)
        feats.append(f)
    j["features"] = feats
    covered = {f.get("para") for f in feats} | set(j["no_feature_paras"])
    j["uncovered_paras"] = [f"P{i}" for i in range(1, len(paragraphs) + 1) if f"P{i}" not in covered]
    return j


def candidate_id(para: str, sentence: str) -> str:
    return "g" + hashlib.sha256(f"{para}|{_qn(sentence)}".encode("utf-8")).hexdigest()[:10]


def _cand_record(f, tier, rank):
    return {"candidate_id": candidate_id(f["para"], f["sentence"]), "rank": rank, "tier": tier, "feature_class": _cls(f),
            "para": f["para"], "sentence": f["sentence"], "front_kind": f.get("front_kind", ""),
            "misread_target": f.get("misread_target", ""), "misread_quote": f.get("misread_quote", ""), "misread_ja": f.get("misread_ja", ""),
            "omitted_words": f.get("omitted_words", ""), "teaching_value": f.get("teaching_value", ""),
            "teaching_value_ja": f.get("teaching_value_ja", ""), "construct_ja": f.get("construct_ja", ""),
            "points_ja": [str(x) for x in f.get("points_ja", [])], "context_ja": f.get("context_ja", ""),
            "prev": f.get("prev", ""), "next": f.get("next", ""), "cross_para_flag": f.get("cross_para_flag"),
            "single_span_ok": f.get("single_span_ok")}


def candidates_sha256(cands: list) -> str:
    return hashlib.sha256(json.dumps(cands, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def build_candidates_doc(parsed: dict, paragraphs: list, label: str, *, audit: dict | None = None, round_no: int = 1,
                         rejected_ids: tuple = ()) -> dict:
    """parse結果 → `grammar_candidates.json`(順位付きlist。TOP1/TOP2+残り)。rejected_ids(Human NG/再選定で外した候補)は除外する。"""
    ranked = [(f, t) for f, t in rank_eligible(parsed["features"]) if candidate_id(f["para"], f["sentence"]) not in set(rejected_ids)]
    cands = [_cand_record(f, t, i) for i, (f, t) in enumerate(ranked, 1)]
    doc = {"schema": SCHEMA_CANDIDATES, "level": LEVEL, "label": label, "text_sha256": text_sha256(paragraphs),
           "n_paragraphs": len(paragraphs), "prompt_id": "part2_stepA8", "prompt_template_sha256": STEPA_PROMPT_SHA256,
           "model": MODEL, "extract_signature": extract_signature(paragraphs, label), "round": round_no,
           "status": "HAS_CANDIDATES" if cands else "NO_CANDIDATE",
           "candidates": cands, "top_ids": [c["candidate_id"] for c in cands[:TOP_N]],
           "n_eligible": len(cands), "rejected_ids": list(rejected_ids),
           "tier_table": tier_table(parsed["features"]), "no_feature_paras": parsed.get("no_feature_paras", []),
           "uncovered_paras": parsed.get("uncovered_paras", []), "candidates_sha256": candidates_sha256(cands),
           "audit": audit or {}}
    return doc


def extract_signature(paragraphs: list, label: str, *, model: str | None = None) -> str:
    return hashlib.sha256(json.dumps({"text_sha256": text_sha256(paragraphs), "label": label, "prompt": STEPA_PROMPT_SHA256,
                                      "model": model or MODEL}, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


# ------------------------------------------------------------
# LLM呼出(call_fn: prompt → (text, response_model, usage, response_id))
# ------------------------------------------------------------
def _usage_dict(usage) -> dict:
    if usage is None:
        return {}
    d = {"input_tokens": getattr(usage, "input_tokens", None), "output_tokens": getattr(usage, "output_tokens", None)}
    det = getattr(usage, "input_tokens_details", None)
    if det is not None:
        d["cached_input_tokens"] = getattr(det, "cached_tokens", None)
    odet = getattr(usage, "output_tokens_details", None)
    if odet is not None:
        d["reasoning_tokens"] = getattr(odet, "reasoning_tokens", None)
    return d


def _default_call_fn_factory(client, model: str, max_output_tokens: int):
    def call_fn(prompt: str):
        r = client.responses.create(model=model, input=[{"role": "user", "content": prompt}], max_output_tokens=max_output_tokens)
        if getattr(r, "status", "completed") not in ("completed", None):   # incomplete(出力上限到達等)は構造失敗として扱う(retry→STOP)
            raise Part2StructureError(f"応答が完了していません(status={getattr(r, 'status', None)})")
        return (getattr(r, "output_text", None) or ""), r.model, _usage_dict(getattr(r, "usage", None)), r.id
    return call_fn


def _cost_jpy(model: str, usage: dict):
    try:
        import er009_n1_routing_governance_10_actual_model_cost as pricing
        return pricing.cost_jpy_for_call("openai", model, usage.get("input_tokens"), usage.get("cached_input_tokens"), usage.get("output_tokens"))
    except Exception:   # 単価表に無い等。費用は監査に残らないだけで生成は止めない(cost loggerが別途記録)
        return None


def _resolve_call_fn(call_fn, client, model, max_out):
    if call_fn is not None:
        return call_fn
    if client is None:
        import er003_v1_b1_scaffold_01_generate as b1s
        client = b1s.get_client()
    return _default_call_fn_factory(client, model, max_out)


def _run_llm(process: str, prompt: str, parse_fn, *, call_fn, client, max_out: int, budget_guard=None, est_jpy: float = 0.0, stage: str = ""):
    """共通: routing検証(API前) → 予算guard → 1 call → parse → 構造失敗なら技術retry1回 → なお失敗/model不一致でfail-closed(fallbackしない)。"""
    model = routing.require_model(process, MODEL)
    fn = _resolve_call_fn(call_fn, client, model, max_out)
    calls, last_err = [], None
    for attempt_no in (1, 2):   # 初回+技術retry1回(上限厳守)
        if budget_guard is not None:
            budget_guard(stage, est_jpy)
        t0 = time.time()
        try:
            text, response_model, usage, response_id = fn(prompt)
        except Part2StructureError as e:
            calls.append({"attempt": attempt_no, "structure_error": str(e)})
            last_err = str(e)
            continue
        rec = {"attempt": attempt_no, "response_model": response_model, "usage": usage, "response_id": response_id,
               "elapsed_sec": round(time.time() - t0, 2), "cost_jpy": _cost_jpy(response_model, usage or {})}
        calls.append(rec)
        if response_model != model:
            rec["model_contract_violation"] = True
            raise Part2Error(f"応答モデルが不一致です(期待: {model}, 実際: {response_model})。fallbackせずSTOPします(ER-006-MODEL-ROUTING-CONTRACT-01)。")
        try:
            parsed = parse_fn(text)
        except Part2StructureError as e:
            last_err = str(e)
            rec["structure_error"] = last_err
            continue
        costs = [c["cost_jpy"] for c in calls if c.get("cost_jpy") is not None]
        audit = {"management_id": MANAGEMENT_ID, "process": process, "model": model, "requested_model": model,
                 "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
                 "response_ids": [c.get("response_id") for c in calls if c.get("response_id")], "calls": calls,
                 "retried_for_parse": attempt_no == 2, "total_cost_jpy": round(sum(costs), 4) if costs else None,
                 "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
        return parsed, audit
    raise Part2Error(f"{process}が2回(初回+技術retry1回)とも構造検査に失敗しました: {last_err}")


# ------------------------------------------------------------
# 工程1: 候補抽出(Step A'' + 決定論のTier順位付け)
# ------------------------------------------------------------
def extract_candidates(paragraphs: list, label: str, *, call_fn=None, client=None, budget_guard=None, round_no: int = 1,
                       rejected_ids: tuple = ()) -> dict:
    """1 call(Step A'')。応答不正は技術retry1回→fail-closed。parse不能を『0件』として扱わない(Trialのparse_errorは0件化したがProductionは止める)。"""
    prompt = stepa_prompt(paragraphs, label)
    parsed, audit = _run_llm(PROCESS_EXTRACT, prompt, lambda t: parse_candidates(t, paragraphs), call_fn=call_fn, client=client,
                             max_out=MAXOUT_EXTRACT, budget_guard=budget_guard, est_jpy=0.5, stage="part2_extract")
    audit["prompt_template_sha256"] = STEPA_PROMPT_SHA256
    return build_candidates_doc(parsed, paragraphs, label, audit=audit, round_no=round_no, rejected_ids=rejected_ids)


def resolve_candidates(paragraphs: list, label: str, cached: dict | None, *, call_fn=None, client=None, budget_guard=None) -> dict:
    """resume: 本文sha・Prompt・modelが同じ保存済み候補はAPI 0で再利用。違えば再抽出。"""
    sig = extract_signature(paragraphs, label)
    if cached and cached.get("schema") == SCHEMA_CANDIDATES and cached.get("extract_signature") == sig \
            and cached.get("candidates_sha256") == candidates_sha256(cached.get("candidates", [])):
        out = json.loads(json.dumps(cached))
        out["reused_from_previous_run"] = True
        return out
    out = extract_candidates(paragraphs, label, call_fn=call_fn, client=client, budget_guard=budget_guard)
    out["reused_from_previous_run"] = False
    return out


def reselect_candidates(doc: dict, rejected_ids) -> dict:
    """Human「再選定」(API 0): 却下した候補を除いた同一抽出内の次順位で新しいTOP1/TOP2を作る。候補が尽きたらexhausted=True
    (呼出側が extract_candidates(..., rejected_ids=..., round_no+1) で再抽出するかを決める)。却下は累積。"""
    rej = list(dict.fromkeys(list(doc.get("rejected_ids", [])) + list(rejected_ids)))
    keep = [c for c in doc["candidates"] if c["candidate_id"] not in set(rej)]
    cands = [dict(c, rank=i) for i, c in enumerate(keep, 1)]
    new = dict(doc)
    new.update({"candidates": cands, "top_ids": [c["candidate_id"] for c in cands[:TOP_N]], "n_eligible": len(cands), "rejected_ids": rej,
                "round": doc.get("round", 1) + 1, "candidates_sha256": candidates_sha256(cands),
                "status": "HAS_CANDIDATES" if cands else "NO_CANDIDATE", "exhausted": not cands})
    return new


# ------------------------------------------------------------
# 工程2: 選定(Human Review接続点。kind="grammar")
# ------------------------------------------------------------
REVIEW_CHOICES = ("top1", "top2", "reselect", "omit")


def review_request(doc: dict) -> dict:
    """er119共通核(kind="grammar")へ渡す提示内容。TOP1/TOP2(順位付き)と残り件数。AI推奨=TOP1。"""
    top = doc["candidates"][:TOP_N]
    return {"kind": "grammar", "candidates_sha256": doc["candidates_sha256"], "round": doc.get("round", 1),
            "top": [{"candidate_id": c["candidate_id"], "rank": c["rank"], "tier": c["tier"], "feature_class": c["feature_class"],
                     "para": c["para"], "sentence": c["sentence"], "teaching_value_ja": c["teaching_value_ja"],
                     "construct_ja": c["construct_ja"], "misread_ja": c["misread_ja"]} for c in top],
            "n_more": max(0, len(doc["candidates"]) - len(top)), "ai_recommended": top[0]["candidate_id"] if top else None,
            "choices": list(REVIEW_CHOICES) if top else ["omit"], "auto_default": "top1" if top else "omit"}


def select_from_candidates(doc: dict, review: dict | None, mode: str) -> dict:
    """戻り値: {"status": SELECTED|ZERO|PENDING_REVIEW|RESELECT_REQUESTED, "candidate": dict|None, "source": str}。
    - 候補0件 → ZERO(no_candidate。Trial-07の0件許容。Humanに判断対象がないので待機しない)
    - review有り(Human): choice=top1/top2/omit/reselect。candidates_sha256が違えばPart2ReviewError(stale)
    - review無し: mode="auto"(呼出側/er119が明示宣言した場合のみ)→ TOP1自動採用 / mode="wait" → PENDING_REVIEW(有料のStep Bへ進まない)
    未レビューを最終承認扱いにしない: sourceに auto_top1 / human_top1 等を残す。"""
    if mode not in ("auto", "wait"):
        raise Part2ReviewError(f"modeは auto|wait のみ: {mode!r}")
    cands = doc.get("candidates", [])
    if not cands:
        return {"status": "ZERO", "candidate": None, "source": "no_candidate"}
    if review is not None:
        ch = review.get("choice")
        if ch not in REVIEW_CHOICES:
            raise Part2ReviewError(f"choiceは {REVIEW_CHOICES} のいずれか: {ch!r}")
        if review.get("candidates_sha256") != doc["candidates_sha256"]:
            raise Part2ReviewError("reviewが古い候補listに対するものです(candidates_sha256不一致)。再レビューが必要です")
        if ch == "omit":
            return {"status": "ZERO", "candidate": None, "source": "human_omit"}
        if ch == "reselect":
            return {"status": "RESELECT_REQUESTED", "candidate": None, "source": "human_reselect"}
        idx = 0 if ch == "top1" else 1
        if idx >= len(cands):
            raise Part2ReviewError("TOP2が存在しません(候補が1件のみ)")
        return {"status": "SELECTED", "candidate": cands[idx], "source": f"human_{ch}"}
    if mode == "auto":
        return {"status": "SELECTED", "candidate": cands[0], "source": "auto_top1"}
    return {"status": "PENDING_REVIEW", "candidate": None, "source": "pending"}


# ------------------------------------------------------------
# 工程3: 日本語訳(T1)+ Step B 解説
# ------------------------------------------------------------
def stepb_item(cand: dict, ref_ja: str | None) -> dict:
    s = {"para": cand["para"], "sentence": cand["sentence"], "construct_ja": cand["construct_ja"],
         "points_ja": [str(x) for x in cand["points_ja"]][:3], "context_ja": cand["context_ja"],
         "prev": cand.get("prev", ""), "next": cand.get("next", "")}
    if ref_ja:
        s["ref_ja"] = ref_ja
    return s


def stepb_items_text(selected: list) -> str:
    out = []
    for i, s in enumerate(selected, 1):
        pts = "\n".join(f"     - {p}" for p in s["points_ja"])
        blk = f"[{i}] 英文: {s['sentence']}\n   構文: {s['construct_ja']}\n   押さえる点:\n{pts}\n   本文での位置づけ: {s['context_ja']}"
        if s.get("prev"):
            blk += f"\n   前の文(本文): {s['prev']}"
        if s.get("next"):
            blk += f"\n   後の文(本文): {s['next']}"
        if s.get("ref_ja"):
            blk += f"\n   参考訳(別工程で確定済み): {s['ref_ja']}"
        out.append(blk)
    return "\n".join(out)


def stepb_prompt(selected: list) -> str:
    return STEPB_PROMPT.format(items=stepb_items_text(selected))


_CJK_RE = re.compile(r"[　-〿぀-ヿ㐀-䶿一-鿿豈-﫿＀-￯]")
_ITEM_RE = re.compile(r"(?m)^=====ITEM (\d+)=====\s*$")
_HEAD_RE = re.compile(r"(?m)^【(.+?)】\s*$")


def parse_stepb(txt: str, n: int = 1) -> dict:
    items = _ITEM_RE.split(txt or "")
    res = {int(items[i]): items[i + 1].strip() for i in range(1, len(items), 2)}
    if sorted(res) != list(range(1, n + 1)):
        raise Part2StructureError(f"Step B応答のITEM区切りが不正: {sorted(res)}")
    return res


def split_sections(md: str) -> dict:
    """【見出し】単位に分割。構造検査: 必須見出し(日本語訳/仕組み/意味)が順序通り1回ずつ、各本文は日本語を含み、ページ非表示語を含まない。違反はPart2StructureError。"""
    parts = _HEAD_RE.split(md.strip())
    if parts[0].strip():
        raise Part2StructureError("最初の見出しの前に本文があります")
    heads = parts[1::2]
    bodies = [b.strip() for b in parts[2::2]]
    if len(set(heads)) != len(heads):
        raise Part2StructureError(f"見出しが重複: {heads}")
    for h in heads:
        if h not in EXPLANATION_HEADINGS:
            raise Part2StructureError(f"想定外の見出し: {h}")
    order = [h for h in EXPLANATION_HEADINGS if h in heads]
    if heads != order:
        raise Part2StructureError(f"見出しの順序が不正: {heads}")
    for h in EXPLANATION_REQUIRED:
        if h not in heads:
            raise Part2StructureError(f"必須見出しなし: {h}")
    sec = dict(zip(heads, bodies))
    for h, b in sec.items():
        if not b or not _CJK_RE.search(b):
            raise Part2StructureError(f"見出し本文が空または日本語を含まない: {h}")
        if PAGE_FORBIDDEN_RE.search(b):
            raise Part2StructureError(f"ページ非表示語を含む: {h}")
    return sec


def _parse_stepb_checked(txt: str) -> dict:
    md = parse_stepb(txt, 1)[1]
    return {"markdown": md, "sections": split_sections(md)}


def _norm_sentence(s: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", _qn(s))).strip().casefold()


def translate_sentence(sentence: str, *, call_fn=None, client=None, ref_ja_pool: dict | None = None) -> dict:
    """引用英文のみを入力とするT1訳(er003_kp_source_sentence_ja_01.generate_translations を再利用。Part 1と同一工程・同一Prompt)。
    Part 1で同じ英文を訳済み(ref_ja_pool)ならAPI 0で再利用(Part 1/Part 2で同一英文に食い違う訳を出さない)。"""
    if ref_ja_pool:
        hit = ref_ja_pool.get(_norm_sentence(sentence))
        if hit:
            return {"ja": hit, "source": "part1_pool", "audit": None}
    import er003_kp_source_sentence_ja_01 as ja
    res = ja.generate_translations([sentence], call_fn=call_fn, client=client)
    return {"ja": res["items"][0]["source_sentence_ja"], "source": "T1", "audit": res["audit"]}


def explain_signature(cand: dict, ref_ja: str | None) -> str:
    sel = stepb_item(cand, ref_ja)
    return hashlib.sha256(json.dumps({"item": sel, "candidate_id": cand["candidate_id"], "stepb": STEPB_PROMPT_SHA256, "model": MODEL},
                                     ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def generate_explanation(cand: dict, ref_ja: str | None, *, call_fn=None, client=None, budget_guard=None) -> dict:
    prompt = stepb_prompt([stepb_item(cand, ref_ja)])
    parsed, audit = _run_llm(PROCESS_EXPLAIN, prompt, _parse_stepb_checked, call_fn=call_fn, client=client, max_out=MAXOUT_EXPLAIN,
                             budget_guard=budget_guard, est_jpy=0.3, stage="part2_explain")
    audit["prompt_template_sha256"] = STEPB_PROMPT_SHA256
    return {"markdown": parsed["markdown"], "sections": parsed["sections"], "audit": audit}


# ------------------------------------------------------------
# 結果の組立(決定論)と検証
# ------------------------------------------------------------
def zero_result(doc: dict, source: str) -> dict:
    return {"schema": SCHEMA_RESULT, "level": LEVEL, "status": "ZERO", "zero_reason": source, "selection": {"source": source},
            "text_sha256": doc["text_sha256"], "extract_signature": doc["extract_signature"], "candidates_sha256": doc["candidates_sha256"],
            "round": doc.get("round", 1), "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z")}


def build_result(doc: dict, sel: dict, translation: dict, expl: dict) -> dict:
    c = sel["candidate"]
    return {"schema": SCHEMA_RESULT, "level": LEVEL, "status": "SELECTED", "zero_reason": None,
            "selection": {"source": sel["source"], "candidate_id": c["candidate_id"], "rank": c["rank"], "tier": c["tier"],
                          "feature_class": c["feature_class"], "para": c["para"], "sentence": c["sentence"],
                          "construct_ja": c["construct_ja"], "teaching_value_ja": c["teaching_value_ja"]},
            "text_sha256": doc["text_sha256"], "extract_signature": doc["extract_signature"], "candidates_sha256": doc["candidates_sha256"],
            "round": doc.get("round", 1), "translation_ja": translation["ja"], "translation_source": translation["source"],
            "explain_signature": explain_signature(c, translation["ja"]), "explanation_md": expl["markdown"], "sections": expl["sections"],
            "audit": {"extract": doc.get("audit"), "translate": translation["audit"], "explain": expl["audit"]},
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z")}


def run_part2(paragraphs: list, label: str, *, review: dict | None = None, mode: str = "wait", cached_candidates: dict | None = None,
              cached_result: dict | None = None, ref_ja_pool: dict | None = None, extract_call_fn=None, explain_call_fn=None,
              translate_call_fn=None, client=None, budget_guard=None) -> dict:
    """純関数的なorchestrator(ファイルI/Oは呼出側。write_artifacts/load_artifactsを使う)。
    戻り値: {"status": SELECTED|ZERO|PENDING_REVIEW|RESELECT_REQUESTED, "candidates": doc, "result": dict|None, "review_request": dict|None}
    PENDING_REVIEWでは有料のStep B・訳を呼ばない。ZERO/SELECTED以外ではresultはNone(下流はfail-closed)。"""
    paragraphs = _check_paragraphs(paragraphs)
    doc = resolve_candidates(paragraphs, label, cached_candidates, call_fn=extract_call_fn, client=client, budget_guard=budget_guard)
    sel = select_from_candidates(doc, review, mode)
    if sel["status"] in ("PENDING_REVIEW", "RESELECT_REQUESTED"):
        return {"status": sel["status"], "candidates": doc, "result": None, "review_request": review_request(doc)}
    if sel["status"] == "ZERO":
        return {"status": "ZERO", "candidates": doc, "result": zero_result(doc, sel["source"]), "review_request": None}
    c = sel["candidate"]
    if cached_result and cached_result.get("schema") == SCHEMA_RESULT and cached_result.get("status") == "SELECTED" \
            and cached_result.get("selection", {}).get("candidate_id") == c["candidate_id"] \
            and cached_result.get("candidates_sha256") == doc["candidates_sha256"] \
            and cached_result.get("explain_signature") == explain_signature(c, cached_result.get("translation_ja")) and cached_result.get("explanation_md"):
        res = json.loads(json.dumps(cached_result))
        res["selection"]["source"] = sel["source"]
        res["reused_from_previous_run"] = True
        return {"status": "SELECTED", "candidates": doc, "result": res, "review_request": None}
    if budget_guard is not None:
        budget_guard("part2_translate", 0.1)
    tr = translate_sentence(c["sentence"], call_fn=translate_call_fn, client=client, ref_ja_pool=ref_ja_pool)
    expl = generate_explanation(c, tr["ja"], call_fn=explain_call_fn, client=client, budget_guard=budget_guard)
    res = build_result(doc, sel, tr, expl)
    res["reused_from_previous_run"] = False
    return {"status": "SELECTED", "candidates": doc, "result": res, "review_request": None}


def require_fresh_part2(result: dict | None, paragraphs: list, label: str, *, next_command: str, where: str = "") -> None:
    """使う側(TTS/assembly/pages/player)のfail-closed確認。無い/古い/不整合ならPart2Stale(次コマンド付き)。
    ZERO(0件)は正当な最終状態として通す。SELECTEDは: 本文sha・抽出signature一致、選定文が単一段落の逐語span、解説signature一致、解説非空。"""
    w = f"[{where}] " if where else ""
    if not result or result.get("schema") != SCHEMA_RESULT:
        raise Part2Stale(f"{w}Part 2 artifactがありません。次の一手: {next_command}")
    paragraphs = _check_paragraphs(paragraphs)
    if result.get("text_sha256") != text_sha256(paragraphs) or result.get("extract_signature") != extract_signature(paragraphs, label):
        raise Part2Stale(f"{w}Part 2が現在の本文・Prompt・modelと一致しません(古い)。次の一手: {next_command}")
    if result.get("status") == "ZERO":
        return
    if result.get("status") != "SELECTED":
        raise Part2Stale(f"{w}Part 2のstatusが不正: {result.get('status')}。次の一手: {next_command}")
    sel = result["selection"]
    d = {"body": paragraphs}
    if not verify_single_span(d, sel.get("para"), sel.get("sentence")):
        raise Part2Stale(f"{w}Part 2の選定文が本文の単一段落の逐語spanではありません。次の一手: {next_command}")
    if not result.get("explanation_md") or not result.get("translation_ja") or not result.get("sections"):
        raise Part2Stale(f"{w}Part 2の解説または訳が欠落しています。次の一手: {next_command}")
    ref = result["translation_ja"]
    cand = {"candidate_id": sel["candidate_id"], "para": sel["para"], "sentence": sel["sentence"]}
    # 解説signatureは材料欄込みで保存されている。ここでは保存値の存在と選定文の同一性を確認する(材料の再計算は候補docを持つ呼出側のrun_part2で行う)
    if not result.get("explain_signature") or result["selection"]["candidate_id"] != candidate_id(cand["para"], cand["sentence"]):
        raise Part2Stale(f"{w}Part 2の解説signature/候補IDが不整合です。次の一手: {next_command}")
    if PAGE_FORBIDDEN_RE.search(result["explanation_md"]) or not ref:
        raise Part2Stale(f"{w}Part 2の解説にページ非表示語が含まれます。次の一手: {next_command}")


# ------------------------------------------------------------
# 保存・描画
# ------------------------------------------------------------
def write_artifacts(dir_path: str, doc: dict | None, result: dict | None) -> dict:
    """study_text/ へ grammar_candidates.json / part2_result.json / .md を保存(UTF-8, LF)。"""
    os.makedirs(dir_path, exist_ok=True)
    out = {}
    if doc is not None:
        out["candidates"] = f"{dir_path}/{CANDIDATES_FILENAME}"
        with open(out["candidates"], "w", encoding="utf-8", newline="\n") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)
    if result is not None:
        out["result"] = f"{dir_path}/{RESULT_FILENAME}"
        with open(out["result"], "w", encoding="utf-8", newline="\n") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        out["md"] = f"{dir_path}/{PART2_FILE_STEM}.md"
        with open(out["md"], "w", encoding="utf-8", newline="\n") as f:
            f.write(render_markdown(result))
    return out


def load_json(path: str) -> dict | None:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def render_markdown(result: dict) -> str:
    """Part 1と同じく節見出しにPart番号を出さない(Part 3/4未採用の番号参照=Dangling防止)。0件はTrialと同じ固定文面。"""
    L = ["# Grammar & Sentence Structure", ""]
    if result.get("status") != "SELECTED":
        return "\n".join(L + [ZERO_P2, ""])
    s = result["selection"]
    L += ["## 対象となる本文英文", "", f"> {s['sentence']}", "", f"**日本語訳**\n{result['translation_ja']}", ""]
    sec = result["sections"]
    for h in EXPLANATION_HEADINGS[1:]:
        if h in sec:
            L += [f"**{h}**", sec[h], ""]
    return "\n".join(L)


def render_html_block(result: dict, *, include_css: bool = True) -> str:
    """ページ用のstudy block(Part 1の `<section class='study'>` と同じ規約。<table>/<h2>不使用)。Part 1ブロックの直後に連結して使う
    (その場合 include_css=False)。0件は固定文面を載せる。LLM出力はHTMLエスケープ後に**→<b>。"""
    import er003_kp_general_explanation_01 as p1
    parts = ["<section class='study'><h3>Grammar &amp; Sentence Structure</h3>"]
    if result.get("status") != "SELECTED":
        parts.append(f"<div class='study-item'><p>{html.escape(ZERO_P2, quote=False)}</p></div>")
    else:
        s, sec = result["selection"], result["sections"]
        dl = [f"<dt>対象となる本文英文</dt><dd>{html.escape(s['sentence'], quote=False)}</dd>",
              f"<dt>日本語訳</dt><dd>{html.escape(result['translation_ja'], quote=False)}</dd>"]
        for h in EXPLANATION_HEADINGS[1:]:
            if h in sec:
                dl.append(f"<dt>{html.escape(h, quote=False)}</dt><dd>{p1._paragraphs_html(sec[h])}</dd>")
        parts.append(f"<div class='study-item'><dl>{''.join(dl)}</dl></div>")
    parts.append("</section>")
    return (p1.STUDY_CSS if include_css else "") + "".join(parts)
