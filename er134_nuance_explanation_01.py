# ============================================================
# er134_nuance_explanation_01.py
# NUANCE-EXPLANATION-PRODUCTION-WIRING-01 委任_02A (Track B、2026-10-29)
# ニュアンス解説(記事・レベルごと最大1件)の生成・主題重複判定 共通module(Family X/Y/Z共通)
# ============================================================
# 承認: ユーザー原文 docs/pm/delegation_log/2026-10-29_NUANCE-EXPLANATION-PRODUCTION-WIRING-01_USER.md §2(APPROVED_FOR_PRODUCTION)。
# 設計: docs/research/NUANCE-EXPLANATION-PRODUCTION-WIRING-01/WIRING_DESIGN_01.md(§3 schema・§4・§5)+ OPUS_REVIEW_01.md(M-1〜M-10・R-1〜R-16、
#       Fable判断で全件採用)。Prompt v3の再検証 = PROMPT_V3_VERIFY_01.md。
#
# 範囲(Track B): 入力組立・候補生成(Prompt v3)・段1構造判定(決定論)・段2重複判定(別Prompt・id単位の全件)・verdictの決定論算出・
#                 focus_terms導出・引用検査・N0 spec・N1 orchestrator(候補doc保存/resume)。
#                 表示・HR・フォーム・確定(N2/N3)・runner配線は本moduleに無い(Track A/02B)。
#
# 安全:
#  - LLM呼出は routing.require_model 経由(gpt-6-luna=SUPPORT_MODEL)。応答modelが違えばretry/fallbackせずSTOP(NuanceModelContractError)。
#  - 技術失敗(API障害・JSON不正・引用不一致・判定不能)は status=FAILED_TECHNICAL(本物の0件=NO_CANDIDATEと区別)。非ブロッキング(例外にしない)。
#  - model契約違反・budget_guard例外・KeyboardInterruptは握りつぶさず伝播(STOP)。
#  - Family A/B/Cからimportされない。DEV/Trial資産(docs/research配下)をimportしない(Prompt定数は本module内、sha固定)。
#  - 未承認機能(Part 4・複数件・自動補充)は存在しない(候補は単数、再生成・次点繰上げの関数なし)。
# ============================================================
from __future__ import annotations

import hashlib
import json
import os
import re
import time
import unicodedata

import er006_model_routing_contract_01 as routing
import er119_kp_human_review_01 as rv
import er120_part2_grammar_production_01 as g

MANAGEMENT_ID = "NUANCE-EXPLANATION-PRODUCTION-WIRING-01"
PROCESS_GEN = "NUANCE_EXPLANATION"
PROCESS_JUDGE = "NUANCE_OVERLAP_JUDGE"
MODEL = routing.SUPPORT_MODEL
SCHEMA = "nuance_candidate_v1"
SPEC_SCHEMA = "nuance_spec_v1"
SPEC_FILENAME = "nuance_spec.json"
CANDIDATE_FILENAME = "nuance_candidate.json"
FAILED_FILENAME = "nuance_failed.json"
SECTION_HEADING_JA = "ニュアンス解説"      # 見出し(Fable判断R-12: 「Deeper Understanding」を使わない)
LEVELS = g.LEVELS                         # {"b1b": "Advanced", "a2": "Standard"}
DEFAULT_CAP = 12                          # exporter(export_form_data_01.DEFAULT_CAP)と同じ提示pool上限
DEFAULT_CAP_BY_KIND = {"phrase": 7, "word": 5}
GRAMMAR_PRESENT_MAX = 2
GEN_MAX_OUTPUT_TOKENS = 9000
JUDGE_MAX_OUTPUT_TOKENS = 5000
EXPLANATION_MIN_CHARS = 60
EXPLANATION_MAX_CHARS = 700

# status
ST_NO_CANDIDATE = "NO_CANDIDATE"
ST_CANDIDATE = "CANDIDATE"
ST_FAILED_TECHNICAL = "FAILED_TECHNICAL"
ST_LEGACY = "LEGACY"
# no_candidate_reason
R_MODEL_NONE = "model_returned_none"
R_SELF_RATING = "self_rating_not_high"
R_OVERLAP_NG = "overlap_ng"
R_AUTO_ADOPTED = "auto_adopted_no_human_review"
# failed_technical kind
F_API = "api_error"
F_GEN_INVALID = "gen_json_invalid"
F_QUOTE = "quote_mismatch"
F_OVERLAP_UNVERIFIED = "overlap_unverified"


class NuanceError(Exception):
    pass


class NuanceModelContractError(NuanceError):
    """応答modelが契約と違う。retryもfallbackもせずSTOP(ER-006-MODEL-ROUTING-CONTRACT-01)。"""


class NuanceInputError(NuanceError):
    pass


# ============================================================
# Prompt v3 (生成)。v2(PROMPT_TRIAL_01.md §2-2)からの差分:
#  - 入力形 = 暫定選定 + その他の提示pool(最大12件) + 文法Top2(提示中)  (M-8)
#  - 文言を「選定済み」から「暫定選定/提示候補」へ。重複回避の対象に文法候補も含める  (F-3)
#  - レベル適合: 「A2基礎文法の対比は不可」を「文法コーナーの領域は扱わない。語用的な含みはStdでも可」へ  (R-9)
#  - 引用: 本文の連続した1〜2文の逐語  (M-9)
# focus_termsはPromptに入れない(expressionから決定論で導出、M-8)。
# ============================================================
PROMPT_GEN = """あなたは英語学習コンテンツの編集者です。下の英語ポッドキャスト台本を読んだ学習者向けに、「ニュアンス解説」を日本語で最大1件だけ作ってください。学習価値のある候補がなければ0件にしてください(0件は正常な結果です)。

# 記事・レベル
- 記事: {title}
- レベル: {level_note}

# 本文(引用では段落番号を付けない)
{body}

# Key Phrase・Word(別コーナーで解説する表現)
## 暫定選定({n_prov}件。このまま採用される可能性が最も高い)
{prov_block}
{pool_section}{grammar_section}
# ニュアンス解説とは
英語表現の微妙な意味の違い、語感、文脈による意味や印象の違いなど、日本語話者が辞書の訳語だけでは気づきにくい差を扱う解説です。扱える焦点の例:
(a) 近い表現との使い分け(強さ・丁寧さ・硬さ・肯定的/否定的な含み)
(b) 同じ語・構文でも文脈で意味や印象が変わる点
(c) 語の選択・助動詞・副詞などで変わる、話し手の態度や確信度の違い
(d) 日本語の訳語に引きずられると誤解しやすい点

# 他のコーナーとの役割分担
- Key Phrase・Wordのコーナー: 上のKey Phrase・Word(暫定選定とその他の提示候補)の意味・よく使う組み合わせ・近い表現との違いを扱う。ニュアンス解説は、これらの表現の語義補足や類義語比較をしてはならない。
- 文法・文構造のコーナー: 文型・時制・仮定法・語順・助動詞の用法などの「仕組み」を扱う(上の文法コーナーの候補が、人間の選択によって載る可能性がある)。ニュアンス解説は、文の仕組みの説明ではなく、語や表現の選択による含み・印象の差を扱う。

# 最重要条件: 上のKey Phrase・Word、文法コーナーの候補と重複しないこと
- 解説の「中心的な学習対象・論点(焦点)」が、上のKey Phrase・Word(暫定選定・その他の提示候補の全件)や文法コーナーの候補のどれとも実質的に同じであってはならない。
- 表現の文字列が違っても、実質的に同じ内容を教えるなら重複とみなす(例: あるKey Phraseの類義語との違いを説明する、同じ語の別の用法を説明する、文法候補と同じ仕組みを語感の話に言い換える)。
- 解説文の中にそれらの表現が一言登場するだけなら問題ない。ただし主役にしない。
- 入れ替えテスト: その解説をKey Phrase・Wordや文法のコーナーに入れても違和感がないなら、重複とみなして外す。

# 学習価値の4条件(すべて明確に満たす候補だけを選ぶ。1つでも弱ければ0件)
1. 文脈性: 本文のこの場面で、その表現が選ばれていることによる含み・印象を具体的に説明できる。
2. 日本語話者の落とし穴: 日本語の訳語や既知の知識のままだと、取り違え・不自然な使い分けが実際に起こりやすい(例: 訳語が数量を連想させ、範囲を限定する含みを見落とす語、助言と誤読しやすい慣用的な誇張表現、因果と取り違えやすい関連の表現)。
3. レベル適合: このレベルの学習者にとって未習か混同しやすい差である。辞書・入門書で十分な基礎語の説明は不可。機能語(副詞・前置詞・助動詞など)や頻出表現が持つ語用的な含み(誇張・婉曲・確信度・範囲の限定など)は、StandardでもAdvancedでも対象にしてよい。助動詞や構文を含む表現でも、焦点が文の仕組みではなく語用的な含みなら対象にしてよい。
4. 非重複: 上の役割分担と重複条件に反しない。

# 選ばないもの(該当する候補しかなければ0件にする)
- 品詞・語形・基礎語の文法的な違いの説明
- A1〜A2の基礎語どうしの使い分け(例: always と often、big と large のように、辞書の訳語の違いで足りるもの)
- 文法・文構造のコーナーの領域(文型・時制・仮定法・語順などの仕組みの説明が中心になるもの)
- 物語や記事内容の感想・解釈・テーマ論(登場人物の心理の読み取りが中心になるもの)
- 辞書を引けば足りる語義の説明、よくある組み合わせの紹介
- 本文に根拠がない一般論、学習者のレベルに見合わない細かすぎる差
- 無理に1件にするための選定。迷うなら0件にする。

# 手順(内部で考え、出力は最後のJSONのみ)
1. 本文から上の焦点に当てはまる候補を最大4つ挙げ、それぞれの焦点を1行で書く。
2. 各候補を、Key Phrase・Word全件および文法コーナー候補との照合と入れ替えテストで確かめ、重複するものを外す。
3. 残った候補を学習価値の4条件で確かめる。4条件をすべて明確に満たす候補が1件以上あれば最も価値の高い1件を選ぶ。なければ0件にする。

# 出力(JSONのみ。前置き・コードフェンスなし。日本語は読みやすく)
{{
  "rejected_candidates": [{{"expression": "外した候補の英語表現", "focus": "焦点を日本語1行", "reason": "kp_word_overlap または grammar_overlap または low_value または not_nuance または too_basic または grammar_structure または other", "note": "理由を一言"}}],
  "candidate": null または {{
    "expression": "解説の中心的な学習対象の英語表現。比較なら 'A vs B'",
    "focus": "学習上の焦点を日本語1行(40字程度まで)",
    "quote_en": "本文から一字一句そのまま引用した、連続する1〜2文(改変・要約・つなぎ合わせ・段落またぎ禁止)",
    "quote_ja": "quote_enの日本語訳",
    "explanation_ja": "日本語の解説。120〜260字。比較する表現・場面を最低1つ具体的に示し、何がどう違うか(語感・印象・使い分け)を書く。Key Phrase・Wordの解説の繰り返しにしない",
    "differs_from_kp_word_ja": "Key Phrase・Word・文法候補のどれとも焦点が異なる理由を1文",
    "criteria_check": {{"context_specific": "本文の場面での含みを1文", "jp_pitfall": "日本語話者が取り違えやすい点を1文", "level_fit": "このレベルで価値がある理由を1文"}},
    "learning_value_self_rating": "high または mid(4条件がすべて明確ならhigh。1つでも弱いならmidとし、midの場合は候補にせず0件にする)",
    "learning_value_reason_ja": "なぜこのレベルの学習者に価値があるかを1文"
  }},
  "no_candidate_reason_ja": "candidateがnullのときだけ理由を1〜2文。候補ありならnull"
}}

# 制約
- quote_enは本文に実在する文字列のみ。本文にない表現・事実・登場人物の言動を作らない。
- 解説の事実(語義・用法)は一般に認められた英語の用法に基づき、断定しすぎない。
- 理解度チェック・クイズ・感想は書かない。
"""

# ============================================================
# 判定Prompt(生成とは別call・別Prompt。生成側のdiffers_from_kp_word_ja/criteria_checkは渡さない=R-8)。
# 出力は圧縮形(R-10): items[{id,same,why(trueのみ)}] + closest。verdictはLLMに書かせず、items全件から決定論で算出する(M-4)。
# ============================================================
PROMPT_JUDGE = """あなたは英語学習コンテンツの重複検査員です。下の「ニュアンス解説の候補」が、「比較対象」のどれかと学習上の焦点で重複していないかを、項目ごとに判定してください。

# 判定基準(ユーザー承認済みの規則)
- 単語の文字列一致ではなく、解説の学習上の焦点で判定する。
- 候補の解説文中に比較対象の表現が登場すること自体は問題ない(焦点が別なら same=false)。
- 候補の中心的な学習対象・論点が、その項目と同じなら same=true(重複)。
- 表現が違っても、実質的に同じ内容(同じ語義・用法・使い分け・語の組み合わせ・近い表現との違い)を教えるなら same=true。
- 入れ替えテスト: 候補の解説を、その項目のコーナーに入れても違和感がないなら same=true。
- 比較対象の種類: K=Key Phrase・Word(語義・用法・コロケーション・近い表現との違いを解説するコーナー)。G=文法・文構造(文型・時制・仮定法・語順などの仕組みを例文つきで解説するコーナー)。
- 「構造ヒント」は参考情報。語を共有していても、焦点が別なら same=false。

# ニュアンス解説の候補
- 表現: {expression}
- 焦点: {focus}
- 本文引用: {quote_en}
- 解説: {explanation_ja}

# 比較対象({n_items}件)
{items_block}

# 出力(JSONのみ。前置き・コードフェンスなし)
{{"items": [{{"id": "K1", "same": false}}, {{"id": "K2", "same": true, "why": "何が同じ焦点か(日本語1文)"}}],
 "closest": {{"id": "最も焦点が近い項目のid", "why": "なぜ近いか、それでも別焦点か(日本語1文)"}}}}
- itemsは上の比較対象の全件を、同じidで1回ずつ列挙する(省略・重複は不可)。
- sameがtrueの項目にだけ"why"を付ける。falseの項目には付けない。
- closestは、全件がfalseの場合でも必ず書く(最も焦点が近い項目を明示する)。
"""

PROMPT_GEN_SHA256 = hashlib.sha256(PROMPT_GEN.encode("utf-8")).hexdigest()
PROMPT_JUDGE_SHA256 = hashlib.sha256(PROMPT_JUDGE.encode("utf-8")).hexdigest()

LEVEL_NOTE = {
    "a2": "Standard(CEFR A2を目標に書かれた英文。学習者はA2〜B1相当の日本語話者)",
    "b1b": "Advanced(CEFR B1を目標に書かれた英文。学習者はB1〜B2相当の日本語話者)",
}


# ============================================================
# 共通ユーティリティ
# ============================================================
def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def jsha(obj) -> str:
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def _qn(x: str) -> str:
    """曲がった引用符/アポストロフィ -> 直線(長さ保存)。文法(er120 `_qn`)と同規則。parityはtestで固定。"""
    return x.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')


_SENT_RE = re.compile(r".+?[.!?…]+[”\"’']?(?=\s|$)|.+?$", re.S)   # er120 `_SENT_RE`と同じ


def _sents(t: str) -> list:
    return [x.strip() for x in _SENT_RE.findall(t) if x.strip()]


def _write_json_atomic(path: str, obj) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = f"{path}.tmp{os.getpid()}"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def _read_json(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _check_level(level) -> str:
    if level not in LEVELS:
        raise NuanceInputError(f"levelは {sorted(LEVELS)} のいずれかを必ず指定してください(既定値なし): {level!r}")
    return level


def parse_json_object(txt: str):
    """応答テキストから最外のJSONオブジェクトを取り出す。失敗=ValueError。"""
    if not isinstance(txt, str) or "{" not in txt:
        raise ValueError("JSONオブジェクトがありません")
    a, b = txt.find("{"), txt.rfind("}")
    if b <= a:
        raise ValueError("JSONオブジェクトの終端がありません")
    try:
        j = json.loads(txt[a:b + 1])
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON不正: {e}") from e
    if not isinstance(j, dict):
        raise ValueError("JSONオブジェクトではありません")
    return j


# ============================================================
# 入力組立 (build_inputs) — M-4/M-8
# ============================================================
def kind_of(c: dict) -> str:
    """exporter(export_form_data_01.kind_of)と同規則。"""
    k = c.get("kind")
    if k in ("phrase", "word"):
        return k
    return "word" if len((c.get("used_form") or "").split()) == 1 else "phrase"


def _cap_info(doc: dict) -> tuple:
    sd = doc.get("shortfall_detail") or {}
    cap = sd.get("cap")
    cbk = sd.get("cap_by_kind")
    return (cap or DEFAULT_CAP), (dict(cbk) if cbk else dict(DEFAULT_CAP_BY_KIND))


def presented_pool(kp_cands: dict) -> list:
    """フォームに提示されるKey Phrase・Word候補(HRで人間が選べる集合)。exporter(`export_form_data_01.convert`)と同じ算出:
    ai_rank順に並べ、phrases[:cap_by_kind.phrase] + words[:cap_by_kind.word]。parityは実exporterと突合するtestで固定(M-4)。
    戻り値: ai_rank順のcandidate dict(元docのdictそのもの)。"""
    # 仕様①(2026-10-29): 提示集合は rv.presentable_candidates(品質検査を通った候補のみ)を通してから種類別capを適用する(exporterと同一。Opus M2)
    cands = sorted(rv.presentable_candidates(kp_cands or {}), key=lambda c: c.get("ai_rank") or 99)
    _, cbk = _cap_info(kp_cands or {})
    phrases = [c for c in cands if kind_of(c) == "phrase"][:cbk.get("phrase", 7)]
    words = [c for c in cands if kind_of(c) == "word"][:cbk.get("word", 5)]
    keep = {id(c) for c in phrases} | {id(c) for c in words}
    return [c for c in cands if id(c) in keep]


def _variants(c: dict) -> list:
    it = c.get("item") or {}
    out = []
    for v in (c.get("used_form"), it.get("display_phrase"), it.get("key_phrase"), c.get("selection_phrase")):
        if v and v not in out:
            out.append(v)
    return out


def _pool_entry(c: dict, provisional: bool) -> dict:
    it = c.get("item") or {}
    return {"id": c["candidate_id"], "kind": kind_of(c), "used_form": c.get("used_form") or c.get("selection_phrase") or "",
            "display_phrase": it.get("display_phrase") or c.get("selection_phrase") or "", "key_phrase": it.get("key_phrase") or c.get("used_form") or "",
            "gloss": c.get("japanese_gloss") or "", "variants": _variants(c), "provisional": bool(provisional), "ai_rank": c.get("ai_rank")}


def pool_identity_sha(pool: list) -> str:
    """HR確定後・候補再利用の判定キー(M-3): candidate_id+used_form/display_phrase/key_phrase+kind。gloss/gate等は含めない。"""
    return jsha(sorted([e["id"], e["used_form"], e["display_phrase"], e["key_phrase"], e["kind"]] for e in pool))


def _grammar_entry(it: dict, k: int) -> dict:
    gid = it.get("id") or it.get("candidate_id")
    return {"id": gid, "rank": it.get("rank", k + 1), "title": it.get("title") or it.get("construct_ja") or "", "example": it.get("example") or it.get("sentence") or ""}


def build_inputs(*, family: str, article_id: str, title: str, level: str, paragraphs: list, kp_cands: dict, grammar_items: list | None = None,
                 provisional_ids: list | None = None, std_part1: bool = True, ng_entries: list | None = None) -> dict:
    """Production形の入力(暫定選定 + 提示pool最大12件 + 文法Top2[提示中])を組み立てる。API 0・決定論。
    provisional_ids未指定=rv.auto_select(AI推奨のvocab最大5件。KPは先頭3件を含む)。std_part1=True(新表示仕様の記事=Stdもvocab有効)。"""
    _check_level(level)
    if not isinstance(paragraphs, (list, tuple)) or not paragraphs or not all(isinstance(p, str) and p.strip() for p in paragraphs):
        raise NuanceInputError("paragraphsは非空文字列のlistである必要があります")
    if not isinstance(title, str) or not title.strip() or "\n" in title:
        raise NuanceInputError("titleは1行の非空文字列")
    kp_cands = kp_cands or {}
    pool_c = presented_pool(kp_cands)
    pool_ids_all = {c["candidate_id"] for c in pool_c}
    if provisional_ids is None:
        sel = rv.auto_select(kp_cands, level=level, kind=rv.KIND_KP, ng_entries=ng_entries or [], std_part1=std_part1)
        provisional_ids = list(sel.get("vocab") or []) or list(sel.get("kp") or [])
    # 暫定選定のうち提示pool外のidは不整合として入力エラー(推測で補わない)
    unknown = [x for x in provisional_ids if x not in pool_ids_all]
    if unknown:
        raise NuanceInputError(f"暫定選定idが提示poolにありません: {unknown}")
    prov = set(provisional_ids)
    pool = [_pool_entry(c, c["candidate_id"] in prov) for c in pool_c]
    provisional = [e for e in pool if e["provisional"]]
    gsorted = sorted(grammar_items or [], key=lambda x: (x.get("rank") is None, x.get("rank") or 0))[:GRAMMAR_PRESENT_MAX]
    grammar = [_grammar_entry(it, k) for k, it in enumerate(gsorted)]
    body = "\n\n".join(paragraphs)
    return {
        "family": family, "article_id": article_id, "title": title.strip(), "level": level, "level_name": LEVELS[level],
        "paragraphs": list(paragraphs), "body": body, "text_sha256": g.text_sha256(list(paragraphs)),
        "pool": pool, "provisional": provisional, "provisional_ids": [e["id"] for e in provisional], "grammar": grammar,
        "pool_identity_sha": pool_identity_sha(pool), "grammar_identity_sha": jsha(sorted([x["id"], x["title"], x["example"]] for x in grammar)),
        "candidates_sha256": (kp_cands.get("candidates_sha256") or (rv.candidates_sha256(kp_cands) if kp_cands.get("candidates") else None)),
    }


# ============================================================
# focus_terms導出 / 正規化 (derive_focus_terms) — M-8: Promptに入れず、expressionから決定論で導出
# ============================================================
_SPLIT_RE = re.compile(r"\s+vs\.?\s+|\s+versus\s+|\s*↔\s*|\s+/\s+", re.I)
_EDGE_RE = re.compile(r"^[\s'\"“”‘’`(\[]+|[\s'\"“”‘’`)\].,;:!?…]+$")


def derive_focus_terms(expression: str) -> list:
    """expression('A vs B'形を含む)から英語の主表現を決定論で導出する。重複除去・順序保存。LLMに追加出力させない。"""
    s = unicodedata.normalize("NFKC", expression or "")
    s = s.replace("...", " ").replace("…", " ")
    parts = [p for p in _SPLIT_RE.split(s) if p]
    out = []
    for p in parts:
        t = _EDGE_RE.sub("", p.strip())
        t = re.sub(r"\s+", " ", t).strip()
        if t and t.lower() not in [x.lower() for x in out]:
            out.append(t)
    return out


_STOP = set("a an the to of in on at for with from by and or one's ones someone's somebody's anyone people person be is are was were been being it its this that i you he she we they me my your his her their our not no do does did".split())
_SLOT = {"someone", "somebody", "something", "anyone", "anything", "one", "ones", "<poss>"}
_POSS_RE = re.compile(r"\b(one's|someone's|somebody's|your|his|her|their|my|our|its)\b")


def _stem(w: str) -> str:
    """簡易の屈折正規化(make/makes/making、help/helped、stop/stopped、link/linked を同じ語幹に)。完全な語幹化は目指さない(不規則形は句の別形[display_phrase等]との照合で補う)。"""
    base, stripped = w, False
    for suf in ("ing", "ed", "es", "s"):
        if len(w) > len(suf) + 2 and w.endswith(suf):
            base, stripped = w[:-len(suf)], True
            break
    if stripped and len(base) > 3 and base[-1] == base[-2] and base[-1] not in "lsz":
        base = base[:-1]
    if base.endswith("e") and len(base) > 3:
        base = base[:-1]
    return base


def _tok_pairs(s: str) -> list:
    s = unicodedata.normalize("NFKC", s or "")
    s = _qn(s).replace("...", " ").replace("…", " ").lower()
    s = _POSS_RE.sub("<poss>", s)
    toks = re.findall(r"<poss>|[a-z0-9]+(?:'[a-z]+)?", s)
    return [(t, _stem(t)) for t in toks if t not in _SLOT]


def norm_tokens(s: str) -> list:
    """段1用の正規化: NFKC・引用符直線化・小文字化・所有格/someoneのスロット除去・簡易屈折(ing/ed/es/s)除去。"""
    return [st for _, st in _tok_pairs(s)]


_LIGHT = {_stem(x) for x in "make take get go have do come give put let be".split()}
_STOP_STEMS = {_stem(x) for x in _STOP}


def content_tokens(toks: list) -> list:
    return [t for t in toks if t not in _STOP_STEMS and t not in _LIGHT]


def _is_sub(a: list, b: list) -> bool:
    if not a or len(a) > len(b):
        return False
    return any(b[i:i + len(a)] == a for i in range(len(b) - len(a) + 1))


# ============================================================
# 段1 構造判定 (structural_check) — F-2 / R-2。決定論・API 0
# ============================================================
def structural_check(expression: str, items: list) -> dict:
    """自動NG(auto_ng) = 次のいずれか(焦点語単位。'A vs B'は各側を主表現として検査):
      (a) 正規化した主表現が、項目の句(used_form/display_phrase/key_phrase)と一致
      (b) 複数語(正規化後2語以上かつ内容語を含む)の項目の句が、主表現に連続して丸ごと含まれる
    それ以外の語共有は shared(段2へのヒント。HR表示用shared_terms)。ここではfailにしない。
    items: build_inputsのpool entry(variants付き)。文法entryは対象外(段2のみ)。
    戻り値: {verdict: fail=暫定選定(必須NG対象①②)に自動NGあり / pass, focus_terms, auto_ng:[...], shared:[...]}"""
    terms = derive_focus_terms(expression)
    auto, shared = [], []
    for it in items:
        if it.get("kind") not in ("phrase", "word"):
            continue
        hit_auto = None
        for term in terms:
            tt = norm_tokens(term)
            if not tt:
                continue
            for v in it.get("variants") or [it.get("used_form")]:
                vt = norm_tokens(v)
                if not vt:
                    continue
                if tt == vt:
                    hit_auto = {"item_id": it["id"], "kind": it["kind"], "provisional": it["provisional"], "relation": "equal", "term": term, "matched_phrase": v}
                    break
                if len(vt) >= 2 and content_tokens(vt) and _is_sub(vt, tt):
                    hit_auto = {"item_id": it["id"], "kind": it["kind"], "provisional": it["provisional"], "relation": "contains", "term": term, "matched_phrase": v}
                    break
            if hit_auto:
                break
        if hit_auto:
            auto.append(hit_auto)
            continue
        for term in terms:   # 語共有ヒント(自動NGでない項目のみ)
            surf = {st: sf for sf, st in _tok_pairs(term) if st in set(content_tokens([st]))}     # 語幹 -> 主表現側の表層形(HR表示用)
            if not surf:
                continue
            for v in it.get("variants") or [it.get("used_form")]:
                inter = set(surf) & set(content_tokens(norm_tokens(v)))
                if inter:
                    shared.append({"item_id": it["id"], "kind": it["kind"], "provisional": it["provisional"], "term": term, "matched_phrase": v, "shared": sorted(surf[x] for x in inter)})
                    break
    seen, shared2 = set(), []
    for s in shared:   # item_id x termで1件
        k = (s["item_id"], s["term"])
        if k not in seen:
            seen.add(k)
            shared2.append(s)
    req_fail = any(a["provisional"] for a in auto)
    return {"verdict": "fail" if req_fail else "pass", "focus_terms": terms, "auto_ng": auto, "shared": shared2}


# ============================================================
# 引用検査 (quote_check) — M-9: 本文の連続した1〜2文の逐語部分文字列
# ============================================================
def quote_check(quote_en: str, body: str) -> dict:
    """quote_enが本文(段落を\\n\\nで連結した文字列)の逐語部分文字列であり、1〜2文・段落をまたがないことを検査する。
    曲がった引用符/空白の差は吸収する(文法のresolve_verbatimと同方式: 長さ保存の正規化で位置を引き、本文側の逐語文字列を返す)。
    戻り値: {ok, reason, verbatim(本文側の文字列), n_sentences}"""
    if not isinstance(quote_en, str) or not quote_en.strip():
        return {"ok": False, "reason": "empty", "verbatim": None, "n_sentences": 0}
    toks = _qn(quote_en).split()
    if not toks:
        return {"ok": False, "reason": "empty", "verbatim": None, "n_sentences": 0}
    m = re.search(r"\s+".join(re.escape(t) for t in toks), _qn(body))
    if not m:
        return {"ok": False, "reason": "not_in_body", "verbatim": None, "n_sentences": 0}
    verb = body[m.start():m.end()]
    if "\n" in verb:
        return {"ok": False, "reason": "spans_paragraphs", "verbatim": verb, "n_sentences": len(_sents(verb))}
    n = len(_sents(verb))
    if n < 1 or n > 2:
        return {"ok": False, "reason": f"sentences_{n}", "verbatim": verb, "n_sentences": n}
    return {"ok": True, "reason": None, "verbatim": verb, "n_sentences": n}


def candidate_sha256(c: dict) -> str:
    """HR提示・確定の照合キー。expression/focus/explanation_ja/quote_en/quote_ja/focus_termsの正規化(引用符直線化・空白圧縮)jsha。"""
    def n(x):
        return re.sub(r"\s+", " ", _qn(x or "")).strip()
    payload = {k: n(c.get(k)) for k in ("expression", "focus", "explanation_ja", "quote_en", "quote_ja")}
    payload["focus_terms"] = [n(t) for t in (c.get("focus_terms") or [])]
    return jsha(payload)


# ============================================================
# LLM呼出共通
# ============================================================
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
        return (getattr(r, "output_text", None) or ""), r.model, _usage_dict(getattr(r, "usage", None)), r.id
    return call_fn


def _cost_jpy(model: str, usage: dict):
    try:
        import er009_n1_routing_governance_10_actual_model_cost as pricing
        return pricing.cost_jpy_for_call("openai", model, usage.get("input_tokens"), usage.get("cached_input_tokens"), usage.get("output_tokens"))
    except Exception:   # 単価表に無い等。費用は監査に残らないだけで生成は止めない
        return None


def _get_client(client):
    if client is not None:
        return client
    import er003_v1_b1_scaffold_01_generate as b1s
    return b1s.get_client()


class _KindError(ValueError):
    def __init__(self, msg, kind):
        super().__init__(msg)
        self.kind = kind


def _call_with_retry(process: str, prompt: str, call_fn, parse_validate, *, budget_guard=None) -> dict:
    """初回 + 技術retry1回(上限厳守)。戻り値 {ok, value, calls, error_kind, error, model}。
    - 応答model不一致 = NuanceModelContractError(retryもfallbackもしない。STOP)
    - budget_guard()の例外は伝播(STOP)
    - call_fnが投げた一般例外 = api_error(attempt消費、retry対象)。ModelContractViolation/KeyboardInterruptは伝播。"""
    model = routing.require_model(process, MODEL)
    calls, last_err, last_kind = [], None, F_API
    for attempt_no in (1, 2):
        if budget_guard is not None:
            budget_guard(process, prompt, attempt_no)
        t0 = time.time()
        try:
            text, response_model, usage, response_id = call_fn(prompt)
        except (routing.ModelContractViolation, KeyboardInterrupt, NuanceModelContractError):
            raise
        except Exception as e:   # API障害 -> 技術失敗(非ブロッキング)。STOP系は上のexceptで伝播済み
            calls.append({"process": process, "attempt": attempt_no, "error": f"{type(e).__name__}: {e}", "elapsed_sec": round(time.time() - t0, 2), "cost_jpy": None})
            last_err, last_kind = f"{type(e).__name__}: {e}", F_API
            continue
        rec = {"process": process, "attempt": attempt_no, "response_model": response_model, "usage": usage, "response_id": response_id,
               "elapsed_sec": round(time.time() - t0, 2), "cost_jpy": _cost_jpy(response_model or model, usage or {})}
        calls.append(rec)
        if response_model != model:
            rec["model_contract_violation"] = True
            raise NuanceModelContractError(f"応答モデルが不一致です(process={process}, 期待: {model}, 実際: {response_model})。fallbackせずSTOPします(ER-006-MODEL-ROUTING-CONTRACT-01)。")
        try:
            value = parse_validate(text)
        except ValueError as e:
            rec["structure_error"] = str(e)
            last_err = str(e)
            last_kind = getattr(e, "kind", None) or F_GEN_INVALID
            continue
        return {"ok": True, "value": value, "calls": calls, "error_kind": None, "error": None, "model": model}
    return {"ok": False, "value": None, "calls": calls, "error_kind": last_kind, "error": last_err, "model": model}


# ============================================================
# 生成 (generate_candidate) — Prompt v3
# ============================================================
def _fmt_item(e: dict, label: str) -> str:
    disp = f"(本文中の形: {e['display_phrase']})" if e.get("display_phrase") and e["display_phrase"] != e["used_form"] else ""
    gloss = f" = {e['gloss']}" if e.get("gloss") else ""
    return f"{label}. {e['used_form']}{disp}{gloss} [{'単語' if e['kind'] == 'word' else '表現'}]"


def labels_for(inputs: dict) -> dict:
    """判定用の短いlocal id(K1..Kn, G1..Gm)と、実id・種別の対応。LLMに12桁hashを写させない。"""
    out = {}
    for k, e in enumerate(inputs["pool"], 1):
        out[f"K{k}"] = {"item_id": e["id"], "kind": e["kind"], "provisional": e["provisional"], "text": e["used_form"]}
    for k, e in enumerate(inputs["grammar"], 1):
        out[f"G{k}"] = {"item_id": e["id"], "kind": "grammar", "provisional": False, "text": e["title"]}
    return out


def build_gen_prompt(inputs: dict) -> str:
    pool = inputs["pool"]
    lab = {e["id"]: f"K{k}" for k, e in enumerate(pool, 1)}
    prov_block = "\n".join(_fmt_item(e, lab[e["id"]]) for e in inputs["provisional"]) or "(なし)"
    others = [e for e in pool if not e["provisional"]]
    pool_section = ""
    if others:
        pool_section = f"\n## その他の提示候補({len(others)}件。人間が選び替えて採用する可能性がある)\n" + "\n".join(_fmt_item(e, lab[e["id"]]) for e in others) + "\n"
    grammar_section = ""
    if inputs["grammar"]:
        grammar_section = (f"\n# 文法・文構造コーナーの候補(上位{len(inputs['grammar'])}件。人間が選ぶと載る可能性がある)\n"
                           + "\n".join(f"G{k}. {e['title']}(例文: {e['example']})" for k, e in enumerate(inputs["grammar"], 1)) + "\n")
    return PROMPT_GEN.format(title=inputs["title"], level_note=LEVEL_NOTE[inputs["level"]], body=inputs["body"], n_prov=len(inputs["provisional"]),
                             prov_block=prov_block, pool_section=pool_section, grammar_section=grammar_section)


_CAND_REQ = ("expression", "focus", "quote_en", "quote_ja", "explanation_ja")


def _parse_validate_gen(body: str):
    def pv(text: str):
        try:
            j = parse_json_object(text)
        except ValueError as e:
            raise _KindError(str(e), F_GEN_INVALID)
        if "candidate" not in j:
            raise _KindError("candidateキーがありません", F_GEN_INVALID)
        c = j["candidate"]
        if c is None:
            return {"candidate": None, "raw": j}
        if isinstance(c, list):   # 配列は不可(U-1)。1件だけの配列も受け入れない(schemaは単数)
            raise _KindError("candidateが配列です(最大1件。複数件は不可)", F_GEN_INVALID)
        if not isinstance(c, dict):
            raise _KindError("candidateがobjectでもnullでもありません", F_GEN_INVALID)
        if isinstance(j.get("candidates"), list) and len(j["candidates"]) > 1:
            raise _KindError("candidates配列に複数件があります", F_GEN_INVALID)
        for k in _CAND_REQ:
            if not isinstance(c.get(k), str) or not c[k].strip():
                raise _KindError(f"candidate.{k}が空または文字列でありません", F_GEN_INVALID)
        n = len(c["explanation_ja"].strip())
        if n < EXPLANATION_MIN_CHARS or n > EXPLANATION_MAX_CHARS:
            raise _KindError(f"explanation_jaの長さが範囲外({n}字。{EXPLANATION_MIN_CHARS}〜{EXPLANATION_MAX_CHARS})", F_GEN_INVALID)
        if not derive_focus_terms(c["expression"]):
            raise _KindError("expressionから英語の主表現を導出できません", F_GEN_INVALID)
        qc = quote_check(c["quote_en"], body)
        if not qc["ok"]:
            raise _KindError(f"quote_enが不正({qc['reason']})", F_QUOTE)
        c = dict(c)
        c["quote_en"] = qc["verbatim"]          # 本文側の逐語文字列へ置換(引用符/空白の差を本文に揃える)
        c["_quote_check"] = {"n_sentences": qc["n_sentences"]}
        return {"candidate": c, "raw": j}
    return pv


def generate_candidate(inputs: dict, *, call_fn=None, client=None, budget_guard=None) -> dict:
    """Prompt v3で1 call(+技術retry1回)。戻り値:
    {status: 'candidate'|'none'|'failed', candidate, no_candidate_reason, rejected_candidates, failure:{kind,detail}, calls, prompt_sha, model}
    self_rating != 'high' は決定論で0件(R-9)。candidateが配列/objectでない/必須欠落は不正(技術retry→それでも不正=failed)。"""
    prompt = build_gen_prompt(inputs)
    model = routing.require_model(PROCESS_GEN, MODEL)
    if call_fn is None:
        call_fn = _default_call_fn_factory(_get_client(client), model, GEN_MAX_OUTPUT_TOKENS)
    r = _call_with_retry(PROCESS_GEN, prompt, call_fn, _parse_validate_gen(inputs["body"]), budget_guard=budget_guard)
    base = {"calls": r["calls"], "prompt_sha": PROMPT_GEN_SHA256, "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(), "model": model,
            "rejected_candidates": None}
    if not r["ok"]:
        return dict(base, status="failed", candidate=None, no_candidate_reason=None, failure={"kind": r["error_kind"], "detail": r["error"]})
    raw = r["value"]["raw"]
    base["rejected_candidates"] = raw.get("rejected_candidates")
    c = r["value"]["candidate"]
    if c is None:
        return dict(base, status="none", candidate=None, no_candidate_reason=R_MODEL_NONE, model_reason_ja=raw.get("no_candidate_reason_ja"), failure=None)
    if (c.get("learning_value_self_rating") or "").strip().lower() != "high":
        return dict(base, status="none", candidate=None, no_candidate_reason=R_SELF_RATING, rejected_candidate_audit=c, failure=None)
    return dict(base, status="candidate", candidate=c, no_candidate_reason=None, failure=None)


# ============================================================
# 段2 判定 (judge_overlap) — M-4 / R-8 / R-10
# ============================================================
def build_judge_prompt(inputs: dict, cand: dict, stage1: dict | None = None) -> str:
    lab = labels_for(inputs)
    hints = {}
    for s in (stage1 or {}).get("shared") or []:
        hints.setdefault(s["item_id"], []).append(f"語『{'・'.join(s['shared'])}』を共有")
    lines = []
    for lid, m in lab.items():
        if m["kind"] == "grammar":
            gi = next(x for x in inputs["grammar"] if x["id"] == m["item_id"])
            lines.append(f"{lid}. {gi['title']}(例文: {gi['example']}) [文法・文構造]")
        else:
            e = next(x for x in inputs["pool"] if x["id"] == m["item_id"])
            h = f" [構造ヒント: {' / '.join(hints[e['id']])}]" if e["id"] in hints else ""
            lines.append(_fmt_item(e, lid) + f" [{'暫定選定' if e['provisional'] else 'その他の提示候補'}]" + h)
    # 生成側のdiffers_from_kp_word_ja/criteria_check/self_ratingは渡さない(R-8)
    return PROMPT_JUDGE.format(expression=cand["expression"], focus=cand["focus"], quote_en=cand["quote_en"], explanation_ja=cand["explanation_ja"],
                               n_items=len(lab), items_block="\n".join(lines))


def _parse_validate_judge(inputs: dict):
    expected = list(labels_for(inputs))

    def pv(text: str):
        try:
            j = parse_json_object(text)
        except ValueError as e:
            raise _KindError(str(e), F_OVERLAP_UNVERIFIED)
        items = j.get("items")
        if not isinstance(items, list):
            raise _KindError("itemsが配列でありません", F_OVERLAP_UNVERIFIED)
        ids = [it.get("id") if isinstance(it, dict) else None for it in items]
        if len(set(map(str, ids))) != len(ids):
            raise _KindError(f"idが重複しています: {ids}", F_OVERLAP_UNVERIFIED)
        if set(ids) != set(expected):
            raise _KindError(f"items全件が揃っていません(欠落: {sorted(set(expected) - set(ids))}, 余分: {sorted(map(str, set(ids) - set(expected)))})", F_OVERLAP_UNVERIFIED)
        per = {}
        for it in items:
            if not isinstance(it.get("same"), bool):
                raise _KindError(f"{it.get('id')}: sameがboolでありません", F_OVERLAP_UNVERIFIED)
            per[it["id"]] = {"same": it["same"], "why": str(it.get("why") or "").strip() if it["same"] else ""}
        closest = j.get("closest") if isinstance(j.get("closest"), dict) else None
        return {"per": per, "closest": closest}
    return pv


def judge_overlap(inputs: dict, cand: dict, *, stage1: dict | None = None, judge_fn=None, client=None, budget_guard=None) -> dict:
    """段2: 別Prompt・別callで、提示pool全件 + 文法Top1/Top2のid単位の判定。items全件(欠落・重複なし)が必須で、
    不正は技術retry1回 -> それでも不正 = {ok: False}(呼出側で overlap_unverified)。verdictはここでは出さない(decideが決定論で算出)。"""
    prompt = build_judge_prompt(inputs, cand, stage1)
    model = routing.require_model(PROCESS_JUDGE, MODEL)
    if judge_fn is None:
        judge_fn = _default_call_fn_factory(_get_client(client), model, JUDGE_MAX_OUTPUT_TOKENS)
    r = _call_with_retry(PROCESS_JUDGE, prompt, judge_fn, _parse_validate_judge(inputs), budget_guard=budget_guard)
    meta = {"calls": r["calls"], "prompt_sha": PROMPT_JUDGE_SHA256, "model": model}
    if not r["ok"]:
        return dict(meta, ok=False, per={}, closest=None, error=r["error"], error_kind=r["error_kind"])
    lab = labels_for(inputs)
    per = {}
    for lid, v in r["value"]["per"].items():
        m = lab[lid]
        per[m["item_id"]] = {"label": lid, "kind": m["kind"], "provisional": m["provisional"], "same_focus": v["same"], "why": v["why"]}
    closest = r["value"]["closest"]
    if closest and closest.get("id") in lab:
        closest = {"item_id": lab[closest["id"]]["item_id"], "label": closest["id"], "why": str(closest.get("why") or "").strip()}
    else:
        closest = None
    return dict(meta, ok=True, per=per, closest=closest, error=None, error_kind=None)


# ============================================================
# verdictの決定論算出 (decide) — F-1 / F-2 / M-4 / R-1 / R-2
# ============================================================
def decide(inputs: dict, cand: dict, stage1: dict, judge: dict | None) -> dict:
    """overlap_checkを返す。LLMのverdict欄は無く、全てper_itemから算出する。
    - 項目(KP/Word)のsame_focus = 段1自動NG or 段2same(段2 fail優先。段2 passは自動NGでない段1ヒットに優先)
    - verdict = fail: 暫定選定(必須NG対象①②)のどれかがsame_focus
                unverified: 必須NGは無いが段2が不能(judge is None or not ok)
                pass: 上記以外。pool項目(非暫定)のsame_focusは pool_conflicts(HRで採用不可の連動に使う)
    - 文法Top1/Top2のsame_focusは grammar_conflicts(警告)。verdictには影響させない(F-1/R-1)。
    - judgeを呼ばなかった(段1でfail)場合はjudge=Noneで、auto_ngだけで算出する。"""
    auto_by_id = {a["item_id"]: a for a in stage1.get("auto_ng") or []}
    shared_by_id = {}
    for s in stage1.get("shared") or []:
        shared_by_id.setdefault(s["item_id"], []).append(s)
    j_ok = bool(judge and judge.get("ok"))
    against, pool_conflicts, grammar_conflicts, shared_terms, req_fail_ids = [], [], [], [], []
    for e in inputs["pool"]:
        a = auto_by_id.get(e["id"])
        j = judge["per"].get(e["id"]) if j_ok else None
        s2 = j["same_focus"] if j else None
        same = bool(a) or bool(s2)
        src = "stage1_auto+stage2" if (a and s2) else ("stage1_auto" if a else ("stage2" if s2 else "none"))
        note = (j or {}).get("why") or (f"段1: 主表現『{a['term']}』が『{a['matched_phrase']}』と{'一致' if a['relation'] == 'equal' else 'を丸ごと含む'}" if a else "")
        against.append({"item_id": e["id"], "item": e["used_form"], "kind": e["kind"], "provisional": e["provisional"], "same_focus": same, "source": src, "note": note,
                        "stage2_judged": j is not None})
        if same:
            (req_fail_ids if e["provisional"] else pool_conflicts).append(e["id"])
        elif e["id"] in shared_by_id:
            for s in shared_by_id[e["id"]]:
                shared_terms.append({"item_id": e["id"], "item": e["used_form"], "term": s["term"], "shared": s["shared"], "stage2_pass": (s2 is False)})
    for ge in inputs["grammar"]:
        j = judge["per"].get(ge["id"]) if j_ok else None
        same = bool(j and j["same_focus"])
        against.append({"item_id": ge["id"], "item": ge["title"], "kind": "grammar", "provisional": False, "same_focus": same, "source": "stage2" if same else "none",
                        "note": (j or {}).get("why") or "", "stage2_judged": j is not None})
        if same:
            grammar_conflicts.append(ge["id"])
    if req_fail_ids:
        verdict = "fail"
    elif not j_ok and (inputs["pool"] or inputs["grammar"]):
        verdict = "unverified"
    else:
        verdict = "pass"
    names = {e["id"]: e["used_form"] for e in inputs["pool"]}
    if verdict == "fail":
        reason = "暫定選定の" + "・".join(f"『{names[i]}』" for i in req_fail_ids) + "と学習上の焦点が重複するため、HR提示前に破棄しました。"
    elif verdict == "unverified":
        reason = "重複判定(段2)が成立しなかった(JSON不正・全件判定の欠落・API障害)ため、安全側で候補を破棄しました。"
    else:
        reason = "暫定選定のKey Phrase・Wordとは学習上の焦点が別と判定しました。"
        if pool_conflicts:
            reason += "ただし、その他の提示候補" + "・".join(f"『{names[i]}』" for i in pool_conflicts) + "と同じ焦点です(HRでそれらを選ぶと採用不可)。"
        if grammar_conflicts:
            gnames = {x["id"]: x["title"] for x in inputs["grammar"]}
            reason += "文法候補" + "・".join(f"『{gnames[i]}』" for i in grammar_conflicts) + "と近い焦点です(警告)。"
    if judge is None:
        s2v = "skipped"
    elif not j_ok:
        s2v = "unverified"
    else:
        s2v = "fail" if any(x["stage2_judged"] and x["source"] in ("stage2", "stage1_auto+stage2") and x["kind"] != "grammar" for x in against) else "pass"
    return {
        "verdict": verdict,
        "stage1_structural": {"verdict": stage1.get("verdict"), "matched": stage1.get("auto_ng") or [], "shared_terms": stage1.get("shared") or []},
        "stage2_llm": {"verdict": s2v, "model": (judge or {}).get("model"), "closest": (judge or {}).get("closest")},
        "reason": reason, "against": against, "pool_conflicts": pool_conflicts, "grammar_conflicts": grammar_conflicts, "shared_terms": shared_terms,
        "required_conflicts": req_fail_ids,
    }


# ============================================================
# N1 orchestrator (run_candidate / candidate_stage) + N0 spec
# ============================================================
def _usage_total(calls: list) -> dict:
    costs = [c["cost_jpy"] for c in calls if c.get("cost_jpy") is not None]
    ins = sum((c.get("usage") or {}).get("input_tokens") or 0 for c in calls)
    outs = sum((c.get("usage") or {}).get("output_tokens") or 0 for c in calls)
    return {"input_tokens": ins, "output_tokens": outs, "cost_jpy": round(sum(costs), 4) if costs else None, "n_calls": len(calls), "calls": calls}


def _basis(inputs: dict) -> dict:
    return {"status": "provisional", "items": [e["used_form"] for e in inputs["provisional"]], "provisional_ids": inputs["provisional_ids"],
            "pool_ids": [{"id": e["id"], "kind": e["kind"]} for e in inputs["pool"]] + [{"id": x["id"], "kind": "grammar"} for x in inputs["grammar"]],
            "candidates_sha256": inputs.get("candidates_sha256"), "pool_identity_sha": inputs["pool_identity_sha"], "grammar_identity_sha": inputs["grammar_identity_sha"]}


def _doc_base(inputs: dict, level_key: str) -> dict:
    return {"schema": SCHEMA, "family": inputs["family"], "article_id": inputs["article_id"], "level": inputs["level_name"], "level_key": level_key,
            "generated_at": _now(), "candidate": None, "no_candidate_reason": None, "kp_word_basis": _basis(inputs), "text_sha256": inputs["text_sha256"],
            "model": MODEL, "prompt_sha": PROMPT_GEN_SHA256, "judge_prompt_sha": PROMPT_JUDGE_SHA256}


def run_candidate(inputs: dict, *, call_fn=None, judge_fn=None, client=None, budget_guard=None) -> dict:
    """N1の中核(保存なし)。生成 -> 段1 -> 段2 -> decide。技術失敗は例外にせずstatus=FAILED_TECHNICAL。
    段1が自動NG(暫定選定)でfailならjudge callを省く(候補は破棄)。同levelでの再生成・次点繰上げはしない(A-7)。"""
    level = _check_level(inputs["level"])
    doc = _doc_base(inputs, level)
    gen = generate_candidate(inputs, call_fn=call_fn, client=client, budget_guard=budget_guard)
    calls = list(gen["calls"])
    doc["generation"] = {"prompt_sha256": gen["prompt_sha256"], "rejected_candidates": gen.get("rejected_candidates"), "model_reason_ja": gen.get("model_reason_ja")}
    if gen["status"] == "failed":
        doc.update(status=ST_FAILED_TECHNICAL, failed_technical=gen["failure"], no_candidate_reason=f"failed_technical:{gen['failure']['kind']}")
        doc["usage"] = _usage_total(calls)
        return doc
    if gen["status"] == "none":
        doc.update(status=ST_NO_CANDIDATE, no_candidate_reason=gen["no_candidate_reason"])
        if gen.get("rejected_candidate_audit"):
            doc["rejected_candidate_audit"] = {"candidate": gen["rejected_candidate_audit"], "reason": gen["no_candidate_reason"]}
        doc["usage"] = _usage_total(calls)
        return doc
    cand = gen["candidate"]
    cand["focus_terms"] = derive_focus_terms(cand["expression"])
    stage1 = structural_check(cand["expression"], inputs["pool"])
    judge = None
    if stage1["verdict"] != "fail" and (inputs["pool"] or inputs["grammar"]):
        judge = judge_overlap(inputs, cand, stage1=stage1, judge_fn=judge_fn, client=client, budget_guard=budget_guard)
        calls += judge["calls"]
    oc = decide(inputs, cand, stage1, judge)
    doc["usage"] = _usage_total(calls)
    audit_cand = {k: v for k, v in cand.items() if not k.startswith("_")}
    if oc["verdict"] == "fail":
        doc.update(status=ST_NO_CANDIDATE, no_candidate_reason=R_OVERLAP_NG, rejected_candidate_audit={"candidate": audit_cand, "overlap_check": oc})
        return doc
    if oc["verdict"] == "unverified":
        doc.update(status=ST_FAILED_TECHNICAL, no_candidate_reason=f"failed_technical:{F_OVERLAP_UNVERIFIED}",
                   failed_technical={"kind": F_OVERLAP_UNVERIFIED, "detail": (judge or {}).get("error")}, rejected_candidate_audit={"candidate": audit_cand, "overlap_check": oc})
        return doc
    out = {k: v for k, v in cand.items() if not k.startswith("_") and k not in ("differs_from_kp_word_ja", "criteria_check", "learning_value_reason_ja")}
    out["generation_meta"] = {k: cand.get(k) for k in ("differs_from_kp_word_ja", "criteria_check", "learning_value_reason_ja") if k in cand}
    out["overlap_check"] = oc
    out["pool_conflicts"] = oc["pool_conflicts"]
    out["grammar_conflicts"] = oc["grammar_conflicts"]
    out["shared_terms"] = oc["shared_terms"]
    out["candidate_sha256"] = candidate_sha256(out)
    doc.update(status=ST_CANDIDATE, candidate=out)
    return doc


def study_files(study_dir: str) -> dict:
    return {"spec": f"{study_dir}/{SPEC_FILENAME}", "candidate": f"{study_dir}/{CANDIDATE_FILENAME}", "failed": f"{study_dir}/{FAILED_FILENAME}"}


def ensure_spec(study_dir: str, *, level: str, new_review: bool, issuer: str = "nuance_stage") -> dict:
    """N0。nuance_spec.jsonの発行は『新規KP review作成時』(new_review=True)だけ(M-2。呼出側が新規review作成フックからだけTrueを渡す)。
    既存spec = 不変(冪等・level一致を検査)。specが無くnew_review=False = LEGACY(発行しない。生成0・待機0・表示0)。KP確定済みかどうかでは発行しない。"""
    _check_level(level)
    p = study_files(study_dir)["spec"]
    if os.path.exists(p):
        d = _read_json(p)
        if d.get("schema") != SPEC_SCHEMA or d.get("level_key") != level:
            raise NuanceInputError(f"nuance_spec.jsonが不正またはlevel不一致です: {p}")
        return {"state": "SPEC_ISSUED", "spec": d, "issued_now": False}
    if not new_review:
        return {"state": ST_LEGACY, "spec": None, "issued_now": False}
    d = {"schema": SPEC_SCHEMA, "spec": "nuance_v1", "level_key": level, "issued_at": _now(), "issuer": issuer}
    _write_json_atomic(p, d)
    return {"state": "SPEC_ISSUED", "spec": d, "issued_now": True}


def _stale_reasons(prev: dict, inputs: dict) -> list:
    out = []
    if prev.get("schema") != SCHEMA:
        out.append("schema")
    if prev.get("text_sha256") != inputs["text_sha256"]:
        out.append("text_sha256")
    b = prev.get("kp_word_basis") or {}
    if b.get("pool_identity_sha") != inputs["pool_identity_sha"]:
        out.append("pool_identity_sha")
    if b.get("grammar_identity_sha") != inputs["grammar_identity_sha"]:
        out.append("grammar_identity_sha")
    if b.get("provisional_ids") != inputs["provisional_ids"]:
        out.append("provisional_ids")
    if prev.get("prompt_sha") != PROMPT_GEN_SHA256 or prev.get("judge_prompt_sha") != PROMPT_JUDGE_SHA256:
        out.append("prompt_sha")
    return out


def candidate_stage(study_dir: str, inputs: dict, *, call_fn=None, judge_fn=None, client=None, budget_guard=None, auto_adopted: bool = False) -> dict:
    """N1(保存あり)。
    - nuance_spec.jsonが無い = LEGACY(生成0)。auto_adopted=True(不在宣言でKPが人間の採否なしにAUTO採用された run) = NO_CANDIDATE(auto_adopted_no_human_review)・生成0。
    - 既存 nuance_candidate.json が text_sha256・pool_identity_sha・grammar_identity_sha・provisional_ids・prompt_sha と一致 = API 0で再利用。
      不一致 = 旧docを nuance_candidate.STALE_<sha8>.json へ退避(削除しない)して再生成。
    - FAILED_TECHNICALの既存docは resume時に自動再試行を1回まで(resume_attempts)。それ以降は同docを返す(再実行は明示コマンド)。
    戻り値: {state, doc, reused, api_calls}"""
    level = _check_level(inputs["level"])
    sp = ensure_spec(study_dir, level=level, new_review=False)
    if sp["state"] == ST_LEGACY:
        return {"state": ST_LEGACY, "doc": None, "reused": False, "api_calls": 0}
    f = study_files(study_dir)
    if auto_adopted:
        doc = _doc_base(inputs, level)
        doc.update(status=ST_NO_CANDIDATE, no_candidate_reason=R_AUTO_ADOPTED, usage=_usage_total([]))
        _write_json_atomic(f["candidate"], doc)
        return {"state": "SPEC_ISSUED", "doc": doc, "reused": False, "api_calls": 0}
    resume_attempts = 0
    if os.path.exists(f["candidate"]):
        prev = _read_json(f["candidate"])
        stale = _stale_reasons(prev, inputs)
        if not stale:
            if prev.get("status") != ST_FAILED_TECHNICAL or prev.get("resume_attempts", 0) >= 1:
                return {"state": "SPEC_ISSUED", "doc": prev, "reused": True, "api_calls": 0}
            resume_attempts = prev.get("resume_attempts", 0) + 1
        else:
            os.replace(f["candidate"], f"{study_dir}/nuance_candidate.STALE_{jsha(prev)[:8]}.json")
    doc = run_candidate(inputs, call_fn=call_fn, judge_fn=judge_fn, client=client, budget_guard=budget_guard)
    if resume_attempts:
        doc["resume_attempts"] = resume_attempts
    _write_json_atomic(f["candidate"], doc)
    if doc["status"] == ST_FAILED_TECHNICAL:
        _write_json_atomic(f["failed"], {"schema": "nuance_failed_v1", "level_key": level, "failed_technical": doc.get("failed_technical"), "at": _now(), "usage": doc["usage"]})
    return {"state": "SPEC_ISSUED", "doc": doc, "reused": False, "api_calls": doc["usage"]["n_calls"]}


# ============================================================
# Runner glue (NUANCE-EXPLANATION-PRODUCTION-WIRING-01 委任_02C。X/Y/Z 3 runnerが呼ぶ共通関数。runnerごとの分岐は『引数の渡し方』だけ)
#   N0+N1 = n1_stage(KP review作成/再利用の後・HR提示前) / N3 = finalize_stage(ページ生成入口。LLM 0・冪等) / 公開API wrapper(er128・exporterが内部関数に依存しない)
#   契約: (a) nuance_spec.json が無い = LEGACY = 生成0・待機0・表示0(ファイルも作らない) (b) 採否は人間のsidecar(confirmed_nuance.json)から決定論で導出し、
#   再生成・resume・regenerationで変わらない(sidecarがある限りLLMを呼ばない) (c) 技術失敗(API障害等)は非ブロッキング=ニュアンス無しで完結(STOP系例外だけ伝播)
# ============================================================
RESULT_SCHEMA = "nuance_result_v1"
RESULT_FILENAME = g.NUANCE_RESULT_FILENAME
REQUEST_FILENAME = "nuance_human_review_request.md"
ST_RESULT_ADOPTED, ST_RESULT_REJECTED, ST_RESULT_NONE = "ADOPTED", "REJECTED", "NONE"


class NuanceNotConfirmed(NuanceError):
    """採否が未確定(Human Review待ち。失敗ではなくrc=4)。pending=[{kind:'nuance', level, request_md, study_dir, status}]。"""

    def __init__(self, message: str, pending: list | None = None):
        super().__init__(message)
        self.pending = pending or []


class NuanceStale(NuanceError):
    """確定結果と現在の本文/確定集合が整合しない、または結果が読めない(STOP rc=3。人間の採用を黙って捨てない/覆さない=R-4)。"""


def pool_identity_sha_of(kp_cands: dict) -> str:
    """public wrapper: KP/Word候補docの提示poolの同一性sha(er128・exporter・form_nuance_bundleが内部関数 `_pool_entry` に依存しないための口)。"""
    return pool_identity_sha([_pool_entry(c, False) for c in presented_pool(kp_cands)])


def presented_ids_of(kp_cands: dict) -> list:
    """public wrapper: 提示pool(HRで人間が選べる集合)のcandidate_id(ai_rank順)。"""
    return [c["candidate_id"] for c in presented_pool(kp_cands)]


def grammar_items_of(study_dir: str) -> list:
    """提示中の文法Top1/Top2(grammar_candidates.json。候補抽出が未実行/無ければ[])。N1の重複判定(警告用)の入力。"""
    p = f"{study_dir}/grammar_candidates.json"
    if not os.path.exists(p):
        return []
    doc = _read_json(p)
    out = []
    for c in (doc.get("candidates") or [])[:GRAMMAR_PRESENT_MAX]:
        out.append({"id": c.get("candidate_id"), "rank": c.get("rank"), "title": c.get("construct_ja") or "", "example": c.get("sentence") or ""})
    return out


def render_request_md(doc: dict, *, level: str, run_hint: str) -> str:
    """HR依頼書(統合依頼書に連結される。フォームを使わない面〔CLI〕の案内を含む)。候補docの内容だけを逐語表示する(API 0)。"""
    cand = (doc or {}).get("candidate") or {}
    oc = cand.get("overlap_check") or {}
    lines = ["# ニュアンス解説 Human Review 依頼", "", f"- level: {level}({LEVELS.get(level)}) / 最大1件・採用するか不採用かを決めます(不採用でも代替候補は自動補充されません)",
             f"- 候補ID: nuance_{str(cand.get('candidate_sha256') or '')[:16]} / candidate_sha256: {cand.get('candidate_sha256')}", "",
             f"## {cand.get('expression')}", f"- 焦点: {cand.get('focus')}", "", cand.get("explanation_ja") or "", "",
             f"- 本文の英文: {cand.get('quote_en')}", f"- 日本語訳: {cand.get('quote_ja')}", "",
             f"- 重複判定(KP/Word): {oc.get('verdict')} / {oc.get('reason')}"]
    if cand.get("pool_conflicts"):
        lines.append(f"- 注意: 次の提示候補と焦点が重複します。これらを選ぶと採用できません: {cand['pool_conflicts']}")
    if cand.get("grammar_conflicts"):
        lines.append(f"- 警告(文法候補との重複の可能性。採否は妨げません): {cand['grammar_conflicts']}")
    lines += ["", "## 決め方", "- V3フォーム: 『ニュアンス解説』欄で採用/不採用を選び、KP・文法と一緒に送信(推奨)",
              f"- CLI(KPを先に確定した場合など): `py er119_kp_human_review_cli_01.py nuance-select --run {run_hint} --level {level} --choice adopt|reject "
              f"--candidates-sha {cand.get('candidate_sha256')} --by <名前> --user-ref <ユーザー発言のdelegation_logパス>`", ""]
    return "\n".join(lines)


def _pending_item(doc: dict | None, study_dir: str, level: str, run_hint: str, status: str) -> dict:
    p = f"{study_dir}/{REQUEST_FILENAME}"
    if doc and doc.get("status") == ST_CANDIDATE:
        os.makedirs(study_dir, exist_ok=True)
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(render_request_md(doc, level=level, run_hint=run_hint))
    return {"kind": "nuance", "level": level, "request_md": p, "study_dir": study_dir, "status": status}


def _failed_input_doc(*, family: str, article_id: str, level: str, kp_cands: dict, paragraphs: list, err: Exception) -> dict:
    """build_inputsが入力不整合で失敗した場合の候補doc(非ブロッキングの技術失敗として残す。黙って候補なしにしない)。"""
    return {"schema": SCHEMA, "family": family, "article_id": article_id, "level": LEVELS[level], "level_key": level, "generated_at": _now(), "candidate": None,
            "status": ST_FAILED_TECHNICAL, "no_candidate_reason": "failed_technical:input_error", "failed_technical": {"kind": "input_error", "detail": f"{type(err).__name__}: {err}"},
            "kp_word_basis": {"status": "provisional", "items": [], "provisional_ids": [], "pool_ids": [], "candidates_sha256": (kp_cands or {}).get("candidates_sha256"),
                              "pool_identity_sha": pool_identity_sha_of(kp_cands or {}), "grammar_identity_sha": None},
            "text_sha256": g.text_sha256(list(paragraphs)), "model": MODEL, "prompt_sha": PROMPT_GEN_SHA256, "judge_prompt_sha": PROMPT_JUDGE_SHA256, "usage": _usage_total([])}


def n1_stage(*, family: str, run_dir: str, kp_dir: str, study_dir: str, level: str, article_id: str, title: str, paragraphs: list, review_existed: bool,
             client=None, call_fn=None, judge_fn=None, budget_guard=None) -> dict:
    """N0(spec発行)+N1(候補生成・重複判定)。KP review作成/再利用の**後**・HR提示前に各levelで1回呼ぶ(Opus M-1)。
    - KP候補docが無い(候補生成失敗等) = SKIPPED(specも作らない)
    - spec: 『この呼出でKP reviewが新規作成された(review_existed=False)』ときだけ発行(M-2。遡及なし)。無ければLEGACY=何もしない
    - 確定済みsidecar(live)がある = 再生成しない(CONFIRMED。採否保持)
    - 不在宣言(AUTO採用)のrun = 生成0(NO_CANDIDATE: auto_adopted_no_human_review)
    - 技術失敗はFAILED_TECHNICAL docを残し非ブロッキング。model契約違反・予算guard例外・KeyboardInterruptは伝播(STOP)
    戻り: {state(LEGACY|SKIPPED|CONFIRMED|SPEC_ISSUED), status(candidate doc status|None), api_calls, cost_jpy, pending(HR待ちitem|None), reused}"""
    _check_level(level)
    cands = rv.load_candidates(kp_dir)
    if cands is None:
        return {"state": "SKIPPED", "status": None, "api_calls": 0, "cost_jpy": 0.0, "pending": None, "reused": False}
    sp = ensure_spec(study_dir, level=level, new_review=not review_existed)
    if sp["state"] == ST_LEGACY:
        return {"state": ST_LEGACY, "status": None, "api_calls": 0, "cost_jpy": 0.0, "pending": None, "reused": False}
    cc = rv._cc()
    if cc.nuance_state(study_dir) is not None:   # 人間が確定済み: LLMを呼ばない(採否保持)
        return {"state": "CONFIRMED", "status": None, "api_calls": 0, "cost_jpy": 0.0, "pending": None, "reused": True}
    review = rv.load_review(kp_dir) or {}
    auto = review.get("status") == rv.ST_AUTO
    try:
        inputs = build_inputs(family=family, article_id=article_id, title=title, level=level, paragraphs=paragraphs, kp_cands=cands,
                              grammar_items=grammar_items_of(study_dir), std_part1=bool(review.get("std_part1", True)))
    except NuanceInputError as e:
        doc = _failed_input_doc(family=family, article_id=article_id, level=level, kp_cands=cands, paragraphs=paragraphs, err=e)
        _write_json_atomic(study_files(study_dir)["candidate"], doc)
        _write_json_atomic(study_files(study_dir)["failed"], {"schema": "nuance_failed_v1", "level_key": level, "failed_technical": doc["failed_technical"], "at": _now(), "usage": doc["usage"]})
        return {"state": "SPEC_ISSUED", "status": ST_FAILED_TECHNICAL, "api_calls": 0, "cost_jpy": 0.0, "pending": None, "reused": False}
    res = candidate_stage(study_dir, inputs, call_fn=call_fn, judge_fn=judge_fn, client=client, budget_guard=budget_guard, auto_adopted=auto)
    doc = res["doc"]
    pend = _pending_item(doc, study_dir, level, run_dir, "NUANCE_PENDING") if (doc and doc.get("status") == ST_CANDIDATE) else None
    cost = (doc or {}).get("usage", {}).get("cost_jpy") if not res["reused"] else 0.0
    return {"state": res["state"], "status": (doc or {}).get("status"), "api_calls": res["api_calls"], "cost_jpy": cost or 0.0, "pending": pend, "reused": res["reused"]}


def retry_failed_candidate(study_dir: str, *, level: str) -> str:
    """明示操作(CLI nuance-retry): **技術失敗(FAILED_TECHNICAL)の候補docだけ**を退避し、次回の制作コマンド(--stage kp等)でN1を再実行させる(R-5。HR送信前の再試行)。
    有効な候補(CANDIDATE)/本物の0件(NO_CANDIDATE)は退避しない=『代替候補を探し直す』経路を作らない(A-7)。確定後は拒否(revoke必須)。戻り: 退避先path。"""
    _check_level(level)
    rv._cc().guard_nuance(study_dir, "候補の再試行")
    p = study_files(study_dir)["candidate"]
    if not os.path.exists(p):
        raise NuanceInputError(f"退避する候補docがありません: {p}")
    if _read_json(p).get("status") != ST_FAILED_TECHNICAL:
        raise NuanceInputError("再試行できるのは技術失敗(FAILED_TECHNICAL)の候補docだけです。有効な候補・本物の0件は、採否を人間が決めます(代替候補の自動補充・探し直しはしません)")
    dst = f"{study_dir}/nuance_candidate.REGEN_{jsha(_read_json(p))[:8]}.json"
    os.replace(p, dst)
    return dst


def _result_path(study_dir: str) -> str:
    return f"{study_dir}/{RESULT_FILENAME}"


def _write_result_if_changed(study_dir: str, res: dict) -> None:
    p = _result_path(study_dir)
    if os.path.exists(p):
        try:
            if _read_json(p) == res:
                return
        except (OSError, ValueError):
            pass
    _write_json_atomic(p, res)


def finalize_stage(study_dir: str, paragraphs: list, *, level: str, kp_dir: str, run_hint: str = "<run>") -> dict | None:
    """N3(ページ生成入口で呼ぶ。**LLM 0**・冪等)。人間の確定(confirmed_nuance.json)から表示用の確定結果 `nuance_result.json` を決定論で書き、その内容を返す。
    戻り: None = LEGACY(nuance_spec.json無し。ファイルも作らない=従来出力と同一) / dict(status=ADOPTED|REJECTED|NONE)。
    - sidecar(live)あり: adopted→ADOPTED(候補全文は確定時の逐語コピー。引用が現在の本文に1〜2文の逐語で残ることと、確定した①②が現在の確定レコードと一致することを再確認。崩れていれば
      NuanceStale=STOP。人間の採用を自動で覆さない=R-4) / rejected→REJECTED / none→NONE
    - sidecarなし: 候補なし/技術失敗の候補docで本文が一致 → NONE(人間の判断対象が無い) / 不在宣言(AUTO採用) → NONE / 候補ありで未決定 → NuanceNotConfirmed(rc=4。黙って不採用にしない)
    - 候補docが無い/古い(本文不一致) → NuanceNotConfirmed(rc=4。制作コマンドを再実行してN1を実行)"""
    _check_level(level)
    sf = study_files(study_dir)
    if not os.path.exists(sf["spec"]):
        return None
    cc = rv._cc()
    cur_text_sha = g.text_sha256(list(paragraphs))
    st = cc.nuance_state(study_dir)
    doc = _read_json(sf["candidate"]) if os.path.exists(sf["candidate"]) else None
    if st is not None:
        side = st["sidecar"]
        decision = side.get("decision")
        base = {"schema": RESULT_SCHEMA, "level_key": level, "confirmation_id": side.get("confirmation_id"), "decided_by": side.get("by"), "decided_at": side.get("decided_at"),
                "user_ref": side.get("user_ref"), "text_sha256": cur_text_sha}
        if decision == "adopted":
            cand = side.get("candidate")
            if not isinstance(cand, dict) or candidate_sha256(cand) != side.get("candidate_sha256") or cand.get("candidate_sha256") != side.get("candidate_sha256"):
                raise NuanceStale("確定したニュアンス解説の本文がsidecarのshaと一致しません(改変の疑い)。表示しません。revoke→再確認してください")
            q = quote_check(cand.get("quote_en"), "\n\n".join(paragraphs))
            if not q["ok"]:
                raise NuanceStale(f"確定したニュアンス解説の引用が現在の本文に逐語で見つかりません({q['reason']})。本文が変わった可能性があります。"
                                  f"`py er128_kp_confirmed_content_01.py revoke --run {run_hint} --level {level} ...` で確定を取り消して選び直してください(人間の採用を自動で覆しません)")
            live_ids = sorted(i["candidate_id"] for i in st["rec"].get("items") or [] if i.get("category") in (1, 2))
            if sorted((side.get("confirmed_against") or {}).get("kp_word") or []) != live_ids:
                raise NuanceStale("ニュアンス解説の確定後にKey Phrase・Wordの確定集合が変わっています(重複の最終確認が成立しません)。revoke→再確認してください")
            out = dict(base, status=ST_RESULT_ADOPTED, reason=None, candidate_sha256=side["candidate_sha256"],
                       candidate={k: (q["verbatim"] if k == "quote_en" else cand[k]) for k in ("expression", "focus", "explanation_ja", "quote_en", "quote_ja")},
                       final_overlap_check={"verdict": "pass", "against_kp_word": live_ids, "stage": "N3_deterministic", "n1_overlap_check": (cand.get("overlap_check") or {}).get("verdict")},
                       model=(doc or {}).get("model"), prompt_sha=(doc or {}).get("prompt_sha"))
        elif decision == "rejected":
            out = dict(base, status=ST_RESULT_REJECTED, reason="human_rejected", candidate_sha256=side.get("candidate_sha256"))
        else:
            out = dict(base, status=ST_RESULT_NONE, reason=side.get("no_candidate_reason") or "no_candidate_at_confirm", candidate_sha256=None)
        _write_result_if_changed(study_dir, out)
        return out
    # sidecarなし(人間の採否が無い)
    if doc is None or doc.get("text_sha256") != cur_text_sha or doc.get("level_key") not in (None, level):
        raise NuanceNotConfirmed("ニュアンス解説の候補がまだ生成されていない、または本文が変わっています(N1未実行/古い)。制作コマンド(X=--stage scaffold / Y・Z=--stage kp)を同じまま再実行して候補を作ってください。",
                                 pending=[{"kind": "nuance", "level": level, "request_md": None, "study_dir": study_dir, "status": "NUANCE_CANDIDATE_MISSING"}])
    review = rv.load_review(kp_dir) or {}
    status = doc.get("status")
    if status == ST_CANDIDATE and review.get("status") != rv.ST_AUTO:
        raise NuanceNotConfirmed(f"ニュアンス解説の採用/不採用がHuman Reviewで未確定です(level={level})。V3フォーム、または `py er119_kp_human_review_cli_01.py nuance-select --run {run_hint} "
                                 f"--level {level} --choice adopt|reject --candidates-sha {(doc.get('candidate') or {}).get('candidate_sha256')} --by <名前> --user-ref <path>` で決めてください。",
                                 pending=[_pending_item(doc, study_dir, level, run_hint, "NUANCE_PENDING")])
    reason = R_AUTO_ADOPTED if status == ST_CANDIDATE else (doc.get("no_candidate_reason") or status)
    out = {"schema": RESULT_SCHEMA, "level_key": level, "status": ST_RESULT_NONE, "reason": reason, "candidate_sha256": None, "confirmation_id": None, "text_sha256": cur_text_sha,
           "candidate_doc_status": status}
    _write_result_if_changed(study_dir, out)
    return out
