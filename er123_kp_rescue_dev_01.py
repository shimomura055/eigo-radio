# -*- coding: utf-8 -*-
"""KP-GATE-EXCLUSION-RESCUE-DESIGN-02 委任_01/委任_02: Key Phrase候補Gate除外の「救済」方式 DEV実証モジュール。
委任_02(2026-10-26): Opus独立レビュー(OPUS_REVIEW_02.md)のM1(-ly名詞の誤受理)/M2(have_roleの3類型)/M3(慣用句例外の閉表化)/M4(A2を区分2・非推奨へ)/
  R3(過去形補完から同形異義語を除外)/R4(A1演算子表拡張+HR旗)/R5(縮約形の測定)を反映。

性質: DEV(Production非配線)。Production code(er105/er003_key_words_canonicalization/er003_key_words_min_unit/er119_*/scaffold)は
  一切編集しない。import・読取・in-memory一時差替え(RulePatch、with文で必ず復元)だけを行う。
  RulePatchは『Productionへ入れる場合の修正差分案』を同一のvalidator関数に当てて効果を測るための机上装置であり、
  Production挙動は変えない(処理後に元へ戻す。test_rule_patch_restoresで固定)。
API: 既定0(socket.connectを例外化)。--judge指定時のみ(.venvのpythonから)LLM評価callを許可。

パターンと区分(docs/research/KP-GATE-EXCLUSION-RESCUE-DESIGN-02/PATTERN_DESIGN_01.md):
  A 語数超過   : A1 連続部分列短縮(現行規則内) / A2 スロット一般化(新規則=区分2)
  B 原形化     : 三重検査(LLM提案語+CMU実在+活用の前方生成一致)+文脈条件。guard拡張(量化詞/副詞=区分1、辞書裏付け=区分2)
  C 助動詞誤判定: 役割判定(lexical have) = 区分1 / 慣用句の法助動詞=辞書裏付けの例外(区分2)
  D その他     : D1 本文近傍への再アンカー / D2 CMU派生語(接頭辞+登録基底語) / D3 閉表網羅(過去形専用表) / Human NG=救済しない

Usage:
  py er123_kp_rescue_dev_01.py --inventory <inventory_01.json> --out <rescue_eval_0N.json> --md <RESCUE_TABLE_0N.md> [--tag N]
  py er123_kp_rescue_dev_01.py --selection-probe <out.json> | --have-probe <out.json> | --gap-report <out.json>
  py er123_kp_rescue_dev_01.py --finalize <rescue_eval.json> --judge-json a.json,b.json,c.json --out <final.json> --final-md <final.md>
  .venv\\Scripts\\python.exe er123_kp_rescue_dev_01.py --judge <rescue_eval.json> --budget-jpy 30 --out <judge.json>
"""
from __future__ import annotations

import argparse
import copy
import glob
import itertools
import json
import os
import re
import socket
import sys
import unicodedata

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
_VENV_SP = os.path.join(ROOT, ".venv", "Lib", "site-packages")
if os.path.isdir(_VENV_SP):
    sys.path.append(_VENV_SP)


def _blocked(*a, **k):
    raise RuntimeError("network blocked: KP-GATE-EXCLUSION-RESCUE-DESIGN-02 DEV module is API-0 (except --judge)")


if "--judge" not in sys.argv and "--judge-headword" not in sys.argv:
    socket.socket.connect = _blocked          # type: ignore[assignment]
    socket.create_connection = _blocked       # type: ignore[assignment]

import er003_key_words_canonicalization as kc   # noqa: E402  決定論validator(読取・呼出のみ)
import er105_kp_fulltext_selector_01 as ft      # noqa: E402
import er108_kp_cmu_lexicon_gate_01 as cmu      # noqa: E402

FAMILY_OF = {"er019_output": "X", "er026_output": "Z", "er121_output": "Y"}

# =====================================================================================================
# 1. 語彙資源: 不規則動詞マスタ(過去形・過去分詞)と前方活用生成 / 辞書(Wiktionary idioms・phrasal verbs・proverbs, 既存ローカル)
# =====================================================================================================
# lemma: (過去形, 過去分詞)。標準的な不規則動詞(be/have/doはft._FUNCTION_VERB_FORMSで別管理)。
IRR = {
    "arise": ("arose", "arisen"), "awake": ("awoke", "awoken"), "bear": ("bore", "borne"), "beat": ("beat", "beaten"),
    "become": ("became", "become"), "begin": ("began", "begun"), "bend": ("bent", "bent"), "bind": ("bound", "bound"),
    "bite": ("bit", "bitten"), "bleed": ("bled", "bled"), "blow": ("blew", "blown"), "break": ("broke", "broken"),
    "breed": ("bred", "bred"), "bring": ("brought", "brought"), "build": ("built", "built"), "buy": ("bought", "bought"),
    "catch": ("caught", "caught"), "choose": ("chose", "chosen"), "cling": ("clung", "clung"), "come": ("came", "come"),
    "creep": ("crept", "crept"), "deal": ("dealt", "dealt"), "dig": ("dug", "dug"), "draw": ("drew", "drawn"),
    "drink": ("drank", "drunk"), "drive": ("drove", "driven"), "eat": ("ate", "eaten"), "fall": ("fell", "fallen"),
    "feed": ("fed", "fed"), "feel": ("felt", "felt"), "fight": ("fought", "fought"), "find": ("found", "found"),
    "flee": ("fled", "fled"), "fling": ("flung", "flung"), "fly": ("flew", "flown"), "forbid": ("forbade", "forbidden"),
    "forget": ("forgot", "forgotten"), "forgive": ("forgave", "forgiven"), "freeze": ("froze", "frozen"),
    "get": ("got", "gotten"), "give": ("gave", "given"), "go": ("went", "gone"), "grind": ("ground", "ground"),
    "grow": ("grew", "grown"), "hang": ("hung", "hung"), "hear": ("heard", "heard"), "hide": ("hid", "hidden"),
    "hold": ("held", "held"), "keep": ("kept", "kept"), "kneel": ("knelt", "knelt"), "know": ("knew", "known"),
    "lay": ("laid", "laid"), "lead": ("led", "led"), "leave": ("left", "left"), "lend": ("lent", "lent"),
    "lie": ("lay", "lain"), "light": ("lit", "lit"), "lose": ("lost", "lost"), "make": ("made", "made"),
    "mean": ("meant", "meant"), "meet": ("met", "met"), "overcome": ("overcame", "overcome"), "pay": ("paid", "paid"),
    "ride": ("rode", "ridden"), "ring": ("rang", "rung"), "rise": ("rose", "risen"), "run": ("ran", "run"),
    "say": ("said", "said"), "see": ("saw", "seen"), "seek": ("sought", "sought"), "sell": ("sold", "sold"),
    "send": ("sent", "sent"), "shake": ("shook", "shaken"), "shine": ("shone", "shone"), "shoot": ("shot", "shot"),
    "show": ("showed", "shown"), "shrink": ("shrank", "shrunk"), "sing": ("sang", "sung"), "sink": ("sank", "sunk"),
    "sit": ("sat", "sat"), "sleep": ("slept", "slept"), "slide": ("slid", "slid"), "speak": ("spoke", "spoken"),
    "spend": ("spent", "spent"), "spin": ("spun", "spun"), "spring": ("sprang", "sprung"), "stand": ("stood", "stood"),
    "steal": ("stole", "stolen"), "stick": ("stuck", "stuck"), "sting": ("stung", "stung"), "strike": ("struck", "struck"),
    "swear": ("swore", "sworn"), "sweep": ("swept", "swept"), "swim": ("swam", "swum"), "swing": ("swung", "swung"),
    "take": ("took", "taken"), "teach": ("taught", "taught"), "tear": ("tore", "torn"), "tell": ("told", "told"),
    "think": ("thought", "thought"), "throw": ("threw", "thrown"), "understand": ("understood", "understood"),
    "undertake": ("undertook", "undertaken"), "wake": ("woke", "woken"), "wear": ("wore", "worn"), "weave": ("wove", "woven"),
    "weep": ("wept", "wept"), "win": ("won", "won"), "wind": ("wound", "wound"), "withdraw": ("withdrew", "withdrawn"),
    "write": ("wrote", "written"),
}
# 過去形が名詞・形容詞・別語としても通用する語(過去形専用表には入れず、直後条件つきのAMBIGUOUS表へ)
# OPEN-476=DEFERRED(er105 is_valid_inflection_normalization docstring: bound to->bind to は拒否のまま)。補完の対象から除外する。
# R3(Opus): 他の動詞の原形/名詞と同形になる新規追加語は補完しない(bound/lay/wound/ground/bore。`bound`を外したのと同じ理由)。
COMPLETION_EXCLUDE = frozenset({"bound", "lay", "wound", "ground", "bore"})
PAST_ALSO_OTHER_WORD = frozenset({
    "saw", "left", "found", "bound", "wound", "lay", "bore", "rose", "felt", "spoke", "stole", "bit", "shot", "won",
    "stuck", "struck", "hung", "bent", "spent", "ground", "lit", "fell", "led", "sat", "bled", "fed", "laid", "dug", "lent",
})
# M2(Opus): 形が変わらない/不規則な過去分詞で表に無かった語(has spread/quit/cast/cost/burst/shed/split/upset/bet/forecast/broadcast/bid/fit/rid/wed、
#   dwelt/leapt/wrung/strode/stunk ほか)。2語の句は nxt2=None になり倒置ルールにも掛からないため、nxt自身を分詞として認識する。迷えばaux側。
IRR_PARTICIPLES_EXTRA = frozenset({
    "spread", "quit", "cast", "cost", "burst", "shed", "split", "upset", "bet", "forecast", "broadcast", "bid", "fit", "rid", "wed",
    "dwelt", "leapt", "wrung", "strode", "stunk", "bust", "slit", "thrust", "sublet", "typeset", "offset", "reset", "outbid", "overcast",
    "recast", "underbid", "unwound", "spat", "slung", "slunk", "snuck", "strung", "leant", "dived", "dove", "spoilt", "wound", "ground",
    "bore", "laid", "lain", "bled", "fled", "sped", "stove", "clad", "shod", "woven", "hewn", "mown", "rent", "bereft", "dealt", "meant",
    "overrun", "outrun", "overthrown", "withstood", "forborne", "foregone", "foresaw", "foreseen", "overseen", "outdone", "overtaken",
    "retaken", "remade", "regrown", "reborn", "reheard", "rebound", "unbound", "unbent", "underlain", "underwritten", "unfrozen"})
IRR_PARTICIPLES = frozenset(p for _, p in IRR.values()) | IRR_PARTICIPLES_EXTRA | frozenset({
    "got", "been", "done", "had", "put", "cut", "set", "let", "hit", "hurt", "read", "shut",
    # IRRマスタ外の過去分詞(完了形のauxを語彙haveと誤認しないための追加。迷えばaux側=現行どおり拒否)
    "proven", "learnt", "burnt", "dreamt", "spelt", "spilt", "smelt", "sped", "knit", "forsaken", "mistaken", "overtaken", "undergone",
    "outgrown", "slain", "striven", "trodden", "sewn", "sown", "shorn", "swollen", "stricken", "begotten", "beheld", "upheld", "withheld",
    "misled", "overdone", "undone", "redone", "rebuilt", "retold", "rewritten", "bidden", "wrought", "come", "become", "run", "gone"})

_VOWELS = "aeiou"


def _cvc(w: str) -> bool:
    return len(w) >= 3 and w[-1] not in _VOWELS + "wxy" and w[-2] in _VOWELS and w[-3] not in _VOWELS


def _doubling_options(l: str) -> tuple:
    """CVC語の重子音化: (重子音形を許す?, 非重子音形を許す?)。単音節/語末強勢→重子音(hop->hopped, plan->planned, prefer->preferred)、
    語末が無強勢→非重子音(visit->visited, open->opened)。CMUに無ければ両方許す。hoped->hop のような誤受理を前方生成一致で拒否するための判定。"""
    try:
        import pronouncing
        prons = pronouncing.phones_for_word(l)
    except Exception:   # noqa: BLE001
        prons = []
    if not prons:
        return True, True
    dbl = plain = False
    for pr in prons:
        vs = [x for x in pr.split() if x[-1].isdigit()]
        if not vs:
            continue
        if len(vs) == 1 or vs[-1].endswith("1"):
            dbl = True
        else:
            plain = True
    return (dbl or not plain), (plain or not dbl)


def regular_forms(lemma: str) -> set:
    """規則活用の前方生成(-s/-es/-ies, -ed/-d/-ied, -ing)。CVC語は重子音あり/なし両方(強勢未判定のため緩め=受理側の誤り防止ではなく『一致確認』用)。"""
    l = lemma.lower()
    out = set()
    # 3sg
    if re.search(r"(s|x|z|ch|sh|o)$", l):
        out.add(l + "es")
    elif re.search(r"[^aeiou]y$", l):
        out.add(l[:-1] + "ies")
    else:
        out.add(l + "s")
    # past / participle
    if l.endswith("e"):
        out.add(l + "d")
    elif re.search(r"[^aeiou]y$", l):
        out.add(l[:-1] + "ied")
    elif _cvc(l):
        dbl, plain = _doubling_options(l)
        if dbl:
            out.add(l + l[-1] + "ed")
        if plain:
            out.add(l + "ed")
    else:
        out.add(l + "ed")
    # gerund
    if l.endswith("ie"):
        out.add(l[:-2] + "ying")
    elif l.endswith("e") and not l.endswith(("ee", "ye", "oe")):
        out.add(l[:-1] + "ing")
    elif _cvc(l):
        dbl, plain = _doubling_options(l)
        if dbl:
            out.add(l + l[-1] + "ing")
        if plain:
            out.add(l + "ing")
    else:
        out.add(l + "ing")
    return out


def forms(lemma: str) -> set:
    """lemmaの活用形全体(前方生成)。不規則動詞は過去形・過去分詞をIRRから、3sg/gerundは規則形。"""
    l = lemma.lower()
    rf = regular_forms(l)
    if l in IRR:
        past, pp = IRR[l]
        rf = {f for f in rf if not f.endswith(("ed", "ied"))} | {past, pp}
    if l in ("be", "have", "do"):
        rf |= {"be": {"is", "are", "was", "were", "been", "being", "am"}, "have": {"has", "had", "having"},
               "do": {"does", "did", "done", "doing"}}[l]
    return rf


def inflects_to(lemma: str, surface: str) -> bool:
    """前方生成一致: surfaceがlemmaの活用形か(`hoped`->`hop`は偽、`hoped`->`hope`は真)。"""
    return surface.lower() in forms(lemma)


def irregular_gap_report() -> dict:
    """ft の閉表(過去形専用/曖昧不規則)に無い不規則形の網羅漏れ。lemma毎に過去形・過去分詞の別を出す。"""
    have = set(ft._PAST_ONLY_IRREGULAR) | set(ft._AMBIGUOUS_IRREGULAR)
    gaps_past_only, gaps_ambiguous, gaps_pp = [], [], []
    for lemma, (past, pp) in sorted(IRR.items()):
        if past in COMPLETION_EXCLUDE or pp in COMPLETION_EXCLUDE or (past in IRR and past != lemma) or (pp in IRR and pp != lemma):
            continue
        if past != lemma and past != lemma + "ed" and past not in have and past not in ft._FUNCTION_VERB_FORMS:
            (gaps_ambiguous if past in PAST_ALSO_OTHER_WORD else gaps_past_only).append((past, lemma))
        if pp not in (past, lemma) and pp not in have:
            gaps_pp.append((pp, lemma))
    return {"missing_past_only_candidates": gaps_past_only, "missing_past_ambiguous_candidates": gaps_ambiguous,
            "missing_participle_forms": gaps_pp,
            "existing_tables": {"past_only": len(ft._PAST_ONLY_IRREGULAR), "ambiguous": len(ft._AMBIGUOUS_IRREGULAR)}}


_LEX = None


def _lex_norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s or "").replace("’", "'").lower()
    return re.sub(r"\s+", " ", s).strip()


def lexicon() -> frozenset:
    """Wiktionary Category(English idioms / phrasal verbs / proverbs)のタイトル一覧(既存ローカル資産、API 0)。"""
    global _LEX
    if _LEX is None:
        base = os.path.join(ROOT, "er023_output", "key_phrase_db_trial_01", "db", "wiktionary")
        titles = set()
        for fn in ("idioms", "phrasal_verbs", "proverbs"):
            p = os.path.join(base, fn + ".json")
            if os.path.exists(p):
                titles |= {_lex_norm(t) for t in json.load(open(p, encoding="utf-8")).get("titles", [])}
        _LEX = frozenset(titles)
    return _LEX


_LEX_CORES = None


def lexicon_cores() -> frozenset:
    global _LEX_CORES
    if _LEX_CORES is None:
        _LEX_CORES = frozenset(t.split(" ", 1)[1] for t in lexicon() if t.startswith(("it ", "that ")) and len(t.split()) >= 4)
    return _LEX_CORES


def lex_hit(phrase: str) -> dict:
    """phraseがlexiconの見出しに一致するか。one's/someone's表記ゆれと先頭のit/thatを許す(完全一致が基本)。"""
    p = _lex_norm(phrase)
    cands = {p, p.replace("someone's", "one's"), p.replace("one's", "someone's")}
    if p.startswith(("it ", "that ")):
        cands.add(p.split(" ", 1)[1])
    L = lexicon()
    # 見出しが『it/that + 核』のとき、主語(ダミー主語it)を除いた核(例: can't be helped)も同一見出しの核として許す
    hit = [c for c in cands if c in L or c in lexicon_cores()]
    # 見出しの末尾部分列(先頭のit/one等を除いた形)かどうか(参考情報)
    sup = [t for t in L if t.endswith(" " + p) and len(t.split()) <= len(p.split()) + 1][:3] if not hit else []
    return {"hit": bool(hit), "entry": hit[0] if hit else None, "longer_entry_containing_as_suffix": sup}


# =====================================================================================================
# 2. 役割判定: 有限助動詞 vs 語彙動詞 have(区分1) / 慣用句の法助動詞(区分2)
# =====================================================================================================
_ORIG_FINITE_AUX = frozenset(kc._FINITE_AUX_WORDS)      # 承認済み仕様(section 12)の語形リスト(実装)
_HAVE = frozenset({"has", "have", "had"})
_NOM_PRONOUN = frozenset({"i", "you", "he", "she", "it", "we", "they", "there", "who"})   # have + 主格代名詞=倒置の助動詞(You/Itは保守的にaux側)
_AUX_FOLLOW = frozenset({"been", "being", "to", "not", "t", "n't", "never", "already", "just", "ever", "better", "rather", "best", "got"})


_NOT_PARTICIPLE_ED = frozenset({"hundred", "kindred", "sacred", "naked", "wicked", "rugged", "crooked", "beloved", "wretched", "hatred", "infrared"})   # -edで終わるが分詞でない語


def _is_participle(w: str) -> bool:
    return w in IRR_PARTICIPLES or (w.endswith("ed") and len(w) > 3 and w not in ft._PARTICIPIAL_ADJ_EXCLUDE and w not in _NOT_PARTICIPLE_ED)


_HAVE_ADV = frozenset({"also", "often", "only", "finally", "just", "already", "ever", "never", "always", "still", "quite", "really", "soon",
                       "recently", "previously", "yet", "long", "so"})
_LEXICAL_START = frozenset(set(ft._GUARD_DET) | {"no", "each", "every", "all", "both", "another", "either", "neither", "several", "few", "many",
                                                 "much", "more", "less", "enough", "what", "something", "nothing", "anything", "everything"})


# M2(Opus): 助動詞と分詞の間に入りうる量化詞・副詞(have all gone / have both agreed / has more than doubled / have just been)。
_HAVE_SKIP = frozenset({"all", "both", "each", "either", "neither", "more", "less", "than", "much", "many", "few", "several", "most", "half",
                        "just", "already", "also", "never", "ever", "only", "still", "always", "often", "finally", "recently", "previously",
                        "yet", "really", "quite", "so", "long", "now", "then", "once", "twice", "nearly", "almost", "barely", "hardly", "all"})
_HAVE_DET_SET = frozenset(ft._GUARD_DET) | {"the", "a", "an"}


def have_role(toks: list, i: int, capitalized_first: bool = False) -> str:
    """have/has/had(toks[i])が『aux』(完了・倒置・慣用の助動詞用法)か『lexical』(所有・経験・実行の語彙動詞)か。
    保守的: 判定に迷えばaux(=現行どおり拒否)。lexicalと判定するのは、直後が限定詞/所有格/数量詞/名詞句の始まりで、かつ
    (1)文頭の大文字Have/Has/Had(倒置・疑問)でない (2)直後に副詞+過去分詞が続かない (3)『have+主語+been/過去分詞』の倒置でない
    (4)[M2] 量化詞/副詞を挟んだ『have all gone』『has more than doubled』でない (5)[M2] 形が変わらない過去分詞(has spread/quit/cast/cost…)でない
    (6)[M2] 限定詞(+形容詞)+名詞+過去分詞(had the board known / had the house painted は形が同じで区別不能→aux)でない 場合のみ。"""
    nxt = toks[i + 1] if i + 1 < len(toks) else None
    nxt2 = toks[i + 2] if i + 2 < len(toks) else None
    if capitalized_first and i == 0 and nxt is not None:
        return "aux"
    if nxt is None:
        return "aux"
    if nxt in _AUX_FOLLOW or nxt in _NOM_PRONOUN or nxt in _HAVE_ADV:
        return "aux"
    if _is_participle(nxt):
        return "aux"
    if nxt in ft._PARTICIPIAL_ADJ_EXCLUDE:
        # 形容詞化もしうる分詞(limited/interested/expected等): 直後が限定詞/前置詞(=目的語を取る完了形)・句末ならaux、名詞が続くときだけ形容詞=語彙have
        if nxt2 is None or nxt2 in ft._GUARD_DET or nxt2 in ft._GUARD_PARTICLE:
            return "aux"
        return "lexical"
    # (4) 量化詞/副詞を読み飛ばして、その先が分詞/been/beingならaux(have all gone / has more than doubled)
    j = i + 1
    skipped = False
    while j < len(toks) and toks[j] in _HAVE_SKIP:
        j += 1
        skipped = True
    if skipped and j < len(toks):
        w = toks[j]
        if w in ("been", "being") or _is_participle(w) or w in ft._PARTICIPIAL_ADJ_EXCLUDE or (w.endswith("ed") and len(w) > 3):
            return "aux"
    if skipped and j >= len(toks) and toks[-1] in _HAVE_SKIP and toks[-1] not in ("all", "both", "each", "either", "neither", "most", "half",
                                                                                     "many", "few", "several", "much", "more", "less", "than"):
        return "aux"      # have just / have already 等の副詞止まり(分詞が切れている)
    # (6) 限定詞(+形容詞)+名詞+過去分詞: had the board known / had the house painted → aux(倒置/使役の区別不能)
    if nxt in _HAVE_DET_SET:
        for k in (i + 3, i + 4):
            if k < len(toks) and (toks[k] in ("been", "being") or _is_participle(toks[k])):
                return "aux"
    if nxt not in _LEXICAL_START and nxt2 is not None and (nxt2 in ("been", "being") or _is_participle(nxt2)):
        return "aux"       # have + 主語(名詞) + been/過去分詞 = 倒置の助動詞(Had users been / Has Vera been)
    return "lexical"


def finite_aux_roles(text: str) -> list:
    orig = kc._WORD_TOKEN_RE.findall(text or "")
    toks = [t.lower() for t in orig]
    out = []
    for i, t in enumerate(toks):
        if t in _ORIG_FINITE_AUX:
            out.append((t, have_role(toks, i, capitalized_first=orig[i][:1].isupper()) if t in _HAVE else "aux"))
    return out


def contains_finite_aux_role_based(text: str) -> bool:
    return any(role == "aux" for _, role in finite_aux_roles(text))


_SUBJ_START = frozenset({"it", "that", "this", "there", "i", "you", "he", "she", "we", "they"})

# ---- M3(Opus): 慣用句の法助動詞/助動詞例外は『レビュー済みの小さな閉表』に限る。
#  対象= idioms由来(proverbs/phrasal verbs除外)かつ『先頭語が法助動詞/助動詞(主語の無い述部)』の句(+『it/that+核』見出しの主語を除いた核)。
#  名詞主語のことわざ・完全文(beggars can't be choosers / boys will be boys / time is money / the die is cast / a leopard can't change its spots)は
#  先頭が助動詞でないため例外にならない。閉表は実行時に外部データ(Wiktionary 17,389見出し)を照会せず、下記JSON(sha256固定)だけを使う。
IDIOM_TABLE_PATH = os.path.join(ROOT, "docs", "research", "KP-GATE-EXCLUSION-RESCUE-DESIGN-02", "idiom_closed_table_01.json")
IDIOM_TABLE_SHA256 = "0fb89833d0e0548102b758bad1af15a6fc3fffe866cdd27c86dec4c21cefa3aa"      # entriesをsortedし改行連結したsha256。不一致なら閉表は空(例外なし=fail-closed)
_AUX_FIRST = {"is": "is", "are": "are", "was": "was", "were": "were", "has": "has", "have": "have", "had": "had", "will": "will", "would": "would",
              "can": "can", "could": "could", "should": "should", "may": "may", "might": "might", "must": "must",
              "can't": "can", "cannot": "can", "couldn't": "could", "won't": "will", "wouldn't": "would", "shouldn't": "should", "mustn't": "must",
              "isn't": "is", "aren't": "are", "wasn't": "was", "weren't": "were", "hasn't": "has", "haven't": "have", "hadn't": "had", "mightn't": "might"}
_POSS_TO_ONES = {"my": "one's", "your": "one's", "his": "one's", "her": "one's", "our": "one's", "their": "one's", "its": "one's"}
_HAVE_TO_BASE = {"has": "have", "had": "have", "having": "have"}

# 機械抽出した候補のうち採用(include)する見出し(レビュー結果)。理由はIDIOM_REVIEW_EXCLUDE_REASONに残す。
IDIOM_REVIEW_INCLUDE = frozenset({
    "can of corn", "can of worms", "could not get elected dogcatcher", "had better", "have been around", "have done with", "have had it",
    "have it all", "have it both ways", "have it coming", "have it made", "have it your way", "have one's hands tied", "have one's head read",
    "have one's ears pinned back", "have seen one's day", "may as well", "might as well",
    "can't get enough", "can't help", "can't stand", "can't stand the sight of", "can't wait", "couldn't be more different",
    "couldn't care less", "wouldn't be seen dead", "can't be helped"})      # 最後は『it can't be helped』の主語を除いた核
IDIOM_REVIEW_EXCLUDE_REASON = {
    "完全文/疑問文(主語を持つ節)": ["are bears catholic", "are you deaf", "are your ears burning", "is a bear catholic", "is what it is", "is a new sheriff in town",
                              "wouldn't you know", "wouldn't you say", "will the real someone please stand up", "were you born in a tent"],
    "語彙動詞can等の曖昧/断片(単独では学習単位でない)": ["can it", "have", "would", "have got", "will do", "have it in one"],
    "スラング/方言/侮蔑的/古風で学習価値が低い(レビューで除外)": ["have it large", "have it going on", "have one's ears lowered", "have one's wig snatched", "have had one's chips",
                                          "have fingers made of lime-twigs", "would give a jew's eye", "has left the building", "have seen this movie",
                                          "have one's name taken"],
    "主語(there等)を要する構文の核/語数・未完": ["is no telling", "is no there there", "must be something in the water", "couldn't happen to a nicer"]}


def _first_aux_word(toks: list) -> str | None:
    return _AUX_FIRST.get(toks[0]) if toks else None


def build_idiom_candidates() -> list:
    """機械抽出(DEV専用。実行時には使わない): Wiktionary `English idioms`の見出し(proverbs/phrasal verbsは除く)のうち
    (1)5語以内 (2)先頭語が法助動詞/助動詞(縮約形含む) (3)役割判定(区分1の是正)後も有限助動詞として拒否される(縮約形・名詞can・節頭の例外候補)
    +『it/that/there + 核』見出しで核の先頭が助動詞のもの(核を候補にする)。"""
    base = os.path.join(ROOT, "er023_output", "key_phrase_db_trial_01", "db", "wiktionary", "idioms.json")
    titles = [_lex_norm(t) for t in json.load(open(base, encoding="utf-8")).get("titles", [])]
    out = {}
    for t in titles:
        w = t.split()
        if 0 < len(w) <= 5 and _first_aux_word(w) and (w[0] in _AUX_FIRST and ("'" in w[0] or contains_finite_aux_role_based(t))):
            out[t] = "title"
        if len(w) >= 3 and w[0] in ("it", "that", "there"):
            core = " ".join(w[1:])
            cw = core.split()
            if len(cw) <= 5 and _first_aux_word(cw):
                out.setdefault(core, f"core_of:{t}")
    return sorted(out.items())


def _entries_sha(entries) -> str:
    import hashlib
    return hashlib.sha256(chr(10).join(sorted(entries)).encode("utf-8")).hexdigest()


_IDIOM_TABLE = None


def idiom_closed_table() -> frozenset:
    """レビュー済み閉表(JSON)を読む。sha256が定数と一致しなければ空(例外なし)。外部辞書への依存なし。"""
    global _IDIOM_TABLE
    if _IDIOM_TABLE is None:
        ents = frozenset()
        if os.path.exists(IDIOM_TABLE_PATH):
            try:
                d = json.load(open(IDIOM_TABLE_PATH, encoding="utf-8"))
                cand = d.get("entries", [])
                if _entries_sha(cand) == IDIOM_TABLE_SHA256:
                    ents = frozenset(cand)
            except Exception:   # noqa: BLE001
                ents = frozenset()
        _IDIOM_TABLE = ents
    return _IDIOM_TABLE


def idiom_variants(phrase: str) -> set:
    """閉表照合用の正規化: 曲線引用符→ASCII・小文字・所有格(my/our/his…)→one's・has/had/having→have(先頭のみ)。"""
    p = _lex_norm(phrase)
    toks = p.split()
    if not toks:
        return set()
    v = {p}
    t2 = [_POSS_TO_ONES.get(t, t) for t in toks]
    v.add(" ".join(t2))
    if t2[0] in _HAVE_TO_BASE:
        v.add(" ".join([_HAVE_TO_BASE[t2[0]]] + t2[1:]))
    v |= {x.replace("one's", "someone's") for x in list(v)}
    return v


def idiom_closed_table_hit(phrase: str) -> bool:
    toks = _lex_norm(phrase).split()
    if not toks or not _first_aux_word(toks):
        return False          # 先頭が(法)助動詞でない句(名詞主語のことわざ/完全文)は例外にしない
    tbl = idiom_closed_table()
    return any(x in tbl for x in idiom_variants(phrase))


def contains_finite_aux_role_based_idiom(text: str) -> bool:
    """区分2(M3後): role判定に加え、『先頭が(法助動詞/助動詞)でidioms由来のレビュー済み閉表(約27件)』に一致する句だけ例外。
    名詞主語のことわざ・完全文・閉表外は不変(拒否)。主語で始まる句(it can't be helped)は例外にせず、主語を除いた核だけを通す。"""
    if idiom_closed_table_hit(text):
        return False
    return contains_finite_aux_role_based(text)


# =====================================================================================================
# 3. guard拡張(原形化の文脈条件)と閉表補完 = 『Productionへ入れる場合の修正差分案』を測るRulePatch
# =====================================================================================================
QUANT_DET = frozenset({"no", "each", "every", "all", "both", "another", "either", "neither", "several", "few", "many", "much", "enough"})
LY_ADJ = frozenset({"friendly", "lovely", "lonely", "elderly", "costly", "likely", "unlikely", "silly", "early", "daily", "weekly", "monthly",
                    "yearly", "only", "family", "holy", "ugly", "lively", "deadly", "orderly", "lowly", "bubbly", "chilly", "curly",
                    # M1(c): -ly形容詞の追加(Opus指摘: timely/scholarly/cowardly/leisurely/manly/hourly/nightly/sickly/burly/unruly 他)
                    "timely", "scholarly", "cowardly", "leisurely", "manly", "womanly", "hourly", "nightly", "sickly", "burly", "unruly", "motherly",
                    "fatherly", "brotherly", "sisterly", "heavenly", "earthly", "ghostly", "kingly", "queenly", "masterly", "saintly", "worldly",
                    "homely", "kindly", "lordly", "neighborly", "neighbourly", "princely", "slovenly", "surly", "wily", "stately", "sprightly",
                    "gentlemanly", "ladylike", "cleanly", "comely", "courtly", "fortnightly", "quarterly", "northerly", "southerly", "easterly",
                    "westerly", "wobbly", "gnarly", "scraggly", "squiggly", "wriggly", "crumbly", "prickly", "bristly", "knobbly", "lumpy"})
# M1(a): -ly で終わる名詞/動詞(副詞ではない)の除外表。語幹検査をすり抜ける語(supply→supple, reply→rep)も明示的に除く。
LY_NOUN_VERB = frozenset({"supply", "reply", "rally", "assembly", "jelly", "belly", "bully", "folly", "monopoly", "anomaly", "tally", "ally",
                          "apply", "comply", "imply", "multiply", "rely", "fly", "ply", "july", "italy", "lily", "dolly", "holly", "molly", "polly",
                          "sally", "wally", "dally", "bully", "melancholy", "homily", "casualty", "butterfly", "firefly", "dragonfly", "gadfly",
                          "underlay", "overlay", "doily", "dilly", "filly", "hillbilly", "billy", "willy", "silly", "chilly", "cobbly", "gully", "bally",
                          "ghastly", "grisly", "grizzly", "bubbly", "dumbly", "unfriendly", "overly", "reapply", "resupply", "outfly", "nelly", "sully"})
_MANNER_ADV_EXTRA = frozenset({"again", "alone", "hard", "fast", "often", "always", "never"})    # well/stillは名詞用法(a well/a still)があるため除外(M1)
_TAIL_OK_FOLLOW = None   # 実行時にft._GUARD_PARTICLE|ft._GUARD_DETから決める


def _ly_stems(w: str) -> set:
    """-ly副詞の語幹候補(綴り規則: -ily→-y happily→happy / -ally→-ic basically→basic / -bly,-ply,-tly等→-ble,-ple,-tle simply→simple /
    -ully,-lly→-l fully→full / -uly→-ue truly→true / それ以外は-ly除去 quietly→quiet)。"""
    st = set()
    base = w[:-2]
    st.add(base)
    if w.endswith("ily"):
        st.add(w[:-3] + "y")
    if w.endswith("ally"):
        st.add(w[:-4])      # basically -> basic
    if re.search(r"[bpdgktz]ly$", w):
        st.add(w[:-1] + "e")
    if w.endswith("lly"):
        st.add(w[:-1])
    if w.endswith("uly"):
        st.add(w[:-2] + "e")
    if w.endswith("ably") or w.endswith("ibly"):
        st.add(w[:-1] + "e")
    return {x for x in st if len(x) >= 3}


def is_manner_adverb(w: str) -> bool:
    """[M1] -ly副詞か。-ly名詞/動詞/形容詞の除外表に無く、かつ語幹(綴り規則で復元)がCMU実在の語であること。
    (CMU実在だけでは rep(reply)/supple(supply)のように語幹検査をすり抜けるため、除外表と併用する。)"""
    w = w.lower()
    if w in _MANNER_ADV_EXTRA:
        return True
    if not (w.endswith("ly") and len(w) > 4) or w in LY_ADJ or w in LY_NOUN_VERB:
        return False
    return any(not cmu.reasons_for_phrase(x) for x in _ly_stems(w))


def _adverb_tail_ok(key_tokens: list, adv_idx: int) -> bool:
    """副詞が句末、または直後が前置詞/不変化詞/限定詞/等位接続詞(= 副詞が動詞を修飾していて、後続名詞を修飾する形容詞化分詞ではない)。"""
    if adv_idx >= len(key_tokens) - 1:
        return True
    f = key_tokens[adv_idx + 1].lower()
    return f in ft._GUARD_PARTICLE or f in ft._GUARD_DET or f in ("and", "or", "but")


class RulePatch:
    """in-memory一時差替え。各flagは独立(どのflagが事例の救済に最小限必要かを測るため)。with文で必ず元へ戻す。
    flags: aux=役割判定(lexical have) / idiom=慣用句の法助動詞例外(区分2) / quant=量化詞限定詞(区分1)
           adverb=副詞後続の原形化(区分1・三重検査付き) / lexguard=辞書裏付けguard(区分2) / past=過去形専用表の補完(区分1)"""
    def __init__(self, aux=False, idiom=False, quant=False, adverb=False, lexguard=False, past=False):
        self.f = {"aux": aux, "idiom": idiom, "quant": quant, "adverb": adverb, "lexguard": lexguard, "past": past}

    def __enter__(self):
        self._saved = (kc._contains_finite_auxiliary, ft._token_pair_ok, dict(ft._PAST_ONLY_IRREGULAR), dict(ft._AMBIGUOUS_IRREGULAR))
        f = self.f
        if f["idiom"]:
            kc._contains_finite_auxiliary = contains_finite_aux_role_based_idiom
        elif f["aux"]:
            kc._contains_finite_auxiliary = contains_finite_aux_role_based
        if f["past"]:
            for lemma, (past, pp) in IRR.items():
                if past in COMPLETION_EXCLUDE or pp in COMPLETION_EXCLUDE:
                    continue
                if (past in IRR and past != lemma) or (pp in IRR and pp != lemma):
                    continue      # R3: 他の動詞の原形と同形(lay→lie等)
                if past != lemma and past not in ft._PAST_ONLY_IRREGULAR and past not in ft._AMBIGUOUS_IRREGULAR \
                        and past not in ft._FUNCTION_VERB_FORMS:
                    (ft._AMBIGUOUS_IRREGULAR if past in PAST_ALSO_OTHER_WORD else ft._PAST_ONLY_IRREGULAR)[past] = lemma
                if pp not in (past, lemma) and pp not in ft._AMBIGUOUS_IRREGULAR and pp not in ft._PAST_ONLY_IRREGULAR:
                    ft._AMBIGUOUS_IRREGULAR[pp] = lemma
        if f["quant"] or f["adverb"] or f["lexguard"]:
            orig = self._saved[1]

            def pair_ok(kt, dt, idx, key_tokens, _orig=orig):
                if _orig(kt, dt, idx, key_tokens):
                    return True
                kl, dl = kt.lower(), dt.lower()
                if kl == dl:
                    return True
                verb_pos = idx == 0 or key_tokens[idx - 1].lower() == "to"
                if not (verb_pos and len(key_tokens) >= 2 and idx + 1 < len(key_tokens)):
                    return False
                if dl in ft._IRREGULAR_PLURAL or dl in ft._PARTICIPIAL_ADJ_EXCLUDE or dl in ft._PLURAL_EXCLUDE:
                    return False
                # 前方生成一致(`hoped`->`hop`を拒否)は拡張経路にのみ課す(既存経路は無変更)
                lemma_ok = ((dl in ft._AMBIGUOUS_IRREGULAR and kl == ft._AMBIGUOUS_IRREGULAR[dl])
                            or (kl in ft._verb_base_candidates(dl) and inflects_to(kl, dl)))
                if not lemma_ok:
                    return False
                nxt = key_tokens[idx + 1].lower()
                if f["quant"] and nxt in QUANT_DET:
                    return True
                if f["adverb"] and is_manner_adverb(nxt) and _adverb_tail_ok(key_tokens, idx + 1):
                    return True
                if f["lexguard"] and lex_hit(" ".join(key_tokens))["hit"]:
                    return True
                return False
            ft._token_pair_ok = pair_ok
        return self

    def __exit__(self, *a):
        kc._contains_finite_auxiliary, ft._token_pair_ok, po, am = self._saved
        ft._PAST_ONLY_IRREGULAR.clear()
        ft._PAST_ONLY_IRREGULAR.update(po)
        ft._AMBIGUOUS_IRREGULAR.clear()
        ft._AMBIGUOUS_IRREGULAR.update(am)


NO_PATCH = dict()
TIER1_PATCH = dict(aux=True, quant=True, adverb=True, past=True)         # 区分1: 承認済み規則の意図に沿う是正(規則文に無い内部条件・閉表網羅・助動詞誤判定)
TIER2_PATCH = dict(aux=True, quant=True, adverb=True, past=True, idiom=True, lexguard=True)   # +区分2(受理面拡大: 辞書裏付け)


# =====================================================================================================
# 4. 検査(既存validatorを同一引数で再適用 = 前回Opus M6)
# =====================================================================================================
def gate_check(key: str, display: str, span: str, original_span: str | None = None, role_ok_poss=frozenset(),
               reason: str | None = None) -> dict:
    """canonicalization最終Gateと同じ引数(allow_inflection_normalization=True, original_span, role_ok_poss)でvalidator+CMUを適用。"""
    unchanged = [t.lower() for t in ft._norm_tokens(key)] == [t.lower() for t in ft._norm_tokens(display)]
    nr = reason or ("none" if unchanged else "lemma_normalization")
    v = kc.validate_canonicalization_item(key, display, span, normalization_reason=nr, original_span=original_span or span,
                                          allow_inflection_normalization=True, role_ok_poss=role_ok_poss)
    cm = cmu.reasons_for_phrase(key)
    return {"ok": bool(v["ok"] and not cm), "validator_ok": v["ok"], "validator_reasons": v["reasons"], "cmu_reasons": cm,
            "words": ft.count_words(key), "unchanged": unchanged}


def selection_gate(phrase: str, units: list) -> dict:
    """選定段gate(本文連続一致・1〜5語・有限助動詞・数値placeholder)+CMU。"""
    v = ft.validate_and_resolve([{"phrase": phrase, "declared_word_count": None}], units)
    reasons = [r for ir in v["item_reasons"] for r in ir["reasons"]] + list(v["reasons"] or [])
    reasons += cmu.reasons_for_phrase(phrase)
    res = v["resolved"][0] if v["resolved"] else {}
    return {"ok": not reasons, "reasons": reasons, "span": res.get("source_span"), "sentence": res.get("source_sentence"),
            "sentence_id": res.get("source_sentence_id")}


def containment(a: str, b: str) -> bool:
    import er119_kp_human_review_01 as rv
    ta, tb = ft.phrase_key(a).split(), ft.phrase_key(b).split()
    return bool(ta and tb) and (rv._is_subseq_tokens(ta, tb) or rv._is_subseq_tokens(tb, ta))


# =====================================================================================================
# 5. 救済method
# =====================================================================================================
SCOPE_WORDS = frozenset({"too", "not", "never", "no", "only", "hardly", "barely", "scarcely", "rarely", "seldom", "nor", "neither",
                         "less", "least", "nothing", "none", "nobody", "without", "cannot", "nowhere", "almost", "nearly",
                         # R4(Opus): little/few(a little/littleで意味が反転)・unless/except/rather/instead/fail(否定・対比の演算子)
                         "little", "few", "unless", "except", "rather", "instead", "fail", "fails", "failed", "failing"})
EDGE_BAN_START = frozenset({"a", "an", "the", "and", "or", "but", "of", "to", "in", "on", "at", "for", "with", "by", "from", "as", "that",
                            "this", "these", "those", "is", "are", "was", "were", "be", "been", "it", "its"})
EDGE_BAN_END = frozenset({"a", "an", "the", "and", "or", "but", "that", "this", "these", "those", "my", "your", "his", "her", "its", "our",
                          "their", "some", "any", "to", "of", "for", "with", "in", "on", "at", "by", "from", "as", "into", "onto"})
_NOT_VERB_LIKE = frozenset(set(EDGE_BAN_START) | set(SCOPE_WORDS) | {"his", "her", "my", "your", "our", "their", "this", "that", "very", "so",
                                                                    "all", "some", "any", "each", "every", "has", "does", "yes", "us", "yours"})
_FUNCTION_ONLY = frozenset(set(EDGE_BAN_START) | set(EDGE_BAN_END) | {"i", "you", "he", "she", "we", "they", "me", "him", "us", "them", "do", "does",
                                                                    "did", "have", "has", "had", "not", "so", "very", "too", "there", "what", "who"})
_CLEAN_CUT_FOLLOW = frozenset({"for", "with", "in", "on", "at", "by", "from", "as", "into", "onto", "of", "to", "and", "or", "but", "that", "than"})


def _verb_like(w: str) -> bool:
    w = w.lower()
    if w in _NOT_VERB_LIKE:
        return False
    return bool(ft._verb_base_candidates(w)) or any(w in (p, pp) for p, pp in IRR.values())


def _anchor_index(toks: list) -> int:
    """HR提示用の優先付け(決定論ヒューリスティック。POS taggerは使わない): 先頭語が動詞形ならそれ、でなければ最初のtoの直後(to不定詞の動詞)。"""
    if _verb_like(toks[0]):
        return 0
    low = [t.lower() for t in toks]
    return low.index("to") + 1 if "to" in low[:-1] else 0


def _scope_violation(toks: list, i: int, j: int) -> str | None:
    """部分列toks[i:j]が否定・程度語の作用域を壊すか。除外された演算子の被演算子(直後語)を保持=意味反転(too soon->soon)。"""
    low = [t.lower() for t in toks]
    for s, w in enumerate(low):
        if w not in SCOPE_WORDS and not w.endswith("n't"):
            continue
        in_sub = i <= s < j
        head_in = i <= s + 1 < j
        if not in_sub and head_in:
            return f"演算子『{toks[s]}』を落として被演算子『{toks[s + 1]}』を保持(意味反転/程度喪失)"
        if in_sub and not head_in and s + 1 < len(low):
            return f"演算子『{toks[s]}』が句末に残り被演算子『{toks[s + 1]}』が無い(未完)"
    return None


_LOW_VALUE_HEADS = frozenset(SCOPE_WORDS | {"soon", "late", "much", "many", "more", "most", "very", "so", "such", "quite", "just", "even"})


def a1_hr_flags(toks: list, rec: dict) -> list:
    """R4(Opus): A1短縮のHR旗。決定論Gateは『機能語だけ』を禁じても質は担保しない→低価値かどうかの最終判断はHR(元句と本文の文を併記)。"""
    flags = ["意味縮小の可能性(元句の一部のみ。元句と本文の文を併記して確認)"]
    low = [t.lower() for t in rec["phrase"].split()]
    if len(low) <= 2 or all(t in _LOW_VALUE_HEADS or t in _FUNCTION_ONLY for t in low):
        flags.append("低価値の可能性(2語以下/程度・否定の語が中心)")
    if rec["suffix"] is False and rec["prefix"] is False:
        flags.append("元句の中間部分(両端を落とした)")
    return flags


def subspan_candidates(phrase: str, units: list, existing: list) -> list:
    """A1: 6語以上の選定句の真部分連続列(1〜5語)。本文対応は元句の部分列なので保持。決定論禁止表(演算子作用域・端の機能語)で歯止め。"""
    toks = ft._norm_tokens(phrase)
    n = len(toks)
    out = []
    anchor0 = _anchor_index(toks)
    for i in range(n):
        for j in range(i + 1, n + 1):
            if (i, j) == (0, n) or j - i > 5:
                continue
            sub = toks[i:j]
            low = [t.lower() for t in sub]
            rec = {"phrase": " ".join(sub), "span": [i, j], "words": len(sub), "suffix": j == n, "prefix": i == 0}
            viol = _scope_violation(toks, i, j)
            if not viol and all(t in _FUNCTION_ONLY for t in low):
                viol = "機能語/代名詞のみ(内容語を含まない)"
            if not viol and j < n and j - 1 == anchor0 and (_verb_like(toks[anchor0]) or (anchor0 > 0 and toks[anchor0 - 1].lower() == "to")):
                viol = f"動詞『{toks[anchor0]}』が句末で目的語・補語を欠く(未完。比喩/慣用の意味が目的語側にある場合に字義へ誤解されうる)"
            if low[0] in EDGE_BAN_START:
                viol = viol or f"先頭が機能語『{sub[0]}』"
            if low[-1] in EDGE_BAN_END:
                viol = viol or f"末尾が機能語『{sub[-1]}』(句が未完)"
            if viol:
                rec.update(rejected=viol)
                out.append(rec)
                continue
            sg = selection_gate(rec["phrase"], units)
            rec["selection_gate"] = {"ok": sg["ok"], "reasons": sg["reasons"]}
            rec["duplicate_with_existing"] = [e for e in existing if containment(rec["phrase"], e)]
            rec["rejected"] = None if (sg["ok"] and not rec["duplicate_with_existing"]) else (
                "; ".join(sg["reasons"]) or "既存候補と重複/包含: " + ", ".join(rec["duplicate_with_existing"]))
            out.append(rec)
    ok = [r for r in out if not r.get("rejected")]
    for r in ok:
        r["hr_flags"] = a1_hr_flags(toks, r)
    anchor = _anchor_index(toks)
    scope_idx = [k for k, t in enumerate(toks) if t.lower() in SCOPE_WORDS]
    for r in ok:
        i, j = r["span"]
        r["keeps_scope_words"] = all(i <= k < j for k in scope_idx)
        r["starts_at_verb_anchor"] = i <= anchor < j      # 名称は互換のため据置: 動詞アンカーを含む
        r["clean_right_boundary"] = j == n or toks[j].lower() in _CLEAN_CUT_FOLLOW
    # 優先(決定論ヒューリスティック): 元句の演算子語(too/not/no等)を保持 > 動詞アンカーを含む > 語数が多い > 右端が句末/前置詞句の直前で切れる > 左に近い。
    # 目的は『HRに最初に見せる1案』の決定のみ。他の案は alternatives として併記(最終選択はHR)。
    ok.sort(key=lambda r: (not r["keeps_scope_words"], not r["starts_at_verb_anchor"], -r["words"], not r["clean_right_boundary"], r["span"][0]))
    return out, ok


SLOT_WORDS = ("do", "something", "someone")


def slot_generalization_candidates(phrase: str, units: list, existing: list) -> list:
    """A2: 『(…) to <動詞句>』の動詞句(2語以上)を『to do』へ一般化。本文に無い語『do』を含むためRule7の外(区分2)。
    決定論検査: 元句の冒頭連続部分列を保持/置換するtailは2語以上/演算子保持/語数≤5/CMU/助動詞なし。生成は決定論(to不定詞枠のみ)。他の枠はLLM提案が必要(DEV範囲外)。"""
    toks = ft._norm_tokens(phrase)
    low = [t.lower() for t in toks]
    res = []
    for k in range(len(low) - 1, 0, -1):
        if low[k] != "to" or len(low) - (k + 1) < 2:
            continue
        pre = toks[:k + 1]
        cand = " ".join(pre + ["do"])
        rec = {"phrase": cand, "kept_prefix": " ".join(pre), "replaced_tail": " ".join(toks[k + 1:]), "slot": "do",
               "words": len(pre) + 1, "contiguous_in_text": False}
        checks = {}
        checks["scope_words_kept_before_slot"] = all(
            (w not in SCOPE_WORDS) or (low.index(w) <= k) for w in low[:k + 1]) and _scope_violation(toks, 0, k + 1) is None
        checks["words_le_5"] = rec["words"] <= 5
        checks["tail_ge_2_tokens"] = len(low) - (k + 1) >= 2
        checks["prefix_is_leading_contiguous"] = True
        checks["cmu"] = not cmu.reasons_for_phrase(cand)
        checks["no_finite_aux"] = not kc._contains_finite_auxiliary(cand)
        checks["prefix_selection_gate"] = selection_gate(" ".join(pre), units)["ok"] or (len(pre) >= 3)
        lx = lex_hit(rec["replaced_tail"])
        rec["dropped_tail_is_lexicon_idiom"] = lx["hit"]       # 捨てる部分が辞書見出しなら慣用の中身を失う(HR旗)
        rec["duplicate_with_existing"] = [e for e in existing if containment(cand, e)]
        rec["checks"] = checks
        rec["rejected"] = None if (all(checks.values()) and not rec["duplicate_with_existing"]) else "検査不合格"
        res.append(rec)
    return res


def rederive_m1(display: str, llm_key: str, span: str, patch_flags: dict, role_ok_poss=frozenset(), orig_span=None) -> dict:
    """前回Opus M1: display窓の各tokenを{display側の語, LLMがその位置に出した語}のどちらかから選ぶだけ。
    LLM keyがdisplayより長い(範囲拡張)場合は、先頭len(display)語を窓として揃え、はみ出し(display/spanに無い語)を捨てる(=新語形は作らない)。
    選択肢はLLM採用語数の多い順に既存validator(+patch)で試す。全てのtokenがLLM提案語かdisplay語。"""
    dt, kt = ft._norm_tokens(display), ft._norm_tokens(llm_key)
    n = len(dt)
    trunc = None
    if len(kt) > n:
        trunc = kt[n:]
        kt = kt[:n]
    if len(kt) != n:
        return {"ok": False, "why": "LLM keyがdisplayより短い/語数不一致(再導出不可)", "truncated_tail": trunc}
    choices = []
    for mask in itertools.product((1, 0), repeat=n):
        key_toks = [kt[i] if m else dt[i] for i, m in enumerate(mask)]
        if [t.lower() for t in key_toks] == [t.lower() for t in dt] and any(mask):
            continue
        choices.append((sum(mask), key_toks))
    choices.sort(key=lambda c: -c[0])
    tried = []
    with RulePatch(**patch_flags):
        for used, kts in choices:
            key = " ".join(kts)
            g = gate_check(key, display, span, orig_span, role_ok_poss)
            tried.append({"key": key, "llm_tokens_used": used, "ok": g["ok"], "reasons": (g["validator_reasons"] + g["cmu_reasons"])[:2]})
            if g["ok"]:
                return {"ok": True, "key": key, "llm_tokens_used": used, "truncated_tail": trunc, "tried": tried, "gate": g}
    return {"ok": False, "why": "全組合せが既存validatorで不合格", "truncated_tail": trunc, "tried": tried}


def reanchor(phrase: str, units: list) -> list:
    """D1: 本文に連続一致しない選定句(LLMが原形で返した等)を、既存の原形化validator(find_inflection_window)を逆向きに使い、
    『phraseがその本文窓の合法な正規化形になる』本文窓へ戻す。新しい受理基準は作らない(窓が合法でなければ戻さない)。"""
    pt = ft._norm_tokens(phrase)
    n = len(pt)
    found = []
    for u in units:
        raw = u["raw_text"]
        toks = list(ft._TOKEN_RE.finditer(raw))
        for s in range(0, len(toks) - n + 1):
            window = raw[toks[s].start():toks[s + n - 1].end()]
            wt = ft._norm_tokens(window)
            if len(wt) != n:
                continue
            if ft.find_inflection_window(phrase, window) is not None:
                found.append({"surface": window, "sentence": raw, "sentence_id": u.get("sentence_id")})
    uniq = {f["surface"].lower(): f for f in found}
    return list(uniq.values())


PREFIXES = ("re", "un", "non", "pre", "post", "over", "under", "mis", "dis", "co", "anti", "de", "inter", "sub", "super", "semi", "multi", "out")


def cmu_derived(word: str) -> list:
    """D2: CMU未登録語を『生産的接頭辞+CMU登録の基底語』へ分解できるか(分解可能でも代替合格にはしない。区分2の判断材料)。"""
    out = []
    w = word.lower()
    for p in PREFIXES:
        if w.startswith(p) and len(w) - len(p) >= 4:
            base = w[len(p):]
            if not cmu.reasons_for_phrase(base) and not cmu.reasons_for_phrase(p):
                out.append({"prefix": p, "base": base, "prefix_in_cmu": True, "base_in_cmu": True,
                            "predicted_phones": _phones(p) + " + " + _phones(base)})
    return out


def _phones(w: str) -> str:
    try:
        import pronouncing
        ph = pronouncing.phones_for_word(w)
        return ph[0] if ph else "?"
    except Exception:   # noqa: BLE001
        return "?"


# =====================================================================================================
# 6. 事例の組立(inventory -> Case) と評価
# =====================================================================================================
def rule7_parts(reason: str):
    m = re.search(r"key_phrase\((.+?)\)が(?:display_phrase)", reason)
    s = re.search(r"source_span\((.+?)\)内の連続部分文字列", reason)
    strip = lambda x: x.strip("'\"") if x else None   # noqa: E731
    return (strip(m.group(1)) if m else None, strip(s.group(1)) if s else None)


def article_text_for(kpdir: str):
    for cand in (f"{kpdir}/kp_candidates/round_1/work/keywords_selector_prompt.txt", f"{kpdir}/keywords_selector_prompt.txt"):
        if os.path.exists(cand):
            t = open(cand, encoding="utf-8").read()
            i = t.find("\n---\n")
            return t[i + 5:] if i >= 0 else t
    return None


_UNITS_CACHE = {}


def units_for(text: str):
    if text is None:
        return []
    if text not in _UNITS_CACHE:
        import er030_key_phrase_db_hybrid_core_01 as core
        _UNITS_CACHE[text] = core.build_sentence_units(text)
    return _UNITS_CACHE[text]


def existing_candidates(source_json: str) -> list:
    try:
        d = json.load(open(source_json, encoding="utf-8"))
        return [c["selection_phrase"] for c in d.get("candidates", [])] + [c["used_form"] for c in d.get("candidates", [])]
    except Exception:   # noqa: BLE001
        return []


def sentence_for(text, phrase):
    """phraseを含む1文(曲線引用符・大小文字を正規化して探す)。無ければNone。"""
    if not text or not phrase:
        return None
    flat = re.sub(r"\s+", " ", unicodedata.normalize("NFKC", text).replace("\u2019", "'"))
    q = unicodedata.normalize("NFKC", phrase).replace("\u2019", "'").lower()
    i = flat.lower().find(q)
    if i < 0:
        return None
    a = max(flat.rfind(". ", 0, i), flat.rfind("? ", 0, i), flat.rfind("! ", 0, i))
    b = min([x for x in (flat.find(". ", i), flat.find("? ", i), flat.find("! ", i)) if x >= 0] or [len(flat)])
    return flat[a + 2 if a >= 0 else 0:b + 1].strip()


def build_case(ev: dict) -> dict:
    src = ev["source"]
    kpdir = os.path.dirname(src)
    text = article_text_for(kpdir)
    case = {"id": None, "family": ev["family"], "level": ev["level"], "run": ev["run"], "era": ev["era"], "stage": ev.get("stage"),
            "display": ev["phrase"], "class": ev["class"], "sub": ev.get("sub"), "reason": ev["reason"],
            "context": ev.get("context"), "source_json": src, "text": text, "units": units_for(text),
            "existing": existing_candidates(src) if ev["era"].startswith("HR") else []}
    k, s = rule7_parts(ev["reason"]) if ev["class"] == "RULE7_NORMALIZATION" else (None, None)
    case["llm_key"], case["span"] = k, (s or ev["phrase"])
    case["sentence"] = ev.get("context") or sentence_for(text, case["span"]) or sentence_for(text, ev["phrase"])
    return case


def ladder(case: dict) -> dict:
    """1事例について、(T0)現行規則のまま/(T1)区分1の規則是正/(T2)区分2(受理面拡大)の順に試し、各段の結果を残す。"""
    c = case
    d, span, cls = c["display"], c["span"], c["class"]
    rows = []
    out = {"id": c["id"], "family": c["family"], "level": c["level"], "run": c["run"], "display": d, "class": cls, "sub": c["sub"],
           "reason": c["reason"], "context": c["context"], "sentence": c.get("sentence"), "llm_key": c["llm_key"], "rows": rows}

    def add(tier, method, **kw):
        rows.append(dict(tier=tier, method=method, **kw))

    # ---- 語数超過
    if cls == "WORDCOUNT_OVER5":
        allr, ok = subspan_candidates(d, c["units"], c["existing"])
        out["subspans_all"] = allr
        for r in ok[:1]:
            add("T0", "A1_subspan", final=r["phrase"], pass_=True, note="連続部分列(現行規則内・受理面不変)。右端保持の最長", selection_gate=r["selection_gate"],
                hr_flags=r.get("hr_flags"))
        alts = [r["phrase"] for r in ok[1:4]]
        out["subspan_alternatives"] = alts
        slots = slot_generalization_candidates(d, c["units"], c["existing"])
        out["slot_candidates"] = slots
        for r in slots:
            add("T2", "A2_slot_generalization", final=r["phrase"], pass_=r["rejected"] is None, note=f"『{r['replaced_tail']}』を『do』へ(本文に無い語)", checks=r["checks"],
                dropped_tail_is_lexicon_idiom=r["dropped_tail_is_lexicon_idiom"])
        return out

    # ---- Rule7 (原形化/人称/範囲拡張)
    if cls == "RULE7_NORMALIZATION":
        K = c["llm_key"]
        # 現行規則そのままでLLM keyが通るか(当時と同じか)
        g0 = gate_check(K, d, span)
        add("T0", "LLM_key_as_is(現行)", final=K, pass_=g0["ok"], reasons=g0["validator_reasons"][:1])
        with RulePatch(**TIER1_PATCH):
            g1 = gate_check(K, d, span)
        add("T1", "LLM_key_as_is(区分1規則是正後)", final=K, pass_=g1["ok"], reasons=g1["validator_reasons"][:1],
            minimal_flags=_minimal_flags(K, d, span) if g1["ok"] else None)
        r0 = rederive_m1(d, K, span, NO_PATCH)
        add("T0", "B_rederive_M1(現行規則)", final=r0.get("key"), pass_=r0["ok"], note=r0.get("why") or "", truncated_tail=r0.get("truncated_tail"),
            tried=r0.get("tried"))
        r1 = rederive_m1(d, K, span, TIER1_PATCH)
        add("T1", "B_rederive_M1(区分1規則是正後)", final=r1.get("key"), pass_=r1["ok"], truncated_tail=r1.get("truncated_tail"), tried=r1.get("tried"))
        r2 = rederive_m1(d, K, span, TIER2_PATCH)
        add("T2", "B_rederive_M1(区分2含む)", final=r2.get("key"), pass_=r2["ok"], truncated_tail=r2.get("truncated_tail"))
        gr = gate_check(d, d, span)
        add("T0", "revert(表層形)", final=d, pass_=gr["ok"], reasons=gr["validator_reasons"][:1])
        return out

    # ---- 有限助動詞
    if cls == "FINITE_AUX_TOKEN":
        canon_stage = c["reason"].strip() == "有限助動詞が含まれている"      # canonicalization段の理由文(キー側の検査)。phraseはkey
        displays = [d]
        if canon_stage and c["units"]:
            anchors = reanchor(d, c["units"])
            displays = [a["surface"] for a in anchors] or [d]
        # 主語(ダミーit/that)で始まる完全文は、主語を除いた連続部分列も試す(本文の連続部分列=対応保持)
        _t = ft._norm_tokens(d)
        if len(_t) >= 3 and _t[0].lower() in ("it", "that"):
            displays.append(d.split(None, 1)[1])      # 元の綴り(曲線引用符)を保つ
        out["aux_roles"] = finite_aux_roles(d)
        out["canon_stage_reason"] = canon_stage
        out["display_candidates"] = displays
        for disp in displays:
            keys = [disp] + ([d] if d != disp else []) + _lemma_variants(disp)
            for key in dict.fromkeys(keys):
                for tier, flags in (("T0", NO_PATCH), ("T1", dict(aux=True)), ("T2", dict(aux=True, idiom=True))):
                    with RulePatch(**flags):
                        sg = selection_gate(disp, c["units"]) if c["units"] else {"ok": True, "reasons": []}
                        lg = ft._legacy_form_reasons(disp)         # 選定段の下流互換precheck(本文不要。displayの有限助動詞)
                        sg = {"ok": sg["ok"] and not lg, "reasons": sg["reasons"] + lg}
                        gg = gate_check(key, disp, disp)
                    add(tier, f"C_aux_gate(display={disp},key={key})", final=key, display=disp, pass_=bool(gg["ok"] and sg["ok"]),
                        reasons=(gg["validator_reasons"] + sg["reasons"])[:2], aux_roles=finite_aux_roles(key))
        out["lexicon"] = lex_hit(d)
        if not any(r.get("pass_") for r in rows) and c["units"]:
            # 助動詞を外した連続部分列(演算子の作用域を壊さないもの)が救済になるか(区分3の根拠確認用。判定はLLM評価で補う)
            _allr, _ok = subspan_candidates(d, c["units"], c["existing"])
            out["aux_free_subspans"] = [r["phrase"] for r in _ok[:3]]
            out["aux_free_subspans_detail"] = [{"phrase": r["phrase"], "selection_gate": r["selection_gate"]["ok"],
                                                "duplicate_with_existing": r["duplicate_with_existing"]} for r in _ok[:3]]
            out["aux_free_subspans_rejected_samples"] = [{"phrase": r["phrase"], "why": r["rejected"]} for r in _allr if r.get("rejected")][:6]
        return out

    if cls == "CMU_UNREGISTERED":
        words = [w for w in re.findall(r"[^\W\d_]+", d) if cmu.reasons_for_phrase(w)]
        out["unregistered"] = words
        out["derivations"] = {w: cmu_derived(w) for w in words}
        add("T0", "現行(代替合格禁止)", final=None, pass_=False, reasons=cmu.reasons_for_phrase(d))
        return out

    if cls == "NOT_CONTIGUOUS_IN_TEXT":
        anchors = reanchor(d, c["units"])
        out["reanchor"] = anchors
        if len(anchors) == 1:
            out["sentence"] = anchors[0]["sentence"]
        add("T0", "D1_reanchor", final=(anchors[0]["surface"] if len(anchors) == 1 else None), pass_=len(anchors) == 1,
            note=f"本文窓{len(anchors)}件")
        return out

    add("T0", "対象外", final=None, pass_=False, note=cls)
    return out


def _minimal_flags(key, display, span) -> list:
    """区分1の各flagを1つずつ外して、LLM keyが通るのに必要な最小flag集合を求める。"""
    base = dict(TIER1_PATCH)
    need = []
    for name in base:
        trial = {k: v for k, v in base.items() if k != name}
        with RulePatch(**trial):
            if not gate_check(key, display, span)["ok"]:
                need.append(name)
    return need


def _lemma_variants(phrase: str) -> list:
    """selection段で落ちた句のcanonicalization出力(基本形化)の合成例(DEV再導出=synthetic)。先頭動詞の機能動詞表(has/had->have)のみ。"""
    toks = ft._norm_tokens(phrase)
    if toks and toks[0].lower() in ft._FUNCTION_VERB_FORMS and ft._FUNCTION_VERB_FORMS[toks[0].lower()] != toks[0].lower():
        return [" ".join([ft._FUNCTION_VERB_FORMS[toks[0].lower()]] + toks[1:])]
    return []


def final_pick(lad: dict, case: dict) -> dict:
    """ladderから(最小変更解=最も低い区分)と(最良解)を選び、区分・救済可否を決める。"""
    rows = lad["rows"]
    passing = [r for r in rows if r.get("pass_")]
    return {"min_tier_pass": min((r["tier"] for r in passing), default=None), "passing_methods": [(r["tier"], r["method"], r.get("final")) for r in passing]}


# =====================================================================================================
# 6b. 判定(区分1/2/3)と救済記録(前回M3/M4: gloss再整合・QA未再判定・HR引渡し)
# =====================================================================================================
def _first(rows, tier, prefix):
    for r in rows:
        if r["tier"] == tier and r["method"].startswith(prefix) and r.get("pass_"):
            return r
    return None


def decide(lad: dict, case: dict) -> dict:
    """ladder結果から最終判定(救済可否・区分・最小規則変更・最終形)を決める。判定は決定論(同じ入力で同じ結果)。
    区分1=承認済み規則の意図に沿う是正(規則文に無い内部条件/閉表の網羅漏れ/助動詞誤判定)でGate自体が通すようになる(救済フロー不要)。
    区分2=受理面の拡大(本文に無い語/辞書裏付け/新しい救済フロー)でユーザー判断。区分3=救済しない(理由は品質・安全)。"""
    cls, rows, d = lad["class"], lad["rows"], lad["display"]
    dec = {"id": lad["id"], "family": lad["family"], "level": lad["level"], "display": d, "class": cls, "era": lad.get("era"),
           "final_display": None, "final_key": None, "method": None, "category": None, "rescuable": False, "rule_changes": [],
           "fallback_surface": None, "why": "", "flow_needed": False}
    if cls == "HUMAN_NG_EXCLUDED":
        dec.update(category="区分3", why="Human NG(ユーザーの明示判断)は復活しない(USER.md:97)。救済経路でもmatch_ngがselection_phrase/used_formの両方を照合し迂回不可")
        return dec
    if cls == "WORDCOUNT_OVER5":
        a1 = _first(rows, "T0", "A1_subspan")
        a2 = next((r for r in rows if r["method"].startswith("A2_") and r.get("pass_")), None)
        if a1:
            dec.update(final_display=a1["final"], final_key=a1["final"], method="A1_subspan", rescuable=True, flow_needed=True,
                       category="区分2(救済フロー本体の採否[後処理工程の新設]。受理面は不変)", rule_changes=["選定段の短縮救済フロー(新規)"],
                       why="元句の連続部分列で本文対応を保持。演算子(too/not/no/little/few/unless/except/rather/instead/fail等)の作用域を壊す部分列は決定論で禁止(意味反転なし)。HRに元句と本文の文を併記",
                       hr_flags=a1.get("hr_flags"))
        if a2:
            dec["option_slot_generalization"] = {"candidate": a2["final"],
                                                  "category": "区分2(非推奨・AI意見付き。M4: ユーザー自身の例のためAIが区分3で閉じず、判断材料を併記してユーザー判断へ)",
                                                  "dropped_tail_is_lexicon_idiom": a2.get("dropped_tail_is_lexicon_idiom"), "checks": a2.get("checks")}
        if not a1 and not a2:
            dec.update(category="区分3", why="検査を通る部分列/一般化が無い")
        return dec
    if cls == "RULE7_NORMALIZATION":
        K = lad["llm_key"]
        now = _first(rows, "T0", "LLM_key_as_is")
        t1 = _first(rows, "T1", "LLM_key_as_is")
        if now:
            dec.update(rescuable=True, final_display=d, final_key=K, method="現行Gateで既に通る", category="(除外ではなくなった)", why="現行validatorで通過(過去世代の除外)")
            return dec
        if t1:
            flags = t1.get("minimal_flags") or []
            dec.update(rescuable=True, final_display=d, final_key=K, method="LLMのkeyが区分1規則是正だけで通常フローを通る", category="区分1",
                       rule_changes=[{"quant": "guard限定詞に量化詞を追加", "adverb": "guardに副詞後続(三重検査付き)を追加", "past": "過去形/分詞の閉表を補完",
                                      "aux": "有限助動詞の役割判定"}.get(f, f) for f in flags],
                       why="承認済みP-04の文言(『先頭またはto直後の動詞』)に無い内部条件/閉表の網羅漏れ。LLMの提案keyはそのまま通る=救済フロー不要")
            r0 = _first(rows, "T0", "revert")
            dec["fallback_surface"] = r0["final"] if r0 else None
            return dec
        r1 = _first(rows, "T1", "B_rederive_M1")
        r0 = _first(rows, "T0", "B_rederive_M1")
        r2 = _first(rows, "T2", "B_rederive_M1")
        rv_ = _first(rows, "T0", "revert")
        best = r2 or r1 or r0
        if best:
            dec.update(rescuable=True, flow_needed=True, final_display=d, final_key=best["final"], method="M1再導出(救済フロー)",
                       fallback_surface=rv_["final"] if rv_ else None)
            if r0 and r0["final"] == best["final"]:
                if best["final"].lower() == d.lower():
                    dec["method"] = "表層形へ戻す(revert。原形はguard/表の範囲外のため)"
                dec["category"] = "区分2(救済フロー本体の採否。受理面は不変=LLM提案語∩display窓)"
                dec["rule_changes"] = ["救済フロー(後処理工程の新設)"]
                if any(x.get("truncated_tail") for x in rows):
                    dec["hr_flags"] = ["LLMが補った語(窓外のtail)を破棄(目的語の意味が失われる/多義の可能性。gloss再整合は本文での意味で行う)"]
                    dec["why"] = "LLMが範囲拡張(display窓外の語を付加)。窓内の語だけ採用(先頭len(display)語。新語形は作らない)。窓外tailは捨てる(gloss再整合必須)"
                else:
                    dec["why"] = "LLM提案語/display語の組合せから最大限LLM提案を採用した形"
            elif r1 and r1["final"] == best["final"]:
                dec["category"] = "区分1(+救済フロー)"
                dec["rule_changes"] = ["区分1規則是正"]
                dec["why"] = "区分1規則是正後に原形が通る"
            else:
                dec["category"] = "区分2(辞書裏付けguard等の受理面拡大)"
                dec["rule_changes"] = ["辞書裏付けguard"]
                dec["why"] = "規則文のguardでは不通過。辞書(Wiktionary見出し)に原形句が存在=動詞用法の裏付けで受理"
            return dec
        dec.update(category="区分3", why="全組合せが既存validatorで不合格")
        return dec
    if cls == "FINITE_AUX_TOKEN":
        # 判定対象は『元の除外句d』そのもの(canonicalization段の除外ではdがkey、選定段ではdがdisplay)。lemma変種は参考行。
        on_d = [r for r in rows if r["final"] and r["final"].lower() == d.lower()]
        t0 = [r for r in on_d if r["tier"] == "T0" and r.get("pass_")]
        t1 = [r for r in rows if r["tier"] == "T1" and r.get("pass_")]
        t1_d = [r for r in on_d if r["tier"] == "T1" and r.get("pass_")]
        t2_d = [r for r in on_d if r["tier"] == "T2" and r.get("pass_")]
        if t0:
            dec.update(rescuable=True, final_display=d, final_key=d, method="現行Gateで通る", category="(除外ではなくなった)", why="現行規則で通過")
            return dec
        if t1_d:
            best = next((r for r in t1 if r["final"].lower() != d.lower() and lad.get("canon_stage_reason") is False), t1_d[0])
            dec.update(rescuable=True, final_display=best.get("display") or d, final_key=best["final"], method="役割判定(lexical have)で通常フローを通る", category="区分1",
                       rule_changes=["有限助動詞の役割判定(語彙動詞have/has/hadは助動詞でない)"], flow_needed=False,
                       why="承認済み規則は『有限助動詞』の排除(DECISION_LOG:7408)。語彙動詞haveは助動詞でなく、OPEN-152で誤判定として既出。"
                           "承認済みP-04(3)のhas/had->haveも語形リストと自己矛盾して常に不通過(dead path)")
            return dec
        if t2_d:
            dec.update(rescuable=True, final_display=d, final_key=d, method="慣用句の法助動詞例外(レビュー済み閉表と一致)", category="区分2",
                       rule_changes=["慣用句の法助動詞例外(先頭が助動詞・idioms由来のレビュー済み閉表)"], flow_needed=False,
                       why="Wiktionary慣用句見出し『it can't be helped』の核(主語を除く)をレビュー済み閉表に収載。固定表現として自立=節の断片ではない。例外は閉表の句に限定(名詞主語のことわざ・完全文は対象外)")
            return dec
        t2_var = [r for r in rows if r["tier"] == "T2" and r.get("pass_") and r.get("display") and r["display"].lower() != d.lower()]
        if t2_var:
            v = t2_var[0]
            dec.update(rescuable=True, final_display=v["display"], final_key=v["final"], method="主語(it)除去の連続部分列+慣用句の法助動詞例外", category="区分2",
                       rule_changes=["選定段の主語除去(連続部分列)", "慣用句の法助動詞例外(レビュー済み閉表)"], flow_needed=True,
                       why="『it can't be helped』は主語を持つ完全文=原承認趣旨(完全文排除)に反するため、主語を除いた核『can't be helped』(本文の連続部分列・"
                           "Wiktionary見出しの核)だけを通す。それでも例外が無ければ不通過")
            return dec
        dec.update(category="区分3", why="法助動詞/進行形auxを核とする節の断片(完全文/節排除の意図どおり)。助動詞を外すと意味が変わる。辞書見出しにも無い")
        return dec
    if cls == "CMU_UNREGISTERED":
        der = lad.get("derivations") or {}
        if der and all(v for v in der.values()):
            dec.update(category="区分2(CMU規則の受理面拡大: 非推奨)", rescuable=False,
                       rule_changes=["CMU未登録語の接頭辞+登録基底語分解(代替合格の一種)"],
                       why="分解は可能(re+delivery)だが、2026-10-22承認のCMU必須条件は未登録語の推測/代替合格を禁止。TTS発音安全のため非採用を推奨(音声ASR検証付きでの限定採用は選択肢)")
        else:
            dec.update(category="区分3", why="CMU未登録でかつ構成語に分解できない(外来語/アクセント付き)。発音を推測で補えない=TTS発音安全")
        return dec
    if cls == "NOT_CONTIGUOUS_IN_TEXT":
        r = _first(rows, "T0", "D1_reanchor")
        if r:
            dec.update(rescuable=True, flow_needed=True, final_display=r["final"], final_key=d, method="D1 本文近傍への再アンカー(既存原形化validatorの逆引き)",
                       category="区分2(救済フロー本体の採否。受理面は不変=本文逐語のspanに戻す)", rule_changes=["選定段の再アンカー救済(新規)"],
                       why="LLMが原形で返した句を、既存validatorが『その本文窓の合法な正規化形』と判定する窓へ戻す。窓が一意のときのみ。以降は通常のcanonicalizationへ")
        else:
            dec.update(category="区分3", why="本文に対応する窓が無い(言い換え・創作)=出典との対応が失われる")
        return dec
    dec.update(category="区分3", why="対象外")
    return dec


def final_check(dec: dict, case: dict) -> dict | None:
    """最終形(final_display/final_key)を、必要な規則是正flagの下で既存validator(同一引数)・CMU・選定gate・既存候補との重複に再適用した証跡。"""
    if not dec.get("rescuable") or not dec.get("final_key") or not dec.get("final_display"):
        return None
    cat = str(dec.get("category", ""))
    flags = NO_PATCH
    if cat.startswith("区分1"):
        flags = TIER1_PATCH
    if "慣用句" in " ".join(dec.get("rule_changes", [])) or "慣用句" in str(dec.get("method", "")):
        flags = dict(TIER1_PATCH, idiom=True)        # M3: 慣用句例外(レビュー済み閉表)のみ。辞書guard(lexguard)は含めない
    if "辞書" in cat:
        flags = TIER2_PATCH
    disp, key = dec["final_display"], dec["final_key"]
    with RulePatch(**flags):
        g = gate_check(key, disp, disp)
        sg = selection_gate(disp, case["units"]) if case.get("units") else None
        lg = ft._legacy_form_reasons(disp)
    return {"patch_flags": {k: v for k, v in flags.items() if v}, "validator_ok": g["validator_ok"], "validator_reasons": g["validator_reasons"],
            "cmu_ok": not g["cmu_reasons"], "words": g["words"], "selection_gate": (sg or {}).get("ok") if sg else "text_unavailable",
            "legacy_form_reasons": lg, "duplicate_with_existing": [e for e in case.get("existing", []) if containment(key, e)]}


def make_rescue_record(dec: dict, case: dict) -> dict | None:
    """kp_candidates.json候補へ付ける救済記録(前回M3/M4/M5)。auto_eligible=False・QA未再判定・gloss再整合必須(キーがLLM提案と異なる場合)。"""
    if not dec.get("rescuable") or not dec.get("final_key"):
        return None
    llm_key = case.get("llm_key")
    gloss_required = bool(dec.get("flow_needed") and (dec["final_key"].lower() != (llm_key or "").lower()))
    return {
        "rescue": {"applied": bool(dec.get("flow_needed")), "method": dec["method"], "category": dec["category"],
                   "before": {"selection_phrase": dec["display"], "llm_key_phrase": llm_key, "stage": case.get("stage"), "reasons": [case["reason"]][:1]},
                   "after": {"used_form": dec["final_key"], "display": dec["final_display"]},
                   "recheck": "既存validator(同一引数)+CMU通過(rescue_eval参照)",
                   "gloss": {"realign_required": gloss_required, "status_if_unresolved": "gloss_hr_pending"}},
        "flags": {"rescued": bool(dec.get("flow_needed")), "gloss_hr_pending": False},
        "gates": {"canonicalization": "RESCUED_QA_NOT_REJUDGED" if dec.get("flow_needed") else "PASS(通常フロー)"},
        "auto_eligible": False if dec.get("flow_needed") else None,
        "hr_row_note": (f"修正済み(元: {dec['display']} / {dec['method']})・QA未再判定" if dec.get("flow_needed") else ""),
    }


# =====================================================================================================
# 7. inventory全体への適用 / corpus probe / main
# =====================================================================================================
def run_inventory(inv_path: str):
    inv = json.load(open(inv_path, encoding="utf-8"))
    events = [e for e in inv["events"] if e["class"] != "QA_REVIEW_REQUIRED(非除外・旗)"]
    out = []
    for n, e in enumerate(events):
        case = build_case(e)
        case["id"] = n
        if e["class"] == "HUMAN_NG_EXCLUDED":
            lad = {"id": n, "family": e["family"], "level": e["level"], "run": e["run"], "display": e["phrase"], "class": e["class"],
                   "reason": e["reason"], "era": e["era"], "rows": [{"tier": "-", "method": "復活禁止(Human NG)", "final": None, "pass_": False}]}
            lad["decision"] = decide(lad, case)
            out.append(lad)
            continue
        lad = ladder(case)
        lad["era"] = e["era"]
        lad["decision"] = decide(lad, case)
        lad["final_check"] = final_check(lad["decision"], case)
        lad["rescue_record"] = make_rescue_record(lad["decision"], case)
        out.append(lad)
    return out


def have_probe(path_out: str, prev_path: str | None = None) -> dict:
    """全本文(X/Y/Z selector prompt)の『have/has/had始まりの2〜4語窓』のうち、現行の語形リストでは拒否され、役割判定で新たに通る窓を列挙(人手レビュー用)。
    [委任_02/M2] 窓単体の判定に加え、文全体を文脈にした判定(ext_role)も出し、窓が助動詞構文の断片(have all|gone 等)のものを fragment_of_aux として別掲する。
    prev_path(委任_01の結果)があれば、M2で再び拒否側(aux)に戻った窓を reblocked_by_m2 として出す。"""
    seen_texts = {}
    for pat in ("er019_output", "er026_output", "er121_output"):
        for f in glob.glob(f"{pat}/**/keywords_selector_prompt.txt", recursive=True):
            t = open(f, encoding="utf-8").read()
            i = t.find(chr(10) + "---" + chr(10))
            art = t[i + 5:] if i >= 0 else t
            seen_texts[hash(art)] = art
    newly, blocked_still, frag = {}, {}, {}
    for art in seen_texts.values():
        flat = unicodedata.normalize("NFKC", art).replace("’", "'")
        for sent in re.split(r"(?<=[.!?])\s+|" + chr(10) + "+", flat):
            toks = ft._norm_tokens(sent)
            low = [x.lower() for x in toks]
            for st in range(len(toks)):
                if low[st] not in _HAVE:
                    continue
                ext = have_role(low, st, capitalized_first=toks[st][:1].isupper())
                for n in (2, 3, 4):
                    w = toks[st:st + n]
                    if len(w) < n:
                        continue
                    ph = " ".join(w)
                    if not kc._contains_finite_auxiliary(ph):
                        continue
                    key = " ".join(w[:3]).lower()
                    if contains_finite_aux_role_based(ph):
                        blocked_still.setdefault(key, ph)
                    else:
                        newly.setdefault(key, ph)
                        if ext == "aux":
                            frag.setdefault(key, {"window": ph, "sentence": sent.strip()[:200]})
    res = {"newly_unblocked_windows": sorted(newly.values()), "still_blocked_windows": sorted(blocked_still.values()),
           "fragment_of_aux_in_sentence": sorted(frag.values(), key=lambda x: x["window"])}
    if prev_path and os.path.exists(prev_path):
        prev = json.load(open(prev_path, encoding="utf-8")).get("newly_unblocked_windows", [])
        res["reblocked_by_m2"] = sorted(set(prev) - set(res["newly_unblocked_windows"]))
        res["prev_n"] = len(prev)
    json.dump(res, open(path_out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return res


def build_idiom_table(out_json: str) -> dict:
    """M3: 機械抽出した候補(build_idiom_candidates)にレビュー結果(IDIOM_REVIEW_INCLUDE/EXCLUDE)を適用して閉表JSONを書く。"""
    import hashlib
    base = os.path.join(ROOT, "er023_output", "key_phrase_db_trial_01", "db", "wiktionary")
    src = {}
    for fn in ("idioms", "phrasal_verbs", "proverbs"):
        p = os.path.join(base, fn + ".json")
        d = json.load(open(p, encoding="utf-8"))
        src[fn + ".json"] = {"sha256": hashlib.sha256(open(p, "rb").read()).hexdigest(), "category": d.get("category"), "n_titles": len(d.get("titles", [])),
                             "used_for_table": fn == "idioms"}
    cands = dict(build_idiom_candidates())
    excl = {t: why for why, ts in IDIOM_REVIEW_EXCLUDE_REASON.items() for t in ts}
    missing = sorted(IDIOM_REVIEW_INCLUDE - set(cands))
    uncovered = sorted(t for t in cands if t not in IDIOM_REVIEW_INCLUDE and t not in excl)
    entries = sorted(IDIOM_REVIEW_INCLUDE & set(cands))
    out = {"purpose": "KP-GATE-EXCLUSION-RESCUE-DESIGN-02 M3: 慣用句の法助動詞/助動詞例外のレビュー済み閉表(DEV。Production非配線)",
           "extraction_rule": "Wiktionary Category:English idioms の見出し(proverbs/phrasal verbsは使わない)のうち、5語以内・先頭語が法助動詞/助動詞(縮約形can't等を含む)・"
                              "役割判定後も有限助動詞として拒否されるもの、+『it/that/there+核』見出しの核(核の先頭が助動詞、5語以内)。実行時に外部辞書は照会しない",
           "source_snapshot": src, "n_candidates": len(cands), "n_entries": len(entries), "entries": entries,
           "entries_sha256": _entries_sha(entries),
           "excluded": [{"title": t, "origin": cands[t], "reason": excl.get(t, "(未分類)")} for t in sorted(cands) if t not in entries],
           "include_not_in_candidates": missing, "uncovered_candidates": uncovered,
           "license_note": "Wiktionary本文はCC BY-SA 4.0(+GFDL)。本表は見出し(語句の列挙)のみを利用し本文・定義・例文は取り込まない。見出しの列挙が著作物として"
                           "継承条件(ShareAlike)の対象かは法的判断が必要(ユーザー判断材料)。出典表示ファイルをrepoに置く案を併記(DESIGN_02参照)"}
    json.dump(out, open(out_json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return out


def monotonicity_run(adv_path: str, out_path: str) -> dict:
    """委任_02: (1)実データ(既存の選定句/used_formペア)に対する単調性(既に受理されていた変換がパッチ後も受理される)+新規受理変換の列挙(selection_probe)
    (2)敵対的test集(adversarial_01.json): 誤受理してはいけない変換/受理すべき変換/役割判定/過去形表/慣用句例外 を機械判定。"""
    tmp = out_path + ".real.tmp"
    real = selection_probe(tmp)
    os.remove(tmp)
    adv = json.load(open(adv_path, encoding="utf-8"))
    res = {"real_data": {k: real[k] for k in ("n_displays", "n_pairs", "n_changed_pairs", "monotonicity_violations")},
           "real_data_newly_accepted": real["newly_accepted_conversions"], "adversarial": {}}
    fails = []

    conv = []
    for c in adv.get("conversions", []):
        with RulePatch(**TIER1_PATCH):
            t1 = ft.find_inflection_window(c["key"], c["display"]) is not None
        base = ft.find_inflection_window(c["key"], c["display"]) is not None
        if c["expect"] == "preexisting_accept":      # パッチ前から受理される既存挙動: パッチで増減しないことだけを固定
            row = dict(c, tier1_accepts=t1, production_accepts=base, ok=(t1 == base and base))
            row["preexisting_in_production"] = True
        else:
            want = c["expect"] == "accept"
            row = dict(c, tier1_accepts=t1, production_accepts=base, ok=(t1 == want))
            row["preexisting_in_production"] = bool(base and not want)
        conv.append(row)
        if not row["ok"]:
            fails.append(("conversion", c["display"], c["key"]))
    res["adversarial"]["conversions"] = conv

    roles = []
    for c in adv.get("have_roles", []):
        got = [role for tok, role in finite_aux_roles(c["phrase"]) if tok in _HAVE]
        ok = got == c["expect"]
        roles.append(dict(c, got=got, ok=ok))
        if not ok:
            fails.append(("have_role", c["phrase"], got))
    res["adversarial"]["have_roles"] = roles

    past = []
    with RulePatch(past=True):
        for w in adv.get("past_forms_must_not_be_added", []):
            added = w in ft._PAST_ONLY_IRREGULAR or w in ft._AMBIGUOUS_IRREGULAR
            past.append({"form": w, "added": added, "ok": not added})
            if added:
                fails.append(("past_form", w, "added"))
        for w in adv.get("past_forms_must_be_added", []):
            added = w in ft._PAST_ONLY_IRREGULAR or w in ft._AMBIGUOUS_IRREGULAR
            past.append({"form": w, "added": added, "ok": added})
            if not added:
                fails.append(("past_form_missing", w, "not added"))
    res["adversarial"]["past_forms"] = past

    idi = []
    with RulePatch(aux=True, idiom=True):
        for c in adv.get("idiom", []):
            blocked = kc._contains_finite_auxiliary(c["phrase"])
            ok = blocked == (c["expect"] == "blocked")
            idi.append(dict(c, blocked=blocked, ok=ok))
            if not ok:
                fails.append(("idiom", c["phrase"], blocked))
    res["adversarial"]["idiom"] = idi
    res["adversarial_summary"] = {"n": len(conv) + len(roles) + len(past) + len(idi), "fails": fails}
    json.dump(res, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return res


_CLITIC_RE = re.compile(r"(?<![A-Za-z])([A-Za-z]+)(n['’]t|['’](?:re|ll|d|ve|m|s))(?![A-Za-z])", re.IGNORECASE)


def contraction_probe(path_out: str) -> dict:
    """R5(Opus): 縮約形('re/'ll/'d/'ve/'m/'s、n't)が有限助動詞検査をすり抜ける範囲の測定(API 0、既存の出力ログのみ)。
    現行の検査(kc._contains_finite_auxiliary)はトークン化 [A-Za-z][A-Za-z'-]* で、ASCII `'`は1語(can't)・曲線`’`は2語(can,t)になる。
    対象= X/Y/Z出力の選定句(selection_phrase/used_form/display_phrase/key_phrase/dropped)。"""
    phrases = {}
    for pat in ("er019_output", "er026_output", "er121_output"):
        for f in glob.glob(f"{pat}/**/kp_candidates.json", recursive=True):
            try:
                d = json.load(open(f, encoding="utf-8"))
            except Exception:   # noqa: BLE001
                continue
            for c in d.get("candidates", []):
                for k in ("selection_phrase", "used_form"):
                    if c.get(k):
                        phrases.setdefault(c[k], set()).add("accepted_candidate")
            for c in d.get("dropped", []):
                if c.get("phrase"):
                    phrases.setdefault(c["phrase"], set()).add("dropped")
        for f in glob.glob(f"{pat}/**/keywords_canonicalized.json", recursive=True):
            try:
                d = json.load(open(f, encoding="utf-8"))
            except Exception:   # noqa: BLE001
                continue
            for it in d.get("items", []):
                for k in ("display_phrase", "key_phrase", "used_form"):
                    if it.get(k):
                        phrases.setdefault(it[k], set()).add("canonicalized_item")
    rows = []
    for ph, where in sorted(phrases.items()):
        ms = _CLITIC_RE.findall(ph)
        if not ms:
            continue
        curly = "’" in ph
        rows.append({"phrase": ph, "where": sorted(where), "quote": "curly" if curly else "ascii",
                     "clitics": [a + b for a, b in ms], "orig_blocked": kc._contains_finite_auxiliary(ph),
                     "has_aux_clitic": any(re.fullmatch(r"n['’]t|['’](re|ll|d|ve|m)", b, re.IGNORECASE) for _, b in ms),
                     "has_s_clitic": any(re.fullmatch(r"['’]s", b, re.IGNORECASE) for _, b in ms)})
    by = {}
    for r in rows:
        k = (r["quote"], "aux_clitic" if r["has_aux_clitic"] else ("'s(所有格/is/has)" if r["has_s_clitic"] else "other"))
        by.setdefault(f"{k[0]}/{k[1]}", {"n": 0, "currently_blocked": 0, "currently_passes": 0})
        by[f"{k[0]}/{k[1]}"]["n"] += 1
        by[f"{k[0]}/{k[1]}"]["currently_blocked" if r["orig_blocked"] else "currently_passes"] += 1
    res = {"n_phrases_scanned": len(phrases), "n_with_clitic": len(rows), "by_class": by, "rows": rows,
           "tokenization_note": {"can't": kc._WORD_TOKEN_RE.findall("can't"), "can’t": kc._WORD_TOKEN_RE.findall("can’t"),
                                 "they’re": kc._WORD_TOKEN_RE.findall("they’re"), "I’ll": kc._WORD_TOKEN_RE.findall("I’ll"),
                                 "it's": kc._WORD_TOKEN_RE.findall("it's"), "won’t": kc._WORD_TOKEN_RE.findall("won’t")}}
    json.dump(res, open(path_out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return res


def _lemma_candidates(tok: str) -> set:
    """先頭/to直後の動詞token tokの『基本形候補』。三重検査のうち(CMU実在)+(前方生成一致)を満たす語のみ(`analyz`/`hop`を作らない)。"""
    d = tok.lower()
    c = set(ft._verb_base_candidates(d))
    if d in ft._AMBIGUOUS_IRREGULAR:
        c.add(ft._AMBIGUOUS_IRREGULAR[d])
    if d in ft._PAST_ONLY_IRREGULAR:
        c.add(ft._PAST_ONLY_IRREGULAR[d])
    for lemma, (past, pp) in IRR.items():
        if d in (past, pp):
            c.add(lemma)
    return {x for x in c if not cmu.reasons_for_phrase(x) and inflects_to(x, d)}


def selection_probe(path_out: str) -> dict:
    """既存の実選定句(311種, X/Y/Z全KP出力)に対し、(1)既受理ペアがRulePatch後も受理される(単調性)、(2)新たに受理される変換と(3)役割判定で新たに通る有限助動詞語を列挙。"""
    displays, pairs = set(), set()
    for pat in ("er019_output", "er026_output", "er121_output"):
        for f in glob.glob(f"{pat}/**/keywords_canonicalized.json", recursive=True):
            try:
                d = json.load(open(f, encoding="utf-8"))
            except Exception:   # noqa: BLE001
                continue
            for it in d.get("items", []):
                dp, kp = it.get("display_phrase"), it.get("key_phrase") or it.get("used_form")
                if dp:
                    displays.add(dp)
                    if kp:
                        pairs.add((dp, kp))
        for f in glob.glob(f"{pat}/**/kp_candidates.json", recursive=True):
            try:
                d = json.load(open(f, encoding="utf-8"))
            except Exception:   # noqa: BLE001
                continue
            for c in d.get("candidates", []):
                displays.add(c["selection_phrase"])
                pairs.add((c["selection_phrase"], c["used_form"]))
            for c in d.get("dropped", []):
                displays.add(c["phrase"])
    base_ok = {(d, k): ft.find_inflection_window(k, d) is not None for d, k in pairs if k and k.lower() != d.lower()}
    mono_violations = []
    with RulePatch(**TIER2_PATCH):
        for (d, k), was in base_ok.items():
            if was and ft.find_inflection_window(k, d) is None:
                mono_violations.append((d, k))
    newly = []
    for disp in sorted(displays):
        toks = ft._norm_tokens(disp)
        if not toks:
            continue
        pos = [0] + [i + 1 for i, t in enumerate(toks[:-1]) if t.lower() == "to"]
        for i in pos:
            for lem in sorted(_lemma_candidates(toks[i])):
                key = " ".join(toks[:i] + [lem] + toks[i + 1:])
                if ft.find_inflection_window(key, disp) is not None:
                    continue
                with RulePatch(**TIER1_PATCH):
                    t1 = ft.find_inflection_window(key, disp) is not None
                with RulePatch(**TIER2_PATCH):
                    t2 = ft.find_inflection_window(key, disp) is not None
                if t1 or t2:
                    flags = {}
                    for fl in ("quant", "adverb", "past", "lexguard"):
                        with RulePatch(**{fl: True}):
                            flags[fl] = ft.find_inflection_window(key, disp) is not None
                    newly.append({"display": disp, "key": key, "tier": "T1" if t1 else "T2", "by_flag": [k for k, v in flags.items() if v]})
    have_rows = []
    for disp in sorted(displays):
        roles = finite_aux_roles(disp)
        if any(t in _HAVE for t, _ in roles):
            have_rows.append({"display": disp, "roles": roles, "orig_blocked": kc._contains_finite_auxiliary(disp),
                              "role_based_blocked": contains_finite_aux_role_based(disp)})
    res = {"n_displays": len(displays), "n_pairs": len(pairs), "n_changed_pairs": len(base_ok), "monotonicity_violations": mono_violations,
           "newly_accepted_conversions": newly, "have_family_displays": have_rows}
    json.dump(res, open(path_out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return res


JUDGE_MODEL = "gpt-6-luna"        # PM_GOVERNANCE 25節: 最新世代の推奨系(repoの承認済みSUPPORT_MODEL)。旧/下位モデルではない
_PRICE_USD_PER_M = {"input": 0.10, "cached": 0.01, "output": 0.50}   # er009_n1_routing_governance_10_actual_model_cost.py:30
_USD_JPY = 160.0                                                      # 同 :21

JUDGE_SCHEMA = {"name": "kp_rescue_judge", "strict": True, "schema": {
    "type": "object", "additionalProperties": False, "required": ["items"],
    "properties": {"items": {"type": "array", "items": {
        "type": "object", "additionalProperties": False,
        "required": ["id", "meaning_vs_source", "natural_english", "standalone_learning_unit", "corresponds_to_source_text", "verdict", "note_ja"],
        "properties": {
            "id": {"type": "string"},
            "meaning_vs_source": {"type": "string", "enum": ["same", "narrowed", "changed", "inverted"]},
            "natural_english": {"type": "boolean"},
            "standalone_learning_unit": {"type": "string", "enum": ["good", "weak", "bad"]},
            "corresponds_to_source_text": {"type": "boolean"},
            "verdict": {"type": "string", "enum": ["adopt", "adopt_with_hr_flag", "reject"]},
            "note_ja": {"type": "string"}}}}}}}

JUDGE_PROMPT = """You are an independent reviewer for an English-learning radio app. For each item, the app extracted a "key phrase" learning unit from an article sentence, a rule-based gate rejected it, and a proposed REPAIRED unit is shown. Judge ONLY the repaired unit.
For each item output:
- meaning_vs_source: compare the repaired unit's meaning (as a learner would take it) with what the original selected phrase meant in the sentence: same / narrowed (less specific but not wrong) / changed / inverted.
- natural_english: is the repaired unit natural, idiomatic English (not a broken fragment)?
- standalone_learning_unit: good / weak / bad as an independent unit to teach.
- corresponds_to_source_text: does the repaired unit correspond to words actually used in the source sentence? The app ALREADY APPROVES these changes, so do NOT penalise them: verb to dictionary form (rose->rise), plural to singular, my/our/his/her -> one's/someone's, him/her/you/me/us -> someone, this/that -> a/an. Penalise only other differences (new words, paraphrase). If no source sentence is given, judge naturalness and meaning only and answer true for this field.
- verdict: adopt / adopt_with_hr_flag (a human should see the original too) / reject.
- note_ja: one short Japanese sentence.
Be strict and independent; do not assume the repair is good. Items:
"""


def build_judge_items(eval_path: str) -> list:
    rows = json.load(open(eval_path, encoding="utf-8"))
    items, seen = [], set()
    for r in rows:
        d = r.get("decision") or {}
        if not r.get("era", "").startswith("HR") and not (d.get("rescuable") and str(d.get("category", "")).startswith("区分"))                 and not r.get("aux_free_subspans"):
            continue
        sent = r.get("sentence") or r.get("context")
        kinds = []
        if d.get("final_key") and d.get("rescuable"):
            kinds.append((d["final_key"], d["method"]))
        opt = d.get("option_slot_generalization")
        if opt:
            kinds.append((opt["candidate"], "A2 slot generalization (replaces the tail with a generic verb 'do'; the word 'do' is not in the source)"))
        for alt in (r.get("aux_free_subspans") or [])[:2]:
            kinds.append((alt, "contiguous sub-span that drops the auxiliary (deterministic scope check passed)"))
        if r["class"] == "WORDCOUNT_OVER5":
            for alt in (r.get("subspan_alternatives") or [])[:3]:
                kinds.append((alt, "A1 contiguous sub-span of the original phrase (alternative)"))
        for key, how in kinds:
            k = (r["display"].lower(), key.lower())
            if k in seen:
                continue
            seen.add(k)
            items.append({"id": f"{r['id']}:{key}", "source_sentence": sent, "original_selected_phrase": r["display"], "repaired_unit": key, "how_repaired": how})
    return items


def run_judge(eval_path: str, budget_jpy: float, out_path: str):
    items = build_judge_items(eval_path)
    from dotenv import load_dotenv
    load_dotenv()
    from openai import OpenAI
    client = OpenAI()
    msg = JUDGE_PROMPT + json.dumps(items, ensure_ascii=False, indent=1)
    resp = client.responses.create(model=JUDGE_MODEL, reasoning={"effort": "low"},
                                   text={"format": {"type": "json_schema", **JUDGE_SCHEMA}}, input=[{"role": "user", "content": msg}])
    if resp.model != JUDGE_MODEL:
        raise RuntimeError(f"model mismatch: {resp.model}")
    u = resp.usage
    inp = getattr(u, "input_tokens", 0) or 0
    cached = getattr(getattr(u, "input_tokens_details", None), "cached_tokens", 0) or 0
    outp = getattr(u, "output_tokens", 0) or 0
    usd = ((inp - cached) * _PRICE_USD_PER_M["input"] + cached * _PRICE_USD_PER_M["cached"] + outp * _PRICE_USD_PER_M["output"]) / 1e6
    jpy = usd * _USD_JPY
    res = json.loads(resp.output_text)
    out = {"model": resp.model, "response_id": resp.id, "n_items": len(items), "usage": {"input": inp, "cached": cached, "output": outp},
           "cost_jpy": round(jpy, 4), "budget_jpy": budget_jpy, "items_in": items, "judgements": res["items"],
           "provenance": "fresh(LLM評価のみ。救済候補の生成は決定論)"}
    json.dump(out, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("judge items:", len(items), "cost_jpy:", round(jpy, 4))


HEADWORD_SCHEMA = {"name": "kp_headword_judge", "strict": True, "schema": {
    "type": "object", "additionalProperties": False, "required": ["items"],
    "properties": {"items": {"type": "array", "items": {
        "type": "object", "additionalProperties": False,
        "required": ["id", "acceptable_as_headword", "entry_type", "learning_value", "meaning_vs_source", "verdict", "note_ja"],
        "properties": {
            "id": {"type": "string"},
            "acceptable_as_headword": {"type": "boolean"},
            "entry_type": {"type": "string", "enum": ["fixed_expression", "grammar_pattern_with_slot", "ordinary_phrase", "not_a_learning_unit"]},
            "learning_value": {"type": "string", "enum": ["good", "weak", "bad"]},
            "meaning_vs_source": {"type": "string", "enum": ["same", "narrowed", "generalized", "changed", "inverted", "no_source"]},
            "verdict": {"type": "string", "enum": ["adopt", "adopt_with_hr_flag", "reject"]},
            "note_ja": {"type": "string"}}}}}}}

HEADWORD_PROMPT = """You are an independent reviewer for an English-learning radio app. Each item is a candidate "key phrase" learning unit. In this evaluation you must judge each unit AS A HEADWORD / PATTERN ENTRY OF A LEARNER'S DICTIONARY (like the pattern headings in Oxford Advanced Learner's, Cambridge or Longman, e.g. "too ... to do", "be about to do", "have a say"), NOT as a natural English sentence fragment. In such headings the word "do" (or "something"/"someone") is a conventional placeholder for a generic verb/object slot.
For each item output:
- acceptable_as_headword: would a learner's dictionary plausibly list this exact form as an entry or pattern heading?
- entry_type: fixed_expression / grammar_pattern_with_slot / ordinary_phrase / not_a_learning_unit.
- learning_value: good / weak / bad as a unit to teach on its own.
- meaning_vs_source: compared with the source phrase's meaning in its sentence (source_phrase_in_article; "no_source" if none): same / narrowed / generalized (a pattern covering the source) / changed / inverted.
- verdict: adopt / adopt_with_hr_flag (a human should also see the original) / reject.
- note_ja: one short Japanese sentence.
Be strict and independent. Items:
"""


def run_judge_headword(cases_path: str, budget_jpy: float, out_path: str, n_runs: int = 3):
    """M4(Opus): A2 `too soon to do` を『学習者向け辞書の見出し形として適切か』の枠組みで再評価(前回=『自然な英文として適切か』の枠組みでreject 7/8)。
    評価は決定論Gateが通したものの却下専用の参考情報であり、QAではない。n_runs回の独立call(各回同一プロンプト)で揺れを見る。"""
    cases = json.load(open(cases_path, encoding="utf-8"))
    from dotenv import load_dotenv
    load_dotenv()
    from openai import OpenAI
    client = OpenAI()
    msg = HEADWORD_PROMPT + json.dumps(cases, ensure_ascii=False, indent=1)
    runs, total = [], 0.0
    for k in range(n_runs):
        resp = client.responses.create(model=JUDGE_MODEL, reasoning={"effort": "low"},
                                       text={"format": {"type": "json_schema", **HEADWORD_SCHEMA}}, input=[{"role": "user", "content": msg}])
        if resp.model != JUDGE_MODEL:
            raise RuntimeError(f"model mismatch: {resp.model}")
        u = resp.usage
        inp = getattr(u, "input_tokens", 0) or 0
        cached = getattr(getattr(u, "input_tokens_details", None), "cached_tokens", 0) or 0
        outp = getattr(u, "output_tokens", 0) or 0
        usd = ((inp - cached) * _PRICE_USD_PER_M["input"] + cached * _PRICE_USD_PER_M["cached"] + outp * _PRICE_USD_PER_M["output"]) / 1e6
        jpy = usd * _USD_JPY
        total += jpy
        runs.append({"run": k + 1, "response_id": resp.id, "usage": {"input": inp, "cached": cached, "output": outp}, "cost_jpy": round(jpy, 4),
                     "judgements": json.loads(resp.output_text)["items"]})
        if total > budget_jpy:
            raise RuntimeError(f"budget exceeded: {total:.3f} > {budget_jpy}")
    out = {"model": JUDGE_MODEL, "model_is_latest_recommended": "repoの承認済み推奨系(SUPPORT_MODEL)。PM_GOVERNANCE 25節: 最新世代の推奨系。旧/下位モデルではない(生成側と同系統=R6の限界を併記)",
           "n_runs": n_runs, "cost_jpy_total": round(total, 4), "budget_jpy": budget_jpy, "cases": cases, "runs": runs,
           "framing": "学習者向け辞書の見出し形/パターン見出しとして適切か(前回judge_06-08=自然な英文としての評価)"}
    json.dump(out, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("headword judge: cases", len(cases), "runs", n_runs, "cost_jpy_total:", round(total, 4))


def rescue_structural_revert(llm_key: str, display: str, span: str, original_span: str | None = None, role_ok_poss=frozenset()) -> dict:
    """前回Opus R1: LLMのkeyが原因の構造違反(OF-X1左端条件/canon段の語数超過/CMU post-canon未登録語 等)の救済は『displayへ戻す』のみ(受理面は不変)。
    戻した後のkeyで既存validator(同一引数)+CMUを必ず再検査する。"""
    before = gate_check(llm_key, display, span, original_span, role_ok_poss)
    after = gate_check(display, display, span, original_span, role_ok_poss)
    return {"before_ok": before["ok"], "before_reasons": (before["validator_reasons"] + before["cmu_reasons"])[:2],
            "reverted_key": display, "after_ok": after["ok"], "after_reasons": (after["validator_reasons"] + after["cmu_reasons"])[:2]}


def summarize(eval_path: str, out_path: str) -> dict:
    rows = json.load(open(eval_path, encoding="utf-8"))

    def label(d):
        c = str(d.get("category"))
        if c.startswith("(除外ではなくなった)") or c.startswith("(現行Gateで通る)"):
            return "NOW_PASS"
        if c.startswith("区分1"):
            return "区分1"
        if c.startswith("区分2(CMU"):
            return "区分2(非推奨)"
        if c.startswith("区分2"):
            return "区分2"
        if c.startswith("区分3"):
            return "区分3"
        return c

    res = {}
    for era in ("HR", "preHR", "all"):
        uniq = {}
        for r in rows:
            e = r.get("era", "")
            if era == "HR" and not e.startswith("HR"):
                continue
            if era == "preHR" and not e.startswith("pre"):
                continue
            d = r["decision"]
            k = (r["family"], r["display"].lower(), r["class"])
            lab = label(d)
            if k not in uniq:
                uniq[k] = (lab, d.get("rescuable"))
        cnt = {}
        for lab, resc in uniq.values():
            cnt[lab] = cnt.get(lab, 0) + 1
        res[era] = {"unique_events": len(uniq), "by_label": cnt}
    json.dump(res, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return res


def _judge_runs(judge_paths: str) -> list:
    runs = []
    for pth in [x for x in (judge_paths or "").split(",") if x]:
        if not os.path.exists(pth):
            continue
        jd = json.load(open(pth, encoding="utf-8"))
        inp = {i["id"]: i for i in jd["items_in"]}
        m = {}
        for j in jd["judgements"]:
            it = inp.get(j["id"])
            if it:
                m[(it["original_selected_phrase"].lower(), it["repaired_unit"].lower())] = j
        runs.append({"path": pth, "map": m, "cost_jpy": jd.get("cost_jpy")})
    return runs


def _adopt_ok(j: dict, strict: bool) -> bool:
    if j["verdict"] not in ("adopt", "adopt_with_hr_flag") or not j["natural_english"] or j["meaning_vs_source"] not in ("same", "narrowed"):
        return False
    return (j["standalone_learning_unit"] == "good") if strict else (j["standalone_learning_unit"] != "bad")


def judge_summary(runs: list, display: str, key: str) -> dict | None:
    """複数回のLLM評価の多数決。LLM評価は揺れる(同一入力でも判定が変わる)ため、2/3以上で採用/却下を決める。"""
    js = [r["map"].get((display.lower(), key.lower())) for r in runs]
    js = [j for j in js if j]
    if not js:
        return None
    n = len(js)
    need = n // 2 + 1
    return {"n_runs": n, "adopt_ok_strict": sum(_adopt_ok(j, True) for j in js), "adopt_ok_loose": sum(_adopt_ok(j, False) for j in js),
            "reject": sum(j["verdict"] == "reject" for j in js), "majority_need": need,
            "verdicts": [(j["verdict"], j["meaning_vs_source"], j["standalone_learning_unit"]) for j in js],
            "notes_ja": [j["note_ja"] for j in js][:3]}


def finalize(eval_path: str, judge_paths: str, out_json: str, out_md: str) -> dict:
    """決定論の判定(decide)にLLM評価(judge、複数回の多数決)を重ね、事例(一意)毎の最終表を作る。judgeは『評価』のみ(候補の生成は決定論)。
    重ね方: (1)決定論で救済可と出た最終形が多数決でreject → 区分3(品質根拠)。(2)助動詞を外した連続部分列(決定論通過)は、
    多数決で『意味same/narrowed・自然・学習単位good』を満たすときだけ区分2(救済フロー)として採る。"""
    rows = json.load(open(eval_path, encoding="utf-8"))
    runs = _judge_runs(judge_paths)
    out, seen = [], set()
    for r in rows:
        k = (r["family"], r["display"].lower(), r["class"], r.get("era", "")[:2])
        if k in seen:
            continue
        seen.add(k)
        d = r["decision"]
        rec = {"id": r["id"], "era": r.get("era"), "family": r["family"], "level": r["level"], "display": r["display"], "class": r["class"],
               "sub": r.get("sub"), "reason": (r["reason"] or "")[:160], "decision": d, "final_check": r.get("final_check"), "judge": None,
               "final_label": None, "final_note": ""}
        cand = d.get("final_key")
        js = judge_summary(runs, r["display"], cand) if (cand and runs) else None
        rec["judge"] = js
        lab = d.get("category")
        if r.get("aux_free_subspans") and runs:
            ev = []
            for a in r["aux_free_subspans"][:2]:
                ev.append({"candidate": a, "judge": judge_summary(runs, r["display"], a)})
            rec["aux_free_subspan_judgements"] = ev
            good = [x["candidate"] for x in ev if x["judge"] and x["judge"]["adopt_ok_strict"] >= x["judge"]["majority_need"]]
            if good:
                lab = "区分2(救済フロー: 助動詞を外した連続部分列)"
                rec["final_note"] = f"助動詞を外した部分列『{good[0]}』が決定論gate+LLM評価(多数決)を通過(HRに元句を併記)"
                rec["decision"] = dict(d, final_display=good[0], final_key=good[0], rescuable=True, flow_needed=True, category=lab,
                                       method="助動詞を外した連続部分列", rule_changes=["選定段の短縮救済フロー(新規)"])
                det = next((x for x in (r.get("aux_free_subspans_detail") or []) if x["phrase"] == good[0]), {})
                g = gate_check(good[0], good[0], good[0])
                rec["final_check"] = {"patch_flags": {}, "validator_ok": g["validator_ok"], "cmu_ok": not g["cmu_reasons"], "words": g["words"],
                                      "selection_gate": det.get("selection_gate"), "duplicate_with_existing": det.get("duplicate_with_existing") or []}
            else:
                rec["final_note"] = "助動詞を外した部分列は多数決で基準(意味same/narrowed・自然・学習単位good)を満たさない。助動詞が意味の核のため区分3"
        if js and d.get("rescuable") and js["reject"] >= js["majority_need"]:
            lab = "区分3(決定論は通過だがLLM評価が多数決でreject)"
        rec["final_label"] = lab
        out.append(rec)
    json.dump(out, open(out_json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    L = ["# FINAL_TABLE (自動生成。決定論の判定 + LLM評価[複数回多数決]の重ね合わせ)", "",
         "| # | era | Family/lv | 元候補 | 除外クラス | 修正後(display→key) | 既存Gate再検証 | LLM評価(採用可/回数) | 区分 |", "|---|---|---|---|---|---|---|---|---|"]
    for r in out:
        d = r["decision"]
        fc = r["final_check"] or {}
        chk = ("validator=%s CMU=%s sel=%s dup=%s flags=%s" % (fc.get("validator_ok"), fc.get("cmu_ok"), fc.get("selection_gate"),
                                                              len(fc.get("duplicate_with_existing") or []), ",".join(fc.get("patch_flags", {})) or "-")) if fc else "-"
        jj = r["judge"]
        jt = f"{jj['adopt_ok_loose']}/{jj['n_runs']}(strict {jj['adopt_ok_strict']}, reject {jj['reject']})" if jj else "-"
        fin = f"{d.get('final_display')}→{d.get('final_key')}" if d.get("final_key") else "-"
        L.append(f"| {r['id']} | {(r['era'] or '')[:2]} | {r['family']}/{r['level']} | `{r['display']}` | {r['class']} | {fin} | {chk} | {jt} | {r['final_label']} |")
    open(out_md, "w", encoding="utf-8").write(chr(10).join(L) + chr(10))
    cnt = {}
    for r in out:
        e = (r["era"] or "")[:2]
        lab = str(r["final_label"]).split("(")[0]
        cnt.setdefault(e, {}).setdefault(lab, 0)
        cnt[e][lab] += 1
    return cnt


def write_md(rows: list, path: str, tag: str):
    L = [f"# RESCUE_TABLE (自動生成 rescue_eval_{tag}) — 詳細はRESCUE_TABLE_01.md(人手整理版)", "",
         "| # | Family/level | 元候補 | 除外クラス | min区分 | 通過した方式(tier/method→final) |", "|---|---|---|---|---|---|"]
    for r in rows:
        ok = [x for x in r["rows"] if x.get("pass_")]
        mt = min((x["tier"] for x in ok), default="-")
        meths = "; ".join(f"{x['tier']}/{x['method']}→{x.get('final')}" for x in ok)[:300]
        L.append(f"| {r['id']} | {r['family']}/{r['level']} | `{r['display']}` | {r['class']}{('/' + r['sub']) if r.get('sub') else ''} | {mt} | {meths} |")
    open(path, "w", encoding="utf-8").write("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory")
    ap.add_argument("--out")
    ap.add_argument("--md")
    ap.add_argument("--tag", default="01")
    ap.add_argument("--have-probe")
    ap.add_argument("--selection-probe")
    ap.add_argument("--summary")
    ap.add_argument("--finalize")
    ap.add_argument("--judge-json")
    ap.add_argument("--final-md")
    ap.add_argument("--gap-report")
    ap.add_argument("--judge")
    ap.add_argument("--judge-headword")
    ap.add_argument("--build-idiom-table")
    ap.add_argument("--monotonicity", action="store_true")
    ap.add_argument("--adversarial")
    ap.add_argument("--contraction-probe")
    ap.add_argument("--prev-have")
    ap.add_argument("--budget-jpy", type=float, default=30.0)
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    if a.gap_report:
        json.dump(irregular_gap_report(), open(a.gap_report, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("gap report ->", a.gap_report)
    if a.have_probe:
        r = have_probe(a.have_probe, a.prev_have)
        print("newly_unblocked:", len(r["newly_unblocked_windows"]), "still_blocked:", len(r["still_blocked_windows"]))
    if a.finalize:
        print(json.dumps(finalize(a.finalize, a.judge_json, a.out, a.final_md), ensure_ascii=False))
    if a.summary:
        print(json.dumps(summarize(a.summary, a.out), ensure_ascii=False))
    if a.selection_probe:
        r = selection_probe(a.selection_probe)
        print("displays:", r["n_displays"], "changed pairs:", r["n_changed_pairs"], "mono_violations:", len(r["monotonicity_violations"]),
              "newly_accepted:", len(r["newly_accepted_conversions"]), "have_family:", len(r["have_family_displays"]))
    if a.inventory:
        rows = run_inventory(a.inventory)
        json.dump(rows, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        if a.md:
            write_md(rows, a.md, a.tag)
        print("events:", len(rows), "->", a.out)
    if a.judge:
        run_judge(a.judge, a.budget_jpy, a.out)
    if a.judge_headword:
        run_judge_headword(a.judge_headword, a.budget_jpy, a.out)
    if a.build_idiom_table:
        r = build_idiom_table(a.build_idiom_table)
        print("idiom table: candidates", r["n_candidates"], "entries", r["n_entries"], "sha256", r["entries_sha256"], "include_not_in_candidates", r["include_not_in_candidates"],
              "uncovered", r["uncovered_candidates"])
    if a.contraction_probe:
        r = contraction_probe(a.contraction_probe)
        print("contraction: scanned", r["n_phrases_scanned"], "with clitic", r["n_with_clitic"], json.dumps(r["by_class"], ensure_ascii=False))
    if a.monotonicity:
        r = monotonicity_run(a.adversarial, a.out)
        print("real:", json.dumps(r["real_data"]["monotonicity_violations"]), "newly_accepted:", len(r["real_data_newly_accepted"]),
              "adversarial n/fails:", r["adversarial_summary"]["n"], r["adversarial_summary"]["fails"])


if __name__ == "__main__":
    main()
