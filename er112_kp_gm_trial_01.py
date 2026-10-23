# -*- coding: utf-8 -*-
"""FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_02: Key Phrase 一般化・文脈意味・意味説明 DEV/Trial 実装(er112)。

位置づけ: DEV/Trial専用。Productionモジュール(er003_*/er105_*/er019_*)・Prompt・template・flag・閾値は**一切編集しない**。
Production関数はimportして呼び、Trial armごとの差分は『スレッドローカルのarm設定を見るdispatcher』をプロセス内monkeypatchで注入して実現する
(arm設定が無い/baseline armでは元の関数へ素通し)。`install_dev_patches()`を明示的に呼ぶまで何も差し替えない(import副作用0・既定OFF)。
Production到達経路: 無し(本ファイルをimportするProductionコードは無い。起動はこのファイルを直接実行した場合のみ)。
正式配線は未承認。Trial成功=VALIDATEDまで。採用はユーザー判断。

arm: base(現行) / a1(A-1: canonicalization規則5+validator表) / a12(+A-2 gloss語義方針) / a123s(+A-3 説明Prompt+Std/Adv gloss決定論共有)。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import threading
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = ROOT / "er112_output" / "kp_gm_trial_01"
LEDGER = OUT / "paid_calls.jsonl"
MANAGEMENT_ID = "FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01"
CAP_JPY_DEFAULT = 80.0

# ------------------------------------------------------------------ Production module hash guard (OF-01)
PROD_FILES = [
    "er003_key_words_canonicalization.py", "er105_" "kp_fulltext_selector_01.py", "er003_key_words_gloss_alignment.py",
    "er019_family_x_kp_explanation_01.py", "er003_v1_n3_01_scaffold_generate.py", "er019_family_x_audio_production_runner_01.py",
    "er026_family_z_fiction_production_runner_01.py", "er003_key_phrase_source_gate_01.py",
    "er003_v1_translator_briefs/b1_p2_keywords_canonicalization_fulltext_prompt_template.txt",
    "er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt",
]


def prod_hashes() -> dict:
    out = {}
    for p in PROD_FILES:
        fp = ROOT / p
        out[p] = hashlib.sha256(fp.read_bytes()).hexdigest() if fp.exists() else None
    return out


# ------------------------------------------------------------------ arm設定 (thread-local)
ARMS = {
    # base_c/a1_c: canonicalizationのみ(gloss・説明は呼ばない。費用節約: 合成item・baselineの揺れ測定用)
    "base": dict(a1=False, a2=False, a3=False, share=False, ctx=False),
    "base_c": dict(a1=False, a2=False, a3=False, share=False, ctx=False, skip_gloss=True, skip_expl=True),
    "a1": dict(a1=True, a2=False, a3=False, share=False, ctx=False),
    "a1_c": dict(a1=True, a2=False, a3=False, share=False, ctx=False, skip_gloss=True, skip_expl=True),
    # a12: a1と同じrep・unitのcanonicalization結果を再利用(API 0)、gloss(A-2)から再実行
    "a12": dict(a1=True, a2=True, a3=False, share=False, ctx=False, canon_from=("a1", "a1_c")),
    # a1g: A-1のみ(gloss・説明は現行Prompt)。a1_cのcanon結果を再利用し、A-2の効果を分離するための比較arm
    "a1g": dict(a1=True, a2=False, a3=False, share=False, ctx=False, canon_from=("a1_c",)),
    # a123s: a12のitems(canon+gloss)をそのまま使い、Adv説明(A-3)+Std/Adv gloss決定論共有だけ再実行
    "a123s": dict(a1=True, a2=True, a3=True, share=True, ctx=False, items_from="a12"),
    "a123c": dict(a1=True, a2=True, a3=True, share=True, ctx=True, items_from="a12"),
    # a3v2: A-3の具体化版(share無し・a12のitemsを再利用して説明段だけ再実行。費用は説明1callのみ)
    "a3v2": dict(a1=True, a2=True, a3=2, share=False, ctx=False, items_from="a12"),
    # a1gE0/a1gE2: A-1のみのitems(a1g rep1)を固定し、説明段だけを現行Prompt(E0)/A-3 v2(E2)で各rep再実行(A-2を採用しない構成での説明比較。説明1callのみ)
    "a1gE0": dict(a1=True, a2=False, a3=False, share=False, ctx=False, items_from="a1g", items_from_rep=1),
    "a1gE3": dict(a1=True, a2=False, a3=3, share=False, ctx=False, items_from="a1g", items_from_rep=1),
    "a1gE2": dict(a1=True, a2=False, a3=2, share=False, ctx=False, items_from="a1g", items_from_rep=1),
}
_TL = threading.local()


class ArmCtx:
    def __init__(self, arm: str, rep: int, unit: str, article_text: str = ""):
        self.arm, self.rep, self.unit, self.article_text = arm, rep, unit, article_text
        self.cfg = dict(ARMS[arm])
        self.dir = None


def cur():
    return getattr(_TL, "ctx", None)


def _flag(name: str) -> bool:
    c = cur()
    return bool(c and c.cfg.get(name))


# ------------------------------------------------------------------ A-1: canonicalization規則5 template
A1_RULE5 = (
    "5. 参照語の不定化(置換): display_phraseに、この記事の特定の対象を指しているだけの次の参照語が含まれる場合、学習用の一般形へ**置換**してください"
    "(削除ではありません。語数は変わりません)。\n"
    "   (a) 指示語this/thatが、単数の可算名詞の直前に置かれた限定詞のとき: aに置換します(直後の語が母音で始まる音ならan)。theは使いません。"
    "例: \"draw that line\"→\"draw a line\"、\"float that idea\"→\"float an idea\"、\"take that step\"→\"take a step\"。"
    "この置換にはnormalization_reason=\"generalize_reference_word\"を使ってください。\n"
    "   (b) 目的格の人称代名詞him/her/me/usが、この記事の特定の人物を指しているだけの場合: someoneに置換します(動詞の語形は規則4で別途基本形にできます)。"
    "例: \"pulled him under\"→\"pull someone under\"、\"told her the truth\"→\"tell someone the truth\"、\"close around me\"→\"close around someone\"。"
    "herが所有格(her jobのように名詞が続く場合)のときは規則3の扱い(one's/someone's)です。"
    "この置換にはnormalization_reason=\"generalize_person_dependent_reference\"を使ってください。\n"
    "   **次の場合は規則5(a)(b)を適用せず、該当語をそのまま残してください**: 指示語が代名詞・副詞・接続詞として働く場合(句末のthat、that much、not that bad、so that…)、"
    "不可算名詞の前(that advice等)、固定表現で指示語・代名詞が意味の一部になっているもの(that said、at that point、in that case、this time、like that、between you and me、all that等)、"
    "およびit/them/these/those。置換しても意味・自然さが保てるか迷う場合は置換しません。\n"
    "   この規則5が置換してよい語はthis/that/him/her/me/usだけで、それ以外の語は規則4の語形変化以外一切変更しません。"
    "また、上の『置換しない』の判断は規則5の対象語(this/that/him/her/me/us)にだけ適用してください。"
    "規則3(my/your/his/their/our/its、yourself/himself等の人称・所有格の一般化)は、従来どおり規則3自身の基準で判断し、規則5があることを理由に控えめにしたり、"
    "規則4(語形の基本形化)を広げたりしないでください(例: 形容詞的に使われる分詞は原形にしない)。"
)

_A1_EDITS = [
    # (old, new)  oldは元templateに**ちょうど1回**存在しなければならない(drift guard)
    ("変更してよいのは、以下の具体的な理由がある場合のみです。",
     "変更してよいのは、以下の具体的な理由がある場合のみです。**ただし、display_phraseに下の規則5に該当する参照語(指示語this/that、目的格のhim/her/me/us)が含まれる場合は"
     "「そのままで自然」とはみなさず、規則5を先に検討してください(規則5の例外に当たる場合のみ無変更でかまいません)。**"),
    ("**一般化してよい代名詞は上に列挙した語(my/your/his/her/their/our/its、you/they/he/she、yourself/himself/herself/themselves等)だけです。"
     "him/her(目的格)/them/me/us/it等の目的格・その他の代名詞は、記事の登場人物を指していても一般形(someone等)へ置換せず、そのまま残してください(列挙外の置換は決定論検証で却下されます)。**",
     "**この規則3で一般化してよい代名詞は上に列挙した語(my/your/his/her/their/our/its、you/they/he/she、yourself/himself/herself/themselves等)だけです。"
     "目的格のhim/her/me/usは下の規則5(b)で扱います。them/it等のその他の代名詞は、記事の登場人物を指していても一般形(someone等)へ置換せず、そのまま残してください"
     "(列挙外の置換は決定論検証で却下されます)。**"),
    ("この規則のいずれにも該当しない場合", A1_RULE5 + "\n\nこの規則(1〜5)のいずれにも該当しない場合"),
    ("規則4(語形の基本形化)・規則3(人称の一般化)に従った同じ語の語形変化のいずれかでなければなりません",
     "規則4(語形の基本形化)・規則3(人称の一般化)・規則5(参照語の不定化)に従った同じ語の語形変化または1対1の置換のいずれかでなければなりません"),
    ("である。(c)(d)の場合、一般化後・基本形化後の語",
     "である、(e) key_phraseが上記規則5に従って生成されたもの(this/that→a/an/the、him/her/me/us→someone)である。(c)(d)(e)の場合、一般化後・基本形化後・不定化後の語"),
    ("それが上記規則3に従って辞書的な一般形に正しく置換されているか",
     "それが上記規則3(目的格のhim/her/me/usは規則5(b))に従って辞書的な一般形に正しく置換されているか"),
    ("\"generalize_person_dependent_reference\"(人称代名詞・所有格の一般化、上記規則3)/",
     "\"generalize_person_dependent_reference\"(人称代名詞・所有格の一般化[上記規則3]、および目的格him/her/me/usのsomeoneへの置換[上記規則5(b)])/ "
     "\"generalize_reference_word\"(指示語this/thatのa/an/theへの置換、上記規則5(a))/"),
]


def build_a1_template(prod_template: str) -> str:
    t = prod_template
    for old, new in _A1_EDITS:
        if t.count(old) != 1:
            raise RuntimeError(f"A-1 template drift: anchor count={t.count(old)} for {old[:40]!r}")
        t = t.replace(old, new)
    return t


# ------------------------------------------------------------------ A-2: gloss 語義方針 (NEW_GENERATION_TEXTへ追記)
A2_EXTRA = (
    "【語義の方針(新規生成の項目に適用。上記1〜3の『すべての語の意味を反映する』より優先)】\n"
    "- key_phraseが慣用句・比喩・定型表現のときは、語ごとの直訳ではなく、フレーズ全体の意味を日本語にしてください"
    "(型の例: cut corners→『手を抜く』であり『角を切る』ではない)。日本語でも同じ比喩が同じ意味で自然に通じる場合は、その表現でかまいません"
    "(型の例: bridge the gap→『溝を埋める』)。通じない場合は、フレーズ全体の意味を書いてください。本文で字義どおりに使われている場合は、字義どおりの意味を書いてください。\n"
    "- どの語義かは本文(source_sentenceと記事本文)で判断し、その文での意味を表してください。ただし記事固有の状況・固有名詞は入れず、"
    "別の場面でも通用する簡潔な言い方にしてください。意味は原則1つだけを書き、訳語を並べないでください。\n"
    "- key_phraseに含まれる冠詞・指示語(a, the, this, that等)を『その』『ある』などと逐語的に訳出しないでください。\n"
    "- 上の『key_phrase全体のすべての語の意味を反映する』は、慣用句・定型表現では、フレーズ全体の意味が日本語に表れていれば満たされます(語ごとの対応は求めません)。\n\n"
)


# ------------------------------------------------------------------ A-3: Adv英語説明 追加規則 (OF-05反映)
A3_EXTRA = (
    "- Use the sense the phrase has in the source sentence; the Japanese reference is only a hint for which sense.\n"
    "- Explain the core meaning of the phrase in its most general use that fits the source sentence. Give ONE meaning; "
    "do not add conditions or details that belong only to this text.\n"
)


# A-3 v2(ITERATION_LOG #2): v1は『most general use / ONE meaning』だけでは、記事の話題に由来する条件(誰が/何のために/何が許容か等)が説明へ残った。
# 追加規則を『辞書が学習者向けに定義する中心義、一般語で、物語の状況・条件を書かない』へ具体化(例は検証セットの語を使わない)。
A3_EXTRA_V2 = (
    "- Use the sense the phrase has in the source sentence; the Japanese reference is only a hint for which sense.\n"
    "- Write only the CORE meaning that stays true in any situation, the way a learner's dictionary would define it: ONE meaning, in general words "
    "(someone, something, a limit, a plan). Do not describe the situation of the source sentence, and do not add who, what for, or what kind of details "
    "that the phrase itself does not contain.\n"
)


# A-3 v3(ITERATION_LOG #3): v2でも『許容される/されない』型の評価的条件が3/3残った(原因=記事ではなく慣用句の辞書的代表義を既定に選ぶLLMの癖)。
# 評価的条件(何が許される/期待される/正しい等)を表現自体が持たない限り足さない、と一般化して明示し、検証セット外の語で良/悪の対比例を1つ付ける。
A3_EXTRA_V3 = (
    "- Use the sense the phrase has in the source sentence; the Japanese reference is only a hint for which sense.\n"
    "- Write only the CORE meaning, as short as a learner's dictionary would give it: ONE meaning, in general words (someone, something). "
    "Do not add a purpose, condition, standard or evaluation (such as what is allowed, expected, right or wrong) unless the phrase itself is about that. "
    "Style example for a different phrase: \"turn a blind eye\" -> \"to ignore something wrong on purpose\" (good), "
    "\"to ignore a rule that someone breaks at work\" (too specific).\n"
)


# ------------------------------------------------------------------ DEV validator (OF-01/OF-02/OF-03)
_DEM_FOLLOW_BLOCK = frozenset({
    "much", "many", "is", "was", "are", "were", "said", "will", "would", "can", "could", "has", "had", "does", "did", "off", "up", "out", "over",
    "down", "in", "on", "at", "to", "for", "with", "by", "from", "and", "or", "but", "if", "as", "than", "so", "time", "point", "case", "way", "day",
    "moment", "reason", "night", "morning", "long", "far", "big", "little", "one", "kind", "sort", "of",
    # 接続詞のthat(直後に主語・限定詞が来る): so that nobody noticed / said that the team won
    "nobody", "everyone", "everybody", "someone", "somebody", "anyone", "anybody", "he", "she", "they", "it", "we", "i", "you", "there",
    "the", "a", "an", "his", "her", "their", "our", "my", "your", "its", "people", "this", "that", "these", "those",
})
_UNCOUNTABLE = frozenset({
    "advice", "information", "news", "equipment", "furniture", "luggage", "baggage", "money", "music", "traffic", "weather", "progress", "research",
    "knowledge", "evidence", "help", "behavior", "behaviour", "attention", "trust", "work", "homework", "software", "feedback", "damage", "noise",
    "luck", "fun", "water", "air", "time", "energy", "love", "hope", "courage", "pressure", "silence", "sound",
})
_OBJ_HER_FOLLOW = frozenset({
    "the", "a", "an", "this", "that", "these", "those", "some", "any", "my", "your", "his", "our", "their", "to", "for", "with", "up", "down", "off", "out",
    "over", "away", "back", "in", "on", "at", "from", "into", "about", "around", "through", "by", "and", "or", "but", "so", "along", "aside", "apart",
})
_cmu = None


def _cmu_dict():
    global _cmu
    if _cmu is None:
        try:
            import cmudict
            _cmu = cmudict.dict()
        except Exception:
            _cmu = {}
    return _cmu


def starts_with_vowel_sound(word: str) -> bool:
    """CMU辞書で語頭の音素が母音か(API 0)。辞書に無い語は綴りの簡易規則。"""
    w = (word or "").lower().strip("'")
    if not w:
        return False
    prons = _cmu_dict().get(w)
    if prons:
        return bool(re.search(r"\d", prons[0][0]))
    if w.startswith(("hour", "honest", "honor", "honour", "heir")):
        return True
    if w.startswith(("uni", "use", "usu", "eu", "one", "once")):
        return False
    return w[0] in "aeiou"


def _looks_plural(w: str) -> bool:
    return len(w) > 3 and w.endswith("s") and not w.endswith(("ss", "us", "is"))


def _ref_pair_ok(kt: str, dt: str, idx: int, key_tokens: list, window: list) -> bool:
    """DEV: 参照語の1対1置換が許されるか。指示語this/that→a/an/the(単数可算名詞の限定詞のときのみ)、目的格him/me/us/(her)→someone。"""
    kl, dl = kt.lower(), dt.lower()
    nxt_d = window[idx + 1].lower() if idx + 1 < len(window) else None
    if dl in ("that", "this"):
        if kl not in ("a", "an"):   # ユーザー明示例(draw a line)優先: theは許可しない(Opus OF-03(1)からの変更、ITERATION_LOG #1)
            return False
        if nxt_d is None or nxt_d in _DEM_FOLLOW_BLOCK or nxt_d in _UNCOUNTABLE or _looks_plural(nxt_d):
            return False
        nxt_k = key_tokens[idx + 1].lower() if idx + 1 < len(key_tokens) else None
        if nxt_k is None:
            return False
        if kl == "a" and starts_with_vowel_sound(nxt_k):
            return False
        if kl == "an" and not starts_with_vowel_sound(nxt_k):
            return False
        return True
    if dl in ("him", "me", "us"):
        return kl in ("someone", "somebody")
    if dl == "her":
        return kl in ("someone", "somebody") and (nxt_d is None or nxt_d in _OBJ_HER_FOLLOW)
    return False


def dev_is_valid_inflection_normalization(key_phrase: str, display_phrase: str) -> bool:
    """er105.is_valid_inflection_normalization の複製+参照語置換(DEV)。元関数と同じ窓走査で、各トークンが
    production `_token_pair_ok`(活用形・人称表) または `_ref_pair_ok`(参照語) のいずれかで許される場合のみTrue。"""
    import importlib; ft = importlib.import_module("er105_" "kp_fulltext_selector_01")
    norm = lambda s: ft._TOKEN_RE.findall(unicodedata.normalize("NFKC", s or "").replace("’", "'"))   # noqa: E731
    k, d = norm(key_phrase), norm(display_phrase)
    if not k or len(k) > len(d):
        return False
    for start in range(0, len(d) - len(k) + 1):
        window = d[start:start + len(k)]
        if all(ft._token_pair_ok(kt, dt, i, k) or _ref_pair_ok(kt, dt, i, k, window) for i, (kt, dt) in enumerate(zip(k, window))) \
                and any(kt.lower() != dt.lower() for kt, dt in zip(k, window)):
            return True
    return False


REASON_REF = "generalize_reference_word"
DEV_ALLOWED_REASONS = ("lemma_normalization", "generalize_person_dependent_reference", REASON_REF)


def dev_is_valid_fulltext_normalization(key_phrase: str, display_phrase: str, normalization_reason) -> bool:
    if normalization_reason not in DEV_ALLOWED_REASONS:
        return False
    return dev_is_valid_inflection_normalization(key_phrase, display_phrase)


# ------------------------------------------------------------------ 費用台帳・Recording client
_LEDGER_LOCK = threading.Lock()
_CLIENT = None


def _real_client():
    global _CLIENT
    if _CLIENT is None:
        from dotenv import load_dotenv
        load_dotenv(ROOT / ".env")
        from openai import OpenAI
        _CLIENT = OpenAI()
    return _CLIENT


def ledger_add(rec: dict):
    with _LEDGER_LOCK:
        LEDGER.parent.mkdir(parents=True, exist_ok=True)
        with open(LEDGER, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def ledger_total_jpy(kinds=None) -> float:
    if not LEDGER.exists():
        return 0.0
    t = 0.0
    for ln in LEDGER.read_text(encoding="utf-8").splitlines():
        if ln.strip():
            r = json.loads(ln)
            if kinds is None or r.get("kind") in kinds:
                t += r.get("cost_jpy") or 0
    return t


class _RecResponses:
    def __init__(self, stage):
        self.stage = stage

    def create(self, **kw):
        import er009_n1_routing_governance_10_actual_model_cost as pricing
        resp = _real_client().responses.create(**kw)
        u = getattr(resp, "usage", None)
        inp = getattr(u, "input_tokens", None)
        outp = getattr(u, "output_tokens", None)
        det = getattr(u, "input_tokens_details", None)
        cached = getattr(det, "cached_tokens", None) if det is not None else None
        try:
            cost = pricing.cost_jpy_for_call("openai", resp.model, inp, cached, outp)
        except Exception:
            cost = None
        c = cur()
        ledger_add(dict(kind="gen", stage=self.stage, arm=c.arm if c else None, rep=c.rep if c else None, unit=c.unit if c else None,
                        model=resp.model, input_tokens=inp, cached=cached, output_tokens=outp, cost_jpy=round(cost, 5) if cost is not None else None,
                        ts=time.strftime("%Y-%m-%dT%H:%M:%S")))
        return resp


class RecClient:
    def __init__(self, stage: str):
        self.responses = _RecResponses(stage)


# ------------------------------------------------------------------ dispatcher (monkeypatch)
_ORIG: dict = {}
_INSTALLED = False
_DEV_SCHEMA = None
_PROD_FT_SCHEMA = None


def _dev_schema():
    import er003_key_words_canonicalization as kc
    s = json.loads(json.dumps(kc.CANONICALIZATION_JSON_SCHEMA_FULLTEXT))
    enum = s["schema"]["properties"]["items"]["items"]["properties"]["normalization_reason"]["enum"]
    if REASON_REF not in enum:
        enum.insert(enum.index("other"), REASON_REF)
    return s


def install_dev_patches():
    """DEV注入を明示的に有効化する(Production moduleのsourceは不変、プロセス内のattribute差し替えのみ)。"""
    global _INSTALLED, _DEV_SCHEMA, _PROD_FT_SCHEMA
    if _INSTALLED:
        return
    import er003_key_words_canonicalization as kc
    import er003_key_words_gloss_alignment as ga
    import er019_family_x_kp_explanation_01 as kx
    _ORIG.update({
        "kc.load_prompt_template": kc.load_prompt_template,
        "kc._is_valid_fulltext_normalization": kc._is_valid_fulltext_normalization,
        "kc.make_canonicalization_fn": kc.make_canonicalization_fn,
        "kc.NORMALIZATION_REASONS_FULLTEXT": kc.NORMALIZATION_REASONS_FULLTEXT,
        "ga.build_user_message_corrected": ga.build_user_message_corrected,
        "ga.make_alignment_fn": ga.make_alignment_fn,
        "ga.person_generalization_pairs": ga.person_generalization_pairs,
        "kx._header_for": kx._header_for,
        "kx.build_explanation_user_message": kx.build_explanation_user_message,
        "kc.run_canonicalization_gate": kc.run_canonicalization_gate,
        "ga.align_glosses": ga.align_glosses,
    })
    _PROD_FT_SCHEMA = kc.CANONICALIZATION_JSON_SCHEMA_FULLTEXT
    _DEV_SCHEMA = _dev_schema()
    ptpl = Path(ROOT / kc.FULLTEXT_PROMPT_TEMPLATE_PATH).read_text(encoding="utf-8")
    a1_tpl = build_a1_template(ptpl)

    def d_load(path=kc.PROMPT_TEMPLATE_PATH):
        t = _ORIG["kc.load_prompt_template"](path)
        if _flag("a1") and path == kc.FULLTEXT_PROMPT_TEMPLATE_PATH:
            assert t == ptpl, "production fulltext template changed during Trial"
            return a1_tpl
        return t

    def d_valid_ft(key_phrase, display_phrase, normalization_reason):
        if _flag("a1"):
            return dev_is_valid_fulltext_normalization(key_phrase, display_phrase, normalization_reason)
        return _ORIG["kc._is_valid_fulltext_normalization"](key_phrase, display_phrase, normalization_reason)

    def d_make_canon(*a, **kw):
        if _flag("a1") and kw.get("schema") is _PROD_FT_SCHEMA:
            kw["schema"] = _DEV_SCHEMA
        if kw.get("client") is None and len(a) < 2:
            kw["client"] = RecClient("canon")
        return _ORIG["kc.make_canonicalization_fn"](*a, **kw)

    def d_make_align(*a, **kw):
        if kw.get("client") is None and len(a) < 2:
            kw["client"] = RecClient("gloss")
        return _ORIG["ga.make_alignment_fn"](*a, **kw)

    def d_build_msg(*a, **kw):
        msg = _ORIG["ga.build_user_message_corrected"](*a, **kw)
        if _flag("a2") and ga.NEW_GENERATION_TEXT in msg:
            msg = msg.replace(ga.NEW_GENERATION_TEXT, ga.NEW_GENERATION_TEXT + A2_EXTRA, 1)
        return msg

    def d_pairs(item):
        pairs = _ORIG["ga.person_generalization_pairs"](item)
        if _flag("a1") and not pairs:
            d = ga._kp_tokens(item.get("display_phrase"))
            k = ga._kp_tokens(item.get("key_phrase"))
            if len(d) == len(k):
                pairs = [{"from": x, "to": y} for x, y in zip(d, k) if x != y and x in ("him", "her", "me", "us") and y in ("someone", "somebody")]
        return pairs

    def d_header(n):
        h = _ORIG["kx._header_for"](n)
        if _flag("a3"):
            marker = "\n\nKey Phrases:\n"
            assert h.count(marker) == 1, "explanation header drift"
            extra = {2: A3_EXTRA_V2, 3: A3_EXTRA_V3}.get(cur().cfg.get("a3"), A3_EXTRA)
            h = h.replace(marker, "\n" + extra + "\nKey Phrases:\n", 1)
        return h

    def d_build_expl(items):
        msg = _ORIG["kx.build_explanation_user_message"](items)
        if _flag("ctx"):
            for it in items:
                ctxs = it.get("_context")
                if ctxs:
                    line = f'   source_sentence: "{it["source_sentence"]}"\n'
                    assert line in msg
                    msg = msg.replace(line, line + f'   surrounding_context (previous and next sentence, for choosing the sense only): "{ctxs}"\n', 1)
        return msg

    def d_gate(*a, **kw):
        c = cur()
        if c and c.cfg.get("canon_from"):
            for src in c.cfg["canon_from"]:
                p = OUT / "runs" / src / f"rep{c.rep}" / c.unit / "canon_cache.json"
                if p.exists():
                    return tuple(json.loads(p.read_text(encoding="utf-8")))
            raise RuntimeError(f"canon cache not found for {c.unit} rep{c.rep} in {c.cfg['canon_from']}")
        res = _ORIG["kc.run_canonicalization_gate"](*a, **kw)
        if c is not None and c.dir is not None:
            (c.dir / "canon_cache.json").write_text(json.dumps(list(res), ensure_ascii=False), encoding="utf-8")
        return res

    def d_align(merged, *a, **kw):
        c = cur()
        if c and c.cfg.get("skip_gloss"):
            return {"merged": merged, "status": "SKIPPED_TRIAL_CANON_ONLY", "targets": [], "attempts": [], "item_log": {}, "unresolved_ranks": []}
        return _ORIG["ga.align_glosses"](merged, *a, **kw)

    kc.run_canonicalization_gate = d_gate
    ga.align_glosses = d_align
    kc.load_prompt_template = d_load
    kc._is_valid_fulltext_normalization = d_valid_ft
    kc.make_canonicalization_fn = d_make_canon
    kc.NORMALIZATION_REASONS_FULLTEXT = tuple(kc.NORMALIZATION_REASONS_FULLTEXT) + (REASON_REF,)
    ga.make_alignment_fn = d_make_align
    ga.build_user_message_corrected = d_build_msg
    ga.person_generalization_pairs = d_pairs
    kx._header_for = d_header
    kx.build_explanation_user_message = d_build_expl
    _INSTALLED = True


def uninstall_dev_patches():
    global _INSTALLED
    if not _INSTALLED:
        return
    import er003_key_words_canonicalization as kc
    import er003_key_words_gloss_alignment as ga
    import er019_family_x_kp_explanation_01 as kx
    kc.load_prompt_template = _ORIG["kc.load_prompt_template"]
    kc._is_valid_fulltext_normalization = _ORIG["kc._is_valid_fulltext_normalization"]
    kc.make_canonicalization_fn = _ORIG["kc.make_canonicalization_fn"]
    kc.NORMALIZATION_REASONS_FULLTEXT = _ORIG["kc.NORMALIZATION_REASONS_FULLTEXT"]
    ga.make_alignment_fn = _ORIG["ga.make_alignment_fn"]
    ga.build_user_message_corrected = _ORIG["ga.build_user_message_corrected"]
    ga.person_generalization_pairs = _ORIG["ga.person_generalization_pairs"]
    kx._header_for = _ORIG["kx._header_for"]
    kx.build_explanation_user_message = _ORIG["kx.build_explanation_user_message"]
    kc.run_canonicalization_gate = _ORIG["kc.run_canonicalization_gate"]
    ga.align_glosses = _ORIG["ga.align_glosses"]
    _INSTALLED = False


# ------------------------------------------------------------------ 入力データ(units)
UNITS_PATH = OUT / "inputs" / "units.json"
CENSUS = ROOT / "docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01/census_items_01.json"
_ORIG_ITEM_FIELDS = ("rank", "source_span", "source_sentence", "display_phrase", "fulltext_source_ref", "source_sentence_id", "occurrence_count",
                     "occurrence_sentence_ids", "selection_resolution_method", "declared_word_count_mismatch")

HARD_DISPLAY = {   # 難例(DESIGN_01 §5-2。display_phraseをlowerで正規化)
    "draw that line", "reach for your wallet", "shines a light on", "fire the starting gun", "turned on its head", "on the throne", "carry the load",
    "pulled him under", "sentenced him to death", "earn such trust", "win such trust", "rose above the other voices", "held out", "held out his hands",
    "kept you company", "gave way", "go out of their way", "brace yourself for", "in your place", "pumps its fist", "for once",
}

SYN_UNITS = [
    ("syn1", "Mia had wanted to leave her small town for years. After weeks of doubt, Mia decided to take that step and move to Osaka. "
             "In the match, the referee warned the players: if you cross that line, he will stop the game. At the meeting, Ken tried to float that idea to the board.",
     [("take that step", "After weeks of doubt, Mia decided to take that step and move to Osaka.", "P", ["take a step"]),
      ("cross that line", "In the match, the referee warned the players: if you cross that line, he will stop the game.", "P", ["cross the line", "cross a line"]),
      ("float that idea", "At the meeting, Ken tried to float that idea to the board.", "P", ["float an idea"])]),
    ("syn2", "The story began on a busy street. In the end, Tom told her the truth about the missing key. When the heavy box fell, a stranger gave him a hand. "
             "The crowd began to close around me near the exit.",
     [("told her the truth", "In the end, Tom told her the truth about the missing key.", "P", ["tell someone the truth"]),
      ("gave him a hand", "When the heavy box fell, a stranger gave him a hand.", "P", ["give someone a hand"]),
      ("close around me", "The crowd began to close around me near the exit.", "P", ["close around someone"])]),
    ("syn3", "Her coach told her to rest, and she decided to take that advice. The tickets did not cost that much last year. He left early so that nobody noticed the delay.",
     [("take that advice", "Her coach told her to rest, and she decided to take that advice.", "N", ["take that advice"]),
      ("cost that much", "The tickets did not cost that much last year.", "N", ["cost that much"]),
      ("so that nobody noticed", "He left early so that nobody noticed the delay.", "N", ["so that nobody noticed"])]),
    ("syn4", "She was afraid she might lose her job after the merger. The plan has risks; that said, it is worth trying. Nobody knew the answer at that point.",
     [("lose her job", "She was afraid she might lose her job after the merger.", "N", ["lose her job", "lose one's job", "lose someone's job"]),
      ("that said", "The plan has risks; that said, it is worth trying.", "N", ["that said"]),
      ("at that point", "Nobody knew the answer at that point.", "N", ["at that point"])]),
    ("syn5", "The forecast looked bad. If it rains, in that case we will stay home. Let's try again, this time with more care. Just between you and me, the plan will fail.",
     [("in that case", "If it rains, in that case we will stay home.", "N", ["in that case"]),
      ("this time", "Let's try again, this time with more care.", "N", ["this time"]),
      ("between you and me", "Just between you and me, the plan will fail.", "N", ["between you and me"])]),
    ("syn6", "The film was not that bad, to be honest. He knew he had to make that call before noon.",
     [("not that bad", "The film was not that bad, to be honest.", "N", ["not that bad"]),
      ("make that call", "He knew he had to make that call before noon.", "P", ["make a call"])]),
]


def _article_from_prompt(path: Path) -> str:
    s = path.read_text(encoding="utf-8")
    m = re.search(r"【記事本文\(参考、文脈確認用\)】\n(.*)\n\n【Key Phrase候補\(JSON\)】", s, re.S)
    if not m:
        raise RuntimeError(f"article not found in {path}")
    return m.group(1)


def build_units() -> dict:
    rows = json.loads(CENSUS.read_text(encoding="utf-8"))
    seen, units = [], []
    for r in rows:
        k = (r["run"], r["level"])
        if k not in seen:
            seen.append(k)
    for run, lv in seen:
        d1 = ROOT / run / lv / "key_phrases"
        d2 = ROOT / run / "key_phrases" / lv
        base = d1 if (d1 / "canonicalization_prompt.txt").exists() else d2
        merged = json.loads((base / "keywords_canonicalized.json").read_text(encoding="utf-8"))
        article = _article_from_prompt(base / "canonicalization_prompt.txt")
        orig = [{f: it[f] for f in _ORIG_ITEM_FIELDS if f in it} for it in merged["items"]]
        expl_by_rank = {r["rank"]: r.get("explanation") for r in rows if r["run"] == run and r["level"] == lv}
        prod = {str(it["rank"]): dict(key_phrase=it["key_phrase"], used_form=it["used_form"], gloss=it.get("japanese_gloss"), reason=it.get("normalization_reason"),
                                       expl=expl_by_rank.get(it["rank"]), source_sentence=it.get("source_sentence")) for it in merged["items"]}
        run_id = run.replace("\\", "/")
        fam = "X" if "er019_output" in run_id else "Z"
        uid = f"{fam}_" + re.sub(r"[^A-Za-z0-9]+", "_", run_id.split("/")[-2] + "__" + run_id.split("/")[-1]) + "__" + lv
        units.append(dict(unit_id=uid, run=run_id, level=lv, family=fam, article_text=article,
                          original_items=orig, production=prod, synthetic=False))
    for sid, art, items in SYN_UNITS:
        oi, exp = [], {}
        for i, (disp, sent, kind, accept) in enumerate(items, 1):
            oi.append(dict(rank=i, source_span=disp, source_sentence=sent, display_phrase=disp, fulltext_source_ref="fulltext_exact_v1",
                           source_sentence_id=f"S{i}", occurrence_count=1, occurrence_sentence_ids=[f"S{i}"],
                           selection_resolution_method="fulltext_exact_unique", declared_word_count_mismatch=False))
            exp[str(i)] = dict(kind=kind, accept=accept)
        units.append(dict(unit_id=f"SYN_{sid}__b1b", run=f"SYN/{sid}", level="b1b", family="SYN", article_text=art, original_items=oi,
                          production={}, synthetic=True, expected=exp))
    return dict(units=units, hard_display=sorted(HARD_DISPLAY))


# ------------------------------------------------------------------ 1 unit の replay
def _split_sentences(article: str) -> list:
    parts = re.split(r"(?<=[.!?])\s+|\n+", article)
    return [p.strip() for p in parts if p.strip()]


def context_for(article: str, sentence: str) -> str:
    ss = _split_sentences(article)
    for i, s in enumerate(ss):
        if sentence.strip() in s or s in sentence.strip():
            prev = ss[i - 1] if i > 0 else ""
            nxt = ss[i + 1] if i + 1 < len(ss) else ""
            return " ".join(x for x in (prev, nxt) if x)
    return ""


def _expl_stage(unit: dict, items: list, rec: dict):
    import er019_family_x_kp_explanation_01 as kx
    inp = []
    for it in sorted(items, key=lambda x: x["rank"]):
        row = dict(rank=it["rank"], display_phrase=it["used_form"], source_sentence=it.get("source_sentence", ""), japanese_gloss=it.get("gloss") or "")
        if _flag("ctx"):
            row["_context"] = context_for(unit["article_text"], it.get("source_sentence", ""))
        inp.append(row)
    try:
        er = kx.generate_kp_explanations(inp, client=RecClient("expl"))
        rec["expl"] = {str(k): dict(text=v["english_explanation"], status=v["status"], words=(v.get("qa") or {}).get("word_count")) for k, v in er["items"].items()}
        rec["expl_retried"] = [er["audit"]["retried_for_parse"], er["audit"]["retried_for_qa"]]
    except Exception as e:   # noqa: BLE001
        rec["expl_error"] = f"{type(e).__name__}: {e}"


def _apply_share(unit: dict, items: list, a2_result: dict | None, rec: dict):
    rec["shared"] = []
    if unit["level"] == "b1b" and _flag("share") and a2_result and a2_result.get("items"):
        a2map = {x["used_form"].lower(): x for x in a2_result["items"] if x.get("gloss")}
        for it in items:
            src = a2map.get(it["used_form"].lower())
            if src and it.get("gloss") != src["gloss"]:
                rec["shared"].append(dict(rank=it["rank"], used_form=it["used_form"], before=it.get("gloss"), after=src["gloss"]))
                it["gloss"] = src["gloss"]


def run_unit(arm: str, rep: int, unit: dict, a2_result: dict | None = None, out_root: Path | None = None) -> dict:
    """1 unit(=1 run・1 level)を本番関数で再生: canonicalization(gate・retry込み)+gloss再整合(retry・HR込み)+(b1bのみ)Adv英語説明。
    選定は再実行しない(記録済みitemを入力)。arm設定: canon_from=他armのcanon結果を再利用 / items_from=他armのcanon+gloss結果を再利用して説明段だけ再実行。"""
    import er003_v1_n3_01_scaffold_generate as n3
    out_root = out_root or (OUT / "runs")
    d = out_root / arm / f"rep{rep}" / unit["unit_id"]
    rf = d / "result.json"
    if rf.exists():
        return json.loads(rf.read_text(encoding="utf-8"))
    d.mkdir(parents=True, exist_ok=True)
    c = ArmCtx(arm, rep, unit["unit_id"], unit["article_text"])
    c.dir = d
    _TL.ctx = c
    t0 = time.time()
    rec = dict(arm=arm, rep=rep, unit_id=unit["unit_id"], level=unit["level"], family=unit["family"], synthetic=unit["synthetic"])
    try:
        if c.cfg.get("items_from"):
            src = json.loads((out_root / c.cfg["items_from"] / f"rep{c.cfg.get('items_from_rep', rep)}" / unit["unit_id"] / "result.json").read_text(encoding="utf-8"))
            for k in ("canon_status", "canon_attempts", "gloss_alignment_status", "gloss_alignment_unresolved_ranks", "gloss_attempts_max"):
                rec[k] = src.get(k)
            rec["items_from"] = c.cfg["items_from"]
            if src.get("items"):
                items = json.loads(json.dumps(src["items"]))
                rec["items"] = items
                _apply_share(unit, items, a2_result, rec)
                if unit["level"] == "b1b":
                    _expl_stage(unit, items, rec)
            else:
                rec["error"] = f"source arm {c.cfg['items_from']} has no items"
        else:
            process = "A2_SUPPORT" if unit["level"] == "a2" else "B1_SUPPORT"
            orig_items = json.loads(json.dumps(unit["original_items"]))
            res = n3.run_key_phrase_canonicalization(unit["article_text"], orig_items, str(d), unit["unit_id"], process=process)
            rec["canon_status"] = res.get("status")
            meta_p = d / "canonicalization_runtime_metadata.json"
            if meta_p.exists():
                meta = json.loads(meta_p.read_text(encoding="utf-8"))
                rec["canon_attempts"] = [dict(attempt=a.get("attempt"), status=a.get("status"), item_reasons=a.get("item_reasons")) for a in meta.get("attempts_detail", [])]
            merged = res.get("merged")
            rec["gloss_alignment_status"] = res.get("gloss_alignment_status")
            rec["gloss_alignment_unresolved_ranks"] = res.get("gloss_alignment_unresolved_ranks")
            gm = res.get("gloss_alignment_metrics") or {}
            rec["gloss_attempts_max"] = gm.get("attempts_max")
            if merged:
                items = []
                for it in merged["items"]:
                    items.append(dict(rank=it["rank"], display_phrase=it["display_phrase"], key_phrase=it["key_phrase"], used_form=it["used_form"],
                                      reason=it.get("normalization_reason"), gloss=it.get("japanese_gloss"), gloss_status=it.get("gloss_alignment_status"),
                                      source_sentence=it.get("source_sentence"), qa_overall=it.get("qa_overall_status")))
                rec["items"] = items
                _apply_share(unit, items, a2_result, rec)
                if unit["level"] == "b1b" and not c.cfg.get("skip_expl"):
                    _expl_stage(unit, items, rec)
    except Exception as e:   # noqa: BLE001
        rec["error"] = f"{type(e).__name__}: {e}"
    rec["elapsed_s"] = round(time.time() - t0, 1)
    rf.write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
    _TL.ctx = None
    return rec


def stop_present():
    for p in (OUT / "STOP", OUT / "STOP_ALL", ROOT / "er026_output" / "family_z_production_e2e_01" / "STOP_ALL",
              ROOT / "docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01" / "STOP"):
        if p.exists():
            return str(p)
    return None


def run_group(arms: list, rep: int, group: list, cap: float):
    """同一runのa2→b1bを順に(share armのため)、armは指定順に逐次(a1→a12→a123sは前armの結果を再利用)。"""
    outs = []
    for arm in arms:
        outs.extend(_run_group_one(arm, rep, group, cap))
    return outs


def _run_group_one(arm: str, rep: int, group: list, cap: float):
    a2res = None
    outs = []
    for u in group:
        if stop_present():
            outs.append(dict(unit_id=u["unit_id"], skipped="STOP"))
            continue
        if ledger_total_jpy(("gen", "judge")) >= cap:
            outs.append(dict(unit_id=u["unit_id"], skipped="CAP"))
            continue
        r = run_unit(arm, rep, u, a2_result=a2res)
        if u["level"] == "a2":
            a2res = r
        outs.append(r)
    return outs


def cmd_run(args):
    install_dev_patches()
    start_h = prod_hashes()
    OUT.mkdir(parents=True, exist_ok=True)
    hs = OUT / "production_hash_start.json"
    if not hs.exists():
        hs.write_text(json.dumps(start_h, indent=1), encoding="utf-8")
    else:
        assert json.loads(hs.read_text(encoding="utf-8")) == start_h, "Production module hash drift since Trial start"
    data = json.loads(UNITS_PATH.read_text(encoding="utf-8"))
    units = data["units"]
    if args.units:
        want = set(args.units.split(","))
        units = [u for u in units if any(w in u["unit_id"] for w in want)]
    if args.no_synth:
        units = [u for u in units if not u["synthetic"]]
    if args.only_synth:
        units = [u for u in units if u["synthetic"]]
    groups = {}
    for u in units:
        groups.setdefault(u["run"], []).append(u)
    for g in groups.values():
        g.sort(key=lambda u: 0 if u["level"] == "a2" else 1)
    arms = args.arms.split(",")
    reps = [int(x) for x in args.reps.split(",")]
    jobs = [(arms, r, g) for r in reps for g in groups.values()]
    print(f"jobs(groups)={len(jobs)} units={len(units)} cap={args.cap}", flush=True)
    done = 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(run_group, a, r, g, args.cap) for a, r, g in jobs]
        for f in as_completed(futs):
            f.result()
            done += 1
            if done % 10 == 0 or done == len(futs):
                print(f"  {done}/{len(futs)} gen_cost_jpy={ledger_total_jpy(('gen',)):.3f}", flush=True)
    end_h = prod_hashes()
    (OUT / "production_hash_end.json").write_text(json.dumps(end_h, indent=1), encoding="utf-8")
    print("production_hash_unchanged:", start_h == end_h)
    print(f"gen_cost_jpy={ledger_total_jpy(('gen',)):.3f} total_cost_jpy={ledger_total_jpy():.3f}")
    return 0 if start_h == end_h else 2


def cmd_make_prod_arm(args):
    """記録済みProduction出力(2026-10-22/23の正式run、API 0)を『prod』armとして保存する(baselineの1標本)。"""
    data = json.loads(UNITS_PATH.read_text(encoding="utf-8"))
    n = 0
    for u in data["units"]:
        if u["synthetic"]:
            continue
        items, expl = [], {}
        for oi in u["original_items"]:
            pr = u["production"][str(oi["rank"])]
            items.append(dict(rank=oi["rank"], display_phrase=oi["display_phrase"], key_phrase=pr["key_phrase"], used_form=pr["used_form"], reason=pr["reason"],
                              gloss=pr["gloss"], gloss_status="ALIGNED", source_sentence=pr["source_sentence"], qa_overall="PASS"))
            if pr.get("expl"):
                expl[str(oi["rank"])] = dict(text=pr["expl"], status="OK", words=len(re.findall(r"[A-Za-z']+", pr["expl"])))
        d = OUT / "runs" / "prod" / "rep0" / u["unit_id"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "result.json").write_text(json.dumps(dict(arm="prod", rep=0, unit_id=u["unit_id"], level=u["level"], family=u["family"], synthetic=False,
                                                       canon_status="CANONICALIZATION_PASS", items=items, expl=expl or None, source="recorded_production"),
                                                  ensure_ascii=False, indent=1), encoding="utf-8")
        n += 1
    print("prod arm units", n)
    return 0


def cmd_build_units(args):
    data = build_units()
    UNITS_PATH.parent.mkdir(parents=True, exist_ok=True)
    UNITS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    n_items = sum(len(u["original_items"]) for u in data["units"])
    print("units", len(data["units"]), "items", n_items)
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build-units")
    sub.add_parser("make-prod-arm")
    r = sub.add_parser("run")
    r.add_argument("--arms", default="base,a1,a12,a123s")
    r.add_argument("--reps", default="1")
    r.add_argument("--units", default="")
    r.add_argument("--no-synth", action="store_true")
    r.add_argument("--only-synth", action="store_true")
    r.add_argument("--workers", type=int, default=8)
    r.add_argument("--cap", type=float, default=CAP_JPY_DEFAULT)
    args = ap.parse_args(argv)
    if args.cmd == "build-units":
        return cmd_build_units(args)
    if args.cmd == "make-prod-arm":
        return cmd_make_prod_arm(args)
    if args.cmd == "run":
        return cmd_run(args)
    return 1


if __name__ == "__main__":
    sys.exit(main())
