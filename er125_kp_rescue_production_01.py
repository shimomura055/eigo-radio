# -*- coding: utf-8 -*-
"""KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01 委任_01: Key Phrase Gate除外「救済」方式のProduction module(DESIGN_03)。

ユーザー正式採用(APPROVED_FOR_PRODUCTION 2026-10-26、X/Y/Z共通・Standard/Advanced)の実装。**本委任ではProductionファイルからimportしない(未配線)**。
委任_02で次の4点にだけ配線する(配線仕様=docs/research/KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01/DESIGN_03.md §3):
  H1 er105.contains_finite_aux_role_based  -> idiom_aux_exception_applies(text)
  H2 er105.validate_and_resolve             -> rescue_selection_item(...)         (D1再アンカー / 慣用句の主語除去)
  H3 scaffold.run_key_phrase_canonicalization(rescue=True) -> chain_postprocess / finalize_rescued_items (revert / M1再導出 / gloss再整合 / QA再判定)
  H4 er119.generate_candidates               -> annotate_candidate(cand)           (候補の旗・auto_eligible・rescueメタ)
救済は『品質Gateの緩和』ではない。(a)本文との照合(窓の一意性) (b)承認済みvalidatorを最終Gateと同一引数で再適用 (c)辞書見出し+構造条件による慣用句判定、
のいずれかを満たしたものだけを通す。Human NG(match_ng)は救済経路でも迂回できない(原句・救済形の両方を照合)。
不採用(ユーザー表・Fable解釈): 6語以上の意味のない短縮(A1) / 本文にない語の追加(A2スロット一般化) / CMU未登録語の分解救済。
API: 本module自体は0(QA再判定・gloss再整合はcallable注入。実callは委任_02のevidenceで計測)。

決定論: 同一入力は同一出力(set/dictの反復順に依存しない)。fail-closed: 辞書の欠落/sha不一致/メタ不一致は『救済しない』(例外は送出しない)。
"""
from __future__ import annotations

import contextlib
import contextvars
import copy
import hashlib
import itertools
import json
import logging
import os
import re
import threading
import unicodedata
from typing import Any, Callable, Optional

import er003_key_words_canonicalization as kc
import er105_kp_fulltext_selector_01 as ft          # er105は本moduleを遅延import(関数内)すること(循環回避)
import er108_kp_cmu_lexicon_gate_01 as cmu

log = logging.getLogger("kp_rescue")

ROOT = os.path.dirname(os.path.abspath(__file__))
SCHEMA = "kp_rescue_v1"

# ---- 理由コード(候補のrescue.codesに永続化) -----------------------------------------------------------
R_REVERT = "REVERT_SURFACE"          # keyを表層形(display)へ戻す(時制・活用形が原形化不可)
R_M1 = "REDERIVE_M1_WINDOW"          # display窓内で {display語, LLM提案語} のどちらかを選び直す(rose above->rise above 型)
R_D1 = "REANCHOR_D1"                 # 本文に連続一致しない選定句を、合法な正規化関係にある本文の表層形へ戻す(catch their interest 型)
R_IDIOM_CORE = "IDIOM_CORE_WITHOUT_IT"   # 辞書見出しの核(主語itを除く連続部分列)を選定する(it can't be helped -> can't be helped)
R_IDIOM_AUX = "IDIOM_AUX_EXCEPTION"      # 句は無変更。辞書見出しに一致する助動詞始まりの慣用句として有限助動詞guardの例外を適用(旗のみ)

KILL_SWITCH_ENV = "EIGO_KP_RESCUE"    # 既定ON。"0"のときだけ全hookが無効(従来動作)。承認済み機能の安全停止スイッチ(gloss整合のEIGO_KP_GLOSS_ALIGNMENTと同型)


def rescue_enabled() -> bool:
    """単一の読取関数(既定ON=ユーザー正式採用)。起動script/.envでOFF/ONを暗黙に変えない。"""
    return os.environ.get(KILL_SWITCH_ENV, "1").strip() != "0"


# ---- 文脈限定(Opus M2): H1(有限助動詞guardの例外)とH2(選定段の救済)は、KP候補生成(er119.generate_candidates)の実行中だけ有効。
# 旧経路(er062 run_kp_with_outer_retry_fulltext / er121の旧kp_fnアダプタ / run_selection_gateの他呼出元)では環境変数が既定ONでも発火しない(挙動不変)。
# contextvarは generate_candidates が開始時にセットし終了時(例外含む)に必ず戻す。thread/asyncioへは自動継承しない(KP経路は同一threadで逐次実行)。
_rescue_ctx: contextvars.ContextVar = contextvars.ContextVar("kp_rescue_ctx", default=False)


@contextlib.contextmanager
def rescue_context():
    token = _rescue_ctx.set(True)
    try:
        yield
    finally:
        _rescue_ctx.reset(token)


def rescue_active() -> bool:
    """H1/H2の発火条件 = kill switch未OFF かつ generate_candidates文脈内。"""
    return rescue_enabled() and _rescue_ctx.get()


# =====================================================================================================
# 1. 慣用句辞書(Wiktionary Category:English idioms の見出しのみ。data/kp_idiom_lexicon_01/)
# =====================================================================================================
LEXICON_DIR = os.path.join(ROOT, "data", "kp_idiom_lexicon_01")
LEXICON_FILE = "idioms.txt"
LEXICON_META_FILE = "meta.json"
DENYLIST_FILE = "denylist.txt"
DENYLIST_SHA256 = "5582e366d784a7d31383c68c4c12def6d9adc814c4fd9a0f2b48e5dbfd028fbd"      # 除外表(スラング/侮蔑/方言/出来事特定の決まり文句。レビュー済み)のコード側固定sha(コメント行を除いた正規化済み行をLF連結)
LEXICON_SHA256 = "5ec8f3aee57745064cbf53d6ab23fa20979a743e1dcb1f1300845bc1439327c1"   # コード側の固定値(メタ側と二重ピン。更新は再レビュー必須)
LEXICON_MIN_ENTRIES = 5000          # 極端な欠落(部分書込・切れ)を疑う下限。下回れば空表

_lex_cache: Optional[frozenset] = None
_lex_status: dict = {"loaded": False, "n": 0, "reason": "not_loaded"}


def _hw_norm(s: str) -> str:
    """見出し照合用の正規化: NFKC・曲線引用符->ASCII・小文字・英数字/アポストロフィ/ハイフン以外は空白・空白畳み込み。"""
    s = unicodedata.normalize("NFKC", s or "").replace("’", "'").replace("‘", "'").lower()
    s = re.sub(r"[^a-z0-9'\- ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def _lines_sha(lines: list) -> str:
    return hashlib.sha256(("\n".join(lines) + "\n").encode("utf-8")).hexdigest()


def load_idiom_lexicon(lexicon_dir: Optional[str] = None, expected_sha: Optional[str] = None) -> tuple:
    """returns (frozenset(正規化済み見出し), status dict)。sha256(ファイル行をLF連結)がコード固定値・meta.jsonの両方と一致しなければ空表(fail-closed)。
    CRLF/LF差はsplitlinesで吸収する。例外は送出しない。"""
    d = lexicon_dir or LEXICON_DIR
    want = expected_sha or LEXICON_SHA256
    try:
        with open(os.path.join(d, LEXICON_FILE), encoding="utf-8", newline="") as f:
            lines = [ln for ln in f.read().splitlines() if ln.strip()]
        with open(os.path.join(d, LEXICON_META_FILE), encoding="utf-8") as f:
            meta = json.load(f)
    except Exception as e:   # noqa: BLE001  fail-closed
        return frozenset(), {"loaded": False, "n": 0, "reason": f"read_error:{type(e).__name__}"}
    got = _lines_sha(lines)
    if got != want:
        return frozenset(), {"loaded": False, "n": 0, "reason": "sha_mismatch_code", "sha": got}
    if meta.get("idioms_txt_sha256") != got:
        return frozenset(), {"loaded": False, "n": 0, "reason": "sha_mismatch_meta", "sha": got}
    if len(lines) < LEXICON_MIN_ENTRIES or meta.get("n_titles") != len(lines):
        return frozenset(), {"loaded": False, "n": 0, "reason": "count_mismatch", "sha": got}
    try:
        with open(os.path.join(d, DENYLIST_FILE), encoding="utf-8", newline="") as f:
            deny_lines = [ln.strip() for ln in f.read().splitlines() if ln.strip() and not ln.lstrip().startswith("#")]
    except Exception as e:   # noqa: BLE001  除外表が読めない=安全側(救済しない)
        return frozenset(), {"loaded": False, "n": 0, "reason": f"denylist_read_error:{type(e).__name__}", "sha": got}
    if expected_sha is None and _lines_sha(deny_lines) != DENYLIST_SHA256:
        return frozenset(), {"loaded": False, "n": 0, "reason": "denylist_sha_mismatch", "sha": got}
    deny = {_hw_norm(x) for x in deny_lines}
    ents = frozenset(n for n in (_hw_norm(x) for x in lines) if n and n not in deny)
    return ents, {"loaded": True, "n": len(ents), "reason": "ok", "sha": got, "fetched_at_utc": meta.get("fetched_at_utc")}


def idiom_lexicon() -> frozenset:
    global _lex_cache, _lex_status
    if _lex_cache is None:
        _lex_cache, _lex_status = load_idiom_lexicon()
        if not _lex_status["loaded"]:
            log.warning("kp_rescue: idiom lexicon not loaded (%s) -> idiom exception disabled (fail-closed)", _lex_status["reason"])
    return _lex_cache


def lexicon_status() -> dict:
    idiom_lexicon()
    return dict(_lex_status)


def _reset_lexicon_cache_for_test(value: Optional[frozenset] = None, status: Optional[dict] = None) -> None:
    global _lex_cache, _lex_status
    _lex_cache = value
    _lex_status = status or {"loaded": value is not None, "n": len(value or ()), "reason": "test"}


# ---- 慣用句の構造条件(Opus M3: 名詞主語のことわざ・完全文・疑問文・断片を通さない) -----------------------------
# 先頭語が『主語を持たない述部』を作る法助動詞/助動詞(be系is/are/was/wereは完全文になるため含めない)
_AUX_START = {
    "can": "can", "could": "could", "should": "should", "may": "may", "might": "might", "must": "must", "will": "will", "would": "would",
    "shall": "shall", "can't": "can", "cannot": "can", "couldn't": "could", "won't": "will", "wouldn't": "would", "shouldn't": "should",
    "mustn't": "must", "mightn't": "might", "have": "have", "has": "has", "had": "had", "haven't": "have", "hasn't": "has", "hadn't": "had",
}
_NOMINATIVE = frozenset({"i", "you", "he", "she", "it", "we", "they", "there", "who", "what", "that", "this"})     # 助動詞直後=倒置の疑問文/完全文
_HAVE_FAMILY = frozenset({"have", "has", "had", "haven't", "hasn't", "hadn't"})
_NOMINATIVE_HAVE = frozenset({"i", "you", "he", "she", "we", "they", "there", "who"})     # have it all / have it coming のitは目的語(倒置ではない)
# 学習単位としての中身(content word)を持たない語(助動詞・代名詞・限定詞・前置詞・do/got等)
_FUNCTION = frozenset({
    "be", "been", "being", "is", "are", "was", "were", "am", "do", "does", "did", "got", "get", "not", "n't", "to", "the", "a", "an", "of", "in",
    "on", "at", "for", "with", "by", "from", "as", "and", "or", "but", "it", "its", "i", "you", "he", "she", "we", "they", "him", "her", "them", "us", "me",
    "my", "your", "his", "our", "their", "one", "one's", "someone", "someone's", "somebody", "somebody's", "this", "that", "these", "those", "there",
    "than", "so", "if"})
# 先頭が助動詞でない句のうち、内部に助動詞を含む『come what may』型だけを許す(命令形come+wh語。名詞主語を持つ形は通さない)
_PRE_AUX_OK = frozenset({"come", "what", "whatever", "whoever", "whenever", "wherever", "however"})      # 先頭は必ずcome(what can i say等の疑問節を除く)
_POSS = frozenset({"my", "your", "his", "her", "our", "their", "its", "one's", "someone's", "somebody's"})


def _toks(s: str) -> list:
    return _hw_norm(s).split()


def _variants(tokens: list) -> set:
    """所有格スロット(my/your/his/her/our/their/its/one's/someone's)を one's / someone's に置換した全組合せ + 先頭has/had->have。上限16。"""
    opts = []
    for t in tokens:
        o = {t}
        if t in _POSS:
            o |= {"one's", "someone's"}
        opts.append(sorted(o))
    out = set()
    for combo in itertools.islice(itertools.product(*opts), 16):
        c = list(combo)
        out.add(" ".join(c))
        if c and c[0] in ("has", "had", "having"):
            out.add(" ".join(["have"] + c[1:]))
    return out


def _has_content(tokens_after_first: list) -> bool:
    return any(t not in _FUNCTION for t in tokens_after_first)


def idiom_exception(phrase: str, lex: Optional[frozenset] = None) -> Optional[dict]:
    """phraseが『辞書見出しに一致する、主語を持たない助動詞始まりの慣用表現』か。
    returns None | {"form": "in_place"|"core_without_it", "core": 助動詞始まりの核(正規化済み), "headword": 一致した見出し, "pattern": "aux_start"|"come_wh"}。
    条件(全て): (1)2〜5語 (2)先頭=_AUX_START(be系を除く)または先頭がcome/wh語で最初の助動詞までが_PRE_AUX_OKのみ (3)助動詞直後が主格代名詞/指示詞でない(疑問文・完全文を除く)
    (4)助動詞以外の中身語を1つ以上含む (5)見出しに一致: 核そのもの、または『it+核』(`it can't be helped`の核)。 先頭が`it`の句は核=it以降(主語itの除去のみ許可。
    that/there/名詞主語は除去しない=Opus M3)。lexが空(未ロード/不一致)なら常にNone(fail-closed)。"""
    L = idiom_lexicon() if lex is None else lex
    if not L:
        return None
    toks = _toks(phrase)
    if not (2 <= len(toks) <= 5):
        return None
    form = "in_place"
    core = toks
    if toks[0] == "it" and len(toks) >= 3:
        form, core = "core_without_it", toks[1:]
    pattern = None
    if core[0] in _AUX_START:
        pattern = "aux_start"
        if len(core) < 2 or core[1] in (_NOMINATIVE_HAVE if core[0] in _HAVE_FAMILY else _NOMINATIVE):
            return None
        if not _has_content(core[1:]):
            return None
    else:
        # come what may 型: 先頭からの連続がPRE_AUX_OKで、その次が助動詞
        i = 0
        while i < len(core) and core[i] in _PRE_AUX_OK:
            i += 1
        if i == 0 or i >= len(core) or core[i] not in _AUX_START or form != "in_place" or core[0] != "come":
            return None
        pattern = "come_wh"
    cands = _variants(core) | {"it " + v for v in _variants(core)}
    hit = sorted(c for c in cands if c in L)
    if not hit:
        return None
    return {"form": form, "core": " ".join(core), "headword": hit[0], "pattern": pattern}


def idiom_aux_exception_applies(text: str) -> bool:
    """[H1] 有限助動詞guard(contains_finite_aux_role_based)の例外。句をそのまま(先頭にitを含まない)通してよい場合だけTrue。
    it付きの完全文は例外にしない(核だけを選定段のrescue_selection_itemで救う)。kill switchがOFF、またはgenerate_candidates文脈外(旧経路)ならFalse(M2)。"""
    if not rescue_active():
        return False
    r = idiom_exception(text)
    return bool(r and r["form"] == "in_place")


# =====================================================================================================
# 2. 選定段の救済 [H2]: D1再アンカー / 慣用句の主語除去
# =====================================================================================================
_NOT_CONTIGUOUS_MARK = "本文に連続一致しない"
_AUX_MARK = "有限助動詞"
_WORDCOUNT_MARK = "語数が1〜"
_tls = threading.local()


def reanchor(phrase: str, units: list) -> list:
    """D1: 本文に連続一致しない選定句(LLMが原形で返した等)を、承認済みの原形化validator(find_inflection_window)を逆向きに使い、
    『phraseがその本文窓の合法な正規化形になる』本文窓へ戻す。新しい受理基準は作らない(窓が合法でなければ戻さない)。
    returns [{"surface","sentence","sentence_id"}](表層の小文字で一意化・出現順に依存しない)。"""
    pt = ft._norm_tokens(phrase)
    n = len(pt)
    found = {}
    for u in units:
        raw = u["raw_text"]
        toks = list(ft._TOKEN_RE.finditer(raw))
        for s in range(0, len(toks) - n + 1):
            window = raw[toks[s].start():toks[s + n - 1].end()]
            wt = ft._norm_tokens(window)
            if len(wt) != n:
                continue
            if ft.find_inflection_window(phrase, window) is not None:
                found.setdefault(window.lower(), {"surface": window, "sentence": raw, "sentence_id": u.get("sentence_id")})
    return [found[k] for k in sorted(found)]


def _default_selection_check(phrase: str, units: list) -> list:
    """救済後の句を、選定段の通常検査(本文連続一致・1〜5語・有限助動詞[慣用句例外込み]・数値placeholder)に再度通す。再帰hookは遮断する。"""
    prev = getattr(_tls, "active", False)
    _tls.active = True
    try:
        v = ft.validate_and_resolve([{"phrase": phrase, "declared_word_count": None}], units)
    finally:
        _tls.active = prev
    reasons = [r for ir in v["item_reasons"] for r in ir["reasons"]] + list(v["reasons"] or [])
    # 件数の検査(1件)は呼出側の事情なので除外
    reasons = [r for r in reasons if not r.startswith("件数が")]
    reasons += cmu.reasons_for_phrase(phrase)
    return reasons


def rescue_selection_item(phrase: str, reasons: list, units: list, *, check_fn: Optional[Callable] = None) -> Optional[dict]:
    """[H2] 選定段で除外されたphrase(reasons)に対する救済。救済不能はNone(従来どおり除外=外側retryで別候補)。
    対象は次の2つだけ(それ以外の理由が1つでもあれば救済しない=例: 語数>5の短縮は不採用):
      - 理由が『本文に連続一致しない』のみ -> D1再アンカー(合法な正規化関係にある一意の本文表層形)
      - 理由が『有限助動詞』のみ かつ 先頭がit -> 慣用句の主語除去(核が辞書見出し+構造条件に一致)
    check_fn(phrase)->reasons(空=合格)で救済後の句を再検査する(既定=選定段の通常検査)。再帰呼出しは遮断。
    returns {"phrase", "selection_rescue": {...永続化メタ}} | None。"""
    if not rescue_active() or getattr(_tls, "active", False) or not reasons:
        return None
    check = check_fn or (lambda p: _default_selection_check(p, units))
    kinds = set()
    for r in reasons:
        if _NOT_CONTIGUOUS_MARK in r:
            kinds.add("d1")
        elif _AUX_MARK in r:
            kinds.add("aux")
        else:
            return None        # 語数・文境界・数値placeholder・その他は救済しない(A1短縮/スロット一般化は不採用)
    if kinds == {"d1"}:
        hits = reanchor(phrase, units)
        if len(hits) != 1:
            return None        # 窓なし/複数(曖昧)は救済しない(fail-closed)
        surface = hits[0]["surface"]
        if ft.count_words(surface) != ft.count_words(phrase) or check(surface):
            return None
        code, new_phrase = R_D1, surface
    elif kinds == {"aux"}:
        ex = idiom_exception(phrase)
        toks = _toks(phrase)
        if not ex or ex["form"] != "core_without_it" or not toks or toks[0] != "it":
            return None
        # 核を、元の表層(語順・綴り)のまま本文から切り出す: 先頭のit(+空白)だけを除く
        m = re.match(r"\s*it\s+(.*)$", unicodedata.normalize("NFKC", phrase), flags=re.IGNORECASE | re.DOTALL)
        if not m:
            return None
        core_surface = m.group(1).strip()
        if not core_surface or check(core_surface):
            return None
        code, new_phrase = R_IDIOM_CORE, core_surface
    else:
        return None
    meta = {"schema": SCHEMA, "stage": "selection", "code": code,
            "original_phrase": phrase, "reasons_before": list(reasons), "rescued_phrase": new_phrase,
            "headword": (idiom_exception(phrase) or {}).get("headword") if code == R_IDIOM_CORE else None,
            "lexicon_sha256": LEXICON_SHA256 if code == R_IDIOM_CORE else None}
    log.info("kp_rescue selection %s: %r -> %r", code, phrase, new_phrase)
    return {"phrase": new_phrase, "selection_rescue": meta}


# =====================================================================================================
# 3. canonicalization段の救済 [H3]: revert / M1窓内再導出(API 0・決定論)
# =====================================================================================================
def _norm_lc(s: str) -> list:
    return [t.lower() for t in ft._norm_tokens(s)]


def _gate(key: str, display: str, span: str, original_span: Optional[str], role_ok_poss: frozenset, reason: Optional[str] = None) -> dict:
    """canonicalization最終Gateと同じ引数(allow_inflection_normalization=True, original_span, role_ok_poss)でvalidator+CMUを適用(Opus M6)。"""
    unchanged = _norm_lc(key) == _norm_lc(display)
    nr = reason or ("none" if unchanged else "lemma_normalization")
    v = kc.validate_canonicalization_item(key, display, span, normalization_reason=nr, original_span=original_span or span,
                                          allow_inflection_normalization=True, role_ok_poss=role_ok_poss)
    cm = cmu.reasons_for_phrase(key)
    return {"ok": bool(v["ok"] and not cm), "reasons": list(v["reasons"]) + list(cm), "unchanged": unchanged}


def rederive_m1(display: str, llm_key: str, span: str, original_span: Optional[str], role_ok_poss: frozenset) -> dict:
    """Opus M1: display窓の各tokenを {display側の語, LLMがその位置に出した語} のどちらかから選ぶだけ(新しい語形は作らない)。
    LLM keyがdisplayより長い場合は先頭len(display)語を窓として揃え、はみ出し(窓外tail)を捨てる。短い/語数不一致は再導出不可。
    選択肢はLLM採用語数の多い順(同数はdisplayに近い順=mask辞書順)に最終Gateと同一引数のvalidator+CMUで試す。最後の選択肢=全token display語(revert)。"""
    dt, kt = ft._norm_tokens(display), ft._norm_tokens(llm_key)
    n = len(dt)
    tail = None
    if len(kt) > n:
        tail, kt = kt[n:], kt[:n]
    if len(kt) != n or n == 0:
        return {"ok": False, "why": "llm_key_shorter_or_empty", "tail": tail}
    choices = []
    for mask in itertools.product((1, 0), repeat=n):
        toks = [kt[i] if m else dt[i] for i, m in enumerate(mask)]
        if _norm_lc(" ".join(toks)) == _norm_lc(display) and any(mask):
            continue         # displayと同一になる重複(LLM語==display語)は全0 maskに一本化
        choices.append((sum(mask), mask, toks))
    choices.sort(key=lambda c: (-c[0], c[1]))
    tried = []
    for used, _mask, toks in choices:
        key = " ".join(toks)
        g = _gate(key, display, span, original_span, role_ok_poss)
        tried.append({"key": key, "llm_tokens_used": used, "ok": g["ok"]})
        if g["ok"]:
            return {"ok": True, "key": key, "llm_tokens_used": used, "tail": tail, "tried": tried}
    return {"ok": False, "why": "all_combinations_rejected", "tail": tail, "tried": tried}


def _validator_args(item: dict, key: str, display: str, span: str, original_span: Optional[str], role_ok: frozenset) -> dict:
    return {"key": key, "display": display, "source_span": span, "original_span": original_span,
            "allow_inflection_normalization": True, "role_ok_poss": sorted(role_ok),
            "normalization_reason": "none" if _norm_lc(key) == _norm_lc(display) else "lemma_normalization"}


def args_sha256(args: dict) -> str:
    return hashlib.sha256(json.dumps(args, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def rescue_canonicalization_item(item: dict, original: dict, view_span: str) -> Optional[dict]:
    """1 itemの救済。LLMのkeyが最終Gate(同一引数)で不合格(またはCMU未登録)のときだけ、M1再導出->revertの順で試す。
    成功時は itemを更新して rescueメタ(永続化用)を返す。不能/不要はNone(itemは無変更)。"""
    display = original.get("display_phrase") or original.get("canonical_english") or ""
    key = item.get("key_phrase")
    if not isinstance(key, str) or not key.strip() or not display:
        return None
    role_ok = kc._role_ok_poss_of(item)
    orig_span = original.get("source_span")
    g0 = _gate(key, display, view_span, orig_span, role_ok, item.get("normalization_reason"))
    if g0["ok"]:
        return None
    m1 = rederive_m1(display, key, view_span, orig_span, role_ok)
    if m1["ok"]:
        new_key, used, tail = m1["key"], m1["llm_tokens_used"], m1.get("tail")
    else:
        g = _gate(display, display, view_span, orig_span, role_ok)
        if not g["ok"]:
            return None
        new_key, used, tail = display, 0, m1.get("tail")
    code = R_REVERT if _norm_lc(new_key) == _norm_lc(display) else R_M1
    args = _validator_args(item, new_key, display, view_span, orig_span, role_ok)
    meta = {"schema": SCHEMA, "stage": "canonicalization", "code": code, "display_phrase": display, "llm_key_phrase": key,
            "rescued_key": new_key, "llm_tokens_used": used, "dropped_tail": list(tail or []), "reasons_before": g0["reasons"][:3],
            "validator_args": args, "validator_args_sha256": args_sha256(args)}
    item["key_phrase"] = new_key
    ft._recompute_item_fields(item, display, new_key, role_ok)
    if code != R_REVERT and item.get("normalization_reason") not in ("lemma_normalization", "generalize_person_dependent_reference", "generalize_reference_word"):
        item["normalization_reason"] = "lemma_normalization"      # LLMが『none』と申告していても、救済後keyはdisplayと異なる原形化形
        item["changed_from_display_phrase"] = True
    item["kp_rescue"] = meta
    log.info("kp_rescue canonicalization %s: display=%r llm_key=%r -> %r", code, display, key, new_key)
    return meta


def postprocess_rescue(parsed: dict, original_items: list) -> dict:
    """canonicalization応答(parsed)に対する決定論後処理(API 0)。run_canonicalization_gateのpostprocess hookから呼ばれる。
    入力は破壊しない(deepcopy)。例外時は呼出側(run_canonicalization_gate)が生応答で続行する(現行と同じ)。"""
    out = copy.deepcopy(parsed)
    items = out.get("items") if isinstance(out, dict) else None
    if not isinstance(items, list) or not rescue_enabled():
        return out
    view = {it["rank"]: it.get("source_span", "") for it in kc.canonicalization_view_items(list(original_items or []))}
    by_rank = {it.get("rank"): it for it in (original_items or []) if isinstance(it, dict)}
    for item in items:
        if not isinstance(item, dict):
            continue
        orig = by_rank.get(item.get("rank"))
        if orig is None or not kc.is_fulltext_item(orig):
            continue
        rescue_canonicalization_item(item, orig, view.get(item.get("rank"), ""))
    return out


def chain_postprocess(*fns: Callable) -> Callable:
    """既存のpostprocess(所有格role後処理)の**後ろ**にrescueを連結する(順序固定: roles -> rescue。Opus論点5(i))。"""
    def pp(parsed: dict, original_items: list) -> dict:
        for fn in fns:
            parsed = fn(parsed, original_items)
        return postprocess_rescue(parsed, original_items)
    return pp


# =====================================================================================================
# 4. 救済後の gloss再整合(強制) と QA再判定 [H3・LLMはcallable注入]
# =====================================================================================================
QA_REJUDGED_PASS = "PASS"
QA_REJUDGED_FAIL = "FAIL"
QA_NOT_REJUDGED = "NOT_REJUDGED"
GLOSS_REALIGNED = "REALIGNED"
GLOSS_FAILED = "FAILED"
GLOSS_NOT_RUN = "NOT_RUN"


def force_gloss_realign(merged: dict, ranks: list, article_text: str, make_factory_for: Callable, *, out_dir: Optional[str] = None,
                        article_id: str = "", ga_module: Any = None) -> dict:
    """救済したrankのglossを**強制的に**最終KP基準で再整合する(Opus-01 M3: 通常のselect_generation_targetsは『表示候補に無い語を含む』場合しか
    対象にせず、revertでは対象0件となりLLMが旧key向けに作ったglossが残る)。既存のrun_alignment_gate_corrected/apply_alignment_corrected
    (承認済みgloss規則・Gate)をそのまま使い、対象の選び方だけを置き換える。returns {"merged","status","unresolved_ranks","cost_jpy","targets"}。"""
    ga = ga_module or __import__("er003_key_words_gloss_alignment")
    targets = [it for it in merged["items"] if it["rank"] in set(ranks)]
    if not targets:
        return {"merged": merged, "status": "NO_TARGETS", "unresolved_ranks": [], "cost_jpy": 0.0, "targets": []}
    pf = ga.preflight(True)
    use_ft = any(t.get("fulltext_source_ref") for t in targets)
    rules_text = pf["rules_fulltext"] if use_ft else pf["rules"]
    gate = ga.run_alignment_gate_corrected(make_factory_for, targets, article_text, rules_text, mapping_gate=False)
    new_merged = ga.apply_alignment_corrected(merged, targets, gate)
    cost = round(sum(a.get("cost_jpy") or 0 for a in gate["attempts"]), 4)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        with open(f"{out_dir}/rescue_gloss_realign_metadata.json", "w", encoding="utf-8") as f:
            json.dump({"article_id": article_id, "targets": [t["rank"] for t in targets], "unresolved_ranks": gate["unresolved_ranks"],
                       "cost_jpy": cost}, f, ensure_ascii=False, indent=2)
    return {"merged": new_merged, "status": "ALIGN_PASS" if not gate["unresolved_ranks"] else "ALIGN_UNRESOLVED",
            "unresolved_ranks": list(gate["unresolved_ranks"]), "cost_jpy": cost, "targets": [t["rank"] for t in targets]}


def build_qa_rejudge_message(text: str, items: list, template: Optional[str] = None) -> str:
    """承認済みfulltext canonicalization promptを**無変更**で使う。救済後のkeyを『display_phrase』として渡し、そのkeyを学習単位として
    QA 12項目を判定させる(新しいPromptは作らない)。source_spanは元の本文表層、source_sentenceは元の文。"""
    template = template if template is not None else kc.load_prompt_template(kc.FULLTEXT_PROMPT_TEMPLATE_PATH)
    pseudo = []
    for n, it in enumerate(items, start=1):
        pseudo.append({"rank": n, "display_phrase": it["key_phrase"], "source_span": it.get("source_span", ""),
                       "source_sentence": it.get("source_sentence", "")})
    return kc.build_user_message(pseudo, text, template=template)


def qa_rejudge(text: str, merged_items: list, call_fn: Callable, role_ok_by_rank: Optional[dict] = None) -> dict:
    """救済したmerged itemsのQA 12項目を再判定する(1 call・バッチ)。call_fn(user_message)->(raw_text, model_id, response_id)。
    返却キー=元のrank。LLMが返したkeyが救済後keyと一致しない/QA欄が不正/例外 -> そのrankはNOT_REJUDGED(auto不可)。
    qa_traceable_contiguous_span は実際の(key, display)組で承認済みの有効判定(_qa_field_effective_verdict)に再計算する。
    returns {"model_id","response_id","by_rank": {rank: {"status","qa":{field:verdict}}}}"""
    out = {"model_id": None, "response_id": None, "by_rank": {}}
    if not merged_items:
        return out
    try:
        msg = build_qa_rejudge_message(text, merged_items)
        raw, model_id, response_id = call_fn(msg)
        parsed = kc.parse_canonicalization_json(raw)
    except Exception as e:   # noqa: BLE001  技術失敗 -> 全件NOT_REJUDGED(新しいINVALID/retryは作らない)
        log.warning("kp_rescue qa_rejudge failed: %s: %s", type(e).__name__, e)
        for it in merged_items:
            out["by_rank"][it["rank"]] = {"status": QA_NOT_REJUDGED, "qa": {}, "error": type(e).__name__}
        return out
    out["model_id"], out["response_id"] = model_id, response_id
    by = {x.get("rank"): x for x in (parsed.get("items") or []) if isinstance(x, dict)}
    for n, it in enumerate(merged_items, start=1):
        r = by.get(n)
        rank = it["rank"]
        key = it["key_phrase"]
        if not r or _norm_lc(r.get("key_phrase", "")) != _norm_lc(key) or any(r.get(f) not in kc.QA_VERDICTS for f in kc.QA_FIELDS):
            out["by_rank"][rank] = {"status": QA_NOT_REJUDGED, "qa": {}, "error": "key_mismatch_or_invalid_fields"}
            continue
        role_ok = frozenset((role_ok_by_rank or {}).get(rank) or ())
        qa = {f: kc._qa_field_effective_verdict(f, r[f], key, it.get("display_phrase", ""), it.get("normalization_reason"),
                                                fulltext=True, role_ok_poss=role_ok) for f in kc.QA_FIELDS}
        out["by_rank"][rank] = {"status": QA_REJUDGED_FAIL if any(v == "FAIL" for v in qa.values()) else QA_REJUDGED_PASS, "qa": qa}
    return out


def finalize_rescued_items(merged: dict, parsed: dict, original_items: list, text: str, *, gloss_realign_fn: Optional[Callable] = None,
                           qa_call_fn: Optional[Callable] = None) -> dict:
    """[H3] mergeとgloss再整合の後に呼ぶ。救済itemへ`rescue`メタを付け、canonicalization段の救済rankのgloss強制再整合とQA再判定を行う。
    gloss_realign_fn(merged, ranks)->force_gloss_realign形のdict / qa_call_fn(msg)->(raw,model_id,response_id)。None=その工程は未実施(NOT_RUN/NOT_REJUDGED)。
    返却mergedは入力を破壊しない。救済が無ければ入力をそのまま返す(バイト同一)。"""
    canon_by_rank = {it.get("rank"): it.get("kp_rescue") for it in (parsed or {}).get("items", []) if isinstance(it, dict) and it.get("kp_rescue")}
    sel_by_rank = {it.get("rank"): it.get("selection_rescue") for it in (original_items or []) if isinstance(it, dict) and it.get("selection_rescue")}
    if not canon_by_rank and not sel_by_rank:
        return merged
    out = copy.deepcopy(merged)
    c_ranks = sorted(canon_by_rank)
    gloss_res = {"status": GLOSS_NOT_RUN, "unresolved": []}
    if c_ranks and gloss_realign_fn is not None:
        try:
            r = gloss_realign_fn(out, c_ranks)
            out = r["merged"]
            gloss_res = {"status": GLOSS_REALIGNED if not r["unresolved_ranks"] else GLOSS_FAILED, "unresolved": list(r["unresolved_ranks"]),
                         "cost_jpy": r.get("cost_jpy")}
        except Exception as e:   # noqa: BLE001
            log.warning("kp_rescue gloss realign failed: %s: %s", type(e).__name__, e)
            gloss_res = {"status": GLOSS_FAILED, "unresolved": list(c_ranks), "error": type(e).__name__}
    qa_res = {"by_rank": {}}
    if c_ranks and qa_call_fn is not None:
        qa_res = qa_rejudge(text, [it for it in out["items"] if it["rank"] in set(c_ranks)], qa_call_fn,
                            {r: (canon_by_rank[r].get("validator_args") or {}).get("role_ok_poss") for r in c_ranks})
    for it in out["items"]:
        rank = it["rank"]
        cm, sm = canon_by_rank.get(rank), sel_by_rank.get(rank)
        if not cm and not sm:
            continue
        rec = {"schema": SCHEMA, "codes": [x["code"] for x in (sm, cm) if x], "selection": sm, "canonicalization": cm}
        if cm:
            g_ok = gloss_res["status"] == GLOSS_REALIGNED and rank not in gloss_res["unresolved"]
            rec["gloss"] = {"status": GLOSS_REALIGNED if g_ok else (GLOSS_NOT_RUN if gloss_res["status"] == GLOSS_NOT_RUN else GLOSS_FAILED)}
            q = qa_res["by_rank"].get(rank) or {"status": QA_NOT_REJUDGED, "qa": {}}
            rec["qa"] = {"status": q["status"], "model_id": qa_res.get("model_id"), **({"error": q["error"]} if q.get("error") else {})}
            if q["status"] in (QA_REJUDGED_PASS, QA_REJUDGED_FAIL):
                it["qa"] = dict(q["qa"])
                it["qa_overall_status"] = "REVIEW_REQUIRED" if q["status"] == QA_REJUDGED_FAIL else "PASS"
        it["rescue"] = rec
    return out


# =====================================================================================================
# 5. 候補への反映 [H4]: 旗・gates・auto_eligible・永続化メタ
# =====================================================================================================
def rescue_auto_ok(rescue: Optional[dict], item: Optional[dict] = None) -> bool:
    """救済候補がHRなし(自動採用)経路に入れるか。通常候補(rescueなし)は常にTrue(本関数の対象外)。
    selection段のみの救済(D1/慣用句の核)は後続の通常canonicalizationを通るので追加条件なし。canonicalization段の救済(revert/M1)は
    gloss再整合がREALIGNED かつ QA再判定がPASS のときだけ(Fable設計§4β)。"""
    if not rescue:
        return True
    if not rescue.get("canonicalization"):
        return True
    return (rescue.get("gloss") or {}).get("status") == GLOSS_REALIGNED and (rescue.get("qa") or {}).get("status") == QA_REJUDGED_PASS


def annotate_candidate(cand: dict) -> dict:
    """[H4] generate_candidatesが組み立てた候補dict(item付き)へ、救済の旗・gates・rescueメタを付与し、auto_eligibleを更新する(常にANDのみ=緩めない)。
    rescueなしの候補は、慣用句例外の旗(in-place)を付けるだけで、他は無変更。
    付与: cand["rescue"](永続化メタ=resume時は再計算せず読み戻す) / flags.rescued / flags.rescue_codes / gates.canonicalization(RESCUED_*) / HR表示用 rescue_note。"""
    it = cand.get("item") or {}
    rs = it.get("rescue")
    flags, gates = cand.setdefault("flags", {}), cand.setdefault("gates", {})
    if not rs:
        ex = idiom_exception(cand.get("selection_phrase") or "") if rescue_enabled() else None
        # R1: 旗は『既存の有限助動詞guardが例外なしなら実際に拒否する句』だけに付ける(have a say等の通常通過句には付けない=HRの誤解防止)
        if ex and ex["form"] == "in_place" and ft.contains_finite_aux_role_based_raw(cand.get("selection_phrase") or ""):
            flags["idiom_exception"] = ex["headword"]
        return cand
    cand["rescue"] = copy.deepcopy(rs)
    flags["rescued"] = True
    flags["rescue_codes"] = list(rs.get("codes") or [])
    if rs.get("canonicalization"):
        qs = (rs.get("qa") or {}).get("status")
        gates["canonicalization"] = {QA_REJUDGED_PASS: "RESCUED_QA_REJUDGED_PASS", QA_REJUDGED_FAIL: "RESCUED_QA_REJUDGED_FAIL"}.get(qs, "RESCUED_QA_NOT_REJUDGED")
        gates["gloss"] = "ALIGNED" if (rs.get("gloss") or {}).get("status") == GLOSS_REALIGNED else gates.get("gloss", "HR_PENDING")
    sm, cm = rs.get("selection"), rs.get("canonicalization")
    orig = (sm or {}).get("original_phrase") or (cm or {}).get("display_phrase")
    cand["rescue_note"] = f"修正済み(元: {orig} / {', '.join(rs.get('codes') or [])})" + ("・QA再判定済み" if (rs.get("qa") or {}).get("status") in (QA_REJUDGED_PASS, QA_REJUDGED_FAIL) else "")
    if not rescue_auto_ok(rs, it):
        cand["auto_eligible"] = False
    return cand


def ng_blocked(cand_or_phrases: Any, ng_entries: list, match_ng_fn: Callable, candidate_id_fn: Callable) -> bool:
    """Human NGは救済で復活させない。候補(selection_phrase/used_form)に加え、救済前の元句(selection.original_phrase / canonicalization.display_phrase)も照合する。
    match_ng_fn=er119_kp_human_review_01.match_ng / candidate_id_fn=同candidate_id_for(呼出側が注入。本moduleはer119をimportしない=er119_isolation_testの方針維持)。
    exact一致があればTrue。"""
    c = cand_or_phrases
    if isinstance(c, dict):
        rs = c.get("rescue") or (c.get("item") or {}).get("rescue") or {}
        phrases = [c.get("selection_phrase") or "", (rs.get("selection") or {}).get("original_phrase") or "",
                   (rs.get("canonicalization") or {}).get("display_phrase") or ""]
        used = c.get("used_form") or ""
    else:
        phrases, used = list(c), ""
    for p in phrases:
        if p and match_ng_fn({"candidate_id": candidate_id_fn(p), "selection_phrase": p, "used_form": used}, ng_entries) == "exact":
            return True
    return False


def rescue_blocks_auto(cand: dict) -> bool:
    """救済済みでauto不可(gloss再整合/QA再判定が未達)の候補か。外側retry判定(M3)用。rescueなし=False。"""
    rs = cand.get("rescue")
    return bool(rs) and not rescue_auto_ok(rs)


def ng_match_originals(cand: dict, ng_entries: list, match_ng_fn: Callable, candidate_id_fn: Callable) -> Optional[str]:
    """R6/Human NG: 救済前の元句(selection.original_phrase / canonicalization.display_phrase)をmatch_ngで照合し、'exact'>'similar'>None を返す
    (候補自身のselection_phrase/used_formは呼出側が通常どおり照合済み。元句のsimilarもauto不可にするため)。"""
    rs = cand.get("rescue") or (cand.get("item") or {}).get("rescue") or {}
    best = None
    for p in ((rs.get("selection") or {}).get("original_phrase"), (rs.get("canonicalization") or {}).get("display_phrase")):
        if not p:
            continue
        m = match_ng_fn({"candidate_id": candidate_id_fn(p), "selection_phrase": p, "used_form": ""}, ng_entries)
        if m == "exact":
            return "exact"
        if m == "similar":
            best = "similar"
    return best


def verify_persisted_rescue(cand: dict) -> bool:
    """resume時の整合確認(再計算ではなく読み戻した内容の自己整合)。R4で強化:
    (1) canonicalization段: validator_args_sha256が引数dictと一致 かつ rescued_key == validator_args.key == item.key_phrase(shaは誰でも再計算できるため、
        3者の値一致で手編集の検出力を補う)。 (2) selection段: rescued_phrase == 候補のselection_phrase(正規化比較)。
    不一致=手編集/破損 -> False(呼出側はfail-closedで候補を信用しない)。"""
    rs = cand.get("rescue") or {}
    cm, sm = rs.get("canonicalization"), rs.get("selection")
    if cm:
        va = cm.get("validator_args") or {}
        if args_sha256(va) != cm.get("validator_args_sha256"):
            return False
        item_key = (cand.get("item") or {}).get("key_phrase")
        if not (cm.get("rescued_key") == va.get("key") and (item_key is None or item_key == va.get("key"))):
            return False
    if sm and cand.get("selection_phrase") is not None:
        if _hw_norm(sm.get("rescued_phrase") or "") != _hw_norm(cand.get("selection_phrase") or ""):
            return False
    return True


def reverify_persisted_rescue(cand: dict) -> dict:
    """R4: 保存済みの引数で最終Gate相当のvalidator+CMUを再実行する(決定論・API 0・報告のみ。候補は変更しない)。
    returns {"checked": bool, "ok": bool|None, "reasons": [...]}。canonicalization段の救済がない候補は checked=False。"""
    cm = (cand.get("rescue") or {}).get("canonicalization")
    if not cm:
        return {"checked": False, "ok": None, "reasons": []}
    va = cm.get("validator_args") or {}
    try:
        g = _gate(va["key"], va["display"], va["source_span"], va.get("original_span"), frozenset(va.get("role_ok_poss") or ()),
                  va.get("normalization_reason"))
    except Exception as e:   # noqa: BLE001  報告のみ
        return {"checked": True, "ok": False, "reasons": [f"{type(e).__name__}: {e}"]}
    return {"checked": True, "ok": bool(g["ok"]), "reasons": list(g["reasons"])}


def provenance() -> dict:
    """R2: kp_candidates.jsonのdoc単位に記録する救済の出所(辞書sha・読込状態・有効/無効・schema)。resume時に現在値と比べてドリフトをlogに残す(停止しない)。"""
    st = lexicon_status()
    return {"schema": SCHEMA, "rescue_enabled": rescue_enabled(), "lexicon_sha256": st.get("sha"), "lexicon_status": st.get("reason"),
            "lexicon_n": st.get("n"), "lexicon_pin": LEXICON_SHA256, "denylist_pin": DENYLIST_SHA256}


def provenance_drift(saved: Optional[dict]) -> list:
    """保存済みprovenanceと現在値の差(読み戻し優先のためlogのみ)。救済導入前のdoc(saved=None)は空list。"""
    if not saved:
        return []
    cur = provenance()
    return [f"{k}: saved={saved.get(k)!r} current={cur.get(k)!r}" for k in cur if saved.get(k) != cur.get(k)]
