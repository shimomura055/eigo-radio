# -*- coding: utf-8 -*-
"""KP-QUALITY-IMPROVEMENT-2ITEMS-PRODUCTION-01 委任_01 / 項目②: Key Phrase選定の『CMU発音辞書 登録語のみ』必須条件の判定core(**未配線module**)。

Status: WIRED_CODE(委任_02、2026-10-22): er105 `run_selection_gate`(M1)と er003_v1_n3_01_scaffold_generate `run_kp_with_outer_retry`(M2)が本moduleを使う
(X/Z共通=fulltext_p2経路。A/B/C無影響)。ユーザー承認APPROVED_FOR_PRODUCTION(2026-10-22)。本moduleは標準ライブラリと`pronouncing`[=cmudict]のみをimportする。
API呼出0・費用0。R4(縮約clitic分解)は閉集合規則: clitic側は s/d/m/re/ve/t がCMU登録エントリ、ll は単独エントリ無し(base登録で許容。census発火0件)。

ユーザー要件(2026-10-22原文§3)の写像:
  - Key Phrase全体でなく、構成する英単語ごとにCMU登録を確認する。                          -> check_phrase() は語(token)単位
  - 大文字小文字・句読点で登録語を誤除外しない。                                           -> 小文字化・前後句読点除去・複数候補で照合
  - CMU未登録語をLLM推測・外部辞書・発音台帳で代替合格にしない。                           -> 辞書は`pronouncing`(cmudict 1.1.3)のみ。台帳/推測/ASCII化での救済なし
  - 未登録語がある候補は選定時点で除外(別候補を選ぶ)、不足時は条件を緩和しない。          -> 除外判定とnote文言のみ本moduleが担う。再選定/shortfallはer105側(設計書§6)

正規化規則(IMPLEMENTATION_DESIGN_01 §5。順に試し、最初に登録語と一致した経路を採る):
  R0 Unicode NFC・曲線引用符をASCII `'` へ・ダッシュ類を`-`へ・小文字化。**アクセント文字は畳まない**(minaudiereはアクセント付きのまま未登録)。
  R1 前後の句読点を除去(英数字・`'`・`.`・`-`・ラテン文字以外)。前後の`'`と末尾`.`は『保持した形』と『除去した形』の両方を候補にする(`'bout` `players'` `u.s.` `mr.`)。
  R2 語全体を照合。無ければ
  R3 ハイフン/ダッシュ語は分解し、各部分を再帰的に照合(全部分が登録語なら合格。`well-being`は全体で登録済みなら全体で合格)。
  R4 アポストロフィ付きで全体が無ければ、`base'clitic`(clitic = s/d/m/re/ve/ll/t の閉集合)に分解し、**baseがCMU登録語**であること。
  不適合: 英字を1つも含まないtoken(数字のみ・記号のみ)、数字を含み全体が未登録のtoken、上記全て不成立の語。
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Callable, Optional

CHECK_VERSION = "kp_cmu_lexicon_gate_v1"
CLITICS = frozenset({"s", "d", "m", "re", "ve", "ll", "t"})   # 閉集合の英語縮約形(R4)。これ以外の接尾は分解を許さない
_APOS_MAP = {ord(c): "'" for c in "’‘ʼ`´"}
_DASH_MAP = {ord(c): "-" for c in "‐‑‒–—―"}
_EDGE_KEEP = "A-Za-z0-9'.\\-À-ɏ"      # 前後で残す文字(英数字・アポストロフィ・ピリオド・ハイフン・ラテン拡張[アクセントを落とさないため])
_EDGE_RE = re.compile(r"^[^" + _EDGE_KEEP + r"]+|[^" + _EDGE_KEEP + r"]+$")

# 理由コード(監査/ログ用)
R_OK = "ok"
R_EMPTY = "empty"
R_NONWORD = "no_letters"             # 英字を含まない(数字のみ・記号のみ)
R_DIGIT = "contains_digit_unregistered"
R_UNREGISTERED = "unregistered"
R_PART_UNREGISTERED = "part_unregistered"   # ハイフン/縮約の分解後に未登録の部分がある


def _default_lookup(word: str) -> bool:
    """本番が使う`pronouncing`(cmudict.dict の組込み)で登録有無を返す。辞書不備の例外はFalseにせず送出する(fail-closed=呼出側がSTOP)。"""
    import pronouncing   # 遅延import(Production既存: er006_m1_multi_candidate_01.py:69, er008_asr_variant_hardening_15_homophone_en.py:33)
    return bool(pronouncing.phones_for_word(word))


def lexicon_info() -> dict:
    """辞書の実体path/version/登録語数(INVESTIGATION記録・runtime evidence用)。"""
    import importlib.metadata as md
    import os
    import cmudict
    import pronouncing
    pronouncing.init_cmu()
    d = os.path.join(os.path.dirname(cmudict.__file__), "data")
    return {"package_cmudict": md.version("cmudict"), "package_pronouncing": md.version("pronouncing"),
            "cmudict_data_dir": d, "entries": len(pronouncing.pronunciations),
            "lookup": "pronouncing.phones_for_word(lowercase)"}


class CmuLexiconError(RuntimeError):
    """CMU辞書を使えない(import失敗/辞書空)。fail-closed: 呼出側はAPI支出の前に停止する(OF-KPQ-P-05)。"""


_PREFLIGHT_CACHE: dict = {}


def preflight(lookup: Optional[Callable[[str], bool]] = None) -> dict:
    """KP段開始時のCMU辞書確認(API 0)。登録済みの基準語(the/have/phrase)が引けること・entries>0を確認し、`lexicon_info()`を返す(metadataに記録)。
    辞書不備は例外(CmuLexiconError)。lookup注入時(test)は基準語確認のみ。"""
    if lookup is not None:
        for w in ("the", "have"):
            if not lookup(w):
                raise CmuLexiconError(f"CMU lookup sanity failed: {w!r}")
        return {"lookup": "injected"}
    if "info" in _PREFLIGHT_CACHE:
        return dict(_PREFLIGHT_CACHE["info"])
    try:
        info = lexicon_info()
        for w in ("the", "have", "phrase"):
            if not _default_lookup(w):
                raise CmuLexiconError(f"CMU lookup sanity failed: {w!r}")
        if int(info.get("entries") or 0) < 100000:
            raise CmuLexiconError(f"CMU entries too small: {info.get('entries')}")
    except CmuLexiconError:
        raise
    except Exception as e:  # noqa: BLE001  import失敗/辞書欠落
        raise CmuLexiconError(f"CMU lexicon unavailable: {type(e).__name__}: {e}") from e
    _PREFLIGHT_CACHE["info"] = info
    return dict(info)


def normalize_token(tok: str) -> str:
    t = unicodedata.normalize("NFC", tok or "")
    return t.translate(_APOS_MAP).translate(_DASH_MAP).lower()


@dataclass
class WordCheck:
    token: str                 # 入力のまま
    normalized: str            # R0-R1後
    ok: bool
    route: str = ""            # whole / whole_stripped / hyphen_parts / clitic_decomposed
    reason: str = R_OK
    unregistered_parts: list = field(default_factory=list)

    def audit(self) -> dict:
        return {"token": self.token, "normalized": self.normalized, "ok": self.ok, "route": self.route, "reason": self.reason,
                "unregistered_parts": list(self.unregistered_parts)}


def _has_letter(s: str) -> bool:
    return bool(re.search(r"[^\W\d_]", s))


def _check_core(w: str, lookup: Callable[[str], bool], depth: int = 0) -> tuple:
    """w=R0-R1済みの小文字語。returns (ok, route, reason, unregistered_parts)。"""
    if not w:
        return False, "", R_EMPTY, []
    if not _has_letter(w):   # 英字(Unicode letter)が1つも無い
        return False, "", R_NONWORD, [w]
    # R2: 語全体(保持した形 -> 前後の'を除いた形 -> 末尾.を除いた形)
    cands = [w]
    if w.startswith("'") or w.endswith("'"):
        cands.append(w.strip("'"))
    if w.endswith("."):
        cands.append(w.rstrip("."))
    seen = []
    for c in cands:
        if c and c not in seen:
            seen.append(c)
    for i, c in enumerate(seen):
        if lookup(c):
            return True, ("whole" if i == 0 else "whole_stripped"), R_OK, []
    base = w.strip("'").rstrip(".")
    # R3: ハイフン語の分解
    if "-" in base and depth < 3:
        parts = base.split("-")
        if all(parts):
            bad = []
            for p in parts:
                ok, _r, _why, _u = _check_core(p, lookup, depth + 1)
                if not ok:
                    bad.append(p)
            if not bad:
                return True, "hyphen_parts", R_OK, []
            return False, "hyphen_parts", R_PART_UNREGISTERED, bad
        return False, "", (R_UNREGISTERED if _has_letter(base) else R_NONWORD), [base]
    # R4: 縮約形(base'clitic)
    if "'" in base:
        head, _, tail = base.rpartition("'")
        if head and tail in CLITICS:
            if lookup(head):
                return True, "clitic_decomposed", R_OK, []
            return False, "clitic_decomposed", R_PART_UNREGISTERED, [head]
    if re.search(r"\d", base):
        return False, "", R_DIGIT, [base]
    return False, "", R_UNREGISTERED, [base]


def check_word(token: str, lookup: Optional[Callable[[str], bool]] = None) -> WordCheck:
    lookup = lookup or _default_lookup
    n = _EDGE_RE.sub("", normalize_token(token))
    ok, route, reason, bad = _check_core(n, lookup)
    return WordCheck(token=token, normalized=n, ok=ok, route=route, reason=reason, unregistered_parts=bad)


@dataclass
class PhraseCheck:
    phrase: str
    ok: bool
    words: list
    unregistered: list         # 不適合token(入力表記のまま。アクセント等も保持)
    version: str = CHECK_VERSION

    def audit(self) -> dict:
        return {"version": self.version, "phrase": self.phrase, "ok": self.ok, "unregistered": list(self.unregistered),
                "words": [w.audit() for w in self.words]}


def split_words(phrase: str) -> list:
    """スペース区切り(Prompt 2の語数定義と同じ)。空tokenは除く。"""
    return [t for t in (phrase or "").split() if t]


def check_phrase(phrase: str, lookup: Optional[Callable[[str], bool]] = None) -> PhraseCheck:
    """構成する英単語ごとにCMU登録を確認する(Key Phrase全体では判定しない)。空phraseは不適合。"""
    words = [check_word(t, lookup) for t in split_words(phrase)]
    bad = [w.token for w in words if not w.ok]
    return PhraseCheck(phrase=phrase, ok=bool(words) and not bad, words=words, unregistered=bad)


def unregistered_words(phrase: str, lookup: Optional[Callable[[str], bool]] = None) -> list:
    return check_phrase(phrase, lookup).unregistered


def reasons_for_phrase(phrase: str, lookup: Optional[Callable[[str], bool]] = None) -> list:
    """er105 validate_and_resolve の item reasons に追加する文言(空list=適合)。再選定note(機械診断)にそのまま載る。"""
    pc = check_phrase(phrase, lookup)
    if pc.ok:
        return []
    if not pc.words:
        return ["語が無い"]
    return ["CMU発音辞書に登録されていない語を含む(未登録語: " + ", ".join(pc.unregistered)
            + "。構成する全ての語がCMU辞書に登録された語句だけを選ぶ)"]


def partition_items(phrases: list, lookup: Optional[Callable[[str], bool]] = None) -> tuple:
    """(適合index list, 除外[(index, 未登録語list)])。shortfall処理用(最終attemptで除外して残りで確定するときに使う)。"""
    keep, drop = [], []
    for i, p in enumerate(phrases):
        pc = check_phrase(p, lookup)
        if pc.ok:
            keep.append(i)
        else:
            drop.append((i, pc.unregistered))
    return keep, drop


def canonicalized_check(merged_items: list, lookup: Optional[Callable[[str], bool]] = None) -> dict:
    """canonicalization後(基本形化・人称一般化後)の最終KP(`used_form`、無ければ`key_phrase`)をCMUで再確認する(後段検査の1箇所)。
    returns {"ok": bool, "bad": [{"rank", "used_form", "unregistered"}], "checked": n}。1件でも不適合ならok=False(呼出側がINVALID扱い)。"""
    bad = []
    n = 0
    for it in merged_items or []:
        uf = it.get("used_form") or it.get("key_phrase") or ""
        n += 1
        pc = check_phrase(uf, lookup)
        if not pc.ok:
            bad.append({"rank": it.get("rank"), "used_form": uf, "unregistered": pc.unregistered})
    return {"version": CHECK_VERSION, "ok": not bad, "bad": bad, "checked": n}


def build_canonicalized_note(chk: dict) -> str:
    """外側retryの次回選定noteに載せる診断(Prompt 2本文は不変。note欄=本文の後ろ)。"""
    if chk.get("ok"):
        return ""
    lines = [f"- 「{b['used_form']}」(基本形化・一般化後): CMU未登録語 {', '.join(b['unregistered'])}" for b in chk.get("bad", [])]
    return ("前回の選定結果のうち、基本形化・一般化後の語句にCMU発音辞書に登録されていない語が含まれていました。"
            "そのような語を含まない別の語句を選んでください。\n" + "\n".join(lines))


def apply_cmu_to_validation(v: dict, *, final_attempt: bool, min_keep: int = 1, lookup: Optional[Callable[[str], bool]] = None) -> dict:
    """er105 `validate_and_resolve()` の戻り値dict(ok/reasons/item_reasons/resolved)にCMU条件を重ねる純関数(入力dictは変更しない)。
      - 各itemの構成語を語単位で照合し、未登録語があればそのitemのreasonsとv["item_reasons"]へ理由を追加(=ok=False。通常のretry+機械診断noteに載る)。
      - final_attempt(最後のattempt)で、不適合がCMU未登録のitemだけ(他の不適合なし)、かつ残るitemが min_keep 件以上なら、
        未登録itemだけを除外して確定する(shortfall。数合わせ/条件緩和なし)。除外した語句と未登録語は v["cmu_excluded"] に残す。
      - 残りが min_keep 未満、またはCMU以外の不適合が残る場合は ok=False のまま(呼出側は既存どおりINVALID=外側retryへ)。
    returns 新しいdict(元のキー+ "cmu_excluded": [{"index","phrase","unregistered"}])。"""
    out = {k: (list(val) if isinstance(val, list) else val) for k, val in v.items()}
    resolved = [dict(r) for r in v.get("resolved", [])]
    item_reasons = [dict(ir, reasons=list(ir["reasons"])) for ir in v.get("item_reasons", [])]
    by_idx = {ir["index"]: ir for ir in item_reasons}
    cmu_only, cmu_info = set(), []
    for rec in resolved:
        rs = reasons_for_phrase(rec["phrase"], lookup)
        if not rs:
            continue
        had_other = bool(by_idx.get(rec["index"]))
        rec["reasons"] = list(rec.get("reasons", [])) + rs
        rec["cmu_unregistered"] = unregistered_words(rec["phrase"], lookup)
        if rec["index"] in by_idx:
            by_idx[rec["index"]]["reasons"].extend(rs)
        else:
            item_reasons.append({"index": rec["index"], "phrase": rec["phrase"], "reasons": list(rs)})
        if not had_other:
            cmu_only.add(rec["index"])
        cmu_info.append({"index": rec["index"], "phrase": rec["phrase"], "unregistered": rec["cmu_unregistered"]})
    out.update(resolved=resolved, item_reasons=item_reasons, cmu_excluded=[])
    out["ok"] = not out.get("reasons") and not item_reasons
    if final_attempt and not out["ok"] and not out.get("reasons") and cmu_info:
        bad_idx = {ir["index"] for ir in item_reasons}
        if bad_idx <= cmu_only:
            keep = [r for r in resolved if r["index"] not in bad_idx]
            if len(keep) >= min_keep:
                out.update(resolved=keep, item_reasons=[], cmu_excluded=[c for c in cmu_info if c["index"] in bad_idx], ok=True)
    return out
