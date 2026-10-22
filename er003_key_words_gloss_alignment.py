# ============================================================
# er003_key_words_gloss_alignment.py
# KP-GLOSS-ALIGNMENT-CORRECTED-PRODUCTION-WIRING-01 (委任_02, 2026-10-15): 修正版(corrected)が唯一の方式。
# ============================================================
# 根本原因: 日本語gloss(japanese_gloss)は「選定段」(DB Hybrid / Strategy Lの選定LLM、
# 承認済みPromptの『選ぶ表現は本文中の実表現(source_span)に対応させ、短く自然な日本語グロスを付ける』)
# が**候補span/display_phraseに対して**生成する。一方、最終Key Phrase(key_phrase)は選定の後段
# canonicalization(別LLM呼出、入力にglossを含まない)が確定する。canonicalizationがKPを候補より
# 長く(補語・目的語を復元して)確定すると、glossは候補基準のまま残り、最終英語KPとglossが不整合になる
# (例: KP『based on interviews』/gloss『～をもとにした』/TTS『なになにをもとにした』)。
#
# 是正(Prompt/Rule7/Validator/Gate無変更): canonicalization確定後、最終KPが表示候補(display_phrase)
# に無い語を含むitemだけを対象に、同一モデルルーティング(SUPPORT_MODEL)で日本語glossを最終KP基準で
# 再整合する工程を追加する(2026-10-15 ユーザー正式採用、Production既定ON)。gloss生成規則は承認済み選定Prompt
# (b1_p2_keywords_l_prompt_template.txt)の「日本語グロス…」の段落を実行時に抽出して再利用する(複製しない)。
# 方針A: 「～」の有無は合否に使わない。追加内容語→日本語span対応は record-only(mapping_gateは既定False、
#   Production呼出元は渡さない)。
# 方針B/C: item単位retry上限2。2回失敗したitemは gloss_alignment_status=FAILED_HUMAN_REVIEW_REQUIRED として
#   artifactに永続化し、消費側(Family X TTS関所/Family Z stage_kp)が参照して停止する(KPを短い候補へ戻さない)。
#   Human Review Lock・human_review_queue.jsonlは使わない。
# 全経路(初回/redundancy retry/Strategy L fallback/regeneration)は run_key_phrase_canonicalization 経由のため
# 同じ工程を通る。kill switch: プロセス環境変数 EIGO_KP_GLOSS_ALIGNMENT=0/false/off/no のみ(import時に1回評価。
# .env経由は保証しない)。無効化は承認済み仕様の無効化であり、起動時に警告+実効値の記録を必須とする。
from __future__ import annotations

import datetime
import difflib
import hashlib
import json
import os
import re
import unicodedata
from typing import Any, Callable, Optional

import er003_audio_tts_asr_safety as safety
import er003_key_words_canonicalization as kc

GLOSS_ALIGNMENT_VERSION = "ER-003-KP-GLOSS-ALIGN-02"   # OF-KGCPW-02: 旧版(-01)artifactと区別する
MAX_GLOSS_ALIGNMENT_ATTEMPTS = 2
APPROVED_GLOSS_RULES_TEMPLATE_PATH = "er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt"
HR_RESOLVE_RUNBOOK = "docs/pm/runbooks/KP_GLOSS_ALIGNMENT_HR_RESOLVE_01.md"
FLAG_ENV_NAME = "EIGO_KP_GLOSS_ALIGNMENT"
_FLAG_OFF_VALUES = ("0", "false", "off", "no")


def _read_flag_env() -> tuple:
    """(enabled, raw, source)。Production既定ON: 未設定ならON。0/false/off/noのときだけOFF(typo等はON=承認済み仕様が動く側)。"""
    raw = os.environ.get(FLAG_ENV_NAME)
    if raw is None:
        return True, None, "default"
    return raw.strip().lower() not in _FLAG_OFF_VALUES, raw, "env"


GLOSS_ALIGNMENT_ENABLED, _FLAG_RAW, _FLAG_SOURCE = _read_flag_env()


def flag_enabled() -> bool:
    """唯一のkill switchの現在値(プロセス環境変数のみ。import時評価)。"""
    return bool(GLOSS_ALIGNMENT_ENABLED)


def flag_effective() -> dict:
    """OF-KGCPW-11: 実効値と取得元。X/Zがrun開始時にstdout+summaryへ記録する。"""
    return {"enabled": bool(GLOSS_ALIGNMENT_ENABLED), "raw": _FLAG_RAW, "source": _FLAG_SOURCE}


def announce_flag(print_fn: Optional[Callable] = None) -> dict:
    """run開始時に1行出力し、実効値dictを返す。OFFは『承認済み仕様の無効化』の警告(設計§3)。"""
    eff = flag_effective()
    pf = print_fn or print
    if eff["enabled"]:
        pf(f"[GLOSS-ALIGN] 実効flag=ON (source={eff['source']}, {FLAG_ENV_NAME}={eff['raw']!r})")
    else:
        pf(f"[GLOSS-ALIGN][WARN] DISABLED by {FLAG_ENV_NAME}={eff['raw']} (承認済み仕様の無効化)。"
           "gloss再整合は実行されません。ユーザーへ必ず報告してください")
    return eff


DEVELOPER_MESSAGE = ("英語学習教材のKey Phraseに付ける日本語グロスを、最終的な英語Key Phrase全体の意味に"
                     "過不足なく一致させてください。")

GLOSS_ALIGNMENT_JSON_SCHEMA = {
    "name": "key_phrase_gloss_alignment_corrected",
    "schema": {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "rank": {"type": "integer"},
                        "current_gloss_consistent": {"type": "boolean"},
                        "japanese_gloss": {"type": "string"},
                        "qa_reflects_all_key_phrase_words": {"type": "string", "enum": ["PASS", "FAIL"]},
                        "reasoning": {"type": "string"},
                        "added_word_mappings": {
                            "type": "array",
                            "items": {"type": "object",
                                      "properties": {"english_word": {"type": "string"}, "japanese_span": {"type": "string"}},
                                      "required": ["english_word", "japanese_span"], "additionalProperties": False},
                        },
                    },
                    "required": ["rank", "current_gloss_consistent", "japanese_gloss", "added_word_mappings",
                                 "qa_reflects_all_key_phrase_words", "reasoning"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["items"],
        "additionalProperties": False,
    },
    "strict": True,
}

_PAREN_RE = re.compile(r"[()（）\[\]［］【】]")
_ARABIC_DIGIT_RE = re.compile(r"[0-9]")
_TOKEN_RE = re.compile(r"[a-z0-9]+(?:'[a-z0-9]+)?")
_GENERIC_TOKENS = {"one's", "someone's", "somebody's", "one", "someone", "somebody", "oneself"}


def _stem(t: str) -> str:
    return re.sub(r"(ing|ed|es|s|d)$", "", t) if len(t) > 3 else t


def _extra_tokens(display_phrase: str, key_phrase: str) -> list:
    """最終KPが表示候補(display_phrase)に対して追加した語(トークン)のリスト(順序保持・重複あり得る)。
    kp_adds_words_beyond_display と追加内容語算出(added_content_words)が共有する。"""
    d = kc._normalize_for_match(display_phrase or "").replace("’", "'")
    k = kc._normalize_for_match(key_phrase or "").replace("’", "'")
    if not k or d == k:
        return []
    articles = {"a", "an", "the"}
    dset = {_stem(t) for t in _TOKEN_RE.findall(d)}
    kset = [t for t in _TOKEN_RE.findall(k) if t not in articles]
    def _near(t):
        return any(difflib.SequenceMatcher(None, _stem(t), x).ratio() >= 0.7 for x in dset)
    return [t for t in kset if t not in _GENERIC_TOKENS and _stem(t) not in dset and not _near(t)]


def kp_adds_words_beyond_display(display_phrase: str, key_phrase: str) -> bool:
    """最終KPが表示候補(display_phrase)に無い語を含むか。活用形の違い(gave/give)・
    人称代名詞の一般化(their->one's)・冠詞の増減は『語の追加』に数えない。"""
    return bool(_extra_tokens(display_phrase, key_phrase))


def select_alignment_targets(merged_items: list) -> list:
    return [it for it in merged_items
            if it.get("kp_extends_beyond_candidate")
            or kp_adds_words_beyond_display(it.get("display_phrase"), it.get("key_phrase"))]


# ============================================================
# 人称・指示対象の整合(FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01 委任_05, 2026-10-19)
# ユーザー2026-10-19 APPROVED_FOR_PRODUCTION(項目①) / Opus条件Aレビュー_E F1-1〜F1-6。X/Z/Y共通。
# 根本原因: 英語KPがcanonicalizationで人称を一般化(your->someone's等)しても、選定時に付いた日本語意味
#   (具体的な人称語を含む日本語意味)は追従せず、旧版は_GENERIC_TOKENSを『語の追加』に数えないため再整合の対象外だった。
# 方式(案III): (a)人称一般化itemを再整合の対象に追加(生成用) (b)汎用制約文(不定の人称は日本語でも不定のまま・文脈は語義選択のみ)
#   (c)決定論的な人称語突合を採用値(adopt_gloss)へ適用し、不整合は既存validate->retry(上限2)->HRへ接続。
# 特定表現・記事に依存する分岐は持たない(閉じた語彙表の構造的な突合のみ)。kill switch(EIGO_KP_GLOSS_ALIGNMENT=0)OFF時は無効。
# 生成用の対象(select_generation_targets)と消費側の未評価判定(select_consumer_unevaluated)は意図的に別関数(F1-1):
#   消費側へ人称一般化item全件を入れると、健全な既存artifact(日本語意味に人称語が無いもの)が一斉にSTOPする。
# ============================================================
PERSON_ALIGNMENT_VERSION = "ER-003-KP-GLOSS-PERSON-ALIGN-01"
PERSON_NORMALIZATION_REASON = "generalize_person_dependent_reference"
# 英語KPが具体的な人称を持つ(=検査対象外とする)語。canonicalizationの閉じた語彙表のkey + 目的格・一人称。
_CONCRETE_PERSON_EN = frozenset(set(kc._PERSON_DEPENDENT_TO_GENERIC) |
                                {"me", "him", "us", "them", "myself", "ourselves", "i", "we", "mine", "ours", "hers"})
_REFLEXIVE_EN = frozenset({"one's", "oneself"})
_KANJI = "㐀-鿿々〆"
# 日本語の具体人称語(閉じた語彙)。かな表記は『きみ』『おれ』『かれ』等の語中・他語義との衝突が大きいため含めない。
_JA_PERSON_WORDS = ("あなた", "貴方", "お前", "おまえ", "わたくし", "わたし", "ぼく", "かのじょ", "我々", "彼女", "君", "私", "僕", "俺", "彼")
_JA_REFLEXIVE_WORDS = ("自分", "自身")
_JA_SUFFIX = ("たち", "から", "より", "だけ", "さえ", "自身", "の", "が", "は", "を", "に", "と", "も", "へ", "で", "や", "ら", "達")
_JA_PUNCT = "\\s、。・,.!?！？～〜~」』)）"
_JA_AFTER = "(?=(?:" + "|".join(_JA_SUFFIX) + ")|$|[" + _JA_PUNCT + "])"
_JA_PERSON_RE = re.compile("(?<![" + _KANJI + "])(" + "|".join(_JA_PERSON_WORDS) + ")" + _JA_AFTER)
# 『あなた方』のみ『方』を接尾として許容する(『彼方』『君主』等の語を誤検出しない)。
_JA_ANATA_KATA_RE = re.compile("(?<![" + _KANJI + "])あなた方")
_JA_REFLEXIVE_RE = re.compile("(?<![" + _KANJI + "])(" + "|".join(_JA_REFLEXIVE_WORDS) + ")" + _JA_AFTER)


def _kp_tokens(kp: Optional[str]) -> list:
    k = kc._normalize_for_match(kp or "").replace("’", "'")
    return _TOKEN_RE.findall(k)


def indefinite_person_tokens(key_phrase: Optional[str]) -> list:
    """英語KPに含まれる不定の人称(一般形)トークン(出現順・重複除去)。"""
    out: list = []
    for t in _kp_tokens(key_phrase):
        if t in _GENERIC_TOKENS and t not in out:
            out.append(t)
    return out


def _ja_person_hits(gloss: Optional[str]) -> tuple:
    """(具体人称語のlist, 再帰語『自分/自身』のlist)。境界付き照合(直前が漢字でない・直後が助詞/接尾/末尾)。"""
    g = unicodedata.normalize("NFKC", gloss or "")
    concrete = [m.group(1) for m in _JA_PERSON_RE.finditer(g)] + ["あなた方" for _ in _JA_ANATA_KATA_RE.finditer(g)]
    reflexive = [m.group(1) for m in _JA_REFLEXIVE_RE.finditer(g)]
    return concrete, reflexive


def person_reference_mismatch(key_phrase: Optional[str], gloss_ja: Optional[str]) -> Optional[str]:
    """決定論(LLM 0): 英語KPが不定の人称(someone/one's/oneself等)を持ち、かつ具体的な人称語(me/him/us/them/your等)を
    持たないとき、日本語意味が具体的な人称語(あなた/私/彼/君…)を含めば不整合理由を返す。無ければNone。
    再帰: KPのどこかにone's/oneselfがあれば『自分/自身』を許容(例 put oneself in someone's shoes)。
    someone系のみのKPで『自分』は不整合。『相手/その人/人』は不定の自然な訳なので検出しない。"""
    toks = _kp_tokens(key_phrase)
    generic = [t for t in toks if t in _GENERIC_TOKENS]
    if not generic or any(t in _CONCRETE_PERSON_EN for t in toks):
        return None
    concrete, reflexive = _ja_person_hits(gloss_ja)
    bad = list(dict.fromkeys(concrete))
    if not any(t in _REFLEXIVE_EN for t in toks):
        bad += [w for w in dict.fromkeys(reflexive)]
    if not bad:
        return None
    return (f"人称不整合: 英語KP『{key_phrase}』は不定の人称({'/'.join(dict.fromkeys(generic))})だが、日本語意味『{gloss_ja}』が"
            f"具体的な人称語({'/'.join(bad)})を含む。不定の人称は日本語でも不定のまま(『誰かの』『人の』、再帰のone's等は『自分の』)表す")


def is_person_generalized(item: dict) -> bool:
    """canonicalizationが人称を一般化したitem(normalization_reason、またはdisplay->keyが閉じた語彙表の1対1置換)。"""
    if not indefinite_person_tokens(item.get("key_phrase")):
        return False
    if item.get("normalization_reason") == PERSON_NORMALIZATION_REASON:
        return True
    try:
        return bool(kc._is_valid_person_generalization(item.get("key_phrase") or "", item.get("display_phrase") or ""))
    except Exception:
        return False


def person_generalization_pairs(item: dict) -> list:
    """display_phrase->key_phraseで人称トークンが一般形へ置換された組([{from,to}])。導出できなければ[]。"""
    d = _kp_tokens(item.get("display_phrase"))
    k = _kp_tokens(item.get("key_phrase"))
    if len(d) != len(k):
        return []
    return [{"from": a, "to": b} for a, b in zip(d, k)
            if a != b and b in (kc._PERSON_DEPENDENT_TO_GENERIC.get(a) or ())]


def _person_mismatch_reason(item: dict) -> Optional[str]:
    """statusにかかわらず全itemへ適用(F1-2)。例外=HUMAN_RESOLVED(人間確定値を再度STOPさせない)。"""
    if item.get("gloss_alignment_status") == STATUS_HUMAN_RESOLVED:
        return None
    return person_reference_mismatch(item.get("key_phrase"), item.get("japanese_gloss"))


def is_fulltext_gloss_missing(item: dict) -> bool:
    """KPFT 委任_02(Q6): 全文選定(fulltext_p2)由来itemでjapanese_glossが未生成(Prompt 2は意味を出力しない)。
    `fulltext_source_ref`マーカーはmerge時にcanonicalizationが引き継ぐ(OF-KPFT-P-01)。A/B/Cのitemは該当しない。"""
    return bool(isinstance(item, dict) and item.get("fulltext_source_ref") and not (item.get("japanese_gloss") or "").strip())


def select_fulltext_gloss_missing(items: list) -> list:
    return [it for it in items if is_fulltext_gloss_missing(it)]


def select_generation_targets(merged_items: list) -> list:
    """(a)生成用: 従来の再整合対象 + 人称一般化item + 決定論checkで不整合のitem + 全文選定でgloss未生成のitem。
    消費側(select_consumer_unevaluated)とは別関数。"""
    out = []
    for it in merged_items:
        if (select_alignment_targets([it]) or is_person_generalized(it) or _person_mismatch_reason(it)
                or is_fulltext_gloss_missing(it)):
            out.append(it)
    return out


def select_person_mismatches(items: list) -> list:
    """修復/検出の対象: 決定論checkで不整合のitem(HUMAN_RESOLVEDとHR待ちを除く。HR待ちは別経路collect_unresolvedで止まる)。"""
    return [it for it in items if isinstance(it, dict)
            and it.get("gloss_alignment_status") not in (STATUS_HR_REQUIRED, STATUS_OLD_FAILED)
            and _person_mismatch_reason(it)]


def select_consumer_unevaluated(items: list) -> list:
    """(b)消費側: 従来の定義(再整合対象なのにstatus無し) + 決定論checkで不整合のitem。
    人称一般化item全件は入れない(健全artifactを一斉STOPさせない。F1-1)。"""
    out = [it for it in select_alignment_targets(items) if not it.get("gloss_alignment_status")]
    seen = {id(it) for it in out}
    out += [it for it in select_person_mismatches(items) if id(it) not in seen]
    # KPFT 委任_02(Q6/OF-KPFT-P-01): 全文選定でgloss未生成のitemは、TTS/組立へ進めない(fail-closed。gloss再整合が生成を担う)。
    seen = {id(it) for it in out}
    out += [it for it in select_fulltext_gloss_missing(items) if id(it) not in seen]
    return out


def person_mismatch_warnings(items: list) -> list:
    """HUMAN_RESOLVEDで人称不整合になっているitem(STOPさせず、WARNとして記録するだけ)。"""
    return [{"rank": it.get("rank"), "key_phrase": it.get("key_phrase"), "japanese_gloss": it.get("japanese_gloss"),
             "reason": person_reference_mismatch(it.get("key_phrase"), it.get("japanese_gloss"))}
            for it in items if isinstance(it, dict) and it.get("gloss_alignment_status") == STATUS_HUMAN_RESOLVED
            and person_reference_mismatch(it.get("key_phrase"), it.get("japanese_gloss"))]


PERSON_CONSTRAINT_TEXT = (
    "【人称・指示対象の規則(indefinite_person_tokens_in_key_phraseを持つ項目に適用。承認済みgloss規則・上記1〜3より優先)】\n"
    "- key_phraseの不定の人称(someone's/someone/somebody/one's/oneself等)は、日本語でも不定のまま表してください"
    "(例: 『誰かの』『人の』『人を』。one's/oneselfのように主語自身を指す再帰の場合は『自分の』『自分自身を』)。"
    "display_phrase_before_canonicalization・current_japanese_gloss・source_sentenceにある具体的な人称"
    "(あなた・君・私・僕・彼・彼女・彼ら・我々等)を日本語意味へ残してはいけません。"
    "不定の人称を具体的な人称で訳すことは『誤っている』に当たります。current_japanese_glossがそうなっている場合は、"
    "指示2の『書き換えない』の例外として、current_gloss_consistent=falseにして書き換えてください。\n"
    "- source_sentenceは、辞書に複数の語義がある表現で、そのうちどの語義かを選ぶためだけに使い、"
    "人称の指示対象を決めるためには使わないでください。\n"
    "- 逐語訳は求めません。不定の人称を訳出すると不自然になる場合は、人称を明示しない自然な表現にしてかまいません。"
    "(型の例: catch someone's attention -> 『人の注意を引く』であって『あなたの注意を引く』ではない。)\n\n")


NEW_GENERATION_TEXT = (
    "【新規生成の規則(current_japanese_glossがnull[未生成]の項目に適用。全文選定で選ばれた表現には、まだ日本語グロスがありません)】\n"
    "- current_japanese_glossがnullの項目は、既存グロスの修正ではなく新規生成です。current_gloss_consistentは必ずfalseにし、"
    "japanese_glossには最終key_phrase全体の意味に過不足なく一致する日本語グロスを新しく書いてください(上記の指示2の"
    "『そのまま返す』は適用されません)。\n"
    "- source_sentenceは、辞書に複数の語義がある表現で、そのうちどの語義かを選ぶためだけに使ってください"
    "(文中の固有名詞・文脈の追加はしないでください)。\n\n")


class GlossRulesExtractionError(RuntimeError):
    pass


_RULES_CACHE: dict = {}


NUMERIC_PLACEHOLDER_RULE_MARKER = "数値を補わないと意味が成立しない句"


def load_approved_gloss_rules(path: str = APPROVED_GLOSS_RULES_TEMPLATE_PATH, include_numeric_rule: bool = False) -> str:
    """承認済み選定Promptの日本語グロス規則を実行時に抽出する(複製・改変しない)。
    対象: (1)『日本語グロス』で始まる段落すべて(3段落以上) + (2)『短く自然な日本語グロス』を含む選定指示の段落
    (OF-229: テンプレート17行『選ぶ表現は必ず本文中の実表現(source_span)に対応させ、短く自然な日本語グロスを付けて…』)。
    いずれかが欠けたらGlossRulesExtractionError(記事内容に依存しない即時失敗)。"""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    selection = [p for p in paras if "短く自然な日本語グロス" in p]
    gloss = [p for p in paras if p.startswith("日本語グロス")]
    if len(gloss) < 3:
        raise GlossRulesExtractionError(f"承認済みgloss規則の抽出に失敗(日本語グロス段落数不足: {len(gloss)})")
    if len(selection) != 1:
        raise GlossRulesExtractionError(f"承認済み選定指示『短く自然な日本語グロス』段落の抽出に失敗(件数: {len(selection)})")
    if include_numeric_rule:
        # KPFT 委任_02(OF-KPFT-P-13、Fable決定): 旧template:15『数値を補わないと意味が成立しない句・日本語グロスは選ばない』は
        # CURRENT_SPEC:470-472『(2) 数値placeholder型の回避』=承認済みProduction品質条件。Prompt 2は逐語固定のため、
        # 全文選定itemのgloss生成規則へ含めて維持する(A/B/Cのgloss規則=従来の抽出は無変更)。
        numeric = [p for p in paras if NUMERIC_PLACEHOLDER_RULE_MARKER in p]
        if len(numeric) != 1:
            raise GlossRulesExtractionError(f"承認済み『数値placeholder型の回避』段落の抽出に失敗(件数: {len(numeric)})")
        return "\n\n".join(selection + gloss + numeric)
    return "\n\n".join(selection + gloss)


def rules_sha256(rules: str) -> str:
    return hashlib.sha256(rules.encode("utf-8")).hexdigest()


def preflight(enabled: Optional[bool] = None) -> Optional[dict]:
    """run開始時に1回呼ぶ(OF-229)。抽出失敗は例外で全記事を即時停止させる。無効時は何もしない。
    成功時は{rules, sha256}をキャッシュし、以後のalign_glossesはキャッシュを使う。"""
    if enabled is None:
        enabled = GLOSS_ALIGNMENT_ENABLED
    if not enabled:
        return None
    if "v" not in _RULES_CACHE:
        rules = load_approved_gloss_rules()
        rules_ft = load_approved_gloss_rules(include_numeric_rule=True)   # 抽出失敗は記事内容に依存しない設定不備=ここで即時停止
        _RULES_CACHE["v"] = {"rules": rules, "sha256": rules_sha256(rules),
                             "rules_fulltext": rules_ft, "sha256_fulltext": rules_sha256(rules_ft)}
    return _RULES_CACHE["v"]


class GlossAlignmentModelMismatchError(RuntimeError):
    pass


def make_alignment_fn(user_message: str, client: Optional[Any] = None, model: str = None,
                      reasoning_effort: str = "high", developer_message: str = DEVELOPER_MESSAGE,
                      schema: Optional[dict] = None):
    if client is None:
        from dotenv import load_dotenv
        load_dotenv()
        from openai import OpenAI
        client = OpenAI()
    if model is None:
        raise ValueError("modelは明示的に指定してください(routing.require_model()経由)")

    def fn():
        response = client.responses.create(
            model=model, reasoning={"effort": reasoning_effort},
            text={"format": {"type": "json_schema", **(schema if schema is not None else GLOSS_ALIGNMENT_JSON_SCHEMA)}},
            input=[{"role": "developer", "content": developer_message},
                   {"role": "user", "content": user_message}],
        )
        if response.model != model:
            raise GlossAlignmentModelMismatchError(
                f"応答モデルが不一致です(期待: {model}, 実際: {response.model})")
        u = getattr(response, "usage", None)
        in_d = getattr(u, "input_tokens_details", None)
        fn.last_usage = {"input_tokens": getattr(u, "input_tokens", None), "output_tokens": getattr(u, "output_tokens", None),
                         "cached_input_tokens": getattr(in_d, "cached_tokens", None) if in_d is not None else None}
        text = getattr(response, "output_text", None)
        if not text or not text.strip():
            raise RuntimeError("gloss alignment応答が空です")
        return text, response.model, response.id

    fn.last_usage = None
    fn.model = model
    fn.reasoning_effort = reasoning_effort
    return fn


def _usage_cost(fn, model_id) -> dict:
    u = getattr(fn, "last_usage", None) or {}
    cost = None
    try:
        import er009_n1_routing_governance_10_actual_model_cost as pricing
        if u.get("input_tokens") is not None:
            cost = round(pricing.cost_jpy_for_call("openai", model_id or getattr(fn, "model", None), u.get("input_tokens"),
                                                   u.get("cached_input_tokens"), u.get("output_tokens")), 4)
    except Exception:
        cost = None
    return {"usage": u, "cost_jpy": cost}


# ============================================================
# item status / HR報告 / 消費側共通定数(Lock・human_review_queue不使用)
# ============================================================
STATUS_HR_REQUIRED = "FAILED_HUMAN_REVIEW_REQUIRED"      # itemのgloss_alignment_status
STATUS_HUMAN_RESOLVED = "HUMAN_RESOLVED"                 # resolve_glossが書く
STATUS_ALIGNED = "ALIGNED"                               # 再整合が成立したitem
STATUS_OLD_FAILED = "FAILED"                             # 旧版(ER-003-KP-GLOSS-ALIGN-01)が書いたFAILED。未解決として扱う(OF-KGCPW-14)
STOPPED_STATUS = "STOPPED_GLOSS_ALIGNMENT_FAILED"        # 消費側(TTS関所)が返す非OK status(Gateは非許可statusとしてblock)
HR_REPORT_JSON = "GLOSS_ALIGNMENT_HUMAN_REVIEW_01.json"
HR_REPORT_MD = "GLOSS_ALIGNMENT_HUMAN_REVIEW_01.md"
HR_REPORT_VERSION = "ER-003-KP-GLOSS-ALIGN-HR-01"
HR_REASON_CODE = "GLOSS_ALIGNMENT_HUMAN_REVIEW_REQUIRED"
HR_REFERENCE_CAUTION = "KPを短くすると意味が失われる、人間判断でのみ採用"
UNEVALUATED_REASON = ("ON化前・未評価のKP成果物(gloss再整合の対象itemにgloss_alignment_statusが無い、または全文選定itemのgloss未生成"
                      "[kill switch EIGO_KP_GLOSS_ALIGNMENT=0のままだとglossが作られないため、X/Zでは解除して再生成])。"
                      "KPを再生成してください(Z: --regenerate-stage kp_<lv> / X: KP成果物削除後に再生成)")


class GlossAlignmentNotificationError(RuntimeError):
    """HR報告の書込/再読検証に失敗(fail-closed: 呼出元は当該stageを止める。『通知失敗だが継続』は禁止)。"""


class GlossResolveRejected(ValueError):
    pass


# ---- 追加内容語(機械算出) -------------------------------------------------
# 機能語(前置詞・不変化詞・助動詞・冠詞・接続/補助語)は日本語spanの必須対象外(Opus OF-KGDC-06)。
# 人称代名詞の一般化(their->one's等)は_extra_tokens側で既に追加語に数えない。
FUNCTION_WORDS = frozenset({
    "a", "an", "the",
    "in", "on", "at", "to", "of", "for", "with", "by", "from", "into", "onto", "about", "around", "through",
    "across", "after", "before", "between", "against", "among", "along", "as", "than", "per", "via", "over",
    "under", "above", "below", "behind", "beyond", "within", "without", "toward", "towards", "upon", "off",
    "up", "down", "out", "away", "back", "forth", "apart",
    "be", "is", "are", "am", "was", "were", "been", "being", "do", "does", "did", "have", "has", "had",
    "will", "would", "can", "could", "shall", "should", "may", "might", "must",
    "and", "or", "but", "if", "that", "so",
})


def added_content_words(display_phrase: str, key_phrase: str) -> list:
    """最終KPが候補に追加した内容語(機能語除く)。重複除去・出現順。correctedの機械検査対象。"""
    seen, out = set(), []
    for t in _extra_tokens(display_phrase, key_phrase):
        if t in FUNCTION_WORDS or t in seen:
            continue
        seen.add(t)
        out.append(t)
    return out


_WS_RE = re.compile(r"\s+")


def _norm_tilde_space(s: Optional[str]) -> str:
    """OF-KGDC-10: 『真なら不変』比較の正規化(空白と～/〜/~のみ。それ以外の書換えは検知する)。"""
    return _WS_RE.sub("", s or "").replace("〜", "～").replace("~", "～")


def _norm_span(s: Optional[str]) -> str:
    """OF-KGDC-06: span一致の正規化(NFKC+空白除去+～/〜統一)。"""
    return _norm_tilde_space(unicodedata.normalize("NFKC", s or ""))


_SYMBOL_ONLY_RE = re.compile(r"[～~〜\s・、。,.!?！？「」『』\-ー_/…]*")


def _span_is_symbol_only(span_norm: str) -> bool:
    return _SYMBOL_ONLY_RE.fullmatch(span_norm or "") is not None


def _words_match(a: str, b: str) -> bool:
    """英単語の同一性(活用/単複を許容): 完全一致・語幹一致・長さ4以上の前方一致(price/prices, watch/watching)。"""
    if a == b or _stem(a) == _stem(b):
        return True
    short, long_ = (a, b) if len(a) <= len(b) else (b, a)
    return len(short) >= 4 and long_.startswith(short)


def check_added_word_mappings(required_words: list, mappings: Any, gloss: str) -> dict:
    """追加内容語→日本語span対応の機械検査(record-only既定。gate化はユーザー承認事項)。
    判定=必須内容語すべてが、gloss内に実在する記号以外のspanのいずれかで覆われる。
    mappingは多対一・重複可、english_wordに句可(トークン/語幹一致)。戻り値のpassは『gateとして判定した場合』の合否。"""
    result = {"required_words": list(required_words), "covered": {}, "uncovered": [], "span_not_in_gloss": [],
              "symbol_only_spans": [], "malformed_mappings": 0, "pass": True}
    if not required_words:
        result["note"] = "必須内容語なし(機械検査対象外)"
        return result
    gnorm = _norm_span(gloss)
    valid = []   # (english_tokens, span_original)
    if not isinstance(mappings, list):
        result["malformed_mappings"] = 1
        mappings = []
    for m in mappings:
        if not (isinstance(m, dict) and isinstance(m.get("english_word"), str) and isinstance(m.get("japanese_span"), str)):
            result["malformed_mappings"] += 1
            continue
        span = m["japanese_span"]
        sn = _norm_span(span)
        if not sn or _span_is_symbol_only(sn):
            result["symbol_only_spans"].append(span)
            continue
        if sn not in gnorm:
            result["span_not_in_gloss"].append(span)
            continue
        toks = _TOKEN_RE.findall(m["english_word"].lower().replace("’", "'"))
        valid.append((toks, span))
    for w in required_words:
        hit = next((span for toks, span in valid if any(_words_match(t, w) for t in toks)), None)
        if hit is None:
            result["uncovered"].append(w)
        else:
            result["covered"][w] = hit
    result["pass"] = not result["uncovered"]
    return result


def build_user_message_corrected(targets: list, article_text: str, rules: Optional[str] = None,
                                 prior: Optional[dict] = None) -> str:
    """prior: {rank: {"gloss": 前回提案, "reasons": [前回INVALID理由]}}。retry時だけ項目単位で渡す(ITEM1 F1-3)。"""
    rules = rules if rules is not None else (preflight(True) or {})["rules"]
    items = []
    any_person = False
    for it in targets:
        d = {
            "rank": it["rank"],
            "key_phrase": it["key_phrase"],
            "display_phrase_before_canonicalization": it.get("display_phrase"),
            "current_japanese_gloss": it.get("japanese_gloss"),
            "source_sentence": it.get("source_sentence", ""),
            "added_content_words": added_content_words(it.get("display_phrase"), it.get("key_phrase")),
        }
        ind = indefinite_person_tokens(it.get("key_phrase"))
        if ind:
            any_person = True
            d["indefinite_person_tokens_in_key_phrase"] = ind
            pairs = person_generalization_pairs(it)
            if pairs:
                d["person_generalization"] = pairs
        if prior and it["rank"] in prior:
            d["previous_attempt_rejected"] = {"gloss": prior[it["rank"]].get("gloss"),
                                              "reasons": list(prior[it["rank"]].get("reasons") or [])}
        items.append(d)
    person_block = PERSON_CONSTRAINT_TEXT if any_person else ""
    new_gen_block = NEW_GENERATION_TEXT if any(is_fulltext_gloss_missing(it) for it in targets) else ""
    prior_block = ("previous_attempt_rejected(ある項目のみ)は、前回の応答が検証で却下された理由です。同じ誤りを繰り返さないでください。\n\n"
                   if prior else "")
    return (
        "以下の各英語key_phraseは、教材として最終確定した英語表現です。current_japanese_glossは、確定前の候補表現"
        "(display_phrase_before_canonicalization)を基準に付けた日本語グロスで、確定したkey_phrase全体とは"
        "一致していない可能性があります。added_content_wordsは、確定時に候補表現へ新しく加わった内容語です"
        "(空の場合があります)。\n\n"
        "各項目について、次を行ってください。\n"
        "1. current_japanese_glossが、最終的なkey_phrase全体(目的語・補語・修飾語を含むすべての語)の意味と過不足なく"
        "一致しているかを判定し(current_gloss_consistent)てください。「～」「〜」を含むかどうかは判定の基準ではありません。"
        "key_phrase全体の意味が日本語に表れているかどうかだけで判定してください。\n"
        "2. 一致している場合は、japanese_glossにcurrent_japanese_glossをそのまま返してください。一致していない場合は、"
        "最終key_phrase全体に一致する日本語グロスを返してください。"
        "current_japanese_glossが最終key_phrase全体の意味を既に表している場合は、より自然・より適切と思える言い換えがあっても"
        "書き換えず、current_japanese_glossをそのまま返してください。書き換えるのは、key_phraseの語の意味が欠けている・"
        "誤っている場合だけです。\n"
        "3. added_content_wordsの各語について、japanese_glossの中でその語の意味を表している部分を、japanese_glossから"
        "そのまま切り出してadded_word_mappingsに書いてください(english_wordには対応させる英語の語、複数語をまとめた句でも"
        "かまいません。japanese_spanにはjapanese_glossに含まれない文字列や、「～」などの記号だけを書かないでください)。"
        "複数の英語語が一つの日本語表現でまとめて表されている場合は、同じ部分を複数の語に対応させてかまいません。"
        "added_content_wordsが空の項目は、added_word_mappingsを空配列にしてください。\n"
        "判定の参考例:\n"
        "- key_phrase「based on」にcurrent「～をもとにした」: 辞書的に自然なので一致です。\n"
        "- key_phrase「based on interviews」にcurrent「～をもとにした」: interviewsの意味が欠けているので不一致です。"
        "「インタビューをもとにした」なら一致です。\n"
        "- key_phrase「fall into」にcurrent「～に落ちる」: 意味は表れているので一致です(「～に陥る」へ書き換えません)。\n\n"
        "key_phrase単体で他の文脈でも再利用できる自然な訳にし、本文固有の固有名詞・文脈の追加はしないでください。"
        "key_phrase全体の意味を反映できている場合のみqa_reflects_all_key_phrase_wordsをPASSにしてください。\n\n"
        + person_block + new_gen_block + prior_block +
        "【日本語グロスの規則(承認済み選定Promptと同一)】\n" + rules + "\n\n"
        "【対象項目】\n" + json.dumps(items, ensure_ascii=False, indent=2) + "\n\n【記事本文(参考)】\n" + article_text
    )


# ---- item単位検証(「～」条件なし) ---------------------------------------------
def validate_item_corrected(resp: Any, target: dict, mapping_gate: bool = False) -> dict:
    """1 itemの応答を検証する。合否=LLM判定(qa PASS・真偽とglossの整合)+承認規則由来の記号チェック。
    mappingの機械検査(machine_check)は常に記録し、mapping_gate=Trueの場合のみ合否にも使う(既定record-only)。"""
    rank = target["rank"]
    cur = target.get("japanese_gloss") or ""
    reasons: list = []
    out = {"rank": rank, "valid": False, "reasons": reasons, "machine_check": None, "adopt_gloss": None,
           "proposed_gloss": None, "current_gloss_consistent": None, "qa": None, "reasoning": None,
           "added_word_mappings": None, "person_check": None}
    if not isinstance(resp, dict):
        reasons.append("応答にこのrankのitemが無い")
        return out
    g = resp.get("japanese_gloss")
    out["current_gloss_consistent"] = resp.get("current_gloss_consistent")
    out["qa"] = resp.get("qa_reflects_all_key_phrase_words")
    out["reasoning"] = resp.get("reasoning")
    out["added_word_mappings"] = resp.get("added_word_mappings")
    if not isinstance(g, str) or not g.strip():
        reasons.append("gloss空")
        return out
    g = g.strip()
    out["proposed_gloss"] = g
    consistent = resp.get("current_gloss_consistent")
    if not isinstance(consistent, bool):
        reasons.append("current_gloss_consistentが真偽値でない")
    if resp.get("qa_reflects_all_key_phrase_words") != "PASS":
        reasons.append("qa_reflects_all_key_phrase_words!=PASS")
    if _PAREN_RE.search(g):
        reasons.append("括弧禁止違反")
    if _ARABIC_DIGIT_RE.search(g):
        reasons.append("算用数字禁止違反")
    if "…" in g:
        reasons.append("…禁止違反")
    if safety.symbol_gate_requires_stop(
            [{**f, "rank": rank} for f in safety.detect_prohibited_symbols(kc.convert_display_gloss_to_tts_text(g), language="ja")]):
        reasons.append("音声化禁止記号")
    same = _norm_tilde_space(g) == _norm_tilde_space(cur)
    new_generation = is_fulltext_gloss_missing(target)   # KPFT 委任_02: current無し=新規生成。矛盾判定は適用しない(他の検査は全て適用)
    if not new_generation:
        if consistent is True and not same:
            reasons.append("current_gloss_consistent=真なのにcurrentと異なるglossを返した(矛盾)")
        if consistent is False and same:
            reasons.append("current_gloss_consistent=偽なのにcurrentと同じglossを返した(矛盾)")
    adopt = cur if (consistent is True and same and not new_generation) else g
    out["adopt_gloss"] = adopt
    # ITEM1(F1-3): 決定論の人称語突合は提案値ではなく採用値adopt_glossに掛ける(current維持でも素通りさせない)。
    pm = person_reference_mismatch(target.get("key_phrase"), adopt)
    out["person_check"] = pm
    if pm:
        reasons.append(pm)
    required = added_content_words(target.get("display_phrase"), target.get("key_phrase"))
    mc = check_added_word_mappings(required, resp.get("added_word_mappings"), adopt)
    out["machine_check"] = mc
    if mapping_gate and not mc["pass"]:
        reasons.append(f"追加内容語に対応するspanが無い/不正: {mc['uncovered']}(mapping gate)")
    out["valid"] = not reasons
    return out


def _item_log_entry(attempt: int, v: dict, batch: dict) -> dict:
    return {"attempt": attempt, "verdict": "VALID" if v["valid"] else "INVALID", "reasons": list(v["reasons"]),
            "proposed_gloss": v["proposed_gloss"], "current_gloss_consistent": v["current_gloss_consistent"],
            "qa": v["qa"], "reasoning": v["reasoning"], "added_word_mappings": v["added_word_mappings"],
            "machine_check": v["machine_check"], "batch_status": batch.get("status"),
            "batch_cost_jpy": batch.get("cost_jpy"), "model": batch.get("model")}


def run_alignment_gate_corrected(make_factory_for: Callable[[str], Callable], targets: list, article_text: str,
                                 rules: str, mapping_gate: bool = False,
                                 max_attempts: int = MAX_GLOSS_ALIGNMENT_ATTEMPTS) -> dict:
    """item単位retry(OF-KGDC-09): 各attemptは未解決itemのみで入力を再構築し、各itemは最初の有効出力を採用する。
    上限は既存と同じ2回(MAX_GLOSS_ALIGNMENT_ATTEMPTS)。技術失敗/JSON不正もattemptを消費する。"""
    adopted: dict = {}
    item_log = {t["rank"]: [] for t in targets}
    attempts: list = []
    messages: list = []
    pending = list(targets)
    prior: dict = {}   # ITEM1 F1-3: 前回INVALID理由(人称語残存等)を項目単位でretryのuser messageへ渡す
    for attempt in range(1, max_attempts + 1):
        if not pending:
            break
        msg = build_user_message_corrected(pending, article_text, rules, prior=prior or None)
        messages.append(msg)
        fn = make_factory_for(msg)
        rec = {"attempt": attempt, "target_ranks": [t["rank"] for t in pending]}
        try:
            raw, model_id, response_id = fn()
        except Exception as e:
            rec.update({"status": "TECHNICAL_FAILED", "error": f"{type(e).__name__}: {e}", **_usage_cost(fn, None)})
            attempts.append(rec)
            for t in pending:
                item_log[t["rank"]].append({"attempt": attempt, "verdict": "TECHNICAL_FAILED", "reasons": [rec["error"]],
                                            "proposed_gloss": None, "batch_status": rec["status"],
                                            "batch_cost_jpy": rec.get("cost_jpy")})
            continue
        rec.update({"model": model_id, "response_id": response_id, **_usage_cost(fn, model_id)})
        try:
            parsed = json.loads(raw)
        except Exception as e:
            rec.update({"status": "PARSE_FAILED", "error": str(e)})
            attempts.append(rec)
            for t in pending:
                item_log[t["rank"]].append({"attempt": attempt, "verdict": "PARSE_FAILED", "reasons": [f"JSON不正: {e}"],
                                            "proposed_gloss": None, "batch_status": rec["status"],
                                            "batch_cost_jpy": rec.get("cost_jpy"), "model": model_id})
            continue
        resp_items = parsed.get("items") if isinstance(parsed, dict) else None
        if not isinstance(resp_items, list):
            resp_items = []
            rec["structure_note"] = "items欠落"
        by_rank: dict = {}
        for it in resp_items:
            if isinstance(it, dict) and isinstance(it.get("rank"), int) and it["rank"] not in by_rank:
                by_rank[it["rank"]] = it
        extra = sorted(set(by_rank) - {t["rank"] for t in pending})
        if extra:
            rec["extra_ranks_ignored"] = extra
        n_valid = 0
        for t in pending:
            v = validate_item_corrected(by_rank.get(t["rank"]), t, mapping_gate=mapping_gate)
            item_log[t["rank"]].append(_item_log_entry(attempt, v, {"status": None, "cost_jpy": rec.get("cost_jpy"),
                                                                    "model": model_id}))
            if v["valid"]:
                adopted[t["rank"]] = {**v, "attempt": attempt}
                n_valid += 1
            else:
                prior[t["rank"]] = {"gloss": v.get("proposed_gloss"), "reasons": list(v["reasons"])}
        rec["status"] = "ALIGN_PASS" if n_valid == len(pending) else ("ALIGN_PARTIAL" if n_valid else "ALIGN_INVALID")
        rec["n_valid"] = n_valid
        rec["n_items"] = len(pending)
        rec["parsed"] = parsed
        attempts.append(rec)
        pending = [t for t in pending if t["rank"] not in adopted]
    return {"adopted": adopted, "unresolved_ranks": [t["rank"] for t in pending], "item_log": item_log,
            "attempts": attempts, "messages": messages}


def apply_alignment_corrected(merged: dict, targets: list, gate: dict) -> dict:
    """適用(新しいdictを返す)。成立item: gloss更新(真なら不変=currentの原文を保持)。未解決item: KP・旧glossは維持し
    gloss_alignment_status=FAILED_HUMAN_REVIEW_REQUIRED(KPを候補へ戻さない=方針C)。対象外itemは無変更。"""
    target_ranks = {t["rank"] for t in targets}
    unresolved = set(gate["unresolved_ranks"])
    items, unresolved_list = [], []
    for it in merged["items"]:
        r = it["rank"]
        if r not in target_ranks:
            items.append(it)
            continue
        new = dict(it)
        orig = it.get("japanese_gloss")
        log = gate["item_log"].get(r, [])
        if r in gate["adopted"]:
            a = gate["adopted"][r]
            adopt = a["adopt_gloss"]
            changed = _norm_tilde_space(adopt) != _norm_tilde_space(orig) or adopt != orig
            if changed:
                new["japanese_gloss"] = adopt
                new["japanese_gloss_tts"] = kc.convert_display_gloss_to_tts_text(adopt)
            new["gloss_alignment"] = {
                "version": GLOSS_ALIGNMENT_VERSION,
                "status": "GLOSS_REALIGNED" if changed else "GLOSS_ALREADY_CONSISTENT",
                "original_japanese_gloss": orig, "current_gloss_consistent_verdict": a["current_gloss_consistent"],
                "reasoning": a["reasoning"], "adopted_attempt": a["attempt"],
                "added_word_mappings": a["added_word_mappings"], "machine_check_record_only": a["machine_check"],
                "attempts_count": len(log)}
            new["gloss_review_hint"] = False
            new["gloss_alignment_status"] = STATUS_ALIGNED
        else:
            new["gloss_alignment"] = {
                "version": GLOSS_ALIGNMENT_VERSION,
                "status": "GLOSS_ALIGNMENT_FAILED_HUMAN_REVIEW_REQUIRED",
                "original_japanese_gloss": orig, "key_phrase_kept": it.get("key_phrase"),
                "failure": {"attempts": log, "attempts_count": len(log)}}
            new["gloss_review_hint"] = True
            new["gloss_alignment_status"] = STATUS_HR_REQUIRED
            unresolved_list.append({"rank": r, "key_phrase": it.get("key_phrase")})
        items.append(new)
    out = dict(merged)
    out["items"] = items
    if unresolved_list:
        out["gloss_alignment_unresolved"] = unresolved_list
    return out


def align_glosses(merged: dict, article_text: str, make_factory_for: Callable[[str], Callable],
                  out_dir: Optional[str] = None, article_id: str = "", enabled: Optional[bool] = None,
                  mapping_gate: bool = False, only_ranks: Optional[list] = None) -> dict:
    """戻り値: {"merged": 更新後merged, "status": ..., "targets": [ranks], "attempts": [...]}。
    対象0件のときはAPI呼出なし・mergedは無変更(同一object)。enabled=False(kill switch)なら status=DISABLED で無変更。"""
    if enabled is None:
        enabled = GLOSS_ALIGNMENT_ENABLED
    if not enabled:
        return {"merged": merged, "status": "DISABLED", "targets": [], "attempts": []}
    targets = select_generation_targets(merged["items"])   # ITEM1(F1-1): 生成用の対象(従来 ∪ 人称一般化 ∪ 人称不整合)
    if only_ranks is not None:   # 永続化済みartifactの修復(Z stage_kpの人称整合関所): 指定rankのみ
        targets = [t for t in targets if t["rank"] in set(only_ranks)]
    if not targets:
        return {"merged": merged, "status": "NO_TARGETS", "targets": [], "attempts": []}
    pf = preflight(True)
    # P-13: 全文選定itemが対象に含まれる場合のみ、数値placeholder型の回避規則を含むgloss規則を使う(A/B/Cの規則・sha無変更)。
    use_ft_rules = any(t.get("fulltext_source_ref") for t in targets)
    rules_text = pf["rules_fulltext"] if use_ft_rules else pf["rules"]
    rules_sha = pf["sha256_fulltext"] if use_ft_rules else pf["sha256"]
    gate = run_alignment_gate_corrected(make_factory_for, targets, article_text, rules_text, mapping_gate=mapping_gate)
    new_merged = apply_alignment_corrected(merged, targets, gate)
    n_unres = len(gate["unresolved_ranks"])
    status = "ALIGN_PASS" if n_unres == 0 else ("ALIGN_FAILED_HUMAN_REVIEW_REQUIRED" if n_unres == len(targets)
                                                else "ALIGN_PARTIAL_HUMAN_REVIEW_REQUIRED")
    total_cost = round(sum(a.get("cost_jpy") or 0 for a in gate["attempts"]), 4)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        for i, msg in enumerate(gate["messages"], 1):
            fn_ = "gloss_alignment_prompt.txt" if i == 1 else f"gloss_alignment_prompt_attempt{i}.txt"
            with open(f"{out_dir}/{fn_}", "w", encoding="utf-8") as f:
                f.write(msg)
        with open(f"{out_dir}/gloss_alignment_runtime_metadata.json", "w", encoding="utf-8") as f:
            json.dump({"article_id": article_id, "version": GLOSS_ALIGNMENT_VERSION,
                       "final_status": status, "targets": [t["rank"] for t in targets],
                       "unresolved_ranks": gate["unresolved_ranks"], "mapping_gate": mapping_gate,
                       "rules_sha256": rules_sha, "cost_jpy": total_cost,
                       "attempts_detail": [{k: v for k, v in a.items() if k != "parsed"} for a in gate["attempts"]],
                       "item_log": {str(k): v for k, v in gate["item_log"].items()}}, f, ensure_ascii=False, indent=2)
    return {"merged": new_merged, "status": status, "targets": [t["rank"] for t in targets],
            "attempts": gate["attempts"], "item_log": gate["item_log"], "unresolved_ranks": gate["unresolved_ranks"],
            "cost_jpy": total_cost, "fallback_event": None, "rules_sha256": rules_sha,
            "model_id": next((a.get("model") for a in gate["attempts"] if a.get("model")), None)}


# ---- 最終artifactに対するHuman Review報告(Lock/queue不使用) ---------------------
def collect_unresolved(kp_json: Any) -> list:
    """永続化済みartifact(keywords_canonicalized.json相当)から、Human Review待ちのitemを返す。
    消費側(TTS関所/stage_kp/assemble前チェック/HR報告)が共通に参照する唯一の関数。
    旧版(-01)が書いた"FAILED"も未解決として扱う(OF-KGCPW-14)。"""
    if not isinstance(kp_json, dict):
        return []
    return [it for it in (kp_json.get("items") or [])
            if isinstance(it, dict) and it.get("gloss_alignment_status") in (STATUS_HR_REQUIRED, STATUS_OLD_FAILED)]


def collect_unevaluated(kp_items: Any) -> list:
    """OF-KGCPW-08(LLM 0・決定論): 再整合の対象(select_alignment_targets)なのにgloss_alignment_statusが無いitem
    =ON化前・未評価のKP成果物。加えて(ITEM1)決定論の人称語突合で不整合のitem(statusにかかわらず。HUMAN_RESOLVEDは除く)。kill switch OFF時は評価対象外のため[]。対象0件の成果物は通過([])。
    kp_itemsはitemのlistまたはartifact dict(items)。"""
    if isinstance(kp_items, dict):
        kp_items = kp_items.get("items")
    if not isinstance(kp_items, list):
        return []
    items = [it for it in kp_items if isinstance(it, dict)]
    if not flag_enabled():
        # KPFT 委任_02: kill switch OFFでもgloss未生成の全文選定itemは通さない(X/Zでは実質『停止スイッチ』。SSOTに明記)。
        return select_fulltext_gloss_missing(items)
    return select_consumer_unevaluated(items)   # ITEM1(F1-1): 消費側の定義(従来 ∪ 人称不整合)。人称一般化item全件は入れない


def build_hr_entries(article_id: str, level: str, unresolved_items: list) -> list:
    entries = []
    for it in unresolved_items:
        info = it.get("gloss_alignment") or {}
        attempts = (info.get("failure") or {}).get("attempts") or []
        reasons = []
        for a in attempts:
            for rs in (a.get("reasons") or []):
                tag = f"attempt{a.get('attempt')}: {rs}"
                if tag not in reasons:
                    reasons.append(tag)
        if not reasons:
            reasons = ["再整合が上限回数で成立しなかった(詳細reasonなし)"]
        proposed = [{"attempt": a.get("attempt"), "proposed_gloss": a.get("proposed_gloss"),
                     "violations": a.get("reasons") or []} for a in attempts if a.get("proposed_gloss")]
        required = added_content_words(it.get("display_phrase"), it.get("key_phrase"))
        missing = []
        for a in attempts:
            for w in ((a.get("machine_check") or {}).get("uncovered") or []):
                if w not in missing:
                    missing.append(w)
        if not missing and not proposed:
            missing = list(required)
        entries.append({
            "article": article_id, "level": level, "rank": it.get("rank"),
            "key_phrase_en": it.get("key_phrase"),
            # KPFT 委任_02: 全文選定でgloss未生成のitemが再整合に失敗した場合、現在glossは空。HR報告書の必須項目検証(非空)でfail-closed例外に
            # ならないよう、空であることを明示する文言を入れる(A/B/Cは従来どおり元のgloss)。
            "current_japanese_gloss": info.get("original_japanese_gloss") or it.get("japanese_gloss") or "(未生成: 全文選定のためgloss無し)",
            "added_content_words": required,
            "failure_reasons": reasons,
            "attempts": attempts,
            "regeneration_candidates": {
                "proposed_glosses": proposed,
                "missing_words": missing,
                "reference_candidate": {"display_phrase": it.get("display_phrase"),
                                        "old_gloss": it.get("japanese_gloss"),
                                        "caution": HR_REFERENCE_CAUTION},
                "kp_regeneration": "既存経路でKey Phraseを再生成する(1レベル1回の運用上限に注意)。人間判断のみ。",
            },
            "resolution_how_to": "resolve_gloss(kp_json_path, rank, gloss, resolved_by) を実行(" + HR_RESOLVE_RUNBOOK + ")",
        })
    return entries


_HR_ENTRY_REQUIRED_STR = ("article", "level", "key_phrase_en", "current_japanese_gloss")


def validate_hr_report(path: str) -> list:
    """HR報告書を**ディスクから再読**し、必須項目が非空であることを検証する。問題のリストを返す(空=OK)。"""
    problems = []
    try:
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
    except Exception as e:
        return [f"読込失敗: {type(e).__name__}: {e}"]
    if not isinstance(doc, dict) or not doc.get("entries"):
        return ["entriesが空/欠落"]
    for i, e in enumerate(doc["entries"]):
        for k in _HR_ENTRY_REQUIRED_STR:
            if not (isinstance(e.get(k), str) and e[k].strip()):
                problems.append(f"entry{i}.{k}が空")
        if not isinstance(e.get("rank"), int):
            problems.append(f"entry{i}.rankが整数でない")
        for k in ("failure_reasons", "attempts"):
            if not (isinstance(e.get(k), list) and e[k]):
                problems.append(f"entry{i}.{k}が空")
        rc = e.get("regeneration_candidates")
        if not isinstance(rc, dict):
            problems.append(f"entry{i}.regeneration_candidatesが無い")
        else:
            for k in ("proposed_glosses", "missing_words", "reference_candidate", "kp_regeneration"):
                if k not in rc:
                    problems.append(f"entry{i}.regeneration_candidates.{k}が無い")
            ref = rc.get("reference_candidate")
            if isinstance(ref, dict) and not ref.get("caution"):
                problems.append(f"entry{i}.reference_candidate.cautionが空")
    return problems


def _render_hr_md(doc: dict) -> str:
    lines = ["# GLOSS_ALIGNMENT_HUMAN_REVIEW", "",
             f"article: {doc['article']} / level: {doc['level']} / generated_at: {doc['generated_at']}", "",
             "KP日本語glossの再整合が上限回数(item単位2回)で成立しませんでした。**対象levelのKP segment(日本語意味・B1解説)は"
             "TTSに進みません(0 API call)。正常完成としても扱われません。** 最終KPは短い候補へ戻していません。",
             "対応: 下の再生成候補から人間が判断し、`resolve_gloss`で確定するか、KPを再生成してください"
             f"(手順: {HR_RESOLVE_RUNBOOK})。", ""]
    for e in doc["entries"]:
        lines += [f"## rank {e['rank']}: {e['key_phrase_en']}", f"- 現在gloss: {e['current_japanese_gloss']}",
                  f"- 追加内容語: {e.get('added_content_words')}", "- 失敗理由:"]
        lines += [f"  - {r}" for r in e["failure_reasons"]]
        lines.append("- 試行結果:")
        for a in e["attempts"]:
            lines.append(f"  - attempt{a.get('attempt')}: verdict={a.get('verdict')} 提案gloss={a.get('proposed_gloss')!r} "
                         f"理由={a.get('reasons')}")
        rc = e["regeneration_candidates"]
        lines.append("- 再生成候補:")
        lines.append(f"  - 提案gloss: {[p['proposed_gloss'] for p in rc['proposed_glosses']]}")
        lines.append(f"  - 欠落語一覧: {rc['missing_words']}")
        ref = rc["reference_candidate"]
        lines.append(f"  - 参考: 候補表現={ref['display_phrase']!r} / 旧gloss={ref['old_gloss']!r} "
                     f"({ref['caution']})")
        lines.append(f"  - KP再生成: {rc['kp_regeneration']}")
        lines.append("")
    return "\n".join(lines)


def emit_human_review_notice(out_dir: str, article_id: str, level: str, kp_json: Any, print_fn: Optional[Callable] = None) -> Optional[dict]:
    """KP段の**最終artifact**に対して1回だけ呼ぶ(OF-KGDC-04)。unresolvedが無ければ古い報告書を除去してNone。
    あれば: 報告書(json+md)を書く -> その場で再読してスキーマ検証 -> 失敗なら例外(fail-closed) -> event生成 -> 専用stdout行。
    戻り値のeventを、呼出元がrun summaryへ載せる(条件②)。条件③(非OKのrun終了status)・④(下流停止)は呼出元と消費側が担う。"""
    unresolved = collect_unresolved(kp_json)
    jpath, mpath = os.path.join(out_dir, HR_REPORT_JSON), os.path.join(out_dir, HR_REPORT_MD)
    if not unresolved:
        for p in (jpath, mpath):
            if os.path.exists(p):
                os.remove(p)   # 最終artifactにunresolvedが無い=過去attempt/過去runの報告書は孤児(OF-KGDC-04)
        return None
    doc = {"report_version": HR_REPORT_VERSION, "article": article_id, "level": level,
           "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
           "entries": build_hr_entries(article_id, level, unresolved)}
    try:
        os.makedirs(out_dir, exist_ok=True)
        with open(jpath, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)
        with open(mpath, "w", encoding="utf-8") as f:
            f.write(_render_hr_md(doc))
        problems = validate_hr_report(jpath)
        if not os.path.exists(mpath) or os.path.getsize(mpath) == 0:
            problems.append("md報告書が空/欠落")
    except GlossAlignmentNotificationError:
        raise
    except Exception as e:
        raise GlossAlignmentNotificationError(f"HR報告書の書込失敗(fail-closed): {type(e).__name__}: {e}") from e
    if problems:
        raise GlossAlignmentNotificationError(f"HR報告書の再読検証に失敗(fail-closed): {problems}")
    with open(jpath, "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest()
    event = {"article": article_id, "level": level, "stage": "kp_gloss_alignment", "reason_code": HR_REASON_CODE,
             "reason": f"gloss再整合がitem単位の上限{MAX_GLOSS_ALIGNMENT_ATTEMPTS}回で成立しなかった"
                       f"(rank={[e['rank'] for e in doc['entries']]})。KPは維持・短い候補へ戻していない",
             "ranks": [e["rank"] for e in doc["entries"]], "report_json": jpath, "report_md": mpath,
             "report_sha256": sha, "report_schema_validated": True,
             "downstream": "当該levelのKP segmentはTTS保留(0 API call、status=" + STOPPED_STATUS + ")。Gateはassemblyを拒否。"
                           "ZはFamilyZE2EStopでstage停止",
             "queue_used": False, "human_review_lock_used": False}
    (print_fn or print)(format_hr_stdout([event]))
    return event


def format_hr_stdout(events: list) -> str:
    if not events:
        return "[GLOSS-ALIGN] Human Review待ちなし"
    ev = events[0] if len(events) == 1 else None
    if ev is not None:
        return (f"[GLOSS-ALIGN][HUMAN-REVIEW-REQUIRED] article={ev['article']} level={ev['level']} ranks={ev['ranks']} "
                f"gloss再整合が成立せず対象KP segmentのTTS/完成を停止します。報告書={ev['report_md']} "
                f"(ユーザーへ必ず報告してください)")
    return "[GLOSS-ALIGN][HUMAN-REVIEW-REQUIRED] " + "; ".join(
        f"article={e['article']} level={e['level']} ranks={e['ranks']} 報告書={e['report_md']}" for e in events)


def resolve_gloss(kp_json_path: str, rank: int, gloss: str, resolved_by: str, now: Optional[str] = None) -> dict:
    """Human Review解消の唯一の手段(OF-KGDC-03)。人間が確定したglossを書き、gloss_alignment_status=HUMAN_RESOLVEDにする。
    承認規則由来の記号チェックを再利用し、違反なら書かずにGlossResolveRejectedを送出する。対象はHR待ち/解消済みitemのみ。"""
    if not isinstance(gloss, str) or not gloss.strip():
        raise GlossResolveRejected("glossが空")
    if not resolved_by or not str(resolved_by).strip():
        raise GlossResolveRejected("resolved_byが空")
    g = gloss.strip()
    bad = []
    if _PAREN_RE.search(g):
        bad.append("括弧禁止違反")
    if _ARABIC_DIGIT_RE.search(g):
        bad.append("算用数字禁止違反")
    if "…" in g:
        bad.append("…禁止違反")
    if safety.symbol_gate_requires_stop(
            [{**f, "rank": rank} for f in safety.detect_prohibited_symbols(kc.convert_display_gloss_to_tts_text(g), language="ja")]):
        bad.append("音声化禁止記号")
    if bad:
        raise GlossResolveRejected(f"gloss不正(書込まない): {bad}")
    with open(kp_json_path, encoding="utf-8") as f:
        doc = json.load(f)
    item = next((it for it in doc.get("items", []) if it.get("rank") == rank), None)
    if item is None:
        raise GlossResolveRejected(f"rank={rank}のitemが無い")
    if item.get("gloss_alignment_status") not in (STATUS_HR_REQUIRED, STATUS_OLD_FAILED, STATUS_HUMAN_RESOLVED):
        raise GlossResolveRejected(f"rank={rank}はHR待ちではない(status={item.get('gloss_alignment_status')!r})。書き換えない")
    prev = item.get("japanese_gloss")
    ts = now or datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    item["japanese_gloss"] = g
    item["japanese_gloss_tts"] = kc.convert_display_gloss_to_tts_text(g)
    item["gloss_alignment_status"] = STATUS_HUMAN_RESOLVED
    item["gloss_review_hint"] = False
    item["gloss_alignment_human_resolution"] = {"resolved_by": str(resolved_by), "resolved_at": ts, "previous_gloss": prev}
    if isinstance(item.get("gloss_alignment"), dict):
        item["gloss_alignment"]["status"] = "GLOSS_HUMAN_RESOLVED"
    if "gloss_alignment_unresolved" in doc:
        remain = [u for u in doc["gloss_alignment_unresolved"] if u.get("rank") != rank]
        if remain:
            doc["gloss_alignment_unresolved"] = remain
        else:
            del doc["gloss_alignment_unresolved"]
    tmp = kp_json_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    os.replace(tmp, kp_json_path)
    log_path = os.path.join(os.path.dirname(kp_json_path), "GLOSS_ALIGNMENT_HUMAN_RESOLUTIONS_01.jsonl")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps({"rank": rank, "key_phrase": item.get("key_phrase"), "previous_gloss": prev, "gloss": g,
                            "resolved_by": str(resolved_by), "resolved_at": ts}, ensure_ascii=False) + "\n")
    return item
