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
# 委任_02(2026-10-25): Opus条件Aレビュー(docs/research/PART2-GRAMMAR-PRODUCTION-WIRING-01/OPUS_REVIEW_01.md)のM-1〜M-7・R-1/3/4/7をmodule内で反映(DESIGN_02.md)。
#   M-1でT1訳callを廃止(訳の出所=Trial-07どおりStep B自身。ref_jaはPart 1訳pool一致時のみ)。runner/er119/ページは引き続き無改変。
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
LEVEL = "Advanced"                       # v1読取専用の定数(GRAMMAR-PREGEN-ALL-LEVELS-01 委任_02以降、新コードは参照しない。levelは必須引数=LEVELS)
LEVELS = {"b1b": "Advanced", "a2": "Standard"}   # GRAMMAR-PREGEN-ALL-LEVELS-01(ユーザー正式決定 2026-10-27): 全6経路(X/Y/Z x Std/Adv)。levelキー->候補docの`level`表示名
SCHEMA_RESULT_V2 = "part2_grammar_v2"
SCHEMA_REVIEW_V2 = "grammar_human_review_v2"
SCHEMA_EXPLANATIONS = "grammar_explanations_v1"
EXPLANATIONS_FILENAME = "grammar_explanations.json"
PREGEN_MAX = 2                           # 提示=事前生成の対象数(文法選定仕様変更 2026-10-27: Trial-08順位のTop1/Top2のみ。旧8)。3位以降は生成せずskipped_over_capに記録
GRAMMAR_MAX = 1                          # ユーザー選択の上限(原則1件・0件可・2件同時選択禁止。旧2=撤去。2026-10-27ユーザー正式決定)
SCHEMA_CANDIDATES = "grammar_candidates_v1"
SCHEMA_RESULT = "part2_grammar_v1"
CANDIDATES_FILENAME = "grammar_candidates.json"
RESULT_FILENAME = "part2_result.json"
PART2_FILE_STEM = "part2_grammar_sentence_structure"
MAXOUT_EXTRACT = 13000                   # Trial-07/08のMAXOUT_A
MAXOUT_EXPLAIN = 6000                    # Trial-07のMAXOUT_B
TOP_N = 2                                # 提示上限(HR/フォーム/事前生成): TOP1/TOP2(ユーザー正式決定)。選択上限ではない(選択=GRAMMAR_MAX=1)

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
# 文法0件はコーナー全体を非表示にする(ユーザー正式決定2026-10-29 §2C。固定文面・見出し・空枠を出さない)。旧固定文面は『既存0件runの旧mdの退避判定(M-6)』専用の
# 読取定数としてのみ残す(描画・出力には使わない)。
_LEGACY_ZERO_GRAMMAR_BODY = "今回の本文には、このPartで特に取り上げる難所となる構文はありませんでした。"
NUANCE_HEADING = "ニュアンス解説"                  # 独立コーナー名(ユーザー原文§2A-5。『Deeper Understanding』は不使用=Fable判断R-12)
NUANCE_RESULT_FILENAME = "nuance_result.json"       # finalize(委任_02C/er134)が書く表示用の確定結果。無い=ニュアンス解説なし(LEGACY/未実施を含む)
NUANCE_ADOPTED = "ADOPTED"                          # 表示するのはこのstatusのときだけ(REJECTED/NONE/LEGACY/FAILED_TECHNICAL等は空文字)
LEGACY_ZERO_GRAMMAR_MD_SUFFIX = ".legacy_zero_p2.md"        # 旧0件md(固定文面入り)の退避先(削除しない)
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
    out, seen, spans = [], set(), []
    for tier, grp in (("T1", t1), ("T2", t2)):
        for f in grp:
            k = (f.get("para"), _qn(f.get("sentence", "")))
            if k in seen:
                continue
            sp = f.get("span")
            if sp and any(p == f.get("para") and sp[0] < q[1] and q[0] < sp[1] for p, q in spans):   # R-4: 同一段落内で範囲が重なる/包含する候補も除外
                continue
            seen.add(k)
            if sp:
                spans.append((f.get("para"), sp))
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
            f["span"] = [a, b]                      # 委任_02: 同一段落内の文字範囲(NG範囲照合・TOP2重複除外に使う。M-5/R-4)
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
            "single_span_ok": f.get("single_span_ok"), "span": f.get("span")}


def candidates_sha256(cands: list) -> str:
    return hashlib.sha256(json.dumps(cands, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


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
# 委任_02 Opus条件Aレビュー反映(M-1〜M-7, R-1/R-3/R-4/R-7)で追加・変更した部分
#   M-1 訳の出所=Trial-07どおり(Step B自身の【日本語訳】を表示。ref_jaはPart 1のT1訳pool一致時のみStep Bへ渡す。T1 callなし)
#   M-2 require_fresh_part2をHuman確定(grammar_review)+候補docに結びつける
#   M-3 mode='auto'は呼出側の文字列では不可(er119の明示宣言dictのみ) / M-4 stage用input_sha・PENDING専用例外・再抽出なしfinalize
#   M-5 NG照合3方式・枯渇時RESELECT_EXHAUSTED・human_rejected_all・reselect上限・NGとNOT_SELECTEDの区別
#   M-6 NO_CANDIDATE_UNREVIEWED・reason必須・history・auto_top1をレビュー済みに数えない集計 / M-7 失敗記録(part2_failed.json)
# ------------------------------------------------------------
MAX_RESELECT = 2        # M-5(d): reselect_count<=2(次順位への再選定+再抽出の合計)
MAX_REEXTRACT = 1       # M-5(d): うち再抽出(Step A'' 再call)は最大1回
ALLOWED_REVIEW_STATUSES = ("REVIEWED", "UNREVIEWED_AUTO_ADOPTED", "NO_CANDIDATE_UNREVIEWED")   # 下流が進めてよいstatus(M-2/M-6)
AUTO_DECLARATION_SOURCES = ("cli_runner_arg", "declare_absent_cli")                         # KP HR DESIGN_01 b-2: er119のmode_declaration.source
WAIT_STATUSES = ("PENDING_REVIEW", "RESELECT_REQUESTED", "RESELECT_EXHAUSTED", "REEXTRACT_REQUESTED")
SCHEMA_REVIEW = "grammar_human_review_v1"
FAILED_FILENAME = "part2_failed.json"
HUMAN_REASON_REQUIRED = ("top2", "reselect", "omit", "reextract")   # M-6: 理由必須の選択


class Part2ReselectLimit(Part2Error):
    """M-5(d): 再選定(再抽出含む)の上限超過。STOPして報告する。"""


class Part2PendingReview(Exception):
    """M-4: Human判断待ち(失敗ではない)。ensure_stageは出力ファイルを書く前にこの例外で抜ける。Part2Errorを継承しない(失敗扱いにしない)。"""

    def __init__(self, status, review_request, candidates_doc):
        super().__init__(f"Part 2はHuman判断待ちです: {status}")
        self.status, self.review_request, self.candidates_doc = status, review_request, candidates_doc


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def _norm_sentence(s: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", _qn(s))).strip().casefold()


# ---- M-3: mode(auto)は呼出側の文字列では指定できない -------------------------------------
def normalize_mode(mode):
    """'wait'(既定。None含む) か、er119の read_mode_declaration() が返す明示宣言dict({'mode':'auto',declared_by,declared_at,reason,source})のみ。
    文字列 'auto' や宣言欠落dictは拒否(runner引数・hooks・環境変数・設定dictからautoにできない)。戻り値: ('wait'|'auto', declaration|None)"""
    if mode is None or mode == "wait":
        return "wait", None
    if isinstance(mode, dict) and mode.get("mode") == "auto":
        for k in ("declared_by", "declared_at", "reason", "source"):
            if not (isinstance(mode.get(k), str) and mode[k].strip()):
                raise Part2ReviewError(f"auto宣言に {k} がありません(er119のmode_declarationのみ有効)")
        if mode["source"] not in AUTO_DECLARATION_SOURCES:
            raise Part2ReviewError(f"auto宣言のsourceが不正: {mode['source']!r}")
        return "auto", dict(mode)
    raise Part2ReviewError("modeは 'wait' か er119 の明示宣言dict のみ。文字列 'auto' は受け付けません(M-3)")


# ---- M-5(b): NG(却下)照合 3方式 ----------------------------------------------------------
def _span_of(x):
    s = x.get("span")
    if isinstance(s, (list, tuple)) and len(s) == 2:
        try:
            return int(s[0]), int(s[1])
        except (TypeError, ValueError):
            return None
    return None


def ng_entry_from_candidate(c: dict, *, reason: str, by: str = "", source: str = "human_reselect") -> dict:
    return {"candidate_id": c["candidate_id"], "para": c["para"], "sentence": c["sentence"], "span": c.get("span"),
            "feature_class": c.get("feature_class"), "tier": c.get("tier"), "reason": reason, "by": by, "source": source, "at": _now()}


def ng_match_methods(cand: dict, entry: dict) -> list:
    """候補がNG entryに該当する方式のlist: candidate_id / sentence(正規化。段落番号は見ない) / range(同一段落内の文字範囲の重なり・包含)。"""
    ms = []
    if entry.get("candidate_id") and cand["candidate_id"] == entry["candidate_id"]:
        ms.append("candidate_id")
    if entry.get("sentence") and _norm_sentence(cand["sentence"]) == _norm_sentence(entry["sentence"]):
        ms.append("sentence")
    a, b = _span_of(cand), _span_of(entry)
    if a and b and cand.get("para") == entry.get("para") and a[0] < b[1] and b[0] < a[1]:
        ms.append("range")
    return ms


def filter_ng(cands: list, ng_entries) -> tuple:
    """(kept, dropped)。dropped=[{candidate_id, methods, ng_candidate_id}]"""
    kept, dropped = [], []
    for c in cands:
        hit = None
        for e in ng_entries or ():
            ms = ng_match_methods(c, e)
            if ms:
                hit = (e, ms)
                break
        if hit:
            dropped.append({"candidate_id": c["candidate_id"], "methods": hit[1], "ng_candidate_id": hit[0].get("candidate_id")})
        else:
            kept.append(c)
    return kept, dropped


def _merge_ng(*lists) -> list:
    out, seen = [], set()
    for lst in lists:
        for e in lst or ():
            k = (e.get("candidate_id"), _norm_sentence(e.get("sentence", "")), tuple(e.get("span") or ()), e.get("para"))
            if k in seen:
                continue
            seen.add(k)
            out.append(e)
    return out


def _rebuild(doc: dict, cands: list, *, ng: list, filtered: list, **upd) -> dict:
    cands = [dict(c, rank=i) for i, c in enumerate(cands, 1)]
    new = dict(doc)
    new.update(upd)
    new.update({"candidates": cands, "top_ids": [c["candidate_id"] for c in cands[:TOP_N]], "n_eligible": len(cands),
                "ng": ng, "filtered_by_ng": filtered, "rejected_ids": list(dict.fromkeys([e["candidate_id"] for e in ng if e.get("candidate_id")])),
                "candidates_sha256": candidates_sha256(cands), "status": "HAS_CANDIDATES" if cands else "NO_CANDIDATE",
                "exhausted": (not cands) and bool(filtered)})
    return new


def build_candidates_doc(parsed: dict, paragraphs: list, label: str, *, level: str, audit: dict | None = None, round_no: int = 1,
                         rejected_ids: tuple = (), ng=(), reselect_count: int = 0, reextract_count: int = 0) -> dict:
    """parse結果 → `grammar_candidates.json`(順位付きlist。TOP1/TOP2+残り)。rejected_ids(id一致のみ)とng(3方式照合のNG entry)に該当する候補は除外し、
    除外理由を filtered_by_ng に残す。全候補がNGで尽きたら exhausted=True(『適格なし』ではない=M-5(c))。"""
    ranked = rank_eligible(parsed["features"])
    cands = [_cand_record(f, t, i) for i, (f, t) in enumerate(ranked, 1)]
    rej = set(rejected_ids)
    dropped = [{"candidate_id": c["candidate_id"], "methods": ["candidate_id"], "ng_candidate_id": c["candidate_id"]} for c in cands if c["candidate_id"] in rej]
    cands = [c for c in cands if c["candidate_id"] not in rej]
    ng = _merge_ng(ng)
    cands, d2 = filter_ng(cands, ng)
    filtered = dropped + d2
    doc = {"schema": SCHEMA_CANDIDATES, "level": level_name(level), "label": label, "text_sha256": text_sha256(paragraphs),
           "n_paragraphs": len(paragraphs), "prompt_id": "part2_stepA8", "prompt_template_sha256": STEPA_PROMPT_SHA256,
           "model": MODEL, "extract_signature": extract_signature(paragraphs, label), "round": round_no,
           "tier_table": tier_table(parsed["features"]), "no_feature_paras": parsed.get("no_feature_paras", []),
           "uncovered_paras": parsed.get("uncovered_paras", []), "audit": audit or {},
           "reselect_count": reselect_count, "reextract_count": reextract_count, "reselect_log": []}
    return _rebuild(doc, cands, ng=ng, filtered=filtered)


def apply_ng(doc: dict, ng_entries) -> dict:
    """保存済み候補docへ(共有registry等の)NGを再適用する。変化が無ければ同一docを返す。"""
    merged = _merge_ng(doc.get("ng", []), ng_entries)
    kept, dropped = filter_ng(doc["candidates"], merged)
    if not dropped and len(merged) == len(doc.get("ng", [])):
        return doc
    return _rebuild(doc, kept, ng=merged, filtered=list(doc.get("filtered_by_ng", [])) + dropped)


# ------------------------------------------------------------
# 工程1: 候補抽出(Step A'' + 決定論のTier順位付け)
# ------------------------------------------------------------
def extract_candidates(paragraphs: list, label: str, *, level: str, call_fn=None, client=None, budget_guard=None, round_no: int = 1,
                       rejected_ids: tuple = (), ng=(), reselect_count: int = 0, reextract_count: int = 0) -> dict:
    """1 call(Step A'')。応答不正は技術retry1回→fail-closed。parse不能を『0件』として扱わない(Trialのparse_errorは0件化したがProductionは止める)。"""
    level_name(level)   # 必須引数の検証(課金前に拒否)
    prompt = stepa_prompt(paragraphs, label)
    parsed, audit = _run_llm(PROCESS_EXTRACT, prompt, lambda t: parse_candidates(t, paragraphs), call_fn=call_fn, client=client,
                             max_out=MAXOUT_EXTRACT, budget_guard=budget_guard, est_jpy=0.5, stage="part2_extract")
    audit["prompt_template_sha256"] = STEPA_PROMPT_SHA256
    return build_candidates_doc(parsed, paragraphs, label, level=level, audit=audit, round_no=round_no, rejected_ids=rejected_ids, ng=ng,
                                reselect_count=reselect_count, reextract_count=reextract_count)


def resolve_candidates(paragraphs: list, label: str, cached: dict | None, *, level: str, call_fn=None, client=None, budget_guard=None, ng=(),
                       allow_extract: bool = True, frozen: bool = False) -> dict:
    """resume: 本文sha・Prompt・modelが同じ保存済み候補はAPI 0で再利用(共有registryのNGは再適用)。違えば再抽出。
    allow_extract=False(再finalize用、M-4)では再抽出せず、無い/古いなら Part2Stale。
    frozen=True(KP-CONFIRMED-CONTENT-PROTECTION-01 M6): ユーザー確定済みの文法がある場合。Prompt・model・routingの変更でextract_signatureが変わっても
    再抽出しない(本文shaが同じ・候補doc自己整合なら保存済み候補をそのまま使う)。本文が変わった場合の再バインドはer119_grammar_review側(API 0)。"""
    sig = extract_signature(paragraphs, label)
    check_doc_level(cached, level)   # 候補docのlevel欄と呼出しのlevelが違えばfail-closed(pathからの推定はしない)
    if frozen and cached and cached.get("schema") == SCHEMA_CANDIDATES and cached.get("text_sha256") == text_sha256(paragraphs) \
            and cached.get("candidates_sha256") == candidates_sha256(cached.get("candidates", [])):
        out = apply_ng(json.loads(json.dumps(cached)), ng)
        out["reused_from_previous_run"] = True
        return out
    if cached and cached.get("schema") == SCHEMA_CANDIDATES and cached.get("extract_signature") == sig \
            and cached.get("candidates_sha256") == candidates_sha256(cached.get("candidates", [])):
        out = apply_ng(json.loads(json.dumps(cached)), ng)
        out["reused_from_previous_run"] = True
        return out
    if not allow_extract:
        raise Part2Stale("保存済みの候補がない、または現在の本文・label・Prompt・modelと一致しません。再抽出はreselect/抽出stageだけで行います(再finalizeでは再抽出しない)")
    out = extract_candidates(paragraphs, label, level=level, call_fn=call_fn, client=client, budget_guard=budget_guard, ng=ng)
    out["reused_from_previous_run"] = False
    return out


def rejection_detail(doc: dict, c: dict) -> dict:
    """却下候補の記録(M-6): 文・分類・tier・tier_tableの行を一緒に残す。"""
    row = next((t for t in doc.get("tier_table", []) if t.get("para") == c["para"] and _qn(t.get("sentence") or "") == _qn(c["sentence"])), None)
    return {"candidate_id": c["candidate_id"], "para": c["para"], "sentence": c["sentence"], "feature_class": c["feature_class"],
            "tier": c["tier"], "rank": c.get("rank"), "teaching_value_ja": c.get("teaching_value_ja"), "tier_table_row": row}


def reselect_candidates(doc: dict, rejected_ids=None, *, reason: str, by: str = "") -> dict:
    """Human「再選定」(API 0): 却下した候補(既定=表示中のTOP1/TOP2)をNGとして記録し、除いた同一抽出内の次順位で新しいTOP1/TOP2を作る。
    reasonは必須(M-6)。reselect_count>MAX_RESELECT でPart2ReselectLimit(STOP)。尽きたら exhausted=True(自動ZEROにしない。M-5(c))。"""
    if not (isinstance(reason, str) and reason.strip()):
        raise Part2ReviewError("再選定の理由(reason)は必須です(M-6)")
    if doc.get("reselect_count", 0) + 1 > MAX_RESELECT:
        raise Part2ReselectLimit(f"再選定の上限({MAX_RESELECT}回)を超えます。STOPして報告します")
    ids = list(rejected_ids) if rejected_ids is not None else list(doc.get("top_ids", []))
    by_id = {c["candidate_id"]: c for c in doc["candidates"]}
    bad = [i for i in ids if i not in by_id]
    if bad or not ids:
        raise Part2ReviewError(f"再選定の対象が候補にありません: {bad or 'なし'}")
    new_ng = [ng_entry_from_candidate(by_id[i], reason=reason, by=by) for i in ids]
    merged = _merge_ng(doc.get("ng", []), new_ng)
    kept, dropped = filter_ng(doc["candidates"], merged)
    log = list(doc.get("reselect_log", [])) + [{"at": _now(), "event": "reselect", "by": by, "reason": reason, "kind": "next_rank",
                                                 "rejected": [rejection_detail(doc, by_id[i]) for i in ids]}]
    return _rebuild(doc, kept, ng=merged, filtered=list(doc.get("filtered_by_ng", [])) + dropped, round=doc.get("round", 1) + 1,
                    reselect_count=doc.get("reselect_count", 0) + 1, reselect_log=log)


def reextract_candidates(doc: dict, paragraphs: list, label: str, *, reason: str, by: str = "", ng_registry=(), call_fn=None,
                         client=None, budget_guard=None) -> dict:
    """枯渇(全候補をHumanがNG)後のStep A'' 再抽出(最大1回、MAX_RESELECTに算入)。NGは3方式で再適用されるので同じ候補は戻らない。"""
    if not (isinstance(reason, str) and reason.strip()):
        raise Part2ReviewError("再抽出の理由(reason)は必須です(M-6)")
    if not doc.get("exhausted"):
        raise Part2ReviewError("再抽出は候補が尽きた(exhausted)ときだけです")
    if doc["text_sha256"] != text_sha256(paragraphs):
        raise Part2Stale("候補docが現在の本文と一致しません")
    if doc.get("reextract_count", 0) + 1 > MAX_REEXTRACT or doc.get("reselect_count", 0) + 1 > MAX_RESELECT:
        raise Part2ReselectLimit(f"再抽出の上限(再抽出{MAX_REEXTRACT}回・再選定合計{MAX_RESELECT}回)を超えます。STOPして報告します")
    merged = _merge_ng(doc.get("ng", []), ng_registry)
    new = extract_candidates(paragraphs, label, level=level_key_of_doc(doc), call_fn=call_fn, client=client, budget_guard=budget_guard, round_no=doc.get("round", 1) + 1,
                             ng=merged, reselect_count=doc.get("reselect_count", 0) + 1, reextract_count=doc.get("reextract_count", 0) + 1)
    new["reselect_log"] = list(doc.get("reselect_log", [])) + [{"at": _now(), "event": "reextract", "by": by, "reason": reason, "kind": "reextract",
                                                                "rejected": []}]
    new["filtered_by_ng"] = list(doc.get("filtered_by_ng", [])) + new.get("filtered_by_ng", [])
    new["exhausted"] = (not new["candidates"]) and bool(new["filtered_by_ng"])
    new["reused_from_previous_run"] = False
    return new


# ------------------------------------------------------------
# 工程2: 選定(Human Review接続点。kind="grammar")
# ------------------------------------------------------------
REVIEW_CHOICES = ("top1", "top2", "reselect", "omit")
EXHAUSTED_CHOICES = ("omit", "reextract")


def review_request(doc: dict) -> dict:
    """er119共通核(kind="grammar")へ渡す提示内容。TOP1/TOP2(順位付き)と残り件数。AI推奨=TOP1。
    候補1件ならtop2を外す(R-4)。再選定は上限内のみ提示。枯渇時はomit/reextractのみ(自動ZEROにしない。M-5(c))。"""
    cands = doc["candidates"]
    top = cands[:TOP_N]
    exhausted = bool(doc.get("exhausted"))
    reselect_ok = doc.get("reselect_count", 0) < MAX_RESELECT
    if top:
        choices = ["top1"] + (["top2"] if len(top) >= 2 else []) + (["reselect"] if reselect_ok else []) + ["omit"]
    elif exhausted:
        choices = ["omit"] + (["reextract"] if reselect_ok and doc.get("reextract_count", 0) < MAX_REEXTRACT else [])
    else:
        choices = ["omit"]
    return {"kind": "grammar", "candidates_sha256": doc["candidates_sha256"], "round": doc.get("round", 1), "exhausted": exhausted,
            "reselect_count": doc.get("reselect_count", 0), "reextract_count": doc.get("reextract_count", 0),
            "top": [{"candidate_id": c["candidate_id"], "rank": c["rank"], "tier": c["tier"], "feature_class": c["feature_class"],
                     "para": c["para"], "sentence": c["sentence"], "teaching_value_ja": c["teaching_value_ja"],
                     "construct_ja": c["construct_ja"], "misread_ja": c["misread_ja"]} for c in top],
            "n_more": max(0, len(cands) - len(top)), "ai_recommended": top[0]["candidate_id"] if top else None,
            "choices": choices, "auto_default": "top1" if top else (None if exhausted else "omit"),
            "reason_required_for": list(HUMAN_REASON_REQUIRED)}


def _check_decision(doc: dict, review: dict) -> str:
    ch = review.get("choice")
    allowed = EXHAUSTED_CHOICES if doc.get("exhausted") else REVIEW_CHOICES
    if ch not in allowed:
        raise Part2ReviewError(f"choiceは {allowed} のいずれか: {ch!r}")
    if review.get("candidates_sha256") != doc["candidates_sha256"]:
        raise Part2ReviewError("reviewが古い候補listに対するものです(candidates_sha256不一致)。再レビューが必要です")
    if ch in HUMAN_REASON_REQUIRED and not (isinstance(review.get("reason"), str) and review["reason"].strip()):
        raise Part2ReviewError(f"{ch} の理由(reason)は必須です(M-6。修正内容・理由を記録する)")
    if review.get("accept_ai") and ch != "top1":
        raise Part2ReviewError("accept_aiはtop1(AI推奨の了承)のときだけ")
    return ch


def select_from_candidates(doc: dict, review: dict | None, mode) -> dict:
    """戻り値: {"status": SELECTED|ZERO|PENDING_REVIEW|RESELECT_REQUESTED|RESELECT_EXHAUSTED|REEXTRACT_REQUESTED,
                "candidate", "source", "review_status"(REVIEWED|UNREVIEWED_AUTO_ADOPTED|NO_CANDIDATE_UNREVIEWED|None), "mode_declaration"}。
    - 候補0件かつNGで尽きていない → ZERO(no_candidate)。Humanに判断対象がないので待機しないが review_status は NO_CANDIDATE_UNREVIEWED(REVIEWEDにしない。M-6)
    - 候補がNGで尽きた(exhausted) → Human無しではRESELECT_EXHAUSTEDで待機(自動ZEROにしない。M-5(c))。omit→ZERO(human_rejected_all) / reextract→REEXTRACT_REQUESTED
    - review有り(Human): choice=top1/top2/omit/reselect。candidates_sha256が違えばPart2ReviewError(stale)。top2/reselect/omit/reextractはreason必須
    - review無し: mode=er119の明示auto宣言dictのみ → TOP1自動採用(UNREVIEWED_AUTO_ADOPTED) / 'wait' → PENDING_REVIEW(有料のStep Bへ進まない)"""
    mode_kind, decl = normalize_mode(mode)
    cands = doc.get("candidates", [])
    if not cands and not doc.get("exhausted"):
        return {"status": "ZERO", "candidate": None, "source": "no_candidate", "review_status": "NO_CANDIDATE_UNREVIEWED", "mode_declaration": None}
    if doc.get("exhausted"):
        if review is None:
            return {"status": "RESELECT_EXHAUSTED", "candidate": None, "source": "pending", "review_status": None, "mode_declaration": None}
        ch = _check_decision(doc, review)
        if ch == "omit":
            return {"status": "ZERO", "candidate": None, "source": "human_rejected_all", "review_status": "REVIEWED", "mode_declaration": None}
        if doc.get("reselect_count", 0) + 1 > MAX_RESELECT or doc.get("reextract_count", 0) + 1 > MAX_REEXTRACT:
            raise Part2ReselectLimit("再抽出の上限を超えます。STOPして報告します")
        return {"status": "REEXTRACT_REQUESTED", "candidate": None, "source": "human_reextract", "review_status": None, "mode_declaration": None}
    if review is not None:
        ch = _check_decision(doc, review)
        if ch == "omit":
            return {"status": "ZERO", "candidate": None, "source": "human_omit", "review_status": "REVIEWED", "mode_declaration": None}
        if ch == "reselect":
            if doc.get("reselect_count", 0) + 1 > MAX_RESELECT:
                raise Part2ReselectLimit(f"再選定の上限({MAX_RESELECT}回)を超えます。STOPして報告します")
            return {"status": "RESELECT_REQUESTED", "candidate": None, "source": "human_reselect", "review_status": None, "mode_declaration": None}
        idx = 0 if ch == "top1" else 1
        if idx >= len(cands):
            raise Part2ReviewError("TOP2が存在しません(候補が1件のみ)")
        return {"status": "SELECTED", "candidate": cands[idx], "source": f"human_{ch}", "review_status": "REVIEWED", "mode_declaration": None}
    if mode_kind == "auto":
        return {"status": "SELECTED", "candidate": cands[0], "source": "auto_top1", "review_status": "UNREVIEWED_AUTO_ADOPTED", "mode_declaration": decl}
    return {"status": "PENDING_REVIEW", "candidate": None, "source": "pending", "review_status": None, "mode_declaration": None}


# ---- Human確定record(er119 kind="grammar" の確定docと同形。M-2/M-6) ---------------------------
def verdicts_for_choice(doc: dict, choice: str) -> dict:
    """M-5(e)/M-6: top1/top2=SELECTED+見たが選ばなかった側はNOT_SELECTED(NGではない)。omit=全てNOT_SELECTED。reselectで外した候補は doc['ng'] 側(NG)。"""
    ids = [c["candidate_id"] for c in doc["candidates"][:TOP_N]]
    if choice == "top1":
        return {ids[0]: "SELECTED", **{i: "NOT_SELECTED" for i in ids[1:]}}
    if choice == "top2":
        return {ids[0]: "NOT_SELECTED", ids[1]: "SELECTED"}
    if choice == "omit":
        return {i: "NOT_SELECTED" for i in ids}
    return {}


def grammar_selection_signature(review: dict) -> str:
    if review.get("schema") == SCHEMA_REVIEW_V2:   # v2(複数選定)は別式。v1 recordの署名式は完全に保存(下)
        return _grammar_selection_signature_v2(review)
    sel = review.get("selection", {})
    payload = {"kind": "grammar", "level": review.get("level"), "text_sha256": review.get("text_sha256"),
               "candidates_sha256": review.get("candidates_sha256"), "status": review.get("status"),
               "selection": {"choice": sel.get("choice"), "candidate_id": sel.get("candidate_id"), "zero_reason": sel.get("zero_reason")},
               "verdicts": review.get("verdicts", {}), "mode_declaration": review.get("mode_declaration"), "ng": sorted(str(e.get("candidate_id")) for e in review.get("ng", []))}
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def finalize_review_record(doc: dict, sel: dict, *, decision: dict | None = None, by: str = "", prior_history: list | None = None) -> dict:
    """確定record(kp_human_review_v1と同形、kind="grammar")。er119が永続化する(本関数は単一builder=I/Fの正本。er119が独自に作る場合も同形・同署名関数を使う)。
    status: REVIEWED(Humanが見て決めた) / UNREVIEWED_AUTO_ADOPTED(明示auto宣言でTOP1採用) / NO_CANDIDATE_UNREVIEWED(適格0件で待たずに確定。REVIEWEDではない)。"""
    if sel["status"] not in ("SELECTED", "ZERO") or sel.get("review_status") not in ALLOWED_REVIEW_STATUSES:
        raise Part2ReviewError(f"確定できない状態です: {sel.get('status')}")
    src = sel["source"]
    choice = {"auto_top1": "top1", "human_top1": "top1", "human_top2": "top2", "human_omit": "omit", "human_rejected_all": "omit",
              "no_candidate": "none"}[src]
    cand = sel.get("candidate")
    verdicts = {e["candidate_id"]: "NG" for e in doc.get("ng", []) if e.get("candidate_id")}
    if sel["review_status"] == "REVIEWED" and choice in ("top1", "top2", "omit"):
        if doc["candidates"]:
            verdicts.update(verdicts_for_choice(doc, choice))
    elif sel["review_status"] == "UNREVIEWED_AUTO_ADOPTED":
        verdicts.update({c["candidate_id"]: None for c in doc["candidates"][:TOP_N]})            # AUTO=全て未レビュー(null)
    history = list(prior_history or [])
    for ev in doc.get("reselect_log", []):
        history.append({"at": ev["at"], "event": ev["event"], "by": ev.get("by", ""), "detail": {k: v for k, v in ev.items() if k not in ("at", "event", "by")}})
    d = decision or {}
    history.append({"at": _now(), "event": "finalize", "by": by or d.get("by", ""),
                    "detail": {"source": src, "status": sel["review_status"], "choice": choice, "reason": d.get("reason"),
                               "round": doc.get("round", 1), "candidates_sha256": doc["candidates_sha256"],
                               "mode_declaration": sel.get("mode_declaration"),
                               "not_selected": [rejection_detail(doc, c) for c in doc["candidates"][:TOP_N]
                                                if choice in ("top1", "top2") and cand and c["candidate_id"] != cand["candidate_id"]]}})
    rec = {"schema": SCHEMA_REVIEW, "kind": "grammar", "level": doc["level"], "text_sha256": doc["text_sha256"],
           "candidates_sha256": doc["candidates_sha256"], "status": sel["review_status"],
           "mode_declaration": sel.get("mode_declaration"),
           "selection": {"choice": choice, "candidate_id": cand["candidate_id"] if cand else None,
                         "zero_reason": src if sel["status"] == "ZERO" else None},
           "accept_ai_default": bool(d.get("accept_ai")), "accepted_candidates_sha256": d.get("candidates_sha256") if d.get("accept_ai") else None,
           "verdicts": verdicts, "ng": list(doc.get("ng", [])), "reselect_count": doc.get("reselect_count", 0),
           "reextract_count": doc.get("reextract_count", 0), "history": history}
    rec["selection_signature"] = grammar_selection_signature(rec)
    return rec


def summarize_review_statuses(reviews) -> dict:
    """M-6: closeout・evidenceの集計。UNREVIEWED_AUTO_ADOPTED(auto_top1)とNO_CANDIDATE_UNREVIEWEDは『レビュー済み』に数えない。"""
    out = {"reviewed": 0, "unreviewed_auto_adopted": 0, "no_candidate_unreviewed": 0, "other": 0, "total": 0}
    for r in reviews:
        out["total"] += 1
        k = {"REVIEWED": "reviewed", "UNREVIEWED_AUTO_ADOPTED": "unreviewed_auto_adopted",
             "NO_CANDIDATE_UNREVIEWED": "no_candidate_unreviewed"}.get((r or {}).get("status"), "other")
        out[k] += 1
    out["human_reviewed"] = out["reviewed"]
    return out


# ------------------------------------------------------------
# 工程3: 日本語訳(Trial-07どおり。Step B自身の訳を表示。M-1)+ Step B 解説
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


_CJK_RE = re.compile(r"[　-〿぀-ヿ㐀-䶿一-鿿豈-﫿＀-￯]")
_ITEM_RE = re.compile(r"(?m)^=====ITEM (\d+)=====\s*$")
_HEAD_RE = re.compile(r"(?m)^【(.+?)】\s*$")
_TRAIL_DELIM_RE = re.compile(r"\n?={5,}[ \t\r\n]*$")


def strip_trailing_delim(text):
    """OPEN-591 第2段: LLM終端区切り`=====`(5個以上のみの終端行)を末尾から除去。`=====ITEM n=====`等の非終端・`=====`無しはバイト不変。"""
    if not isinstance(text, str):
        return text
    return _TRAIL_DELIM_RE.sub("", text)


def parse_stepb(txt: str, n: int = 1) -> dict:
    items = _ITEM_RE.split(txt or "")
    res = {int(items[i]): strip_trailing_delim(items[i + 1].strip()).strip() for i in range(1, len(items), 2)}   # OPEN-591: 最終itemを含む各item末尾の終端`=====`
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


def lookup_ref_ja(sentence: str, ref_ja_pool: dict | None) -> str | None:
    """Trial-07の規則(run_trial_07.py:161-163): Part 1で訳済みの英文と一致(_qn正規化の完全一致)したときだけ、その訳を参考訳(ref_ja)として返す。
    一致しなければ None(T1 callもしない。画面の【日本語訳】はStep B自身の訳=M-1)。"""
    if not ref_ja_pool:
        return None
    key = _qn(sentence).strip()
    for k, v in ref_ja_pool.items():
        if v and _qn(k).strip() == key:
            return v
    return None


def explain_signature(cand: dict, ref_ja: str | None) -> str:
    """解説signature。ref_ja(pool一致の参考訳)を含むので、pool側が変われば失効を検出できる(R-7)。"""
    sel = stepb_item(cand, ref_ja)
    return hashlib.sha256(json.dumps({"item": sel, "candidate_id": cand["candidate_id"], "stepb": STEPB_PROMPT_SHA256, "model": MODEL},
                                     ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def frozen_sha_of(candidate_id: str, sentence: str, explanation_md: str, translation_ja: str | None) -> str:
    """凍結した解説の内容sha(er128.frozen_shaと同一規則。突合test: 両者の出力が一致)。"""
    return hashlib.sha256(json.dumps([candidate_id, sentence, explanation_md, translation_ja], ensure_ascii=False).encode("utf-8")).hexdigest()


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
    return {"schema": SCHEMA_RESULT, "level": doc["level"], "status": "ZERO", "zero_reason": source, "selection": {"source": source},
            "text_sha256": doc["text_sha256"], "extract_signature": doc["extract_signature"], "candidates_sha256": doc["candidates_sha256"],
            "round": doc.get("round", 1), "generated_at": _now()}


def build_result(doc: dict, sel: dict, ref_ja: str | None, expl: dict) -> dict:
    c = sel["candidate"]
    return {"schema": SCHEMA_RESULT, "level": doc["level"], "status": "SELECTED", "zero_reason": None,
            "selection": {"source": sel["source"], "candidate_id": c["candidate_id"], "rank": c["rank"], "tier": c["tier"],
                          "feature_class": c["feature_class"], "para": c["para"], "sentence": c["sentence"],
                          "construct_ja": c["construct_ja"], "teaching_value_ja": c["teaching_value_ja"]},
            "text_sha256": doc["text_sha256"], "extract_signature": doc["extract_signature"], "candidates_sha256": doc["candidates_sha256"],
            "round": doc.get("round", 1), "translation_ja": expl["sections"]["日本語訳"], "translation_source": "stepB",
            "ref_ja": ref_ja, "ref_ja_source": "part1_pool" if ref_ja else None,
            "explain_signature": explain_signature(c, ref_ja), "explanation_md": expl["markdown"], "sections": expl["sections"],
            "audit": {"extract": doc.get("audit"), "explain": expl["audit"]}, "generated_at": _now()}


def result_from_frozen(doc: dict, sel: dict, fz: dict) -> dict:
    """凍結した解説(KP-CONFIRMED-CONTENT-PROTECTION-01 M6)から結果を決定論で組み立てる(LLM呼出0)。signatureの代わりに `frozen:<sha>` を持つ。"""
    c = sel["candidate"]
    token = "frozen:" + fz["frozen_sha256"][:16]
    return {"schema": SCHEMA_RESULT, "level": doc["level"], "status": "SELECTED", "zero_reason": None,
            "selection": {"source": sel["source"], "candidate_id": c["candidate_id"], "rank": c["rank"], "tier": c["tier"],
                          "feature_class": c["feature_class"], "para": c["para"], "sentence": c["sentence"],
                          "construct_ja": c["construct_ja"], "teaching_value_ja": c["teaching_value_ja"]},
            "text_sha256": doc["text_sha256"], "extract_signature": doc["extract_signature"], "candidates_sha256": doc["candidates_sha256"],
            "round": doc.get("round", 1), "translation_ja": fz.get("translation_ja"), "translation_source": "frozen",
            "ref_ja": fz.get("ref_ja_at_freeze"), "ref_ja_source": "frozen" if fz.get("ref_ja_at_freeze") else None,
            "explain_signature": token, "explanation_md": fz["explanation_md"], "sections": fz.get("sections") or {},
            "frozen": token, "frozen_source": fz.get("source"),
            "audit": {"extract": doc.get("audit"), "explain": {"frozen": True, "source": fz.get("source")}}, "generated_at": _now()}


def run_part2(paragraphs: list, label: str, *, level: str, review: dict | None = None, mode="wait", cached_candidates: dict | None = None,
              cached_result: dict | None = None, ref_ja_pool: dict | None = None, extract_call_fn=None, explain_call_fn=None,
              client=None, budget_guard=None, ng=(), allow_extract: bool = True, prior_history: list | None = None,
              frozen: dict | None = None) -> dict:
    """【v1・単一選定の legacy orchestrator】GRAMMAR-PREGEN-ALL-LEVELS-01 委任_02以降、Production配線(er120_part2_wiring_01)は呼ばない(新経路=pregen_explanations→finalize_part2_v2、LLM 0)。
    v1(単一選定)形のresultを作る互換・offline用。Step Bは `pregen_explanations`(唯一の呼出点)経由でのみ、かつ explain_call_fn / client を**明示した場合に限り**呼ぶ
    (未指定で解説が無ければ Part2Stale=fail-closed。実client自動生成はしない)。
    orchestrator(ファイルI/Oは呼出側。write_artifacts/load_artifactsを使う)。LLM callは最大2(Step A''・Step B)。T1訳callはない(M-1)。
    戻り値: {"status": SELECTED|ZERO|WAIT_STATUSES…, "candidates": doc, "result": dict|None, "review_request": dict|None, "selection": sel, "review_record": dict|None}
    待機系ではresultはNone(下流はfail-closed)。PENDING_REVIEWでは有料のStep Bを呼ばない。"""
    paragraphs = _check_paragraphs(paragraphs)
    doc = resolve_candidates(paragraphs, label, cached_candidates, level=level, call_fn=extract_call_fn, client=client, budget_guard=budget_guard, ng=ng,
                             allow_extract=allow_extract, frozen=frozen is not None)
    sel = select_from_candidates(doc, review, mode)
    if sel["status"] in WAIT_STATUSES:
        return {"status": sel["status"], "candidates": doc, "result": None, "review_request": review_request(doc), "selection": sel, "review_record": None}
    rec = finalize_review_record(doc, sel, decision=review, prior_history=prior_history)
    if sel["status"] == "ZERO":
        return {"status": "ZERO", "candidates": doc, "result": zero_result(doc, sel["source"]), "review_request": None, "selection": sel, "review_record": rec}
    c = sel["candidate"]
    if frozen is not None:   # M6: 凍結した解説を使う(再解説しない・LLM 0 call)。選定が凍結した文法と違えばfail-closed
        if c["candidate_id"] != frozen["candidate_id"] or c["sentence"] != frozen["sentence"]:
            raise Part2Stale("Part 2の確定(選定)が、凍結した確定文法と一致しません(確定後に選定が変わった疑い)")
        cr = cached_result
        if cr and cr.get("schema") == SCHEMA_RESULT and cr.get("status") == "SELECTED" and cr.get("selection", {}).get("candidate_id") == c["candidate_id"] \
                and cr.get("candidates_sha256") == doc["candidates_sha256"] and cr.get("explanation_md") == frozen["explanation_md"] \
                and cr.get("text_sha256") == doc["text_sha256"]:
            res = json.loads(json.dumps(cr))
            res["selection"]["source"] = sel["source"]
        else:
            res = result_from_frozen(doc, sel, frozen)
        res["reused_from_previous_run"] = True
        return {"status": "SELECTED", "candidates": doc, "result": res, "review_request": None, "selection": sel, "review_record": rec}
    ref_ja = lookup_ref_ja(c["sentence"], ref_ja_pool)
    if cached_result and cached_result.get("schema") == SCHEMA_RESULT and cached_result.get("status") == "SELECTED" \
            and cached_result.get("selection", {}).get("candidate_id") == c["candidate_id"] \
            and cached_result.get("candidates_sha256") == doc["candidates_sha256"] \
            and cached_result.get("explain_signature") == explain_signature(c, ref_ja) and cached_result.get("explanation_md"):
        res = json.loads(json.dumps(cached_result))
        res["selection"]["source"] = sel["source"]
        res["reused_from_previous_run"] = True
        return {"status": "SELECTED", "candidates": doc, "result": res, "review_request": None, "selection": sel, "review_record": rec}
    if explain_call_fn is None and client is None:   # Step Bは明示opt-inのみ(finalize相当の呼出で黙って課金しない)
        raise Part2Stale("Part 2の解説(事前生成物)がありません。Step Bは事前生成(pregen)でのみ呼びます。制作の解説事前生成stageを実行してください")
    ex_doc, _st = pregen_explanations(doc, None, level=level, ids=[c["candidate_id"]], source="stepB_generated",
                                      ref_ja_by_id=({c["candidate_id"]: ref_ja} if ref_ja else None), call_fn=explain_call_fn, client=client, budget_guard=budget_guard)
    it = ex_doc["items"][0]
    expl = {"markdown": it["explanation_md"], "sections": split_sections(it["explanation_md"]), "audit": it["audit"]}   # 唯一の呼出点=pregen_explanations
    res = build_result(doc, sel, ref_ja, expl)
    res["reused_from_previous_run"] = False
    return {"status": "SELECTED", "candidates": doc, "result": res, "review_request": None, "selection": sel, "review_record": rec}


def _no_extract(prompt):
    raise Part2Error("finalizeではStep A''(再抽出)を呼びません")


def finalize_part2(paragraphs: list, label: str, *, level: str, candidates_doc: dict, review: dict | None = None, mode="wait", cached_result: dict | None = None,
                   ref_ja_pool: dict | None = None, explain_call_fn=None, client=None, budget_guard=None, ng=(), prior_history: list | None = None,
                   frozen: dict | None = None) -> dict:
    """M-4: 保存済み候補と現在の確定からの再finalize(再抽出なし。Step A''は絶対に呼ばない)。待機系ならPart2PendingReviewで抜ける(出力ファイルを作らない)。
    frozen: ユーザー確定済みの文法の凍結解説(M6)。あれば解説も再生成しない。"""
    r = run_part2(paragraphs, label, level=level, review=review, mode=mode, cached_candidates=candidates_doc, cached_result=cached_result, ref_ja_pool=ref_ja_pool,
                  extract_call_fn=_no_extract, explain_call_fn=explain_call_fn, client=client, budget_guard=budget_guard, ng=ng,
                  allow_extract=False, prior_history=prior_history, frozen=frozen)
    if r["status"] in WAIT_STATUSES:
        raise Part2PendingReview(r["status"], r["review_request"], r["candidates"])
    return r


def cand_stage_input_sha(paragraphs: list, label: str) -> str:
    """M-4: Z `part2_cand_b1b` のinput_sha(本文sha+label+抽出signature[Prompt・model])。"""
    return hashlib.sha256(f"{text_sha256(paragraphs)}|{label}|{extract_signature(paragraphs, label)}".encode("utf-8")).hexdigest()


def final_stage_input_sha(paragraphs: list, label: str, grammar_review: dict) -> str:
    """M-4: Z `part2_b1b` のinput_sha = sha(text_sha|label|文法の確定selection_signature)。確定が変われば変わる(再finalize対象)。"""
    return hashlib.sha256(f"{text_sha256(paragraphs)}|{label}|{grammar_review['selection_signature']}".encode("utf-8")).hexdigest()


# ---- M-2: 使う側のfail-closed確認(Human確定・候補docと結びつける) -----------------------------
def _expected_outcome(doc: dict, review: dict, where: str, nxt: str):
    """確定recordと候補docから期待される結果を導く: ('SELECTED', cand, source) | ('ZERO', None, zero_reason)。不整合はPart2Stale。"""
    w = f"[{where}] " if where else ""
    st, sel = review.get("status"), review.get("selection") or {}
    cands = doc.get("candidates", [])
    ch = sel.get("choice")

    def stale(msg):
        return Part2Stale(f"{w}{msg}。次の一手: {nxt}")
    if st == "NO_CANDIDATE_UNREVIEWED":
        if cands or doc.get("filtered_by_ng") or ch != "none" or sel.get("candidate_id") or sel.get("zero_reason") != "no_candidate":
            raise stale("Part 2の確定(NO_CANDIDATE_UNREVIEWED)が候補docと一致しません")
        return "ZERO", None, "no_candidate"
    if st == "UNREVIEWED_AUTO_ADOPTED":
        try:
            if normalize_mode(review.get("mode_declaration"))[0] != "auto":
                raise Part2ReviewError("宣言なし")
        except Part2ReviewError as e:
            raise stale(f"Part 2の自動採用にer119の明示auto宣言がありません({e})")
        if not cands or ch != "top1" or sel.get("candidate_id") != cands[0]["candidate_id"]:
            raise stale("Part 2の自動採用(auto_top1)が現在の候補docのTOP1と一致しません")
        return "SELECTED", cands[0], "auto_top1"
    if st == "REVIEWED":
        if ch in ("top1", "top2"):
            idx = 0 if ch == "top1" else 1
            if idx >= len(cands) or sel.get("candidate_id") != cands[idx]["candidate_id"]:
                raise stale(f"Part 2のHuman確定({ch})が現在の候補docと一致しません")
            return "SELECTED", cands[idx], f"human_{ch}"
        if ch == "omit":
            zr = sel.get("zero_reason")
            if (zr == "human_omit" and cands) or (zr == "human_rejected_all" and not cands and doc.get("exhausted")):
                return "ZERO", None, zr
            raise stale("Part 2のHuman省略(omit)が現在の候補docと一致しません")
    raise stale(f"Part 2の確定statusが不正または前進不可です: {st}/{ch}")


def require_fresh_part2(result: dict | None, paragraphs: list, label: str, *, next_command: str, where: str = "",
                        candidates_doc: dict | None, grammar_review: dict | None, ref_ja_pool: dict | None = None,
                        frozen=None, explanations: dict | None = None) -> None:
    """使う側(TTS/assembly/pages/player/公開ページbuilder)のfail-closed確認。無い/古い/不整合ならPart2Stale(次コマンド付き)。
    M-2: 本文sha・抽出signatureに加え、(i)確定statusが前進可 (ii)result.candidates_sha256==現在の候補doc (iii)result.selection==確定のchoiceに対応する候補
    (iv)候補docの材料欄でexplain_signatureを再計算して一致 (v)確定のselection_signatureを再計算して一致。ZEROも確定と候補docに結びつく。
    事後レビューでTOP2へ変えた後・reselect/omit後の古い結果(auto_top1等)は拒否される。candidates_doc/grammar_reviewは必須(省略不可)。"""
    w = f"[{where}] " if where else ""
    nxt = next_command
    if result and result.get("schema") == SCHEMA_RESULT_V2:   # v2(items[])。v1 resultは下の既存検査(review v1 かつ result v1 = legacy)
        return _require_fresh_part2_v2(result, paragraphs, label, next_command=nxt, where=where, candidates_doc=candidates_doc, grammar_review=grammar_review,
                                       frozen=([frozen] if isinstance(frozen, dict) else frozen), explanations=explanations)
    if not result or result.get("schema") != SCHEMA_RESULT:
        raise Part2Stale(f"{w}Part 2 artifactがありません。次の一手: {nxt}")
    if isinstance(frozen, list):
        raise Part2Stale(f"{w}v1の結果に複数itemの凍結値は適用できません。次の一手: {nxt}")
    paragraphs = _check_paragraphs(paragraphs)
    # M6(frozen): ユーザー確定済みの文法は extract/explain signature の代わりに `frozen:<sha>`+選定文の逐語span+candidate_id一致で判定する(Prompt/model/routing変更で失効しない)
    if result.get("text_sha256") != text_sha256(paragraphs) or (frozen is None and result.get("extract_signature") != extract_signature(paragraphs, label)):
        raise Part2Stale(f"{w}Part 2が現在の本文・Prompt・modelと一致しません(古い)。次の一手: {nxt}")
    if not candidates_doc or candidates_doc.get("schema") != SCHEMA_CANDIDATES:
        raise Part2Stale(f"{w}Part 2の候補docがありません。次の一手: {nxt}")
    if candidates_doc.get("text_sha256") != text_sha256(paragraphs) or (frozen is None and candidates_doc.get("extract_signature") != extract_signature(paragraphs, label)) \
            or candidates_doc.get("candidates_sha256") != candidates_sha256(candidates_doc.get("candidates", [])):
        raise Part2Stale(f"{w}Part 2の候補docが現在の本文と一致、または自己整合していません。次の一手: {nxt}")
    if not grammar_review or grammar_review.get("schema") != SCHEMA_REVIEW or grammar_review.get("kind") != "grammar":
        raise Part2Stale(f"{w}Part 2のHuman確定recordがありません。次の一手: {nxt}")
    if grammar_review.get("status") not in ALLOWED_REVIEW_STATUSES:
        raise Part2Stale(f"{w}Part 2の確定statusが前進不可です: {grammar_review.get('status')}(判断待ち・再選定中・stale)。次の一手: {nxt}")
    if grammar_review.get("candidates_sha256") != candidates_doc["candidates_sha256"] or grammar_review.get("text_sha256") != candidates_doc["text_sha256"]:
        raise Part2Stale(f"{w}Part 2の確定が現在の候補docに対するものではありません。次の一手: {nxt}")
    if grammar_review.get("selection_signature") != grammar_selection_signature(grammar_review):
        raise Part2Stale(f"{w}Part 2の確定のselection_signatureが一致しません(手編集の疑い)。次の一手: {nxt}")
    kind, cand, source = _expected_outcome(candidates_doc, grammar_review, where, nxt)
    if result.get("candidates_sha256") != candidates_doc["candidates_sha256"]:
        raise Part2Stale(f"{w}Part 2の結果が現在の候補docから作られたものではありません(再選定・再抽出後の古い結果)。次の一手: {nxt}")
    if kind == "ZERO":
        if result.get("status") != "ZERO" or result.get("zero_reason") != source:
            raise Part2Stale(f"{w}Part 2の結果が確定(省略/適格なし: {source})と一致しません。次の一手: {nxt}")
        return
    if result.get("status") != "SELECTED":
        raise Part2Stale(f"{w}Part 2のstatusが確定(選定)と一致しません: {result.get('status')}。次の一手: {nxt}")
    sel = result["selection"]
    if sel.get("candidate_id") != cand["candidate_id"] or sel.get("source") != source \
            or sel.get("para") != cand["para"] or sel.get("sentence") != cand["sentence"]:
        raise Part2Stale(f"{w}Part 2の結果の選定が確定した候補({source})と一致しません。次の一手: {nxt}")
    if not verify_single_span({"body": paragraphs}, sel.get("para"), sel.get("sentence")):
        raise Part2Stale(f"{w}Part 2の選定文が本文の単一段落の逐語spanではありません。次の一手: {nxt}")
    if candidate_id(sel["para"], sel["sentence"]) != sel["candidate_id"]:
        raise Part2Stale(f"{w}Part 2の候補IDが不整合です。次の一手: {nxt}")
    secs = result.get("sections") or {}
    if not result.get("explanation_md") or not secs or not secs.get("日本語訳") or result.get("translation_ja") != secs.get("日本語訳"):
        raise Part2Stale(f"{w}Part 2の解説または訳(Step Bの【日本語訳】)が欠落・不整合です。次の一手: {nxt}")
    if frozen is not None:   # signature(Prompt/model依存)の代わりに、凍結した解説全文・訳との一致(frozen:<sha>)で判定。参考訳poolの変化は呼出側(wiring)がISSUEで扱う
        if frozen_sha_of(sel["candidate_id"], sel["sentence"], result["explanation_md"], result.get("translation_ja")) != frozen.get("frozen_sha256"):
            raise Part2Stale(f"{w}Part 2の解説が凍結した確定解説(frozen:{str(frozen.get('frozen_sha256'))[:16]})と一致しません。次の一手: {nxt}")
    else:
        if result.get("explain_signature") != explain_signature(cand, result.get("ref_ja")):
            raise Part2Stale(f"{w}Part 2の解説signatureが候補docの材料欄から再計算した値と一致しません。次の一手: {nxt}")
        if ref_ja_pool is not None and result.get("ref_ja") != lookup_ref_ja(sel["sentence"], ref_ja_pool):
            raise Part2Stale(f"{w}Part 2の参考訳が現在のPart 1訳poolと一致しません(再生成が必要)。次の一手: {nxt}")
    if PAGE_FORBIDDEN_RE.search(result["explanation_md"]):
        raise Part2Stale(f"{w}Part 2の解説にページ非表示語が含まれます。次の一手: {nxt}")


# ---- R-3: 確定 <-> part2_result.json <-> study_text/*.md <-> 公開HTML の一致検証(module側) ------------------
def verify_selection_matches_outputs(*, kind: str = "grammar", paragraphs: list, label: str, candidates_doc: dict, grammar_review: dict,
                                     result: dict, md_text: str | None = None, html_text: str | None = None, next_command: str,
                                     where: str = "", ref_ja_pool: dict | None = None, frozen=None, explanations: dict | None = None,
                                     section_scoped: bool = False) -> None:
    """kind='grammar'のみ。不一致はPart2Stale。md_text/html_textを渡した場合は決定論の描画(render_markdown / render_html_block)と照合する。
    html_textは『render_html_block(include_css=False)の出力を部分文字列として含む』ことを確認(ページbuilderが包む前提。包み方は呼出側)。
    0件(status!=SELECTED)の期待は『md不在(md_text="")・節内の文法ブロック0個』(固定文面なし)。"""
    if kind != "grammar":
        raise ValueError(f"このmoduleが検証できるのは kind='grammar' のみ: {kind!r}")
    require_fresh_part2(result, paragraphs, label, next_command=next_command, where=where, candidates_doc=candidates_doc,
                        grammar_review=grammar_review, ref_ja_pool=ref_ja_pool, frozen=frozen, explanations=explanations)
    w = f"[{where}] " if where else ""
    if html_text is not None and section_scoped and count_grammar_blocks(html_text) != expected_grammar_blocks(result):   # O-6: 自levelの節の文法ブロック数=期待数(SELECTED=1 / 0件=0。取り違え・欠落・重複・0件なのに残存を検出)
        raise Part2Stale(f"{w}公開HTMLの当該levelの節のPart 2文法ブロック数が期待と一致しません(件数={count_grammar_blocks(html_text)} / 期待={expected_grammar_blocks(result)}。"
                         f"文法0件はコーナー全体が非表示)。次の一手: {next_command}")
    if md_text is not None and md_text != render_markdown(result):
        raise Part2Stale(f"{w}study_text/のPart 2 markdownが確定結果(part2_result.json)と一致しません。次の一手: {next_command}")
    if html_text is not None and render_html_block(result, include_css=False) not in html_text:
        raise Part2Stale(f"{w}公開HTMLのPart 2ブロックが確定結果(part2_result.json)と一致しません。次の一手: {next_command}")


# ---- M-7: 失敗の記録(part2_failed.json。有料工程をやり直させない案内用) --------------------------
def write_failed_record(dir_path: str, exc: BaseException, *, next_command: str, stage: str = "") -> str:
    os.makedirs(dir_path, exist_ok=True)
    p = f"{dir_path}/{FAILED_FILENAME}"
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump({"schema": "part2_failed_v1", "stage": stage, "error_type": type(exc).__name__, "error": str(exc)[:500],
                   "next_command": next_command, "at": _now()}, f, ensure_ascii=False, indent=2)
    return p


# ------------------------------------------------------------
# 保存・描画
# ------------------------------------------------------------
def write_artifacts(dir_path: str, doc: dict | None, result: dict | None) -> dict:
    """study_text/ へ grammar_candidates.json / part2_result.json / .md を保存(UTF-8, LF)。待機系(result=None)ではresult/mdを作らない(M-4)。"""
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
        md_text = render_markdown(result)
        if md_text:
            out["md"] = f"{dir_path}/{PART2_FILE_STEM}.md"
            with open(out["md"], "w", encoding="utf-8", newline="\n") as f:
                f.write(md_text)
        else:   # 0件=mdを書かない(内部artifactにも固定文面・プレースホルダーを残さない)。以前のmdが残っていれば退避(削除しない)
            out["md_retired"] = retire_part2_md(dir_path)
    return out


def retire_part2_md(dir_path: str, *, only_legacy: bool = False) -> str | None:
    """0件結果なのに以前のPart 2 markdownが残っているとき、削除せず退避する(M-6)。旧固定文面とバイト一致=`.legacy_zero_p2.md`、それ以外(SELECTED時代の残骸)=
    `.superseded_by_zero.md`。決定論(同入力で同じ退避先)・冪等(mdが無ければ何もしない)。戻り=退避先path|None。
    only_legacy=True(検証側から呼ぶ場合): 旧固定文面と完全一致するmdだけ退避する。それ以外のmdは触らず、0件の期待(md不在)との不一致として検証がPart2Staleにする。"""
    md = f"{dir_path}/{PART2_FILE_STEM}.md"
    if not os.path.exists(md):
        return None
    with open(md, encoding="utf-8", newline="") as f:
        cur = f.read()
    is_legacy = cur == _legacy_zero_markdown()
    if only_legacy and not is_legacy:
        return None
    suffix = LEGACY_ZERO_GRAMMAR_MD_SUFFIX if is_legacy else ".superseded_by_zero.md"
    dst = f"{dir_path}/{PART2_FILE_STEM}{suffix}"
    os.replace(md, dst)
    return dst


def _legacy_zero_markdown() -> str:
    """旧仕様(2026-10-29以前)が0件のときに書いていたmarkdown(バイト列)。退避判定専用。"""
    return "\n".join(["# Grammar & Sentence Structure", "", _LEGACY_ZERO_GRAMMAR_BODY, ""])


def load_json(path: str) -> dict | None:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def render_markdown(result: dict) -> str:
    """Part 1と同じく節見出しにPart番号を出さない(Part 3/4未採用の番号参照=Dangling防止)。**0件は空文字**(コーナー全体を出さない。ユーザー正式決定2026-10-29 §2C)。
    【日本語訳】はStep B自身の訳(Trial-07どおり。M-1)。"""
    if result.get("status") != "SELECTED":
        return ""
    L = ["# Grammar & Sentence Structure", ""]
    for it in result_items(result):   # 1件はv1とバイト同一。2件以上は同ブロックを(本文出現順の)item順に連結
        s, sec = it["selection"], it["sections"]
        L += ["## 対象となる本文英文", "", f"> {s['sentence']}", ""]
        for h in EXPLANATION_HEADINGS:
            if h in sec:
                L += [f"**{h}**", strip_trailing_delim(sec[h]), ""]   # 表示層の共通防御(凍結データは不変)
    return "\n".join(L)


def render_html_block(result: dict, *, include_css: bool = True) -> str:
    """ページ用のstudy block(Part 1の `<section class='study'>` と同じ規約。<table>/<h2>不使用)。**0件は空文字**(見出し・空枠・固定文面を出さない。CSSも出さない)。
    LLM出力はHTMLエスケープ後に**→<b>。Part 1ブロックの直後に連結する場合は compose_study_html を使う(R-1)。"""
    import er003_kp_general_explanation_01 as p1
    if result.get("status") != "SELECTED":
        return ""
    parts = ["<section class='study'><h3>Grammar &amp; Sentence Structure</h3>"]
    for it in result_items(result):   # itemごと(新規確定は<=1。旧2件結果の読取互換)に<div class='study-item'>。<section>と<h3>は1つ
        s, sec = it["selection"], it["sections"]
        dl = [f"<dt>対象となる本文英文</dt><dd>{html.escape(s['sentence'], quote=False)}</dd>"]
        for h in EXPLANATION_HEADINGS:
            if h in sec:
                dl.append(f"<dt>{html.escape(h, quote=False)}</dt><dd>{p1._paragraphs_html(strip_trailing_delim(sec[h]))}</dd>")   # OPEN-591 表示層の共通防御(凍結データは不変)
        parts.append(f"<div class='study-item'><dl>{''.join(dl)}</dl></div>")
    parts.append("</section>")
    return (p1.STUDY_CSS if include_css else "") + "".join(parts)


# ------------------------------------------------------------
# ニュアンス解説(独立コーナー。ユーザー正式決定2026-10-29 APPROVED_FOR_PRODUCTION)。表示は採用(ADOPTED)のときだけ。
# nuance = 確定結果dict(`nuance_result.json`。finalizeはer134/委任_02C)。契約(表示側が読む最小キー):
#   {"status": "ADOPTED"|"REJECTED"|"NONE"|..., "candidate": {"expression","focus","explanation_ja","quote_en","quote_ja"}}
#   ADOPTED以外=空文字(見出し・空枠・プレースホルダーなし)。ADOPTEDなのに必須キー欠落=Part2Stale(黙って非表示にしない)。
# ------------------------------------------------------------
NUANCE_REQUIRED_FIELDS = ("expression", "focus", "explanation_ja", "quote_en", "quote_ja")


def nuance_is_adopted(nuance) -> bool:
    return isinstance(nuance, dict) and nuance.get("status") == NUANCE_ADOPTED


def expected_grammar_blocks(result) -> int:
    """節に出るべき文法ブロック数(SELECTED=1 / 0件=0)。検査側(verify_selection_matches_outputs・各runnerのpage_verify)はこの関数だけを期待値にする。"""
    return 1 if (isinstance(result, dict) and result.get("status") == "SELECTED") else 0


def expected_nuance_blocks(nuance) -> int:
    return 1 if nuance_is_adopted(nuance) else 0


def nuance_candidate_of(nuance: dict) -> dict:
    """ADOPTED結果の候補本文(必須キーが無い/空はPart2Stale。fail-closed)。"""
    cand = nuance.get("candidate")
    miss = [k for k in NUANCE_REQUIRED_FIELDS if not isinstance(cand, dict) or not str(cand.get(k) or "").strip()]
    if miss:
        raise Part2Stale(f"ニュアンス解説の確定結果(status=ADOPTED)に必須項目がありません: {miss}。黙って非表示にはしません(nuance_result.jsonを確認してください)")
    return cand


def nuance_text_fields(nuance: dict) -> list:
    """ページ非表示語の検査(M-7)対象=表示される全文字列。"""
    cand = nuance_candidate_of(nuance)
    return [str(cand[k]) for k in NUANCE_REQUIRED_FIELDS]


def render_nuance_html_block(nuance, *, include_css: bool = True) -> str:
    """独立コーナー『ニュアンス解説』(採用時のみ。他は空文字)。Part 1/文法と同じ規約(`<section class='study'>`・<h3>・<div class='study-item'>・<dl>、<table>/<h2>不使用)。
    LLM出力はHTMLエスケープ後に**→<b>(`er003._paragraphs_html`)。LLM関数を取らない決定論の描画。"""
    import er003_kp_general_explanation_01 as p1
    if not nuance_is_adopted(nuance):
        return ""
    c = nuance_candidate_of(nuance)
    dl = [f"<dt>ポイント</dt><dd>{html.escape(c['focus'], quote=False)}</dd>",
          f"<dt>解説</dt><dd>{p1._paragraphs_html(c['explanation_ja'])}</dd>",
          f"<dt>本文の英文</dt><dd>{html.escape(c['quote_en'], quote=False)}</dd>",
          f"<dt>日本語訳</dt><dd>{html.escape(c['quote_ja'], quote=False)}</dd>"]
    body = f"<div class='study-item'><h4>{html.escape(c['expression'], quote=False)}</h4><dl>{''.join(dl)}</dl></div>"
    return (p1.STUDY_CSS if include_css else "") + f"<section class='study'><h3>{NUANCE_HEADING}</h3>{body}</section>"


def compose_study_html(part1_html: str, result: dict, nuance=None) -> str:
    """R-1: Part 1 -> 文法(Part 2) -> ニュアンス解説 の順に連結する唯一の合成関数。各ブロックは該当しなければ空文字(文法0件・不採用・候補なしはコーナー全体を出さない)。
    CSS(STUDY_CSS)は『最初の非空ブロック』が持つ(Part 1はSTUDY_CSS込みで返る)。3ブロックとも空なら空文字(CSSも出さない)。
    nuance=None(既定)は従来呼出との互換用(ニュアンス解説なし)。Production呼出元は`er120_part2_wiring_01.compose_page_html`が必須keywordで渡す(R-6)。"""
    part1_html = part1_html or ""
    gram_html = render_html_block(result, include_css=not part1_html)
    nuance_html = render_nuance_html_block(nuance, include_css=not (part1_html or gram_html))
    return part1_html + gram_html + nuance_html


def count_nuance_blocks(html_text: str) -> int:
    """HTML(または節)内のニュアンス解説ブロック(`<h3>ニュアンス解説</h3>`)の数。"""
    return html_text.count(f"<h3>{NUANCE_HEADING}</h3>")


_STUDY_SECTION_RE = re.compile(r"<section class='study'>(.*?)</section>", re.S)


def count_empty_study_sections(html_text: str) -> int:
    """見出しだけ・本文なしの`<section class='study'>`(空枠)の数。0件コーナーの固定文面撤去後は常に0であること(否定検査)。"""
    n = 0
    for m in _STUDY_SECTION_RE.finditer(html_text):
        if not m.group(1).startswith("<h3>"):   # 見出し付きの学習ブロック(Part 1/文法/ニュアンス解説)だけが対象
            continue
        inner = re.sub(r"<h3>.*?</h3>", "", m.group(1), flags=re.S)
        if "<div class='study-item'>" not in inner or not re.sub(r"<[^>]+>", "", inner).strip():
            n += 1
    return n


def verify_nuance_in_section(nuance, html_text: str, *, next_command: str, where: str = "") -> None:
    """M-7: 当該levelの節(html_text)のニュアンス解説を節単位で検証する(文法のO-6と同型)。(1)ブロック数=期待(ADOPTED=1 / 他=0) (2)ADOPTEDなら決定論の描画が節に含まれる
    (Std/Advの取り違え・改変を検出) (3)表示される全文字列にページ非表示語(PAGE_FORBIDDEN_RE)がない (4)空の`<section class='study'>`がない。不一致=Part2Stale。"""
    w = f"[{where}] " if where else ""
    exp, got = expected_nuance_blocks(nuance), count_nuance_blocks(html_text)
    if got != exp:
        raise Part2Stale(f"{w}公開HTMLの当該levelの節のニュアンス解説ブロック数が期待と一致しません(件数={got} / 期待={exp}。採用以外は非表示)。次の一手: {next_command}")
    if exp:
        for t in nuance_text_fields(nuance):
            if PAGE_FORBIDDEN_RE.search(t):
                raise Part2Stale(f"{w}ニュアンス解説の表示文にページ非表示語が含まれます。次の一手: {next_command}")
        if render_nuance_html_block(nuance, include_css=False) not in html_text:
            raise Part2Stale(f"{w}公開HTMLのニュアンス解説ブロックが確定結果(nuance_result.json)と一致しません(levelの取り違え・改変の疑い)。次の一手: {next_command}")
    if count_empty_study_sections(html_text):
        raise Part2Stale(f"{w}公開HTMLの当該levelの節に空の学習ブロック(見出しだけ)があります。次の一手: {next_command}")


# ============================================================
# GRAMMAR-PREGEN-ALL-LEVELS-01 委任_02(2026-10-27): 全level共通の事前生成核 + v2 schema(契約=docs/research/GRAMMAR-PREGEN-ALL-LEVELS-01/SCHEMA_CONTRACT_01.md)
# ユーザー正式決定(APPROVED_FOR_PRODUCTION): 候補抽出(Step A'')の直後にTop1/Top2(=PREGEN_MAX件)のStep Bだけを事前生成し、Top1/Top2の解説全文を見て原則1件(0件可・2件禁止)を選ぶ(2026-10-27改訂: 旧=全候補<=8・最大2件)。
# 確定後のfinalizeはLLM 0 call(事前生成物/凍結値から決定論で組立)。Prompt(STEPA/STEPB本文・sha)・eligible7・Trial-08 Tier・TOP_Nの意味は無変更。
# Step Bの呼出点は pregen_explanations の1か所だけ(Opus O-3: 二重生成防止)。
# ============================================================
class Part2IntegrityError(Part2Stale):
    """INTEGRITY(STOP rc=3): v2成果物があるのに事前生成物が無い(copy-runでの欠落・手動削除の疑い)等。黙って旧経路/再生成へ落とさない。"""


def level_name(level) -> str:
    """levelキー('b1b'|'a2') -> 候補docの表示名。**必須引数・既定値なし**(None/不正は課金前にPart2InputError)。"""
    if level not in LEVELS:
        raise Part2InputError(f"levelは {sorted(LEVELS)} のいずれかを必ず指定してください(既定値なし): {level!r}")
    return LEVELS[level]


def level_key_of_doc(doc: dict) -> str:
    for k, v in LEVELS.items():
        if v == (doc or {}).get("level"):
            return k
    raise Part2Stale(f"候補docのlevel欄が不正です: {(doc or {}).get('level')!r}")


def check_doc_level(doc: dict | None, level) -> None:
    """候補docの`level`欄と呼出しの`level`が一致することを確認(pathから推定しない。不一致=fail-closed)。doc=Noneは何もしない。"""
    name = level_name(level)
    if doc is not None and doc.get("level") != name:
        raise Part2Stale(f"候補docのlevel({doc.get('level')!r})が呼出しのlevel({level}={name})と一致しません(別levelのstudy dirを渡した疑い)。fail-closed")


def text_order_key(c: dict):
    sp = _span_of(c)
    return (int(re.sub(r"\D", "", str(c["para"])) or 0), sp[0] if sp else 0, c["candidate_id"])


def order_by_text(cands) -> list:
    """本文出現順(段落番号->段落内位置)。ユーザーのクリック順・rank順に依存しない(決定論)。"""
    return sorted(cands, key=text_order_key)


# ---- 事前生成物(grammar_explanations.json) ----------------------------------------------------
def explanation_sha256(md: str) -> str:
    return hashlib.sha256(md.encode("utf-8")).hexdigest()


def explanations_digest(items: list) -> str:
    return hashlib.sha256(json.dumps(sorted([i["candidate_id"], i["explanation_sha256"]] for i in items), ensure_ascii=False).encode("utf-8")).hexdigest()


def _make_expl_item(cand: dict, expl: dict, doc: dict, *, source: str, ref_ja: str | None = None) -> dict:
    audit = expl["audit"]
    return {"candidate_id": cand["candidate_id"], "level": doc["level"], "title": cand["construct_ja"], "sentence": cand["sentence"], "para": cand["para"],
            "explanation_md": expl["markdown"], "translation_ja": expl["sections"]["日本語訳"], "explanation_sha256": explanation_sha256(expl["markdown"]),
            "explain_signature": explain_signature(cand, ref_ja), "generated_at": _now(), "model_id": audit.get("model"), "source": source, "audit": audit}


def _assemble_explanations(doc: dict, items: list) -> dict:
    order = {c["candidate_id"]: i for i, c in enumerate(doc["candidates"])}
    items = sorted([i for i in items if i["candidate_id"] in order], key=lambda i: order[i["candidate_id"]])
    have = {i["candidate_id"] for i in items}
    skipped = [c["candidate_id"] for c in doc["candidates"][PREGEN_MAX:] if c["candidate_id"] not in have]
    return {"schema": SCHEMA_EXPLANATIONS, "level": doc["level"], "text_sha256": doc["text_sha256"], "candidates_sha256": doc["candidates_sha256"],
            "stepb_prompt_sha256": STEPB_PROMPT_SHA256, "model": MODEL, "pregen_max": PREGEN_MAX, "items": items, "skipped_over_cap": skipped,
            "explanations_sha256": explanations_digest(items), "written_at": _now()}


def pregen_targets(doc: dict, ids=None) -> list:
    """事前生成の対象。ids=None: 候補doc先頭PREGEN_MAX件。ids指定(確定済みrunの選定済みid限定): その候補だけ(候補doc内に限る)。"""
    cands = doc.get("candidates") or []
    if ids is None:
        return cands[:PREGEN_MAX]
    want = list(dict.fromkeys(ids))
    by_id = {c["candidate_id"]: c for c in cands}
    bad = [i for i in want if i not in by_id]
    if bad:
        raise Part2ReviewError(f"事前生成の対象が候補docにありません: {bad}")
    return [by_id[i] for i in want]


def pregen_explanations(doc: dict, existing: dict | None, *, level: str, ids=None, source: str = "pregen", ref_ja_by_id: dict | None = None,
                        call_fn=None, client=None, budget_guard=None, on_progress=None) -> tuple:
    """**Step B(解説)の唯一の呼出点**。対象候補ごとに、有効な既存解説(explain_signature一致)があれば再利用(API 0)、無ければ `generate_explanation` を1 call(直列。
    `_run_llm`の技術retry1回・モデル不一致STOP・fallbackなし・budget_guardは無変更)。1候補ごとに `on_progress(explanations_doc)` を呼ぶので、途中失敗でも成功分が保存でき、
    再開は未生成分だけ(Part2Errorはそのまま伝播=呼出側が part2_failed.json を書いてSTOP)。
    戻り値: (explanations_doc, {"generated":[id], "reused":[id]})。候補docに無い既存itemは捨てる(reselect/NG後の古い解説)。"""
    check_doc_level(doc, level)
    targets = pregen_targets(doc, ids)
    by_id = {c["candidate_id"]: c for c in doc.get("candidates") or []}
    kept = {}
    for it in (existing or {}).get("items") or []:
        c = by_id.get(it.get("candidate_id"))
        if c is not None and _expl_item_ok(it, c, (ref_ja_by_id or {}).get(c["candidate_id"])):
            kept[it["candidate_id"]] = it
    stats = {"generated": [], "reused": []}
    for c in targets:
        cid = c["candidate_id"]
        if cid in kept:
            stats["reused"].append(cid)
            continue
        ref = (ref_ja_by_id or {}).get(cid)
        expl = generate_explanation(c, ref, call_fn=call_fn, client=client, budget_guard=budget_guard)   # <- Step Bの唯一の呼出点
        kept[cid] = _make_expl_item(c, expl, doc, source=source, ref_ja=ref)
        stats["generated"].append(cid)
        if on_progress is not None:
            on_progress(_assemble_explanations(doc, list(kept.values())))
    return _assemble_explanations(doc, list(kept.values())), stats


def _expl_item_ok(it: dict, cand: dict, ref_ja: str | None = None) -> bool:
    md = it.get("explanation_md")
    return bool(md and it.get("candidate_id") == cand["candidate_id"] and it.get("explanation_sha256") == explanation_sha256(md)
                and it.get("explain_signature") == explain_signature(cand, ref_ja))


def explanations_complete(doc: dict, ex: dict | None, ids=None) -> tuple:
    """(complete: bool, missing_ids: list)。対象(先頭PREGEN_MAX件/ids)の全候補に有効な解説があること。例外を出さない判定用。"""
    have = {it.get("candidate_id"): it for it in (ex or {}).get("items") or []} if (ex or {}).get("schema") == SCHEMA_EXPLANATIONS else {}
    missing = []
    for c in pregen_targets(doc, ids):
        it = have.get(c["candidate_id"])
        if it is None or not _expl_item_ok(it, c):
            missing.append(c["candidate_id"])
    return (not missing), missing


def validate_explanations(ex: dict | None, doc: dict, *, level: str, next_command: str = "", ids=None, require_complete: bool = True) -> dict:
    """事前生成物の整合検査(fail-closed。Part2Stale)。schema・level・本文sha・全itemのsha/signature/構造・digest・(require_complete=True)対象の完全性。
    フォームexporter・grammar-show・HR提示・finalizeの入口が使う。不完全/不整合のままデータを出さない(Opus O-9)。"""
    nxt = f"。次の一手: {next_command}" if next_command else ""
    check_doc_level(doc, level)
    if not ex or ex.get("schema") != SCHEMA_EXPLANATIONS:
        raise Part2Stale(f"文法解説の事前生成物(grammar_explanations.json)がありません{nxt}")
    if ex.get("level") != doc["level"] or ex.get("text_sha256") != doc["text_sha256"]:
        raise Part2Stale(f"文法解説の事前生成物が現在の候補doc(level/本文)と一致しません{nxt}")
    by_id = {c["candidate_id"]: c for c in doc.get("candidates") or []}
    seen = set()
    for it in ex.get("items") or []:
        c = by_id.get(it.get("candidate_id"))
        if c is None or it["candidate_id"] in seen:
            raise Part2Stale(f"文法解説の事前生成物に、現在の候補docに無い/重複する項目があります({it.get('candidate_id')}){nxt}")
        seen.add(it["candidate_id"])
        if not _expl_item_ok(it, c):
            raise Part2Stale(f"文法解説の事前生成物の項目が候補docの材料欄・Prompt・modelと一致しません({it['candidate_id']}){nxt}")
        try:
            secs = split_sections(it["explanation_md"])
        except Part2StructureError as e:
            raise Part2Stale(f"文法解説の事前生成物の構造が不正です({it['candidate_id']}): {e}{nxt}") from e
        if it.get("translation_ja") != secs.get("日本語訳") or it.get("title") != c["construct_ja"] or it.get("sentence") != c["sentence"] \
                or it.get("level") != doc["level"] or it.get("source") not in ("pregen", "stepB_generated"):
            raise Part2Stale(f"文法解説の事前生成物の項目が不整合です({it['candidate_id']}){nxt}")
    if ex.get("explanations_sha256") != explanations_digest(ex.get("items") or []):
        raise Part2Stale(f"文法解説の事前生成物のexplanations_sha256が一致しません(書換えの疑い){nxt}")
    if require_complete:
        ok, missing = explanations_complete(doc, ex, ids)
        if not ok:
            raise Part2Stale(f"文法解説の事前生成が完了していません(未生成: {missing}){nxt}")
    return ex


def explanation_sha_by_id(ex: dict | None, ids) -> dict:
    have = {it["candidate_id"]: it["explanation_sha256"] for it in (ex or {}).get("items") or []}
    return {i: have[i] for i in ids if i in have}


# ---- 選定 v2(Top1/Top2提示・原則1件・0件可・2件禁止。top1/top2は単件ショートカット) -------------------------------------
def _pick_ids(doc: dict, review: dict) -> list:
    ch = review.get("choice")
    cands = doc.get("candidates") or []
    if ch == "pick":
        ids = list(review.get("candidate_ids") or [])
    else:
        raise Part2ReviewError(f"pick以外はここでは扱いません: {ch!r}")
    if not ids or len(ids) > GRAMMAR_MAX or len(set(ids)) != len(ids):
        raise Part2ReviewError(f"文法は{GRAMMAR_MAX}件だけ選べます(2件同時選択は禁止。0件はomit): {ids}")
    shown = {c["candidate_id"] for c in cands[:PREGEN_MAX]}
    bad = [i for i in ids if i not in shown]
    if bad:
        raise Part2ReviewError(f"選べるのは提示されたTop1/Top2(先頭{PREGEN_MAX}件)だけです: {bad}")
    return ids


def select_from_candidates_v2(doc: dict, review: dict | None, mode) -> dict:
    """v1のselect_from_candidatesの複数選定版。choice=pick(candidate_ids 1件。2件はPart2ReviewError)を追加し、top1/top2/omit/reselect/reextract・exhausted・ZERO・auto(TOP1のみ)・wait は
    v1と同一規則(v1関数へ委譲)。戻り値は v1 と同形 + "selected": [候補...](本文出現順。ZERO/待機は[])。"""
    if review is not None and review.get("choice") == "pick":
        if doc.get("exhausted") or not (doc.get("candidates") or []):
            raise Part2ReviewError("候補がありません(omit か reextract を選んでください)")
        if review.get("candidates_sha256") != doc["candidates_sha256"]:
            raise Part2ReviewError("reviewが古い候補listに対するものです(candidates_sha256不一致)。再レビューが必要です")
        ids = _pick_ids(doc, review)
        top1 = doc["candidates"][0]["candidate_id"]
        if ids != [top1] and not (isinstance(review.get("reason"), str) and review["reason"].strip()):
            raise Part2ReviewError("AI推奨(TOP1のみ)以外を選ぶ場合の理由(reason)は必須です(M-6。修正内容・理由を記録する)")
        if review.get("accept_ai") and ids != [top1]:
            raise Part2ReviewError("accept_aiはAI推奨(TOP1のみ)を選ぶときだけ")
        by_id = {c["candidate_id"]: c for c in doc["candidates"]}
        sel = order_by_text([by_id[i] for i in ids])
        return {"status": "SELECTED", "candidate": sel[0], "selected": sel, "source": "human_pick", "review_status": "REVIEWED", "mode_declaration": None}
    out = select_from_candidates(doc, review, mode)
    out = dict(out)
    out["selected"] = [out["candidate"]] if out.get("status") == "SELECTED" and out.get("candidate") else []
    return out


def review_request_v2(doc: dict, ex: dict) -> dict:
    """er119共通核(kind="grammar")へ渡す提示内容(v2): Top1/Top2(<=PREGEN_MAX=2)の文法名+解説全文(順位順)。exは検証済み(validate_explanations)の事前生成物。
    3位以降は n_not_generated として件数だけ示す(非表示・解説は生成していない)。AI推奨=rank1。"""
    cands = doc["candidates"]
    shown = cands[:PREGEN_MAX]
    by_ex = {it["candidate_id"]: it for it in ex.get("items") or []}
    exhausted = bool(doc.get("exhausted"))
    reselect_ok = doc.get("reselect_count", 0) < MAX_RESELECT
    if shown:
        choices = ["pick"] + (["reselect"] if reselect_ok else []) + ["omit"]
    elif exhausted:
        choices = ["omit"] + (["reextract"] if reselect_ok and doc.get("reextract_count", 0) < MAX_REEXTRACT else [])
    else:
        choices = ["omit"]
    return {"kind": "grammar", "schema": SCHEMA_REVIEW_V2, "candidates_sha256": doc["candidates_sha256"], "round": doc.get("round", 1), "exhausted": exhausted,
            "reselect_count": doc.get("reselect_count", 0), "reextract_count": doc.get("reextract_count", 0), "max_pick": GRAMMAR_MAX,
            "candidates": [{"candidate_id": c["candidate_id"], "rank": c["rank"], "tier": c["tier"], "feature_class": c["feature_class"], "para": c["para"],
                            "sentence": c["sentence"], "title": c["construct_ja"], "teaching_value_ja": c["teaching_value_ja"], "misread_ja": c["misread_ja"],
                            "explanation_md": by_ex[c["candidate_id"]]["explanation_md"], "explanation_sha256": by_ex[c["candidate_id"]]["explanation_sha256"]}
                           for c in shown if c["candidate_id"] in by_ex],
            "n_not_generated": max(0, len(cands) - len(shown)), "ai_recommended": shown[0]["candidate_id"] if shown else None,
            "choices": choices, "auto_default": "top1" if shown else (None if exhausted else "omit"), "reason_required_for": list(HUMAN_REASON_REQUIRED) + ["pick(TOP1のみ以外)"]}


def _grammar_selection_signature_v2(review: dict) -> str:
    sel = review.get("selection", {})
    payload = {"kind": "grammar", "schema": "v2", "level": review.get("level"), "text_sha256": review.get("text_sha256"),
               "candidates_sha256": review.get("candidates_sha256"), "status": review.get("status"),
               "selection": {"choice": sel.get("choice"), "candidate_ids": sorted(sel.get("candidate_ids") or []), "zero_reason": sel.get("zero_reason")},
               "verdicts": review.get("verdicts", {}), "mode_declaration": review.get("mode_declaration"),
               "ng": sorted(str(e.get("candidate_id")) for e in review.get("ng", []))}
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def finalize_review_record_v2(doc: dict, sel: dict, *, decision: dict | None = None, by: str = "", prior_history: list | None = None) -> dict:
    """確定record(grammar_human_review_v2。契約SCHEMA_CONTRACT_01 §2)。selection.candidate_idsは本文出現順(クリック順に依存しない)。
    decision.explanation_sha_by_id=提示した解説のid別sha(新候補の追加だけでは確定が古くならない)。formからの文法0件=omit(zero_reason=form_submission_no_grammar)。"""
    if sel["status"] not in ("SELECTED", "ZERO") or sel.get("review_status") not in ALLOWED_REVIEW_STATUSES:
        raise Part2ReviewError(f"確定できない状態です: {sel.get('status')}")
    src, d = sel["source"], dict(decision or {})
    selected = order_by_text(sel.get("selected") or [])
    ids = [c["candidate_id"] for c in selected]
    if sel["status"] == "SELECTED":
        choice, zero_reason = "pick", None
    else:
        choice = "none" if src == "no_candidate" else "omit"
        zero_reason = "form_submission_no_grammar" if (src == "human_omit" and d.get("channel") == "form") else src
    shown = [c["candidate_id"] for c in doc["candidates"][:PREGEN_MAX]]
    verdicts = {e["candidate_id"]: "NG" for e in doc.get("ng", []) if e.get("candidate_id")}
    if sel["review_status"] == "REVIEWED" and choice in ("pick", "omit"):
        verdicts.update({i: ("SELECTED" if i in ids else "NOT_SELECTED") for i in shown})
    elif sel["review_status"] == "UNREVIEWED_AUTO_ADOPTED":
        verdicts.update({i: None for i in shown})
    history = list(prior_history or [])
    for ev in doc.get("reselect_log", []):
        history.append({"at": ev["at"], "event": ev["event"], "by": ev.get("by", ""), "detail": {k: v for k, v in ev.items() if k not in ("at", "event", "by")}})
    history.append({"at": _now(), "event": "finalize", "by": by or d.get("by", ""),
                    "detail": {"source": src, "status": sel["review_status"], "choice": choice, "candidate_ids": ids, "reason": d.get("reason"), "channel": d.get("channel", "cli"),
                               "round": doc.get("round", 1), "candidates_sha256": doc["candidates_sha256"], "mode_declaration": sel.get("mode_declaration"),
                               "not_selected": [rejection_detail(doc, c) for c in doc["candidates"][:PREGEN_MAX] if choice == "pick" and c["candidate_id"] not in ids]}})
    dec = None
    if decision:
        dec = {"choice": d.get("choice"), "candidate_ids": list(d.get("candidate_ids") or []), "candidates_sha256": d.get("candidates_sha256"), "reason": d.get("reason"),
               "by": d.get("by"), "accept_ai": bool(d.get("accept_ai")), "explanation_sha_by_id": dict(d.get("explanation_sha_by_id") or {}), "channel": d.get("channel", "cli")}
    rec = {"schema": SCHEMA_REVIEW_V2, "kind": "grammar", "level": doc["level"], "text_sha256": doc["text_sha256"], "candidates_sha256": doc["candidates_sha256"],
           "status": sel["review_status"], "mode_declaration": sel.get("mode_declaration"),
           "selection": {"choice": choice, "candidate_ids": ids, "zero_reason": zero_reason},
           "accept_ai_default": bool(d.get("accept_ai")), "accepted_candidates_sha256": d.get("candidates_sha256") if d.get("accept_ai") else None,
           "verdicts": verdicts, "ng": list(doc.get("ng", [])), "reselect_count": doc.get("reselect_count", 0), "reextract_count": doc.get("reextract_count", 0),
           "decision": dec, "history": history}
    rec["selection_signature"] = grammar_selection_signature(rec)
    return rec


# ---- 結果 v2(items[]) の組立(LLM 0 call・決定論) -----------------------------------------------
def _item_selection(c: dict, source: str) -> dict:
    return {"source": source, "candidate_id": c["candidate_id"], "rank": c["rank"], "tier": c["tier"], "feature_class": c["feature_class"], "para": c["para"],
            "sentence": c["sentence"], "construct_ja": c["construct_ja"], "teaching_value_ja": c["teaching_value_ja"]}


def zero_result_v2(doc: dict, source: str) -> dict:
    return {"schema": SCHEMA_RESULT_V2, "level": doc["level"], "status": "ZERO", "zero_reason": source, "selection": {"source": source}, "items": [],
            "text_sha256": doc["text_sha256"], "extract_signature": doc["extract_signature"], "candidates_sha256": doc["candidates_sha256"],
            "round": doc.get("round", 1), "generated_at": _now()}


def _result_item_from_expl(c: dict, source: str, it: dict) -> dict:
    return {"selection": _item_selection(c, source), "translation_ja": it["translation_ja"], "translation_source": it["source"], "ref_ja": None,
            "explain_signature": it["explain_signature"], "explanation_md": it["explanation_md"], "sections": split_sections(it["explanation_md"]),
            "explanation_sha256": it["explanation_sha256"]}


def _result_item_from_frozen(c: dict, source: str, fz: dict) -> dict:
    token = "frozen:" + fz["frozen_sha256"][:16]
    md = fz["explanation_md"]
    return {"selection": _item_selection(c, source), "translation_ja": fz.get("translation_ja"), "translation_source": "frozen", "ref_ja": fz.get("ref_ja_at_freeze"),
            "explain_signature": token, "explanation_md": md, "sections": fz.get("sections") or split_sections(md.strip()), "explanation_sha256": explanation_sha256(md),
            "frozen": token, "frozen_source": fz.get("source")}


def build_result_v2(doc: dict, sel: dict, *, explanations: dict | None, frozen_items: list | None, shown_shas: dict | None = None) -> dict:
    """選定(本文出現順)の各候補について、凍結値 > 有効な事前生成物 の順で解説を引く。どちらも無ければ Part2Stale(fail-closed。その場でStep Bを呼ばない)。
    shown_shas(確定時にユーザーへ提示した解説のid別sha)があれば、事前生成物のshaが一致しない限りPart2Stale(確定=提示=公開の一致。確定後に解説が差し替わった場合を止める)。"""
    fz_by = {f.get("candidate_id"): f for f in frozen_items or []}
    ex_by = {it["candidate_id"]: it for it in (explanations or {}).get("items") or []}
    items, audits = [], {}
    for c in order_by_text(sel["selected"]):
        cid = c["candidate_id"]
        if cid in fz_by:
            items.append(_result_item_from_frozen(c, sel["source"], fz_by[cid]))
            audits[cid] = {"frozen": True, "source": fz_by[cid].get("source")}
        elif cid in ex_by and _expl_item_ok(ex_by[cid], c):
            if (shown_shas or {}).get(cid) not in (None, ex_by[cid]["explanation_sha256"]):
                raise Part2Stale(f"事前生成された解説({cid})が、ユーザーが確定時に見た解説と一致しません(確定後に差し替わった疑い)。fail-closed")
            items.append(_result_item_from_expl(c, sel["source"], ex_by[cid]))
            audits[cid] = ex_by[cid].get("audit") or {}
        else:
            raise Part2Stale(f"選定された文法({cid})の事前生成された解説(または凍結値)がありません。finalizeではStep Bを呼びません。解説の事前生成stageを実行してください")
    return {"schema": SCHEMA_RESULT_V2, "level": doc["level"], "status": "SELECTED", "zero_reason": None, "selection": {"source": sel["source"]}, "items": items,
            "text_sha256": doc["text_sha256"], "extract_signature": doc["extract_signature"], "candidates_sha256": doc["candidates_sha256"],
            "round": doc.get("round", 1), "audit": {"extract": doc.get("audit"), "explain": audits}, "generated_at": _now()}


def _same_result(a: dict | None, b: dict) -> bool:
    if not a:
        return False
    strip = lambda r: {k: v for k, v in r.items() if k not in ("generated_at", "reused_from_previous_run")}   # noqa: E731
    return strip(a) == strip(b)


def finalize_part2_v2(paragraphs: list, label: str, *, level: str, candidates_doc: dict, review: dict | None, mode="wait", explanations: dict | None = None,
                      cached_result: dict | None = None, frozen_items: list | None = None, prior_history: list | None = None, record_schema: str = SCHEMA_REVIEW_V2,
                      ng=()) -> dict:
    """確定済みの文法から結果(part2_grammar_v2)を**LLM 0 callで**組み立てる。Step A''もStep Bも呼ばない(LLM関数を引数に持たない)。
    record_schema=SCHEMA_REVIEW(v1)なら確定recordをv1式で再導出する(v1確定済みの進行中runの署名突合用。v1は単一選定のみ)。
    待機系はPart2PendingReview。返り値: {"status","candidates","result","selection","review_record"}。"""
    paragraphs = _check_paragraphs(paragraphs)
    doc = resolve_candidates(paragraphs, label, candidates_doc, level=level, ng=ng, allow_extract=False, frozen=bool(frozen_items))
    sel = select_from_candidates_v2(doc, review, mode)
    if sel["status"] in WAIT_STATUSES:
        raise Part2PendingReview(sel["status"], review_request(doc), doc)
    if record_schema == SCHEMA_REVIEW:
        if len(sel["selected"]) > 1:
            raise Part2Stale("v1の確定recordは単一選定のみです(複数選定はgrammar_human_review_v2)")
        rec = finalize_review_record(doc, dict(sel, candidate=(sel["selected"][0] if sel["selected"] else None)), decision=review, prior_history=prior_history)
    else:
        rec = finalize_review_record_v2(doc, sel, decision=review, prior_history=prior_history)
    if sel["status"] == "ZERO":
        res = zero_result_v2(doc, rec["selection"]["zero_reason"])   # 確定recordのzero_reason(form_submission_no_grammar等)と一致させる
    else:
        res = build_result_v2(doc, sel, explanations=explanations, frozen_items=frozen_items, shown_shas=(review or {}).get("explanation_sha_by_id"))
    if _same_result(cached_result, res):
        res = json.loads(json.dumps(cached_result))
        res["reused_from_previous_run"] = True
    else:
        res["reused_from_previous_run"] = False
    return {"status": sel["status"], "candidates": doc, "result": res, "selection": sel, "review_record": rec}


def result_items(result: dict | None) -> list:
    """結果のitem列(v2=items[]、v1=単一item、ZERO/None=[])。v1は書換えず正規化して読むだけ。"""
    if not result or result.get("status") != "SELECTED":
        return []
    if result.get("schema") == SCHEMA_RESULT_V2:
        return list(result.get("items") or [])
    return [{"selection": result["selection"], "translation_ja": result.get("translation_ja"), "translation_source": result.get("translation_source"),
             "ref_ja": result.get("ref_ja"), "explain_signature": result.get("explain_signature"), "explanation_md": result.get("explanation_md"),
             "sections": result.get("sections") or {}, "frozen": result.get("frozen")}]


def translation_issues(result: dict | None, ref_ja_pool: dict | None, acks: dict | None = None) -> list:
    """Opus O-1: Part 1訳(参考訳pool)と、選定文の【日本語訳】(事前生成=ref_ja無しのStep B自身の訳)が食い違うitem(凍結の有無に関係なく検査)。
    pool無し/選定文がPart 1引用文と一致しない/訳が一致 -> 問題なし。ユーザー了承(acks: candidate_id -> [{step_b_ja_sha256, part1_ja_sha256}])があれば除外。
    戻り値: [{"candidate_id","sentence","step_b_ja","part1_ja"}]"""
    out = []
    if not ref_ja_pool:
        return out
    for it in result_items(result):
        s = it["selection"]
        pv = lookup_ref_ja(s["sentence"], ref_ja_pool)
        if not pv or pv in {it.get("translation_ja"), it.get("ref_ja")}:
            continue
        sb = hashlib.sha256(str(it.get("translation_ja")).encode("utf-8")).hexdigest()
        p1 = hashlib.sha256(pv.encode("utf-8")).hexdigest()
        if any(a.get("step_b_ja_sha256") == sb and a.get("part1_ja_sha256") == p1 for a in (acks or {}).get(s["candidate_id"], [])):
            continue
        out.append({"candidate_id": s["candidate_id"], "sentence": s["sentence"], "step_b_ja": it.get("translation_ja"), "part1_ja": pv})
    return out


def _expected_outcome_v2(doc: dict, review: dict, where: str, nxt: str):
    """('SELECTED', [cand...本文出現順], source) | ('ZERO', [], zero_reason)。review schema v1は既存の_expected_outcomeへ委譲(単件)。不整合はPart2Stale。"""
    if review.get("schema") == SCHEMA_REVIEW:
        kind, cand, source = _expected_outcome(doc, review, where, nxt)
        return kind, ([cand] if cand else []), source
    w = f"[{where}] " if where else ""

    def stale(msg):
        return Part2Stale(f"{w}{msg}。次の一手: {nxt}")
    st, sel = review.get("status"), review.get("selection") or {}
    cands = doc.get("candidates", [])
    ch, ids = sel.get("choice"), list(sel.get("candidate_ids") or [])
    if st == "NO_CANDIDATE_UNREVIEWED":
        if cands or doc.get("filtered_by_ng") or ch != "none" or ids or sel.get("zero_reason") != "no_candidate":
            raise stale("Part 2の確定(NO_CANDIDATE_UNREVIEWED)が候補docと一致しません")
        return "ZERO", [], "no_candidate"
    if st == "UNREVIEWED_AUTO_ADOPTED":
        try:
            if normalize_mode(review.get("mode_declaration"))[0] != "auto":
                raise Part2ReviewError("宣言なし")
        except Part2ReviewError as e:
            raise stale(f"Part 2の自動採用にer119の明示auto宣言がありません({e})")
        if not cands or ch != "pick" or ids != [cands[0]["candidate_id"]]:
            raise stale("Part 2の自動採用(auto_top1)が現在の候補docのTOP1(1件のみ)と一致しません")
        return "SELECTED", [cands[0]], "auto_top1"
    if st == "REVIEWED":
        if ch == "pick":
            shown = {c["candidate_id"]: c for c in cands[:PREGEN_MAX]}
            if not ids or len(ids) > GRAMMAR_MAX or len(set(ids)) != len(ids) or any(i not in shown for i in ids):
                raise stale("Part 2のHuman確定(pick)が現在の候補docと一致しません")
            ordered = order_by_text([shown[i] for i in ids])
            if [c["candidate_id"] for c in ordered] != ids:
                raise stale("Part 2のHuman確定(pick)のcandidate_idsが本文出現順に正規化されていません")
            dch = (review.get("decision") or {}).get("choice")
            return "SELECTED", ordered, ("human_" + dch if dch in ("top1", "top2") else "human_pick")
        if ch == "omit":
            zr = sel.get("zero_reason")
            if (zr in ("human_omit", "form_submission_no_grammar") and cands and not ids) or (zr == "human_rejected_all" and not cands and doc.get("exhausted") and not ids):
                return "ZERO", [], zr
            raise stale("Part 2のHuman省略(omit)が現在の候補docと一致しません")
    raise stale(f"Part 2の確定statusが不正または前進不可です: {st}/{ch}")


def _require_fresh_part2_v2(result: dict | None, paragraphs: list, label: str, *, next_command: str, where: str, candidates_doc: dict | None,
                            grammar_review: dict | None, frozen: list | None, explanations: dict | None) -> None:
    w = f"[{where}] " if where else ""
    nxt = next_command
    frz = {f.get("candidate_id"): f for f in frozen or []}
    paragraphs = _check_paragraphs(paragraphs)
    if result.get("text_sha256") != text_sha256(paragraphs) or (not frz and result.get("extract_signature") != extract_signature(paragraphs, label)):
        raise Part2Stale(f"{w}Part 2が現在の本文・Prompt・modelと一致しません(古い)。次の一手: {nxt}")
    if not candidates_doc or candidates_doc.get("schema") != SCHEMA_CANDIDATES:
        raise Part2Stale(f"{w}Part 2の候補docがありません。次の一手: {nxt}")
    if candidates_doc.get("text_sha256") != text_sha256(paragraphs) or (not frz and candidates_doc.get("extract_signature") != extract_signature(paragraphs, label)) \
            or candidates_doc.get("candidates_sha256") != candidates_sha256(candidates_doc.get("candidates", [])):
        raise Part2Stale(f"{w}Part 2の候補docが現在の本文と一致、または自己整合していません。次の一手: {nxt}")
    if result.get("level") != candidates_doc.get("level"):
        raise Part2Stale(f"{w}Part 2の結果のlevel({result.get('level')})が候補doc({candidates_doc.get('level')})と一致しません(別levelの成果物)。次の一手: {nxt}")
    if not grammar_review or grammar_review.get("schema") not in (SCHEMA_REVIEW, SCHEMA_REVIEW_V2) or grammar_review.get("kind") != "grammar":
        raise Part2Stale(f"{w}Part 2のHuman確定recordがありません。次の一手: {nxt}")
    if grammar_review.get("level") != candidates_doc.get("level"):
        raise Part2Stale(f"{w}Part 2の確定recordのlevelが候補docと一致しません。次の一手: {nxt}")
    if grammar_review.get("status") not in ALLOWED_REVIEW_STATUSES:
        raise Part2Stale(f"{w}Part 2の確定statusが前進不可です: {grammar_review.get('status')}(判断待ち・再選定中・stale)。次の一手: {nxt}")
    if grammar_review.get("candidates_sha256") != candidates_doc["candidates_sha256"] or grammar_review.get("text_sha256") != candidates_doc["text_sha256"]:
        raise Part2Stale(f"{w}Part 2の確定が現在の候補docに対するものではありません。次の一手: {nxt}")
    if grammar_review.get("selection_signature") != grammar_selection_signature(grammar_review):
        raise Part2Stale(f"{w}Part 2の確定のselection_signatureが一致しません(手編集の疑い)。次の一手: {nxt}")
    kind, cands, source = _expected_outcome_v2(candidates_doc, grammar_review, where, nxt)
    if result.get("candidates_sha256") != candidates_doc["candidates_sha256"]:
        raise Part2Stale(f"{w}Part 2の結果が現在の候補docから作られたものではありません(再選定・再抽出後の古い結果)。次の一手: {nxt}")
    if kind == "ZERO":
        if result.get("status") != "ZERO" or result.get("zero_reason") != source or result.get("items"):
            raise Part2Stale(f"{w}Part 2の結果が確定(省略/適格なし: {source})と一致しません。次の一手: {nxt}")
        return
    if result.get("status") != "SELECTED":
        raise Part2Stale(f"{w}Part 2のstatusが確定(選定)と一致しません: {result.get('status')}。次の一手: {nxt}")
    items = result.get("items") or []
    if len(items) > GRAMMAR_MAX:
        raise Part2Stale(f"{w}Part 2の結果の文法が{len(items)}件です(文法選定仕様 2026-10-27: 最大{GRAMMAR_MAX}件。旧2件結果は再選定が必要)。次の一手: {nxt}")
    if len(items) != len(cands):
        raise Part2Stale(f"{w}Part 2の結果の件数({len(items)})が確定({len(cands)}件)と一致しません。次の一手: {nxt}")
    shas = (grammar_review.get("decision") or {}).get("explanation_sha_by_id") or {}
    ex_by = {it["candidate_id"]: it for it in (explanations or {}).get("items") or []}
    for it, cand in zip(items, cands):
        sel = it.get("selection") or {}
        if sel.get("candidate_id") != cand["candidate_id"] or sel.get("source") != source or sel.get("para") != cand["para"] or sel.get("sentence") != cand["sentence"]:
            raise Part2Stale(f"{w}Part 2の結果の選定が確定した候補({source})と一致しません。次の一手: {nxt}")
        if not verify_single_span({"body": paragraphs}, sel.get("para"), sel.get("sentence")):
            raise Part2Stale(f"{w}Part 2の選定文が本文の単一段落の逐語spanではありません。次の一手: {nxt}")
        if candidate_id(sel["para"], sel["sentence"]) != sel["candidate_id"]:
            raise Part2Stale(f"{w}Part 2の候補IDが不整合です。次の一手: {nxt}")
        secs = it.get("sections") or {}
        md = it.get("explanation_md") or ""
        if not md or not secs or not secs.get("日本語訳") or it.get("translation_ja") != secs.get("日本語訳") or it.get("explanation_sha256") != explanation_sha256(md):
            raise Part2Stale(f"{w}Part 2の解説または訳(Step Bの【日本語訳】)が欠落・不整合です。次の一手: {nxt}")
        fz = frz.get(cand["candidate_id"])
        if fz is not None:   # 凍結値: signatureの代わりに frozen:<sha> と凍結した解説全文・訳との一致で判定(Prompt/model変更で失効しない)
            if frozen_sha_of(cand["candidate_id"], cand["sentence"], md, it.get("translation_ja")) != fz.get("frozen_sha256"):
                raise Part2Stale(f"{w}Part 2の解説が凍結した確定解説(frozen:{str(fz.get('frozen_sha256'))[:16]})と一致しません。次の一手: {nxt}")
        else:
            if it.get("explain_signature") != explain_signature(cand, None) or it.get("ref_ja") is not None:
                raise Part2Stale(f"{w}Part 2の解説signatureが候補docの材料欄から再計算した値と一致しません。次の一手: {nxt}")
            if explanations is not None and (cand["candidate_id"] not in ex_by or ex_by[cand["candidate_id"]]["explanation_sha256"] != it["explanation_sha256"]):
                raise Part2Stale(f"{w}Part 2の解説が事前生成物と一致しません。次の一手: {nxt}")
        shown_sha = shas.get(cand["candidate_id"])
        if fz is None and shown_sha is not None and shown_sha != it["explanation_sha256"]:   # 凍結値は frozen:<sha> が正(上)。凍結なしは確定時に見た解説のshaと一致すること
            raise Part2Stale(f"{w}Part 2の解説が、ユーザーが確定時に見た解説(sha {shown_sha[:12]})と一致しません(確定内容の書換え防止)。次の一手: {nxt}")
        if PAGE_FORBIDDEN_RE.search(md):
            raise Part2Stale(f"{w}Part 2の解説にページ非表示語が含まれます。次の一手: {nxt}")


def count_grammar_blocks(html_text: str) -> int:
    """HTML(または節)内のPart 2文法ブロック(`<h3>Grammar &amp; Sentence Structure</h3>`を持つstudy section)の数。節単位4者一致検査(O-6)用。"""
    return html_text.count("<h3>Grammar &amp; Sentence Structure</h3>")


def write_explanations(dir_path: str, ex: dict) -> str:
    """grammar_explanations.json を原子的に保存(tmp+os.replace。途中失敗でも成功分を保持)。"""
    os.makedirs(dir_path, exist_ok=True)
    path = f"{dir_path}/{EXPLANATIONS_FILENAME}"
    tmp = f"{path}.tmp{os.getpid()}"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(ex, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)
    return path


def load_explanations(dir_path: str) -> dict | None:
    return load_json(f"{dir_path}/{EXPLANATIONS_FILENAME}")
